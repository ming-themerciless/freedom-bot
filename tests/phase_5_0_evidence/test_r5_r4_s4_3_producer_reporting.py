"""C-P5.0-R5-R4, finding P5.0-R5-R3-EVIDENCE-1 — S4-3's producer reporting is truthful.

Codex's review of C-P5.0-R5-R3: the gate is fail-closed, but the evidence model
contradicted it. `observations.producer_mapping()` treated every required case
without a Band-7 schema as having an in-harness producer, so S4-3's row said
`in_harness_producer=True`, named *"this harness's own generated steps"* and
said *"the executor records the step's observation directly"* — while its
`produced_by_plan_steps` was empty and C-S4-3 blocked it. The persisted
`COMPLETENESS_WITHHELD` rationale said every required case outside the Band-7
importer's scope *"is produced by the executed plan"*, which S4-3 is not.

R4 derives in-harness production from the plan's actual step attribution, gives
a case with no producer anywhere a producer and collection text that name none,
and makes the withholding rationale describe both kinds of outside-scope case.
These tests prove that:

* S4-3 reports no in-harness producer, no producing step, no reviewed external
  producer and C-S4-3 as its blocker, and its text names no producer and no
  runnable procedure — in the mapping, the persisted artifact, the manifest and
  the CLI summary alike;
* the three produced capability cases and the three Band-7 contracts keep their
  truthful rows;
* in-harness production follows attribution, not absence from `BAND_7_SCHEMA`;
* S4-3 stays outside the Band-7 importer and cannot be supplied or covered; and
* neither this change, nor C-7's resolution, nor supplied input clears C-S4-3
  or makes the plan executable.
"""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.phase_5_0_evidence import concrete_plan as concrete_plan_module
from tools.phase_5_0_evidence.concrete_plan import (
    S4_3_CONFLICT,
    ConcretePlan,
    ExternalCase,
    build_concrete_plan,
)
from tools.phase_5_0_evidence.errors import ObservationRefused
from tools.phase_5_0_evidence.execution import evidence_cli
from tools.phase_5_0_evidence.execution.evidence_cli import scope_document, write_artifact
from tools.phase_5_0_evidence.observations import (
    BAND_7_SCHEMA,
    COMPLETENESS_WITHHELD,
    Custody,
    SYNTHETIC_TARGET_IDENTITY,
    classify_supplied_observations,
    import_observations,
    producer_mapping,
)
from tools.phase_5_0_evidence.required_cases import REQUIRED_CASES
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES, ReviewManifest

from tests.phase_5_0_evidence.test_r16_c6_c7_c8 import (
    complete_records,
    payload,
    record,
)
from tests.phase_5_0_evidence.test_r5_r2_s4_3_dependency import _capture_step

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCES = {name: (REPOSITORY_ROOT / name).read_bytes() for name in COVERED_SOURCES}
MANIFEST_PATH = REPOSITORY_ROOT / "docs/review/phase-5-0-evidence-harness-review-manifest.json"

CAPABILITY_CASES = (
    "JNL-49-E4-CLEAR-ARCHIVE-IMMUTABLE",
    "JNL-49-E6-CLEAR-ARCHIVE-IMMUTABLE",
    "JNL-50-E5-CLEAR-THEN-DENIED-OPEN",
)

#: R3's text for S4-3's row and rationale. Each one claims a producer exists.
FALSE_PRODUCER = "this harness's own generated steps"
FALSE_PROCEDURE = "the executor records the step's observation directly"
FALSE_RATIONALE = "outside this importer's scope are produced by the executed plan"


@pytest.fixture(scope="module")
def plan() -> ConcretePlan:
    return build_concrete_plan()


def _rows(plan: ConcretePlan) -> dict:
    return {row.case_id: row for row in producer_mapping(plan)}


def _digest(plan: ConcretePlan) -> str:
    return ReviewManifest.build(plan, SOURCES).digest()


