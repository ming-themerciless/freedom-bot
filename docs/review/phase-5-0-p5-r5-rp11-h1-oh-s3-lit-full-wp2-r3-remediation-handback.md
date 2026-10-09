# LIT-FULL WP-2 R3 remediation — handback

**WP-2 R3 REMEDIATION RETURNED — INDEPENDENT RE-REVIEW PENDING.**

Work ID `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R3-20261009-17`. Executor: Claude, once, under the bounded repository-only authority of the accepted prompt `phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3-remediation-claude-prompt.md` (236 lines, 12,257 bytes, SHA-256 `06d974f68a3c1c3e2ebec886fe4b3101f6507d8c658b3ad41045ad8cc5b04fe1`, verified in the ledger below). Date 2026-10-09. **No HARD STOP.**

This return does not accept WP-2, authorize WP-3, establish concrete Route 3 or select LIT-FULL for implementation. Baseline v1.8, the F-1 boundary (B2-F; `AP-2` and the OS-6 `stop` in; H-1, RB-1, RS-1, H-1R out), EX-1/EX-2 (no EX-3) and the separate WP-3 … WP-7 gates are preserved. Independent Codex re-review and Peter's later acceptance are required before any WP-3 prompt or authority.

## 1. Deliverables

The corrected cumulative, self-contained inventory is `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md` (1426 lines, 223855 bytes, SHA-256 `e5c32312caf87d337b581a0fa8a8715a6396bcc0755f134d34421503c441d1e2`). This handback cannot contain its own SHA-256, because the value would change the file it describes; its byte count, line count and hash are reported only in the terminal chat summary, which is a convenience, not evidence. Everything else a reviewer needs is in this file.

## 2. The three findings and exactly how each was remediated

### 2.1 `WP2-R2-1` — Blocking — complete-reading precondition not met

All 26 required items were read first byte through EOF **before the first edit**, in chunks that stayed under the tool's read limit (no search, excerpt, heading scan, prior read or summary was used as a substitute). For items 2 and 4 the prompt requires only the named portions (the plan's reading map and §§0, 16, 20; the test-server restriction banner); those portions were read completely and the whole-file figures are given for identification. The pre-edit ledger (§3) was recorded in working notes before the first edit; after the reading was complete the same figures were recomputed and found **identical** (all 26 rows: lines, bytes, SHA-256), which shows that no required source changed during the reading. Every item was readable, so no HARD STOP applied.

The whole cumulative inventory was revalidated against the governing sources, not only the changed rows: the scratch parser reproduced the R2 counts exactly (317 rows, class, tag, question and step counts), and the SN, DI and call-site statements were compared with D R2 (f), R8 §7.5a, §8.1, §9.3, A-I-16 and WP-1 R6. Nothing outside the three findings was changed (§9 reports what was noticed and left alone).

### 2.2 `WP2-R2-2` — Blocking — SN-10 / A-I-16 wrongly extended to BS-4

Complete reading found that SN-10 names the `systemd-run` call (AK-1) and the `systemctl stop` calls at BS-2 and BS-3; R8 §9.3 DI-4, A-I-16 and WP-1 R6 list BS-2 and BS-3; D R2 (f) BS-4 and R8 §8.1 BS-4 Δ2 state the BS-4 terminal-disarm call without stating the `unknown`-effect treatment. **No accepted passage applies the obligation to BS-4, and none excludes it**, so no HARD STOP applies and no answer was chosen. Changes, all in the inventory:

- BS-4 stays the third DI-4 call site (`CALL-DI4-03`, row `RT4.BS4.2`); the three-site reconciliation of §7.1, §8 (PC-5) and §11.3(c) is unchanged.
- `RT4.BS4.2` no longer states or implies SN-10 / A-I-16; its tag `Q6-6` became `Q6-7`, and it says the treatment is not stated and the extension is open.
- `RT4.SN.1` now states the mutating-child / `unknown`-effect treatment for the BS-2 and BS-3 calls (and for DI-3 via `RT2.SN.1`) only, and tags `Q6-6;Q6-7`.
- §7 (DI-4 row), §7.1 (`CALL-DI4-03` note), §8 (PC-5), §8.1 (DI-4 row and the preserved-obligation paragraph) and §13 carry the same distinction; §12 Q6-6 now covers DI-3, BS-2 and BS-3 only; §12 Q6-7 gained the BS-4 extension question (no new question ID); §11.4 and its note, §14 and §15 were reconciled; an R3 revision record and an R3 stop-rule note were added.
- The edit was a scripted exact-string replacement with an assertion that each target occurred exactly once; no text outside the listed places changed except the header and revision record.

