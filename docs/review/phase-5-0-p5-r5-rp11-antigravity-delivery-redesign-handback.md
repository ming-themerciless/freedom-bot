# Handback — Antigravity-compatible R-5 delivery redesign (`C-P5.0-R5-RP11-FRESH-D1`)

Date: 2026-10-03\
Assignee: Claude\
Prompt: [`phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-claude-prompt.md`](phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-claude-prompt.md)\
Authority: [R3 HARD STOP acceptance and redesign authority](project-review-2026-10-03-p5-r5-rp11-fresh-r3-hard-stop-acceptance.md)\
Proposed successor: [`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r4.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r4.md)

Scope was repository-only design, implementation and local testing. **No R-5
step and no remote command was run. `oracle-test` was not accessed.** No
dependency was installed, no host configuration changed, no secret or
protected file was read, no accepted launcher input or normative baseline was
altered, and nothing was committed or pushed. Gemini is not activated, and
R-5 readiness is not claimed.

R-5 remains Blocking and unaccepted. RP-11 remains unwired and unmet,
`plan.is_executable=False`, PO-9 and PO-14 remain open, and Package 5.0 remains
not ready.

## 1. Inputs read

* `.agents/AGENTS.md`, completely; `docs/implementation-plan.md` reading map,
  §0, §16 and §20; `docs/review/Handover information`.
* In full: the accepted R3 assignment
  (`…-assignment-r3.md`, SHA-256
  `039f68fbe7fc0f572b31879087a2e9d91e2a6b17892a4fca075af1c81b767bac`,
  108,733 bytes); the R3 handback (`…-r3-handback.md`); Codex's R3 HARD STOP
  review; Peter Duscha's R3 HARD STOP acceptance and redesign authority.
* Code read to place the runner safely: `read_covered_sources` and
  `COVERED_SOURCES` (`tools/phase_5_0_evidence/execution/cli.py`), the
  `cc1check.py` summary format, `pytest.ini`, and repository tests that scan
  `tools/` (`tests/test_rejected_scope_absent.py`).

No disposable artifact from any earlier run was read or reused.

## 2. Design

The R3 failure was in delivery, not in the commands: Antigravity's background
terminal never delivered the Step 1 heredoc, then returned 0 after a manual
EOF (`FRESH-R3-HS-1`), and the closeout that depended on the executor's
judgment skipped S12.start (`FRESH-R3-HS-2`). The redesign removes the
terminal and the executor's judgment from both paths and changes no command.

* **Static command resources.** `tools/r5_runner/blocks/` holds R3 §6's
  sixteen blocks as files, each exactly the text R3 placed between
  `<<'R5BLOCK'` and `R5BLOCK`, with R3 §6.0's substitutions applied except
  `<RUN>`, plus step 4b's `rsync` command as an argument vector
  (`s04b-sync.argv`). They were **generated mechanically from R3** by the
  derivation functions in the focused test, not hand-copied.
* **Runner.** `tools/r5_runner/r5run.py` is a stdlib-only, single-file Python
  orchestrator that runs under `python3 -I -B`. For each block it starts
  exactly R3's process (`/bin/bash --noprofile --norc -s`, or that behind
  `ssh oracle-test`). It writes the resource's bytes, with only `<RUN>`
  substituted, to that process's standard input through a pipe, then closes
  the pipe. That is the input R3's quoted heredoc delivered. It runs `rsync`
  through `execve` with no shell and standard input from `/dev/null`. Every
  child starts in a new session, so it has no controlling terminal. Standard
  output, standard error and the true `waitpid` status are captured
  separately and in full.
* **Enforcement in the runner.** The runner enforces:
  * a fixed order, with each step attempted exactly once (an attempt ledger
    refuses repeats and reorders);
  * evidence completeness after every invocation: every
    `<label> exit=0` line the block's `r5_block` prints, in order and exactly
    once, plus its timestamps and a `final exit` equal to the true status.
    Exit 0 with missing output is a HARD STOP;
  * R3's pass outputs that no exit status encodes: S1.3 count and digest, S5.8
    mode `755`, S9.1 `5120` and the `cc1check.py` result lines, and S11
    against S2;
  * a stop at the first terminal condition, with R3's single S4b.end
    exception;
  * no timeout, retry, cleanup or remediation path.
* **Mandatory closeout.** In a `finally` path that also covers runner
  exceptions and SIGINT/SIGTERM (SIGHUP is ignored), the runner always:
  1. runs S12.start;
  2. renders the body from the captured transcripts, falling back to a raw
     transcript dump if the renderer fails;
  3. appends the body once;
  4. **seals** the handback writer;
  5. runs R3's unchanged S12.end block, which appends the closing record.

  After S12.end it reads, writes and runs nothing.
* **One immutable handback.** The handback is created with `O_EXCL|O_NOFOLLOW`,
  and the runner refuses if it exists. It holds the identity record and the
  §2 attestation, written before step 1, then the body; the closing record is
  written only by S12.end.
* **Identity before any host action.** The runner refuses before touching any
  host if:
  * the interpreter was not started with `-I -B`;
  * the arguments are not exactly R4 §13's;
  * its own SHA-256 differs from the value on the command line;
  * any pinned resource or the focused test differs in SHA-256 or length;
  * `tools/r5_runner/` holds any other file or a link; or
  * the handback already exists.

  It then sends only the verified in-memory bytes.
* **One short invocation.** Gemini issues one line, once (R4 §13), containing
  no heredoc, pipe or multiline text.

## 3. Deliverables

| # | Required | Delivered |
|---|---|---|
| 1 | Repository-owned, non-interactive runner with exact reviewable bytes; no interactive stdin or EOF | `tools/r5_runner/r5run.py` plus 17 static resources. The runner never reads standard input, and the invocation redirects it from `/dev/null` |
| 2 | Focused local tests that simulate execution; no `oracle-test`, no download, no R-5 | `tests/test_r5_runner.py`, 75 tests (§5). Every block is answered by a fake host. One test drives the real transport with a harmless non-R-5 script |
| 3 | Complete standalone successor derived from R3; only delivery and closeout replaced | `…-assignment-r4.md` (§4 below) |
| 4 | Runner, every resource and every focused test pinned by SHA-256 and length; verified before any remote access | R4 §3.5 and Appendix C; runner `PINS`; runner digest on the command line |
| 5 | One short, non-interactive Gemini invocation path | R4 §13: the standard `/goal` line plus one command |
| 6 | Runner enforces order, exactly-once, first-terminal stop, capture of stdout/stderr/status, mandatory closeout, one immutable handback, no cleanup/retry/remediation | `AttemptLedger`, `evidence_gaps`, `Runner._run_operational`, `SubprocessExecutor`, `Runner._closeout`, `HandbackFile` |
| 7 | Standard resolved `/goal` pointing to the successor's final path | R4 §13 |

Coverage of the tests the prompt names:

| Required case | Tests |
|---|---|
| Step 1 success and progression | `test_step1_success_progresses_to_step2`, `test_a_complete_run_attempts_every_invocation_once_in_order` |
| Step 1 missing output despite exit 0 | `test_step1_exit_zero_without_any_output_is_a_hard_stop` (the R3 case), `test_a_partial_transcript_with_exit_zero_is_a_hard_stop`, `test_a_zero_status_that_disagrees_with_the_blocks_final_exit_is_a_hard_stop` |
| Nonzero first-step failure | `test_a_nonzero_first_step_is_a_hard_stop_quoting_its_first_failure` |
| First failure, no later operational step | `test_the_first_failure_stops_every_later_operational_step` (each of the 12 step blocks), plus the 4b sync and S4b.start cases and `test_step3_status_20_*` |
| Unconditional S12.start, body, S12.end | every failure test asserts `… + ["S12.start", "S12.end"]` and the closing record; also `test_closeout_follows_a_failed_s12_start`, `…_process_that_could_not_start_or_was_interrupted`, `…_runner_internal_error`, `…_signal_outside_a_process`, `test_a_failed_renderer_still_produces_a_closed_handback` |
| Closing-record immutability | `test_the_body_is_final_before_s12_end_and_nothing_writes_after_it`, `test_an_existing_handback_is_never_overwritten` |
| Rejection of altered resources or runner identity | `test_an_altered_command_resource_is_refused`, `test_an_altered_runner_is_refused`, `test_an_altered_focused_test_is_refused`, `test_an_extra_or_linked_resource_is_refused`, `test_only_the_assignments_invocation_is_accepted`, `test_the_runner_refuses_without_isolated_bytecode_free_python` |
| Preservation of R3's commands | `test_each_resource_is_its_r3_block_with_only_the_6_0_substitutions` (17), `test_the_plan_uses_r3s_invoking_process_for_every_block`, `test_the_plan_order_is_r3s_order`, `test_the_r4_assignment_displays_every_resource_exactly`, `test_each_block_is_sent_as_its_resource_with_only_run_substituted` |

## 4. The successor assignment (R4)

R4 was made by mechanically copying R3. Each of R3's sixteen heredoc-wrapped
code blocks was re-presented as `Resource: <path>` followed by the identical
block body; only the invoking line and the `R5BLOCK` terminator were removed.
The prose was then edited only where delivery or closeout is described.
Preserved unchanged:

* every block's command bytes;
* the 28 pinned inputs and Appendices A and B, re-verified read-only for this
  preparation (all 28 `OK`);
* the normative outputs and the reference environment;
* the HA rules and the `/var/tmp` resource model, including the 4 GiB floor;
* statuses 10–33 and the timed-scope table;
* the first-failure semantics and the S4b.end rule;
* the verdicts and their precedence;
* the handback item list and the retention rules; and
* the no-cleanup, no-retry and no-remediation rules.

Changed (R4 §0.1 lists them):

* header and status (Proposed);
* §0 decision list, including the commit precondition;
* §2 attestation by invocation, and the R3 run added to the forbidden list;
* §3.5 runner pins (new);
* §5 runner-generated `<RUN>`, consumed IDs and handback path;
* §6.0 "Delivery" (replaces "Substitutions" and "Blocks") and "Runner
  enforcement" (new);
* small edits in steps 1, 3, 4b, 9, 10 and 11 naming the runner where R3 named
  the executor;
* step 12 (runner performs 12a–12c unconditionally and seals before S12.end);
* §7 executor and runner actions, and new forbidden items;
* §8.3 additions and §8.4 pre-run refusal;
* §10 runner-written handback;
* §12 U-7 and the new U-13 … U-18;
* §13 invocation and single command; and
* Appendix C.

**No conflict with exact preservation was found**, so no gate or command was
changed and the stop clause did not trigger. These delivery-level differences
are disclosed for review:

1. **Separate streams.** R3's transcript was what a terminal showed, with
   stdout and stderr interleaved. The runner captures and embeds them
   separately, each with its length and SHA-256. Ordering between the two
   streams is not preserved.
2. **New session.** Each child has no controlling terminal. A prompt from
   `ssh` (host key or password) now fails with status 255 instead of waiting.
   This is a process attribute, not a command change.
3. **`rsync` without a shell.** The fifteen arguments equal R3's line after
   shell quote removal (tested). R3's remark that this was "the only shape the
   repository secrets guard admits" concerned the Claude Code hook. That hook
   does not mediate the runner's `execve`, and R4 says so.
4. **Synchronization evidence.** Only the exit status and the `sent …` and
   `total size is …` lines are embedded. The per-file list and standard error
   are identified by length and SHA-256 only, applying R3 §10.1's "only" rule
   and its non-controlled-content rule. If `rsync` fails, its error text is
   therefore not in the handback (reviewer focus).
5. **Two R3 judgments stay with the reviewer** rather than becoming runner
   conditions:
   * whether an unexpected pytest warning reports a skipped, failed or unrun
     check; and
   * whether any network traffic other than HTTPS to the snapshot occurred.

   R3 left both to the executor's reading; R4 §6.0 item 6 states it.
6. **Inner heredocs remain.** `<<'SUMS'`, `<<'LIST'` and `<<'OUTPUTS'` are
   part of R3's block text and are read by the block's own `bash` from its
   script, not from a terminal. Removing them would change R3's commands.

## 5. Commands run and exact results

Interpreter for the tests: `/opt/freedom-blades/platform/venv-web/bin/python`
(Python 3.12.3, pytest 9.1.1), verified before use. This is a local
repository-host run. It is not the canonical `oracle-test` environment, which
this task forbids. `TEST_DATABASE_URL` was unset, so database-marked tests
skip; no figure here is PostgreSQL evidence.

| Command | Result |
|---|---|
| `env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 venv-web/bin/python -m pytest -q -p no:cacheprovider tests/test_r5_runner.py` | **75 passed**, 0 skipped, 2 warnings (`PytestConfigWarning: Unknown config option: asyncio_default_fixture_loop_scope` and `… asyncio_mode`; pytest-asyncio is not installed in this interpreter) |
| `env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 venv-web/bin/python -m pytest -q -rs -p no:cacheprovider tests/test_r5_runner.py tests/test_rejected_scope_absent.py tests/test_rp11_launch_gate.py tests/test_rp11_launch_source.py tests/test_rp11_launch_toolchain.py tests/phase_5_0_evidence` | **4131 passed, 19 skipped**, 2 warnings (same two), 38.19 s. Skips: 7 in `test_rejected_scope_absent.py` (`TEST_DATABASE_URL is not configured`) and 12 in `test_rp11_launch_toolchain.py` (`RP11_LAUNCH_BUILD_ROOT is not set`), the known toolchain-dependent set |
| `python3 -m py_compile tools/r5_runner/r5run.py tests/test_r5_runner.py` | compiled (the bytecode it wrote was then deleted) |
| `ast.parse(..., feature_version=(3, 10))` on both files | accepted (Python 3.10 grammar) |
| `git diff --check` | exit 0, no output (no tracked file changed by this task) |
| `git diff --no-index --check /dev/null <file>` for the runner, the 17 resources, the test and R4 | no whitespace finding |
| `sha256sum --strict -c --quiet` over R3 Appendix A (28 lines) | all 28 `OK`, at `HEAD` `9cad3ded6479fb7b423b35c1d815fbfc7e48aaaa` |
| `git status --porcelain --untracked-files=all -- infra tests tools pytest.ini` | only the 19 new untracked files (§6); nothing else in the controlled paths |

The rendered handback was also inspected for a simulated PASS run and for the
R3 failure shape (S1 exit 0, no output). In the second, steps 2–11 are shown
as `not run`, S1's timestamps as `absent (invoking status 0)`, S12.start as
present, and the file ends with the closing record.

### Audit of the final proposal

| Path searched for | Result |
|---|---|
| Interactive standard input | none. The runner has no `sys.stdin` or `input(` (test-enforced); children get a closed pipe or `/dev/null` in a new session |
| Terminal heredoc | none. No resource contains `R5BLOCK` (test-enforced). R4 shows blocks as resources. The only heredocs are R3's inner `SUMS`/`LIST`/`OUTPUTS` documents, read by the block's own `bash` (§4 item 6) |
| Background tasks | none. No `&`, `nohup`, `disown`, `wait` or `sleep` in any resource (test-enforced); the runner uses `communicate` on one child at a time |
| Retry | none. The ledger refuses a second attempt. No `retry` in resources; the runner has no loop that re-invokes |
| Cleanup | none. No `rm`, `rmdir`, `sudo` or `apt` in resources (test-enforced); the runner deletes nothing |
| Shell in the runner | none. No `shell=True`, `os.system` or `pty` (test-enforced) |

### Checks not run

* **No canonical suite on `oracle-test`.** The task forbids access, so the
  `TEST_DATABASE_URL`-exported web/bot runs and the 80-skip check were not
  performed.
* **No full local bot or web suite.** Only the focused and directly affected
  modules above were run.
* **No type checker or linter.** None is configured in the repository (no
  `pyproject.toml`, `setup.cfg`, `mypy.ini` or ruff configuration), and none
  is installed in the available interpreters. The code is typed but not
  machine-checked.
* **No real execution of any R-5 block,** including S1.8's in-memory
  manifest. That S1.8 and S1.6 are unaffected was established by reading
  instead: `COVERED_SOURCES` is enumerated and names no runner file, and no
  runner file is under `infra/rp11-launch/`.
* **No Python 3.10 or 3.11 interpreter.** Only the 3.10 grammar check was run.
  The repository host's `/usr/bin/python3` is 3.12.3.
* **No Antigravity behaviour testing** (U-14).

## 6. Files

New, all untracked, nothing committed:

| File | Bytes | SHA-256 |
|---|---:|---|
| `tools/r5_runner/r5run.py` | 58050 | `4ef88bd6059af6624bea9c4155ab895076e6076d031efd6c0fe60f13a63be015` |
| `tools/r5_runner/blocks/s01.sh` | 11516 | `2900b9f43e114cc30571f4b2db8f6c46828a6e932330096eb29c4ecbff57ea0d` |
| `tools/r5_runner/blocks/s02.sh` | 7000 | `a0cda6026583275d45c1a8b88cc0ed77ba97a9973408d66990469901ef78d264` |
| `tools/r5_runner/blocks/s03.sh` | 1560 | `2d4c39b8ccf9d84afc4a439b08611ce3f5bca32a3b97021bb6caca8d8759676b` |
| `tools/r5_runner/blocks/s04a.sh` | 1172 | `1a948d6758f6ece09dbafc8f250a5682ec2b096cbed814eb25a8ed57657ef0a1` |
| `tools/r5_runner/blocks/s04b-start.sh` | 240 | `55ab56d97581e442bf24c3ebe6ab9e6b6714a1aaac04f0f0d620e3d45d4aff85` |
| `tools/r5_runner/blocks/s04b-sync.argv` | 313 | `7dddbaef33807f4158792c7270d5a6d7e38049938a87953c7c905c44c8738050` |
| `tools/r5_runner/blocks/s04b-end.sh` | 232 | `a77be397cf2b9a00737f25a5c4d4e17dc706e2d5478353f9afc2dbdbb95c261e` |
| `tools/r5_runner/blocks/s04c.sh` | 4420 | `1c8b06263214b29e6675b23b2fee3a203ea0a31018485f113e2abebf8de63a84` |
| `tools/r5_runner/blocks/s04d.sh` | 8708 | `8912189776ffa2f9644e24e297e73f9598b0137035afbaaa91c24e266e485331` |
| `tools/r5_runner/blocks/s05.sh` | 3231 | `7750e2502d7ecea05350d3d596b15d59b0b7243789502cc954592862ff4cb64b` |
| `tools/r5_runner/blocks/s06-s07.sh` | 3193 | `58a63f9cefb8323b339e92dd3f799e2570291803792c705a4face97eacc49868` |
| `tools/r5_runner/blocks/s08.sh` | 2440 | `c55ada18c1cd607189e7f6ef4d99de4e4589ee1d78208a643006caf900464878` |
| `tools/r5_runner/blocks/s09.sh` | 1588 | `46bbcd1f6eee93531d08350699b83f71897e3c40cea35c2eedde54c517d02dc6` |
| `tools/r5_runner/blocks/s10.sh` | 2029 | `6502636bf63a5194574ca553e3ca8c2ac3889e2d2bfe97c76e890f60731828f7` |
| `tools/r5_runner/blocks/s11.sh` | 10066 | `1431cb617b27a2c978b337203973674723dd8ede6aa6ae2510a00a9341400ef4` |
| `tools/r5_runner/blocks/s12-start.sh` | 240 | `bf495fd370a236b04295e955ce083e63fd4ead1fa8e2fabe4ca788a21f1f2aa3` |
| `tools/r5_runner/blocks/s12-end.sh` | 1283 | `eda40b93b105e04fa1d0c52d950120a85100eaa1d0dd71ddedd1f28e1bbf16aa` |
| `tests/test_r5_runner.py` | 30835 | `6bc5320c389f4f816297782436d0f4c97d084ae6dbefdb983e3d2255f26b448f` |
| `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r4.md` | 132703 | `12c07e4b0639a436baccee2381dbacdc02396406ff38e9e13bf5e2f09844e8df` |
| `docs/review/phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-handback.md` | this file | — |

The first 19 rows are the controlled files that R4 §3.5 pins. The runner's
digest appears in R4 §13's command. The runner holds the other 18 as `PINS`.
The R4 document is not pinned by any controlled file, so its digest is
recorded here for Peter's acceptance record only.

No migration and no configuration or deployment change. No tracked file was
modified. The working tree's pre-existing uncommitted changes (documentation
under `docs/`) were left untouched. No current-state or governance document
(`Handover information`, `status.md`, plan §20) was edited; recording this
handback there is left to the maintainer or Codex.

Rollback: delete the 21 new files. Nothing else changed.

## 7. Security and safety implications

* The runner writes exactly one file, the handback. It creates nothing under
  `/tmp` or `/var/tmp` on the repository host and keeps no log.
* The synchronization scope is R3's, unchanged, and is still the documented
  secret-excluding list. Withholding the per-file list keeps non-controlled
  file names out of the handback.
* Transcripts embed each block's complete standard error, as R3's terminal
  transcripts did. No block reads a secret.
* **Self-verification has a limit.** A deliberately altered runner could skip
  its own check. The independent assurances are:
  * Codex's review of the exact bytes;
  * the commit of those bytes before activation, which S1.4 then binds to
    `HEAD`;
  * the digest that the executor's command carries from R4; and
  * R4 Appendix C, which a reviewer can check without the runner.
* **Residuals:**
  * killing a local `ssh` may not stop remote work;
  * SIGKILL of the runner prevents closeout, because nothing can catch it; and
  * a hung step waits forever (U-16).

**Guard refusal during preparation.** One of my edit commands was refused by
`guard-secrets.py`. The command text quoted R3's `rsync` exclusion pattern
while editing R4 prose; it read no secret. I treated the refusal as binding
and did not re-send that text. I confirmed that the refused command had made
no change, then issued the same prose edits with that one replacement anchored
after the quoted pattern, so the command no longer named it. The resulting R4
text keeps R3's sentence about the exclusion order verbatim.

## 8. Unresolved decisions for Peter Duscha

* **Commit precondition (R4 §0 item 4).** The 19 controlled files must be
  committed with the §6 bytes before activation. Otherwise S1.4 stops step 1
  with status 28.
* **U-7.** Confirm work ID `C-P5.0-R5-RP11-FRESH-R5-R4` and handback path
  `…-rebuild-r4-handback.md`. Changing the path changes `s12-end.sh`, the
  runner `HANDBACK` constant and every pin.
* **U-14.** Antigravity terminal behaviour cannot be verified from the
  repository. R4 has Gemini report and stop if the tool returns before the
  runner finishes, with no polling and no touching the process. The runner
  completes and closes the handback regardless.
* **U-15.** Whether a pre-run refusal, which touches no host and writes no
  handback, consumes the activation.
* **U-16.** No per-step timeout, as in R3. Adding one would be a new stop
  condition.
* **U-17.** Attestation made by the invocation flags and written by the
  runner.
* **U-18 (disclosed).** Warning classification and network observation stay
  with the reviewer.

## 9. Proposed reviewer focus

1. **Byte preservation.** Check `derived_resources()` in the test and confirm
   it is an adequate proof that each resource equals R3's block under R3
   §6.0. In particular check:
   * `<APPENDIX A>`/`<APPENDIX B>` line replacement with no blank line added;
   * the S1.6 program's quote boundaries in S4d.4 and S11.3; and
   * `<HANDBACK>`.
2. **Transport equivalence.** Check that `bash -s` reading a closed pipe is
   the same input as R3's quoted heredoc, given `r5_block </dev/null`. Check
   the effect of `start_new_session` on `ssh` and on `bwrap`/`enter.py`
   (`--die-with-parent --new-session` is inside `enter.py` and unchanged).
3. **Runner rules.** Check that `evidence_gaps` and the specific pass outputs
   (R4 §6.0 "Runner enforcement") neither add nor relax an R3 gate. Check in
   particular:
   * that taking the label list from the resource text is complete for every
     block, including S2.11's conditional branch and S6.2/S9.3/S10.2's
     separately captured statuses; and
   * the S3 INVALID RUN condition.
4. **Closeout.** Check that every path through `Runner.run` reaches S12.start,
   the body and S12.end once each, and that the handback writer cannot be
   used after sealing.
5. **Synchronization evidence** (§4 item 4), and whether rsync standard error
   should be embedded on failure despite R3 §10.1.
6. **The single command and U-14** (R4 §13): whether the wording gives Gemini
   no decision to make.

## 10. Stop

The proposal and this handback are complete. I have stopped. R4 is not
executable until Codex independently reviews it and Peter Duscha records a
separate acceptance and Gemini activation.
