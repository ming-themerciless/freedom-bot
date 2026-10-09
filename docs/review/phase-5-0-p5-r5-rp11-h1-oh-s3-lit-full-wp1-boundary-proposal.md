# Proposal — LIT-FULL WP-1: the R3-ROOT root-procedure boundary, with BQ-2 and BQ-3 decision-ready

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-20261007-09`

Date: 2026-10-07

Executor: Claude Code (Sonnet 5.5) on the production workspace controller

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-claude-prompt.md),
5504 bytes, SHA-256 `60074759b6e0ae8f41b9cf3d5ddd0f477fa960cc4cd4d7fad5f21661b0a1011e`,
recomputed before any edit and equal to the pin in the
[WP-1 authority](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-lit-full-wp1-authority.md).

Durable handback: [`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-handback.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-handback.md).

**Status: a proposal for independent Codex review and Peter Duscha's decision.
Nothing in it is accepted. BQ-2 and BQ-3 are PENDING PETER'S DECISION. This record
decides neither, creates no authority, and authorizes neither WP-2 nor any later
package.**

---

## 0. Outcome

### 0.1 In one page

* **What was asked.** Execute WP-1 of the accepted R8 proposal [R8 §9.5] for the
  commissioned LIT-FULL / R3-ROOT investigation [G-1 decisions]: state which
  procedures are in scope, where each begins, and whether any exception would be
  required, so that BQ-2 and BQ-3 can be decided by Peter.
* **Recorded from the commissioned direction, not decided here.** BQ-1 is R3-ROOT.
  BQ-4 is *no dynamic child in a root procedure's process tree* (§2, §9).
* **Root procedures that need no exception.** The four that PID 1 starts: CP
  (`consume`), the holder, the stop-post and the backstop (RT-1 … RT-4, §4). Their
  first image is what the unit names, and nothing dynamic precedes it. LIT-FULL can
  satisfy LR-1 … LR-6 for them literally.
* **Where the boundary question really lies.** Every root act that **`sudo`** starts
  begins with a dynamic root program that **no design in this repository controls**:
  `attest` (RT-5), the installer class (IC-1 … IC-3), AP-2's `sudo systemd-run`
  (SA-1) and, **found while preparing this record and not named in R8 §9.3 (E-4)**,
  the OS-6 interruption `sudo -n systemctl stop` (SA-2, §4.4). `sudo` itself cannot be
  made loader-free by any design this repository contains, so:
  * **beginning the procedure at `sudo` makes LR-2 unsatisfiable** for every such path
    (§5.3). It is not an exception; it is a boundary under which LIT-FULL cannot be
    met unless a start path that does not use `sudo` is designed, and none is
    designed, cited or evaluated in any accepted record (§5.5);
  * **beginning at the first image the design controls** satisfies LR-1 … LR-6 for
    everything the procedure does, **and requires the single `sudo` exception that R8
    §9.3 (BQ-2) and §12.2 (BC-4) already say it requires** (§5.4, §8).
* **A second, separate finding for BQ-2.** AP-2 and the OS-6 stop have **no controlled
  image today**: they run the distribution's `systemd-run` and `systemctl` directly.
  "The first image the procedure controls" therefore does not exist for them. The
  question is not only *where they begin* but *whether they are root procedures that
  must acquire a controlled image* (§5.2, §5.4.2).
