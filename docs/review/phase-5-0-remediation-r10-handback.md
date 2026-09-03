# Package 5.0 — design remediation R10 handback

Date: 2026-08-31 · Package 5.0 — Migration and cutover harness

Prepared by: Claude — implementer and working Technical Lead (designated, OD-61)

Returned to: Peter Duscha (Acceptance Authority, Product Owner, Data Owner,
Operations Owner, Delivery Lead) and Codex (Independent Reviewer and independent
logical-schema reviewer, OD-61).

In response to: `docs/review/Handover information`, *Package 5.0 remediation R10
— implementation instructions*, which **authorizes documentation and design
remediation only**. No production code, migration `0014`, database or
operating-system change, privileged probe, service change, Google access,
deployment, cutover, Package 5.1+ work or any environment mutation is authorized,
and none occurred.

> **Claude claims no finding closed.** P5.0-R1, P5.0-R4 and P5.0-R5 are closed by
> the Independent Reviewer, not here. **P5.0-R5 remains Blocking.**
>
> **The R10 findings are conceded before any replacement is presented.** Each
> concession is written into the documents themselves — package plan
> **§2.13.1 rows 25–28**, and again at the head of §2.13.5c's executable-identity
> subsection — *before* the corrections are stated, so a reader meets the defect
> first.
>
> - **R10-A.** Revision 10 built identities **E2 … E6** with
>   `setpriv --securebits=+keep_caps,+no_setuid_fixup …`. The installed and named
>   `setpriv(1)` from util-linux **2.39.3** lists its accepted securebits as
>   *"noroot, noroot\_locked, no\_setuid\_fixup, no\_setuid\_fixup\_locked, and
>   keep\_caps\_locked"* and states that **"keep\_caps is cleared by execve(2) and
>   is therefore not allowed"**. Those five commands exit **127** at option
>   parsing. **Five of the eight identities did not exist**, so every `JNL-49` and
>   `JNL-50` case naming them would have stopped at its own mandatory
>   `/proc/self/status` precondition as **`inconclusive`**.
> - **R10-B.** **E8** declared `CapBnd = 0x0` and its recipe dropped nothing.
>   **E7** wrote **dashes** for inheritable and ambient in a subsection whose own
>   title claimed complete masks. And — **not named by the re-review, found by the
>   mechanical comparison the brief requires** — **E2 … E6** requested
>   `--bounding-set=+linux_immutable`, an **addition** to the bounding set, which
>   the same manual page says **"the kernel does not permit"**; from root's full
>   set the declared `0x200 … 0x20E` would have been `0x000001ffffffffff`.
>   **Three recipe/mask disagreements, not two.**
> - **R10-C.** Two dependent claims were wrong rather than merely restated.
>   `JNL-50` case 7 and the journal half of `JNL-49` case 11 gave **E2** as the
>   positive control for an **E4** refusal, but E2 differs from E4 in **uid,
>   supplementary groups and two capabilities** and therefore isolates nothing;
>   and `JNL-50` case 4 named **no control at all**. Both are corrected below.
>
> **Nothing was executed.** No capability set, UID, GID, group or securebit was
> constructed anywhere, no `chattr`, `setpriv`, `capsh`, `systemd-run` or
> privileged helper was run, and **A-5.0-5 remains unconfirmed**. The host was
> **read** non-mutatingly to record the tool contract — package plan §8.1
> **H-6** — and was **not written**. **An independent re-review of revision 11 is
> required.**

---

## 1. Instruction-by-instruction change table

