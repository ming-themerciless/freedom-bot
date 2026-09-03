# Package 5.0 — design remediation R7 handback

> **Superseded.** Codex independently re-reviewed this revision-8 response on
> 2026-08-30 and requested changes. Four Blocking inconsistencies were found
> (R8-A through R8-D); P5.0-R5 remains Blocking. The active instructions are in
> `docs/review/Handover information` (remediation R8), and the response to them
> is **revision 9** with
> `docs/review/phase-5-0-remediation-r8-handback.md`, which is now the current
> handback. This file is retained as review history, is not the active record of
> the design, and claims no finding closed. Where it describes Algorithm C's
> value ordering, the cleanup contract, the eight-capability register or F-7's
> outcome, **revision 9 has superseded it** — see §2.13.2b, §2.13.2c, §2.13.5a
> and §2.13.5c of the package plan.

Date: 2026-08-30 · Package 5.0 — Migration and cutover harness

Prepared by: Claude — implementer and working Technical Lead (designated, OD-61)

Returned to: Peter Duscha (Acceptance Authority, Product Owner, Data Owner,
Operations Owner, Delivery Lead) and Codex (Independent Reviewer and independent
logical-schema reviewer, OD-61).

In response to: `docs/review/Handover information`, *Package 5.0 remediation R7 —
documentation and design instructions*, which **authorizes documentation and
design remediation only**. No production code, migration `0014`, database or
operating-system change, privileged probe, service change, Google access,
deployment, cutover, Package 5.1+ work or any environment mutation is authorized,
and none occurred.

> **Claude claims no finding closed.** P5.0-R1, P5.0-R4 and P5.0-R5 are closed by
> the Independent Reviewer, not here. **P5.0-R5 remains Blocking.**
>
> **The four R7 findings are conceded before any replacement is presented.** Each
> concession is written into the documents themselves — package plan
> **§2.13.1 rows 14–17** — *before* the corrections are stated, so a reader meets
> the defect first.
>
> - **R7-A.** Algorithm C step **C0** refused unless `verify-capability` had
>   *"passed in this invocation, all four stages"*, with a report whose
>   `writer_deployment_digest` matched — and step **C1** was the step that ran
>   those stages and built that report. **An ordered algorithm cannot validate an
>   output before producing it.** Revision 7's Algorithm C therefore had **no
>   executable order at all**.
> - **R7-B.** Stage 4 case **S4-2** appended to an unnamed path *"outside
>   `ReadWritePaths=`"* and accepted `EROFS` as evidence of `ProtectSystem=strict`
>   **without first proving that path and file writable by `freedomsheet` without
>   the sandbox**. Every directory in §2.13.3 except the arena denies that
>   identity, so the refusal was attributable to ordinary permissions — **the same
>   defect Stage 1 exists to prevent, left in the one stage that runs under
>   systemd**.
> - **R7-C.** Class 1 was defined as unable to clear `FS_APPEND_FL` and then said
>   to reach *"every row below except F-1b"*. That class cannot rewrite record 0,
>   replace the journal inode in a root-owned directory, alter a `chattr +i`
>   archive, write the root-owned deployment path, rewrite `/etc/machine-id` or
>   touch PostgreSQL. **F-2 was assigned class 1 while its own note conceded that
>   rewriting record 0 requires class 2.**
> - **R7-D.** Implementation-plan §20 identified revision 5 / R5 as the active
>   handoff. The reviewer corrected it to revision 7 / R7.
>
> **The preserved states are preserved.** P5.0-R1 and P5.0-R4 remain open;
> **P5.0-R2 remains closed**; P5.0-R5 remains **Blocking**; D5.0-9 through
> D5.0-13 / OD-62 through OD-66 remain **open**; the Security Reviewer remains
> **unnamed**; implementation remains **unauthorized**. The journal remains an
> **enumeration control, not a Google accepted-request completion barrier**, and
> **narrows R-5.0-8 by no case at all**.

---

## 1. Finding-by-finding change table

