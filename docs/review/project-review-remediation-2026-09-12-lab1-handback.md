# LAB-1 run-record binding remediation — handback, 2026-09-12

Direction: C-P5.0-LAB-1, reserved disposable laboratory.
Assignment: [bounded remediation prompt](project-review-remediation-2026-09-12-lab1-claude-prompt.md).
Finding answered: **PR-20260912-LAB1-1**, from the
[Codex re-review](project-review-2026-09-12-lab1-rereview.md).

**This is a return to Codex for independent technical re-review. It closes
nothing.** LAB-1 is not closed, Package 5.0 is not ready, and no execution is
authorized. The session that implemented this correction does not dispose of the
finding it answers.

---

## 1. Disposition and traceability

| Finding | Classification | Disposition in this pass |
|---|---|---|
| PR-20260912-LAB1-1 — the run-record reader accepts a substituted recovery procedure | Important | **Repaired in pure code**, with the reviewer's own reproduction as a failing-before regression, a fourteen-row substitution and cause/presence matrix, and two negative controls |

The reviewer's required correction, clause by clause, and where each is answered:

| Required | Where |
|---|---|
| exact equality with the residue procedure serialized from the outcome | `write_run_record`'s whole-document read-back comparison, `_read_back_matches` |
| the canonical five-step procedure when residue is present, empty when absent | `validate_run_record`, via `_matches_canonical` against `CANONICAL_RESIDUE_RECOVERY` |
| negative regressions for changed action/rationale, a shorter ordered list, an arbitrary ordered replacement, a procedure without residue, residue without the procedure | `tests/phase_5_0_evidence/test_r13_remediation.py`, §3 below |
| the same binding for the configuration recovery and its retained-capture cause | `validate_run_record`, against `CANONICAL_CONFIGURATION_RECOVERY` |

**Scope kept.** The cleanup state machine, the observation importer, the
reservation lifecycle and the laboratory architecture are unchanged. The
accepted separation of residue recovery from configuration recovery is preserved
exactly as the disposition records it; this pass binds the run record to it and
changes nothing about what `classify_cleanup` produces.

---

## 2. Failing-before, and passing-after

**Measured against the submitted LAB-1 tree, before any source was edited.** The
tree was neither discarded nor modified to obtain the comparison: the two
reproduction tests were appended to the existing focused module and run while
`tools/` still carried the submitted implementation.

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
  tests/phase_5_0_evidence/test_r13_remediation.py \
  -k "substituted_residue_procedure or reproduction_holds_for_a_record_with_no_steps"

E  Failed: DID NOT RAISE <class '…artifact.RunRecordRefused'>
2 failed, 56 deselected in 0.16s
```

Both are the re-review's reproduction: a schema-2 S-B record whose five-step
residue recovery is replaced by

```text
{order: 1, action: "IGNORE THE RESIDUE AND CONTINUE",
 rationale: "arbitrary replacement"}
