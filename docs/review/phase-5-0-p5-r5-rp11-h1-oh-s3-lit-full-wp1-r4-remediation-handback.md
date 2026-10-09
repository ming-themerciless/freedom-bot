# Handback — LIT-FULL WP-1 R4 remediation: `WP-1 R4 REMEDIATION RETURNED — DECISION AND §0.2 GATE PENDING`

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R4-20261008-13`

Date: 2026-10-08

Executor: Claude Code (Sonnet 5.5) on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-claude-prompt.md),
**12,936 bytes (245 lines), SHA-256
`218040bc5bc5ee34e27cb1e1eeaceb66443992f25ebb30629a2053ae7c473620`**, recomputed with `wc -c` and
`sha256sum` before any edit and equal to the pin in the
[R4 authority](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-authority.md)
(itself 2,647 bytes, 48 lines, SHA-256 `2a9a3a2ef0d59a366f3db2ff2fc50d57f15f0dae824d3e48a76ebd2f8aa6a267`)
and to the figures the active Handover recorded. **The prompt and the authority are consumed by this
return.**

Deliverables:

| Deliverable | Lines | Bytes | SHA-256 |
|---|---:|---:|---|
| [`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-proposal.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-proposal.md) | 1,542 | 133,795 | `00e15e5cb5e8575d829d7f1fd8ae93d273fd43f536f53308b5a07926c24d8737` |
| [`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-pointer-archive-erratum.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-pointer-archive-erratum.md) | 151 | 10,162 | `eca8aff5fd18b5f2eb3c58684345b5472cca34cff90d33faa74637af57d2df4e` |
| this handback | — | — | reported in the executor's final message, because a file cannot contain its own digest |

## 1. Terminal state

**`WP-1 R4 REMEDIATION RETURNED — DECISION AND §0.2 GATE PENDING`.** No `HARD STOP` arose. All thirteen
required records existed, were readable, and matched the identities their authorities name; the prompt
matched its authority pin before any edit. **Nothing is accepted.** I decided neither BQ-2 nor BQ-3, nor
PD-2a, PD-2b or PD-3; approved no exception (EX-1, EX-2, EX-3 or BC-4); opened and executed no §0.2
change control; resolved no BC (BC-2 included); decided neither whether `AP-2` or the OS-6 `stop`
belongs in the set nor whether `H-1R` belongs in the installer class; designed neither B2-N nor the
installer; established no concrete Route 3; and authorized no successor. WP-1 remains
`changes requested`.

## 2. Complete-read evidence

Each of the **thirteen** required records was read from the first byte to EOF, in bounded,
non-overlapping chunks (a chunk began at the line after the previous one, and the last chunk of every
file ended at the line count shown). No required read was truncated or skipped. The digests were taken
by `sha256sum` before any edit of this return.

| # | File | Lines | Bytes | SHA-256 |
|---|---|---:|---:|---|
| 1 | `.agents/AGENTS.md` | 700 | 36,014 | `87bab4ab8d67e308af0c59b99c8604235ee84d75cfa12448458b1a04cc88390a` |
| 2 | `docs/implementation-plan.md` (pre-edit) | 2,617 | 129,045 | `ca60068199d9fa5049adf0b43c54b66ba79bc3e9412e89fb836d80159fc6d111` |
| 3 | `docs/review/Handover information` (pre-edit) | 55 | 3,638 | `78dd71dcd8de8ee83cc656370a9dd24e115af9f50bc5289215340371ca6cd61f` |
| 4 | `docs/operations/disposable-test-server.md` (pre-edit) | 186 | 9,263 | `efc090d80fad494c570e0ac5ceea665dcaf65d55e0ff2fa97bf1519bb61354c8` |
| 5 | independent R3 re-review | 93 | 5,017 | `6f3017ed472eb03b4fcd9b728cdc567097b8e9ce0f24cba2ca20985b2d993c72` |
| 6 | R3 remediation proposal | 1,339 | 111,399 | `07f2d4851c3b339f90ba3ceda66c98af349d34ddd75e2886d295de053306c84d` |
| 7 | R3 remediation handback | 194 | 16,550 | `9d659ce2068174cae593fe279871edcbe911aca269684d655ade411eb101ca8a` |
| 8 | R3 remediation authority | 45 | 2,386 | `29b492720fca0aa5ea4be564fd673232bcdbca77714a3000dd51115c541cda7a` |
| 9 | R3 remediation prompt | 222 | 11,277 | `73238176135e73f71fc3cfe8049d15e6af6234d6b125c7ab61ff5f17558da03b` |
| 10 | independent R2 re-review | 81 | 4,278 | `836cd7b262431e9b876d6ac8c3537733918aae598d1f7feab94ca1f5b6e2443a` |
| 11 | G-1 decisions | 46 | 2,455 | `09234e4acada1b3487f9147f0c8c76110a90dc1dc491e6a02f68892c07bab00e` |
| 12 | accepted R8 proposal | 4,816 | 551,246 | `ab5db5010d9d1b2738b04f1ffbd62ab4414d901e9f7f79323ac49f811f660e04` |
| 13 | accepted one-host design amendment | 7,307 | 525,019 | `a752a4b8fe7eb1edf3e3a25decd3a7517ecccc85fedbb0b0b7e003cb7e615d02` |

Chunk boundaries:

| # | Chunks |
|---|---|
| 1 | single call, 1–700 |
| 2 | 1–650, 651–1250, 1251–1850, 1851–2617 |
| 3 | single call, 1–55 |
| 4 | single call, 1–186 |
| 5 | single call, 1–93 |
| 6 | 1–450, 451–900, 901–1340 |
| 7 | single call, 1–194 |
| 8 | single call, 1–45 |
| 9 | single call, 1–222 |
| 10 | single call, 1–81 |
| 11 | single call, 1–46 |
| 12 | 1–500, 501–1000, 1001–1480, 1481–1960, 1961–2440, 2441–2920, 2921–3390, 3391–3510, 3511–3620, 3621–3840, 3841–4070, 4071–4300, 4301–4560, 4561–4690, 4691–4816 |
| 13 | 1–600, 601–1200, 1201–1800, 1801–2400, 2401–3000, 3001–3600, 3601–4200, 4201–4800, 4801–5400, 5401–6000, 6001–6600, 6601–7307 |

Also read completely: the R4 prompt (245 lines, once at the start) and the R4 authority
(48 lines), to verify the pin; `docs/project-management/status.md` (71 lines, pre-edit
SHA-256 `9715da2e3cee8ca16bced25f7e56fa8e7178026a48c802c5e1c0cb728215172c`) and the four archive indexes, because this return edits them. The
pre-edit digests of items 2, 3 and 4 are the pre-edit values of pointers this return edits; they already
carried the R4 authorization when the run began.

**Not re-read in this return.** The R1 and R2 prompts, authorities and handbacks, the original WP-1
proposal and handback and the R8 acceptance record (carried from earlier readings; proposal §1.1).

## 3. Files created or changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-proposal.md` | **created** |
| `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-pointer-archive-erratum.md` | **created** |
| `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-handback.md` | **created** (this file) |
| `docs/review/Handover information` | pointer rewritten (R4 returned) |
| `docs/project-management/status.md` | pointer rewritten (R4 returned) |
| `docs/implementation-plan.md` | **§20 only**: from "Independent Codex re-review of the R3 remediation requests …" to the end |
| `docs/operations/disposable-test-server.md` | **restriction banner only**: from "**Active restriction, 2026-10-08 …**" up to "Agents that support skills …" |
| `docs/review/handover-archive/README.md` | one new table row (the erratum) |
| `docs/project-management/status-archive/README.md` | one new table row (the erratum) |
| `docs/implementation-plan-archive/README.md` | one new table row (the erratum) |
| `docs/operations/disposable-test-server-archive/README.md` | one new table row (the erratum) |

Nothing else was created, changed or deleted: a comparison of the SHA-256 of every file under `docs/` and
`.agents/` before and after (§5) shows exactly these 3 created and 8 changed files. The four
controller-created **R3-return snapshots**, every earlier proposal, handback, review, authority, exact
prompt, register and accepted record are byte-identical to their pre-run state. The eight "changed"
files were already modified in the working tree when the session began (they appear as modified in
`git status` at session start), so `git status --short` lists 3 more entries after the return and no fewer.

### The superseded R4-authorization pointer text (the gap the erratum describes, and what was done about it)

This return overwrote the **R4-authorization** wording that the four pointers carried at the start. The
R4 prompt permits only the four pointer edits and the four erratum index entries, so I created no archive
snapshot of that wording. The R3 handback kept the equivalent
text only in a session scratchpad, and WP1-R3R-3 found that insufficient. Here the verbatim pre-edit text
and its digests are instead **kept in this handback (Appendix A)**, so the repository holds the bytes and
a reader can verify them: each block's digest is given and recomputing it over the block equals it.
Appendix A is **not an archive snapshot and is not indexed**. The controller should decide whether to
create dated, indexed snapshots of it, as the forward control of the erratum (§7) requires; I did not,
because the prompt does not permit it (§7 below).

## 4. The precise correction for each finding

| Finding | The correction | Where |
|---|---|---|
| **WP1-R3R-1** (Blocking) | R3 Table A's B2-S row said that after B2-N each in-set act begins at B2-N's start path while `sudo` is inside the tree; R3 §12.2 answered "no" to whether `sudo` is outside an inventoried B2-S tree and then said the tree starts at B2-N. **Corrected** to one process-tree result: PD-2a = B2-S means the current `sudo`-started form begins at `sudo` and cannot meet LR-2; B2-N is the separate loader-free privileged-start design required to replace that start for every in-set act before WP-2 can rely on B2-S; after B2-N an in-set act's inventoried tree begins at B2-N's loader-free start path and contains no `sudo`; an act PD-2b classifies out is not started by B2-N, so its current `sudo` plus distribution-client path stays outside the boundary under EX-3 and needs complete §0.2 closure; B2-N changes how an in-set act starts, not whether it is in the set, and does not erase EX-2 or EX-3; B2-S decides no membership question and PD-2b remains required for both acts under both PD-2a answers. Table A's false statement is replaced; §12.2's "`sudo` outside every inventoried tree" row is answered per act with no yes/no contradiction (in-set B2-S act: `sudo` absent because B2-N replaces it; out act: the whole existing `sudo` path is outside the boundary under EX-3 and is not inventoried as a root procedure). A new process-tree rule PT-1 … PT-5 (§10.1) and a process-tree table (§7.4) state it once | proposal §0.1, §0.7, §2.2, §7.4, §9.3, §10.1 (Table A, rule PT), §12.2, §13.2 |
| **WP1-R3R-2** (Blocking) | R3 §0.2 step 5 read "steps 1–3 and 4 or 4′". **Corrected** to "only after steps 1–3 **and every applicable item among 4 and 4′**", with the meaning spelled out (every §0.2 closure step 4 requires and every design prerequisite step 4′ requires; both needed means both complete). **New §10.3** derives, from that rule, the step 4 and step 4′ prerequisites of all sixteen worked combinations and compares them with §10.1's G and D cells (§5 below). Every gate summary was rechecked against U6; U6 and the exact successor-gate paragraph are not weakened | proposal §0.1, §0.2, §0.7, §2.4, §10.3 |
| **WP1-R3R-3** (Important) | R3 kept its overwritten R3-authorization pointer text only in an external scratchpad. The repository holds no snapshot, and no committed revision, ref or stash matches the four pre-edit digests, so the bytes cannot be proved. **The erratum records the gap honestly:** the four digests exactly as the R3 handback §3 records them (abbreviated), which full values exist in the R3 proposal §1.1 and R3 handback §2, the search that found no match, the R3 authority, exact prompt, proposal and handback as the durable evidence of the substance, a statement that it recreates nothing and decides nothing, the R4 authority as its authority, and the forward control (current-state text snapshotted and indexed before replacement; a task prompt may not prohibit a governing §16.3 archival obligation without an approved governing-document change). One entry for it is added to each of the four archive indexes. No archived snapshot was modified | the erratum; the four index rows; proposal §0.7, §1.2 |

## 5. Checks performed and exact results

| Check | Exact result |
|---|---|
| prompt identity: `wc -c`, `sha256sum` against the R4 authority pin | 12,936 bytes, 245 lines; digest equal to `218040bc…3620`; performed before any edit |
| digests of the thirteen required records, taken after the reads and before any edit | recorded in §2 and proposal §1.1. The R3 proposal (`07f2d485…6c84d`, 111,399 bytes, 1,339 lines), the R3 handback (`9d659ce2…ca8a`) and the R3 prompt and authority equal the pins recorded by the R3 re-review, the R3 handback and the R3 authority |
| fixed-string counts, repeated for R4 (`grep -c -F` lines; `grep -o -F \| wc -l` occurrences) | `sudo -n`: R8 **8 lines, 11 occurrences**; design 24 lines, 29 occurrences. `H-1R`: R8 0 lines; design 10 lines, 11 occurrences. `OS-6`, `AP-2`, `iii-a` in R8: 2, 9 and 6 lines. Identical to R2's and R3's results |
| the exact successor gate: the R4 prompt's quoted paragraph extracted, whitespace-normalized and compared with the proposal §2.4 and each of the four pointers | **present exactly once in each of the five** (proposal, Handover, `status.md`, §20, banner); the prompt's own paragraph equals the normalized text used |
| **sixteen combinations against the compact gate** (scratch Python): the 16 worked rows of §10.1 parsed from the proposal; exceptions recomputed from the rule (EX-1 if B2-F; EX-3 per act left out; EX-2 if B3-OUT), design prerequisites recomputed (B2-N if B2-S; installer design if B3-IN), roles recomputed (`start` if `AP-2` in, `stop` if stop in, `I` if B3-IN), and the three recorded decisions and "WP-1 accepted" required in every G cell | **all 16 rows equal what the rule derives; 0 mismatches.** The §10.3 table (16 rows) was generated from the rule and re-parsed: **0 mismatches** against both the rule and the §10.1 G and D cells. Rows needing both step 4 and step 4′: F-2, F-4, F-6, F-8, S-1, S-3, S-4, S-5, S-6, S-7, S-8. Only S-2 has no step 4 item. Only F-1, F-3, F-5, F-7 have no step 4′ item |
| text checks on the proposal (`grep`) | "4 or 4′" and "steps 1–3 and 4": only the two quotations of the R3 defect (§0.1, §0.7). "`sudo` is inside the tree": only the two quotations of the R3 defect (§0.1, §0.7), the §3 general statement about where a procedure begins, §7.4's description of the *current* `sudo` form before B2-N, and PT-5's negation. "LR exception": only closure rows, §2.2's explanation and the §10.1 alternatives table. Nine as a reproduced R8 count: none (nine appears only as R1's figure). Fourteen as a correction count: none (COR-01 quotes R1's own "14 records"). "sixteen": 18 occurrences |
| proposal structure (scratch Python) | 0 code fences; 38 tables, 0 inconsistent rows; 0 lines with trailing whitespace |
| structure of the erratum and the four pointers | 0 lines with trailing whitespace in each; all local link targets resolve (the erratum, the proposal and the four archive indexes), the handback included once written |
| confinement of the §20 and banner edits | `docs/implementation-plan.md`: the text before "Independent Codex re-review of the R3 remediation requests …" (124,993 bytes) is byte-identical to the pre-edit file; `docs/operations/disposable-test-server.md`: the title and the text from "Agents that support skills …" onward are byte-identical to the pre-edit file |
| required pointer content (scratch Python, whitespace-normalized) | each of the four pointers contains: "changes requested", "not accepted", "BQ-2", "undecided", "unestablished", "not authorized", "Independent Codex re-review of the R4 remediation", the no-host and retained-evidence restriction, and links to the R4 proposal, handback, authority, exact prompt and independent R3 re-review. 0 missing |
| whole-tree integrity: SHA-256 of every file under `docs/` and `.agents/` before (871 files) and after, compared by path | **created:** the proposal and the erratum (the handback is created last). **deleted:** none. **changed:** exactly the 8 files of §3 (4 pointers, 4 indexes). Every other file, including the four R3-return snapshots, the R3 deliverables, all earlier prompts, authorities and reviews, is byte-identical |
| controller-created R3-return snapshots | the SHA-256 of each equals the value its archive index records: Handover `0ede35e5…256f`, status `e45b221d…ba07`, plan §20 `0c45cc6a…cf01`, banner `388b655f…ee9a` |
| search for the missing R3-authorization pointer bytes | none of the four digests (`69f5c8cc…10e9cb`, `25cf5bc9…0b488b`, `7e0486d0…3883bc`, `bd15b163…a2ce4c`) equals the SHA-256 of any file under `docs/` or `.agents/`, of any committed revision of the four pointer paths in any ref (`git rev-list --all`), or of the one stash entry |
| `git rev-parse HEAD` | `9ac7ca488105322483f4d5d5f1794e6e4c0bbe11`, unchanged. No commit, no push, no branch operation |
| anything run that is not a read of a repository file or a write of a permitted file | **nothing.** Commands: `wc`, `sha256sum`, `grep`, `diff`, `cp` of pre-edit pointers and of the R3 proposal to the session scratchpad, `git status`, `git rev-parse`, `git rev-list`, `git show`, `git stash list`, `git branch`, and scratch Python reading and writing the permitted files |

## 6. Changes from the R3 remediation

The R4 proposal is the R3 proposal with these changes, and nothing else: the title, header and status
block (R4 identity, prompt and authority pins, links to the R3 re-review, the R3 proposal and handback and
the erratum); §0.1 rewritten; the step 5 row and following paragraph of §0.2; one row in §0.3 and one
paragraph in §0.4; a new **§0.7**; §1.1 (thirteen R4 records, new digests, the pointers' pre-edit state)
and a re-run note and the pointer-bytes search in §1.2; three bullets of the R3 re-review and the R4
authority in §2.1; one passage of §2.2; the §2.4 gate (R3 → R4 wording, one sentence added); the COR-01
read count; §7.4's B2-S block (with a process-tree table and a fourth column on the 2×2) and one sentence
after B2-N; the B2-S row of §9.3; Table A's B2-F and B2-S rows, a new **rule PT** and one reading item in
§10.1; a new **§10.3**; the §12.2 `sudo` row; the PD-2a row of §13.2; the §14 checklist (R4C-1 … R4C-13
added, R3C and RC carried); and one clause in §15. **No boundary member, no recommendation direction, no
COR-01 … COR-16 meaning, no worked-row cell and no Peter decision changed.**

## 7. Unresolved Peter decisions and governance gates

* **PD-1** BC-2 reading (before any WP-9 selection of LIT-FULL; not a WP-2 gate).
* **PD-2a** where a `sudo`-started root procedure begins; **PD-2b** whether `AP-2` and the OS-6 `stop` are
  root procedures (each separately, under both PD-2a answers); **PD-3** whether the installer class, `H-1R`
  included, is a root procedure. All three are required, recorded, before WP-2 in every combination.
* **Gates:** independent Codex re-review of this R4 remediation; the BQ-2 and BQ-3 records; **complete §0.2
  change control for every exception the chosen answers contain** (EX-1, EX-2, EX-3) **and** every
  separately authorized and reviewed design prerequisite they require (B2-N; the Python-free installer
  design), **both complete where both apply** (§10.3); or, for literal LIT-FULL (row S-2), the two design
  prerequisites alone, or withdrawal.
* **For the controller (not decided here):** (a) whether to create dated, indexed snapshots of the
  R4-authorization pointer text preserved in Appendix A, as the erratum's forward control requires; this
  return could not, because the prompt permits no new snapshot files; (b) whether to snapshot and index the
  R4-returned pointers before the next authorization becomes current, as was done for R3.
* **Not decided here:** BQ-2, BQ-3, PD-2a, PD-2b, PD-3, EX-1, EX-2, EX-3, BC-4, BC-2, whether `AP-2` or the
  OS-6 `stop` belongs in the set, whether `H-1R` belongs in the installer class. Concrete Route 3 remains
  unestablished; WP-2 is not authorized.

## 8. Checks not run

No host check of any kind, no test, formatter, linter, type checker or build, no Markdown linter (none is
configured; the scratch structure check is the substitute), no package or network operation. No suite
figure is claimed. No digest match for the missing R3-authorization pointer bytes could be performed,
because the bytes are not in the repository.

## 9. Post-write verification

| Check | Exact result |
|---|---|
| Appendix A.1: digest, byte count and line count recomputed over the block | equal (3638 bytes, 55 lines, `78dd71dcd8de…6cd61f`) |
| Appendix A.2: digest, byte count and line count recomputed over the block | equal (4355 bytes, 71 lines, `9715da2e3cee…15172c`) |
| Appendix A.3: digest, byte count and line count recomputed over the block | equal (3850 bytes, 60 lines, `cda0a1d7a3e8…61e9f9`) |
| Appendix A.4: digest, byte count and line count recomputed over the block | equal (2881 bytes, 42 lines, `d3ad5e331fef…2712e1`) |
| Appendix A.1 and A.2 equal the pre-edit copies saved before the first pointer edit | equal |
| local link targets of the handback, proposal, erratum, four pointers and four archive indexes (189 links) | all resolve |
| trailing whitespace in the handback outside Appendix A | none |
| Appendix A contains trailing whitespace (verbatim text of the pre-edit pointers) | none |
| placeholder left in the handback | none |
| whole-tree comparison (871 files before): created | 3: phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-pointer-archive-erratum.md, phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-handback.md, phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-proposal.md |
| whole-tree comparison: deleted | 0 |
| whole-tree comparison: changed | 8: implementation-plan-archive/README.md, implementation-plan.md, operations/disposable-test-server-archive/README.md, operations/disposable-test-server.md, project-management/status-archive/README.md, project-management/status.md, review/Handover information, review/handover-archive/README.md |
| the four R3-return snapshots: SHA-256 on disk equals the value its archive index records | 4 of 4 equal |
| archive indexes: one erratum entry in each | 4 table rows across the 4 indexes |
| `git status --short` entries (46 at session start) | 49; HEAD `9ac7ca488105322483f4d5d5f1794e6e4c0bbe11` unchanged; no commit, no push |
| the proposal's line count, byte count and SHA-256 equal the header table of this handback | equal |
| the erratum's line count, byte count and SHA-256 equal the header table of this handback | equal |

## 10. Statement on prohibited operations

**No prohibited operation occurred.** I used no SSH and made no connection to any host; did not access
retained evidence, secrets, credentials, player data, production, staging, `oracle-test`, Foundry or a
database; did no network research; ran no package operation, installation, implementation, configuration
or infrastructure edit, launcher work, build, test, formatter, service or database operation, cleanup or
workspace recreation; did no OH-S4/OH-S4p or later work, no H-1/H-2, activation or rollback; opened and
executed no §0.2 change control; made no Product Owner decision beyond faithfully recording the
authority; and made no commit and no push. I edited no accepted record, review, authority, exact prompt,
register, archived snapshot or earlier deliverable, and I added to each archive index only the one erratum
entry the prompt names.

## Appendix A. The R4-authorization pointer text this return overwrote, verbatim

Each block is the exact text the pointer carried when this run began. The digest of each is given; the
text between the fences, without the fence lines, hashes to it. **Appendix A is evidence kept in this
handback. It is not a snapshot and is not indexed** (§3, §7).

### A.1 `docs/review/Handover information` (whole file)

Lines 55, bytes 3638, SHA-256 `78dd71dcd8de8ee83cc656370a9dd24e115af9f50bc5289215340371ca6cd61f`.

````text
# Active handover — LIT-FULL WP-1 R4 remediation authorized — 2026-10-08

Peter Duscha accepts neither the R3 proposal nor WP-1. Independent Codex
re-review of the R3 remediation found two Blocking defects and one Important
defect: WP1-R3R-1 identifies the contradictory post-B2-N `sudo` tree; WP1-R3R-2
identifies the non-cumulative “4 or 4′” gate; and WP1-R3R-3 identifies the
missing durable archive of superseded R3-authorization pointer text. WP-1
remains `changes requested`.

Peter authorizes Claude Code to execute the exact repository-only R4 remediation
prompt under work ID
`C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R4-20261008-13`. The prompt is 12,936 bytes,
245 lines, SHA-256
`218040bc5bc5ee34e27cb1e1eeaceb66443992f25ebb30629a2053ae7c473620`.
It creates a cumulative R4 proposal, an honest archive erratum and a durable
handback; corrects the two boundary/gate contradictions; preserves all earlier
corrections; and returns for independent Codex re-review. The R3-returned
current-state text was snapshotted and indexed before this authorization became
current.

**WP-1 remains `changes requested` and is NOT accepted; BQ-2 and BQ-3 are
undecided; PD-2a, PD-2b and PD-3 are undecided; EX-1, EX-2, EX-3, BC-4 and BC-2
are neither decided nor approved; concrete Route 3 remains unestablished; WP-2
is not authorized.**

**Gate before WP-2.** Independent Codex re-review of the R4 remediation and
Peter's recorded BQ-2 and BQ-3 decisions, including PD-2a, PD-2b and PD-3, are
always necessary. If either chosen answer contains an exception, including
EX-1, EX-2 or EX-3 under BC-4, the complete implementation-plan §0.2
change-control process must close before WP-2 may be prompted, authorized or
rely on that boundary. A Peter decision on BQ-2 or BQ-3 is not by itself §0.2
approval. Every separately required design prerequisite must also exist under
its own authority and independent review before WP-2 may rely on it. If Peter
retains literal no-exception LIT-FULL, WP-2 remains blocked until the required
loader-free privileged-start and, where B3-IN is selected, installer designs
make the boundary attainable, or Peter withdraws the affected design. BC-2
remains unresolved for any later WP-9 selection. WP-1 remains changes-requested
and is not accepted; BQ-2 and BQ-3 are undecided.

No host or retained-evidence access, network research, cleanup, workspace
recreation, implementation, configuration/infrastructure edit, launcher work,
build, test, formatter, package or service/database operation, OH-S4/OH-S4p or
later slice, H-1/H-2, activation, rollback, commit or push is authorized. No
successor implementation is authorized. The R5 and H-0G retained paths remain
untouched pending separately gated LC-3 through LC-5 authority.

- [Active R4 remediation prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-claude-prompt.md)
- [R4 remediation authority](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-authority.md)
- [Independent R3 re-review](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation.md)
- [R3 remediation proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-proposal.md)
- [R3 remediation handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-handback.md)
- [G-1 decision record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md)
- [Accepted cumulative R8 proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md)
- [Archived R3-return handover](Handover-information-through-2026-10-08-lit-full-wp1-r3-remediation-return.md)
- [Handover archive index](handover-archive/README.md)
````

### A.2 `docs/project-management/status.md` (whole file)

Lines 71, bytes 4355, SHA-256 `9715da2e3cee8ca16bced25f7e56fa8e7178026a48c802c5e1c0cb728215172c`.

````text
# Project status

This is the concise current operational-status entry point. Historical states
are indexed under [`status-archive/`](status-archive/README.md).

## Current status — LIT-FULL WP-1 R4 remediation authorized — 2026-10-08

The canonical public repository is `ming-themerciless/freedom-platform` at
`https://github.com/ming-themerciless/freedom-platform.git`. The rename does
not rename the Freedom bot application or service.

Peter Duscha accepts DEC-1 through DEC-6 exactly as recommended in the accepted
OH-S3 R8 proposal and commissions the LIT-FULL/R3-ROOT Route 3 readiness
investigation, WP-1 through WP-7 in dependency order. This preserves the
accepted Route 3 boundary and does not select LIT-FULL for implementation.

Independent Codex re-review of the R3 remediation requests two Blocking and one
Important correction (WP1-R3R-1 through WP1-R3R-3). Peter accepts neither the
R3 proposal nor WP-1.

Peter authorizes Claude Code to execute the exact repository-only R4 remediation
prompt under work ID
`C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R4-20261008-13`. The prompt is 12,936 bytes,
245 lines, SHA-256
`218040bc5bc5ee34e27cb1e1eeaceb66443992f25ebb30629a2053ae7c473620`.
It corrects the contradictory post-B2-N process-tree statement, makes the
governance/design gate cumulative, records the missing R3-authorization archive
honestly, and preserves the earlier corrections and boundaries. The
R3-returned current-state text was snapshotted and indexed before this
authorization became current.

**WP-1 remains `changes requested` and is NOT accepted; BQ-2 and BQ-3 are
undecided; PD-2a, PD-2b and PD-3 are undecided; EX-1, EX-2, EX-3, BC-4 and BC-2
are neither decided nor approved; concrete Route 3 remains unestablished; WP-2
is not authorized.**

**Gate before WP-2.** Independent Codex re-review of the R4 remediation and
Peter's recorded BQ-2 and BQ-3 decisions, including PD-2a, PD-2b and PD-3, are
always necessary. If either chosen answer contains an exception, including
EX-1, EX-2 or EX-3 under BC-4, the complete implementation-plan §0.2
change-control process must close before WP-2 may be prompted, authorized or
rely on that boundary. A Peter decision on BQ-2 or BQ-3 is not by itself §0.2
approval. Every separately required design prerequisite must also exist under
its own authority and independent review before WP-2 may rely on it. If Peter
retains literal no-exception LIT-FULL, WP-2 remains blocked until the required
loader-free privileged-start and, where B3-IN is selected, installer designs
make the boundary attainable, or Peter withdraws the affected design. BC-2
remains unresolved for any later WP-9 selection. WP-1 remains changes-requested
and is not accepted; BQ-2 and BQ-3 are undecided.

WP-2 through WP-7 remain separately gated. Concrete Route 3 remains
unestablished and no Route 3 implementation is authorized. The accepted R8
design, R2 citation basis and missing-fact dispositions otherwise remain
unchanged.

No host or retained-evidence access, network research, cleanup, workspace
recreation, implementation, configuration/infrastructure edit, launcher work,
build, test, formatter, package or service/database operation, OH-S4/OH-S4p or
later slice, H-1/H-2, activation, rollback, commit or push is authorized. No
successor implementation is authorized. The R5 and H-0G retained paths remain
untouched pending separately gated LC-3 through LC-5 authority.

[Active R4 remediation prompt](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-claude-prompt.md)
· [R4 remediation authority](../review/project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-authority.md)
· [Independent R3 re-review](../review/project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation.md)
· [R3 remediation proposal](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-proposal.md)
· [R3 remediation handback](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-handback.md)
· [G-1 decision record](../review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md)
· [Accepted cumulative R8 proposal](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md)
· [Archived R3-return status](status-through-2026-10-08-lit-full-wp1-r3-remediation-return.md)
· [Status archive](status-archive/README.md).
````

### A.3 `docs/implementation-plan.md`, §20 (from the heading to the end of the file)

Lines 60, bytes 3850, SHA-256 of this excerpt `cda0a1d7a3e868783fdb59fa0f9d0aad75eafe12b9ffae0139400fed2761e9f9`. The whole pre-edit file is 2,617 lines, 129,045
bytes, SHA-256 `ca60068199d9fa5049adf0b43c54b66ba79bc3e9412e89fb836d80159fc6d111`.

````text
## 20. Immediate next actions

Peter Duscha accepts DEC-1 through DEC-6 exactly as recommended in the accepted
OH-S3 R8 proposal. For G-1b he commissions the LIT-FULL/R3-ROOT Route 3
readiness investigation, WP-1 through WP-7 in dependency order. This preserves
the accepted Route 3 boundary, opens no §0.2 scope change and does not select
LIT-FULL for implementation.

Independent Codex re-review of the R3 remediation requests two Blocking and one
Important correction (WP1-R3R-1 through WP1-R3R-3). Peter accepts neither the
R3 proposal nor WP-1.

**Current action:** Claude Code executes the exact repository-only R4 remediation
prompt under work ID
`C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R4-20261008-13`. Peter authorizes that prompt
at 12,936 bytes, 245 lines, SHA-256
`218040bc5bc5ee34e27cb1e1eeaceb66443992f25ebb30629a2053ae7c473620`.
It corrects the contradictory post-B2-N process-tree statement, makes the
governance/design gate cumulative, records the missing R3-authorization archive
honestly, and preserves the earlier corrections and boundaries. The
R3-returned current-state text was snapshotted and indexed before this
authorization became current.

**WP-1 remains `changes requested` and is NOT accepted; BQ-2 and BQ-3 are
undecided; PD-2a, PD-2b and PD-3 are undecided; EX-1, EX-2, EX-3, BC-4 and BC-2
are neither decided nor approved; concrete Route 3 remains unestablished; WP-2
is not authorized.**

**Gate before WP-2.** Independent Codex re-review of the R4 remediation and
Peter's recorded BQ-2 and BQ-3 decisions, including PD-2a, PD-2b and PD-3, are
always necessary. If either chosen answer contains an exception, including
EX-1, EX-2 or EX-3 under BC-4, the complete implementation-plan §0.2
change-control process must close before WP-2 may be prompted, authorized or
rely on that boundary. A Peter decision on BQ-2 or BQ-3 is not by itself §0.2
approval. Every separately required design prerequisite must also exist under
its own authority and independent review before WP-2 may rely on it. If Peter
retains literal no-exception LIT-FULL, WP-2 remains blocked until the required
loader-free privileged-start and, where B3-IN is selected, installer designs
make the boundary attainable, or Peter withdraws the affected design. BC-2
remains unresolved for any later WP-9 selection. WP-1 remains changes-requested
and is not accepted; BQ-2 and BQ-3 are undecided.

Concrete Route 3 remains unestablished. WP-2 through WP-7 remain separately
gated; WP-9 remains Peter's later choice after readiness.

No host or retained-evidence access, network research, cleanup, workspace
recreation, implementation, configuration/infrastructure edit, launcher work,
build, test, formatter, package or service/database operation, OH-S4/OH-S4p or
later slice, H-1/H-2, activation, rollback, commit or push is authorized. No
successor implementation is authorized. The R5 and H-0G retained paths remain
untouched pending separately gated LC-3 through LC-5 authority.

[Active R4 remediation prompt](review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-claude-prompt.md)
· [R4 remediation authority](review/project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-authority.md)
· [Independent R3 re-review](review/project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation.md)
· [R3 remediation proposal](review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-proposal.md)
· [R3 remediation handback](review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-handback.md)
· [G-1 decision record](review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md)
· [Accepted cumulative R8 proposal](review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md)
· [Archived R3-return §20](implementation-plan-through-2026-10-08-lit-full-wp1-r3-remediation-return.md).
````

### A.4 `docs/operations/disposable-test-server.md`, from the title to the line before "Agents that support skills …"

Lines 42, bytes 2881, SHA-256 of this excerpt `d3ad5e331fefc43f3e162e0402d88a287aec78beb8349402a00a5281b22712e1`. The whole pre-edit file is 186 lines, 9,263
bytes, SHA-256 `efc090d80fad494c570e0ac5ceea665dcaf65d55e0ff2fa97bf1519bb61354c8`.

````text
# Disposable Linux Test Server

**Active restriction, 2026-10-08 — LIT-FULL WP-1 R4 remediation authorized; no host authority.**

Peter authorizes Claude Code to execute the exact repository-only R4 remediation
prompt under work ID
`C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R4-20261008-13`. It remediates two Blocking
and one Important finding from the independent R3 re-review. WP-1 remains
changes-requested and not accepted; BQ-2 and BQ-3 are undecided. Concrete Route
3 remains unestablished; WP-2 is not authorized.

**Gate before WP-2.** Independent Codex re-review of the R4 remediation and
Peter's recorded BQ-2 and BQ-3 decisions, including PD-2a, PD-2b and PD-3, are
always necessary. If either chosen answer contains an exception, including
EX-1, EX-2 or EX-3 under BC-4, the complete implementation-plan §0.2
change-control process must close before WP-2 may be prompted, authorized or
rely on that boundary. A Peter decision on BQ-2 or BQ-3 is not by itself §0.2
approval. Every separately required design prerequisite must also exist under
its own authority and independent review before WP-2 may rely on it. If Peter
retains literal no-exception LIT-FULL, WP-2 remains blocked until the required
loader-free privileged-start and, where B3-IN is selected, installer designs
make the boundary attainable, or Peter withdraws the affected design. BC-2
remains unresolved for any later WP-9 selection. WP-1 remains changes-requested
and is not accepted; BQ-2 and BQ-3 are undecided.

No SSH connection to `oracle-test`, host or retained-evidence access, fact
collection, cleanup, workspace recreation, privilege, package operation,
installation, build, test, formatter, service/database mutation, H-1/H-2,
OH-S4/OH-S4p or later slice, activation, rollback, commit or push is authorized.
No successor implementation is authorized. MF-1 through MF-8 remain
uncollected. The R5 and H-0G retained paths remain untouched pending separately
gated LC-3 through LC-5 authority.

[Active R4 remediation prompt](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-claude-prompt.md)
· [R4 remediation authority](../review/project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-authority.md)
· [Independent R3 re-review](../review/project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation.md)
· [R3 remediation proposal](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-proposal.md)
· [R3 remediation handback](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-handback.md)
· [G-1 decision record](../review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md)
· [Accepted cumulative R8 proposal](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md)
· [Archived R3-return restriction](disposable-test-server-through-2026-10-08-lit-full-wp1-r3-remediation-return.md).

````
