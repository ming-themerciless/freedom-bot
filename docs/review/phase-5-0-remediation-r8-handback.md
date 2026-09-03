# Package 5.0 — design remediation R8 handback

> **Superseded review history.** Revision 9 was independently re-reviewed on
> 2026-08-30 and returned changes requested. The active brief is the remediation
> R9 brief in `docs/review/Handover information`, and the active response is
> **[`phase-5-0-remediation-r9-handback.md`](phase-5-0-remediation-r9-handback.md)**
> with revision 10 of the package plan and the logical schema. This handback is
> retained as review history and grants no implementation authority. **Two of its
> statements were corrected by remediation R9** and are true only as a record of
> what revision 9 said: §4.1's nine-authority register, in which `A1` carries the
> whole of a flag change, and §4.3's `A1 + A3` / `A1 + A4` minimum combinations
> against root-owned inodes. `FS_IOC_SETFLAGS` also requires the caller to own
> the inode or hold `CAP_FOWNER`; see revision 10 §2.13.5c.

Date: 2026-08-30 · Package 5.0 — Migration and cutover harness

Prepared by: Claude — implementer and working Technical Lead (designated, OD-61)

Returned to: Peter Duscha (Acceptance Authority, Product Owner, Data Owner,
Operations Owner, Delivery Lead) and Codex (Independent Reviewer and independent
logical-schema reviewer, OD-61).

In response to: `docs/review/Handover information`, *Package 5.0 remediation R8 —
documentation and design instructions*, which **authorizes documentation and
design remediation only**. No production code, migration `0014`, database or
operating-system change, privileged probe, service change, Google access,
deployment, cutover, Package 5.1+ work or any environment mutation is authorized,
and none occurred.

> **Claude claims no finding closed.** P5.0-R1, P5.0-R4 and P5.0-R5 are closed by
> the Independent Reviewer, not here. **P5.0-R5 remains Blocking.**
>
> **The four R8 findings are conceded before any replacement is presented.** Each
> concession is written into the documents themselves — package plan
> **§2.13.1 rows 18–21** — *before* the corrections are stated, so a reader meets
> the defect first.
>
> - **R8-A.** Algorithm C's value table asserted *"In every row, produced <
>   validated ≤ consumed"* while its **first row** had `writer_deployment_digest`
>   consumed at **C1** and validated at **C2**. And the C2 comparison was not a
>   validation in any case: `PR`'s copy of the digest **came from** the supplied
>   value, so comparing them is a tautology that passes for any string, including
>   one describing no deployment on the host. **Nothing in revision 8 ever
>   compared the supplied digest with the deployed bytes.**
> - **R8-B.** `JNL-47` asserted that a failure injected in the privileged cleanup
>   leaves *"no `…/probe` or `…/probe-ro` residue"*; `JNL-48(d)` planted an
>   artifact *"made undeletable"* and asserted that the residue is **named by
>   path** and that `init-generation` then refuses at **C0**. **One injected
>   failure was required to leave the host in two mutually exclusive states**, so
>   both tests cannot pass against one implementation. Revision 8 also gave the
>   next invocation **two** behaviours: `verify-capability` cleaning residue as an
>   explicit first step, and `init-generation` refusing while it exists.
> - **R8-C.** `K3` was given as *"a holder of `CAP_LINUX_IMMUTABLE`"* and `K4` as
>   *"root with `CAP_LINUX_IMMUTABLE`"*. **`CAP_LINUX_IMMUTABLE` permits flag
>   control and confers no discretionary access whatever.** A non-root holder
>   clears `+i` on a `0440 root:freedomcoord` archive file and then receives
>   `EACCES` on the open. The register recorded an **achieved ability** where it
>   should have recorded **what an attacker must hold to achieve it**, and the
>   same conflation ran through F-2, F-4, F-5 and the `JNL-49`/`JNL-50` cases.
> - **R8-D.** **F-7** recorded the host identity as refused by *"the coordinator,
>   against the registered row — which is not on the restored tree"*. **The
>   registered row carries the same `host_machine_id` the seal does.** When
>   **A6** rewrites `/etc/machine-id` to the recorded value, all three copies
>   agree and **neither W10 nor C-d has anything to disagree with**. The device
>   and inode differences revision 8 leaned on are incidental: a restore that
>   changes them is refused as **F-5**/**F-10**/**F-11** by a *named* field, and a
>   restore that preserves them produces no refusal at all.
>
> **The preserved states are preserved.** P5.0-R1 and P5.0-R4 remain open;
> **P5.0-R2 remains closed**, and OD-55 and OD-58 remain preserved; P5.0-R5
> remains **Blocking**; D5.0-9 through D5.0-13 / OD-62 through OD-66 remain
> **open** and are not ruled from revision 8 or revision 9; the Security Reviewer
> remains **unnamed**; implementation remains **unauthorized**. The journal
> remains an **enumeration control, not a Google accepted-request completion
> barrier**, and **narrows R-5.0-8 by no case at all**. **R7-B's exact S4-2
> target and its positive DAC control are retained unchanged**; only their
> cleanup contract moves.

---

## 1. Finding-by-finding change table