```

was **accepted** — once against the record's own step count, and once with
`expected_steps=0`, which is the form the reviewer ran. After the correction both
refuse, and the whole module passes: **93 passed**.

---

## 3. What the repair binds, and how

One module changed: `tools/phase_5_0_evidence/execution/artifact.py`.

### 3.1 Content bound to cause — independent validation

`validate_run_record` now enforces the cleanup contract **from the bytes alone**,
with no reference to the outcome they came from:

* residue present ⇒ the residue procedure must equal `journal.RECOVERY_PROCEDURE`
  exactly — every `order`, `action` and `rationale` compared with the canonical
  value;
* residue absent ⇒ the residue procedure must be empty;
* retained recovery inputs present ⇒ the configuration procedure must equal
  `cleanup.RECOVERY_PROCEDURE` exactly;
* no retained inputs ⇒ the configuration procedure must be empty.

The two causes are independent and **neither answers for the other**: a record
that leaves residue and carries only the (perfectly canonical) configuration
procedure is refused, and so is its mirror. That is LAB-1's own clause, applied
in the reader rather than only in the classifier.

**What it deliberately is not.** Not `bool(procedure)`, not a length check, not a
consecutive-order check, and not a digest supplied by the same untrusted record.
Each of those is satisfied by a well-shaped substitute, which is exactly what was
reproduced. The comparison lives in one named function, `_matches_canonical`, so
that weakening it is a visible edit rather than a condition quietly dropped from a
longer predicate.

**Keys are refused, not ignored.** A recovery step must carry exactly
`{order, action, rationale}`; the document must carry exactly the ten keys
`build_run_record` emits, and `cleanup` exactly its ten. A missing or unknown key
is a refusal — a reader that skips an unexpected field cannot say what the field
meant. `DOCUMENT_FIELDS` and `CLEANUP_FIELDS` are pinned to the encoder's output
by a test, so a field added to the record and not to the validated set fails the
suite rather than travelling unchecked.

**The canonical values are derived, not restated.**
`CANONICAL_RESIDUE_RECOVERY` and `CANONICAL_CONFIGURATION_RECOVERY` are built
from `journal.RECOVERY_PROCEDURE` and `cleanup.RECOVERY_PROCEDURE`, so the
document contract cannot drift from the procedure an operator is actually given.
A test asserts that derivation.

### 3.2 The whole-document read-back comparison

`write_run_record` compares the document read from disk with the document
serialized from the supplied outcome — mapping equality **and** the re-serialized
bytes under the same canonical settings. The byte half is not decoration: it
separates `true` from `1`, which mapping equality would accept, and one matrix row
exercises precisely that.

*Read back whole* previously meant *read back and found structurally plausible*.
It now means the bytes are the ones that were written, so a partial flush or a
substituted-but-well-shaped value in any emitted field is refused **whatever
`expected_steps` matches**. That comparison is likewise one named function,
`_read_back_matches`.

**Error messages stay safe and bounded.** Every refusal is a fixed string naming
the property that failed. No path, no read value and no hostile content is
serialized, and the CLI's `_write_run_record` still returns `no — <fixed reason>`.

---

## 4. Schema and compatibility consequences

**The run-record schema is version 3.** Under version 2 an arbitrary ordered
procedure was a *valid* record; under version 3 it is not. Those are incompatible
meanings of one field, so the version moves rather than widening: a version-2
document is refused by name as another schema and is never reinterpreted under
either reading. A regression asserts that refusal.

**Consumers updated coherently.** The run record has exactly two consumers:
`execution/cli.py`, which calls `write_run_record` and is unaffected by the
version number, and the focused regressions, whose version assertion is now
pinned to `RUN_RECORD_SCHEMA_VERSION` rather than to the literal `2`.

**What did *not* change, and why.**

| Contract | Version | Why unchanged |
|---|---|---|
| supplied-observation schema | **3** | the classifier's per-cause clause is untouched by this pass |
| review manifest | **10** | the manifest declares the plan, the exit classifications, the observation schema and the covered-source digests. It does not declare the run-record document contract, so no covered-contract change occurred. Only `artifact.py`'s pinned hash moved |
| `EVIDENCE_SCHEMA_VERSION` | unchanged | a different document again |

The run record is **not** the classified evidence artifact, and raising its
version says nothing about Band 7, C-7 or coverage.

---

## 5. Regression matrix and negative controls

All in `tests/phase_5_0_evidence/test_r13_remediation.py`, in a new
`PR-20260912-LAB1-1` section. **37 new test nodes**; the module is **93 passed**.

| # | Case | Result |
|---|---|---|
| 1 | arbitrary one-step replacement (the reviewer's reproduction) | refused |
| 2 | the same at `expected_steps=0` | refused |
| 3 | changed action text, canonical order and length | refused |
| 4 | changed rationale text | refused |
| 5 | shorter but consecutively ordered procedure | refused |
| 6 | one additional ordered step | refused |
| 7 | residue present, residue procedure empty | refused |
| 8 | residue present, residue-procedure field missing | refused |
| 9 | residue absent, canonical residue procedure present | refused |
| 10 | reordered steps — the preserved version-2 case | still refused |
| 11 | retained captures, configuration procedure empty / changed / shorter / replaced by the residue procedure | refused (four rows) |
| 12 | retained captures, configuration-procedure field missing | refused |
| 13 | no retained captures, configuration procedure present | refused |
| 14 | residue present with only the canonical *configuration* procedure, and its mirror | both refused |
| 15 | residue alone with only its exact procedure | **accepted** |
| 16 | configuration recovery alone with only its exact procedure | **accepted** |
| 17 | both causes with both exact procedures | **accepted** |
| 18 | neither cause, both procedures empty | **accepted** |
| 19 | any other emitted scalar or list substituted on read-back — target identity, manifest digest, stop reason, completed flag, mutations reached, cleanup exit code, exit code written as a boolean, preserved list, configuration risk | refused (nine rows) |
| 20 | partially flushed file | refused |
| 21 | a version-2 document | refused by version |
| 22 | the validated key sets equal what the encoder emits | asserted |
| 23 | the canonical values equal `journal`'s and `cleanup`'s procedures | asserted |

Rows 15–18 go through the **public write/read-back function**, not only the
reader: `write_run_record` to a real file, then `validate_run_record` on the bytes
read back. Rows 19–20 also go through it, using a destination that writes
faithfully and returns different bytes — the only way to produce a substituted
read-back, since the writer serializes what it compares.

**A limit stated rather than implied.** `RunOutcome.artifact_admissible` requires
`S-C`, so a real S-B run never reaches `write_run_record` at all. The populated
recovery forms are therefore constructed the way the existing version-2
round-trip test constructs them — a real run outcome with its cleanup fields
replaced. The validator is nonetheless the contract for any document read back,
which is the surface the finding is about.

### 5.1 Negative controls

Two, one per comparison, each asserting that the regression disappears when the
function it rests on is hardcoded:

* `test_gutting_the_canonical_comparison_makes_the_regression_fail` — with
  `_matches_canonical` returning `True`, the reviewer's reproduction is accepted
  again;
* `test_gutting_the_read_back_comparison_makes_the_regression_fail` — with
  `_read_back_matches` returning `True`, a substituted read-back is accepted
  again.

### 5.2 Reversal on a scratch copy

The submitted tree was neither modified nor discarded. A scratch tree symlinks
every top-level entry and replaces `tools/` with a real copy, in which the repair
is reversed: the version back to 2, both comparisons hardcoded to `True`, and the
two key-set checks removed.

```text
cd <scratch>
env -u TEST_DATABASE_URL PYTHONPATH=<scratch> \
  /opt/discord-bots/venv-web/bin/python -m pytest -q tests/phase_5_0_evidence
  26 failed, 1882 passed in 9.73s
