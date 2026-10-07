# Handback — OH-S3 R5 remediation: `HARD STOP: concrete Route 3 not established`

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R5-20261007-05`

Date: 2026-10-07

Executor: Claude Code (Sonnet 5.5) on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r5-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r5-remediation-claude-prompt.md),
**12223 bytes, SHA-256
`f00e1970a4732f6056751e4b96cd939c9f68bf430201c1da7b56399d86a27696`**, recomputed
with `wc -c` and `sha256sum` before any edit and again at handback, and equal to the
pin in the
[authority record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r5-remediation-authority.md).
**The prompt and the authority are consumed by this return.**

Deliverable: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r5-remediation-proposal.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r5-remediation-proposal.md).

## 1. Terminal state

**`HARD STOP: concrete Route 3 not established`.** The prompt identity matched, so the
identity hard stop did not arise. The second defined hard stop, `HARD STOP: OH-S3 R5
remediation requires maintainer direction`, **did not arise**: closing R5-F1 and R5-F2
needed no scope or design decision beyond this assignment. The one behavioural question
that closing R5-F1 surfaced (whether `Popen.poll()` can raise after the kernel has
consumed a child's status) is a **proposed, version-bound proof obligation** at the existing
citation gate and a **review question** (Q18), not a decision I made. The conditional hard
stop of the OH-S3 R2, R3 and R4 proposals **remains in force and is unchanged**.

**Nothing is accepted by this return.** I have not claimed Codex's or Peter's acceptance,
have not proposed any successor for activation, have made no scope decision and have
created no authority. R1, R2, R3 and R4 are unchanged, unaccepted and historical.

## 2. Findings remediated

| Finding | Disposition | Proposal |
|---|---|---|
| **R5-F1** (Important): IM-S omits the reaping that completes inside an interrupted reap attempt | **Closed in the proposal, not accepted.** New §7.5a.6c defines **the boundary of one reap attempt** as five phases: RA-0 before the `waitpid` call, RA-1 inside the call before the kernel reaps, **RA-2 after the kernel reap and before the handle-state update (the handle still says `running`)**, RA-3 after the handle-state update and before the durable line, RA-4 after the durable line. Rules RB-1 … RB-5: the phases and their order; the kernel reaps only inside `reap_step()` (so T1, T2 and T4 contain no reap attempt, and the enclosing E wait's polls are reap attempts of the same phases that precede T0); no act is made between RA-2 and RA-3; the mapping to points; and the open question of an attempt that raises. **T3 and T5 are redefined to mean "not yet reaped by the kernel", new points T3k and T5k are RA-2 inside S3 and S5 (the final attempt included), and T6 now begins at the handle-state update (RA-3) or at the abandon decision, never earlier.** CS-5 and CS-7 are redefined as *reaped in the kernel*, with or without an in-memory record; the matrix gains rows T3k and T5k and three corrected cells. IS-9 states the conservative observer rule: without a durable `child` line a later procedure learns no reap fact, records only `children-unknown`, and a kernel reap that nothing recorded is not evidence that the group is empty. E1, "Reading the matrix", INV-18, INV-20, INV-23, §5.5 rows 19 and 20, RO-7, SI-3, SN-7, §7.3 row 3g, PO-SN (c), §7.5a.9, §8.5, §13, Q17, SR-13 and Appendix A, B, C.2 and D are corrected. NT-IS-1 and NT-IS-8 are rewritten and NT-IS-16 and NT-IS-17 added | §0.1, §0.7, §3, §5.5, §5.6, §7.5a.3, §7.5a.4, §7.5a.6c, §7.5a.8, §7.5a.9, §7.7, §7.9, §7.12, §8.5 … §8.7, §13, §14, Appendices |
| **R5-F2** (Important): NT-WB-5 gives one impossible expectation to two slow-validation runs | **Closed in the proposal, not accepted.** NT-WB-5 is split into **NT-WB-5a (slow S1)**: S1 costs 2,100 ms, so `t_g` is reached before S2; S3 and S5 skip every timed wait; `SIGTERM` returns at t0 + 2,120 and `SIGKILL` at t0 + 2,140, both `late`; scheduled sleeping 0 ms. And **NT-WB-5b (slow S4)**: S1 costs 10 ms, `SIGTERM` 20 ms (returns at t0 + 30, **not** `late`), S3 makes one capped sleep of 100 ms that begins before `t_g`, S4's validation costs 2,100 ms and returns at t0 + 2,230, `SIGKILL` is still sent and returns at t0 + 2,250, `late`; S5 makes no sleep; scheduled sleeping 100 ms. Both keep the shared assertions (one `t_g`, no restarted grace, no timed wait at or after it, each send at most once, scheduled waiting at most g, no class-X time bound). The case table of §7.5a.6b gets one row for each | §0.1, §0.7, §7.5a.6b, §7.12 |

The proposal's Appendix D maps every numbered item of both findings to its closing section.

## 3. Result in brief

* **A reap attempt now has an interior, and the map covers it.** The kernel can consume a
  child's exit status before the helper's handle or `child` line records it. That state is
  CS-5 (`reaped in the kernel`), reached at T3k and T5k, and a later procedure cannot tell it
  from a child that was never reaped. It learns no reap fact from it and may not infer that
  the group is empty (IS-9).
* **Every dash was re-derived.** The proposal states why each dash is unreachable (§7.9,
  *Corrected cells*). In doing so I found two further cells that R4's own text contradicted
  and corrected them: T0 and T1 `u` admit CS-5 (R4's table SN-R row 3, NT-SN-5 (a) and
  NT-IS-6 already allowed SN to be entered with a reaped handle), and T5 `i` names CS-2 for
  the PK subject (it has no `SIGTERM`). They are called out as CC-18 and CC-19.
* **The slow-S1 and slow-S4 cases now read their own clock.** The slow-S4 case shows that S3
  may make its capped wait and `SIGTERM` need not be late.
* **Seven consistency corrections are called out for review** (§0.7, CC-16 … CC-22). None
  changes a deadline class, a parameter value, a sizing rule, PO-11 (d′), a send rule, a wait
  rule (WB-1 … WB-7), the Route 3 boundary, the SSW classification, an MF disposition or the
  hard stop. **CC-18 and CC-19 go beyond the literal finding** (they fix cells the finding did
  not name) and are flagged for confirmation or rejection.
* **A risk is made visible, not closed (RB-5, Q18).** If `Popen.poll()` can raise *after*
  `waitpid` has consumed the status, row 3g would read that attempt as *unreaped*, and S4
  could send `SIGKILL` to a number the kernel had released. No repository evidence settles
  it. I added it to PO-SN (c), whose refusal ends the SN contract, and asked the reviewer
  whether the design should already forbid a send after a `reap-error`. **I did not change
  row 3g, S4 or SN-4.**

## 4. Files changed

**Created** (untracked):

* `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r5-remediation-proposal.md`
* `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r5-remediation-handback.md` (this file)

**Updated, current-state pointers only** (tracked; the OH-S3 R5 paragraph changed from
"authorized and unexecuted" to "executed, hard stop"; the R5 authority and prompt are
labelled *Consumed*; proposal and handback links added; the heading or restriction line
updated):

* `docs/review/Handover information`
* `docs/project-management/status.md`
* `docs/implementation-plan.md`, §20 only (the edited paragraph and link list lie after the
  `## 20. Immediate next actions` heading)
