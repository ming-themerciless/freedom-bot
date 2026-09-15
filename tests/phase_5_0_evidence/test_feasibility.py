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
from dataclasses import replace

from tools.phase_5_0_evidence import feasibility
from tools.phase_5_0_evidence.cleanup import (
    RECOVERY_PROCEDURE as CONFIGURATION_RECOVERY_PROCEDURE,
)
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
from tools.phase_5_0_evidence.journal import (
    CLEANUP_FAILURE_VARIANTS,
    FAILURE_STAGES,
    RECOVERY_PROCEDURE as RESIDUE_RECOVERY_PROCEDURE,
)
from tools.phase_5_0_evidence.approved_target import APPROVED_TARGET
from tools.phase_5_0_evidence.observations import (
    BAND_7_SCHEMA,
    SYNTHETIC_TARGET_IDENTITY,
)
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
        "no configuration capture was retained, so configuration recovery is "
        "not named for this residue-only S-B state"
    )
    assert run.residue_recovery_procedure == RESIDUE_RECOVERY_PROCEDURE


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
        residue_recovery_named=True,
        configuration_capture_retained=False,
        configuration_recovery_named=False,
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
def test_cleanup_recovery_case_names_the_residue_procedure(variant):
    """The residue-only S-B outcome carries the named, applicable recovery."""
    record = classify_recovery_experiment(variant=variant)

    assert record.status is Status.PASSED
    assert record.detail["variant"] == variant
    assert "the named operator recovery is reported" in str(record.observed.value)


@pytest.mark.parametrize("variant", sorted(CLEANUP_FAILURE_VARIANTS))
def test_the_recovery_record_is_derived_from_the_outcome_not_asserted(variant, monkeypatch):
    """The negative control that constrains the repair itself.

    `classify_recovery_experiment` must read whether a procedure was named off
    the outcome the harness really produced. This replaces that outcome with one
    that names neither procedure and requires the record to fail. A derivation
    hardcoded to `True` — the way an unimplemented property is made to look
    implemented — passes every other test in this file and fails this one.
    """
    real = feasibility.run_recovery_experiment(variant=variant)
    silent = replace(real, recovery_procedure=(), residue_recovery_procedure=())
    monkeypatch.setattr(
        feasibility, "run_recovery_experiment", lambda **kwargs: silent
    )

    record = classify_recovery_experiment(variant=variant)

    assert record.status is Status.FAILED
    assert "residue recovery not named" in str(record.observed.value)


@pytest.mark.parametrize("variant", sorted(CLEANUP_FAILURE_VARIANTS))
def test_naming_the_configuration_procedure_does_not_answer_residue(variant, monkeypatch):
    """LAB-1's shape, one level up — runner contract r6 §8.1.

    An S-B run that left residue and named only the *configuration* recovery has
    not reported the procedure that applies to the state it reached. A single
    boolean over both procedures accepted this, which is the same reporting gap
    LAB-1 named in the outcome.
    """
    real = feasibility.run_recovery_experiment(variant=variant)
    misreported = replace(
        real,
        residue_recovery_procedure=(),
        recovery_procedure=CONFIGURATION_RECOVERY_PROCEDURE,
        retained_recovery_inputs=("/var/lib/fb-evidence-r1/before/pg_hba.conf",),
    )
    monkeypatch.setattr(
        feasibility, "run_recovery_experiment", lambda **kwargs: misreported
    )

    record = classify_recovery_experiment(variant=variant)

    assert record.status is Status.FAILED
    assert "residue recovery not named" in str(record.observed.value)


@pytest.mark.parametrize("variant", sorted(CLEANUP_FAILURE_VARIANTS))
def test_a_retained_capture_requires_its_own_procedure(variant, monkeypatch):
    """The mirror clause: a present configuration cause must be answered too."""
    real = feasibility.run_recovery_experiment(variant=variant)
    misreported = replace(
        real,
        recovery_procedure=(),
        retained_recovery_inputs=("/var/lib/fb-evidence-r1/before/pg_hba.conf",),
    )
    monkeypatch.setattr(
        feasibility, "run_recovery_experiment", lambda **kwargs: misreported
    )

    record = classify_recovery_experiment(variant=variant)

    assert record.status is Status.FAILED
    assert "configuration recovery not named" in str(record.observed.value)


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
        residue_recovery_named=True,
        configuration_capture_retained=False,
        configuration_recovery_named=False,
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


# ---------------------------------------------------------------------------
# C-P5.0-LAB-I — the producer-to-importer adapter, end to end
# ---------------------------------------------------------------------------


def _imported(arrangement=feasibility.Arrangement.CORRECT):
    """Producer runs → records → payload → importer → classified result.

    The whole path in one helper, so every assertion below is about the same
    path rather than about a re-assembled approximation of it.
    """
    from tools.phase_5_0_evidence.concrete_plan import build_concrete_plan
    from tools.phase_5_0_evidence.observations import (
        classify_supplied_observations,
        read_records,
    )

    digest = "a" * 64
    plan = build_concrete_plan(APPROVED_TARGET)
    payload = feasibility.producer_report(
        run_id="feasibility-1",
        review_manifest_digest=digest,
        arrangement=arrangement,
    ).payload
    supplied = read_records(
        payload,
        target_identity=SYNTHETIC_TARGET_IDENTITY,
        run_id="feasibility-1",
        review_manifest_digest=digest,
    )
    return plan, supplied, classify_supplied_observations(supplied, plan=plan)


