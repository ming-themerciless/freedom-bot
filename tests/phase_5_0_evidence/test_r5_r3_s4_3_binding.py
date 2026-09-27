"""C-P5.0-R5-R3, finding P5.0-R5-R2-PLAN-1 — S4-3's producer gate fails closed.

Codex's review of C-P5.0-R5-R2: `SandboxAttestationProducer` carried two strings
and refused only blank ones, so `SandboxAttestationProducer("x", "y")` together
with a complete vector made `s4_3_dependency_gaps()` return nothing. Nothing
bound those labels to an accepted review, a reviewed artifact, the deployed unit
or an actual `SystemdIdentity` producer, and the R2 tests treated explicitly
hypothetical labels as a complete producer.

R3 removes the class and the resolved branch. These tests prove that:

* no metadata value — a string, a path, a boolean, a digest or a description of
  a review — can clear C-S4-3, because there is no parameter or module attribute
  that reads one;
* the two producer requirements are always reported unmet, and the current
  vector is still insufficient;
* supplied observations, an `ExternalCase`, a PASSED classification and the
  removal or resolution of C-7 cannot clear it, alone or together;
* even replacing the gap predicate does not clear it, so resolving C-S4-3 needs
  a code change to the generator plus its independent review; and
* S4-3 is a canonical required case, so deleting both its unresolved
  declaration and its step attribution is refused by `check_case_coverage`.

No test here constructs a complete reviewed producer: there is no success branch
to exercise, and the tests assert that there is none.
"""
from __future__ import annotations

import inspect
from dataclasses import replace
from pathlib import Path

import pytest

from tools.phase_5_0_evidence import concrete_plan as concrete_plan_module
from tools.phase_5_0_evidence.approved_target import APPROVED_TARGET
from tools.phase_5_0_evidence.concrete_plan import (
    S4_3_CONFLICT,
    S4_3_UNMET_PRODUCER_REQUIREMENTS,
    ConcretePlan,
    ExternalCase,
    build_concrete_plan,
    s4_3_dependency_gaps,
)
from tools.phase_5_0_evidence.errors import ObservationRefused, PlanRefused
from tools.phase_5_0_evidence.observations import (
    BAND_7_SCHEMA,
    Custody,
    SuppliedObservation,
    classify_supplied_observations,
    producer_mapping,
)
from tools.phase_5_0_evidence.records import Status
from tools.phase_5_0_evidence.required_cases import (
    REQUIRED_CASES,
    check_case_coverage,
)
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES, ReviewManifest
from tools.phase_5_0_evidence.unit_sandbox import (
    CANONICAL_PROBE_PATH,
    COMPARED_PROPERTIES,
)
from tests.phase_5_0_evidence.unit_sandbox_fixtures import classify

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

#: Metadata of every shape R2's gate accepted or a later edit might try. None of
#: it is a reviewed deployed unit, a reviewed `SystemdIdentity` producer or the
#: binding between them.
METADATA_ONLY_VALUES = (
    "x",
    "y",
    "hypothetical deployed-unit review",
    "Codex review of C-P5.0-R5-R3, accepted 2026-09-23",
    "docs/review/phase-5-0-security-review.md",
    "/etc/systemd/system/freedom-sheet-writer.service",
    "/usr/lib/systemd/systemd",
    "a" * 64,
    "sha256:" + "0" * 64,
    True,
    1,
    ("unit review", "identity review"),
    {"deployed_unit_review_reference": "x", "systemd_identity_producer_review_reference": "y"},
)

#: Every module attribute name a producer declaration has had or might plausibly
#: be given. The generator reads none of them.
PRODUCER_ATTRIBUTE_NAMES = (
    "S4_3_PRODUCER",
    "S4_3_REVIEWED_PRODUCER",
    "S4_3_PRODUCER_REVIEWED",
    "SYSTEMD_IDENTITY_PRODUCER",
    "DEPLOYED_UNIT_REVIEW",
)


