# WP-2 R5 remediation handback — 2026-10-09

**WP-2 R5 REMEDIATION RETURNED — INDEPENDENT RE-REVIEW PENDING.**

Work ID `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R5-20261009-19`. Executor: Claude. Accepted assignment: [WP-2 R5 remediation prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5-remediation-claude-prompt.md) (250 lines, 13,757 bytes, SHA-256 `8451d7157c5bf6245bf87ca6ed6fc109421460b7255a6efd3c05d58013d73b9e`), activated by [the R5 acceptance record](project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5-remediation-acceptance-and-claude-activation.md).

This return does not accept WP-2, authorize WP-3, establish concrete Route 3 or select LIT-FULL for implementation. Baseline v1.8, the F-1 combination (B2-F), EX-1 and EX-2 (no EX-3) and the no-host restriction are preserved. WP-3 through WP-7 remain separately gated. A clean independent Codex re-review of the complete R5 return and Peter's later acceptance are required before any WP-3 prompt or authority may be prepared.

## 1. Finding and remediation

| Finding | Remediation |
|---|---|
| `WP2-R4-1` (Blocking) — `RT3.SN.1` conflated recovery of the interrupted stop-post cleanup (the backstop's CL, then CP, then the boot, then `attest`) with the accepted R8 SN-RO ownership of a child left behind by stop-post | The `RT3.SN.1` row of the cumulative inventory was rewritten in place. (1) *Owner:* PID 1, which sends `FINAL_SIGTERM` and, after another S, `FINAL_SIGKILL` to “what remains” (R8 §7.5a.7 table SN-RO, stop-post CL row; R2 §8 (e)); whether “what remains” includes a `setsid` child is PO-SN (e) and the row adds nothing to it; the boot is a separate recovery event (IS-7); `attest` has no automatic owner of the child. (2) *Observer contract, stated separately:* CS-7, CS-8 and CS-10 leave a line; CS-1 … CS-6 and CS-9 leave only the missing `run-end`; the backstop's CL or `attest` may record `children-unknown` and does nothing else; no later procedure searches for, signals, reaps or acts on the child (SN-9). (3) *Cleanup-state recovery* is no longer in the row; it stays, unchanged, on `RT3.FI.2` and `RT3.CLG` … `RT3.CLOUT` and is not described as child ownership. The blocking cell now says E, X, C for the helper's own waits and class M for PID 1's `FINAL_SIGTERM` / `FINAL_SIGKILL` (taxonomy row 3f): a send is not proof of exit and no elapsed bound is claimed. The title, status line, work-ID chain, an R5 revision record, the R4 record label (its owner sentence is marked superseded), the §14 pointer and snapshot checklist lines and the §15 reviewer focus were reconciled. The R4 prompt's instruction that named the chain as the child's owner was superseded because it conflicted with accepted R8; the R4 prompt was not altered. |

## 2. Pre-edit reading ledger

All 34 items below were read as specified, first byte through EOF (items 2 and 4 in their required portions: the plan's reading map, §0, §16 and §20; the full banner of the test-server document), **before the first edit**. The values are those read. After the reading, and before the first edit, the line and byte counts matched the first listing. At return, every item except 2, 3, 4 and 18 re-verifies at the SHA-256 shown; those four are the files this assignment edits, and their final values are in §3.

| # | Path | Lines | Bytes | SHA-256 |
|---|---|---|---|---|
| 1 | `.agents/AGENTS.md` | 700 | 36014 | `87bab4ab8d67e308af0c59b99c8604235ee84d75cfa12448458b1a04cc88390a` |
| 2 | `docs/implementation-plan.md` | 2614 | 128781 | `e17a5980a0d3b848c7d411101cb7ebea905c6aeadaccdca6a268e7f1cb30ff9d` |
| 3 | `docs/review/Handover information` | 48 | 3127 | `6bf9f56ebb660495821fd9a9acc1ddfb3f3c88b2d09fc8ca1aafbc3be504dd4e` |
| 4 | `docs/operations/disposable-test-server.md` | 334 | 15762 | `b290e883db80c4d28eb5161ecc79638de9daad0b12fac29ce15fa413ce6b1368` |
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
| 18 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md` | 1440 | 227365 | `a981534baba73012ef70035e2ef4be933b970839d22d49509ebba063cd1603c5` |
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
| 31 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r4-remediation-handback.md` | 125 | 14787 | `92cedbf2a37336c2d47015d22648a93a1f71a4fb846d59a7138f5cdefbfad897` |
| 32 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r4.md` | 124 | 6507 | `2848f3ad6ba17fa445dd98c0c0323822248313c80f433affcadab00796eeda6c` |
| 33 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5-remediation-claude-prompt.md` | 250 | 13757 | `8451d7157c5bf6245bf87ca6ed6fc109421460b7255a6efd3c05d58013d73b9e` |
| 34 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5-remediation-acceptance-and-claude-activation.md` | 68 | 3482 | `cee3a575aac3c933d69a3a008b67ef1bdb8468cece5dcad00c2c2f28a3c11251` |

## 3. Deliverables, edits and metrics

Created: this handback and the four `lit-full-wp2-r5-authorization` snapshots. Edited: the cumulative inventory, the four archive indexes (one top row each, with SHA-256) and the four current-state pointers (`docs/review/Handover information`, `docs/project-management/status.md`, §20 of `docs/implementation-plan.md`, and the banner of `docs/operations/disposable-test-server.md`). The snapshots are verbatim: the whole handover and status files, the §20 block from its heading to end of file, and banner lines 1–46. This handback's own line count, byte count and SHA-256 are not self-referential and are not stated.

| Path | Lines | Bytes | SHA-256 |
|---|---|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md` | 1450 | 230574 | `da341efb8c29b862d63c1463e981ccfedbe1f6680de2d416ff285fdae06461fd` |
| `docs/review/Handover information` | 51 | 3330 | `22c9927147d7a5c7fbb8cf98dc1e9a830c76375b328b936d2cc49d6de860a758` |
| `docs/project-management/status.md` | 60 | 3725 | `e6f8c835332c53e4c0693a9487b8debe6434809e37288504d09ad856e3fcb830` |
| `docs/implementation-plan.md` | 2620 | 129195 | `b808284c08141c6218a101a40790306e0cd82ed5c7fa171ba750ffba51af2055` |
| `docs/operations/disposable-test-server.md` | 340 | 16188 | `49f50fb8ad5143b5516f017183b4432d030975d0ab216568883b6dbe7236614b` |
| `docs/review/Handover-information-through-2026-10-09-lit-full-wp2-r5-authorization.md` | 48 | 3127 | `6bf9f56ebb660495821fd9a9acc1ddfb3f3c88b2d09fc8ca1aafbc3be504dd4e` |
| `docs/project-management/status-through-2026-10-09-lit-full-wp2-r5-authorization.md` | 54 | 3299 | `54af253cd6e02ab3c523547916162e60bf125866a64aa14063ebb9cd0b79ad21` |
| `docs/implementation-plan-through-2026-10-09-lit-full-wp2-r5-authorization.md` | 56 | 3557 | `1daf220a4750d66cc0b0a296801ad48b69ca91d9db992d9853c540fc0709d489` |
| `docs/operations/disposable-test-server-through-2026-10-09-lit-full-wp2-r5-authorization.md` | 46 | 2998 | `d35390e9fb2e5d0608061bc8d2c5fa31bd535f1d063807df8cf1f16951a39674` |
| `docs/review/handover-archive/README.md` | 68 | 19280 | `72471f42019f619e76d0379ab9fb84ea9506bbd0f0325e1cb00a8092ae2a82e7` |
| `docs/project-management/status-archive/README.md` | 67 | 17374 | `3d272784331a209e67681927e294df46a8232a2668011606fe7c5d1d44e9ec48` |
| `docs/implementation-plan-archive/README.md` | 54 | 15933 | `25cf936bf3c03c1f4c3b8cea85a57a3f53f1f3ed455297a5a50d65cefa6a05f8` |
| `docs/operations/disposable-test-server-archive/README.md` | 55 | 16075 | `d9e359704dbccdced43c86ca0df6c34eb854441fb33cc0b0888a8238f87496a6` |

## 4. Reconciled counts

The counts were re-derived by a read-only parser over the delivered §4 and §5 operation tables. **The correction changes none of them.** Rows 318; classes CN 63, CMP 36, GAP 1; RT-3 rows 15; tag [A] only 238, tag [M] only 4; Q6-6 on 5 rows and Q6-7 on 3 rows; steps 77; taxonomy rows 1, 2, 3 and 3a … 3g, the DI sites (41), the identifier citations and the 24 deferred questions are as in R4. No row, step, tag or question was added or removed. The one row changed in substance is `RT3.SN.1` (its text and its blocking cell); `RT3.FI.2` and the `RT3.CL*` interruption cells were not touched.

## 5. Checks

Run: reading, searching and mechanical Markdown-table parsing; `wc -l -c`; `sha256sum`; `git diff --check` (clean on the edited files); read-only Git status; the terminal link check below.

Not run, and why: application and hook suites, builds, formatters and linters (outside this authority; they cannot prove a documentation-only change); any host, network, package, service or database operation (prohibited).

**Terminal link check:** scope = the 14 delivered files that can carry links (the cumulative inventory, this handback, the four R5-return pointers, the four `lit-full-wp2-r5-authorization` snapshots and the four archive indexes); every relative Markdown link target checked for existence; run once with this field reserved and rerun unchanged after it was populated; result both runs: 14 files, 277 links, 0 broken, exit 0. No link-bearing content changed between the runs.

## 6. Unresolved later-package questions and newly observed matters

Q6-6 and Q6-7 remain unanswered, as do all 24 deferred questions of §12; none was answered. No newly discovered conflict or omission was found outside `WP2-R4-1`. `RT5.SN.1` keeps “no unit owns it” for `attest`, which agrees with `RT5.PRE.3`; the other SN rows keep their PID-1-end-of-unit-then-boot form and were not changed. No `HARD STOP` applies.

## 7. Prohibited operations

No SSH or host connection, retained-evidence, secret, network, package, service, database, build, test, formatter, cleanup, workspace-recreation, H-1/H-2, OH-S4/OH-S4p or later, WP-3 through WP-7, activation, rollback, commit or push action occurred. The R5 and H-0G retained paths were not touched. No earlier handback, review, prompt, activation record, accepted record or historical snapshot was edited.

## 8. Reviewer focus

- Confirm that `RT3.SN.1` states PID 1's `FINAL_SIGTERM` then `FINAL_SIGKILL` after another S to “what remains” as the owner, adds nothing to PO-SN (e), treats the boot as a separate event and gives `attest` no automatic owner.
- Confirm that the observer contract is separate and never an action on the child, and that the backstop/CP/boot/`attest` chain appears only as cleanup-state recovery on `RT3.FI.2` and `RT3.CLG` … `RT3.CLOUT`.
- Confirm the class-M reading of PID 1's signalling and that no elapsed bound was introduced.
- Confirm that no count changed, and that every R1 … R4 correction is intact.
