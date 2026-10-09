# Proposal — LIT-FULL WP-1 R6 remediation: the audited R3-ROOT boundary, BQ-2 and BQ-3 decision-ready, an unambiguous B2-S/B2-N process-tree result, a cumulative WP-2 gate that requires every applicable prerequisite, and the R4 archival defect closed from controller-created, dated, indexed snapshots

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R6-20261008-15`

Date: 2026-10-08

Executor: Claude Code (Sonnet 5.5) on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation-claude-prompt.md),
11,742 bytes (222 lines), SHA-256 `4cab67cfefdd3975902676f61b7efe4e9d63099348823a4a7361d6eef1271ea6`,
recomputed with `wc -c` and `sha256sum` before any edit and equal to the pin in the
[R6 remediation authority](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation-authority.md)
(itself 3,474 bytes, 61 lines, SHA-256 `04ac208574a812fb36700eea0fae83dc2a9d0f29ce592b84c6c0b313c6c29ef9`).
The R6 prompt corrects the G-1 decision-record filename in the consumed R5 prompt and supersedes it
without altering it; the R5 attempt ended in the `HARD STOP` recorded by the
[R5 hard-stop handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r5-remediation-handback.md).

Durable handback: [`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation-handback.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation-handback.md).

R3 pointer-archive erratum, **unchanged by this assignment**: [`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-pointer-archive-erratum.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-pointer-archive-erratum.md).
This assignment creates no erratum and no snapshot.

Earlier deliverables and reviews, **preserved unchanged**: the
[original WP-1 proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-boundary-proposal.md)
(53,995 bytes, SHA-256 `4c4535b8c1c7f207d6d82e039a9395b0bd97a6bfe5cc3cb33108e1fdd2b34775`)
and [its handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-handback.md); the
[R1 remediation proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-proposal.md)
(75,452 bytes, 997 lines, SHA-256 `121969c4e305a7d2cbba587b82bbaf43ec2124ba5b4250ddfd4a963caf7bdf8c`)
and [its handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-handback.md); the
[R2 remediation proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-proposal.md)
(95,541 bytes, 1,168 lines, SHA-256 `8881f4ba5d96c9be4f1dfb6f79115a43154e633f384ac250e6401d9ae31bacce`)
and [its handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-handback.md); the
[R3 remediation proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-proposal.md)
(111,399 bytes, 1,339 lines, SHA-256 `07f2d4851c3b339f90ba3ceda66c98af349d34ddd75e2886d295de053306c84d`)
and [its handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-handback.md); the
[independent review of the original return](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-lit-full-wp1.md); the
[independent re-review of the R1 remediation](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation.md); the
[independent re-review of the R2 remediation](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation.md); and the
[independent re-review of the R3 remediation](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation.md); the
[R4 remediation proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-proposal.md)
(1,542 lines, 133,795 bytes, SHA-256 `00e15e5cb5e8575d829d7f1fd8ae93d273fd43f536f53308b5a07926c24d8737`)
and [its handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-handback.md); the
[independent re-review of the R4 remediation](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation.md); and the
[R5 hard-stop handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r5-remediation-handback.md).

**Status: a proposal for independent Codex re-review and Peter Duscha's later
decisions. Nothing in it is accepted. WP-1 remains `changes requested` and is not
accepted. BQ-2 and BQ-3 are PENDING PETER'S DECISION, and so are PD-2a, PD-2b and
PD-3; this record decides none of them. It approves no exception (EX-1, EX-2,
EX-3 or BC-4), opens and executes no §0.2 change control, resolves no BC (BC-2
included), establishes no concrete Route 3, selects LIT-FULL for no implementation
and authorizes neither WP-2 nor any later package.**

This document is **cumulative and self-contained**: it carries the R4 remediation
forward with the two R4 re-review findings corrected, and a reader needs the
earlier proposals only to compare. Where this record corrects the original WP-1
return, the correction is listed in §6.4 (**sixteen** corrections, COR-01 … COR-16).
Where it corrects the R1 remediation, the correction is listed in §0.5; the R2
remediation, in §0.6; the R3 remediation, in §0.7; and the R4 remediation, in §0.8.

---

## 0. Outcome

### 0.1 In one page

* **What was asked.** Remediate the two findings of Codex's independent re-review of
  the R4 remediation: **WP1-R4R-1 (Important)** and **WP1-R4R-2 (Optional)**. Close the
  archival defect using the controller-created, dated, indexed snapshots; retire the stale
  checklist item RC-16; and preserve every substantive R4 correction and boundary. No new
  analysis of the boundary was asked for, and none was made. Nothing is accepted, decided or
  authorized.
* **The two findings are each closed (§0.8).**
  * **WP1-R4R-1:** the R4 return replaced the four R4-authorization current-state pointers
    without first creating dated, indexed snapshots, although the R3 erratum's forward control
    required them. The R4-authorization bytes were recoverable from the R4 handback's Appendix A,
    and under the R5 and R6 authorities the controller recovered them into four dated snapshots
    with four archive-index entries. This record verifies them against Appendix A byte for byte,
    identifies them with the four R4-return, four R5-authorization and four R6-authorization
    snapshots (sixteen snapshot/index pairs in all), distinguishes them from the R3 erratum, which
    stays an honest record of bytes the repository does not possess, and carries the forward
    control without weakening it (§0.8.3).
  * **WP1-R4R-2:** cumulative checklist item RC-16 asserted that only the proposal, the handback
    and the four pointers changed, which was the R1 file set. It is retired and replaced by an
    exact R6 file-set assertion (§14, RC-16 and RC-16′).
* **The R4 corrections stand (§0.7, §7.4, §10.1, §10.3).** After B2-N, every in-set act's
  inventoried tree begins at B2-N's loader-free start path and contains no `sudo`; every act
  classified out remains wholly outside the boundary under EX-3; the compact gate requires steps
  1–3 and every applicable item among 4 and 4′; and all sixteen combinations remain consistent
  with U1 through U7.
* **Three decisions, three dimensions (unchanged from R3).**
  * **PD-2a** decides where a `sudo`-started root procedure begins: **B2-F**, at the
    first design-controlled image, or **B2-S**, at `sudo`.
  * **PD-2b** decides, separately for `AP-2` and for the OS-6 `stop`, whether the act
    belongs to the final root-procedure set. **It is required under both PD-2a
    answers.**
  * **PD-3** decides **B3-OUT** or **B3-IN** for the installer class, `H-1R` included.
  * **B2-S by itself decides no membership question.** It puts neither act in the set
    nor out of it. For every act PD-2b puts **in**, B2-N must provide the loader-free
    privileged start that **replaces the current `sudo` start**, and the act's `start` or
    `stop` role stays work for WP-2 … WP-7. For every act PD-2b leaves **out**, **EX-3**
    remains a proposed wider BC-4 boundary exception for that whole act and needs
    complete §0.2 closure. B2-N changes how an included act starts, not whether the act
    is in the set, and it does not erase EX-2 or EX-3.
* **The successor gate is cumulative (§0.2, §2.4, §10.3).** The exact paragraph of the R6
  prompt appears in §2.4 and, word for word, in all four returned pointers. WP-2 may be
  prompted only after independent acceptance of WP-1, the recorded PD-2a, PD-2b and PD-3,
  **every** §0.2 closure the chosen answers require (EX-1, EX-2, EX-3) **and every**
  separately required design prerequisite (B2-N; the installer design). U6 is not
  weakened.
* **The R2, R3 and R4 corrections stand (§0.5 … §0.8).** EX-3 is not an LR-4 exception (LR-4
  reaches DI-2 only when `AP-2` is in the set); governance prerequisites, separate
  design prerequisites and later WP work stay separate; FR-1 is a documentation
  amendment, not a pre-WP-2 design package; `H-1R` is named in PD-3 with no invocation
  literal asserted, its verified-exec-stub invocation remaining an inference outside
  Peter's proposed sentence; COR-01 … COR-16 are **sixteen** corrections; and the
  reproduced R8 count is **eight** lines and **eleven** occurrences.
* **Two numbers, not to be confused.** This prompt required **twelve** complete-read
  records (§1.1). The audit of the original return produced **sixteen** corrections
  (§6.4). They are unrelated.
* **Carried from the R3 and R4 remediations, unchanged in substance.** The complete-record
  audit and its sixteen corrections (§6); the **final proposed sets** (§5): root
  procedures that R8 names **RT-1 … RT-5** (consume, holder, stop-post, backstop,
  `attest`), and **seven** `sudo`-started paths (`attest`, `AP-2`, the OS-6 `stop`, and
  the installer class H-1, RB-1, RS-1, H-1R) with the dispositions of §5.4; the
  plain-language BQ-2 and BQ-3 alternatives and recommendations (§7, §8), still
  pending; and the resolution or conversion of Q-1 … Q-6 and Q-7 (§13).
* **BQ-2 and BQ-3 recommendations (§7, §8) are unchanged in kind and still pending.**
  BQ-2: B2-F with both acts in (B2-F-A), `sudo` a launch preamble excepted from LR-2 and
  a static image for `attest`, `AP-2` and the OS-6 stop. BQ-3: leave the installer class,
  `H-1R` included, outside the set as an exception with HB-1 (B3-OUT). Both
  recommendations **contain exceptions** (EX-1, EX-2), so under §2 they would enter §0.2
  before WP-2.
* **Commissioned facts, unchanged (§3).** BQ-1 is R3-ROOT for the investigation. BQ-4
  permits no dynamic child. Concrete Route 3 remains unestablished. WP-2 through WP-7 are
  separately gated, and WP-9 is Peter's later choice.

### 0.2 Decision and gate flow

| Step | Gate | Applies | Closed by | Effect on WP-2 |
|---|---|---|---|---|
| 1 | independent Codex re-review of this remediation | **always** | Codex, then Peter accepts | WP-1 stays `changes requested` until accepted |
| 2 | BQ-2 recorded: **PD-2a and PD-2b together** (§13.2) | **always**. PD-2b is needed under both PD-2a answers | Peter | a decision is **not** §0.2 approval |
| 3 | BQ-3 recorded: PD-3 (§13.2) | **always** | Peter | the same |
| 4 | **§0.2 change control**, steps 1–5 (§2.3), one complete item per exception | **if** a chosen answer contains an exception: EX-1 (B2-F), EX-3 (each act PD-2b leaves out, under either PD-2a answer), EX-2 (B3-OUT) (§10.0) | Product Owner recommendation and Technical Lead review, Acceptance Authority approval, a new baseline version if the roadmap or release boundary changes | must be **closed before WP-2 may be prompted, authorized or rely on that boundary** |
| 4′ | a separately authorized, reviewed **design prerequisite**: for B2-S, B2-N, a loader-free privileged-start design that is not `sudo`; for B3-IN, a Python-free installer with a loader-free verified-exec equivalent | **if** Peter chooses B2-S, retaining a literal start path, or chooses B3-IN | its own prompt, authority, work ID and Codex review | WP-2 **stays blocked** until it makes the boundary attainable, or Peter withdraws the affected design |
| 5 | WP-2 prompt, authority, work ID, Codex review | only after steps 1–3 **and every applicable item among 4 and 4′** (§10.3) | separate | WP-2 only; WP-3 … WP-7 each separately gated |
| later | BC-2 (PD-1) before any WP-9 selection of LIT-FULL | if a maintainer reads R3-ROOT as a narrowing | Peter | not a WP-2 gate |

Steps 4 and 4′ are independent and can both apply (a B2-S answer that leaves an act out
needs §0.2 for EX-3 **and** B2-N). "Every applicable item among 4 and 4′" means every
§0.2 closure that step 4 requires for the chosen answers **and** every design
prerequisite that step 4′ requires for them, so a combination that needs both stays
blocked until **both** are complete. Step 5 is not satisfied by whichever of the two is
reached first. The row-by-row result for every combination is §10.1, whose mechanical rule
is stated once, and §10.3 verifies every row against step 5.

### 0.3 Decision summary

| Item | Status | Where |
|---|---|---|
| BQ-1 | **recorded**: R3-ROOT, from the commissioned direction | §3 |
| BQ-2 | **pending Peter**, as two decisions. **PD-2a** (where a `sudo`-started procedure begins) and **PD-2b** (whether `AP-2` and the OS-6 stop are root procedures) are independent. Recommendation B2-F-A. **Contains EX-1.** | §7, §9, §13 |
| BQ-3 | **pending Peter** (**PD-3**), `H-1R` named without an asserted invocation. Recommendation B3-OUT. **Contains EX-2.** | §8, §9, §13 |
| BQ-4 | **recorded**: no dynamic-child exception | §3, §11 |
| BC-2 | **unresolved**; no accepted record resolves it (PD-1) | §10, §13 |
| §0.2 for EX-1, EX-2, EX-3 | **not opened, not executed, not approved** | §2, §10 |
| BC-4 | **not approved** and not widened by this record | §10.0 |
| WP-2 | **not authorized** | §2, §12 |
| R3-authorization pointer text (WP1-R3R-3) | **not in the repository**; recorded by erratum, **not reconstructed** | the erratum |
| R4-authorization pointer text (WP1-R4R-1) | **recoverable and recovered**: four controller-created, dated, indexed snapshots, verified byte for byte against the R4 handback's Appendix A | §0.8 |
| R4-return, R5-authorization and R6-authorization pointer text | **snapshotted and indexed** by the controller before each could be replaced: twelve snapshot/index pairs, verified | §0.8 |

### 0.4 What this proposal does not do

It does not decide BQ-2, BQ-3, PD-2a, PD-2b or PD-3, approve EX-1, EX-2, EX-3 or BC-4,
open or execute §0.2, resolve BC-2, accept WP-1, establish concrete Route 3, perform
WP-2's system-call-intent inventory, design B2-N or the installer, add a design,
protocol or external citation, record any host fact, decide whether `AP-2` or the OS-6
`stop` belongs in the set, decide whether `H-1R` belongs in the installer class, or touch
any host. It uses R8's DI-1 … DI-6 delegation map only to define boundaries, as the
prompt allows.

It also does not recreate the missing pre-R3-return pointer snapshots, claim a digest match
that cannot be performed, edit any archived snapshot or archive index, change any decision or
authorize any work through the archival erratum, perform a new boundary audit, invent an
exception or change a recommendation direction. It creates, rewrites and repairs no snapshot:
the sixteen snapshots of §0.8 were verified and left as they were.

### 0.5 Closure of the four R1 re-review findings

| Finding | Severity | The defect in the R1 remediation | The correction in this record | Where |
|---|---|---|---|---|
| **WP1-R1R-1** | Blocking | R1 §10.1 said B2-F-B carries EX-3 for "LR-2 and, for DI-2, LR-4". That contradicted R1's own COR-09, COR-16 and §7.5, and the table is the canonical statement of every LR exception | EX-3 is **not** an LR-4 exception. LR-4 applies to a root procedure in the final set and reaches DI-2 only if `AP-2` is in that set. Under B2-F-B, `AP-2` and/or the OS-6 stop are outside the set, so their exclusion is not a free-standing LR-4 exception. EX-3 is the proposed wider BC-4 boundary exception for whichever whole `sudo`-started acts Peter leaves outside the set. BC-4 is not silently expanded, EX-3 is not BC-3, and neither act's membership is decided. Every exception-bearing choice still needs complete §0.2 closure before WP-2 | §10.0, §10.1; §2.2, §7.4, §9.3, §12.2, §13.2 agree |
| **WP1-R1R-2** | Important | R1 §2.2 headed a column "New design package before WP-2 can be meaningful" and put B2-F-A's `start` and `stop` roles in it as "FR-1, documentation amendment only" | the column and rows are replaced by three separate categories (governance prerequisite; separate design prerequisite; work allocated to WP-2 … WP-7). FR-1 is described exactly as a documentation amendment that records the selected boundary and adds roles to the commissioned work, and each design activity is assigned to WP-2, WP-3, WP-4, WP-5, WP-6 or WP-7 | §2.2, §10.1, §10.2 |
| **WP1-R1R-3** | Important | R1 §9.2 defined the class including `H-1R` as "the installer tool run through the verified-exec stub", promoting an inference to fact | the sentence names `H-1R` expressly and classifies it as a separately authorized root re-record operation, read-only plus record write, implemented as a subcommand of the one installer tool. It asserts no invocation literal. The inference is stated outside the sentence and is labelled an inference | §9.2, §5.3 (IC-4), §5.4, COR-13 |
| **WP1-R1R-4** | Optional | R1 §0.1 gave the number of corrections as 14 where §6.4 enumerates COR-01 … COR-16 | **sixteen** is used in §0.1, §0.5, §6.2, §6.4 and the checklist. No figure other than sixteen is used for the corrections; the one quotation of R1's figure is in this cell's "defect" column | §0.1, §6.4, §14 |

### 0.6 Closure of the two R2 re-review findings

| Finding | Severity | The defect in the R2 remediation | The correction in this record | Where |
|---|---|---|---|---|
| **WP1-R2R-1** | Blocking | R2 §2.2 rows 5 and 6 (B2-S) omitted PD-2b although their work column depended on "the acts PD-2b puts in the set": B2-S plus B3-OUT carried EX-2 only, and B2-S plus B3-IN carried no exception, although each PD-2b "out" answer adds an EX-3 part. R2 §10.1 recorded only PD-2a for B2-S. R2 §12.2 hard-coded both the `start` and the `stop` act as absent under B2-S. The R2 gate said "LR exception", which does not reach EX-3 (a boundary exception, not an LR-4 exception) | PD-2a, PD-2b and PD-3 are three independent decision dimensions and all three are required under every combination. B2-S decides where a procedure begins and no membership question. Under B2-S each act PD-2b leaves out carries EX-3 and a complete §0.2 item, each act it puts in keeps its role in WP-2 … WP-7 after B2-N, and B2-N erases neither EX-2 nor EX-3. One canonical matrix replaces the collapsed rows: three orthogonal tables, a mechanical union rule and sixteen worked rows (§10.1). §2.2, §7.3, §7.4, §9.3, §10.0, §12.2 and §13.2 agree with it. The gate now says "an exception, including EX-1, EX-2 or EX-3 under BC-4" | §2.2, §2.4, §7.3, §7.4, §9.3, §10.0, §10.1, §12.2, §13.2 |
| **WP1-R2R-2** | Optional | R2 §13.1 Q-2 said "9 in R8" although R2 §1.2 and the R2 handback report the reproduced count as eight lines and identify nine as the non-reproducing R1 count | Q-2 now says **8** `sudo -n` lines in R8 (eleven occurrences). The proposal and the handback were searched for any other place that presents nine as the reproduced R8 line count: there is none. §1.2 keeps quoting nine as R1's figure, and keeps the distinction between eight matching lines and eleven occurrences. No conclusion changes | §13.1 Q-2; §1.2 |

**How the R2 rows map to the R3 worked rows (§10.1).** R2 row 1 is F-1, row 2 is F-2, row
3 is F-7, row 4 is F-8, rows 5 and 6 (B2-S) are the eight rows S-1 … S-8, and R2's two
"mixed" rows 7 and 8 are F-3 … F-6. Every F row and every S row has an EX-3 part for each
act PD-2b leaves out.

**Preserved from the R2 remediation without regression** (R3 prompt item 4): EX-3 is not
an LR-4 exception (LR-4 reaches DI-2 only when `AP-2` is in the set); the three categories
G, D and W stay separate; FR-1 is a documentation amendment; `H-1R` is named in PD-3
without an invocation literal and the inference stays outside Peter's proposed sentence;
COR-01 … COR-16 are sixteen corrections, distinct from the complete-read
records of the R3 prompt; BQ-2, BQ-3, EX-1, EX-2, EX-3, BC-4 and BC-2 remain undecided or unapproved;
concrete Route 3 remains unestablished; and no successor is authorized.

### 0.7 Closure of the three R3 re-review findings

| Finding | Severity | The defect in the R3 remediation | The correction in this record | Where |
|---|---|---|---|---|
| **WP1-R3R-1** | Blocking | R3 canonical Table A (B2-S row) said that after B2-N each in-set act begins at B2-N's start path while "`sudo` is inside the tree". B2-N is defined as a loader-free privileged-start design that is not `sudo` and replaces `sudo` for every in-set act, so both statements cannot be true. R3 §12.2 repeated the contradiction: it answered "no" to whether `sudo` is outside an inventoried B2-S tree, then said the tree starts at B2-N rather than `sudo` | One process-tree result, stated once and mechanical. **PD-2a = B2-S** means the *current* `sudo`-started form begins at `sudo` and cannot meet LR-2. **B2-N** is the separate loader-free design that replaces that current start for every in-set act before WP-2 can rely on B2-S. **After B2-N**, an in-set act's resulting inventoried tree begins at B2-N's loader-free start path and contains **no `sudo`**. An act PD-2b classifies **out** is **not started by B2-N**: its current `sudo` plus distribution-client path stays outside the boundary under EX-3 and needs complete §0.2 closure. B2-N changes how an in-set act starts, not whether it is in the set, and does not erase EX-2 or EX-3. B2-S still decides no membership question, and PD-2b remains required for both acts under both PD-2a answers. Table A's false statement is replaced, and §12.2's "`sudo` outside every inventoried tree" row is answered per act without a yes/no contradiction: for in-set B2-S acts `sudo` is **absent** because B2-N replaces it; for out acts the entire existing `sudo` path is outside the boundary under EX-3 and is not inventoried as a root procedure | §2.2, §7.4 (with its process-tree table), §9.3, §10.1 Table A and rule PT, §12.2, §13.2 |
| **WP1-R3R-2** | Blocking | R3 §0.2 step 5 said WP-2 follows "steps 1–3 and 4 or 4′". Several B2-S combinations need both step 4 (§0.2 closure for EX-2 and/or EX-3) and step 4′ (B2-N and/or the installer design), so the compact gate could be read to release WP-2 after only one of them. Union rule U6 and the successor-gate paragraph already stated the cumulative rule | Step 5 now reads "only after steps 1–3 **and every applicable item among 4 and 4′**" and says in words what that means. **§10.3 verifies every one of the sixteen worked combinations against the rule**: all require independent acceptance of WP-1 and recorded PD-2a, PD-2b and PD-3; every exception requires its complete §0.2 item; every B2-S combination requires B2-N; every B3-IN combination requires the installer design; and a combination needing both governance closure and design prerequisites remains blocked until both are complete. U6 and the exact successor-gate paragraph are not weakened, and every gate summary was rechecked against U6 | §0.2, §2.2, §2.4, §10.1 (U6), §10.3, §12 |
| **WP1-R3R-3** | Important | The R3 handback recorded that the R3-authorization wording overwritten in all four current-state pointers was saved only in an external session scratchpad, because the R3 prompt prohibited archive-index work. That conflicts with implementation-plan §16.3, which moves consumed and superseded current-state blocks verbatim to dated, indexed snapshots | The exact pre-R3-return pointer bytes **are not present in the repository** (§1.2 records a search of every ref and of the working tree for the four digests). The erratum records the four pre-edit SHA-256 values exactly as the R3 handback §3 records them, explains which full values exist elsewhere, links the R3 authority, exact prompt, proposal and handback as the durable evidence of the authorization and return, states that it recreates nothing, and states the forward control. It is indexed from all four archive indexes. The controller-created R3-return snapshots are unchanged | the erratum; the four archive-index entries; §1.2; handback §3 |

**Preserved from the R3 remediation without regression** (R4 prompt item 4): PD-2a, PD-2b and
PD-3 remain independent and required in every combination; every act classified out under
either PD-2a answer carries EX-3 and a separate complete §0.2 item; every act classified in
retains its later-WP role; B3-OUT adds EX-2 and B3-IN adds the installer design; EX-3 is not an
LR-4 exception and LR-4 reaches DI-2 only when `AP-2` is in the set; governance prerequisites,
design prerequisites and later WP work stay separate; FR-1 remains a documentation amendment;
`H-1R` is named in PD-3 without an invocation literal; COR-01 … COR-16 remain sixteen
corrections; the reproduced R8 count remains eight lines and eleven occurrences; BQ-2, BQ-3,
EX-1, EX-2, EX-3, BC-4 and BC-2 remain undecided or unapproved; concrete Route 3 remains
unestablished; and no successor implementation is authorized.

### 0.8 Closure of the two R4 re-review findings

| Finding | Severity | The defect in the R4 remediation | The correction in this record | Where |
|---|---|---|---|---|
| **WP1-R4R-1** | Important | The R4 return replaced all four R4-authorization current-state pointers without first creating dated, indexed snapshots, although the R3 erratum it had just recorded states the forward control that current-state text must be snapshotted and indexed before replacement. The R4 handback kept the verbatim text only in its Appendix A, said Appendix A "is not an archive snapshot and is not indexed", and left the creation of compliant snapshots to the controller. That does not satisfy implementation-plan §16.3 or the repository's current-state archive convention. A prompt restriction was a conflict to resolve before replacement, not a reason to defer the archive again | Unlike the R3 gap, the R4-authorization bytes were recoverable. Under the R5 and R6 authorities the controller created four dated snapshots of them and indexed each. This record **verifies** (§0.8.1, §0.8.2) that each was recovered from the exact Appendix A evidence, equals Appendix A byte for byte and by SHA-256, and sits beside its canonical file so its relative links resolve; identifies the four R4-return, four R5-authorization and four R6-authorization snapshots and their index entries; distinguishes all of them from the R3 erratum; and carries the forward control (§0.8.3). It recreates, rewrites and repairs nothing | §0.8.1 … §0.8.3; handback §2, §5, §9 |
| **WP1-R4R-2** | Optional | Proposal §14 carried RC-16, "Only the proposal, the handback and the four pointers changed", which was the R1 file set. The R4 handback correctly records three created and eight changed files | RC-16 is retired and replaced by RC-16′, which states the exact R6 permitted file set (§0.8.4, §14) | §0.8.4, §14 |

#### 0.8.1 The sixteen snapshot/index pairs

Four sets of four. The **R4-authorization** set records the pointers as the R4 assignment made them
current; the **R4-return** set records them as the R4 return left them; the **R5-authorization** set
records them as the R5 authority made them current; the **R6-authorization** set records them as the
R6 authority made them current, which is the text this assignment may replace on a successful return.
Each is verbatim, dated, and kept in the same directory as its canonical file so that its original
relative links continue to resolve. Each is indexed in the archive directory for its pointer.

| Set | Pointer | Snapshot (beside the canonical file) | Bytes | SHA-256 recorded by its archive index | On disk equals index |
|---|---|---|---:|---|---|
| R4-authorization | Handover | [`Handover-information-through-2026-10-08-lit-full-wp1-r4-remediation-authorization.md`](Handover-information-through-2026-10-08-lit-full-wp1-r4-remediation-authorization.md) | 3,638 | `78dd71dcd8de8ee83cc656370a9dd24e115af9f50bc5289215340371ca6cd61f` | yes |
| R4-authorization | status | [`status-through-2026-10-08-lit-full-wp1-r4-remediation-authorization.md`](../project-management/status-through-2026-10-08-lit-full-wp1-r4-remediation-authorization.md) | 4,355 | `9715da2e3cee8ca16bced25f7e56fa8e7178026a48c802c5e1c0cb728215172c` | yes |
| R4-authorization | §20 | [`implementation-plan-through-2026-10-08-lit-full-wp1-r4-remediation-authorization.md`](../implementation-plan-through-2026-10-08-lit-full-wp1-r4-remediation-authorization.md) | 3,850 | `cda0a1d7a3e868783fdb59fa0f9d0aad75eafe12b9ffae0139400fed2761e9f9` | yes |
| R4-authorization | banner | [`disposable-test-server-through-2026-10-08-lit-full-wp1-r4-remediation-authorization.md`](../operations/disposable-test-server-through-2026-10-08-lit-full-wp1-r4-remediation-authorization.md) | 2,881 | `d3ad5e331fefc43f3e162e0402d88a287aec78beb8349402a00a5281b22712e1` | yes |
| R4-return | Handover | [`Handover-information-through-2026-10-08-lit-full-wp1-r4-remediation-return.md`](Handover-information-through-2026-10-08-lit-full-wp1-r4-remediation-return.md) | 4,583 | `c76b70f3bcb347818ec35c7b445e9ef2cdbaca51e451c5c029c59c82d5b2b0e0` | yes |
| R4-return | status | [`status-through-2026-10-08-lit-full-wp1-r4-remediation-return.md`](../project-management/status-through-2026-10-08-lit-full-wp1-r4-remediation-return.md) | 5,475 | `fd6f9f9f0cd1c54b497089767523dbedf845c112835389a5c311d53a9216a6b1` | yes |
| R4-return | §20 | [`implementation-plan-through-2026-10-08-lit-full-wp1-r4-remediation-return.md`](../implementation-plan-through-2026-10-08-lit-full-wp1-r4-remediation-return.md) | 4,963 | `bb2b09e2cd10966f9988edd8355e01c75190bd90e62d951d8c0134684690112c` | yes |
| R4-return | banner | [`disposable-test-server-through-2026-10-08-lit-full-wp1-r4-remediation-return.md`](../operations/disposable-test-server-through-2026-10-08-lit-full-wp1-r4-remediation-return.md) | 4,370 | `9d96fd1b360211737b6cd341984c485aa12282787f7f9fac2bff2b4875f47daa` | yes |
| R5-authorization | Handover | [`Handover-information-through-2026-10-08-lit-full-wp1-r5-remediation-authorization.md`](Handover-information-through-2026-10-08-lit-full-wp1-r5-remediation-authorization.md) | 3,880 | `3bd50f84e0c33ad54407f12859f5d5d3f4b359a003e63495f5ed3cc10c862a4e` | yes |
| R5-authorization | status | [`status-through-2026-10-08-lit-full-wp1-r5-remediation-authorization.md`](../project-management/status-through-2026-10-08-lit-full-wp1-r5-remediation-authorization.md) | 4,551 | `09082c4c6498efd19787ab137e9c90380a2090c93b0917b13a8fd3eee1b2fc7f` | yes |
| R5-authorization | §20 | [`implementation-plan-through-2026-10-08-lit-full-wp1-r5-remediation-authorization.md`](../implementation-plan-through-2026-10-08-lit-full-wp1-r5-remediation-authorization.md) | 4,201 | `a8903307a6fa5b860e031f6106576ffec7da1d084f66be94c2dd1b73ade52d5c` | yes |
| R5-authorization | banner | [`disposable-test-server-through-2026-10-08-lit-full-wp1-r5-remediation-authorization.md`](../operations/disposable-test-server-through-2026-10-08-lit-full-wp1-r5-remediation-authorization.md) | 3,278 | `f6345779ddf3837163642dda3d2490e4fa17958ae595e4de6c80503cb1053877` | yes |
| R6-authorization | Handover | [`Handover-information-through-2026-10-08-lit-full-wp1-r6-remediation-authorization.md`](Handover-information-through-2026-10-08-lit-full-wp1-r6-remediation-authorization.md) | 4,197 | `d39d1d8d533181f4d7d1b5cd71f4cfbd95bfb86f409e0d5f55b200192a74f7ef` | yes |
| R6-authorization | status | [`status-through-2026-10-08-lit-full-wp1-r6-remediation-authorization.md`](../project-management/status-through-2026-10-08-lit-full-wp1-r6-remediation-authorization.md) | 4,881 | `fd698b57b4c90df5b892f21fd8b456141d49c98fa36d6c8e6a786513f545bc02` | yes |
| R6-authorization | §20 | [`implementation-plan-through-2026-10-08-lit-full-wp1-r6-remediation-authorization.md`](../implementation-plan-through-2026-10-08-lit-full-wp1-r6-remediation-authorization.md) | 4,525 | `7d4fb7a229991e81ec55cdf03bd9b0197984756ab24dd4256c335823a8523f34` | yes |
| R6-authorization | banner | [`disposable-test-server-through-2026-10-08-lit-full-wp1-r6-remediation-authorization.md`](../operations/disposable-test-server-through-2026-10-08-lit-full-wp1-r6-remediation-authorization.md) | 3,585 | `fea21e7fce5eca66fc10cfbfcd6b2e1d3b81fb3035dbfa1e72d21f5dce3b7c3f` | yes |

The twelve snapshots of the R4-return, R5-authorization and R6-authorization sets are the
**controller-created transition snapshots** of the R6 acceptance checklist; the four
R4-authorization snapshots are the recovery that closes the R4 defect. All sixteen exist, each
equals the SHA-256 its archive index records, and none was opened for editing, created, rewritten
or repaired by this assignment.

#### 0.8.2 What was verified, and what each set is

* **The four R4-authorization snapshots.** Created by the controller under the R5 remediation
  authority, after the defect was found, from the exact Appendix A evidence (the four
  fenced blocks of the R4 handback). Each was verified for this record by extracting
  its Appendix A block and comparing the bytes with the snapshot: Handover 3,638 bytes (55 lines),
  status 4,355 (71), §20 3,850 (60) and banner 2,881 (42), SHA-256 `78dd71dc…cd61f`, `9715da2e…5172c`,
  `cda0a1d7…61e9f9` and `d3ad5e33…2712e1`, each **identical** to the Appendix A block and to the
  byte count and digest Appendix A records. Every local link in each snapshot resolves from the
  directory in which the snapshot sits, which is the canonical pointer's directory, so the relative-link
  base is correct. **This is a recovery after the replacement, not ex ante compliance:** the R4
  transition itself still lacked its snapshots when it happened, which is the defect WP1-R4R-1 found.
  The recovery closes the evidentiary gap because the bytes were in the repository.
* **They are not the R3 erratum.** The R3 pointer-archive erratum remains the honest record of
  bytes that **the repository does not possess**: the R3-authorization pointer text. Its four pre-edit
  digests cannot be matched to any file, and this assignment neither recovers those bytes, reconstructs
  them nor claims a match. The erratum, and the four R3-return snapshots it lists, are unchanged: the
  erratum still has 151 lines, 10,162 bytes and SHA-256 `eca8aff5fd18b5f2eb3c58684345b5472cca34cff90d33faa74637af57d2df4e`, and each R3-return snapshot
  still equals the digest its index records.
* **The four R4-return snapshots.** Created by the controller before the R5 authority became
  current: the pointers as the R4 return left them, before the independent R4 re-review findings and
  R5 remediation authority replaced them.
* **The four R5-authorization snapshots.** Created by the controller after the R5 authority became
  current, preserving the exact text the R5 assignment would have replaced on return. The R5 attempt
  hard-stopped and replaced no pointer, so the R6 authorization replaced that text; the controller
  verified before it did that each snapshot exactly preserved the displaced pointer and that each
  index digest matched. This record corroborates that from the repository: (a) the R5-authorization
  Handover snapshot's SHA-256 `3bd50f84e0c33ad54407f12859f5d5d3f4b359a003e63495f5ed3cc10c862a4e` equals the digest the R5 hard-stop handback records for
  the Handover it read; (b) the current implementation plan with its §20 replaced by the
  R5-authorization snapshot reproduces the whole-file digest the R5 hard-stop handback records for the
  plan (129,396 bytes, `f2d07b9124cb73c9f05770cd65a8cf29b4526e5a16e95b0011ebe6ace959e1eb`); and (c) the current test-server document with its banner
  replaced by the R5-authorization snapshot reproduces the whole-file digest recorded there for that
  document (9,660 bytes, `f3cb5eea5950c6f4746548e1b5328c6868f381610d68413a19325945e43e4cc1`). No whole-file digest of the R5-era `status.md` was
  recorded, so the status snapshot rests on its index digest alone.
* **The four R6-authorization snapshots.** Created by the controller after the R6 authority became
  current and before this assignment began. **They reproduce the current pointer file or controlled
  block byte for byte.** Before any edit this assignment compared them with the live pointers:
  `docs/review/Handover information` is identical to its snapshot; `docs/project-management/status.md`
  is identical to its snapshot; the live `docs/implementation-plan.md` from the "## 20" heading to
  the end of the file is identical to its snapshot; and the live `docs/operations/disposable-test-server.md`
  begins with its snapshot, byte for byte, the restriction banner being that opening block.
* **Order.** The R5-authorization set was in place and indexed before the R6 authorization replaced
  the R5 pointers, and the R6-authorization set was in place and indexed before this assignment began
  and therefore before it replaced any current pointer. This assignment confirmed the presence,
  index entry and digest of every one of the sixteen snapshots before its first edit, and replaced
  each pointer only after that confirmation. The ordering is recorded by the R6 authority and the R6
  prompt and is confirmed here by finding every snapshot present, indexed and matching when the run
  began.

#### 0.8.3 The forward control, not weakened

**Every current-state transition must have its exact dated, indexed snapshot in place before the
current pointer is replaced.** The snapshot is a verbatim copy kept beside the canonical file and
indexed in the archive directory, as implementation-plan §16.3, `.agents/AGENTS.md` ("Current-state
documents and archives") and the R3 erratum §7 require. This is a mandatory control, not an optional
practice and not a later controller decision. A task prompt may not prohibit it without an approved
change to the governing documents. Two consequences follow for this return:

1. The R6 return replaces the four R6-authorization pointers. The R6-authorization snapshots were in
   place and indexed first, so this transition complies.
2. The four pointers that this return writes become the next text a later authorization will
   replace. **Their exact dated snapshots must be created and indexed before any later authorization
   makes it current.** This assignment is not permitted to create them (the prompt forbids adding
   another snapshot), and it therefore leaves that step as a precondition of the next transition
   that the next authority must satisfy first. It does not defer or relax the control.

#### 0.8.4 RC-16 corrected

The cumulative checklist no longer asserts the R1 file set as the result of R4, R5 or R6. RC-16 is
retired and RC-16′ replaces it (§14): the **exact R6 permitted file set** is two created
deliverables (this proposal and its handback) and the returned current-state pointer edits (the
Handover, `status.md`, §20 of the implementation plan and the restriction banner of the test-server
document). The sixteen controller-created, indexed snapshots are pre-existing prerequisites that this
assignment verified and did not change. For the record, the R4 return created three files and changed
eight (R4 handback §3), and the R5 attempt created one file (a hard-stop handback) and changed nothing
else; neither is the R1 set.

**Preserved from the R4 remediation without regression** (R6 prompt item 3): after B2-N every in-set
act's inventoried tree begins at B2-N's loader-free start path and contains no `sudo` (§7.4, §10.1
Table A and rule PT, §12.2); every act classified out remains wholly outside the boundary under EX-3;
the compact gate requires steps 1–3 and every applicable item among 4 and 4′ (§0.2, §10.3); all
sixteen combinations remain consistent with U1 through U7; PD-2a, PD-2b and PD-3 remain independent
and required in every combination; every selected exception needs complete §0.2 closure and every
selected design prerequisite needs its own authority and independent review; BQ-2, BQ-3, EX-1, EX-2,
EX-3, BC-4 and BC-2 remain undecided or unapproved; concrete Route 3 remains unestablished; and no
successor implementation is authorized.

---

## 1. Sources, method and fact classes

### 1.1 Complete-read evidence

Each of the **twelve** records the R6 prompt requires was read **from the first byte to EOF**, in
bounded, non-overlapping chunks. The tool's output limit forced the chunking; each chunk began at the
line after the previous one, and the last chunk of every file ended at the line count shown, which is
`wc -l` of the file. The digests were taken from the same on-disk bytes, before any edit of this
return. Items 2, 3 and 4 are current-state pointers (§20, the Handover, the restriction banner) that
this return edits; their digests are the **pre-edit** values, and they already carried the R6
authorization (including the gate paragraph of §2.4) when the run began. Item 12 is the existing
`2026-10-07` G-1 decision record, which the R6 prompt names correctly; the R5 prompt's `2026-10-08`
filename, which does not exist, is the typo that the R5 attempt hard-stopped on. The chunk boundaries
are in the handback.

| # | File | Lines | Bytes | SHA-256 |
|---|---|---:|---:|---|
| 1 | `.agents/AGENTS.md` | 700 | 36,014 | `87bab4ab8d67e308af0c59b99c8604235ee84d75cfa12448458b1a04cc88390a` |
| 2 | `docs/implementation-plan.md` (pre-edit; §20 is edited) | 2,628 | 129,720 | `aa3952efc1e33f1ee80a268733b909247a54fdc9981e2fa03f8bcd737b6d57ab` |
| 3 | `docs/review/Handover information` (pre-edit) | 61 | 4,197 | `d39d1d8d533181f4d7d1b5cd71f4cfbd95bfb86f409e0d5f55b200192a74f7ef` |
| 4 | `docs/operations/disposable-test-server.md` (pre-edit; the banner is edited) | 196 | 9,967 | `39263f544cbb6ba4848ed58fee2d5479bf1ef786da94c1b8df81c1889b3bea92` |
| 5 | `phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r5-remediation-handback.md` (R5 hard-stop handback) | 114 | 5,317 | `9a246cb7753f0ceb2c2dcd3bee7dfedcecd4f84a77ccde6e3587cd914ed0acb0` |
| 6 | `project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation.md` (independent R4 re-review) | 77 | 4,393 | `4cfa96502884c132d9b359824ddfa9faa304ae33a1158ff385eefe5ff8ef55e3` |
| 7 | `phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-proposal.md` (R4 proposal) | 1,542 | 133,795 | `00e15e5cb5e8575d829d7f1fd8ae93d273fd43f536f53308b5a07926c24d8737` |
| 8 | `phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-handback.md` (R4 handback) | 487 | 39,519 | `ae99a2df8c13afc7d222c895680d63d167b08b85196ed099199c77a0f051446f` |
| 9 | `phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-pointer-archive-erratum.md` (R3 pointer-archive erratum) | 151 | 10,162 | `eca8aff5fd18b5f2eb3c58684345b5472cca34cff90d33faa74637af57d2df4e` |
| 10 | `project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-authority.md` (R4 authority) | 48 | 2,647 | `2a9a3a2ef0d59a366f3db2ff2fc50d57f15f0dae824d3e48a76ebd2f8aa6a267` |
| 11 | `phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-claude-prompt.md` (R4 prompt) | 245 | 12,936 | `218040bc5bc5ee34e27cb1e1eeaceb66443992f25ebb30629a2053ae7c473620` |
| 12 | `project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md` (G-1 decisions) | 46 | 2,455 | `09234e4acada1b3487f9147f0c8c76110a90dc1dc491e6a02f68892c07bab00e` |

Items 5 through 12 are under `docs/review/` (items 2 through 4 are named with their paths). The R6
prompt itself (222 lines) was read completely and its identity matched its pin before any edit
(header). Further reads, recorded in the handback: the R6 authority (61 lines, 3,474 bytes), to verify
the pin; `docs/project-management/status.md` (76 lines, pre-edit SHA-256
`fd698b57b4c90df5b892f21fd8b456141d49c98fa36d6c8e6a786513f545bc02`), because it is a pointer this
return edits; the four archive indexes, to confirm the sixteen index entries of §0.8.1; and the
sixteen snapshots, opened read-only for the byte comparisons of §0.8.2. No snapshot or index was
opened for editing.

The files were consistent with the identities their authorities name: the R6 prompt matches its
authority pin (11,742 bytes, `4cab67cf…1ea6`), the R4 proposal matches the pin the independent R4
re-review and the R4 handback record (133,795 bytes, 1,542 lines, `00e15e5c…8737`), the R3 erratum
matches the pin the R4 handback records (151 lines, 10,162 bytes, `eca8aff5…df4e`), and the R4 prompt
matches its authority pin (12,936 bytes, 245 lines, `218040bc…3620`).

**Not re-read in this return, and carried from earlier readings.** The R8 proposal and the accepted
one-host design amendment (items 12 and 13 of the R4 prompt), the R3 and earlier remediation
proposals, handbacks, reviews, authorities and prompts, the original WP-1 proposal and handback, the
accepted OH-S2 R2 citation record and the R8 acceptance record. The R6 prompt does not list them.
The R8 and one-host design files were read in full in the R4 return, whose proposal this one carries
forward; here only the fixed-string counts of §1.2 were re-run over them. Every `[R2 §n]` citation in
this record is carried from the R1 remediation and from R8's own citations of that record, not
re-verified.

### 1.2 Method

Repository text only. After the complete reads, a small set of fixed-string checks
was run over the two large files, so that the completeness statements of §5 rest on
counts that can be repeated. They add no fact that the reading did not supply.

| Check (`grep -c -F` lines; `grep -o -F | wc -l` occurrences) | Result |
|---|---|
| `H-1R` in R8 | **0** lines, 0 occurrences |
| `H-1R` in D | 10 lines, 11 occurrences: the activation gate (§4.2.5-R2 (i), line 2140; §4.2.5-R3 (e), line 2699), the drift rows of §4.6.3 (lines 5069, 5071, 5072), the §4.7.2 row (5213), the OH-S4 rows (5393, 5440) and the two closing implications (5677, 6789). **None states an invocation literal.** D §4.6.3 describes it as a "re-record step (read-only plus record write, no file change) under separate authority" whose record is published "by PF into `h1/`", and the OH-S4 row lists it among the subcommands of `rp11_h1.py` |
| `sudo -n` in R8 | 8 lines, 11 occurrences. Literal classes: `sudo -n /usr/bin/systemd-run` (DI-2, AP-2), the `sudo -n python3.14 -I -S -c` stub (BQ-3 text, installer role row, A7), `attest`, and the SSW literals. No literal that D lacks |
| `sudo -n` in D | 24 lines, 29 occurrences. Every literal met in the complete reading is classified in §5.3 and §5.5: the stub (§4.2.4), the AP-2 holder literal (§4.2.5-R2 (e)), the `attest` literal ((i)), the OS-6 `systemctl stop` literal (§4.2.5-R4 (e) and its restatements), and Option C's `systemctl start --wait` (§4.2.5-R3 (c), **not adopted**) |
| `OS-6` in R8 | 2 lines (§12.1 and Appendix B-09): the act is named in R8, but not in R8's §9 enumeration of `sudo`-started paths |
| `AP-2` in R8 | 9 lines: §3 holder row, §7.3 row 5, §7.6 `act_wait_s`, §8.1 step AP-2, §8.2 AW-0, §9.3 DI-2 and E-4, Appendix B-03 and B-04. The §9.1 root list and the §9.6.1 role table do not name it |
| `iii-a` in R8 | 6 lines (§8.2 AW-5, §8.7, §8.8, Appendix B-02, B-03, B-05) |

**A note on the R1 counts.** R1 §1.2 stated 9 lines for `sudo -n` in R8 and 16 lines
for `H-1R` in D. A recount by the commands above gives 8 and 10 lines (11
occurrences each). The difference is in how the earlier counts were taken. No
conclusion changes: `H-1R` is absent from R8 and present in D without a literal,
and no `sudo -n` literal outside §5.3 and §5.5 exists. Neither figure is a
correction in the sense of §6.4.

**Re-run for R3 (WP1-R2R-2).** The checks above were repeated over the same files for this
return and gave the same results: `sudo -n` is **8 lines and 11 occurrences** in R8 and 24
lines and 29 occurrences in D; `H-1R` is 0 lines in R8 and 10 lines (11 occurrences) in D;
`OS-6`, `AP-2` and `iii-a` in R8 are 2, 9 and 6 lines. Nine is the R1 figure and does not
reproduce. R2 §13.1 Q-2 repeated it; §13.1 now says eight. The distinction between the
eight matching **lines** and the eleven **occurrences** is kept wherever either is quoted.

**Re-run for R4.** The same fixed-string checks were repeated over the same files and gave
the same results: `sudo -n` is **8 lines and 11 occurrences** in R8 and 24 lines and 29
occurrences in D; `H-1R` is 0 lines in R8 and 10 lines (11 occurrences) in D; `OS-6`, `AP-2`
and `iii-a` in R8 are 2, 9 and 6 lines. The reproduced R8 count stays eight lines and eleven
occurrences wherever it is quoted; nine remains only R1's non-reproducing figure.

**Re-run for R6.** The same fixed-string checks were repeated over the same two files (R8 4,816
lines, 551,246 bytes; D 7,307 lines, 525,019 bytes) and gave the same results: `sudo -n` is **8 lines
and 11 occurrences** in R8 and 24 lines and 29 occurrences in D; `H-1R` is 0 lines in R8 and 10 lines
(11 occurrences) in D; `OS-6`, `AP-2` and `iii-a` in R8 are 2, 9 and 6 lines. The reproduced R8 count
stays eight lines and eleven occurrences wherever it is quoted. No boundary audit was performed.

**Search for the missing R3-authorization pointer bytes (WP1-R3R-3), carried from R4 and not repeated
in R6.** The four pre-edit
SHA-256 values recorded by the R3 handback §3 and the R3 proposal §1.1 were searched (a) in the
sorted digest list of every file under `docs/` and `.agents/`, and (b) as the SHA-256 of every
committed revision, in every ref (`git rev-list --all`), of the four pointer paths and of the one
stash entry. **No file, committed revision or stash matches any of the four.** The pre-R3-return
pointer bytes are therefore not present in the repository, and the erratum neither reconstructs
nor claims them.

### 1.3 Fact classes

| Tag | Meaning |
|---|---|
| **[A]** | **accepted repository text**, restated with its source. Sources: **R8** (the accepted cumulative proposal), **D** (the accepted one-host design), **R2** (the accepted citation record), **G-1** (the decision record), **Auth** (an authority record). I change nothing in it |
| **[O]** | an **observation about accepted text**: an omission, an ambiguity or a tension. It adds no fact |
| **[N]** | a **new recommendation or analysis** of this record. It is not accepted, and no later document may cite it as accepted |
| **[C]** | a **correction** of the original WP-1 return, with its entry in §6.4 |

No host fact is stated. Nothing here relies on `sudo`'s configuration, on the
linkage of any distribution binary beyond what R8 states, or on any kernel or
glibc behaviour. Where R8 records an absence (MF-9), the absence is repeated.

**Naming.** `[R2 §n]` and "the R2 record" always mean the accepted OH-S2 R2
citation record; the work of this return is called "WP-1 R2". `WP1-R1` and `WP1-R2`
are the findings of the independent review of the original WP-1 return (they head
§2 and §6); `WP1-R1R-1` … `WP1-R1R-4` are the findings of the independent re-review
of the R1 remediation, closed in §0.5.

---

## 2. The successor gate (WP1-R1)

### 2.1 The rule, and what it rests on

* **R8 §9.4**, LIT-FULL row: no baseline decision is needed "beyond Peter's choice
  after readiness. **If BQ-2, BQ-3 or BQ-4 are answered by an *exception*, that
  exception is a §0.2 change.**" [A]
* **R8 §12.2**: a change of the accepted Route 3 boundary "is such a change" (a
  §0.2 change); BC-4 is "except `sudo`-started procedures or the installer class
  from LR-1 … LR-2 (BQ-2, BQ-3)", needed for "any LIT alternative that answers BQ-2
  or BQ-3 by an exception"; each BC "is separate from §12.1, and none can be made by
  accepting this proposal." [A]
* **G-1**: "any proposed exception must instead stop and enter §0.2 change
  control", and the WP-1 proposal "must return the remaining BQ-2 and BQ-3
  interpretations for Peter's explicit approval before WP-2 is authorized."
  Also: "No exception to LR-1 through LR-6 is approved here." [A]
* **Independent review (WP1-R1)**: an exception "changes the accepted security
  boundary; WP-2 may not rely on it until the §0.2 change-log entry, impact
  assessment, Product Owner recommendation, Technical Lead review and Acceptance
  Authority approval have closed, with a new baseline version if required." [A]
* **R1 Auth**: Peter's recorded BQ-2/BQ-3 decisions "and, for any exception-bearing
  choice, completed §0.2 change control are required before WP-2 can be prepared or
  authorized." [A]
* **R2 Auth**: the same sentence, and "This authority does not decide BQ-2 or BQ-3,
  approve EX-1, EX-2, EX-3 or BC-4, open or execute implementation-plan §0.2 change
  control, resolve BC-2, accept WP-1, establish concrete Route 3, authorize WP-2 or
  select LIT-FULL for implementation." [A]
* **R3 Auth**: "The result requires independent Codex re-review. Peter's later recorded
  PD-2a, PD-2b and PD-3 decisions and, for every selected exception-bearing choice,
  completed §0.2 change control are required before WP-2 can be prepared or
  authorized." It adds that the authority "does not decide BQ-2 or BQ-3; decide PD-2a,
  PD-2b or PD-3; approve EX-1, EX-2, EX-3 or BC-4; open or execute implementation-plan
  §0.2 change control; resolve BC-2; accept WP-1; establish concrete Route 3; authorize
  WP-2; or select LIT-FULL for implementation." [A]
* **Independent R2 re-review (WP1-R2R-1)**: for every act Peter leaves outside the set,
  EX-3 "remains a proposed wider BC-4 boundary exception and must complete §0.2 change
  control before WP-2 may be prompted, authorized or rely on that boundary. PD-2b is
  therefore required on every B2-S combination." [A]
* **Independent R3 re-review (WP1-R3R-1)**: "Once B2-N replaces the current `sudo` start for
  an in-set act, the resulting inventoried procedure starts at B2-N's loader-free path and
  contains no `sudo`. An act classified out remains outside the boundary under EX-3 and may
  retain its current `sudo` plus distribution-client path." [A]
* **Independent R3 re-review (WP1-R3R-2)**: replace the step 5 condition with "steps 1–3 and
  every applicable item among 4 and 4′" or equally exact wording, and "Recheck every gate summary
  against U6 so no combination can bypass either governance closure or a design prerequisite." [A]
* **Independent R3 re-review (WP1-R3R-3)**: "Remediation must not invent or silently
  reconstruct missing historical bytes. If the exact pre-edit copies cannot be proved from
  repository evidence, add a dated erratum that records the four hashes from the R3 handback, the
  missing snapshot limitation, the authority/prompt records that preserve the substantive
  authorization, and the forward archival control. Index it from each affected archive." [A]
* **R4 Auth**: "This authority does not decide BQ-2 or BQ-3; decide PD-2a, PD-2b or PD-3;
  approve EX-1, EX-2, EX-3 or BC-4; open or execute implementation-plan §0.2 change control;
  resolve BC-2; accept WP-1; establish concrete Route 3; authorize WP-2; or select LIT-FULL for
  implementation." It adds: "The result requires independent Codex re-review. Peter's later
  recorded PD-2a, PD-2b and PD-3 decisions, complete §0.2 change control for every selected
  exception-bearing choice, and every applicable separately authorized and reviewed design
  prerequisite are required before WP-2 can be prepared or authorized." [A]
* **Independent R4 re-review (WP1-R4R-1)**: the R4 return "again replaced current-state text without
  dated, indexed snapshots"; the prompt restriction "was a conflict to resolve before replacement, not a
  reason to defer the archive again"; and, because the R4-authorization bytes remain recoverable from
  Appendix A, "create dated snapshots in the four canonical archive locations, verify them against
  Appendix A, and add one accurate entry to each archive index. Do this before another current-state
  transition." [A]
* **Independent R4 re-review (WP1-R4R-2)**: a cumulative proposal "should remove RC-16 as no longer
  applicable or replace it with an exact R5 scope assertion; it must not present the old R1 file set as
  the R4/R5 result." The R6 prompt applies the same instruction to R6. [A]
* **R6 Auth**: the R6 prompt "supersedes the consumed R5 prompt without altering it"; the controller
  verified the R5-authorization snapshots and created the four R6-authorization snapshots; and "This
  authority does not decide BQ-2 or BQ-3; decide PD-2a, PD-2b or PD-3; approve EX-1, EX-2, EX-3 or BC-4;
  open or execute implementation-plan §0.2 change control; resolve BC-2; accept WP-1; establish concrete
  Route 3; authorize WP-2; or select LIT-FULL for implementation." [A]

### 2.2 The gate: three categories and three decision dimensions

Three categories are kept strictly apart in this section and in §10. They answer
different questions and are not interchangeable.

| Category | What it is | What belongs in it |
|---|---|---|
| **G, governance prerequisite before WP-2** | a recorded decision or a closed governance process that must exist before WP-2 may be prompted or authorized | independent acceptance of WP-1; Peter's recorded BQ-2 and BQ-3 decisions, that is **PD-2a, PD-2b (for both acts) and PD-3**; and complete §0.2 closure for every exception the chosen answers contain (EX-1, EX-2, EX-3) |
| **D, separate design prerequisite before WP-2** | a design that does not exist in any accepted record, must be separately authorized and reviewed, and without which the selected boundary cannot be attained | **B2-N**, a loader-free privileged-start design that is not `sudo`, for B2-S; and the **Python-free installer with a loader-free verified-exec equivalent**, for a B3-IN path |
| **W, work allocated to WP-2 … WP-7 after the gate** | work the commissioned readiness sequence performs once G (and D, where it applies) are met | RT-1 … RT-5; the `start` and `stop` roles of every act PD-2b puts in the set (FR-1); and, for B3-IN, the installer's operations: their inventory (WP-2), interfaces (WP-3), images (WP-4), proof method (WP-5), mapping (WP-6) and estimate (WP-7) |

An *exception-bearing* answer is one that excludes any program or act from the
boundary (EX-1 `sudo`'s loader; EX-2 the installer class; EX-3 a whole
`sudo`-started act, §10.0). A *literal* answer is one that excludes nothing and
therefore needs a start path that is loader-free from its first process. The
definitions are in §10.0.

**The three decision dimensions.** They are independent. **All three are required,
recorded, before WP-2 in every combination.** None drops out because of another
dimension's answer.

| Dimension | What it decides | Answers | Required before WP-2 |
|---|---|---|---|
| **PD-2a** | where a `sudo`-started root procedure begins | **B2-F**, at the first design-controlled image; **B2-S**, at `sudo` | always |
| **PD-2b** | separately for `AP-2` and for the OS-6 `stop`, whether the act belongs to the final root-procedure set | for each act, **in** or **out**: four combinations | **always, under both PD-2a answers** |
| **PD-3** | whether the installer class (H-1, RB-1, RS-1, `H-1R`) is among the root procedures | **B3-OUT**, **B3-IN** | always |

**B2-S decides no membership question.** It puts neither `AP-2` nor the OS-6 `stop` in
the set or out of it, and it does not make the `start` or `stop` role absent: under B2-S
their presence follows PD-2b. B2-N changes **how** an included role starts, not
**whether** the role is in the set. **Process-tree result (WP1-R3R-1).** B2-S means the
*current* `sudo`-started form begins at `sudo` and cannot meet LR-2; B2-N is the separate
design that replaces that current start for every in-set act. After B2-N an in-set act's
inventoried tree begins at B2-N's loader-free start path and contains **no `sudo`**. An act
PD-2b leaves out is not started by B2-N: its current `sudo` plus distribution-client path is
wholly outside the boundary under EX-3. §7.4 states this once; §10.1 rule PT applies it.

**FR-1 is in category W for its design activities and is not in category D.** It is
a documentation amendment that records the selected boundary and adds the `start`
and `stop` roles to the commissioned work (§10.2). It is not a completed pre-WP-2
design package, and it designs nothing. B2-F with both acts in has **no category D
item**.

**The canonical matrix is §10.1.** It states, for every combination of the three
dimensions and by one mechanical rule, the exceptions and their complete §0.2 items, the
separate design prerequisites, the roles and activities allocated to WP-2 … WP-7, and the
resulting WP-2 status. It is not restated here, so that there is exactly one.

[N] Any combination that contains EX-1, EX-2 or EX-3 needs **complete §0.2 closure
before WP-2 may be prompted, authorized or rely on that boundary**. EX-3 is a
BC-4-family **boundary** exception for whole `sudo`-started acts left outside the set. It
is **not** an LR-4 exception (§10.0), and the gate (§2.4) therefore says "an exception",
not "an LR exception". **B2-S is not by itself exception-free:** it carries EX-3 for every
act PD-2b leaves out, and EX-2 under B3-OUT. The only combination with no exception at
all is B2-S with both acts in and B3-IN (row S-2 of §10.1), and that is exactly the
literal no-exception LIT-FULL of the gate: it is blocked on category D.

### 2.3 What §0.2 requires, and what a Peter decision is not

Implementation-plan §0.2 requires, for a material change to scope, authority,
privacy, architecture, data ownership, release criteria, phase order or target
range: **(1)** a change-log entry identifying requester, reason and affected
requirements; **(2)** an impact assessment for scope, dependencies, estimate, risk,
testing, migration and operations; **(3)** a Product Owner recommendation and
Technical Lead review; **(4)** Acceptance Authority approval before the change
becomes effective; and **(5)** a new baseline version when the roadmap or release
boundary changes. [A]

* A recorded Peter decision on BQ-2 or BQ-3 **is not** §0.2 approval. It names the
  boundary. §0.2 makes an exception effective.
* This record **does not** open §0.2, draft its change-log entry or perform its
  impact assessment. Whether step 5 (a new baseline version) is needed is for that
  assessment to find; this record does not decide it.
* Until §0.2 closes, an exception is a *proposal*, not a boundary that WP-2 may
  assume. WP-2's inventory must not be prepared on the assumption that `sudo` or
  the installer class is outside the tree.
* A **literal** answer is not made available by choosing it. It needs the design
  of step 4′, which no accepted record contains (§7.4, B2-N).

### 2.4 The exact gate text carried into all four pointers

> **Gate before WP-2.** Independent Codex re-review of the R6 remediation and Peter's
> recorded BQ-2 and BQ-3 decisions, including PD-2a, PD-2b and PD-3, are always
> necessary. If either chosen answer contains an exception, including EX-1, EX-2 or EX-3
> under BC-4, the complete implementation-plan §0.2 change-control process must close
> before WP-2 may be prompted, authorized or rely on that boundary. A Peter decision on
> BQ-2 or BQ-3 is not by itself §0.2 approval. Every separately required design
> prerequisite must also exist under its own authority and independent review before
> WP-2 may rely on it. If Peter retains literal no-exception LIT-FULL, WP-2 remains
> blocked until the required loader-free privileged-start and, where B3-IN is selected,
> installer designs make the boundary attainable, or Peter withdraws the affected
> design. BC-2 remains unresolved for any later WP-9 selection. WP-1 remains
> changes-requested and is not accepted; BQ-2 and BQ-3 are undecided.

This is the paragraph of the R6 prompt, word for word. Against the R4 paragraph it changes one
phrase only, "the R4 remediation" becoming "the R6 remediation". It keeps the sentence "Every
separately required design prerequisite must also exist under its own authority and independent
review before WP-2 may rely on it" and the naming of "the required loader-free privileged-start and,
where B3-IN is selected, installer designs" as the designs whose existence makes the boundary
attainable. It weakens nothing.

---

## 3. The commissioned facts, recorded

| ID | Recorded as | Source |
|---|---|---|
| **BQ-1** | **R3-ROOT.** The investigated path is LIT-FULL under R3-ROOT, not LIT-DR1. The `ubuntu`-run entry may remain Python and is **outside** the root-procedure set | G-1; WP-1 prompt "Fixed direction" [A] |
| **BQ-4** | **no dynamic child** in any root procedure's process tree. LIT-FULL satisfies LR-1 … LR-6 literally, so LR-2 admits no exception for a child. Any proposed exception must stop and enter §0.2. No SCDC or other exception is introduced | G-1; R8 §9.4 LIT-FULL row, §12.2 BC-3 "Not needed for LIT-FULL" [A] |
| Concrete Route 3 | **unestablished.** The standing `HARD STOP: concrete Route 3 not established` remains | R8 acceptance; Auth [A] |
| WP-2 … WP-7 | commissioned as a sequence, each needing its own prompt, authority, work ID and Codex review. WP-9 is Peter's later choice | G-1; R8 §9.5, §11 [A] |
| SSW, SCDC, ACCEPT-X1 | not selected; scope-change alternatives | R8 §9.4 [A] |
| WITHDRAW | available only as a later decision of Peter's | R8 §9.4, §12.2 BC-5 [A] |

**LR-1 … LR-6** [A: R8 §9.2], restated so that §§5 … 12 read alone. For every root
procedure *p*: **LR-1** no CPython in *p*'s process tree; **LR-2** no dynamic loader
in *p*'s process tree, so every image *p* executes, children included, is static, or
*p* performs the function itself; **LR-3** RH-1 … RH-3 hold for each image (RH-1:
only reviewed literals reach any image's environment; RH-2: descriptors 0, 1, 2
checked and every descriptor ≥ 3 closed before the first state operation; RH-3:
signal dispositions, mask, `umask` and working directory fixed); **LR-4** every
function *p* delegates to a child today (DI-1 … DI-6) is performed in-process or by
a cited loader-free interface; **LR-5** the accepted behaviours are preserved by a
stated mapping; **LR-6** each image passes the D9 chain and PO-17.

[N] LR-2 speaks of *p*'s **process tree**. Where *p* begins therefore decides what
is inside the tree. R8 §9.3 says so in its own words: "Treating `sudo`'s own loader
as outside the procedure is an exception to LR-2 and needs to be stated as one."

---

## 4. The R3-ROOT entry boundary (not a root procedure)

This section exists so that no reader mistakes the `ubuntu`-run entry for a root
procedure. **It is not in the root-procedure set, and nothing in §§5 … 12 applies to
it.**

| Item | Statement | Source |
|---|---|---|
| Role | **entry** | R8 §9.6.1 [A] |
| Started by | PID 1, the capture unit's `ExecStart=` | R8 §9.6.1 [A] |
| Runs as | `ubuntu` | R8 §9.1 table [A] |
| Privilege state | static `rp11-launch`, `ubuntu`, `NoNewPrivileges` | R8 §9.6.1 entry row; D TR-8 [A] |
| First image | `rp11-launch` (static), which then `execve`s `python3.12 -I -S …/rp11_entry.py` today; the accepted literal is already marked for replacement | R8 §9.6.1 [A] |
| Under R3-ROOT | unchanged in kind. The literal retarget to `/usr/bin/python3.14` is **the only source delta of the entry image** (Role A, A1) | R8 §9.6.1, §9.6.2 A1 [A] |
| Environment | `rp11-entry-env/1` | R8 §9.6.1 [A] |
| What binds it | PO-12′ and PO-19, **narrowed to the entry**; the consumer set of MF-1, MF-2, MF-4 narrows with them | R8 §9.8, §10 [A] **[C] COR-08** |
| Why it is not a root procedure | the R3-ROOT set is "the root procedures that touch the grant and the activation mechanism"; the entry is not root | R8 §9.1 [A] |
| If BQ-1 were R3-DR1 | the entry becomes Python-free and A1 … A5 obsolete. That is WP-8, **not commissioned** | R8 §9.4 LIT-DR1, §9.5 WP-8 [A] |

**The boundary between the entry and the root set** [A+O]. CP (RT-1) is started by
PID 1 as `ExecStartPre=+` of the same capture unit, as root, before the unit's
`ExecStart=` runs the entry as `ubuntu` (R8 §9.6.1; R2 §8 (n), (o)). They share a
unit and nothing else. The entry's PO-12′ and PO-19 obligations do not discharge
any obligation of CP, and CP's obligations under LIT-FULL do not touch the entry.

**Also outside the set, for the same reason** [A: R8 §7.3 row 21; **[C] COR-02**]:
the executor's verification reads, which row 21 lists as **AP-0, H-2 and H-2b**.
They are unprivileged and interactive. **AV-1 is not among them**: it is a step of
the holder (R8 §8.1 Machine H, step AV-1; D §4.2.5-R2 (d)) and therefore part of
RT-2.

---

## 5. The audited procedure sets

### 5.1 Reading of the tables

* *Accepted name* is the name in R8 and D.
* *Caller* is who causes the process to start.
* *Current first root image* is what the accepted text runs first as root. The
  accepted text names `/usr/bin/python3.12`, a literal R8 already marks for
  replacement; its replacement by `python3.14` is **refuted for the root roles**
  (R2 §10.4, §15.4 X-1) [A: R8 §9.6.1]. For every unit-started row it is a
  distribution CPython started through the dynamic loader, with `rp11_h1.py` as its
  script.
* *Controlled image today?* asks whether the first root image is an image the
  project builds and pins. **For every row below the answer is no**: the first image
  is a distribution program. [N: reading of R8 §9.6.1's "accepted today" column]
* *Controlled first image (LIT-FULL)* is R8 §9.6.1's LIT-FULL column: a static
  image that performs the procedure itself. It is a **requirement, not a design**.
  Its name, path and size are WP-4's [A: R8 §9.6.1].
* *DI* lists the delegations of R8 §9.3 that the procedure uses. It is a boundary
  aid, not WP-2's inventory.

### 5.2 The root procedures that R8 names: RT-1 … RT-5

| ID | Accepted name | Caller | Current first root image | Controlled first image (LIT-FULL) | DI-1 … DI-6 used |
|---|---|---|---|---|---|
| **RT-1** | **consume** (CP: CQ-0 … CQ-7) | PID 1, the capture unit's `ExecStartPre=+` | `python3.12 -I -S …/rp11_h1.py consume`, under PID 1's open environment block | a static image performs CQ-0 … CQ-7 and DI-1, DI-5, DI-6 itself; RH-1 … RH-3 | DI-1 (CQ-4), DI-5 (CQ-5), DI-6 (PK subject) |
| **RT-2** | **hold** (the holder: ACT, HL, IGR, GRR, **and AV-1**) | PID 1, the transient holder unit that AP-2 creates | `python3.12 -I -S …/rp11_h1.py hold ⟨id⟩ ⟨a2⟩` | a static image performs the holder, IGR, GRR and DI-1, DI-3, DI-5, DI-6 itself | DI-1 (BSP, HL, `hold-start`, the timer `show`), **DI-3** (AK-1, the backstop `systemd-run`), DI-5 (AV-1), DI-6 |
| **RT-3** | **stop-post** (CL, trigger `stop-post`; CL-G, GP-R3) | PID 1, the holder unit's `ExecStopPost=` | `python3.12 -I -S …/rp11_h1.py deact ⟨id⟩ ⟨a2⟩ stop-post` | a static image performs CL and DI-1, DI-5, DI-6 | DI-1 (CL-2, CL-6), DI-5 (CL-4, GP-R3), DI-6 |
| **RT-4** | **backstop** (BS-1 … BS-4, and CL, trigger `backstop`) | PID 1, the service that the backstop timer starts (the holder creates the timer at AK-1) | `python3.12 -I -S …/rp11_h1.py backstop ⟨id⟩ ⟨a2⟩` | a static image performs BS, CL and DI-1, **DI-4**, DI-5, DI-6 | DI-1 (BS-1), **DI-4** (BS-2, BS-3), DI-5, DI-6 |
| **RT-5** | **attest** (CL, trigger `attest`; its first act is CL-G) | the executor / operator, interactive, `sudo -n`; no unit | `sudo -n /usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_h1.py deact ⟨id⟩ ⟨a2⟩ attest` (the installed tool, **by path**; D §4.2.5-R2 (i)) | **BQ-2**: a static image after `sudo`, or another start path | DI-1 (CL-2, CL-6), DI-5 (CL-4, "attestation"), DI-6, per R8 §9.3's "Used by" cells and §7.5a.1's callers [O] |

[A] Sources: R8 §9.1, §9.3, §9.6.1, §8.1, §7.5a.1; D §4.2.5-R2 (d), (e), (f), (i);
R2 §8. RT-1 … RT-4 are started by PID 1, the manager, which is not a procedure of
the set (it is the trusted supervisor behind every accepted unit guarantee, R2 §8,
and RO-3 is its named outside-the-guarantee case, R8 §13.1). The first thing in
the procedure's tree is the image the unit names. A static image there satisfies
LR-1 … LR-3 with nothing dynamic before it. **No BQ-2 exception arises for RT-1 …
RT-4.** [N] That is the sense in which "LR-1 … LR-6 literally" is attainable for
four of the five procedures R8 names.

### 5.3 The `sudo`-started paths: seven

| ID | Act | Caller | Literal in the accepted record | Dynamic first program after `sudo` | In R8 §9.1 list? | In R8 §9.6.1 role table? | In R8 §9.3 E-4? |
|---|---|---|---|---|---|---|---|
| **RT-5** | `attest` | the executor, interactive | `sudo -n /usr/bin/python3.12 -I -S …/rp11_h1.py deact ⟨id⟩ ⟨a2⟩ attest` [D §4.2.5-R2 (i)] | CPython (today) | **yes** | **yes** | **yes** |
| **SA-1** | **AP-2**, creating the holder unit | the executor, privileged | `sudo -n /usr/bin/systemd-run --system --no-ask-password --quiet --unit=⟨id⟩ --service-type=exec … ⟨holder command⟩` [D §4.2.5-R2 (e); R8 §9.7 repeats it for SSW] | `systemd-run` (E-4: dynamic; see COR-12) | **no** | **no** | **yes** ("AP-2's `sudo systemd-run`") |
| **SA-2** | the **OS-6 interruption**: a root `stop` of the running pass | the executor, under A-2, only under OC-1 … OC-3 | `sudo -n /usr/bin/systemctl stop rp11-capture-pass-a.service` [D §4.2.5-R4 (e), R6 (b)] | `systemctl` (dynamic: D §4.1.3 TR-4, via R8 §9.3) | **no** | **no** | **no**, but the act is named in R8 §8.2 AW-5 and Appendix B-02, B-03, B-05, and OS-6 is left unchanged by §12.1 |
| **IC-1** | **H-1** | the executor | `sudo -n /usr/bin/python3.12 -I -S -c '⟨verified-exec stub⟩' install …` [D §4.2.4; R8 §9.6.1, A7] | CPython running the stub | no | **yes** (installer class) | **yes** (installer class) |
| **IC-2** | **RB-1** | the executor, separately authorized | the same stub, subcommand `rb1` [D §4.2.4, §4.6.2-R1] | CPython | no | **yes** | **yes** |
| **IC-3** | **RS-1** (the read-only recovery `scan`) | the executor | "runs as root through the verified-exec stub" [D §4.6.2-R1] | CPython | no | **yes** | **yes** |
| **IC-4** | **H-1R** (the re-record step) | the executor, separate authority | **no literal is stated.** The design makes it a subcommand of the one tool, "read-only plus record write, no file change" [D §4.6.3, OH-S4 row]. Run by the same stub: **[O] inferred**, not stated | CPython (inferred) | no | **no** | **no** |

[A] for every cell with a source. The IC-4 invocation is an **inference** (COR-13):
no accepted record states it, and **no sentence that Peter is asked to approve in §9
relies on it** (WP1-R1R-3).
**R8 §9.3 (E-4) names three groups of `sudo`-started paths: `attest`, `AP-2`, and
the installer class.** SA-2 and IC-4 are the two members that the accepted record
holds but R8's §9 enumeration does not classify.

### 5.4 Disposition of the seven named items

"Proposed" is [N] and **pending Peter**. "Fixed" is already settled by an accepted
record.

| Item | Accepted source | Status in R8 | Proposed disposition | Decided by |
|---|---|---|---|---|
| **attest** | D §4.2.5-R2 (i); R8 §9.1, §9.6.1 | a root procedure of the set; `sudo`-started | **in the set (fixed)**. BQ-2 decides **where it begins**. Under the recommendation: a static `attest` image after `sudo` | R8 (membership); PD-2a (start) |
| **AP-2** | D §4.2.5-R2 (e); R8 §8.1 | named a `sudo`-started path (E-4); has a DI row (DI-2); **not** in the §9.1 list or the §9.6.1 table | **in the set, as a static `start` role** (B2-F-A). It must be classified; it cannot stay unclassified | **PD-2b** |
| **OS-6 stop** | D §4.2.5-R4 (e), R6 (b); R8 §12.1 (unchanged), App. B-03 | an accepted act, left unchanged by §12.1, **not** classified as a `sudo`-started path; **no DI row** | **in the set, as a static `stop` role** (B2-F-A). It touches neither the grant nor ACT (the grant was consumed before the pass), so the alternative "not a root procedure of the boundary" is also coherent and is stated (§7.4) | **PD-2b** |
| **H-1** | D §4.2.4, §4.2.4-R1; R8 §9.6.1, §13.1 HB-1 | installer class; membership is BQ-3 | **outside the set**, as exception EX-2 with HB-1 (B3-OUT) | **PD-3** |
| **RB-1** | D §4.6.2-R1; R8 §9.6.1, HB-1 | installer class | **outside the set**, same answer | **PD-3** |
| **RS-1** | D §4.6.2-R1; R8 §9.6.1, HB-1 | installer class | **outside the set**, same answer. It is read-only; that does not change the class | **PD-3** |
| **H-1R** | D §4.6.3; §4.2.5-R2 (i) gate; OH-S4 row | **not named** in R8 (0 of 4,816 lines) | **same answer as the class**, but **named expressly** in Peter's BQ-3 sentence, so that it is not silently covered. The sentence classifies it only as far as the accepted record goes and **asserts no invocation** (§9.2) | **PD-3** |

### 5.5 Other root or privileged acts considered, and why they are not in either set

| Act | Where | Why it is excluded |
|---|---|---|
| the operator's `systemctl start` of the capture unit | D §4.2.5-R4, R6 | unprivileged; authorized by the one-shot Polkit grant; it *starts* CP, which is RT-1 |
| Option C, `sudo -n /usr/bin/systemctl start --wait …` | D §4.2.5-R3 (c) | **not adopted**: Peter decided OH-D-10 Option A, route (iii-a) |
| the historical D3 `ACT`/`DEACT` through the stub | D §4.2.5 (original), §4.2.5-R1 | superseded by D3-R2: the holder (RT-2) and `ExecStopPost=` (RT-3) replace them. Only `attest` keeps `sudo` |
| the PK subject and `pkcheck` | R8 §7.5, DI-5, DI-6 | children of RT-1 … RT-5, not `sudo`-started |
| **H-0M2**, the proposed privileged read-only observing slice (DEC-4) | R8 §10, §11 | a future observation slice with no designed literal; it does not touch the grant or the activation mechanism; no accepted record says it uses `sudo` |
| the OH-S8b activation fault drill, PO-16, D9-5 | D §4.7.4, §4.6.4 | future slices under their own authority; no literal designed |
| Pass A acts A1-14, A1-15, A1-31 … A1-33 | D §3.5 (OH-D-5) | decided `not_run (one-host: no privilege in RP-11)`; no `sudo` runs in the pass |
| AP-0, H-2, H-2b | R8 §7.3 row 21 | unprivileged executor reads |

---

## 6. The complete-record audit (WP1-R2)

### 6.1 Caller, first image, controlled-image status and DI map: verification

Every attribute below was checked against the accepted text, not against the
original return.

| Row | Caller | First root image today | Controlled image today / LIT-FULL | DI map | Verdict |
|---|---|---|---|---|---|
| RT-1 | R8 §9.6.1; R2 §8 (n) | R8 §9.6.1 | no / R8 §9.6.1 | R8 §9.3 (CQ-4, CQ-5, PK/2) | verified |
| RT-2 | R8 §9.6.1; D (e) | R8 §9.6.1 | no / R8 §9.6.1 | R8 §9.3 (BSP, HL, `hold-start`, AK-1, AV-1) | verified; **AV-1 belongs here** (COR-02) |
| RT-3 | R8 §9.6.1; R2 §8 (e) | R8 §9.6.1 | no / R8 §9.6.1 | R8 §9.3 (CL-2, CL-4, CL-6, GP-R3) | verified |
| RT-4 | R8 §9.6.1; D (f) | R8 §9.6.1 | no / R8 §9.6.1 | R8 §9.3 (BS-1 … BS-3, CL) | verified |
| RT-5 | R8 §9.6.1; D (i) | R8 §9.6.1; D (i) literal | no / **BQ-2** | R8 §9.3 "Used by" cells: DI-1 (CL), DI-5 (attestation), DI-6 (PK/2) | verified; the literal is **not** the stub (COR-03) |
| SA-1 | R8 §8.1 AP-2; E-4 | D (e) literal | no / none designed | R8 §9.3 DI-2 | verified; membership open (COR-09) |
| SA-2 | D R4 (e), R6 (b) | D literal | no / none designed | **none** in R8 §9.3 | verified; absent from E-4 (COR-04) |
| IC-1 … IC-3 | R8 §9.6.1; D §4.2.4, §4.6.2-R1 | the stub | no / BQ-3 | none (R8 §9.6.1) | verified |
| IC-4 | D §4.6.3 | not stated | no / BQ-3 | none | verified as **inferred** (COR-13) |

**DI-1 … DI-6 by procedure** (a letter marks use; "?" marks conditional on the
membership decision; blank is no use):

| | RT-1 | RT-2 | RT-3 | RT-4 | RT-5 | SA-1 | SA-2 | IC-1 … IC-4 |
|---|---|---|---|---|---|---|---|---|
| **DI-1** state reads | CQ-4 | BSP, HL, `hold-start`, AK-1 timer | CL-2, CL-6 | BS-1 | CL-2, CL-6 | | | |
| **DI-2** create holder unit | | | | | | AP-2 ? | | |
| **DI-3** create backstop units | | AK-1 | | | | | | |
| **DI-4** disarm the timer | | | | BS-2, BS-3 | | | | |
| **DI-5** Polkit decision | CQ-5 | AV-1 | CL-4, GP-R3 | CL-4 | CL-4, attestation | | | |
| **DI-6** authorization subject | PK/2 | PK/2 | PK/2 | PK/2 | PK/2 | | | |
| *stop-unit call* (no DI row) | | | | | | | `stop` ? | |

[O] The OS-6 stop uses a function that R8's closed DI table (DI-1 … DI-6) does not
list. If SA-2 is in the set, that function is a **design addition**, not an
existing delegation (Q-5, §13).

### 6.2 What the complete reading adds, removes or changes

* **Adds** (§6.4): the AV-1 attribution (COR-02), the three distinct `sudo` shapes
  (COR-03), the R8 appearances of the OS-6 act (COR-04), the exact BC-4 wording
  and its LR-2 scope (COR-05, COR-06), the conditional reach of LR-4 over DI-2
  (COR-09), R8's internal tension on dynamic linkage (COR-12), and the confirmed
  absence of `H-1R` from R8 (COR-13).
* **Removes:** no original boundary member and no original recommendation.
* **Changes:** one premise (COR-09), two sentences (COR-06 and the BQ-3 sentence,
  §9), the pointer wording (COR-07) and three citations (COR-08, COR-10, COR-11).
* **Count.** The corrections are **sixteen** in all, COR-01 … COR-16 (§6.4). The
  twelve required reads of §1.1 are a different number.

### 6.3 Ledger of the original return's substantive claims

V = verified unchanged. V\* = verified, citation tightened. C = corrected (§6.4).
R = restated or reclassified. D = now a Peter decision.

| # | Original claim (proposal section) | Verdict |
|---|---|---|
| OL-01 | §0.1: what was asked; WP-1 scope | V |
| OL-02 | §0.1, §2: BQ-1 = R3-ROOT, BQ-4 = no dynamic child, both from the commissioned direction | V |
| OL-03 | §0.1: RT-1 … RT-4 need no exception because PID 1 starts a design image first | V |
| OL-04 | §0.1: the `sudo`-started set is `attest`, the installer class, `AP-2`, the OS-6 stop | R (`H-1R` added; see §5.3) |
| OL-05 | §0.1, §5.3: beginning at `sudo` makes LR-2 unsatisfiable | V |
| OL-06 | §0.1, §8: B2-F "requires the single `sudo` exception R8 §9.3 and §12.2 BC-4 already say" | C (COR-05) |
| OL-07 | §0.1, §5.2: `AP-2` and the OS-6 stop have no controlled image | V |
| OL-08 | §0.1, §7.1: BQ-2 recommendation B2-F-A | R, D (PD-2a, PD-2b) |
| OL-09 | §0.1, §7.2: BQ-3 recommendation B3-OUT | R, D (PD-3; `H-1R` named; COR-10) |
| OL-10 | §0.1: the "stop and report" reading | V (Q-7 resolved) |
| OL-11 | §0.1: no exception-free answer is available from the repository | V |
| OL-12 | §0.2: decision summary | R (§0.3) |
| OL-13 | §1.1: documents read | C (COR-01) |
| OL-14 | §1.2: fact tags | V (extended) |
| OL-15 | §2: BQ-1, BQ-4, SSW, SCDC, ACCEPT-X1, WITHDRAW | V |
| OL-16 | §2: LR-1 … LR-6 restated | V |
| OL-17 | §2: "where *p* begins decides what is in its tree" | V |
| OL-18 | §3: entry boundary rows | V\* (COR-08) |
| OL-19 | §3: AV-1 among the executor's verification reads | C (COR-02) |
| OL-20 | §4.2: RT-1 … RT-4 caller, image, DI | V |
| OL-21 | §4.2: RT-5 row and its DI reading | V |
| OL-22 | §4.2: no BQ-2 exception arises for RT-1 … RT-4 | V |
| OL-23 | §4.3: sub-roles are not rows | V |
| OL-24 | §4.4: SA-1 row | V\* (COR-12) |
| OL-25 | §4.4: SA-2 row and "R8 never names the stop as a `sudo` act" | R (COR-04) |
| OL-26 | §4.4: IC row | V\* (COR-03, COR-13) |
| OL-27 | §4.4: SA-2 "an omission in R8's enumeration" | V\* (R8 knows the act; E-4 does not list it) |
| OL-28 | §4.4 and handback §4: completeness search and "the stub is used for installer and for `attest`" | C (COR-03); searches repeated (§1.2) |
| OL-29 | §4.4: what is in neither table | R (`H-1R` now a member; §5.5) |
| OL-30 | §5.1: the order of events for RT-5 | V |
| OL-31 | §5.2: BQ-2a and BQ-2b | V; D (PD-2a, PD-2b) |
| OL-32 | §5.3: B2-S | V |
| OL-33 | §5.4.1: RT-5 under B2-F; the ambient-input reasoning | V; Q-4 resolved (§13) |
| OL-34 | §5.4.2: B2-F-A and B2-F-B; "DI-2 left un-replaced though LR-4 requires" | C (COR-09) |
| OL-35 | §5.4.3, §5.6: summary tables | V |
| OL-36 | §5.5: B2-N | V |
| OL-37 | §6.1: the installer class facts | V\* (COR-03, COR-13) |
| OL-38 | §6.2: B3-IN | V |
| OL-39 | §6.3: B3-OUT and its detection controls | R (COR-10) |
| OL-40 | §6.4: neither R8 list names the installer | V |
| OL-41 | §7.1: the four reasons for B2-F-A | V, except reason 3 (COR-09) |
| OL-42 | §7.1: the recommended BQ-2 sentence | C (COR-06) |
| OL-43 | §7.2: the recommended BQ-3 sentence | R (names `H-1R`; COR-10) |
| OL-44 | §7.3: alternative sentences | V\* (re-worded in §9.3) |
| OL-45 | §8: EX-1, EX-2, EX-3; BC-2; BC-3; BC-1, BC-5 | C (COR-05, COR-16) |
| OL-46 | §8: FR-1 … FR-5 | V (FR-3 now names the stop; §10.2) |
| OL-47 | §9: BQ-4 and its constraints on WP-2 … WP-7 | V (carried, §11) |
| OL-48 | §10: inputs WP-2 may rely on, and may not | R (gate restated; §12) |
| OL-49 | §11: acceptance checklist, C-14 "three" questions | C (COR-11) |
| OL-50 | §12: Q-1 … Q-6 | resolved or converted (§13) |
| OL-51 | §13: what is not established | V |
| OL-52 | the four pointers: "WP-2 may be prompted after review and Peter's decisions" | C (COR-07) |

### 6.4 Correction table, old to new

| ID | Old (original WP-1 return) | New |
|---|---|---|
| **COR-01** | R8 and R2 read "in the sections named … and not in full" (proposal §1.1; handback §4) | the R1 remediation read all 14 records of its own prompt's list to EOF (R1 proposal §1.1). WP-1 R2 repeated a complete read of the twelve records of its own prompt (R2 proposal §1.1), WP-1 R3 repeated it for the thirteen records of its own prompt (R3 proposal §1.1), WP-1 R4 repeated it for the thirteen records of its own prompt (R4 proposal §1.1), and WP-1 R6 repeated it for the twelve records of its own prompt (§1.1 here), with the searches of §1.2 run over the whole files |
| **COR-02** | proposal §3: the executor's unprivileged verification reads include "AV-1's re-verification" | R8 §7.3 row 21 lists **AP-0, H-2 and H-2b**. **AV-1 is a holder step** (R8 §8.1 Machine H; D §4.2.5-R2 (d)); it belongs to RT-2 and makes no `sudo` act |
| **COR-03** | handback §4 and proposal §4.4: the stub is "used for installer and for `attest`" | four different `sudo` shapes: the `-c` stub (installer class IC-1 … IC-4); the installed tool **by path** (`attest`, D §4.2.5-R2 (i); R8 §9.6.1); `systemd-run` (AP-2); `systemctl stop` (OS-6) |
| **COR-04** | handback §4: `systemctl stop` appears in R8 "only as DI-4 and as a mutating child, never as a `sudo` act" | R8 also names the executor's route (iii-a) `stop`: §8.2 AW-5, §8.8, §12.1 (OS-6 unchanged), Appendix B-02, B-03, B-05, B-09. It never lists it among the §9 `sudo`-started paths. The absence from E-4 stands; the act is not unknown to R8 |
| **COR-05** | proposal §8: BC-4 quoted as "except `sudo`-started procedures … from LR-1 … LR-2 (BQ-2)" | BC-4 reads "except `sudo`-started procedures **or the installer class** from LR-1 … LR-2 (BQ-2, BQ-3)". The BQ-2 exception is stated by R8 §9.3 as "an exception to **LR-2**" |
| **COR-06** | proposal §7.1: `sudo` is "outside the procedure and outside LR-1 through LR-6" | `sudo` is excepted from **LR-2 only**. LR-1 and LR-3 … LR-6 apply in full to the image `sudo` executes and everything beneath it (§9.1) |
| **COR-07** | the four pointers said WP-2 may be prompted after independent review and Peter's BQ-2/BQ-3 decisions | the gate of §2.4, in all four pointers |
| **COR-08** | proposal §3: "runs as `ubuntu`, under `NoNewPrivileges`" and "what binds it" cited to R8 §9.1 table and §13.2 | `ubuntu` is in the §9.1 table; `NoNewPrivileges` is in the §9.6.1 entry row and D TR-8; the narrowing of PO-12′ and PO-19 to the entry is R8 §9.8 and §10 |
| **COR-09** | proposal §5.4.2, §7.1 reason 3: B2-F-B "would leave DI-2 un-replaced though LR-4 requires" | LR-4 binds the root procedures of R8 §9.1, a list that omits `AP-2`. R8 §9.3 gives DI-2 to `AP-2`. LR-4 therefore reaches DI-2 **only if `AP-2` is in the set (PD-2b)**. B2-F-B is a wider exception, not a free-standing LR-4 violation |
| **COR-10** | proposal §6.3, §7.2: "AP-0, AM-0 and H-2 verify the installed bytes before they are used" | the verification is against the H-1 record **and the maintainer-supplied A-2 pins** (R8 Appendix B-01, `MI.image_sha256[]`, `tool_sha256`), not against the installer's own report alone. The installer's source bytes are checked against digests pinned in the H-1 assignment (D §4.2.4-R1, PF). Stated as an observation for Codex |
| **COR-11** | proposal §11, C-14: "the three open classification questions of §12" | §12 listed six; the handback adds a seventh. All seven are resolved or converted in §13 |
| **COR-12** | proposal §4.4: `systemd-run` and `systemctl` "dynamic distribution client", unqualified | R8 §9.3 E-4 states that `sudo` and `systemd-run` are dynamic root processes; D §4.1.3 TR-4 records `systemctl` as dynamic; **but R8 §9.3's body records the linkage of `systemd-run`, `pkcheck` and `sleep` in no accepted record (MF-9) and calls the expectation "not a fact"**. Both statements are R8's. BQ-2 does not depend on the difference, because `sudo` is in every path |
| **COR-13** | proposal §6.1: `H-1R` "runs by the same stub" | no accepted record states its invocation. It is inferred from "one tool" (D §4.2.4; OH-S4 row) and from its root-owned record write (D §4.6.3, PF into `h1/`) **[O]**. R8 does not name it (0 of 4,816 lines) |
| **COR-14** | handback §6: Q-7 (the "stop and report" reading) left open | resolved (§13): neither the independent review nor the R1 authority treats the original return as a `HARD STOP`, and both proceed to remediation |
| **COR-15** | proposal §0.1: "Following the prompt, this record stops at reporting that fact" | unchanged in effect; restated in §2.1 as the explicit chain G-1 → review → R1 Auth |
| **COR-16** | proposal §8: EX-3 "BC-4 widened; also reopens LR-4 for DI-2" | EX-3 is **BC-4 applied to whole procedures** (`AP-2`, the OS-6 stop) instead of only to `sudo`. It is **not** BC-3 (dynamic children of a static root image), which BQ-4 forbids: under B2-F-B there is no static root image in those two paths. Whether LR-4 reaches DI-2 follows COR-09 |

---

## 7. BQ-2 in plain language: where does a `sudo`-started procedure begin?

### 7.1 The question

R8 §9.3 asks: "For a procedure that `sudo` starts, where does 'the root procedure'
begin: at the first image the procedure controls, or at `sudo`? Treating `sudo`'s
own loader as outside the procedure is an exception to LR-2 and needs to be stated
as one."

In plain words. The rule says a root procedure must not run through CPython or a
dynamic loader. `sudo` is a distribution program that is itself dynamically
linked, and this project cannot rebuild or replace it. If the clock starts when
`sudo` starts, `sudo` is *inside* the procedure and the rule cannot be met. If the
clock starts at the first program the project controls, `sudo` is a launcher that
sits outside, and leaving it outside must be written down as an exception.

### 7.2 What actually runs [A+O]

For `attest` today: the executor (unprivileged, Python, `ubuntu`) calls `sudo -n`;
**`sudo`** runs as root in its own environment handling (D §3.5 notes that `sudo`
merges its PAM environment; D §4.2.4 says the tool "runs under `sudo`'s
environment, which is not closed (AS-12)"); then `sudo` executes the first program
the procedure names (today CPython running `rp11_h1.py`; under LIT-FULL, a static
image). R8 records **no accepted fact** about `sudo`'s linkage or about what its
pre-`exec` phase reads, and this record adds none.

### 7.3 Two separable questions [N]

* **PD-2a (BQ-2a): where does a `sudo`-started procedure begin?** At `sudo`, or at
  the image `sudo` executes.
* **PD-2b (BQ-2b): which `sudo`-started acts are root procedures that need a
  controlled image?** `attest` certainly (R8 §9.1). `AP-2` and the OS-6 `stop` are
  the open cases. The installer class is BQ-3. **PD-2b is required under both PD-2a
  answers:** B2-S decides where a procedure begins and no membership question.

BQ-2 "as R8 worded it" assumes each `sudo`-started path has a first image the
procedure controls. That is true only for `attest`, and only after WP-4 designs
one. For `AP-2` and the OS-6 `stop`, `sudo` executes a distribution program
directly.

### 7.4 The alternatives

**B2-S: the procedure begins at `sudo`.** *Plain:* the **current** `sudo`-started form of an
act begins at `sudo`, so `sudo` is inside that form's procedure. LR-2 **cannot be met** by
that current form, because `sudo` is a dynamic root program in the tree and no accepted
record makes it, or a replacement for it, loader-free. B2-S is the strictest reading; it is
not an exception. It is a boundary under which LIT-FULL is attainable for an act only if the
current `sudo` start is **replaced** by a start path that is not `sudo` (**B2-N**, below, a
separate design of category D).

**The process-tree result under B2-S, stated once.** B2-S decides where a `sudo`-started
procedure begins. B2-N is the separate, loader-free privileged-start design required to
replace that current start for every in-set act before WP-2 can rely on B2-S. PD-2b decides
which acts are in the set. The three together give this result for each act:

| Act, by PD-2b (under B2-S) | Who starts it | The resulting inventoried tree begins at | Does the tree contain `sudo`? | Exception | Later work |
|---|---|---|---|---|---|
| **in** the set (`attest` always; `AP-2` and the OS-6 `stop` if PD-2b puts them in) | **B2-N**, the separate loader-free privileged-start design that replaces the current `sudo` start | **B2-N's loader-free start path** | **No.** Once B2-N has replaced the current start, no `sudo` is in the tree | none for the act itself (B2-N is a category D item) | the act's role (`start`, `stop`; `attest` is RT-5) stays work for WP-2 … WP-7 |
| **out** of the set (`AP-2` and/or the OS-6 `stop`, if PD-2b leaves it out) | **not B2-N.** B2-N changes how an in-set act starts. The act keeps its current `sudo` plus distribution-client path | **not inventoried.** The whole current path is outside the boundary | not applicable: the entire path, `sudo` and the distribution client alike, is outside the boundary and is not inventoried as a root procedure | **EX-3** for the whole act, with a complete §0.2 item | no role |

B2-N changes **how** an in-set act starts, not **whether** it is in the set. It does not erase
EX-2 or EX-3 and does not substitute for their §0.2 closure. **B2-S by itself decides no
membership question.** It does not put `AP-2` or the OS-6 `stop` in the set or out of it, and it
does not make the `start` or `stop` role absent. **PD-2b is still required** (§2.2) under both
PD-2a answers. For every act PD-2b puts **in**, B2-N must provide the loader-free privileged
start and the act's role stays work for WP-2 … WP-7. For every act PD-2b leaves **out**, EX-3
remains a proposed wider BC-4 boundary exception for that whole act, and complete §0.2 closure
must close before WP-2 may be prompted, authorized or rely on the boundary. The four
combinations under B2-S (`attest` is in the set in every one, so B2-N is always needed):

| `AP-2` | OS-6 stop | Exceptions present under B2-S | B2-N must start | New roles | After B2-N, is `sudo` in an inventoried tree? |
|---|---|---|---|---|---|
| in the set | in the set | none | `attest`, `AP-2`, the stop | `start`, `stop` | no, in none of the three |
| in the set | not in the set | EX-3 for the left-out `stop` act | `attest`, `AP-2` | `start` | no, in neither; the `stop` act's `sudo` and `systemctl` path is outside the boundary |
| not in the set | in the set | EX-3 for the left-out `start` act | `attest`, the stop | `stop` | no, in neither; the `start` act's `sudo` and `systemd-run` path is outside the boundary |
| not in the set | not in the set | EX-3 for both left-out acts | `attest` | none | no, in the `attest` tree; both left-out acts' paths are outside the boundary |

**B2-F: the procedure begins at the first image the design controls.** *Plain:*
`sudo` is a launcher outside the procedure; that exclusion is exception **EX-1**
(LR-2 only, §9.1). Everything the procedure itself does, every child it forks and
every descriptor it holds is loader-free and closed. Two ways to complete the
answer for `AP-2` and the OS-6 stop:

* **B2-F-A: bring them into the set with a static client image each** [N]. `AP-2`'s
  image performs DI-2 in-process (one `StartTransientUnit` call carrying the
  accepted AP-2 properties). The OS-6 image performs one `stop` of one named unit.
  The only dynamic root program left on any `sudo`-started path other than the
  installer is `sudo` itself. *Cost:* a new `start` role and a new `stop` role
  (FR-1); the stop function is not in R8's DI table (§6.1); the marshalling that
  WP-3 must specify for DI-3 also serves DI-2.
* **B2-F-B: leave them outside the set** [N]. `sudo` **and** the distribution's
  `systemd-run` and `systemctl` run as root before any controlled image, outside
  the boundary. This is **EX-3**, the proposed **wider BC-4 boundary exception** for
  whichever whole `sudo`-started acts Peter leaves outside the set (§10.0). It is
  wider than EX-1 because a dynamic program that does the act's real work is
  excepted, not only `sudo`'s loader. It is **not an LR-4 exception**: LR-4 binds a
  root procedure in the set, and an act outside the set is not one (COR-09,
  COR-16). It is not BC-3, and it does not expand BC-4. The 2×2 below shows that the
  two acts can be decided separately.

| `AP-2` | OS-6 stop | Exceptions present | New roles |
|---|---|---|---|
| in the set | in the set | EX-1 | `start`, `stop` |
| in the set | not in the set | EX-1, and EX-3 for the left-out `stop` act (`sudo` and `systemctl`) | `start` |
| not in the set | in the set | EX-1, and EX-3 for the left-out `start` act (`sudo` and `systemd-run`) | `stop` |
| not in the set | not in the set | EX-1, and EX-3 for both left-out acts | none |

**B2-N: another privileged start path that is not `sudo`.** *Plain:* a way for the
`ubuntu` executor to cause a root, static image to run without a dynamic launcher.
The accepted records contain **no design, citation or evaluation** of one. Every
candidate is a new trust mechanism with its own citations (privilege elevation,
environment and descriptor inheritance, authorization, auditability). Its benefit
under OH-D-6 would be purely LR-2 literalness, because `ubuntu` already has
unrestricted `sudo`. It is a design package outside R8's WP list and might itself be
a §0.2 matter. **B2-N is not recommended and is not decision-ready.** It is stated
so that "no exception" is shown to depend on it. It is the replacement for the current
`sudo` start that the process-tree table above refers to: it starts the acts PD-2b puts in,
it starts none that PD-2b leaves out, and this record designs it nowhere.

### 7.5 Recommendation (pending Peter's decision) [N]

**B2-F, with B2-F-A.** Reasons:

1. B2-S cannot be met by anything the repository contains, so it is not a
   decision-ready answer for LIT-FULL; it is a different project (B2-N).
2. B2-F puts everything the design writes, every child it forks and every
   descriptor it holds inside loader-free, closed images, and confines the
   exception to one program (`sudo`) and one `execve`. It is the narrowest
   exception that exists.
3. B2-F-A removes the only dynamic root programs that do real work from any
   `sudo`-started path other than the installer, and uses interface work (DI-3's)
   that LIT-FULL already requires. **If `AP-2` is not a root procedure, LR-4 does
   not by itself require this (COR-09)**; the argument is then uniformity and
   narrowness, not an LR-4 breach.
4. It makes the answer uniform: every `sudo`-started root path begins at a design
   image, so Peter's exception has a single, small statement.

The honest counter-position, for Peter: the OS-6 stop touches neither the grant nor
the holder, so treating it as outside the boundary (B2-F-B for that act) is
coherent; it costs a wider exception and saves a new role.

---

## 8. BQ-3 in plain language: is the installer class a root procedure of the boundary?

### 8.1 The question

R8 §9.3 asks: "Is the installer class (H-1, RB-1, RS-1: the `sudo -n python3.14 -I
-S -c` verified-exec stub, HB-1) among the 'root procedures that touch the …
activation mechanism'? They install and remove the files the mechanism consists
of."

In plain words. The install, remove, scan and re-record tools run as root and place
the files that the activation mechanism consists of. If they count as root
procedures they must also be Python-free and loader-free. If they do not, they stay
Python, run through `sudo`, and that is a recorded exception.

### 8.2 What the class is and does [A]

* **Run:** `sudo -n /usr/bin/python3.12 -I -S -c '⟨verified-exec stub⟩' ⟨subcommand⟩ …`
  today, retargeted to `python3.14` under HB-1 (D §4.2.4; R8 §9.6.2 A7).
* **The stub** reads the tool file once, requires its SHA-256 to equal the value
  pinned in the H-1 assignment, and executes those bytes: there is no window between
  the check and the use (D §4.2.4).
* **The stated limit (HB-1).** The tool "runs under `sudo`'s environment, which is
  not closed (AS-12). That is acceptable only because H-1 is not the capture entry.
  Its results are re-read unprivileged by H-2, and diagnostically by the entry." (D
  §4.2.4; R8 §13.1.)
* **When:** ST-0 to ST-1 (H-1), the separately authorized RB-1, the read-only `scan`
  (RS-1), and `H-1R` under separate authority. None is part of the grant window, the
  pass or the consume step.
* **What they touch:** they publish and remove the launcher, the bootstrap, the
  unit, the staged rule, the H-1 record and the tool itself (tree **L** now includes
  `rp11_h1.py`, D §4.2.5-R2 (b)).
* **One tool.** D lists `rp11_h1.py` as one tool whose subcommands include
  *preflight, install, record, verify, rollback, `ACT`, `DEACT`, H-1R* (D, OH-S4
  row), with `scan`, `rb1`, `hold`, `backstop` and `consume` added by D3-R1 … R4.
  Under LIT-FULL the root roles leave that file for static images (R8 §9.6.2 D2). So
  **B3-OUT leaves a Python `rp11_h1.py` that carries the installer-class
  subcommands only** and is on no activation path. B3-IN would remove it.
* **Membership.** R8 names "H-1, RB-1, RS-1". It does not name `H-1R` (COR-13).

### 8.3 B3-IN: the installer class is in the set

*Plain:* each of H-1, RB-1, RS-1 (and `H-1R`) must satisfy LR-1 … LR-6.

* LR-1 and LR-3: the tool must not be CPython, so **a Python-free installer is a
  new work package** (R8 §9.6.1), not in R8 §9.5.
* LR-2: the installer is `sudo`-started, so **BQ-2 applies to it in full**.
  Inclusion does not remove the `sudo` exception under B2-F, and under B2-S it still
  fails LR-2.
* **Size** [N]: the installer carries the whole publication algorithm (PF, PT), the
  crash-consistent journal and its parser, recovery binding, `fsync` discipline,
  RB-1's removal and the SHA-256 and canonical-JSON handling (D §4.2.4-R1). It is a
  larger, differently shaped image than any activation procedure.
* **The verified-exec property** [N]: the stub's "no window between check and use"
  is achieved by a Python program that reads once and executes those bytes. A
  loader-free equivalent is designed nowhere in the accepted records. A static
  installer run by `sudo` by path invites a window between the executor's check and
  `sudo`'s `execve`.
* **HB-1** is closed for Python and the loader after the first image; the `sudo`
  preamble remains.

### 8.4 B3-OUT: the installer class is outside the set

*Plain:* the installer class stays Python behind `sudo`; this is exception **EX-2**
(LR-1 and LR-2), with HB-1 as the named residual.

* R8 already provides the wording: `/usr/bin/python3.14` with the HB-1 sentence (R8
  §9.6.2 A7; Appendix A-II-03).
* **Detection controls that already bound the damage a faulty install can do** [A]:
  the installed bytes are checked before use by AP-0, AM-0 and H-2 (R8 §13.1 RO-2:
  "AP-0, H-2, AM-0 detect a prior tamper"; §7.3 row 9 hashes helper images at AP-0,
  AM-0 and H-2); H-2 is unprivileged (§7.3 row 21); the stub's digest pin protects
  the installer's own bytes against accident (D §4.2.4); the grant is
  start-consumed, and only the holder that AP-2 creates links a rule (D §4.2.5-R2
  (n) 1). **[C] COR-10:** the comparison is against the H-1 record and the
  maintainer-supplied A-2 pins, not the installer's report alone.
* **What it does not claim:** that ST-1 is privilege-inert (OH-D-6 says it is not
  for `ubuntu`); that the installer cannot install wrong bytes (only that the
  activation refuses to use bytes that fail verification); that CPython's and the
  loader's file inputs are closed (MF-1, MF-2, MF-4 stay open for the entry; for the
  installer they are exactly HB-1).

### 8.5 B3-OUT is an exception, not only a scope note (Q-3)

Neither R8 §9.1 list names the installer: R3-ROOT's list is "CP, the holder (ACT,
HL, IGR), the stop-post, the backstop, `attest`", and DR1 §5.3's list does not name
one either. **R8 nevertheless words the exclusion as an exception**: §9.6.1 ("out of
scope, stated as an exception with the HB-1 residual"), §12.2 BC-4 ("or the
installer class"), §13.1 HB-1 ("a stated exception (a BC, §12.2)"), and §9.4 ("if
BQ-2, BQ-3 or BQ-4 are answered by an *exception*, that exception is a §0.2
change"). The independent review states the same: "B3-OUT is a BC-4 exception under
the accepted R8 wording, not merely a harmless membership classification." Q-3 is
therefore resolved by the accepted record (§13).

### 8.6 Recommendation (pending Peter's decision) [N]

**B3-OUT, with `H-1R` named in the sentence.** Reasons:

1. The installer runs outside the grant window, the pass and the consume step, and
   is not the capture entry, so no LR-3 closed-environment guarantee of the
   activation depends on it.
2. The activation does not use what the installer writes unless it verifies
   (§8.4, COR-10).
3. Inclusion does **not** remove the `sudo` exception (§8.3). It would remove only
   the installer's own CPython and loader, at the price of the largest single image
   and an unspecified loader-free equivalent of the verified-exec property.
4. Peter can revisit it: B3-IN remains available as a follow-on after WP-2 … WP-7,
   or if Codex finds that an installer fault can reach a grant. Nothing WP-2 builds
   is lost if it later moves into the set (§12).

---

## 9. The sentences Peter could approve (pending)

**All are recommendations of this record. None is decided. None may be cited as
decided until Peter records it, and any sentence containing an exception takes
effect only after §0.2 closes (§2).**

### 9.1 BQ-2, recommended (B2-F-A) [N]; corrected by COR-06

> *For a root procedure that `sudo` starts (`attest`, the holder-creation act of
> AP-2 and the OS-6 interruption), the procedure begins at the first image that the
> design controls and that `sudo` executes. Each such act has a design-controlled
> static first image that applies RH-1 through RH-3. `sudo`, and nothing else, is a
> launch preamble outside the procedure, and that exclusion is recorded as an
> exception to LR-2 only, under BC-4 of the accepted R8 proposal. LR-1 and LR-3
> through LR-6 apply in full to the image `sudo` executes and to everything beneath
> it. No other dynamic program is part of or beneath a `sudo`-started root
> procedure. This sentence takes effect only when Peter records it and the complete
> implementation-plan §0.2 change-control process has closed.*

### 9.2 BQ-3, recommended (B3-OUT) [N]; `H-1R` named

> *The installer class is not among the root procedures of the LIT-FULL boundary.
> It comprises H-1, RB-1, RS-1 and H-1R. H-1, RB-1 and RS-1 are run through the
> verified-exec stub as `sudo -n /usr/bin/python3.14 -I -S -c ⟨stub⟩`, the
> interpreter literal following R8 §9.6.2 A7. H-1R is named here so that it is
> classified expressly and not by silence: it is a separately authorized root
> re-record operation, read-only plus a record write, implemented as a subcommand of
> the one installer tool. This sentence asserts no invocation literal for H-1R,
> which a later, separately authorized record may state. The class is recorded as an
> exception to LR-1 and LR-2 under BC-4 of the accepted R8 proposal, with HB-1 as
> its stated residual for the members that run under `sudo`'s environment. The
> installer runs outside the grant window, the pass and the consume step, and the
> files it installs are re-verified before any use by AP-0, AM-0 and H-2 against the
> H-1 record and the maintainer-supplied A-2 pins. This sentence takes effect only
> when Peter records it and the complete implementation-plan §0.2 change-control
> process has closed.*

**Outside the sentence (WP1-R1R-3).** [O] No accepted record states an invocation
for H-1R (COR-13; §1.2: 0 lines in R8, no literal in D). The accepted design
describes it as a "re-record step (read-only plus record write, no file change)
under separate authority" whose record is published "by PF into `h1/`", and lists it
among the subcommands of the one tool (D §4.6.3; OH-S4 row). **It may run through
the same verified-exec stub, but that is an inference, not an accepted fact.** It is
recorded here only so that Peter can see what the sentence deliberately leaves
open. It is not part of the text he is asked to approve, and this record performs no
new invocation design. Whether `H-1R` belongs in the installer class remains PD-3.
Naming it in the sentence does not decide that, and removing it from the sentence
would not remove it from PD-3.

### 9.3 The alternatives, as sentences

| Choice | Sentence to approve instead |
|---|---|
| B2-F-B | *as §9.1, but `sudo` and the distribution's `systemd-run` and `systemctl` are launch preambles outside the procedure; AP-2 and the OS-6 interruption are not root procedures of the boundary, and their exclusion, with the programs that do their work, is recorded as a boundary exception under BC-4 (EX-3).* **EX-3 is a wider boundary exception, not an LR-4 exception: LR-4 binds only root procedures in the set. DI-2 remains the distribution `systemd-run`'s, outside the boundary.** |
| mixed | *as §9.1 for the acts named in the set, and the exception of B2-F-B for each act left outside* (the 2×2 of §7.4). The same four combinations apply under B2-S, with B2-N in place of the `sudo` preamble (§7.4, §10.1) |
| B2-S | *a root procedure that `sudo` starts begins at `sudo`.* **LR-2 cannot be met by the current `sudo` start; a start path that is not `sudo` must then be designed (B2-N) to replace it for every act in the set, or LIT-FULL is not attainable for these paths. After B2-N an in-set act's inventoried tree begins at B2-N's path and contains no `sudo`; an act left out is not started by B2-N and its whole current `sudo` path is outside the boundary (EX-3).** **B2-S decides no membership question: PD-2b is still required. Each act it leaves out carries EX-3 (§10.0) and a complete §0.2 item; each act it puts in keeps its role in WP-2 … WP-7 and needs B2-N's start path; B2-N erases neither EX-2 nor EX-3.** |
| B3-IN | *the installer class (H-1, RB-1, RS-1 and H-1R) is among the root procedures of the LIT-FULL boundary; each begins at its first design-controlled image and meets LR-1 through LR-6, with `sudo` excepted as in the BQ-2 sentence.* **Adds a Python-free installer package; the verified-exec property needs a loader-free design.** |

---

## 10. Exceptions, §0.2 items, design prerequisites and downstream dependencies

### 10.0 The exceptions defined, and the reach of LR-4

This subsection exists so that §10.1 can be one canonical table. **WP1-R1R-1** found
that R1 described EX-3 as an LR-4 exception. It is not one.

| ID | What is excepted | Source and status | What it is not |
|---|---|---|---|
| **EX-1** | `sudo`'s own dynamic loader, as a launch preamble before the first design-controlled image of a `sudo`-started root procedure **in the set**: an exception to **LR-2 only**. LR-1 and LR-3 … LR-6 apply in full to the image `sudo` executes and to everything beneath it (COR-05, COR-06) | R8 §9.3 ("an exception to LR-2"), §12.2 BC-4. Proposed with B2-F. **Not approved** | not an exception to LR-1 or to LR-3 … LR-6; no licence for any other dynamic program |
| **EX-2** | the installer class (H-1, RB-1, RS-1 and `H-1R`, if PD-3 classes it with them) left outside the set: an exception to **LR-1 and LR-2**, with HB-1 as the stated residual | R8 §9.6.1, §12.2 BC-4, §13.1 HB-1. Proposed with B3-OUT. **Not approved** | not a mere membership note (Q-3) |
| **EX-3** | the **whole `sudo`-started act** that Peter leaves outside the set (`AP-2`, the OS-6 `stop`, or both), so that the distribution `systemd-run` and/or `systemctl` that does the act's real work runs as a dynamic root program outside the boundary. It is a proposed boundary exception **wider than EX-1**, in the family of BC-4 | this record. Proposed with B2-F-B, with the mixed answers of §7.4 and with every B2-S combination in which PD-2b leaves an act out (§10.1). It is independent of PD-2a. **Not approved** | **not an LR-4 exception** (below). **Not BC-3**: under B2-F-B there is no static root image in those paths for a dynamic child to hang from (COR-16). It does not decide whether either act belongs in the set (PD-2b) |

**The reach of LR-4.** LR-4 (R8 §9.2) binds each root procedure *in the final set*:
every function it delegates to a child today (DI-1 … DI-6) is performed in-process
or by a cited loader-free interface. R8 §9.3 gives DI-2 (creating the holder unit)
to `AP-2`. Therefore:

* if `AP-2` is **in** the set, LR-4 reaches DI-2, and DI-2 is **not** excepted: the
  static `start` image performs it. The `systemd-run` part of EX-3 is then absent;
* if `AP-2` is **outside** the set, it is not a root procedure of the boundary, LR-4
  does not bind it, and its exclusion is **not a free-standing LR-4 exception**.
  What is excepted is the act, under EX-3 (COR-09, COR-16); and
* the OS-6 `stop` has no row in R8's closed DI table (§6.1). If it is in the set, the
  function it delegates to `systemctl` must be performed loader-free like any other,
  which is a design addition (Q-5). If it is outside, EX-3 covers it.

**BC-4 is not expanded here.** R8 §12.2 words BC-4 as "except `sudo`-started
procedures or the installer class from LR-1 … LR-2 (BQ-2, BQ-3)". Whether that wording
already covers the exclusion of a whole `sudo`-started act, or must be widened, is a
question for the §0.2 impact assessment. This record neither answers it nor widens
BC-4, and it approves nothing. The gate is unchanged: every exception-bearing choice
(EX-1, EX-2 or EX-3) requires complete §0.2 closure before WP-2 may be prompted,
authorized or rely on the boundary.

### 10.1 The canonical matrix: every exception, §0.2 item, prerequisite, role and WP-2 status

This is the **one** canonical matrix. §2.2 defines the categories and §12.2 lists the
WP-2 inputs; neither restates a row. Categories **G**, **D** and **W** are those of §2.2.
"Exception" names an exception to an LR criterion (EX-1, EX-2) or a **boundary**
exception (EX-3, which is **not** an LR-4 exception, §10.0).

**Form.** Three orthogonal tables, one for each decision dimension (A: PD-2a, B: PD-2b, C:
PD-3), then one mechanical union rule (U1 … U7), then worked rows for every combination:
2 PD-2a answers × 4 PD-2b membership combinations × 2 PD-3 answers = 16 rows, eight of them
B2-S. If a worked row and the rule disagree, the rule governs and the row is a defect.

**Table A: PD-2a, where a `sudo`-started root procedure begins**

| PD-2a | Exceptions it adds | §0.2 items | D: design prerequisite | W: effect on the work | Note |
|---|---|---|---|---|---|
| **B2-F** | **EX-1** (`sudo`'s loader, **LR-2 only**). Always present under B2-F, because `attest` is a `sudo`-started root procedure in the set (R8 §9.1) | one complete item for EX-1 | none | each in-set `sudo`-started act begins at its first design-controlled image; `sudo` is a launch preamble outside the inventoried tree. For an act PD-2b leaves out, the whole existing `sudo` plus distribution-client path is outside the boundary under EX-3 and is not inventoried | |
| **B2-S** | **none claimable.** A procedure that begins at `sudo` fails LR-2, and no exception is proposed to cover a start at `sudo` | no exception to close from this table. **B2-N may itself be a §0.2 matter** | **B2-N**, a loader-free privileged-start design that is not `sudo` (outside R8's WP list). **Always required under B2-S, because `attest` is in the set**; it must also start every other in-set `sudo`-started act | after B2-N, an in-set act's resulting inventoried tree begins at B2-N's loader-free start path and contains **no `sudo`**, because B2-N replaces the current `sudo` start. An act PD-2b leaves out is **not started by B2-N**: its current `sudo` plus distribution-client path stays outside the boundary under EX-3 and is not inventoried | **B2-S decides no membership question.** It adds nothing to the exceptions of Table B and removes nothing from them. B2-N changes how an in-set act starts, not whether it is in the set |

**Table B: PD-2b, for each of `AP-2` and the OS-6 `stop`, separately. Identical under B2-F and B2-S**

| PD-2b answer for an act | Exceptions it adds | §0.2 items | D | W: role and activities | Note |
|---|---|---|---|---|---|
| **in** | none for the act itself | none | none of its own (B2-N under B2-S, Table A) | the act's role: **`start`** for `AP-2`, **`stop`** for the OS-6 stop. FR-1 records it (a documentation amendment); the activities are WP-2 inventory, WP-3 interface (DI-2 for `start`, a stop call for `stop`), WP-4 image, WP-5 D9 / PO-17, WP-6 mapping, WP-7 estimate (§10.2) | `AP-2` in: LR-4 reaches DI-2 and it is performed in-process. Stop in: the stop function is a design addition, not an existing delegation (Q-5) |
| **out** | **EX-3** for that whole act (a boundary exception wider than EX-1, in the BC-4 family): `sudo` and the distribution `systemd-run` (for `AP-2`) or `systemctl` (for the stop) run as dynamic root programs outside the boundary | **one complete §0.2 item for EX-3 for that act.** The impact assessment states EX-3 exactly and asks whether BC-4 as worded covers it | none. **B2-N does not erase EX-3 and does not substitute for its §0.2 closure** | no role for that act | not an LR-4 exception: LR-4 binds only acts in the set, so `AP-2` out leaves DI-2 the distribution `systemd-run`'s. Not BC-3 (§10.0, COR-16) |

**Table C: PD-3, the installer class (H-1, RB-1, RS-1 and `H-1R`)**

| PD-3 | Exceptions it adds | §0.2 items | D | W | Note |
|---|---|---|---|---|---|
| **B3-OUT** | **EX-2** (LR-1 and LR-2), with HB-1 as the stated residual. Independent of PD-2a and PD-2b | one complete item for EX-2; FR-5 text change (A7 / A-II-03) | none | the installer is omitted from WP-2 … WP-7; the estimate excludes the largest single item | |
| **B3-IN** | none for the installer itself | none for the installer | the **Python-free installer with a loader-free verified-exec equivalent**, separately authorized and reviewed (R8 §9.6.1 "a new WP"; not in R8 §9.5) | the installer's operations (PF, PT, journals, RB-1, RS-1 and `H-1R`, as PD-3 sets) enter WP-2; one more large image in WP-4; WP-5 … WP-7 scale; WP-7 states the delta as a separate line | the installer is `sudo`-started, so PD-2a applies to it in full (§8.3): under B2-F its `sudo` is within EX-1, already present; under B2-S its loader-free start is also B2-N's |

**The union rule.** For any combination of the three answers:

* **U1, exceptions.** E = {EX-1 if PD-2a is B2-F} ∪ {EX-3 for `AP-2` if `AP-2` is out} ∪ {EX-3
  for the stop if the stop is out} ∪ {EX-2 if PD-3 is B3-OUT}.
* **U2, §0.2 items.** One complete implementation-plan §0.2 item for each member of E, each
  closed before WP-2.
* **U3, design prerequisites.** D = {B2-N if PD-2a is B2-S, starting `attest` and every other
  in-set `sudo`-started act, the installer included if PD-3 is B3-IN} ∪ {the Python-free
  installer design if PD-3 is B3-IN}.
* **U4, later work.** W = RT-1 … RT-5 ∪ {the `start` role if `AP-2` is in} ∪ {the `stop` role if
  the stop is in} ∪ {the installer's operations if PD-3 is B3-IN}. W has the same members
  under B2-F and B2-S: B2-S changes where each begins (at B2-N's start path), not whether it
  is in W.
* **U5, governance.** G = {WP-1 accepted} ∪ {PD-2a, PD-2b (both acts) and PD-3 recorded} ∪
  {complete §0.2 closure for every member of E}. **All three decisions are in G for every
  combination.** A Peter decision is not by itself §0.2 approval.
* **U6, WP-2 status.** WP-2 is blocked until G is complete **and** every member of D exists,
  separately authorized and reviewed, or Peter withdraws the affected design. G alone does
  not release WP-2 when D is not empty, and D alone does not release it when E is not empty.
* **U7, independence.** (a) B2-S adds nothing to E and nothing to W by itself. (b) B2-N, once it
  exists, discharges only its D item: it does not remove EX-2 or EX-3 from E and does not
  stand in for their §0.2 closure. (c) EX-3 does not depend on PD-2a. (d) EX-3 is a boundary
  exception: it is never an LR-4 exception and never BC-3.

**Process-tree rule PT** (a reading of U3, U4 and U7 that adds no member to E, D or W). It
states, for each act and each combination, where the inventoried process tree begins and
whether `sudo` is in it:

* **PT-1, in the set, PD-2a = B2-F.** The act begins at its first design-controlled image.
  `sudo` is a launch preamble outside the inventoried tree (EX-1, LR-2 only).
* **PT-2, in the set, PD-2a = B2-S, after B2-N exists.** B2-N has replaced the current `sudo`
  start. The act's inventoried tree begins at B2-N's loader-free start path and contains
  **no `sudo`**. EX-1 is absent for it (B2-S proposes no exception, Table A).
* **PT-3, out of the set, either PD-2a answer.** The act is not inventoried and is **not started
  by B2-N**. Its entire current `sudo` plus distribution-client path (`systemd-run` for `AP-2`,
  `systemctl` for the stop) is outside the boundary under EX-3, and is not inventoried as a root
  procedure.
* **PT-4.** B2-N changes how an in-set act starts, not whether it is in the set (PD-2b), and does
  not erase EX-2 or EX-3 (U7 (b)). B2-S still decides no membership question.
* **PT-5, consequence.** No statement of this record says or implies that `sudo` is inside an
  inventoried tree after B2-N exists. Before B2-N exists nothing is relied on: the current form
  fails LR-2 and WP-2 is blocked on D (U6).

**Worked rows.** Legend: **RT** = RT-1 … RT-5, allocated to WP-2 … WP-7. **start** and
**stop** are the roles of Table B. **I** = the installer's operations (Table C).
"EX-3 (start)" is EX-3 for the `AP-2` / `start` act and "EX-3 (stop)" is EX-3 for the OS-6
stop act. Every row's G cell states the three recorded decisions and the §0.2 closure it
needs. Rows F-1 … F-8 are B2-F; rows S-1 … S-8 are B2-S.

| Row | PD-2a | `AP-2` | stop | PD-3 | G: recorded decisions and §0.2 closure before WP-2 | D: separate design prerequisites | W: later work | WP-2 status |
|---|---|---|---|---|---|---|---|---|
| **F-1** | B2-F | in | in | B3-OUT | WP-1 accepted; PD-2a, PD-2b, PD-3 recorded; **§0.2 closed for EX-1 and EX-2** | none | RT, start, stop | blocked until G is complete |
| **F-2** | B2-F | in | in | B3-IN | WP-1 accepted; PD-2a, PD-2b, PD-3 recorded; **§0.2 closed for EX-1** | the installer design | RT, start, stop, I | blocked until G is complete **and** D exists |
| **F-3** | B2-F | in | out | B3-OUT | WP-1 accepted; PD-2a, PD-2b, PD-3 recorded; **§0.2 closed for EX-1, EX-3 (stop) and EX-2** | none | RT, start | blocked until G is complete |
| **F-4** | B2-F | in | out | B3-IN | WP-1 accepted; PD-2a, PD-2b, PD-3 recorded; **§0.2 closed for EX-1 and EX-3 (stop)** | the installer design | RT, start, I | blocked until G is complete **and** D exists |
| **F-5** | B2-F | out | in | B3-OUT | WP-1 accepted; PD-2a, PD-2b, PD-3 recorded; **§0.2 closed for EX-1, EX-3 (start) and EX-2** | none | RT, stop | blocked until G is complete |
| **F-6** | B2-F | out | in | B3-IN | WP-1 accepted; PD-2a, PD-2b, PD-3 recorded; **§0.2 closed for EX-1 and EX-3 (start)** | the installer design | RT, stop, I | blocked until G is complete **and** D exists |
| **F-7** | B2-F | out | out | B3-OUT | WP-1 accepted; PD-2a, PD-2b, PD-3 recorded; **§0.2 closed for EX-1, EX-3 (start), EX-3 (stop) and EX-2** | none | RT | blocked until G is complete |
| **F-8** | B2-F | out | out | B3-IN | WP-1 accepted; PD-2a, PD-2b, PD-3 recorded; **§0.2 closed for EX-1, EX-3 (start) and EX-3 (stop)** | the installer design | RT, I | blocked until G is complete **and** D exists |
| **S-1** | B2-S | in | in | B3-OUT | WP-1 accepted; PD-2a, PD-2b, PD-3 recorded; **§0.2 closed for EX-2** (no EX-1, no EX-3) | **B2-N**, starting `attest`, `AP-2` and the stop | RT, start, stop, each beginning at B2-N's start path | blocked until G is complete **and** B2-N makes the boundary attainable, or Peter withdraws the affected design |
| **S-2** | B2-S | in | in | B3-IN | WP-1 accepted; PD-2a, PD-2b, PD-3 recorded; **no exception, so no exception to close** (B2-N or the installer design may themselves be §0.2 matters) | **B2-N**, starting `attest`, `AP-2`, the stop and the installer; and the installer design | RT, start, stop, I | blocked until both D items exist, or Peter withdraws the affected design. **This is the literal no-exception LIT-FULL** |
| **S-3** | B2-S | in | out | B3-OUT | WP-1 accepted; PD-2a, PD-2b, PD-3 recorded; **§0.2 closed for EX-3 (stop) and EX-2** | **B2-N**, starting `attest` and `AP-2` | RT, start | blocked until G is complete **and** B2-N exists, or withdrawal |
| **S-4** | B2-S | in | out | B3-IN | WP-1 accepted; PD-2a, PD-2b, PD-3 recorded; **§0.2 closed for EX-3 (stop)** | **B2-N**, starting `attest`, `AP-2` and the installer; and the installer design | RT, start, I | blocked until G is complete **and** both D items exist, or withdrawal |
| **S-5** | B2-S | out | in | B3-OUT | WP-1 accepted; PD-2a, PD-2b, PD-3 recorded; **§0.2 closed for EX-3 (start) and EX-2** | **B2-N**, starting `attest` and the stop | RT, stop | blocked until G is complete **and** B2-N exists, or withdrawal |
| **S-6** | B2-S | out | in | B3-IN | WP-1 accepted; PD-2a, PD-2b, PD-3 recorded; **§0.2 closed for EX-3 (start)** | **B2-N**, starting `attest`, the stop and the installer; and the installer design | RT, stop, I | blocked until G is complete **and** both D items exist, or withdrawal |
| **S-7** | B2-S | out | out | B3-OUT | WP-1 accepted; PD-2a, PD-2b, PD-3 recorded; **§0.2 closed for EX-3 (start), EX-3 (stop) and EX-2** | **B2-N**, starting `attest` | RT | blocked until G is complete **and** B2-N exists, or withdrawal |
| **S-8** | B2-S | out | out | B3-IN | WP-1 accepted; PD-2a, PD-2b, PD-3 recorded; **§0.2 closed for EX-3 (start) and EX-3 (stop)** | **B2-N**, starting `attest` and the installer; and the installer design | RT, I | blocked until G is complete **and** both D items exist, or withdrawal |

Reading the table. (1) A row that contains any of EX-1, EX-2 or EX-3 needs complete §0.2
closure before WP-2 may be prompted, authorized or rely on that boundary; a recorded
decision is not that closure. (2) **No B2-S row lacks PD-2b:** each B2-S row names both acts'
membership, carries EX-3 for each act left out, and keeps the `start` and `stop` role of
each act put in. (3) Row S-2 is the only row with no exception. (4) Row F-1 is the R1 / R2
recommendation (B2-F-A with B3-OUT). (5) **Step 5 of §0.2 applies to every row as written:**
WP-2 may be prompted only after the G cell is complete **and** every design prerequisite in the D
cell exists; §10.3 verifies all sixteen rows.

**Other alternatives.**

| Alternative | LR exceptions | §0.2 items | G | D | W |
|---|---|---|---|---|---|
| **BC-2** | not an LR exception | **yes**, if a maintainer reads R3-ROOT as a narrowing, before any WP-9 selection of LIT-FULL | PD-1 (not a WP-2 gate) | none | none for WP-2 … WP-7 |
| **BC-3** | not requested; BQ-4 forbids it | would enter §0.2 | — | — | — |

### 10.2 Follow-on redesign and documentation items (none performed, none authorized)

| Item | Change | Where it would be applied |
|---|---|---|
| **FR-1** | **a documentation amendment**, not a design package: it records the selected BQ-2 boundary and adds the `start` and `stop` roles to the commissioned work, and amends the AP-2 and OS-6 literals' text to name them. It designs nothing and is not complete before WP-2. The design activities it names are owned by later WPs (table below) | R8 §9.6.1 role table; Appendix A (A8 and the literals); D §4.2.5-R2 (e), R4 (e), through OH-S0d or a dated addendum. Not itself §0.2 (Q-5), and it depends on the selected boundary having passed §0.2. Whether its text is applied before the WP-2 prompt, or carried by that prompt, is for the later authority |
| FR-2 | WP-3 to specify DI-2 and the stop call among the loader-free interfaces | WP-3 |
| FR-3 | R8 §9.3 (E-4) and §9.6.1 to be completed: the OS-6 stop and `H-1R` classified | OH-S0d / a dated addendum, a documentation correction, **not edited here** |
| FR-4 | record EX-1, EX-2 and, if chosen, EX-3 through §0.2 | change control, **not opened by this assignment** |
| FR-5 | A7 / A-II-03: `/usr/bin/python3.14` with the HB-1 sentence | OH-S0d / OH-S4 |

**Which later WP owns each design activity of FR-1's roles** (B2-F-A and the mixed
answers that put an act in the set; none is performed or authorized here):

| Activity | Owner |
|---|---|
| record the selected boundary and name the `start` and `stop` roles in the commissioned work | FR-1, a documentation amendment (not a design activity) |
| system-call-intent inventory of each role | WP-2 |
| loader-free interface for DI-2 (one `StartTransientUnit` call carrying the accepted AP-2 properties) and for one `stop` of one named unit | WP-3 (FR-2) |
| the images: language class, system-call inventory, blocking and `EINTR` analysis, bounds | WP-4 |
| proof method and evidence plan (D9, PO-17) per image | WP-5 |
| the equivalence mapping of the accepted steps | WP-6 |
| size and review-cost estimate | WP-7 |

### 10.3 Verification of the sixteen combinations against the compact gate

Rule checked: **WP-2 may be prompted only after steps 1–3 and every applicable item among
4 and 4′ of §0.2.** Applied mechanically to each worked row of §10.1:

* steps 1–3 apply to every row: independent acceptance of WP-1 (step 1) and recorded PD-2a and
  PD-2b (step 2) and PD-3 (step 3);
* step 4 applies to a row for each exception it contains, and each needs its complete §0.2 item:
  EX-1 if PD-2a is B2-F; EX-3 for each act PD-2b leaves out, under either PD-2a answer; EX-2 if PD-3
  is B3-OUT;
* step 4′ applies to a row for each design prerequisite it contains: B2-N if PD-2a is B2-S; the
  installer design if PD-3 is B3-IN;
* a row with items in **both** step 4 and step 4′ stays blocked until **both** are complete.

The table was **derived from the rule** (not copied from §10.1) and then compared with the G and D
cells of §10.1 for all sixteen rows by a scratch script that parsed the rows from this file. The
derived and the recorded prerequisites were equal for every row (handback §5).

| Row | Step 4: §0.2 closures required | Step 4′: design prerequisites required | Needs both 4 and 4′? | WP-2 may be prompted only after |
|---|---|---|---|---|
| **F-1** | EX-1, EX-2 | none | no | steps 1–3, the step 4 closures |
| **F-2** | EX-1 | installer design | **yes** | steps 1–3, **both** the step 4 closures and the step 4′ designs |
| **F-3** | EX-1, EX-3 (stop), EX-2 | none | no | steps 1–3, the step 4 closures |
| **F-4** | EX-1, EX-3 (stop) | installer design | **yes** | steps 1–3, **both** the step 4 closures and the step 4′ designs |
| **F-5** | EX-1, EX-3 (start), EX-2 | none | no | steps 1–3, the step 4 closures |
| **F-6** | EX-1, EX-3 (start) | installer design | **yes** | steps 1–3, **both** the step 4 closures and the step 4′ designs |
| **F-7** | EX-1, EX-3 (start), EX-3 (stop), EX-2 | none | no | steps 1–3, the step 4 closures |
| **F-8** | EX-1, EX-3 (start), EX-3 (stop) | installer design | **yes** | steps 1–3, **both** the step 4 closures and the step 4′ designs |
| **S-1** | EX-2 | B2-N | **yes** | steps 1–3, **both** the step 4 closures and the step 4′ designs |
| **S-2** | none | B2-N, installer design | no | steps 1–3, the step 4′ designs |
| **S-3** | EX-3 (stop), EX-2 | B2-N | **yes** | steps 1–3, **both** the step 4 closures and the step 4′ designs |
| **S-4** | EX-3 (stop) | B2-N, installer design | **yes** | steps 1–3, **both** the step 4 closures and the step 4′ designs |
| **S-5** | EX-3 (start), EX-2 | B2-N | **yes** | steps 1–3, **both** the step 4 closures and the step 4′ designs |
| **S-6** | EX-3 (start) | B2-N, installer design | **yes** | steps 1–3, **both** the step 4 closures and the step 4′ designs |
| **S-7** | EX-3 (start), EX-3 (stop), EX-2 | B2-N | **yes** | steps 1–3, **both** the step 4 closures and the step 4′ designs |
| **S-8** | EX-3 (start), EX-3 (stop) | B2-N, installer design | **yes** | steps 1–3, **both** the step 4 closures and the step 4′ designs |

Reading the table. (1) **A row with items in both step 4 and step 4′ is released by neither alone.**
A row with items in only one of them needs that step's items, together with steps 1–3, and nothing
else is skipped. (2) Every B2-S
row (S-1 … S-8) lists B2-N; every B3-IN row (F-2, F-4, F-6, F-8, S-2, S-4, S-6, S-8) lists the
installer design. (3) Every row that lists a §0.2 closure lists one complete item for each
exception. (4) Rows that need **both** (F-2, F-4, F-6, F-8, S-1, S-3, S-4, S-5, S-6, S-7, S-8) stay blocked until both are complete. (5) Row
S-2 lists no step 4 item and two step 4′ items: it is the literal no-exception LIT-FULL and is
blocked on design prerequisites alone. (6) Union rule U6 and the exact successor-gate paragraph are
unchanged.

---

## 11. BQ-4 and its constraints on WP-2 … WP-7

**Recorded:** under the commissioned LIT-FULL direction, LR-2 admits **no** dynamic
child in any root procedure's process tree. The children R8 §9.3 lists (DI-1 …
DI-6: `systemctl`, `systemd-run`, `pkcheck`, `sleep`) cannot be kept as children. A
proposal to keep any of them is SCDC (R8 §9.4, BC-3) and **enters §0.2; it is not a
decision of any WP**. [A+N]

It decides that the process tree of every procedure in the final set contains only
static images from the first image on. It does **not** decide where a
`sudo`-started tree begins (BQ-2) or whether the installer is in the set (BQ-3). It
changes no accepted behaviour: R8 §7.5 says HS-1 … HS-6, SN, WB, RE and GD hold
"under every Route 3 outcome that keeps any child process", and a forked static
process still falls under them.

| WP | Constraint from BQ-4 [N] |
|---|---|
| WP-2 (inventory) | every process creation is classified as a fork continuing in a static image or an `execve` of a **static** image the design controls; no row is an `execve` of a distribution program; the `spawn()` call sites of R8 §7.3 (rows 1 … 3g) become rows of those two forms; rows are kept per procedure and sub-role; **the installer's operations are enumerated only if B3-IN is recorded** |
| WP-3 (interfaces) | each of DI-1 … DI-6 is a loader-free interface with version-bound citation for `systemd 259.5-0ubuntu3.4` and `polkit 127-2ubuntu1.1`, or in-process; DI-5 must give decisions equal to `pkcheck`'s, and the exit-status contract R2 §6.4 (e) cites is a command-line contract that does not carry over (R8 §9.3 E-2); DI-6 cannot remain `sleep`, and whether the subject is a static fork or image is WP-4's; DI-2 and a stop call join only if SA-1 and SA-2 are in the set; WP-3 remains a citation slice with **no network research** authorized |
| WP-4 (images) | no image may `execve` a dynamic program; the inventory covers process creation, credential change, signal send and wait; no design relies on a dynamic helper "for convenience" |
| WP-5 (proof method) | D9 / PO-17 per image, including every static image any root procedure `execve`s, so the image count follows BQ-2 and BQ-3 |
| WP-6 (mapping) | a behaviour that cannot be preserved without a dynamic child is **recorded as not preserved and returned to Peter**, never silently covered |
| WP-7 (estimate) | states the count and size of images, which BQ-2 and BQ-3 fix, and the B3-IN delta as a separate line |

**A stop rule for any package** [N]: if a package finds that a function cannot be
performed without a dynamic child, it stops and reports. That is a candidate SCDC
(BC-3) and a §0.2 matter, not a WP result.

---

## 12. Inputs that WP-2 may rely on

WP-2 is **not authorized** by this record, and the gate of §2 applies first.

### 12.1 Inputs that do not depend on BQ-2 or BQ-3

| Input | Status |
|---|---|
| BQ-1 = R3-ROOT; BQ-4 = no dynamic child | recorded by the commissioned direction (§3) |
| RT-1 … RT-4 and their DI map (§5.2, §6.1) | accepted text [A] |
| LR-1 … LR-6, RH-1 … RH-3, DI-1 … DI-6 | accepted text [A: R8 §9.2, §9.3] |
| the §7.3 inventory, rows 1 … 22 (including the sends and validation of rows 3a … 3g), as the starting table | accepted text [A: R8 §7.3, §9.5 WP-2] |
| HS-1 … HS-6, SN, WB, RE, GD, PK/2, SG, LD, BS, SD | accepted text [A: R8 §7] |

### 12.2 Inputs that WP-2 may rely on only after the gate closes

"The gate" is G and D of §10.1's union rule for the combination Peter records.

| Input | Depends on | Holds when |
|---|---|---|
| WP-2 covers RT-5 (`attest`) from its first image | PD-2a | **B2-F:** yes, from the first design-controlled image. **B2-S:** only after B2-N, from B2-N's start path |
| WP-2 covers the `start` act (SA-1) | PD-2b for `AP-2`, under **either** PD-2a answer | **yes iff `AP-2` is in the set.** Under B2-S its start follows B2-N. If `AP-2` is out, it is not inventoried and EX-3 covers it |
| WP-2 covers the `stop` act (SA-2) | PD-2b for the stop, under **either** PD-2a answer | **yes iff the stop is in the set**, on the same terms. If the stop is out, it is not inventoried and EX-3 covers it |
| `sudo` is outside every inventoried tree | PD-2a, PD-2b | **Answered per act, with no yes/no contradiction.** *For an act PD-2b puts in:* **B2-F:** `sudo` is a launch preamble outside the inventoried tree (EX-1). **B2-S:** `sudo` is **absent** from the inventoried tree, because B2-N replaces the current `sudo` start and the tree begins at B2-N's loader-free start path. *For an act PD-2b leaves out (either PD-2a answer):* the act is not inventoried and is not started by B2-N; its **entire existing `sudo` plus distribution-client path is outside the boundary** under EX-3 and is **not inventoried as a root procedure** (rule PT of §10.1) |
| WP-2 covers installer operations (PF, PT, journals, RB-1, RS-1) | PD-3 | **no** under B3-OUT; **yes** under B3-IN, after the installer design and, under B2-S, after B2-N |
| the exceptions EX-1 / EX-2 / EX-3 exist as a boundary | PD-2a, PD-2b, PD-3 **and §0.2 closed** | proposed, not approved, until §0.2 closes for each |
| B2-N's start path exists | PD-2a = B2-S | a **D** item, not an input: it must exist, separately authorized and reviewed, before WP-2 may rely on any in-set act beginning at it |

No row of this table hard-codes the `start` or `stop` act as absent under B2-S: each is
present or absent by PD-2b alone.

### 12.3 Inputs WP-2 may **not** rely on, whatever Peter decides

* the §9 sentences, or any other text of this record, as accepted: they are
  proposals until Peter records them;
* any host fact: `sudo`'s configuration or linkage, the linkage of `systemd-run`,
  `systemctl`, `pkcheck` or `sleep` (MF-9 is uncollected), MF-1 … MF-8;
* any citation not already in the accepted R2 record;
* a view that EX-1, EX-2 or EX-3 is approved before §0.2 closes it; and
* a view that BC-2 is resolved.

---

## 13. The review questions, resolved or converted

### 13.1 Resolution

| Q | Question | Resolution |
|---|---|---|
| **Q-1** | Is treating the `ubuntu`-run entry as outside the set a narrowing of DR1 §5.3 (R8 BC-2)? | **Not resolved by any accepted record; converted to PD-1.** R8 §9.1 says "if a maintainer treats R3-ROOT as a narrowing … adopting it is a scope question for §0.2, and I record it as BC-2". G-1 chooses "the R3-ROOT reading for investigation" and says the direction "preserves the accepted Route 3 boundary", but it neither reads R3-ROOT as a narrowing nor rules that it is not one, and it opens no BC-2 change. No inference is made |
| **Q-2** | Is the list of `sudo`-started acts complete; is `H-1R` in the class; did R8 consider SA-2? | **Resolved by the record, with two classifications left to Peter.** Complete as far as the accepted record goes (§1.2, 24 `sudo -n` lines in D and 8 in R8 (11 occurrences), no further literal). SA-2 is an accepted act that R8 names (§8.2, Appendix B) but does not classify; `H-1R` is in D and not in R8. Both classifications are **PD-2b** and **PD-3** |
| **Q-3** | Is B3-OUT an exception or only set membership? | **Resolved by the accepted record: an exception** (§8.5: R8 §9.6.1, §9.4, §12.2 BC-4, §13.1 HB-1; independent review) |
| **Q-4** | Does the OH-D-6 reasoning of R8 §2.4 reach inputs that `ubuntu` itself sets on a `sudo`-started path? | **Resolved.** OH-D-6 is a decision of Peter's: `ubuntu` has unrestricted `sudo`, and "every later record must state that limit" (D §3.6; D §4.2.5-R1 (b) `authority_limit`). An ambient input set by the account that can already be root is therefore a consistency limit, not an escalation. R8 §9.9 still holds that it remains an *input*. What is left is wording: **EX-1's residual statement must say so in the §0.2 impact assessment**. It is not a new decision |
| **Q-5** | Are the added `start` and `stop` roles an in-scope consequence of LR-4, or a design addition? | **Split.** The `start` role is a *consequence* of LR-4 **if** AP-2 is in the set (R8 §9.2 LR-4; §9.3 DI-2). The `stop` role has **no DI row** in R8 and is a *design addition*. Both are therefore part of **PD-2b**; both need FR-1 (a documentation amendment, not itself §0.2) |
| **Q-6** | Should BQ-2a and BQ-2b be decided separately? | **Resolved procedurally: yes.** They are now PD-2a and PD-2b. Peter may still answer BQ-2 with one sentence (§9.1), which then answers both |
| **Q-7** (handback) | Does "stop and report" mean what the original handback said it means? | **Resolved.** Neither the independent review nor the R1 authority treats the original return as a `HARD STOP`; both proceed to remediation and to the gate of §2 |

### 13.2 The exact Peter decisions

None is made here. Each is a decision for Peter as Acceptance Authority. A decision
that contains an exception does not become effective until §0.2 closes.

| ID | Decision | Alternatives | Needed before |
|---|---|---|---|
| **PD-1** | Is R3-ROOT, with the `ubuntu`-run entry outside the root set, a *narrowing* of DR1 §5.3? | **N:** the working restatement stands and BC-2 is not needed. **Y:** BC-2 enters §0.2 | any WP-9 selection of LIT-FULL. **Not** a WP-2 gate in the commissioned sequence |
| **PD-2a** | Where does a `sudo`-started root procedure begin? | B2-F (first design image; EX-1) · B2-S (at `sudo`; the current `sudo` start cannot meet LR-2 and is attainable only if B2-N replaces it for every in-set act). **B2-S decides no membership question** | WP-2 |
| **PD-2b** | Which `sudo`-started acts are root procedures: `AP-2`? the OS-6 `stop`? | in/out for each (§7.4's 2×2), **under both PD-2a answers**; each "out" adds an EX-3 part and a §0.2 item, each "in" keeps a role in WP-2 … WP-7 (and needs B2-N's start path under B2-S) | WP-2 |
| **PD-3** | Is the installer class (H-1, RB-1, RS-1, **H-1R**) among the root procedures? | B3-OUT (EX-2, HB-1) · B3-IN (a Python-free installer package). Independent of PD-2a and PD-2b | WP-2 |

PD-2a, PD-2b and PD-3 are three independent decisions. **All three are required, recorded, before
WP-2 in every combination** (§2.2, §10.1 U5). Peter may still answer BQ-2 with one sentence
(§9.1), which then answers PD-2a and PD-2b together; a sentence that answers PD-2a alone does
not answer PD-2b.

---

## 14. Remediation acceptance checklist

For independent Codex re-review and Peter's recorded decisions. Unticked: nothing
here is accepted. **R6C-1 … R6C-12** are the twelve checks of the R6 prompt; **R4C-1 … R4C-13**
are the checks of the R4 prompt, **R3C-1 … R3C-14** those of the R3 prompt, and **RC-2 … RC-17**
carry the R1 checklist forward, all where they still apply. **RC-16 is retired and replaced by
RC-16′** (WP1-R4R-2).

- [ ] **R6C-1** All twelve required reads reached EOF, and this prompt matched its authority pin
  before any edit (§1.1, header, handback).
- [ ] **R6C-2** All twelve controller-created transition snapshots (R4-return, R5-authorization,
  R6-authorization), and the four recovered R4-authorization snapshots, exist, match their indexed
  digests and were not modified (§0.8.1; handback §5, §9).
- [ ] **R6C-3** The four R6-authorization snapshots match the pre-return pointer text or controlled
  block byte for byte (§0.8.2; handback §5).
- [ ] **R6C-4** WP1-R4R-1 and WP1-R4R-2 are each explicitly addressed (§0.8).
- [ ] **R6C-5** RC-16 no longer makes the stale file-set claim (RC-16 and RC-16′ below; §0.8.4).
- [ ] **R6C-6** All R4 process-tree, cumulative-gate and sixteen-combination corrections remain
  intact (§7.4; §10.1 Table A and rule PT-1 … PT-5; §10.3; §12.2).
- [ ] **R6C-7** The exact R6 successor gate appears in §2.4 and, word for word, in all four returned
  pointers (handback §5).
- [ ] **R6C-8** BQ-2, BQ-3, EX-1, EX-2, EX-3, BC-4 and BC-2 remain undecided or unapproved
  (§0.3, §2.3, §10.0, §13.2).
- [ ] **R6C-9** Concrete Route 3 remains unestablished and no successor is authorized
  (§3, §12, §15).
- [ ] **R6C-10** Prior deliverables, indexes, snapshots and accepted records are unchanged
  (handback §5, §9).
- [ ] **R6C-11** The handback is linked from `docs/review/Handover information` at every terminal
  state (handback §3).
- [ ] **R6C-12** No prohibited operation occurred (handback §10).

The R4 checklist follows as history. **R4C-1 … R4C-13** are the thirteen checks of the R4 prompt.

- [ ] **R4C-1** All thirteen required reads reached EOF, and this prompt matched its authority
  pin before any edit (§1.1, header, handback).
- [ ] **R4C-2** WP1-R3R-1, WP1-R3R-2 and WP1-R3R-3 are each explicitly addressed (§0.7).
- [ ] **R4C-3** No post-B2-N in-set path contains `sudo`, while out acts remain wholly outside
  the boundary under EX-3 (§7.4 process-tree table; §10.1 Table A and rule PT-1 … PT-5; §12.2).
- [ ] **R4C-4** The compact gate requires every applicable governance closure and design
  prerequisite (§0.2 step 5; §10.3).
- [ ] **R4C-5** All sixteen combinations remain mechanically consistent with U1 through U7
  (§10.1; §10.3; handback §5).
- [ ] **R4C-6** The exact R4 successor gate appears in §2.4 and, word for word, in all four
  returned pointers (handback §5).
- [ ] **R4C-7** The archive erratum records the historical gap without fabricating content and is
  linked by all four archive indexes (the erratum; handback §3).
- [ ] **R4C-8** The controller-created R3-return snapshots remain unchanged (handback §5).
- [ ] **R4C-9** All R3 corrections and the earlier R2 corrections remain intact (§0.5 … §0.7).
- [ ] **R4C-10** BQ-2, BQ-3, EX-1, EX-2, EX-3, BC-4 and BC-2 remain undecided or unapproved
  (§0.3, §2.3, §10.0, §13.2).
- [ ] **R4C-11** Concrete Route 3 remains unestablished and no successor is authorized
  (§3, §12, §15).
- [ ] **R4C-12** Prior deliverables and accepted records are unchanged (handback, digests).
- [ ] **R4C-13** No prohibited operation occurred (handback).

The R3 checklist follows. Its items R3C-1 … R3C-14 are the checks of the R3 prompt and are carried
as history; RC-2 … RC-17 carry the R1 checklist forward, with RC-16 retired and replaced.

- [ ] **R3C-1** All thirteen required reads reached EOF, with line count, byte count
  and SHA-256 recorded (§1.1, handback), and this prompt matched its authority pin
  before any edit (header).
- [ ] **R3C-2** WP1-R2R-1 and WP1-R2R-2 are each explicitly closed (§0.6).
- [ ] **R3C-3** PD-2a, PD-2b and PD-3 appear as governance prerequisites in every
  complete BQ-2 / BQ-3 combination (§2.2; §10.1 rule U5 and the G cell of each of
  the sixteen worked rows).
- [ ] **R3C-4** Every B2-S act classified **out** carries EX-3 and complete §0.2 closure
  (§7.4; §10.1 Table B, U1 and U2; rows S-3 … S-8).
- [ ] **R3C-5** Every B2-S act classified **in** retains its later-WP role after B2-N
  (§7.4; §10.1 Table B, U4 and U7; rows S-1 … S-6; §12.2).
- [ ] **R3C-6** B3-OUT adds EX-2 and B3-IN adds its separate installer design
  prerequisite in every combination (§10.1 Table C, U1 and U3; all sixteen rows).
- [ ] **R3C-7** The canonical matrix has no collapsed or unclassified decision dimension
  (§10.1).
- [ ] **R3C-8** The exact successor gate appears in §2.4 and, word for word, in all four
  returned pointers.
- [ ] **R3C-9** The reproduced R8 count is eight lines and eleven occurrences everywhere
  (§1.2, §13.1 Q-2, handback); nine appears only as R1's non-reproducing figure.
- [ ] **R3C-10** All four R2 corrections remain intact: EX-3 is not an LR-4 exception (§10.0;
  COR-09, COR-16); G, D and W stay separate and FR-1 is a documentation amendment (§2.2,
  §10.2); `H-1R` is named in PD-3 with no invocation literal asserted (§9.2); COR-01 …
  COR-16 are sixteen corrections, distinct from the thirteen complete-read records (§6.4).
- [ ] **R3C-11** BQ-2, BQ-3, EX-1, EX-2, EX-3, BC-4 and BC-2 remain undecided or
  unapproved (§0.3, §2.3, §10.0, §13.2).
- [ ] **R3C-12** Concrete Route 3 remains unestablished and no successor is authorized
  (§3, §12, §15).
- [ ] **R3C-13** Prior deliverables and accepted records are unchanged (handback,
  digests).
- [ ] **R3C-14** No prohibited operation occurred (handback).
- [ ] **RC-2** The successor gate is exact (§2.4): review and Peter's decisions always;
  §0.2 closed before WP-2 may be prompted, authorized or rely on the boundary, if an
  answer contains an exception (EX-1, EX-2 or EX-3); a decision is not §0.2 approval;
  the literal path stays blocked until a separately authorized, reviewed loader-free
  privileged-start design exists, or Peter withdraws the design; BC-2 remains unresolved.
- [ ] **RC-4** The decision/gate flow is shown in compact tables (§0.2, §10.1).
- [ ] **RC-5** The final root-procedure set and the `sudo`-started set are
  enumerated (§5.2, §5.3), with OS-6, H-1R, AP-2, `attest`, H-1, RB-1 and RS-1
  explicitly disposed of (§5.4).
- [ ] **RC-6** Every caller, first image, controlled-image status and DI-1 … DI-6
  mapping is verified against the whole accepted record (§6.1).
- [ ] **RC-7** Accepted fact, textual observation, new recommendation and correction
  are distinguished (§1.3), and no host fact, external citation or invented source
  appears.
- [ ] **RC-8** The complete reading's effect on the original return is stated, with
  an exact old-to-new table (§6.2, §6.4) and a claim ledger (§6.3).
- [ ] **RC-9** BQ-2 and BQ-3 alternatives and recommendations are in plain language
  and both stay pending (§7, §8, §9).
- [ ] **RC-10** Every exception, §0.2 change, design prerequisite and downstream WP
  dependency each combination requires is stated, once, in the canonical matrix
  (§10.1).
- [ ] **RC-11** Q-1 … Q-6 (and Q-7) are resolved where the record permits and
  otherwise converted into exact Peter decisions (§13).
- [ ] **RC-13** The commissioned facts are preserved: BQ-1 = R3-ROOT, BQ-4 permits no
  dynamic child, concrete Route 3 is unestablished, WP-2 … WP-7 are separately gated
  (§3, §11).
- [ ] **RC-14** WP-2's inventory is **not** performed; only R8's DI map is used.
- [ ] **RC-16 (retired, WP1-R4R-2).** The R1 assertion "Only the proposal, the handback and the four
  pointers changed" described the R1 file set. It is **not** carried as the result of R4, R5 or R6, and
  nothing in this record claims it for them. It is replaced by RC-16′.
- [ ] **RC-16′** The exact R6 permitted file set is **two created deliverables** (this proposal and its
  handback) **and the returned current-state pointer edits** (the Handover, `status.md`, §20 only of
  `docs/implementation-plan.md`, and the restriction banner only of
  `docs/operations/disposable-test-server.md`). The sixteen controller-created, indexed snapshots are
  **pre-existing prerequisites** that this assignment verified and did not change; it edited no archive
  index, register, accepted record, authority, exact prompt, prior deliverable or historical snapshot
  (§0.8.4; handback §3, §9).
- [ ] **RC-17** The handback lists files, the complete-read evidence, the proposal's
  line count, byte count and SHA-256, the correction for each finding, checks and
  results, unresolved Peter decisions and gates, checks not run, and the statement
  that no prohibited operation occurred.

---

## 15. What this proposal does not establish

It establishes no host fact. It does not show that `sudo` cannot be controlled,
that a static image can be built, or that B2-N is impossible: it shows only that no
accepted record designs, cites or evaluates any of them. It does not discharge any
obligation (PO-12′, PO-19, PO-17, PO-SN), does not establish concrete Route 3, and
does not touch the standing `HARD STOP: concrete Route 3 not established`. It does
not decide BQ-2, BQ-3, PD-2a, PD-2b or PD-3, approve or open any exception or §0.2 entry, resolve BC-2,
accept WP-1, or authorize WP-2 or any later package. It does not recreate the pre-R3-return
pointer snapshots that the repository does not hold, and the erratum that records the gap decides
and authorizes nothing. It does not recover those R3 bytes: the four R4-authorization snapshots of
§0.8 were recoverable from Appendix A and are a different matter. It creates, rewrites and repairs
no snapshot, and it does not make the next transition's snapshots: those must be in place and
indexed before any later authorization replaces the pointers this return writes (§0.8.3).
