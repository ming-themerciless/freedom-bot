# Claude handback — C-P5.0-R5-R3; S4-3 producer gate made fail-closed and the invalidation summary corrected — 2026-09-23

*Disposition, 2026-09-23:* Peter Duscha accepted C-P5.0-R5-R3 and closed
**P5.0-R5-R2-PLAN-1** and **P5.0-R5-R2-DESIGN-1** as remediated after Codex's
independent review reported no findings. C-S4-3 and C-7 remain unresolved, and
this disposition creates no host or execution authority.
[Acceptance record](project-review-2026-09-23-p5-r5-r3-acceptance.md).

*Performed under the accepted C-P5.0-R5-R3 assignment in
`docs/review/Handover information`. Peter Duscha accepted Codex's review of
C-P5.0-R5-R2 and assigned this bounded, repository-only scope to Claude.*

*Repository work only. **No action on `oracle-test` or any other host was
taken.** There was no SSH, synchronization, `sudo`, database, service, network
or credential access. Nothing touched `/run`, `/var/lib`, deployed
`/opt/freedom-blades` locations outside this repository or any protected `/tmp`
artifact. No verifier, provisioner or evidence band was invoked, and no secrets
scan was run. No guard refused a call. Nothing was committed or pushed.
**P5.0-R5-R2-PLAN-1 and P5.0-R5-R2-DESIGN-1 are left Open for independent Codex
review.***

## 1. Outcome

* **PLAN-1.** `SandboxAttestationProducer`, `S4_3_PRODUCER` and the plan's
  resolved branch are **removed**, and nothing replaces them. C-S4-3 is now
  declared **unconditionally**. `s4_3_dependency_gaps()` takes only the two
  plan-derived inputs, and it always reports the two producer requirements as
  unmet. No string, path, boolean, digest or review description can be supplied
  to change that. To resolve C-S4-3, a future pass must change the generator's
  code and add artifacts, and that change must then be reviewed independently.
* **Coverage invariant.** S4-3 is now a `required_cases.REQUIRED_CASES` row. It
  is the only new row; no other Stage 1–4 case was added. If both its
  `UnresolvedStep` and its step attribution are deleted, `build_concrete_plan()`
  now refuses the plan.
* **DESIGN-1.** The present-tense "honest division of labour" row now states
  both invalidation conditions and the pending availability cost. The single-rule
  wording is labelled as superseded. A search of the package plan found no other
  live contradiction (§7).
* **Nothing is claimed as evidence or approval.** P5.0-R5 remains **Blocking**,
  OD-62 G-A remains conditional, `plan.is_executable=False`, C-7 and C-S4-3
  remain unresolved, and Package 5.0 remains **not ready**. No digest is
  approved, and no `--execute` is authorized.

## 2. Files changed

This pass edited only the files below. Every other change in the worktree
predates it (§11).

