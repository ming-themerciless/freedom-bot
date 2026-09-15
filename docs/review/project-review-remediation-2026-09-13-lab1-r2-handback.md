# Claude handback — LAB-1 raw read-back byte binding, R2 remediation

Date: 2026-09-13. Direction: C-P5.0-LAB-1, reserved disposable laboratory.
Assignment: [2026-09-13 raw read-back byte binding prompt](project-review-remediation-2026-09-13-lab1-r2-claude-prompt.md).
Review answered: [Codex R2 re-review](project-review-2026-09-12-lab1-rereview-r2.md).
Submission reviewed there: [2026-09-12 handback](project-review-remediation-2026-09-12-lab1-handback.md).

**Returned to Codex for independent technical re-review. LAB-1 is not closed
here, Package 5.0 is not ready, and no execution is authorized.**

---

## 1. Disposition and traceability

| Finding | Classification | Disposition |
|---|---|---|
| **PR-20260912-LAB1-2** — raw substituted read-back bytes are accepted | Important | **Repaired in code**, reproduced first, regression-covered, negative-controlled. Disposition is Codex's, not this session's |

| The re-review required | Where it is |
|---|---|
| retain the raw bytes `destination.read_bytes()` returns | `execution/artifact.py::write_run_record`, local `raw` |
| require exact byte equality with `serialized` | `_read_back_matches`'s first conjunct, `raw == serialized` |
| before or alongside parsing and schema validation | ordered read → decode/parse → `_read_back_matches` → `validate_run_record` |
| public-writer regression for changed whitespace | `test_read_back_bytes_that_are_not_the_bytes_written_are_refused`, five whitespace rows, plus the named reproduction |
| public-writer regression for a duplicate key resolving to the same value | four duplicate-member rows, plus the named reproduction |
| a negative control that fails when the raw comparison is gutted | `test_reversing_only_the_raw_byte_conjunct_accepts_every_collapsing_tamper`, ten rows |
| keep fixed refusal messages | `NOT_THE_DOCUMENT_WRITTEN`, unchanged string, unchanged use |
| keep the existing canonical cause/content checks | `validate_run_record` untouched; its 37-node matrix still green |

---

## 2. What was wrong, exactly

`write_run_record` read the destination and consumed the bytes in the same
expression:

```python
written = json.loads(destination.read_bytes().decode("utf-8"))
```

The bytes had no name after that line, so the comparison that followed could not
receive them. `_read_back_matches(written, document, serialized)` compared the
parsed **mapping** with the emitted document, and a **fresh canonical
re-serialization of that mapping** with the emitted bytes. Both are statements
about what a reader made of the file. Neither is a statement about the file.

So every difference JSON parsing collapses was accepted, and the module's own
documented claim — *"the read-back is the document that was written, whole"* —
was not established. The two independent reproductions the re-review names were
confirmed here before anything was changed.

The duplicate-member case is the material one. `json.loads` keeps the last
occurrence of a repeated name and raises nothing, but RFC 8259 leaves duplicate
handling to the implementation, so such a file has no single agreed meaning while
this writer asserts it is exactly the document serialized from the outcome.

---

## 3. Failing-before, on the submitted tree

The regressions were added first and run while `tools/` still carried the
submitted implementation. Nothing was discarded, reverted or rewritten to obtain
the comparison; the snapshot of the submitted `artifact.py` used later for the
reversal control has SHA-256
`93b58e215181051be7d4edd2084eda5c088f58cc41e1d450413fd383835d62e2`.

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python \
  -m pytest -q tests/phase_5_0_evidence/test_r13_remediation.py
