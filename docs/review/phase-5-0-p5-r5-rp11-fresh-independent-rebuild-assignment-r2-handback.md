# R2 remediation handback — fresh R-5 assignment timestamp contract

Work ID: `C-P5.0-R5-RP11-FRESH-A1-R2`

Date: 2026-10-02

Drafting-remediation assignee: Claude, appointed by Peter Duscha, who accepted
this work ID in this session

Controlling prompt:
[`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r2-claude-prompt.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r2-claude-prompt.md)
(SHA-256 `0efbf17ef0144b884faa7972d84429dc92dc0ec9abc13f82147ee855a1dda57c`)

Finding source:
[`project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r1.md`](project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r1.md)
(SHA-256 `8960efaa6b76a5baf32af00198d663b1628e42385e8fcfb06810edddcb7bd7c8`)

Corrected output:
[`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md)

Historical records, not amended:
[preparation handback](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-handback.md),
[R1 handback](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r1-handback.md)

Status: **Corrected assignment returned for independent Codex re-review. It is
not accepted, not assigned and not executable. `FRESH-A1-R2-1` is not claimed
closed. Claude has stopped.** Claude implemented I-7/I-7-R1 and remains
ineligible to execute R-5, to be its assignee, to select one, or to review or
accept the assignment. R-5 remains stopped, Blocking, unaccepted and
unauthorized.

---

## 1. Result and disposition

