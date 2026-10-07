# Handback — OH-S3 R7 remediation: `HARD STOP: concrete Route 3 not established`

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R7-20261007-07`

Date: 2026-10-07

Executor: Claude Code (Sonnet 5.5) on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r7-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r7-remediation-claude-prompt.md),
**13330 bytes, SHA-256
`749dc19eb87ab867d3c075ddd7786667c7501bf46c542c8a29b421466e166c35`**, recomputed
with `wc -c` and `sha256sum` before any edit and again at handback, and equal to the
pin in the
[authority record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r7-remediation-authority.md).
**The prompt and the authority are consumed by this return.**

Deliverable: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r7-remediation-proposal.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r7-remediation-proposal.md).

## 1. Terminal state

**`HARD STOP: concrete Route 3 not established`.** The prompt identity matched, so the
identity hard stop did not arise. The second defined hard stop, `HARD STOP: OH-S3 R7
remediation requires maintainer direction`, **did not arise**: closing R7-F1, R7-F2 and
R7-F3 needed no scope or design decision beyond this assignment, and no kernel, language or
systemd behaviour was researched or invented. The conditional hard stop of the OH-S3 R2 …
R6 proposals **remains in force and is unchanged**.

**Nothing is accepted by this return.** I have not claimed Codex's or Peter's acceptance,
have not proposed any successor for activation, have made no scope decision and have created
no authority. R1 through R6 are unchanged, unaccepted and historical.

## 2. Findings remediated

| Finding | Disposition | Proposal |
|---|---|---|
| **R7-F1** (Important): the pre-S0 `reap-error` path has no defined grace-deadline record | **Closed in the proposal, not accepted.** New §7.5a.6e, **GD-1 … GD-5**: **`t_g` exists exactly when S0 ran.** In every `children` entry the key `grace_deadline_ms` is always present and is an integer **if and only if** the new boolean `s0_ran` is true and JSON `null` otherwise, never omitted, never `0`; the schema check is one line, `s0_ran == (grace_deadline_ms != null)`, with stated implications (`sends != [] ⇒ s0_ran`, `waits_skipped ⇒ s0_ran`, `abandoned ⇒ s0_ran`, any `late` ⇒ `s0_ran`, `outcome == "reap-error" ⇒ ¬s0_ran`). A `reap-error` raised in a poll of the enclosing E wait goes to S8 and S7 as in R6 and now reads **zero** `t_g`, makes **zero** clock reads in SN, enters no S0, starts no grace period, and records `s0_ran: false`, `grace_deadline_ms: null`, `outcome: "reap-error"`, `sends: []`, `waits_skipped: false`, `reap_unknown: true`, `send_suppressed: true`; the enclosing operation returns its fail-closed result. The distinction is **whether S0 ran, not where the poll stood**. The same representation covers a child that exits within c, a failed spawn, and a handle that is already settled when SN is called. Once S0 has run, the one absolute `t_g` is read once and never moved, extended or restarted (WB-1, unchanged). **Consistency correction CC-31:** S0 is entered only for a `running` handle (a settled handle goes to S1-a and S7 with no clock read), so a later SN call on a pre-S0 `reap-unknown` handle cannot create a `t_g` after the record was written with none; R6's own handback left that question open. SN-6, WB-1, RE-4, RE-5, S0, S1-a, S8, table SN-R row 12, §7.5a.9, §8.5, INV-22 (amended), INV-26 (new), NT-SN-5, -9, NT-WB-11, -12, NT-RE-7, -11, -12, NT-NS-1 … 3, Appendix A (A-I-17), Appendix B (B-08, B-13) follow. **NT-GD-1 … 4** are new focused paper-only cases, and NT-GD-1 follows the enclosing poll through S8 and S7 field by field | §0.1, §0.2, §0.9, §3, §7.5a.4 … §7.5a.6e, §7.5a.9, §7.7 (W-18), §7.9, §7.12, §8.5 … §8.7, §14, Appendices |
| **R7-F2** (Important): CC-30 assumes validation always detects a foreign reap and reuse | **Closed in the proposal, not accepted.** CC-30's claim is **withdrawn** (marked superseded in §0.8, W-17, CC-33). The sole-reaper contract is explicit and load-bearing (SI-3: no thread, signal disposition, destructor, foreign `wait*` call, `Popen` cleanup or other path reaps outside `reap_step()`; the `Popen` object of every child is kept referenced for the helper's life) with PO-SN (b), (c), (f) and the AP-0 refusal **unchanged**. **New SI-5:** an injected foreign reap is a **deliberate violation of a design precondition, not a supported runtime state**; SN-4 is a detector that may or may not notice (a released PID and group number can be reused by a process with the same structural relationship, and `start_ticks` is optional under PO-SN (d)); **once the invariant is violated the design makes no reuse-safety claim from SN-4 alone**; no mandatory `start_ticks`, pidfd or other identity mechanism is added. **NT-SN-12 is rewritten**: (a) … (c) structural scans (no threads, no `SIGCHLD` ignore, no `wait*` outside `reap_step()`, `state` assigned in exactly three places, `Popen` objects kept), (d) one detector exercise **labelled non-universal** with a deliberately mismatching fake identity, (e) a boundary statement that a same-structure fake identity is **not asserted to be caught** and that no document says otherwise. NT-SN-6 (b) and (c) carry the same label. INV-19 (clause), INV-27 (new), SI-2 and SN-4 (clauses), Q15, Q21, Q23, SR-12, SR-15, A-I-16 and Appendix D follow | §0.1, §0.2, §0.8, §0.9, §3, §7.5a.3, §7.5a.4, §7.7 (W-17), §7.12, §8.6, §14, Appendices |
| **R7-F3** (Optional): the CH vocabulary omits `reap-unknown` | **Closed in the proposal, not accepted.** The §3 row **child handle (CH)** now lists `running`, `reaped`, `abandoned` and `reap-unknown`. **Every current, non-historical definition or list of the handle state set was checked** (§0.9 *Handle-state vocabulary check*): §7.5a.3's CH lists four; SI-4, S1-a and S7, WB-5 (a), table SN-R row 9 and INV-25 list the three **settled** states by design; RE-2 and RE-3 name the states the handle never moves to. Only the §3 row was incomplete. Historical change tables, W-1 … W-16 and earlier Appendix D rows were **not rewritten** | §0.9, §3 |

The proposal's Appendix D maps every numbered item of the three findings to its closing section.

## 3. Result in brief

* **`t_g` exists exactly when S0 ran, and that is now a schema fact, not a convention.** The
  five-row paths table of §7.5a.6e shows, per path, S0, the number of `t_g` reads (0 or 1),
  `s0_ran`, `grace_deadline_ms`, `outcome` and `sends`. The one place R6's text produced a
  contradiction (a schema and a test requiring a deadline that no path had created) is gone,
  and so is the case it generalized (a child that exits within c).
* **A pre-S0 `reap-error` is fully specified**: the step-by-step path in §7.5a.6e lists every
  record field and the counts for the whole path (`t_g` reads 0; SN clock reads 0; sends 0;
  further polls 0; sleeps after the raise 0; searches 0; grace periods started 0).
* **The reuse defence is stated where it lives.** SN-4 stays a detector (SI-2, SN-4, SI-5), the
  sole-reaper invariant is load-bearing (SI-3), the honest consequence of violating it is
  stated (SI-5), and no new mechanism is invented.
* **A paper model of the sequence was run** (below): 880 generated runs, 0 violations, and
  both mutants of the model (R6's S0 ordering; an invented `t_g` on the pre-S0 path) were
  detected. It is a check of the paper design, **not a test of any implementation**, and is not
  a deliverable.
* **Four consistency corrections are called out for review** (§0.9, CC-31 … CC-34). None
  changes a deadline class, a parameter value, a sizing rule, PO-11 (d′), a wait rule
  (WB-1 … WB-4, WB-6, apart from one clause of WB-1), the one absolute `t_g` of every sequence
  in which S0 ran, the at-most-once send rule, any send, any proof obligation, the Route 3
  boundary, the SSW classification, an MF disposition or the hard stop. **No send, wait, grace
  period, clock read or identity mechanism is added; CC-31 removes one clock read** (S0 on a
  settled handle). **CC-31 and CC-32 go beyond the letter of the findings** (CC-31 narrows an
  R6 step; CC-32 adds the field `s0_ran`, the outcome value `reap-error` and the statement that
  S8 reads no clock) and are flagged for confirmation or rejection.

## 4. Files changed

**Created** (untracked):

* `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r7-remediation-proposal.md`
* `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r7-remediation-handback.md` (this file)

**Updated, current-state pointers only** (tracked; the OH-S3 R7 paragraph changed from
"authorized and unexecuted" to "executed, hard stop"; the R7 authority and prompt are labelled
*Consumed*; proposal and handback links added; the heading or restriction line updated):

* `docs/review/Handover information`
* `docs/project-management/status.md`
* `docs/implementation-plan.md`, §20 only (the edited paragraph and link list lie after the
  `## 20. Immediate next actions` heading)
