"""The bounded local producers for the three C-7 cases, and their limits.

Every test here is a **feasibility** test. None of them observes product code,
because none exists to observe, and the suite says so in the two places it would
otherwise be easy to forget: the tests that assert a case passes are paired with
tests that assert the same classifier fails a deliberately defective
arrangement, and the tests at the end assert that nothing here moves a case out
of the unresolved column.

A passing run of this file is not evidence that Package 5.0's coordinator
behaves correctly. It is evidence that the rules the coordinator will have to
satisfy are constructible, that their observations are falsifiable, and that the
harness's own §2.13.2b state machine does what §2.13.2b says under an injected
cleanup failure.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tools.phase_5_0_evidence import feasibility
from tools.phase_5_0_evidence.cleanup import ConfigurationRestoration, classify_cleanup
from tools.phase_5_0_evidence.errors import ObservationRefused
from tools.phase_5_0_evidence.feasibility import (
    SEQUENCE,
    Arrangement,
    Omission,
    PublicationSink,
    classify_provenance_experiment,
    classify_recovery_experiment,
    classify_stage_failure_experiment,
    dependent_work_to_stop,
    feasibility_dispositions,
    next_run_refuses,
    run_provenance_experiment,
    run_recovery_experiment,
    run_sequence,
    run_stage_failure_experiment,
    synthetic_payload,
)
from tools.phase_5_0_evidence.journal import CLEANUP_FAILURE_VARIANTS, FAILURE_STAGES
from tools.phase_5_0_evidence.observations import SYNTHETIC_TARGET_IDENTITY
from tools.phase_5_0_evidence.records import Status
from tools.phase_5_0_evidence.required_cases import REQUIRED_CASES

C7_CASES = (
    "JNL-51-PROVENANCE-OMITTED",
    "JNL-47-NO-GENERATION-ON-FAILURE",
    "JNL-47-RECOVERY-STATE",
)


# ---------------------------------------------------------------------------
# JNL-51 — the provenance gate
# ---------------------------------------------------------------------------


def test_the_positive_control_admits_and_creates_everything():
    """Without it, a refusal proves only that the model creates nothing."""
    run = run_provenance_experiment(omission=Omission.NONE)

    assert run.refusal_code is None
    assert run.artifacts == ("journal", "seal", "current", "close")
    assert run.registry_row_present is True
    assert run.probe_ran is True


@pytest.mark.parametrize(
    "omission",
    [Omission.PROVENANCE_RECORD, Omission.APPROVAL_RECORD, Omission.BOTH],
)
def test_an_omitted_provenance_fact_refuses_before_anything_durable_exists(omission):
    run = run_provenance_experiment(omission=omission)

    assert run.refusal_code == "J-26"
    assert run.artifacts == ()
    assert run.registry_row_present is False
    assert run.probe_ran is False, "C0 precedes the probe, so it cannot have run"


@pytest.mark.parametrize(
    "omission",
    [Omission.PROVENANCE_RECORD, Omission.APPROVAL_RECORD, Omission.BOTH],
)
def test_the_omission_case_is_classified_passed_on_the_real_classifier(omission):
    records = classify_provenance_experiment(omission=omission)

    assert records, "the classifier returns one record per assertion"
    assert all(record.status is Status.PASSED for record in records)


def test_the_unguarded_arrangement_is_classified_failed():
    """The negative control. A classifier that cannot fail decides nothing.

    Same omission, same classifier, same reader — with the C0 gate removed. The
    model then admits, creates all four artifacts and inserts a row, and the
    record must say so.
    """
    run = run_provenance_experiment(
        omission=Omission.PROVENANCE_RECORD, arrangement=Arrangement.UNGUARDED
    )
    assert run.refusal_code is None
    assert run.artifacts == ("journal", "seal", "current", "close")

    records = classify_provenance_experiment(
        omission=Omission.PROVENANCE_RECORD, arrangement=Arrangement.UNGUARDED
    )
    assert any(record.status is Status.FAILED for record in records)


def test_the_precondition_unmet_case_cannot_pass():
    """A run in which nothing was omitted is evidence of a different situation.

    `Arrangement.UNGUARDED` with `Omission.NONE` admits, which is correct
    behaviour for an unomitted deployment — and it is not this case passing.
    """
    records = classify_provenance_experiment(
        omission=Omission.NONE, arrangement=Arrangement.UNGUARDED
    )

    assert any(record.status is Status.FAILED for record in records)


def test_the_expected_refusal_comes_from_the_classifier_and_not_from_here():
    """EH-R16-2's separation, asserted rather than described.

    The model reports the code its own rule produced. The expectation lives in
    `provenance.EXPECTED_OMISSION_REFUSAL`. This asserts the two are compared
    rather than shared: a model reporting a different real refusal fails.
    """
    from tools.phase_5_0_evidence.provenance import classify_missing_provenance

    host_records = classify_missing_provenance(
        apr=None,
        pvr=None,
        probe_ran=False,
        generation_artifacts=(),
        generation_row_inserted=False,
        observed_refusal_code="DEP-04",
    )

    assert any(record.status is Status.FAILED for record in host_records)


# ---------------------------------------------------------------------------
# JNL-47-NO-GENERATION-ON-FAILURE — the creation order
# ---------------------------------------------------------------------------


def test_the_uninjected_run_creates_the_whole_generation():
    """The positive control for the stage experiment.

    It is also the control that makes every absence below attributable: the same
    model, with nothing injected, reaches C5 and the sink records the four
    artifacts and the row in creation order.
    """
    run = run_stage_failure_experiment(stage=None)

    assert run.stopped_at is None
    assert run.publication_reached is True
    assert run.publication_attempted == (
        "journal",
        "seal",
        "current",
        "close",
        "row:generation-1",
    )
    assert run.artifacts == ("journal", "seal", "current", "close")
    assert run.registry_row_present is True


@pytest.mark.parametrize("stage", list(FAILURE_STAGES))
def test_a_failure_at_any_injection_point_leaves_no_generation(stage):
    """PR-20260911-5: all five points, cleanup included, and the same absence.

    C1 runs the probe **and its cleanup**, C2 validates, C5 creates the first
    persistent artifact. Every one of the five injection points is before C5, so
    `JNL-47`'s *"no journal file, no seal, no symlink, no `.close` manifest and
    no database row"* holds for the same reason at all five: creation was never
    reached.
    """
    run = run_stage_failure_experiment(stage=stage)

    assert run.artifacts == ()
    assert run.registry_row_present is False
    assert classify_stage_failure_experiment(stage=stage).status is Status.PASSED


@pytest.mark.parametrize("stage", list(FAILURE_STAGES))
def test_no_failure_point_ever_reaches_the_publication_sink(stage):
    """The absence is *creation never reached*, asserted separately.

    Two independent observations are required by PR-20260911-5 and made here:
    publication was never attempted, and no artifact or row exists. A model that
    created a generation and unwound it would satisfy the second and fail the
    first.
    """
    run = run_stage_failure_experiment(stage=stage)

    assert run.publication_attempted == ()
    assert run.publication_reached is False
    assert run.artifacts == () and run.registry_row_present is False


@pytest.mark.parametrize("stage", list(FAILURE_STAGES))
def test_the_misordered_control_publishes_early_and_is_classified_failed(stage):
    """The intentionally misordered negative control.

    `Arrangement.UNORDERED` moves C5 in front of C1, which is the ordering the
    submitted model used. Publication is reached before anything can fail, the
    generation and the row survive every injection, and the same classifier must
    call the record failed.
    """
    run = run_stage_failure_experiment(stage=stage, arrangement=Arrangement.UNORDERED)

    assert run.publication_reached is True
    assert run.artifacts == ("journal", "seal", "current", "close")
    assert run.registry_row_present is True
    record = classify_stage_failure_experiment(
        stage=stage, arrangement=Arrangement.UNORDERED
    )
    assert record.status is Status.FAILED


def test_the_cleanup_point_stops_the_run_inside_c1():
    """*"If the finally cleanup does not complete … no later step executes."*"""
    run = run_stage_failure_experiment(stage="cleanup")

    assert run.stopped_at == "C1-cleanup"
    assert run.publication_attempted == ()


def test_a_probe_stage_failure_stops_the_run_before_the_first_artifact():
    """A probe-stage failure is refused at C2, which is still before C5."""
    for stage in ("stage-1", "stage-2", "stage-3", "stage-4"):
        run = run_stage_failure_experiment(stage=stage)
        assert run.stopped_at == "C2"
        assert run.publication_attempted == ()


def test_the_sequence_is_the_approved_one_and_cleanup_belongs_to_c1():
    """The modelled order is the package's, named rather than implied."""
    steps = [step for step, _ in SEQUENCE]

    assert steps == ["C0", "C1-probe", "C1-cleanup", "C2", "C5"]
    assert steps.index("C1-cleanup") < steps.index("C2") < steps.index("C5")