| Finding | Classification | Conceded at | Replaced by | What a reviewer should check |
|---|---|---|---|---|
| **R8-A** — make Algorithm C's validation order truthful and executable | Blocking — integrity and production reliability | package plan **§2.13.1 row 18**, and again in §2.13.5a's *Why the order changed again in revision 9* | **new §2.13.2c** (the digest's computor, manifest and finality); **§2.13.5a** — **C0** computes and compares, **C1** consumes `DD`, **C2** recomputes and checks consistency, the **I-1 … I-5** invariant table, the **class**-annotated value table, the revised failure-cost table and the two-gate dependency graph; **§2.13.2a** (the deployment-binding paragraph); **§2.13.5b** **W11**; **§2.13.7** (`verify-capability` and `init-generation` preconditions); **§2.13.8** `JNL-46`; **§3** WP-15, WP-4b; **§9.3** stop condition **10j**; logical schema **§3.7** `writer_deployment_digest`, **§3.7.1**, **§9** | that **C0 computes the digest itself** and refuses on inequality, so nothing consumes an unvalidated external input; that **the supplied string is discarded at C0** and every later step consumes `DD`; that **C2's second computation** is what detects a deployment changed since C0; that the universal inequality is **withdrawn** and each row of the value table satisfies the invariant its **class** names; and that **I-2 (validate an external input against a source that is not itself) and I-3 (check an internal value before a persistent artifact depends on it) are genuinely different requirements** rather than one restated |
| **R8-B** — give cleanup failure one possible, recoverable outcome | Blocking — integrity and production reliability | package plan **§2.13.1 row 19**, and again at the head of **§2.13.2b** | **new §2.13.2b** — the three-state machine, the *two claims separated* paragraph, the single next-invocation rule and the *why refusal rather than automatic cleanup* argument; **§2.13.2a** (`verify-capability` step 2 rewritten, step 5 extended); **§2.13.5a** (the per-step failure-cost table, **C1**, **C2**, **C5**); **§2.13.4** (the transient row); **§2.13.7** (both lifecycle rows); **§2.13.8** `JNL-30`, `JNL-47`, `JNL-48(d)`; **§3** WP-8, WP-9, WP-15; **§7.1** row 26; **§7.4** **R-5.0-14**; **§9.2** an extended question; **§9.3** stop conditions **10f**, **10l**; logical schema **§4.3.8** Band 3, **§9** | that **“no generation or database artifact” is unconditional** in every state and every refusal above C5; that **“no transient residue” is written conditionally** everywhere it appears; that exactly **one** next-invocation behaviour is specified — refuse, never clean, never reuse — and that revision 8's automatic clean is actually removed rather than merely re-worded; and that `JNL-47` and `JNL-48(d)` now assert the **same** state for the same injected failure |
| **R8-C** — separate immutable-flag authority from DAC authority | Blocking — integrity and production reliability | package plan **§2.13.1 row 20**, and again at the head of **§2.13.5c** | **§2.13.5c**, rewritten: the **nine-authority register**, the *achieved ability versus the privileges that achieve it* table, the identity-boundary paragraph, the thirteen-row matrix with a **minimum combination** per row, the not-constructible table with two new capability-only rows, and five bounded claims replacing four; **§2.13.5b** (the verifier table); **§2.13.11** option J-2; **§3** WP-6, WP-8; **§6.5** items 18–19; **§7.1** row 24; **§7.4** **R-5.0-12** relabelled; **§9.2** a rewritten question; **§9.3** stop condition **10k** extended; **§2.13.8** `JNL-35`, `JNL-38`, `JNL-49`, `JNL-50`; logical schema **§3.7**, **§3.7.1**, **§9** | that **A1 confers no DAC** and that the register says so in the row itself, not in a note; that each F-row's **minimum combination can actually construct** its alteration; that **F-2 = `A1 + A2`**, **F-4 = `A1 + A4`** and **F-5 = `A1 + A3`**, and that each re-evaluation is right in both directions; that **`freedomsheet` is recorded as *holding* A2** rather than as denied it, so the flag and the empty bounding set are identified as the whole of what refuses a rewrite; and that the new `JNL-49`/`JNL-50` cases would in practice be **executed under a real capability set**, not as root |
| **R8-D** — correct or withdraw F-7's host-identity refusal | Blocking — integrity and production reliability | package plan **§2.13.1 row 21**, and again in §2.13.5c's *F-7, in full* | **§2.13.5c** — F-7's row, the *F-7, in full* subsection with its four-row remaining-evidence table, bounded claim 3 corrected and bounded claim 5 added; **§2.13.5** (the `host_machine_id` field row); **§2.13.5b** **W10** and the verifier table; **§2.13.6** **J-23**; **§2.13.8** `JNL-40`, `JNL-49` case 3; **§5.3** **option A-2**; **§7.1** row 25; **§7.4** **R-5.0-13**; **§9.2** a new question; **§9.3** stop conditions **10b**, **10h** extended; logical schema **§3.7** `host_machine_id` and *What this table cannot do*, **§3.7.1** (a new enforce/record row), **§9** (a new row), **§10** D5.0-13 | that the **refusal is withdrawn rather than re-worded**, and that no document still claims a detector; that the changed-device/inode reasoning is **withdrawn as incidental** and that the tests **name the field** when a device or inode refusal does occur; that the remaining operational evidence is an honest account of what a responder would have; and that **option A-2 is routed under §0.2 and not adopted**, with its restore cost stated rather than glossed |
| Correction found while remediating | — | — | **§2.13.5a** step **C5** | Algorithm C step **C5** still said *"every refusal above it leaves the tree untouched"* — a live instance of the R8-B defect that the brief did not name. It is corrected to *"creates no generation and no database artifact"*, with the transient-directory qualification pointing at §2.13.2b. **This was not an R8 finding**; it is reported because the brief requires every contradiction to be searched for rather than only the four named |

**No finding is claimed closed by this table.** It records what changed and where,
so the re-review can check the change rather than the claim.

---

## 2. The corrected Algorithm C value table, and the invariants that replace the inequality

The authoritative statement is package plan **§2.13.5a**, with the digest defined
in **§2.13.2c**. Reproduced here so the re-review can check it without turning
back.

### 2.1 What was wrong, in one paragraph

The digest reached `init-generation` as a string on the command line. **C1**
passed it to the probe, the probe copied it into `PR`, and **C2** compared `PR`'s
copy with the string. Two things follow. The comparison is **late** — C1 already
consumed it — and it is **vacuous**: both sides derive from the same input, so
the check passes for any value at all, including one naming no deployment on this
host. The design never compared the supplied digest with the deployed bytes.

### 2.2 The digest, defined before anything consumes it (§2.13.2c)

`deployment_manifest_digest(root)` is **one named function**, implemented once and
run by three actors: the deploy step, `init-generation` at **C0** and **C2**, and
the writer at **W11**. `JNL-46` asserts the three call sites produce identical
bytes for one tree.

| Covered | Detail |
|---|---|
| every regular file under `/opt/freedom-blades/sheet-writer/`, recursively | path relative to that root, mode, uid, gid, size, and SHA-256 of content |
| `/etc/systemd/system/freedom-sheet-writer.service` | the same five facts, under `unit:freedom-sheet-writer.service` |
| every drop-in under `…/freedom-sheet-writer.service.d/`, sorted | the same five facts, under `unit.d:<name>` — **included because a drop-in changes the directives Stage 4 attests without touching the unit file** |
| `manifest_format_version` | first field, so a later manifest definition is a visible versioned change |

Excluded deliberately: symlink targets outside the two roots (the symlink's own
path, mode and target string are covered as content), timestamps and inode
numbers (they differ between two byte-identical deployments), the Google
credential wherever D5.0-12 places it (it is not the writer's code, it rotates
separately, and hashing a credential into a sealed artifact is a disclosure this
design will not make), and anything under `/var/lib/freedom-sheet-writer` (that
is state, and including it would change the digest at every appended record).

**It becomes final** at the end of the deploy step that installs those files and
runs `systemctl daemon-reload`, and is invariant until the next deployment, which
**forces a rotation** (**J-22**, **F-6**). It is therefore final before **C0**,
which already requires the unit deployed.

**The operator still supplies it**, because a generation must be sealed against a
deployment somebody *meant*. Without a supplied value `init-generation` would
seal whatever happened to be on disk — a half-finished deploy, a rollback in
progress, a drop-in added minutes earlier — and the first evidence of the mistake
would be `SW-J22` at the next writer start.

### 2.3 The corrected steps

| Step | What changed |
|---|---|
| **C0** | additionally **computes** `DD = deployment_manifest_digest()` and **refuses unless the supplied value equals `DD`**. The supplied string is then **discarded**; every later step consumes `DD`. C0 also refuses on a malformed supplied value, and refuses — **without cleaning** — while `…/probe` or `…/probe-ro` exists |
| **C1** | records **`DD`** in `PR`, not the operator's string, which no longer exists at this point. A failed `finally` ends the run in §2.13.2b state **S-B** and no later step executes |
| **C2** | keeps the report checks; `PR.writer_deployment_digest == DD` is now a **consistency** check over an already-validated value; and root **recomputes** `deployment_manifest_digest()` and refuses on any change — **the only thing that detects a deployment changed between C0 and the probe's capture** |
| **C3** | carries `DD` into `SB` as `writer_deployment_digest` |
| **C5** | its *"leaves the tree untouched"* claim is corrected to *"creates no generation and no database artifact"* — invariant **I-4** |

### 2.4 The invariants that replace the universal inequality

*"produced < validated ≤ consumed"* cannot hold for every value: values produced
**inside** the algorithm are checked after their producing step and often after a
later step has used them as an input, and derived values are not validated at
all. Stating one inequality for all of them either forces a false claim or forces
*validated* to mean two things in one table.

| # | Invariant | Applies to | What it forbids |
|---|---|---|---|
| **I-1** | production strictly precedes first consumption | every value | a step consuming a value a later step produces — the R7-A defect |
| **I-2** | **pre-consumption validation of external inputs**, against a source **independent of that value**: `produced < validated ≤ first consumed` | the supplied digest, the deployed unit and drop-ins, the predecessor `.close` manifest, the absence of both transient directories | consuming caller-supplied text before checking it against the host, and “validating” it against a copy of itself — **the R8-A defect** |
| **I-3** | **post-production consistency checking of internal values**: `produced < checked ≤ first persistent dependence` | `PR` (C2 → C9), the journal file (C6, C7), the seal file (C10) | sealing a probe result nothing examined; setting an attribute and not re-reading it |
| **I-4** | **no persistent artifact before the checks** — C5 is the first, C13 the first row | the whole algorithm | a refusal at C0 … C4 leaving a half-created generation |
| **I-5** | **derived values carry no validation row**; a later reader re-derives them | `probe_report_digest`, `seal_body_digest`, `G`, `genesis_record_digest`, `BND`, `seal_digest` | inventing a validation step for a value nothing could disagree with |

### 2.5 The value table, with its class column

| Value | Class | Produced | Validated / checked | First consumed |
|---|---|---|---|---|
| supplied `writer_deployment_digest` | **I-2** | operator, before C0 | **C0** — well-formed, **and equal to `DD`** | **nothing.** Discarded at C0 |
| `DD` | **I-3** | **C0** | C0 (against the supplied value); **C2** (recomputed, and vs `PR`) | C1, C3 |
| deployed unit and drop-ins | **I-2** | deployment | **C0** deployed and inside `DD`'s manifest; **C1** S4-3 hashes the applied set | C0, C1 |
| `…/probe`, `…/probe-ro` absent | **I-2** | — | **C0**, refusing rather than cleaning | C1 creates them |
| predecessor sealed, archived, `.close` verified | **I-2** | predecessor `seal` | **C0** | C3 |
| `PR` and every case result | **I-3** | **C1** | **C2** | C2, C3 |
| `probe_report_digest` | **I-5** | C2 | — (re-derived at **W4**) | C3 |
| `SB`, `seal_body_digest` | **I-5** | C3 | — (re-derived at **W3**, and vs record 0 at **W13**) | C4 |
| `G`, `genesis_record_digest` | **I-5** | C4 | — (re-derived at **W5**) | C5, C8 |
| the journal file | **I-3** | **C5** | **C6** (`+a`), **C7** (`st_dev`) | C7 |
| `journal_device`, `journal_inode` | **I-5** | C7 | — (compared at **W7**) | C8 |
| `BND` | **I-5** | C8 | — | C9 |
| the seal file | **I-3** | **C9** | **C10** (`+i`) | C12 |
| `seal_digest` | **I-5**, leaf | C12 | — | C13 |

**Every I-2 row is validated at or before first consumption against a source that
is not itself; every I-3 row is checked before the first persistent artifact
depends on it; every I-5 row is a pure function a later independent reader
re-derives. I-1 holds for every row without exception.**

`JNL-46` grows from one case to **five**: the ordered walk asserting I-1 … I-5
and the three-call-site identity of the digest function; **a malformed supplied
digest** refused at C0 with the probe never run; **a well-formed but wrong
supplied digest** refused at C0 by comparison with `DD` — *the case revision 8
could not catch*; **a deployed file or drop-in changed between C0 and C1**
refused at C2 by the second computation; and **a report whose
`writer_deployment_digest` differs from `DD`** refused at C2. In all four
failure cases the run refuses before **C5** and creates **no journal file, no
seal, no `current` symlink, no `.close` manifest and no database row**.

---

## 3. The cleanup state machine

The authoritative statement is package plan **§2.13.2b**.

**The two claims, separated — and this is the whole correction.** *"No generation
or database artifact"* is **unconditional** and survives every state, because
nothing under `…/journal` is created before **C5** and no row before **C13**.
*"No transient residue"* is **conditional on cleanup succeeding**, and revision 8
stated it as though it were unconditional.

| State | Reached when | Transient residue | Generation artifact | Database row | Exit | Operator sees |
|---|---|---|---|---|---|---|
| **S-A** | a Stage 1–4 case is `failed` or `inconclusive`, **and** the `finally` removes both directories | **none** | **none** | **none** | non-zero, **code 2** | the failing case, its expected and observed result, its `errno`, and a line confirming cleanup completed |
| **S-B** | the `finally` cannot remove some artifact — an attribute it cannot clear, an I/O error, `ENOSPC`, a directory that will not `rmdir` — **whether or not a probe stage also failed** | **exactly the artifacts it could not remove**, each by **absolute path**, with the operation attempted and its `errno` | **none** | **none** | non-zero, **code 3**, distinct from S-A | the failing case if any, **and** the residue report, **and** a line stating that operator recovery is required before another generation can be created |
| **S-C** | all four stages pass and both directories are removed | **none** | created by C5 … C11 after C2 admitted the report | inserted separately at C13 | zero | the values to pass to `RegisterJournalGeneration` |

**The next invocation: one behaviour, and it is refusal.** Both
`verify-capability` and `init-generation` **C0** refuse while either directory
exists, report every residual artifact by path, and **do not clean it**. Recovery
is a named operator procedure in the WP-9 operations document: read the reported
paths, `lsattr` each, clear `FS_IMMUTABLE_FL` or `FS_APPEND_FL` as root where
that is why removal failed, remove the artifacts and directories, re-run.
**Revision 8's automatic clean-and-reuse step is withdrawn, and no separately
named privileged cleanup command is introduced.** The brief permits one of the
two; this design takes the refusal.

**Why refusal.** The residue is by construction something the privileged cleanup
already failed to remove **as root, in a `finally`, with `CAP_LINUX_IMMUTABLE`
available**. A second automatic attempt by the same code with the same authority
has no reason to succeed, and if it did succeed it would mean the first failed
for a reason nobody investigated. An automatic clean would also give
`verify-capability` a routine path that deletes a directory the writer's identity
can write — the class of act stop condition **10f** exists to forbid. The refusal
is the cheaper failure: both directories hold **no evidence**, so what is lost is
generation creation until someone looks. That cost is **R-5.0-14**.

**Evidence.** `JNL-47` — **six cases**: four probe-stage injections producing
**S-A**, and **two** cleanup-failure injections producing **S-B**, one after a
probe-stage failure and one after a **fully passing** probe, because a cleanup
can fail on a run in which nothing else did. Each asserts **exit status**, **safe
path reporting**, **generation and database absence**, **residue state**, **next-run
behaviour** and **recovery**. `JNL-48(d)` produces S-B at the Stage-4 level and
asserts the same. `JNL-30` asserts that planted residue is **reported and
refused**, never cleaned and never reused, and is byte-for-byte unchanged after
the refusal.

---

## 4. The corrected capability matrix

The authoritative statement is package plan **§2.13.5c**, rewritten.

### 4.1 The nine authorities

| # | Authority | Minimum holder here | Confers | Does **not** confer |
|---|---|---|---|---|
| **A1** | flag control — set/clear `FS_APPEND_FL`/`FS_IMMUTABLE_FL` on an inode already reachable and openable under DAC | `CAP_LINUX_IMMUTABLE`; root; grantable as an ambient capability. **Unreachable from the writer** | making an `+a`/`+i` inode writable *in principle* | **any discretionary access at all.** *This is the whole of R8-C* |
| **A2** | DAC on the live journal **file** (`0640 freedomsheet:freedomcoord`) | **`freedomsheet` itself, by ownership**; uid 0; `CAP_DAC_OVERRIDE` | writing the journal's bytes **once `+a` is gone** | writing them while `+a` is set (A1); the directory, the seal or the archive |
| **A3** | DAC on `…/journal` (`0750 root:freedomjournal`) and on the seal (`0440 root:freedomjournal`) | **uid 0 or `CAP_DAC_OVERRIDE` only.** No group or other identity | replacing the journal inode; writing the seal | the journal file's bytes while `+a` is set; the archive; PostgreSQL |
| **A4** | DAC on `…/archive` (`0750 root:freedomcoord`) and its `0440 root:freedomcoord` files | traversal: `freedomcoord`, uid 0, `CAP_DAC_READ_SEARCH`. **Write: uid 0 or `CAP_DAC_OVERRIDE` only** | altering an archived artifact **once `+i` is gone** | clearing `+i` (A1); the registered `predecessor_close_digest` |
| **A5** | DAC on the deployment path and its unit and drop-ins | uid 0, `CAP_DAC_OVERRIDE`. **H-1**: the repository copy is group-writable by `discordbot` and `freedomweb` | changing what the writer computes at **W11** | the digest recorded in the seal (A1 + A3) |
| **A6** | host identity and restoration control — write `/etc/machine-id`, or restore onto a controlled host | root on whichever host the tree is read on | defeating **W10** — **and C-d**, revision 9 states | the production PostgreSQL, which is not on the restored tree |
| **A7** | full host-root identity | root | **A1 … A6**, and `setuid` to `freedomcoord`, hence **A8** | **A9.** Root here is not a PostgreSQL superuser |
| **A8** | coordinator execution and authentication → `INSERT` | the `foundry` account via `sudoers`; A7 | inserting generation and evidence rows | `UPDATE`/`DELETE`/`TRUNCATE` |
| **A9** | PostgreSQL mutation or direct datafile access | a PostgreSQL **superuser**, or the `postgres` OS user. **Nobody in this design** | changing a registered digest | any host artifact |

**A7 is listed as its own row** because it is how the DAC rows are acquired in
practice, and because a matrix that omits it invites the reader to imagine an
attacker holding one DAC row without the rest.

### 4.2 Achieved ability versus the privileges that achieve it

| Achieved ability | Revision 8 called it | It actually requires |
|---|---|---|
| “archive write” | `K4`, *"root with `CAP_LINUX_IMMUTABLE`"* | **A1 + A4.** A non-root holder of A1 alone clears `+i` and gets `EACCES` on the open |
| “journal-content rewrite” | `K3`, *"a holder of `CAP_LINUX_IMMUTABLE`"* | **A1 + A2** — and **A2 is `freedomsheet`'s own**, so A1's absence is the *whole* of what refuses the writer |
| “replace the journal file” | `K2`, directory write alone | **A1 + A3.** An `+a` victim cannot be unlinked or renamed over (probe cases **P-4**, **P-5**) |

### 4.3 The re-evaluated rows

| Row | Revision 8 | Revision 9 | Why |
|---|---|---|---|
| **F-1a** | `K1` | **A1 + A3** | clearing `+i` and writing a `0440` root-owned file in a root-owned directory are two authorities. **And revision 9 adds the honest qualification**: every real holder of A3 also holds A2, so F-1a is separated from F-1b by *what was altered*, not by *what could be* |
| **F-1b** | `K1 + K3` | **A1 + A2 + A3** | the same, plus the journal file |
| **F-2** | `K3`, *"every route needs root"* | **A1 + A2** | **the second half was wrong in the DAC direction.** `freedomsheet` owns the journal file at `0640` and holds A2; what it lacks is A1, and only A1 |
| **F-3** | `K8` / `K7` | **A9** for mutation, **A8** for insertion | relabelled; the property is unchanged |
| **F-4** | `K4` alone | **A1 + A4** | clearing `+i` is not writing a `0440 root:freedomcoord` file; **`freedomcoord` membership confers read and traverse only** |
| **F-5** | `K2` alone | **A1 + A3** | an `+a` victim cannot be unlinked or renamed over, so the flag must be cleared first |
| **F-6** | `K5` | **A5** | relabelled |
| **F-7** | `K6`, refused by the coordinator | **A6, refused by nothing** | §5 below |
| **F-8 … F-12** | `K1` | **A1 + A3** | all are seal writes |

### 4.4 The not-constructible table, and its two corrected rows

| Identity or capability set | Sought | Constructible? | Control |
|---|---|---|---|
| `freedomsheet` | **A2** on the journal file | **Yes — it holds it, by ownership.** *Revision 8 recorded this as “No”, which was wrong: `0640` gives the owner `rw`* | **nothing in DAC refuses it.** `FS_APPEND_FL` refuses the non-append write, and the empty `CapabilityBoundingSet=` with `NoNewPrivileges=true` puts A1 out of reach. **This row is why those two directives are load-bearing rather than defence in depth** |
| **a non-root process holding `CAP_LINUX_IMMUTABLE` and nothing else** — new | **A4** archive write | **No** | it clears `+i` **successfully** and then receives **`EACCES`** on the `O_WRONLY` open. **This is the row revision 8 got wrong**, and `JNL-50` case 9 executes it |
| **the same capability-only identity** — new | **A3** journal-directory write | **No** | `0750 root:freedomjournal` with no `w` for group or other; clearing a flag changes no directory permission → `EACCES`. `JNL-50` case 10 |
| `freedomcoord` | **A4** archive **write** | **No** | membership gives traverse and read on `…/archive` and read on its `0440` files; **it confers no write on any of them**, and the coordinator holds no A1 |

The remaining rows — `freedomsheet` against A1, A3 and A4; `freedomsheet` against
the database; `freedomcoord` against A2/A3 and A9; `discordbot`, `freedomweb` and
`foundry` against `…/journal` — are unchanged in substance and relabelled.

### 4.5 The bounded claims

Claim 1 (rows refused by an actor that did not author the artifact) now excludes
**F-5** deliberately and says why. Claim 2 (nine rows refused by the writer
alone) is unchanged. **Claim 3 is corrected**: revision 8 attached *"and a forged
`machine-id` under F-7"* to F-1b's coordinator refusal, and that is withdrawn.
Claim 4 (**R-5.0-12**) is unchanged and relabelled. **Claim 5 is new**: one
alteration has **no detector in this design at all**, and it is F-7.

**Evidence.** `JNL-49` and `JNL-50` grow to **ten cases each**. Every case is
executed under an identity and capability set that really holds the stated
combination — `setpriv --reuid`/`--regid` and `--ambient-caps` rather than a root
process standing in for one. New in `JNL-49`: **case 9** proves F-5's corrected
minimum (`A3` alone gives `EPERM` on the `+a` victim; only `A1 + A3` succeeds),
and **case 10** proves F-2's (`freedomsheet` with an ambient
`CAP_LINUX_IMMUTABLE` and no other privilege rewrites record 0). New in
`JNL-50`: the two capability-only rows above.

