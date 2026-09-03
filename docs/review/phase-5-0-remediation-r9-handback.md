# Package 5.0 — design remediation R9 handback

Date: 2026-08-30 · Package 5.0 — Migration and cutover harness

Prepared by: Claude — implementer and working Technical Lead (designated, OD-61)

Returned to: Peter Duscha (Acceptance Authority, Product Owner, Data Owner,
Operations Owner, Delivery Lead) and Codex (Independent Reviewer and independent
logical-schema reviewer, OD-61).

In response to: `docs/review/Handover information`, *Package 5.0 remediation R9 —
documentation and design instructions*, which **authorizes documentation and
design remediation only**. No production code, migration `0014`, database or
operating-system change, privileged probe, service change, Google access,
deployment, cutover, Package 5.1+ work or any environment mutation is authorized,
and none occurred.

> **Claude claims no finding closed.** P5.0-R1, P5.0-R4 and P5.0-R5 are closed by
> the Independent Reviewer, not here. **P5.0-R5 remains Blocking.**
>
> **The R9 findings are conceded before any replacement is presented.** Each
> concession is written into the documents themselves — package plan
> **§2.13.1 rows 22–24**, and again at the head of **§2.13.5c** — *before* the
> corrections are stated, so a reader meets the defect first.
>
> - **R9-A.** Revision 9's **A1** was *"flag control — `FS_IOC_SETFLAGS` setting
>   or clearing `FS_APPEND_FL` / `FS_IMMUTABLE_FL` on an inode the holder can
>   already reach and open under DAC"*, with minimum holder
>   `CAP_LINUX_IMMUTABLE`. **`FS_IOC_SETFLAGS` requires the caller's effective UID
>   to match the inode's owner, or `CAP_FOWNER`; changing `FS_IMMUTABLE_FL` or
>   `FS_APPEND_FL` requires `CAP_LINUX_IMMUTABLE` in addition.** They are two
>   independent kernel checks and revision 9 recorded one. `CAP_DAC_OVERRIDE` is
>   not a substitute for the owner check. So a non-root process holding only
>   `CAP_LINUX_IMMUTABLE` **cannot clear `+i` on the root-owned archive at all**,
>   and every combination written as `A1 + A3` or `A1 + A4` against a root-owned
>   seal, archive file or `.close` manifest was incomplete. `A1 + A2` for **F-2**
>   was constructible only because `freedomsheet` owns its journal file and so
>   satisfies the owner half by ownership — **a label that is right by accident is
>   not a model.**
> - **R9-B.** Revision 9 asserted that **A1 … A6 confer nothing on one another**
>   and then, under **F-1a**, that *"every real holder of A3 also holds A2"*.
>   **Both were live text in one subsection**, and the falsification matrix's
>   detector-reach column was computed from the first while the qualification came
>   from the second.
> - **R9-C.** `JNL-50` case 9 required a non-root `CAP_LINUX_IMMUTABLE`-only
>   identity to clear `+i` on an archived file *"successfully"* and then receive
>   `EACCES`. **The kernel returns `EPERM` from the ioctl and the case never
>   reaches the open**, so it could not have passed and the register's central
>   claim had no executable evidence behind it. And
>   `setpriv --ambient-caps=+linux_immutable` **does not build the set it names**:
>   an ambient capability must also be permitted and inheritable, and a `setuid`
>   away from 0 clears the permitted set unless `SECBIT_KEEP_CAPS` and
>   `SECBIT_NO_SETUID_FIXUP` are set first.
>
> **The materially addressed R8 corrections are preserved, as the brief
> requires.** §2.13.2c's deployment-digest lifecycle, §2.13.2b's three-state
> cleanup machine and R8-D's withdrawal of F-7's forged-host-identity detector are
> carried forward **unchanged in substance**. None is reopened, none is weakened,
> and **R-5.0-13** stands as a residual.
>
> **The preserved states are preserved.** P5.0-R1 and P5.0-R4 remain open;
> **P5.0-R2 remains closed**, and OD-55 and OD-58 remain preserved; P5.0-R5
> remains **Blocking**; D5.0-9 through D5.0-13 / OD-62 through OD-66 remain
> **open** and are not ruled from revision 9 or revision 10; **no option is
> adopted**; the Security Reviewer remains **unnamed**; implementation remains
> **unauthorized**. The journal remains an **enumeration control, not a Google
> accepted-request completion barrier**, and **narrows R-5.0-8 by no case at
> all**.

---

## 1. Instruction-by-instruction change table

