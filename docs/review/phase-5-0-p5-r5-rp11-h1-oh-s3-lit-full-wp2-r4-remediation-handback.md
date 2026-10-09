# WP-2 R4 remediation handback — 2026-10-09

**WP-2 R4 REMEDIATION RETURNED — INDEPENDENT RE-REVIEW PENDING.**

Work ID `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R4-20261009-18`. Executor: Claude. Accepted assignment: [WP-2 R4 remediation prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r4-remediation-claude-prompt.md) (237 lines, 12,643 bytes, SHA-256 `df77802e752041ce0a1a3cb2180a622efd673a6945a2a021f1bc70d4d06dafb0`, matching its [activation record](project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r4-remediation-acceptance-and-claude-activation.md)). Basis: the [independent WP-2 R3 re-review](project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3.md).

This return does not accept WP-2, authorize WP-3, establish concrete Route 3 or select LIT-FULL for implementation. Baseline v1.8, the F-1 combination (B2-F), EX-1 and EX-2 (no EX-3) and the no-host restriction are unchanged. WP-3 through WP-7 remain separately gated. No `HARD STOP` was needed: no accepted function requires a dynamic child.

## 1. Findings and remediation

| Finding | Remediation |
|---|---|
| `WP2-R3-1` (Important) — withdrawn `T_s ≥ ⌈P/1000⌉ + 30` presented as current | Removed from `RT1.FI.2` and from the §11.1 `T_s` row, with the `D R4 (g) AR-4` citation dropped from both. `T_s` is stated as the capture unit's loaded finite `TimeoutStartUSec`, PID 1's class-M deadline, required to satisfy N1 (`T_s·1,000 ≥ W_show + W_series + ρ`, `W_show = c + g`, `W_series = P + c + g`). N1 is stated as a necessary condition only; no margin was invented, W-7 was not reinstated and no elapsed-time guarantee was added. A whole-file search found no other statement of the formula; the only remaining occurrences are the R4 revision record and reviewer focus, which name it as withdrawn. §13/§14 checklist and summary statements were reconciled. |
| `WP2-R3-2` (Important) — no `RT3.SN.1` | Added `RT3.SN.1` to §5.3 after `RT3.CLOUT` (class CN, tag [A], §7.3 cell `1,2,3,3a-3g`, blocking `E, X, C`), parallel to the other SN rows and modelled on `RT5.SN.1`. It states the child surface in the two tiers of §8.1 (accepted today: DI-1 unit-state-read children, plus the DI-5 `pkcheck` and DI-6 subject children of CL-4; LIT-FULL replacement: only the DI-6 subject remains, DI-1 and DI-5 children removed), says H-SN governs any child that exists, and keeps the stop-post recovery chain verbatim (the backstop's CL if armed and spawnable, else a later CP, then the boot, then `attest`). No new owner, signal, wait, result or guarantee was introduced. It carries no Q tag: RT-3 performs neither DI-3 nor DI-4. An `SN` step was added to the RT-3 trace (§6). §8.1, the §13 and §14 SN-row lists and the reviewer focus now name five SN rows. |

## 2. Pre-edit reading ledger

All 30 items below were read as specified, first byte through EOF (items 2 and 4 in their required portions: plan reading map, §0, §16, §20; the full banner of the test-server document), **before the first edit of this task**. The ledger was recomputed after the reading and was identical to the pre-reading ledger. Item 18 is the R3 inventory as read, before it was edited; its final state is in §3.

| # | Path | Lines | Bytes | SHA-256 |
|---|---|---|---|---|
| 1 | `.agents/AGENTS.md` | 700 | 36014 | `87bab4ab8d67e308af0c59b99c8604235ee84d75cfa12448458b1a04cc88390a` |
| 2 | `docs/implementation-plan.md` | 2614 | 128700 | `f97ba862623eb37928541fb1870a380ba36a079238be2c5e7f9e27d729ee6fb9` |
| 3 | `docs/review/Handover information` | 46 | 2898 | `9914bfafbf9b133ca56a506efc4ba157346acc881767beba9e7cb899869b5b6b` |
| 4 | `docs/operations/disposable-test-server.md` | 191 | 9297 | `fe41363e4716f3e0a836e68009a8571dcacd17598b316a26c798637b049e8812` |
| 5 | `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md` | 46 | 2455 | `09234e4acada1b3487f9147f0c8c76110a90dc1dc491e6a02f68892c07bab00e` |
| 6 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md` | 4816 | 551246 | `ab5db5010d9d1b2738b04f1ffbd62ab4414d901e9f7f79323ac49f811f660e04` |
| 7 | `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r8-acceptance.md` | 46 | 2653 | `594292d44d9ad5b161dc61a6f4cdc6457b56029d73cc1be60da84153c8c01e30` |
| 8 | `docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md` | 7307 | 525019 | `a752a4b8fe7eb1edf3e3a25decd3a7517ecccc85fedbb0b0b7e003cb7e615d02` |
| 9 | `docs/review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-acceptance.md` | 59 | 2633 | `afe1f2256259244f207c87a1244be5455ad18aebc6ac9a86db400fc105f729f5` |
| 10 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md` | 1866 | 177481 | `299f0598bb198572f2edb994234a63956ecafc9ab1873cb10879d0a238dea1a5` |
| 11 | `docs/review/project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-acceptance.md` | 43 | 2186 | `af72d1e2017292b932148c467004bb096556553cdb6d5e9453846c12e20f258c` |
| 12 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation-proposal.md` | 1741 | 155403 | `f0c4e92e40f74bf5b4f65919853b9fbac6341a5e677fa6ab90e958246b3f3d2e` |
| 13 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation.md` | 88 | 4203 | `18a4288bfb3d572dc9f7a43bfd05ca87a819b002eb72b63081815c67f94fb4c7` |
| 14 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-acceptance-and-bq-decisions.md` | 46 | 2925 | `13c8b466b666fc53b63e924e283a3bc7effc12389024a5e1327adf1f95a7527f` |
| 15 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-ex1-ex2-change-control-assessment.md` | 126 | 10861 | `00269aed9b9350068a7e94de99e5dab990f6237452fd3f0f4230d7bd88a80d2b` |
| 16 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-ex1-ex2-change-control-approval.md` | 50 | 2878 | `ab7b7e54f45ad3600ea4c00cde904aba10582ce44b8dbec6710a580167479332` |
| 17 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1-claude-prompt.md` | 207 | 11016 | `6737e231e8237805a6517d006240321c4c4fb7aa14b1923aaa2b3a80cb2f6510` |
| 18 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md` | 1426 | 223855 | `e5c32312caf87d337b581a0fa8a8715a6396bcc0755f134d34421503c441d1e2` |
| 19 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-handback.md` | 102 | 9987 | `e324f18aa3ad3550bd1a02c1c1b12d414f40cc95e55e9e81315c99e7e62a099f` |
| 20 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1.md` | 127 | 6618 | `058e355573cbb3a0e011b8436fc7e1ac53865af19d387d96ee8c1c8959edd2f6` |
| 21 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-claude-prompt.md` | 205 | 9640 | `4fb48bcd3c482fe053623256ebe54d5d2cf379913605099146a04544cb10d14b` |
| 22 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-acceptance-and-claude-activation.md` | 65 | 3060 | `423a90f47c31fb9b879fa0c1fbf13144b5c3c3ba06116ba745eeb956b4a0538b` |
| 23 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-handback.md` | 155 | 22952 | `72d5e4eef058f81f839a57d9138eb98b17bf8c6bb10be355bfd9b68790d25fc2` |
| 24 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2.md` | 154 | 8230 | `f36ad5b15d6b8742836a6cd188167c06c32714617cd8aab77371381ee4a58118` |
| 25 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3-remediation-claude-prompt.md` | 236 | 12257 | `06d974f68a3c1c3e2ebec886fe4b3101f6507d8c658b3ad41045ad8cc5b04fe1` |
| 26 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3-remediation-acceptance-and-claude-activation.md` | 66 | 3295 | `51ba13ec1007495ca7f9d6a7aaceaa148504aaec75bc97c7ac75af3bc8f3da42` |
| 27 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3-remediation-handback.md` | 151 | 19962 | `3aadf044dded52f912b1c4abd91a315d31c73a8065c5ce27b4dce0fef83fdbae` |
| 28 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3.md` | 143 | 7655 | `d337e1fcd86cc08ebf9f83a00a0537a143b6c73eb662cc60a383ccf8272b52c9` |
| 29 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r4-remediation-claude-prompt.md` | 237 | 12643 | `df77802e752041ce0a1a3cb2180a622efd673a6945a2a021f1bc70d4d06dafb0` |
| 30 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r4-remediation-acceptance-and-claude-activation.md` | 68 | 3414 | `7385370252d43e8d3e64f81e2841389514c28cd038de9fc5bfdee4db7ca7bdd9` |

## 3. Deliverables (final)

| File | Lines | Bytes | SHA-256 |
|---|---|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md` (edited) | 1440 | 227365 | `a981534baba73012ef70035e2ef4be933b970839d22d49509ebba063cd1603c5` |
| `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r4-remediation-handback.md` (this file) | see the final response | — | A file cannot carry its own hash; the final response gives it. |

The four pointers (`docs/review/Handover information`, `docs/project-management/status.md`, `docs/implementation-plan.md` §20 and the banner of `docs/operations/disposable-test-server.md`) were replaced last; their final sizes and hashes are given in the final response, not here.

**Files created:** this handback and four snapshots of the R4-authorization pointers, created and verified identical to their sources before any pointer was replaced:

| Snapshot | Lines | Bytes | SHA-256 |
|---|---|---|---|
| `docs/review/Handover-information-through-2026-10-09-lit-full-wp2-r4-authorization.md` | 46 | 2898 | `9914bfafbf9b133ca56a506efc4ba157346acc881767beba9e7cb899869b5b6b` |
| `docs/project-management/status-through-2026-10-09-lit-full-wp2-r4-authorization.md` | 55 | 3282 | `999d6b7d30daf149cd22c7b60c0ec87286b6185569c36eb5d5aa9c1ef60f2402` |
| `docs/implementation-plan-through-2026-10-09-lit-full-wp2-r4-authorization.md` | 56 | 3476 | `bf77a0c638f9e0ab9c0d6922c9885b9d7089547725d81fae9c08c245f3fd00f1` |
| `docs/operations/disposable-test-server-through-2026-10-09-lit-full-wp2-r4-authorization.md` | 46 | 2914 | `333657bcf9268d39bdf0d0990a647aeacb7343fa2cea122c5646e61de4ecb63c` |

**Files edited:** the inventory; the four pointers; and the four archive indexes (`docs/review/handover-archive/README.md`, `docs/project-management/status-archive/README.md`, `docs/implementation-plan-archive/README.md`, `docs/operations/disposable-test-server-archive/README.md`), each with one new row carrying the snapshot's SHA-256, added before its pointer was replaced. No other file was edited.

## 4. Corrected counts

Produced by a read-only parser over the §§4–5 tables, run before and after; no count was edited by hand. The parser reproduced every R3 figure and the inventory's own §11.3(d) identifier table before the edit (no mismatch), and the table still matches after.

| Quantity | R3 | R4 | Effect of `RT3.SN.1` |
|---|---|---|---|
| Total rows | 317 | 318 | +1 |
| Operation / contract / composition rows (gap row excluded) | 316 | 317 | +1 |
| Class CN | 62 | 63 | +1 |
| RT-3 rows | 14 | 15 | +1 |
| Procedure subtotal | 173 | 174 | +1 |
| Shared-helper subtotal | 144 | 144 | 0 |
| Tag [A] only | 237 | 238 | +1 |
| Tags [A]+[Q] / [M] / [Q] alone | 73 / 6 / 1 | 73 / 6 / 1 | 0 |
| RT-3 steps | 13 | 14 | +1 (`SN`) |
| Steps in all procedures | 76 | 77 | +1 |
| Taxonomy rows 1, 2, 3, 3a, 3b, 3c, 3d, 3e, 3f, 3g | 36, 29, 19, 14, 14, 16, 16, 16, 13, 17 | 37, 30, 20, 15, 15, 17, 17, 17, 14, 18 | +1 each |
| Every other taxonomy row (4 … 22) | unchanged | unchanged | 0 |
| §11.3(d) identifier citation counts | — | unchanged | 0 (the row cites none of the table's identifiers) |
| §11.4 question rows (Q6-6 5, Q6-7 3, all others) | — | unchanged | 0 (no Q tag) |
| Logical accepted call sites (§7.1) | 41 | 41 | 0 (DI-1 23, DI-2 1, DI-3 1, DI-4 3, DI-5 6, DI-6 6, DI-S 1) |
| Other classes | — | unchanged | 0 |

Total rows rise by one because exactly one row was delivered. The R3 BS-4 correction is untouched: SN-10 / A-I-16 apply only to AK-1, BS-2 and BS-3; BS-4 remains the third DI-4 site (`CALL-DI4-03`) under the open Q6-7.

## 5. Checks run and not run

**Run (read-only):** the complete source reading and ledger; snapshot-to-source byte comparison (`cmp`); the table parser, before and after the edits; whole-file searches for the withdrawn formula, stale 317/316/76/173 figures, and "four SN rows"; the link check (§9); `git diff --check`.

**Not run:** no test suite, build, formatter, linter, package, service, database, SSH or network operation (none is authorized, and none is relevant to a Markdown-only change). `python3 .claude/hooks/test_guards.py` was not run; no hook was changed.

## 6. Unresolved questions and observations (not repaired)

- Q6-6 and Q6-7 are unanswered and carried unchanged. No WP-3 … WP-7 question was answered and nothing was designed.
- Observation: D R4 (g) AR-4 states the withdrawn formula as design text; R8 §7.7 W-7 withdraws it and §7.6 N1 replaces it. The inventory now follows R8. The design text itself was not touched.
- Observation: the R3 handback's scratch parser reported RA-E as 0; the table's 1 (`H-SN.6`) is correct.
- Observation: carried historical R2/R3 revision records and reviewer-focus paragraphs still say "four SN rows" or give R3 totals; they are labelled as carried and state R3 figures.
- No newly discovered conflict was found.

## 7. No-prohibited-action statement

No host, SSH, retained-evidence, secret, network, package, service or database access occurred. No cleanup, workspace recreation, implementation, configuration, launcher work, build, test, formatter, H-1/H-2, OH-S4/OH-S4p or later slice, WP-3 … WP-7 work, activation, rollback, commit or push took place. No subagent was used. No earlier snapshot, accepted record, prior handback or review, application file or the R5/H-0G retained paths was changed.

## 8. Reviewer focus

1. `RT1.FI.2` and the §11.1 `T_s` row: only finite, class M and N1 remain; N1 is necessary-only.
2. `RT3.SN.1`: grounded only in accepted text (R8 §7.5a.7, §7.5a.8 last paragraph, §8.1), two tiers, owner chain verbatim, no Q tag, no DI-3/DI-4.
3. The count effect in §4 is exactly +1 row, +1 step and +1 in rows 1, 2, 3 and 3a … 3g.
4. R3 BS-4 correction and Q6-6/Q6-7 text are unchanged.

## 9. Terminal link-check result

Reserved field (non-link-bearing). Scope: 14 link-bearing files (the corrected inventory, this handback, the four return pointers, the four R4-authorization snapshots and the four archive indexes), every relative Markdown link resolved against the file's own directory. Result after the field was populated and the identical check rerun: **246 links checked, 0 broken, exit 0**. The same check before the field was populated also gave 246 links, 0 broken, exit 0. No link-bearing content changed after the rerun.