12 failed, 98 passed
```

All twelve failed with `Failed: DID NOT RAISE <class RunRecordRefused>` — the
writer returned a path for bytes it had not written:

| Reproduction | Before | After |
|---|---|---|
| `read_back = b"\n" + serialized + b"\n"` | accepted | refused |
| `read_back = serialized` with a duplicate `schema_version=3` | accepted | refused |
| leading newline / trailing newline / trailing spaces / mixed leading whitespace | accepted | refused |
| a different indent, same document | accepted | refused |
| duplicate `document_type`, same value | accepted | refused |
| duplicate nested `cleanup.state`, same value | accepted | refused |
| duplicate nested `cleanup.exit_code`, same value | accepted | refused |

Each regression additionally asserts, on the bytes the destination actually
handed back, that they **differ** from the bytes written and that they **parse to
the same mapping**. That pair is the whole finding: it is why mapping equality and
canonical re-serialization cannot refuse these files, and why only a comparison
holding the raw bytes can.

The duplicate-key reproduction states it exhaustively — on the tampered bytes it
asserts two `"schema_version"` members are present, that the parse yields
`schema_version == 3`, that the parsed mapping equals the written mapping, that
the canonical re-serialization equals the written bytes, and that
`validate_run_record` **passes** — and then requires the writer to refuse anyway.

---

## 4. The correction

One module, `tools/phase_5_0_evidence/execution/artifact.py`. The executable
change is 4 lines of behavior across two functions.

```python
    try:
        destination.write_bytes(serialized)
        raw = destination.read_bytes()          # retained, not consumed
    except OSError as failure:
        raise RunRecordRefused(
            "the run record could not be written or read back"
        ) from failure
    try:
        written = json.loads(raw.decode("utf-8"))
    except ValueError as failure:
        raise RunRecordRefused(NOT_THE_DOCUMENT_WRITTEN) from failure
    if not _read_back_matches(raw, written, document, serialized):
        raise RunRecordRefused(NOT_THE_DOCUMENT_WRITTEN)
    validate_run_record(written, expected_steps=len(outcome.steps))
    return destination
```

```python
def _read_back_matches(
    raw: bytes, written: Any, document: Mapping[str, Any], serialized: bytes
) -> bool:
    return (
        raw == serialized
        and written == document
        and json.dumps(written, indent=2, sort_keys=True).encode("utf-8") == serialized
    )
