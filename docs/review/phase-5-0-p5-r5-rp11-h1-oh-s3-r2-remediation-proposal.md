# Proposal — OH-S3 R2: repaired activation design with enforced-deadline cleanup claims, and the Route 3 alternatives record

**Terminal state: `HARD STOP: concrete Route 3 not established`.**

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R2-20261007-02`

Date: 2026-10-07

Executor: Claude Code (Sonnet 5.5) on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Independent reviewer: Codex · Decision owner: Peter Duscha

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r2-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r2-remediation-claude-prompt.md),
**13180 bytes, SHA-256
`c79b320e1afdf737699db19283b552fb66982bbd136c9c1d5b588fe1aa52b5a2`**,
recomputed with `wc -c` and `sha256sum` before any edit and equal to the pin in
the [authority record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r2-remediation-authority.md).

Durable handback: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r2-remediation-handback.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r2-remediation-handback.md).

This document **supersedes the OH-S3 R1 proposal as the cumulative forward
candidate** and is self-contained. R1
([proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-r1-design-remediation-proposal.md),
[handback](phase-5-0-p5-r5-rp11-h1-oh-s3-r1-design-remediation-handback.md)) is
preserved **unchanged, unaccepted and historical**. Nothing here accepts R1.

Basis (all accepted, all inactive): the cumulative
[OH-S2 R2 citation record](phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md) and
its [acceptance](project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-acceptance.md);
the [one-host design amendment](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md)
through D3-R6 and its
[acceptance](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-acceptance.md);
the [H-0 completeness proposal (DR1)](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-proposal.md),
the [cumulative R3 H-0 completeness proposal](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-proposal.md)
and its [acceptance](project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r3-acceptance.md);
the [composed H-0 and U-9 acceptance](project-review-2026-10-06-p5-r5-rp11-h1-h0g-r1-acceptance-and-u9.md);
the [C11 launcher contract](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md)
and [D2 static launcher design](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md).

This document is a **proposal and an alternatives record only**: inactive,
unreviewed and unaccepted. It changes no accepted record, no source, test,
configuration, unit, rule or launcher byte. It authorizes no host access,
implementation, build, test, cleanup, activation, successor slice, commit or
push. Naming a successor, a work package or a decision in it authorizes nothing.

---

## 0. Outcome

### 0.1 In one page

Independent review returned R1 with two findings. This record closes both, and
it ends at the hard stop that R1's prompt and R2's prompt both define for the
case in which a concrete Route 3 cannot be established from repository evidence.

* **R2-F1 — R1's recommended RT3-A did not meet the authorized Route 3
  boundary.** Correct, and R1's text is not repaired in place. The accepted
  Route 3 means that the root procedures that touch the grant and activation
  mechanism **do not run through CPython or a dynamic loader** (§9.1). R1 instead
  re-scoped "Route 3" to "no environment-derived input", kept CPython and glibc in
  every root-helper path, left the file-based loader inputs to MF-1, MF-2 and
  MF-4, and asked Peter to confirm that new scope inside DEC-1. A static first
  image closes inherited environment and descriptors. It does not remove the
  interpreter, the dynamic loader or their file inputs from the path. RT3-A
  survives only as **`STATIC-SCRUB-WRAPPER` (SSW)**, a named **scope-change
  alternative that is not Route 3**, selectable only after an explicit baseline
  decision under implementation-plan §0.2 (§9.7). DEC-1 no longer carries a Route
  decision.
* **Literal Route 3 is not decision-ready.** The repository holds the accepted
  procedures that a Python-free root path would have to reimplement, but it holds
  no evidence for the loader-free interface by which a static root image would
  read unit state, create the transient units, query Polkit and create the
  authorization subject (five of the six functions the root helpers delegate to
  distribution binaries today), no proof method for a static image with
  that system-call inventory, and no settled boundary for the procedures that
  `sudo` starts. Defining those would invent facts (§9.3). §9.4 gives the exact
  bounded alternatives and §9.5 the exact work, in order, that would make literal
  Route 3 decision-ready. **That is the hard stop.**
* **R2-F2 — the claimed cleanup bounds contained unbounded local work.**
  Correct. The S grammar reserves a fixed 30-second margin. It bounds none of the
  filesystem inspection, hashing, process creation and reaping, journal writes
  and `fsync` that CL and IGR perform. R1's "CL < S by the S grammar" and "IGR acts
  within about ten seconds" are **withdrawn**, together with the accepted design's
  "CL-0 … CL-3, which are local operations bounded by S" (§7.7). The replacement
  is a discipline, not an arithmetic claim (§7):
  every wait the helpers perform on a child, a lock or a clock has a **monotonic
  deadline and a fail-closed consequence** (class E); every whole-procedure
  elapsed-time claim is made **only where PID 1 enforces it**, as a signal
  delivered at a stated offset, and no completion is promised (class M); a few
  loops are bounded by a count (class C); everything else is **expected to be
  quick and is not bounded** (class X). Each procedure's interruption at any
  point maps to a state and a next recovery owner (§7.9). Signal handlers are
  installed **before any state is created and only set a flag** (§7.8), so
  nothing depends on an interruptible Python `finally` block finishing within an
  unsupported time, and a second signal during IGR is idempotent. While doing
  this I found a probable defect in the accepted backstop literal: for a
  `Type=exec` service `TimeoutStartSec=` ends at `execve` (systemd's documented
  behaviour, **proposed for citation**, not yet cited), so **nothing would bound a
  backstop firing that has started**. The literal gains a PID-1-enforced
  `RuntimeMaxSec=` (§7.4, BS-RM).
* **The safety kernel is unchanged.** G1 … G5 never cited the lock, the hold loop,
  `ExecStopPost=`, the backstop, any polling bound or any elapsed time (§2), so
  neither finding touches them. PO-11 (d′) is retained exactly: **no Polkit
  reload-time bound is claimed, and every operational timeout fails closed**
  (§7.10).
* **Two design improvements follow from F2 and are offered, not imposed.** The
  grant-removal routine GRR is one tmpfs-only, lockless, no-spawn routine used by
  IGR, by CL's first act and by the backstop, and it precedes every `ext4` write
  (§5.7, GR-2). A root-only identity object `grant.id` inside K lets those
  rungs act without reading an `ubuntu`-owned `ext4` journal (§4.5, GI-1; DEC-3).
* **MF-1 … MF-8, PO-12′, PO-19, PO-17, OH-S4/OH-S4p, the rebuild chain and the
  successor order** are re-evaluated under the corrected boundary, per
  alternative (§§9.8 … 9.13, 10, 11). Root-owned dynamic inputs do **not** cease
  to be inputs because the threat model excludes an unprivileged writer: under
  every alternative that keeps CPython or the loader in the path they remain
  inputs that must be observed and bound (§9.9).
* **Peter's choices (§12) are split.** Six decisions on the activation design may
  be made only after a clean independent review. **Any change of the accepted
  Route 3 boundary is a separate matter under §0.2 change control and is not a
  decision this proposal's acceptance can make** (§12.2).

### 0.2 Returned findings, repair and location

| # | Returned item | Repair in this proposal | Section |
|---|---|---|---|
| R2-F1 | RT3-A does not satisfy the authorized Route 3 boundary; DEC-1 used to change scope | R1 preserved; RT3-A renamed SSW and described as a scope-change alternative; accepted Route 3 restored; literal Route 3 evidence assessed; hard stop; exact alternatives and work; no scope change inside DEC-1 | §9.1 … §9.7, §12.2 |
| R2-F1 (7) | re-evaluate Role A–H, PO-12′, PO-19, MF-1 … MF-8, OH-S4/OH-S4p, rebuild chain, PO-17, surface comparison, successor order | per-alternative tables | §9.6, §9.8 … §9.13, §10, §11 |
| R2-F1 (8) | root-owned dynamic inputs are still inputs | stated and applied | §9.9 |
| R2-F2 (1)–(3) | inventory every blocking operation; distinguish enforced from expected; no inference from a fixed margin | classes E, M, C, X; inventory; withdrawn claims | §7.2, §7.3, §7.7 |
| R2-F2 (4) | enforce a deadline with a fail-closed consequence, or withdraw the claim and state the termination and recovery path | both, per component | §7.3, §7.4, §7.6 |
| R2-F2 (5) | map every interruption point of CL to a state and a next owner | interruption maps for the holder, CP, IGR, CL and the backstop | §7.9 |
| R2-F2 (6), (7) | handler installation relative to AM-2; no reliance on an interruptible `finally`; a signal during IGR; re-entry | signal discipline SG-1 … SG-8; IGR latch; flag-only handlers | §7.8, §5.7 |
| R2-F2 (8) | correct every affected formula, table, invariant, test, Appendix A amendment, Appendix B obligation and recommended parameter | all corrected; sizing rules N1 … N4 are necessary conditions only | §7.6, §8, Appendices A, B, §12 |
| R2-F2 (9) | retain PO-11 (d′) | retained verbatim in substance | §7.10 |

The carried items of R1 (PO-20 (f), PO-21 (c), PO-21 (s), PO-11 (d), PO-12′,
PO-19, PO-17, MF-1 … MF-8) keep their accepted R2 verdicts and are located in
Appendix C.

### 0.3 What this proposal does not do

It does not claim any citation, fact or acceptance. Every new host-behaviour
statement is a **proposed proof obligation** (§1.3), version-bound and paired
with the fact that fixes its version. It does not implement, rebuild, install,
test or observe anything. It does not edit the operational draft, the accepted
design, the C11 or D2 records, the R2 record, source code, tests, service files,
the decision register or the change log. It does not select a third-party
artifact and performed no network research. It does not change the accepted
Route 3 boundary, and it makes no scope decision.

### 0.4 Terminal-state check

The R1 prompt and the R2 prompt both define one conditional hard stop:
*if repository evidence is insufficient to choose a safe concrete Route 3, return
a decision-ready set of exact alternatives and a `HARD STOP` rather than inventing
facts.* The R2 prompt names it `HARD STOP: concrete Route 3 not established`. The
prompt identity matched, so the identity hard stop did not arise. The conditional
hard stop **does** arise, for the reasons of §9.3: the repository evidence that
would define a Python-free, loader-free root path is absent in four named places
(interface contract, static proof method, boundary for sudo-started procedures,
and size). The repaired activation design (§§2 … 8) is complete and
decision-ready on its own terms, **except** that its helper-start contract RH
(§9.2) is discharged by whichever Route 3 outcome is eventually chosen. Nothing
here is labelled completion on the strength of a scope-change alternative.

---

## 1. Sources, method and fact classes

### 1.1 Repository documents read

**Read completely:** `.agents/AGENTS.md`; this assignment's prompt and authority;
the R1 prompt, the R1 authority, the complete R1 proposal and the complete R1
handback; the accepted OH-S2 R2 acceptance, the OH-S2 R2 handback, and the accepted
R3 H-0 completeness acceptance; `docs/review/Handover information`; the
`docs/project-management/status.md` pointer; the restriction banner of
`docs/operations/disposable-test-server.md`.

**Read by section:** `docs/implementation-plan.md` (the reading map; §0.1 … 0.5;
§14.1 … 14.3; §16 in full; §17 in full; §20 in full). The accepted R2 citation record
`phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md`: §0.1 … 0.2 (the verdict summary and
terminal dispositions), §6.3 … 6.4, §7, §8 (every limb), §10.4 … 10.5, §11.6,
§12.9, §14.3 … 14.4, §15.4 … 15.5, §16, and the section headings; fixed-string
searches elsewhere. DR1 `phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-proposal.md`
§5.3 … 5.5 (the definition of Route 3) and the accepted R3 proposal's §6.3 … 6.5. The
one-host design
`phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`: the trace
and trust table (§4.1.3), the `ACT`/`DEACT` order and D3-R2 (d) … (l) in full (steps,
literals, backstop, hold loop, CL, attestation, states, the death matrix and
"what remains"), D3-R5 (e) CQ-0 … CQ-7 and (i) the boundary matrix, and fixed
searches for the interpreter literal, `systemctl`, `pkcheck` and `systemd-run`. C11
and D2 by the lines the design and R1 cite (the interpreter literal occurrences), and
D2's header. The operational draft
`phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` by heading and by
fixed searches for elapsed-time language, `PIN.interpreter` and the §9.5.3 and C-15
anchors (**not edited**). The tracked, non-secret launcher sources only by the
line numbers of the Role A literals (`infra/rp11-launch/launch.c`,
`tools/phase_5_0_evidence/rp11_launch.py`, and the evidence-harness review manifest).

**Carried from R1 without re-reading the underlying source:** the line references
of the Role A inventory outside the files listed above (C11 and D2 lines, the design's
`:2481`, `:5242`, `:6979`, and the `launch.c` structure), and the launcher build
description of §9.7 and §9.11. The R1 proposal states them, and the lines that I
re-checked by fixed search agree with R1's. I did not re-verify the rest and state
them as R1's.

No host, retained-evidence path, secret-bearing path, credential, player datum
or network resource was touched. No recursive search was rooted at the repository,
a workspace root, home, `/opt`, `/var`, `/tmp` or `/`. Every search named its file,
or listed the documents of the one directory `docs/review/` by name.

### 1.2 Method

1. Re-derive, from the accepted text, **which claim rests on which mechanism**
   (§2). Repair only where a refuted premise is load-bearing.
2. For every elapsed-time statement, ask who enforces it. If the answer is "the
   arithmetic of a parameter", the statement is withdrawn (§7.7).
3. Where a repair needs a host fact R2 did not establish, write it as a new
   **proposed** obligation. Never as a fact.
4. Give every wait, retry and poll a **finite, fail-closed** bound whose expiry
   has a defined consequence, **and say what is being bounded**: the helper's
   waiting, not the work of the kernel or of a child.
5. For Route 3, apply the accepted definition literally. Compare scope-change
   alternatives against it, never as a substitute for it.

### 1.3 Fact classes used in this proposal

| Tag | Meaning |
|---|---|
| **[R2 §n]** | an accepted source or verdict in the accepted R2 record, section `n` |
| **[D §n]** | accepted inactive design text (one-host amendment through D3-R6), section `n` |
| **[R3 §n]**, **[DR1 §n]** | accepted R3 or DR1 text, section `n` |
| **[C11]**, **[D2]** | accepted launcher contract or static-launcher design |
| **[R1 §n]** | the unaccepted, unchanged R1 proposal, cited only to say what was withdrawn or renamed |
| **[N]** | **new, proposed**: a design statement or proof obligation introduced here. It is not a fact. It needs citation, test or observation under its own gate |
| **[P]** | a **parameter** whose value Peter chooses |
| **E, M, C, X** | deadline classes of §7.2 |

Identifiers introduced here (LD, GR, GRR, GI, RL, IGR, IL, RO, SD, BSP, SG, IM, RH,
LR, WP, BQ, BC, DEC, G-, N1 … N4) are **proposal-local** until accepted. They do not
reuse any accepted identifier except where a primed form (PO-20 (f′)) restates an
accepted one. Identifiers that R1 introduced and that survive keep their R1 name
and meaning unless §7.7 or §9 says otherwise. R1's `RT3-A` is renamed `SSW`;
R1's `RT3-B` is renamed `SCDC`; R1's `RT3-Z` is renamed `ACCEPT-X1` (§9.4).

---
## 2. The safety kernel: what the accepted claims rest on

The four items R2 refuted or left uncited are all in machinery that surrounds the grant boundary, and R2-F2 concerns the elapsed time of that machinery.
Before changing anything, this section re-reads the accepted proofs and records
exactly which mechanism each safety claim cites. That reading is the licence for
every repair below. **Codex is asked to confirm it** (§14, question 1).

### 2.1 Claims, and what each rests on

| Claim | Accepted source | Rests on | Does **not** rest on |
|---|---|---|---|
| **G1.** No live grant at any instant from the `execve` of `ExecStart=` onward | [D §4.2.5-R4 (i)] | CQ-3's removal of the A1-intact rule, journaled `removed` (SB-3's token); CQ-5's PK *not authorized*; `ExecStart=` runs only after every `ExecStartPre=` exits `0` [R2 §8 (o)]; polkit authorizes `StartUnit` once [R2 §8 (p)]; `ACT` links the rule once (AM-2) | the lock, HL, `ExecStopPost=`, the backstop, any polling bound, any elapsed time |
| **G2.** One start attempt per activation (contract OSA over 𝒜) | [D §4.2.5-R5 (f), R6 (e)] | SB-1 (the claim: `mkdirat` fails `EEXIST`); SB-2 (PID 1's inactive-entry record, τ); SB-3 (one removal token); attempts never overlap [R2 §8 (t)]; end states [R2 §8 (u)] | the lock, HL, `ExecStopPost=`, the backstop |
| **G3.** The grant is created once, only after A-2 and after the holder's baseline | [D §4.2.5-R2 (d), R5 (c)] | A-2's pins; AM-0 … AM-2 order; AP-0's absence conditions; one identifier and one unit name [R2 §8 (m)] | the lock |
| **G4.** No grant survives a kernel boot | [D §4.2.5-R2 (a) M-B] | the rule and `pass-a.json` live only on `/run` (tmpfs, cleared at every boot, [R2 §7 (g)]) | everything else |
| **G5.** A failed start is never recorded as a pass | [D §4.2.5-R5 (f) proof of 4] | a pass is claimed only from a consume journal with `consumed` plus a capture root | everything else |

I re-read §4.2.5-R4 (i) items 1 … 7, §4.2.5-R5 (f) Lemmas 1 … 3 and the proofs of
OSA 1 … 4, and §4.2.5-R6 (c) … (e). **No step in any of them cites lock
exclusivity, HL's timing, the stop-post trigger, the backstop, a Polkit
latency or any elapsed time.** The only items that cite the lock are OS-5 and CX-1, both of which
the accepted text itself classes as **lifetime**, not grant, properties
([D §4.2.5-R5 (k)]: "a lifetime defect, not a grant defect").

### 2.2 Machinery that is hygiene or liveness

| Device | What it buys | What its failure costs |
|---|---|---|
| the activation lock (`flock`) | ordering of lifetime decisions (OS-5); clean, non-interleaved evidence | a refused start, a delayed HL end, a degraded (unordered) cleanup record |
| the hold loop HL and the lease L | bounds the activation's lifetime, by PID 1's `RuntimeMaxSec=` (class M, §7.2); ends it after a failed start or a pass | an activation that lasts until L, then ends by `RuntimeMaxSec=` |
| `ExecStopPost=` and the backstop | remove `pass-a.json`, tree directories and a *pre-pass* rule, and write the records | a pre-pass rule that stays live but **inert** (§5.4) until another rung acts or the host boots or the host boots |
| Polkit waits (PK) | evidence that the grant is absent, and the positive control that makes that evidence meaningful | a refused start or a failed `ACT` (fail closed) |

### 2.3 Consequence

Every repair in §§4 … 7 is allowed to **fail closed to "no pass"**. None may
weaken G1 … G5, and none may add an elapsed-time claim whose enforcer is not
named (§7). Where a repair adds a step to a safety path (BSP at the
baseline, PK/2 in CQ-5) it only **narrows** what can succeed. The safety kernel's
procedures (CQ-0 … CQ-7, SB-1 … SB-3, the claim, the rule and unit bytes) are
unchanged except for the textual amendments of Appendix A, each of which is a
fail-closed refinement.

### 2.4 What the safety kernel does depend on: the executable boundary

G1 … G5 are claims about procedures **as designed**. That the procedures execute
as designed, as root processes, depends on what starts them and what they inherit.
The accepted design assumed that `python -I -S` started under PID 1's open block is
such a start. [R2 §10.4, §15.4 (X-1)] refuted that for CPython 3.14.4, and the
accepted disposition returns the question to **Route 3 design review** (§9). The
helper-start contract RH-1 … RH-3 (§9.2) states what any chosen boundary must
deliver. Until Route 3 is established, **X-1 stays open for the root roles**, and G1 … G5
are conditional on RH. This is not new: it is the accepted disposition, restated so
that no reader takes the repaired activation design to have closed it. Under
OH-D-6, `ubuntu` already has unrestricted `sudo`, so an ambient input that only root
or a Polkit-authorized actor can set is a consistency limit and not a privilege
escalation. That reasoning makes RH a *consistency* requirement. It does not make a
dynamic input stop being an input (§9.9).

---

## 3. Vocabulary used by the repairs

| Term | Meaning |
|---|---|
| **grant object** | the rule file `/run/polkit-1/rules.d/50-freedom-blades-rp11.rules` together with polkitd's loaded copy of it |
| **G0 … G4** | grant-object states. **G0** never linked, or cleared by a boot. **G1** linked: the file is present and A1-intact. **G2** unlinked, unconfirmed: the file is absent, but polkitd's loaded copy may still authorize until it reloads. This proposal claims **nothing** about how long that lasts. **G3** verified absent: the file is absent and a PK/2 *not authorized* was observed after the unlink in this activation. **G4** unremovable: the file is present and `unlinkat` fails |
| **holder (H)** | the PID-1-supervised transient service whose main process runs the `hold` role (AP-2) |
| **CP** | the capture unit's `ExecStartPre=+` consume step (CQ-0 … CQ-7) |
| **CL** | cleanup, in every trigger (`stop-post`, `backstop`, `attest`), including GP-R3 |
| **GRR** | the **grant-release routine** (§5.7): one tmpfs-only, lockless, spawn-free routine that removes an A1-intact rule through a descriptor re-verification. Used by IGR, by CL's first act (CL-G) and nowhere else. CP's CQ-3 keeps its accepted order and write-ahead form |
| **IGR** | *inline grant release*: the holder's own call of GRR on every catchable end (§5.7) |
| **K** | the root-only lock directory `/run/freedom-blades-rp11-lock-⟨activation_id⟩/` (LD-1) |
| **GI-1, `grant.id`** | the root-only identity object inside K that lets a rung find the rule's identity without reading an `ubuntu`-owned `ext4` journal (§4.5, DEC-3) |
| **BS** | the backstop procedure and its timer |
| **executor (X), operator (O)** | the actor working under A-2 on `oracle-test`; the `ubuntu` client that issues the one `start` |
| **spawn** | creation of any child process by a root helper, always through the single function `spawn()` (§7.5) |
| **owner (of a lock)** | the single process that opened the open file description the lock is attached to |
| **lock mode** | `held`, `degraded` (acquisition deadline reached, cleanup proceeded unordered) or `absent` (the lock object could not be opened) |
| **𝒜** | the authorized path set of [D §4.2.5-R6 (d)], unchanged |
| **deadline classes** | **E** a monotonic deadline enforced by the helper on its own waiting; **M** a timer enforced by PID 1 that delivers signals at stated offsets; **C** a count bound; **X** expected to be quick, not bounded (§7.2) |
| **abandon** | stop waiting for a child after its kill and a grace period, without having reaped it, and record that fact. The consequence of every abandon is a fail-closed result |
| **flag** | the single boolean `stop_requested` that the holder's signal handlers set and nothing else (SG-2) |
| **RH-1 … RH-3** | the helper-start contract any Route 3 outcome must discharge for each root procedure (§9.2) |
| **R3-ROOT, R3-DR1** | the two readings of the accepted Route 3 boundary (§9.1) |
| **LIT-FULL, LIT-DR1, WITHDRAW, SSW, SCDC, ACCEPT-X1** | the exact alternatives of §9.4 |

---
## 4. Repair A — PO-20 (f): lock release and descriptor ownership *(carried from R1, with R2-F2 corrections)*

### 4.1 What the accepted text says and what is true

The accepted text relies on process end as the release event in three places:

* [D §4.4.2a] PO-20 (f): *"`flock` on an `O_RDONLY` directory descriptor gives an
  exclusive advisory lock that is released when the process ends."*
* [D §4.2.5-R3 (e)]: *"The kernel releases the lock when a process dies
  (PO-20 (f)), so a killed GP-R3 attempt never blocks the next one."*
* [D §4.2.5-R4 (c)] and [D §4.2.5-R5 (g)]: *"The lock is released by the kernel at
  every exit, including a kill"* and *"…at every process exit, including a
  kill."*

**What is true** [R2 §7 (f)]: the lock is available on any descriptor with
`FMODE_READ` or `FMODE_WRITE`, directories included. It is released when the
**last reference to the open file description** is dropped (`__fput` →
`locks_remove_file`). A forked child, or any holder of a duplicate, keeps it
after the locking process ends. R2's corrected form: *"released when the last
descriptor referring to that open file description is closed, which process exit
does when no other process holds one."*

### 4.2 Lock inventory

| # | Lock | Acquirer(s) | Object | Mode | Spawns while held? | Release in the accepted text |
|---|---|---|---|---|---|---|
| L-1 | H-1 run lock (M-0) | the root tool [D §4.2.4-R1 (b)] | `/var/tmp/⟨RUN⟩-h1-evidence/` (`ubuntu`, `0700`) | `LOCK_EX\|LOCK_NB`, whole lifetime | yes | process end |
| L-2 | `ACT` chain lock, taken by the holder at AM-0 | holder | `/var/tmp/⟨activation_id⟩-act-evidence/` (`ubuntu`, `0700`) | `LOCK_EX`; kept to `hold-start` (AR-2) | yes: AK-1's `systemd-run`, baseline `systemctl show` | explicit at `hold-start`, otherwise process end |
| L-3 | CP's lock (CQ-1) | CP | the same directory | `LOCK_EX\|LOCK_NB` once | yes: CQ-4's `systemctl show`, CQ-5's PK subject and `pkcheck` | CQ-7, otherwise process end |
| L-4 | HL's decision lock (OS-5) | holder | the same directory | `LOCK_EX\|LOCK_NB` once per decision | yes: the re-observation | the holder **exits while holding it** |
| L-5 | CL's lock (CL-0) | `stop-post`, `backstop`, `attest`, GP-R3 | the same directory | retry `LOCK_NB` every second for at most S seconds | yes: PK, `systemctl show` | process end |

### 4.3 Defects

* **D-LK-1, inheritance is not specified.** Every holder in the table spawns
  children while it holds. A child created by `fork` holds a duplicate of every
  inherited descriptor from creation until it `exec`s a `CLOEXEC` descriptor
  away, closes it, or exits. PK's subject process is the accepted example
  ([D §4.2.5-R1 (f)]): it is forked, changes credentials and then executes
  `sleep 60`. If the owner is killed while such a child is stopped, slow or
  failing to `exec`, the lock outlives the owner. The accepted text never says
  how descriptors are kept out of children.
* **D-LK-2, the lock object is not root-only.** `ubuntu` owns the evidence
  directory (`0700`). It can open it and take `flock` for as long as it likes.
  Then CP gets `consume-busy`, HL never ends, and CL stops with `lock-timeout`
  and "acts on nothing" ([D §4.2.5-R2 (h) CL-0]), so a pre-pass rule can stay
  live until L or the boot. Under OH-D-6 `ubuntu` can do more than that on
  purpose. But the same reachability exists *by accident*, for example any
  `ubuntu` tool that opens the directory and locks it, and the design's claim is
  that cleanup does not wait for anybody.
* **D-LK-3, the wait equals the stop timeout.** CL waits up to S seconds for the
  lock, and S is the holder's `TimeoutStopSec=`, which bounds CL itself
  ([R2 §8 (e)]). At S systemd sends `SIGTERM` to CL. CL is terminated at the
  instant its own wait would expire and never reaches `lock-timeout`.
* **D-LK-4, exit while holding.** OS-5 has HL exit "while holding the lock", so
  the design's release event is process end, which is the refuted premise. It
  buys nothing: `hold-end` is durable before exit and CQ-4 refuses on it.
* **D-LK-5, `lock-timeout` is the opposite of grant priority.** "Acts on
  nothing" leaves a removable rule in place because of a contended
  *coordination* object.

### 4.4 The corrected obligation, PO-20 (f′) *(proposed [N], text for [D §4.4.2a])*

For the HF-04 kernel series and the HF-07 `libc6` and CPython versions:

* **(f′-1)** [R2 §7 (f), established] a `flock` lock on a directory descriptor
  is attached to the open file description and is released when the last
  reference to that description is closed.
* **(f′-2)** *[N]* a descriptor opened with `O_CLOEXEC` is closed in the new
  image by `execve` and so is not inherited across it; `close_range(3, ~0, 0)`
  closes every descriptor from 3 upward ([D2 §5.7 S-4]).
* **(f′-3)** *[N]* a child created by `fork`, `vfork`, `clone` without
  `CLONE_FILES`, `posix_spawn` or CPython's `subprocess` holds a duplicate
  reference to every inherited open file description from creation until it
  closes the descriptor, `exec`s it away (`CLOEXEC`) or exits. With
  `close_fds=True` and no `pass_fds`, CPython's child closes all descriptors
  ≥ 3 before `exec`.
* **(f′-4)** *[N]* the only ways a second process obtains a reference to an
  existing open file description are inheritance, descriptor passing over a Unix
  socket, and `pidfd_getfd`. Re-opening `/proc/⟨pid⟩/fd/⟨n⟩` creates a **new**
  description and shares no lock.
* **(f′-5)** *[N]* an unprivileged process cannot open an object that is a
  directory owned by root with mode `0700`, and so cannot lock it.

(f′-1) is established. (f′-2) … (f′-5) are kernel and CPython behaviours that no
accepted record cites. They join the OH-S2 citation step (§11, slice OH-S2b).
**AP-0 is INVALID RUN unless each is accepted for the observed versions, and no
lock object is created.** The statement "released when the process ends" is
withdrawn everywhere; wherever the accepted text depends on it, LD-8 below says
what happens instead.

### 4.5 Design: lock discipline LD-1 … LD-9 *(proposed)*

* **LD-1, root-only lock object K.** The `ACT` chain lock object is the
  directory `K = /run/freedom-blades-rp11-lock-⟨activation_id⟩/`, `root:root`,
  mode `0700`, empty at creation (it receives only `grant.id`, GI-1), with no `system.posix_acl_*` or capability extended
  attribute. The holder creates it at AM-0 with an exclusive `mkdirat` on a
  descriptor of `/run` (which never follows a final symbolic link and fails
  `EEXIST` for any existing name [R2 §7 (h)]), opens it, verifies type, owner,
  mode and `st_nlink`, and journals its `(dev, ino)` in `run-start`. AP-0
  requires K absent. K lies under `/run`, whose parent conditions already require
  a root-owned tmpfs directory without group or other write. K is cleared by
  every kernel boot (M-B). CL-5b removes `grant.id` and then K, through a descriptor re-verification
  against the journaled identity and only if K holds nothing else, together with the other
  `/run` objects; a K left by a crash between its creation and the journal is
  class **S0** (reported, kept, cleared at the boot), exactly like the other
  run-unique `/run` leftovers of [D §4.2.5-R2 (h) CL-5b]. Nobody but root can open
  K, so no unprivileged process can hold the lock (f′-5).
* **GI-1, the grant identity object (proposed [N]; DEC-3).** Immediately before
  the rule is linked (AM-2's PF-6), and after the staged rule's identity is known,
  the holder creates `K/grant.id` (`root:root`, `0600`, `O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC`,
  then `fchmod`) holding one canonical line: `{path, dev, ino, sha256, size, mode,
  uid, gid, boot_id}` of the staged rule that PF-6 will link. K lies on tmpfs, so
  writing it involves no `ext4`. A rung that must remove the rule (IGR, CL-G, the
  backstop, `attest`) reads its identity from `grant.id`, **not** from the
  `ubuntu`-owned evidence directory's journal. The journal's `file-identity` line
  stays the durable evidence, and a disagreement between the two is recorded as
  `identity-conflict` and acted on by `grant.id`, because removing the name whose
  identity the holder itself wrote is never wrong. This closes two things R1
  flagged and could not close: a replaced `ubuntu`-owned journal can no longer
  make CL class the rule A0 and leave it; and the removal path no longer reads
  `ext4` before the `unlinkat` (GR-2, §5.7). **Without GI-1** (the alternative of
  DEC-3) CL reads the journal as accepted and RO-6 (§5.6) widens. CP's CQ-3 is
  **not** changed: it keeps the accepted order, after the claim and under the
  lock, and the accepted journal-based classification.
* **LD-2, one owner per open file description.** A lock is taken only on a
  descriptor that the acquiring process itself opened for that purpose:
  `open(K, O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC)`. It is never duplicated
  (`dup*`, `fcntl(F_DUPFD*)`), never passed over a socket, never handed to
  another thread, and never stored in an object that outlives the acquisition.
  One acquisition is one description and one owner.
* **LD-3, inheritance prevention.** (a) Every `open` carries `O_CLOEXEC`
  explicitly. The test asserts the flag and does not rely on a language default.
  (b) A process holds a lock only while it is single-threaded. (c) **No raw
  `fork` in any root helper.** Every child is created by one function
  `spawn()` (HS-1, §7.5), which uses only a creation primitive that closes every
  descriptor ≥ 3 before `exec` and passes none (`close_fds=True`,
  `pass_fds=()`). (d) The helper-start contract RH-2 (§9.2) requires every
  descriptor ≥ 3 to be closed before the helper's first state operation. Which
  mechanism discharges RH-2 depends on the Route 3 outcome (§9). **The discipline
  here does not rely on it**: (a) … (c) and (e) alone keep K's descriptor out of
  children, and K does not exist until after RH-2 is discharged (AM-0). (e) A child's duplicate reference therefore exists only between
  its creation and its own `exec` or `_exit`. This is the only window, and it is
  not widened by any step of the design (f′-3).
* **LD-4, explicit close points, and no process designed to end holding a
  lock.** A lock is closed as the first act after the last operation it
  protects (table 4.6). Process exit is the last-resort release and is **never**
  the design. OS-5's "exits while holding the lock" is replaced by: *HL appends
  and `fsync`s `hold-end`, closes K, then exits*. CQ-4 refuses on `hold-end`, so
  the earlier release leaves no gap.
* **LD-5, bounded acquisition.** Every acquisition is `LOCK_EX|LOCK_NB`. A wait
  is a loop of non-blocking attempts bounded by a **monotonic deadline**
  `lock_wait_ms` (λ) [P] (§7.6: range 1,000 … 10,000, recommended 5,000), never by
  a count of sleeps. The deadline bounds **this loop's waiting** (class E, §7.2).
  It is **not** a bound on CL's elapsed time: nothing in this document derives one
  from λ (§7.7). CP does not wait: one attempt, as accepted (AR-1). `EINTR`
  retries within the deadline. Any other error is "cannot acquire".
* **LD-6, grant removal never waits for the lock (GR-1).** CL-G (§5.7), IGR and
  GP-R3's rule step do not require the lock, and CL-G runs **before** CL's first
  lock attempt. If CL cannot acquire K within
  `lock_wait_ms`, or cannot open K, it continues in **degraded mode**: it
  records `lock_mode: "degraded"` or `"absent"` and performs CL-1 … CL-7 as it
  would holding the lock, except that it is not ordered against CP. This is safe
  because the rule's removal is one descriptor-re-verified `unlinkat` of one
  A1-intact object that CP's CQ-3 also performs (the later actor gets `ENOENT`),
  and because G1 and G2 do not depend on the lock (§2). `lock-timeout` as an
  outcome that acts on nothing is **withdrawn**.
* **LD-7, no lock on an object a non-root actor can open.** It applies to K and
  to any later lock that serializes an act of the activation chain. H-1's run
  lock (L-1) and any lock of the same M-0 pattern may stay on their
  `ubuntu`-owned evidence directories, because holding one can only stop *that
  run* before any mutation and nothing is cleaned up through it. They obey LD-2
  … LD-5, and each journal records its lock object and mode.
* **LD-8, failure behavior.** Table 4.7.
* **LD-9, the holder of a lock is never hunted.** No procedure scans for,
  signals, ptraces or kills a lock holder, and no decision reads `/proc/locks`.
  A retained lock is handled only by LD-8.

### 4.6 Close points

| Procedure | Opens K | Acquires | Closes K | Exit while holding? |
|---|---|---|---|---|
| holder AM-0 | after the exclusive `mkdirat` of K | `LOCK_EX\|LOCK_NB`. `EWOULDBLOCK` is impossible for a fresh K and is HARD STOP `lock-object` | immediately after `hold-start` is durable (AR-2, unchanged) | no. A failure before that point closes in `finally` |
| holder AK-1, baseline reads | — | — | — | children are created by `spawn()` while the lock is held (LD-3) |
| HL decision (OS-5) | per decision, derived from `activation_id` | `LOCK_EX\|LOCK_NB`, once | after `hold-end` is durable and before the exit, or immediately if no terminal reason holds | no (**amended**) |
| CP | CQ-1, derived from `pass-a.json`'s `activation_id` (CQ-0) | `LOCK_EX\|LOCK_NB`, once (AR-1) | after CQ-7's `run-end`; on every failure path before the non-zero exit | no |
| CL (`stop-post`, `backstop`, `attest`) | CL-0 | `LOCK_NB` attempts until the `lock_wait_ms` deadline, then degraded | after CL-7's `run-end` | no |
| IGR | none | none | — | — |

### 4.7 Failure behavior (LD-8)

| Condition | CP | HL | CL, BS, `attest` | holder AM-0 | Effect on the grant and on a pass |
|---|---|---|---|---|---|
| K absent, not a directory, wrong owner or mode, unopenable | `consume-unidentified`: nothing created, SB-2 covers | `observation-failed`: the activation ends | `lock_mode: "absent"`, degraded | HARD STOP `lock-object` before AM-1; nothing is linked | no pass; the rule is removed by IGR, CL-G or CQ-3 |
| `EWOULDBLOCK` | `consume-busy` (no pass) | observes again after Δ | retries to the deadline, then degraded | n/a | no pass; removal unaffected (GR-1) |
| other `flock` error | as "cannot acquire": `consume-busy` | as `EWOULDBLOCK` | as the deadline expiring | HARD STOP `lock-object` | as above |
| the lock is retained for a long time, by a root act or by a bug | CP never passes | waits until L, then the holder ends and IGR runs | degraded, every time | n/a | **no grant outlives the first rung of RL that can act** (§5); no start passes |
| the owner dies while a child holds a duplicate | as `EWOULDBLOCK` for everyone else | as above | as above | n/a | LD-3 admits this only inside the spawn window; no design path keeps it |

### 4.8 What the lock still protects, and what degraded mode costs

The lock still orders lifetime decisions (OS-5: after HL's durable `hold-end`
every CP refuses) and keeps cleanup records from interleaving with a running CP.
Degraded mode costs one thing: a CL record may not be ordered against a CP that
is mid-flight. Then the accepted outcome applies, a pass running without a grant
while CL ends HARD STOP `unit-still-active` ([D §4.2.5-R5 (k)], CX-1). The
`deact` record states `lock_mode`, so the reviewer sees the basis. Neither G1
nor G2 changes.

### 4.9 Evidence

`rp11-activation-record/2`, as amended in §8.5, gains `lock: {object: {path,
dev, ino} or "absent", mode: "held"|"degraded"|"absent", wait_ms}`. The consume and CL attempt
journals' `run-start` lines carry the same three values.

### 4.10 Negative tests *(proposed, for OH-S4; none run here)*

| ID | Case | Asserts |
|---|---|---|
| NT-LD-1 | a lock owner spawns each helper child (`systemctl`, `systemd-run`, `pkcheck`, the PK subject) while holding K | after `spawn()` returns and after each child's `exec`, **no child holds a descriptor on K's inode** (checked through the child's descriptor table in the harness) |
| NT-LD-2 | the owner is killed while a deliberately stopped fake child holds a duplicate | the second acquirer sees `EWOULDBLOCK` (the hazard exists in the model), and the same scenario cannot be produced through `spawn()` |
| NT-LD-3 | code scan over every root helper | no `os.fork`, no `os.dup*`, no `fcntl` `F_DUPFD*`, no `SCM_RIGHTS`, every `os.open` carries `O_CLOEXEC`, every lock acquisition has a matching `close` on every path including exceptions |
| NT-LD-4 | K's creation and mode | K is `root:root`, `0700`, empty at creation, no forbidden extended attribute; a non-root actor in the harness cannot open it |
| NT-LD-5 | `ubuntu`-style retention of the old `ubuntu`-owned directory lock | has **no effect** on CP, HL or CL once the lock object is K |
| NT-LD-6 | CL against a lock retained forever | CL-G removes an A1-intact rule **without having attempted the lock**; CL then reaches `lock_mode: "degraded"` when the λ deadline is reached, and continues. The test asserts the order (removal, then lock attempt) and that no elapsed-time statement is made about CL |
| NT-LD-7 | the sizing rules of §7.6 | AP-0 refuses any parameter set that violates N1 … N4, **and** a code and text scan asserts that no document, record or log line states the result as a bound on CL, CP or IGR |
| NT-LD-8 | HL's decision | `hold-end` is durable and K is closed before the process exits; a CP that acquires K in between refuses at CQ-4 |
| NT-LD-9 | PK subject | the subject child holds no lock descriptor, runs under the credentials in the H-1 record, and is killed after each call (reaped within the grace period, otherwise abandoned and recorded) |
| NT-LD-10 | GI-1 | `grant.id` exists, is `root:root` `0600` and equals the staged rule's identity **before** PF-6; with the `ubuntu`-owned journal replaced or unreadable, CL-G still removes the A1-intact rule; a disagreement between `grant.id` and the journal is `identity-conflict` and the rule is removed by `grant.id`; a `grant.id` that names an object that is not at the rule path removes nothing |

---

## 5. Repair B — PO-21 (c): `ExecStopPost=` is a rung, not a guarantee *(carried from R1, with R2-F2 corrections)*

### 5.1 What the accepted text says and what is true

[D §4.4.2b] PO-21 (c): *"`ExecStopPost=` runs … after the main process ends for
**every** cause."* [D §4.2.5-R2 (a)]: *"The service's `ExecStopPost=` runs
cleanup CL whenever its main process ends, for any cause."* [D §4.2.5-R2 (n)
item 3] and the (k) matrix's SP cells follow from it.

**What is true** [R2 §8 (c)]: for each listed cause the state machine enters
`STOP_POST` and *attempts* to spawn `ExecStopPost=`. **If spawning it fails, the
unit goes to `FINAL_SIGTERM` with result `resources` and `ExecStopPost=` never
runs.** PID 1 failure and power loss are outside any unit guarantee.

### 5.2 The authorized guarantee, restated *(proposed)*

* **G1 … G5 (§2.1) hold unconditionally within 𝒜.** None uses `ExecStopPost=`.
* **H1, a hygiene guarantee, conditional and untimed.** *After the holder's main
  process ends, the rule is unlinked by the first rung of the ladder RL (§5.3)
  that acts. No time to that rung is claimed.* R1 stated an "operational latency"
  per rung. That column is withdrawn (§7.7): the rungs are ordered, not timed.
* **Outside the guarantee (RO-1 … RO-6, §5.6).** Stated by name.

### 5.3 The recovery ladder RL-0 … RL-5

| Rung | Mechanism | Needs PID 1 to spawn something? | Covers | Terminated or limited by (class) |
|---|---|---|---|---|
| **RL-0** | **IGR**, the inline grant release in the holder (§5.7) | **no** | every *catchable* end of the holder's main process that the process reaches a flag check on | nothing: its local work is class X. PID 1's `SIGKILL` of the holder (class M, §7.4) ends the process whether or not IGR finished |
| **RL-1** | `ExecStopPost=` running CL with trigger `stop-post`; its **first act is CL-G** | yes | every end after which PID 1 can spawn it | `TimeoutStopSec=` S: `SIGTERM` at S, `SIGKILL` after a further S, then `failed` with result `timeout` [R2 §8 (e)] (class M) |
| **RL-2** | the backstop timer's service running CL (BS-4); its **first act is CL-G** | yes | a stop-post that could not be spawned, or a CL that was killed | `RuntimeMaxSec=` S_b on the service (BS-RM, §7.4, class M, **[N]**) and at most B firings (class C) |
| **RL-3** | **CP at any later start** (CQ-3 in grant-priority form), by anyone | yes (a start needs it) | the rule itself, whenever any start is attempted | the capture unit's start timeout T_s (class M) |
| **RL-4** | a kernel boot clears `/run` (M-B) | no | everything under `/run` | none: the next boot |
| **RL-5** | attestation, trigger `attest` (record only; **its first act is CL-G**, which finds nothing the boot did not already remove) | n/a | the *records* | none: interactive, under A-2 |

RL-0 and CL-G are new. RL-1, RL-2, RL-4 and RL-5 are the accepted `SP`, `BS`,
`BC` and attestation mechanisms. RL-3 is accepted behaviour (§5.4 uses it)
promoted to a named rung. **PID 1 being unable to spawn is exactly the case in
which RL-0 and RL-4 can still act and RL-1 … RL-3 may not.**

### 5.4 The inertness lemma IL

**IL.** Let X be an activation whose holder's `ActiveState` is not `active`, or
whose `ACT` journal has `hold-end`. A rule left live for X cannot produce a pass.

*Proof.* A pass is the execution of `ExecStart=` of the capture unit. PID 1
executes it only after every `ExecStartPre=` has exited `0` [R2 §8 (o)]. CP
exits `0` only at CQ-7. CQ-7 follows CQ-4, whose OS-4 requires the holder
`active` with the `ACT` journal's invocation and whose check requires no
`hold-end`. Both are false, so CP exits non-zero at CQ-4 after CQ-3 has removed
the rule if it could. If PID 1 cannot spawn CP, or CP's image cannot be
executed, no `ExecStartPre=` exits `0`, so `ExecStart=` is never executed
([R2 §8 (c)]: start-pre spawn failures end the start; [R2 §8 (o)]). ∎

**IL′ (the window is ended by PID 1, not by a helper).** The holder's
`RuntimeMaxSec=` L is a class-M timer on `CLOCK_MONOTONIC` that starts at the
holder's `ActiveEnterTimestampMonotonic` [R2 §8 (d)]. When it fires, PID 1 sends
`SIGTERM`, and the holder's `ActiveState` leaves `active`. **From that moment IL
applies, whatever any helper is doing, including a holder that is wedged in
local work.** Consequently the period in which a live rule could be consumed by a
pass ends no later than L after the holder became active, and this does not
depend on IGR, CL, the backstop or any helper timing. Two limits are stated, not
hidden: `CLOCK_MONOTONIC` does not count suspended time [R2 §8 (d)], and PID 1
must be able to act (RO-3).

IL says that a rule left live after the holder has gone is a *hygiene* matter.
It is still a Polkit grant of `start` for `ubuntu` (OH-D-6 says `ubuntu` already
has unrestricted `sudo`, so it adds no privilege). It cannot produce a pass, and
OH-D-7's "after the pass" is not engaged.

### 5.5 Terminal causes of the holder's main process

*Catchable* means a signal or an orderly end that the Python process can handle
(SG-1: the set H). "IGR" means RL-0 removed an A1-intact rule before the process
exited **if the process reached a flag check or the end of its body before it
was killed**. No cell promises that it did.

| # | Cause | Catchable? | RL-0 IGR | RL-1 stop-post | RL-2 backstop | RL-3 CP | RL-4 boot | Grant afterwards |
|---|---|---|---|---|---|---|---|---|
| 1 | HL's normal end (`exit 0`) | yes | attempts | runs | if 1 cannot spawn | at a start | — | G1 → G2, then G3 by CL |
| 2 | `observation-failed` (non-zero exit) | yes | attempts | runs | as 1 | as 1 | — | as 1 |
| 3 | unhandled exception, `SystemExit` | yes | attempts (`finally`) | runs | as 1 | as 1 | — | as 1 |
| 4 | `SIGTERM` from a stop job | yes | attempts at the next flag check | runs | as 1 | as 1 | — | as 1 |
| 5 | `RuntimeMaxSec=` expiry: `SIGTERM`, then `SIGKILL` after S [R2 §8 (d), (e)] | the first yes; the second no | attempts at `SIGTERM`; **no promise before the `SIGKILL`** | runs | as 1 | as 1 | — | as 1 |
| 6 | orderly shutdown, reboot or `kexec` (EO, outside 𝒜): stop, then boot | yes | attempts | runs (PO-21 (h)) | n/a | n/a | clears | G0 after the boot |
| 7 | `SIGINT`, `SIGHUP`, `SIGQUIT`, `SIGUSR1`, `SIGUSR2`, `SIGALRM` (the set H) | yes | attempts | runs | as 1 | as 1 | — | as 1 |
| 8 | `SIGKILL` (a root act, or the escalation after S) | **no** | — | runs if PID 1 can spawn it | if 8's stop-post cannot spawn | at a start | clears | G1 live **inert** (IL) until a rung acts |
| 9 | a fatal signal in the interpreter (`SIGSEGV`, `SIGABRT`, `SIGILL`, `SIGBUS`, `SIGFPE`) or any default-terminating signal not in H | **no** | — | as 8 | as 8 | as 8 | clears | as 8 |
| 10 | kernel OOM kill | excluded by `OOMScoreAdjust=-1000` [R2 §8 (f)] | — | — | — | — | — | not applicable |
| 11 | a kill by a user-space OOM daemon | **no** (not covered by (f)) | — | as 8 | as 8 | as 8 | clears | as 8 |
| 12 | the holder never started: the first image is missing or cannot be executed | n/a | n/a | n/a | n/a | n/a | — | **no grant was ever linked**: AM-2 is the holder's act |
| 13 | PID 1 cannot spawn `ExecStopPost=` (result `resources`) [R2 §8 (c)] | any | attempts if catchable | **does not run** | runs if PID 1 can spawn it | at a start | clears | catchable: G2 then G3 by RL-2; uncatchable: live inert, RO-1 |
| 14 | EU: power loss, panic, hard reset | no | — | — | — | — | clears | G0 after the boot; attestation records it |
| 15 | PID 1 is dead or hung | n/a | attempts if catchable | no | no | no | clears | outside any unit guarantee [R2 §8 (c)]; a live rule is inert (IL) because no start can run |
| 16 | **a second termination signal while IGR runs** | yes | the handler sets the flag again and **nothing else**; GRR is not interrupted and not restarted (SG-5) | runs | as 1 | as 1 | — | as the first signal's row |
| 17 | `SIGKILL` **during** IGR | **no** | stops at the point reached (§7.9, IM-I) | as 8 | as 8 | as 8 | clears | by IGR point: G1 inert before the `unlinkat`, G2 after it |
| 18 | uninterruptible stall of the holder (a blocked kernel or filesystem call): no signal is acted on until it returns | n/a | none until the stall ends | `SIGKILL` is delivered; whether the process leaves the kernel call is the kernel's, and unit state moves on after the second S [R2 §8 (e)] | as 8 | as 8 | clears | **RO-6**; IL holds while the holder is not `active` |

### 5.6 What remains outside the authorized guarantee

* **RO-1 (named).** *An uncatchable end of the holder (rows 8, 9, 11) while PID 1
  cannot spawn `ExecStopPost=` and cannot spawn the backstop's service, for as
  long as that lasts.* The rule then stays at G1 and **inert** (IL). It is
  removed by the first rung that can act: the backstop on its next firing, CP at
  any start, or the boot. No pass can run in that interval (G1, G2, IL). This is
  the one failure of RL that the authorized guarantee does not cover. It needs
  two independent faults (an uncatchable holder end and a PID 1 that cannot
  spawn) and its only effect is a *pre-pass, inert* grant of `start` for
  `ubuntu`.
* **RO-2 (common-cause).** *The helper bytes on disk are damaged or removed after
  `ACT`.* RL-1 and RL-2 then fail identically because they run the same
  installed image. RL-0 is **not** affected, since it runs inside a process that
  was already loaded. AP-0, H-2 and AM-0 verify those bytes before `ACT`, so
  after `ACT` the cause is a root act (SL-1).
* **RO-3 (PID 1).** If PID 1 is dead or hung, nothing in any unit runs. That is
  outside every unit-level guarantee in the accepted record.
* **RO-4 (IGR not completed; new in R2).** *The holder's end is catchable, but
  the process is killed (`SIGKILL` after S, or a root act) or stalls before GRR's
  `unlinkat`.* The state is G1 inert, exactly as rows 8 and 17, with the same
  rungs. R1 implied that IGR "acts within about ten seconds". That claim is
  withdrawn: IGR's local work is class X, and the design relies on the ordering of
  the rungs and on IL, not on IGR's speed.
* **RO-5 (an unbounded backstop firing; new in R2, closed by BS-RM).** In the
  accepted literal the backstop service is `--service-type=exec` with
  `--property=TimeoutStartSec=⟨S⟩`. The accepted record establishes that such a
  unit is `Type=exec` and which start timeout applies [R2 §8 (r)]. That the start
  job of a `Type=exec` service is complete once the binary has been executed, so
  that `TimeoutStartSec=` ends there, is systemd's documented behaviour and is
  **proposed for citation [N]** (OH-S2b, `service.c` start-state transitions). If
  it holds, a firing that has started has **no PID-1 bound at all**, and, because
  the timer does not re-arm while its service is active [R2 §8 (j)], a firing that
  hangs also **prevents every later firing**. The repair BS-RM (§7.4) adds
  `--property=RuntimeMaxSec=⟨S_b⟩` so that PID 1 ends each firing. Until BS-RM is
  accepted, RO-5 is a defect of the accepted design that this record reports.
* **RO-6 (a persistent stall of a filesystem or the kernel; new in R2).** Every
  rung whose work touches `ext4` can be delayed by an `ext4` stall: that is
  every rung except RL-0 and CL-G (tmpfs only, GR-2), and CL-G only with GI-1. The
  design does not claim otherwise. Nothing in it makes a stalled kernel call
  return. The rule stays inert (IL) and the next boot clears it (RL-4).

Root's deliberate acts (SL-1), DF-1 and the unremovable-rule class (GU) are
unchanged ([D §4.2.5-R2 (l)]).

### 5.7 GRR, IGR and CL-G *(proposed)*

**GR-2 (new).** *Grant removal is the first mutating act of every rung that
removes a grant on its own initiative (IGR, CL-G), and it precedes every `ext4`
write, every spawn and every lock attempt in that rung.* CP's CQ-3 is not such a
rung: it keeps the accepted order, after the claim, because the claim is the
barrier of SB-1.

**GRR, the grant-release routine.** One routine, one implementation, one test
set. Inputs: the activation identifier and, for the holder, the identity it holds
in memory. Output: one outcome from `removed`, `absent`, `kept-damaged`,
`kept-foreign`, `unremovable {errno}`, `identity-unavailable`. It **never raises**.
It takes no lock, spawns nothing, calls no PK, reads no `ext4` object and writes
nothing except the one `unlinkat`.

1. **GRR-1, identity.** The holder uses its in-memory identity (also the content of
   `grant.id`). Any other caller opens K from a descriptor of `/run`
   (`O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC`), then `grant.id`
   (`O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK`) and requires a regular file,
   `root:root`, `0600`, at most 4,096 bytes (mechanically enforced), one parseable
   line. If K or `grant.id` is missing, unreadable or unparsable the outcome is
   `identity-unavailable` and the caller continues with CL's accepted,
   journal-based classification (CL-3). Without GI-1 (DEC-3) every non-holder
   caller takes that path.
2. **GRR-2, presence.** `fstatat(rules_dir_fd, name, AT_SYMLINK_NOFOLLOW)`.
   `ENOENT` → `absent`.
3. **GRR-3, descriptor re-verification, as G-R1.** `openat` the object
   (`O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK`); `fstat` must show a regular file
   with the identity's `(dev, ino)`, uid and gid 0, mode `0644`, `st_nlink = 1` and
   `st_size` equal to the identity's size and at most 65,536 bytes (a mechanically
   enforced cap: GRR reads at most size + 1 bytes); the full SHA-256 must equal the
   identity's; `flistxattr` must show no forbidden name. A mismatch is
   `kept-damaged` or `kept-foreign` and **removes nothing**.
4. **GRR-4, removal.** `unlinkat(rules_dir_fd, name, 0)`. `ENOENT` is `absent`. Any
   other error is `unremovable {errno}`. A `fsync` of the rules directory follows
   for parity with G-R1. On tmpfs it may be a no-op [R2 §7 (g)], and its result is
   ignored by GRR.

GRR is a small number of local system calls on tmpfs. **No elapsed time is claimed
for it** (class X). It waits for none of PID 1, a lock, a child, Polkit or `ext4`,
which is the whole of what is claimed, and it can still be delayed by the kernel.

**IGR (RL-0).**

* **When.** On every catchable end of the holder, from **one** call site: a
  `finally` that wraps the whole body of the holder from the first line after SG-1.
  The body ends by returning, by raising, or by observing the flag (SG-4). No
  signal handler calls IGR (SG-2).
* **IGR-0, latch.** `igr_state` is `idle`, `running` or `done`. IGR returns at once
  unless `idle`. Re-entry is impossible by construction: the single call site, the
  handlers that only set the flag, and GRR, which never raises. A second call (for
  instance a second `finally` after an exception in IGR-2) finds `done` and
  returns. Because GRR is idempotent (a second run of an interrupted removal
  finds `absent`), a *restart* after a crash is also safe: the next rung simply
  re-runs it.
* **IGR-1.** GRR with the in-memory identity. If AM-2 was never reached there is no
  rule and GRR returns `absent`.
* **IGR-2, evidence, after the removal.** One append of `igr {outcome, identity}` to
  the `ACT` journal with `fsync`, **best effort**: an `ext4` write that fails or
  stalls here changes nothing about the grant, which is already gone. If the
  process is killed between the `unlinkat` and this line, a later CL finds the
  rule absent with no `igr` line and classes it `absent-before-removal`, which
  still needs PK *not authorized* before `st1-verified`.
* **IGR-3.** Nothing else. IGR leaves `pass-a.json`, the directories and the
  records to CL.
* **What it does not do.** No spawn, no PK, no lock, no network. It does **not**
  claim `removed-verified`, which needs PK *not authorized* (CL-4).
* **CL's view.** CL-3 reads an `igr` line with outcome `removed` for the rule's
  identity as `removed-earlier`, and a rule found absent with no such line as
  `absent-before-removal`. Either still needs CL-4's own PK *not authorized* for
  `st1-verified`, like CQ-3's removal.
* **Why it is independent of PID 1.** It runs in the process that PID 1 already
  started. It needs PID 1 only to have delivered the signal, which a stop job,
  `RuntimeMaxSec=` and an orderly shutdown all do by `SIGTERM`.
* **No elapsed-time claim.** R1's "handler latency" paragraph (every blocking call
  bounded, "acted on within about ten seconds") is **withdrawn**. IGR runs when the
  main thread reaches a flag check (sliced waits, SG-4) or the end of its body.
  Between those points the holder may be in class-X work. IGR may therefore not run
  before a `SIGKILL`, and the design is correct in that case too (rows 8 and 17,
  IL).

**CL-G (the first act of CL in every trigger).** `stop-post`, `backstop` and
`attest` each begin with GRR, using `grant.id`, **before** CL-0's lock attempts,
its attempt directory and its journal. CL-G's outcome is held in memory and written
as a `cl-g {outcome}` line once the attempt journal exists. CL-3 then classifies
with the benefit of CL-G's result: `removed` → `removed-earlier` (in-process),
`absent` → by the journal as accepted, `kept-*` and `unremovable` → as accepted. If
CL-G returns `identity-unavailable`, CL-3 performs the accepted journal-based
removal (G-R1 with write-ahead, or its grant-priority form).

**The CL order, as amended:** CL-G; CL-0 (lock attempts to the λ deadline, attempt
directory, journal, `run-start`); CL-1; CL-2; CL-3; CL-4; CL-5; CL-5b (which removes
`grant.id` and K last); CL-6; CL-7. §7.9 maps an interruption after each.

### 5.8 PO-21 (c′) *(proposed [N], text for [D §4.4.2b])*

> **(c′)** `ExecStopPost=` is run, as the unit's user, after the main process
> ends for each of these causes: exit `0`, a non-zero exit, any signal, `RuntimeMaxSec=`
> expiry, `systemctl stop`, a failure to execute `ExecStart=`, and a stop issued
> by an orderly shutdown, reboot, `kexec` or userspace-only restart, **provided
> PID 1 can spawn it**. If spawning fails, the unit enters `FINAL_SIGTERM` with
> result `resources` and `ExecStopPost=` does not run [R2 §8 (c)]. The design
> relies on `ExecStopPost=` as one rung of RL and never as a guarantee.

(c′) is the R2 evidence restated. It adds no new host fact. What RL adds as new
proposed behaviour is IGR and GRR (§5.7), the inertness lemmas (§5.4) and the
bounded backstop of §7.4 (`backstop_max`, BS-RM).

### 5.9 Bounded alternative: a resident sentinel *(ALT-SENT, not recommended)*

A second long-lived root process, started at AK-1 before any grant exists, that
waits on a `pidfd` of the holder's main process and, when it ends for any cause,
performs GRR itself. It would close the **uncatchable** branch of RO-1 without
PID 1. It is not recommended because: (a) it adds a second long-lived root image
containing grant-removal code, including a re-hash for G-R1's descriptor
re-verification, which in a Python-free sentinel is new freestanding C and in a
Python sentinel is another unit PID 1 must have spawned and that is exposed to
the same signals; (b) it needs further host-behaviour citations (`pidfd_open`,
poll on process exit, the sentinel's own cgroup and kill behaviour); (c) IL already
shows that the residual it closes is a pre-pass, inert grant; and (d) which of the
two forms it takes depends on the Route 3 outcome. Peter may elect it (DEC-1). If
he does, OH-S4 gains a sentinel and a drill, and §5.6's RO-1 is narrowed to the
loss of both the holder and the sentinel. A sentinel does not remove RO-6.

### 5.10 Negative tests *(proposed, for OH-S4)*

| ID | Case | Asserts |
|---|---|---|
| NT-RL-1 | a fake manager delivers each catchable cause of rows 1 … 7 with `ExecStopPost=` and the backstop both returning `resources` | the rule is unlinked **before the holder exits**, an `igr` line is written **after** the unlink, no spawn, no lock attempt and no `ext4` write occurred before the unlink |
| NT-RL-2 | `SIGKILL` of the holder with both spawns failing (RO-1) | the rule stays live, a start attempt by the fake manager reaches CP, CP removes it (CQ-3 grant priority) and exits non-zero at CQ-4, and `ExecStart=` is never executed (IL) |
| NT-RL-3 | `SIGKILL` with stop-post failing but the backstop spawnable | the backstop's CL runs on its next firing, its first act is CL-G, and it records `st1-verified` or ST-1.ur. **No elapsed time is asserted** |
| NT-RL-4 | `backstop_max` firings with every CL dying | the backstop disarms after the last, appends a journal line, and exits; no unbounded loop; the final state is recorded or left to M-B |
| NT-RL-5 | the installed helper image removed after `ACT` (RO-2) | IGR still ran for a catchable end, RL-1 and RL-2 fail identically, and AP-0 and H-2 would have refused a prior tamper |
| NT-RL-6 | a wedged holder (alive, not observing) | `RuntimeMaxSec=` delivers `SIGTERM` (class M); the holder's `ActiveState` leaves `active`; IL′ holds from that moment; the `SIGKILL` after S finds nothing to do or ends the process |
| NT-RL-7 | IL over generated sequences | with the holder not `active` or `hold-end` present, no fake-manager path executes `ExecStart=` |
| NT-RL-8 | the terminal-cause table | every row 1 … 18 has a defined first removing rung and a defined residual |
| NT-RL-9 | a second and third `SIGTERM` (and a mix of the set H) delivered at every instruction boundary of IGR in a stepped harness | GRR runs at most once to completion, never restarts, never raises; the flag is the only effect of the extra signals; the final `igr_state` is `done` |
| NT-RL-10 | `SIGKILL` of the holder at each IGR point (before GRR-2, after GRR-3, after the `unlinkat`, after the journal line) | the state is exactly the one IM-I (§7.9) names for that point, and the next rung reaches `st1-verified` or a defined HARD STOP |
| NT-RL-11 | handler installation order | the handlers are installed before K exists, before the backstop is armed and before AM-2; a `SIGTERM` delivered at every earlier point creates no grant (SG-1) |
| NT-RL-12 | a backstop CL that never returns (an injected infinite loop) | with BS-RM the fake manager ends it at S_b; without BS-RM the model shows the timer never firing again (the defect of RO-5 is reproduced) |
| NT-RL-13 | `identity-unavailable` | GRR returns it for a missing, wrongly owned, oversized or unparsable `grant.id`, removes nothing, and CL falls back to the journal-based path |

---
## 6. Repair C — PO-21 (s): a valid start-history discriminator *(carried from R1; no R2-F2 change beyond the deadline note)*

### 6.1 What the accepted text says and what is true

[D §4.2.5-R5 (j)] PO-21 (s): *`InactiveEnterTimestampMonotonic` is set, at every
transition of a unit into `inactive` or `failed`, to the manager's monotonic
time of that transition, which is later than every earlier value in the boot.*
Lemma 2 of [D §4.2.5-R5 (f)] uses it as "every ended attempt changes τ to a value
later than every earlier one". SB-2, OS-1, OS-7, CQ-4 and the HL reasons depend
on that reading.

**What is true** [R2 §8 (s), (k), (u), (v)]:

* τ is set only on a transition **from a non-inactive state** into `inactive` or
  `failed`, **while the manager is not reloading**. A `failed` → `inactive`
  transition (`reset-failed`) does **not** set it.
* Its value is `now(CLOCK_MONOTONIC)` in microseconds. **Non-decreasing is
  established. Strictly later than every earlier value is not**: it rests on at
  least one microsecond elapsing between two such transitions.
* It is unchanged while the unit is `activating`, by reads and by a queued start;
  it survives reload and re-exec for a loaded unit; it reads `0` for a unit that
  has been loaded afresh; `systemctl show -p` prints it as decimal microseconds.
* A failed unit stays loaded with its last `InvocationID` until `reset-failed` or
  the next start; an `inactive` unit may be unloaded.
* An attempt ends `failed` when its pre-start step exits non-zero, is killed by a
  signal that no stop job sent, exceeds the start timeout, or cannot be forked or
  executed. **A stop during `start-pre` ends `failed`** (result `signal`) when the
  stop's signal terminates CP. It ends `inactive` **only if CP exits `0` before
  the signal lands** (PO-21 (u), established).
* `systemctl show -p`, run by an `ExecStartPre=+` process during its own start,
  returns without waiting and reports `activating` and τ as it was before the
  attempt (PO-21 (v), established).

### 6.2 What the barrier actually needs

SB-2 never needs "later than every earlier value", and never compares two later
values with each other. It needs one thing: *after the baseline, an ended attempt
leaves τ different from the baseline τ₀.* Three events could break that: the end
of an attempt that does not set τ; a τ that equals τ₀ by coincidence of the
microsecond; and a reload that resets τ to `0`. §6.4 closes the second by
construction, §6.5 handles the first and third explicitly.

### 6.3 The attempt model

| Unit state | `ActiveState` | Entered by | Left by |
|---|---|---|---|
| **Q-i**, quiescent inactive | `inactive` | an attempt's end; `reset-failed`; a fresh load | a start job |
| **Q-f**, quiescent failed | `failed` | an attempt's end with a non-zero result | a start job; `reset-failed` |
| **A**, attempt running its pre-start step | `activating` (`start-pre`) | a start job | CP's exit (to **R** or to an end) |
| **R**, running | `active` (after `ExecStart=`'s `execve`) | CP exit `0` | the main process's end or a stop |
| **E**, ended | `inactive` or `failed` | the end of A or R | — (it is Q-i or Q-f) |

An **attempt** is the interval from a start job leaving a quiescent state to the
unit next entering `inactive` or `failed`. By PO-21 (t) attempts never overlap,
and a start request that joins a queued or running start job is part of that
attempt.

### 6.4 The discriminator SD-1 and the baseline-separation precondition BSP *(proposed)*

* **Reads.** `τ(t)` is the value printed by `systemctl show -p
  InactiveEnterTimestampMonotonic rp11-capture-pass-a.service` (a decimal
  number; `0` if the unit has just been loaded). `m(t)` is
  `floor(CLOCK_MONOTONIC in microseconds)`, read by the holder with
  `clock_gettime`.
* **BSP.** At AM-0 the holder reads `m_a`, and **only then** reads τ₀ together
  with `ActiveState`, `InvocationID` and `Job`. It requires `τ₀ < m_a`. If
  `τ₀ ≥ m_a`, a transition occurred inside the read; it waits at least 2 ms and
  repeats, at most 5 times (class C), then exits `capture-baseline-unstable`
  (non-zero; CL runs; nothing has been linked). Each read is a `spawn()` of
  `systemctl show` under a class-E deadline (§7.3, §7.5): a read that does not
  finish is an *error*, never a baseline. The baseline is `B₀ = (m_a, τ₀, ActiveState,
  InvocationID, Job)` and is journaled in `run-start.capture`.
* **SD-1 (lemma).** If BSP held for `B₀`, then after the τ₀ read any transition of
  the capture unit into `inactive` or `failed` from a non-inactive state, outside
  a reload, leaves `τ ≠ τ₀`.
  *Proof.* The transition happens after the τ₀ read, which happens after the
  `m_a` read. By [E2] CLOCK_MONOTONIC does not decrease, so its time `t′` is at
  least the time of the `m_a` read, and by [E1] the new τ is `floor_µs(t′) ≥
  m_a`. By BSP, `m_a > τ₀`. Hence `τ ≠ τ₀`. ∎ A transition that happened between
  the `m_a` read and the τ₀ read would be reflected in τ₀ and make `τ₀ ≥ m_a`,
  which BSP rejects.
* **The verdict SD.** At any later read, **SD = "no attempt has ended since
  B₀"** if and only if `τ = τ₀` and the unit has not been unloaded (`τ₀ ≠ 0 ⇒
  τ ≠ 0`). `τ = 0` while `τ₀ ≠ 0` is **SD-2**: the unit was unloaded since the
  baseline and an attempt may have ended; the activation ends fail-closed (HL
  `capture-unloaded`).
* **No strictness is used.** SD compares a later τ with the baseline only, never
  two later values with each other, and BSP rules out equality with the baseline
  by the clock, not by an invariant of systemd.
* **Assumptions, as proposed obligations.** *[E1]* τ is the floor, in
  microseconds, of the manager's `CLOCK_MONOTONIC` at the transition ([R2 §8 (s)]
  states "now(CLOCK_MONOTONIC) in µs"; the floor is to be confirmed). *[E2]* the
  holder and the manager read the same `CLOCK_MONOTONIC` and it does not
  decrease within a boot (same time namespace: the holder's loaded unit has no
  `PrivateTimeNamespace=` or equivalent, a property the baseline compares).

### 6.5 Handling of every event the prompt names

| Event | τ effect (accepted evidence) | SD verdict | Handling |
|---|---|---|---|
| an attempt begins (start job, `activating`) | none | unchanged | CQ-4 reads τ during its own attempt: `τ = τ₀` for the first attempt (PO-21 (v)) |
| an attempt ends `failed` (CP non-zero, signal, timeout, fork or exec failure, or a stop during `start-pre`) | set from a non-inactive state | **changed** (SD-1) | SB-2 refuses every later attempt; HL `start-failed-before-exec` |
| an attempt ends `inactive` (the pass ends normally, or a stop lands after CP exited `0`) | set from a non-inactive state | **changed**, or `0` if the unit is then unloaded | the claim exists (CP exited `0` means CQ-2 ran), so SB-1 refuses every later attempt |
| **`reset-failed`** (`failed` → `inactive`) | **not set** | unchanged relative to the last failure's τ | a failure since the baseline already made `τ ≠ τ₀`; with none, the unit was merely reset and no attempt occurred. A root act, outside 𝒜 |
| `daemon-reload`, `daemon-reexec` | preserved for a loaded unit; transitions during the reload are not recorded | unchanged | an attempt whose end is processed after the reload is recorded then. A root act, outside 𝒜 (§13) |
| unit unloaded (`inactive`, garbage-collected) and reloaded | reads `0` | **SD-2 if `τ₀ ≠ 0`**; **blind if `τ₀ = 0`** (SD-3) | SD-2: the activation ends, no pass (liveness). SD-3: see below |
| the same microsecond | n/a | n/a | BSP removes equality with the baseline by construction. Two equal later observations carry no information beyond "no transition between them" |
| a stop during `start-pre` | the attempt ends `failed` (PO-21 (u)) | changed | **CX-4 is void** (§6.8) |
| userspace-only restart, reboot | outside 𝒜; M-B and DF-1 | — | unchanged |

**SD-3, the one blind case.** With `τ₀ = 0` and an attempt that ended `inactive`
with the unit then unloaded, SD reads `τ = 0 = τ₀`. Within 𝒜 an attempt ends
`inactive` only after CP exited `0`, so the claim exists and SB-1 refuses
([R2 §8 (u)]). A first attempt that failed unidentified ends `failed`, which
stays loaded and sets τ. So reaching SD-3 without a claim needs, together: a
failed unidentified first attempt, a root `reset-failed`, and the unit's unload,
all outside 𝒜 (§13, CX-5).

### 6.6 Revised lemmas *(replace [D §4.2.5-R5 (f)] Lemmas 2 and 3)*

* **Lemma 2′ (an ended attempt changes τ, or leaves a claim).** Every attempt
  ends by a transition of the unit into `failed` or `inactive` from a non-inactive
  state. By SD-1, that transition leaves `τ ≠ τ₀` provided BSP held and the
  transition was not during a reload. An attempt that ended `inactive` passed CP
  (PO-21 (u)), so its claim exists. An attempt that ended `failed` keeps the unit
  loaded (PO-21 (k)), so τ persists.
* **Lemma 3′ (the baseline is valid).** `τ₀` is read at AM-0 under BSP and
  re-read at `hold-start` under the lock; the re-read must equal `τ₀` with an
  empty `Job` and a quiescent state (OS-1, OS-7 unchanged). If an attempt had
  begun or ended between them, `hold-start` is not written.
* **Proof of OSA 1 and 3 over 𝒜**, [D §4.2.5-R5 (f)] and [D §4.2.5-R6 (e)] stand,
  with the third case (A₁ in the pre-barrier class and ended `inactive`) now
  **empty**: that case needs a stop job during `start-pre` that ends the attempt
  `inactive` with no claim, and PO-21 (u) shows that such a stop ends `failed`
  (`inactive` only after CP exited `0`, which means a claim).

### 6.7 Procedure amendments *(text for Appendix A)*

* **AM-0** reads `B₀` under BSP and journals `run-start.capture {active_state,
  invocation_id, inactive_enter_us, m_a_us, bsp_retries}`.
* **`hold-start`** re-reads `ActiveState`, `InvocationID`, `InactiveEnterTimestampMonotonic` and
  `Job`; it requires `ActiveState` `inactive` or `failed`, an empty `Job` and
  `τ = τ₀` (which includes "not unloaded").
* **CQ-4 (OS-1)** requires `activating`, `InvocationID` equal to CP's own,
  `τ = τ₀`, with the justification of SD-1. Its text is otherwise unchanged.
* **HL** reasons are unchanged. `capture-unloaded` is SD-2.

### 6.8 CX-4 under the accepted R2 evidence

[D §4.2.5-R5 (k)] and [D §4.2.5-R6 (f)] state CX-4: a root `stop` during the first
attempt's `start-pre`, **plus** "PO-21 (u) showing that such a stop ends the
attempt `inactive`", plus τ₀ = `0` and an unload. [D §4.2.5-R6 (f)] adds: *"If the
PO-21 (u) citation shows that a stop job during `start-pre` ends the attempt
`failed`, CX-4 is void."* The accepted R2 record establishes exactly that
(§6.1). **CX-4 is therefore void** for the cited systemd `259.5-0ubuntu3.4`.
The only remaining way both SB-1 and SB-2 are absent is SD-3 (CX-5, §13), which
needs three root acts outside 𝒜.

This is a restatement of an accepted residual, which Peter accepted as a
documented outside-𝒜 residual. It is **not applied by this proposal**. DEC-6
asks Peter to record the retirement. A change of the systemd version returns
CX-4 to review, because the retirement rests on that version's PO-21 (u).

### 6.9 PO-21 (s′) *(proposed [N], text for [D §4.4.2b] and [D §4.2.5-R5 (j)])*

> **(s′)** For the HF-07 systemd version: (1) `InactiveEnterTimestampMonotonic`
> is set to the floor, in microseconds, of the manager's `CLOCK_MONOTONIC` at a
> transition of the unit from a non-inactive state into `inactive` or `failed`,
> while the manager is not reloading [R2 §8 (s); the floor is *[N]*]; (2) it is
> not set by a `failed` → `inactive` transition, by a read, by a queued start or
> while the unit is `activating` [R2]; (3) it is non-decreasing, and **no
> strictness is claimed** [R2]; (4) it survives reload and re-exec for a loaded
> unit and reads `0` for a unit loaded afresh [R2]; (5) *[N]* the holder and
> the manager read the same, non-decreasing `CLOCK_MONOTONIC`.

The earlier wording, "at every transition" and "later than every earlier value",
is withdrawn. (s′) (1) … (4) restate R2. (5) and the floor are the only new
claims.

### 6.10 Negative tests *(proposed, for OH-S4)*

A fake manager implements exactly the R2-established semantics of §6.1 and
nothing stronger.

| ID | Case | Asserts |
|---|---|---|
| NT-SD-1 | a transition lands in the same microsecond as `m_a` | BSP rejects and retries; after five rejections the holder exits `capture-baseline-unstable` and links nothing |
| NT-SD-2 | randomized timelines of baseline reads and transitions, with transitions allowed in the same microsecond as each other | for every transition after the τ₀ read, `τ ≠ τ₀` (property test of SD-1) |
| NT-SD-3 | an attempt ends `failed`, then a second start | the second CP refuses at CQ-4; `ExecStart=` is never executed |
| NT-SD-4 | `reset-failed` after a failure | τ unchanged and still ≠ τ₀: the second attempt is refused |
| NT-SD-5 | `reset-failed` with no attempt since the baseline | τ = τ₀: the first attempt is allowed |
| NT-SD-6 | `daemon-reload` and `daemon-reexec` at every journal boundary, and an attempt whose end is processed during and after a reload | τ is preserved; an end during the reload is recorded after it |
| NT-SD-7 | the unit unloaded after the baseline with `τ₀ ≠ 0` | SD-2: HL `capture-unloaded`; the activation ends with no pass |
| NT-SD-8 | the SD-3 blind case, built from three root acts | the claim barrier still refuses an *identified* attempt; the blind case is reachable only through the three acts and is recorded as CX-5 |
| NT-SD-9 | a stop job during `start-pre` (the fake implements R2 (u)) | the attempt ends `failed`; SB-2 refuses the next; no combination produces CX-4 |
| NT-SD-10 | code scan | no comparison orders two later τ values; τ is compared only for equality with the journaled baseline |

---

## 7. Repair D — PO-11 (d) and R2-F2: enforced deadlines, named enforcers, and interruption

R1 repaired PO-11 (d) by an operational timeout family, which stands (§7.5, §7.10).
R2-F2 found that R1 also claimed bounds on *CL* and *IGR* that its own procedures
do not support. This section replaces R1's §7 and the elapsed-time statements of
R1's §§4.7, 5.3, 5.7 and 8.2 in full.

### 7.1 What was said, and what is true

**PO-11 (d).** [D §4.4.2a] required a cited bound on Polkit's reload after a
rules file is created or removed, and returned `ACT` and `DEACT` to design review
"rather than polling without a bound". [R2 §6.3, §6.4 (d)]: reload is synchronous
in a GIO monitor callback with no polkit-side timer, coalescing or bound; delivery
latency belongs to GLib and inotify. **No bound is citable.** §7.10 answers that
as R1 did, and it stays.

**R1's elapsed-time claims, and why they fail.**

* *"CL: worst case `lock_wait_ms` + local work + (`pk_op_ms` + `pk_call_ms`),
  below `TimeoutStopSec=` by the S grammar."* The S grammar adds a fixed 30-second
  margin to two arithmetic terms. It does not bound the **local work**, which is
  filesystem inspection, full hashing, process creation and reaping, journal
  writes and `fsync`. A margin is an expectation. It is not a bound.
* *"IGR acts within about ten seconds."* That sentence bounded each *sleep and
  wait* and then inferred a bound on the handler. IGR's own work (descriptor
  verification, a full hash, `unlinkat`, a directory `fsync`, journal appends) has
  no stated deadline, and a Python signal handler runs only when the main thread
  next executes bytecode.
* The accepted design's own *"CL-0 … CL-3, which are local operations bounded by
  S"* [D §4.2.5-R2 (g), "Latency bound"] has the same defect. D3-R3 withdrew that
  paragraph only as a statement about OH-D-7. The sentence and its echoes ("HL ends
  within Δ", "≤ Δ" in the (k) matrix) remain. Appendix A corrects them.

**What PID 1 does enforce** [R2 §8]:

| Fact | Source |
|---|---|
| `RuntimeMaxSec=` arms a deadline on `CLOCK_MONOTONIC` at the service's active-enter time; suspended time is not counted. On expiry the main process receives `SIGTERM`, and after `TimeoutStopSec=` `SIGKILL`, then stop-post runs | (d) |
| `ExecStopPost=` is spawned with `timeout_stop_usec`. On expiry `SIGTERM` goes to what remains (`FINAL_SIGTERM`), after another `TimeoutStopSec=` `SIGKILL` (`FINAL_SIGKILL`), and the unit ends `failed` with result `timeout` | (e) |
| a start-pre step that times out, or is stopped, ends the attempt `failed`; `ExecStart=` is never executed | (o), (u) |
| the capture unit's start timeout is the manager default (HF-16: 1 min 30 s) unless the unit sets one; it is finite for this `Type=exec` unit | (r) |
| the backstop timer does not re-arm while its service is active, and re-arms when the service enters `inactive` or `failed` | (j) |

None of these says that a process leaves an uninterruptible kernel call because a
signal was sent. They fix **when signals are sent**.

### 7.2 Deadline classes

| Class | Name | Who enforces | What it bounds | What it does **not** bound |
|---|---|---|---|---|
| **E** | enforced wait | the helper, on its **own** waiting, with a deadline on `CLOCK_MONOTONIC` set **before** the wait starts and checked at every wake-up (at most every `slice_ms`) | the time the helper spends *waiting* on a child, a lock or a clock. At expiry it stops waiting, kills the child's process group, waits for its reaping for at most `reap_grace_ms` (g), then **abandons** the child, and takes the operation's fail-closed consequence | the time a child or the kernel needs to finish; the creation of the child; the helper's own reads, writes and CPU; the time to run the expiry code |
| **M** | enforced by PID 1 | PID 1, by a unit property (`RuntimeMaxSec=`, `TimeoutStopSec=`, the start timeout) | **when `SIGTERM` and `SIGKILL` are sent**, while PID 1 can act (RO-3) | completion of any work; a process in an uninterruptible kernel call; suspended time (`CLOCK_MONOTONIC`) |
| **C** | count | the code, by a fixed number of iterations | the number of attempts, firings or retries | the time of an iteration, which is itself E, M or X |
| **X** | expected quick | nobody | nothing | everything. **No elapsed time is stated for an X operation, and no formula, table, record or test treats a sum of X operations as a bound** |

A **volume cap** (for example, reading at most size + 1 bytes of a file) is
enforced mechanically. It bounds the amount of work and not its time, and it is
listed beside the class it modifies.

### 7.3 Inventory of every potentially blocking operation

Operations are grouped across ACT (AP-0 … HL), CP (CQ-0 … CQ-7), IGR, CL (CL-G …
CL-7, in every trigger), the backstop (BS-1 … BS-4 and its service) and
verification (AP-0, H-2, H-2b, AV-1's re-verification, CL-6, drift checks).

| # | Operation | Where it occurs | Class | Enforcement and fail-closed consequence |
|---|---|---|---|---|
| 1 | creating a child (`fork`, `clone`, `execve` inside `spawn()`) | holder: BSP reads, AK-1 `systemd-run`, the timer `show`, AV-1 PK; CP: CQ-4 `show`, CQ-5 PK; CL: CL-2, CL-4, CL-6; BS: BS-1 … BS-3 | **X** | none. The call's deadline starts **before** creation, so a slow creation consumes it, but creation itself cannot be interrupted |
| 2 | waiting for a child's exit and reading its output | every `spawn()` | **E** (`pk_call_ms` c) | at expiry `SIGKILL` to the child's process group; result `error` (PK: `unconfirmed`). Output is capped at 65,536 bytes (volume cap); more is `error` |
| 3 | reaping a killed child | every `spawn()` | **E** (`reap_grace_ms` g) | after g the child is **abandoned** (not reaped), `abandoned: true` is recorded, and the helper continues fail-closed. An abandoned child holds no descriptor of K (LD-3) |
| 4 | the PK subject's own life (`sleep 60`) | PK/2 | self-limiting (its argument), not enforced by the helper | counted as **X** for every claim. If the helper dies the subject ends by itself |
| 5 | the executor's wait for the `act` record or the holder's end | AP-2 | **E** (`act_wait_s`) | HARD STOP `act-unconfirmed`. The executor acts on nothing and repairs nothing. The holder continues under L |
| 6 | the lock loop on K | holder AM-0 (once), HL decision (once), CP (once, CQ-1), CL (to the deadline) | **E** (`lock_wait_ms` λ) for the loop. Each `flock(LOCK_NB)` call is non-blocking by its flag and counted **X** | at λ: `lock_mode: "degraded"` (CL), `consume-busy` (CP), HARD STOP `lock-object` (holder AM-0) |
| 7 | sleeps between polls (HL Δ, the PK schedule, BSP's 2 ms) | holder, PK/2, CL | **E** | sliced at `slice_ms` so that the flag (SG-4) is observed |
| 8 | reading small root-owned files: journals, records, `pass-a.json`, `grant.id`, the H-1 record, A-2 pins | all | **X** with a **volume cap**: `pass-a.json` 65,536 bytes (accepted CQ-0), `grant.id` 4,096 bytes, any journal `journal_max_bytes` | an oversize or unparsable object is `invalid-journal` or `consume-unidentified` and fails closed. No time is stated |
| 9 | SHA-256 over files | GRR (the rule, at most 65,536 bytes); AP-0, AM-0, H-2 (helper images, `rp11_h1.py`); CL-6's **recomputation of the H-1 `baseline`**, which hashes every member of the baseline set | **X** with a volume cap per file | CL-6's recomputation is the **largest local job** in CL and runs **last** before the records, so an interruption in it costs only verification (§7.9, L7) |
| 10 | metadata and extended-attribute inspection (`fstat`, `lstat`, `flistxattr`, `readlink`) | every verification | **X** | none |
| 11 | appends and `fsync` to the `ext4` journals and records; `mkdirat` of evidence directories; PF and PT publication (`linkat`, `renameat2`, `mkdirat`) | holder, CP, CL | **X** | an *error* return is handled as accepted (grant-priority and GP-R3 forms). A *stall* is unbounded (RO-6) |
| 12 | `unlinkat` of the rule and of `pass-a.json`; `fsync` of a tmpfs directory | GRR, CQ-3, CL-5, CL-5b | **X** (tmpfs; `fsync` may be a no-op [R2 §7 (g)]) | none |
| 13 | signal delivery to the interpreter and handler execution | holder | **X** | handlers run only between bytecodes of the main thread and only set a flag (SG-2). The flag is observed at boundaries and at every slice of an E wait (SG-4) |
| 14 | the PK series as a whole | PK/2 | **E** (P) | no call starts after P; the last call stops being waited for by P + c + g; result `unconfirmed` |
| 15 | BSP re-reads | holder AM-0 | **C** (5) | `capture-baseline-unstable` |
| 16 | backstop firings that run CL | BS-4 | **C** (`backstop_max` B; `k` ≤ 99 accepted) | the next firing disarms the timer, appends a journal line, exits non-zero |
| 17 | the holder's whole life | ACT … HL | **M** (`RuntimeMaxSec=` L) | `SIGTERM` at L, `SIGKILL` after S |
| 18 | the stop-post CL's whole life | RL-1 | **M** (`TimeoutStopSec=` S) | `SIGTERM` at S, `SIGKILL` after a further S, unit `failed` / `timeout` |
| 19 | the backstop firing's whole life | RL-2 | **M** (`RuntimeMaxSec=` S_b, **proposed [N]**, BS-RM) | `SIGTERM` at S_b, `SIGKILL` after S. **Absent BS-RM, no bound (RO-5)** |
| 20 | CP's whole life | RL-3, CQ-0 … CQ-7 | **M** (the capture unit's start timeout T_s) | the attempt ends `failed`; `ExecStart=` is never executed; SB-2 refuses every later attempt |
| 21 | verification reads by the executor (AP-0, H-2, H-2b) | executor, unprivileged, interactive | **X**; no PID-1 timer | an interruption mutates nothing (these steps create nothing): INVALID RUN, no lock object, no grant |
| 22 | `attest` | operator, interactive | no enforcer | an interruption leaves the records missing; every later RP-11 step refuses (the accepted gate) |

### 7.4 Terminators by procedure, and the backstop literal

| Procedure | PID-1 terminator (class M) | Offsets | Whole-procedure elapsed-time claim |
|---|---|---|---|
| holder (ACT, HL, IGR) | `RuntimeMaxSec=` L | `SIGTERM` at L; `SIGKILL` after S | the holder leaves `active` at L (IL′). **No claim about when its work completes** |
| stop-post CL (RL-1) | `TimeoutStopSec=` S | `SIGTERM` at S; `SIGKILL` after a further S; then `failed`, result `timeout` | **none.** CL may be signalled at S and killed at 2S |
| backstop firing (RL-2) | `RuntimeMaxSec=` S_b (BS-RM) | `SIGTERM` at S_b; `SIGKILL` after S | **none**; the firing ends, and the timer then re-arms [R2 §8 (j)] |
| CP (RL-3) | the capture unit's start timeout T_s | the attempt ends `failed` | **none** for CP's completion. SB-2 and SB-1 make every later attempt refused |
| `attest`, AP-0, H-2 | none | — | none |

**BS-RM (proposed [N], a correction of the accepted backstop literal).** The
literal of [D §4.2.5-R2 (f)] ends with `--property=TimeoutStartSec=⟨S⟩`. It is
replaced by two properties:

```text
--property=RuntimeMaxSec=⟨S_b⟩ --property=TimeoutStopSec=⟨S⟩
```

and `TimeoutStartSec=` is dropped, because on a `Type=exec` service it would end at
`execve` (§5.6, RO-5). `S_b` is a parameter (§7.6). The statement that
`RuntimeMaxSec=` applies to the main process of a `Type=exec` service that a timer
activates is the same code path R2 cites for the holder [R2 §8 (d)] and is
**proposed for citation** (OH-S2b). It needs no new host fact beyond that.

### 7.5 `spawn()`, the helper-child discipline, and PK/2

These are properties of the activation design and hold under every Route 3
outcome that keeps any child process.

* **HS-1.** Every child of a root helper is created by **one** function, `spawn()`,
  in one module. No other process-creation call appears in any root helper
  (scan test NT-HS-1).
* **HS-2.** `spawn()` passes **only** the closed map `{LC_ALL=C, PATH=/usr/bin}`,
  never `None`, never a copy of the helper's own environment, and the program's
  absolute path under `/usr/bin`.
* **HS-3.** `close_fds=True`, `pass_fds=()`, working directory `/`, a **new
  session**, no `preexec_fn`, and for the PK subject the credential change by the
  primitive's own arguments (user, group, supplementary groups) rather than by code
  between `fork` and `exec` *[N: CPython 3.14.4's process-creation arguments are
  cited at OH-S2b]*.
* **HS-4.** No shell, no `os.system`, no `os.exec*p`, no `shell=True`.
* **HS-5 (class E).** Every spawn has a monotonic deadline c, is killed at it by a
  signal to its process group, is given at most g to be reaped, and is then
  abandoned (§7.2). No `wait()` or `waitpid()` without a deadline.
* **HS-6.** `rp11_h1.py` (or its successor under Route 3) reads the environment
  only for the diagnostic `INVOCATION_ID` and decides nothing from any other
  variable.

**PK/2 (replaces `pk-root/1` of [D §4.2.5-R1 (f)]).**

* **Subject.** One subject process **per call**, created by `spawn()`, in its own
  session, with the supplementary groups, GID and UID that the H-1 record holds for
  `ubuntu`, executing `/usr/bin/sleep 60`. It is killed after each call. If the tool
  dies it lives at most 60 s and holds no lock descriptor.
* **Call.** `/usr/bin/pkcheck --action-id org.freedesktop.systemd1.manage-units
  --process ⟨pid⟩,⟨start-time⟩,⟨uid⟩ --detail unit rp11-capture-pass-a.service
  --detail verb ⟨verb⟩`, as **root**, without `--allow-user-interaction`, with the
  closed environment of HS-2, under the deadline c. The process group is killed at c.
* **Outcome of one call.** Exit `0` is `authorized`. Exit `1` or `2` is
  `not-authorized` ([R2 §6.4 (e)]: 1 not authorized, 2 challenge). Any other status,
  a spawn failure, an unparsable result, the deadline, or an abandon is `error`.
* **Series.** Three modes: **seek-authorized** stops at the first `authorized`;
  **seek-not-authorized** stops at the first `not-authorized`;
  **first-decisive** stops at the first `authorized` or `not-authorized`. An
  `error` never ends a series: it retries on the closed schedule, offsets 0, 250,
  500, 1,000, 2,000, 3,000 and 4,000 ms, then every 2,000 ms, measured on
  `CLOCK_MONOTONIC`. **No call starts after P has elapsed.** The helper stops
  *waiting* on the last call by P + c + g. A `stop_requested` flag (SG-4) ends the
  series at the next slice with result `interrupted`.
* **Result.** `authorized`, `not-authorized`, or `unconfirmed`, with a reason:
  `only-errors`, `still-authorized` (a seek-not-authorized series saw only
  `authorized` and errors), `not-seen` (a seek-authorized series saw only
  `not-authorized` and errors), or `interrupted`.
* PK starts, stops or changes nothing (as accepted).

### 7.6 Parameters and the sizing rules N1 … N4

| Name | Meaning | Grammar | Recommended |
|---|---|---|---|
| `pk_op_ms` (**P**) | the interval in which a PK/2 series may **start** calls | 5,000 … 60,000 | 30,000 |
| `pk_call_ms` (**c**) | deadline of one child wait (a PK call, a `systemctl show`, a `systemd-run`) | 1,000 … 10,000, and c ≤ P | 5,000 |
| `reap_grace_ms` (**g**) | how long a killed child is waited for before abandon | 500 … 5,000 | 2,000 |
| `lock_wait_ms` (**λ**) | CL's lock acquisition deadline (LD-5) | 1,000 … 10,000 | 5,000 |
| `slice_ms` | the longest interval between flag checks inside any E wait | 50 … 250 | 100 |
| `stop_timeout_s` (**S**) | the holder's `TimeoutStopSec=`; also the backstop service's | 60 … 600 | 120 |
| `bs_runtime_s` (**S_b**) | the backstop service's `RuntimeMaxSec=` (BS-RM) | 60 … 600 | 120 |
| `backstop_period_s` (**R**) | the backstop timer's period | 30 … 600 (as accepted) | 60 |
| `backstop_max` (**B**) | the most firings that run CL before the backstop disarms | 1 … 99 | 20 |
| `reserve_ms` (**ρ**) | the allowance for class-X work in the sizing rules. **An expectation, not a bound** | ≥ 30,000 | 30,000 |
| `act_wait_s` | the executor's deadline in AP-2 | 60 … L | L |
| `journal_max_bytes` | volume cap for any journal read | 65,536 … 4,194,304 | 1,048,576 |
| `start_window_s` (W), `lease_s` (L), `poll_ms` (Δ) | unchanged | as accepted | as accepted |

Define **W_show = c + g** and **W_series = P + c + g**. The **sizing rules** are
*necessary* conditions that AP-0 evaluates. **A set that violates one is refused,
because the deadline-enforced waits alone could consume the timer. A set that
satisfies them proves nothing about CP, CL or IGR.** No document, record or log
line states a satisfied rule as a bound (NT-DL-4, NT-DL-5).

* **N1 (CP).** `T_s · 1,000 ≥ W_show + W_series + ρ`, with CQ-4's one `show` and
  CQ-5's one series. `T_s` is the capture unit's loaded `TimeoutStartUSec`, recorded
  in the H-1 baseline, **finite** (AR-4). With HF-16's default (90 s) and the
  recommended values, `7,000 + 37,000 + 30,000 = 74,000 ≤ 90,000`: **satisfied, 16 s
  to spare**. A larger P needs an explicit `TimeoutStartSec=` in the unit, which
  changes the reviewed unit bytes (T-B1) and is the second alternative of DEC-2.
* **N2 (CL, stop-post and backstop).** `S · 1,000 ≥ λ + W_show + W_series + W_show
  + ρ`, with CL-2's `show`, CL-4's series and CL-6's `show`. Recommended:
  `5,000 + 7,000 + 37,000 + 7,000 + 30,000 = 86,000 ≤ 120,000`: **satisfied**.
* **N3 (backstop firing).** `S_b · 1,000 ≥` the same left side as N2. Recommended
  `S_b = S`.
* **N4 (holder before HL).** `L · 1,000 ≥ 9 · W_show + 2 · W_series + W · 1,000 + ρ`:
  BSP's first read and at most five repeats (six `show` calls), AK-1's `systemd-run`
  and its timer `show`, `hold-start`'s re-read, AV-1's two series, the start window
  and the allowance.

R1's S grammar `⌈λ/1,000⌉ + ⌈(P + c)/1,000⌉ + 30 … 600` and its `T_s` rule
`⌈(P + c)/1,000⌉ + 30` are **withdrawn** (§7.7, W-6, W-7). The 30-second term was
never derived. It is now the parameter ρ, named for what it is.

### 7.7 Withdrawn claims

| # | Claim | Where it appeared | Why it is withdrawn | Replacement |
|---|---|---|---|---|
| W-1 | CL's worst case is `lock_wait_ms` + local work + (P + c), below S "by the S grammar" | [R1 §7.3] | the grammar adds a margin; the local work is class X | CL is class M-terminated at S and 2S (§7.4); N2 is a necessary condition; §7.9 IM-L |
| W-2 | a catchable end "is therefore acted on within about ten seconds" | [R1 §5.7] | IGR's work is class X, and handlers run only between bytecodes | no time claim; GR-2, the ladder's order, IL, IL′ |
| W-3 | the "Operational latency" column of the ladder | [R1 §5.3] | same | the column "Terminated or limited by (class)" |
| W-4 | the backstop in total takes B·(R + S) | [R1 §7.3] | needs CL bounded by S, and the accepted literal bounds no started firing (RO-5) | B firings (class C), each ended by BS-RM (class M) |
| W-5 | "CL-0 … CL-3, which are local operations bounded by S"; "HL ends within Δ"; "HL detecting an end (≤ Δ)" | [D §4.2.5-R2 (g), (k)] | class X work stated as bounded | corrected in Appendix A: HL observes every Δ **plus** one observation whose child waits are class E and whose other work is class X |
| W-6 | the S grammar `⌈λ/1,000⌉ + ⌈(P + c)/1,000⌉ + 30 … 600` | [R1 §7.3] | a fixed margin presented as a bound | N2 and the parameter ρ |
| W-7 | `T_s ≥ ⌈(P + c)/1,000⌉ + 30` | [R1 §7.3], generalizing AR-4 | same | N1 |
| W-8 | the lock wait is "always shorter than S by the inequality of §7.3" | [R1 LD-5] | it follows from W-6 | LD-5, revised |
| W-9 | "CL is not killed by the stop timeout" | [R1 NT-LD-6] | not showable | NT-LD-6, revised |
| W-10 | every blocking *call* in the holder is bounded | [R1 §5.7] | only the *waits* are | §7.3 |
| W-11 | IGR "cannot be starved by PID 1, by the lock or by Polkit" | [R1 §5.7] | kept only in the narrowed form: it **waits for none** of them | §5.7 |

### 7.8 Signal discipline SG-1 … SG-8 *(proposed)*

* **SG-1, when handlers are installed.** The holder installs handlers for the set
  **H** = `SIGTERM`, `SIGINT`, `SIGHUP`, `SIGQUIT`, `SIGUSR1`, `SIGUSR2`, `SIGALRM` as
  the **first act** of its `hold` entry, after the helper-start contract RH is
  discharged and **before any state operation**: before AM-0's re-checks, before K,
  `grant.id`, the journal, AK-1, AM-1 and **AM-2**. A signal that arrives before SG-1
  takes its default action and ends the process **before any object exists**
  (state ST-1; nothing to remove).
* **SG-2, handlers only set a flag.** A handler sets `stop_requested = True` and
  returns. It raises nothing, calls nothing, writes nothing, takes no lock and never
  calls IGR. R1's design, in which the handler raised a dedicated exception that
  could fire at any bytecode, is **withdrawn**: that exception could land inside
  IGR itself.
* **SG-3.** `SIGPIPE` stays ignored (the interpreter's default). `SIGCHLD` is not
  handled: children are polled. A signal outside H that cannot be caught, or whose
  default action terminates, is an *uncatchable* cause (§5.5, rows 8 and 9).
* **SG-4, where the flag is checked.** At every step boundary of the holder (AM-0's
  steps, AK-1, AM-1, AM-1R, **immediately before AM-2's PF-6 link**, AV-1, AM-3,
  `hold-start`); at every HL iteration; and **at every `slice_ms` wake-up of every E
  wait** (§7.3 rows 2, 3, 6, 7, 14). When the flag is set an E wait kills and
  abandons its child, returns `interrupted`, and the body returns. After PF-6
  returns the flag is checked at the very next statement. A `SIGTERM` delivered
  between the last check and PF-6 therefore costs a brief G1 that IGR removes.
* **SG-5, a second signal.** Further signals set the same flag again. They never
  re-enter IGR and never restart GRR. Because no handler raises, **no exception can
  arise inside GRR from a signal**.
* **SG-6.** The holder never blocks signals. A blocked pending signal would be
  delivered at an unpredictable later point, which SG-2 and SG-4 are designed to
  avoid.
* **SG-7, the single IGR site.** IGR runs from one `finally` around the whole body
  after SG-1, once (IGR-0). After it the holder returns its exit status. No
  `atexit` work and no `os._exit` before IGR exist.
* **SG-8, CP, CL and BS install no handlers.** They take the default action on
  `SIGTERM`. Their interruption is **mapped** (IM-C, IM-L, IM-B) and not handled,
  because their first state-changing acts (CQ-3, CL-G) are already ordered first,
  and a handler would add a path whose own elapsed time is unbounded.

The design **does not depend** on any `finally` completing in any time. IGR is the
first rung. Its absence is covered by RL-1 … RL-4 and by IL and IL′.

### 7.9 Interruption maps

"Interrupted" means the process is ended by a signal at the stated point, by a
class-M timer or by a root act. The *state* is what remains. The *first owner* is
the first rung (§5.3) that acts next. All objects named are under `/run` unless
stated, and a kernel boot (RL-4) clears every one of them.

**IM-L, CL (each trigger).** CL receives `SIGTERM` at S (stop-post) or S_b
(backstop) and `SIGKILL` after S, or any kill. CL installs no handler (SG-8), so
the first signal ends it.

| Point | Interrupted at | State | Grant | First owner | Then |
|---|---|---|---|---|---|
| **L0** | process start, K open, `grant.id` read, GRR-2 or GRR-3, **before** the `unlinkat` | **ST-1.i**: holder gone, rule live | G1 **inert** (IL) | the backstop's CL (if armed and spawnable); else CP at a later start | the boot; `attest` for records |
| **L1** | after the `unlinkat`, before CL-0 finishes (no attempt journal yet) | rule absent, nothing recorded | G2 | the backstop's CL (classes the rule `absent-before-removal`) | `attest` |
| **L2** | during CL-0: lock attempts, attempt directory, journal | a partial attempt directory may exist; `k` counts it | G2 | the backstop's CL as attempt `k + 1` | `attest` |
| **L3** | after CL-0, before CL-3's record | `run-start` present, no classification line | G2 | the backstop's CL | `attest` |
| **L4** | during CL-4's PK series, or after it before its record | rule absent, `removed-verified` **not** recorded | G2 (G3 not recorded) | the backstop's CL re-runs CL-4 and needs PK *not authorized* again | `attest` |
| **L5** | during CL-5: `remove-intent` for `pass-a.json` written, `unlinkat` perhaps done | **ST-1.d1** | G3 if CL-4 recorded it, else G2 | the backstop's CL-5 classes `removed-earlier` or `absent-before-removal` from the intent line | the boot |
| **L6** | during CL-5b: tree **P**'s top, tree **R**, `grant.id`, K | partial `/run` objects: class S0 | as L5 | the backstop's CL-5b, else the boot | — |
| **L7** | after CL-5b, during CL-6 (reads, the **baseline recomputation**, `show`) | everything removed; `st1-verified` not recorded | G3 | the backstop's CL re-verifies; or `attest` | — |
| **L8** | during CL-7, record publication | PF is atomic: a record is absent or complete. The journal lacks `run-end`. **ST-1.ur** if no `deact` record exists | G3 | the backstop writes the record; or `attest`. If a terminal `deact` record exists BS-2 disarms | — |
| **L9** | after `run-end` | complete | G3 | none | — |

Every row ends in `st1-verified`, in a defined HARD STOP (ST-1+R), or in ST-1.bc
followed by attestation. **No row waits for a human to disable the grant.**

**IM-I, IGR.**

| Point | Interrupted at | State | Grant | First owner |
|---|---|---|---|---|
| **I0** | before GRR-2 (flag observed, nothing done) | ST-1.i | G1 inert | stop-post CL (CL-G); else the rungs of L0 |
| **I1** | GRR-3 verification (open, `fstat`, hash, `flistxattr`) | ST-1.i | G1 inert | as I0 |
| **I2** | after the `unlinkat`, before the directory `fsync` or the `igr` line | rule absent, unattributed | G2 | stop-post CL classes it `absent-before-removal` |
| **I3** | after the `igr` line is durable | rule absent, attributed | G2 | stop-post CL: `removed-earlier`, then CL-4 |
| **I4** | the `igr` line's `fsync` stalls | as I2 or I3 | G2 | RO-6 for the evidence; the grant is already gone |

A second termination signal at any of I0 … I4 sets the flag and changes nothing
(SG-5). `SIGKILL` at any of them is the corresponding row.

**IM-C, CP.** The start timeout T_s or any kill ends CP. The accepted matrix
[D §4.2.5-R5 (i)], column "K or T", is unchanged and is restated by reference:
before CQ-2 no claim exists and the rule stays live (G1), the attempt ends `failed`,
SB-2 refuses every later attempt, HL ends `start-failed-before-exec`, and IGR or CL
removes the rule first. After CQ-2 the claim exists (SB-1). After CQ-3's `unlinkat`
and before `removed` the rule is absent and CL classes it `absent-before-removal`.
During CQ-5 the rule is gone (G2), no `consumed` line exists and `ExecStart=` is
never executed [R2 §8 (o)]. After `consumed` and before CQ-7 the attempt is recorded
`start-failed-before-exec`. R2-F2 adds only that **T_s is class M and CP's own
elapsed time is not claimed**, and that CP installs no handler (SG-8).

**IM-B, a backstop firing.** BS-RM sends `SIGTERM` at S_b and `SIGKILL` after S. The
points are those of IM-L. After the service ends, the timer re-arms and fires again
[R2 §8 (j)], at most B times. Without BS-RM a hung firing prevents every later one
(RO-5).

**IM-A, the holder (ACT and HL).** Termination at a point leaves the objects built so
far. Before SG-1 and AM-0: none. After K and before the journal: K only (S0). AK-1:
ST-1.a0. AM-1: ST-1.a1 (tree **P**). Between the `grant.id` write and PF-6:
`grant.id` and tree **P**, no rule. After PF-6 (ST-1.a2, ST-2): G1, removed by IGR if
the end is catchable and reached, else by RL-1 … RL-4. After CP's CQ-3 (ST-3): no
grant. Each continues to CL as in §8.3.

### 7.10 PO-11 (d′) *(proposed [N], text for [D §4.4.2a]; retained from R1)*

> **(d′)** *No bound is claimed on the time between the creation or removal of a
> polkit rules file and polkitd's use of that change.* A PK call returns the
> decision of polkitd's **current** rule set at the instant of the call. The
> design waits for a stated decision for at most `pk_op_ms` (starting calls) and
> `pk_call_ms` plus `reap_grace_ms` (waiting on the last call), enforced by the
> caller (class E), and treats every other result, including the expiry of that
> time, as *unconfirmed*, which **fails closed at every use** (§7.11). The same
> holds for `/run/polkit-1/rules.d` ((f)(iii)). Obligations (e), (f)(i), (f)(ii)
> and (f)(iv) stand as accepted. **Every operational timeout of this design fails
> closed: no expiry authorizes, passes, or hides a failure.**

AP-0's requirement "the PO-11 (d) … citations accepted" becomes "PO-11 (d′)
accepted, the parameter grammar of §7.6 and the sizing rules N1 … N4 evaluated".
**This needs no host citation for (d′).** The block that returned `ACT` and
`DEACT` to design review is answered by the design itself: no bound is cited, and
nothing polls without one.

### 7.11 What each timeout does, and what it can leave

| Step | Mode | Budget (class E) | On `unconfirmed` |
|---|---|---|---|
| AV-1, positive control for verb `start` | seek-authorized | P | `ACT` ends HARD STOP `grant-not-seen`; CL runs, rule first. No pass. PK's sensitivity was not shown, so nothing later may be read as evidence |
| AV-1, negative control for verb `stop` (AR-7) | first-decisive | P | `authorized` fails `ACT` at once. `unconfirmed` fails `ACT` (HARD STOP `stop-control-unconfirmed`) |
| CQ-5, consume post-check | seek-not-authorized | P | CP exits non-zero `consume-failed {CQ-5, removed-unconfirmed}`; **`ExecStart=` is not executed**; CL re-checks |
| CL-4 | seek-not-authorized | P | rule class `removed-unconfirmed`; outcome HARD STOP; the backstop retries within `backstop_max` |
| GP-R3's grant post-check | as CL-4, result held in memory | P | as CL-4 |
| attestation, `cleared-by-boot` | seek-not-authorized | P | no `st1-verified` record is written |
| H-2, AP-0, CL-6 | **do not run PK** | — | CL-6 uses CL-4's result |
| drills (OH-S8b) | as the step they exercise | P | as that step |

* **G1 is unaffected.** A CQ-5 timeout blocks `ExecStart=`. The rule is already gone
  from the directory (CQ-3).
* **After CQ-5 `unconfirmed(still-authorized)`**, polkitd may still authorize a
  `start` for `ubuntu`, which is G2 in the visible-lag state. A later start reaches
  CQ-2, finds the claim (`EEXIST`) and exits with nothing touched (SB-1). No pass.
* **After AV-1 `grant-not-seen`**, polkitd may load the rule late. CL removes the
  file, and any reload that follows reads a directory without it.
* **Every wait in the design is class E, M or C.** The PK series ends waiting by P + c
  + g; the lock loop at λ; BSP after five reads; HL at L (M); the backstop after B
  firings (C) with each firing ended by S_b (M); PK never runs outside these
  procedures. Class-X work is **not** bounded, and §7.9 states what its interruption
  leaves.
* **NUDGE is not proposed.** Creating and removing an empty `*.rules` file in a
  monitored directory to force a reload would add a write path into polkit's rules
  directory whose effect is a GLib behaviour no accepted record cites. The safe
  response to a missed event is the failure above.

### 7.12 Negative tests *(proposed, for OH-S4; none run here)*

| ID | Case | Asserts |
|---|---|---|
| NT-DL-1 | a fake child that ignores `SIGTERM` and never exits | the call is killed by `SIGKILL` to its process group at c, waited for at most g, then abandoned with `abandoned: true`; the result is `error`; the assertion is on **the helper's waiting** on a fake clock, and **not** on the child |
| NT-DL-2 | a fake child that cannot be reaped (a model of an uninterruptible call) | the helper abandons it, continues fail-closed, and leaks no descriptor of K |
| NT-DL-3 | code scan over every root helper | every wait carries a monotonic deadline; no unbounded `wait()` or `waitpid()`; `time.sleep` appears only inside a sliced wait; every file read carries a volume cap |
| NT-DL-4 | text and record scan | no document, record schema, log format or test states an elapsed time for a class-X operation or derives one from N1 … N4; the strings "bounded by S", "within Δ", "within about", "by the S grammar" are absent; a satisfied sizing rule is never recorded as a bound |
| NT-DL-5 | AP-0 with parameters that violate each of N1 … N4 | INVALID RUN; no lock object, no grant. A satisfying set is accepted **and** recorded as `sizing: "necessary-conditions-met"` |
| NT-DL-6 | the executor's `act_wait_s` expiry | HARD STOP `act-unconfirmed`; the executor mutates nothing; the holder is unaffected |
| NT-DL-7 | an oversize journal | `invalid-journal`; the read stops at `journal_max_bytes`; fail-closed |
| NT-DL-8 | the backstop literal and the loaded properties | `RuntimeMaxSec=` equals S_b and `TimeoutStopSec=` equals S; no `TimeoutStartSec=`; the baseline normalization carries them |
| NT-DL-9 | a fake manager implementing exactly R2 §8 (d), (e), (j), (o), (u) | signals at the stated offsets and no stronger behaviour; the interruption maps IM-L, IM-C, IM-B reproduce |
| NT-DL-10 | CL killed at each of L0 … L9 in a stepped harness | the state and first owner equal §7.9; a following backstop CL reaches `st1-verified` or a defined HARD STOP; none waits for a human |
| NT-DL-11 | CP killed at every point of the accepted (i) matrix | the states of [D §4.2.5-R5 (i)] hold; `ExecStart=` is never executed |
| NT-SG-1 | handler installation order | the handlers are installed before K, `grant.id`, the journal, AK-1, AM-1 and AM-2; a `SIGTERM` at every earlier point creates no grant |
| NT-SG-2 | AST scan of every handler | each assigns the flag and returns; no call, no raise, no write |
| NT-SG-3 | a flag set while each E wait is in progress | the wait observes it within `slice_ms` on a fake clock, kills and abandons its child and returns `interrupted` |
| NT-SG-4 | a `SIGTERM` delivered between the last flag check and PF-6 | at most a brief G1; IGR removes it; nothing else remains |
| NT-PK-1 | a fake `pkcheck` that hangs | each call is killed at c; no call starts after P; the series stops *waiting* by P + c + g |
| NT-PK-2 | a fake polkit that keeps answering `authorized` for P − ε, then `not authorized` | CQ-5 passes only on the first `not-authorized`; with latency > P it fails closed |
| NT-PK-3 | exit statuses 3, 126, 127 and a signal death | counted as `error`, never as `not-authorized` |
| NT-PK-4 | AP-0 with parameters that violate the §7.6 grammar | INVALID RUN; no lock object, no grant |
| NT-PK-5 | code scan | every loop on a PK or lock path carries a monotonic deadline; there is no unbounded `while` and no sleep-count bound |
| NT-PK-6 | `removed-verified` | requires AV-1's `authorized` in the same activation and a later `not-authorized` from the same procedure |
| NT-PK-7 | `grant-not-seen` | the rule is removed by CL and the activation ends with no pass |
| NT-PK-8 | the backstop under a permanently failing PK | disarms after B firings and leaves a journal line; no unbounded loop |
| NT-HS-1 | `spawn()` | rejects `env=None`, `shell=True`, a relative `argv[0]`, `preexec_fn`, a missing deadline |
| NT-HS-2 | a child of `spawn()` | inherits no descriptor and carries exactly the closed map |
| NT-HS-3 | deadlines | a child that outlives its deadline is killed, waited for at most g, abandoned, and the helper continues fail-closed |

---

## 8. The repaired activation design, integrated

This section restates the machines, windows, owners, records and invariants that
change. Everything not listed here stays as the accepted D3-R6 text states it
(§8.8). Rows marked **Δ** differ from the accepted text. Rows marked **Δ2** differ
from R1 as well, because of R2-F1 or R2-F2.

### 8.1 Three coordinated machines

**Machine H, the holder** (steps of [D §4.2.5-R2 (d)], with the §4 … §7 deltas):

| Step | Where | Action | Grant after | On failure |
|---|---|---|---|---|
| AP-0 **Δ2** | executor, unprivileged | as accepted, **plus**: PO-20 (f′), PO-21 (c′), (s′) and PO-11 (d′) accepted for the observed versions; the parameter grammar and sizing rules N1 … N4 of §7.6 evaluated (necessary conditions only); the digests of **every root-procedure image and `rp11_h1.py` (or its Route 3 successor)** equal the H-1 record's; `K` absent; the loaded unit's `ExecStartPre` normalized to the form the Route 3 outcome fixes; `T_s` finite; the backstop literal carries BS-RM | none | INVALID RUN; nothing mutated |
| AP-1 | executor | create the `ACT` evidence directory (consumes the identifier) | none | INVALID RUN |
| AP-2 **Δ2** | executor, privileged | issue the holder literal, which starts the holder through the first image the Route 3 outcome fixes. The executor then waits **at most `act_wait_s`** for the `act` record or the holder's end (§7.3 row 5) | none | as accepted; expiry is HARD STOP `act-unconfirmed`, acting on nothing |
| SG-1 **Δ2** | holder | the **first act**: install the handlers of the set H (§7.8). Nothing exists yet | none | a signal before this point ends the process with nothing created |
| AM-0 **Δ** | holder | (i) re-check `boot_id`, `/run` and every AP-0 absence condition, **K included**; (ii) create K by exclusive `mkdirat`, open it `O_CLOEXEC`, verify it, take `flock(LOCK_EX\|LOCK_NB)` (LD-1, LD-2); (iii) read the baseline under **BSP** (SD-1); (iv) create the journal and append `run-start {…, lock, capture, helper, params}` (§8.5) | none | exit non-zero; IGR is a no-op; CL |
| AK-1 **Δ2** | holder | append `backstop-intent`; issue the backstop literal (with BS-RM) through `spawn()`; require the timer `active`; append `backstop-armed {timer, period_s, max, runtime_s}`. No activation file exists before this commit | none | exit non-zero; CL |
| AM-1, AM-1R | holder | PT builds tree **P** (and tree **R**) | none | as accepted |
| AM-1G **Δ2** | holder | create `K/grant.id` (GI-1) with the staged rule's identity, **before** the link | none | exit non-zero; CL; no rule exists |
| AM-2 | holder | PF publishes the rule. **The flag is checked immediately before PF-6** (SG-4). **The grant is live from PF-6**, and the flag is checked again at the next statement | **G1** | exit non-zero; IGR; CL |
| AV-1 **Δ** | holder | both files re-verified; H-2b; **PK/2 seek-authorized for verb `start`** (P); **PK/2 first-decisive for verb `stop`** must be `not-authorized` (AR-7) | G1 | IGR; CL |
| AM-3 | holder | PF publishes `⟨activation_id⟩.act.json` (`activated`): **`ACT` PASS** | G1 | as above |
| `hold-start` **Δ** | holder | re-read per SD-1 (`τ = τ₀`, empty `Job`, quiescent); append `hold-start`; `fsync`; **close K** | G1 | OS-7: `hold-end {start-before-hold}`; IGR; CL |
| HL **Δ** | holder | observe every Δ without the lock. On a terminal reason: `LOCK_NB` on K once; re-observe; append `hold-end`; `fsync`; **close K**; exit | G1 → G2 | IGR on every catchable end |
| end **Δ2** | holder | **IGR** (§5.7: GRR, then one best-effort evidence line), then exit; then PID 1 runs `ExecStopPost=` CL if it can | G2 | RL ladder |

**Machine C, the capture unit's attempt** (CQ steps of [D §4.2.5-R5 (e)], deltas only):

| Step | Change | Why |
|---|---|---|
| CQ-0 | none | |
| CQ-1 **Δ** | opens **K** (derived from the `activation_id` of CQ-0) `O_CLOEXEC`, one `LOCK_EX\|LOCK_NB`. K absent or unopenable is `consume-unidentified` (nothing created) | LD-1, LD-8 |
| CQ-2, CQ-3 | none. CQ-3's grant-priority form and its removal are unchanged, and **CQ-3 keeps its accepted order after the claim** (GR-2 does not apply to it) | G1 |
| CQ-4 **Δ** | `τ = τ₀` is justified by SD-1 (no change to the check); K closed on every failure path | §6 |
| CQ-5 **Δ** | PK/2 **seek-not-authorized**, budget P; `unconfirmed` is `consume-failed {CQ-5, removed-unconfirmed}` | §7 |
| CQ-6 | none | |
| CQ-7 **Δ** | `run-end`, `fsync`, **close K**, exit `0` | LD-4 |

**Machine G, the grant object** (§3): `G0 → G1` at AM-2 (the only link, once);
`G1 → G2` at the first `unlinkat` of the rule by IGR, CL-G, CQ-3 or CL-3; `G2 → G3`
at the first PK/2 *not authorized* observed after that unlink in this activation
(CQ-5, CL-4 or attestation); `G1 → G4` if `unlinkat` fails (GU). `G1`/`G2`/`G4 → G0`
at the next kernel boot. **Cross-machine invariant:** the capture unit's state does
not pass from **A** to **R** (the `ExecStart=` `execve`) unless the grant state is
**G3** for this activation (CQ-3 and CQ-5 order).

**CL deltas** (in [D §4.2.5-R2 (h)] and [D §4.2.5-R3 (e)]):

| Step | Change |
|---|---|
| **CL-G Δ2** | **new first act**: GRR with the identity of `grant.id` (§5.7), before the lock attempts, the attempt directory and the journal. `identity-unavailable` falls back to CL-3 as accepted |
| CL-0 **Δ** | the lock is K, acquired by non-blocking attempts until the `lock_wait_ms` deadline. On expiry or `K` unopenable, **degraded mode** records `lock_mode` and continues. **`lock-timeout` is withdrawn** |
| CL-3 **Δ** | an ACT-journal `igr` line with outcome `removed`, or a `cl-g {removed}` result for the rule's identity, is class `removed-earlier`; a rule absent with neither is `absent-before-removal`. The rule's removal does not require the lock (GR-1) |
| CL-4 **Δ** | PK/2 seek-not-authorized, budget P |
| CL-5b **Δ2** | also removes **`grant.id` and then K**, last among the `/run` objects, through a descriptor re-verification against the journaled identity, only if K holds nothing else. A K without an identity line is **S0** |
| CL-6 **Δ2** | as accepted. Its `baseline` recomputation is the largest local job in CL and is class X (§7.3, row 9). It uses CL-4's PK result and runs `show` under a class-E deadline |
| CL-7 | `st1-verified` additionally requires `lock_mode` to be recorded |
| BS-4 **Δ2** | at most `backstop_max` firings run CL; the next firing disarms the timer, appends a journal line and exits non-zero. BS runs CL in degraded mode if K cannot be acquired. **Each firing is ended by BS-RM** |

### 8.2 Authority windows

| Window | Opens | Closes | What A-2 permits | Grant | Bound, and its class |
|---|---|---|---|---|---|
| **AW-0**, preparation | AP-0 | AP-2 | unprivileged reads; AP-1 | none | none needed |
| **AW-1**, baseline | SG-1 | AK-1's commit | holder only | none | BSP at most 5 re-reads (C); each read a class-E wait. The holder's life is bounded by L (M) |
| **AW-2**, grant window | AM-2's PF-6 | the first unlink of the rule (IGR, CQ-3, CL-G or CL-3) | the operator's single `start`, **only after `hold-start`** and while the holder is `active` | **G1**: `start` only, for `ubuntu` | **W (start window) and the lease L, enforced by PID 1 (M), IL′.** No helper timing is claimed |
| **AW-3**, visibility lag | that unlink | the first PK/2 *not authorized* | nothing new. A start in this window reaches CQ-2 and is refused if a claim exists, or runs CP, which re-verifies | **G2**: polkitd may still authorize | PK/2 waits end by P + c + g (E) at each use. **No claim about Polkit** |
| **AW-4**, consume | the accepted `start` job | CQ-7 | CP only | G1 → G2 → G3 | the unit's start timeout T_s (M). CP's own elapsed time is not claimed |
| **AW-5**, pass | `ExecStart=`'s `execve` | the main process's end | route (iii-a) only under OC-1 … OC-3 [D §4.2.5-R6 (b)] | **none** (G3) | no bound is claimed by this design |
| **AW-6**, cleanup | the holder's end (or IGR) | the terminal `deact` record, or `attest` | CL in every trigger; IGR | G2/G3 | the rungs RL-0 … RL-5, **ordered and not timed**; each process by its class-M terminator (§7.4) |

### 8.3 Recovery ownership

Who must return each state to ST-1, in order. The first owner is the first rung of
RL (§5.3) that acts. §7.9 maps the interruption points of each procedure to these
rows.

| State | What is undone | First owner | Then | Last |
|---|---|---|---|---|
| ST-1.a0 (K, journal, backstop armed) | K, tree directories, backstop | IGR (nothing to remove) → stop-post CL | backstop | boot, `attest` |
| ST-1.a1 (tree **P**, `grant.id`) | `pass-a.json`, tree **P**, `grant.id`, K | stop-post CL | backstop | boot, `attest` |
| ST-1.a2, ST-2 (rule live) | the rule first, then the rest | **IGR** | stop-post CL (CL-G); backstop; CP at any start | boot |
| **ST-1.i** (holder gone, rule live, inert) | the rule | stop-post CL (CL-G) | backstop; CP at any start (CQ-3) | boot |
| ST-2.c, ST-2.f | the rule if CP did not | CP (CQ-3) | CL (HL's reason, rule first) | boot |
| ST-3 | `pass-a.json`, records (**no** grant) | CL after HL observes the pass end | backstop | boot |
| ST-1.d1, ST-1.ur, ST-1.bc, ST-1+R | as accepted | as accepted | as accepted | as accepted |

**ST-1.i** is the only new state: activation objects present, holder not `active`
or `hold-end` journaled, rule live. It is **inert** (IL, §5.4), entered by a
holder's end before the rule's removal completes, and left by IGR, CL-G, CQ-3 or
the boot.

### 8.4 The states table, deltas

| State | Activation objects present | Grant | Entered by | Left by |
|---|---|---|---|---|
| ST-1.a0 **Δ** | holder `active`, backstop armed, **K**, `ACT` journal; no activation file | none | AK-1 | AM-1, or the holder's end |
| ST-1.a1 … ST-3 | as accepted, with **K** (and `grant.id` from AM-1G) present throughout | as accepted | as accepted | as accepted |
| **ST-1.i** | as ST-1.a2 or ST-2, holder not `active` | G1 **inert** | the holder's end | the rungs of §8.3 |

### 8.5 Evidence records and journals

`rp11-activation-record/2` was never implemented, so its additive amendment below
needs no new schema number.

| Key | Content (amended) |
|---|---|
| `lock` | `{object: {path, dev, ino} or "absent", mode: "held"\|"degraded"\|"absent", wait_ms}` (§4.9) |
| `grant_identity` | `{source: "grant.id"\|"journal"\|"memory", conflict: bool}` (GI-1) |
| `pk` | `{procedure: "pk-root/2", mode, op_ms, call_ms, reap_grace_ms, calls, abandoned, elapsed_ms, outcome, reason}`, replacing `grant_check.bound_ms`. `elapsed_ms` is **observed**, never a claim |
| `release` | `{first_rung: "igr"\|"cl-g"\|"stop-post"\|"backstop"\|"cp"\|"boot"\|"absent", igr: outcome or "absent"}` |
| `capture` | `{active_state, invocation_id, inactive_enter_us, m_a_us, bsp_retries}` at AM-0; `{…, inactive_enter_us}` at `hold-start` and at CQ-4 |
| `helper` | `{role, image_sha256: [one digest per root-procedure image the Route 3 outcome installs], tool_sha256}` |
| `params` | the §7.6 values and `T_s` as recorded in the H-1 `baseline`, with `sizing: "necessary-conditions-met"` (never "bounded") |
| failure classes **Δ2** | add `lock-object`, `capture-baseline-unstable`, `grant-not-seen`, `stop-control-unconfirmed`, `act-unconfirmed`, `invalid-journal`; **withdraw** `lock-timeout`. `identity-conflict` is a recorded condition, not a failure |

The `ACT` journal's closed `op` set gains `igr` and the CL attempt journal's gains
`cl-g`. The consume journal's and each CL journal's `run-start` carry `lock` and
`helper`. Journals, digests and the OH-D-9 return path are unchanged.

### 8.6 Invariants

| ID | Invariant | Where it is checked |
|---|---|---|
| INV-1 | `ExecStart=` runs only after CP exits `0`, which needs CQ-3's journaled removal and CQ-5's *not authorized* within P | NT-PK-2, NT-RL-7 |
| INV-2 | contract OSA over 𝒜 without exception; CX-4 void (§6.8) | NT-SD-3, -9 |
| INV-3 | the rule is linked once, by AM-2, after a BSP baseline and after `grant.id` | AM-0 and AM-2 order tests |
| INV-4 | no safety property cites the lock **or any elapsed time** | the §2.1 table; NT-LD-6; NT-DL-4 |
| INV-5 | no lock of the activation chain is on an object a non-root actor can open | NT-LD-4, -5 |
| INV-6 | no process is designed to end holding a lock; every lock has an explicit close point | NT-LD-3, -8 |
| INV-7 | grant removal by IGR and CL-G waits for no lock, no spawn, no `ext4` write and no Polkit, and **precedes every one of them** (GR-2) | NT-LD-6, NT-RL-1 |
| INV-8 | every wait, poll and retry has a deadline of class E, M or C and a defined consequence. Class-X work is stated as unbounded | NT-PK-5, NT-DL-3, NT-RL-4 |
| INV-9 | a PK `unconfirmed` is never evidence of absence | NT-PK-3, -6 |
| INV-10 | SD compares only with the journaled baseline, and BSP held | NT-SD-1, -2, -10 |
| INV-11 | **conditional on Route 3:** the helper-start contract RH-1 … RH-3 holds for every root procedure | the tests that the chosen Route 3 outcome defines (§9.2). Not testable until that outcome exists |
| INV-12 | every child of a root helper is created by `spawn()` with the closed map and `close_fds` | NT-LD-3, NT-HS-1 … 3 |
| INV-13 | `removed-verified` needs a journaled removal (CQ-3, CL-3 or IGR) or a `cl-g` result, `ENOENT` and a *not authorized* from the procedure that returned *authorized* in this activation | NT-PK-6 |
| INV-14 | records state `lock`, `grant_identity`, `pk`, `release`, `capture` and `helper` | schema tests |
| INV-15 | any drift of a bound version or digest is INVALID RUN before any lock object or grant exists | AP-0 tests, §9.12 |
| INV-16 | **every elapsed-time statement names its class and its enforcer.** A sum of class-X operations is never stated as a bound, and a sizing rule is never recorded as one | NT-DL-4, NT-DL-5 |
| INV-17 | the handlers are installed before any state operation and only set a flag; IGR runs from one site, once, and cannot be re-entered | NT-SG-1, -2, NT-RL-9 |
| INV-18 | every procedure's interruption at any point maps to a state and a first owner (§7.9) | NT-DL-10, -11, NT-RL-10 |

### 8.7 Where the tests land

The accepted successor table numbers OH-S4's tests up to (29). This proposal adds,
without renumbering any accepted test: **(30)** NT-LD-1 … 10; **(31)** NT-RL-1 … 13;
**(32)** NT-SD-1 … 10; **(33)** NT-PK-1 … 8, NT-DL-1 … 11 and NT-SG-1 … 4;
**(34)** NT-HS-1 … 3, plus the NT-RH tests that the chosen Route 3 outcome defines;
**(35)** the PO-17 matcher over every launcher image the chosen outcome includes and
the recorded HF-14 entry. OH-S8b's drills gain only what a real host can safely show:
route (iii-a) is unchanged; `SIGTERM` of a test holder showing IGR before exit;
`SIGKILL` of a test holder showing the live-inert state and its removal by the
stop-post; a test unit with `TasksMax` too small is **not** proposed, because PID 1
spawn failure is a model-only case (NT-RL-2, NT-RL-3).

### 8.8 What stays exactly as accepted

The unit and rule bytes (apart from the `ExecStartPre=` program, which the Route 3
outcome fixes, and the backstop literal's BS-RM change); SB-1, SB-2 and SB-3; CQ-0,
CQ-2, CQ-3, CQ-6; the claim's publication, blocking and durability points; the
grant-priority form of CQ-3; GP-R3's principle and ST-1.ur; route (iii-a) and OC-1
… OC-3; OS-1, OS-4, OS-5's decision rule, OS-7, OS-8; `hold-start`'s durability;
A-2's pins other than the additions of Appendix A; M-B and M-S; the AC-1 … AC-9,
AC-12 rows; the attribution classes, PF, PT, G-R1, RS-1 and RB-1; ST-1+R; DF-1,
SL-1, GU; HF-facts other than the rows named in Appendix A.

---

## 9. Route 3: the accepted boundary, why a concrete design is not established, and the exact alternatives

### 9.1 The accepted Route 3 boundary, and what R1 did to it

**The accepted definition.** DR1 §5.3 compared three routes. Route 3 is *"abandon
the Python-dependent route"*: *"the entry bootstrap, capture mechanism, CP, holder,
backstop and CL must be re-implemented without Python, or RP-11's one-host design is
withdrawn."* It adds that its security "depends on the replacement. Likely a larger
trusted computing base, written new", that it is "a long redesign", and that review
is "a new design cycle". [R3 §6.3] (accepted) records that **Peter decided Route 1
(D-3)** and that *"Route 3 remains the destination only if OH-S2 refutes PO-12 or
PO-19 for 3.14."* The accepted OH-S2 R2 record refutes PO-12 and AS-8 [R2 §10.4], and
the acceptance states: *"Route 1 returns to Route 3 design review because PO-12 and
AS-8 are refuted."*

**The working restatement.** The R2 assignment states the boundary this proposal
must restore: *the root procedures that touch the grant and activation mechanism do
not run through CPython or a dynamic loader.* No prior record changes it. A search of
the named accepted documents found no §0.2 change, and the decision register and
change log are not edited here.

**Two readings, not decided here.**

| | **R3-ROOT** (the R2 assignment's restatement; this proposal's working boundary) | **R3-DR1** (the verbatim wording of DR1 §5.3) |
|---|---|---|
| Procedures that must be Python-free | the root procedures that touch the grant and the activation mechanism: CP, the holder (ACT, HL, IGR), the stop-post, the backstop, `attest`. Whether the installer class (H-1, RB-1, RS-1) is among them is **BQ-3** | the entry bootstrap, the capture mechanism, CP, the holder, the backstop and CL |
| Dynamic loader | absent from those procedures **including every child they start** (LR-2) | implied: the Python-dependent route is abandoned |
| The entry (run as `ubuntu`, `python3.14` under the C11 launcher) | **stays Python**. PO-12′ and PO-19 still bind it | Python-free as well |
| Source | the R2 assignment, finding R2-F1 | DR1 §5.3, accepted through R3 §6.3 |

This proposal applies R3-ROOT because the authorizing assignment states it. It
**neither narrows nor widens** the accepted boundary. If a maintainer treats R3-ROOT
as a *narrowing* of DR1 §5.3, adopting it is a scope question for §0.2, and I record
it as **BC-2** (§12.2). Everything in §9 is written so that it stays true under either
reading, and §9.8 and §10 give both.

**What R1 did.** R1's scoping note (R1 §9.1) read "Route 3 design" as *"the
replacement of Route 1 … defined by the elimination of the ambient inputs … and not
by the removal of Python"*. It treated DR1's literal Route 3 as an alternative
(RT3-C) and rejected it as "not decision-ready", it recommended RT3-A, and it asked
Peter to confirm the re-scoping in DEC-1. **That is a scope change presented as a
design choice.** A static first image closes inherited environment and descriptors.
It does not remove the interpreter, the dynamic loader or their file-based inputs
from the root path. R1's recommended RT3-A therefore did **not** meet the authorized
Route 3 boundary. R1 stays unchanged and unaccepted. In this record RT3-A is renamed
**`STATIC-SCRUB-WRAPPER` (SSW)** and described in §9.7 as a scope-change alternative.

### 9.2 What any outcome must deliver: the helper-start contract RH and the literal criteria LR

**RH-1 … RH-3** describe what a root procedure's *first image* must establish. They
are the part of R1's Route 3 that is **independent of the Python question** and that
the activation design (§§4 … 8) relies on.

* **RH-1, environment.** No environment string reaches any image of a root procedure
  except reviewed literals (and, where the accepted design reads it, the 32-hex
  `INVOCATION_ID` selection of [D2 §5.6]).
* **RH-2, descriptors.** Descriptors 0, 1 and 2 are checked, and every descriptor ≥ 3
  is closed before the procedure's first state operation.
* **RH-3, process state.** Signal dispositions are reset and the mask cleared, `umask`
  and the working directory are fixed, where the unit configuration does not already
  fix them. Limits, `no_new_privs`, capabilities, seccomp, cgroup, scheduling and
  timers are **not touched and not claimed** (R-10, K-5).

**Status today.** RH-1 is **not met** for the root roles: [R2 §10.4, §15.4 (X-1)]
refuted the premise that `python -I -S` under PID 1's open block starts cleanly. RH-2
is not established for them either. The accepted dispositions are unchanged: PO-12
and AS-8 are refuted, and Route 1 returns to Route 3 design review.

**LR-1 … LR-6, the literal criteria.** A concrete Route 3 under R3-ROOT is one in
which, for every root procedure *p* of §9.1:

* **LR-1.** No CPython runs in *p*'s process tree.
* **LR-2.** No dynamic loader runs in *p*'s process tree. Every image *p* executes,
  including every child, is statically linked, or *p* performs that function itself.
* **LR-3.** RH-1 … RH-3 hold for each image of *p*.
* **LR-4.** Every function that *p* delegates to a child today (§9.3, DI-1 … DI-6) is
  performed in-process, or by an interface that is itself loader-free and cited.
* **LR-5.** The behaviour of the accepted procedures (CQ-0 … CQ-7, CL, IGR, GRR, PK/2,
  BS, SD, LD) is preserved, each by a stated mapping from the old step to the new one.
* **LR-6.** Each image passes the D9 chain and PO-17 (§9.10).

LR-1 and LR-2 are the criteria RT3-A fails. They are why it cannot be Route 3.

### 9.3 Evidence assessment: why no concrete Route 3 is established

**What the root procedures delegate today.**

| # | Function | Today's mechanism | Used by |
|---|---|---|---|
| DI-1 | unit state reads (`ActiveState`, `InvocationID`, `InactiveEnterTimestampMonotonic`, `Job`, `LoadState`, `Result`, `TimeoutStartUSec`, `DropInPaths`, …) | `systemctl show -p …` through `spawn()` | holder (BSP, HL, `hold-start`), CP (CQ-4), CL (CL-2, CL-6), BS-1 |
| DI-2 | creating the transient holder unit | `sudo -n /usr/bin/systemd-run` by the executor | AP-2 |
| DI-3 | creating the backstop service and timer | `/usr/bin/systemd-run` by the holder | AK-1 |
| DI-4 | disarming the backstop timer | `systemctl stop ⟨id⟩-backstop.timer` | BS-2, BS-3 |
| DI-5 | the Polkit decision | `/usr/bin/pkcheck` | AV-1, CQ-5, CL-4, GP-R3, attestation |
| DI-6 | the authorization subject | `/usr/bin/sleep 60` under `ubuntu`'s credentials | PK/2 |

`/usr/bin/systemctl` is recorded as dynamic [D §4.1.3, TR-4]. The linkage of
`systemd-run`, `pkcheck` and `sleep` is recorded by **no accepted record** (it is the
optional fact MF-9). Distribution binaries of those packages are expected to be
dynamic, and that expectation is not a fact.

**What a literal Route 3 needs, and what the repository holds.**

| # | Need | Repository evidence | Gap |
|---|---|---|---|
| E-1 | the **definition** of every root procedure | present: the accepted design through D3-R6 and this record define CP, the holder, CL, IGR, GRR, BS, PK/2, SD and LD completely | none for *what* is to be re-implemented |
| E-2 | a **loader-free interface** for DI-1 … DI-5, with version-bound citation | the accepted R2 record cites **server-side** behaviour: `StartTransientUnit` refusal semantics ([R2 §8 (m)]), the `StartUnit` and Polkit-check flow ([§8 (p), (q)]), property vtables and `GetAll` ([§4]), `CheckAuthorization` detail restrictions ([§6.3]), and `pkcheck`'s exit statuses ([§6.4 (e)], a command-line contract). **No accepted record cites a client-side contract**: the bus address and authentication, message marshalling, the argument structures of `StartTransientUnit` (including the `ExecStopPost=` and timer properties), the Polkit subject structure, error mapping, or how a static image obtains decisions equal to `pkcheck`'s. A fixed-string count of SASL, marshalling, wire format, wire protocol, the private systemd socket and the system-bus socket over the R2 record, the one-host design, D2 and the R3 proposal returned a single hit: TR-4's mention of the system-bus socket path | **Gap 1**: interface contract and its citation |
| E-3 | a **proof method** for a static image with a larger system-call inventory | D2 and D9 proved the closed nine-call launcher. [R2 §12] **refuted AD-8 as a general statement** and established it **only for that closed inventory** (a system call can return `EINTR` with no handler). A root image needs sockets, directory and file operations, `flock`, `fsync`, `renameat2`, `linkat`, `unlinkat`, a clock and, for DI-6, process creation. None of their blocking or `EINTR` behaviours is cited | **Gap 2**: restated proof method and citations |
| E-4 | a **boundary** for procedures that `sudo` starts (`attest`, AP-2's `sudo systemd-run`, and the installer class) | `sudo` and `systemd-run` are dynamic root processes that run before any image the procedure controls. The accepted text treats `sudo`'s environment as an OH-D-6 consistency limit (HB-1). That is a boundary statement, not evidence | **Gap 3**: BQ-2 and BQ-3 |
| E-5 | **size and effort** | none. R1 states that "the repository holds no measure of their size", and DR1 says "a long redesign" and "a new design cycle" | **Gap 4**: an estimate |
| E-6 | which **reading** binds | R3-ROOT or R3-DR1 (§9.1) | **Gap 5**: BQ-1 |
| E-7 | a prior **§0.2 decision** that changes the boundary | none found in the named accepted documents | confirms that **no scope change exists** |

**Conclusion.** A concrete Route 3 is **not established**. That is not a finding that
it is impossible. Defining it needs an interface contract, a proof method and a
boundary the repository does not hold, and the assignment forbids inventing them. The
terminal state is therefore **`HARD STOP: concrete Route 3 not established`**.

**Four boundary questions** that the work of §9.5 must settle first. None is decided
here, and none is a design choice.

* **BQ-1.** Does R3-ROOT or R3-DR1 bind (is the `ubuntu`-run entry in scope)?
* **BQ-2.** For a procedure that `sudo` starts, where does "the root procedure" begin:
  at the first image the procedure controls, or at `sudo`? Treating `sudo`'s own loader
  as outside the procedure is an exception to LR-2 and needs to be stated as one.
* **BQ-3.** Is the installer class (H-1, RB-1, RS-1: the `sudo -n python3.14 -I -S -c`
  verified-exec stub, HB-1) among the "root procedures that touch the … activation
  mechanism"? They install and remove the files the mechanism consists of.
* **BQ-4.** Are dynamic *children* of a static root image excluded by LR-2, or
  excepted? An exception is **SCDC** (§9.4), which is a scope change.

### 9.4 The exact bounded alternatives

| ID | What it is | Meets the accepted Route 3? | Decision-ready? | Baseline decision needed before it could be selected |
|---|---|---|---|---|
| **LIT-FULL** | the root procedures re-implemented as static images that perform DI-1 … DI-6 in-process or by a cited loader-free interface; no dynamic child; the entry stays Python (R3-ROOT) | **yes** (LR-1 … LR-6) | **no**: needs WP-1 … WP-7 | none beyond Peter's choice after readiness. If BQ-2, BQ-3 or BQ-4 are answered by an *exception*, that exception is a §0.2 change |
| **LIT-DR1** | LIT-FULL **plus** a Python-free entry bootstrap and capture mechanism (R3-DR1) | **yes**, under the wider reading | **no**: needs WP-1 … WP-8 | none; the largest |
| **WITHDRAW** | RP-11's one-host design (or its activation part) is withdrawn, the second limb of DR1 §5.3 | **yes**: it is in the accepted definition | n/a | Peter's decision. Its effect on the Phase 5 RP-11 plan is outside this record and may itself need §0.2 |
| **SSW**, `STATIC-SCRUB-WRAPPER` (R1's RT3-A) | a static environment-ignoring first image in front of `python3.14 -I -S` for CP, the holder, the stop-post, the backstop and `attest` | **no. A scope-change alternative.** It leaves CPython, the dynamic loader and their file inputs in the root path (fails LR-1, LR-2, LR-4) | **yes, as an alternative** (§9.7) | **§0.2**: amend the accepted Route 3 boundary to "closed environment and descriptors; CPython and glibc remain; file inputs bound by MF-1, MF-2, MF-4 and the drift gates" |
| **SCDC**, `STATIC-CORE-DYNAMIC-CHILDREN` (R1's RT3-B) | the helper logic as freestanding C, with `systemctl`, `systemd-run`, `pkcheck` and `sleep` still dynamic children | **no**: the dynamic loader stays in the root path through its children (fails LR-2, LR-4) | **no**: needs WP-2, WP-4, WP-5, WP-6, MF-9 | **§0.2**: except the dynamic children from the boundary |
| **ACCEPT-X1** (R1's RT3-Z) | no new image: accept X-1 as an explicit root-ambient residual and bind PO-12′ and PO-19 for the entry only | **no**: PO-12 stays refuted for the root roles, and the accepted disposition "Route 1 returns to Route 3 design review" is left unanswered for them | **yes** (no code) | **§0.2**, and Peter's explicit residual acceptance under OH-D-6 and R-10. *Nuance:* [R2 §15.4] frames X-1 as "a design decision, not a citation: whether the activation design accepts this under OH-D-6/R-10 or needs these processes to start from a literal environment". Whether accepting it is a design decision within existing authority or a change of the Route 3 boundary is **not decided here**. Until a maintainer rules otherwise this record treats it as a change |

Rejected, for the reasons R1 gave and that stand: **unit-level scrubbing** (`UnsetEnvironment=`
removes only named variables from the assembled block [R2 §3.1 P14-3]; the set of
harmful names is open-ended; the reviewed unit admits none of these lines, T-B1);
a **dynamic wrapper** (`env -i`, a shell), whose own loader reads `LD_*` and the
tunables before any user code [R2 §11.3]; a **private pinned interpreter**, for which
the repository holds no source, recipe or provenance and which would need network
research and a new trust root.

**None of SSW, SCDC and ACCEPT-X1 is described anywhere in this record as satisfying
literal Route 3.** This record makes no recommendation among the six. It states one
observation, for the reviewer and not as a recommendation: of the alternatives that
do not meet the accepted boundary, SSW introduces the least new code, and of the
alternatives that do, WITHDRAW introduces none. Neither fact selects anything.

### 9.5 The work that would make literal Route 3 decision-ready

Each package is **repository-only unless stated**, needs its own prompt, authority,
work ID and Codex review, and is **not requested or authorized here**. The order is a
dependency order.

| WP | Work | Output | Needs |
|---|---|---|---|
| **WP-1** | settle BQ-1 … BQ-4 | a boundary record stating which procedures are in scope, where each begins, and whether any exception is requested. An exception is a **BC** (§12.2) | Peter, with Codex review. Documentation |
| **WP-2** | inventory every operation of every in-scope procedure at system-call intent, from the accepted procedures and this record | an operation table (the §7.3 inventory extended to every call) | derived from accepted text. Documentation |
| **WP-3** | the loader-free interface contract for DI-1 … DI-5 (and DI-6): what a static image sends and receives, and which accepted semantics each rests on | proposed obligations with version-bound citations for `systemd 259.5-0ubuntu3.4` and `polkit 127-2ubuntu1.1` | a **citation slice** of the OH-S2 class (U-10). It must name its authorized sources. **No network research is authorized** by anything here |
| **WP-4** | the static-image design: language class, system-call inventory, blocking and `EINTR` analysis (AD-8 restated over the larger inventory), memory and stack bounds, parsing, a SHA-256 and canonical-JSON implementation with test vectors | a D2-class design for each image | after WP-2 and WP-3. Documentation |
| **WP-5** | the proof method and evidence plan: D9-1 … D9-4 extended, independent decoding (XD) for larger images, reproducible-build reuse, PO-17 per image | a plan, not the evidence | after WP-4 |
| **WP-6** | the equivalence mapping: each accepted step to its new step, each accepted negative test to its image-level counterpart, and every behaviour that cannot be preserved, restated | a mapping table | after WP-4 |
| **WP-7** | a size and review-cost estimate | a recorded estimate, so that Peter's choice is informed | after WP-4 |
| **WP-8** | only for R3-DR1: the Python-free entry bootstrap and capture mechanism | a design of the same kind | after WP-1 settles BQ-1. The largest item |
| **WP-9** | the decision record | Peter's choice among LIT-FULL, LIT-DR1, WITHDRAW and, **only after a §0.2 change**, any scope-change alternative | after WP-1 … WP-7 (or WP-8) and Codex review |

Without WP-3 and WP-4 no static image can be specified without inventing the protocol
it speaks and the system calls it needs. That is the content of the hard stop.

---

### 9.6 The corrected executable and runtime boundary, and the Role A–H inventory

#### 9.6.1 Boundary, role by role

"Accepted today" is the accepted text, which **names `/usr/bin/python3.12`**, a
literal that the accepted R3 record already marks for replacement. Route 1's
replacement by `/usr/bin/python3.14` is refuted for the root roles (X-1) and so is
**not** a boundary. The LIT-FULL column is the *requirement* of §9.2, not a design:
what the static images are, and how they perform DI-1 … DI-6, is exactly what is not
established. The SSW column is the scope-change alternative of §9.7.

| Role | Started by | Accepted today (refuted for root roles) | **LIT-FULL** (R3-ROOT; requirement only) | **SSW** (scope change; §9.7) |
|---|---|---|---|---|
| **entry** | PID 1, capture unit `ExecStart=` | `rp11-launch` (static, `ubuntu`, NNP), then `python3.12 -I -S …/rp11_entry.py`, environment `rp11-entry-env/1` | **unchanged in kind**: `rp11-launch`, then Python as `ubuntu` (R3-ROOT). The literal retarget to the accepted `python3.14` remains. Under LIT-DR1 the entry is Python-free and A1 … A5 are obsolete | `rp11-launch` retargeted by one literal; `python3.14 -I -S`; `rp11-entry-env/1` |
| **consume** (CP) | PID 1, `ExecStartPre=+` | `python3.12 -I -S …/rp11_h1.py consume` under PID 1's open block | a static image performs CQ-0 … CQ-7 and DI-1, DI-5, DI-6 itself; RH-1 … RH-3 | `rp11-rootexec consume`, then `python3.14 -I -S …/rp11_h1.py consume` under `rp11-helper-env/1` |
| **hold** | PID 1, the transient holder | `python3.12 -I -S …/rp11_h1.py hold ⟨id⟩ ⟨a2⟩` | a static image performs the holder, IGR, GRR and DI-1, DI-3, DI-5, DI-6 itself | `rp11-rootexec hold ⟨id⟩ ⟨a2⟩`, then `python3.14` |
| **stop-post** | PID 1, `ExecStopPost=` | `python3.12 -I -S …/rp11_h1.py deact ⟨id⟩ ⟨a2⟩ stop-post` | a static image performs CL and DI-1, DI-5, DI-6 | `rp11-rootexec stop-post …`, then `python3.14` |
| **backstop** | PID 1, the timer's service | `python3.12 -I -S …/rp11_h1.py backstop ⟨id⟩ ⟨a2⟩` | a static image performs BS, CL and DI-1, DI-4, DI-5, DI-6 | `rp11-rootexec backstop …`, then `python3.14` |
| **attest** | the executor, `sudo -n`, interactive | `sudo -n python3.12 -I -S …/rp11_h1.py deact ⟨id⟩ ⟨a2⟩ attest` | **BQ-2**: a static image after `sudo`, with `sudo`'s own loader an explicit, stated exception, **or** another start path | `sudo -n …/rp11-rootexec attest …`, then `python3.14`, `rp11-helper-env/1a` |
| **H-1, RB-1, RS-1** (installer class) | the executor, `sudo -n` | `sudo -n python3.12 -I -S -c ⟨verified-exec stub⟩ …` under `sudo`'s environment | **BQ-3**: in scope (a Python-free installer is then a new WP) or out of scope, stated as an exception with the HB-1 residual | `python3.14 -I -S -c …` under `sudo`'s environment: **HB-1** residual |
| **helper children** (DI-1 … DI-6) | `spawn()` of a root helper | dynamic distribution binaries under the closed map `{LC_ALL=C, PATH=/usr/bin}` | **none** (LR-2): each function is in-process or by a cited loader-free interface (WP-3) | unchanged: dynamic children under the closed map. Their file-level loader inputs are MF-9 |

#### 9.6.2 Inventory of every Role A–H occurrence, and its disposition

Line references are the **current** lines of the cited files, as found by fixed
searches of those named files and compared with R1's (they agree). "Applied by" names
the slice that would apply the row. **None is applied here.** The LIT columns apply
only if Peter later chooses a conforming alternative; the SSW column only after a §0.2
decision.

**Role A, executed literals.**

| # | Location | Text | **LIT-FULL** | **SSW** | Applied by |
|---|---|---|---|---|---|
| A1 | `infra/rp11-launch/launch.c:207`, `:221` | `argv_out[0]` and the `execve` path `/usr/bin/python3.12` | retained: `/usr/bin/python3.14` for the entry, **the only source delta of the entry image** (R3-ROOT). Obsolete under LIT-DR1 | as LIT-FULL | OH-S4p |
| A2 | `rp11-launch.x86_64.listing:412–413` | `.rodata` bytes `/usr/bin/python3` `.12` | regenerated by the rebuild, never hand-edited | as LIT-FULL | OH-S4p |
| A3 | image `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572` and every pin of it (`rp11_launch.py`, `expected.sha256`, `tools/r5_runner/blocks/s08.sh`, design §4.2.4 P-0 and §4.5.2, IA-8) | the compiled literal | a new reviewed digest for the entry, **plus** a digest set for every static root image | the entry's new digest **plus** the four digests of the wrapper image | OH-S4p |
| A4 | `tools/phase_5_0_evidence/rp11_launch.py:47`, `:49` | `EXECVE_PATH`, `EXECVE_ARGV[0]` | `/usr/bin/python3.14`; **plus** a contract per static root image | `/usr/bin/python3.14`; plus a contract for the wrapper's five vectors | OH-S4p |
| A5 | `docs/review/phase-5-0-evidence-harness-review-manifest.json:2732`, `:2744`, `:2824`, `:2841` | `rp11_launch` `execve_argv`, `execve_path`, `execve.argv`, `execve.path` | `/usr/bin/python3.14` in a new manifest version, **plus** a contract per static root image | the same, plus the wrapper contract | OH-S4p |
| A6 | design `:2857` (also `:228`, `:2481`, `:2509`, `:5242`, `:6979`) | `ExecStartPre=+/usr/bin/python3.12 -I -S …/rp11_h1.py consume` | **replaced** by the static CP image's path (fixed by WP-4). No Python literal remains for CP. T-B1 admits exactly that line | `ExecStartPre=+/usr/local/libexec/freedom-blades-rp11/rp11-rootexec consume` | OH-S0d (text), OH-S4 (tests) |
| A7 | design `:1257` | `sudo -n /usr/bin/python3.12 -I -S -c '⟨verified-exec stub⟩' …` | **BQ-3**: `/usr/bin/python3.14` with the HB-1 residual stated, or a Python-free installer | `/usr/bin/python3.14` under HB-1 | OH-S0d, OH-S4 |
| A8 | design `:1996`, `:1997`, `:2016`, `:2147` | the holder's `ExecStopPost=`, the holder command, the backstop command and the attest command | **replaced** by the static images' paths. The backstop literal also gains BS-RM (§7.4) | the wrapper literals of §9.7, with BS-RM | OH-S0d, OH-S4 |
| A9 | design `:3124` | the `ExecStartPre` normalization (`path`, `argv[0]`) | path and `argv` of the static CP image, `+` flag | path `…/rp11-rootexec`, `argv` `[…/rp11-rootexec, "consume"]`, `+` flag | OH-S0d, OH-S4 |
| A10 | C11 `:688`, `:903–904`; D2 `:436`, `:1256`, `:1258`, `:1567–1568` | the entry's `execve` contract | a dated amendment note naming `/usr/bin/python3.14` for the entry; **plus** a dated D2 addendum for every added image | the same, for the wrapper | OH-S0d |

**Role B, trust-path and proof-obligation statements.**

| # | Location | **LIT-FULL** | **SSW** |
|---|---|---|---|
| B1 | design TR-9 `:945` | `/usr/bin/python3.14 -I -S` for the **entry** only. **New rows** for each static root image in place of the Python rows for the root roles | the entry as LIT-FULL; **new row TR-6a′** for the root roles (the wrapper first, then the interpreter) |
| B2 | design PO-19 (a) `:4497` | restated for the **entry's** interpreter and closure | restated, six consumers (§9.8) |
| B3 | C11 PO-12 and AS-8 (`:456`) | **refuted** for CPython 3.14.4 [R2 §10.4]; PO-12′ restated for the entry | as LIT-FULL, with the root roles added |
| B4 | C11 M-5; design M-5 `:5154` | the entry interpreter `/usr/bin/python3.14`; **plus** every installed static root image as a root-owned `0755` regular file pinned by digest | as LIT-FULL, for the wrapper |
| B5 | C11 descriptive text (`:62`, `:281`, `:514`, `:576`, `:598`, `:619`, `:809`, `:941`, `:1748`) | a dated C11 amendment note for the entry. The withdrawn LB-2 and LB-3 rows and change records (`:226`, `:798`, `:1019`, `:2529`, `:2533`) stay as history, unchanged | the same note, **plus** that the root roles start through the wrapper |
| B6 | U-9 decision | **unchanged**. Its consumers narrow by the obligation text, which is itself a scope matter only if BQ-1 reads R3-ROOT as a narrowing (BC-2) | unchanged; the narrowing is **not** achieved by DEC-1 |

**Role C, H-0 facts and command classes.**

| # | Location | **LIT-FULL / SSW** |
|---|---|---|
| C1 | HF-06, HF-07, HF-08, HF-10 (`:4436–4440`), C-VER (`:4472`) | **unchanged by Route 3**: the `python3.14` rows are already observed by H-0G in the accepted composed H-0. The design text (`:4438`, `:4440`, `:4472`) still names `python3.12`. That text is replaced by OH-S0d, and no observation changes |
| C2 | HF-10, HF-11 | **add rows** for each installed static image (absent at H-0; present at P-0 and H-2) and for `/run/freedom-blades-rp11-lock-*` (absent) |

**Role D, standard-library capability claims.**

| # | Location | **LIT-FULL** | **SSW** |
|---|---|---|---|
| D1 | PT-8: `renameat2` through `ctypes` | **unchanged for the entry-side Python**. In a static root image `renameat2` is a direct system call, which [R2 §7 (c)] establishes at the kernel and glibc level. `os.renameat2` does not exist in 3.14.4 [R2 §10.5] | unchanged: `ctypes`, whose `_ctypes` closure (`libffi`) is an MF-1 consumer |
| D2 | the bootstrap, the capture mechanism and `rp11_h1.py` under TR-9's interpreter | **`rp11_h1.py` is replaced** by static images (WP-4). The entry-side bootstrap tests run under 3.14 as well as the suite interpreter, or the gap is stated | unchanged: OH-S4 tests run under 3.14 as well as the suite interpreter, or the gap is stated |

**Role E, verification artifacts.** `tests/test_rp11_launch_source.py` and
`infra/rp11-launch/verify/ctverify.py` read their constants from the manifest
contract. They need **no literal edit** and need **extension** for every added image
(OH-S4p). D2's test methods (`:1525`, `:2207`) and the I-7 handback's decoded `execve`
record are evidence for the **old** image. They remain history and are superseded by
re-run evidence for each new image.

**Role F, development and test runtimes** (`venv-web` CPython 3.12.14, the
controller's 3.12.3 records, the production deployment Python, the harness and
laboratory fixtures): **unaffected under every alternative.** They are not the trusted
path.

**Role G, current-state records.** `docs/implementation-plan.md` §20,
`docs/project-management/status.md`, `docs/review/Handover information` and the
test-server banner: **pointers only**. This assignment updates them, and only them.

**Role H, historical or consumed evidence:** the R3 … R5 prompts, authorities,
handbacks and reviews, the design's revision history, the preparation handback, the
2026-09-29 C11 review, the R1 proposal and handback, and the `*-through-*` snapshots:
**never edited.**

### 9.7 `STATIC-SCRUB-WRAPPER` (SSW): the scope-change alternative, stated exactly

SSW is R1's RT3-A with its recommendation removed and its name changed. It is kept
because it is a coherent, bounded design that a maintainer may wish to weigh **after a
§0.2 decision**. It is **not Route 3**.

**What it is.** A second static image of the class the repository already reviews,
`rp11-rootexec`, installed beside `rp11-launch` in tree **L**. It accepts five roles,
validates their operands byte for byte, writes a literal environment, closes every
descriptor from 3 up, resets signals, sets `umask 0077`, `chdir("/")`, and `execve`s
`/usr/bin/python3.14 -I -S …/rp11_h1.py ⟨subcommand⟩ …`. Every unit-run root helper
names it as the program PID 1 starts. `attest` is run through it under `sudo -n`. The
entry keeps `rp11-launch`, with one literal retargeted. H-1, RB-1 and RS-1 keep the
accepted verified-exec stub (HB-1).

**Contract (carried from R1, condensed).**

* **Class.** The accepted launcher's [D2 §5.1]: freestanding ISO C11, `-ffreestanding
  -nostdinc`, one assembly `_start` entering one C function by one `jmp`, no runtime,
  no writable data segment, no `ret`, no `call`, every exit `exit_group` followed by
  `ud2`. A separate image from the same build.
* **Accepted argv.** `argv[0]` is not examined. `argv[1]` is one of `consume`, `hold`,
  `stop-post`, `backstop`, `attest`. `consume` takes `argc = 2`. The other four take
  `argc = 4`: `argv[2]` exactly **34** bytes matching
  `rp11-act-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}`, `argv[3]` exactly **64** bytes of
  `[0-9a-f]`. Anything else exits `111` before any state operation.
* **Environment.** The four unit roles read only the `INVOCATION_ID` selection
  ([D2 §5.6], exit `112`). `attest` reads none. `rp11-helper-env/1` is the same three
  entries, in the same order and bytes, as `rp11-entry-env/1`: `LC_ALL=C`,
  `PATH=/usr/bin`, `INVOCATION_ID=⟨32⟩`. `rp11-helper-env/1a` is the first two only.
* **State operations**, in the accepted order [D2 §5.7]: argv check `111`;
  `INVOCATION_ID` `112`; `fcntl(F_GETFD)` on 0, 1, 2 `113`; `close_range(3,
  0xFFFFFFFF, 0)` `114`; every signal disposition reset except `SIGKILL` and
  `SIGSTOP`, then the mask cleared `115`; `umask(0077)`; `chdir("/")` `116`; the
  `execve` `117`.
* **System calls**: exactly the launcher's inventory (`fcntl`, `close_range`,
  `rt_sigaction`, `rt_sigprocmask`, `umask`, `chdir`, `execve`, `write`, `exit_group`).
  AD-8 holds only for that closed inventory [R2 §12].
* **Not touched and not claimed**: limits, `no_new_privs`, capabilities, securebits,
  seccomp, namespaces, cgroup, scheduling, `oom_score_adj` (R-10, K-5). It claims
  nothing about `NoNewPrivileges` for the root roles.

**The literals (design text; none is run).**

```text
ExecStartPre=+/usr/local/libexec/freedom-blades-rp11/rp11-rootexec consume
```

```text
sudo -n /usr/bin/systemd-run --system --no-ask-password --quiet
  --unit=⟨activation_id⟩ --service-type=exec
  --property=Restart=no --property=OOMScoreAdjust=-1000
  --property=RuntimeMaxSec=⟨L⟩ --property=TimeoutStopSec=⟨S⟩
  "--property=ExecStopPost=/usr/local/libexec/freedom-blades-rp11/rp11-rootexec stop-post ⟨activation_id⟩ ⟨a2_sha256⟩"
  /usr/local/libexec/freedom-blades-rp11/rp11-rootexec hold ⟨activation_id⟩ ⟨a2_sha256⟩
