# Handback — OH-S3 R8 remediation: `HARD STOP: concrete Route 3 not established`

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R8-20261007-08`

Date: 2026-10-07

Executor: Claude Code (Sonnet 5.5) on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-claude-prompt.md),
**12733 bytes, SHA-256
`1dd1c57124f72fd6cafb33fc8d2a7142fa4b9bfe7d2c7f2928466f19212e40e7`**, recomputed
with `wc -c` and `sha256sum` before any edit and again at handback, and equal to the
pin in the
[authority record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r8-remediation-authority.md).
**The prompt and the authority are consumed by this return.**

Deliverable: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md).

## 1. Terminal state

**`HARD STOP: concrete Route 3 not established`.** The prompt identity matched, so the
identity hard stop did not arise. The second defined hard stop, `HARD STOP: OH-S3 R8
remediation requires maintainer direction`, **did not arise**: closing R8-F1 and R8-F2
needed no scope or design decision beyond this assignment, and no kernel, language or
systemd behaviour was researched or invented. The conditional hard stop of the OH-S3 R2 …
R7 proposals **remains in force and is unchanged**.

**Nothing is accepted by this return.** I have not claimed Codex's or Peter's acceptance,
have not proposed any successor for activation, have made no scope decision and have created
no authority. R1 through R7 are unchanged, unaccepted and historical.

## 2. Findings remediated

| Finding | Disposition | Proposal |
|---|---|---|
| **R8-F1** (Important): the grace-deadline invariant conflates the child's durable S0 history with the current SN invocation | **Closed in the proposal, not accepted.** Two scopes are now defined and kept apart in §7.5a.6e. **History (per child, durable):** `s0_ran` is true **if and only if S0 has ever run for the child**; S0 sets it and no later SN invocation resets, clears or reinterprets it (GD-1); `grace_deadline_ms` is the integer iff `s0_ran`, otherwise `null` (GD-2, the check `s0_ran == (grace_deadline_ms != null)` is unchanged). **Invocation (per SN call):** S0 runs on a call only for a `running` handle at SN's entry, hence at most once per child, because every SN call ends at S7 with the handle settled (GD-4, rewritten). The §7.5a.6e **path table has separate columns** for "S0 ever ran for this child", "S0 runs on this call", "new `t_g` reads on this call" and "`t_g` reads over the whole life", and the **settled-handle row is split in two**: (a) a handle **settled before any S0** keeps `false` / `null` / 0 reads; (b) a handle **settled after an S0** (abandoned at S6, or reaped, or `reap-unknown`, in that sequence) keeps `true` / the recorded integer / 1 read. **New GD-6:** a settled-handle re-entry of either history runs no S0, reads no new clock or `t_g`, writes no second line, starts no grace period and changes neither field. **INV-26** (rewritten) and INV-22 no longer say that a settled handle reads no `t_g`: they say the re-entry reads no *new* one. The vocabulary row, SN-6, WB-1, the S0 and S8 rows of table SN-S, RE-4, §7.5a.9, §8.5, NT-WB-11 (i), NT-GD-2 … 4, NT-NS-1 … 3, Q22, SR-15, A-I-16, A-I-17, B-08, B-13 and Appendix D follow; **W-19** withdraws the unqualified R7 sentences. **NT-GD-5 (new)** steps both settled histories (before any S0; abandoned, `reap-unknown` and reaped after an S0) through a re-entry at every position. The pre-S0 `reap-error` path, a child reaped within c, spawn failure, every post-S0 path and every settled re-entry were rechecked path by path: **no send, wait, outcome, fail-closed behaviour, parameter, class, field or obligation changed** | §0.1, §0.2, §0.10, §1.1, §1.3, §3, §7.5a.4, §7.5a.6, §7.5a.6a, §7.5a.6d, §7.5a.6e, §7.5a.9, §7.7 (W-19), §7.9, §7.12, §8.5 … §8.7, §13.2, §14, Appendices A … D |
| **R8-F2** (Optional): the four canonical current-state narratives place R7 before the R5 and R6 records that produced it | **Closed in the four pointers, not accepted.** In `docs/review/Handover information`, `docs/project-management/status.md` and §20 of `docs/implementation-plan.md` the R5 and R6 blocks were moved (verbatim, by line range) from after the R7 and R8 blocks to between R4 and R7, giving **R1 → R2 → R3 → R4 → R5 → R6 → R7 → R8 return**. The R8 block was changed from "authorized and unexecuted" to "executed; its authority and prompt are consumed", with the prompt identity and the links to the proposal and this handback. In §20 the standing restriction paragraph ("No host or retained-evidence access …"), which the other two pointers carry directly after the R1 block, was moved from after the R3 block to directly after the R1 block, for the same reason. **In the restriction banner of `docs/operations/disposable-test-server.md` no block was moved: it already narrated R1 → R2 → R3 → R4 → R5 → R6 → R7 in order**, so only its heading, its R8 paragraph and its link rows changed | §3 and §5 of this handback; proposal §0.1, §0.10 (*R8-F2*), §14.1 Q25 |

The proposal's Appendix D maps every numbered item of both findings to its closing section.

## 3. The four pointers: what moved, what changed, what was preserved

| Pointer | Moved | Changed | Style kept |
|---|---|---|---|
| `docs/review/Handover information` | R5 block (lines 149 … 171 before) and R6 block (173 … 202) moved to follow R4; R7 block (103 … 129) then R8 (131 … 147) follow | heading "authorized and unexecuted" → "returned for independent Codex re-review"; R8 execution paragraph; R8 link rows (proposal, handback, *Consumed* authority, *Consumed* prompt) | bare relative file names, `- [..]` list |
| `docs/project-management/status.md` | R5 (141 … 163) and R6 (165 … 194) moved to follow R4; R7 (100 … 125) then R8 (127 … 139) follow | heading; R8 execution paragraph; link rows | `../review/…` links, `·` list |
| `docs/implementation-plan.md`, §20 only | R5 (2688 … 2710) and R6 (2712 … 2741) moved to follow R4; R7 (2648 … 2672) then R8 (2674 … 2686) follow; the standing restriction paragraph (2620 … 2624) moved up to follow R1 | R8 execution paragraph; link rows. The section heading `## 20. Immediate next actions` is untouched | `review/…` links, `·` list |
| `docs/operations/disposable-test-server.md`, banner only | none | banner heading line; the R8 paragraph; link rows | `../review/…` links, `·` list |