| R10 instruction | Where it is answered | What it now says |
|---|---|---|
| **R10-A** — define a launch mechanism syntactically valid for the exact named util-linux/kernel contract | package plan **§2.13.5c**, *The launch mechanism* and *The construction* | The mechanism is **`capsh(1)`**, not `setpriv(1)`. `capsh(1)` documents that it *"takes a number of optional arguments, acting on them in the order they are provided"*; every intermediate credential state is therefore derivable from the command line plus `capabilities(7)` |
| **R10-A** — do not use `+keep_caps` with `setpriv` | throughout | **`keep_caps` is used nowhere, with any tool.** It is also unnecessary: `capabilities(7)` says `SECBIT_NO_SETUID_FIXUP` *"provides a superset of the effect of"* `SECBIT_KEEP_CAPS` and, unlike it, survives `execve` |
| **R10-A** — if `setpriv` remains, explain precisely how P/E/I/A/B survive the UID transition and the final `execve` | **§2.13.5c**, and §2.13.1 defect 25's lesson paragraph | `setpriv` does **not** remain, and the reason is stated rather than assumed: substituting `+no_setuid_fixup` would make the commands *parse* but not make their results **derivable**, because `setpriv(1)` never states the order in which it applies securebits, the UID/GID change and the three capability sets — and every declared mask depends on that order. The seven-step `capsh` construction gives the full survival argument for each set |
| **R10-A** — if another mechanism is chosen, state its ownership, mode, lifecycle, cleanup, authority and security-review consequences; do not silently widen the host design | **§2.13.5c**, *The launch mechanism, stated as a host fact and priced* | `/usr/sbin/capsh`, `libcap2-bin` 1:2.66-5ubuntu2.4, **already installed**, `root:root`, `0755`, **no file capabilities, not set-user-ID**; lifecycle is the operating system's; **no cleanup is required or performed**; invoked only by the root harness and by no service identity or `sudoers` rule; and the security-review consequence is stated as a new §9.2 question. **No file capability is set, no set-user-ID artifact is created, no helper is written or deployed, no package is installed, and no `sudoers` rule, unit, drop-in, group or directory is added.** The declined alternatives are tabulated |
| **R10-A** — state any prerequisite on root's current bounding set | **§2.13.5c**, *The prerequisite on the launching process's bounding set* | **No tool can add to a bounding set** — `setpriv(1)` says so and `capsh` offers only `--drop`, so **no invocation in revision 11 asks for an addition at all**. The seven capabilities the identities need must already be present; the harness asserts its own `CapBnd` before constructing anything and reports **`inconclusive`** otherwise. Observed on this host: `CapBnd: 000001ffffffffff`, all forty-one capabilities, `CAP_LAST_CAP = 40`, kernel 6.8.0-138-generic (§8.1 **H-6**) |
| **R10-B** — exact UID, GID, supplementary groups and exact `CapPrm`/`CapEff`/`CapInh`/`CapAmb`/`CapBnd` for E1 … E8 | **§2.13.5c**, *The identities* | All eight rows carry exact values, **plus securebits**, which revision 10 omitted from the table entirely. *"No supplementary groups"* is replaced by the exact list the harness sets |
| **R10-B** — replace E7's dashes with explicit masks or an exact justified value | **§2.13.5c** | `CapPrm`, `CapEff`, `CapBnd` = `0x000001ffffffffff`; `CapInh`, `CapAmb` = `0x0`; securebits `0x0`. Derived from `CAP_LAST_CAP = 40` on kernel **6.8.0-138-generic**, read from `/proc/1/status` on 2026-08-31, **labelled environment-dependent**, and required to be **re-read and re-asserted** on the host the harness actually runs on |
| **R10-B** — correct E8 so its recipe creates its declared bounding set | **§2.13.5c** | E8 is built by the same seven-step procedure as every other empty-mask identity, with `--drop` over all forty-one capabilities |
| **R10-B** — a complete invocation for every capability-bearing identity, not *"as E2/E3"* | **§2.13.5c**, *Every invocation, in full* | Eight rows, each a complete command line. `DROP(M)` is a **total** substitution over an enumerated forty-one-name constant, so it is not shorthand and cannot alter the result |
| **R10-B** — retain the rule that a mismatched identity assertion is `inconclusive` | **§2.13.5c**, *The assertion contract* | Retained and extended: securebits are now asserted too, from `prctl(PR_GET_SECUREBITS)`, because `/proc/self/status` does not report them |
| **R10-C** — recheck every E-identity reference in `JNL-49`, `JNL-50`, `JNL-13`, `JNL-35`, `JNL-38`, A-5.0-5 and the logical-schema evidence mapping | §2.13.8, §2.13.2a, §5.1, §7.4, logical schema §4.3.8 and §9 | Done; §9 of this handback lists every hit and its classification. `JNL-48` and §2.13.2a were added to the sweep because they name a privilege drop, and the outcome for both is that **`verify-capability`'s `setpriv --reuid` drop is kept and is explicitly *not* identity E1** |
| **R10-C** — keep every negative flag case paired with a control differing only in the isolated authority; redesign the pair or narrow the claim if not | §2.13.5c *The two control forms*, §2.13.8 | **One pair is redesigned.** `JNL-50` case 7 and `JNL-49` case 11 take **E6** — differing from E4 by `CAP_FOWNER` alone — as the isolating control; **E2** is retained as **corroborating**, by the ownership route, and labelled as such. `JNL-50` case 4 gains **control form C-II**, which holds the identity fixed and varies the inode's owner. **No claim is narrowed**, because C-I with E6 supports it in full |
| **R10-C** — recalculate counts, estimates and security-review effort only if the corrected contract changes them; otherwise state that they are unchanged and why | §2.13.8, §4, §9.2 | **All unchanged, with reasons stated and no arithmetic invented.** Fifty identifiers and eighty-eight cases; PERT **40.9** implementer-days; **3.5–4.5** reviewer-days. §5 of this handback gives the four reasons |
| **R10-C** — do not claim any privileged case ran; A-5.0-5 remains unconfirmed | §2.13.5c, §8.1, §10, and §8 of this handback | No case is claimed to have run. **A-5.0-5 is widened and remains unconfirmed**, and §8.1 **H-6** is explicitly labelled a read of the tool contract and **not** a confirmation of it |