* **Recommendation (PENDING PETER'S DECISION).**
  **BQ-2: begin at the first image the design controls; `sudo` is a launch preamble
  stated as one bounded exception (BC-4); bring AP-2 and the OS-6 stop into the set
  with a static client image each, so that the only dynamic root program left on any
  `sudo`-started path is `sudo` itself.**
  **BQ-3: leave the installer class outside the root-procedure set, stated as an
  exception with HB-1, because it runs outside the grant window and its output is
  re-verified by accepted controls, and because a loader-free installer is the
  largest single item and still would not remove `sudo`.** Exact sentences are in §7.
* **An exception is required by the recommendation.** The recommended answers to
  BQ-2 and BQ-3 are each an **exception to LR-1 … LR-2 under R8 §12.2 BC-4**. Following
  the prompt, this record **stops at reporting that fact and treats nothing as
  approved**. Whether the BQ-3 outcome is an *exception* or only a *determination of
  which procedures are in the set* is a classification R8 itself resolves toward
  "exception"; I have followed R8 and ask Codex to confirm (§8, Q-3).
* **An exception-free answer is not available from the repository.** The only
  exception-free route for a `sudo`-started path is a non-`sudo` privileged start
  that is loader-free. It is not established (§5.5). If Peter will approve no
  exception, BQ-2 cannot be answered within LIT-FULL by anything the accepted
  records contain; the choices then are a new design work package for that start path
  (outside this assignment), WITHDRAW, or a §0.2 scope change.

### 0.2 Decision summary

| Question | Status | Where |
|---|---|---|
| BQ-1 | **recorded**: R3-ROOT, from the commissioned direction | §2 |
| BQ-2 | **pending Peter's decision**; recommendation B2-F with AP-2 and OS-6 stop brought into the set; **exception (BC-4) required** | §5, §7.1, §8 |
| BQ-3 | **pending Peter's decision**; recommendation B3-OUT, **exception (BC-4) with HB-1 required** | §6, §7.2, §8 |
| BQ-4 | **recorded**: no dynamic-child exception; constrains WP-2 … WP-7 | §2, §9 |
| BC-2 (is R3-ROOT a narrowing of DR1 §5.3?) | **not decided by any accepted record; flagged** | §8, Q-1 |

### 0.3 What this proposal does not do

It does not perform WP-2's system-call-intent inventory (§9.4 lists the only
delegation map it uses, and that map is R8's). It records no host fact and collected
none. It does not edit R8, the R2 citation record, the design, any decision, change-log
or register, or any historical snapshot. It does not select LIT-FULL for
implementation, open §0.2 change control, approve an exception, or choose among SSW,
SCDC, ACCEPT-X1, LIT-DR1 and WITHDRAW.

---

## 1. Sources, method and fact classes

### 1.1 Documents read

Completely: `.agents/AGENTS.md`; the WP-1 prompt, authority and G-1 decision record;
`docs/review/Handover information`; the restriction banner of
`docs/operations/disposable-test-server.md`; `docs/project-management/status.md`;
`docs/implementation-plan.md` reading map, §0, §16 and §20; the R8 acceptance record.

From the accepted cumulative R8 proposal
([`…-r8-remediation-proposal.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md)),
the sections the prompt names: §2.4, §9.1 … §9.7 (read whole), §11, §12 and §13, and
§7.2 … §7.5 and §7.5a.1, which bear on the process tree. I consulted §4 and §5 (lock
and recovery-ladder text) only by targeted search, and did not read the rest of the
4,800-line proposal; nothing here depends on it, and where I lean on a rule outside
those sections I name it and say so.

From the accepted OH-S2 R2 citation record
([`…-oh-s2-r2-citations.md`](phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md)): §8
(introductory note), §10.4 and §15.4 (X-1), §15.5 and §16. R8's own citations of other
R2 sections (for example §6.4 (e)) are used only as R8 states them.

From the accepted one-host design
([`…-oracle-test-one-host-design-amendment-proposal.md`](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md),
"[D]" in R8): §3.5 (AS-12), §3.6 (OH-D-6), §4.2.4 (the verified-exec stub and its
stated limit), §4.2.5-R2 (e) (the AP-2 literal) and (i) (attestation), the OS-6 / route (iii-a) text of §4.2.5-R4 (e), and the OH-S4 row
that lists the subcommands of `rp11_h1.py`. I used it only to **identify and locate**
`sudo`-started acts, never to alter a finding. Three fixed-string searches support the
completeness statements: `sudo -n` over the design, `sudo -n` over R8, and `H-1R` over
the design (handback §4).

The unaccepted R1 proposal's §9.4.4 (the HB-1 note) was **not relied on**; HB-1 is
used only as R8 §13.1 states it.

### 1.2 Method

Repository text only. Every statement below carries one of these tags.

| Tag | Meaning |
|---|---|
| **[A]** | **derived from accepted repository text**; the source is named. I restate it and change nothing in it |
| **[O]** | an **observation about the accepted text** (an omission, an ambiguity, a classification R8 leaves implicit). It adds no fact; it is a reading for review |
| **[N]** | a **new recommendation or analysis** of this record. It is not accepted, and no later document may cite it as accepted |

No host fact is stated. Nothing about `sudo`'s configuration, linkage, privilege
handling, the distribution binaries, or any kernel or glibc behaviour is relied on
beyond what the accepted records say, and where R8 records the absence of a fact I
repeat the absence (for example MF-9, the linkage of `systemd-run`, `pkcheck` and
`sleep`). **I do not rely on any belief about how a setuid program treats its
environment**, because no accepted record cites one; §5.4 says what it would take to
state that.

---

## 2. The commissioned direction, recorded

| ID | Recorded as | Source |
|---|---|---|
| **BQ-1** | **R3-ROOT.** The investigated path is LIT-FULL under R3-ROOT, not LIT-DR1. The `ubuntu`-run entry may remain Python and is **outside** the root-procedure set | prompt, "Fixed direction"; [A: G-1 decisions] |
| **BQ-4** | **no dynamic child** in any root procedure's process tree. LIT-FULL satisfies LR-1 … LR-6 literally, so LR-2 admits no exception for a child. No SCDC or other exception is introduced | prompt, "Fixed direction"; [A: R8 §9.4 LIT-FULL row, §12.2 BC-3 "Not needed for LIT-FULL"] |
| SSW, SCDC, ACCEPT-X1 | **not selected**; remain scope-change alternatives | prompt; [A: R8 §9.4] |
| WITHDRAW | available only as a later decision of Peter's; not this assignment's direction | prompt; [A: R8 §9.4, §12.2 BC-5] |

**LR-1 … LR-6**, restated verbatim in substance from [A: R8 §9.2] so that §§5 … 9 are
readable alone: (LR-1) no CPython in *p*'s process tree; (LR-2) no dynamic loader in
*p*'s process tree, every image *p* executes, children included, being static, or *p*
doing the function itself; (LR-3) RH-1 … RH-3 hold for each image; (LR-4) every DI-1 …
DI-6 function is in-process or by a cited loader-free interface; (LR-5) the accepted
behaviours are preserved by stated mapping; (LR-6) each image passes the D9 chain and
PO-17.

**One consequence of BQ-4 worth stating at the outset** [N]: LR-2 speaks of *p*'s
**process tree**. Where *p* begins therefore decides what is *inside* the tree. A
`sudo`-started procedure whose tree begins at `sudo` contains `sudo`; one whose tree
begins at the image `sudo` executes does not. That is the whole of BQ-2, and R8 §9.3
already says so in its own words: *"Treating `sudo`'s own loader as outside the
procedure is an exception to LR-2 and needs to be stated as one."*

---

## 3. The R3-ROOT entry boundary (not a root procedure)

This section exists so that no reader mistakes the `ubuntu`-run entry for a root
procedure. **It is not in the root-procedure set, and nothing in §§4 … 9 applies to it.**

| Item | Statement | Source |
|---|---|---|
| Role | **entry** | [A: R8 §9.6.1] |
| Started by | PID 1, the **capture unit's `ExecStart=`** | [A: R8 §9.6.1] |
| Runs as | **`ubuntu`**, under `NoNewPrivileges` | [A: R8 §9.1 table; §9.6.1 "`rp11-launch` (static, `ubuntu`, NNP)"] |
| First image | `rp11-launch` (static), which then `execve`s `python3.12 -I -S …/rp11_entry.py` today, the accepted literal being already marked for replacement | [A: R8 §9.6.1] |
| Under R3-ROOT | **unchanged in kind**: `rp11-launch`, then Python as `ubuntu`; the literal retarget to `/usr/bin/python3.14` is **the only source delta of the entry image** (Role A, A1) | [A: R8 §9.6.1, §9.6.2 A1] |
| Environment | `rp11-entry-env/1` | [A: R8 §9.6.1] |
| What binds it | **PO-12′ and PO-19** (the entry's literal environment and its interpreter closure; MF-1, MF-2, MF-4 at the entry's consumer set) | [A: R8 §9.1 table; §13.2] |
| Why it is not a root procedure | the R3-ROOT set is *"the root procedures that touch the grant and the activation mechanism"*; the entry is not root | [A: R8 §9.1] |
| If BQ-1 were R3-DR1 | the entry becomes Python-free and A1 … A5 obsolete; that is WP-8, **not commissioned** | [A: R8 §9.4 LIT-DR1, §9.5 WP-8] |

**Boundary between the entry and the root set** [A+O]: CP (RT-1) is started by PID 1
as `ExecStartPre=+` of the same capture unit, as **root**, **before** the unit's
`ExecStart=` runs the entry as `ubuntu` [A: R8 §9.6.1 rows *consume* and *entry*; §7.3
row 20]. They share a unit and nothing else. The entry's PO-12′ / PO-19 obligations do
not discharge any obligation of CP, and CP's obligations under LIT-FULL do not touch
the entry.

**Also outside the set, by the same reading** [A: R8 §7.3 row 21]: the executor's
verification reads (AP-0, H-2, H-2b, AV-1's re-verification as an unprivileged
executor step) are unprivileged and interactive; they are not root procedures.

---

## 4. The root procedures implicated by R8

### 4.1 Reading of the table

* *Accepted name* is the name in R8 / the design.
* *Caller* is who causes the process to start.
* *Current first root image* is what the **accepted text** runs first as root. The
  accepted text names `/usr/bin/python3.12`, a literal R8 already marks for
  replacement; the replacement by `python3.14` is **refuted for the root roles** (X-1)
  [A: R8 §9.6.1; R2 §10.4, §15.4]. In every row the first mapped image is therefore
  the CPython interpreter, started through the dynamic loader.
* *Controlled first image (LIT-FULL)* is R8 §9.6.1's LIT-FULL column: **a static image
  that performs the procedure itself**. Its name, path and size are **WP-4's**, not
  fixed here.
* *DI* lists the delegations of R8 §9.3 that the procedure uses, as R8 §9.6.1 and §9.3
  ("Used by") record them. It is a boundary aid, not WP-2's inventory.

### 4.2 Table RT: procedures that PID 1 starts, and `attest`

| ID | Accepted name | Caller | Current first root image | Controlled first image (LIT-FULL) | DI-1 … DI-6 delegated today |
|---|---|---|---|---|---|
| **RT-1** | **consume** (CP: CQ-0 … CQ-7) | PID 1, the capture unit's `ExecStartPre=+` | `python3.12 -I -S …/rp11_h1.py consume`, under PID 1's open environment block | a static image performs CQ-0 … CQ-7 and DI-1, DI-5, DI-6 itself; RH-1 … RH-3 | DI-1 (CQ-4), DI-5 (CQ-5), DI-6 (PK/2 subject) |
| **RT-2** | **hold** (the holder: ACT, HL, IGR, GRR) | PID 1, the transient holder unit that AP-2 creates | `python3.12 -I -S …/rp11_h1.py hold ⟨id⟩ ⟨a2⟩` | a static image performs the holder, IGR, GRR and DI-1, DI-3, DI-5, DI-6 itself | DI-1 (BSP, HL, `hold-start`), **DI-3** (AK-1, the backstop `systemd-run`), DI-5 (AV-1), DI-6 |
| **RT-3** | **stop-post** (CL, trigger `stop-post`; CL-G, GP-R3) | PID 1, the holder unit's `ExecStopPost=` | `python3.12 -I -S …/rp11_h1.py deact ⟨id⟩ ⟨a2⟩ stop-post` | a static image performs CL and DI-1, DI-5, DI-6 | DI-1 (CL-2, CL-6), DI-5 (CL-4, GP-R3), DI-6 |
| **RT-4** | **backstop** (BS-1 … BS-4, and CL, trigger `backstop`) | PID 1, the service that the backstop timer starts (timer created by the holder at AK-1) | `python3.12 -I -S …/rp11_h1.py backstop ⟨id⟩ ⟨a2⟩` | a static image performs BS, CL and DI-1, **DI-4**, DI-5, DI-6 | DI-1 (BS-1), **DI-4** (BS-2, BS-3), DI-5, DI-6 |
| **RT-5** | **attest** (CL, trigger `attest`; its first act is CL-G) | the executor / operator, interactive, **`sudo -n`**; no unit | `sudo -n python3.12 -I -S …/rp11_h1.py deact ⟨id⟩ ⟨a2⟩ attest` | **BQ-2**: a static image after `sudo`, or another start path (R8 §9.6.1) | R8 §9.6.1 lists none for this row. **[O]** R8 §9.3 attributes DI-1 (CL-2, CL-6) and DI-5 (CL-4, "attestation") to CL, and §7.5a.1 names `attest` among the callers of the PK subject (DI-6) and of every `spawn()`; I take those three |

Sources: [A: R8 §9.1, §9.3 DI table, §9.6.1 role table, §7.5a.1 SN-I]; the RT-5 DI
reading is **[O]**.

**RT-1 … RT-4 and BQ-2** [A+N]. Each is started by PID 1, the manager, which is not a
procedure of the set (it is the trusted supervisor of every accepted unit guarantee,
[R2 §8], with RO-3 as its named outside-the-guarantee case [A: R8 §13.1]). The first
thing in the procedure's tree is the image the unit names. A static image there
satisfies LR-1 … LR-3 with nothing dynamic before it. **No BQ-2 exception arises for
RT-1 … RT-4.** [N] That is the sense in which the "LR-1 … LR-6 literally" direction is
fully attainable for four of the five procedures R8 names.

### 4.3 Sub-roles that are part of a row, not rows

[A: R8 §4, §5, §9.6.1] The holder (RT-2) contains ACT, HL, IGR and the
single-routine GRR; CL is performed by RT-3, RT-4 and RT-5 (each with its own trigger)
and by GP-R3 inside it; IGR/GRR and CL-G are not separate processes. The helper
children are not rows; they are BQ-4's subject (§9).

### 4.4 Table SU: root acts that `sudo` starts and that are not rows of §9.6.1

R8's role table lists `attest` (RT-5) and the installer class. R8 §9.3 (E-4) also
names **"AP-2's `sudo systemd-run`"** as a `sudo`-started path, and its DI table puts
DI-2 against AP-2. **The role table gives AP-2 no row** [O]. A fourth path is in the
accepted design and is named nowhere in R8 §9 [O]. The table records all of them so that
BQ-2 is answered for the complete set.

| ID | Act | Caller | Current first root image(s) | Controlled image today? | DI | In R8's role table? |
|---|---|---|---|---|---|---|
| **SA-1** | **AP-2**, creating the holder unit (the "holder literal") | the executor (privileged), `sudo -n` | `sudo`, then `/usr/bin/systemd-run --system …` (dynamic distribution client). It makes one transient service; its only effect is the holder unit | **none.** Neither `sudo` nor `systemd-run` is a design image | **DI-2** (`sudo -n systemd-run` by the executor) | **no** [O]; named only in §9.3 (E-4) and §9.3's DI table |
| **SA-2** | the **OS-6 interruption** of a hung pass: the executor, under A-2, issues the pinned root literal `sudo -n /usr/bin/systemctl stop rp11-capture-pass-a.service` | the executor, `sudo -n` | `sudo`, then `/usr/bin/systemctl stop …` (dynamic distribution client) | **none** | none in R8's DI table (it is not a delegation of a root helper; it is a root act of the executor) | **no, and not named in E-4** [O] |
| **IC-1 … IC-3** | the **installer class**: **H-1**, **RB-1**, **RS-1** | the executor, `sudo -n` | `sudo -n python3.12 -I -S -c ⟨verified-exec stub⟩ …`, under `sudo`'s environment, which is not closed | the stub is the design's own text but it is **Python**; the tool it executes is `rp11_h1.py`'s installer subcommands | none | yes [A: R8 §9.6.1 last-but-one row] |

Sources: SA-1 [A: D §4.2.5-R2 (e); R8 §9.3 E-4, DI-2]; SA-2 [A: D §4.2.5-R4 (e) and the
decided OS-6 / route (iii-a); R8 §12.1 lists OS-6 among the decisions it leaves
unchanged]; IC [A: D §4.2.4, §4.2.4-R1; R8 §13.1 HB-1].

**SA-2 is an omission in R8's enumeration of `sudo`-started paths** [O]. Whether R8
considered it and judged it outside "the root procedures that touch the grant and
activation mechanism", or missed it, I cannot tell from the text, and I do not say it
was missed. A pass is interrupted by a root `stop` of the capture unit, which is plainly
part of the activation mechanism's operation, and its first root program is a dynamic
`systemctl` after a dynamic `sudo`. I therefore include it, and Q-2 asks Codex to
confirm that the list is complete. A fixed-string search of the design for `sudo -n` found four distinct root literals:
the stub (installer and `attest`, as `python3.12 -I -S`), the AP-2 `systemd-run`, the
OS-6 `systemctl stop`, and `systemctl start` (Option C, not adopted). A search of R8 found
none that the design lacks. **Completeness of SU is nonetheless a review question, not
an established fact**: the search covers literals, not prose.

**What is deliberately not in either table** [A]: `sudo -n systemctl start --wait`
(Option C of the design, "not recommended" and not adopted); the operator's own
Polkit-authorized `systemctl start` of the capture unit, which is unprivileged
and is the *start* the one-shot grant is consumed against; and `H-1R` is discussed at §6.1: the design places it in the same tool as the installer,
R8 does not list it, and I treat it as sharing BQ-3's answer (Q-2).

---

## 5. BQ-2: for a procedure that `sudo` starts, where does it begin?

**The question, verbatim from R8 §9.3:** *"For a procedure that `sudo` starts, where
does 'the root procedure' begin: at the first image the procedure controls, or at
`sudo`? Treating `sudo`'s own loader as outside the procedure is an exception to LR-2
and needs to be stated as one."*

### 5.1 What actually runs, in order [A+O]

For RT-5 today:

1. the executor (unprivileged, Python, `ubuntu`) calls `sudo -n …`;
2. **`sudo`**: a dynamic root program (R8 §9.3 E-4 describes it as one). It runs in its
   own environment handling: the design states that `sudo` *"merges its PAM
   environment"* into what it starts [A: D §3.5, AS-12] and that the run is *"under
   `sudo`'s environment, which is not closed"* [A: D §4.2.4];
3. the program `sudo` executes: today the CPython interpreter (RT-5, IC), the
   dynamic `systemd-run` (SA-1) or the dynamic `systemctl` (SA-2); under LIT-FULL, a
   static image for RT-5.

R8 records **no accepted fact** about `sudo`'s linkage or about what its pre-`exec`
phase reads. The linkage of `systemd-run`, `pkcheck` and `sleep` is MF-9, optional and
uncollected [A: R8 §9.3]. I add none.

### 5.2 The two things BQ-2 mixes [N]

BQ-2 as R8 worded it assumes that each `sudo`-started path has *a first image the
procedure controls*. That is true only for RT-5, and only after WP-4 designs one. It is
**not true for SA-1, SA-2 or the installer**, where `sudo` executes a distribution
program or an interpreter. So BQ-2 contains two separable questions:

* **BQ-2a. Where does a `sudo`-started procedure begin?** (At `sudo` or at the image
  `sudo` executes.)
* **BQ-2b. Which `sudo`-started acts are root procedures that must have a controlled
  image?** (RT-5 certainly. SA-1 and SA-2 are the open cases. The installer is
  BQ-3.)

### 5.3 Option B2-S: the procedure begins at `sudo`

**Statement.** For a `sudo`-started path, the root procedure begins at the `sudo`
process. *p*'s process tree contains `sudo`.

| Criterion | Result for RT-5 / SA-1 / SA-2 | Basis |
|---|---|---|
| LR-1 | met provided no CPython remains (RT-5 static) | [A: R8 §9.2] |
| **LR-2** | **cannot be met.** `sudo` is a dynamic root program inside *p*'s tree, and the repository contains no design, build, citation or evidence that makes it, or a replacement for it, loader-free | [A: R8 §9.3 E-4]; [N] the inference |
| LR-3 … LR-6 | cannot be assessed for `sudo`, whose behaviour is no image of the design; they can be met for the image `sudo` starts | [N] |
| Exception needed | **none is available to cite**: B2-S is the *no-exception* reading, and it **fails** LR-2. It does not need an exception; it needs a different start path | [N] |

**Consequence.** B2-S is the strictest reading, and under it LIT-FULL **is not
attainable for any `sudo`-started path with the mechanisms the repository contains**.
A `sudo`-free route would be required for RT-5 (and for SA-1/SA-2 if they are in the
set). That route is B2-N (§5.5).

**What B2-S would also mean for the installer** [N]: BQ-3's inclusion would not help,
because the installer is `sudo`-started too. Under B2-S, "include the installer" cannot
satisfy LR-2 either.

### 5.4 Option B2-F: the procedure begins at the first image the design controls

**Statement.** For a `sudo`-started path, the root procedure begins at the image that
`sudo` executes, which the design controls. `sudo` is a launch preamble that is not part
of *p*, and that exclusion is stated as an exception to LR-2 (BC-4), bounded to `sudo`
and to its single `execve` of that image.

#### 5.4.1 RT-5 (`attest`) under B2-F

| Criterion | Result |
|---|---|
| LR-1 | met by a static image: no CPython |
| LR-2 | **met for *p* as defined**: every image *p* executes, children included, is static (BQ-4). **`sudo` is outside *p* by the stated exception** |
| LR-3 | met by the image itself: RH-1 (it ignores the environment it inherits from `sudo` and uses reviewed literals), RH-2 (descriptors 0, 1, 2 checked, every descriptor ≥ 3 closed before the first state operation), RH-3 [A: R8 §9.2]. This is the **function of the first image**, and it is why the image must be the first thing after `sudo` and not a Python program |
| LR-4 | met if DI-1, DI-5, DI-6 are in-process or by a cited loader-free interface (WP-3) |
| LR-5, LR-6 | unchanged by BQ-2; WP-4 … WP-6 |
| What stays outside | `sudo`'s own pre-`exec` execution, under the caller's environment |

The exposure that remains is confined to `sudo`: **the procedure's own code, its
children and its descriptors are all loader-free and closed**. [A: R8 §2.4] states the
accepted reasoning for ambient inputs: under OH-D-6 `ubuntu` already has unrestricted
`sudo`, so an ambient input that only root or a Polkit-authorized actor can set is a
*consistency* limit and not an escalation. [N] On a `sudo`-started path the ambient
input is set by the executor's own account, which the same decision already lets run any
command as root, so the reasoning applies at least as strongly. I record that as my
reading; **Codex should confirm it** (Q-4), because R8 stated the reasoning for inputs
settable by root or by a Polkit-authorized actor, not for inputs set by `ubuntu`.

#### 5.4.2 SA-1 (AP-2) and SA-2 (OS-6 stop) under B2-F: two sub-options

Under B2-F the "first image the design controls" is undefined for these acts, because
they run the distribution's client directly. There are two ways to complete the answer.

* **B2-F-A: bring SA-1 and SA-2 into the set with a static client image each** [N].
  AP-2's image performs DI-2 in-process: one `StartTransientUnit` call that carries the
  accepted AP-2 properties (service type `exec`, `Restart=no`, `OOMScoreAdjust`,
  `RuntimeMaxSec=`, `TimeoutStopSec=`, the `ExecStopPost=` command, the holder
  command). The OS-6 stop's image performs one stop of one named unit. Each is started
  by `sudo`, applies RH-1 … RH-3 and closes the environment, and the only dynamic root
  program left on any `sudo`-started path is `sudo`. **Cost** [N]: a new `start` and a
  new `stop` role (they could be one image with two fixed subcommands; that is
  WP-4's), additions to R8 §9.6.1 and to Appendix A (the AP-2 literal would name the
  image instead of `systemd-run`). **Mitigation of the cost** [A+N]: DI-3 (the holder's
  creation of the backstop service and timer, a `systemd-run`) is **already required
  in-process by LR-4** for RT-2, and DI-2 has the same shape (a transient-unit
  creation), so the marshalling and bus-protocol work that WP-3 must specify for DI-3
  also serves DI-2. SA-2 adds a stop call whose accepted semantics are cited
  server-side ([R2 §8]).
* **B2-F-B: leave SA-1 and SA-2 outside the set** [N]. `sudo` and the dynamic
  `systemd-run` / `systemctl` run as root before any controlled image, and the whole
  body of each act is dynamic. This is **a wider exception than B2-F's `sudo`
  preamble**: it excepts a dynamic program that does real work, not only the launcher.
  It also leaves **DI-2 without the in-process / loader-free treatment LR-4 requires**
  for the functions of the set.

#### 5.4.3 Consequence of B2-F, in summary

| | RT-5 | SA-1 | SA-2 |
|---|---|---|---|
| B2-F-A | static image; `sudo` excepted | static `start` image; `sudo` excepted | static `stop` image; `sudo` excepted |
| B2-F-B | static image; `sudo` excepted | `sudo` **and** `systemd-run` excepted; DI-2 left dynamic | `sudo` **and** `systemctl` excepted |
| Exception to cite | BC-4 (the `sudo` binary) | BC-4 (the `sudo` binary) | BC-4 (the `sudo` binary) |
| Exception to cite in addition | — | BC-4 widened to `systemd-run` (B2-F-B only) | BC-4 widened to `systemctl` (B2-F-B only) |

### 5.5 Option B2-N: another start path (no `sudo`)

[N] The only exception-free route to LR-2 for these acts is a privileged start that does
not run a dynamic program. **The accepted records contain no design, citation or
evaluation of one**, and I do not propose one. For completeness, what it would have to
establish, so that Peter can see what "exception-free" costs:

* a route by which the executor (`ubuntu`) causes a **root** static image to run, other
  than `sudo`. Every candidate is a new trust mechanism with its own citations
  (privilege elevation, environment and descriptor inheritance, authorization,
  auditability). None is cited in R2, R8 or the design;
* the same OH-D-6 consideration: `ubuntu` already has unrestricted `sudo`, so a new
  route does not reduce what `ubuntu` can do. Its benefit would be purely LR-2
  literalness, at the price of a new trusted mechanism that is not itself accepted;
* it is a **design work package**, outside WP-1 and not in R8's WP list. It might itself
  be a change that needs §0.2.

**B2-N is not recommended and not decision-ready.** It is stated so that "no
exception" is shown to depend on it.

### 5.6 BQ-2 across the five questions the prompt asks for each `sudo` path

| Path | Begin at `sudo` (B2-S) | Begin at the first controlled image (B2-F) |
|---|---|---|
| **attest** (RT-5) | LR-2 fails (`sudo` in tree); no repository-established remedy | LR-1 … LR-3 met by the static image; `sudo` excepted (BC-4); RH-1 … RH-3 done by the image |
| **AP-2** (SA-1) | LR-2 fails twice (`sudo` and the dynamic `systemd-run`); LR-4 fails for DI-2 | needs a controlled image first (B2-F-A, new role) — then as `attest`; without one (B2-F-B) the exception also covers `systemd-run`, and DI-2 stays dynamic |
| **OS-6 stop** (SA-2) | LR-2 fails twice (`sudo`, `systemctl`) | same as SA-1 |

---

## 6. BQ-3: is the installer class among the "root procedures that touch the activation mechanism"?

**The question, verbatim from R8 §9.3:** *"Is the installer class (H-1, RB-1, RS-1: the
`sudo -n python3.14 -I -S -c` verified-exec stub, HB-1) among the 'root procedures that
touch the … activation mechanism'? They install and remove the files the mechanism
consists of."*

### 6.1 What the class is and does [A]

* **Run**: `sudo -n /usr/bin/python3.12 -I -S -c '⟨verified-exec stub⟩' ⟨subcommand⟩ …`
  today (retarget to `python3.14` under HB-1) [D §4.2.4; R8 §9.6.2 A7].
* **The stub**: reads the tool file **once**, requires its SHA-256 to equal the value
  pinned in the H-1 assignment, and executes **those** bytes, so there is *no window
  between the check and the use* [D §4.2.4].
* **The stated limit**: the tool *"runs under `sudo`'s environment, which is not
  closed (AS-12). That is acceptable only because H-1 is not the capture entry. Its
  results are re-read unprivileged by H-2, and diagnostically by the entry."*
  [D §4.2.4]. R8 names this **HB-1** [R8 §13.1].
* **When**: ST-0 → ST-1 (H-1), and the separately authorized RB-1 [D §4.1.1 row for
  H-1 installation; D state tables; R8 §9.1 table]. These are **not** part of the grant
  window, the pass or the consume step [A: D §4.2.4, "H-1 is not the capture entry"].
* **What they touch**: they publish and remove the files the mechanism consists of:
  the launcher, the bootstrap, the unit, the staged rule, the H-1 record and
  directories [D state tables, ST-1].
* **One tool.** The design's OH-S4 row lists `rp11_h1.py` as one tool whose subcommands
  are *preflight, install, record, verify, rollback, `ACT`, `DEACT`, H-1R* [A: D, OH-S4
  row]. Under LIT-FULL the root roles (`consume`, `hold`, `stop-post`, `backstop`,
  `attest`) leave that file for static images (R8 §9.6.2 D2). **[O]** B3-OUT therefore
  leaves a Python `rp11_h1.py` that carries **installer-class subcommands only** and is no
  longer on any activation path; B3-IN would remove it.
* **H-1R.** The same row lists **H-1R**, "a re-record step (read-only plus record write,
  no file change)" under separate authority [A: D, package-drift row]. R8 does not name
  it in the installer class. **[O]** It runs by the same stub, and I treat it as a
  member for BQ-3 (it shares the answer), and ask Codex to confirm membership (Q-2).
* **Membership.** R8 names the class as "H-1, RB-1, RS-1". The design cites RS-1
  beside RB-1 and `DEACT` as consumers of the journal parser. Its definition is not
  re-derived here. **[O]** If the class is in scope, WP-2 must fix its membership.

### 6.2 Option B3-IN: the installer class is in the set

**Statement.** The installer class is among the root procedures; each of H-1, RB-1,
RS-1 must satisfy LR-1 … LR-6.

| Aspect | Consequence |
|---|---|
| LR-1 / LR-3 | the tool must not be CPython: a Python-free installer, **a new work package** [A: R8 §9.6.1 "a Python-free installer is then a new WP"] |
| LR-2 | the installer would be started by `sudo`, so **BQ-2 applies to it in full**. Inclusion does **not** remove the `sudo` exception under B2-F, and under B2-S it still fails LR-2. [N] |
| Size [N] | the installer carries the whole publication algorithm (PF, PT), the crash-consistent journal and its parser, recovery binding, `fsync` discipline, RB-1's removal and the SHA-256 and canonical-JSON handling [D §4.2.4-R1]. It is a larger, differently shaped image than any activation procedure |
| Verified-exec property [N] | the stub's *no window between check and use* is achieved by a Python program that reads once and executes those bytes. **A loader-free equivalent is designed nowhere in the accepted records.** A static installer run by `sudo` by path invites a window between the executor's check and `sudo`'s `execve`. WP-3 / WP-4 would have to design and cite a loader-free way to preserve that property, which is a new item in LR-5's mapping |
| HB-1 | closed for Python and the loader after the first image; the `sudo` preamble remains (§5.4) |
| WPs affected | WP-2 inventories the installer's operations; WP-3 may need interfaces beyond DI-1 … DI-6 (none; the installer has none today); WP-4 designs one more large image; WP-5 / WP-6 extend; WP-7's estimate grows by the largest single item |

### 6.3 Option B3-OUT: the installer class is outside the set

**Statement.** The installer class is not among the root procedures of the LIT-FULL
boundary. It is stated as an exception to LR-1 … LR-2 (BC-4), with HB-1 as the named
residual.

| Aspect | Consequence |
|---|---|
| LR-1 … LR-2 | not required of the installer; the exception is stated, **and it is the same kind of exception as B2-F's** (a root program outside the set that starts under `sudo`'s environment), widened to include CPython and its loader for the installer's own run |
| Text changes | R8 Appendix A-II-03 already provides the wording: `/usr/bin/python3.14` with the HB-1 sentence; Role A row A7 likewise [A: R8 §9.6.2 A7; Appendix A] |
| Detection controls that already bound the damage a faulty install can do [A] | the installed bytes are verified before they are used: **AP-0, H-2 and AM-0 detect a prior tamper** [R8 §13.1 RO-2 row, which says AP-0, H-2 and AM-0 detect a prior tamper; §7.3 row 9, which hashes helper images at AP-0, AM-0 and H-2]; H-2 is unprivileged [R8 §7.3 row 21]; the stub's digest pin protects the installer's own bytes against accident [D §4.2.4]; the grant is start-consumed and only the holder that AP-2 creates links a rule (AM-2) [D §4.2.5-R2] |
| What it does **not** claim [A+N] | that ST-1 is privilege-inert: OH-D-6 says it is *not* for `ubuntu`; that the installer cannot install wrong bytes (only that the activation refuses to use bytes that fail verification); that CPython's and the loader's file inputs are closed (MF-1, MF-2, MF-4 stay open for the entry; for the installer they are exactly HB-1) |
| LR-5 / LR-6 | unaffected; the installer's behaviour is unchanged |
| WPs | WP-2 … WP-7 omit the installer. The estimate (WP-7) excludes the largest single item |

### 6.4 How each reading sits against the textual boundary lists [A+O]

Neither list in R8 §9.1 names the installer. R3-ROOT's list is *"CP, the holder (ACT,
HL, IGR), the stop-post, the backstop, `attest`"* with the installer class explicitly
flagged as BQ-3. DR1 §5.3's list (*"the entry bootstrap, capture mechanism, CP, holder,
backstop and CL"*) does not name an installer either. **[O]** So B3-OUT is consistent
with the *text* of both lists; what R8 says is that **stating it as out is an
exception to LR-1 … LR-2 that must be written down** (§9.6.1, §12.2 BC-4). I follow
R8 and treat B3-OUT as an exception. Whether a determination that a procedure is not
in a named set is an *exception* or only a *scoping* is for Codex to confirm (Q-3).

---

## 7. Recommendations *(pending Peter's decision; [N])*

**Both are recommendations of this record. Neither is decided. Neither may be cited as
decided until Peter records it.**

### 7.1 BQ-2: recommended B2-F with B2-F-A

**Reasons** [N], each tied to the text above.

1. B2-S cannot be met by anything the repository contains (§5.3), so it is not a
   decision-ready answer for LIT-FULL; it is a different project (§5.5).
2. B2-F puts **everything the design writes, every child it forks and every descriptor
   it holds** inside loader-free, closed images, and confines the exception to one
   program (`sudo`) and one `execve`. It is the narrowest exception that exists.
3. B2-F-A removes the only **dynamic root programs that do real work** from any
   `sudo`-started path other than the installer (§5.4.2), and uses work (DI-3's
   interface) that LIT-FULL already requires. B2-F-B would leave DI-2 un-replaced
   though LR-4 requires the function to be in-process or by a cited loader-free
   interface.
4. B2-F-A makes the answer **uniform**: every `sudo`-started root path begins at a
   design image, so that Peter's exception has a single, small statement.

**Exact boundary sentence for Peter to approve or amend (BQ-2):**

> *For a root procedure that `sudo` starts (`attest`, the holder-creation act of AP-2
> and the OS-6 interruption), the procedure begins at the first image that the design
> controls and that `sudo` executes. Each such act has a design-controlled static first
> image that applies RH-1 through RH-3. `sudo`, and nothing else, is a launch
> preamble outside the procedure and outside LR-1 through LR-6, and that exclusion is
> recorded as an exception to LR-2 under BC-4 of the accepted R8 proposal. No other
> dynamic program is part of or beneath a `sudo`-started root procedure.*

### 7.2 BQ-3: recommended B3-OUT

**Reasons** [N]:

1. The installer runs **outside the grant window, the pass and the consume step**, and
   is not the capture entry [A: D §4.2.4], so no LR-3 closed-environment guarantee for
   the activation depends on it.
2. The activation does not trust what the installer writes: AP-0, AM-0 and H-2 verify
   the installed bytes before they are used (§6.3) [A].
3. Inclusion does **not** remove the `sudo` exception (§6.2). It would remove only the
   installer's own CPython and loader, at the price of the largest single image and an
   unspecified loader-free equivalent of the verified-exec property.
4. Peter can still revisit it: B3-IN remains available as a follow-on after WP-2 … WP-7,
   or if Codex finds that an installer fault can reach a grant. §10 shows that nothing
   WP-2 builds is lost if it later moves into the set.

**Exact boundary sentence for Peter to approve or amend (BQ-3):**

> *The installer class (H-1, RB-1 and RS-1, run as `sudo -n /usr/bin/python3.14 -I -S -c
> ⟨verified-exec stub⟩`) is not among the root procedures of the LIT-FULL boundary. It
> is recorded as an exception to LR-1 and LR-2 under BC-4 of the accepted R8 proposal,
> with HB-1 as its stated residual: it runs under `sudo`'s environment, outside the
> grant window, the pass and the consume step, and its results are re-verified before
> any use by AP-0, AM-0 and H-2.*

### 7.3 If Peter prefers the alternatives

| Choice | Sentence to approve instead |
|---|---|
| B2-F-B | *as §7.1, but `sudo` and the distribution's `systemd-run` and `systemctl` are launch preambles outside the procedure; AP-2 and the OS-6 interruption are not root procedures of the boundary.* **Wider exception; DI-2 stays dynamic.** |
| B2-S | *a root procedure that `sudo` starts begins at `sudo`.* **LR-2 cannot be met; a `sudo`-free start path must then be designed (B2-N) or LIT-FULL is not attainable for these paths.** |
| B3-IN | *the installer class is among the root procedures of the LIT-FULL boundary; each of H-1, RB-1 and RS-1 begins at its first design-controlled image and meets LR-1 through LR-6, with `sudo` excepted as in the BQ-2 sentence.* **Adds a Python-free installer work package; the verified-exec property needs a loader-free design.** |

---

## 8. Exceptions, baseline changes and follow-on redesign required by the recommendation

**The recommendation requires exceptions. They are reported here. None is approved,
none is treated as approved, and no later package may assume one.** [A: prompt item 6;
R8 §12.2]

| ID | What | Required by | Governing item | State |
|---|---|---|---|---|
| **EX-1** | exclude **`sudo`** (its dynamic loader and pre-`exec` execution) from the process tree of RT-5, SA-1 and SA-2 | B2-F (any sub-option) | R8 §12.2 **BC-4**: "except `sudo`-started procedures … from LR-1 … LR-2 (BQ-2)"; needs §0.2 steps 1 … 5 | **an LR-2 exception; not approved** |
| **EX-2** | exclude the **installer class** (CPython, the loader, `sudo`'s environment) from LR-1 … LR-2 | B3-OUT | **BC-4** ("or the installer class", BQ-3) | **an LR-1 and LR-2 exception; not approved** |
| EX-3 | exclude `systemd-run` and `systemctl` from the process tree of SA-1 and SA-2 | B2-F-B only | **BC-4** widened; also reopens LR-4 for DI-2 | not recommended; not approved |
| **BC-2** | whether treating the `ubuntu`-run entry as outside the set is a *narrowing* of DR1 §5.3 | BQ-1 as recorded | R8 §12.2 BC-2: *"treat R3-ROOT as a narrowing of DR1 §5.3 … Needed for LIT-FULL, if a maintainer reads it as a narrowing"* | **unresolved.** The G-1 record chooses "the R3-ROOT reading for investigation" and says it opens no §0.2 change; it does not say whether this reading is a narrowing. **I do not decide it.** Q-1 |
| BC-3 | except dynamic children from LR-2 (SCDC) | none | — | **not required, not requested**; BQ-4 forbids it |
| BC-1, BC-5 | CPython/glibc may remain (SSW, ACCEPT-X1); withdraw RP-11 | none | — | not required here |

**Whether EX-1 and EX-2 together exhaust the exceptions.** [N] Under the recommended
answers, LR-1 … LR-6 would hold **literally** for RT-1 … RT-5 and for the static
images of SA-1 and SA-2; the only exclusions are `sudo` and the installer class. If
Peter will approve neither, B2-F and B3-OUT fall away, and §0.1's last bullet applies:
no answer exists in the accepted records.

**Baseline changes and follow-on redesign that follow from the recommendation** [N]
(none performed, none authorized):

| Item | Change | Where it would be applied |
|---|---|---|
| FR-1 | add **two roles** (`start`, `stop`; one image or two), and amend the AP-2 and OS-6 literals to name them | R8 §9.6.1 role table; Appendix A rows A8 and the AP-2 / OS-6 literals (OH-S0d Part II); the design's §4.2.5-R2 (e) and §4.2.5-R4 (e) text |
| FR-2 | WP-3 to specify DI-2 and the stop call among the loader-free interfaces | WP-3 |
| FR-3 | R8 §9.3 (E-4) and §9.6.1 to be completed by the amendment: SA-2 named | OH-S0d / a dated addendum, as a documentation correction, **not edited here** |
| FR-4 | EX-1 / EX-2 to be recorded through §0.2 (change-log entry, impact assessment, PO recommendation and TL review, Acceptance Authority approval, a baseline version if the roadmap or release boundary changes) | change control, **not opened by this assignment** |
| FR-5 | A7 / A-II-03: `/usr/bin/python3.14` with the HB-1 sentence | OH-S0d / OH-S4 [A: R8 §9.6.2 A7; Appendix A] |

---

## 9. BQ-4: no dynamic-child exception, and what it constrains in WP-2 … WP-7

**Recorded** [A+N]: under the commissioned LIT-FULL direction, LR-2 admits **no**
dynamic child in any root procedure's process tree. The child set that R8 §9.3 lists
(DI-1 … DI-6: `systemctl`, `systemd-run`, `pkcheck`, `sleep`) cannot be kept as
children. A proposal to keep any of them is SCDC (R8 §9.4, BC-3) and **enters §0.2 change
control; it is not a decision of any WP**.

### 9.1 What BQ-4 does and does not decide

* It decides that **the process tree of RT-1 … RT-5 (and of SA-1 and SA-2 if they are
  in the set) contains only static images**, including every child, from the first
  image onward.
* It does **not** decide where a `sudo`-started tree begins (BQ-2) or whether the
  installer is in the set (BQ-3).
* It does **not** change HS-1 … HS-6, the SN, WB, RE and GD contracts, PK/2, or any
  accepted behaviour: R8 §7.5 says these hold *"under every Route 3 outcome that keeps
  any child process"* [A]. A child that is a forked static process still falls under
  them.

### 9.2 Constraints on WP-2 (inventory) [N]

1. Every **process creation** in the inventory must be classified as either (i) a fork
   that continues in a static image, or (ii) an `execve` of a **static** image the
   design controls. No row may be an `execve` of a distribution program.
2. The `spawn()` call sites of R8 §7.3 (rows 1 … 3g) become rows whose *creation* call
   is one of those two forms; the sends, validations and reap attempts of rows 3a … 3g
   are unaffected in kind.
3. Rows must be kept per **procedure and per sub-role** (§4.3), so that WP-3 and WP-4
   can attribute each call to one image.
4. WP-2 must not enumerate the installer's operations unless Peter's BQ-3 answer is B3-IN
   (§10).

### 9.3 Constraints on WP-3 (interface contract) [N]

* Each of DI-1 … DI-6 must be a **loader-free interface with version-bound citation**
  for `systemd 259.5-0ubuntu3.4` and `polkit 127-2ubuntu1.1` [A: R8 §9.5 WP-3], or
  in-process; **DI-5** must give decisions equal to `pkcheck`'s, and the exit-status
  contract R2 cites for it [R2 §6.4 (e)] is a command-line contract that does not carry
  over by itself [A: R8 §9.3 E-2].
* **DI-6**, the PK subject, is a child that today runs `/usr/bin/sleep 60` under
  `ubuntu`'s credentials. It cannot remain `sleep`. Whether the subject is a static
  fork, a static image or something else is **WP-4's decision**; WP-3 must not
  presuppose it.
* If SA-1 and SA-2 are in the set (B2-F-A), DI-2 and a stop call join the list.
* WP-3 is a **citation slice** with **no network research** authorized [A: R8 §9.5];
  that constraint is unchanged and not relaxed by BQ-4.

### 9.4 Constraints on WP-4 … WP-7 [N]

| WP | Constraint from BQ-4 |
|---|---|
| WP-4 | no image may `execve` a dynamic program. The system-call inventory must contain the process-creation, credential-change, signal-send and wait calls that replace `spawn()`; AD-8's restatement covers them [A: R8 §9.5 WP-4]. No design may rely on a dynamic helper "for convenience" |
| WP-5 | D9 / PO-17 per image **including every static image any root procedure `execve`s**, so the image count follows BQ-2 and BQ-3 |
| WP-6 | a behaviour that cannot be preserved without a dynamic child is **recorded as not preserved and returned to Peter** [A: R8 §9.5 WP-6: "every behaviour that cannot be preserved, restated"]. It is **never** silently covered by a child |
| WP-7 | the estimate states the count and size of images, which BQ-2 / BQ-3 fix; it states the delta of B3-IN as a separate line |

**A stop rule for any package** [N]: if a package finds that a function cannot be
performed without a dynamic child, it **stops and reports**. That is a candidate SCDC
(BC-3) and a §0.2 matter, not a WP result.

---

## 10. Inputs WP-2 may rely on, and only after Peter decides BQ-2 and BQ-3

WP-2 is **not authorized** by this record. If it is later separately prompted and
authorized, then:

### 10.1 Inputs that do not depend on BQ-2 or BQ-3

| Input | Status |
|---|---|
| BQ-1 = R3-ROOT; BQ-4 = no dynamic child | **recorded** by the commissioned direction (§2) |
| RT-1 … RT-4 and their DI map (§4.2) | accepted text [A] |
| LR-1 … LR-6, RH-1 … RH-3, DI-1 … DI-6 | accepted text [A: R8 §9.2, §9.3] |
| The §7.3 inventory, rows 1 … 22 (including the sends and validation of rows 3a … 3g), as the starting table | accepted text [A: R8 §7.3, §9.5 WP-2] |
| HS-1 … HS-6, SN, WB, RE, GD, PK/2, SG, LD, BS, SD | accepted text [A: R8 §7] |

### 10.2 Inputs that WP-2 may rely on only after Peter decides

| Input | Depends on | If B2-F-A | If B2-F-B | If B2-S | If B3-OUT | If B3-IN |
|---|---|---|---|---|---|---|
| WP-2 covers RT-5 (`attest`) from its first image | BQ-2 | yes | yes | **no: redesign first** | — | — |
| WP-2 covers the `start` act (SA-1) | BQ-2 | yes | **no** | **no** | — | — |
| WP-2 covers the `stop` act (SA-2) | BQ-2 | yes | **no** | **no** | — | — |
| `sudo` is outside every inventoried tree | BQ-2 | yes | yes (and the clients) | **no** | — | — |
| WP-2 covers installer operations (PF, PT, journals, RB-1, RS-1) | BQ-3 | — | — | — | **no** | yes |
| the exceptions EX-1 / EX-2 exist | BQ-2 / BQ-3 and a §0.2 decision | recorded as **proposed**, not approved | | | | |

### 10.3 Inputs WP-2 may **not** rely on, whatever Peter decides

* the §7 sentences, or any other text of this record, **as accepted**: they are
  proposals until Peter records them;
* any host fact: `sudo`'s configuration or linkage, the linkage of `systemd-run`,
  `systemctl`, `pkcheck` or `sleep` (MF-9 is uncollected), MF-1 … MF-8;
* any citation not already in the accepted R2 record;
* a view that EX-1 or EX-2 is approved before §0.2 closes it.

---

## 11. WP-1 acceptance checklist

For independent Codex review and Peter's recorded decisions. Unticked: nothing here is
accepted.

- [ ] **C-1** Every procedure implicated by R8 §9.1 is in §4 with accepted name, caller,
  current first root image, controlled first image and DI-1 … DI-6 delegation (RT-1 …
  RT-5, SA-1, SA-2, IC-1 … IC-3).
- [ ] **C-2** The R3-ROOT entry boundary is stated separately (§3) and the `ubuntu`-run
  entry cannot be mistaken for a root procedure.
- [ ] **C-3** BQ-2 is analysed for `attest`, AP-2 and the OS-6 stop (§5), at `sudo` and
  at the first controlled image, with consequences for LR-1 … LR-6.
- [ ] **C-4** BQ-3 is analysed for H-1, RB-1 and RS-1 (§6), including the verified-exec
  stub and the installer/removal actions, with and without the class.
- [ ] **C-5** A technically reasoned recommendation for BQ-2 and BQ-3 with an exact
  approvable boundary sentence each (§7), **marked pending Peter's decision**.
- [ ] **C-6** Every exception, baseline change and follow-on redesign the
  recommendation needs is listed (§8); **no exception is treated as approved**.
- [ ] **C-7** BQ-4 is recorded as no dynamic-child exception and its constraints on
  WP-2 … WP-7 are stated (§9); no SCDC or other exception is introduced.
- [ ] **C-8** The inputs WP-2 may rely on, and those it may not, are separated by
  Peter's decisions (§10).
- [ ] **C-9** Statements are tagged [A] / [O] / [N] (§1.2) and no host fact, external
  citation or invented source appears.
- [ ] **C-10** WP-2's inventory is **not** performed; only R8's DI map is used (§4.1).
- [ ] **C-11** R8, the R2 citation record, the design, the decision register and change
  log, and all historical snapshots are unedited.
- [ ] **C-12** Only the four current-state pointers were updated, preserving their
  restrictions and archive links, and say that WP-1 returned and awaits independent
  Codex review and Peter's BQ-2 / BQ-3 decisions.
- [ ] **C-13** The handback lists files changed, checks, unresolved questions and the
  statement that no prohibited operation occurred.
- [ ] **C-14** Review has judged the three open classification questions of §12.

---

## 12. Open questions for review

| ID | Question | Why it matters |
|---|---|---|
| **Q-1** | Is treating the `ubuntu`-run entry as outside the set a *narrowing* of DR1 §5.3 (R8 BC-2) that needs §0.2 even for LIT-FULL? The G-1 record does not say | if yes, a BC-2 change entry precedes any WP-9 choice of LIT-FULL |
| **Q-2** | Is SU complete? SA-2 is not named in R8 §9.3 (E-4). Is `H-1R` (same tool, same stub) part of the installer class? Did R8 consider and exclude SA-2? | BQ-2 must be answered for every `sudo` path |
| **Q-3** | Is B3-OUT an *exception* (as R8 §9.6.1 and BC-4 word it) or only a determination of set membership? | decides whether B3-OUT needs §0.2 or only a recorded scope |
| **Q-4** | Does the OH-D-6 consistency reasoning [R8 §2.4] apply to inputs that `ubuntu` itself sets on a `sudo`-started path? | EX-1's residual statement depends on it |
| **Q-5** | Is B2-F-A's addition of `start` / `stop` roles an in-scope consequence of LR-4 (DI-2) or a design addition that needs Peter's separate approval? | FR-1 |
| **Q-6** | Should Peter decide BQ-2a and BQ-2b separately (§5.2)? | the recommended sentence combines them |

---

## 13. What this proposal does not establish

It establishes no host fact. It does not show that `sudo` cannot be controlled, that a
static image can be built, or that B2-N is impossible; it shows only that **no accepted
record designs, cites or evaluates any of them**. It does not discharge any obligation
(PO-12′, PO-19, PO-17, PO-SN), does not establish concrete Route 3, and does not touch
**the standing `HARD STOP: concrete Route 3 not established`**. It does not decide BQ-2
or BQ-3, create an exception, or authorize WP-2 or any later package.
