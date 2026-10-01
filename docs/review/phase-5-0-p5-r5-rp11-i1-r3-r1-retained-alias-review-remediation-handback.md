# Claude handback — RP-11 I1-R3-R1 retained-alias review remediation

Prompt ID: `C-P5.0-R5-RP11-I1-R3-R1`

Date: 2026-09-28

Assignment:
[`phase-5-0-p5-r5-rp11-i1-r3-r1-retained-alias-review-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r1-retained-alias-review-remediation-claude-prompt.md)

Review remediated:
[`project-review-2026-09-28-p5-r5-rp11-i1-r3.md`](project-review-2026-09-28-p5-r5-rp11-i1-r3.md)

State: **returned repository-only for independent Codex technical, security,
operational and evidence re-review; Claude has stopped.** No finding is closed.
Nothing is accepted.

## 1. Summary

* **RP11-I1-R3-2, the whole-package discrepancy, is diagnosed and remediated
  in tests only.**
  * **Reproduced exactly.** In a fresh process with the soft descriptor limit
    lowered to Codex's 1024: **2941 passed, 379 failed, 0 skipped**.
  * **Why the earlier run passed.** This repository host's shells run with a
    soft limit of 1 048 576, which is why the I1-R3 run passed with 3320.
  * **Cause.** No production code in RP-11 fails to release a descriptor. The
    RP-11 capture suite **deliberately** leaves 618 descriptors open in the
    pytest process, and the retention suite leaves one:
    * interruption tests, 533: the mechanism must make no call after an
      interruption, not even a close;
    * sessions that tests never end, 73;
    * fault modes that withhold or discard a real close, 13.
  * **Second contributor, older lab suites.** Four older, unrelated lab test
    modules leak another 963. Together the two sources pass 1024 at the
    RP-11 capture suite.
  * **Fix.** It is test-only: the RP-11 fixtures now track and release what
    they leave open.
  * **Result after the fix.** The whole package passes from a fresh process
    at **both** limits: **3336 passed, 0 failed, 0 skipped**.
* **The lab leak is outside this assignment's authority.** It sits in
  `lifecycle_storage.DurableRecordStore`, production source that §8 does not
  authorize. It is reported, not fixed (§7.5). It leaves about 49 descriptors
  of headroom under 1024.
* **RP11-I1-R3-3, the stale wording, is corrected.**
  * The proposed operational draft no longer says that no RP-11 mechanism
    exists. It states the precise state instead.
  * It marks the unadmitted-pair rule as awaiting a decision of record.
  * No requirement changed. The draft is now SHA-256
    `4f68e4c75d477db041935906c0138146700b85bb1c6ece14434cf60711c2d549`,
    unaccepted.
* **RP11-I1-R3-1, the unadmitted-pair policy, is prepared for Peter's
  decision.**
  * The
    [decision proposal](phase-5-0-p5-r5-rp11-i1-r3-r1-unadmitted-pair-decision-proposal.md)
    compares the two options and recommends **option 1, permit
    metadata-only**. It carries adoptable `accept option 1` and `accept
    option 2` texts.
  * Source semantics are unchanged: option 1 stays implemented.
  * Fifteen new tests prove that option 1's exception is exactly one recorded
    pair and no wider. **No decision is recorded.**
* **Unchanged.** No `tools/` byte changed. The review manifest (version 23,
  `264674da…`), both generated artifacts and the capture-tool digest
  (`9c1b02a1…`) are unchanged. The mechanism remains unwired.

## 2. RP11-I1-R3-1 — decision proposal and still-open status

The proposal is
[`phase-5-0-p5-r5-rp11-i1-r3-r1-unadmitted-pair-decision-proposal.md`](phase-5-0-p5-r5-rp11-i1-r3-r1-unadmitted-pair-decision-proposal.md).
Its key points:

* **Where the conflict comes from.** The accepted redesign proposal §4
  permits the recorded pair of a *published* object. The I1-R3 assignment §4
  permits the pair of an *admitted* object.
* **When the options differ.** Only after a stop between a final link and
  admission, followed by a successful X-3. That is **15 of the 43** modelled
  act-stage storage failures: P-7 after the link, every P-8 step after it,
  and every X-2 step.
* **Consequence of option 2.** Each of those 15 makes X-4 `inconclusive` for
  the whole pass and makes B0-RA stop, permanently, because C-8 retains the
  root and forbids removal.
* **No recovery path under option 2.** The draft has no provision for a
  second Pass A. One would repeat the §5 `rsync --delete`.
* **Recommendation: option 1.** It adds no evidentiary claim, and it stops on
  every shape except the one the mechanism leaves. It avoids discarding
  admitted acts for a post-verification close or barrier failure. It matches
  the accepted design direction, and it is what is implemented and tested.
* **What each option would change.** The proposal lists the exact draft,
  source and test changes an option-2 implementation would make (§7), and the
  small follow-up an option-1 decision needs (§8).

**Status: Open, Blocking.** Peter supplied no decision while this assignment
was active, and none is recorded or inferred. The draft's X-4 and B0-RA text,
and one test docstring, now say that the rule awaits a decision of record.
`retention_check.py`'s module docstring still says "maintainer decision,
2026-09-28". Editing it would change covered-source bytes and the manifest, so
it is left for the decision implementation (proposal §8).

## 3. Dispositions

| Finding | Severity | Disposition on return |
|---|---|---|
| RP11-I1-R3-1 | Blocking | **Open.** Decision proposal prepared, recommendation option 1, semantics unchanged. Boundary tests added (§5). Awaits Peter's decision of record. |
| RP11-I1-R3-2 | Important | **Open, remediation proposed.** Reproduced, root-caused and remediated test-side. The whole package passes at 1024 and at the host default from fresh processes. One out-of-scope contributor is reported (§7.5). Closure is Codex's and Peter's call. |
| RP11-I1-R3-3 | Important | **Open, remediation proposed.** Stale existence statements replaced; draft digest recomputed. |
| RP11-I1-R1-1, RP11-I1-R2-1, RP11-I1-2 | — | **Open**, untouched. |

## 4. Files changed, with SHA-256

"Before" is what I recomputed at the start of this assignment, or, for the
three RP-11 test files, the value the I1-R3 handback reports. I did not hash
those three before my first edit. Nothing else touched them after I1-R3.

| File | Change | Before → after |
|---|---|---|
| `tests/phase_5_0_evidence/rp11_fixtures.py` | descriptor tracking and release (§6.4); `open_session` defaults to a pass-through `FaultFilesystem` | `8fe61df4…` → `73f8808e5b23443ed9e2a9d255c8dbb5b0044f45e3bb2850e2349e8c40784e2b` |
| `tests/phase_5_0_evidence/test_rp11_capture.py` | imports the autouse fixture; one regression test | `053de064…` → `07e1bfb57c0cdb80b215d3fb18cafba9efc8aa022ca3a514ec81d6cef7f7e4bd` |
| `tests/phase_5_0_evidence/test_rp11_retention.py` | imports the autouse fixture; 15 unadmitted-pair boundary tests; one docstring marked pending decision | `0863414c…` → `9a1104a07edf1ae3a38a928c11b595cca03d0c327ca07cb3503360155d4fd768` |
| `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` | state wording (§5) | `402126322f341d378c569cc302c8eb3607b746a1b5c8fc81a91d6af8b19cbe28` → `4f68e4c75d477db041935906c0138146700b85bb1c6ece14434cf60711c2d549` |
| `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r1-unadmitted-pair-decision-proposal.md` | new | → `ac504ce188cb2eb477006eb3cbbdf0d66cd932568ecb5ed62a72151ba47f3e60` |
| this handback | new | not self-hashed |
| four current-state pointers (§12) | pointer updates only | before: Handover `22255a5e…`, status `7d57a449…`, plan `3dab23fe…`, test server `1cadb67d…` |

**Unchanged, recomputed after the final edit.** Each value equals the I1-R3
handback's "after" value:

* `capture_contract.py` `437d663e…`
* `capture_store.py` `c038174d…`
* `capture_mechanism.py` `b64d92cb…`
* `retention_check.py` `482e1a5a…`
* `descriptors.py` `84db0935…`
* `review_manifest.py` `b7e7cabe…`
* review manifest JSON `f4f24537…`
* concrete plan `ddb51460…`
* capture-tool digest over the seven `RP11_SOURCES`: `9c1b02a1b7ef861ffb177b162427a185b90d86c3aa25d3a64573848d36a1d992`

## 5. RP11-I1-R3-3 — the wording correction

The draft states the facts the assignment requires. No requirement is added,
removed or changed. The changes are:

* **Header.** A note records this correction and its scope.
* **Admission status, Pass A.** "RP-11 … which does not exist" is replaced by
  the following. RP-11 is unmet. Repository source and focused tests for a
  candidate mechanism exist, but that implementation is unreviewed,
  unaccepted, not pinned and wired to no operational command.
* **Notation.** `⟨RP-n⟩` is a prerequisite that is "not yet met", instead of
  one that "does not exist yet".
* **RP-11 row.** "No such mechanism exists in the repository" becomes an
  explicit state:
  * the source files are named;
  * the implementation, amendment and manifest digest are unaccepted;
  * the mechanism is wired to nothing;
  * C-11 and the launcher environment are unresolved;
  * no real capture root and no Pass A handback exist;
  * RP-11 is unmet.
* **§9.3.** "Until RP-11 exists" becomes "Until RP-11 is met — reviewed,
  accepted, pinned and wired".
* **A0-08.** Its unresolved cell says RP-11 is unmet and why, so A0-08 is
  unusable.
* **B0-RA.** Its unresolved cell adds that no real Pass A capture root and no
  Pass A handback exist, so B0-RA is unusable. The unadmitted-pair sentence no
  longer calls the in-session answer a "maintainer decision". It says the rule
  is not yet a decision of record and links the proposal.
* **B0-08.** Its unresolved cell says RP-11 is unmet and B0-RA cannot yet
  succeed, so B0-08 is unusable.
* **§9.5.2 X-4.** The unadmitted-pair clause is marked as awaiting a decision
  of record.
* **§11 stop table.** "RP-11 absent" becomes "RP-11 unmet".

Kept, because they are already accurate: §9.5's heading ("unmet: no
**reviewed** mechanism exists") and `PIN.capture_tool_sha256` ("no reviewed
RP-11 mechanism exists"). A scan for `does not exist` and `no such mechanism`
now finds no statement about RP-11.

## 6. RP11-I1-R3-2 — descriptor-exhaustion diagnosis

### 6.1 The six questions

1. **Does the whole-package command reproduce the failure in a fresh
   process?** Yes, at Codex's limit. With `ulimit -Sn 1024` in a subshell and
   the stated prefix, the unchanged tree gave **379 failed, 2941 passed, 0
   skipped**, with `OSError: [Errno 24] Too many open files`. That is Codex's
   figure exactly. At this host's default soft limit of 1 048 576, the same
   tree passes.
2. **The first failing test and the earliest attributable growth.**
   * The first failure is
     `test_rp11_capture.py::test_exceeding_a_bound_stops_the_pass_without_truncating`.
     The launcher cannot create its pipes and reports `capture-start-failed`
     instead of `stream-bound-exceeded`.
   * A per-test observation of the pytest process's own descriptor table
     (§6.3) shows the table already at **975** when RP-11's first test
     starts. Of those, 963 were leaked by `test_lab_call_graph` (101),
     `test_lab_integration` (112), `test_lab_implementation` (350) and
     `test_lab_live_authority` (400).
   * RP-11's capture tests then add about 6 each. The table crosses 1024 at
     `test_the_root_is_created_exclusively_with_the_fixed_layout_and_modes`
     (1011 → 1017 → …), and the next test that needs a pipe fails.
3. **Do the retained-alias changes introduce, expose or merely follow the
   leak?** They **enlarge** a leak that I1 introduced. They introduce no new
   kind of leak.
   * The committed HEAD tree, exported to the scratchpad and run the same
     way, leaks **429** from the RP-11 capture suite, against 618 now. It also
     fails at 1024, at the **same first test**.
   * I1-R3 added publication stages, and so more parametrized interruption
     and fault cases.
   * The lab leak predates RP-11 entirely. It alone leaves the package under
     1024.
4. **The exact descriptor ownership or release defect.**
   * **RP-11, test-side only.** Three classes, 619 descriptors across both
     RP-11 suites:
     * **(a) Interruptions, 533.** `CaptureInterrupted` models the
       mechanism's process ending, so C-15 requires no further call, not even
       a close. A real crash has the kernel close them; pytest's process
       lives on.
     * **(b) Unended sessions, 73.** Tests that inspect an `OPEN` session
       never end it. Ending it would add an X-3 write the test is not about.
     * **(c) Fault injection, 13.** Mode `"fail"` on a close stage withholds
       the real close. Mode `"after"` on an opening stage discards the
       descriptor the real call returned.

     In production RP-11 code, every ordinary failure path closes through
     `_close_quietly`, and the stop transition releases the store. No
     production RP-11 release defect was found.
   * **Lab, production-side, out of scope.** `lifecycle_storage.DurableRecordStore`
     opens file descriptors through `PosixFilesystem.openat` in
     `read_record_bytes` (about line 1615) and `create_file` in its
     publication (about line 1849), and never closes them. The leaked
     descriptors are `lifecycle.json`, `lifecycle.json.tmp (deleted)` and
     run-ledger files, including on fully successful protocol paths.
5. **Why the earlier 3320-pass run differed.** It ran under a soft limit of
   1 048 576, so the combined leak of about 1594 descriptors never reached
   the limit. Nothing in the test outcomes differs otherwise.
   **Resolved.**
6. **Do the selections pass from fresh processes after remediation?** Yes,
   as shown in §8. The focused RP-11 selection gives 383 passed, 0 skipped.
   The whole package gives 3336 passed, 0 skipped, both at 1024 and at the
   host default.

### 6.2 Not classified as 379 defects

The 379 failures are one cascade. Once the table reaches 1024, every later
test that opens a pipe, a directory or a file fails, in RP-11, provisioning
and elsewhere.

### 6.3 The observation used

A scratchpad-only pytest plugin, `fdwatch.py`, was loaded with `-p` from
`PYTHONPATH=<scratchpad>`. It is not in the repository. It lists
`/proc/self/fd` of the pytest process before and after each test, and logs
the growth reduced to the last two path components. It inspects no other
process, host, protected artifact, secret or environment.

The one repository test that observes descriptors,
`test_the_suite_releases_every_descriptor_it_leaves_open_on_purpose`, also
reads only `/proc/self/fd`. The structural `/proc` guard covers
`RP11_SOURCE_MODULES` under `tools/`, not tests.

### 6.4 The remediation, test-side only

`rp11_fixtures.FaultFilesystem` records every descriptor its real opening
calls return, together with the `(st_dev, st_ino)` of that descriptor. It
drops a descriptor when a real close of it succeeds. With no stage set,
`FaultFilesystem` is the real filesystem, unchanged, and `open_session` now
defaults to it.

An autouse fixture, `rp11_release_descriptors`, runs `release_suite_descriptors()`
after each test body. It closes only descriptors whose number still refers to
the recorded object. It closes **outside** `_invoke`, so each interruption
test's "no call after the interruption" log is unaffected.

No assertion was weakened. No test was reordered, split or skipped. No
resource limit was raised: the only `ulimit` used **lowered** the limit to
reproduce Codex's run. No production source changed.

**Regression test.**
`test_the_suite_releases_every_descriptor_it_leaves_open_on_purpose` builds
all three classes of scenario, asserts that they hold descriptors, releases
them, and asserts the process's own table is back to its baseline.

* With `FaultFilesystem.release_held` neutralized by a scratchpad-only plugin
  (`norelease.py`), the test **fails**: extra descriptor `15`.
* With the fix, it passes.

## 7. Requirements, source and test consistency map

### 7.1 The recorded unadmitted pair under option 1, as implemented

The decision proposal §6 carries the full map. In summary:

* **Draft.** RP-11 row (e); §9.5.2 X-4; B0-RA condition 5.
* **Pair representation.** `capture_contract.accounted_objects` pairs two
  recorded unadmitted names by `role_of`, with no identity.
* **Store accounting.**
  * `CaptureRootStore.publish` records a final name only after a successful
    link, or after a failed link whose `lstat` shows the bound inode.
  * An `EEXIST` occupant is never recorded.
  * `PublicationState` is exact.
* **Final state.** `CaptureSession._finalize_once` records every known
  regular name that is not admitted.
* **Retention check.**
  * `_Verifier.enumerate` permits link count one or two, and no more names
    than links.
  * `_aliases` requires two names to be recorded partners at link count two,
    and gives `pair-divergent` for partners on different inodes.
  * `_admitted_pairs` checks identity, owner and mode for admitted pairs only.
  * `read_admitted` is never called for an unadmitted name.

### 7.2 The assignment's minimum refusal list

Each item below now has a test, and each new test asserts that neither
unadmitted member was opened:

* a lone member at link count two (new);
* divergent members;
* a third link outside the root, and inside it (new);
* a cross-object alias (new, plus the existing ones);
* a name in two pairs or categories (new, plus the existing one);
* an unrecorded pair;
* a non-regular member, as a directory or a symbolic link (new);
* an absent member;
* an incomplete enumeration (new);
* a changing enumeration or verification (new).

**Three expectations corrected against observed behaviour.** Each still
stops fail-closed:

* A non-regular member stops with `pair-divergent`, because the partner check
  precedes the bidirectional type comparison.
* A third link added during listing stops with `path-alias`, because it is
  seen at link count three before any time comparison.
* The same holds for a third link added during verification.

### 7.3 Option 2

The exact draft, `retention_check` and test changes are in proposal §7. They
are **not** implemented.

### 7.4 Preserved

The following are unchanged, byte for byte:

* the R5 bidirectional name/type comparison and evidentiary limit;
* named exclusive staging, one no-follow non-replacing link, both names
  retained, no cleanup, and admission by the next durable state;
* the mechanism remains unwired.

### 7.5 Out-of-scope follow-up — proposed, not done

* **Source.** `tools/phase_5_0_evidence/lifecycle_storage.py`,
  `DurableRecordStore.read_record_bytes` and its publication path. Each opens
  a descriptor through `PosixFilesystem` and never releases it.
* **Effect.** 963 descriptors across four lab test modules, and a real
  per-operation leak in any long-lived process using the store.
* **Smallest scope.** Close, or `PosixFilesystem.release`, each descriptor
  those two methods open, on success and failure paths. Add a descriptor
  regression test in `test_lab_integration.py`. Bump the manifest version for
  the covered-source change.
* **Why not here.** The file is covered production source outside §8's
  authority.
* **Risk.** Until it is fixed, the whole-package run has about 49
  descriptors of headroom under a 1024 soft limit. A future test that holds a
  few more could reproduce the cascade.

## 8. Commands and results

**Environment.**

* Interpreter `/opt/freedom-blades/runtime/venv-web/bin/python` (CPython
  3.12.3).
* Linux 6.8.0-139-generic, on the repository host only.
* Pytest temporary directories only.
* Default soft descriptor limit 1 048 576, hard limit 1 048 576.

**Prefix.** Every pytest command ran serially, each in its own fresh process,
with this prefix:
`env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 /opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs -p no:cacheprovider`.

**Diagnosis, before the fix.**

| # | Selection | Limit | Result |
|---|---|---|---|
| D1 | `tests/phase_5_0_evidence` | 1024 (lowered) | **379 failed, 2941 passed, 0 skipped**; `Errno 24`; first failure as §6.1(2) |
| D2 | RP-11 suites with `-p fdwatch` | default | 367 passed; 619 descriptors left open |
| D3 | `tests/phase_5_0_evidence` with `-p fdwatch` | default | 3320 passed; 1582 descriptors left open (RP-11 capture 618, retention 1, lab 963) |
| D4 | HEAD tree (`git archive HEAD` to the scratchpad), same, with `-p fdwatch` | default | 3220 passed; RP-11 capture 429, lab 963 |
| D5 | HEAD tree, `tests/phase_5_0_evidence` | 1024 (lowered) | failures and errors, then an internal error at session finish. First failure `test_exceeding_a_bound_stops_the_pass_without_truncating` (`-x`) |
| D6 | the regression test with `-p norelease` | default | **1 failed**, as intended |

**Final tree.** Each row is a fresh process.

| # | Selection | Limit | Result |
|---|---|---|---|
| 1 | `test_rp11_capture.py` | default | **265 passed, 0 skipped** |
| 2 | `test_rp11_retention.py` | default | **118 passed, 0 skipped** |
| 3 | 1 + 2 together | default | **383 passed, 0 skipped** |
| 4 | the I1 focused selection as recorded in the I1-R3 handback (§8 row 4): RP-11 suites plus the nine named modules | default | **1286 passed, 0 skipped** |
| 5 | `tests/phase_5_0_evidence`, one process | default | **3336 passed, 0 failed, 0 skipped** |
| 6 | `tests/phase_5_0_evidence`, one process | **1024** (lowered) | **3336 passed, 0 failed, 0 skipped** |
| 7 | `-m tools.phase_5_0_evidence.execution.cli --manifest-out <scratchpad>/manifest.json --render <scratchpad>/plan.md` | — | exit 0. The output reports: `DRY RUN — nothing was executed.`; 138 steps; 43 mutations; 47 cleanup steps; 4 unresolved (C-7, C-S4-3); `review manifest digest: 264674daf8ac…`; `executable : False`. Both outputs are **byte-identical** (`cmp`) to the committed artifacts. |

* **Warnings.** Every pytest run printed exactly pytest's two `Unknown config
  option` warnings: `asyncio_default_fixture_loop_scope` and `asyncio_mode`,
  from the shared `pytest.ini`.
* **Skips.** Zero in every row, checked with `grep -ci skipped`.
* **Other checks.**
  * `git diff --check` scoped to the four edited repository files: clean.
  * Each changed Python module compiled with `compile()`: clean.
  * The capture-tool digest was recomputed with
    `capture_contract.capture_tool_sha256`.
  * Every SHA-256 in §4 was recomputed with `sha256sum` after the final edit.
  * Markdown links in the draft header, proposal, handback and pointers
    resolve to existing files.
  * The bytecode-free runs wrote no `__pycache__`. The pre-existing
    `__pycache__` directories were left alone.

## 9. Manifest and generated artifacts

No covered source byte changed. `review_manifest.py` stays at version 23, and
the manifest is not regenerated: the dry run reproduced both artifacts byte
for byte. Neither the draft nor the tests are manifest inputs.
`264674da…` remains review input only, **not an approval**.

## 10. Unwired confirmation

* No `execution/*cli.py` names `capture_mechanism`, `capture_store`,
  `retention_check` or `capture_contract`.
* `test_nothing_outside_tests_arms_the_launcher_or_creates_a_session` passed
  in row 1.
* The dry run executed nothing and reports `executable : False`.

## 11. Checks not run, and why

* **Not run: the full bot and web suites, `oracle-test`, SSH, sync and
  database.** §6 and §9 of the assignment prohibit them.
  `TEST_DATABASE_URL` was unset throughout.
* **Not run: a secrets scan.** It is prohibited by §9.
* **Not run: formatter, linter and type checker.** None is configured: the
  repository has no `pyproject.toml`, `setup.cfg`, `ruff.toml`, `mypy.ini`,
  `.flake8` or `tox.ini`. The package's structural tests are its enforced
  checks, and they ran.
* **Not hashed before my edits: the three RP-11 test files.** Their "before"
  values in §4 are the I1-R3 handback's.
* **Not remediated: the lab descriptor leak.** Outside scope (§7.5).

No guard or tool refused a call. One Bash call received no auto-mode
classifier verdict, a transient error. It was retried once, as-is, and ran.

## 12. Current-state pointers updated

The following now point to this remediation, its handback and mandatory
independent Codex re-review:

* `docs/review/Handover information`;
* `docs/project-management/status.md`;
* `docs/implementation-plan.md` §20;
* the first restriction banner of `docs/operations/disposable-test-server.md`.

No historical handback, review or acceptance record was edited. No acceptance
record was added.

## 13. Task-relevant Git status

The branch is `docs/platform-plan`. Nothing was committed or pushed.

* **This assignment modified** `rp11_fixtures.py`, `test_rp11_capture.py`,
  `test_rp11_retention.py`, the operational draft and the four pointers. It
  added the decision proposal and this handback.
* **Still modified and uncommitted from I1-R3, unchanged by this
  assignment:**
  * the five RP-11 `tools/` modules;
  * `review_manifest.py`;
  * both generated artifacts;
  * `test_no_execution.py` and `test_r16_remediation.py`.
* **Untracked from earlier work:** the assignment prompt. Other unrelated
  worktree changes are preserved.

## 14. Proposed independent-review focus

1. **Diagnosis.** Reproduce D1 and row 6 under `ulimit -Sn 1024`. Confirm the
   cascade has one cause.
2. **The release fixture.** Check that it cannot close a descriptor the
   code under test still relies on, since it runs only after the body and
   checks identity. Check that it masks no production leak: every RP-11 leak
   class is by design or injected.
3. **Option 1 boundary tests.** Check they are complete against the
   assignment's list. Check that the three corrected expected reasons are the
   right fail-closed classification.
4. **The decision proposal.** Check its analysis of the 15 pair-leaving stops
   and the operational consequence of option 2.
5. **The draft wording.** Check it asserts no acceptance, pin, authority or
   closure.
6. **The lab leak follow-up.** Is it a production defect worth its own
   assignment, and does the thin headroom need action first?

## 15. Return state

* RP11-I1-R3-1 remains Open, Blocking.
* RP11-I1-R3-2 and RP11-I1-R3-3 remain Open, Important.
* RP11-I1-R1-1, RP11-I1-R2-1 and RP11-I1-2 remain Open.
* The requirements amendment, the implementation and the digest remain
  unaccepted.
* RP-11 remains unmet, and neither pass is executable or authorized.
* P5.0-R5 remains Blocking and OD-62 G-A remains conditional.
* `plan.is_executable=False`, and Package 5.0 remains not ready.

Claude has stopped.