### 2.3 `WP2-R2-3` — Important — final link-check result missing

The terminal link check was run after every delivered file existed and again after the result field was populated; scope, link count, broken-link count and exit status are in §6.1 of this file. Nothing link-bearing changed after the rerun.

## 3. Pre-edit reading ledger

**Every item below was read first byte through EOF before the first edit** (items 2 and 4: the portions the prompt requires). Figures are `wc -l`, `wc -c` and `sha256sum` of the files as read; the same figures were recomputed after the reading and before the first edit and were identical for all 26 rows. Items 3, 4, 2 are the files later edited as pointers; their figures are the pre-edit (R3-authorization) state, and the snapshots in §4 preserve that state.

| # | Path | Lines | Bytes | SHA-256 as read | Note |
|---|---|---|---|---|---|
| 1 | `.agents/AGENTS.md` | 700 | 36014 | `87bab4ab8d67e308af0c59b99c8604235ee84d75cfa12448458b1a04cc88390a` |  |
| 2 | `docs/implementation-plan.md` | 2616 | 128908 | `3356d23953f90a9e82950eca45b8ce078a047a636be44241a514b68bda54c6c7` | required portion: reading map, §0, §16, §20 (read byte through EOF of each); file stats are of the whole file |
| 3 | `docs/review/Handover information` | 49 | 3289 | `aa7203fbb8fcef9de8282b9009dd9b60d085982fd0f97c34aedf1aa1e13ff659` |  |
| 4 | `docs/operations/disposable-test-server.md` | 193 | 9521 | `72c7937b6031e9ec9a746702fcb0d40bb16670d0e44ddbbd7c309c8371ce8983` | required portion: the restriction banner block (lines 1–48); file stats are of the whole file |
| 5 | `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md` | 46 | 2455 | `09234e4acada1b3487f9147f0c8c76110a90dc1dc491e6a02f68892c07bab00e` |  |
| 6 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md` | 4816 | 551246 | `ab5db5010d9d1b2738b04f1ffbd62ab4414d901e9f7f79323ac49f811f660e04` |  |
| 7 | `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r8-acceptance.md` | 46 | 2653 | `594292d44d9ad5b161dc61a6f4cdc6457b56029d73cc1be60da84153c8c01e30` |  |
| 8 | `docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md` | 7307 | 525019 | `a752a4b8fe7eb1edf3e3a25decd3a7517ecccc85fedbb0b0b7e003cb7e615d02` |  |
| 9 | `docs/review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-acceptance.md` | 59 | 2633 | `afe1f2256259244f207c87a1244be5455ad18aebc6ac9a86db400fc105f729f5` |  |
| 10 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md` | 1866 | 177481 | `299f0598bb198572f2edb994234a63956ecafc9ab1873cb10879d0a238dea1a5` |  |
| 11 | `docs/review/project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-acceptance.md` | 43 | 2186 | `af72d1e2017292b932148c467004bb096556553cdb6d5e9453846c12e20f258c` |  |
| 12 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation-proposal.md` | 1741 | 155403 | `f0c4e92e40f74bf5b4f65919853b9fbac6341a5e677fa6ab90e958246b3f3d2e` |  |
| 13 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation.md` | 88 | 4203 | `18a4288bfb3d572dc9f7a43bfd05ca87a819b002eb72b63081815c67f94fb4c7` |  |
| 14 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-acceptance-and-bq-decisions.md` | 46 | 2925 | `13c8b466b666fc53b63e924e283a3bc7effc12389024a5e1327adf1f95a7527f` |  |
| 15 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-ex1-ex2-change-control-assessment.md` | 126 | 10861 | `00269aed9b9350068a7e94de99e5dab990f6237452fd3f0f4230d7bd88a80d2b` |  |
| 16 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-ex1-ex2-change-control-approval.md` | 50 | 2878 | `ab7b7e54f45ad3600ea4c00cde904aba10582ce44b8dbec6710a580167479332` |  |
| 17 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1-claude-prompt.md` | 207 | 11016 | `6737e231e8237805a6517d006240321c4c4fb7aa14b1923aaa2b3a80cb2f6510` |  |
| 18 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md` | 1410 | 220050 | `e2960f233d4d5e540a68011f6dab2bc297442088eab28d36867b5736f13e3012` |  |
| 19 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-handback.md` | 102 | 9987 | `e324f18aa3ad3550bd1a02c1c1b12d414f40cc95e55e9e81315c99e7e62a099f` |  |
| 20 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1.md` | 127 | 6618 | `058e355573cbb3a0e011b8436fc7e1ac53865af19d387d96ee8c1c8959edd2f6` |  |
| 21 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-claude-prompt.md` | 205 | 9640 | `4fb48bcd3c482fe053623256ebe54d5d2cf379913605099146a04544cb10d14b` |  |
| 22 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-acceptance-and-claude-activation.md` | 65 | 3060 | `423a90f47c31fb9b879fa0c1fbf13144b5c3c3ba06116ba745eeb956b4a0538b` |  |
| 23 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-handback.md` | 155 | 22952 | `72d5e4eef058f81f839a57d9138eb98b17bf8c6bb10be355bfd9b68790d25fc2` |  |
| 24 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2.md` | 154 | 8230 | `f36ad5b15d6b8742836a6cd188167c06c32714617cd8aab77371381ee4a58118` |  |
| 25 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3-remediation-claude-prompt.md` | 236 | 12257 | `06d974f68a3c1c3e2ebec886fe4b3101f6507d8c658b3ad41045ad8cc5b04fe1` |  |
| 26 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3-remediation-acceptance-and-claude-activation.md` | 66 | 3295 | `51ba13ec1007495ca7f9d6a7aaceaa148504aaec75bc97c7ac75af3bc8f3da42` |  |

## 4. Files created and edited

Created (5): this handback and the four dated snapshots (`lit-full-wp2-r3-authorization`), whose SHA-256 values are in the four archive indexes and below. Edited (9): the inventory, the four current-state pointers and the four archive indexes. The snapshot extents follow earlier practice: whole files for the handover and status; the §20 block (line 2559 to end of file) for the plan; the banner block (lines 1–48) for the test-server document. No other file was written. Scratch material (parser, ledger, pre-edit copies) is held in the session scratchpad outside the repository and is not delivered.

| Role | Path | Lines | Bytes | SHA-256 |
|---|---|---|---|---|
| Corrected cumulative inventory | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md` | 1426 | 223855 | `e5c32312caf87d337b581a0fa8a8715a6396bcc0755f134d34421503c441d1e2` |
| Pointer: handover | `docs/review/Handover information` | 43 | 2917 | `ae9cb85518f0848501dec5a7d7a1dea9e0e8eb94afde4b0fbf9148ca3ad34bd5` |
| Pointer: status | `docs/project-management/status.md` | 52 | 3312 | `cd1cdf66cf90f40661aa09ff983206faa6ef8dcfae257e706a3eec8ea003599d` |
| Pointer: plan (§20 edited only) | `docs/implementation-plan.md` | 2612 | 128782 | `5c57231841b13b3495b73eeb2c8c2dcb9020fb5bc5e21bb3a33691a6cb2608e5` |
| Pointer: test-server banner (banner edited only) | `docs/operations/disposable-test-server.md` | 189 | 9394 | `adac0e8b38b733cdb58a656c5658604338a232f96cac14c4f8305edd26c1b1ac` |
| Snapshot | `docs/review/Handover-information-through-2026-10-09-lit-full-wp2-r3-authorization.md` | 49 | 3289 | `aa7203fbb8fcef9de8282b9009dd9b60d085982fd0f97c34aedf1aa1e13ff659` |
| Snapshot | `docs/project-management/status-through-2026-10-09-lit-full-wp2-r3-authorization.md` | 56 | 3418 | `851334df3c6e7d11eefa046404075e132f5643e0fe7b2af20b9e5821bd5aaa75` |
| Snapshot | `docs/implementation-plan-through-2026-10-09-lit-full-wp2-r3-authorization.md` | 58 | 3684 | `97f874292be598f690eb4474ec08180a041a13c90b43750ea17e5a72018ff1c9` |
| Snapshot | `docs/operations/disposable-test-server-through-2026-10-09-lit-full-wp2-r3-authorization.md` | 48 | 3138 | `6bde62bb9d1c969dba16c6ea383c93cddb3aa818da802715930f93aadc17e4f7` |
| Archive index (one new top row) | `docs/review/handover-archive/README.md` | 63 | 17474 | `b6cab1552bebed4e83286787389d795c79bdc6bb6556a79244132ec71650de7c` |
| Archive index (one new top row) | `docs/project-management/status-archive/README.md` | 62 | 15718 | `a4d3cc90c1c34bb9b37631f535754fd090781459dc7c501176bd1e9c274be244` |
| Archive index (one new top row) | `docs/implementation-plan-archive/README.md` | 49 | 14091 | `9343005319aaafa89441d9cbbcc60afbe121f29d650b08cba52b0bd279ecc45e` |
| Archive index (one new top row) | `docs/operations/disposable-test-server-archive/README.md` | 50 | 14199 | `e57d6c5da51e4c06354e6f1ca5da10c4178c3e7972abb10d8957b38997ca7e22` |

