# Handback — LIT-FULL WP-1 R2 remediation: `WP-1 R2 REMEDIATION RETURNED — DECISION AND §0.2 GATE PENDING`

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R2-20261008-11`

Date: 2026-10-08

Executor: Claude Code (Sonnet 5.5) on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-claude-prompt.md),
**10,678 bytes (203 lines), SHA-256
`bb88208f76a4d9dcfd7f76cb0678c3e44193a4b9e9a25af0a1b7fb450300256f`**, recomputed
with `wc -c` and `sha256sum` before any edit and equal to the pin in the
[R2 authority](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-authority.md)
(itself 2,378 bytes, SHA-256
`c73fa2a86bf662943f91408146009d945ab682da1b02ce56ceba00bb9f0e1a7a`).
**The prompt and the authority are consumed by this return.**

Deliverable: [`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-proposal.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-proposal.md),
**1,168 lines, 95,541 bytes, SHA-256
`8881f4ba5d96c9be4f1dfb6f79115a43154e633f384ac250e6401d9ae31bacce`.**

## 1. Terminal state

**`WP-1 R2 REMEDIATION RETURNED — DECISION AND §0.2 GATE PENDING`.** The audit
succeeded; no `HARD STOP` arose. All twelve required records existed, were readable,
and matched the identities their authorities name. **Nothing is accepted.** I decided
neither BQ-2 nor BQ-3, approved no exception (EX-1, EX-2, EX-3 or BC-4), opened and
executed no §0.2 change control, resolved no BC (BC-2 included), decided neither
whether `AP-2` or the OS-6 `stop` belongs in the set nor whether `H-1R` belongs in
the installer class, established no concrete Route 3 and authorized no successor.
WP-1 remains `changes requested`.

## 2. Complete-read evidence

Each of the **twelve** required records was read from the first byte to EOF, in
bounded, non-overlapping chunks. The tool caps one call at about 25,000 tokens. One
call (R8, a 380-line request starting at line 3471) was refused for exceeding it,
and was re-read as two smaller chunks (3471–3670 and 3671–3870), so no line was
skipped. Line counts, byte counts and SHA-256 digests are in proposal §1.1.
Summary:

| # | File | Lines | Bytes |
|---|---|---:|---:|
| 1 | `.agents/AGENTS.md` | 700 | 36,014 |
| 2 | `docs/implementation-plan.md` (pre-edit) | 2,603 | 128,268 |
| 3 | `docs/review/Handover information` (pre-edit) | 55 | 3,889 |
| 4 | `docs/operations/disposable-test-server.md` (pre-edit) | 183 | 9,018 |
| 5 | independent R1 re-review | 102 | 5,524 |
| 6 | R1 remediation proposal | 997 | 75,452 |
| 7 | R1 remediation handback | 155 | 9,283 |
| 8 | R1 remediation authority | 45 | 2,250 |
| 9 | R1 remediation prompt | 155 | 7,482 |
| 10 | G-1 decisions | 46 | 2,455 |
| 11 | accepted R8 proposal | 4,816 | 551,246 |
| 12 | accepted one-host design amendment | 7,307 | 525,019 |

Chunk boundaries used. Single call, first line to EOF: items 1, 3, 4, 5, 7, 8, 9
and 10. Plan: 1–650, 651–1250, 1251–1850, 1851–2450, 2451–2603. R1 proposal:
1–500, 501–997. R8: 1–550, 551–1100, 1101–1650, 1651–2170, 2171–2650, 2651–3070,
3071–3470, 3471–3670, 3671–3870, 3871–4170, 4171–4470, 4471–4650, 4651–4816. Design:
1–380, 381–760, 761–1140, 1141–1520, 1521–1900, 1901–2280, 2281–2660, 2661–3040,
3041–3420, 3421–3800, 3801–4180, 4181–4560, 4561–4920, 4921–5280, 5281–5620,
5621–5960, 5961–6300, 6301–6640, 6641–6980, 6981–7307.