| File | Before this pass | Change |
|---|---|---|
| `tools/phase_5_0_evidence/concrete_plan.py` | modified (earlier passes) | Removes `SandboxAttestationProducer` and `S4_3_PRODUCER`. Adds `S4_3_UNMET_PRODUCER_REQUIREMENTS`, the two unmet producer requirements as fixed text. `s4_3_dependency_gaps()` loses its `producer` parameter; its two remaining parameters are keyword-only and its result is never empty. `_stage_four` declares `STAGE4-S4-3` with no `if gaps`, and the capture step's `evidence_case_ids` is always `()`. `what_would_resolve_it` names a code and artifact integration pass, not a declared value. `__all__` is updated. The argv and the step's purpose text are byte-identical |
| `tools/phase_5_0_evidence/required_cases.py` | modified | Adds the `S4-3` `RequiredCase` in the `filesystem` band, sourced to §2.13.2a S4-3 conditions 1–4 and §2.13.6 J-25 |
| `tools/phase_5_0_evidence/observations.py` | modified | `classify_supplied_observations` now counts only in-scope (Band-7 schema) cases as `unresolved_cases`, which is what `EvidenceResult.unresolved_cases` is documented to hold. S4-3 is reported in `outside_scope` |
| `tools/phase_5_0_evidence/review_manifest.py` | modified | `MANIFEST_VERSION` 19 → **20**, with a history entry |
| `tests/phase_5_0_evidence/test_r5_r3_s4_3_binding.py` | — | **New.** 97 tests (§4, §5) |
| `tests/phase_5_0_evidence/test_r5_r2_s4_3_dependency.py` | untracked (R2) | Removes three misleading tests and the `HYPOTHETICAL` fixture, and replaces two more (§3). Moves to the new signature. Its S4-3 mapping assertion now expects a row blocked by C-S4-3. The module docstring records the change. 20 → 16 tests |
| `tests/phase_5_0_evidence/test_r16_c6_c7_c8.py` | tracked, unmodified | Three exact-set pins gain `S4-3`: `outside_scope` twice, and the `producer_mapping` row set, which also gains S4-3's produced/blocked assertions |
| `tests/phase_5_0_evidence/test_r16_remediation.py` | modified | Manifest pin 19 → 20, with its dated reason |
| `docs/review/phase-5-0-package-plan.md` | modified | Corrects the systemd-sandbox row of §2.13.8a's "honest division of labour" table, and adds one dated R3 sentence after §2.13.2a's C-S4-3 paragraph (§7) |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json`, `…-concrete-plan.md` | modified | Regenerated by the canonical generator (§7) |
| `docs/review/phase-5-0-p5-r5-r2-s4-3-dependency-and-invalidation-remediation-handback.md` | untracked (R2) | Dated *Update … C-P5.0-R5-R3* notes in §3, §4, §11 and §12. §11 also gains a new item 7. No R2 measurement was rewritten |
| this handback; `docs/review/Handover information`; `docs/project-management/status.md`; `docs/project-management/change-log.md` | — / modified | State pointers. The R3 assignment heading is relabelled *Consumed*, and its body is untouched |

## 3. PLAN-1 — the producer gate, before and after

**Before (R2).** `s4_3_dependency_gaps(producer, *, requested_properties,
substituted_path)`. Requirements 1 (deployed unit and drop-in policy) and 4
(`SystemdIdentity` producer and binding) were met by any
`SandboxAttestationProducer`. That class held two strings and refused only blank
ones. With the 12-property vector and `CANONICAL_PROBE_PATH`,
`SandboxAttestationProducer("x", "y")` returned `()`. `_stage_four` then skipped
the `UnresolvedStep` and attributed S4-3 to the capture step. The gate was
*"no gaps ⇒ resolved"*, and a label could produce "no gaps".

**After (R3).**

* `s4_3_dependency_gaps(*, requested_properties, substituted_path)`. **No
  producer parameter exists**, so no metadata value can reach it. Requirement 1's
  gap is always first and requirement 4's is always last. Their text is
  `S4_3_UNMET_PRODUCER_REQUIREMENTS`. Requirements 2 (every
  `COMPARED_PROPERTIES` member exactly once) and 3 (the canonical
  `ReadWritePaths=`) are still derived from the plan's own vectors. As before,
  they add their own gaps when unmet.
* `_stage_four` calls it only to **render detail** into `why_not_a_vector`. It
  then calls `steps.block(UnresolvedStep(… C-S4-3 …))` with no condition, and the
  capture step carries `evidence_case_ids=()` with no condition. **The plan has
  no success branch at all.**
* `what_would_resolve_it` now says that resolution is *"a separately
  authorized, independently reviewed pass that adds the reviewed deployed unit
  and drop-in policy, widens the capture vector, and implements and integrates
  the reviewed `SystemdIdentity` producer — code and artifacts that change this
  generator. No review reference, label, path, digest or flag resolves it …"*.

**Why nothing replaces the class.** The assignment asked for the smallest
structurally honest representation. It prefers exposing no resolution branch
over *"inventing a token, boolean, path or label that purports to prove
review"*. Any typed stand-in I could write now, such as a digest field, a path
to a unit file or a review record, would be exactly that. The real producer's
shape belongs to the pass that builds it.

**R2 tests removed as misleading**, all in `test_r5_r2_s4_3_dependency.py`:

| R2 test | Why it is removed |
|---|---|
| `HYPOTHETICAL` fixture | an explicitly hypothetical pair of labels, used as a reviewed producer |
| `test_the_current_vector_leaves_a_gap_even_with_a_reviewed_producer` | asserted that the labels discharged requirements 1 and 4. It is replaced by `test_the_current_vector_leaves_a_vector_gap`, which expects three gaps |
| `test_installing_a_reviewed_producer_alone_does_not_resolve_it` | asserted `"no reviewed deployed" not in why_not_a_vector` once the labels were installed |
| `test_every_requirement_is_necessary` (7 cases) | its last case asserted **0 gaps** for labels plus a complete vector. It is replaced by `test_every_plan_derived_requirement_is_necessary` (6 cases), where every case has the two producer gaps |
| `test_a_producer_must_name_both_reviews` | the class it tested is gone |
| `test_the_gap_predicate_is_the_only_resolution_route` | asserted that a predicate returning `()` **cleared** C-S4-3. R3 asserts the opposite |

## 4. Proof that metadata alone cannot resolve it

All of these are in `test_r5_r3_s4_3_binding.py`:

| Test | What it proves |
|---|---|
| `test_the_label_only_producer_is_gone` | neither `SandboxAttestationProducer` nor `S4_3_PRODUCER` exists on the module or in `__all__` |
| `test_the_gap_function_accepts_no_producer_argument` | the signature is exactly `{requested_properties, substituted_path}`, both keyword-only |
| `test_metadata_cannot_be_passed_as_a_producer` (×13) | each of 13 metadata values (`"x"`, `"y"`, a hypothetical review description, a plausible review citation, a doc path, a unit path, a binary path, a bare and a prefixed fabricated digest, `True`, `1`, a pair of labels, a dict of R2's field names) raises `TypeError`, whether passed positionally or as `producer=` |
| `test_installing_metadata_on_the_module_cannot_clear_c_s4_3` (×65) | each of those 13 values, set on 5 attribute names (`S4_3_PRODUCER`, `S4_3_REVIEWED_PRODUCER`, `S4_3_PRODUCER_REVIEWED`, `SYSTEMD_IDENTITY_PRODUCER`, `DEPLOYED_UNIT_REVIEW`), leaves exactly one C-S4-3 entry, no step claiming S4-3 and `is_executable=False` |
| `test_the_producer_requirements_are_unmet_even_with_a_complete_vector` | with all 12 properties and the canonical path, the result **equals** the two unmet producer requirements. No constructible input yields fewer |
| `test_the_gap_list_is_never_empty` (×4) | the result is never empty and always contains both producer gaps. This holds for complete, partial, empty and doubled vectors and for a wrong path |
| `test_the_current_vector_remains_insufficient` | the real plan's entry renders `requests 2 of 12 compared properties` and both producer gaps. It no longer mentions `S4_3_PRODUCER` |
| `test_c7_removed_leaves_c_s4_3` | with C-7 removed by `dataclasses.replace`, `conflicts() == ("C-S4-3",)` and `is_executable=False` |
| `test_c7_resolved_plus_every_other_input_leaves_c_s4_3` | all of these **together**: C-7 resolved (`_band_7` replaced by reviewed `ExternalCase`s), the five attribute names set to `"reviewed and accepted"`, and a PASSED `unit_sandbox` classification with attestation. The result is still `("C-S4-3",)` and not executable |
| `test_a_supplied_s4_3_observation_cannot_cover_it` | for **every** `Custody`, including `reviewer_verified`, the importer refuses the observation and the plan is unchanged |
| `test_a_reviewed_external_case_for_s4_3_is_an_overlap` | a reviewed S4-3 `ExternalCase` is refused as an overlap with the unresolved column |
| `test_replacing_the_gap_predicate_does_not_clear_it` | `s4_3_dependency_gaps` monkeypatched to return `()` leaves `conflicts() == ("C-7", "C-S4-3")`. This is the inverse of R2's test |
| `test_the_generator_has_no_resolution_branch` | `_stage_four`'s source has no `if gaps` or `if not gaps`, and exactly one `("S4-3",)` attribution (the `UnresolvedStep`). The module no longer mentions `S4_3_PRODUCER` |

No test constructs a complete reviewed producer, and none needs to. No success
branch exists to reach.

**Regression direction.** I did not rerun the new file against the R2 module,
because R2's `concrete_plan.py` was not preserved separately and I did not
restore anything from `HEAD`. By construction it would fail there at import:
`S4_3_UNMET_PRODUCER_REQUIREMENTS` does not exist in R2. In substance,
`test_replacing_the_gap_predicate_does_not_clear_it` asserts the exact opposite
of R2's own `test_the_gap_predicate_is_the_only_resolution_route`, which passed
against R2.

## 5. Coverage invariant

**Choice.** One `REQUIRED_CASES` row, `S4-3`, in the `filesystem` band. This is
the canonical mechanism: it is the table `check_case_coverage` reads, and its
docstring says it grows when a reviewer adds a row. The R3 assignment is that
direction. S4-3 is the only probe case with a known-missing producer, so it is
the only one where this deletion is fail-open. No other Stage 1–4 case was
added. `test_s4_3_is_a_required_case_and_the_only_new_one` pins the whole table
as R13/R16's six rows plus S4-3.

**Proof.**

* `test_coverage_refuses_a_plan_missing_s4_3_from_every_column`: dropping S4-3
  from the unresolved column makes `check_case_coverage` raise `PlanRefused`
  with `S4-3` in the message.
* `test_deleting_the_declaration_and_the_attribution_is_refused`: `_Steps.block`
  is patched to drop only the C-S4-3 entry. The capture step already carries no
  S4-3, so this is R2's disclosed fail-open deletion, and `build_concrete_plan()`
  now raises `PlanRefused`.
* `test_s4_3_is_visible_as_required_in_the_mapping_and_the_manifest`: in
  `producer_mapping`, S4-3 has `produced_by_plan_steps=()` and
  `declared_unresolved_by=("C-S4-3",)`. The manifest's `required_cases` entry has
  `produced_by=[]`, `blocked_by=["C-S4-3"]` and `supplied_externally=false`.

**One consequential change, and why.** Adding the row put S4-3 into the Band-7
importer's `unresolved_cases`, because that list was computed over all required
cases. That would make `band_7_coverage_complete` false for a reason outside
Band 7, which contradicts `EvidenceResult.unresolved_cases`'s documented meaning
(*"in-scope cases the plan still declares unresolved"*). The importer now
filters that list to cases in `BAND_7_SCHEMA`. S4-3 appears in `outside_scope`
instead, which is what that field is for. This can open nothing:
`overall_completeness_established` and `eligible_for_operational_acceptance`
remain unconditionally `False`, and the Band-7 result is what it was before this
pass. `test_the_importer_reports_s4_3_outside_its_scope_not_as_band_7` covers
it.

## 6. C-7 independence

C-S4-3 is unconditional, so it cannot depend on C-7. The tests in §4 show this
three ways: C-7 removed, C-7 resolved through reviewed external producers, and
C-7 resolved together with every other input. The dry-run summary reports
`unresolved conflicts : 4 (C-7, C-S4-3)`. The three C-7 manifest entries are
content-identical to version 19 (§8).

## 7. DESIGN-1 — corrected text and search disposition

**§2.13.8a "The honest division of labour", systemd-sandbox row, "merely
records" cell.**

*Before:* "… It is inside the same report, under the same digest, and
invalidated by the same rule — a redeployment forces a rotation (**J-22**,
**F-6**) — so it needs no column, no second artifact and no second authority"

*After:* "… It is inside the same report, under the same digest. *Amended
2026-09-23 under C-P5.0-R5-R3, pending review:* it is invalidated under **two
conditions**, matching §2.13.2a's Option-1 table — (1) a change of **deployed
bytes** invalidates through **J-22**/**F-6** and requires a rotation; (2) a
change of **systemd or package identity** invalidates the S4-3 attestation at
**W4**/**C-a** under **J-25** and requires a fresh `verify-capability`, which is
a rotation. The second is a further refusal cause of the existing
`SW-J25`/`J-25`, not a new rule family: it needs no column, no second evidence
artifact, no second digest authority and no new refusal-code family. Its
availability cost extends **R-5.0-11** and **R-5.0-16** and remains pending
review and maintainer disposition. *(Revision 7 said "invalidated by the same
rule — a redeployment forces a rotation"; that single-rule statement is
superseded.)*"

**§2.13.2a, after the C-S4-3 paragraph.** I added one dated sentence. It says
that no review reference, label, path, digest or flag can stand in for the
producer, that C-S4-3 has no resolution branch, that resolution is a code and
artifact integration pass followed by independent review, and that S4-3 is a
required case.

**Search.** I searched the package plan for `J-22`, "rotation" near
sandbox/S4/systemd/probe report, "same rule", "no second/new invalidation",
"single/only invalidation" and "sandbox evidence". Disposition:

| Location | Disposition |
|---|---|
| R6-A history row | already labelled superseded as to invalidation (R2). Unchanged |
| §2.13.2a paragraph before the Option-1 table | already states the second rule with W4/C-a (R1). Unchanged |
| §2.13.2a Option-1 table, Invalidation and Cost rows | already consistent (R2). Unchanged |
| §2.13.2c "When it becomes final" | already scoped to deployed bytes, with a dated identity sentence (R2). Unchanged |
| §2.13.6 J-25 row | already includes the systemd-identity cause (R1). Unchanged |
| **"honest division of labour" row** | **corrected (above)** |
| §2.13.2a "inside the same option-A cost … not a new artifact, authority or rule" | about S4-0 and the `…/probe-ro` control, not invalidation. Unchanged |
| §5.3 host-binding option A-2, "the same rule as J-22 and F-6, and no second invalidation rule" | the separate, not-adopted option. The assignment says not to rewrite it. Unchanged |
| Revision-7 security-review question (*"is a redeployment forcing a rotation (J-22) sufficient invalidation …"*) | a question, not a requirement, and R1's condition 4 answers it. Unchanged |
| R-5.0-11 register row, *"J-22 is the one an operator will meet in normal work"* | describes J-22 as the common case, not the only rule. Residual rows are out of scope, and the cost is recorded as pending in the design text. Unchanged |

Outside the package plan, `open-decisions.md` and `status.md` still repeat
revision-7/8/9 wording inside dated history records. As in R2, I left those
unchanged.

## 8. Generated artifacts — review input only

* **Before any edit**, the committed artifacts' SHA-256s equalled R2's reported
  values (`1a50964e…` manifest, `2b27fa5b…` plan).
* **After:**
  `env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 /opt/freedom-blades/runtime/venv-web/bin/python -m tools.phase_5_0_evidence.execution.cli --manifest-out docs/review/phase-5-0-evidence-harness-review-manifest.json --render docs/review/phase-5-0-evidence-harness-concrete-plan.md`
  reported a dry run: 138 steps, `unresolved conflicts : 4 (C-7, C-S4-3)`,
  `executable : False`. A second generation to scratch matched both files byte
  for byte (`cmp`).
* **`MANIFEST_VERSION` 20. Review-input digest
  `d72ec6779abe478a57032d4576669deab6bb8475dbf01ad388c37f35d1ef3f3a`.**
  File SHA-256s: manifest JSON
  `9fe6496b07c7df3d71a517f593128c42b84fc142a354f4b3987fe52b3a323bcd`, concrete
  plan `a8f74244ceed8ee3900add9ff5aef74345616069a6828ab4e7a57bdad50967df`.
* **Structural manifest diff against version 19:** `manifest_version`; the source
  digests of `concrete_plan.py`, `observations.py`, `required_cases.py` and
  `review_manifest.py`; `required_cases` 6 → 7 (S4-3, blocked by C-S4-3); and the
  C-S4-3 entry's `why_not_a_vector` and `what_would_resolve_it`. **Every step,
  argv and purpose is identical.** Mutations, materializations, expectations,
  target facts and the three C-7 entries are unchanged.
* Neither digest is approval or operational evidence. `032d947b…` (v19) no
  longer reproduces from this tree.

## 9. Commands and results

All runs were local, on the **repository host**, not `oracle-test`, with
`/opt/freedom-blades/runtime/venv-web/bin/python` (Python 3.12.3). Every pytest
run used `env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 … -m pytest -q -rs
-p no:cacheprovider`.

1. **Service-free check before the full suite.** I grepped
   `tests/phase_5_0_evidence/` for `subprocess.`, `socket.socket`,
   `create_connection`, `psycopg.connect`, `create_engine`, `urllib.request`,
   `requests.get/post` and `httpx.`. The one hit is the message text of
   `test_no_execution.py`'s own no-`subprocess` assertion.
   `test_no_execution.py` asserts that `TEST_DATABASE_URL` is never consulted
   there.
2. **With the code change and before the test updates**, the R2 test file failed
   at collection (`ImportError: S4_3_PRODUCER`), as expected. With that file
   updated, **3 failed, 2916 passed**. The three failures were the exact-set pins
   in `test_r16_c6_c7_c8.py` that lacked S4-3 (§2).
3. **Focused:** `test_r5_r3_s4_3_binding.py`, `test_r5_r2_s4_3_dependency.py`,
   `test_r5_r1_stage4_s4_3.py`, `test_concrete_plan.py`,
   `test_r16_remediation.py`, `test_r16_c6_c7_c8.py`, `test_r14_remediation.py`,
   `test_r13_remediation.py` and `test_executor.py` → **555 passed, 0 skipped, 0
   failed, 2 warnings**. The R3 file alone → **97 passed**.
4. **`tests/phase_5_0_evidence`, complete** → **2919 passed, 0 skipped, 0
   failed, 2 warnings**. That is R2's 2826, minus 4 removed R2 tests (20 → 16),
   plus 97 new ones.
5. **Scope guard**, `tests/web/test_p3_4_static_assets.py` → **110 passed, 1
   failed, 2 warnings**. The failure is
   `test_the_discovery_enumerates_untracked_files_rather_than_directories`:
   *"no untracked directory in this tree; this test proves nothing"*. It is the
   same pre-existing, Git-state-dependent failure R1 and R2 reported. This pass
   adds one untracked test file and no directory or tools module.
6. **Warnings.** Every run gave the same two `PytestConfigWarning`s, for the
   unknown options `asyncio_mode` and `asyncio_default_fixture_loop_scope`.
7. **Canonical generation and second-generation `cmp`**, as in §8.
8. **`git diff --check`** → clean. The new test file has no trailing whitespace.

## 10. Checks not run, and why

* Anything on `oracle-test`, including the canonical bot/web/Foundry suites:
  prohibited by this assignment.
* Database-marked tests: prohibited, and `TEST_DATABASE_URL` stayed unset. I did
  not run the web suite beyond the scope-guard file.
* Formatter, linter and type checker: **none is configured**. There is no
  `pyproject.toml`, `setup.cfg`, `tox.ini`, `ruff.toml`, `mypy.ini` or pre-commit
  config, and `ruff`, `mypy` and `black` are not installed in the interpreter.
* The new tests against the R2 module (§4, "Regression direction").
* A secrets scan: prohibited. I reviewed the diff manually. It adds no
  credential, token, key, host address or player data.

## 11. Git status

**Before:** 116 porcelain entries, the same as R2's "after". **After:** 121. The
new entries are all this pass's:

```
 M tests/phase_5_0_evidence/test_r16_c6_c7_c8.py
 M tools/phase_5_0_evidence/observations.py
 M tools/phase_5_0_evidence/required_cases.py