@pytest.fixture(scope="module")
def plan() -> ConcretePlan:
    return build_concrete_plan()


def _s4_3_items(plan: ConcretePlan):
    return [item for item in plan.unresolved if item.conflict_id == S4_3_CONFLICT]


def _declares_s4_3(plan: ConcretePlan) -> bool:
    items = _s4_3_items(plan)
    return (
        len(items) == 1
        and items[0].evidence_case_ids == ("S4-3",)
        and not [step for step in plan.steps if "S4-3" in step.evidence_case_ids]
        and plan.is_executable is False
    )


def _complete_vector_gaps() -> tuple[str, ...]:
    return s4_3_dependency_gaps(
        requested_properties=COMPARED_PROPERTIES,
        substituted_path=CANONICAL_PROBE_PATH,
    )


def _resolved_band_7(steps) -> None:
    """Band 7 as if C-7 were resolved: every case supplied externally by a
    hypothetical reviewed producer, so it occupies the external column."""
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


# ---------------------------------------------------------------------------
# No metadata can satisfy the producer requirements
# ---------------------------------------------------------------------------


def test_the_label_only_producer_is_gone() -> None:
    for name in ("SandboxAttestationProducer", "S4_3_PRODUCER"):
        assert not hasattr(concrete_plan_module, name)
        assert name not in concrete_plan_module.__all__


def test_the_gap_function_accepts_no_producer_argument() -> None:
    parameters = inspect.signature(s4_3_dependency_gaps).parameters
    assert set(parameters) == {"requested_properties", "substituted_path"}
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in parameters.values()
    )


@pytest.mark.parametrize("value", METADATA_ONLY_VALUES, ids=repr)
def test_metadata_cannot_be_passed_as_a_producer(value) -> None:
    with pytest.raises(TypeError):
        s4_3_dependency_gaps(  # type: ignore[misc]
            value,
            requested_properties=COMPARED_PROPERTIES,
            substituted_path=CANONICAL_PROBE_PATH,
        )
    with pytest.raises(TypeError):
        s4_3_dependency_gaps(  # type: ignore[call-arg]
            producer=value,
            requested_properties=COMPARED_PROPERTIES,
            substituted_path=CANONICAL_PROBE_PATH,
        )


@pytest.mark.parametrize("value", METADATA_ONLY_VALUES, ids=repr)
@pytest.mark.parametrize("name", PRODUCER_ATTRIBUTE_NAMES)
def test_installing_metadata_on_the_module_cannot_clear_c_s4_3(
    monkeypatch, name, value
) -> None:
    monkeypatch.setattr(concrete_plan_module, name, value, raising=False)
    assert _declares_s4_3(build_concrete_plan())


def test_the_producer_requirements_are_unmet_even_with_a_complete_vector() -> None:
    """The best the plan-derived half can do still leaves both producer gaps. No
    currently constructible input represents a complete reviewed producer."""
    assert _complete_vector_gaps() == S4_3_UNMET_PRODUCER_REQUIREMENTS
    assert len(S4_3_UNMET_PRODUCER_REQUIREMENTS) == 2
    assert "`freedom-sheet-writer.service`" in S4_3_UNMET_PRODUCER_REQUIREMENTS[0]
    assert "drop-in policy" in S4_3_UNMET_PRODUCER_REQUIREMENTS[0]
    assert "`unit_sandbox.SystemdIdentity`" in S4_3_UNMET_PRODUCER_REQUIREMENTS[1]
    assert "binding" in S4_3_UNMET_PRODUCER_REQUIREMENTS[1]