def test_the_cleanup_point_is_not_a_probe_stage():
    """C1's cleanup and C1's probe stages are different steps and stay apart."""
    with pytest.raises(ObservationRefused):
        run_sequence(probe_failure_stage="cleanup")


def test_the_publication_sink_refuses_a_name_that_is_not_a_generation_artifact():
    sink = PublicationSink()
    with pytest.raises(ObservationRefused):
        sink.publish_artifact("almost-a-journal")


def test_an_unknown_stage_is_refused():
    with pytest.raises(ObservationRefused):
        run_stage_failure_experiment(stage="stage-9")


def test_every_declared_failure_stage_has_an_experiment():
    """The stage table and the experiment cannot drift apart silently."""
    for stage in FAILURE_STAGES:
        run_stage_failure_experiment(stage=stage)


# ---------------------------------------------------------------------------
# JNL-47-RECOVERY-STATE — the harness's own state machine, with a fault injected
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("variant", sorted(CLEANUP_FAILURE_VARIANTS))
def test_an_injected_cleanup_failure_produces_s_b_for_both_variants(variant):
    run = run_recovery_experiment(variant=variant)

    assert run.state == "S-B"
    assert run.exit_code == 3
    assert run.residue == ("/…/probe",)
    assert run.next_run_refuses is True
    assert run.recovery_procedure == (), (
        "no configuration capture was retained, so no configuration recovery "
        "procedure is named; the state is still S-B on residue alone"
    )