```

**25 of the 37 new nodes fail**, the reviewer's reproduction among them, plus one
preserved test whose version assertion moved. The **12 that still pass are named
rather than glossed**: the reordered-step case and the partial-flush case are
version-2 behaviour the reversal leaves in place; the two presence clauses
(a procedure without its cause) are guarded by branches the reversal does not
touch; the four accepted cause combinations are positive controls that must hold
under both revisions; the two key-set/canonical-derivation assertions pin
constants; and the two gutting controls assert acceptance under gutting, which a
reversed tree already provides.

---

## 6. Files changed, security and operational implications, rollback

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/execution/artifact.py` | schema version 3; canonical residue/configuration procedures derived from their owners; document and cleanup key sets; `_matches_canonical`, `_read_back_matches`, `_residue_procedure`, `_configuration_procedure`, `_string_list`; cause-bound validation; whole-document read-back comparison; named fixed refusal strings |
| `tests/phase_5_0_evidence/test_r13_remediation.py` | the failing-before reproduction, the matrix above and the two negative controls; the existing version assertion re-pinned to the constant |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | regenerated — `artifact.py` is a covered source |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | regenerated for the same reason |
| `docs/review/project-review-remediation-2026-09-12-lab1-handback.md` | this document |
| `docs/review/project-review-2026-09-12-lab1-disposition.md` | dated correction appended; the original text preserved |
| `docs/review/phase-5-0-reserved-laboratory-runner-contract-r6.md` | third dated follow-up in §8; proposal text preserved |
| `docs/review/Handover information`, `docs/implementation-plan.md` §20, `docs/project-management/status.md` | action pointer and status, with the prior entries kept as history |

**Security and operational implications: none reachable.** This tier plans and
classifies; `artifact.py` writes one reviewed file and is not armed. The change
makes a reader **stricter**, so its only behavioural effect is that documents
previously accepted are now refused. It opens no operation, relaxes no gate, adds
no capability, reads no host, touches no credential and makes nothing executable.
The new imports are planning-tier modules (`..journal`, `..cleanup`); the
execution-tier scans in `test_no_execution.py` pass unchanged — **217 passed**.

**Rollback.** Revert the two source files and regenerate the manifest and plan
through the non-executing CLI. There is no migration, no persistent state and no
deployed artifact: nothing has been executed, and no run record exists anywhere.

---

## 7. Commands, interpreters, exact results

**Restricted local pass.** The canonical environment remains
`/opt/freedom-blades/runtime/venv-web/bin/python` on `oracle-test`. The active
restriction forbids SSH, synchronization and host inspection, so the historical
local interpreters were used as the restricted-pass exception, verified before
use. `/opt/freedom-blades/runtime/venv-web/bin/python` **exists on this host and
has no `pytest`** — the maintainer's separately authorized installation was on
`oracle-test`, which this pass may not reach. `TEST_DATABASE_URL` was **unset
throughout** (`env -u`). Bot and web ran **serially**, in that order, because they
share one disposable database.