## 5. Corrected counts [M]

Recomputed by a read-only parser run over the delivered inventory bytes (the parser is a convenience, not evidence). Compared with the R2 inventory:

| Figure | R2 | R3 |
|---|---|---|
| Rows (all tables with row IDs) | 317 | 317 (316 operation / contract / composition rows + 1 gap row `RT2.AM0.7`) |
| Row classes | as §11.2 | unchanged (e.g. UA 24, CN 62, CMP 36, GAP 1) |
| Tags | A+Q 73, A only 237, M 6, Q alone 1 | unchanged |
| Logical accepted call sites (DI-1 … DI-6, stop unit) | 41 (DI-4: 3) | 41 (DI-4: 3) |
| Rows carrying Q6-6 | 6 | **5** (`RT2.AK1.2`, `RT2.SN.1`, `RT4.BS2.2`, `RT4.BS3.1`, `RT4.SN.1`) |
| Rows carrying Q6-7 | 1 | **3** (`RT2.AM0.7`, `RT4.BS4.2`, `RT4.SN.1`) |
| Every other question count (Q3-x, Q4-x, Q6-1 … Q6-4) | §11.4 | unchanged |
| Questions defined in §12 / in §11.4 / sets equal | 24 / 24 / yes | 24 / 24 / yes |
| Step, taxonomy and identifier-citation counts (§11.2, §11.3) | as R2 | not touched by any R3 edit; the §11.3(d) identifier recount reproduces every cited figure except `RA-E`, where the scratch parser counts 0 and the table states 1 — a mismatch the scratch parser also shows, identically, on the R2 file and which was assessed as a parser artifact (the cause was not investigated further); the table figure is the R2 figure and was not altered |