---

## 2. Why the mechanism changed, and not just the option list

The narrow finding is a parse error, and a narrow fix exists:
`+no_setuid_fixup` alone is accepted by `setpriv(1)` 2.39.3, and
`capabilities(7)` says it is **strictly stronger** than the bit that was
rejected — it *"stops the kernel from adjusting the process's permitted,
effective, and ambient capability sets when the thread's effective and filesystem
UIDs are switched between zero and nonzero values"*, it *"provides a superset of
the effect of"* `SECBIT_KEEP_CAPS`, and it **survives `execve`**, which
`keep_caps` explicitly does not. Substituting one token would have made the
commands run.

**It would not have made their results derivable, which is the standard R10
sets.** The declared masks depend entirely on the order in which the tool applies
three things:

- if the **UID transition** happens before the securebit is set, the kernel
  clears permitted, effective and ambient, and nothing later can restore them;
- if the **bounding-set drop** happens after the UID transition, there is no
  `CAP_SETPCAP` in the effective set to perform it with; and
- if the **ambient raise** happens before the inheritable set is populated, it is
  refused, because a capability may be raised in the ambient set only when it is
  already in both permitted and inheritable.

`setpriv(1)` states none of this. Its one relevant sentence — *"setting a uid or
gid does not change capabilities, although the exec call at the end might change
capabilities"* — is a claim about the tool that `capabilities(7)` does not
support on its own, and it names no ordering. **The only way to settle it is to
run the tool and observe, which this remediation is explicitly not authorized to
do.** Writing a recipe whose correctness rests on an experiment nobody may
perform, and then defending it in a document, is the shape of the defect being
corrected.

`capsh(1)` removes the question rather than answering it: *"capsh takes a number
of optional arguments, **acting on them in the order they are provided**."* The
ordering becomes a property of the command line, checkable by reading it.

**What was considered and declined** — recorded in §2.13.5c so the choice is a
choice: `setpriv` with the substitution (undocumented ordering); a **file
capability** on a purpose-built helper (a persistent `security.capability`
artifact with its own ownership, deployment, integrity and revocation questions,
placed inside the hierarchy this package exists to protect); a **set-user-ID**
helper (the same objection, on a host whose set-user-ID inventory §8.1 records as
**not audited**); and a small **`prctl`/`capset`** program (the most precise, but
more code to review than an unmodified distribution binary — **retained as the
named fallback** if `capsh` is absent on the target host).

**The host design is not widened.** The only new host object in the whole
capability harness remains the disposable **`fbprobe`** account, which revision 10
already introduced and A-5.0-5 already carried.

---

## 3. The construction, and why each set survives

Root starts with permitted, effective and bounding full, inheritable and ambient
empty, securebits `0`. **M** is the identity's capability set; `DROP(M)` is the
forty-one-name constant minus **M**.