---

## 5. The corrected F-7 outcome

**Option 1 of the two the brief offers is taken: a forged matching host identity
is classified as a residual that neither W10 nor C-d detects.** Option 2 is
specified and **routed**, not adopted.

**What the design does.** `SB.host_machine_id` is fixed once at **C3** and sealed
under `+i`. **W10** compares it with `/etc/machine-id`. **C-d** compares the
registered `host_machine_id` with the value read from disk, which is
`SB.host_machine_id`. All three copies record the **same fact**, taken at the
same instant, from the same host.

**What that means when the fact is forged.** An actor holding **A6** rewrites
`/etc/machine-id` on the host where the tree is read. The three copies agree.
**W10 passes. C-d passes.** Storing a copy outside the restored tree creates no
mismatch, because the copy stored there is the same forged-to-match value. **This
design contains no independent host-bound authenticated value.**

**Why device and inode are withdrawn as a substitute.** A restore that changes
`st_dev`/`st_ino` is refused at **W7** with `SW-J11` and at **C-d** on
`journal_device`/`journal_inode` — that is **F-5**, **F-10** or **F-11**, and the
refusal names *those* fields. A restore that **preserves** them is refused by
nothing. A detector that fires only when a different, named field happens to
differ is not a host-identity detector.

**The independent operational evidence that remains.**