def test_the_adapter_supplies_every_variant_of_every_c7_case():
    """The positive case, for all three producers and all eight variants.

    A case is not covered until every variant its schema declares is supplied,
    so the adapter's job is to supply all of them from real producer runs — not
    to supply one and let the rest be inferred.
    """
    _plan, supplied, _result = _imported()

    keys = {observation.key for observation in supplied}
    expected = {
        f"{case_id}#{variant}"
        for case_id, schema in BAND_7_SCHEMA.items()
        for variant in schema.variants
    }
    assert keys == expected
    assert all(
        observation.target_identity == SYNTHETIC_TARGET_IDENTITY
        for observation in supplied
    )
    assert all(
        observation.custody is feasibility.Custody.SYNTHETIC_FIXTURE
        for observation in supplied
    )


def test_a_complete_producer_payload_still_resolves_no_c7_case():
    """**The sentence this whole module turns on.**

    Every variant of every C-7 case is supplied and every record is well formed,
    and all three cases are still reported `unresolved`, none is `covered`, and
    the importer classifies **nothing at all** for them. A validated record does
    not discharge a missing producer, and synthetic feasibility is not
    operational evidence.

    `records == ()` is the strongest form of that: the importer does not
    classify a case the plan declares unresolved, so there is not even a passing
    record for somebody to cite.
    """
    _plan, supplied, result = _imported()

    assert len(supplied) == 8
    assert set(result.unresolved_cases) == set(BAND_7_SCHEMA)
    assert result.covered == ()
    assert result.records == ()
    assert not result.eligible_for_operational_acceptance
    assert result.outside_scope, "the executed bands are outside this result"
    # The three Band-7 rows are the ones this importer is about, and each is
    # declared unresolved by a plan step. The capability rows beside them are
    # produced by the plan itself and are `outside_scope` — listed, never
    # counted, and on their own enough to withhold overall completeness.
    band_7 = {row.case_id: row for row in result.producers if row.case_id in BAND_7_SCHEMA}
    assert set(band_7) == set(BAND_7_SCHEMA)
    for row in band_7.values():
        assert row.declared_unresolved_by
        assert not row.in_harness_producer


def test_the_false_success_control_changes_the_observations_it_reports():
    """The negative control, through the same adapter.

    A deliberately defective arrangement must produce **different observations**
    — ones the band's own classifier fails — rather than an absence. A producer
    whose failure showed up as a missing record would be indistinguishable from
    a producer that was never run, and a classifier that cannot fail proves
    nothing.

    The failure is asserted at the classifier, because the importer deliberately
    classifies nothing while the plan declares the case unresolved: that is the
    safeguard the test above pins, and it is not weakened here to make a control
    convenient.
    """
    correct = {
        (record["case_id"], record["variant"]): record["fields"]
        for record in feasibility.producer_records(
            run_id="feasibility-1", review_manifest_digest="a" * 64
        )
    }
    unguarded = {
        (record["case_id"], record["variant"]): record["fields"]
        for record in feasibility.producer_records(
            run_id="feasibility-1",
            review_manifest_digest="a" * 64,
            arrangement=feasibility.Arrangement.UNGUARDED,
        )
    }

    assert set(correct) == set(unguarded), "every variant is still reported"
    assert correct != unguarded, "and the observations are not the same"

    failed = feasibility.classify_provenance_experiment(
        omission=feasibility.Omission.PROVENANCE_RECORD,
        arrangement=feasibility.Arrangement.UNGUARDED,
    )
    assert any(record.status is not Status.PASSED for record in failed)


def test_the_adapters_records_are_refused_against_the_approved_target():
    """The importer binding, stated as a refusal rather than as a convention.

    A feasibility payload pointed at the approved target is refused for naming
    the wrong target. That refusal — not a docstring — is what keeps a
    facsimile's output out of a real result.
    """
    from tools.phase_5_0_evidence.observations import read_records

    payload = feasibility.producer_report(
        run_id="feasibility-1", review_manifest_digest="a" * 64
    ).payload
    with pytest.raises(ObservationRefused):
        read_records(
            payload,
            target_identity=APPROVED_TARGET.identity,
            run_id="feasibility-1",
            review_manifest_digest="a" * 64,
        )


def test_the_recovery_adapter_keeps_the_two_causes_apart():
    """r6 §8.1, one layer further out than LAB-1 was repaired.

    The residue cause and the configuration cause are two fields in the record,
    and neither answers for the other. A single boolean here would put LAB-1's
    own shape back into the producer's output.
    """
    records = {
        record["variant"]: record["fields"]
        for record in feasibility.producer_records(
            run_id="feasibility-1", review_manifest_digest="a" * 64
        )
        if record["case_id"] == "JNL-47-RECOVERY-STATE"
    }
    assert set(records) == set(feasibility.CLEANUP_FAILURE_VARIANTS)
    for fields in records.values():
        assert "residue_recovery_named" in fields
        assert "configuration_recovery_named" in fields
        assert "configuration_capture_retained" in fields
        # A residue-bearing S-B run names the residue procedure, and that is a
        # different statement from whether a configuration capture was retained.
        if int(fields["residue_path_count"]) > 0:
            assert fields["residue_recovery_named"] == "yes"


def test_an_undeclared_field_is_never_defaulted_by_the_adapter():
    """Every field the schema declares comes from something the run observed.

    The rendering is mechanical and **total**: a field the producer does not
    observe raises rather than being filled with something plausible, which is
    the difference between an observation and a value somebody chose.
    """
    run = feasibility.run_recovery_experiment(
        variant=sorted(feasibility.CLEANUP_FAILURE_VARIANTS)[0]
    )
    fields = run.as_fields()
    assert set(fields) == BAND_7_SCHEMA["JNL-47-RECOVERY-STATE"].field_names()