* `docs/operations/disposable-test-server.md`, the restriction banner and its link list only

**Pre-existing worktree changes.** Before my first edit `git status` showed six modified
tracked files (the four pointers above, plus `docs/project-management/change-log.md` and
`docs/project-management/decision-register.md`) and eighteen untracked files (the R1, R2, R3
and R4 prompts, handbacks, proposals and authorities as applicable, and this assignment's
prompt and authority). All were left by earlier work. The four pointers already carried the
uncommitted "OH-S3 R5 authorized" text, which I edited in place and otherwise preserved. **I
did not touch** `change-log.md`, `decision-register.md`, any R1 … R4 file, this assignment's
prompt or its authority.

**Not edited:** R1 through R4 proposals, handbacks, prompts and authorities; any accepted
historical evidence; the operational draft; any source, test, configuration, service file or
migration; any archive snapshot or archive index; the decision register; the change log. The
SHA-256 of twenty-three unchanged inputs was recorded before the first edit and compared at
the end (§6, §13).

## 5. Repository documents consulted

**Read completely:** `.agents/AGENTS.md`; the R5 prompt and its authority; the R4 prompt (all
220 lines) and its authority; the **complete** R4 proposal (3,594 lines, read in passes; most
passes through a byte-identical scratchpad copy of it, checked with `cmp`) and the **complete**
R4 handback (312 lines); `docs/review/Handover information`; the restriction banner of
`docs/operations/disposable-test-server.md` (lines 1 … 110); and
`docs/project-management/status.md` (all 141 lines).