* `/opt/discord-bots/venv-web/bin/python` — Python 3.12.3, pytest 8.4.2
* `/opt/discord-bots/venv/bin/python` — Python 3.12.3, pytest 8.4.2
* `node` — v24.20.0

| Command | Result |
|---|---|
| `pytest -q -rs tests/phase_5_0_evidence/test_r13_remediation.py` | **93 passed** |
| `pytest -q -rs …/test_feasibility.py …/test_plan_and_cleanup.py …/test_r13_remediation.py` | **232 passed** |
| `pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py` | **217 passed** |
| `pytest -q -rs tests/phase_5_0_evidence` | **1908 passed**, zero skips |
| `pytest -q -rs tests/test_*.py` (bot, `venv`) | **3018 passed, 326 skipped** |
| `pytest -q -rs tests/web` (web, `venv-web`) | **1609 passed, 1 failed, 1362 skipped** |
| `node --test 'foundry-module/tests/'*.test.mjs` | **171 passed**, 0 failed, 0 skipped |
| `git diff --check` | passed |
| `compileall` on the two changed Python files | ok |

Every figure was produced against the tree being submitted, **after** the
generated artifacts were replaced. The complete harness is **1908** because 37
nodes were added to 1871.

**Every skip is unverified.** The web suite's **1362** skips are what a
database-disabled run produces; the documented database-enabled baseline is
**80**. The bot suite's **326** skips have the same cause —
`TEST_DATABASE_URL is not configured for a disposable PostgreSQL database` is the
printed reason on both. Nothing in the skipped set was verified by this pass.

**The one web failure is pre-existing and unrelated.**
`tests/web/test_p3_4_static_assets.py::test_the_discovery_enumerates_untracked_files_rather_than_directories`
fails on its own final assertion, `no untracked directory in this tree; this test
proves nothing`. Its docstring still says `tools/phase_5_0_evidence/` is untracked
here; that directory was committed in `5b0d1f2`, so the premise is stale and the
result depends on incidental working-tree state rather than on the behaviour the
test names. This change adds no untracked file. It was reported the same way by
the previous pass and is **reported here, not fixed here**.

**Checks not run, and why:**

| Check | Why |
|---|---|
| formatter, linter, type checker | **not configured and not installed.** No `pyproject.toml`, `setup.cfg`, `tox.ini`, `.flake8`, `.ruff.toml` or `mypy.ini`, and neither interpreter has `ruff`, `flake8`, `black`, `mypy`, `pylint` or `pyflakes`. **Unavailable tooling, not a pass** |
| database-marked tests | `TEST_DATABASE_URL` kept unset by the restriction |
| anything on `oracle-test` | no SSH, synchronization, host inspection, preflight, permission change, provisioning, dependency operation, service change or environment reset is authorized. The separately completed pytest installation broadens none of this |
| the read-only target preflight, V6, V8, V10's actual identity | follow implementation review; neither performed nor expanded here |
| any real execution | `--execute`, an armed boundary or materializer, and generated-vector execution are all refused. The bot was not restarted |

---

## 8. Generated-artifact integrity and the review-only digest

Covered source changed — `tools/phase_5_0_evidence/execution/artifact.py` is in
`COVERED_SOURCES` — so both derived artifacts were regenerated through the
**non-executing** CLI.

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python \
  -m tools.phase_5_0_evidence.execution.cli --manifest-out <temporary> --render <temporary>
