# Handback — OH-S3 R6 remediation: `HARD STOP: concrete Route 3 not established`

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R6-20261007-06`

Date: 2026-10-07

Executor: Claude Code (Sonnet 5.5) on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r6-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r6-remediation-claude-prompt.md),
**13147 bytes, SHA-256
`c635c30306b1aa3424e12a68de78da4a0aeb4dc490b329a207743022f9059a6b`**, recomputed
with `wc -c` and `sha256sum` before any edit and again at handback, and equal to the
pin in the
[authority record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r6-remediation-authority.md).
**The prompt and the authority are consumed by this return.**

Deliverable: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r6-remediation-proposal.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r6-remediation-proposal.md).

## 1. Terminal state

**`HARD STOP: concrete Route 3 not established`.** The prompt identity matched, so the
identity hard stop did not arise. The second defined hard stop, `HARD STOP: OH-S3 R6
remediation requires maintainer direction`, **did not arise**: closing R6-F1 and R6-F2
needed no scope or design decision beyond this assignment, and no kernel, language or
systemd behaviour was researched or invented. The one behavioural question that R5 had
made a safety gate (whether `Popen.poll()` can raise after the kernel has consumed a
child's status) is now an **evidence-only** proposed obligation, PO-SN (c′), because the
design is safe for both answers. The conditional hard stop of the OH-S3 R2, R3, R4 and R5
proposals **remains in force and is unchanged**.

**Nothing is accepted by this return.** I have not claimed Codex's or Peter's acceptance,
have not proposed any successor for activation, have made no scope decision and have
created no authority. R1 through R5 are unchanged, unaccepted and historical.

## 2. Findings remediated

| Finding | Disposition | Proposal |
|---|---|---|
| **R6-F1** (Blocking): a `reap-error` can permit a root signal to a reused process-group number | **Closed in the proposal, not accepted.** New §7.5a.6d, **RE-1 … RE-6**, makes the design fail closed after **any** `reap-error`. The child handle enters a fourth state, **`reap-unknown`**, which says only that the helper does not know whether the direct child is still unreaped or was reaped in the kernel with no handle update, and is labelled neither *reaped*, *unreaped* nor *abandoned* as a fact. **No later signal of any kind is sent to that child, S4's `SIGKILL` included, and no retry, alternate primitive, further poll or process search is made.** The handle and `Popen` object are kept for the helper's life; `reap-error`, `send_suppressed`, `reap_unknown` and, for a mutating child, `effect: "unknown"` are recorded; the enclosing operation returns its existing fail-closed result; the suppression starts no wait and no grace (one absolute `t_g`, the at-most-once send rule and WB-1 … WB-4, WB-6 unchanged). Table SN-S gains **S8** (suppress); row 3g and table SN-R (new row 12) are corrected; **WB-7's clause that let S4's escalation follow a reap-attempt exception is withdrawn** (CC-27, W-16); a new phase **RA-E**, points **T3x** and **T5x** and child states **CS-9** and **CS-10** extend the interruption map; IS-10 and the matrix follow. **PO-SN (c) is split**: (c) keeps what the design rests on and the post-poll exception question becomes **(c′)**, evidence about CPython that no decision depends on and AP-0 does not read; either answer leaves the design safe, so no answer can make AP-0 pass an unsafe branch (RE-6). Twelve paper-only cases, NT-RE-1 … 12, cover a `reap-error` before and after a kernel reap at S3, S5 and the final attempt, in the enclosing wait's poll, for the PK subject, for mutating children and for both answers to (c′) | §0.1, §0.2, §0.8, §3, §5.5, §5.6, §7.2, §7.3, §7.5, §7.5a.3 … §7.5a.9, §7.7, §7.9, §7.12, §8.1, §8.5 … §8.7, §13, §14, Appendices |
| **R6-F2** (Important): SN-S and IM-S disagree on `not-sent(reaped)` | **Closed in the proposal, not accepted.** **S1 is split.** **S1-a:** `not-sent(reaped)`, `not-sent(abandoned)` and (R6-F1) `not-sent(reap-unknown)` make no call, begin no wait and end at the new step **S7**, *settle, record, return*. **S1-b:** `not-sent(identity-mismatch)` and `not-sent(identity-unverifiable)` make no send and go to the capped S5 reap and final-attempt path. The same distinction holds at S4 (the PK-only path included), and **no `not-sent` result is ever followed by a send** (INV-25). For a handle that an enclosing wait's poll reaped before SN was entered, the **settled-state decision is that poll's RA-3, before SN, and the durable record is made by S7: the interval between them is T6 and the durable line is T7; T0 and T1 exist only for a `running` handle** (CC-23), so no interruption is at T0/T1 and at T7 at once. T0 `u` and T1 `u` return to CS-1 only (R4's cells; R5's CS-5 there is withdrawn), T5 `u` is now genuinely unreachable, and the outcome `u`, T6 and T7, the matrix cells, NT-SN-5 … 7 and 12, NT-IS-1, -5, -6 and -16 and the narrative agree. Eight paper-only cases, NT-NS-1 … 8, step an interruption before, during and after S1's branch for each `not-sent` subtype and audit every cell and dash | §0.1, §0.2, §0.8, §7.5a.3 … §7.5a.6a, §7.5a.6c, §7.9, §7.12, §8.6, §14, Appendices |

The proposal's Appendix D maps every numbered item of both findings to its closing section.

## 3. Result in brief

* **After a `reap-error` nothing is sent, on either truth.** The proposal says why no
  process-group number is exposed: every send is made while the handle is `running` and
  exact, which the helper knows only because the last attempt returned normally and found
  the child unreaped, or because none has run; a `reap-error` is the only event that can
  make that false, and S8 makes the helper's ignorance permanent, so the set of sends made
  after a possible release of the number is empty. SN-4's validation is not part of the
  argument and stays a detector.
* **The state `reap-unknown` is not a fact label.** It permits both truths. The matrix
  cells for it (CS-9, CS-10) are the same for either truth, and NT-RE-2, -4 and -6 require
  the design-visible state, the record and the sequence to be byte-identical to their
  *before* twins.
* **Every dash was re-derived and then checked mechanically.** I wrote a throwaway
  paper model of table SN-S in the session scratchpad (outside the repository; fake
  clock, no process, no signal, not application code) and ran it over **13,245**
  generated runs (settled handles, identity branches, PK and other children, every send
  outcome, eight child exit times, and a reap-attempt exception injected at every attempt
  under both truths). It found **0 invariant violations** (no send after a `not-sent`, none
  after a `reap-error`, no poll or sleep after one, no sleep beginning at or after `t_g`,
  scheduled sleeping never above g, at most one send per signal), **0 mismatches** between
  each matrix cell, parsed from the proposal, and the child state derived independently
  from the run's facts, **no generated pair that is a dash**, and **all 44 non-dash
  pairs reached**. It reproduced the NT-RE clock figures (for example scheduled sleeping
  1,950 ms and two sends before a raise at the final attempt, none after). It is a check of
  the paper design, **not a test of any implementation**, and is not a deliverable.
* **Eight consistency corrections are called out for review** (§0.8, CC-23 … CC-30). None
  changes a deadline class, a parameter value, a sizing rule, PO-11 (d′), a wait rule
  (WB-1 … WB-4, WB-6), the one absolute `t_g`, the at-most-once send rule, the Route 3
  boundary, the SSW classification, an MF disposition or the hard stop. **No send and no
  wait is added anywhere; CC-27 and RE-1 remove one send** (S4 after a `reap-error`).
  **CC-23 reverses part of R5** (its CC-18 cell correction, W-16) and **CC-30 corrects an R5
  test** (NT-SN-12's foreign-reaper expectation): both go beyond the letter of the findings
  and are flagged for confirmation or rejection.
* **R5's T0 and T1 correction was an over-correction.** R4's own matrix had T0 `u` and T1 `u`
  as CS-1 and T6 `u` and T7 `u` as CS-5 and CS-7; R6 returns to those cells and states where
  the settled-state decision and the record occur.

## 4. Files changed

**Created** (untracked):

* `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r6-remediation-proposal.md`
* `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r6-remediation-handback.md` (this file)

**Updated, current-state pointers only** (tracked; the OH-S3 R6 paragraph changed from
"authorized and unexecuted" to "executed, hard stop"; the R6 authority and prompt are
labelled *Consumed*; proposal and handback links added; the heading or restriction line
updated):

* `docs/review/Handover information`
* `docs/project-management/status.md`
* `docs/implementation-plan.md`, §20 only (the edited paragraph and link list lie after the
  `## 20. Immediate next actions` heading)