* `docs/operations/disposable-test-server.md`, the restriction banner and its link list only

**Pre-existing worktree changes.** Before my first edit `git status --short` showed **32**
entries: six modified tracked files (the four pointers above, plus
`docs/project-management/change-log.md` and `docs/project-management/decision-register.md`)
and twenty-six untracked files (the R1 through R6 prompts, handbacks, proposals and
authorities as applicable, and this assignment's prompt and authority). All were left by
earlier work. The four pointers already carried the uncommitted "OH-S3 R7 authorized" text,
which I edited in place and otherwise preserved. **I did not touch** `change-log.md`,
`decision-register.md`, any R1 … R6 file, this assignment's prompt or its authority.

**Not edited:** R1 through R6 proposals, handbacks, prompts and authorities; any accepted
historical evidence; the operational draft; any source, test, configuration, service file or
migration; any archive snapshot or archive index; the decision register; the change log. The
SHA-256 of thirty-two unchanged inputs (the earlier five-file pin set, the R6 proposal, handback,
prompt and authority and the R7 prompt, is a subset) was recorded before the first edit and
compared at the end (§6, §13).

## 5. Repository documents consulted

**Read completely:** `.agents/AGENTS.md` (700 lines); the R7 prompt (236 lines) and its authority
(37 lines); `docs/review/Handover information` (213 lines before editing); the **complete R6
proposal** (4,200 lines, read in passes, section by section: §0, §1, §2, §3, §4, §5, §6, §7 with
§7.9 and the whole of §7.12, §8, §9 … §12, §13, §14 and Appendices A, B, C and D); the R6
handback (326 lines); `docs/project-management/status.md` (204 lines); the restriction banner of
`docs/operations/disposable-test-server.md` (lines 1 … 125).

**Read by section:** `docs/implementation-plan.md`: the reading map (lines 19 … 51), §0.1 … 0.5
(53 … 183), §14.1 … 14.3 (2216 … 2250), §16 in full (2394 … 2490), §17 (2492 … 2511) and §20 in
full (2558 to the end).

**Read at the exact text named:** the R5 proposal's boundary of a reap attempt (§7.5a.6c, lines
2035 … 2084, phases RA-0 … RA-4 and RB-1 … RB-5) and NT-WB-5a, NT-WB-5b and NT-IS-16, to confirm
that the remediation does not regress R5-F1 or R5-F2; the R4 proposal's table SN-R, table SN-S
and WB-1 … WB-7 (lines 1749 … 1853) and the opening and rules IS-1 … IS-7 of its IM-S (lines
2085 … 2185), to confirm that it does not regress R4-F1 or R4-F2; the R3 proposal's
signal-sending contract (lines 1412 … 1500 and 1552 … 1600), to confirm that it does not regress
R3-F1; the operational draft `phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` by a
fixed-string search for `grace_deadline`, `children` and `children-unknown` (no match) and at
§11.2, §11.3 and the opening of §14 (lines 1344 … 1362 and 1459 … 1478), as the consumers of B-08
and B-13, **without editing it**.

