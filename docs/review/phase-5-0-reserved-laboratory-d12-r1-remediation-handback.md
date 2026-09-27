# Claude handback — C-P5.0-LAB-D12-R1, the D1 lifecycle-publication admission

Date: 2026-09-15. Authorization: **C-P5.0-LAB-D12-R1**, one bounded
repository-local remediation.
Finding remediated: **PR-20260915-LAB-D12-1 — Blocking**, from
[Codex's D1/D2 correction re-review](project-review-2026-09-15-reserved-laboratory-d1-d2-corrections.md).
Contract amended: [runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).
Submission it answers: [the correction handback](phase-5-0-reserved-laboratory-r6-d1-d2-correction-handback.md).

**Returned for independent Codex technical and security re-review. Nothing here
closes a finding or advances a gate.** C-7 remains unresolved; EH-R16-1 **Open**;
`plan.is_executable` **False**; all twelve target facts and **I3** unconfirmed;
V6, V8 and V10 unperformed; LAB-R6 **Open**; **LAB-X1 newly Open**; Package 5.0
**not ready**; P5.0-R5 **Blocking**; OD-62 **Open**. The authorized read-only
target preflight stays queued until this re-review accepts the remediation and
Peter releases it.

**New review-input digest:**
`e7b23fb428cb5eaddcff58bc36caec8030813cbfcce95b74c95bfc54863b8f5a`, replacing
`5df172565b3b27fe769a87a56f9638e33f25c33c779178d62f0e35a15125d957`. **Review
input only. It was not passed to `--execute` and must not be.**

---

## 1. The defect, reproduced before it was repaired

Codex's finding, in the shape it actually takes. After T1's exclusive `linkat`
succeeds and its `unlinkat` fails, the reservation record's final name and its
temporary are two names for one inode. **The record under the final name is
valid, complete and parses cleanly** — its bytes were synchronized before the
link. `read_and_admit()` re-sealed that record, parsed it, validated it and
surveyed the ledger, and asked nothing about `record.temporary_present()`.

Driving the seven real integration points over that state on the submitted tree:

```text
BOT_SUITE            may_proceed=True  refusals=0
WEB_SUITE            may_proceed=True  refusals=0
FOUNDRY_TESTS        may_proceed=True  refusals=0
SYNCHRONIZATION      may_proceed=True  refusals=0
DEPENDENCY_UPDATE    may_proceed=True  refusals=0
ENVIRONMENT_RESET    may_proceed=True  refusals=0
HARNESS_CLI          may_proceed=True  refusals=0
```

All seven, the harness included. The harness's later refusal is at T7, when its
own publication meets the temporary — by which point six participants have
already been admitted, and the seventh has been admitted and is merely unable to
publish.

**Why the parse could never have caught it.** The finding is a fact about the
record's *name*, not about its history. A reader that only ever consults bytes
cannot distinguish a finished publication from an unfinished one, because the
bytes of the two are identical. That is why the repair is a comparison of two
names and not a stricter parse.

## 2. The repair

### 2.1 One check, on the authoritative path, in the specified order

`lifecycle_storage.read_and_admit()` gains one step between the re-seal and the
parse:

```python
interruption = record.observe_publication_temporary()
refusals.extend(interruption.refusals())
```

* **The existing path, not a second one.** No new admission state machine, no
  second lifecycle reader, no participant-specific branch. `read_and_admit` is
  still the one function `LaboratorySession.admit()` calls for all seven, and
  `ParticipantIntegration.run()` and `run_harness()` still refuse on its result
  before any work is called.
* **The order is preserved exactly.** Lock → re-seal → **comparison** → record
  parse → history order → validator → ledger survey → decide. The comparison
  follows the re-seal because no participant reads before it re-seals, and
  precedes the parse because it is not a statement about the parse. Every
  pre-existing fail-closed condition is untouched: `test_a_failed_re_seal_…`,
  the ten tampered-record cases, the ledger-survey refusals, the absent-ledger
  refusal and the quarantine refusal all still hold, and the suite says so.
* **It appends rather than returning**, so a refusal still reports everything
  else the pass found rather than stopping at the first problem.
* **Nothing is removed, renamed or repaired.** Both names and their bytes are
  byte-identical after every refusal, and row 74 asserts that over the record,
  the temporary and the whole ledger directory.

### 2.2 One comparison object, so an unobserved comparison is not expressible

`DurableRecordStore.observe_publication_temporary()` stats both names once and
returns a `PublicationTemporary`: what each name resolved to, or `None`, or a
failed observation. `temporary_present()` now delegates to it, so there is **one
reader** of a temporary's meaning rather than two that can drift — the property
every finding since R3-1 is about.

It distinguishes r6 §6.2's three states, because their operator recoveries
differ:

| Observed | Refusal says |
|---|---|
| final absent, temporary present | nothing was published; retry from the beginning after the operator removes it |
| **one inode, two names** | §6.2's second state: **published**, not yet durable; remove **only** the temporary; do not repeat the publication |
| two different objects | neither state. **Nothing removes it**; the host stays refused until an operator establishes what it is |
| `fstatat` refused | a failed **observation**, not an absent temporary — §5.9's rule for an unreadable lock, applied here |

The last row is a deliberate fail-closed addition. `temporary_present()` raises
on it rather than returning `False`, because its two callers (`publish` and
`initialize_first_use_record`) are about to *write*, and a writer that read
*absent* from a call that refused would create a temporary over a state nobody
observed.

### 2.3 T1's and T6's operator recovery — the comparison is now the argument

Assignment item 1. r6 §6.2 already said an operator tells the two states apart by
comparing `(st_dev, st_ino)`, and §5.10 already said to remove only the
temporary. **Stated as prose, the comparison is a step an operator can skip.**

`DurableRecordStore.remove_publication_temporary(comparison=…, author=…,
reference=…)` takes the comparison as a required argument. Five refusals, all
before `unlinkat`, and equality is the only admitting branch — the shape
PR-20260913-LABI-2 established for every removal in this package:

| Refusal | When |
|---|---|
| `no_observed_comparison` | `comparison=None`. **This is the whole of the unobserved case** |
| `foreign_comparison` | the comparison is of another record's two names |
| `unattributed` | no author or no reference |
| `identity_mismatch` | the comparison does not show one inode under two names |
| `stale_comparison` | the comparison no longer holds **at the moment of the call**. The names are compared again here, and the presented comparison must still be true — which is what *immediately preceding* means mechanically |

It removes exactly the temporary: never the record, never a republication, never
a repeated initialization, and it settles no run. One implementation serves both
T1 and T6 because `DurableRecordStore` is one publication path for both objects;
`ReservationRecord` and `ParticipantRunLedger` delegate to it and add no rule.

**`unlinkat` is not inode-bound and this does not claim otherwise.** It resolves
its component at the time of the call, exactly as r6 §1.4.5 states for every
removal here. The guard is a detection performed immediately before the call,
not a binding.

**No participant path reaches this.** It is the one attributed exception to
`lifecycle_record`'s standing rule that the module never removes a temporary
another publication left, and the module's docstring now says so rather than
stating a rule the code no longer keeps.

### 2.4 X1's `execveat` route — owner, evidence, stop condition

Assignment item 2, and **no route is chosen or implemented**, as the
authorization requires. r6 §6.4 gains a table giving the item an owner (the
agent Peter designates as Package 5.0's working Technical Lead, under
implementation-plan §0.3), the evidence that would close it, and the condition
that stops execution while it is open. It is stated in code at
`execution.descriptors.UNIMPLEMENTED_EXECUTION_ROUTE` and opened as RAID item
**LAB-X1**.

The required evidence names four things: which call is issued and from where;
whether the one `ctypes` exception would be widened, **which is a separate
approval**; whether the `/proc` fallback is reached deliberately or refused,
since a `/proc`-mediated execution re-resolves a pathname and gives up exactly
the descriptor binding X1 exists for; and §9.3's I7.

The stop condition: while LAB-X1 is open, X1 is not executed,
`plan.is_executable` stays `False`, `reservation.REAL_EXECUTION_REFUSAL` stands
unconditionally, and no `--execute` run is taken on the grounds that the
remaining route is obvious. Both states are asserted, not merely asserted about.

### 2.5 V6 — Peter's approved disposition, incorporated

Assignment item 3. V6 is a **read-only prerequisite survey** of filesystem and
mount type, `fs.protected_hardlinks`, execution identity, ownership and mode
assumptions and relevant capability state. It creates no link. **It does not
prove real `linkat` viability and does not close I3**; a controlled write
verification requires separate authorization before execution.

Incorporated at r6 §7's V6 row and its paragraph — where the previous text's
open *question* is now answered — §9.3's I3, §10's assumption list,
`provisioning.UNCONFIRMED_TARGET_FACTS` and
`descriptors.EXCLUSIVE_PUBLICATION_SUBSTITUTE`. V6 remains unperformed and one
of the twelve unconfirmed target facts.

## 3. Contract changes, by section

All in `phase-5-0-reserved-laboratory-runner-contract-r6.md`, each marked
*amended 2026-09-15, D1 remediation*.

| Section | Change |
|---|---|
| header | dated remediation note: the finding, the repair, the three items and what still is not authorized |
| §5.6 | the reader/writer order gains the name comparison; a new paragraph says why it is a step of its own and cannot be part of the parse |
| §5.7 Table A | T4 now begins with the comparison and refuses all seven before the bytes are read |
| §5.7 Table B | T1's restart column and recovery owner; rows 74–78 cited |
| §5.9 | two refusal rows: a leftover **record**-publication temporary, and a temporary that cannot be observed |
| §5.10 | `interrupted_initialization` requires the immediately preceding comparison; every participant refuses while the temporary is there |
| §6.2 | the per-reader table's T1 and T6 rows name the admission refusal and the required comparison; the *"[P] for every operator recovery"* sentence is corrected — T1's and T6's is now executable and guarded, and §2.5's and P2's remain [P] |
| §6.4 | X1's row cross-references the new owner/evidence/stop-condition table below it |
| §7 | V6's row and paragraph carry Peter's approved disposition; the open question is answered |
| §9.2 | rows **74–79**, with the single-point reversal that catches each and an explicit note that row 75 is caught by none because it is the control |
| §9.3 | I3: V6 observes the prerequisites and does not close it |
| §10 | the V6 assumption; PR-20260915-LAB-D12-1 remediated and **not closed**; LAB-X1 newly open |

## 4. Code changes

| File | Change |
|---|---|
| `lifecycle_storage.py` | new `PublicationTemporary` and its `refusals()`; `DurableRecordStore.observe_publication_temporary()`; `temporary_present()` delegates to it and raises on a failed observation; new `TemporaryRemoval`/`TemporaryRemovalRefusal` and `remove_publication_temporary()`; `read_and_admit` gains the comparison and `SuccessorAdmission` carries it; `FIRST_USE_RECOVERY[interrupted_initialization]` requires the immediately preceding comparison; `RunLedger` gains T6's observe/remove pair; five `__all__` entries |
| `execution/lifecycle_record.py` | `observe_publication_temporary()` and `remove_publication_temporary()` delegations; the module docstring's *"never removes a temporary"* rule now names its one attributed exception |
| `execution/run_ledger.py` | the same two delegations for a run file |
| `execution/descriptors.py` | V6's approved disposition; a statement of the admission repair where a reader of the publication substitute meets it; new `UNIMPLEMENTED_EXECUTION_ROUTE` |
| `provisioning.py` | V6's approved disposition in `UNCONFIRMED_TARGET_FACTS` |
| `tests/phase_5_0_evidence/test_lab_implementation.py` | nine new tests, three helpers, three imports |

**No control flow outside the added checks changed.** No signature was altered,
no refusal reclassified, no schema touched. `COVERED_SOURCES` stays **43**,
`manifest_version` **12**, `evidence_schema_version` **3**, verbs **20**,
`PERMITTED_EXECUTABLES` **20**.

## 5. Evidence

Restricted local pass on this workstation. `TEST_DATABASE_URL` **unset**
throughout. Suites run **serially**. No SSH, synchronization, target inspection,
preflight, provisioning, permission or group change, `systemd-tmpfiles`,
database operation, generated-vector execution, real participant, real
boundary/materializer or `--execute`. Nothing was created under `/run`,
`/var/lib` or `/etc`, and the suite's own guard asserts that against this
module's source.

### 5.1 The new regressions

`tests/phase_5_0_evidence/test_lab_implementation.py`. Rows 70–73 and their
real-filesystem coverage are **retained unchanged**. The helper that reaches
D1's state is the existing `_stop_between_link_and_unlink`, which fails the one
real `unlinkat` after a real `linkat` has succeeded.

| r6 §9.2 row | Test | Against the submitted tree |
|---|---|---|
| 74 | `test_d1_a_record_publication_temporary_refuses_all_seven_before_their_work` | **failed** — all seven admitted; this is §1's reproduction |
| 75 | `test_d1_a_clean_record_with_no_temporary_still_admits_all_seven_control` | passed — the successful control, and it must keep passing |
| 76 | `test_d1_a_temporary_that_is_not_the_record_refuses_and_is_never_removed` | **failed** — the six admitted |
| 77 | `test_d1_a_temporary_whose_resolution_is_unknown_is_not_an_absent_one` | **failed** — the check did not exist |
| 78 | `test_d1_the_t1_recovery_removes_the_temporary_only_on_an_identity_match`, `…_refuses_a_mismatch_and_removes_nothing`, `…_refuses_an_unobserved_comparison`, `…_refuses_a_comparison_that_no_longer_holds` | **failed** — `remove_publication_temporary` did not exist |
| 79 | `test_d1_the_t6_recovery_uses_the_same_guard_and_settles_nothing` | **failed** — same |
| — | `test_the_unimplemented_execveat_route_has_an_owner_and_a_stop_condition` | **failed** — the item had no owner |

Row 74 proves, in one test, each thing the assignment required: the two names
remain and identify one inode; every member of `Participant` refuses; the work
callback is never called; the refusal is the `SuccessorAdmission` the one
admission path produced, carrying its comparison, with the re-seal still
discharged; and the record's bytes, the temporary and every file in the ledger
directory are byte-identical afterwards.

### 5.2 Single-point reversals

Each removes exactly one conjunct from `lifecycle_storage.py`, runs the D1 tests
**unchanged**, restores the file's bytes and verifies its SHA-256. A fresh
`PYTHONPYCACHEPREFIX` per run and an `mtime` touch, because a same-size edit
restored within one second is otherwise served from a stale `.pyc` — the
measurement defect the previous handback disclosed, avoided here by construction.

| # | Removed | Result | Failing regression(s) |
|---|---|---|---|
| RV-admit-temporary | `read_and_admit` stops checking the record's publication temporary | 3 failed | rows **74**, 76, 77 |
| RV-admit-failclosed | a failed observation is read as an absent temporary | 1 failed | row 77 |
| RV-recovery-unobserved | the recovery accepts a removal that compared nothing | 2 failed | rows 78, 79 |
| RV-recovery-identity | the recovery stops requiring the two names to be one inode | 1 failed | row 78 |
| RV-recovery-stale | the comparison no longer has to be the immediately preceding one | 1 failed | row 78 |
| RV-recovery-attribution | the recovery no longer names who performed it | 1 failed | row 78 |

Baseline and final control: **13 passed** (the nine new tests plus rows 70–73).
Every source hash verified restored after each run.

**RV-admit-temporary is the reversal that catches the new admission case**, and
it is the one r6 §9.2 names. **Row 75 is caught by no reversal and must not be**:
a control that failed when a refusal was removed would be testing the refusal
rather than controlling for it.

### 5.3 Suites on the submitted tree

| Command | Result |
|---|---|
| `env -u TEST_DATABASE_URL …/runtime/venv-web/bin/python -m pytest -q -p no:randomly tests/phase_5_0_evidence/test_lab_implementation.py tests/phase_5_0_evidence/test_no_execution.py` | **371 passed** |
| `… -q -rsfE tests/phase_5_0_evidence` | **2 239 passed, 0 failed, 0 skipped**, 2 warnings |
| bot: `env -u TEST_DATABASE_URL /opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py` | **3 025 passed, 326 skipped**, 1 warning |
| web: `env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rsfE tests/web` | **1 609 passed, 1 failed, 1 362 skipped** |
| `node --test foundry-module/tests/*.test.mjs` | **171 passed, 0 failed, 0 skipped** |
| `python3 .claude/hooks/test_guards.py` | **31 cases, all passed** (19 refused, 12 allowed) |
| `python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | succeeded |
| `git diff --check` | clean |

The evidence suite was **2 229 passed** before this pass, which is Codex's own
figure on the submitted tree; the ten new tests take it to 2 239.

**Every skip is unverified, and none of it is PostgreSQL evidence.** All 326 bot
skips and all 1 362 web skips report *"TEST_DATABASE_URL is not configured for a
disposable PostgreSQL database."* The database-enabled web baseline is **80**,
and these runs exit 0 without the variable. The authorization permits local tests
with `TEST_DATABASE_URL` unset only, so the 80-skip run **was not performed** and
is reported as not run rather than inferred.

**The web failure is the pre-existing one**, unchanged and unrelated:
`test_p3_4_static_assets.py::test_the_discovery_enumerates_untracked_files_rather_than_directories`
fails on its own guard, *"no untracked directory in this tree; this test proves
nothing"*. This work created no untracked **directory**: `git status` lists
eleven modified files and one new untracked file, this handback.

**Interpreters.** `/opt/freedom-blades/runtime/venv-web/bin/python` (Python
3.12.3, pytest 9.1.1) for the evidence suite, matching the interpreter Codex's
re-review used; `/opt/discord-bots/venv-web/bin/python` and
`/opt/discord-bots/venv/bin/python` (Python 3.12.3, pytest 8.4.2) for the web and
bot suites, matching the previous handback's; node v24.20.0. **These are
available local runners on this workstation, not canonical-environment
evidence.** `.agents/AGENTS.md` names `/opt/freedom-blades/runtime/venv-web/bin/python`
**on `oracle-test`**, and a path existing here establishes nothing about there.

**No formatter, linter or type checker is configured** in this repository, so
none was run. That is a statement about the repository, not a check skipped.

### 5.4 Generated artifacts and the review-only digest

Five covered sources changed, so the artifacts were regenerated — through the
**non-executing** CLI only:

```text
python -m tools.phase_5_0_evidence.execution.cli --manifest-out <scratch>/genN/manifest.json --render <scratch>/genN/plan.md
```

No `--execute`, no `--confirm-target`, no `--reviewed-digest`.

* Generations 1, 2 and 3 are **byte-identical**: manifest
  `0d321b2b…c178`, plan `44979f45…2cea`. Generation 1 was installed and
  generation 3 was compared against the installed files byte for byte.
* `COVERED_SOURCES` is **43** paths, equal to the manifest's path set. All 43
  hashes recomputed from disk: **zero mismatches**.
* Exactly **five** `source_digests` entries changed — the five files of §4.
  Every other manifest field is identical to the previous one.
* The installed plan differs from the previous one in **one line**, its digest.
* Dry run: `executable : False`; `unresolved conflicts : 3 (C-7)`; twelve
  unconfirmed facts listed, each refusing the executor before any command starts.

**The digest is review input only. Do not pass it to `--execute`.**

## 6. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-reserved-laboratory-runner-contract-r6.md` | §3 |
| `docs/project-management/raid-register.md` | a dated entry; LAB-X1 opened |
| `tools/phase_5_0_evidence/lifecycle_storage.py`, `execution/lifecycle_record.py`, `execution/run_ledger.py`, `execution/descriptors.py`, `provisioning.py` | §4 |
| `tests/phase_5_0_evidence/test_lab_implementation.py` | nine tests, three helpers, three imports |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json`, `…-concrete-plan.md` | regenerated (§5.4) |
| `docs/review/Handover information` | a dated entry at the top |
| this handback | new |

No migration, no configuration change, no deployment change. `status.md`, the
decision register, implementation-plan §20 and the change log are **not edited**:
they record Peter's decisions and are the maintainer's to update on disposition.

## 7. Security, interruption and residual observations

* **The repair strictly narrows what admits.** It adds refusals and removes
  none. Every refusal the pre-existing regressions exercise still holds, and
  the 2 239-test suite includes all of them.
* **One new mutating operation exists in this package**, and it is
  `remove_publication_temporary`. It is an operator recovery, no participant
  path reaches it, it removes exactly one name, it issues no barrier — the next
  re-seal covers the directory entry — and it settles nothing. Its five refusals
  each have a test and a reversal.
* **`unlinkat` is not bindable to a previously observed inode.** The guard is a
  detection immediately before the call, as r6 §1.4.5 states for every removal
  in this design. A substitution in the window between the confirmation and the
  call is not prevented and is not claimed to be.
* **Not established here:** anything about `oracle-test`. `tmp_path` is tmpfs or
  ext4 on this workstation; that a `linkat` and an `unlinkat` behave here says
  nothing about V6, V8, I3 or any of the twelve facts.
* **Not modelled:** `durability_model.py` still models an atomic exclusive
  rename and its `MODEL_LIMITS` still names `RENAME_NOREPLACE`, so D1's second
  state is not reachable in the synthetic model. Rows 70–79 cover it on real
  files instead. Changing the model remains a separate slice, unchanged from the
  previous handback.
* **Pre-existing discrepancy, not changed:** §2.3.2's barrier row 2 says a P2
  data-barrier failure removes the temporary; `install_case_program` closes the
  descriptor and raises instead. It predates D1 and is outside this remediation.
* **The six non-harness participants are still not wired** to anything outside
  this repository, and this authorization forbids invoking a real participant.
  LAB-R6 records why wiring must not precede provisioning.

## 8. Rollback

Repository-only. Nothing was deployed, provisioned or applied, and no host was
touched.

1. Delete this handback and the top entry of `docs/review/Handover information`.
2. `git checkout --` the eleven modified files, which restores every one to the
   committed tree. The previous artifacts are also copied in the session
   scratchpad under `before/`.
3. The digest returns to `5df17256…5957`.

There is no data change, no migration and no recovery step: the only
operator-visible behaviour added is a refusal, and reverting it restores the
admission Codex found defective.

## 9. Questions for Codex

1. **The comparison's placement.** It follows the re-seal and precedes the
   parse. Placing it after the parse would report the record's own state first
   and the interruption second; placing it before the re-seal would read before
   re-sealing, which is revision 3. Is between the two right?
2. **The stale check.** *Immediately preceding* is implemented as *the presented
   comparison must still hold when the call is made*, re-observed inside the
   removal. Is that the intended reading, or should the recovery instead refuse
   any comparison not produced within the same held lock?
3. **The removal's barrier.** It issues none, on the argument that the next
   participant's re-seal covers the directory entry exactly as it covers the
   publication being recovered. Is that right, or should an operator recovery
   `fsync` the containing directory itself?
4. **LAB-X1's owner.** It is written as *Package 5.0's working Technical Lead*
   rather than as a named person, because implementation-plan §0.3 says Peter
   designates that role per package. Is a role the right granularity, or should
   the item name whoever holds it today?
5. **Row 75.** It is deliberately caught by no reversal. Is stating that
   explicitly in §9.2 the right treatment of a control, or should controls be
   listed separately from the proof rows?

---

**Stop point.** The next checkpoint is independent Codex technical and security
re-review of this remediation. **The implementer closes no finding, approves no
digest and advances no gate.** PR-20260915-LAB-D12-1 remains Open until that
review says otherwise. The authorized read-only target preflight remains queued
behind it and Peter's release. No preflight, provisioning, wiring, database
operation, generated-vector execution or execution follows automatically from
anything here.