| Finding | Severity | Disposition (proposed; for Codex's re-review) |
|---|---|---|
| `FRESH-A1-R2-1`: required per-step timestamps cannot be produced by the authorized procedure | Important | **Remediated in text by adding authorized timestamp capture. The evidence contract was not narrowed.** §10 item 2 still requires start and end UTC timestamps for the whole run and for each step. §6.0 now defines "each step" as fifteen named timed scopes. Every scope has an exact producing label and invocation, all of them written in the assignment. Each timestamp's status is captured, printed and enforced, and a missing, failed or malformed timestamp is a HARD STOP |

No stop condition of R2 prompt §8 arose. Every mandatory document was read
completely (§8). Every controlling digest and accepted baseline value is
unchanged (§10). Step 4b's `rsync` bytes are unchanged (§5). The contract is
executable using only commands written in the assignment. No implementation,
test, fixture, manifest or governance change was needed. No further
execution-safety or PASS-eligibility ambiguity was found, and no other agent
changed either authorized path.

## 2. What changed in the assignment

* **Header.** A "Revised again under `C-P5.0-R5-RP11-FRESH-A1-R2`" line, with
  links to the R2 prompt, this handback and Codex's R1 review.
* **§4.1 item 3.** HA-4 is tied to S2.1 and S11.7, which stay unchanged, and
  is kept separate from the timed-scope values.
* **§4.3 item 2.** Timestamp values are listed as an explained,
  recorded-not-compared difference.
* **§6.0.**
  * A new substitution, `<HANDBACK>`, used only in the S12.end block and
    restricted to `[a-z0-9./-]`.
  * The block description now covers twelve step blocks and four timestamp
    blocks.
  * A new normative **Timestamps** subsection: format, the `r5_end` `EXIT`
    handler, governing-status precedence, and the meaning of "block exit 0".
  * A new **Timed scopes** table and rules: `not run`, `absent`, no
    reconstruction, HARD STOP, and no cross-host comparison.
  * A new status, 33: the handback body is missing.
* **Twelve step blocks** (1, 2, 3, 4a, 4c, 4d, 5, 6/7, 8, 9, 10, 11). Each gets
  an `r5_end` handler, and `r5_block` now begins with `trap r5_end EXIT` and a
  labelled start `date`. Nothing else in any pre-R2 block changed (§9).
* **Step 4b.** Separate S4b.start and S4b.end repository-host timestamp blocks
  around the unchanged `rsync`, with ordering and status rules.
* **Steps 1–11.** Each Pass text names the step's timing lines. Step 3 states
  that an INVALID RUN shows `S3 final exit=20`.
* **Step 12.** Rewritten as 12a (the S12.start block), 12b (the handback
  body) and 12c (the S12.end block, which appends the closing record). The
  exact closing-record form, the stop rule and the Pass text are given.
* **§7.** The summary now lists the four timestamp blocks, the timestamp
  commands on both hosts and the S12.end append. The unexpected-command rule
  now covers substitute timestamps, wrappers around the `rsync` and edits to
  the handback after S12.end begins.
* **§8.1.** New condition 3 (all fifteen scopes timed with status 0, and the
  closing record present). The later conditions were renumbered 4–9; their
  text is unchanged.
* **§8.3.** Adds timestamp and closing-record failures, and the S4b.end and
  step-12 exceptions to "no later step".
* **§10.** Item 2 is rewritten (§4 below). Item 6 now names the timestamp
  blocks, item 14 covers the `in closing record` answers and the verdict of
  record, and item 16 places the stop after S12.end.
* **§10.1 item 1.** The embedded transcripts now include every timing line;
  the S12.end closing record is the evidence for that block.
* **§12, U-7.** The confirmed handback filename is the `<HANDBACK>`
  substitution.

## 3. Timestamp-coverage table

The assignment's §6.0 holds this table normatively. Labels are exact. "Step
block" means the `date -u` command written in that block: the start `date`
runs immediately after `trap r5_end EXIT`, and the end `date` runs inside
`r5_end`.

| Scope | Start: label (status line) | End: label (status line) | Host |
|---|---|---|---|
| whole run | `RUN.start start_utc=`, from the same `date` invocation as `S1.start` (`S1.start date exit=`) | `RUN.end end_utc=`, from the same `date` invocation as `S12.end` (`S12.end.4 date exit=`), written into the closing record | repository host |
| step 1 | `S1.start start_utc=` (`S1.start date exit=`) | `S1.end end_utc=` (`S1.end date exit=`; `S1 final exit=`) | repository host |
| step 2 | `S2.start` (`S2.start date exit=`) | `S2.end` (`S2.end date exit=`; `S2 final exit=`) | `oracle-test` |
| step 3 | `S3.start` | `S3.end` (`S3 final exit=`, including 20) | `oracle-test` |
| step 4a | `S4a.start` | `S4a.end` | `oracle-test` |
| step 4b (`rsync`) | `S4b.start start_utc=`, S4b.start block (`S4b.start date exit=`, `S4b.start block exit=`) | `S4b.end end_utc=`, S4b.end block (`S4b.end date exit=`, `S4b.end block exit=`) | repository host |
| step 4c | `S4c.start` | `S4c.end` | repository host |
| step 4d | `S4d.start` | `S4d.end` | `oracle-test` |
| step 5 | `S5.start` | `S5.end` | `oracle-test` |
| steps 6 and 7, **combined** (R-1 gate, R-2 build, manifest `cmp`, root checks) | `S6-S7.start` | `S6-S7.end` (`S6-S7 final exit=`) | `oracle-test` |
| step 8 | `S8.start` | `S8.end` | `oracle-test` |
| step 9 | `S9.start` | `S9.end` | `oracle-test` |
| step 10 | `S10.start` | `S10.end` | `oracle-test` |
| step 11 | `S11.start` | `S11.end` | `oracle-test` |
| step 12 (handback and immediate stop) | `S12.start start_utc=`, S12.start block (`S12.start date exit=`) | `S12.end end_utc=`, S12.end block (`S12.end.4 date exit=`), written into the closing record | repository host |

The assignment states normatively that "each step" means these scopes and
nothing finer. Numbered checks such as S5.2, and prose actions, are not timed
separately. Steps 6 and 7 have exactly one combined pair. The §2 attestation,
written before step 1, is not timed.

## 4. Handback timestamp requirement: exact before and after

Before (`f4f4e1a3…9ff7`, §10 item 2):

```text
2. start and end UTC timestamps for the whole run and for each step;
```

After:

```text
2. start and end UTC timestamps for the whole run and for each step, where
   "each step" means each timed scope of §6.0 and nothing finer: a table with
   one row per scope (whole run; steps 1, 2, 3, 4a, 4b, 4c, 4d, 5, 6/7
   combined, 8, 9, 10, 11 and 12), giving the producing label, the host and
   the exact `start_utc`/`end_utc` line and status line copied from the
   transcript. The rows for the step-12 end and the whole-run end say
   `in closing record`, because the S12.end block writes those values into the
   handback itself (§6 step 12). A scope that did not start says `not run`,
   and an end value that was not printed says `absent`, with the invoking
   shell's status. No value is supplied from any other source;
```

## 5. Step 4b: the final `rsync` command and its unchanged bytes

```bash
rsync -avz --delete \
  --include='.env.example' \
  --exclude='.env*' \
  --exclude='*.pem' \
  --exclude='*.key' \
  --exclude='yt-cookies.txt' \
  --exclude='*service_account*.json' \
  --exclude='*credentials*.json' \
  --exclude='__pycache__/' \
  --exclude='*.py[cod]' \
  --exclude='.pytest_cache/' \
  /opt/freedom-blades/platform/ oracle-test:/tmp/<RUN>-checkout/
```

A Python comparison of the `rsync` code block extracted from the assignment
before and after R2 found it **byte-identical**. The extracted block's
SHA-256 is `ab36f33b63c43424f7da539d9a624658aee76cb872c7a7c2bb4ca9a95661f994`
both times, so the only variable part is still the existing `<RUN>`
placeholder. Nothing is prepended, appended, wrapped, redirected or chained.
The S4b.start and S4b.end timestamp blocks are separate `/bin/bash … -s`
invocations, and the executor issues nothing between them and the `rsync`.
Each preserves and prints its own status. The `rsync` status remains directly
observable as the invocation's own status, is reported first and governs step
4b. S4b.end is run after the `rsync` returns, **whatever its status**, so
that step 4b always has an end value. That is the only invocation permitted
after a nonzero synchronization status apart from step 12. If S4b.start
fails, the `rsync` is not run.

## 6. How the step-12 and whole-run timestamps are obtained

The difficulty is that the handback must contain values that, by definition,
exist only once the handback is complete. The assignment resolves this
without hand-copying a value and without any edit after the final reading:

1. **Whole-run start.** The first two commands of the step-1 block are
   `trap r5_end EXIT` (non-substantive) and one `date -u` whose format prints
   `RUN.start start_utc=…` and `S1.start start_utc=…` from a single clock
   reading. Both come before `cd` and every other preflight check. They enter
   the handback through the embedded step-1 transcript (§10 items 2 and 6,
   §10.1 item 1).
2. **Step-12 start.** The S12.start block runs immediately after the last
   invocation of the run. Its transcript is embedded in the body.
3. **Body.** The executor writes items 1–16. For the step-12 end and the
   whole-run end it writes the literal `in closing record`. The body must not
   contain a `Closing record` heading. From then on the body is final.
4. **Step-12 end and whole-run end.** The S12.end block checks the handback
   is a regular non-link file (otherwise status 33). It then calls
   `r5_close` with its standard output appended to `<HANDBACK>`. `r5_close`
   writes the `Closing record` heading and a `~~~text` fence, prints its own
   status line, and runs one `date -u` whose format prints
   `S12.end end_utc=…` and `RUN.end end_utc=…` from a single reading. It then
   prints that status (`S12.end.4 date exit=…`) and the closing fence. Each
   status is captured and enforced with `return`. The block prints
   `S12.end.5 closing-record exit=…` to the terminal and exits.
5. **Status recording.** The `date` status is inside the closing record. The
   append's own status is S12.end.5, and the closing fence's presence shows
   that the append completed. The assignment gives the record's exact
   six-line form. A handback that does not end with it is a HARD STOP for
   missing evidence, whatever the body says, and the reviewer can check this
   from the file alone.
6. **Immediate stop.** After the single reading that gives `RUN.end`, only
   the block's own status lines, the closing fence and `exit` occur. The
   executor then stops. It issues no command and makes no edit whatever the
   status.

The step-12 end and the whole-run end are equal by construction. A `~~~`
fence is used because a backtick fence inside the assignment's ```` ```bash ````
block would terminate that markdown block.

## 7. Status capture and failure handling

* Every new `date -u` and `trap` command is followed immediately by
  `status=$?` or `end_status=$?`, a labelled `printf`, and either an
  `exit`/`return` on nonzero or a precedence rule.
* **Step-block precedence in `r5_end`.** The first statement captures the
  exit status as `block_status`, per POSIX's definition of `$?` on entry to an
  `EXIT` trap. A nonzero `block_status` governs. Otherwise the end-`date`
  status governs. `<step> final exit=` prints the governing status, which is
  also the status the invoking shell reports. A check's failure status (for
  example 25, 29 or 32), and step 3's 20, are therefore preserved unchanged.
  This is the same "first checked status governs" rule as the R1 display
  pattern.