**Not re-read in R7, and said so in the proposal (§1.1):** the R1 … R5 prompts, authorities,
proposals and handbacks beyond the R3, R4 and R5 text above (their unchanged state is checked by
digest); the accepted OH-S2 R2 citation record and the one-host design: **no R7 claim cites a
section of either, so none was searched**, and every `[R2 §n]` and `[D §n]` citation of R6 is
**carried, not re-verified**. Every CPython, kernel, libc and systemd statement is a proposed,
version-bound obligation and was **not researched**.

**Two carried items were not resolved and stay open for OH-S0d:** whether CL's by-name disarm
of the backstop timer is keyed to `backstop-intent` (A-I-16), and which terminal journal line
marks each helper's complete end (A-I-17). R7 did not search for them again.

## 6. Commands and checks run

Every command named exact files or one named directory. None was recursive over the
repository, a workspace root, home, `/opt`, `/var`, `/tmp` or `/`.

| # | Command or tool (targets) | Result |
|---|---|---|
| 1 | `wc -c` and `sha256sum` on the R7 prompt; read of the authority | `13330`; `749dc19e…c35`: **equal** |
| 2 | `sha256sum` of the R6 proposal, handback, prompt and authority before any edit (saved to the session scratchpad) | recorded before the first edit |
| 3 | `sha256sum` of thirty-two named files (the R1 … R7 proposals, handbacks, prompts and authorities that existed; the accepted OH-S2 R2 record and handback; the one-host design; the operational draft; `change-log.md`; `decision-register.md`), and of the four pointers, saved to the session scratchpad | recorded before the first edit of the pointers and the R7 proposal's body |
| 4 | `git status --short` before the first edit | the pre-existing state of §4 |
| 5 | file reads of the documents in §5 by named path and line range | read as listed |
| 6 | `cp` of the R6 proposal to the R7 proposal path | the R7 proposal began as a byte-identical copy |
| 7 | exact-anchor replacement through `python3 -I` scripts, each asserting that its anchor occurs exactly once and writing nothing otherwise (the `apply_patch` tool named by the prompt is not available in this environment) | applied; see the disclosures below |
| 8 | `python3 -I` check of Markdown table row widths, both deliverables and the R6 proposal | see §13 |
| 9 | section-by-section `difflib` comparison of the R6 and R7 proposals | see §8 and §13 |
| 10 | the paper model of the R7 sequence and its two mutants (scratchpad, `python3 -I`) | 880 runs, 0 violations; the mutants flag 440 and 256 violations |
| 11 | `python3 -I` edit of the four pointer files, with exact-anchor assertions; `sha256sum` of the four before and after | applied |
| 12 | `grep -n` scans of the R7 proposal for stale wording (`validation yields`, `never a send to the stale`, `detects a foreign`, `seen by validation`, `CS-1 … CS-8`, `one grace`) | each hit classed as historical or corrected (§8) |
| 13 | the final checks of §8 and §13 | see there |

