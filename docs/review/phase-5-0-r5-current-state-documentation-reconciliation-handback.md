# Handback — R-5 current-state documentation reconciliation

Work ID: `C-P5.0-R5-DOC-R1`

Date: 2026-10-01

Assignee: Claude

Controlling prompt:
[`phase-5-0-r5-current-state-documentation-reconciliation-claude-prompt.md`](phase-5-0-r5-current-state-documentation-reconciliation-claude-prompt.md)

Status: **documentation reconciliation complete; Claude has stopped.** This
record creates no authority, accepts nothing and does not review or use any
result of Gemini's concurrent R4 task.

## 1. Summary

The canonical handover, status, implementation-plan §20 and disposable-server
restriction banner described Gemini's R2 remediation as the current action.
They now state that R2 and R3 are complete, that Peter accepted R3, and that
Gemini's bounded R4 `cc1.v` baseline recovery is the current action, with its
restrictions and stop conditions. Each displaced canonical file was first
preserved as a byte-identical snapshot and hash-indexed. One change-log row and
one decision-register entry summarize the accepted R3 decision and the R4
authority.

No technical decision, finding, gate, authority or disposition was changed.

## 2. Files changed and SHA-256

Before hashes were recorded from the worktree, which already held accepted
uncommitted work, immediately before the first edit.

| File | Before SHA-256 | After SHA-256 |
|---|---|---|
| `docs/review/Handover information` | `7e8a8e16440c3ec0c8e368eafb40bb3023f1b28e1a3362d3aa811fe42f1f3ef5` | `961b9da69b50204bc58a869972b797d5821201e9fac95325c50b7631c16d317a` |
| `docs/review/handover-archive/README.md` | `cbccd58d168254ee4d6d7a2447541d47c12ca761447b3e7f08da478e15973985` | `2aa7b17c13c5cc22fca8add145bea886bf4d06aa351acae28963b577e9c25ed1` |
| `docs/project-management/status.md` | `ee3ba027539239e6b25207e5eeec84e58d57190fad9d07bf2d51d85eea6724f7` | `b64e4c12594d14504c8a1806a496ab6aaed371214f4e2076c9c56e4ffc7c04c8` |
| `docs/project-management/status-archive/README.md` | `79fde38672d4253e58f67450891ebafb0b867dd64972a3fe4b35ffcc17b3ce53` | `1cb0c3ee5bfa0663e9e1f1e9407349819492d00b524e515915501529ac052cff` |
| `docs/implementation-plan.md` (§20 only) | `d22cf9626a34a322e56dcd4375318eaab4a07d8d1a3c7cbe3cd3ebe006307990` | `d96efd8c7ecaa435d4e305ec3f31be1e297772086ddc0711c3d3b888a8e36f42` |
| `docs/implementation-plan-archive/README.md` | `c3b85739b8ec85bc890eb9d711c236bdf7318a879020181eacc7dccf87a47a7c` | `a85811eeab3167ca3c44632aa59299bd4f3c8053971a13b8616dc24cdcca356a` |
| `docs/operations/disposable-test-server.md` (banner only) | `c422f0b39a5db782decd26fdce8376a702e12482e6930a2896e3d02c1c7f9222` | `42dee893942980485ec4de410fe25a73b63fc63aa5e6b5297843f81c14324a84` |
| `docs/operations/disposable-test-server-archive/README.md` | `2417e951f86266cd7d69294af98802c993b059197d3b9d91d5c8392f3c65ad3b` | `0ac6ec07c6ace1f3f0e9c707e35204fd9f1353d9f0627ef99128d26e4d980c9b` |
| `docs/project-management/change-log.md` | `9329133c17c073a741322b5f8ad7e79cc05eb045460588b49a1efae4a9393a68` | `36c64468d4225d3bf014441137165ec2be05d510d6d86a3755c7d7b415490280` |
| `docs/project-management/decision-register.md` | `64dceee513c0a2455943dced78bb578bdcccf6879191c149d3bf628faa571fde` | `9055681c861e742b23b667777085f347ef1ad83998b0e7d09ccf7925316ac9ed` |

New files: the four snapshots in §3 and this handback.

Scope checks against the snapshots: `diff` shows the implementation-plan
changes confined to lines at or after `## 20. Immediate next actions` (line
2549), and the disposable-server changes confined to the restriction banner and
its archive-pointer line.