def _resolved_band_7(steps) -> None:
    """Band 7 as if C-7 were resolved by hypothetical reviewed producers."""
    for schema in BAND_7_SCHEMA.values():
        steps.external(
            ExternalCase(
                case_id=schema.case_id,
                band=schema.band,
                producer=schema.producer,
                collection_procedure=schema.collection_procedure,
                variants=schema.variants,
                why_not_a_step="hypothetical reviewed producer",
                producer_artifact_reviewed=True,
                producer_review_reference="hypothetical Band-7 review",
            )
        )


def _assert_s4_3_row_is_absent(row) -> None:
    """The one shape S4-3's row may have, wherever it is read from."""
    get = row.get if isinstance(row, dict) else lambda name: getattr(row, name)
    assert get("in_harness_producer") is False
    assert tuple(get("produced_by_plan_steps")) == ()
    assert tuple(get("declared_unresolved_by")) == (S4_3_CONFLICT,)
    producer, procedure = get("producer"), get("collection_procedure")
    assert producer.startswith("none — ")
    assert procedure.startswith("none — ")
    assert S4_3_CONFLICT in producer
    for text in (producer, procedure):
        assert FALSE_PRODUCER not in text
        assert FALSE_PROCEDURE not in text


# ---------------------------------------------------------------------------
# S4-3's row: no producer, no step, no external producer, blocked by C-S4-3
# ---------------------------------------------------------------------------


def test_s4_3_reports_no_producer_of_any_kind(plan) -> None:
    row = _rows(plan)["S4-3"]
    _assert_s4_3_row_is_absent(row)
    assert "S4-3" not in BAND_7_SCHEMA
    assert not [item for item in plan.external_cases if item.case_id == "S4-3"]


def test_s4_3_fields_cannot_be_read_as_a_producer_or_a_procedure(plan) -> None:
    """Neither field names an actor, a step, a path or a runnable procedure, and
    neither is R3's text for a produced case."""
    row = _rows(plan)["S4-3"]
    assert row.producer != FALSE_PRODUCER
    assert row.collection_procedure != FALSE_PROCEDURE
    assert "no step of this plan produces" in row.producer
    assert "no reviewed external producer" in row.producer
    assert "no collection procedure" in row.collection_procedure
    step_ids = {step.step_id for step in plan.steps}
    for text in (row.producer, row.collection_procedure):
        assert not [step_id for step_id in step_ids if f"`{step_id}`" in text]
        assert "systemctl" not in text and "/" not in text


def test_the_partial_capture_step_is_not_an_s4_3_producer(plan) -> None:
    capture = _capture_step(plan)
    row = _rows(plan)["S4-3"]
    assert capture.evidence_case_ids == ()
    assert capture.step_id not in row.produced_by_plan_steps
    assert capture.step_id not in row.producer


# ---------------------------------------------------------------------------
# The other six rows keep their truthful shape
# ---------------------------------------------------------------------------


def test_the_produced_capability_cases_still_report_in_harness_production(plan) -> None:
    rows = _rows(plan)
    for case_id in CAPABILITY_CASES:
        row = rows[case_id]
        assert row.in_harness_producer is True
        assert row.produced_by_plan_steps
        assert row.declared_unresolved_by == ()
        assert row.producer == FALSE_PRODUCER  # true here: steps produce it
        assert row.collection_procedure == FALSE_PROCEDURE


def test_band_7_remains_unresolved_external_input_contracts(plan) -> None:
    rows = _rows(plan)
    for case_id, schema in BAND_7_SCHEMA.items():
        row = rows[case_id]
        assert row.in_harness_producer is False
        assert row.produced_by_plan_steps == ()
        assert row.declared_unresolved_by == ("C-7",)
        assert row.producer == schema.producer
        assert row.collection_procedure == schema.collection_procedure
        assert not row.producer.startswith("none")


