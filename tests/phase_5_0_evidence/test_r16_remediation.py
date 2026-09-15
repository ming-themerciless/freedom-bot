"""**R16's independent review, remediated — EH-R16-2, EH-R16-3 and EH-R16-4.**

Three findings, three sections, and one thing they have in common: each was a
place where the harness **reported a conclusion its inputs did not support**.

* **EH-R16-2 (Blocking)** — the observed provenance refusal was replaced by an
  inference. `classify_missing_provenance` built an observed `refused J-26` out
  of APR/PVR absence, which is the *experimental input*, so a payload reporting
  `DEP-04` was stored as a passing `refused J-26`.
* **EH-R16-3 (Important)** — complete coverage omitted the capability cases.
  The coverage loop skipped every required case with no Band-7 schema entry, so
  eight records produced `complete=True` with no run record and no capability
  observation anywhere in the result.
* **EH-R16-4 (Important)** — missing producers were reclassified as resolved.
  Band 7's three cases were declared externally supplied on the strength of a
  description of coordinator tooling that does not exist.

**EH-R16-1 is not here.** Its revised design is
`docs/review/phase-5-0-evidence-harness-c8-ownership-design-r16.md`, submitted
for the technical review checkpoint the original C-8 assignment required and
R16 recorded as not performed. It is not implemented, so there is nothing to
regress against, and a test written against an unimplemented design would be a
test of the design document.

**Nothing here starts a process, reads a host account, opens a socket or
performs a privileged operation.** Every plan is built in memory, every payload
is a synthetic fixture that says so in its own custody field, and
`test_no_execution.py` scans this file with the rest.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.phase_5_0_evidence.concrete_plan import (
    ConcretePlan,
    ExternalCase,
    build_concrete_plan,
)
from tools.phase_5_0_evidence.errors import ObservationRefused, PlanRefused
from tools.phase_5_0_evidence.execution.evidence_cli import (
    ArtifactRefused,
    scope_document,
    write_artifact,
)
from tools.phase_5_0_evidence.observations import (
    BAND_7_SCHEMA,
    OBSERVATION_SCHEMA,
    OBSERVATION_SCHEMA_VERSION,
    SYNTHETIC_TARGET_IDENTITY,
    Custody,
    import_observations,
    producer_mapping,
)
from tools.phase_5_0_evidence.provenance import (
    EXPECTED_OMISSION_REFUSAL,
    OBSERVED_ADMITTED,
    OBSERVED_PRECONDITION_UNMET,
    classify_missing_provenance,
)
from tools.phase_5_0_evidence.records import Status
from tools.phase_5_0_evidence.required_cases import (
    REQUIRED_CASES,
    check_case_coverage,
)
from tools.phase_5_0_evidence.review_manifest import (
    COVERED_SOURCES,
    MANIFEST_VERSION,
    ReviewManifest,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCES = {
    name: (REPOSITORY_ROOT / name).read_bytes() for name in COVERED_SOURCES
}


@pytest.fixture(scope="module")
def plan() -> ConcretePlan:
    return build_concrete_plan()


def _digest(plan: ConcretePlan) -> str:
    return ReviewManifest.build(plan, SOURCES).digest()


def _importable(plan: ConcretePlan) -> ConcretePlan:
    """The shipped plan with Band 7's unresolved entries removed — a fixture.

    The shipped plan declares all three Band-7 cases unresolved (EH-R16-4), so
    nothing supplied can be counted covered against it — which is the property
    §3 asserts. The classification behaviour EH-R16-2 is about can only be
    exercised against a plan that does not block it, so §1 uses this. It creates
    no producer and resolves nothing; every result it yields still has
    `eligible_for_operational_acceptance` `False`.
    """
    return ConcretePlan(
        execution_plan=plan.execution_plan,
        cleanup_plan=plan.cleanup_plan,
        unresolved=(),
        external_cases=plan.external_cases,
    )


ABSENT_ARTIFACTS = {
    "journal_present": "no",
    "seal_present": "no",
    "current_present": "no",
    "close_present": "no",
}


def _record(case_id: str, variant: str, *, digest: str, fields: dict) -> dict:
    return {
        "case_id": case_id,
        "variant": variant,
        "target_identity": SYNTHETIC_TARGET_IDENTITY,
        "run_id": "synthetic-run-1",
        "review_manifest_digest": digest,
        "custody": Custody.SYNTHETIC_FIXTURE.value,
        "collected_by": "independent reviewer",
        "collected_at": "2026-09-09",
        "fields": fields,
    }


def _provenance_fields(**overrides) -> dict:
    fields = {
        "apr_present": "yes",
        "pvr_present": "no",
        "refused": "yes",
        "refusal_code": EXPECTED_OMISSION_REFUSAL,
        **ABSENT_ARTIFACTS,
        "generation_row_present": "no",
        "probe_ran": "no",
    }
    fields.update(overrides)
    return fields


def _all_records(digest: str, **provenance) -> list[dict]:
    rows = [
        _record(
            "JNL-51-PROVENANCE-OMITTED",
            "provenance-omitted",
            digest=digest,
            fields=_provenance_fields(**provenance),
        )
    ]
    for stage in BAND_7_SCHEMA["JNL-47-NO-GENERATION-ON-FAILURE"].variants:
        rows.append(
            _record(
                "JNL-47-NO-GENERATION-ON-FAILURE",
                stage,
                digest=digest,
                fields={**ABSENT_ARTIFACTS, "generation_row_present": "no"},
            )
        )
    for variant in BAND_7_SCHEMA["JNL-47-RECOVERY-STATE"].variants:
        rows.append(
            _record(
                "JNL-47-RECOVERY-STATE",
                variant,
                digest=digest,
                fields={
                    "exit_code": "3",
                    "state": "S-B",
                    "residue_path_count": "2",
                    "generation_present": "no",
                    "database_row_present": "no",
                    "next_run_refuses": "yes",
                    "residue_recovery_named": "yes",
                    "configuration_capture_retained": "no",
                    "configuration_recovery_named": "no",
                },
            )
        )
    return rows


def _payload(rows: list[dict], *, version: int = OBSERVATION_SCHEMA_VERSION) -> bytes:
    return json.dumps(
        {
            "schema": OBSERVATION_SCHEMA,
            "schema_version": version,
            "records": rows,
        }
    ).encode("utf-8")


def _import(plan: ConcretePlan, rows: list[dict], **overrides):
    keywords = dict(
        plan=plan,
        target_identity=SYNTHETIC_TARGET_IDENTITY,
        run_id="synthetic-run-1",
        review_manifest_digest=_digest(plan),
    )
    keywords.update(overrides)
    return import_observations(_payload(rows), **keywords)


def _refusal_record(result):
    return next(
        record for record in result.records if record.case_id == "JNL-51-g-refusal"
    )


# ---------------------------------------------------------------------------
# EH-R16-2 — the observed provenance result reaches the classifier
# ---------------------------------------------------------------------------


def test_the_expected_refusal_comes_from_the_classifier_and_not_from_a_record(
    plan,
) -> None:
    """The expectation is a module constant, and no field reaches it.

    This is the property the rest of §1 rests on: a record can fail to match the
    expected value and can never choose it. `EXPECTED_OMISSION_REFUSAL` is
    `provenance.py`'s own, the schema has no field for an expected value, and the
    only refusal a record carries is an **observed** one.
    """
    assert EXPECTED_OMISSION_REFUSAL == "J-26"
    schema = BAND_7_SCHEMA["JNL-51-PROVENANCE-OMITTED"]
    names = {spec.name for spec in schema.fields}
    assert "refusal_code" in names and "refused" in names
    assert not any("expected" in name for name in names)


def test_the_observed_refusal_is_classified_and_not_inferred(plan) -> None:
    """**EH-R16-2's exact reproduction, now failing evidence.**

    R16 took the complete synthetic payload, changed only the provenance
    record's refusal code from `J-26` to `DEP-04`, and got a record with status
    **passed** and observed value **refused J-26**. The same payload now
    classifies `failed`, and the observed value is the code the producer
    reported.
    """
    fixture = _importable(plan)
    result = _import(
        fixture, _all_records(_digest(fixture), refusal_code="DEP-04")
    )
    record = _refusal_record(result)

    assert record.status is Status.FAILED
    assert record.observed.value == "refused DEP-04"
    assert record.expected.value == "refused J-26"
    assert record.detail["observed_refusal_code"] == "DEP-04"


@pytest.mark.parametrize("code", ["DEP-04", "J-27", "J-28", "DEP-01", "DEP-09"])
def test_any_valid_code_that_is_not_the_expected_one_fails(plan, code) -> None:
    """A well-formed unexpected outcome stays failed evidence.

    *"Malformed payloads may be refused, but a well-formed unexpected outcome
    must remain failed/inconclusive evidence and must not be rewritten as the
    expected result."* Every code here is a real member of the deploy or
    consumer refusal families, so none of them is malformed.
    """
    fixture = _importable(plan)
    result = _import(fixture, _all_records(_digest(fixture), refusal_code=code))
    record = _refusal_record(result)
    assert record.status is Status.FAILED
    assert record.observed.value == f"refused {code}"


def test_an_unexpected_admission_is_represented_explicitly(plan) -> None:
    """`refused=no` is a result, not a missing field.

    Version 1 of the schema could not express *"the program did not refuse"* at
    all, which is why the classifier inferred one. It is now a record the
    importer accepts, a value the comparison fails against, and a sentence in
    the artifact.
    """
    fixture = _importable(plan)
    result = _import(
        fixture,
        _all_records(_digest(fixture), refused="no", refusal_code="none"),
    )
    record = _refusal_record(result)
    assert record.status is Status.FAILED
    assert record.observed.value == OBSERVED_ADMITTED
    assert record.detail["observed_refusal_code"] == "none"


def test_the_expected_refusal_is_the_control(plan) -> None:
    """The positive direction, so the failures above are about the values."""
    fixture = _importable(plan)
    result = _import(fixture, _all_records(_digest(fixture)))
    record = _refusal_record(result)
    assert record.status is Status.PASSED
    assert record.observed.value == "refused J-26"
    assert record.detail["observed_refusal_code"] == "J-26"


@pytest.mark.parametrize(
    ("label", "mutate"),
    [
        ("a missing refused field", lambda fields: fields.pop("refused")),
        ("a missing refusal code", lambda fields: fields.pop("refusal_code")),
        (
            "an unreadable refusal code",
            lambda fields: fields.update({"refusal_code": "J-2"}),
        ),
        (
            "a refusal code that is free text",
            lambda fields: fields.update({"refusal_code": "it refused"}),
        ),
        (
            "an unreadable refused field",
            lambda fields: fields.update({"refused": "maybe"}),
        ),
    ],
)
def test_a_missing_or_unreadable_result_is_refused(plan, label, mutate) -> None:
    """Malformed is refused; it is never read as either outcome.

    An unmade observation must not become a result, and the two ways it could
    have — a key nobody supplied and a value that is not the shape its field can
    have — are refusals rather than defaults.
    """
    fixture = _importable(plan)
    rows = _all_records(_digest(fixture))
    mutate(rows[0]["fields"])
    with pytest.raises(ObservationRefused):
        _import(fixture, rows)


@pytest.mark.parametrize(
    ("label", "overrides"),
    [
        ("a refusal with no code", {"refused": "yes", "refusal_code": "none"}),
        ("a code with no refusal", {"refused": "no", "refusal_code": "J-26"}),
    ],
)
def test_half_an_observation_is_refused(plan, label, overrides) -> None:
    """The two halves of one observation have to agree with each other."""
    fixture = _importable(plan)
    rows = _all_records(_digest(fixture), **overrides)
    with pytest.raises(ObservationRefused):
        _import(fixture, rows)


def test_the_observed_result_survives_into_the_persisted_artifact(
    plan, tmp_path: Path
) -> None:
    """*"Preserve the observed result in the persisted artifact."*"""
    fixture = _importable(plan)
    result = _import(
        fixture, _all_records(_digest(fixture), refusal_code="DEP-04")
    )
    destination = tmp_path / "evidence.json"
    write_artifact(result, destination)

    document = json.loads(destination.read_text(encoding="utf-8"))
    stored = next(
        item
        for item in document["records"]
        if item["case_id"] == "JNL-51-g-refusal"
    )
    assert stored["observed"]["value"] == "refused DEP-04"
    assert stored["expected"]["value"] == "refused J-26"
    assert stored["detail"]["observed_refusal_code"] == "DEP-04"
    assert stored["status"] == "failed"


def test_the_precondition_is_a_precondition_and_not_the_observation() -> None:
    """APR/PVR absence is the situation, never the program's answer.

    Both directions. A run in which nothing was omitted fails even when the
    expected refusal was observed, because the case is the omission; and a run
    in which the omission held fails when the program admitted.
    """
    from tools.phase_5_0_evidence.provenance import (
        ApprovedRevision,
        FileFacts,
        ProvenanceRecord,
    )

    apr = ApprovedRevision(
        component="sheet-writer",
        source_commit="c" * 40,
        source_tree_id="t" * 40,
        source_manifest_digest="d" * 64,
        review_reference="r",
        approved_by="root",
        approved_at="2026-09-09",
        facts=FileFacts(True, "root", "root", "0444"),
    )
    pvr = ProvenanceRecord(
        component="sheet-writer",
        source_commit="c" * 40,
        source_tree_id="t" * 40,
        source_manifest_digest="d" * 64,
        deployment_manifest_digest="e" * 64,
        dependency_lock_digest="f" * 64,
        deployed_at="2026-09-09",
        deployed_by="root",
        facts=FileFacts(True, "root", "root", "0444"),
    )
    nothing_omitted = classify_missing_provenance(
        apr=apr,
        pvr=pvr,
        probe_ran=False,
        generation_artifacts=(),
        generation_row_inserted=False,
        observed_refusal_code=EXPECTED_OMISSION_REFUSAL,
    )
    assert nothing_omitted[0].status is Status.FAILED
    assert nothing_omitted[0].observed.value == OBSERVED_PRECONDITION_UNMET

    admitted = classify_missing_provenance(
        apr=None,
        pvr=None,
        probe_ran=False,
        generation_artifacts=(),
        generation_row_inserted=False,
        observed_refusal_code=None,
    )
    assert admitted[0].status is Status.FAILED
    assert admitted[0].observed.value == OBSERVED_ADMITTED


def test_the_classifier_cannot_be_called_without_the_observation() -> None:
    """No default. A caller that forgot the observation is an error, not a pass.

    The defect EH-R16-2 names is exactly a classifier deciding the observed value
    for itself, so the keyword is required and a missing one is a `TypeError`
    rather than an inferred `J-26`.
    """
    with pytest.raises(TypeError):
        classify_missing_provenance(  # type: ignore[call-arg]
            apr=None,
            pvr=None,
            probe_ran=False,
            generation_artifacts=(),
            generation_row_inserted=False,
        )


def test_a_payload_written_under_the_previous_schema_is_refused(plan) -> None:
    """An earlier version meant something else, so it is refused, not reread."""
    assert OBSERVATION_SCHEMA_VERSION == 3
    fixture = _importable(plan)
    with pytest.raises(ObservationRefused):
        import_observations(
            _payload(_all_records(_digest(fixture)), version=1),
            plan=fixture,
            target_identity=SYNTHETIC_TARGET_IDENTITY,
            run_id="synthetic-run-1",
            review_manifest_digest=_digest(fixture),
        )


# ---------------------------------------------------------------------------
# EH-R16-3 — the result reports the scope it actually has
# ---------------------------------------------------------------------------


def test_required_cases_outside_the_schema_are_reported_and_not_skipped(
    plan,
) -> None:
    """**EH-R16-3's exact reproduction.**

    R16: *"The coverage loop skips every required case absent from
    `BAND_7_SCHEMA`. … Eight Band-7 input records yield `complete=True`,
    `missing=()`, without a run record or any capability observation."* The three
    capability cases are now named in `outside_scope`, and their presence there
    is on its own enough to withhold overall completeness.
    """
    fixture = _importable(plan)
    result = _import(fixture, _all_records(_digest(fixture)))

    capability_cases = {
        case.case_id
        for case in REQUIRED_CASES
        if case.case_id not in BAND_7_SCHEMA
    }
    assert capability_cases
    assert set(result.outside_scope) == capability_cases
    assert result.band_7_coverage_complete is True
    assert result.overall_completeness_established is False
    assert result.eligible_for_operational_acceptance is False


def test_no_payload_makes_the_importer_report_overall_completeness(plan) -> None:
    """Withheld is not a computation that comes out false today.

    A payload that is complete in scope, entirely `reviewer_verified`, not
    synthetic and every record passing is the best input this importer can
    receive, and it still establishes nothing about the harness. The importer
    holds no execution observation, so there is no input from which the question
    could be answered.
    """
    fixture = _importable(plan)
    rows = _all_records(_digest(fixture))
    for row in rows:
        row["custody"] = Custody.REVIEWER_VERIFIED.value
        row["target_identity"] = plan.target.identity
    result = _import(
        fixture,
        rows,
        target_identity=plan.target.identity,
    )
    assert result.band_7_evidence_holds is True
    assert result.structural_disqualifications == ()
    assert result.overall_completeness_established is False
    assert result.eligible_for_operational_acceptance is False
    assert len(result.withheld) == 2


def test_coverage_is_not_an_outcome(plan) -> None:
    """A failed record covers its variant and does not pass it.

    *"Distinguish coverage from passing outcomes."* A `DEP-04` provenance record
    is a validated record for the only variant its case has, so coverage is
    complete; the record failed, so the evidence does not hold.
    """
    fixture = _importable(plan)
    result = _import(
        fixture, _all_records(_digest(fixture), refusal_code="DEP-04")
    )
    assert result.band_7_coverage_complete is True
    assert result.band_7_records_all_passed is False
    assert result.band_7_evidence_holds is False
    assert any(
        "not every classified record passed" in problem
        for problem in result.structural_disqualifications
    )


def test_a_failed_control_inside_a_case_does_not_pass_it(plan) -> None:
    """A generation artifact surviving the refusal fails its own record.

    The `JNL-51` case is four records, and three of them are controls about
    things that must not have happened. One of them failing is a failed case,
    not a differently covered one.
    """
    fixture = _importable(plan)
    result = _import(
        fixture, _all_records(_digest(fixture), journal_present="yes")
    )
    statuses = {
        record.case_id: record.status
        for record in result.records
        if record.case_id.startswith("JNL-51-")
    }
    assert statuses["JNL-51-g-refusal"] is Status.PASSED
    assert statuses["JNL-51-g-no-artifact"] is Status.FAILED
    assert result.band_7_coverage_complete is True
    assert result.band_7_evidence_holds is False


@pytest.mark.parametrize(
    ("label", "overrides"),
    [
        ("a mismatched target", {"target_identity": "somewhere-else"}),
        ("a mismatched run", {"run_id": "another-run"}),
        ("a mismatched digest", {"review_manifest_digest": "0" * 64}),
    ],
)
def test_a_mismatched_binding_is_refused_rather_than_scoped(
    plan, label, overrides
) -> None:
    """A record is bound to the target, run and reviewed plan it names."""
    fixture = _importable(plan)
    rows = _all_records(_digest(fixture))
    rows[0].update(overrides)
    with pytest.raises(ObservationRefused):
        _import(fixture, rows)


def test_a_duplicate_variant_is_refused_rather_than_counted_twice(plan) -> None:
    fixture = _importable(plan)
    rows = _all_records(_digest(fixture))
    rows.append(dict(rows[3]))
    with pytest.raises(ObservationRefused):
        _import(fixture, rows)


def test_partial_variants_are_reported_by_name(plan) -> None:
    """Three of five stages supplied is not a covered case."""
    fixture = _importable(plan)
    rows = [
        row
        for row in _all_records(_digest(fixture))
        if row["variant"] not in ("stage-2", "stage-4")
    ]
    result = _import(fixture, rows)
    assert set(result.missing) == {
        "JNL-47-NO-GENERATION-ON-FAILURE#stage-2",
        "JNL-47-NO-GENERATION-ON-FAILURE#stage-4",
    }
    assert result.band_7_coverage_complete is False
    assert result.overall_completeness_established is False


def test_the_scope_document_carries_every_vocabulary(plan) -> None:
    """The scope a reviewer reads is derived, never supplied by a record."""
    fixture = _importable(plan)
    result = _import(fixture, _all_records(_digest(fixture)))
    document = scope_document(result)

    assert "Band 7 supplied observations only" in document["scope"]
    assert document["covered"] == list(result.covered)
    assert document["missing"] == []
    assert document["outside_scope"] == list(result.outside_scope)
    assert document["overall_completeness_established"] is False
    assert document["eligible_for_operational_acceptance"] is False
    assert len(document["withheld"]) == 2
    assert {row["case_id"] for row in document["producers"]} == {
        case.case_id for case in REQUIRED_CASES
    }


def test_the_importer_still_cannot_reach_an_executing_boundary() -> None:
    """The C-7 property EH-R16-3's correction must not have weakened.

    `test_no_execution.py` asserts the import graph against the syntax tree; this
    asserts the same thing from the other side, so a refactor that added a
    boundary import would fail in the module about the finding as well as in the
    structural suite.
    """
    import ast

    import tools.phase_5_0_evidence.execution.evidence_cli as module

    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
            imported.update(alias.name for alias in node.names)
    assert not {"boundary", "executor", "materializer", "cli"} & imported
    assert not any(
        name.endswith((".boundary", ".executor", ".materializer", ".cli"))
        for name in imported
    )


# ---------------------------------------------------------------------------
# EH-R16-4 — a missing producer stays a missing producer
# ---------------------------------------------------------------------------


def test_band_7_declares_its_three_producers_unresolved(plan) -> None:
    """**EH-R16-4's required correction.**

    *"Restore explicit unresolved status for the three Band-7 producers unless an
    actual reviewed producer artifact and concrete collection procedure already
    exist."* None does.
    """
    blocked = {
        case_id
        for item in plan.unresolved
        for case_id in item.evidence_case_ids
    }
    assert blocked == set(BAND_7_SCHEMA)
    assert {item.conflict_id for item in plan.unresolved} == {"C-7"}
    assert plan.is_executable is False


def test_a_documented_contract_occupies_no_coverage_column(plan) -> None:
    """*"A description of future `init-generation` tooling is not a producer."*

    The input contract survives — the shape a reviewed observation would have to
    have is worth pinning — and it resolves nothing: `producer_artifact_reviewed`
    is `False` for every entry, so `resolves_coverage` is `False`, so
    `check_case_coverage`'s third column is empty and the case is unresolved.
    """
    assert plan.external_cases
    for contract in plan.external_cases:
        assert contract.producer_artifact_reviewed is False
        assert contract.producer_review_reference == ""
        assert contract.resolves_coverage is False
        # and the contract still says who and how, which is what it is for
        assert contract.producer.strip()
        assert contract.collection_procedure.strip()
        assert contract.variants


def test_the_third_column_needs_a_producer_and_not_a_description() -> None:
    """`check_case_coverage` is unchanged and is fed an empty external list.

    Asserted from both sides. A case in no column is refused, which is the
    EH-R13-4 property; and the shipped plan's Band-7 cases reach the checker
    through `declared_unresolved`, never through `supplied_externally`.
    """
    with pytest.raises(PlanRefused):
        check_case_coverage(produced=[], declared_unresolved=[], supplied_externally=[])

    # A case in two columns is refused, so a plan cannot both declare a producer
    # missing and claim it supplies the case anyway.
    with pytest.raises(PlanRefused):
        check_case_coverage(
            produced=[],
            declared_unresolved=[case.case_id for case in REQUIRED_CASES],
            supplied_externally=["JNL-51-PROVENANCE-OMITTED"],
        )


def test_a_contract_claiming_a_producer_must_name_its_review() -> None:
    """The escape hatch exists and is gated, in both directions."""
    common = dict(
        case_id="JNL-51-PROVENANCE-OMITTED",
        band="provenance",
        producer="a producer",
        collection_procedure="a procedure",
        variants=("provenance-omitted",),
        why_not_a_step="it is not a vector",
    )
    with pytest.raises(PlanRefused):
        ExternalCase(**common, producer_artifact_reviewed=True)
    with pytest.raises(PlanRefused):
        ExternalCase(**common, producer_review_reference="some review")

    resolved = ExternalCase(
        **common,
        producer_artifact_reviewed=True,
        producer_review_reference="a review that accepted the producer",
    )
    assert resolved.resolves_coverage is True
    assert ExternalCase(**common).resolves_coverage is False


def test_supplied_records_cannot_close_a_missing_producer(plan) -> None:
    """The whole of EH-R16-4, asserted against the **shipped** plan.

    A payload that is complete, well formed and correctly bound covers nothing,
    classifies nothing and closes nothing, because the plan declares all three
    cases unresolved. This is the assertion the review asked for: *"Tests must
    prove that supplied records cannot close a missing producer."*
    """
    result = _import(plan, _all_records(_digest(plan)))

    assert result.covered == ()
    assert result.records == ()
    assert set(result.unresolved_cases) == set(BAND_7_SCHEMA)
    assert result.band_7_coverage_complete is False
    assert result.overall_completeness_established is False
    assert result.eligible_for_operational_acceptance is False
    assert any(
        "declares these required cases unresolved" in problem
        for problem in result.structural_disqualifications
    )


def test_the_producer_mapping_reports_the_dependency_as_open(plan) -> None:
    """The table the handback carries says *unresolved*, and says by what."""
    rows = {row.case_id: row for row in producer_mapping(plan)}
    for case_id in BAND_7_SCHEMA:
        assert rows[case_id].declared_unresolved_by == ("C-7",)
        assert rows[case_id].produced_by_plan_steps == ()
        assert rows[case_id].in_harness_producer is False


def test_the_manifest_pins_whether_a_contract_resolves_anything(plan) -> None:
    """A change from documentation to resolution is a digest change.

    The whole mechanism would be worthless if flipping `producer_artifact_
    reviewed` were invisible to the reviewer: the point of the flag is that
    turning it on is a re-review, and that is what pinning it in the manifest
    makes true.
    """
    body = ReviewManifest.build(plan, SOURCES).as_mapping()
    contracts = body["external_cases"]
    assert contracts
    for contract in contracts:
        assert contract["producer_artifact_reviewed"] is False
        assert contract["resolves_coverage"] is False
    # **C-P5.0-LAB-I, 2026-09-13.** The manifest version moves to 11 because the
    # covered source set and the reviewed verb table both change; what this test
    # is about does not. The supplied-observation schema stays at 3, the three
    # contracts still resolve nothing, and `is_executable` stays False.
    assert body["manifest_version"] == MANIFEST_VERSION == 12
    assert body["supplied_observations"]["schema_version"] == 3
    assert "Band 7 supplied observations only" in (
        body["supplied_observations"]["importer_scope"]
    )
    assert len(body["supplied_observations"]["withheld"]) == 2
    assert {item["conflict_id"] for item in body["unresolved"]} == {"C-7"}


def test_the_executor_gate_refuses_a_plan_with_a_missing_producer(plan) -> None:
    """`is_executable` is `False`, so no run can be classified at all.

    That is the structural half of EH-R13-4, and EH-R16-4 restores it: the
    executor's second gate refuses a plan carrying an unresolved conflict, so a
    complete-harness success cannot be produced with a required band missing.
    """
    from tools.phase_5_0_evidence.execution.executor import (
        ExecutingRunner,
        ExecutorRefused,
    )

    with pytest.raises(ExecutorRefused) as refusal:
        ExecutingRunner(
            plan=plan,
            boundary=_NeverRuns(),
            reviewed_digest="0" * 64,
            confirmation_token="wrong",
            source_bytes={},
        )
    assert "unresolved conflicts" in str(refusal.value)
    assert "C-7" in str(refusal.value)


class _NeverRuns:
    """A boundary that refuses to be called. Asserting the gate refuses is only
    meaningful if the object behind it could not have run anything either way."""

    def run(self, **_: object):  # pragma: no cover - never reached
        raise AssertionError("the gate was supposed to refuse before this")