| Step | Option | Why the result is what it is |
|---|---|---|
| 1 | `--secbits=4` | `SECBIT_NO_SETUID_FIXUP` is bit **2** in `/usr/include/linux/securebits.h` on this host, hence `0x4`. `PR_SET_SECUREBITS` needs `CAP_SETPCAP`, which root holds. **`SECBIT_KEEP_CAPS` (bit 4) is not set**, and `SECBIT_NO_CAP_AMBIENT_RAISE` (bit 6) is cleared, which step 6 needs |
| 2 | `--drop=DROP(M)` | `capsh(1)`: *"remove the listed capabilities from the prevailing bounding set … requires that capsh is operating with `CAP_SETPCAP` in its effective set"*. **A bounding-set drop does not touch permitted or effective**, so `CAP_SETPCAP`, `CAP_SETUID` and `CAP_SETGID` remain usable for steps 3–5 even when `M` excludes them. **B = M** |
| 3 | `--inh=M` | the new inheritable set must be a subset of inheritable ∪ bounding (now `M`) and, absent `CAP_SETPCAP`, of inheritable ∪ permitted. Both hold. **I = M** |
| 4 | `--gid=G --groups=S` | `setgid(2)` and `setgroups(2)`, both needing `CAP_SETGID`, still effective. **They must precede step 5** |
| 5 | `--uid=U` | the transition `capabilities(7)` describes as clearing permitted, effective and ambient — **except that step 1 set the securebit that stops exactly that adjustment**. Needs `CAP_SETUID`, still effective |
| 6 | `--addamb=` per capability in `M` | `PR_CAP_AMBIENT_RAISE` requires the capability in **both** permitted (still full) and inheritable (`M`), and requires `SECBIT_NO_CAP_AMBIENT_RAISE` clear. **No `CAP_SETPCAP` is needed**, which matters, since it is not in `M`. **A = M** |
| 7 | `--shell=<case> --` | the `execve` transformation for a file with **no** capabilities: `P'(amb) = P(amb)`; `P'(perm) = (I ∧ F_I) ∨ (F_P ∧ B) ∨ P'(amb) = M`; `P'(eff) = P'(amb) = M`; `P'(inh) = I = M`; bounding unchanged; securebits preserved except `keep_caps`, never set. **`CapPrm = CapEff = CapInh = CapAmb = CapBnd = M`** |

**The pre-`execve` permitted set never appears in a declared mask**, because step
7 recomputes it from the ambient set. That is why ambient is the carrier, and why
revision 10's `--ambient-caps` instinct was right about the destination and wrong
about the route.

**When `M` is empty** — E1 and E8 — steps 3 and 6 are omitted and step 2 drops
all forty-one. **Step 1 is still executed**, so that **E1 and E2 differ in `M`
and in nothing else**; with an empty permitted set the securebit confers nothing,
and §2.13.5c says so rather than leaving it to be noticed.

---

## 4. The identities, and the mask-versus-recipe comparison

| Id | UID : GID | Supplementary | P | E | I | A | B | Secbits |
|---|---|---|---|---|---|---|---|---|
| **E1** | `freedomsheet` : `freedomsheet` | `freedomsheet`, `freedomjournal` | `0x0` | `0x0` | `0x0` | `0x0` | `0x0` | `0x4` |
| **E2** | `freedomsheet` : `freedomsheet` | `freedomsheet`, `freedomjournal` | `0x200` | `0x200` | `0x200` | `0x200` | `0x200` | `0x4` |
| **E3** | `fbprobe` : `fbprobe` | `fbprobe` | `0x200` | `0x200` | `0x200` | `0x200` | `0x200` | `0x4` |
| **E4** | `fbprobe` : `fbprobe` | `fbprobe` | `0x206` | `0x206` | `0x206` | `0x206` | `0x206` | `0x4` |
| **E5** | `fbprobe` : `fbprobe` | `fbprobe`, `freedomcoord` | `0x208` | `0x208` | `0x208` | `0x208` | `0x208` | `0x4` |
| **E6** | `fbprobe` : `fbprobe` | `fbprobe` | `0x20E` | `0x20E` | `0x20E` | `0x20E` | `0x20E` | `0x4` |
| **E7** | `0` : `0` | `0` | `0x000001ffffffffff` | `0x000001ffffffffff` | `0x0` | `0x0` | `0x000001ffffffffff` | `0x0` |
| **E8** | `freedomcoord` : `freedomcoord` | `freedomcoord` | `0x0` | `0x0` | `0x0` | `0x0` | `0x0` | `0x4` |

Every mask was recomputed independently from the capability indices —
`CAP_DAC_OVERRIDE` 1, `CAP_DAC_READ_SEARCH` 2, `CAP_FOWNER` 3,
`CAP_LINUX_IMMUTABLE` 9 — and cross-checked with `capsh --decode`. **The four
non-zero values revision 10 declared were arithmetically correct**; what was
wrong was that nothing produced them.

**Revision 10, compared mechanically against its own recipes:**