* A missing, failed or malformed required timestamp, or a missing or
  malformed closing record, is a **HARD STOP** (§6.0, §8.1 condition 3,
  §8.3).
* No required value may come from an operator's clock, terminal or SSH-client
  metadata, shell history, file times or an unstated wrapper. An unprinted
  value is recorded as `absent`, with the shell's status. It is never
  reconstructed.

**For the reviewer.** The `EXIT`-trap behaviour was taken from the POSIX and
bash definitions. Under the R2 prompt's authority it was checked by syntax
only (`bash -n`) and was not executed. The reviewer may want to confirm it
independently.

## 8. Mandatory documents read completely

Each was read from first byte to last before the first edit:

1. `.agents/AGENTS.md`;
2. `docs/review/Handover information`;
3. `docs/project-management/status.md`;
4. `docs/operations/disposable-test-server.md`;
5. the preparation prompt and the preparation handback;
6. the R1 remediation prompt and the R1 handback;
7. the proposed assignment (`f4f4e1a3…9ff7`, all 1,464 lines, read in two
   parts);
8. Codex's R1 review,
   `project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r1.md`;
9. the B1-R4 acceptance decision,
   `project-review-2026-10-02-p5-r5-rp11-b1-r4-acceptance.md`; and
10. the R2 prompt.

