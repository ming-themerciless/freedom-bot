"""C-P5.0-R5-R2, finding P5.0-R5-R1-PLAN-1 — S4-3's producer dependency.

Codex's review of C-P5.0-R5-R1: the concrete plan's S4-3 vector requests two
properties and cannot produce a passing observation under §2.13.2a condition 4,
yet the plan declared no `UnresolvedStep` for it. `is_executable` is solely
`not self.unresolved`, so resolving C-7 would have made the plan report
executable while S4-3 stayed structurally incapable of passing.

The dependency is now declared under its own conflict, **C-S4-3**. These tests
prove it is independent of C-7, that the current vector cannot resolve it, that
nothing but a reviewed producer meeting all four requirements can, and that
supplied observations, an `ExternalCase` or the typed classifier cannot take
S4-3 out of the unresolved column.

No producer is implemented here.

**Amended under C-P5.0-R5-R3 (finding P5.0-R5-R2-PLAN-1).** R2's
`SandboxAttestationProducer` let two nonblank review-reference strings discharge
both producer requirements, and four tests here treated an explicitly
hypothetical instance of it as a complete producer — including one that replaced
the gap predicate to reach a resolved branch. The class, `S4_3_PRODUCER` and the
resolved branch are removed, and so are those tests. Their fail-closed
replacements are in `test_r5_r3_s4_3_binding.py`.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from tools.phase_5_0_evidence import concrete_plan as concrete_plan_module
from tools.phase_5_0_evidence.approved_target import APPROVED_TARGET
from tools.phase_5_0_evidence.capture import CapturePolicy
from tools.phase_5_0_evidence.concrete_plan import (
    S4_3_CONFLICT,
    S4_3_UNMET_PRODUCER_REQUIREMENTS,
    TRANSIENT_UNIT,
    ConcretePlan,
    ExternalCase,
    build_concrete_plan,
    s4_3_dependency_gaps,
)
from tools.phase_5_0_evidence.errors import ObservationRefused, PlanRefused
from tools.phase_5_0_evidence.execution.cli import render_plan
from tools.phase_5_0_evidence.observations import (
    BAND_7_SCHEMA,
    Custody,
    SuppliedObservation,
    classify_supplied_observations,
    producer_mapping,
)
from tools.phase_5_0_evidence.records import Status
from tools.phase_5_0_evidence.required_cases import check_case_coverage
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES, ReviewManifest
from tools.phase_5_0_evidence.unit_sandbox import (
    CANONICAL_PROBE_PATH,
    COMPARED_PROPERTIES,
)
from tests.phase_5_0_evidence.unit_sandbox_fixtures import classify

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

#: The Stage-4 capture vector as C-P5.0-R5-R1 left it. PLAN-1 is remediated by
#: declaring the gap, not by widening the vector — that is out of scope — so the
#: vector is pinned here byte for byte.
UNCHANGED_CAPTURE_VECTOR = (
    "/usr/bin/systemctl",
    "show",
    "--property=ProtectSystem",
    "--property=ReadWritePaths",
    TRANSIENT_UNIT,
)


@pytest.fixture(scope="module")
def plan() -> ConcretePlan:
    return build_concrete_plan()


def _dependency(plan: ConcretePlan):
    items = [item for item in plan.unresolved if item.conflict_id == S4_3_CONFLICT]
    assert len(items) == 1
    return items[0]


def _capture_step(plan: ConcretePlan):
    return next(
        step
        for step in plan.steps
        if step.capture is CapturePolicy.UNIT_DIRECTIVES
        and step.argv[-1] == TRANSIENT_UNIT
        and "--property=ReadWritePaths" in step.argv
    )


def _without_c7(plan: ConcretePlan) -> ConcretePlan:
    return replace(
        plan,
        unresolved=tuple(item for item in plan.unresolved if item.conflict_id != "C-7"),
    )


# ---------------------------------------------------------------------------
# The declaration
# ---------------------------------------------------------------------------


def test_s4_3_is_declared_unresolved_under_its_own_conflict(plan) -> None:
    item = _dependency(plan)
    assert S4_3_CONFLICT == "C-S4-3" != "C-7"
    assert item.step_ref == "STAGE4-S4-3"
    assert item.band == "filesystem"
    assert item.evidence_case_ids == ("S4-3",)
    # A missing producer, not a blocked ownership baseline.
    assert item.blocks_mutation_ids == ()
    assert not hasattr(concrete_plan_module, "S4_3_PRODUCER")


def test_the_dependency_names_all_four_requirements(plan) -> None:
    requires = _dependency(plan).design_requires
    assert "`freedom-sheet-writer.service`" in requires
    assert "drop-in policy" in requires
    assert "`unit_sandbox.COMPARED_PROPERTIES` exactly once" in requires
    assert "`ReadWritePaths=`" in requires
    assert "`unit_sandbox.CANONICAL_PROBE_PATH`" in requires
    assert "`unit_sandbox.SystemdIdentity`" in requires
    assert "**all** of" in requires


def test_it_appears_in_every_view_of_the_plan(plan) -> None:
    item = _dependency(plan)
    assert item in plan.unresolved
    assert item in plan.unresolved_by_band("filesystem")
    assert S4_3_CONFLICT in plan.conflicts()
    rendered = render_plan(plan, "0" * 64, "0" * 64)
    assert f"### `STAGE4-S4-3` — {S4_3_CONFLICT} (filesystem)" in rendered
    sources = {name: (REPOSITORY_ROOT / name).read_bytes() for name in COVERED_SOURCES}
    body = ReviewManifest.build(plan, sources).as_mapping()
    assert [
        (entry["step_ref"], entry["band"], entry["evidence_case_ids"])
        for entry in body["unresolved"]
        if entry["conflict_id"] == S4_3_CONFLICT
    ] == [("STAGE4-S4-3", "filesystem", ["S4-3"])]
    assert plan.is_executable is False


def test_no_step_claims_s4_3_and_the_vector_is_unchanged(plan) -> None:
    """A case is in exactly one coverage column. The capture step still runs the
    same two-property vector; it no longer says it produces S4-3."""
    assert not [step for step in plan.steps if "S4-3" in step.evidence_case_ids]
    step = _capture_step(plan)
    assert step.argv == UNCHANGED_CAPTURE_VECTOR
    assert step.evidence_case_ids == ()
    assert "It is not S4-3 evidence" in step.purpose
    produced = [case for step in plan.steps for case in step.evidence_case_ids]
    unresolved = [case for item in plan.unresolved for case in item.evidence_case_ids]
    assert "S4-3" not in produced and unresolved.count("S4-3") == 1
    # The overlap refusal applies to S4-3 like any declared case. **C-P5.0-R5-R3:**
    # S4-3 is now a `REQUIRED_CASES` row, so it is in `producer_mapping` too,
    # blocked by C-S4-3 and produced by nothing.
    check_case_coverage(produced=produced, declared_unresolved=unresolved)
    row = {row.case_id: row for row in producer_mapping(plan)}["S4-3"]
    assert row.produced_by_plan_steps == ()
    assert row.declared_unresolved_by == (S4_3_CONFLICT,)


# ---------------------------------------------------------------------------
# Independent of C-7
# ---------------------------------------------------------------------------


def test_removing_c7_leaves_the_plan_inexecutable(plan) -> None:
    from tools.phase_5_0_evidence.execution.executor import (
        ExecutingRunner,
        ExecutorRefused,
    )

    constructed = _without_c7(plan)
    assert constructed.conflicts() == (S4_3_CONFLICT,)
    assert constructed.is_executable is False

    class NeverRuns:
        def run(self, **_: object):  # pragma: no cover - never reached
            raise AssertionError("the gate was supposed to refuse before this")

    with pytest.raises(ExecutorRefused) as refusal:
        ExecutingRunner(
            plan=constructed,
            boundary=NeverRuns(),
            reviewed_digest="0" * 64,
            confirmation_token="wrong",
            source_bytes={},
        )
    assert S4_3_CONFLICT in str(refusal.value)


def test_resolving_band_7_by_reviewed_producers_leaves_s4_3_open(monkeypatch) -> None:
    """C-7 *resolved*, not merely deleted: Band 7's three cases are supplied by
    hypothetical reviewed producers, so they occupy the external column and the
    plan's coverage check passes. S4-3 is still unresolved."""

    def resolved_band_7(steps) -> None:
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

    monkeypatch.setattr(concrete_plan_module, "_band_7", resolved_band_7)
    constructed = build_concrete_plan()
    assert "C-7" not in constructed.conflicts()
    assert constructed.conflicts() == (S4_3_CONFLICT,)
    assert constructed.is_executable is False


