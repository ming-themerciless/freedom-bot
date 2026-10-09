# Proposal — LIT-FULL WP-1 R2 remediation: the audited R3-ROOT boundary, BQ-2 and BQ-3 decision-ready, the EX-3 classification corrected, the decision matrix repaired and the §0.2 successor gate kept

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R2-20261008-11`

Date: 2026-10-08

Executor: Claude Code (Sonnet 5.5) on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-claude-prompt.md),
10,678 bytes, SHA-256 `bb88208f76a4d9dcfd7f76cb0678c3e44193a4b9e9a25af0a1b7fb450300256f`,
recomputed with `wc -c` and `sha256sum` before any edit and equal to the pin in the
[R2 remediation authority](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-authority.md)
(itself 2,378 bytes, SHA-256 `c73fa2a86bf662943f91408146009d945ab682da1b02ce56ceba00bb9f0e1a7a`).

Durable handback: [`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-handback.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-handback.md).

Earlier deliverables and reviews, **preserved unchanged**: the
[original WP-1 proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-boundary-proposal.md)
(53,995 bytes, SHA-256 `4c4535b8c1c7f207d6d82e039a9395b0bd97a6bfe5cc3cb33108e1fdd2b34775`)
and [its handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-handback.md); the
[R1 remediation proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-proposal.md)
(75,452 bytes, 997 lines, SHA-256 `121969c4e305a7d2cbba587b82bbaf43ec2124ba5b4250ddfd4a963caf7bdf8c`)
and [its handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-handback.md); the
[independent review of the original return](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-lit-full-wp1.md); and the
[independent re-review of the R1 remediation](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation.md).

**Status: a proposal for independent Codex re-review and Peter Duscha's later
decisions. Nothing in it is accepted. WP-1 remains `changes requested` and is not
accepted. BQ-2 and BQ-3 are PENDING PETER'S DECISION and this record decides
neither. It approves no exception (EX-1, EX-2, EX-3 or BC-4), opens and executes no
§0.2 change control, resolves no BC (BC-2 included), establishes no concrete
Route 3, selects LIT-FULL for no implementation and authorizes neither WP-2 nor any
later package.**

This document is **cumulative and self-contained**: it carries the R1 remediation
forward with the four R1 re-review findings corrected, and a reader needs the
earlier proposals only to compare. Where this record corrects the original WP-1
return, the correction is listed in §6.4 (**sixteen** corrections, COR-01 … COR-16).
Where it corrects the R1 remediation, the correction is listed in §0.5.

---

## 0. Outcome

### 0.1 In one page

* **What was asked.** Remediate the four findings of Codex's independent re-review
  of the R1 remediation: **WP1-R1R-1 (Blocking)**, **WP1-R1R-2 (Important)**,
  **WP1-R1R-3 (Important)** and **WP1-R1R-4 (Optional)**; carry the R1 successor gate
  forward word for word, changing only "R1 remediation" to "R2 remediation"; and
  keep everything the R1 audit established. No new analysis of the boundary was
  asked for, and none was made. Nothing is accepted, decided or authorized.
* **The four findings are each closed (§0.5).**
  * **WP1-R1R-1:** EX-3 is no longer called an LR-4 exception. LR-4 binds a root
    procedure in the final set and reaches DI-2 only if `AP-2` is in that set
    (COR-09). Under B2-F-B, `AP-2` and/or the OS-6 `stop` are outside the set, so
    their exclusion is not a free-standing LR-4 exception. EX-3 is the proposed
    **wider BC-4 boundary exception** for whichever whole `sudo`-started acts Peter
    leaves outside the set. §10 now holds one canonical table (§10.0, §10.1).
  * **WP1-R1R-2:** the §2.2 matrix keeps three categories apart: the governance
    prerequisites before WP-2, the separate design prerequisites before WP-2, and
    the work allocated to WP-2 … WP-7 after the gate. FR-1 is a documentation
    amendment that records the selected boundary and adds the `start` and `stop`
    roles to the commissioned work. It is **not** a design package and is not
    completed before WP-2; each design activity it names belongs to a later WP
    (§10.2).
  * **WP1-R1R-3:** the proposed BQ-3 decision sentence names `H-1R` expressly, and
    classifies it only as far as the accepted record supports. It asserts no
    invocation literal for `H-1R`. The inference that it runs through the
    verified-exec stub is stated outside the text Peter is asked to approve (§9.2).
  * **WP1-R1R-4:** the correction count is **sixteen** (COR-01 … COR-16, §6.4)
    everywhere.
