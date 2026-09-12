# R16 remediation handback — EH-R16-1 … EH-R16-4, 2026-09-09

Returned to Codex for independent re-review. **Nothing here is closed on the
implementer's authority.** Passing tests do not approve execution.

**Read this first: the submission is deliberately partial.** EH-R16-2, EH-R16-3
and EH-R16-4 are implemented with regressions. **EH-R16-1 is a design submitted
for technical review and is not implemented**, because the remediation prompt
requires the revised C-8 design to be reviewed *before* the changed mechanism is
built, and R16 recorded that the checkpoint was skipped last time and that
reviewing a combined submission does not retroactively satisfy it. Implementing
it again before that review would repeat the process failure the finding names.

| Finding | Severity | Disposition |
|---|---|---|
| EH-R16-1 — root identity checked after dependent cleanup | Blocking | **Design submitted, not implemented.** No source changed for it |
| EH-R16-2 — observed provenance refusal replaced by an inference | Blocking | **Conceded and corrected**, with regressions |
| EH-R16-3 — complete coverage omits the capability cases | Important | **Conceded and corrected**, as the bounded partial-scope option the review offers |
| EH-R16-4 — missing producers reclassified as resolved | Important | **Conceded in full.** The three Band-7 cases are unresolved again and `is_executable` is `False` |

Review-input digest, **not execution approval**:
`ec1e3e70b5d24aca911df9e4dcd394361ebffdb04b9587434cb74386756f2839`.
It must not be passed to `--execute`. The starting digest
`765b299bf680b06bce4edd34ed236dea13dff466c39e6d457d7da190b5772acd` was review
input only and was not used to execute anything.

---

## 1. EH-R16-1 — the revised C-8 design, for technical review

**Location of the design:**
[`phase-5-0-evidence-harness-c8-ownership-design-r16.md`](phase-5-0-evidence-harness-c8-ownership-design-r16.md).
It supersedes §3 of the C-6/C-7/C-8 handback, which R16 did not accept.

**Not implemented. No file changed for this finding.** `cleanup.py`,
`execution/executor.py` and `execution/case_program.py` carry the R16 mechanism
exactly as reviewed, including the defect: the only `REVALIDATE` step is
generated immediately before the root `rmdir`, and the thirty cleanup commands
R16 counted still precede it.

The design in summary, so this document is readable without it:

* **The claim.** No cleanup operation whose safety depends on the disposable
  root being the object this run created is performed unless an identity reading
  taken *immediately before that operation*, through the reviewed bootstrap
  program, matched the identity `mkroot` reported.
* **Creation.** `_do_mkroot` moves to `mkdirat(2)` plus `openat(2)` against one
  parent directory descriptor, so the creation and the identity reading cannot
  disagree about which parent they resolved. A replacement between them remains
  detectable and takes the existing exit-`66` path: no ownership, bounded
  residue, never removed. No verb, arity or argument kind changes, and the
  privileged interface is not widened.
* **Guards.** One read-only `statroot` per root-dependent cleanup step — every
  configuration restore, the reload, both post-reload observations and all 29
  contained-path reversals, 34 in the current plan — each named by the step it
  guards, with the immediacy enforced by `CleanupPlan.ordering_holds()` rather
  than described.
* **A failed guard.** The guarded step is **not attempted**. A restore that is
  not attempted cannot install a substituted `before/` file, which is the direct
  answer to *"Never restore PostgreSQL configuration from substituted files."*
  Subjects become residue, the configuration risk is reported, the state is S-B.
* **Recovery inputs.** New: when a guard did not match, the retained captures are
  reported as **unverified** and a different procedure is issued. R13's four-step
  procedure tells an operator to reinstall from the captures, and doing that from
  inside an object this run did not create is exactly what the guards refuse.
* **Independently safe work continues.** Account, group, membership, catalog and
  transient-unit reversals do not depend on root identity and still run, so a
  failed guard does not leave those behind as well.
* **Residual risk, stated rather than accepted silently.** §5 of the design names
  three: descendant replacement is **not** detected and closing it needs a
  descriptor-addressed removal that would move deletion out of `rm`/`rmdir` and
  into the reviewed program — a widening of the privileged interface, offered as
  a maintainer decision and **not** proposed; the guard-to-operation interval is
  one process spawn and is not zero; and device/inode reuse is bounded by the
  same trust assumption. The descendant trust assumption is stated narrowly and
  its limits are stated with it — it does not hold for a path whose containing
  directory the plan makes group-writable, and the design commits to enumerating
  that subset in the rendered plan rather than arguing it away.