@pytest.mark.parametrize(
    "requested, path",
    [
        (COMPARED_PROPERTIES, CANONICAL_PROBE_PATH),
        (COMPARED_PROPERTIES[:2], CANONICAL_PROBE_PATH),
        ((), "/elsewhere"),
        ((*COMPARED_PROPERTIES, *COMPARED_PROPERTIES), CANONICAL_PROBE_PATH),
    ],
)
def test_the_gap_list_is_never_empty(requested, path) -> None:
    gaps = s4_3_dependency_gaps(requested_properties=requested, substituted_path=path)
    assert gaps
    assert set(S4_3_UNMET_PRODUCER_REQUIREMENTS) <= set(gaps)


def test_the_current_vector_remains_insufficient(plan) -> None:
    item = _s4_3_items(plan)[0]
    assert "requests 2 of 12 compared properties" in item.why_not_a_vector
    for requirement in S4_3_UNMET_PRODUCER_REQUIREMENTS:
        assert requirement in item.why_not_a_vector
    assert "S4_3_PRODUCER" not in item.what_would_resolve_it
    assert "No review reference, label, path, digest or flag" in (
        item.what_would_resolve_it
    )


# ---------------------------------------------------------------------------
# Nothing outside the generator clears it, alone or combined
# ---------------------------------------------------------------------------


def test_c7_removed_leaves_c_s4_3(plan) -> None:
    constructed = replace(
        plan,
        unresolved=tuple(item for item in plan.unresolved if item.conflict_id != "C-7"),
    )
    assert constructed.conflicts() == (S4_3_CONFLICT,)
    assert constructed.is_executable is False


def test_c7_resolved_plus_every_other_input_leaves_c_s4_3(monkeypatch) -> None:
    """C-7 resolved by reviewed external producers, metadata installed on the
    module, and a PASSED `unit_sandbox` classification in hand — together."""
    monkeypatch.setattr(concrete_plan_module, "_band_7", _resolved_band_7)
    for name in PRODUCER_ATTRIBUTE_NAMES:
        monkeypatch.setattr(
            concrete_plan_module, name, "reviewed and accepted", raising=False
        )
    record, attestation = classify()
    assert record.status is Status.PASSED and attestation is not None

    constructed = build_concrete_plan()
    assert "C-7" not in constructed.conflicts()
    assert constructed.conflicts() == (S4_3_CONFLICT,)
    assert _declares_s4_3(constructed)


def test_a_supplied_s4_3_observation_cannot_cover_it(plan) -> None:
    for custody in Custody:
        observation = SuppliedObservation(
            case_id="S4-3",
            variant="applied",
            target_identity=APPROVED_TARGET.host,
            run_id="run-1",
            review_manifest_digest="0" * 64,
            custody=custody,
            collected_by="reviewer",
            collected_at="2026-09-23",
            fields={"matches": "yes"},
        )
        with pytest.raises(ObservationRefused):
            classify_supplied_observations([observation], plan=plan)
    assert _declares_s4_3(build_concrete_plan())


def test_a_reviewed_external_case_for_s4_3_is_an_overlap(plan) -> None:
    produced = [case for step in plan.steps for case in step.evidence_case_ids]
    unresolved = [case for item in plan.unresolved for case in item.evidence_case_ids]
    with pytest.raises(PlanRefused):
        check_case_coverage(
            produced=produced,
            declared_unresolved=unresolved,
            supplied_externally=["S4-3"],
        )


def test_replacing_the_gap_predicate_does_not_clear_it(monkeypatch) -> None:
    """R2's gate was *"no gaps ⇒ resolved"*, so a monkeypatched predicate cleared
    C-S4-3. The gate is now unconditional: resolution is a change to the
    generator's code, reviewed as such, and not a value any function returns."""
    monkeypatch.setattr(
        concrete_plan_module, "s4_3_dependency_gaps", lambda *_, **__: ()
    )
    constructed = build_concrete_plan()
    assert _declares_s4_3(constructed)
    assert constructed.conflicts() == ("C-7", S4_3_CONFLICT)