**The paper model.** A throwaway Python script in the session scratchpad (outside the
repository; fake clock, no process, no signal, not application code) models the enclosing E wait
and table SN-S with CC-31's entry check. It generated **880** runs: eleven child-exit times
(including never), ten reap-attempt-raise positions (none, early polls, S3, S5, the final attempt,
two raises), four cost profiles (including S1 and S4 validations consuming g and a send consuming
more than g), each with and without a later SN call on the settled handle. It checks, on the record
that S7 writes: `s0_ran == (grace_deadline_ms != null)`; `t_g` reads equal to 1 if S0 ran and 0
otherwise; `sends`, `waits_skipped`, `abandoned` and `late` imply `s0_ran`; `outcome ==
"reap-error"` implies `¬s0_ran`; no clock read in S7 or S8; no poll after a raise; no sleep
beginning at or after `t_g`; no sleep over its cap; scheduled sleeping at most g; at most one send
per signal; exactly one `child` line per child; no `reap-unknown` handle that is also abandoned;
and, for every pre-S0 raise, the exact field values of NT-GD-1. **0 violations**; 448 runs had an
S0 and 432 had none, and **256 were pre-S0 `reap-error` runs**. Two mutants were run to show that
the model can fail: R6's ordering (S0 entered even for a settled handle) gave **440** violations
(a second line write and a `t_g` on a `reap-error` entry), and a mutant that invents a `t_g` on the
pre-S0 path gave **256**. The model checks the paper design and is not a test of any implementation.

**Disclosed mistakes, each caught by a check and repaired before handback.**

* My first draft of the §1.1 reading paragraph said the R6 proposal's text was read "except" two
  passages; I had in fact read all of it by then, and the sentence was garbled. Rewritten to say
  what was read.
* The first §0.9 sections table listed SG-3 (in the remediation map) as amended and §13.1 as
  changed; SG-3 is unchanged and only §13.2 changed. Both were corrected.
