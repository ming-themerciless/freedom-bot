# Proposal — OH-S3 R1: repaired activation design and concrete Route 3

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R1-20261007-01`

Date: 2026-10-07

Executor: Claude Code (Sonnet 5.5) on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Independent reviewer: Codex · Decision owner: Peter Duscha

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r1-design-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r1-design-remediation-claude-prompt.md),
**9693 bytes, SHA-256
`8e4d2a95092b15aec184b7099716fd9f6f56d4a3695aa8e70bc58188bf2b8c00`**,
recomputed with `wc -c` and `sha256sum` before any edit and equal to the pin in
the [authority record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r1-design-remediation-authority.md).

Durable handback: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r1-design-remediation-handback.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r1-design-remediation-handback.md).

Basis (all accepted, all inactive): the cumulative
[OH-S2 R2 citation record](phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md) and
its [acceptance](project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-acceptance.md);
the [one-host design amendment](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md)
through D3-R6 and its
[acceptance](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-acceptance.md);
the [cumulative R3 H-0 completeness proposal](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-proposal.md)
and its [acceptance](project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r3-acceptance.md);
the [composed H-0 and U-9 acceptance](project-review-2026-10-06-p5-r5-rp11-h1-h0g-r1-acceptance-and-u9.md);
the [C11 launcher contract](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md)
and [D2 static launcher design](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md).

**Terminal state: `OH-S3 R1 DESIGN REMEDIATION READY FOR REVIEW`.** No `HARD STOP`
condition arose (§0.4). This document is a **proposal only**: inactive,
unreviewed and unaccepted. It changes no accepted record, no source, test,
configuration, unit, rule or launcher byte. It authorizes no host access,
implementation, build, test, cleanup, activation, successor slice, commit or
push. Everything marked *proposed* is a proposal for Codex's independent review
and Peter Duscha's later recorded decision. Naming a successor in §11 does not
authorize it.

---

## 0. Outcome and recommendation

### 0.1 In one page

The activation design and Route 1 both failed for reasons that are narrower than
the accepted text made them look. This proposal keeps what the accepted design
proved and replaces only what the R2 evidence refuted.

* **The grant boundary and the one-start-attempt contract do not depend on the
  four refuted items.** They rest on the claim directory (SB-1), PID 1's
  inactive-entry record (SB-2), the rule token (SB-3), CP's journaled removal
  and *not authorized* check (CQ-3, CQ-5) and systemd's `ExecStartPre=` order
  (PO-21 (o)). They do **not** rest on the lock, on the hold loop, on
  `ExecStopPost=`, on the backstop or on any polling bound (§2). That is why the
  four items can be repaired by tightening machinery around the boundary, without
  weakening LB-2S, A-2, the start-only grant, the one start attempt, the
  no-follow source-consumption contract, evidence durability or any fail-closed
  rule.
* **PO-20 (f), lock release.** A `flock` lock belongs to an *open file
  description* and is released when the **last** reference to it is closed, not
  when "the process ends". The repair is lock discipline LD-1 … LD-9 (§4): one
  root-only lock object, one owning process, descriptors that are never
  inherited or passed, explicit close points, a bounded wait, and grant removal
  that never waits for the lock. A retained lock can then delay or refuse work.
  It can never keep a grant alive or let a start through.
* **PO-21 (c), `ExecStopPost=`.** It is skipped when PID 1 cannot spawn it. The
  repair is a **recovery ladder** RL-0 … RL-5 (§5) whose first rung, an *inline
  grant release* inside the dying holder, needs no spawn at all. A live rule
  whose holder has gone is shown to be **inert** (it cannot produce a pass). The
  one failure that remains outside the authorized guarantee is named (RO-1).
* **PO-21 (s), `InactiveEnterTimestampMonotonic`.** The strict, every-transition
  premise is withdrawn. The valid discriminator is *inequality with a baseline
  that has been separated from the monotonic clock* (SD-1, BSP, §6). It needs no
  strictness, tolerates `reset-failed`, reload, re-exec and same-microsecond
  observations, and makes residual **CX-4 void** under R2's own (accepted) PO-21
  (u).
* **PO-11 (d), the Polkit reload bound.** No bound is invented and nothing polls
  without a bound. The design claims **nothing** about Polkit internals. It uses
  one **operational timeout family** (`pk_op_ms`, `pk_call_ms`, §7) enforced by
  the helpers. A timeout is a failure, every failure refuses the start or ends
  the activation, and a *not authorized* answer is a sound observation whatever
  the reload latency was.
* **Route 3 (§9).** Route 1 assumed a clean interpreter start-up. R2 refuted
  that for root helpers, which start under PID 1's open block (R2 X-1). The
  recommended Route 3 (**RT3-A**) puts a **static, environment-ignoring first
  image**, `rp11-rootexec`, in front of every root helper, built by the already
  accepted reproducible launcher chain. No Python, loader or `MIMALLOC_*`
  input can then come from the manager. The entry keeps its accepted launcher
  with one literal retargeted to `/usr/bin/python3.14`. PO-12′ and PO-19 remain
  necessary, **narrowed** to what is left: root-owned *file* inputs of one
  interpreter and its closure (§9.9). The recommendation is compared with a
  Python-free alternative (RT3-B) and four rejected routes (§9.2, §9.12).
* **MF-1 … MF-8 and gates (§10, §11).** Route 3 eliminates none of them, narrows
  two (MF-1, MF-2), moves one (MF-4) and leaves five unchanged. Each has a
  minimum observing slice, privilege, path scope, evidence, drift trigger and
  dependent gate. A staged successor order with review gates is proposed, none
  authorized.
* **Peter's choices (§12).** Six decisions are needed. Two supersede or narrow
  accepted decisions (D-3's Route 1; the CX-4 residual). Each has a
  recommendation and bounded alternatives.

### 0.2 Returned items, repair and location

| # | Returned item (accepted R2 verdict) | Repair in this proposal | Section |
|---|---|---|---|
| 1 | PO-20 (f) **refuted**: "released when the process ends" | LD-1 … LD-9; PO-20 (f′); GR-1 (grant removal never waits for the lock); relocation of the lock to a root-only object | §4 |
| 2 | PO-21 (c) **refuted**: `ExecStopPost=` "for every cause" | recovery ladder RL-0 … RL-5; inline grant release IGR; inertness lemma IL; residual RO-1; PO-21 (c′) | §5 |
| 3 | PO-21 (s) **refuted**: every-transition wording, strictness | discriminator SD-1 with BSP; handling table; PO-21 (s′); CX-4 void under PO-21 (u) | §6 |
| 4 | PO-11 (d) **not established**: no citable bound | operational timeout family; procedure PK/2; budgets; PO-11 (d′) states that no bound is claimed | §7 |
| 5 | PO-12, AS-8 **refuted**; Route 1 returned | RT3-A, with `rp11-rootexec`; PO-12′ and PO-19 narrowed; Role A–H dispositions | §9 |
| 6 | PO-19 **not established** (MF-1, MF-2); PO-17 **not evaluated** (OH-S4p) | binding tuple restated; byte-level OH-S4p boundary | §9.9, §9.10 |
| 7 | MF-1 … MF-8 **open** | disposition table, observing slices, drift triggers | §10 |

### 0.3 What this proposal does not do

It does not claim any citation, fact or acceptance. Every new host-behaviour
statement is a **proposed proof obligation** (§1.3), version-bound and paired
with the fact that fixes its version. It does not implement, rebuild, install,
test or observe anything. It does not edit the operational draft, the accepted
design, the C11 or D2 records, the R2 record, source code, tests, service files,
the decision register or the change log. It does not select a third-party
artifact and performed no network research.

### 0.4 Terminal-state check

The prompt defines one `HARD STOP` on the authority side (prompt identity
mismatch) and one conditional `HARD STOP` for Route 3 (repository evidence
insufficient to choose a safe concrete design). The identity matched. Repository
evidence **is** sufficient to specify RT3-A concretely, because the accepted
launcher chain (D2, toolchain lock, reproducible build, independent decoding)
already exists and RT3-A reuses it unchanged in method (§9.4, §9.7). Two things
are **not** decided by evidence and are therefore returned as decisions, not
invented: the Route 3 choice itself (DEC-1) and the operational timeout values
(DEC-3).

---

## 1. Sources, method and fact classes

### 1.1 Repository documents read

Read completely: `.agents/AGENTS.md`; this assignment's prompt and authority.
Read by the sections the prompt names: `docs/implementation-plan.md` (reading
map, §§0, 14, 16, 17, 20); `docs/review/Handover information`; the restriction
banner of `docs/operations/disposable-test-server.md`; the accepted R2 citation
record (all of §§R2-0 … R2-6 and §§0 … 16, Appendices by reference only); the R2
handback and acceptance; the R1-F1 residual-risk acceptance (closure state
only); the accepted R3 proposal (§§6, 13, 14 and its acceptance); the
H-0/U-9 acceptance; the one-host design (§§0-R6, 4.1 … 4.7 and the D3-R6
sections, read in full for 4.2.1 … 4.2.5-R6, 4.4 and 4.7.4); C11 and D2 by the
sections the design cites (D2 §§5.1, 5.5 … 5.8, 6); the operational draft
`phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` by heading and
by the rows named in Appendix B (**not edited**); and the tracked, non-secret
launcher build files `infra/rp11-launch/{launch.c, start.s, select.h,
rp11-launch.ld, build.sh, toolchain.lock, expected.sha256}` and
`rp11-launch.x86_64.listing` lines 410 … 414, for sizes and structure only. Fixed
searches for the interpreter literal covered `tools/phase_5_0_evidence/rp11_launch.py`,
`infra/rp11-launch/verify/ctverify.py`, `tests/test_rp11_launch_source.py` and
the evidence-harness review manifest.

No host, retained-evidence path, secret-bearing path, credential, player datum
or network resource was touched. No recursive search was rooted at the
repository, a workspace root, home, `/opt`, `/var`, `/tmp` or `/`. Searches ran
over named documents or named source files, with **two disclosed exceptions**,
both inside the one documentation directory `docs/review/` and neither
recursive: a directory listing filtered by name, and one fixed-string search over
that directory's `*.md` files to locate the document that defines "DR1" and
"Route 3" (handback §5).

### 1.2 Method

1. Re-derive, from the accepted text, **which claim rests on which mechanism**
   (§2). Repair only where a refuted premise is load-bearing.
2. For each repair, state the correct statement from the accepted R2 evidence
   first, then the design that does not need more than that evidence.
3. Where a repair needs a host fact R2 did not establish, write it as a new
   **proposed** obligation. Never as a fact.
4. Give every wait, retry and poll a **finite, fail-closed** bound whose
   expiry has a defined consequence.
5. For Route 3, compare at least one bounded alternative and say what each
   adds to the trusted and runtime surface.

### 1.3 Fact classes used in this proposal

| Tag | Meaning |
|---|---|
| **[R2 §n]** | an accepted source or verdict in the accepted R2 record, section `n` |
| **[D §n]** | accepted inactive design text (one-host amendment through D3-R6), section `n` |
| **[R3 §n]** | accepted R3 text, section `n` |
| **[C11]**, **[D2]** | accepted launcher contract or static-launcher design |
| **[N]** | **new, proposed**: a design statement or proof obligation introduced here. It is not a fact. It needs citation, test or observation under its own gate |
| **[P]** | a **parameter** whose value Peter chooses (DEC-3) |

Identifiers introduced here (LD, GR, RL, IGR, IL, RO, SD, BSP, OP, RX, RT3, HS,
HB, DEC, G-) are **proposal-local** until accepted. They do not reuse any
accepted identifier except where a primed form (PO-20 (f′)) restates an
accepted one.

---

## 2. The safety kernel: what the accepted claims rest on

The four refuted items are all in machinery that surrounds the grant boundary.
Before changing anything, this section re-reads the accepted proofs and records
exactly which mechanism each safety claim cites. That reading is the licence for
every repair below. **Codex is asked to confirm it** (§14, question 1).

### 2.1 Claims, and what each rests on

| Claim | Accepted source | Rests on | Does **not** rest on |
|---|---|---|---|
| **G1.** No live grant at any instant from the `execve` of `ExecStart=` onward | [D §4.2.5-R4 (i)] | CQ-3's removal of the A1-intact rule, journaled `removed` (SB-3's token); CQ-5's PK *not authorized*; `ExecStart=` runs only after every `ExecStartPre=` exits `0` [R2 §8 (o)]; polkit authorizes `StartUnit` once [R2 §8 (p)]; `ACT` links the rule once (AM-2) | the lock, HL, `ExecStopPost=`, the backstop, any polling bound |
| **G2.** One start attempt per activation (contract OSA over 𝒜) | [D §4.2.5-R5 (f), R6 (e)] | SB-1 (the claim: `mkdirat` fails `EEXIST`); SB-2 (PID 1's inactive-entry record, τ); SB-3 (one removal token); attempts never overlap [R2 §8 (t)]; end states [R2 §8 (u)] | the lock, HL, `ExecStopPost=`, the backstop |
| **G3.** The grant is created once, only after A-2 and after the holder's baseline | [D §4.2.5-R2 (d), R5 (c)] | A-2's pins; AM-0 … AM-2 order; AP-0's absence conditions; one identifier and one unit name [R2 §8 (m)] | the lock |
| **G4.** No grant survives a kernel boot | [D §4.2.5-R2 (a) M-B] | the rule and `pass-a.json` live only on `/run` (tmpfs, cleared at every boot, [R2 §7 (g)]) | everything else |
| **G5.** A failed start is never recorded as a pass | [D §4.2.5-R5 (f) proof of 4] | a pass is claimed only from a consume journal with `consumed` plus a capture root | everything else |

I re-read §4.2.5-R4 (i) items 1 … 7, §4.2.5-R5 (f) Lemmas 1 … 3 and the proofs of
OSA 1 … 4, and §4.2.5-R6 (c) … (e). **No step in any of them cites lock
exclusivity, HL's timing, the stop-post trigger, the backstop or a Polkit
latency.** The only items that cite the lock are OS-5 and CX-1, both of which
the accepted text itself classes as **lifetime**, not grant, properties
([D §4.2.5-R5 (k)]: "a lifetime defect, not a grant defect").

### 2.2 Machinery that is hygiene or liveness

| Device | What it buys | What its failure costs |
|---|---|---|
| the activation lock (`flock`) | ordering of lifetime decisions (OS-5); clean, non-interleaved evidence | a refused start, a delayed HL end, a degraded (unordered) cleanup record |
| the hold loop HL and the lease L | bounds the activation's lifetime; ends it after a failed start or a pass | an activation that lasts until L, then ends by `RuntimeMaxSec=` |
| `ExecStopPost=` and the backstop | remove `pass-a.json`, tree directories and a *pre-pass* rule, and write the records | a pre-pass rule that stays live but **inert** (§5.4) until another rung acts or the host boots |
| Polkit waits (PK) | evidence that the grant is absent, and the positive control that makes that evidence meaningful | a refused start or a failed `ACT` (fail closed) |

### 2.3 Consequence

Every repair in §§4 … 7 is allowed to **fail closed to "no pass"**. None may
weaken G1 … G5. Where a repair adds a step to a safety path (BSP at the
baseline, PK/2 in CQ-5) it only **narrows** what can succeed. The safety kernel's
procedures (CQ-0 … CQ-7, SB-1 … SB-3, the claim, the rule and unit bytes) are
unchanged except for the textual amendments of Appendix A, each of which is a
fail-closed refinement.

---

## 3. Vocabulary used by the repairs

| Term | Meaning |
|---|---|
| **grant object** | the rule file `/run/polkit-1/rules.d/50-freedom-blades-rp11.rules` together with polkitd's loaded copy of it |
| **G0 … G4** | grant-object states. **G0** never linked, or cleared by a boot. **G1** linked: the file is present and A1-intact. **G2** unlinked, unconfirmed: the file is absent, but polkitd's loaded copy may still authorize until it reloads. This proposal claims **nothing** about how long that lasts. **G3** verified absent: the file is absent and a PK/2 *not authorized* was observed after the unlink in this activation. **G4** unremovable: the file is present and `unlinkat` fails |
| **holder (H)** | the PID-1-supervised transient service whose main process runs the `hold` role (AP-2) |
| **CP** | the capture unit's `ExecStartPre=+` consume step (CQ-0 … CQ-7) |
| **CL** | cleanup, in every trigger (`stop-post`, `backstop`, `attest`), including GP-R3 |
| **IGR** | *inline grant release*: new, the holder's own syscall-only removal of the rule on every catchable end (§5.7) |
| **BS** | the backstop procedure and its timer |
| **executor (X)**, **operator (O)** | the actor working under A-2 on `oracle-test`; the `ubuntu` client that issues the one `start` |
| **spawn** | creation of any child process by a root helper (`fork`, `vfork`, `clone`, `posix_spawn`, a `subprocess` call) |
| **owner (of a lock)** | the single process that opened the open file description the lock is attached to |
| **lock mode** | `held`, `degraded` (acquisition timed out, cleanup proceeded unordered) or `absent` (the lock object could not be opened) |
| **𝒜** | the authorized path set of [D §4.2.5-R6 (d)], unchanged |

---

## 4. Repair A — PO-20 (f): lock release and descriptor ownership

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
  mode `0700`, empty, with no `system.posix_acl_*` or capability extended
  attribute. The holder creates it at AM-0 with an exclusive `mkdirat` on a
  descriptor of `/run` (which never follows a final symbolic link and fails
  `EEXIST` for any existing name [R2 §7 (h)]), opens it, verifies type, owner,
  mode and `st_nlink`, and journals its `(dev, ino)` in `run-start`. AP-0
  requires K absent. K lies under `/run`, whose parent conditions already require
  a root-owned tmpfs directory without group or other write. K is cleared by
  every kernel boot (M-B). CL-5b removes it, through a descriptor re-verification
  against the journaled identity and only if empty, together with the other
  `/run` objects; a K left by a crash between its creation and the journal is
  class **S0** (reported, kept, cleared at the boot), exactly like the other
  run-unique `/run` leftovers of [D §4.2.5-R2 (h) CL-5b]. Nobody but root can open
  K, so no unprivileged process can hold the lock (f′-5).
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
  `spawn()` (HS-1, §9.5), which uses only a creation primitive that closes every
  descriptor ≥ 3 before `exec` and passes none (`close_fds=True`,
  `pass_fds=()`). (d) The static first image closes every descriptor ≥ 3 before
  it executes the helper (§9.4), so the helper starts with none of PID 1's
  descriptors. (e) A child's duplicate reference therefore exists only between
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
  `lock_wait_ms` [P] (§7.3: range 1,000 … 10,000, recommended 5,000), never by a
  count of sleeps, and always shorter than S by the inequality of §7.3. CP does
  not wait: one attempt, as accepted (AR-1). `EINTR` retries within the
  deadline. Any other error is "cannot acquire".
* **LD-6, grant removal never waits for the lock (GR-1).** CL-3, IGR and
  GP-R3's rule step do not require the lock. If CL cannot acquire K within
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
| K absent, not a directory, wrong owner or mode, unopenable | `consume-unidentified`: nothing created, SB-2 covers | `observation-failed`: the activation ends | `lock_mode: "absent"`, degraded | HARD STOP `lock-object` before AM-1; nothing is linked | no pass; the rule is removed by CL-3, IGR or CQ-3 |
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
| NT-LD-4 | K's creation and mode | K is `root:root`, `0700`, empty, no forbidden extended attribute; a non-root actor in the harness cannot open it |
| NT-LD-5 | `ubuntu`-style retention of the old `ubuntu`-owned directory lock | has **no effect** on CP, HL or CL once the lock object is K |
| NT-LD-6 | CL against a lock retained forever | CL reaches `lock_mode: "degraded"` before S, removes an A1-intact rule, writes its records, and is not killed by the stop timeout |
| NT-LD-7 | the arithmetic of §7.3 | AP-0 refuses any parameter set with `lock_wait_ms` + CL budget + PK budget ≥ S·1,000 |
| NT-LD-8 | HL's decision | `hold-end` is durable and K is closed before the process exits; a CP that acquires K in between refuses at CQ-4 |
| NT-LD-9 | PK subject | the subject child holds no lock descriptor, runs under the credentials in the H-1 record, and is killed and reaped after each call |

---

## 5. Repair B — PO-21 (c): `ExecStopPost=` is a rung, not a guarantee

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
* **H1, a hygiene guarantee, conditional.** *After the holder's main process
  ends, the rule is unlinked by the first rung of the ladder RL (§5.3) that can
  act. The time to that rung is an operational bound, not a claim about systemd
  or Polkit.*
* **Outside the guarantee (RO-1 … RO-3, §5.6).** Stated by name.

### 5.3 The recovery ladder RL-0 … RL-5

| Rung | Mechanism | Needs PID 1 to spawn something? | Covers | Operational latency |
|---|---|---|---|---|
| **RL-0** | **IGR**, the inline grant release in the holder (§5.7) | **no** | every *catchable* end of the holder's main process | before the process exits |
| **RL-1** | `ExecStopPost=` running CL with trigger `stop-post` | yes | every end after which PID 1 can spawn it | ≤ S |
| **RL-2** | the backstop timer's service running CL (BS-4) | yes | a stop-post that could not be spawned, or a CL that died | ≤ R + S per firing, at most `backstop_max` firings |
| **RL-3** | **CP at any later start** (CQ-3 in grant-priority form), by anyone | yes (a start needs it) | the rule itself, whenever any start is attempted | at that start |
| **RL-4** | a kernel boot clears `/run` (M-B) | no | everything under `/run` | the next boot |
| **RL-5** | attestation, trigger `attest` (record only; it removes nothing the boot did not already remove) | n/a | the *records* | under A-2, when the host is next reachable |

RL-0 is new. RL-1, RL-2, RL-4 and RL-5 are the accepted `SP`, `BS`, `BC` and
attestation mechanisms. RL-3 is accepted behaviour (§5.4 uses it) promoted to a
named rung. **PID 1 being unable to spawn is exactly the case in which RL-0 and
RL-4 can still act and RL-1 … RL-3 may not.**

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

IL says that a rule left live after the holder has gone is a *hygiene* matter.
It is still a Polkit grant of `start` for `ubuntu` (OH-D-6 says `ubuntu` already
has unrestricted `sudo`, so it adds no privilege). It cannot produce a pass, and
OH-D-7's "after the pass" is not engaged.

### 5.5 Terminal causes of the holder's main process

*Catchable* means a signal or an orderly end that the Python process can handle.
"IGR" means RL-0 removed an A1-intact rule before the process exited.

| # | Cause | Catchable? | RL-0 IGR | RL-1 stop-post | RL-2 backstop | RL-3 CP | RL-4 boot | Grant afterwards |
|---|---|---|---|---|---|---|---|---|
| 1 | HL's normal end (`exit 0`) | yes | removes | runs | if 1 cannot spawn | at a start | — | G1 → G2, then G3 by CL |
| 2 | `observation-failed` (non-zero exit) | yes | removes | runs | as 1 | as 1 | — | as 1 |
| 3 | unhandled exception, `SystemExit` | yes | removes (`finally`) | runs | as 1 | as 1 | — | as 1 |
| 4 | `SIGTERM` from a stop job | yes | removes | runs | as 1 | as 1 | — | as 1 |
| 5 | `RuntimeMaxSec=` expiry: `SIGTERM`, then `SIGKILL` after S [R2 §8 (d), (e)] | the first yes | removes at `SIGTERM` | runs | as 1 | as 1 | — | as 1 |
| 6 | orderly shutdown, reboot or `kexec` (EO, outside 𝒜): stop, then boot | yes | removes | runs (PO-21 (h)) | n/a | n/a | clears | G0 after the boot |
| 7 | `SIGINT`, `SIGHUP` | yes | removes | runs | as 1 | as 1 | — | as 1 |
| 8 | `SIGKILL` (a root act, or the escalation after S) | **no** | — | runs if PID 1 can spawn it | if 8's stop-post cannot spawn | at a start | clears | G1 live **inert** (IL) until a rung acts |
| 9 | a fatal signal in the interpreter (`SIGSEGV`, `SIGABRT`, `SIGILL`) | **no** | — | as 8 | as 8 | as 8 | clears | as 8 |
| 10 | kernel OOM kill | excluded by `OOMScoreAdjust=-1000` [R2 §8 (f)] | — | — | — | — | — | not applicable |
| 11 | a kill by a user-space OOM daemon | **no** (not covered by (f)) | — | as 8 | as 8 | as 8 | clears | as 8 |
| 12 | the holder never started: the first image is missing or cannot be executed | n/a | n/a | n/a | n/a | n/a | — | **no grant was ever linked**: AM-2 is the holder's act |
| 13 | PID 1 cannot spawn `ExecStopPost=` (result `resources`) [R2 §8 (c)] | any | removes if catchable | **does not run** | runs if PID 1 can spawn it | at a start | clears | catchable: G2 then G3 by RL-2; uncatchable: live inert, RO-1 |
| 14 | EU: power loss, panic, hard reset | no | — | — | — | — | clears | G0 after the boot; attestation records it |
| 15 | PID 1 is dead or hung | n/a | removes if catchable | no | no | no | clears | outside any unit guarantee [R2 §8 (c)]; a live rule is inert (IL) because no start can run |

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
  was already loaded. AP-0, H-2 and AM-0 verify those bytes before `ACT`
  (§9.7), so after `ACT` the cause is a root act (SL-1).
* **RO-3 (PID 1).** If PID 1 is dead or hung, nothing in any unit runs. That is
  outside every unit-level guarantee in the accepted record.

Root's deliberate acts (SL-1), DF-1 and the unremovable-rule class (GU) are
unchanged ([D §4.2.5-R2 (l)]).

### 5.7 RL-0: the inline grant release IGR *(proposed)*

* **When.** On every catchable end of the holder: the main loop's normal end,
  `observation-failed`, any exception or `SystemExit` (a `finally` around the
  whole holder body), and `SIGTERM`, `SIGINT` and `SIGHUP`. The handlers set a
  flag and raise one dedicated exception that every loop iteration and every
  return from a blocking call checks.
* **What it does, in order.** **IGR-1:** if the object at the rule path is
  A1-intact against the identity the holder itself recorded when it linked the
  rule (held in the process's memory and also journaled as the `file-identity`
  line, so a replaced or damaged journal cannot make IGR class the rule A0) and
  against the H-1 record's staged digest, re-verify it through a descriptor (type,
  `(dev, ino)`, uid and gid 0, mode `0644`, `st_nlink = 1`, full re-hash, no
  forbidden extended attribute), `unlinkat`, `fsync` the rules directory. If the
  rule is absent, IGR-1 does nothing. **IGR-2:** append
  `igr {step, class}` lines and, on success, `igr-removed {path, dev, ino}` if
  the journal still accepts them, as GP-R3 does (a failure to write evidence
  reduces what is claimed, never what is removed). **IGR-3:** nothing else. It
  leaves `pass-a.json`, the directories and the records to CL.
* **What it does not do.** No spawn, no PK, no lock, no network, no `fsync` of
  anything but the rules directory and the journal. So it is a handful of local
  system calls and cannot be starved by PID 1, by the lock or by Polkit. It does
  not claim `removed-verified`, which needs PK *not authorized* (CL-4).
* **Handler latency.** Every blocking call in the holder is bounded: its sleep is
  at most Δ ≤ 5 s, a spawn wait at most `pk_call_ms` ≤ 10 s, a lock wait at most
  `lock_wait_ms` ≤ 10 s. A catchable end is therefore acted on within about ten
  seconds. `RuntimeMaxSec=` sends `SIGTERM` first and `SIGKILL` only after S
  ([R2 §8 (e)]), and with the recommended values S ≥ 70 s (§7.3), so IGR has at
  least that long.
  *[N]* That Python handlers run when a bounded sleep or wait returns is a
  tested property (NT-RL-1), not a citation.
* **CL's view.** CL-3 reads an `igr-removed` line for the rule's identity as
  `removed-earlier`, and a `igr` intent without it as `absent-before-removal`.
  Either still needs CL-4's own PK *not authorized* for `st1-verified`, like
  CQ-3's removal.
* **Why it is independent of PID 1.** It runs in the process that PID 1 already
  started. It needs PID 1 only to have delivered the signal, which a stop job,
  `RuntimeMaxSec=` and an orderly shutdown all do by `SIGTERM`.

### 5.8 PO-21 (c′) *(proposed [N], text for [D §4.4.2b])*

> **(c′)** `ExecStopPost=` is run, as the unit's user, after the main process
> ends for each of these causes: exit `0`, a non-zero exit, any signal, `RuntimeMaxSec=`
> expiry, `systemctl stop`, a failure to execute `ExecStart=`, and a stop issued
> by an orderly shutdown, reboot, `kexec` or userspace-only restart, **provided
> PID 1 can spawn it**. If spawning fails, the unit enters `FINAL_SIGTERM` with
> result `resources` and `ExecStopPost=` does not run [R2 §8 (c)]. The design
> relies on `ExecStopPost=` as one rung of RL and never as a guarantee.

(c′) is the R2 evidence restated. It adds no new host fact. What RL adds as new
proposed behaviour is IGR (§5.7), the inertness lemma (§5.4) and the bounded
backstop of §7.3 (`backstop_max`).

### 5.9 Bounded alternative: a resident sentinel *(ALT-SENT, not recommended)*

A second long-lived root process, started at AK-1 before any grant exists, that
waits on a `pidfd` of the holder's main process and, when it ends for any cause,
performs IGR itself. It would close the **uncatchable** branch of RO-1 without
PID 1. It is not recommended because: (a) it adds a second long-lived root image
containing grant-removal code, including a re-hash for G-R1's descriptor
re-verification, which in a Python-free sentinel is new freestanding C and in a
Python sentinel is another unit PID 1 must have spawned and that is exposed to
the same signals; (b) it needs further host-behaviour citations (`pidfd_open`,
poll on process exit, the sentinel's own cgroup and kill behaviour); and (c) IL
already shows that the residual it closes is a pre-pass, inert grant. Peter may
elect it (DEC-2). If he does, OH-S4 gains a sentinel and a drill, and §5.6's RO-1
is narrowed to the loss of both the holder and the sentinel.

### 5.10 Negative tests *(proposed, for OH-S4)*

| ID | Case | Asserts |
|---|---|---|
| NT-RL-1 | a fake manager delivers each catchable cause of rows 1 … 7 with `ExecStopPost=` and the backstop both returning `resources` | the rule is unlinked **before the holder exits**, an `igr` line is written, no spawn occurred in IGR |
| NT-RL-2 | `SIGKILL` of the holder with both spawns failing (RO-1) | the rule stays live, a start attempt by the fake manager reaches CP, CP removes it (CQ-3 grant priority) and exits non-zero at CQ-4, and `ExecStart=` is never executed (IL) |
| NT-RL-3 | `SIGKILL` with stop-post failing but the backstop spawnable | the backstop's CL runs within R + S and records `st1-verified` or ST-1.ur |
| NT-RL-4 | `backstop_max` firings with every CL dying | the backstop disarms after the last, appends a journal line, and exits; no unbounded loop; the final state is recorded or left to M-B |
| NT-RL-5 | the installed helper image removed after `ACT` (RO-2) | IGR still ran for a catchable end, RL-1 and RL-2 fail identically, and AP-0 and H-2 would have refused a prior tamper |
| NT-RL-6 | a wedged holder (alive, not observing) | `RuntimeMaxSec=` delivers `SIGTERM`, IGR runs, the `SIGKILL` after S finds nothing to do |
| NT-RL-7 | IL over generated sequences | with the holder not `active` or `hold-end` present, no fake-manager path executes `ExecStart=` |
| NT-RL-8 | the terminal-cause table | every row 1 … 15 has a defined first removing rung and a defined residual |

---

## 6. Repair C — PO-21 (s): a valid start-history discriminator

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
  repeats, at most 5 times, then exits `capture-baseline-unstable` (non-zero; CL
  runs; nothing has been linked). The baseline is `B₀ = (m_a, τ₀, ActiveState,
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

## 7. Repair D — PO-11 (d): an operational timeout, no claim about Polkit

### 7.1 What the accepted text says and what is true

[D §4.4.2a] PO-11 (d): *after a rules file is created by `linkat` in, or removed
by `unlinkat` from, `/etc/polkit-1/rules.d`, polkitd reloads its rules within a
cited bound. That bound becomes A-2's PO-11 (d) value. If no bound can be cited,
`ACT` and `DEACT` return to design review rather than polling without a bound.*
(f)(iii) extends it to `/run/polkit-1/rules.d`. The bound is used by AV-1, CL-4,
CQ-5 and GP-3, by A-2's pin, by AR-4's start timeout and by S's range.

**What is true** [R2 §6.3, §6.4 (d)]: reload is triggered only by a GIO monitor
event for a `.rules` name; it is synchronous in the monitor callback; there is
**no polkit-side timer, coalescing or bound** (the source's own TODO says so).
Delivery latency belongs to GLib and inotify, which are outside the authorized
sources. **No bound is citable.** The accepted design then says `ACT` and
`DEACT` return to design review "rather than polling without a bound". That is
this section.

### 7.2 What can and cannot be said

* A PK call is a query to polkitd's **current** rule set. `authorized` after the
  link shows the loaded copy contains the rule. `not authorized` after the file
  is gone shows that polkitd's loaded copy contains no matching `YES` at that
  query. Nothing re-links the rule (G1, §2.1), so no later reload can add it back
  and the observation stays true. An error or a timeout shows nothing.
* **Not claimed:** how long polkitd takes to notice a creation or a removal, or
  whether it always does (for example after an inotify queue overflow).
* Therefore the bound is **operational**. It is chosen and enforced by the helpers.
  Its expiry is a failure, never evidence.

### 7.3 Parameters and arithmetic *(proposed [P]; values are DEC-3)*

| Name | Meaning | Grammar | Recommended |
|---|---|---|---|
| `pk_op_ms` (**P**) | total time of one PK/2 series | 5,000 … 60,000 | 30,000 |
| `pk_call_ms` (**c**) | deadline of one PK call | 1,000 … 10,000, and c ≤ P | 5,000 |
| `lock_wait_ms` (**λ**) | CL's lock acquisition deadline (LD-5) | 1,000 … 10,000 | 5,000 |
| `stop_timeout_s` (**S**) | the holder's `TimeoutStopSec=`, which bounds CL | ⌈λ/1,000⌉ + ⌈(P + c)/1,000⌉ + 30 … 600 | 120 |
| `backstop_period_s` (**R**) | the backstop timer's period | 30 … 600 (as accepted) | 60 |
| `backstop_max` (**B**) | the most firings that run CL before the backstop disarms | 1 … 99 | 20 |
| `start_window_s` (W), `lease_s` (L), `poll_ms` (Δ) | unchanged | as accepted | as accepted |

**The capture unit's start timeout T_s** (the loaded `TimeoutStartUSec`, recorded
in the H-1 baseline) must be finite and satisfy
`T_s ≥ ⌈(P + c)/1,000⌉ + 30` seconds (AR-4, generalized; the accepted
`⌈bound/1,000⌉ + 30` becomes this). **HF-16 recorded `DefaultTimeoutStartUSec=1min
30s`**, so with the unit's default timeout, **P + c ≤ 60,000**. With the
recommended values, P + c = 35,000, T_s must be at least 65 s, and the 90 s
default leaves 25 s. A larger P would need an explicit `TimeoutStartSec=` line,
which changes the reviewed unit bytes (T-B1) and is the second alternative of
DEC-3.

**Budgets that follow:**

| Procedure | Worst-case duration | Bound |
|---|---|---|
| one PK/2 series | P + c | no call starts after P; each call ends by its deadline c |
| CP | the unit's own start timeout T_s | finite (AR-4); expiry ends the attempt `failed` |
| CL | λ + local work + (P + c) | **< S** by the S grammar. S also bounds it through `TimeoutStopSec=` |
| the backstop, in total | B·(R + S) | `backstop_max` (B), then it disarms |
| HL | the lease L | `RuntimeMaxSec=` |
| BSP | 5 retries of ≥ 2 ms | five |

With the recommended values the S floor is 5 + 35 + 30 = 70 s, so S = 120 s
leaves 50 s for CL's local work.

### 7.4 PK/2 *(proposed; replaces `pk-root/1` of [D §4.2.5-R1 (f)])*

* **Subject.** One subject process **per call**, created by `spawn()` (LD-3) with
  `close_fds=True`, in its own session, with the supplementary groups, GID and UID
  that the H-1 record holds for `ubuntu`, executing `/usr/bin/sleep 60`. It is
  killed and reaped after the call. If the tool dies it lives at most 60 s and
  holds no lock descriptor.
* **Call.** `/usr/bin/pkcheck --action-id org.freedesktop.systemd1.manage-units
  --process ⟨pid⟩,⟨start-time⟩,⟨uid⟩ --detail unit rp11-capture-pass-a.service
  --detail verb ⟨verb⟩`, as **root**, without `--allow-user-interaction`, with the
  closed environment of HS-2 (§9.5), under the deadline c. The process is killed at c.
* **Outcome of one call.** Exit `0` is `authorized`. Exit `1` or `2` is
  `not-authorized` ([R2 §6.4 (e)]: 1 not authorized, 2 challenge). Any other
  status, a spawn failure, an unparsable result or the deadline is `error`.
* **Series.** Three modes: **seek-authorized** stops at the first `authorized`;
  **seek-not-authorized** stops at the first `not-authorized`;
  **first-decisive** stops at the first `authorized` or `not-authorized`. An
  `error` never ends a series: it retries on the closed schedule, offsets 0, 250,
  500, 1,000, 2,000, 3,000 and 4,000 ms, then every 2,000 ms, measured on
  `CLOCK_MONOTONIC`. **No call starts after P has elapsed.** A call that starts by P
  ends by P + c.
* **Result.** `authorized`, `not-authorized`, or `unconfirmed`, with a reason:
  `only-errors`, `still-authorized` (a seek-not-authorized series saw only
  `authorized` and errors) or `not-seen` (a seek-authorized series saw only
  `not-authorized` and errors).
* PK starts, stops or changes nothing (as accepted).

### 7.5 What each step does, and what a timeout does

| Step | Mode | Budget | On `unconfirmed` |
|---|---|---|---|
| AV-1, positive control for verb `start` | seek-authorized | P | `ACT` ends HARD STOP `grant-not-seen`; CL runs, rule first. No pass. PK's sensitivity was not shown, so nothing later may be read as evidence |
| AV-1, negative control for verb `stop` (AR-7) | first-decisive | P | `authorized` fails `ACT` at once. `unconfirmed` fails `ACT` (HARD STOP `stop-control-unconfirmed`) |
| CQ-5, consume post-check | seek-not-authorized | P | CP exits non-zero `consume-failed {CQ-5, removed-unconfirmed}`; **`ExecStart=` is not executed**; CL re-checks |
| CL-4 | seek-not-authorized | P | rule class `removed-unconfirmed`; outcome HARD STOP; the backstop retries within `backstop_max` |
| GP-R3's grant post-check | as CL-4, result held in memory | P | as CL-4 |
| attestation, `cleared-by-boot` | seek-not-authorized | P | no `st1-verified` record is written |
| H-2, AP-0, CL-6 | **do not run PK** | — | CL-6 uses CL-4's result |
| drills (OH-S8b) | as the step they exercise | P | as that step |

### 7.6 What a timeout can and cannot leave

* **G1 is unaffected.** A CQ-5 timeout blocks `ExecStart=`. The rule is already
  gone from the directory (CQ-3).
* **After CQ-5 `unconfirmed(still-authorized)`**, polkitd may still authorize a
  `start` for `ubuntu`, which is G2 in the visible-lag state. A later start
  reaches CQ-2, finds the claim (`EEXIST`) and exits with nothing touched (SB-1).
  No pass.
* **After AV-1 `grant-not-seen`**, polkitd may load the rule late. CL removes the
  file, and any reload that follows reads a directory without it.
* **No unbounded poll exists.** Every series ends at P (+ c); the lock wait ends
  at λ; BSP ends after five reads; HL ends at L; the backstop ends after B
  firings; PK never runs outside these procedures.

### 7.7 Separating the operational timeout from Polkit internals

The proposal asserts nothing about polkitd's reload. It does not rely on reload
being synchronous, prompt or bounded. Each series records `pk: {procedure:
"pk-root/2", mode, op_ms, call_ms, calls, elapsed_ms, outcome, reason}`. A
reviewer reads P as an operator's timeout and an `unconfirmed` as a failure.
One more mechanism was considered and is **not** proposed (NUDGE): creating and
removing an empty `*.rules` file in a monitored directory to force a reload
after a suspected missed event. It would add a write path into polkit's rules
directory, whose effect on the reload is a GLib behaviour no accepted record
cites. The safe response to a missed event is the failure above.

### 7.8 PO-11 (d′) *(proposed [N], text for [D §4.4.2a])*

> **(d′)** *No bound is claimed on the time between the creation or removal of a
> polkit rules file and polkitd's use of that change.* A PK call returns the
> decision of polkitd's **current** rule set at the instant of the call. The
> design waits for a stated decision for at most `pk_op_ms`, enforced by the
> caller, and treats every other result, including the expiry of that time, as
> *unconfirmed*, which fails closed at every use (§7.5). The same holds for
> `/run/polkit-1/rules.d` ((f)(iii)). Obligations (e), (f)(i), (f)(ii) and
> (f)(iv) stand as accepted.

AP-0's requirement "the PO-11 (d) … citations accepted" becomes "PO-11 (d′)
accepted" and the parameter grammar and arithmetic of §7.3 hold. **This needs
no host citation.** The block that returned `ACT` and `DEACT` to design review
is answered by the design itself: no bound is cited, and nothing polls without
one.

### 7.9 Negative tests *(proposed, for OH-S4)*

| ID | Case | Asserts |
|---|---|---|
| NT-PK-1 | a fake `pkcheck` that hangs | each call is killed at c; no call starts after P; the series ends by P + c |
| NT-PK-2 | a fake polkit that keeps answering `authorized` for P − ε, then `not authorized` | CQ-5 passes only on the first `not-authorized`; with latency > P it fails closed |
| NT-PK-3 | exit statuses 3, 126, 127 and a signal death | counted as `error`, never as `not-authorized` |
| NT-PK-4 | AP-0 with parameters that violate the §7.3 inequalities | INVALID RUN; no lock object, no grant |
| NT-PK-5 | code scan | every loop on a PK or lock path carries a monotonic deadline; there is no unbounded `while` and no sleep-count bound |
| NT-PK-6 | `removed-verified` | requires AV-1's `authorized` in the same activation and a later `not-authorized` from the same procedure |
| NT-PK-7 | `grant-not-seen` | the rule is removed by CL and the activation ends with no pass |
| NT-PK-8 | the backstop under a permanently failing PK | disarms after B firings and leaves a journal line; no unbounded loop |

---

## 8. The repaired activation design, integrated

This section restates the machines, windows, owners, records and invariants that
change. Everything not listed here stays as the accepted D3-R6 text states it
(§8.8). Rows marked **Δ** differ from the accepted text.

### 8.1 Three coordinated machines

**Machine H, the holder** (steps of [D §4.2.5-R2 (d)], with the §4 … §7 deltas):

| Step | Where | Action | Grant after | On failure |
|---|---|---|---|---|
| AP-0 **Δ** | executor, unprivileged | as accepted, **plus**: PO-20 (f′), PO-21 (c′), (s′) and PO-11 (d′) accepted for the observed versions; the parameter grammar and every inequality of §7.3; the installed `rp11-rootexec` and `rp11_h1.py` digests equal the H-1 record's; `K` absent; the loaded unit's `ExecStartPre` normalized to the `rp11-rootexec consume` form (§9.4); `T_s` finite and ≥ ⌈(P + c)/1,000⌉ + 30 | none | INVALID RUN; nothing mutated |
| AP-1 | executor | create the `ACT` evidence directory (consumes the identifier) | none | INVALID RUN |
| AP-2 **Δ** | executor, privileged | issue the holder literal of §9.4, which starts the holder through `rp11-rootexec` | none | as accepted |
| AM-0 **Δ** | holder | (i) re-check `boot_id`, `/run` and every AP-0 absence condition, **K included**; (ii) create K by exclusive `mkdirat`, open it `O_CLOEXEC`, verify it, take `flock(LOCK_EX\|LOCK_NB)` (LD-1, LD-2); (iii) read the baseline under **BSP** (SD-1); (iv) create the journal and append `run-start {…, lock, capture, helper, params}` (§8.5) | none | exit non-zero; IGR is a no-op; CL |
| AK-1 **Δ** | holder | append `backstop-intent`; issue the backstop literal of §9.4 through `spawn()`; require the timer `active`; append `backstop-armed {timer, period_s, max}`. No activation file exists before this commit | none | exit non-zero; CL |
| AM-1, AM-1R | holder | PT builds tree **P** (and tree **R**) | none | as accepted |
| AM-2 | holder | PF publishes the rule. **The grant is live from PF-6** | **G1** | exit non-zero; IGR; CL |
| AV-1 **Δ** | holder | both files re-verified; H-2b; **PK/2 seek-authorized for verb `start`** (P); **PK/2 first-decisive for verb `stop`** must be `not-authorized` (AR-7) | G1 | IGR; CL |
| AM-3 | holder | PF publishes `⟨activation_id⟩.act.json` (`activated`): **`ACT` PASS** | G1 | as above |
| `hold-start` **Δ** | holder | re-read per SD-1 (`τ = τ₀`, empty `Job`, quiescent); append `hold-start`; `fsync`; **close K** | G1 | OS-7: `hold-end {start-before-hold}`; IGR; CL |
| HL **Δ** | holder | observe every Δ without the lock. On a terminal reason: `LOCK_NB` on K once; re-observe; append `hold-end`; `fsync`; **close K**; exit | G1 → G2 | IGR on every catchable end |
| end **Δ** | holder | **IGR** (§5.7), then exit; then PID 1 runs `ExecStopPost=` CL if it can | G2 | RL ladder |

**Machine C, the capture unit's attempt** (CQ steps of [D §4.2.5-R5 (e)], deltas only):

| Step | Change | Why |
|---|---|---|
| CQ-0 | none | |
| CQ-1 **Δ** | opens **K** (derived from the `activation_id` of CQ-0) `O_CLOEXEC`, one `LOCK_EX\|LOCK_NB`. K absent or unopenable is `consume-unidentified` (nothing created) | LD-1, LD-8 |
| CQ-2, CQ-3 | none. CQ-3's grant-priority form and its removal are unchanged | G1 |
| CQ-4 **Δ** | `τ = τ₀` is justified by SD-1 (no change to the check); K closed on every failure path | §6 |
| CQ-5 **Δ** | PK/2 **seek-not-authorized**, budget P; `unconfirmed` is `consume-failed {CQ-5, removed-unconfirmed}` | §7 |
| CQ-6 | none | |
| CQ-7 **Δ** | `run-end`, `fsync`, **close K**, exit `0` | LD-4 |

**Machine G, the grant object** (§3): `G0 → G1` at AM-2 (the only link, once);
`G1 → G2` at the first `unlinkat` of the rule by IGR, CQ-3 or CL-3; `G2 → G3` at
the first PK/2 *not authorized* observed after that unlink in this activation
(CQ-5, CL-4 or attestation); `G1 → G4` if `unlinkat` fails (GU). `G1`/`G2`/`G4 →
G0` at the next kernel boot. **Cross-machine invariant:** the capture unit's
state does not pass from **A** to **R** (the `ExecStart=` `execve`) unless the
grant state is **G3** for this activation (CQ-3 and CQ-5 order).

**CL deltas** (in [D §4.2.5-R2 (h)] and [D §4.2.5-R3 (e)]):

| Step | Change |
|---|---|
| CL-0 **Δ** | the lock is K, acquired by non-blocking attempts until the `lock_wait_ms` deadline. On expiry or `K` unopenable, **degraded mode** records `lock_mode` and continues. **`lock-timeout` is withdrawn** |
| CL-3 **Δ** | an ACT-journal `igr-removed {path, dev, ino}` for the rule's identity is class `removed-earlier`; an `igr` intent without it is `absent-before-removal`. The rule's removal does not require the lock (GR-1) |
| CL-4 **Δ** | PK/2 seek-not-authorized, budget P |
| CL-5b **Δ** | also removes **K**, through a descriptor re-verification against the journaled identity, only if empty. A K without an identity line is **S0** |
| CL-7 | `st1-verified` additionally requires `lock_mode` to be recorded |
| BS-4 **Δ** | at most `backstop_max` firings run CL; the next firing disarms the timer, appends a journal line and exits non-zero. BS runs CL in degraded mode if K cannot be acquired |

### 8.2 Authority windows

| Window | Opens | Closes | What A-2 permits | Grant | Bound |
|---|---|---|---|---|---|
| **AW-0**, preparation | AP-0 | AP-2 | unprivileged reads; AP-1 | none | none needed |
| **AW-1**, baseline | AM-0 | AK-1's commit | holder only | none | AM-0 steps; BSP ≤ 5 reads |
| **AW-2**, grant window | AM-2's PF-6 | the first unlink of the rule (IGR, CQ-3 or CL-3) | the operator's single `start`, **only after `hold-start`** and while the holder is `active` | **G1**: `start` only, for `ubuntu` | W (start window) and L (lease) |
| **AW-3**, visibility lag | that unlink | the first PK/2 *not authorized* | nothing new. A start in this window reaches CQ-2 and is refused if a claim exists, or runs CP, which re-verifies | **G2**: polkitd may still authorize | `pk_op_ms` P at each use. **No claim about Polkit** |
| **AW-4**, consume | the accepted `start` job | CQ-7 | CP only | G1 → G2 → G3 | the unit's start timeout T_s |
| **AW-5**, pass | `ExecStart=`'s `execve` | the main process's end | route (iii-a) only under OC-1 … OC-3 [D §4.2.5-R6 (b)] | **none** (G3) | no bound is claimed by this design |
| **AW-6**, cleanup | the holder's end (or IGR) | the terminal `deact` record, or `attest` | CL in every trigger; IGR | G2/G3 | RL: IGR now; stop-post ≤ S; backstop ≤ B·(R + S); boot |

### 8.3 Recovery ownership

Who must return each state to ST-1, in order. The first owner is the first rung of RL (§5.3) that can act.

| State | What is undone | First owner | Then | Last |
|---|---|---|---|---|
| ST-1.a0 (K, journal, backstop armed) | K, tree directories, backstop | IGR (nothing to remove) → stop-post CL | backstop | boot, `attest` |
| ST-1.a1 (tree **P**) | `pass-a.json`, tree **P** | stop-post CL | backstop | boot, `attest` |
| ST-1.a2, ST-2 (rule live) | the rule first, then the rest | **IGR** | stop-post CL; backstop; CP at any start | boot |
| **ST-1.i** (new: holder gone, rule live, inert) | the rule | stop-post CL | backstop; CP at any start (CQ-3) | boot |
| ST-2.c, ST-2.f | the rule if CP did not | CP (CQ-3) | CL (HL's reason, rule first) | boot |
| ST-3 | `pass-a.json`, records (**no** grant) | CL after HL observes the pass end | backstop | boot |
| ST-1.d1, ST-1.ur, ST-1.bc, ST-1+R | as accepted | as accepted | as accepted | as accepted |

**ST-1.i** is the only new state: activation objects present, holder not `active`
or `hold-end` journaled, rule live. It is **inert** (IL, §5.4), entered by a
holder's end before CL-3 completes, and left by IGR, CL-3, CQ-3 or the boot.

### 8.4 The states table, deltas

| State | Activation objects present | Grant | Entered by | Left by |
|---|---|---|---|---|
| ST-1.a0 **Δ** | holder `active`, backstop armed, **K**, `ACT` journal; no activation file | none | AK-1 | AM-1, or the holder's end |
| ST-1.a1 … ST-3 | as accepted, with **K** present throughout | as accepted | as accepted | as accepted |
| **ST-1.i** | as ST-1.a2 or ST-2, holder not `active` | G1 **inert** | the holder's end | the rungs of §8.3 |

### 8.5 Evidence records and journals

`rp11-activation-record/2` was never implemented, so its additive amendment
below needs no new schema number.

| Key | Content (amended) |
|---|---|
| `lock` | `{object: {path, dev, ino} or "absent", mode: "held"\|"degraded"\|"absent", wait_ms}` (§4.9) |
| `pk` | `{procedure: "pk-root/2", mode, op_ms, call_ms, calls, elapsed_ms, outcome, reason}`, replacing `grant_check.bound_ms` |
| `release` | `{first_rung: "igr"\|"stop-post"\|"backstop"\|"cp"\|"boot"\|"absent", igr: class or "absent"}` |
| `capture` | `{active_state, invocation_id, inactive_enter_us, m_a_us, bsp_retries}` at AM-0; `{…, inactive_enter_us}` at `hold-start` and at CQ-4 |
| `helper` | `{role, rootexec_sha256, tool_sha256}` |
| `params` | the §7.3 values and `T_s` as recorded in the H-1 `baseline` |
| failure classes **Δ** | add `lock-object`, `capture-baseline-unstable`, `grant-not-seen`, `stop-control-unconfirmed`; **withdraw** `lock-timeout` |

The `ACT` journal's closed `op` set gains `igr` and `igr-removed`. The consume
journal's and each CL journal's `run-start` carry `lock` and `helper`. Journals,
digests and the OH-D-9 return path are unchanged.

### 8.6 Invariants

| ID | Invariant | Where it is checked |
|---|---|---|
| INV-1 | `ExecStart=` runs only after CP exits `0`, which needs CQ-3's journaled removal and CQ-5's *not authorized* within P | NT-PK-2, NT-RL-7 |
| INV-2 | contract OSA over 𝒜 without exception; CX-4 void (§6.8) | NT-SD-3, -9 |
| INV-3 | the rule is linked once, by AM-2, after a BSP baseline | AM-0 and AM-2 order tests |
| INV-4 | no safety property cites the lock | the §2.1 table; NT-LD-6 |
| INV-5 | no lock of the activation chain is on an object a non-root actor can open | NT-LD-4, -5 |
| INV-6 | no process is designed to end holding a lock; every lock has an explicit close point | NT-LD-3, -8 |
| INV-7 | grant removal waits for no lock, no evidence, no PID 1 spawn (IGR) and no Polkit | NT-LD-6, NT-RL-1 |
| INV-8 | every wait, poll and retry has a monotonic deadline and a defined consequence | NT-PK-5, NT-RL-4 |
| INV-9 | a PK `unconfirmed` is never evidence of absence | NT-PK-3, -6 |
| INV-10 | SD compares only with the journaled baseline, and BSP held | NT-SD-1, -2, -10 |
| INV-11 | the first image of every root helper is the static `rp11-rootexec`, so a helper starts with the closed environment and no inherited descriptor | NT-RX-1 … -5 |
| INV-12 | every child of a root helper is created by `spawn()` with the closed map and `close_fds` | NT-LD-3, NT-RX-7 |
| INV-13 | `removed-verified` needs a journaled removal (CQ-3, CL-3 or IGR), `ENOENT` and a *not authorized* from the procedure that returned *authorized* in this activation | NT-PK-6 |
| INV-14 | records state `lock`, `pk`, `release`, `capture` and `helper` | schema tests |
| INV-15 | any drift of a bound version or digest is INVALID RUN before any lock object or grant exists | AP-0 tests, §9.7 |

### 8.7 Where the tests land

The accepted successor table numbers OH-S4's tests up to (29). This proposal adds,
without renumbering any accepted test: **(30)** NT-LD-1 … 9; **(31)** NT-RL-1 … 8;
**(32)** NT-SD-1 … 10; **(33)** NT-PK-1 … 8; **(34)** NT-RX-1 … 9 and NT-HS-1 … 3
(§9.13); **(35)** the PO-17 matcher over both launcher images and the recorded
HF-14 entry. OH-S8b's drills gain only what a real host can safely show: route
(iii-a) is unchanged; `SIGTERM` of a test holder showing IGR before exit;
`SIGKILL` of a test holder showing the live-inert state and its removal by the
stop-post; a test unit with `TasksMax` too small is **not** proposed, because
PID 1 spawn failure is a model-only case (NT-RL-2, NT-RL-3).

### 8.8 What stays exactly as accepted

The unit and rule bytes (apart from the `ExecStartPre=` program, §9.4); SB-1,
SB-2 and SB-3; CQ-0, CQ-2, CQ-3, CQ-6; the claim's publication, blocking and
durability points; the grant-priority form of CQ-3; GP-R3's principle and
ST-1.ur; route (iii-a) and OC-1 … OC-3; OS-1, OS-4, OS-5's decision rule, OS-7,
OS-8; `hold-start`'s durability; A-2's pins other than the additions of
Appendix A; M-B and M-S; the AC-1 … AC-9, AC-12 rows; the attribution classes,
PF, PT, G-R1, RS-1 and RB-1; ST-1+R; DF-1, SL-1, GU; HF-facts other than the
rows named in Appendix A.

---

## 9. Route 3: no ambient input reaches a Python process of the trusted path

### 9.1 Why Route 1 failed, and what Route 3 must achieve

R2 refuted PO-12 and AS-8 for CPython `3.14.4` [R2 §10.4]. Under `-I -S` the
interpreter still reads `PYTHONEXECUTABLE` and `__PYVENV_LAUNCHER__` and acts on
them, including selecting a `._pth` or `pyvenv.cfg` outside the prefix, and the
bundled mimalloc reads `mimalloc_*` and `MIMALLOC_*` in a constructor at process
load, independent of `-I` [R2 §10.2]. R2 also recorded the cross-cutting finding
**X-1** [R2 §15.4]: CP, the holder, its `ExecStopPost=` and the backstop are
`python -I -S` processes that **PID 1 starts with the unit's open block**, not
with a literal environment. Their dynamic loader consumes `LD_*` and the tunables
from that block [R2 §11.3], and CPython consumes the names above. The manager's
global sources are root-controlled or need Polkit authorization, and PO-19 and
PO-12′ as framed cover only the *entry's* literal environment. The entry was
never in the affected set, because the accepted launcher already writes its
environment (`rp11-entry-env/1`, [D2 §5.8]).

Route 3 must make the following true **by construction**, for the entry and for
each of the four root helper roles (`consume`, `hold`, the `ExecStopPost=` role,
`backstop`) and for `attest`:

* **RT-1.** No environment string reaches the interpreter or its loader except a
  reviewed literal. This removes `PYTHONEXECUTABLE`, `__PYVENV_LAUNCHER__`,
  `PYTHON*`, `MIMALLOC_*`, `LD_*`, `GLIBC_TUNABLES`, `MALLOC_*`, locale
  variables and every manager-global input.
* **RT-2.** No descriptor is inherited from PID 1, from `sudo` or from a caller.
* **RT-3.** The first image that runs under the executor is static and reads
  nothing ambient, so no dynamic loader and no interpreter starts under the
  unit's open block.
* **RT-4.** Every child of a root helper starts the same way: closed
  environment, no inherited descriptor (§9.5).
* **RT-5.** It needs no network research and selects no third-party artifact.

**Scoping note.** DR1 §5.3 defined "Route 3" as *abandon the Python-dependent
route*: re-implement the bootstrap, the capture mechanism, CP, the holder, the
backstop and CL without Python, or withdraw the one-host design. The R2
acceptance and this assignment use "Route 3 design" for the **replacement of
Route 1**, defined by the elimination of the ambient inputs above and not by the
removal of Python. This proposal therefore treats DR1's literal Route 3 as an
alternative (RT3-C) and recommends a bounded variant, RT3-A, that keeps Python
where it cannot be avoided: the entry runs the whole capture mechanism, which
cannot be rewritten in a freestanding image. DEC-1 asks Peter to confirm that
scoping.

### 9.2 Options considered

| ID | Route | What it is | Verdict |
|---|---|---|---|
| **RT3-A** | **recommended** | a **static, environment-ignoring first image** `rp11-rootexec` for the root helper roles, built and reviewed by the accepted launcher chain; the entry launcher is retargeted by one literal; system `python3.14` is run only from these images with a closed environment | recommended (§9.3 … §9.12) |
| **RT3-B** | bounded alternative | RT3-A's entry, plus a **Python-free root path**: the procedures that touch the grant (CP, the holder, CL, the backstop, IGR) re-implemented in freestanding C | not recommended (§9.12) |
| RT3-C | DR1's literal Route 3 | no Python anywhere: rewrite the entry's bootstrap and the capture mechanism too | rejected: not decision-ready. The capture mechanism (`capture_contract.py`, `execution/capture_mechanism.py`, `capture_store.py`, the bootstrap) has no non-Python implementation and a rewrite is a new design cycle |
| RT3-D | unit-level scrubbing | `UnsetEnvironment=`, `PassEnvironment=` or `Environment=` on the unit and on `systemd-run` | rejected: closed-world impossible. `UnsetEnvironment=` unsets **named** variables from the assembled block [R2 §3.1 P14-3]; the list of names that can hurt (`PYTHON*`, `mimalloc_*` in both cases, `LD_*`, the tunable aliases) is open-ended; the reviewed unit admits none of these lines (T-B1) |
| RT3-E | dynamic wrapper | `/usr/bin/env -i …` or a shell as the first image | rejected: a dynamic image is loaded by the loader **under the ambient block**, which reads `LD_*` and the tunables before any user code runs [R2 §11.3]. Only a *static* first image closes RT-1 |
| RT3-F | private pinned interpreter | a separately built or separately obtained CPython | not selectable: the repository holds no evidence for its source, build recipe or provenance, and the assignment forbids network research. It would also be a new trust root |
| RT3-Z | accept the residual | no new image: accept X-1 explicitly under OH-D-6 and R-10, and bind PO-12′ and PO-19 for the entry only | not recommended, but offered to Peter (DEC-1) because it needs no code. It leaves every ambient input of §9.1 in place for the four root helper roles and leaves PO-12 refuted for them |

### 9.3 RT3-A in one paragraph

A second image of the class the repository already reviews, `rp11-rootexec`
("RX"), is installed beside `rp11-launch` in tree **L**. It accepts a closed set
of five roles, validates their operands byte for byte, writes a literal
environment, closes every descriptor from 3 up, resets signals, sets
`umask 0077`, `chdir("/")`, and `execve`s `/usr/bin/python3.14 -I -S
…/rp11_h1.py ⟨subcommand⟩ …` (§9.4). Every unit-run root helper (the capture
unit's `ExecStartPre=+`, the holder, its `ExecStopPost=`, the backstop) names RX
as the program PID 1 starts. `attest` is run through RX under `sudo -n`. The
entry keeps `rp11-launch`, with one literal retargeted. H-1, RB-1 and RS-1 keep
the accepted verified-exec stub (HB-1). Everything else about the interpreter,
the tool and the bootstrap is unchanged.

### 9.4 The executable and runtime boundary

#### 9.4.1 Boundary, role by role

| Role | Started by | First image (static) | uid | `NoNewPrivileges` | Interpreter vector | Environment |
|---|---|---|---|---|---|---|
| **entry** | PID 1, capture unit `ExecStart=` | `rp11-launch --pass A` (unchanged contract) | `ubuntu` | `yes` (unit) | `/usr/bin/python3.14 -I -S …/rp11_entry.py run --pass A` | `rp11-entry-env/1` |
| **consume** (CP) | PID 1, capture unit `ExecStartPre=+` | `rp11-rootexec consume` | root | not set (`+`) | `/usr/bin/python3.14 -I -S …/rp11_h1.py consume` | `rp11-helper-env/1` |
| **hold** (holder) | PID 1, the transient holder's main process | `rp11-rootexec hold ⟨id⟩ ⟨a2⟩` | root | not set | `… rp11_h1.py hold ⟨id⟩ ⟨a2⟩` | `rp11-helper-env/1` |
| **stop-post** (`ExecStopPost=`) | PID 1, the holder's `ExecStopPost=` | `rp11-rootexec stop-post ⟨id⟩ ⟨a2⟩` | root | not set | `… rp11_h1.py deact ⟨id⟩ ⟨a2⟩ stop-post` | `rp11-helper-env/1` |
| **backstop** | PID 1, the backstop timer's service | `rp11-rootexec backstop ⟨id⟩ ⟨a2⟩` | root | not set | `… rp11_h1.py backstop ⟨id⟩ ⟨a2⟩` | `rp11-helper-env/1` |
| **attest** | the executor, `sudo -n`, interactive | `rp11-rootexec attest ⟨id⟩ ⟨a2⟩` | root | not set | `… rp11_h1.py deact ⟨id⟩ ⟨a2⟩ attest` | `rp11-helper-env/1a` |
| H-1, RB-1, RS-1 tool | the executor, `sudo -n` | the accepted verified-exec stub under `/usr/bin/python3.14 -I -S -c` | root | not set | the tool's own subcommand | **sudo's environment, unchanged (HB-1)** |
| helper children (`systemctl`, `systemd-run`, `pkcheck`, `sleep`) | `spawn()` of a root helper | none (dynamic distribution binaries) | root, or `ubuntu` for the PK subject | not set | their own | `{LC_ALL=C, PATH=/usr/bin}` only (HS-2) |

`rp11-helper-env/1` is the **same three entries, in the same order and bytes, as
`rp11-entry-env/1`**: `LC_ALL=C`, `PATH=/usr/bin`, `INVOCATION_ID=⟨32⟩`.
`rp11-helper-env/1a` is the first two only (`attest` is not started by PID 1 and
has no unit invocation).

#### 9.4.2 The literals *(design text; none is run by this document)*

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
  --property=Restart=no --property=OOMScoreAdjust=-1000 --property=TimeoutStartSec=⟨S⟩
  /usr/local/libexec/freedom-blades-rp11/rp11-rootexec backstop ⟨activation_id⟩ ⟨a2_sha256⟩
```

```text
sudo -n /usr/local/libexec/freedom-blades-rp11/rp11-rootexec attest ⟨activation_id⟩ ⟨a2_sha256⟩
```

They are the accepted literals of [D §4.2.5-R2 (e), (f), (i)] and
[D §4.2.5-R4 (b)] with the `/usr/bin/python3.12 -I -S …/rp11_h1.py` prefix
replaced by the RX path and role. The grammar rules stand: no `--setenv`, `-E`,
`--scope`, `--user`, `--pty`, `--wait` or `--collect`, and no `%`, `$`, `\` or
quotation mark apart from the shell quotes around the `ExecStopPost=` argument.
The RX path contains **no `.`**, which matters for extension matching (§9.10).

#### 9.4.3 The RX contract *(proposed; D2's class, one new image)*

* **Class.** The same as the accepted launcher [D2 §5.1]: freestanding ISO C11,
  `-ffreestanding -nostdinc`, one assembly `_start` that enters one C function by
  one `jmp`, no runtime, no writable data segment, no `ret`, no `call`, every exit
  `exit_group` followed by `ud2`. It is a **separate image**, built by the same
  build, from sources that share `start.s`, `select.h` and the linker script with
  `rp11-launch` (§9.7).
* **Accepted argv.** `argv[0]` is not examined. `argv[1]` is one of the five role
  names, compared byte for byte. `consume` takes `argc = 2`. `hold`, `stop-post`,
  `backstop` and `attest` take `argc = 4`: `argv[2]` is exactly **34** bytes
  matching `rp11-act-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}` ([D §4.2.5-R1 (a)]) and
  `argv[3]` is exactly **64** bytes of `[0-9a-f]`. Anything else exits `111`
  before any state operation. Operands are copied into fixed stack buffers and
  nowhere else. `rp11_h1.py` re-validates both against the same grammars.
* **`envp`.** For `consume`, `hold`, `stop-post` and `backstop` the one code that
  reads an environment string is the accepted `INVOCATION_ID` selection, with
  the same bounds, the same refusals and exit `112` ([D2 §5.6]). For `attest` no
  environment string is read at all. No other entry is copied, parsed or passed.
* **State operations**, in the accepted order ([D2 §5.7]): argv check `111`;
  `INVOCATION_ID` selection `112` (not for `attest`); `fcntl(F_GETFD)` on 0, 1, 2
  `113`; **`close_range(3, 0xFFFFFFFF, 0)` `114`**; reset every signal's
  disposition except `SIGKILL` and `SIGSTOP`, then clear the mask `115`;
  `umask(0077)`; `chdir("/")` `116`; the `execve` `117`.
* **The `execve`.** Path `/usr/bin/python3.14`. `argv`: `/usr/bin/python3.14`,
  `-I`, `-S`, `/usr/local/libexec/freedom-blades-rp11/rp11_h1.py`, then the
  role's vector of §9.4.1 (`consume`; `hold ⟨id⟩ ⟨a2⟩`; `deact ⟨id⟩ ⟨a2⟩ stop-post`;
  `backstop ⟨id⟩ ⟨a2⟩`; `deact ⟨id⟩ ⟨a2⟩ attest`). `envp`: the literal of §9.4.1.
  Every byte except the operands and the 32 selected digits is a compiled
  literal.
* **System calls**: exactly the accepted launcher's inventory (`fcntl`,
  `close_range`, `rt_sigaction`, `rt_sigprocmask`, `umask`, `chdir`, `execve`,
  `write`, `exit_group`). If OH-S4p needs any other, [D2]'s restated AD-8 must be
  re-restated for it (§9.8).
* **Not touched**, and so unchanged from the unit configuration: resource limits,
  `no_new_privs`, capabilities, securebits, seccomp, namespaces, cgroup,
  scheduling, `oom_score_adj` and timers (R-10, K-5). The image neither resets nor
  reports them, and no record claims otherwise. In particular **RX claims nothing
  about `NoNewPrivileges`** for the root roles.
* **Exit statuses.** `111` usage, `112` invocation id, `113` stdio, `114`
  descriptors, `115` signals, `116` chdir, `117` exec failed. Each writes one
  fixed diagnostic line `rp11-rootexec/1: ⟨code⟩` to descriptor 2. No new status
  is introduced.
* **What this closes.** The interpreter and the loader start under a closed
  environment and a closed descriptor table. The manager's block, `sudo`'s block
  and the caller's block never reach them.

#### 9.4.4 HB-1, the residual that Route 3 does not close

H-1, RB-1 and RS-1 run `sudo -n /usr/bin/python3.14 -I -S -c ⟨verified-exec
stub⟩` **under `sudo`'s environment**, as [D §4.2.4] states (AS-12). It cannot be
closed by RX, because RX does not exist on the host until H-1 installs it, and
the later subcommands are too open to fit RX's closed grammar. The accepted
reasoning stands and is narrowed here: those runs are not part of the grant window,
the pass or the consume step; they run in ST-0 … ST-1 or under a separately
authorized RB-1; their results are re-read unprivileged by H-2; and OH-D-6 already
gives `ubuntu` unrestricted `sudo`, so this is a consistency limit and not a
prevention claim. **HB-1** is the name under which the review accepts or rejects
that residual (§14, question 5).

### 9.5 Environment contracts and spawn discipline *(proposed)*

* **HS-1.** Every child of a root helper is created by **one** function,
  `spawn()`, in one module. No other process-creation call appears in any root
  helper (a scan test, NT-HS-1).
* **HS-2.** `spawn()` passes **only** the closed map `{LC_ALL=C, PATH=/usr/bin}`
  (the accepted `rp11-launcher-env/1` shape), never `None`, never a copy of the
  helper's own environment, and the program's absolute path under `/usr/bin`.
* **HS-3.** `close_fds=True`, `pass_fds=()`, a stated working directory `/`, no
  `preexec_fn`, and for the PK subject the credential change by the primitive's
  own arguments (user, group, supplementary groups) rather than by code between
  `fork` and `exec`.
* **HS-4.** No shell, no `os.system`, no `os.exec*p`, no `shell=True`.
* **HS-5.** Every spawn has a monotonic deadline and is killed and reaped at it.
* **HS-6.** `rp11_h1.py` reads the environment only for the diagnostic
  `INVOCATION_ID` and decides nothing from any other variable.

HS-1 … HS-6 are properties of the code, tested (NT-HS-1 … 3) and reviewed in
OH-S4. They are what makes RT-4 true, and they are what LD-3 (§4.5) relies on.

### 9.6 Inventory of every Role A–H occurrence, and its Route 3 disposition

Line references are the **current** lines of the cited files as found with fixed
searches of those named files in this assignment (the R3 inventory's numbers
agree). "R1" is Route 1's replacement under accepted R3 §6.2. "RT3-A" is this
proposal's disposition. Source-bearing rows are applied only by OH-S4p or OH-S4,
text rows by the documentation slices OH-S0d or OH-S3S (§11), and none is applied
here.

**Role A, executed literals.**

| # | Location | Text | Route 1 (R3 §6.2) | **RT3-A** | Applied by |
|---|---|---|---|---|---|
| A1 | `infra/rp11-launch/launch.c:207`, `:221` | `argv_out[0]` and the `execve` path `/usr/bin/python3.12` | `/usr/bin/python3.14`, then rebuild | **retained**: the only source delta of the entry image | OH-S4p |
| A2 | `rp11-launch.x86_64.listing:412–413` | `.rodata` bytes `/usr/bin/python3` `.12` at `0x40067f` | regenerated by the rebuild | retained; regenerated, never hand-edited | OH-S4p |
| A3 | image `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572` and every pin of it (`rp11_launch.py`, `expected.sha256`, `tools/r5_runner/blocks/s08.sh`, design §4.2.4 P-0 and §4.5.2, IA-8) | the compiled literal | superseded by a new reviewed digest | retained, **plus** the RX image's four digests | OH-S4p |
| A4 | `tools/phase_5_0_evidence/rp11_launch.py:47`, `:49` | `EXECVE_PATH`, `EXECVE_ARGV[0]` | `/usr/bin/python3.14` | retained; **plus** a contract for RX with its five vectors | OH-S4p |
| A5 | `docs/review/phase-5-0-evidence-harness-review-manifest.json:2732`, `:2744`, `:2824`, `:2841` | `rp11_launch` `execve_argv`, `execve_path`, `execve.argv`, `execve.path` | `/usr/bin/python3.14`, in a new manifest version | retained; **plus** a new `rp11_rootexec` contract in the same new version | OH-S4p |
| A6 | design `:2857` (also `:228`, `:2481`, `:2509`, `:5242`, `:6979`) | `ExecStartPre=+/usr/bin/python3.12 -I -S …/rp11_h1.py consume` | `ExecStartPre=+/usr/bin/python3.14 -I -S …/rp11_h1.py consume` | **changed**: `ExecStartPre=+/usr/local/libexec/freedom-blades-rp11/rp11-rootexec consume`. T-B1 admits exactly this line | OH-S0d (design text), OH-S4 (tests) |
| A7 | design `:1257` | `sudo -n /usr/bin/python3.12 -I -S -c '⟨verified-exec stub⟩' …` | `/usr/bin/python3.14` | `/usr/bin/python3.14`, under **HB-1** | OH-S0d, OH-S4 |
| A8 | design `:1996`, `:1997`, `:2016`, `:2147` | the holder's `ExecStopPost=`, the holder command, the backstop command and the attest command | each `python3.12` → `python3.14` | **replaced** by the RX literals of §9.4.2 | OH-S0d, OH-S4 |
| A9 | design `:3124` | the `ExecStartPre` normalization (`path`, `argv[0]`) | `/usr/bin/python3.14` | path `…/rp11-rootexec`, `argv` `[…/rp11-rootexec, "consume"]`, `+` flag | OH-S0d, OH-S4 |
| A10 | C11 `:688`, `:903–904`; D2 `:436`, `:1256`, `:1258`, `:1567–1568` | the entry's `execve` contract | a dated amendment note naming `/usr/bin/python3.14` | the same note for the entry; **plus** a dated D2 addendum for the second image | OH-S0d |

**Role B, trust-path and proof-obligation statements.**

| # | Location | Route 1 | **RT3-A** |
|---|---|---|---|
| B1 | design TR-9 `:945` | `/usr/bin/python3.14 -I -S`; PO-12 and PO-19 re-cited | `/usr/bin/python3.14 -I -S` for the entry; **new row TR-6a′** for the root roles (RX first, then the interpreter); PO-12′ and PO-19 narrowed (§9.9) |
| B2 | design PO-19 (a) `:4497` | `/usr/bin/python3.14`; re-cited | restated, narrowed to the file inputs of one executable and its closure |
| B3 | C11 PO-12 and AS-8 (`:456`) | re-cited for 3.14 | **refuted** [R2 §10.4]; replaced by PO-12′, narrowed (§9.9) |
| B4 | C11 M-5; design M-5 `:5154` | the entry interpreter `/usr/bin/python3.14` | entry interpreter `/usr/bin/python3.14`; **plus** the two installed static images as root-owned `0755` regular files pinned by digest |
| B5 | C11 descriptive text (`:62`, `:281`, `:514`, `:576`, `:598`, `:619`, `:809`, `:941`, `:1748`) | a dated C11 amendment note | the same note, **plus** the statement that the root roles start through RX. The withdrawn LB-2 and LB-3 rows and change records (`:226`, `:798`, `:1019`, `:2529`, `:2533`) stay as history, unchanged |
| B6 | U-9 decision | Peter's restatement for `/usr/bin/python3.14` | **unchanged**. Narrowing the consumers is done by the obligation text, not by a new decision (DEC-1 covers it) |

**Role C, H-0 facts and command classes.**

| # | Location | RT3-A |
|---|---|---|
| C1 | HF-06, HF-07, HF-08, HF-10 (`:4436–4440`), C-VER (`:4472`) | **unchanged by Route 3**: the `python3.14` rows are already observed by H-0G in the accepted composed H-0 |
| C2 | HF-10, HF-11 | **add rows** for `/usr/local/libexec/freedom-blades-rp11/rp11-rootexec` (absent at H-0; present at P-0 and H-2) and `/run/freedom-blades-rp11-lock-*` (absent) |

**Role D, standard-library capability claims.**

| # | Location | RT3-A |
|---|---|---|
| D1 | PT-8: `renameat2` through `ctypes` | **unchanged**: `os.renameat2` and `os.RENAME_NOREPLACE` do not exist in 3.14.4 [R2 §10.5]; `ctypes` stays. Its `_ctypes` closure (`libffi`) is an MF-1 consumer: the H-1 tool and the holder's tree builds |
| D2 | the bootstrap, the capture mechanism and `rp11_h1.py` under TR-9's interpreter | **unchanged**: OH-S4 tests run under CPython 3.14 as well as the suite interpreter, or the gap is stated |

**Role E, verification artifacts.** `tests/test_rp11_launch_source.py` and
`infra/rp11-launch/verify/ctverify.py` read their constants from the manifest
contract. They need **no literal edit** and need **extension** for the second
image (OH-S4p). D2's test methods (`:1525`, `:2207`) and the I-7 handback's
decoded `execve` record are evidence for the **old** image. They remain history
and are superseded by re-run evidence for each new image.

**Role F, development and test runtimes** (`venv-web` CPython 3.12.14, the
controller's 3.12.3 records, the production deployment Python, the harness and
laboratory fixtures): **unaffected under every route.** They are not the trusted
path.

**Role G, current-state records.** `docs/implementation-plan.md` §20,
`docs/project-management/status.md`, `docs/review/Handover information` and the
test-server banner: **pointers only**. This assignment updates them, and only
them.

**Role H, historical or consumed evidence:** the R3 … R5 prompts, authorities,
handbacks and reviews, the design's revision history, the preparation handback,
the 2026-09-29 C11 review and the `*-through-*` snapshots: **never edited.**

### 9.7 Reproducible source, build, pinning, digest, ownership, installation, update, rollback and drift *(none performed)*

* **Source (proposed layout; OH-S4p may refine it).** `infra/rp11-launch/` gains
  `rootexec.c`. It shares `start.s`, `select.h`, `rp11-launch.ld`, `build.sh`,
  `toolchain.lock` and `build-root.manifest` with the entry image. **The entry
  image's compiler flags and every other source byte are unchanged**, apart from
  A1. The sources' SHA-256 values are recorded before and after.
* **Build.** The accepted chain, unchanged in method: `provision.py` and
  `enter.py build` over the pinned Ubuntu snapshot archive
  (`archive_snapshot=20261001T000000Z`, every package SHA-256 in
  `toolchain.lock`), `build.sh` as the first process in the verified build root,
  the same-invocation R-1 tree-manifest gate, IC-1, and R-2 as the unprivileged
  build user. It produces two images.
* **Pinning.** `expected.sha256` gains rows for the RX image, listing, map and
  assembly (four), beside the entry's four. The manifest takes one new version
  with both contracts. A-2 pins `rootexec_sha256` and `launcher_sha256`.
* **Independent bindings** for each image, as [D §4.5.2]: `expected.sha256`, the
  manifest contract, an accepted independent-rebuild record (D9-3), and Codex's
  independent decoding (XD-11).
* **Ownership.** `/usr/local/libexec/freedom-blades-rp11/rp11-rootexec` is a
  regular file, `root:root`, `0755`, with no set-user-ID, set-group-ID or sticky
  bit, no `security.capability` and no `system.posix_acl_*` attribute, a member
  of tree **L** (§4.2.3). Its parents are the accepted tree **L** parents.
* **Installation.** By H-1 only (PT, PF, M-1), from the OH-S5 rebuild's bytes read
  **once**, hashed in memory and written from those bytes ([D §4.2.4]). The H-1
  record's `baseline.files` gains the image (SHA-256, size, owner, mode,
  `(dev, ino)`), compared by H-2.
* **Update.** **Never in place.** A new image is a new OH-S4p cycle (D9-1 … D9-4),
  a new OH-S5, then RB-1 and a new H-1, because H-1 requires its paths absent at
  P-0. A distribution update of `python3.14-minimal`, `libc6`, the kernel,
  `systemd` or `polkitd` is not an update of RX: it is drift (below).
* **Rollback.** RB-1, separately authorized and never automatic, removes tree
  **L**'s members, including RX. No procedure removes it during an activation.
* **Drift, checked before any lock object or grant exists.** The kernel,
  `systemd`, `polkitd`, `libc6`, `python3.14-minimal` and `/usr/bin/python3.14`'s
  SHA-256 of [R2 §16]; the **RX digest**, the entry launcher's digest and
  `rp11_h1.py`'s digest, each against the H-1 record; the nine Polkit rule
  digests of [R2 §16]; the HF-14 entries; and the unit's loaded configuration.
  P-0, H-2, AP-0 and AM-0 each compare. Any difference is INVALID RUN followed by
  re-citation, **never accepted at run time**. `unattended-upgrades` is active
  (HF-17), so drift is expected unless separately controlled, and a package hold
  is not authorized (R3 §6.7).

### 9.8 What is preserved, and every claim that needs re-review

**Preserved:** the C11 launcher contract for the entry; D9's objectives (the
path from the kernel to the first reviewed instruction contains no user-space
code; no environment string is read except the selection; the image contains
nothing outside its control-flow graph); I-7's evidence methods (T-L7, T-L10,
T-L11, XD, R-1 … R-5); LB-2S's two prevention claims about the entry; PO-14 and
AD-7 (established) and so TR-7; the entry's environment literal; the start-only
rule, CP, A-2 and every safety invariant of §2.

**Needs re-review** (each stays unaccepted until its gate):

| # | Claim | Why | Gate |
|---|---|---|---|
| RR-1 | **X-1 is closed**: a root helper starts under a closed environment and descriptor table | new construction (RX) | OH-S4p, D9-2 |
| RR-2 | PO-9 for the RX image (**PO-9R**): P-1 … P-7 restated for the five roles | a new image | OH-S4p |
| RR-3 | D9-1 for RX: AD-3, AD-4, AD-6, AD-11, AD-12 (established for the kernel), and **AD-8 as restated over the closed inventory**, which holds only if RX's system-call set equals the launcher's | the inventory is a property of the image | OH-S4p |
| RR-4 | D9-2 BI-1 … BI-11 and independent decoding (XD, T-L11, XD-11) for **both** images; the decoder corpus may need extending | two images changed or new | OH-S4p |
| RR-5 | D9-3 independent rebuild, with a recorded variation of at least one of HA-1 … HA-3, for both images | new bytes | an R-5-class slice (§11) |
| RR-6 | D9-4 and PO-17 for both images | installed bytes and live `binfmt_misc` entries | P-0, V-1, H-2 (§9.10) |
| RR-7 | operand grammar (34 and 64 bytes), five-role dispatch, `attest`'s no-`INVOCATION_ID` variant | new image behaviour | OH-S4p |
| RR-8 | `umask 0077` and `chdir("/")` for the root roles; no helper relies on an inherited `umask` (every created object's mode is set by `fchmod`, AR-5) | the roles previously inherited unit or `systemd-run` defaults | OH-S4 tests |
| RR-9 | HS-1 … HS-6 | new code properties | OH-S4 |
| RR-10 | HB-1 | residual restated | Codex, Peter |
| RR-11 | the PO-12′ and PO-19 narrowing (§9.9) | scope change | OH-S2b, then MF bindings |

### 9.9 PO-12′ and PO-19: still necessary, and narrowed to what is left

| Obligation | Consumers under Route 1 | Consumers under RT3-A | What the construction now discharges | What remains, and its fact |
|---|---|---|---|---|
| **PO-12′** (CPython `-I -S` start-up) | the entry | the entry **and** the four root roles **and** `attest`: every process whose `execve` target is `/usr/bin/python3.14` | the **environment precondition**: none of `PYTHONEXECUTABLE`, `__PYVENV_LAUNCHER__`, `PYTHON*` or `mimalloc_*`/`MIMALLOC_*` is in any of the six literal environments. This is a **byte-level property of two static images** (D9-2, NT-RX-2), not a CPython citation | the **file** inputs: absence or root ownership of `/usr/bin/python3.14._pth`, `/usr/pyvenv.cfg`, `/usr/bin/pyvenv.cfg`, `/usr/bin/pybuilddir.txt`, `/usr/bin/Modules/Setup.local`, and ownership of `/usr/lib/python3.14`: **MF-4** |
| **PO-19** (glibc loader inputs) | the entry's literal environment only | the same six processes | (b) `INVOCATION_ID`, `LC_ALL`, `PATH` are not loader or tunable inputs: **established** [R2 §11.3]. The environment-sourced loader inputs (`LD_PRELOAD`, `LD_LIBRARY_PATH`, `GLIBC_TUNABLES`, `MALLOC_*`) are **absent by construction**, which removes them from (a) | (a′) the **file** inputs of one executable and its closure: `/etc/ld.so.preload`, `/etc/ld.so.cache`, `DT_RUNPATH`/`DT_RPATH`/`DT_NEEDED`/`DT_FLAGS_1`/`PT_INTERP` of `/usr/bin/python3.14` and each loaded object, the built-in trusted directories and their `glibc-hwcaps` subdirectories: **MF-1**; (d) root ownership of those: **MF-2**. (c) is established |
| helper children | not covered | **out of PO-19's scope** | they run as root, from root-owned distribution files, under the closed map of HS-2 | their file-level loader inputs are root-owned system state (R-8). Whether the review wants them observed is **question 7** (§14); it would be a new fact, MF-9 |

The binding tuple of [R2 §11.6] is unchanged and gains one row: the **RX digest**.
`python3.14-minimal` `3.14.4-1ubuntu0.2`, `libc6` `2.43-2ubuntu2.4` and
`/usr/bin/python3.14`'s SHA-256 `be9a2a5e…69fd` stay the bound values. The
dynamic-section row stays **unestablished** until MF-1 is observed. PO-19 remains
**not established** and PO-12′ remains source-established with its binding
needing MF-4. **Route 3 does not close either, and it does not need to**: it
removes the part that R2 refuted (the ambient environment) and leaves the part
that was never refuted and never observed (the files).

### 9.10 PO-17 and the OH-S4p byte-level boundary

[R2 §12.9] established PO-17's premises and left it **not evaluated against any
launcher image**. For RT3-A there are two images, the retargeted `rp11-launch`
and the new `rp11-rootexec`. **OH-S4p** (repository only) must supply, for each:

1. **The bytes.** The file's complete bytes (as a digest and a size) and its
   **first 256 bytes** (`BINPRM_BUF_SIZE`, [R2 §12.9 (3)]), recorded as an
   independent digest and as hex in the review record.
2. **The installed path string**, exactly as it will be passed to `execve`
   (`bprm->interp`), and the statement that **it contains no `.`** over the whole
   path. Extension entries compare the text after the last `.` in the *full path*,
   not the basename [R2 §12.9 (4)]. Both proposed paths
   (`/usr/local/libexec/freedom-blades-rp11/rp11-launch` and `…/rp11-rootexec`)
   contain none. `rp11_h1.py` and `rp11_entry.py` are arguments, not `execve`
   targets, and are not subject to this rule.
3. **The mechanical evaluation** of every recorded `binfmt_misc` entry against the
   image under premises 2 … 4 of [R2 §12.9] and the algorithm of [D §4.3.6]: the
   global gate, the per-entry enable bit, the magic comparison (`offset`, `size`,
   optional `mask`, over the 256 bytes) and the extension comparison on the full
   path. The accepted H-0 recorded one entry,
   `python3.14` (`offset 0`, magic `2b0e0d0a`, no mask, interpreter
   `/usr/bin/python3.14`, flags empty). An ELF image begins `7f454c46`, so a
   *preliminary* result can be computed from bytes alone. It is a **preliminary,
   record-bound evaluation**. PO-17 is **not discharged** by it.
4. **The live evaluation** at H-1's P-0, at V-1 and at H-2, against the entries
   re-observed on the host (HF-14), with any new, changed or enabled entry an
   INVALID RUN.
5. **The static-image facts** the D9-2 evidence already requires: `ET_EXEC`, no
   `PT_INTERP`, no dynamic section, no relocation or TLS, a closed list of `.rodata`
   strings (for RX: the five role names, the interpreter and tool paths, the
   environment literals, the diagnostics), no `ret`, no `call`, the closed
   system-call set of §9.4.3.
6. **The delta of the entry image**: A1 and nothing else. Every other source
   file hashes equal to its accepted value, and the compile line is
   byte-identical.
7. **The pins**: the new digests in `expected.sha256` and the manifest, the A-2
   and H-1 fields they feed, and the independent bindings of §9.7.

OH-S4p **does not**: contact a host, install anything, edit the operational draft
or run any activation step.

### 9.11 Failure and recovery for missing, altered, wrongly owned or incompatible artifacts

| Artifact | Condition | Detected by | Behavior | Recovery owner |
|---|---|---|---|---|
| `rp11-rootexec` | **missing** | H-1's own post-install verification, H-2, AP-0 | INVALID RUN; no lock object, no grant. After `ACT`: the holder never starts, so no grant was linked (§5.5 row 12); an `ExecStopPost=` or backstop that cannot execute it is RO-2 | RB-1 then H-1, separately authorized. **No in-place repair** |
| | **altered** (digest) | H-2, AP-0, AM-0 | INVALID RUN or HARD STOP before AM-1 | as above |
| | **wrong owner, mode or extended attribute** | H-2, AP-0 (`lstat`, `listxattr` names) | INVALID RUN | as above |
| | **incompatible**: the kernel cannot run it, an enabled `binfmt_misc` entry matches it, or a system call it needs is refused | P-0 and H-2 (PO-17 live evaluation, D9-4); the first start of a **test** unit under OH-S8b | INVALID RUN; if met at run time, exit `117` or a kernel refusal ends the start, and `ExecStart=` is never executed | design review |
| `rp11-launch` (entry) | missing, altered, wrongly owned, incompatible | as RX | as RX; at run time the unit fails and no pass runs (PO-21 (o) governs `ExecStart=` itself) | as RX |
| `rp11_h1.py` | missing, altered | H-2, AP-0, AM-0 (digest pinned by A-2) | as RX; at run time CP's helper does not run, so no pass | as RX |
| `python3.14` and its closure | version or digest drift | P-0, H-2, AP-0 (the §9.7 drift list) | INVALID RUN, then re-citation | OH-S2b |
| the unit | altered after H-1 | H-2, AP-0 (`baseline_sha256`) | INVALID RUN | RB-1 / H-1 |

### 9.12 Comparison with the bounded alternative, and the surface argument

**RT3-B** keeps RT3-A's entry and replaces the Python root path with freestanding
C: CP (CQ-0 … CQ-7), the holder (AM-0 … HL), CL and GP-R3, the backstop, IGR, the
journal (canonical JSON and a hash chain), protocols PF and PT, G-R1's descriptor
re-verification **with a full re-hash**, PK's orchestration and `systemctl show`
parsing. The accepted design names every one of those procedures. The repository
holds no measure of their size and this proposal estimates none.

| Criterion | **RT3-A** (recommended) | RT3-B |
|---|---|---|
| New trusted code | one image of the class the repository already reviews. The accepted entry launcher's sources are 445 lines (`launch.c` 224, `start.s` 23, `select.h` 75, `rp11-launch.ld` 58, `build.sh` 65), and RX adds a role table and two fixed-length operand checks to that pattern | a freestanding re-implementation of the procedures above. No accepted proof method (D9-class) exists for code of that size |
| Ambient inputs to the root path | removed (RT-1 … RT-4) | removed |
| Interpreter and loader in the root path | **still present**: file inputs only (MF-1, MF-2, MF-4) | **absent for the helper's own logic**. But `systemctl`, `systemd-run`, `pkcheck` and `sleep` are **still dynamic children** (their file-level loader inputs remain, MF-9), so RT3-B does not remove the dynamic loader from the root path |
| Drift exposure | `python3.14` and `libc6` updates trigger re-citation (HF-17) | the root path is immune to interpreter drift; the entry is not |
| Review | one new static image plus a literal retarget, through the accepted chain | everything in RT3-A, **plus** a security review and a new proof method for the C helper |
| Failure containment | every failure fails closed to "no pass" | the same, with more code that can fail |
| Reversibility | RB-1 removes the image | the same |
| Re-opening trigger | if interpreter drift makes INVALID RUN routine, RT3-B can be revisited as a successor; RX's build and proof chain would be reused for the C helper | n/a |

**Why RT3-A has the smaller trusted and runtime surface.** It adds one small
static image of an already-reviewed class and removes **all ambient input** from
the root path. It does not shrink the *runtime* (CPython and glibc stay in the
path, bounded by MF-1, MF-2 and MF-4 and by the drift gates), but it also does not
grow the *trusted code* by a freestanding reimplementation, and RT3-B does not
remove the dynamic children anyway. RT3-D and RT3-E fail on the loader's
ordering. RT3-C is a new design cycle. RT3-F has no evidence.

### 9.13 Negative tests for Route 3 *(proposed, for OH-S4 and OH-S4p)*

| ID | Case | Asserts |
|---|---|---|
| NT-RX-1 | every role with a wrong `argc`, an operand of the wrong length or class, an extra argument, an unknown role, an `argv[0]` of any value | exit `111` before any state operation; nothing executed |
| NT-RX-2 | an environment block containing each of `PYTHONEXECUTABLE`, `__PYVENV_LAUNCHER__`, `PYTHONPATH`, `PYTHONHOME`, `PYTHONSAFEPATH`, `mimalloc_*` and `MIMALLOC_*`, `LD_PRELOAD`, `LD_LIBRARY_PATH`, `LD_AUDIT`, `GLIBC_TUNABLES`, `MALLOC_CHECK_`, `MALLOC_ARENA_MAX`, `LOCPATH`, `GCONV_PATH`, `LANG`, `LC_*`, `TZ`, `HOME`, a hostile `PATH`, and duplicate or malformed `INVOCATION_ID` | the observed `execve` environment is **exactly** the literal (the strace-class method of [D2 §5.12], Method A); malformed or duplicate `INVOCATION_ID` exits `112` for the four unit roles; `attest` ignores the block |
| NT-RX-3 | descriptors | every inherited descriptor ≥ 3 is closed before `execve`; a closed descriptor 0, 1 or 2 exits `113` |
| NT-RX-4 | signals, mask, `umask`, working directory | as the accepted launcher's tests, applied to RX |
| NT-RX-5 | the image | `ET_EXEC`, no `PT_INTERP`, no dynamic section, closed `.rodata`, no `ret`, no `call`, closed system-call set |
| NT-RX-6 | PO-17 matcher | over both images, the recorded HF-14 entry and generated entries (magic at offset 0 and elsewhere, masks, extension entries) |
| NT-RX-7 | AST scan of `rp11_h1.py` | no `os.environ` pass-through; no process-creation call outside `spawn()` |
| NT-RX-8 | unit text T-B1 and the baseline normalization | exactly the RX line; an altered image or a changed normalization is detected by the H-2 code |
| NT-RX-9 | OH-S4 | the helper tests run under CPython 3.14 as well as the suite interpreter, or the gap is stated |
| NT-HS-1 | `spawn()` | rejects `env=None`, `shell=True`, a relative `argv[0]`, `preexec_fn`, a missing deadline |
| NT-HS-2 | a child of `spawn()` | inherits no descriptor and carries exactly the closed map |
| NT-HS-3 | deadlines | a child that outlives its deadline is killed and reaped, and the helper continues fail-closed |

---

## 10. MF-1 … MF-8: disposition under Route 3 *(nothing is collected here)*

The identifiers and facts are those of [R2 §14.3]. Two read-only observing slices
are **proposed** (names are proposal-local, neither is authorized): **H-0M1**,
unprivileged, and **H-0M2**, privileged and read-only. Each needs its own authority,
work ID, exact commands and evidence path, on `oracle-test` only. Both obey the
accepted H-0 prohibitions (no `env`, `printenv`, `/proc/*/environ`, no secret, no
`ldd`, no `LD_TRACE_LOADED_OBJECTS`, no listing of retained paths). ELF
parsing, if needed, reads file bytes and executes nothing from the closure.

**Route 3 effect:** eliminates none of the eight, **narrows MF-1 and MF-2**, **moves
MF-4** to a wider consumer set, and leaves **MF-3, MF-5, MF-6, MF-7 and MF-8
unchanged**.

| MF | Fact (R2 §14.3) | Route 3 effect | Minimum observing slice and privilege | Exact-path scope | Evidence and drift trigger | Dependent gate |
|---|---|---|---|---|---|---|
| **MF-1** | `/usr/bin/python3.14` `DT_RUNPATH`, `DT_RPATH`, `DT_NEEDED`, `DT_FLAGS_1`, `PT_INTERP`, and the same for each object in its closure, including every `lib-dynload` extension the entry, CP and the H-1 tool import (for example `_ctypes` → `libffi`) | **narrowed.** The environment-sourced part of the loader's inputs is gone (§9.9). Consumers: the six Python processes of §9.4.1, one executable and one closure. The closure now also covers what the holder, CP, the backstop and `attest` import | **H-0M1**, no privilege. **After OH-S4** fixes the import closure, so the extension-module list is known | `/usr/bin/python3.14`; each `/usr/lib/python3.14/lib-dynload/*.so` that OH-S4's import record names; each library the recorded `DT_NEEDED` names resolve to, through `/etc/ld.so.cache` and the built-in directories, by reading bytes only | the parsed dynamic entries and a SHA-256 for each file, as admitted capture records. **Drift:** any change of `python3.14-minimal`, `libc6`, any digest in the closure, or the import closure | PO-19 (a′) binding (OH-S2c); H-1 readiness |
| **MF-2** | type, owner, mode of `/lib`, `/lib/x86_64-linux-gnu`, `/usr/lib`, `/usr/lib/x86_64-linux-gnu`, their `glibc-hwcaps/x86-64-v{2,3,4}`, and each library MF-1 resolves to | **narrowed** to the closure of one executable. Helper children are out of scope (§9.9) | **H-0M1**, no privilege | exactly those paths, `lstat` of each and its parents, extended-attribute **names** only | type, owner, group, mode, `(dev, ino)`, attribute names. **Drift:** any ownership or mode change, a changed `ld.so` configuration, a `libc6` change | PO-19 (d) |
| **MF-3** | privileged read-only inventory of `/etc/polkit-1/rules.d` (names, types, owners, modes, SHA-256) | **unchanged.** Independent of Route 3: it settles PO-11 (b) and (g) | **H-0M2**, root, read-only, one reviewed fixed literal. **Recommended before H-1** (DEC-5) | exactly `/etc/polkit-1/rules.d` and each regular file in it, by digest only | names, types, owners, modes, SHA-256. **Drift:** any added, removed or changed file; re-observed at H-1's P-0p. A later PK result corroborates and never replaces it | PO-11 (b), (g); H-1 readiness |
| **MF-4** | absence or root ownership of `/usr/bin/python3.14._pth`, `/usr/pyvenv.cfg`, `/usr/bin/pyvenv.cfg`, `/usr/bin/pybuilddir.txt`, `/usr/bin/Modules/Setup.local`; ownership of `/usr/lib/python3.14` | **fact unchanged; its consumer set moves** from "the entry" to "the entry, the four root roles and `attest`". It is now the **sole remaining residual of PO-12′** | **H-0M1**, no privilege | exactly the five paths and `/usr/lib/python3.14` | `lstat` results (`ENOENT` or type, owner, mode). **Drift:** appearance of any of the five, or an ownership change | PO-12′ binding; H-1 readiness |
| **MF-5** | whether the ext4 filesystem on `/dev/sda1` has a journal (`has_journal`) and its data mode | **unchanged.** It bounds PO-20 (a)'s crash limb and (d) for every durable write of the design | **H-0M1** if an unprivileged read exists, otherwise **H-0M2** read-only. **The slice must name the exact read-only path or literal.** This proposal asserts no availability. Candidates, not facts: the filesystem's feature flags (privileged) or a kernel-exposed journal entry for the device | the one device already recorded by HF-15 | has-journal yes/no and the data mode. **Drift:** a different filesystem, a changed mount option (HF-15 is re-observed at P-0 and AP-0 anyway) | PO-20 (a), (d); H-1 readiness |
| **MF-6** | run-time `fs.protected_hardlinks` and `fs.protected_symlinks` | **unchanged**; needed only for a non-owner publisher, and every publisher in the design is root | **H-0M1**, no privilege | the two named kernel parameters | the two values. **Drift:** a sysctl change | PO-20 (a) |
| **MF-7** | `/run/nextroot` absent | **unchanged.** AP-0 and AM-0 already observe it (R3 §7.2). **No separate slice is needed**; H-0M1 may record it early | AP-0, AM-0 (as designed); optionally H-0M1 | `/run/nextroot` | `lstat` → `ENOENT`. **Drift:** any creation of the path | CL-21i acceptance; before any A-2 |
| **MF-8** | the dash-prefix drop-in directories (`rp11-.service.d`, `rp11-capture-.service.d`, `rp11-capture-pass-.service.d`) in all 12 unit paths | **unchanged**; covered mechanically at H-1 by `DropInPaths` empty | **H-0M1** (early knowledge) and H-1 (the mechanical check) | the 36 paths (3 names under each of the 12 unit paths of HF-13) | `lstat` each. **Drift:** existence of any | HF-13 completeness; H-1 P-0 |

**What Route 3 adds, and does not add.** Route 3 adds **no required fact**. It adds
**one optional fact, MF-9**, only if the review decides that helper children's
loader inputs should be observed (§9.9, question 7): the dynamic sections of
`/usr/bin/systemctl`, `/usr/bin/systemd-run`, `/usr/bin/pkcheck` and
`/usr/bin/sleep`. It is not proposed as required, because those children run as
root, from root-owned distribution files, under the closed map.

---

## 11. Successor order and review gates *(no successor is authorized by naming it)*

Every row needs its own prompt, authority record, work ID and Codex review. The
order is a dependency order. Rows with the same number may run in parallel. None
of them is requested here.

| Order | Slice (proposal-local name) | Scope | Host | Gate before it | Closes |
|---|---|---|---|---|---|
| **G-0** | independent Codex review of this proposal and handback | review | none | — | the findings of this return |
| **G-1** | **Peter's recorded decisions** DEC-1 … DEC-6 (§12), and acceptance of the repaired design and Route 3 as the **inactive** basis | decision | none | G-0 | the accepted-decision changes (D-3, CX-4) |
| **2a** | **OH-S2b**: citation addendum for the new and restated obligations (§13.2) | documentation, U-10 | none | G-1 | PO-20 (f′-2 … 5), PO-21 (s′) floor and [E1], [E2]; confirms (c′) and (d′) as design acceptances |
| **2b** | **OH-S3S**: operational-draft incorporation (Appendix B), if separately needed | documentation | none | G-1 | the draft's A-2 pins, matrix, interruption, stop and handback rows. Codex re-review of the draft (A-1) |
| **2c** | **OH-S0d**: apply Appendix A to the one-host design as a cumulative amendment (the design's own marker convention), including the dated C11 and D2 notes of §9.6 | documentation | none | G-1 | the accepted inactive design is amended in place. Codex re-review, then Peter's acceptance of the H-1 and activation design |
| **3a** | **OH-S4 (amended)**: Route 3 implementation of the non-launcher code, with tests (30) … (35) | repository only, unwired, nothing installed | none | 2c accepted (and 2a for version-bound data) | LD, IGR, SD, PK/2, HS, the role vectors. **Security-focused Codex review** |
| **3b** | **OH-S4p**: the launcher images, byte level (§9.10) | repository only | none | 2c accepted | PO-9R, D9-1 … D9-2 documentary and mechanical parts, the preliminary PO-17 evaluation. **Byte-level, security-focused Codex review** |
| **4** | an **R-5-class independent rebuild** of both images (D9-3), then **OH-S5** (the installation-source rebuild, §4.5), where still applicable | build as `ubuntu` on `oracle-test` | `oracle-test` | 3b accepted (and 3a for the tool bytes) | D9-3; the installation-source record. Retained R4/R5 outputs stay evidence only and are never an installation source |
| **5** | **H-0M1 and H-0M2**: read-only MF collection (§10) | read-only | `oracle-test` | 3a (the import closure for MF-1, MF-2); G-1 | MF-1 … MF-8 observations |
| **6** | **OH-S2c**: citation closure binding PO-19 (a′), (d), PO-12′, PO-11 (b), (g), PO-20 (a), (d) to the MF observations | documentation | none | 5 accepted | PO-19, PO-12′ and PO-11 verdicts |
| **7** | **H-1 readiness review** | review | none | 2a, 2b, 2c, 3a, 3b, 4, 5, 6 accepted; DEC-1 … DEC-6 recorded | the readiness list of §11.1 |

After G-7 the accepted successors are unchanged and **separately authorized**:
OH-S7 (H-1 assignment preparation), OH-S8 (H-1), CPP, H-2, OH-S8b (activation
fault drill), then A-2, `ACT`, Pass A and `DEACT`. Cleanup (LC-3 … LC-5) and
workspace recreation stay separate and are not sequenced by this table.

### 11.1 H-1 readiness list *(a review checklist, not an authority)*

1. DEC-1 … DEC-6 recorded; the repaired design and Route 3 accepted as the inactive
   basis; Appendix A applied to the one-host design (OH-S0d) and accepted.
2. PO-20 (f′), PO-21 (c′), (s′) and PO-11 (d′) accepted; PO-9R, D9-1 … D9-4 and
   the preliminary PO-17 evaluation accepted for **both** images.
3. PO-19 and PO-12′ **bound** to MF-1, MF-2 and MF-4, or each explicitly
   returned.
4. MF-3 observed and PO-11 (b), (g) decided; MF-5 and MF-6 observed and PO-20 (a),
   (d) decided; MF-7 and MF-8 covered.
5. The operational draft amended (OH-S3S) and re-reviewed (A-1).
6. The drift list of §9.7 fixed to accepted values.

---

## 12. Decisions needed from Peter

No accepted decision is silently changed by this proposal. **Two accepted
decisions are superseded or narrowed if Peter accepts the recommendation**
(D-3 and the CX-4 residual), and four design choices are bounded options with a
recommendation. Peter's acceptance of the repaired design as a whole follows
Codex's review (G-1). **OH-D-1 … OH-D-10, OS-6, OH-D-6 … 8, U-9's text, M-B, M-S
and the R2 dispositions are not changed.**

| ID | Decision | Recommendation | Bounded alternatives | Consequence |
|---|---|---|---|---|
| **DEC-1** | **Route 3.** This supersedes **D-3 (Route 1, exact `/usr/bin/python3.14`)** as the interpreter route, and confirms the scoping of §9.1 | **RT3-A** (§9.3): RX in front of the root helpers; the entry retargeted by one literal; PO-12′ and PO-19 narrowed | **RT3-B** (Python-free root path, §9.12). **RT3-Z**: no new image; accept X-1 as an explicit root-ambient residual (R-10) and bind PO-12′ and PO-19 for the entry only. It leaves the ambient inputs of §9.1 in place for the root helpers | RT3-A needs OH-S4p, a second image and its D9 chain. RT3-B needs a new proof method. RT3-Z needs no code and leaves PO-12 refuted for the root path |
| **DEC-2** | **PO-21 (c).** Which residual is acceptable | accept **RO-1** (§5.6) as the named, outside-guarantee, pre-pass and inert residual | elect **ALT-SENT** (§5.9), a resident sentinel, to narrow RO-1 | accepting adds no code beyond IGR. ALT-SENT adds a long-lived root image or process, citations and a drill |
| **DEC-3** | **PO-11 (d) parameters** (§7.3) | `pk_op_ms` 30,000, `pk_call_ms` 5,000, `lock_wait_ms` 5,000, S 120 s, R 60 s, `backstop_max` 20. P + c = 35,000 against the 90 s default start timeout leaves 25 s | shorter P (for example 15,000), at some risk of false `unconfirmed`; **or** a larger P with an explicit `TimeoutStartSec=` in the unit, which changes the reviewed unit bytes (T-B1) and the H-1 baseline | the values are A-2 pins. A wrong value fails closed (no pass, a refused start), never open |
| **DEC-4** | **Lock location** (LD-1) | the root-only object **K** under `/run` | keep the `ubuntu`-owned evidence directory as the lock object and rely on GR-1 and LD-2 … LD-6 only | K adds one `/run` object and path rows. Keeping the old object leaves `ubuntu` able to hold the lock, which then only refuses CP and delays HL, never holds a grant |
| **DEC-5** | **MF-3's observing slice** | a separate privileged read-only slice (**H-0M2**) **before H-1** | observe it in H-1's P-0p | the alternative saves a slice but settles PO-11 (b) only at install time |
| **DEC-6** | **CX-4 retirement.** Record that CX-4 is void for the cited systemd, because the accepted PO-21 (u) shows that a stop during `start-pre` ends the attempt `failed` | record the retirement, bound to systemd `259.5-0ubuntu3.4` | keep CX-4 as accepted (harmless) | retiring changes no mechanism. It removes a documented residual and adds the version-bound drift trigger of §6.8 |

---

## 13. Residuals, status of every obligation, and what this does not establish

### 13.1 Residuals

| ID | Residual | Status |
|---|---|---|
| RO-1 | uncatchable holder end while PID 1 can spawn neither stop-post nor the backstop | **new, named** (§5.6); pre-pass, inert; DEC-2 |
| RO-2 | helper bytes damaged after `ACT`: stop-post and backstop fail together | **new, named** (§5.6); IGR unaffected; AP-0, H-2, AM-0 detect a prior tamper |
| RO-3 | PID 1 dead or hung | outside every unit guarantee [R2 §8 (c)] |
| **CX-5** | with `τ₀ = 0`: a failed unidentified first attempt, then a root `reset-failed`, then the unit's unload | **new** (§6.5, SD-3); three root acts outside 𝒜 (SL-1 class). A later start runs the pass **with no grant** (G1 holds), but a second attempt occurs |
| CX-4 | a stop job during `start-pre` | **void** under R2 (u); retirement is DEC-6 |
| CX-1, CX-2, CX-3 | as accepted [D §4.2.5-R5 (k), R6 (f)] | unchanged |
| HB-1 | H-1, RB-1 and RS-1 run under `sudo`'s environment | restated (§9.4.4); question 5 |
| SL-1, DF-1, GU | as accepted [D §4.2.5-R2 (l)] | unchanged |
| the `ubuntu`-owned `ACT` evidence directory | `ubuntu` can replace the journal, which makes CL class the rule A0 and keep it, and makes CP refuse (accepted analysis [D §4.2.5-R4 (b)]) | **not changed for CL and CP**; under OH-D-6 it is no more than `ubuntu` can already do. **Narrowed for RL-0 only**: IGR uses the identity the holder holds in memory (§5.7). Flagged for the reviewer (question 2) |

### 13.2 Status of every obligation this proposal touches

| Obligation | Status after this proposal |
|---|---|
| PO-20 (f′-1) | **established** [R2 §7 (f)] |
| PO-20 (f′-2 … 5) | **proposed [N]**; OH-S2b citation |
| PO-21 (c′) | **established** [R2 §8 (c)] as a statement of what is not guaranteed; the ladder is design, not citation |
| PO-21 (s′) (1) … (4) | **established** [R2 §8 (s)]; (5) and the floor in (1) are **proposed [N]** |
| PO-21 (u) | **established** [R2 §8 (u)]; now load-bearing for CX-4's retirement (version-bound) |
| PO-11 (d′) | a **design acceptance**: it claims no bound, so no citation is needed. PO-11 (e), (f)(i), (f)(ii), (f)(iv) as accepted; (b), (g) remain **not established** (MF-3) |
| PO-9R | **proposed**; OH-S4p, D9-2 |
| PO-12′ | **source-established**; binding needs MF-4 |
| PO-19 | **not established** (MF-1, MF-2) |
| PO-17 | **not evaluated** against either image until OH-S4p; live evaluation at P-0, V-1, H-2 |
| PO-14, AD-7, PO-8, CL-21i | **established**, unchanged |

**Not addressed by this assignment, and still returned** [R2 §15.5 item 3]: PO-15 (d)
(`NeedDaemonReload`), AD-8 as a general statement (the closed-inventory restatement
is used here, §9.8), PO-17's type-E basename test, and C-1 … C-14 other than those
named in this proposal (C-9, C-10, C-11 and C-12 are answered by §§4 … 6 and 9).

### 13.3 What this proposal does not establish

It establishes no host fact and discharges no obligation. It does not show that RX
can be built, that its image is correct, that any helper behaves as specified or
that any parameter value is right. Each of those is a later gate (§11). It does not
change PO-14, LB-2S's two prevention claims about the entry, A-2, the start-only
grant, one start attempt, the no-follow source-consumption contract, evidence
durability or any fail-closed rule, and §2 shows why none of the four repairs can.

---

## 14. Proposed independent-review focus

1. **§2.** Is the reading right that no safety proof (G1 … G5) cites the lock,
   HL, `ExecStopPost=`, the backstop or a Polkit latency?
2. **§4.** Are LD-1 … LD-9 sufficient to prevent a longer-lived process from
   retaining a lock, and is the root-only object K (LD-1) the right choice over
   the `ubuntu`-owned directory (DEC-4)? Is the flagged `ubuntu`-owned journal
   directory (§13.1) correctly left alone?
3. **§5.** Does IGR (RL-0) need any citation beyond signal delivery by systemd? Is
   IL (§5.4) sound, and is RO-1 stated narrowly enough?
4. **§6.** Is BSP's use of `CLOCK_MONOTONIC` valid given [E1] and [E2], and is the
   handling table complete? Is CX-4's retirement under R2 (u) correct?
5. **§9.4.4.** Is HB-1 acceptable as a stated residual, or must H-1's own start be
   closed too?
6. **§7.** Is the operational-timeout design, with an `unconfirmed` that always
   fails closed, a sufficient answer to "no bound, no unbounded polling", and are
   the §7.3 inequalities and recommended values sound?
7. **§9.9.** Should helper children's loader inputs be observed (MF-9), or is the
   closed-map, root-owned-files argument enough?
8. **§9.4.3.** Is the RX contract (five roles, 34- and 64-byte operands, `attest`
   without `INVOCATION_ID`) within the class that D9 already proves, and is
   `umask 0077` for the root roles safe given AR-5?
9. **§9.9.** Are PO-12′ and PO-19 correctly narrowed, and is anything that R2
   refuted still hidden inside them?
10. **§9.6.** Is the Role A … H inventory complete against the current files?
11. **§9.12.** Is the surface argument for RT3-A over RT3-B fair, and is RT3-Z
    correctly presented as a residual-accepting alternative?
12. **§11.** Is the successor order and dependency structure right, and is any
    gate missing?

---

## Appendix A. Exact amendments needed in the one-host design

These are **proposed text changes** to the accepted, inactive
[one-host design](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md).
None is applied by this assignment. A later documentation slice (OH-S0d, §11)
would apply them, keeping the design's own D3-Rn labelling convention: each added
in place with an *(OH-S3 R1)* marker and the replaced text retained as history.

| # | Location | Action |
|---|---|---|
| A-01 | §4.1.3 TR-9 | interpreter becomes `/usr/bin/python3.14 -I -S` for the entry. **Add TR-6a′**: *the root roles' first image is `rp11-rootexec` (static), which writes the literal `rp11-helper-env/1` and then executes `/usr/bin/python3.14 -I -S`* |
| A-02 | §4.1.3, D3-R4 note on TR-6a | CP's program is `rp11-rootexec consume` |
| A-03 | §4.2.3 path tables | add `rp11-rootexec` (tree **L**, `root:root`, `0755`, state ST-1) and `K = /run/freedom-blades-rp11-lock-⟨activation_id⟩/` (`root:root`, `0700`, created by AM-0, removed by CL-5b or cleared by the boot) |
| A-04 | §4.2.4, stub line | `/usr/bin/python3.14`; add the **HB-1** sentence of §9.4.4 |
| A-05 | §4.2.5-R2 (b), (c) | paths gain K. A-2 pins gain `rootexec_sha256`, `launcher_sha256`, `pk_op_ms`, `pk_call_ms`, `lock_wait_ms`, `backstop_max`. **Replace "the PO-11 (d) bound"** by `pk_op_ms` and `pk_call_ms`. S's grammar becomes ⌈λ/1,000⌉ + ⌈(P + c)/1,000⌉ + 30 … 600 |
| A-06 | §4.2.5-R2 (d) AP-0, AM-0, AK-1, AV-1, `hold-start` | as §8.1. AM-0's lock text ("keep the lock until the holder exits") is already replaced by R4's AR-2 and is further replaced by K |
| A-07 | §4.2.5-R2 (e), (f), (i) | literals become §9.4.2's |
| A-08 | §4.2.5-R2 (g) and §4.2.5-R5 (g) OS-5 | "exits **while holding the lock**" becomes "appends and `fsync`s `hold-end`, closes K, then exits" |
| A-09 | §4.2.5-R2 (h) CL-0 … CL-5b; §4.2.5-R3 (e) GP-R3 | CL-0's lock, `lock-timeout` withdrawn, degraded mode; CL-3's `igr-removed`; CL-4's PK/2; CL-5b removes K. **Replace** the sentence "The kernel releases the lock when a process dies (PO-20 (f))" by LD-8 and GR-1 |
| A-10 | §4.2.5-R2 (j), (k), (l) | add **ST-1.i** (§8.4); the SP cells of the (k) matrix read "SP, *if PID 1 can spawn it* (RL-1), and IGR (RL-0) for a catchable end"; (l) gains RO-1, RO-2, RO-3, CX-5 |
| A-11 | §4.2.5-R4 (b) | the unit's one added line becomes `ExecStartPre=+/usr/local/libexec/freedom-blades-rp11/rp11-rootexec consume`; T-B1 admits exactly that |
| A-12 | §4.2.5-R4 (c) | **replace** "The lock is released by the kernel at every exit, including a kill (PO-20 (f))" by "CP closes K at CQ-7 and on every failure path; LD-4"; CP-6's "PO-11 (d) bound" becomes PK/2 |
| A-13 | §4.2.5-R4 (h) | the `ExecStartPre` normalization: path `…/rp11-rootexec`, `argv` `[…/rp11-rootexec, "consume"]`, `+` flag; the start-timeout rule becomes `T_s ≥ ⌈(P + c)/1,000⌉ + 30` |
| A-14 | §4.2.5-R5 (c) | OS-1 reads the baseline under **BSP** (§6.4) |
| A-15 | §4.2.5-R5 (e) | CQ-1 opens K; CQ-4's τ check cites SD-1; CQ-5 is PK/2 seek-not-authorized |
| A-16 | §4.2.5-R5 (f) | **replace Lemmas 2 and 3** by Lemmas 2′ and 3′ (§6.6); the third case is empty |
| A-17 | §4.2.5-R5 (g) | the lock paragraph: K, LD-2 … LD-5; the sentence "The kernel releases the lock at every process exit, including a kill" is withdrawn |
| A-18 | §4.2.5-R5 (j) | the PO-21 (s) row becomes (s′) (§6.9) |
| A-19 | §4.2.5-R5 (k), §4.2.5-R6 (f), (g) | CX-4 is marked **void** (§6.8), subject to DEC-6; "SB-2, except CX-4" and the other CX-4 qualifiers are retired accordingly; CX-5 is added |
| A-20 | §4.3.3 baseline | `files` gains `rp11-rootexec`; `ExecStartPre` normalization as A-13; the start-timeout rule as A-13 |
| A-21 | §4.4.1 | HF-10 and HF-11 gain the RX path and K's path (Role C, C2) |
| A-22 | §4.4.2 PO-19 | the scope text of §9.9: six consumers, file inputs, helper children out of scope; `/usr/bin/python3.12` becomes `/usr/bin/python3.14` |
| A-23 | §4.4.2a | PO-20 (f) becomes (f′) (§4.4); PO-11 (d) becomes (d′) (§7.8) |
| A-24 | §4.4.2b | PO-21 (c) becomes (c′) (§5.8); the (s) wording is withdrawn |
| A-25 | §4.4.3 citation order | add OH-S2b (§11); the PO-11 (d) citation step is removed |
| A-26 | §4.5 | the rebuild produces two images; `expected.sha256` gains four rows; the independent bindings (§9.7) apply to each |
| A-27 | §4.7.1 M-5 | entry interpreter `/usr/bin/python3.14`; the two installed static images are root-owned `0755` regular files pinned by digest. D-1's text is unchanged |
| A-28 | §4.6.2-R1 RB-1 | RX is a member of tree **L**; K is not an RB-1 object |
| A-29 | §4.2.4-R1 PT-8 | "(Python 3.12 has no wrapper)" becomes "CPython 3.14.4 has no `os` wrapper [R2 §10.5]" |
| A-30 | §4.7.4 | add the §11 rows; extend OH-S4's test list with (30) … (35) |

## Appendix B. Exact amendments needed in the operational draft

The draft, [`phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`](phase-5-0-p5-r5-operational-evidence-authorization-prompt.md),
is a **draft that authorizes nothing**, and this assignment does not edit it. These
are the **content obligations** for the OH-S3 successor (OH-S3S), by the draft's
own section and row identifiers. The final bytes are composed under that slice's
authority. Each new value follows the draft's typed-placeholder rule of §0 (no
value is filled by the operator's judgement).

| # | Draft location | Content to add or change |
|---|---|---|
| B-01 | §4.5 Maintainer inputs | new inputs, supplied only in the A-2 record: `MI.pk_op_ms`, `MI.pk_call_ms`, `MI.lock_wait_ms`, `MI.stop_timeout_s`, `MI.backstop_period_s`, `MI.backstop_max`, the existing lease parameters, `MI.rootexec_sha256`, `MI.launcher_sha256`, `MI.activation_id` |
| B-02 | §4.1 row A-2 | the A-2 record also quotes: the §7.3 inequalities as verified, the route (iii-a) pre-`stop` condition OC-1 … OC-3, and the sentence *"the consume step is part of the start; an activation admits one start attempt while every act stays within the pass's authorization"* |
| B-03 | §4.2 Authorization matrix | separate rows: `AP-2` (the holder), the operator's single `start` (only after `hold-start`), the executor's route (iii-a) `stop` (only under OC-1 … OC-3), the automatic CL triggers (`stop-post`, `backstop`) and `attest` |
| B-04 | §6 Pass A (before Band A1) | the activation chain as **admission rows**: AP-0's conditions (including drift of the RX and launcher digests and the §7.3 arithmetic), AP-1, AP-2, and the evidence each returns. The pass's own acts remain the entry's, started by one `start` |
| B-05 | §9.5.3 Interruption (C-15) | route (iii-a) only while OC-1 … OC-3 hold, with its pre-`stop` read recorded as operational evidence; **never** while the unit is `activating`; a hung consume step ended only by the start timeout; a failed consume step is **not** a pass |
| B-06 | §11 Stop conditions | add `lock-object`, `capture-baseline-unstable`, `grant-not-seen`, `stop-control-unconfirmed`, `consume-failed {CQ-5}` and INVALID RUN on any drift of the §9.7 list. **Stop, record, never repair** applies |
| B-07 | §13.1 Intended changes and §13.2 survey | add K, tree **P**, the rule (G1 → G3), the claim and consume evidence, the transient units and every record; the final survey adds K absent and the rule absent, each with PK *not authorized* from PK/2 |
| B-08 | §14 Handback template | add `lock`, `pk`, `release`, `capture`, `helper` and `params` (§8.5) and the journals' digests and lengths (OH-D-9) |
| B-09 | §3 Binding decisions | add rows for OH-D-10 (A) with OS-6 and for the Route 3 decision (once recorded) |
| B-10 | `PIN.interpreter` (`:342`), `OP.interpreter_version` | **unchanged**: `venv-web` CPython 3.12 is Role F and runs the suite and Pass A acts A1-S1 and A1-13. State this explicitly so it is not read as the entry interpreter |

## Appendix C. Identifier cross-check against the accepted R2 record

Every returned item and every MF identifier named in the prompt appears in the
accepted R2 record at the location shown. The handback records the check.

| Item | R2 location | R2 verdict | Where this proposal addresses it |
|---|---|---|---|
| PO-20 (f) | §7 table, §R2-6 | refuted | §4 |
| PO-21 (c) | §8 table, §R2-6 | refuted | §5 |
| PO-21 (s) | §8 table, §R2-6 | refuted | §6 |
| PO-11 (d) | §6.4, §R2-6 | not established | §7 |
| PO-12, AS-8 | §10.4, §R2-6 | refuted | §9 |
| PO-12′ | §10.4, §R2-6 | source-established; binding needs MF-4 | §9.9 |
| PO-19 | §11, §R2-6 | not established (MF-1, MF-2) | §9.9 |
| PO-17 | §12.9, §R2-6 | not evaluated | §9.10 |
| MF-1 … MF-8 | §14.3 | open | §10 |
| X-1 | §15.4 | cross-cutting finding | §9.1 |