@pytest.mark.parametrize("variant", sorted(CLEANUP_FAILURE_VARIANTS))
def test_a_cleanup_failure_never_reaches_publication(variant):
    """PR-20260911-5: both absence clauses, observed rather than supplied.

    The run ends at C1's cleanup. C2 is not reached, C5 is not reached, and the
    publication sink records nothing — so the generation and the registry row are
    absent because they were never created, which is what `JNL-47` requires.
    """
    run = run_recovery_experiment(variant=variant)

    assert run.stopped_at == "C1-cleanup"
    assert run.publication_reached is False
    assert run.artifacts == ()
    assert run.registry_row_present is False


@pytest.mark.parametrize("variant", sorted(CLEANUP_FAILURE_VARIANTS))
def test_the_completing_control_does_not_produce_s_b(variant):
    """The positive control. Same injection point, nothing injected."""
    run = run_recovery_experiment(variant=variant, cleanup_completes=True)

    assert run.state in ("S-A", "S-C")
    assert run.residue == ()
    assert run.next_run_refuses is False


def test_the_passing_control_does_reach_publication():
    """Without this, an empty sink would prove nothing.

    The passing-probe variant with the cleanup completing runs the whole approved
    sequence and publishes. So the empty sink in the failing case is attributable
    to the run stopping at C1, not to a model that never publishes.
    """
    control = run_recovery_experiment(
        variant="cleanup-failure-after-passing-probe", cleanup_completes=True
    )

    assert control.state == "S-C"
    assert control.publication_reached is True
    assert control.artifacts == ("journal", "seal", "current", "close")
    assert control.registry_row_present is True


def test_the_misordered_control_leaves_a_generation_behind_a_failed_cleanup():
    """The negative control for the recovery case's absence clauses.

    Publishing at C5 before C1 runs is the prohibited ordering. It leaves the
    generation and the row behind a failed cleanup, and the classifier fails the
    record on the two absence clauses rather than only on LAB-1.
    """
    from tools.phase_5_0_evidence.journal import classify_cleanup_failure_state

    observed = run_sequence(cleanup_fails=True, arrangement=Arrangement.UNORDERED)

    assert observed.publication_reached is True
    assert observed.artifacts == ("journal", "seal", "current", "close")
    assert observed.registry_row_present is True
    record = classify_cleanup_failure_state(
        variant="cleanup-failure-after-passing-probe",
        exit_code=observed.exit_code,
        state=observed.state,
        residue_path_count=len(observed.residue),
        generation_present=bool(observed.artifacts),
        database_row_present=observed.registry_row_present,
        next_run_refuses=True,
        recovery_procedure_named=True,
    )
    assert record.status is Status.FAILED