* The first map row cited "Q15, Q21, Q22" for the R7-F2 questions; the R7-F2 question is Q23.
  Corrected.
* The first §7.12 text-scan case NT-GD-4 forbade any statement of a single `t_g` and would have
  contradicted the carried sentences about a *signalled* child; it now allows a signalled child's
  sequence to say one `t_g` and requires "at most one" for children in general.
* CC-30's first superseded-marker said "its second sentence"; the false claim is half of its
  first sentence. The marker and CC-33 were rewritten to name the claim.
* The first `grep` of the reading step used a backtick inside a double-quoted shell string and ran
  a stray command (`t_g: command not found`); it changed nothing, and the search was repeated
  correctly.

**Scratchpad files.** Helper scripts, the digest baselines and the paper model are in this
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
* **No test of the 54 proposed regression cases.** NT-WB-1 … 12 (NT-WB-5 as 5a and 5b), NT-IS-1 …
  17, NT-RE-1 … 12, NT-NS-1 … 8 and NT-GD-1 … 4 are defined on paper only; nothing was
  implemented or executed. The scratchpad paper model checks the **design's** state machine and
  the record invariants; it is not an implementation and not a test.
* **No citation, observation or measurement of any kernel, libc, CPython or systemd
  behaviour.** PO-SN (a) … (g) stay **proposed**; PO-SN (b), (c) and (f), on which the
  sole-reaper invariant rests, are unchanged, and the source files named there are proposed
  citation targets that I did not read.
* No re-verification of the R6 proposal's own citations of the accepted record.
* No byte-level inspection of any launcher image; PO-17 stays unevaluated.
* No network research. No third-party artifact was selected.
* No resolution of the CL-disarm confirmation item or of the helper terminal-line item (§5).
* **No measurement of the size or effort of a Python-free root path** (WP-7).

## 8. Final checks

All operated on the six allowed files, listed explicitly.