| Evidence | Establishes | Does not |
|---|---|---|
| the **production PostgreSQL**, absent from the restored tree | a forged tree is **inert** until its holder also reaches the coordinator (**A8**) and, for registered rows, **A9** | detect the forgery |
| `sudo log_output`, journald, `audit_events` | where `init-generation` and `register-journal-generation` actually ran, under whose account, when | hold if the attacker also holds A7 where those records live |
| the **archive** on the production host | a forged head has no `seal` record, no `.close` manifest, no archived predecessor | distinguish two hosts claiming one identity |
| the production host's systemd and deployment records | that the real writer unit ran on the real host with the deployment `DD` names | act as a refusal any algorithm here makes |

**Option A-2, routed under §0.2 and not adopted.** A TPM-sealed or
coordinator-signed host token, provisioned once per host by the Operations Owner
before the first `init-generation`, rotated by forcing a rotation exactly as a
redeployment already does, and verified by a new **V-W** step and a new
coordinator comparison. It would make F-7 a refusal. Its cost is a new secret
with a custody model, a hardware or credential dependency, a seal field, a
refusal code beyond `SW-J25`, a §2.13.6 condition, a column in
`sheet_writer_journal_generations`, at least three new `TC-5.0-JNL` cases — and,
**the price that matters, a legitimate restore onto replacement hardware that
fails closed**, in a design whose purpose is that evidence survives a restore. It
is recorded at package plan **§5.3** and open-decisions **OD-66**, and it is the
Acceptance Authority's.