def test_in_harness_production_follows_attribution_not_schema_absence(plan) -> None:
    """A non-Band-7 case reports an in-harness producer only while a step
    carries it. Strip one capability case's attribution from a copy of the plan
    and its row reports no producer, exactly as S4-3's does."""
    for row in producer_mapping(plan):
        if row.case_id not in BAND_7_SCHEMA:
            assert row.in_harness_producer is bool(row.produced_by_plan_steps)

    stripped_case = CAPABILITY_CASES[0]
    # `producer_mapping` reads only `steps` and `unresolved`, so a stand-in with
    # those two attributes is enough and needs no re-validated execution plan.
    stripped = SimpleNamespace(
        steps=tuple(
            replace(
                step,
                evidence_case_ids=tuple(
                    case for case in step.evidence_case_ids if case != stripped_case
                ),
            )
            for step in plan.steps
        ),
        unresolved=plan.unresolved,
    )
    row = _rows(stripped)[stripped_case]
    assert row.in_harness_producer is False
    assert row.produced_by_plan_steps == ()
    assert row.producer.startswith("none — ")
    assert row.collection_procedure.startswith("none — ")


# ---------------------------------------------------------------------------
# The persisted withholding rationale
# ---------------------------------------------------------------------------


def test_the_withholding_rationale_does_not_claim_s4_3_is_produced() -> None:
    text = " ".join(COMPLETENESS_WITHHELD)
    assert len(COMPLETENESS_WITHHELD) == 2
    assert FALSE_RATIONALE not in text
    assert "S4-3" in text and S4_3_CONFLICT in text
    assert "no producer" in text


def test_the_rationale_names_every_outside_case_that_has_no_producer(plan) -> None:
    """Tied to the plan, so the fixed text cannot go stale silently: every
    outside-scope case no step produces is named in it with its blocker, and the
    produced outside-scope cases are described as produced by steps."""
    result = classify_supplied_observations([], plan=plan)
    rows = {row.case_id: row for row in result.producers}
    first = COMPLETENESS_WITHHELD[0]
    unproduced = [case for case in result.outside_scope if not rows[case].produced_by_plan_steps]
    produced = [case for case in result.outside_scope if rows[case].produced_by_plan_steps]
    assert unproduced == ["S4-3"]
    assert sorted(produced) == sorted(CAPABILITY_CASES)
    for case in unproduced:
        assert case in first
        for conflict in rows[case].declared_unresolved_by:
            assert conflict in first
    assert "produced by the executed plan's steps" in first
    assert result.withheld == COMPLETENESS_WITHHELD


def test_completeness_and_eligibility_stay_withheld(plan) -> None:
    result = classify_supplied_observations([], plan=plan)
    assert result.overall_completeness_established is False
    assert result.eligible_for_operational_acceptance is False


# ---------------------------------------------------------------------------
# Every serialized representation agrees
# ---------------------------------------------------------------------------


def test_the_persisted_artifact_agrees(plan, tmp_path: Path) -> None:
    digest = _digest(plan)
    result = import_observations(
        payload(complete_records(digest)),
        plan=plan,
        target_identity=SYNTHETIC_TARGET_IDENTITY,
        run_id="synthetic-run-1",
        review_manifest_digest=digest,
    )
    destination = tmp_path / "evidence.json"
    write_artifact(result, destination)
    scope = json.loads(destination.read_text(encoding="utf-8"))["scope"]

    row = next(item for item in scope["producers"] if item["case_id"] == "S4-3")
    _assert_s4_3_row_is_absent(row)
    assert scope["withheld"] == list(COMPLETENESS_WITHHELD)
    assert FALSE_RATIONALE not in " ".join(scope["withheld"])
    assert scope_document(result)["producers"] == scope["producers"]


def test_the_manifest_pins_the_corrected_rationale(plan) -> None:
    body = ReviewManifest.build(plan, SOURCES).as_mapping()
    assert body["supplied_observations"]["withheld"] == list(COMPLETENESS_WITHHELD)
    entry = next(item for item in body["required_cases"] if item["case_id"] == "S4-3")
    assert entry["produced_by"] == []
    assert entry["blocked_by"] == [S4_3_CONFLICT]
    assert entry["supplied_externally"] is False
    assert "S4-3" not in {case["case_id"] for case in body["supplied_observations"]["cases"]}