Also read, because the exact prompt and the pointer edits required them: the R2
prompt (203 lines, once at the start) and the R2 authority (45 lines), to verify the
pin; and `docs/project-management/status.md` (56 lines, pre-edit SHA-256
`c164f8ced5bccb1465b2e16f7abf89b09ac778839c0949bc0fa7aa9f8cc22102`).

**Not re-read in this return.** The accepted OH-S2 R2 citation record and the R8
acceptance record were read completely by the R1 remediation but are not among the
twelve this prompt requires. They were not read again. Every `[R2 §n]` citation is
carried (proposal §1.1).

## 3. Files created or changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-proposal.md` | **created** |
| `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-handback.md` | **created** (this file) |
| `docs/review/Handover information` | pointer rewritten (heading, state, gate, links) |
| `docs/project-management/status.md` | pointer rewritten |
| `docs/implementation-plan.md` | **§20 only** |
| `docs/operations/disposable-test-server.md` | **restriction banner only** |

Nothing else was edited. The 32 status entries present at session start were left as
they were, apart from the four pointers (which were already modified at start by the
R2 authorization) and the two new untracked deliverables: `git status --short` lists
34 entries after the return.

**Superseded pointer text.** The R2-authorization wording that the four pointers
carried at the start was overwritten. The prompt permits only the four pointer edits
and forbids edits to archive indexes, so no archive snapshot was created. Verbatim
pre-edit copies were saved outside the repository, in the session scratchpad, and
their SHA-256 digests are: Handover `8dcb38224c41…562d7`, `status.md`
`c164f8ced5bc…22102`, `implementation-plan.md` `c3587ee54edc…6cbd9`,
`disposable-test-server.md` `a72a3e4a89d1…6a8ad`. The authorization content they held
is preserved in the R2 authority and exact prompt, which are unedited.

## 4. The precise correction for each review finding