**No test asserts a C-d refusal here.** `JNL-40` carries **two** cases: unforged,
in which W10 refuses with `SW-J23` and C-d with `J-16`; and forged-to-match with
device and inode preserved, in which **W10 is asserted to pass and C-d is asserted
not to refuse on `host_machine_id`**. Where the harness cannot preserve device
and inode, the case asserts that the refusal that does occur is `SW-J11` at W7
and **names that field**. `JNL-49` case 3 is rewritten to the same rule.

---

## 6. Schema, evidence, estimate, RAID and decision impacts

| Area | Effect |
|---|---|
| **Schema objects** | **None.** No column, constraint, index, trigger, sequence, vocabulary, table, command or health check changes. `append_only_probe_version` still reads `jnl-probe-1`; what that value denotes gains a pre-consumption digest validation and a cleanup state machine — a change to the procedure the closed vocabulary names, not to the vocabulary |
| **Logical schema wording** | §3.7's `writer_deployment_digest` and `host_machine_id` rules and *What this table cannot do*; §3.7.1 gains a **host identity** enforce/record row; §4.3.8 Band 3's counts and prerequisites; §9 gains **two** rows and rewrites three; §10's D5.0-13 and D5.0-8 entries. **Two of these correct claims this artifact itself made** |
| **Evidence band** | **Fifty identifiers, unchanged. Seventy-four → eighty-four cases.** `JNL-46` 1 → **5**, `JNL-47` 5 → **6**, `JNL-49` 8 → **10**, `JNL-50` 8 → **10**, `JNL-40` 1 → **2**. `JNL-30` and `JNL-48` change contract without changing count. **No identifier is added**, because every correction is a change to an existing case's contract or an added case under an existing identifier |
| **§6.5** | eighteen → **nineteen** items |
| **Falsification rows** | **Thirteen, unchanged.** R8-C re-evaluates rows and R8-D reclassifies one outcome; neither adds nor removes a row |
| **§2.13.6 conditions** | **Twenty-five, unchanged**; `SW-J01 … SW-J25` unchanged. **J-23**'s description is narrowed to the unforged mismatch. **No condition is added, because R8-D removes a claimed detection rather than adding one**, and C0/C2 refusals are `init-generation` exits rather than writer or coordinator conditions |
| **Numeric controls** | **Nine, unchanged.** N5.0-21 … N5.0-23 untouched |
| **Stop conditions** | **10l added.** **10b** extended (a forged matching machine-id may not be described as detected), **10f** extended (residue may not be reused, silently removed or treated as absent, and only one next-invocation behaviour may be specified), **10h** extended (a comparison is not a detector unless its two sides can differ under the threat claimed; no test may assert a refusal without naming the field whose inherent mismatch the threat proves), **10j** re-worded to **I-1 … I-5**, **10k** extended (a capability may not be credited with an access it does not confer; cases must be executed under a real capability set) |
| **Estimate** | PERT **39.5 → 40.4** implementer-days. WP-8 **+0.53**, WP-15 **+0.20**, WP-9 **+0.12**, WP-4b **+0.08**; WP-1, WP-2, WP-3, WP-4, WP-6, WP-7, WP-14 unchanged. Work-package table totals **19.7 / 39.3 / 65.5**, `(19.7 + 157.2 + 65.5) / 6 = 40.4` |
| **Allowance and contingency** | remediation allowance 11.5 → **11.9** (30 % of ML). **Contingency stays at 4.0** — none of R-5.0-12, R-5.0-13 or R-5.0-14 is work this package can do; two are residuals for the Acceptance Authority and the third is an operator path already inside WP-9 |
| **Security review** | **2.5–3.5 → 3.0–4.0 reviewer-days**, with **surfaces unchanged at eleven** and **two added questions**. The cost is the nine-authority model whose combinations must each be checked against real Unix DAC, and a **second** unrefused residual. Independent implementation review 2.5–3.0 and schema re-review 0.5–1.0 are unchanged |
| **§7.1 risk rows** | **25** (forged host identity) and **26** (residue state) added; row 24 retained and relabelled |
| **RAID** | **R-5.0-13** and **R-5.0-14** added. **R-5.0-9** extended to the whole §2.13.2c manifest — including drop-ins — and to S-B residue. **A-5.0-5** widened to a non-root ambient `CAP_LINUX_IMMUTABLE` set and a second host, and **remains unconfirmed**. **D-5.0-1** and **D-5.0-2** extended. R-03's estimate → **40.4** |
| **Decisions** | **No decision number added.** **D5.0-13 / OD-66 option A's content changes in two places**; **option A-2 is raised inside it and not adopted**. D5.0-9 … D5.0-12 untouched. OD-55, OD-58 preserved |
| **Governance** | implementation-plan §20 names revision 9 as the response to the R8 brief; status, RAID, decision register, open decisions and the change log (**C-P5.0-Q**) all record it; the R7 handback is marked superseded and retained |

