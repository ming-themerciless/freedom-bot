# Claude handback — reserved disposable laboratory, C-P5.0-LAB-1

> **Partly corrected 2026-09-11.** This is the submission the
> [September 11 review](project-review-2026-09-11.md) answered, preserved
> unchanged apart from the dated correction in §3.4. The consolidated answer to
> that review's six findings is
> [`project-review-remediation-2026-09-11-handback.md`](project-review-remediation-2026-09-11-handback.md),
> and the runner contract this handback submitted is superseded by
> [revision 2](phase-5-0-reserved-laboratory-runner-contract-r2.md). Nothing here
> is accepted and no finding is closed.

Date: 2026-09-11. Author: Claude. Returned to: Codex, for technical review.

**Nothing here is accepted, no finding is closed, no digest is approved for
execution and no host was touched.** Package 5.0 remains **not ready**, P5.0-R5
**Blocking**, OD-62 **Open**, EH-R16-1 **Open**, `is_executable=False`, and the
three C-7 cases remain **declared unresolved**. Migration `0014`, product
implementation, deployment, cutover and Package 5.1+ remain unauthorized.

One decision is submitted for Peter: the **criterion split for
`JNL-47-RECOVERY-STATE`**, §3.4 below. It is not pre-approved by the laboratory
prompt and is not assumed anywhere in this tree.

---

## 1. Summary of what was done

| | Work | State |
|---|---|---|
| §2 | **CRP regression fix** PR-20260910-R2-1 in `models/skills.py` | implemented, reproduced first, 17 new regression tests |
| §3 | **Three C-7 dispositions** with bounded local producers | implemented; **resolves no case**; one criterion split submitted |
| §4 | **Reservation, admission and release** | decision half implemented and tested; lock adapter **proposed, not built** |
| §5 | **Operation-by-operation privileged-runner contract** | written; submitted for review; **not implemented** |
| §6 | **LAB-1**, a new defect found by the producers | reported, reproduced, **not repaired** |
| §7 | Permission delta | **zero** new privileged surface added; the EH-R16-1 remedy's exact diff submitted |
| §8 | Verification | full battery run against the submitted tree |

## 2. The CRP regression fix — separate, small, independently reviewable

**Finding PR-20260910-R2-1, conceded in full.** Reproduced before any change, on
the reported cell, with the reported numbers:

```
crp_dict: {'herbalist': 60, 'herbalism': 50}
read  "Herbalism Kit"        -> 60.0
add   "Herbalism Kit" + 1    -> 111.0
reversed cell order, read    -> 50.0
```

**Cause.** `get_tool_crp()` returned the **first** entry whose cleaned name
matched; `add_tool_crp()` summed **every** matching entry. The artisan alias
table makes `Herbalist` and `Herbalism` one tool, so one tool held two entries
and the read and the write disagreed about which of them counted.

**Correction.** One place now decides which stored entries belong to a tool —
`Skills._equivalent_crp_keys()` — and one place totals them,
`Skills._sum_crp_entries()`. Both `get_tool_crp()` and `add_tool_crp()` call
both. The identity rule is `_clean_tool_name()`'s, which both callers already
used for lookup, so **nothing is widened**: it is the existing bridge applied
consistently.

**What is preserved, and asserted:**

* **no persistence or mutation on read.** `get_tool_crp()` consolidates nothing,
  renames nothing and leaves `crp_modified` false. OD-06's rule that free-text
  column W stays unmerged on disk until reputation is actually awarded is
  unchanged, and so is `test_equivalent_spellings_are_not_merged_at_read_time`;
* **untagged CRP** (OD-34): the `general` fallback answers only when no tagged
  entry matches, and is never folded into a tool total;
* **unreadable CRP**: a single unreadable entry still reads as `0.0`; an
  unreadable entry among equivalents makes the whole read `0.0` rather than a
  total that silently omits it, and the write still refuses with `ValueError`;
* **mastered CRP** (OD-29): `"Master"` remains terminal and `can_record_tool_crp()`
  still refuses; and
* the existing alias fix and the synthetic skills fixture are untouched.

**Coverage added** — `tests/test_skills.py`, 17 tests, all synthetic fixtures:
both entry orders; all three alias families (Herbalist/Herbalism,
Forger/Forgery, Thief/Thieves); the Master-learning threshold above and below
100; the read-before-plus-one equality invariant; the purity of the read;
distinct tools still never totalled together; untagged, unreadable, unparsed and
mastered semantics; and the zero-award short circuit.