**Requested:** technical acceptance or rejection of the mechanism, the residual
statements, and §7's regression list, before it is built.

---

## 2. EH-R16-2 — the observed provenance result is classified

**Conceded.** R16's reproduction is exact: changing only the provenance record's
refusal code from `J-26` to `DEP-04` produced `JNL-51-g-refusal` with status
**passed** and observed value **refused J-26**. The classifier built its observed
value from `bool(absent)` — from whether APR or PVR was missing, which is the
*experimental input the producer arranged*, and which says nothing about what
`init-generation` then did.

**What changed.**

* `provenance.classify_missing_provenance` takes `observed_refusal_code` as a
  **required keyword with no default**. A code is compared with
  `EXPECTED_OMISSION_REFUSAL`, this module's own constant; `None` is the program
  having admitted, recorded explicitly as `OBSERVED_ADMITTED` rather than as an
  absence. A missing keyword is a `TypeError`, asserted.
* APR/PVR absence keeps the role it actually has. It is the **precondition**, and
  when it does not hold the observed value says so and the record fails —
  a refusal observed in a run where nothing was omitted is a refusal for another
  reason.
* The supplied-observation schema is **version 2**. `JNL-51-PROVENANCE-OMITTED`
  carries `refused` (yes/no) and a `refusal_code` whose shape now admits `none`,
  so *"the program did not refuse"* is expressible. Version 1 could not say it,
  which is why the classifier inferred one. A version-1 payload is refused rather
  than reinterpreted.
* Two halves of one observation must agree: `refused=yes` with `refusal_code=none`
  and `refused=no` with a code are both refused as contradictory records.
* The observed result is persisted: `detail["observed_refusal_code"]` beside
  `detail["refusal_code"]` (the expected one) and `detail["precondition_holds"]`,
  and the `observed` outcome value in the artifact reads `refused DEP-04`.

**Regressions** (`tests/phase_5_0_evidence/test_r16_remediation.py` §1):
`DEP-04` fails with the observed value preserved; four further valid non-`J-26`
codes fail; unexpected admission is represented explicitly and fails; the `J-26`
control passes; five malformed or missing-result payloads are refused; both
half-observations are refused; the observed result survives into the written
artifact; the precondition is asserted in both directions; the keyword is
required; a version-1 payload is refused.

---

## 3. EH-R16-3 — the result reports the scope it has

**Conceded.** The coverage loop skipped every required case with no
`BAND_7_SCHEMA` entry, so the three capability cases never entered `missing` and
eight Band-7 records produced `complete=True` with no run record and no
capability observation.

**The option taken is the second one the review offers** — *"explicitly keep the
importer a partial Band-7 result with overall completeness and operational
eligibility withheld"*. No execution evidence is invented, and no join is
implemented.

* `EvidenceResult.outside_scope` names the required cases the importer does not
  observe. The `continue` that skipped them is gone.
* `complete` is replaced by `band_7_coverage_complete`, which is a statement
  about Band 7 and says so in its name.
* `overall_completeness_established` and `eligible_for_operational_acceptance`
  are `False` **unconditionally**, with the reason in their docstrings: the
  importer holds no execution observation, so there is no input from which the
  question could be answered, and answering it from Band 7 alone would answer a
  different question under the same name. A payload that is complete in scope,
  entirely `reviewer_verified`, non-synthetic and all-passing still gets `False`,
  which is asserted.
* Coverage and outcome are separated: `band_7_records_all_passed` and
  `band_7_evidence_holds` are distinct properties, and a failed record covers its
  variant without passing it.
* `structural_disqualifications` replaces the old boolean and names every reason
  the in-scope half would not qualify.
* **The scope is persisted, not only printed.** `write_artifact` now writes an
  envelope — `freedom-blades/phase-5.0/classified-evidence`, version 1 — carrying
  the scope document beside the records, read back and compared before a path is
  reported. An artifact is written for a result that classified **no** record,
  because the scope and the missing evidence are exactly what such a run's reader
  needs; the previous version refused one.
* The CLI never exits 0. Overall completeness is withheld, so there is no result
  it can report as complete.
* The importer's inability to reach an executing boundary is unchanged and is
  asserted twice — in `test_no_execution.py` against the syntax tree, and again
  in the module about this finding.

**Regressions** (§2 of the same file): the capability cases are reported and not
skipped; no payload makes the importer report overall completeness; coverage is
not an outcome; a failed control inside a case does not pass it; mismatched
target, run and digest are refused; a duplicate variant is refused; partial
variants are reported by name; the scope document carries every vocabulary; the
import graph is asserted from the syntax tree.