* **Two numbers, not to be confused.** This prompt required **twelve** complete-read
  records (§1.1). The audit of the original return produced **sixteen** corrections
  (§6.4). They are unrelated.
* **The successor gate is unchanged (§2).** Independent Codex re-review of this
  remediation and Peter's recorded BQ-2 and BQ-3 decisions are always necessary. If
  either chosen answer contains an LR exception, the complete implementation-plan
  §0.2 process must close **before WP-2 may be prompted, authorized or rely on that
  boundary**, and a Peter decision is not itself §0.2 approval. If Peter retains
  literal no-exception LIT-FULL, WP-2 stays blocked until a separately authorized,
  reviewed loader-free privileged-start design makes the boundary attainable, or
  Peter withdraws the affected design. The same gate, word for word, is in all four
  pointers (§2.4).
* **Carried from the R1 remediation, unchanged in substance.** The complete-record
  audit and its **sixteen** corrections (§6); the **final proposed sets** (§5):
  root procedures that R8 names **RT-1 … RT-5** (consume, holder, stop-post,
  backstop, `attest`), and **seven** `sudo`-started paths (`attest`, `AP-2`, the OS-6
  `stop`, and the installer class H-1, RB-1, RS-1, H-1R) with the dispositions of
  §5.4; the plain-language BQ-2 and BQ-3 alternatives and recommendations (§7, §8),
  still pending; and the resolution or conversion of Q-1 … Q-6 and Q-7 (§13).
* **BQ-2 and BQ-3 recommendations (§7, §8) are unchanged in kind and still pending.**
  BQ-2: begin a `sudo`-started procedure at the first image the design controls,
  with `sudo` as a launch preamble excepted from LR-2 and a static image for
  `attest`, `AP-2` and the OS-6 stop (B2-F-A). BQ-3: leave the installer class, now
  expressly including `H-1R`, outside the set as an exception with HB-1 (B3-OUT).
  Both recommendations **contain LR exceptions** (EX-1, EX-2), so under §2 they
  would enter §0.2 before WP-2.
* **Commissioned facts, unchanged (§3).** BQ-1 is R3-ROOT for the investigation. BQ-4
  permits no dynamic child. Concrete Route 3 remains unestablished. WP-2 through
  WP-7 are separately gated, and WP-9 is Peter's later choice.

### 0.2 Decision and gate flow

| Step | Gate | Applies | Closed by | Effect on WP-2 |
|---|---|---|---|---|
| 1 | independent Codex re-review of this remediation | **always** | Codex, then Peter accepts | WP-1 stays `changes requested` until accepted |
| 2 | BQ-2 recorded (PD-2a, PD-2b, §13) | **always** | Peter | a decision is **not** §0.2 approval |
| 3 | BQ-3 recorded (PD-3, §13) | **always** | Peter | the same |
| 4 | **§0.2 change control**, steps 1–5 (§2.3) | **if** a chosen answer contains an LR exception (EX-1, EX-2, EX-3; §10.0) | Product Owner recommendation and Technical Lead review, Acceptance Authority approval, a new baseline version if the roadmap or release boundary changes | must be **closed before WP-2 may be prompted, authorized or rely on that boundary** |
| 4′ | a separately authorized, reviewed **design prerequisite**: for B2-S, a loader-free privileged-start design that is not `sudo` (B2-N); for B3-IN, a Python-free installer with a loader-free verified-exec equivalent | **if** Peter retains literal no-exception LIT-FULL for that path, or chooses B3-IN | its own prompt, authority, work ID and Codex review | WP-2 **stays blocked** until it makes the boundary attainable, or Peter withdraws the affected design |
| 5 | WP-2 prompt, authority, work ID, Codex review | only after steps 1–3 and 4 or 4′ | separate | WP-2 only; WP-3 … WP-7 each separately gated |
| later | BC-2 (PD-1) before any WP-9 selection of LIT-FULL | if a maintainer reads R3-ROOT as a narrowing | Peter | not a WP-2 gate |

The row-by-row result for each pair of answers is in §2.2 and, with every LR
exception, §0.2 item, prerequisite and downstream effect, in §10.1.

### 0.3 Decision summary