From `docs/implementation-plan.md`, each read completely: the reading map
(lines 19–51), §0 (53–183), §13 (2111–2215), §16 (2394–2482), §17 (2483–2503)
and §20 (2549–2616). `CLAUDE.md` was in context.

No search, excerpt or sizing substituted for these reads. The `grep -n` of
section headings was used only to find offsets.

## 9. Commands actually run

All were run on the repository host, in `/opt/freedom-blades/platform`. The
only repository files written were the two authorized outputs: the assignment
through a scratch Python edit script and the Edit tool, and this handback
through the Write tool.

* **State:** `git status --short` (start and end); `git rev-parse HEAD`
  (`9cad3ded…aaaa`); and `git diff --quiet HEAD -- infra tests tools
  pytest.ini` (exit 0).
* **Sizing and offsets:** `wc -c` on the required documents; `grep -nE '^#{1,2} '`
  on the implementation plan; `grep -n` for block-closing lines, Pass
  paragraphs and HA-4 references in the assignment; and `grep -n -iE` for
  redirect/substitution handling in `.claude/hooks/guard-secrets.py`, to
  confirm that its shape rules concern `rsync` invocations.
* **Copy:** one `cp` of the pre-R2 assignment to the session scratchpad
  (`assignment-before-r2.md`).
* **Edits:** `r2_transform.py` (scratchpad) inserted `r5_end` and the
  trap-and-start lines into exactly the 12 step blocks, then asserted 12. An
  inline Python replacement script made exact-once text replacements, each
  asserted unique. The remaining edits used the Edit tool.
* **Verification:** `r2_verify.py` (scratchpad) was **syntax-only**:
  * the `rsync` block is byte-identical before and after;
  * §3.1–§3.3 and both appendices are byte-identical;
  * every one of the 14 pre-R2 code blocks reappears verbatim once the R2
    insertions are removed;
  * after substituting sample values (`<RUN>` =
    `p5-r5-fresh-20261003T000000Z-0123abcd`, `<PY>`, the appendices, the S1.6
    program, and `<HANDBACK>` = the pending handback path), `bash -n` passed
    on all 18 code blocks and on the 16 inner block scripts (34 checks);
  * `ast.parse` passed on all 14 embedded Python programs;
  * no placeholder remained; and
  * the timestamp-coverage check found exactly one start, end and `final`
    line for each of the 12 step blocks, and exactly one each of
    `S4b.start`, `S4b.end`, `S12.start`, `S12.end`, `RUN.start` and
    `RUN.end`.

  The two blocks without an inner script are the §6.0 convention snippet and
  the `rsync`. Failures: 0. **No block, program or command of the assignment
  was executed**, and nothing was run locally or remotely as R-5.
* **Digests:** `sha256sum --strict -c --quiet` of the assignment's Appendix A
  (28 lines, extracted to the scratchpad) against the tree (exit 0); and
  `sha256sum` of the assignment, the preparation and R1 handbacks, the R2
  prompt and the R1 review.
* **Documentation checks:** §12.

Scratch files, all outside the repository: `assignment-before-r2.md`,
`r2_transform.py`, `r2_verify.py`, `appA.txt`, `r2syntax/*.sh`.

## 10. Accepted values and controlling bytes unchanged

* All 28 §3.2 files match Appendix A in the tree (`sha256sum -c` exit 0),
  and §3.1, §3.2, §3.3 and both appendices are byte-identical to the R1
  version. Manifest version 30; aggregate
  `28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526`;
  `cc1.v.baseline` 5,120 bytes,
  `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`; the
  four `expected.sha256` entries; `toolchain.lock` `f9238073…84cf`;
  `build-root.manifest` `f08ba9de…e76f`; and every other pinned digest. All
  are unchanged.
* `git diff --quiet HEAD -- infra tests tools pytest.ini` exits 0. No
  implementation, test, fixture, manifest, concrete plan, launcher source,
  generated artifact, `toolchain.lock`, `build-root.manifest` or
  `expected.sha256` was touched.
* The preparation handback (`0bb3a678…6b0b`) and the R1 handback
  (`0946d03b…5e8e`) still have the digests recorded earlier and in Codex's
  review. The R1 review, Handover, status, implementation plan and operations
  document were not modified.