---

## 4. EH-R16-4 — a missing producer stays a missing producer

**Conceded in full.** Declaring Band 7's cases externally supplied on the
strength of a description of coordinator tooling removed every unresolved entry
from the band and made `is_executable` true again. *"Naming `init-generation` and
a future table does not resolve the evidence dependency."*

* The three cases are **`UnresolvedStep`s again**, under conflict **C-7**, and
  `ConcretePlan.is_executable` is **`False`**. The executor's second gate refuses
  the shipped plan, which is asserted.
* The **input contract survives as documentation**. `ExternalCase` gains
  `producer_artifact_reviewed` (default `False`) and `producer_review_reference`,
  and `resolves_coverage` requires both. Every shipped contract has the default,
  so `check_case_coverage`'s external column is empty and each case is in exactly
  one column. The contract still records who would produce the observation and
  how, and the manifest pins the flags, so turning one on is a digest change and
  a re-review rather than an invisible edit.
* `check_case_coverage`'s docstring states the rule: a named producer and a
  declared procedure are what make the column *safe to use*, not what make it
  applicable.
* Three independent mechanisms stop a record closing a missing producer, each
  sufficient alone: the plan declares the case unresolved and is not executable;
  the importer reports an unresolved case in `unresolved_cases` and never in
  `covered`; and operational eligibility is `False` unconditionally.
* Coverage categories, the manifest, the rendered plan and both CLI summaries
  agree. The dry run reports *"3 documented input contract(s) … of which 0 have a
  reviewed producer artifact"*, and rendered section 5d carries a **Resolves the
  case?** column reading *"no — no reviewed producer artifact exists"* for all
  three.

**No gated Package 5.0 product tooling was built, no table was created, and
nothing was run to resolve this finding.**

**The separate evidence-only producer work, described for later review and not
undertaken.** Scope: three bounded artifacts that arrange one situation each on
the disposable host and record the observation in the reviewed schema — a run of
`init-generation` with `D8` suppressed or `PVR` deleted; a run of the §2.13.2a
probe with a failure injected at one named stage, five times; and a run whose
cleanup did not complete, twice. Each is evidence-only: it must not create the
journal hierarchy, insert a registration row, or become the coordinator tooling
Package 5.0's work packages own. Authority needed, and not held: a maintainer
decision that evidence-only producers may be written at all before the product
work they observe; a decision on whether they may run on `oracle-test` and under
what identity; and Codex's technical review of each producer before any
observation it makes is admitted. Until all three exist the dependency is open,
which is what this submission records.

---

## 5. Changed files

| File | Finding | What changed |
|---|---|---|
| `tools/phase_5_0_evidence/provenance.py` | R16-2 | required `observed_refusal_code`; the three observed-value constants; precondition separated from observation; observed result in `detail` |
| `tools/phase_5_0_evidence/observations.py` | R16-2, R16-3 | schema version 2, `refused` field, `refusal_code_or_none` shape, both agreement rules, observed code passed to the classifier; `outside_scope`; `band_7_*` properties; unconditional withholding; `structural_disqualifications`; `IMPORTER_SCOPE`; `COMPLETENESS_WITHHELD` |
| `tools/phase_5_0_evidence/concrete_plan.py` | R16-4 | `_band_7` emits `UnresolvedStep`s under C-7 beside the documented contracts; `ExternalCase.producer_artifact_reviewed` / `.producer_review_reference` / `.resolves_coverage`; the external column is fed only resolving contracts |
| `tools/phase_5_0_evidence/required_cases.py` | R16-4 | the third column's rule stated |
| `tools/phase_5_0_evidence/review_manifest.py` | all three | `MANIFEST_VERSION` 8 → 9 with its paragraph; the contract flags pinned; the importer scope and withholding pinned |
| `tools/phase_5_0_evidence/execution/evidence_cli.py` | R16-3 | the artifact envelope, `scope_document`, an artifact for a zero-record result, the rewritten summary, never exit 0 |
| `tools/phase_5_0_evidence/execution/cli.py` | R16-4 | the dry-run contract line; rendered section 5d rewritten with the resolves column; the "no unresolved items" text corrected |
| `tests/phase_5_0_evidence/test_r16_remediation.py` | all three | **new**, 39 cases |
| `tests/phase_5_0_evidence/test_r16_c6_c7_c8.py` | R16-2/3/4 | the `importable_plan` fixture; the new schema field; coverage assertions renamed; the eligibility assertion removed; the artifact tests read the envelope; a scope-persistence case added |
| `tests/phase_5_0_evidence/test_bands.py`, `test_concrete_plan.py`, `test_r13_remediation.py`, `test_r14_remediation.py`, `test_executor.py` | R16-2/4 | expectations updated to the new signature and to C-7 being open; the R14 assertions narrowed to C-8 so they fail for their own reason |
| `docs/review/phase-5-0-evidence-harness-c8-ownership-design-r16.md` | R16-1 | **new**, the design for review |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json`, `…-concrete-plan.md` | all | regenerated, never hand-edited |

`tools/phase_5_0_evidence/cleanup.py`, `execution/executor.py` and
`execution/case_program.py` are **unchanged**: they are EH-R16-1's surface.

---

## 6. Verification — exact commands and results

Serially, `TEST_DATABASE_URL` **explicitly unset** throughout. Structural
no-execution tests first, then the focused regressions, then the complete
synthetic harness suite, then the other available suites.

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q tests/phase_5_0_evidence/test_no_execution.py
193 passed

env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q tests/phase_5_0_evidence/test_r16_remediation.py
39 passed

env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q tests/phase_5_0_evidence
1375 passed

env -u TEST_DATABASE_URL /opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
2990 passed, 326 skipped, 1 warning

env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
1610 passed, 1362 skipped

node --test "foundry-module/tests/"*.test.mjs
tests 171, pass 171, fail 0

/opt/discord-bots/venv-web/bin/python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence
clean

git diff --check
clean
```