| Id | Declared `CapBnd` | The recipe would have produced | Agrees? |
|---|---|---|---|
| E1 | `0x0` | `0x0` only if the bounding drop precedes the UID change — **not determinable from `setpriv(1)`** | **undetermined** |
| E2 … E6 | `0x200` … `0x20E` | **`0x000001ffffffffff`**; and in any case the command **exits 127** | **no** |
| E7 | *"full"* | not evaluable — no mask, no `CAP_LAST_CAP` | **not evaluable** |
| E8 | `0x0` | **`0x000001ffffffffff`** | **no** |

**Revision 11:** every row derived option by option from its invocation, and
every one agrees. E7 is the single exception in kind — it is **measured** rather
than derived, and is required to be re-measured on the target host.

---

## 5. Counts, estimates and effort — unchanged, and why

The brief requires recalculation **only if the corrected contract actually
changes them**, and an explicit statement otherwise. **Nothing changes.**

| Figure | Revision 10 | Revision 11 |
|---|---|---|
| Evidence identifiers | 50 | **50** |
| Evidence cases | 88 | **88** (`JNL-49` 12, `JNL-50` 12) |
| Authorities | 11 | **11** |
| Falsification rows | 13 | **13** |
| §2.13.4 manipulation rows | 15 | **15** |
| Fail-closed conditions / refusal codes | 25 / `SW-J01 … SW-J25` | **unchanged** |
| Estimate | PERT 40.9 | **PERT 40.9** |
| Remediation allowance | 11.9 | **11.9** |
| Security review | 3.5–4.5 reviewer-days | **3.5–4.5** |
| Schema objects | unchanged | **unchanged** |

**The four reasons, stated rather than asserted:**

1. **No case, identifier or test is added or removed.** R10 corrects how an
   identity is *built* and which identity is the *control*; the executed work is
   the same work.
2. **The capability harness was already budgeted** — WP-8 **+0.40** and WP-9
   **+0.08** in revision 10. R10 substitutes one already-installed,
   non-set-user-ID, no-file-capability system binary for another **inside** it,
   and adds a single `prctl(PR_GET_SECUREBITS)` assertion beside five
   `/proc/self/status` assertions the harness already made.
3. **No host artifact, account, group, unit, `sudoers` rule, package
   installation, privileged command or production code path is added.** WP-4b,
   WP-14 and WP-15 cannot move; `verify-capability`, `freedom-journal-admin`,
   `migration-authority` and the writer are untouched.
4. **The redesigned control pair reuses an identity the plan already builds.**
   E6 was already in the table and already constructed for other cases.

**Nothing is rounded, absorbed or netted off to reach that answer.** Inventing an
increment for a documentation remediation that adds no executed work would be an
estimate about a state that does not exist — the class of claim stop condition
**10b** forbids.

---

## 6. What changed elsewhere, and what deliberately did not

**Added — three items, and nothing else.**

- **Stop condition 10n**: no executable identity may declare a credential state
  its own recipe does not produce, and none may be constructed by a mechanism
  whose ordering the named tool's documentation does not determine. It completes
  **10m**: 10m requires the identity to be *specified* completely, 10n requires
  it to be *constructible* as specified.
- **§7.1 risk row 28**: the recurrence class — a specification written against a
  model of a tool rather than against the tool's documentation.
- **§8.1 row H-6**: the non-mutating tool-contract read, dated 2026-08-31, and
  explicitly **not** a confirmation of A-5.0-5.

**Changed.**

- **A-5.0-5** is widened: `capsh(1)` and `libcap2-bin` on the target host, the
  launching bounding set as a prerequisite, `prctl(PR_GET_SECUREBITS)` readable,
  and the case binary carrying no file capability and no set-user-ID bit.
  **Revision 10's wording is withdrawn rather than carried forward**, exactly as
  revision 10 withdrew revision 9's. **It remains unconfirmed.**
- **§9.2** replaces its E1 … E8 bullet with the questions the new mechanism
  actually raises, including whether a root harness constructing reduced
  identities with an unmodified distribution binary is the right approach given
  that the host's set-user-ID inventory is **not audited**.
- **§8.1's last row** no longer says `setpriv` presence was not checked; H-6
  records it. **Everything else in that row remains unverified.**

**Preserved unchanged in substance, as the brief requires.** The **R8-A**
deployment-digest lifecycle (§2.13.2c), the **R8-B** cleanup state machine
(§2.13.2b), the **R8-D/F-7** residual treatment and **R-5.0-13**, and revision
10's **R9-A** kernel-requirements table, eleven-authority register, holder table
and thirteen-row falsification matrix and **R9-B** primitive-versus-holder
separation with its narrowed bounded claim 2. **No corrected executable identity
produced a direct conflict with any of them**, so nothing was stopped and
reported under the brief's conflict clause. **R-5.0-12, R-5.0-13 and R-5.0-14
are unchanged and no RAID row is added or closed. No decision number, option,
schema object, column, constraint, index, trigger, sequence, command, vocabulary
or health check changes.**