def test_the_generator_has_no_resolution_branch() -> None:
    """A structural check on the one function that declares C-S4-3: it neither
    branches on the gap list nor attributes S4-3 to a step."""
    source = inspect.getsource(concrete_plan_module._stage_four)
    assert "if gaps" not in source and "if not gaps" not in source
    assert 'evidence_case_ids=("S4-3",)' in source  # the UnresolvedStep's
    assert source.count('"S4-3",)') == 1
    assert "S4_3_PRODUCER" not in inspect.getsource(concrete_plan_module)


# ---------------------------------------------------------------------------
# The coverage invariant — S4-3 cannot be deleted silently
# ---------------------------------------------------------------------------


def test_s4_3_is_a_required_case_and_the_only_new_one() -> None:
    rows = [case for case in REQUIRED_CASES if case.case_id == "S4-3"]
    assert len(rows) == 1
    assert rows[0].band == "filesystem"
    assert "§2.13.2a" in rows[0].source
    # Narrow, not a reclassification of Stage 1–4: the table is R13/R16's six
    # rows plus S4-3, and no other probe case.
    assert [case.case_id for case in REQUIRED_CASES] == [
        "JNL-49-E4-CLEAR-ARCHIVE-IMMUTABLE",
        "JNL-49-E6-CLEAR-ARCHIVE-IMMUTABLE",
        "JNL-50-E5-CLEAR-THEN-DENIED-OPEN",
        "JNL-51-PROVENANCE-OMITTED",
        "JNL-47-NO-GENERATION-ON-FAILURE",
        "JNL-47-RECOVERY-STATE",
        "S4-3",
    ]


def test_coverage_refuses_a_plan_missing_s4_3_from_every_column(plan) -> None:
    produced = [case for step in plan.steps for case in step.evidence_case_ids]
    unresolved = [
        case
        for item in plan.unresolved
        for case in item.evidence_case_ids
        if case != "S4-3"
    ]
    with pytest.raises(PlanRefused, match="S4-3"):
        check_case_coverage(produced=produced, declared_unresolved=unresolved)


def test_deleting_the_declaration_and_the_attribution_is_refused(monkeypatch) -> None:
    """The fail-open deletion R2 disclosed: drop the `UnresolvedStep` and leave
    the capture step without S4-3. `build_concrete_plan` now refuses."""
    original = concrete_plan_module._Steps.block

    def block_all_but_s4_3(self, item) -> None:
        if item.conflict_id == S4_3_CONFLICT:
            return
        original(self, item)

    monkeypatch.setattr(concrete_plan_module._Steps, "block", block_all_but_s4_3)
    with pytest.raises(PlanRefused, match="S4-3"):
        build_concrete_plan()


def test_s4_3_is_visible_as_required_in_the_mapping_and_the_manifest(plan) -> None:
    row = {row.case_id: row for row in producer_mapping(plan)}["S4-3"]
    assert row.produced_by_plan_steps == ()
    assert row.declared_unresolved_by == (S4_3_CONFLICT,)

    sources = {name: (REPOSITORY_ROOT / name).read_bytes() for name in COVERED_SOURCES}
    body = ReviewManifest.build(plan, sources).as_mapping()
    entry = next(item for item in body["required_cases"] if item["case_id"] == "S4-3")
    assert entry["produced_by"] == []
    assert entry["blocked_by"] == [S4_3_CONFLICT]
    assert entry["supplied_externally"] is False


def test_the_importer_reports_s4_3_outside_its_scope_not_as_band_7(plan) -> None:
    """S4-3 has no Band-7 schema, so the Band-7 importer lists it outside its
    scope. It is not an in-scope unresolved case: `band_7_coverage_complete`
    remains a statement about Band 7 alone."""
    result = classify_supplied_observations([], plan=plan)
    assert "S4-3" in result.outside_scope
    assert "S4-3" not in result.unresolved_cases
    assert set(result.unresolved_cases) <= set(BAND_7_SCHEMA)