**Preservation check** (a script that compared each pointer, before and after, over the multiset of
lines and over the sets of work IDs, 64-hex-digit identities, Markdown link targets and finding IDs):
the only lines that left each file are the R8 "authorized and unexecuted" paragraph, the heading and
the two *Authorized* link rows (their targets remain, relabelled *Consumed*); **every work ID
(8, 8, 8, 7), every SHA-256 identity (8, 7, 7, 5), every finding ID (16, 16, 16, 10) and every
earlier link target is still present**; the added links are the proposal and this handback. The
first-appearance order of the OH-S3 work IDs is R1, R2, R3, R4, R5, R6, R7, R8 in all three pointers
that had been out of order (the banner begins at R2 because it carries no R1 work ID, as before).
No archive, prior proposal, prompt, authority or handback was edited.

*Observation, not changed:* the banner's link list has no *Consumed OH-S3 R1 prompt* row, which the
other three pointers carry. It was missing before this assignment; adding a link is outside "restore
causal order and add the R8 return", so I left it and report it here.

## 4. Files changed

**Created** (untracked):

* `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md`
* `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-handback.md` (this file)

**Updated, current-state pointers only** (tracked; the OH-S3 narrative, heading and links):

* `docs/review/Handover information`
* `docs/project-management/status.md`
* `docs/implementation-plan.md`, §20 only (every changed line lies after the
  `## 20. Immediate next actions` heading)
* `docs/operations/disposable-test-server.md`, the restriction banner and its link list only

