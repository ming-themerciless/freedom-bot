# Handback — LIT-FULL WP-1 R3 remediation: `WP-1 R3 REMEDIATION RETURNED — DECISION AND §0.2 GATE PENDING`

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R3-20261008-12`

Date: 2026-10-08

Executor: Claude Code (Sonnet 5.5) on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-claude-prompt.md),
**11,277 bytes (222 lines), SHA-256
`73238176135e73f71fc3cfe8049d15e6af6234d6b125c7ab61ff5f17558da03b`**, recomputed
with `wc -c` and `sha256sum` before any edit and equal to the pin in the
[R3 authority](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-authority.md)
(itself 2,386 bytes, SHA-256
`29b492720fca0aa5ea4be564fd673232bcdbca77714a3000dd51115c541cda7a`).
**The prompt and the authority are consumed by this return.**

Deliverable: [`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-proposal.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-proposal.md),
**1,339 lines, 111,399 bytes, SHA-256
`07f2d4851c3b339f90ba3ceda66c98af349d34ddd75e2886d295de053306c84d`.**

## 1. Terminal state

**`WP-1 R3 REMEDIATION RETURNED — DECISION AND §0.2 GATE PENDING`.** The audit
succeeded; no `HARD STOP` arose. All thirteen required records existed, were
readable, and matched the identities their authorities name, and the prompt matched
its authority pin before any edit. **Nothing is accepted.** I decided neither BQ-2
nor BQ-3, nor PD-2a, PD-2b or PD-3; approved no exception (EX-1, EX-2, EX-3 or
BC-4); opened and executed no §0.2 change control; resolved no BC (BC-2 included);
decided neither whether `AP-2` or the OS-6 `stop` belongs in the set nor whether
`H-1R` belongs in the installer class; designed neither B2-N nor the installer;
established no concrete Route 3; and authorized no successor. WP-1 remains
`changes requested`.

## 2. Complete-read evidence

Each of the **thirteen** required records was read from the first byte to EOF, in
bounded, non-overlapping chunks. The tool caps one call at about 25,000 tokens. Two
R8 calls (3391–3840 and 3391–3620) were refused for exceeding it, and that span was
re-read as 3391–3510, 3511–3620 and 3621–3840, so no line was skipped. Line counts,
byte counts and SHA-256 digests are in proposal §1.1. Summary:

| # | File | Lines | Bytes |
|---|---|---:|---:|
| 1 | `.agents/AGENTS.md` | 700 | 36,014 |
| 2 | `docs/implementation-plan.md` (pre-edit) | 2,615 | 129,260 |
| 3 | `docs/review/Handover information` (pre-edit) | 54 | 3,698 |
| 4 | `docs/operations/disposable-test-server.md` (pre-edit) | 190 | 9,802 |
| 5 | independent R2 re-review | 81 | 4,278 |
| 6 | R2 remediation proposal | 1,168 | 95,541 |
| 7 | R2 remediation handback | 187 | 15,724 |
| 8 | R2 remediation authority | 45 | 2,378 |
| 9 | R2 remediation prompt | 203 | 10,678 |
| 10 | independent R1 re-review | 102 | 5,524 |
| 11 | G-1 decisions | 46 | 2,455 |
| 12 | accepted R8 proposal | 4,816 | 551,246 |
| 13 | accepted one-host design amendment | 7,307 | 525,019 |

Chunk boundaries used. Single call, first line to EOF: items 1, 3, 4, 5, 7, 8, 9, 10
and 11. Plan: 1–650, 651–1250, 1251–1850, 1851–2450, 2451–2615. R2 proposal: 1–600,
601–1168. R8: 1–500, 501–1000, 1001–1500, 1501–1980, 1981–2460, 2461–2940, 2941–3390,
3391–3510, 3511–3620, 3621–3840, 3841–4290, 4291–4550, 4551–4816. Design: 1–380,
381–760, 761–1140, 1141–1520, 1521–1900, 1901–2280, 2281–2660, 2661–3040, 3041–3420,
3421–3800, 3801–4180, 4181–4560, 4561–4920, 4921–5280, 5281–5620, 5621–5960,
5961–6300, 6301–6640, 6641–6980, 6981–7307.