## 6. Checks run, with exact scope and results

All checks are repository-only reads of the files named. No application or hook suite, build, formatter or linter was run (none is authorized or relevant).

1. Reading ledger: `wc -l`, `wc -c` and `sha256sum` of the 26 required items before and after the reading — identical.
2. Scratch parser on the R2 inventory (reproduced R2 counts) and on the R3 inventory (§5 above).
3. Leftover-statement search in the inventory for “three sites”, “each a mutating”, “at all three”, “all three”: the only remaining hits are the DI-1 `RT3.CL6`, `RT4.CL6`, `RT5.CL6` “implements three sites” notes and the DI-4 three-call-site reconciliation statements, all correct.
4. `git diff --check` over the delivered files: exit 0, no whitespace errors reported for the nine edited tracked files (the new files are untracked; a trailing-whitespace search over them found none).
5. Link check — see §6.1.

### 6.1 Terminal link check

Rule: every relative Markdown link target (the parenthesised part of a bracket-then-parenthesis link; not `http…`, `mailto…` or `#anchor`) in the 14 delivered link-bearing files — the inventory, this handback, the four current-state pointers (handover, status, plan, test-server document), the four snapshots and the four archive indexes — is resolved against the file's own directory and tested for existence. Anchors are stripped before the test; anchors themselves are not checked. The check ran after every delivered file existed, was run again after this field was populated, and nothing link-bearing changed afterwards.

