# Conflict C-8, third revision — ownership, custody and recovery

**Submitted for Codex technical review. Not accepted, and not implemented.**
No production harness source changed for EH-R16-1 in the submission carrying
this document. `tools/phase_5_0_evidence/cleanup.py`,
`execution/executor.py`, `execution/case_program.py`, `concrete_plan.py` and
`execution/materializer.py` are byte-identical to the tree R16 and R2 reviewed,
so the defect is still present and still reproducible; §10 says how, and the
reproductions are in the tree and labelled as reproductions.

Supersedes `phase-5-0-evidence-harness-c8-ownership-design-r16-2.md`, which was
**not accepted** in project review R2 of 2026-09-09. Neither its proposed
interface expansions nor its residuals R-C8-1 … R-C8-4 were accepted, and this
revision does not treat any of them as settled. It supersedes, in turn,
`phase-5-0-evidence-harness-c8-ownership-design-r16.md`, which was rejected at
R16.

**EH-R16-1 remains open**, with its existing identity. It is not renumbered,
not partially closed, and not closed by this document.

Scope: EH-R16-1 only. Package 5.0 remains **not ready**, P5.0-R5 **Blocking**,
OD-62 **Open**, `is_executable=False`.

---

## 0. Where each R2 finding is answered

| Finding | Answered in |
|---|---|
| **PR-20260909-R2-1** — guards omit execution-time effects | §2 (vocabulary), §3 (the complete ledger), §4 (what establishes ownership per step), §6.2 (`G-2`), §6.5 (substitution during execution: refusal, uncertainty, residue, recovery), §6.6 (installed-program integrity), §6.7 (the guards' own source), §6.8 (independently safe recovery), §10 rows 1–6 |
| **PR-20260909-R2-2** — installed bytes not bound to verified bytes | §5 (capture-to-recovery contract), §6.1 (`G-1`), §6.1.4 (destination safety, partial writes, interruption, restart), §7 (exact interface impact), §8 (R-C8-3′ restated honestly), §10 rows 7–13 |
| **PR-20260909-R2-3** — alternatives rest on a false equivalence | §1.3 (the three false statements withdrawn), §9 (the four substitution classes × eight candidates), §9.5 (exclusion of concurrent writers), §9.6 (protected namespace), §11 (erratum record) |
| Evidence limitations | §10.1 (what is implemented and injected now), §10.2 (what is proposed and why it cannot be written yet), §12 (the historical-claim correction) |

Separation required by the prompt: **observations** are §3 and §9.1;
**assumptions** are §4.4 and §9.5; **proof obligations** are §13.1;
**proposed acceptance decisions** are §8 and §14; **unresolved dependencies**
are §13.2.

---

## 1. What the previous revisions got wrong

### 1.1 Preserved from the second revision — two concessions that stand

These were correctly conceded at R16 and are **not** reopened.

* **`mkdirat` followed by `openat` does not detect child replacement.** Holding
  the parent descriptor fixes which directory `name` is looked up *in*. It says
  nothing about whether the entry `name` now refers to is the entry `mkdirat`
  created. There was no comparison in the rejected pseudocode and therefore no
  branch that could reach its claimed refusal.
* **The root-permission argument does not cover the plan's own directories.**
  `…/probe` and `…/probe-ro` are `0770 root:freedomsheet`; `CAP_DAC_OVERRIDE` is
  granted **ambiently** to `fbprobe` in `B5-E4`, `B5-E6` and `B5-C6-01` …
  `B5-C6-04`. Both identities are created by this run, so neither is outside the
  threat model. §9.1 keeps the inventory.

### 1.2 Preserved — the permissions inventory

§9.1 reproduces the inventory the second revision supplied, with two
corrections R2's reading makes necessary (§9.1.1 and §9.1.2). The inventory
itself is retained; R2 did not dispute it.

### 1.3 Withdrawn — three statements this revision does not make

**(a) "The sequence cannot exist on Linux", used as a general impossibility.**
The accurate, narrow claims are:

* there is no primitive that returns a descriptor to a newly created
  **directory**. `mkdir(2)`/`mkdirat(2)` return `0` or `-1`; `O_TMPFILE` creates
  an unnamed **regular file** and is invalid with `O_DIRECTORY`; `linkat(2)`
  refuses a directory `oldpath` with `EPERM`, and refuses `AT_EMPTY_PATH` when
  `olddirfd` refers to a directory, also with `EPERM`. Verified against the
  installed `mkdir(2)`, `open(2)` and `link(2)` manual pages;
* Linux has no `funlinkat(2)`. Every removal — `unlink(2)`, `unlinkat(2)` with
  or without `AT_REMOVEDIR`, `rmdir(2)` — names a **final path component**.
  Verified against `unlink(2)`.

Neither claim generalises to *"every design on Linux must retain the current
exposure."* It does not, and §9 sets out four candidate designs that reduce it.
The withdrawn sentence was an over-generalisation from two true syscall facts.

**(b) "The benefit a descriptor gives is already obtained by comparing the
root's identity."** False, and the distinction is documented. `rename(2)` states
that open file descriptors for `oldpath` are unaffected by the rename: a held
descriptor continues to refer to the **object**, whatever happens to the name.
A successful pathname identity comparison establishes what was at the name at
the instant of the comparison and stabilises no later lookup. A held reference
and a compared observation are different protections, and §2 keeps them apart by
name from here on.

**(c) "A root descriptor followed by `journal/000001.seal` fixes the still-
resolved `journal` component."** It does not. A descriptor-relative multi-
component pathname resolves every component after the first by name. Fixing
`journal` requires a second `openat` on the root descriptor with
`O_DIRECTORY|O_NOFOLLOW`, and fixing the final entry requires an operation that
does not name it — which for removal does not exist (see (a)). The chain is
per-component, and the second revision's example conflated one component with
all of them.

**(d) Withdrawn as a matter of framing.** The second revision recommended
maintainer acceptance of R-C8-1 … R-C8-4 partly on the ground that "no mechanism
is available". That ground does not hold for R-C8-4 (§9.5 supplies a mechanism)
and is stated too strongly for R-C8-2 and R-C8-3 (§9 narrows both). All four are
restated in §8; none is presented as unavoidable.

**Nothing in §1 rewrites a historical review finding.** The prior handback's
repetitions of (a) and (b) are corrected by the dated erratum in §11 and in the
handback itself, not by editing the original text.

---

## 2. Four things that are not interchangeable

The review requires these to be distinguished at every step of §3 and §4. They
are used with exactly these meanings for the rest of the document.

| Term | What it is | What it establishes | What it does not |
|---|---|---|---|
| **Observed baseline** | A recorded result of a reading taken before anything changed — `R-02`'s `getent` exit 2, a catalog listing, `mkroot`'s reported `(device, inode)` | that the named subject was in a stated condition **at that instant** | nothing about any later instant, and nothing about an object the reading did not address |
| **Vector allowlist** | `validate_argv`, `DisposableTarget.contained_path`, `PERMITTED_EXECUTABLES`, `FORBIDDEN_CLEANUP_TOKENS` | that the **string** a step will execute is one the review approved | nothing at all about what that string will resolve to at execution time |
| **Held object reference** | An open file descriptor kept across operations, with subsequent work done `*at()`-relative to it | that later operations act on **that object**, surviving rename of its name (`rename(2)`) | nothing about the final component of a descriptor-relative pathname, and nothing about the object's *content*, which can change in place under a held descriptor |
| **Exclusion boundary** | An argument that no actor able to perform the substitution existed, or was running, during the interval | that the substitution had no author, **if** the argument's premises are separately verified | nothing where a premise is a distribution default nobody recorded, and nothing about uid 0 or `CAP_DAC_OVERRIDE` |

Two consequences used throughout:

1. The executor's `_revalidate()` and `_revalidate_cleanup()` are **vector
   allowlist** operations. They re-check the string. They establish no current
   ownership of anything, and the second revision's implementation table was
   read as though they did.
2. `state.owned` is a set of **observed baselines**, fixed at the moment each
   baseline or exclusive creation was satisfied. It is not a live property of the
   host. `state.created_identity` is likewise a single observed baseline of two
   numbers.

---

## 3. The complete ownership-dependency ledger

Requirement of PR-20260909-R2-1. Every ownership-dependent read and mutation
across the whole lifecycle, in plan order. **Object/bytes** names what the
operation acts on. **Resolution** says how the operation reaches it. **Depends
on** names the ownership claim its correctness rests on. **Enforcement point
today** is what stands between the claim and the effect in the current tree —
and it is empty for most of the table, which is the finding.

Notation: *root-id* = the `(device, inode)` pair `B3-01` recorded;
*contained* = the vector allowlist's containment check only.

### 3.1 Creation

| # | Step | Object / bytes | Resolution | Depends on | Enforcement today | Proposed enforcement |
|---|---|---|---|---|---|---|
| 1 | `R-B-ROOT` | the root pathname | full path, `stat` | — | — | unchanged. It establishes nothing (EH-R14-1) and is retained only to stop an obviously occupied path early |
| 2 | `B3-01` `mkroot` | the directory `mkdir(2)` creates | full path, once | nothing prior | `mkdir` is exclusive; `EEXIST` is the refusal | unchanged. This call **is** the ownership |
| 3 | `B3-01` `open` | whatever is at the root pathname now | **second** full-path resolution | the parent's write permission during the interval | none | `G-0`: the parent's identity and mode become reviewed facts and are reported from the same descriptor (§6.0). The interval is **not** closed — R-C8-1 |
| 4 | `B3-01` `fchmod`, `fstat` | the object the descriptor refers to | held object reference | — | descriptor-addressed; sound | unchanged |
| 5 | `B3-02` | the root pathname | full path, `stat` | root-id | none — it is a mode/owner control and compares no identity | `G-2` guard before it |

### 3.2 Provisioning

| # | Steps | Object / bytes | Resolution | Depends on | Enforcement today | Proposed |
|---|---|---|---|---|---|---|
| 6 | `B3-03` … `B3-06` | 4 directories created under the root | 4 full paths | root-id | contained only | `G-2` guard immediately before each |
| 7 | `B3-07` | the reviewed case-program bytes → `…/bin/case` | 2 full paths (source outside the root, destination under it) | root-id; and the **source worktree's** integrity | contained only; source integrity is the manifest digest (`H-1`) | `G-2`; source integrity unchanged and restated in §6.7 |
| 8 | `P-03`, `P-04` | `…/bin/case` — its file capabilities, mode, owner | 2 full paths | root-id; the installed file's identity | expectation contracts on the observations | `G-2`; plus `G-3` (§6.6): `P-04`'s digest becomes a **prerequisite of every later use** of the installed program, not a one-time reading |
| 9 | `P-05`, `P-06` | `…/bin/case` — **executed** | full path, `execve` via the interpreter | root-id; the installed program's bytes | none between `P-04`'s reading and this execution | `G-3` |
| 10 | `B3-08` … `B3-12` | 5 files created under the root | 5 full paths | root-id | contained only | `G-2` |
| 11 | `B3-13` | `…/journal/current` symlink, created **by the installed program** | full path, inside the installed program | root-id; installed-program bytes | none | `G-2`, `G-3` |
| 12 | `B3-14` … `B3-18` | inode flags on 5 files | 5 full paths, `chattr` | root-id; each file's identity | none | `G-2`. Descendant identity is **not** established — R-C8-4′ |
| 13 | `B3-19` … `B3-22` | flag and namei readings | 4 full paths | root-id | expectation contracts | `G-2` |

### 3.3 Experiments

| # | Steps | Object / bytes | Resolution | Depends on | Enforcement today | Proposed |
|---|---|---|---|---|---|---|
| 14 | `B3-23` … `B3-38` | 16 opens under the root, as four identities, **through the installed program** | 16 full paths | root-id; installed-program bytes; each subject's identity | contained only | `G-2` at band and identity-transition boundaries (§6.2.2), `G-3` |
| 15 | `B4-01` … `B4-08` | 2 directories, 5 files, 1 flag change | 8 full paths | root-id | contained only | `G-2` |
| 16 | `B4-09` … `B4-31` | ≈23 filesystem experiments, **as `freedomsheet`**, including 4 `rename` and 3 `unlink` the run performs on its own subjects | ≈23 full paths | root-id; installed-program bytes; subject identity | contained only | `G-2`, `G-3`. §9.5's exclusion boundary is what covers the subjects |
| 17 | `B4-32` … `B4-34` | a transient unit writing under `…/probe` | systemd resolves the paths | root-id | `--wait`, `ReadWritePaths` | `G-2` before, and `G-4`: the unit's `LoadState` must be `not-found` before any removal under `…/probe` (§9.5) |
| 18 | `B5-E1` … `B5-E8`, `B5-C6-01` … `B5-C6-11` | capability experiments, several with **ambient `CAP_DAC_OVERRIDE`**, 2 `chattr +i` | ≈20 full paths | root-id; installed-program bytes | contained only | `G-2`, `G-3` |

### 3.4 Capture and materialization — the highest-consequence rows

| # | Steps | Object / bytes | Resolution | Depends on | Enforcement today | Proposed |
|---|---|---|---|---|---|---|
| 19 | `B6-01`, `B6-02` | the **live** `pg_hba.conf` / `pg_ident.conf` bytes, copied to `…/before/` | 2 full-path reads outside the root, 2 full-path writes under it | root-id for the destination; nothing for the source | exit status only | `G-1` (§6.1): the executor obtains the same bytes through the materializer, records their digest, and the on-disk copy is verified against it |
| 20 | `B6-M1`, `B6-M2` | reviewed configuration bytes written over the two live files | 2 full paths outside the root | that a byte-exact recovery input exists | `_revalidate_materialization` checks only that the **capture step was satisfied** | `G-1.2`: refuse unless the executor **holds** verified original bytes for this destination. Recoverability before mutation, as R2-2 requires |
| 21 | `B6-03` … `B6-09` | database, role, reload, 4 authentication observations | no filesystem object under the root | — | contracts | unchanged |

### 3.5 Cleanup

| # | Steps | Object / bytes | Resolution | Depends on | Enforcement today | Proposed |
|---|---|---|---|---|---|---|
| 22 | `CL-01`, `CL-02` | the **bytes** in `…/before/<file>`, installed over the live files | 2 full-path reads under the root, 2 full-path writes outside it | root-id; the capture's identity **and content** | **none** — this is EH-R16-1's worst effect | `G-1.3`: restoration writes the **held, digest-matched** bytes; the on-disk copy is a fallback the operator is told about, never an automatic source |
| 23 | `CL-03` | PostgreSQL reload | socket | that 22 restored the right bytes | none | inherits `G-1.3` |
| 24 | `CL-04`, `CL-05` | two post-reload observations | socket | 23 | contracts | inherits |
| 25 | `CL-06` … `CL-08` | unit, role, database | not filesystem | Band-0 / catalog baselines | applicability | unchanged — independently safe (§6.8) |
| 26 | `CL-09` … `CL-36` | 6 flag clears, 16 removals, 6 directory removals | 28 full paths | root-id; each subject's identity | **none** | `G-2` immediately before each; `G-4` for the 7 subjects in the `0770` directories |
| 27 | `CL-37` | the root's current identity | full path | — | this is the only comparison the current design makes | retained, and no longer the only one |
| 28 | `CL-38` | the root directory | full path, `rmdir` | root-id | `requires_revalidated` on `CL-37` | unchanged; the residual interval is R-C8-2 |
| 29 | `CL-39` … `CL-47` | memberships, accounts, groups | not filesystem | Band-0 baselines | applicability | unchanged — independently safe (§6.8) |

### 3.6 What the ledger shows

* **Between row 4 and row 27 the harness holds no descriptor at all.** Every
  step is a separate process. Identity, once acquired, is not held; it is
  re-derived by name, and in the current tree it is re-derived exactly once, at
  row 27.
* **Ninety-odd pathname resolutions precede the single comparison**, of which
  rows 19–20 and 22 move bytes into and out of the disposable instance's
  authentication configuration.
* The current design's protection is confined to row 28. A cleanup refusal at
  row 27 cannot undo rows 6–26, and the review's example — a root replaced
  between row 2 and row 6 — is a case in which **no guard exists at all**, not a
  case of a replacement racing a guard.

---

## 4. What establishes, retains or checks current ownership, per class

Requirement of PR-20260909-R2-1, second bullet, using §2's four terms.

### 4.1 The root itself

**Established** by row 2 — an exclusive `mkdir(2)`. This is an observed
baseline, and it is sound as one: `mkdir` returning success is itself the proof
that nothing was at the path, with no preliminary check and therefore no
observe-then-create window.

**Retained** by nothing. No descriptor survives row 4.

**Checked** at row 27 only, today. `G-2` adds a check immediately before each
dependent step, which converts the exposure from *"the whole run"* to *"one
process spawn per effect"* — for whole-root substitution only.

### 4.2 The root's identity as recorded

Row 3's second resolution is what ties the recorded numbers to the created
object, and it is an **exclusion boundary**, not detection: the numbers are the
identity of whatever occupied the root pathname immediately after `mkdir(2)`
returned, and they are the created object's identity **if and only if** no other
actor had write access to the root's parent during that interval.

`G-0` makes that boundary's premise checkable rather than assumed by adding the
parent's owner, group, mode, device and inode as reviewed target facts. It does
**not** close the interval; see R-C8-1.

### 4.3 Descendants of the root

**Established** transitively: `mkdir(2)` returns an *empty* directory, so at row
2 nothing existed under the root. Every declared subject was created by a later
step of this run.

**Retained** by nothing, and this is where the second revision's inventory
matters: the transitive claim survives only while no actor writes in a directory
under the root. Three actors can: uid 0, a `CAP_DAC_OVERRIDE` holder, and the
`freedomsheet` account in the two `0770` directories (§9.1).

**Checked** nowhere, today or under `G-2`. A per-descendant identity comparison
requires either 28 further reviewed observation keys and 28 further guard
processes, or a descriptor chain inside the reviewed program (§9.3). Neither is
proposed for implementation in this revision. What **is** proposed is `G-4`, an
exclusion boundary for the third actor (§9.5), which is the only one of the
three this run constructs and can therefore reason about.

### 4.4 Assumptions, stated as assumptions

1. **A-1.** The root's parent is a directory whose write access is confined to
   uid 0 and `CAP_DAC_OVERRIDE` holders. *Unverified.* No reviewed fact records
   it; `G-0` proposes to make it one. Until then row 3's exclusion boundary has
   an unstated premise.
2. **A-2.** The `freedomsheet` group's only member is the `freedomsheet` account
   this run creates. Derived from the plan (`B2-03`, `B2-06`, `B2-09`), and
   sound **for the group as this run makes it**; it says nothing about a host on
   which the name already exists — which `R-B-G-freedomsheet` is there to
   refuse.
3. **A-3.** The `freedomsheet` account has no interactive route onto the host.
   The plan sets `--system --no-create-home --shell /usr/sbin/nologin` and sets
   no password. Whether `useradd` leaves the password field locked is a
   **distribution default this repository has not recorded**, so A-3 is an
   assumption and is listed as a proof obligation in §13.1.
4. **A-4.** uid 0 and `CAP_DAC_OVERRIDE` holders are not excluded by anything in
   this design, and no part of it claims otherwise.

---

## 5. The capture-to-recovery contract

Requirement of PR-20260909-R2-2. Today there is no contract: `B6-01` copies a
pathname to a pathname and reports an exit status, `_revalidate_materialization`
checks only that the copy step was satisfied, and `CL-02` reopens the copy's
pathname in a different process. Nothing binds any of the three to the same
bytes.

The contract this revision proposes, in the order the run must satisfy it:

**C-1. Obtain the original bytes before the first configuration mutation.** At
`B6-01`/`B6-02` the executor obtains the live file's bytes through the injected
materializer (§6.1.1) and records their SHA-256 as an observation. A read that
fails, or one that cannot be completed, is a refusal **before any configuration
mutation is attempted**, not a degraded restore later.

**The bound is a real open question, not a reuse.** `MAX_MATERIALIZED_BYTES` is
`4096`, sized for the reviewed *replacement* content — the plan renders 975
bytes for `pg_hba.conf`. The **original** file this contract must capture is a
distribution default with its comment header, and on Debian/Ubuntu that is
commonly larger than 4096 bytes. Reusing the constant would therefore make C-1
refuse on a perfectly ordinary target, which is a refusal in the wrong
direction: it would block the run rather than protect it. `G-1` needs its own
reviewed capture bound, and the value cannot be chosen from this repository —
the two files' actual sizes are a **read-only preflight** observation. Until it
is chosen the bound is unresolved; see §13.1-5.

**C-2. Establish the on-disk copy against those bytes.** The copy in
`…/before/<file>` is read back and its digest compared with C-1's. Equal is the
only satisfying outcome. Unequal means the copy and the live file disagreed
within the run's own capture window — an inconsistent capture — and it is a
refusal before mutation.

**C-3. Recoverability is a prerequisite of mutation, checked at the
materialization gate.** `B6-M1`/`B6-M2` are refused unless the executor holds
C-1 bytes for that exact destination whose digest matched at C-2. This is where
"recoverability established before configuration mutation begins" becomes an
enforced condition rather than a described intention.

**C-4. Restoration writes the bytes that were checked.** `CL-01`/`CL-02` write
the **held buffer**, not a re-read of a pathname. The bytes written are the
bytes whose digest was recorded, because they are the same object in memory.
There is no second read of the source to substitute.

**C-5. What is not proved, stated plainly.** C-4 removes *source* substitution
from the restoration path. It does not remove *destination* substitution (§6.1.4),
and it does not survive loss of the executor's process (§6.1.5). Both are
residuals with named consequences in §8, not proofs.

**Why not the second revision's `digest` verb.** A `digest <path>` read followed
by an `install` of the same pathname in another process leaves the window R2-2
describes: the digest passes, the source is replaced, and `install` opens the
replacement. Labelling that `[proved]` was wrong. The verb narrows the failure
from *"arbitrary substituted bytes"* to *"bytes that matched at check time and
were swapped within one process spawn"*, which is a real narrowing and an honest
description — but it is not the contract above, and this revision does not
recommend it as the primary mechanism. It is kept as the documented fallback in
§7.3 for the case where Codex or the maintainer refuses `G-1`'s materializer
widening.

---

## 6. The proposed mechanism

Each item is labelled by what decides it: **[observation]** — a reading in the
run decides it; **[boundary]** — it rests on a stated exclusion boundary whose
premises are named; **[residual]** — it needs an acceptance decision.

Nothing in §6 is implemented. Nothing in §6 may be implemented before the
technical checkpoint, and the items marked as widening may not be implemented
before a recorded maintainer decision.

### 6.0 `G-0` — the parent's facts, compared *(§4.2)* — [boundary]

Five reviewed target facts — `root_parent_owner`, `root_parent_group`,
`root_parent_mode`, `root_parent_device`, `root_parent_inode` — with five
additional observation keys reported by the existing `mkroot` verb from a
descriptor it already opens, and one expectation contract. They ship
`UNCONFIRMED`; the executor refuses at the same gate that already refuses for
the interpreter and `E7` facts.

No new verb, no new arity, no new argument kind, no new privilege, nothing
writable. Obtaining the five values is the **read-only target preflight**, which
is authorized and assigned to Codex; this design neither performs it nor asks to.

Unchanged from the second revision's P1, which R2 did not dispute.

### 6.1 `G-1` — configuration recovery bound to bytes *(§5)* — [observation, for source substitution only]

This is the substantive change, and it replaces the second revision's P3.

#### 6.1.1 Where the bytes come from

The injected **materializer** is the one component in this harness already
permitted to touch the two live configuration files: it writes the reviewed
replacement bytes to them at `B6-M1`/`B6-M2`, with an owner, group, mode and
declared SHA-256. `G-1` gives it a read side, used at `B6-01`/`B6-02`:

```text
materializer.capture(path, *, max_bytes) -> CaptureResult(content, sha256)
materializer.restore(destination, *, content, sha256, owner, group, mode)
```

Both are on the **already-injected** interface, so every test drives fakes and
no test touches a host file. Neither is a case-program verb, so the reviewed
verb table, its arities and its argument kinds are unchanged. Neither raises a
privilege, admits an executable, or adds an identity.

The captured bytes are held in `_RunState` and **never enter an observation, a
record or the journal**. Only the SHA-256 does. This is deliberate: the content
of a live `pg_hba.conf` is security-relevant material, and widening the capture
surface to carry file content into evidence would be a worse change than the one
it fixes.

#### 6.1.2 The gate before mutation

`_revalidate_materialization` gains one condition: the run holds C-1 bytes for
this destination whose digest matched C-2's read-back. Its refusal category is
the existing `MATERIALIZATION_CAPTURE_INCOMPLETE` shape, extended with a new
fixed reason that names no path and no content.

#### 6.1.3 The restoration

`CL-01`/`CL-02` change kind: from a `RESTORE` whose vector is an `install` of
one pathname onto another, to a `RESTORE` the executor satisfies by calling
`materializer.restore(...)` with the held buffer. The declared destination,
owner, group and mode stay exactly as the plan renders them today, and remain
manifest-covered.

If the held buffer is absent — the executor did not reach C-1, or C-2 refused —
the restore is **not issued**, the file stays out of `restored_files`,
`ConfigurationRestoration.problems()` reports it, the state is S-B, and the
capture on disk is retained as a recovery input with the unverified procedure of
§6.4.

#### 6.1.4 Destination safety, partial writes, interruption, order

Solving source substitution while ignoring destination substitution would be the
same error one step along, so:

* **Destination substitution is not solved and is stated.** `/etc/postgresql/16/
  main/pg_hba.conf` is `postgres:postgres 0640` in a `postgres`-owned directory.
  Replacing it requires uid 0, `CAP_DAC_OVERRIDE`, or the `postgres` identity —
  the same three actors §4.4's A-4 does not exclude. `G-1` reduces the
  consequence (the bytes written are known-good) but not the possibility that
  they are written somewhere other than intended.
* **Partial writes.** The write is staged: create a uniquely named temporary in
  the **same directory** with `O_CREAT|O_EXCL|O_NOFOLLOW`, write the buffer,
  `fchmod`/`fchown` on the descriptor, `fsync`, then `rename(2)` into place.
  `rename(2)` is atomic for a reader of the destination pathname, so PostgreSQL
  never reloads a half-written file, and a failure before the rename leaves the
  live file untouched.
* **Interruption.** An interruption before the rename leaves a temporary file:
  bounded, in one known directory, named in the run record as residue, removed
  by no automatic step. An interruption after the rename has completed the
  restoration for that file; the reload has not necessarily run, which is
  already S-B by `ConfigurationRestoration`.
* **Restart and recovery.** A restarted run does not inherit the held buffer
  (§6.1.5). It must not silently reinstall from the retained on-disk capture;
  §6.4's procedure applies.
* **Order.** Unchanged: every restore, then the single reload, then the two
  post-reload observations, then everything whose safety depends on the restored
  authentication. `ordering_holds()` already enforces this and continues to.
* **Retention.** The on-disk captures stay retained — `CL-15`/`CL-16` are
  skipped — until the restore, the reload and both observations are satisfied.
  Unchanged from EH-R13-2, and `G-1` does not weaken it.

#### 6.1.5 What `G-1` does not do — [residual]

The held buffer lives in one process. If that process dies, the only remaining
recovery input is the on-disk capture, whose custody is exactly what `G-1`
declines to trust. The design's answer is **not** to trust it anyway: it is
§6.4's non-prescriptive procedure, which names the retained files, states that
their custody is not established, and directs the operator to a source outside
the disposable root. This is R-C8-3′ in §8.

### 6.2 `G-2` — a root identity guard immediately before every root-dependent effect — [observation, for whole-root substitution only]

#### 6.2.1 The rule

A step is **root-dependent** when its correctness depends on the object at the
reviewed root path being the one `mkroot` recorded — that is, when its argument
vector contains any path under the root, or it executes the installed case
program, or it is a restore, reload or verification that depends on one.

| Step class | Root-dependent | Why |
|---|---|---|
| creation `mkroot` | no | it *is* the establishment |
| provisioning `install`, `chattr`, `symlink` | yes | they resolve paths under the root |
| preflight and experiment steps through `…/bin/case` | yes | they resolve paths under the root and execute a file under it |
| `psql`, `getent`, `id`, account and group steps | no | their subjects are outside the filesystem hierarchy |
| `RESTORE`, `RELOAD`, `VERIFY` | yes, transitively | the restore's inputs were captured under the root |
| `REVERSAL` under the root | yes | it resolves a path under the root |
| `REVERSAL` on account, group, membership, role, database, unit | no | §6.8 |

`ConcretePlan` and `CleanupPlan.for_mutations()` each emit one `REVALIDATE`
immediately before each root-dependent step; the step names it through
`requires_revalidated`; and both plans gain an **immediacy clause** so a plan
that separates a guard from its step is a `PlanRefused` at generation time
rather than a comment. The executor's existing skip-on-unmatched-guard logic,
today confined to `REVERSAL`, is generalised to every guarded kind.

#### 6.2.2 Cost, stated rather than minimised

Counted against the plan the current tree generates, not estimated: of 139
execution steps, **96** name a path at or under the root, of which `R-B-ROOT`
and `B3-01` are the two that establish rather than depend — **94 guards**. Of 47
cleanup steps, **35** are root-dependent, of which `CL-37` is itself the guard —
**34 guards**, the same number the second revision reported. **128 guards in
total**, each a read-only `statroot` process that creates and changes nothing.

That roughly doubles the run's process count and is the largest cost in this
design. A cheaper variant, guarding only at band and identity-transition
boundaries, is **not** proposed: it would reinstate exactly the gap R2-1 found,
one band wide instead of one run wide.

#### 6.2.3 What `G-2` proves and does not

**Proves:** the whole root was not substituted between the guard and the guard's
own return, for each guarded step.

**Does not prove:** anything about a descendant (§4.3); anything about the
interval between the guard's return and the effect (R-C8-2); and it does not
undo an effect issued before a substitution occurred. Its value is that it stops
*subsequent* effects — which is precisely what R2-1's example requires and what
a cleanup-only guard cannot supply.

### 6.3 `G-3` — the installed case program's integrity is a prerequisite, not a reading — [observation]

`P-04` and `P-05` read the installed program's mode, owner and SHA-256 once,
early. Sixteen experiment steps then **execute** that file. Nothing today
re-establishes that the bytes executed are the bytes read.

Proposal: the recorded digest becomes a prerequisite the executor re-checks
immediately before each execution of the installed program, through the same
read side `G-1` gives the materializer — no new verb, no new privilege. Where
the digest does not match, or cannot be read, the step is refused and its
subject reported.

Cost: one additional read per experiment step. Residual: the read and the
`execve` are two operations, so R-C8-2 applies here too.

### 6.4 `G-4` — recovery instructions that do not assume custody — [observation]

`RECOVERY_PROCEDURE` step 3 currently tells the operator to reinstall from the
retained captures. If a guard did not match, or a capture's digest did not, the
retained files are not established to be this run's, and that instruction tells
the operator to do what `G-1` and `G-2` just refused.

`CleanupOutcome` gains `ownership_revalidated: bool | None` and
`recovery_inputs_verified: bool`. Neither defaults to the safe-looking value;
`None` selects the unverified path. `UNVERIFIED_RECOVERY_PROCEDURE` names the
retained paths, states that custody of the original bytes is not established,
directs the operator to a source outside the disposable root, and **prescribes
no reinstall.**

Unchanged from the second revision's P4, which R2 did not dispute.

### 6.5 Behaviour when the root or a descendant is substituted during execution

Requirement of PR-20260909-R2-1, third bullet.

| Situation | Refusal | Uncertainty | Residue | Recovery |
|---|---|---|---|---|
| `G-2` guard reports a different identity | the guarded step is not issued; the run stops at that step | none — the comparison is decisive | every subject not yet removed is declared residue; nothing under the root is deleted | independently safe reversals proceed (§6.8); `G-4`'s unverified procedure is reported |
| `G-2` guard cannot read the identity (`ENOENT`, `ELOOP` from `O_NOFOLLOW`, `ENOTDIR`, any errno) | the guarded step is not issued | **treated as mismatch** — fail closed, exactly as `_revalidation_refusal` does today | as above | as above |
| `G-2` guard times out, or its launch fails | the guarded step is not issued | fail closed | as above | as above |
| root substituted **after** a guard and before its effect | not detected | R-C8-2 | the effect lands on the replacement | `G-4`'s procedure, because `ownership_revalidated` will be `False` at the next guard |
| a descendant is substituted, root unchanged | not detected by `G-2`; `G-4`'s unit quiescence check covers only the two `0770` directories | R-C8-4′ | — | — |
| capture digest disagreement at C-2 | `B6-M1`/`B6-M2` refused; **no configuration mutation happens at all** | none | the captures stay; the live files are untouched | ordinary — nothing was changed |
| held buffer lost (interruption) | restore not issued | the on-disk capture's custody is unestablished | temporary file, if any, plus retained captures | `G-4`'s unverified procedure |

Two invariants across the table: **a guard that cannot answer refuses**, and
**a refusal produces reported residue, never a deletion and never a silent
success.**

### 6.6 The guards' own trust chain

The guards run `case_program.py` from the repository worktree, which is
group-writable by `discordbot` and `freedomweb` — residual `H-1`, decisions
`D5.0-12`/`OD-65` — and whose integrity rests on the review manifest digest
recomputed on the host at plan time. This is not new risk and this design does
not change it, but a design about identity that did not say where its own
instrument comes from would be incomplete. `G-3` addresses the **installed**
copy; the **bootstrap** copy remains covered only by `H-1`.

### 6.7 Independently safe recovery proceeds — [observation]

Account, group, membership, role, database and unit reversals depend on no
filesystem identity claim: their ownership comes from Band-0 absence baselines
and the two catalog-listing baselines. A failed guard must not suppress them, or
a root-replacement scenario would additionally leave three accounts, four
groups, a role and a database behind.

Their separate ownership basis, stated as §2 requires: each is an **observed
baseline** taken before any mutation (`getent` exit 2, or a catalog listing that
did not contain the name), paired with an attempt record. Neither reads nor
depends on the disposable root. This property holds today and is asserted by a
control in the reproduction suite so that a future change gating everything on
the guard would fail the suite.

### 6.8 The descendant inventory is rendered, not argued

§9.1's tables are generated into the rendered concrete plan from the plan's own
declared modes, so the replaceable subjects and the ambient-capability
identities are visible to every reviewer of every future revision rather than
asserted in prose here. Asserted against the generated plan by four tests in the
reproduction suite today.

---

## 7. Exact interface, argument, syscall, privilege and manifest impact

Requirement of PR-20260909-R2-2, point 4. **These are alternatives for review.
None is permission to implement a writer or extend the privileged surface.**

### 7.1 The preferred approach

| Surface | Change | Authorization impact |
|---|---|---|
| case-program verbs | **none.** No new verb, no changed arity, no new argument kind | — |
| privileges, identities, executables | **none** | — |
| materializer interface | **two new methods**: a bounded `capture(path, max_bytes)` read and a `restore(destination, content, …)` write (`G-1`) | **widening — maintainer decision.** It is a new *read* of a live file and a write of **observed** rather than manifest-pinned bytes |
| `mkroot` observations | five parent keys added; arity and arguments unchanged (`G-0`) | observation widening — flagged |
| target facts | five new, shipping `UNCONFIRMED`; the executor refuses while any is | requires the read-only preflight, which is Codex's |
| syscalls | `mkroot` gains `fstat` on a parent descriptor it already opens; the materializer's staged write uses `open(O_CREAT\|O_EXCL\|O_NOFOLLOW)`, `fchmod`, `fchown`, `fsync`, `rename` | the staged write is new; the two files are ones the materializer already writes |
| `concrete_plan.py` | `is_root_dependent`; one `REVALIDATE` before each root-dependent execution step; an immediacy clause | none |
| `cleanup.py` | the same for cleanup; `requires_revalidated` extended beyond `REVERSAL`; `RESTORE_NOT_VERIFIED`; `UNVERIFIED_RECOVERY_PROCEDURE`; two `CleanupOutcome` fields | none |
| `executor.py` | the guard skip generalised; C-1 … C-4 held-bytes handling; `G-3`'s pre-execution digest prerequisite; guard results threaded into `classify_cleanup` | none |
| cleanup state | S-B additionally for an unverified capture, an unmatched guard or a lost buffer; `preserved` unchanged in meaning | none |
| manifest | unchanged **file set**; every file above is already in `COVERED_SOURCES`; a version increment when implementation lands | regeneration through the non-executing path, twice, byte-compared |

### 7.2 What `G-2` costs operationally

128 additional `statroot` processes in a full run, counted in §6.2.2. Each is
read-only, bounded by the existing per-executable timeout, and creates nothing.
The run takes longer; no new object, privilege or identity exists because of it.
If that cost is judged unacceptable, the honest alternatives are candidate 2 of
§9.2 — fewer processes, a much larger interface change — or a narrower scope
decision recorded explicitly, **not** a silent return to cleanup-only guards.

### 7.3 The documented fallback, if `G-1`'s widening is refused

A read-only `digest <path>` verb on the case program — one `TARGET_PATH`
argument, no flags, no writes — used to compare the capture before the `install`
that restores it. This is the second revision's P3, kept here **without its
`[proved]` label**. It narrows the restoration failure from *"install arbitrary
substituted bytes"* to *"install bytes that matched at check time and were
swapped within one process spawn"*. It does not bind the write to the check, and
it must not be described as if it did.

This revision **recommends `G-1` over the fallback**, because the fallback adds a
verb to the reviewed grammar and still leaves the restoration dependent on a
second resolution of a pathname whose custody is the thing in question, while
`G-1` adds no verb and removes the second resolution entirely.

---

## 8. Residuals, restated with actor, prerequisite, interval and consequence

Requirement of PR-20260909-R2-2, point 5. Each names a specific actor, what that
actor must already have, the interval, what happens, and what the alternative
would be. **None is accepted here.** All remain unaccepted until a decision is
recorded.

**R-C8-1 — the create-to-identify interval.**
*Actor:* uid 0, or a `CAP_DAC_OVERRIDE` holder, with write access to the root's
**parent**. *Prerequisite:* that access, plus the ability to act between two
adjacent syscalls in one process. *Interval:* between `mkdir(2)` returning and
the following `open(2)` in `B3-01`. *Consequence:* the run records the
replacement's identity as its own; every later guard agrees with it, because
every guard compares against that recorded value. *Alternative:* none available
— there is no primitive that returns a descriptor to a newly created directory
(§1.3(a)). `G-0` narrows *who could have done it* to a reviewed, compared fact;
it does not close the interval. *Proposed disposition:* accept, conditional on
`G-0`'s parent facts being confirmed and compared.

**R-C8-2 — the guard-to-effect interval.**
*Actor:* uid 0, a `CAP_DAC_OVERRIDE` holder, or — for the two `0770` directories
— the `freedomsheet` account. *Prerequisite:* the corresponding write access,
plus the ability to act within one process spawn. *Interval:* between a
`statroot` guard's return and the following effect. *Consequence:* the effect
lands on a replacement the guard did not see. *Alternative:* a descriptor chain
inside the reviewed program closes every component **except the final one**
(§9.3); nothing closes the final one for a removal, because Linux has no
`funlinkat(2)`. *Proposed disposition:* accept for the final-component case;
route §9.3 as an available but expensive improvement for the rest, **not**
proposed for implementation now.

**R-C8-3′ — recovery after loss of the held buffer.**
Replaces the second revision's R-C8-3, which described a digest-to-install
window `G-1` does not have. *Actor:* none — this is a fault, not an adversary.
*Prerequisite:* the executor process ending between capture and restoration.
*Interval:* the whole run. *Consequence:* the only remaining recovery input is
the on-disk capture, whose custody is not established, so no automatic
restoration is performed and the run reports S-B with §6.4's procedure.
*Alternative:* a durable, integrity-protected copy of the captured bytes outside
the disposable root. That needs a new writable location, a new destination and a
retention decision, and is **not** proposed here. *Proposed disposition:* accept
the reported-S-B behaviour; route the durable-copy alternative separately.

**R-C8-4′ — removal of the seven replaceable probe subjects.**
Replaces the second revision's R-C8-4, whose recommendation rested on there
being no mechanism. There is one. *Actor:* the `freedomsheet` account. *Prerequisite:*
a running process as that account, in the interval. *Interval:* between the
subject's creation and its removal at cleanup. *Consequence:* `rm --force` on
one named non-directory removes a replacement rather than the created object.
*Alternative:* §9.5's exclusion boundary — establish and verify that no
`freedomsheet` process is running, and remove only then. *Proposed disposition:*
**refuse the blanket acceptance the second revision recommended.** Instead:
remove the seven only when §9.5's quiescence check passes, and report them
preserved when it does not. This does not make S-B universal, because the check
passes on an ordinary run.

**R-C8-5 — destination substitution in the restoration.**
*Actor:* uid 0, a `CAP_DAC_OVERRIDE` holder, or the `postgres` identity.
*Prerequisite:* write access to `/etc/postgresql/16/main/`. *Interval:* between
the staged write and the `rename(2)`. *Consequence:* known-good bytes are
renamed over an object other than the intended one. *Alternative:* hold a
descriptor on the destination directory and `renameat` relative to it, which
fixes the directory but not the final name. *Proposed disposition:* state and
route; not proposed for repair in this revision.

---

## 9. The alternatives, compared accurately

Requirement of PR-20260909-R2-3. Four substitution classes, eight candidates.

### 9.0 The four classes

* **W — whole-root replacement.** The object at the reviewed root path is
  replaced; the pathname still resolves.
* **D — deeper-directory replacement.** An intermediate component under the root
  — `journal`, `probe` — is replaced; the root is untouched.
* **F — final-entry replacement.** The last component of a path — a file or an
  empty directory being removed — is replaced.
* **C — in-place content mutation.** No object is replaced; the bytes inside one
  change.

### 9.1 The permissions inventory (retained, with two corrections)

| Directory | Mode / owner | May create, rename or unlink entries in it |
|---|---|---|
| the root's **parent** | **unknown — not a reviewed fact** | unknown. `G-0` |
| `…/fb-evidence-p5-0` (root) | `0755 root:root` | uid 0; `CAP_DAC_OVERRIDE` |
| `…/journal` | `0750 root:freedomjournal` | uid 0; `CAP_DAC_OVERRIDE` |
| `…/archive` | `0750 root:freedomcoord` | uid 0; `CAP_DAC_OVERRIDE` |
| `…/before` | `0700 root:root` | uid 0; `CAP_DAC_OVERRIDE` |
| `…/bin` | `0755 root:root` | uid 0; `CAP_DAC_OVERRIDE` |
| `…/probe` | **`0770 root:freedomsheet`** | uid 0; `CAP_DAC_OVERRIDE`; the `freedomsheet` account |
| `…/probe-ro` | **`0770 root:freedomsheet`** | uid 0; `CAP_DAC_OVERRIDE`; the `freedomsheet` account |

**9.1.1 Correction.** The second revision wrote *"any member of `freedomsheet`"*,
which reads as an open population. It is not: the plan creates the group
(`B2-03`), creates one account with it as primary group (`B2-06`), and adds that
account to `freedomjournal` (`B2-09`) rather than adding anyone to
`freedomsheet`. The population is **one account this run constructs**, and
`R-B-G-freedomsheet` refuses a host where the name already exists. This makes
§9.5 possible and it does **not** reduce the exposure to uid 0 or
`CAP_DAC_OVERRIDE`.

**9.1.2 Correction.** The seven replaceable subjects listed by the second
revision are unchanged and are asserted against the generated plan:

```text
…/probe/stage1.target      …/probe/stage1.moved
…/probe/stage2.target      …/probe/s4-1.target
…/probe-ro/s4-0.unlink     …/probe-ro/s4-0.moved
…/probe-ro/s4-2.target
```

`CAP_DAC_OVERRIDE` is held **ambiently** by `fbprobe` in `B5-E4`, `B5-E6` and
`B5-C6-01` … `B5-C6-04`, so an identity that may write in `…/before` and
`…/bin` is inside the plan.

### 9.2 The comparison

Cells read: **yes** = the class is prevented or reliably detected; **detect** =
detected before the dependent effect, not prevented; **no** = neither.

| Candidate | W | D | F | C | Implementation cost | Operational prerequisite | Authorization impact |
|---|---|---|---|---|---|---|---|
| **1. Per-step `statroot` guard** (`G-2`) | detect | no | no | no | moderate: plan generation, immediacy clause, executor skip | ≈89 extra processes per run | none |
| **2. Held root descriptor + `openat` chain inside the reviewed program** | yes | yes | no | no | **high**: every guarded effect must move out of `install`/`chattr`/`rm`/`rmdir` into the reviewed program | a new writer surface; reviewed vectors stop being the reviewed absolute paths for those steps | **large** — new verbs, new writes, a widened privileged interface |
| **3. `/proc/self/fd/N` prefixing** | yes | yes | no | no | high: descriptor inheritance into every permitted executable | procfs dependency; `contained_path` can no longer validate the vectors as written | moderate — the reviewed-vector property is lost |
| **4. `openat2(RESOLVE_BENEATH\|RESOLVE_NO_SYMLINKS)`** | yes | yes | no | no | moderate inside the reviewed program; Python 3.12 exposes no binding, so it needs a second `ctypes` exception | Linux ≥ 5.6, unverified on the target | moderate — a second foreign-call exception beside `PR_GET_SECUREBITS` |
| **5. Held-bytes recovery** (`G-1`) | — | — | — | **yes**, for the restoration source | moderate: two materializer methods, one gate, one state field | none | **maintainer decision** — the materializer writes observed bytes |
| **6. Content digest by pathname** (`digest` verb, §7.3) | — | — | — | detect | low | none | maintainer decision — one new verb |
| **7. Exclusion of concurrent writers** (`G-4`, §9.5) | no | no | **yes**, for the `freedomsheet` actor only | yes, same scope | low: one `LoadState` check, one applicability condition | the quiescence premises of §9.5 must hold | none |
| **8. Protected mount namespace** (§9.6) | partial | partial | no | no | high | the whole run in one namespace, which the process-per-step boundary forbids | large |

### 9.3 What candidate 2 actually buys, since the second revision denied it

`rename(2)`: *"Open file descriptors for `oldpath` are also unaffected."* A held
directory descriptor therefore continues to refer to the same object after its
name is renamed away, which a pathname identity comparison cannot reproduce: the
comparison describes an instant and stabilises no later lookup. Candidate 2 is
**strictly stronger** than candidate 1 for classes W and D. The second
revision's claim that its benefit "is already obtained by comparing the root's
identity" is withdrawn.

It remains **not proposed for implementation**, for a reason that is about cost
and authority rather than about capability: it moves deletion and flag changes
out of `rm`, `rmdir` and `chattr` — whose argument vectors the plan pins and
whose bounded behaviour is what makes cleanup reviewable — into the reviewed
program's own code, and that is a widening of the privileged interface which
this checkpoint is not the place to grant.

### 9.4 Why no candidate closes class F

Every removal names a final path component. `unlinkat(2)` takes `dirfd` plus a
pathname; `AT_REMOVEDIR` changes what may be removed, not how it is named.
Linux has no `funlinkat(2)` (FreeBSD 13 does). A descriptor-relative operation
fixes every component **except** the last, which is the one whose identity is in
question. This is a genuine platform limitation and it is the only one this
revision claims.

### 9.5 Exclusion of concurrent writers — how it would be established and verified

The `freedomsheet` account is the only actor in §9.1 that this run constructs and
can therefore reason about. Excluding it requires four premises:

1. **The account exists only for this run.** `R-B-A-freedomsheet` proves absence
   before creation; `CL-42` removes it. *Established by an observed baseline.*
2. **It has no interactive route.** `--system --no-create-home --shell
   /usr/sbin/nologin`, no password set. *Assumption A-3* — the password-field
   default is a distribution behaviour this repository has not recorded. **Proof
   obligation §13.1-2.**
3. **Every process the run starts as that account is synchronous.** The process
   boundary spawns each step as a direct child with `user=`/`group=` and a
   bounded timeout, and waits for it. *Established by the boundary's own
   contract, asserted by the suite.*
4. **The one asynchronous exception is stopped and confirmed stopped.**
   `B4-32`/`B4-33` start `fb-evidence-s4.service`, a transient unit running as
   `freedomsheet` with `ReadWritePaths=…/probe`. `CL-06` stops it.

**How `G-4` verifies it:** `systemctl show --property=LoadState
fb-evidence-s4.service` — a vector shape the plan already renders at `B4-34` —
must report `not-found` **before** the first removal under `…/probe` or
`…/probe-ro`. Where it does not, or where the reading cannot be made, the seven
subjects are **reported preserved** rather than removed, and the run is S-B for
that reason and names it.

**What happens if the exclusion cannot be proved:** exactly the above — residue,
not deletion. And premise 2 remains an assumption whichever way the check goes,
so `G-4` is labelled **[boundary]** and not **[observation]**; it excludes the
run's own concurrency, not an adversary who has already obtained the identity.

### 9.6 The protected namespace, stated as a trust-boundary design

A private mount namespace with the disposable root bind-mounted, established
through `systemd-run --property=PrivateMounts=yes` or an equivalent, would
prevent substitution performed *through a different view of the filesystem*. It
does not prevent `unlink` followed by a fresh creation inside the namespace by
an actor with DAC write access there, which is the substitution this design is
about.

It also requires the **whole run** to execute inside one namespace, and this
harness's boundary deliberately spawns one process per step so that each vector
is separately reviewed and separately bounded. Reconciling the two is an
architecture change, not a mechanism swap. It is named here because R2 asked for
it to be evaluated, and it is **not proposed**: a protected namespace is a
trust-boundary design requiring evidence, and no evidence for it exists in this
repository.

### 9.7 What is not asserted

* Not asserted: that descriptors alone solve every race. Candidate 2 leaves
  class F entirely open and class C entirely open.
* Not asserted: that DAC excludes an unrestricted root adversary. It does not,
  and §4.4's A-4 says so.
* Not asserted: that an interface limitation proves there is no safer
  architecture. §9.2 lists four designs safer than the current one.

---

## 10. The test matrix

Injected boundary and injected materializer only; every effect fake; no host
operation. Two labels, meaning different things:

* **[reproduction]** — asserts the behaviour of the **current, unfixed** tree.
  These are in the submission now, in
  `tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py`, and they will
  have to be inverted when a mechanism lands. **A passing reproduction is
  evidence that the defect is open. It is not a passed safety invariant.**
* **[proposed]** — cannot be written until the mechanism exists. Listed with its
  injected event, injection point, expected blocked effects and successful
  control so Codex can accept or reject the coverage at this checkpoint rather
  than after.

### 10.1 Implemented now, as reproductions and inventory

| # | Case | Injected event | Injection point | Asserted on | Label |
|---|---|---|---|---|---|
| 1 | root replaced between creation and first provisioning | `substitute_root()` | before `B3-03` | all four `install -d`, the flag changes and both captures are issued afterwards; **no `statroot` is issued anywhere in the execution phase** | [reproduction] |
| 2 | root replaced before a later experiment | `substitute_root()` | before `B5-C6-08` | the `chattr` and both captures are issued afterwards | [reproduction] |
| 3 | root replaced before cleanup | scripted `statroot` mismatch | `CL-37` | both restores issued, ≥30 root-referencing cleanup commands precede the only comparison | [reproduction] |
| 4 | unreadable root identity | scripted `unreadable` inode | `CL-37` | fails closed, and protects only the final `rmdir` | [reproduction] |
| 5 | **descendant replaced, root unchanged** | `substitute(…/probe/stage2.target)` | before `B4-19` | the `rm` consumes the **replacement's identity**, distinguished by value from the created object's, with its bytes | [reproduction] |
| 6 | **capture replaced before its restore** | `substitute(…/before/pg_hba.conf, content=…)` | before `CL-02` | the **bytes** that reach the live `pg_hba.conf` are the substituted bytes; run reports S-C, no configuration risk, no retained input | [reproduction] |
| 7 | ordinary cleanup completes | none | — | S-C, no residue, both restores issued | control |
| 8 | independently safe recovery proceeds | scripted mismatch | `CL-37` | `userdel`, `groupdel`, `DROP ROLE`, `DROP DATABASE` still issued | control |
| 9–12 | the §9.1 inventory | none | — | the two `0770` directories, the run's own renames/unlinks in them, the two ambient-`CAP_DAC_OVERRIDE` identities, the seven subjects, and the absence of any parent target fact — all against the **generated plan** | inventory |

Cases 1, 2, 5 and 6 are new in this submission and are the evidence correction
R2 required: they inject a substitution and assert **which object or which
bytes** an effect consumed, rather than checking that a named path was removed.

### 10.2 Proposed, unwritable until the mechanism exists

| # | Case | Injected event | Injection point | Expected blocked effect | Control |
|---|---|---|---|---|---|
| 13 | `G-2` blocks provisioning after a root replacement | `substitute_root()` | before `B3-03` | no `install -d`, no `install`, no `chattr` issued after the guard; run stops; nothing under the root removed | case 7 still S-C |
| 14 | `G-2` blocks a later experiment | `substitute_root()` | before `B5-C6-08` | the `chattr` and every subsequent root-dependent step are not issued | case 7 |
| 15 | `G-2` blocks the capture | `substitute_root()` | before `B6-01` | neither capture is written; `B6-M1`/`B6-M2` refused; **the live files are never modified** | a run reaching materialization normally |
| 16 | `G-2` fails closed on an unreadable identity | `statroot` refusal | any guard | as 13 | a readable guard proceeds |
| 17 | `G-2` immediacy is structural | — | plan generation | a plan separating a guard from its step is `PlanRefused` | the generated plan passes |
| 18 | `G-1` refuses a substituted capture | `substitute(…/before/pg_hba.conf)` | before `CL-02` | **no restore is issued**; file absent from `restored_files`; S-B; `UNVERIFIED_RECOVERY_PROCEDURE` reported; the live file's bytes are unchanged from the materialized ones | case 7's restoration writes the captured bytes |
| 19 | `G-1` refuses in-place content change of the capture | mutate the capture's bytes, identity unchanged | before `CL-02` | as 18. This is the case a descriptor would **not** catch and content comparison does | as 18 |
| 20 | C-2 disagreement before the first mutation | make the on-disk copy differ from the live read | before `B6-M1` | **no configuration mutation is attempted at all**; both live files untouched | matching digests proceed |
| 21 | failed capture | `capture()` raises / exceeds `max_bytes` | `B6-01` | as 20 | — |
| 22 | destination substitution | replace `/etc/postgresql/16/main/pg_hba.conf` | before `CL-02` | R-C8-5: **not blocked.** The test asserts the residual honestly — the bytes written are the held bytes, and the object written to is the replacement | — |
| 23 | interruption between staged write and rename | raise after the staged write | `CL-02` | live file unchanged; temporary file reported as residue; no partial content | an uninterrupted run renames |
| 24 | restart after buffer loss | new executor, retained captures on disk | cleanup | **no automatic reinstall**; `UNVERIFIED_RECOVERY_PROCEDURE` reported | — |
| 25 | successful restoration control | none | — | the bytes at the live file equal the bytes captured at C-1, by value | — |
| 26 | `G-3` blocks a tampered installed program | change `…/bin/case`'s bytes | before `B3-23` | the experiment is not issued | an untampered program runs |
| 27 | `G-4` quiescence | `LoadState=loaded` at cleanup | before `CL-17` | the seven subjects are **reported preserved**, not removed; run S-B and names why | `not-found` removes them and reaches S-C |
| 28 | replacement inside the guard-to-effect interval | substitute after the guard returns | between guard and effect | **not blocked.** Asserts R-C8-2 is a stated limitation, not a closed hole | — |
| 29 | replacement between `mkdir` and the identity read | model it in the fake | `B3-01` | **not blocked.** Asserts R-C8-1 in its honest form | — |

Every proposed case asserts the presence or absence of **specific commands and
specific bytes** in the fake's own log, not a final state label. Cases 22, 28 and
29 exist to prevent a future submission from claiming a closure it does not have.

**Model-level tests are not implementation evidence.** Cases 13–29 model a
proposal; none of them will be written until the mechanism they describe is
accepted and implemented, and none of them is offered as evidence for anything
in this document.

---

## 11. Erratum — corrections to the prior handback, dated 2026-09-09

Recorded here and repeated in
`docs/review/project-review-remediation-2026-09-09-handback.md` as a dated
erratum. The original text is **not** rewritten.

| Location | Statement | Correction |
|---|---|---|
| Handback §2.2, sixth bullet | *"**§6 guard-to-effect window** — stated as **not closable**. Linux has no `funlinkat`."* | The `funlinkat` fact is correct and narrow. The generalisation is not: it is not closable **for a removal that names a final path component**, which is class F. Classes W and D are reducible by a descriptor chain (§9.2, candidate 2) |
| Handback §2.2, fourth bullet | *"on Linux, **nothing does** … Creation and identity acquisition cannot be made atomic for a directory."* | Correct as stated for a **directory**, and it is retained. It does not support any wider impossibility claim |
| Handback §2.2, seventh bullet | P3 *"removes the highest-consequence effect from the identity argument altogether"* | Withdrawn. P3 hashes a capture and then reopens its pathname in another process; a substitution after the digest passes is installed. §5 replaces P3 with `G-1` |
| Handback §2.3 and design §9, R-C8-4 | recommending acceptance of the seven removals *"because (b) makes the S-B state meaningless"* | Withdrawn. §9.5 supplies a mechanism the second revision did not consider, and R-C8-4′ conditions the removal on it rather than accepting it blanket |
| Handback §3.3 | *"The material is in commits before this session."* | Not established. §12 states the observed scope |

---

## 12. The historical-claim correction

The prior handback asserted that the sanitized material was already committed
and that Git history was therefore the maintainer's disposition. **That
assertion is not supported and is withdrawn.**

What was observed, by read-only inspection of this repository only:

| Check | Result |
|---|---|
| `git status --porcelain` on the report | untracked (`??`) |
| `git ls-files --error-unmatch` on the report | not known to Git |
| `git log --all --oneline -- <report>` | no commits |
| `git log --all --oneline -S <former test name>` | no commits |
| `git status` on `tests/test_skills.py`, `models/skills.py` | modified, uncommitted |

**What this does and does not establish.** Within the scope of those commands —
this working tree and the refs reachable from it — the sanitized report is not
tracked and no reachable commit contains it or the former test name. This is
**not** proof of absence from every remote, from unreachable objects, or from
any copy outside this repository. Equally, nothing observed supports a claim of
historical exposure. No remote was contacted, no history was rewritten, and the
removed material is not reproduced anywhere in this document.

The synthetic skills fixture, the sanitized crafting report and the production
alias fix are preserved unchanged. That work is not reopened and no service was
restarted or contacted.

---

## 13. Proof obligations and unresolved dependencies

### 13.1 Proof obligations — things this design needs and does not have

1. **The root's parent's owner, group, mode, device and inode.** Needed by
   `G-0` and by A-1. Obtainable only through the read-only target preflight,
   which is authorized and **assigned to Codex**. This design does not perform
   it and does not ask to. Until then the five facts ship `UNCONFIRMED` and the
   executor refuses.
2. **Whether `useradd --system` leaves the account's password field locked on
   the target distribution.** Needed by A-3 and therefore by `G-4`'s premise 2.
   Not recorded anywhere in this repository. Until it is, `G-4` is a boundary,
   not an observation.
3. **Whether the target kernel provides `openat2(2)`** — candidate 4 needs
   Linux ≥ 5.6. Unverified; candidate 4 is not proposed, so this is only
   relevant if Codex prefers it.
4. **That the `systemd-run` transient unit is the only asynchronous
   `freedomsheet` process.** Derived from the plan and asserted by the suite
   against the generated plan; it would need re-asserting for any plan revision
   that adds one. The synchronous half is established: the boundary spawns each
   step through `subprocess.run` with `user=`, `group=`, `extra_groups=` and a
   bounded `timeout=`, and waits for it.
5. **The two live configuration files' sizes on the target.** Needed to choose
   `G-1`'s capture bound (§6.1.1). A read-only preflight observation; not
   obtainable from this repository, and not obtained here.

### 13.2 Unresolved dependencies

* **The C-7 conflict is unresolved**, three Band-7 cases remain open, twelve
  reviewed target facts are `UNCONFIRMED`, and `is_executable` is `False` for
  the independent EH-R16-4 reason. `G-0` would add five more unconfirmed facts
  of the same kind. Nothing in this design changes any of that, and supplied
  observations cannot establish that a missing producer exists.
* **`H-1` / `D5.0-12` / `OD-65`** — the group-writable worktree the guards' own
  bootstrap program comes from (§6.6). Unchanged and not addressed here.
* **The manifest.** No file in `COVERED_SOURCES` changed in this submission, so
  no regeneration and no version increment applies (§15). An accepted
  implementation would change covered sources and require regeneration through
  the non-executing path twice, byte comparison, and independent hashing.

---

## 14. What needs a decision, and who decides

| Id | What | Who decides |
|---|---|---|
| `G-0` | five parent target facts; obtaining them is the read-only preflight | maintainer, on Codex's recommendation |
| `G-1` | the materializer's capture/restore methods — a **read of a live file** and a write of **observed** rather than manifest-pinned bytes | **maintainer — it widens a privileged interface** |
| §7.3 | the fallback `digest` verb, if `G-1` is refused | maintainer — it adds a verb |
| `G-2`, `G-3`, `G-4` | execution-time guards, installed-program integrity, quiescence | Codex technical acceptance — no new verb, privilege, identity or executable |
| R-C8-1 | create-to-identify interval | maintainer, via Codex |
| R-C8-2 | guard-to-effect interval | maintainer, via Codex |
| R-C8-3′ | recovery after loss of the held buffer | maintainer, via Codex |
| R-C8-4′ | the seven probe subjects: remove **only** on a passing quiescence check | maintainer, via Codex |
| R-C8-5 | destination substitution in the restoration | maintainer, via Codex |
| — | the rest of §6 and §7.1 | Codex technical acceptance |

**None of these is decided by this document, by a passing test suite, or by a
reviewer acknowledging that the proposal is clearer than its predecessor.**

---

## 15. Status

Nothing in §6 is implemented. `cleanup.py`, `concrete_plan.py`,
`execution/executor.py`, `execution/case_program.py` and
`execution/materializer.py` are unchanged. The changes in this submission are
this document, the synthetic reproduction and fake improvements described in
§10.1, and the document corrections in §11 and §12.

No file in `COVERED_SOURCES` changed, so the review-input manifest digest is
unchanged at
`ec1e3e70b5d24aca911df9e4dcd394361ebffdb04b9587434cb74386756f2839`. **It is
review input and not execution approval. It must not be passed to `--execute`.**

Package 5.0 remains **not ready**, P5.0-R5 **Blocking**, OD-62 **Open**. The
shipped plan retains three unresolved C-7 cases, twelve unconfirmed facts and
`is_executable=False`. Migration 0014, product implementation, deployment,
cutover and Package 5.1+ remain unauthorized.

The next step is Codex's technical review of this design. Implementation follows
only an accepted mechanism, and only once any required maintainer expansion and
residual decisions are recorded.
