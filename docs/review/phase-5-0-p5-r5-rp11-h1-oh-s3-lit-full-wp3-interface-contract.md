# LIT-FULL WP-3 interface contract — HARD STOP

Work ID `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP3-20261009-20` · executor Claude · 2026-10-10 ·
repository-only, no host, no network, no research.

**Terminal state: `HARD STOP`.** The authorized repository sources do not support
eighteen facts that the nine required Q3 closures need (registry in §6, `UF-01`
… `UF-18`; `UF-05` expanded by R1 to cover cancellation and abandonment). Per the accepted prompt's stop rule, no citation was manufactured,
nothing was silently deferred, no fact was introduced from memory, and nothing
was researched. This file is therefore **not a complete interface contract**: it
records everything the sources do support, separates it from what they do not,
and names each missing fact exactly. Q3-1 … Q3-7 and Q3-9 are **not closed**.
Q3-11 is closed as a fail-closed record (§5). WP-4 … WP-7 are neither prepared
nor authorized.

**R1 revision (work ID `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP3-R1-20261010-22`, 2026-10-10).**
This file is corrected in place and cumulatively after the independent review
finding `WP3-HS-R1`: the original return did not say, for DI-2, DI-3, DI-4 and
DI-S, that cancellation and abandonment semantics are unsupported. The
correction (a) expands `UF-05` (identifier kept, no renumbering; the count stays
eighteen) to include the four cancellation and abandonment facts, (b) adds the
common cancellation rules and a seven-interface cancellation treatment table
(§3.0), (c) amends §§3.2, 3.3, 3.4 and 3.7 and also states DI-1, DI-5 and DI-6,
and (d) reconciles §§5–10. It also corrects one citation defect found on
revalidation (§3, common supported facts: the former `DR WP-2 §7.1` fail-closed
sentence is replaced by exact sources; see C-33, C-34). The substantive `HARD
STOP`, the seven interfaces, the 41 call sites, the nine Q3 identifiers and
Q6-6, Q6-7 are unchanged. This revision does not accept WP-3, authorize WP-4,
establish concrete Route 3 or select LIT-FULL.

## 1. Fixed scope, source hierarchy, fact classes and version boundary

**Scope.** LIT-FULL under the R3-ROOT readiness investigation: procedures RT-1 …
RT-5, SA-1 (`start`) and SA-2 (`stop`); EX-1 (`sudo` launch preamble, LR-2 only)
and EX-2 (installer class, HB-1) stay outside the root-procedure set; BQ-4 means
no dynamic child. Baseline v1.8, F-1 B2-F, both lifecycle acts in, B3-OUT, EX-1,
EX-2 and no EX-3 are unchanged. Q6-6 and Q6-7 are **not answered** here (§3.3,
§3.4 state only that the `effect: "unknown"` mapping and the BS-4 extension are
theirs). BC-2 remains a later WP-9 question. This file selects nothing for
implementation and chooses no language, library, binding or syscall.

**Source hierarchy** (highest first; a lower source never overrides a higher):

1. `.agents/AGENTS.md`, `docs/implementation-plan.md`, `docs/review/Handover information`.
2. The accepted WP-2 inventory
   (`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md`, 318
   rows, 77 steps, 41 call sites), the accepted R8 proposal and its acceptance,
   the accepted one-host amendment proposal and its D3-R6 acceptance, the
   accepted WP-1 R6 proposal with its acceptance, BQ decisions and EX-1/EX-2
   change control, and g1-decisions.
3. The accepted OH-S2 R2 citation record
   (`phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md`, cited as **R2**), the only
   authorized carrier of version-bound server-side facts.

**Version boundary.** Every version-bound claim is bound to systemd
`259.5-0ubuntu3.4` and polkit `127-2ubuntu1.1` as recorded in R2. No claim is
made for any other version, and none is extended by inference.

**Fact classes.** Each statement in this file carries exactly one class.