---

## 7. Documentation checks, and their results

All non-mutating. **Nothing in this list changed a UID, GID, group, capability
set, securebit, file, mode or filesystem attribute, and nothing executed a
privileged helper.**

| Check | Result |
|---|---|
| **1 — record `setpriv --version` for the target tool** | **`setpriv from util-linux 2.39.3`**; `dpkg -l util-linux` → `2.39.3-9ubuntu6.5`. Recorded in §8.1 **H-6** |
| **2 — check every named `--securebits`, capability and group option against that version's documented syntax** | The installed `setpriv(1)` accepts only `noroot`, `noroot_locked`, `no_setuid_fixup`, `no_setuid_fixup_locked`, `keep_caps_locked` — **`keep_caps` is documented as not allowed**, confirming the finding; it also documents that **the kernel does not permit additions to the bounding set**, which is defect 26. `setpriv --list-caps` enumerates forty-one names; the four used are present. `capsh(1)`'s `--secbits`, `--drop`, `--inh`, `--gid`, `--groups`, `--uid`, `--addamb` and `--shell` were each checked against the installed page, and its ordering guarantee quoted. `capabilities(7)` was checked for the UID-transition rules, the securebit semantics, the `execve` transformation and the ambient-raise preconditions. `/usr/include/linux/securebits.h` gives `SECURE_NO_SETUID_FIXUP = 2`, hence `0x4`. **`capsh` takes numeric uid/gid/group values**, which is why §2.13.5c states the name→number resolution explicitly |
| **3 — demonstrate that no recipe asks `setpriv` to add a capability to the bounding set without stating the prerequisite** | **Discharged by construction.** `capsh` has **no** bounding-set addition option, so **no invocation in revision 11 can express one**. The prerequisite is stated in its own subsection and asserted at run time from the harness's own `CapBnd`, an absence yielding `inconclusive`. Revision 10 **did** ask — `--bounding-set=+linux_immutable` in E2 … E6 — and is conceded as defect 26 |
| **4 — mechanically compare each declared P/E/I/A/B mask with the recipe intended to produce it** | Done for **both** revisions and tabulated in §2.13.5c. Revision 10: **three disagreements** — E2 … E6 (bounding), E8 (bounding), E7 (not evaluable) — plus E1 undetermined. Revision 11: **every row agrees**, E7 by measurement. Every mask was also recomputed independently from capability indices and cross-checked with `capsh --decode` |
| **5 — Markdown whitespace, table-shape, heading-order, link and stale-wording checks across all changed controlled documents** | `git diff --check` **clean**; **no trailing whitespace and no tab characters** anywhere in the nine changed documents; **every Markdown table has a consistent column count** (escaped pipes excluded, all nine scanned in full); **heading order is monotone**, the two apparent exceptions being `#`-prefixed lines inside fenced `pg_hba`/`pg_ident` code blocks, which predate this remediation; every internal document reference resolves, the two exceptions being `docs/contracts/phase-5-migration-and-cutover-contract.md` and `docs/operations/migration-cutover-and-rollback.md`, which are **§1.2 deliverables of this package** and correctly do not exist yet. **Fourteen pre-existing stray blank lines that split a Markdown table in two were found and removed** — three in the package plan (§6.5 and §7.1), five in the RAID register, one in the decision register and five in the change log. A blank line inside a table ends it, so the rows after it were rendering as plain text without their header. **None was introduced by R10**, the fix is whitespace only, and no cell content changed. Stale-wording results are in §9 below |
| **6 — report implementation and privileged suites as not run, with the reason** | **Not run.** §8 below |

---

## 8. Checks run, checks not run, and their accountable owners