## 3. Archive snapshots and indexed hashes

All four snapshots use the prescribed suffix
`through-2026-10-01-r5-r3-acceptance`; no same-day name collided. Each is a
complete copy of its canonical file, placed beside it so relative links still
resolve, matching the existing complete-file convention (for example the
`d2-r2-acceptance` snapshots).

| Snapshot | Canonical before | Snapshot bytes | Index row | Result |
|---|---|---|---|---|
| [`Handover-information-through-2026-10-01-r5-r3-acceptance.md`](Handover-information-through-2026-10-01-r5-r3-acceptance.md) | `7e8a8e16…3ef5` | `7e8a8e16…3ef5` | `7e8a8e16…3ef5` | equal (`cmp` and SHA-256) |
| [`status-through-2026-10-01-r5-r3-acceptance.md`](../project-management/status-through-2026-10-01-r5-r3-acceptance.md) | `ee3ba027…24f7` | `ee3ba027…24f7` | `ee3ba027…24f7` | equal |
| [`implementation-plan-through-2026-10-01-r5-r3-acceptance.md`](../implementation-plan-through-2026-10-01-r5-r3-acceptance.md) | `d22cf962…7990` | `d22cf962…7990` | `d22cf962…7990` | equal |
| [`disposable-test-server-through-2026-10-01-r5-r3-acceptance.md`](../operations/disposable-test-server-through-2026-10-01-r5-r3-acceptance.md) | `c422f0b3…f9222` | `c422f0b3…f9222` | `c422f0b3…f9222` | equal |

Full 64-character values are in §2's "before" column and in each archive index.

Navigation: each canonical file links to its new snapshot and archive index.
The plan and disposable-server pointers also keep their existing link to the
older `d2-r2-acceptance` full-history snapshot. Each archive index links back
to its canonical file or names it, as the existing indexes do.

**Archive necessity.** An archive was required in all four cases. AGENTS.md
"Current-state documents and archives", plan §0.2 and §16.3 all require
displaced current-state text to be preserved verbatim and hash-indexed, and
no index said otherwise. The change-log and decision register are
append-only, so their new entries needed no snapshot.

## 4. Current-state statements reconciled

Handover, status, §20 and the change-log/decision-register entries now
consistently state the following. The disposable-server banner states the
subset that applies to the server:

1. R2 introduced the same-invocation R-1/R-2 gate and withdrew the erroneous
   R-5 PASS.
2. R3 removed the unsafe causal regex override, making byte equality the only
   route to `PASS`. Peter accepted it on Codex's independent recommendation.
3. Codex reproduced 4,019 passing repository tests, with 12
   toolchain-dependent skips because no accepted local root was available,
   plus clean compilation, byte-range checks and `git diff --check`.
4. Gemini R4 is the current action. It is limited to recovering Claude's
   historical `cc1.v` with exact SHA-256
   `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`.
5. R4 authorizes no rebuild, baseline reproduction, SSH, `oracle-test`,
   download, provisioning or R-5 rerun.
6. If the exact bytes are not recovered, Gemini writes a handback and stops.
7. Success authenticates only the historical artifact. It does not explain
   Gemini's differing `cc1.v` and does not accept R-5.
8. R-5 remains stopped, Blocking and unaccepted. RP-11 remains unwired and
   unmet, `plan.is_executable=False`, and Package 5.0 remains not ready.

Stale current-tense wording that was made historical:

* in `status.md`, "Gemini may perform only that bounded run" and "Peter
  narrowly authorizes";
* in §20, "Peter narrowly authorizes" and "Gemini is now authorized to
  perform that bounded R-5 run". The second was replaced by "No R-5 rerun is
  authorized".

The handover's accepted LD-7/LD-8/LD-9 and I-7-R1 sections are unchanged. The
former "Current action and restrictions" section is replaced by an "R-5
history to date" section and a new R4 current-action section.

## 5. Verification