**Read by section:** `docs/implementation-plan.md`: the reading map (lines 19 … 52), §0.1 …
0.5 (lines 53 … 183), §14.1 … 14.3 (lines 2216 … 2250), §16 in full (lines 2394 … 2490), §17
(lines 2492 … 2511) and §20 in full (lines 2558 to the end).

**Read at the exact text named:** the R3 proposal's interruption map and signal-sequence text
(lines 1829 … 1878 of that file: the old IM-S table T0 … T5, its closing sentence, and the
opening of §7.10 and §7.11), plus the heading of its table SN-S by `grep`, to confirm the
remediation does not regress R3-F1. It does not: R4 had already replaced that table, and R5
changes none of R3's inventory SN-I, its class statement, table SN-R, SI-1, SI-2, SI-4 or the
pinning argument. The operational draft at §11.2, §11.3 and the opening of §14 (lines 1344 …
1362 and 1459 … 1478), as the consumers of B-13, **without editing it**; its headings by
fixed pattern.

**Not re-read in R5, and said so in the proposal (§1.1):** the R1, R2 and R3 prompts,
authorities, proposals and handbacks beyond the R3 text above (their unchanged state is
checked by digest); the accepted OH-S2 R2 citation record and the one-host design. **No R5
claim cites a section of either, so none was searched**; every `[R2 §n]` and `[D §n]`
citation of R4 is **carried, not re-verified**. The prompt's item 7 asks for those records at
the sections cited by changed R4 claims; R5 changed none of those claims' citations. Appendix
B's other row identifiers are carried from R4.

**Two carried items were not resolved and stay open for OH-S0d:** whether CL's by-name disarm
of the backstop timer is keyed to `backstop-intent` (A-I-16), and which terminal journal line
marks each helper's complete end (A-I-17). R5 did not search for them again.

## 6. Commands and checks run

Every command named exact files or one named directory. None was recursive over the
repository, a workspace root, home, `/opt`, `/var`, `/tmp` or `/`.

| # | Command or tool (targets) | Result |
|---|---|---|
| 1 | `wc -c` and `sha256sum` on the R5 prompt; read of the authority | `12223`; `f00e1970…27696`: **equal** |
| 2 | `sha256sum` of twenty-three named files (the R1, R2, R3 and R4 proposals, handbacks, prompts and authorities; the R5 prompt and authority; the accepted OH-S2 R2 record; the one-host design; the operational draft; `change-log.md`; `decision-register.md`), saved to the session scratchpad | recorded before the first edit |
| 3 | `git status --short` before the first edit | the pre-existing state of §4 |
| 4 | file reads of the documents in §5 by named path and line range | read as listed |
| 5 | `cp` of the R4 proposal to the R5 proposal path, then `cmp`; the R4 proposal also copied to the scratchpad | identical |
| 6 | the editor's exact-string replacement (the `apply_patch` tool named by the prompt is not available in this environment) for the larger edits, and `python3 -I` scripts in the session scratchpad for the table and multi-row edits, each asserting that its anchor occurs exactly once and writing nothing otherwise | applied; see the disclosures below |
| 7 | `python3 -I` check of Markdown table row widths; `diff` and a section-by-section `difflib` comparison of the R4 and R5 proposals; `grep -n` scans of the R5 proposal for stale wording and for authority language | see §8 and §13 |
| 8 | `python3 -I` edit of the four pointer files, with exact-anchor assertions | applied |
| 9 | the final checks of §8 and §13 | see there |