| Not run | Why |
|---|---|
| **Every `TC-5.0-JNL` case, and every case in `JNL-49`/`JNL-50`** | **A-5.0-5 is unconfirmed.** The journal hierarchy does not exist on this host, and creating it, creating `fbprobe`, setting `chattr +a`, or constructing any capability set is a host change this remediation is not authorized to make. **Owner: Operations Owner** |
| **Any verification that the `capsh` seven-step construction produces `0x0`, `0x200`, `0x206`, `0x208` and `0x20E` on this kernel** | the same authorization. It would change a UID, a group list and a capability set, which the brief forbids in terms. **The construction is argued from `capsh(1)` and `capabilities(7)` and from nothing else, and this handback does not claim more.** **Owner: Operations Owner** |
| **Any determination of `setpriv`'s internal option ordering** | it requires running `setpriv` with a UID change, which the brief forbids. **This is why the mechanism was changed rather than the recipe patched** |
| **The Python, web and Node suites** | no source file, test, migration, configuration or dependency changed. A green run would be a statement about a tree that this remediation did not alter |
| **Formatter, linter and type checker** | **none is configured** in this repository (§8.1). Stated as not configured, never as passed |
| **The privileged probe, `verify-capability`, `init-generation`, `freedom-journal-admin` and any `sudo` path** | unauthorized, and none of their code or contracts changed |
| **A supervised reboot, `fsync` fault injection, `systemd-run`** | unauthorized; unchanged from revision 10 |

| Run | Result |
|---|---|
| Reading of the installed `setpriv(1)`, `capsh(1)`, `capabilities(7)` manual pages and `/usr/include/linux/securebits.h` | as tabulated in §7 |
| `setpriv --version`, `setpriv --list-caps`, `capsh --decode=<mask>`, `dpkg -l`, `dpkg -S`, `ls -l`, `getcap`, `getent passwd`, `getent group`, `cat /proc/self/status`, `cat /proc/1/status`, `uname -r` | **all read-only.** Recorded in §8.1 **H-6** |
| Independent recomputation of every declared capability mask from capability indices | agrees with `capsh --decode` and with the declared values |
| Markdown whitespace, table-shape, heading-order, link and stale-wording checks | §7 check 5 and §9 |

---

## 9. Stale-form search results, each hit classified

Searched across `docs/` for `keep_caps`, `--bounding-set=+`, `--ambient-caps`,
`CAP_LINUX_IMMUTABLE`-only flag clears, `A1 + A2 + A3`, `A1 + A3`, `A1 + A4` and
every `E1 … E8` reference.

| Form | Hits | Classification |
|---|---|---|
| `keep_caps` | package plan, logical schema, implementation plan, status, RAID, decision register, change log, open decisions | **All corrected live text or deliberate history.** Every live occurrence now names it as the rejected securebit; every other occurrence is inside a superseded block, a conceded-defect row, or a review record that must retain the original wording |
| `--bounding-set=+` | package plan §2.13.1 row 26, §2.13.5c's concession and comparison table, and the governance summaries | **All are the conceded defect being stated.** **No recipe uses the form** |
| `--ambient-caps` | package plan §2.13.1 row 24 and the revision-10 header block; logical schema §4.3.8 and its revision-10 row; R8 and R9 handbacks | **All history.** The live `--ambient-caps` instinct is discussed in §2.13.5c only to explain why the ambient set is the carrier |
| a **`CAP_LINUX_IMMUTABLE`-only** identity clearing `+i` | logical schema §4.3.8's `JNL-50` sentence and §9's threat-model row | **Two live hits, found here and corrected.** Both still described the identity that clears `+i` and receives `EACCES` as holding `CAP_LINUX_IMMUTABLE` *"and nothing else"*, which is revision 9's non-constructible form — without the owner half the ioctl returns `EPERM` and the open is never reached. **The package plan corrected the case in revision 10 as `JNL-49` case 12 under identity E5; these two copies were not corrected with it.** Both now name **E5**, `CAP_LINUX_IMMUTABLE` **and `CAP_FOWNER`** |
| `A1 + A2 + A3` as R-5.0-12's host half | logical schema §9's threat-model row | **One live hit, found here and corrected.** It still gave the residual as `A1 + A2 + A3` plus a PostgreSQL superuser. R9-A widened the host half to `A1 + A2 + A3 + A10 + A11`; §3.7 was updated in revision 10 and this copy was not |
| `A1 + A2 + A3 + A8` for `JNL-49` case 6, and *"ten cases in revision 9"* for `JNL-49` and `JNL-50` | logical schema §4.3.8 | **Two live hits, found here and corrected.** The band was still described at revision 9's counts and combination. Now `A1 + A2 + A3 + A10 + A11 + A8`, and **twelve cases each since revision 10** |
| `setpriv --reuid=freedomsheet` | package plan §2.13.2a and `JNL-48(a)` | **Kept, and now explicitly annotated.** It requests **no securebit and no capability option**, so no R10 finding touches it, and its result is derivable without knowing `setpriv`'s ordering. It differs from **E1** in retaining the launching bounding set — *more* latent authority, never less — which cannot manufacture a false pass, since every case run under it is a positive control expected to succeed with an empty permitted set against a target carrying no file capability. **`verify-capability` acquires no `capsh` dependency** |

