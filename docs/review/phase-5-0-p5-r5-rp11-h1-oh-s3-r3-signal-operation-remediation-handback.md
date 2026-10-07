# Handback — OH-S3 R3 remediation: `HARD STOP: concrete Route 3 not established`

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R3-20261007-03`

Date: 2026-10-07

Executor: Claude Code (Sonnet 5.5) on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r3-signal-operation-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r3-signal-operation-remediation-claude-prompt.md),
**11173 bytes, SHA-256
`6fa0c1b9cf41942b16a4d15ba0ec55ab2c1418da0fa2e71564426631c7df46e3`**, recomputed
with `wc -c` and `sha256sum` before any edit and again at handback, and equal to the
pin in the
[authority record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r3-signal-operation-remediation-authority.md).
**The prompt and the authority are consumed by this return.**

Deliverable: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r3-signal-operation-remediation-proposal.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r3-signal-operation-remediation-proposal.md).

## 1. Terminal state

**`HARD STOP: concrete Route 3 not established`.** The prompt identity matched, so the
identity hard stop did not arise. The conditional hard stop of the OH-S3 R2 proposal
**remains in force and is unchanged**: repository evidence does not suffice to define a
Python-free, loader-free root path without inventing facts. R3 changes nothing about
that. It adds no new hard stop: the kernel, CPython and systemd facts that closing
R3-F1 needs are recorded as **proposed, version-bound obligations** on the future
citation gate (OH-S2b), as the prompt directs, and are not researched or asserted.

**Nothing is accepted by this return.** I have not claimed Codex's or Peter's
acceptance, have not proposed any successor for activation, have made no scope
decision and have created no authority. R1 and the OH-S3 R2 proposal are unchanged,
unaccepted and historical.

## 2. Finding remediated

| Finding | Remediation | Proposal |
|---|---|---|
| **R3-F1** (Important): the required blocking-operation inventory omits signal *sending* | One function, **SN**, performs every local signal send. Its inventory (table SN-I: the initial group-directed `SIGTERM`, the `SIGKILL` escalation, the `SIGKILL` of the PK subject, and the statement that cleanup and recovery send none); its class (**X** for the call, **C** for the attempts, never a wait and with no elapsed-time bound), distinguished from PID 1's class-**M** delivery; a **child handle** and the **pinning argument** (an unreaped child pins its PID and its group number) with validation as a detector only; a result table for success, `ESRCH`, permission and validation failures and every other error, none of which authorizes a pass, converts *unconfirmed* into confirmation or is hidden; the sequence after a failed or indeterminate send (reap wait of at most g read before the first send, then abandon, record, next recovery owner); the *effect-unknown* rule for mutating children; and 18 negative tests. Propagated through class E, HS-5, PK/2, SG-3, SG-4, SG-9, the terminal-cause map (rows 19, 20), the interruption maps (IM-S), the records, INV-12/-16/-17/-19 … 21, the residuals (RO-7), AP-0, the OH-S2b gate, Appendices A and B, and the review focus | §0.1, §0.5, §7.2 … §7.5a, §7.8, §7.9, §7.12, §8, §13, Appendices A, B, D |
| **R2-F2 item 1**, previously incomplete | the same inventory now includes the sending operation (§7.3 rows 3a … 3f) | §7.3, §7.5a, Appendix D |

The proposal's Appendix D maps every numbered item of R3-F1 and the amended R2-F2 (1)
row to its closing section.

## 3. Result in brief

* **No timing claim is strengthened.** A send is class X and is not a wait. g is read
  before the first send, so a slow send consumes it; W_show = c + g, W_series = P + c +
  g and N1 … N4 are unchanged and still bound only the helper's *waiting*. No parameter
  is added: the escalation interval is the existing `slice_ms`.
* **No send result is evidence.** Not exit, not reaping, not absence, not authorization.
  An expired deadline is `error` whatever the send results and whatever partial output
  arrived. After a failed or indeterminate send the helper waits for reaping at most g,
  then abandons the child, never signals it again and records it.
* **The reuse defence is stated as a proof obligation, not invented.** It is SI-2 with
  SI-3: an unreaped child pins its PID and group number *[proposed, PO-SN (b)]*, and one
  function is the sole reaper. If PO-SN (b) is refused, AP-0 is INVALID RUN. The accepted
  OH-S2 R2 record and the one-host design were searched by fixed string: **no accepted
  record cites `killpg`, `kill(`, `os.kill`, `ESRCH`, `pidfd` (as a behaviour),
  `start_new_session`, `setsid`, `process group` or `SIGCHLD`**. The record cites
  `FINAL_SIGTERM`/`FINAL_SIGKILL` "to what remains" and the `kill.c:13–16` defaults [R2
  §8 (e)].
* **Two consequences R3 surfaced and recorded, not hidden:** an abandoned child can
  outlive its helper with no automatic owner but PID 1's unit cleanup and the boot
  (RO-7; `attest` has none); and an abandoned *mutating* child (`systemd-run`,
  `systemctl stop`) may act late, so its effect after `error` is *unknown* (SN-10, CC-7).
  Whether CL's by-name disarm of the backstop timer is keyed to `backstop-intent` was
  **not re-read** and is a confirmation item for OH-S0d (Appendix A, A-I-16).
* **Seven consistency corrections are called out for review** (§0.5, CC-1 … CC-7). None
  changes a deadline class, a parameter, a sizing rule, PO-11 (d′), the Route 3 boundary,
  the SSW classification, an MF disposition or the hard stop.

## 4. Files changed

**Created** (untracked):

* `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r3-signal-operation-remediation-proposal.md`
* `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r3-signal-operation-remediation-handback.md` (this file)

**Updated, current-state pointers only** (tracked; the OH-S3 R3 paragraph changed from
"authorized and unexecuted" to "executed, hard stop"; the R3 authority and prompt
relabelled *Consumed*; proposal and handback links added; the heading or restriction
line updated):

* `docs/review/Handover information`
* `docs/project-management/status.md`
* `docs/implementation-plan.md`, §20 only (diff hunks begin at line 2574)
* `docs/operations/disposable-test-server.md`, the restriction banner and its link list only

**Pre-existing worktree changes.** Before my first edit `git status` showed six
modified tracked files (the four pointers above, plus `docs/project-management/change-log.md`
and `docs/project-management/decision-register.md`) and ten untracked files (the R1 prompt,
handback, proposal and authority; the R2 prompt, handback, proposal and authority; and this
assignment's prompt and authority). All were left by earlier work. The four pointers already
carried the uncommitted "OH-S3 R3 authorized" text, which I edited in place and otherwise
preserved. **I did not touch** `change-log.md`, `decision-register.md`, the R1 and R2 files,
this assignment's prompt or its authority.

**Not edited:** R1 and the OH-S3 R2 proposal, handback, prompt and authority; any accepted
historical evidence; the operational draft; any source, test, configuration, service file
or migration; any archive snapshot or archive index; the decision register; the change log.
The SHA-256 of eleven unchanged inputs was recorded before the first edit and compared at
the end (§8).

## 5. Repository documents consulted

**Read completely:** `.agents/AGENTS.md`; this assignment's prompt and authority; the R2
prompt and the R2 authority; `docs/review/Handover information`; the **complete** OH-S3 R2
proposal (2,576 lines) and the **complete** OH-S3 R2 handback; the restriction banner of
`docs/operations/disposable-test-server.md`; the §20 pointer of
`docs/implementation-plan.md`; and `docs/project-management/status.md`.

**Read by section:** `docs/implementation-plan.md`: the reading map; §0.1 … 0.5; §14.1 …
14.3; §16 in full; §17 in full; §20 in full.

**By fixed-string search only, over the two named documents** `phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md`
and `phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`: `killpg`,
`os.kill`, `kill(`, `ESRCH`, `pidfd`, `start_new_session`, `setsid`, `process group`,
`SIGCHLD`, `KillMode`, `control-group`, `FINAL_SIGTERM`, `SendSIGKILL`, `kill.c:13`,
`backstop-intent`, `pk-root/1` and the HF-04 kernel identifier, with the matching lines
printed.

**Not re-read in R3, and said so in the proposal (§1.1):** the R1 prompt, authority,
proposal and handback (R3-F1 carries no R1-only obligation; their unchanged state is
checked by digest); the accepted OH-S2 R2 record beyond those searches (the proposal's
citations of it are carried from the OH-S3 R2 proposal, not re-verified); the accepted
OH-S2 R2 handback and acceptance; the one-host design beyond those searches; the
operational draft (Appendix B's row identifiers are carried from the OH-S3 R2 proposal;
its digest was recorded and compared). The prompt asks for the accepted records "only at the
exact sections cited by R2" and for the operational draft "as a future consumer"; I limited
myself to the searches above because R3-F1 concerns one operation that those records do not
describe, and I report the limit rather than imply a fuller reading.

## 6. Commands and checks run

Every command named exact files or one named directory. None was recursive over the
repository, a workspace root, home, `/opt`, `/var`, `/tmp` or `/`.

| # | Command or tool (targets) | Result |
|---|---|---|
| 1 | `wc -c`, `sha256sum` on the prompt; read of the authority | `11173`; `6fa0c1b9…46e3`: **equal** |
| 2 | `git status` (session start) and `git status --short` | the pre-existing state of §4 |
| 3 | file reads of the documents in §5, by named path and line range | read as listed |
| 4 | `grep -cF` and `grep -nF` of the two named accepted documents for the terms of §5 | counts and lines as cited in proposal §7.5a.8 |
| 5 | `sha256sum` of eleven named files (R1 proposal, handback, prompt, authority; the OH-S3 R2 proposal, handback, prompt, authority; the accepted OH-S2 R2 record; the one-host design; the operational draft), saved to a scratchpad file | recorded before the first edit |
| 6 | `cp` of the OH-S3 R2 proposal to the R3 proposal path, then `cmp` | identical (the prompt recommends copying R2 and amending it) |
| 7 | `python3 -I` scripts in the session scratchpad that apply 73 exact-count replacements (each asserts that its anchor occurs exactly once, and stops otherwise), then smaller `python3 -I` edits | applied (see the disclosures below) |
| 8 | `python3 -I` check of Markdown table row widths; `diff`; `grep -n` scans of the R3 proposal | see §8 |
| 9 | `python3 -I` edits of the four pointer files, each with exact-anchor assertions | applied |
| 10 | the final checks of §8 | see §8 and §13 |

**Disclosed mistakes, each caught by a check and repaired before handback.**

* The first run of the replacement script stopped on an assertion (a row prefix I had
  already rewritten) **before it wrote anything**; I corrected the anchor and reran it.
* My first pointer script stopped on an assertion (the handover labels its prompt link
  "Claude prompt", the other files do not) **before it wrote anything**; I made the link
  fix tolerant of both labels and reran it.
* The table-width check found that my 17 new negative-test rows had four columns in a
  three-column table; I merged each setup into its Case cell.
* A scan for leftover direct-kill wording found three sentences of the OH-S3 R2 text that I
  had not amended (the PK call line, the definition of g, NT-PK-1); I amended them.
* A review of propagation found that AP-0's acceptance list and the §11 citation slice did
  not yet name PO-SN, and that the AP-0 gate had no test; I added both and NT-SN-18 (the
  count is therefore 18, not 17).

**Scratchpad files.** Helper scripts and text blocks (`blocks_a.py`, `blocks_b.py`,
`blocks_c.py`, `apply.py`) and the baseline digest file are in this session's scratchpad
directory, outside the repository. They are not deliverables. I took no cleanup action.

**No guard refusal occurred.** `.claude/hooks/guard-secrets.py` and `guard-git.py` refused
nothing, and no command text contained a secret-bearing file name pattern.

## 7. Checks not run, and why

* No SSH or other host connection, `oracle-test`, production, staging, Foundry or database
  access, and no retained-evidence access: forbidden.
* No application test, hook test (`python3 .claude/hooks/test_guards.py`), formatter, build,
  package tool, network check or remote-host check: forbidden, and this is a documentation
  slice. `run-suites` does not apply.
* **No citation, observation or measurement of any kernel, libc, CPython or systemd
  behaviour.** Every such statement in the proposal (PO-SN (a) … (f)) is **proposed**, and
  the source files named there are proposed citation targets that I did not read.
* No re-verification of the OH-S3 R2 proposal's own citations of the accepted record.
* No byte-level inspection of any launcher image; PO-17 stays unevaluated.
* No network research. No third-party artifact was selected.
* No re-read of the operational draft or of the one-host design's CL disarm step (see §3).
* **No measurement of the size or effort of a Python-free root path** (WP-7).

## 8. Final checks

All operated on the six allowed files, listed explicitly.

| Check | Result |
|---|---|
| Prompt identity, re-checked at handback | `11173`; `6fa0c1b9…46e3`: equal (§13) |
| Unchanged inputs (eleven files) | 11 of 11 digests equal (§13) |
| Scan of the R3 proposal for the local signal-sending operation, PID 1's delivery, `SIGTERM`, `SIGKILL`, `ESRCH`, identity and reuse handling, reap, abandon, evidence fields, residuals and negative tests | all present: §7.5a (SN-I, SN-R, SN-S, SN-RO), §7.3 rows 3a … 3f, §5.6 RO-7, §8.5 `children`, §7.12 NT-SN-1 … 18 |
| Every send outcome fails closed; no send success is treated as proof of exit or reaping | SN-7 and INV-20 state it; table SN-R has ten rows, each leaving the enclosing result unchanged; NT-SN-13 is a property test of it; "sent" is defined as "queued", never as exit |
| Route 3 boundary, SSW classification, MF-1 … MF-8 dispositions and the hard stop unchanged | the text of §2, §6, §9.1 … 9.2, §9.4, §9.6 … 9.13, §10 and §12 is **byte-identical** to the OH-S3 R2 proposal (compared section by section). The only edits inside §9 are one clause each in E-3, WP-2 and WP-4. §11 differs only by PO-SN in slice 2a and in readiness item 2; its order and gates are unchanged |
| Every non-mechanical change is necessary to close R3-F1 | the diff against the OH-S3 R2 proposal removes or rewrites 71 lines and adds 589 (§13); every changed section is listed in §0.5 (sections changed, CC-1 … CC-7). No unrelated R2 content was altered |
| Table row widths, both deliverables | see §13 |
| Trailing whitespace, six files | see §13 |
| Links introduced in the six files, from an explicit target list | see §13 |
| `git diff --check`, four tracked pointers and two new deliverables | see §13 |
| Six-file diff review | the four pointers differ from their pre-start state only by the heading or restriction line, the one replaced R3 paragraph, the relabelled authority and prompt links and the added proposal and handback links; the plan's hunks lie only in §20. The two deliverables are new files. A scan for authority language found no host, implementation, successor, cleanup, credential, secret, commit or push authority granted or implied: every occurrence states that nothing is authorized, names a design object (for example *not authorized*, PK's result) or refers to a future separately authorized slice |

## 9. Security implications

* **No new attack surface is created by this return.** It is documentation.
* **What the proposal changes, if accepted later:** every signal a root helper sends goes
  through one function, to a validated, unreaped child of its own, from a two-signal set,
  one attempt each, never from a handler or from the grant-removal path; no send result is
  read as evidence; a child that cannot be ended is abandoned, recorded and never signalled
  again. Each change **narrows** what can succeed. The risk it addresses is a signal
  reaching an unrelated process after a PID or group reuse; its defence rests on a kernel
  property (PO-SN (b)) that **no accepted record cites**, so the contract is conditional:
  AP-0 is INVALID RUN until it is accepted.
* **What it does not close, stated by name** (proposal §13.1): **X-1** for the root roles
  until Route 3 is established; RO-1 … RO-6; CX-5; HB-1; and the new **RO-7**: an
  abandoned or unsignalled child has no automatic owner except PID 1's unit cleanup and the
  boot, and `attest` has none. An abandoned `systemd-run` or `systemctl stop` may act late.
* **Elapsed-time honesty.** No statement implies a time for a send, a validation or the
  SN sequence; the only times stated are c, g and `slice_ms` as waits.
* **Route 3 is not established.** The accepted disposition stands: Route 1 returns to Route
  3 design review, PO-12 and AS-8 are refuted, PO-19 stays not established.
* **No secret, credential or player datum was read**, and no secret-bearing path was opened
  or named.

## 10. Unresolved decisions

* **For Peter, only after a clean independent review** (proposal §12.1): DEC-1 … DEC-6 as in
  the OH-S3 R2 proposal, unchanged. R3 adds **no decision**. DEC-6's signal and removal
  discipline now includes SG-9 and the SN contract, and the proposal treats the SN contract
  as part of what DEC-6 would adopt; whether to state that more explicitly is a review
  question (§14.1 Q15).
* **New acceptance gate, not a decision:** PO-SN (a), (b), (c), (e), (f) must be accepted
  for the observed versions at OH-S2b before AP-0 can proceed.
* **Route 3 direction** (G-1b) and the **boundary changes** BC-1 … BC-5 (proposal §12.2):
  unchanged and not made by this return.
* **Confirmation item for OH-S0d:** whether CL's by-name disarm of the backstop timer is
  keyed to `backstop-intent` as well as `backstop-armed` (Appendix A, A-I-16).

## 11. Proposed independent-review focus

Proposal §14.1 Q15 and Q5 first. In particular: (1) whether table SN-I is complete, with
no send by `spawn()`, another helper, cleanup or recovery omitted; (2) whether the pinning
argument (SI-2, SI-3) with PO-SN (b) and (c) is sufficient and whether validation is rightly
a detector only; (3) whether an escalation `SIGKILL` that does not depend on the clock (S4),
a reap wait that a flag does not shorten (CC-2) and the interpretation of `slice_ms` as the
escalation interval are right; (4) whether any statement still reads a send result as
evidence (search for "killed", "terminated", "dead", "gone"); (5) whether SN-10's
*effect-unknown* rule is enough for `systemd-run` and `systemctl stop`, and whether RO-7's
lack of an owner for `attest` is acceptable; (6) whether PO-SN (a) … (f) are the right facts
and AP-0's refusal until they are accepted is the right consequence; and (7) that CC-1 …
CC-7 are each necessary and none strengthens or silently weakens an OH-S3 R2 claim. The
claims needing independent **security** re-review are proposal §14.2 SR-1 … SR-12, SR-12
being new.

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
| Prompt identity, last run | `11173`; `6fa0c1b9…46e3`: equal |
| Unchanged inputs: the R1 proposal, handback, prompt and authority; the OH-S3 R2 proposal, handback, prompt and authority; the accepted OH-S2 R2 record; the one-host design; the operational draft | `sha256sum -c` against the digests taken before the first edit: **11 of 11 OK**, 0 failed |
| Trailing whitespace, six files | 0 lines in each |
| Link check, six files: the 46 distinct targets were collected first and seen to be project documentation under `docs/` only, then tested for existence | 123 links checked, **0 broken** |
| Markdown table row widths | proposal: 71 tables, 0 mismatches; handback: 3 tables, 0 mismatches |
| `git diff --check`, four tracked pointers | exit 0, no output |
| `git diff --check --no-index`, the two new deliverables | exit 1 (differences exist) and **no whitespace error reported** |
| Diff of the R3 proposal against the OH-S3 R2 proposal | 71 lines removed or rewritten, 589 added; every one belongs to a section listed in proposal §0.5 |
| Size | proposal: 3,094 lines, 282,418 bytes; handback: 283 lines, 21,339 bytes |

HARD STOP: concrete Route 3 not established; OH-S3 R3 remediation awaits independent Codex re-review; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.