| Finding | The correction | Where |
|---|---|---|
| **WP1-R1R-1** (Blocking) | R1 §10.1 said B2-F-B carries EX-3 for "LR-2 and, for DI-2, LR-4". Corrected: **EX-3 is not an LR-4 exception.** LR-4 binds a root procedure in the final set and reaches DI-2 only if `AP-2` is in the set (COR-09). Under B2-F-B, `AP-2` and/or the OS-6 `stop` are outside the set, so their exclusion is not a free-standing LR-4 exception. EX-3 is the proposed wider BC-4 boundary exception for whichever whole `sudo`-started acts Peter leaves outside the set; not BC-3; BC-4 not silently expanded; neither act's membership decided; every exception-bearing choice still needs complete §0.2 closure before WP-2 may be prompted, authorized or rely on the boundary. One canonical table states every LR exception, §0.2 item, prerequisite, design prerequisite and downstream WP effect for B2-S, B2-F-A, B2-F-B, the two mixed answers, B3-OUT and B3-IN | proposal §10.0, §10.1; agreeing edits in §2.2, §7.4 (bullet and 2×2), §9.3 |
| **WP1-R1R-2** (Important) | The ambiguous §2.2 column and rows are replaced. Three categories are kept apart: **G** governance prerequisite before WP-2 (WP-1 acceptance, Peter's BQ-2 and BQ-3 decisions, complete §0.2 closure for any selected exception-bearing answer); **D** separate design prerequisite before WP-2 (B2-N for B2-S; the Python-free installer / loader-free verified-exec design for B3-IN); **W** work allocated to WP-2 … WP-7 after the gate. FR-1 is no longer called a pre-WP-2 design package: it is a documentation amendment that records the selected boundary and adds the `start` and `stop` roles to the commissioned work, and each design activity is assigned to WP-2 (inventory), WP-3 (interfaces), WP-4 (images), WP-5 (proof method), WP-6 (mapping) or WP-7 (estimate). B2-F-A has no category D item | proposal §2.2, §10.1, §10.2 |
| **WP1-R1R-3** (Important) | The proposed BQ-3 sentence names `H-1R` expressly and classifies it only as the accepted record supports: a separately authorized root re-record operation, read-only plus a record write, implemented as a subcommand of the one installer tool. It asserts no invocation literal and says a later separately authorized record may state one. The inference that it runs through the verified-exec stub is stated **outside** the sentence, labelled an inference. `H-1R` stays in PD-3. No new invocation design was made | proposal §9.2 (and §5.3 IC-4 note, §5.4) |
| **WP1-R1R-4** (Optional) | The count is **sixteen** for COR-01 … COR-16 throughout. The twelve required reads are distinguished from the sixteen corrections in the one-page outcome, §6.2 and the checklist | proposal §0.1, §0.5, §6.2, §6.4, §14 |

## 5. Checks performed and exact results

| Check | Exact result |
|---|---|
| prompt identity: `wc -c`, `sha256sum` against the R2 authority pin | 10,678 bytes; digest equal; performed before any edit |
| digests of the twelve required records, taken after the reads and before any edit | recorded in proposal §1.1. The original WP-1 proposal (`4c4535b8…4775`), the original WP-1 handback (`e2ffd79f…ad76`), the R1 proposal, handback, authority and prompt, both independent reviews, the G-1 record, R8 and the design were re-hashed at the end of the run and **are unchanged** (see the last row) |
| fixed-string counts after the reads (proposal §1.2): `H-1R`, `sudo -n`, `OS-6`, `AP-2`, `iii-a` in R8 and in the design | `H-1R`: R8 0 lines; design 10 lines (11 occurrences), none a literal. `sudo -n`: R8 8 lines (11), design 24 lines (29). `OS-6` in R8 2 lines; `AP-2` 9; `iii-a` 6. Two R1 line counts (9 for `sudo -n` in R8, 16 for `H-1R` in the design) do not reproduce by this method; the conclusions are unaffected and no correction is claimed |
| the exact successor gate: the prompt's quoted paragraph compared, whitespace-normalized, with proposal §2.4 and each of the four pointers | **present exactly once in each of the five**, differing from R1 only by "R1 remediation" → "R2 remediation" |
| stale references to the count of corrections: the spelled-out form of the number 14, searched case-insensitively over the proposal, this handback and the four pointers | **0 matches** in the proposal and in the four pointers; this handback is covered by the post-write run in §9. The only figure other than sixteen is the numeral quoted from R1 in proposal §0.5 (the defect column) and §6.4 COR-01 (a count of R1's required records, not of corrections) |
| proposal structure (scratch Python): fences, table cell counts, trailing whitespace | 0 fences (none used); 29 tables, 0 inconsistent rows; 0 lines with trailing whitespace |
| local link targets of the proposal | all exist, except this handback, which did not yet exist when first checked; rechecked in §9 |
| integrity of the pointers outside the edited regions | `docs/implementation-plan.md`: the text before `## 20.` is byte-identical to the pre-edit file; `docs/operations/disposable-test-server.md`: the text before the banner and from "Agents that support skills" onward is byte-identical to the pre-edit file |
| anything run that is not a read or a write of a permitted file | **nothing.** Commands: `wc`, `sha256sum`, `grep`, `sed`, `git status`, `git diff --no-index --stat`, `cp` of the R1 proposal to the new deliverable path and of the four pointers to the scratchpad, and scratch Python reading and writing the permitted files |

## 6. Changes from the R1 remediation

The R2 proposal is the R1 proposal with these changes, and nothing else: the header
and status block (R2 identity, prompt pin, links to both reviews); §0 rewritten (one
page, flow, decision summary, scope, and the new **§0.5** closure table); §1.1
(twelve records, new digests, the carried-citations statement) and §1.2 (the repeated
fixed-string checks, with the note on R1's two counts) and a naming note in §1.3; the
§2.1 R2-authority bullet and the §2.4 gate (R1 → R2); the repaired **§2.2** matrix;
the §5.3 note and §5.4 `H-1R` row; the §6.2 count bullet; the COR-01 "new" cell (a
count of R1's records, not of corrections); the §7.4 B2-F-B bullet and 2×2; the §9.2
sentence and the new "outside the sentence" paragraph; the §9.3 B2-F-B row; the new
**§10.0** and the rewritten **§10.1** and **§10.2**; and the rewritten §14 checklist.
**No boundary member, no recommendation direction, no COR-01 … COR-16 meaning and no
Peter decision changed.**

## 7. Unresolved Peter decisions and governance gates

* **PD-1** BC-2 reading (before any WP-9 selection of LIT-FULL; not a WP-2 gate).
* **PD-2a** where a `sudo`-started root procedure begins; **PD-2b** whether `AP-2`
  and the OS-6 `stop` are root procedures.
* **PD-3** whether the installer class, `H-1R` included, is a root procedure.
* **Gates:** independent Codex re-review of this R2 remediation; the BQ-2 and BQ-3
  records; **complete §0.2 change control, closed before WP-2 may be prompted,
  authorized or rely on the boundary, if a chosen answer contains an LR exception**
  (EX-1, EX-2 or EX-3); or, for literal LIT-FULL, a separately authorized, reviewed
  loader-free privileged-start design, or withdrawal; and, for a B3-IN path, the
  separately authorized Python-free installer design.
* **Not decided here:** BQ-2, BQ-3, EX-1, EX-2, EX-3, BC-4, BC-2, whether `AP-2` or
  the OS-6 `stop` belongs in the set, whether `H-1R` belongs in the installer class.
  Concrete Route 3 remains unestablished; WP-2 is not authorized.

## 8. Checks not run

No host check of any kind, no test, formatter, linter, type checker or build, no
Markdown linter (none is configured; the scratch structure check is the substitute),
no package or network operation. No suite figure is claimed.

## 9. Post-write verification

Run after this handback was written, with scratch Python reading the files:

| Check | Exact result |
|---|---|
| the proposal's line count, byte count and SHA-256 | 1,168 lines, 95,541 bytes, `8881f4ba…bacce`, equal to the header of this file |
| the spelled-out form of 14, case-insensitive, over the proposal, this handback and the four pointers | 0 matches in all six |
| local link targets of the proposal, this handback and the four pointers | all resolve; none missing |
| the gate paragraph in the proposal §2.4 and the four pointers | present in all five |
| the four pointers say changes-requested / not accepted, BQ-2 and BQ-3 undecided, concrete Route 3 unestablished and WP-2 not authorized | yes, all four |
| unchanged files: SHA-256 of the original WP-1 proposal and handback, the R1 proposal, handback, authority and prompt, both independent reviews, the G-1 record, the R2 authority and prompt, R8 and the design | equal to the values recorded before the run. For the independent review of the original return, which this run did not pin, the value is the one the R1 proposal recorded (2,750 bytes, `ae45d78c…ff6f`), and it is unchanged |
| `git status --short` before versus after | the only difference is the two new untracked deliverables; the four pointers were already modified at session start |
| trailing whitespace in the Handover, `status.md` and this handback | none |

## 10. Statement on prohibited operations

**No prohibited operation occurred.** I used no SSH and made no connection to any
host; did not access retained evidence, secrets, credentials, player data,
production, staging, `oracle-test`, Foundry or a database; did no network research;
ran no package operation, installation, implementation, configuration or
infrastructure edit, launcher work, build, test, formatter, service or database
operation, cleanup or workspace recreation; did no OH-S4/OH-S4p or later work, no
H-1/H-2, activation or rollback; opened and executed no §0.2 change control; made no
Product Owner decision; and made no commit and no push. I edited no accepted
record, review, authority, exact prompt, register, archive index or historical
snapshot, and neither earlier WP-1 deliverable nor either R1 deliverable.