```

```text
/usr/bin/systemd-run --system --no-ask-password --quiet
  --unit=⟨activation_id⟩-backstop --on-active=⟨R⟩ --on-unit-active=⟨R⟩
  --timer-property=AccuracySec=1s --service-type=exec
  --property=Restart=no --property=OOMScoreAdjust=-1000
  --property=RuntimeMaxSec=⟨S_b⟩ --property=TimeoutStopSec=⟨S⟩
  /usr/local/libexec/freedom-blades-rp11/rp11-rootexec backstop ⟨activation_id⟩ ⟨a2_sha256⟩
```

```text
sudo -n /usr/local/libexec/freedom-blades-rp11/rp11-rootexec attest ⟨activation_id⟩ ⟨a2_sha256⟩
```

The grammar rules stand: no `--setenv`, `-E`, `--scope`, `--user`, `--pty`, `--wait`
or `--collect`, and no `%`, `$`, `\` or quotation mark apart from the shell quotes
around the `ExecStopPost=` argument. The image path contains **no `.`**, which
matters for extension matching (§9.10). The backstop literal carries BS-RM.

**What SSW closes.** The interpreter and the loader start under a closed environment
and a closed descriptor table. The manager's block, `sudo`'s block and the caller's
block never reach them.

**What SSW leaves, by name.** CPython and glibc stay in the root path. Their **file**
inputs stay inputs: MF-1, MF-2, MF-4 (§9.8, §9.9). The dynamic children stay (MF-9).
HB-1 stays. **Each is a reason it is not Route 3.**

**The baseline decision that would precede selecting it.** Peter, as Acceptance
Authority, would amend the accepted Route 3 boundary [DR1 §5.3, R3 §6.3] to read:
*"the root procedures start under a closed environment and a closed descriptor
table; CPython and the glibc loader remain in their path; the file-based inputs of
one interpreter and its closure are bound by MF-1, MF-2 and MF-4 and by the drift
gates"*, through §0.2 steps 1 to 5: a change-log entry, an impact assessment, the
Product Owner recommendation and Technical Lead review, Acceptance Authority approval,
and a new baseline version if the roadmap or release boundary changes. **This
proposal does not make that decision, does not request it, and does not use DEC-1 or
the acceptance of this proposal to make it.** The same applies, with the alternative's
own text, to SCDC and ACCEPT-X1.

### 9.8 PO-12′ and PO-19 under the corrected boundary

| Obligation | Today | **LIT-FULL** (R3-ROOT) | **LIT-DR1** | **SSW** | **SCDC, ACCEPT-X1** |
|---|---|---|---|---|---|
| **PO-12′** (CPython `-I -S` start-up) | PO-12 and AS-8 **refuted** [R2 §10.4]; PO-12′ source-established, binding needs MF-4 | still necessary, **narrowed to the entry** (the one remaining Python process). The environment precondition is met by the entry's literal environment; the **file** inputs remain MF-4 | **eliminated**: no Python process remains | necessary for the entry **and** the five root roles; environment precondition by byte-level construction of two static images; file inputs MF-4 | SCDC: entry only. ACCEPT-X1: entry only, and **PO-12 stays refuted for the root roles** |
| **PO-19** (glibc loader inputs) | **not established** (MF-1, MF-2) | still necessary, **narrowed to the entry** (one executable and its closure). (a′) file inputs MF-1; (d) ownership MF-2 | **eliminated** for Python; each static image is its own D9 case | the same six processes; (a′) MF-1 and (d) MF-2 for them | SCDC: the entry **and** the dynamic children (MF-9). ACCEPT-X1: the entry; the root roles stay **open** |
| **PO-9R, D9-1 … D9-4** | not applicable | for the entry launcher and every static root image | for every static image | for the entry launcher and the wrapper | for the entry launcher (and the SCDC image) |
| **PO-17** | **not evaluated** against any image | per image (§9.10) | per image | per image | per image |

The binding tuple of [R2 §11.6] is unchanged for whatever still runs `python3.14`:
`python3.14-minimal` `3.14.4-1ubuntu0.2`, `libc6` `2.43-2ubuntu2.4` and
`/usr/bin/python3.14`'s SHA-256 `be9a2a5e…69fd`. Its dynamic-section row stays
**unestablished** until MF-1 is observed. **No alternative closes PO-19 by itself.**

### 9.9 Root-owned dynamic inputs are still inputs

R1 wrote that Route 3 "removes the part R2 refuted (the ambient environment) and
leaves the part that was never refuted and never observed (the files)", and that it
"does not need to" close the file inputs. That sentence is **withdrawn**. The accepted
Route 3 *does* need them out of the root path, and SSW does not take them out.

The ownership of `/etc/ld.so.preload`, `/etc/ld.so.cache`, `DT_RUNPATH` and
`DT_NEEDED` of `/usr/bin/python3.14` and each loaded object, the trusted directories
and their `glibc-hwcaps` subdirectories, `/usr/bin/python3.14._pth`, `pyvenv.cfg`,
`pybuilddir.txt`, `Modules/Setup.local` and `/usr/lib/python3.14` determines **who can
change them**. It does not stop them being **inputs of the process**. The threat model
excludes an unprivileged writer, and that explains **how a residual is argued** (R-8,
OH-D-6). It does **not** make a root-owned dynamic input stop being something that must
be (a) observed, (b) bound by digest, version and ownership, and (c) covered by a drift
gate. Such an input ceases to be an input of a root procedure **only if no process of
that procedure loads it**, which is LIT-FULL's property for the root path and not
SSW's. The entry still loads them under every alternative except LIT-DR1.

### 9.10 PO-17, the byte-level boundary, and the OH-S4 / OH-S4p split

[R2 §12.9] established PO-17's premises and left it **not evaluated against any
launcher image**. For **each** static image that is an `execve` target (the entry
launcher in every alternative but LIT-DR1; the wrapper under SSW; every static root
image under LIT) **OH-S4p** (repository only) must supply:

1. **The bytes.** The file's complete bytes (a digest and a size) and its **first 256
   bytes** (`BINPRM_BUF_SIZE`, [R2 §12.9 (3)]), recorded as an independent digest and
   as hex in the review record.
2. **The installed path string**, exactly as it will be passed to `execve`
   (`bprm->interp`), and the statement that **it contains no `.`** over the whole path.
   Extension entries compare the text after the last `.` in the *full path*, not the
   basename [R2 §12.9 (4)]. `rp11_h1.py` and `rp11_entry.py` are arguments, not
   `execve` targets.
3. **The mechanical evaluation** of every recorded `binfmt_misc` entry against the
   image under premises 2 … 4 of [R2 §12.9] and the algorithm of [D §4.3.6]: the global
   gate, the per-entry enable bit, the magic comparison (`offset`, `size`, optional
   `mask`, over the 256 bytes) and the extension comparison on the full path. The
   accepted H-0 recorded one entry, `python3.14` (`offset 0`, magic `2b0e0d0a`, no
   mask, interpreter `/usr/bin/python3.14`, flags empty). An ELF image begins
   `7f454c46`, so a *preliminary* result can be computed from bytes alone. It is a
   **preliminary, record-bound evaluation**. PO-17 is **not discharged** by it.
4. **The live evaluation** at H-1's P-0, at V-1 and at H-2, against the entries
   re-observed on the host (HF-14), with any new, changed or enabled entry an INVALID
   RUN.
5. **The static-image facts** D9-2 already requires: `ET_EXEC`, no `PT_INTERP`, no
   dynamic section, no relocation or TLS, a closed list of `.rodata` strings, no `ret`,
   no `call`, the closed system-call set (for a root image under LIT, the set WP-4
   fixes, with AD-8 restated over it).
6. **The delta of the entry image**: A1 and nothing else. Every other source file
   hashes equal to its accepted value, and the compile line is byte-identical.
7. **The pins**: the new digests in `expected.sha256` and the manifest, the A-2 and
   H-1 fields they feed, and the independent bindings of §9.11.

OH-S4p **does not** contact a host, install anything, edit the operational draft or run
any activation step.

**The split under each alternative.**

| Alternative | **OH-S4** (repository implementation that is not a launcher image) | **OH-S4p** (launcher images, byte level) |
|---|---|---|
| **LIT-FULL** | the entry-side Python (bootstrap, tests), the H-1 and H-2 tooling if BQ-3 is out of scope, the activation tests that do not depend on an image | the entry retarget (A1) **and every static root image**. *The split is by image versus non-image, not by "non-launcher code":* the root procedures **are** images, so OH-S4 shrinks and OH-S4p grows |
| **LIT-DR1** | the tests and tooling that remain | every static image, including the entry |
| **SSW** | the Python procedures `rp11_h1.py` and its tests, under 3.14 and the suite interpreter | the entry retarget and the wrapper |
| **SCDC** | the entry-side Python and tests | the entry retarget and the SCDC image, with a much larger proof obligation |
| **ACCEPT-X1** | the Python procedures and tests | the entry retarget only |
| **WITHDRAW** | none | none |

### 9.11 Reproducible source, build, pinning, digest, ownership, installation, update, rollback and drift *(none performed; applies to each static image of any alternative)*

* **Source.** `infra/rp11-launch/` gains one source file per added image. Every image
  shares `start.s`, `select.h`, `rp11-launch.ld`, `build.sh`, `toolchain.lock` and
  `build-root.manifest`. **The entry image's compiler flags and every other source byte
  are unchanged**, apart from A1. Source SHA-256 values are recorded before and after.
* **Build.** The accepted chain, unchanged in method: `provision.py` and `enter.py
  build` over the pinned Ubuntu snapshot archive (`archive_snapshot=20261001T000000Z`,
  every package SHA-256 in `toolchain.lock`), `build.sh` as the first process in the
  verified build root, the same-invocation R-1 tree-manifest gate, IC-1, and R-2 as the
  unprivileged build user. It produces one image per source file.
* **Pinning.** `expected.sha256` gains four rows per added image (image, listing, map,
  assembly). The manifest takes one new version with every contract. A-2 pins the image
  digests.
* **Independent bindings** for each image, as [D §4.5.2]: `expected.sha256`, the
  manifest contract, an accepted independent-rebuild record (D9-3), and Codex's
  independent decoding (XD-11).
* **Ownership.** Each image is a regular file, `root:root`, `0755`, with no set-user-ID,
  set-group-ID or sticky bit, no `security.capability` and no `system.posix_acl_*`
  attribute, a member of tree **L** (§4.2.3). Its parents are the accepted tree **L**
  parents. Its path contains no `.`.
* **Installation.** By H-1 only (PT, PF, M-1), from the OH-S5 rebuild's bytes read
  **once**, hashed in memory and written from those bytes ([D §4.2.4]). The H-1 record's
  `baseline.files` gains each image (SHA-256, size, owner, mode, `(dev, ino)`),
  compared by H-2.
* **Update.** **Never in place.** A new image is a new OH-S4p cycle (D9-1 … D9-4), a new
  OH-S5, then RB-1 and a new H-1, because H-1 requires its paths absent at P-0. A
  distribution update of `python3.14-minimal`, `libc6`, the kernel, `systemd` or
  `polkitd` is not an update of an image: it is drift.
* **Rollback.** RB-1, separately authorized and never automatic, removes tree **L**'s
  members, including every static image. No procedure removes one during an activation.
* **Drift, checked before any lock object or grant exists.** The kernel, `systemd`,
  `polkitd`, and, **for whatever still runs them**, `libc6`, `python3.14-minimal` and
  `/usr/bin/python3.14`'s SHA-256 of [R2 §16]; **every image digest**, the entry
  launcher's digest and the digest of the root procedures' non-image code, each against
  the H-1 record; the nine Polkit rule digests of [R2 §16]; the HF-14 entries; and the
  unit's loaded configuration. P-0, H-2, AP-0 and AM-0 each compare. Any difference is
  INVALID RUN followed by re-citation, **never accepted at run time**.
  `unattended-upgrades` is active (HF-17), so drift is expected unless separately
  controlled, and a package hold is not authorized (R3 §6.7).

### 9.12 Failure and recovery for missing, altered, wrongly owned or incompatible artifacts

| Artifact | Condition | Detected by | Behavior | Recovery owner |
|---|---|---|---|---|
| a static root image | **missing** | H-1's own post-install verification, H-2, AP-0 | INVALID RUN; no lock object, no grant. After `ACT`: the holder never starts, so no grant was linked (§5.5 row 12); an `ExecStopPost=` or backstop that cannot execute it is RO-2 | RB-1 then H-1, separately authorized. **No in-place repair** |
| | **altered** (digest) | H-2, AP-0, AM-0 | INVALID RUN or HARD STOP before AM-1 | as above |
| | **wrong owner, mode or extended attribute** | H-2, AP-0 (`lstat`, `listxattr` names) | INVALID RUN | as above |
| | **incompatible**: the kernel cannot run it, an enabled `binfmt_misc` entry matches it, or a system call it needs is refused | P-0 and H-2 (PO-17 live evaluation, D9-4); the first start of a **test** unit under OH-S8b | INVALID RUN; if met at run time, the start ends and `ExecStart=` is never executed | design review |
| `rp11-launch` (entry) | missing, altered, wrongly owned, incompatible | as above | as above; at run time the unit fails and no pass runs (PO-21 (o) governs `ExecStart=` itself) | as above |
| the non-image root code (`rp11_h1.py` under SSW, SCDC, ACCEPT-X1) | missing, altered | H-2, AP-0, AM-0 (digest pinned by A-2) | as above; at run time CP's helper does not run, so no pass | as above |
| `python3.14` and its closure (wherever still used) | version or digest drift | P-0, H-2, AP-0 (the §9.11 drift list) | INVALID RUN, then re-citation | OH-S2b |
| the unit | altered after H-1 | H-2, AP-0 (`baseline_sha256`) | INVALID RUN | RB-1 / H-1 |

### 9.13 Trusted and runtime surface, compared under the corrected boundary

| Criterion | **LIT-FULL** | **LIT-DR1** | **WITHDRAW** | **SSW** | **SCDC** | **ACCEPT-X1** |
|---|---|---|---|---|---|---|
| Meets the accepted Route 3 | yes | yes (wider) | yes | **no** | **no** | **no** |
| Decision-ready | **no** (WP-1 … 7) | **no** (WP-1 … 8) | n/a | yes, as an alternative | no | yes, as an alternative |
| New trusted code | static images implementing the root procedures and loader-free interfaces: **no accepted measure, and no accepted proof method for that inventory** | LIT-FULL plus a Python-free entry | none | one small static image of an already-reviewed class | a static core as large as LIT-FULL's logic | none |
| CPython in the root path | **absent** | absent everywhere | n/a | present | absent from the helper logic | present |
| Dynamic loader in the root path | **absent** (LR-2) | absent | n/a | present | **present via children** | present |
| Environment inputs to root procedures | RH-1 by construction | RH-1 by construction | n/a | RH-1 by construction | RH-1 by construction | **ambient (PO-12 refuted)** |
| File-based loader and interpreter inputs | removed from the root path; remain for the entry (MF-1, MF-2, MF-4 narrowed) | removed everywhere | n/a | **remain (six consumers)** | remain for children and entry (MF-1, MF-2, MF-4, MF-9) | remain |
| Drift exposure | the entry only | none from Python | n/a | `python3.14`, `libc6` updates trigger re-citation (HF-17) | as SSW plus the children | as SSW |
| Review | a new design cycle, a new proof method, security re-review | larger still | a decision, with consequences for the Phase 5 plan | one new static image through the accepted chain, plus the §0.2 change | everything in LIT-FULL's logic, **and** the §0.2 change | the §0.2 change and a residual acceptance |
| Reversibility | RB-1 removes the images | the same | n/a | RB-1 removes the image | the same | none needed |

The comparison supports one statement without selecting anything: **only LIT-FULL,
LIT-DR1 and WITHDRAW satisfy the accepted boundary, and none of them is decision-ready
except WITHDRAW, which ends the design.**

### 9.14 Negative tests the Route 3 outcome would define *(proposed; none run)*

| ID | Case | Asserts |
|---|---|---|
| NT-RH-1 | every root role against an environment block containing each of `PYTHONEXECUTABLE`, `__PYVENV_LAUNCHER__`, `PYTHONPATH`, `PYTHONHOME`, `PYTHONSAFEPATH`, `mimalloc_*`, `MIMALLOC_*`, `LD_PRELOAD`, `LD_LIBRARY_PATH`, `LD_AUDIT`, `GLIBC_TUNABLES`, `MALLOC_CHECK_`, `MALLOC_ARENA_MAX`, `LOCPATH`, `GCONV_PATH`, `LANG`, `LC_*`, `TZ`, `HOME`, a hostile `PATH`, and a duplicate or malformed `INVOCATION_ID` | RH-1: the observed environment of every image the root procedure executes is **exactly** the reviewed literal, by the strace-class method of [D2 §5.12], Method A. Malformed or duplicate `INVOCATION_ID` exits `112` for the four unit roles |
| NT-RH-2 | descriptors | RH-2: every descriptor ≥ 3 is closed before the first state operation; a closed descriptor 0, 1 or 2 is refused |
| NT-RH-3 | signals, mask, `umask`, working directory | RH-3 as the accepted launcher's tests |
| NT-RH-4 | each image | `ET_EXEC`, no `PT_INTERP`, no dynamic section, closed `.rodata`, no `ret`, no `call`, the closed system-call set |
| NT-RH-5 | the PO-17 matcher | over every image, the recorded HF-14 entry and generated entries (magic at offset 0 and elsewhere, masks, extension entries) |
| NT-LR-1 | **LIT-FULL only**: a process-tree scan of every root procedure under a stepped harness | every `execve` target is a static ELF with no `PT_INTERP`; **no CPython and no dynamic loader appears** (LR-1, LR-2) |
| NT-LR-2 | **LIT-FULL only**: the equivalence mapping (WP-6) | every accepted step and every accepted negative test has a counterpart that passes against the image |
| NT-SSW-1 | **SSW only**: five roles with a wrong `argc`, an operand of the wrong length or class, an extra argument, an unknown role, any `argv[0]` | exit `111` before any state operation; nothing executed |
| NT-SSW-2 | **SSW only**: unit text T-B1 and the baseline normalization | exactly the wrapper line; an altered image or a changed normalization is detected by the H-2 code |
| NT-SSW-3 | **SSW only**: the helper tests | run under CPython 3.14 as well as the suite interpreter, or the gap is stated |

---

## 10. MF-1 … MF-8: disposition under the corrected boundary *(nothing is collected here)*

The identifiers and facts are those of [R2 §14.3]. Two read-only observing slices are
**proposed** (names are proposal-local, neither is authorized): **H-0M1**,
unprivileged, and **H-0M2**, privileged and read-only. Each needs its own authority,
work ID, exact commands and evidence path, on `oracle-test` only. Both obey the
accepted H-0 prohibitions (no `env`, `printenv`, `/proc/*/environ`, no secret, no
`ldd`, no `LD_TRACE_LOADED_OBJECTS`, no listing of retained paths). ELF parsing, if
needed, reads file bytes and executes nothing from the closure.

**Ordering consequence of the hard stop.** The consumer set of MF-1, MF-2 and MF-4
**depends on the Route 3 outcome**, so **the scope of their observation cannot be
fixed before WP-9**. MF-3, MF-5, MF-6, MF-7 and MF-8 do not depend on it and may be
observed earlier, if separately authorized.

**Route 3 effect, by alternative.**

| MF | Fact (R2 §14.3) | **LIT-FULL** (R3-ROOT) | **LIT-DR1** | **SSW** | **SCDC** | **ACCEPT-X1** |
|---|---|---|---|---|---|---|
| **MF-1** | `/usr/bin/python3.14` `DT_RUNPATH`, `DT_RPATH`, `DT_NEEDED`, `DT_FLAGS_1`, `PT_INTERP`, and the same for each object in its closure | **narrowed** to the entry's one executable and closure | **eliminated** (no Python) | six consumers; the closure covers what the root helpers import | entry plus the dynamic children (MF-9) | entry only; the root roles stay **open** |
| **MF-2** | type, owner, mode of `/lib`, `/lib/x86_64-linux-gnu`, `/usr/lib`, `/usr/lib/x86_64-linux-gnu`, their `glibc-hwcaps/x86-64-v{2,3,4}`, and each library MF-1 resolves to | **narrowed** to the entry's closure | **eliminated** | six consumers | entry plus children | entry only |
| **MF-3** | privileged read-only inventory of `/etc/polkit-1/rules.d` (names, types, owners, modes, SHA-256) | **unchanged** | unchanged | unchanged | unchanged | unchanged |
| **MF-4** | absence or root ownership of `/usr/bin/python3.14._pth`, `/usr/pyvenv.cfg`, `/usr/bin/pyvenv.cfg`, `/usr/bin/pybuilddir.txt`, `/usr/bin/Modules/Setup.local`; ownership of `/usr/lib/python3.14` | **narrowed to the entry**; the sole remaining residual of PO-12′ | **eliminated** | six consumers | entry | entry only |
| **MF-5** | whether the ext4 filesystem on `/dev/sda1` has a journal (`has_journal`) and its data mode | unchanged | unchanged | unchanged | unchanged | unchanged |
| **MF-6** | run-time `fs.protected_hardlinks` and `fs.protected_symlinks` | unchanged | unchanged | unchanged | unchanged | unchanged |
| **MF-7** | `/run/nextroot` absent | unchanged | unchanged | unchanged | unchanged | unchanged |
| **MF-8** | the dash-prefix drop-in directories in all 12 unit paths | unchanged | unchanged | unchanged | unchanged | unchanged |
| **MF-9** *(new, optional)* | the dynamic sections and closures of the helper children: `/usr/bin/systemctl`, `/usr/bin/systemd-run`, `/usr/bin/pkcheck`, `/usr/bin/sleep` | **none** (LR-2: no dynamic child) | none | **optional**: whether the review wants helper children's loader inputs observed. Not required | **required** | not applicable |

**The observing slices, common to every alternative.**

| MF | Minimum observing slice and privilege | Exact-path scope | Evidence and drift trigger | Dependent gate |
|---|---|---|---|---|
| **MF-1** | **H-0M1**, no privilege. **After** the repository implementation fixes the import closure of every Python process that remains | `/usr/bin/python3.14`; each `/usr/lib/python3.14/lib-dynload/*.so` that the import record names; each library the recorded `DT_NEEDED` names resolve to, through `/etc/ld.so.cache` and the built-in directories, by reading bytes only | the parsed dynamic entries and a SHA-256 for each file, as admitted capture records. **Drift:** any change of `python3.14-minimal`, `libc6`, any digest in the closure, or the import closure | PO-19 (a′) binding (OH-S2c); H-1 readiness |
| **MF-2** | **H-0M1**, no privilege | exactly the MF-2 paths: `lstat` of each and its parents, extended-attribute **names** only | type, owner, group, mode, `(dev, ino)`, attribute names. **Drift:** any ownership or mode change, a changed `ld.so` configuration, a `libc6` change | PO-19 (d) |
| **MF-3** | **H-0M2**, root, read-only, one reviewed fixed literal. **Recommended before H-1** (DEC-4) | exactly `/etc/polkit-1/rules.d` and each regular file in it, by digest only | names, types, owners, modes, SHA-256. **Drift:** any added, removed or changed file; re-observed at H-1's P-0p. A later PK result corroborates and never replaces it | PO-11 (b), (g); H-1 readiness |
| **MF-4** | **H-0M1**, no privilege | exactly the five paths and `/usr/lib/python3.14` | `lstat` results (`ENOENT` or type, owner, mode). **Drift:** appearance of any of the five, or an ownership change | PO-12′ binding; H-1 readiness |
| **MF-5** | **H-0M1** if an unprivileged read exists, otherwise **H-0M2** read-only. **The slice must name the exact read-only path or literal.** This proposal asserts no availability | the one device already recorded by HF-15 | has-journal yes/no and the data mode. **Drift:** a different filesystem, a changed mount option (HF-15 is re-observed at P-0 and AP-0 anyway) | PO-20 (a), (d); H-1 readiness |
| **MF-6** | **H-0M1**, no privilege | the two named kernel parameters | the two values. **Drift:** a sysctl change | PO-20 (a) |
| **MF-7** | none separate: AP-0 and AM-0 already observe it. H-0M1 may record it early | `/run/nextroot` | `lstat` → `ENOENT`. **Drift:** any creation of the path | CL-21i acceptance; before any A-2 |
| **MF-8** | **H-0M1** (early knowledge) and H-1 (the mechanical check, `DropInPaths` empty) | the 36 paths (3 names under each of the 12 unit paths of HF-13) | `lstat` each. **Drift:** existence of any | HF-13 completeness; H-1 P-0 |
| **MF-9** | **H-0M1** if required, no privilege, bytes only | the four binaries and their closures, as MF-1 | as MF-1 | only under SCDC, or if the review elects it under SSW |

---

## 11. Successor order and review gates *(no successor is authorized by naming it)*

Every row needs its own prompt, authority record, work ID and Codex review. The order
is a dependency order. Rows with the same number may run in parallel. None of them is
requested here. The hard stop changes the order of R1: **Route 3 readiness precedes
every row that depends on the executable boundary.**

| Order | Slice (proposal-local name) | Scope | Host | Gate before it | Closes |
|---|---|---|---|---|---|
| **G-0** | independent Codex re-review of this proposal and handback | review | none | — | the findings of this return |
| **G-1a** | **Peter's decisions on the activation design** DEC-1 … DEC-6 (§12.1), after a **clean** review | decision | none | G-0 clean | the activation-design choices only |
| **G-1b** | **Peter's direction on Route 3** (§12.2): commission WP-1 … WP-7 (or WP-8); **or** open a §0.2 change request for a scope-change alternative; **or** WITHDRAW. **Not a DEC and not a consequence of accepting this proposal** | decision | none | G-0 clean | which of §9.4's paths proceeds |
| **2R** | **Route 3 readiness**: WP-1 → WP-2 → WP-3 (a citation slice) → WP-4 → WP-5, WP-6, WP-7 (and WP-8 for LIT-DR1) → Codex review → WP-9, Peter's recorded choice | documentation, plus a citation slice | none | G-1b | the hard stop |
| **2R′** | **§0.2 change control** for a scope-change alternative, if Peter chooses that path: change-log entry, impact assessment, Product Owner recommendation and Technical Lead review, Acceptance Authority approval, a new baseline version if needed | governance | none | G-1b | the baseline change, **before** any design acceptance of SSW, SCDC or ACCEPT-X1 |
| **2a** | **OH-S2b**: citation addendum for the new and restated obligations (§13.2), including BS-RM's `RuntimeMaxSec=` on a timer-started `Type=exec` service and the `Type=exec` start-job completion | documentation, U-10 | none | G-1a | PO-20 (f′-2 … 5), PO-21 (s′) floor, [E1], [E2]; confirms (c′) and (d′) as design acceptances |
| **2b** | **OH-S3S**: operational-draft incorporation (Appendix B), if separately needed | documentation | none | G-1a (and 2R for the rows that depend on the boundary) | the draft's A-2 pins, matrix, interruption, stop and handback rows. Codex re-review of the draft (A-1) |
| **2c-I** | **OH-S0d, part I**: apply Appendix A-I (the route-independent rows) to the one-host design as a cumulative amendment | documentation | none | G-1a | the accepted inactive design is amended in place. Codex re-review, then Peter's acceptance |
| **2c-II** | **OH-S0d, part II**: apply Appendix A-II (the boundary-dependent rows) | documentation | none | **2R** (and 2R′ if applicable) | the boundary-dependent text. Codex re-review, then Peter's acceptance |
| **3a** | **OH-S4 (amended)**: **Route 3 implementation** and its tests (30) … (35), for what the chosen outcome leaves as non-image code | repository only, unwired, nothing installed | none | 2c-I accepted, 2R decided (and 2a for version-bound data) | LD, IGR, GRR, SD, PK/2, SG, DL, HS and the role vectors. **Security-focused Codex review** |
| **3b** | **OH-S4p**: the launcher images, byte level (§9.10), for every image the chosen outcome includes | repository only | none | 2c-II accepted | PO-9R, D9-1 … D9-2 documentary and mechanical parts, the preliminary PO-17 evaluation. **Byte-level, security-focused Codex review** |
| **4** | an **R-5-class independent rebuild** of every image (D9-3), then **OH-S5** (the installation-source rebuild, §4.5), where still applicable | build as `ubuntu` on `oracle-test` | `oracle-test` | 3b accepted (and 3a for the tool bytes) | D9-3; the installation-source record. Retained R4/R5 outputs stay evidence only and are never an installation source |
| **5a** | **read-only MF collection**: H-0M1 and H-0M2, for MF-3, MF-5, MF-6, MF-7, MF-8 | read-only | `oracle-test` | G-1a; they do not depend on Route 3 | those observations |
| **5b** | **read-only MF collection**: H-0M1, for MF-1, MF-2, MF-4 (and MF-9) | read-only | `oracle-test` | 2R decided; 3a (the import closure) | those observations, at the consumer set the outcome fixes |
| **6** | **OH-S2c**: citation closure binding PO-19 (a′), (d), PO-12′, PO-11 (b), (g), PO-20 (a), (d) to the MF observations | documentation | none | 5a and 5b accepted | PO-19, PO-12′ and PO-11 verdicts |
| **7** | **H-1 readiness review** | review | none | 2a, 2b, 2c-I, 2c-II, 2R, 3a, 3b, 4, 5a, 5b, 6 accepted; DEC-1 … DEC-6 recorded | the readiness list of §11.1 |

After G-7 the accepted successors are unchanged and **separately authorized**: OH-S7
(H-1 assignment preparation), OH-S8 (H-1), CPP, H-2, OH-S8b (activation fault drill),
then A-2, `ACT`, Pass A and `DEACT`. Cleanup (LC-3 … LC-5) and workspace recreation
stay separate and are not sequenced by this table.

### 11.1 H-1 readiness list *(a review checklist, not an authority)*

1. DEC-1 … DEC-6 recorded; **Route 3 established** by a recorded WP-9 choice, or a
   §0.2 change accepted; the repaired design accepted as the inactive basis;
   Appendix A applied to the one-host design (OH-S0d) and accepted.
2. PO-20 (f′), PO-21 (c′), (s′) and PO-11 (d′) accepted; PO-9R, D9-1 … D9-4 and the
   preliminary PO-17 evaluation accepted for **every** image.
3. PO-19 and PO-12′ **bound** to MF-1, MF-2 and MF-4 at the consumer set the outcome
   fixes, or each explicitly returned.
4. MF-3 observed and PO-11 (b), (g) decided; MF-5 and MF-6 observed and PO-20 (a),
   (d) decided; MF-7 and MF-8 covered.
5. The operational draft amended (OH-S3S) and re-reviewed (A-1).
6. The drift list of §9.11 fixed to accepted values.
7. **No elapsed-time claim anywhere in the accepted design, the operational draft or a
   record states a bound that §7.7 withdrew** (NT-DL-4).

---

## 12. Decisions

### 12.1 Decisions Peter may make only after a clean independent review

No accepted decision is silently changed by this proposal. **OH-D-1 … OH-D-10, OS-6,
OH-D-6 … 8, U-9's text, M-B, M-S and the R2 dispositions are not changed.** Each
decision below has a recommendation and bounded alternatives. **None of them selects a
Route 3 alternative.** R1's DEC-1 (the Route 3 choice, which superseded D-3) is
**withdrawn**: D-3 is not superseded by anything in this proposal.

| ID | Decision | Recommendation | Bounded alternatives | Consequence |
|---|---|---|---|---|
| **DEC-1** | **PO-21 (c).** Which residual is acceptable | accept **RO-1** (§5.6) as the named, outside-guarantee, pre-pass and inert residual, together with RO-4 and RO-6 | elect **ALT-SENT** (§5.9), a resident sentinel, to narrow RO-1 | accepting adds no code beyond IGR and GRR. ALT-SENT adds a long-lived root image or process, citations and a drill |
| **DEC-2** | **Operational parameters** (§7.6) and the **backstop correction BS-RM** | P 30,000, c 5,000, g 2,000, λ 5,000, S 120 s, S_b 120 s, R 60 s, B 20, ρ 30,000, `slice_ms` 100, `journal_max_bytes` 1,048,576, `act_wait_s` = L. N1 holds with 16 s to spare under the 90 s default start timeout. **BS-RM adopted** | a shorter P (for example 15,000), at some risk of false `unconfirmed`; **or** a larger P with an explicit `TimeoutStartSec=` in the unit, which changes the reviewed unit bytes (T-B1) and the H-1 baseline; **or** keep the accepted backstop literal and record RO-5 as an accepted residual | the values are A-2 pins. A wrong value fails closed (no pass, a refused start), never open. **They are sizing parameters and never bounds** (§7.6) |
| **DEC-3** | **Lock and identity objects** (LD-1, GI-1) | the root-only object **K** under `/run` **with `grant.id`** | K without GI-1 (CL reads the `ubuntu`-owned journal as accepted; RO-6 widens and R1's flagged residual stays); **or** keep the `ubuntu`-owned evidence directory as the lock object and rely on GR-1 and LD-2 … LD-6 only | K adds one `/run` object and path rows; GI-1 adds one tmpfs file. Keeping the old object leaves `ubuntu` able to hold the lock, which then only refuses CP and delays HL, never holds a grant |
| **DEC-4** | **MF-3's observing slice** | a separate privileged read-only slice (**H-0M2**) **before H-1** | observe it in H-1's P-0p | the alternative saves a slice but settles PO-11 (b) only at install time |
| **DEC-5** | **CX-4 retirement.** Record that CX-4 is void for the cited systemd, because the accepted PO-21 (u) shows that a stop during `start-pre` ends the attempt `failed` | record the retirement, bound to systemd `259.5-0ubuntu3.4` | keep CX-4 as accepted (harmless) | retiring changes no mechanism. It removes a documented residual and adds the version-bound drift trigger of §6.8 |
| **DEC-6** | **Signal and removal discipline.** Adopt SG-1 … SG-8, GR-2 and the single-routine GRR as the activation design's removal and signal contract | adopt | keep R1's exception-raising handler (withdrawn here because it can fire inside IGR); or omit GRR's sharing with CL-G | adopting narrows what can fail. The alternatives re-open R2-F2 items 6 and 7 |

### 12.2 Changes of the accepted Route 3 boundary: not decisions of this proposal

**Implementation-plan §0.2** requires, for *"a material change to scope, authority,
privacy, architecture, data ownership, release criteria, phase order or target range"*:
a change-log entry identifying requester, reason and affected requirements; an impact
assessment for scope, dependencies, estimate, risk, testing, migration and
operations; Product Owner recommendation and Technical Lead review; Acceptance
Authority approval before the change becomes effective; and a new baseline version
when the roadmap or release boundary changes.

A change of the accepted Route 3 boundary, **before design acceptance**, is such a
change. The following are the ones this record identifies. **Each is separate from
§12.1, and none can be made by accepting this proposal.**

| ID | Change | Needed for | Not needed for |
|---|---|---|---|
| **BC-1** | amend the Route 3 boundary so that CPython and the glibc loader may remain in the root path under a closed environment (for ACCEPT-X1 see the nuance in §9.4) | SSW; ACCEPT-X1 (with its residual acceptance) | LIT-FULL, LIT-DR1, WITHDRAW |
| **BC-2** | treat R3-ROOT as a *narrowing* of DR1 §5.3 (the `ubuntu`-run entry stays Python) | LIT-FULL, if a maintainer reads it as a narrowing | LIT-DR1 |
| **BC-3** | except the dynamic children (DI-1 … DI-6's binaries) from LR-2 | SCDC | LIT-FULL |
| **BC-4** | except `sudo`-started procedures or the installer class from LR-1 … LR-2 (BQ-2, BQ-3) | any LIT alternative that answers BQ-2 or BQ-3 by an exception | an alternative that answers them without one |
| **BC-5** | withdraw RP-11's one-host design or its activation part | WITHDRAW | everything else |

---

## 13. Residuals, status of every obligation, and what this does not establish

### 13.1 Residuals

| ID | Residual | Status |
|---|---|---|
| **X-1** | a root helper starts under PID 1's open block, so CPython and the loader consume ambient inputs [R2 §10.4, §15.4] | **open for the root roles** until Route 3 is established (§9). The activation design is conditional on RH (§2.4) |
| RO-1 | uncatchable holder end while PID 1 can spawn neither stop-post nor the backstop | **named** (§5.6); pre-pass, inert; DEC-1 |
| RO-2 | helper bytes damaged after `ACT`: stop-post and backstop fail together | **named** (§5.6); IGR unaffected; AP-0, H-2, AM-0 detect a prior tamper |
| RO-3 | PID 1 dead or hung | outside every unit guarantee [R2 §8 (c)] |
| **RO-4** | IGR not completed: the holder is killed or stalls before GRR's `unlinkat` | **new in R2** (§5.6); the state is G1 inert; the rungs and IL apply; **no IGR speed is claimed** |
| **RO-5** | a started backstop firing has no PID-1 bound, and a hung one prevents every later firing | **new in R2** (§5.6); closed by BS-RM if accepted (DEC-2); the `Type=exec` start-completion claim is proposed for citation |
| **RO-6** | a persistent stall of a filesystem or the kernel delays every rung that touches `ext4` | **new in R2** (§5.6); IL holds; the boot clears `/run`; GRR and, with GI-1, CL-G avoid `ext4` |
| **CX-5** | with `τ₀ = 0`: a failed unidentified first attempt, then a root `reset-failed`, then the unit's unload | **new in R1, kept** (§6.5, SD-3); three root acts outside 𝒜 (SL-1 class). A later start runs the pass **with no grant** (G1 holds), but a second attempt occurs |
| CX-4 | a stop job during `start-pre` | **void** under R2 (u); retirement is DEC-5 |
| CX-1, CX-2, CX-3 | as accepted [D §4.2.5-R5 (k), R6 (f)] | unchanged |
| HB-1 | H-1, RB-1 and RS-1 run under `sudo`'s environment | **depends on BQ-3**: under SSW and ACCEPT-X1 it stays; under LIT-FULL it is either a stated exception (a BC, §12.2) or removed by a Python-free installer |
| SL-1, DF-1, GU | as accepted [D §4.2.5-R2 (l)] | unchanged |
| the `ubuntu`-owned `ACT` evidence directory | `ubuntu` can replace the journal, which makes CL class the rule A0 and keep it, and makes CP refuse (accepted analysis [D §4.2.5-R4 (b)]) | **narrowed by GI-1** for IGR and CL-G, which act on `grant.id` and the in-memory identity. **Unchanged for CP's CQ-3 and for CL's fallback**. Without GI-1 (DEC-3) it is unchanged for CL. Under OH-D-6 it is no more than `ubuntu` can already do |

### 13.2 Status of every obligation this proposal touches

| Obligation | Status after this proposal |
|---|---|
| PO-20 (f′-1) | **established** [R2 §7 (f)] |
| PO-20 (f′-2 … 5) | **proposed [N]**; OH-S2b citation |
| PO-21 (c′) | **established** [R2 §8 (c)] as a statement of what is not guaranteed; the ladder is design, not citation |
| PO-21 (s′) (1) … (4) | **established** [R2 §8 (s)]; (5) and the floor in (1) are **proposed [N]** |
| PO-21 (u) | **established** [R2 §8 (u)]; load-bearing for CX-4's retirement (version-bound) |
| PO-11 (d′) | a **design acceptance**: it claims no bound, so no citation is needed. PO-11 (e), (f)(i), (f)(ii), (f)(iv) as accepted; (b), (g) remain **not established** (MF-3) |
| **BS-RM** (`RuntimeMaxSec=` on a timer-started `Type=exec` service; start-job completion of `Type=exec`) | **proposed [N]**; OH-S2b citation; same code path as [R2 §8 (d), (r)] |
| **SG-1 … SG-8** (CPython 3.14.4 signal-handler timing and restart behaviour; the process-creation arguments of HS-3) | **proposed [N]** wherever the holder stays Python; OH-S2b citation. **Not applicable** where the Route 3 outcome removes Python from the holder |
| PO-9R | **proposed**; OH-S4p, D9-2, for every image of the chosen outcome |
| PO-12′ | **source-established**; binding needs MF-4 at the consumer set of §9.8 |
| PO-19 | **not established** (MF-1, MF-2) |
| PO-17 | **not evaluated** against any image until OH-S4p; live evaluation at P-0, V-1, H-2 |
| PO-14, AD-7, PO-8, CL-21i | **established**, unchanged |
| **Route 3** | **not established** (§9.3). The accepted disposition "Route 1 returns to Route 3 design review" stands |

**Not addressed by this assignment, and still returned** [R2 §15.5 item 3]: PO-15 (d)
(`NeedDaemonReload`), AD-8 as a general statement, PO-17's type-E basename test, and
C-1 … C-14 other than those named in this proposal (C-9, C-10, C-11 and C-12 are
answered by §§4 … 6 and 9, with C-12 carrying the Route 3 hard stop).

### 13.3 What this proposal does not establish

It establishes no host fact and discharges no obligation. It does not show that any
image can be built, that any helper behaves as specified, that any parameter value
is right, or that any sizing rule holds on the host. Each of those is a later gate
(§11). It does not change PO-14, LB-2S's two prevention claims about the entry, A-2,
the start-only grant, one start attempt, the no-follow source-consumption contract,
evidence durability or any fail-closed rule, and §2 shows why none of the repairs can.
**It does not establish Route 3, and it does not establish that any alternative
conforms to it except by the criteria LR-1 … LR-6.**

---

## 14. Proposed independent-review focus

### 14.1 Questions

1. **§2, §2.4.** Is the reading right that no safety proof (G1 … G5) cites the lock, HL,
   `ExecStopPost=`, the backstop, a Polkit latency or any elapsed time, and is it
   right to state that G1 … G5 are conditional on RH until Route 3 is established?
2. **§4.** Are LD-1 … LD-9 sufficient to prevent a longer-lived process from retaining
   a lock? Is K the right choice over the `ubuntu`-owned directory, and is GI-1 sound
   (its creation before PF-6, its root-only tmpfs location, the `identity-conflict`
   rule)?
3. **§5.** Does GRR need any citation beyond signal delivery? Are IL and IL′ sound?
   Are RO-1 and RO-4 … RO-6 stated narrowly enough? Is the single IGR site and latch
   (IGR-0) idempotent under a second signal at every instruction boundary?
4. **§6.** Is BSP's use of `CLOCK_MONOTONIC` valid given [E1] and [E2]? Is CX-4's
   retirement under R2 (u) correct?
5. **§7 (R2-F2).** Does any statement in this document still imply an elapsed time for
   a class-X operation (search for it, not only for the strings of NT-DL-4)? Is the
   inventory of §7.3 complete for ACT, CP, IGR, CL, the backstop and verification? Are
   N1 … N4 correctly described as necessary conditions only? Is BS-RM's reading of
   `Type=exec` right, and is RO-5 a defect of the accepted design? Are the signal
   discipline and the interruption maps of §7.8 and §7.9 complete?
6. **§9.1 (R2-F1).** Is R3-ROOT the right working boundary, and is DR1 §5.3's wording
   (R3-DR1) correctly stated as the wider reading? Are BQ-1 … BQ-4 the right questions?
7. **§9.3.** Is the hard stop justified? Is there repository evidence for a loader-free
   interface (E-2) or a static proof method (E-3) that the search missed?
8. **§9.4, §9.7.** Is SSW described everywhere as a scope-change alternative and
   nowhere as satisfying Route 3? Is the baseline decision text of §9.7 the right
   statement of what §0.2 would need?
9. **§9.5.** Are WP-1 … WP-9 complete and ordered correctly? Is anything missing that
   would make a literal Route 3 decision-ready?
10. **§9.6, §9.8.** Is the Role A–H inventory complete against the current files? Are
    PO-12′ and PO-19 correctly narrowed per alternative, and is anything that R2 refuted
    still hidden inside them?
11. **§9.9.** Is the statement that root-owned dynamic inputs remain inputs correctly
    applied to every alternative?
12. **§9.10.** Is the byte-level PO-17 boundary complete, and is the OH-S4 / OH-S4p
    split right under each alternative?
13. **§10, §11.** Are the MF dispositions per alternative right, and is the successor
    order (2R, 2R′, 2c-I, 2c-II) free of a missing or circular gate?
14. **§12.** Is the split between decisions that follow a clean review (§12.1) and
    changes that need §0.2 (§12.2) correct, and does any DEC smuggle in a scope change?

### 14.2 Claims that need independent security re-review

| # | Claim | Why | Gate |
|---|---|---|---|
| SR-1 | GRR's descriptor re-verification, and the residual name-to-descriptor window of `unlinkat` (as G-R1) | the removal path is now shared by IGR and CL-G | OH-S4 security review |
| SR-2 | GI-1: `grant.id` as the authoritative identity for non-holder rungs, `identity-conflict` resolved by `grant.id` | a new trust object, root-only, tmpfs | Codex security review, then OH-S4 |
| SR-3 | flag-only handlers, install-before-state, the IGR latch (SG-1 … SG-8, IGR-0) | replaces R1's exception-raising handler | OH-S4 |
| SR-4 | K and the lock discipline LD-1 … LD-9, including a lock never on a non-root object | PO-20 (f′) | OH-S2b, OH-S4 |
| SR-5 | BS-RM and the correction of the backstop literal | a change to an accepted literal | OH-S2b, OH-S0d |
| SR-6 | IL and IL′: a live rule cannot produce a pass once the holder is not `active` | the basis of the whole ladder's fail-closed behaviour | Codex security review |
| SR-7 | the sizing rules N1 … N4 are necessary conditions only, and nothing records them as bounds | R2-F2 | NT-DL-4, NT-DL-5, review |
| SR-8 | PO-17 evaluation for every image (§9.10) | not evaluated | OH-S4p |
| SR-9 | the chosen Route 3 outcome's interface contract, proof method and equivalence mapping | none exists | WP-3 … WP-6 |
| SR-10 | HB-1 and the BQ-2, BQ-3 exceptions, if any | a stated residual | Codex, Peter |
| SR-11 | X-1 stays open for the root roles until Route 3 is established | the accepted disposition | Codex |

---

## Appendix A. Exact amendments needed in the one-host design

These are **proposed text changes** to the accepted, inactive
[one-host design](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md).
None is applied by this assignment. A later documentation slice (OH-S0d, §11) would
apply them, keeping the design's own D3-Rn labelling convention: each added in place
with an *(OH-S3 R2)* marker and the replaced text retained as history. The rows are
split. **Part I** is independent of the Route 3 outcome and may be applied first
(slice 2c-I). **Part II** depends on the chosen boundary and waits for it (slice
2c-II).

### Part I. Route-independent rows

| # | Location | Action |
|---|---|---|
| A-I-01 | §4.2.3 path tables | add `K = /run/freedom-blades-rp11-lock-⟨activation_id⟩/` (`root:root`, `0700`, created by AM-0, removed by CL-5b or cleared by the boot) and `K/grant.id` (`root:root`, `0600`, created by AM-1G, removed by CL-5b before K) |
| A-I-02 | §4.2.5-R2 (b), (c) | paths gain K and `grant.id`. A-2 pins gain `pk_op_ms`, `pk_call_ms`, `reap_grace_ms`, `lock_wait_ms`, `slice_ms`, `stop_timeout_s`, `bs_runtime_s`, `backstop_max`, `reserve_ms`, `act_wait_s`, `journal_max_bytes`. **Replace "the PO-11 (d) bound"** by those. **Withdraw** S's grammar `⌈λ/1,000⌉ + ⌈(P + c)/1,000⌉ + 30 … 600` and replace it by N1 … N4 as **necessary conditions** (§7.6) |
| A-I-03 | §4.2.5-R2 (d) AP-0, AM-0, AK-1, AV-1, `hold-start`; add SG-1 and AM-1G | as §8.1. AM-0's lock text ("keep the lock until the holder exits") is already replaced by R4's AR-2 and is further replaced by K. SG-1 is the holder's first act |
| A-I-04 | §4.2.5-R2 (f), the backstop literal | **replace** `--property=TimeoutStartSec=⟨S⟩` by `--property=RuntimeMaxSec=⟨S_b⟩ --property=TimeoutStopSec=⟨S⟩` (BS-RM, §7.4). BS-4 gains the `backstop_max` rule |
| A-I-05 | §4.2.5-R2 (g) HL, and its "Latency bound" paragraph; §4.2.5-R5 (g) OS-5 | **delete** "which are local operations bounded by S" and the sentence it ends, and state W-5; OS-5's "exits **while holding the lock**" becomes "appends and `fsync`s `hold-end`, closes K, then exits" |
| A-I-06 | §4.2.5-R2 (h) CL-0 … CL-7; §4.2.5-R3 (e) GP-R3 | add **CL-G** as the first act; CL-0's lock with `lock-timeout` withdrawn and degraded mode; CL-3's `igr`/`cl-g` classes; CL-4's PK/2; CL-5b removes `grant.id` and K last; CL-6's baseline recomputation is class X. **Replace** the sentence "The kernel releases the lock when a process dies (PO-20 (f))" by LD-8 and GR-1 |
| A-I-07 | §4.2.5-R2 (j), (k), (l) | add **ST-1.i**; the SP cells of the (k) matrix read "SP, *if PID 1 can spawn it* (RL-1), and IGR (RL-0) for a catchable end"; **delete** "HL ends within Δ, then SP" in the ST-3 row and "(≤ Δ)" in the row "HL detecting an end", replacing them by the class-E and class-X statement of §7.7 W-5; (l) gains RO-1 … RO-6 and CX-5 |
| A-I-08 | §4.2.5-R4 (c), (h) | **replace** "The lock is released by the kernel at every exit, including a kill (PO-20 (f))" by "CP closes K at CQ-7 and on every failure path; LD-4"; CP-6's "PO-11 (d) bound" becomes PK/2; the start-timeout rule `⌈bound/1,000⌉ + 30` becomes N1 |
| A-I-09 | §4.2.5-R5 (c), (e), (f), (g), (j), (k) | OS-1 reads the baseline under **BSP**; CQ-1 opens K; CQ-4's τ check cites SD-1; CQ-5 is PK/2 seek-not-authorized; **replace Lemmas 2 and 3** by Lemmas 2′ and 3′ (§6.6); the lock paragraph: K, LD-2 … LD-5, and the sentence "The kernel releases the lock at every process exit, including a kill" is withdrawn; the PO-21 (s) row becomes (s′) |
| A-I-10 | §4.2.5-R5 (k), §4.2.5-R6 (f), (g) | CX-4 is marked **void** (§6.8), subject to DEC-5; "SB-2, except CX-4" and the other CX-4 qualifiers are retired accordingly; CX-5 is added |
| A-I-11 | §4.3.3 baseline | the backstop's loaded properties (`RuntimeMaxSec`, `TimeoutStopSec`) and the start-timeout rule N1 are baselined |
| A-I-12 | §4.4.2a | PO-20 (f) becomes (f′) (§4.4); PO-11 (d) becomes (d′) (§7.10) |
| A-I-13 | §4.4.2b | PO-21 (c) becomes (c′) (§5.8); the (s) wording is withdrawn |
| A-I-14 | §4.4.3 citation order; §4.4.1 | add OH-S2b (§11); the PO-11 (d) citation step is removed; HF-10 and HF-11 gain K's path |
| A-I-15 | §4.7.4 | add the §11 rows; extend OH-S4's test list with (30) … (35) |

### Part II. Rows that depend on the chosen Route 3 outcome

| # | Location | Action |
|---|---|---|
| A-II-01 | §4.1.3 TR-9; add TR-6a′ | the entry's interpreter becomes `/usr/bin/python3.14 -I -S`. The root roles' trust-path rows are fixed by the outcome: **LIT-FULL**, the static images; **SSW (after §0.2)**, TR-6a′ *"the first image is `rp11-rootexec`, which writes `rp11-helper-env/1` and executes `python3.14 -I -S`"* |
| A-II-02 | §4.1.3, D3-R4 note on TR-6a | CP's program is the outcome's CP image |
| A-II-03 | §4.2.4, the verified-exec stub line | BQ-3: `/usr/bin/python3.14` with the HB-1 sentence, or the installer's replacement |
| A-II-04 | §4.2.5-R2 (e), (f), (i) | the literals take the outcome's first image (the SSW literals of §9.7 are the only fully stated form) |
| A-II-05 | §4.2.5-R4 (b); T-B1 | the unit's one added line is the outcome's `ExecStartPre=+` line, and T-B1 admits exactly it |
| A-II-06 | §4.2.5-R4 (h); §4.3.3 baseline | the `ExecStartPre` normalization (`path`, `argv`, `+`); `files` gains every installed image |
| A-II-07 | §4.4.1 | HF-10 and HF-11 gain every image path |
| A-II-08 | §4.4.2 PO-19 | the scope text of §9.8 per outcome; `/usr/bin/python3.12` becomes `/usr/bin/python3.14` for the entry |
| A-II-09 | §4.5 | the rebuild produces one image per source file; `expected.sha256` gains four rows per added image; the independent bindings of §9.11 apply to each |
| A-II-10 | §4.7.1 M-5 | entry interpreter `/usr/bin/python3.14`; every installed image is a root-owned `0755` regular file pinned by digest. D-1's text is unchanged |
| A-II-11 | §4.6.2-R1 RB-1 | every installed image is a member of tree **L**; K and `grant.id` are not RB-1 objects |
| A-II-12 | §4.2.4-R1 PT-8 | "(Python 3.12 has no wrapper)" becomes "CPython 3.14.4 has no `os` wrapper [R2 §10.5]" for entry-side Python; a static image calls `renameat2` directly |
| A-II-13 | C11 `:688`, `:903–904`; D2 `:436`, `:1256`, `:1258`, `:1567–1568` | the dated amendment notes of §9.6.2 (A10, B5) |

## Appendix B. Exact amendments needed in the operational draft

The draft, [`phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`](phase-5-0-p5-r5-operational-evidence-authorization-prompt.md),
is a **draft that authorizes nothing**, and this assignment does not edit it. These
are the **content obligations** for the OH-S3 successor (OH-S3S), by the draft's own
section and row identifiers. The final bytes are composed under that slice's
authority. Each new value follows the draft's typed-placeholder rule of §0 (no value
is filled by the operator's judgement).

| # | Draft location | Content to add or change |
|---|---|---|
| B-01 | §4.5 Maintainer inputs | new inputs, supplied only in the A-2 record: `MI.pk_op_ms`, `MI.pk_call_ms`, `MI.reap_grace_ms`, `MI.lock_wait_ms`, `MI.slice_ms`, `MI.stop_timeout_s`, `MI.bs_runtime_s`, `MI.backstop_period_s`, `MI.backstop_max`, `MI.reserve_ms`, `MI.act_wait_s`, `MI.journal_max_bytes`, the existing lease parameters, `MI.image_sha256[]` (one per root-procedure image the outcome installs), `MI.launcher_sha256`, `MI.activation_id` |
| B-02 | §4.1 row A-2 | the A-2 record also quotes: N1 … N4 as evaluated **necessary conditions**, the route (iii-a) pre-`stop` condition OC-1 … OC-3, the sentence *"the consume step is part of the start; an activation admits one start attempt while every act stays within the pass's authorization"*, and the sentence *"no elapsed time is claimed for any class-X operation"* |
| B-03 | §4.2 Authorization matrix | separate rows: `AP-2` (the holder, with its `act_wait_s`), the operator's single `start` (only after `hold-start`), the executor's route (iii-a) `stop` (only under OC-1 … OC-3), the automatic CL triggers (`stop-post`, `backstop`) and `attest` |
| B-04 | §6 Pass A (before Band A1) | the activation chain as **admission rows**: AP-0's conditions (including drift of every image digest and the §7.6 arithmetic), AP-1, AP-2, and the evidence each returns. The pass's own acts remain the entry's, started by one `start` |
| B-05 | §9.5.3 Interruption (C-15) | route (iii-a) only while OC-1 … OC-3 hold, with its pre-`stop` read recorded as operational evidence; **never** while the unit is `activating`; a hung consume step ended only by the start timeout (class M), with CP's own elapsed time **not claimed**; a failed consume step is **not** a pass |
| B-06 | §11 Stop conditions | add `lock-object`, `capture-baseline-unstable`, `grant-not-seen`, `stop-control-unconfirmed`, `act-unconfirmed`, `invalid-journal`, `consume-failed {CQ-5}` and INVALID RUN on any drift of the §9.11 list. **Stop, record, never repair** applies |
| B-07 | §13.1 Intended changes and §13.2 survey | add K, `grant.id`, tree **P**, the rule (G1 → G3), the claim and consume evidence, the transient units and every record; the final survey adds K absent and the rule absent, each with PK *not authorized* from PK/2 |
| B-08 | §14 Handback template | add `lock`, `grant_identity`, `pk` (with `reap_grace_ms` and `abandoned`), `release`, `capture`, `helper` and `params` with `sizing` (§8.5), and the journals' digests and lengths (OH-D-9). **Observed** elapsed times are recorded as observations and never as bounds |
| B-09 | §3 Binding decisions | add rows for OH-D-10 (A) with OS-6 and, once recorded, for the Route 3 decision (WP-9) or the §0.2 change that precedes it |
| B-10 | `PIN.interpreter` (`:342`), `OP.interpreter_version` (`:407`) | **unchanged**: `venv-web` CPython 3.12 is Role F and runs the suite and Pass A acts A1-S1 and A1-13. State this explicitly so it is not read as the entry interpreter |
| B-11 | any sentence of the draft that states or implies a cleanup, consume or activation time | **none was found by the fixed-string search of this assignment** (bound, latency, timeout, within S, TimeoutStop, RuntimeMax); OH-S3S repeats the search and rejects any addition that does |
| B-12 | §6 Pass A, the executor's wait | the executor waits at most `act_wait_s` for the `act` record or the holder's end, then reports HARD STOP `act-unconfirmed`, acting on nothing |

## Appendix C. Identifier cross-check against the accepted R2 record, and against R1

### C.1 Returned items and MF identifiers against the accepted R2 record

Every returned item and every MF identifier named in the prompt appears in the
accepted R2 record at the location shown.

| Item | R2 location | R2 verdict | Where this proposal addresses it |
|---|---|---|---|
| PO-20 (f) | §7 table, §R2-6 | refuted | §4 |
| PO-21 (c) | §8 table, §R2-6 | refuted | §5 |
| PO-21 (s) | §8 table, §R2-6 | refuted | §6 |
| PO-11 (d) | §6.4, §R2-6 | not established | §7 |
| PO-12, AS-8 | §10.4, §R2-6 | refuted | §9 |
| PO-12′ | §10.4, §R2-6 | source-established; binding needs MF-4 | §9.8 |
| PO-19 | §11, §R2-6 | not established (MF-1, MF-2) | §9.8 |
| PO-17 | §12.9, §R2-6 | not evaluated | §9.10 |
| MF-1 … MF-8 | §14.3 | open | §10 |
| X-1 | §15.4 | cross-cutting finding | §9.1, §13.1 |

### C.2 R1 identifiers: carried, renamed, withdrawn

| R1 identifier | In this proposal |
|---|---|
| LD-1 … LD-9, GR-1, PO-20 (f′) | carried; LD-1 gains GI-1; LD-3 (d), LD-5, LD-6 corrected (§4) |
| RL-0 … RL-5, IL, RO-1 … RO-3, PO-21 (c′), ALT-SENT | carried; the latency column withdrawn; IL′, RO-4 … RO-6, GRR, CL-G added (§5) |
| IGR | carried and rewritten: one site, latch, flag-only handlers, GRR, no time claim (§5.7, §7.8) |
| SD-1, BSP, SD-2, SD-3, PO-21 (s′), CX-4 void, CX-5 | carried unchanged (§6) |
| PK/2, `pk_op_ms`, `pk_call_ms`, PO-11 (d′) | carried; `reap_grace_ms` and the abandon rule added (§7.5, §7.10) |
| the R1 budget table and the S grammar | **withdrawn** (§7.7 W-1, W-6, W-7) |
| HS-1 … HS-6 | carried (§7.5), no longer tied to a static first image |
| RT3-A, RX (`rp11-rootexec`) | renamed **SSW** and described as a scope-change alternative (§9.7) |
| RT3-B | renamed **SCDC** |
| RT3-C | folded into **LIT-FULL** and **LIT-DR1** (§9.4) |
| RT3-D, RT3-E, RT3-F | rejected, with their R1 reasons (§9.4) |
| RT3-Z | renamed **ACCEPT-X1** |
| HB-1 | carried; depends on BQ-3 |
| RR-1 … RR-11 | replaced by SR-1 … SR-11 (§14.2) |
| NT-LD, NT-RL, NT-SD, NT-PK, NT-HS | carried, corrected where they asserted a bound (§§4, 5, 7) |
| NT-RX-1 … 9 | replaced by NT-RH-1 … 5, NT-LR-1, 2 and NT-SSW-1 … 3 (§9.14) |
| INV-1 … INV-15 | carried; INV-4, INV-7, INV-8, INV-11 corrected; INV-16 … INV-18 added (§8.6) |
| DEC-1 (Route 3) | **withdrawn** (§12.2) |
| DEC-2, DEC-3, DEC-4, DEC-5, DEC-6 | DEC-1, DEC-2 (with BS-RM), DEC-3 (with GI-1), DEC-4, DEC-5 (§12.1). DEC-6 is new (signal and removal discipline) |
| Appendix A rows A-01 … A-30 | split into Part I (A-I-01 … 15) and Part II (A-II-01 … 13) |
| Appendix B rows B-01 … B-10 | carried and extended; B-11 and B-12 new |
| OH-S0d, OH-S2b, OH-S3S, OH-S4, OH-S4p, H-0M1, H-0M2, G-0 … G-7 | carried; G-1 split into G-1a and G-1b; 2R and 2R′ added (§11) |

## Appendix D. Remediation map

| Finding and item | Closed in |
|---|---|
| R2-F1 (1) preserve R1 unchanged and state that RT3-A did not meet the boundary | the document header; §0.1; §9.1 |
| R2-F1 (2) restore the accepted Route 3 meaning throughout | §0.1; §9.1; §9.2 (LR-1 … LR-6); the whole of §9 |
| R2-F1 (3) a decision-ready concrete design only if evidence suffices | §9.3 (it does not) |
| R2-F1 (4) otherwise exact bounded alternatives, the work needed, and the hard stop | §9.4; §9.5; the terminal state of the header and §0.4 |
| R2-F1 (5) RT3-A under a new name, as a scope-change alternative, with the baseline decision needed | §9.4; §9.7 |
| R2-F1 (6) no scope change inside DEC-1; §0.2 change control | §12.1 (DEC-1 withdrawn and replaced); §12.2 (BC-1 … BC-5); §9.7 |
| R2-F1 (7) re-evaluate Role A–H, PO-12′, PO-19, MF-1 … MF-8, OH-S4 / OH-S4p, the rebuild chain, PO-17, the surface comparison and the successor order | §9.6; §9.8; §10; §9.10; §9.11; §9.13; §11 |
| R2-F1 (8) root-owned dynamic inputs are still inputs | §9.9; §9.8 |
| R2-F2 (1) inventory every blocking operation | §7.3 |
| R2-F2 (2) enforced versus merely expected | §7.2 (E, M, C, X); §7.3 |
| R2-F2 (3) no bound for kernel or filesystem work from a fixed margin | §7.1; §7.6; §7.7 |
| R2-F2 (4) a deadline with a fail-closed consequence, or withdraw and state termination and recovery | §7.3; §7.4; §7.7 (withdrawals); §7.9 |
| R2-F2 (5) interruption of CL at the stop timeout, mapped to a state and a next owner | §7.9, IM-L (L0 … L9); IM-I; IM-C; IM-B; §8.3 |
| R2-F2 (6) when the holder installs handlers relative to AM-2; no reliance on a `finally` completing in time | §7.8 (SG-1 … SG-8); §5.4 (IL, IL′) |
| R2-F2 (7) a signal during IGR; re-entry; a second signal | §5.7 (IGR-0); §7.8 (SG-2, SG-5, SG-7); §5.5 rows 16, 17; §7.9 IM-I |
| R2-F2 (8) correct every affected formula, table, invariant, test, Appendix A and B item, and parameter | §§4.7 … 4.10; §5.3; §5.7; §7.6; §8; Appendices A, B; §12.1 |
| R2-F2 (9) retain PO-11 (d′) | §7.10 |

---

## Closing statement

This proposal ends at **`HARD STOP: concrete Route 3 not established`**. The repaired
activation design (§§2 … 8) is complete and awaits independent review. The Route 3
question is returned as an exact set of alternatives (§9.4) and the exact work that
would make a literal Route 3 decision-ready (§9.5). No scope change is made or
requested, no successor is authorized, and R1 is unchanged.