| Item | Status | Where |
|---|---|---|
| BQ-1 | **recorded**: R3-ROOT, from the commissioned direction | §3 |
| BQ-2 | **pending Peter**. Split into PD-2a (where a `sudo`-started procedure begins) and PD-2b (whether `AP-2` and the OS-6 stop are root procedures). Recommendation B2-F-A. **Contains EX-1.** | §7, §9, §13 |
| BQ-3 | **pending Peter** (PD-3), `H-1R` named without an asserted invocation. Recommendation B3-OUT. **Contains EX-2.** | §8, §9, §13 |
| BQ-4 | **recorded**: no dynamic-child exception | §3, §11 |
| BC-2 | **unresolved**; no accepted record resolves it (PD-1) | §10, §13 |
| §0.2 for EX-1, EX-2, EX-3 | **not opened, not executed, not approved** | §2, §10 |
| BC-4 | **not approved** and not widened by this record | §10.0 |
| WP-2 | **not authorized** | §2, §12 |

### 0.4 What this proposal does not do

It does not decide BQ-2 or BQ-3, approve EX-1, EX-2, EX-3 or BC-4, open or
execute §0.2, resolve BC-2, accept WP-1, establish concrete Route 3, perform WP-2's
system-call-intent inventory, add a design, protocol or external citation, record
any host fact, decide whether `AP-2` or the OS-6 `stop` belongs in the set, decide
whether `H-1R` belongs in the installer class, or touch any host. It uses R8's
DI-1 … DI-6 delegation map only to define boundaries, as the prompt allows.

### 0.5 Closure of the four R1 re-review findings

| Finding | Severity | The defect in the R1 remediation | The correction in this record | Where |
|---|---|---|---|---|
| **WP1-R1R-1** | Blocking | R1 §10.1 said B2-F-B carries EX-3 for "LR-2 and, for DI-2, LR-4". That contradicted R1's own COR-09, COR-16 and §7.5, and the table is the canonical statement of every LR exception | EX-3 is **not** an LR-4 exception. LR-4 applies to a root procedure in the final set and reaches DI-2 only if `AP-2` is in that set. Under B2-F-B, `AP-2` and/or the OS-6 stop are outside the set, so their exclusion is not a free-standing LR-4 exception. EX-3 is the proposed wider BC-4 boundary exception for whichever whole `sudo`-started acts Peter leaves outside the set. BC-4 is not silently expanded, EX-3 is not BC-3, and neither act's membership is decided. Every exception-bearing choice still needs complete §0.2 closure before WP-2 | §10.0, §10.1; §2.2, §7.4, §9.3, §12.2, §13.2 agree |
| **WP1-R1R-2** | Important | R1 §2.2 headed a column "New design package before WP-2 can be meaningful" and put B2-F-A's `start` and `stop` roles in it as "FR-1, documentation amendment only" | the column and rows are replaced by three separate categories (governance prerequisite; separate design prerequisite; work allocated to WP-2 … WP-7). FR-1 is described exactly as a documentation amendment that records the selected boundary and adds roles to the commissioned work, and each design activity is assigned to WP-2, WP-3, WP-4, WP-5, WP-6 or WP-7 | §2.2, §10.1, §10.2 |
| **WP1-R1R-3** | Important | R1 §9.2 defined the class including `H-1R` as "the installer tool run through the verified-exec stub", promoting an inference to fact | the sentence names `H-1R` expressly and classifies it as a separately authorized root re-record operation, read-only plus record write, implemented as a subcommand of the one installer tool. It asserts no invocation literal. The inference is stated outside the sentence and is labelled an inference | §9.2, §5.3 (IC-4), §5.4, COR-13 |
| **WP1-R1R-4** | Optional | R1 §0.1 gave the number of corrections as 14 where §6.4 enumerates COR-01 … COR-16 | **sixteen** is used in §0.1, §0.5, §6.2, §6.4 and the checklist. No figure other than sixteen is used for the corrections; the one quotation of R1's figure is in this cell's "defect" column | §0.1, §6.4, §14 |

---

## 1. Sources, method and fact classes

### 1.1 Complete-read evidence

Each of the **twelve** records the R2 prompt requires was read **from the first
byte to EOF**, in bounded, non-overlapping chunks. The tool's output limit (about
25,000 tokens per call) forced the chunking; each chunk began at the line after the
previous one, and a chunk that exceeded the limit was re-read in smaller chunks, so
no line was skipped. The last chunk of every file ended at the line count shown,
which is `wc -l` of the file. The digests were taken from the same on-disk bytes,
before any edit of this return. Items 2, 3 and 4 are current-state pointers (§20,
the Handover, the restriction banner) that this return edits; their digests are the
**pre-edit** values, and they already carried the R2 authorization when the run
began. The chunk boundaries are in the handback.