Also read: the R3 prompt (222 lines, once at the start) and the R3 authority
(45 lines), to verify the pin; and `docs/project-management/status.md` (66 lines,
pre-edit SHA-256 `25cf5bc954d62c8477d536bf9f4800b472ced9c2e41e8983dc0af6c4fa0b488b`), because it is a pointer this return edits.

**Not re-read in this return.** The R1 remediation proposal, handback, authority and
prompt (read completely by the R2 remediation, not among the thirteen), the original
WP-1 proposal and handback, the accepted OH-S2 R2 citation record and the R8
acceptance record. Every `[R2 §n]` citation is carried, not re-verified (proposal
§1.1).

## 3. Files created or changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-proposal.md` | **created** |
| `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-handback.md` | **created** (this file) |
| `docs/review/Handover information` | pointer rewritten (heading, return paragraph, writes sentence, links) |
| `docs/project-management/status.md` | pointer rewritten |
| `docs/implementation-plan.md` | **§20 only** |
| `docs/operations/disposable-test-server.md` | **restriction banner only** |

Nothing else was edited. The four pointers were already modified at session start by
the R3 authorization; the 37 status entries present at session start are otherwise
unchanged, and the two new deliverables are the only additions (`git status --short`
lists 39 entries after the return).

**Superseded pointer text.** The R3-authorization wording that the four pointers
carried at the start was overwritten. The prompt permits only the four pointer edits
and forbids edits to archive indexes, so no archive snapshot was created. Verbatim
pre-edit copies were saved outside the repository, in the session scratchpad; their
SHA-256 digests are: Handover `69f5c8cc8e09…10e9cb`, `status.md` `25cf5bc954d6…0b488b`,
`implementation-plan.md` `7e0486d0c1eb…3883bc`, `disposable-test-server.md`
`bd15b1637606…a2ce4c`. The authorization content they held is preserved in the R3
authority and exact prompt, which are unedited.

## 4. The precise correction for each review finding

| Finding | The correction | Where |
|---|---|---|
| **WP1-R2R-1** (Blocking) | R2 rows 5 and 6 (B2-S) omitted PD-2b although their work column depended on it, so a B2-S combination that left `AP-2` or the OS-6 `stop` outside the set carried no EX-3 and no §0.2 item; R2 §10.1 recorded only PD-2a for B2-S; R2 §12.2 hard-coded both acts absent under B2-S; the R2 gate said "LR exception", which cannot reach EX-3. **Corrected:** PD-2a (where a `sudo`-started procedure begins), PD-2b (per act, whether it is in the set, under **both** PD-2a answers) and PD-3 (B3-OUT or B3-IN) are three independent dimensions, all required before WP-2. B2-S decides no membership question. Each act PD-2b leaves out carries EX-3 and a complete §0.2 item; each act it puts in keeps its `start` or `stop` role in WP-2 … WP-7 after B2-N; B3-OUT adds EX-2; B3-IN adds the installer design; B2-N erases neither EX-2 nor EX-3. One canonical matrix: three orthogonal tables (A: PD-2a, B: PD-2b, C: PD-3), a union rule U1 … U7, and sixteen worked rows, F-1 … F-8 and S-1 … S-8. The gate paragraph is carried word for word and covers EX-3 expressly | proposal §0.1, §0.2, §0.6, §2.2, §2.4, §7.3, §7.4 (with a B2-S 2×2), §9.3, §10.0, §10.1, §12.2, §13.2, §14 |
| **WP1-R2R-2** (Optional) | R2 §13.1 Q-2 said nine `sudo -n` lines in R8. **Corrected** to **eight** lines (eleven occurrences), the reproduced count. The proposal and this handback were searched for any other place that presents nine as the reproduced R8 line count: none. §1.2 still quotes nine, as R1's non-reproducing figure, and keeps the distinction between eight lines and eleven occurrences. No conclusion changes | proposal §13.1 Q-2, §1.2 |

## 5. Checks performed and exact results