| Instruction | Classification | Conceded at | Answered in | What a reviewer should check |
|---|---|---|---|---|
| **R9-A** — correct the inode-flag authority model | Blocking — integrity and production reliability | package plan **§2.13.1 row 22**, and again at the head of **§2.13.5c** | **§2.13.5c**, redesigned: the *kernel requirements* table; the eleven-authority register with **A1** narrowed and **A10**/**A11** added; the *why A10 and A11 are two rows* paragraph; the *achieved ability versus the privileges that achieve it* table with a revision-9 column; the thirteen-row falsification matrix with corrected minimum combinations and a *which rows changed* summary; the not-constructible table. Also **§2.13.4** (two rows added, thirteen → fifteen, plus the *refused twice over* paragraph); **§2.13.2a** case **P-8**; **§2.13.5b** (both verifier-table rows); **§2.13.7** (the root rationale, and the *clearing does not require an undocumented ambient capability* paragraph); **§2.13.8** `JNL-13`, `JNL-35`, `JNL-38`; **§4** (WP-8, WP-9, WP-15); **§5.3** D5.0-13; **§6.5** item 20; **§7.1** row 27; **§7.4** **R-5.0-12**, **A-5.0-5**, **D-5.0-1**, **D-5.0-2**; **§9.2** (two questions); **§9.3** stop conditions **10k**, **10m**; **§10** (two non-claims); logical schema **§3.7**, **§3.7.1**, **§4.3.8** Band 3, **§9** | that the kernel-requirements table is stated **before** the register that encodes it; that **A1 confers nothing on its own** and says so; that **A10 and A11 are separate rows with genuinely different holder sets** — `freedomsheet` holds A10 by ownership and holds A11 not at all; that **every root-owned-inode row now carries A11** and every `freedomsheet`-owned-inode flag change carries **A10**; and that **every correction adds a prerequisite**, so no refusal is strengthened and no risk narrowed |
| **R9-B** — remove the A3/A2 contradiction | Blocking — integrity and production reliability | package plan **§2.13.1 row 23**, and again at the head of **§2.13.5c** | **§2.13.5c**: the register's independence claim is scoped to the **primitives**; the new **holder table**; the *consequence for detector reach* paragraph; the falsification matrix's two reach columns — *by combination* and *by holder*; and **bounded claim 2**, rewritten. Also **§9.2** (a new question on the holder table) and **§9.3** stop condition **10k** as extended | that the model chosen is stated explicitly — **independent primitives, bundled holders** — rather than left implicit; that **F-1a's qualification is now the general case** rather than a footnote contradicting the register; and that **bounded claim 2 is materially narrower than revision 9's**, naming **F-2, F-3 and F-6** and no others |
| **R9-C** — rewrite the executable evidence contract | Blocking — integrity and production reliability | package plan **§2.13.1 row 24** | **§2.13.5c**'s executable-identity table (**E1 … E8**) and **§2.13.8**'s `JNL-49` and `JNL-50`, both at **twelve cases**. Also `JNL-13`, `JNL-35`, `JNL-38`; **§2.13.2a** **P-8**; **§4** WP-8/WP-9; **§6.5** item 20; **§7.4** **A-5.0-5**; **§9.2** (a new question on constructibility); **§9.3** stop condition **10m**; logical schema **§4.3.8** Band 3 and **§9** | that **every identity carries permitted, effective, inheritable, ambient *and* bounding sets**, not ambient shorthand; that `setpriv`'s **securebits** appear in every invocation that drops from uid 0 while keeping a capability; that **every case names its syscall, result and `errno`**; that **every negative flag case runs with all other prerequisites satisfied** and carries a **positive control that succeeds** differing by exactly the privilege under test; and that **no privileged case is claimed to have run** |
| Correction found while remediating | — | — | package plan **§2.13.2a** case **P-8** | The probe's own `FS_IOC_SETFLAGS` case said *"needs `CAP_LINUX_IMMUTABLE`, which the writer never holds"* — true, but ambiguous between the two checks. Because the arena file is created **owned by the writer's uid**, the owner half is satisfied and the capability is the whole of the refusal; the case now says so. **This was not an R9 finding**; it is the same incomplete model one level down, and leaving it would have made P-8 prove less than it does |

**No finding is claimed closed by this table.** It records what changed and where,
so the re-review can check the change rather than the claim.

---

## 2. The corrected authority model

The authoritative statement is package plan **§2.13.5c**. Reproduced here far
enough that the re-review can check it without turning back.

### 2.1 What was wrong, in one paragraph

`FS_IOC_SETFLAGS` makes **two** permission decisions, not one. The first is an
ownership decision — the caller's effective UID must equal the inode's owner, or
it must hold `CAP_FOWNER` — and it applies to **every** flag change. The second is
a special-bit decision: changing `FS_IMMUTABLE_FL` or `FS_APPEND_FL` additionally
requires `CAP_LINUX_IMMUTABLE`. Revision 9's **A1** carried the second and not the
first. Because the design's protected inodes are **root-owned** (the seal, every
archived file) while the live journal is **`freedomsheet`-owned**, the omission
mattered in opposite directions on the two halves of the hierarchy: it made
root-owned alterations look reachable by a capability that cannot reach them, and
it made the journal's alteration look constructible for a reason the register did
not state.

Primary contract:
<https://man7.org/linux/man-pages/man2/fs_ioc_setflags.2const.html>

### 2.2 The kernel requirements, now stated before the register

| Operation | Checks the kernel makes, all of which must pass |
|---|---|
| traverse to an inode | `x` on every directory on the path, or `CAP_DAC_READ_SEARCH` |
| open it (`O_RDONLY` suffices for the ioctl) | `r` under DAC, or `CAP_DAC_OVERRIDE` |
| `FS_IOC_SETFLAGS` at all | effective UID **equal to the inode's owner**, or `CAP_FOWNER` |
| `FS_IOC_SETFLAGS` changing `FS_IMMUTABLE_FL`/`FS_APPEND_FL` | **`CAP_LINUX_IMMUTABLE`**, in addition to the row above |
| write the inode's content | `w` under DAC, or `CAP_DAC_OVERRIDE` — **and** the flag must already be clear, because `inode_permission()` refuses `MAY_WRITE` on an immutable inode with `EPERM` *before* DAC |
| create, unlink, rename or link in a directory | `w` and `x` on the directory, or `CAP_DAC_OVERRIDE`; and, for an append-only or immutable victim, the flag must already be clear |

Two orderings are load-bearing and are now asserted rather than assumed:
**immutability is checked before DAC on a write open**, so `EPERM` proves nothing
about the mode and `EACCES` proves the flag was already gone; and **the owner
check is evaluated whether or not `CAP_LINUX_IMMUTABLE` is held**, which is why
every negative flag case runs with all other prerequisites satisfied.

### 2.3 The register — nine authorities to eleven

| # | Authority | Minimum holder | Changed? |
|---|---|---|---|
| **A1** | the `CAP_LINUX_IMMUTABLE` half of a flag change | `CAP_LINUX_IMMUTABLE` | **narrowed** — it now confers nothing on its own |
| **A10** | **new** — `FS_IOC_SETFLAGS` owner authorization over the **`freedomsheet`-owned** journal | `freedomsheet`'s uid, **by ownership**; or `CAP_FOWNER` | **added** |
| **A11** | **new** — `FS_IOC_SETFLAGS` owner authorization over the **root-owned** seal and archive | uid 0, or `CAP_FOWNER`. **No service identity holds it** | **added** |
| **A2** | DAC on the live journal *file* | `freedomsheet` by ownership; uid 0; `CAP_DAC_OVERRIDE` | unchanged |
| **A3** | DAC on `…/journal` and the seal within it | uid 0 or `CAP_DAC_OVERRIDE` | unchanged |
| **A4** | DAC on `…/archive` and its files | traverse/read: `freedomcoord`, uid 0, `CAP_DAC_READ_SEARCH`. Write: uid 0 or `CAP_DAC_OVERRIDE` | unchanged |
| **A5** | DAC on the deployment path | uid 0 or `CAP_DAC_OVERRIDE`; H-1 qualifies the repository copy | unchanged |
| **A6** | host identity and restoration control | root on the host where the tree is read | unchanged |
| **A7** | full host-root identity (a composite) | root | now confers **A10** and **A11** as well |
| **A8** | coordinator execution and authentication | `foundry` through the `sudoers` rule; or A7 | unchanged |
| **A9** | PostgreSQL mutation authority | a PostgreSQL superuser. **Held by nobody in this design** | unchanged |

`A2 … A9` keep their labels and their meanings, so every cross-reference in the
package plan, the logical schema and the registers remains valid.

### 2.4 The holder table, which is the R9-B answer

The register says what each authority **is**; the holder table says who can
**hold** it. **Both statements are made explicitly**, which is what revision 9 did
not do.

| Identity | Holds |
|---|---|
| `freedomsheet` inside its deployed unit | **A2, A10** — by ownership of the journal file, and nothing else |
| `freedomsheet`'s uid with an ambient `CAP_LINUX_IMMUTABLE` (**E2**) | **A1, A2, A10** — exactly the set that constructs **F-2** |
| `freedomcoord` (**E8**) | **A8**, and A4's read/traverse only |
| `discordbot`, `freedomweb`, `foundry` | — |
| a non-root uid with `CAP_LINUX_IMMUTABLE` alone (**E3**) | **A1** — and can therefore change **no flag on any inode in this hierarchy** |
| `CAP_LINUX_IMMUTABLE` + `CAP_FOWNER` (**E5**) | **A1, A10, A11** — and almost no inode it can open |
| `CAP_LINUX_IMMUTABLE` + `CAP_DAC_OVERRIDE` + `CAP_DAC_READ_SEARCH` (**E4**) | **A1 … A6** — **and still no flag change**, holding neither A10 nor A11. *The isolating case* |
| all four capabilities (**E6**) | **A1 … A6, A10, A11** — the practical non-root composite |
| uid 0 (**E7**) | **A1 … A8, A10, A11** — everything but A9 |
| a PostgreSQL superuser | **A9**, and no host authority |

**The consequence, stated as bounded claim 2 and materially narrower than
revision 9's.** Every falsification row is assessed twice — against its minimum
combination, and against the smallest identity that can actually hold it. **Only
F-2, F-3 and F-6** are bounded by the attacker's authority rather than by its
choice of alteration. For every other row the writer's refusal tells a responder
**what was done**, not **what could have been done**.

### 2.5 The re-evaluated falsification rows

| Row | Revision 9 | Revision 10 | Why |
|---|---|---|---|
| **F-1a** | `A1 + A3` | **`A1 + A11 + A3`** | the seal is root-owned |
| **F-1b** | `A1 + A2 + A3` | **`A1 + A2 + A3 + A10 + A11`** | two flags on two differently-owned inodes |
| **F-2** | `A1 + A2` | **`A1 + A2 + A10`** | the writer's ownership supplies A10; the label now says so |
| **F-3** | `A9` / `A8` | **unchanged** | no flag is changed |
| **F-4** | `A1 + A4` | **`A1 + A11 + A4`** | archived files are root-owned |
| **F-5** | `A1 + A3` | **`A1 + A10 + A3`** | the `+a` victim is `freedomsheet`-owned |
| **F-6** | `A5` | **unchanged** | no flag is changed |
| **F-7** | `A6` | **unchanged** | no flag is changed |
| **F-8 … F-12** | `A1 + A3` | **`A1 + A11 + A3`** | all five are seal writes |

**Eleven rows change; two do not; none is added, removed or reclassified.** Every
change **adds** a prerequisite, so each alteration becomes harder to construct and
**no refusal in this design is strengthened by any of it**.

---

## 3. The executable identities, and why ambient shorthand was not a specification

`CAP_LINUX_IMMUTABLE` is capability 9 (`0x200`), `CAP_FOWNER` 3 (`0x8`),
`CAP_DAC_OVERRIDE` 1 (`0x2`), `CAP_DAC_READ_SEARCH` 2 (`0x4`).

| Id | UID : GID, groups | Prm | Eff | Inh | Amb | Bnd | Authorities |
|---|---|---|---|---|---|---|---|
| **E1** | `freedomsheet`:`freedomsheet`, +`freedomjournal` | `0x0` | `0x0` | `0x0` | `0x0` | `0x0` | A2, A10 |
| **E2** | `freedomsheet`:`freedomsheet`, +`freedomjournal` | `0x200` | `0x200` | `0x200` | `0x200` | `0x200` | A1, A2, A10 |
| **E3** | `fbprobe`:`fbprobe`, none | `0x200` | `0x200` | `0x200` | `0x200` | `0x200` | A1 |
| **E4** | `fbprobe`:`fbprobe`, none | `0x206` | `0x206` | `0x206` | `0x206` | `0x206` | A1 … A6; **no A10, no A11** |
| **E5** | `fbprobe`:`fbprobe`, +`freedomcoord` | `0x208` | `0x208` | `0x208` | `0x208` | `0x208` | A1, A10, A11; A4 read/traverse |
| **E6** | `fbprobe`:`fbprobe`, none | `0x20E` | `0x20E` | `0x20E` | `0x20E` | `0x20E` | A1 … A6, A10, A11 |
| **E7** | `0`:`0` | full | full | — | — | full | A7 |
| **E8** | `freedomcoord`:`freedomcoord` | `0x0` | `0x0` | `0x0` | `0x0` | `0x0` | A8; A4 read/traverse |

**Why `--ambient-caps` alone is insufficient**, and why every dropping invocation
carries securebits: an ambient capability must **also** be permitted and
inheritable, and a `setuid` away from 0 clears the permitted set unless
`SECBIT_KEEP_CAPS` and `SECBIT_NO_SETUID_FIXUP` are set first. Each row's full
invocation is in package plan §2.13.5c.

**Every case asserts its identity before its result.** The harness reads
`/proc/self/status` inside the dropped process and asserts `Uid:`, `Gid:`,
`Groups:`, `CapPrm`, `CapEff`, `CapInh`, `CapAmb` and `CapBnd` **before** the
operation under test. A case whose identity assertion fails is **`inconclusive`**,
never a pass and never a refusal.

**`fbprobe` is a disposable identity** created and removed by the harness against
a disposable hierarchy. It is added to **A-5.0-5**, which remains **unconfirmed**.

---

## 4. The rewritten evidence cases

### 4.1 `JNL-49` — twelve feasible cases

Cases 1 … 10 are revision 9's, re-stated under corrected combinations and named
identities; cases **11** and **12** are new.

| Case | Combination | Identity | Assertion |
|---|---|---|---|
| 1 | `A1 + A11 + A4` | **E6** | archive altered; `archive-verify` fails; successor registration refused. *Was `A1 + A4`, not constructible* |
| 2 | `A5` | **E4** | **W11** `SW-J22`, **W4** `SW-J25`; and E4 asserted to receive `EPERM` on the seal |
| 3 | `A6` | **E7** on the second host | **W10 passes**, **C-d does not refuse**; **R-5.0-13**. *Unchanged from revision 9* |
| 4 | `A8` alone | **E8** | **V-R** refuses; partial unique index refuses a second head |
| 5 | `A1 + A2 + A10` | **E2** | mid-chain rewrite → **W14** `SW-J09` |
| 6 | `A1 + A2 + A3 + A10 + A11 + A8` | **E6** + coordinator | forged head with no `seal`, no `.close`, no archive; predecessor FK refuses |
| 7 | the same **+ A9** | — | **not refused** — the limit asserted, not hidden. **R-5.0-12** |
| 8 | `A1 + A11 + A4 + A3` | **E6** | both disk copies agree; the registered digest disagrees → `J-16` |
| 9 | **F-5's corrected minimum, three steps** | **E4**, then **E6** | `A3` alone → `EPERM` on `unlink`/`rename`; `A1 + A3` without A10 → **`EPERM`** from the flag clear; `A1 + A10 + A3` → succeeds → **W7** `SW-J11` |
| 10 | **F-2's corrected minimum** | **E2** | clear, rewrite record 0, restore → **W13** `SW-J04`; and **`EPERM`** against the root-owned seal |
| **11** | **new — the owner-authorization boundary** | **E4** vs **E6**; **E1** vs **E2** | on one disposable root-owned `+i` file with DAC fully satisfied: E4 **opens successfully** and receives **`EPERM`**; E6, differing only by `CAP_FOWNER`, **succeeds**. The same pair against a `freedomsheet`-owned `+a` file with E2 as control |
| **12** | **new — flag authority without DAC, made constructible** | **E5** | `+i` cleared **successfully**; `open(O_WRONLY)` → **`EACCES`**. *This is revision 9's case 9, corrected: it now includes the `CAP_FOWNER` the clear requires* |

### 4.2 `JNL-50` — twelve not-constructible cases

| Case | Identity | Sought | Assertion |
|---|---|---|---|
| 1 | **E1** | A3, the seal | `O_WRONLY` → **`EPERM`** with `+i`; **`EACCES`** on a disposable copy without it |
| 2 | **E1** | A3, the directory | `creat`/`unlink`/`rename` → **`EACCES`** |
| 3 | **E1** | **A1** on its **own** inode | `FS_IOC_SETFLAGS` → **`EPERM`**. Owner half satisfied by ownership; control **E2** succeeds |
| 4 | **E2** | **A11** on the root-owned seal | `FS_IOC_SETFLAGS` → **`EPERM`** with the capability held. **New; makes F-2's separation executable** |
| 5 | **E1** | A4 | `open` → **`EACCES`** at the directory |
| 6 | **E4** | **A11** on a root-owned archive file | open **succeeds**; ioctl → **`EPERM`**; control **E6** succeeds. **The R9-A isolating control** |
| 7 | **E4** | **A10** on the journal | same shape against `FS_APPEND_FL`; control **E2** |
| 8 | **E5** | A3 | `creat`/`unlink`/`rename` → **`EACCES`** |
| 9 | **E8** | A2/A3 | `EACCES` on the directory, `EPERM` on the seal open |
| 10 | **E8** | A4 write | traverse and read **succeed**; `O_WRONLY` → **`EPERM`** with `+i`, **`EACCES`** without |
| 11 | `discordbot`, `freedomweb`, `foundry`; **E1**; **E8** | `…/journal`; A8/A9 | `EACCES`; no database connection at all; `UPDATE`/`DELETE` refused |
| 12 | **E1**, **E2** | **A2 and A10 asserted positively** | with `+a` cleared by root, E1's non-append write **succeeds**; E2 clears the flag itself and writes |

**Every negative flag case runs with all other prerequisites satisfied and carries
a positive control that succeeds**, so no refusal here is attributable to an
unrelated DAC or path-search denial.

### 4.3 Cases whose contract changed without changing count

`JNL-13` (thirteen → **fifteen** manipulation rows, §2.13.4), `JNL-35` and
`JNL-38` (corrected minimum combinations, and the negative half against the
root-owned seal), `JNL-30` and `JNL-48` (unchanged, listed so a reviewer can
confirm they were not disturbed).

---

## 5. Changed counts and estimates, with their arithmetic

| Figure | Revision 9 | Revision 10 | Arithmetic |
|---|---|---|---|
| Authority register | 9 | **11** | `A1` narrowed; `A10`, `A11` added; `A2 … A9` unchanged |
| Falsification rows | 13 | **13** | eleven re-stated, two unchanged, none added or removed |
| §2.13.4 manipulation rows | 13 | **15** | `chattr -i` on the seal, and on an archived file |
| Evidence-band identifiers | 50 | **50** | none added |
| Evidence-band cases | 84 | **88** | `JNL-49` 10 → 12 (+2), `JNL-50` 10 → 12 (+2); 84 + 4 = 88 |
| §6.5 items | 19 | **20** | item 20 added |
| Executable identities | 0 specified | **8** | `E1 … E8`; none previously specified as a capability set |
| Fail-closed conditions | 25 | **25** | unchanged; `SW-J01 … SW-J25` unchanged |
| V-W steps | 18 | **18** | unchanged |
| Schema objects | six tables, five trigger conditions, three journal evidence columns, five commands, `jnl-probe-1` | **unchanged, every one** | no schema movement at all |
| Stop conditions | … 10l | **… 10m** | 10m added; 10k extended |
| §7.1 risk rows | 26 | **27** | row 27, a recurrence class, not a residual |
| RAID rows | R-5.0-1 … 14 | **unchanged** | R-5.0-12's authority set corrected to a **larger** one; none added or closed |
| Security-review surfaces | 11 | **11** | unchanged |
| Security-review questions | +2 at R8 | **+2 at R9** | the holder table, and identity constructibility |
| Security review | 3.0–4.0 reviewer-days | **3.5–4.5** | eleven authorities, a holder table to confirm identity by identity, eleven changed combinations |
| PERT estimate | 40.4 | **40.9** | see below |
| Remediation allowance | 11.9 | **11.9** | 0.30 × 39.8 = 11.94 |
| Contingency | 4.0 | **4.0** | unchanged; R9 adds no residual |

**The PERT arithmetic, from the table rather than asserted.** WP-8 moves
O 4.1 → 4.3, ML 8.0 → 8.4, P 12.5 → 13.1; WP-9 moves ML 3.6 → 3.7, P 5.9 → 6.0;
WP-15 moves P 5.5 → 5.8. Totals become **O 19.9, ML 39.8, P 66.5**, and
`(19.9 + 4 × 39.8 + 66.5) / 6 = 245.6 / 6 = 40.93` → **40.9**. Decomposed:
WP-8 **+0.40** → 40.80, WP-9 **+0.08** → 40.88, WP-15 **+0.05** → **40.9**.
**WP-1, WP-2, WP-3, WP-4, WP-4b, WP-6, WP-7 and WP-14 are unchanged** — WP-4b in
particular, because R9 corrects the model of a kernel check the writer never
invokes.

---

## 6. Schema, RAID, decision and preserved-correction impacts

**Schema: none.** No column, constraint, index, trigger, sequence, vocabulary,
table, command or health check changes. Logical schema §3.7's *What this table
uniquely can do* now names the F-1b combination as `A1 + A2 + A3 + A10 + A11`;
§3.7.1's seal-integrity row notes that `A9`'s label is unchanged by the redesign;
§4.3.8's Band 3 carries 88 cases and the corrected A-5.0-5; §9 gains one row and
corrects two. **The property this artifact rests on does not move**: `A9` is held
by no principal in this design.

**RAID: no row added, none closed.** **R-5.0-12**'s authority set is corrected to
`A1 + A2 + A3 + A10 + A11 + A9`, which is **larger** than revision 9's — a harder
combination to assemble, and the same residual. **R-5.0-13** and **R-5.0-14** are
unchanged. **A-5.0-5 is corrected**, its revision-9 capability-only case withdrawn
as not constructible, and **remains unconfirmed**. **D-5.0-1**'s scope and
estimate rise; **D-5.0-2** records that R9 amends D5.0-13 **not at all**.

**Decisions: none added, none decided, no option added.** **D5.0-13 / OD-66 option
A's content does not move** — R9 corrects the *description* of a kernel check
option A's design already depended on, so no artifact, authority, column, refusal
code or cost changes. **Option A-2 is preserved unchanged and remains not
adopted.** Options B, C and D are unchanged. OD-62 … OD-66 remain **Open** and
must not be ruled from revision 10.

**The preserved R8 corrections, checked rather than assumed.** §2.13.2b's three
states, §2.13.2c's `deployment_manifest_digest()` and its C0/C2 placement, and
F-7's classification as **R-5.0-13** with its four-row remaining-evidence table are
present and unaltered in substance. The only edit touching any of them is F-7's
closing sentence, which now says revision **10** continues to take the first of
R8-D's two options.

---

## 7. Exact documentation checks, and their results

| Check | Command | Result |
|---|---|---|
| Whitespace errors in tracked changes | `git diff --check` | **clean; no output, exit 0** |
| Whitespace errors in the untracked review artifacts | `git diff --check --no-index /dev/null <file>` over **all ten** untracked `docs/review/phase-5-0-*` artifacts. *`--no-index` exits non-zero merely because the file differs from `/dev/null`; the check is the **output**, not the exit code, and a first run that read the exit code was corrected* | **clean; no output for any of the ten** |
| Trailing whitespace | `grep -nE ' +$'` over the ten edited or created documents | **none** |
| Tabs | `grep -nP` for a tab over the same | **none** |
| CRLF | `grep -c` for a carriage return over the same | **none** |
| Markdown table integrity | a column-count script over every table in the package plan, the logical schema and this handback: each body row's unescaped, non-code pipe count compared with its header's | **no ragged row.** One flagged line was a false positive of the script's inline-code tokenizer on a nested-backtick cell in this document; the cell was reworded so both the script and a renderer agree |
| Truncated prose and unbalanced inline code | a scan for odd backtick counts per line | **47 lines**, every one either a fenced-block delimiter or an inline-code span deliberately wrapped across two lines, **all pre-existing and none introduced by R9** |
| Duplicated prose | a scan for repeated adjacent lines over 60 characters, and for duplicated table rows | **none found** |
| Heading sequence | `grep -n '^#'` on both review artifacts | **monotonic; §2.13.5c … §2.13.6 intact; the revision-9 “What changed” section demoted to `###` history and revision 10 added as `##` in both documents** |
| Link targets | every relative link in the two review artifacts resolved against the filesystem | **all resolve, including the new `phase-5-0-remediation-r9-handback.md`** |

---

## 8. Checks run, checks not run, and their accountable owners

**Run:** the documentation checks in §7, and the search classification in §9.

**Not run, and why:**

| Not run | Why | Owner |
|---|---|---|
| **The implementation test suites** — `tests/test_*.py`, `tests/web`, the Foundry module tests | **Deliberately not run, as the R9 brief directs.** This remediation changed **no** production code, no test, no migration and no configuration; every edit is to a Markdown document. Running a suite here would produce a figure about a tree whose executable content is identical to the last run's, and reporting it would imply this remediation was verified by it. The brief says to state that it was not run and why, and this is that statement | Technical Lead |
| **Every `TC-5.0-JNL` case, and every case in `JNL-49`/`JNL-50`** | **A-5.0-5 is unconfirmed.** The journal hierarchy does not exist on this host, the disposable `fbprobe` identity was not created, and no `setpriv`, `chattr`, `systemd-run` or privileged probe was run. **Revision 9's two capability-set cases were not merely unrun but not constructible**, which is R9-C | Operations Owner |
| **Any verification that `setpriv` produces the masks `0x200`, `0x206`, `0x208` and `0x20E` on this kernel and util-linux version** | the same authorization boundary. §9.2 asks the Security Reviewer whether the securebits route is the right mechanism, or whether a file-capability or `capsh` route is safer | Operations Owner, with the Security Reviewer |
| **Any confirmation that the `E4`/`E6` pair isolates the owner check** rather than a confound (a mount option, an LSM, an overlay layer) | the same boundary. It is asked as a §9.2 question rather than assumed, because a control that refuses for the wrong reason is precisely the R9-A defect one level down | Security Reviewer |
| **The supervised host reboot** (`JNL-02b`) | unchanged from earlier revisions; it needs Operations Owner authorization | Operations Owner |
| **The `pg_hba`/`pg_ident` peer-denial matrix** (A-5.0-4) | unchanged; it needs a host change | Operations Owner |

**No privileged case is claimed to have run, and no figure in revision 10 is
presented as measured.** The register is an argument checked against the kernel's
documented contract and against nothing else.

---

## 9. Search results for the stale forms, each hit classified

Searched across the package plan, the logical schema, `docs/implementation-plan.md`,
`docs/discovery/open-decisions.md` and the four `docs/project-management/`
registers. **Every hit is classified as corrected live text, a definition, or
labelled history.**

| Search | Hits | Classification |
|---|---|---|
| `CAP_LINUX_IMMUTABLE` near `alone`, `only`, `clear`, `+i`, `+a` | **60 lines** | **Corrected live text:** §2.13.5c's register row **A1**, its holder table, its identity boundary, §2.13.4's two new rows, §2.13.2a **P-8**, §2.13.7's root rationale and its *undocumented ambient capability* paragraph, §9.2 surface 9, and the R9 blocks in the header, §2.13.1 rows 22–24 and *What changed in revision 10*. **Definition:** the E-identity table and the kernel-requirements table, where the capability is named as one of two prerequisites. **Labelled history:** the revision-8 and revision-9 status blocks, §2.13.1 rows 16 and 20, the retained *What changed in revision 8/9* tables, the retained estimate decompositions, the superseded change-log rows, the superseded status sections and the superseded OD-66/RAID paragraphs. **No live sentence credits the capability with a flag change on its own.** |
| `CAP_FOWNER` | **77 occurrences** across eight documents | **All new, and all either corrected live text or a definition.** The term did not appear anywhere in revision 9 except in the reviewer's own finding text, which is exactly the defect |
| `FS_IOC_SETFLAGS` | **76 occurrences** across eight documents | **Corrected live text and definitions.** Every live occurrence names both permission requirements, or is a case that asserts one of them in isolation with the other satisfied |
| `A1 + A3`, `A1 + A4`, `A1+A3`, `A1+A4` | **22 lines** | **Corrected live text showing the old value beside the new:** §2.13.5c's *achieved ability* table (a revision-9 column), the F-1a/F-4/F-5 rows' parenthetical *(revision 9 said …)*, §2.13.5b's verifier row, and §2.13.5c's concession bullets. **Labelled history:** the revision-8/9 header blocks, §2.13.1 rows 20 and 22, the retained *What changed* tables, the retained OD-66 and RAID R8 paragraphs, the superseded status section and the superseded change-log rows. **No live combination against a root-owned inode omits `A11`, and no live flag change on the journal omits `A10`.** |
| `confer nothing`, `confers A2`, `every real` | **15 lines** | **Corrected live text:** §2.13.5c's concession bullet and its holder-table paragraph; §2.13.1 row 23. **Labelled history:** the reviewer's own finding text retained in the header block, the registers' *R9 required* blocks, and the logical schema's R9-B row. **No live sentence asserts both independence and implication.** |
| `clears +i successfully` | **1 line** | **It is the concession**, quoting revision 9 in order to withdraw it: §2.13.5c's opening bullet. §2.13.1 row 24 states the same defect in its own words. **No live case asserts it, and `JNL-50`'s corrected case 6 asserts `EPERM` in its place.** |
| `ambient-caps` | **11 lines** | **Corrected live text:** §2.13.5c's E-identity table, where every invocation also carries `--inh-caps`, `--bounding-set` and securebits; the accompanying *why shorthand is not a specification* paragraph. **Corrected in the registers:** package-plan A-5.0-5, RAID A-5.0-5 and logical-schema §4.3.8, each of which withdraws the revision-9 form. **No live text presents the shorthand as sufficient.** |
| `JNL-49`, `JNL-50` | **88 lines** across eight documents | **Corrected live text:** §2.13.8's two rewritten rows (twelve cases each), §2.13.5c's per-row test column, §6.5 items 18–20, §4's WP-8 movement, logical schema §4.3.8 and §9. **Labelled history:** the retained *What changed in revision 8/9* tables, the superseded status and change-log rows, and the retained OD-66/RAID R8 paragraphs, all of which say eight or ten cases as a record of what those revisions said |
| revision 9 / R8 described as active or awaiting review | 0 in Package 5.0 scope | The only `awaiting re-review` hits are **Phase 4 RAID rows P4-R1 … P4-R5** and two Phase 3 review artifacts, none of which is Package 5.0. Every Package 5.0 document names **revision 10 / R9** as the submitted response and the R9 brief as active: package plan header, logical schema status, implementation-plan §20, status.md, the RAID register, the decision register, open-decisions and the change log. The **R8 handback carries a superseded banner** naming this handback as the active response |

---

## 10. What P5.0-R1, P5.0-R2 and P5.0-R4 look like after this remediation

**Unchanged, all three, and deliberately.**

- **P5.0-R1.** §2.10's barrier search stands; the conclusion is unchanged; the
  journal remains an **enumeration control**; **R-5.0-8 is narrowed by no case**.
- **P5.0-R2.** **Closed, and preserved.** §2.1's authority-state matrix, §2.5's
  effective-time model, OD-55 and OD-58 are untouched.
- **P5.0-R4.** §2.12's host boundary stands and **no operational evidence is
  claimed passed**. OD-64, OD-65 and the Security Reviewer remain open; A-5.0-4
  remains unconfirmed.

**P5.0-R5 remains Blocking**, and revision 10 does not decide whether R9 is
answered.

---

## 11. Confirmation that no finding is claimed closed and no unauthorized action occurred

**No finding is claimed closed.** Closure belongs to the Independent Reviewer.

**No implementation or environment change occurred.** No production code, no
migration `0014`, no table, no database role, no operating-system account or
group, no `pg_hba.conf`, `pg_ident.conf` or `sudoers` entry, no credential, no
Google access change, no configuration or environment change, no directory, file,
file mode or **filesystem attribute**, no deployment, no service restart, no
`systemd-run`, no `chattr`, no `setpriv`, no privileged probe, no reboot, no data
mutation, no Sheet access, no authority cutover, no Package 5.1+ work.
`/var/lib/freedom-sheet-writer` does not exist on this host and was not created;
**no probe arena, no `…/probe-ro` and no `fbprobe` identity were created
anywhere**. **The host was neither read nor written for this remediation.** The
only changes are to documents.

**Documents changed:**

| Document | Change |
|---|---|
| `docs/review/phase-5-0-package-plan.md` | **revision 10**; §2.13.5c redesigned; §2.13.1 rows 22–24 and their narrative; §2.13.2a P-8; §2.13.4; §2.13.5b; §2.13.7; §2.13.8; §4; §5.3; §6.5; §7.1; §7.4; §9.2; §9.3; §10; header and *What changed in revision 10* |
| `docs/review/phase-5-0-logical-schema.md` | **revision 10**; status; *What changed in revision 10*; §3.7; §3.7.1; §4.3.8 Band 3; §9 |
| `docs/review/phase-5-0-remediation-r9-handback.md` | **new** — this document |
| `docs/review/phase-5-0-remediation-r8-handback.md` | superseded banner, naming the two of its statements R9 corrects |
| `docs/implementation-plan.md` | §20 — revision 10 recorded as the R9 response |
| `docs/discovery/open-decisions.md` | the Package 5.0 review note; OD-66's R9 entry, with the R8 entry demoted to history |
| `docs/project-management/status.md` | current update — R9 submitted; the R9-required section demoted to history |
| `docs/project-management/raid-register.md` | the R9-submitted block; the P5.0-R5 row's R9 segment; **A-5.0-5 corrected** |
| `docs/project-management/decision-register.md` | the R9-submitted block; OD-66 option A recorded as unchanged |
| `docs/project-management/change-log.md` | entry **C-P5.0-S** |

---

## 12. What is requested next

1. **Independent re-review of revision 10** of the package plan and the logical
   schema against this handback, by Codex, as Independent Reviewer and as
   independent logical-schema reviewer.
2. **A decision on whether P5.0-R5 is answered**, which is the Independent
   Reviewer's and not the implementer's.
3. **A named Security Reviewer** (D-5.0-1), whose scope now includes eleven
   authorities, a holder table to confirm identity by identity, and the two new
   §9.2 questions.
4. **Rulings on D5.0-9 … D5.0-13 / OD-62 … OD-66**, none of which this revision
   decides, and none of which should be ruled from revision 10.
5. **A decision on A-5.0-5**, which is the Operations Owner's: without the
   disposable identity and the four capability sets, `JNL-49` and `JNL-50` cannot
   be produced and P5.0-R5 cannot close on evidence.

**Nothing in this handback grants implementation, migration, deployment, cutover
or acceptance authority.**