| Finding | Classification | Conceded at | Replaced by | What a reviewer should check |
|---|---|---|---|---|
| **R7-A** — make Algorithm C executable in its stated order | Blocking — integrity and production reliability | package plan **§2.13.1 row 14**, and again in §2.13.5a's *Why the order changed* | **§2.13.5a** — steps **C0 … C13**, the new **C2**, the *value-dependency table*, the *what a refusal costs at each step* paragraph and the revised dependency graph; **§2.13.2a** (`init-generation` compares the digest at C2, cleanup reaches disk at C9); **§2.13.7** (`verify-capability`, `init-generation` and `rotate` preconditions); **§2.13.8** `JNL-46`, `JNL-47`; **§3** WP-15; **§9.3** stop condition **10j**; logical schema **§3.7**, **§4.3.8** Band 3, **§9** | that **C0 reads no probe result**; that **C1 is the only invocation of the probe stages and the only creation point of `PR`**; that every result-dependent check sits at **C2**, after C1 and before **C5**, the first persistent artifact; that *produced < validated ≤ consumed* holds in every row of the dependency table; and that every C-reference in both documents was renumbered rather than left at the old number |
| **R7-B** — give S4-2 an exact positive DAC control | Blocking — integrity and production reliability | package plan **§2.13.1 row 15**, and again in §2.13.2a's *Revision 7's remaining defect* | **§2.13.2a** — the `…/probe-ro` lifecycle table, case **`S4-0`**, the revised `S4-1 … S4-3` rows, *Why S4-0 has to run outside the unit*, *The order inside Stage 4*, and three new attribution-table rows; **§2.13.3** (a `…/probe-ro` row, and the unit note); **§2.13.4** (the arena row covers both directories); **§2.13.5a** **C0**/**C1**; **§2.13.7**; **§2.13.8** `JNL-29`, `JNL-48`; **§9.2** surface 11 and a new question; **§9.3** stop conditions **10f**, **10i**; logical schema **§3.7**, **§3.7.1**, **§4.3.8** Band 3, **§9** | that the target is **named**, that its ownership, mode and mount are **identical to the arena's**, that it is **inside** `ProtectSystem=strict`'s tree and **outside** the substituted `ReadWritePaths=`, and that a path cannot be both — which is why it is a sibling directory; that **S4-0 runs outside any unit**, on the exact file, under the writer's uid; that `EACCES` is `inconclusive` and a sandboxed success is `failed`; and that cleanup, the residue report and the `C0` refusal all cover both directories |
| **R7-C** — replace the attacker-class matrix with capability-correct cases | Blocking — integrity and production reliability | package plan **§2.13.1 row 16**, and again at the head of **§2.13.5c** | **§2.13.5c**, rewritten: the eight-capability register, the identity-boundary paragraph, the thirteen-row falsification matrix with five columns per row, the not-constructible table, and four bounded claims replacing three global ones; **§2.13.5b** (the verifier table now names `K1`/`K3`); **§2.13.11** option J-2; **§3** WP-6, WP-8; **§6.5** items 16 and 18; **§7.1** row 24; **§7.4** **R-5.0-12**; **§9.2** a new question; **§9.3** stop condition **10k**; **§2.13.8** `JNL-49`, `JNL-50`; logical schema **§3.7** (*What this table uniquely can do*), **§3.7.1**, **§9** | that no capability in the register implies another except where the table says so; that each F-row's **minimum capability can actually construct** its alteration; that **F-2 is `K3`** and **F-7 is corrected in the opposite direction**; that no *"reaches every row"* claim survives as a live claim; that impossible pairings carry the control that makes them so; and that the combined-authority case is stated as a **residual**, not a refusal |
| **R7-D** — keep the controlled active-handoff reference current | Important — governance and review evidence | — | **implementation-plan §20**, whose correction to revision 7 / R7 is preserved and extended to name revision 8; **status**, **RAID**, **decision register**, **open decisions** and the **change log**, which all name **R7** as the active cycle and revision 8 as the response; and `phase-5-0-remediation-r6-handback.md`, marked **superseded** | that §20 still names the R7 brief as active, now with revision 8 recorded as the response and the next-revision rule stated; and that the five registers agree on the cycle name |
| Correction found while remediating | — | — | **§2.13.5c**, WP-8, **§6.5** item 16, logical schema **§9** | revision 7 described §2.13.5c as *"twelve falsification rows"* while listing **thirteen** (F-1a, F-1b, F-2 … F-12). The count is corrected. **This was not an R7 finding**; it is reported because the handoff requires every count to be recalculated |

**No finding is claimed closed by this table.** It records what changed and where,
so the re-review can check the change rather than the claim.

---

## 2. The complete chronological creation algorithm, and its value-dependency table

The authoritative statement is package plan **§2.13.5a**. It is reproduced here in
outline because the handoff requires the handback to contain it.

| Step | Actor | What it does | First persistent artifact? |
|---|---|---|---|
| **C0** | root | **Pre-probe preconditions only.** Writer unit inactive; its unit file deployed; `…/journal` and `…/archive` present with the §2.13.3 owners and modes; **`…/probe` and `…/probe-ro` absent**; predecessor sealed, archived and its `.close` manifest verifying; a `writer_deployment_digest` supplied. **No probe result is read here** | no |
| **C1** | root | Run §2.13.2a stages **1–4** in one `verify-capability` invocation, clean up both transient directories, and build the probe report `PR`. **The only probe invocation and the only creation point of `PR` in the whole algorithm** | no |
| **C2** | root | **New.** Validate the result-dependent facts: all four stages present with every case; every observed result equal to its expected result, so the overall result is `passed`; `PR.writer_deployment_digest` equal to the digest supplied at C0; and cleanup complete, so neither transient directory exists. Then compute `probe_report_digest` **once** | no |
| **C3** | root | Build the seal body `SB`, excluding `genesis_record_digest`, `journal_device`, `journal_inode` and `seal_digest`; compute `seal_body_digest` | no |
| **C4** | root | **Derive** the genesis record `G` from `SB` alone; `genesis_record_digest` = `G.record_hash` | no |
| **C5** | root | Create the journal `O_CREAT\|O_EXCL`, write `G`, `fsync` file then directory | **yes — the first** |
| **C6** | root | `chattr +a`, re-read, refuse if absent | — |
| **C7** | root | `fstat` → `journal_device`, `journal_inode`; refuse unless the device equals `PR.probe_device` | — |
| **C8** | root | Build the three-field binding `BND` at the `binding_format_version` `SB` declares | — |
| **C9** | root | Write `SB ‖ BND` to `.tmp`, `fsync`, `rename`, `fsync` directory. **The only step that writes `PR` to disk** | — |
| **C10** | root | `chattr +i` on the seal, re-read, refuse if absent | — |
| **C11** | root | Atomically replace the `current` symlink | — |
| **C12** | root | Compute `seal_digest` over the finished file and print the registration values. **Nothing on disk contains it** | — |
| **C13** | coordinator, not root | `register-journal-generation` — Algorithm V-R, then one transaction: row, receipt, audit event | PostgreSQL |

**The value-dependency table.** *Produced < validated ≤ consumed* in every row.

| Value | Produced at | Validated at | First consumed at |
|---|---|---|---|
| supplied `writer_deployment_digest` | before C0 | **C0** presence; **C2** equality with `PR` | C1, then C3 |
| the deployed unit and its directives | before C0 | **C0** deployed; **C1** S4-3 hashes the applied set | C1 |
| absence of `…/probe`, `…/probe-ro` | — | **C0** | C1 |
| predecessor sealed/archived/`.close` verified | predecessor's `seal` | **C0** | C3 |
| `PR` and every case result | **C1** | **C2** | C2, C3 |
| `probe_report_digest` | **C2** | pure function of validated `PR` | C3 |
| `SB`, `seal_body_digest` | **C3** | — | C4 |
| `G`, `genesis_record_digest` | **C4** | re-derived at **V-W W5** every start | C5, C8 |
| the journal file | **C5** | **C6** (`+a`), **C7** (`st_dev`) | C7 |
| `journal_device`, `journal_inode` | **C7** | — | C8 |
| `BND` | **C8** | — | C9 |
| the seal file | **C9** | **C10** (`+i`) | C12 |
| `seal_digest` | **C12** | — | C13 (a leaf) |

**Failure behaviour, which is the other half of what R7-A asks for.** A refusal at
**C0**, **C1** or **C2** leaves the tree exactly as it was — no journal file, no
seal, no `current` symlink, no `.close` manifest, no registration row and no
transient-directory residue. **`JNL-47`** asserts this for a failure injected in
each of Stage 1, Stage 2, Stage 3, Stage 4 and cleanup — five cases. A refusal at
**C5 … C11** leaves an unregistered partial generation; `init-generation` names
the artifacts, exits non-zero, and `repair` rather than a re-run is the documented
recovery, because `O_EXCL` at C5 refuses to overwrite. A refusal at **C13** leaves
a complete unregistered generation, which row **J-16** already refuses.
**`JNL-46`** walks C0 … C13 and asserts, per value, that it exists, is final and
has passed its validation before use.

**What did *not* change.** Algorithm **V-W** still has eighteen steps; **V-C** and
**V-R** are unchanged; the refusal codes stay `SW-J01 … SW-J25`; the fail-closed
table stays at twenty-five rows; the registration step is unmoved in everything
but its number (C12 → **C13**).

---

## 3. The exact S4-2 target, its positive control, and the negative test's lifecycle

The authoritative statement is package plan **§2.13.2a**, *Stage 4*.

**The target.** `…/probe-ro/s4-2.target`, with an identically created sibling
`…/probe-ro/s4-0.unlink`, both `freedomsheet:freedomsheet 0600`, neither carrying
`+a` or `+i`, inside a transient directory `…/probe-ro` owned `root:freedomsheet`
mode `0770` — **identical to the arena in ownership, mode and mount**, and created
by `verify-capability` at the same point in the same command.

**Why that path and not another.**

| Requirement from the handoff | How the design meets it |
|---|---|
| created without touching live evidence | it is created by `verify-capability`, holds only probe bytes, and lives nowhere near `…/journal` or `…/archive`; `verify-capability` refuses while the writer unit is active, and `init-generation` refuses at **C0** while either transient directory exists |
| inside the tree protected by `ProtectSystem=strict` | it is under `/var/lib/freedom-sheet-writer`, on the same ext4 device Stage 3 recorded as `probe_device`; `ProtectSystem=strict` mounts the whole hierarchy read-only except `/dev`, `/proc`, `/sys` and the paths in `ReadWritePaths=` |
| outside the substituted `ReadWritePaths=` | the substitution names **`…/probe` and nothing else**, and it is recorded verbatim in the report as part of **S4-3**. `…/probe-ro` is a **sibling** rather than a subdirectory precisely because the arena must be inside the substitution for **S4-1** and the target outside it for **S4-2**, and one path cannot be both |
| privileged cleanup on every exit path | the same `finally` that clears the arena clears `…/probe-ro`: attributes cleared as root, each file unlinked, both directories `rmdir`ed; a failure **exits non-zero naming the residue by path**; a residue found on a later run is reported and cleaned as an explicit first step and never silently reused; and `init-generation` refuses at **C0** while either exists |

**The lifecycle, in execution order.** root creates `…/probe-ro` and its two files
→ **S4-0** runs, as `freedomsheet` through `setpriv`, **outside any unit** → the
transient `systemd-run` unit starts → **S4-1**, **S4-2**, **S4-3** run inside it →
the unit exits → the `finally` removes both directories. **S4-0 precedes S4-2 in
every execution**, and a report in which S4-2 passes while S4-0 is absent or
failing is refused at Algorithm C **C2** and again by the writer at **W4**.

**The cases.**

| Case | What it does | Accepted result |
|---|---|---|
| **S4-0** *(new)* | on the exact `s4-2.target`: `open(O_WRONLY\|O_APPEND)`, `write`, `fsync`, `close`; `rename` to `s4-2.target.moved` **within `…/probe-ro`** and back; and `unlink` on the identically created sibling `s4-0.unlink` | **every operation succeeds.** Any failure ⇒ Stage 4 is **`inconclusive`**, never `passed`, and `verify-capability` exits non-zero naming the operation and its `errno` |
| **S4-1** | append inside the substituted `ReadWritePaths=` | succeeds |
| **S4-2** | the same append **to the exact file S4-0 just proved writable** | **`EROFS` and nothing else.** `EACCES` ⇒ **`inconclusive`**. Success ⇒ **failed** stage |
| **S4-3** | `systemctl show` compared with the deployed unit file, applied directive set hashed | equal but for the one recorded substitution; a mismatch ⇒ **`inconclusive`** |

**Why the unlink leg is proved on a sibling, stated rather than glossed.** Unlink
permission is a **directory** permission plus the victim's own flags. Proving it on
the target itself would destroy the file the negative case needs. The sibling is
created in the same directory with the same ownership and mode, so the directory
permission it demonstrates is the one that governs the target; the target's own
unlink is then exercised at cleanup, where success or failure is recorded and a
failure is a non-zero exit. This is stated as *"as applicable"* in the handoff's
own terms rather than claimed as an unlink of the target.

**The four outcomes the handoff requires the test to produce and distinguish** are
**`JNL-48`**, four cases: *(a)* positive DAC success outside the sandbox on the
exact target; *(b)* a deliberately mis-provisioned target (`root:root 0600`)
producing **`EACCES`** under the sandbox, classified DAC and recorded
**`inconclusive`**; *(c)* **`EROFS`** under the sandbox on a correctly provisioned
target with S4-0 passing, classified as the systemd read-only bind and recorded a
**pass**; *(d)* a planted cleanup failure producing a **non-zero exit naming the
residue**, with `init-generation` then refusing at **C0**.

**Everything the change touches.** Stage 4's case identifiers become
**`S4-0 … S4-3`**; the canonical probe bytes at **C1** carry them plus the target
path and its `st_dev`; §2.13.3 gains a `…/probe-ro` row; §2.13.4's arena row covers
both directories; the deployed unit's `ReadWritePaths=` is stated to exclude both;
the evidence band gains `JNL-48` and `JNL-29` gains the S4-0 assertions; the
attribution table gains three rows; §9.2 gains a surface element and a question;
stop conditions **10f** and **10i** follow; and logical schema §3.7, §3.7.1, §4.3.8
and §9 carry the new case list.

---

## 4. The capability-by-artifact threat matrix, and the corrected F-row assignments

The authoritative statement is package plan **§2.13.5c**, rewritten in full. The
two-class model is **withdrawn**, and with it every *"reaches every row except"*
claim.

**The capability register.**

| # | Capability | Who can hold it here |
|---|---|---|
| **K1** | seal-file write or replacement | root only — `0440 root:freedomjournal`, `chattr +i`, in a directory with no group write |
| **K2** | journal-directory write | root only — `…/journal` is `0750 root:freedomjournal` |
| **K3** | journal-content rewrite | a holder of `CAP_LINUX_IMMUTABLE`. **Not the writer**: empty `CapabilityBoundingSet=`, `NoNewPrivileges=true` |
| **K4** | archive write / attribute control | root with `CAP_LINUX_IMMUTABLE` |
| **K5** | deployment-path write | root; and, for the *repository* copy only, `discordbot`/`freedomweb` via H-1 |
| **K6** | host identity or restoration control | root on whichever host the tree is read on |
| **K7** | coordinator execution and peer authentication | `foundry` via the `sudoers` rule, and root by `setuid` |
| **K8** | PostgreSQL row mutation or insertion | **insertion:** K7. **mutation:** nobody in this design — it needs a PostgreSQL superuser |

**The identity boundary the handoff asks to be stated accurately.**
`CAP_LINUX_IMMUTABLE` **alone** is K3 and K4 and nothing else. **Full root** holds
K1 … K7 *and* can cross operating-system identities into `freedomcoord`, so it
reaches K8's **insertion** half. **A PostgreSQL superuser** is a third authority
and the only holder of K8's **mutation** half. These are not a ladder of one
attacker growing stronger.

**Per row, the five things R7-C requires.** §2.13.5c's matrix gives, for each of
the **thirteen** rows, the minimum capability, whether that capability also
reaches the detector, the independent actor or artifact that refuses it, the exact
step and code, and the residual when the attacker holds both. The corrections:

| Row | Revision 7 | Revision 8 | Why |
|---|---|---|---|
| **F-2** | class 1 | **`K3`** | rewriting record 0 in place requires clearing `FS_APPEND_FL`; appending cannot change it; and a replacement file in `…/journal` requires `K2`. Every route needs root. *Revision 7's own note said so while the class column said otherwise* |
| **F-7** | class 1 **and** 2, with *"class 2 cannot forge another host's `machine-id` on this one"* | **`K6`, and the capability does reach the detector** | `/etc/machine-id` is an ordinary root-writable file. Root on the restoring host can set it to the recorded value and **W10 then passes**. The refusal is the **coordinator's**, against the registered row, which is not on the restored tree. **The correction is in the opposite direction from the rest** |
| **F-3** | *"either; refused with no host access at all"* | **`K8`**, with insertion and mutation separated | insertion needs K7; mutation needs a superuser, because `reject_history_mutation` and the revoked grants refuse `UPDATE`/`DELETE`/`TRUNCATE` for every principal including the schema owner |
| **F-4** | class 1 | **`K4`** | the archive is `0440 +i` under `0750 root:freedomcoord`; altering it needs root **and** `CAP_LINUX_IMMUTABLE` |
| **F-5** | class 1 | **`K2`** | `…/journal` is root-owned with no group write, so replacing the inode is a root act |
| **F-6** | class 1 | **`K5`** | the deployment path is root-owned. H-1 is noted as the qualification |
| **F-8** | class 1 | **`K1`**, with the detector reach stated as *partly* | `probe_report_digest` is inside `SB`, so K1 keeps the seal self-consistent; `seal_body_digest` then changes and record 0 does not, which needs `K3` |
| **F-1a**, **F-9 … F-12** | class 1 | **`K1`** | confirmed rather than changed: each detector is either the derived genesis record, `fstat`, or `binding_format_version` in the chain-authenticated body, none of which K1 controls |
| **F-1b** | class 2 | **`K1 + K3`** | unchanged in substance, restated in capabilities. **Still refused only by the coordinator, against PostgreSQL** — the negative assertion the handoff asks to keep |

**The pairings that are not constructible** are tabulated with the control that
makes each so — the writer against the seal, the journal directory, the journal's
content, the archive and PostgreSQL; the coordinator against the journal and
against row mutation; and `discordbot`/`freedomweb`/`foundry` against `…/journal`
itself. **`JNL-50`** executes all eight under their real identities; **`JNL-49`**
gives one case per feasible pairing not already covered by `JNL-34 … 45`, plus the
three combined-authority residuals.

**The residual that is now written down.** When an attacker holds **`K1 + K3` and
K8's mutation half** — host root *and* a PostgreSQL superuser — it writes both
copies the design compares, and **no check in this design refuses it**. That is
package plan §7.1 row **24** and RAID row **R-5.0-12**, owned by the Acceptance
Authority. What remains is external to both stores: `sudo log_output`, journald,
the `audit_events` chain, offline backups, and the fact that a forged head has no
`seal` record, no `.close` manifest and no archive. **`JNL-49` case 7 asserts the
limit rather than hiding it.**

**What is preserved.** The disk-to-PostgreSQL comparison stays one-directional;
nothing on disk depends on a database value; the writer still opens no database
connection; the writer still cannot modify, replace, rotate, seal, archive or
dispose of evidence; `/var/lib/freedom-sheet-writer` is unchanged; and `chattr +i`
is **not** offered as the answer to any row — it is the attribute `K3` clears by
definition, which is why the register is written in capabilities.

---

## 5. Schema, evidence, estimate, RAID and decision impacts

**Schema: none.** No column, constraint, index, trigger, sequence, vocabulary,
table, command or health check changes. `append_only_probe_version` still reads
`jnl-probe-1`; what that value *denotes* gains a fourth-stage control case, which
is a change to the procedure the closed vocabulary names and not to the
vocabulary — the movement a closed vocabulary exists to make visible. Logical
schema §3.7's `append_only_probe_digest` and `seal_digest` notes, §3.7.1's sandbox
and privileged-rewrite rows, §4.3.8 Band 3 and §9 change in wording, case lists
and counts only.

**Evidence.**

| | Revision 7 | Revision 8 |
|---|---|---|
| `TC-5.0-JNL` identifiers | forty-five | **fifty** |
| `TC-5.0-JNL` cases | forty-eight | **seventy-four** |
| New identifiers | — | `JNL-46` (1 case), `JNL-47` (5), `JNL-48` (4), `JNL-49` (8), `JNL-50` (8) |
| Extended | — | `JNL-29` gains the S4-0 assertions and the S4-0-before-S4-2 ordering |
| §6.5 items | seventeen | **eighteen** |
| Falsification rows | stated *twelve*, listed thirteen | **thirteen**, stated and listed |
| Fail-closed conditions | twenty-five | **twenty-five** — unchanged. **J-25** already covers a probe report that is absent, altered, unsupported or not a pass, which is what a failing S4-0 produces |
| Refusal codes | `SW-J01 … SW-J25` | **unchanged** |
| V-W steps | eighteen | **unchanged** |

**Estimate.** PERT **38.2 → 39.5** implementer-days, from `(19.3 + 4×38.4 +
63.9) / 6`. Decomposed: **WP-8 +0.87** (the band grows by five identifiers and
twenty-six cases, and the capability matrix has to be tested cell by cell),
**WP-15 +0.30** (`…/probe-ro`, the `setpriv` control, the extended cleanup, and
Algorithm C's validation step), **WP-9 +0.10** (the rehearsal runs S4-0 and the
`…/probe-ro` residue path). WP-1, WP-2, WP-3, WP-4, WP-4b, WP-6, WP-7 and WP-14
are **unchanged**. Remediation allowance **11.1 → 11.5** (30 % of ML). Contingency
**4.0**, unchanged: R-5.0-12 is an acceptance question, not implementation effort.
Independent review 2.5–3.0 and security review **2.5–3.5** reviewer-days,
unchanged, with **one added surface element** and **two added questions**.

**RAID.** New risk **R-5.0-12** (§7.4), owned by the Acceptance Authority with the
Security Reviewer. **R-5.0-9** extended to `…/probe-ro` residue and to both
transient directories' ownership and mode. **A-5.0-5** widened again — a second
transient directory on the same mount and the `S4-0` control executed under the
writer's uid outside any unit — and **remains unconfirmed**. **D-5.0-1** and
**D-5.0-2** extended. §7.1 gains row **24**. New stop conditions **10i**, **10j**,
**10k**; **10f** extended.

**Decisions.** **No new decision number.** None of the three Blocking corrections
introduces a governed choice: two change no host artifact at all, and the third
adds one transient directory to a probe **D5.0-13 / OD-66 option A** already
carries. Option A's content is re-stated in three places (§5.3, open decisions
OD-66) and **not adopted**. D5.0-9, D5.0-10, D5.0-11 and D5.0-12 are untouched;
the numeric register stays at nine; OD-55, OD-58 and P5.0-R2 are preserved.

---

## 6. Exact commands run, and their results

Every command was run in `/opt/freedom-blades/platform` on 2026-08-30. **All are
read-only or act on documentation files in the working tree.** No test suite was
run, and none is required for a documentation-only remediation; **no result from
an earlier tree is carried forward as current evidence.**

| # | Command | Result |
|---|---|---|
| 1 | `cat "docs/review/Handover information"` | the R7 instructions, read in full |
| 2 | `cat CLAUDE.md`, then `.agents/AGENTS.md` read in full | as `CLAUDE.md` requires |
| 3 | `wc -l` over the two design artifacts, the implementation plan, the R6 handback and the five registers | 3539, 1955, 2522, 498 and the register sizes; the revision-7 tree located |
| 4 | `grep -n '^#\{1,4\} ' docs/review/phase-5-0-package-plan.md` | the section inventory |
| 5 | `sed -n` reads of package-plan §§1.2, 2.13.1–2.13.11, 3, 4, 5.3, 6.5, 7.1, 7.4, 9.1–9.4, 10, and logical-schema §§0–4.3.8, 9, 10 | the revision-7 text under remediation |
| 6 | `sed -n '2485,2522p' docs/implementation-plan.md` | §20, confirming the reviewer's R7 correction is present |
| 7 | the thirteen stale-form searches the handoff names, over the package plan, the logical schema, the implementation plan, `docs/project-management/` and `docs/discovery/open-decisions.md` | recorded in §9 below |
| 8 | `git diff --check` | **exit 0, no output.** Re-run after the final edit |
| 8b | `git diff --no-index --check /dev/null <file>` for the package plan, the logical schema, this handback and the R6 handback | **no whitespace error reported for any of them.** The command exits 1 because the files differ from `/dev/null`; a control file containing one trailing space was checked the same way and produced `trailing whitespace` with **exit 3**, so the absence of output is a real result and not a silent failure. Stated because the design artifacts are **untracked** in this worktree, so `git diff --check` alone does not inspect them |
| 9 | `git status --porcelain` | only the intended documentation files, plus the pre-existing unrelated worktree changes, which were **preserved** |

---

## 7. Checks not run, their reasons and their accountable owners

Stated because the handoff requires it and because stop condition 10b forbids
describing an unproven property as proven.

| Check | Why not run | Owner |
|---|---|---|
| The `TC-5.0-JNL` band, all seventy-four cases | **the code does not exist and is not authorized.** Every case is a planned assertion, not a result | Technical Lead, after D5.0-13 and implementation authority |
| `verify-capability` and its four stages, including **S4-0** and the `…/probe-ro` lifecycle | **no probe was run; neither transient directory was created.** It needs root, `chattr`, `setpriv`, `systemd-run` and a durable hierarchy that does not exist on this host | Operations Owner — **A-5.0-5, unconfirmed** |
| The construction-order harness (`JNL-46`) and its failure injections (`JNL-47`) | the same: `init-generation` does not exist | Technical Lead |
| The capability matrix (`JNL-49`, `JNL-50`) | it needs real OS identities, real capabilities and a real database; **no pairing was executed and none is claimed to have been** | Operations Owner and Technical Lead — **A-5.0-4** and **A-5.0-5**, both unconfirmed |
| The Band 2 host and authentication matrix | needs real OS identities and a `pg_hba` reload | Operations Owner — **A-5.0-4, unconfirmed** |
| The supervised host reboot (`JNL-02b`) | needs an authorized reboot | Operations Owner |
| The bot, web and Foundry test suites | **not run.** No production or test code changed in this remediation, so a suite result would evidence nothing about it, and a figure from an earlier tree would be an assertion about a state that no longer exists | Technical Lead |
| Formatter, linter, type checker | **not run**, for the same reason: no Python file was touched | Technical Lead |
| The Google-access margin (WP-13) | disposable spreadsheet and service account unavailable | Delivery Lead — **A-5.0-3, unconfirmed** |
| Security review | **the Security Reviewer is unnamed** | Delivery Lead — **D-5.0-1** |

---

## 8. Confirmation that no implementation or environment mutation occurred

**No production code, no migration `0014`, no table, no database role, no database
object, no grant, no operating-system account, no group, no `pg_hba.conf`,
`pg_ident.conf` or `sudoers` entry, no credential, no Google access change, no
configuration or environment change, no directory, no file outside `docs/`, no
file mode, no filesystem attribute, no deployment, no service start, stop or
restart, no `systemd-run`, no `chattr`, no `setpriv`, no `sudo`, no data mutation,
no Sheet access, no authority cutover and no Package 5.1+ work.**

- `/var/lib/freedom-sheet-writer` **does not exist on this host and was not
  created**. Neither did `…/journal`, `…/archive`, `…/probe`, **`…/probe-ro`**,
  any seal, any journal, any archive or any generation.
- **No probe was executed**, no arena and no Stage-4 target directory were
  created, and no transient unit was started. `S4-0` is a specification, not a
  result.
- **The host was neither read nor written for this remediation.** No
  `/proc/mounts`, `df`, `statvfs`, `systemctl`, `stat`, `lsattr` or `chattr`
  observation was taken; every host fact in the documents is the one recorded on
  2026-08-29 at package plan §8.1, carried forward as previously recorded evidence
  and labelled as such.
- **No test suite, formatter, linter or type checker was run**, because no code
  changed. §7 lists this as a check not run rather than implying a pass.
- **Unrelated worktree changes were preserved.** `git status` before and after
  shows the same pre-existing modified and untracked files outside `docs/`, and
  none was edited, staged, reverted or committed by this remediation.

The only changes are to documents: `docs/review/phase-5-0-package-plan.md`,
`docs/review/phase-5-0-logical-schema.md`, this file,
`docs/review/phase-5-0-remediation-r6-handback.md` (superseded-disposition note
only), `docs/implementation-plan.md` §20, and the status, RAID, decision-register,
open-decisions and change-log entries, which **record impacts and approve
nothing**.

---

## 9. Search results for the stale forms

Run over `docs/review/phase-5-0-package-plan.md`,
`docs/review/phase-5-0-logical-schema.md`, `docs/implementation-plan.md`,
`docs/project-management/` and `docs/discovery/open-decisions.md`. **Counts
exclude this handback**, which quotes several of the forms by design.
`C0`, `C1` and `F-2` were matched on a word boundary with a negative lookahead for
a following digit, so `C10 … C13` and any `F-2x` are not counted as hits.

**Every surviving hit is one of four kinds:** a **definition** (the form is now a
defined identifier), a **corrected use** (the form is now true of the artifact), a
**labelled retained-history row**, or a **marked quotation** of the withdrawn
wording inside the correction that withdraws it. **No hit is a stale claim.**

| Form | Surviving hits | Disposition |
|---|---|---|
| `passed in this invocation` | package plan **3** | **marked quotations only** — the revision-8 status block, §2.13.1 row 14 and Algorithm C's **C0** note, each naming it as the withdrawn revision-7 requirement. **No live use survives anywhere** |
| `C0` | package plan **47**; logical schema **8**; status **5**; RAID **5**; change log **5**; open decisions **7** | **corrected uses and definitions.** `C0` now denotes the pre-probe precondition step and is defined at §2.13.5a; the register hits describe the renumbering. The retained-history forms `C0–C12` in the RAID and change-log records of R5 and R6 are **labelled retained-history rows** |
| `C1` | package plan **37**; logical schema **7**; status **8**; RAID **5**; change log **8**; open decisions **5** | **corrected uses.** `C1` is now the single probe invocation and the single creation point of `PR`, defined at §2.13.5a; every use points at that definition. The revision-6/7 change tables that mention C1's old duties are labelled retained history |
| `S4-2` | package plan **36**; logical schema **5**; status **2**; RAID **2**; change log **1**; open decisions **2** | **defined and corrected.** S4-2 is now the named negative case against `…/probe-ro/s4-2.target`, preceded by **S4-0**; every use carries the control. The `S4-1 … S4-3` form survives only in the **retained** revision-7 change rows and in the R6-A concession; the live case list is **`S4-0 … S4-3`** |
| `outside ReadWritePaths` | **none anywhere** | the unqualified form is gone. Every current statement names the exact path and says which substitution it is outside of |
| `EROFS` | package plan **24**; logical schema **6**; status **3**; RAID **4**; change log **2**; open decisions **4** | **corrected uses.** Every current statement pairs `EROFS` with the control that attributes it — S4-0 for the sandbox, M-1/M-2 for the mount — and the attribution table now distinguishes `EROFS` **with** a passing control, `EROFS` **without** one (`inconclusive`), and a sandboxed success (`failed`) |
| `Class 1` | package plan **1**; status **1** | **marked quotations only**, both introducing the withdrawal of the two-class model. **No live class claim survives** |
| `Class 2` | **none anywhere** | withdrawn with the model |
| `every row below` | package plan **2** | **marked quotations only** — §2.13.1 row 16 and the head of §2.13.5c, both quoting the false claim inside its withdrawal |
| `every row except` | package plan **4**; change log **1** | **marked quotations and withdrawal statements only** — the status block, the R7-C change row, §2.13.5c's withdrawal sentence and the change-log entry, each naming the form as withdrawn. **No live claim of this shape survives** |
| `F-2` | package plan **14**; logical schema **2**; status **4**; RAID **3**; change log **3**; open decisions **3** | **corrected uses, plus four hits in a different identifier space.** Of the twenty-nine, **twenty-five** are the falsification row or a statement about it, and in every one F-2's minimum capability is **`K3`**; the concession and register entries that quote the old class assignment are marked as such. **Four are unrelated and were not touched by this remediation**: status **1** and change log **2** are the **Phase 3 gate-evidence findings** `F-2`/`F-3` (*"no `freedom-web` systemd unit template exists"*), and open decisions **1** is the **Foundry topology** identifier `F-2a` under OD-13. Those are three separate `F-n` identifier spaces in this repository, and this is recorded rather than glossed, because the same collision was reported for `M-1`/`M-2` at R6 |
| `remediation R5 brief` | **none anywhere** | — |
| `remediation R6 brief` | **none anywhere** | — |

**`git diff --check`: run, exit 0, no output.** `git diff --no-index --check
/dev/null <file>` reported **no whitespace error** for the package plan, the
logical schema, this handback or the R6 handback, verified against a control file
that does report one.

**One defect found and fixed while remediating, reported rather than absorbed.**
`docs/review/phase-5-0-logical-schema.md` carried a **duplicated line** in the
revision-5 re-review paragraph (*"**Independent re-review of revision 5,
2026-08-29: P5.0-R5 remained"* appeared twice). It was a pre-existing corruption
of the same class as R6-D, it is removed, and it is named here rather than left
for a reviewer to find.

---

## 10. What P5.0-R1, P5.0-R2 and P5.0-R4 look like after this remediation

| Finding | State | What revision 8 did to it |
|---|---|---|
| **P5.0-R1** | **Open.** Its database half is met by the authority-fence trigger; its Sheet half is not | **Nothing.** §2.10's barrier search is unchanged, its conclusion is unchanged, and **R-5.0-8 is narrowed by no case at all**. §2.13.10 is unchanged: the journal is an enumeration control and **is not** a Google accepted-request completion barrier. It is not offered as one anywhere, and stop condition 10b forbids describing it as one |
| **P5.0-R2** | **Closed, and preserved** | **Nothing.** §2.1's matrix, §2.5's effective-time model and §11's telemetry contract are untouched, and the regression guard remains |
| **P5.0-R4** | **Open** | **Nothing.** §2.12's host boundary, §4.3's grant and authentication matrices and the revision-4 denial evidence plan are unchanged, and **no operational evidence is claimed passed**. The additions are to the Security Reviewer's scope and to R-5.0-9's drift surface, both of which widen the finding's cost rather than closing it |
| **P5.0-R5** | **Blocking** | The three Blocking defects are corrected and the governance defect is preserved-and-extended. **No closure is claimed** |
| **OD-55**, **OD-58** | **Closed, and preserved** | No telemetry table and no ledger table exists in this package |

---

## 11. What is requested next

**An independent re-review of revision 8**, on
`docs/review/phase-5-0-package-plan.md`,
`docs/review/phase-5-0-logical-schema.md` and this handback.

**This submission claims no finding closed.** It asks the Independent Reviewer to
decide whether the R7 findings are answered, and it does not ask for readiness,
for a gate, or for implementation authority.

**The most useful disagreements would be:**

1. a step in Algorithm C **C0 … C13** that still consumes a value a later step
   produces, or a row of the value-dependency table that mis-attributes where a
   value is produced, validated or first used;
2. a failure path between **C0** and **C5** that would in fact leave a persistent
   artifact, which `JNL-47` would then be asserting falsely;
3. a way `…/probe-ro` can be reached from inside the transient unit — through
   `StateDirectory=`, `BindPaths=`, `PrivateTmp=` or a drop-in — that **S4-3**'s
   directive-set comparison would not detect, which would make **S4-2** ambiguous
   again;
4. a capability in §2.13.5c's register that is wrongly bounded, a **ninth**
   capability the register omits, or an F-row whose stated minimum capability
   cannot in fact construct its alteration — in either direction;
5. a pairing marked **not constructible** that is constructible, or a control
   named for one that does not hold;
6. a residual that is understated — **R-5.0-12** in particular, where the claim is
   that nothing in this design refuses the combination and that only external
   records remain; or
7. a fourth instance of the R7 class: a correction in **this** revision that
   reproduces, one level down, the defect it corrects.

**Package 5.0 remains `not ready`, and implementation remains unauthorized**
until all Blocking findings are closed, the Security Reviewer is named and
completes review, Peter records D5.0-9 through D5.0-13, and the package
definition of ready is satisfied.