# ---------------------------------------------------------------------------
# The current vector cannot resolve it
# ---------------------------------------------------------------------------


def test_the_current_vector_leaves_a_vector_gap() -> None:
    requested = tuple(
        argument.split("=", 1)[1]
        for argument in UNCHANGED_CAPTURE_VECTOR
        if argument.startswith("--property=")
    )
    gaps = s4_3_dependency_gaps(
        requested_properties=requested,
        substituted_path=CANONICAL_PROBE_PATH,
    )
    # The two producer gaps, which nothing discharges, and the vector gap.
    assert gaps[0] == S4_3_UNMET_PRODUCER_REQUIREMENTS[0]
    assert gaps[-1] == S4_3_UNMET_PRODUCER_REQUIREMENTS[1]
    assert len(gaps) == 3
    assert "requests 2 of 12 compared properties" in gaps[1]


# ---------------------------------------------------------------------------
# Nothing else can occupy its coverage column
# ---------------------------------------------------------------------------


def test_a_supplied_s4_3_observation_is_refused(plan) -> None:
    observation = SuppliedObservation(
        case_id="S4-3",
        variant="applied",
        target_identity=APPROVED_TARGET.host,
        run_id="run-1",
        review_manifest_digest="0" * 64,
        custody=Custody.REVIEWER_VERIFIED,
        collected_by="reviewer",
        collected_at="2026-09-23",
        fields={"matches": "yes"},
    )
    with pytest.raises(ObservationRefused):
        classify_supplied_observations([observation], plan=plan)
    # However the importer treats it, the plan is what it was.
    assert _dependency(build_concrete_plan()) == _dependency(plan)