### Figures whose matrix changed but whose value did not, explained

| Figure | Value | Why unchanged |
|---|---|---|
| falsification rows | **13** | R8-C changes what each row *requires* and R8-D changes what one row *concludes*; neither adds or removes a row |
| `TC-5.0-JNL` identifiers | **50** | all ten added cases sit under existing identifiers. A new identifier would have implied a new requirement; there is none |
| fail-closed conditions and refusal codes | **25**, `SW-J01 … SW-J25` | R8-D **removes** a claimed detection; R8-A and R8-B change `init-generation` exits, which are not writer or coordinator conditions; R8-C changes classification, not mechanism |
| numeric controls | **9** | nothing here introduces a threshold |
| security-review surfaces | **11** | R8 adds no host artifact. `…/probe-ro` was already surface 11's element at R7-B; the reviewer-day rise is depth, not breadth |
| V-W steps | **18** | W10's and W11's contracts are narrowed and re-pointed; **no step is added or removed** |
| work packages | **14 active** | no package added or removed |
| contingency | **4.0** | see above |
| independent implementation review | **2.5–3.0** | the implementation surface is unchanged |
| schema objects | **0 changed** | every correction is host-side or a wording correction |

---

## 7. Exact documentation checks, and their results

Every command was run in `/opt/freedom-blades/platform` on 2026-08-30. **All are
read-only or act on documentation files in the working tree.** No test suite was
run, and none is required for a documentation-only remediation; **no result from
an earlier tree is carried forward as current evidence.**

| # | Check | Result |
|---|---|---|
| 1 | `cat "docs/review/Handover information"` | the R8 instructions, read in full |
| 2 | `CLAUDE.md`, then `.agents/AGENTS.md` and `docs/implementation-plan.md` read in full | as `CLAUDE.md` and §16.1 require, **before** any edit |
| 3 | `wc -l` and heading inventories over the two design artifacts and the five registers | the revision-8 tree located; package plan 3920 lines, logical schema 2034 |
| 4 | `sed -n` reads of package-plan §§1–2.13.11, 3, 4, 5.3, 6.5, 7.1, 7.4, 9.1–9.4, 10, 12, and logical-schema §§0–4.3.8, 9, 10 | the revision-8 text under remediation |
| 5 | `git status` before and after | only the intended documentation files, plus the pre-existing unrelated worktree changes, which were **preserved** |
| 6 | **Markdown table-integrity check**, programmatic, over both design artifacts: for every table, every body row's column count compared with its header, **ignoring escaped `\|`** | **no column-count mismatch** in either artifact. Run after the final edit. A naive count reported twelve apparent mismatches, all of which are escaped pipes inside cells (`O_WRONLY\|O_TRUNC` and similar) and none of which is a broken table |
| 7 | `git diff --check` | **exit 0, no output.** Re-run after the final edit |
| 8 | `git diff --no-index --check /dev/null <file>` for the package plan, the logical schema and the R7 handback | **no whitespace error reported for any of them.** Each exits 1 because the file differs from `/dev/null`; a control file containing one trailing space was checked the same way and produced `trailing whitespace` with **exit 3**, so the absence of output is a real result and not a silent failure. Stated because the design artifacts are **untracked** in this worktree, so `git diff --check` alone does not inspect them |
| 9 | the stale-form searches of §9 below | recorded there |

---

## 8. Checks not run, their reasons and their accountable owners

Stated because the handoff requires it and because stop condition 10b forbids
describing an unproven property as proven.