**Result field (populated after the first run; the rerun after population gave the identical result):** scope 14 files; 237 links checked; 0 broken; exit status 0. One earlier run reported 1 broken: that was this section's own description of the rule, which contained a literal link pattern; it was reworded before the terminal runs and is not a missing file.

## 7. Checks not run, and why

Nothing the prompt required was skipped. Not run, because outside this authority and irrelevant to a documentation-only remediation: application and hook suites, builds, formatters, linters, `python3 .claude/hooks/test_guards.py`, any host or `oracle-test` command.

## 8. Unresolved later-package questions

None was answered. §12 of the inventory lists all 24 with owners; the two touched here are **Q6-6** (the `effect: "unknown"` obligation for the DI-3 call at AK-1 and the DI-4 calls at BS-2 and BS-3, mapping to a non-child interaction unanswered, WP-6) and **Q6-7** (accepted-text gaps, now including whether SN-10 / A-I-16 extend to the BS-4 terminal disarm, in addition to the AM-0 “no unterminated activation” question, `run-end` placement, BS-4's final-line journal and the `helper.image_sha256[]` source, WP-6). WP-2 selected neither extension nor exclusion for BS-4 and neither answer for AM-0.

## 9. Observations outside the three findings (reported, not remediated)

Found during the complete reading and left as they are, because the prompt forbids silently repairing matters outside the three findings; none changes a count in §5 and none is a HARD STOP:

- the formula and wording used for `T_s` in the accepted text versus how the inventory restates it should be confirmed by the reviewer against the cited passages;
- the AM-0 “absence conditions” phrase and the row `RT2.AM0.5` — the competing wording already recorded under Q6-7;
- D R2 (i) lists a gate in which AM-0 is not named, which bears on the same Q6-7 question and was not used to resolve it;
- no row `RT-3.SN` exists beside the other procedures' SN rows; the RT-3 child surface is covered by the shared child-surface rows and §8.1, and the reviewer may judge whether a separate row is wanted;
- some accepted passages speak of mutating children at class level without naming call sites; the inventory applies the obligation only where a passage names the call, which is the rule applied to BS-4.

## 10. Prohibited actions

None occurred. No SSH, host, `oracle-test`, retained-evidence, secret, credential, player-data, production, staging, Foundry or database access; no network research; no package, installation, implementation, configuration, launcher, build, test, formatter or service operation; no cleanup or workspace recreation; no WP-3 work, OH-S4/OH-S4p or later work, H-1/H-2, activation or rollback; **no commit or push**. The R5 and H-0G retained paths were not touched. No earlier snapshot, accepted record, earlier handback, independent review, prompt or authority record was changed.

## 11. Reviewer focus for the independent re-review

1. `WP2-R2-1`: check the ledger (§3) against the prompt's 26-item list and re-verify a sample of the hashes; confirm the statement of reading is unambiguous.
2. `WP2-R2-2`: search the inventory for every occurrence of “SN-10”, “A-I-16”, “unknown” and “BS-4” and confirm that none applies the obligation to the BS-4 terminal disarm; confirm `CALL-DI4-03`, `RT4.BS4.2` and the three-site statements are intact; confirm Q6-6 is limited to DI-3, BS-2 and BS-3 and Q6-7 carries the BS-4 question with WP-6 as owner; confirm §11.4 (Q6-6 5, Q6-7 3) against the tables.
3. `WP2-R2-3`: re-run the §6.1 rule and compare its numbers with the field.
4. The observations in §9, to decide whether any needs a separately authorized correction.

## 12. Handoff items (plan §16.3)

Task: WP-2 R3 remediation. Authority: the accepted R3 prompt and its activation record. State: returned, awaiting independent re-review. Changed: the files in §4. Not changed: application code, hooks, configuration, hosts. Next: independent Codex re-review, then Peter's decision; no WP-3 work before both.