def test_the_two_cleanup_failures_are_distinguished():
    """§2.13.2b requires the two situations to be told apart, not merged."""
    after_failure = run_recovery_experiment(
        variant="cleanup-failure-after-probe-failure"
    )
    after_pass = run_recovery_experiment(
        variant="cleanup-failure-after-passing-probe"
    )
    control_failure = run_recovery_experiment(
        variant="cleanup-failure-after-probe-failure", cleanup_completes=True
    )
    control_pass = run_recovery_experiment(
        variant="cleanup-failure-after-passing-probe", cleanup_completes=True
    )

    # The failing runs agree on state, which is the point: S-B supersedes.
    assert after_failure.state == after_pass.state == "S-B"
    # Their controls do not, which is what distinguishes the two situations.
    assert control_failure.state == "S-A"
    assert control_pass.state == "S-C"


@pytest.mark.parametrize("variant", sorted(CLEANUP_FAILURE_VARIANTS))
def test_the_recovery_case_reproduces_lab_1(variant):
    """**A labelled defect reproduction, not a passing case.**

    §2.13.2b requires an S-B run to report the named operator recovery, and the
    harness does not for a residue-only S-B: `CleanupOutcome.recovery_procedure`
    carries the configuration recovery alone, and `journal.RECOVERY_PROCEDURE` —
    the five-step residue recovery — is never attached. The experiment observes
    that and the record fails, which is finding LAB-1.

    This assertion is deliberately the failure. Adjusting the input until the
    record passed would be exactly what the R2 prompt forbids: making an
    unimplemented safety property appear to pass.
    """
    record = classify_recovery_experiment(variant=variant)

    assert record.status is Status.FAILED
    assert record.detail["variant"] == variant
    assert "recovery not named" in str(record.observed.value)


@pytest.mark.parametrize("variant", sorted(CLEANUP_FAILURE_VARIANTS))
def test_a_run_that_reports_s_c_after_a_failed_cleanup_is_failed(variant):
    """The negative control: six of seven clauses is a failed record."""
    from tools.phase_5_0_evidence.journal import classify_cleanup_failure_state

    record = classify_cleanup_failure_state(
        variant=variant,
        exit_code=0,
        state="S-C",
        residue_path_count=1,
        generation_present=False,
        database_row_present=False,
        next_run_refuses=True,
        recovery_procedure_named=True,
    )

    assert record.status is Status.FAILED


def test_an_unknown_recovery_variant_is_refused():
    with pytest.raises(ObservationRefused):
        run_recovery_experiment(variant="cleanup-failure-after-lunch")


def test_the_next_run_predicate_matches_the_executors_own_rule():
    """`next_run_refuses` and `executor._refuse_when_blocked` state one rule.

    The predicate lives in the planning tier so the experiments can reach it, and
    the executor implements it in the execution tier. This binds them: for every
    outcome shape below, the predicate and the executor's own gate condition —
    residue or configuration risk present — agree.
    """
    cases = [
        ((), (), False),
        (("/…/probe",), (), True),
        ((), ("pg_hba.conf may still be effective",), True),
        (("/…/probe",), ("pg_hba.conf may still be effective",), True),
    ]
    for residue, risk, expected in cases:
        outcome = classify_cleanup(
            probe_passed=True,
            unremoved=residue,
            configuration=ConfigurationRestoration(
                declared_files=("pg_hba.conf",) if risk else (),
            ),
        )
        assert next_run_refuses(
            residue=outcome.residue, configuration_risk=outcome.configuration_risk
        ) is expected
        assert (outcome.state == "S-B") is expected


# ---------------------------------------------------------------------------
# Missing, corrupt and duplicate producer output
# ---------------------------------------------------------------------------


