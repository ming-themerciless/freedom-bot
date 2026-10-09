# LIT-FULL WP-2 — system-call-intent operation inventory (R5 remediation return)

**Status: WP-2 R5 REMEDIATION RETURNED — INDEPENDENT RE-REVIEW PENDING.**

Work ID `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R5-20261009-19` (remediation of the R4 return, work ID `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R4-20261009-18`, itself a remediation of the R3 return, work ID `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R3-20261009-17`, itself a remediation of the R2 return, work ID `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R2-20261009-16`, itself a remediation of the R1 return, work ID `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R1-20261009-15`). Repository-only documentation deliverable of the accepted assignment `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5-remediation-claude-prompt.md`. This document replaces the R4 inventory as the proposed WP-2 result. This return does not accept WP-2, authorize WP-3, establish concrete Route 3 or select LIT-FULL for implementation. Independent Codex re-review of the complete WP-2 R5 return and Peter's later acceptance are required before any WP-3 prompt or authority may be prepared. Baseline v1.8 stands. No host was contacted.

This document is cumulative and self-contained: it can be reviewed without any earlier WP-2 draft. It states what accepted behavior needs at system-call intent. It selects no interface, language, syscall sequence, image architecture, parser, bound, proof method, equivalence disposition or estimate; each such question is recorded in §12 with its owning later package and is not answered here.

**R5 revision record.** The independent re-review of the R4 return closed `WP2-R3-1` and recorded one Blocking finding, `WP2-R4-1`; this document corrects only that finding. Everything else is carried from R4 unchanged. No row, step, table, tag or question is added or removed, so no count in §11 changes.

