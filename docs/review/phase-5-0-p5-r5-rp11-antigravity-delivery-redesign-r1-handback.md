# Handback — R4-R1 Antigravity wait-contract remediation (`C-P5.0-R5-RP11-FRESH-D1-R1`)

Date: 2026-10-04\
Assignee: Claude\
Prompt: [`phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-r1-claude-prompt.md`](phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-r1-claude-prompt.md)\
Finding: `R4-D1-1` in [Codex's independent review](project-review-2026-10-04-p5-r5-rp11-antigravity-delivery-redesign.md)\
Revised proposal: [`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r4.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r4.md)

Scope was a repository-only remediation with local tests. **No R-5 step and
no remote command was run, and `oracle-test` was not accessed.** No runner,
command resource, focused test, pin, identifier or handback path changed. No
secret or protected file was read. Nothing was committed or pushed.

R4 remains a proposal. It is unaccepted, and no host or execution authority
exists. R-5 remains Blocking and unaccepted. RP-11 remains unwired and unmet,
`plan.is_executable=False`, PO-9 and PO-14 remain open, and Package 5.0 remains
not ready.

## 1. Inputs read

* `.agents/AGENTS.md`, completely.
* `docs/implementation-plan.md`: the reading map, §0, §16 and §20.
* `docs/review/Handover information`.
* The R4-R1 prompt and Codex's review.
* The original redesign handback.
* In R4: the header, §0, §0.1, §2, §6.0 (including "Runner enforcement"),
  step 12, and §7 through §13.
* In `tests/test_r5_runner.py`: every place it reads R4 or applies a text
  rule. This established that an R4 prose change cannot affect a pin.
  * `test_the_r4_assignment_displays_every_resource_exactly` reads only the
    displayed block bodies.
  * The `\bwait\b` prohibition applies to the command resources only, not to
    R4.
  * No controlled file pins R4's digest.

## 2. Remediation of `R4-D1-1`

The defect was in R4 §13. It said that if Antigravity returned control before
the runner's final line, Gemini would report and stop. That conflicts with the
`/goal` terminal state.

§13 now has Gemini wait through Antigravity's wait facility for **the same,
already-started task**, and only that task, until the task returns showing the
runner's final line. If one wait call ends while the task is still running,
Gemini waits on the same task again.

While waiting, Gemini:

* does not reinvoke the runner or take any other action;
* sends no input, EOF or signal;
* does not poll or inspect the OS process by other means (`ps`, `pgrep`,
  `kill -0`, `/proc`, `ssh`, or reading the handback);
* does not yield, post progress or ask for confirmation.

Waiting ends only in one of two ways:

1. **The same task returns.** Gemini reports the final line or the refusal
   line and stops, as before. If the task returned without a final line,
   Gemini reports what the facility showed and stops.
2. **The wait facility reports a terminal transport failure.** The runner's
   state is then unknown. Gemini reports the condition verbatim and stops,
   without reinvoking, retrying, repairing, polling or signalling. This is
   explicitly not a verdict. The runner continues autonomously and closes the
   handback itself.

§13 also defines what "the defined terminal state" and "do not yield turns …
on background tasks" mean under this assignment. The runner's autonomous
closeout is unchanged.

The same rule is stated consistently in:

* **§0.1 item 7:** the amendment row, now citing `R4-D1-1`.
* **§7:** waiting is part of the one command and is not a second invocation or
  operational command.
* **§7.2:** the ban on polling and inspection now names the same-task wait as
  the only permitted contact.
* **§12 U-14:** the full disposition.

The audit (§4) found one further early-stop wording, which was also corrected.
§7.2's prerequisite paragraph said that "the executor **stops and reports**".
It now says that the run stops as a HARD STOP, the runner closes it, and the
executor reports the final line when the task finishes.

## 3. Maintainer dispositions recorded (R4 §12)

| Item | Recorded disposition | Also reflected in |
|---|---|---|
| U-14 | Same-task Antigravity waiting, as in §2 above | §0.1, §7, §7.2, §13 |
| U-15 | A pre-run refusal consumes the activation. A further invocation needs a new acceptance and activation | §8.4 |
| U-16 | No runner timeout. During a hung step Gemini keeps waiting and sends nothing. Ending a hung run needs a separately authorized recovery decision | §13 |
| U-17 | Invocation-based attestation accepted | — |

Other related changes:

* §12's preamble now says that only U-7 still needs confirmation.
* §0 item 3 no longer asks for U-13 … U-16 to be decided.
* The header gains an R4-R1 revision note that lists the changed sections. Its
  status line no longer says "not independently reviewed". It now records that
  this revision has not yet been re-reviewed.

## 4. Commands run and exact results

Local repository-host run. This is not the canonical `oracle-test`
environment, which the task forbids. `TEST_DATABASE_URL` was unset; no
database-marked test is in the focused file.

| Command | Result |
|---|---|
| `sha256sum tools/r5_runner/r5run.py tests/test_r5_runner.py` | `4ef88bd6…be015` and `6bc5320c…448f`, unchanged from the original handback and Codex's review |
| `sha256sum -c` over R4 Appendix C (19 lines, extracted from the revised R4) | all OK |
| `env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 venv-web/bin/python -m pytest -q -p no:cacheprovider tests/test_r5_runner.py` | **75 passed**, 0 skipped. The 2 warnings are the known `PytestConfigWarning`s for `asyncio_default_fixture_loop_scope` and `asyncio_mode` |
| `compile()` and `ast.parse(..., feature_version=(3, 10))` on the runner and the test, using `/usr/bin/python3` 3.12.3 | both accepted. No bytecode was written |
| `git diff --check` | exit 0, no output |
| `git diff --no-index --check /dev/null <R4>` | no whitespace finding. Exit 1 only signals that the files differ |
| `git check-ignore -v tools/r5_runner/__pycache__/r5run.cpython-312.pyc` | ignored by `.gitignore:6` (see §6) |

**Audit of the revised R4.** I searched for:

* `stop`/`stops` near `Gemini`/`executor`;
* `wait`, `poll`, `EOF`, `yield`, `reinvo`, `background`, `foreground`,
  `interactive` and `terminal tool`;
* the stale phrases `did not finish`, `in the foreground`, `open for Peter`,
  `U-13 … U-16` and `not independently reviewed`.

Results:

* **Early stop.** No instruction tells Gemini to stop before the same task
  returns. The only exceptions are a §8.4 refusal, which is itself the task
  returning, and §13 item 2's transport failure.
* **Waiting.** No instruction forbids the same-task wait.
* **No permitted interference.** None permits polling, inspection, input, EOF,
  a signal, a reinvocation or a user yield.
* **Remaining stop sentences.** These are consistent: §6 step 2's "the block
  stops", §7.1's banner expiry, §8.4's refusal, and §11's "After the handback,
  the executor stops".
* **Stale phrases.** None remain.

### Checks not run

* No canonical suite on `oracle-test`, because the task forbids access. The
  80-skip check therefore does not apply.
* No full local bot or web suite. Only documentation changed, and the focused
  suite is the one that reads R4.
* No type checker or linter. None is configured in the repository.
* **No Antigravity behaviour test.** The wait facility's real semantics cannot
  be verified from the repository. Examples are its maximum wait period and
  what it calls a terminal failure.

## 5. Files

| File | Change | Bytes | SHA-256 |
|---|---|---:|---|
| `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r4.md` | prose of header, §0, §0.1, §7, §7.2, §8.4, §12, §13 | 137335 (was 132703) | `7d472c0a2ca2b0a7efc0f42bd58c0d85bacbdef0911f1bbe9f6858a957b7e8cc` (was `12c07e4b…e8df`) |
| `docs/review/phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-r1-handback.md` | new (this file) | — | — |

No runner, resource or test file changed, so the 19 controlled files keep the
original handback's §6 identities and R4 §3.5 and Appendix C remain correct.

No migration, configuration or deployment change. The working tree's other
uncommitted changes were left untouched. I edited no governance or
current-state document (`Handover information`, `status.md`, plan §20).
Recording this result there is left to the maintainer or Codex, as before.

Rollback: restore R4 to SHA-256 `12c07e4b…e8df` (the reviewed bytes) and
delete this handback. R4 is untracked, so Git holds no copy. The prior bytes
are identified by digest only.

## 6. Unresolved issues and reviewer focus

1. **Provenance of the dispositions.** I recorded U-14 … U-17 as maintainer
   dispositions on the authority of the R4-R1 prompt, which states them, and
   Codex's recommendations. No separate decision record signed by Peter Duscha
   exists for them yet. The acceptance record should restate them.
2. **Re-waiting versus polling.** §13 lets Gemini call the wait facility again
   on the same task when one wait period elapses. I read this as part of
   "waiting until it completes", not as the forbidden polling, because Gemini
   reads only the facility's report for that task. The reviewer should confirm
   that reading.
3. **What counts as a "terminal transport failure".** R4 gives examples (the
   task is lost, or the facility can no longer wait on it) but cannot define
   Antigravity's actual error vocabulary. The judgement stays with Gemini at
   run time.
4. **A hung run never ends Gemini's turn.** Under U-16, Gemini waits
   indefinitely. Only a separately authorized recovery decision ends it.
5. **The original redesign handback's R4 digest is now historical.**
   `12c07e4b…e8df` describes the reviewed pre-R4-R1 bytes. That handback is
   not edited.
6. **Pre-existing bytecode.** `tools/r5_runner/__pycache__/r5run.cpython-312.pyc`
   exists, timestamped 2026-10-03 23:13 UTC. That is before this task and two
   minutes before Codex's review was written. I did not create or delete it.
   It does not affect a run:
   * the runner's identity check skips `__pycache__`;
   * `.gitignore` excludes it, so S1.3's untracked listing omits it; and
   * the runner runs under `-B`.

## 7. Stop

The remediation and this handback are complete, and I have stopped. R4
remains unaccepted. No host or execution authority exists until Codex re-reviews
R4-R1 and Peter Duscha records a separate acceptance and Gemini activation.