* `docs/operations/disposable-test-server.md`, the restriction banner and its link list only

**Pre-existing worktree changes.** Before my first edit `git status --short` showed 28
entries: six modified tracked files (the four pointers above, plus
`docs/project-management/change-log.md` and `docs/project-management/decision-register.md`)
and twenty-two untracked files (the R1 through R5 prompts, handbacks, proposals and
authorities as applicable, and this assignment's prompt and authority). All were left by
earlier work. The four pointers already carried the uncommitted "OH-S3 R6 authorized" text,
which I edited in place and otherwise preserved. **I did not touch** `change-log.md`,
`decision-register.md`, any R1 … R5 file, this assignment's prompt or its authority.

**Not edited:** R1 through R5 proposals, handbacks, prompts and authorities; any accepted
historical evidence; the operational draft; any source, test, configuration, service file or
migration; any archive snapshot or archive index; the decision register; the change log.
The SHA-256 of twenty-seven unchanged inputs was recorded before the first edit and compared
at the end (§6, §13).

## 5. Repository documents consulted

**Read completely:** `.agents/AGENTS.md`; the R6 prompt (229 lines) and its authority; the
R5 prompt (all 216 lines) and its authority; the **complete** R5 proposal (3,891 lines,
read in passes; the passes over §6 and §9 … §12 and the later checks were made through a
byte-identical scratchpad copy) and the **complete** R5 handback (300 lines); `docs/review/Handover
information` (175 lines); the restriction banner of `docs/operations/disposable-test-server.md`
(lines 1 … 115); and `docs/project-management/status.md` (all 169 lines).

**Read by section:** `docs/implementation-plan.md`: the reading map (lines 19 … 51), §0.1 …
0.5 (53 … 183), §14.1 … 14.3 (2216 … 2250), §16 in full (2394 … 2490), §17 (2492 … 2511) and
§20 in full (2558 to the end).

**Read at the exact text named:** the R4 proposal's table SN-R, table SN-S and WB-5 (lines
1749 … 1783 and 1821 … 1842) and its IM-S (lines 2148 … 2260), to confirm that the remediation
does not regress R4-F1 or R4-F2; the R3 proposal's signal-sending contract (lines 1412 … 1500
and 1552 … 1600), to confirm that it does not regress R3-F1; the operational draft at §11.2,
§11.3 and the opening of §14 (lines 1344 … 1362 and 1459 … 1478), as the consumers of B-13,
**without editing it**.