```

* Generated **twice to temporary paths**; both generations byte-identical.
* All **36** covered-source SHA-256 hashes recomputed independently with
  `hashlib`, against `COVERED_SOURCES` read through the AST rather than imported:
  **exact set equality, no mismatch**.
* The installed artifacts were **replaced with the generated output**, never
  hand-edited, and a **third** generation was compared with the installed files
  byte-for-byte: identical.
* Coverage and schema unchanged: still 36 sources, manifest schema
  `phase-5-0-evidence-review-manifest`, `manifest_version` **10**,
  `evidence_schema_version` **3**. Only `artifact.py`'s hash moved, because only
  it changed among the covered set.

| Artifact | SHA-256 |
|---|---|
| `phase-5-0-evidence-harness-review-manifest.json` | `1309462d8679fc0a3c1539ad90d26d6c008948422119facfe94c27b6218e62ca` |
| `phase-5-0-evidence-harness-concrete-plan.md` | `eb144f75bd7eabf8df805d47c3b3a1b644c968b9d4fd1f36b566c87096b42edb` |

**New review-input digest, review input only — do not pass it to `--execute`:**

```text
3b50e8f7adb309549aa1e69a61e9ddce1ce5bf11429eecc002f427b773df98a3
```

It replaces `af3181ed276f61a89a51b25afcbfb91f7a4c938b21a5bf83c1ff53f8b3764821`,
which described the pre-repair tree and is now evidence about a state that no
longer exists. **No digest was passed to `--execute` at any point.**

---

## 9. Preserved behavior

Confirmed against the submitted tree, not assumed:

* supplied-observation schema **version 3** and its separate cause/procedure
  fields — unchanged;
* review-manifest **version 10** — unchanged; no covered contract the manifest
  declares was altered;
* the operator-facing S-B message naming each applicable recovery — unchanged;
* all R3/R4/R5 lifecycle fixes, the reservation binding and the terminal
  publication order — unchanged; the complete harness is green;
* all unresolved C-7 cases and the twelve target-fact refusals — unchanged;
  `build_concrete_plan().conflicts()` is still `('C-7',)`;
* `is_executable` is **False**; EH-R16-1 remains **Open**; Package 5.0 remains
  **not ready**; package-level P5.0-R5 remains **Blocking**; OD-62 remains
  **Open**.

Historical statements in the disposition note and runner contract r6 were
**preserved and dated-corrected**, not rewritten.

---

## 10. Assumptions, unresolved questions and reviewer focus

Stated as assumptions, not as findings:

1. **The review manifest stays at version 10.** The manifest declares the plan,
   the exit classifications, the supplied-observation schema and the covered-
   source digests. It does not declare the run-record document contract, so a
   run-record version change is not a covered-contract change and only
   `artifact.py`'s pinned hash moved. If the reviewer reads the manifest's
   contract more broadly, the version is the thing to challenge.
2. **Validation is keyed on cause, not on state.** Residue and retained recovery
   inputs decide which procedure is required, exactly as `classify_cleanup`
   derives them. The record's `cleanup.state` is not additionally required to be
   `S-B` when residue is present. That keeps one authority for the requirement
   instead of two that can disagree.
3. **Key-set strictness was applied to the whole document**, not only to the
   recovery steps: the document must carry exactly the ten keys the encoder emits
   and `cleanup` exactly its ten. This is a reading of *"the whole of what the run
   produced"*; it is stricter than the finding strictly required.
4. **A real S-B run cannot reach `write_run_record`** because
   `artifact_admissible` requires `S-C`. The populated recovery forms are
   therefore exercised through synthetically constructed outcomes and through
   direct validation. Whether the admissibility rule should itself change is a
   separate question and was **not** touched here.

**Proposed reviewer focus areas:**

* the run-record version decision, and whether refusing a version-2 document by
  name is the right compatibility behaviour for a document nothing has yet
  emitted in production;
* the two comparison seams — whether `_matches_canonical` and
  `_read_back_matches` are genuinely the load-bearing functions, and whether the
  negative controls constrain them rather than something adjacent;
* the cause/procedure independence in the reader against r6 §8.1's clause, and
  whether the classifier and the reader can still disagree anywhere;
* assumption 2 above, and the 12 new nodes that survive the reversal in §5.2;
* the manifest-version judgement in assumption 1.

**Nothing here is proposed-but-unimplemented.** The whole of PR-20260912-LAB1-1's
required correction is implemented in code; no part of it is carried as a design
proposal.

---

## 11. Remaining gates and the next checkpoint

**Next action: Codex independent technical re-review** of this run-record binding
correction and of the run-record schema version change it entails.

Still open, and not advanced by this pass:

* **LAB-1 is not closed.** PR-20260912-LAB1-1 is answered, not disposed of;
* C-7 unresolved; EH-R16-1 Open; `is_executable` **False**; twelve target facts
  unconfirmed;
* Package 5.0 **not ready**; package-level P5.0-R5 **Blocking**; OD-62 **Open**;
* V6, V8 and V10's actual-identity preflight fact unperformed; none of the
  ten-item r6 §7 delta provisioned;
* the first privileged execution remains prohibited, and the real-execution
  refusal is retained while EH-R16-1 is open.

Phase 5 product work and every operational gate remain deferred. Any later
preflight, provisioning or host action needs an updated handover that explicitly
permits it and must satisfy its own review and execution gates.