**Regression proof.** Re-running the suite with only the pre-fix `get_tool_crp()`
restored fails **17 of the new tests and none of the pre-existing ones**. With
the fix, `tests/test_skills.py` is **83 passed**.

No bot restart was performed and none is requested by this change.

## 3. The three C-7 dispositions

New module `tools/phase_5_0_evidence/feasibility.py` (planning tier) and
`tests/phase_5_0_evidence/test_feasibility.py` (46 tests).

### 3.1 How the producers work, and why they are not a supplied answer

Each experiment runs a deterministic model over an in-memory `_SyntheticHost`,
the model mutates that host, and the observation is **read back off the host** —
which artifacts exist, whether a registry row exists, whether the probe ran, what
the gate returned. The observation is then handed to the **existing, unchanged**
classifier in `provenance.py`, `journal.py` or `cleanup.py`, which holds the
expectation. That is EH-R16-2's separation, kept.

**Every experiment has a negative control that makes it fail.** A classifier that
cannot fail decides nothing, so `Arrangement.UNGUARDED` removes the provenance
gate and `Arrangement.UNORDERED` inverts the creation order, and the same
classifier over the same reader must return `FAILED` for both. It does.

The prompt's four extra cases are covered: **missing** output (four of five
stages supplied is not the case), **corrupt** output (a value outside its shape
is refused, not repaired), **duplicate** input (two records for one
`case_id#variant` is a refusal), **injected failure** (per stage, per omission)
and **cleanup failure** (both §2.13.2b variants).

### 3.2 Feasibility versus product evidence

| Case | Missing producer, in source terms | Local experiment | Establishes (feasibility) | Does **not** establish (product) | Carried by |
|---|---|---|---|---|---|
| `JNL-51-PROVENANCE-OMITTED` | `init-generation`. No file in this repository implements it; the C0 gate exists only as `provenance.EXPECTED_OMISSION_REFUSAL` and its classifier | C0 ordering modelled; `PVR` and/or `APR` omitted; host read back | that a gate ordered before the first durable artifact **and** before the probe is constructible, that case (g)'s four assertions are jointly satisfiable, and that the classifier separates a guarded from an unguarded arrangement | that `init-generation` refuses, that it refuses with `J-26`, or that it creates nothing when it does | §2.12.5a C0 implementation acceptance test, on the reserved host, `APR`/`PVR` suppressed out of band |
| `JNL-47-NO-GENERATION-ON-FAILURE` | the §2.13.2a probe with `init-generation`. The only stage vocabulary in the repository is `journal.FAILURE_STAGES` and its classifier | four-stage creation order with a deterministic failure at one named stage | that an ordering exists in which no single-stage failure leaves a partial generation, that the property is per-stage rather than aggregate, and that an arrangement publishing early is failed | that the real creation order has that property, that the product's failure paths are those five stages, or that a real failure at one leaves nothing | §2.13.5a R7-A implementation acceptance test: five runs, one per injected stage |
| `JNL-47-RECOVERY-STATE` | a run whose cleanup failed **after a coordinator created a generation**. Four clauses are produced today by `cleanup.classify_cleanup` — real harness code — and one by `executor._refuse_when_blocked`; the two **absence** clauses have no producer | an unremovable path injected into the harness's own §2.13.2b state machine, both variants | that the two cleanup failures are distinguished, that both report `S-B` with exit 3 and named residue, and that the next invocation is blocked — **four of seven clauses, on real harness code** | the fifth clause (**LAB-1**, §6) and the two absence clauses, which are vacuously true here because no coordinator ran | §2.13.2b implementation acceptance test, where a generation and a row exist to be absent |

### 3.3 What the dispositions do **not** do

All three remain `UnresolvedStep`s under conflict C-7, all three `ExternalCase`
contracts keep `producer_artifact_reviewed=False`, `resolves_coverage` is `False`
for every one of them, the external coverage column is empty, and
`ConcretePlan.is_executable` is `False`. `is_executable` was not changed and no
case was marked covered. `EvidenceResult.eligible_for_operational_acceptance`
remains unconditionally `False`. The unconditional operational-ineligibility and
missing-coverage controls were not touched.

Additionally, `feasibility.synthetic_payload()` emits under
`observations.SYNTHETIC_TARGET_IDENTITY`, so a feasibility record pointed at the
approved target is **refused for naming the wrong target**.
`test_feasibility.py` asserts that refusal, and asserts against the shipped plan
that all three cases are still unresolved.

### 3.4 The one decision required — criterion split for `JNL-47-RECOVERY-STATE`