def test_an_external_case_cannot_take_s4_3_from_the_unresolved_column(plan) -> None:
    produced = [case for step in plan.steps for case in step.evidence_case_ids]
    unresolved = [case for item in plan.unresolved for case in item.evidence_case_ids]
    external = ExternalCase(
        case_id="S4-3",
        band="filesystem",
        producer="hypothetical",
        collection_procedure="hypothetical",
        variants=("applied",),
        why_not_a_step="hypothetical",
        producer_artifact_reviewed=True,
        producer_review_reference="hypothetical review",
    )
    assert external.resolves_coverage
    with pytest.raises(PlanRefused):
        check_case_coverage(
            produced=produced,
            declared_unresolved=unresolved,
            supplied_externally=[external.case_id],
        )
    # And an unreviewed contract resolves nothing at all.
    assert replace(
        external, producer_artifact_reviewed=False, producer_review_reference=""
    ).resolves_coverage is False


def test_a_passing_typed_classification_does_not_resolve_it(plan) -> None:
    """`unit_sandbox` can classify a complete, matching applied set as PASSED.
    That is a classifier over inputs, not a producer of them: the plan has no
    route by which a record reaches `unresolved`, and none is added."""
    record, attestation = classify()
    assert record.status is Status.PASSED and attestation is not None
    rebuilt = build_concrete_plan()
    assert _dependency(rebuilt) == _dependency(plan)
    assert rebuilt.is_executable is False


# ---------------------------------------------------------------------------
# The plan-derived requirements are each checked
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "requested, path, plan_derived_gaps",
    [
        (COMPARED_PROPERTIES, CANONICAL_PROBE_PATH, 0),
        (COMPARED_PROPERTIES[:-1], CANONICAL_PROBE_PATH, 1),
        ((*COMPARED_PROPERTIES, "User"), CANONICAL_PROBE_PATH, 1),
        ((*COMPARED_PROPERTIES, "ExecStart"), CANONICAL_PROBE_PATH, 1),
        (COMPARED_PROPERTIES, f"{CANONICAL_PROBE_PATH}-ro", 1),
        ((), "/elsewhere", 2),
    ],
)
def test_every_plan_derived_requirement_is_necessary(
    requested, path, plan_derived_gaps
) -> None:
    """**Amended under C-P5.0-R5-R3.** The two producer gaps are always present,
    so even a complete vector on the canonical path leaves two."""
    gaps = s4_3_dependency_gaps(requested_properties=requested, substituted_path=path)
    assert len(gaps) == 2 + plan_derived_gaps
    assert gaps[0] == S4_3_UNMET_PRODUCER_REQUIREMENTS[0]
    assert gaps[-1] == S4_3_UNMET_PRODUCER_REQUIREMENTS[1]