```

**The comparison and its ordering.** There is **one** named comparison and the
raw bytes are one of its inputs, so weakening the binding is a single visible
edit. The order of the completed path is:

1. `destination.write_bytes(serialized)` — write;
2. `raw = destination.read_bytes()` — retain;
3. decode and parse; `UnicodeDecodeError` is a `ValueError`, so bytes that are
   not UTF-8 and bytes that are not JSON refuse by the same fixed name;
4. `_read_back_matches(raw, ...)`, whose **first** conjunct is `raw ==
   serialized` and which short-circuits, so nothing downstream of the byte
   comparison can decide the result when the bytes differ; and
5. `validate_run_record(written, ...)` — unchanged, including the exact per-cause
   canonical recovery contract.

There is no path that returns `destination` without all three claims holding:
the raw bytes are the bytes written; they decode and parse as the expected
document; the parsed document satisfies `validate_run_record`. Every failure is
the pre-existing fixed `NOT_THE_DOCUMENT_WRITTEN`, or the pre-existing fixed
OSError category. No refusal carries a path, the raw bytes, parsed content or
operating-system text.

**What was not substituted.** No digest, no normalized JSON, no mapping equality,
no newly serialized mapping, no file size, no decoded-text equality. The raw
comparison is `bytes == bytes`.

**No document-contract change.** This is a writer implementation fix. A valid
schema-3 record means exactly what it meant before; the bytes a conforming writer
emits are unchanged and every document version 3 accepted it still accepts. The
run-record schema therefore stays at **3**. Nothing in the inspection revealed a
genuine document-contract change; had it, the prompt required stopping, and this
paragraph would say so instead.

**One consequence stated plainly, as a reviewer focus.** Byte equality is
strictly stronger than the two conjuncts that follow it, so for anything
`build_run_record` can emit those two are now a **restatement** rather than an
independently observable barrier: no input to the public writer can make the
second or third conjunct decide the outcome. They are kept because the prompt
requires the three claims to remain distinct and because a later relaxation of the
first must confront the second rather than find it already gone. The
consequence for the previous pass's control is in §6.

---

## 5. Regression matrix

`tests/phase_5_0_evidence/test_r13_remediation.py`, new section
*PR-20260912-LAB1-2 — the raw bytes read back were never compared*, plus a new
negative-control section. **+28 nodes**, module **93 → 121**.

| Required by the prompt | Node | Rows |
|---|---|---|
| leading or trailing whitespace refused | `test_read_back_bytes_that_are_not_the_bytes_written_are_refused` | 5 (leading newline, trailing newline, both ends, trailing spaces, mixed leading whitespace) |
| — also, same document re-serialized | same | 1 (a different indent) |
| duplicate top-level key, same value, refused | same | 2 (`schema_version`, `document_type`) |
| duplicate nested cleanup key, same value, refused | same | 2 (`cleanup.state`, `cleanup.exit_code`) |
| the two reproductions, stated as bytes | `test_the_duplicate_key_reproduction_is_the_one_the_re_review_ran`, `test_the_whitespace_reproduction_is_the_one_the_re_review_ran` | 2 |
| the exact bytes written and returned are accepted | `test_the_exact_bytes_written_and_returned_are_accepted` | 1 |
| the four accepted cleanup-cause combinations still pass | `test_the_accepted_cause_combinations_survive_the_raw_byte_binding` | 4 |
| the seam itself, called directly with both reproductions | `test_the_raw_comparison_is_the_first_thing_the_read_back_seam_states` | 1 |
| negative control on the raw comparison | `test_reversing_only_the_raw_byte_conjunct_accepts_every_collapsing_tamper` | 10 |

Preserved and still green, unmodified except where §6 states otherwise:

* malformed and partially flushed bytes still refuse —
  `test_a_partially_flushed_run_record_is_refused`;
* the substituted scalar/list matrix still refuses — `UNCONSTRAINED_SUBSTITUTIONS`,
  9 rows including the `False`/`0` case;
* the four accepted cleanup-cause combinations still pass through the ordinary
  `Path` destination — `test_the_exact_procedures_for_the_causes_present_are_accepted`,
  4 rows;
* schema version 2 still refuses by name rather than being reinterpreted —
  `test_a_version_2_run_record_is_refused_by_version_rather_than_reinterpreted`;
* the 37-node substitution, cause/presence and read-back matrix from
  PR-20260912-LAB1-1 — unchanged and green.

The regressions run through the public `write_run_record()`. The only test that
calls the seam directly does so **in addition**, so a change to the seam's
contract cannot pass by leaving the writer's call site untouched.

---

## 6. Negative controls and reversal

**Control A — the whole seam hardcoded.**
`test_gutting_the_read_back_comparison_makes_the_regression_fail` (pre-existing)
replaces `_read_back_matches` with `True` and requires the substituted
`target_identity` to be accepted. **It was updated**: the lambda now takes `raw`,
because the seam's signature changed. Its meaning changed with it and the
docstring says so — the substitution it plants is now refused by the raw
comparison as well as by the mapping comparison, so it demonstrates that the
read-back seam as a whole is load-bearing and no longer isolates the mapping
half. That is the honest reading; it is not claimed to do more.

**Control B — only the raw conjunct removed.**
`test_reversing_only_the_raw_byte_conjunct_accepts_every_collapsing_tamper`
replaces `_read_back_matches` with `_without_the_raw_comparison`, which is the
**submitted implementation verbatim** — the two conjuncts as they were, accepting
`raw` and ignoring it exactly as the submitted writer ignored it by never passing
it. With only that conjunct gone, **all ten** collapsing tampers are written and
reported through `write_run_record()` without refusal. This is the control the
prompt asked for: it exercises the public writer, and it isolates the raw-byte
comparison rather than the seam, so the whitespace and duplicate-key regressions
are shown to constrain *that* comparison and the mapping comparison is shown to be
incapable of the job.

**Reversal run — the repair reversed in a scratch copy.** The complete tree was
copied to the scratchpad and **only** `execution/artifact.py` was replaced with
the submitted file; every test file was the submitted-plus-new set:

```text
cd <scratch copy>
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python \
  -m pytest -q -p no:randomly tests/phase_5_0_evidence