> **Correction, 2026-09-11 — the rationale below is withdrawn and the decision
> request with it.** Finding **PR-20260911-5** established that §3.4's reasoning
> rests on the wrong creation order. Package plan §2.13.5a **C1** performs the
> §2.13.2a probe **and its cleanup**, and *"if the `finally` cleanup does not
> complete, the run ends in state S-B of §2.13.2b and no later step executes"*;
> **C2** validates while *"nothing has yet been written under `…/journal`"*; and
> **C5** is *"the first persistent artifact Algorithm C creates"*. `JNL-47`
> (package plan line 4159) requires **no journal file, no seal, no symlink, no
> `.close` manifest and no database row** for both cleanup-failure variants.
>
> So the run this section called the missing producer — *a run whose cleanup
> failed after a coordinator created a generation* — is a run the package
> **forbids**. Absence after a cleanup failure is **creation never reached**, not
> an already-created generation deleted, and the synthetic arrangement that
> published the journal, seal, `current`, `.close` and a registry row before
> injecting the cleanup failure modelled a prohibited ordering.
>
> **What changed as a result**, in
> [`project-review-remediation-2026-09-11-handback.md`](project-review-remediation-2026-09-11-handback.md)
> and in `tools/phase_5_0_evidence/feasibility.py`:
>
> * the model now runs C0 → C1-probe → C1-cleanup → C2 → C5 with publication
>   routed through an injected sink, so *creation never reached* and *creation
>   undone* are separate observations;
> * the two absence clauses are read off that sink rather than passed as
>   constants, and the positive control publishes, so an empty sink is
>   attributable;
> * `JNL-47-RECOVERY-STATE` is `meaningful_without_product_code=True`,
>   `dependent_work_to_stop()` is empty, and **the criterion split submitted
>   below is withdrawn.** No corrected criterion decision is required of Peter;
> * `JNL-47-NO-GENERATION-ON-FAILURE` now covers all five injection points
>   uniformly. The submitted claim that the `cleanup` point *"is not describable
>   by R7-A at all"* is also withdrawn: it is describable, for the same reason a
>   Stage-1 failure is; and
> * **LAB-1 is unaffected.** The recovery records still fail, and they still fail
>   on the named-operator-recovery clause alone. The repair is proposed in
>   [runner contract r2](phase-5-0-reserved-laboratory-runner-contract-r2.md) §8
>   and is not made.
>
> All three C-7 cases remain **declared unresolved** in the shipped execution
> plan, `is_executable` remains `False`, and nothing here closes a finding. The
> original submission is preserved unchanged below.


**The essential case that cannot be meaningful without gated product code.** Two
of its seven clauses — *no generation artifact* and *no database row* — require
that a generation created by a **real** coordinator is absent after the failed
cleanup. A run that never created one satisfies both vacuously, and a facsimile
that created a fake generation would be the second coordinator implementation the
direction forbids.

Dependent work on those two clauses is **stopped**, per the prompt. The exact
split submitted, and **not assumed anywhere in this tree**:

| | Criterion | Where it belongs | Rationale |
|---|---|---|---|
| **A** | `JNL-47-RECOVERY-STATE` clauses 1–5: exit status, §2.13.2b state, safe residue path reporting, next-run refusal, named operator recovery | **readiness**, P5.0-R5 | Produced by harness code that exists. Four pass today; the fifth is LAB-1 and is a repair, not a dependency on product code |
| **B** | clauses 6–7: generation absence and database-row absence | **implementation acceptance**, at the Package 5.0 gate | Only observable once a coordinator can create a generation. Requiring them before implementation is the circular dependency the September 2 authorization exists to break |

**Recommendation: adopt the split.** It is the smallest change that lets P5.0-R5
progress without either deleting a requirement or accepting a vacuous
observation as evidence. It **reduces no requirement**: clauses 6–7 keep their
full force and become a named acceptance test rather than an unmet readiness
precondition. Peter decides; Codex reviews the split before it is recorded.

If the split is **not** adopted, the consequence is explicit and should be stated
rather than worked around: P5.0-R5 cannot close before Package 5.0 implementation,
and Package 5.0 implementation cannot start before P5.0-R5 closes.

## 4. Reservation, admission and release

New module `tools/phase_5_0_evidence/reservation.py` (planning tier) and
`tests/phase_5_0_evidence/test_reservation.py` (41 tests).

**Implemented** — the decision half, as pure functions over injected
observations:

* the six states the direction names, with a transition table in which
  `QUARANTINED` and `RELEASED` have **no successors**. There is no edge from
  `RECOVERING` back to `ADMITTED`: recovery ends a reservation, never resumes it;
* the owner/run/target/release record. A request with no owner, target, deadline
  or recovery owner is refused at construction;
* **fail-closed admission** reporting *every* refusal rather than the first, so a
  caller cannot discover them one run at a time. It refuses on: a mismatched
  target; a quarantined host (cleared or not); a lock held by another
  reservation; a lock that could not be read; an incomplete inventory; any
  unaccounted writer; and real execution while EH-R16-1 is unremedied;
* **release** requiring six observations, each made rather than inferred, with
  `None` treated exactly like `False` and reported separately as *not checked*.
  A release that cannot establish its conditions **quarantines**; it does not
  fail back into a state somebody eventually takes the host from; and
* **recovery** requiring a complete operator attestation — termination
  established, residue accounted for, restoration verified or a separately
  approved rebuild — **and** release evidence. A complete attestation alone
  quarantines, because an operator's account of the recovery is not an
  observation of the target, the lock or the residue.

**The nine situations the prompt names are each an injected case:** a second
executor; a missing reservation (unreadable lock); an expired reservation; a
mismatched target; a mismatched release; an unknown writer; an orphaned child; a
delayed database transaction; an interrupted recovery; and the successful
release, which is the positive control without which every refusal above could be
a function that refuses everything.

**The cooperative lock.** One lock, `/run/freedom-blades/laboratory.lock`, and
`PARTICIPATING_ENTRY_POINTS` enumerates the seven project entry points that must
take it and what each does when it is held — the bot suite, the web suite, the
Foundry tests, §3.2 synchronization, §3.5 dependency updates, §4 environment
reset and the harness CLI. The rule for all seven is *wait or refuse*, never
proceed. `LOCK_LIMITS` states, in the module and asserted by a test, that the
lock is advisory, **revokes no permission**, and that **manual root access
remains a trusted operational premise** — holding it is not evidence the host is
quiet, which is what the inventory is for, and releasing it is not evidence the
run ended.

**Not implemented, and deliberately:** the adapter that actually takes the lock.
It is §9.2(c) of the contract, an unprivileged `flock(2)` on an ordinary file,
and it is an execution-tier module, so it is submitted rather than built.

**No VM manager, distributed scheduler or general privileged shell was
introduced.** A test asserts the module exports no name containing `spawn`,
`run`, `execute`, `kill`, `terminate` or `acquire`.

**The real-execution refusal is retained.** `admit()` refuses any request with
`real_execution=True` while the ownership remedy is unaccepted, unconditionally,
with a message stating that a reserved host does not repair substitution by the
run's own experimental writers. The operational-ineligibility control was not
cleared as a shortcut to testing admission.

## 5. The privileged-runner contract

`docs/review/phase-5-0-reserved-laboratory-runner-contract.md`, submitted for
technical review and **not implemented**. It contains the operation-by-operation
inventory the prompt requires: 15 numbered operations across creation,
provisioning, capture, materialization, experiments and cleanup, each with its
subject and bytes, how the path or descriptor resolves, its prerequisite, where
that prerequisite is enforced **today**, and whether there is a gap.

**Seven rows carry a gap and they are one finding, not seven:** every
ownership-dependent effect is issued against a pathname whose current resolution
nobody checked at the moment of the effect. The contract also carries subjects
and writable parents, the test identities, source custody, the verified
capture-to-restore binding, the restore destination, quiescence, and refusal and
uncertainty handling.

Four positions it takes explicitly, each answering an earlier correction:

* **staged-source substitution is not reintroduced** and stays withdrawn;
* **a held root descriptor does not protect every descendant.** `open(R, O_PATH)`
  does not stabilize the lookup of `R/bin`, of any deeper directory, or of any
  final entry;
* **independent configuration recovery is preserved** when the disposable root is
  unsafe, with its separate ownership basis stated: it is root's over
  `/etc/postgresql`, and it does not pass through the disposable root at all; and
* **destination substitution is not solved by fixing source substitution**, and
  the residual destination exposure is recorded as a residual rather than
  described as proved.

## 6. LAB-1 — a new defect, reported and not repaired

