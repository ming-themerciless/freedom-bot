# Proposal — OH-S3 R7: repaired activation design with enforced-deadline cleanup claims, a complete signal-sending contract, a send sequence that cannot outrun its wait budget, an interruption map that covers the interior of a reap attempt, slow-validation cases that state their own clock, a reap error that never licenses a later signal, a send sequence whose `not-sent` branches agree with its interruption map, a grace deadline that exists exactly when S0 ran, a sole-reaper contract that claims no reuse safety once it is violated, a child-handle vocabulary with all four states, and the Route 3 alternatives record

**Terminal state: `HARD STOP: concrete Route 3 not established`.**

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R7-20261007-07`

Date: 2026-10-07

Executor: Claude Code (Sonnet 5.5) on the production workspace controller
(`/opt/freedom-blades/platform`, branch `docs/platform-plan`)

Independent reviewer: Codex · Decision owner: Peter Duscha

Prompt: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r7-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r7-remediation-claude-prompt.md),
**13330 bytes, SHA-256
`749dc19eb87ab867d3c075ddd7786667c7501bf46c542c8a29b421466e166c35`**,
recomputed with `wc -c` and `sha256sum` before any edit and equal to the pin in the
[authority record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r7-remediation-authority.md).

Durable handback: [`phase-5-0-p5-r5-rp11-h1-oh-s3-r7-remediation-handback.md`](phase-5-0-p5-r5-rp11-h1-oh-s3-r7-remediation-handback.md).

**R7 (Δ7).** This document **supersedes the OH-S3 R6 proposal as the cumulative forward
candidate** and is self-contained. It is the R6 proposal with **three focused
remediations: R7-F1** (the pre-S0 `reap-error` path had no defined grace-deadline record:
the new §7.5a.6e GD-1 … GD-5, S0's entry condition, RE-4, SN-6, WB-1, INV-22, the record
schema and the cases NT-GD-1 … 4 with NT-RE-7, NT-RE-11, NT-RE-12 and NT-SN-9 corrected),
**R7-F2** (CC-30 assumed that validation always detects a foreign reap and reuse: SI-3
made explicit, the new SI-5, CC-30 superseded, NT-SN-12 and NT-SN-6 rewritten, the
withdrawn-claims row W-17) and **R7-F3** (the CH vocabulary omitted `reap-unknown`),
plus the consistency corrections that those remediations directly need (§0.9). Every
section that R7 changed is listed in §0.9 and marked **Δ7** where it appears; the **Δ6**,
**Δ5**, **Δ4** and **Δ3** markers of R6 … R3 are kept so that a reviewer can compare the R7
candidate against R6 without splicing documents. The R6 proposal
([proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-r6-remediation-proposal.md),
[handback](phase-5-0-p5-r5-rp11-h1-oh-s3-r6-remediation-handback.md)) and every earlier
proposal are preserved **unchanged, unaccepted and historical**. Nothing here accepts R1
through R6.

The paragraphs that follow are carried from R6 and describe the R6 candidate. They are
accurate as history and are amended by R7 only where marked **Δ7**.

This document supersedes the OH-S3 R5 proposal as the cumulative forward
candidate and is self-contained. It is the R5 proposal with **two focused
remediations, R6-F1** (a `reap-error` can permit a root signal to a reused
process-group number: the new §7.5a.6d, the handle state `reap-unknown`, row 3g,
table SN-R, table SN-S with its new step S8, WB-5, WB-7, RB-5, PO-SN (c) and the new
(c′), the child-state set, the interruption points and the matrix, and the new cases
NT-RE-1 … 12) **and R6-F2** (table SN-S and IM-S disagreed on `not-sent(reaped)`: the
two branches of S1 and the new step S7, table SN-R rows 3 and 9, WB-5 (a), SN-4, the
outcome `u`, T0, T1, T5, T6 and T7, the matrix, and the new cases NT-NS-1 … 8), plus
the consistency corrections that those remediations directly need (§0.8). Every
section that R6 changed is listed in §0.8 and marked **Δ6** where it appears; the
**Δ5** markers of R5, the **Δ4** markers of R4 and the **Δ3** markers of R3 are kept so
that a reviewer can compare the R6 candidate against R5 without splicing documents and
see which text each round introduced; a section that carries several was amended again
by R6. The R5 proposal
([proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-r5-remediation-proposal.md),
[handback](phase-5-0-p5-r5-rp11-h1-oh-s3-r5-remediation-handback.md)), the R4 proposal
([proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-r4-remediation-proposal.md),
[handback](phase-5-0-p5-r5-rp11-h1-oh-s3-r4-remediation-handback.md)), the R3 proposal
([proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-r3-signal-operation-remediation-proposal.md),
[handback](phase-5-0-p5-r5-rp11-h1-oh-s3-r3-signal-operation-remediation-handback.md)),
the OH-S3 R2 proposal
([proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-r2-remediation-proposal.md),
[handback](phase-5-0-p5-r5-rp11-h1-oh-s3-r2-remediation-handback.md)) and R1
([proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-r1-design-remediation-proposal.md),
[handback](phase-5-0-p5-r5-rp11-h1-oh-s3-r1-design-remediation-handback.md)) are
preserved **unchanged, unaccepted and historical**. Nothing here accepts R1, the
OH-S3 R2 proposal, the R3 proposal, the R4 proposal or the R5 proposal.

Basis (all accepted, all inactive): the cumulative
[OH-S2 R2 citation record](phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md) and
its [acceptance](project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-acceptance.md);
the [one-host design amendment](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md)
through D3-R6 and its
[acceptance](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-acceptance.md);
the [H-0 completeness proposal (DR1)](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-proposal.md),
the [cumulative R3 H-0 completeness proposal](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-proposal.md)
and its [acceptance](project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r3-acceptance.md);
the [composed H-0 and U-9 acceptance](project-review-2026-10-06-p5-r5-rp11-h1-h0g-r1-acceptance-and-u9.md);
the [C11 launcher contract](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md)
and [D2 static launcher design](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md).

This document is a **proposal and an alternatives record only**: inactive,
unreviewed and unaccepted. It changes no accepted record, no source, test,
configuration, unit, rule or launcher byte. It authorizes no host access,
implementation, build, test, cleanup, activation, successor slice, commit or
push. Naming a successor, a work package or a decision in it authorizes nothing.

---

## 0. Outcome

### 0.1 In one page

**Δ7.** This section is carried from R6 and extended. The three bullets headed R7-F1, R7-F2 and R7-F3 are R7's; they stand before the paragraph on the safety kernel. The earlier bullets describe the R2 … R6 rounds as they stood and are amended only where marked **Δ7**.

Independent review returned R1 with two findings, and then returned the OH-S3 R2
proposal with one further **Important** finding, R3-F1. This record closes all
three, and it ends at the hard stop that the R1, R2 and R3 prompts all define for
the case in which a concrete Route 3 cannot be established from repository
evidence.

* **R2-F1 — R1's recommended RT3-A did not meet the authorized Route 3
  boundary.** Correct, and R1's text is not repaired in place. The accepted
  Route 3 means that the root procedures that touch the grant and activation
  mechanism **do not run through CPython or a dynamic loader** (§9.1). R1 instead
  re-scoped "Route 3" to "no environment-derived input", kept CPython and glibc in
  every root-helper path, left the file-based loader inputs to MF-1, MF-2 and
  MF-4, and asked Peter to confirm that new scope inside DEC-1. A static first
  image closes inherited environment and descriptors. It does not remove the
  interpreter, the dynamic loader or their file inputs from the path. RT3-A
  survives only as **`STATIC-SCRUB-WRAPPER` (SSW)**, a named **scope-change
  alternative that is not Route 3**, selectable only after an explicit baseline
  decision under implementation-plan §0.2 (§9.7). DEC-1 no longer carries a Route
  decision.
* **Literal Route 3 is not decision-ready.** The repository holds the accepted
  procedures that a Python-free root path would have to reimplement, but it holds
  no evidence for the loader-free interface by which a static root image would
  read unit state, create the transient units, query Polkit and create the
  authorization subject (five of the six functions the root helpers delegate to
  distribution binaries today), no proof method for a static image with
  that system-call inventory, and no settled boundary for the procedures that
  `sudo` starts. Defining those would invent facts (§9.3). §9.4 gives the exact
  bounded alternatives and §9.5 the exact work, in order, that would make literal
  Route 3 decision-ready. **That is the hard stop.**
* **R2-F2 — the claimed cleanup bounds contained unbounded local work.**
  Correct. The S grammar reserves a fixed 30-second margin. It bounds none of the
  filesystem inspection, hashing, process creation and reaping, journal writes
  and `fsync` that CL and IGR perform. R1's "CL < S by the S grammar" and "IGR acts
  within about ten seconds" are **withdrawn**, together with the accepted design's
  "CL-0 … CL-3, which are local operations bounded by S" (§7.7). The replacement
  is a discipline, not an arithmetic claim (§7):
  every wait the helpers perform on a child, a lock or a clock has a **monotonic
  deadline and a fail-closed consequence** (class E); every whole-procedure
  elapsed-time claim is made **only where PID 1 enforces it**, as a signal
  delivered at a stated offset, and no completion is promised (class M); a few
  loops are bounded by a count (class C); everything else is **expected to be
  quick and is not bounded** (class X). Each procedure's interruption at any
  point maps to a state and a next recovery owner (§7.9). Signal handlers are
  installed **before any state is created and only set a flag** (§7.8), so
  nothing depends on an interruptible Python `finally` block finishing within an
  unsupported time, and a second signal during IGR is idempotent. While doing
  this I found a probable defect in the accepted backstop literal: for a
  `Type=exec` service `TimeoutStartSec=` ends at `execve` (systemd's documented
  behaviour, **proposed for citation**, not yet cited), so **nothing would bound a
  backstop firing that has started**. The literal gains a PID-1-enforced
  `RuntimeMaxSec=` (§7.4, BS-RM).
* **R3-F1 — the blocking-operation inventory omitted signal *sending*. (R3)** Correct.
  The OH-S3 R2 proposal inventoried signal *delivery* and handler execution and the
  *reaping* of children, but not the helper's own act of *sending* a signal. It used
  `SIGTERM` and `SIGKILL` to a child's process group as the consequence of an
  expired wait and wrote HS-5 and related rows as if that operation always works.
  It also never said how the helper keeps the target's identity so that a PID or
  process-group reuse cannot send a signal to an unrelated process. This was the
  part of R2-F2 item 1 that the OH-S3 R2 proposal left incomplete. §7.5a now gives
  one function, **SN**, that performs every local send; its inventory (§7.3 rows
  3a … 3f); its class (**X** for the call, **C** for the attempts, never a wait and
  never given an elapsed-time bound); a **child handle** and the **pinning
  argument** (an unreaped child pins its PID and group number) with validation as a
  detector only; a result table for success, `ESRCH`, permission and validation
  failures and every other error, none of which authorizes a pass, converts
  *unconfirmed* into confirmation, or is hidden; the sequence after a failed or
  indeterminate send (scheduled reap waiting of at most g, **Δ4**, then **abandon**, record, and the
  next recovery owner); and 18 negative tests. **Sending a signal is not proof that
  the target exited, was reaped, or left an uninterruptible kernel call**, and no
  R2 timing claim is strengthened. The kernel, CPython and systemd facts the
  contract needs are cited by **no accepted record**, so they are **proposed,
  version-bound obligations** (PO-SN (a) … (f), §7.5a.8, §13.2) and AP-0 is INVALID
  RUN until they are accepted. The Route 3 hard stop is unchanged.
* **R4-F1 — the send sequence could wait past its own grace deadline. (R4)** Correct.
  R3's table SN-S read `t_g` before the first send (S0), but S3 then waited a full
  `slice_ms` after `SIGTERM` returned without looking at what was left of g, and S5's
  last sleep was not capped either. If the send, or the validation before it, had
  already used all of g, the helper waited again, while R3 kept W_show = c + g and
  W_series = P + c + g as wait budgets. §7.5a.6a now states **one absolute `t_g`** per
  child, read once before the first send or validation, and a **cap on every sleep** by
  the time remaining to it (WB-1, WB-2). **No timed wait begins at or after `t_g`**
  (WB-3). The at-most-once, identity-validated `SIGKILL` of S4 is not a wait and is not
  skipped; it may still be a class-X call at or after `t_g`, and it is recorded as late,
  never presented as completion within g (WB-4). The boundary is ordered by one
  non-blocking **reap attempt**, which is class X and never a wait: a child already
  reaped, a child that exits during a send, and a child still unreaped at `t_g` each
  have a defined result (WB-5). **The wait budget is stated separately from elapsed
  procedure time** (WB-6): the budget is the total of the scheduled sleeps, at most g;
  the elapsed time includes every send, validation and reap attempt and has no bound. No
  send, validation or other class-X operation acquires a time bound, and no sizing rule
  becomes a completion guarantee. R3's sentence "Everything from S0 to S6 sits inside g"
  is withdrawn (§7.7 W-14). No parameter changes.
* **R4-F2 — the interruption map assumed that a send succeeded. (R4)** Correct. R3's IM-S
  called the state after `SIGTERM` "signalled" and after `SIGKILL` "killed, or alive in
  an uninterruptible call", although table SN-R admits failed, indeterminate and unmade
  sends and a child can stay alive because delivery failed. Its rows used "as S0" and "as
  S3" where its own rows were T0 … T5, and it never set out the interactive `attest`
  case, which has no automatic recovery owner. §7.9 IM-S is rewritten around a **common
  child-state set CS-1 … CS-8** and a **point × send-outcome matrix**. "Sent" means only
  that the kernel send call returned 0. Only a recorded reap status proves that the direct
  child was reaped, and it never proves that the process group is empty. After **any**
  send the target may remain alive. The state after an interruption is **not a function of
  any send result** (IS-5), and ownership follows the **enclosing procedure** (holder, CP,
  stop-post, backstop service, interactive `attest`), with the boot recorded as a separate
  recovery event and never as evidence that a signal worked (§7.5a.7). R3's statement that
  an interrupted helper leaves its children "unsignalled by anyone" is withdrawn (§7.7
  W-14). Mutating-child effect stays `unknown`, the enclosing result stays fail-closed,
  and no retry and no process hunting is granted.
* **R5-F1 — IM-S omitted the kernel reap that completes inside an interrupted reap
  attempt. (R5)** Correct. R4 defined T3 and T5 as containing a reap attempt, defined T6
  only after the sequence has decided, and mapped the T3 and T5 cells to CS-2, CS-3 and
  CS-4, whose direct child is alive or exited and unreaped. But the helper can be ended
  after the kernel has consumed the direct child's exit status inside `waitpid` and
  before the helper has set the handle's state or written the `child` line (R4's E1
  admitted it and NT-IS-8 modelled it), and T6, which begins after the decision, cannot
  cover an interruption inside the attempt. NT-IS-1 therefore could not truthfully prove
  that every reachable cell has the exact state the matrix names. §7.5a.6c now defines
  the **boundary of one reap attempt** as five phases RA-0 … RA-4 (before the call;
  inside the call before the kernel reaps; **the kernel has reaped but the handle still
  says `running`**; the handle has been updated; the `child` line is durable), says that
  the kernel reaps the direct child only inside `reap_step()` and that no act is made
  between RA-2 and RA-3, and maps the phases to points: **T3 and T5 now mean "not yet
  reaped by the kernel", the new points T3k and T5k are RA-2 inside S3 and S5 (the final
  attempt included), and T6 begins at the handle-state update (RA-3) or at the abandon
  decision and never earlier.** **CS-5 is redefined to cover a direct child that the
  kernel has reaped, whether or not the helper recorded it in memory**, so T3k and T5k
  map to CS-5. The conservative observer rule is stated as IS-9: without a durable
  `child` line a later procedure learns no reap fact, records the gap `children-unknown`,
  and does not read a kernel reap that nothing recorded as evidence that the group is
  empty. E1, the matrix and its narrative, INV-18, INV-20, INV-23, rows 19 and 20 of
  §5.5, RO-7, the record text, review questions, Appendix A, B and D rows and every
  reference are corrected; NT-IS-1 and NT-IS-8 are rewritten; NT-IS-16 and NT-IS-17
  distinguish the five interruption positions. While making every cell exact I found two
  further cells that R4's own text contradicted (T0 and T1 with a handle already reaped,
  and the PK subject at T5) and corrected them (CC-18, CC-19). **Δ6: CC-18 is superseded by CC-23 and W-16.** **No parameter, deadline
  class, send rule or wait rule changes.**
* **R5-F2 — NT-WB-5 gave one impossible expectation to two slow-validation runs. (R5)**
  Correct. NT-WB-5 combined a run in which S1's validation costs 2,100 ms with a run in
  which S4's second validation costs 2,100 ms, and asserted for both that S3 and S5 skip
  every timed wait and that both `SIGTERM` and `SIGKILL` are late. That fits a slow S1,
  which consumes g before any send. It does not fit a slow S4 after a prompt S1 and a
  prompt `SIGTERM`: S3 has by then made its capped wait before `t_g`, and `SIGTERM`
  returned before `t_g` and is not late. NT-WB-5 is split into **NT-WB-5a (slow S1)** and
  **NT-WB-5b (slow S4)**, each with explicit costs and clock positions on one fake clock
  (§7.12), and the case table of §7.5a.6b gets one row for each. The shared assertions are
  kept in both: one `t_g`, no restarted grace, no timed wait at or after it, each send
  attempted at most once, scheduled waiting within g, and no elapsed-time bound for any
  class-X operation. **WB-1 … WB-7 do not change.**
* **R6-F1 — a `reap-error` could permit a root signal to a reused process-group number.
  (R6, Blocking)** Correct. R5 read a raised `Popen.poll()` as *unreaped* for that attempt
  (row 3g) and left table SN-S, S4 and SN-4 unchanged, so after a `reap-error` the
  sequence could continue to an identity validation and a root `SIGKILL`. R5 itself
  admitted that, if the exception arose after `waitpid` had consumed the status, the PID
  and the process-group number may have been released, and that SN-4's validation is a
  detector and not a reuse defence (SI-2). It put the question into PO-SN (c) as an AP-0
  gate, but a gate that only requires the obligation to be *accepted* does not say what
  the safe outcome is: a later citation could have established that a post-reap exception
  is possible and still been accepted. §7.5a.6d (RE-1 … RE-6) now makes the design **fail
  closed after any `reap-error`**. The handle goes to a new state, **`reap-unknown`**,
  which says only that the helper does not know whether the direct child is still
  unreaped or was reaped in the kernel with no handle update, and is labelled neither
  *reaped*, *unreaped* nor *abandoned*. **No later signal of any kind is sent to that
  child, S4's `SIGKILL` included, and no retry, alternate primitive, further poll or
  process search is made.** The handle and the `Popen` object are kept for the helper's
  life; the `reap-error`, the send suppression and, for a mutating child, `effect:
  "unknown"` are recorded; the enclosing operation returns its existing fail-closed
  result; and the suppression starts no new wait and no new grace (one absolute `t_g`
  and the at-most-once send rule are unchanged). **PO-SN (c) is split:** (c) keeps what
  the design rests on, and the post-poll exception question becomes **PO-SN (c′)**,
  evidence about CPython only. **Neither answer changes any decision:** if CPython can
  raise after the kernel's reap, nothing is sent; if it cannot, nothing is sent either.
  AP-0 does not read (c′). Row 3g, table SN-R (new row 12), table SN-S (new step S8),
  WB-5, WB-7, SI-3, SI-4, SN-4, SN-7, SN-8, RB-5, the phases of a reap attempt (new
  RA-E), the interruption points (new T3x and T5x), the child-state set (new CS-9 and
  CS-10), the matrix, the records, invariants, residuals, review questions, security
  rows and Appendices follow. Twelve paper-only cases, NT-RE-1 … 12, cover a
  `reap-error` before and after a kernel reap at S3, at S5 and at the final attempt.
* **R6-F2 — table SN-S and IM-S disagreed on `not-sent(reaped)`. (R6, Important)**
  Correct. R5's S1 sent every `not-sent` result to S5, while table SN-R rows 3 and 9 and
  WB-5 (a) said that an already-reaped child ends the sequence at once, the outcome `u` of
  IM-S included `not-sent(reaped)`, and the T5/`u` cell was a dash that R5 called
  unreachable although S1 reached S5 with that outcome. S1 is now split into two
  branches. **`not-sent(reaped)`, `not-sent(abandoned)` and `not-sent(reap-unknown)` make
  no call, begin no wait and end the sequence at the new step S7**, the settled-state
  record path. **`not-sent(identity-mismatch)` and `not-sent(identity-unverifiable)` make
  no send and go to the capped S5 reap and final-attempt path**, as in R5. The same
  distinction holds wherever a send is validated, S4's PK-only path included, and **no
  `not-sent` result is ever followed by a send**. When an enclosing wait's own poll
  reaped the handle before SN was entered, **the settled-state decision was made at that
  poll's phase RA-3, before SN; the durable record is made by S7; the interval between
  them is T6 and the durable line is T7. T0 and T1 exist only for a handle that is still
  `running`**, so no interruption is placed at T0 or T1 and at T7 at once. T0 `u` and T1
  `u` return to CS-1 only, and T5 `u` is a dash that is now unreachable (CC-23). The
  outcome definition, T0 … T7, every affected cell and dash, NT-SN-5 … 7, NT-IS-1, -5,
  -6 and -16 and the narrative follow, and NT-NS-1 … 8 step an interruption before,
  during and after S1's branch for each `not-sent` subtype.
* **R7-F1 — the pre-S0 `reap-error` path had no defined grace-deadline record. (R7,
  Important)** Correct. R6 sent a `reap-error` raised in a poll of the **enclosing E wait**
  straight to S8 and S7, which is right: it happens before a deadline or the flag triggers
  SN, so **S0 has not run and no `t_g` exists**. But the `children` record required
  `grace_deadline_ms` for every child, INV-22 said each child has one grace deadline, and
  NT-RE-11 asserted one `t_g` read across random attempt positions, so NT-RE-7 could not
  be implemented together with the schema, the invariant and the test. The same gap held
  for every child whose S0 never ran (one that exits within c, one that fails to spawn).
  §7.5a.6e (GD-1 … GD-5) now states that **`t_g` exists exactly when S0 ran**: the
  record key `grace_deadline_ms` is always present and is an integer **iff** the new
  boolean `s0_ran` is true and **`null`** otherwise, so the distinction is a one-line
  schema check; a pre-S0 `reap-error` reads `t_g` **zero** times, enters no S0, reads no
  clock for the record, starts no grace period and records `outcome: "reap-error"`,
  `sends: []`, `waits_skipped: false` and `grace_deadline_ms: null`; and once S0 has run
  the one absolute `t_g` is still read once and never moved, extended or restarted
  (WB-1, unchanged). S0 is entered only for a `running` handle: a handle that is already
  settled when SN is called ends at S1-a with no clock read (CC-31), which stops a later
  SN call from creating a `t_g` after the record is written. SN-6, WB-1, RE-4, §7.5a.9,
  §8.5, INV-22, NT-SN-9, NT-RE-7, NT-RE-11, NT-RE-12, NT-WB-11 (i) and the Appendix A and B
  rows are corrected; **NT-GD-1 … 4** are focused paper-only cases, and NT-GD-1 follows
  the enclosing poll that raises through S8 and S7 field by field. **No parameter, class,
  send rule or wait rule changes**, and no grace period is added.
* **R7-F2 — CC-30 assumed that validation always detects a foreign reap and reuse. (R7,
  Important)** Correct. R6's NT-SN-12 injected a foreign reaper, left the handle's state
  unchanged, and claimed that validation then necessarily yields `identity-mismatch` or
  `identity-unverifiable`, so no stale number is signalled. That does not follow: a
  released PID and process-group number can be reused by a new process whose PID, PGID and
  SID have the same structural relationship, and the `start_ticks` check (SN-4 (iv)) is
  optional under PO-SN (d). **SN-4 is a detector of contradiction and of a corrupted
  handle. It is not the reuse defence.** The reuse defence is SI-3's **sole-reaper
  invariant** together with PO-SN (b), (c) and (f) (SI-2). R7 withdraws CC-30's universal
  claim (W-17), keeps the sole-reaper contract explicit and load-bearing (SI-3: no thread,
  signal disposition, destructor, foreign `wait*` call or other path reaps outside
  `reap_step()`, with its version-bound obligations and the AP-0 refusal unchanged), and
  adds **SI-5**: an injected foreign reap is a **deliberate violation of a design
  precondition, not a supported runtime state, and once the invariant is violated this
  design makes no reuse-safety claim from SN-4 alone**. NT-SN-12 now proves the structural
  sole-reaper properties and keeps one detector exercise, labelled non-universal and run
  with a deliberately mismatching fake identity; NT-SN-6 (b) carries the same label. **No
  `start_ticks` requirement, no pidfd and no other identity mechanism is added.**
* **R7-F3 — the child-handle vocabulary omitted `reap-unknown`. (R7, Optional)** Correct.
  The normative definition (§7.5a.3) has four states, but the vocabulary row **child handle
  (CH)** of §3 listed three. It now lists all four. Every other current definition of the
  handle state set was checked (§0.9) and lists four.
* **The safety kernel is unchanged.** G1 … G5 never cited the lock, the hold loop,
  `ExecStopPost=`, the backstop, any polling bound or any elapsed time (§2), so
  neither finding touches them. PO-11 (d′) is retained exactly: **no Polkit
  reload-time bound is claimed, and every operational timeout fails closed**
  (§7.10).
* **Two design improvements follow from F2 and are offered, not imposed.** The
  grant-removal routine GRR is one tmpfs-only, lockless, no-spawn routine used by
  IGR, by CL's first act and by the backstop, and it precedes every `ext4` write
  (§5.7, GR-2). A root-only identity object `grant.id` inside K lets those
  rungs act without reading an `ubuntu`-owned `ext4` journal (§4.5, GI-1; DEC-3).
* **MF-1 … MF-8, PO-12′, PO-19, PO-17, OH-S4/OH-S4p, the rebuild chain and the
  successor order** are re-evaluated under the corrected boundary, per
  alternative (§§9.8 … 9.13, 10, 11). Root-owned dynamic inputs do **not** cease
  to be inputs because the threat model excludes an unprivileged writer: under
  every alternative that keeps CPython or the loader in the path they remain
  inputs that must be observed and bound (§9.9).
* **Peter's choices (§12) are split.** Six decisions on the activation design may
  be made only after a clean independent review. **Any change of the accepted
  Route 3 boundary is a separate matter under §0.2 change control and is not a
  decision this proposal's acceptance can make** (§12.2).

### 0.2 Returned findings, repair and location

| # | Returned item | Repair in this proposal | Section |
|---|---|---|---|
| R2-F1 | RT3-A does not satisfy the authorized Route 3 boundary; DEC-1 used to change scope | R1 preserved; RT3-A renamed SSW and described as a scope-change alternative; accepted Route 3 restored; literal Route 3 evidence assessed; hard stop; exact alternatives and work; no scope change inside DEC-1 | §9.1 … §9.7, §12.2 |
| R2-F1 (7) | re-evaluate Role A–H, PO-12′, PO-19, MF-1 … MF-8, OH-S4/OH-S4p, rebuild chain, PO-17, surface comparison, successor order | per-alternative tables | §9.6, §9.8 … §9.13, §10, §11 |
| R2-F1 (8) | root-owned dynamic inputs are still inputs | stated and applied | §9.9 |
| R2-F2 (1)–(3) | inventory every blocking operation; distinguish enforced from expected; no inference from a fixed margin | classes E, M, C, X; inventory; withdrawn claims | §7.2, §7.3, §7.7 |
| R2-F2 (4) | enforce a deadline with a fail-closed consequence, or withdraw the claim and state the termination and recovery path | both, per component | §7.3, §7.4, §7.6 |
| R2-F2 (5) | map every interruption point of CL to a state and a next owner | interruption maps for the holder, CP, IGR, CL and the backstop | §7.9 |
| R2-F2 (6), (7) | handler installation relative to AM-2; no reliance on an interruptible `finally`; a signal during IGR; re-entry | signal discipline SG-1 … SG-8; IGR latch; flag-only handlers | §7.8, §5.7 |
| R2-F2 (8) | correct every affected formula, table, invariant, test, Appendix A amendment, Appendix B obligation and recommended parameter | all corrected; sizing rules N1 … N4 are necessary conditions only | §7.6, §8, Appendices A, B, §12 |
| R2-F2 (9) | retain PO-11 (d′) | retained verbatim in substance | §7.10 |
| **R3-F1** (1) | preserve the OH-S3 R2 proposal unchanged; self-contained cumulative R3 | the OH-S3 R2 proposal is a copy source only; R3 is a complete document with every changed section marked **Δ3** | header; §0.5 |
| **R3-F1** (2), (3) | inventory every signal-sending operation (initial group-directed termination, escalation to `SIGKILL`, cleanup and recovery sends); distinguish the local call from PID 1's class-M delivery and give it the correct class | table SN-I; rows 3a … 3f; the class **X** (call) and **C** (attempts) statement; the local-versus-PID-1 table | §7.2, §7.3, §7.4, §7.5a.1 … 7.5a.2 |
| **R3-F1** (4) | results for success, `ESRCH`, permission and validation failure, every other error; none authorizes, confirms or hides | table SN-R; SN-7 | §7.5a.5 |
| **R3-F1** (5) | validate and retain the child's process-group identity against PID or group reuse; define the missing proof obligation rather than invent a kernel guarantee | child handle CH; SI-1 … SI-4; SN-4; PO-SN (b), (c), (d) | §7.5a.3, §7.5a.8 |
| **R3-F1** (6) | what the helper does after a failed or indeterminate send: reap wait, abandonment, record, next owner | sequence SN-S; SN-6, SN-8; table SN-RO; SN-10 | §7.5a.6, §7.5a.7 |
| **R3-F1** (7) | propagate through class E, HS-5, PK/2, SG-4, the terminal-cause and interruption maps, records, invariants, residuals, Appendices A and B | each marked **Δ3** | §7.2, §7.5, §7.8, §5.5, §7.9, §8.5, §8.6, §13, Appendices A, B |
| **R3-F1** (8) | negative tests | NT-SN-1 … 18; five existing tests amended | §7.12 |
| **R3-F1** (9) | the remediation map shows how R3-F1 and the previously incomplete R2-F2 item 1 are closed | Appendix D | Appendix D |
| **R4-F1** (1) **Δ4** | one absolute `t_g`, set before the first send; every S3 and S5 wait capped by the remaining interval; no new grace period after a send, validation, poll, error or signal receipt | WB-1, WB-2, WB-7; the rewritten table SN-S | §7.5a.6, §7.5a.6a |
| **R4-F1** (2) **Δ4** | skip every later timed wait once a send or validation returns at or after `t_g`; keep the at-most-once identity-validated escalation of S4, not presented as completion within g | WB-3, WB-4 | §7.5a.6a |
| **R4-F1** (3) **Δ4** | boundary ordering for a child already reaped, one that exits during a send and one still unreaped at the deadline; a non-blocking reap attempt is class X | WB-5; the reap attempt | §7.5a.6a |
| **R4-F1** (4) **Δ4** | the wait budget stated separately from elapsed procedure time; no class-X operation acquires a bound; no sizing rule becomes a guarantee | WB-6 | §7.5a.6a, §7.6 |
| **R4-F1** (5) **Δ4** | every dependent sentence and test: CC-1, CC-2, SN-R, SN-S, SN-6, HS-5, PK/2, SG-4, the parameter notes, invariants, amendment tables | each marked **Δ4** | §0.6, §7.2, §7.3, §7.5, §7.5a, §7.6, §7.7, §7.8, §7.12, §8.6, Appendices A, B |
| **R4-F1** (6) **Δ4** | fake-clock regression cases: a send under, at and over g; less than one slice left; slow validation; expired deadline before S3 and S5; successful and failed sends; a child reaped at the boundary | NT-WB-1 … 12 (paper only) | §7.12 |
| **R4-F2** (1) **Δ4** | rewrite IM-S for successful, failed, indeterminate and unmade sends; "sent" means only the kernel result; only a recorded reap status proves reaping; no group emptiness from reaping the direct child | IS-1 … IS-8; the common state set CS-1 … CS-8 | §7.9 |
| **R4-F2** (2) **Δ4** | the cross-product of interruption point and send outcome, explicit and compact, including validation failure, `ESRCH`, other errors, partial escalation, death during a send, reaping and abandonment | the point × outcome matrix (T0 … T7 × six outcomes) | §7.9 |
| **R4-F2** (3) **Δ4** | correct every row reference; separate sends already attempted from the absence of further sends by the ended helper; remove "unsignalled by anyone" | the CS table; W-14 | §7.9, §7.7 |
| **R4-F2** (4) **Δ4** | recovery ownership by enclosing procedure (holder, CP, stop-post, backstop service, interactive `attest`); SN-RO's cgroup obligations; `attest` has no automatic owner; the boot is a separate event | table SN-RO (amended) | §7.5a.7, §7.9 |
| **R4-F2** (5) **Δ4** | propagate to terminal-cause rows 19/20, RO-7, records and gaps, invariants, review focus, Appendices A and B; mutating-child effect `unknown`; fail-closed result; no retry or process hunting | rows 19, 20; RO-7; §7.5a.9; INV-20 … 23; Q16, Q17; A-I-16, A-I-17; B-08, B-13 | §5.5, §5.6, §7.5a.9, §8.6, §14, Appendices A, B |
| **R4-F2** (6) **Δ4** | stepped regression cases for each IM-S point after success, `ESRCH`, another error, identity rejection and an unmade send, for a child alive, exited but unreaped, reaped or abandoned; the interactive `attest` case; lost child records | NT-IS-1 … 15 (paper only) | §7.12 |
| **R4-F1, R4-F2** (map) **Δ4** | the remediation map | Appendix D | Appendix D |
| **R5-F1** (1) **Δ5** | define the exact interruption boundary of a reap attempt, including the kernel reap before the handle state or the `child` line records it | the phases RA-0 … RA-4 and rules RB-1 … RB-5 | §7.5a.6c; WB-5 (pointer) |
| **R5-F1** (2) **Δ5** | make T3, T5 and T6 mutually consistent; no interruption inside an attempt is T6 | T3 and T5 mean "not reaped by the kernel"; T3k, T5k added; T6 begins at the handle-state update (RA-3) or the abandon decision | §7.9 point table; RB-4 |
| **R5-F1** (3) **Δ5** | extend the child-state set and matrix so every reachable interruption has a state that permits the true direct-child condition; no inference from a send result | CS-5 redefined; matrix rows T3k and T5k; T0, T1 and T5 cells corrected | §7.9 state set and matrix |
| **R5-F1** (4) **Δ5** | keep the conservative observer rule: no durable `child` line, no reap fact, only the applicable gap or `children-unknown`; a kernel reap not durably recorded is not evidence that the group is empty | IS-9; the record paragraph; the owner table | §7.9; §7.5a.9; SN-7 |
| **R5-F1** (5) **Δ5** | correct E1, the matrix narrative, INV-18, INV-20, INV-23, terminal-state and record text, review questions, Appendix A and B rows and every affected reference | E1 rewritten; §5.5 rows 19, 20; §5.6 RO-7; SI-3; SN-7; §7.3 row 3g; PO-SN (c); §8.5; §8.6; §13; §14; Appendices A, B, C.2, D | §0.7 lists every one |
| **R5-F1** (6) **Δ5** | correct NT-IS-1 and NT-IS-8; add paper-only cases for before the call, inside the call before a reap, after the kernel reap before the handle update, after the handle update before the durable line, and after the durable line; every dash claimed unreachable is unreachable | NT-IS-1, -6, -8, -11, -14 amended; NT-IS-16 and NT-IS-17 added | §7.12 |
| **R5-F2** (1) **Δ5** | split NT-WB-5 into explicit slow-S1 and slow-S4 cases | NT-WB-5a and NT-WB-5b | §7.12 |
| **R5-F2** (2) **Δ5** | slow S1: S3 and S5 waits and `late` fields from the actual clock | NT-WB-5a | §7.12; §7.5a.6b |
| **R5-F2** (3) **Δ5** | slow S4: explicit costs for S1, `SIGTERM` and S3; S3's capped wait allowed when it begins before `t_g`; `SIGTERM` late only if its own return is at or after `t_g`; S5 makes no timed wait; `SIGKILL` late when its return is at or after `t_g` | NT-WB-5b | §7.12; §7.5a.6b |
| **R5-F2** (4) **Δ5** | keep the shared assertions | both cases carry them | §7.12 |
| **R5-F2** (5) **Δ5** | propagate the split to the case table, the remediation map, the handback and every cross-reference | the case table rows; Appendix D; §0.7 | §7.5a.6b; Appendix D |
| **R5-F1, R5-F2** (map) **Δ5** | the remediation map | Appendix D | Appendix D |
| **R6-F1** (1) **Δ6** | fail closed after **any** `reap-error`: no later signal to that child, S4's `SIGKILL` included; no retry, alternate primitive or process search | RE-1; table SN-S (S3, S5 and the new S8); WB-7; table SN-R row 12; SI-4 | §7.5a.6d; §7.5a.5; §7.5a.6; §7.5a.6a |
| **R6-F1** (2) **Δ6** | a child state that permits either truth (unreaped, or reaped in the kernel with no handle update) and is not labelled `reaped`, `unreaped` or `abandoned` as a fact; the sequence transition | the handle state `reap-unknown`; RE-2; RA-E; CS-9, CS-10; T3x, T5x; IS-10 | §7.5a.3; §7.5a.6c; §7.5a.6d; §7.9 |
| **R6-F1** (3) **Δ6** | keep the handle and `Popen` for the helper's life; record `reap-error`, the send suppression and `effect: "unknown"`; the enclosing fail-closed result; the owner rules and observer rules of R5 unchanged; nothing acts on or searches for the child | RE-3, RE-5; §7.5a.9; table SN-RO (unchanged); IS-6, IS-7, IS-9 | §7.5a.6d; §7.5a.9; §7.9 |
| **R6-F1** (4) **Δ6** | correct row 3g, table SN-S, SN-4, SN-7, SN-8, RB-5, the RA and point mapping, the child-state set, IM-S cells and dashes, records, invariants, residuals, review questions, security rows, Appendices A and B and every reference; keep the at-most-once send rule and the one absolute `t_g`; no new wait or grace after the suppression | each marked **Δ6**; §0.8 lists them | §0.8; §7.3; §7.5a.3 … §7.5a.9; §7.9; §8.5 … §8.7; §13; §14; Appendices |
| **R6-F1** (5) **Δ6** | rephrase PO-SN (c) so that its citation stays useful about CPython but is no safety precondition for deciding whether to send after `reap-error`; either answer leaves the design safe and AP-0 cannot pass an unsafe branch | PO-SN (c) narrowed; PO-SN (c′) evidence-only; RE-6; NT-RE-12; NT-SN-18 | §7.5a.8; §7.5a.6d |
| **R6-F1** (6) **Δ6** | paper-only cases: `reap-error` before and after a kernel reap, at S3, S5 and the final attempt; zero later sends, no PID or group reuse exposure, indeterminate child truth, fail-closed result, correct record or gap, no later search or retry | NT-RE-1 … 12 | §7.12 |
| **R6-F2** (1) **Δ6** | split S1: `not-sent(reaped)` or `not-sent(abandoned)` makes no call, begins no wait and ends the sequence through the settled-state record path; `not-sent(identity-mismatch)` or `not-sent(identity-unverifiable)` makes no send and goes to the capped S5 path | table SN-S (S1-a, S1-b, S7) | §7.5a.6 |
| **R6-F2** (2) **Δ6** | the same distinction wherever a send is validated, including the PK-only S4 path, with no send after any `not-sent` | SN-4; table SN-S S4; table SN-R rows 3, 7 … 9 | §7.5a.4; §7.5a.5; §7.5a.6 |
| **R6-F2** (3) **Δ6** | make table SN-R, table SN-S, WB-5, the outcome definition, T0/T1/T5/T6/T7, every affected cell and dash, NT-SN-5/6/7, NT-IS-1/5/6/16 and the narrative mutually consistent; state exactly when the settled-state decision and the durable record occur for a handle already reaped by an enclosing poll; no interruption at T0/T1 and T7 at once | WB-5 (a); outcome `u`; the point table and the paragraph *Before T0*; the matrix; CC-23; RB-2 | §7.5a.6a; §7.9; §0.8 |
| **R6-F2** (4) **Δ6** | a focused paper-only case stepping an interruption before, during and after the S1 branch for each `not-sent` subtype; every dash claimed unreachable is unreachable | NT-NS-1 … 8; the corrected dash analysis | §7.12; §7.9 |
| **R6-F1, R6-F2** (map) **Δ6** | the remediation map | Appendix D | Appendix D |
| **R7-F1** (1) **Δ7** | one explicit representation for a child whose enclosing-wait poll raises before S0: `grace_deadline_ms` null; no invented deadline, no S0, no clock read for the record, no grace period | GD-1, GD-2, GD-3; `s0_ran`; `outcome: "reap-error"` | §7.5a.6e; §7.5a.9; §8.5 |
| **R7-F1** (2) **Δ7** | `t_g` exists exactly when S0 ran; once it exists it is read once and never moved, extended or restarted; a pre-S0 `reap-error` reads it zero times | GD-1, GD-3; WB-1 and SN-6 (amended); S0's entry condition (CC-31) | §7.5a.4; §7.5a.6; §7.5a.6a; §7.5a.6e |
| **R7-F1** (3) **Δ7** | correct §7.5a.9, §8.5, INV-22, NT-SN-9, NT-RE-7, NT-RE-11, NT-RE-12 and every dependent record, schema, Appendix A/B and handback statement; make the distinction machine-checkable | GD-2 (the schema constraint); INV-22, INV-26; NT-SN-9, NT-RE-7, -11, -12, NT-WB-11 amended; A-I-17, B-08 | §7.5a.9; §8.5; §8.6; §7.12; Appendices A, B |
| **R7-F1** (4) **Δ7** | a focused paper-only case: enclosing poll raises before S0; no `t_g` read; `grace_deadline_ms` null; zero send, wait, further poll or search; S8 and S7 record `reap-unknown`; the enclosing operation fails closed | NT-GD-1 (with NT-RE-7); NT-GD-2 … 4 | §7.12 |
| **R7-F2** (1) **Δ7** | withdraw CC-30's universal claim that validation detects every foreign reap and that the injected state reaches S1-b | CC-30 superseded; W-17; CC-33 | §0.8; §7.7 |
| **R7-F2** (2) **Δ7** | keep the sole-reaper contract explicit and load-bearing; version-bound obligations and the AP-0 refusal unchanged | SI-3 (amended); SG-3 (unchanged); PO-SN (b), (c), (f) (unchanged); AP-0 (unchanged) | §7.5a.3; §7.5a.8 |
| **R7-F2** (3) **Δ7** | an injected foreign reap is a deliberate violation of a design precondition, not a supported state; NT-SN-12 proves the structural properties; any detector exercise is labelled non-universal with a deliberately mismatching fake identity | SI-5; NT-SN-12, NT-SN-6 (rewritten) | §7.5a.3; §7.12 |
| **R7-F2** (4) **Δ7** | the honest consequence: after the invariant is violated the design makes no reuse-safety claim from SN-4 alone; no new identity mechanism | SI-5; SN-4 (a clause); SI-2 (a clause) | §7.5a.3; §7.5a.4 |
| **R7-F2** (5) **Δ7** | correct CC-30, NT-SN-12, the reuse narrative, invariants, review questions, security rows and the remediation map | CC-30; §0.1; INV-19, INV-27; Q15, Q21, Q23; SR-12, SR-15; Appendix D | §0.8; §8.6; §14; Appendix D |
| **R7-F3** (1), (2) **Δ7** | add `reap-unknown` to the CH vocabulary row; check every current definition of the handle state set | §3 CH row; the check recorded in §0.9 | §3; §0.9 |
| **R7-F1, R7-F2, R7-F3** (map) **Δ7** | the remediation map | Appendix D | Appendix D |

The carried items of R1 (PO-20 (f), PO-21 (c), PO-21 (s), PO-11 (d), PO-12′,
PO-19, PO-17, MF-1 … MF-8) keep their accepted R2 verdicts and are located in
Appendix C.

### 0.3 What this proposal does not do

It does not claim any citation, fact or acceptance. Every new host-behaviour
statement is a **proposed proof obligation** (§1.3), version-bound and paired
with the fact that fixes its version. It does not implement, rebuild, install,
test or observe anything. It does not edit the operational draft, the accepted
design, the C11 or D2 records, the R2 record, source code, tests, service files,
the decision register or the change log. It does not select a third-party
artifact and performed no network research. It does not change the accepted
Route 3 boundary, and it makes no scope decision. **R3 researched no kernel, libc,
CPython or systemd behaviour.** Every statement about how `kill`, `killpg`,
process-group numbers, `subprocess`, `setsid`, `SIGCHLD` or cgroup cleanup
behave is a **proposed, version-bound obligation** (§7.5a.8), not a fact.
**R4 researched none either (Δ4).** It states what happens to a child after its parent
helper ends only as *unknown to the design*: no step relies on reparenting, on the
reaping of an orphaned zombie or on any signal that the end of an interactive session
may cause. The one behavioural statement the interruption map would like to make, that
the end of a helper leaves its children running until something acts on them, is
recorded as an **optional proposed obligation, PO-SN (g)** (§7.5a.8), which no safety
claim rests on.
**R6 researched none either (Δ6).** The one behavioural question R6-F1 touches, whether
`Popen.poll()` can raise after `waitpid` has consumed a child's status, is stated as the
evidence-only obligation **PO-SN (c′)** (§7.5a.8). The design does not wait for its answer
and is safe for both: after any `reap-error` it sends nothing (§7.5a.6d). No kernel,
language or systemd behaviour was researched or invented.
**R7 researched none either (Δ7).** R7-F1 is a question about the design's own record and
asks for no kernel or language fact. R7-F2 **narrows** a claim: it states what the design
does *not* know once its sole-reaper precondition is violated, and adds no behaviour. The
facts the sole-reaper contract needs remain the proposed, version-bound obligations
PO-SN (b), (c) and (f) at the existing citation gate (§7.5a.8); none is cited, none is
strengthened, and none is weakened. No kernel, language or systemd behaviour was
researched or invented.

### 0.4 Terminal-state check

The R1 prompt and the R2 prompt both define one conditional hard stop:
*if repository evidence is insufficient to choose a safe concrete Route 3, return
a decision-ready set of exact alternatives and a `HARD STOP` rather than inventing
facts.* The R2 and R3 prompts name it `HARD STOP: concrete Route 3 not established`. The
prompt identity matched, so the identity hard stop did not arise. The conditional
hard stop **does** arise, for the reasons of §9.3: the repository evidence that
would define a Python-free, loader-free root path is absent in four named places
(interface contract, static proof method, boundary for sudo-started procedures,
and size). The repaired activation design (§§2 … 8) is complete and
decision-ready on its own terms, **except** that its helper-start contract RH
(§9.2) is discharged by whichever Route 3 outcome is eventually chosen. Nothing
here is labelled completion on the strength of a scope-change alternative.

**R3.** Closing R3-F1 needs kernel, CPython and systemd facts that no named
repository evidence establishes (§7.5a.8). The R3 prompt provides that such a fact is
to be added to the relevant future citation gate and the Route 3 hard stop retained.
That is what R3 does: PO-SN (a) … (f) join the OH-S2b citation step (§11, slice 2a),
and no new hard stop arises.

**R4 (Δ4).** Closing R4-F1 and R4-F2 needs no scope or design decision beyond this
assignment and no behaviour that named repository evidence fails to establish. The only
new behavioural statement is the optional PO-SN (g), added to the same citation step. The
prompt's second hard stop, `HARD STOP: OH-S3 R4 remediation requires maintainer direction`,
**did not arise**, and the identity hard stop did not arise (the pin matched). The Route 3
hard stop is unchanged.

**R5 (Δ5).** Closing R5-F1 and R5-F2 needs no scope or design decision beyond this
assignment and no behaviour that named repository evidence fails to establish. The one
behavioural question R5 touches, whether `Popen.poll()` can raise after the kernel has
consumed the child's status, is added to the proposed, version-bound obligation PO-SN
(c) at the same citation step (§7.5a.8) and is put to the reviewer as Q18; no kernel,
language or systemd behaviour was researched or invented. The prompt's second hard
stop, `HARD STOP: OH-S3 R5 remediation requires maintainer direction`, **did not
arise**, and the identity hard stop did not arise (the pin matched). The Route 3 hard
stop is unchanged.

**R6 (Δ6).** Closing R6-F1 and R6-F2 needs no scope or design decision beyond this
assignment. The one behavioural question R6-F1 touches, whether `Popen.poll()` can raise
after the kernel has consumed a child's status, is **no longer a safety precondition**: the
design is safe for both answers (RE-1 … RE-6), the question stays as the evidence-only
obligation PO-SN (c′) at the same citation step (§7.5a.8) and as review question Q18 in its
rewritten form, and no kernel, language or systemd behaviour was researched or invented. The
prompt's second hard stop, `HARD STOP: OH-S3 R6 remediation requires maintainer direction`,
**did not arise**, and the identity hard stop did not arise (the pin matched). The Route 3
hard stop is unchanged.

**R7 (Δ7).** Closing R7-F1, R7-F2 and R7-F3 needs no scope or design decision beyond this
assignment. The obligations PO-SN (b), (c) and (f) are unchanged; the new SI-5 states a
consequence of violating the precondition that they support and adds no obligation; no new
identity mechanism is added. The prompt's second hard stop, `HARD STOP: OH-S3 R7
remediation requires maintainer direction`, **did not arise**, and the identity hard stop
did not arise (the pin matched). The Route 3 hard stop is unchanged.

### 0.5 R3 change summary, consistency corrections, and what R3 leaves unchanged **Δ3**

**The finding.** R3-F1 (Important, documentation and design completeness) is stated
in §0.1. It is not a new host fact and gave no authority for research.

**Sections changed by R3** (each is marked **Δ3** where it appears):

| Section | Change |
|---|---|
| title, header, §0.1 … §0.5 | R3 identity and pin; the R3-F1 bullet; the map rows; the scope and terminal-state sentences; this section |
| §1.1, §1.3 | the R3 reading; the naming note; the identifier list and tag row |
| §3 | vocabulary: SN, child handle, unreaped; the definition of *abandon* |
| §4.5 LD-9 | extended from lock holders to children: only SN, only an own unreaped child |
| §5.5 rows 19, 20; §5.6 RO-7; §5.7 | two terminal-cause rows; the new residual; GRR and IGR send no signal |
| §7.2 | class E wording; what E does not bound; the local-versus-PID-1 distinction |
| §7.3 | rows 2, 3, 4, 13 amended; rows 3a … 3f added |
| §7.4 | one paragraph: local sends and PID 1's sends |
| §7.5 | HS-3, HS-5; the PK/2 subject and outcome |
| **§7.5a (new)** | **the signal-sending operation SN, the child handle, SI-1 … SI-4, SN-1 … SN-10, tables SN-I, SN-R, SN-S, SN-RO, PO-SN (a) … (f)** |
| §7.6 | one note: no parameter added, N1 … N4 unchanged |
| §7.7 | W-12, W-13 |
| §7.8 | SG-3, SG-4 amended; SG-9 added |
| §7.9 | IM-S added; the L4 row |
| §7.11 | one bullet |
| §7.12 | NT-DL-1, -2, -3, NT-SG-3, NT-HS-3, NT-LD-9, NT-RL-8 amended; NT-SN-1 … 18 added |
| §8.1 (AP-0 row), §8.5, §8.6, §8.7 | AP-0 also requires PO-SN; the `children` record key and condition names; INV-12, -16, -17 amended; INV-19 … 21; test group (36) |
| §9.3 (E-3), §9.5 (WP-2, WP-4) | one clause each: the signal-sending inventory joins the Route 3 work |
| §11 (slice 2a, readiness item 2) | PO-SN (a) … (f) join the OH-S2b citation step and the readiness list; **the order and the gates are unchanged** |
| §13.1, §13.2 | RO-7; SG-9; PO-SN (a) … (f) |
| §14.1 Q5, Q15; §14.2 SR-12 | review questions and the claim needing security re-review |
| Appendix A (A-I-15, A-I-16), B (B-08, B-13), C.2, D | the amendment, obligation and map rows |
| closing statement | one clause |

**Consistency corrections called out for review.** Each is directly necessary to
close R3-F1. **None changes** an OH-S3 R2 deadline class, a parameter or a sizing rule
(N1 … N4), PO-11 (d′), the Route 3 boundary, the SSW classification, an MF
disposition or the hard stop.

| ID | Correction | Why it is necessary | Effect on a timing claim |
|---|---|---|---|
| **CC-1** | §7.3 row 2 and HS-5 said an expired child is "killed … by a signal to its process group". They now say it is acted on **only through SN**: `SIGTERM`, then, if the child is still unreaped after the capped wait of S3, `SIGKILL` once (S4), with the scheduled waiting for reaping totalling at most g, measured from one `t_g` read before the first send **Δ4** | the prompt requires the initial termination signal and the escalation to be inventoried separately, and the OH-S3 R2 wording assumed a send that cannot fail | none. **Δ4:** R3 added that "both signals sit **inside** g". That is withdrawn (CC-8, W-14): the *scheduled waits* sit inside g; a send may not. W_show = c + g and W_series = P + c + g are unchanged, as budgets of the helper's *scheduled waiting* only (WB-6) |
| **CC-2** | an E wait that observes the flag (SG-4) now runs the SN sequence including the scheduled reap waiting of at most g before it returns `interrupted`; the OH-S3 R2 text said "kills and abandons" | the abandon decision cannot precede the reap wait without making a send's outcome unobservable | the flag is still *observed* at the next wake-up, at most `slice_ms` of scheduled sleep later; only the **return** follows the SN sequence. **Δ4:** R3 said "by at most g". The *scheduled waiting* before the return is at most g (class E); the elapsed time to the return includes class-X operations and has no bound (CC-9, WB-6) |
| **CC-3** | the PK subject's termination after a call is an SN send (SN-I-3), not an unspecified "killed" | it is a signal send by a helper | none; the call's decision is unaffected (SN-7) |
| **CC-4** | OH-S3 R2's "an abandoned child holds no descriptor of K (LD-3)" is now conditional on SN-8 (e), which rests on PO-SN (c) | the statement was unconditional and rests on a CPython behaviour that no accepted record cites | none |
| **CC-5** | SG-3 forbids setting `SIGCHLD` to `SIG_IGN` or `SA_NOCLDWAIT`; SG-9 forbids any send from a handler; LD-9 is extended to children | the sole-reaper and pinning argument (SI-2, SI-3) needs them | none |
| **CC-6** | the terminal-cause table gains rows 19 and 20, so NT-RL-8 reads "every row 1 … 20" | a holder can end, or be killed, while a child is abandoned or mid-sequence | none |
| **CC-7** | `systemd-run` (AK-1) and `systemctl stop` (BS-2, BS-3) are classed *mutating* children: after `error`, `interrupted` or an abandon their **effect is unknown** (SN-10) | an abandoned mutating child may act late; an `error` result is not evidence that it did not | none |

**Unchanged by R3** (checked by comparison with the OH-S3 R2 proposal): the safety
kernel G1 … G5 (§2), every deadline class and the withdrawal of unsupported
elapsed-time claims (§7.1 … §7.2, §7.7 W-1 … W-11), the parameters and sizing rules
(§7.6), PO-11 (d′) (§7.10), the accepted Route 3 boundary and R3-ROOT/R3-DR1 (§9.1),
the six alternatives and the SSW classification as a scope-change alternative that is
**not** Route 3 (§9.4, §9.7), WP-1 … WP-9 (§9.5, apart from the two clauses above),
the Role A–H inventory (§9.6), PO-12′ and PO-19 (§9.8), MF-1 … MF-8 (§10), the
successor order (§11, apart from the PO-SN entries above), DEC-1 … DEC-6 and BC-1 … BC-5 (§12), the decisions, the
baseline-change separation and the no-authority statements.

The R3-F1 remediation map is in Appendix D.

### 0.6 R4 change summary, consistency corrections, and what R4 leaves unchanged **Δ4**

**The findings.** R4-F1 and R4-F2 (both **Important**, design completeness and
correctness of the documented sequence) are stated in §0.1. Neither is a new host fact,
and neither gave authority for research.

**Sections changed by R4** (each is marked **Δ4** where it appears; R3's **Δ3** marks
are kept):

| Section | Change |
|---|---|
| title, header, §0.1 … §0.4, §0.6 | R4 identity and pin; the two finding bullets; the map rows; the scope and terminal-state sentences; this section |
| §1.1, §1.3 | the R4 reading; the tag row; the identifier list |
| §3 | vocabulary: *wait budget*, *reap attempt*, *late*, *CS* |
| §5.5 rows 19, 20; §5.6 RO-7 | the two terminal-cause rows and the residual widened to every child state CS-1 … CS-8 |
| §7.2 | class E: the cap on every sleep; what E does not bound |
| §7.3 | rows 2, 3, 3a, 3b, 3e, 7, 14 amended (the cap, the late send, the wording of the budget; **no class changes**); row 3g (reap attempt) added |
| §7.5 | HS-5 (the wait, the cap and the late escalation); the PK/2 subject and series sentences |
| §7.5a.2 | one sentence: `t_g` is read once, and a send returning at or after it leaves no timed wait |
| §7.5a.4 | SN-6 and SN-8 rewritten; SN-7 amended by one clause (`abandoned` is not evidence of life; a reap status is not evidence of an empty group); SN-10 unchanged |
| §7.5a.5 | table SN-R rows 1, 2, 4 … 8 and 10 amended; row 11 added |
| §7.5a.6, §7.5a.6a, §7.5a.6b | table SN-S rewritten; the closing paragraph replaced; **§7.5a.6a (new) the wait budget WB-1 … WB-7**; §7.5a.6b (new) a table of cases as a review aid |
| §7.5a.7 | table SN-RO amended: enclosing procedure, further signals from others, the explicit `attest` case, the boot as a separate event |
| §7.5a.8 | PO-SN (g) added (optional) |
| §7.5a.9 | record fields `grace_deadline_ms`, `late`, `waits_skipped`; condition `children-unknown` |
| §7.5a.10 | one clause: no claim of completion within g |
| §7.6 | the g row and the R3 note |
| §7.7 | W-14 added |
| §7.8 | SG-4 amended |
| §7.9 | **IM-S rewritten**: rules IS-1 … IS-8, the common state set CS-1 … CS-8, the point × outcome matrix, the owner table |
| §7.11 | one bullet |
| §7.12 | NT-DL-1, -2, NT-SG-3, NT-HS-3, NT-PK-1, NT-SN-2, -3, -4, -5, -7, -8, -9, -14, -16, -17 amended; NT-WB-1 … 12 and NT-IS-1 … 15 added |
| §8.2 | AW-3's wording of the PK/2 wait budget |
| §8.5, §8.6, §8.7 | the `children` key and conditions; INV-16, -18, -20, -21 amended and INV-22, -23 added; test groups (37), (38) |
| §9.5 (WP-4), §11 (slice 2a) | one clause each: the wait budget and the child-state set join the Route 3 work; optional PO-SN (g) joins the OH-S2b citation step. **The order and the gates are unchanged** |
| §13.1, §13.2 | RO-7; PO-SN (g); SN-1 … SN-10 row |
| §14.1 Q5, Q15; new Q16, Q17; §14.2 SR-12 | review questions and the claim needing security re-review |
| Appendix A (A-I-15, A-I-16, new A-I-17), B (B-08, B-13), C.2, D | the amendment, obligation and map rows |
| closing statement | one clause |

**Consistency corrections called out for review.** Each is directly necessary to close
R4-F1 or R4-F2. **None changes** a deadline class, a parameter value, a sizing rule
(N1 … N4), PO-11 (d′), the Route 3 boundary, the SSW classification, an MF disposition
or the hard stop.

| ID | Correction | Why it is necessary | Effect on a timing claim |
|---|---|---|---|
| **CC-8** | CC-1 (below, §0.5) said that, for the expired child, "both signals sit **inside** g". It now says that the **scheduled waits** of the SN sequence sit inside g and that the sends, the validations and the reap attempts do not belong to any wait | R4-F1: the statement is false when a send consumes g | W_show = c + g and W_series = P + c + g are unchanged as budgets of *scheduled waiting* (WB-6). The text that said otherwise is withdrawn (W-14) |
| **CC-9** | CC-2 (below, §0.5) said that the flag's `interrupted` return follows the SN sequence "by at most g". It now says the *scheduled waiting* of that sequence is at most g, and that the elapsed time to return is unbounded | R4-F1 item 4: wait budget is not elapsed time | none to the budget; the unbounded part was already class X |
| **CC-10** | WB-2's cap, "every sleep lasts at most the time remaining to its own deadline", is applied to **every E wait** (the child wait to c, the lock loop to λ, BSP's sleeps, the PK schedule), not only to S3 and S5 | R4-F1 asks for the cap on S3 and S5. W_show = c + g is a budget of scheduled waiting, and the child wait to c is the first term of it; a final sleep of `slice_ms` started just before c would otherwise add up to `slice_ms` to the sum. **This is the one place R4 extends the cap beyond S3 and S5, and the reviewer may prefer to reject the extension**; the consequence would be that W_show and W_series carry one extra `slice_ms` each | none to a parameter; it makes the existing budget true |
| **CC-11** | table SN-R rows 1, 2, 4 … 8 and 10 now refer to the capped waits, the reap attempt and `late`, in place of "one slice", "reap wait to `t_g`" and "abandon at once" | follows from WB-1 … WB-5 | none |
| **CC-12** | IM-S is rewritten (§7.9), the "as S0", "as S3" references are removed and the absolute statement that a killed helper leaves its children "unsignalled by anyone" is withdrawn (W-14) | R4-F2 items 1 … 3 | none |
| **CC-13** | terminal-cause rows 19 and 20 and RO-7 name the child states CS-1 … CS-8 instead of "a send failed or was not made and a child was abandoned" | R4-F2 item 5; the old wording covered a subset | none |
| **CC-14** | the `children` record gains `grace_deadline_ms`, `late` and `waits_skipped`, one anomaly `reaped-at-or-after-deadline`, and the recorded condition `children-unknown`; Appendix A gains A-I-17 | the budget and the lost-record case need evidence fields; `children-unknown` is how a later procedure reports a lost `child` line without searching | none: all are observations |
| **CC-15** | PO-SN (g), optional: the behaviour of a process's children when it ends | the interruption map states the child's fate as *unknown to the design*; (g) records what a later citation could add, without any safety claim resting on it | none |

**Unchanged by R4** (checked by comparison with the R3 proposal): the safety kernel
G1 … G5 (§2), every deadline class and the withdrawal of unsupported elapsed-time claims
(§7.1, §7.2 apart from the cap in the E row, W-1 … W-13), **all parameter values** and the
sizing rules N1 … N4 (§7.6), PO-11 (d′) (§7.10), the accepted Route 3 boundary and
R3-ROOT/R3-DR1 (§9.1), the six alternatives and the SSW classification (§9.4, §9.7),
WP-1 … WP-9, the Role A–H inventory (§9.6), PO-12′ and PO-19 (§9.8), MF-1 … MF-8 (§10), the
successor order (§11, apart from the PO-SN (g) entry), DEC-1 … DEC-6 and BC-1 … BC-5
(§12), SN-1 … SN-5 and SN-7, SN-9, SN-10, SI-1 … SI-4, the escalation signal set and its
at-most-once rule, the abandon rule, the decisions, the baseline-change separation and the
no-authority statements.

The R4 remediation map is in Appendix D.

### 0.7 R5 change summary, consistency corrections, and what R5 leaves unchanged **Δ5**

**The findings.** R5-F1 and R5-F2 (both **Important**, correctness of the documented
interruption map and of a regression case) are stated in §0.1. Neither is a new host fact,
and neither gave authority for research.

**Sections changed by R5** (each is marked **Δ5** where it appears; the **Δ3** and **Δ4**
marks are kept):

| Section | Change |
|---|---|
| title, header, §0.1, §0.2, §0.4, §0.7 | R5 identity and pin; the two finding bullets; the map rows; the terminal-state sentence; this section |
| §1.1, §1.3 | the R5 reading; the tag row; the identifier list |
| §3 | vocabulary: *reap attempt*, *kernel reap*, RA-0 … RA-4, CS-1 … CS-8, T0 … T7 with T3k and T5k |
| §5.5 rows 19, 20; §5.6 RO-7 | the child states and points named include the kernel reap inside an attempt (CS-5, T3k, T5k) |
| §7.3 row 3g | one sentence: the attempt's five phases and the raised-exception question |
| §7.5a.3 SI-3; §7.5a.4 SN-7 | one clause each: where `state = running` is exact; a kernel reap with no durable record is evidence of nothing |
| §7.5a.6 (the sentence before table SN-S), §7.5a.6a WB-5 | one sentence each: the interior of an attempt is defined in §7.5a.6c, and changes no step of table SN-S |
| §7.5a.6b | the one case row "a slow validation" is split into a slow-S1 row and a slow-S4 row (R5-F2) |
| **§7.5a.6c (new)** | **the boundary of a reap attempt: phases RA-0 … RA-4, rules RB-1 … RB-5, the mapping to points** |
| §7.5a.8 | PO-SN (c) extended by one clause: whether `Popen.poll()` can raise after the kernel has consumed the status |
| §7.5a.9 | the record paragraph: CS-5 included among the states that leave no line, and what a later procedure may and may not read |
| §7.7 | W-15 added |
| §7.9 | IM-S: the introduction; IS-1, IS-3, IS-5 amended and **IS-9 added**; the point list (**T3, T5, T6 redefined; T3k, T5k added**); the state set (**CS-5 and CS-7 redefined**); the matrix (**rows T3k, T5k added; cells T0, T1, T5 corrected**); "Reading the matrix" (**E1 rewritten**, the observer bullet) |
| §7.12 | **NT-WB-5 split into NT-WB-5a and NT-WB-5b**; NT-IS-1, -6, -8, -11, -14 amended; NT-IS-16, -17 added |
| §8.5, §8.6, §8.7 | the `children` key; INV-18, -20, -23 amended; test group (38) |
| §13.1, §13.2 | RO-7; the status rows for IS, RB, CS and PO-SN (c) |
| §14.1 Q17; new Q18, Q19; §14.2 SR-13 | review questions and the claim needing security re-review |
| Appendix A (A-I-16, A-I-17), B (B-13), C.2, D | the amendment, obligation and map rows |
| closing statement | one clause |

**Consistency corrections called out for review.** Each is directly necessary to close
R5-F1 or R5-F2. **None changes** a deadline class, a parameter value, a sizing rule
(N1 … N4), PO-11 (d′), a send rule, a wait rule (WB-1 … WB-7), the Route 3 boundary, the
SSW classification, an MF disposition or the hard stop.

| ID | Correction | Why it is necessary | Effect on a timing claim |
|---|---|---|---|
| **CC-16** | T3 and T5 are redefined to mean "not yet reaped by the kernel"; the new points **T3k** and **T5k** are the phase RA-2 inside S3 and S5; **T6 begins at the handle-state update (RA-3) or the abandon decision, never earlier** | R5-F1 items 1 and 2: an interruption inside an attempt cannot be T6, and cannot be T3 or T5 with a child that is certainly unreaped | none |
| **CC-17** | **CS-5 and CS-7 are redefined**: the direct child is *reaped in the kernel* by the helper's own `waitpid`; CS-5 does not say that the helper's memory recorded it. CS-6 and CS-8 are unchanged | R5-F1 item 3: a state must exist that permits the true direct-child condition at T3k and T5k | none |
| **CC-18** **Δ6: superseded by CC-23 and W-16** | the matrix cells T0 `u` and T1 `u` admit CS-5 (a handle already reaped by the enclosing wait's own poll), and the introduction of the point list states that the wait's own polls precede T0 and have the same phases | R4's table SN-R row 3 and NT-SN-5 (a) admit SN with a reaped handle and NT-IS-6 expected CS-5 or CS-7 for it, while the matrix said CS-1; item 6 requires every cell to be exact | none |
| **CC-19** | the matrix cell T5 `i` names CS-2 for a PK subject whose S4 validation rejected | the PK subject has no `SIGTERM` (S2 and S3 are skipped), so CS-3 would assert a send that was never attempted; item 6 | none |
| **CC-20** **Δ6: its last sentence is superseded by RE-1 and W-16** | SI-3 and row 3g say where the handle's `state = running` is exact, name RA-2 as the only window in which it is stale, and send the question whether a raised exception can follow the kernel's reap to PO-SN (c) and Q18. **Row 3g's reading of a raised exception as *unreaped* is not changed** | the boundary is incomplete without saying that no send is made in that window; the exception question is surfaced, not decided (§0.4) | none |
| **CC-21** | IS-1, IS-3 and IS-5 are amended and **IS-9** (the observer rule) is added; "IS-1 … IS-8" becomes "IS-1 … IS-9" where it names the current set; W-15 withdraws the R4 sentences that R5-F1 refuted | R5-F1 items 3 and 4 | none |
| **CC-22** | NT-WB-5 is split; the case table of §7.5a.6b is split likewise; NT-IS-1, -6, -8, -11, -14 are amended; NT-IS-16 and -17 are added; "NT-IS-1 … 15" becomes "NT-IS-1 … 17" where it names the current set; "NT-WB-1 … 12" is kept, NT-WB-5 now being two subcases | R5-F1 item 6 and R5-F2 items 1 … 5 | none |

**Unchanged by R5** (checked by comparison with the R4 proposal, §8 of the handback): the
safety kernel G1 … G5 (§2), every deadline class (§7.1, §7.2), **all parameter values** and
the sizing rules N1 … N4 (§7.6), PO-11 (d′) (§7.10), WB-1 … WB-4 and WB-6, WB-7, table SN-S
(S0 … S6), table SN-R (rows 1 … 11), SN-1 … SN-6 and SN-8 … SN-10, SI-1, SI-2, SI-4, the
escalation signal set and its at-most-once rule, the abandon rule, table SN-RO and the owner
table of §7.9, the outcome codes `u`, `i`, `x`, `s`, `e`, `f`, CS-1 … CS-4, CS-6 and CS-8,
T0, T1, T2, T4 and T7 as definitions, the accepted Route 3 boundary and R3-ROOT/R3-DR1
(§9.1), the six alternatives and the SSW classification (§9.4, §9.7), WP-1 … WP-9, the
Role A–H inventory (§9.6), PO-12′ and PO-19 (§9.8), MF-1 … MF-8 (§10), the successor order
(§11), DEC-1 … DEC-6 and BC-1 … BC-5 (§12), the decisions, the baseline-change separation
and the no-authority statements.

The R5 remediation map is in Appendix D.

### 0.8 R6 change summary, consistency corrections, and what R6 leaves unchanged **Δ6**

**The findings.** R6-F1 (**Blocking**, a design path to a root signal sent to a possibly
reused process-group number) and R6-F2 (**Important**, a state machine and its completeness
tests that disagree) are stated in §0.1. Neither is a new host fact, and neither gave
authority for research.

**Sections changed by R6** (each is marked **Δ6** where it appears; the **Δ3**, **Δ4** and
**Δ5** marks are kept):

| Section | Change |
|---|---|
| title, header, §0.1 … §0.4, §0.8 | R6 identity and pin; the two finding bullets; the map rows; the scope and terminal-state sentences; this section |
| §1.1, §1.3 | the R6 reading; the tag row; the identifier list |
| §3 | vocabulary: *reap-unknown*, *RE*, *RA-E*, *S7*, *S8*, CS-1 … CS-10, T0 … T7 with T3x and T5x |
| §5.5 rows 19, 20; §5.6 RO-7 | the child states and points named include CS-9, CS-10, T3x and T5x |
| §7.2 (class E row), §7.3 rows 3, 3e, 3g | the suppression after a `reap-error`; row 3e one clause; row 3g rewritten |
| §7.5 HS-5, PK/2 | one clause each: a child suppressed by a `reap-error` is never signalled |
| §7.8 SG-4 | one clause: a reap-error ends the sequence at once |
| §7.5a.3 | the handle's state set gains `reap-unknown`; SI-3 and SI-4 amended |
| §7.5a.4 | SN-4, SN-6, SN-7 and SN-8 amended |
| §7.5a.5 | table SN-R rows 1, 2, 3, 4, 5, 7, 8 and 9 amended; **row 12 added** |
| §7.5a.6 | the lead sentence; table SN-S: **S1 split into S1-a and S1-b**; S3, S4, S5 and S6 amended; **S7 and S8 added**; the paragraph after the table |
| §7.5a.6a | WB-5 (a) amended and (e) added; WB-7 amended |
| §7.5a.6b | four case rows added |
| §7.5a.6c | table: RA-3 amended and **RA-E added**; RB-1 … RB-4 amended; **RB-5 replaced** by a pointer |
| **§7.5a.6d (new)** | **the reap error: RE-1 … RE-6** |
| §7.5a.7 | the first paragraph: a child suppressed by a `reap-error` is owned like an abandoned one |
| §7.5a.8 | PO-SN (c) narrowed, **(c′) added**, the AP-0 sentence |
| §7.5a.9 | the record fields and the paragraph on lines that are not written |
| §7.7 | W-16 added |
| §7.9 | IM-S: the introduction; IS-9 amended and **IS-10 added**; the point list (**T0, T1 narrowed; T3x, T5x added; T6 amended**); the paragraph *Before T0*; the outcome `u`; the state set (**CS-9, CS-10 added**); the matrix (**rows T3x, T5x added; cells T0, T1, T6, T7 corrected**); *Reading the matrix* (E1 rewritten, the corrected-cells paragraph, the observer bullet); the owner table |
| §7.12 | NT-SN-5, -6, -7, -9, -12, -18, NT-WB-11, NT-IS-1, -5, -6, -11, -13, -14, -16, -17 amended; **NT-RE-1 … 12 and NT-NS-1 … 8 added** |
| §8.1 (AP-0), §8.5, §8.6, §8.7 | AP-0's sentence on (c′); the `children` key; INV-18, -20, -21, -23 amended; **INV-24, INV-25 added**; test groups (39), (40) |
| §9.5 (WP-4), §11 (slice 2a) | one clause each: the child-state set and the reap-error rules join the Route 3 work; the evidence-only PO-SN (c′) joins the OH-S2b citation step. **The order and the gates are unchanged** |
| §13.1, §13.2 | RO-7; the status rows for PO-SN (c) and (c′), RE, IS and CS |
| §14.1 Q17; Q18 rewritten; new Q20, Q21; §14.2 SR-13; new SR-14 | review questions and the claims needing security re-review |
| Appendix A (A-I-16, A-I-17), B (B-13), C.2, D | the amendment, obligation and map rows |
| closing statement | one clause |

**Consistency corrections called out for review.** Each is directly necessary to close
R6-F1 or R6-F2. **None changes** a deadline class, a parameter value, a sizing rule (N1 …
N4), PO-11 (d′), a wait rule (WB-1 … WB-4, WB-6), the one absolute `t_g`, the at-most-once
send rule, the Route 3 boundary, the SSW classification, an MF disposition or the hard
stop. **No send and no wait is added anywhere; CC-27 and RE-1 remove one send (S4 after a
`reap-error`).**

| ID | Correction | Why it is necessary | Effect on a timing claim |
|---|---|---|---|
| **CC-23** | T0 and T1 exist **only for a handle in state `running`**. A handle that is `reaped`, `abandoned` or `reap-unknown` when SN is entered ends at S1-a and S7: its settled-state decision was made **before SN** (at RA-3 of the enclosing poll, at S6, or at S8), the interval from that decision to the durable line is **T6**, and the durable line is **T7**. The matrix cells T0 `u` and T1 `u` return to CS-1 only. R5's CC-18 cell correction (T0 and T1 `u` admitting CS-5) and its paragraph *Before T0* are superseded | R6-F2 item 3: an interruption must not be at T0 or T1 and at T6 or T7 at once, and the settled-state decision and the record must each occur exactly once, at a stated place | none |
| **CC-24** | table SN-S gains **S7**, *settle, record, return*. R5's "stop" in S3 and S5 and S6's "record" meant it without naming it; S1-a needs the same path. S7 writes the `child` line once, best effort, never retries it, and returns the enclosing operation's result | R6-F2 item 1: "the applicable settled-state record path" must be a step | none: S7 makes no send, no wait and no clock read |
| **CC-25** | table SN-R row 3 (reaped) and row 9 (reaped, abandoned, reap-unknown) now say *no call, no wait, ends at S7*; rows 7 and 8 say *no send, S5*; **row 12** (a reap attempt raised) is added; rows 1, 2, 4, 5 name the S8 branch of a raising attempt | R6-F2 items 1 and 3; R6-F1 item 4 | none |
| **CC-26** | the handle state `reap-unknown`; phase RA-E; points T3x and T5x; child states CS-9 and CS-10; IS-10; E1 and the matrix extended; RB-5 (R5's open question) is replaced by RE-1 … RE-6; "CS-1 … CS-8" becomes "CS-1 … CS-10", "IS-1 … IS-9" becomes "IS-1 … IS-10", "RB-1 … RB-5" becomes "RB-1 … RB-4 and RE-1 … RE-6" where the current set is named | R6-F1 items 2 and 4 | none |
| **CC-27** | WB-7 no longer allows "the single escalation of S4" after a reap-attempt exception: **a `reap-error` causes no further send of any kind** (RE-1). R5's wording ("a reap-attempt exception … cause[s] no further send apart from the single escalation of S4") is withdrawn (W-16) | R6-F1 item 1: that clause was the path to the root `SIGKILL` | removes a send; adds none |
| **CC-28** | PO-SN (c) is split: (c) keeps `setsid`, the return of `Popen()` after `exec`, `close_fds`, the reaping `poll()` and the destructor; the post-poll exception question is **(c′)**, evidence-only. AP-0 still names (a), (b), (c), (e), (f) and does **not** read (c′). Q18 is rewritten | R6-F1 item 5 | none |
| **CC-29** | the `children` record gains `reap_unknown` and `send_suppressed`; the anomaly `reap-error` (R5) now has a defined consequence; the `children-unknown` gap covers CS-9; INV-24 and INV-25 are added | R6-F1 items 3 and 4 | none: observations |
| **CC-30** **Δ7: its claim that validation sees an injected foreign reap as `not-sent(identity-mismatch)` or `not-sent(identity-unverifiable)` and sends it to S5 is withdrawn (CC-33, W-17); the rest is kept as history** | NT-SN-12's expectation for an injected foreign reaper is corrected: the handle's state is changed only by `reap_step()` (SI-3), so a foreign reap is seen by validation as `not-sent(identity-mismatch)` or `not-sent(identity-unverifiable)` and goes to S5; it is never seen as `not-sent(reaped)`. NT-SN-5 … 7 and NT-IS-5, -6 say which branch each `not-sent` subtype takes | R6-F2 item 3: those tests named `not-sent(reaped)` for a result that the state test cannot produce | none |

**Unchanged by R6** (checked by comparison with the R5 proposal, §8 of the handback): the safety
kernel G1 … G5 (§2), every deadline class (§7.1, §7.2 apart from one clause of the E row),
**all parameter values** and the sizing rules N1 … N4 (§7.6), PO-11 (d′) (§7.10), WB-1 … WB-4
and WB-6, table SN-S steps S0 and S2, SN-1 … SN-3, SN-5, SN-9 and SN-10, SI-1 and SI-2, the
escalation signal set and its at-most-once rule, the abandon rule's condition (a *normal*
return of the final attempt that finds the child unreaped), table SN-RO, the owner table of
§7.9, the outcome codes `u`, `i`, `x`, `s`, `e`, `f` (the meaning of `u` is made exact),
CS-1 … CS-8 as definitions, the phases RA-0 … RA-4, T2 and T4 as definitions, the accepted
Route 3 boundary and R3-ROOT/R3-DR1 (§9.1), the six alternatives and the SSW classification
(§9.4, §9.7), WP-1 … WP-9, the Role A–H inventory (§9.6), PO-12′ and PO-19 (§9.8), MF-1 …
MF-8 (§10), the successor order (§11), DEC-1 … DEC-6 and BC-1 … BC-5 (§12), the decisions, the
baseline-change separation and the no-authority statements.

The R6 remediation map is in Appendix D.

### 0.9 R7 change summary, consistency corrections, and what R7 leaves unchanged **Δ7**

**The findings.** R7-F1 (**Important**, a record schema, an invariant and a test that
cannot all hold on one path), R7-F2 (**Important**, a test and a correction note that claim
more than the detector can show) and R7-F3 (**Optional**, a vocabulary row) are stated in
§0.1. None is a new host fact, and none gave authority for research.

**Sections changed by R7** (each is marked **Δ7** where it appears; the **Δ3** … **Δ6**
marks are kept):

| Section | Change |
|---|---|
| title, header, §0.1 … §0.4, §0.9 | R7 identity and pin; the three finding bullets and a note at the head of §0.1; the §0.2 map rows; the scope and terminal-state sentences; this section |
| §0.8 | the row **CC-30** is marked superseded (its text is kept as history) |
| §1.1, §1.3 | the R7 reading; the tag row |
| §3 | vocabulary: the **CH row lists all four states** (R7-F3); new terms *s0_ran*, *GD*, *SI-5* |
| §7.5a.3 | SI-2 (one clause: the sole-reaper invariant is part of the defence); **SI-3 made explicit and load-bearing**; **SI-5 added** |
| §7.5a.4 | SN-4 (one clause: a detector, no reuse claim); SN-6 ("one grace deadline per child" becomes "at most one") |
| §7.5a.5 | table SN-R row 12 (one clause: before S0 no `t_g`) |
| §7.5a.6 | table SN-S: **S0's entry condition** and S8's `t_g` clause; the paragraph after the table |
| §7.5a.6a | WB-1 (one clause: when S0 runs) |
| §7.5a.6b | one case row added: a `reap-error` before S0 |
| §7.5a.6d | RE-4 (one clause: nothing to read or leave unused before S0), RE-5 (the record) |
| **§7.5a.6e (new)** | **the grace deadline exists exactly when S0 ran: GD-1 … GD-5, the record of every pre-S0 and settled-entry path** |
| §7.5a.9 | the record fields `s0_ran`, `grace_deadline_ms` (integer or `null`) and `outcome` (`reap-error` added) |
| §7.9 | the paragraph *Before T0*: one sentence (a poll that raised is before S0; a settled handle reaches S1-a without S0) |
| §7.7 | **W-17** (R7-F2) and **W-18** (R7-F1) added |
| §7.12 | NT-SN-5, -6, -9, **NT-SN-12 (rewritten)**, NT-WB-11, -12, NT-RE-7, -11, -12, NT-NS-1 … 3 amended; **NT-GD-1 … 4 added** |
| §8.1 (AP-0), §8.5, §8.6, §8.7 | AP-0 unchanged (a sentence says so); the `children` key; INV-19, INV-22 amended and **INV-26, INV-27 added**; test group (41) |
| §13.2 | the status rows for SI-1 … SI-5 and GD-1 … GD-5 |
| §14.1 Q15, Q21; new Q22, Q23, Q24; §14.2 SR-12; new SR-15 | review questions and the claim needing security re-review |
| Appendix A (A-I-16, A-I-17), B (B-08, B-13), C.2, D | the amendment, obligation and map rows |
| closing statement | one clause |

**Consistency corrections called out for review.** Each is directly necessary to close
R7-F1 or R7-F2. **None changes** a deadline class, a parameter value, a sizing rule (N1 …
N4), PO-11 (d′), a wait rule (WB-1 … WB-4, WB-6, apart from WB-1's clause), the one
absolute `t_g` of every sequence in which S0 ran, the at-most-once send rule, any send, any
proof obligation, the Route 3 boundary, the SSW classification, an MF disposition or the
hard stop. **No send, wait, grace period, clock read or identity mechanism is added.**

| ID | Correction | Why it is necessary | Effect on a timing claim |
|---|---|---|---|
| **CC-31** | **S0 is entered only for a `running` handle.** A handle that is `reaped`, `abandoned` or `reap-unknown` when SN is called goes from SN's entry straight to S1-a and S7 **without S0 and without a clock read**. R6 listed S0 before S1, so a call on a settled handle read a `t_g` first, and a later call on a handle that a pre-S0 `reap-error` had settled (NT-RE-7) would have created a `t_g` after the `child` line had been written with none | R7-F1 item 2: `t_g` exists exactly when S0 ran, and a record that is written once cannot be contradicted by a later read. The behaviour of S1-a is unchanged (no call, no wait, ends at S7); only a clock read that nothing used is removed | removes one clock read on a path that makes no wait; adds none |
| **CC-32** | the `children` record key `grace_deadline_ms` is **always present** and is an integer iff the new boolean `s0_ran` is true, otherwise `null`; `outcome` gains the value `reap-error`, used only when S0 did not run and a `reap-error` ended the child's enclosing wait; "one grace deadline per child" (SN-6, WB-1, INV-22, NT-WB-11 (i)) becomes "**at most one**: exactly one if S0 ran, none otherwise" | R7-F1 items 1, 3: R6 required a deadline for every child, including one that exits within c, one that fails to spawn and one whose enclosing poll raised, none of which ever starts a grace period | none: an observation field and the wording of a count |
| **CC-33** | **CC-30 (R6) is superseded in part.** The part of its claim that a foreign reap "is seen by validation as `not-sent(identity-mismatch)` or `not-sent(identity-unverifiable)` and goes to S5" is withdrawn (W-17). Its remaining content, that each `not-sent` subtype takes the branch SN-S gives it and that a foreign reap is never seen as `not-sent(reaped)`, is kept only as a statement about the **state test** (SI-3): the state is changed by `reap_step()` alone | R7-F2 items 1 … 5 | none |
| **CC-34** | NT-SN-12 is rewritten around the structural sole-reaper properties, with one labelled non-universal detector exercise; NT-SN-6 (b) carries the same label; NT-RE-7, NT-RE-11, NT-RE-12, NT-SN-9 and NT-WB-11 (i) say what a pre-S0 `reap-error` reads and records; NT-GD-1 … 4 are added | R7-F1 item 4; R7-F2 item 3 | none |

**Handle-state vocabulary check (R7-F3 item 2).** Every current, non-historical definition
or list of the handle's state set was inspected: §3 vocabulary row **child handle (CH)**
(**corrected**: it listed `running`, `reaped`, `abandoned`); §3 row **reap-unknown (RU)**
(names the fourth state); §7.5a.3 CH (`running`, `reaped`, `abandoned`, `reap-unknown`:
**complete**); §7.5a.3 SI-4, §7.5a.6 S1-a and S7, §7.5a.6a WB-5 (a), table SN-R row 9 and
INV-25 (each lists the **settled** states `reaped`, `abandoned`, `reap-unknown`: a subset
by design, complete for its purpose); §7.5a.6d RE-2 and RE-3 (name the states the handle
never moves to). The handle-state *summary* of historical rows (§0.5 … §0.8 change tables,
the withdrawn-claims table W-1 … W-16, and the Appendix D rows of earlier rounds) is
historical and **was not rewritten**.

**Unchanged by R7** (checked by comparison with the R6 proposal, §8 of the handback): the
safety kernel G1 … G5 (§2), every deadline class (§7.1, §7.2), **all parameter values** and
the sizing rules N1 … N4 (§7.6), PO-11 (d′) (§7.10), WB-1 … WB-7 (WB-1 by one clause),
every step of table SN-S except S0's entry condition and one clause of S8, SN-1 … SN-3, SN-5 and SN-7 … SN-10,
SI-1, SI-2, SI-4, the escalation signal set and its at-most-once rule, the abandon rule,
RE-1 … RE-3 and RE-6, the phases RA-0 … RA-4 and RA-E, RB-1 … RB-4, table SN-RO, the owner
table of §7.9, IS-1 … IS-10, CS-1 … CS-10, the matrix, T0 … T7 with T3k, T3x, T5k and T5x,
PO-SN (a) … (g) including (c′), the AP-0 condition, the accepted Route 3 boundary and
R3-ROOT/R3-DR1 (§9.1), the six alternatives and the SSW classification (§9.4, §9.7), WP-1 …
WP-9, the Role A–H inventory (§9.6), PO-12′ and PO-19 (§9.8), MF-1 … MF-8 (§10), the
successor order (§11), DEC-1 … DEC-6 and BC-1 … BC-5 (§12), the decisions, the
baseline-change separation and the no-authority statements.

The R7 remediation map is in Appendix D.

---

## 1. Sources, method and fact classes

### 1.1 Repository documents read

**Carried from the OH-S3 R2 proposal.** The paragraphs below, down to the paragraph
headed "R3 reading", record the reading that produced the text R3 amends. In
them "this assignment" means the OH-S3 R2 assignment, and "R1's" and "R2's" keep
their OH-S3 meaning. R3's own reading follows them.

**Read completely:** `.agents/AGENTS.md`; this assignment's prompt and authority;
the R1 prompt, the R1 authority, the complete R1 proposal and the complete R1
handback; the accepted OH-S2 R2 acceptance, the OH-S2 R2 handback, and the accepted
R3 H-0 completeness acceptance; `docs/review/Handover information`; the
`docs/project-management/status.md` pointer; the restriction banner of
`docs/operations/disposable-test-server.md`.

**Read by section:** `docs/implementation-plan.md` (the reading map; §0.1 … 0.5;
§14.1 … 14.3; §16 in full; §17 in full; §20 in full). The accepted R2 citation record
`phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md`: §0.1 … 0.2 (the verdict summary and
terminal dispositions), §6.3 … 6.4, §7, §8 (every limb), §10.4 … 10.5, §11.6,
§12.9, §14.3 … 14.4, §15.4 … 15.5, §16, and the section headings; fixed-string
searches elsewhere. DR1 `phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-proposal.md`
§5.3 … 5.5 (the definition of Route 3) and the accepted R3 proposal's §6.3 … 6.5. The
one-host design
`phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`: the trace
and trust table (§4.1.3), the `ACT`/`DEACT` order and D3-R2 (d) … (l) in full (steps,
literals, backstop, hold loop, CL, attestation, states, the death matrix and
"what remains"), D3-R5 (e) CQ-0 … CQ-7 and (i) the boundary matrix, and fixed
searches for the interpreter literal, `systemctl`, `pkcheck` and `systemd-run`. C11
and D2 by the lines the design and R1 cite (the interpreter literal occurrences), and
D2's header. The operational draft
`phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` by heading and by
fixed searches for elapsed-time language, `PIN.interpreter` and the §9.5.3 and C-15
anchors (**not edited**). The tracked, non-secret launcher sources only by the
line numbers of the Role A literals (`infra/rp11-launch/launch.c`,
`tools/phase_5_0_evidence/rp11_launch.py`, and the evidence-harness review manifest).

**Carried from R1 without re-reading the underlying source:** the line references
of the Role A inventory outside the files listed above (C11 and D2 lines, the design's
`:2481`, `:5242`, `:6979`, and the `launch.c` structure), and the launcher build
description of §9.7 and §9.11. The R1 proposal states them, and the lines that I
re-checked by fixed search agree with R1's. I did not re-verify the rest and state
them as R1's.

No host, retained-evidence path, secret-bearing path, credential, player datum
or network resource was touched. No recursive search was rooted at the repository,
a workspace root, home, `/opt`, `/var`, `/tmp` or `/`. Every search named its file,
or listed the documents of the one directory `docs/review/` by name.

**R3 reading (this assignment).** *Read completely:* `.agents/AGENTS.md`; the R3
prompt and its authority; the R2 prompt and its authority; `docs/review/Handover information`; the
complete OH-S3 R2 proposal and the complete OH-S3 R2 handback; the restriction
banner of `docs/operations/disposable-test-server.md`; the §20 pointer of
`docs/implementation-plan.md` and the `docs/project-management/status.md` pointer.
*Read by section:* `docs/implementation-plan.md` (the reading map, §0.1 … 0.5, §14.1
… 14.3, §16 in full, §17 in full, §20 in full). *By fixed-string search only,
over the named documents:* the accepted OH-S2 R2 citation record and the one-host
design, for `killpg`, `os.kill`, `kill(`, `ESRCH`, `pidfd`, `start_new_session`,
`setsid`, `process group`, `SIGCHLD`, `KillMode`, `control-group`, `FINAL_SIGTERM`
and `SendSIGKILL` (result in §7.5a.8: **no accepted record cites any of the first
nine as a behaviour**; the record cites `FINAL_SIGTERM`/`FINAL_SIGKILL` "to what
remains" and the `kill.c:13–16` defaults at its §8 (e), and lists `KillMode` only as a
property row), and for `backstop-intent` and `pk-root/1` in the one-host design. **Not
re-read in R3:** the R1 prompt, authority, proposal and handback (no R1-only
obligation is carried by R3-F1, and their unchanged state is checked by digest), the
accepted OH-S2 R2 record beyond those searches (the OH-S3 R2 proposal's citations of
it are carried, not re-verified), the one-host design beyond those searches and the
operational draft (Appendix B's row identifiers are carried from the OH-S3 R2
proposal; the draft's digest was recorded before the first edit and compared at the
end). No host, retained-evidence path, secret-bearing path, credential, player datum
or network resource was touched.

**R4 reading (this assignment) Δ4.** *Read completely:* `.agents/AGENTS.md`; the R4
prompt and its authority; the R3 prompt, the R3 authority, the **complete** R3 proposal
(3,094 lines) and the **complete** R3 handback; `docs/review/Handover information`; the
restriction banner of `docs/operations/disposable-test-server.md`; the `docs/project-management/status.md`
pointer. *Read by section:* `docs/implementation-plan.md` (the reading map; §0.1 … 0.5;
§14.1 … 14.3; §16 in full; §17 in full; §20 in full). *By fixed-string search and by the
exact lines named, over named documents only:* the OH-S3 R2 proposal (the anchors
`reap_grace_ms`, `IM-L`, `SG-4`, `W_show` and its §7.9 opening, to confirm that the
deadline, signal and interruption text R3 carried is unchanged); the accepted OH-S2 R2
record (rows (c), (e), (j) of §8, read in full for `FINAL_SIGTERM`, `FINAL_SIGKILL` and the
timer behaviour that the owner table cites); the one-host design (`backstop-intent`,
`backstop-armed`, BS-2, BS-3 and the disarm text: **R4 re-searched for the by-name disarm
that R3 left as a confirmation item and found only BS-2 and BS-3, in which the backstop
disarms itself on a terminal `deact` record; no step of CL that disarms the timer by name
was matched by the fixed strings used, so the item stays open for OH-S0d and is
widened in A-I-16**); and the operational draft (the stop-condition table of §11.2, the
no-retry rule of §11.3 and the opening of the §14 handback template, as the consumers of
B-06, B-08 and B-13), without editing it. **Not re-read in R4:** the R1 prompt, authority,
proposal and handback and the R2 prompt, authority and handback (their unchanged state is
checked by digest); the accepted OH-S2 R2 record beyond the rows named; the one-host
design beyond the searches; the operational draft beyond the three places named
(Appendix B's other row identifiers are carried from R3). **Carried citations are
carried, not re-verified:** every `[R2 §n]` and `[D §n]` citation of R3 that R4 did not
touch. No host, retained-evidence path, secret-bearing path, credential, player datum or
network resource was touched, and no recursive search was rooted at the repository, a
workspace root, home, `/opt`, `/var`, `/tmp` or `/`.

**R5 reading (this assignment) Δ5.** *Read completely:* `.agents/AGENTS.md`; the R5
prompt and its authority; the R4 prompt (all 220 lines) and its authority; the
**complete** R4 proposal (3,594 lines, read in passes) and the **complete** R4 handback
(312 lines); `docs/review/Handover information`; the restriction banner of
`docs/operations/disposable-test-server.md` (lines 1 … 110); and
`docs/project-management/status.md` (all 141 lines). *Read by section:*
`docs/implementation-plan.md`: the reading map (lines 19 … 52), §0.1 … 0.5 (53 … 183),
§14.1 … 14.3 (2216 … 2250), §16 in full (2394 … 2490), §17 (2492 … 2511) and §20 in
full (2558 to the end). *Read at the exact text named:* the R3 proposal's interruption
map and signal-sequence text (the old IM-S table T0 … T5 and its closing sentence, lines
1829 … 1846 of that file, and the heading of its table SN-S), to confirm that the
remediation does not regress R3-F1: R4 had already replaced that table, and R5 changes
none of R3's inventory SN-I, its class statement, its results table SN-R, the
child-handle contract SI-1, SI-2, SI-4 or the pinning argument; SI-3 gains one clause
(CC-20). The operational draft
`phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` at §11.2, §11.3 and the
opening of §14 (lines 1344 … 1362 and 1459 … 1478), as the consumers of B-13, **without
editing it**. **Not re-read in R5:** the R1, R2 and R3 prompts, authorities, proposals
and handbacks beyond the R3 text named above (their unchanged state is checked by
digest); the accepted OH-S2 R2 citation record and the one-host design: **no R5 claim
cites a section of either, so none was searched** and every `[R2 §n]` and `[D §n]`
citation of R4 is **carried, not re-verified**; the operational draft beyond the three
places named (Appendix B's other row identifiers are carried from R4). No host,
retained-evidence path, secret-bearing path, credential, player datum or network
resource was touched, and no recursive search was rooted at the repository, a workspace
root, home, `/opt`, `/var`, `/tmp` or `/`.

**R6 reading (this assignment) Δ6.** *Read completely:* `.agents/AGENTS.md`; the R6 prompt
(229 lines) and its authority; the R5 prompt (all 216 lines) and its authority; the
**complete** R5 proposal (3,891 lines, read in passes, partly through a byte-identical
scratchpad copy) and the **complete** R5 handback (300 lines); `docs/review/Handover
information` (175 lines); the restriction banner of `docs/operations/disposable-test-server.md`
(lines 1 … 115); and `docs/project-management/status.md` (all 169 lines). *Read by section:*
`docs/implementation-plan.md`: the reading map (lines 19 … 51), §0.1 … 0.5 (53 … 183), §14.1 …
14.3 (2216 … 2250), §16 in full (2394 … 2490), §17 (2492 … 2511) and §20 in full (2558 to the
end). *Read at the exact text named:* the R4 proposal's table SN-R, table SN-S and WB-5 (lines
1749 … 1783 and 1821 … 1842 of that file) and its IM-S (lines 2148 … 2260: the rules IS-1 …
IS-8, the points, the outcomes, the state set CS-1 … CS-8 and the matrix), to confirm that the
remediation does not regress R4-F1 or R4-F2 (R4's matrix had T0 `u` and T1 `u` as CS-1 only and
T6 `u` and T7 `u` as CS-5 and CS-7; R6 returns to those cells, CC-23); and the R3 proposal's
signal-sending contract (lines 1412 … 1500 and 1552 … 1600 of that file: table SN-I, the class
statement, CH and SI-1 … SI-4, SN-1, table SN-R, table SN-S and table SN-RO), to confirm that
the remediation does not regress R3-F1: R6 changes none of SN-I, the class statement, SI-1,
SI-2, SN-1 … SN-3, SN-5, SN-9 or SN-10, and the changes to SI-3, SI-4, SN-4, SN-6 … SN-8 and
table SN-R are listed in §0.8. The operational draft
`phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` at §11.2, §11.3 and the opening
of §14 (lines 1344 … 1362 and 1459 … 1478), as the consumers of B-13, **without editing it**;
its SHA-256 was recorded before the first edit. **Not re-read in R6:** the R1, R2 and R3 prompts,
authorities, proposals and handbacks beyond the R3 text named above, and the R4 prompt, authority,
proposal and handback beyond the R4 text named above (their unchanged state is checked by digest);
the accepted OH-S2 R2 citation record and the one-host design: **no R6 claim cites a section of
either, so none was searched**, and every `[R2 §n]` and `[D §n]` citation of R5 is **carried, not
re-verified**; the operational draft beyond the three places named (Appendix B's other row
identifiers are carried from R5). The R6 prompt's item 8 asks for those records at the sections
cited by changed R5 claims; R6 changed none of those claims' citations. **Carried, not
re-verified:** every CPython, kernel, libc and systemd statement, all of which are proposed,
version-bound obligations (§7.5a.8). No host, retained-evidence path, secret-bearing path,
credential, player datum or network resource was touched, and no recursive search was rooted at
the repository, a workspace root, home, `/opt`, `/var`, `/tmp` or `/`.

**R7 reading (this assignment) Δ7.** *Read completely:* `.agents/AGENTS.md` (700 lines); the R7
prompt (236 lines) and its authority (37 lines); `docs/review/Handover information` (213 lines);
the R6 handback (326 lines); `docs/project-management/status.md` (204 lines); and the restriction
banner of `docs/operations/disposable-test-server.md` (lines 1 … 125). The **complete R6 proposal** (4,200
lines) was read in passes, section by section (§0, §1, §2, §3, §4, §5, §6, §7 including §7.9 and the
whole of §7.12, §8, §9 … §12, §13, §14 and Appendices A, B, C and D). The R7 proposal began as a
byte-identical copy of the R6 proposal, and the R7-versus-R6 differences are listed in §0.9.
*Read by section:* `docs/implementation-plan.md`: the reading map (lines 19 … 51), §0.1 … 0.5
(53 … 183), §14.1 … 14.3 (2216 … 2250), §16 in full (2394 … 2490), §17 (2492 … 2511) and §20 in
full (2558 to the end). *Read at the exact text named:* the R5 proposal's boundary of a reap
attempt (§7.5a.6c, lines 2035 … 2084 of that file: phases RA-0 … RA-4, RB-1 … RB-5, with its open
RB-5) and NT-WB-5a, NT-WB-5b and NT-IS-16 (lines 2654, 2655 and 2678), to confirm that the
remediation does not regress R5-F1 or R5-F2: R7 changes no phase, no RB rule apart from the
record that RB-2 already describes, and no case clock; the R4 proposal's table SN-R, table SN-S
and WB-1 … WB-7 (lines 1749 … 1853 of that file) and the opening and rules IS-1 … IS-7 of its
IM-S (lines 2085 … 2185), to confirm that the remediation does not regress R4-F1 or R4-F2
(R4's S0 precedes S1 for every handle, which CC-31 narrows to a `running` handle; no R4 wait,
cap or send rule changes); and the R3 proposal's signal-sending contract (lines 1412 … 1500 and
1552 … 1600 of that file: the class statement, CH, SI-1 … SI-4, SN-1, table SN-R, table SN-S and
table SN-RO), to confirm that the remediation does not regress R3-F1 (R3's SI-2 already says that
validation is a detector and not a substitute; SI-5 adds the consequence of a violated SI-3). The
operational draft `phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`: a fixed-string
search for `grace_deadline`, `children` and `children-unknown` (no match: the draft carries no
record field of this proposal) and its §11.2, §11.3 and the opening of §14 (lines 1344 … 1362 and
1459 … 1478), as the consumers of B-08 and B-13, **without editing it**; its SHA-256 was recorded
before the first edit. **Not re-read in R7:** the R1 … R5 prompts, authorities, proposals and
handbacks beyond the R3, R4 and R5 text named above (their unchanged state is checked by
digest); the accepted OH-S2 R2 citation record and the one-host design: **no R7 claim cites a
section of either, so none was searched**, and every `[R2 §n]` and `[D §n]` citation of R6 is
**carried, not re-verified**. **Carried, not re-verified:** every CPython, kernel, libc and
systemd statement, all of which are proposed, version-bound obligations (§7.5a.8). No host,
retained-evidence path, secret-bearing path, credential, player datum or network resource was
touched, and no recursive search was rooted at the repository, a workspace root, home, `/opt`,
`/var`, `/tmp` or `/`.

### 1.2 Method

1. Re-derive, from the accepted text, **which claim rests on which mechanism**
   (§2). Repair only where a refuted premise is load-bearing.
2. For every elapsed-time statement, ask who enforces it. If the answer is "the
   arithmetic of a parameter", the statement is withdrawn (§7.7).
3. Where a repair needs a host fact R2 did not establish, write it as a new
   **proposed** obligation. Never as a fact.
4. Give every wait, retry and poll a **finite, fail-closed** bound whose expiry
   has a defined consequence, **and say what is being bounded**: the helper's
   waiting, not the work of the kernel or of a child.
5. For Route 3, apply the accepted definition literally. Compare scope-change
   alternatives against it, never as a substitute for it.

### 1.3 Fact classes used in this proposal

| Tag | Meaning |
|---|---|
| **[R2 §n]** | an accepted source or verdict in the accepted R2 record, section `n` |
| **[D §n]** | accepted inactive design text (one-host amendment through D3-R6), section `n` |
| **[R3 §n]**, **[DR1 §n]** | accepted R3 or DR1 text, section `n` |
| **[C11]**, **[D2]** | accepted launcher contract or static-launcher design |
| **[R1 §n]** | the unaccepted, unchanged R1 proposal, cited only to say what was withdrawn or renamed |
| **[N]** | **new, proposed**: a design statement or proof obligation introduced here. It is not a fact. It needs citation, test or observation under its own gate |
| **[P]** | a **parameter** whose value Peter chooses |
| **E, M, C, X** | deadline classes of §7.2 |
| **SN**, **SI**, **CH**, **PO-SN**, **CC**, **S0 … S6** | **R3, proposed**: the signal-sending operation, the identity rules, the child handle, the proof obligations of §7.5a and the consistency corrections of §0.5. Each is class **[N]**; the steps S0 … S6 are those of table SN-S |
| **WB**, **IS**, **CS**, **T0 … T7**, **CC-8 … 15**, **INV-22, 23**, **NT-WB**, **NT-IS** **Δ4** | **R4, proposed**: the wait-budget rules WB-1 … WB-7 (§7.5a.6a), the interruption rules IS-1 … IS-8 and the child-state set CS-1 … CS-8 (§7.9), the interruption points T0 … T7, the consistency corrections of §0.6, the two invariants and the two test groups. Each is class **[N]** |
| **RB**, **RA-0 … RA-4**, **T3k**, **T5k**, **IS-9**, **CC-16 … 22**, **W-15**, **NT-WB-5a, 5b**, **NT-IS-16, 17**, **Q18, Q19** **Δ5** | **R5, proposed**: the reap-attempt boundary rules RB-1 … RB-5 and phases RA-0 … RA-4 (§7.5a.6c), the two added interruption points, the observer rule, the consistency corrections of §0.7, the withdrawn claim W-15, the split slow-validation cases, the two added interruption cases and two review questions. Each is class **[N]** |
| **RE-1 … RE-6**, **`reap-unknown` (RU)**, **RA-E**, **T3x**, **T5x**, **S1-a**, **S1-b**, **S7**, **S8**, **CS-9**, **CS-10**, **IS-10**, **CC-23 … 30**, **W-16**, **INV-24, 25**, **NT-RE-1 … 12**, **NT-NS-1 … 8**, **PO-SN (c′)**, **Q20, Q21**, **SR-14** **Δ6** | **R6, proposed**: the reap-error rules (§7.5a.6d), the fourth handle state, the added phase and points, the two branches of S1 and the two added steps of table SN-S, the two added child states, the interruption rule IS-10, the consistency corrections of §0.8, the withdrawn claim W-16, two invariants, the twenty paper-only cases, the evidence-only obligation (c′) and the added review and security items. Each is class **[N]** |
| **GD-1 … GD-5**, **`s0_ran`**, **SI-5**, **CC-31 … 34**, **W-17, W-18**, **INV-26, 27**, **NT-GD-1 … 4**, **Q22 … Q24**, **SR-15** **Δ7** | **R7, proposed**: the grace-deadline rules and the record boolean (§7.5a.6e), the consequence of a violated sole-reaper invariant (§7.5a.3), the consistency corrections of §0.9, the two withdrawn claims, two invariants, four paper-only cases and the added review and security items. Each is class **[N]** |

**Naming in R7 (Δ7).** "R7-F1", "R7-F2" and "R7-F3" are findings of the same review series, returned on the OH-S3 R6 proposal. The OH-S3 R2 … R6 proposals are always called by those names.

**Naming in R6.** In this document **[R2 §n]** still means the accepted **OH-S2 R2
citation record**, and "R2-F1", "R2-F2", "R3-F1", "R4-F1", "R4-F2", "R5-F1", "R5-F2", "R6-F1"
and "R6-F2" are findings of the OH-S3 review series. The OH-S3 R2, R3, R4 and R5 proposals are
always called by those names.

Identifiers introduced here (LD, GR, GRR, GI, RL, IGR, IL, RO, SD, BSP, SG, IM, RH,
LR, WP, BQ, BC, DEC, G-, N1 … N4, and, in R3, SN, SI, CH, PO-SN, CC, INV-19 … 21,
RO-7, NT-SN, and, in R4, WB, IS, CS, INV-22 … 23, NT-WB, NT-IS, and, in R5, RB, RA, T3k,
T5k, IS-9, W-15, NT-IS-16 … 17, and, in R6, RE, RU, RA-E, T3x, T5x, S7, S8, CS-9 … 10, IS-10,
W-16, INV-24 … 25, NT-RE, NT-NS, and, in R7, GD, `s0_ran`, SI-5, CC-31 … 34, W-17 … 18, INV-26 … 27, NT-GD) are
**proposal-local** until accepted. They do not
reuse any accepted identifier except where a primed form (PO-20 (f′)) restates an
accepted one. Identifiers that R1 introduced and that survive keep their R1 name
and meaning unless §7.7 or §9 says otherwise. R1's `RT3-A` is renamed `SSW`;
R1's `RT3-B` is renamed `SCDC`; R1's `RT3-Z` is renamed `ACCEPT-X1` (§9.4).

---
## 2. The safety kernel: what the accepted claims rest on

The four items R2 refuted or left uncited are all in machinery that surrounds the grant boundary, and R2-F2 concerns the elapsed time of that machinery.
Before changing anything, this section re-reads the accepted proofs and records
exactly which mechanism each safety claim cites. That reading is the licence for
every repair below. **Codex is asked to confirm it** (§14, question 1).

### 2.1 Claims, and what each rests on

| Claim | Accepted source | Rests on | Does **not** rest on |
|---|---|---|---|
| **G1.** No live grant at any instant from the `execve` of `ExecStart=` onward | [D §4.2.5-R4 (i)] | CQ-3's removal of the A1-intact rule, journaled `removed` (SB-3's token); CQ-5's PK *not authorized*; `ExecStart=` runs only after every `ExecStartPre=` exits `0` [R2 §8 (o)]; polkit authorizes `StartUnit` once [R2 §8 (p)]; `ACT` links the rule once (AM-2) | the lock, HL, `ExecStopPost=`, the backstop, any polling bound, any elapsed time |
| **G2.** One start attempt per activation (contract OSA over 𝒜) | [D §4.2.5-R5 (f), R6 (e)] | SB-1 (the claim: `mkdirat` fails `EEXIST`); SB-2 (PID 1's inactive-entry record, τ); SB-3 (one removal token); attempts never overlap [R2 §8 (t)]; end states [R2 §8 (u)] | the lock, HL, `ExecStopPost=`, the backstop |
| **G3.** The grant is created once, only after A-2 and after the holder's baseline | [D §4.2.5-R2 (d), R5 (c)] | A-2's pins; AM-0 … AM-2 order; AP-0's absence conditions; one identifier and one unit name [R2 §8 (m)] | the lock |
| **G4.** No grant survives a kernel boot | [D §4.2.5-R2 (a) M-B] | the rule and `pass-a.json` live only on `/run` (tmpfs, cleared at every boot, [R2 §7 (g)]) | everything else |
| **G5.** A failed start is never recorded as a pass | [D §4.2.5-R5 (f) proof of 4] | a pass is claimed only from a consume journal with `consumed` plus a capture root | everything else |

I re-read §4.2.5-R4 (i) items 1 … 7, §4.2.5-R5 (f) Lemmas 1 … 3 and the proofs of
OSA 1 … 4, and §4.2.5-R6 (c) … (e). **No step in any of them cites lock
exclusivity, HL's timing, the stop-post trigger, the backstop, a Polkit
latency or any elapsed time.** The only items that cite the lock are OS-5 and CX-1, both of which
the accepted text itself classes as **lifetime**, not grant, properties
([D §4.2.5-R5 (k)]: "a lifetime defect, not a grant defect").

### 2.2 Machinery that is hygiene or liveness

| Device | What it buys | What its failure costs |
|---|---|---|
| the activation lock (`flock`) | ordering of lifetime decisions (OS-5); clean, non-interleaved evidence | a refused start, a delayed HL end, a degraded (unordered) cleanup record |
| the hold loop HL and the lease L | bounds the activation's lifetime, by PID 1's `RuntimeMaxSec=` (class M, §7.2); ends it after a failed start or a pass | an activation that lasts until L, then ends by `RuntimeMaxSec=` |
| `ExecStopPost=` and the backstop | remove `pass-a.json`, tree directories and a *pre-pass* rule, and write the records | a pre-pass rule that stays live but **inert** (§5.4) until another rung acts or the host boots or the host boots |
| Polkit waits (PK) | evidence that the grant is absent, and the positive control that makes that evidence meaningful | a refused start or a failed `ACT` (fail closed) |

### 2.3 Consequence

Every repair in §§4 … 7 is allowed to **fail closed to "no pass"**. None may
weaken G1 … G5, and none may add an elapsed-time claim whose enforcer is not
named (§7). Where a repair adds a step to a safety path (BSP at the
baseline, PK/2 in CQ-5) it only **narrows** what can succeed. The safety kernel's
procedures (CQ-0 … CQ-7, SB-1 … SB-3, the claim, the rule and unit bytes) are
unchanged except for the textual amendments of Appendix A, each of which is a
fail-closed refinement.

### 2.4 What the safety kernel does depend on: the executable boundary

G1 … G5 are claims about procedures **as designed**. That the procedures execute
as designed, as root processes, depends on what starts them and what they inherit.
The accepted design assumed that `python -I -S` started under PID 1's open block is
such a start. [R2 §10.4, §15.4 (X-1)] refuted that for CPython 3.14.4, and the
accepted disposition returns the question to **Route 3 design review** (§9). The
helper-start contract RH-1 … RH-3 (§9.2) states what any chosen boundary must
deliver. Until Route 3 is established, **X-1 stays open for the root roles**, and G1 … G5
are conditional on RH. This is not new: it is the accepted disposition, restated so
that no reader takes the repaired activation design to have closed it. Under
OH-D-6, `ubuntu` already has unrestricted `sudo`, so an ambient input that only root
or a Polkit-authorized actor can set is a consistency limit and not a privilege
escalation. That reasoning makes RH a *consistency* requirement. It does not make a
dynamic input stop being an input (§9.9).

---

## 3. Vocabulary used by the repairs

| Term | Meaning |
|---|---|
| **grant object** | the rule file `/run/polkit-1/rules.d/50-freedom-blades-rp11.rules` together with polkitd's loaded copy of it |
| **G0 … G4** | grant-object states. **G0** never linked, or cleared by a boot. **G1** linked: the file is present and A1-intact. **G2** unlinked, unconfirmed: the file is absent, but polkitd's loaded copy may still authorize until it reloads. This proposal claims **nothing** about how long that lasts. **G3** verified absent: the file is absent and a PK/2 *not authorized* was observed after the unlink in this activation. **G4** unremovable: the file is present and `unlinkat` fails |
| **holder (H)** | the PID-1-supervised transient service whose main process runs the `hold` role (AP-2) |
| **CP** | the capture unit's `ExecStartPre=+` consume step (CQ-0 … CQ-7) |
| **CL** | cleanup, in every trigger (`stop-post`, `backstop`, `attest`), including GP-R3 |
| **GRR** | the **grant-release routine** (§5.7): one tmpfs-only, lockless, spawn-free routine that removes an A1-intact rule through a descriptor re-verification. Used by IGR, by CL's first act (CL-G) and nowhere else. CP's CQ-3 keeps its accepted order and write-ahead form |
| **IGR** | *inline grant release*: the holder's own call of GRR on every catchable end (§5.7) |
| **K** | the root-only lock directory `/run/freedom-blades-rp11-lock-⟨activation_id⟩/` (LD-1) |
| **GI-1, `grant.id`** | the root-only identity object inside K that lets a rung find the rule's identity without reading an `ubuntu`-owned `ext4` journal (§4.5, DEC-3) |
| **BS** | the backstop procedure and its timer |
| **executor (X), operator (O)** | the actor working under A-2 on `oracle-test`; the `ubuntu` client that issues the one `start` |
| **spawn** | creation of any child process by a root helper, always through the single function `spawn()` (§7.5) |
| **owner (of a lock)** | the single process that opened the open file description the lock is attached to |
| **lock mode** | `held`, `degraded` (acquisition deadline reached, cleanup proceeded unordered) or `absent` (the lock object could not be opened) |
| **𝒜** | the authorized path set of [D §4.2.5-R6 (d)], unchanged |
| **deadline classes** | **E** a monotonic deadline enforced by the helper on its own waiting; **M** a timer enforced by PID 1 that delivers signals at stated offsets; **C** a count bound; **X** expected to be quick, not bounded (§7.2) |
| **abandon** **Δ3** **Δ4** | stop waiting for a child after the SN sequence (§7.5a.6), once the **final reap attempt** (WB-5) begun at or after `t_g` has found it unreaped, **stop signalling it for good** (SI-4), and record that fact. The consequence of every abandon is a fail-closed result, and it is never read as the child's absence. **Δ6:** an abandon follows only a *normal* return of the final attempt that found the child unreaped. A reap attempt that **raised** is not an abandon: it is a suppression, `reap-unknown` (RE-1) |
| **wait budget** **Δ4** | the total of a helper's **scheduled sleeps** in one wait or one SN sequence: at most c for a child wait, and at most g for the reaping of a signalled child (WB-6). It counts sleeps only. It is **not** the elapsed time of the procedure and bounds no class-X operation |
| **reap attempt** **Δ4** **Δ5** | exactly one non-blocking `reap_step()` (SI-3). Class **X**, never a wait, never given a timeout argument or a retry loop (WB-5). **Δ5:** its interior has five phases RA-0 … RA-4 (§7.5a.6c); the kernel reaps the direct child inside it, at the boundary between RA-1 and RA-2. **Δ6:** an attempt has one of three results, *reaped*, *unreaped* or *raised*; a raised attempt adds the phase RA-E and ends in S8 (§7.5a.6d) |
| **kernel reap** **Δ5** | the consumption of the direct child's exit status by this helper's own `waitpid` inside a reap attempt. After it the kernel no longer holds the child (its PID and group number are no longer pinned by it). It is **not** the same as the handle's `state = reaped` (RA-3), and it is **not** a durable record (RA-4); the three differ by the phases RA-2 … RA-4 |
| **late** **Δ4** | said of a send, validation or reap attempt that returned at or after `t_g`. A recorded observation, not a failure and not a bound |
| **CS-1 … CS-10** **Δ4** **Δ5** **Δ6** | the common child-state set of §7.9: what a child's state can be after the helper that owns it ends, given the sends that helper had attempted, **whether the kernel had reaped the direct child**, and the record that survived. A member is **not** a function of any send result. **Δ5:** CS-5 and CS-7 are the states in which the kernel has reaped the direct child. **Δ6:** CS-9 and CS-10 are the states in which the helper does not know whether it has (`reap-unknown`) |
| **T0 … T7** **Δ4** **Δ5** | the interruption points of the SN sequence (§7.9, table IM-S); they replace R3's T0 … T5. **Δ5:** T3 and T5 mean "not yet reaped by the kernel"; **T3k** and **T5k** are the phase RA-2 inside S3 and S5; T6 begins at the handle-state update or the abandon decision (RB-4). **Δ6:** **T3x** and **T5x** are the phase RA-E inside S3 and S5; T0 and T1 exist only for a handle that is still `running`; a handle already settled when SN is entered is at T6 or T7 (CC-23); T6 also begins at the suppression decision of S8 |
| **reap-unknown (RU)** **Δ6** | the fourth state of a child handle: the helper's reap attempt **raised**, so it does not know whether the direct child is still unreaped, or was reaped in the kernel with no handle update. It is **not** labelled *reaped*, *unreaped* or *abandoned* as a fact. It never changes back, it is never signalled (RE-1), and nothing in the design reads it as either truth (RE-2) |
| **RE-1 … RE-6** **Δ6** | the reap-error rules of §7.5a.6d: fail closed after any `reap-error`; the state RU; the handle kept; no new wait or grace; the record and the unchanged fail-closed result; the evidence-only status of the CPython question |
| **S1-a, S1-b, S7, S8** **Δ6** | the steps of table SN-S added or split in R6 (§7.5a.6): S1-a (a settled handle: no call, no wait, to S7), S1-b (an identity rejection: no send, to S5), S7 (settle, record, return) and S8 (suppress after a `reap-error`) |
| **s0_ran, GD-1 … GD-5** **Δ7** | the record boolean and the rules of §7.5a.6e: **`t_g` exists exactly when S0 ran**; `grace_deadline_ms` is an integer iff `s0_ran` is true and `null` otherwise; a pre-S0 `reap-error`, a child that exits within c, a child that fails to spawn and a handle that is already settled when SN is called each read no `t_g` and start no grace period |
| **SI-5** **Δ7** | the consequence of a violated sole-reaper invariant (§7.5a.3): an injected foreign reap is a deliberate violation of a design precondition, not a supported runtime state, and **the design then makes no reuse-safety claim from SN-4 alone**. SN-4 is a detector, never the reuse defence |
| **flag** | the single boolean `stop_requested` that the holder's signal handlers set and nothing else (SG-2) |
| **SN** **Δ3** | the one function through which a root helper sends a signal to a child's process group (§7.5a). Class **X** for the call, **C** for its attempts. It is **not** PID 1's delivery of signals (class **M**) |
| **child handle (CH)** **Δ3** **Δ7** | the in-memory record `spawn()` creates for each child: PID, process-group and session ID (both equal to the PID), start time where readable, state `running`, `reaped`, `abandoned` or `reap-unknown` (**Δ7:** all four; R6's row omitted the fourth, R7-F3), the sends made and the anomalies seen (§7.5a.3) |
| **unreaped** **Δ3** | a child for which this process has not yet received an exit status from `waitpid`. A zombie is unreaped. An unreaped child pins its PID number and its group's number *[N, PO-SN (b)]* |
| **RH-1 … RH-3** | the helper-start contract any Route 3 outcome must discharge for each root procedure (§9.2) |
| **R3-ROOT, R3-DR1** | the two readings of the accepted Route 3 boundary (§9.1) |
| **LIT-FULL, LIT-DR1, WITHDRAW, SSW, SCDC, ACCEPT-X1** | the exact alternatives of §9.4 |

---
## 4. Repair A — PO-20 (f): lock release and descriptor ownership *(carried from R1, with R2-F2 corrections)*

### 4.1 What the accepted text says and what is true

The accepted text relies on process end as the release event in three places:

* [D §4.4.2a] PO-20 (f): *"`flock` on an `O_RDONLY` directory descriptor gives an
  exclusive advisory lock that is released when the process ends."*
* [D §4.2.5-R3 (e)]: *"The kernel releases the lock when a process dies
  (PO-20 (f)), so a killed GP-R3 attempt never blocks the next one."*
* [D §4.2.5-R4 (c)] and [D §4.2.5-R5 (g)]: *"The lock is released by the kernel at
  every exit, including a kill"* and *"…at every process exit, including a
  kill."*

**What is true** [R2 §7 (f)]: the lock is available on any descriptor with
`FMODE_READ` or `FMODE_WRITE`, directories included. It is released when the
**last reference to the open file description** is dropped (`__fput` →
`locks_remove_file`). A forked child, or any holder of a duplicate, keeps it
after the locking process ends. R2's corrected form: *"released when the last
descriptor referring to that open file description is closed, which process exit
does when no other process holds one."*

### 4.2 Lock inventory

| # | Lock | Acquirer(s) | Object | Mode | Spawns while held? | Release in the accepted text |
|---|---|---|---|---|---|---|
| L-1 | H-1 run lock (M-0) | the root tool [D §4.2.4-R1 (b)] | `/var/tmp/⟨RUN⟩-h1-evidence/` (`ubuntu`, `0700`) | `LOCK_EX\|LOCK_NB`, whole lifetime | yes | process end |
| L-2 | `ACT` chain lock, taken by the holder at AM-0 | holder | `/var/tmp/⟨activation_id⟩-act-evidence/` (`ubuntu`, `0700`) | `LOCK_EX`; kept to `hold-start` (AR-2) | yes: AK-1's `systemd-run`, baseline `systemctl show` | explicit at `hold-start`, otherwise process end |
| L-3 | CP's lock (CQ-1) | CP | the same directory | `LOCK_EX\|LOCK_NB` once | yes: CQ-4's `systemctl show`, CQ-5's PK subject and `pkcheck` | CQ-7, otherwise process end |
| L-4 | HL's decision lock (OS-5) | holder | the same directory | `LOCK_EX\|LOCK_NB` once per decision | yes: the re-observation | the holder **exits while holding it** |
| L-5 | CL's lock (CL-0) | `stop-post`, `backstop`, `attest`, GP-R3 | the same directory | retry `LOCK_NB` every second for at most S seconds | yes: PK, `systemctl show` | process end |

### 4.3 Defects

* **D-LK-1, inheritance is not specified.** Every holder in the table spawns
  children while it holds. A child created by `fork` holds a duplicate of every
  inherited descriptor from creation until it `exec`s a `CLOEXEC` descriptor
  away, closes it, or exits. PK's subject process is the accepted example
  ([D §4.2.5-R1 (f)]): it is forked, changes credentials and then executes
  `sleep 60`. If the owner is killed while such a child is stopped, slow or
  failing to `exec`, the lock outlives the owner. The accepted text never says
  how descriptors are kept out of children.
* **D-LK-2, the lock object is not root-only.** `ubuntu` owns the evidence
  directory (`0700`). It can open it and take `flock` for as long as it likes.
  Then CP gets `consume-busy`, HL never ends, and CL stops with `lock-timeout`
  and "acts on nothing" ([D §4.2.5-R2 (h) CL-0]), so a pre-pass rule can stay
  live until L or the boot. Under OH-D-6 `ubuntu` can do more than that on
  purpose. But the same reachability exists *by accident*, for example any
  `ubuntu` tool that opens the directory and locks it, and the design's claim is
  that cleanup does not wait for anybody.
* **D-LK-3, the wait equals the stop timeout.** CL waits up to S seconds for the
  lock, and S is the holder's `TimeoutStopSec=`, which bounds CL itself
  ([R2 §8 (e)]). At S systemd sends `SIGTERM` to CL. CL is terminated at the
  instant its own wait would expire and never reaches `lock-timeout`.
* **D-LK-4, exit while holding.** OS-5 has HL exit "while holding the lock", so
  the design's release event is process end, which is the refuted premise. It
  buys nothing: `hold-end` is durable before exit and CQ-4 refuses on it.
* **D-LK-5, `lock-timeout` is the opposite of grant priority.** "Acts on
  nothing" leaves a removable rule in place because of a contended
  *coordination* object.

### 4.4 The corrected obligation, PO-20 (f′) *(proposed [N], text for [D §4.4.2a])*

For the HF-04 kernel series and the HF-07 `libc6` and CPython versions:

* **(f′-1)** [R2 §7 (f), established] a `flock` lock on a directory descriptor
  is attached to the open file description and is released when the last
  reference to that description is closed.
* **(f′-2)** *[N]* a descriptor opened with `O_CLOEXEC` is closed in the new
  image by `execve` and so is not inherited across it; `close_range(3, ~0, 0)`
  closes every descriptor from 3 upward ([D2 §5.7 S-4]).
* **(f′-3)** *[N]* a child created by `fork`, `vfork`, `clone` without
  `CLONE_FILES`, `posix_spawn` or CPython's `subprocess` holds a duplicate
  reference to every inherited open file description from creation until it
  closes the descriptor, `exec`s it away (`CLOEXEC`) or exits. With
  `close_fds=True` and no `pass_fds`, CPython's child closes all descriptors
  ≥ 3 before `exec`.
* **(f′-4)** *[N]* the only ways a second process obtains a reference to an
  existing open file description are inheritance, descriptor passing over a Unix
  socket, and `pidfd_getfd`. Re-opening `/proc/⟨pid⟩/fd/⟨n⟩` creates a **new**
  description and shares no lock.
* **(f′-5)** *[N]* an unprivileged process cannot open an object that is a
  directory owned by root with mode `0700`, and so cannot lock it.

(f′-1) is established. (f′-2) … (f′-5) are kernel and CPython behaviours that no
accepted record cites. They join the OH-S2 citation step (§11, slice OH-S2b).
**AP-0 is INVALID RUN unless each is accepted for the observed versions, and no
lock object is created.** The statement "released when the process ends" is
withdrawn everywhere; wherever the accepted text depends on it, LD-8 below says
what happens instead.

### 4.5 Design: lock discipline LD-1 … LD-9 *(proposed)*

* **LD-1, root-only lock object K.** The `ACT` chain lock object is the
  directory `K = /run/freedom-blades-rp11-lock-⟨activation_id⟩/`, `root:root`,
  mode `0700`, empty at creation (it receives only `grant.id`, GI-1), with no `system.posix_acl_*` or capability extended
  attribute. The holder creates it at AM-0 with an exclusive `mkdirat` on a
  descriptor of `/run` (which never follows a final symbolic link and fails
  `EEXIST` for any existing name [R2 §7 (h)]), opens it, verifies type, owner,
  mode and `st_nlink`, and journals its `(dev, ino)` in `run-start`. AP-0
  requires K absent. K lies under `/run`, whose parent conditions already require
  a root-owned tmpfs directory without group or other write. K is cleared by
  every kernel boot (M-B). CL-5b removes `grant.id` and then K, through a descriptor re-verification
  against the journaled identity and only if K holds nothing else, together with the other
  `/run` objects; a K left by a crash between its creation and the journal is
  class **S0** (reported, kept, cleared at the boot), exactly like the other
  run-unique `/run` leftovers of [D §4.2.5-R2 (h) CL-5b]. Nobody but root can open
  K, so no unprivileged process can hold the lock (f′-5).
* **GI-1, the grant identity object (proposed [N]; DEC-3).** Immediately before
  the rule is linked (AM-2's PF-6), and after the staged rule's identity is known,
  the holder creates `K/grant.id` (`root:root`, `0600`, `O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC`,
  then `fchmod`) holding one canonical line: `{path, dev, ino, sha256, size, mode,
  uid, gid, boot_id}` of the staged rule that PF-6 will link. K lies on tmpfs, so
  writing it involves no `ext4`. A rung that must remove the rule (IGR, CL-G, the
  backstop, `attest`) reads its identity from `grant.id`, **not** from the
  `ubuntu`-owned evidence directory's journal. The journal's `file-identity` line
  stays the durable evidence, and a disagreement between the two is recorded as
  `identity-conflict` and acted on by `grant.id`, because removing the name whose
  identity the holder itself wrote is never wrong. This closes two things R1
  flagged and could not close: a replaced `ubuntu`-owned journal can no longer
  make CL class the rule A0 and leave it; and the removal path no longer reads
  `ext4` before the `unlinkat` (GR-2, §5.7). **Without GI-1** (the alternative of
  DEC-3) CL reads the journal as accepted and RO-6 (§5.6) widens. CP's CQ-3 is
  **not** changed: it keeps the accepted order, after the claim and under the
  lock, and the accepted journal-based classification.
* **LD-2, one owner per open file description.** A lock is taken only on a
  descriptor that the acquiring process itself opened for that purpose:
  `open(K, O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC)`. It is never duplicated
  (`dup*`, `fcntl(F_DUPFD*)`), never passed over a socket, never handed to
  another thread, and never stored in an object that outlives the acquisition.
  One acquisition is one description and one owner.
* **LD-3, inheritance prevention.** (a) Every `open` carries `O_CLOEXEC`
  explicitly. The test asserts the flag and does not rely on a language default.
  (b) A process holds a lock only while it is single-threaded. (c) **No raw
  `fork` in any root helper.** Every child is created by one function
  `spawn()` (HS-1, §7.5), which uses only a creation primitive that closes every
  descriptor ≥ 3 before `exec` and passes none (`close_fds=True`,
  `pass_fds=()`). (d) The helper-start contract RH-2 (§9.2) requires every
  descriptor ≥ 3 to be closed before the helper's first state operation. Which
  mechanism discharges RH-2 depends on the Route 3 outcome (§9). **The discipline
  here does not rely on it**: (a) … (c) and (e) alone keep K's descriptor out of
  children, and K does not exist until after RH-2 is discharged (AM-0). (e) A child's duplicate reference therefore exists only between
  its creation and its own `exec` or `_exit`. This is the only window, and it is
  not widened by any step of the design (f′-3).
* **LD-4, explicit close points, and no process designed to end holding a
  lock.** A lock is closed as the first act after the last operation it
  protects (table 4.6). Process exit is the last-resort release and is **never**
  the design. OS-5's "exits while holding the lock" is replaced by: *HL appends
  and `fsync`s `hold-end`, closes K, then exits*. CQ-4 refuses on `hold-end`, so
  the earlier release leaves no gap.
* **LD-5, bounded acquisition.** Every acquisition is `LOCK_EX|LOCK_NB`. A wait
  is a loop of non-blocking attempts bounded by a **monotonic deadline**
  `lock_wait_ms` (λ) [P] (§7.6: range 1,000 … 10,000, recommended 5,000), never by
  a count of sleeps. The deadline bounds **this loop's waiting** (class E, §7.2).
  It is **not** a bound on CL's elapsed time: nothing in this document derives one
  from λ (§7.7). CP does not wait: one attempt, as accepted (AR-1). `EINTR`
  retries within the deadline. Any other error is "cannot acquire".
* **LD-6, grant removal never waits for the lock (GR-1).** CL-G (§5.7), IGR and
  GP-R3's rule step do not require the lock, and CL-G runs **before** CL's first
  lock attempt. If CL cannot acquire K within
  `lock_wait_ms`, or cannot open K, it continues in **degraded mode**: it
  records `lock_mode: "degraded"` or `"absent"` and performs CL-1 … CL-7 as it
  would holding the lock, except that it is not ordered against CP. This is safe
  because the rule's removal is one descriptor-re-verified `unlinkat` of one
  A1-intact object that CP's CQ-3 also performs (the later actor gets `ENOENT`),
  and because G1 and G2 do not depend on the lock (§2). `lock-timeout` as an
  outcome that acts on nothing is **withdrawn**.
* **LD-7, no lock on an object a non-root actor can open.** It applies to K and
  to any later lock that serializes an act of the activation chain. H-1's run
  lock (L-1) and any lock of the same M-0 pattern may stay on their
  `ubuntu`-owned evidence directories, because holding one can only stop *that
  run* before any mutation and nothing is cleaned up through it. They obey LD-2
  … LD-5, and each journal records its lock object and mode.
* **LD-8, failure behavior.** Table 4.7.
* **LD-9, the holder of a lock is never hunted.** No procedure scans for,
  signals, ptraces or kills a lock holder, and no decision reads `/proc/locks`.
  A retained lock is handled only by LD-8. **Δ3** The only processes a root helper
  ever signals are its **own unreaped children**, only through SN (§7.5a), and an
  abandoned child is never signalled again (SN-9).

### 4.6 Close points

| Procedure | Opens K | Acquires | Closes K | Exit while holding? |
|---|---|---|---|---|
| holder AM-0 | after the exclusive `mkdirat` of K | `LOCK_EX\|LOCK_NB`. `EWOULDBLOCK` is impossible for a fresh K and is HARD STOP `lock-object` | immediately after `hold-start` is durable (AR-2, unchanged) | no. A failure before that point closes in `finally` |
| holder AK-1, baseline reads | — | — | — | children are created by `spawn()` while the lock is held (LD-3) |
| HL decision (OS-5) | per decision, derived from `activation_id` | `LOCK_EX\|LOCK_NB`, once | after `hold-end` is durable and before the exit, or immediately if no terminal reason holds | no (**amended**) |
| CP | CQ-1, derived from `pass-a.json`'s `activation_id` (CQ-0) | `LOCK_EX\|LOCK_NB`, once (AR-1) | after CQ-7's `run-end`; on every failure path before the non-zero exit | no |
| CL (`stop-post`, `backstop`, `attest`) | CL-0 | `LOCK_NB` attempts until the `lock_wait_ms` deadline, then degraded | after CL-7's `run-end` | no |
| IGR | none | none | — | — |

### 4.7 Failure behavior (LD-8)

| Condition | CP | HL | CL, BS, `attest` | holder AM-0 | Effect on the grant and on a pass |
|---|---|---|---|---|---|
| K absent, not a directory, wrong owner or mode, unopenable | `consume-unidentified`: nothing created, SB-2 covers | `observation-failed`: the activation ends | `lock_mode: "absent"`, degraded | HARD STOP `lock-object` before AM-1; nothing is linked | no pass; the rule is removed by IGR, CL-G or CQ-3 |
| `EWOULDBLOCK` | `consume-busy` (no pass) | observes again after Δ | retries to the deadline, then degraded | n/a | no pass; removal unaffected (GR-1) |
| other `flock` error | as "cannot acquire": `consume-busy` | as `EWOULDBLOCK` | as the deadline expiring | HARD STOP `lock-object` | as above |
| the lock is retained for a long time, by a root act or by a bug | CP never passes | waits until L, then the holder ends and IGR runs | degraded, every time | n/a | **no grant outlives the first rung of RL that can act** (§5); no start passes |
| the owner dies while a child holds a duplicate | as `EWOULDBLOCK` for everyone else | as above | as above | n/a | LD-3 admits this only inside the spawn window; no design path keeps it |

### 4.8 What the lock still protects, and what degraded mode costs

The lock still orders lifetime decisions (OS-5: after HL's durable `hold-end`
every CP refuses) and keeps cleanup records from interleaving with a running CP.
Degraded mode costs one thing: a CL record may not be ordered against a CP that
is mid-flight. Then the accepted outcome applies, a pass running without a grant
while CL ends HARD STOP `unit-still-active` ([D §4.2.5-R5 (k)], CX-1). The
`deact` record states `lock_mode`, so the reviewer sees the basis. Neither G1
nor G2 changes.

### 4.9 Evidence

`rp11-activation-record/2`, as amended in §8.5, gains `lock: {object: {path,
dev, ino} or "absent", mode: "held"|"degraded"|"absent", wait_ms}`. The consume and CL attempt
journals' `run-start` lines carry the same three values.

### 4.10 Negative tests *(proposed, for OH-S4; none run here)*

| ID | Case | Asserts |
|---|---|---|
| NT-LD-1 | a lock owner spawns each helper child (`systemctl`, `systemd-run`, `pkcheck`, the PK subject) while holding K | after `spawn()` returns and after each child's `exec`, **no child holds a descriptor on K's inode** (checked through the child's descriptor table in the harness) |
| NT-LD-2 | the owner is killed while a deliberately stopped fake child holds a duplicate | the second acquirer sees `EWOULDBLOCK` (the hazard exists in the model), and the same scenario cannot be produced through `spawn()` |
| NT-LD-3 | code scan over every root helper | no `os.fork`, no `os.dup*`, no `fcntl` `F_DUPFD*`, no `SCM_RIGHTS`, every `os.open` carries `O_CLOEXEC`, every lock acquisition has a matching `close` on every path including exceptions |
| NT-LD-4 | K's creation and mode | K is `root:root`, `0700`, empty at creation, no forbidden extended attribute; a non-root actor in the harness cannot open it |
| NT-LD-5 | `ubuntu`-style retention of the old `ubuntu`-owned directory lock | has **no effect** on CP, HL or CL once the lock object is K |
| NT-LD-6 | CL against a lock retained forever | CL-G removes an A1-intact rule **without having attempted the lock**; CL then reaches `lock_mode: "degraded"` when the λ deadline is reached, and continues. The test asserts the order (removal, then lock attempt) and that no elapsed-time statement is made about CL |
| NT-LD-7 | the sizing rules of §7.6 | AP-0 refuses any parameter set that violates N1 … N4, **and** a code and text scan asserts that no document, record or log line states the result as a bound on CL, CP or IGR |
| NT-LD-8 | HL's decision | `hold-end` is durable and K is closed before the process exits; a CP that acquires K in between refuses at CQ-4 |
| NT-LD-9 | PK subject | the subject child holds no lock descriptor, runs under the credentials in the H-1 record, and receives an SN-3 send after each call (it is reaped by the final attempt, otherwise abandoned and recorded; the send is never read as its end) **Δ3** **Δ4** |
| NT-LD-10 | GI-1 | `grant.id` exists, is `root:root` `0600` and equals the staged rule's identity **before** PF-6; with the `ubuntu`-owned journal replaced or unreadable, CL-G still removes the A1-intact rule; a disagreement between `grant.id` and the journal is `identity-conflict` and the rule is removed by `grant.id`; a `grant.id` that names an object that is not at the rule path removes nothing |

---

## 5. Repair B — PO-21 (c): `ExecStopPost=` is a rung, not a guarantee *(carried from R1, with R2-F2 corrections)*

### 5.1 What the accepted text says and what is true

[D §4.4.2b] PO-21 (c): *"`ExecStopPost=` runs … after the main process ends for
**every** cause."* [D §4.2.5-R2 (a)]: *"The service's `ExecStopPost=` runs
cleanup CL whenever its main process ends, for any cause."* [D §4.2.5-R2 (n)
item 3] and the (k) matrix's SP cells follow from it.

**What is true** [R2 §8 (c)]: for each listed cause the state machine enters
`STOP_POST` and *attempts* to spawn `ExecStopPost=`. **If spawning it fails, the
unit goes to `FINAL_SIGTERM` with result `resources` and `ExecStopPost=` never
runs.** PID 1 failure and power loss are outside any unit guarantee.

### 5.2 The authorized guarantee, restated *(proposed)*

* **G1 … G5 (§2.1) hold unconditionally within 𝒜.** None uses `ExecStopPost=`.
* **H1, a hygiene guarantee, conditional and untimed.** *After the holder's main
  process ends, the rule is unlinked by the first rung of the ladder RL (§5.3)
  that acts. No time to that rung is claimed.* R1 stated an "operational latency"
  per rung. That column is withdrawn (§7.7): the rungs are ordered, not timed.
* **Outside the guarantee (RO-1 … RO-6, §5.6).** Stated by name.

### 5.3 The recovery ladder RL-0 … RL-5

| Rung | Mechanism | Needs PID 1 to spawn something? | Covers | Terminated or limited by (class) |
|---|---|---|---|---|
| **RL-0** | **IGR**, the inline grant release in the holder (§5.7) | **no** | every *catchable* end of the holder's main process that the process reaches a flag check on | nothing: its local work is class X. PID 1's `SIGKILL` of the holder (class M, §7.4) ends the process whether or not IGR finished |
| **RL-1** | `ExecStopPost=` running CL with trigger `stop-post`; its **first act is CL-G** | yes | every end after which PID 1 can spawn it | `TimeoutStopSec=` S: `SIGTERM` at S, `SIGKILL` after a further S, then `failed` with result `timeout` [R2 §8 (e)] (class M) |
| **RL-2** | the backstop timer's service running CL (BS-4); its **first act is CL-G** | yes | a stop-post that could not be spawned, or a CL that was killed | `RuntimeMaxSec=` S_b on the service (BS-RM, §7.4, class M, **[N]**) and at most B firings (class C) |
| **RL-3** | **CP at any later start** (CQ-3 in grant-priority form), by anyone | yes (a start needs it) | the rule itself, whenever any start is attempted | the capture unit's start timeout T_s (class M) |
| **RL-4** | a kernel boot clears `/run` (M-B) | no | everything under `/run` | none: the next boot |
| **RL-5** | attestation, trigger `attest` (record only; **its first act is CL-G**, which finds nothing the boot did not already remove) | n/a | the *records* | none: interactive, under A-2 |

RL-0 and CL-G are new. RL-1, RL-2, RL-4 and RL-5 are the accepted `SP`, `BS`,
`BC` and attestation mechanisms. RL-3 is accepted behaviour (§5.4 uses it)
promoted to a named rung. **PID 1 being unable to spawn is exactly the case in
which RL-0 and RL-4 can still act and RL-1 … RL-3 may not.**

### 5.4 The inertness lemma IL

**IL.** Let X be an activation whose holder's `ActiveState` is not `active`, or
whose `ACT` journal has `hold-end`. A rule left live for X cannot produce a pass.

*Proof.* A pass is the execution of `ExecStart=` of the capture unit. PID 1
executes it only after every `ExecStartPre=` has exited `0` [R2 §8 (o)]. CP
exits `0` only at CQ-7. CQ-7 follows CQ-4, whose OS-4 requires the holder
`active` with the `ACT` journal's invocation and whose check requires no
`hold-end`. Both are false, so CP exits non-zero at CQ-4 after CQ-3 has removed
the rule if it could. If PID 1 cannot spawn CP, or CP's image cannot be
executed, no `ExecStartPre=` exits `0`, so `ExecStart=` is never executed
([R2 §8 (c)]: start-pre spawn failures end the start; [R2 §8 (o)]). ∎

**IL′ (the window is ended by PID 1, not by a helper).** The holder's
`RuntimeMaxSec=` L is a class-M timer on `CLOCK_MONOTONIC` that starts at the
holder's `ActiveEnterTimestampMonotonic` [R2 §8 (d)]. When it fires, PID 1 sends
`SIGTERM`, and the holder's `ActiveState` leaves `active`. **From that moment IL
applies, whatever any helper is doing, including a holder that is wedged in
local work.** Consequently the period in which a live rule could be consumed by a
pass ends no later than L after the holder became active, and this does not
depend on IGR, CL, the backstop or any helper timing. Two limits are stated, not
hidden: `CLOCK_MONOTONIC` does not count suspended time [R2 §8 (d)], and PID 1
must be able to act (RO-3).

IL says that a rule left live after the holder has gone is a *hygiene* matter.
It is still a Polkit grant of `start` for `ubuntu` (OH-D-6 says `ubuntu` already
has unrestricted `sudo`, so it adds no privilege). It cannot produce a pass, and
OH-D-7's "after the pass" is not engaged.

### 5.5 Terminal causes of the holder's main process

*Catchable* means a signal or an orderly end that the Python process can handle
(SG-1: the set H). "IGR" means RL-0 removed an A1-intact rule before the process
exited **if the process reached a flag check or the end of its body before it
was killed**. No cell promises that it did.

| # | Cause | Catchable? | RL-0 IGR | RL-1 stop-post | RL-2 backstop | RL-3 CP | RL-4 boot | Grant afterwards |
|---|---|---|---|---|---|---|---|---|
| 1 | HL's normal end (`exit 0`) | yes | attempts | runs | if 1 cannot spawn | at a start | — | G1 → G2, then G3 by CL |
| 2 | `observation-failed` (non-zero exit) | yes | attempts | runs | as 1 | as 1 | — | as 1 |
| 3 | unhandled exception, `SystemExit` | yes | attempts (`finally`) | runs | as 1 | as 1 | — | as 1 |
| 4 | `SIGTERM` from a stop job | yes | attempts at the next flag check | runs | as 1 | as 1 | — | as 1 |
| 5 | `RuntimeMaxSec=` expiry: `SIGTERM`, then `SIGKILL` after S [R2 §8 (d), (e)] | the first yes; the second no | attempts at `SIGTERM`; **no promise before the `SIGKILL`** | runs | as 1 | as 1 | — | as 1 |
| 6 | orderly shutdown, reboot or `kexec` (EO, outside 𝒜): stop, then boot | yes | attempts | runs (PO-21 (h)) | n/a | n/a | clears | G0 after the boot |
| 7 | `SIGINT`, `SIGHUP`, `SIGQUIT`, `SIGUSR1`, `SIGUSR2`, `SIGALRM` (the set H) | yes | attempts | runs | as 1 | as 1 | — | as 1 |
| 8 | `SIGKILL` (a root act, or the escalation after S) | **no** | — | runs if PID 1 can spawn it | if 8's stop-post cannot spawn | at a start | clears | G1 live **inert** (IL) until a rung acts |
| 9 | a fatal signal in the interpreter (`SIGSEGV`, `SIGABRT`, `SIGILL`, `SIGBUS`, `SIGFPE`) or any default-terminating signal not in H | **no** | — | as 8 | as 8 | as 8 | clears | as 8 |
| 10 | kernel OOM kill | excluded by `OOMScoreAdjust=-1000` [R2 §8 (f)] | — | — | — | — | — | not applicable |
| 11 | a kill by a user-space OOM daemon | **no** (not covered by (f)) | — | as 8 | as 8 | as 8 | clears | as 8 |
| 12 | the holder never started: the first image is missing or cannot be executed | n/a | n/a | n/a | n/a | n/a | — | **no grant was ever linked**: AM-2 is the holder's act |
| 13 | PID 1 cannot spawn `ExecStopPost=` (result `resources`) [R2 §8 (c)] | any | attempts if catchable | **does not run** | runs if PID 1 can spawn it | at a start | clears | catchable: G2 then G3 by RL-2; uncatchable: live inert, RO-1 |
| 14 | EU: power loss, panic, hard reset | no | — | — | — | — | clears | G0 after the boot; attestation records it |
| 15 | PID 1 is dead or hung | n/a | attempts if catchable | no | no | no | clears | outside any unit guarantee [R2 §8 (c)]; a live rule is inert (IL) because no start can run |
| 16 | **a second termination signal while IGR runs** | yes | the handler sets the flag again and **nothing else**; GRR is not interrupted and not restarted (SG-5) | runs | as 1 | as 1 | — | as the first signal's row |
| 17 | `SIGKILL` **during** IGR | **no** | stops at the point reached (§7.9, IM-I) | as 8 | as 8 | as 8 | clears | by IGR point: G1 inert before the `unlinkat`, G2 after it |
| 18 | uninterruptible stall of the holder (a blocked kernel or filesystem call): no signal is acted on until it returns | n/a | none until the stall ends | `SIGKILL` is delivered; whether the process leaves the kernel call is the kernel's, and unit state moves on after the second S [R2 §8 (e)] | as 8 | as 8 | clears | **RO-6**; IL holds while the holder is not `active` |
| 19 | **a catchable end of the holder (rows 1 … 7) while a child of the holder is in any state of the set CS-1 … CS-10 (§7.9): its sends were made, failed, indeterminate or unmade, and it was reaped, abandoned, suppressed after a `reap-error` or never reached SN** **Δ3** **Δ4** | yes | unaffected: IGR spawns nothing and sends no signal (SG-9) | runs | as 1 | as 1 | — | as the row of the end. A flag observed in an E wait runs the SN sequence to its end before the body returns, so the children of a flag-driven end are settled (CS-5 … CS-10: reaped, abandoned or `reap-unknown`); an exception that ends the body inside an E wait leaves a child unsettled (CS-1 … CS-4), or in CS-5 when the exception falls inside a reap attempt after the kernel has reaped the direct child (RB-1, RB-2) **Δ5**, or in CS-9 when it falls after a reap attempt raised and before the handle was updated (RA-E, RE-1) **Δ6**. Neither state is a grant object, and a child that has come back from `Popen` holds no descriptor of K (SN-8 (e)). The child may remain alive in every state. PID 1's stop of the holder unit may signal what remains *[N, PO-SN (e)]*, as a class-M act that proves nothing about the child; RO-7 |
| 20 | **`SIGKILL` of the holder (row 8) at any interruption point T0 … T7 of SN, T3k, T5k, T3x and T5x included, with any send outcome** (§7.9, matrix IM-S) **Δ3** **Δ4** **Δ5** | **no** | — | as 8 | as 8 | as 8 | clears | as 8 for the grant (G1 live **inert**, IL). The child is in the state of the matrix cell: CS-1 … CS-6 or CS-9 when no `child` line is durable (CS-5 includes a direct child that the kernel reaped inside a reap attempt, T3k and T5k, **Δ5**; CS-9 is a child whose reap attempt raised, T3x, T5x, or T6 after S8, **Δ6**), CS-7, CS-8 or CS-10 when it is. The ended helper makes **no further send**, and what it had already attempted is history, not a result. The child **may remain alive**; it is reached by PID 1's cgroup cleanup of the unit *[N, PO-SN (e)]*, if PID 1 can act, or ends by itself; the boot is a later, separate event; IM-S (§7.9); RO-7 |

### 5.6 What remains outside the authorized guarantee

* **RO-1 (named).** *An uncatchable end of the holder (rows 8, 9, 11) while PID 1
  cannot spawn `ExecStopPost=` and cannot spawn the backstop's service, for as
  long as that lasts.* The rule then stays at G1 and **inert** (IL). It is
  removed by the first rung that can act: the backstop on its next firing, CP at
  any start, or the boot. No pass can run in that interval (G1, G2, IL). This is
  the one failure of RL that the authorized guarantee does not cover. It needs
  two independent faults (an uncatchable holder end and a PID 1 that cannot
  spawn) and its only effect is a *pre-pass, inert* grant of `start` for
  `ubuntu`.
* **RO-2 (common-cause).** *The helper bytes on disk are damaged or removed after
  `ACT`.* RL-1 and RL-2 then fail identically because they run the same
  installed image. RL-0 is **not** affected, since it runs inside a process that
  was already loaded. AP-0, H-2 and AM-0 verify those bytes before `ACT`, so
  after `ACT` the cause is a root act (SL-1).
* **RO-3 (PID 1).** If PID 1 is dead or hung, nothing in any unit runs. That is
  outside every unit-level guarantee in the accepted record.
* **RO-4 (IGR not completed; new in R2).** *The holder's end is catchable, but
  the process is killed (`SIGKILL` after S, or a root act) or stalls before GRR's
  `unlinkat`.* The state is G1 inert, exactly as rows 8 and 17, with the same
  rungs. R1 implied that IGR "acts within about ten seconds". That claim is
  withdrawn: IGR's local work is class X, and the design relies on the ordering of
  the rungs and on IL, not on IGR's speed.
* **RO-5 (an unbounded backstop firing; new in R2, closed by BS-RM).** In the
  accepted literal the backstop service is `--service-type=exec` with
  `--property=TimeoutStartSec=⟨S⟩`. The accepted record establishes that such a
  unit is `Type=exec` and which start timeout applies [R2 §8 (r)]. That the start
  job of a `Type=exec` service is complete once the binary has been executed, so
  that `TimeoutStartSec=` ends there, is systemd's documented behaviour and is
  **proposed for citation [N]** (OH-S2b, `service.c` start-state transitions). If
  it holds, a firing that has started has **no PID-1 bound at all**, and, because
  the timer does not re-arm while its service is active [R2 §8 (j)], a firing that
  hangs also **prevents every later firing**. The repair BS-RM (§7.4) adds
  `--property=RuntimeMaxSec=⟨S_b⟩` so that PID 1 ends each firing. Until BS-RM is
  accepted, RO-5 is a defect of the accepted design that this record reports.
* **RO-6 (a persistent stall of a filesystem or the kernel; new in R2).** Every
  rung whose work touches `ext4` can be delayed by an `ext4` stall: that is
  every rung except RL-0 and CL-G (tmpfs only, GR-2), and CL-G only with GI-1. The
  design does not claim otherwise. Nothing in it makes a stalled kernel call
  return. The rule stays inert (IL) and the next boot clears it (RL-4).

* **RO-7 (a child left behind by its helper; new in R3, widened in R4 Δ4, R5 Δ5 and R6 Δ6).** *A child
  of a root helper that SN did not signal (`identity-mismatch`, `identity-unverifiable`),
  could not signal (a failed send), signalled with a result that proves nothing (success,
  `ESRCH`), was being signalled when the helper ended (an indeterminate send), or was
  signalled without being reaped before the final reap attempt, **may be alive** after the
  helper has moved on or has ended.* **Δ5:** where the helper was ended inside a reap
  attempt after the kernel had reaped the direct child, the direct child is **not** alive and
  **no record says so** (CS-5, IS-9); the processes of its group may still be alive (IS-3). **Δ6:** where a reap attempt **raised** (`reap-unknown`, RE-1), the direct child may be alive, or may have been reaped in the kernel with its PID and group number released; **no helper sends it any signal** after the error, no record can say which truth holds (RE-2), and its owner is the owner of its enclosing procedure, as for an abandoned child.
  Whether it is alive is **not** derived from any send result (IS-5). When the helper itself decides, it abandons the child (SN-8), records it,
  and never signals it again. When the helper is ended first, it makes **no further send**
  and what it had already attempted is history (§7.9). Consequences, stated narrowly: it
  holds **no descriptor of K** (SN-8 (e)); it holds **no grant** (the grant is one tmpfs
  file removed by name, and no child owns it); it **cannot affect G1 … G5**, none of which
  cites any child (§2.1); a read-only child (`systemctl show`, `pkcheck`, the PK subject)
  can only linger, the PK subject for at most 60 s; a **mutating** child (`systemd-run`,
  `systemctl stop`) may act late, which is why its *effect is unknown* and no step
  reads `error` as "not created" or "not stopped" (SN-10, CC-7). Its owner is **the
  owner of its enclosing procedure** (table SN-RO): PID 1's cleanup of the unit that started
  the helper *[N, PO-SN (e)]* for the holder, CP, stop-post and the backstop service, and
  then the boot as a **separate recovery event, not evidence that any signal worked**;
  the interactive `attest` has **no automatic owner**. The number of abandoned (or, **Δ6**, `reap-unknown`) children in one PK series is at most the number of calls the schedule
  starts: **at most 20 at the recommended P = 30,000 ms** (7 fixed offsets, then
  every 2,000 ms, counting an offset equal to P). That count is arithmetic on the
  schedule, not a claim about any child's time.

Root's deliberate acts (SL-1), DF-1 and the unremovable-rule class (GU) are
unchanged ([D §4.2.5-R2 (l)]).

### 5.7 GRR, IGR and CL-G *(proposed)*

**GR-2 (new).** *Grant removal is the first mutating act of every rung that
removes a grant on its own initiative (IGR, CL-G), and it precedes every `ext4`
write, every spawn and every lock attempt in that rung.* CP's CQ-3 is not such a
rung: it keeps the accepted order, after the claim, because the claim is the
barrier of SB-1.

**GRR, the grant-release routine.** One routine, one implementation, one test
set. Inputs: the activation identifier and, for the holder, the identity it holds
in memory. Output: one outcome from `removed`, `absent`, `kept-damaged`,
`kept-foreign`, `unremovable {errno}`, `identity-unavailable`. It **never raises**.
It takes no lock, spawns nothing, **sends no signal**, calls no PK, reads no `ext4`
object and writes nothing except the one `unlinkat`.

1. **GRR-1, identity.** The holder uses its in-memory identity (also the content of
   `grant.id`). Any other caller opens K from a descriptor of `/run`
   (`O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC`), then `grant.id`
   (`O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK`) and requires a regular file,
   `root:root`, `0600`, at most 4,096 bytes (mechanically enforced), one parseable
   line. If K or `grant.id` is missing, unreadable or unparsable the outcome is
   `identity-unavailable` and the caller continues with CL's accepted,
   journal-based classification (CL-3). Without GI-1 (DEC-3) every non-holder
   caller takes that path.
2. **GRR-2, presence.** `fstatat(rules_dir_fd, name, AT_SYMLINK_NOFOLLOW)`.
   `ENOENT` → `absent`.
3. **GRR-3, descriptor re-verification, as G-R1.** `openat` the object
   (`O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK`); `fstat` must show a regular file
   with the identity's `(dev, ino)`, uid and gid 0, mode `0644`, `st_nlink = 1` and
   `st_size` equal to the identity's size and at most 65,536 bytes (a mechanically
   enforced cap: GRR reads at most size + 1 bytes); the full SHA-256 must equal the
   identity's; `flistxattr` must show no forbidden name. A mismatch is
   `kept-damaged` or `kept-foreign` and **removes nothing**.
4. **GRR-4, removal.** `unlinkat(rules_dir_fd, name, 0)`. `ENOENT` is `absent`. Any
   other error is `unremovable {errno}`. A `fsync` of the rules directory follows
   for parity with G-R1. On tmpfs it may be a no-op [R2 §7 (g)], and its result is
   ignored by GRR.

GRR is a small number of local system calls on tmpfs. **No elapsed time is claimed
for it** (class X). It waits for none of PID 1, a lock, a child, Polkit or `ext4`,
which is the whole of what is claimed, and it can still be delayed by the kernel.

**IGR (RL-0).**

* **When.** On every catchable end of the holder, from **one** call site: a
  `finally` that wraps the whole body of the holder from the first line after SG-1.
  The body ends by returning, by raising, or by observing the flag (SG-4). No
  signal handler calls IGR (SG-2).
* **IGR-0, latch.** `igr_state` is `idle`, `running` or `done`. IGR returns at once
  unless `idle`. Re-entry is impossible by construction: the single call site, the
  handlers that only set the flag, and GRR, which never raises. A second call (for
  instance a second `finally` after an exception in IGR-2) finds `done` and
  returns. Because GRR is idempotent (a second run of an interrupted removal
  finds `absent`), a *restart* after a crash is also safe: the next rung simply
  re-runs it.
* **IGR-1.** GRR with the in-memory identity. If AM-2 was never reached there is no
  rule and GRR returns `absent`.
* **IGR-2, evidence, after the removal.** One append of `igr {outcome, identity}` to
  the `ACT` journal with `fsync`, **best effort**: an `ext4` write that fails or
  stalls here changes nothing about the grant, which is already gone. If the
  process is killed between the `unlinkat` and this line, a later CL finds the
  rule absent with no `igr` line and classes it `absent-before-removal`, which
  still needs PK *not authorized* before `st1-verified`.
* **IGR-3.** Nothing else. IGR leaves `pass-a.json`, the directories and the
  records to CL. **Δ3** IGR spawns nothing and sends no signal (SG-9).
* **What it does not do.** No spawn, no PK, no lock, no network. It does **not**
  claim `removed-verified`, which needs PK *not authorized* (CL-4).
* **CL's view.** CL-3 reads an `igr` line with outcome `removed` for the rule's
  identity as `removed-earlier`, and a rule found absent with no such line as
  `absent-before-removal`. Either still needs CL-4's own PK *not authorized* for
  `st1-verified`, like CQ-3's removal.
* **Why it is independent of PID 1.** It runs in the process that PID 1 already
  started. It needs PID 1 only to have delivered the signal, which a stop job,
  `RuntimeMaxSec=` and an orderly shutdown all do by `SIGTERM`.
* **No elapsed-time claim.** R1's "handler latency" paragraph (every blocking call
  bounded, "acted on within about ten seconds") is **withdrawn**. IGR runs when the
  main thread reaches a flag check (sliced waits, SG-4) or the end of its body.
  Between those points the holder may be in class-X work. IGR may therefore not run
  before a `SIGKILL`, and the design is correct in that case too (rows 8 and 17,
  IL).

**CL-G (the first act of CL in every trigger).** `stop-post`, `backstop` and
`attest` each begin with GRR, using `grant.id`, **before** CL-0's lock attempts,
its attempt directory and its journal. CL-G's outcome is held in memory and written
as a `cl-g {outcome}` line once the attempt journal exists. CL-3 then classifies
with the benefit of CL-G's result: `removed` → `removed-earlier` (in-process),
`absent` → by the journal as accepted, `kept-*` and `unremovable` → as accepted. If
CL-G returns `identity-unavailable`, CL-3 performs the accepted journal-based
removal (G-R1 with write-ahead, or its grant-priority form).

**The CL order, as amended:** CL-G; CL-0 (lock attempts to the λ deadline, attempt
directory, journal, `run-start`); CL-1; CL-2; CL-3; CL-4; CL-5; CL-5b (which removes
`grant.id` and K last); CL-6; CL-7. §7.9 maps an interruption after each.

### 5.8 PO-21 (c′) *(proposed [N], text for [D §4.4.2b])*

> **(c′)** `ExecStopPost=` is run, as the unit's user, after the main process
> ends for each of these causes: exit `0`, a non-zero exit, any signal, `RuntimeMaxSec=`
> expiry, `systemctl stop`, a failure to execute `ExecStart=`, and a stop issued
> by an orderly shutdown, reboot, `kexec` or userspace-only restart, **provided
> PID 1 can spawn it**. If spawning fails, the unit enters `FINAL_SIGTERM` with
> result `resources` and `ExecStopPost=` does not run [R2 §8 (c)]. The design
> relies on `ExecStopPost=` as one rung of RL and never as a guarantee.

(c′) is the R2 evidence restated. It adds no new host fact. What RL adds as new
proposed behaviour is IGR and GRR (§5.7), the inertness lemmas (§5.4) and the
bounded backstop of §7.4 (`backstop_max`, BS-RM).

### 5.9 Bounded alternative: a resident sentinel *(ALT-SENT, not recommended)*

A second long-lived root process, started at AK-1 before any grant exists, that
waits on a `pidfd` of the holder's main process and, when it ends for any cause,
performs GRR itself. It would close the **uncatchable** branch of RO-1 without
PID 1. It is not recommended because: (a) it adds a second long-lived root image
containing grant-removal code, including a re-hash for G-R1's descriptor
re-verification, which in a Python-free sentinel is new freestanding C and in a
Python sentinel is another unit PID 1 must have spawned and that is exposed to
the same signals; (b) it needs further host-behaviour citations (`pidfd_open`,
poll on process exit, the sentinel's own cgroup and kill behaviour); (c) IL already
shows that the residual it closes is a pre-pass, inert grant; and (d) which of the
two forms it takes depends on the Route 3 outcome. Peter may elect it (DEC-1). If
he does, OH-S4 gains a sentinel and a drill, and §5.6's RO-1 is narrowed to the
loss of both the holder and the sentinel. A sentinel does not remove RO-6.

### 5.10 Negative tests *(proposed, for OH-S4)*

| ID | Case | Asserts |
|---|---|---|
| NT-RL-1 | a fake manager delivers each catchable cause of rows 1 … 7 with `ExecStopPost=` and the backstop both returning `resources` | the rule is unlinked **before the holder exits**, an `igr` line is written **after** the unlink, no spawn, no lock attempt and no `ext4` write occurred before the unlink |
| NT-RL-2 | `SIGKILL` of the holder with both spawns failing (RO-1) | the rule stays live, a start attempt by the fake manager reaches CP, CP removes it (CQ-3 grant priority) and exits non-zero at CQ-4, and `ExecStart=` is never executed (IL) |
| NT-RL-3 | `SIGKILL` with stop-post failing but the backstop spawnable | the backstop's CL runs on its next firing, its first act is CL-G, and it records `st1-verified` or ST-1.ur. **No elapsed time is asserted** |
| NT-RL-4 | `backstop_max` firings with every CL dying | the backstop disarms after the last, appends a journal line, and exits; no unbounded loop; the final state is recorded or left to M-B |
| NT-RL-5 | the installed helper image removed after `ACT` (RO-2) | IGR still ran for a catchable end, RL-1 and RL-2 fail identically, and AP-0 and H-2 would have refused a prior tamper |
| NT-RL-6 | a wedged holder (alive, not observing) | `RuntimeMaxSec=` delivers `SIGTERM` (class M); the holder's `ActiveState` leaves `active`; IL′ holds from that moment; the `SIGKILL` after S finds nothing to do or ends the process |
| NT-RL-7 | IL over generated sequences | with the holder not `active` or `hold-end` present, no fake-manager path executes `ExecStart=` |
| NT-RL-8 **Δ3** | the terminal-cause table | every row 1 … 20 has a defined first removing rung and a defined residual |
| NT-RL-9 | a second and third `SIGTERM` (and a mix of the set H) delivered at every instruction boundary of IGR in a stepped harness | GRR runs at most once to completion, never restarts, never raises; the flag is the only effect of the extra signals; the final `igr_state` is `done` |
| NT-RL-10 | `SIGKILL` of the holder at each IGR point (before GRR-2, after GRR-3, after the `unlinkat`, after the journal line) | the state is exactly the one IM-I (§7.9) names for that point, and the next rung reaches `st1-verified` or a defined HARD STOP |
| NT-RL-11 | handler installation order | the handlers are installed before K exists, before the backstop is armed and before AM-2; a `SIGTERM` delivered at every earlier point creates no grant (SG-1) |
| NT-RL-12 | a backstop CL that never returns (an injected infinite loop) | with BS-RM the fake manager ends it at S_b; without BS-RM the model shows the timer never firing again (the defect of RO-5 is reproduced) |
| NT-RL-13 | `identity-unavailable` | GRR returns it for a missing, wrongly owned, oversized or unparsable `grant.id`, removes nothing, and CL falls back to the journal-based path |

---
## 6. Repair C — PO-21 (s): a valid start-history discriminator *(carried from R1; no R2-F2 change beyond the deadline note)*

### 6.1 What the accepted text says and what is true

[D §4.2.5-R5 (j)] PO-21 (s): *`InactiveEnterTimestampMonotonic` is set, at every
transition of a unit into `inactive` or `failed`, to the manager's monotonic
time of that transition, which is later than every earlier value in the boot.*
Lemma 2 of [D §4.2.5-R5 (f)] uses it as "every ended attempt changes τ to a value
later than every earlier one". SB-2, OS-1, OS-7, CQ-4 and the HL reasons depend
on that reading.

**What is true** [R2 §8 (s), (k), (u), (v)]:

* τ is set only on a transition **from a non-inactive state** into `inactive` or
  `failed`, **while the manager is not reloading**. A `failed` → `inactive`
  transition (`reset-failed`) does **not** set it.
* Its value is `now(CLOCK_MONOTONIC)` in microseconds. **Non-decreasing is
  established. Strictly later than every earlier value is not**: it rests on at
  least one microsecond elapsing between two such transitions.
* It is unchanged while the unit is `activating`, by reads and by a queued start;
  it survives reload and re-exec for a loaded unit; it reads `0` for a unit that
  has been loaded afresh; `systemctl show -p` prints it as decimal microseconds.
* A failed unit stays loaded with its last `InvocationID` until `reset-failed` or
  the next start; an `inactive` unit may be unloaded.
* An attempt ends `failed` when its pre-start step exits non-zero, is killed by a
  signal that no stop job sent, exceeds the start timeout, or cannot be forked or
  executed. **A stop during `start-pre` ends `failed`** (result `signal`) when the
  stop's signal terminates CP. It ends `inactive` **only if CP exits `0` before
  the signal lands** (PO-21 (u), established).
* `systemctl show -p`, run by an `ExecStartPre=+` process during its own start,
  returns without waiting and reports `activating` and τ as it was before the
  attempt (PO-21 (v), established).

### 6.2 What the barrier actually needs

SB-2 never needs "later than every earlier value", and never compares two later
values with each other. It needs one thing: *after the baseline, an ended attempt
leaves τ different from the baseline τ₀.* Three events could break that: the end
of an attempt that does not set τ; a τ that equals τ₀ by coincidence of the
microsecond; and a reload that resets τ to `0`. §6.4 closes the second by
construction, §6.5 handles the first and third explicitly.

### 6.3 The attempt model

| Unit state | `ActiveState` | Entered by | Left by |
|---|---|---|---|
| **Q-i**, quiescent inactive | `inactive` | an attempt's end; `reset-failed`; a fresh load | a start job |
| **Q-f**, quiescent failed | `failed` | an attempt's end with a non-zero result | a start job; `reset-failed` |
| **A**, attempt running its pre-start step | `activating` (`start-pre`) | a start job | CP's exit (to **R** or to an end) |
| **R**, running | `active` (after `ExecStart=`'s `execve`) | CP exit `0` | the main process's end or a stop |
| **E**, ended | `inactive` or `failed` | the end of A or R | — (it is Q-i or Q-f) |

An **attempt** is the interval from a start job leaving a quiescent state to the
unit next entering `inactive` or `failed`. By PO-21 (t) attempts never overlap,
and a start request that joins a queued or running start job is part of that
attempt.

### 6.4 The discriminator SD-1 and the baseline-separation precondition BSP *(proposed)*

* **Reads.** `τ(t)` is the value printed by `systemctl show -p
  InactiveEnterTimestampMonotonic rp11-capture-pass-a.service` (a decimal
  number; `0` if the unit has just been loaded). `m(t)` is
  `floor(CLOCK_MONOTONIC in microseconds)`, read by the holder with
  `clock_gettime`.
* **BSP.** At AM-0 the holder reads `m_a`, and **only then** reads τ₀ together
  with `ActiveState`, `InvocationID` and `Job`. It requires `τ₀ < m_a`. If
  `τ₀ ≥ m_a`, a transition occurred inside the read; it waits at least 2 ms and
  repeats, at most 5 times (class C), then exits `capture-baseline-unstable`
  (non-zero; CL runs; nothing has been linked). Each read is a `spawn()` of
  `systemctl show` under a class-E deadline (§7.3, §7.5): a read that does not
  finish is an *error*, never a baseline. The baseline is `B₀ = (m_a, τ₀, ActiveState,
  InvocationID, Job)` and is journaled in `run-start.capture`.
* **SD-1 (lemma).** If BSP held for `B₀`, then after the τ₀ read any transition of
  the capture unit into `inactive` or `failed` from a non-inactive state, outside
  a reload, leaves `τ ≠ τ₀`.
  *Proof.* The transition happens after the τ₀ read, which happens after the
  `m_a` read. By [E2] CLOCK_MONOTONIC does not decrease, so its time `t′` is at
  least the time of the `m_a` read, and by [E1] the new τ is `floor_µs(t′) ≥
  m_a`. By BSP, `m_a > τ₀`. Hence `τ ≠ τ₀`. ∎ A transition that happened between
  the `m_a` read and the τ₀ read would be reflected in τ₀ and make `τ₀ ≥ m_a`,
  which BSP rejects.
* **The verdict SD.** At any later read, **SD = "no attempt has ended since
  B₀"** if and only if `τ = τ₀` and the unit has not been unloaded (`τ₀ ≠ 0 ⇒
  τ ≠ 0`). `τ = 0` while `τ₀ ≠ 0` is **SD-2**: the unit was unloaded since the
  baseline and an attempt may have ended; the activation ends fail-closed (HL
  `capture-unloaded`).
* **No strictness is used.** SD compares a later τ with the baseline only, never
  two later values with each other, and BSP rules out equality with the baseline
  by the clock, not by an invariant of systemd.
* **Assumptions, as proposed obligations.** *[E1]* τ is the floor, in
  microseconds, of the manager's `CLOCK_MONOTONIC` at the transition ([R2 §8 (s)]
  states "now(CLOCK_MONOTONIC) in µs"; the floor is to be confirmed). *[E2]* the
  holder and the manager read the same `CLOCK_MONOTONIC` and it does not
  decrease within a boot (same time namespace: the holder's loaded unit has no
  `PrivateTimeNamespace=` or equivalent, a property the baseline compares).

### 6.5 Handling of every event the prompt names

| Event | τ effect (accepted evidence) | SD verdict | Handling |
|---|---|---|---|
| an attempt begins (start job, `activating`) | none | unchanged | CQ-4 reads τ during its own attempt: `τ = τ₀` for the first attempt (PO-21 (v)) |
| an attempt ends `failed` (CP non-zero, signal, timeout, fork or exec failure, or a stop during `start-pre`) | set from a non-inactive state | **changed** (SD-1) | SB-2 refuses every later attempt; HL `start-failed-before-exec` |
| an attempt ends `inactive` (the pass ends normally, or a stop lands after CP exited `0`) | set from a non-inactive state | **changed**, or `0` if the unit is then unloaded | the claim exists (CP exited `0` means CQ-2 ran), so SB-1 refuses every later attempt |
| **`reset-failed`** (`failed` → `inactive`) | **not set** | unchanged relative to the last failure's τ | a failure since the baseline already made `τ ≠ τ₀`; with none, the unit was merely reset and no attempt occurred. A root act, outside 𝒜 |
| `daemon-reload`, `daemon-reexec` | preserved for a loaded unit; transitions during the reload are not recorded | unchanged | an attempt whose end is processed after the reload is recorded then. A root act, outside 𝒜 (§13) |
| unit unloaded (`inactive`, garbage-collected) and reloaded | reads `0` | **SD-2 if `τ₀ ≠ 0`**; **blind if `τ₀ = 0`** (SD-3) | SD-2: the activation ends, no pass (liveness). SD-3: see below |
| the same microsecond | n/a | n/a | BSP removes equality with the baseline by construction. Two equal later observations carry no information beyond "no transition between them" |
| a stop during `start-pre` | the attempt ends `failed` (PO-21 (u)) | changed | **CX-4 is void** (§6.8) |
| userspace-only restart, reboot | outside 𝒜; M-B and DF-1 | — | unchanged |

**SD-3, the one blind case.** With `τ₀ = 0` and an attempt that ended `inactive`
with the unit then unloaded, SD reads `τ = 0 = τ₀`. Within 𝒜 an attempt ends
`inactive` only after CP exited `0`, so the claim exists and SB-1 refuses
([R2 §8 (u)]). A first attempt that failed unidentified ends `failed`, which
stays loaded and sets τ. So reaching SD-3 without a claim needs, together: a
failed unidentified first attempt, a root `reset-failed`, and the unit's unload,
all outside 𝒜 (§13, CX-5).

### 6.6 Revised lemmas *(replace [D §4.2.5-R5 (f)] Lemmas 2 and 3)*

* **Lemma 2′ (an ended attempt changes τ, or leaves a claim).** Every attempt
  ends by a transition of the unit into `failed` or `inactive` from a non-inactive
  state. By SD-1, that transition leaves `τ ≠ τ₀` provided BSP held and the
  transition was not during a reload. An attempt that ended `inactive` passed CP
  (PO-21 (u)), so its claim exists. An attempt that ended `failed` keeps the unit
  loaded (PO-21 (k)), so τ persists.
* **Lemma 3′ (the baseline is valid).** `τ₀` is read at AM-0 under BSP and
  re-read at `hold-start` under the lock; the re-read must equal `τ₀` with an
  empty `Job` and a quiescent state (OS-1, OS-7 unchanged). If an attempt had
  begun or ended between them, `hold-start` is not written.
* **Proof of OSA 1 and 3 over 𝒜**, [D §4.2.5-R5 (f)] and [D §4.2.5-R6 (e)] stand,
  with the third case (A₁ in the pre-barrier class and ended `inactive`) now
  **empty**: that case needs a stop job during `start-pre` that ends the attempt
  `inactive` with no claim, and PO-21 (u) shows that such a stop ends `failed`
  (`inactive` only after CP exited `0`, which means a claim).

### 6.7 Procedure amendments *(text for Appendix A)*

* **AM-0** reads `B₀` under BSP and journals `run-start.capture {active_state,
  invocation_id, inactive_enter_us, m_a_us, bsp_retries}`.
* **`hold-start`** re-reads `ActiveState`, `InvocationID`, `InactiveEnterTimestampMonotonic` and
  `Job`; it requires `ActiveState` `inactive` or `failed`, an empty `Job` and
  `τ = τ₀` (which includes "not unloaded").
* **CQ-4 (OS-1)** requires `activating`, `InvocationID` equal to CP's own,
  `τ = τ₀`, with the justification of SD-1. Its text is otherwise unchanged.
* **HL** reasons are unchanged. `capture-unloaded` is SD-2.

### 6.8 CX-4 under the accepted R2 evidence

[D §4.2.5-R5 (k)] and [D §4.2.5-R6 (f)] state CX-4: a root `stop` during the first
attempt's `start-pre`, **plus** "PO-21 (u) showing that such a stop ends the
attempt `inactive`", plus τ₀ = `0` and an unload. [D §4.2.5-R6 (f)] adds: *"If the
PO-21 (u) citation shows that a stop job during `start-pre` ends the attempt
`failed`, CX-4 is void."* The accepted R2 record establishes exactly that
(§6.1). **CX-4 is therefore void** for the cited systemd `259.5-0ubuntu3.4`.
The only remaining way both SB-1 and SB-2 are absent is SD-3 (CX-5, §13), which
needs three root acts outside 𝒜.

This is a restatement of an accepted residual, which Peter accepted as a
documented outside-𝒜 residual. It is **not applied by this proposal**. DEC-6
asks Peter to record the retirement. A change of the systemd version returns
CX-4 to review, because the retirement rests on that version's PO-21 (u).

### 6.9 PO-21 (s′) *(proposed [N], text for [D §4.4.2b] and [D §4.2.5-R5 (j)])*

> **(s′)** For the HF-07 systemd version: (1) `InactiveEnterTimestampMonotonic`
> is set to the floor, in microseconds, of the manager's `CLOCK_MONOTONIC` at a
> transition of the unit from a non-inactive state into `inactive` or `failed`,
> while the manager is not reloading [R2 §8 (s); the floor is *[N]*]; (2) it is
> not set by a `failed` → `inactive` transition, by a read, by a queued start or
> while the unit is `activating` [R2]; (3) it is non-decreasing, and **no
> strictness is claimed** [R2]; (4) it survives reload and re-exec for a loaded
> unit and reads `0` for a unit loaded afresh [R2]; (5) *[N]* the holder and
> the manager read the same, non-decreasing `CLOCK_MONOTONIC`.

The earlier wording, "at every transition" and "later than every earlier value",
is withdrawn. (s′) (1) … (4) restate R2. (5) and the floor are the only new
claims.

### 6.10 Negative tests *(proposed, for OH-S4)*

A fake manager implements exactly the R2-established semantics of §6.1 and
nothing stronger.

| ID | Case | Asserts |
|---|---|---|
| NT-SD-1 | a transition lands in the same microsecond as `m_a` | BSP rejects and retries; after five rejections the holder exits `capture-baseline-unstable` and links nothing |
| NT-SD-2 | randomized timelines of baseline reads and transitions, with transitions allowed in the same microsecond as each other | for every transition after the τ₀ read, `τ ≠ τ₀` (property test of SD-1) |
| NT-SD-3 | an attempt ends `failed`, then a second start | the second CP refuses at CQ-4; `ExecStart=` is never executed |
| NT-SD-4 | `reset-failed` after a failure | τ unchanged and still ≠ τ₀: the second attempt is refused |
| NT-SD-5 | `reset-failed` with no attempt since the baseline | τ = τ₀: the first attempt is allowed |
| NT-SD-6 | `daemon-reload` and `daemon-reexec` at every journal boundary, and an attempt whose end is processed during and after a reload | τ is preserved; an end during the reload is recorded after it |
| NT-SD-7 | the unit unloaded after the baseline with `τ₀ ≠ 0` | SD-2: HL `capture-unloaded`; the activation ends with no pass |
| NT-SD-8 | the SD-3 blind case, built from three root acts | the claim barrier still refuses an *identified* attempt; the blind case is reachable only through the three acts and is recorded as CX-5 |
| NT-SD-9 | a stop job during `start-pre` (the fake implements R2 (u)) | the attempt ends `failed`; SB-2 refuses the next; no combination produces CX-4 |
| NT-SD-10 | code scan | no comparison orders two later τ values; τ is compared only for equality with the journaled baseline |

---

## 7. Repair D — PO-11 (d) and R2-F2: enforced deadlines, named enforcers, and interruption

R1 repaired PO-11 (d) by an operational timeout family, which stands (§7.5, §7.10).
R2-F2 found that R1 also claimed bounds on *CL* and *IGR* that its own procedures
do not support. This section replaces R1's §7 and the elapsed-time statements of
R1's §§4.7, 5.3, 5.7 and 8.2 in full.

### 7.1 What was said, and what is true

**PO-11 (d).** [D §4.4.2a] required a cited bound on Polkit's reload after a
rules file is created or removed, and returned `ACT` and `DEACT` to design review
"rather than polling without a bound". [R2 §6.3, §6.4 (d)]: reload is synchronous
in a GIO monitor callback with no polkit-side timer, coalescing or bound; delivery
latency belongs to GLib and inotify. **No bound is citable.** §7.10 answers that
as R1 did, and it stays.

**R1's elapsed-time claims, and why they fail.**

* *"CL: worst case `lock_wait_ms` + local work + (`pk_op_ms` + `pk_call_ms`),
  below `TimeoutStopSec=` by the S grammar."* The S grammar adds a fixed 30-second
  margin to two arithmetic terms. It does not bound the **local work**, which is
  filesystem inspection, full hashing, process creation and reaping, journal
  writes and `fsync`. A margin is an expectation. It is not a bound.
* *"IGR acts within about ten seconds."* That sentence bounded each *sleep and
  wait* and then inferred a bound on the handler. IGR's own work (descriptor
  verification, a full hash, `unlinkat`, a directory `fsync`, journal appends) has
  no stated deadline, and a Python signal handler runs only when the main thread
  next executes bytecode.
* The accepted design's own *"CL-0 … CL-3, which are local operations bounded by
  S"* [D §4.2.5-R2 (g), "Latency bound"] has the same defect. D3-R3 withdrew that
  paragraph only as a statement about OH-D-7. The sentence and its echoes ("HL ends
  within Δ", "≤ Δ" in the (k) matrix) remain. Appendix A corrects them.

**What PID 1 does enforce** [R2 §8]:

| Fact | Source |
|---|---|
| `RuntimeMaxSec=` arms a deadline on `CLOCK_MONOTONIC` at the service's active-enter time; suspended time is not counted. On expiry the main process receives `SIGTERM`, and after `TimeoutStopSec=` `SIGKILL`, then stop-post runs | (d) |
| `ExecStopPost=` is spawned with `timeout_stop_usec`. On expiry `SIGTERM` goes to what remains (`FINAL_SIGTERM`), after another `TimeoutStopSec=` `SIGKILL` (`FINAL_SIGKILL`), and the unit ends `failed` with result `timeout` | (e) |
| a start-pre step that times out, or is stopped, ends the attempt `failed`; `ExecStart=` is never executed | (o), (u) |
| the capture unit's start timeout is the manager default (HF-16: 1 min 30 s) unless the unit sets one; it is finite for this `Type=exec` unit | (r) |
| the backstop timer does not re-arm while its service is active, and re-arms when the service enters `inactive` or `failed` | (j) |

None of these says that a process leaves an uninterruptible kernel call because a
signal was sent. They fix **when signals are sent**.

### 7.2 Deadline classes

| Class | Name | Who enforces | What it bounds | What it does **not** bound |
|---|---|---|---|---|
| **E** | enforced wait | the helper, on its **own** waiting, with a deadline on `CLOCK_MONOTONIC` set **before** the wait starts and checked at every wake-up. **Δ4** Every sleep lasts at most `slice_ms` **and at most the time then remaining to the wait's own deadline**, and a sleep is not started when nothing remains (WB-2, CC-10) | the time the helper spends *asleep* on a child, a lock or a clock (its **wait budget**, WB-6). At expiry it stops waiting and applies the SN sequence (§7.5a) to the child's process group. The scheduled sleeping for the reaping totals at most `reap_grace_ms` (g), from **one** `t_g` read before the first send or validation; the helper then **abandons** the child after the final reap attempt and takes the operation's fail-closed consequence **Δ3** **Δ4**. **Δ6:** a reap attempt that **raises** ends the sequence at once, with no further send of any kind and no further sleep (RE-1) | the time a child or the kernel needs to finish; the creation of the child; **the signal-send calls, the identity validation and the reap attempts (rows 3a … 3e, 3g) Δ3 Δ4**; the helper's own reads, writes and CPU; the lateness of a sleep; the time to run the expiry code. **Δ4: the elapsed time from the start of an SN sequence to its return is not bounded by g** |
| **M** | enforced by PID 1 | PID 1, by a unit property (`RuntimeMaxSec=`, `TimeoutStopSec=`, the start timeout) | **when `SIGTERM` and `SIGKILL` are sent**, while PID 1 can act (RO-3) | completion of any work; a process in an uninterruptible kernel call; suspended time (`CLOCK_MONOTONIC`) |
| **C** | count | the code, by a fixed number of iterations | the number of attempts, firings or retries | the time of an iteration, which is itself E, M or X |
| **X** | expected quick | nobody | nothing | everything. **No elapsed time is stated for an X operation, and no formula, table, record or test treats a sum of X operations as a bound** |

A **volume cap** (for example, reading at most size + 1 bytes of a file) is
enforced mechanically. It bounds the amount of work and not its time, and it is
listed beside the class it modifies.

**Local sends and PID 1's sends (R3, Δ3).** Two different things are called
"sending a signal". The helper's own system call (**SN**) is class **X** for the call
and class **C** for the number of attempts: it is an *operation*, not a *wait*, and a
helper cannot put a deadline on a system call it is itself executing. PID 1's
sending of `SIGTERM` and `SIGKILL` at the offsets of §7.4 is class **M**. Neither
class says that a signal took effect. The table is §7.5a.1.

### 7.3 Inventory of every potentially blocking operation

Operations are grouped across ACT (AP-0 … HL), CP (CQ-0 … CQ-7), IGR, CL (CL-G …
CL-7, in every trigger), the backstop (BS-1 … BS-4 and its service) and
verification (AP-0, H-2, H-2b, AV-1's re-verification, CL-6, drift checks).

| # | Operation | Where it occurs | Class | Enforcement and fail-closed consequence |
|---|---|---|---|---|
| 1 | creating a child (`fork`, `clone`, `execve` inside `spawn()`) | holder: BSP reads, AK-1 `systemd-run`, the timer `show`, AV-1 PK; CP: CQ-4 `show`, CQ-5 PK; CL: CL-2, CL-4, CL-6; BS: BS-1 … BS-3 | **X** | none. The call's deadline starts **before** creation, so a slow creation consumes it, but creation itself cannot be interrupted |
| 2 | waiting for a child's exit and reading its output | every `spawn()` | **E** (`pk_call_ms` c) | at expiry the SN sequence (rows 3a … 3e, 3g) on the child's process group; result `error` (PK: `unconfirmed`) **whatever the send results and whatever partial output arrived**. Output is capped at 65,536 bytes (volume cap); more is `error` **Δ3**. **Δ4:** every sleep of this wait is capped by the time remaining to c (WB-2) |
| 3 | the scheduled waiting for the reaping of a *signalled* child (SN-6, WB-1 … WB-3) **Δ3** **Δ4** | every `spawn()` | **E** (`reap_grace_ms` g, from **one** `t_g` read **before the first send or validation**) | the sleeps total at most g, none begins at or after `t_g`, and none is restarted by a send, validation, poll, error or signal receipt. After the **final reap attempt** (WB-5) the child is **abandoned** if unreaped (not reaped), `abandoned: true` is recorded, no further signal is sent (SI-4), and the helper continues fail-closed. **Δ6:** if an attempt **raises** instead, the child is not abandoned: it is `reap-unknown`, and no sleep and no send follows (RE-1). An abandoned child holds no descriptor of K **if** SN-8 (e) holds, which rests on PO-SN (c) *[N]* |
| 3a | **send 1, the initial group-directed termination** (SN-I-1): `SIGTERM` to the child's process group when its deadline c expired or the flag was observed | `spawn()` callers in the holder, CP, CL, BS and `attest` | **X** for the call; **C**: one attempt; a local, non-blocking system call *[N, PO-SN (a)]* | no deadline can be put on the call and none is claimed. g was read before it, so a slow send consumes g, and **a send that returns at or after `t_g` skips every later timed wait (WB-3) Δ4**. Result per table SN-R. **No result authorizes, confirms or hides anything** |
| 3b | **send 2, the escalation** (SN-I-2): `SIGKILL` to the same group when the child is still unreaped and valid after send 1 or after its failure | as 3a | **X**; **C**: one attempt, regardless of the clock | as 3a. A late `SIGKILL` costs one call and is sent even after g has passed (WB-4). **Δ4: it is not a wait, it is not completion within g, and it is recorded `late`** |
| 3c | **send 3, the termination of the PK subject** (SN-I-3): `SIGKILL` to the subject's group after every PK call | PK/2 in the holder (AV-1), CP (CQ-5), CL (CL-4), GP-R3, `attest` | **X**; **C**: one attempt | the call's decision is unaffected (SN-7). A failed or indeterminate send leaves a subject that lives at most 60 s (row 4) and is recorded |
| 3d | **sends in cleanup and recovery** (SN-I-4) | IGR, GRR, CL-G, the handlers, CQ-0 … CQ-7, CL-1 … CL-7, BS-1 … BS-4, AP steps, `attest` | **none** | none exist except 3a … 3c inside a `spawn()` wait. No rung signals a process that is not its own unreaped child (SN-9) |
| 3e | **validation of the child's identity before a send** (SN-4: the `reaped` flag, `getpgid`, `getsid`, one capped read of `/proc/⟨pid⟩/stat`) | before each of 3a … 3c | **X** with a volume cap of 4,096 bytes | a mismatch or an unreadable source is **no send** (`identity-mismatch`, `identity-unverifiable`), never a send to a number. **Δ4:** a slow validation consumes g exactly as a slow send does; no time is stated for it. **Δ6:** a handle that is not `running` is not validated at all: no call and no wait (S1-a) |
| 3f | **PID 1's sending of signals** (`RuntimeMaxSec=`, `TimeoutStopSec=`, the start timeout, `FINAL_SIGTERM`, `FINAL_SIGKILL`, cgroup cleanup at a unit's stop) | rows 17 … 20 | **M**; **distinct from 3a … 3c** | fixes *when* PID 1 sends, while PID 1 can act (RO-3). Its sending is not proof that the target exited |
| 3g | **a reap attempt** (WB-5): one non-blocking `reap_step()` (`Popen.poll()`), made after a clock read at S3, S5 and S6 **Δ4** | every `spawn()` | **X**; **C** only in that the sequence makes a fixed number of them per sleep | it is never a wait: it has no timeout argument and no retry loop. It may report the child reaped or unreaped. A raised exception is caught inside SN and recorded as the anomaly `reap-error`, and **it is read as neither reaped nor unreaped (Δ6)**: the handle becomes `reap-unknown`, **no later signal of any kind, no further attempt and no sleep follows** (RE-1 … RE-5), and the child is neither abandoned nor presumed reaped. The timed wait that precedes an attempt is row 3, capped. **Δ5:** its interior has five phases (RA-0 … RA-4, §7.5a.6c), and **Δ6:** a sixth, RA-E, for an attempt that raised; whether `poll()` can raise after the kernel has consumed the status is evidence only (PO-SN (c′), Q18) and **changes no decision of this row** (RE-6). **No elapsed time is stated for it** |
| 4 | the PK subject's own life (`sleep 60`) | PK/2 | self-limiting (its argument), not enforced by the helper | counted as **X** for every claim. If the helper dies the subject ends by itself. Its termination after a call is send 3 (row 3c) **Δ3** |
| 5 | the executor's wait for the `act` record or the holder's end | AP-2 | **E** (`act_wait_s`) | HARD STOP `act-unconfirmed`. The executor acts on nothing and repairs nothing. The holder continues under L |
| 6 | the lock loop on K | holder AM-0 (once), HL decision (once), CP (once, CQ-1), CL (to the deadline) | **E** (`lock_wait_ms` λ) for the loop. Each `flock(LOCK_NB)` call is non-blocking by its flag and counted **X** | at λ: `lock_mode: "degraded"` (CL), `consume-busy` (CP), HARD STOP `lock-object` (holder AM-0) |
| 7 | sleeps between polls (HL Δ, the PK schedule, BSP's 2 ms) | holder, PK/2, CL | **E** | sliced at `slice_ms` so that the flag (SG-4) is observed, and **Δ4** each slice capped by the time remaining to the wait's own deadline (WB-2, CC-10) |
| 8 | reading small root-owned files: journals, records, `pass-a.json`, `grant.id`, the H-1 record, A-2 pins | all | **X** with a **volume cap**: `pass-a.json` 65,536 bytes (accepted CQ-0), `grant.id` 4,096 bytes, any journal `journal_max_bytes` | an oversize or unparsable object is `invalid-journal` or `consume-unidentified` and fails closed. No time is stated |
| 9 | SHA-256 over files | GRR (the rule, at most 65,536 bytes); AP-0, AM-0, H-2 (helper images, `rp11_h1.py`); CL-6's **recomputation of the H-1 `baseline`**, which hashes every member of the baseline set | **X** with a volume cap per file | CL-6's recomputation is the **largest local job** in CL and runs **last** before the records, so an interruption in it costs only verification (§7.9, L7) |
| 10 | metadata and extended-attribute inspection (`fstat`, `lstat`, `flistxattr`, `readlink`) | every verification | **X** | none |
| 11 | appends and `fsync` to the `ext4` journals and records; `mkdirat` of evidence directories; PF and PT publication (`linkat`, `renameat2`, `mkdirat`) | holder, CP, CL | **X** | an *error* return is handled as accepted (grant-priority and GP-R3 forms). A *stall* is unbounded (RO-6) |
| 12 | `unlinkat` of the rule and of `pass-a.json`; `fsync` of a tmpfs directory | GRR, CQ-3, CL-5, CL-5b | **X** (tmpfs; `fsync` may be a no-op [R2 §7 (g)]) | none |
| 13 | signal *receipt* by the interpreter and handler execution (the *sending* of signals is rows 3a … 3f) **Δ3** | holder | **X** | handlers run only between bytecodes of the main thread and only set a flag (SG-2). The flag is observed at boundaries and at every slice of an E wait (SG-4) |
| 14 | the PK series as a whole | PK/2 | **E** (P) | no call starts after P; the helper's **scheduled waiting** for the last call totals at most c + g after that call starts, so the series' scheduled waiting is at most P + c + g (**Δ4:** a budget of sleeps, WB-6, not the instant of return); result `unconfirmed` |
| 15 | BSP re-reads | holder AM-0 | **C** (5) | `capture-baseline-unstable` |
| 16 | backstop firings that run CL | BS-4 | **C** (`backstop_max` B; `k` ≤ 99 accepted) | the next firing disarms the timer, appends a journal line, exits non-zero |
| 17 | the holder's whole life | ACT … HL | **M** (`RuntimeMaxSec=` L) | `SIGTERM` at L, `SIGKILL` after S |
| 18 | the stop-post CL's whole life | RL-1 | **M** (`TimeoutStopSec=` S) | `SIGTERM` at S, `SIGKILL` after a further S, unit `failed` / `timeout` |
| 19 | the backstop firing's whole life | RL-2 | **M** (`RuntimeMaxSec=` S_b, **proposed [N]**, BS-RM) | `SIGTERM` at S_b, `SIGKILL` after S. **Absent BS-RM, no bound (RO-5)** |
| 20 | CP's whole life | RL-3, CQ-0 … CQ-7 | **M** (the capture unit's start timeout T_s) | the attempt ends `failed`; `ExecStart=` is never executed; SB-2 refuses every later attempt |
| 21 | verification reads by the executor (AP-0, H-2, H-2b) | executor, unprivileged, interactive | **X**; no PID-1 timer | an interruption mutates nothing (these steps create nothing): INVALID RUN, no lock object, no grant |
| 22 | `attest` | operator, interactive | no enforcer | an interruption leaves the records missing; every later RP-11 step refuses (the accepted gate) |

### 7.4 Terminators by procedure, and the backstop literal

| Procedure | PID-1 terminator (class M) | Offsets | Whole-procedure elapsed-time claim |
|---|---|---|---|
| holder (ACT, HL, IGR) | `RuntimeMaxSec=` L | `SIGTERM` at L; `SIGKILL` after S | the holder leaves `active` at L (IL′). **No claim about when its work completes** |
| stop-post CL (RL-1) | `TimeoutStopSec=` S | `SIGTERM` at S; `SIGKILL` after a further S; then `failed`, result `timeout` | **none.** CL may be signalled at S and killed at 2S |
| backstop firing (RL-2) | `RuntimeMaxSec=` S_b (BS-RM) | `SIGTERM` at S_b; `SIGKILL` after S | **none**; the firing ends, and the timer then re-arms [R2 §8 (j)] |
| CP (RL-3) | the capture unit's start timeout T_s | the attempt ends `failed` | **none** for CP's completion. SB-2 and SB-1 make every later attempt refused |
| `attest`, AP-0, H-2 | none | — | none |

**Local sends and PID 1's sends (R3, Δ3).** The offsets in the table above are
PID 1's sends (class **M**, §7.3 row 3f). A root helper that sends a signal to its
own child does so through SN (class **X**/**C**, §7.3 rows 3a … 3e). A helper's send
is never described as a PID-1 act, and PID 1's offsets are never described as proof
that a process left a kernel call.

**BS-RM (proposed [N], a correction of the accepted backstop literal).** The
literal of [D §4.2.5-R2 (f)] ends with `--property=TimeoutStartSec=⟨S⟩`. It is
replaced by two properties:

```text
--property=RuntimeMaxSec=⟨S_b⟩ --property=TimeoutStopSec=⟨S⟩
```

and `TimeoutStartSec=` is dropped, because on a `Type=exec` service it would end at
`execve` (§5.6, RO-5). `S_b` is a parameter (§7.6). The statement that
`RuntimeMaxSec=` applies to the main process of a `Type=exec` service that a timer
activates is the same code path R2 cites for the holder [R2 §8 (d)] and is
**proposed for citation** (OH-S2b). It needs no new host fact beyond that.

### 7.5 `spawn()`, the helper-child discipline, and PK/2

These are properties of the activation design and hold under every Route 3
outcome that keeps any child process.

* **HS-1.** Every child of a root helper is created by **one** function, `spawn()`,
  in one module. No other process-creation call appears in any root helper
  (scan test NT-HS-1).
* **HS-2.** `spawn()` passes **only** the closed map `{LC_ALL=C, PATH=/usr/bin}`,
  never `None`, never a copy of the helper's own environment, and the program's
  absolute path under `/usr/bin`.
* **HS-3.** `close_fds=True`, `pass_fds=()`, working directory `/`, a **new
  session** (so the child's process-group and session IDs equal its PID, SI-1), no `preexec_fn`, and for the PK subject the credential change by the
  primitive's own arguments (user, group, supplementary groups) rather than by code
  between `fork` and `exec` *[N: CPython 3.14.4's process-creation arguments are
  cited at OH-S2b]*.
* **HS-4.** No shell, no `os.system`, no `os.exec*p`, no `shell=True`.
* **HS-5 (class E for the wait; class X and C for each send). Δ3 Δ4** Every spawn has a
  monotonic deadline c. At expiry, at an observed flag, or (for the PK subject) after
  the call, the helper acts on the child **only through SN (§7.5a)**: validated,
  unreaped, the closed set `SIGTERM`/`SIGKILL`, one attempt per signal, no retry, and
  no result read as evidence. Its **scheduled waiting** for the child's reaping totals at
  most g, from **one** `t_g` read once, before the first send or validation. Every sleep
  is capped by the time remaining to `t_g`, none begins at or after it, and no send,
  validation, poll, error or signal receipt starts another grace period (WB-1 … WB-3,
  WB-7). The escalation of S4 is **not a wait**: it may follow `t_g`, as a class-X call
  recorded `late` (WB-4). After the final reap attempt (WB-5) the helper abandons the
  child (SN-8) without a further signal. **Δ6:** A reap attempt that raises ends the sequence at once, with no further send of any kind and no further sleep (RE-1). There is no blocking `wait()` or `waitpid()`;
  the only reaping call is the non-blocking reap attempt (row 3g). No send goes to a child the helper has reaped, abandoned or suppressed after a `reap-error` (**Δ6**). **Sending a signal is not proof that the target exited, was reaped, or left
  a kernel call.** The OH-S3 R2 wording "is killed at it by a signal to its process
  group" is withdrawn (§7.7 W-12).
* **HS-6.** `rp11_h1.py` (or its successor under Route 3) reads the environment
  only for the diagnostic `INVOCATION_ID` and decides nothing from any other
  variable.

**PK/2 (replaces `pk-root/1` of [D §4.2.5-R1 (f)]).**

* **Subject.** One subject process **per call**, created by `spawn()`, in its own
  session, with the supplementary groups, GID and UID that the H-1 record holds for
  `ubuntu`, executing `/usr/bin/sleep 60`. **Δ3** **Δ4** It receives, after each call, an SN-3 send (`SIGKILL`, process group,
  under the SN contract), which neither ends it nor proves that it ended. If that send fails, is not made, or the subject is not reaped by the final attempt (WB-5, **Δ4**), the subject is abandoned (SN-8), recorded, and lives at most 60 s. **Δ6:** if a reap attempt of the subject raises, the subject is `reap-unknown` (RE-1): it is signalled no further, recorded, and lives at most 60 s.
  If the tool dies it also lives at most 60 s. It holds no lock descriptor. The
  call's decision, already given by `pkcheck`'s own exit status, is unaffected.
  **Δ4:** the subject's single send is `SIGKILL` (S4), which is not a wait and which
  the wait budget does not delay or skip; the capped reap waiting that follows it
  (S5) takes its `t_g` from S0, read after the call finished.
* **Call.** `/usr/bin/pkcheck --action-id org.freedesktop.systemd1.manage-units
  --process ⟨pid⟩,⟨start-time⟩,⟨uid⟩ --detail unit rp11-capture-pass-a.service
  --detail verb ⟨verb⟩`, as **root**, without `--allow-user-interaction`, with the
  closed environment of HS-2, under the deadline c. At c the child's process group receives the SN sequence (§7.5a), not a direct kill (Δ3).
* **Outcome of one call.** Exit `0` is `authorized`. Exit `1` or `2` is
  `not-authorized` ([R2 §6.4 (e)]: 1 not authorized, 2 challenge). Any other status,
  a spawn failure, an unparsable result, the deadline (**whatever the send results of SN and whatever partial output arrived**, Δ3), or an abandon is `error`.
* **Series.** Three modes: **seek-authorized** stops at the first `authorized`;
  **seek-not-authorized** stops at the first `not-authorized`;
  **first-decisive** stops at the first `authorized` or `not-authorized`. An
  `error` never ends a series: it retries on the closed schedule, offsets 0, 250,
  500, 1,000, 2,000, 3,000 and 4,000 ms, then every 2,000 ms, measured on
  `CLOCK_MONOTONIC`. **No call starts after P has elapsed.** The helper's *scheduled
  waiting* for the series totals at most P + c + g (**Δ4**: a budget of sleeps, WB-6;
  not a statement about when the series returns, which includes class-X operations). A
  `stop_requested` flag (SG-4) ends the series at the next wake-up with result
  `interrupted`.
* **Result.** `authorized`, `not-authorized`, or `unconfirmed`, with a reason:
  `only-errors`, `still-authorized` (a seek-not-authorized series saw only
  `authorized` and errors), `not-seen` (a seek-authorized series saw only
  `not-authorized` and errors), or `interrupted`.
* PK starts, stops or changes nothing (as accepted).

### 7.5a The signal-sending operation SN and the child-handle contract *(R3; proposed)* **Δ3**

R3-F1 found that §7.3 inventoried the *delivery* of signals and the *reaping* of
children but not the helper's own act of *sending* a signal. This subsection supplies
the inventory, the class, the failure contract, the identity contract and the
recovery owner. It adds **no parameter**: the deadlines are c, g and `slice_ms` of
§7.6, and N1 … N4 are unchanged, because their terms bound the helper's *waiting* and
a send is not a wait. It claims **no elapsed time** for any send. It does not touch
G1 … G5, none of which cites a child or a signal (§2.1).

#### 7.5a.1 Two operations share the word "signal"

| | the local send (**SN**) | PID 1's delivery |
|---|---|---|
| Actor | a root helper's own process, one system call | PID 1's unit state machine |
| Occurs | at an expired deadline, an observed flag, or after a completed PK call (table SN-I) | at `RuntimeMaxSec=`, `TimeoutStopSec=`, the start timeout, `FINAL_SIGTERM`, `FINAL_SIGKILL` and a unit's stop (§7.4) |
| Class | **X** for the call; **C** for the number of attempts | **M** |
| What the class fixes | nothing about elapsed time; at most one attempt per signal | *when* PID 1 sends, at the stated offsets, while PID 1 can act (RO-3) |
| What success means | the kernel accepted the signal for at least one process of the target group *[N, PO-SN (a)]* | PID 1 attempted delivery |
| What success never means | that the target acted on it, exited, was reaped or left a kernel call; that the group is empty; that any authorization or file state changed | the same |

**The inventory SN-I.** Every signal send that `spawn()` or another helper performs:

| ID | Send | Trigger | Signal | Target | Callers |
|---|---|---|---|---|---|
| SN-I-1 | the initial group-directed termination | an E wait's deadline c expired, or the flag (SG-4) was observed during an E wait | `SIGTERM` | the process group of that wait's child | every `spawn()` caller: the holder (BSP and baseline `show`, AK-1 `systemd-run`, the timer `show`, AV-1's PK calls, HL's observations), CP (CQ-4, CQ-5), CL (CL-2, CL-4, CL-6), BS (BS-1 … BS-3) and `attest` |
| SN-I-2 | the escalation | the child is still unreaped and valid after SN-I-1's send, or after its failure (step S4) | `SIGKILL` | the same group | the same |
| SN-I-3 | the termination of the PK subject | a PK call finished, with any result | `SIGKILL` | the subject's process group | PK/2 in the holder (AV-1), CP (CQ-5), CL (CL-4), GP-R3 and `attest` |
| SN-I-4 | any signal used by cleanup or recovery | — | **none** | — | IGR, GRR, CL-G, the handlers, CQ-0 … CQ-7, CL-1 … CL-7, BS-1 … BS-4, the executor's AP steps and `attest` send **no signal** except SN-I-1 … SN-I-3 inside a `spawn()` wait. No rung signals a process that is not its own unreaped child (SN-9) |

#### 7.5a.2 The class of the local send

The call is class **X** (§7.2): *expected quick, not bounded*. It is a local system
call that, by the kernel's documented semantics, queues the signal and returns
without waiting for the target *[N, PO-SN (a)]*, so it is not a wait and a helper
cannot enforce a deadline on it. It is also class **C**: **one attempt per signal,
no retry, at most two sends per expired child and one per completed PK subject**.
Two consequences are stated rather than assumed. First, the deadline that governs
what follows, the grace deadline `t_g`, is **read once, before the first validation or send**, so a slow or
stalled send consumes g, and **a send that returns at or after `t_g` leaves no timed wait to
make (WB-3, Δ4)**. Second, because the kernel can delay the call, no sum
containing a send is stated as a bound, and none of N1 … N4, W_show or W_series
contains one.

#### 7.5a.3 The child handle and identity: CH, SI-1 … SI-4

`spawn()` returns, and the helper keeps in memory only, a **child handle (CH)**:
`pid`; `pgid` and `sid` (both equal to `pid`); `start_ticks` (field 22 of
`/proc/⟨pid⟩/stat`, read at creation; optional, PO-SN (d)); `created_ms` and
`deadline_ms` on `CLOCK_MONOTONIC`; `state` ∈ `running`, `reaped`, `abandoned`, `reap-unknown` (**Δ6**, RE-2);
`sends` (each: signal, result, offset); `anomalies`; and `effect` (`none` or
`unknown`, SN-10). A CH is diagnostic evidence. **No PID or group number is ever an
authority** (SN-2).

* **SI-1, own group.** Every child is created in a new session (HS-3), so its
  process-group and session IDs equal its PID. `spawn()` returns a handle only after
  `Popen` has returned, which on CPython happens after the child's `exec` or its
  failure *[N, PO-SN (c)]*. A returned handle therefore names a child that is already
  in its own group, and `spawn()` checks `getpgid(pid) == getsid(pid) == pid` and
  that `pid` is not the helper's own group before the handle is usable. A failed
  check or a failed capture marks the handle `identity-unverifiable` **from creation**:
  no signal is ever sent to it (SN-4).
* **SI-2, the pinning argument: the whole reuse defence.** While the helper has **not
  reaped** a child, the kernel does not assign the child's PID number to another
  process, and does not assign a process-group number equal to it to a new group
  while the child's group has a member *[N, PO-SN (b)]*. An unreaped child, including
  a zombie, pins both numbers. So while `state` is `running` the number in the handle
  names this child's group. **Validation (SN-4) is a detector of contradiction and of
  a corrupted handle. It is not a substitute for SI-2.** **Δ7:** SI-2 in turn holds only while SI-3's sole-reaper invariant does (SI-5). If PO-SN (b) is not accepted
  for the HF-04 kernel, the contract of this subsection cannot be adopted and AP-0 is
  INVALID RUN (§13.2). R3 invents no weaker guarantee.
* **SI-3, sole reaper.** Exactly one function, `reap_step()`, reaps a child (a
  non-blocking `waitpid` through `Popen.poll()`), and it sets `state = reaped` in the
  same step. Root helpers create no threads, never set `SIGCHLD` to `SIG_IGN` or
  `SA_NOCLDWAIT` (SG-3, PO-SN (f)) and call no other `wait*` (NT-SN-12). **Δ7: this invariant is load-bearing.** SI-2's pinning is a
  statement about a process that is the **only** reaper of its children, so **no thread, signal
  disposition, destructor or finalizer, foreign `wait*` call, `Popen` cleanup or other path may reap a child
  outside `reap_step()`**. The `Popen` object of every child is kept referenced for the helper's life
  (SN-8 (c), RE-3), so no destructor of this design's children runs while a send decision can
  still be made. The version-bound obligations that support the invariant are PO-SN (b), (c) and
  (f), proposed and unchanged, and **AP-0 is INVALID RUN unless they are accepted** (§7.5a.8). The
  detector in SN-4 is not part of the invariant, and what follows if the invariant is violated is
  stated in SI-5. Hence
  `state = running` means "not reaped by this process", and the only event that can
  change the child's kernel state between SN's validation and its send is the child's
  own exit, which leaves a zombie that still pins the numbers (SI-2). **Δ5:** the one
  window in which `state = running` is stale is RA-2 (the kernel has reaped the child and
  the handle is not yet updated), and **no validation, send, wait or record is made in it**
  (RB-3): at every point where SN acts, `running` is exact. **Δ6:** the same holds for the phase RA-E (a reap attempt that raised, the handle not yet updated): the helper does nothing there but set `reap-unknown` (S8, RE-1), and a handle in `reap-unknown` **never returns to `running`**. SN acts only on a handle that is `running`, and a `running` handle was last seen by a **normal** return of an attempt that found the child unreaped, or has had no attempt at all.
* **SI-4, no use after release.** A handle in `reaped`, `abandoned` or `reap-unknown` state is never signalled: SN returns `not-sent(reaped)`, `not-sent(abandoned)` or `not-sent(reap-unknown)` without calling the kernel, and the sequence ends at S7 (S1-a, **Δ6**). A PID or group number is never taken from `/proc`, `MainPID`, a journal,
  a record or an earlier handle (SN-2).
* **SI-5, a violated sole-reaper invariant is outside the design (R7, Δ7).** SI-2 holds only while
  SI-3 does. Suppose a child is reaped by any path other than `reap_step()`: an injected foreign
  reaper in a test, a thread, a signal disposition, a destructor, a foreign `wait*` call. The
  handle then still says `running`, the kernel may already have released the child's PID and
  process-group number, and a new process may have taken both with **the same structural
  relationship** (`pgid == pid == sid`). The `start_ticks` comparison of SN-4 (iv) exists only if
  PO-SN (d), which is optional, is accepted, and even then it distinguishes a reuse only if the
  reading succeeds and the values differ. **SN-4's validation is a detector of contradiction and
  of a corrupted handle: it may return `identity-mismatch` or `identity-unverifiable`, and it need
  not.** Therefore (a) an injected foreign reap is a **deliberate violation of a design
  precondition, not a supported runtime state**, and the design has no guaranteed mechanism that
  notices it; (b) **once the invariant is violated, this design makes no reuse-safety claim from
  SN-4 alone**, for any send that follows; (c) R7 adds no mandatory `start_ticks` check, no pidfd
  and no other identity mechanism (PO-SN (d) stays optional, and a stronger mechanism would be a
  separate design decision, not this remediation); (d) the defence is the **structural**
  sole-reaper properties, which NT-SN-12 tests, with PO-SN (b), (c) and (f) and the AP-0 refusal;
  (e) no sentence of this document says that validation catches a foreign reap or a coincidental
  reuse, and the sentence that did is withdrawn (W-17).

#### 7.5a.4 The rules SN-1 … SN-10

* **SN-1, one function, a closed set.** One function, `send_child_signal(handle,
  sig)`, in the module of `spawn()`, makes the system call. `sig` is `SIGTERM` or
  `SIGKILL`. No other call in any root helper sends a signal: no `os.kill`, no
  `os.killpg`, no `pidfd_send_signal`, no `raise_signal`, no spawned `kill`, `pkill`,
  `killall`, `timeout` or `systemctl kill` (NT-SN-10).
* **SN-2, never by number alone.** The target is the group of a CH created by this
  process's `spawn()`. SN never signals a number obtained from anywhere else.
* **SN-3, one attempt each.** At most one send per child and signal. `EINTR` or any
  other error is **not retried**. A child therefore receives at most two sends; a PK
  subject one.
* **SN-4, validate, then send, on the main thread, with the child unreaped.** Before
  each send SN requires, in order: (i) `state == running` (else `not-sent(reaped)`, `not-sent(abandoned)` or `not-sent(reap-unknown)`, which **end the sequence at S7 with no call and no wait**, S1-a, **Δ6**); (ii) `pid > 1`, `pgid == pid`, and `pgid` not the helper's own
  group; (iii) `getpgid(pid) == pgid` and `getsid(pid) == pgid`; (iv) *if PO-SN (d) is
  accepted*, the start time read from `/proc/⟨pid⟩/stat` (parsed after the last `)`,
  read capped at 4,096 bytes) equals `start_ticks`. A failure of (ii), (iii) or (iv) is
  `not-sent(identity-mismatch)`; a read or parse error, an unavailable `/proc`, or a
  handle marked `identity-unverifiable` is `not-sent(identity-unverifiable)`. After either of those two, **no signal of any kind is sent to that child** (SN-5, rows 7 and 8 of SN-R) and the sequence goes to S5 (S1-b, **Δ6**). **Δ7:** validation is a **detector only**. It cannot show that a released number has not been reused by a process of the same structural identity, and **no reuse claim rests on it** (SI-2, SI-5).
* **SN-5, no mechanism but SN.** If SN does not send, the helper tries nothing else:
  no `sudo`, no `kill` binary, no capability, no second primitive.
* **SN-6, the reap wait (class E). Δ4** **Δ7** There is **at most one** grace deadline per child
  (**Δ7:** exactly one if S0 ran and none otherwise, GD-1). When S0 runs,
  `t_g` = `CLOCK_MONOTONIC` + g, **read once at S0, before the first validation or send**.
  After the first send, or at once if none is made, the helper makes reap attempts and
  sleeps only as WB-1 … WB-7 (§7.5a.6a) allow: every sleep is capped by the time remaining
  to `t_g`, **no timed wait begins at or after `t_g`**, and no send, validation, poll, error
  or signal receipt starts another grace period. The flag (SG-4) is observed at each
  wake-up but **neither shortens nor extends** this waiting (CC-2). The escalation of S4 is not a wait and does not depend on `t_g`. **Δ6:** a reap attempt that raises ends all waiting at once (S8, RE-4).
* **SN-7, no send result is evidence.** No send result (`sent`, `esrch`, an error,
  `not-sent`) is read as *exited*, *reaped*, *absent*, *authorized*, *not authorized*,
  *created*, *removed* or *armed*. The only evidence that a child ended is its reaped
  status; `abandoned` records only that the final reap attempt did not find it reaped, and
  is **not** evidence that it is alive (**Δ4**). **Δ6:** a `reap-error` is evidence of neither reaping nor its absence (RE-2). A recorded reap status of the direct child
  is not evidence that its process group is empty. **Δ5:** a kernel reap that no durable
  `child` line records (CS-5) is evidence of nothing to any later procedure (IS-9). The enclosing
  operation's result is the one its E wait defines (`error`; `interrupted` for a flag;
  PK `unconfirmed`), **whatever the send results and whatever partial output arrived**.
* **SN-8, abandon.** If the **final reap attempt** (WB-5: the attempt of S5 that begins at or after `t_g`) **returns normally** and finds the child unreaped **Δ4** **Δ6** (an attempt that raises is S8, never an abandon): (a) its state becomes
  `abandoned`; (b) the helper stops waiting for it and never signals it again (SI-4);
  (c) its `Popen` object stays referenced for the life of the process, so that no
  destructor decides anything, and a later reaping by the interpreter's own cleanup
  changes nothing because nothing signals it afterwards; (d) the helper records
  `abandoned: true`, `sends`, `last_signal` and `anomalies`; (e) **the abandoned child
  holds no descriptor of K**, because a child is abandonable only after `Popen`
  returned, that is after its `close_fds` closed every descriptor ≥ 3 and it `exec`ed
  *[N, PO-SN (c)]*; a child that has not yet returned from `Popen` is not abandonable,
  because the helper is still inside creation (row 1, class X); (f) the operation
  continues with its fail-closed result; (g) the helper runs no recovery on the child.
* **SN-9, nothing hunts.** No later procedure (CL, BS, `attest`, CP, the executor, a
  later activation) scans for, signals, reaps or otherwise acts on an abandoned child
  or on any process of an earlier procedure. A recorded PID is evidence only. This
  extends LD-9.
* **SN-10, effect unknown for a mutating child.** `systemctl show`, `pkcheck` and the
  PK subject change no host state. `systemd-run` (AK-1) and `systemctl stop` (BS-2,
  BS-3) **do**. For a mutating child whose result is `error`, `interrupted` or
  abandoned, the record states `effect: "unknown"`, and **no later step may read the
  result as "not created" or "not stopped"**. AK-1's existing consequence (exit
  non-zero; CL runs) already follows `backstop-intent`, which the design appends
  before the literal is issued; **whether CL's by-name disarm of the backstop timer is
  keyed to `backstop-intent` and not only to `backstop-armed` was not re-read in R3
  and is a confirmation item for OH-S0d (Appendix A, A-I-16)**.

#### 7.5a.5 Results of a send: table SN-R

Every row ends the same way for the enclosing operation (SN-7): its result is the E
wait's own, and **no row yields a pass, a confirmation or a concealment**. Every row
is recorded (§7.5a.9), except row 11, which is the loss of the record with the helper.

| # | Condition at the call | Recorded send result | Anomaly recorded | What the helper does next |
|---|---|---|---|---|
| 1 | the call returns 0 | `sent` | none | go on to S3 (after `SIGTERM`: one reap attempt, then, **if `t_g` has not been reached**, one capped sleep of `min(slice_ms, t_g − now)`, then S4) or S5 (after `SIGKILL`). `sent` is not exit, reaping or absence; a reap attempt that raises goes to S8 (row 12) **Δ4** **Δ6** |
| 2 | `ESRCH` while the child is unreaped | `esrch` | `esrch-while-unreaped`: a group with an unreaped member exists, so the kernel's answer contradicts the handle | as row 1; **never read as "the child is gone"**; after `SIGTERM`, S4 still sends `SIGKILL` once if the child is still unreaped (a normal return of S3's attempts) and valid; an attempt that raises goes to S8, **no `SIGKILL`** (row 12) **Δ4** **Δ6** |
| 3 | the handle is `reaped`: an enclosing wait's poll reaped it before SN was entered (RA-3 of that poll) **Δ6** | **no call is made**: `not-sent(reaped)` | `reaped-before-send` (benign) | **no call, no wait; the sequence ends at S7 (S1-a).** Never S5 **Δ6** |
| 4 | `EPERM` | `eperm` | `eperm-from-root` | after `SIGTERM`: one reap attempt (S8 if it raises), then S4 at once, **no timed wait first**; after `SIGKILL`: no further send, S5 (capped sleeps while `t_g` has not been reached, then the final reap attempt), then abandon. No other mechanism (SN-5) **Δ4** |
| 5 | `EINVAL`, `EINTR`, or any other errno, or an `OSError` without one | `errno:⟨n⟩` | `send-error` | as row 4; **no retry** (SN-3). The error starts no grace period (WB-7) **Δ4** |
| 6 | an exception that is not `OSError`, or the primitive is unavailable | `exception:⟨class⟩` | `send-error` | as row 4; the exception is caught **inside** SN and never propagates to the helper's body |
| 7 | SN-4 (ii), (iii) or (iv) fails | `not-sent(identity-mismatch)` | `identity-mismatch` | **no send of either signal to this child**; **S1-b: go to S5** (capped sleeps while `t_g` has not been reached, then the final reap attempt); abandon, or S8 if an attempt raises **Δ4** **Δ6** |
| 8 | the handle is `identity-unverifiable`, or `/proc` cannot be read or parsed | `not-sent(identity-unverifiable)` | `identity-unverifiable` | as row 7 |
| 9 | the handle is `abandoned` or `reap-unknown`, or `reaped` as in row 3 **Δ6** | `not-sent(abandoned)`, `not-sent(reap-unknown)` or `not-sent(reaped)` | none | **no call, no wait; the sequence ends at S7 (S1-a)** **Δ6** |
| 10 | a send, or the validation before it, **returns at or after `t_g`** (the kernel or the system delayed it) **Δ4** | recorded as it returns, with `late: true` | none | **every later timed wait is skipped** (WB-3). One reap attempt follows; if the child is unreaped and valid, `SIGKILL` once (S4, not a wait, WB-4), then the final reap attempt, then abandon. `SIGTERM` and `SIGKILL` may therefore be sent back to back with no sleep between them; that is accepted: the grace was spent |
| 11 | the helper itself ends **inside** the call or between the call and the recording of its result (a signal, a class-M timer, a root act) **Δ4** | **none: the result is lost with the helper** | none | not a helper action, so no next step. The signal may or may not have been queued. The state is the cell of the matrix IM-S (§7.9, outcome `x`); nothing is inferred |
| 12 **Δ6** | a **reap attempt raises** (S3, S5, the final attempt, or a poll of the enclosing wait). It is not a send, so it has no send result and no send decision | none | `reap-error` | **S8:** the handle becomes `reap-unknown`; **no further send of any kind (S4's `SIGKILL` included), no further attempt and no sleep**; the record; the enclosing fail-closed result (RE-1 … RE-5). **Δ7:** a raise in a **poll of the enclosing wait** happens **before S0**: no `t_g` exists, none is read and none is created, and `grace_deadline_ms` is `null` (GD-1 … GD-3) |

#### 7.5a.6 The sequence after a deadline or a flag: table SN-S **Δ4** **Δ6**

In this table `clock()` is one `CLOCK_MONOTONIC` read, `R-attempt` is one reap attempt
(row 3g, WB-5), `sleep(d)` is a timed wait of length `d` (class E), and "reaped" means the
R-attempt returned an exit status for the direct child. No step calls a blocking `wait`. **Δ6:** an R-attempt has three results: *reaped*, *unreaped* (a normal return that found no exit status) or *raised* (an exception, recorded as `reap-error`); a raised attempt is never read as either of the others and goes to S8. A **settled** handle is one in state `reaped`, `abandoned` or `reap-unknown`. **Δ5:** the interior of an R-attempt (RA-0 … RA-4 and, **Δ6**, RA-E) is defined in §7.5a.6c; **R5** changed no step of this table by it.

| Step | Action |
|---|---|
| **S0** | **Δ7: entry check, before S0.** If the handle's `state` is `reaped`, `abandoned` or `reap-unknown`, **S0 is not entered: no clock is read and no `t_g` is set**; go to S1-a (and so to S7). S0 runs only for a `running` handle (CC-31, GD-4). **Otherwise:** the deadline c expired, or the flag was observed in an E wait, or a PK call finished (SN-I-3). Read **`t_g = clock() + g` once**, before any validation or send; this sets `s0_ran` and `grace_deadline_ms` (GD-1, GD-2). Nothing later reads, moves, extends or restarts it (WB-1). Go to S1. **For the PK subject skip S2 and S3**: only `SIGKILL` is sent, at S4 |
| **S1** | validate (SN-4), class X, in the order of SN-4. **Δ6:** **S1-a, a settled handle.** If `state` is `reaped`, `abandoned` or `reap-unknown`, the verdict is `not-sent(reaped)`, `not-sent(abandoned)` or `not-sent(reap-unknown)`: **no call, no wait, no further validation and (Δ7) no clock read; go to S7**. The settled-state decision was taken before SN was entered (CC-23). **S1-b, an identity rejection.** If (ii), (iii) or (iv) fails, or the handle is `identity-unverifiable`, the verdict is `not-sent(identity-mismatch)` or `not-sent(identity-unverifiable)`: **no signal of either kind is sent; go to S5**. Otherwise continue as S0 says (S2, or S4 for the PK subject). **No `not-sent` result is ever followed by a send** |
| **S2** | send `SIGTERM` (SN-I-1), one attempt, class X. Record its result and whether it returned at or after `t_g` (`late`) |
| **S3** | `R-attempt`; if reaped, **stop (go to S7): no `SIGKILL`**; **Δ6: if it raised, go to S8** (no `SIGKILL`, no sleep). Otherwise `now = clock()`. If S2 returned `sent` or `esrch` **and `now < t_g`**: `sleep(min(slice_ms, t_g − now))`, then `R-attempt`; if reaped, **stop (S7): no `SIGKILL`**; **Δ6: if it raised, go to S8**. If S2 failed, or was not made, **or `now ≥ t_g`**: **no timed wait** (WB-3). Go to S4 |
| **S4** | the child is unreaped (a **normal** return of S3's last attempt, or, for the PK subject, no attempt yet; S3 neither stopped nor raised, **Δ6**): validate again and send `SIGKILL` (SN-I-2 or SN-I-3), one attempt, class X, **at most once**. Record the result and `late`. **This step is not a wait and does not depend on the clock** (WB-4): it may begin or finish at or after `t_g`, and that is not completion within g. **Δ6:** the validation has the two branches of S1. A verdict `not-sent(identity-mismatch)` or `not-sent(identity-unverifiable)` (S1-b) **sends nothing, closes the escalation and goes to S5**. A verdict `not-sent(reaped)`, `not-sent(abandoned)` or `not-sent(reap-unknown)` (S1-a) cannot occur here by construction, because the handle is `running` after S3 (nothing has changed it since a normal return that found the child unreaped, and the PK subject has had no attempt); were it to occur it would make **no call and no wait and go to S7**. Go to S5 |
| **S5** | the loop of WB-5: `began = clock()`; `R-attempt`; if reaped, **stop (S7)**; **Δ6: if it raised, go to S8**; if `began ≥ t_g`, that attempt was the final attempt, go to S6; otherwise `now = clock()` and, **only if `now < t_g`**, `sleep(min(slice_ms, t_g − now))`; repeat |
| **S6** | the final attempt **returned normally** and found the child unreaped: abandon (SN-8) (**Δ6**), then go to S7 |
| **S7** **Δ6** | **settle, record, return.** The handle is settled: `reaped` (set at RA-3 of the attempt, or of the enclosing poll, that reaped it), `abandoned` (set at S6) or `reap-unknown` (set at S8). Write the `child` line **once**, best effort (§7.5a.9): a handle whose line was already written, or whose append failed, is not written again and **not retried**. Return the enclosing operation's own fail-closed result (`error`, `interrupted` for a flag, PK `unconfirmed`), whatever the send results, whatever partial output arrived and whichever settled state (SN-7). S7 makes **no send, no wait, no clock read and no reap attempt** |
| **S8** **Δ6** | **suppress after a `reap-error`** (RE-1 … RE-6). Reached from any reap attempt that raised: in S3, in S5 (the final attempt included), or in a poll of the enclosing wait. Set `state = reap-unknown`; record the anomaly `reap-error`, `send_suppressed: true` and, for a mutating child, `effect: "unknown"` (SN-10). **Send nothing, S4's `SIGKILL` included; make no further attempt and no sleep; read no clock and no `t_g` (Δ7: if S0 ran, the one `t_g` already read is neither moved nor extended; if S0 did not run, none exists and none is created, GD-3); search for nothing.** Keep the handle and the `Popen` object for the helper's life. Go to S7 |

**The escalation interval** is `min(slice_ms, t_g − now)` at the instant S3's sleep starts:
no parameter is added, and there is no sleep at all when `t_g` has been reached. Two
statements of R3 are withdrawn (§7.7 W-14): that everything from S0 to S6 *sits inside g*,
and that `SIGKILL` follows the first wake-up at least `slice_ms` after `SIGTERM`. The first
is false whenever a send, a validation or a reap attempt is slow; the second is false
whenever fewer than `slice_ms` of the grace remain, or none. **W_show = c + g and W_series =
P + c + g are unchanged**, and they are budgets of the helper's *scheduled waiting* (WB-6,
§7.2), not of the creation of the child, the send calls, the validation, the reap attempts
or the time at which the sequence returns.

#### 7.5a.6a The wait budget: WB-1 … WB-7 *(R4; proposed)* **Δ4**

R4-F1 found that S3 could wait beyond `t_g` after a slow send. The rules below close that
for S3 and S5 and state, once, what the budget does and does not mean. They add **no
parameter** and change no value of §7.6.

* **WB-1, one absolute grace deadline, set once.** When S0 runs, `t_g` is read once per child, at S0,
  before the first validation or send. **Δ7:** a child whose S0 never ran has no `t_g` (GD-1). It is not read again. No send, validation,
  poll, error, signal receipt, flag or abandon decision sets, moves, extends or restarts
  it, and no step begins a new grace period (WB-7).
* **WB-2, every sleep is capped.** A sleep in S3 or S5 lasts `min(slice_ms, t_g − now)`,
  with `now` read immediately before the sleep, and is started only if `t_g − now > 0`.
  **CC-10:** the same cap applies to every sleep of every E wait against **its own**
  deadline (the child wait to c, the lock loop to λ, BSP's sleeps, the PK schedule), so
  that the sum of sleeps in W_show and W_series is not exceeded by a final sleep that
  crosses its deadline.
* **WB-3, no timed wait begins at or after `t_g`.** The comparison is `≥`. A send that
  returns exactly at `t_g`, a validation that returns after it, or a clock read that shows
  it skips every later timed wait of the sequence: S3's sleep and S5's sleeps. Control goes
  to the next step that is not a wait.
* **WB-4, the escalation is not a wait and is not skipped.** The decision of S4 (a
  validated `SIGKILL`, at most once, only if the child is still unreaped) is made whatever
  the clock shows. It is a class-X call. When it happens at or after `t_g` it is recorded
  `late` and is **not** presented as completion within g, as an escalation that "ended the
  child" or as a reason to extend any wait. `SIGTERM` and `SIGKILL` may then be sent back to
  back with no sleep between them.
* **WB-5, the reap attempt and the boundary.** A *reap attempt* is exactly one
  non-blocking `reap_step()` (SI-3, `Popen.poll()`). It is class X, takes no timeout and is
  never repeated inside itself. **Δ5:** its interior is divided into the phases RA-0 … RA-4 of §7.5a.6c, **Δ6:** and RA-E for an attempt that raised. The order at every decision is: read the clock, make the
  attempt, decide. **(a) A child already settled** (handle state `reaped`, `abandoned` or, **Δ6**, `reap-unknown`) is never sent a signal, starts no wait, makes no call and ends the sequence at S7 (`not-sent(reaped)`, `not-sent(abandoned)`, `not-sent(reap-unknown)`, SI-4, S1-a). It is **not** sent to S5, which only an identity rejection reaches (S1-b). **(b) A child
  that exits during a send, a validation or a sleep** is a zombie that still pins its numbers
  (SI-2); the send result is recorded as returned (`sent`, `esrch` or an error); the next
  reap attempt reaps it; if that attempt precedes S4, **no `SIGKILL` is sent**; if the exit
  falls inside the `SIGKILL` call, the next attempt reaps it. **(c) A child still unreaped
  when `t_g` is reached:** the reap attempt **of S5** that **begins** at or after `t_g` is the
  *final attempt*. It is made after any S4 send, so a `SIGKILL` that falls after `t_g` is
  always followed by one more attempt before the abandon. An attempt of S3 that begins at or
  after `t_g` is not final. If it reaps the child, the state is `reaped` with the benign anomaly
  `reaped-at-or-after-deadline`, and the enclosing result is unchanged (it is the E wait's
  fail-closed result). If not, S6 abandons the child. **No timed wait follows the final
  attempt.** **(d)** A child that exits at the instant of the final attempt may be reported
  either way; both lead to a fail-closed enclosing result and a record, and the state follows the attempt's result only. **(e) Δ6: an attempt that raises** is neither a reap nor an unreaped return: it goes to S8, starts no wait, and **no signal follows it** (RE-1).
* **WB-6, the budget is not elapsed time.** The **wait budget** of a signalled child is
  the total of its scheduled sleeps in S3 and S5. By WB-1 … WB-3 each sleep is at most the
  time then remaining to `t_g` and the sleeps are sequential, so **their total is at most
  g**. W_show and W_series are budgets of that kind. The **elapsed procedure time** from S0
  to the return is the scheduled sleeps **plus** every validation, send call, reap attempt,
  journal append and record write **plus** the lateness of the sleeps themselves, and **no
  bound is claimed for it**. It may exceed g: a send may consume more than g, S4 may follow
  `t_g`, and the final attempt follows it. **No send, validation, reap attempt or other
  class-X operation acquires a time bound from the budget, and no sizing rule (N1 … N4)
  becomes a completion guarantee.**
* **WB-7, nothing starts another grace period.** A send error, `ESRCH`, `EINTR`, a
  validation failure, a poll, the receipt of a signal (the flag), a PID 1 delivery and an abandon decision do not read a new `t_g`, do not add to the budget and, apart from the single escalation of S4, cause no further send (SN-3). **Δ6:** a **reap-attempt exception** reads no new `t_g`, adds nothing to the budget and causes **no further send of any kind, S4's escalation included, and no further wait** (RE-1, RE-4). R5's wording, which let the escalation follow a reap-attempt exception, is withdrawn (W-16).

#### 7.5a.6b The same sequence in a table of cases *(an aid to review; WB-1 … WB-7 govern)*

`g = 2,000 ms` and `slice_ms = 100` are the recommended values of §7.6. The costs are
illustrative, not claims.

| Case | Costs (S2's send unless stated) | After S2 | Scheduled sleeping | S4 | Return |
|---|---|---|---|---|---|
| a send under g | 300 ms | `t_g − now = 1,700`; the child ignores `SIGTERM` | one sleep of 100 ms in S3; sleeps of 100 ms each in S5 until `t_g` | `SIGKILL` after S3's sleep, not `late` | the final attempt at or just after `t_g`; abandon if unreaped. Total sleeping ≤ 2,000 ms |
| a send at g | exactly 2,000 ms | `now = t_g` | **none**: S3 and S5 skipped | `SIGKILL` at once, `late` | R-attempt, S4, the final attempt: reaped or abandoned. Total sleeping 0 |
| a send over g | 2,500 ms | `now > t_g` | **none** | `SIGKILL` at once, `late` | as above. Elapsed time exceeds g; no statement is violated (WB-6) |
| less than a slice left | 1,960 ms | `t_g − now = 40` | one sleep of **40 ms** in S3, not 100 | `SIGKILL` after it | the final attempt at `t_g` |
| a slow S1 validation **Δ5** | S1 costs 2,100 ms; S2 and S4's sends cost 20 ms each; reap attempts cost 0 | `now ≥ t_g` before S2 is made; S2 returns at 2,120 ms, `late` | **none**: S3 and S5 skip every timed wait | `SIGKILL` at once after S3's reap attempt, `late` | S5's final attempt: reaped or abandoned. Total sleeping 0 ms. Both sends `late` |
| a slow S4 validation **Δ5** | S1 costs 10 ms; S2 costs 20 ms and returns at 30 ms, **not** `late`; S4's second validation costs 2,100 ms; the `SIGKILL` costs 20 ms | at S3 `t_g − now = 1,970`; the child ignores `SIGTERM` | **one sleep of 100 ms in S3**, begun at 30 ms, before `t_g` and allowed; S5: **none** (its first attempt begins at 2,250 ms, at or after `t_g`) | the validation returns at 2,230 ms, at or after `t_g`; `SIGKILL` is still sent (WB-4), returns at 2,250 ms, `late` | the final attempt at or after 2,250 ms: reaped or abandoned. Total sleeping 100 ms. `SIGTERM` is **not** `late`, `SIGKILL` is |
| a failed `SIGTERM` | any | `errno` | none in S3 (no timed wait after a failure) | at once, after one R-attempt | S5 as `t_g` allows |
| a successful `SIGTERM`, the child exits | 100 ms | reaped by S3's R-attempt | at most one sleep of 100 ms | **not sent** | `reaped` |
| the child exits at the boundary | any | exit between the last sleep and `t_g` | as the case | as the case | the final attempt reaps it: `reaped` with `reaped-at-or-after-deadline` |
| S1-a: the handle is already `reaped` **Δ6** | none: no validation cost, no call | no S2 | **none** | **not sent** | S7 only: the `child` line is written once; the enclosing result is unchanged. Sends 0, sleeps 0 |
| S1-b: `not-sent(identity-mismatch)` **Δ6** | S1 costs 10 ms and rejects | no S2 | S5 only: capped sleeps while `t_g` has not been reached | **not sent**: no signal of either kind | the final attempt at or after `t_g`: reaped or abandoned. Sends 0 |
| a `reap-error` at S3 **Δ6** | S1 costs 10 ms; S2 costs 20 ms and returns `sent`; S3's first attempt, at 30 ms, raises | S8 at once | **none** (no S3 sleep, no S5 sleep) | **not sent** (RE-1) | S7: `reap-unknown`, one `SIGTERM`, no `SIGKILL`; the enclosing result is `error`; no abandon |
| a `reap-error` at S5, or at the final attempt **Δ6** | as the slow-S4 sequence up to a normal attempt of S5 | S8 at once | the sleeps made before the error only, none after it | the one `SIGKILL` already sent is history; none follows | S7 as above |
| a `reap-error` before S0 **Δ7** | no SN: a wake-up poll of the **enclosing** wait, at 1,000 ms of its c = 5,000, raises; no deadline has expired and no flag is set | S8 at once, **S0 never ran** | none after the error | **not sent**; no `t_g` read, none created | S7: `reap-unknown`, `sends: []`, `grace_deadline_ms: null`, `s0_ran: false`, `outcome: "reap-error"`; the enclosing result is `error`; no abandon (§7.5a.6e) |

#### 7.5a.6c The boundary of a reap attempt: RA-0 … RA-4, RA-E and RB-1 … RB-5 *(R5; amended and in part replaced in R6)* **Δ5** **Δ6**

R5-F1 found that the interruption map had no state for a helper that is ended inside a reap
attempt after the kernel has reaped the direct child, and that T6, which begins after the
sequence has decided, cannot cover it. This subsection defines the interior of one attempt.
It adds **no parameter, no wait, no send and no class**, and changes no step of table SN-S. **R6 (Δ6)** adds the phase RA-E and amends RB-1 … RB-4; RB-5 is replaced by RE-1 … RE-6 (§7.5a.6d); the steps S7 and S8 and the two branches of S1 are in table SN-S.

| Phase | The attempt is at | The kernel and the direct child | Handle `state` | Durable `child` line | Interruption point (§7.9) |
|---|---|---|---|---|---|
| **RA-0** | **before the `waitpid` call**: the clock read that precedes the attempt (WB-5), and any step between the previous action and the call | not reaped (alive, or exited and unreaped) | `running` | none | **T3** (an attempt of S3) or **T5** (an attempt of S5, the final attempt included) |
| **RA-1** | **inside the call, before the kernel has reaped**: the call has not yet consumed a status, or it has returned "not yet exited" and the attempt has not yet returned | not reaped | `running` | none | T3 or T5 |
| **RA-2** | **after the kernel reap, before the handle-state update**: the kernel has consumed the status (the child is reaped in the kernel) and `reap_step()` has not yet set `state = reaped` | **reaped** | **`running`, stale** | none | **T3k** (S3) or **T5k** (S5, the final attempt included) |
| **RA-E** **Δ6** | **the attempt has raised, before the handle-state update**: `Popen.poll()` raised and the helper is at the start of S8, which has not yet set `reap-unknown` | **not known**: not reaped (the exception came before any kernel reap) or reaped in the kernel (it came after) | `running`, not known to be exact | none | **T3x** (S3) or **T5x** (S5, the final attempt included) |
| **RA-3** | **after the handle-state update, before the durable line**: `reap_step()` has set `state = reaped` and the exit status in the handle (**Δ6:** or S8 has set `reap-unknown` after an attempt that raised); the sequence has **decided** | reaped (**Δ6:** for `reap-unknown`, not known) | `reaped` (**Δ6:** or `reap-unknown`) | none | **T6** |
| **RA-4** | **after the durable line**: the `child` line is durable | reaped | `reaped` | durable | **T7** |

* **RB-1, phases.** An attempt has the phases below in this order (**Δ6:** RA-E is the phase of an attempt that raises, and takes the place of RA-2 for it). An attempt that finds
  the child unreaped passes RA-0 and RA-1, returns, and never reaches RA-2: the sequence continues (S3: the capped sleep or S4; S5: the capped sleep or S6). **Δ6:** an attempt that **raises** passes RA-0 and RA-1, may or may not have crossed the kernel's reap (the design cannot tell, RE-2), and is at RA-E until S8 sets `reap-unknown` (RA-3); it is not RA-2, which is a normal return. The boundary between
  RA-1 and RA-2 is the kernel's own act inside the `waitpid` call. **The design cannot
  observe it; a test harness can** (NT-IS-16), which is why RA-1 and RA-2 are separate
  rows even though both lie inside one call.
* **RB-2, where the kernel reaps.** The kernel reaps a direct child only inside a reap
  attempt: `reap_step()` is the sole reaper (SI-3, resting on PO-SN (c) and (f)). T1, T2
  and T4 contain **no reap attempt**, so no child *becomes* reaped there. **One
  qualification:** the polls of the **enclosing E wait** (§7.3 row 2) are reap attempts with
  the same five phases, and they **precede T0**. A child that such a poll reaped is already reaped when SN is entered (table SN-R row 3, NT-SN-5 (a)). **Δ6:** its settled-state decision was RA-3 of that poll, **before SN**: a helper ended from then until S7 has written the line is at **T6** (CS-5), after the line at **T7** (CS-7), and **T0 and T1 are never entered for it** (CC-23). A helper ended inside such a poll at RA-2 leaves CS-5, and at RA-E leaves CS-9, with **no SN point**, because SN has not been entered; a poll that raised sets `reap-unknown` and the wait ends at once through S8 and S7 (RE-1).
* **RB-3, no act inside the window.** Between RA-2 and RA-3 the helper makes no
  validation, no send, no wait, no record and no clock-dependent decision: the main thread
  is inside the attempt, and a handler only sets the flag (SG-2, SG-9). The stale `running` state is therefore never used to send (SI-3). **Δ6:** the same holds from the raise to S8's state update (RA-E): S8's first act sets `reap-unknown`, and nothing precedes it.
* **RB-4, the mapping to points.** **T3 and T5 are the spans of S3 and S5 while the direct
  child is not reaped in the kernel**: RA-0, RA-1, and the sleeps, clock reads and decisions
  between attempts. **T3k and T5k are RA-2** of an attempt of S3 and of S5, the final
  attempt included. **T6 begins at RA-3**, the handle-state update by an attempt that
  reaped the child, **or at the abandon decision of S6, and never earlier**: an
  interruption inside an attempt is never T6. T7 begins at RA-4. An interruption at RA-0 or RA-1 of the final attempt is T5, whatever the attempt would have found. **Δ6:** **T3x and T5x are RA-E** of an attempt of S3 and of S5 (the final attempt included). T6 also begins at the suppression decision, S8's update of the handle to `reap-unknown`, and an interruption inside S8 before that update is T3x or T5x, never T6. A handle already settled when SN is entered is at T6 or T7, never at T0 or T1 (CC-23).
* **RB-5, an attempt that raises (replaced in R6, Δ6).** R5 left this open, read the raised
  attempt as unreaped and made the question an AP-0 gate. R6 closes it by **RE-1 … RE-6**
  (§7.5a.6d): an attempt that raises is neither a reap nor an unreaped return, and the design
  sends nothing after it, whatever the kernel did inside the call. Whether `Popen.poll()` can
  raise after `waitpid` has consumed the status is **evidence only** (PO-SN (c′), Q18) and no
  longer decides anything. R5's sentences that left row 3g, S4 and SN-4 unchanged for it, and
  that made PO-SN (c) an AP-0 gate for it, are withdrawn (W-16).

#### 7.5a.6d The reap error: RE-1 … RE-6 *(R6; proposed)* **Δ6**

R6-F1 found that a reap attempt that raised was read as *unreaped*, so the sequence could go on
to validate and send a root `SIGKILL`, although the kernel may already have consumed the child's
status and released its PID and process-group number. This subsection makes the design **safe
for either truth**. It adds **no parameter, no wait, no class and no send**, and it **removes**
one send (S4 after a `reap-error`). It decides nothing from CPython behaviour: the helper cannot
see which truth holds, so it does what is safe under both.

| If the attempt raised … | the direct child | its PID and group number | what the design does after the error |
|---|---|---|---|
| **before** the kernel reaped (the exception came first) | not reaped: alive, or exited and unreaped; **pinned** (SI-2) | pinned | nothing is sent; no attempt; no sleep; `reap-unknown`; record; the enclosing fail-closed result |
| **after** the kernel reaped (the call consumed the status, then raised) | **reaped in the kernel** with no handle update | **may be released, and may be reused** by an unrelated process or group | **the same: nothing is sent.** No signal can reach a reused number, because none is sent |

The two rows have the **same** action. The design therefore needs no answer to the question
which row is true, and it has no observable difference between them (RE-2).

* **RE-1, fail closed after any `reap-error`.** The first `reap-error` of any reap attempt of a
  child (in S3, in S5 including the final attempt, or in a poll of the enclosing E wait) takes
  the child to `reap-unknown` (S8). **From then on this helper sends no signal of any kind to
  that child:** not `SIGTERM`, **not S4's `SIGKILL`** (including when `SIGTERM` was sent and the
  escalation was still to come), no signal through any other primitive (SN-5), no retry, and
  no search for the process (SN-9, LD-9). The at-most-once rule (SN-3) is unchanged: sends
  already attempted are history, and none is added. **No validation, no send decision and no
  `SIGKILL` follows an attempt that raised.**
* **RE-2, the state `reap-unknown`.** It says only that the helper does **not know** whether the
  direct child is still unreaped or was reaped in the kernel with no handle update, because the
  attempt raised and nothing the helper holds tells which. **It is not labelled `reaped`,
  `unreaped` or `abandoned` as a fact**, no later step reads it as any of them, and neither the
  exception nor the absence of an exception is evidence of either truth (SN-7). A later
  observer sees a durable line with `reap_unknown: true` (CS-10) or no line (CS-9) and learns
  neither truth (IS-10).
* **RE-3, the handle and the `Popen` object are kept.** The child handle and its `Popen` object
  stay referenced for the helper's remaining life (as SN-8 (c)), so that no destructor or
  interpreter cleanup decides anything on the helper's behalf. **No further `poll()` of that
  object is made** (it would be a retry), and the handle's state never leaves `reap-unknown`:
  not to `running`, `reaped` or `abandoned`.
* **RE-4, no new wait and no new grace.** S8 starts no wait and no sleep and reads no new
  `t_g`; whatever remains of the one absolute `t_g` is left unused (WB-1, WB-7). **Δ7:** if S0 had not run (a raise in a poll of the enclosing wait), **no `t_g` exists, none is read and none is created**: there is nothing to leave unused, and `grace_deadline_ms` is `null` (§7.5a.6e). WB-1 … WB-4
  and WB-6 are unchanged. `waits_skipped` is set to true if a timed wait of S3 or S5 would
  otherwise have followed; that is an observation, not a claim. **Δ7:** it is `false` before S0, where no wait of S3 or S5 is pending.
* **RE-5, record, result and owner.** S7 records the anomaly `reap-error`, `reap_unknown: true`, **(Δ7: and `s0_ran` and `grace_deadline_ms` as GD-2 states them)**,
  `send_suppressed: true`, `reaped: false`, `abandoned: false` and `sends` as attempted, and, for
  a mutating child (`systemd-run`, `systemctl stop`), `effect: "unknown"` (SN-10): no step reads
  that as "not created" or "not stopped". **The enclosing operation returns its existing
  fail-closed result** (`error`; `interrupted` for a flag; PK `unconfirmed`), whatever the send
  results and whatever partial output arrived (SN-7). A PK subject that is `reap-unknown` is
  signalled no further and lives at most 60 s. **No later procedure acts on or searches for the
  child** (SN-9). Its owner is the owner of its enclosing procedure (table SN-RO), the boot is a
  separate recovery event, and the interactive `attest` has no automatic owner: all unchanged
  from R5. The line is written once, best effort (S7); a helper ended before it leaves CS-9,
  and the next procedure records `children-unknown` (§7.5a.9).
* **RE-6, the CPython question is evidence, not a precondition.** Whether `Popen.poll()` can
  raise at all, and if it can whether it can do so **after** `waitpid` consumed the status, is
  PO-SN (c′) (§7.5a.8). **No decision of the design depends on the answer.** If it can raise
  after the kernel's reap, RE-1 sends nothing; if it cannot, RE-1 sends nothing either, because
  the helper has no way to read the answer at run time and does not condition on it. AP-0 does
  not read (c′), and **no answer to it can make AP-0 pass a branch that sends after a
  `reap-error`, because no such branch exists.**

**Why no process-group number is exposed.** Every send of the design is made while the handle
is `running` and exact (SI-3, RB-3), which the helper knows only because the last attempt
returned **normally** and found the child unreaped, or because no attempt has yet run. A
`reap-error` is the one event that can make that knowledge false, and S8 makes the helper's
ignorance permanent from that instant: the set of sends made after a possible release of the
number is **empty**. SN-4's validation is not part of this argument and stays a detector (SI-2).
The sends made **before** the error were made while the child was pinned.

#### 7.5a.6e The grace deadline exists exactly when S0 ran: GD-1 … GD-5 *(R7; proposed)* **Δ7**

R7-F1 found that a `reap-error` raised in a poll of the **enclosing E wait** goes to S8 and S7
(RE-1) **before** a deadline or the flag has triggered SN, so **S0 has not run and no `t_g`
exists**, while R6's record required `grace_deadline_ms` for every child, INV-22 said each
child has one grace deadline, and NT-RE-11 asserted one `t_g` read. The same held for a child
that exits within c and for one whose creation failed. This subsection states one
representation. It adds **no parameter, no wait, no send, no class and no grace period**, and
every sequence in which S0 ran is exactly as WB-1 … WB-7 and table SN-S say.

| Path | S0 ran | `t_g` reads | `s0_ran` | `grace_deadline_ms` | `outcome` | `sends` |
|---|---|---|---|---|---|---|
| a child exits within c: the enclosing wait's poll reaps it normally (RA-3 of that poll); SN is never entered | no | **0** | `false` | `null` | `exited` | `[]` |
| `spawn()` failed; there is no child | no | **0** | `false` | `null` | `spawn-failed` | `[]` |
| **a poll of the enclosing wait raises (RA-E, then S8, S7)** | **no** | **0** | `false` | **`null`** | **`reap-error`** | `[]` |
| SN is called on a handle that is already `reaped`, `abandoned` or `reap-unknown` (S1-a, S7); this includes a **later** call on the handle of the previous row | no | **0** | `false`, **or `true` with the integer already recorded if the handle was abandoned after an S0** | `null`, or the integer already recorded | as the enclosing wait or the earlier sequence set it | as already made |
| S0 ran, and any later path: S1-b, S2 … S7, an abandon, a raise at S3, S5 or the final attempt (S8) | **yes** | **exactly 1** | `true` | an integer | `expired` or `interrupted` (PK: as R6) | as made |

* **GD-1, `t_g` exists exactly when S0 ran.** S0 runs at most once per child, only for a
  `running` handle at SN's entry (GD-4). Before S0 the child has no `t_g`. After S0 it has exactly
  one, read once, never moved, extended or restarted (WB-1, WB-7, unchanged). **No code path
  reads, sets or derives a grace deadline except S0.** A pre-S0 `reap-error` reads it **zero**
  times.
* **GD-2, one representation, machine-checkable.** In every `children` entry the key
  `grace_deadline_ms` is **always present** and the key `s0_ran` is always present and boolean.
  `grace_deadline_ms` is the integer instant of `t_g` **if and only if** `s0_ran` is `true`, and is
  JSON `null` otherwise. It is **never omitted, never `0`, never negative and never a
  placeholder**: `0` would read as a deadline long past, and an omitted key would make the schema
  conditional on a field that the reader cannot see. The schema check is one line,
  `s0_ran == (grace_deadline_ms != null)`, and these implications are checked with it:
  `sends != [] ⇒ s0_ran`; `waits_skipped ⇒ s0_ran`; `abandoned ⇒ s0_ran`; any `late` entry ⇒
  `s0_ran`; `outcome == "reap-error" ⇒ ¬s0_ran`.
* **GD-3, what a path without S0 reads and starts.** It reads **no `t_g`** and **no clock for the
  record**: S8 and S7 read no clock (S7 already made none), and the `start_ticks`, `created_ms` and
  `deadline_ms` of the entry are the values captured when `spawn()` created the child, not read
  again. It enters no S0, starts no grace period, sends nothing and makes no further poll, wait or
  search. The enclosing E wait's own clock reads before the raising poll belong to that wait (its
  capped sleeps, WB-2); none follows the raise, and none is a `t_g` read.
* **GD-4, S0 is entered only for a `running` handle (CC-31).** A handle that SN finds `reaped`,
  `abandoned` or `reap-unknown` goes from SN's entry to S1-a and S7 **without S0 and without a clock
  read**. A **later** SN call on the handle of a pre-S0 `reap-error` therefore does not create a
  `t_g` after the record was written with none, and S7 does not write the line again (it is
  written once, S7). R6 listed S0 before S1 for every handle, so a call on a settled handle read a
  `t_g` that nothing used; R6's handback left that question open, and R7 closes it here.
* **GD-5, nothing else changes.** `waits_skipped` is `false` before S0. The sends, the waits, the
  escalation, S1 … S8 after S0, the absolute `t_g` of every sequence in which S0 ran, the
  remaining-time caps and the at-most-once rule are as in R6.

**The pre-S0 `reap-error`, step by step (the case NT-GD-1 follows).** A child has been created and
its handle is `running`, with `created_ms` and `deadline_ms` set at creation, `s0_ran` false and no
`t_g`. The enclosing E wait is at a wake-up and polls the child (a reap attempt, RB-2).

1. The poll raises. The helper is at RA-E (a helper ended here leaves CS-9, with no SN point, RB-2).
   No deadline need have expired and no flag need be set. If S0 **had** already run for this child
   the path is a post-S0 one, with an integer `t_g`; **the distinction is whether S0 ran, not where
   the poll stood**.
2. **S8:** `state = reap-unknown`; anomaly `reap-error`; `send_suppressed: true`; for a mutating
   child `effect: "unknown"` (SN-10). No send, no further poll, no sleep, no clock read, no `t_g`.
3. **S7:** the `child` line is written once, best effort, never retried, with: `role`, `argv0`,
   `pid`, `pgid`, `start_ticks` and `deadline_ms` as captured at creation; **`s0_ran: false`;
   `grace_deadline_ms: null`; `outcome: "reap-error"`; `sends: []`; `waits_skipped: false`;**
   `reaped: false`; `abandoned: false`; `reap_unknown: true`; `send_suppressed: true`;
   `last_signal: null`; `effect: "none"` or `"unknown"`; `anomalies: ["reap-error"]`. The enclosing
   operation returns its fail-closed result (`error`; PK `unconfirmed`), whatever partial output
   arrived (SN-7).
4. **Counts for the whole path:** `t_g` reads **0**; clock reads by SN **0**; sends **0**; sleeps
   after the raise **0**; further polls **0**; process searches **0**; grace periods started **0**.

#### 7.5a.7 Who owns a child that is left behind: table SN-RO **Δ4**

"Owner" is the first party that can end the child **by an act of its own**. Ownership
follows the **enclosing procedure**: the helper that created the child and that either abandoned it (SN-8), suppressed it after a `reap-error` (RE-1, **Δ6**) or was ended before it could decide (§7.9). **The owner does not
depend on any send result** (IS-5). Nobody acts on the child in the procedure that
abandoned it (SN-8 (g)), nobody hunts it later (SN-9), and a helper that has ended makes no
further send.

| Enclosing procedure | Where it runs | Owner of the child | Signals from others (class **M**; delivery, never proof) | Status of the basis |
|---|---|---|---|---|
| the holder (ACT, HL, AV-1) | the holder unit's control group | PID 1's stop of the holder unit (`RuntimeMaxSec=`, a stop job, the main process's end): its cleanup may signal what remains in the unit | PID 1's `SIGTERM` and `SIGKILL` to the unit's remaining processes at that stop, while PID 1 can act (RO-3) | class **M**; the cgroup membership of a child that called `setsid`, and the `KillMode=` default, are *[N, PO-SN (e)]* |
| CP | the capture unit's `start-pre` step | PID 1's end of the attempt (the start timeout, the helper's end, a stop), as above | as above | as above |
| stop-post CL | the holder unit's stop-post | `FINAL_SIGTERM`, then `FINAL_SIGKILL` after another S, which signal "what remains" **[R2 §8 (e), established]** | those two | the *what remains* wording is established; that it includes a `setsid` child is *[N, PO-SN (e)]* |
| backstop service (CL, BS-1 … BS-3) | the backstop service | the end of the service (BS-RM's `RuntimeMaxSec=` or its exit), as above | PID 1's signals at the service's end | as above; BS-RM is proposed (§7.4) |
| **`attest`** | an interactive `sudo` session; **no unit** | **no automatic owner is claimed.** The design neither relies on nor denies any signal that the end of an interactive session may cause, because nothing in it could show that such a signal happened. The helper records `children` if it can (§7.5a.9); the executor reports the record, or `children-unknown`, and **does not act** (SN-9, Appendix B-13) | none claimed | n/a. **This is the one procedure with no automatic owner, and it is retained as such (R4-F2 item 4)** |

**The boot is a separate recovery event** for every row (RL-4). It ends every process on
the host. It is **not evidence** that a signal was sent, that a signal succeeded, that the
child exited before it, or that a state was reached by any act of this design, and no
record is marked `signalled`, `exited` or `reaped` on its basis (IS-7, INV-20).

#### 7.5a.8 Proof obligations PO-SN *(proposed [N]; none is cited, none is run)*

The accepted OH-S2 R2 record and the one-host design were searched by fixed string in
R3 for `killpg`, `os.kill`, `kill(`, `ESRCH`, `pidfd`, `start_new_session`, `setsid`,
`process group`, `SIGCHLD`, `KillMode` and `control-group`. **No accepted record cites
any of the first nine as a behaviour.** The record cites `FINAL_SIGTERM` and
`FINAL_SIGKILL` "to what remains" and the defaults at `kill.c:13–16` [R2 §8 (e)]; it
lists `KillMode` only as a property row. The obligations below are therefore proposed,
**bound to the observed versions** (the HF-04 kernel series, `7.0.0-31-generic`; `libc6`
`2.43-2ubuntu2.4`; `python3.14-minimal` `3.14.4-1ubuntu0.2`; systemd
`259.5-0ubuntu3.4`), and join the OH-S2b citation step (§11, slice 2a). The source
files named are **proposed citation targets, not read here**.

| ID | Obligation | Needed by | Status |
|---|---|---|---|
| **PO-SN (a)** | `kill`/`killpg` semantics: return 0 when the signal is permitted and queued for at least one process of the target group; `ESRCH` when no such process or group exists; `EPERM` when no target may be signalled; `EINVAL` for an invalid signal; the call does not wait for the target to act; a signal to a zombie is accepted and has no effect; `SIGKILL` cannot be caught, blocked or ignored but is not acted on by a process in an uninterruptible call until it leaves it; `SIGTERM` can be ignored; CPython's `os.killpg` raises `OSError` subclasses from the errno and whether it retries `EINTR` | SN-1, SN-3, table SN-R | proposed; targets `kernel/signal.c` and `Modules/posixmodule.c` |
| **PO-SN (b)** | PID and process-group number non-reuse: a PID number is not assigned to a new process while it is the PID of an unreaped process (a zombie included), nor while it is the PGID or SID of any existing process | SI-2, the whole reuse defence | proposed; targets `kernel/pid.c` and `kernel/exit.c`. **If not accepted, the SN contract is not adopted and AP-0 is INVALID RUN** |
| **PO-SN (c)** **Δ6** | CPython 3.14.4 `subprocess.Popen` on POSIX: `start_new_session=True` runs `setsid()` in the child before `exec`; `Popen()` returns only after the child has `exec`ed or failed; `close_fds=True` closes every descriptor ≥ 3 before `exec`; `Popen.poll()` is a non-blocking `waitpid` that reaps; what `Popen.__del__` and the interpreter's own cleanup do with a running child. **(R5's clause on a post-reap exception is moved to (c′).)** | SI-1, SI-3, SN-8 (c) and (e), RB-2 | proposed; targets `Lib/subprocess.py` and `Modules/_posixsubprocess.c` |
| **PO-SN (c′)** *(evidence only; R6 Δ6)* | CPython 3.14.4 `Popen.poll()`: whether it can raise at all and, if it can, whether it can raise **after** `waitpid` has consumed the exit status, and what it then leaves in the `Popen` object (the return code, the PID). **No decision of the design depends on the answer** (RE-6): after any `reap-error` nothing is sent, on either answer | RE-6; Q18; the wording of the record only | proposed; target `Lib/subprocess.py`. **Not an AP-0 condition.** A citation that establishes *post-reap exceptions are possible* is accepted as evidence and makes nothing unsafe; one that establishes *not possible* licenses no send after a `reap-error`; one that establishes neither leaves the design unchanged |
| **PO-SN (d)** *(optional)* | `/proc/⟨pid⟩/stat` field 22 (`starttime`) is readable for an unreaped zombie, is fixed for a process's life, and the record must be parsed after the last `)` because `comm` may contain spaces and `)` | SN-4 (iv) only | proposed; target `fs/proc/array.c`. **If not accepted, SN-4 (iv) is removed. The safety claim does not rest on it** (SI-2 does) |
| **PO-SN (e)** | systemd's cleanup of a service's control group: at a unit's stop the processes remaining in its control group are signalled according to `KillMode=` (default `control-group`) and `SendSIGKILL=` (default yes); a process that called `setsid` stays in its cgroup | table SN-RO; RO-7 | proposed; targets `src/core/kill.c`, `src/core/service.c`. [R2 §8 (e)] establishes only `FINAL_SIGTERM`/`FINAL_SIGKILL` "to what remains"; whether `kill.c:13–16` is the `KillMode` default is for OH-S2b to confirm |
| **PO-SN (f)** | a process's `SIGCHLD` disposition: the default does not reap children automatically; an explicit `SIG_IGN` or `SA_NOCLDWAIT` does; CPython's startup leaves the default | SI-3, SG-3 | proposed; target `kernel/signal.c` |
| **PO-SN (g)** *(optional; R4 Δ4)* | when a process ends, its children are reparented (to PID 1 or the nearest subreaper), keep their process group, session and cgroup, and an exited child is reaped by its new parent; the end of the parent signals no child | §7.9 only, as a description of why a child may outlive its helper. **Nothing relies on it** | proposed; targets `kernel/exit.c`. **If not accepted, §7.9 stands as written**: it already says that the fate of a child after its helper ends is unknown to the design |

**AP-0 is INVALID RUN unless PO-SN (a), (b), (c), (e) and (f) are accepted for the observed versions, and no lock object is created.** (d) and (g) are optional, and **(c′) is evidence only: AP-0 does not read it** (**Δ6**), and no answer to it can make AP-0 pass a branch that sends after a `reap-error` (RE-6).

**Where a Route 3 outcome removes Python from a root procedure,** SN-1 … SN-10 and
SI-1 … SI-4 apply to the replacement unchanged, and PO-SN (c) is replaced by the
replacement's own `clone`/`setsid`/`wait4` behaviour. That is part of WP-2, WP-3 and
WP-4 (§9.5). It is a reason the hard stop is not weakened.

#### 7.5a.9 Records

Each child yields one entry in the record key `children` (§8.5) and, where the journal
exists, one best-effort `child` journal line (an `ext4` append, class X: a failed or
stalled append changes no result and is itself recorded as a gap). Entries made
before the journal exists are held in memory (at most 64 entries and 64 KiB) and
flushed in order; beyond that a counter `overflow` is kept. Fields: `role`, `argv0`,
`pid`, `pgid`, `start_ticks`, `deadline_ms`, **`s0_ran`** (boolean, **Δ7**), **`grace_deadline_ms` (`t_g`: an integer iff `s0_ran`, otherwise `null`, never omitted; GD-2, Δ7)**, `outcome` (`exited`, `expired`,
`interrupted`, `spawn-failed`, and, **Δ7**, `reap-error`, only when `s0_ran` is false), `sends` (signal, result, offset, **`late`**), **`waits_skipped`
(true when at least one timed wait was skipped because the clock showed `t_g` reached,
WB-3)**, `reaped`, `abandoned`, **`reap_unknown`** and **`send_suppressed`** (**Δ6**: both false unless S8 ran; when `reap_unknown` is true, `reaped` and `abandoned` are false), `last_signal`, `effect` (`none` or `unknown`) and `anomalies` (including **`reaped-at-or-after-deadline`**, **`reap-error`**). **Elapsed
times in them are observations, never claims, and `late` is an observation, not a
failure.** PIDs are evidence only (SN-9).

**The line is written once, after the child is settled (reaped, abandoned or, Δ6, `reap-unknown`). Δ4** A
helper that ends earlier leaves no `child` line for that child (states CS-1 … CS-6 of §7.9, and **CS-9, Δ6**). The record of what was attempted then exists only in the dead helper's memory,
and **no later procedure can know which child, how many, or what was sent**. **Δ5:** CS-5 is in that set. A direct child that the kernel reaped
inside an attempt that the helper's end cut short (T3k, T5k), and one whose reap the helper
held only in memory (T6), leave no line; a later procedure sees **no reap fact** for either,
records only `children-unknown` (below), and does **not** read the missing line as *reaped*,
*exited*, *alive* or *the group is empty* (IS-9). **Δ6:** the same holds for CS-9, a child whose reap attempt raised and whose helper ended before S7 wrote the line: the next procedure records only `children-unknown` and reads neither *reaped*, *unreaped*, *alive*, *gone* nor *the group is empty* from it (IS-10). What a later
procedure *can* see is that the interrupted procedure's own journal lacks its terminal
line (for the holder, `hold-end`; for a CL attempt, `run-end`). It then records the
condition **`children-unknown {helper_role, missing_terminal_line}`** in its `deact`
record: a recorded **gap**, not a count, not a hypothesis about any send, and never a
reason to search for a process (SN-9). Which terminal line marks a helper's complete end
is a confirmation item for OH-S0d (A-I-17).

#### 7.5a.10 What §7.5a does not claim

It claims no elapsed time for a send, a validation, a reap attempt or the sequence, and
**no claim that the sequence returns within g** (**Δ4**, WB-6): g bounds the helper's
scheduled sleeping, and the sequence may return after `t_g`. It claims no
kernel guarantee beyond PO-SN (b), which is proposed and, if refused, ends the
contract. It does not claim that any send succeeds, that a signalled process exits, or
that an abandoned child is gone. It does not change the safety kernel, PO-11 (d′), the
accepted Route 3 boundary or the Route 3 hard stop.

### 7.6 Parameters and the sizing rules N1 … N4

| Name | Meaning | Grammar | Recommended |
|---|---|---|---|
| `pk_op_ms` (**P**) | the interval in which a PK/2 series may **start** calls | 5,000 … 60,000 | 30,000 |
| `pk_call_ms` (**c**) | deadline of one child wait (a PK call, a `systemctl show`, a `systemd-run`) | 1,000 … 10,000, and c ≤ P | 5,000 |
| `reap_grace_ms` (**g**) | the **wait budget** for a *signalled* child: the total of scheduled sleeping for its reaping (SN-6, WB-6), from one `t_g` read before the first send or validation, after which the child is abandoned **Δ3** **Δ4**. It is not a bound on the time to return | 500 … 5,000 | 2,000 |
| `lock_wait_ms` (**λ**) | CL's lock acquisition deadline (LD-5) | 1,000 … 10,000 | 5,000 |
| `slice_ms` | the longest interval between flag checks inside any E wait | 50 … 250 | 100 |
| `stop_timeout_s` (**S**) | the holder's `TimeoutStopSec=`; also the backstop service's | 60 … 600 | 120 |
| `bs_runtime_s` (**S_b**) | the backstop service's `RuntimeMaxSec=` (BS-RM) | 60 … 600 | 120 |
| `backstop_period_s` (**R**) | the backstop timer's period | 30 … 600 (as accepted) | 60 |
| `backstop_max` (**B**) | the most firings that run CL before the backstop disarms | 1 … 99 | 20 |
| `reserve_ms` (**ρ**) | the allowance for class-X work in the sizing rules. **An expectation, not a bound** | ≥ 30,000 | 30,000 |
| `act_wait_s` | the executor's deadline in AP-2 | 60 … L | L |
| `journal_max_bytes` | volume cap for any journal read | 65,536 … 4,194,304 | 1,048,576 |
| `start_window_s` (W), `lease_s` (L), `poll_ms` (Δ) | unchanged | as accepted | as accepted |

Define **W_show = c + g** and **W_series = P + c + g** (**Δ4:** budgets of *scheduled
waiting*, WB-6, not of elapsed time). The **sizing rules** are
*necessary* conditions that AP-0 evaluates. **A set that violates one is refused,
because the deadline-enforced waits alone could consume the timer. A set that
satisfies them proves nothing about CP, CL or IGR.** No document, record or log
line states a satisfied rule as a bound (NT-DL-4, NT-DL-5).

* **N1 (CP).** `T_s · 1,000 ≥ W_show + W_series + ρ`, with CQ-4's one `show` and
  CQ-5's one series. `T_s` is the capture unit's loaded `TimeoutStartUSec`, recorded
  in the H-1 baseline, **finite** (AR-4). With HF-16's default (90 s) and the
  recommended values, `7,000 + 37,000 + 30,000 = 74,000 ≤ 90,000`: **satisfied, 16 s
  to spare**. A larger P needs an explicit `TimeoutStartSec=` in the unit, which
  changes the reviewed unit bytes (T-B1) and is the second alternative of DEC-2.
* **N2 (CL, stop-post and backstop).** `S · 1,000 ≥ λ + W_show + W_series + W_show
  + ρ`, with CL-2's `show`, CL-4's series and CL-6's `show`. Recommended:
  `5,000 + 7,000 + 37,000 + 7,000 + 30,000 = 86,000 ≤ 120,000`: **satisfied**.
* **N3 (backstop firing).** `S_b · 1,000 ≥` the same left side as N2. Recommended
  `S_b = S`.
* **N4 (holder before HL).** `L · 1,000 ≥ 9 · W_show + 2 · W_series + W · 1,000 + ρ`:
  BSP's first read and at most five repeats (six `show` calls), AK-1's `systemd-run`
  and its timer `show`, `hold-start`'s re-read, AV-1's two series, the start window
  and the allowance.

**R3 note (Δ3), corrected in R4 (Δ4).** No parameter is added and N1 … N4 are unchanged.
R3 wrote that the sends of SN "sit inside g". That is withdrawn (W-14). The **scheduled
waits** of SN sit inside g (WB-6); the sends, validations and reap attempts are class X,
belong to no wait budget and may fall after `t_g`. W_show = c + g and W_series = P + c + g
are budgets of *scheduled waiting*, contain no term for them, and **a satisfied sizing
rule says nothing about when a sequence returns**. N1 … N4 remain necessary conditions on
the sum of the waiting budgets; they are not completion guarantees for CP, CL or the
holder.

R1's S grammar `⌈λ/1,000⌉ + ⌈(P + c)/1,000⌉ + 30 … 600` and its `T_s` rule
`⌈(P + c)/1,000⌉ + 30` are **withdrawn** (§7.7, W-6, W-7). The 30-second term was
never derived. It is now the parameter ρ, named for what it is.

### 7.7 Withdrawn claims

| # | Claim | Where it appeared | Why it is withdrawn | Replacement |
|---|---|---|---|---|
| W-1 | CL's worst case is `lock_wait_ms` + local work + (P + c), below S "by the S grammar" | [R1 §7.3] | the grammar adds a margin; the local work is class X | CL is class M-terminated at S and 2S (§7.4); N2 is a necessary condition; §7.9 IM-L |
| W-2 | a catchable end "is therefore acted on within about ten seconds" | [R1 §5.7] | IGR's work is class X, and handlers run only between bytecodes | no time claim; GR-2, the ladder's order, IL, IL′ |
| W-3 | the "Operational latency" column of the ladder | [R1 §5.3] | same | the column "Terminated or limited by (class)" |
| W-4 | the backstop in total takes B·(R + S) | [R1 §7.3] | needs CL bounded by S, and the accepted literal bounds no started firing (RO-5) | B firings (class C), each ended by BS-RM (class M) |
| W-5 | "CL-0 … CL-3, which are local operations bounded by S"; "HL ends within Δ"; "HL detecting an end (≤ Δ)" | [D §4.2.5-R2 (g), (k)] | class X work stated as bounded | corrected in Appendix A: HL observes every Δ **plus** one observation whose child waits are class E and whose other work is class X |
| W-6 | the S grammar `⌈λ/1,000⌉ + ⌈(P + c)/1,000⌉ + 30 … 600` | [R1 §7.3] | a fixed margin presented as a bound | N2 and the parameter ρ |
| W-7 | `T_s ≥ ⌈(P + c)/1,000⌉ + 30` | [R1 §7.3], generalizing AR-4 | same | N1 |
| W-8 | the lock wait is "always shorter than S by the inequality of §7.3" | [R1 LD-5] | it follows from W-6 | LD-5, revised |
| W-9 | "CL is not killed by the stop timeout" | [R1 NT-LD-6] | not showable | NT-LD-6, revised |
| W-10 | every blocking *call* in the holder is bounded | [R1 §5.7] | only the *waits* are | §7.3 |
| W-11 | IGR "cannot be starved by PID 1, by the lock or by Polkit" | [R1 §5.7] | kept only in the narrowed form: it **waits for none** of them | §5.7 |
| W-12 | "every spawn … is killed at [its deadline] by a signal to its process group"; the absolute reading that the kill takes effect, and a direct `SIGKILL` at c | OH-S3 R2 §7.3 row 2, §7.5 HS-5, NT-DL-1 | the sending operation's failure contract, class and target-identity handling were unstated | SN, §7.5a: `SIGTERM`, escalation, results, abandon |
| W-13 | "an abandoned child holds no descriptor of K (LD-3)", unconditionally | OH-S3 R2 §7.3 row 3 | rests on a CPython behaviour no accepted record cites | conditional on SN-8 (e) and PO-SN (c) |
| **W-14 Δ4** | (a) "Everything from S0 to S6 sits inside g"; (b) "both signals sit **inside** g" (CC-1); (c) `SIGKILL` "at the first wake-up at least `slice_ms` later"; (d) "S3: poll … for one `slice_ms`" after `SIGTERM` returns; (e) the return follows the SN sequence "by at most g" (CC-2); (f) the sends of SN "sit inside g" (§7.6 note); (g) IM-S: "signalled" for T2, "killed, or alive in an uninterruptible call" for T3, "as S0" and "as S3" for rows named T0 … T5, "**unsignalled by anyone**" | R3 §7.5a.6 and §0.5 CC-1, CC-2, §7.6, §7.9 IM-S | (a) … (f): the wait ran past `t_g` after a slow send, validation or reap attempt, and the sentences treated the scheduled sleeps as the whole procedure; (g): the map assumed successful delivery, named rows that did not exist, and denied that an earlier send or PID 1's cleanup could apply | WB-1 … WB-7 (§7.5a.6a); table SN-S; IM-S rewritten (§7.9); SN-RO (§7.5a.7) |
| **W-15 Δ5** | (a) R4's E1: "At T3, T5 and T6 the helper may have been ended inside a reap attempt that had reaped the direct child just before. … The design cannot tell the two apart and no step relies on the difference"; (b) T3 and T5 as spans that contain a reap attempt and map only to CS-2, CS-3 and CS-4, and T6 as the point that covers an attempt in progress; (c) CS-5 as "reaped by the helper (the status was held in memory only)"; (d) the matrix cells T0 `u` and T1 `u` as CS-1 only, and T5 `i` as CS-2 or CS-3 without the PK subject; (e) NT-WB-5 as one case for a slow S1 and a slow S4 | R4 §7.9 IM-S (E1, the point table, the state set, the matrix); §7.12 NT-IS-1, NT-IS-8, NT-WB-5 | (a) … (c): the kernel reap completes inside the attempt before the handle records it, so "alive, or exited and unreaped" is false there, and T6 begins only after the decision; (d): R4's own table SN-R row 3, NT-SN-5 (a) and NT-IS-6 admit a reaped handle at T0 and T1, and a PK subject has no `SIGTERM`; (e): one expectation cannot hold for both runs | §7.5a.6c RB-1 … RB-5; T3k, T5k; CS-5 redefined; the corrected cells; NT-WB-5a, NT-WB-5b; NT-IS-16, NT-IS-17 |
| **W-16 Δ6** | (a) R5's row 3g: a raised `Popen.poll()` is "read as *unreaped* for that attempt, so the child can be abandoned but never presumed reaped"; (b) R5's RB-5: "R5 does not change row 3g, S4 or SN-4 for it", and that PO-SN (c) "is an AP-0 gate: if it is not accepted as extended, the contract is not adopted"; (c) R5's WB-7: a reap-attempt exception causes no further send "apart from the single escalation of S4"; (d) R5's CC-20: "Row 3g's reading of a raised exception as *unreaped* is not changed"; (e) R5's table SN-S S1: "If it yields `not-sent`, no signal is sent: go to S5" for every subtype, and R5's claim that the T5 `u` dash is unreachable; (f) R5's CC-18 and its paragraph *Before T0*: the cells T0 `u` and T1 `u` admitting CS-5, and "a helper ended at T0 or at T1 then leaves a reaped direct child (CS-5)"; (g) NT-IS-6's "CS-5 at T0 and T1" | R5 §7.3 row 3g, §7.5a.6c RB-5, §7.5a.6a WB-7, §0.7 CC-18 and CC-20, §7.5a.6 S1, §7.9 IM-S (the T0 and T1 cells, *Before T0*), §7.12 NT-IS-6 | (a) … (d): the exception may follow the kernel's reap, so *unreaped* is not known and a later `SIGKILL` could reach a released PID or group number; a gate that only requires acceptance does not state a safe outcome. (e): S1 sent `not-sent(reaped)` to S5, which polls a reaped handle and contradicts table SN-R rows 3 and 9, WB-5 (a) and the dash in T5 `u`. (f), (g): a reaped handle entered at T0 or T1 puts one interruption at T0 or T1 and, once the line is written, at T7, and the settled-state decision was made before SN | RE-1 … RE-6; S8; S1-a, S1-b, S7; CS-9, CS-10; CC-23; NT-RE-1 … 12; NT-NS-1 … 8 |
| **W-17 Δ7** | (a) R6's CC-30: a foreign reap "is seen by validation as `not-sent(identity-mismatch)` or `not-sent(identity-unverifiable)` and goes to S5"; (b) R6's NT-SN-12: "when a foreign reap is injected the handle's state is unchanged …, so validation yields `not-sent(identity-mismatch)` or `not-sent(identity-unverifiable)` and the sequence goes to S5 … **never a send to the stale number**" | R6 §0.8 CC-30; §7.12 NT-SN-12 | A released PID and process-group number can be reused by a process with the same structural relationship (`pgid == pid == sid`), and the `start_ticks` check is optional (PO-SN (d)), so validation need not detect a foreign reap, the injected state need not reach S1-b, and a send to a reused number is **not excluded by SN-4**. SN-4 is a detector (SI-2); the reuse defence is SI-3's sole-reaper invariant with PO-SN (b), (c), (f) | SI-3 (explicit, load-bearing); SI-5; NT-SN-12 (structural, with one labelled non-universal detector exercise); NT-SN-6 (b) labelled; INV-27; CC-33, CC-34 |
| **W-18 Δ7** | (a) R6's record schema: `grace_deadline_ms` as a field of every `children` entry with no condition; (b) R6's INV-22: "each child has **one** grace deadline, read once before its first validation or send"; (c) R6's NT-RE-11 "one `t_g` read" and NT-WB-11 (i) "one grace-deadline read per child", both unconditional; (d) R6's table SN-S: S0 entered before S1 for every handle, a settled one included | R6 §7.5a.9, §8.5, §8.6 INV-22, §7.12 NT-RE-11, NT-WB-11, §7.5a.6 S0 | A child whose S0 never ran has no deadline: a `reap-error` raised in a poll of the enclosing wait before S0, a child that exits within c, a failed spawn. The schema, the invariant and the tests could not hold on those paths together (R7-F1), and a settled handle must not start a grace period | GD-1 … GD-5 (§7.5a.6e); INV-22 (amended), INV-26; NT-GD-1 … 4; CC-31, CC-32 |

### 7.8 Signal discipline SG-1 … SG-8 *(proposed)*

* **SG-1, when handlers are installed.** The holder installs handlers for the set
  **H** = `SIGTERM`, `SIGINT`, `SIGHUP`, `SIGQUIT`, `SIGUSR1`, `SIGUSR2`, `SIGALRM` as
  the **first act** of its `hold` entry, after the helper-start contract RH is
  discharged and **before any state operation**: before AM-0's re-checks, before K,
  `grant.id`, the journal, AK-1, AM-1 and **AM-2**. A signal that arrives before SG-1
  takes its default action and ends the process **before any object exists**
  (state ST-1; nothing to remove).
* **SG-2, handlers only set a flag.** A handler sets `stop_requested = True` and
  returns. It raises nothing, calls nothing, writes nothing, takes no lock and never
  calls IGR. R1's design, in which the handler raised a dedicated exception that
  could fire at any bytecode, is **withdrawn**: that exception could land inside
  IGR itself.
* **SG-3.** `SIGPIPE` stays ignored (the interpreter's default). `SIGCHLD` is not
  handled: children are polled. **Δ3** The holder never sets `SIGCHLD` to `SIG_IGN` or
  `SA_NOCLDWAIT`, which would let the kernel reap children outside the sole reaper
  (SI-3, PO-SN (f)). A signal outside H that cannot be caught, or whose
  default action terminates, is an *uncatchable* cause (§5.5, rows 8 and 9).
* **SG-4, where the flag is checked.** At every step boundary of the holder (AM-0's
  steps, AK-1, AM-1, AM-1R, **immediately before AM-2's PF-6 link**, AV-1, AM-3,
  `hold-start`); at every HL iteration; and **at every `slice_ms` wake-up of every E
  wait** (§7.3 rows 2, 3, 6, 7, 14). When the flag is set an E wait runs the SN sequence on
  its child (§7.5a.6: validation, `SIGTERM`, escalation, and the scheduled reap waiting of
  at most g from one `t_g` read before the first send), abandons it if it is unreaped (**Δ6:** a reap-error instead ends the sequence at once, RE-1), returns `interrupted`, and the body returns. **Δ3** **Δ4** The flag is *observed* at the
  next wake-up, which is at most `slice_ms` of scheduled sleep away (and sooner when the
  sleep is capped, WB-2); the *return* follows the SN sequence, whose **scheduled waiting**
  is at most g and whose elapsed time is not bounded (CC-2, CC-9, WB-6). The flag neither
  shortens nor extends the grace (WB-7). After PF-6
  returns the flag is checked at the very next statement. A `SIGTERM` delivered
  between the last check and PF-6 therefore costs a brief G1 that IGR removes.
* **SG-5, a second signal.** Further signals set the same flag again. They never
  re-enter IGR and never restart GRR. Because no handler raises, **no exception can
  arise inside GRR from a signal**.
* **SG-6.** The holder never blocks signals. A blocked pending signal would be
  delivered at an unpredictable later point, which SG-2 and SG-4 are designed to
  avoid.
* **SG-7, the single IGR site.** IGR runs from one `finally` around the whole body
  after SG-1, once (IGR-0). After it the holder returns its exit status. No
  `atexit` work and no `os._exit` before IGR exist.
* **SG-8, CP, CL and BS install no handlers.** They take the default action on
  `SIGTERM`. Their interruption is **mapped** (IM-C, IM-L, IM-B) and not handled,
  because their first state-changing acts (CQ-3, CL-G) are already ordered first,
  and a handler would add a path whose own elapsed time is unbounded.
* **SG-9, no handler sends a signal. Δ3** SN runs only on the main thread, at step
  boundaries and inside E waits. No handler, no `finally` other than the single IGR
  site, IGR, GRR and CL-G sends a signal (§7.5a.1, SN-I-4), and SN cannot be
  re-entered from a handler.

The design **does not depend** on any `finally` completing in any time. IGR is the
first rung. Its absence is covered by RL-1 … RL-4 and by IL and IL′.

### 7.9 Interruption maps

"Interrupted" means the process is ended by a signal at the stated point, by a
class-M timer or by a root act. The *state* is what remains. The *first owner* is
the first rung (§5.3) that acts next. All objects named are under `/run` unless
stated, and a kernel boot (RL-4) clears every one of them.

**IM-L, CL (each trigger).** CL receives `SIGTERM` at S (stop-post) or S_b
(backstop) and `SIGKILL` after S, or any kill. CL installs no handler (SG-8), so
the first signal ends it.

| Point | Interrupted at | State | Grant | First owner | Then |
|---|---|---|---|---|---|
| **L0** | process start, K open, `grant.id` read, GRR-2 or GRR-3, **before** the `unlinkat` | **ST-1.i**: holder gone, rule live | G1 **inert** (IL) | the backstop's CL (if armed and spawnable); else CP at a later start | the boot; `attest` for records |
| **L1** | after the `unlinkat`, before CL-0 finishes (no attempt journal yet) | rule absent, nothing recorded | G2 | the backstop's CL (classes the rule `absent-before-removal`) | `attest` |
| **L2** | during CL-0: lock attempts, attempt directory, journal | a partial attempt directory may exist; `k` counts it | G2 | the backstop's CL as attempt `k + 1` | `attest` |
| **L3** | after CL-0, before CL-3's record | `run-start` present, no classification line | G2 | the backstop's CL | `attest` |
| **L4** | during CL-4's PK series, or after it before its record | rule absent, `removed-verified` **not** recorded; a PK child or subject in flight is left to IM-S | G2 (G3 not recorded) | the backstop's CL re-runs CL-4 and needs PK *not authorized* again | `attest` |
| **L5** | during CL-5: `remove-intent` for `pass-a.json` written, `unlinkat` perhaps done | **ST-1.d1** | G3 if CL-4 recorded it, else G2 | the backstop's CL-5 classes `removed-earlier` or `absent-before-removal` from the intent line | the boot |
| **L6** | during CL-5b: tree **P**'s top, tree **R**, `grant.id`, K | partial `/run` objects: class S0 | as L5 | the backstop's CL-5b, else the boot | — |
| **L7** | after CL-5b, during CL-6 (reads, the **baseline recomputation**, `show`) | everything removed; `st1-verified` not recorded | G3 | the backstop's CL re-verifies; or `attest` | — |
| **L8** | during CL-7, record publication | PF is atomic: a record is absent or complete. The journal lacks `run-end`. **ST-1.ur** if no `deact` record exists | G3 | the backstop writes the record; or `attest`. If a terminal `deact` record exists BS-2 disarms | — |
| **L9** | after `run-end` | complete | G3 | none | — |

Every row ends in `st1-verified`, in a defined HARD STOP (ST-1+R), or in ST-1.bc
followed by attestation. **No row waits for a human to disable the grant.**

**IM-I, IGR.**

| Point | Interrupted at | State | Grant | First owner |
|---|---|---|---|---|
| **I0** | before GRR-2 (flag observed, nothing done) | ST-1.i | G1 inert | stop-post CL (CL-G); else the rungs of L0 |
| **I1** | GRR-3 verification (open, `fstat`, hash, `flistxattr`) | ST-1.i | G1 inert | as I0 |
| **I2** | after the `unlinkat`, before the directory `fsync` or the `igr` line | rule absent, unattributed | G2 | stop-post CL classes it `absent-before-removal` |
| **I3** | after the `igr` line is durable | rule absent, attributed | G2 | stop-post CL: `removed-earlier`, then CL-4 |
| **I4** | the `igr` line's `fsync` stalls | as I2 or I3 | G2 | RO-6 for the evidence; the grant is already gone |

A second termination signal at any of I0 … I4 sets the flag and changes nothing
(SG-5). `SIGKILL` at any of them is the corresponding row.

**IM-C, CP.** The start timeout T_s or any kill ends CP. The accepted matrix
[D §4.2.5-R5 (i)], column "K or T", is unchanged and is restated by reference:
before CQ-2 no claim exists and the rule stays live (G1), the attempt ends `failed`,
SB-2 refuses every later attempt, HL ends `start-failed-before-exec`, and IGR or CL
removes the rule first. After CQ-2 the claim exists (SB-1). After CQ-3's `unlinkat`
and before `removed` the rule is absent and CL classes it `absent-before-removal`.
During CQ-5 the rule is gone (G2), no `consumed` line exists and `ExecStart=` is
never executed [R2 §8 (o)]. After `consumed` and before CQ-7 the attempt is recorded
`start-failed-before-exec`. R2-F2 adds only that **T_s is class M and CP's own
elapsed time is not claimed**, and that CP installs no handler (SG-8).

**IM-B, a backstop firing.** BS-RM sends `SIGTERM` at S_b and `SIGKILL` after S. The
points are those of IM-L. After the service ends, the timer re-arms and fires again
[R2 §8 (j)], at most B times. Without BS-RM a hung firing prevents every later one
(RO-5).

**IM-A, the holder (ACT and HL).** Termination at a point leaves the objects built so
far. Before SG-1 and AM-0: none. After K and before the journal: K only (S0). AK-1:
ST-1.a0. AM-1: ST-1.a1 (tree **P**). Between the `grant.id` write and PF-6:
`grant.id` and tree **P**, no rule. After PF-6 (ST-1.a2, ST-2): G1, removed by IGR if
the end is catchable and reached, else by RL-1 … RL-4. After CP's CQ-3 (ST-3): no
grant. Each continues to CL as in §8.3.

**IM-S, the signal-sending sequence SN (R3 Δ3; rewritten in R4 Δ4; the points, the state set and the matrix corrected in R5 Δ5; the S1 branches, T0, T1, T6, T7, the raised attempt (T3x, T5x, CS-9, CS-10) and the matrix cells corrected in R6 Δ6).** SN never touches a
grant object, a lock, a journal other than its own `child` line, or the claim. An
interruption **inside SN** is the interruption of the enclosing step: its row in IM-A,
IM-L, IM-C or IM-B fixes the grant, the lock and the records. IM-S adds only the child.
"Interrupted" is as in the introduction of this section (a signal that ends the helper, a
class-M timer, a root act). **The interrupted helper is the process that owns the
sequence: once it has ended it makes no further send, no wait and no record.** R3's table
assumed that every send succeeded, used the row names "as S0" and "as S3" for rows that
were called T0 … T5, and omitted the interactive `attest`. It is withdrawn (W-14) and
replaced by the rules, the state set, the matrix and the owner table below. **R5 (Δ5)** found
that R4's points T3, T5 and T6 and its matrix gave a direct child that the kernel had reaped
inside a reap attempt no state: the T3 and T5 cells named only unreaped children, and T6
begins after the sequence has decided. The point list, CS-5 and CS-7 and the matrix are
corrected below on the boundary of a reap attempt defined in §7.5a.6c (RA-0 … RA-4, RB-1 … RB-5). **R6 (Δ6)** found that R5's S1 sent `not-sent(reaped)` to S5 while the matrix, table SN-R and WB-5 ended the sequence (R6-F2), and that a raised reap attempt, read as unreaped, could lead to a send (R6-F1). The outcome `u`, T0, T1, T6, T7, the cells and the state set gain the settled-handle rule (CC-23) and the states CS-9 and CS-10 (§7.5a.6d, RE-1 … RE-6); T0 and T1 return to R4's cells.

**Rules IS-1 … IS-10 *(proposed [N])*.**

* **IS-1, the words.** *Sent* means only that the kernel send call returned 0 *[PO-SN
  (a)]*. A **recorded reap status** is the only thing that proves that the **direct child**
  was reaped. Neither proves that any process exited, that the process group is empty, or
  that anything acted on a signal. **Δ5:** "proves" is said of what the design can know.
  The kernel may have reaped the direct child with **no** record anywhere (a *kernel reap*
  inside an attempt that the helper did not survive, phase RA-2 of §7.5a.6c): that is a truth
  about the child, not evidence, and IS-9 says what it is worth.
* **IS-2, after any send the target may remain alive.** This holds after `SIGTERM`, after a
  `SIGKILL` that returned 0, after `ESRCH` and after every error. Delivery may have failed;
  the process may be in an uninterruptible call; the signal may not have been queued.
* **IS-3, no inference to the group.** A reap status concerns the direct child. SI-1 makes
  that child the leader of its own group; it may have started others. **Group emptiness is
  never inferred from reaping the direct child.** **Δ5:** nor from a kernel reap that no
  record shows (CS-5).
* **IS-4, history is not a future send.** What an ended helper had **already attempted** is
  history, and it is not erased: a `SIGTERM` may have been sent, and PID 1's cleanup of the
  helper's unit may later signal what remains (table SN-RO, class **M**, *[N, PO-SN (e)]*).
  What the ended helper will do is **nothing**: it makes no further send. No other
  procedure signals the child (SN-9). **No statement in this document says that an ended
  helper leaves its children "unsignalled".**
* **IS-5, the state is not a function of the result.** The state of a child after an
  interruption, and its owner, are **not** functions of any send result. Several outcomes
  of one point give the same state (matrix, below), and a test harness varies the truth
  about the child freely (NT-IS-1 … 17). **Δ5:** two points that differ only by the phase of a
  reap attempt (T3 and T3k, T5 and T5k) differ by the kernel's truth about the direct child
  (§7.5a.6c), never by a send result.
* **IS-6, ownership follows the enclosing procedure** (table SN-RO): the holder, CP,
  stop-post CL, the backstop service, or the interactive `attest`, which has **no automatic
  owner**.
* **IS-7, the boot is a separate recovery event.** It is neither an owner that acts on the
  child nor evidence that any signal was sent or succeeded (§7.5a.7).
* **IS-8, effect and result.** The effect of a mutating child (`systemd-run`, `systemctl
  stop`) is `unknown` in **every** state below (SN-10). The enclosing operation's result is
  the fail-closed one it would have had. No retry, no repetition of the step and no search
  for a process is granted (SN-9, Appendix B-13).
* **IS-9, the observer rule (R5).** *Without a durable `child` line a later procedure learns
  no reap fact.* For CS-1 … CS-6 and CS-9 it records only the gap `children-unknown` (§7.5a.9) or the
  applicable gap. **A kernel reap that was not durably recorded (CS-5, the phases RA-2 and
  RA-3) is not evidence, to any later procedure, that the child is gone, that it was reaped,
  that anything exited, or that the process group is empty.** No later procedure may act on it, search for a process because of it, or derive a state from the absence of a line.
* **IS-10, the raised-attempt rule (R6, Δ6).** After a reap attempt raised, the child is in the
  handle state `reap-unknown` (RE-2) and, once its helper has ended, in CS-9 (no durable line) or
  CS-10 (a durable line with `reap_unknown: true`). **Neither state says whether the direct child
  is unreaped or was reaped in the kernel**, and a later procedure derives neither truth from the
  state, from the line, from its absence or from the exception that caused it. The ended helper
  makes no further send, and **no send was made, and none will be made, after the error** (RE-1).
  A later procedure records `children-unknown` for CS-9 and reads the line for CS-10; it acts on
  nothing and searches for nothing (SN-9).

**The interruption points** (they replace R3's T0 … T5; they follow table SN-S; **Δ5:** T3, T5 and T6 are redefined and T3k and T5k added, on the phases RA-0 … RA-4 of §7.5a.6c; **Δ6:** T0, T1 and T6 are redefined for a settled handle, and T3x and T5x added, on the phase RA-E):

| Point | The helper is ended at |
|---|---|
| **T0** **Δ6** | the trigger (deadline c, flag, or a finished PK call) is decided; `t_g` is not yet read (before S0); **for a handle in state `running`**. A handle already settled when SN is entered is never at T0 (CC-23) |
| **T1** **Δ6** | S0 done, S1 validating a `running` handle or having rejected it (S1-b); the `SIGTERM` call has not begun (for a PK subject: the `SIGKILL` call has not begun). A settled handle at S1 (S1-a) is at T6, not T1 (CC-23) |
| **T2** | S2: **inside** the `SIGTERM` call, or after it returned and before S3 begins |
| **T3** **Δ5** | S3 **while the direct child is not reaped in the kernel**: before the first reap attempt (RA-0), inside it before a reap (RA-1), the capped sleep, between the attempts, the second attempt's RA-0 and RA-1; before the S4 decision |
| **T3k** **Δ5** | S3 **inside a reap attempt at RA-2**: the kernel has reaped the direct child and the handle still says `running`; the sequence has not decided |
| **T3x** **Δ6** | S3 **inside a reap attempt at RA-E**: the attempt raised and S8 has not yet set `reap-unknown`; whether the direct child is reaped is **not known**; no act has been made |
| **T4** | S4: the second validation, **inside** the `SIGKILL` call, or after it returned; before S5 |
| **T5** **Δ5** | S5 **while the direct child is not reaped in the kernel**: the loop of attempts (RA-0, RA-1) and capped sleeps, **the final attempt's RA-0 and RA-1 included**; before the sequence decides |
| **T5k** **Δ5** | S5 **inside a reap attempt at RA-2**, of any attempt of the loop and of the final attempt |
| **T5x** **Δ6** | S5 **inside a reap attempt at RA-E**, of any attempt of the loop and of the final attempt: as T3x |
| **T6** **Δ5** **Δ6** | the sequence has **decided**: the handle's state has been **set** (to `reaped` by an attempt that reaped the child, phase RA-3, at S3, S5 or the final attempt; to `abandoned` at S6; or **to `reap-unknown` at S8**), **or the handle was already settled when SN was entered** (by an enclosing poll's RA-3, by an earlier S6, or by an earlier S8: S1-a), and in every case the `child` line is **not yet durable**. This includes S1-a's path to S7 and S7 before its line is durable. **T6 never includes the interior of an attempt** (RB-4) |
| **T7** | the `child` line is durable; the enclosing operation has not yet returned its result |

**Before T0 (Δ5, rewritten in R6, Δ6).** T0 is entered only for a handle in state `running`,
after the enclosing E wait's most recent poll returned *unreaped*, or with no poll yet made (a PK
subject is never polled by the call that created it). The polls of the enclosing wait are reap
attempts of the same phases (RB-2) and precede T0, in the enclosing step: a helper ended there
leaves CS-1 (the direct child not reaped), CS-5 (RA-2 of that poll: the kernel reaped it, no
line, handle `running`) or CS-9 (RA-E of that poll: it raised). **A handle that the enclosing
poll left settled** (`reaped` at that poll's RA-3, or `reap-unknown` at S8) **is never at T0 or
T1:** its settled-state decision was made **before SN**, and **from that decision until S7 has
made the `child` line durable the helper is at T6 (CS-5 or CS-9), and afterwards at T7 (CS-7 or
CS-10)**. S1-a ends the sequence at S7 with no call and no wait (CC-23). **Δ7:** a poll that raised (RA-E) is **before S0**: it reads no `t_g`, and its entry carries `s0_ran: false` and `grace_deadline_ms: null` (§7.5a.6e); and a settled handle that SN is later called on reaches S1-a **without S0 and without a clock read** (CC-31).

**The send outcomes** (columns of the matrix): the outcome of the **send decision that the
point concerns** — `SIGTERM`'s at T1, T2, T3, T3k and T3x; `SIGKILL`'s at T4, T5, T5k and T5x (the validation verdict where S1 or S4 rejected); and the latest decision reached at T6 and T7. A PK subject has no T2, no T3, no T3k and no T3x (S2 and S3 are skipped, table SN-S, S0).

| Code | Outcome | Meaning |
|---|---|---|
| **u** | unmade | no call and no verdict yet (the point precedes it: T0, T1, T4), or, **Δ6**, **a settled handle** whose verdict is `not-sent(reaped)`, `not-sent(abandoned)` or `not-sent(reap-unknown)` (S1-a: **no call, no wait, to S7**; only at T6 and T7) |
| **i** | identity-rejected | `not-sent(identity-mismatch)` or `not-sent(identity-unverifiable)`: validation failed, **no call is made**, and no signal of either kind will ever be sent to this child (SN-4); the sequence goes to S5 (S1-b, **Δ6**) |
| **x** | indeterminate | the helper ended **inside** the call, or before the result was held. The signal may or may not have been queued |
| **s** | `sent` | the call returned 0 |
| **e** | `esrch` | the call returned `ESRCH` (with the anomaly `esrch-while-unreaped`) |
| **f** | failed | `eperm`, `errno:⟨n⟩` or `exception:⟨class⟩` |

**The common child-state set** (what a child can be once its helper has ended). "Further
sends by the ended helper" is **none in every row**; the history column is what it
*had* attempted. **Δ5:** in CS-1 … CS-4, CS-6 and CS-8 the direct child is **not reaped in the
kernel**; in CS-5 and CS-7 it is. **Δ6:** in CS-9 and CS-10 the helper **does not know** (RE-2).

| ID | Sends already attempted (history) | The direct child | Record that survives |
|---|---|---|---|
| **CS-1** | none | alive, or exited and unreaped | none |
| **CS-2** | none; validation rejected, so none would ever be made | as CS-1 | none |
| **CS-3** | `SIGTERM` attempted (result held in memory only, or lost in the call); `SIGKILL` **not** attempted, because S4 was not reached, or its second validation rejected, or the helper ended inside it | alive, or exited and unreaped. It may be acting on the signal; this is **not known** | none |
| **CS-4** | a `SIGKILL` send attempted, after a `SIGTERM` send or alone for a PK subject (result in memory only, or lost in the call) | as CS-3 | none |
| **CS-5** **Δ5** | any of the above | **reaped in the kernel** by the helper's own `waitpid` (a kernel reap, §7.5a.6c). The handle may still say `running` (RA-2: T3k, T5k) or say `reaped`, held in memory only (RA-3: T6). The group may still contain live processes (IS-3) | none: the line was not durable |
| **CS-6** | any of the above | **abandoned**: unreaped when the final attempt ran; since then alive, or exited and unreaped (no other reaper acts: SI-3, RB-2) | none: the abandon was decided, the line was not durable |
| **CS-7** **Δ5** | any of the above | reaped in the kernel and recorded (RA-4), as CS-5 | a durable `child` line with `reaped: true` |
| **CS-8** | any of the above | abandoned, as CS-6 | a durable `child` line with `abandoned: true` |
| **CS-9** **Δ6** | any of the above, **as attempted**; **none is attempted after the error** (RE-1) | **not known** (RE-2): not reaped (alive, or exited and unreaped), **or** reaped in the kernel with no handle update, in which case its PID and group number may since have been released. The helper did not know either | none: the line was not durable (the helper ended at T3x or T5x, at T6 after S8, or inside an enclosing wait's own poll at RA-E, which has no SN point) |
| **CS-10** **Δ6** | any of the above, as CS-9 | not known, as CS-9 | a durable `child` line with `reap_unknown: true`, `send_suppressed: true`, `reaped: false` and `abandoned: false` |

**The matrix: interruption point × latest send outcome.** A dash is a combination that
cannot occur. A cell names the state of the child after the helper has ended; the owner of
every state is the row of table SN-RO for the enclosing procedure. "(PK)" marks the
difference for a PK subject, whose only send is `SIGKILL` at S4.

| Point | u | i | x | s | e | f |
|---|---|---|---|---|---|---|
| **T0** **Δ6** | CS-1 | — | — | — | — | — |
| **T1** **Δ6** | CS-1 | CS-2 | — | — | — | — |
| **T2** | — | — | CS-3 | CS-3 | CS-3 | CS-3 |
| **T3** | — | — | — | CS-3 | CS-3 | CS-3 |
| **T3k** **Δ5** | — | — | — | CS-5 | CS-5 | CS-5 |
| **T3x** **Δ6** | — | — | — | CS-9 | CS-9 | CS-9 |
| **T4** | CS-3 (PK: CS-1) | CS-3 (PK: CS-2) | CS-4 | CS-4 | CS-4 | CS-4 |
| **T5** | — | CS-2 (S1 rejected, or a PK subject's S4 rejected; **Δ5**) or CS-3 (S4 rejected after a `SIGTERM`) | — | CS-4 | CS-4 | CS-4 |
| **T5k** **Δ5** | — | CS-5 | — | CS-5 | CS-5 | CS-5 |
| **T5x** **Δ6** | — | CS-9 | — | CS-9 | CS-9 | CS-9 |
| **T6** **Δ6** | CS-5 if reaped, CS-6 if abandoned, CS-9 if `reap-unknown` (the settled handle of S1-a) | CS-5 if reaped, CS-6 if abandoned, CS-9 if `reap-unknown` | — | as `i` | as `i` | as `i` |
| **T7** **Δ6** | CS-7 if reaped, CS-8 if abandoned, CS-10 if `reap-unknown` (the settled handle of S1-a) | CS-7 if reaped, CS-8 if abandoned, CS-10 if `reap-unknown` | — | as `i` | as `i` | as `i` |

**Reading the matrix.**

* **Death during a send** is the column **x**: T2 and T4. The cell is the same state as the
  cells for `s`, `e` and `f` of that row (IS-5): nothing distinguishes a signal that was
  queued, a signal that failed and a call that never finished.
* **Partial escalation** is CS-3: `SIGTERM` attempted, `SIGKILL` never attempted. The
  states of T4 `u` and `i` are CS-3 for the same reason.
* **Validation failure** is the column **i**; **`ESRCH`** is **e**; **other errors** are
  **f**; an **unmade send** is **u**. None of them yields "exited".
* **Reaping and abandonment** are T3k, T5k, T6 and T7 **(Δ5)**. T3k and T5k are a kernel reap inside an attempt of S3, of S5 or the final attempt that the helper did not survive to record (**Δ6:** a raised attempt is T3x and T5x, then T6 and T7 through S8 and S7, and its states CS-9 and CS-10 say only that the helper does not know, IS-10); T6 and T7 are the decision (S3, S5 or the final attempt for the reap; S6 for the
  abandon) and the durable line. CS-5 and CS-7 say only that the **direct child** was reaped
  in the kernel (IS-3).
* **E1, the interior of a reap attempt (rewritten in R5, Δ5).** An interruption inside a reap
  attempt is one of RA-0 … RA-2 or, **Δ6**, RA-E of §7.5a.6c. **Before the call (RA-0) and inside the call
  before the kernel has reaped (RA-1)** it is T3 or T5, and the direct child is not reaped
  (CS-3, CS-4, CS-2). **After the kernel reap and before the handle-state update (RA-2)** it
  is T3k or T5k, and the direct child **is reaped** with the handle still `running` and no
  line (CS-5). **After the handle-state update, before the durable line (RA-3)** it is T6
  (CS-5 with the handle `reaped`, or CS-6 if the sequence abandoned), and **after the durable
  line (RA-4)** it is T7 (CS-7, CS-8). RA-1 and RA-2 are separated only by the kernel's act
  inside one call: the design cannot tell them apart. A later procedure sees a record only for RA-4 and nothing for RA-0 … RA-3, and nothing is inferred from any of them (IS-9). **Δ6:** **after a raised attempt, before S8 has set `reap-unknown` (RA-E)** the interruption is T3x or T5x and the direct child is **not known** (CS-9), whichever the kernel did inside the call; **after S8's update and before the line** it is T6 (CS-9), and **after the line** T7 (CS-10). A later procedure sees a record only for T7 (IS-10).
* **Corrected cells (R5, Δ5; corrected again in R6, Δ6).** **T0 and T1 `u` are CS-1 only** (R6,
  CC-23: a handle that an enclosing poll reaped is settled before SN, so it is at T6 or T7, never
  at T0 or T1; R5's CS-5 in those cells is withdrawn, W-16). T5 `i` names CS-2 for the PK subject
  whose S4 validation rejected, because it has no `SIGTERM` (CC-19, R5). **T6 and T7 `u` are the
  settled handles of S1-a** (CS-5 or CS-7 reaped, CS-6 or CS-8 abandoned, CS-9 or CS-10
  `reap-unknown`). **Every dash is a combination that the sequence cannot reach, re-derived from
  table SN-S (R6):** before S1's verdict the only outcome is `u` (T0, T1); `i` needs a verdict,
  and `s`, `e`, `f` a call that has returned, and `x` exists only inside a call (T2, T4); **S1-a
  goes to S7 and never to S5, so T5, T5k and T5x have no `u`**; S1-b is the only way to S5
  without a send, so T5 and T5k hold `i` for it and `s`, `e`, `f` after a returned send; S2
  follows a passing validation, so T2, T3, T3k and T3x have neither `u` nor `i`; S3 follows the
  return of the `SIGTERM` call, so T3, T3k and T3x have no `x`; S5 follows a verdict or a
  returned `SIGKILL`, so T5, T5k and T5x have neither `u` nor `x`; **T3x and T5x follow an
  attempt, which follows a send decision, so they carry that decision's outcome and never `u` or
  `x`**; T6 and T7 hold a result or a settled handle, so they have no `x`; and T1, T2 and T4
  contain no reap attempt, so no kernel reap and no raised attempt begins there (RB-2).
* **Truth versus record.** The column "The direct child" of the state set lists what *may
  be true*. A later procedure sees only the record column: for CS-1 … CS-6 nothing. **Δ5:** it
  therefore cannot tell CS-5 from CS-1, CS-3, CS-4 or CS-6; they differ in truth only (IS-9). **Δ6:** the same holds for CS-9: it cannot be told from CS-1 … CS-6, and CS-10 records only that the helper did not know (IS-10).

**The owner and the record of each state** (the same for every outcome, IS-5, IS-6):

| Enclosing procedure | Owner of a CS-1 … CS-10 child | What the next procedure can know |
|---|---|---|
| holder (ACT, HL, AV-1) | PID 1's stop of the holder unit *[N, PO-SN (e)]*; then the boot | CS-7, CS-8, CS-10: the `child` line. CS-1 … CS-6, CS-9: only that the holder's journal lacks `hold-end`, which the stop-post CL records as `children-unknown` |
| CP | PID 1's end of the attempt *[N, PO-SN (e)]*; then the boot | CS-7, CS-8, CS-10: the line in the consume journal. CS-1 … CS-6, CS-9: the missing `run-end`, which the next CL records as `children-unknown` |
| stop-post CL | `FINAL_SIGTERM` / `FINAL_SIGKILL` to "what remains" **[R2 §8 (e)]**; then the boot | CS-7, CS-8, CS-10: the line in the CL attempt journal. CS-1 … CS-6, CS-9: the missing `run-end`; the backstop's CL, or `attest`, records `children-unknown` |
| backstop service | the end of the service *[N, BS-RM, PO-SN (e)]*; then the boot | as stop-post CL |
| **interactive `attest`** | **no automatic owner**; the boot is a separate event | CS-7, CS-8, CS-10: the line in the attempt journal. CS-1 … CS-6, CS-9: the missing `run-end`. The executor **reports** `children` or `children-unknown` and does not act (SN-9) |

A helper ended at any of T0 … T7 (T3k, T5k, T3x and T5x included) makes no further send, wait or record. What it had
attempted before that stays history; what PID 1 may do to the unit's remaining processes is
a separate class-M act with no promised effect; no other procedure hunts the child (SN-9);
the boot clears it later and proves nothing about it. Every conclusion that does not
depend on the child stands, and G1 … G5 cite no child.

### 7.10 PO-11 (d′) *(proposed [N], text for [D §4.4.2a]; retained from R1)*

> **(d′)** *No bound is claimed on the time between the creation or removal of a
> polkit rules file and polkitd's use of that change.* A PK call returns the
> decision of polkitd's **current** rule set at the instant of the call. The
> design waits for a stated decision for at most `pk_op_ms` (starting calls) and
> `pk_call_ms` plus `reap_grace_ms` (waiting on the last call), enforced by the
> caller (class E), and treats every other result, including the expiry of that
> time, as *unconfirmed*, which **fails closed at every use** (§7.11). The same
> holds for `/run/polkit-1/rules.d` ((f)(iii)). Obligations (e), (f)(i), (f)(ii)
> and (f)(iv) stand as accepted. **Every operational timeout of this design fails
> closed: no expiry authorizes, passes, or hides a failure.**

AP-0's requirement "the PO-11 (d) … citations accepted" becomes "PO-11 (d′)
accepted, the parameter grammar of §7.6 and the sizing rules N1 … N4 evaluated".
**This needs no host citation for (d′).** The block that returned `ACT` and
`DEACT` to design review is answered by the design itself: no bound is cited, and
nothing polls without one.

### 7.11 What each timeout does, and what it can leave

| Step | Mode | Budget (class E) | On `unconfirmed` |
|---|---|---|---|
| AV-1, positive control for verb `start` | seek-authorized | P | `ACT` ends HARD STOP `grant-not-seen`; CL runs, rule first. No pass. PK's sensitivity was not shown, so nothing later may be read as evidence |
| AV-1, negative control for verb `stop` (AR-7) | first-decisive | P | `authorized` fails `ACT` at once. `unconfirmed` fails `ACT` (HARD STOP `stop-control-unconfirmed`) |
| CQ-5, consume post-check | seek-not-authorized | P | CP exits non-zero `consume-failed {CQ-5, removed-unconfirmed}`; **`ExecStart=` is not executed**; CL re-checks |
| CL-4 | seek-not-authorized | P | rule class `removed-unconfirmed`; outcome HARD STOP; the backstop retries within `backstop_max` |
| GP-R3's grant post-check | as CL-4, result held in memory | P | as CL-4 |
| attestation, `cleared-by-boot` | seek-not-authorized | P | no `st1-verified` record is written |
| H-2, AP-0, CL-6 | **do not run PK** | — | CL-6 uses CL-4's result |
| drills (OH-S8b) | as the step they exercise | P | as that step |

* **G1 is unaffected.** A CQ-5 timeout blocks `ExecStart=`. The rule is already gone
  from the directory (CQ-3).
* **After CQ-5 `unconfirmed(still-authorized)`**, polkitd may still authorize a
  `start` for `ubuntu`, which is G2 in the visible-lag state. A later start reaches
  CQ-2, finds the claim (`EEXIST`) and exits with nothing touched (SB-1). No pass.
* **After AV-1 `grant-not-seen`**, polkitd may load the rule late. CL removes the
  file, and any reload that follows reads a directory without it.
* **Every wait in the design is class E, M or C.** (A signal *send* is not a wait: it
  is class X with a count bound, §7.3 rows 3a … 3f; nor is a reap attempt, row 3g. **Δ3 Δ4**)
  The PK series' scheduled waiting totals at most P + c + g (WB-6); the lock loop's at λ; BSP after five reads; HL at L (M); the backstop after B
  firings (C) with each firing ended by S_b (M); PK never runs outside these
  procedures. Class-X work is **not** bounded, and §7.9 states what its interruption
  leaves.
* **NUDGE is not proposed.** Creating and removing an empty `*.rules` file in a
  monitored directory to force a reload would add a write path into polkit's rules
  directory whose effect is a GLib behaviour no accepted record cites. The safe
  response to a missed event is the failure above.

### 7.12 Negative tests *(proposed, for OH-S4; none run here)*

| ID | Case | Asserts |
|---|---|---|
| NT-DL-1 **Δ3** **Δ4** | a fake child that ignores `SIGTERM` and never exits | the SN sequence runs: `SIGTERM` at c; `SIGKILL` after S3's capped sleep of `min(slice_ms, t_g − now)` (once, S4); capped sleeps in S5 while `t_g` has not been reached; the final reap attempt at or after `t_g`; then abandon with `abandoned: true`; the result is `error`; the assertions are on **the helper's scheduled waiting** (at most g, from one `t_g`) on a fake clock, and **not** on the child or on the time of return |
| NT-DL-2 **Δ3** | a fake child that cannot be reaped (a model of an uninterruptible call) | the helper abandons it, sends it **no further signal**, continues fail-closed, and leaks no descriptor of K |
| NT-DL-3 | code scan over every root helper | every wait carries a monotonic deadline; no unbounded `wait()` or `waitpid()`; `time.sleep` appears only inside a sliced wait; every file read carries a volume cap; **`os.kill` and `os.killpg` appear only inside SN (Δ3)** |
| NT-DL-4 | text and record scan | no document, record schema, log format or test states an elapsed time for a class-X operation or derives one from N1 … N4; the strings "bounded by S", "within Δ", "within about", "by the S grammar" are absent; a satisfied sizing rule is never recorded as a bound |
| NT-DL-5 | AP-0 with parameters that violate each of N1 … N4 | INVALID RUN; no lock object, no grant. A satisfying set is accepted **and** recorded as `sizing: "necessary-conditions-met"` |
| NT-DL-6 | the executor's `act_wait_s` expiry | HARD STOP `act-unconfirmed`; the executor mutates nothing; the holder is unaffected |
| NT-DL-7 | an oversize journal | `invalid-journal`; the read stops at `journal_max_bytes`; fail-closed |
| NT-DL-8 | the backstop literal and the loaded properties | `RuntimeMaxSec=` equals S_b and `TimeoutStopSec=` equals S; no `TimeoutStartSec=`; the baseline normalization carries them |
| NT-DL-9 | a fake manager implementing exactly R2 §8 (d), (e), (j), (o), (u) | signals at the stated offsets and no stronger behaviour; the interruption maps IM-L, IM-C, IM-B reproduce |
| NT-DL-10 | CL killed at each of L0 … L9 in a stepped harness | the state and first owner equal §7.9; a following backstop CL reaches `st1-verified` or a defined HARD STOP; none waits for a human |
| NT-DL-11 | CP killed at every point of the accepted (i) matrix | the states of [D §4.2.5-R5 (i)] hold; `ExecStart=` is never executed |
| NT-SG-1 | handler installation order | the handlers are installed before K, `grant.id`, the journal, AK-1, AM-1 and AM-2; a `SIGTERM` at every earlier point creates no grant |
| NT-SG-2 | AST scan of every handler | each assigns the flag and returns; no call, no raise, no write |
| NT-SG-3 **Δ3** **Δ4** | a flag set while each E wait is in progress | the wait observes it at the next wake-up on a fake clock (at most `slice_ms` of scheduled sleep, less when capped), runs the SN sequence on its child (scheduled reap waiting of at most g), abandons it if unreaped after the final attempt and returns `interrupted`; the flag neither shortens nor extends the grace |
| NT-SG-4 | a `SIGTERM` delivered between the last flag check and PF-6 | at most a brief G1; IGR removes it; nothing else remains |
| NT-PK-1 | a fake `pkcheck` that hangs | each call receives the SN sequence at c (**Δ3**); no call starts after P; the series' *scheduled waiting* totals at most P + c + g (**Δ4**; no assertion on the time of return) |
| NT-PK-2 | a fake polkit that keeps answering `authorized` for P − ε, then `not authorized` | CQ-5 passes only on the first `not-authorized`; with latency > P it fails closed |
| NT-PK-3 | exit statuses 3, 126, 127 and a signal death | counted as `error`, never as `not-authorized` |
| NT-PK-4 | AP-0 with parameters that violate the §7.6 grammar | INVALID RUN; no lock object, no grant |
| NT-PK-5 | code scan | every loop on a PK or lock path carries a monotonic deadline; there is no unbounded `while` and no sleep-count bound |
| NT-PK-6 | `removed-verified` | requires AV-1's `authorized` in the same activation and a later `not-authorized` from the same procedure |
| NT-PK-7 | `grant-not-seen` | the rule is removed by CL and the activation ends with no pass |
| NT-PK-8 | the backstop under a permanently failing PK | disarms after B firings and leaves a journal line; no unbounded loop |
| NT-HS-1 | `spawn()` | rejects `env=None`, `shell=True`, a relative `argv[0]`, `preexec_fn`, a missing deadline |
| NT-HS-2 | a child of `spawn()` | inherits no descriptor and carries exactly the closed map |
| NT-HS-3 **Δ3** **Δ4** | deadlines | a child that outlives its deadline receives the SN sequence, is waited for (scheduled sleeping) at most g from one `t_g`, abandoned after the final attempt, and the helper continues fail-closed |
| NT-SN-1 | the successful send — a fake child exits on `SIGTERM`; the fake kernel returns 0 | `SIGTERM` is recorded `sent`; the child is reaped at the next poll; **no `SIGKILL` is attempted**; `reaped: true`, `abandoned: false`; the enclosing result is `error` (PK: `unconfirmed`), **not** a decision derived from any partial output |
| NT-SN-2 **Δ4** | `SIGTERM` ignored — a fake child that ignores `SIGTERM` and exits on `SIGKILL` | `SIGKILL` is sent after S3's capped sleep of `min(slice_ms, t_g − now)`, or at once when none remains; two sends in all, one per signal (SN-3); the child is reaped |
| NT-SN-3 | `ESRCH` — (a) the fake kernel returns `ESRCH` for `SIGTERM` while the child is unreaped; (b) for `SIGKILL`; (c) `ESRCH` for both and the child never reaped | (a) recorded `esrch` with anomaly `esrch-while-unreaped`; not read as exit; `SIGKILL` is still attempted once; the reap wait continues; (b) as (a), no third send; (c) abandon with `abandoned: true` and both sends recorded |
| NT-SN-4 | every other send error — `EPERM`, `EINVAL`, `EINTR`, `EIO`, an `OSError` with no errno, a non-`OSError` exception, the primitive unavailable | each recorded exactly (`errno:⟨n⟩`, `exception:⟨class⟩`); **no retry** (SN-3); a `SIGTERM` failure sends `SIGKILL` at once after one reap attempt, **with no timed wait first**; a `SIGKILL` failure sends nothing more, sleeps only while `t_g` has not been reached, makes the final attempt, then abandons (**Δ4**); **no exception escapes the helper function**; the enclosing result is the fail-closed one |
| NT-SN-5 | the already-exited child — (a) the child exited and was reaped before the expiry decision; (b) the child exited but is unreaped when SN starts; (c) the child exits between the `SIGTERM` and the escalation | (a) **zero calls to the send primitive**; **Δ6:** the sequence ends at S7 (S1-a) with **zero sleeps, zero reap attempts, no S0 and no clock read (Δ7) and one `child` line**, never at S5; the result is still `error` because the deadline expired; (b) validation passes; the send returns 0 or `ESRCH`; the child is reaped at the next poll; (c) the poll before S4 reaps it and **no `SIGKILL` is sent** |
| NT-SN-6 | target-identity mismatch and a reuse simulation — a fake process table in which, after the helper's reap, the same PID and group number is assigned to an unrelated process group; a stepped scheduler interleaves reap and expiry events in every order | (a) the send primitive is **never called for a reaped handle**, the sequence ends at S7 with no sleep (S1-a, **Δ6**) and the unrelated group receives nothing; (b) **detector exercise, non-universal (Δ7):** corrupted handles with a **deliberately mismatching fake identity** (the `reaped` flag forced false while the table shows another process: `getpgid` ≠ `pgid`, `start_ticks` different, `pgid` equal to the helper's own group, `pid` ≤ 1, `pgid` 0 or negative) each give `not-sent(identity-mismatch)`, zero sends, capped reap waiting to `t_g` (**Δ4**), abandon, and nothing for the unrelated group; (c) an unreadable `/proc` gives `not-sent(identity-unverifiable)` and zero sends; both identity results go to S5 (S1-b, **Δ6**); **Δ7:** (a) is structural (it holds because the handle is `reaped`, whatever the table shows); (b) and (c) exercise SN-4 on handles built to differ and are **not** read as a guarantee against a coincidental reuse by a process of the same structural identity (SI-5, W-17) |
| NT-SN-7 | failure of `SIGTERM` followed by the escalation decision — the matrix {`SIGTERM`: `sent`, `esrch`, `eperm`, other errno, `not-sent`} × {child: exits on `SIGTERM`, ignores it, already reaped} | `SIGKILL` is attempted **if and only if** the child is unreaped and valid after S3 and not before; with a failed `SIGTERM` it is attempted at once; with a `not-sent` result **no** send of either signal is made (SN-4): **Δ6:** `not-sent(reaped)`, `not-sent(abandoned)` and `not-sent(reap-unknown)` end at S7 with no wait; `not-sent(identity-mismatch)` and `not-sent(identity-unverifiable)` go to S5 |
| NT-SN-8 | failure of `SIGKILL`, and the resulting reap and abandon — (a) `SIGKILL` returns an error; (b) `SIGKILL` returns 0 but the child (a model of an uninterruptible call) is not reaped before `t_g` | no further send; the sleeping stops at `t_g` and the final attempt follows (**Δ4**); `abandoned: true`, `last_signal: SIGKILL`, `sends` as returned; the operation returns its fail-closed result; **the abandoned child is never signalled again** (SI-4) |
| NT-SN-9 | the record — schema and ordering of `children[]`; the 64-entry cap with an `overflow` count; entries held in memory before the journal exists and flushed in order; a journal append that fails or stalls | every field of §7.5a.9 is present; a failed append changes no result and is recorded as a gap; `pk.abandoned` equals the count of abandoned PK children; a lost record (IM-S T6, states CS-1 … CS-6 and CS-9, **Δ6**) is the recorded condition `children-unknown` at the next procedure, derived from the missing terminal journal line and never from a search (**Δ4**); **Δ7:** `s0_ran` and `grace_deadline_ms` are present in every entry, `grace_deadline_ms` is an integer iff `s0_ran` is true and `null` otherwise, and the implications of GD-2 hold; `late` and `waits_skipped` are present and are observations |
| NT-SN-10 | the closed set and the sole sender — AST scan of every root helper | only the SN function references `killpg` or `kill`; `sig` ∈ {`SIGTERM`, `SIGKILL`}; no `pidfd_send_signal`, `raise_signal`, `os.abort`; no spawned `kill`, `pkill`, `killall`, `timeout` or `systemctl kill`; **IGR, GRR and CL-G contain no spawn and no send** |
| NT-SN-11 | no send from a handler — signals delivered at every step of the stepped harness, including inside SN | a handler only sets the flag (SG-2, SG-9); SN is not re-entered; no nested send; the SN sequence completes once |
| NT-SN-12 **Δ6** **Δ7** | **the sole reaper — structural properties (rewritten in R7).** (a) scans of every root helper: no thread creation; no `SIGCHLD` set to `SIG_IGN` or `SA_NOCLDWAIT`; no `wait*`, `waitpid`, `waitid`, `os.wait*`, `Popen.wait` or `Popen.communicate` outside `reap_step()`; no `poll()` of a child's `Popen` except in `reap_step()`; (b) a child handle's `state` is assigned in exactly three places: `reap_step()` (to `reaped`), S6 (to `abandoned`) and S8 (to `reap-unknown`); (c) every `Popen` object is kept referenced for the helper's life (SN-8 (c), RE-3), so a fake interpreter that runs destructors reaps nothing while a send decision can still be made; (d) **detector exercise, labelled non-universal:** a fake process table in which a foreign reaper is *injected* (a deliberate violation of the design precondition, SI-5) **and the fake identity now on the released number deliberately mismatches** (a different `pgid` or `sid` or, if PO-SN (d) is modelled, a different `start_ticks`); SN-4 then returns `not-sent(identity-mismatch)` or `not-sent(identity-unverifiable)` and the sequence goes to S5 with zero sends; this shows what the detector does **for that fake identity** and nothing more; (e) **boundary statement, not a guarantee:** the same injection with a fake identity of the **same** structural relationship (`pgid == pid == sid`) and no `start_ticks` check is **not asserted to be caught**; the case records that SN-4 may pass, and its only assertion is a text scan that no document, record or test says that validation detects a foreign reap or a coincidental reuse (SI-5, W-17) | (a) … (c) hold structurally; (d) holds only for the mismatching fake identity and is **not** read as a reuse defence; (e) states the limit: once the invariant is violated the design makes no reuse-safety claim from SN-4 alone, and **no case asserts that a send to a reused number cannot then happen**, and no document says so |
| NT-SN-13 | no result is evidence — a property test over every send result × every child behaviour × every PK series mode × the flag | no state exists in which `authorized`, `not-authorized`, `removed-verified`, `st1-verified`, `backstop-armed`, a pass, "exited" or "absent" is derived from a send result; an expired deadline always yields `error` |
| NT-SN-14 | a mutating child with an unknown effect — a fake `systemd-run` (AK-1) and a fake `systemctl stop` (BS-2) that are abandoned and later create the timer or stop it | the result is `error` and `effect: "unknown"` is recorded; no step reads it as "not created" or "not stopped". **The assertion that CL's by-name disarm is keyed to `backstop-intent` is deferred until A-I-16 is applied and is not asserted here** |
| NT-SN-15 | the PK subject — the SN-3 send after each call: success, `ESRCH`, an error, `not-sent` | the call's decision is unchanged in every case; a failed or unmade send leaves a subject abandoned and recorded (at most 60 s on a fake clock); it holds no descriptor of K |
| NT-SN-16 | a flag during an E wait and during the reap wait — the flag set at each point of S0 … S6 | it is observed at the next wake-up on a fake clock; the SN sequence runs once; the reap waiting is **neither shortened nor extended**; the helper returns `interrupted` after the reap or after the final attempt (CC-2, CC-9, **Δ4**) |
| NT-SN-17 | no timing claim — text and record scan | no document, record schema, log format or test states an elapsed time for a send, a validation, a reap attempt or the SN sequence, or says that the sequence returns within g; the only times stated are c, g and `slice_ms`, as *waits* (**Δ4**) |
| NT-SN-18 | the AP-0 gate — each of PO-SN (a), (b), (c), (e), (f) absent in turn from the accepted set; and (d), (g) and (c′) absent (**Δ4**, **Δ6**) | with any of (a), (b), (c), (e), (f) absent AP-0 is INVALID RUN, **no lock object and no grant exists**; with only (d) absent SN-4 (iv) is disabled, and with only (g) absent nothing changes: §7.9 already states the fate of a child after its helper ends as unknown to the design; **Δ6: with only (c′) absent, or present with either answer, nothing changes: AP-0 does not read it and no branch sends after a `reap-error` (RE-6)** |
| NT-WB-1 **Δ4** | a send consuming less than g — fake clock and fake kernel with a configurable cost per operation; g 2,000, `slice_ms` 100; `SIGTERM` costs 300 ms; the child ignores `SIGTERM` and never exits | the grace deadline is read **once** (a counter of reads is 1); S3's sleep is exactly 100 ms; `SIGKILL` is sent once after it, not `late`; every S5 sleep is at most `min(100, t_g − start)` and none starts at or after `t_g`; the sum of all scheduled sleeps is at most 2,000; the final attempt begins at or after `t_g`; the child is abandoned; the enclosing result is `error` |
| NT-WB-2 **Δ4** | a send consuming exactly g — `SIGTERM` costs exactly 2,000 ms | `now` equals `t_g` after the send: S3's sleep is skipped (the comparison is `≥`, WB-3); one reap attempt; `SIGKILL` once, `late: true`; S5's sleeps are skipped; the final attempt; scheduled sleeping is 0; `waits_skipped` is true |
| NT-WB-3 **Δ4** | a send consuming more than g — `SIGTERM` costs 2,500 ms | as NT-WB-2; the elapsed time exceeds g and the test asserts **no bound on elapsed time** (WB-6); no sleep starts at or after `t_g` |
| NT-WB-4 **Δ4** | a send leaving less than one slice — `SIGTERM` costs 1,960 ms | S3's sleep is exactly 40 ms and not 100; S5 sleeps 0 times because `t_g` is reached; the total scheduled sleeping is 40 ms; the final attempt follows |
| NT-WB-5a **Δ4** **Δ5** | **slow S1** — fake clock, g 2,000, `slice_ms` 100; S0 reads `t_g = t0 + 2,000`; **S1's validation costs 2,100 ms** (returns at t0 + 2,100, at or after `t_g`); `SIGTERM` and `SIGKILL` cost 20 ms each; clock reads and reap attempts cost 0; the child ignores `SIGTERM` and never exits | the grace deadline is read **once**, before S1 (a counter of reads is 1). After S1 has consumed g no timed wait begins: **S3's sleep is skipped** (`now ≥ t_g`, WB-3) and **S5 makes no sleep** (its first attempt begins at or after `t_g` and is the final attempt). `SIGTERM` is still sent once (S2 follows S1) and returns at t0 + 2,120: `late: true`. One reap attempt (S3); `SIGKILL` once at S4 (WB-4), returns at t0 + 2,140: `late: true`; the final attempt; the child is abandoned. Scheduled sleeping is **0 ms**; `waits_skipped` is true; the enclosing result is `error`. **Shared with NT-WB-5b:** one `t_g`, no restarted grace, no timed wait begins at or after it, each send is attempted at most once, scheduled waiting is at most g, and no assertion gives the validation, a send or a reap attempt an elapsed-time bound |
| NT-WB-5b **Δ5** | **slow S4** — the same clock and parameters; **S1 costs 10 ms**; `SIGTERM` costs 20 ms and returns at t0 + 30 (before `t_g`); the child ignores `SIGTERM` and never exits; **S4's second validation costs 2,100 ms**; the `SIGKILL` costs 20 ms; clock reads and reap attempts cost 0 | one `t_g` read, before S1. `SIGTERM` is **not** `late`. S3's first attempt at t0 + 30 finds the child unreaped and `now < t_g`, so S3 makes **one sleep of `min(100, t_g − now)` = 100 ms** (it begins before `t_g`, so it is allowed), then its second attempt, then S4. S4's validation returns at t0 + 2,230, at or after `t_g`; `SIGKILL` is **still sent once** (WB-4) and returns at t0 + 2,250: `late: true`. S5's first attempt begins at t0 + 2,250, at or after `t_g`, so it is the **final attempt and S5 makes no sleep**; the child is abandoned. Scheduled sleeping is **100 ms**, at most g; `waits_skipped` is true (S5's sleeps); the enclosing result is `error`. The assertions shared with NT-WB-5a hold |
| NT-WB-6 **Δ4** | an expired deadline before S3 and before S5 — (a) the fake clock jumps past `t_g` between S2's return and S3; (b) between S4's return and S5 | (a) S3 skips its sleep; (b) S5 makes only the final attempt; in both, zero sleeps begin at or after `t_g`; nothing restarts the grace |
| NT-WB-7 **Δ4** | successful and failed sends — the matrix {`SIGTERM`: `sent`, `esrch`, `eperm`, another errno, an exception} × {`SIGKILL`: `sent`, `esrch`, an error} × {the child exits on `SIGTERM`, only on `SIGKILL`, never} | for every combination: at most one `SIGTERM` and one `SIGKILL`; a failed `SIGTERM` skips S3's sleep; a `sent` `SIGTERM` followed by the child's exit ends the sequence at S3 with no `SIGKILL`; the sum of sleeps is at most g; the enclosing result is the fail-closed one; no send result sets a child state |
| NT-WB-8 **Δ4** | a child reaped at the boundary — (a) the child exits at `t_g − 1 ms`, during S5's last sleep; (b) exactly at `t_g`; (c) at `t_g + 1 ms`; an exit at time τ is visible to any attempt that begins at or after τ | (a) and (b) the final attempt reaps it: state `reaped`, anomaly `reaped-at-or-after-deadline`, the enclosing result unchanged, no abandon; (c) the final attempt finds it unreaped and the child is abandoned; in all three no sleep follows the final attempt and no further signal is sent |
| NT-WB-9 **Δ4** | a child that exits during a send — it exits inside the `SIGTERM` call; in a second run inside the `SIGKILL` call | the send is recorded as returned (`sent` or `esrch`); the next reap attempt reaps the child; in the first run **no `SIGKILL` is sent**; in both the state is `reaped` and the pinned numbers were never reused (SI-2) |
| NT-WB-10 **Δ4** | the cap on the other E waits (CC-10) — c 5,000, `slice_ms` 100, a wake-up at 4,960 ms; the same for the lock loop (λ), BSP's retries and the PK schedule | the sleep is 40 ms; no sleep of any E wait crosses its own deadline; the sum of each wait's sleeps is at most its own deadline |
| NT-WB-11 **Δ4** | no new grace — a property test over generated schedules: random costs for validation, send and reap attempt, random send results, random child exit times, random flag times | (i) **Δ7:** exactly one grace-deadline read per child for which S0 ran, and none for a child for which it did not (a pre-S0 `reap-error`, a settled handle); (ii) no sleep begins at or after `t_g`; (iii) every sleep is at most `min(slice_ms, t_g − start)`; (iv) the sum of the sleeps is at most g; (v) at most one `SIGTERM` and one `SIGKILL`; (vi) exactly one final attempt unless the child was reaped earlier, and no sleep after it; (vii) the enclosing result is the fail-closed one; (viii) **no assertion states or implies a bound on elapsed time**; (ix) **Δ6:** with a reap-attempt exception injected at a random attempt, no send and no sleep follows it (RE-1, RE-4) |
| NT-WB-12 **Δ4** | text and record scan of the design documents, the operational draft's successor and the record schema, excluding tables of withdrawn claims | none says that the sequence returns within g, that everything from S0 to S6 sits inside g, that both signals or the sends sit inside g, or that `SIGKILL` follows only after a full `slice_ms`; `grace_deadline_ms` (**Δ7:** an integer iff `s0_ran`, otherwise `null`), `s0_ran`, `late` and `waits_skipped` are in the schema as observations |
| NT-IS-1 **Δ4** **Δ5** | matrix completeness — a stepped harness with a fake kernel whose truth about the direct child is a free variable (not reaped; reaped at a chosen instant inside `waitpid`) interrupts the helper at every cell of the matrix (T0 … T7, **T3k, T5k, T3x and T5x included**, × `u`, `i`, `x`, `s`, `e`, `f`), once in each phase RA-0 … RA-4 and RA-E (**Δ6**: a raise before and a raise after the kernel's reap) of each reap attempt (the attempts of S3, the loop and the final attempt of S5, and the enclosing wait's polls), and proves every dash unreachable | each reachable cell has exactly the state the matrix names, **and the harness's truth about the direct child is permitted by that state in every run: not reaped for CS-1 … CS-4, CS-6 and CS-8; reaped in the kernel for CS-5 and CS-7; **Δ6:** either, in separate runs with an identical design-visible state, for CS-9 and CS-10**; a reachable cell whose state forbids the harness's truth fails the case; no cell is unclassified; every dash is unreachable in the harness (**Δ6:** T5 `u`, T5k `u` and T5x `u` included, and no run places a settled handle at T0 or T1); every `T⟨n⟩`, `T⟨n⟩k`, `T⟨n⟩x`, `RA-⟨n⟩`, `RA-E`, `RE-⟨n⟩`, `RB-⟨n⟩`, `CS-⟨n⟩`, `IS-⟨n⟩` and `WB-⟨n⟩` reference in the design resolves to an existing row |
| NT-IS-2 **Δ4** | success — the helper ended at T2, T3, T4 and T5 after `sent` for `SIGTERM` and for `SIGKILL`; the fake child is alive in one run and exited-unreaped in another | CS-3 or CS-4 as the matrix says, **the same in both runs**; no `children` entry; the owner is the row of SN-RO for the enclosing procedure; no step infers exit or reaping from `sent` |
| NT-IS-3 **Δ4** | `ESRCH` — as NT-IS-2 with the fake kernel returning `ESRCH` while the child is alive | the same state as for `sent`; no step infers absence |
| NT-IS-4 **Δ4** | other send errors — `EPERM`, `EINVAL`, `EINTR`, `EIO`, an exception, the primitive unavailable, for `SIGTERM` and for `SIGKILL`; the child alive and exited-unreaped | the same states; no retry and no further send by anyone after the helper's end; partial escalation (CS-3) is reached when `SIGKILL` is never attempted |
| NT-IS-5 **Δ4** | identity rejection — a mismatch and an unverifiable handle, at S1 (T1, T5) and at S4 (T4, T5) | CS-2 or CS-3; **zero sends** when S1 rejects, and no `SIGKILL` when S4 rejects; the capped reap waiting is the only thing that continues while the helper lives; no state is derived from the rejection; **Δ6:** the sequence goes to S5 and never to S7, and the same identity cases at S4 go to S5 |
| NT-IS-6 **Δ4** **Δ5** **Δ6** | an unmade send — the helper ended at T0 and T1 with a `running` handle, and with a handle that an enclosing poll left `reaped`, or `reap-unknown`, before SN, or (a defensive re-entry) `abandoned` | CS-1 at T0 and T1 with a `running` handle; **for a settled handle no T0 or T1 exists: the helper is at T6** (CS-5, CS-9 or CS-6) **until S7's line is durable, then at T7** (CS-7, CS-10 or CS-8) (CC-23, **Δ6**); no `children` entry for CS-1; the fake kernel records zero send calls, and S7 makes zero waits |
| NT-IS-7 **Δ4** | death during a send — the helper ended inside the `SIGTERM` call and inside the `SIGKILL` call; in one run the fake kernel queued the signal and in another it did not | CS-3 and CS-4 respectively **in both runs**; the harness can see whether the signal was queued, the recorded state cannot; a property test asserts equality of the design-visible state |
| NT-IS-8 **Δ4** **Δ5** | reaping — T3k, T5k, T6 and T7 with a fake child that exits and a fake grandchild in the same group that stays alive; the helper is ended at **each phase of one attempt** while the fake kernel reaps the child inside the `waitpid` call at a configurable instant: (a) before the call (RA-0), (b) inside the call before the reap (RA-1), (c) after the reap and before the handle-state update (RA-2), (d) after the handle-state update and before the durable line (RA-3), (e) after the durable line (RA-4) | (a) and (b): T3 or T5, **not** CS-5 (CS-2, CS-3 or CS-4 as the history says); (c): **T3k or T5k, CS-5**, handle `running`, no line; (d): **T6, CS-5**, handle `reaped`, no line; (e): T7, CS-7. In (c) and (d) the state says only that the direct child was reaped in the kernel; no assertion and no record states that the group is empty; the grandchild stays alive and unrecorded; a later procedure sees no reap fact for (a) … (d) (IS-9) |
| NT-IS-9 **Δ4** | abandonment — T6 and T7 with a child that never exits | CS-6 and CS-8; `abandoned: true` is in a durable line only for CS-8; the next procedure records `children-unknown` for CS-6 and reads the line for CS-8; nothing searches for or signals the child |
| NT-IS-10 **Δ4** | owner by enclosing procedure — a fake manager that implements exactly [R2 §8 (e)] with a switch for PO-SN (e), for the holder, CP, stop-post CL and the backstop service | with the switch on, the unit's cleanup delivers its signals to the remaining processes and no record changes; with it off the design names no owner but the boot; in neither case is exit or reaping recorded because of a delivery |
| NT-IS-11 **Δ4** | the interactive `attest` — interrupted at every point T0 … T7 (T3k, T5k, T3x and T5x included) and for every outcome | **no automatic owner** is assigned or claimed and no unit cleanup is modelled; the executor reports `children` or `children-unknown` and does not act; no process search, no send, no retry |
| NT-IS-12 **Δ4** | the boot — a model boot after each state | every process ends; no `child` line is created or changed; no state becomes `signalled`, `exited` or `reaped` on the boot's account (IS-7); a scan finds no field derived from a boot |
| NT-IS-13 **Δ4** | mutating children — a fake `systemd-run` and a fake `systemctl stop` at every point and outcome | `effect: "unknown"` wherever the result is `error`, `interrupted` or abandoned, and for the next procedure in every state CS-1 … CS-10; no step reads "not created" or "not stopped"; the enclosing result is fail-closed; no retry; no search |
| NT-IS-14 **Δ4** | lost child records — the holder, CP, CL and an `attest` session ended at T0 … T6 (T3k, T5k, T3x and T5x included), and a `child` append that fails or stalls | the next procedure records `children-unknown {helper_role, missing_terminal_line}` and no count; with the terminal line present and only the `child` line lost, the gap is recorded as in NT-SN-9; the grant, the lock and the records of the enclosing step are those of IM-A, IM-L, IM-C or IM-B in every case |
| NT-IS-15 **Δ4** | text scan of the design documents, excluding tables of withdrawn claims | absent: "unsignalled by anyone", "killed, or alive in an uninterruptible call", "signalled" used as a child state without "attempted", "as S0", "as S3"; no sentence derives exit, reaping, absence or group emptiness from a send result or from the reaping of the direct child |
| NT-IS-16 **Δ5** | the reap-attempt boundary — one fake child and one fake kernel; every attempt of the sequence (S3's two attempts, S5's loop and the final attempt) and the enclosing wait's poll; for each attempt the helper is ended in each of RA-0, RA-1, RA-2, RA-3 and RA-4, in a run where the child is alive at the call, in a run where it exited and is unreaped, and in a run where it exits during the call, and (**Δ6**, RA-E) in a run where the call raises before the kernel reaps and in a run where it raises after | the five positions are told apart by state and by nothing else. **Before the call and inside the call before a reap:** T3 or T5, the child not reaped (CS-2 … CS-4). **After the kernel reap, before the handle-state update:** T3k or T5k, CS-5, handle `running`, no line, and no act was made in the window (RB-3). **After the handle-state update, before the durable line:** T6, CS-5, handle `reaped`. **After the durable line:** T7, CS-7. **After a raise, before S8's update (RA-E, Δ6):** T3x or T5x, CS-9, handle `running` and not known to be exact, no line, no act made, **identical in both runs**. An attempt that finds the child unreaped never reaches RA-2; the final attempt's RA-0 and RA-1 are T5 and never T6; **no interruption inside an attempt is classified T6**; the stale `running` handle is never used to send; the enclosing wait's poll gives CS-1, CS-5 or CS-9 before T0 (RB-2) |
| NT-IS-17 **Δ5** | the conservative observer rule — the helper ended at T3k, T5k and T6 (each a kernel reap with no durable line), at T3x, T5x and T6 after S8 (**Δ6**, each a raised attempt with no durable line) and at T7, with a fake grandchild alive in the child's group; the next procedure is a stop-post CL, a backstop CL or an `attest` | for T3k, T5k, T3x, T5x and T6 the next procedure finds no `child` line, records only the applicable gap or `children-unknown {helper_role, missing_terminal_line}`, derives no reap fact, does not state or imply that the child is gone, exited or reaped, does not state or imply that the group is empty, and does not search for, signal or retry anything; for T7 it reads the line (`reaped: true`, or **Δ6** `reap_unknown: true` for a suppression) and still states nothing about the group or about which truth holds; a text and record scan finds no field derived from a kernel reap that no line records (IS-9) |
| NT-RE-1 **Δ6** | **a `reap-error` before a kernel reap, at S3** — a fake kernel with a process table, one send counter per signal and a free variable *truth* for an injected `OSError` raised by `Popen.poll()`: **before** (the exception comes before the fake `waitpid` consumes the status; the child stays in the table, pinned). g 2,000, `slice_ms` 100, fake clock, t0 = 0; S1 costs 10 ms; `SIGTERM` costs 20 ms and returns `sent` at 30; the child ignores `SIGTERM`. Variants: (i) S3's first attempt (at 30) raises; (ii) S3's first attempt returns unreaped, S3 sleeps 100 ms (30 → 130) and its second attempt raises | S8 at once: handle `reap-unknown`; **zero further sends** (counters: `SIGTERM` 1, `SIGKILL` **0**; S4 is not entered, S5 is not entered); no second poll of the object; no `/proc` read and no process search after the error; scheduled sleeping 0 ms in (i) and exactly 100 ms in (ii), none after the error; `t_g` read once; `waits_skipped` true; the record: anomaly `reap-error`, `reap_unknown` true, `send_suppressed` true, `reaped` false, `abandoned` false; the enclosing result `error` (PK: `unconfirmed`); the handle and the `Popen` object are still referenced when the helper ends |
| NT-RE-2 **Δ6** | **a `reap-error` after a kernel reap, at S3** — as NT-RE-1, with *truth* **after**: the fake `waitpid` consumes the status, **releases the PID and the process-group number to the pool, and an unrelated process group G′ is created on the released number at the next instant**, and then the exception is raised. Variants (i) and (ii) | every assertion of NT-RE-1 **and**: G′ receives **zero** signals (its counter is 0 throughout); **no PID or group reuse exposure**, because no send follows the error; the design-visible state, the record and the sequence are **byte-identical to NT-RE-1** (the harness's truth differs, nothing the design can see does); no field says `reaped`; the state is `reap-unknown`, the truth is indeterminate to the design (RE-2) |
| NT-RE-3 **Δ6** | **a `reap-error` before a kernel reap, at S5 (the loop)** — as NT-RE-1 up to S3: the child ignores `SIGTERM`; S3 sleeps 100 ms (30 → 130) and its second attempt finds the child unreaped; S4 validates and sends `SIGKILL` (20 ms), `sent`, returning at 150; S5's first attempt (at 150, before `t_g` = 2,000) raises, *truth* **before**. Variant: a later loop attempt raises | **two sends in all, both made before the error** (`SIGTERM` 1, `SIGKILL` 1); **none after**; no sleep after the error (scheduled sleeping 100 ms, or 100 ms plus the S5 sleeps already made in the variant); no abandon (the final attempt is never made); no second poll; state `reap-unknown`; the record shows both sends as history; the enclosing result `error`; `t_g` read once, never extended (RE-4) |
| NT-RE-4 **Δ6** | **a `reap-error` after a kernel reap, at S5 (the loop)** — as NT-RE-3 with *truth* **after** (the numbers are released and G′ is created on them) | every assertion of NT-RE-3 **and** G′ receives zero signals; byte-identical design-visible state, record and sequence to NT-RE-3 |
| NT-RE-5 **Δ6** | **a `reap-error` before a kernel reap, at the final attempt** — as NT-RE-3, but every S5 attempt returns unreaped: S5 attempts at 150, 250, … 1,950 each followed by a capped sleep, the last of 50 ms to `t_g` = 2,000; the **final attempt** (it begins at 2,000, at or after `t_g`) raises, *truth* **before** | scheduled sleeping is 1,950 ms in all (100 in S3, 1,850 in S5), at most g; **no abandon**: the raised final attempt goes to S8 and not to S6; state `reap-unknown`; no further send (`SIGTERM` 1, `SIGKILL` 1, both made before); no sleep after `t_g`; the enclosing result `error`; the record shows `reap_unknown` and not `abandoned` |
| NT-RE-6 **Δ6** | **a `reap-error` after a kernel reap, at the final attempt** — as NT-RE-5 with *truth* **after** | every assertion of NT-RE-5 **and** G′ receives zero signals; byte-identical to NT-RE-5; the child is recorded neither `reaped` nor `abandoned` |
| NT-RE-7 **Δ6** **Δ7** | **a `reap-error` in a poll of the enclosing E wait, before S0** — c 5,000; a wake-up poll at 1,000 raises, both truths; no deadline has expired and no flag is set; the child's handle is `running` and has no `t_g` | the wait ends at once through S8 and S7: **zero sends of any kind (not even `SIGTERM`)**, zero sleeps after the error, state `reap-unknown`, the wait's result `error`; **S0 never ran: `t_g` reads 0, clock reads by SN 0, `s0_ran` false, `grace_deadline_ms` null (GD-1 … GD-3), `outcome` `reap-error`, `sends` `[]`, `waits_skipped` false**; a later SN call on the same handle is `not-sent(reap-unknown)` with no call, no wait, **no S0, no clock read and no second line** (S1-a, GD-4); G′ receives zero signals in the *after* run; NT-GD-1 states the full record |
| NT-RE-8 **Δ6** | **interruption around a raised attempt** — the helper ended at RA-E (T3x and T5x), after S8's update and before the line (T6), and after the line (T7), in both truths | CS-9, CS-9 and CS-10 respectively, **in both truths**; the helper makes no further send; a later procedure sees no line for T3x, T5x and T6 and records `children-unknown`, and sees `reap_unknown: true` for T7; **no later procedure derives *reaped*, *unreaped*, *alive*, *gone* or *the group is empty* from either** (IS-10); no search, no send, no retry |
| NT-RE-9 **Δ6** | **the PK subject** — `SIGKILL` is sent at S4 and returns `sent`; S5's first attempt raises | the subject is `reap-unknown`, is signalled no further, lives at most 60 s on the fake clock, and the call's decision (already given by `pkcheck`'s exit status) is unchanged; the series' scheduled waiting is unchanged; the record and `children-unknown` rules are as NT-RE-8 |
| NT-RE-10 **Δ6** | **a mutating child** — a fake `systemd-run` (AK-1) and a fake `systemctl stop` (BS-2) whose reap attempt raises, both truths, after the fake child created the timer or stopped it | `effect: "unknown"` is recorded; the enclosing result is the fail-closed one (`error`; AK-1 exits non-zero and CL runs); **no step reads "not created" or "not stopped"**; no retry; no process search; no later send |
| NT-RE-11 **Δ6** | **no later signal, retry, alternate primitive or search** — an AST scan and a property test over random attempt positions, random truth, random prior send results and random flag times | after the first `reap-error` of a child the counters for `killpg`, `kill`, any other send primitive, `poll`, any `wait*`, `sleep`, `/proc` reads and spawns concerning that child are **0**; at most the sends made before the error exist; the state `reap-unknown` is permanent; `t_g` reads are **exactly one if S0 ran before the first error and zero if it did not** (Δ7), never a second and never one created after the error; the enclosing result is fail-closed; no field of any record is derived from the error (INV-24) |
| NT-RE-12 **Δ6** | **either answer to PO-SN (c′)** — the whole of NT-RE-1 … 11, NT-RE-8 and NT-GD-1 run against a fake `Popen` that **never raises after the reap** and against one that **can**; AP-0 modelled with (c′) accepted as *possible*, accepted as *not possible* and *not established* | the design's behaviour, records and send counters are **identical** under every combination; AP-0's outcome does not depend on (c′); **Δ7:** the record of NT-RE-7 and NT-GD-1 (`s0_ran` false, `grace_deadline_ms` null, `outcome` `reap-error`) is identical under every combination; **no combination yields a send after a `reap-error`**, so no answer can make AP-0 pass an unsafe branch (RE-6) |
| NT-NS-1 **Δ6** | **S1-a, `not-sent(reaped)`** — an enclosing wait's poll reaped the child (RA-3 of that poll) and SN is then entered; the helper is ended (i) before S1's verdict, (ii) during S1, (iii) after the S1 branch and before S7's line is durable, (iv) after the line | **T0 and T1 are never entered**: (i) … (iii) are **T6**, cell `u`, CS-5; (iv) is **T7**, cell `u`, CS-7; **zero send calls, zero sleeps, zero further reap attempts** in every run, and **(Δ7) no S0 and no clock read, so no `t_g` is created and `grace_deadline_ms` stays `null`**; handle `reaped` throughout; the record is absent in (i) … (iii) and one `child` line in (iv); the enclosing result is unchanged (`error`); the sequence never reaches S5 |
| NT-NS-2 **Δ6** | **S1-a, `not-sent(abandoned)`** — a defensive re-entry of SN on a handle that S6 abandoned (in one run its `child` line failed to append, in another it is durable); the helper is ended before S1's verdict, during S1, after the branch and after S7 | T6 cell `u`, **CS-6** where no line is durable; T7 cell `u`, **CS-8** where it is; zero send calls, zero sleeps, **no S0 and no clock read (Δ7)**; the handle stays `abandoned`; the integer `grace_deadline_ms` already recorded by its earlier S0 is unchanged; the line is **not rewritten and not retried** (S7) |
| NT-NS-3 **Δ6** | **S1-a, `not-sent(reap-unknown)`** — a re-entry of SN on a `reap-unknown` handle (NT-RE-7); the same four positions | T6 cell `u`, **CS-9**; T7 cell `u`, **CS-10**; zero send calls, sleeps and polls, **no S0 and no clock read (Δ7)**; the handle stays `reap-unknown`; `grace_deadline_ms` stays `null` |
| NT-NS-4 **Δ6** | **S1-b, `not-sent(identity-mismatch)`** — a `running` handle whose `getpgid` differs; the child is alive and ignores every signal; the helper is ended (i) before S1 (T0), (ii) during S1's validation (T1), (iii) after the verdict and before S5's first attempt (T1), (iv) inside S5's attempts at RA-0 and RA-1 (T5), (v) at RA-2 (T5k), (vi) at RA-E (T5x, an injected raise), (vii) after the decision (T6), (viii) after the line (T7) | the cells are: (i) `u` CS-1; (ii) `u` CS-1; (iii) `i` CS-2; (iv) `i` CS-2; (v) `i` CS-5; (vi) `i` CS-9; (vii) `i` CS-5 if reaped or CS-6 if abandoned; (viii) `i` CS-7 or CS-8; **zero send calls in every run**; the sequence goes to S5 (S5 only, never S7 before its decision); S5's sleeps are capped by `t_g` and none begins at or after it; the handle is `running` until the decision |
| NT-NS-5 **Δ6** | **S1-b, `not-sent(identity-unverifiable)`** — as NT-NS-4 with an unreadable `/proc` | the same cells and assertions; zero send calls; S5 only |
| NT-NS-6 **Δ6** | **the PK-only S4 path** — a PK subject: S1 passes with no send; S4's second validation returns (a) `identity-mismatch`, (b) `identity-unverifiable`; and a forced model in which the handle is `reaped`, `abandoned` or `reap-unknown` at S4 | (a), (b): **no `SIGKILL`**, the escalation closes, the sequence goes to S5; the interrupted cells are T4 `u` CS-1 (PK), T4 `i` CS-2 (PK), T5 `i` CS-2 (PK), then T5k, T5x, T6, T7 as NT-NS-4. The forced settled handle (unreachable by construction) makes **no call and no wait and goes to S7**; in no case is a send made after a `not-sent` |
| NT-NS-7 **Δ6** | **no send after any `not-sent`** — a property test over {reaped, abandoned, reap-unknown, identity-mismatch, identity-unverifiable} × {S1, S4} × {PK subject, other child} × random clock costs | the send counter does not move after the verdict; the first three end at S7 with **zero waits**; the last two go to S5 with capped waits and the final attempt; no case reaches S5 from S1-a |
| NT-NS-8 **Δ6** | **cell and dash audit after the S1 split** — the harness generates every pair (point, outcome) that table SN-S can reach, with every settled-handle and identity branch, and compares it with the matrix of §7.9 | every reachable pair has exactly the cell the matrix names; **every dash is produced by no run**, in particular T5 `u`, T5k `u`, T5x `u`, T3 `u`, T3x `u`, and any settled handle at T0 or T1; the outcome `u` appears only at T0, T1, T4 (unmade) and, for a settled handle, at T6 and T7 |
| NT-GD-1 **Δ7** | **the pre-S0 `reap-error`, field by field** — fake clock and fake kernel; c 5,000, g 2,000, `slice_ms` 100; the child is alive; the enclosing E wait sleeps 1,000 ms (capped, WB-2) and polls; the poll raises, in a *before* run and in an *after* run (the numbers released and an unrelated group G′ created on them); no deadline has expired, no flag is set; counters for `t_g` reads, clock reads by SN, sends per signal, polls, sleeps after the raise, `/proc` reads and spawns | the poll raises, then S8, then S7: **`t_g` reads 0; clock reads by SN 0; sends 0 (`SIGTERM` 0, `SIGKILL` 0); further polls 0; sleeps after the raise 0; `/proc` reads and searches 0; grace periods started 0**; handle `reap-unknown`; the entry has exactly the fields of §7.5a.6e step 3: `s0_ran` false, `grace_deadline_ms` null, `outcome` `reap-error`, `sends` `[]`, `waits_skipped` false, `reaped` false, `abandoned` false, `reap_unknown` true, `send_suppressed` true, `last_signal` null, `anomalies` `["reap-error"]`; the check `s0_ran == (grace_deadline_ms != null)` passes; the enclosing operation returns `error` (PK `unconfirmed`); G′ receives 0 signals; the two runs are byte-identical in everything the design can see |
| NT-GD-2 **Δ7** | **the iff over every path** — a generated population of children: exits within c; spawn failure; a pre-S0 raise (both truths, every poll position); an SN call on a settled handle (`reaped`, `abandoned`, `reap-unknown`); and full sequences (every send outcome, every exit time, a raise at S3, S5 and the final attempt, an abandon) | for every entry `s0_ran == (grace_deadline_ms != null)` and the implications of GD-2 hold; entries with `s0_ran` true have **exactly one** `t_g` read and entries with it false have **zero**; no entry omits the key, holds `0` or a negative value, or carries a placeholder; `outcome == "reap-error"` occurs only with `s0_ran` false |
| NT-GD-3 **Δ7** | **a later SN call on a settled handle** — the handle of NT-GD-1 (and, separately, one reaped by an enclosing poll and one abandoned after an S0) is passed to SN again at every position of the helper's remaining life | no S0, no clock read, no call, no wait; S1-a, then S7; **the `child` line is not written a second time** and the entry is unchanged; for the abandoned handle the integer already recorded and `s0_ran` true are unchanged; no `t_g` is created for the other two |
| NT-GD-4 **Δ7** | **text and schema scan** — the record schema, §7.5a.9, §8.5, INV-22, INV-26, Appendix B's successor text and every case of §7.12 | no schema, invariant or case states that **every** child has a grace deadline or that `grace_deadline_ms` is an unconditional integer; a statement about a **signalled** child's sequence (whose S0 ran by definition) may say that it has one `t_g`, and every statement about children in general says *at most one: one if S0 ran, none otherwise*; the **historical** tables (§0.5 … §0.8, W-1 … W-16) are excluded and not rewritten |

---

## 8. The repaired activation design, integrated

This section restates the machines, windows, owners, records and invariants that
change. Everything not listed here stays as the accepted D3-R6 text states it
(§8.8). Rows marked **Δ** differ from the accepted text. Rows marked **Δ2** differ
from R1 as well, because of R2-F1 or R2-F2.

### 8.1 Three coordinated machines

**Machine H, the holder** (steps of [D §4.2.5-R2 (d)], with the §4 … §7 deltas):

| Step | Where | Action | Grant after | On failure |
|---|---|---|---|---|
| AP-0 **Δ2** | executor, unprivileged | as accepted, **plus**: PO-20 (f′), PO-21 (c′), (s′) and PO-11 (d′) accepted for the observed versions, **and PO-SN (a), (b), (c), (e), (f) (Δ3; Δ6: (c′) is evidence only and AP-0 does not read it; Δ7: this condition is unchanged, and SI-5 adds none)**; the parameter grammar and sizing rules N1 … N4 of §7.6 evaluated (necessary conditions only); the digests of **every root-procedure image and `rp11_h1.py` (or its Route 3 successor)** equal the H-1 record's; `K` absent; the loaded unit's `ExecStartPre` normalized to the form the Route 3 outcome fixes; `T_s` finite; the backstop literal carries BS-RM | none | INVALID RUN; nothing mutated |
| AP-1 | executor | create the `ACT` evidence directory (consumes the identifier) | none | INVALID RUN |
| AP-2 **Δ2** | executor, privileged | issue the holder literal, which starts the holder through the first image the Route 3 outcome fixes. The executor then waits **at most `act_wait_s`** for the `act` record or the holder's end (§7.3 row 5) | none | as accepted; expiry is HARD STOP `act-unconfirmed`, acting on nothing |
| SG-1 **Δ2** | holder | the **first act**: install the handlers of the set H (§7.8). Nothing exists yet | none | a signal before this point ends the process with nothing created |
| AM-0 **Δ** | holder | (i) re-check `boot_id`, `/run` and every AP-0 absence condition, **K included**; (ii) create K by exclusive `mkdirat`, open it `O_CLOEXEC`, verify it, take `flock(LOCK_EX\|LOCK_NB)` (LD-1, LD-2); (iii) read the baseline under **BSP** (SD-1); (iv) create the journal and append `run-start {…, lock, capture, helper, params}` (§8.5) | none | exit non-zero; IGR is a no-op; CL |
| AK-1 **Δ2** | holder | append `backstop-intent`; issue the backstop literal (with BS-RM) through `spawn()`; require the timer `active`; append `backstop-armed {timer, period_s, max, runtime_s}`. No activation file exists before this commit | none | exit non-zero; CL |
| AM-1, AM-1R | holder | PT builds tree **P** (and tree **R**) | none | as accepted |
| AM-1G **Δ2** | holder | create `K/grant.id` (GI-1) with the staged rule's identity, **before** the link | none | exit non-zero; CL; no rule exists |
| AM-2 | holder | PF publishes the rule. **The flag is checked immediately before PF-6** (SG-4). **The grant is live from PF-6**, and the flag is checked again at the next statement | **G1** | exit non-zero; IGR; CL |
| AV-1 **Δ** | holder | both files re-verified; H-2b; **PK/2 seek-authorized for verb `start`** (P); **PK/2 first-decisive for verb `stop`** must be `not-authorized` (AR-7) | G1 | IGR; CL |
| AM-3 | holder | PF publishes `⟨activation_id⟩.act.json` (`activated`): **`ACT` PASS** | G1 | as above |
| `hold-start` **Δ** | holder | re-read per SD-1 (`τ = τ₀`, empty `Job`, quiescent); append `hold-start`; `fsync`; **close K** | G1 | OS-7: `hold-end {start-before-hold}`; IGR; CL |
| HL **Δ** | holder | observe every Δ without the lock. On a terminal reason: `LOCK_NB` on K once; re-observe; append `hold-end`; `fsync`; **close K**; exit | G1 → G2 | IGR on every catchable end |
| end **Δ2** | holder | **IGR** (§5.7: GRR, then one best-effort evidence line), then exit; then PID 1 runs `ExecStopPost=` CL if it can | G2 | RL ladder |

**Machine C, the capture unit's attempt** (CQ steps of [D §4.2.5-R5 (e)], deltas only):

| Step | Change | Why |
|---|---|---|
| CQ-0 | none | |
| CQ-1 **Δ** | opens **K** (derived from the `activation_id` of CQ-0) `O_CLOEXEC`, one `LOCK_EX\|LOCK_NB`. K absent or unopenable is `consume-unidentified` (nothing created) | LD-1, LD-8 |
| CQ-2, CQ-3 | none. CQ-3's grant-priority form and its removal are unchanged, and **CQ-3 keeps its accepted order after the claim** (GR-2 does not apply to it) | G1 |
| CQ-4 **Δ** | `τ = τ₀` is justified by SD-1 (no change to the check); K closed on every failure path | §6 |
| CQ-5 **Δ** | PK/2 **seek-not-authorized**, budget P; `unconfirmed` is `consume-failed {CQ-5, removed-unconfirmed}` | §7 |
| CQ-6 | none | |
| CQ-7 **Δ** | `run-end`, `fsync`, **close K**, exit `0` | LD-4 |

**Machine G, the grant object** (§3): `G0 → G1` at AM-2 (the only link, once);
`G1 → G2` at the first `unlinkat` of the rule by IGR, CL-G, CQ-3 or CL-3; `G2 → G3`
at the first PK/2 *not authorized* observed after that unlink in this activation
(CQ-5, CL-4 or attestation); `G1 → G4` if `unlinkat` fails (GU). `G1`/`G2`/`G4 → G0`
at the next kernel boot. **Cross-machine invariant:** the capture unit's state does
not pass from **A** to **R** (the `ExecStart=` `execve`) unless the grant state is
**G3** for this activation (CQ-3 and CQ-5 order).

**CL deltas** (in [D §4.2.5-R2 (h)] and [D §4.2.5-R3 (e)]):

| Step | Change |
|---|---|
| **CL-G Δ2** | **new first act**: GRR with the identity of `grant.id` (§5.7), before the lock attempts, the attempt directory and the journal. `identity-unavailable` falls back to CL-3 as accepted |
| CL-0 **Δ** | the lock is K, acquired by non-blocking attempts until the `lock_wait_ms` deadline. On expiry or `K` unopenable, **degraded mode** records `lock_mode` and continues. **`lock-timeout` is withdrawn** |
| CL-3 **Δ** | an ACT-journal `igr` line with outcome `removed`, or a `cl-g {removed}` result for the rule's identity, is class `removed-earlier`; a rule absent with neither is `absent-before-removal`. The rule's removal does not require the lock (GR-1) |
| CL-4 **Δ** | PK/2 seek-not-authorized, budget P |
| CL-5b **Δ2** | also removes **`grant.id` and then K**, last among the `/run` objects, through a descriptor re-verification against the journaled identity, only if K holds nothing else. A K without an identity line is **S0** |
| CL-6 **Δ2** | as accepted. Its `baseline` recomputation is the largest local job in CL and is class X (§7.3, row 9). It uses CL-4's PK result and runs `show` under a class-E deadline |
| CL-7 | `st1-verified` additionally requires `lock_mode` to be recorded |
| BS-4 **Δ2** | at most `backstop_max` firings run CL; the next firing disarms the timer, appends a journal line and exits non-zero. BS runs CL in degraded mode if K cannot be acquired. **Each firing is ended by BS-RM** |

### 8.2 Authority windows

| Window | Opens | Closes | What A-2 permits | Grant | Bound, and its class |
|---|---|---|---|---|---|
| **AW-0**, preparation | AP-0 | AP-2 | unprivileged reads; AP-1 | none | none needed |
| **AW-1**, baseline | SG-1 | AK-1's commit | holder only | none | BSP at most 5 re-reads (C); each read a class-E wait. The holder's life is bounded by L (M) |
| **AW-2**, grant window | AM-2's PF-6 | the first unlink of the rule (IGR, CQ-3, CL-G or CL-3) | the operator's single `start`, **only after `hold-start`** and while the holder is `active` | **G1**: `start` only, for `ubuntu` | **W (start window) and the lease L, enforced by PID 1 (M), IL′.** No helper timing is claimed |
| **AW-3**, visibility lag | that unlink | the first PK/2 *not authorized* | nothing new. A start in this window reaches CQ-2 and is refused if a claim exists, or runs CP, which re-verifies | **G2**: polkitd may still authorize | PK/2's scheduled waiting totals at most P + c + g (E, WB-6) at each use. **No claim about Polkit, and none about when the use returns** |
| **AW-4**, consume | the accepted `start` job | CQ-7 | CP only | G1 → G2 → G3 | the unit's start timeout T_s (M). CP's own elapsed time is not claimed |
| **AW-5**, pass | `ExecStart=`'s `execve` | the main process's end | route (iii-a) only under OC-1 … OC-3 [D §4.2.5-R6 (b)] | **none** (G3) | no bound is claimed by this design |
| **AW-6**, cleanup | the holder's end (or IGR) | the terminal `deact` record, or `attest` | CL in every trigger; IGR | G2/G3 | the rungs RL-0 … RL-5, **ordered and not timed**; each process by its class-M terminator (§7.4) |

### 8.3 Recovery ownership

Who must return each state to ST-1, in order. The first owner is the first rung of
RL (§5.3) that acts. §7.9 maps the interruption points of each procedure to these
rows.

| State | What is undone | First owner | Then | Last |
|---|---|---|---|---|
| ST-1.a0 (K, journal, backstop armed) | K, tree directories, backstop | IGR (nothing to remove) → stop-post CL | backstop | boot, `attest` |
| ST-1.a1 (tree **P**, `grant.id`) | `pass-a.json`, tree **P**, `grant.id`, K | stop-post CL | backstop | boot, `attest` |
| ST-1.a2, ST-2 (rule live) | the rule first, then the rest | **IGR** | stop-post CL (CL-G); backstop; CP at any start | boot |
| **ST-1.i** (holder gone, rule live, inert) | the rule | stop-post CL (CL-G) | backstop; CP at any start (CQ-3) | boot |
| ST-2.c, ST-2.f | the rule if CP did not | CP (CQ-3) | CL (HL's reason, rule first) | boot |
| ST-3 | `pass-a.json`, records (**no** grant) | CL after HL observes the pass end | backstop | boot |
| ST-1.d1, ST-1.ur, ST-1.bc, ST-1+R | as accepted | as accepted | as accepted | as accepted |

**ST-1.i** is the only new state: activation objects present, holder not `active`
or `hold-end` journaled, rule live. It is **inert** (IL, §5.4), entered by a
holder's end before the rule's removal completes, and left by IGR, CL-G, CQ-3 or
the boot.

### 8.4 The states table, deltas

| State | Activation objects present | Grant | Entered by | Left by |
|---|---|---|---|---|
| ST-1.a0 **Δ** | holder `active`, backstop armed, **K**, `ACT` journal; no activation file | none | AK-1 | AM-1, or the holder's end |
| ST-1.a1 … ST-3 | as accepted, with **K** (and `grant.id` from AM-1G) present throughout | as accepted | as accepted | as accepted |
| **ST-1.i** | as ST-1.a2 or ST-2, holder not `active` | G1 **inert** | the holder's end | the rungs of §8.3 |

### 8.5 Evidence records and journals

`rp11-activation-record/2` was never implemented, so its additive amendment below
needs no new schema number.

| Key | Content (amended) |
|---|---|
| `lock` | `{object: {path, dev, ino} or "absent", mode: "held"\|"degraded"\|"absent", wait_ms}` (§4.9) |
| `grant_identity` | `{source: "grant.id"\|"journal"\|"memory", conflict: bool}` (GI-1) |
| `pk` | `{procedure: "pk-root/2", mode, op_ms, call_ms, reap_grace_ms, calls, abandoned, signals, elapsed_ms, outcome, reason}`, replacing `grant_check.bound_ms`. `signals` counts `{sent, esrch, failed, not_sent}` (**Δ3**). `elapsed_ms` is **observed**, never a claim |
| `children` **Δ3** **Δ4** | an array of `{role, argv0, pid, pgid, start_ticks, deadline_ms, s0_ran: bool, grace_deadline_ms: integer\|null, outcome: "exited"\|"expired"\|"interrupted"\|"spawn-failed"\|"reap-error", sends: [{signal, result, offset_ms, late}], waits_skipped, reaped, abandoned, reap_unknown, send_suppressed, last_signal, effect: "none"\|"unknown", anomalies}`, at most 64 entries and an `overflow` count (§7.5a.9). **Δ7:** `grace_deadline_ms` is always present, an integer iff `s0_ran` is true and `null` otherwise, and `outcome` is `reap-error` only when `s0_ran` is false (GD-2, §7.5a.6e). One entry per child, written once, after the child is settled; a child that was not settled when its helper ended has **no entry** (states CS-1 … CS-6; **Δ5:** CS-5 included, so a kernel reap that no durable line records is no reap fact, IS-9; **Δ6:** CS-9 included, so a raised attempt that no durable line records leaves no fact either, IS-10). PIDs are evidence only; elapsed values, `late` and `waits_skipped` are observations |
| `release` | `{first_rung: "igr"\|"cl-g"\|"stop-post"\|"backstop"\|"cp"\|"boot"\|"absent", igr: outcome or "absent"}` |
| `capture` | `{active_state, invocation_id, inactive_enter_us, m_a_us, bsp_retries}` at AM-0; `{…, inactive_enter_us}` at `hold-start` and at CQ-4 |
| `helper` | `{role, image_sha256: [one digest per root-procedure image the Route 3 outcome installs], tool_sha256}` |
| `params` | the §7.6 values and `T_s` as recorded in the H-1 `baseline`, with `sizing: "necessary-conditions-met"` (never "bounded") |
| failure classes **Δ2** | add `lock-object`, `capture-baseline-unstable`, `grant-not-seen`, `stop-control-unconfirmed`, `act-unconfirmed`, `invalid-journal`; **withdraw** `lock-timeout`. `identity-conflict`, `child-abandoned`, `signal-send-failed`, `signal-not-sent` and, in **Δ4**, `children-unknown {helper_role, missing_terminal_line}` are **recorded conditions, not failures** (**Δ3**; a failure of the *enclosing operation* is classed as before) |

The `ACT` journal's closed `op` set gains `igr` and the CL attempt journal's gains
`cl-g`. The consume journal's and each CL journal's `run-start` carry `lock` and
`helper`. Journals, digests and the OH-D-9 return path are unchanged.

### 8.6 Invariants

| ID | Invariant | Where it is checked |
|---|---|---|
| INV-1 | `ExecStart=` runs only after CP exits `0`, which needs CQ-3's journaled removal and CQ-5's *not authorized* within P | NT-PK-2, NT-RL-7 |
| INV-2 | contract OSA over 𝒜 without exception; CX-4 void (§6.8) | NT-SD-3, -9 |
| INV-3 | the rule is linked once, by AM-2, after a BSP baseline and after `grant.id` | AM-0 and AM-2 order tests |
| INV-4 | no safety property cites the lock **or any elapsed time** | the §2.1 table; NT-LD-6; NT-DL-4 |
| INV-5 | no lock of the activation chain is on an object a non-root actor can open | NT-LD-4, -5 |
| INV-6 | no process is designed to end holding a lock; every lock has an explicit close point | NT-LD-3, -8 |
| INV-7 | grant removal by IGR and CL-G waits for no lock, no spawn, no `ext4` write and no Polkit, and **precedes every one of them** (GR-2) | NT-LD-6, NT-RL-1 |
| INV-8 | every wait, poll and retry has a deadline of class E, M or C and a defined consequence. Class-X work is stated as unbounded | NT-PK-5, NT-DL-3, NT-RL-4 |
| INV-9 | a PK `unconfirmed` is never evidence of absence | NT-PK-3, -6 |
| INV-10 | SD compares only with the journaled baseline, and BSP held | NT-SD-1, -2, -10 |
| INV-11 | **conditional on Route 3:** the helper-start contract RH-1 … RH-3 holds for every root procedure | the tests that the chosen Route 3 outcome defines (§9.2). Not testable until that outcome exists |
| INV-12 **Δ3** | every child of a root helper is created by `spawn()` with the closed map and `close_fds`, **and signalled only by SN** | NT-LD-3, NT-HS-1 … 3, NT-SN-10 |
| INV-13 | `removed-verified` needs a journaled removal (CQ-3, CL-3 or IGR) or a `cl-g` result, `ENOENT` and a *not authorized* from the procedure that returned *authorized* in this activation | NT-PK-6 |
| INV-14 | records state `lock`, `grant_identity`, `pk`, `release`, `capture` and `helper` | schema tests |
| INV-15 | any drift of a bound version or digest is INVALID RUN before any lock object or grant exists | AP-0 tests, §9.12 |
| INV-16 | **every elapsed-time statement names its class and its enforcer.** A sum of class-X operations is never stated as a bound, and a sizing rule is never recorded as one. **Δ3** A signal send is class X with a count bound, and no time is stated for it. **Δ4** The same holds for a validation and a reap attempt, and the wait budget counts scheduled sleeps only (WB-6): no statement says that a sequence returns within g | NT-DL-4, NT-DL-5, NT-SN-17, NT-WB-12 |
| INV-17 | the handlers are installed before any state operation and only set a flag; IGR runs from one site, once, and cannot be re-entered. **Δ3** No handler sends a signal and IGR sends none | NT-SG-1, -2, NT-RL-9, NT-SN-11 |
| INV-18 **Δ4** | every procedure's interruption at any point maps to a state and a first owner (§7.9), **and every point of IM-S (T3k, T5k, T3x and T5x included), for every send outcome and every phase RA-0 … RA-4 and RA-E of a reap attempt, maps to a child state of the set CS-1 … CS-10 and an owner by enclosing procedure** **Δ5** | NT-DL-10, -11, NT-RL-10, NT-IS-1, -16, NT-NS-8 |
| INV-19 **Δ3** | every signal a root helper sends goes through SN, to a validated, unreaped child group of its own, from the closed set `SIGTERM`/`SIGKILL`, one attempt per signal, never from a handler, IGR, GRR or CL-G. **Δ7:** the *unreaped* premise rests on the sole-reaper invariant (SI-3); validation is a detector only and no reuse claim rests on it (SI-5) | NT-SN-6, -10, -11, -12 |
| INV-20 **Δ3** **Δ4** | no send result (`sent`, `esrch`, an error, `not-sent`, or the loss of a result with the helper) is evidence of exit, reaping, absence, authorization, non-authorization, creation, removal or arming; the enclosing operation's fail-closed result is unchanged by it. **Only a recorded reap status proves that the direct child was reaped, and it never proves that the process group is empty. Δ5: a kernel reap that no durable `child` line records is evidence of nothing to a later procedure (IS-9). Δ6: a `reap-error` is evidence of neither reaping nor its absence (RE-2, IS-10)** | NT-SN-1, -3, -4, -13, NT-IS-2 … 4, -7, -8, -16, -17 |
| INV-21 **Δ3** **Δ4** | an abandoned child, and (**Δ6**) a `reap-unknown` child, is never signalled again and never presumed gone; every abandon and every non-`sent` result is recorded, or its loss is a recorded gap (`children-unknown`); a mutating child's effect after `error`, `interrupted`, an abandon or the end of its helper is *unknown* | NT-SN-8, -9, -14, NT-IS-9, -13, -14 |
| INV-22 **Δ4** **Δ7** | each child has **at most one** grace deadline: **exactly one if S0 ran, read once before its first validation or send, and none otherwise** (GD-1); every sleep is capped by the time remaining to its own deadline; **no timed wait begins at or after `t_g`**; the scheduled sleeping for a child's reaping totals at most g; the escalation of S4 is not a wait, is made at most once, and may be `late`; no class-X operation acquires a time bound from the budget | NT-WB-1 … 12, NT-GD-1 … 4 |
| INV-23 **Δ4** | after an interruption a child is in exactly one state of CS-1 … CS-10, **never derived from a send result**, and its owner is that of the enclosing procedure (table SN-RO); **Δ5:** inside a reap attempt the state follows the kernel's truth about the direct child by phase (RB-4), which no later procedure can observe without a durable line (IS-9); the interactive `attest` has **no automatic owner**; the boot is a separate recovery event and never evidence of a send; the ended helper makes no further send, and no one hunts the child | NT-IS-1 … 17 |
| INV-24 **Δ6** | **no signal of any kind is sent to a child after any `reap-error` on it**: the handle is `reap-unknown`, S4's `SIGKILL` included; no retry, no alternate primitive, no further poll and no process search; the state never changes; the enclosing result is the fail-closed one; no new wait or grace starts; the rule holds for either truth about the direct child, so it needs no answer to PO-SN (c′) | NT-RE-1 … 12 |
| INV-25 **Δ6** | **no `not-sent` result is followed by a send**: `not-sent(reaped)`, `not-sent(abandoned)` and `not-sent(reap-unknown)` end at S7 with no call and no wait; `not-sent(identity-mismatch)` and `not-sent(identity-unverifiable)` go to S5; T0 and T1 exist only for a `running` handle; every dash of the matrix is unreachable | NT-NS-1 … 8, NT-IS-1, -5, -6 |
| INV-26 **Δ7** | **`t_g` exists exactly when S0 ran**: `children[].grace_deadline_ms` is an integer iff `s0_ran` and `null` otherwise, never omitted; a pre-S0 `reap-error`, a child that exits within c, a failed spawn and a settled handle read **no** `t_g`, read no clock for the record and start no grace period; S0 is entered only for a `running` handle; `sends != []`, `waits_skipped`, `abandoned` and `late` each imply `s0_ran` | NT-GD-1 … 4, NT-RE-7, -11, NT-SN-9 |
| INV-27 **Δ7** | **the reuse defence is the sole-reaper invariant, not validation**: no path reaps outside `reap_step()`; SN-4 is a detector only; **once the invariant is violated the design makes no reuse-safety claim from SN-4 alone**; no document, record or test says that validation detects a foreign reap or a coincidental reuse; no mandatory `start_ticks`, pidfd or other identity mechanism is claimed | NT-SN-12, NT-SN-6 (b), NT-GD-4 text scan |

### 8.7 Where the tests land

The accepted successor table numbers OH-S4's tests up to (29). This proposal adds,
without renumbering any accepted test: **(30)** NT-LD-1 … 10; **(31)** NT-RL-1 … 13;
**(32)** NT-SD-1 … 10; **(33)** NT-PK-1 … 8, NT-DL-1 … 11 and NT-SG-1 … 4;
**(34)** NT-HS-1 … 3, plus the NT-RH tests that the chosen Route 3 outcome defines;
**(35)** the PO-17 matcher over every launcher image the chosen outcome includes and
the recorded HF-14 entry; **(36) Δ3** NT-SN-1 … 18, the signal-sending contract; **(37) Δ4** NT-WB-1 … 12 (NT-WB-5 as 5a and 5b, **Δ5**), the wait budget on a fake clock; **(38) Δ4 Δ5** NT-IS-1 … 17, the interruption map and the reap-attempt boundary; **(39) Δ6** NT-RE-1 … 12, the reap error before and after a kernel reap, at S3, S5 and the final attempt, and the evidence-only status of PO-SN (c′); **(40) Δ6** NT-NS-1 … 8, the two branches of S1 and the cell and dash audit; **(41) Δ7** NT-GD-1 … 4, the grace deadline that exists exactly when S0 ran (NT-SN-12 is rewritten in group (36), NT-RE-7 in group (39)). OH-S8b's drills gain only what a real host can safely show:
route (iii-a) is unchanged; `SIGTERM` of a test holder showing IGR before exit;
`SIGKILL` of a test holder showing the live-inert state and its removal by the
stop-post; a test unit with `TasksMax` too small is **not** proposed, because PID 1
spawn failure is a model-only case (NT-RL-2, NT-RL-3).

### 8.8 What stays exactly as accepted

The unit and rule bytes (apart from the `ExecStartPre=` program, which the Route 3
outcome fixes, and the backstop literal's BS-RM change); SB-1, SB-2 and SB-3; CQ-0,
CQ-2, CQ-3, CQ-6; the claim's publication, blocking and durability points; the
grant-priority form of CQ-3; GP-R3's principle and ST-1.ur; route (iii-a) and OC-1
… OC-3; OS-1, OS-4, OS-5's decision rule, OS-7, OS-8; `hold-start`'s durability;
A-2's pins other than the additions of Appendix A; M-B and M-S; the AC-1 … AC-9,
AC-12 rows; the attribution classes, PF, PT, G-R1, RS-1 and RB-1; ST-1+R; DF-1,
SL-1, GU; HF-facts other than the rows named in Appendix A.

---

## 9. Route 3: the accepted boundary, why a concrete design is not established, and the exact alternatives

### 9.1 The accepted Route 3 boundary, and what R1 did to it

**The accepted definition.** DR1 §5.3 compared three routes. Route 3 is *"abandon
the Python-dependent route"*: *"the entry bootstrap, capture mechanism, CP, holder,
backstop and CL must be re-implemented without Python, or RP-11's one-host design is
withdrawn."* It adds that its security "depends on the replacement. Likely a larger
trusted computing base, written new", that it is "a long redesign", and that review
is "a new design cycle". [R3 §6.3] (accepted) records that **Peter decided Route 1
(D-3)** and that *"Route 3 remains the destination only if OH-S2 refutes PO-12 or
PO-19 for 3.14."* The accepted OH-S2 R2 record refutes PO-12 and AS-8 [R2 §10.4], and
the acceptance states: *"Route 1 returns to Route 3 design review because PO-12 and
AS-8 are refuted."*

**The working restatement.** The R2 assignment states the boundary this proposal
must restore: *the root procedures that touch the grant and activation mechanism do
not run through CPython or a dynamic loader.* No prior record changes it. A search of
the named accepted documents found no §0.2 change, and the decision register and
change log are not edited here.

**Two readings, not decided here.**

| | **R3-ROOT** (the R2 assignment's restatement; this proposal's working boundary) | **R3-DR1** (the verbatim wording of DR1 §5.3) |
|---|---|---|
| Procedures that must be Python-free | the root procedures that touch the grant and the activation mechanism: CP, the holder (ACT, HL, IGR), the stop-post, the backstop, `attest`. Whether the installer class (H-1, RB-1, RS-1) is among them is **BQ-3** | the entry bootstrap, the capture mechanism, CP, the holder, the backstop and CL |
| Dynamic loader | absent from those procedures **including every child they start** (LR-2) | implied: the Python-dependent route is abandoned |
| The entry (run as `ubuntu`, `python3.14` under the C11 launcher) | **stays Python**. PO-12′ and PO-19 still bind it | Python-free as well |
| Source | the R2 assignment, finding R2-F1 | DR1 §5.3, accepted through R3 §6.3 |

This proposal applies R3-ROOT because the authorizing assignment states it. It
**neither narrows nor widens** the accepted boundary. If a maintainer treats R3-ROOT
as a *narrowing* of DR1 §5.3, adopting it is a scope question for §0.2, and I record
it as **BC-2** (§12.2). Everything in §9 is written so that it stays true under either
reading, and §9.8 and §10 give both.

**What R1 did.** R1's scoping note (R1 §9.1) read "Route 3 design" as *"the
replacement of Route 1 … defined by the elimination of the ambient inputs … and not
by the removal of Python"*. It treated DR1's literal Route 3 as an alternative
(RT3-C) and rejected it as "not decision-ready", it recommended RT3-A, and it asked
Peter to confirm the re-scoping in DEC-1. **That is a scope change presented as a
design choice.** A static first image closes inherited environment and descriptors.
It does not remove the interpreter, the dynamic loader or their file-based inputs
from the root path. R1's recommended RT3-A therefore did **not** meet the authorized
Route 3 boundary. R1 stays unchanged and unaccepted. In this record RT3-A is renamed
**`STATIC-SCRUB-WRAPPER` (SSW)** and described in §9.7 as a scope-change alternative.

### 9.2 What any outcome must deliver: the helper-start contract RH and the literal criteria LR

**RH-1 … RH-3** describe what a root procedure's *first image* must establish. They
are the part of R1's Route 3 that is **independent of the Python question** and that
the activation design (§§4 … 8) relies on.

* **RH-1, environment.** No environment string reaches any image of a root procedure
  except reviewed literals (and, where the accepted design reads it, the 32-hex
  `INVOCATION_ID` selection of [D2 §5.6]).
* **RH-2, descriptors.** Descriptors 0, 1 and 2 are checked, and every descriptor ≥ 3
  is closed before the procedure's first state operation.
* **RH-3, process state.** Signal dispositions are reset and the mask cleared, `umask`
  and the working directory are fixed, where the unit configuration does not already
  fix them. Limits, `no_new_privs`, capabilities, seccomp, cgroup, scheduling and
  timers are **not touched and not claimed** (R-10, K-5).

**Status today.** RH-1 is **not met** for the root roles: [R2 §10.4, §15.4 (X-1)]
refuted the premise that `python -I -S` under PID 1's open block starts cleanly. RH-2
is not established for them either. The accepted dispositions are unchanged: PO-12
and AS-8 are refuted, and Route 1 returns to Route 3 design review.

**LR-1 … LR-6, the literal criteria.** A concrete Route 3 under R3-ROOT is one in
which, for every root procedure *p* of §9.1:

* **LR-1.** No CPython runs in *p*'s process tree.
* **LR-2.** No dynamic loader runs in *p*'s process tree. Every image *p* executes,
  including every child, is statically linked, or *p* performs that function itself.
* **LR-3.** RH-1 … RH-3 hold for each image of *p*.
* **LR-4.** Every function that *p* delegates to a child today (§9.3, DI-1 … DI-6) is
  performed in-process, or by an interface that is itself loader-free and cited.
* **LR-5.** The behaviour of the accepted procedures (CQ-0 … CQ-7, CL, IGR, GRR, PK/2,
  BS, SD, LD) is preserved, each by a stated mapping from the old step to the new one.
* **LR-6.** Each image passes the D9 chain and PO-17 (§9.10).

LR-1 and LR-2 are the criteria RT3-A fails. They are why it cannot be Route 3.

### 9.3 Evidence assessment: why no concrete Route 3 is established

**What the root procedures delegate today.**

| # | Function | Today's mechanism | Used by |
|---|---|---|---|
| DI-1 | unit state reads (`ActiveState`, `InvocationID`, `InactiveEnterTimestampMonotonic`, `Job`, `LoadState`, `Result`, `TimeoutStartUSec`, `DropInPaths`, …) | `systemctl show -p …` through `spawn()` | holder (BSP, HL, `hold-start`), CP (CQ-4), CL (CL-2, CL-6), BS-1 |
| DI-2 | creating the transient holder unit | `sudo -n /usr/bin/systemd-run` by the executor | AP-2 |
| DI-3 | creating the backstop service and timer | `/usr/bin/systemd-run` by the holder | AK-1 |
| DI-4 | disarming the backstop timer | `systemctl stop ⟨id⟩-backstop.timer` | BS-2, BS-3 |
| DI-5 | the Polkit decision | `/usr/bin/pkcheck` | AV-1, CQ-5, CL-4, GP-R3, attestation |
| DI-6 | the authorization subject | `/usr/bin/sleep 60` under `ubuntu`'s credentials | PK/2 |

`/usr/bin/systemctl` is recorded as dynamic [D §4.1.3, TR-4]. The linkage of
`systemd-run`, `pkcheck` and `sleep` is recorded by **no accepted record** (it is the
optional fact MF-9). Distribution binaries of those packages are expected to be
dynamic, and that expectation is not a fact.

**What a literal Route 3 needs, and what the repository holds.**

| # | Need | Repository evidence | Gap |
|---|---|---|---|
| E-1 | the **definition** of every root procedure | present: the accepted design through D3-R6 and this record define CP, the holder, CL, IGR, GRR, BS, PK/2, SD and LD completely | none for *what* is to be re-implemented |
| E-2 | a **loader-free interface** for DI-1 … DI-5, with version-bound citation | the accepted R2 record cites **server-side** behaviour: `StartTransientUnit` refusal semantics ([R2 §8 (m)]), the `StartUnit` and Polkit-check flow ([§8 (p), (q)]), property vtables and `GetAll` ([§4]), `CheckAuthorization` detail restrictions ([§6.3]), and `pkcheck`'s exit statuses ([§6.4 (e)], a command-line contract). **No accepted record cites a client-side contract**: the bus address and authentication, message marshalling, the argument structures of `StartTransientUnit` (including the `ExecStopPost=` and timer properties), the Polkit subject structure, error mapping, or how a static image obtains decisions equal to `pkcheck`'s. A fixed-string count of SASL, marshalling, wire format, wire protocol, the private systemd socket and the system-bus socket over the R2 record, the one-host design, D2 and the R3 proposal returned a single hit: TR-4's mention of the system-bus socket path | **Gap 1**: interface contract and its citation |
| E-3 | a **proof method** for a static image with a larger system-call inventory | D2 and D9 proved the closed nine-call launcher. [R2 §12] **refuted AD-8 as a general statement** and established it **only for that closed inventory** (a system call can return `EINTR` with no handler). A root image needs sockets, directory and file operations, `flock`, `fsync`, `renameat2`, `linkat`, `unlinkat`, a clock and, for DI-6, process creation. None of their blocking or `EINTR` behaviours is cited. **Δ3** The inventory also needs, for every child a root image controls, `setsid`, signal sending and waiting (SN, §7.5a), which no accepted record cites either | **Gap 2**: restated proof method and citations |
| E-4 | a **boundary** for procedures that `sudo` starts (`attest`, AP-2's `sudo systemd-run`, and the installer class) | `sudo` and `systemd-run` are dynamic root processes that run before any image the procedure controls. The accepted text treats `sudo`'s environment as an OH-D-6 consistency limit (HB-1). That is a boundary statement, not evidence | **Gap 3**: BQ-2 and BQ-3 |
| E-5 | **size and effort** | none. R1 states that "the repository holds no measure of their size", and DR1 says "a long redesign" and "a new design cycle" | **Gap 4**: an estimate |
| E-6 | which **reading** binds | R3-ROOT or R3-DR1 (§9.1) | **Gap 5**: BQ-1 |
| E-7 | a prior **§0.2 decision** that changes the boundary | none found in the named accepted documents | confirms that **no scope change exists** |

**Conclusion.** A concrete Route 3 is **not established**. That is not a finding that
it is impossible. Defining it needs an interface contract, a proof method and a
boundary the repository does not hold, and the assignment forbids inventing them. The
terminal state is therefore **`HARD STOP: concrete Route 3 not established`**.

**Four boundary questions** that the work of §9.5 must settle first. None is decided
here, and none is a design choice.

* **BQ-1.** Does R3-ROOT or R3-DR1 bind (is the `ubuntu`-run entry in scope)?
* **BQ-2.** For a procedure that `sudo` starts, where does "the root procedure" begin:
  at the first image the procedure controls, or at `sudo`? Treating `sudo`'s own loader
  as outside the procedure is an exception to LR-2 and needs to be stated as one.
* **BQ-3.** Is the installer class (H-1, RB-1, RS-1: the `sudo -n python3.14 -I -S -c`
  verified-exec stub, HB-1) among the "root procedures that touch the … activation
  mechanism"? They install and remove the files the mechanism consists of.
* **BQ-4.** Are dynamic *children* of a static root image excluded by LR-2, or
  excepted? An exception is **SCDC** (§9.4), which is a scope change.

### 9.4 The exact bounded alternatives

| ID | What it is | Meets the accepted Route 3? | Decision-ready? | Baseline decision needed before it could be selected |
|---|---|---|---|---|
| **LIT-FULL** | the root procedures re-implemented as static images that perform DI-1 … DI-6 in-process or by a cited loader-free interface; no dynamic child; the entry stays Python (R3-ROOT) | **yes** (LR-1 … LR-6) | **no**: needs WP-1 … WP-7 | none beyond Peter's choice after readiness. If BQ-2, BQ-3 or BQ-4 are answered by an *exception*, that exception is a §0.2 change |
| **LIT-DR1** | LIT-FULL **plus** a Python-free entry bootstrap and capture mechanism (R3-DR1) | **yes**, under the wider reading | **no**: needs WP-1 … WP-8 | none; the largest |
| **WITHDRAW** | RP-11's one-host design (or its activation part) is withdrawn, the second limb of DR1 §5.3 | **yes**: it is in the accepted definition | n/a | Peter's decision. Its effect on the Phase 5 RP-11 plan is outside this record and may itself need §0.2 |
| **SSW**, `STATIC-SCRUB-WRAPPER` (R1's RT3-A) | a static environment-ignoring first image in front of `python3.14 -I -S` for CP, the holder, the stop-post, the backstop and `attest` | **no. A scope-change alternative.** It leaves CPython, the dynamic loader and their file inputs in the root path (fails LR-1, LR-2, LR-4) | **yes, as an alternative** (§9.7) | **§0.2**: amend the accepted Route 3 boundary to "closed environment and descriptors; CPython and glibc remain; file inputs bound by MF-1, MF-2, MF-4 and the drift gates" |
| **SCDC**, `STATIC-CORE-DYNAMIC-CHILDREN` (R1's RT3-B) | the helper logic as freestanding C, with `systemctl`, `systemd-run`, `pkcheck` and `sleep` still dynamic children | **no**: the dynamic loader stays in the root path through its children (fails LR-2, LR-4) | **no**: needs WP-2, WP-4, WP-5, WP-6, MF-9 | **§0.2**: except the dynamic children from the boundary |
| **ACCEPT-X1** (R1's RT3-Z) | no new image: accept X-1 as an explicit root-ambient residual and bind PO-12′ and PO-19 for the entry only | **no**: PO-12 stays refuted for the root roles, and the accepted disposition "Route 1 returns to Route 3 design review" is left unanswered for them | **yes** (no code) | **§0.2**, and Peter's explicit residual acceptance under OH-D-6 and R-10. *Nuance:* [R2 §15.4] frames X-1 as "a design decision, not a citation: whether the activation design accepts this under OH-D-6/R-10 or needs these processes to start from a literal environment". Whether accepting it is a design decision within existing authority or a change of the Route 3 boundary is **not decided here**. Until a maintainer rules otherwise this record treats it as a change |

Rejected, for the reasons R1 gave and that stand: **unit-level scrubbing** (`UnsetEnvironment=`
removes only named variables from the assembled block [R2 §3.1 P14-3]; the set of
harmful names is open-ended; the reviewed unit admits none of these lines, T-B1);
a **dynamic wrapper** (`env -i`, a shell), whose own loader reads `LD_*` and the
tunables before any user code [R2 §11.3]; a **private pinned interpreter**, for which
the repository holds no source, recipe or provenance and which would need network
research and a new trust root.

**None of SSW, SCDC and ACCEPT-X1 is described anywhere in this record as satisfying
literal Route 3.** This record makes no recommendation among the six. It states one
observation, for the reviewer and not as a recommendation: of the alternatives that
do not meet the accepted boundary, SSW introduces the least new code, and of the
alternatives that do, WITHDRAW introduces none. Neither fact selects anything.

### 9.5 The work that would make literal Route 3 decision-ready

Each package is **repository-only unless stated**, needs its own prompt, authority,
work ID and Codex review, and is **not requested or authorized here**. The order is a
dependency order.

| WP | Work | Output | Needs |
|---|---|---|---|
| **WP-1** | settle BQ-1 … BQ-4 | a boundary record stating which procedures are in scope, where each begins, and whether any exception is requested. An exception is a **BC** (§12.2) | Peter, with Codex review. Documentation |
| **WP-2** | inventory every operation of every in-scope procedure at system-call intent, from the accepted procedures and this record | an operation table (the §7.3 inventory, **including the sends and validation of rows 3a … 3f (Δ3)**, extended to every call) | derived from accepted text. Documentation |
| **WP-3** | the loader-free interface contract for DI-1 … DI-5 (and DI-6): what a static image sends and receives, and which accepted semantics each rests on | proposed obligations with version-bound citations for `systemd 259.5-0ubuntu3.4` and `polkit 127-2ubuntu1.1` | a **citation slice** of the OH-S2 class (U-10). It must name its authorized sources. **No network research is authorized** by anything here |
| **WP-4** | the static-image design: language class, system-call inventory, blocking and `EINTR` analysis (AD-8 restated over the larger inventory, **including the signal-send and wait calls and the SN/SI contract of §7.5a, Δ3, and the wait budget WB-1 … WB-7 and the child-state set CS-1 … CS-10, Δ4 Δ6, and the reap-error rules RE-1 … RE-6, Δ6**), memory and stack bounds, parsing, a SHA-256 and canonical-JSON implementation with test vectors | a D2-class design for each image | after WP-2 and WP-3. Documentation |
| **WP-5** | the proof method and evidence plan: D9-1 … D9-4 extended, independent decoding (XD) for larger images, reproducible-build reuse, PO-17 per image | a plan, not the evidence | after WP-4 |
| **WP-6** | the equivalence mapping: each accepted step to its new step, each accepted negative test to its image-level counterpart, and every behaviour that cannot be preserved, restated | a mapping table | after WP-4 |
| **WP-7** | a size and review-cost estimate | a recorded estimate, so that Peter's choice is informed | after WP-4 |
| **WP-8** | only for R3-DR1: the Python-free entry bootstrap and capture mechanism | a design of the same kind | after WP-1 settles BQ-1. The largest item |
| **WP-9** | the decision record | Peter's choice among LIT-FULL, LIT-DR1, WITHDRAW and, **only after a §0.2 change**, any scope-change alternative | after WP-1 … WP-7 (or WP-8) and Codex review |

Without WP-3 and WP-4 no static image can be specified without inventing the protocol
it speaks and the system calls it needs. That is the content of the hard stop.

---

### 9.6 The corrected executable and runtime boundary, and the Role A–H inventory

#### 9.6.1 Boundary, role by role

"Accepted today" is the accepted text, which **names `/usr/bin/python3.12`**, a
literal that the accepted R3 record already marks for replacement. Route 1's
replacement by `/usr/bin/python3.14` is refuted for the root roles (X-1) and so is
**not** a boundary. The LIT-FULL column is the *requirement* of §9.2, not a design:
what the static images are, and how they perform DI-1 … DI-6, is exactly what is not
established. The SSW column is the scope-change alternative of §9.7.

| Role | Started by | Accepted today (refuted for root roles) | **LIT-FULL** (R3-ROOT; requirement only) | **SSW** (scope change; §9.7) |
|---|---|---|---|---|
| **entry** | PID 1, capture unit `ExecStart=` | `rp11-launch` (static, `ubuntu`, NNP), then `python3.12 -I -S …/rp11_entry.py`, environment `rp11-entry-env/1` | **unchanged in kind**: `rp11-launch`, then Python as `ubuntu` (R3-ROOT). The literal retarget to the accepted `python3.14` remains. Under LIT-DR1 the entry is Python-free and A1 … A5 are obsolete | `rp11-launch` retargeted by one literal; `python3.14 -I -S`; `rp11-entry-env/1` |
| **consume** (CP) | PID 1, `ExecStartPre=+` | `python3.12 -I -S …/rp11_h1.py consume` under PID 1's open block | a static image performs CQ-0 … CQ-7 and DI-1, DI-5, DI-6 itself; RH-1 … RH-3 | `rp11-rootexec consume`, then `python3.14 -I -S …/rp11_h1.py consume` under `rp11-helper-env/1` |
| **hold** | PID 1, the transient holder | `python3.12 -I -S …/rp11_h1.py hold ⟨id⟩ ⟨a2⟩` | a static image performs the holder, IGR, GRR and DI-1, DI-3, DI-5, DI-6 itself | `rp11-rootexec hold ⟨id⟩ ⟨a2⟩`, then `python3.14` |
| **stop-post** | PID 1, `ExecStopPost=` | `python3.12 -I -S …/rp11_h1.py deact ⟨id⟩ ⟨a2⟩ stop-post` | a static image performs CL and DI-1, DI-5, DI-6 | `rp11-rootexec stop-post …`, then `python3.14` |
| **backstop** | PID 1, the timer's service | `python3.12 -I -S …/rp11_h1.py backstop ⟨id⟩ ⟨a2⟩` | a static image performs BS, CL and DI-1, DI-4, DI-5, DI-6 | `rp11-rootexec backstop …`, then `python3.14` |
| **attest** | the executor, `sudo -n`, interactive | `sudo -n python3.12 -I -S …/rp11_h1.py deact ⟨id⟩ ⟨a2⟩ attest` | **BQ-2**: a static image after `sudo`, with `sudo`'s own loader an explicit, stated exception, **or** another start path | `sudo -n …/rp11-rootexec attest …`, then `python3.14`, `rp11-helper-env/1a` |
| **H-1, RB-1, RS-1** (installer class) | the executor, `sudo -n` | `sudo -n python3.12 -I -S -c ⟨verified-exec stub⟩ …` under `sudo`'s environment | **BQ-3**: in scope (a Python-free installer is then a new WP) or out of scope, stated as an exception with the HB-1 residual | `python3.14 -I -S -c …` under `sudo`'s environment: **HB-1** residual |
| **helper children** (DI-1 … DI-6) | `spawn()` of a root helper | dynamic distribution binaries under the closed map `{LC_ALL=C, PATH=/usr/bin}` | **none** (LR-2): each function is in-process or by a cited loader-free interface (WP-3) | unchanged: dynamic children under the closed map. Their file-level loader inputs are MF-9 |

#### 9.6.2 Inventory of every Role A–H occurrence, and its disposition

Line references are the **current** lines of the cited files, as found by fixed
searches of those named files and compared with R1's (they agree). "Applied by" names
the slice that would apply the row. **None is applied here.** The LIT columns apply
only if Peter later chooses a conforming alternative; the SSW column only after a §0.2
decision.

**Role A, executed literals.**

| # | Location | Text | **LIT-FULL** | **SSW** | Applied by |
|---|---|---|---|---|---|
| A1 | `infra/rp11-launch/launch.c:207`, `:221` | `argv_out[0]` and the `execve` path `/usr/bin/python3.12` | retained: `/usr/bin/python3.14` for the entry, **the only source delta of the entry image** (R3-ROOT). Obsolete under LIT-DR1 | as LIT-FULL | OH-S4p |
| A2 | `rp11-launch.x86_64.listing:412–413` | `.rodata` bytes `/usr/bin/python3` `.12` | regenerated by the rebuild, never hand-edited | as LIT-FULL | OH-S4p |
| A3 | image `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572` and every pin of it (`rp11_launch.py`, `expected.sha256`, `tools/r5_runner/blocks/s08.sh`, design §4.2.4 P-0 and §4.5.2, IA-8) | the compiled literal | a new reviewed digest for the entry, **plus** a digest set for every static root image | the entry's new digest **plus** the four digests of the wrapper image | OH-S4p |
| A4 | `tools/phase_5_0_evidence/rp11_launch.py:47`, `:49` | `EXECVE_PATH`, `EXECVE_ARGV[0]` | `/usr/bin/python3.14`; **plus** a contract per static root image | `/usr/bin/python3.14`; plus a contract for the wrapper's five vectors | OH-S4p |
| A5 | `docs/review/phase-5-0-evidence-harness-review-manifest.json:2732`, `:2744`, `:2824`, `:2841` | `rp11_launch` `execve_argv`, `execve_path`, `execve.argv`, `execve.path` | `/usr/bin/python3.14` in a new manifest version, **plus** a contract per static root image | the same, plus the wrapper contract | OH-S4p |
| A6 | design `:2857` (also `:228`, `:2481`, `:2509`, `:5242`, `:6979`) | `ExecStartPre=+/usr/bin/python3.12 -I -S …/rp11_h1.py consume` | **replaced** by the static CP image's path (fixed by WP-4). No Python literal remains for CP. T-B1 admits exactly that line | `ExecStartPre=+/usr/local/libexec/freedom-blades-rp11/rp11-rootexec consume` | OH-S0d (text), OH-S4 (tests) |
| A7 | design `:1257` | `sudo -n /usr/bin/python3.12 -I -S -c '⟨verified-exec stub⟩' …` | **BQ-3**: `/usr/bin/python3.14` with the HB-1 residual stated, or a Python-free installer | `/usr/bin/python3.14` under HB-1 | OH-S0d, OH-S4 |
| A8 | design `:1996`, `:1997`, `:2016`, `:2147` | the holder's `ExecStopPost=`, the holder command, the backstop command and the attest command | **replaced** by the static images' paths. The backstop literal also gains BS-RM (§7.4) | the wrapper literals of §9.7, with BS-RM | OH-S0d, OH-S4 |
| A9 | design `:3124` | the `ExecStartPre` normalization (`path`, `argv[0]`) | path and `argv` of the static CP image, `+` flag | path `…/rp11-rootexec`, `argv` `[…/rp11-rootexec, "consume"]`, `+` flag | OH-S0d, OH-S4 |
| A10 | C11 `:688`, `:903–904`; D2 `:436`, `:1256`, `:1258`, `:1567–1568` | the entry's `execve` contract | a dated amendment note naming `/usr/bin/python3.14` for the entry; **plus** a dated D2 addendum for every added image | the same, for the wrapper | OH-S0d |

**Role B, trust-path and proof-obligation statements.**

| # | Location | **LIT-FULL** | **SSW** |
|---|---|---|---|
| B1 | design TR-9 `:945` | `/usr/bin/python3.14 -I -S` for the **entry** only. **New rows** for each static root image in place of the Python rows for the root roles | the entry as LIT-FULL; **new row TR-6a′** for the root roles (the wrapper first, then the interpreter) |
| B2 | design PO-19 (a) `:4497` | restated for the **entry's** interpreter and closure | restated, six consumers (§9.8) |
| B3 | C11 PO-12 and AS-8 (`:456`) | **refuted** for CPython 3.14.4 [R2 §10.4]; PO-12′ restated for the entry | as LIT-FULL, with the root roles added |
| B4 | C11 M-5; design M-5 `:5154` | the entry interpreter `/usr/bin/python3.14`; **plus** every installed static root image as a root-owned `0755` regular file pinned by digest | as LIT-FULL, for the wrapper |
| B5 | C11 descriptive text (`:62`, `:281`, `:514`, `:576`, `:598`, `:619`, `:809`, `:941`, `:1748`) | a dated C11 amendment note for the entry. The withdrawn LB-2 and LB-3 rows and change records (`:226`, `:798`, `:1019`, `:2529`, `:2533`) stay as history, unchanged | the same note, **plus** that the root roles start through the wrapper |
| B6 | U-9 decision | **unchanged**. Its consumers narrow by the obligation text, which is itself a scope matter only if BQ-1 reads R3-ROOT as a narrowing (BC-2) | unchanged; the narrowing is **not** achieved by DEC-1 |

**Role C, H-0 facts and command classes.**

| # | Location | **LIT-FULL / SSW** |
|---|---|---|
| C1 | HF-06, HF-07, HF-08, HF-10 (`:4436–4440`), C-VER (`:4472`) | **unchanged by Route 3**: the `python3.14` rows are already observed by H-0G in the accepted composed H-0. The design text (`:4438`, `:4440`, `:4472`) still names `python3.12`. That text is replaced by OH-S0d, and no observation changes |
| C2 | HF-10, HF-11 | **add rows** for each installed static image (absent at H-0; present at P-0 and H-2) and for `/run/freedom-blades-rp11-lock-*` (absent) |

**Role D, standard-library capability claims.**

| # | Location | **LIT-FULL** | **SSW** |
|---|---|---|---|
| D1 | PT-8: `renameat2` through `ctypes` | **unchanged for the entry-side Python**. In a static root image `renameat2` is a direct system call, which [R2 §7 (c)] establishes at the kernel and glibc level. `os.renameat2` does not exist in 3.14.4 [R2 §10.5] | unchanged: `ctypes`, whose `_ctypes` closure (`libffi`) is an MF-1 consumer |
| D2 | the bootstrap, the capture mechanism and `rp11_h1.py` under TR-9's interpreter | **`rp11_h1.py` is replaced** by static images (WP-4). The entry-side bootstrap tests run under 3.14 as well as the suite interpreter, or the gap is stated | unchanged: OH-S4 tests run under 3.14 as well as the suite interpreter, or the gap is stated |

**Role E, verification artifacts.** `tests/test_rp11_launch_source.py` and
`infra/rp11-launch/verify/ctverify.py` read their constants from the manifest
contract. They need **no literal edit** and need **extension** for every added image
(OH-S4p). D2's test methods (`:1525`, `:2207`) and the I-7 handback's decoded `execve`
record are evidence for the **old** image. They remain history and are superseded by
re-run evidence for each new image.

**Role F, development and test runtimes** (`venv-web` CPython 3.12.14, the
controller's 3.12.3 records, the production deployment Python, the harness and
laboratory fixtures): **unaffected under every alternative.** They are not the trusted
path.

**Role G, current-state records.** `docs/implementation-plan.md` §20,
`docs/project-management/status.md`, `docs/review/Handover information` and the
test-server banner: **pointers only**. This assignment updates them, and only them.

**Role H, historical or consumed evidence:** the R3 … R5 prompts, authorities,
handbacks and reviews, the design's revision history, the preparation handback, the
2026-09-29 C11 review, the R1 proposal and handback, and the `*-through-*` snapshots:
**never edited.**

### 9.7 `STATIC-SCRUB-WRAPPER` (SSW): the scope-change alternative, stated exactly

SSW is R1's RT3-A with its recommendation removed and its name changed. It is kept
because it is a coherent, bounded design that a maintainer may wish to weigh **after a
§0.2 decision**. It is **not Route 3**.

**What it is.** A second static image of the class the repository already reviews,
`rp11-rootexec`, installed beside `rp11-launch` in tree **L**. It accepts five roles,
validates their operands byte for byte, writes a literal environment, closes every
descriptor from 3 up, resets signals, sets `umask 0077`, `chdir("/")`, and `execve`s
`/usr/bin/python3.14 -I -S …/rp11_h1.py ⟨subcommand⟩ …`. Every unit-run root helper
names it as the program PID 1 starts. `attest` is run through it under `sudo -n`. The
entry keeps `rp11-launch`, with one literal retargeted. H-1, RB-1 and RS-1 keep the
accepted verified-exec stub (HB-1).

**Contract (carried from R1, condensed).**

* **Class.** The accepted launcher's [D2 §5.1]: freestanding ISO C11, `-ffreestanding
  -nostdinc`, one assembly `_start` entering one C function by one `jmp`, no runtime,
  no writable data segment, no `ret`, no `call`, every exit `exit_group` followed by
  `ud2`. A separate image from the same build.
* **Accepted argv.** `argv[0]` is not examined. `argv[1]` is one of `consume`, `hold`,
  `stop-post`, `backstop`, `attest`. `consume` takes `argc = 2`. The other four take
  `argc = 4`: `argv[2]` exactly **34** bytes matching
  `rp11-act-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}`, `argv[3]` exactly **64** bytes of
  `[0-9a-f]`. Anything else exits `111` before any state operation.
* **Environment.** The four unit roles read only the `INVOCATION_ID` selection
  ([D2 §5.6], exit `112`). `attest` reads none. `rp11-helper-env/1` is the same three
  entries, in the same order and bytes, as `rp11-entry-env/1`: `LC_ALL=C`,
  `PATH=/usr/bin`, `INVOCATION_ID=⟨32⟩`. `rp11-helper-env/1a` is the first two only.
* **State operations**, in the accepted order [D2 §5.7]: argv check `111`;
  `INVOCATION_ID` `112`; `fcntl(F_GETFD)` on 0, 1, 2 `113`; `close_range(3,
  0xFFFFFFFF, 0)` `114`; every signal disposition reset except `SIGKILL` and
  `SIGSTOP`, then the mask cleared `115`; `umask(0077)`; `chdir("/")` `116`; the
  `execve` `117`.
* **System calls**: exactly the launcher's inventory (`fcntl`, `close_range`,
  `rt_sigaction`, `rt_sigprocmask`, `umask`, `chdir`, `execve`, `write`, `exit_group`).
  AD-8 holds only for that closed inventory [R2 §12].
* **Not touched and not claimed**: limits, `no_new_privs`, capabilities, securebits,
  seccomp, namespaces, cgroup, scheduling, `oom_score_adj` (R-10, K-5). It claims
  nothing about `NoNewPrivileges` for the root roles.

**The literals (design text; none is run).**

```text
ExecStartPre=+/usr/local/libexec/freedom-blades-rp11/rp11-rootexec consume
```

```text
sudo -n /usr/bin/systemd-run --system --no-ask-password --quiet
  --unit=⟨activation_id⟩ --service-type=exec
  --property=Restart=no --property=OOMScoreAdjust=-1000
  --property=RuntimeMaxSec=⟨L⟩ --property=TimeoutStopSec=⟨S⟩
  "--property=ExecStopPost=/usr/local/libexec/freedom-blades-rp11/rp11-rootexec stop-post ⟨activation_id⟩ ⟨a2_sha256⟩"
  /usr/local/libexec/freedom-blades-rp11/rp11-rootexec hold ⟨activation_id⟩ ⟨a2_sha256⟩
```

```text
/usr/bin/systemd-run --system --no-ask-password --quiet
  --unit=⟨activation_id⟩-backstop --on-active=⟨R⟩ --on-unit-active=⟨R⟩
  --timer-property=AccuracySec=1s --service-type=exec
  --property=Restart=no --property=OOMScoreAdjust=-1000
  --property=RuntimeMaxSec=⟨S_b⟩ --property=TimeoutStopSec=⟨S⟩
  /usr/local/libexec/freedom-blades-rp11/rp11-rootexec backstop ⟨activation_id⟩ ⟨a2_sha256⟩
```

```text
sudo -n /usr/local/libexec/freedom-blades-rp11/rp11-rootexec attest ⟨activation_id⟩ ⟨a2_sha256⟩
```

The grammar rules stand: no `--setenv`, `-E`, `--scope`, `--user`, `--pty`, `--wait`
or `--collect`, and no `%`, `$`, `\` or quotation mark apart from the shell quotes
around the `ExecStopPost=` argument. The image path contains **no `.`**, which
matters for extension matching (§9.10). The backstop literal carries BS-RM.

**What SSW closes.** The interpreter and the loader start under a closed environment
and a closed descriptor table. The manager's block, `sudo`'s block and the caller's
block never reach them.

**What SSW leaves, by name.** CPython and glibc stay in the root path. Their **file**
inputs stay inputs: MF-1, MF-2, MF-4 (§9.8, §9.9). The dynamic children stay (MF-9).
HB-1 stays. **Each is a reason it is not Route 3.**

**The baseline decision that would precede selecting it.** Peter, as Acceptance
Authority, would amend the accepted Route 3 boundary [DR1 §5.3, R3 §6.3] to read:
*"the root procedures start under a closed environment and a closed descriptor
table; CPython and the glibc loader remain in their path; the file-based inputs of
one interpreter and its closure are bound by MF-1, MF-2 and MF-4 and by the drift
gates"*, through §0.2 steps 1 to 5: a change-log entry, an impact assessment, the
Product Owner recommendation and Technical Lead review, Acceptance Authority approval,
and a new baseline version if the roadmap or release boundary changes. **This
proposal does not make that decision, does not request it, and does not use DEC-1 or
the acceptance of this proposal to make it.** The same applies, with the alternative's
own text, to SCDC and ACCEPT-X1.

### 9.8 PO-12′ and PO-19 under the corrected boundary

| Obligation | Today | **LIT-FULL** (R3-ROOT) | **LIT-DR1** | **SSW** | **SCDC, ACCEPT-X1** |
|---|---|---|---|---|---|
| **PO-12′** (CPython `-I -S` start-up) | PO-12 and AS-8 **refuted** [R2 §10.4]; PO-12′ source-established, binding needs MF-4 | still necessary, **narrowed to the entry** (the one remaining Python process). The environment precondition is met by the entry's literal environment; the **file** inputs remain MF-4 | **eliminated**: no Python process remains | necessary for the entry **and** the five root roles; environment precondition by byte-level construction of two static images; file inputs MF-4 | SCDC: entry only. ACCEPT-X1: entry only, and **PO-12 stays refuted for the root roles** |
| **PO-19** (glibc loader inputs) | **not established** (MF-1, MF-2) | still necessary, **narrowed to the entry** (one executable and its closure). (a′) file inputs MF-1; (d) ownership MF-2 | **eliminated** for Python; each static image is its own D9 case | the same six processes; (a′) MF-1 and (d) MF-2 for them | SCDC: the entry **and** the dynamic children (MF-9). ACCEPT-X1: the entry; the root roles stay **open** |
| **PO-9R, D9-1 … D9-4** | not applicable | for the entry launcher and every static root image | for every static image | for the entry launcher and the wrapper | for the entry launcher (and the SCDC image) |
| **PO-17** | **not evaluated** against any image | per image (§9.10) | per image | per image | per image |

The binding tuple of [R2 §11.6] is unchanged for whatever still runs `python3.14`:
`python3.14-minimal` `3.14.4-1ubuntu0.2`, `libc6` `2.43-2ubuntu2.4` and
`/usr/bin/python3.14`'s SHA-256 `be9a2a5e…69fd`. Its dynamic-section row stays
**unestablished** until MF-1 is observed. **No alternative closes PO-19 by itself.**

### 9.9 Root-owned dynamic inputs are still inputs

R1 wrote that Route 3 "removes the part R2 refuted (the ambient environment) and
leaves the part that was never refuted and never observed (the files)", and that it
"does not need to" close the file inputs. That sentence is **withdrawn**. The accepted
Route 3 *does* need them out of the root path, and SSW does not take them out.

The ownership of `/etc/ld.so.preload`, `/etc/ld.so.cache`, `DT_RUNPATH` and
`DT_NEEDED` of `/usr/bin/python3.14` and each loaded object, the trusted directories
and their `glibc-hwcaps` subdirectories, `/usr/bin/python3.14._pth`, `pyvenv.cfg`,
`pybuilddir.txt`, `Modules/Setup.local` and `/usr/lib/python3.14` determines **who can
change them**. It does not stop them being **inputs of the process**. The threat model
excludes an unprivileged writer, and that explains **how a residual is argued** (R-8,
OH-D-6). It does **not** make a root-owned dynamic input stop being something that must
be (a) observed, (b) bound by digest, version and ownership, and (c) covered by a drift
gate. Such an input ceases to be an input of a root procedure **only if no process of
that procedure loads it**, which is LIT-FULL's property for the root path and not
SSW's. The entry still loads them under every alternative except LIT-DR1.

### 9.10 PO-17, the byte-level boundary, and the OH-S4 / OH-S4p split

[R2 §12.9] established PO-17's premises and left it **not evaluated against any
launcher image**. For **each** static image that is an `execve` target (the entry
launcher in every alternative but LIT-DR1; the wrapper under SSW; every static root
image under LIT) **OH-S4p** (repository only) must supply:

1. **The bytes.** The file's complete bytes (a digest and a size) and its **first 256
   bytes** (`BINPRM_BUF_SIZE`, [R2 §12.9 (3)]), recorded as an independent digest and
   as hex in the review record.
2. **The installed path string**, exactly as it will be passed to `execve`
   (`bprm->interp`), and the statement that **it contains no `.`** over the whole path.
   Extension entries compare the text after the last `.` in the *full path*, not the
   basename [R2 §12.9 (4)]. `rp11_h1.py` and `rp11_entry.py` are arguments, not
   `execve` targets.
3. **The mechanical evaluation** of every recorded `binfmt_misc` entry against the
   image under premises 2 … 4 of [R2 §12.9] and the algorithm of [D §4.3.6]: the global
   gate, the per-entry enable bit, the magic comparison (`offset`, `size`, optional
   `mask`, over the 256 bytes) and the extension comparison on the full path. The
   accepted H-0 recorded one entry, `python3.14` (`offset 0`, magic `2b0e0d0a`, no
   mask, interpreter `/usr/bin/python3.14`, flags empty). An ELF image begins
   `7f454c46`, so a *preliminary* result can be computed from bytes alone. It is a
   **preliminary, record-bound evaluation**. PO-17 is **not discharged** by it.
4. **The live evaluation** at H-1's P-0, at V-1 and at H-2, against the entries
   re-observed on the host (HF-14), with any new, changed or enabled entry an INVALID
   RUN.
5. **The static-image facts** D9-2 already requires: `ET_EXEC`, no `PT_INTERP`, no
   dynamic section, no relocation or TLS, a closed list of `.rodata` strings, no `ret`,
   no `call`, the closed system-call set (for a root image under LIT, the set WP-4
   fixes, with AD-8 restated over it).
6. **The delta of the entry image**: A1 and nothing else. Every other source file
   hashes equal to its accepted value, and the compile line is byte-identical.
7. **The pins**: the new digests in `expected.sha256` and the manifest, the A-2 and
   H-1 fields they feed, and the independent bindings of §9.11.

OH-S4p **does not** contact a host, install anything, edit the operational draft or run
any activation step.

**The split under each alternative.**

| Alternative | **OH-S4** (repository implementation that is not a launcher image) | **OH-S4p** (launcher images, byte level) |
|---|---|---|
| **LIT-FULL** | the entry-side Python (bootstrap, tests), the H-1 and H-2 tooling if BQ-3 is out of scope, the activation tests that do not depend on an image | the entry retarget (A1) **and every static root image**. *The split is by image versus non-image, not by "non-launcher code":* the root procedures **are** images, so OH-S4 shrinks and OH-S4p grows |
| **LIT-DR1** | the tests and tooling that remain | every static image, including the entry |
| **SSW** | the Python procedures `rp11_h1.py` and its tests, under 3.14 and the suite interpreter | the entry retarget and the wrapper |
| **SCDC** | the entry-side Python and tests | the entry retarget and the SCDC image, with a much larger proof obligation |
| **ACCEPT-X1** | the Python procedures and tests | the entry retarget only |
| **WITHDRAW** | none | none |

### 9.11 Reproducible source, build, pinning, digest, ownership, installation, update, rollback and drift *(none performed; applies to each static image of any alternative)*

* **Source.** `infra/rp11-launch/` gains one source file per added image. Every image
  shares `start.s`, `select.h`, `rp11-launch.ld`, `build.sh`, `toolchain.lock` and
  `build-root.manifest`. **The entry image's compiler flags and every other source byte
  are unchanged**, apart from A1. Source SHA-256 values are recorded before and after.
* **Build.** The accepted chain, unchanged in method: `provision.py` and `enter.py
  build` over the pinned Ubuntu snapshot archive (`archive_snapshot=20261001T000000Z`,
  every package SHA-256 in `toolchain.lock`), `build.sh` as the first process in the
  verified build root, the same-invocation R-1 tree-manifest gate, IC-1, and R-2 as the
  unprivileged build user. It produces one image per source file.
* **Pinning.** `expected.sha256` gains four rows per added image (image, listing, map,
  assembly). The manifest takes one new version with every contract. A-2 pins the image
  digests.
* **Independent bindings** for each image, as [D §4.5.2]: `expected.sha256`, the
  manifest contract, an accepted independent-rebuild record (D9-3), and Codex's
  independent decoding (XD-11).
* **Ownership.** Each image is a regular file, `root:root`, `0755`, with no set-user-ID,
  set-group-ID or sticky bit, no `security.capability` and no `system.posix_acl_*`
  attribute, a member of tree **L** (§4.2.3). Its parents are the accepted tree **L**
  parents. Its path contains no `.`.
* **Installation.** By H-1 only (PT, PF, M-1), from the OH-S5 rebuild's bytes read
  **once**, hashed in memory and written from those bytes ([D §4.2.4]). The H-1 record's
  `baseline.files` gains each image (SHA-256, size, owner, mode, `(dev, ino)`),
  compared by H-2.
* **Update.** **Never in place.** A new image is a new OH-S4p cycle (D9-1 … D9-4), a new
  OH-S5, then RB-1 and a new H-1, because H-1 requires its paths absent at P-0. A
  distribution update of `python3.14-minimal`, `libc6`, the kernel, `systemd` or
  `polkitd` is not an update of an image: it is drift.
* **Rollback.** RB-1, separately authorized and never automatic, removes tree **L**'s
  members, including every static image. No procedure removes one during an activation.
* **Drift, checked before any lock object or grant exists.** The kernel, `systemd`,
  `polkitd`, and, **for whatever still runs them**, `libc6`, `python3.14-minimal` and
  `/usr/bin/python3.14`'s SHA-256 of [R2 §16]; **every image digest**, the entry
  launcher's digest and the digest of the root procedures' non-image code, each against
  the H-1 record; the nine Polkit rule digests of [R2 §16]; the HF-14 entries; and the
  unit's loaded configuration. P-0, H-2, AP-0 and AM-0 each compare. Any difference is
  INVALID RUN followed by re-citation, **never accepted at run time**.
  `unattended-upgrades` is active (HF-17), so drift is expected unless separately
  controlled, and a package hold is not authorized (R3 §6.7).

### 9.12 Failure and recovery for missing, altered, wrongly owned or incompatible artifacts

| Artifact | Condition | Detected by | Behavior | Recovery owner |
|---|---|---|---|---|
| a static root image | **missing** | H-1's own post-install verification, H-2, AP-0 | INVALID RUN; no lock object, no grant. After `ACT`: the holder never starts, so no grant was linked (§5.5 row 12); an `ExecStopPost=` or backstop that cannot execute it is RO-2 | RB-1 then H-1, separately authorized. **No in-place repair** |
| | **altered** (digest) | H-2, AP-0, AM-0 | INVALID RUN or HARD STOP before AM-1 | as above |
| | **wrong owner, mode or extended attribute** | H-2, AP-0 (`lstat`, `listxattr` names) | INVALID RUN | as above |
| | **incompatible**: the kernel cannot run it, an enabled `binfmt_misc` entry matches it, or a system call it needs is refused | P-0 and H-2 (PO-17 live evaluation, D9-4); the first start of a **test** unit under OH-S8b | INVALID RUN; if met at run time, the start ends and `ExecStart=` is never executed | design review |
| `rp11-launch` (entry) | missing, altered, wrongly owned, incompatible | as above | as above; at run time the unit fails and no pass runs (PO-21 (o) governs `ExecStart=` itself) | as above |
| the non-image root code (`rp11_h1.py` under SSW, SCDC, ACCEPT-X1) | missing, altered | H-2, AP-0, AM-0 (digest pinned by A-2) | as above; at run time CP's helper does not run, so no pass | as above |
| `python3.14` and its closure (wherever still used) | version or digest drift | P-0, H-2, AP-0 (the §9.11 drift list) | INVALID RUN, then re-citation | OH-S2b |
| the unit | altered after H-1 | H-2, AP-0 (`baseline_sha256`) | INVALID RUN | RB-1 / H-1 |

### 9.13 Trusted and runtime surface, compared under the corrected boundary

| Criterion | **LIT-FULL** | **LIT-DR1** | **WITHDRAW** | **SSW** | **SCDC** | **ACCEPT-X1** |
|---|---|---|---|---|---|---|
| Meets the accepted Route 3 | yes | yes (wider) | yes | **no** | **no** | **no** |
| Decision-ready | **no** (WP-1 … 7) | **no** (WP-1 … 8) | n/a | yes, as an alternative | no | yes, as an alternative |
| New trusted code | static images implementing the root procedures and loader-free interfaces: **no accepted measure, and no accepted proof method for that inventory** | LIT-FULL plus a Python-free entry | none | one small static image of an already-reviewed class | a static core as large as LIT-FULL's logic | none |
| CPython in the root path | **absent** | absent everywhere | n/a | present | absent from the helper logic | present |
| Dynamic loader in the root path | **absent** (LR-2) | absent | n/a | present | **present via children** | present |
| Environment inputs to root procedures | RH-1 by construction | RH-1 by construction | n/a | RH-1 by construction | RH-1 by construction | **ambient (PO-12 refuted)** |
| File-based loader and interpreter inputs | removed from the root path; remain for the entry (MF-1, MF-2, MF-4 narrowed) | removed everywhere | n/a | **remain (six consumers)** | remain for children and entry (MF-1, MF-2, MF-4, MF-9) | remain |
| Drift exposure | the entry only | none from Python | n/a | `python3.14`, `libc6` updates trigger re-citation (HF-17) | as SSW plus the children | as SSW |
| Review | a new design cycle, a new proof method, security re-review | larger still | a decision, with consequences for the Phase 5 plan | one new static image through the accepted chain, plus the §0.2 change | everything in LIT-FULL's logic, **and** the §0.2 change | the §0.2 change and a residual acceptance |
| Reversibility | RB-1 removes the images | the same | n/a | RB-1 removes the image | the same | none needed |

The comparison supports one statement without selecting anything: **only LIT-FULL,
LIT-DR1 and WITHDRAW satisfy the accepted boundary, and none of them is decision-ready
except WITHDRAW, which ends the design.**

### 9.14 Negative tests the Route 3 outcome would define *(proposed; none run)*

| ID | Case | Asserts |
|---|---|---|
| NT-RH-1 | every root role against an environment block containing each of `PYTHONEXECUTABLE`, `__PYVENV_LAUNCHER__`, `PYTHONPATH`, `PYTHONHOME`, `PYTHONSAFEPATH`, `mimalloc_*`, `MIMALLOC_*`, `LD_PRELOAD`, `LD_LIBRARY_PATH`, `LD_AUDIT`, `GLIBC_TUNABLES`, `MALLOC_CHECK_`, `MALLOC_ARENA_MAX`, `LOCPATH`, `GCONV_PATH`, `LANG`, `LC_*`, `TZ`, `HOME`, a hostile `PATH`, and a duplicate or malformed `INVOCATION_ID` | RH-1: the observed environment of every image the root procedure executes is **exactly** the reviewed literal, by the strace-class method of [D2 §5.12], Method A. Malformed or duplicate `INVOCATION_ID` exits `112` for the four unit roles |
| NT-RH-2 | descriptors | RH-2: every descriptor ≥ 3 is closed before the first state operation; a closed descriptor 0, 1 or 2 is refused |
| NT-RH-3 | signals, mask, `umask`, working directory | RH-3 as the accepted launcher's tests |
| NT-RH-4 | each image | `ET_EXEC`, no `PT_INTERP`, no dynamic section, closed `.rodata`, no `ret`, no `call`, the closed system-call set |
| NT-RH-5 | the PO-17 matcher | over every image, the recorded HF-14 entry and generated entries (magic at offset 0 and elsewhere, masks, extension entries) |
| NT-LR-1 | **LIT-FULL only**: a process-tree scan of every root procedure under a stepped harness | every `execve` target is a static ELF with no `PT_INTERP`; **no CPython and no dynamic loader appears** (LR-1, LR-2) |
| NT-LR-2 | **LIT-FULL only**: the equivalence mapping (WP-6) | every accepted step and every accepted negative test has a counterpart that passes against the image |
| NT-SSW-1 | **SSW only**: five roles with a wrong `argc`, an operand of the wrong length or class, an extra argument, an unknown role, any `argv[0]` | exit `111` before any state operation; nothing executed |
| NT-SSW-2 | **SSW only**: unit text T-B1 and the baseline normalization | exactly the wrapper line; an altered image or a changed normalization is detected by the H-2 code |
| NT-SSW-3 | **SSW only**: the helper tests | run under CPython 3.14 as well as the suite interpreter, or the gap is stated |

---

## 10. MF-1 … MF-8: disposition under the corrected boundary *(nothing is collected here)*

The identifiers and facts are those of [R2 §14.3]. Two read-only observing slices are
**proposed** (names are proposal-local, neither is authorized): **H-0M1**,
unprivileged, and **H-0M2**, privileged and read-only. Each needs its own authority,
work ID, exact commands and evidence path, on `oracle-test` only. Both obey the
accepted H-0 prohibitions (no `env`, `printenv`, `/proc/*/environ`, no secret, no
`ldd`, no `LD_TRACE_LOADED_OBJECTS`, no listing of retained paths). ELF parsing, if
needed, reads file bytes and executes nothing from the closure.

**Ordering consequence of the hard stop.** The consumer set of MF-1, MF-2 and MF-4
**depends on the Route 3 outcome**, so **the scope of their observation cannot be
fixed before WP-9**. MF-3, MF-5, MF-6, MF-7 and MF-8 do not depend on it and may be
observed earlier, if separately authorized.

**Route 3 effect, by alternative.**

| MF | Fact (R2 §14.3) | **LIT-FULL** (R3-ROOT) | **LIT-DR1** | **SSW** | **SCDC** | **ACCEPT-X1** |
|---|---|---|---|---|---|---|
| **MF-1** | `/usr/bin/python3.14` `DT_RUNPATH`, `DT_RPATH`, `DT_NEEDED`, `DT_FLAGS_1`, `PT_INTERP`, and the same for each object in its closure | **narrowed** to the entry's one executable and closure | **eliminated** (no Python) | six consumers; the closure covers what the root helpers import | entry plus the dynamic children (MF-9) | entry only; the root roles stay **open** |
| **MF-2** | type, owner, mode of `/lib`, `/lib/x86_64-linux-gnu`, `/usr/lib`, `/usr/lib/x86_64-linux-gnu`, their `glibc-hwcaps/x86-64-v{2,3,4}`, and each library MF-1 resolves to | **narrowed** to the entry's closure | **eliminated** | six consumers | entry plus children | entry only |
| **MF-3** | privileged read-only inventory of `/etc/polkit-1/rules.d` (names, types, owners, modes, SHA-256) | **unchanged** | unchanged | unchanged | unchanged | unchanged |
| **MF-4** | absence or root ownership of `/usr/bin/python3.14._pth`, `/usr/pyvenv.cfg`, `/usr/bin/pyvenv.cfg`, `/usr/bin/pybuilddir.txt`, `/usr/bin/Modules/Setup.local`; ownership of `/usr/lib/python3.14` | **narrowed to the entry**; the sole remaining residual of PO-12′ | **eliminated** | six consumers | entry | entry only |
| **MF-5** | whether the ext4 filesystem on `/dev/sda1` has a journal (`has_journal`) and its data mode | unchanged | unchanged | unchanged | unchanged | unchanged |
| **MF-6** | run-time `fs.protected_hardlinks` and `fs.protected_symlinks` | unchanged | unchanged | unchanged | unchanged | unchanged |
| **MF-7** | `/run/nextroot` absent | unchanged | unchanged | unchanged | unchanged | unchanged |
| **MF-8** | the dash-prefix drop-in directories in all 12 unit paths | unchanged | unchanged | unchanged | unchanged | unchanged |
| **MF-9** *(new, optional)* | the dynamic sections and closures of the helper children: `/usr/bin/systemctl`, `/usr/bin/systemd-run`, `/usr/bin/pkcheck`, `/usr/bin/sleep` | **none** (LR-2: no dynamic child) | none | **optional**: whether the review wants helper children's loader inputs observed. Not required | **required** | not applicable |

**The observing slices, common to every alternative.**

| MF | Minimum observing slice and privilege | Exact-path scope | Evidence and drift trigger | Dependent gate |
|---|---|---|---|---|
| **MF-1** | **H-0M1**, no privilege. **After** the repository implementation fixes the import closure of every Python process that remains | `/usr/bin/python3.14`; each `/usr/lib/python3.14/lib-dynload/*.so` that the import record names; each library the recorded `DT_NEEDED` names resolve to, through `/etc/ld.so.cache` and the built-in directories, by reading bytes only | the parsed dynamic entries and a SHA-256 for each file, as admitted capture records. **Drift:** any change of `python3.14-minimal`, `libc6`, any digest in the closure, or the import closure | PO-19 (a′) binding (OH-S2c); H-1 readiness |
| **MF-2** | **H-0M1**, no privilege | exactly the MF-2 paths: `lstat` of each and its parents, extended-attribute **names** only | type, owner, group, mode, `(dev, ino)`, attribute names. **Drift:** any ownership or mode change, a changed `ld.so` configuration, a `libc6` change | PO-19 (d) |
| **MF-3** | **H-0M2**, root, read-only, one reviewed fixed literal. **Recommended before H-1** (DEC-4) | exactly `/etc/polkit-1/rules.d` and each regular file in it, by digest only | names, types, owners, modes, SHA-256. **Drift:** any added, removed or changed file; re-observed at H-1's P-0p. A later PK result corroborates and never replaces it | PO-11 (b), (g); H-1 readiness |
| **MF-4** | **H-0M1**, no privilege | exactly the five paths and `/usr/lib/python3.14` | `lstat` results (`ENOENT` or type, owner, mode). **Drift:** appearance of any of the five, or an ownership change | PO-12′ binding; H-1 readiness |
| **MF-5** | **H-0M1** if an unprivileged read exists, otherwise **H-0M2** read-only. **The slice must name the exact read-only path or literal.** This proposal asserts no availability | the one device already recorded by HF-15 | has-journal yes/no and the data mode. **Drift:** a different filesystem, a changed mount option (HF-15 is re-observed at P-0 and AP-0 anyway) | PO-20 (a), (d); H-1 readiness |
| **MF-6** | **H-0M1**, no privilege | the two named kernel parameters | the two values. **Drift:** a sysctl change | PO-20 (a) |
| **MF-7** | none separate: AP-0 and AM-0 already observe it. H-0M1 may record it early | `/run/nextroot` | `lstat` → `ENOENT`. **Drift:** any creation of the path | CL-21i acceptance; before any A-2 |
| **MF-8** | **H-0M1** (early knowledge) and H-1 (the mechanical check, `DropInPaths` empty) | the 36 paths (3 names under each of the 12 unit paths of HF-13) | `lstat` each. **Drift:** existence of any | HF-13 completeness; H-1 P-0 |
| **MF-9** | **H-0M1** if required, no privilege, bytes only | the four binaries and their closures, as MF-1 | as MF-1 | only under SCDC, or if the review elects it under SSW |

---

## 11. Successor order and review gates *(no successor is authorized by naming it)*

Every row needs its own prompt, authority record, work ID and Codex review. The order
is a dependency order. Rows with the same number may run in parallel. None of them is
requested here. The hard stop changes the order of R1: **Route 3 readiness precedes
every row that depends on the executable boundary.**

| Order | Slice (proposal-local name) | Scope | Host | Gate before it | Closes |
|---|---|---|---|---|---|
| **G-0** | independent Codex re-review of this proposal and handback | review | none | — | the findings of this return |
| **G-1a** | **Peter's decisions on the activation design** DEC-1 … DEC-6 (§12.1), after a **clean** review | decision | none | G-0 clean | the activation-design choices only |
| **G-1b** | **Peter's direction on Route 3** (§12.2): commission WP-1 … WP-7 (or WP-8); **or** open a §0.2 change request for a scope-change alternative; **or** WITHDRAW. **Not a DEC and not a consequence of accepting this proposal** | decision | none | G-0 clean | which of §9.4's paths proceeds |
| **2R** | **Route 3 readiness**: WP-1 → WP-2 → WP-3 (a citation slice) → WP-4 → WP-5, WP-6, WP-7 (and WP-8 for LIT-DR1) → Codex review → WP-9, Peter's recorded choice | documentation, plus a citation slice | none | G-1b | the hard stop |
| **2R′** | **§0.2 change control** for a scope-change alternative, if Peter chooses that path: change-log entry, impact assessment, Product Owner recommendation and Technical Lead review, Acceptance Authority approval, a new baseline version if needed | governance | none | G-1b | the baseline change, **before** any design acceptance of SSW, SCDC or ACCEPT-X1 |
| **2a** | **OH-S2b**: citation addendum for the new and restated obligations (§13.2), including BS-RM's `RuntimeMaxSec=` on a timer-started `Type=exec` service and the `Type=exec` start-job completion | documentation, U-10 | none | G-1a | PO-20 (f′-2 … 5), PO-21 (s′) floor, [E1], [E2], **PO-SN (a) … (f) (Δ3)** and, optional, **(g) (Δ4)**, and, evidence only, **PO-SN (c′) (Δ6)**; confirms (c′) and (d′) as design acceptances |
| **2b** | **OH-S3S**: operational-draft incorporation (Appendix B), if separately needed | documentation | none | G-1a (and 2R for the rows that depend on the boundary) | the draft's A-2 pins, matrix, interruption, stop and handback rows. Codex re-review of the draft (A-1) |
| **2c-I** | **OH-S0d, part I**: apply Appendix A-I (the route-independent rows) to the one-host design as a cumulative amendment | documentation | none | G-1a | the accepted inactive design is amended in place. Codex re-review, then Peter's acceptance |
| **2c-II** | **OH-S0d, part II**: apply Appendix A-II (the boundary-dependent rows) | documentation | none | **2R** (and 2R′ if applicable) | the boundary-dependent text. Codex re-review, then Peter's acceptance |
| **3a** | **OH-S4 (amended)**: **Route 3 implementation** and its tests (30) … (35), for what the chosen outcome leaves as non-image code | repository only, unwired, nothing installed | none | 2c-I accepted, 2R decided (and 2a for version-bound data) | LD, IGR, GRR, SD, PK/2, SG, DL, HS and the role vectors. **Security-focused Codex review** |
| **3b** | **OH-S4p**: the launcher images, byte level (§9.10), for every image the chosen outcome includes | repository only | none | 2c-II accepted | PO-9R, D9-1 … D9-2 documentary and mechanical parts, the preliminary PO-17 evaluation. **Byte-level, security-focused Codex review** |
| **4** | an **R-5-class independent rebuild** of every image (D9-3), then **OH-S5** (the installation-source rebuild, §4.5), where still applicable | build as `ubuntu` on `oracle-test` | `oracle-test` | 3b accepted (and 3a for the tool bytes) | D9-3; the installation-source record. Retained R4/R5 outputs stay evidence only and are never an installation source |
| **5a** | **read-only MF collection**: H-0M1 and H-0M2, for MF-3, MF-5, MF-6, MF-7, MF-8 | read-only | `oracle-test` | G-1a; they do not depend on Route 3 | those observations |
| **5b** | **read-only MF collection**: H-0M1, for MF-1, MF-2, MF-4 (and MF-9) | read-only | `oracle-test` | 2R decided; 3a (the import closure) | those observations, at the consumer set the outcome fixes |
| **6** | **OH-S2c**: citation closure binding PO-19 (a′), (d), PO-12′, PO-11 (b), (g), PO-20 (a), (d) to the MF observations | documentation | none | 5a and 5b accepted | PO-19, PO-12′ and PO-11 verdicts |
| **7** | **H-1 readiness review** | review | none | 2a, 2b, 2c-I, 2c-II, 2R, 3a, 3b, 4, 5a, 5b, 6 accepted; DEC-1 … DEC-6 recorded | the readiness list of §11.1 |

After G-7 the accepted successors are unchanged and **separately authorized**: OH-S7
(H-1 assignment preparation), OH-S8 (H-1), CPP, H-2, OH-S8b (activation fault drill),
then A-2, `ACT`, Pass A and `DEACT`. Cleanup (LC-3 … LC-5) and workspace recreation
stay separate and are not sequenced by this table.

### 11.1 H-1 readiness list *(a review checklist, not an authority)*

1. DEC-1 … DEC-6 recorded; **Route 3 established** by a recorded WP-9 choice, or a
   §0.2 change accepted; the repaired design accepted as the inactive basis;
   Appendix A applied to the one-host design (OH-S0d) and accepted.
2. PO-20 (f′), PO-21 (c′), (s′), PO-11 (d′) and PO-SN (a) … (f) accepted; PO-9R, D9-1 … D9-4 and the
   preliminary PO-17 evaluation accepted for **every** image.
3. PO-19 and PO-12′ **bound** to MF-1, MF-2 and MF-4 at the consumer set the outcome
   fixes, or each explicitly returned.
4. MF-3 observed and PO-11 (b), (g) decided; MF-5 and MF-6 observed and PO-20 (a),
   (d) decided; MF-7 and MF-8 covered.
5. The operational draft amended (OH-S3S) and re-reviewed (A-1).
6. The drift list of §9.11 fixed to accepted values.
7. **No elapsed-time claim anywhere in the accepted design, the operational draft or a
   record states a bound that §7.7 withdrew** (NT-DL-4).

---

## 12. Decisions

### 12.1 Decisions Peter may make only after a clean independent review

No accepted decision is silently changed by this proposal. **OH-D-1 … OH-D-10, OS-6,
OH-D-6 … 8, U-9's text, M-B, M-S and the R2 dispositions are not changed.** Each
decision below has a recommendation and bounded alternatives. **None of them selects a
Route 3 alternative.** R1's DEC-1 (the Route 3 choice, which superseded D-3) is
**withdrawn**: D-3 is not superseded by anything in this proposal.

| ID | Decision | Recommendation | Bounded alternatives | Consequence |
|---|---|---|---|---|
| **DEC-1** | **PO-21 (c).** Which residual is acceptable | accept **RO-1** (§5.6) as the named, outside-guarantee, pre-pass and inert residual, together with RO-4 and RO-6 | elect **ALT-SENT** (§5.9), a resident sentinel, to narrow RO-1 | accepting adds no code beyond IGR and GRR. ALT-SENT adds a long-lived root image or process, citations and a drill |
| **DEC-2** | **Operational parameters** (§7.6) and the **backstop correction BS-RM** | P 30,000, c 5,000, g 2,000, λ 5,000, S 120 s, S_b 120 s, R 60 s, B 20, ρ 30,000, `slice_ms` 100, `journal_max_bytes` 1,048,576, `act_wait_s` = L. N1 holds with 16 s to spare under the 90 s default start timeout. **BS-RM adopted** | a shorter P (for example 15,000), at some risk of false `unconfirmed`; **or** a larger P with an explicit `TimeoutStartSec=` in the unit, which changes the reviewed unit bytes (T-B1) and the H-1 baseline; **or** keep the accepted backstop literal and record RO-5 as an accepted residual | the values are A-2 pins. A wrong value fails closed (no pass, a refused start), never open. **They are sizing parameters and never bounds** (§7.6) |
| **DEC-3** | **Lock and identity objects** (LD-1, GI-1) | the root-only object **K** under `/run` **with `grant.id`** | K without GI-1 (CL reads the `ubuntu`-owned journal as accepted; RO-6 widens and R1's flagged residual stays); **or** keep the `ubuntu`-owned evidence directory as the lock object and rely on GR-1 and LD-2 … LD-6 only | K adds one `/run` object and path rows; GI-1 adds one tmpfs file. Keeping the old object leaves `ubuntu` able to hold the lock, which then only refuses CP and delays HL, never holds a grant |
| **DEC-4** | **MF-3's observing slice** | a separate privileged read-only slice (**H-0M2**) **before H-1** | observe it in H-1's P-0p | the alternative saves a slice but settles PO-11 (b) only at install time |
| **DEC-5** | **CX-4 retirement.** Record that CX-4 is void for the cited systemd, because the accepted PO-21 (u) shows that a stop during `start-pre` ends the attempt `failed` | record the retirement, bound to systemd `259.5-0ubuntu3.4` | keep CX-4 as accepted (harmless) | retiring changes no mechanism. It removes a documented residual and adds the version-bound drift trigger of §6.8 |
| **DEC-6** | **Signal and removal discipline.** Adopt SG-1 … SG-8, GR-2 and the single-routine GRR as the activation design's removal and signal contract | adopt | keep R1's exception-raising handler (withdrawn here because it can fire inside IGR); or omit GRR's sharing with CL-G | adopting narrows what can fail. The alternatives re-open R2-F2 items 6 and 7 |

### 12.2 Changes of the accepted Route 3 boundary: not decisions of this proposal

**Implementation-plan §0.2** requires, for *"a material change to scope, authority,
privacy, architecture, data ownership, release criteria, phase order or target range"*:
a change-log entry identifying requester, reason and affected requirements; an impact
assessment for scope, dependencies, estimate, risk, testing, migration and
operations; Product Owner recommendation and Technical Lead review; Acceptance
Authority approval before the change becomes effective; and a new baseline version
when the roadmap or release boundary changes.

A change of the accepted Route 3 boundary, **before design acceptance**, is such a
change. The following are the ones this record identifies. **Each is separate from
§12.1, and none can be made by accepting this proposal.**

| ID | Change | Needed for | Not needed for |
|---|---|---|---|
| **BC-1** | amend the Route 3 boundary so that CPython and the glibc loader may remain in the root path under a closed environment (for ACCEPT-X1 see the nuance in §9.4) | SSW; ACCEPT-X1 (with its residual acceptance) | LIT-FULL, LIT-DR1, WITHDRAW |
| **BC-2** | treat R3-ROOT as a *narrowing* of DR1 §5.3 (the `ubuntu`-run entry stays Python) | LIT-FULL, if a maintainer reads it as a narrowing | LIT-DR1 |
| **BC-3** | except the dynamic children (DI-1 … DI-6's binaries) from LR-2 | SCDC | LIT-FULL |
| **BC-4** | except `sudo`-started procedures or the installer class from LR-1 … LR-2 (BQ-2, BQ-3) | any LIT alternative that answers BQ-2 or BQ-3 by an exception | an alternative that answers them without one |
| **BC-5** | withdraw RP-11's one-host design or its activation part | WITHDRAW | everything else |

---

## 13. Residuals, status of every obligation, and what this does not establish

### 13.1 Residuals

| ID | Residual | Status |
|---|---|---|
| **X-1** | a root helper starts under PID 1's open block, so CPython and the loader consume ambient inputs [R2 §10.4, §15.4] | **open for the root roles** until Route 3 is established (§9). The activation design is conditional on RH (§2.4) |
| RO-1 | uncatchable holder end while PID 1 can spawn neither stop-post nor the backstop | **named** (§5.6); pre-pass, inert; DEC-1 |
| RO-2 | helper bytes damaged after `ACT`: stop-post and backstop fail together | **named** (§5.6); IGR unaffected; AP-0, H-2, AM-0 detect a prior tamper |
| RO-3 | PID 1 dead or hung | outside every unit guarantee [R2 §8 (c)] |
| **RO-4** | IGR not completed: the holder is killed or stalls before GRR's `unlinkat` | **new in R2** (§5.6); the state is G1 inert; the rungs and IL apply; **no IGR speed is claimed** |
| **RO-5** | a started backstop firing has no PID-1 bound, and a hung one prevents every later firing | **new in R2** (§5.6); closed by BS-RM if accepted (DEC-2); the `Type=exec` start-completion claim is proposed for citation |
| **RO-6** | a persistent stall of a filesystem or the kernel delays every rung that touches `ext4` | **new in R2** (§5.6); IL holds; the boot clears `/run`; GRR and, with GI-1, CL-G avoid `ext4` |
| **RO-7** **Δ3** **Δ4** **Δ5** **Δ6** | a child left behind by its helper (a successful, failed, indeterminate or unmade send; no reap by the final attempt; the helper ended first) **may be alive**, or (**Δ5**) was reaped by the kernel inside an interrupted attempt with nothing recording it (CS-5), **or (Δ6) whose reap attempt raised, so that no one knows whether it was reaped (CS-9, CS-10)**, holds no K descriptor and no grant, and is owned by the owner of its enclosing procedure (PID 1's cleanup of its unit, then the boot as a separate event); **the interactive `attest` has no automatic owner** | **new in R3, widened in R4, R5 and R6** (§5.6, §7.5a.7, §7.9, table SN-RO); mutating children have an *unknown* effect (SN-10); at most 20 abandoned or `reap-unknown` children per PK series at the recommended P |
| **CX-5** | with `τ₀ = 0`: a failed unidentified first attempt, then a root `reset-failed`, then the unit's unload | **new in R1, kept** (§6.5, SD-3); three root acts outside 𝒜 (SL-1 class). A later start runs the pass **with no grant** (G1 holds), but a second attempt occurs |
| CX-4 | a stop job during `start-pre` | **void** under R2 (u); retirement is DEC-5 |
| CX-1, CX-2, CX-3 | as accepted [D §4.2.5-R5 (k), R6 (f)] | unchanged |
| HB-1 | H-1, RB-1 and RS-1 run under `sudo`'s environment | **depends on BQ-3**: under SSW and ACCEPT-X1 it stays; under LIT-FULL it is either a stated exception (a BC, §12.2) or removed by a Python-free installer |
| SL-1, DF-1, GU | as accepted [D §4.2.5-R2 (l)] | unchanged |
| the `ubuntu`-owned `ACT` evidence directory | `ubuntu` can replace the journal, which makes CL class the rule A0 and keep it, and makes CP refuse (accepted analysis [D §4.2.5-R4 (b)]) | **narrowed by GI-1** for IGR and CL-G, which act on `grant.id` and the in-memory identity. **Unchanged for CP's CQ-3 and for CL's fallback**. Without GI-1 (DEC-3) it is unchanged for CL. Under OH-D-6 it is no more than `ubuntu` can already do |

### 13.2 Status of every obligation this proposal touches

| Obligation | Status after this proposal |
|---|---|
| PO-20 (f′-1) | **established** [R2 §7 (f)] |
| PO-20 (f′-2 … 5) | **proposed [N]**; OH-S2b citation |
| PO-21 (c′) | **established** [R2 §8 (c)] as a statement of what is not guaranteed; the ladder is design, not citation |
| PO-21 (s′) (1) … (4) | **established** [R2 §8 (s)]; (5) and the floor in (1) are **proposed [N]** |
| PO-21 (u) | **established** [R2 §8 (u)]; load-bearing for CX-4's retirement (version-bound) |
| PO-11 (d′) | a **design acceptance**: it claims no bound, so no citation is needed. PO-11 (e), (f)(i), (f)(ii), (f)(iv) as accepted; (b), (g) remain **not established** (MF-3) |
| **BS-RM** (`RuntimeMaxSec=` on a timer-started `Type=exec` service; start-job completion of `Type=exec`) | **proposed [N]**; OH-S2b citation; same code path as [R2 §8 (d), (r)] |
| **SG-1 … SG-9** (CPython 3.14.4 signal-handler timing and restart behaviour; the process-creation arguments of HS-3; SG-9 added in R3) | **proposed [N]** wherever the holder stays Python; OH-S2b citation. **Not applicable** where the Route 3 outcome removes Python from the holder |
| **PO-SN (a), (b), (c), (e), (f)** **Δ3** (`kill`/`killpg` semantics; PID and process-group number non-reuse; CPython `subprocess` and `setsid` **(Δ6: R5's clause on a post-reap exception is moved to PO-SN (c′))**; systemd cgroup cleanup; the `SIGCHLD` disposition) | **proposed [N]**, version-bound (HF-04 kernel, `libc6`, `python3.14-minimal`, systemd); OH-S2b citation; **AP-0 is INVALID RUN until accepted**. No accepted record cites any of them (§7.5a.8). Not applicable where a Route 3 outcome removes Python, which then needs the replacement's own equivalents |
| **PO-SN (d)** *(optional)* **Δ3** (`/proc/⟨pid⟩/stat` start time) | **proposed [N]**; if not accepted, SN-4 (iv) is removed and no safety claim changes |
| **PO-SN (c′)** *(evidence only)* **Δ6** (whether `Popen.poll()` can raise and, if so, whether after the kernel's reap) | **proposed [N]**, version-bound; OH-S2b citation; **no decision depends on it, AP-0 does not read it, and either answer leaves the design safe** (RE-6) |
| **PO-SN (g)** *(optional)* **Δ4** (the children of an ended process: reparenting, group, session and cgroup membership, reaping by the new parent) | **proposed [N]**, version-bound; OH-S2b citation; **nothing relies on it**: §7.9 states the fate of a child after its helper ends as unknown to the design |
| **SN-1 … SN-10, SI-1 … SI-5** **Δ3** **Δ7** | design **[N]**: a contract, not a citation; INV-19 … 21, INV-27; NT-SN-1 … 18 (**Δ7:** SI-5 states the consequence of a violated sole-reaper invariant and adds no obligation; NT-SN-12 rewritten) |
| **WB-1 … WB-7, IS-1 … IS-10, CS-1 … CS-10, RB-1 … RB-4, RE-1 … RE-6** **Δ4** **Δ5** **Δ6** | design **[N]**: a contract, not a citation; INV-22 … INV-25; NT-WB-1 … 12 (NT-WB-5 as 5a and 5b), NT-IS-1 … 17, NT-RE-1 … 12, NT-NS-1 … 8 |
| **GD-1 … GD-5** **Δ7** | design **[N]**: a contract about the design's own record, not a citation; INV-22 (amended), INV-26; NT-GD-1 … 4 |
| PO-9R | **proposed**; OH-S4p, D9-2, for every image of the chosen outcome |
| PO-12′ | **source-established**; binding needs MF-4 at the consumer set of §9.8 |
| PO-19 | **not established** (MF-1, MF-2) |
| PO-17 | **not evaluated** against any image until OH-S4p; live evaluation at P-0, V-1, H-2 |
| PO-14, AD-7, PO-8, CL-21i | **established**, unchanged |
| **Route 3** | **not established** (§9.3). The accepted disposition "Route 1 returns to Route 3 design review" stands |

**Not addressed by this assignment, and still returned** [R2 §15.5 item 3]: PO-15 (d)
(`NeedDaemonReload`), AD-8 as a general statement, PO-17's type-E basename test, and
C-1 … C-14 other than those named in this proposal (C-9, C-10, C-11 and C-12 are
answered by §§4 … 6 and 9, with C-12 carrying the Route 3 hard stop).

### 13.3 What this proposal does not establish

It establishes no host fact and discharges no obligation. It does not show that any
image can be built, that any helper behaves as specified, that any parameter value
is right, or that any sizing rule holds on the host. Each of those is a later gate
(§11). It does not change PO-14, LB-2S's two prevention claims about the entry, A-2,
the start-only grant, one start attempt, the no-follow source-consumption contract,
evidence durability or any fail-closed rule, and §2 shows why none of the repairs can.
**It does not establish Route 3, and it does not establish that any alternative
conforms to it except by the criteria LR-1 … LR-6.**

---

## 14. Proposed independent-review focus

### 14.1 Questions

1. **§2, §2.4.** Is the reading right that no safety proof (G1 … G5) cites the lock, HL,
   `ExecStopPost=`, the backstop, a Polkit latency or any elapsed time, and is it
   right to state that G1 … G5 are conditional on RH until Route 3 is established?
2. **§4.** Are LD-1 … LD-9 sufficient to prevent a longer-lived process from retaining
   a lock? Is K the right choice over the `ubuntu`-owned directory, and is GI-1 sound
   (its creation before PF-6, its root-only tmpfs location, the `identity-conflict`
   rule)?
3. **§5.** Does GRR need any citation beyond signal delivery? Are IL and IL′ sound?
   Are RO-1 and RO-4 … RO-6 stated narrowly enough? Is the single IGR site and latch
   (IGR-0) idempotent under a second signal at every instruction boundary?
4. **§6.** Is BSP's use of `CLOCK_MONOTONIC` valid given [E1] and [E2]? Is CX-4's
   retirement under R2 (u) correct?
5. **§7 (R2-F2).** Does any statement in this document still imply an elapsed time for
   a class-X operation (search for it, not only for the strings of NT-DL-4)? Is the
   inventory of §7.3 complete for ACT, CP, IGR, CL, the backstop and verification, **including rows 3a … 3g (Δ3, Δ4)**? Are
   N1 … N4 correctly described as necessary conditions only? Is BS-RM's reading of
   `Type=exec` right, and is RO-5 a defect of the accepted design? Are the signal
   discipline and the interruption maps of §7.8 and §7.9 complete?
6. **§9.1 (R2-F1).** Is R3-ROOT the right working boundary, and is DR1 §5.3's wording
   (R3-DR1) correctly stated as the wider reading? Are BQ-1 … BQ-4 the right questions?
7. **§9.3.** Is the hard stop justified? Is there repository evidence for a loader-free
   interface (E-2) or a static proof method (E-3) that the search missed?
8. **§9.4, §9.7.** Is SSW described everywhere as a scope-change alternative and
   nowhere as satisfying Route 3? Is the baseline decision text of §9.7 the right
   statement of what §0.2 would need?
9. **§9.5.** Are WP-1 … WP-9 complete and ordered correctly? Is anything missing that
   would make a literal Route 3 decision-ready?
10. **§9.6, §9.8.** Is the Role A–H inventory complete against the current files? Are
    PO-12′ and PO-19 correctly narrowed per alternative, and is anything that R2 refuted
    still hidden inside them?
11. **§9.9.** Is the statement that root-owned dynamic inputs remain inputs correctly
    applied to every alternative?
12. **§9.10.** Is the byte-level PO-17 boundary complete, and is the OH-S4 / OH-S4p
    split right under each alternative?
13. **§10, §11.** Are the MF dispositions per alternative right, and is the successor
    order (2R, 2R′, 2c-I, 2c-II) free of a missing or circular gate?
14. **§12.** Is the split between decisions that follow a clean review (§12.1) and
    changes that need §0.2 (§12.2) correct, and does any DEC smuggle in a scope change?
15. **§7.5a (R3-F1).** Is the SN inventory (table SN-I) complete: is there any signal send
    by `spawn()`, another helper, cleanup or recovery that it omits? Is the pinning
    argument (SI-2, SI-3) with PO-SN (b), (c) sufficient against PID or group reuse, with
    validation only a detector? **Δ7:** does any sentence, record or test still say that validation detects a foreign reap or a coincidental reuse (SI-5, W-17)? Is it right that the escalation `SIGKILL` (S4) does not
    depend on the clock and that the reap wait is not shortened by a flag (CC-2)? Does any
    send result still get read as evidence anywhere in this document (search for "killed",
    "terminated", "dead", "gone")? Is the *effect unknown* rule of SN-10 enough for
    `systemd-run` and `systemctl stop`, and is RO-7's absence of an owner for `attest`
    acceptable? Are PO-SN (a) … (f) the right facts, and is AP-0's refusal until they are
    accepted the right consequence?
16. **§7.5a.6, §7.5a.6a (R4-F1).** Is there anywhere a timed wait that can begin at or after
    `t_g`, or a second grace period that a send, a validation, a poll, an error or a signal
    receipt can start (search for "grace", "wait", "poll", "sleep", "slice")? Is it right that
    S4's `SIGKILL` is not skipped after `t_g`, and that `SIGTERM` and `SIGKILL` may then be
    sent back to back? Is the final-attempt rule (WB-5) well defined for a child that exits
    during a send, at the boundary or just after it? Is the statement of the wait budget
    separately from elapsed time (WB-6) free of any residual claim that the sequence returns
    within g (search for "within g", "inside g", "by P + c + g")? Is extending the cap to
    every E wait (CC-10) acceptable, or should it be confined to S3 and S5?
17. **§7.9 IM-S, §7.5a.7 (R4-F2).** Does every cell of the matrix agree with table SN-S,
    and is every dash truly unreachable? Is the common state set CS-1 … CS-10 free of any
    state derived from a send result, a boot or a reap of the direct child? Are the owners of
    table SN-RO right for the holder, CP, stop-post and the backstop service, and is the
    absence of an automatic owner for the interactive `attest` acceptable as stated? Is
    `children-unknown`, derived from a missing terminal journal line, a sound way for a later
    procedure to report a lost record without searching (A-I-17)? Does any sentence still say
    that an ended helper leaves a child "unsignalled", "killed" or "gone"? **(R5, Δ5)** Does
    every cell, T3k, T5k and the corrected cells T0, T1 and T5 included, give a state that
    permits the true condition of the direct child, is every dash unreachable, and is the
    observer rule (IS-9) the right conservative reading of a kernel reap that no line records?
18. **§7.5a.6d RE-1 … RE-6, PO-SN (c′) (R6-F1; rewritten).** Does any path remain by which a
    signal is sent to a child after a `reap-error`, S4's `SIGKILL` included, or a retry, an
    alternate primitive, a further poll or a process search is made? Is `reap-unknown` free of
    any label that reads as *reaped*, *unreaped* or *abandoned* as a fact, and is the handle's
    permanence (RE-3) sufficient? Is the argument *why no process-group number is exposed*
    complete, given that every send is made on a `running` handle last seen by a normal return?
    Is it right that PO-SN (c′) is evidence only, and that no answer to it, in either direction,
    can make AP-0 pass a branch that sends after a `reap-error`? Does the suppression start any
    new wait or grace (RE-4), and are the result, the record and the owner and observer rules
    (RE-5) those of R5?
19. **§7.12 NT-WB-5a, NT-WB-5b (R5-F2).** Do the explicit costs and clock positions of the
    two slow-validation cases agree with table SN-S and WB-1 … WB-7, and does every
    assertion (the S3 and S5 sleeps, the `late` fields, the scheduled sleeping and
    `waits_skipped`) follow from the actual clock of that case?
20. **§7.5a.6 S1, S7, table SN-R rows 3, 9 and 12, §7.9 (R6-F2).** After the split of S1, does
    every `not-sent` subtype take exactly one branch (S7 for a settled handle, S5 for an
    identity rejection), and is no send ever made after one, S4's PK-only path included? Does
    every cell and dash of the matrix agree with table SN-S, is T5 `u` unreachable, and is it
    right that a handle already settled by an enclosing poll is at T6 or T7 and never at T0 or
    T1 (CC-23), with the settled-state decision at that poll's RA-3 and the record at S7? Do
    NT-NS-1 … 8 step every position before, during and after S1's branch?
21. **§0.8 CC-23 … CC-30 (R6).** Is each consistency correction necessary, in particular CC-23
    (which withdraws R5's CC-18 cells), CC-27 (which removes S4's send after a `reap-error`)
    and CC-30 (NT-SN-12's foreign-reap wording; **Δ7:** superseded by CC-33)? Does any of them change a class, a parameter,
    a send rule or a wait rule?

22. **§7.5a.6e GD-1 … GD-5, S0's entry condition, CC-31, CC-32 (R7-F1).** Is "`t_g` exists
    exactly when S0 ran" true on every path: a child that exits within c, a failed spawn, a
    pre-S0 `reap-error` (both truths), a settled handle, a *later* SN call on a pre-S0
    `reap-unknown` handle, and every post-S0 path? Is the schema check `s0_ran ==
    (grace_deadline_ms != null)` with its implications complete? Is CC-31 (S0 entered only for a
    `running` handle) necessary, or would you rather leave S0 before S1 and have a settled
    handle read and record a `t_g` that nothing uses? Does NT-GD-1 follow the enclosing poll
    through S8 and S7 correctly, with zero `t_g` reads, zero clock reads by SN, no grace period
    and every record field named? Is the new `outcome` value `reap-error` acceptable?
23. **§7.5a.3 SI-2, SI-3, SI-5, NT-SN-12, NT-SN-6 (b), W-17, CC-33, CC-34 (R7-F2).** Is the
    sole-reaper contract stated as load-bearing, with PO-SN (b), (c), (f) and the AP-0 refusal
    unchanged? Is "an injected foreign reap is a deliberate violation of a precondition, not a
    supported state" the right reading, and is "no reuse-safety claim from SN-4 alone once the
    invariant is violated" the honest consequence? Is NT-SN-12 (d) correctly labelled
    non-universal, and is (e) an acceptable way to keep the limit visible? Is it right that no
    `start_ticks`, pidfd or other identity mechanism is added in this remediation? Does any text
    outside the historical tables still claim that validation catches a foreign reap?
24. **§3 child handle (CH), §0.9 (R7-F3).** Does every current, non-historical definition of the
    handle state set list `running`, `reaped`, `abandoned` and `reap-unknown`, or a stated
    subset (the settled states) for its purpose? Is any historical text changed?

### 14.2 Claims that need independent security re-review

| # | Claim | Why | Gate |
|---|---|---|---|
| SR-1 | GRR's descriptor re-verification, and the residual name-to-descriptor window of `unlinkat` (as G-R1) | the removal path is now shared by IGR and CL-G | OH-S4 security review |
| SR-2 | GI-1: `grant.id` as the authoritative identity for non-holder rungs, `identity-conflict` resolved by `grant.id` | a new trust object, root-only, tmpfs | Codex security review, then OH-S4 |
| SR-3 | flag-only handlers, install-before-state, the IGR latch (SG-1 … SG-8, IGR-0) | replaces R1's exception-raising handler | OH-S4 |
| SR-4 | K and the lock discipline LD-1 … LD-9, including a lock never on a non-root object | PO-20 (f′) | OH-S2b, OH-S4 |
| SR-5 | BS-RM and the correction of the backstop literal | a change to an accepted literal | OH-S2b, OH-S0d |
| SR-6 | IL and IL′: a live rule cannot produce a pass once the holder is not `active` | the basis of the whole ladder's fail-closed behaviour | Codex security review |
| SR-7 | the sizing rules N1 … N4 are necessary conditions only, and nothing records them as bounds | R2-F2 | NT-DL-4, NT-DL-5, review |
| SR-8 | PO-17 evaluation for every image (§9.10) | not evaluated | OH-S4p |
| SR-9 | the chosen Route 3 outcome's interface contract, proof method and equivalence mapping | none exists | WP-3 … WP-6 |
| SR-10 | HB-1 and the BQ-2, BQ-3 exceptions, if any | a stated residual | Codex, Peter |
| SR-11 | X-1 stays open for the root roles until Route 3 is established | the accepted disposition | Codex |
| SR-12 **Δ3** **Δ7** | SN, the child handle and the pinning argument (SI-1 … SI-5, SN-1 … SN-10), and PO-SN (b) in particular | a root helper sends signals; a wrong number could reach an unrelated process | Codex security review, then OH-S2b and OH-S4 |
| SR-13 **Δ4** | the wait budget (WB-1 … WB-7), the reap-attempt boundary (RB-1 … RB-4, RE-1 … RE-6; **Δ5** **Δ6**), the interruption rules and state set (IS-1 … IS-10, CS-1 … CS-10) and the owner table SN-RO, including the interactive `attest` with no automatic owner | a helper's termination path runs as root; a wrong state or owner could hide a live child or license a search for it | Codex security review, then OH-S2b and OH-S4 |
| SR-14 **Δ6** | the fail-closed rule after a `reap-error` (RE-1 … RE-6, S8, `reap-unknown`) and the two branches of S1 (S1-a, S1-b, S7): that no signal can reach a possibly released PID or process-group number, whichever truth holds | a root helper's termination path; a missed branch would send a root `SIGKILL` to an unrelated process | Codex security review, then OH-S2b and OH-S4 |
| SR-15 **Δ7** | the sole-reaper invariant as the reuse defence (SI-3, SI-5, INV-27), the statement that nothing says validation detects a foreign reap or a coincidental reuse, and the pre-S0 record (GD-1 … GD-5) | a root helper signals process groups; a reuse defence that is claimed and not held could send a root `SIGKILL` to an unrelated process, and a record that invents a deadline could be read as a grace period | Codex security review, then OH-S2b and OH-S4 |

---

## Appendix A. Exact amendments needed in the one-host design

These are **proposed text changes** to the accepted, inactive
[one-host design](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md).
None is applied by this assignment. A later documentation slice (OH-S0d, §11) would
apply them, keeping the design's own D3-Rn labelling convention: each added in place
with an *(OH-S3 R2)* marker and the replaced text retained as history. The rows are
split. **Part I** is independent of the Route 3 outcome and may be applied first
(slice 2c-I). **Part II** depends on the chosen boundary and waits for it (slice
2c-II).

### Part I. Route-independent rows

| # | Location | Action |
|---|---|---|
| A-I-01 | §4.2.3 path tables | add `K = /run/freedom-blades-rp11-lock-⟨activation_id⟩/` (`root:root`, `0700`, created by AM-0, removed by CL-5b or cleared by the boot) and `K/grant.id` (`root:root`, `0600`, created by AM-1G, removed by CL-5b before K) |
| A-I-02 | §4.2.5-R2 (b), (c) | paths gain K and `grant.id`. A-2 pins gain `pk_op_ms`, `pk_call_ms`, `reap_grace_ms`, `lock_wait_ms`, `slice_ms`, `stop_timeout_s`, `bs_runtime_s`, `backstop_max`, `reserve_ms`, `act_wait_s`, `journal_max_bytes`. **Replace "the PO-11 (d) bound"** by those. **Withdraw** S's grammar `⌈λ/1,000⌉ + ⌈(P + c)/1,000⌉ + 30 … 600` and replace it by N1 … N4 as **necessary conditions** (§7.6) |
| A-I-03 | §4.2.5-R2 (d) AP-0, AM-0, AK-1, AV-1, `hold-start`; add SG-1 and AM-1G | as §8.1. AM-0's lock text ("keep the lock until the holder exits") is already replaced by R4's AR-2 and is further replaced by K. SG-1 is the holder's first act |
| A-I-04 | §4.2.5-R2 (f), the backstop literal | **replace** `--property=TimeoutStartSec=⟨S⟩` by `--property=RuntimeMaxSec=⟨S_b⟩ --property=TimeoutStopSec=⟨S⟩` (BS-RM, §7.4). BS-4 gains the `backstop_max` rule |
| A-I-05 | §4.2.5-R2 (g) HL, and its "Latency bound" paragraph; §4.2.5-R5 (g) OS-5 | **delete** "which are local operations bounded by S" and the sentence it ends, and state W-5; OS-5's "exits **while holding the lock**" becomes "appends and `fsync`s `hold-end`, closes K, then exits" |
| A-I-06 | §4.2.5-R2 (h) CL-0 … CL-7; §4.2.5-R3 (e) GP-R3 | add **CL-G** as the first act; CL-0's lock with `lock-timeout` withdrawn and degraded mode; CL-3's `igr`/`cl-g` classes; CL-4's PK/2; CL-5b removes `grant.id` and K last; CL-6's baseline recomputation is class X. **Replace** the sentence "The kernel releases the lock when a process dies (PO-20 (f))" by LD-8 and GR-1 |
| A-I-07 | §4.2.5-R2 (j), (k), (l) | add **ST-1.i**; the SP cells of the (k) matrix read "SP, *if PID 1 can spawn it* (RL-1), and IGR (RL-0) for a catchable end"; **delete** "HL ends within Δ, then SP" in the ST-3 row and "(≤ Δ)" in the row "HL detecting an end", replacing them by the class-E and class-X statement of §7.7 W-5; (l) gains RO-1 … RO-6 and CX-5 |
| A-I-08 | §4.2.5-R4 (c), (h) | **replace** "The lock is released by the kernel at every exit, including a kill (PO-20 (f))" by "CP closes K at CQ-7 and on every failure path; LD-4"; CP-6's "PO-11 (d) bound" becomes PK/2; the start-timeout rule `⌈bound/1,000⌉ + 30` becomes N1 |
| A-I-09 | §4.2.5-R5 (c), (e), (f), (g), (j), (k) | OS-1 reads the baseline under **BSP**; CQ-1 opens K; CQ-4's τ check cites SD-1; CQ-5 is PK/2 seek-not-authorized; **replace Lemmas 2 and 3** by Lemmas 2′ and 3′ (§6.6); the lock paragraph: K, LD-2 … LD-5, and the sentence "The kernel releases the lock at every process exit, including a kill" is withdrawn; the PO-21 (s) row becomes (s′) |
| A-I-10 | §4.2.5-R5 (k), §4.2.5-R6 (f), (g) | CX-4 is marked **void** (§6.8), subject to DEC-5; "SB-2, except CX-4" and the other CX-4 qualifiers are retired accordingly; CX-5 is added |
| A-I-11 | §4.3.3 baseline | the backstop's loaded properties (`RuntimeMaxSec`, `TimeoutStopSec`) and the start-timeout rule N1 are baselined |
| A-I-12 | §4.4.2a | PO-20 (f) becomes (f′) (§4.4); PO-11 (d) becomes (d′) (§7.10) |
| A-I-13 | §4.4.2b | PO-21 (c) becomes (c′) (§5.8); the (s) wording is withdrawn |
| A-I-14 | §4.4.3 citation order; §4.4.1 | add OH-S2b (§11); the PO-11 (d) citation step is removed; HF-10 and HF-11 gain K's path |
| A-I-15 **Δ4** | §4.7.4 | add the §11 rows; extend OH-S4's test list with (30) … (40) |
| A-I-16 **Δ3** | §4.2.5-R1 (f) (`pk-root/1`, replaced by PK/2: its subject "killed after each call" becomes an SN-3 send); the design's child-process wording where it names a kill or a deadline; §4.2.5-R2 (d) AK-1; the CL disarm steps | add SN-1 … SN-10, SI-1 … SI-4 and table SN-R as the helper-child signal contract; amend `pk-root/1`'s subject text; classify `systemd-run` and `systemctl stop` as *mutating* with an *unknown* effect after `error`, `interrupted` or an abandon (SN-10); **confirm, by a fixed search at OH-S0d, whether CL's by-name disarm of `⟨activation_id⟩-backstop.timer` is keyed to `backstop-intent` as well as `backstop-armed`, and amend it if not** (R3 did not re-read it); add the `children` record key and the recorded conditions of §8.5; add PO-SN (a) … (f) to the OH-S2b list. **Δ4:** add the wait-budget rules WB-1 … WB-7 and the reap attempt, the rewritten table SN-S, table SN-R rows 1 … 11, the interruption rules IS-1 … IS-9, the state set CS-1 … CS-8 and the matrix of §7.9, table SN-RO with the explicit interactive `attest` case, and optionally PO-SN (g); delete from the design any wording that gives a send, a validation or a reap attempt a time bound or says a sequence returns within g. **Δ5:** add the reap-attempt boundary RB-1 … RB-5 (§7.5a.6c) and the points T3k and T5k, redefine T3, T5, T6, CS-5 and CS-7, correct the matrix cells T0, T1 and T5, add IS-9, and, in R5, extend PO-SN (c) by a clause that **R6 moves to the evidence-only PO-SN (c′)**. **Δ6:** add the reap-error rules RE-1 … RE-6 and the handle state `reap-unknown`, the steps S1-a, S1-b, S7 and S8 of table SN-S, rows 3, 9 and 12 of table SN-R, the points T3x and T5x, the states CS-9 and CS-10, IS-10 and the corrected cells; delete from the design any wording that reads a raised reap attempt as *unreaped* or lets a signal follow one. **R4 searched the design again by fixed strings (`backstop-intent`, `backstop-armed`, `BS-2`, `BS-3`, `disarm`, `by name`) and found the disarm only in BS-2 and BS-3, performed by the backstop itself on a terminal `deact` record; a by-name disarm by CL was not matched, so the confirmation stands and widens: OH-S0d states which step disarms the timer after an `error`, `interrupted` or abandoned `systemd-run`, and amends the design if none does** **Δ7:** add **SI-5** and the explicit, load-bearing statement of SI-3 (the sole-reaper invariant), amend SN-4 by the clause that validation is a detector only, and **delete from the design any wording that says validation detects a foreign reap or a coincidental PID or process-group reuse** (W-17); add S0's entry condition (S0 only for a `running` handle, CC-31); no obligation is added to the OH-S2b list and no mandatory `start_ticks` check, pidfd or other identity mechanism is added. |
| A-I-17 **Δ4** | §4.2.5-R2 (d) HL and (h) CL-7; §4.2.5-R5 (e) CQ-7; the journals' closed `op` set | **confirm, by a fixed search at OH-S0d, which journal line marks the complete end of each helper** (`hold-end` for the holder, `run-end` for CP and CL, and for `attest` its attempt journal's `run-end`), and add the recorded condition `children-unknown {helper_role, missing_terminal_line}` to the `deact` record: a later procedure reports a lost `child` line from the missing terminal line, **never from a search for a process** (SN-9). If a helper has no such line the condition cannot be derived and the design returns to review for that helper. **Δ5:** the same holds for CS-5: a missing terminal line is all a later procedure derives, and a kernel reap with no `child` line is never recorded as a reap (IS-9). **Δ6:** the same holds for CS-9: a raised attempt with no `child` line is recorded only as `children-unknown` and never as *reaped*, *unreaped*, *gone* or *group empty* (IS-10) **Δ7:** the record of a child for which S0 never ran (a pre-S0 `reap-error`, a child that exits within c, a failed spawn, a settled handle) carries `s0_ran: false` and `grace_deadline_ms: null`, never an invented deadline (GD-1, GD-2), and the same line-and-gap rules apply to it. |

### Part II. Rows that depend on the chosen Route 3 outcome

| # | Location | Action |
|---|---|---|
| A-II-01 | §4.1.3 TR-9; add TR-6a′ | the entry's interpreter becomes `/usr/bin/python3.14 -I -S`. The root roles' trust-path rows are fixed by the outcome: **LIT-FULL**, the static images; **SSW (after §0.2)**, TR-6a′ *"the first image is `rp11-rootexec`, which writes `rp11-helper-env/1` and executes `python3.14 -I -S`"* |
| A-II-02 | §4.1.3, D3-R4 note on TR-6a | CP's program is the outcome's CP image |
| A-II-03 | §4.2.4, the verified-exec stub line | BQ-3: `/usr/bin/python3.14` with the HB-1 sentence, or the installer's replacement |
| A-II-04 | §4.2.5-R2 (e), (f), (i) | the literals take the outcome's first image (the SSW literals of §9.7 are the only fully stated form) |
| A-II-05 | §4.2.5-R4 (b); T-B1 | the unit's one added line is the outcome's `ExecStartPre=+` line, and T-B1 admits exactly it |
| A-II-06 | §4.2.5-R4 (h); §4.3.3 baseline | the `ExecStartPre` normalization (`path`, `argv`, `+`); `files` gains every installed image |
| A-II-07 | §4.4.1 | HF-10 and HF-11 gain every image path |
| A-II-08 | §4.4.2 PO-19 | the scope text of §9.8 per outcome; `/usr/bin/python3.12` becomes `/usr/bin/python3.14` for the entry |
| A-II-09 | §4.5 | the rebuild produces one image per source file; `expected.sha256` gains four rows per added image; the independent bindings of §9.11 apply to each |
| A-II-10 | §4.7.1 M-5 | entry interpreter `/usr/bin/python3.14`; every installed image is a root-owned `0755` regular file pinned by digest. D-1's text is unchanged |
| A-II-11 | §4.6.2-R1 RB-1 | every installed image is a member of tree **L**; K and `grant.id` are not RB-1 objects |
| A-II-12 | §4.2.4-R1 PT-8 | "(Python 3.12 has no wrapper)" becomes "CPython 3.14.4 has no `os` wrapper [R2 §10.5]" for entry-side Python; a static image calls `renameat2` directly |
| A-II-13 | C11 `:688`, `:903–904`; D2 `:436`, `:1256`, `:1258`, `:1567–1568` | the dated amendment notes of §9.6.2 (A10, B5) |

## Appendix B. Exact amendments needed in the operational draft

The draft, [`phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`](phase-5-0-p5-r5-operational-evidence-authorization-prompt.md),
is a **draft that authorizes nothing**, and this assignment does not edit it. These
are the **content obligations** for the OH-S3 successor (OH-S3S), by the draft's own
section and row identifiers. The final bytes are composed under that slice's
authority. Each new value follows the draft's typed-placeholder rule of §0 (no value
is filled by the operator's judgement).

| # | Draft location | Content to add or change |
|---|---|---|
| B-01 | §4.5 Maintainer inputs | new inputs, supplied only in the A-2 record: `MI.pk_op_ms`, `MI.pk_call_ms`, `MI.reap_grace_ms`, `MI.lock_wait_ms`, `MI.slice_ms`, `MI.stop_timeout_s`, `MI.bs_runtime_s`, `MI.backstop_period_s`, `MI.backstop_max`, `MI.reserve_ms`, `MI.act_wait_s`, `MI.journal_max_bytes`, the existing lease parameters, `MI.image_sha256[]` (one per root-procedure image the outcome installs), `MI.launcher_sha256`, `MI.activation_id` |
| B-02 | §4.1 row A-2 | the A-2 record also quotes: N1 … N4 as evaluated **necessary conditions**, the route (iii-a) pre-`stop` condition OC-1 … OC-3, the sentence *"the consume step is part of the start; an activation admits one start attempt while every act stays within the pass's authorization"*, and the sentence *"no elapsed time is claimed for any class-X operation"* |
| B-03 | §4.2 Authorization matrix | separate rows: `AP-2` (the holder, with its `act_wait_s`), the operator's single `start` (only after `hold-start`), the executor's route (iii-a) `stop` (only under OC-1 … OC-3), the automatic CL triggers (`stop-post`, `backstop`) and `attest` |
| B-04 | §6 Pass A (before Band A1) | the activation chain as **admission rows**: AP-0's conditions (including drift of every image digest and the §7.6 arithmetic), AP-1, AP-2, and the evidence each returns. The pass's own acts remain the entry's, started by one `start` |
| B-05 | §9.5.3 Interruption (C-15) | route (iii-a) only while OC-1 … OC-3 hold, with its pre-`stop` read recorded as operational evidence; **never** while the unit is `activating`; a hung consume step ended only by the start timeout (class M), with CP's own elapsed time **not claimed**; a failed consume step is **not** a pass |
| B-06 | §11 Stop conditions | add `lock-object`, `capture-baseline-unstable`, `grant-not-seen`, `stop-control-unconfirmed`, `act-unconfirmed`, `invalid-journal`, `consume-failed {CQ-5}` and INVALID RUN on any drift of the §9.11 list. **Stop, record, never repair** applies |
| B-07 | §13.1 Intended changes and §13.2 survey | add K, `grant.id`, tree **P**, the rule (G1 → G3), the claim and consume evidence, the transient units and every record; the final survey adds K absent and the rule absent, each with PK *not authorized* from PK/2 |
| B-08 | §14 Handback template | add `lock`, `grant_identity`, `pk` (with `reap_grace_ms`, `abandoned` and `signals`), `release`, `capture`, `helper`, `children` (**Δ3**; **Δ4:** with `grace_deadline_ms`, `late` and `waits_skipped` per child, and the condition `children-unknown {helper_role, missing_terminal_line}`) and `params` with `sizing` (§8.5), and the journals' digests and lengths (OH-D-9). **Observed** elapsed times are recorded as observations and never as bounds **Δ7:** `children` entries also carry `s0_ran` (boolean) and `grace_deadline_ms`, an integer iff `s0_ran` and `null` otherwise, never omitted (GD-2); `outcome` may be `reap-error`, only when `s0_ran` is false. |
| B-09 | §3 Binding decisions | add rows for OH-D-10 (A) with OS-6 and, once recorded, for the Route 3 decision (WP-9) or the §0.2 change that precedes it |
| B-10 | `PIN.interpreter` (`:342`), `OP.interpreter_version` (`:407`) | **unchanged**: `venv-web` CPython 3.12 is Role F and runs the suite and Pass A acts A1-S1 and A1-13. State this explicitly so it is not read as the entry interpreter |
| B-11 | any sentence of the draft that states or implies a cleanup, consume or activation time | **none was found by the fixed-string search of this assignment** (bound, latency, timeout, within S, TimeoutStop, RuntimeMax); OH-S3S repeats the search and rejects any addition that does |
| B-12 | §6 Pass A, the executor's wait | the executor waits at most `act_wait_s` for the `act` record or the holder's end, then reports HARD STOP `act-unconfirmed`, acting on nothing |
| B-13 **Δ3** **Δ4** | §11 Stop conditions (§11.2, §11.3) and §14 Handback template | a child left behind by its helper (abandoned, unsignalled, indeterminate or unmade; any of CS-1 … CS-10, **Δ5:** CS-5 included, a direct child that the kernel reaped and no line records, of which the executor reports only `children-unknown` and states nothing about the child or its group, IS-9; **Δ6:** CS-9 and CS-10 included, a child whose reap attempt raised, so that its truth is unknown: the executor reports `children-unknown` or the line's `reap_unknown`, states nothing about whether the child is reaped, alive or gone or about its group, signals nothing and searches for nothing, IS-10) is a **recorded condition**, never a stop condition of its own and never an invitation to act: the executor reports `children` from the record, or `children-unknown` where the record is missing, does not look for the process, does not signal it, and does not repeat the step (stop, record, never repair; SN-9; no-retry rule §11.3). **For the interactive `attest` there is no automatic owner**: the executor reports the record and the missing terminal line, claims no signal on behalf of the end of the session, and treats the boot as a separate event that proves nothing about any child. The handback states that no send result is evidence (INV-20), that a recorded reap status concerns the direct child only (IS-3), and that no elapsed time is a bound (WB-6) **Δ7:** a child whose entry has `s0_ran: false` and `grace_deadline_ms: null` never started a grace period; the executor reads no deadline, no elapsed time and no send into it, and reports the entry as recorded. |

## Appendix C. Identifier cross-check against the accepted R2 record, and against R1

### C.1 Returned items and MF identifiers against the accepted R2 record

Every returned item and every MF identifier named in the prompt appears in the
accepted R2 record at the location shown.

| Item | R2 location | R2 verdict | Where this proposal addresses it |
|---|---|---|---|
| PO-20 (f) | §7 table, §R2-6 | refuted | §4 |
| PO-21 (c) | §8 table, §R2-6 | refuted | §5 |
| PO-21 (s) | §8 table, §R2-6 | refuted | §6 |
| PO-11 (d) | §6.4, §R2-6 | not established | §7 |
| PO-12, AS-8 | §10.4, §R2-6 | refuted | §9 |
| PO-12′ | §10.4, §R2-6 | source-established; binding needs MF-4 | §9.8 |
| PO-19 | §11, §R2-6 | not established (MF-1, MF-2) | §9.8 |
| PO-17 | §12.9, §R2-6 | not evaluated | §9.10 |
| MF-1 … MF-8 | §14.3 | open | §10 |
| X-1 | §15.4 | cross-cutting finding | §9.1, §13.1 |

### C.2 R1 identifiers: carried, renamed, withdrawn

| R1 identifier | In this proposal |
|---|---|
| LD-1 … LD-9, GR-1, PO-20 (f′) | carried; LD-1 gains GI-1; LD-3 (d), LD-5, LD-6 corrected (§4) |
| RL-0 … RL-5, IL, RO-1 … RO-3, PO-21 (c′), ALT-SENT | carried; the latency column withdrawn; IL′, RO-4 … RO-6, GRR, CL-G added (§5) |
| IGR | carried and rewritten: one site, latch, flag-only handlers, GRR, no time claim (§5.7, §7.8) |
| SD-1, BSP, SD-2, SD-3, PO-21 (s′), CX-4 void, CX-5 | carried unchanged (§6) |
| PK/2, `pk_op_ms`, `pk_call_ms`, PO-11 (d′) | carried; `reap_grace_ms` and the abandon rule added (§7.5, §7.10) |
| the R1 budget table and the S grammar | **withdrawn** (§7.7 W-1, W-6, W-7) |
| HS-1 … HS-6 | carried (§7.5), no longer tied to a static first image |
| RT3-A, RX (`rp11-rootexec`) | renamed **SSW** and described as a scope-change alternative (§9.7) |
| RT3-B | renamed **SCDC** |
| RT3-C | folded into **LIT-FULL** and **LIT-DR1** (§9.4) |
| RT3-D, RT3-E, RT3-F | rejected, with their R1 reasons (§9.4) |
| RT3-Z | renamed **ACCEPT-X1** |
| HB-1 | carried; depends on BQ-3 |
| RR-1 … RR-11 | replaced by SR-1 … SR-11 (§14.2) |
| NT-LD, NT-RL, NT-SD, NT-PK, NT-HS | carried, corrected where they asserted a bound (§§4, 5, 7) |
| NT-RX-1 … 9 | replaced by NT-RH-1 … 5, NT-LR-1, 2 and NT-SSW-1 … 3 (§9.14) |
| INV-1 … INV-15 | carried; INV-4, INV-7, INV-8, INV-11 corrected; INV-16 … INV-18 added (§8.6) |
| DEC-1 (Route 3) | **withdrawn** (§12.2) |
| DEC-2, DEC-3, DEC-4, DEC-5, DEC-6 | DEC-1, DEC-2 (with BS-RM), DEC-3 (with GI-1), DEC-4, DEC-5 (§12.1). DEC-6 is new (signal and removal discipline) |
| Appendix A rows A-01 … A-30 | split into Part I (A-I-01 … 15, and in R3 A-I-16, in R4 A-I-17) and Part II (A-II-01 … 13) |
| Appendix B rows B-01 … B-10 | carried and extended; B-11 and B-12 new |
| OH-S0d, OH-S2b, OH-S3S, OH-S4, OH-S4p, H-0M1, H-0M2, G-0 … G-7 | carried; G-1 split into G-1a and G-1b; 2R and 2R′ added (§11) |
| SN, SI, CH, PO-SN, CC, SN-I, SN-R, SN-S, SN-RO, IM-S (T0 … T5), SG-9, RO-7, INV-19 … 21, NT-SN-1 … 18, W-12, W-13, A-I-16, B-13 | **new in R3** (§0.5, §7.5a); the OH-S3 R2 identifiers are otherwise carried unchanged |
| WB-1 … WB-7, the reap attempt, IS-1 … IS-8, CS-1 … CS-8, IM-S (T0 … T7, redefined), PO-SN (g), CC-8 … CC-15, W-14, INV-22, INV-23, NT-WB-1 … 12, NT-IS-1 … 15, A-I-17, SR-13, Q16, Q17; SN-S, SN-R, SN-RO, SN-6, SN-8, RO-7 and rows 19 and 20 of §5.5 **rewritten or amended** | **new or changed in R4** (§0.6, §7.5a.6a, §7.9). **R3's T0 … T5 are withdrawn as a set**; no R4 identifier reuses a R3 meaning. All R3 identifiers not listed are carried unchanged |
| RB-1 … RB-5, RA-0 … RA-4, T3k, T5k, IS-9, CC-16 … CC-22, W-15, NT-WB-5a, NT-WB-5b, NT-IS-16, NT-IS-17, Q18, Q19; IM-S (T3, T5, T6 redefined; E1 rewritten), CS-5, CS-7, the matrix cells T0, T1 and T5, NT-IS-1, -6, -8, -11, -14, the case table of §7.5a.6b, INV-18, -20, -23, SI-3, SN-7, rows 19 and 20 of §5.5, RO-7, SR-13 and PO-SN (c) **rewritten or amended** | **new or changed in R5** (§0.7, §7.5a.6c, §7.9). No R5 identifier reuses an R4 meaning, and **R4's T3, T5 and T6 are redefined, not withdrawn**; all R4 identifiers not listed are carried unchanged |
| RE-1 … RE-6, `reap-unknown`, RA-E, T3x, T5x, S1-a, S1-b, S7, S8, CS-9, CS-10, IS-10, CC-23 … CC-30, W-16, INV-24, INV-25, NT-RE-1 … 12, NT-NS-1 … 8, PO-SN (c′), Q20, Q21, SR-14; SI-3, SI-4, SN-4, SN-6, SN-7, SN-8, table SN-R rows 1 … 5, 7 … 9 and 12, table SN-S (S1, S3 … S6 amended; S7 and S8 added), WB-5, WB-7, RB-1 … RB-5 (RB-5 replaced), row 3g, IM-S (T0, T1, T6, T7, the outcome `u`, the matrix, E1, the observer bullet), IS-9, Q17, Q18, SR-13, NT-SN-5 … 7, -9, -12, -18, NT-WB-11, NT-IS-1, -5, -6, -11, -13, -14, -16, -17, INV-18, -20, -21, -23 and PO-SN (c) **rewritten or amended** | **new or changed in R6** (§0.8, §7.5a.6d, §7.9). No R6 identifier reuses an R5 meaning; **R5's CC-18 cell correction (T0 and T1 `u` admitting CS-5) is withdrawn (W-16)**; all R5 identifiers not listed are carried unchanged |
| GD-1 … GD-5, `s0_ran`, SI-5, CC-31 … CC-34, W-17, W-18, INV-26, INV-27, NT-GD-1 … 4, Q22 … Q24, SR-15; SI-2, SI-3, SN-4, SN-6, WB-1, RE-4, RE-5, table SN-S (S0's entry check, S1-a's clock clause, S8), table SN-R row 12, the case table of §7.5a.6b (one row), §7.5a.9, §8.5, INV-19, INV-22, NT-SN-6, -9, -12, NT-RE-7, -11, -12, NT-WB-11, -12, NT-NS-1 … 3, NT-SN-5, the CH row of §3, CC-30 (marked superseded), Q15, Q21, SR-12, A-I-16, A-I-17, B-08 and B-13 **rewritten or amended** | **new or changed in R7** (§0.9, §7.5a.3, §7.5a.6e). No R7 identifier reuses an R6 meaning; **R6's CC-30 claim about validation and a foreign reap, and R6's unconditional `grace_deadline_ms` and "one grace deadline per child", are withdrawn (W-17, W-18)**; all R6 identifiers not listed are carried unchanged |

## Appendix D. Remediation map

| Finding and item | Closed in |
|---|---|
| R2-F1 (1) preserve R1 unchanged and state that RT3-A did not meet the boundary | the document header; §0.1; §9.1 |
| R2-F1 (2) restore the accepted Route 3 meaning throughout | §0.1; §9.1; §9.2 (LR-1 … LR-6); the whole of §9 |
| R2-F1 (3) a decision-ready concrete design only if evidence suffices | §9.3 (it does not) |
| R2-F1 (4) otherwise exact bounded alternatives, the work needed, and the hard stop | §9.4; §9.5; the terminal state of the header and §0.4 |
| R2-F1 (5) RT3-A under a new name, as a scope-change alternative, with the baseline decision needed | §9.4; §9.7 |
| R2-F1 (6) no scope change inside DEC-1; §0.2 change control | §12.1 (DEC-1 withdrawn and replaced); §12.2 (BC-1 … BC-5); §9.7 |
| R2-F1 (7) re-evaluate Role A–H, PO-12′, PO-19, MF-1 … MF-8, OH-S4 / OH-S4p, the rebuild chain, PO-17, the surface comparison and the successor order | §9.6; §9.8; §10; §9.10; §9.11; §9.13; §11 |
| R2-F1 (8) root-owned dynamic inputs are still inputs | §9.9; §9.8 |
| R2-F2 (1) inventory every blocking operation | §7.3, **completed in R3 by rows 3a … 3f and §7.5a** (the signal-sending operation that the OH-S3 R2 proposal left out) |
| R2-F2 (2) enforced versus merely expected | §7.2 (E, M, C, X); §7.3 |
| R2-F2 (3) no bound for kernel or filesystem work from a fixed margin | §7.1; §7.6; §7.7 |
| R2-F2 (4) a deadline with a fail-closed consequence, or withdraw and state termination and recovery | §7.3; §7.4; §7.7 (withdrawals); §7.9 |
| R2-F2 (5) interruption of CL at the stop timeout, mapped to a state and a next owner | §7.9, IM-L (L0 … L9); IM-I; IM-C; IM-B; §8.3 |
| R2-F2 (6) when the holder installs handlers relative to AM-2; no reliance on a `finally` completing in time | §7.8 (SG-1 … SG-8); §5.4 (IL, IL′) |
| R2-F2 (7) a signal during IGR; re-entry; a second signal | §5.7 (IGR-0); §7.8 (SG-2, SG-5, SG-7); §5.5 rows 16, 17; §7.9 IM-I |
| R2-F2 (8) correct every affected formula, table, invariant, test, Appendix A and B item, and parameter | §§4.7 … 4.10; §5.3; §5.7; §7.6; §8; Appendices A, B; §12.1 |
| R2-F2 (9) retain PO-11 (d′) | §7.10 |
| **R3-F1 (1)** preserve the OH-S3 R2 proposal unchanged; create a self-contained cumulative R3 proposal | the document header; §0.5 (every changed section listed and marked **Δ3**) |
| **R3-F1 (2)** add every signal-sending operation of `spawn()` or another helper to §7.3: the initial group-directed termination signal, the escalation to `SIGKILL`, any signal used by cleanup or recovery | §7.5a.1 table SN-I (SN-I-1 … SN-I-4); §7.3 rows 3a, 3b, 3c, 3d |
| **R3-F1 (3)** distinguish the local system call from PID 1's class-M delivery; give the local operation the correct class without inventing an elapsed-time bound | §7.2 (paragraph *Local sends and PID 1's sends*); §7.3 rows 3a … 3f; §7.4; §7.5a.1; §7.5a.2 (class **X** for the call, **C** for the attempts) |
| **R3-F1 (4)** results for success, `ESRCH`/absent target, permission or validation failure and every other error; no error authorizes a pass, converts *unconfirmed* into confirmation, or is hidden | §7.5a.5 table SN-R (rows 1 … 10); SN-7; INV-20 |
| **R3-F1 (5)** validate and retain the intended process-group identity against PID or group reuse; where repository evidence is insufficient define the proof obligation, not a kernel guarantee | §7.5a.3 (CH, SI-1 … SI-4); SN-2, SN-4; §7.5a.8 PO-SN (a) … (f); §13.2 |
| **R3-F1 (6)** what the helper does after a failed or indeterminate send: reap wait, abandonment, record, next recovery owner, continuing only with the existing fail-closed result | §7.5a.6 table SN-S; SN-6, SN-8, SN-9, SN-10; §7.5a.7 table SN-RO; §7.5a.9; §7.9 IM-S |
| **R3-F1 (7)** propagate through class E, HS-5, PK/2, SG-4, the terminal-cause and interruption maps, evidence fields, invariants, residuals, Appendices A and B | §7.2 (E row); §7.5 (HS-3, HS-5, PK/2); §7.8 (SG-3, SG-4, SG-9); §5.5 rows 19, 20; §7.9 (IM-S, L4); §8.5; §8.6 (INV-12, -16, -17, -19 … 21); §5.6 RO-7; §13.1; §13.2; Appendix A (A-I-15, A-I-16); Appendix B (B-08, B-13); §9.3, §9.5 |
| **R3-F1 (8)** negative tests: successful send, `ESRCH`, other send errors, an already-exited child, target-identity mismatch and reuse simulation, failure of `SIGTERM` then the escalation decision, failure of `SIGKILL`, the resulting reap and abandon record | §7.12: NT-SN-1 (success), -3 (`ESRCH`), -4 (other errors), -5 (already exited), -6 (identity mismatch and reuse), -7 (`SIGTERM` failure and escalation), -8 (`SIGKILL` failure, reap and abandon), -9 (record), and -2, -10 … 18; NT-DL-1, -2, -3, NT-SG-3, NT-HS-3, NT-LD-9, NT-RL-8 amended |
| **R3-F1 (9)** the remediation map shows how R3-F1 and the previously incomplete R2-F2 item 1 are closed | this appendix: the rows above, and the amended **R2-F2 (1)** row |
| **R4-F1 (1)** one absolute `t_g` set before the first send; cap every S3 and S5 wait by the remaining interval; no new grace period after a send, validation, poll, error or signal receipt | §7.5a.6 table SN-S (S0, S3, S5); §7.5a.6a WB-1, WB-2, WB-7; SN-6; HS-5; §7.3 rows 2, 3, 7 |
| **R4-F1 (2)** a send or validation returning at or after `t_g` skips every later timed wait; the at-most-once identity-validated escalation of S4 is preserved and not presented as completion within g | §7.5a.6a WB-3, WB-4; table SN-S (S3, S4); table SN-R rows 1, 10; §7.3 rows 3a, 3b |
| **R4-F1 (3)** boundary ordering for a child already reaped, one that exits during a send and one still unreaped at the deadline; a non-blocking reap attempt is class X, never a timed wait | §7.5a.6a WB-5 (a) … (d); §7.3 row 3g; SN-8; table SN-S (S3, S5, S6) |
| **R4-F1 (4)** the wait budget stated separately from elapsed procedure time; no class-X operation acquires a bound; no sizing rule becomes a completion guarantee | §7.5a.6a WB-6; §7.2 (E row); §7.5a.10; §7.6 (the g row, the R3 note, W_show and W_series); W-14 |
| **R4-F1 (5)** every dependent sentence and test: CC-1, CC-2, SN-R, SN-S, SN-6, HS-5, PK/2, SG-4, the parameter notes, invariants and amendment tables; no unconditional claim of return within g or of a signal only after a full slice | §0.5 CC-1, CC-2 (amended in place, **Δ4**); §0.6 CC-8, CC-9, CC-10, CC-11; §7.3 rows 2, 3, 3a, 3b, 3e, 3g, 7, 14; §7.5 (HS-5, PK/2); §7.5a.4 (SN-6, SN-7, SN-8); §7.5a.5; §7.5a.6; §7.6; §7.7 W-14; §7.8 SG-4; §7.11; §8.6 INV-16, INV-22; Appendix A (A-I-16); Appendix B (B-08, B-13) |
| **R4-F1 (6)** fake-clock cases: a send under, at and over g; less than one slice left; a slow validation; an expired deadline before S3 and S5; successful and failed sends; a child reaped at the boundary; no timed wait after `t_g`; scheduled waiting within the budget (paper only) | §7.12 NT-WB-1 … 12 (and the case table of §7.5a.6b); NT-DL-1, NT-SG-3, NT-HS-3, NT-PK-1, NT-SN-2, -4, -6, -8, -16, -17 amended; §8.7 (37) |
| **R4-F2 (1)** rewrite IM-S for successful, failed, indeterminate and unmade sends; "sent" means only the kernel result; only a recorded reap status proves reaping; nothing is inferred about the group | §7.9 IM-S: IS-1 … IS-8, the outcome codes `u`, `i`, `x`, `s`, `e`, `f`, the state set CS-1 … CS-8; §7.5a.5 row 11; SN-7 |
| **R4-F2 (2)** the cross-product of interruption point and send outcome, with validation failure, `ESRCH`, other errors, partial escalation, death during a send, reaping and abandonment | §7.9 the point table T0 … T7 and the matrix; "Reading the matrix" |
| **R4-F2 (3)** correct every row reference; separate sends already attempted from the absence of further sends by the ended helper; remove the absolute "unsignalled by anyone" | §7.9 (the CS table, IS-4); §7.7 W-14 |
| **R4-F2 (4)** recovery ownership by enclosing procedure (holder, CP, stop-post, backstop service, interactive `attest`) with SN-RO's cgroup obligations; `attest` keeps no automatic owner; the boot is a separate event | §7.5a.7 table SN-RO (rewritten); §7.9 the owner and record table; IS-6, IS-7; PO-SN (e), (g) |
| **R4-F2 (5)** propagate to terminal-cause rows 19 and 20, RO-7, records and gaps, invariants, review focus and Appendices A and B; keep mutating-child effect `unknown`, the fail-closed result, no retry and no process hunting | §5.5 rows 19, 20; §5.6 RO-7; §7.5a.9 (`children-unknown`); §8.5; §8.6 INV-18, -20, -21, -23; §13.1, §13.2; §14.1 Q5, Q16, Q17; §14.2 SR-13; Appendix A (A-I-16, A-I-17); Appendix B (B-08, B-13); IS-8 |
| **R4-F2 (6)** stepped cases interrupting each IM-S point after success, `ESRCH`, another send error, identity rejection and an unmade send, with a child alive, exited but unreaped, reaped or abandoned; the interactive `attest`; lost child records (paper only) | §7.12 NT-IS-1 … 15; NT-SN-9 amended; §8.7 (38) |
| **R5-F1 (1)** define the exact interruption boundary of a reap attempt, including the kernel reap before the handle state or the `child` line records it | §7.5a.6c table RA-0 … RA-4 and RB-1 … RB-5; §3 (*kernel reap*, *reap attempt*); WB-5 (pointer) |
| **R5-F1 (2)** make T3, T5 and T6 mutually consistent; no interruption inside an attempt is T6 | §7.9 point list (T3, T3k, T5, T5k, T6, and the *Before T0* paragraph); RB-4; CC-16 |
| **R5-F1 (3)** extend the state set and matrix so every reachable interruption has a state that permits the true direct-child condition; no inference from a send result | §7.9 CS-5, CS-7 (and the sentence after the state table); the matrix rows T3k and T5k and the corrected cells T0, T1, T5; IS-5; CC-17, CC-18, CC-19 |
| **R5-F1 (4)** preserve the conservative observer rule | §7.9 IS-9 and the *Truth versus record* bullet; §7.5a.9; SN-7; INV-20; CC-21 |
| **R5-F1 (5)** correct E1, the matrix narrative, INV-18, -20, -23, terminal-state and record text, review questions, Appendix A and B rows and every reference | §7.9 (E1 rewritten, *Corrected cells*, *Reading the matrix*); §5.5 rows 19, 20; §5.6 RO-7; §7.3 row 3g; §7.5a.3 SI-3; §7.5a.4 SN-7; §7.5a.8 PO-SN (c); §7.5a.9; §7.7 W-15; §8.5; §8.6 INV-18, -20, -23; §8.7; §13.1; §13.2; §14.1 Q17, Q18; §14.2 SR-13; Appendix A (A-I-16, A-I-17); Appendix B (B-13); Appendix C.2 |
| **R5-F1 (6)** correct NT-IS-1 and NT-IS-8; add cases for before the call, inside the call before a reap, after the kernel reap before the handle update, after the handle update before the durable line, and after the durable line; every dash unreachable | §7.12 NT-IS-1, -6, -8, -11, -14 amended; NT-IS-16, NT-IS-17 added; §8.7 (38) |
| **R5-F2 (1)** split NT-WB-5 into slow-S1 and slow-S4 cases | §7.12 NT-WB-5a, NT-WB-5b; §7.5a.6b (two rows) |
| **R5-F2 (2)** slow S1: the S3 and S5 waits and the `late` fields from the actual clock | §7.12 NT-WB-5a; §7.5a.6b |
| **R5-F2 (3)** slow S4: explicit costs for S1, `SIGTERM` and S3; S3's capped wait allowed before `t_g`; `SIGTERM` late only if its return is at or after `t_g`; no S5 wait; `SIGKILL` late | §7.12 NT-WB-5b; §7.5a.6b |
| **R5-F2 (4)** keep the shared assertions | §7.12 NT-WB-5a and NT-WB-5b (the *Shared* sentence) |
| **R5-F2 (5)** propagate to the case table, the remediation map, the handback summary and every cross-reference | §7.5a.6b; §0.2 map rows; §0.7 (CC-22); §8.7 (37); this appendix; the handback §2 |
| **R6-F1 (1)** fail closed after **any** `reap-error`: no later signal to that child, S4's `SIGKILL` included; no retry, alternate primitive or process search | §7.5a.6d RE-1; §7.5a.6 table SN-S (S3, S4, S5, S8); §7.5a.6a WB-7 (amended); §7.5a.5 table SN-R row 12; §7.5a.3 SI-4; INV-24; CC-27 |
| **R6-F1 (2)** a state that permits either truth and is not labelled `reaped`, `unreaped` or `abandoned` as a fact; the handle and sequence transition | §7.5a.3 (the handle's state set); §7.5a.6d RE-2, RE-3; §7.5a.6c RA-E; §7.9 CS-9, CS-10, T3x, T5x, IS-10; the matrix; CC-26 |
| **R6-F1 (3)** keep the handle and `Popen`; record `reap-error`, the send suppression and `effect: "unknown"`; the enclosing fail-closed result; owner and observer rules unchanged; nothing acts on or searches for the child | §7.5a.6d RE-3, RE-5; §7.5a.9; table SN-RO (unchanged); §7.9 IS-6, IS-7, IS-9, IS-10; SN-9; SN-10 |
| **R6-F1 (4)** correct row 3g, table SN-S, SN-4, SN-7, SN-8, RB-5, the RA and point mapping, the child-state set, every IM-S cell and dash, records, invariants, residuals, review questions, security rows, Appendix A and B rows and every reference; keep the at-most-once send rule and the one absolute `t_g`; no new wait or grace | §7.3 row 3g; §7.5a.4 SN-4, SN-6, SN-7, SN-8; §7.5a.6 table SN-S; §7.5a.6c (RA-E, RB-1 … RB-5); §7.5a.6d RE-4; §7.5a.9; §7.7 W-16; §7.9; §5.5 rows 19, 20; §5.6 RO-7; §8.5; §8.6 INV-18, -20, -21, -23, -24; §13.1, §13.2; §14.1 Q17, Q18; §14.2 SR-13, SR-14; Appendices A (A-I-16, A-I-17), B (B-13), C.2; §0.8 (CC-26 … CC-29) |
| **R6-F1 (5)** rephrase PO-SN (c): the citation stays useful about CPython but is no safety precondition; either answer leaves the design safe; AP-0 cannot pass an unsafe branch | §7.5a.8 PO-SN (c) narrowed and (c′) added; §7.5a.6d RE-6; §8.1 AP-0; §7.12 NT-SN-18, NT-RE-12; §13.2; CC-28 |
| **R6-F1 (6)** paper-only cases: `reap-error` before and after a kernel reap at S3, S5 and the final attempt; zero later sends, no reuse exposure, indeterminate truth, fail-closed result, correct record or gap, no later search or retry | §7.12 NT-RE-1 … 12; §8.7 (39) |
| **R6-F2 (1)** split S1: `not-sent(reaped)` or `not-sent(abandoned)` makes no call, begins no wait and ends through the settled-state record path; `not-sent(identity-mismatch)` or `not-sent(identity-unverifiable)` makes no send and goes to the capped S5 path | §7.5a.6 table SN-S (S1-a, S1-b, S7); §7.5a.5 rows 3, 7, 8, 9; SN-4; SI-4; CC-24, CC-25 |
| **R6-F2 (2)** the same distinction wherever a send is validated, the PK-only S4 path included, with no send after any `not-sent` | §7.5a.6 table SN-S S4; SN-4; INV-25; §7.12 NT-NS-6, NT-NS-7 |
| **R6-F2 (3)** make table SN-R, table SN-S, WB-5, the outcome definition, T0/T1/T5/T6/T7, every affected cell and dash, NT-SN-5/6/7, NT-IS-1/5/6/16 and the narrative consistent; state when the settled-state decision and the durable record occur for a handle already reaped by an enclosing poll; no interruption at T0/T1 and T7 at once | §7.5a.6a WB-5 (a); §7.5a.6c RB-2, RB-4; §7.9 (the point list, *Before T0*, the outcome `u`, the matrix, *Corrected cells*); §7.12 NT-SN-5 … 7, -12, NT-IS-1, -5, -6, -16; CC-23, CC-30; §0.1 |
| **R6-F2 (4)** a focused paper-only case stepping an interruption before, during and after the S1 branch for each `not-sent` subtype; every dash claimed unreachable is unreachable | §7.12 NT-NS-1 … 8 (NT-NS-8 the cell and dash audit); §7.9 *Corrected cells*; §8.7 (40) |
| **R7-F1 (1)** one explicit representation for a child whose enclosing-wait poll raises before S0: `grace_deadline_ms` null; no invented deadline, no S0, no clock read for the record, no grace period | §7.5a.6e GD-1, GD-2, GD-3 and the step-by-step path; §7.5a.9; §8.5; table SN-R row 12 and table SN-S S8 (clauses); RE-4; CC-32 |
| **R7-F1 (2)** `t_g` exists exactly when S0 ran; once it exists it is read once and never moved, extended or restarted; a pre-S0 `reap-error` reads it zero times | §7.5a.6e GD-1, GD-4; table SN-S S0 (entry check); SN-6; WB-1; INV-22 (amended); INV-26; CC-31 |
| **R7-F1 (3)** correct §7.5a.9, §8.5, INV-22, NT-SN-9, NT-RE-7, NT-RE-11, NT-RE-12 and every dependent record, schema, Appendix A and B and handback statement; make the distinction machine-checkable | §7.5a.9; §8.5; §8.6 INV-22, INV-26; §7.12 NT-SN-9, NT-RE-7, -11, -12, NT-WB-11, -12, NT-NS-1 … 3, NT-SN-5; GD-2's one-line schema check and its implications; Appendix A (A-I-17); Appendix B (B-08, B-13); the handback §2 and §9 |
| **R7-F1 (4)** a focused paper-only case: enclosing poll raises before S0; no `t_g` read; `grace_deadline_ms` absent or null; zero send, wait, further poll or search; S8 and S7 record `reap-unknown`; the enclosing operation fails closed | §7.12 NT-GD-1 (with NT-RE-7), NT-GD-2 … 4; the case table of §7.5a.6b (the row *a `reap-error` before S0*); §8.7 (41) |
| **R7-F2 (1)** withdraw CC-30's universal claim that validation detects every foreign reap and reuse and that the injected state reaches S1-b | §0.8 CC-30 (marked superseded); §0.9 CC-33; §7.7 W-17; §7.12 NT-SN-12 |
| **R7-F2 (2)** keep the sole-reaper contract explicit and load-bearing, its version-bound obligations and the AP-0 refusal unchanged | §7.5a.3 SI-3 (amended), SG-3 (unchanged); §7.5a.8 PO-SN (b), (c), (f) and the AP-0 sentence (unchanged); §8.1 AP-0; INV-27 |
| **R7-F2 (3)** an injected foreign reap is a deliberate violation of a design precondition, not a supported state; NT-SN-12 proves the structural properties; any detector exercise is labelled non-universal with a deliberately mismatching fake identity | §7.5a.3 SI-5; §7.12 NT-SN-12 (a) … (e), NT-SN-6 (b), (c) labelled; CC-34 |
| **R7-F2 (4)** the honest consequence: after the invariant is violated, no reuse-safety claim from SN-4 alone; no new identity mechanism | SI-5 (a) … (e); SI-2 and SN-4 (clauses); §7.5a.8 PO-SN (d) (optional, unchanged) |
| **R7-F2 (5)** correct CC-30, NT-SN-12, the reuse narrative, invariants, review questions, security rows and remediation map | §0.8 CC-30; §0.1 (R7-F2 bullet); §3 (SI-5); §7.7 W-17; §7.12; §8.6 INV-19, INV-27; §14.1 Q15, Q21, Q23; §14.2 SR-12, SR-15; this appendix; Appendix A (A-I-16) |
| **R7-F3 (1)** add `reap-unknown` to the CH vocabulary state set | §3 (the *child handle (CH)* row) |
| **R7-F3 (2)** check every current, non-historical definition of the handle state set for the same omission; historical descriptions untouched | §0.9 (*Handle-state vocabulary check*): §3 CH row corrected; every other current definition already lists four states or a stated subset |

---

## Closing statement

This proposal ends at **`HARD STOP: concrete Route 3 not established`**. The repaired
activation design (§§2 … 8, including the signal-sending contract of §7.5a, its wait
budget WB-1 … WB-7, the interruption map of §7.9 **Δ4**, the reap-attempt boundary of §7.5a.6c **Δ5** the reap-error rules of §7.5a.6d **Δ6**, the grace deadline that exists exactly when S0 ran, §7.5a.6e **Δ7**, and the sole-reaper contract with its stated limit, SI-3 and SI-5 **Δ7**) is
complete and awaits independent review. The Route 3
question is returned as an exact set of alternatives (§9.4) and the exact work that
would make a literal Route 3 decision-ready (§9.5). No scope change is made or
requested, no successor is authorized, and R1, the OH-S3 R2 proposal, the R3 proposal, the R4
proposal, the R5 proposal and the R6 proposal are unchanged.