| # | File | Lines | Bytes | SHA-256 |
|---|---|---:|---:|---|
| 1 | `.agents/AGENTS.md` | 700 | 36,014 | `87bab4ab8d67e308af0c59b99c8604235ee84d75cfa12448458b1a04cc88390a` |
| 2 | `docs/implementation-plan.md` (pre-edit; §20 is edited) | 2,603 | 128,268 | `c3587ee54edc459f51528b87f452e348c2a3c83b9ec3ea01928f235df96d0f94` |
| 3 | `docs/review/Handover information` (pre-edit) | 55 | 3,889 | `8dcb38224c41b4ffaa7a5cd130e6fe73f67798ecfeb3562d4305ad989cf562d7` |
| 4 | `docs/operations/disposable-test-server.md` (pre-edit; the banner is edited) | 183 | 9,018 | `a72a3e4a89d10cc9f561ebaff883ffd29a8d83c8fe6e0e7c6f8776ea2706a8ad` |
| 5 | `project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation.md` (independent R1 re-review) | 102 | 5,524 | `11524bd52cfbd313fe094c42102583d64f9c833736d078c92aab6db9524f4d9e` |
| 6 | `phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-proposal.md` (R1 proposal) | 997 | 75,452 | `121969c4e305a7d2cbba587b82bbaf43ec2124ba5b4250ddfd4a963caf7bdf8c` |
| 7 | `phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-handback.md` (R1 handback) | 155 | 9,283 | `be268dfd0c5bf77478acef5c80b15daa662461c5692bc67022b77fc08c73d290` |
| 8 | `project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-authority.md` (R1 authority) | 45 | 2,250 | `0da9e8200349149c620dd407631e8cda7c9fa028b72aaba94c02bdf079b40970` |
| 9 | `phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-claude-prompt.md` (R1 prompt) | 155 | 7,482 | `2724e5c19d4edf9084200dc7bde58853864b19d41fadfbebbde4a2b508f4f127` |
| 10 | `project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md` (G-1 decisions) | 46 | 2,455 | `09234e4acada1b3487f9147f0c8c76110a90dc1dc491e6a02f68892c07bab00e` |
| 11 | `phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md` (accepted R8) | 4,816 | 551,246 | `ab5db5010d9d1b2738b04f1ffbd62ab4414d901e9f7f79323ac49f811f660e04` |
| 12 | `phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md` (accepted one-host design, D) | 7,307 | 525,019 | `a752a4b8fe7eb1edf3e3a25decd3a7517ecccc85fedbb0b0b7e003cb7e615d02` |

Items 5 through 12 are under `docs/review/` (items 2 through 4 are named with their
paths). The R2 prompt itself (203 lines) was read completely and its identity
matched its pin before any edit (header). Two further reads were needed and are
recorded in the handback: the R2 authority (45 lines), to verify the pin, and
`docs/project-management/status.md` (56 lines, pre-edit SHA-256
`c164f8ced5bccb1465b2e16f7abf89b09ac778839c0949bc0fa7aa9f8cc22102`), because it is a
pointer this return edits.

The files were consistent with the identities their authorities name: the R1
proposal matches the pin recorded by the independent re-review (75,452 bytes,
997 lines, SHA-256 `121969c4…bf8c`), and the R1 prompt matches its authority pin
(7,482 bytes, `2724e5c1…f127`).

**Not re-read in this return, and carried from the R1 reading.** The accepted OH-S2
R2 citation record and the R8 acceptance record were complete reads of R1, are not
among the twelve this prompt requires, and were **not** read again. Every `[R2 §n]`
citation in this record is therefore carried from the R1 remediation and from R8's
own citations of that record, not re-verified. The same holds for the original WP-1
proposal and handback, which were consulted only through the R1 proposal's ledger
(§6.3) and their digests (header).

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

### 2.2 The gate, by pair of answers

Three categories are kept strictly apart in this section and in §10. They answer
different questions and are not interchangeable.

| Category | What it is | What belongs in it |
|---|---|---|
| **G, governance prerequisite before WP-2** | a recorded decision or a closed governance process that must exist before WP-2 may be prompted or authorized | independent acceptance of WP-1; Peter's recorded BQ-2 and BQ-3 decisions (PD-2a, PD-2b, PD-3); and complete §0.2 closure for any selected exception-bearing answer (EX-1, EX-2, EX-3) |
| **D, separate design prerequisite before WP-2** | a design that does not exist in any accepted record, must be separately authorized and reviewed, and without which the selected boundary cannot be attained | **B2-N**, a loader-free privileged-start design that is not `sudo`, for B2-S; and the **Python-free installer with a loader-free verified-exec equivalent**, for a B3-IN path |
| **W, work allocated to WP-2 … WP-7 after the gate** | work the commissioned readiness sequence performs once G (and D, where it applies) are met | for B2-F-A, the `start` and `stop` roles (FR-1): their inventory (WP-2), interfaces (WP-3), images (WP-4), proof method (WP-5), mapping (WP-6) and estimate (WP-7) |