§2.13.2b requires an S-B run to report *the named operator recovery*, and
`journal.classify_cleanup_failure_state` compares that clause like the other six.
Two named recoveries exist for different things: `journal.RECOVERY_PROCEDURE` is
the five-step residue recovery, `cleanup.RECOVERY_PROCEDURE` the four-step
configuration recovery. `CleanupOutcome.recovery_procedure` carries **only the
second**, and only when a configuration capture was retained. A run reaching S-B
on **residue alone** — which is both variants of `JNL-47-RECOVERY-STATE` —
therefore reports no named recovery and fails that clause.

The repair changes `CleanupOutcome`'s accepted contract and adds a `cleanup` →
`journal` dependency, which is a mechanism change behind the outstanding design
checkpoint. **So it is submitted and not made.**
`test_feasibility.py::test_the_recovery_case_reproduces_lab_1` is a labelled
defect reproduction and deliberately asserts that the record **fails**; it was
not weakened to make the clause appear satisfied. Proposed **Important**; Codex
classifies.

## 7. Permission delta — zero

| Surface | Before | After |
|---|---|---|
| `plan.PERMITTED_EXECUTABLES` | 22 absolute paths | **22, unchanged** |
| `case_program.VERBS` / `BOOTSTRAP_VERBS` | 16 / 2 | **16 / 2, unchanged** |
| `executor.PERMITTED_RUN_AS` | the identity contract | **unchanged** |
| `sudoers.EXPECTED_COMMANDS` | 2 | **2, unchanged** |
| The one `ctypes` exception | `case_program._prctl_get_securebits` | **unchanged** |
| New privileged writer, verb, syscall, sudoers rule, capability, unit or file mode | — | **none** |

`git status` confirms `plan.py`, `case_program.py`, `executor.py`,
`boundary.py`, `materializer.py` and `sudoers.py` are unchanged in this pass.
Both new modules are planning tier: no process, no file, no socket, no product
import. `test_no_execution.py` asserts the first against their source, and
`test_feasibility.py` asserts the product-tree isolation against the module's
syntax tree — no `application`, `domain`, `adapters`, `models`, `migrations`,
`web`, `config`, `ext`, `helpers`, `connectors` or `main` import. Neither module
is reachable from bot startup, the web application or `migrations/`.

**The exact diff for the EH-R16-1 remedy is submitted, not built**, in contract
§9.2: four descriptor-relative verbs (`openat`, `unlinkat`, `renameat`,
`fstatat`) with two new argument kinds, reaching `openat(2)` with
`O_PATH|O_NOFOLLOW|O_DIRECTORY`, `unlinkat(2)`, `renameat2(2)` with
`RENAME_NOREPLACE` and `fstatat(2)` with `AT_SYMLINK_NOFOLLOW`; a descriptor
chain walked once per run with `st_dev`/`st_ino` comparison before every
dependent effect; an unprivileged lock adapter; and a verify-and-write over a
held buffer for the restore. It adds **no executable, no sudoers rule, no
capability and no identity**. No broad architecture round is requested, and the
rejected C-8 and VM mechanisms are not silently adopted.

## 8. Verification

Local synthetic tests with injected effects only. The canonical interpreter is
`/opt/freedom-blades/runtime/venv-web/bin/python` **on `oracle-test`**; this pass
used the handover's local fallback interpreters, **verified before use** —
`/opt/discord-bots/venv/bin/python` and `/opt/discord-bots/venv-web/bin/python`,
both Python 3.12.3. They are an exception for this restricted task and are not
the canonical environment. `TEST_DATABASE_URL` was explicitly unset throughout;
bot and web suites ran serially.

| Command | Result |
|---|---|
| `pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py` | **205 passed** |
| `pytest -q -rs tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py` | **16 passed** |
| `pytest -q -rs tests/phase_5_0_evidence/test_feasibility.py tests/…/test_reservation.py` | **87 passed** |
| `pytest -q -rs tests/test_skills.py` | **83 passed**, 1 warning |
| `pytest -q -rs tests/phase_5_0_evidence` | **1490 passed** |
| `pytest -q -rs tests/test_*.py` (bot) | **3016 passed, 326 skipped**, 1 warning |
| `pytest -q -rs tests/web` | **1610 passed, 1362 skipped** |
| `node --test 'foundry-module/tests/'*.test.mjs` | **171 passed, 0 failed, 0 skipped** |
| `compileall` on the nine changed Python files | passed |
| `git diff --check` | passed |
| `python3 .claude/hooks/test_guards.py` | 31 cases, all passed |

Baseline for comparison (2026-09-10 R2 review): harness 1391, bot 2991/326, web
1610/1362, Foundry 171. The harness and bot deltas are the 87 new tests and the
new module rows in the parametrized tier scans.