| Class | Meaning | Rule |
|---|---|---|
| `SF` | Accepted source fact | Quoted or paraphrased from an authorized source with file and line. |
| `MD` | Mechanical derivation | Follows by counting, matching or set operations over `SF` only; the derivation is stated. |
| `DR` | Accepted design requirement | A requirement already accepted in WP-2/R8/D (intent, failure contract). Not a wire fact. |
| `PO3` | Proposed obligation | A WP-3 proposal for WP-4/maintainer decision. Not accepted until reviewed. |
| `UF` | Unsupported (missing) fact | A fact a Q3 closure needs that no authorized source states. Identified `UF-nn` (not `MF-n`, to avoid collision with R2's `MF` ids). |

A `UF` is never filled by `PO3` text: where a `PO3` obligation depends on a `UF`,
it says so and is conditional on that fact.

## 2. Closed interface roster and call-site mapping

Closed roster (`SF`, R8 DI table lines 3791–3796; WP-2 §7.1 line 729): **DI-1**
unit-state read; **DI-2** create holder unit; **DI-3** create backstop timer and
service; **DI-4** disarm backstop timer; **DI-5** Polkit decision; **DI-6**
authorization subject; plus **DI-S**, the SA-2 stop-unit call. Seven interfaces,
no other. Mapping to all 41 WP-2 logical call sites (`MD`: parsed from WP-2
§7.1, inventory lines 743–783, by call-site identifier prefix):

| Call site | Interface | Procedure | Accepted act | Implementing row(s) | Governing closure | Note |
|---|---|---|---|---|---|---|
| `CALL-DI1-01` | DI-1 | RT-1 | CQ-4 OS-4: holder `ActiveState` and `InvocationID` | `RT1.CQ4.7` | Q3-1 |  |
| `CALL-DI1-02` | DI-1 | RT-1 | CQ-4 OS-1: capture unit `ActiveState`, `InvocationID`, `InactiveEnterTimestampMonotonic` | `RT1.CQ4.8` | Q3-1 | read during the unit's own start-pre (OS-1) |
| `CALL-DI1-03` | DI-1 | RT-2 | AM-0 (i): `LoadState` of three units (one stated act, three unit reads) | `RT2.AM0.5` | Q3-1 | unit that may be unloaded / not yet created (`LoadState`) |
| `CALL-DI1-04` | DI-1 | RT-2 | AM-0 (iii): capture-unit baseline under BSP (the BSP retries are this same site) | `RT2.AM0.12` | Q3-1 |  |
| `CALL-DI1-05` | DI-1 | RT-2 | AK-1: the backstop timer must be `active` | `RT2.AK1.3` | Q3-1 |  |
| `CALL-DI1-06` | DI-1 | RT-2 | AV-1 H-2b baseline recomputation: `unit` key | `RT2.AV1.2` composing `H-BSE.10` | Q3-1, Q3-9 |  |
| `CALL-DI1-07` | DI-1 | RT-2 | AV-1 H-2b baseline recomputation: `manager` key | `RT2.AV1.2` composing `H-BSE.11` | Q3-1, Q3-9 |  |
| `CALL-DI1-08` | DI-1 | RT-2 | `hold-start`: re-read while K is held | `RT2.HS.1` | Q3-1 |  |
| `CALL-DI1-09` | DI-1 | RT-2 | HL observation (the OS-5 decision's re-observation under the lock is this same site run again) | `RT2.HL.3`; re-run `RT2.HL.7` | Q3-1 |  |
| `CALL-DI1-10` | DI-1 | RT-3 | CL-2: capture-unit state | `RT3.CL2` composing `H-CL.2.1`, `H-DI1.1` | Q3-1 |  |
| `CALL-DI1-11` | DI-1 | RT-3 | CL-6: capture unit not active | `RT3.CL6` composing `H-CL.6.3` | Q3-1 |  |
| `CALL-DI1-12` | DI-1 | RT-3 | CL-6 baseline recomputation: `unit` key | `RT3.CL6` composing `H-BSE.10` | Q3-1, Q3-9 |  |
| `CALL-DI1-13` | DI-1 | RT-3 | CL-6 baseline recomputation: `manager` key | `RT3.CL6` composing `H-BSE.11` | Q3-1, Q3-9 |  |
| `CALL-DI1-14` | DI-1 | RT-4 | BS-1: holder `ActiveState` | `RT4.BS1.1` | Q3-1 |  |
| `CALL-DI1-15` | DI-1 | RT-4 | CL-2: capture-unit state | `RT4.CL2` composing `H-CL.2.1`, `H-DI1.1` | Q3-1 |  |
| `CALL-DI1-16` | DI-1 | RT-4 | CL-6: capture unit not active | `RT4.CL6` composing `H-CL.6.3` | Q3-1 |  |
| `CALL-DI1-17` | DI-1 | RT-4 | CL-6 baseline recomputation: `unit` key | `RT4.CL6` composing `H-BSE.10` | Q3-1, Q3-9 |  |
| `CALL-DI1-18` | DI-1 | RT-4 | CL-6 baseline recomputation: `manager` key | `RT4.CL6` composing `H-BSE.11` | Q3-1, Q3-9 |  |
| `CALL-DI1-19` | DI-1 | RT-5 | `attest` precondition: three unit-state reads (one stated act) | `RT5.PRE.1` | Q3-1 | units that may be `not-found` |
| `CALL-DI1-20` | DI-1 | RT-5 | CL-2: capture-unit state | `RT5.CL2` composing `H-CL.2.1`, `H-DI1.1` | Q3-1 |  |
| `CALL-DI1-21` | DI-1 | RT-5 | CL-6: capture unit not active | `RT5.CL6` composing `H-CL.6.3` | Q3-1 |  |
| `CALL-DI1-22` | DI-1 | RT-5 | CL-6 baseline recomputation: `unit` key | `RT5.CL6` composing `H-BSE.10` | Q3-1, Q3-9 |  |
| `CALL-DI1-23` | DI-1 | RT-5 | CL-6 baseline recomputation: `manager` key | `RT5.CL6` composing `H-BSE.11` | Q3-1, Q3-9 |  |
| `CALL-DI2-01` | DI-2 | SA-1 | AP-2: create the transient holder unit | `SA1.OP.2` | Q3-2 |  |
| `CALL-DI3-01` | DI-3 | RT-2 | AK-1: create the backstop timer and service | `RT2.AK1.2` | Q3-3 |  |
| `CALL-DI4-01` | DI-4 | RT-4 | BS-2: disarm after a `st1-verified` record | `RT4.BS2.2` | Q3-4 |  |
| `CALL-DI4-02` | DI-4 | RT-4 | BS-3: disarm after a `hard-stop` record with nothing further removable | `RT4.BS3.1` (decision and invocation), `RT4.BS2.2` (the disarm operation it invokes) | Q3-4 |  |
| `CALL-DI4-03` | DI-4 | RT-4 | BS-4 terminal disarm (`backstop_max` exceeded or `k` > 99) | `RT4.BS4.2` | Q3-4 |  |
| `CALL-DI5-01` | DI-5 | RT-1 | CQ-5: PK/2 seek-not-authorized for `start` — the decision | `RT1.CQ5.2` (PK/2 inside, `H-PK2.4`, `H-PK2.5`) | Q3-5, Q3-6 |  |
| `CALL-DI5-02` | DI-5 | RT-2 | AV-1 positive control: PK/2 seek-authorized for `start` — the decision | `RT2.AV1.3` (PK/2 inside, `H-PK2.4`, `H-PK2.5`) | Q3-5, Q3-6 |  |
| `CALL-DI5-03` | DI-5 | RT-2 | AV-1 negative control: PK/2 first-decisive for `stop` — the decision | `RT2.AV1.4` (PK/2 inside, `H-PK2.4`, `H-PK2.5`) | Q3-5, Q3-6 |  |
| `CALL-DI5-04` | DI-5 | RT-3 | CL-4: PK/2 seek-not-authorized for `start` — the decision | `RT3.CL4` composing `H-PK2.4`, `H-PK2.5` | Q3-5, Q3-6 |  |
| `CALL-DI5-05` | DI-5 | RT-4 | CL-4: PK/2 seek-not-authorized for `start` — the decision | `RT4.CL4` composing `H-PK2.4`, `H-PK2.5` | Q3-5, Q3-6 |  |
| `CALL-DI5-06` | DI-5 | RT-5 | CL-4: PK/2 seek-not-authorized for `start` — the decision | `RT5.CL4` composing `H-PK2.4`, `H-PK2.5` | Q3-5, Q3-6 |  |
| `CALL-DI6-01` | DI-6 | RT-1 | CQ-5: PK/2 seek-not-authorized for `start` — the subject created for it | `RT1.CQ5.2` (PK/2 inside, `H-PROC.1` … `H-PROC.5`) | Q3-6 |  |
| `CALL-DI6-02` | DI-6 | RT-2 | AV-1 positive control: PK/2 seek-authorized for `start` — the subject created for it | `RT2.AV1.3` (PK/2 inside, `H-PROC.1` … `H-PROC.5`) | Q3-6 |  |
| `CALL-DI6-03` | DI-6 | RT-2 | AV-1 negative control: PK/2 first-decisive for `stop` — the subject created for it | `RT2.AV1.4` (PK/2 inside, `H-PROC.1` … `H-PROC.5`) | Q3-6 |  |
| `CALL-DI6-04` | DI-6 | RT-3 | CL-4: PK/2 seek-not-authorized for `start` — the subject created for it | `RT3.CL4` composing `H-PROC.1`, `H-PROC.2`, `H-PROC.3`, `H-PROC.5` | Q3-6 |  |
| `CALL-DI6-05` | DI-6 | RT-4 | CL-4: PK/2 seek-not-authorized for `start` — the subject created for it | `RT4.CL4` composing `H-PROC.1`, `H-PROC.2`, `H-PROC.3`, `H-PROC.5` | Q3-6 |  |
| `CALL-DI6-06` | DI-6 | RT-5 | CL-4: PK/2 seek-not-authorized for `start` — the subject created for it | `RT5.CL4` composing `H-PROC.1`, `H-PROC.2`, `H-PROC.3`, `H-PROC.5` | Q3-6 |  |
| `CALL-DIS-01` | DI-S | SA-2 | OS-6 `stop`: stop-unit call for `rp11-capture-pass-a.service` | `SA2.OP.2` | Q3-7 |  |

Procedure-by-interface matrix (`MD`, same parse):

| Interface | RT-1 | RT-2 | RT-3 | RT-4 | RT-5 | SA-1 | SA-2 | Sites |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DI-1 | 2 | 7 | 4 | 5 | 5 | — | — | 23 |
| DI-2 | — | — | — | — | — | 1 | — | 1 |
| DI-3 | — | 1 | — | — | — | — | — | 1 |
| DI-4 | — | — | — | 3 | — | — | — | 3 |
| DI-5 | 1 | 2 | 1 | 1 | 1 | — | — | 6 |
| DI-6 | 1 | 2 | 1 | 1 | 1 | — | — | 6 |
| DI-S | — | — | — | — | — | — | 1 | 1 |
| **All** | **4** | **12** | **6** | **10** | **7** | **1** | **1** | **41** |

## 3. Per-interface contract

Each interface section states, in order: what is **supported** (`SF`/`MD`/`DR`),
the **request, response, value encoding, completion, cancellation and failure**
semantics that the sources fix, the **`PO3`** obligations proposed for WP-4, and
the **`UF`** gaps that stop the contract. No language, library, binding or
syscall is chosen anywhere in this section.

Common supported facts (all interfaces):

* `SF` R2 §6.2: `StartUnit` and `StopUnit` call `bus_verify_manage_units_async_full` with details `unit` (unit ID) and `verb` (`start`/`stop`) (R2 lines 625–627); the job is queued only after a positive decision.
* `SF` R2 §6.3: only uid 0 or an action owner may pass details to a Polkit check (R2 §6.3, `polkitbackendinteractiveauthority.c:1045–1085`); a root subject is always authorized unless `ALWAYS_CHECK` (`:1234–1238`).
* `SF` D TR-4 (line 940): the system-bus socket is the transport locus. **Nothing more** about client transport, authentication or message framing is stated (`UF-01`).
* `MD` WP-2 §7.1 (inventory lines 729–739): every call is counted as one logical call site. That section defines the count only; it states no failure, cancellation or retry rule (corrected in R1, which had attributed a fail-closed sentence to it).
* `DR` R8 SN-10 (line 2521) and IS-8 (line 3212): a mutating child whose result is `error`, interrupted or indeterminate has an *unknown* effect, no later step may read it as “not created” or “not stopped”, and no retry, repetition or search is granted (C-34). WP-2 carries the obligation unmapped for non-child interactions (inventory §8.1, lines 851–861, rows 854–859; Q6-6, Q6-7; C-33). The non-child mapping is **not decided here**.
* `DR` WP-2 Q4-7 (inventory line 1348): enforcing the class-E deadline `c`, including cancellation, the fail-closed `error` result at expiry and behaviour after expiry, on an in-process interface call is a WP-4 question. Whether the *interface* offers cancellation is WP-3's, and is a `UF`.
* `PO3-C1` Every interface result is exactly one of `ok(value)`, `refused(reason)` or `error(kind)`; there is no fourth state and no implicit success. The *content* of `reason` and `kind` is conditional on `UF-04`.
* `PO3-C2` No interface call carries an elapsed-time bound claimed by WP-3. The WP-2 class-E deadline `c` bounds the historical child wait only; an interface-call bound is a WP-4/WP-5 decision (`UF-05`).

### 3.0 Cancellation and abandonment (common contract, added in R1)

Two different things are called cancellation and this file never merges them.
**Cancelling a client wait** is the client ceasing to wait for, or losing its
connection to, a call or a job result. **Cancelling a manager job** is an
interface-level request that the manager stop a queued or running job. The
sources support neither as an interface fact for DI-2, DI-3, DI-4 or DI-S.

* `PO3-X1` A cancelled client wait, a client disconnection and an unconfirmed outcome are each `error` for the cancelled call; none is `ok` or `refused`. This is a proposed obligation, not an upstream fact; which kind it carries is conditional on `UF-04`.
* `PO3-X2` For a mutating interface (DI-2, DI-3, DI-4, DI-S) cancelling a client wait, a disconnection or an unconfirmed outcome is **never proof that the request had no effect and never proof that a queued job stopped**. A cancelled client wait is not proof that a queued job stopped or that a mutating request had no effect. No silent retry follows from it. Classification: for DI-3 and for DI-4 at BS-2 and BS-3 the child-form rule is `DR` (SN-10, IS-8; C-33, C-34) and its mapping to a non-child interface is Q6-6, not decided; for DI-2, DI-S and DI-4 at BS-4 it is `PO3` (binding through the R1 assignment's fixed boundary, not an upstream fact), and the BS-4 extension of SN-10 stays in Q6-7, not decided.
* `PO3-X3` A cancelled wait on a read (DI-1) yields `error` and never a value (`PO3-1.4`); a read changes nothing, so no unknown-effect question arises for it.
* `UF-05` (expanded): the facts the sources lack for DI-2, DI-3, DI-4 and DI-S are (i) how a client cancels or abandons its wait; (ii) whether an already accepted or queued job continues after that; (iii) how the eventual job result and the mutation's effect are observed; (iv) how cancellation, client disconnection and an unconfirmed outcome map to the accepted `refused`/`error` outcomes and unknown-effect boundaries. Search evidence: none of `CancelJob`, `JobRemoved`, `JobNew`, `GetJob`, `disconnect`, `queued job` occurs in R2, R8, D or W2 (0 in each); the lower-case word `cancel` occurs once in R2, three times in D and once in W2, none as an interface cancellation fact for these four interfaces.

Treatment of every interface:

| Interface | Cancellation treatment | Class | Gap |
|---|---|---|---|
| DI-1 | A cancelled or interrupted read yields fail-closed `error`, never a value (`PO3-1.4`). Proposed obligation, not an upstream fact. How the cancellation is carried depends on the unregistered transport and error facts | `PO3` | `UF-01`, `UF-04` (not `UF-05`; a read has no job) |
| DI-2 | Not supported by any source. Cancel/abandon of the wait, fate of the accepted job, observation of result and effect, and the mapping to `refused`/`error` and unknown effect are the expanded `UF-05`. Abandonment never proves no effect and never permits a silent retry (`PO3-X2`) | `UF` + `PO3` | expanded `UF-05`, `UF-04` |
| DI-3 | As DI-2. The child-form `effect: "unknown"` obligation (SN-10, A-I-16) is `DR`; its mapping is Q6-6 and is not decided | `UF` + `DR` + `PO3` | expanded `UF-05`, `UF-04`; Q6-6 |
| DI-4 | As DI-2, three sites. SN-10 is `DR` at BS-2 and BS-3 (mapping Q6-6); BS-4 is not extended (Q6-7) | `UF` + `DR` + `PO3` | expanded `UF-05`, `UF-04`; Q6-6, Q6-7 |
| DI-5 | Cancellation of the Polkit call is owned by `UF-10`. The proposed obligation that it yields `error` (`PO3-5.3`) is conditional on that fact. `DR` H-PK2.5: an abandon is `error` | `UF` + `DR` + `PO3` | `UF-10` |
| DI-6 | The subject interface has no separate client-wait cancellation fact. Cancellation belongs to the enclosing DI-5 decision (an abandon is `error`, `DR` H-PK2.5; cancelling the DI-5 call itself is `UF-10`) and to the later cleanup of the subject under the accepted SN contract (`DR` H-PROC.1, H-PK2.7: signalled once after the call; a failed, unmade or unreaped subject is abandoned or `reap-unknown`, recorded, living at most 60 s). The mechanics are WP-4's (Q4-1, Q4-8) and are not designed here. What the call conveys about the subject's identity stays `UF-12`, `UF-13`. No additional unsupported fact is registered | `DR` | `UF-10` (via DI-5); `UF-12`, `UF-13` |
| DI-S | As DI-2 (one site, SA-2). The accepted text states no failure contract for the stop call (SA2.OP.2); abandonment never proves the unit was or was not stopped | `UF` + `PO3` | expanded `UF-05`, `UF-04`, `UF-09` |

### 3.1 DI-1 — unit-state read (23 call sites)

*Supported.*

* `DR` H-DI1.1 (inventory line 252): obtain named properties of one named unit, read-only. The properties used are `ActiveState`, `InvocationID`, `InactiveEnterTimestampMonotonic`, `Job`, `LoadState`, `Result`, and for baselines `ExecMainStartTimestampMonotonic` and `TimeoutStartUSec`; these eight are `MD` all present in R2 Appendix A (rows #7, #169, #166, #170, #215, #343, #101, #436; lines 1182, 1344, 1341, 1345, 1390, 1518, 1276, 1611) and none carries `HIDDEN` or `EXPLICIT`.
* `SF` R2 lines 479–480: `systemctl show` issues one `GetAll("")`, and `GetAll` omits properties flagged `HIDDEN` or `PROPERTY_EXPLICIT` (`bus-objects.c:767–783`). `SF` R2 line 481: a `-p` name the manager does not return is skipped and the exit status is still 0.
* `MD` R2 Appendix A has 464 rows and Appendix B 126 rows of which 58 are marked `yes`; no row carries `EXPLICIT` (counted over the appendices; C.1 line 1776 is the legend).
* `DR` H-DI1.2 (line 253): value text is the exact bytes after the first `=` of the printed form, decoded as strict UTF-8; a failed decode is a stop; a property the manager does not report is a stop, enforced by the reader because the tool does not fail.
* `DR` H-DI1.3 (line 254): reads start, stop and change nothing; reading an unloaded unit may load it (R2 §8 (l), line 708); a read made during the unit's own start-pre returns without waiting and reports `activating`, the attempt's `InvocationID` and the earlier τ (R2 §8 (v), line 718).
* `DR` H-DI1.4 (line 255): a satisfied read is never evidence of absence; `InvocationID` of an `inactive` unit may be stale and `InactiveEnterTimestampMonotonic` may read `0` (R2 §8 (k), (s), lines 707, 715).

*Request / response / value encoding / completion / cancellation / failure.*
`PO3-1.1` Request = (unit name, ordered list of property names); response =
for each name either `value(text)` or `absent`, never both, order preserved.
`PO3-1.2` `absent` for a name in the baseline set is a stop (H-DI1.2). `PO3-1.3`
A read completes when all names are answered; no partial result is returned.
`PO3-1.4` A cancelled or interrupted read yields `error`, never a value (a proposed fail-closed obligation, not an upstream fact; §3.0).
Whether the **typed** value maps to the printed text H-DI1.2 expects, how a unit
name resolves to an object (including an unloaded unit), how bus errors are
represented, and whether a per-property read can reach `HIDDEN`/`EXPLICIT`
properties are **not** supported (`UF-02`, `UF-03`, `UF-04`, `UF-14`).

*Stop.* Q3-1 and the DI-1 half of Q3-9 cannot be closed (§5).

### 3.2 DI-2 — create holder unit (1 call site: SA-1)

*Supported.* `DR` SA1.OP.2 (inventory line 583): create the holder `⟨id⟩.service` as a transient system service. `SF` R2 §8 (a), (m) (lines 697, 709): creation is `StartTransientUnit` for a `.service`, which refuses a unit that has a fragment or source path, a job, or is merged (`Unit %s was already loaded or has a fragment file.`). `SF` R2 §8 (q) (line 713): `--wait` uses signal matches and `GetAll`, with no polkit action after the start. `SF` D line 1989: the holder literal.

*PO3.* `PO3-2.1` Refusal because the unit already exists is a distinct `refused(exists)` outcome, not `error`. `PO3-2.2` The call is not repeated after an `error` whose effect is unconfirmed. `PO3-2.3` Completion is observed by a job-completion mechanism whose existence is only half-supported (`UF-05`). `PO3-2.4` Cancelling or abandoning the client wait, or losing the connection, is `error` with unknown effect and never proves the holder was not created, nor that a queued job stopped; it never permits a silent retry (`PO3-X2`; class `PO3`, DI-2 is not named by SN-10, inventory line 854).

*Stop.* The `StartTransientUnit` signature and job mode (`UF-06`), the write-side property names, types, units and exec-command structure (`UF-07`) and the completion mechanism with the cancellation and abandonment semantics (`UF-05` expanded: client-wait cancellation, fate of an accepted job, observation of result and effect, mapping to `refused`/`error` and unknown effect) are absent. Q3-2 cannot be closed.

### 3.3 DI-3 — create backstop timer and service (1 call site: RT-2 AK-1)

*Supported.* `DR` RT2.AK1.2 (line 457): create `⟨id⟩-backstop.timer` firing at `--on-active=⟨R⟩` and `--on-unit-active=⟨R⟩` with `AccuracySec=1s`, and `⟨id⟩-backstop.service` (type `exec`, `Restart=no`, `OOMScoreAdjust=-1000`, `RuntimeMaxSec=⟨S_b⟩`, `TimeoutStopSec=⟨S⟩`, no `TimeoutStartSec=`, role `backstop`). `SF` R2 §8 (d), (j) (lines 700, 706): `RuntimeMaxSec=` deadline and the timer semantics. `SF` D line 2009: backstop literal. `DR` SN-10 / A-I-16: the `effect: "unknown"` obligation applies to this call as a historical child; its mapping is **Q6-6 and is not decided here**. Cancelling or abandoning the client wait, or losing the connection, is `error` with unknown effect (`PO3-X2`; `DR` RT2.AK1.2 for the child form); it never proves the timer or service was not created nor that a queued job stopped, and never permits a silent retry. Carried dependency, not owned by WP-3: the `RuntimeMaxSec` on a timer-started `Type=exec` service (BS-RM) is adopted by DEC-2 but its citation obligation (OH-S2b) is still proposed.

*Stop.* How a timer and its service are created together (naming, ordering, one call or two), and the timer property names and types (the Timer interface is **not** in Appendix A), are absent (`UF-08`), as are `UF-05` (expanded: job completion and the cancellation and abandonment semantics), `UF-06`, `UF-07`. Q3-3 cannot be closed.

### 3.4 DI-4 — disarm backstop timer (3 call sites: BS-2, BS-3, BS-4)

*Supported.* `DR` RT4.BS2.2 (line 531): stop `⟨id⟩-backstop.timer`, the only unit verb the backstop issues; BS-3 (RT4.BS3.1, line 532) invokes the same operation; BS-4 (RT4.BS4.2, line 534) is the terminal disarm (`CALL-DI4-03`). `SF` R2 §6.2 (lines 625–627): the stop verb is Polkit-checked for non-root callers. `DR` WP2-R2-2 (inventory line 27): SN-10 / A-I-16 applies to BS-2 and BS-3 only; whether it extends to BS-4 is **not decided** and is carried as part of Q6-7.

*PO3.* `PO3-4.1` Stopping an already-inactive or not-loaded timer is a distinct outcome whose classification (success vs. refusal) is conditional on `UF-09`. `PO3-4.2` The three sites share one interface definition; they differ only in the surrounding step and its failure contract. `PO3-4.3` Cancelling or abandoning the client wait, or losing the connection, is `error` and never proves the timer was or was not stopped, nor that a queued job stopped; no silent retry (`PO3-X2`). At BS-2 and BS-3 the child-form unknown-effect rule is `DR`; at BS-4 it is `PO3` only, and Q6-7 is not answered.

*Stop.* The `StopUnit` signature, mode and semantics, the already-inactive and not-loaded behaviour, and whether systemd Polkit-checks root are absent (`UF-09`, plus `UF-01`, `UF-04` and `UF-05` expanded to the cancellation and abandonment semantics). Q3-4 cannot be closed.

### 3.5 DI-5 — Polkit decision (6 call sites)

*Supported.* `DR` H-PK2.4 (line 275): ask the authorization authority, as root and without interaction, for action `org.freedesktop.systemd1.manage-units` with details `unit` = `rp11-capture-pass-a.service` and `verb` = the series verb, for the subject of H-PROC.5. `DR` H-PK2.5 (line 276): one outcome — `authorized`, `not-authorized` or `error`; any unparsable result, deadline or abandon is `error`; volume cap 65,536 bytes. `SF` R2 §6.4 (e) (line 656): `pkcheck` exit statuses 0 authorized, 1 not authorized, 2 challenge, 3 dismissed, 126 usage error, 127 error checking; an unprivileged caller passing `--detail` gets a `NOT_AUTHORIZED` *error*, so status 127 (R2 line 656). `DR` R8 §9.3 E-2 (line 3808): the exit-status mapping is a command-line contract that **does not carry over** to an interface. `SF` R2 §6.3: root may pass details; a root subject is always authorized.

*PO3.* `PO3-5.1` Request = (action id, details map with exactly `unit` and `verb`, subject from DI-6, no-interaction flag); response = `authorized | not-authorized | error`. `PO3-5.2` A challenge is `not-authorized`, never `error`, matching the accepted H-PK2.5 table. `PO3-5.3` Cancellation yields `error` (a proposed obligation conditional on `UF-10`; the accepted source says only that an abandon is `error`, H-PK2.5).

*Stop.* The Polkit check method, signature, process-subject encoding, flags, details and cancellation (`UF-10`, which owns cancellation of the Polkit call) and the mapping from the authority's result fields to the three outcomes (`UF-11`) are absent. Q3-5 cannot be closed.

### 3.6 DI-6 — authorization subject (6 call sites)

*Supported.* `DR` H-PROC.5 (inventory line 265): obtain the subject's start time and UID for the authorization call by reading the child's start time from `/proc` (field 22) and its UID; unreadable ⇒ the call is `error`. `DR` H-PROC.4 (line 264): the child handle records PID, process-group and session ID, and `start_ticks` (`/proc/<pid>/stat` field 22), but `start_ticks` there is **optional (PO-SN (d), R8 line 2921), proposed and not accepted**. `SF` R8 PK/2 (lines 2322–2354; Subject 2324). Today the subject reaches the authority as `--process ⟨pid⟩,⟨start-time⟩,⟨uid⟩` (H-PK2.4), a command-line form that does not carry over (E-2). `PO3-6.1` Subject = (pid, start time, uid), all three required; any unreadable component is `error` (H-PROC.5). The accepted source names the `/proc` field but **not** the unit or encoding in which polkitd expects it.

*Cancellation.* DI-6 has no client-wait cancellation fact of its own. Cancellation belongs to the enclosing DI-5 decision (`DR` H-PK2.5: an abandon is `error`; cancelling the DI-5 call itself is `UF-10`) and to the later cleanup of the subject under the accepted SN contract (`DR` H-PROC.1, H-PK2.7; mechanics are WP-4's, Q4-1 and Q4-8, and are not designed here). No additional unsupported fact is registered for it.

*Stop.* The unit and encoding in which a process subject's start time is expressed to the authority, and that `/proc` field 22 is that value (`UF-12`), and polkitd's treatment of a process subject's start time and uid (`UF-13`) are absent. Q3-6 cannot be closed.

### 3.7 DI-S — SA-2 stop-unit call (1 call site)

*Supported.* `DR` SA2.OP.2 (inventory line 595): stop the holder unit at SA-2. `SF` R2 §6.2 (lines 625–627). `PO3-7.1` Same outcome set as DI-4 (`PO3-4.1`). `PO3-7.2` Cancelling or abandoning the client wait, or losing the connection, is `error` and never proves the unit was or was not stopped, nor that a queued job stopped; no silent retry (`PO3-X2`; class `PO3`, DI-S is not named by SN-10, inventory line 859, and the stop call's failure contract is not accepted text).

*Stop.* `UF-09` (stop semantics), `UF-01`, `UF-04`, `UF-05` (expanded: job completion and the cancellation and abandonment semantics). Q3-7 cannot be closed.

### 3.8 Baseline reads (Q3-9)

*Supported.* `MD` the baseline schema (D lines 4160–4186) and value encoding (D line 4286) name the properties read by `H-BSE.10` and `H-BSE.11`; all eight DI-1 properties are visible to `GetAll` (§3.1). *Not supported:* the typed-to-text rule (`UF-03`) and whether a per-property read can reach `HIDDEN`/`EXPLICIT` properties (`UF-14`). Q3-9 cannot be closed.

### 3.9 Baseline acquisition (Q3-11) — fail-closed record

Rows `H-BSE.1`, `.2`, `.3`, `.4`, `.6` (inventory lines 305–310) acquire host identity (nodename, machine-id hash, architecture, kernel release), operator identity (passwd/group/NSS), repository state, package state and the launcher's file identity. Each row states that the tool's mechanism is not stated (inventory lines 305–308, 310). `SF` R2 line 620: group membership is evaluated through NSS at each decision. The authorized sources name **no** direct acquisition mechanism for these (`UF-15` host, `UF-16` operator, `UF-17` repository commit identity and launcher file attributes with the re-read/carried split of `H-BSE.6`, `UF-18` packages). `PO3-11.1` Until a mechanism is supported, each of these five acquisitions is recorded as *unavailable* and the baseline that needs it fails closed; no value is invented.

## 4. Citation matrix

Every `SF` used in §3, with its authorized location. Line numbers are lines of
the cited file in this working tree. `R2` = OH-S2 R2 citation record; `R8` = R8
remediation proposal; `D` = one-host design amendment proposal; `W2` = WP-2
inventory. Version binding: systemd `259.5-0ubuntu3.4`, polkit `127-2ubuntu1.1`.

| Ref | Class | Statement | Source | Used in |
|---|---|---|---|---|
| C-01 | SF | `systemctl show` issues one `GetAll("")` on the unit object | R2 line 479 | §3.1 |
| C-02 | SF | `GetAll` omits `HIDDEN` and `PROPERTY_EXPLICIT` properties | R2 line 480 | §3.1, §3.8 |
| C-03 | SF | a `-p` name the manager does not return is skipped; exit 0 | R2 line 481 | §3.1 |
| C-04 | SF | `StartUnit` has signature `ss` (name, mode) for `systemctl start` | R2 line 585 (S-8) | §3 |
| C-05 | SF | `StartUnit`/`StopUnit` call `bus_verify_manage_units_async_full` with details `unit`, `verb`; job queued only after a positive decision | R2 lines 625–627 | §3.4, §3.5, §3.7 |
| C-06 | SF | shipped defaults of `manage-units`: `auth_admin` / `auth_admin` / `auth_admin_keep` | R2 lines 630–632 | §3.5 |
| C-07 | SF | only uid 0 or an action owner may pass details to `CheckAuthorization` | R2 line 646 | §3.5 |
| C-08 | SF | a root subject is always authorized unless `ALWAYS_CHECK` | R2 line 647 | §3.5 |
| C-09 | SF | group membership is evaluated through NSS at each decision | R2 line 620 | §3.9 |
| C-10 | SF | `pkcheck` exit statuses 0/1/2/3/126/127; unprivileged `--detail` ⇒ 127 | R2 line 656 | §3.5 |
| C-11 | SF | `systemd-run --system` makes a PID-1-supervised service via `StartTransientUnit` | R2 line 697 (a) | §3.2 |
| C-12 | SF | `RuntimeMaxSec=` deadline on `CLOCK_MONOTONIC`, suspended time not counted | R2 line 700 (d) | §3.3 |
| C-13 | SF | timers `--on-active=`/`--on-unit-active=` with `AccuracySec=1s` | R2 line 706 (j) | §3.3 |
| C-14 | SF | failed unit stays loaded with last `InvocationID`; inactive unit may be unloaded | R2 line 707 (k) | §3.1 |
| C-15 | SF | `systemctl show -p` changes nothing but may load an unloaded unit | R2 line 708 (l) | §3.1 |
| C-16 | SF | `StartTransientUnit` refuses a loaded/fragment/jobbed/merged unit: `Unit %s was already loaded or has a fragment file.` | R2 line 709 (m) | §3.2 |
| C-17 | SF | `ExecStart=` only after every `ExecStartPre=` exits 0 | R2 line 711 (o) | §3.1 |
| C-18 | SF | polkit authorizes `StartUnit` once before enqueueing | R2 line 712 (p) | §3.5 |
| C-19 | SF | `--wait` uses signal matches and `GetAll`; no polkit action after `StartUnit` | R2 line 713 (q) | §3.2 |
| C-20 | SF | `InactiveEnterTimestampMonotonic` set only on non-inactive → inactive/failed; `failed`→`inactive` does not set it | R2 line 715 (s) | §3.1 |
| C-21 | SF | read from an `ExecStartPre=+` process during its own start reports `activating` and the attempt's `InvocationID` | R2 line 718 (v) | §3.1 |
| C-22 | SF | the eight DI-1 properties are Appendix A rows #7, #169, #166, #170, #215, #343, #101, #436 | R2 lines 1182, 1344, 1341, 1345, 1390, 1518, 1276, 1611 | §3.1 |
| C-23 | SF | no accepted record cites a client-side contract: bus address and authentication, marshalling, `StartTransientUnit` argument structures, Polkit subject structure, error mapping | R8 line 3808 (E-2) | §6 |
| C-24 | SF | system-bus socket as transport locus (TR-4) | D line 940 | §3 |
| C-25 | SF | holder literal; backstop literal; BS-2 | D lines 1989, 2009, 2025 | §3.2, §3.3, §3.4 |
| C-26 | SF | baseline schema; value encoding; ExecStart normalization | D lines 4160–4186, 4286, 4264 | §3.8 |
| C-27 | SF | PK/2 call (2333), outcome (2337), subject (2324) | R8 lines 2322–2354 | §3.5, §3.6 |
| C-28 | SF | `/proc` field 22 start time for the authorization subject | W2 line 265 (H-PROC.5) | §3.6 |
| C-29 | DR | per-interface intents and failure contracts | W2 rows H-DI1.1–.4 (252–255), SA1.OP.2 (583), RT2.AK1.2 (457), RT4.BS2.2/BS3.1/BS4.2 (531, 532, 534), H-PK2.4/.5 (275, 276), H-PROC.4/.5 (264, 265), SA2.OP.2 (595) | §3 |
| C-30 | SF | SN-10 / A-I-16 for DI-4 at BS-2/BS-3 only; BS-4 extension undecided (Q6-7) | W2 line 27 | §3.3, §3.4 |
| C-31 | MD | Appendix A 464 rows, Appendix B 126 rows (58 `yes`); no `EXPLICIT` flag | counted over R2 lines 1165–1773 | §3.1 |
| C-32 | MD | 7 interfaces, 41 sites, procedure matrix, 34 distinct Q3-tagged rows | parse of W2 lines 146–598, 743–783 | §2, §8 |
| C-33 | DR | SN-10 / A-I-16 child-form unknown-effect rule: DI-3 yes, DI-4 yes at BS-2/BS-3, not stated at BS-4 (Q6-7), DI-2 and DI-S not named; carried unmapped (Q6-6); H-PROC.1, H-PK2.5, H-PK2.7 for the subject and the abandon; Q4-7 for deadline and cancellation enforcement | W2 lines 457, 531, 532, 534, 583, 595, 261, 276, 278, 851–861, 1348, 1364, 1365 | §3 common facts, §3.0, §3.2–§3.7 |
| C-34 | DR | SN-10 effect unknown for a mutating child; IS-8 no retry, no repetition, no search | R8 lines 2521, 3212 | §3 common facts, §3.0 |

Not cited because absent from every authorized source: see §6.

## 5. Q3 closure table

Exactly the nine questions, none invented, none omitted. A question is
**closed** only if every fact it needs is `SF`/`MD`/`DR` and its contract is
fully stated; otherwise it is **not closed** and the blocking facts are named.

| Q3 | Question (WP-2 §12, inventory lines 1325–1337) | Contract state | Blocking `UF` | Section |
|---|---|---|---|---|
| Q3-1 | DI-1 interface, value forms, version-bound citation | **Not closed** | UF-01, UF-02, UF-03, UF-04 | §3.0, §3.1 |
| Q3-2 | DI-2 holder creation | **Not closed** | UF-01, UF-04, UF-05 (expanded), UF-06, UF-07 | §3.0, §3.2 |
| Q3-3 | DI-3 timer and service creation | **Not closed** | UF-01, UF-04, UF-05 (expanded), UF-06, UF-07, UF-08 | §3.0, §3.3 |
| Q3-4 | DI-4 disarm, three sites | **Not closed** | UF-01, UF-04, UF-05 (expanded), UF-09 | §3.0, §3.4 |
| Q3-5 | DI-5 Polkit decision | **Not closed** | UF-01, UF-04, UF-10 (owns Polkit-call cancellation), UF-11 | §3.0, §3.5 |
| Q3-6 | DI-6 subject to DI-5 | **Not closed** | UF-10, UF-12, UF-13 (cancellation via the enclosing DI-5 decision; no additional UF) | §3.0, §3.6 |
| Q3-7 | SA-2 stop-unit call | **Not closed** | UF-01, UF-04, UF-05 (expanded), UF-09 | §3.0, §3.7 |
| Q3-9 | explicit/hidden property reads and printed-form facts | **Not closed** | UF-03, UF-14 (and the UF-01/02/04 read path) | §3.8 |
| Q3-11 | direct on-disk / kernel facts for the baseline | **Closed as fail-closed record**: no mechanism is supported; each acquisition is `unavailable` and the baseline fails closed (`PO3-11.1`) | UF-15, UF-16, UF-17, UF-18 recorded, not blocking by itself | §3.9 |

Result: 0 of 8 interface questions closed; Q3-11 answered as a fail-closed record.

## 6. Unsupported-fact registry

Each entry is the exact missing fact. **Search evidence** for all of them: the
authorized sources of §1 were read in full and searched; R8 line 3808 (E-2) itself
records, from a fixed-string count over R2, the one-host design and D2, that no
accepted record cites a client-side contract. Term counts over R2 / R8 / D / W2:
`GetUnit` 0/0/0/0; `LoadUnit` 0/0/0/0; `StartTransientUnit` 2/1/0/1 (server-side
refusal text only); `StopUnit` 1/0/0/0 (verb name only, R2 line 625);
`CheckAuthorization` 1/1/0/0 (restriction only, R2 line 646; R8 E-2 text); the
Polkit service name and a process-subject kind: 0 in all four; `sd_bus`: 0 in all
four.

| ID | Exact missing fact | Needed by |
|---|---|---|
| UF-01 | Client transport, authentication and message framing used to reach the manager and the authority (only the system-bus socket locus, D line 940, is stated) | Q3-1…Q3-5, Q3-7 |
| UF-02 | How a unit name resolves to the object that holds its properties, including a unit that is not loaded | Q3-1 |
| UF-03 | The wire type of each of the eight DI-1 properties (and of Appendix A/B baseline properties) and the rule from typed value to the printed text H-DI1.2 expects; R2 Appendix A/B carry names, interfaces, flags and source lines but no type signatures | Q3-1, Q3-9 |
| UF-04 | How a bus error is represented and mapped to `refused`/`error` kinds | Q3-1…Q3-5, Q3-7 |
| UF-05 | **Expanded in R1 (same identifier, no renumbering).** For DI-2, DI-3, DI-4 and DI-S: the job-completion mechanism (R2 (q) says only that `--wait` uses signal matches and `GetAll`) **and** the cancellation and abandonment facts: how a client cancels or abandons its wait; whether an already accepted or queued job continues; how the eventual job result and the mutation's effect are observed; how cancellation, client disconnection and an unconfirmed outcome map to the accepted `refused`/`error` outcomes and unknown-effect boundaries. A cancelled client wait is not proof that a queued job stopped or that a mutating request had no effect | Q3-2, Q3-3, Q3-4, Q3-7 |
| UF-06 | The `StartTransientUnit` signature and job mode (R2 gives only the refusal text) | Q3-2, Q3-3 |
| UF-07 | Write-side property names, types and units and the exec-command structure for the holder and backstop service (including `ExecStopPost=`) | Q3-2, Q3-3 |
| UF-08 | How a timer and its service are created together, their naming relation, and the timer property names and types (the Timer interface is not in Appendix A) | Q3-3 |
| UF-09 | The `StopUnit` signature, mode and semantics; the result for an already-inactive or not-loaded unit; whether systemd Polkit-checks a root caller | Q3-4, Q3-7 |
| UF-10 | The Polkit check method, its signature, the process-subject encoding, flags, details encoding and cancellation of the Polkit call (DI-6 cancellation belongs to the enclosing DI-5 decision, §3.0) | Q3-5, Q3-6 |
| UF-11 | The mapping from the authority's result fields to `authorized`/`not-authorized`/`error`, replacing `pkcheck`'s exit statuses (R8 E-2) | Q3-5 |
| UF-12 | The unit and encoding of a process subject's start time, and that `/proc` field 22 is that value (H-PROC.5 names the field; PO-SN (d) is proposed only) | Q3-6 |
| UF-13 | How polkitd treats a process subject's start time and uid (verification, mismatch result) | Q3-6 |
| UF-14 | Whether a per-property read can reach `HIDDEN`/`EXPLICIT` properties that `GetAll` omits | Q3-9 |
| UF-15 | Direct acquisition of host nodename, machine-id hash, architecture, kernel release (H-BSE.1) | Q3-11 |
| UF-16 | Direct acquisition of operator account, group and supplementary-group data through NSS (H-BSE.2) | Q3-11 |
| UF-17 | Direct acquisition of repository commit identity and of the launcher file attributes, and which `H-BSE.6` keys are re-read vs carried (H-BSE.3, H-BSE.6) | Q3-11 |
| UF-18 | Direct acquisition of installed-package name/version/architecture records (H-BSE.4) | Q3-11 |

## 7. WP-4 input table

What WP-4 may take from this file without further source, and what it may not.

| # | WP-4 input | Class | Status |
|---|---|---|---|
| 1 | The closed roster of seven interfaces and 41 sites (§2) | MD | usable |
| 2 | The intent, outcome set and failure contract per interface (§3, `DR`), and the cancellation treatment table (§3.0) with its `DR` rows only | DR | usable |
| 3 | Common result discipline `ok`/`refused`/`error` (`PO3-C1`), the no-bound rule (`PO3-C2`) and the cancellation obligations `PO3-X1`…`PO3-X3` (cancelled wait never proves no effect, no silent retry) | PO3 | needs review |
| 4 | Per-interface `PO3` obligations (§3.1–§3.7) | PO3 | needs review; each conditional on its `UF` |
| 5 | The eighteen `UF` items (§6), `UF-05` expanded to the cancellation and abandonment facts for DI-2, DI-3, DI-4 and DI-S | UF | **must be supplied by an authorized source before any interface is built**; WP-4 may not fill them from memory |
| 6 | Q3-11 fail-closed record (`PO3-11.1`) | PO3 | needs review |
| 7 | Carried, not owned by WP-3: BS-RM citation (OH-S2b); Q6-6 mapping of `effect: "unknown"`; Q6-7 BS-4 extension; the 109 unclassified run-time-varying names (C-4); enforcement of the class-E deadline and of cancellation on an in-process call (Q4-7); subject cleanup mechanics (Q4-1, Q4-8) | — | later packages |

## 8. Reconciliation

| Item | Expected (accepted WP-2) | This file | Result |
|---|---|---|---|
| Interfaces in the roster | 7 (DI-1…DI-6, DI-S) | 7 | match |
| Logical call sites | 41 | 41 (23 + 1 + 1 + 3 + 6 + 6 + 1) | match |
| Q3 identifiers closed or recorded | 9, exactly those listed | 9 (Q3-1, 2, 3, 4, 5, 6, 7, 9, 11) | match; none invented or omitted |
| Q3 identifiers found in WP-2 operation-row tags outside the nine | 0 | 0 | match |
| Q3 tag instances / distinct rows | 38 / 34 | 38 / 34 | match |
| Per-Q3 row counts (§11.4) | 13, 1, 1, 3, 6, 6, 1, 2, 5 | 13, 1, 1, 3, 6, 6, 1, 2, 5 | match |
| Operation rows parsed (§4–§5 of WP-2) | 318 | 318 | match |
| Unsupported facts | — | 18 (`UF-01`…`UF-18`); `UF-05` expanded in R1 | recorded |
| Citation-matrix entries | — | 34 (`C-01`…`C-34`; `C-33`, `C-34` added in R1) | recorded |
| Interfaces with a stated cancellation treatment (§3.0) | 7 | 7 | match |

The 38 tag instances are 34 rows because `H-CL.4.2`, `RT1.CQ5.2`, `RT2.AV1.3` and
`RT2.AV1.4` each carry both Q3-5 and Q3-6.

### 8.1 Q3-tagged rows (every row carrying a Q3 identifier)

| Row | Inventory line | Class | Q3 identifier(s) carried (inventory tag) | Interface | Contract section | Closure state |
|---|---:|---|---|---|---|---|
| `H-DI1.1` | 252 | UA | Q3-1 (`A;Q3-1;Q4-7`) | DI-1 | §3.1 | covered; **not closed** (see §5) |
| `H-DI1.3` | 254 | CN | Q3-1 (`A;Q3-1`) | DI-1 | §3.1 | covered; **not closed** (see §5) |
| `H-PROC.4` | 264 | ID | Q3-6 (`A;Q3-6`) | DI-6 (subject identity) | §3.6 | covered; **not closed** (see §5) |
| `H-PROC.5` | 265 | FS | Q3-6 (`A;Q3-6`) | DI-6 (subject identity) | §3.6 | covered; **not closed** (see §5) |
| `H-PK2.4` | 275 | UA | Q3-5 (`A;Q3-5;Q4-7`) | DI-5 | §3.5 | covered; **not closed** (see §5) |
| `H-PK2.5` | 276 | PR | Q3-5 (`A;Q3-5;Q6-1`) | DI-5 | §3.5 | covered; **not closed** (see §5) |
| `H-BSE.1` | 305 | FS | Q3-11 (`A;Q3-11;Q6-3`) | none (baseline acquisition, Q3-11) | §3.9 | covered; answered as fail-closed record (§3.9) |
| `H-BSE.2` | 306 | FS | Q3-11 (`A;Q3-11;Q6-3`) | none (baseline acquisition, Q3-11) | §3.9 | covered; answered as fail-closed record (§3.9) |
| `H-BSE.3` | 307 | FS | Q3-11 (`A;Q3-11;Q6-3`) | none (baseline acquisition, Q3-11) | §3.9 | covered; answered as fail-closed record (§3.9) |
| `H-BSE.4` | 308 | FS | Q3-11 (`A;Q3-11;Q6-3`) | none (baseline acquisition, Q3-11) | §3.9 | covered; answered as fail-closed record (§3.9) |
| `H-BSE.6` | 310 | FS | Q3-11 (`A;Q3-11;Q6-2`) | none (baseline acquisition, Q3-11) | §3.9 | covered; answered as fail-closed record (§3.9) |
| `H-BSE.10` | 314 | UA | Q3-9 (`A;Q3-9;Q6-2`) | DI-1 (baseline `unit` / `manager` reads) | §3.1, §3.8 | covered; **not closed** (see §5) |
| `H-BSE.11` | 315 | UA | Q3-9 (`A;Q3-9`) | DI-1 (baseline `unit` / `manager` reads) | §3.1, §3.8 | covered; **not closed** (see §5) |
| `H-CL.2.1` | 351 | UA | Q3-1 (`A;Q3-1;Q4-7`) | DI-1 | §3.1 | covered; **not closed** (see §5) |
| `H-CL.4.2` | 356 | UA | Q3-5, Q3-6 (`A;Q3-5;Q3-6;Q4-1`) | DI-5 and DI-6 | §3.5, §3.6 | covered; **not closed** (see §5) |
| `H-CL.6.3` | 363 | UA | Q3-1 (`A;Q3-1;Q4-7`) | DI-1 | §3.1 | covered; **not closed** (see §5) |
| `RT1.CQ4.7` | 417 | UA | Q3-1 (`A;Q3-1;Q4-7`) | DI-1 | §3.1 | covered; **not closed** (see §5) |
| `RT1.CQ4.8` | 418 | UA | Q3-1 (`A;Q3-1;Q4-7`) | DI-1 | §3.1 | covered; **not closed** (see §5) |
| `RT1.CQ5.2` | 420 | UA | Q3-5, Q3-6 (`A;Q3-5;Q3-6;Q4-1`) | DI-5 and DI-6 | §3.5, §3.6 | covered; **not closed** (see §5) |
| `RT2.AM0.5` | 443 | UA | Q3-1 (`A;Q3-1`) | DI-1 | §3.1 | covered; **not closed** (see §5) |
| `RT2.AM0.12` | 450 | UA | Q3-1 (`A;Q3-1;Q4-7`) | DI-1 | §3.1 | covered; **not closed** (see §5) |
| `RT2.AK1.2` | 457 | UA | Q3-3 (`A;Q3-3;Q4-7;Q6-6`) | DI-3 | §3.3 | covered; **not closed** (see §5) |
| `RT2.AK1.3` | 458 | UA | Q3-1 (`A;Q3-1`) | DI-1 | §3.1 | covered; **not closed** (see §5) |
| `RT2.AV1.3` | 474 | UA | Q3-5, Q3-6 (`A;Q3-5;Q3-6;Q4-1`) | DI-5 and DI-6 | §3.5, §3.6 | covered; **not closed** (see §5) |
| `RT2.AV1.4` | 475 | UA | Q3-5, Q3-6 (`A;Q3-5;Q3-6;Q4-1`) | DI-5 and DI-6 | §3.5, §3.6 | covered; **not closed** (see §5) |
| `RT2.HS.1` | 478 | UA | Q3-1 (`A;Q3-1;Q4-7`) | DI-1 | §3.1 | covered; **not closed** (see §5) |
| `RT2.HL.3` | 483 | UA | Q3-1 (`A;Q3-1;Q4-7`) | DI-1 | §3.1 | covered; **not closed** (see §5) |
| `RT4.BS1.1` | 529 | UA | Q3-1 (`A;Q3-1;Q4-7`) | DI-1 | §3.1 | covered; **not closed** (see §5) |
| `RT4.BS2.2` | 531 | UA | Q3-4 (`A;Q3-4;Q4-7;Q6-6`) | DI-4 | §3.4 | covered; **not closed** (see §5) |
| `RT4.BS3.1` | 532 | PR | Q3-4 (`A;Q3-4;Q4-7;Q6-6`) | DI-4 | §3.4 | covered; **not closed** (see §5) |
| `RT4.BS4.2` | 534 | UA | Q3-4 (`A;Q3-4;Q4-7;Q4-11;Q6-7`) | DI-4 | §3.4 | covered; **not closed** (see §5) |
| `RT5.PRE.1` | 558 | UA | Q3-1 (`A;Q3-1;Q4-7`) | DI-1 | §3.1 | covered; **not closed** (see §5) |
| `SA1.OP.2` | 583 | UA | Q3-2 (`A;Q3-2;Q4-7`) | DI-2 | §3.2 | covered; **not closed** (see §5) |
| `SA2.OP.2` | 595 | UA | Q3-7 (`A;Q3-7;Q4-7;Q4-11`) | DI-S | §3.7 | covered; **not closed** (see §5) |

### 8.2 Rows per Q3 identifier

| Q3 | Rows carrying it | Count (this parse) | Count (inventory §11.4) |
|---|---|---:|---:|
| Q3-1 | `H-DI1.1` `H-DI1.3` `H-CL.2.1` `H-CL.6.3` `RT1.CQ4.7` `RT1.CQ4.8` `RT2.AM0.5` `RT2.AM0.12` `RT2.AK1.3` `RT2.HS.1` `RT2.HL.3` `RT4.BS1.1` `RT5.PRE.1` | 13 | 13 |
| Q3-2 | `SA1.OP.2` | 1 | 1 |
| Q3-3 | `RT2.AK1.2` | 1 | 1 |
| Q3-4 | `RT4.BS2.2` `RT4.BS3.1` `RT4.BS4.2` | 3 | 3 |
| Q3-5 | `H-PK2.4` `H-PK2.5` `H-CL.4.2` `RT1.CQ5.2` `RT2.AV1.3` `RT2.AV1.4` | 6 | 6 |
| Q3-6 | `H-PROC.4` `H-PROC.5` `H-CL.4.2` `RT1.CQ5.2` `RT2.AV1.3` `RT2.AV1.4` | 6 | 6 |
| Q3-7 | `SA2.OP.2` | 1 | 1 |
| Q3-9 | `H-BSE.10` `H-BSE.11` | 2 | 2 |
| Q3-11 | `H-BSE.1` `H-BSE.2` `H-BSE.3` `H-BSE.4` `H-BSE.6` | 5 | 5 |

## 9. Acceptance checklist

| # | Required content | Present | State |
|---|---|---|---|
| 1 | Fixed scope, source hierarchy, fact classes, version boundary | §1 | complete |
| 2 | Closed roster mapped to all 41 call sites | §2 | complete |
| 3 | Request, response, value encoding, completion, cancellation, failure per interface | §3, §3.0 | complete **to the extent the sources support**; cancellation treatment stated for all seven interfaces (§3.0); gaps named as `UF`, `UF-05` expanded |
| 4 | Citation matrix | §4 | complete |
| 5 | Exact Q3 closure table, nine ids | §5 | complete as a table; **0 of 8 interface questions closed** |
| 6 | WP-4 input table | §7 | complete |
| 7 | Reconciliation of Q3-tagged rows and call sites | §8 | complete |
| 8 | Acceptance checklist | §9 | this table |
| 9 | Stop-rule result | §10 | `HARD STOP` |
| – | No language, library or syscall chosen | whole file | confirmed |
| – | Q6-6, Q6-7 unanswered; BC-2 later; WP-4…WP-7 not prepared | §1, §3.3, §3.4, §7 | confirmed |

## 10. Stop-rule result

**`HARD STOP`.** The authorized repository sources do not support the facts
`UF-01` … `UF-14` that Q3-1 … Q3-7 and Q3-9 require (the exact statements are in
§6; `UF-05` now includes the cancellation and abandonment semantics of DI-2, DI-3,
DI-4 and DI-S). Cancelling a client wait is not proof that a queued job stopped or
that a mutating request had no effect, and no silent retry follows. This R1
revision preserves the `HARD STOP`. Q3-11's `UF-15` … `UF-18` are recorded in a fail-closed answer. No citation
was manufactured, no gap was deferred silently, no fact was taken from memory and
no research was done. The next authority step is for a maintainer to decide how
the client-side facts are to be supplied by an authorized record; this file does
not make or prepare that decision and does not authorize WP-4 … WP-7.