An *exception-bearing* answer is one that excludes any program or act from the
boundary (EX-1 `sudo`'s loader; EX-2 the installer class; EX-3 a whole
`sudo`-started act, §10.0). A *literal* answer is one that excludes nothing and
therefore needs a start path that is loader-free from its first process. The
definitions are in §10.0.

**FR-1 is in category W for its design activities and is not in category D.** It is
a documentation amendment that records the selected boundary and adds the `start`
and `stop` roles to the commissioned work (§10.2). It is not a completed pre-WP-2
design package, and it designs nothing. B2-F-A has **no category D item**.

| # | BQ-2 | BQ-3 | LR exceptions | G: governance prerequisite before WP-2 | D: separate design prerequisite before WP-2 | W: work allocated to WP-2 … WP-7 after the gate | WP-2 status |
|---|---|---|---|---|---|---|---|
| 1 | B2-F-A (*recommended*) | B3-OUT (*recommended*) | **EX-1, EX-2** | WP-1 accepted; PD-2a, PD-2b (both acts in) and PD-3 recorded; **§0.2 closed for EX-1 and EX-2** | none | RT-1 … RT-5 plus the `start` and `stop` roles: WP-2 inventories them, WP-3 specifies DI-2 and a stop call, WP-4 designs their images, WP-5 gives D9 / PO-17 per image, WP-6 maps, WP-7 estimates. The installer is omitted | blocked until G closes |
| 2 | B2-F-A | B3-IN | **EX-1** | as row 1, for EX-1 only (no EX-2 exists) | **the Python-free installer with a loader-free verified-exec equivalent** (R8 §9.6.1 "a new WP"; not in R8 §9.5) | as row 1, plus the installer's operations (WP-2), one more large image (WP-4), and its delta as a separate line (WP-7) | blocked until G closes **and** D is separately authorized and reviewed |
| 3 | B2-F-B | B3-OUT | **EX-1, EX-2, EX-3** | as row 1, with PD-2b (both acts out); **§0.2 closed for EX-1, EX-2 and EX-3** | none | RT-1 … RT-5 only. No `start` or `stop` role; the installer is omitted | blocked until G closes |
| 4 | B2-F-B | B3-IN | **EX-1, EX-3** | as row 3, without EX-2 | the installer design, as row 2 | RT-1 … RT-5 plus the installer's operations; no `start` or `stop` role | blocked until G closes **and** D is met |
| 5 | B2-S | B3-OUT | **EX-2** only. No `sudo` exception exists to claim | PD-2a (B2-S) and PD-3 recorded; §0.2 closed for EX-2. B2-N may itself be a §0.2 matter | **B2-N** (outside R8's WP list) | after B2-N: RT-5 and the acts PD-2b puts in the set begin at B2-N's start path | **blocked** until B2-N makes the boundary attainable, or Peter withdraws the affected design |
| 6 | B2-S | B3-IN | **none** | PD-2a and PD-3 recorded. No exception to close; B2-N may itself be a §0.2 matter | **B2-N** and the installer design | after both: as row 5 plus the installer's operations | **blocked** until both exist, or Peter withdraws the affected design |
| 7 | B2-F, mixed: `AP-2` in, OS-6 `stop` out | B3-OUT or B3-IN | **EX-1, EX-3** (the left-out `stop` act); plus EX-2 under B3-OUT | as rows 1 and 3; PD-2b in/out | the installer design under B3-IN; otherwise none | RT-1 … RT-5 plus the `start` role only | blocked until G (and D under B3-IN) |
| 8 | B2-F, mixed: `AP-2` out, OS-6 `stop` in | B3-OUT or B3-IN | **EX-1, EX-3** (the left-out `start` act); plus EX-2 under B3-OUT | as rows 1 and 3; PD-2b out/in | the installer design under B3-IN; otherwise none | RT-1 … RT-5 plus the `stop` role only | blocked until G (and D under B3-IN) |

[N] Every row that contains EX-1, EX-2 or EX-3 needs **complete §0.2 closure before
WP-2 may be prompted, authorized or rely on that boundary** (rows 1 to 5, 7, 8). The
literal path needs category D instead (row 6, and the `sudo` part of row 5). A
recorded choice outside these eight combinations changes only which parts are
present. EX-3 is a BC-4-family boundary exception for whole `sudo`-started acts left
outside the set. It is **not** an LR-4 exception (§10.0).

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

> **Gate before WP-2.** Independent Codex re-review of the R2 remediation and
> Peter's recorded BQ-2 and BQ-3 decisions are always necessary. If either chosen
> answer contains an LR exception, including EX-1 or EX-2 under BC-4, the complete
> implementation-plan §0.2 change-control process must close before WP-2 may be
> prompted, authorized or rely on that boundary. A Peter decision on BQ-2 or BQ-3
> is not by itself §0.2 approval. If Peter retains literal no-exception LIT-FULL,
> WP-2 remains blocked until a separately authorized, reviewed loader-free
> privileged-start design makes the boundary attainable, or Peter withdraws the
> affected design. BC-2 remains unresolved for any later WP-9 selection. WP-1
> remains changes-requested and is not accepted; BQ-2 and BQ-3 are undecided.

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
| **COR-01** | R8 and R2 read "in the sections named … and not in full" (proposal §1.1; handback §4) | the R1 remediation read all 14 records of its own prompt's list to EOF (R1 proposal §1.1). WP-1 R2 repeated a complete read of the twelve records of its own prompt (§1.1 here), and ran the searches of §1.2 over the whole files |
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
  the open cases. The installer class is BQ-3.

BQ-2 "as R8 worded it" assumes each `sudo`-started path has a first image the
procedure controls. That is true only for `attest`, and only after WP-4 designs
one. For `AP-2` and the OS-6 `stop`, `sudo` executes a distribution program
directly.

### 7.4 The alternatives

**B2-S: the procedure begins at `sudo`.** *Plain:* `sudo` is inside the procedure.
LR-2 **cannot be met** by anything the repository contains, because `sudo` is a
dynamic root program in the tree and no accepted record makes it, or a replacement
for it, loader-free. B2-S is the strictest reading; it is not an exception, it is a
boundary under which LIT-FULL is unattainable unless a start path that is not
`sudo` is designed (B2-N).

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
so that "no exception" is shown to depend on it.

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
| mixed | *as §9.1 for the acts named in the set, and the exception of B2-F-B for each act left outside* (the 2×2 of §7.4) |
| B2-S | *a root procedure that `sudo` starts begins at `sudo`.* **LR-2 cannot be met; a start path that is not `sudo` must then be designed (B2-N), or LIT-FULL is not attainable for these paths.** |
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
| **EX-3** | the **whole `sudo`-started act** that Peter leaves outside the set (`AP-2`, the OS-6 `stop`, or both), so that the distribution `systemd-run` and/or `systemctl` that does the act's real work runs as a dynamic root program outside the boundary. It is a proposed boundary exception **wider than EX-1**, in the family of BC-4 | this record. Proposed with B2-F-B and with the mixed answers of §7.4. **Not approved** | **not an LR-4 exception** (below). **Not BC-3**: under B2-F-B there is no static root image in those paths for a dynamic child to hang from (COR-16). It does not decide whether either act belongs in the set (PD-2b) |

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

### 10.1 The canonical table, per alternative

Categories G, D and W are those of §2.2. "LR exception" names an exception to an LR
criterion; EX-3 is listed as a boundary exception and is marked as such.

| Alternative | LR exceptions | §0.2 items | G: governance prerequisite before WP-2 | D: separate design prerequisite before WP-2 | W: work allocated to WP-2 … WP-7 after the gate | Downstream WP effect |
|---|---|---|---|---|---|---|
| **B2-S** | **none claimable.** A procedure that begins at `sudo` fails LR-2, and no exception is proposed to cover it | no exception to close. **B2-N may itself be a §0.2 matter** | WP-1 accepted; PD-2a (B2-S) recorded | **B2-N**, a loader-free privileged-start design that is not `sudo` (outside R8's WP list) | after B2-N: RT-5 and the acts PD-2b puts in the set begin at B2-N's start path | WP-2 stays blocked (the gate) until B2-N makes the boundary attainable, or Peter withdraws the affected design. WP-3 … WP-7 are separately gated in any case |
| **B2-F-A** | **EX-1** (`sudo`, **LR-2 only**) | **yes**, steps 1–5, for EX-1 | WP-1 accepted; PD-2a (B2-F) and PD-2b (both acts in) recorded; **§0.2 closed for EX-1** | **none.** FR-1 is a documentation amendment, not a design package (§10.2) | the `start` and `stop` roles: WP-2 inventory, WP-3 DI-2 and a stop call, WP-4 two more images, WP-5 D9 / PO-17 per image, WP-6 mapping, WP-7 estimate | WP-2 adds `start` and `stop`; the image count grows by two; DI-2 is performed in-process, so LR-4 is met for it |
| **B2-F-B** | **EX-1** (LR-2 only) **and EX-3** (boundary exception for both left-out acts). **No LR-4 exception** | **yes**, for EX-1 and EX-3. The impact assessment states EX-3 exactly and asks whether BC-4 as worded covers it | as B2-F-A, with PD-2b (both acts out); **§0.2 closed for EX-1 and EX-3** | none | RT-1 … RT-5 only | WP-2 … WP-7 omit the `start` and `stop` roles. No procedure in the set delegates DI-2, so LR-4 does not reach it; it remains the distribution `systemd-run`'s, outside the boundary |
| **mixed BQ-2**: `AP-2` in, OS-6 `stop` out | **EX-1** and **EX-3** (the `stop` act). No LR-4 exception | **yes**, for EX-1 and EX-3 | as B2-F-B with PD-2b (in / out); §0.2 closed for both | none | RT-1 … RT-5 plus the `start` role | DI-2 is bound by LR-4 and performed in-process; the stop remains a distribution `systemctl`, outside the boundary |
| **mixed BQ-2**: `AP-2` out, OS-6 `stop` in | **EX-1** and **EX-3** (the `start` act). No LR-4 exception | **yes**, for EX-1 and EX-3 | as B2-F-B with PD-2b (out / in); §0.2 closed for both | none | RT-1 … RT-5 plus the `stop` role | LR-4 does not reach DI-2; the stop function is a design addition (Q-5) |
| **B3-OUT** | **EX-2** (installer class, LR-1 and LR-2), HB-1 residual. Independent of the BQ-2 answer | **yes**, for EX-2 | PD-3 recorded; **§0.2 closed for EX-2** | none; FR-5 text change (A7 / A-II-03) | the installer is omitted from WP-2 … WP-7 | the estimate excludes the largest single item |
| **B3-IN** | **none** for the installer itself (EX-1 still applies to its `sudo` under B2-F; under B2-S it needs B2-N) | none for the installer; EX-1 only if B2-F | PD-3 recorded (and EX-1's §0.2 closure if B2-F) | **a Python-free installer with a loader-free verified-exec equivalent**, separately authorized and reviewed (R8 §9.6.1 "a new WP"; not in R8 §9.5) | the installer's operations (PF, PT, journals, RB-1, RS-1 and `H-1R`, as PD-3 sets) enter WP-2; one more large image in WP-4; WP-5 … WP-7 scale; WP-7 states the delta as a separate line | WP-2 stays blocked until the installer design exists |
| **BC-2** | not an LR exception | **yes**, if a maintainer reads R3-ROOT as a narrowing, before any WP-9 selection of LIT-FULL | PD-1 (not a WP-2 gate) | none | none | none for WP-2 … WP-7 |
| **BC-3** | not requested; BQ-4 forbids it | would enter §0.2 | — | — | — | — |

**Combinations.** A BQ-2 answer and a BQ-3 answer combine by taking the union of
their LR exceptions, §0.2 items and prerequisites. Any combination that contains
EX-1, EX-2 or EX-3 needs complete §0.2 closure before WP-2 may be prompted,
authorized or rely on that boundary, and a Peter decision is not by itself §0.2
approval. The eight combinations are enumerated in §2.2.

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

| Input | Depends on | B2-F-A | B2-F-B | B2-S | B3-OUT | B3-IN |
|---|---|---|---|---|---|---|
| WP-2 covers RT-5 (`attest`) from its first image | BQ-2 | yes | yes | **no: B2-N first** | | |
| WP-2 covers the `start` act (SA-1) | PD-2b | yes | **no** | **no** | | |
| WP-2 covers the `stop` act (SA-2) | PD-2b | yes | **no** | **no** | | |
| `sudo` is outside every inventoried tree | BQ-2 | yes | yes (and the clients) | **no** | | |
| WP-2 covers installer operations (PF, PT, journals, RB-1, RS-1) | BQ-3 | | | | **no** | yes |
| the exceptions EX-1 / EX-2 / EX-3 exist as a boundary | BQ-2 / BQ-3 **and §0.2 closed** | proposed, not approved, until §0.2 closes | | | | |

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
| **Q-2** | Is the list of `sudo`-started acts complete; is `H-1R` in the class; did R8 consider SA-2? | **Resolved by the record, with two classifications left to Peter.** Complete as far as the accepted record goes (§1.2, 24 `sudo -n` lines in D and 9 in R8, no further literal). SA-2 is an accepted act that R8 names (§8.2, Appendix B) but does not classify; `H-1R` is in D and not in R8. Both classifications are **PD-2b** and **PD-3** |
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
| **PD-2a** | Where does a `sudo`-started root procedure begin? | B2-F (first design image; EX-1) · B2-S (at `sudo`; unattainable without B2-N) | WP-2 |
| **PD-2b** | Which `sudo`-started acts are root procedures: `AP-2`? the OS-6 `stop`? | in/out for each (§7.4's 2×2); each "out" adds an EX-3 part, each "in" adds a role | WP-2 |
| **PD-3** | Is the installer class (H-1, RB-1, RS-1, **H-1R**) among the root procedures? | B3-OUT (EX-2, HB-1) · B3-IN (a Python-free installer package) | WP-2 |

---

## 14. Remediation acceptance checklist

For independent Codex re-review and Peter's recorded decisions. Unticked: nothing
here is accepted. **R2C-1 … R2C-11** are the eleven checks of the R2 prompt;
**RC-2 … RC-17** carry the R1 checklist forward where it still applies.

- [ ] **R2C-1** All twelve required records reached EOF, with line count, byte count
  and SHA-256 recorded (§1.1, handback), and this prompt matched its authority pin
  before any edit (header).
- [ ] **R2C-2** WP1-R1R-1 through WP1-R1R-4 are each explicitly closed (§0.5).
- [ ] **R2C-3** EX-3 is not called an LR-4 exception when `AP-2` is outside the set
  (§10.0, §10.1, §2.2, §7.4, §9.3; COR-09, COR-16).
- [ ] **R2C-4** The decision matrix separates governance prerequisites, separate
  design prerequisites and WP-2 … WP-7 work, and does not call FR-1 a completed
  pre-WP-2 design package (§2.2, §10.1, §10.2).
- [ ] **R2C-5** The proposed BQ-3 sentence names `H-1R` without asserting an
  unestablished invocation, and the inference is stated outside the sentence (§9.2).
- [ ] **R2C-6** COR-01 … COR-16 are counted as **sixteen** everywhere (§0.1, §0.5,
  §6.2, §6.4, the handback and the four pointers), and the twelve required reads are
  not confused with them.
- [ ] **R2C-7** The exact successor gate appears in §2.4 and, word for word, in all
  four pointers, with "R1 remediation" changed to "R2 remediation" and nothing else.
- [ ] **R2C-8** BQ-2, BQ-3, EX-1, EX-2, EX-3, BC-4 and BC-2 remain undecided or
  unapproved (§0.3, §2.3, §10.0, §13.2).
- [ ] **R2C-9** Concrete Route 3 remains unestablished and no successor is authorized
  (§3, §12, §15).
- [ ] **R2C-10** The original WP-1 proposal and handback, the R1 proposal and
  handback, both independent reviews, the G-1 record, the authorities, the exact
  prompts and the accepted R8 and R2 records are unedited (handback, digests).
- [ ] **R2C-11** No prohibited operation occurred (handback).
- [ ] **RC-2** The successor gate is exact (§2): review and Peter's decisions always;
  §0.2 closed before WP-2 may be prompted, authorized or rely on the boundary, if an
  answer contains an LR exception; a decision is not §0.2 approval; the literal path
  stays blocked until a separately authorized, reviewed loader-free privileged-start
  design exists, or Peter withdraws the design; BC-2 remains unresolved.
- [ ] **RC-4** The decision/gate flow is shown in compact tables (§0.2, §2.2).
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
- [ ] **RC-10** Every LR exception, §0.2 change, design prerequisite and downstream WP
  dependency each alternative requires is stated, once, in the canonical table
  (§10.1).
- [ ] **RC-11** Q-1 … Q-6 (and Q-7) are resolved where the record permits and
  otherwise converted into exact Peter decisions (§13).
- [ ] **RC-13** The commissioned facts are preserved: BQ-1 = R3-ROOT, BQ-4 permits no
  dynamic child, concrete Route 3 is unestablished, WP-2 … WP-7 are separately gated
  (§3, §11).
- [ ] **RC-14** WP-2's inventory is **not** performed; only R8's DI map is used.
- [ ] **RC-16** Only the proposal, the handback and the four pointers changed.
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
not decide BQ-2 or BQ-3, approve or open any exception or §0.2 entry, resolve BC-2,
accept WP-1, or authorize WP-2 or any later package.