**The R1 corrections remain intact:**

1. **`FRESH-A1-R1-1`.** Every pre-R2 status capture is preserved verbatim
   (§9). The added commands follow the same convention, and `r5_end` keeps the
   first failing status as the governing one.
2. **`FRESH-A1-R1-2`.** The absence conditionals and their distinct statuses
   10–14 are unchanged. The new status 33 follows the same pattern.
3. **`FRESH-A1-R1-3`.** The documented secret-excluding `rsync` is
   byte-identical, and so are the local (S4c) and remote (S4d) exact-byte
   checks.
4. **`FRESH-A1-R1-4`.** §4.2's HA-1/HA-2 rules, and the rule that a
   bubblewrap version-only difference is not HA-3, are unchanged.
5. **`FRESH-A1-R1-5`.** This task's complete reading is §8. The earlier
   records are untouched.

Also preserved:

* Claude's ineligibility to execute R-5, and the TBD executor named only by
  Peter;
* fresh resources, and no reuse of earlier R-5, B1, I-7 or I-7-R1 artifacts;
* the four normative outputs as distinct from the diagnostic
  `cc1.v.baseline`;
* the same-invocation R-1/R-2 gate, and exact bytes as the only `cc1check.py`
  PASS;
* 12 tests with 0 skips;
* one run, with no retry or remediation;
* no privilege and no prerequisite repair;
* HARD STOP over INVALID RUN over PASS;
* evidence retention (§10.1, with only the transcript-scope clarification);
* the executor's immediate stop; and
* Codex review and Peter's decision after any run.

## 11. Files modified or created

| File | Action | SHA-256 |
|---|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md` | revised in place (authorized) | before `f4f4e1a3e48d6968215596432af6a08218f91dbf9b60c458fd50f969cfa89ff7` (1,464 lines); after `f5b4c4e935817e7a68df3c8d1b6f8cc78617e0db6622a86a45ea38c1f0c18f94` (1,994 lines) |
| `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r2-handback.md` | created (this file) | not self-embeddable |

## 12. Documentation checks and final state

Relative links were resolved with a read-only Python `pathlib` check, which
also counted trailing-whitespace lines and tabs. Whitespace was also checked
with `git diff --no-index --check /dev/null <file>`, because both files are
untracked.

```text
assignment: relative links 9, missing [], trailing-whitespace lines 0, tabs 0
handback:   relative links 5, missing [], trailing-whitespace lines 0, tabs 0
git diff --no-index --check /dev/null <assignment>  -> no output, exit 1
git diff --no-index --check /dev/null <handback>    -> no output, exit 1
```

Neither checker reported a whitespace finding. Exit 1 comes from `--no-index`
reporting that the file differs from `/dev/null`; it is not a whitespace
finding.

**Correction during this task.** My first `git diff --no-index --check` run
recorded `exit 0` for both files, and that was wrong. The command expanded
`$(basename …)` before `$?`, so the status printed was `basename`'s. A re-run
that captured the status directly gave exit 1 with zero bytes of output for
both files, as shown above. The handback was checked before this results text
and the final status listing were filled in, and was re-checked afterwards
with the same result. The assignment's final SHA-256 is
`f5b4c4e935817e7a68df3c8d1b6f8cc78617e0db6622a86a45ea38c1f0c18f94`.

Final `git status --short`:

```text
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r1-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r1-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r2-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r2-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md
?? docs/review/project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r1.md
```

At the start, every entry except this handback was already present and
untracked. The only new entry is this handback. The assignment is the only
file modified, and all unrelated state is preserved.

## 13. Boundary confirmation

* No host inspection beyond repository files.
* No remote access: no `oracle-test`, SSH, `rsync` or network use.
* No provisioning, build, test or verifier run, and no synchronization. No
  `provision.py`, `enter.py`, `cc1check.py`, IC-1, B1 or R-5. No proposed
  block, program or command was run, even locally. `bash -n` and `ast.parse`
  only parse.
* No access to retained `/tmp` run evidence.
* No `sudo`, and no package, service, database or host-configuration change.
* No governance or current-state document edited. No implementation, test,
  fixture, manifest or generated artifact changed.
* No staging, commit or push.
* No executor selected, appointed, reviewed or accepted.

**R-5 remains stopped, Blocking, unaccepted and unauthorized.** RP-11 remains
unwired and unmet; `plan.is_executable=False`; PO-9 and PO-14 remain open;
Package 5.0 is not ready. Next: Codex's independent re-review of the corrected
assignment, then Peter Duscha's decision. Claude has stopped.