| # | Check | Command / method | Result |
|---|---|---|---|
| 1 | Relative Markdown links | Python resolver over every `](…)` target in the 10 edited files | 331 links checked, 0 broken. In this handback, every real link resolves; the only unresolved match is the literal `](…)` notation in this row |
| 2 | Snapshot equals pre-edit canonical | `cmp` immediately after copy; SHA-256 compared with the recorded before hashes | 4/4 equal |
| 3 | Index hash equals snapshot bytes | SHA-256 of each snapshot compared with the value parsed from its index row | 4/4 equal |
| 4 | No surviving claim that R2 or R3 is active | `grep -Ei` for R2-prompt/remediation, "is assigned a repository-only", "now authorized", "may perform only that bounded run", "narrowly authorizes", "Restriction during R-5 R2" across the handover, status, banner and §20 | 2 hits, both past-tense history of the completed R2 |
| 5 | No implied R-5 acceptance or host authority | `grep -Ei` for "R-5 accepted", "rerun authorized", "authorized to rerun/rebuild", "R-5 passed" | 1 hit: the negation "No R-5 rerun is authorized" |
| 6 | Documentation-focused structural test | `env -u TEST_DATABASE_URL /opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/test_filesystem_layout.py` on the repository host | **5 passed, 0 skipped**, 2 pytest config warnings (unknown config option) |
| 7 | Whitespace | `git diff --check` (tracked files); `git diff --no-index --check /dev/null <file>` for each new snapshot | Clean; 0 issues in each snapshot |

`tests/test_filesystem_layout.py` is the only structural test I found that
reads these governance documents. It checks the entry points' links to the
disposable-server document. A grep found no test or review manifest that
hashes any edited file.

## 6. Concurrency and Gemini-owned paths

* Before the first edit I captured `git status --porcelain=v1` (50 entries).
  I compared it again before the status, change-log/decision-register and
  handback writes. Each time, the only differences were my own four new
  snapshots. Before each edit I re-verified every Claude-owned file against its
  recorded before hash, and every check matched. No collision occurred.
* `infra/rp11-launch/verify/fixtures/cc1.v.baseline` did not exist at any
  check, including the last one.
  `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r4-cc1-baseline-recovery-handback.md`
  first appeared as an untracked file at the final check, after all my
  canonical edits were complete. Gemini created it concurrently. Claude did
  not open, read, create, modify, delete, rename, stage or format either path.
  The R4 handback's existence and content were not used in this reconciliation.
* No file below `infra/rp11-launch/` or `tests/` was modified. Their
  `git status` entries are unchanged from the initial capture.
* The R3 acceptance record and the R4 prompt were read only.
* Nothing was staged, committed or pushed.

## 7. Checks not run and why

* The full bot, web and Foundry suites, the evidence-harness suite and the
  launcher suites were not run. Only documentation changed, and the prompt
  allows documentation-focused tests only. The 4,019/12 figure is Codex's
  reproduced result, cited from the accepted R3 decision. It is not a fresh
  result from this task.
* Nothing ran on `oracle-test` or against a database, and nothing used SSH,
  synchronization, a package operation, a download, a build, harness
  `--execute` or a secrets scan. The prompt forbids all of them.
* Gemini's R4 result was not reviewed or incorporated, as the prompt §6
  requires.

## 8. Security, configuration, deployment and rollback

* **Security:** documentation only. No secret, credential or protected
  artifact was read or written. The new text narrows rather than widens stated
  authority. The disposable-server banner still forbids every action on
  `oracle-test`.
* **Configuration / deployment:** none.
* **Rollback:** delete the four new snapshots and this handback. Restore the
  ten edited files from their snapshots, or reverse the edits, and verify them
  against the "before" hashes in §2. The four canonical files can be restored
  byte-for-byte from the snapshots. The four index README files can be
  restored by removing their last table row. The change-log and
  decision-register can be restored by removing the single entry each.

## 9. Proposed independent-review focus

1. Check that the handover, status, §20 and the banner do not imply R-5
   acceptance, a rerun or any host authority beyond the R4 prompt. In
   particular, check the banner's wording that R4 "allows only read-only
   recovery … from bounded local sources".
2. Check that the R3 and R4 summaries in the change-log and decision register
   match the R3 acceptance record and the R4 prompt, and add nothing to them.
3. Confirm by `cmp` or SHA-256 that the snapshots match their index rows.
4. Confirm that the past-tense rewording of the bwrap and R-5 assignment
   sentences in `status.md` and §20 preserves the historical facts.

## 10. Stop gate

Claude stops here. Claude has not reviewed or acted on Gemini's R4 result,
authorized an R-5 rerun or advanced any package.