def test_a_synthetic_report_carries_the_scope_beside_the_payload():
    """The envelope stays the importer's closed three keys; the two bounding
    sentences travel beside it rather than widening the schema."""
    import json

    report = feasibility.synthetic_report([])

    assert report.target_identity == SYNTHETIC_TARGET_IDENTITY
    assert report.scope == feasibility.FEASIBILITY_SCOPE
    assert report.not_coverage == feasibility.NOT_COVERAGE
    assert set(json.loads(report.payload)) == {"schema", "schema_version", "records"}


def test_a_synthetic_payload_is_refused_against_a_real_target():
    """A feasibility record pointed at the approved target is refused for naming
    the wrong target. That refusal is the safeguard, not an inconvenience."""
    from tools.phase_5_0_evidence.observations import read_records

    payload = synthetic_payload(
        [
            {
                "case_id": "JNL-47-NO-GENERATION-ON-FAILURE",
                "variant": "stage-1",
                "target_identity": SYNTHETIC_TARGET_IDENTITY,
                "run_id": "feasibility-1",
                "review_manifest_digest": "a" * 64,
                "custody": "synthetic_fixture",
                "collected_by": "implementer",
                "collected_at": "2026-09-10",
                "fields": {
                    "journal_present": "no",
                    "seal_present": "no",
                    "current_present": "no",
                    "close_present": "no",
                    "generation_row_present": "no",
                },
            }
        ]
    )

    with pytest.raises(ObservationRefused):
        read_records(
            payload,
            target_identity="oracle-test",
            run_id="feasibility-1",
            review_manifest_digest="a" * 64,
        )


def test_a_missing_variant_is_reported_missing_and_never_assumed():
    """Missing producer output. Four of five stages supplied is not the case."""
    from tools.phase_5_0_evidence.observations import read_records

    records = [
        {
            "case_id": "JNL-47-NO-GENERATION-ON-FAILURE",
            "variant": stage,
            "target_identity": SYNTHETIC_TARGET_IDENTITY,
            "run_id": "feasibility-1",
            "review_manifest_digest": "a" * 64,
            "custody": "synthetic_fixture",
            "collected_by": "implementer",
            "collected_at": "2026-09-10",
            "fields": {
                "journal_present": "no",
                "seal_present": "no",
                "current_present": "no",
                "close_present": "no",
                "generation_row_present": "no",
            },
        }
        for stage in ("stage-1", "stage-2", "stage-3", "stage-4")
    ]
    supplied = read_records(
        synthetic_payload(records),
        target_identity=SYNTHETIC_TARGET_IDENTITY,
        run_id="feasibility-1",
        review_manifest_digest="a" * 64,
    )

    keys = {observation.key for observation in supplied}
    assert "JNL-47-NO-GENERATION-ON-FAILURE#cleanup" not in keys


def test_corrupt_producer_output_is_refused_rather_than_repaired():
    from tools.phase_5_0_evidence.observations import read_records

    payload = synthetic_payload(
        [
            {
                "case_id": "JNL-47-NO-GENERATION-ON-FAILURE",
                "variant": "stage-1",
                "target_identity": SYNTHETIC_TARGET_IDENTITY,
                "run_id": "feasibility-1",
                "review_manifest_digest": "a" * 64,
                "custody": "synthetic_fixture",
                "collected_by": "implementer",
                "collected_at": "2026-09-10",
                "fields": {"journal_present": "maybe"},
            }
        ]
    )

    with pytest.raises(ObservationRefused):
        read_records(
            payload,
            target_identity=SYNTHETIC_TARGET_IDENTITY,
            run_id="feasibility-1",
            review_manifest_digest="a" * 64,
        )


def test_duplicate_producer_output_is_refused():
    from tools.phase_5_0_evidence.observations import read_records

    one = {
        "case_id": "JNL-47-NO-GENERATION-ON-FAILURE",
        "variant": "stage-1",
        "target_identity": SYNTHETIC_TARGET_IDENTITY,
        "run_id": "feasibility-1",
        "review_manifest_digest": "a" * 64,
        "custody": "synthetic_fixture",
        "collected_by": "implementer",
        "collected_at": "2026-09-10",
        "fields": {
            "journal_present": "no",
            "seal_present": "no",
            "current_present": "no",
            "close_present": "no",
            "generation_row_present": "no",
        },
    }

    with pytest.raises(ObservationRefused):
        read_records(
            synthetic_payload([one, dict(one)]),
            target_identity=SYNTHETIC_TARGET_IDENTITY,
            run_id="feasibility-1",
            review_manifest_digest="a" * 64,
        )