**Disclosed mistakes, each caught by a check and repaired before handback.**

* One edit attempt in §0.1 failed on an anchor that did not match and wrote nothing; I read the
  exact text and repeated it.
* The first insertion of the R5 row in the §1.3 tag table left the row detached from its
  table by a blank line; a `grep -B` of the area showed it and a script rejoined it. An
  awkward parenthesis I wrote in the §1.1 reading paragraph was reworded.
* The first draft of the §0.7 sections table omitted §7.5a.6, which the section-by-section
  comparison showed I had changed (one sentence); I added it.
* A proofreading pass found that my RB-2 said "no child is reaped in the kernel at T1, T2 or
  T4" while the T1 cell admits CS-5 (a handle reaped by the enclosing wait's poll). I rewrote
  RB-2 to say those points contain no reap attempt, so none *becomes* reaped there, and kept
  the qualification about the enclosing wait's polls.
* The first wording of the slow-S1 case row contained a meaningless clause and its table
  header said "S2 costs" over cells that listed several costs; both were corrected.
* I did not take a digest of the four pointer files before editing, because they are in the
  allowed edit set. Their pre-edit state is the uncommitted state recorded by `git status`;
  every change to them was an exact-anchor replacement with a uniqueness assertion.

**Scratchpad files.** Helper scripts, the R4 copy and the digest baseline are in this
session's scratchpad directory, outside the repository. They are not deliverables. I took no
cleanup action.

**No guard refusal occurred.** `.claude/hooks/guard-secrets.py` and `guard-git.py` refused
nothing, and no command text contained a secret-bearing file name pattern.

## 7. Checks not run, and why

* No SSH or other host connection, `oracle-test`, production, staging, Foundry or database
  access, and no retained-evidence access: forbidden.
* No application test, hook test (`python3 .claude/hooks/test_guards.py`), formatter, build,
  package tool, network check or remote-host check: forbidden, and this is a documentation
  slice. `run-suites` does not apply.
* **No test of the 30 proposed regression cases.** NT-WB-1 … 12 (NT-WB-5 as 5a and 5b) and
  NT-IS-1 … 17 are defined on paper only; nothing was implemented or executed, and the
  fake-clock arithmetic of NT-WB-5a, NT-WB-5b and the case table of §7.5a.6b was checked by
  hand only.
* **No citation, observation or measurement of any kernel, libc, CPython or systemd
  behaviour.** PO-SN (a) … (g) stay **proposed**, PO-SN (c) now carries one more clause, and
  the source files named there are proposed citation targets that I did not read.
* No re-verification of the R4 proposal's own citations of the accepted record.
* No byte-level inspection of any launcher image; PO-17 stays unevaluated.
* No network research. No third-party artifact was selected.
* No resolution of the CL-disarm confirmation item or of the helper terminal-line item (§5).
* **No measurement of the size or effort of a Python-free root path** (WP-7).

## 8. Final checks

All operated on the six allowed files, listed explicitly.