**Not re-read in R6, and said so in the proposal (§1.1):** the R1, R2 and R3 prompts,
authorities, proposals and handbacks beyond the R3 text above, and the R4 prompt, authority,
proposal and handback beyond the R4 text above (their unchanged state is checked by digest);
the accepted OH-S2 R2 citation record and the one-host design: **no R6 claim cites a section of
either, so none was searched**, and every `[R2 §n]` and `[D §n]` citation of R5 is **carried, not
re-verified**; the operational draft beyond the three places named (Appendix B's other row
identifiers are carried from R5). Every CPython, kernel, libc and systemd statement is a
proposed, version-bound obligation and was **not researched**.

**Two carried items were not resolved and stay open for OH-S0d:** whether CL's by-name disarm
of the backstop timer is keyed to `backstop-intent` (A-I-16), and which terminal journal line
marks each helper's complete end (A-I-17). R6 did not search for them again.

## 6. Commands and checks run

Every command named exact files or one named directory. None was recursive over the
repository, a workspace root, home, `/opt`, `/var`, `/tmp` or `/`.

| # | Command or tool (targets) | Result |
|---|---|---|
| 1 | `wc -c` and `sha256sum` on the R6 prompt; read of the authority | `13147`; `c635c303…059a6`: **equal** |
| 2 | `sha256sum` of the R5 proposal, handback, prompt and authority before any edit, then of twenty-seven named files (the R1 … R4 proposals, handbacks, prompts and authorities; the R5 and R6 prompts and authorities; the R5 proposal and handback; the accepted OH-S2 R2 record; the one-host design; the operational draft; `change-log.md`; `decision-register.md`), saved to the session scratchpad | recorded before the first edit |
| 3 | `git status --short` before the first edit | the pre-existing state of §4 |
| 4 | file reads of the documents in §5 by named path and line range | read as listed |
| 5 | `cp` of the R5 proposal to the R6 proposal path, then `cmp`; a second copy to the scratchpad for comparison | identical |
| 6 | exact-anchor replacement through `python3 -I` scripts in the session scratchpad (the `apply_patch` tool named by the prompt is not available in this environment), each asserting that its anchor occurs exactly once and writing nothing otherwise | applied; see the disclosures below |
| 7 | `python3 -I` check of Markdown table row widths, both deliverables and the R5 proposal | see §13 |
| 8 | section-by-section `difflib` comparison of the R5 and R6 proposals | see §8 and §13 |
| 9 | the paper model of table SN-S and the NT-RE clock check (scratchpad, `python3 -I`) | 13,245 runs; results in §3; no implementation was run |
| 10 | `python3 -I` edit of the four pointer files, with exact-anchor assertions; `sha256sum` of the four before and after | applied; the first run wrote nothing (below) |
| 11 | `grep -n` scans of the R6 proposal for stale wording (`CS-1 … CS-8`, `IS-1 … IS-9`, `RB-1 … RB-5`, `reap-error`, `not-sent`, `go to S5`, authority language) | each hit classed as historical or corrected |
| 12 | the final checks of §8 and §13 | see there |