| Check | Exact result |
|---|---|
| prompt identity: `wc -c`, `sha256sum` against the R3 authority pin | 11,277 bytes; digest equal; performed before any edit |
| digests of the thirteen required records, taken after the reads and before any edit | recorded in proposal §1.1. The R2 proposal (`8881f4ba…bacce`, 95,541 bytes, 1,168 lines) and the R2 prompt (`bb88208f…256f`) equal the pins recorded by the independent R2 re-review and the R2 authority |
| fixed-string counts (proposal §1.2), repeated for R3 | `sudo -n`: **R8 8 lines, 11 occurrences**; design 24 lines, 29 occurrences. `H-1R`: R8 0 lines; design 10 lines, 11 occurrences. `OS-6`, `AP-2`, `iii-a` in R8: 2, 9 and 6 lines. Identical to R2's results |
| the exact successor gate: the prompt's quoted paragraph compared, whitespace-normalized, with proposal §2.4 and each of the four pointers | **present exactly once in each of the five** (proposal, Handover, `status.md`, §20, banner) |
| the gate no longer reads "LR exception" | the gate paragraph says "an exception, including EX-1, EX-2 or EX-3 under BC-4". The words "LR exception" occur in the proposal at 5 lines: the two historical closure rows (§0.5 WP1-R1R-1 and §0.6 WP1-R2R-1, quoting the earlier defects), the §2.2 sentence explaining why the gate does not say it, and the heading and BC-2 row of §10.1's Other-alternatives table |
| stale count: nine presented as the reproduced R8 line count, searched (`grep -n -i -E '\bnine\b|\b9 (lines|in R8)'`) in the proposal and in this handback | **0** such places. In the proposal nine appears in §0.1 and §0.6 as the finding's own description, in §1.2 as R1's non-reproducing figure and in the §14 checklist as R1's figure; the two further hits (an `AP-2` line count of 9 in §1.2's table, and `9` in `2, 9 and 6 lines`) are unrelated counts. In this handback it appears only in the §4 finding row and in this row |
| matrix consistency (scratch Python): the 16 worked rows parsed and recomputed from U1, U3, U4 and U5 | **all 16 rows equal what the union rule derives** (exceptions in G, B2-N and installer design in D, RT/start/stop/I in W, the three recorded decisions in every G cell) |
| coverage of the dimensions | 16 rows = 2 PD-2a × 4 PD-2b × 2 PD-3. Every B2-S row (S-1 … S-8) names both acts' membership. The only row with no exception is S-2 |
| proposal structure (scratch Python): fences, table cell counts, trailing whitespace | 0 fences (none used); 35 tables, 0 inconsistent rows; 0 lines with trailing whitespace |
| local link targets of the proposal | all exist except this handback, which did not yet exist when first checked; rechecked in §9 |
| integrity of the pointers outside the edited regions | `docs/implementation-plan.md`: the text before `## 20.` is byte-identical to the pre-edit file; `docs/operations/disposable-test-server.md`: the text from "Agents that support skills" onward is byte-identical to the pre-edit file |
| anything run that is not a read or a write of a permitted file | **nothing.** Commands: `wc`, `sha256sum`, `grep`, `diff`, `git status`, `cp` of the R2 proposal to the new deliverable path and of the four pointers to the scratchpad, and scratch Python reading and writing the permitted files |

## 6. Changes from the R2 remediation