| Check | Result |
|---|---|
| Prompt identity, re-checked at handback | `13330`; `749dc19e…c35`: equal (§13) |
| Unchanged inputs (thirty-two files; the earlier five-file pin set is a subset) | all digests equal (§13) |
| R7-versus-R6: every content change closes R7-F1, R7-F2 or R7-F3 or is a directly necessary consistency correction | the section-by-section comparison attributes every changed region to a section listed in proposal §0.9 (sections changed; CC-31 … CC-34). Fifty-five R6 lines were rewritten and every one is a header or identity line, a row the findings name, or a clause the change directly needs (listed in §13). Sections byte-identical to R6 include §2, §4, §5, §6, §7.1 … §7.4, §7.6, §7.10, §7.11, §9 … §12 and Appendix C.1 |
| Manual cross-check of the enclosing-wait pre-S0 `reap-error` path through S8 and S7, including clock reads and every record field | the poll raises at RA-E (CS-9 if the helper ends there); S8 sets `reap-unknown`, records `reap-error`, `send_suppressed`, `effect`; S7 writes one line; **`t_g` reads 0, SN clock reads 0, sends 0, sleeps after the raise 0, polls 0, searches 0, grace periods 0**; the entry has `s0_ran: false`, `grace_deadline_ms: null`, `outcome: "reap-error"`, `sends: []`, `waits_skipped: false`, `reaped: false`, `abandoned: false`, `reap_unknown: true`, `send_suppressed: true`, `last_signal: null`, `anomalies: ["reap-error"]`; the enclosing operation fails closed. Confirmed again by the paper model (256 such runs, 0 violations) |
| Manual cross-check that every path with S0 has exactly one `t_g` and every path without S0 has none, and that neither starts or restarts a grace period | the paths table of §7.5a.6e: exits within c, failed spawn, pre-S0 raise and settled-handle SN entry have none; every S0 path has one, read once, never moved. No step other than S0 reads or sets it. A later SN call on a settled handle makes no S0 and no read (GD-4). The paper model agrees (448 runs with S0: one read each; 432 without: none) |
| Manual cross-check of the sole-reaper invariant, CC-30's replacement, NT-SN-12 and every PID or process-group reuse claim; SN-4 remains a detector only | SI-2, SI-3, SI-5, SN-4, NT-SN-6, NT-SN-12, INV-19, INV-27, W-17 and the review questions state SN-4 as a detector and name the sole-reaper invariant as the defence; the only places that still contain the withdrawn wording are the §0.8 CC-30 row (marked superseded, history), the W-17 row (the withdrawn claim, quoted), CC-33 (quotes it to withdraw it) and the R7 bullets that describe it. No live definition, test, invariant or review question claims that validation detects a foreign reap or a coincidental reuse |
| The CH vocabulary and every current handle-state definition list all four states | §3 CH row corrected; §7.5a.3 lists four; the settled-state lists (SI-4, S1-a, S7, WB-5 (a), SN-R row 9, INV-25) list three by design; no other current list exists. Historical rows untouched (§0.9) |
| No regression of R6-F1 or R6-F2 | no signal after any `reap-error` (RE-1, S8, WB-7, INV-24 unchanged); no send after any `not-sent` (INV-25 unchanged); S1-a and S1-b, S4's branches, T0 … T7 and the matrix are unchanged; the model confirms no poll or send after a raise |
| No wait after `t_g`, no restarted grace, no class-X time bound, no send-result inference of exit or reaping, no missing `attest` owner case | unchanged: WB-1 … WB-7 (WB-1 by one clause), SN-6 (one clause), SN-7, table SN-RO, IS-1 … IS-10, INV-16, INV-20; S7 and S8 make no wait and no clock read (S8's clock clause added); `attest` keeps no automatic owner |
| Route 3 boundary, SSW classification, MF dispositions, decisions, successor order, hard stop retained | §2, §4, §5, §6, §9, §10, §11 and §12 byte-identical to R6; SSW is still a scope-change alternative that is not Route 3 |
| Table row widths, both deliverables | see §13 |
| Trailing whitespace, six files | see §13 |
| Links introduced in the six files, from an explicit target list | see §13 |
| `git diff --check`, four tracked pointers and two new deliverables | see §13 |
| Six-file diff review | the four pointers differ from their pre-start state only by the heading or restriction line, the one replaced R7 paragraph and the link lines. The two deliverables are new files. A scan of the added lines for authority language found no host, implementation, successor, cleanup, credential, secret, commit or push authority granted or implied: every occurrence states that nothing is authorized, names a design object, or refers to a future separately authorized slice |

## 9. Security implications

* **No new attack surface is created by this return.** It is documentation.
* **What the proposal changes, if accepted later:** it adds no helper behaviour, no send, no wait
  and no signal. It narrows a claim: the design no longer says that validation detects a foreign
  reap or a coincidental reuse, and says instead that, if the sole-reaper invariant is violated,
  no reuse-safety claim stands on SN-4 alone. That is a **weakening of a stated guarantee to match
  what the mechanism can show**; the design's actual defence (SI-2's pinning under SI-3's sole
  reaper) is unchanged. It also adds a record representation (`s0_ran`, a nullable
  `grace_deadline_ms`, the outcome `reap-error`) that creates no behaviour.
* **What it does not close, stated by name** (proposal §13.1): **X-1** for the root roles until
  Route 3 is established; RO-1 … RO-6; CX-5; HB-1; and **RO-7**, unchanged from R6.
* **What the argument rests on, stated by name:** SI-2's pinning rests on **PO-SN (b)** and the
  sole-reaper invariant rests on **PO-SN (c) and (f)**, all proposed, version-bound and AP-0
  gates. R7 weakens none and invents no stronger guarantee. A violation of the invariant by a
  future implementation defect is outside the design (SI-5); the structural scans of NT-SN-12 are
  the means of keeping it true, and they are paper-only.
* **Route 3 is not established.** The accepted disposition stands: Route 1 returns to Route 3
  design review, PO-12 and AS-8 are refuted, PO-19 stays not established.
* **No secret, credential or player datum was read**, and no secret-bearing path was opened
  or named.

## 10. Unresolved decisions

* **For Peter, only after a clean independent review** (proposal §12.1): DEC-1 … DEC-6 as in
  the R6 proposal, unchanged. R7 adds **no decision**.
