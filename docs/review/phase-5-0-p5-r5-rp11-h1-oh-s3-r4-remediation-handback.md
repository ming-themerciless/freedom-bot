# Handback — OH-S3 R4 remediation: `HARD STOP: concrete Route 3 not established`

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R4-20261007-04`

Date: 2026-10-07

Executor: Claude Code (Sonnet 5.5) on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r4-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r4-remediation-claude-prompt.md),
**12569 bytes, SHA-256
`3d9279b689dd14d527c6c139e9ba674918ecb1fe60b1efa384114c1d7f04ca55`**, recomputed
with `wc -c` and `sha256sum` before any edit and again at handback, and equal to the
pin in the
[authority record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r4-remediation-authority.md).
**The prompt and the authority are consumed by this return.**

Deliverable: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r4-remediation-proposal.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r4-remediation-proposal.md).

## 1. Terminal state

**`HARD STOP: concrete Route 3 not established`.** The prompt identity matched, so the
identity hard stop did not arise. The second defined hard stop, `HARD STOP: OH-S3 R4
remediation requires maintainer direction`, **did not arise**: closing R4-F1 and R4-F2
needed no scope or design decision beyond this assignment. The conditional hard stop of the
OH-S3 R2 and R3 proposals **remains in force and is unchanged**.

**Nothing is accepted by this return.** I have not claimed Codex's or Peter's acceptance,
have not proposed any successor for activation, have made no scope decision and have
created no authority. R1, R2 and R3 are unchanged, unaccepted and historical.

## 2. Findings remediated

| Finding | Disposition | Proposal |
|---|---|---|
| **R4-F1** (Important): the send sequence can exceed its stated wait budget | **Closed in the proposal, not accepted.** One absolute `t_g`, read once before the first validation or send (WB-1). Every sleep in S3 and S5 is capped by the time remaining to it, and, as the one extension I flag for review, every sleep of every E wait against its own deadline (WB-2, CC-10). No timed wait begins at or after `t_g`, with a `≥` comparison (WB-3). S4's identity-validated, at-most-once `SIGKILL` is **not a wait and is not skipped**; it may fall after `t_g`, is recorded `late` and is not presented as completion within g (WB-4). Boundary ordering is one non-blocking **reap attempt** (class X, never a wait) in the order clock, attempt, decision, with explicit results for a child already reaped, one that exits during a send, and one still unreaped at the deadline (the *final attempt* of S5, WB-5). The wait budget (scheduled sleeps, at most g) is stated separately from elapsed time, which is unbounded (WB-6); no new grace period starts after a send, validation, poll, error or signal receipt (WB-7). Table SN-S is rewritten and a case table is added. R3's sentences "everything from S0 to S6 sits inside g", "both signals sit inside g", and the `slice_ms`-after-`SIGTERM` escalation are withdrawn (W-14). Dependent text corrected: CC-1, CC-2, SN-R rows 1, 2, 4 … 8, 10 (row 11 added), SN-6, SN-7, SN-8, HS-5, PK/2, SG-4, §7.2 class E, §7.3 rows 2, 3, 3a, 3b, 3e, 3g (new), 7, 14, the parameter notes, INV-16 and INV-22, Appendices A and B | §0.1, §0.6, §7.2, §7.3, §7.5, §7.5a.4 … §7.5a.6b, §7.6, §7.7, §7.8, §8.6 |
| **R4-F2** (Important): the interruption map assumes successful signal delivery | **Closed in the proposal, not accepted.** IM-S is rewritten: rules IS-1 … IS-8 (*sent* means only the kernel's return; only a recorded reap status proves the direct child reaped and never an empty group; the target may remain alive after any send; the state is never a function of a send result; the boot is a separate event); eight interruption points T0 … T7 that follow table SN-S; six send outcomes (`u` unmade, `i` identity-rejected, `x` indeterminate, `s`, `e`, `f`); a common child-state set CS-1 … CS-8 separating sends already attempted from the absence of further sends by the ended helper; and a point × outcome matrix covering validation failure, `ESRCH`, other errors, partial escalation, death during a send, reaping and abandonment. Ownership follows the enclosing procedure in the amended table SN-RO (holder, CP, stop-post, backstop service, interactive `attest`), with the unit rows resting on the proposed PO-SN (e) and **`attest` explicitly keeping no automatic owner**. R3's "unsignalled by anyone", "signalled", "killed, or alive in an uninterruptible call" and the "as S0" / "as S3" row references are withdrawn (W-14). Propagated to terminal-cause rows 19 and 20, RO-7, the `children` record (new fields, new condition `children-unknown`), INV-18, -20, -21, -23, review questions Q16 and Q17, SR-13, Appendix A (A-I-16, new A-I-17) and Appendix B (B-08, B-13). Mutating-child effect stays `unknown`, the enclosing result stays fail-closed, no retry and no process hunting is granted | §0.1, §0.6, §5.5, §5.6, §7.5a.7, §7.5a.9, §7.9, §8.5, §8.6, §14 |

The proposal's Appendix D maps every numbered item of both findings to its closing section.

## 3. Result in brief

* **A wait budget is not an elapsed-time bound, and the proposal now says so once.** The
  scheduled sleeps of one signalled child total at most g. The sequence's elapsed time
  includes validations, send calls, reap attempts and journal writes and has no bound; it
  may exceed g. No sizing rule (N1 … N4) becomes a completion guarantee. **No parameter
  value changes.**
* **Back-to-back signals are accepted, not hidden.** When the grace is spent before
  `SIGTERM` returns, S4 still sends `SIGKILL` once, so the two signals may follow one
  another with no sleep between them. R3 preserved S4 as clock-independent; R4 keeps that
  and records it as `late`.
* **No send result is evidence, including the loss of one.** An interruption inside a send
  is its own outcome (`x`); the matrix gives it the same state as `sent`, `esrch` and a
  failure. A reap status concerns the direct child only.
* **A later procedure cannot know which child was lost.** For states CS-1 … CS-6 no `child`
  line is durable. The only thing a later procedure can see is a missing terminal journal
  line, from which it records `children-unknown`. Which line marks a helper's complete end
  is a confirmation item for OH-S0d (A-I-17).
* **Eight consistency corrections are called out for review** (§0.6, CC-8 … CC-15). None
  changes a deadline class, a parameter value, a sizing rule, PO-11 (d′), the Route 3
  boundary, the SSW classification, an MF disposition or the hard stop. **CC-10 goes one
  step beyond the finding**: it applies the sleep cap to every E wait, because W_show = c +
  g is a budget of scheduled waiting and the child wait to c is its first term. The
  proposal asks the reviewer to confirm or reject it (Q16); rejecting it adds up to one
  `slice_ms` to each of W_show and W_series.

## 4. Files changed

**Created** (untracked):

* `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r4-remediation-proposal.md`
* `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r4-remediation-handback.md` (this file)

**Updated, current-state pointers only** (tracked; the OH-S3 R4 paragraph changed from
"authorized and unexecuted" to "executed, hard stop"; the R4 authority and prompt are
labelled *Consumed*; proposal and handback links added; the heading or restriction line
updated):

* `docs/review/Handover information`
* `docs/project-management/status.md`
* `docs/implementation-plan.md`, §20 only (diff hunks begin at line 2574, inside §20, which starts at line 2558)
* `docs/operations/disposable-test-server.md`, the restriction banner and its link list only

**Pre-existing worktree changes.** Before my first edit `git status` showed six modified
tracked files (the four pointers above, plus `docs/project-management/change-log.md` and
`docs/project-management/decision-register.md`) and ten untracked files (the R1, R2 and R3
prompts, handbacks, proposals and authorities as applicable, and this assignment's prompt
and authority). All were left by earlier work. The four pointers already carried the
uncommitted "OH-S3 R4 authorized" text, which I edited in place and otherwise preserved. **I
did not touch** `change-log.md`, `decision-register.md`, the R1, R2 or R3 files, this
assignment's prompt or its authority.

**Not edited:** R1, the OH-S3 R2 proposal and the R3 proposal, handback, prompt and
authority; any accepted historical evidence; the operational draft; any source, test,
configuration, service file or migration; any archive snapshot or archive index; the
decision register; the change log. The SHA-256 of nineteen unchanged inputs was recorded
before the first edit and compared at the end (§8, §13).

## 5. Repository documents consulted

**Read completely:** `.agents/AGENTS.md`; the R4 prompt and its authority; the R3 prompt
(lines 38 … 197, which contain its required reading, finding, deliverables and verification;
the title block above it was not re-read) and the R3 authority; `docs/review/Handover
information`; the **complete** R3 proposal (3,094 lines, read in seven passes) and the
**complete** R3 handback (283 lines); the restriction banner of
`docs/operations/disposable-test-server.md` (lines 1 … 80); and `docs/project-management/status.md`
(lines 1 … 125).

**Read by section:** `docs/implementation-plan.md`: the reading map (lines 19 … 52), §0.1 …
0.5 (lines 53 … 183), §14.1 … 14.3 (lines 2216 … 2251), §16 in full (lines 2394 … 2490),
§17 (lines 2492 … 2512) and §20 in full (lines 2558 to the end).

**By fixed-string search or the exact lines named, over named documents only:** the OH-S3 R2
proposal (anchors `reap_grace_ms`, `IM-L`, `SG-4`, `W_show`; its §7.9 opening, lines 1318 …
1330); the accepted OH-S2 R2 citation record (rows (c), (e), (j) of §8, lines 699 … 706, rows
(e) and (j) printed in full); the one-host design (`BS-2`, `BS-3`, `backstop-intent`,
`backstop-armed`, `disarm`, `by name`, `-backstop.timer`, with lines 1968 … 1972 printed); and
the operational draft (headings by fixed pattern; §11.2, §11.3 and the opening of §14, lines
1344 … 1362 and 1459 … 1478), without editing it.

**Not re-read in R4, and said so in the proposal (§1.1):** the R1 prompt, authority, proposal
and handback and the R2 prompt, authority and handback (their unchanged state is checked by
digest); the accepted OH-S2 R2 record beyond the rows named; the one-host design beyond the
searches; the operational draft beyond the three places named (Appendix B's other row
identifiers are carried from R3). The prompt asks for the R2 proposal "as needed for
consistency"; I limited it to the anchors above because R3 is cumulative and its carried
text was checked by section against the R4 text (§8). **Carried citations are carried, not
re-verified:** every `[R2 §n]` and `[D §n]` citation of R3 that R4 did not touch.

**One carried confirmation item was re-searched and not resolved.** R3's A-I-16 left open
whether CL's by-name disarm of the backstop timer is keyed to `backstop-intent`. R4's fixed
searches of the one-host design found the timer's disarm only in BS-2 and BS-3, performed by
the backstop on a terminal `deact` record, and **no CL step that disarms it by name**. The
item therefore stays open for OH-S0d and is widened in A-I-16.

## 6. Commands and checks run

Every command named exact files or one named directory. None was recursive over the
repository, a workspace root, home, `/opt`, `/var`, `/tmp` or `/`.

| # | Command or tool (targets) | Result |
|---|---|---|
| 1 | `wc -c` and `sha256sum` on the R4 prompt; read of the authority | `12569`; `3d9279b6…4ca55`: **equal** |
| 2 | `git status --short` (before the first edit) | the pre-existing state of §4 |
| 3 | file reads of the documents in §5 by named path and line range | read as listed |
| 4 | `sha256sum` of nineteen named files (the R1 proposal, handback, prompt, authority; the R2 proposal, handback, prompt, authority; the R3 proposal, handback, prompt, authority; the accepted OH-S2 R2 record; the one-host design; the operational draft; the R4 prompt and authority; `change-log.md`; `decision-register.md`), saved to the session scratchpad | recorded before the first edit |
| 5 | `cp` of the R3 proposal to the R4 proposal path, then `cmp`; the R3 proposal also copied to the scratchpad | identical (the R3 prompt recommended the same method and the R4 prompt requires a cumulative document) |
| 6 | `grep -F` and `sed -n` over the named documents (§5) | as reported in §5 |
| 7 | the editor's exact-string replacement (the `apply_patch` tool named by the prompt is not available in this environment) for the larger edits, and `python3 -I` scripts in the session scratchpad for the table and multi-row edits, each asserting that its anchor occurs exactly once and writing nothing otherwise | applied; see the disclosures below |
| 8 | `python3 -I` check of Markdown table row widths; `diff` and a section-by-section `difflib` comparison of the R3 and R4 proposals; `grep -n` scans of the R4 proposal for stale wording | see §8 and §13 |
| 9 | `python3 -I` edit of the four pointer files, with exact-anchor assertions | applied |
| 10 | the final checks of §8 and §13 | see there |

**Disclosed mistakes, each caught by a check and repaired before handback.**

* The first attempt to extend §0.3 failed on an anchor mismatch and wrote nothing; I read the
  exact text and repeated it.
* A multi-replacement script stopped on an assertion (the SN-8 anchor wrapped differently from
  my copy) before it wrote anything; I corrected the anchor and reran it.
* A scan for the superseded wording found sentences of R3 that I had not amended: a PK/2
  sentence ("the subject is not reaped within g"), the definition of g in §7.5a.2, AW-3's
  "PK/2 waits end by P + c + g", and the R3-F1 bullet's "reap wait of at most g". I amended
  each.
* The same scan found two sentences that read a `SIGKILL` send as the end of a child ("is
  terminated after each call", PK/2 and NT-LD-9). They were R3 text and exactly the
  inference R4-F2 prohibits; I rewrote both.
* My first definition of the *final attempt* ("the first reap attempt that begins at or
  after `t_g`") could have let an attempt of S3 end the sequence before S4's `SIGKILL`; I
  corrected it to the attempt of S5 (WB-5 (c)).
* The first draft of the §0.6 table omitted six sections the comparison showed I had changed
  (§7.5a.2, §8.2, §9.5, §11 and two row groups); I added them. The comparison now accounts
  for every changed section (§8).

**Scratchpad files.** Helper scripts and the digest baseline are in this session's
scratchpad directory, outside the repository. They are not deliverables. I took no cleanup
action.

**No guard refusal occurred.** `.claude/hooks/guard-secrets.py` and `guard-git.py` refused
nothing, and no command text contained a secret-bearing file name pattern.

## 7. Checks not run, and why

* No SSH or other host connection, `oracle-test`, production, staging, Foundry or database
  access, and no retained-evidence access: forbidden.
* No application test, hook test (`python3 .claude/hooks/test_guards.py`), formatter, build,
  package tool, network check or remote-host check: forbidden, and this is a documentation
  slice. `run-suites` does not apply.
* **No test of the 27 proposed regression cases.** NT-WB-1 … 12 and NT-IS-1 … 15 are defined
  on paper only; nothing was implemented or executed, and none of the fake-clock arithmetic
  in the case table of §7.5a.6b has been run.
* **No citation, observation or measurement of any kernel, libc, CPython or systemd
  behaviour.** PO-SN (a) … (g) stay **proposed**, and the source files named there are
  proposed citation targets that I did not read.
* No re-verification of the R3 proposal's own citations of the accepted record.
* No byte-level inspection of any launcher image; PO-17 stays unevaluated.
* No network research. No third-party artifact was selected.
* No resolution of the CL-disarm confirmation item (see §5).
* **No measurement of the size or effort of a Python-free root path** (WP-7).

## 8. Final checks

All operated on the six allowed files, listed explicitly.

| Check | Result |
|---|---|
| Prompt identity, re-checked at handback | `12569`; `3d9279b6…4ca55`: equal (§13) |
| Unchanged inputs (nineteen files) | 19 of 19 digests equal (§13) |
| R3 proposal still identical to the copy taken before the first edit | `cmp` equal |
| R4-versus-R3: every content change closes R4-F1 or R4-F2 or is a directly necessary consistency correction | the section-by-section comparison attributes every changed region to a section listed in proposal §0.6 (sections changed; CC-8 … CC-15). The sections that are byte-identical to R3 include §2, §4, §6, §7.1, §7.10, §10 and §12, and §9 differs only by the WP-4 clause |
| Scan of SN-S, SN-R, IM-S, SN-RO, CC-1/CC-2, HS-5, PK/2, SG-4, records, invariants, residuals and Appendix A/B obligations | each was read in full after the final edit; the cross-checks of the next four rows were made against them |
| No wait after `t_g` | WB-3 (comparison `≥`), table SN-S (S3 tests `now < t_g`; S5 sleeps only if `now < t_g`), the case table, NT-WB-2, -3, -5, -6, -11 (ii) |
| No restarted grace period | WB-1 (read once), WB-7, SN-6, INV-22, NT-WB-11 (i); the strings "read before the first send" are the only grace reads and refer to the same single read |
| No class-X time bound | §7.2, §7.3 rows 3a … 3g, WB-6, §7.5a.10, INV-16, NT-WB-12, NT-SN-17; the remaining occurrences of "within g" and "inside g" are negations or withdrawals (a scan lists them) |
| No send-result inference of exit or reaping | IS-1 … IS-5, SN-7, INV-20, the matrix (same state for `x`, `s`, `e`, `f`); two R3 sentences that read a send as a child's end were rewritten (§6) |
| No missing `attest` owner case | SN-RO's `attest` row, the owner and record table in §7.9, IS-6, INV-23, NT-IS-11, Appendix B-13 |
| Route 3 boundary, SSW classification, MF dispositions, decisions, successor order, hard stop retained | §2, §4, §6, §10 and §12 byte-identical to R3; §9 differs only by one clause in WP-4; §11 only by the optional PO-SN (g) in slice 2a; SSW is still a scope-change alternative that is not Route 3 |
| Table row widths, both deliverables | see §13 |
| Trailing whitespace, six files | see §13 |
| Links introduced in the six files, from an explicit target list | see §13 |
| `git diff --check`, four tracked pointers and two new deliverables | see §13 |
| Six-file diff review | the four pointers differ from their pre-start state only by the heading or restriction line, the one replaced R4 paragraph, the added proposal, handback, authority and prompt links; the plan's hunks lie only in §20. The two deliverables are new files. A scan for authority language found no host, implementation, successor, cleanup, credential, secret, commit or push authority granted or implied: every occurrence states that nothing is authorized, names a design object (for example PK's *not authorized*) or refers to a future separately authorized slice |

## 9. Security implications

* **No new attack surface is created by this return.** It is documentation.
* **What the proposal changes, if accepted later:** a helper that signals its own children
  can no longer wait past its single grace deadline after a slow send, and can no longer
  describe the state of a child after an interruption as a function of whether a signal
  was sent. Each change **narrows** what can succeed or be claimed. The risk the second
  change addresses is a recovery step, or a reviewer, treating a child as gone because a send
  returned 0 or `ESRCH`, and so releasing something that is still running; its defence is a
  state set that does not depend on any send result.
* **What it does not close, stated by name** (proposal §13.1): **X-1** for the root roles
  until Route 3 is established; RO-1 … RO-6; CX-5; HB-1; and **RO-7**, now widened: a child
  left behind by its helper **may be alive**, its owner is the owner of its enclosing
  procedure, and the interactive `attest` has none. An abandoned `systemd-run` or `systemctl
  stop` may act late.
* **A residual that R4 makes visible rather than closes:** when a helper is ended before it
  settles a child, no later procedure can know which child it was or what was sent. It
  records only that its terminal journal line is missing (`children-unknown`), and the
  design promises no more.
* **Back-to-back signals.** After a slow send or validation `SIGTERM` and `SIGKILL` can be
  sent with no sleep between them. That removes `SIGTERM`'s grace in the slow case; it does
  not change the signal set, the attempt counts or the identity validation.
* **Elapsed-time honesty.** No statement implies a time for a send, a validation, a reap
  attempt or the sequence's return; the only times stated are c, g and `slice_ms`, as
  scheduled waits.
* **Route 3 is not established.** The accepted disposition stands: Route 1 returns to Route
  3 design review, PO-12 and AS-8 are refuted, PO-19 stays not established.
* **No secret, credential or player datum was read**, and no secret-bearing path was opened
  or named.

## 10. Unresolved decisions

* **For Peter, only after a clean independent review** (proposal §12.1): DEC-1 … DEC-6 as in
  the R3 proposal, unchanged. R4 adds **no decision**.
* **For the reviewer (Q16):** whether CC-10 (the sleep cap on every E wait) is accepted or
  confined to S3 and S5. Rejecting it widens W_show and W_series by up to one `slice_ms`
  each and changes no other statement.
* **Citation gate, not a decision:** PO-SN (a), (b), (c), (e), (f) must be accepted for the
  observed versions at OH-S2b before AP-0 can proceed (unchanged from R3). PO-SN (g) is
  optional and nothing relies on it.
* **Route 3 direction** (G-1b) and the **boundary changes** BC-1 … BC-5 (proposal §12.2):
  unchanged and not made by this return.
* **Confirmation items for OH-S0d:** the CL by-name disarm (A-I-16, widened) and which
  terminal journal line marks each helper's complete end (A-I-17).

## 11. Proposed independent-review focus

Proposal §14.1 Q16 and Q17 first. In particular: (1) whether any timed wait can still begin
at or after `t_g`, or any send, validation, poll, error or signal receipt can start another
grace period (search "grace", "wait", "poll", "sleep", "slice"); (2) whether S4's
unconditional, at-most-once `SIGKILL`, and its back-to-back use after a spent grace, is the
right reading of "preserve the existing escalation decision"; (3) whether the final-attempt
rule (WB-5) is well defined for a child that exits during a send, at the boundary or just
after it, and whether a reap attempt that raises is rightly read as *unreaped*; (4) whether
the wait budget is now free of any residual claim that a sequence returns within g; (5)
whether every cell of the IM-S matrix agrees with table SN-S and every dash is unreachable;
(6) whether CS-1 … CS-8 is free of any state derived from a send result, a boot or a reap of
the direct child; (7) whether the owners of table SN-RO are right and the absence of an
automatic owner for the interactive `attest` is acceptable as stated; (8) whether
`children-unknown`, derived from a missing terminal journal line, is a sound way to report a
lost record without searching; (9) whether the claim in rows 19 and 20 of §5.5, that a
flag-driven end leaves its children settled while an exception inside an E wait does not,
is right; and (10) that CC-8 … CC-15 are each necessary and none strengthens or silently
weakens an R3 claim. The claims needing independent **security** re-review are proposal
§14.2 SR-1 … SR-13, SR-13 being new.

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
| Prompt identity, last run | `12569`; `3d9279b6…4ca55`: equal |
| Unchanged inputs: the nineteen files of §6 row 4 | `sha256sum -c` against the digests taken before the first edit: **19 of 19 OK**, 0 failed |
| Trailing whitespace, six files | 0 lines in each |
| Link check, six files: every `](…)` target was extracted, resolved against its file's directory and tested for existence | 149 links checked, **50 distinct targets, all under `docs/`, 0 missing** |
| Markdown table row widths | proposal: 78 tables, 0 mismatches; handback: 4 tables, 0 mismatches |
| `git diff --check`, four tracked pointers | exit 0, no output |
| `git diff --check --no-index`, the two new deliverables | exit 1 (differences exist) and **no whitespace error reported** |
| Diff of the R4 proposal against the R3 proposal | 157 lines removed or rewritten, 657 added; every one belongs to a section listed in proposal §0.6 |
| Size | proposal: 3,594 lines, 351,578 bytes (this handback's own size is not recorded, because recording it would change it) |

HARD STOP: concrete Route 3 not established; OH-S3 R4 remediation awaits independent Codex re-review; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.