# ---------------------------------------------------------------------------
# The dispositions, and what they may not do
# ---------------------------------------------------------------------------


def test_there_is_a_disposition_for_every_c7_case_and_no_other():
    dispositions = feasibility_dispositions()

    assert tuple(finding.case_id for finding in dispositions) == C7_CASES


def test_every_disposition_names_a_requirement_producer_and_acceptance_test():
    for finding in feasibility_dispositions():
        assert finding.requirement.strip()
        assert finding.missing_producer.strip()
        assert finding.carried_by.strip()
        assert finding.establishes.strip()
        assert finding.does_not_establish.strip()


def test_no_disposition_resolves_c7():
    for finding in feasibility_dispositions():
        assert finding.resolves_c7 is False


def test_every_disposition_actually_ran_its_experiment():
    """A disposition that claimed an observation it did not make would be the
    substitution EH-R16-4 refused, in a new place.

    Each disposition declares the status its records carry, and the records are
    produced by running the experiment. A disposition that reproduces a defect
    declares `FAILED` and is labelled as a reproduction, so a failing record here
    is a reported finding rather than a broken test.
    """
    for finding in feasibility_dispositions():
        assert finding.records, f"{finding.case_id} claims a producer and shows none"
        assert all(
            record.status is finding.expected_status for record in finding.records
        )
        if finding.reproduces_a_defect:
            assert finding.observed_defect.strip()


def test_no_case_stops_dependent_work_under_the_corrected_ordering():
    """PR-20260911-5: the criterion-split request is withdrawn.

    The submitted pass returned `JNL-47-RECOVERY-STATE` here because its two
    absence clauses were believed to need a generation a real coordinator had
    created and a failed cleanup had left behind. The package forbids that run,
    so the absences are modellable and no case needs a readiness-versus-
    implementation split. All three keep the ordinary feasibility/product
    boundary, and all three stay unresolved under conflict C-7.
    """
    assert dependent_work_to_stop() == ()
    assert all(
        finding.meaningful_without_product_code
        for finding in feasibility_dispositions()
    )


def test_the_three_cases_are_still_declared_unresolved_in_the_plan():
    """The load-bearing assertion of this file.

    Whatever passed above, the plan still declares all three cases unresolved and
    reports itself inexecutable. If this ever fails, a facsimile has been counted
    as a producer.
    """
    from tools.phase_5_0_evidence.concrete_plan import build_concrete_plan

    plan = build_concrete_plan()
    unresolved = {
        case_id for step in plan.unresolved for case_id in step.evidence_case_ids
    }

    for case_id in C7_CASES:
        assert case_id in unresolved
    assert plan.is_executable is False
    assert all(not case.resolves_coverage for case in plan.external_cases)


def test_the_required_case_table_is_unchanged_by_this_work():
    assert {case.case_id for case in REQUIRED_CASES} >= set(C7_CASES)


# ---------------------------------------------------------------------------
# Isolation from the product tree
# ---------------------------------------------------------------------------


def test_the_producer_imports_nothing_from_the_product_tree():
    """No bot startup, no web application, no migration, no repository.

    The no-execution suite proves the module cannot reach a process. This proves
    the other isolation the laboratory prompt requires: that the producer is
    unreachable from production startup, database migrations and runtime
    imports, because it depends on none of them.
    """
    source = (
        Path(__file__).resolve().parents[2]
        / "tools"
        / "phase_5_0_evidence"
        / "feasibility.py"
    )
    tree = ast.parse(source.read_text(encoding="utf-8"))

    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                continue  # a sibling in this package
            if node.module:
                roots.add(node.module.split(".")[0])

    forbidden = {
        "adapters",
        "alembic",
        "application",
        "config",
        "connectors",
        "domain",
        "ext",
        "helpers",
        "main",
        "migrations",
        "models",
        "web",
    }
    assert not roots & forbidden, f"{sorted(roots & forbidden)} is product code"


def test_the_producer_is_in_the_planning_tier():
    """It plans and classifies. It does not execute, and the tier says so."""
    from tests.phase_5_0_evidence import test_no_execution

    assert "feasibility" in test_no_execution.PLANNING_TIER_NAMES