| Finding | Correction |
|---|---|
| `WP2-R4-1` — `RT3.SN.1` conflated cleanup recovery with child ownership | `RT3.SN.1` now separates three things. (1) *Owner of a child left behind by stop-post:* PID 1's `FINAL_SIGTERM`, then `FINAL_SIGKILL` after another S, to “what remains” (R8 §7.5a.7 SN-RO; R2 §8 (e)); whether that reaches a `setsid` child is PO-SN (e) and not guaranteed; the boot is a separate event; `attest` has no automatic owner of the child. (2) *Observer contract:* CS-7, CS-8, CS-10 leave a line; CS-1 … CS-6 and CS-9 leave the missing `run-end`; the backstop's CL or `attest` may record `children-unknown` and nothing acts on the child (SN-9). (3) *Recovery of the unfinished cleanup state* (the backstop's CL (RT-4) if armed and spawnable, else CP at a later start (CQ-3), then the boot, then `attest`) stays on `RT3.FI.2` and `RT3.CLG` … `RT3.CLOUT` and is not stated as the child's owner. The R4 prompt's instruction that gave the chain as the child's owner conflicted with accepted R8 and is superseded by it. |

**R4 revision record (carried; its `RT3.SN.1` owner sentence is superseded by the R5 record above).** The independent re-review of the R3 return recorded two Important findings; this document corrects only those. Everything else is carried from R3 unchanged, except counts and tables that are recomputed because the added row changes them (§11, stated there). The R3 BS-4 correction (`WP2-R2-2`) is untouched: SN-10 / A-I-16 apply to AK-1, BS-2 and BS-3 only, and BS-4 stays the third DI-4 call site under the open Q6-7.

| Finding | Correction |
|---|---|
| `WP2-R3-1` — withdrawn `T_s` formula presented as current | The expression `⌈P/1000⌉ + 30` (design text D R4 (g) AR-4, withdrawn by R8 §7.7 W-7) is removed from `RT1.FI.2` and from the §11.1 `T_s` row, and its citation is dropped there. What remains is what accepted text states: `T_s` is the capture unit's loaded `TimeoutStartUSec`, finite, PID 1's class-M deadline for CP, and it must satisfy N1, `T_s·1,000 ≥ W_show + W_series + ρ` with `W_show = c + g` and `W_series = P + c + g`. N1 is a necessary condition only; no margin is added, W-7 is not reinstated, and no elapsed-time guarantee is claimed. |
| `WP2-R3-2` — no per-procedure `RT-3.SN` row | `RT3.SN.1` is added to §5.3 (class CN, tag [A], no [Q] tag), parallel to `RT1.SN.1`, `RT2.SN.1`, `RT4.SN.1` and `RT5.SN.1`, and an `SN` step is added to the RT-3 trace in §6. It states the child surface in the two tiers of §8.1 and keeps the stop-post recovery owner chain. RT-3 performs neither DI-3 nor DI-4, so the row carries neither Q6-6 nor Q6-7. Counts change as stated in §11: rows 317 → 318, CN 62 → 63, RT-3 14 → 15, tag [A] only 237 → 238, RT-3 steps 13 → 14, steps 76 → 77, and taxonomy rows 1, 2, 3 and 3a … 3g each +1. |

**R3 revision record (carried).** The independent re-review of the R2 return recorded three findings (two Blocking, one Important); this document corrects only those. Everything else is carried from R2 unchanged, except counts and tables that are recomputed because a corrected row changes them (§11, stated there).

| Finding | Correction |
|---|---|
| `WP2-R2-1` — complete-reading precondition not met | Not a change to the inventory text. Every required source was read first byte through EOF before the first edit of R3; the reading ledger (path, lines, bytes, SHA-256, re-verified unchanged after the reading) is in the R3 handback. |
| `WP2-R2-2` — SN-10 / A-I-16 extended to BS-4 | Accepted text names the `effect: "unknown"` obligation for the DI-4 call at BS-2 and BS-3 only. The extension to the BS-4 terminal disarm is removed from `RT4.BS4.2`, `RT4.SN.1`, §7 (DI-4), §8 (PC-5), §8.1, §11.4, §12 (Q6-6) and §13. BS-4 stays the third DI-4 call site (`CALL-DI4-03`); whether SN-10 / A-I-16 extends to it is **not decided** and is carried as an open part of Q6-7 (owner WP-6). |
| `WP2-R2-3` — final link-check result missing | The terminal link-check scope, link count, broken-link count and exit status are in the R3 handback. |

**R2 revision record (carried).** The independent review of the R1 return recorded two findings; this document corrects only those two. Everything else is carried from R1 unchanged, except counts and tables that are recomputed because a corrected row or definition changes them (§11, stated there).

| Finding | Correction in this document |
|---|---|
| `WP2-R1-1` — AM-0 row selected an unresolved behavior | `RT2.AM0.7` no longer states any operation: it is a non-operative **gap row** (class GAP, tag `Q6-7`) that records the accepted-text gap and instructs nothing. WP-2 selects neither answer to whether AM-0 repeats AP-0's “no unterminated activation” condition; the question stays open as Q6-7 (§12, owner WP-6). The unambiguous AM-0 operations are unchanged. |
| `WP2-R1-2` — DI-3/DI-4 child surface and DI-4 call sites inconsistent | The accepted-today dynamic-child behavior and the LIT-FULL replacement child set are separated (§8.1; rows `RT1.SN.1`, `RT2.SN.1`, `RT4.SN.1`, `RT5.SN.1`, `H-SN.1`). The SN-10 / A-I-16 “effect unknown” obligation is kept and carried, unmapped, as Q6-6. §7.1 now counts **logical accepted call sites** from an explicit call-site table; DI-4 has three sites (BS-2, BS-3, BS-4 terminal disarm); §§7.2, 8, 11.3(c), 11.5, 12, 13 and 14 use that unit. |

## Contents

1. Fixed scope and exclusions
2. Fact tags, conventions, classes and sources
3. Procedure and sub-role roster
4. Shared-helper operation tables
5. Per-procedure operation tables
6. Step trace: every accepted step to its rows
7. DI-1 … DI-6 and the stop-unit call: replacement-intent map
8. Process-creation classification
9. SN-I-1 … SN-I-4, SN-4 and the reap surface, traced
10. Interruption maps, terminal causes and residuals
11. Parameters, coverage and reconciliation tables
12. Questions deferred to WP-3 … WP-7
13. Inputs WP-3 may and may not rely on
14. Acceptance checklist
15. Stop rule applied

## 1. Fixed scope and exclusions

This section records the accepted boundary exactly; it is authority, not a question. **The scope header and the role roster in §1 and §3 are the FR-1 documentation amendment**: they record the accepted boundary and name the `start` and `stop` roles in the commissioned work. They do not amend a historical proposal and do not perform WP-3 through WP-7.

- The path is **LIT-FULL under R3-ROOT**. The unprivileged `ubuntu` entry remains Python and is outside the root-procedure set. [A]
- The in-scope procedure set is exactly **RT-1 through RT-5 plus SA-1 and SA-2**: consume, hold, stop-post, backstop, `attest`, the `AP-2` static `start` role and the OS-6 static `stop` role. [A]
- Under EX-1, each `sudo`-started in-scope procedure begins at the first design-controlled static image. `sudo`, and nothing else, is outside its inventoried tree as an LR-2 launch-preamble exception. [A]
- Under EX-2, the installer class H-1, RB-1, RS-1 and H-1R is outside the root-procedure set, with HB-1 accepted. Installer operations are not inventoried here as WP-2 procedures and no H-1R invocation literal is asserted. [A]
- **No EX-3** exists. Both lifecycle acts (`start`, `stop`) are in the set. [A]
- BQ-4 permits **no dynamic child** in an in-scope procedure's process tree. Every process-creation intent must ultimately be a fork continuing in a static image or an `execve` of a design-controlled static image. An `execve` of a distribution program is not an admissible WP-2 result. [A]
- B2-N and a Python-free installer are not prerequisites for this combination. [A]
- BC-2 remains a later WP-9 question and is not decided here. [A]
- Concrete Route 3 remains **unestablished**. Nothing in this inventory claims otherwise. [A]
- The F-1 combination is: B2-F; `AP-2` and the OS-6 `stop` both in; B3-OUT. [A]

Everything below is bounded by those items. Where the accepted text of a function today uses a dynamic distribution program (`systemctl`, `systemd-run`, `pkcheck`, `sleep`) the row records the **intent** the replacement must realize and the later owner; it never names a replacement executable, protocol or library.

## 2. Fact tags, conventions, classes and sources

### 2.1 Fact tags

| Tag | Meaning |
|---|---|
| **[A]** | Accepted text: the row restates an operation, bound, order or failure contract that the cited accepted record states. The citation is the evidence. |
| **[M]** | Mechanically derived inventory statement: a count, a mapping or a classification that follows from [A] rows by inspection, with no new behavior. |
| **[Q`<owner>-<n>`]** | A later-package obligation: the accepted text does not decide the point; the question is recorded in §12 under that identifier with its owning package and is **not answered** here. Written `A;Q3-1` in the tag column when an accepted row also carries an open obligation. |

In the tables the **Tag** column carries these tags. No row carries a claim beyond its citation. Where a row says a mechanism is "not stated", that is the finding; it is not a defect to be repaired in WP-2.

A row tagged with a `Q` alone (no `A` and no `M`) is a **gap row**: it records that accepted text does not decide a point, states no operation, and cannot be consumed as an instruction to perform, list, check or omit anything. Its class is GAP. A mechanically derived `[M]` tag is never given to a statement that chooses between answers to an open question.

### 2.2 Row format and identifiers

Row identifiers are `<procedure>.<step>.<n>` (e.g. `RT1.CQ0.1`), or `<helper>.<n>` for shared-helper rows (e.g. `H-SN.6`). Trigger-instance rows of the shared cleanup are `<RT3|RT4|RT5>.<step>`. A row's **§7.3** cell lists the R8 §7.3 taxonomy rows (1 … 22, 3a … 3g) it falls under (`—` where none applies). **Blocking / bound** carries the accepted class (E enforced by the helper, M manager deadline, C count, X unbounded or no accepted bound, volume cap) only where the accepted record supplies it; a class-X call is never turned into an elapsed-time bound and a scheduled-waiting budget is never turned into a return bound. **Failure / interruption contract** is the accepted fail-closed outcome, interruption state or "unknown" state; a signal attempt is never read as proof of exit and a missing record is never read as proof of absence.

### 2.3 Operation classes

| Code | Class |
|---|---|
| EN | environment / entry condition of a first image |
| FD | descriptor handling |
| SR | signal-disposition reset or handler installation |
| FS | filesystem and metadata access (open, read, stat, list, directory work) |
| FM | filesystem mutation (create, link, rename, unlink, mode, owner) |
| SY | flush / synchronization |
| LK | advisory lock operation |
| CK | clock read |
| SL | sleep |
| HS | hashing |
| PR | parse / serialize / validate a record |
| JR | journal or record publication |
| UA | unit-manager or authorization interaction (DI-1 … DI-5, stop-unit call) |
| PC | process creation |
| CR | credential change of a created child |
| ID | identity capture / validation |
| SG | signal send |
| PL | poll / reap attempt |
| XT | exit or return |
| DG | diagnostic output |
| CN | contract row: a rule, bound or ownership statement that fixes how other rows behave, with no system-call intent of its own |
| CMP | composition row: a trigger instance of a shared cleanup step, naming the helper rows it performs |
| GAP | gap row: records an accepted-text gap carried as a later-package question; no operation, no system-call intent, no instruction (tag `Q` alone) |

### 2.4 Source abbreviations

| Abbreviation | Source |
|---|---|
| D | the accepted one-host design, `docs/review/phase-5-0-p5-r5-rp11-h1-design.md` family as cited by the accepted record; `D R5 (e)` means §4.2.5-R5 item (e); `D 4.3.x` means design §4.3.x |
| R8 | the accepted R8 remediation text (signal operation contract §7.5a, §7.3 taxonomy, §7.4 … §7.9, §8, §9) |
| R2 | the accepted R2 citations (version-bound facts, PO-21 items) |
| W1 | the accepted WP-1 R6 record (roster, EX-1/EX-2 consequences, DI-1 … DI-6 site lists, FR-1) |
| AP | the accepted EX-1 / EX-2 approval record (`lit-full-wp1-ex1-ex2-approval`) |

Parameter symbols: P = `pk_op_ms`, c = `pk_call_ms`, g = `reap_grace_ms`, λ = `lock_wait_ms`, slice_ms, S = `stop_timeout_s`, S_b = `bs_runtime_s`, R = `backstop_period_s`, B = `backstop_max`, ρ = `reserve_ms`, L = `lease_s`, W = `start_window_s`, Δ = `poll_ms`, T_s = CP's start timeout (§11.1).

**Reading and checking method (stated for the reviewer).** The R1 rows were authored in structured form with a scratch generator held outside the repository. For R2 and R3 the corrections were made directly in the delivered Markdown, and every count in §§7.1, 11.2 – 11.5 was **recomputed by a read-only parser run over the delivered bytes of this document** (parser held in the session scratchpad outside the repository, not delivered). The parser and the scratchpad are conveniences, not evidence: the delivered document is the only artifact. Treat §11's counts as [M] and verify them against the tables. The counting rules are stated where each table is given (§7.1 for call sites; §11.3(d) for identifier citations).

## 3. Procedure and sub-role roster

| ID | Procedure | Caller | Beginning boundary | Accepted current implementation | Accepted failure contract | Sub-roles |
|---|---|---|---|---|---|---|
| `RT-1` | consume (CP: CQ-0 … CQ-7) | PID 1, the capture unit's `ExecStartPre=+` step, inside that unit's start job, after Polkit authorized the operator's `start` and before PID 1 may execute `ExecStart=` | the first design-controlled static image that PID 1 executes (no `sudo`, no dynamic program before it); nothing from the requester reaches it (PO-21 (n)) | `python3.12 -I -S …/rp11_h1.py consume` under PID 1's open environment block (refuted for the root roles, X-1); accepted design CQ-0 … CQ-7 of D §4.2.5-R5 (e) as amended by R8 §8.1 Machine C (K lock, PK/2, BSP-aware CQ-4) | every exit other than CQ-7's exit 0 is non-zero and leaves `ExecStart=` unexecuted (PO-21 (o)); a CP failure is a failed start, not a pass; no `consumed` line means no pass; stable codes consume-unidentified / consume-busy / consume-repeated / consume-claim-failed / consume-evidence-unwritable / consume-precondition / consume-failed {step, class}; SB-1, SB-2, SB-3 refuse every later attempt (contract OSA over 𝒜, no exception within 𝒜; CX-4 outside 𝒜) | RT-1.CQ (claim, grant, preconditions, post-check, consumed); RT-1.PK (PK/2 series at CQ-5); RT-1.SN (child contract) |
| `RT-2` | hold (the holder: ACT, HL, IGR, GRR and AV-1) | PID 1, the main process of the transient holder unit `⟨activation_id⟩.service` that SA-1 creates | the first design-controlled static image that PID 1 executes for the holder unit | `python3.12 -I -S …/rp11_h1.py hold ⟨id⟩ ⟨a2⟩` under PID 1's open environment block; accepted design D §4.2.5-R2 (d) AM-0 … AM-3, (g) HL, R8 §5.7 IGR/GRR, R8 §8.1 Machine H (SG-1, K, GI-1, BSP, AV-1 negative control, OS-1, OS-5, OS-7) | any failure before AM-3: exit non-zero then CL through `ExecStopPost=`; HARD STOPs `lock-object`, `capture-baseline-unstable`, `grant-not-seen`, `stop-control-unconfirmed`; `capture-busy-at-act`; OS-7 `start-before-hold`; IGR on every catchable end; uncatchable ends are covered by RL-1 … RL-4 and the inertness lemma (IL, IL′) | RT-2.SG (signal discipline); RT-2.AM0 (re-check, K, BSP, journal); RT-2.AK1 (backstop arming, DI-3); RT-2.AM1/AM1R/AM1G (tree P, tree R, grant.id); RT-2.AM2 (rule publication); RT-2.AV1 (verification, H-2b, PK/2 controls); RT-2.AM3 (act record); RT-2.HS (hold-start); RT-2.HL (hold loop); RT-2.IGR (inline grant release, GRR); RT-2.SN (child contract) |
| `RT-3` | stop-post (CL, trigger `stop-post`; CL-G, GP-R3) | PID 1, the holder unit's `ExecStopPost=` | the first design-controlled static image that PID 1 executes for `ExecStopPost=` | `python3.12 -I -S …/rp11_h1.py deact ⟨id⟩ ⟨a2⟩ stop-post` under PID 1's block; accepted design D §4.2.5-R1 (e), R2 (h), R3 (e), R5 (g), R8 §5.7 (CL-G, GRR), §8.1 CL deltas | `st1-verified` or HARD STOP (ST-1+R) with a residual list; `record-unpublished`; `evidence-unwritable` under GP-R3 (ST-1.ur); `unit-still-active`; a stop-post that PID 1 cannot spawn is skipped (`FINAL_SIGTERM`, result `resources`) and RT-4 is the next rung | RT-3.CL (CL-G … CL-7); RT-3.GP (GP-R3); RT-3.PK (PK/2 at CL-4); RT-3.SN (child contract) |
| `RT-4` | backstop (BS-1 … BS-4 and CL, trigger `backstop`) | PID 1, the service that the backstop timer starts (the holder creates the timer at AK-1) | the first design-controlled static image that PID 1 executes for the backstop service | `python3.12 -I -S …/rp11_h1.py backstop ⟨id⟩ ⟨a2⟩` under PID 1's block; accepted design D §4.2.5-R2 (f) with BS-RM (R8 §7.4) and BS-4 Δ2 (R8 §8.1) | BS-1 … BS-3 exit `0` without record; BS-4 runs CL; after `backstop_max` firings or `k` > 99 the timer is disarmed, a journal line appended and the service exits non-zero without a record; each firing ends at `RuntimeMaxSec=` S_b (BS-RM) | RT-4.BS (BS-1 … BS-4); RT-4.CL (CL, trigger backstop); RT-4.PK (PK/2 at CL-4); RT-4.SN (child contract) |
| `RT-5` | attest (CL, trigger `attest`; first act CL-G) | the executor / operator, interactive, `sudo -n`; no unit | the first design-controlled static image that `sudo -n` executes (BQ-2 answered B2-F by Peter; EX-1: `sudo` alone is a launch preamble outside the inventoried tree) | `sudo -n /usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_h1.py deact ⟨id⟩ ⟨a2⟩ attest` (installed tool by path; D §4.2.5-R2 (i)); not the verified-exec stub | refuses to run CL while the holder or either backstop unit is `activating`, `active`, `deactivating` or `reloading`; otherwise as RT-3; records `cleared-by-boot` / `st1-verified` only if CL-4 and CL-6 hold; an interruption leaves records missing and every later RP-11 step refuses; no automatic owner for a left-behind child | RT-5.PRE (unit-state precondition); RT-5.CL (CL, trigger attest); RT-5.PK (PK/2 at CL-4); RT-5.SN (child contract) |
| `SA-1` | `start` role — AP-2, creating the holder unit | the executor, privileged, under A-2 | the first design-controlled static image that `sudo -n` executes (PD-2a = B2-F; PD-2b = in; EX-1) | `sudo -n /usr/bin/systemd-run --system --no-ask-password --quiet --unit=⟨id⟩ --service-type=exec --property=Restart=no --property=OOMScoreAdjust=-1000 --property=RuntimeMaxSec=⟨L⟩ --property=TimeoutStopSec=⟨S⟩ "--property=ExecStopPost=…" ⟨holder command⟩` (D §4.2.5-R2 (e)); DI-2 | a name already loaded makes the call fail and create nothing (PO-21 (m)); the executor then finds the unit not loaded ⇒ INVALID RUN, nothing mutated; a loaded unit means the holder governs; the call's own failure contract is not accepted text | SA-1.FI; SA-1.OP (operands, DI-2 call, return) |
| `SA-2` | `stop` role — the OS-6 interruption | the executor, under A-2, only while OC-1, OC-2 and OC-3 hold | the first design-controlled static image that `sudo -n` executes (PD-2a = B2-F; PD-2b = in; EX-1) | `sudo -n /usr/bin/systemctl stop rp11-capture-pass-a.service` (D §4.2.5-R4 (e), R6 (b)); the stop-unit call has no R8 DI row | a §9.5.3 interruption: no X-3 finalization, capture root retained read-only; if the condition cannot be established the route is unavailable and the pass continues without a grant (CX-3); the call's own failure contract is not accepted text | SA-2.FI; SA-2.OP (preconditions outside, stop-unit call, return) |

The sub-role identifiers are the groups of rows in §5; each shared helper in §4 is instantiated by the procedures named in §6. `sudo` is the only element outside the inventoried tree of RT-5, SA-1 and SA-2 (EX-1). RT-1 … RT-4 are started by PID 1 and have no `sudo`, no dynamic program before their first design-controlled static image, and nothing from the requester reaching it. [A]

## 4. Shared-helper operation tables

Shared helpers are kept as separate rows and are instantiated by name, not collapsed. Sections follow the order in which a root image meets them.

### 4.1 H-FI — First-image state operations (RH-1 … RH-3)

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `H-FI.1` | EN | Treat the inherited environment as untrusted: no variable decides anything except, for the four unit-started roles that read it, the 32-lowercase-hex INVOCATION_ID selection (RH-1); `attest`, the `start` role and the `stop` role read none | R8 §9.2 RH-1; R8 §7.5 HS-6; R8 §9.7 (comparison only: `attest` reads none) | — | X | a malformed or duplicate selection is refused before any state operation (NT-RH-1 class); exit values not accepted for LIT-FULL | A;Q4-2 |
| `H-FI.2` | FD | Check that descriptors 0, 1 and 2 are open; a closed 0, 1 or 2 is refused | R8 §9.2 RH-2; R8 §9.14 NT-RH-2 | — | X | refuse before the first state operation | A;Q4-2 |
| `H-FI.3` | FD | Close every descriptor numbered 3 or higher before the first state operation | R8 §9.2 RH-2; R8 §4.5 LD-3 (d) | — | X | none stated (no state exists yet) | A |
| `H-FI.4` | SR | Reset every signal disposition that can be reset and clear the signal mask (where unit configuration does not already fix them) | R8 §9.2 RH-3 | — | X | none stated | A |
| `H-FI.5` | FS | Fix `umask` and the working directory (where unit configuration does not already fix them) | R8 §9.2 RH-3 | — | X | none stated | A |
| `H-FI.6` | CN | Limits, `no_new_privs`, capabilities, securebits, seccomp, namespaces, cgroup, scheduling, `oom_score_adj` and timers are not touched and not claimed by the first image | R8 §9.2 RH-3 (R-10, K-5) | — | — | — | A |
| `H-FI.7` | CN | LR-1 and LR-3 … LR-6 hold from the first design-controlled image downward; LR-2 holds from the same image (for the three `sudo`-started roles `sudo` alone is the launch preamble outside the tree, EX-1) | AP (EX-1); R8 §9.2 LR-1 … LR-6 | — | — | a dynamic program at or below the first image is a failure (not an exception) | A |

### 4.2 H-CLK — Clocks and sleeps

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `H-CLK.1` | CK | Read the monotonic clock to set an absolute deadline before a wait starts and to test it at each wake-up; every sleep lasts at most `slice_ms` and at most the time then remaining to its own deadline, and is not started when nothing remains | R8 §7.2 class E; R8 §7.5a.6a WB-2, CC-10 | 3,7 | E (deadline per wait) | expiry applies the wait's own fail-closed consequence | A |
| `H-CLK.2` | SL | Sleep for the capped interval of H-CLK.1; the sliced interval is the longest between flag checks inside any E wait (`slice_ms`, 50 … 250, recommended 100) | R8 §7.6; R8 §7.8 SG-4 | 7 | E | the holder observes its stop flag at each wake-up (SG-4) | A |
| `H-CLK.3` | CK | Read the wall clock (UTC) for the record `time` fields `start_utc`, `end_utc`, `grant_linked_utc`, `grant_removed_utc`; elapsed values recorded are observations, never claims | D R1 (g) `time`; R8 §8.5 `pk.elapsed_ms` | — | X | a failed read is not an accepted case; value `absent` is the accepted placeholder for an unreached event | A;Q4-11 |

### 4.3 H-LK — The lock on K (LD-1 … LD-9)

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `H-LK.1` | FD | Open K = `/run/freedom-blades-rp11-lock-⟨activation_id⟩/` from a descriptor of `/run` for reading as a directory without following a final symbolic link, close-on-exec; the descriptor is never duplicated, passed, shared with another thread or stored beyond the acquisition | R8 §4.5 LD-1, LD-2, LD-3 (a) | 6 | X | K absent, not a directory, wrong owner/mode or unopenable: CP `consume-unidentified`; HL `observation-failed`; CL `lock_mode: "absent"` (degraded); holder AM-0 HARD STOP `lock-object` | A |
| `H-LK.2` | LK | Take an exclusive advisory lock on the K descriptor without blocking; one attempt (holder AM-0, CP, HL decision) or repeated attempts until the λ deadline (CL); an interrupted attempt is retried within the deadline, any other error is "cannot acquire" | R8 §4.5 LD-5; R8 §4.6; R8 §4.7 | 6 | X per call; E (λ = `lock_wait_ms`, 1,000 … 10,000, rec. 5,000) for the CL loop; none claimed for CL's elapsed time | `EWOULDBLOCK`: CP `consume-busy`; HL does not end and re-observes after Δ; CL continues in degraded mode after λ (`lock_mode: "degraded"`); other error as cannot acquire | A |
| `H-LK.3` | FD | Close K at the explicit close point (holder: after `hold-start` is durable; HL: after `hold-end` is durable and before exit, or at once if no terminal reason holds; CP: after `run-end` and on every failure path; CL: after `run-end`); no process is designed to end while holding the lock | R8 §4.5 LD-4; R8 §4.6 | — | X | a descriptor left open is released only at the last close of its open file description (kernel); no design path keeps it | A |
| `H-LK.4` | CN | A process holds a lock only while single-threaded; no raw `fork` in any root helper; a child exists only via the single process-creation function; no procedure scans for, signals, ptraces or kills a lock holder; `/proc/locks` is read by no decision | R8 §4.5 LD-3 (b),(c), LD-9 | — | — | — | A |

### 4.4 H-JRN — Journals (format `rp11-journal/1`)

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `H-JRN.1` | FD | Open the evidence directory (ACT: `/var/tmp/⟨activation_id⟩-act-evidence/`) for reading as a directory without following a final symbolic link; the root tool requires owner `ubuntu` and mode `0700` for the ACT directory | D R1 (b); D R4 (c) CQ-1 (superseded by R8 K for the lock) | 11 | X | a missing or unopenable ACT directory makes every object A0 for removal and nothing is removed | A |
| `H-JRN.2` | FM | Create the file `journal` in the evidence directory with exclusive creation, write-only, append, no-follow, close-on-exec (mode `0644`; the consume journal is created `0600` then `fchmod` `0644`) | D R1 (b); D R5 (d) | 11 | X | cannot create: CL enters GP-R3 (E-a); CP follows grant-priority form; holder AM-0 HARD STOP | A |
| `H-JRN.3` | SY | After creating the journal, flush the file and its directory so both are durable | D R1 (b) | 11 | X | a failed flush is "a line that cannot be made durable": same branches as H-JRN.2 | A |
| `H-JRN.4` | HS | Compute the SHA-256 of the previous line's exact bytes for the `prev` field (64 `0` characters for `seq` 1) | D R1 (b) | 9 | X | — | A |
| `H-JRN.5` | PR | Serialize one entry as `canonical_bytes`: one canonical JSON object (sorted keys, compact separators, ASCII, no floats, no `null`, absent facts as the string `"absent"`) followed by LF, with `seq`, `prev`, `run`, `op` and the closed fields of that `op` | D R1 (b); D 4.3.1 | 8 | X | — | A |
| `H-JRN.6` | JR | Append the whole line with a single write; short write or write error stops the tool, nothing further is mutated, the flush is never retried (H-1/ACT publication); for CL and CP evidence lines a failed append reduces what can be claimed and enters GP-R3 / grant-priority form | D R1 (b); D R3 (e); D R5 (e) | 11 | X | see GP-R3 entries E-b, E-c; CQ-2 branches | A |
| `H-JRN.7` | SY | Flush the journal file after every appended line before the step the line announces or records | D R1 (b) (invariant W); D R4 (c) | 11 | X (stall unbounded, RO-6) | a stalled flush is not bounded; the grant is already removed before any `ext4` write by IGR/CL-G (GR-2) | A |
| `H-JRN.8` | FS | Read a journal for parsing: read at most `journal_max_bytes` (65,536 … 4,194,304; rec. 1,048,576) | R8 §7.3 row 8; R8 §7.6 | 8 | X + volume cap | oversize ⇒ `invalid-journal`, fail closed | A |
| `H-JRN.9` | PR | Parse a journal: split at LF; a final segment without LF is a torn tail (ignored, reported); every complete line must be canonical (re-serialization equal), `seq` contiguous, `prev` correct, `run` expected, `op` known and exactly its closed fields; any violation makes the journal invalid and every object A0 | D R1 (b); D R5 (e) CQ-3 | 8 | X | invalid or missing ⇒ nothing is removed on its authority | A |
| `H-JRN.10` | CN | Closed `op` sets: ACT journal = run-start, backstop-intent, backstop-armed, tree-intent, dir-identity, file-intent, file-identity, file-linked, tree-sealed, tree-linked, grant-check, hold-start, pass-observed, hold-end, run-end (+ `igr`, `child`); CL attempt journal = run-start, remove-intent, removed, remove-failed, grant-check, classified, file-intent, file-identity, file-linked, run-end (+ `cl-g`, `child`); consume journal = run-start, remove-intent, removed, remove-failed, grant-check, consumed, consume-failed, run-end (+ `child`) | D R2 (m); D R4 (c); R8 §8.5 | — | — | — | A |

### 4.5 H-PF — Protocol PF — publish one file

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `H-PF.1` | FS | Require that nothing exists at the target name in the open parent directory (lookup without following a final symlink must give "absent") | D R1 (c) PF-1 | 11 | X | anything else: HARD STOP `preexisting-path`; the object found is class A0 | A |
| `H-PF.2` | JR | Append `file-intent {dir, name, sha256, size, uid 0, gid 0, mode, grant}` (`grant` true only for the active rule) and flush | D R1 (c) PF-2 | 11 | X | stop at once (publication) / GP-R3 (CL) | A |
| `H-PF.3` | FM | Create an unnamed regular file in the parent directory (unnamed temporary file; exclusive-create flag not used, so it can be linked later), write-only, close-on-exec, mode `0600` | D R1 (c) PF-3 | 11 | X | failure: stop; the name stays absent | A |
| `H-PF.4` | FS | Check the new inode is a regular file, uid 0, zero links, size 0; append `file-identity {dir, name, dev, ino}` and flush | D R1 (c) PF-4 | 11 | X | identity must be durable before any name exists (invariant I) | A |
| `H-PF.5` | FM | Write the bytes in full; flush the file; set owner `0:0` and mode; flush again; re-check same `(dev, ino)`, size and mode | D R1 (c) PF-5 | 11 | X | failure: stop; only an unnamed inode exists (freed on last close) | A |
| `H-PF.6` | FM | Link the unnamed inode under its final name, no replace, in the form the file-creation interface documents for unnamed temporary files (link of `/proc/self/fd/⟨fd⟩` into the parent descriptor following the link) | D R1 (c) PF-6; R2 §7 (a) | 11 | X | `EEXIST`: HARD STOP, the object found is A0, the unnamed inode is freed on close | A;Q4-1 |
| `H-PF.7` | SY | Flush the parent directory so the name is durable | D R1 (c) PF-7 | 11 | X | a crash between PF-6 and PF-7 leaves the name present or absent, both attributable | A |
| `H-PF.8` | JR | Append `file-linked {dir, name}` and flush (the commit) | D R1 (c) PF-8 | 11 | X | — | A |
| `H-PF.9` | FS | Close the descriptor; re-open the final name read-only without following; require recorded `(dev, ino)`, regular file, uid and gid 0, mode, one link, size, no forbidden extended-attribute name (names only), and a re-read SHA-256 equal to the digest | D R1 (c) PF-9; D 4.2.3 | 8,9,10 | X + volume cap (≤ 65,536 bytes for GRR-class files) | a mismatch is a HARD STOP of the enclosing step (CL runs) | A |

### 4.6 H-PT — Protocol PT — build and publish a directory tree

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `H-PT.1` | FS | Require that neither the final top name nor the temporary name `.rp11-⟨RUN⟩-⟨tag⟩.tmp` exists in the pre-existing parent | D R1 (d) PT-1 | 11 | X | otherwise HARD STOP; what is found is A0 | A |
| `H-PT.2` | JR | Append `tree-intent {parent, top, temp, tag, members}` and flush | D R1 (d) PT-2 | 11 | X | — | A |
| `H-PT.3` | FM | Create the temporary top directory (mode `0700`, no replace), open it as a directory without following, check directory/uid 0/mode `0700`/two links/empty, append `dir-identity {rel ".", dev, ino}` and flush (window W-T from creation to this flush) | D R1 (d) PT-3 | 11 | X | a crash in W-T leaves an S0 name that is never final, never removed, never blocking | A |
| `H-PT.4` | FM | For each member directory in pre-order: create (`0700`), open and verify as PT-3, append `dir-identity`, flush | D R1 (d) PT-4 | 11 | X | — | A |
| `H-PT.5` | CN | Each member file is published by protocol PF into its directory descriptor (rows H-PF.1 … H-PF.9) | D R1 (d) PT-5 | 11 | — | — | A |
| `H-PT.6` | FM | Bottom-up for each directory: set owner `0:0` and final mode, flush; finally flush the parent | D R1 (d) PT-6 | 11 | X | — | A |
| `H-PT.7` | FS | Seal: list every directory of the tree (entries must be exactly the members), `fstatat` each member against its identity line; append `tree-sealed {temp, inventory_sha256}` (canonical list `[rel, kind, dev, ino, mode, sha256 or "absent"]`) and flush | D R1 (d) PT-7 | 8,9,10,11 | X | mismatch: HARD STOP, the tree stays under the temporary name | A |
| `H-PT.8` | FM | Rename the temporary top to the final name with no-replace semantics, atomically (glibc `renameat2` with `RENAME_NOREPLACE` in the accepted design) | D R1 (d) PT-8; R2 §7 (c); R2 §10.5 | 11 | X | `EEXIST`: HARD STOP, A0 at the top, tree stays under the temporary name; `EINVAL` refutes PO-20 for the host | A;Q4-1 |
| `H-PT.9` | SY | Flush the parent, append `tree-linked {parent, top}`, flush (the commit) | D R1 (d) PT-9 | 11 | X | — | A |
| `H-PT.10` | FS | Verify: open the top without following; recorded `(dev, ino)`; every member re-verified (files as PF-9) | D R1 (d) PT-10 | 8,9,10 | X | — | A |

### 4.7 H-GR1 — Attribution, re-verification and the removal guard G-R1

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `H-GR1.1` | FS | Classify the object at a target name against the identity line in the journal: look it up without following a final symlink; type and `(dev, ino)` must equal the line, uid and gid 0, recorded mode (or `0700` for an unsealed temporary directory), and for a file recorded size, SHA-256 and one link — classes A1-intact, A1-damaged, A0, S0, absent | D §4.6.2-R1 (attribution classes); D R1 (e) | 8,10 | X | A1-damaged and A0 are kept and escalated; an invalid or missing journal makes everything A0 | A |
| `H-GR1.2` | FS | Re-verify immediately before removal through a descriptor: open read-only without following (close-on-exec, non-blocking), `fstat` type/`(dev, ino)`/uid/gid/mode/one link/size (≤ 65,536 bytes mechanically enforced; read at most size + 1), full SHA-256, list extended-attribute names (no forbidden name); for a directory: open as directory and list — must be empty | D §4.6.2-R1 G-R1; R8 §5.7 GRR-3; D R3 (e) GP-2 | 8,9,10 | X + volume cap | mismatch ⇒ the object is A1-damaged or A0 now and is kept | A |
| `H-GR1.3` | JR | Append `remove-intent {path, dev, ino, sha256}` to the removing run's own journal and flush (write-ahead) — omitted under grant-priority / GP-R3 when the journal no longer accepts lines | D §4.6.2-R1 G-R1; D R3 (e) | 11 | X | GP-R3: removal proceeds without the line; no removal is claimed | A |
| `H-GR1.4` | FM | Remove the name (`unlinkat`, with directory removal for a directory) in the open parent descriptor | D §4.6.2-R1 G-R1 | 12 | X (tmpfs for activation objects) | `ENOENT` ⇒ absent; any other error ⇒ `grant-unremovable {errno}` (rule) / `unremovable {errno}`; BS-4 retries every R | A |
| `H-GR1.5` | SY | Flush the parent directory (on tmpfs possibly a no-op; result not relied on) | D §4.6.2-R1 G-R1; R2 §7 (g) | 12 | X | — | A |
| `H-GR1.6` | JR | Append `removed {path}` and flush | D §4.6.2-R1 G-R1 | 11 | X | a missing `removed` line only makes a later attempt class the object `absent-before-removal` | A |
| `H-GR1.7` | CN | Stated limit: between re-verification and removal only root can swap a name (T-B, M-10 out of scope) | D §4.6.2-R1 G-R1 | — | — | — | A |

### 4.8 H-GRR — GRR, IGR-0 and the GR-2 rule

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `H-GRR.1` | FD | GRR-1: for a non-holder caller open K from a descriptor of `/run` (directory, no-follow, close-on-exec), then open `grant.id` read-only, no-follow, close-on-exec, non-blocking; the holder uses the identity it holds in memory (same content as `grant.id`) | R8 §5.7 GRR-1 | 6,8 | X | missing/unreadable/unparsable ⇒ `identity-unavailable`; the caller continues with CL-3's journal-based classification | A |
| `H-GRR.2` | FS | Require `grant.id` is a regular file, `root:root`, mode `0600`, at most 4,096 bytes (mechanically enforced), one parseable line `{path, dev, ino, sha256, size, mode, uid, gid, boot_id}` | R8 §5.7 GRR-1; R8 §4.5 GI-1 | 8 | X + volume cap 4,096 | violation ⇒ `identity-unavailable` | A |
| `H-GRR.3` | FS | GRR-2: look up the rule name in the rules-directory descriptor without following a final symlink; `ENOENT` ⇒ `absent` | R8 §5.7 GRR-2 | 10 | X | — | A |
| `H-GRR.4` | FS | GRR-3: descriptor re-verification as G-R1 (regular file with the identity's `(dev, ino)`, uid and gid 0, mode `0644`, one link, size equal and ≤ 65,536; full SHA-256 equals the identity's; extended-attribute names contain no forbidden name) | R8 §5.7 GRR-3 | 8,9,10 | X + volume cap | mismatch ⇒ `kept-damaged` or `kept-foreign`, nothing removed | A |
| `H-GRR.5` | FM | GRR-4: remove the rule name; `ENOENT` ⇒ `absent`; other error ⇒ `unremovable {errno}`; flush the rules directory afterwards, result ignored | R8 §5.7 GRR-4 | 12 | X | GRR never raises; outcome ∈ removed, absent, kept-damaged, kept-foreign, unremovable {errno}, identity-unavailable | A |
| `H-GRR.6` | CN | GRR takes no lock, spawns nothing, sends no signal, calls no authorization, reads no `ext4` object and writes only the one removal; no elapsed time claimed (class X) | R8 §5.7 GRR; R8 §7.5a.1 SN-I-4 | 3d | X | — | A |
| `H-GRR.7` | CN | GR-2: grant removal is the first mutating act of every rung that acts on its own initiative (IGR, CL-G) and precedes every `ext4` write, every spawn and every lock attempt in that rung; CP's CQ-3 keeps its accepted order after the claim | R8 §5.7 GR-2 | — | — | — | A |
| `H-GRR.8` | CN | IGR-0 latch: `igr_state` ∈ idle, running, done; re-entry is impossible by construction (single call site, flag-only handlers, GRR never raises); a restart after a crash is safe because GRR is idempotent | R8 §5.7 IGR-0 | — | — | — | A |

### 4.9 H-DI1 — DI-1 — unit-state read

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `H-DI1.1` | UA | DI-1 unit-state read: obtain the named properties of one named unit (the capture unit `rp11-capture-pass-a.service`, the holder `⟨id⟩.service`, `⟨id⟩-backstop.timer`, `⟨id⟩-backstop.service`) from the service manager, read-only; today a `systemctl show -p …` child created by the process-creation function; the properties used by the root procedures are `ActiveState`, `InvocationID`, `InactiveEnterTimestampMonotonic`, `Job`, `LoadState`, `Result` and, for baselines, the explicit lists of H-BSE | R8 §9.3 DI-1; D R2 (g),(h); D R5 (c),(e); D 4.3.3 | 1,2 | E (c = `pk_call_ms`, 1,000 … 10,000, c ≤ P, rec. 5,000) for the wait; call itself X | at c: result `error` (never a baseline, never "inactive"); a read that cannot be completed is an error and fails closed at its use (stop / `observation-failed` / `consume-failed`) | A;Q3-1;Q4-7 |
| `H-DI1.2` | PR | Take each property value as the exact bytes after the first `=` of the printed form, decoded as strict UTF-8; any decoding failure is a stop; a property the installed manager does not report is a stop (enforced by the tool, because the client does not fail); `ExecStart`/`ExecStartPre` are read from their printed structure (`path`, `argv[]`, flags from the `Ex` form) and run-time fields are dropped | D 4.3.3 (value encoding, ExecStart normalization); R2 §4.1, §4.4 | 8 | X | parse failure is a stop | A;Q6-2 |
| `H-DI1.3` | CN | Reads start, stop or change nothing; reading an unloaded unit may load it into memory (PO-21 (l) precision); a read made by a process during its own unit's start-pre returns without waiting for that job and reports `activating`, the attempt's `InvocationID` and the earlier τ (PO-21 (v)) | R2 §8 (l),(v); D R5 (j) | — | — | — | A;Q3-1 |
| `H-DI1.4` | CN | A satisfied read is never evidence of a unit's absence: `InvocationID` of an `inactive` unit may be stale (the unit may be unloaded and `InactiveEnterTimestampMonotonic` read `0`) | R2 §8 (k),(s); D R5 (g) | — | — | — | A |

### 4.10 H-PROC — DI-6 — the authorization subject and the child handle

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `H-PROC.1` | PC | DI-6 authorization subject: create one subject process per authorization call, in its own session (its process-group and session IDs equal its PID), with the supplementary groups, GID and UID that the H-1 record holds for `ubuntu`, that remains alive for at least the call and for at most 60 s on its own; admissible forms are a fork that continues in a static image or an `execve` of a design-controlled static image, never a distribution program (`/usr/bin/sleep` is today's DI-6) | R8 §7.5 PK/2 Subject; R8 §9.3 DI-6; W1 §11 (BQ-4); R8 §7.5 HS-3 | 1 | X (creation); the subject's life is self-limiting 60 s (row 4) and counted X | spawn failure ⇒ call result `error`; the subject is later signalled by SN-3 (H-SN) and lives at most 60 s if abandoned | A;Q4-1;Q6-4 |
| `H-PROC.2` | CR | In the subject, change credentials by the creation primitive's own arguments (user, group, supplementary groups) and not by code between creation and execution of a separate image; no `preexec`-style hook | R8 §7.5 HS-3 | 1 | X | credential failure ⇒ spawn failure, call `error` | A;Q4-1 |
| `H-PROC.3` | FD | The child inherits no descriptor from the helper (every descriptor ≥ 3 closed before it runs), holds no descriptor of K, and the working directory is `/`; no environment other than the closed map when it runs an image (`{LC_ALL=C, PATH=/usr/bin}` is the dynamic-child map; for a static subject no environment is needed) | R8 §7.5 HS-2, HS-3; R8 §4.5 LD-3 (c); R8 §7.5a.4 SN-8 (e) | 1 | X | a duplicate of K would outlive the owner only inside the creation window (LD-3 (e)) | A;Q4-1 |
| `H-PROC.4` | ID | Capture the child handle at creation: PID, process-group and session ID (both = PID), `start_ticks` (field 22 of `/proc/⟨pid⟩/stat`, optional, PO-SN (d)), `created_ms`, `deadline_ms`, state `running`; verify `getpgid(pid) == getsid(pid) == pid` and that `pid` is not the helper's own group; a failed check marks the handle `identity-unverifiable` from creation | R8 §7.5a.3 CH, SI-1 | 3e | X + volume cap 4,096 for the `/proc` read | no signal is ever sent to an `identity-unverifiable` handle | A;Q3-6 |
| `H-PROC.5` | FS | Obtain the subject's start time and UID for the authorization call (`--process ⟨pid⟩,⟨start-time⟩,⟨uid⟩`): read the child's start time from `/proc` (field 22) and its UID | R8 §7.5 PK/2 Call; D R1 (f) | 8 | X | unreadable ⇒ call `error` | A;Q3-6 |
| `H-PROC.6` | CN | Every child of a root helper is created by the single process-creation function; no raw `fork`; the child count of one PK series is at most 20 at the recommended P (arithmetic on the schedule) | R8 §7.5 HS-1; R8 §4.5 LD-3; R8 §5.6 RO-7 | 1 | — | — | A |

### 4.11 H-PK2 — PK/2 — the authorization series (DI-5)

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `H-PK2.1` | CK | Series start: read the monotonic clock; no call starts after `pk_op_ms` (P, 5,000 … 60,000, rec. 30,000) has elapsed; offsets 0, 250, 500, 1,000, 2,000, 3,000, 4,000 ms then every 2,000 ms on the monotonic clock | R8 §7.5 PK/2 Series; R8 §7.6 | 14 | E (P); scheduled waiting ≤ P + c + g (WB-6, a budget of sleeps, not a return bound) | no call after P ⇒ result `unconfirmed` | A |
| `H-PK2.2` | CN | Modes: seek-authorized stops at the first `authorized`; seek-not-authorized stops at the first `not-authorized`; first-decisive stops at the first of either; an `error` never ends a series (it retries on the schedule) | R8 §7.5 PK/2 Series | 14 | — | — | A |
| `H-PK2.3` | CN | Per call, in order: DI-6 subject (H-PROC.1 … H-PROC.5), DI-5 decision (H-PK2.4), SN-3 send and reap of the subject (H-SN), schedule sleep | R8 §7.5 PK/2; R8 §7.5a.1 SN-I-3 | 1,2,3c,14 | — | — | A |
| `H-PK2.4` | UA | DI-5 Polkit decision: ask the authorization authority, as root and without interaction, for action `org.freedesktop.systemd1.manage-units` with details `unit` = `rp11-capture-pass-a.service` and `verb` = the series verb (`start` or `stop`) for the subject process of H-PROC.5; today `/usr/bin/pkcheck` with that action, `--process ⟨pid⟩,⟨start-time⟩,⟨uid⟩`, `--detail unit …`, `--detail verb …`, no `--allow-user-interaction`, closed environment, deadline c | R8 §7.5 PK/2 Call; D R1 (f); R8 §9.3 DI-5 | 2 | E (c) | at c: `error` ⇒ SN sequence on the child group (today); PK result `unconfirmed` whatever the sends and whatever partial output | A;Q3-5;Q4-7 |
| `H-PK2.5` | PR | Map the decision to one call outcome: today exit 0 ⇒ `authorized`; exit 1 or 2 ⇒ `not-authorized` (2 = challenge); any other status, a creation failure, an unparsable result, the deadline or an abandon ⇒ `error`; output capped at 65,536 bytes, more is `error` | R8 §7.5 PK/2 Outcome; R2 §6.4 (e); R8 §7.3 row 2 | 2,8 | X + volume cap | the exit-status mapping is a command-line contract that does not carry over (R8 §9.3 E-2) | A;Q3-5;Q6-1 |
| `H-PK2.6` | CN | Series result: `authorized`, `not-authorized` or `unconfirmed` with reason `only-errors`, `still-authorized`, `not-seen` or `interrupted`; the flag (SG-4) ends the series at the next wake-up with `interrupted`; PK starts, stops or changes nothing | R8 §7.5 PK/2 Result | 14 | — | `unconfirmed` fails closed at every use (R8 §7.11) | A |
| `H-PK2.7` | CN | A subject is signalled once, by SN-3 `SIGKILL` of its group after the call; the call's decision (already given by the authorization result) is unaffected by that send; a failed, unmade or unreaped subject is abandoned or `reap-unknown`, recorded, and lives at most 60 s | R8 §7.5a.1 SN-I-3; R8 §7.5a.4 SN-7, SN-8 | 3c,4 | X, C (one attempt) | see H-SN | A |

### 4.12 H-SN — SN — the signal-sending, validation, reap and wait contract

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `H-SN.1` | CN | Applicability: for the LIT-FULL replacement SN-1 … SN-10 and SI-1 … SI-4 apply unchanged to every child a root image controls; the only child-creation intent that the LIT-FULL classification retains is the DI-6 authorization subject (PC-1, §8); the DI-1 … DI-5 and stop-unit children of today's accepted behavior are removed from the replacement (PC-2 … PC-7, §8.1) and are not H-SN children of it; should a later package admit any other child it must be (F) or (X) under BQ-4 and H-SN then applies to it, which WP-2 neither selects nor maps; PO-SN (c) is replaced by the replacement's own `clone`/`setsid`/`wait4` behaviour (WP-3/4) | R8 §7.5a.8 (last paragraph); W1 §11; §8.1 of this document | 3a-3g | — | — | A;Q4-8 |
| `H-SN.2` | CK | S0 (only for a handle in state `running` at SN's entry): read `t_g = clock() + g` once, before any validation or send, with g = `reap_grace_ms` (500 … 5,000, rec. 2,000); sets `s0_ran` and `grace_deadline_ms`; nothing later reads, moves, extends or restarts it; a settled handle goes from SN's entry to S1-a without S0 and without a clock read | R8 §7.5a.6 S0; WB-1; GD-1 … GD-6 | 3 | E (g) as a budget of scheduled sleeping | `t_g` exists exactly when S0 has ever run for the child; a pre-S0 `reap-error` creates none | A |
| `H-SN.3` | ID | S1 validation (SN-4), per send, on the main thread, with the child unreaped: (i) `state == running`; (ii) `pid > 1`, `pgid == pid`, `pgid` not the helper's own group; (iii) `getpgid(pid) == pgid` and `getsid(pid) == pgid`; (iv) only if PO-SN (d) is accepted, start time read from `/proc/⟨pid⟩/stat` (parsed after the last `)`, read capped at 4,096 bytes) equals `start_ticks` | R8 §7.5a.4 SN-4; §7.3 row 3e | 3e | X + volume cap 4,096 | (ii)/(iii)/(iv) fail ⇒ `not-sent(identity-mismatch)`; unreadable/unparsable ⇒ `not-sent(identity-unverifiable)`; either ⇒ S1-b (no send, go to S5); validation is a detector only (SI-2, SI-5), never a reuse defence | A |
| `H-SN.4` | CN | S1-a: a settled handle (`reaped`, `abandoned`, `reap-unknown`) ⇒ `not-sent(reaped)` / `not-sent(abandoned)` / `not-sent(reap-unknown)`: no call, no wait, no validation, no clock read; go to S7; no `not-sent` result is ever followed by a send | R8 §7.5a.6 S1-a, S7; SN-4; SI-4; INV-25 | 3e | — | sequence ends at S7 | A |
| `H-SN.5` | SG | S2: send `SIGTERM` to the child's process group (SN-I-1), one attempt, no retry; skipped for a PK subject; record the result and whether it returned at or after `t_g` (`late`) | R8 §7.5a.1 SN-I-1; SN-1, SN-3; §7.3 row 3a | 3a | X (call), C (one attempt); no elapsed time claimed | results per table SN-R rows 1 … 6; none is evidence; a send returning at or after `t_g` skips every later timed wait (WB-3) | A;Q4-8 |
| `H-SN.6` | PL | S3: one non-blocking reap attempt (`reap_step()`, class X, never a wait, no timeout argument, no retry inside itself) — phases RA-0 (before the call), RA-1 (inside the call before the kernel reap), RA-2 (after the kernel reap, handle still `running`), RA-3 (handle state updated, line not durable), RA-4 (line durable), RA-E (the attempt raised): the kernel reaps only inside this attempt | R8 §7.5a.6 S3; §7.5a.6c RB-1 … RB-4; §7.3 row 3g | 3g | X | reaped ⇒ stop at S7, no `SIGKILL`; raised ⇒ S8 (no `SIGKILL`, no sleep) | A;Q4-8 |
| `H-SN.7` | SL | S3 (cont.): if S2 returned `sent` or `esrch` and `now < t_g`: one sleep of `min(slice_ms, t_g − now)`, then one more reap attempt; no timed wait after a failed or unmade `SIGTERM` or when `now ≥ t_g` | R8 §7.5a.6 S3; WB-2, WB-3 | 3 | E (g budget) | — | A |
| `H-SN.8` | SG | S4 (at most once, not a wait, not skipped): the child is unreaped after a normal return of S3's last attempt (for a PK subject no attempt yet): validate again (S1 branches) and send `SIGKILL` (SN-I-2, or SN-I-3 for the subject), one attempt; record result and `late`; it may follow `t_g` and is then recorded `late`, never presented as completion within g | R8 §7.5a.6 S4; WB-4; SN-I-2, SN-I-3; §7.3 rows 3b, 3c | 3b,3c | X (call), C (one attempt) | a validation verdict `not-sent(identity-*)` sends nothing and goes to S5; after a `reap-error` S4 is never reached (RE-1) | A;Q4-8 |
| `H-SN.9` | PL | S5: loop: read clock; one reap attempt; reaped ⇒ S7; if the attempt began at or after `t_g` it is the final attempt ⇒ S6; otherwise sleep `min(slice_ms, t_g − now)` only while `now < t_g`, repeat | R8 §7.5a.6 S5; WB-5 | 3,3g | E (g), X | raised ⇒ S8 | A |
| `H-SN.10` | XT | S6: the final attempt returned normally and found the child unreaped ⇒ abandon (SN-8): state `abandoned`; stop waiting; never signal again; keep the `Popen`-equivalent handle referenced for the helper's life; record `abandoned: true`, `sends`, `last_signal`, `anomalies`; the child holds no descriptor of K; the operation continues fail-closed; no recovery on the child | R8 §7.5a.6 S6; SN-8; SI-4 | 3 | — | the abandoned child is never presumed gone or signalled again | A;Q4-8 |
| `H-SN.11` | JR | S7 settle, record, return: write the `child` line once, best effort, never retried; return the enclosing operation's own fail-closed result (`error`, `interrupted` for a flag, PK `unconfirmed`) whatever the send results and whatever partial output arrived; S7 makes no send, wait, clock read or reap attempt; entries made before the journal exists are held in memory (≤ 64 entries, ≤ 64 KiB, `overflow` counter) and flushed in order | R8 §7.5a.6 S7; §7.5a.9; SN-7 | 11 | X | a failed or stalled append changes no result and is recorded as a gap | A |
| `H-SN.12` | CN | S8 suppress after a `reap-error` (from S3, S5 including the final attempt, or a poll of the enclosing wait): set `reap-unknown`; record anomaly `reap-error`, `send_suppressed: true`, and `effect: "unknown"` for a mutating child; send nothing (S4's `SIGKILL` included), no further attempt or sleep, no clock or `t_g` read, no search; keep the handle; go to S7 | R8 §7.5a.6 S8; RE-1 … RE-6; §7.5a.6e | 3g | — | either truth about the direct child is safe because nothing is sent | A |
| `H-SN.13` | CN | Record per child (`children[]`): role, argv0, pid, pgid, start_ticks, deadline_ms, `s0_ran`, `grace_deadline_ms` (integer iff `s0_ran`, else `null`, never omitted), outcome (exited/expired/interrupted/spawn-failed/reap-error — last only when `s0_ran` false), sends [signal, result, offset_ms, late], waits_skipped, reaped, abandoned, reap_unknown, send_suppressed, last_signal, effect, anomalies; at most 64 entries; schema check `s0_ran == (grace_deadline_ms != null)` with its implications | R8 §8.5 `children`; §7.5a.6e GD-2 | 11 | X | a lost record is the recorded condition `children-unknown {helper_role, missing_terminal_line}` derived from a missing terminal journal line, never from a process search | A |
| `H-SN.14` | CN | A send is SN only: the closed set {`SIGTERM`, `SIGKILL`}, never by number alone, never from a handler / IGR / GRR / CL-G, no other primitive (`kill`, `pkill`, `pidfd_send_signal`, a spawned `kill`), at most one send per child and signal; no retry on `EINTR` or any error; no later procedure scans for, signals, reaps or acts on a left-behind child | R8 §7.5a.4 SN-1, SN-2, SN-3, SN-5, SN-9; §7.5a.1 SN-I-4 | 3d | C | nothing hunts (LD-9, SN-9) | A |
| `H-SN.15` | CN | Result table SN-R rows 1 … 12 (sent; `ESRCH`; handle reaped; `EPERM`; other errno; non-`OSError` exception; identity-mismatch; identity-unverifiable; settled; late return; helper ended in or after the call; reap attempt raised) — no row yields a pass, a confirmation or a concealment; each is recorded except row 11 | R8 §7.5a.5 | 3a-3g | — | see table SN-R in §9 of this document | A |
| `H-SN.16` | CN | Sole-reaper invariant (SI-3, load-bearing): exactly one function reaps; no thread, no `SIGCHLD` set to ignore / no-wait, no foreign `wait*`, no destructor reaping outside it; SI-5: once violated the design makes no reuse-safety claim from validation alone | R8 §7.5a.3 SI-2, SI-3, SI-5; SG-3 | 3g | — | — | A;Q4-8 |

### 4.13 H-BSE — Baseline recomputation (H-2 code; AV-1 H-2b; CL-6)

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `H-BSE.1` | FS | Baseline recomputation (H-2 code; used by AV-1 as H-2b and by CL-6): host — nodename, `machine_id_sha256` (hash of `/etc/machine-id`), architecture `x86_64`, kernel release; today obtained by `uname -n` / `sha256sum` class commands in H-0, mechanism in the tool not stated | D 4.3.2 `baseline.host`; D 4.3.4 | 9,10 | X | a difference ⇒ stop (baseline mismatch) | A;Q3-11;Q6-3 |
| `H-BSE.2` | FS | operator — user `ubuntu`, uid, gid, supplementary groups as `[name, gid]` sorted by gid; `repository_root` `/opt/freedom-blades/platform` with owner, group, mode; today `id ubuntu` / `getent` class in H-0; acquisition inside the tool not stated | D 4.3.2 `baseline.operator`; D 4.4.1 HF-03 | 9,10 | X | a changed UID/GID/groups ⇒ stop and return to Peter (never substitute an account) | A;Q3-11;Q6-3 |
| `H-BSE.3` | FS | repository — commit, manifest version, reviewed digest, `expected_sha256_file_sha256`, `manifest_json_sha256`; acquisition of the commit identity inside the tool not stated | D 4.3.2 `baseline.repository` | 8,9 | X | mismatch ⇒ stop | A;Q3-11;Q6-3 |
| `H-BSE.4` | FS | packages — the sorted list `[package, version, architecture]` for the fixed HF-07 set (systemd, systemd-sysv, libsystemd0, libsystemd-shared, polkitd, libpolkit-gobject-1-0, libc6, libc-bin, python3.12 family, coreutils, util-linux, sudo, dbus, plus the owner of `/usr/bin/pkcheck`); H-0 used `dpkg-query`; the tool's mechanism is not stated; a package-version drift is detected here (H-1R path, outside the set) | D 4.3.2 `baseline.packages`; D 4.4.1 HF-07; D 4.6.3 | 9 | X | mismatch ⇒ stop (package-version drift) | A;Q3-11;Q6-3 |
| `H-BSE.5` | HS | citations — for each of D9-1, PO-8, PO-11, PO-12, PO-14, PO-15, PO-19, PO-20, PO-21: record path, SHA-256 of the record and `cited_version`; read and hash the cited repository records | D 4.3.2 `baseline.citations`; D R2 (note) | 8,9 | X + volume cap | mismatch ⇒ stop | A |
| `H-BSE.6` | FS | launcher — path, SHA-256, size, owner, group, mode, set-ID false, file capability false, ACL false, `(dev, ino)`, parents, plus the carried record facts (toolchain lock digest, build-root manifest digest, builds, `ha_variation`, `ic1_record_sha256`, `t_l10`/`t_l11`/`t_l12`, `xd_*`, agreed stream, `interpreter_version`, `d9_2`, `installation_source_record_sha256`); which sub-keys are re-read and which are carried is not stated | D 4.3.2 `baseline.launcher`; D 4.3.4 | 8,9,10 | X | mismatch ⇒ stop | A;Q3-11;Q6-2 |
| `H-BSE.7` | FS | files — for the bootstrap, the unit, the staged rule and the installed tool (and each installed root-procedure image under the Route 3 outcome): `lstat` role, path, SHA-256, size, owner, group, mode, `(dev, ino)`, set-ID, file capability, ACL via extended-attribute names only | D 4.3.2 `files`; D R2 (note); R8 §8.5 `helper` | 8,9,10 | X + volume cap per file | mismatch ⇒ stop | A |
| `H-BSE.8` | FS | directories — every §4.2.3 directory and every parent to `/`: path, owner, group, mode, ACL via names, `created_by_run`, `dev`, `ino` | D 4.3.2 `directories`; D 4.2.3 | 10 | X | mismatch ⇒ stop | A |
| `H-BSE.9` | FS | absent — the listed paths must give "absent": `/run/freedom-blades-rp11/pass-a.json`, `/run/polkit-1/rules.d/50-freedom-blades-rp11.rules`, `/etc/freedom-blades-rp11` and the rule basename in every other rules directory PO-11 (f) lists | D 4.3.2 `absent`; D R2 (note) | 10 | X | a present object ⇒ stop | A |
| `H-BSE.10` | UA | unit — read the capture unit with an explicit property list taken from the version-bound data file `infra/rp11-unit-properties.⟨systemd version⟩.txt` (never `--all`; volatile set V and environment-bearing set E not compared/never queried; `ActiveState`/`SubState` checked separately), `ExecStart` and `ExecStartPre` normalized (path, argv, flags; the `+` flag read from the `Ex` form) | D 4.3.3 (a); R2 §4.2, §4.4 | 1,8 | E (c) | a property the manager does not report ⇒ stop | A;Q3-9;Q6-2 |
| `H-BSE.11` | UA | manager — read the manager object with an explicit list: every `Default*`, `Version`, `Features`, `Architecture`, `UnitPath`, `ConfirmSpawn`, `ServiceWatchdogs`; no name containing `Environment` is ever read | D 4.3.3 (b); R2 Appendix B | 1,8 | E (c) | — | A;Q3-9 |
| `H-BSE.12` | FS | po17 — read `/proc/self/mountinfo` for a `binfmt_misc` mount; if mounted read `status` (exactly `enabled\n`/`disabled\n`), list the directory excluding `register` and `status`, sort bytewise, read and parse each entry (grammar: first line enabled/disabled, `interpreter`, `flags:`, `offset`/`magic`/optional `mask` or `extension`), match each entry against the image bytes (read once) by the §4.3.6 algorithm; unmounted ⇒ treated as a stop | D 4.3.6; D 4.3.2 `po17`; R2 §12 | 8,10 | X | any line outside the grammar is a stop | A |
| `H-BSE.13` | FS | po18 — machine `x86_64`, kernel release compared numerically on the dotted prefix against 5.9 | D 4.3.2 `baseline.po18` | 10 | X | — | A |
| `H-BSE.14` | HS | Serialize the baseline as `canonical_bytes`, hash it, and require equality with the `baseline_sha256` of the H-1 record (read the record from the record store and verify its own digest); report the first differing key path on a stop | D 4.3.4; D R1 (d) AP-0/AV-1 | 9 | X + volume cap | inequality ⇒ stop (INVALID RUN at AP-0; HARD STOP in AV-1; CL-6 not-verified) | A;Q6-2 |
| `H-BSE.15` | CN | CL-6's recomputation is the largest local job in CL and runs last before the records; an interruption in it costs only verification; no elapsed time is stated | R8 §7.3 row 9; R8 §7.9 L7 | 9 | X | — | A |

### 4.14 H-REC — Records (`rp11-activation-record/2`)

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `H-REC.1` | JR | Assemble the activation record `rp11-activation-record/2` as `canonical_bytes` with the closed keys: schema, kind, activation_id, attempt, trigger, authority, authority_limit (fixed OH-D-6 sentence), h1_record, h2_record_sha256, boot {pinned, act_boot, observed_at_start, observed_at_end, run_fstype}, pass_config, staged_rule, active_rule, grant_check, unit, lease, holder, consume, directories, lock, grant_identity, pk, children, release, capture, helper, params {…, sizing "necessary-conditions-met"}, st1, journals [{path, sha256, length}], act_record_sha256, outcome, failure, residual, evidence_mode, time; no extra key, no value outside its grammar, no environment content, no content of any object | D R1 (g); D R2 (m); D R3 (h); D R4/R5 (m),(j); R8 §8.5 | 8,9,11 | X | a record that cannot be published at CL-7 is `record-unpublished`; removals stay durable in the journal | A;Q6-2 |
| `H-REC.2` | CN | Closed enumerations the record admits: rule classes (removed-verified, removed-unconfirmed, never-linked, removed-earlier, absent-before-removal, present-damaged-unremoved, present-foreign-unremoved, cleared-by-boot, grant-unremovable); pass_config classes; directory classes (removed, never-created, removed-earlier, absent-before-removal, cleared-by-boot, pre-existing-kept, present-nonempty-unremoved, present-damaged-unremoved, present-foreign-unremoved, unremovable); failure classes (lock-object, capture-baseline-unstable, grant-not-seen, stop-control-unconfirmed, act-unconfirmed, invalid-journal, record-unpublished, evidence-unwritable, observation-failed, unit-still-active, …); recorded conditions (identity-conflict, child-abandoned, signal-send-failed, signal-not-sent, children-unknown) | D R1 (e),(g); D R2 (h); D R3 (h); R8 §8.5 | — | — | — | A |
| `H-REC.3` | FS | Publish the record by protocol PF into `/var/lib/freedom-blades-rp11/activation/` as `⟨activation_id⟩.act.json` (written once) or `⟨activation_id⟩.deact-⟨k⟩.json` (`root:root`, `0444`); re-read the published record; records are never deleted by any procedure; report the SHA-256 and byte length (including the final LF) | D R1 (g); D R2 (m) | 11 | X | see CL-7 | A |
| `H-REC.4` | FS | Hash each journal the record cites, in full (the writing attempt's own journal as its prefix up to the line before its record's `file-intent`), for the `journals` list `{path, sha256, length}` | D R1 (g); D R2 (m) | 8,9 | X + volume cap | — | A |

### 4.15 H-DIAG — Diagnostic output

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `H-DIAG.1` | DG | Write one fixed diagnostic line without values to standard error (the system journal) naming the stable code (`consume-unidentified`, `consume-busy`, `consume-repeated`, `consume-claim-failed`, `consume-evidence-unwritable`, `consume-failed {step, class}`, `consume-precondition`, `rp11-cl grant-priority ⟨activation_id⟩ rule=⟨class⟩ pk=⟨status⟩ pass_config=⟨class⟩ dirs=⟨class,…⟩`); diagnostic only, never evidence | D R4 (c); D R5 (e); D R3 (e) GP-7 | 11 | X | a failed write is not an accepted case | A;Q4-11 |

### 4.16 H-CL — CL — cleanup (all triggers) and GP-R3

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `H-CL.G.1` | CN | CL-G, the first act of every trigger: run GRR with the identity of `grant.id` (H-GRR.1 … H-GRR.5) before CL-0's lock attempts, attempt directory and journal; the outcome (`removed`, `absent`, `kept-damaged`, `kept-foreign`, `unremovable {errno}`, `identity-unavailable`) is held in memory and written as a `cl-g {outcome}` line once the attempt journal exists | R8 §5.7 CL-G; R8 §8.1 CL deltas; GR-2 | 12 | X | `identity-unavailable` ⇒ CL-3 performs the accepted journal-based removal (G-R1 with write-ahead, or its grant-priority form) | A |
| `H-CL.G.2` | CN | CL-3's use of CL-G: `removed` ⇒ `removed-earlier` (in-process); `absent` ⇒ by the journal as accepted; `kept-*` and `unremovable` ⇒ as accepted; the class still needs CL-4's own *not authorized* for `st1-verified` | R8 §5.7 CL-G (last paragraph); R8 §8.1 CL-3 | — | — | — | A |
| `H-CL.0.1` | LK | CL-0: open K and attempt the lock without blocking, repeatedly, until the λ deadline (H-LK.1, H-LK.2); `lock-timeout` as an outcome that acts on nothing is withdrawn | R8 §4.5 LD-5, LD-6; R8 §8.1 CL-0 | 6 | E (λ); CL's elapsed time unclaimed | at λ, or K unopenable: degraded mode — record `lock_mode: "degraded"` / `"absent"` and perform CL-1 … CL-7 unordered with respect to CP | A |
| `H-CL.0.2` | SL | CL-0: sleep between lock attempts (capped by the remaining λ; the accepted text of CL-0 states one second between attempts in D R2 (h), R8 caps every sleep by its own deadline) | D R2 (h) CL-0; R8 §7.5a.6a WB-2, CC-10 | 6,7 | E (λ) | — | A |
| `H-CL.0.3` | FS | CL-0: list `/var/tmp` by prefix `⟨activation_id⟩-deact-` to count existing attempt directories; `k` = 1 + that count, 1 … 99 | D R2 (h) CL-0; D R1 (e) CL-0 | 10 | X | k beyond 99 ⇒ BS-4 disarms, no record | A |
| `H-CL.0.4` | FM | CL-0: create the attempt directory `/var/tmp/⟨activation_id⟩-deact-⟨k⟩-evidence/` exclusively as root, mode `0755` | D R2 (h) CL-0; D R2 (b) | 11 | X | `EEXIST` ⇒ `concurrent-deact`, act on nothing; cannot create ⇒ GP-R3 (E-a) | A |
| `H-CL.0.5` | JR | CL-0: create the attempt `journal` (H-JRN.2, H-JRN.3) and append `run-start {trigger, boot_id, holder_state, lock {object, mode, wait_ms}, helper}`; for `stop-post` and `backstop` also record the parent PID and INVOCATION_ID as provenance (diagnostic only) | D R2 (h) CL-0; R8 §4.9; R8 §8.5 | 11 | X | cannot create / append ⇒ GP-R3 (E-a, E-b) | A |
| `H-CL.0.6` | JR | CL-0: once the journal exists write the held `cl-g` line | R8 §5.7 CL-G | 11 | X | — | A |
| `H-CL.1.1` | FS | CL-1: list and read the ACT journal, every earlier attempt's journal and the consume journal (if it exists) and parse them (H-JRN.8, H-JRN.9) | D R1 (e) CL-1; D R2 (h) CL-1; D R4 (g) CL-1 | 8,10 | X + volume cap | ACT journal missing or invalid ⇒ every object at an activation path is A0 for removal | A |
| `H-CL.1.2` | FS | CL-1: read the A-2 pins and the H-1 record (digest-checked) needed for classification and the record's `h1_record`/`authority`/`lease` fields | D R1 (e) CL-1 | 8,9 | X + volume cap | — | A;Q4-6 |
| `H-CL.1.3` | CN | CL-1 boot scoping: an identity line for an object under `/run` is valid only in the boot recorded by the ACT journal's `run-start`; in any other boot every object found under `/run` is A0 | D R2 (h) CL-1 | — | X | — | A |
| `H-CL.2.1` | UA | CL-2: DI-1 read of the capture unit `ActiveState` and `InactiveEnterTimestampMonotonic`; CL never issues start, stop or kill | D R1 (e) CL-2; D R5 (g) CL-2 | 1 | E (c) today | if the unit is `active`, `activating`, `deactivating` or `reloading` CL continues with grant removal and its outcome cannot be better than HARD STOP `unit-still-active` | A;Q3-1;Q4-7 |
| `H-CL.2.2` | CN | CL classifies the attempt for the `consume` key: `none` (no claim, τ = τ₀, hold-end reason not start-before-hold/start-failed-before-exec); `unidentified` (no claim and τ ∉ {τ₀, 0}, or hold-end is start-failed-before-exec/start-before-hold); `indeterminate` (no claim, τ = 0 ≠ τ₀); `claimed` (claim exists; outcome consumed / failed {step, class} / incomplete / unjournaled) | D R5 (g) | 8,10 | X | — | A |
| `H-CL.3.1` | FS | CL-3: classify the object at the active rule path against the ACT journal's `file-identity` line for the rule (H-GR1.1); a CP journal `removed` line, an `igr` line with outcome `removed`, or a `cl-g {removed}` result ⇒ `removed-earlier`; absent with none of these ⇒ `absent-before-removal`; absent with no identity line ⇒ `never-linked`; another boot ⇒ `cleared-by-boot` | D R1 (e) CL-3; D R2 (h) CL-3; D R4 (g); R8 §8.1 CL-3 | 8,10 | X | A1-damaged or A0 ⇒ not removed | A |
| `H-CL.3.2` | FM | CL-3: if A1-intact remove it by G-R1 with write-ahead in this attempt's journal (H-GR1.2 … H-GR1.6); the removal does not require the lock (GR-1) | D R1 (e) CL-3; R8 §4.5 LD-6 | 8,9,10,11,12 | X | `unlinkat` failure ⇒ `grant-unremovable {errno}`; BS-4 retries every R | A |
| `H-CL.4.1` | FS | CL-4: the rule path must give `ENOENT` | D R1 (e) CL-4 | 10 | X | — | A |
| `H-CL.4.2` | UA | CL-4: PK/2 seek-not-authorized for verb `start`, budget P (H-PK2.1 … H-PK2.7); classes `removed-verified` (durable `removed`, `ENOENT` and a *not authorized* from the procedure that returned *authorized* in this activation), `removed-unconfirmed`, `never-linked`, `removed-earlier`, `absent-before-removal`, `present-damaged-unremoved`, `present-foreign-unremoved` | D R1 (e) CL-4; R8 §7.11; R8 §8.1 CL deltas | 2,3,3a-3g,14 | E (P); scheduled waiting ≤ P + c + g | `unconfirmed` ⇒ class `removed-unconfirmed`; outcome HARD STOP; the backstop retries within `backstop_max` | A;Q3-5;Q3-6;Q4-1 |
| `H-CL.5.1` | FS | CL-5: classify `pass-a.json` at `/run/freedom-blades-rp11/pass-a.json` against its identity line and A-2's digest (H-GR1.1); classes removed, never-linked, removed-earlier, absent-before-removal, cleared-by-boot, present-damaged-unremoved, present-foreign-unremoved, unremovable | D R1 (e) CL-5; D R2 (h) CL-5 | 8,9,10 | X + volume cap | always attempted, even when CL-3 could not remove the rule | A |
| `H-CL.5.2` | FM | CL-5: if A1-intact remove it by G-R1 with write-ahead (H-GR1.2 … H-GR1.6) | D R1 (e) CL-5; D R2 (h) | 8,9,10,11,12 | X | `unlinkat` failure ⇒ `unremovable {errno}` | A |
| `H-CL.5b.1` | FM | CL-5b: remove tree P's top, then any tree R directory that ACT created, each by G-R1 only if A1-intact against the ACT journal and empty (descriptor open as directory, listing empty); never remove a pre-existing `/run/polkit-1/rules.d`; run-unique temporary names under `/run` (S0) are reported and kept | D R2 (h) CL-5b; D R3 (e) GP-5 | 8,10,11,12 | X | `ENOTEMPTY`, mismatch or other error: kept, with its class | A |
| `H-CL.5b.2` | FM | CL-5b (last among the `/run` objects): remove `K/grant.id` and then K through a descriptor re-verification against the journaled identity and only if K holds nothing else; a K without an identity line is S0 | R8 §8.1 CL-5b Δ2; R8 §4.5 LD-1 | 8,10,12 | X | — | A |
| `H-CL.6.1` | FS | CL-6: verify ST-1: the rule, `pass-a.json` and tree P's top absent; `/run/polkit-1/rules.d` present with its AP-0 identity if it pre-existed, absent if ACT created it; `/etc/freedom-blades-rp11` and the rule basename absent everywhere they were at AP-0 | D R2 (h) CL-6 | 10 | X | any difference ⇒ ST-1 not verified (HARD STOP ST-1+R) | A |
| `H-CL.6.2` | HS | CL-6: recompute the baseline (H-BSE.1 … H-BSE.14) and require it to equal the H-1 record's `baseline_sha256`; this is the largest local job in CL and runs last before the records | D R2 (h) CL-6; R8 §7.3 row 9; R8 §8.1 CL-6 | 9 | X | an interruption here costs only verification (L7) | A;Q6-2 |
| `H-CL.6.3` | UA | CL-6: DI-1 read of the capture unit — not active (`inactive` or `failed`) | D R2 (h) CL-6; R8 §8.1 CL-6 | 1 | E (c) today | active ⇒ HARD STOP `unit-still-active` | A;Q3-1;Q4-7 |
| `H-CL.6.4` | CN | CL-6 uses CL-4's PK result and does not run PK itself | R8 §8.1 CL-6 | — | — | — | A |
| `H-CL.7.1` | JR | CL-7: if no `act` record exists, first publish `⟨activation_id⟩.act.json` with outcome `failed` (a later attempt never writes a second `act` record); then publish `⟨activation_id⟩.deact-⟨k⟩.json` (H-REC.1, H-REC.3, H-REC.4); re-read both | D R2 (h) CL-7; D R1 (e) | 8,9,11 | X | cannot be published ⇒ HARD STOP `record-unpublished`; removals remain durable in the journal; the next attempt records | A |
| `H-CL.7.2` | JR | CL-7: append `run-end`, flush, then close K; `st1-verified` additionally requires `lock_mode` recorded | D R1 (e); R8 §8.1 CL-7 | 6,11 | X | — | A |
| `H-CL.OUT` | CN | Outcome: `st1-verified` iff the rule's class ∈ {removed-verified, never-linked, removed-earlier, absent-before-removal with PK *not authorized*, cleared-by-boot}, `pass-a.json`'s class ∈ {removed, never-linked, removed-earlier, absent-before-removal, cleared-by-boot}, directories' classes ∈ the first six, CL-6 holds and the unit is not active; every other combination is HARD STOP (ST-1+R) with the residual list | D R1 (e) Outcome; D R2 (h) Outcome; D R3 (h) | — | — | — | A |
| `H-CL.GP.1` | FS | GP-R3 entry on E-a (attempt directory or journal cannot be created), E-b (a journal append or flush fails before the rule's removal is durable) or E-c (a journal append or flush fails after that, up to CL-6); GP-1: read the ACT and earlier journals only (apply boot scoping); a missing or invalid ACT journal makes every object A0 and nothing is removed | D R3 (e) Entry, GP-1 | 8,10 | X | HARD STOP; nothing removed | A |
| `H-CL.GP.2` | FM | GP-2/GP-3: remove the A1-intact rule after a descriptor re-verification immediately before removal (write-ahead line only if the journal still accepts it); then the grant post-check (CL-4) held in memory | D R3 (e) GP-2, GP-3 | 8,9,10,12,2,14 | X; E (P) for the check | `unlinkat` error ⇒ `grant-unremovable`; mismatch ⇒ kept | A |
| `H-CL.GP.3` | FM | GP-4/GP-5: always after GP-3, remove `pass-a.json` and then the directories (tree P's top, tree R directories ACT created, bottom-up), each A1-intact, re-verified through a descriptor immediately before removal, directories empty | D R3 (e) GP-4, GP-5 | 8,10,12 | X | errors: `unremovable`, `present-nonempty-unremoved`, kept with class | A |
| `H-CL.GP.4` | FS | GP-6: CL-6 read-only verification; GP-7: write the one fixed diagnostic line to standard error (H-DIAG.1) and exit non-zero; no record is written, nothing durable is claimed, no attempt number `k` is consumed | D R3 (e) GP-6, GP-7 | 10,11 | X | outcome HARD STOP `evidence-unwritable`; the host is in ST-1.ur | A |
| `H-CL.GP.5` | CN | A later journaled attempt classes an object GP-R3 removed `absent-before-removal` (or `cleared-by-boot` in a later boot), obtains its own PK *not authorized* and CL-6 before recording `st1-verified`, and never records `removed`, `removed-verified` or `removed-earlier` for it | D R3 (e) What can and cannot be claimed | — | — | — | A |

## 5. Per-procedure operation tables

### 5.1 RT-1 — consume (CP: CQ-0 … CQ-7)

Caller: PID 1, the capture unit's `ExecStartPre=+` step, inside that unit's start job, after Polkit authorized the operator's `start` and before PID 1 may execute `ExecStart=`. Beginning boundary: the first design-controlled static image that PID 1 executes (no `sudo`, no dynamic program before it); nothing from the requester reaches it (PO-21 (n)). Accepted failure contract: every exit other than CQ-7's exit 0 is non-zero and leaves `ExecStart=` unexecuted (PO-21 (o)); a CP failure is a failed start, not a pass; no `consumed` line means no pass; stable codes consume-unidentified / consume-busy / consume-repeated / consume-claim-failed / consume-evidence-unwritable / consume-precondition / consume-failed {step, class}; SB-1, SB-2, SB-3 refuse every later attempt (contract OSA over 𝒜, no exception within 𝒜; CX-4 outside 𝒜)

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `RT1.FI.1` | EN | Instantiate H-FI for `consume`: the first image is the one PID 1 executes as `ExecStartPre=+` of the capture unit, as root, with no operand and nothing from the requester; it reads INVOCATION_ID (its own, equal to the `ExecStart=` process of the same start, AR-6) and no other variable | D R4 (c); R2 §8 (n); R8 §9.6.1; H-FI.1 … H-FI.7 | — | X | see H-FI | A;Q4-6 |
| `RT1.FI.2` | CN | CP installs no signal handler (SG-8): the default action on `SIGTERM` ends it; its interruption is mapped (IM-C), not handled; CP's start timeout T_s (the capture unit's loaded `TimeoutStartUSec`, finite, and required to satisfy N1, a necessary condition only) is PID 1's class-M terminator | R8 §7.8 SG-8; R8 §7.4; R8 §7.6 N1 | 20 | M (T_s) | the attempt ends `failed`; `ExecStart=` is never executed; SB-2 refuses every later attempt | A |
| `RT1.CQ0.1` | FD | CQ-0: open `/run/freedom-blades-rp11` for reading as a directory without following a final symbolic link (pfd) | D R5 (e) CQ-0 | 8 | X | `consume-unidentified`, exit, nothing created (unidentified attempt) | A |
| `RT1.CQ0.2` | FD | CQ-0: open `pass-a.json` relative to pfd, read-only, without following, non-blocking | D R5 (e) CQ-0 | 8 | X | as RT1.CQ0.1 | A |
| `RT1.CQ0.3` | FS | CQ-0: `fstat` it: regular file, uid and gid 0, mode `0644`, one link, size at most 65,536 bytes | D R5 (e) CQ-0 | 10 | X + volume cap 65,536 | as RT1.CQ0.1 | A |
| `RT1.CQ0.4` | FS | CQ-0: read the file (at most 65,536 bytes) | D R5 (e) CQ-0; R8 §7.3 row 8 | 8 | X + volume cap | oversize/unreadable ⇒ `consume-unidentified` | A |
| `RT1.CQ0.5` | PR | CQ-0: parse only `activation_id` and match `^rp11-act-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}$`; nothing else is decided yet | D R5 (e) CQ-0; D R1 (a) | 8 | X | no match ⇒ `consume-unidentified` | A;Q4-5 |
| `RT1.CQ0.6` | DG | On any CQ-0 failure write the fixed diagnostic line (H-DIAG.1) and exit; nothing is created | D R5 (e) CQ-0; D R4 (c) | 11 | X | — | A |
| `RT1.CQ1.1` | FD | CQ-1: open K = `/run/freedom-blades-rp11-lock-⟨activation_id⟩/` (derived from the `activation_id` of CQ-0) with the K discipline (H-LK.1) | R8 §8.1 Machine C CQ-1 Δ; D R5 (e) CQ-1 (the earlier `/var/tmp` ACT-directory form is replaced by K) | 6 | X | K absent or unopenable ⇒ `consume-unidentified`; nothing created | A |
| `RT1.CQ1.2` | LK | CQ-1: one non-blocking exclusive lock on K, no wait (H-LK.2) | D R5 (e) CQ-1 (AR-1); R8 §8.1 | 6 | X | `EWOULDBLOCK` ⇒ `consume-busy`, exit, nothing created; cleanup or another CP holds the lock | A |
| `RT1.CQ2.1` | FD | CQ-2: open `/var/tmp` as a directory without following a final symlink (vfd); `fstat` must show a directory, `root:root`, mode `1777` | D R5 (d) Publication | 8,10 | X | wrong type/mode ⇒ no claim: CQ-3 in grant-priority form, exit `consume-claim-failed` (pre-barrier class) | A |
| `RT1.CQ2.2` | FM | CQ-2 blocking point: create `⟨activation_id⟩-consume-evidence` in vfd as a directory, mode `0700`, no replace, never following a final symlink; `0` is the barrier for every later attempt in this boot | D R5 (d); R2 §7 (h) | 11 | X | `EEXIST` ⇒ `consume-repeated`: exit at once, the existing claim and journal are not opened; any other error ⇒ no claim: grant-priority CQ-3, exit `consume-claim-failed` | A |
| `RT1.CQ2.3` | FD | CQ-2: open the claim directory (cfd) read-only as a directory without following | D R5 (d) Identity | 11 | X | failure after the blocking point: claim exists, grant-priority CQ-3, exit `consume-evidence-unwritable` | A |
| `RT1.CQ2.4` | FS | CQ-2: `fstat(cfd)` must show a directory, uid 0, gid 0, mode `0700`, two links | D R5 (d) Identity | 10 | X | as RT1.CQ2.3 | A |
| `RT1.CQ2.5` | FM | CQ-2: create `journal` in cfd (write-only, create-exclusive, append, no-follow, close-on-exec, `0600`), then set `0644`; set cfd to `0755` once the journal exists | D R5 (d) Journal; D R4 (c) CP-4 | 11 | X | as RT1.CQ2.3 | A |
| `RT1.CQ2.6` | FS | CQ-2 (derived): read the ACT journal in full (≤ `journal_max_bytes`) and hash it, to fill `act_journal {sha256, length}` of `run-start` | D R5 (d) `run-start {…act_journal…}` | 8,9 | X + volume cap | unreadable/oversize ⇒ evidence failure branch of CQ-2 | M |
| `RT1.CQ2.7` | FS | CQ-2 (derived): read the boot identifier (`/proc/sys/kernel/random/boot_id`) for `run-start.boot_id` and for the boot-scoping comparison of CQ-3 | D R5 (d); D R1 (a); D R2 (h) CL-1 | 8 | X | — | M |
| `RT1.CQ2.8` | EN | CQ-2: take CP's own `INVOCATION_ID` for `run-start.invocation_id` (the same value the entry's genesis state records) | D R4 (c) CP-4; AR-6; D R5 (d) | — | X | — | A |
| `RT1.CQ2.9` | JR | CQ-2: append `run-start {invocation_id, boot_id, claim {dev, ino}, act_journal {sha256, length}}` (R8 adds `lock`, `helper`) as a canonical line | D R5 (d); R8 §8.5 | 11 | X | as RT1.CQ2.3 | A |
| `RT1.CQ2.10` | SY | CQ-2 durability point: flush the journal, then cfd, then vfd; on return the claim and its first line survive a crash (evidence only: a kernel boot ends the activation in any case) | D R5 (d) Durability point; R2 §7 (d) | 11 | X (stall unbounded, RO-6) | a failed flush ⇒ claim exists, grant-priority CQ-3, exit `consume-evidence-unwritable` | A |
| `RT1.CQ3.1` | FS | CQ-3: read the ACT journal and parse it (torn tail ignored); require the current boot identifier to equal the journal's `run-start` boot (boot scoping) | D R5 (e) CQ-3; H-JRN.8, H-JRN.9 | 8 | X + volume cap | unparsable ACT journal or another boot ⇒ `consume-failed {CQ-3, class}`, exit; the rule is left for CL | A |
| `RT1.CQ3.2` | FS | CQ-3 (derived): read the H-1 record (root-owned, `0444`, in `/var/lib/freedom-blades-rp11/h1/`) and take `baseline.files[staged rule].sha256` — the digest comes from the H-1 record, not from the journal | D R4 (b) Files CP reads; D R5 (e) CQ-3 | 8 | X + volume cap | unreadable ⇒ `consume-failed {CQ-3}`; how CP locates the record (its identifier) is not stated | M;Q4-6 |
| `RT1.CQ3.3` | FD | CQ-3: open `/run/polkit-1/rules.d` as a directory (rules-directory descriptor) without following | D R5 (e) CQ-3; D R2 (b) | 8 | X | absent directory ⇒ the rule cannot be A1-intact ⇒ `consume-failed` | A |
| `RT1.CQ3.4` | FS | CQ-3: classify the object at `50-freedom-blades-rp11.rules` against the journal's identity line and the H-1 record's staged-rule digest (H-GR1.1) | D R5 (e) CQ-3 | 8,10 | X | absent, A1-damaged, A0 ⇒ `consume-failed {CQ-3, class}`, exit; **SB-3: CP never succeeds unless this step journals `removed` for the A1-intact rule** | A |
| `RT1.CQ3.5` | ID | CQ-3: if A1-intact, re-verify immediately before removal through a descriptor (H-GR1.2): regular file, `(dev, ino)`, uid/gid 0, mode `0644`, one link, full re-hash, no forbidden extended-attribute name | D R5 (e) CQ-3; D R4 (c) CP-5 | 8,9,10 | X + volume cap 65,536 | mismatch ⇒ `consume-failed`, rule left as is for CL | A |
| `RT1.CQ3.6` | JR | CQ-3: append `remove-intent {path, dev, ino, sha256}` and flush (H-GR1.3) | D R5 (e) CQ-3 | 11 | X | grant-priority form: no line that cannot be made durable | A |
| `RT1.CQ3.7` | FM | CQ-3: remove the rule name (H-GR1.4); flush the rules directory (H-GR1.5) | D R5 (e) CQ-3 | 12 | X (tmpfs) | `unlinkat` error ⇒ `remove-failed {errno}`, exit; rule left for CL (`grant-unremovable`) | A |
| `RT1.CQ3.8` | JR | CQ-3: append `removed {path}` and flush (H-GR1.6) | D R5 (e) CQ-3 | 11 | X | — | A |
| `RT1.CQ3.9` | CN | Grant-priority form of CQ-3 (used when the claim journal is unwritable or the claim was not made): classification and removal depend only on the ACT journal's identity and the H-1 digest; remove an A1-intact rule after the same re-verification, write no line that cannot be made durable, run CQ-5's authorization check with the result held in memory, never continue to CQ-4; the attempt always fails | D R5 (e) Grant-priority form | 11,12 | X | GP-R3 principle applied to CP: a failure to write evidence reduces what is claimed and never keeps a removable live grant | A |
| `RT1.CQ4.1` | FS | CQ-4: confirm `pass-a.json` is still at its path with pfd's `(dev, ino)`, is A1-intact against its identity line in the ACT journal and its SHA-256 equals `run-start.pass_config_sha256` (re-hash) | D R5 (e) CQ-4; AR-3 | 8,9,10 | X + volume cap 65,536 | false ⇒ `consume-failed {CQ-4, class}`, exit `consume-precondition`; the rule is already removed | A |
| `RT1.CQ4.2` | FS | CQ-4: the current boot identifier equals the ACT journal's | D R5 (e) CQ-4 | 8 | X | as RT1.CQ4.1 | A |
| `RT1.CQ4.3` | FS | CQ-4: open `/var/lib/freedom-blades-rp11/activation/⟨activation_id⟩.act.json`; it must be `root:root`, `0444`, `outcome: "activated"` | D R5 (e) CQ-4 | 8,10 | X + volume cap | as RT1.CQ4.1 | A |
| `RT1.CQ4.4` | PR | CQ-4: the ACT journal has `hold-start` and no `hold-end` (parse, torn tail ignored); take τ₀ from `hold-start.capture.inactive_enter_us` | D R5 (e) CQ-4; AR-3 | 8 | X | as RT1.CQ4.1 | A |
| `RT1.CQ4.5` | FS | CQ-4: no `⟨activation_id⟩-deact-*` evidence directory exists in `/var/tmp` and no `deact` record exists in the activation record directory (list both by prefix) | D R5 (e) CQ-4 | 8,10 | X | as RT1.CQ4.1 | A |
| `RT1.CQ4.6` | FS | CQ-4 (derived): parse from `pass-a.json` the capture-root path it names and look it up without following; it must be absent | D R5 (e) CQ-4; D R2 (g) | 10 | X | CQ-0 parsed only `activation_id`; the other field is read here, under the lock | M |
| `RT1.CQ4.7` | UA | CQ-4 OS-4: DI-1 read of the holder `⟨activation_id⟩.service`: `ActiveState` `active` and `InvocationID` equal to the ACT journal's `holder_invocation_id` | D R5 (e) CQ-4 OS-4; R8 §9.3 DI-1 | 1,2 | E (c) as a child wait today | read error or false ⇒ `consume-failed {CQ-4}`; K closed on every failure path | A;Q3-1;Q4-7 |
| `RT1.CQ4.8` | UA | CQ-4 OS-1: DI-1 read of the capture unit: `ActiveState` `activating`, `InvocationID` equal to CP's own, `InactiveEnterTimestampMonotonic` equal to τ₀ (PO-21 (s), (v)); the call returns without waiting for CP's own start job | D R5 (e) CQ-4 OS-1; R2 §8 (v) | 1,2 | E (c) today | as RT1.CQ4.7 | A;Q3-1;Q4-7 |
| `RT1.CQ5.1` | FS | CQ-5: look up the rule path; it must give `ENOENT` | D R5 (e) CQ-5 | 10 | X | present ⇒ `consume-failed {CQ-5, removed-unconfirmed}` | A |
| `RT1.CQ5.2` | UA | CQ-5: PK/2 seek-not-authorized for verb `start` with budget P (H-PK2.1 … H-PK2.7; DI-5 and DI-6 inside) | D R5 (e) CQ-5; R8 §8.1 Machine C; R8 §7.11 | 2,3,3a-3g,14 | E (P); scheduled waiting ≤ P + c + g | `unconfirmed` or still `authorized` ⇒ `consume-failed {CQ-5, removed-unconfirmed}`; `ExecStart=` is not executed | A;Q3-5;Q3-6;Q4-1 |
| `RT1.CQ5.3` | JR | CQ-5: append `grant-check {status}` and flush | D R5 (e) CQ-5 | 11 | X | — | A |
| `RT1.CQ6.1` | JR | CQ-6: append `consumed {pk_status, inactive_enter_us}` and flush; no `consumed` line means no pass | D R5 (e) CQ-6 | 11 | X | failed append/flush ⇒ exit `consume-evidence-unwritable` | A |
| `RT1.CQ7.1` | JR | CQ-7: append `run-end` and flush | D R5 (e) CQ-7 | 11 | X | failed ⇒ exit non-zero; `consumed` is durable but `ExecStart=` does not run | A |
| `RT1.CQ7.2` | FD | CQ-7: close K (release the lock) — also on every failure path before a non-zero exit | R8 §8.1 Machine C CQ-7 Δ; R8 §4.6 | 6 | X | — | A |
| `RT1.CQ7.3` | XT | CQ-7: exit `0`; only now may PID 1 execute `ExecStart=`; every other exit is non-zero and leaves `ExecStart=` unexecuted | D R5 (e); R2 §8 (o) | 20 | M (T_s) | — | A |
| `RT1.CQ7.4` | CN | CP writes no record file; its journal is retained evidence; CP never removes `pass-a.json`, a directory, a record or the claim; CL never creates, opens for writing or removes the claim | D R4 (c); D R5 (d),(g) | — | — | — | A |
| `RT1.SN.1` | CN | Child surface of CP in two tiers (§8.1). *Accepted today:* the DI-1 `systemctl show` children of CQ-4 and the DI-5 `pkcheck` and DI-6 `sleep` children of the PK/2 series at CQ-5. *LIT-FULL replacement:* the only retained child intent is the DI-6 subject of the CQ-5 series (PC-1); the DI-1 and DI-5 children are removed (PC-2, PC-6). Any child that exists is created, validated, signalled, reaped or abandoned only by the H-SN contract; CP's own death leaves it in a state CS-1 … CS-10 owned by PID 1's end of the attempt, then the boot | R8 §7.5a.7 table SN-RO; §7.9 IM-S; R8 §7.5a.8 (last paragraph); §8.1 | 1,2,3,3a-3g | E, X, C | a child outliving CP holds no descriptor of K and no grant | A |

### 5.2 RT-2 — hold (the holder: ACT, HL, IGR, GRR and AV-1)

Caller: PID 1, the main process of the transient holder unit `⟨activation_id⟩.service` that SA-1 creates. Beginning boundary: the first design-controlled static image that PID 1 executes for the holder unit. Accepted failure contract: any failure before AM-3: exit non-zero then CL through `ExecStopPost=`; HARD STOPs `lock-object`, `capture-baseline-unstable`, `grant-not-seen`, `stop-control-unconfirmed`; `capture-busy-at-act`; OS-7 `start-before-hold`; IGR on every catchable end; uncatchable ends are covered by RL-1 … RL-4 and the inertness lemma (IL, IL′)

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `RT2.FI.1` | EN | Instantiate H-FI for `hold`: the first image is the one PID 1 executes as the main process of the transient holder unit `⟨activation_id⟩.service` (created by SA-1), run as root with PID 1's block; operands are the activation identifier and the A-2 SHA-256; reads INVOCATION_ID (recorded as `holder_invocation_id`) and no other variable | D R2 (e); R8 §9.6.1; R8 §9.7 (operand grammar comparison only); H-FI.1 … H-FI.7 | — | X | see H-FI | A;Q4-6 |
| `RT2.SG1.1` | SR | SG-1, the first act after the first-image operations and before any state operation: install flag-only handlers for the set H = `SIGTERM`, `SIGINT`, `SIGHUP`, `SIGQUIT`, `SIGUSR1`, `SIGUSR2`, `SIGALRM`; a handler sets `stop_requested` and returns; it raises, calls, writes, locks and sends nothing and never calls IGR | R8 §7.8 SG-1, SG-2, SG-9; R8 §7.3 row 13 | 13 | X (receipt); handlers run only between steps of the main thread | a signal arriving before SG-1 takes its default action and ends the process before any object exists (ST-1) | A;Q4-3 |
| `RT2.SG1.2` | CN | `SIGPIPE` stays ignored; `SIGCHLD` is not handled, never set to ignore or no-wait; the holder never blocks signals; a second signal sets the same flag and never re-enters IGR or restarts GRR; no deferred-exit work or immediate-exit call runs before IGR | R8 §7.8 SG-3, SG-5, SG-6, SG-7 | 13 | — | uncatchable ends (rows 8, 9, 11 of §5.5) are covered by the rungs of RL | A |
| `RT2.SG1.3` | CN | The flag is checked at every step boundary (AM-0's steps, AK-1, AM-1, AM-1R, immediately before AM-2's link, AV-1, AM-3, `hold-start`), at every HL iteration and at every `slice_ms` wake-up of every E wait; a set flag makes an E wait run the SN sequence on its child (scheduled reap waiting ≤ g), abandon if unreaped, return `interrupted`, and the body return | R8 §7.8 SG-4; R8 §7.5a.6 | 2,3,6,7,14 | E | the flag neither shortens nor extends the grace (WB-7) | A |
| `RT2.AM0.1` | FS | AM-0 (derived): read the A-2 file (location in the verified repository tree) and require its SHA-256 to equal the operand; parse the pins it quotes (activation_id, `h1_record_id`/`sha256`, `h2_record_sha256`, `boot_id`, the complete `pass-a.json` document and its SHA-256, `staged_rule_sha256` with `(dev, ino)`, lease parameters W/L/Δ/S/R and the other §7.6 pins, command-literal digests, tool and image digests) | D R1 (b) (carried by D R2 (c)); D R2 (d) AM-0 `run-start` fields; R8 §7.6 | 8,9 | X + volume cap | digest mismatch ⇒ exit non-zero (IGR is a no-op); the location of the A-2 file is not stated | M;Q4-6 |
| `RT2.AM0.2` | FS | AM-0 (i): re-check the boot identifier against A-2's `boot_id` | D R2 (d) AM-0; D R1 (a) | 8 | X | mismatch ⇒ exit non-zero; CL | A |
| `RT2.AM0.3` | FS | AM-0 (i): re-check `/run` is a `tmpfs` mount (read `/proc/self/mountinfo`, parse) and the parent conditions of `/run`, `/run/polkit-1` and `/run/polkit-1/rules.d` (when present): directory, root-owned, no group/other write, no POSIX ACL extended-attribute name | D R2 (b) Parents; D R2 (d) AP-0 row; R8 §8.1 | 8,10 | X | violation ⇒ exit non-zero; CL | A |
| `RT2.AM0.4` | FS | AM-0 (i): re-check the absence conditions by name lookup without following: tree P's top `/run/freedom-blades-rp11`, the rule path, `/etc/freedom-blades-rp11`, K, the capture root named in `pass-a.json`, and the basename `50-freedom-blades-rp11.rules` in every rules directory PO-11 (f) lists (`/etc/polkit-1/rules.d`, `/run/polkit-1/rules.d`, `/usr/local/share/polkit-1/rules.d`, `/usr/share/polkit-1/rules.d`); `/run/polkit-1/rules.d` must be present (or absent with PO-11 (f)(ii) accepted) | D R2 (d) AP-0 row; R8 §8.1 AM-0 (i) (K included) | 10 | X | present object ⇒ exit non-zero; CL | A |
| `RT2.AM0.5` | UA | AM-0 (i): DI-1 reads `LoadState` of `⟨activation_id⟩.service`, `⟨activation_id⟩-backstop.timer` and `⟨activation_id⟩-backstop.service`; each must be `not-found` | D R2 (d) AP-0 row | 1 | E (c) per read today | any other value or a read error ⇒ exit non-zero; CL | A;Q3-1 |
| `RT2.AM0.6` | FS | AM-0 (i): `/run/nextroot` must be absent (CL-21i single disarm condition) | D R2 (d); R2 §9 | 10 | X | present ⇒ exit non-zero; CL | A |
| `RT2.AM0.7` | GAP | **Gap row — non-operative.** Accepted text does not state whether AM-0 repeats AP-0's “no unterminated activation of this H-1 record” condition. D R2 (d) AM-0 says to re-check “AP-0's `boot_id`, `/run` and absence conditions”; R8 §8.1 AM-0 (i) says “`boot_id`, `/run` and every AP-0 absence condition, `K` included”; D R2 (d) AP-0 states the no-unterminated-activation condition as a separate item and does not say that it is one of its “absence conditions”. WP-2 has selected **neither** answer. This row states no operation: it requires no listing of the activation record directory, no read of any `deact` record and no enforcement or omission of any check, and it is not to be consumed as an instruction. The AM-0 operations that are unambiguous are `RT2.AM0.1` … `RT2.AM0.6` and `RT2.AM0.8` … `RT2.AM0.17`. The question is Q6-7 (§12, owner WP-6) | D R2 (d) AM-0 and AP-0 rows; R8 §8.1 AM-0 (i) | — | — | none stated: no operation is described | Q6-7 |
| `RT2.AM0.8` | FM | AM-0 (ii): create K by exclusive directory creation on a `/run` descriptor (fails `EEXIST` for any existing name, never follows a final symlink), `root:root`, mode `0700`, empty, no `system.posix_acl_*` or capability extended attribute | R8 §4.5 LD-1; R2 §7 (h) | 11 | X | failure ⇒ exit non-zero; a K left by a crash before the journal is class S0 and is cleared by the boot | A |
| `RT2.AM0.9` | FD | AM-0 (ii): open K (H-LK.1) and verify type, owner, mode and link count | R8 §4.5 LD-1 | 6,10 | X | violation ⇒ HARD STOP `lock-object` before AM-1; nothing is linked | A |
| `RT2.AM0.10` | LK | AM-0 (ii): take the exclusive non-blocking lock once; `EWOULDBLOCK` is impossible for a fresh K and is HARD STOP `lock-object` | R8 §4.6; R8 §4.7 | 6 | X | HARD STOP `lock-object` | A |
| `RT2.AM0.11` | CK | AM-0 (iii) BSP: read the monotonic clock and floor it to microseconds (`m_a`) before reading the baseline | R8 §6.4 BSP | 3 | X | — | A |
| `RT2.AM0.12` | UA | AM-0 (iii): DI-1 read of the capture unit `ActiveState`, `InvocationID`, `InactiveEnterTimestampMonotonic` (τ₀), `Job` | R8 §6.4 BSP; D R5 (c) AM-0 | 1 | E (c) per read | a read that does not finish is an error, never a baseline | A;Q3-1;Q4-7 |
| `RT2.AM0.13` | CN | AM-0 (iii): require τ₀ < `m_a`; otherwise wait at least 2 ms and repeat, at most 5 times (class C), then exit non-zero `capture-baseline-unstable` (nothing linked; CL runs); require `ActiveState` `inactive` or `failed` and `Job` empty, else exit non-zero `capture-busy-at-act` | R8 §6.4 BSP; D R5 (c) | 15 | C (5) | `capture-baseline-unstable`; `capture-busy-at-act` | A |
| `RT2.AM0.14` | SL | AM-0 (iii): the 2 ms wait of each BSP retry | R8 §6.4; §7.3 row 7 | 7 | E (capped by WB-2) | flag observed at the wake-up | A |
| `RT2.AM0.15` | FD | AM-0 (iv): open the ACT evidence directory `/var/tmp/⟨activation_id⟩-act-evidence/` (created by AP-1 as `ubuntu`, `0700`) without following; require owner `ubuntu`, mode `0700` | D R1 (b); D R2 (d) | 8,10 | X | violation ⇒ exit non-zero; CL | A |
| `RT2.AM0.16` | JR | AM-0 (iv): create `journal` (H-JRN.2, H-JRN.3) and append `run-start {a2_sha256, h1_record_sha256, h2_record_sha256, boot_id, pass_config_sha256, staged_rule_sha256, tool_sha256, holder_invocation_id, lease, lock {object {path, dev, ino}, mode, wait_ms}, capture {active_state, invocation_id, inactive_enter_us, m_a_us, bsp_retries}, helper {role, image_sha256[], tool_sha256}, params}` (H-JRN.5 … H-JRN.7) | D R2 (d) AM-0; D R5 (c); R8 §8.5 `lock`, `capture`, `helper`, `params` | 11 | X | any failure ⇒ exit non-zero, then CL (`stop-post`) | A;Q4-6 |
| `RT2.AM0.17` | CN | AM-0 keeps K until `hold-start` is durable (AR-2); the holder holds a lock only while single-threaded | D R5 (c) AR-2; R8 §4.6; LD-3 (b) | 6 | — | — | A |
| `RT2.AK1.1` | JR | AK-1: append `backstop-intent` and flush before the literal is issued (CL's by-name disarm after an `error`, `interrupted` or abandoned `systemd-run` is keyed to it: confirmation item of OH-S0d, A-I-16) | D R2 (d) AK-1; R8 §7.5a.4 SN-10, §8.1 | 11 | X | failure ⇒ exit non-zero; CL | A |
| `RT2.AK1.2` | UA | AK-1 DI-3: create the backstop service and timer — timer `⟨activation_id⟩-backstop.timer` firing at `--on-active=⟨R⟩` and `--on-unit-active=⟨R⟩` with `AccuracySec=1s`; service `⟨activation_id⟩-backstop.service` of type `exec`, `Restart=no`, `OOMScoreAdjust=-1000`, `RuntimeMaxSec=⟨S_b⟩`, `TimeoutStopSec=⟨S⟩` (no `TimeoutStartSec=`, BS-RM), main command the `backstop` role with the activation identifier and the A-2 SHA-256; no environment, scope, user, terminal, wait or collect option; no `%`, `$`, `\` or quotation mark in the arguments; today one `/usr/bin/systemd-run` child (removed from the LIT-FULL replacement, PC-4; call site CALL-DI3-01) | D R2 (f); R8 §7.4 BS-RM; R8 §9.3 DI-3; R2 §8 (j),(m) | 1,2,3 | E (c) today; today a mutating child: effect unknown after `error`/`interrupted`/abandon (SN-10) | a name already loaded makes the call fail and create nothing (PO-21 (m)); today `error`, `interrupted` or abandon ⇒ `effect: "unknown"` (SN-10, A-I-16), exit non-zero, CL runs; the mapping of `unknown` to a non-child loader-free interaction is the unanswered Q6-6 (not made here) | A;Q3-3;Q4-7;Q6-6 |
| `RT2.AK1.3` | UA | AK-1: DI-1 read of the timer `⟨activation_id⟩-backstop.timer`: it must be `active` | D R2 (d) AK-1; R8 §7.5a.1 callers ("the timer `show`") | 1 | E (c) today | not active ⇒ exit non-zero; CL | A;Q3-1 |
| `RT2.AK1.4` | JR | AK-1: append `backstop-armed {timer, period_s, max, runtime_s}` and flush; no activation file exists before this commit | D R2 (d) AK-1; R8 §8.1 | 11 | X | failure ⇒ exit non-zero; CL | A |
| `RT2.AM1.1` | FM | AM-1: build tree P — top `/run/freedom-blades-rp11/` (`root:root`, `0755`) with member `pass-a.json` (`root:root`, `0644`) — in the pre-existing parent `/run` by protocol PT (H-PT.1 … H-PT.10) with the temporary name `.rp11-⟨RUN⟩-P.tmp`; the file's bytes are `canonical_bytes(doc)` with `doc` exactly as A-2 quotes it (no field edited) | D R2 (b),(d); D R1 (c),(d) | 11 | X | exit non-zero; CL (state ST-1.a1 once committed) | A |
| `RT2.AM1.2` | HS | AM-1: serialize the A-2 `pass-a.json` document as `canonical_bytes` and require its SHA-256 to equal A-2's pin before publication | D R1 (c); D 4.3.5 | 9 | X | mismatch ⇒ exit non-zero; CL | A |
| `RT2.AM1R.1` | FM | AM-1R, only if `/run/polkit-1/rules.d` was absent (admissible only if PO-11 (f)(ii) is accepted; otherwise AP-0 requires the directory to exist): build tree R by PT — its top is the first absent component of `/run/polkit-1/rules.d`, with no file member | D R2 (d) AM-1R; R2 §6.4 (f)(ii) | 11 | X | exit non-zero; CL | A |
| `RT2.AM1G.1` | FS | AM-1G (derived): open the staged rule under tree L read-only through a descriptor whose `(dev, ino)` equals the H-1 record's, read it once and require its SHA-256 to equal `staged_rule_sha256` | D R1 (c); D R2 (d) AM-2 | 8,9,10 | X + volume cap 65,536 | mismatch ⇒ exit non-zero; no rule exists | M |
| `RT2.AM1G.2` | FM | AM-2/PF steps PF-1 … PF-5 for the rule into `/run/polkit-1/rules.d` (`grant: true`, mode `0644`): nothing at the name, intent, unnamed inode, identity line, write, flush, owner, mode (H-PF.1 … H-PF.5) | D R2 (d) AM-2; D R1 (c) | 11 | X | exit non-zero; no rule linked | A |
| `RT2.AM1G.3` | FM | AM-1G: create `K/grant.id` (exclusive creation, no-follow, close-on-exec, then mode `0600`, `root:root`) holding one canonical line `{path, dev, ino, sha256, size, mode, uid, gid, boot_id}` of the staged rule that PF-6 will link — after the unnamed inode's identity is known and immediately before PF-6; tmpfs only | R8 §4.5 GI-1; R8 §8.1 AM-1G | 11 | X | failure ⇒ exit non-zero; CL; no rule exists | A |
| `RT2.AM2.1` | CN | AM-2: check the stop flag immediately before the link (SG-4); a `SIGTERM` between the last check and the link costs a brief G1 that IGR removes | R8 §7.8 SG-4 | 13 | — | — | A |
| `RT2.AM2.2` | FM | AM-2 PF-6: link the unnamed inode under `50-freedom-blades-rp11.rules` in `/run/polkit-1/rules.d` — the grant is live from this link (state G1, ST-1.a2) | D R2 (d) AM-2; D R1 (c) PF-6 | 11 | X | `EEXIST` ⇒ HARD STOP `foreign-rule`; the object is A0 and kept; `pass-a.json` removed by CL; any other failure ⇒ exit non-zero | A;Q4-1 |
| `RT2.AM2.3` | CN | AM-2: check the stop flag at the very next statement after the link returns | R8 §7.8 SG-4 | 13 | — | — | A |
| `RT2.AM2.4` | SY | AM-2 PF-7: flush `/run/polkit-1/rules.d` (tmpfs; possibly a no-op, no claim depends on it) | D R1 (c) PF-7; R2 §7 (g) | 12 | X | — | A |
| `RT2.AM2.5` | JR | AM-2 PF-8: append `file-linked {dir, name}` and flush | D R1 (c) PF-8 | 11 | X | failure ⇒ exit non-zero; IGR; CL | A |
| `RT2.AM2.6` | FS | AM-2 PF-9 and record the time of the link (`grant_linked_utc`) | D R1 (c) PF-9; D R1 (g) `time` | 8,9,10 | X + volume cap | mismatch ⇒ exit non-zero; IGR; CL | A |
| `RT2.AV1.1` | ID | AV-1: re-verify both published files as PF-9 (`pass-a.json` and the rule) | D R2 (d) AV-1; D R1 (d) AV-1 | 8,9,10 | X + volume cap | failure ⇒ IGR; CL | A |
| `RT2.AV1.2` | HS | AV-1 H-2b: recompute the complete baseline (H-BSE.1 … H-BSE.14) and require it to equal the H-1 record's `baseline_sha256` | D R1 (d) AV-1; D 4.3.4 | 9 | X | mismatch ⇒ IGR; CL | A;Q6-2 |
| `RT2.AV1.3` | UA | AV-1 positive control: PK/2 seek-authorized for verb `start`, budget P (H-PK2); `unconfirmed` ⇒ HARD STOP `grant-not-seen` (CL runs, rule first; nothing later may be read as evidence) | R8 §8.1 AV-1; R8 §7.11 | 2,3,3a-3g,14 | E (P); ≤ P + c + g of scheduled waiting | HARD STOP `grant-not-seen` | A;Q3-5;Q3-6;Q4-1 |
| `RT2.AV1.4` | UA | AV-1 negative control (AR-7): PK/2 first-decisive for verb `stop`, which must be `not-authorized`; `authorized` fails ACT at once; `unconfirmed` ⇒ HARD STOP `stop-control-unconfirmed` | R8 §8.1 AV-1; D R4 (g) AR-7; R8 §7.11 | 2,3,3a-3g,14 | E (P) | `authorized` ⇒ ACT fails, CL rule first; `unconfirmed` ⇒ HARD STOP | A;Q3-5;Q3-6;Q4-1 |
| `RT2.AM3.1` | JR | AM-3: assemble the `act` record (outcome `activated`) and publish it by PF into the activation record directory (H-REC.1, H-REC.3), then re-read it — the commit of this record is ACT PASS | D R2 (d) AM-3; D R1 (d),(g) | 8,9,11 | X | failure ⇒ exit non-zero; CL writes `act.json` outcome `failed` if none exists | A |
| `RT2.AM3.2` | JR | AM-3 (placement unresolved): the ACT journal's closed set includes `run-end`; D R1 (d) appended it after the `act` record, D R2 does not restate it, and HL ends with `hold-end`; R8 A-I-17 names `hold-end` as the holder's complete-end line | D R1 (d); D R2 (m); R8 Appendix A A-I-17 | 11 | X | — | A;Q4-11 |
| `RT2.HS.1` | UA | `hold-start`: DI-1 re-read of the capture unit `ActiveState`, `InvocationID`, `InactiveEnterTimestampMonotonic`, `Job` while K is still held; require `inactive`/`failed`, empty `Job`, τ equal to τ₀ | D R5 (c); R8 §6.7 | 1 | E (c) today | mismatch (OS-7) ⇒ append `hold-end {reason: "start-before-hold"}` instead, exit non-zero, CL (rule first); never reaches ST-2 | A;Q3-1;Q4-7 |
| `RT2.HS.2` | JR | `hold-start`: append `hold-start {capture {active_state, inactive_enter_us}}` and flush | D R5 (c); R2 (d) | 11 | X | failure ⇒ OS-7 branch | A |
| `RT2.HS.3` | FD | `hold-start`: close K immediately after `hold-start` is durable (AR-2); A-2 permits the operator's `start` only after this point and while the holder is `active` | R8 §4.6; D R5 (c) AR-2; D R4 (g) | 6 | X | — | A |
| `RT2.HL.1` | SL | HL: every Δ ms (`poll_ms`, 250 … 5,000) after ACT PASS, in `slice_ms` slices, observing the flag at each wake-up | D R2 (g); R8 §7.3 row 7; §7.8 SG-4 | 7 | E | flag ⇒ the body returns after the SN sequence; HL's life is bounded by L (class M) | A |
| `RT2.HL.2` | FS | HL: look up the capture root `c` named in `pass-a.json` (name lookup only; HL never lists, opens or changes `c`) | D R2 (g) | 10 | X | error ⇒ `observation-failed` | A |
| `RT2.HL.3` | UA | HL: DI-1 read of the capture unit `ActiveState`, `InvocationID` (and, for the amended reasons, `InactiveEnterTimestampMonotonic`, `Job`, `ExecMainStartTimestampMonotonic`) | D R2 (g); D R5 (g),(j) PO-21 (v) | 1 | E (c) today | an observation that errors or does not parse ⇒ `observation-failed`: fail closed, the activation ends | A;Q3-1;Q4-7 |
| `RT2.HL.4` | CN | HL evaluates, in order, the first matching terminal reason: `pass-ended`, `pass-failed-early`, `start-failed-before-exec`, `capture-unloaded`, `start-window-expired` (W s since ACT PASS, W 60 … 3,600), `observation-failed`; HL never treats one as a reason to remove anything itself | D R2 (g); D R4 (f); D R5 (g) | — | X | — | A |
| `RT2.HL.5` | JR | HL: append `pass-observed` only when an observation differs from the previous one (not at every poll) | D R2 (m) | 11 | X | — | A |
| `RT2.HL.6` | FD | HL decision (OS-5): when a terminal reason holds, open K (derived from the activation identifier) and try the exclusive lock once without blocking | R8 §4.6 HL; D R5 (g) OS-5 | 6 | X | `EWOULDBLOCK` ⇒ a CP holds the lock: HL does not end and observes again after Δ | A |
| `RT2.HL.7` | FS | HL decision under the lock: observe again, now also reading the claim directory and its journal (consume `run-start`, `consumed`); if a terminal reason still holds continue, otherwise release K and continue | D R5 (g) OS-5 | 8,10 | X + volume cap | — | A |
| `RT2.HL.8` | JR | HL: append `hold-end {reason, observation}` and flush | D R2 (g); D R5 (g) | 11 | X | `observation-failed` exits non-zero | A |
| `RT2.HL.9` | FD | HL: close K after `hold-end` is durable and before exiting (LD-4 replaces OS-5's "exits while holding the lock"); exit `0` (`observation-failed`: non-zero) | R8 §4.5 LD-4; R8 §4.6 | 6 | X | a CP that gets the lock afterwards finds `hold-end` and refuses at CQ-4 | A |
| `RT2.HL.10` | CN | A pass or activation still running at L is ended by PID 1: `RuntimeMaxSec=` L sends `SIGTERM` to the holder and, after S, `SIGKILL`; from the moment the holder's `ActiveState` leaves `active`, the inertness lemma applies whatever any helper is doing | R8 §7.4; §5.4 IL, IL′; R2 §8 (d) | 17 | M (L) | IL′ holds; no helper timing is claimed | A |
| `RT2.IGR.1` | CN | IGR (RL-0): runs from one `finally`-equivalent site that wraps the whole body after SG-1, once, on every catchable end (return, raise or observed flag); no handler calls it | R8 §5.7 IGR "When"; SG-7 | 13 | X | IGR may not run before a `SIGKILL`; the design is correct in that case too (IL) | A |
| `RT2.IGR.2` | CN | IGR-1: GRR with the in-memory identity (H-GRR.3 … H-GRR.5); if AM-2 was never reached there is no rule and GRR returns `absent` | R8 §5.7 IGR-1 | 12 | X | GRR never raises | A |
| `RT2.IGR.3` | JR | IGR-2: after the removal append `igr {outcome, identity}` to the ACT journal and flush, best effort; an `ext4` write that fails or stalls changes nothing about the grant | R8 §5.7 IGR-2 | 11 | X (stall unbounded, RO-6) | a kill between removal and this line ⇒ a later CL classes the rule `absent-before-removal` | A |
| `RT2.IGR.4` | CN | IGR-3: nothing else — no spawn, no signal, no authorization call, no lock, no network; `pass-a.json`, directories and records are left to CL; IGR does not claim `removed-verified` | R8 §5.7 IGR-3; SG-9 | 3d | X | — | A |
| `RT2.IGR.5` | CN | Interruption map IM-I I0 … I4 and IM-A (termination at a point leaves the objects built so far; first owner per ladder RL) — see §10 of this document | R8 §7.9 IM-I, IM-A | — | — | — | A |
| `RT2.END.1` | XT | After IGR return the holder's exit status; no `atexit` work and no immediate-exit call before IGR; then PID 1 runs `ExecStopPost=` (RT-3) if it can spawn it | R8 §7.8 SG-7; R8 §5.3 RL-1 | 18 | M (S) | spawn failure ⇒ `FINAL_SIGTERM` with result `resources`; the backstop (RT-4) is the next rung | A |
| `RT2.SN.1` | CN | Child surface of the holder in two tiers (§8.1). *Accepted today:* the DI-1 `systemctl show` children (AM-0, AK-1, `hold-start`, HL, the H-2b baseline reads), the DI-3 `systemd-run` child at AK-1 — a **mutating** child whose effect is `unknown` after `error`, `interrupted` or abandon (SN-10, A-I-16) — and the DI-5 `pkcheck` and DI-6 `sleep` children of the AV-1 series. *LIT-FULL replacement:* the only retained child intent is the DI-6 subject of the AV-1 series (PC-1); the DI-1, DI-3 and DI-5 children are removed (PC-2, PC-4, PC-6) and are not children in the replacement root-procedure tree. *Carried, unmapped obligation:* the accepted `effect: "unknown"` obligation of SN-10 must still be honoured for the DI-3 interaction; its mapping to a non-child loader-free interaction is the unanswered Q6-6, and WP-2 does not choose whether that interaction is realized in process, by a static child or by another admitted mechanism. Any child that exists is created, validated, signalled, reaped or abandoned only by the H-SN contract; the holder's death leaves it in a state CS-1 … CS-10 owned by PID 1's stop of the holder unit, then the boot | R8 §7.5a.7 table SN-RO; SN-10; A-I-16; §7.9 IM-S; R8 §7.5a.8 (last paragraph); §8.1 | 1,2,3,3a-3g | E, X, C | CS-7, CS-8, CS-10: the `child` line; CS-1 … CS-6, CS-9: only the missing `hold-end` ⇒ `children-unknown` | A;Q6-6 |

### 5.3 RT-3 — stop-post (CL, trigger `stop-post`; CL-G, GP-R3)

Caller: PID 1, the holder unit's `ExecStopPost=`. Beginning boundary: the first design-controlled static image that PID 1 executes for `ExecStopPost=`. Accepted failure contract: `st1-verified` or HARD STOP (ST-1+R) with a residual list; `record-unpublished`; `evidence-unwritable` under GP-R3 (ST-1.ur); `unit-still-active`; a stop-post that PID 1 cannot spawn is skipped (`FINAL_SIGTERM`, result `resources`) and RT-4 is the next rung

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `RT3.FI.1` | EN | Instantiate H-FI for `stop-post`: the first image is the one PID 1 executes as `ExecStopPost=` of `⟨activation_id⟩.service`; operands: activation identifier, A-2 SHA-256 and the trigger `stop-post`; reads INVOCATION_ID only (provenance, diagnostic); caller: PID 1, the holder unit's `ExecStopPost=` (run as the unit's user, root, after the main process ends for any cause PID 1 can spawn it after) | R8 §9.6.1; R8 §9.2; H-FI | — | X | see H-FI | A;Q4-6 |
| `RT3.FI.2` | CN | Whole-life terminator: PID 1's `TimeoutStopSec=` S (60 … 600, rec. 120): `SIGTERM` at S, `SIGKILL` after a further S, then `failed` / `timeout`; CL installs no handler (SG-8) so the first signal ends it; elapsed time of CL is not claimed (class M terminator only) | R8 §7.4; R8 §7.8 SG-8 | 18 | M (S) | interruption map: IM-L points L0 … L9; first owner: the backstop's CL (RT-4) if armed and spawnable, else CP at a later start (CQ-3), then the boot, then `attest` | A |
| `RT3.CLG` | CMP | CL-G (first act), trigger `stop-post`: perform H-CL.G.1, H-CL.G.2, H-GRR.1 … H-GRR.8. If PID 1 cannot spawn `ExecStopPost=` (result `resources`) this rung does not run and RT-2's IGR (earlier) and RT-4 (later) are the other rungs. | R8 §5.7 CL-G | 12,10,8 | see the helper rows | interruption: L0, L1 (IM-L points L0 … L9); owner: the backstop's CL (RT-4) if armed and spawnable, else CP at a later start (CQ-3), then the boot, then `attest` | A |
| `RT3.CL0` | CMP | CL-0 (lock attempts to λ, attempt directory, journal, `run-start`, held `cl-g` line), trigger `stop-post`: perform H-CL.0.1 … H-CL.0.6, H-LK.1 … H-LK.4, H-JRN.1 … H-JRN.7. For `stop-post` record the parent PID and INVOCATION_ID as provenance (diagnostic only); lock attempts are bounded by λ, never by S (a lock retained forever leaves CL in degraded mode, not `lock-timeout`). | D R2 (h) CL-0; R8 §8.1 | 6,7,10,11 | see the helper rows | interruption: L2 (IM-L points L0 … L9); owner: the backstop's CL (RT-4) if armed and spawnable, else CP at a later start (CQ-3), then the boot, then `attest` | A |
| `RT3.CL1` | CMP | CL-1 (read journals, A-2 pins, H-1 record; boot scoping), trigger `stop-post`: perform H-CL.1.1 … H-CL.1.3, H-JRN.8, H-JRN.9. | D R2 (h) CL-1; D R4 (g) | 8,9,10 | see the helper rows | interruption: L3 (IM-L points L0 … L9); owner: the backstop's CL (RT-4) if armed and spawnable, else CP at a later start (CQ-3), then the boot, then `attest` | A |
| `RT3.CL2` | CMP | CL-2 (capture-unit state; attempt classification), trigger `stop-post`: perform H-CL.2.1, H-CL.2.2, H-DI1.1 … H-DI1.4. | D R1 (e) CL-2 | 1,2,8,10 | see the helper rows | interruption: L3 (IM-L points L0 … L9); owner: the backstop's CL (RT-4) if armed and spawnable, else CP at a later start (CQ-3), then the boot, then `attest` | A |
| `RT3.CL3` | CMP | CL-3 (classify the rule; remove if A1-intact), trigger `stop-post`: perform H-CL.3.1, H-CL.3.2, H-GR1.1 … H-GR1.6. | D R1 (e) CL-3; R8 §8.1 | 8,9,10,11,12 | see the helper rows | interruption: L3 (IM-L points L0 … L9); owner: the backstop's CL (RT-4) if armed and spawnable, else CP at a later start (CQ-3), then the boot, then `attest` | A |
| `RT3.CL4` | CMP | CL-4 (rule absent; PK/2 seek-not-authorized), trigger `stop-post`: perform H-CL.4.1, H-CL.4.2, H-PK2.1 … H-PK2.7, H-PROC.1 … H-PROC.6, H-SN.1 … H-SN.16. | D R1 (e) CL-4; R8 §8.1 | 1,2,3,3a,3b,3c,3d,3e,3f,3g,4,14 | see the helper rows | interruption: L4 (IM-L points L0 … L9); owner: the backstop's CL (RT-4) if armed and spawnable, else CP at a later start (CQ-3), then the boot, then `attest` | A |
| `RT3.CL5` | CMP | CL-5 (`pass-a.json`), trigger `stop-post`: perform H-CL.5.1, H-CL.5.2, H-GR1.1 … H-GR1.6. | D R1 (e) CL-5 | 8,9,10,11,12 | see the helper rows | interruption: L5 (IM-L points L0 … L9); owner: the backstop's CL (RT-4) if armed and spawnable, else CP at a later start (CQ-3), then the boot, then `attest` | A |
| `RT3.CL5b` | CMP | CL-5b (directories; `grant.id` and K last), trigger `stop-post`: perform H-CL.5b.1, H-CL.5b.2, H-GR1.1 … H-GR1.6. | D R2 (h) CL-5b; R8 §8.1 | 8,10,11,12 | see the helper rows | interruption: L6 (IM-L points L0 … L9); owner: the backstop's CL (RT-4) if armed and spawnable, else CP at a later start (CQ-3), then the boot, then `attest` | A |
| `RT3.CL6` | CMP | CL-6 (verify ST-1; baseline recomputation), trigger `stop-post`: perform H-CL.6.1 … H-CL.6.4, H-BSE.1 … H-BSE.15, H-DI1.1. | D R2 (h) CL-6; R8 §8.1 | 1,8,9,10 | see the helper rows | interruption: L7 (IM-L points L0 … L9); owner: the backstop's CL (RT-4) if armed and spawnable, else CP at a later start (CQ-3), then the boot, then `attest` | A |
| `RT3.CL7` | CMP | CL-7 (records; `run-end`; close K), trigger `stop-post`: perform H-CL.7.1, H-CL.7.2, H-REC.1 … H-REC.4, H-PF.1 … H-PF.9. | D R2 (h) CL-7; R8 §8.1 | 6,8,9,11 | see the helper rows | interruption: L8, L9 (IM-L points L0 … L9); owner: the backstop's CL (RT-4) if armed and spawnable, else CP at a later start (CQ-3), then the boot, then `attest` | A |
| `RT3.CLGP` | CMP | GP-R3 (grant-priority mode; entered on E-a, E-b, E-c), trigger `stop-post`: perform H-CL.GP.1 … H-CL.GP.5. | D R3 (e) | 2,8,9,10,11,12,14 | see the helper rows | interruption: GP-R3 entry E-a/E-b/E-c; ST-1.ur (IM-L points L0 … L9); owner: the backstop's CL (RT-4) if armed and spawnable, else CP at a later start (CQ-3), then the boot, then `attest` | A |
| `RT3.CLOUT` | CMP | Outcome rule and ST-1 mapping, trigger `stop-post`: perform H-CL.OUT. | D R1 (e); D R2 (h) | — | see the helper rows | interruption: — (IM-L points L0 … L9); owner: the backstop's CL (RT-4) if armed and spawnable, else CP at a later start (CQ-3), then the boot, then `attest` | A |
| `RT3.SN.1` | CN | Child surface of stop-post in two tiers (§8.1); the DI-3 and DI-4 calls are not made by stop-post. *Accepted today:* the DI-1 `systemctl show` children (the CL-2 / CL-6 reads) and the DI-5 `pkcheck` and DI-6 `sleep` children of the CL-4 series. *LIT-FULL replacement:* the only retained child intent is the DI-6 subject of the CL-4 series (PC-1); the DI-1 and DI-5 children are removed (PC-2, PC-6). H-SN applies to any child that exists. *Owner of a child left behind by stop-post (R8 §7.5a.7 table SN-RO, stop-post CL row):* PID 1, which sends `FINAL_SIGTERM` and then, after another S, `FINAL_SIGKILL` to “what remains” (R2 §8 (e), established; taxonomy row 3f, class M: PID 1's sending is not proof that the target exited, and no elapsed bound is claimed); whether “what remains” includes a child that called `setsid` is PO-SN (e) and is not guaranteed; the boot is a separate recovery event (IS-7). `attest` has no automatic owner of the child. *Observer contract, separate from ownership:* CS-7, CS-8 and CS-10 leave a line in the CL attempt journal; CS-1 … CS-6 and CS-9 leave only the missing `run-end`, from which the backstop's CL or `attest` may record `children-unknown {helper_role, missing_terminal_line}` and does nothing else; no later procedure searches for, signals, reaps or acts on the child (SN-9). *Recovery of the unfinished cleanup state is not child ownership:* it is carried by the CL rows `RT3.FI.2` and `RT3.CLG` … `RT3.CLOUT` (the backstop's CL (RT-4) if armed and spawnable, else CP at a later start (CQ-3), then the boot, then `attest`) and the row does not restate it | R8 §7.5a.7; R8 §7.5a.8 (last paragraph); §8.1 | 1,2,3,3a-3g | E, X, C for the helper's own waits; PID 1's `FINAL_SIGTERM` / `FINAL_SIGKILL` are class M (taxonomy row 3f): a send is not proof of exit and no elapsed bound is claimed | CS-7, CS-8, CS-10: the line; CS-1 … CS-6, CS-9: the missing `run-end` | A |

### 5.4 RT-4 — backstop (BS-1 … BS-4 and CL, trigger `backstop`)

Caller: PID 1, the service that the backstop timer starts (the holder creates the timer at AK-1). Beginning boundary: the first design-controlled static image that PID 1 executes for the backstop service. Accepted failure contract: BS-1 … BS-3 exit `0` without record; BS-4 runs CL; after `backstop_max` firings or `k` > 99 the timer is disarmed, a journal line appended and the service exits non-zero without a record; each firing ends at `RuntimeMaxSec=` S_b (BS-RM)

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `RT4.FI.1` | EN | Instantiate H-FI for `backstop`: the first image is the one PID 1 executes as the backstop service's main command; operands: activation identifier, A-2 SHA-256; reads INVOCATION_ID only (provenance, diagnostic); caller: PID 1, the service `⟨activation_id⟩-backstop.service` that the backstop timer starts (the holder created the timer at AK-1); each firing runs BS-1 … BS-4 | R8 §9.6.1; R8 §9.2; H-FI | — | X | see H-FI | A;Q4-6 |
| `RT4.FI.2` | CN | Whole-life terminator: PID 1's `RuntimeMaxSec=` S_b (BS-RM, 60 … 600, rec. 120) with `TimeoutStopSec=` S: `SIGTERM` at S_b, `SIGKILL` after S; at most `backstop_max` B firings run CL (class C); CL installs no handler (SG-8); the timer re-arms only when the service leaves the active states | R8 §7.4; R8 §7.8 SG-8 | 19 | M (S_b); C (B) | interruption map: IM-B (points of IM-L); first owner: the next firing of the backstop, else CP at a later start, then the boot, then `attest` | A |
| `RT4.BS1.1` | UA | BS-1: DI-1 read of the holder unit `⟨activation_id⟩.service` `ActiveState`; if `activating`, `active`, `deactivating` or `reloading` exit `0` with no record and no mutation (the holder or its `ExecStopPost=` still owns the activation) | D R2 (f) BS-1; R8 §9.3 DI-1 | 1 | E (c) today | a read error is not an accepted case for BS-1; the unit may be `not-found`/`inactive`/`failed` ⇒ continue | A;Q3-1;Q4-7 |
| `RT4.BS2.1` | FS | BS-2: list the activation record directory and read the latest `deact` record(s) of this activation; test for a record with outcome `st1-verified` that is `root:root`, `0444` and parses (record schema check) | D R2 (f) BS-2 | 8,10 | X + volume cap | no such record ⇒ continue to BS-3 | A |
| `RT4.BS2.2` | UA | BS-2: DI-4 disarm the backstop timer — stop `⟨activation_id⟩-backstop.timer` (the only unit verb BS issues; it names only this activation's own timer); then exit `0`, no record; today `systemctl stop ⟨id⟩-backstop.timer` as a mutating child (removed from the LIT-FULL replacement, PC-5). **This row defines the disarm intent and is shared:** it implements call site CALL-DI4-01 (BS-2) and, by the delegation stated in `RT4.BS3.1`, call site CALL-DI4-02 (BS-3) | D R2 (f); R8 §9.3 DI-4; R2 §8 (j) | 1,2 | E (c) today; today a mutating child: effect unknown after `error`/`interrupted`/abandon (SN-10) | the timer stays armed and fires again; no record; BS never starts, stops or kills the holder or the capture unit; the mapping of `effect: "unknown"` to a non-child loader-free interaction is the unanswered Q6-6 | A;Q3-4;Q4-7;Q6-6 |
| `RT4.BS3.1` | PR | BS-3: if the latest `deact` record is `hard-stop`, its residual contains no A1-intact object and its grant class is not `removed-unconfirmed` or `grant-unremovable`: disarm (DI-4, the operation of `RT4.BS2.2`) and exit `0`; nothing further can be removed without Peter (ST-1+R). **This row is the decision and the invocation of call site CALL-DI4-02 (BS-3);** the disarm operation it invokes is the one defined by `RT4.BS2.2`, and the mutating-call obligation of that operation applies at this call site as well | D R2 (f) BS-3; R8 §9.3 DI-4 | 8,1,2 | X; the disarm: E (c) today, mutating (SN-10) | otherwise BS-4; as `RT4.BS2.2` for the disarm; Q6-6 applies | A;Q3-4;Q4-7;Q6-6 |
| `RT4.BS4.1` | CN | BS-4: otherwise run CL with trigger `backstop` (rows RT4.CLG … RT4.CLOUT, in degraded lock mode if K cannot be acquired); at most `backstop_max` (B, 1 … 99, rec. 20; accepted `k` ≤ 99) firings run CL | D R2 (f) BS-4; R8 §8.1 BS-4 Δ2; R8 §7.3 row 16 | 16 | C (B) | the next firing disarms the timer, appends a journal line and exits non-zero | A |
| `RT4.BS4.2` | UA | BS-4 (B exceeded or `k` would exceed 99): disarm the timer (DI-4; the same call form as `RT4.BS2.2`, here the **terminal disarm**), append one journal line and exit non-zero without a record; the journals stand; which journal receives the line is not stated. **This row implements call site CALL-DI4-03 (BS-4)** | D R2 (f) BS-4; R8 §8.1 BS-4 Δ2; R8 §9.3 DI-4 | 16,11,1,2 | C; the disarm: E (c) today (the same call form as `RT4.BS2.2`) | the journals stand; the final state is recorded or left to the boot; accepted text states no `unknown`-effect treatment for this call site: SN-10 / A-I-16 name the DI-4 call at BS-2 and BS-3 only, and whether they extend to the BS-4 terminal disarm is not decided here (open, Q6-7) | A;Q3-4;Q4-7;Q4-11;Q6-7 |
| `RT4.BS.1` | CN | BS never starts, stops or kills the holder or the capture unit; BS-1 … BS-3 only read; every BS-4 attempt runs CL under the lock (or degraded) and cannot interleave with CP's attempt except in degraded mode | D R2 (f); D R5 (g) | — | — | — | A |
| `RT4.SN.1` | CN | Child surface of the backstop service in two tiers (§8.1). *Accepted today:* the DI-1 `systemctl show` children (BS-1 and the CL-2 / CL-6 reads), the DI-4 `systemctl stop` child at each of its three call sites (BS-2, BS-3, BS-4 terminal disarm), of which the BS-2 and BS-3 calls are **mutating** children whose effect is `unknown` after `error`, `interrupted` or abandon (SN-10; A-I-16); accepted text does not state that treatment for the BS-4 call, and whether it extends there is open (Q6-7) — and the DI-5 `pkcheck` and DI-6 `sleep` children of the CL-4 series. *LIT-FULL replacement:* the only retained child intent is the DI-6 subject of the CL-4 series (PC-1); the DI-1, DI-4 and DI-5 children are removed (PC-2, PC-5, PC-6) and are not children in the replacement root-procedure tree. *Carried, unmapped obligation:* the accepted `effect: "unknown"` obligation must still be honoured for the DI-4 interactions at BS-2 and BS-3 (and for the DI-3 call, `RT2.SN.1`); its mapping to a non-child loader-free interaction is the unanswered Q6-6, and WP-2 does not choose whether that interaction is realized in process, by a static child or by another admitted mechanism. Any child that exists is created, signalled, reaped or abandoned only through H-SN; a left-behind child's owner is PID 1's end of the backstop service (BS-RM or exit), then the boot | R8 §7.5a.7 table SN-RO; SN-10; A-I-16; R8 §7.5a.8 (last paragraph); §8.1 | 1,2,3,3a-3g | E, X, C | CS-7, CS-8, CS-10: the line in the attempt journal; CS-1 … CS-6, CS-9: the missing `run-end` ⇒ the next CL or `attest` records `children-unknown` | A;Q6-6;Q6-7 |
| `RT4.CLG` | CMP | CL-G (first act), trigger `backstop`: perform H-CL.G.1, H-CL.G.2, H-GRR.1 … H-GRR.8. The first act of each firing that reaches BS-4. | R8 §5.7 CL-G | 12,10,8 | see the helper rows | interruption: L0, L1 (IM-B (points of IM-L)); owner: the next firing of the backstop, else CP at a later start, then the boot, then `attest` | A |
| `RT4.CL0` | CMP | CL-0 (lock attempts to λ, attempt directory, journal, `run-start`, held `cl-g` line), trigger `backstop`: perform H-CL.0.1 … H-CL.0.6, H-LK.1 … H-LK.4, H-JRN.1 … H-JRN.7. For `backstop` record the parent PID and INVOCATION_ID as provenance (diagnostic only); run CL in degraded mode if K cannot be acquired; `k` beyond 99 or more than `backstop_max` firings ⇒ RT4.BS4.2. | D R2 (h) CL-0; R8 §8.1 | 6,7,10,11 | see the helper rows | interruption: L2 (IM-B (points of IM-L)); owner: the next firing of the backstop, else CP at a later start, then the boot, then `attest` | A |
| `RT4.CL1` | CMP | CL-1 (read journals, A-2 pins, H-1 record; boot scoping), trigger `backstop`: perform H-CL.1.1 … H-CL.1.3, H-JRN.8, H-JRN.9. | D R2 (h) CL-1; D R4 (g) | 8,9,10 | see the helper rows | interruption: L3 (IM-B (points of IM-L)); owner: the next firing of the backstop, else CP at a later start, then the boot, then `attest` | A |
| `RT4.CL2` | CMP | CL-2 (capture-unit state; attempt classification), trigger `backstop`: perform H-CL.2.1, H-CL.2.2, H-DI1.1 … H-DI1.4. | D R1 (e) CL-2 | 1,2,8,10 | see the helper rows | interruption: L3 (IM-B (points of IM-L)); owner: the next firing of the backstop, else CP at a later start, then the boot, then `attest` | A |
| `RT4.CL3` | CMP | CL-3 (classify the rule; remove if A1-intact), trigger `backstop`: perform H-CL.3.1, H-CL.3.2, H-GR1.1 … H-GR1.6. | D R1 (e) CL-3; R8 §8.1 | 8,9,10,11,12 | see the helper rows | interruption: L3 (IM-B (points of IM-L)); owner: the next firing of the backstop, else CP at a later start, then the boot, then `attest` | A |
| `RT4.CL4` | CMP | CL-4 (rule absent; PK/2 seek-not-authorized), trigger `backstop`: perform H-CL.4.1, H-CL.4.2, H-PK2.1 … H-PK2.7, H-PROC.1 … H-PROC.6, H-SN.1 … H-SN.16. | D R1 (e) CL-4; R8 §8.1 | 1,2,3,3a,3b,3c,3d,3e,3f,3g,4,14 | see the helper rows | interruption: L4 (IM-B (points of IM-L)); owner: the next firing of the backstop, else CP at a later start, then the boot, then `attest` | A |
| `RT4.CL5` | CMP | CL-5 (`pass-a.json`), trigger `backstop`: perform H-CL.5.1, H-CL.5.2, H-GR1.1 … H-GR1.6. | D R1 (e) CL-5 | 8,9,10,11,12 | see the helper rows | interruption: L5 (IM-B (points of IM-L)); owner: the next firing of the backstop, else CP at a later start, then the boot, then `attest` | A |
| `RT4.CL5b` | CMP | CL-5b (directories; `grant.id` and K last), trigger `backstop`: perform H-CL.5b.1, H-CL.5b.2, H-GR1.1 … H-GR1.6. | D R2 (h) CL-5b; R8 §8.1 | 8,10,11,12 | see the helper rows | interruption: L6 (IM-B (points of IM-L)); owner: the next firing of the backstop, else CP at a later start, then the boot, then `attest` | A |
| `RT4.CL6` | CMP | CL-6 (verify ST-1; baseline recomputation), trigger `backstop`: perform H-CL.6.1 … H-CL.6.4, H-BSE.1 … H-BSE.15, H-DI1.1. | D R2 (h) CL-6; R8 §8.1 | 1,8,9,10 | see the helper rows | interruption: L7 (IM-B (points of IM-L)); owner: the next firing of the backstop, else CP at a later start, then the boot, then `attest` | A |
| `RT4.CL7` | CMP | CL-7 (records; `run-end`; close K), trigger `backstop`: perform H-CL.7.1, H-CL.7.2, H-REC.1 … H-REC.4, H-PF.1 … H-PF.9. | D R2 (h) CL-7; R8 §8.1 | 6,8,9,11 | see the helper rows | interruption: L8, L9 (IM-B (points of IM-L)); owner: the next firing of the backstop, else CP at a later start, then the boot, then `attest` | A |
| `RT4.CLGP` | CMP | GP-R3 (grant-priority mode; entered on E-a, E-b, E-c), trigger `backstop`: perform H-CL.GP.1 … H-CL.GP.5. | D R3 (e) | 2,8,9,10,11,12,14 | see the helper rows | interruption: GP-R3 entry E-a/E-b/E-c; ST-1.ur (IM-B (points of IM-L)); owner: the next firing of the backstop, else CP at a later start, then the boot, then `attest` | A |
| `RT4.CLOUT` | CMP | Outcome rule and ST-1 mapping, trigger `backstop`: perform H-CL.OUT. | D R1 (e); D R2 (h) | — | see the helper rows | interruption: — (IM-B (points of IM-L)); owner: the next firing of the backstop, else CP at a later start, then the boot, then `attest` | A |

### 5.5 RT-5 — attest (CL, trigger `attest`; first act CL-G)

Caller: the executor / operator, interactive, `sudo -n`; no unit. Beginning boundary: the first design-controlled static image that `sudo -n` executes (BQ-2 answered B2-F by Peter; EX-1: `sudo` alone is a launch preamble outside the inventoried tree). Accepted failure contract: refuses to run CL while the holder or either backstop unit is `activating`, `active`, `deactivating` or `reloading`; otherwise as RT-3; records `cleared-by-boot` / `st1-verified` only if CL-4 and CL-6 hold; an interruption leaves records missing and every later RP-11 step refuses; no automatic owner for a left-behind child

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `RT5.FI.1` | EN | Instantiate H-FI for `attest`: the first image is the one `sudo -n` executes (installed tool by path in the accepted literal); operands: activation identifier, A-2 SHA-256 and the trigger `attest`; reads no environment variable; caller: the executor / operator, interactive, `sudo -n` to the first design-controlled image; no unit; under EX-1 `sudo` alone is the launch preamble outside the tree | R8 §9.6.1; R8 §9.2; H-FI | — | X | see H-FI | A;Q4-6 |
| `RT5.FI.2` | CN | Whole-life terminator: no enforcer: no PID-1 timer applies; an interruption leaves records missing and every later RP-11 step refuses | R8 §7.4; R8 §7.8 SG-8 | 22 | no enforcer | interruption map: IM-L points (trigger `attest`) and the owner table: no automatic owner; first owner: no automatic owner is claimed; the boot is a separate event; the executor reports the record or `children-unknown` and does not act | A |
| `RT5.PRE.1` | UA | `attest` precondition: DI-1 reads of `⟨activation_id⟩.service`, `⟨activation_id⟩-backstop.timer` and `⟨activation_id⟩-backstop.service`; none may be `activating`, `active`, `deactivating` or `reloading` (a unit that is `not-found`, `inactive` or `failed` does not block) | D R2 (i) Attest | 1 | E (c) per read today | any blocking state ⇒ `attest` does not run CL; the executor reports and does not act | A;Q3-1;Q4-7 |
| `RT5.PRE.2` | CN | `attest` disables nothing after a kernel boot (the grant ceased to exist when the kernel booted); in the same boot it is CL with its ordinary classes; in a later boot it finds nothing A1 under `/run` (CL-1 boot scoping) and removes nothing attributable; it records `cleared-by-boot` and `st1-verified` only if CL-4 and CL-6 hold | D R2 (i); D R3 (e) ST-1.ur mapping | — | — | — | A |
| `RT5.PRE.3` | CN | `attest` installs no signal handler (SG-8); it has no automatic owner for a left-behind child: the helper records `children` if it can, the executor reports the record or `children-unknown` and does not act; the boot is a separate event | R8 §7.8 SG-8; R8 §7.5a.7 table SN-RO, RO-7 | 22 | — | an interruption leaves records missing; the gate (H-2, AP-0, H-1R, RB-1 refuse) holds until a terminal `deact` record exists | A |
| `RT5.SN.1` | CN | Child surface of `attest` in two tiers (§8.1); the DI-3 and DI-4 calls are not made by `attest`. *Accepted today:* the DI-1 `systemctl show` children (the precondition and the CL-2 / CL-6 reads) and the DI-5 `pkcheck` and DI-6 `sleep` children of the CL-4 series. *LIT-FULL replacement:* the only retained child intent is the DI-6 subject of the CL-4 series (PC-1); the DI-1 and DI-5 children are removed (PC-2, PC-6). H-SN applies to any child that exists; no unit owns it | R8 §7.5a.7; R8 §7.5a.8 (last paragraph); §8.1 | 1,2,3,3a-3g | E, X, C | CS-7, CS-8, CS-10: the line; CS-1 … CS-6, CS-9: the missing `run-end` | A |
| `RT5.CLG` | CMP | CL-G (first act), trigger `attest`: perform H-CL.G.1, H-CL.G.2, H-GRR.1 … H-GRR.8. After a kernel boot K and `grant.id` are absent: GRR returns `identity-unavailable` and CL-3 uses the journal-based classification (boot scoping: every `/run` object of another boot is A0). | R8 §5.7 CL-G | 12,10,8 | see the helper rows | interruption: L0, L1 (IM-L points (trigger `attest`) and the owner table: no automatic owner); owner: no automatic owner is claimed; the boot is a separate event; the executor reports the record or `children-unknown` and does not act | A |
| `RT5.CL0` | CMP | CL-0 (lock attempts to λ, attempt directory, journal, `run-start`, held `cl-g` line), trigger `attest`: perform H-CL.0.1 … H-CL.0.6, H-LK.1 … H-LK.4, H-JRN.1 … H-JRN.7. `attest` records no parent PID or INVOCATION_ID provenance; its attempt number `k` follows the same count. | D R2 (h) CL-0; R8 §8.1 | 6,7,10,11 | see the helper rows | interruption: L2 (IM-L points (trigger `attest`) and the owner table: no automatic owner); owner: no automatic owner is claimed; the boot is a separate event; the executor reports the record or `children-unknown` and does not act | A |
| `RT5.CL1` | CMP | CL-1 (read journals, A-2 pins, H-1 record; boot scoping), trigger `attest`: perform H-CL.1.1 … H-CL.1.3, H-JRN.8, H-JRN.9. In a later boot CL-1 can find nothing A1 under `/run`: the rule and `pass-a.json` are classed `cleared-by-boot` when the four conditions hold (different `boot_id`, tmpfs observed, an identity line, `ENOENT`). | D R2 (h) CL-1; D R4 (g) | 8,9,10 | see the helper rows | interruption: L3 (IM-L points (trigger `attest`) and the owner table: no automatic owner); owner: no automatic owner is claimed; the boot is a separate event; the executor reports the record or `children-unknown` and does not act | A |
| `RT5.CL2` | CMP | CL-2 (capture-unit state; attempt classification), trigger `attest`: perform H-CL.2.1, H-CL.2.2, H-DI1.1 … H-DI1.4. | D R1 (e) CL-2 | 1,2,8,10 | see the helper rows | interruption: L3 (IM-L points (trigger `attest`) and the owner table: no automatic owner); owner: no automatic owner is claimed; the boot is a separate event; the executor reports the record or `children-unknown` and does not act | A |
| `RT5.CL3` | CMP | CL-3 (classify the rule; remove if A1-intact), trigger `attest`: perform H-CL.3.1, H-CL.3.2, H-GR1.1 … H-GR1.6. | D R1 (e) CL-3; R8 §8.1 | 8,9,10,11,12 | see the helper rows | interruption: L3 (IM-L points (trigger `attest`) and the owner table: no automatic owner); owner: no automatic owner is claimed; the boot is a separate event; the executor reports the record or `children-unknown` and does not act | A |
| `RT5.CL4` | CMP | CL-4 (rule absent; PK/2 seek-not-authorized), trigger `attest`: perform H-CL.4.1, H-CL.4.2, H-PK2.1 … H-PK2.7, H-PROC.1 … H-PROC.6, H-SN.1 … H-SN.16. | D R1 (e) CL-4; R8 §8.1 | 1,2,3,3a,3b,3c,3d,3e,3f,3g,4,14 | see the helper rows | interruption: L4 (IM-L points (trigger `attest`) and the owner table: no automatic owner); owner: no automatic owner is claimed; the boot is a separate event; the executor reports the record or `children-unknown` and does not act | A |
| `RT5.CL5` | CMP | CL-5 (`pass-a.json`), trigger `attest`: perform H-CL.5.1, H-CL.5.2, H-GR1.1 … H-GR1.6. | D R1 (e) CL-5 | 8,9,10,11,12 | see the helper rows | interruption: L5 (IM-L points (trigger `attest`) and the owner table: no automatic owner); owner: no automatic owner is claimed; the boot is a separate event; the executor reports the record or `children-unknown` and does not act | A |
| `RT5.CL5b` | CMP | CL-5b (directories; `grant.id` and K last), trigger `attest`: perform H-CL.5b.1, H-CL.5b.2, H-GR1.1 … H-GR1.6. | D R2 (h) CL-5b; R8 §8.1 | 8,10,11,12 | see the helper rows | interruption: L6 (IM-L points (trigger `attest`) and the owner table: no automatic owner); owner: no automatic owner is claimed; the boot is a separate event; the executor reports the record or `children-unknown` and does not act | A |
| `RT5.CL6` | CMP | CL-6 (verify ST-1; baseline recomputation), trigger `attest`: perform H-CL.6.1 … H-CL.6.4, H-BSE.1 … H-BSE.15, H-DI1.1. | D R2 (h) CL-6; R8 §8.1 | 1,8,9,10 | see the helper rows | interruption: L7 (IM-L points (trigger `attest`) and the owner table: no automatic owner); owner: no automatic owner is claimed; the boot is a separate event; the executor reports the record or `children-unknown` and does not act | A |
| `RT5.CL7` | CMP | CL-7 (records; `run-end`; close K), trigger `attest`: perform H-CL.7.1, H-CL.7.2, H-REC.1 … H-REC.4, H-PF.1 … H-PF.9. | D R2 (h) CL-7; R8 §8.1 | 6,8,9,11 | see the helper rows | interruption: L8, L9 (IM-L points (trigger `attest`) and the owner table: no automatic owner); owner: no automatic owner is claimed; the boot is a separate event; the executor reports the record or `children-unknown` and does not act | A |
| `RT5.CLGP` | CMP | GP-R3 (grant-priority mode; entered on E-a, E-b, E-c), trigger `attest`: perform H-CL.GP.1 … H-CL.GP.5. | D R3 (e) | 2,8,9,10,11,12,14 | see the helper rows | interruption: GP-R3 entry E-a/E-b/E-c; ST-1.ur (IM-L points (trigger `attest`) and the owner table: no automatic owner); owner: no automatic owner is claimed; the boot is a separate event; the executor reports the record or `children-unknown` and does not act | A |
| `RT5.CLOUT` | CMP | Outcome rule and ST-1 mapping, trigger `attest`: perform H-CL.OUT. | D R1 (e); D R2 (h) | — | see the helper rows | interruption: — (IM-L points (trigger `attest`) and the owner table: no automatic owner); owner: no automatic owner is claimed; the boot is a separate event; the executor reports the record or `children-unknown` and does not act | A |

### 5.6 SA-1 — `start` role — AP-2, creating the holder unit

Caller: the executor, privileged, under A-2. Beginning boundary: the first design-controlled static image that `sudo -n` executes (PD-2a = B2-F; PD-2b = in; EX-1). Accepted failure contract: a name already loaded makes the call fail and create nothing (PO-21 (m)); the executor then finds the unit not loaded ⇒ INVALID RUN, nothing mutated; a loaded unit means the holder governs; the call's own failure contract is not accepted text

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `SA1.FI.1` | EN | Instantiate H-FI for the `start` role (AP-2): the first design-controlled image is the one `sudo -n` executes; EX-1: `sudo` alone is the launch preamble outside the inventoried tree; the role reads no environment variable and receives `sudo`'s environment unclosed (an accepted consistency limit under OH-D-6, not an escalation) | AP (EX-1); W1 §9.1; W1 §6.1; R8 §9.2 RH-1; D R2 (e) | — | X | see H-FI | A;Q4-6 |
| `SA1.OP.1` | CN | Obtain the operands the accepted literal fixes: activation identifier, A-2 SHA-256, lease `L` (`RuntimeMaxSec=`), `S` (`TimeoutStopSec=`), the `stop-post` command line and the `hold` command line; the way a static image receives and validates them (argument grammar, length, class) is not accepted for LIT-FULL | D R2 (c),(e) (A-2 pins the literal and its SHA-256); W1 §10.2 FR-1 | — | X | a malformed operand is refused before any state operation | A;Q4-6 |
| `SA1.OP.2` | UA | DI-2: create one transient system service named `⟨activation_id⟩` of type `exec` carrying the accepted AP-2 properties — `Restart=no`, `OOMScoreAdjust=-1000`, `RuntimeMaxSec=⟨L⟩`, `TimeoutStopSec=⟨S⟩`, `ExecStopPost=` the `stop-post` role command, main command the `hold` role command — in one `StartTransientUnit`-equivalent call (today `sudo -n /usr/bin/systemd-run --system --no-ask-password --quiet --unit=⟨id⟩ --service-type=exec --property=… `); no environment, scope, user, terminal, wait or collect option; no `%`, `$`, `\` or quotation mark in the arguments; its only effect is the transient holder unit | D R2 (d) AP-2, (e); R8 §9.3 DI-2; W1 §7.4 (B2-F-A); R8 §8.1 AP-2 | — | X: no accepted class or bound for this call; `act_wait_s` (row 5) bounds the executor's later wait, not this call | a name already loaded makes the call fail and create nothing (PO-21 (m)); afterwards the executor (outside the set) checks the unit is loaded: not loaded ⇒ INVALID RUN, nothing mutated; loaded ⇒ the holder governs | A;Q3-2;Q4-7 |
| `SA1.OP.3` | XT | Return the call's result (success or failure) to the executor and exit; no signal is sent, no child is created, no record is written, no wait is made by the role | D R2 (d) AP-2; W1 §7.4 | — | X | the accepted text states no failure contract beyond the executor's check; any further contract is a design addition | A;Q4-11 |
| `SA1.OP.4` | CN | Not part of SA-1: the executor's wait of at most `act_wait_s` (60 … L, rec. L) for the `act` record or the holder's end, reading only records, journals and `systemctl show -p ActiveState,Result ⟨activation_id⟩.service` unprivileged (row 5, class E; expiry is HARD STOP `act-unconfirmed`, the executor acting on nothing); AP-0 … AP-1 (row 21) | R8 §7.3 rows 5, 21; D R2 (d) AP-2 | 5,21 | E (act_wait_s) | HARD STOP `act-unconfirmed` | A |

### 5.7 SA-2 — `stop` role — the OS-6 interruption

Caller: the executor, under A-2, only while OC-1, OC-2 and OC-3 hold. Beginning boundary: the first design-controlled static image that `sudo -n` executes (PD-2a = B2-F; PD-2b = in; EX-1). Accepted failure contract: a §9.5.3 interruption: no X-3 finalization, capture root retained read-only; if the condition cannot be established the route is unavailable and the pass continues without a grant (CX-3); the call's own failure contract is not accepted text

| ID | Cl | Operation intent | Source | §7.3 | Blocking / bound | Failure / interruption contract | Tag |
|---|---|---|---|---|---|---|---|
| `SA2.FI.1` | EN | Instantiate H-FI for the `stop` role (OS-6): the first design-controlled image is the one `sudo -n` executes; EX-1 as SA1.FI.1; the accepted literal has no operand or option other than the fixed unit name | AP (EX-1); D R4 (e) Literal; W1 §5.3 SA-2; W1 §9.1 | — | X | see H-FI | A;Q4-6 |
| `SA2.OP.1` | CN | Preconditions are the executor's, evaluated before the role runs and outside the set: the capture unit `ActiveState` is `active` (OC-1), its `InvocationID` equals the consume journal's `run-start.invocation_id` (OC-2), the journal contains `consumed` (OC-3); the executor reads `systemctl show -p ActiveState,InvocationID rp11-capture-pass-a.service` unprivileged and the consume journal (`root:root`, `0644`, readable by `ubuntu`); the route is unavailable in every other state; whether the role re-checks any of them is not stated | D R6 (b); W1 §5.3 SA-2 | 8,21 | X | if the condition cannot be established the route is unavailable and the pass continues without a grant (CX-3) | A;Q4-6 |
| `SA2.OP.2` | UA | Stop-unit call (the named stop function, no R8 DI row — a design addition): request the stop of exactly one unit, `rp11-capture-pass-a.service`, and no other; never to start, restart or reset it; today `sudo -n /usr/bin/systemctl stop rp11-capture-pass-a.service` | D R4 (e); D R6 (b); W1 §6.1 (*stop-unit call*); W1 §10.0 | — | X: no accepted class, bound or failure contract for this call | a §9.5.3 interruption: no X-3 finalization follows and the capture root is retained read-only; HL observes the unit's end within Δ and the holder ends; the stop call's own failure contract is not accepted text | A;Q3-7;Q4-7;Q4-11 |
| `SA2.OP.3` | XT | Return the call's result and exit; no signal, no child, no record, no wait by the role | D R4 (e); D R6 (b) | — | X | see SA2.OP.2 | A;Q4-11 |
| `SA2.OP.4` | CN | A stop during `start-pre` is not route (iii-a): it is a root act outside the authorized path set 𝒜 (CX-4); a hung consume step is ended only by the unit's finite start timeout (class M), never by this role; by Lemma R6 every `stop` this role issues lands after SB-1's blocking point | D R6 (b),(c),(d),(f) | 20 | M (T_s) | CX-4 residual outside 𝒜 | A |

## 6. Step trace: every accepted step to its rows

Each accepted step of each in-scope procedure is listed with the rows that realize it. A step without a row would be a defect; the check in §11.3 found none.

### RT-1

| Step | Accepted step | Source | Rows |
|---|---|---|---|
| FI | first-image state operations RH-1 … RH-3 and SG-8 (no handlers) | R8 §9.2; R8 §7.8 SG-8 | `RT1.FI.1`, `RT1.FI.2` |
| CQ0 | CQ-0 identify | D R5 (e) | `RT1.CQ0.1`, `RT1.CQ0.2`, `RT1.CQ0.3`, `RT1.CQ0.4`, `RT1.CQ0.5`, `RT1.CQ0.6` |
| CQ1 | CQ-1 activation lock | D R5 (e); R8 §8.1 | `RT1.CQ1.1`, `RT1.CQ1.2` |
| CQ2 | CQ-2 claim | D R5 (d),(e) | `RT1.CQ2.1`, `RT1.CQ2.2`, `RT1.CQ2.3`, `RT1.CQ2.4`, `RT1.CQ2.5`, `RT1.CQ2.6`, `RT1.CQ2.7`, `RT1.CQ2.8`, `RT1.CQ2.9`, `RT1.CQ2.10` |
| CQ3 | CQ-3 grant | D R5 (e) | `RT1.CQ3.1`, `RT1.CQ3.2`, `RT1.CQ3.3`, `RT1.CQ3.4`, `RT1.CQ3.5`, `RT1.CQ3.6`, `RT1.CQ3.7`, `RT1.CQ3.8`, `RT1.CQ3.9` |
| CQ4 | CQ-4 live and first attempt (OS-1, OS-4) | D R5 (e) | `RT1.CQ4.1`, `RT1.CQ4.2`, `RT1.CQ4.3`, `RT1.CQ4.4`, `RT1.CQ4.5`, `RT1.CQ4.6`, `RT1.CQ4.7`, `RT1.CQ4.8` |
| CQ5 | CQ-5 post-check | D R5 (e); R8 §8.1 | `RT1.CQ5.1`, `RT1.CQ5.2`, `RT1.CQ5.3` |
| CQ6 | CQ-6 consumed | D R5 (e) | `RT1.CQ6.1` |
| CQ7 | CQ-7 run-end, close K, exit 0 | D R5 (e); R8 §8.1 | `RT1.CQ7.1`, `RT1.CQ7.2`, `RT1.CQ7.3`, `RT1.CQ7.4` |
| SN | child contract (PK/2 subjects) | R8 §7.5, §7.5a | `RT1.SN.1` |

### RT-2

| Step | Accepted step | Source | Rows |
|---|---|---|---|
| FI | first-image state operations | R8 §9.2 | `RT2.FI.1` |
| SG1 | SG-1 … SG-9 signal discipline | R8 §7.8 | `RT2.SG1.1`, `RT2.SG1.2`, `RT2.SG1.3` |
| AM0 | AM-0 re-check, K, BSP, journal (`RT2.AM0.7` is the non-operative gap row for Q6-7; the other sixteen are operation rows) | D R2 (d); R8 §8.1; R8 §6.4 | `RT2.AM0.1`, `RT2.AM0.2`, `RT2.AM0.3`, `RT2.AM0.4`, `RT2.AM0.5`, `RT2.AM0.6`, `RT2.AM0.7`, `RT2.AM0.8`, `RT2.AM0.9`, `RT2.AM0.10`, `RT2.AM0.11`, `RT2.AM0.12`, `RT2.AM0.13`, `RT2.AM0.14`, `RT2.AM0.15`, `RT2.AM0.16`, `RT2.AM0.17` |
| AK1 | AK-1 backstop arming | D R2 (d),(f); R8 §8.1 | `RT2.AK1.1`, `RT2.AK1.2`, `RT2.AK1.3`, `RT2.AK1.4` |
| AM1 | AM-1 tree P | D R2 (d) | `RT2.AM1.1`, `RT2.AM1.2` |
| AM1R | AM-1R tree R | D R2 (d) | `RT2.AM1R.1` |
| AM1G | AM-1G grant.id | R8 §8.1 | `RT2.AM1G.1`, `RT2.AM1G.2`, `RT2.AM1G.3` |
| AM2 | AM-2 rule publication | D R2 (d) | `RT2.AM2.1`, `RT2.AM2.2`, `RT2.AM2.3`, `RT2.AM2.4`, `RT2.AM2.5`, `RT2.AM2.6` |
| AV1 | AV-1 verification and controls | D R1 (d); R8 §8.1 | `RT2.AV1.1`, `RT2.AV1.2`, `RT2.AV1.3`, `RT2.AV1.4` |
| AM3 | AM-3 act record | D R2 (d) | `RT2.AM3.1`, `RT2.AM3.2` |
| HS | `hold-start` | D R5 (c); R8 §8.1 | `RT2.HS.1`, `RT2.HS.2`, `RT2.HS.3` |
| HL | HL hold loop and OS-5 | D R2 (g); D R5 (g) | `RT2.HL.1`, `RT2.HL.2`, `RT2.HL.3`, `RT2.HL.4`, `RT2.HL.5`, `RT2.HL.6`, `RT2.HL.7`, `RT2.HL.8`, `RT2.HL.9`, `RT2.HL.10` |
| IGR | IGR, GRR, IGR-0 … IGR-3 | R8 §5.7 | `RT2.IGR.1`, `RT2.IGR.2`, `RT2.IGR.3`, `RT2.IGR.4`, `RT2.IGR.5` |
| END | holder end | R8 §7.8 SG-7 | `RT2.END.1` |
| SN | child contract | R8 §7.5a | `RT2.SN.1` |

### RT-3

| Step | Accepted step | Source | Rows |
|---|---|---|---|
| FI | first-image state operations and trigger | R8 §9.2 | `RT3.FI.1`, `RT3.FI.2` |
| CLG | CL-G | R8 §5.7 | `RT3.CLG` |
| CL0 | CL-0 | D R2 (h); R8 §8.1 | `RT3.CL0` |
| CL1 | CL-1 | D R1 (e); D R2 (h) | `RT3.CL1` |
| CL2 | CL-2 | D R1 (e) | `RT3.CL2` |
| CL3 | CL-3 | D R1 (e); R8 §8.1 | `RT3.CL3` |
| CL4 | CL-4 | D R1 (e); R8 §8.1 | `RT3.CL4` |
| CL5 | CL-5 | D R1 (e) | `RT3.CL5` |
| CL5b | CL-5b | D R2 (h); R8 §8.1 | `RT3.CL5b` |
| CL6 | CL-6 | D R2 (h); R8 §8.1 | `RT3.CL6` |
| CL7 | CL-7 | D R2 (h); R8 §8.1 | `RT3.CL7` |
| CLGP | GP-R3 | D R3 (e) | `RT3.CLGP` |
| CLOUT | outcome rule | D R1 (e) | `RT3.CLOUT` |
| SN | child contract | R8 §7.5a | `RT3.SN.1` |

### RT-4

| Step | Accepted step | Source | Rows |
|---|---|---|---|
| FI | first-image state operations and trigger | R8 §9.2 | `RT4.FI.1`, `RT4.FI.2` |
| BS1 | BS-1 | D R2 (f) | `RT4.BS1.1` |
| BS2 | BS-2 | D R2 (f) | `RT4.BS2.1`, `RT4.BS2.2` |
| BS3 | BS-3 | D R2 (f) | `RT4.BS3.1` |
| BS4 | BS-4 | D R2 (f); R8 §8.1 | `RT4.BS4.1`, `RT4.BS4.2` |
| BS | BS constraints | D R2 (f) | `RT4.BS.1` |
| CLG | CL-G | R8 §5.7 | `RT4.CLG` |
| CL0 | CL-0 | D R2 (h) | `RT4.CL0` |
| CL1 | CL-1 | D R2 (h) | `RT4.CL1` |
| CL2 | CL-2 | D R1 (e) | `RT4.CL2` |
| CL3 | CL-3 | D R1 (e) | `RT4.CL3` |
| CL4 | CL-4 | D R1 (e) | `RT4.CL4` |
| CL5 | CL-5 | D R1 (e) | `RT4.CL5` |
| CL5b | CL-5b | D R2 (h) | `RT4.CL5b` |
| CL6 | CL-6 | D R2 (h) | `RT4.CL6` |
| CL7 | CL-7 | D R2 (h) | `RT4.CL7` |
| CLGP | GP-R3 | D R3 (e) | `RT4.CLGP` |
| CLOUT | outcome rule | D R1 (e) | `RT4.CLOUT` |
| SN | child contract | R8 §7.5a | `RT4.SN.1` |

### RT-5

| Step | Accepted step | Source | Rows |
|---|---|---|---|
| FI | first-image state operations and trigger | R8 §9.2 | `RT5.FI.1`, `RT5.FI.2` |
| PRE | `attest` precondition and boot cases | D R2 (i) | `RT5.PRE.1`, `RT5.PRE.2`, `RT5.PRE.3` |
| CLG | CL-G | R8 §5.7 | `RT5.CLG` |
| CL0 | CL-0 | D R2 (h) | `RT5.CL0` |
| CL1 | CL-1 | D R2 (h) | `RT5.CL1` |
| CL2 | CL-2 | D R1 (e) | `RT5.CL2` |
| CL3 | CL-3 | D R1 (e) | `RT5.CL3` |
| CL4 | CL-4 | D R1 (e) | `RT5.CL4` |
| CL5 | CL-5 | D R1 (e) | `RT5.CL5` |
| CL5b | CL-5b | D R2 (h) | `RT5.CL5b` |
| CL6 | CL-6 | D R2 (h) | `RT5.CL6` |
| CL7 | CL-7 | D R2 (h) | `RT5.CL7` |
| CLGP | GP-R3 | D R3 (e) | `RT5.CLGP` |
| CLOUT | outcome rule | D R1 (e) | `RT5.CLOUT` |
| SN | child contract | R8 §7.5a | `RT5.SN.1` |

### SA-1

| Step | Accepted step | Source | Rows |
|---|---|---|---|
| FI | first-image state operations (EX-1) | AP; W1 §9.1 | `SA1.FI.1` |
| OP | operands, DI-2 call, return | D R2 (d),(e); W1 §7.4 | `SA1.OP.1`, `SA1.OP.2`, `SA1.OP.3`, `SA1.OP.4` |

### SA-2

| Step | Accepted step | Source | Rows |
|---|---|---|---|
| FI | first-image state operations (EX-1) | AP; W1 §9.1 | `SA2.FI.1` |
| OP | preconditions, stop-unit call, return | D R4 (e); D R6 (b) | `SA2.OP.1`, `SA2.OP.2`, `SA2.OP.3`, `SA2.OP.4` |

## 7. DI-1 … DI-6 and the stop-unit call: replacement-intent map

This is an **input list for WP-3**, not the loader-free interface contract. Each delegation that accepted text makes today (through a dynamic child) is mapped to the procedure/sub-role and the operation intent that must replace it. The interface that carries each intent, its request form, completion semantics and failure mapping are WP-3 questions (Q3-1 … Q3-9, Q3-11). Which of today's delegations are children, which are mutating, and which child intent the LIT-FULL replacement retains is stated once in §8.1.

| DI | Delegation | Today | Replacement intent (WP-2 statement) | Open obligations |
|---|---|---|---|---|
| DI-1 | unit-state read | today `systemctl show -p …` child of a root helper, run read-only; used by CQ-4 (OS-1, OS-4), AM-0, AK-1, `hold-start`, HL, BS-1, the `attest` precondition, CL-2, CL-6 and the baseline `unit` and `manager` keys | obtain named properties of one named unit, or of the manager, read-only; the values a static image needs are typed, not printed text | Q3-1, Q3-9, Q4-7, Q6-2 |
| DI-2 | create the holder unit | today `systemd-run --system … --unit=⟨id⟩ --service-type=exec --property=…` run under `sudo -n` | create one transient service unit with the AP-2 property set in one call; no other effect | Q3-2, Q4-7 |
| DI-3 | create the backstop timer and service | today `systemd-run … --on-active --on-unit-active …` at AK-1, a mutating child of the holder | create one transient timer and its service with the accepted properties. The call is mutating: the accepted obligation that its effect may be `unknown` after an error, an interruption or an indeterminate completion (SN-10, A-I-16) applies to it; its mapping to a non-child interaction is **not made here** | Q3-3, Q4-7, Q6-6 |
| DI-4 | disarm the backstop timer | today `systemctl stop ⟨id⟩-backstop.timer` at **three** logical call sites — BS-2, BS-3 and the BS-4 terminal disarm — each a `systemctl stop` child of the backstop service | request the stop of exactly the activation's own timer at each of the three call sites. SN-10 / A-I-16 state the `effect: "unknown"` obligation for the BS-2 and BS-3 calls; accepted text does not state it for the BS-4 terminal disarm, and whether it extends there is open (Q6-7). The mapping of the obligation to a non-child interaction is **not made here** | Q3-4, Q4-7, Q6-6, Q6-7 |
| DI-5 | authorization decision | today `pkcheck --action-id org.freedesktop.systemd1.manage-units --process …` for the DI-6 subject, as the PK/2 series at CQ-5, AV-1 and CL-4 | obtain a Polkit decision for the manage-units action for one subject identity; the decision is evidence of seek-not-authorized only | Q3-5, Q3-6, Q4-7 |
| DI-6 | authorization subject | today `sleep 60` created as a child with `ubuntu`'s credentials in its own session | one subject process with those credentials and a self-limited lifetime; see §8 | Q4-1, Q6-4 |
| DI-S | stop-unit call (SA-2); no R8 DI row | today `systemctl stop rp11-capture-pass-a.service` under `sudo -n` | request the stop of exactly one unit and never a start, restart or reset | Q3-7, Q4-11 |

### 7.1 DI call sites per procedure

**Unit of counting: logical accepted call sites.** A *logical accepted call site* is one invocation of a DI delegation that accepted text states as one act at one step or sub-step of one procedure. §7.1 counts nothing else: not operation rows, not composition rows. The rules are:

1. A step that reads several units or properties as one stated act is **one** site (AM-0 (i)'s three `LoadState` reads; the `attest` precondition's three reads). Acts that the accepted text states separately are separate sites even within one step (CQ-4's OS-4 and OS-1; CL-6's “not active” read and the baseline `unit` and `manager` reads).
2. A repetition is the same site: loop iterations (HL polls, the PK/2 schedule), retries (BSP), further firings (BS-4) and the same act re-run on an alternate path that a step defines by reference to another step's act (the OS-5 decision's re-observation, GP-R3's reuse of CL-4 and CL-6, CP's grant-priority use of CQ-5).
3. Each trigger instance of the shared cleanup (RT-3, RT-4, RT-5) is a separate procedure and has its own sites.
4. A DI-6 subject is created for every DI-5 call; the pair is two sites (CALL-DI5-n and CALL-DI6-n).
5. **Rows and sites are many-to-many and the tables say so.** A composition row (for example `RT3.CL6`) may implement more than one site; one operation row (`RT4.BS2.2`) may implement more than one site; one site may need more than one row. The “Implementing row(s)” and “Sharing” columns below state each case. The row lists of §7.2 and the matrix below are both derived from this table.

The table is the source of the matrix: 41 sites in all.

| Call site | DI | Procedure | Accepted step: the one act | Source | Implementing row(s) | Sharing |
|---|---|---|---|---|---|---|
| `CALL-DI1-01` | DI-1 | RT-1 | CQ-4 OS-4: holder `ActiveState` and `InvocationID` | D R5 (e) CQ-4 OS-4 | `RT1.CQ4.7` | — |
| `CALL-DI1-02` | DI-1 | RT-1 | CQ-4 OS-1: capture unit `ActiveState`, `InvocationID`, `InactiveEnterTimestampMonotonic` | D R5 (e) CQ-4 OS-1 | `RT1.CQ4.8` | — |
| `CALL-DI1-03` | DI-1 | RT-2 | AM-0 (i): `LoadState` of three units (one stated act, three unit reads) | D R2 (d) AP-0 row | `RT2.AM0.5` | one site, three reads |
| `CALL-DI1-04` | DI-1 | RT-2 | AM-0 (iii): capture-unit baseline under BSP (the BSP retries are this same site) | R8 §6.4 BSP; D R5 (c) | `RT2.AM0.12` | the BSP retry control rows `RT2.AM0.13` and `RT2.AM0.14` are not DI-carrying; the retries are this same site |
| `CALL-DI1-05` | DI-1 | RT-2 | AK-1: the backstop timer must be `active` | D R2 (d) AK-1 | `RT2.AK1.3` | — |
| `CALL-DI1-06` | DI-1 | RT-2 | AV-1 H-2b baseline recomputation: `unit` key | D R1 (d) AV-1; D 4.3.3 (a) | `RT2.AV1.2` composing `H-BSE.10` | `RT2.AV1.2` implements this site and CALL-DI1-07 |
| `CALL-DI1-07` | DI-1 | RT-2 | AV-1 H-2b baseline recomputation: `manager` key | D R1 (d) AV-1; D 4.3.3 (b) | `RT2.AV1.2` composing `H-BSE.11` | `RT2.AV1.2` implements this site and CALL-DI1-06 |
| `CALL-DI1-08` | DI-1 | RT-2 | `hold-start`: re-read while K is held | D R5 (c); R8 §6.7 | `RT2.HS.1` | — |
| `CALL-DI1-09` | DI-1 | RT-2 | HL observation (the OS-5 decision's re-observation under the lock is this same site run again) | D R2 (g); D R5 (g) | `RT2.HL.3`; re-run `RT2.HL.7` | — |
| `CALL-DI1-10` | DI-1 | RT-3 | CL-2: capture-unit state | D R1 (e) CL-2 | `RT3.CL2` composing `H-CL.2.1`, `H-DI1.1` | — |
| `CALL-DI1-11` | DI-1 | RT-3 | CL-6: capture unit not active | D R2 (h) CL-6 | `RT3.CL6` composing `H-CL.6.3` | `RT3.CL6` implements this site and the next two |
| `CALL-DI1-12` | DI-1 | RT-3 | CL-6 baseline recomputation: `unit` key | D R2 (h) CL-6; D 4.3.3 (a) | `RT3.CL6` composing `H-BSE.10` | `RT3.CL6` implements three sites |
| `CALL-DI1-13` | DI-1 | RT-3 | CL-6 baseline recomputation: `manager` key | D R2 (h) CL-6; D 4.3.3 (b) | `RT3.CL6` composing `H-BSE.11` | `RT3.CL6` implements three sites |
| `CALL-DI1-14` | DI-1 | RT-4 | BS-1: holder `ActiveState` | D R2 (f) BS-1 | `RT4.BS1.1` | — |
| `CALL-DI1-15` | DI-1 | RT-4 | CL-2: capture-unit state | D R1 (e) CL-2 | `RT4.CL2` composing `H-CL.2.1`, `H-DI1.1` | — |
| `CALL-DI1-16` | DI-1 | RT-4 | CL-6: capture unit not active | D R2 (h) CL-6 | `RT4.CL6` composing `H-CL.6.3` | `RT4.CL6` implements this site and the next two |
| `CALL-DI1-17` | DI-1 | RT-4 | CL-6 baseline recomputation: `unit` key | D R2 (h) CL-6; D 4.3.3 (a) | `RT4.CL6` composing `H-BSE.10` | `RT4.CL6` implements three sites |
| `CALL-DI1-18` | DI-1 | RT-4 | CL-6 baseline recomputation: `manager` key | D R2 (h) CL-6; D 4.3.3 (b) | `RT4.CL6` composing `H-BSE.11` | `RT4.CL6` implements three sites |
| `CALL-DI1-19` | DI-1 | RT-5 | `attest` precondition: three unit-state reads (one stated act) | D R2 (i) Attest | `RT5.PRE.1` | one site, three reads |
| `CALL-DI1-20` | DI-1 | RT-5 | CL-2: capture-unit state | D R1 (e) CL-2 | `RT5.CL2` composing `H-CL.2.1`, `H-DI1.1` | — |
| `CALL-DI1-21` | DI-1 | RT-5 | CL-6: capture unit not active | D R2 (h) CL-6 | `RT5.CL6` composing `H-CL.6.3` | `RT5.CL6` implements this site and the next two |
| `CALL-DI1-22` | DI-1 | RT-5 | CL-6 baseline recomputation: `unit` key | D R2 (h) CL-6; D 4.3.3 (a) | `RT5.CL6` composing `H-BSE.10` | `RT5.CL6` implements three sites |
| `CALL-DI1-23` | DI-1 | RT-5 | CL-6 baseline recomputation: `manager` key | D R2 (h) CL-6; D 4.3.3 (b) | `RT5.CL6` composing `H-BSE.11` | `RT5.CL6` implements three sites |
| `CALL-DI2-01` | DI-2 | SA-1 | AP-2: create the transient holder unit | D R2 (d) AP-2, (e); R8 §9.3 DI-2 | `SA1.OP.2` | — |
| `CALL-DI3-01` | DI-3 | RT-2 | AK-1: create the backstop timer and service | D R2 (d) AK-1, (f); R8 §9.3 DI-3 | `RT2.AK1.2` | — |
| `CALL-DI4-01` | DI-4 | RT-4 | BS-2: disarm after a `st1-verified` record | D R2 (f) BS-2; R8 §9.3 DI-4 | `RT4.BS2.2` | `RT4.BS2.2` defines the disarm operation and implements this site and CALL-DI4-02; `RT4.BS2.1` is only the BS-2 condition and carries no DI |
| `CALL-DI4-02` | DI-4 | RT-4 | BS-3: disarm after a `hard-stop` record with nothing further removable | D R2 (f) BS-3; R8 §9.3 DI-4 | `RT4.BS3.1` (decision and invocation), `RT4.BS2.2` (the disarm operation it invokes) | shares the disarm operation of `RT4.BS2.2` |
| `CALL-DI4-03` | DI-4 | RT-4 | BS-4 terminal disarm (`backstop_max` exceeded or `k` > 99) | D R2 (f) BS-4; R8 §8.1 BS-4 Δ2 | `RT4.BS4.2` | same call form as `RT4.BS2.2`; its own row; the SN-10 / A-I-16 obligation is not stated for this site (open, Q6-7) |
| `CALL-DI5-01` | DI-5 | RT-1 | CQ-5: PK/2 seek-not-authorized for `start` — the decision | D R5 (e) CQ-5; R8 §8.1 | `RT1.CQ5.2` (PK/2 inside, `H-PK2.4`, `H-PK2.5`) | — |
| `CALL-DI5-02` | DI-5 | RT-2 | AV-1 positive control: PK/2 seek-authorized for `start` — the decision | R8 §8.1 AV-1 | `RT2.AV1.3` (PK/2 inside, `H-PK2.4`, `H-PK2.5`) | — |
| `CALL-DI5-03` | DI-5 | RT-2 | AV-1 negative control: PK/2 first-decisive for `stop` — the decision | R8 §8.1 AV-1; D R4 (g) AR-7 | `RT2.AV1.4` (PK/2 inside, `H-PK2.4`, `H-PK2.5`) | — |
| `CALL-DI5-04` | DI-5 | RT-3 | CL-4: PK/2 seek-not-authorized for `start` — the decision | D R1 (e) CL-4; R8 §8.1 | `RT3.CL4` composing `H-PK2.4`, `H-PK2.5` | — |
| `CALL-DI5-05` | DI-5 | RT-4 | CL-4: PK/2 seek-not-authorized for `start` — the decision | D R1 (e) CL-4; R8 §8.1 | `RT4.CL4` composing `H-PK2.4`, `H-PK2.5` | — |
| `CALL-DI5-06` | DI-5 | RT-5 | CL-4: PK/2 seek-not-authorized for `start` — the decision | D R1 (e) CL-4; R8 §8.1 | `RT5.CL4` composing `H-PK2.4`, `H-PK2.5` | — |
| `CALL-DI6-01` | DI-6 | RT-1 | CQ-5: PK/2 seek-not-authorized for `start` — the subject created for it | D R5 (e) CQ-5; R8 §8.1 | `RT1.CQ5.2` (PK/2 inside, `H-PROC.1` … `H-PROC.5`) | paired with CALL-DI5-01 |
| `CALL-DI6-02` | DI-6 | RT-2 | AV-1 positive control: PK/2 seek-authorized for `start` — the subject created for it | R8 §8.1 AV-1 | `RT2.AV1.3` (PK/2 inside, `H-PROC.1` … `H-PROC.5`) | paired with CALL-DI5-02 |
| `CALL-DI6-03` | DI-6 | RT-2 | AV-1 negative control: PK/2 first-decisive for `stop` — the subject created for it | R8 §8.1 AV-1; D R4 (g) AR-7 | `RT2.AV1.4` (PK/2 inside, `H-PROC.1` … `H-PROC.5`) | paired with CALL-DI5-03 |
| `CALL-DI6-04` | DI-6 | RT-3 | CL-4: PK/2 seek-not-authorized for `start` — the subject created for it | D R1 (e) CL-4; R8 §8.1 | `RT3.CL4` composing `H-PROC.1`, `H-PROC.2`, `H-PROC.3`, `H-PROC.5` | paired with CALL-DI5-04 |
| `CALL-DI6-05` | DI-6 | RT-4 | CL-4: PK/2 seek-not-authorized for `start` — the subject created for it | D R1 (e) CL-4; R8 §8.1 | `RT4.CL4` composing `H-PROC.1`, `H-PROC.2`, `H-PROC.3`, `H-PROC.5` | paired with CALL-DI5-05 |
| `CALL-DI6-06` | DI-6 | RT-5 | CL-4: PK/2 seek-not-authorized for `start` — the subject created for it | D R1 (e) CL-4; R8 §8.1 | `RT5.CL4` composing `H-PROC.1`, `H-PROC.2`, `H-PROC.3`, `H-PROC.5` | paired with CALL-DI5-06 |
| `CALL-DIS-01` | DI-S | SA-2 | OS-6 `stop`: stop-unit call for `rp11-capture-pass-a.service` | D R4 (e); D R6 (b) | `SA2.OP.2` | — |

**Matrix (derived from the table above) [M].** A dash is an accepted absence: for instance `attest` makes no DI-3 or DI-4 call, RT-3 makes neither, and only RT-4 makes a DI-4 call.

| DI | RT-1 | RT-2 | RT-3 | RT-4 | RT-5 | SA-1 | SA-2 | Sites |
|---|---|---|---|---|---|---|---|---|
| DI-1 | 2 | 7 | 4 | 5 | 5 | — | — | 23 |
| DI-2 | — | — | — | — | — | 1 | — | 1 |
| DI-3 | — | 1 | — | — | — | — | — | 1 |
| DI-4 | — | — | — | 3 | — | — | — | 3 |
| DI-5 | 1 | 2 | 1 | 1 | 1 | — | — | 6 |
| DI-6 | 1 | 2 | 1 | 1 | 1 | — | — | 6 |
| DI-S | — | — | — | — | — | — | 1 | 1 |
| **All** | **4** | **12** | **6** | **10** | **7** | **1** | **1** | **41** |

**DI-4 reconciled.** DI-4 has three logical call sites, all in RT-4: BS-2 (CALL-DI4-01), BS-3 (CALL-DI4-02) and the BS-4 terminal disarm (CALL-DI4-03). They are carried by three operation rows — `RT4.BS2.2`, `RT4.BS3.1`, `RT4.BS4.2` — and `RT4.BS2.2` implements two of the three sites (BS-2, and BS-3 by delegation). §7.2, §8 (PC-5) and §11.3(c) use the same three sites and the same three rows.

**Reconciliation with the R1 return's §7.1 [M].** R1 counted operation rows whose DI column named a DI and did not define its unit. Under the logical-call-site unit the differences are exactly: DI-1 gains the baseline `unit` and `manager` reads at AV-1 (RT-2) and at CL-6 (RT-3, RT-4, RT-5) — two sites at each of four places, eight in all, which R1's §7.3 already named as DI-1 sites but its matrix did not count (RT-2 5 → 7; RT-3 2 → 4; RT-4 3 → 5; RT-5 3 → 5; RT-1 unchanged at 2); DI-4 in RT-4 becomes 3 (R1: 2; BS-3 had no row of its own in the count). DI-2, DI-3, DI-5, DI-6 and DI-S are unchanged.

### 7.2 Rows that carry each DI

Rows are listed by identifier; a row appears under every DI it carries. Helper rows are those the procedure rows compose.

- **DI-1**: `H-DI1.1`, `H-DI1.2`, `H-DI1.3`, `H-BSE.10`, `H-BSE.11`, `H-CL.2.1`, `H-CL.6.3`, `RT1.CQ4.7`, `RT1.CQ4.8`, `RT2.AM0.5`, `RT2.AM0.12`, `RT2.AK1.3`, `RT2.AV1.2`, `RT2.HS.1`, `RT2.HL.3`, `RT3.CL2`, `RT3.CL6`, `RT4.BS1.1`, `RT4.CL2`, `RT4.CL6`, `RT5.PRE.1`, `RT5.CL2`, `RT5.CL6` (`RT2.HL.7` re-runs the HL site; it is not a further site)
- **DI-2**: `SA1.OP.2`
- **DI-3**: `RT2.AK1.2`
- **DI-4**: `RT4.BS2.2` (the shared disarm operation: BS-2 and, by delegation, BS-3), `RT4.BS3.1` (BS-3 decision and invocation), `RT4.BS4.2` (BS-4 terminal disarm)
- **DI-5**: `H-PROC.5`, `H-PK2.4`, `H-PK2.5`, `H-CL.4.2`, `RT1.CQ5.2`, `RT2.AV1.3`, `RT2.AV1.4`, `RT3.CL4`, `RT4.CL4`, `RT5.CL4`
- **DI-6**: `H-PROC.1`, `H-PROC.2`, `H-PROC.3`, `H-PROC.5`, `H-CL.4.2`, `RT1.CQ5.2`, `RT2.AV1.3`, `RT2.AV1.4`, `RT3.CL4`, `RT4.CL4`, `RT5.CL4`
- **DI-S**: `SA2.OP.2`

### 7.3 DI-1 call sites that W1's site list omits (WP-2 additions)

W1's DI-1 site list omits several accepted DI-1 uses. They are recorded here as WP-2 additions so that WP-3 sizes the interface from the complete set. [M]

- `RT2.AM0.5` — AM-0 `LoadState` reads of the holder, the backstop timer and the backstop service (three reads).
- `RT5.PRE.1` — the `attest` precondition (three unit-state reads).
- `RT1.CQ4.7` and `RT1.CQ4.8` — CQ-4 OS-4 and OS-1.
- `H-BSE.10` and `H-BSE.11` — baseline reads of the capture unit and of the manager in AV-1 (H-2b) and CL-6, with explicit property lists.
- `RT2.HL.3` — the extra properties HL reads (`InactiveEnterTimestampMonotonic`, `Job`, `ExecMainStartTimestampMonotonic`).

All of these are call sites in the §7.1 table (CALL-DI1-01 … CALL-DI1-23); the baseline `unit` and `manager` reads are counted there at AV-1 and at each CL-6.

## 8. Process-creation classification

Every process-creation row is classified as either **(F)** a fork that continues in a static image or **(X)** an `execve` of a design-controlled static image. No row is an `execve` of a distribution program. Where the choice between (F) and (X) belongs to WP-3 or WP-4, the required intent and the later owner are recorded and no mechanism is chosen. The finding that no accepted function requires an `execve` of a distribution program is the basis of the stop-rule result in §15.

| # | Process-creation intent | Procedure / sub-role | Row | Today | Classification | Owner of the mechanism |
|---|---|---|---|---|---|---|
| PC-1 | DI-6 authorization subject (one per authorization call) | RT-1.PK, RT-2.AV1, RT-3/4/5.CL-4 | `H-PROC.1`, `H-PROC.2`, `H-PK2.3` | `sleep 60`, a dynamic distribution program, created as a child with `ubuntu`'s credentials | (F) or (X): a fork continuing in a static image, or an `execve` of a design-controlled static image; credentials set by the creation primitive's own arguments; no distribution program | WP-4 (Q4-1); WP-6 (Q6-4) for the subject's accepted properties |
| PC-2 | DI-1 unit-state read child | every procedure that reads a unit | `H-DI1.1` | `systemctl show -p …` | **removed**: no process-creation row remains; replaced by the DI-1 intent (not a process-creation intent unless WP-3 chooses a child, in which case it must be (F) or (X)) | WP-3 (Q3-1) |
| PC-3 | DI-2 creation child (`start`) | SA-1 | `SA1.OP.2` | `systemd-run` under `sudo -n` | **removed** as a child of the static `start` role; the role itself is the first design-controlled static image after `sudo` (EX-1) | WP-3 (Q3-2) |
| PC-4 | DI-3 creation child | RT-2.AK1 | `RT2.AK1.2` | `systemd-run` (timer and service) | **removed**; replaced by the DI-3 intent | WP-3 (Q3-3) |
| PC-5 | DI-4 disarm child (three logical call sites: BS-2, BS-3, BS-4 terminal disarm; §7.1) | RT-4.BS2, BS3, BS4 | `RT4.BS2.2` (BS-2 and, by delegation, BS-3), `RT4.BS3.1` (BS-3), `RT4.BS4.2` (BS-4) | `systemctl stop ⟨id⟩-backstop.timer` | **removed**; replaced by the DI-4 intent at each of the three call sites | WP-3 (Q3-4); the `unknown`-effect obligation at BS-2 and BS-3: WP-6 (Q6-6); whether it extends to BS-4: WP-6 (Q6-7) |
| PC-6 | DI-5 decision child | RT-1.PK, RT-2.AV1, RT-3/4/5.CL-4 | `H-PK2.4` | `pkcheck` | **removed**; replaced by the DI-5 intent | WP-3 (Q3-5, Q3-6) |
| PC-7 | stop-unit call child (`stop`) | SA-2 | `SA2.OP.2` | `systemctl stop rp11-capture-pass-a.service` under `sudo -n` | **removed** as a child; the role itself is the first design-controlled static image after `sudo` (EX-1) | WP-3 (Q3-7) |
| PC-8 | First image of each PID-1-started procedure (hold, deact, backstop, consume) | RT-1 … RT-4 | `H-FI.1`, `RT1.FI.1`, `RT2.FI.1`, `RT3.FI.1`, `RT4.FI.1` | `python3.12 -I -S …/rp11_h1.py ⟨role⟩` (refuted for root roles, X-1) | (X) an `execve` by PID 1 of a design-controlled static image; this is PID 1's act, not a child of a helper, and is the beginning boundary | WP-4 (Q4-6) for the image architecture |
| PC-9 | `sudo` launch preamble (RT-5, SA-1, SA-2) | RT-5, SA-1, SA-2 | — | `sudo -n …` | outside the inventoried tree: the single LR-2 exception (EX-1); nothing else | none (accepted exception) |
| PC-10 | Baseline-acquisition commands (host, operator, repository, packages, citations, launcher, files, directories keys) | H-BSE | `H-BSE.1` … `H-BSE.15` | `uname`, `sha256sum`, `id`, `getent` class commands inside H-0 / the tool; the mechanism inside the tool is not stated for some keys | **not classified here**: the accepted text states only the facts compared, not how a static image would obtain them. Each must end as an in-process read, an (F) fork or an (X) `execve` of a design-controlled image; never a distribution program. Flagged for the reviewer (§15). | WP-3 (Q3-11), WP-6 (Q6-2, Q6-3) |

No accepted function was found to require an `execve` of a distribution program (§15). The only unresolved edge is PC-10, carried as questions and not as a HARD STOP.

The unit of counting in this section is the **process-creation intent** (PC-1 … PC-10). It is neither the operation row nor the logical call site of §7.1: one intent can span several call sites (PC-5 spans three), and one call site can relate to more than one intent.

### 8.1 Child surface: accepted today and the LIT-FULL replacement

This table separates the dynamic-child behavior that accepted text records for **today's** root procedures from the child set the **LIT-FULL replacement** retains. It is the single statement the SN rows (`RT1.SN.1`, `RT2.SN.1`, `RT3.SN.1`, `RT4.SN.1`, `RT5.SN.1`) and `H-SN.1` refer to. It chooses no mechanism.

| Delegation | Child today (accepted text) | Mutating, SN-10 | Child retained in the LIT-FULL replacement | Does the H-SN contract govern a replacement child | Obligation carried and not answered |
|---|---|---|---|---|---|
| DI-1 | `systemctl show -p …`, read-only | no | none (PC-2 removed) | no child to govern | Q3-1, Q3-9, Q4-7 |
| DI-2 | `systemd-run` run under `sudo -n` by the executor; not a child of a root-helper image (EX-1: `sudo` alone is outside the tree) | not named by SN-10 | none (PC-3 removed) | no child to govern | Q3-2, Q4-7 |
| DI-3 | `systemd-run` child of the holder at AK-1 | **yes** | none (PC-4 removed) | no child to govern | Q3-3, Q4-7; **Q6-6** (the `unknown`-effect obligation) |
| DI-4 | `systemctl stop ⟨id⟩-backstop.timer` child of the backstop service at BS-2, BS-3 and the BS-4 terminal disarm | **yes at BS-2 and BS-3** (SN-10 names those two calls); **not stated for the BS-4 terminal disarm** (open, Q6-7) | none (PC-5 removed) | no child to govern | Q3-4, Q4-7; **Q6-6** (the `unknown`-effect obligation, at BS-2 and BS-3); Q6-7 (BS-4) |
| DI-5 | `pkcheck` child inside the PK/2 series | no | none (PC-6 removed) | no child to govern | Q3-5, Q3-6, Q4-7 |
| DI-6 | `sleep 60` subject, one per authorization call | no | **retained creation intent** (PC-1): (F) or (X), never a distribution program | **yes**: SN-1 … SN-10 and SI-1 … SI-4 apply unchanged (R8 §7.5a.8, last paragraph) | Q4-1, Q4-8, Q6-4 |
| DI-S | `systemctl stop rp11-capture-pass-a.service` under `sudo -n` by the executor; not a child of a root-helper image | not named by SN-10 | none (PC-7 removed) | no child to govern | Q3-7, Q4-7, Q4-11 |

**The SN-10 / A-I-16 obligation is preserved and carried unmapped.** Accepted text requires that the effect of a mutating operation may be `unknown` after an `error`, an interruption or an indeterminate completion, and that no later step may read the result as “not created” or “not stopped”. Accepted text states this for the DI-3 call (AK-1) and the DI-4 calls at BS-2 and BS-3 **as children**; it does not state it for the BS-4 terminal disarm (Q6-7). Their removal as children does not remove the obligation; how it maps to a non-child loader-free interaction is the unanswered **Q6-6**, and WP-2 invents no mapping. WP-2 does not choose whether a later package realizes a loader-free interaction in process, by a static child or by another admitted mechanism. If a later design chooses a child, BQ-4 still requires (F) or (X) and never a distribution executable, and the applicable child contract (the H-SN contract) must then be mapped by that later package. Until then the DI-3 and DI-4 children are **historical behavior**, not part of the replacement root-procedure tree, and the H-SN contract is part of the replacement contract only for DI-6 subjects.

## 9. SN-I-1 … SN-I-4, SN-4 and the reap surface, traced

This section traces the complete signal-sending, validation, reap and wait surface represented by R8 §7.3 rows 3a … 3g. The operation rows are `H-SN.1` … `H-SN.16` and the PK/2 rows in §4; the tables below record the accepted consequences for WB, RE, GD and the child state at every point, without summary. They record the accepted contract for **any** child of a root image. Which children the LIT-FULL replacement retains is stated in §8.1: only the DI-6 subject (PC-1); the DI-1 … DI-5 and stop-unit children are today's behavior and are not replacement children.

### 9.1 Send identifiers (SN-I-1 … SN-I-4)

| ID | Send | Trigger | Signal | Target | Callers (LIT-FULL residue) |
|---|---|---|---|---|---|
| SN-I-1 | the initial group-directed termination | an E wait's deadline c expired, or the flag was observed during an E wait | `SIGTERM` | the process group of that wait's child | every child wait of the seven procedures (in LIT-FULL only waits that cover a child process: PK/2 subjects) |
| SN-I-2 | the escalation | the child is still unreaped and valid after SN-I-1's send or its failure (S4) | `SIGKILL` | the same group | the same |
| SN-I-3 | the termination of the PK subject | a PK call finished, with any result | `SIGKILL` | the subject's process group | PK/2 in RT-1 (CQ-5), RT-2 (AV-1), RT-3/4/5 (CL-4, GP-R3) |
| SN-I-4 | any signal used by cleanup or recovery | — | none | — | IGR, GRR, CL-G, the handlers, CQ-0 … CQ-7, CL-1 … CL-7, BS-1 … BS-4, SA-1, SA-2, `attest` send no signal except SN-I-1 … SN-I-3 inside a child wait |

### 9.2 Result table SN-R (rows 1 … 12)

| # | Condition at the call | Recorded result | What the helper does next | WB / RE / GD / child-state consequence |
|---|---|---|---|---|
| 1 | call returns 0 | `sent` | S3 (after `SIGTERM`: one reap attempt, then if `now < t_g` one capped sleep, then S4) or S5 (after `SIGKILL`) | not exit, reaping or absence; a raising attempt ⇒ S8 (WB-5 (e), RE-1) |
| 2 | `ESRCH` while the child is unreaped | `esrch` (anomaly `esrch-while-unreaped`) | as row 1; never read as "gone"; S4 still sends `SIGKILL` once if the child is still unreaped after a normal S3 | a raising attempt ⇒ S8, no `SIGKILL` |
| 3 | handle `reaped` before SN was entered | no call: `not-sent(reaped)` | S1-a ⇒ S7, never S5 | settled-state decision was RA-3 of the enclosing poll; T6/T7, CS-5/CS-7; GD-6: no S0, no clock read, no new line |
| 4 | `EPERM` | `eperm` (anomaly `eperm-from-root`) | after `SIGTERM`: one reap attempt, then S4 at once with no timed wait; after `SIGKILL`: S5 (capped sleeps while `t_g` not reached, final attempt), then abandon; no other mechanism (SN-5) | WB-3: no timed wait begins at or after `t_g` |
| 5 | `EINVAL`, `EINTR` or any other errno, or `OSError` without errno | `errno:⟨n⟩` (anomaly `send-error`) | as row 4; no retry (SN-3) | the error starts no grace period (WB-7) |
| 6 | exception that is not `OSError`, or the primitive unavailable | `exception:⟨class⟩` | as row 4; caught inside SN, never reaches the body | WB-7 |
| 7 | SN-4 (ii), (iii) or (iv) fails | `not-sent(identity-mismatch)` | no send of either signal; S1-b ⇒ S5; abandon, or S8 if an attempt raises | CS-2 / CS-3 (T1, T5, T5 cells) |
| 8 | handle `identity-unverifiable`, or `/proc` unreadable | `not-sent(identity-unverifiable)` | as row 7 | as row 7 |
| 9 | handle `abandoned`, `reap-unknown`, or `reaped` as in row 3 | `not-sent(abandoned)` / `not-sent(reap-unknown)` / `not-sent(reaped)` | no call, no wait; S1-a ⇒ S7 | INV-25: no `not-sent` is followed by a send |
| 10 | a send or its validation returns at or after `t_g` | recorded with `late: true` | every later timed wait skipped (WB-3); one reap attempt; `SIGKILL` once if unreaped and valid (S4, not a wait, WB-4); final attempt; abandon | `SIGTERM` and `SIGKILL` may be sent back to back; accepted |
| 11 | helper ends inside the call or before recording | none (lost with the helper) | not a helper action | cell of the matrix (outcome x); nothing inferred |
| 12 | a reap attempt raises (S3, S5, final attempt, or a poll of the enclosing wait) | no send result; anomaly `reap-error` | S8: `reap-unknown`; no further send of any kind, no attempt, no sleep; record; enclosing fail-closed result | RE-1 … RE-6; before S0 no `t_g` exists (GD-1 … GD-3): `s0_ran` false, `grace_deadline_ms` null, `outcome: "reap-error"` |

### 9.3 Interruption points of a helper inside SN (T0 … T7, T3k, T3x, T5k, T5x)

| Point | The helper is ended at | Notes (accepted text) |
|---|---|---|
| T0 | the trigger (deadline c, flag, or a finished PK call) is decided; `t_g` not yet read; handle `running` | a settled handle is never at T0 (CC-23) |
| T1 | S0 done, S1 validating a `running` handle or having rejected it (S1-b); no `SIGTERM` call yet (PK subject: no `SIGKILL` call yet) | a settled handle at S1-a is at T6, not T1 |
| T2 | S2: inside the `SIGTERM` call, or after it returned and before S3 | |
| T3 | S3 while the direct child is not reaped in the kernel (RA-0, RA-1, the capped sleep, between attempts) | |
| T3k | S3 inside a reap attempt at RA-2 (kernel has reaped; handle still `running`) | CS-5 |
| T3x | S3 inside a reap attempt at RA-E (the attempt raised; S8 has not set `reap-unknown`) | CS-9 |
| T4 | S4: the second validation, inside the `SIGKILL` call, or after it returned | |
| T5 | S5 while the direct child is not reaped in the kernel (loop, final attempt's RA-0/RA-1 included) | |
| T5k | S5 inside a reap attempt at RA-2 | CS-5 |
| T5x | S5 inside a reap attempt at RA-E | CS-9 |
| T6 | the sequence has decided (state set to `reaped` at RA-3, to `abandoned` at S6 or to `reap-unknown` at S8) or the handle was already settled when SN was entered; the `child` line is not yet durable | never the interior of an attempt (RB-4) |
| T7 | the `child` line is durable; the enclosing operation has not returned | |

### 9.4 Child states CS-1 … CS-10

| State | Sends already attempted (history) | Direct child | Record that survives |
|---|---|---|---|
| CS-1 | none | alive, or exited and unreaped | none |
| CS-2 | none; validation rejected | as CS-1 | none |
| CS-3 | `SIGTERM` attempted; `SIGKILL` not attempted | alive or exited-unreaped; may be acting on the signal (not known) | none |
| CS-4 | a `SIGKILL` attempted (after `SIGTERM`, or alone for a PK subject) | as CS-3 | none |
| CS-5 | any of the above | reaped in the kernel by the helper's own wait; the handle may still say `running` (RA-2) or `reaped` held in memory (RA-3) | none (line not durable) |
| CS-6 | any of the above | abandoned (unreaped at the final attempt) | none (abandon decided, line not durable) |
| CS-7 | any of the above | reaped in the kernel and recorded (RA-4) | durable `child` line, `reaped: true` |
| CS-8 | any of the above | abandoned | durable line, `abandoned: true` |
| CS-9 | as attempted; none after the error | not known (unreaped, or reaped with PID/group number possibly released) | none |
| CS-10 | as CS-9 | not known | durable line, `reap_unknown: true`, `send_suppressed: true`, `reaped: false`, `abandoned: false` |

### 9.5 Point × send-history matrix

| Point | u | i | x | s | e | f |
|---|---|---|---|---|---|---|
| T0 | CS-1 | — | — | — | — | — |
| T1 | CS-1 | CS-2 | — | — | — | — |
| T2 | — | — | CS-3 | CS-3 | CS-3 | CS-3 |
| T3 | — | — | — | CS-3 | CS-3 | CS-3 |
| T3k | — | — | — | CS-5 | CS-5 | CS-5 |
| T3x | — | — | — | CS-9 | CS-9 | CS-9 |
| T4 | CS-3 (PK: CS-1) | CS-3 (PK: CS-2) | CS-4 | CS-4 | CS-4 | CS-4 |
| T5 | — | CS-2 (S1 rejected, or a PK subject's S4 rejected) or CS-3 (S4 rejected after a `SIGTERM`) | — | CS-4 | CS-4 | CS-4 |
| T5k | — | CS-5 | — | CS-5 | CS-5 | CS-5 |
| T5x | — | CS-9 | — | CS-9 | CS-9 | CS-9 |
| T6 | CS-5 if reaped, CS-6 if abandoned, CS-9 if `reap-unknown` | same | — | as `i` | as `i` | as `i` |
| T7 | CS-7 / CS-8 / CS-10 | same | — | as `i` | as `i` | as `i` |

Outcome codes: u unmade (also a settled handle's `not-sent(reaped|abandoned|reap-unknown)` at T6, T7); i identity-rejected; x indeterminate (helper ended inside the call); s `sent`; e `ESRCH`; f failed. A dash is a combination the sequence cannot reach (R8 §7.9).

Reading rules (accepted): a send is `sent`, `esrch`, `eperm` or another recorded result and is never read as exit, reaping or absence; `ESRCH` while the child is unreaped is an anomaly (`esrch-while-unreaped`); no wait begins at or after `t_g`; there is no restarted grace period and no class-X time bound; a `reap-error` yields `reap-unknown` with suppression of all later sends; `t_g` exists exactly when S0 ran (GD-1 … GD-6). [A]

## 10. Interruption maps, terminal causes and residuals

### 10.1 IM-L — the helper (CL) interruption points

| Point | Interrupted at | State | Grant | First owner |
|---|---|---|---|---|
| L0 | process start, K open, `grant.id` read, GRR-2 or GRR-3, before the removal | ST-1.i | G1 inert (IL) | the backstop's CL (if armed and spawnable), else CP at a later start |
| L1 | after the removal, before CL-0 finishes (no attempt journal yet) | rule absent, nothing recorded | G2 | the backstop's CL (classes the rule `absent-before-removal`) |
| L2 | during CL-0: lock attempts, attempt directory, journal | a partial attempt directory may exist; `k` counts it | G2 | the backstop's CL as attempt `k + 1` |
| L3 | after CL-0, before CL-3's record | `run-start` present, no classification line | G2 | the backstop's CL |
| L4 | during CL-4's PK series, or after it before its record | rule absent, `removed-verified` not recorded; a PK child or subject in flight is left to IM-S | G2 (G3 not recorded) | the backstop's CL re-runs CL-4 |
| L5 | during CL-5: `remove-intent` for `pass-a.json` written, removal perhaps done | ST-1.d1 | G3 if CL-4 recorded it, else G2 | the backstop's CL-5 classes `removed-earlier` / `absent-before-removal` |
| L6 | during CL-5b | partial `/run` objects: class S0 | as L5 | the backstop's CL-5b, else the boot |
| L7 | after CL-5b, during CL-6 (reads, the baseline recomputation, unit read) | everything removed; `st1-verified` not recorded | G3 | the backstop's CL re-verifies; or `attest` |
| L8 | during CL-7, record publication | publication is atomic: a record is absent or complete; the journal lacks `run-end`; ST-1.ur if no `deact` record exists | G3 | the backstop writes the record; or `attest` |
| L9 | after `run-end` | complete | G3 | none |

### 10.2 IM-I — the inline grant release (IGR)

| Point | Interrupted at | State | Grant | First owner |
|---|---|---|---|---|
| I0 | before GRR-2 (flag observed, nothing done) | ST-1.i | G1 inert | stop-post CL (CL-G); else the rungs of L0 |
| I1 | GRR-3 verification (open, `fstat`, hash, extended-attribute names) | ST-1.i | G1 inert | as I0 |
| I2 | after the removal, before the directory flush or the `igr` line | rule absent, unattributed | G2 | stop-post CL classes it `absent-before-removal` |
| I3 | after the `igr` line is durable | rule absent, attributed | G2 | stop-post CL: `removed-earlier`, then CL-4 |
| I4 | the `igr` line's flush stalls | as I2 or I3 | G2 | RO-6 for the evidence; the grant is already gone |

### 10.3 IM-C, IM-B and IM-A

IM-C (CP): the start timeout T_s or any kill ends CP. Before CQ-2 no claim exists and the rule stays live (G1); the attempt ends `failed`; SB-2 refuses every later attempt; HL ends `start-failed-before-exec`; IGR or CL removes the rule first. After CQ-2 the claim exists (SB-1). After CQ-3's removal and before `removed` the rule is absent and CL classes it `absent-before-removal`. During CQ-5 the rule is gone (G2), no `consumed` line exists and `ExecStart=` is never executed. After `consumed` and before CQ-7 the attempt is recorded `start-failed-before-exec`. T_s is class M and CP's own elapsed time is not claimed; CP installs no handler (SG-8). The full per-point table of D §4.2.5-R5 (i) (events K/T, S, C, M, L, EO, EU against each CQ point; every cell ends without `ExecStart=`) is accepted text and is the interruption contract of rows RT1.CQ0 … RT1.CQ7.

IM-B (a backstop firing): BS-RM sends `SIGTERM` at S_b and `SIGKILL` after S; the points are those of IM-L; after the service ends the timer re-arms and fires again, at most B times; without BS-RM a hung firing prevents every later one (RO-5).

IM-A (the holder, ACT and HL): termination at a point leaves the objects built so far. Before SG-1 and AM-0: none. After K and before the journal: K only (S0). AK-1: ST-1.a0. AM-1: ST-1.a1 (tree P). Between the `grant.id` write and the link: `grant.id` and tree P, no rule. After the link (ST-1.a2, ST-2): G1, removed by IGR if the end is catchable and reached, else by RL-1 … RL-4. After CP's CQ-3 (ST-3): no grant. Each continues to CL as in D §4.2.5-R2 (k) and R8 §8.3.

### 10.4 Terminal causes of the holder's end

| # | Cause of the holder's end | Catchable | First removing rung | Residual (accepted) |
|---|---|---|---|---|
| 1–3 | HL's normal end; `observation-failed`; unhandled exception / `SystemExit` | yes | IGR (RL-0), then stop-post (RL-1) | none beyond G2 → G3 by CL |
| 4, 7 | `SIGTERM` from a stop job; `SIGINT`, `SIGHUP`, `SIGQUIT`, `SIGUSR1`, `SIGUSR2`, `SIGALRM` | yes | IGR at the next flag check; RL-1 | as above |
| 5 | `RuntimeMaxSec=` expiry (`SIGTERM`, then `SIGKILL` after S) | the first yes, the second no | IGR at `SIGTERM`; no promise before `SIGKILL` | RL-1 … RL-3 |
| 6 | orderly shutdown / reboot / `kexec` (outside 𝒜) | yes | IGR; RL-1 | G0 after the boot |
| 8, 9, 11 | `SIGKILL`; fatal interpreter signal or other default-terminating signal; user-space OOM kill | no | RL-1 if PID 1 can spawn it; RL-2; RL-3 at a start; boot | G1 live inert (IL) until a rung acts (RO-1 when both spawns fail) |
| 10 | kernel OOM kill | excluded by `OOMScoreAdjust=-1000` | n/a | not applicable |
| 12 | the holder never started (first image missing / not executable) | n/a | n/a | no grant was ever linked |
| 13 | PID 1 cannot spawn `ExecStopPost=` (`resources`) | any | IGR if catchable; RL-2 if PID 1 can spawn it | catchable: G2 then G3 by RL-2; uncatchable: live inert, RO-1 |
| 14, 15 | power loss, panic, hard reset; PID 1 dead or hung | no / n/a | boot clears `/run` | G0 after the boot; attestation records it; outside any unit guarantee |
| 16, 17 | a second termination signal while IGR runs; `SIGKILL` during IGR | yes / no | the handler sets the flag only; GRR is not interrupted / the IM-I point | per IM-I |
| 18 | uninterruptible stall of the holder | n/a | none until the stall ends | RO-6; IL holds while the holder is not `active` |
| 19, 20 | a catchable end while a child is in CS-1 … CS-10; `SIGKILL` of the holder at any SN point | yes / no | as the row of the end | the child may remain alive; owner = PID 1's stop of the unit then the boot; RO-7 |

### 10.5 Accepted residuals (RO-1 … RO-7, CX-1 … CX-5 and others)

| ID | Residual (accepted) |
|---|---|
| RO-1 | uncatchable holder end while PID 1 can spawn neither stop-post nor the backstop: pre-pass, inert grant (IL) until the backstop, a CP at a start, or the boot |
| RO-2 | helper bytes damaged after ACT: RL-1 and RL-2 fail together; IGR unaffected; prior tamper is detected by AP-0, H-2, AM-0 |
| RO-3 | PID 1 dead or hung: outside every unit guarantee |
| RO-4 | IGR not completed (killed or stalled before the removal) |
| RO-5 | a started backstop firing without BS-RM has no PID-1 bound (closed by BS-RM) |
| RO-6 | a persistent stall of a filesystem or the kernel delays every rung that touches `ext4` |
| RO-7 | a child left behind by its helper may be alive (or reaped with nothing recording it, CS-5; or not known, CS-9/10); owned by the owner of the enclosing procedure; `attest` has no automatic owner |
| CX-1 | a holder end racing with a start (narrowed: only the holder's own death or lease expiry after CQ-4); no grant; CL ends `unit-still-active` |
| CX-2 | a failed attempt that did not complete CQ-3 leaves a pre-pass grant until the activation ends |
| CX-3 | interruption needs the executor; if the OC-1 … OC-3 condition cannot be established the pass runs to its end without a grant |
| CX-4 | a stop job during the first attempt's `start-pre` from an act outside 𝒜 (a non-route root `stop` or a forbidden orderly transition) combined with PO-21 (u), τ₀ = 0 and an unload; no grant exists during or after a pass even then |
| CX-5 | τ₀ = 0, a failed unidentified first attempt, a root `reset-failed` and the unit's unload (three root acts outside 𝒜) |
| DF-1, SL-1, GU | userspace-only restart double fault (outside 𝒜); deliberate root acts; an `unlinkat` failure on tmpfs (BS-4 retries, the boot clears) |

## 11. Parameters, coverage and reconciliation tables

### 11.1 Parameters

| Parameter | Meaning | Accepted range | Recommended | Source | Class |
|---|---|---|---|---|---|
| `pk_op_ms` (P) | interval in which a PK/2 series may start calls | 5,000 … 60,000 | 30,000 | R8 §7.6 | E |
| `pk_call_ms` (c) | deadline of one child wait (a PK call, a unit-state read, a creation call) | 1,000 … 10,000, c ≤ P | 5,000 | R8 §7.6 | E |
| `reap_grace_ms` (g) | wait budget (total scheduled sleeping) for reaping a signalled child; not a return bound | 500 … 5,000 | 2,000 | R8 §7.6; WB-6 | E |
| `lock_wait_ms` (λ) | CL's lock acquisition deadline | 1,000 … 10,000 | 5,000 | R8 §7.6; LD-5 | E |
| `slice_ms` | longest interval between flag checks inside any E wait | 50 … 250 | 100 | R8 §7.6 | E |
| `stop_timeout_s` (S) | the holder's `TimeoutStopSec=`; also the backstop service's | 60 … 600 | 120 | R8 §7.6 | M |
| `bs_runtime_s` (S_b) | the backstop service's `RuntimeMaxSec=` (BS-RM) | 60 … 600 | 120 | R8 §7.6, §7.4 | M |
| `backstop_period_s` (R) | the backstop timer's period | 30 … 600 | 60 | R8 §7.6 | — |
| `backstop_max` (B) | most firings that run CL before the backstop disarms | 1 … 99 | 20 | R8 §7.6 | C |
| `reserve_ms` (ρ) | allowance for class-X work in the sizing rules (an expectation, not a bound) | ≥ 30,000 | 30,000 | R8 §7.6 | — |
| `act_wait_s` | executor's wait in AP-2 (outside the set) | 60 … L | L | R8 §7.6; row 5 | E |
| `journal_max_bytes` | volume cap for any journal read | 65,536 … 4,194,304 | 1,048,576 | R8 §7.6 | volume cap |
| `start_window_s` (W) | time from ACT PASS within which the operator's start must be observed | 60 … 3,600 | as accepted | D R2 (c) | — |
| `lease_s` (L) | the holder's `RuntimeMaxSec=` | W < L ≤ 86,400 | as accepted | D R2 (c) | M |
| `poll_ms` (Δ) | HL observation period | 250 … 5,000 | as accepted | D R2 (c) | — |
| `T_s` | the capture unit's loaded `TimeoutStartUSec`: finite; must satisfy N1: T_s·1,000 ≥ W_show + W_series + ρ, with W_show = c + g and W_series = P + c + g (N1 is a necessary condition only and claims no elapsed time) | manager default 90 s | 90 s | R8 §7.6 N1 | M |
| BSP retries | re-reads of the capture-unit baseline | ≤ 5 | 5 | R8 §6.4 | C |
| `pass-a.json` read | volume cap | 65,536 bytes |  | D R5 (e) CQ-0 | volume cap |
| rule file read | volume cap (GRR re-verification reads at most size + 1) | 65,536 bytes |  | R8 §5.7 GRR-3 | volume cap |
| `grant.id` read | volume cap | 4,096 bytes |  | R8 §5.7 GRR-1 | volume cap |
| `/proc/⟨pid⟩/stat` read | volume cap for SN validation | 4,096 bytes |  | R8 §7.5a.4 SN-4 | volume cap |
| PK child output | volume cap | 65,536 bytes |  | R8 §7.3 row 2 | volume cap |
| `children` record | entries / memory before the journal exists | ≤ 64 / ≤ 64 KiB, `overflow` counter |  | R8 §7.5a.9 | volume cap |
| PK schedule | call offsets (ms) | 0, 250, 500, 1,000, 2,000, 3,000, 4,000, then every 2,000 |  | R8 §7.5 | — |
| PK subject lifetime | self-limiting | 60 s |  | R8 §7.5; row 4 | X |

CP's whole-life bound `T_s` is a manager deadline (class M); CP's elapsed time is not claimed. [A]

### 11.2 Row counts [M]

Every count in this section is produced by a read-only parser run over the delivered operation tables of §§4 and 5 of this document; none is edited by hand. A **row** is any line of those tables. 318 rows are delivered: 317 are operation, contract or composition rows and 1 is a gap row (`RT2.AM0.7`, class GAP, which states no operation). The total is the count the corrected tables produce; it is not a target carried over from R1.

| Class | Rows |
|---|---|
| EN | 9 |
| FD | 19 |
| SR | 2 |
| FS | 59 |
| FM | 26 |
| SY | 7 |
| LK | 4 |
| CK | 5 |
| SL | 5 |
| HS | 6 |
| PR | 7 |
| JR | 28 |
| UA | 24 |
| PC | 1 |
| CR | 1 |
| ID | 4 |
| SG | 2 |
| PL | 2 |
| XT | 5 |
| DG | 2 |
| CN | 63 |
| CMP | 36 |
| GAP | 1 |
| **Total** | **318** |

| Part | Rows |
|---|---|
| H-FI | 7 |
| H-CLK | 3 |
| H-LK | 4 |
| H-JRN | 10 |
| H-PF | 9 |
| H-PT | 10 |
| H-GR1 | 7 |
| H-GRR | 8 |
| H-DI1 | 4 |
| H-PROC | 6 |
| H-PK2 | 7 |
| H-SN | 16 |
| H-BSE | 15 |
| H-REC | 4 |
| H-DIAG | 1 |
| H-CL | 33 |
| *shared helpers subtotal* | *144* |
| RT-1 | 46 |
| RT-2 | 63 |
| RT-3 | 15 |
| RT-4 | 22 |
| RT-5 | 18 |
| SA-1 | 5 |
| SA-2 | 5 |
| *procedure subtotal* | *174* |
| **Total** | **318** |

| Tag | Rows |
|---|---|
| [A] only | 238 |
| [A] with one or more [Q] | 73 |
| [M] (with or without a [Q]) | 6 |
| [Q] alone (gap row, class GAP) | 1 |
| **Total** | **318** |

### 11.3 Closed coverage tables

**(a) Procedures and steps.** Every accepted step has at least one row (§6). Steps with no row: **0** of 77. Procedure rows that appear in no step: **0**. Steps traced only by a gap row: **0** (the AM0 step has sixteen operation rows besides the gap row).

| Procedure | Steps | Steps with ≥1 row | Rows | of which gap rows |
|---|---|---|---|---|
| RT-1 | 10 | 10 | 46 | 0 |
| RT-2 | 15 | 15 | 63 | 1 |
| RT-3 | 14 | 14 | 15 | 0 |
| RT-4 | 19 | 19 | 22 | 0 |
| RT-5 | 15 | 15 | 18 | 0 |
| SA-1 | 2 | 2 | 5 | 0 |
| SA-2 | 2 | 2 | 5 | 0 |

**(b) R8 §7.3 taxonomy rows 1 … 22 and 3a … 3g.**

| Row | Operation / wait | Class | Rows citing it |
|---|---|---|---|
| 1 | creating a child (`fork`, `clone`, `execve` inside the process-creation function) | X | 37 |
| 2 | waiting for a child's exit and reading its output | E (c) | 30 |
| 3 | the scheduled waiting for the reaping of a signalled child | E (g) | 20 |
| 3a | send 1, the initial group-directed termination (SN-I-1) | X, C | 15 |
| 3b | send 2, the escalation (SN-I-2) | X, C | 15 |
| 3c | send 3, the termination of the PK subject (SN-I-3) | X, C | 17 |
| 3d | sends in cleanup and recovery (SN-I-4): none | none | 17 |
| 3e | validation of the child's identity before a send (SN-4) | X + cap | 17 |
| 3f | PID 1's sending of signals | M | 14 |
| 3g | a reap attempt | X | 18 |
| 4 | the PK subject's own life (60 s) | X | 4 |
| 5 | the executor's wait for the `act` record or the holder's end (AP-2) | E | 1 |
| 6 | the lock loop on K | E (λ); calls X | 22 |
| 7 | sleeps between polls (HL Δ, the PK schedule, BSP's 2 ms) | E | 9 |
| 8 | reading small root-owned files (journals, records, `pass-a.json`, `grant.id`, H-1 record, A-2 pins) | X + cap | 92 |
| 9 | SHA-256 over files (GRR, AP-0/AM-0/H-2, CL-6 baseline recomputation) | X + cap | 52 |
| 10 | metadata and extended-attribute inspection | X | 78 |
| 11 | appends and flushes to `ext4` journals and records; evidence directories; PF and PT publication | X (stall unbounded, RO-6) | 85 |
| 12 | removal of the rule and of `pass-a.json`; flush of a tmpfs directory | X | 29 |
| 13 | signal receipt and handler execution | X | 5 |
| 14 | the PK series as a whole | E (P) | 16 |
| 15 | BSP re-reads | C (5) | 1 |
| 16 | backstop firings that run CL | C (B) | 2 |
| 17 | the holder's whole life | M (L) | 1 |
| 18 | the stop-post CL's whole life | M (S) | 2 |
| 19 | the backstop firing's whole life | M (S_b) | 1 |
| 20 | CP's whole life | M (T_s) | 3 |
| 21 | verification reads by the executor (AP-0, H-2, H-2b) | X (outside the set) | 2 |
| 22 | `attest` | no enforcer | 2 |

Taxonomy rows without an operation row: **0**.

**(c) DI-1 … DI-6 and the stop-unit call × procedure.** The unit is the **logical accepted call site** of §7.1; the call-site table and the matrix of §7.1 are the tables this claim summarizes, and no other unit is used. The table lists 41 call sites:

| DI | Call sites |
|---|---|
| DI-1 | 23 |
| DI-2 | 1 |
| DI-3 | 1 |
| DI-4 | 3 |
| DI-5 | 6 |
| DI-6 | 6 |
| DI-S | 1 |
| **All** | **41** |

DI-4 is reconciled at three sites (BS-2, BS-3, BS-4 terminal disarm), implemented by `RT4.BS2.2` (BS-2 and, by delegation, BS-3), `RT4.BS3.1` and `RT4.BS4.2`; §7.2, §8 (PC-5) and the roster agree. Every cell that accepted text requires is non-empty and every dash is an accepted absence. Cells required but empty: **0**. Call sites naming a row that does not exist: **0**. Procedure rows named by the call-site table but missing from the §7.2 list for that DI: **0**. Matrix cells that disagree with the call-site table: **0**. [M]

**(d) SN / SI / WB / RE / GD / RA / RB / CS identifiers and other cited contract identifiers.** Counting rule: an identifier is *cited* by an operation row when its text appears in that row's own cells (a stated range such as `SN-1 … SN-10` cites every member); a row that merely composes a helper does not inherit the helper's identifiers. Each identifier below appears in at least one row. The R1 return's figures in this table were produced by a different method that this document does not reproduce; they are replaced by the figures below, which can be re-derived from the tables:

| Identifier | Rows citing it |
|---|---|
| SN-1 | 3 |
| SN-2 | 2 |
| SN-3 | 6 |
| SN-4 | 3 |
| SN-5 | 2 |
| SN-6 | 1 |
| SN-7 | 3 |
| SN-8 | 4 |
| SN-9 | 2 |
| SN-10 | 8 |
| SI-1 | 2 |
| SI-2 | 3 |
| SI-3 | 2 |
| SI-4 | 3 |
| SI-5 | 2 |
| WB-1 | 1 |
| WB-2 | 4 |
| WB-3 | 2 |
| WB-4 | 1 |
| WB-5 | 1 |
| WB-6 | 1 |
| WB-7 | 1 |
| RE-1 | 2 |
| RE-2 | 1 |
| RE-3 | 1 |
| RE-4 | 1 |
| RE-5 | 1 |
| RE-6 | 1 |
| GD-1 | 1 |
| GD-2 | 2 |
| GD-3 | 1 |
| GD-4 | 1 |
| GD-5 | 1 |
| GD-6 | 1 |
| RA-0 | 1 |
| RA-1 | 1 |
| RA-2 | 1 |
| RA-3 | 1 |
| RA-4 | 1 |
| RA-E | 1 |
| RB-1 | 2 |
| RB-2 | 1 |
| RB-3 | 1 |
| RB-4 | 1 |
| SN-I-1 | 1 |
| SN-I-2 | 1 |
| SN-I-3 | 3 |
| SN-I-4 | 2 |
| RH-1 | 2 |
| RH-2 | 2 |
| RH-3 | 3 |
| LD-1 | 4 |
| LD-2 | 1 |
| LD-3 | 6 |
| LD-4 | 2 |
| LD-5 | 2 |
| LD-6 | 2 |
| LD-9 | 2 |
| SG-1 | 2 |
| SG-2 | 1 |
| SG-3 | 2 |
| SG-4 | 6 |
| SG-5 | 1 |
| SG-6 | 1 |
| SG-7 | 3 |
| SG-8 | 5 |
| SG-9 | 2 |
| IGR-0 | 1 |
| IGR-1 | 1 |
| IGR-2 | 1 |
| IGR-3 | 1 |
| GR-1 | 1 |
| GR-2 | 3 |
| GI-1 | 2 |
| OS-1 | 1 |
| OS-4 | 1 |
| OS-5 | 3 |
| OS-7 | 2 |
| AR-2 | 2 |
| BSP | 4 |
| IL | 2 |
| SB-1 | 1 |
| SB-3 | 1 |

Identifiers with no row: **0**. The WB-1 … WB-7, RE-1 … RE-6, GD-1 … GD-6, CS-1 … CS-10 and T0 … T7 consequences are traced in tables §9.2 – §9.5 and in rows `H-SN.2` … `H-SN.16`.

**(e) Added roles.** `start` (SA-1) has 5 rows and `stop` (SA-2) has 5 rows; every operation of each is in the tables of §5. Each role has one logical call site (CALL-DI2-01 and CALL-DIS-01).

### 11.4 Rows per deferred question [M]

| Question | Owner | Rows carrying it |
|---|---|---|
| Q3-1 | WP-3 | 13 |
| Q3-2 | WP-3 | 1 |
| Q3-3 | WP-3 | 1 |
| Q3-4 | WP-3 | 3 |
| Q3-5 | WP-3 | 6 |
| Q3-6 | WP-3 | 6 |
| Q3-7 | WP-3 | 1 |
| Q3-9 | WP-3 | 2 |
| Q3-11 | WP-3 | 5 |
| Q4-1 | WP-4 | 10 |
| Q4-2 | WP-4 | 2 |
| Q4-3 | WP-4 | 1 |
| Q4-5 | WP-4 | 1 |
| Q4-6 | WP-4 | 13 |
| Q4-7 | WP-4 | 17 |
| Q4-8 | WP-4 | 6 |
| Q4-11 | WP-4 | 7 |
| Q6-1 | WP-6 | 1 |
| Q6-2 | WP-6 | 7 |
| Q6-3 | WP-6 | 4 |
| Q6-4 | WP-6 | 1 |
| Q6-6 | WP-6 | 5 |
| Q6-7 | WP-6 | 3 |
| Q7-1 | WP-7 | 0 |

Q6-7 is carried by the gap row `RT2.AM0.7` (the AM-0 gap) and by `RT4.BS4.2` and `RT4.SN.1` (whether SN-10 / A-I-16 extend to the BS-4 terminal disarm). Its other accepted-text gaps (placement of `run-end` in the ACT journal; which journal receives BS-4's final line; the source of the `helper.image_sha256[]` values) are stated in §12 and in the text of `RT2.AM3.2` and `RT4.BS4.2` and are not separately tagged. Q7-1 is not carried by a row: it is an obligation about the inventory as a whole (the counts in this section as WP-7 inputs). Q6-6 is carried by the three call-site rows (`RT2.AK1.2`, `RT4.BS2.2`, `RT4.BS3.1`) and by the two SN rows that state the carried obligation (`RT2.SN.1`, `RT4.SN.1`). Questions defined in §12: 24; questions in this table: 24; sets equal: yes.

### 11.5 Counts offered as WP-7 inputs only [M]

These counts are offered for Q7-1. WP-2 makes **no estimate**. Interface-call counts are stated in the unit of §7.1 (logical call sites) **and** in operation rows, with the unit named in each line.

| Quantity | Count |
|---|---|
| process-creation intents (§8 rows PC-1 … PC-10, of which PC-1 and PC-8 are retained creations, PC-2 … PC-7 removed, PC-9 outside the tree, PC-10 unclassified) | 10 |
| interface call sites, DI-1 … DI-6 and the stop-unit call (logical accepted call sites, §7.1) | 41 (DI-1 23, DI-2 1, DI-3 1, DI-4 3, DI-5 6, DI-6 6, DI-S 1) |
| unit-manager or authorization interaction rows (class UA; operation rows, not call sites) | 24 |
| hashing rows (class HS) | 6 |
| parse / serialize / validate rows (class PR) | 7 |
| journal / record publication rows (class JR) | 28 |
| filesystem access rows (FS) and mutation rows (FM) | 59 and 26 |
| baseline keys (H-BSE) | 12 (host, operator, repository, packages, citations, launcher, files, directories, absent, unit, manager, po17/po18 pair) |

## 12. Questions deferred to WP-3 … WP-7

Each question is stated for its owning package and is **not answered** here. They are the exact obligations that the accepted text leaves open at system-call intent.

### WP-3

| ID | Question |
|---|---|
| Q3-1 | Loader-free interface and version-bound citation for DI-1 (unit-state read): which interface carries the reads; the value form a static image receives for each property it uses (`ActiveState`, `InvocationID`, `InactiveEnterTimestampMonotonic`, `Job`, `LoadState`, `Result`, `ExecMainStartTimestampMonotonic`, `TimeoutStartUSec`); behaviour for an unloaded unit and for a unit read during its own start-pre. |
| Q3-2 | Interface contract for DI-2 (creation of the transient holder service): the property set and value forms for `Restart`, `OOMScoreAdjust`, `RuntimeMaxSec`, `TimeoutStopSec`, `ExecStopPost`, main command and unit type; job mode; completion semantics; the refusal when the name is already loaded. |
| Q3-3 | Interface contract for DI-3 (creation of the backstop timer and service): the timer properties (`on-active`, `on-unit-active`, `AccuracySec`), the service properties including `RuntimeMaxSec` and `TimeoutStopSec`, and how creation of a timer and a service is expressed. |
| Q3-4 | Interface contract for DI-4 (disarm: stop of the backstop timer unit), which has three logical call sites — BS-2, BS-3 and the BS-4 terminal disarm (§7.1): request form, completion semantics, behaviour when the timer is already stopped or not loaded. |
| Q3-5 | Interface contract for DI-5: a Polkit decision equal to `pkcheck`'s for action `org.freedesktop.systemd1.manage-units`, details `unit` and `verb`, subject = a process (pid, start time, uid), caller root, no interaction; the exact mapping of the authority's answers to `authorized` / `not-authorized` / `error` (the exit-status contract of R2 §6.4 (e) is a command-line contract that does not carry over). |
| Q3-6 | How the subject's identity (pid, start time, uid) obtained from DI-6 is conveyed to DI-5 and what the authority records about it (interface fact only; the creation of the subject belongs to WP-4). |
| Q3-7 | Interface contract for the stop-unit call of SA-2 (no R8 DI row): job mode, completion and result semantics, behaviour when the unit is already inactive, behaviour during start-pre (which is outside the route), and the authorization the call needs when issued by root. |
| Q3-9 | Interface facts needed to read the explicit property lists of the baseline `unit` and `manager` keys (including properties that are hidden or explicit-only, and the printed-form facts the normalization relies on: R2 §4.1 … §4.4). |
| Q3-11 | Version-bound citations for the on-disk or kernel facts a static image would read directly where the accepted text states only the baseline value and not the mechanism: account and group databases (`operator`), installed-package records (`packages`), repository head resolution and manifests (`repository`), host identity and kernel release (`host`). WP-2 does not choose any of them and does not state that any suffices. |

### WP-4

| ID | Question |
|---|---|
| Q4-1 | Process-creation mechanism for DI-6 subjects (and for any other child a root image creates): fork continuing in a static image or `execve` of a design-controlled static image; session and process-group setup; credential change (supplementary groups, GID, UID from the H-1 record); the subject's body that keeps it alive for the call and at most 60 s; the exact system-call sequence; the linking primitive for PF-6 and the rename primitive for PT-8 in a static image. |
| Q4-2 | The first-image state operations (RH-1 … RH-3): sequence, refusal codes, handling of the inherited environment for unit-started and `sudo`-started roles, and treatment of INVOCATION_ID. |
| Q4-3 | Realization of flag-only signal handlers for the holder (SG-1 … SG-9) in a static image: handler contents, interaction with blocking calls, `EINTR` and restart behaviour, and the guarantee that no handler sends a signal or re-enters IGR. |
| Q4-5 | Parsers and bounded memory: canonical JSON (serialize and parse), SHA-256, the journal parser, the `pass-a.json` / A-2 / H-1 record / `act` record parsers, the printed-property decoders, the mountinfo and binfmt_misc parsers, and the stack and memory bounds for each, within the volume caps the accepted text states. |
| Q4-6 | Image architecture and operand handling: the number of static images and which roles each contains; the argument or operand grammar and validation for every role (unit-started and `sudo`-started); where each root role finds its inputs where the accepted text does not give a path (the A-2 file, the H-1 record locator for CP, the activation record locator). |
| Q4-7 | How the class-E deadline `c` (and `pk_call_ms`-bounded waits) is enforced on an in-process interface call that replaces a child wait, including cancellation, the fail-closed `error` result at expiry, and behaviour after expiry; likewise for the unbounded SA-1 and SA-2 calls (no accepted class or bound). |
| Q4-8 | The signal-send, validation, reap and wait calls of the SN contract for a static fork child: `setsid`, group send, non-blocking reap, the sole-reaper invariant without CPython's behaviours, and the replacement of PO-SN (c). |
| Q4-11 | Errno-to-outcome mapping and failure handling for calls whose accepted text states no failure contract (the diagnostic write, clock reads, the SA-1 and SA-2 calls' own failures, directory listings, reads of `/proc`), without changing any accepted fail-closed outcome. |

### WP-5

None recorded by WP-2.

### WP-6

| ID | Question |
|---|---|
| Q6-1 | Equivalence mapping of each accepted step to its replacement step and of each accepted negative test (NT-*) to an image-level counterpart, including the PK exit-status mapping and the `sleep 60` subject. |
| Q6-2 | Byte-level equivalence of the baseline recomputation: the H-1 record's `baseline_sha256` was written by the installer class (outside the set, Python, `systemctl show` printed text); a static image reading typed values must reproduce the same canonical bytes (value encoding, `ExecStart` normalization, strict UTF-8, ordering, absent facts). State whether the equality is preservable. |
| Q6-3 | Behaviours that cannot be preserved without a dynamic child, if any are found by WP-3/WP-4: the candidates WP-2 flags are the baseline keys whose acquisition mechanism the accepted text does not state (`packages`, `host`, `operator`, `repository`, `citations`, `launcher` sub-keys). Any behaviour that cannot be preserved is recorded as not preserved and returned to Peter, never silently covered; a proposal to keep a dynamic child is SCDC/BC-3 (§0.2), not a WP result. |
| Q6-4 | The DI-6 subject's accepted properties (`sleep 60`, self-limiting lifetime, argv, credentials from the H-1 record) restated for a static subject. |
| Q6-6 | SN-10 and the OH-S0d confirmation item A-I-16, carried as an **unanswered obligation** for mutating calls that are no longer children. Accepted text requires that the effect of a mutating operation may be `unknown` after an `error`, an interruption or an indeterminate completion, and that no later step may read the result as “not created” or “not stopped”; it states this for the DI-3 call (AK-1) and the DI-4 call (BS-2, BS-3). Accepted text does not state it for the BS-4 terminal disarm (the third DI-4 call site); that extension is part of Q6-7, not of this question. The question: what `effect: "unknown"` means for each of those interactions once it is not a child, how the obligation maps to a non-child loader-free interaction, and which step disarms the backstop timer after an `error`, `interrupted` or unconfirmed creation. WP-2 supplies no mapping. WP-2 does not choose whether a later package realizes the interaction in process, by a static child or by another admitted mechanism; if a later design chooses a child, BQ-4 still requires (F) or (X) and never a distribution executable, and the applicable child contract must then be mapped by that later package. (The R1 return also named DI-2 here; accepted SN-10 names only the AK-1 and BS-2 / BS-3 calls, so whether DI-2 is within the obligation is part of this question and is not asserted.) |
| Q6-7 | Accepted-text gaps found while inventorying, to be restated or confirmed (documentation, OH-S0d class) without changing accepted behaviour: placement of `run-end` in the ACT journal; which journal receives BS-4's final line; **whether SN-10 / A-I-16 extend to the DI-4 call at the BS-4 terminal disarm** (accepted text names BS-2 and BS-3 only; D R2 (f) BS-4 and R8 §8.1 BS-4 Δ2 state the call, R8 §9.3 DI-4, A-I-16 and WP-1 R6 list BS-2 and BS-3, and no accepted passage applies the obligation to BS-4 or excludes it; WP-2 selects neither answer); **whether AM-0 repeats AP-0's “no unterminated activation of this H-1 record” condition**; the source of the `helper.image_sha256[]` values recorded in `run-start`. **The AM-0 gap and the BS-4 extension are open and WP-2 has selected neither answer in either case.** The competing accepted passages are quoted without choosing between them: D R2 (d) AM-0 — “re-check, as root, AP-0's `boot_id`, `/run` and absence conditions”; R8 §8.1 AM-0 (i) — “re-check `boot_id`, `/run` and every AP-0 absence condition, `K` included”; D R2 (d) AP-0 — lists “no unterminated activation of this H-1 record (each has a `deact` record with outcome `st1-verified`, or ST-1+R has been decided by Peter)” as a separate item and does not call it an “absence condition”. The inventory therefore states no AM-0 operation for it (`RT2.AM0.7` is a gap row) and nothing may be derived from the inventory in either direction. Owner under the accepted package allocation: WP-6. |

### WP-7

| ID | Question |
|---|---|
| Q7-1 | Inputs for the estimate (counts only, no estimate made by WP-2): the numbers of process-creation intents, interface calls (DI-1 … DI-6 and the stop-unit call), parsers, hashing sites, journal/record writes and baseline keys given in §11 of this document. |

WP-5 (proof and evidence method) receives no question from WP-2: the inventory records what must be proven and not how. [M]

## 13. Inputs WP-3 may and may not rely on

| WP-3 may rely on | WP-3 may not rely on |
|---|---|
| The fixed F-1 scope and exclusions of §1 [A] | Any claim that LIT-FULL is selected, that concrete Route 3 is established, or that WP-2 is accepted |
| The procedure and sub-role roster of §3, including SA-1 and SA-2 [A] | A completed review: the independent Codex review and Peter's acceptance are still required |
| The operation tables of §4 and §5 as the list of intents that replace each delegation, with their accepted blocking class and failure contract [A] | Any interface, protocol, wire format, library, language or syscall sequence: none is chosen here |
| The DI-1 … DI-6 and stop-unit map of §7, including the logical call-site table of §7.1 (the unit of counting, with DI-4 at three sites: BS-2, BS-3, BS-4 terminal disarm) and the DI-1 additions of §7.3 [M] | W1's DI-1 site list on its own: it is incomplete (§7.3). Operation-row counts as call-site counts, or the R1 return's §7.1 figures |
| The child surface of §8.1: today's accepted children (DI-1 … DI-5, stop-unit) are historical; the only child intent the LIT-FULL replacement retains is the DI-6 subject (PC-1), to which the H-SN contract applies [A][M] | Any reading that DI-3 or DI-4 children remain in the replacement root-procedure tree, or that H-SN is part of the replacement contract for them. Any mapping of the SN-10 / A-I-16 `effect: "unknown"` obligation to a non-child interaction: that is Q6-6, unanswered. Any statement that SN-10 / A-I-16 apply, or do not apply, to the DI-4 call at the BS-4 terminal disarm: that is Q6-7, open |
| The AM-0 operations `RT2.AM0.1` … `RT2.AM0.6` and `RT2.AM0.8` … `RT2.AM0.17` [A] | `RT2.AM0.7` as an operation: it is a gap row. Either answer to whether AM-0 repeats AP-0's “no unterminated activation” condition: Q6-7 is open and WP-2 selected neither |
| The process-creation classification of §8 (no `execve` of a distribution program is required) [M] | A choice between (F) and (X) for any row: that is WP-3 / WP-4 work |
| The signal, validation and reap surface and its consequences in §9 [A] | Any bound turned into an elapsed time for a class-X call or a scheduled-waiting budget |
| The accepted residuals and "unknown" states of §10 [A] | Any residual weakened, closed or reworded: a signal attempt is not proof of exit and a missing record is not proof of absence |
| The question list of §12, as stated [M] | An answer to any question in §12 from this document |
| The counts of §11 as [M] inputs for Q7-1 | A size, cost or review-effort estimate: none is made here |
| Baseline v1.8 and the no-host restriction as stated in the current-state pointers | Any host fact (MF-1 … MF-9) or any retained evidence: none was collected |

## 14. Acceptance checklist

Prepared for the independent reviewer. Each item is verifiable from the document; none is asserted as passed by the reviewer.

- [ ] §1 states the fixed scope and exclusions as in the assignment (LIT-FULL under R3-ROOT; RT-1 … RT-5, SA-1, SA-2; EX-1, EX-2, no EX-3; BQ-4 no dynamic child; BC-2 deferred; Route 3 unestablished).
- [ ] §2 defines the tags [A], [M], [Q] and the class codes; every row carries exactly one tag set.
- [ ] §3 gives a stable ID, caller, beginning boundary, accepted implementation and failure contract for every procedure and sub-role.
- [ ] §4 and §5 give rows per procedure and sub-role; shared helpers are separate tables, not collapsed.
- [ ] §6 traces every accepted step to at least one row; §11.3(a) shows zero steps without a row.
- [ ] §11.3(b) shows every R8 §7.3 row 1 … 22 and 3a … 3g covered.
- [ ] §7 maps DI-1 … DI-6 and the stop-unit call to procedures and intents, with the omissions of W1's site list added; §7.1 defines its unit as the **logical accepted call site**, lists every site with its implementing rows, derives the matrix and the §7.2 row lists from that table, and reconciles DI-4 at three sites (BS-2, BS-3, BS-4 terminal disarm) carried by `RT4.BS2.2`, `RT4.BS3.1` and `RT4.BS4.2`.
- [ ] §8 classifies every process-creation row as (F) or (X); no row is an `execve` of a distribution program; PC-10 is flagged; §8.1 separates today's accepted children from the LIT-FULL replacement child set and carries the SN-10 / A-I-16 `unknown`-effect obligation unmapped as Q6-6; `RT1.SN.1`, `RT2.SN.1`, `RT3.SN.1`, `RT4.SN.1`, `RT5.SN.1` and `H-SN.1` agree with §8.1.
- [ ] §9 traces SN-I-1 … SN-I-4, SN-4 validation and the reap-attempt surface with WB, RE, GD and child-state consequences.
- [ ] §10 preserves interruption maps, terminal causes and accepted residuals without weakening them.
- [ ] §11 gives parameters, counts and closed coverage tables; counts are labelled [M], are recomputed from the delivered tables, and state their counting unit (§11.3(c) uses the call-site unit of §7.1; §11.3(d) states its citation rule); the total of 318 rows is the count the corrected tables produce and includes one gap row.
- [ ] `RT2.AM0.7` is a non-operative gap row (class GAP, tag `Q6-7`); it states no operation, is not tagged [M], and Q6-7 is explicit, unanswered and owned by WP-6; the AM0 step trace, §11.2, §11.3, §11.4 and §13 agree.
- [ ] SN-10 / A-I-16 are applied only to the calls accepted text names (DI-3 at AK-1; DI-4 at BS-2 and BS-3); the BS-4 terminal disarm remains the third DI-4 call site (`CALL-DI4-03`) with the extension left open as part of Q6-7; `RT4.BS4.2`, `RT4.SN.1`, §7, §8 (PC-5), §8.1, §11.4, §12 and §13 agree.
- [ ] §12 lists each deferred question with its owner and answers none.
- [ ] §13 states what WP-3 may and may not rely on.
- [ ] §15 applies the stop rule and reports no HARD STOP, with the reviewer-focus note.
- [ ] The four current-state pointers say `WP-2 R5 REMEDIATION RETURNED — INDEPENDENT RE-REVIEW PENDING` and preserve baseline v1.8, the F-1 boundary, EX-1/EX-2, the no-host restriction and the separate WP-3 … WP-7 gates.
- [ ] Dated snapshots of the four pointers (`lit-full-wp2-r5-authorization`) exist and their SHA-256 values are in the four archive indexes; no earlier snapshot, accepted record, the R1 and R2 handbacks, the independent reviews, the R5 prompt or its authority record, the R4 handback, or any application file changed.

## 15. Stop rule applied

**Result: no HARD STOP.** No accepted function appears to require a dynamic child, and no accepted function could not be inventoried without changing accepted behavior. The replacement of each removed dynamic child (`systemctl`, `systemd-run`, `pkcheck`, `sleep`) is an intent in §7 and §8 owned by WP-3 or WP-4. SCDC is not proposed and no BC-3 exception is created. [M]

**R2 stop-rule note on `WP2-R1-1`.** The remediation was authorized to preserve the AM-0 question, not to decide it. The competing accepted passages (D R2 (d) AM-0, R8 §8.1 AM-0 (i), D R2 (d) AP-0; quoted in Q6-7) do not, read together, state whether AM-0 repeats the “no unterminated activation” condition: the AM-0 wording refers to AP-0's “absence conditions”, and AP-0 states that condition as a separate item without calling it one. No accepted passage was found that genuinely resolves the question, so no `HARD STOP` is returned and no answer is applied. If the reviewer finds a passage that does resolve it, the correct result is a `HARD STOP` citing the competing passages, not a silent reading. [M]

**Reviewer focus — flagged baseline-acquisition items.** The stop rule is evaluated on accepted text only. Three items sit at its edge and are carried as questions, not as a HARD STOP, because the accepted text does not require a dynamic child for them:

- **Q3-11** — the on-disk or kernel facts a static image would read directly where the accepted text names a command (`uname`, `sha256sum`, `id`, `getent`, the repository identity) for the baseline keys host, operator, repository, packages, citations, launcher, files and directories. If the facts cannot be read without a distribution program, the finding belongs to WP-3 and WP-6, and would then be a HARD STOP for LIT-FULL at that point.
- **Q6-2** — byte-level equivalence of the baseline recomputation: the H-1 record's `baseline_sha256` was written by the installer class (Python, printed `systemctl show` text); a static image reading typed values must reproduce the same canonical bytes. Whether that equality is preservable is not decided by the accepted text.
- **Q6-3** — behaviors that cannot be preserved without a dynamic child, if WP-3 or WP-4 finds any; the candidates are those of PC-10.

These three are exactly where a reviewer should push hardest. WP-2 neither resolves them nor asserts that they resolve favorably. [M]

**R3 stop-rule note on `WP2-R2-2`.** No accepted passage states that SN-10 / A-I-16 apply to the DI-4 call at the BS-4 terminal disarm, and none excludes it: D R2 (f) BS-4 and R8 §8.1 BS-4 Δ2 state the call; R8 §9.3 DI-4, A-I-16 and WP-1 R6 list BS-2 and BS-3. The question is carried in Q6-7 unanswered, so no `HARD STOP` is returned and no answer is applied.

**Reviewer focus — the R5 correction.**

- **`WP2-R4-1`** — confirm that `RT3.SN.1` names PID 1's `FINAL_SIGTERM` then `FINAL_SIGKILL` after another S to “what remains” as the owner of a left-behind child, adds nothing to PO-SN (e) about `setsid`, treats the boot as a separate event, gives `attest` no automatic owner, states the observer contract separately and never as an action on the child, and that the backstop/CP/boot/`attest` chain survives only as cleanup-state recovery on `RT3.FI.2` and `RT3.CLG` … `RT3.CLOUT`. Confirm that no count in §11 changed.

**Reviewer focus — the R4 corrections (carried).**

- **`WP2-R3-1`** — confirm that `⌈P/1000⌉ + 30` appears nowhere in this document as a requirement, that `RT1.FI.2` and the §11.1 `T_s` row keep only finite, class M and N1, and that N1 is stated as a necessary condition with no margin and no elapsed-time claim.
- **`WP2-R3-2`** — confirm that `RT3.SN.1` is grounded only in accepted text, states the two tiers of §8.1, carries no Q tag, and that every count in §11 moved only by the one added row and the one added step (R4). Its owner sentence is corrected by `WP2-R4-1` below.

**Reviewer focus — the two R2 corrections (carried).**

- **`WP2-R1-1`** — confirm that `RT2.AM0.7` states no operation and no instruction, that no other row, count or table treats the no-unterminated-activation check as required or as excluded, and that Q6-7 is open with WP-6 as owner.
- **`WP2-R1-2`** — confirm that §8.1 and the five SN rows agree (today's DI-1 … DI-5 and stop-unit children are historical; only the DI-6 subject is retained); that the SN-10 / A-I-16 obligation is kept and carried unmapped as Q6-6; that §7.1's call-site table, matrix, §7.2 row lists, §8 PC-5, §11.3(c) and §11.5 use the same unit; and that DI-4 has exactly the three sites BS-2, BS-3 and the BS-4 terminal disarm. Also confirm that the eight added DI-1 sites (baseline `unit` and `manager` reads at AV-1 and at the three CL-6 instances) are properly sites, since R1's own §7.3 named them but R1's matrix did not count them.

**Reviewer focus — the R3 corrections.**

- **`WP2-R2-2`** — confirm that no row, count or table applies SN-10 / A-I-16 to the BS-4 terminal disarm, that BS-4 is still the third DI-4 call site (`CALL-DI4-03`, `RT4.BS4.2`), and that Q6-7 carries the open extension question with WP-6 as owner. Counts changed only as follows: Q6-6 rows 6 → 5 and Q6-7 rows 1 → 3 (§11.4); the 317 total, the 316 operation / contract / composition rows, the 41 call sites and the tag totals were unchanged in R3 (the R4 figures are in §11.2 and the R4 revision record).
- **`WP2-R2-1`, `WP2-R2-3`** — these are evidenced in the R3 handback (reading ledger; terminal link-check), not in this document.

*End of inventory.*