?? docs/review/phase-5-0-p5-r5-r3-s4-3-binding-and-invalidation-remediation-handback.md
?? tests/phase_5_0_evidence/test_r5_r3_s4_3_binding.py
```

The other files in §2 were already modified or untracked before this pass. I
restored nothing from `HEAD`, and every pre-existing change is preserved. Content
hashes of every porcelain entry, taken before and after, differ only for the
§2 files.

## 12. Security, data-authority, deployment and rollback effects

* **Security.** This closes a fail-open route: a label could clear C-S4-3 and,
  with C-7 resolved, make the plan executable while S4-3 could not pass. It also
  closes a second one: deleting S4-3's declaration together with its
  attribution. **Authority only narrows.** No executable, vector, mutation,
  identity, permission, `PERMITTED_EXECUTABLES` entry or gate changed, and the
  plan no longer has a branch in which S4-3 is produced. The importer change can
  only keep an out-of-scope case out of a Band-7 statement. Every completeness
  and eligibility answer stays withheld.
* **Design.** DESIGN-1 changes no requirement. It makes a summary say what
  §2.13.2a, the Option-1 table, W4 and J-25 already say. The amendment is dated
  and marked pending review.
* **Data authority.** None. No schema, migration, database or Sheet behaviour
  changed.
* **Deployment.** None.
* **Rollback.** Revert this pass's edits to the §2 files, then re-run the
  canonical generator. No host state exists to undo.

## 13. Remaining gaps

1. **C-S4-3 is open by design and now has no resolution branch.** Resolving it
   needs the deployed writer unit (reconciliation row 16), `SUPPORTED_DROP_INS`
   confirmation, a widened capture and transient unit, and a reviewed
   `SystemdIdentity` producer and binding. That pass must also add the resolution
   branch itself. All of this is out of scope here.
2. In `producer_mapping()`, S4-3's row reports `in_harness_producer=True` and
   the generic "this harness's own generated steps" producer text, because that
   field only distinguishes Band-7-schema cases. `declared_unresolved_by=("C-S4-3",)`
   makes the row unresolved, but the producer wording is generic. I did not
   change the mapping's vocabulary.

   *Update 2026-09-23, C-P5.0-R5-R4:* Codex raised this gap as
   P5.0-R5-R3-EVIDENCE-1, together with the persisted `COMPLETENESS_WITHHELD`
   claim that every outside-scope case is produced by the executed plan. R4
   derives `in_harness_producer` from plan attribution, gives S4-3 *none*
   producer and procedure texts naming C-S4-3, and corrects the rationale
   (`MANIFEST_VERSION` 21). The R3 measurements above are unchanged.
   [R4 handback](phase-5-0-p5-r5-r4-s4-3-producer-reporting-remediation-handback.md).
3. The identity-change availability cost is recorded as extending
   R-5.0-11/R-5.0-16, pending disposition. The register rows are not amended.
4. Unchanged from R1/R2: the J-12/J-17 and J-02 → `J-20` readings, real
   `systemctl show` formats, C-7 and the missing JNL vectors, and the
   pre-existing scope-guard failure.
5. `docs/implementation-plan.md` §20 still names C-P5.0-R5-E1 as the current
   action. I kept to the minimum state pointers.

## 14. Proposed Codex review focus

1. Whether exposing **no** resolution branch is the right representation, and
   whether `s4_3_dependency_gaps` should keep reporting the plan-derived
   requirements at all, given that it no longer gates anything.
2. The metadata tests in §4. Can any path still clear C-S4-3 other than editing
   `_stage_four`?
3. The `REQUIRED_CASES` row as the coverage invariant, and whether its wording
   (`asserts`, `source`) is right.
4. The importer's in-scope filter in `classify_supplied_observations`, and gap 2
   (the generic producer wording for S4-3's mapping row).
5. The corrected division-of-labour row against §2.13.2a, the Option-1 table,
   W4 and J-25, and the §7 search disposition, especially the R-5.0-11 row and
   the revision-7 review question.
6. That `MANIFEST_VERSION` 20 and `d72ec677…` are recorded as review input only.