**Disclosed mistakes, each caught by a check and repaired before handback.**

* The first draft of the §1.1 reading paragraph said the R6 prompt has 230 lines; `wc -l`
  shows 229. Corrected.
* The first run of the pointer script aborted on an anchor (the Handover file labels the R5
  link "Claude prompt") and wrote nothing; I confirmed by digest that all four files were
  unchanged, fixed the anchor and re-ran it.
* The owner-table edit asserted five occurrences and found four (the backstop row says "as
  stop-post CL"); that one script stopped after its earlier edits and I applied the rest
  separately with the correct count.
* The closing-statement edit dropped an "and" before the new clause; found by `grep` and
  repaired.
* My first clock figures for NT-RE-3 and NT-RE-5 (a `SIGKILL` returning at 160 ms and 1,940 ms
  of sleeping) were wrong by the 10 ms I had mis-added to S3's first attempt; recomputing by
  hand and with the paper model gave 150 ms and 1,950 ms (100 in S3, 1,850 in S5) and I
  corrected both rows.
* The paper model's first run reported 9,120 cell mismatches. All were defects of the model
  (it recorded a send as *not yet attempted* inside the call, and it did not resolve the
  matrix cells written "as `i`"); after fixing the model there were 0, and no matrix cell
  changed.
* The section comparison showed that my first §0.8 table omitted §7.8 SG-4, §9.5 and §11 and
  named §7.3 row 2 where I had changed rows 3, 3e and 3g; all were corrected.
* I did not take a digest of the four pointer files before editing until just before the
  pointer edit (the digests are recorded and compared in §13); they are in the allowed edit
  set, their pre-edit state is the uncommitted state recorded by `git status`, and every
  change was an exact-anchor replacement with a uniqueness assertion.

**Scratchpad files.** Helper scripts, the R5 copy, the digest baselines and the paper model
are in this session's scratchpad directory, outside the repository. They are not deliverables.
I took no cleanup action.

**No guard refusal occurred.** `.claude/hooks/guard-secrets.py` and `guard-git.py` refused
nothing, and no command text contained a secret-bearing file name pattern.

## 7. Checks not run, and why

* No SSH or other host connection, `oracle-test`, production, staging, Foundry or database
  access, and no retained-evidence access: forbidden.
* No application test, hook test (`python3 .claude/hooks/test_guards.py`), formatter, build,
  package tool, network check or remote-host check: forbidden, and this is a documentation
  slice. `run-suites` does not apply.
* **No test of the 50 proposed regression cases.** NT-WB-1 … 12 (NT-WB-5 as 5a and 5b),
  NT-IS-1 … 17, NT-RE-1 … 12 and NT-NS-1 … 8 are defined on paper only; nothing was
  implemented or executed. The scratchpad paper model of §3 checks the **design's** state
  machine and the figures of a few cases; it is not an implementation and not a test.
* **No citation, observation or measurement of any kernel, libc, CPython or systemd
  behaviour.** PO-SN (a) … (g) stay **proposed**; PO-SN (c) is narrowed, (c′) is new and
  evidence-only, and the source files named there are proposed citation targets that I did
  not read.
* No re-verification of the R5 proposal's own citations of the accepted record.
* No byte-level inspection of any launcher image; PO-17 stays unevaluated.
* No network research. No third-party artifact was selected.
* No resolution of the CL-disarm confirmation item or of the helper terminal-line item (§5).
* **No measurement of the size or effort of a Python-free root path** (WP-7).

## 8. Final checks

All operated on the six allowed files, listed explicitly.

| Check | Result |
|---|---|
| Prompt identity, re-checked at handback | `13147`; `c635c303…059a6`: equal (§13) |
| Unchanged inputs (twenty-seven files) | 27 of 27 digests equal (§13) |
| R5 proposal still identical to the copy taken before the first edit | digest equal (§13) |
| R6-versus-R5: every content change closes R6-F1 or R6-F2 or is a directly necessary consistency correction | the section-by-section comparison attributes every changed region to a section listed in proposal §0.8 (sections changed; CC-23 … CC-30). Sections byte-identical to R5 include §2, §4, §6, §7.1, §7.6, §7.10, §9 (apart from one clause of WP-4), §10, §12 and Appendix C.1 |
| Manual cross-check of every `reap-error` branch, before and after a kernel reap, at S3, S5 and the final attempt, and in the enclosing wait's poll | each branch ends at S8 with the same action under both truths: zero later sends (S4's `SIGKILL` included), no further poll, no sleep, no new `t_g`; the handle never leaves `reap-unknown`; the record and `children-unknown` rules, owner rules and observer rules are those of R5 plus CS-9 and CS-10. Confirmed again by the paper model (0 violations) |
| Manual cross-check of S1 and S4 for every `not-sent` subtype, T0/T1/T5/T6/T7, every affected cell and dash, and the paper cases | S1-a (settled handle) ends at S7 with no call and no wait; S1-b goes to S5 with no send; S4 has the same two branches (its settled branch is unreachable by construction); T0 and T1 exist only for a `running` handle; T6 and T7 `u` are the settled handles; all 28 dashes are unreachable and all 44 non-dash pairs are reachable (paper model); NT-NS-1 … 8 step every position |
| No wait after `t_g`; no restarted grace; no class-X time bound; no send-result inference of exit or reaping; no missing `attest` owner case | unchanged: WB-1 … WB-7 (WB-7 narrowed), SN-6, SN-7 (one clause added), table SN-RO, INV-16, INV-20, INV-22; S7 and S8 make no wait and no clock read; RE-4 starts no grace; `attest` keeps no automatic owner (SN-RO, IS-6, NT-IS-11 extended to T3x and T5x); R6 adds no elapsed-time claim |
| Route 3 boundary, SSW classification, MF dispositions, decisions, successor order, hard stop retained | §2, §4, §6, §9, §10, §11 (one clause in slice 2a) and §12 byte-identical to R5 apart from the clauses listed in §0.8; SSW is still a scope-change alternative that is not Route 3 |
| Table row widths, both deliverables | see §13 |
| Trailing whitespace, six files | see §13 |
| Links introduced in the six files, from an explicit target list | see §13 |
| `git diff --check`, four tracked pointers and two new deliverables | see §13 |
| Six-file diff review | the four pointers differ from their pre-start state only by the heading or restriction line, the one replaced R6 paragraph and the link lines. The two deliverables are new files. A scan of the added lines for authority language found no host, implementation, successor, cleanup, credential, secret, commit or push authority granted or implied: every occurrence states that nothing is authorized, names a design object (for example PK's *not authorized*) or refers to a future separately authorized slice |

## 9. Security implications

* **No new attack surface is created by this return.** It is documentation.
* **What the proposal changes, if accepted later:** a root helper can no longer send a signal
  to a child after a failed reap attempt. The change *removes* one send, adds no helper
  behaviour, and holds whichever way CPython behaves, so a citation outcome cannot turn it
  unsafe. A child whose reap attempt failed is recorded as unknown, never as reaped or gone.
* **What it does not close, stated by name** (proposal §13.1): **X-1** for the root roles
  until Route 3 is established; RO-1 … RO-6; CX-5; HB-1; and **RO-7**, widened again: a child
  left behind by its helper (now including a `reap-unknown` child) may be alive; its owner is
  the owner of its enclosing procedure, and the interactive `attest` has none.
* **What the new argument still rests on, stated by name:** the sends made *before* a
  `reap-error` rest on SI-2's pinning and so on **PO-SN (b)** (still an AP-0 gate), and the
  claim that a normal "not yet exited" return leaves the handle exact rests on **PO-SN (c)**
  (the reaping, non-blocking `poll()`; also still an AP-0 gate). R6 weakens neither and
  invents no weaker guarantee.
* **Route 3 is not established.** The accepted disposition stands: Route 1 returns to Route
  3 design review, PO-12 and AS-8 are refuted, PO-19 stays not established.
* **No secret, credential or player datum was read**, and no secret-bearing path was opened
  or named.

## 10. Unresolved decisions

* **For Peter, only after a clean independent review** (proposal §12.1): DEC-1 … DEC-6 as in
  the R5 proposal, unchanged. R6 adds **no decision**.
* **For the reviewer:** whether CC-23 (which withdraws R5's CC-18 cells and moves a handle
  settled by an enclosing poll to T6 and T7) and CC-30 (NT-SN-12's foreign-reaper
  expectation) are accepted; whether S0 should read `t_g` for a settled handle at all (R6
  leaves S0 unchanged, so `t_g` is read and unused on the S1-a path, which starts no wait);
  Q18 as rewritten; Q20 and Q21; and Q16's CC-10 from R4, still open.
* **Citation gate, not a decision:** PO-SN (a), (b), (c), (e), (f) must be accepted for the
  observed versions at OH-S2b before AP-0 can proceed. PO-SN (c′), (d) and (g) are optional
  or evidence-only.
* **Route 3 direction** (G-1b) and the **boundary changes** BC-1 … BC-5 (proposal §12.2):
  unchanged and not made by this return.
* **Confirmation items for OH-S0d:** the CL by-name disarm (A-I-16) and which terminal journal
  line marks each helper's complete end (A-I-17).

## 11. Proposed independent-review focus

Proposal §14.1 Q18, Q20 and Q21 first. In particular: (1) whether any path remains by which a
signal is sent to a child after a `reap-error` (table SN-S S3, S4, S5, S8; WB-7; table SN-R row
12; the poll of the enclosing wait; the PK subject), and whether *why no process-group number
is exposed* is complete; (2) whether `reap-unknown` is free of any label that reads as a fact
about the child, and whether its permanence (RE-3) and the absence of a further poll are
enough; (3) whether PO-SN (c′) is rightly evidence-only and AP-0 rightly does not read it
(RE-6, NT-RE-12); (4) whether every `not-sent` subtype takes exactly one branch (S7 for a
settled handle, S5 for an identity rejection), S4's PK-only path included; (5) whether T0, T1,
T6 and T7 now place the settled-state decision and the record exactly once for a handle
reaped by an enclosing poll (CC-23), and whether T5 `u` is unreachable; (6) whether CS-9 and
CS-10 and the matrix rows T3x and T5x permit both truths and whether every dash is
unreachable (the paper model agrees, but it is only a model); (7) whether the twenty new cases
agree with the actual clock and branches; and (8) that CC-23 … CC-30 are each necessary and
none strengthens or silently weakens an R5 claim. The claims needing independent **security**
re-review are proposal §14.2 SR-1 … SR-14, SR-13 widened and **SR-14 new**.

## 12. Confirmation

I confirm that **no** host connection, `oracle-test` or production access, Foundry or
database access, retained-evidence access, secret, credential or player-data access,
network research, package operation, implementation or configuration edit, launcher
retarget or rebuild, application or hook test, formatter, build, service or database
mutation, repository or host cleanup, workspace recreation, OH-S4/OH-S4p or later slice,
H-1/H-2, activation, rollback, commit or push occurred.

## 13. Closing record of the final repository checks

| Check | Result |
|---|---|
| Prompt identity, last run | `13147`; `c635c303…059a6`: equal |
| Unchanged inputs: the twenty-seven files of §6 row 2 | `sha256sum -c` against the digests taken before the first edit: **27 of 27 OK**, 0 failed (this includes the R5 proposal, handback, prompt and authority, `change-log.md` and `decision-register.md`) |
| R5 proposal against the scratchpad copy taken before the first edit | `cmp`: identical |
| Trailing whitespace, six files | 0 lines in each |
| Link check, six files: every `](…)` target was extracted, resolved against its file's directory and tested for existence | 220 links checked, **58 distinct file targets, all under `docs/`, 0 missing** (this covers the links introduced and the pre-existing ones) |
| Markdown table row widths | proposal: 84 tables, 0 mismatches (R5: 81; the three added are the §0.8 tables and the §7.5a.6d table); handback: 4 tables, 0 mismatches |
| `git diff --check`, four tracked pointers | exit 0, no output |
| `git diff --check --no-index`, the two new deliverables | no whitespace error reported (0 output lines each) |
| Diff of the R6 proposal against the R5 proposal | 210 lines removed or rewritten, 519 added; every changed region belongs to a section listed in proposal §0.8 |
| Paper model of table SN-S (scratchpad; not an implementation) | 13,245 runs; 0 invariant violations; 0 cell mismatches; 0 generated dash pairs; 44 of 44 non-dash pairs reached |
| `git status --short` at the end | 30 entries: the 28 pre-existing ones plus the two new deliverables |
| Size | proposal: 4,200 lines, 461,877 bytes (this handback's own size is not recorded, because recording it would change it) |

HARD STOP: concrete Route 3 not established; OH-S3 R6 remediation awaits independent Codex re-review; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.