| Check | Result |
|---|---|
| Prompt identity, re-checked at handback | `12223`; `f00e1970…27696`: equal (§13) |
| Unchanged inputs (twenty-three files) | 23 of 23 digests equal (§13) |
| R4 proposal still identical to the copy taken before the first edit | `cmp` equal |
| R5-versus-R4: every content change closes R5-F1 or R5-F2 or is a directly necessary consistency correction | the section-by-section comparison attributes every changed region to a section listed in proposal §0.7 (sections changed; CC-16 … CC-22). Sections byte-identical to R4 include §2, §4, §6, §7.1, §7.6, §7.10, §9, §10, §11 and §12 |
| Manual cross-check of the reap-attempt boundary, T3/T5/T6, E1, CS-1 … CS-8, every matrix cell and dash, `children-unknown`, NT-IS-1 and NT-IS-8 | each cell was re-derived from table SN-S and the phases RA-0 … RA-4 (§7.9, *Corrected cells*); the five positions of the prompt map to T3/T5 (before the call; inside the call before a reap), T3k/T5k, T6 and T7; the final attempt's RA-0 and RA-1 are T5 and the interior of an attempt is never T6; the abandon (S6) involves no kernel change, so CS-6 and CS-8 stay unreaped |
| Manual cross-check of both slow-validation cases | NT-WB-5a: `t_g` = t0 + 2,000, S1 returns at 2,100, S2 at 2,120 (late), S3 skips its sleep, S4 at 2,140 (late), the final attempt, sleeping 0. NT-WB-5b: S1 at 10, S2 at 30 (not late), S3 sleeps 100 from 30 to 130 (before `t_g`), S4's validation returns at 2,230, `SIGKILL` at 2,250 (late), S5 makes no sleep, sleeping 100. Both agree with table SN-S and WB-1 … WB-7 |
| No wait after `t_g`; no restarted grace; no class-X time bound; no send-result inference; no missing `attest` owner case | unchanged: WB-1 … WB-7, table SN-S, SN-6, SN-7 (one clause added), IS-1 … IS-8, SN-RO, INV-16, INV-20, INV-22, NT-WB-1 … 12; R5 adds no wait, no elapsed-time claim (the NT-WB-5a and NT-WB-5b numbers are fake-clock test costs, not claims) and no inference, and IS-9 forbids inferring a reap fact or an empty group from an unrecorded kernel reap |
| Route 3 boundary, SSW classification, MF dispositions, decisions, successor order, hard stop retained | §2, §4, §6, §9, §10, §11 and §12 byte-identical to R4; SSW is still a scope-change alternative that is not Route 3 |
| Table row widths, both deliverables | see §13 |
| Trailing whitespace, six files | see §13 |
| Links introduced in the six files, from an explicit target list | see §13 |
| `git diff --check`, four tracked pointers and two new deliverables | see §13 |
| Six-file diff review | the four pointers differ from their pre-start state only by the heading or restriction line, the one replaced R5 paragraph and the link lines. The two deliverables are new files. A scan of the added lines for authority language found no host, implementation, successor, cleanup, credential, secret, commit or push authority granted or implied: every occurrence states that nothing is authorized, names a design object (for example PK's *not authorized*) or refers to a future separately authorized slice |

## 9. Security implications

* **No new attack surface is created by this return.** It is documentation.
* **What the proposal changes, if accepted later:** a recovery step or reviewer can no longer
  read a child as unreaped, or its group as empty, from a state that the design cannot
  observe. A direct child may have been reaped by the kernel with no record, and the map now
  says so and forbids acting on the absence of a line. The change narrows what can be
  claimed; it adds no helper behaviour.
* **What it does not close, stated by name** (proposal §13.1): **X-1** for the root roles
  until Route 3 is established; RO-1 … RO-6; CX-5; HB-1; and **RO-7**, widened again: a child
  left behind by its helper may be alive, or may have been reaped with nothing recording it;
  its owner is the owner of its enclosing procedure, and the interactive `attest` has none.
* **A residual that R5 makes visible rather than closes (RB-5, Q18):** whether a failed
  `Popen.poll()` can follow the kernel's reap, which would leave the handle `running` for a
  number the kernel has released and let S4 send `SIGKILL` to it. SI-2's pinning argument and
  SN-4's validation do not cover that case if it exists. It is an AP-0 gate through PO-SN (c).
* **Back-to-back signals** (carried from R4): after a slow send or validation `SIGTERM` and
  `SIGKILL` can be sent with no sleep between them; NT-WB-5a and NT-WB-5b show both clocks.
* **Route 3 is not established.** The accepted disposition stands: Route 1 returns to Route
  3 design review, PO-12 and AS-8 are refuted, PO-19 stays not established.
* **No secret, credential or player datum was read**, and no secret-bearing path was opened
  or named.

## 10. Unresolved decisions

* **For Peter, only after a clean independent review** (proposal §12.1): DEC-1 … DEC-6 as in
  the R4 proposal, unchanged. R5 adds **no decision**.
* **For the reviewer:** Q18 (whether to leave row 3g, S4 and SN-4 unchanged and rely on the
  PO-SN (c) gate for an attempt that raises, or to forbid any send after a `reap-error` now);
  whether CC-18 and CC-19 (cells beyond the finding's letter) are accepted; and Q16's CC-10
  from R4, still open.
* **Citation gate, not a decision:** PO-SN (a), (b), (c), (e), (f) must be accepted for the
  observed versions at OH-S2b before AP-0 can proceed, (c) now including the `poll()` clause.
  PO-SN (d) and (g) are optional.
* **Route 3 direction** (G-1b) and the **boundary changes** BC-1 … BC-5 (proposal §12.2):
  unchanged and not made by this return.
* **Confirmation items for OH-S0d:** the CL by-name disarm (A-I-16) and which terminal journal
  line marks each helper's complete end (A-I-17).

## 11. Proposed independent-review focus

Proposal §14.1 Q17, Q18 and Q19 first. In particular: (1) whether the five phases RA-0 …
RA-4 are the exact boundary of an attempt and whether `Popen.poll()` is rightly treated as one
call with a kernel reap inside it (RB-1); (2) whether T3, T3k, T5, T5k and T6 are mutually
consistent, in particular that the final attempt's RA-0 and RA-1 are T5 and that T6 never
contains the interior of an attempt (RB-4); (3) whether CS-5 as *reaped in the kernel, with or
without an in-memory record* is the right state for T3k and T5k and whether any reachable cell
still names a state that forbids the true direct-child condition (try the corrected T0, T1 and
T5 cells and the enclosing wait's polls); (4) whether every dash is truly unreachable; (5)
whether IS-9 is the right conservative reading and whether any sentence still derives a reap
fact, exit or an empty group from a missing line; (6) RB-5 and Q18; (7) whether the two
slow-validation cases agree with the actual clock and whether each assertion follows from it;
and (8) that CC-16 … CC-22 are each necessary and none strengthens or silently weakens an R4
claim. The claims needing independent **security** re-review are proposal §14.2 SR-1 …
SR-13, SR-13 widened to cover RB-1 … RB-5 and IS-9.

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
| Prompt identity, last run | `12223`; `f00e1970…27696`: equal |
| Unchanged inputs: the twenty-three files of §6 row 2 | `sha256sum -c` against the digests taken before the first edit: **23 of 23 OK**, 0 failed |
| Trailing whitespace, six files | 0 lines in each |
| Link check, six files: every `](…)` target was extracted, resolved against its file's directory and tested for existence | 175 links checked, **54 distinct targets, all under `docs/`, 0 missing** |
| Markdown table row widths | proposal: 81 tables, 0 mismatches; handback: 4 tables, 0 mismatches |
| `git diff --check`, four tracked pointers | exit 0, no output |
| `git diff --check --no-index`, the two new deliverables | exit 1 (differences exist) and **no whitespace error reported** (0 output lines each) |
| Diff of the R5 proposal against the R4 proposal | 86 lines removed or rewritten, 383 added; every one belongs to a section listed in proposal §0.7 |
| `git status --short` at the end | 26 entries: the 24 pre-existing ones plus the two new deliverables |
| Size | proposal: 3,891 lines, 393,392 bytes (this handback's own size is not recorded, because recording it would change it) |

HARD STOP: concrete Route 3 not established; OH-S3 R5 remediation awaits independent Codex re-review; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.