The R3 proposal is the R2 proposal with these changes, and nothing else: the title,
header and status block (R3 identity, prompt and authority pins, links to the R2
re-review); §0.1 … §0.4 rewritten and a new **§0.6**; §1.1 (thirteen records, new
digests, the carried-citations statement) and a re-run note in §1.2; the R3 Auth and
R2-re-review bullets in §2.1; §2.2 rewritten (categories, the three dimensions and a
pointer to §10.1); the §2.4 gate (R2 → R3 remediation; "an exception, including EX-1,
EX-2 or EX-3 under BC-4"); the §6.2 and COR-01 counts of reads; the PD-2b sentence in
§7.3; the B2-S additions and 2×2 in §7.4; the B2-S and mixed rows of §9.3; the EX-3 row
of §10.0; the rewritten **§10.1** and **§12.2**; Q-2 in §13.1; the PD-2a, PD-2b and PD-3
rows and a sentence in §13.2; the rewritten §14 checklist; and one clause in §15. **No
boundary member, no recommendation direction, no COR-01 … COR-16 meaning and no Peter
decision changed.**

## 7. Unresolved Peter decisions and governance gates

* **PD-1** BC-2 reading (before any WP-9 selection of LIT-FULL; not a WP-2 gate).
* **PD-2a** where a `sudo`-started root procedure begins; **PD-2b** whether `AP-2` and
  the OS-6 `stop` are root procedures (each separately, under both PD-2a answers);
  **PD-3** whether the installer class, `H-1R` included, is a root procedure. All three
  are required, recorded, before WP-2 in every combination.
* **Gates:** independent Codex re-review of this R3 remediation; the BQ-2 and BQ-3
  records; **complete §0.2 change control, closed before WP-2 may be prompted,
  authorized or rely on the boundary, if a chosen answer contains an exception** (EX-1,
  EX-2 or EX-3); or, for literal LIT-FULL (matrix row S-2), a separately authorized,
  reviewed loader-free privileged-start design, or withdrawal; and, for a B3-IN path,
  the separately authorized Python-free installer design.
* **Not decided here:** BQ-2, BQ-3, PD-2a, PD-2b, PD-3, EX-1, EX-2, EX-3, BC-4, BC-2,
  whether `AP-2` or the OS-6 `stop` belongs in the set, whether `H-1R` belongs in the
  installer class. Concrete Route 3 remains unestablished; WP-2 is not authorized.

## 8. Checks not run

No host check of any kind, no test, formatter, linter, type checker or build, no
Markdown linter (none is configured; the scratch structure check is the substitute),
no package or network operation. No suite figure is claimed.

## 9. Post-write verification

Run after this handback was written, with scratch Python and `grep` reading the files:

| Check | Exact result |
|---|---|
| the proposal's line count, byte count and SHA-256 | 1,339 lines, 111,399 bytes, `07f2d485…6c84d`, equal to the header of this file |
| "fourteen" or "14" searched, case-insensitive, over the proposal, this handback and the four pointers | 2 hits, neither a count of corrections: COR-01's "all 14 records" is the number of records in R1's own prompt list (carried from R2), and §14's "fourteen checks of the R3 prompt" counts R3C-1 … R3C-14. **0** references to fourteen corrections |
| local link targets of the proposal and this handback | all resolve; none missing |
| the gate paragraph, whitespace-normalized, in the proposal §2.4 and the four pointers | present exactly once in each of the five |
| the four pointers say WP-1 remains changes-requested / not accepted, BQ-2 and BQ-3 undecided, concrete Route 3 unestablished, WP-2 not authorized, retain the no-host and retained-evidence restriction, and link the R3 proposal, handback, authority, exact prompt and the independent R2 re-review | yes, all four |
| confinement: `docs/implementation-plan.md` before `## 20.`; `docs/operations/disposable-test-server.md` from "Agents that support skills" | both byte-identical to the pre-edit copies |
| unchanged files: SHA-256 of the original WP-1 proposal, the R1 proposal, the R2 proposal and handback, the R2 and R3 authorities, the R2 and R3 exact prompts, both independent reviews pinned earlier, the G-1 record, R8 and the design | equal to the values recorded before the run. For the independent R2 re-review, the value was not pinned by an authority and its bytes were read once unchanged (81 lines, 4,278 bytes) |
| `git status --short` before versus after | 37 entries before; 39 after. The only differences are the two new untracked deliverables; the four pointers were already modified at session start |
| trailing whitespace in the Handover, `status.md`, the banner, §20 and this handback | none |
| matrix consistency (§5) re-run on the final proposal | all 16 worked rows equal what the union rule derives |
| commits and pushes | none; HEAD is unchanged (`9ac7ca4`) |

## 10. Statement on prohibited operations

**No prohibited operation occurred.** I used no SSH and made no connection to any
host; did not access retained evidence, secrets, credentials, player data,
production, staging, `oracle-test`, Foundry or a database; did no network research;
ran no package operation, installation, implementation, configuration or
infrastructure edit, launcher work, build, test, formatter, service or database
operation, cleanup or workspace recreation; did no OH-S4/OH-S4p or later work, no
H-1/H-2, activation or rollback; opened and executed no §0.2 change control; made no
Product Owner decision; and made no commit and no push. I edited no accepted record,
review, authority, exact prompt, register, archive index or historical snapshot, and
neither earlier WP-1 deliverable, nor either R1 deliverable, nor either R2 deliverable.