| Check | Why not run | Owner |
|---|---|---|
| The `TC-5.0-JNL` band, all **eighty-four** cases | **the code does not exist and is not authorized.** Every case is a planned assertion, not a result | Technical Lead, after D5.0-13 and implementation authority |
| `verify-capability` and its four stages, including **S4-0** and the `…/probe-ro` lifecycle | **no probe was run; neither transient directory was created.** It needs root, `chattr`, `setpriv`, `systemd-run` and a durable hierarchy that does not exist on this host | Operations Owner — **A-5.0-5, unconfirmed** |
| `deployment_manifest_digest()` at its three call sites (`JNL-46` case a) | the function does not exist; the deployed writer tree does not exist | Technical Lead |
| The construction-order harness and its four digest cases (`JNL-46`), and the six failure injections (`JNL-47`) | the same: `init-generation` does not exist | Technical Lead |
| The **§2.13.2b** state machine, including a real cleanup failure | it needs a privileged run against a real hierarchy. **No residue was produced and none is claimed** | Operations Owner and Technical Lead |
| The capability matrix (`JNL-49`, `JNL-50`), **including the non-root `CAP_LINUX_IMMUTABLE`-only cases** | it needs real OS identities, real ambient capability sets and a real database. **No `setpriv`, no `--ambient-caps`, no combination was executed and none is claimed to have been** | Operations Owner and Technical Lead — **A-5.0-4** and **A-5.0-5**, both unconfirmed |
| `JNL-40`'s forged-matching host case | it needs a second host, or a disposable host whose `/etc/machine-id` may be rewritten. **Neither was used, and `/etc/machine-id` on this host was neither read nor written** | Operations Owner — **A-5.0-5, unconfirmed** |
| The Band 2 host and authentication matrix | needs real OS identities and a `pg_hba` reload | Operations Owner — **A-5.0-4, unconfirmed** |
| The supervised host reboot (`JNL-02b`) | needs an authorized reboot | Operations Owner |
| The bot, web and Foundry test suites | **not run.** No production or test code changed in this remediation, so a suite result would evidence nothing about it, and a figure from an earlier tree would be an assertion about a state that no longer exists | Technical Lead |
| Formatter, linter, type checker, `compileall` | **not run**, for the same reason: no Python file was touched | Technical Lead |
| The Google-access margin (WP-13) | disposable spreadsheet and service account unavailable | Delivery Lead — **A-5.0-3, unconfirmed** |
| Security review | **the Security Reviewer is unnamed** | Delivery Lead — **D-5.0-1** |

---

## 9. Search results for the stale forms

Run over `docs/review/phase-5-0-package-plan.md`,
`docs/review/phase-5-0-logical-schema.md`, `docs/implementation-plan.md`,
`docs/project-management/` and `docs/discovery/open-decisions.md`. **Counts
exclude this handback**, which quotes several of the forms by design.