24 failed, 1912 passed
```

Of the 24, **12 fail behaviorally** with `DID NOT RAISE` — the ten refusal rows
and the two named reproductions. The other 12 fail by **arity**, not by behavior,
and this is reported as such rather than folded into the count: reversing the
repair restores the three-parameter seam, so the ten Control-B rows, Control A and
the direct-seam test raise `TypeError: ... missing 1 required positional
argument: 'serialized'`. They detect the reversal, but they detect it as a changed
signature.

**New tests that remain green under reversal — 5 of 28, named and explained:**

| Node | Why it stays green |
|---|---|
| `test_the_exact_bytes_written_and_returned_are_accepted` | It is the positive half. A faithful destination is accepted by both implementations, and it must be: without it the correction could be a writer that refuses everything and writes no evidence at all |
| `test_the_accepted_cause_combinations_survive_the_raw_byte_binding` (4 rows) | Same reason. These assert the four accepted cleanup-cause combinations are still **written**, which the submitted writer also did. They constrain the repair against over-refusal, not against under-refusal |

No other new node is green under reversal.

---

## 7. Preserved behavior — confirmed against this tree, not assumed

* run-record schema **version 3** — unchanged, and unchanged deliberately (§4);
* supplied-observation schema **version 3** and its separate cause/procedure
  fields — unchanged;
* review manifest **version 10** — unchanged; no contract the manifest declares
  was altered (§8);
* exact residue/configuration procedure validation and the strict document and
  `cleanup` key sets — `validate_run_record` is untouched;
* the operator-facing S-B message naming each applicable recovery — untouched;
* all R3/R4/R5 lifecycle fixes, reservation binding and terminal order —
  untouched; the complete harness is green;
* every unresolved C-7 case and target-fact refusal — unchanged;
* `is_executable` **False**, EH-R16-1 **Open**, Package 5.0 **not ready**,
  package-level P5.0-R5 **Blocking**, OD-62 **Open** — unchanged.

Historical statements were **dated-corrected, not rewritten**. The module
docstring's version-3 sentence claiming the bytes were compared now carries an
inline `(Corrected 2026-09-13: …)` note pointing at PR-20260912-LAB1-2, and the
earlier text is preserved. No Codex review record was edited or amended.

---

## 8. Generated-artifact integrity and the review-only digest

`tools/phase_5_0_evidence/execution/artifact.py` is in `COVERED_SOURCES`, so both
derived artifacts were regenerated through the **non-executing** CLI:

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python \
  -m tools.phase_5_0_evidence.execution.cli --manifest-out <temporary> --render <temporary>
```

* Generated **twice to temporary paths**; both generations byte-identical
  (`cmp` on manifest and plan).
* All **36** covered-source SHA-256 hashes recomputed independently with
  `hashlib`, against a `COVERED_SOURCES` read out of `review_manifest.py` through
  the **AST** rather than imported: exact set equality, **no mismatch**.
* Compared with the previously installed manifest: same 36-source set, and
  **exactly one hash moved** — `artifact.py`'s. `manifest_version` 10,
  `evidence_schema_version` 3, `manifest_schema`
  `phase-5-0-evidence-review-manifest`, `harness_version` `0.7.0-pre-execution`:
  all unchanged, and **no other top-level field differs**.
* The installed artifacts were **replaced with the generated output**, never
  hand-edited, and a **third** generation was compared byte-for-byte with the
  installed files: identical.

| Artifact | SHA-256 |
|---|---|
| `phase-5-0-evidence-harness-review-manifest.json` | `24d38e8df02a818ce4ce5d239318736fe494d5d5a304809b5b93d4c357aecac6` |
| `phase-5-0-evidence-harness-concrete-plan.md` | `784bed179baf209998961554e6ff5faa30dde9cdd06183c8b85e096b08338200` |
| `tools/phase_5_0_evidence/execution/artifact.py` | `64ad95ce188316111c4f3f205580f500bf85ce3992882b2ecd1fe7af46006e27` |

**New review-input digest — review input only, never an execution argument:**