The harness baseline before this work was **1335**; **40** cases were added.

**Artifacts.** `--manifest-out` and `--render` were run twice into a scratch
directory and compared: **byte-identical**. The committed
`docs/review/phase-5-0-evidence-harness-review-manifest.json` and
`docs/review/phase-5-0-evidence-harness-concrete-plan.md` are those bytes, and a
third regeneration matched the committed files. The manifest's 32 covered sources
were independently re-hashed outside the harness: **0 mismatches**. Manifest
version **9**, harness version `0.7.0-pre-execution`.

**The importer was exercised end to end** against the shipped plan with a
synthetic payload: exit **5**, scope reported, all three Band-7 cases
`unresolved`, all three capability cases `outside this scope`, overall
completeness and operational eligibility **WITHHELD**, zero records classified,
and an artifact written carrying the scope and the missing evidence.

---

## 7. Environment, stated because it changes what the figures mean

**The interpreter is an explicitly local fallback on this host**:
`/opt/discord-bots/venv-web/bin/python` (3.12.3, pytest 8.4.2) for the harness
and web suites and `/opt/discord-bots/venv/bin/python` for the bot suite, which
is the only one here with `discord` importable. **The canonical test interpreter
is `/opt/freedom-blades/runtime/venv-web/bin/python` on `oracle-test`; it exists
on this host as a path and has no pytest, so it establishes nothing about
`oracle-test` and was not used.**

**Every database assertion was skipped, and the skips are the restriction rather
than a pass.** `TEST_DATABASE_URL` was unset for every command above. The bot
suite skipped **326** cases and the web suite **1362**; the documented figure for
a real database run is 80 web skips. Nothing in this submission establishes any
PostgreSQL behaviour.

**Checks not configured and therefore not run:** no formatter, no linter and no
type checker is configured in this repository, and `shellcheck` is not installed.
That is stated rather than reported as a pass. `compileall` and `git diff --check`
are what is configured and both are clean.

**Checks not run by choice:** no `--execute`, no armed boundary, no armed
materializer, no generated vector, no SSH, no `oracle-test` contact,
synchronization or inspection, no provisioning, no database operation, no
destructive drill, no service change and no credential access. Every effect in
every test is injected. `oracle-test` was neither mutated nor read.

**The twelve reviewed target facts remain `UNCONFIRMED`** — the two interpreter
facts and `E7`'s ten — and were not supplied. The maintainer's read-only
preflight authorization remains recorded, remains assigned to Codex, and was not
exercised.

---

## 8. Gate

Package 5.0 remains **not ready**, P5.0-R5 remains **Blocking**, OD-62 remains
**Open**. `is_executable` is **`False`**, so the executor's second gate refuses
the shipped plan before its other five are reached. No execution digest is
approved and none is requested. Migration 0014, product implementation,
deployment, cutover and Package 5.1+ remain outside this assignment and
unauthorized.

Stopping for Codex's independent re-review, and specifically for technical
acceptance of the EH-R16-1 design before it is implemented.