def test_the_committed_manifest_carries_the_corrected_rationale() -> None:
    committed = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    withheld = committed["supplied_observations"]["withheld"]
    assert withheld == list(COMPLETENESS_WITHHELD)
    assert FALSE_RATIONALE not in MANIFEST_PATH.read_text(encoding="utf-8")


def test_the_cli_summary_and_artifact_agree(
    plan, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    observations = tmp_path / "observations.json"
    observations.write_bytes(payload(complete_records(_digest(plan))))
    artifact = tmp_path / "evidence.json"
    exit_code = evidence_cli.main(
        [
            "--observations",
            str(observations),
            "--run-id",
            "synthetic-run-1",
            "--synthetic",
            "--artifact-out",
            str(artifact),
        ]
    )
    printed = capsys.readouterr().out
    assert exit_code == evidence_cli.INCOMPLETE_EXIT_CODE
    assert FALSE_RATIONALE not in printed
    for reason in COMPLETENESS_WITHHELD:
        assert reason in printed
    assert "S4-3" in printed.split("outside this scope :", 1)[1].splitlines()[0]
    scope = json.loads(artifact.read_text(encoding="utf-8"))["scope"]
    _assert_s4_3_row_is_absent(
        next(item for item in scope["producers"] if item["case_id"] == "S4-3")
    )


# ---------------------------------------------------------------------------
# S4-3 stays outside the importer, and nothing clears C-S4-3
# ---------------------------------------------------------------------------


def test_s4_3_stays_outside_the_importer_and_cannot_be_supplied(plan) -> None:
    result = classify_supplied_observations([], plan=plan)
    assert "S4-3" not in BAND_7_SCHEMA
    assert "S4-3" in result.outside_scope
    assert "S4-3" not in result.unresolved_cases
    assert not [key for key in result.covered if key.startswith("S4-3")]

    digest = _digest(plan)
    rows = complete_records(digest) + [
        record("S4-3", "applied", digest=digest, fields={"matches": "yes"})
    ]
    with pytest.raises(ObservationRefused):
        import_observations(
            payload(rows),
            plan=plan,
            target_identity=SYNTHETIC_TARGET_IDENTITY,
            run_id="synthetic-run-1",
            review_manifest_digest=digest,
        )


def test_c7_resolved_and_supplied_input_leave_c_s4_3_and_its_absent_producer(
    monkeypatch,
) -> None:
    """C-7 resolved by reviewed external producers, every Band-7 variant
    supplied under reviewer-verified custody and classified: S4-3's row is still
    producer-absent, C-S4-3 still blocks, and the plan is not executable."""
    monkeypatch.setattr(concrete_plan_module, "_band_7", _resolved_band_7)
    resolved = build_concrete_plan()
    assert resolved.conflicts() == (S4_3_CONFLICT,)
    assert resolved.is_executable is False

    digest = _digest(resolved)
    result = import_observations(
        payload(
            complete_records(
                digest,
                custody=Custody.REVIEWER_VERIFIED.value,
                target=resolved.target.identity,
            )
        ),
        plan=resolved,
        target_identity=resolved.target.identity,
        run_id="synthetic-run-1",
        review_manifest_digest=digest,
    )
    assert result.records and result.unresolved_cases == ()
    rows = {row.case_id: row for row in result.producers}
    _assert_s4_3_row_is_absent(rows["S4-3"])
    for case_id in BAND_7_SCHEMA:
        assert rows[case_id].in_harness_producer is False
    assert "S4-3" in result.outside_scope
    assert result.overall_completeness_established is False
    assert result.eligible_for_operational_acceptance is False
    assert build_concrete_plan().is_executable is False


def test_the_required_case_table_is_unchanged() -> None:
    assert [case.case_id for case in REQUIRED_CASES] == [
        *CAPABILITY_CASES,
        "JNL-51-PROVENANCE-OMITTED",
        "JNL-47-NO-GENERATION-ON-FAILURE",
        "JNL-47-RECOVERY-STATE",
        "S4-3",
    ]