**Every surviving hit is one of four kinds:** a **definition**, a **corrected
use**, a **labelled retained-history row** (a *"What changed in revision N —
retained"* table or a superseded status block), or a **marked quotation** of the
withdrawn wording inside the correction that withdraws it. **One live stale claim
was found and is fixed**; it is named below rather than absorbed.

| Form | Surviving hits | Disposition |
|---|---|---|
| `produced < validated` | package plan **9**; status **1**; RAID **1**; change log **2**; open decisions **2** | **marked quotations and withdrawal statements only.** In the package plan: the revision-9 status block, the R8-A change row, §2.13.1 row 18, §2.13.5a's withdrawal paragraph, invariant **I-2**'s row, stop condition **10j**, §9.4 and §10 — each naming it as the **withdrawn** universal claim; plus the retained revision-8 change row and the superseded revision-8 status block. **No live claim of this shape survives**; the live statement is invariants **I-1 … I-5** |
| `was supplied` (of the deployment digest) | package plan **1** live | **corrected use.** Algorithm C **C0** now says the digest *"was supplied, well-formed, and equal to `DD`, which C0 computes"*. The other two hits are the unrelated §3.7.1/§2.13.8a phrase *"a value the coordinator supplied"* about the withdrawn Boolean column |
| `cleans it as an explicit first step` | package plan **1**; change log **1** | **marked quotations only** — §2.13.2a's step 2, which names it as the withdrawn revision-8 behaviour, and the C-P5.0-Q change-log entry. **No live self-cleaning path survives** |
| `leaves the tree untouched` / `leaves the tree exactly as it was` | package plan **2** | **one was a live stale claim and is fixed.** Algorithm C step **C5** said *"every refusal above it leaves the tree untouched"*; it now says *"creates no generation and no database artifact — invariant I-4"* with the transient-directory qualification pointing at §2.13.2b. The remaining hit is §2.13.5a's failure-cost paragraph **quoting** the withdrawn revision-8 sentence inside its correction |
| `eight-capability` | package plan **7**; logical schema **2**; implementation plan **1**; status **2**; RAID **4**; decision register **1**; change log **2**; open decisions **3** | **withdrawal statements and labelled retained history.** Every current hit either states that the eight-capability register is **withdrawn** and names its replacement, or sits in a retained revision-8 change table or superseded status block. **No live register of eight capabilities survives** |
| `K1` … `K8` | package plan **14**, logical schema **4** — **no live use in either** | **relabelled to `A1 … A9` in every live statement.** Package plan: four hits are in the retained revision-8 change table and the superseded revision-8 status block; two are §2.13.1 rows 16 and 21, which quote the old labels inside their concessions; eight are §2.13.5c's own correction paragraph, its *achieved ability versus the privileges that achieve it* table and the F-2/F-4/F-5 rows, each quoting the label it is replacing. Logical schema: two are the R7-C and R8-C change rows, one is §3.7's *What this table uniquely can do* paragraph quoting the withdrawn pairing, and one is §3.7.1. **Seven live uses were rewritten to the A-labels** — §2.13.5b's two verifier rows, §2.13.11's option J-2, WP-6, §6.5 item 17, §7.1 row 24 and §9.2's revision-8 question in the package plan, plus §3.7, §3.7.1 and §9 in the logical schema — and **three of them carry a parenthetical naming the old label** (`§6.5 item 17`, `§7.1 row 24`, and logical schema §3.7.1) so a reader tracking the earlier revision can follow |
| `restored onto another host is refused` | package plan **1**; logical schema **2** | **corrected uses.** The package plan's `host_machine_id` field row and the logical schema's column rule both now carry *"unless `/etc/machine-id` there is rewritten to this value, which nothing in this design detects — F-7, residual R-5.0-13"*. The logical schema's second hit is the R8-D change row |
| `twelve falsification` | package plan **1**; logical schema **1** | **labelled retained-history rows only**, both recording the revision-7 → revision-8 count correction |
| `seventy-four cases` / `forty-eight cases` | package plan **2** / **2**; logical schema **2** / **2**; RAID **2** / **2**; change log **1** / **1**; open decisions **1** / **2** | **before-and-after columns in change tables, and labelled retained history.** Every live count is **eighty-four** |
| `remediation R6 brief` / `remediation R7 brief` | **none anywhere** | — |

**`git diff --check`: run, exit 0, no output.** `git diff --no-index --check
/dev/null <file>` reported **no whitespace error** for the package plan, the
logical schema or the R7 handback, verified against a control file that does
report one. **The Markdown table-integrity check reported no column-count
mismatch in either design artifact.**

**One defect found and fixed while remediating, reported rather than absorbed** —
Algorithm C step **C5**'s *"leaves the tree untouched"*, above. It is a live
instance of the R8-B class that the brief did not name, and it is corrected in
the same terms as the rest.

---

## 10. What P5.0-R1, P5.0-R2 and P5.0-R4 look like after this remediation

| Finding | State | What revision 9 did to it |
|---|---|---|
| **P5.0-R1** | **Open.** Its database half is met by the authority-fence trigger; its Sheet half is not | **Nothing.** §2.10's barrier search is unchanged, its conclusion is unchanged, and **R-5.0-8 is narrowed by no case at all**. §2.13.10 is unchanged: the journal is an enumeration control and **is not** a Google accepted-request completion barrier. It is not offered as one anywhere, and stop condition 10b forbids describing it as one |
| **P5.0-R2** | **Closed, and preserved** | **Nothing.** §2.1's matrix, §2.5's effective-time model and §11's telemetry contract are untouched, and the regression guard remains |
| **P5.0-R4** | **Open** | **Nothing.** §2.12's host boundary, §4.3's grant and authentication matrices and the revision-4 denial evidence plan are unchanged, and **no operational evidence is claimed passed**. The additions are to the Security Reviewer's depth and to R-5.0-9's drift surface, both of which widen the finding's cost rather than closing it |
| **P5.0-R5** | **Blocking** | All four Blocking inconsistencies are corrected. **No closure is claimed** |
| **OD-55**, **OD-58** | **Closed, and preserved** | No telemetry table and no ledger table exists in this package |

---

## 11. Confirmation that no finding is claimed closed and no unauthorized action occurred

**No finding is claimed closed.** P5.0-R1, P5.0-R4 and P5.0-R5 are the
Independent Reviewer's to close. P5.0-R5 remains **Blocking**. D5.0-9 through
D5.0-13 / OD-62 through OD-66 remain **open** and are not ruled from revision 8 or
revision 9. The Security Reviewer remains **unnamed**. Package 5.0 remains
`not ready` and implementation remains **unauthorized**.

**No implementation or environment mutation occurred.** No production code, no
migration `0014`, no table, no database role, no database object, no grant, no
operating-system account, no group, no `pg_hba.conf`, `pg_ident.conf` or
`sudoers` entry, no credential, no Google access change, no configuration or
environment change, no directory, no file outside `docs/`, no file mode, no
filesystem attribute, no deployment, no service start, stop or restart, no
`systemd-run`, no `chattr`, no `setpriv`, no `sudo`, no data mutation, no Sheet
access, no authority cutover and no Package 5.1+ work.

- `/var/lib/freedom-sheet-writer` **does not exist on this host and was not
  created**. Neither did `…/journal`, `…/archive`, `…/probe`, `…/probe-ro`, any
  seal, any journal, any archive or any generation.
- **No probe was executed**, no arena and no Stage-4 target directory were
  created, and no transient unit was started. `S4-0` remains a specification.
- **No capability set was constructed.** No `setpriv`, no `--ambient-caps`, no
  ambient `CAP_LINUX_IMMUTABLE`, and no combination from §2.13.5c was executed.
  Every authority statement in the register is a design claim awaiting the
  evidence `JNL-49`/`JNL-50` would produce.
- **No host identity was read or written.** `/etc/machine-id` was neither read
  nor modified, and no second host was used.
- **The host was neither read nor written for this remediation.** No
  `/proc/mounts`, `df`, `statvfs`, `systemctl`, `stat`, `lsattr` or `chattr`
  observation was taken; every host fact in the documents is the one recorded on
  2026-08-29 at package plan §8.1, carried forward as previously recorded
  evidence and labelled as such.
- **No test suite, formatter, linter or type checker was run**, because no code
  changed. §8 lists each as a check not run rather than implying a pass.
- **Unrelated worktree changes were preserved.** `git status` before and after
  shows the same pre-existing modified and untracked files outside `docs/`, and
  none was edited, staged, reverted or committed by this remediation.

The only changes are to documents: `docs/review/phase-5-0-package-plan.md`,
`docs/review/phase-5-0-logical-schema.md`, this file,
`docs/review/phase-5-0-remediation-r7-handback.md` (superseded-disposition note
only), `docs/implementation-plan.md` §20, and the status, RAID, decision-register,
open-decisions and change-log entries, which **record impacts and approve
nothing**.

---

## 12. What is requested next

**An independent re-review of revision 9**, on
`docs/review/phase-5-0-package-plan.md`,
`docs/review/phase-5-0-logical-schema.md` and this handback.

**This submission claims no finding closed.** It asks the Independent Reviewer to
decide whether the R8 findings are answered, and it does not ask for readiness,
for a gate, or for implementation authority.

**The most useful disagreements would be:**

1. an authority in §2.13.5c's register that is still wrongly bounded, a **tenth**
   the register omits — `CAP_DAC_OVERRIDE`, `CAP_DAC_READ_SEARCH`, `CAP_FOWNER`,
   `CAP_CHOWN`, `CAP_SYS_ADMIN`, a mount namespace, a `setgid` into
   `freedomjournal` or `freedomcoord` — or an F-row whose stated minimum
   **combination** still cannot construct its alteration, in either direction;
2. a case in `JNL-49`/`JNL-50` that would in practice have to be executed as root
   rather than under the capability set it names, which would make it prove
   something weaker than it claims;
3. a state a real cleanup failure can reach that §2.13.2b does not list, or a
   claim elsewhere in either document that is still written unconditionally when
   §2.13.2b makes it conditional;
4. a value in §2.13.5a whose **class** under I-2 / I-3 / I-5 is wrong, or an
   external input the table treats as internal — in particular anything reaching
   Algorithm C from outside it that **C0** does not validate against an
   independent source;
5. a way the deployment manifest of §2.13.2c can change without changing `DD` —
   a drop-in path not covered, a symlink, a `systemd` unit source directory the
   manifest does not name — which would make **F-6** and **J-22** weaker than
   stated;
6. a residual that is understated: **R-5.0-13** in particular, where the claim is
   that *nothing in this design detects it* and that the operational evidence in
   §5 is what actually remains; or a judgement that **option A-2** should be
   adopted rather than accepted, which is the Acceptance Authority's; and
7. a fifth instance of the recurring class: a correction in **this** revision that
   reproduces, one level down, the defect it corrects — or, worse, another claim
   that credits a mechanism with something it does not do, which is what R8-C and
   R8-D were.

**Package 5.0 remains `not ready`, and implementation remains unauthorized**
until all Blocking findings are closed, the Security Reviewer is named and
completes review, Peter records D5.0-9 through D5.0-13, and the package
definition of ready is satisfied.