* **For the reviewer:** whether CC-31 (S0 only for a `running` handle) is accepted, or S0 should
  stay before S1 with a `t_g` read and recorded for a settled handle; whether the new outcome
  value `reap-error` and the field `s0_ran` are the right representation (the alternative is a
  nullable `grace_deadline_ms` alone, with `outcome` kept to R6's four values); whether S8
  reading no clock for any path is acceptable; whether NT-SN-12 (e), which records a limit
  rather than asserting a property, is the right way to keep the limit visible; Q22, Q23 and Q24;
  and Q16's CC-10 from R4, still open.
* **Citation gate, not a decision:** PO-SN (a), (b), (c), (e), (f) must be accepted for the
  observed versions at OH-S2b before AP-0 can proceed. PO-SN (c′), (d) and (g) are optional or
  evidence-only. R7 changes none.
* **Route 3 direction** (G-1b) and the **boundary changes** BC-1 … BC-5 (proposal §12.2):
  unchanged and not made by this return.
* **Confirmation items for OH-S0d:** the CL by-name disarm (A-I-16) and which terminal journal
  line marks each helper's complete end (A-I-17).

## 11. Proposed independent-review focus

Proposal §14.1 Q22, Q23 and Q24 first. In particular: (1) whether `t_g` really exists exactly
when S0 ran on every path (a child that exits within c, a failed spawn, a pre-S0 raise under both
truths, a settled handle, a later SN call on a pre-S0 `reap-unknown` handle, and every post-S0
path), and whether `s0_ran == (grace_deadline_ms != null)` with its implications is complete
(§7.5a.6e GD-1 … GD-5, NT-GD-1 … 4); (2) whether CC-31 is necessary and whether it regresses
R4-F1 or R6-F2 (it leaves S1-a's behaviour unchanged and removes only a clock read); (3) whether
SI-3 now states the sole-reaper invariant as load-bearing enough, whether SI-5's reading of a
foreign reap as a violated precondition is right, and whether "no reuse-safety claim from SN-4
alone" is the honest consequence (and no new mechanism is the right scope for this remediation);
(4) whether NT-SN-12 (d) is labelled non-universal enough, and whether any text outside the
historical tables still claims that validation catches a foreign reap or a coincidental reuse
(W-17, NT-GD-4); (5) that the CH vocabulary and every current handle-state definition list four
states (§0.9), with the historical rows untouched; and (6) that CC-31 … CC-34 are each necessary
and none strengthens or silently weakens an R6 claim. The claims needing independent **security**
re-review are proposal §14.2 SR-1 … SR-15, **SR-12 widened and SR-15 new**.

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
| Prompt identity, last run | `13330`; `749dc19e…c35`: equal |
| Unchanged inputs: the thirty-two files of §6 row 3 (the R1 … R6 proposals, handbacks, prompts and authorities, the R7 prompt and authority, the accepted OH-S2 R2 record and handback, the one-host design, the operational draft, `change-log.md`, `decision-register.md`) | `sha256sum -c` against the digests taken before the first edit: **32 of 32 OK**, 0 failed; the earlier five-file pin set (R6 proposal, handback, prompt and authority; R7 prompt) also **5 of 5 OK** |
| Trailing whitespace, six files | 0 lines in each |
| Link check, six files: every Markdown link target was extracted, resolved against its file's directory and tested for existence | 227 links checked, **62 distinct file targets, all under `docs/`, 0 missing** (this covers the links introduced and the pre-existing ones) |
| Markdown table row widths | proposal: 87 tables, 0 mismatches (R6: 84; the three added are the two §0.9 tables and the §7.5a.6e table); handback: 4 tables, 0 mismatches |
| `git diff --check`, four tracked pointers | exit 0, no output |
| `git diff --check --no-index`, the two new deliverables against `/dev/null` | no whitespace error reported (0 output lines each; the exit status 1 is the tool's "files differ" status) |
| Diff of the R7 proposal against the R6 proposal | 55 R6 lines removed or rewritten, 399 added; every changed region belongs to a section listed in proposal §0.9 (97 sections byte-identical, 32 changed, 2 added) |
| Paper model of the R7 sequence (scratchpad; not an implementation) | 880 runs; 0 invariant violations; 256 pre-S0 `reap-error` runs checked field by field; both mutants flagged (440 and 256 violations) |
| `git status --short` at the end | 34 entries: the 32 pre-existing ones plus the two new deliverables |
| Size | proposal: 4,544 lines, 512,328 bytes (this handback's own size is not recorded, because recording it would change it) |

HARD STOP: concrete Route 3 not established; OH-S3 R7 remediation awaits independent Codex re-review; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.