**Every skip is an unverified assertion.** The 1362 web skips and 326 bot skips
are database-marked tests that did not run. The canonical database-enabled web
figure is **80** skips, not 1362, so these results establish **no** PostgreSQL
migration, constraint, concurrency, recovery or backup evidence whatsoever.

**Checks not run, and why:**

* every `oracle-test` check. No SSH, synchronization, host inspection,
  provisioning, database operation, service mutation, generated-vector execution,
  `--execute` or armed real boundary or materializer was performed, per the
  task restriction;
* the authorized Codex read-only target preflight. It remains assigned to Codex
  after implementation review, unperformed, and this pass did not expand it. The
  **twelve unconfirmed target facts were not populated**, by assumption or
  otherwise, and `E7`'s ten reviewed facts were not supplied outside test
  fixtures;
* **formatter, linter and type checker: unconfigured, not failed.** No `ruff`,
  `black`, `flake8`, `mypy` or `isort` appears in `pyproject.toml` (absent),
  `pytest.ini`, or any of the four requirements files, and none is installed in
  either fallback interpreter. There is nothing configured to run; this is an
  environment/tooling gap to report, not a passed check; and
* no formatter was run, so no unrelated file was reformatted.

### 8.1 Manifest integrity

Manifest-covered source changed, so the manifest was regenerated **through the
non-executing path only** — `python -m tools.phase_5_0_evidence.execution.cli
--manifest-out … --render …`, which executes nothing.

* generated **twice** and compared: manifest and rendered plan **byte-identical**
  across both runs;
* `COVERED_SOURCES` grew from 32 to **34**: `feasibility.py` and
  `reservation.py` were added, which is why the count changed. Adding a file to
  the package is a declaration in three places — `COVERED_SOURCES`,
  `test_no_execution.py`'s tier table, and the `tests/web` scope guard — and all
  three were made explicitly;
* all **34** covered hashes independently recomputed with `hashlib.sha256` over
  the files on disk and compared with the manifest: **zero mismatches**;
* the manifest was **not hand-edited**. No digest was altered to hide a source
  change, and no producer review is recorded as performed.

**New review-input digest, not execution approval:**

```
bbb3854fbdffae00696544465f1cd7bbdf22ad18583056490a6735444800e4fa
```

It supersedes `ec1e3e70…56f2839` as review input because covered source changed.
**It must not be passed to `--execute`.** `is_executable` remains `False`, three
unresolved steps remain, and zero external cases resolve coverage.

## 9. Next runnable step

| | |
|---|---|
| **Step** | Codex technical review of this handback, the runner contract §9.2 permission diff, and the criterion split in §3.4 |
| **Owner** | Codex, with Peter deciding the split and classifying LAB-1's severity |
| **Evidence it establishes** | whether the descriptor-relative remedy is the accepted mechanism for EH-R16-1, and whether P5.0-R5's recovery criterion divides as §3.4 proposes. It establishes no operational evidence and closes no gate |

After that review, and only after it, the sequence is unchanged: implement only
the accepted mechanism, then the already-authorized Codex read-only preflight,
then a separate execution decision. Neither a green suite nor a clearer document
advances any of them.

## 10. Files changed

**Product (one file, one defect):** `models/skills.py`, `tests/test_skills.py`.

**Evidence harness:** `tools/phase_5_0_evidence/feasibility.py` (new),
`tools/phase_5_0_evidence/reservation.py` (new),
`tools/phase_5_0_evidence/review_manifest.py` (two `COVERED_SOURCES` entries),
`tests/phase_5_0_evidence/test_feasibility.py` (new),
`tests/phase_5_0_evidence/test_reservation.py` (new),
`tests/phase_5_0_evidence/test_no_execution.py` (two tier-table entries),
`tests/web/test_p3_4_static_assets.py` (two scope-guard declarations).

**Generated artifacts, review input only:**
`docs/review/phase-5-0-evidence-harness-review-manifest.json`,
`docs/review/phase-5-0-evidence-harness-concrete-plan.md`.

**Documents:** `docs/review/phase-5-0-reserved-laboratory-runner-contract.md`
(new), this handback (new), and concise pointer updates to
`docs/review/Handover information`, `docs/implementation-plan.md` §20,
`docs/operations/disposable-test-server.md` and the four registers under
`docs/project-management/`.

No migration was added. No configuration, deployment or rollback requirement
changes. No secret was read, printed or modified. Unrelated working-tree changes
were preserved; nothing was staged, committed, pushed or rewritten.