**Five live stale statements, across four passages, were found by this sweep and
corrected** — all in the logical schema, all of them revision-10 omissions rather
than R10 findings. They
are reported here rather than absorbed silently, because a correction that leaves
copies of the superseded claim behind is the defect class §2.13.1 has now
recorded four times.

---

## 10. What P5.0-R1, P5.0-R2 and P5.0-R4 look like after this remediation

Unchanged, and deliberately so.

- **P5.0-R1** — §2.10's barrier search stands, §2.10.2's conclusion is unchanged,
  and **R-5.0-8 is narrowed by no cases at all**. R10 touched nothing in it.
- **P5.0-R2** — **remains closed.** §2.1's authority-state matrix, OD-55 and
  OD-58 are preserved unchanged.
- **P5.0-R4** — §2.12's coordinator host boundary stands; **no operational
  evidence is claimed passed**; OD-64, OD-65 and the named privileged checks
  remain open, and the Security Reviewer remains **unnamed**.
- **P5.0-R5** — **remains Blocking**, and is the reviewer's to close.

---

## 11. Confirmation that no finding is claimed closed and no unauthorized action occurred

- **No finding is claimed closed.** P5.0-R5 remains **Blocking**; P5.0-R1 and
  P5.0-R4 remain **open**; P5.0-R2 remains **closed**.
- **No decision is made.** D5.0-9 through D5.0-13 / OD-62 through OD-66 remain
  **Open**; no decision number and no option is added; D5.0-13 / OD-66's options
  do not move. **The `capsh` choice is an evidence-harness mechanism inside
  unconfirmed A-5.0-5 and is routed to the Security Reviewer, not decided here.**
- **No option, risk, decision or schema object is adopted or closed by R10.**
- **The Security Reviewer remains unnamed.**
- **Package 5.0 is `not ready` and implementation remains unauthorized.**
- **No implementation or environment change occurred.** No production code, no
  migration `0014`, no table, no database role, no operating-system account or
  group, no `pg_hba.conf`, `pg_ident.conf` or `sudoers` entry, no credential, no
  Google access change, no configuration or environment change, no directory,
  file, file mode or filesystem attribute, no deployment, no service restart, no
  `systemd-run`, no `chattr`, no `setpriv`, no `capsh`, no privileged probe, no
  data mutation, no Sheet access, no authority cutover, no Package 5.1+ work.
  `/var/lib/freedom-sheet-writer` does not exist on this host and was not
  created; **no probe arena, no `…/probe-ro` and no `fbprobe` identity were
  created anywhere.**
- **The host was read and not written.** §8.1 **H-6** records `setpriv --version`,
  `dpkg`, `ls`, `getcap`, `getent`, `/proc/*/status`, `uname` and header reads —
  all non-mutating. **No capability set, UID, GID, group or securebit was
  constructed anywhere**, and **H-6 is not a confirmation of A-5.0-5.**
- **The only changes are to documents**: the package plan, the logical schema,
  this handback, implementation-plan §20, and the five governance registers the
  brief names. Beyond the content the brief requires, the only other edits are
  **fourteen whitespace deletions** — pre-existing stray blank lines that split a
  Markdown table in two, listed in §7 check 5. They change no cell, no figure and
  no claim.

---

## 12. What is requested next

1. **An independent re-review of revision 11**, which this submission requires
   and does not pre-empt.
2. **A ruling on whether the launch mechanism belongs in the decision register.**
   This submission treats it as an evidence-harness detail inside unconfirmed
   A-5.0-5 and routes it to the Security Reviewer. If the Acceptance Authority
   judges otherwise, that is a ruling to make, not one made here.
3. **A named Security Reviewer** (D-5.0-1), whose scope now includes the
   questions §9.2 adds about a root harness constructing reduced identities with
   an unmodified system binary, and about the declined alternatives.
4. **Nothing else.** No implementation, migration, host change, privileged probe,
   deployment, cutover or Package 5.1+ work is requested or authorized, and
   **A-5.0-5 remains unconfirmed** until the Operations Owner authorizes the
   environment the evidence needs.