**Pre-existing worktree changes.** Before my first edit `git status --short` showed **36**
entries: six modified tracked files (the four pointers above, plus
`docs/project-management/change-log.md` and `docs/project-management/decision-register.md`) and
thirty untracked files (the R1 through R7 prompts, handbacks, proposals and authorities, and this
assignment's prompt and authority). All were left by earlier work. The four pointers already
carried the uncommitted "OH-S3 R8 authorized" text, which I edited in place and otherwise
preserved. **I did not touch** `change-log.md`, `decision-register.md`, any R1 … R7 file, this
assignment's prompt or its authority.

**Not edited:** R1 through R7 proposals, handbacks, prompts and authorities; any accepted
historical evidence; the operational draft; any source, test, configuration, service file or
migration; any archive snapshot or archive index; the decision register; the change log.

## 5. Repository documents consulted

**Read completely:** `.agents/AGENTS.md` (700 lines); the R8 prompt (224 lines) and its authority
(37 lines); the R7 prompt (235 lines) and its authority (37 lines); `docs/review/Handover
information` (242 lines before editing); `docs/project-management/status.md` (231 lines); the
restriction banner of `docs/operations/disposable-test-server.md` (lines 1 … 200, which contain the
whole banner); the R7 handback (328 lines); and the **complete R7 proposal** (4,544 lines, read in
passes, section by section: §0, §1, §2, §3, §4, §5, §6, §7 with §7.5a, §7.9 and the whole of §7.12,
§8, §9 … §12, §13, §14 and Appendices A, B, C and D). The R8 proposal began as a byte-identical copy
of the R7 proposal, and the R8-versus-R7 differences are listed in proposal §0.10.

**Read by section:** `docs/implementation-plan.md`: the reading map (lines 19 … 51), §0.1 … 0.5
(53 … 183), §14.1 … 14.3 (2216 … 2250), §16 in full (2394 … 2490), §17 (2492 … 2511) and §20 in
full (2558 to the end).

**Read at the exact text named:** the R6 proposal's table SN-S rows S0, S1, S7 and S8, WB-1, §7.5a.9,
the *Before T0* paragraph of its IM-S and INV-22 (lines 2123 … 2131, 2149 … 2153, 2382 … 2398,
2693 … 2703, 3110), to confirm that the repair preserves the R7 corrections; the R4 proposal's table
SN-S step S0 and WB-1 (lines 1777, 1801 … 1804) and the R5 proposal's RB-2 (lines 2056 … 2062), to
confirm that the remediation does not regress R4-F1 or R5-F1; the operational draft
`phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` by a fixed-string search for
`grace_deadline`, `children-unknown`, `s0_ran` and `` `children` `` (no match) and at §11.2, §11.3 and
the opening of §14 (lines 1344 … 1362 and 1459 … 1478), as the consumers of B-08 and B-13,
**without editing it**.

**Not re-read in R8, and said so in the proposal (§1.1):** the R1 … R3 prompts, authorities,
proposals and handbacks; the R4, R5 and R6 proposals beyond the passages above; the R6 handback;
the accepted OH-S2 R2 citation record, the accepted OH-S2 R2 handback and the one-host design:
**no R8 claim adds or changes an `[R2 §n]` or `[D §n]` citation, so none was searched**, and every
such citation of R7 is **carried, not re-verified**. Every CPython, kernel, libc and systemd
statement is a proposed, version-bound obligation and was **not researched**.

**Two carried items were not resolved and stay open for OH-S0d:** whether CL's by-name disarm of
the backstop timer is keyed to `backstop-intent` (A-I-16), and which terminal journal line marks
each helper's complete end (A-I-17). R8 did not search for them again.

## 6. Commands and checks run

Every command named exact files or one named directory. None was recursive over the repository, a
workspace root, home, `/opt`, `/var`, `/tmp` or `/`.

| # | Command or tool (targets) | Result |
|---|---|---|
| 1 | `wc -c` and `sha256sum` on the R8 prompt; read of the authority | `12733`; `1dd1c571…0e7`: **equal** |
| 2 | `sha256sum` of the R7 proposal, handback, prompt and authority **before any edit** (saved to the session scratchpad) | recorded before the first edit |
| 3 | `git status --short` before the first edit | the pre-existing state of §4 |
| 4 | file reads of the documents in §5 by named path and line range | read as listed |
| 5 | `cp` of the R7 proposal to the R8 proposal path | the R8 proposal began as a byte-identical copy |
| 6 | the `Edit` tool, one anchored replacement at a time, on the R8 proposal and on the restriction banner, the heading and the link rows of the pointers (the `apply_patch` tool named by the prompt is not available in this environment) | applied |
| 7 | copies of the four pointers' pre-edit state to the session scratchpad, then a `python3` script (scratchpad) that moved the R5, R6, R7 and R8 blocks of the Handover, status and §20 **by asserted line range** and wrote the R8 execution paragraph, followed by a multiset comparison of old and new lines | applied; only the lines listed in §3 left each file |
| 8 | `sha256sum` of 36 unchanged files (the 21 R1 … R7 proposals, handbacks and prompts, the 8 R1 … R8 authorities, the R8 prompt, the accepted OH-S2 R2 record and handback, the one-host design, the operational draft, `change-log.md` and `decision-register.md`), saved to the scratchpad, and of the operational draft separately | recorded **after my first edits had begun** (none of these files was ever opened for writing); compared at the end |
| 9 | the paper model of the R8 scope rule (scratchpad, `python3 -I`) | 64 runs, 0 violations; both mutants flagged (below) |
| 10 | `difflib` comparison of the R7 and R8 proposals, grouped by section | see §8 |
| 11 | `python3 -I` checks of Markdown table row widths, trailing whitespace, link existence and the pointer preservation of §3 | see §13 |
| 12 | `sha256sum -c` of the saved digests, `git diff --check` | see §13 |

**The paper model.** A throwaway Python script in the session scratchpad (outside the repository;
fake clock, no process, no signal, not application code) models a child's life: created, polled by
the enclosing wait, possibly passed to SN (S0 only for a `running` handle, every call ending at S7
with the handle settled), and then re-entered 0 … 3 times. It generated **64** runs: eight
lifecycles (a child that exits within c, a failed spawn, a pre-S0 raise, a handle reaped by an enclosing
poll and then passed to SN, an abandon, a reap in S3, a raise in S3, a raise at the final attempt)
× a successful and a failed `child` line append × 0 … 3 re-entries. After every step it checks:
`s0_ran == (grace_deadline_ms != null)`; whole-life `t_g` reads equal 1 if `s0_ran` else 0; sends,
`abandoned` and a `reap-error` outcome imply the stated `s0_ran` values; at most one `child` line; and,
for every re-entry, **0 S0 entries, 0 new clock reads, 0 new sends, 0 sleeps, 0 grace periods, 0 new
lines, a byte-identical entry, and unchanged history** (`false` / `null` for the 32 runs that settled before
any S0, `true` / the integer for the 32 that settled after one; the two lifecycles in which SN is never
entered, a child that exits within c and a failed spawn, have no re-entry). **0 violations.** Two mutants show that it can
fail: R7's literal INV-26 ("every settled handle has `s0_ran` false") is contradicted by 4 of the 8
lifecycles, and a re-entry that reads a new clock (R6's ordering) is flagged. The model checks the paper
design and is not a test of any implementation.

**Disclosed mistakes, each caught by a check and repaired before handback.**

* My first paper-model run reported **24 violations**. They were a defect in the *model*, not in the
  design: the model did not count a failed `child` append as the one attempt that S7 makes and never
  retries, so a re-entry looked as if it wrote a late line. S7 already says "a handle whose line was
  already written, or whose append failed, is not written again and not retried". I fixed the model, not
  the design, and re-ran it.
* When I added the R8 tag row to the §1.3 fact-class table I put a blank line before it, which split the
  table. I noticed it on inspection and removed the blank line.
* The first draft of the proposal's §0.10 sections table omitted four changed places (the S8 row of
  table SN-S, RE-4, review question Q25 and SR-15). The R8-versus-R7 comparison of §8 showed the changed
  regions, and I added them.
* My first draft of the §1.1 reading paragraph said that the operational draft's digest was recorded
  "before the pointer edits". It was recorded after my first edits had begun; the file was never opened for
  writing. I corrected the sentence.
* I did not record the digests of the 36-file unchanged set before the first edit, only the R7 four and
  (afterwards) the rest. Row 8 says so. None of those files was opened for writing, and all 36 digests
  match at the end.
* I ran one `grep` with a context regular expression that the tool refused as too complex; it printed an
  error and changed nothing, and I redid the scan with a small `python3 -I` script.

**Scratchpad files.** Helper scripts, the digest baselines, the pre-edit copies of the four pointers and
the paper model are in this session's scratchpad directory, outside the repository. They are not
deliverables. I took no cleanup action.

**No guard refusal occurred.** `.claude/hooks/guard-secrets.py` and `guard-git.py` refused nothing, and no
command text contained a secret-bearing file name pattern.

## 7. Checks not run, and why

* No SSH or other host connection, `oracle-test`, production, staging, Foundry or database access, and
  no retained-evidence access: forbidden.
* No application test, hook test (`python3 .claude/hooks/test_guards.py`), formatter, build, package
  tool, network check or remote-host check: forbidden, and this is a documentation slice. `run-suites`
  does not apply.
* **No test of the proposed regression cases.** NT-WB-1 … 12 (NT-WB-5 as 5a and 5b), NT-IS-1 … 17,
  NT-RE-1 … 12, NT-NS-1 … 8 and NT-GD-1 … 5 are defined on paper only; nothing was implemented or
  executed. The scratchpad paper model checks the **design's** record invariants and the re-entry rule;
  it is not an implementation and not a test.
* **No citation, observation or measurement of any kernel, libc, CPython or systemd behaviour.**
  PO-SN (a) … (g) stay **proposed**; PO-SN (b), (c) and (f), on which the sole-reaper invariant rests,
  are unchanged, and the source files named there are proposed citation targets that I did not read.
* No re-verification of any `[R2 §n]` or `[D §n]` citation of R7.
* No byte-level inspection of any launcher image; PO-17 stays unevaluated.
* No network research. No third-party artifact was selected.
* No resolution of the CL-disarm confirmation item or of the helper terminal-line item (§5).
* **No measurement of the size or effort of a Python-free root path** (WP-7).

## 8. Final checks

All operated on the six allowed files, listed explicitly.

| Check | Result |
|---|---|
| Prompt identity, re-checked at handback | `12733`; `1dd1c571…0e7`: equal (§13) |
| Unchanged inputs: R7 proposal, handback, prompt and authority (recorded before editing) | all four digests equal (§13); and the 36-file set (§6 row 8) all equal |
| R8-versus-R7: every content change closes a finding or is a directly necessary consistency correction | the section-by-section comparison attributes every changed region to a section listed in proposal §0.10: the title, header and §0.1 … §0.4 (identity, reading rule, finding bullets, map rows, research and terminal-state sentences), the new §0.10, §1.1 (the R8 reading) and §1.3 (the tag row and naming), the §3 vocabulary row, SN-6, WB-1, the S0 and S8 rows of table SN-S, RE-4, §7.5a.6e (path table, GD-1 … GD-6), §7.5a.9, W-19, the *Before T0* paragraph of §7.9, NT-WB-11 (i), NT-NS-1 … 3, NT-GD-2 … 5, the §8.5 `children` row, INV-22 and INV-26, test group (41), the §13.2 row, Q22 and Q25, SR-15, A-I-16, A-I-17, B-08, B-13, C.2, Appendix D and the closing statement. **Sixty R7 lines were rewritten or removed and 328 added**; of the 131 sections of the R7 proposal, **103 are byte-identical in R8** (including §0.5 … §0.9, §2, §4, §5, §6, §7.1 … §7.5a.3, §7.5a.5, §7.5a.6b, §7.5a.6c, §7.5a.7, §7.5a.8, §7.5a.10, §7.6, §7.8, §7.10, §7.11, §8.1 … §8.4, §8.8, §9 … §12, §13.1, §13.3 and Appendix C.1), 28 changed (two of them renamed: the title and the §7.5a.6e heading) and one (§0.10) was added |
| `s0_ran` is consistently per-child history; a settled re-entry reads no new clock and preserves any earlier deadline | proposal §3 row, GD-1, GD-2, GD-4, GD-6, the path table, SN-6, WB-1, S0 row, RE-4, §7.5a.9, §8.5, INV-22, INV-26, NT-WB-11 (i), NT-GD-2 … 5, A-I-16, A-I-17, B-08, B-13: each says *history* where it speaks of the record and *call* where it speaks of the step. The paper model agrees (64 runs) |
| Both settled histories (false/null and true/integer), through the path table, INV-26, the schema, the cases and Appendix A/B | path table rows (a) and (b); INV-26; §8.5 `children` row; NT-GD-2, -3, -5, NT-NS-1, -2, -3; A-I-16, A-I-17, B-08, B-13. The only places that still contain the unqualified R7 sentences are historical (the R7 bullets of §0.1, §0.9, CC-31/32, Appendix D rows of R7) and the quotations that W-19 withdraws; a scan for "exactly when S0 ran" and for "a settled handle … read(s) no `t_g`" finds only those |
| No regression of R7-F1 … R7-F3, R6-F1, R6-F2 | a pre-S0 `reap-error` still creates no `t_g` (path table row 3, NT-GD-1, NT-RE-7 unchanged); S0 runs only for a `running` handle (GD-4); no signal after any `reap-error` (RE-1, S8, WB-7, INV-24 unchanged); no send after any `not-sent` (INV-25 unchanged); the sole-reaper invariant stays load-bearing and SN-4 a detector only (SI-3, SI-5, INV-27, NT-SN-12 unchanged); no validation guarantee against a foreign reap or coincidental reuse is claimed; the CH vocabulary row and every current handle-state list keep four states or a stated settled subset (§0.9 unchanged) |
| No wait after `t_g`, no restarted grace period, no class-X time bound, no send-result inference of exit/reaping, no missing `attest` owner case | unchanged: WB-1 … WB-7 (WB-1 by one clause), SN-6 (one clause), SN-7, table SN-RO, IS-1 … IS-10, INV-16, INV-20; GD-6 adds no wait, no clock read and no grace period; `attest` keeps no automatic owner |
| The four current-state narratives in causal R1 → R8 order with every authority state, restriction, finding and link preserved | §3: the work-ID order is R1 … R8 in the Handover, status and §20; the banner was already in order; every work ID, SHA-256, finding ID and earlier link target is present; R8's authority and prompt are marked consumed in all four |
| Route 3, MF and authority restrictions retained | the pointers still say that nothing is accepted, that Codex re-review and Peter's recorded decision are required, that no successor, host, implementation, cleanup, OH-S4/OH-S4p or later slice, activation, commit or push is authorized, and that the retained R5 and H-0G paths stay untouched; the proposal's §2, §4, §5, §6, §9, §10, §11 and §12 are byte-identical to R7; SSW is still a scope-change alternative that is not Route 3; the MF dispositions are unchanged |
| Table row widths, both deliverables | see §13 |
| Trailing whitespace, six files | see §13 |
| Links introduced in the six files, from an explicit target list | see §13 |
| `git diff --check`, four tracked pointers and two new deliverables | see §13 |
| Six-file diff review | the four pointers differ from their pre-start state only by the heading or restriction line, the reordered blocks, the one replaced R8 paragraph and the link lines. The two deliverables are new files. A scan of the added lines for authority language found no host, implementation, successor, cleanup, credential, secret, commit or push authority granted or implied: every occurrence states that nothing is authorized, names a design object, or refers to a future separately authorized slice |

## 9. Security implications

* **No new attack surface is created by this return.** It is documentation.
* **What the proposal changes, if accepted later:** it adds no helper behaviour, no send, no wait, no
  clock read, no record field and no signal. It states which of two scopes a record field belongs to:
  `s0_ran` and `grace_deadline_ms` are the child's history and are not changed by a later SN call. The
  only practical effect for a reader of the record is that an abandoned child's entry is read as "S0 ran,
  here is its deadline", never as "never had a deadline"; the design's sends, waits and fail-closed
  results are the R7 ones.
* **What it does not close, stated by name** (proposal §13.1): **X-1** for the root roles until
  Route 3 is established; RO-1 … RO-6; CX-5; HB-1; and **RO-7**, unchanged from R7.
* **What the argument rests on, stated by name:** SI-2's pinning rests on **PO-SN (b)** and the
  sole-reaper invariant rests on **PO-SN (c) and (f)**, all proposed, version-bound and AP-0 gates. R8
  weakens none and strengthens none.
* **Route 3 is not established.** The accepted disposition stands: Route 1 returns to Route 3 design
  review, PO-12 and AS-8 are refuted, PO-19 stays not established.
* **No secret, credential or player datum was read**, and no secret-bearing path was opened or named.

## 10. Unresolved decisions

* **For Peter, only after a clean independent review** (proposal §12.1): DEC-1 … DEC-6 as in the R7
  proposal, unchanged. R8 adds **no decision**.
* **For the reviewer:** whether splitting `s0_ran` (history) from "S0 runs on this call" and splitting the
  settled-handle row in two is the right way to state the invariant, or whether the record should name the
  call-scoped fact separately; whether the added GD-6 is necessary or only restates GD-4; whether moving
  the §20 standing restriction paragraph up to follow the R1 block (as the Handover and status already
  have it) is acceptable or should be reverted; Q22 and Q25; and Q16's CC-10 from R4, still open.
* **Citation gate, not a decision:** PO-SN (a), (b), (c), (e), (f) must be accepted for the observed
  versions at OH-S2b before AP-0 can proceed. PO-SN (c′), (d) and (g) are optional or evidence-only. R8
  changes none.
* **Route 3 direction** (G-1b) and the **boundary changes** BC-1 … BC-5 (proposal §12.2): unchanged and
  not made by this return.
* **Confirmation items for OH-S0d:** the CL by-name disarm (A-I-16) and which terminal journal line marks
  each helper's complete end (A-I-17).

## 11. Proposed independent-review focus

Proposal §14.1 Q22 and Q25 first. In particular: (1) whether `s0_ran` is defined once, as a per-child
historical fact, and everything that speaks of the record uses that meaning while everything that speaks
of a step uses "S0 runs on this call" (§7.5a.6e GD-1, GD-4, the path table); (2) whether the
settled-handle row is correctly split into "settled before any S0" (`false` / `null` / 0 reads) and
"settled after an S0" (`true` / integer / 1 read), and whether any live text still says or implies that
every settled handle has never read `t_g` (INV-26, INV-22, NT-WB-11 (i), NT-GD-4's text scan, W-19);
(3) whether GD-6 and NT-GD-5 cover a re-entry of both histories at every position, including the failed
`child` append of an abandoned handle; (4) that no send, wait, outcome, fail-closed result, parameter,
class or field changed (the path-by-path table of §0.10); (5) that the four pointers read R1 → R8 with
every fact, work ID, prompt identity, finding, disposition, restriction and link preserved (§3), and that
the one block moved for a non-chronological reason (the §20 standing restriction paragraph) is
acceptable; and (6) that CC-35 … CC-37 are each necessary and none strengthens or silently weakens an R7
claim. The claims needing independent **security** re-review are proposal §14.2 SR-1 … SR-15, **SR-15
extended by GD-6**.

## 12. Confirmation

I confirm that **no** host connection, `oracle-test` or production access, Foundry or database access,
retained-evidence access, secret, credential or player-data access, network research, package
operation, implementation or configuration edit, launcher retarget or rebuild, application or hook
test, formatter, build, service or database mutation, repository or host cleanup, workspace
recreation, OH-S4/OH-S4p or later slice, H-1/H-2, activation, rollback, commit or push occurred.

## 13. Closing record of the final repository checks

| Check | Result |
|---|---|
| Prompt identity, last run | `12733`; `1dd1c571…0e7`: equal |
| Unchanged inputs, the R7 proposal, handback, prompt and authority (digests taken before the first edit) | `sha256sum -c`: **4 of 4 OK** |
| Unchanged inputs, the 36-file set of §6 row 8 and the operational draft (digests taken after my first edits, files never opened for writing) | `sha256sum -c`: **36 of 36 OK**, 0 failed; the operational draft **OK** |
| Trailing whitespace, six files | 0 lines in each |
| Link check, six files: every Markdown link target was extracted, resolved against its file's directory and tested for existence | 253 links checked, **66 distinct file targets, all under `docs/`, 0 missing**; the four R8 targets (prompt, authority, proposal, handback) all exist |
| Markdown table row widths | proposal: 91 tables, 0 mismatches (R7: 87; the four added are the tables of §0.10); handback: 5 tables, 0 mismatches; the other four files: 0 mismatches |
| `git diff --check`, four tracked pointers | exit 0, no output |
| `git diff --check --no-index`, the two new deliverables against `/dev/null` | 0 output lines each |
| Diff of the R8 proposal against the R7 proposal | 60 R7 lines removed or rewritten, 328 added; 103 of 131 R7 sections byte-identical, 28 changed, 1 added (§0.10); every changed region belongs to a section listed in proposal §0.10 |
| Diff of the four pointers against their pre-start state | `implementation-plan.md`: every changed line lies after line 2582, below the `## 20.` heading (line 2558); the banner: lines 3, 124 … 142 and 174 … 177 only; the Handover and status: the heading, the reordered narrative and the link rows; the multiset and token preservation check of §3 passed |
| Paper model of the R8 scope rule (scratchpad; not an implementation) | 64 runs; 0 invariant violations; both mutants flagged |
| `git status --short` at the end | 38 entries: the 36 pre-existing ones plus the two new deliverables; the six modified tracked files are the same six as at the start |
| Size | proposal: 4,812 lines, 550,934 bytes (this handback's own size is not recorded, because recording it would change it) |

HARD STOP: concrete Route 3 not established; OH-S3 R8 remediation awaits independent Codex re-review; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.