```text
6ef61afbaa96dcbd5eda408eed5042aff3a227ce32cb56b149111e531f7a2408
```

It replaces `3b50e8f7adb309549aa1e69a61e9ddce1ce5bf11429eecc002f427b773df98a3`,
which described the pre-correction tree. **No digest was passed to `--execute` at
any point.**

---

## 9. Files changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/execution/artifact.py` | `_read_back_matches` takes and compares the raw read-back bytes; `write_run_record` retains them and orders read → parse → compare → validate; module and function docstrings record PR-20260912-LAB1-2 and date-correct the overstated version-3 sentence |
| `tests/phase_5_0_evidence/test_r13_remediation.py` | new PR-20260912-LAB1-2 section (17 nodes) and new negative-control section (11 nodes); `_TamperingDestination` records the bytes written and returned; Control A's lambda takes `raw` |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | regenerated — covered source changed |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | regenerated for the same reason |
| `docs/review/project-review-remediation-2026-09-13-lab1-r2-handback.md` | this document (new) |
| `docs/review/Handover information`, `docs/implementation-plan.md` §20, `docs/project-management/status.md` | dated pointer updates only |

**Security and operational implications: none.** No authentication,
authorization, privacy, network, filesystem-scope, credential or privilege
behavior is touched. The change makes an existing local refusal strictly stricter
on a code path that is unreachable in production today —
`write_run_record` requires `artifact_admissible`, and `is_executable` is
`False`. The refusal strings are unchanged and still carry no path, byte, parsed
content or operating-system text.

**Rollback.** Restore `execution/artifact.py` and
`tests/phase_5_0_evidence/test_r13_remediation.py` to their prior contents and
regenerate the two artifacts through the non-executing CLI. No migration, no
persistent state, no deployment step, no configuration change, nothing to undo on
any host.

---

## 10. Commands, interpreters and exact results

`TEST_DATABASE_URL` **unset throughout** (`env -u`), local only, in the order the
prompt requires.

| Suite | Command | Result |
|---|---|---|
| narrow run-record module | `pytest -q -rs tests/phase_5_0_evidence/test_r13_remediation.py` | **121 passed**, 0 skipped |
| focused LAB-1 set | `pytest -q -rs tests/phase_5_0_evidence/test_feasibility.py tests/phase_5_0_evidence/test_plan_and_cleanup.py tests/phase_5_0_evidence/test_r13_remediation.py` | **260 passed**, 0 skipped |
| structural no-execution | `pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py` | **217 passed**, 0 skipped |
| complete synthetic evidence harness | `pytest -q -rs tests/phase_5_0_evidence` | **1936 passed, zero skips** |
| bot | `pytest -q -rs tests/test_*.py` | **3018 passed, 326 skipped** |
| web | `pytest -q -rs tests/web` | **1609 passed, 1 failed, 1362 skipped** |
| Foundry | `node --test "foundry-module/tests/"*.test.mjs` | **171 passed, 0 failed, 0 skipped** |
| scoped `compileall` | `python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | **passed** |
| `git diff --check` | — | **clean** |

Every suite was re-run against the tree being submitted, **after** the generated
artifacts were reinstalled.

**Interpreters.** `/opt/discord-bots/venv-web/bin/python` and
`/opt/discord-bots/venv/bin/python`, both Python **3.12.3** with pytest
**8.4.2**; `node v24.20.0`. This is the restricted-pass exception recorded by the
previous pass and it still applies:
`/opt/freedom-blades/runtime/venv-web/bin/python` exists on **this** host at
Python 3.12.3 but has **no pytest**, and `oracle-test` may not be reached under
the active restriction. Interpreter availability on one host is not availability
on another.

**Every skip is unverified.** The 326 bot skips and 1362 web skips have one
printed cause — `TEST_DATABASE_URL is not configured for a disposable PostgreSQL
database`. The database-enabled web baseline is **80**, not 1362, so this pass
verified nothing in the skipped set. The evidence harness has **zero** skips.

**The one web failure is pre-existing and unrelated.**
`tests/web/test_p3_4_static_assets.py::test_the_discovery_enumerates_untracked_files_rather_than_directories`
fails on its own final assertion, `no untracked directory in this tree; this test
proves nothing`. Its premise is that `tools/phase_5_0_evidence/` is untracked;
that directory was committed in `5b0d1f2`, so the result depends on incidental
working-tree state. This change adds no untracked directory — its only untracked
additions are files inside the already-tracked `docs/review/`. It failed
identically before this change and in the two preceding passes. **Reported, not
fixed**: fixing it is outside this bounded assignment.

**Checks not run, and why — unavailable tooling is not a pass:**

| Check | Why |
|---|---|
| formatter, linter, type checker | **not configured and not installed.** No `pyproject.toml`, `setup.cfg`, `tox.ini`, `.flake8`, `.ruff.toml`, `mypy.ini` or `.pre-commit-config.yaml`; and no `ruff`, `flake8`, `black`, `mypy`, `pylint`, `pyflakes` or `isort` on either interpreter's path. **Unavailable, not a pass** |
| database-marked tests | `TEST_DATABASE_URL` kept unset by the restriction |
| anything on `oracle-test` | no SSH, synchronization, host inspection, preflight, permission change, provisioning, dependency operation, service change or environment reset is authorized. The prior pytest installation there broadens none of it |
| the read-only target preflight, V6, V8, V10's actual identity | not authorized; neither performed nor expanded |
| any real execution | `--execute`, an armed boundary or materializer, and generated-vector execution all refused |

One further note for completeness: a diff secret-scan command was **refused by
`guard-secrets.py`** because the grep pattern I passed contained a literal that
matches a protected filename. No protected file was read; the scan was re-run
with a pattern that does not name one, and it reports no secret-shaped content in
any added line.

---

## 11. Restrictions honored

Nothing was executed, provisioned, synchronized or inspected. No SSH,
synchronization, host inspection, preflight, permission change, provisioning,
database operation, destructive drill, service change, credential access,
generated-vector execution, `--execute`, real boundary or materializer,
migration, deployment, cutover, commit, push, reset or history rewrite. The bot
was not restarted. Every unrelated and reviewer-authored working-tree change was
preserved; the two Codex review records were neither overwritten nor amended.

---

## 12. Remaining gates and the next checkpoint

**Next action: Codex independent technical re-review** of this raw-byte binding
correction. The session that implemented it does not dispose of the finding.

Unchanged and still open:

* **LAB-1** — Important, **not closed**;
* **PR-20260912-LAB1-2** — repaired here, disposition is Codex's;
* **C-7** — unresolved, all cases;
* **EH-R16-1** — Open, real-execution refusal in force;
* **`is_executable`** — `False`;
* the **twelve target facts** — unconfirmed; V6, V8 and V10's actual-identity
  fact unperformed;
* the **ten-item r6 §7 delta** — accepted as design, **not provisioned**;
* **Package 5.0** — not ready; **P5.0-R5** — Blocking; **OD-62** — Open.

**Proposed reviewer focus areas:**

1. **The subsumption stated in §4.** Byte equality is strictly stronger than the
   two conjuncts after it, so those two can no longer be falsified through the
   public writer. Keeping them satisfies the prompt's three-distinct-claims
   requirement; a reviewer may reasonably hold that an unfalsifiable conjunct
   should be removed instead, or that it should be exercised through a different
   caller. This is the judgement call in the change.
2. **Control A's changed meaning** (§6) — whether updating the pre-existing
   control's arity rather than replacing it is the right treatment, given that
   its demonstration is now weaker than it was.
3. **The arity-versus-behavior split in the reversal run** (§6) — whether 12
   behavioral detections is the right sensitivity for a 4-line change, or whether
   more of the reversal ought to be behavioral.
4. **The ordering choice** — parsing before the byte comparison rather than after
   it. Short-circuiting makes the outcome identical, but a reviewer may prefer the
   raw comparison to precede any parse of bytes the writer has not yet accepted.
5. Whether the run-record schema staying at **3** is right (§4), given that no
   document a conforming writer emits changes meaning.
