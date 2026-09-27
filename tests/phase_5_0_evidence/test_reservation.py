"""Whole-host reservation, admission and release — direction C-P5.0-LAB-1.

Nine situations the direction names are covered here, each with an injected
effect rather than a described one: a second executor, a missing reservation, an
expired reservation, a mismatched target, a mismatched release, an unknown
writer, an orphaned child, a delayed database transaction, an interrupted
recovery and a successful release.

Two properties are asserted repeatedly and deliberately, because they are the
ones a later convenience would erode:

* **no takeover.** Nothing in this module moves a host to an available state
  because time passed, a lock was released or a process died; and
* **quarantine is terminal.** There is no argument, no elapsed interval and no
  operator field that turns a quarantined host into an admissible one within the
  same reservation.
"""
from __future__ import annotations

import pytest

from tools.phase_5_0_evidence.errors import PlanRefused
from tools.phase_5_0_evidence.reservation import (
    ADAPTER_RESPONSIBILITIES,
    ADMITTING_DISPOSITIONS,
    DECISIONS_DO_NOT_PERSIST,
    DURABLE_RECORD_ORDERING,
    GUARDED_TRANSITIONS,
    HOST_LOCK_PATH,
    LIFECYCLE_SHAPES,
    LOCK_LIMITS,
    PARTICIPATING_ENTRY_POINTS,
    REAL_EXECUTION_REFUSAL,
    TRANSITIONS,
    VALIDATED_LIFECYCLE_OUTCOMES,
    AdmissionDecision,
    EvidenceRule,
    HostInventory,
    LifecycleHistory,
    LockView,
    OperatorAttestation,
    PredecessorDisposition,
    QuarantineRecord,
    ReleaseEvidence,
    ReleaseOutcome,
    ReleaseRecord,
    ReservationRequest,
    ReservationState,
    ResidueObservation,
    Writer,
    WriterDisposition,
    admit,
    advance,
    deadline_reached,
    recover,
    release,
    validate_lifecycle,
)

TARGET = "oracle-test"


def _request(**overrides) -> ReservationRequest:
    fields = {
        "reservation_id": "RES-1",
        "owner": "claude, working technical lead",
        "host": TARGET,
        "target_identity": TARGET,
        "requested_at": "2026-09-11T09:00:00Z",
        "deadline": "2026-09-11T11:00:00Z",
        "recovery_owner": "peter duscha, operations owner",
    }
    fields.update(overrides)
    return ReservationRequest(**fields)


def _quiet_inventory() -> HostInventory:
    """A host whose every writer is accounted for. The positive control."""
    return HostInventory(
        complete=True,
        taken_at="2026-09-11T08:59:00Z",
        writers=(
            Writer(
                name="postgresql@16-main",
                kind="service",
                disposition=WriterDisposition.REQUIRED_SERVICE,
                accounted_by="operations owner: the disposable cluster the suites use",
            ),
            Writer(
                name="sshd",
                kind="service",
                disposition=WriterDisposition.REQUIRED_SERVICE,
                accounted_by="operations owner: the only access path to the host",
            ),
        ),
    )


def _evidence(**overrides) -> ReleaseEvidence:
    fields = {
        "reservation_id": "RES-1",
        "target_identity": TARGET,
        "lock_held_by": "RES-1",
        "child_processes_ended": True,
        "database_transactions_settled": True,
        "residue": ResidueObservation.empty(observed_by="executor, post-run sweep"),
        "configuration_restored": True,
    }
    fields.update(overrides)
    return ReleaseEvidence(**fields)


def _first_use(**overrides) -> LifecycleHistory:
    """A durable record that was read, is complete, and names no predecessor."""
    fields = {
        "host": TARGET,
        "readable": True,
        "complete": True,
        "disposition": PredecessorDisposition.VERIFIED_FIRST_USE,
        "target_identity": TARGET,
        "first_use_attested_by": "peter duscha, operations owner",
        "first_use_basis": "the host was rebuilt from a fresh image on 2026-09-11",
        "read_at": "2026-09-11T08:58:00Z",
        "read_by": "executor",
    }
    fields.update(overrides)
    return LifecycleHistory(**fields)


def _released_predecessor(**overrides) -> LifecycleHistory:
    """A durable record whose predecessor released, with the record to show it."""
    fields = {
        "host": TARGET,
        "readable": True,
        "complete": True,
        "predecessor_id": "RES-0",
        "predecessor_state": ReservationState.RELEASED,
        "disposition": PredecessorDisposition.RELEASED,
        "release_record": ReleaseRecord(
            reservation_id="RES-0",
            host=TARGET,
            target_identity=TARGET,
            released_at="2026-09-11T08:30:00Z",
            recorded_by="executor of RES-0",
        ),
        "target_identity": TARGET,
        "read_at": "2026-09-11T08:58:00Z",
        "read_by": "executor",
    }
    fields.update(overrides)
    return LifecycleHistory(**fields)


def _admit(**overrides) -> AdmissionDecision:
    """Admission with every observation supplied and nothing defaulted."""
    fields = {
        "request": _request(),
        "inventory": _quiet_inventory(),
        "lock": LockView(held_by=None),
        "approved_target_identity": TARGET,
        "lifecycle": _first_use(),
    }
    fields.update(overrides)
    return admit(**fields)


# ---------------------------------------------------------------------------
# The contract itself
# ---------------------------------------------------------------------------


def test_a_request_without_an_owner_target_or_deadline_is_refused():
    for missing in ("owner", "target_identity", "deadline", "recovery_owner"):
        with pytest.raises(PlanRefused):
            _request(**{missing: "  "})


def test_quarantine_is_terminal_in_the_transition_table():
    assert TRANSITIONS[ReservationState.QUARANTINED] == frozenset()
    assert TRANSITIONS[ReservationState.RELEASED] == frozenset()


def test_a_transition_the_table_does_not_hold_is_refused_by_name():
    with pytest.raises(PlanRefused, match="does not transition"):
        advance(
            current=ReservationState.QUARANTINED, target=ReservationState.ADMITTED
        )
    with pytest.raises(PlanRefused, match="does not transition"):
        advance(current=ReservationState.RECOVERING, target=ReservationState.ADMITTED)


def test_recovery_never_resumes_a_reservation():
    """Recovery ends a reservation. It does not put the host back in service
    under the same owner, which is the shape a takeover would take."""
    assert ReservationState.ADMITTED not in TRANSITIONS[ReservationState.RECOVERING]
    assert ReservationState.RUNNING not in TRANSITIONS[ReservationState.RECOVERING]


def test_an_admitted_decision_cannot_carry_a_refusal():
    with pytest.raises(PlanRefused):
        AdmissionDecision(
            admitted=True,
            state=ReservationState.ADMITTED,
            refusals=("an unknown writer is running",),
        )


def test_a_writer_is_either_accounted_for_or_unknown_and_never_both():
    with pytest.raises(PlanRefused):
        Writer(
            name="mystery",
            kind="process",
            disposition=WriterDisposition.UNKNOWN,
            accounted_by="probably fine",
        )
    with pytest.raises(PlanRefused):
        Writer(
            name="mystery",
            kind="process",
            disposition=WriterDisposition.REQUIRED_SERVICE,
        )


# ---------------------------------------------------------------------------
# Admission
# ---------------------------------------------------------------------------


def test_a_quiet_host_with_a_free_lock_is_admitted():
    """The positive control. Without it every refusal below could be a function
    that refuses everything."""
    decision = admit(
        request=_request(),
        inventory=_quiet_inventory(),
        lock=LockView(held_by=None),
        approved_target_identity=TARGET,
        lifecycle=_first_use(),
    )

    assert decision.admitted is True
    assert decision.state is ReservationState.ADMITTED
    assert decision.refusals == ()


def test_a_second_executor_is_refused_and_does_not_take_the_host():
    decision = admit(
        request=_request(reservation_id="RES-2", owner="another agent"),
        inventory=_quiet_inventory(),
        lock=LockView(held_by="RES-1", holder_owner="claude"),
        approved_target_identity=TARGET,
        lifecycle=_first_use(),
    )

    assert decision.admitted is False
    assert any("held by reservation 'RES-1'" in reason for reason in decision.refusals)
    assert decision.state is ReservationState.REQUESTED


def test_an_unreadable_lock_is_not_an_unheld_lock():
    decision = admit(
        request=_request(),
        inventory=_quiet_inventory(),
        lock=LockView(observation_failed=True),
        approved_target_identity=TARGET,
        lifecycle=_first_use(),
    )

    assert decision.admitted is False
    assert any(HOST_LOCK_PATH in reason for reason in decision.refusals)


def test_an_unknown_writer_refuses_admission_and_is_not_killed():
    """The direction's sentence, asserted: *never kill an unknown process or
    disable an unknown service to obtain admission*. The decision names the
    writer and stops; there is no parameter that would do anything else."""
    inventory = HostInventory(
        complete=True,
        writers=(
            *_quiet_inventory().writers,
            Writer(name="pytest[4711]", kind="process", disposition=WriterDisposition.UNKNOWN),
        ),
    )

    decision = admit(
        request=_request(),
        inventory=inventory,
        lock=LockView(held_by=None),
        approved_target_identity=TARGET,
        lifecycle=_first_use(),
    )

    assert decision.admitted is False
    assert any("pytest[4711]" in reason for reason in decision.refusals)
    assert any("not killed" in reason for reason in decision.refusals)


def test_an_incomplete_inventory_refuses_admission():
    """A partial enumeration establishes nothing about what it did not reach."""
    decision = admit(
        request=_request(),
        inventory=HostInventory(complete=False, writers=_quiet_inventory().writers),
        lock=LockView(held_by=None),
        approved_target_identity=TARGET,
        lifecycle=_first_use(),
    )

    assert decision.admitted is False
    assert any("not complete" in reason for reason in decision.refusals)


def test_a_mismatched_target_refuses_admission():
    decision = admit(
        request=_request(target_identity="some-other-host"),
        inventory=_quiet_inventory(),
        lock=LockView(held_by=None),
        approved_target_identity=TARGET,
        lifecycle=_first_use(),
    )

    assert decision.admitted is False
    assert any("not transferable" in reason for reason in decision.refusals)


def test_a_quarantined_host_is_never_admitted():
    decision = admit(
        request=_request(reservation_id="RES-9"),
        inventory=_quiet_inventory(),
        lock=LockView(held_by=None),
        approved_target_identity=TARGET,
        lifecycle=_first_use(),
        quarantine=QuarantineRecord(
            host=TARGET,
            reservation_id="RES-1",
            reason="cleanup did not complete.",
            residue=("/var/lib/fb-evidence-p5-0/probe",),
        ),
    )

    assert decision.admitted is False
    assert any("No lock release and no elapsed time" in r for r in decision.refusals)


def test_a_cleared_quarantine_does_not_admit_the_request_that_saw_it():
    """Clearing permits a new reservation to be requested. It does not admit the
    one that was already asking against the quarantined host."""
    decision = admit(
        request=_request(reservation_id="RES-9"),
        inventory=_quiet_inventory(),
        lock=LockView(held_by=None),
        approved_target_identity=TARGET,
        lifecycle=_first_use(),
        quarantine=QuarantineRecord(
            host=TARGET,
            reservation_id="RES-1",
            reason="cleanup did not complete.",
            cleared_by_operator=True,
        ),
    )

    assert decision.admitted is False
    assert any("does not admit this one" in reason for reason in decision.refusals)


def test_real_execution_is_refused_while_the_ownership_remedy_is_unaccepted():
    """EH-R16-1 is open, and a reserved host does not close it."""
    decision = admit(
        request=_request(real_execution=True),
        inventory=_quiet_inventory(),
        lock=LockView(held_by=None),
        approved_target_identity=TARGET,
        lifecycle=_first_use(),
    )

    assert decision.admitted is False
    assert REAL_EXECUTION_REFUSAL in decision.refusals


def test_the_synthetic_pass_is_not_blocked_by_the_real_execution_refusal():
    decision = admit(
        request=_request(real_execution=False),
        inventory=_quiet_inventory(),
        lock=LockView(held_by=None),
        approved_target_identity=TARGET,
        lifecycle=_first_use(),
    )

    assert decision.admitted is True


def test_every_refusal_is_reported_rather_than_the_first_one():
    """A caller that fixed one reason and retried would meet the next a run at a
    time, and each rediscovery is a chance to route around it."""
    decision = admit(
        request=_request(target_identity="elsewhere", real_execution=True),
        inventory=HostInventory(complete=False),
        lock=LockView(held_by="RES-OTHER"),
        approved_target_identity=TARGET,
        lifecycle=_first_use(),
    )

    assert len(decision.refusals) >= 4


# ---------------------------------------------------------------------------
# Release
# ---------------------------------------------------------------------------


def test_a_complete_release_releases():
    """The positive control for release."""
    outcome = release(
        request=_request(),
        current_state=ReservationState.RUNNING,
        evidence=_evidence(),
    )

    assert outcome.state is ReservationState.RELEASED
    assert outcome.quarantine is None
    assert outcome.reasons == ()


def test_an_orphaned_child_quarantines_rather_than_releasing():
    outcome = release(
        request=_request(),
        current_state=ReservationState.RUNNING,
        evidence=_evidence(child_processes_ended=False),
    )

    assert outcome.state is ReservationState.QUARANTINED
    assert outcome.quarantine is not None
    assert any("has not exited" in reason for reason in outcome.reasons)


def test_a_delayed_database_transaction_quarantines():
    outcome = release(
        request=_request(),
        current_state=ReservationState.RUNNING,
        evidence=_evidence(database_transactions_settled=False),
    )

    assert outcome.state is ReservationState.QUARANTINED
    assert any("has not settled" in reason for reason in outcome.reasons)


def test_an_unmade_observation_quarantines_exactly_like_a_false_one():
    """An unmade observation is not a passed one, and the report says which of
    the two it was."""
    outcome = release(
        request=_request(),
        current_state=ReservationState.RUNNING,
        evidence=_evidence(child_processes_ended=None),
    )

    assert outcome.state is ReservationState.QUARANTINED
    assert any("were not made" in reason for reason in outcome.reasons)
    assert any("child_processes_ended" in reason for reason in outcome.reasons)


def test_residue_quarantines_and_is_never_cleaned_here():
    outcome = release(
        request=_request(),
        current_state=ReservationState.RUNNING,
        evidence=_evidence(residue=ResidueObservation.found(
            ("/var/lib/fb-evidence-p5-0/probe",), observed_by="executor"
        )),
    )

    assert outcome.state is ReservationState.QUARANTINED
    assert outcome.quarantine is not None
    assert outcome.quarantine.residue == ("/var/lib/fb-evidence-p5-0/probe",)


def test_a_release_naming_another_reservation_quarantines():
    outcome = release(
        request=_request(),
        current_state=ReservationState.RUNNING,
        evidence=_evidence(reservation_id="RES-2"),
    )

    assert outcome.state is ReservationState.QUARANTINED
    assert any("releases nothing here" in reason for reason in outcome.reasons)


def test_a_release_reporting_another_target_quarantines():
    outcome = release(
        request=_request(),
        current_state=ReservationState.RUNNING,
        evidence=_evidence(target_identity="some-other-host"),
    )

    assert outcome.state is ReservationState.QUARANTINED
    assert any("unaccounted activity" in reason for reason in outcome.reasons)


def test_a_lock_released_early_quarantines():
    """Either another participant entered while this run was live, or somebody
    else took the lock. Both are reasons the host is not known to be quiet."""
    outcome = release(
        request=_request(),
        current_state=ReservationState.RUNNING,
        evidence=_evidence(lock_held_by=None),
    )

    assert outcome.state is ReservationState.QUARANTINED
    assert any("released early" in reason for reason in outcome.reasons)


def test_releasing_a_quarantined_reservation_changes_nothing():
    outcome = release(
        request=_request(),
        current_state=ReservationState.QUARANTINED,
        evidence=_evidence(),
    )

    assert outcome.state is ReservationState.QUARANTINED
    assert any("no outgoing transition" in reason for reason in outcome.reasons)


def test_releasing_an_already_released_reservation_is_refused():
    with pytest.raises(PlanRefused):
        release(
            request=_request(),
            current_state=ReservationState.RELEASED,
            evidence=_evidence(),
        )


# ---------------------------------------------------------------------------
# Deadlines, and what they do not authorize
# ---------------------------------------------------------------------------


def test_a_deadline_not_yet_reached_changes_nothing():
    outcome = deadline_reached(
        request=_request(),
        current_state=ReservationState.RUNNING,
        now="2026-09-11T10:00:00Z",
    )

    assert outcome.state is ReservationState.RUNNING


def test_an_expired_reservation_recovers_and_authorizes_no_takeover():
    outcome = deadline_reached(
        request=_request(),
        current_state=ReservationState.RUNNING,
        now="2026-09-11T11:00:01Z",
    )

    assert outcome.state is ReservationState.RECOVERING
    assert any("authorizes no takeover" in reason for reason in outcome.reasons)
    assert any("peter duscha" in reason for reason in outcome.reasons)


def test_an_expired_reservation_never_becomes_released():
    outcome = deadline_reached(
        request=_request(),
        current_state=ReservationState.RUNNING,
        now="2026-09-12T00:00:00Z",
    )

    assert outcome.state is not ReservationState.RELEASED


def test_a_deadline_does_not_reopen_a_quarantine():
    outcome = deadline_reached(
        request=_request(),
        current_state=ReservationState.QUARANTINED,
        now="2026-09-12T00:00:00Z",
    )

    assert outcome.state is ReservationState.QUARANTINED


def test_a_second_executor_is_still_refused_after_the_deadline_passes():
    """The situation an expiry-based takeover would be introduced for, asserted
    to remain a refusal. The lock is still held, so admission still refuses."""
    deadline_reached(
        request=_request(),
        current_state=ReservationState.RUNNING,
        now="2026-09-11T11:30:00Z",
    )
    decision = admit(
        request=_request(reservation_id="RES-2", owner="another agent"),
        inventory=_quiet_inventory(),
        lock=LockView(held_by="RES-1"),
        approved_target_identity=TARGET,
        lifecycle=_first_use(),
    )

    assert decision.admitted is False


# ---------------------------------------------------------------------------
# Recovery
# ---------------------------------------------------------------------------


def test_an_interrupted_recovery_quarantines_and_names_what_is_missing():
    outcome = recover(
        request=_request(),
        attestation=OperatorAttestation(
            operator="peter duscha",
            termination_established=True,
            residue_accounted=False,
            restoration_verified_or_rebuilt=False,
        ),
    )

    assert outcome.state is ReservationState.QUARANTINED
    assert any("residue_accounted" in reason for reason in outcome.reasons)
    assert any("restoration_verified_or_rebuilt" in reason for reason in outcome.reasons)


def test_an_attestation_with_no_operator_is_incomplete():
    outcome = recover(
        request=_request(),
        attestation=OperatorAttestation(
            operator="   ",
            termination_established=True,
            residue_accounted=True,
            restoration_verified_or_rebuilt=True,
        ),
    )

    assert outcome.state is ReservationState.QUARANTINED


def test_a_complete_attestation_without_evidence_still_quarantines():
    """An operator's account of the recovery is not an observation of the
    target, the lock or the residue."""
    outcome = recover(
        request=_request(),
        attestation=OperatorAttestation(
            operator="peter duscha",
            termination_established=True,
            residue_accounted=True,
            restoration_verified_or_rebuilt=True,
        ),
    )

    assert outcome.state is ReservationState.QUARANTINED
    assert any("not an observation" in reason for reason in outcome.reasons)


def test_a_complete_recovery_releases():
    """The positive control for recovery."""
    outcome = recover(
        request=_request(),
        attestation=OperatorAttestation(
            operator="peter duscha",
            termination_established=True,
            residue_accounted=True,
            restoration_verified_or_rebuilt=True,
        ),
        evidence=_evidence(),
    )

    assert outcome.state is ReservationState.RELEASED


def test_a_complete_attestation_does_not_excuse_remaining_residue():
    outcome = recover(
        request=_request(),
        attestation=OperatorAttestation(
            operator="peter duscha",
            termination_established=True,
            residue_accounted=True,
            restoration_verified_or_rebuilt=True,
        ),
        evidence=_evidence(residue=ResidueObservation.found(
            ("/var/lib/fb-evidence-p5-0/probe",), observed_by="executor"
        )),
    )

    assert outcome.state is ReservationState.QUARANTINED


# ---------------------------------------------------------------------------
# The lock contract
# ---------------------------------------------------------------------------


def test_every_project_entry_point_that_touches_the_host_participates():
    """The lock is only as good as the set of entry points that take it, so the
    set is enumerated and this asserts the ones the direction names."""
    participants = " ".join(PARTICIPATING_ENTRY_POINTS)

    assert "tests/test_*.py" in participants
    assert "tests/web" in participants
    assert "foundry-module/tests" in participants
    assert "synchronization" in participants
    assert "dependency updates" in participants
    assert "environment reset" in participants
    assert "execution/cli.py" in participants


def test_the_lock_does_not_claim_to_revoke_root():
    """Manual root access stays a trusted operational premise. A mechanism that
    claimed otherwise would be claiming something it cannot do."""
    limits = " ".join(LOCK_LIMITS)

    assert "advisory and cooperative" in limits
    assert "revokes no permission" in limits
    assert "trusted operational premise" in limits


def test_holding_the_lock_is_not_evidence_that_the_host_is_quiet():
    """Lock plus incomplete inventory still refuses, which is the property that
    sentence describes."""
    decision = admit(
        request=_request(),
        inventory=HostInventory(complete=False),
        lock=LockView(held_by="RES-1"),
        approved_target_identity=TARGET,
        lifecycle=_first_use(),
    )

    assert decision.admitted is False


def test_the_module_introduces_no_scheduler_manager_or_shell():
    """The direction rules out three things by name. This asserts the absence of
    each against the module's own surface rather than against its docstring."""
    from tools.phase_5_0_evidence import reservation

    exported = set(reservation.__all__)
    for forbidden in ("spawn", "run", "execute", "kill", "terminate", "acquire"):
        assert not any(forbidden in name.lower() for name in exported)


# ---------------------------------------------------------------------------
# PR-20260911-3 — admission cannot infer a released predecessor
# ---------------------------------------------------------------------------


def test_a_free_readable_lock_with_no_lifecycle_history_refuses():
    """The reproduction from the September 11 review, now a refusal.

    A readable, free lock and a complete inventory with nothing unknown used to
    admit. They cannot: the lock disappears with the process whether or not the
    run finished, and the inventory can be quiet while a server-side transaction
    the run opened is still open.
    """
    decision = _admit(lifecycle=LifecycleHistory(host=TARGET))

    assert decision.admitted is False
    assert any("could not be read" in reason for reason in decision.refusals)


def test_an_unreadable_history_is_not_an_empty_history():
    decision = _admit(
        lifecycle=LifecycleHistory(
            host=TARGET,
            readable=False,
            disposition=PredecessorDisposition.VERIFIED_FIRST_USE,
        )
    )

    assert decision.admitted is False
    assert any("not an empty record" in reason for reason in decision.refusals)


def test_an_incomplete_history_refuses_however_clean_the_part_that_was_read():
    decision = _admit(lifecycle=_first_use(complete=False))

    assert decision.admitted is False
    assert any("not complete" in reason for reason in decision.refusals)


def test_an_unclassified_predecessor_refuses():
    decision = _admit(
        lifecycle=LifecycleHistory(host=TARGET, readable=True, complete=True)
    )

    assert decision.admitted is False
    assert any("disposition is unknown" in reason for reason in decision.refusals)


def test_a_crashed_predecessor_with_a_free_lock_refuses():
    """The expired/crashed executor, with its process lock already gone."""
    decision = _admit(
        lock=LockView(held_by=None),
        lifecycle=LifecycleHistory(
            host=TARGET,
            readable=True,
            complete=True,
            predecessor_id="RES-0",
            predecessor_state=ReservationState.RUNNING,
            disposition=PredecessorDisposition.ACTIVE,
        ),
    )

    assert decision.admitted is False
    assert any("still active on this host" in reason for reason in decision.refusals)


def test_a_crash_after_effects_but_before_quarantine_publication_refuses():
    """`DURABLE_RECORD_ORDERING` item 3, as an injected case.

    The predecessor issued effects and died before it could publish a quarantine
    record, so no quarantine argument is available to supply. The durable record
    still says RUNNING, and that — not the missing quarantine — is what refuses.
    """
    decision = _admit(
        lock=LockView(held_by=None),
        quarantine=None,
        lifecycle=LifecycleHistory(
            host=TARGET,
            readable=True,
            complete=True,
            predecessor_id="RES-0",
            predecessor_state=ReservationState.RUNNING,
            disposition=PredecessorDisposition.ACTIVE,
        ),
    )

    assert decision.admitted is False
    assert any("free process lock does not contradict" in r for r in decision.refusals)


def test_a_recovering_predecessor_refuses():
    decision = _admit(
        lifecycle=LifecycleHistory(
            host=TARGET,
            readable=True,
            complete=True,
            predecessor_id="RES-0",
            predecessor_state=ReservationState.RECOVERING,
            disposition=PredecessorDisposition.RECOVERING,
        )
    )

    assert decision.admitted is False
    assert any("is recovering" in reason for reason in decision.refusals)


def test_a_quarantined_predecessor_in_the_record_refuses_without_a_quarantine_argument():
    """The record is sufficient on its own; the argument is a second channel."""
    decision = _admit(
        quarantine=None,
        lifecycle=LifecycleHistory(
            host=TARGET,
            readable=True,
            complete=True,
            predecessor_id="RES-0",
            predecessor_state=ReservationState.QUARANTINED,
            disposition=PredecessorDisposition.QUARANTINED,
        ),
    )

    assert decision.admitted is False
    assert any("quarantined this host" in reason for reason in decision.refusals)


def test_a_released_state_with_no_release_record_refuses():
    decision = _admit(lifecycle=_released_predecessor(release_record=None))

    assert decision.admitted is False
    assert any("no release record to show" in reason for reason in decision.refusals)


def test_a_release_record_for_another_reservation_refuses():
    decision = _admit(
        lifecycle=_released_predecessor(
            release_record=ReleaseRecord(
                reservation_id="RES-SOMEBODY-ELSE",
                host=TARGET,
                target_identity=TARGET,
                released_at="2026-09-11T08:30:00Z",
                recorded_by="another executor",
            )
        )
    )

    assert decision.admitted is False
    assert any("releases nothing here" in reason for reason in decision.refusals)


def test_a_release_record_for_another_host_refuses():
    decision = _admit(
        lifecycle=_released_predecessor(
            release_record=ReleaseRecord(
                reservation_id="RES-0",
                host="some-other-host",
                target_identity=TARGET,
                released_at="2026-09-11T08:30:00Z",
                recorded_by="executor of RES-0",
            )
        )
    )

    assert decision.admitted is False
    assert any("names host 'some-other-host'" in reason for reason in decision.refusals)


def test_a_history_read_for_another_host_refuses():
    decision = _admit(lifecycle=_first_use(host="some-other-host"))

    assert decision.admitted is False
    assert any("is evidence about that host" in reason for reason in decision.refusals)


def test_a_first_use_claim_that_also_names_a_predecessor_refuses():
    decision = _admit(
        lifecycle=_first_use(
            predecessor_id="RES-0", predecessor_state=ReservationState.RUNNING
        )
    )

    assert decision.admitted is False
    assert any("One of the two is wrong" in reason for reason in decision.refusals)


def test_verified_first_use_is_a_positive_control():
    decision = _admit(lifecycle=_first_use())

    assert decision.admitted is True
    assert decision.state is ReservationState.ADMITTED


def test_a_verified_predecessor_release_is_a_positive_control():
    decision = _admit(lifecycle=_released_predecessor())

    assert decision.admitted is True
    assert decision.state is ReservationState.ADMITTED


def test_a_completed_operator_recovery_admits_a_new_reservation():
    """Recovery permits a **new** reservation; it never resumes the old one."""
    decision = _admit(
        request=_request(reservation_id="RES-2"),
        lifecycle=_recovered(),
    )

    assert decision.admitted is True


def test_an_operator_recovery_never_resumes_the_quarantined_run():
    decision = _admit(
        request=_request(reservation_id="RES-0"),
        lifecycle=LifecycleHistory(
            host=TARGET,
            readable=True,
            complete=True,
            predecessor_id="RES-0",
            predecessor_state=ReservationState.QUARANTINED,
            disposition=PredecessorDisposition.OPERATOR_RECOVERED,
            operator_recovery_reference="ops-recovery-2026-09-11-01",
        ),
    )

    assert decision.admitted is False
    assert any("never resumes the quarantined run" in r for r in decision.refusals)


def test_an_unattributed_operator_recovery_refuses():
    decision = _admit(
        request=_request(reservation_id="RES-2"),
        lifecycle=LifecycleHistory(
            host=TARGET,
            readable=True,
            complete=True,
            predecessor_id="RES-0",
            disposition=PredecessorDisposition.OPERATOR_RECOVERED,
        ),
    )

    assert decision.admitted is False
    assert any("names no recovery reference" in reason for reason in decision.refusals)


def test_an_elapsed_deadline_does_not_stand_in_for_a_release():
    """A predecessor whose deadline passed is RECOVERING, and still refuses."""
    predecessor = _request(reservation_id="RES-0", deadline="2026-09-11T09:30:00Z")
    expired = deadline_reached(
        request=predecessor,
        current_state=ReservationState.RUNNING,
        now="2026-09-11T10:00:00Z",
    )
    assert expired.state is ReservationState.RECOVERING

    decision = _admit(
        request=_request(reservation_id="RES-1"),
        lifecycle=LifecycleHistory(
            host=TARGET,
            readable=True,
            complete=True,
            predecessor_id="RES-0",
            predecessor_state=expired.state,
            disposition=PredecessorDisposition.RECOVERING,
        ),
    )

    assert decision.admitted is False


def test_the_durable_record_ordering_is_stated_and_puts_the_record_first():
    assert len(DURABLE_RECORD_ORDERING) == 5
    assert "before the first effect" in DURABLE_RECORD_ORDERING[0]
    assert "never evidence that" in DURABLE_RECORD_ORDERING[2]


# ---------------------------------------------------------------------------
# PR-20260911-4 — an unobserved residue check is not a passed one
# ---------------------------------------------------------------------------


def test_omitted_residue_evidence_quarantines():
    """The review's minimal reproduction, now a quarantine."""
    outcome = release(
        request=_request(),
        current_state=ReservationState.RUNNING,
        evidence=_evidence(residue=None),
    )

    assert outcome.state is ReservationState.QUARANTINED
    assert any("'residue'" in reason for reason in outcome.reasons)


def test_an_explicitly_unmade_residue_observation_quarantines_the_same_way():
    outcome = release(
        request=_request(),
        current_state=ReservationState.RUNNING,
        evidence=_evidence(residue=ResidueObservation.not_made()),
    )

    assert outcome.state is ReservationState.QUARANTINED


def test_observed_empty_residue_releases():
    """The positive control that separates *nobody looked* from *nothing there*."""
    outcome = release(
        request=_request(),
        current_state=ReservationState.RUNNING,
        evidence=_evidence(
            residue=ResidueObservation.empty(observed_by="executor, post-run sweep")
        ),
    )

    assert outcome.state is ReservationState.RELEASED


def test_observed_present_residue_quarantines_and_names_the_paths():
    outcome = release(
        request=_request(),
        current_state=ReservationState.RUNNING,
        evidence=_evidence(
            residue=ResidueObservation.found(
                ("/var/lib/fb-evidence-p5-0/probe",), observed_by="executor"
            )
        ),
    )

    assert outcome.state is ReservationState.QUARANTINED
    assert outcome.quarantine is not None
    assert outcome.quarantine.residue == ("/var/lib/fb-evidence-p5-0/probe",)


def test_an_incomplete_residue_search_is_not_an_observed_empty_one():
    outcome = release(
        request=_request(),
        current_state=ReservationState.RUNNING,
        evidence=_evidence(
            residue=ResidueObservation(
                observed=True, paths=(), complete=False, observed_by="executor"
            )
        ),
    )

    assert outcome.state is ReservationState.QUARANTINED
    assert any("did not complete" in reason for reason in outcome.reasons)


def test_a_residue_observation_with_no_observer_is_refused():
    with pytest.raises(PlanRefused):
        ResidueObservation(observed=True, paths=(), complete=True)


def test_an_unmade_residue_observation_cannot_carry_a_result():
    with pytest.raises(PlanRefused):
        ResidueObservation(observed=False, paths=("/…/probe",))


def test_a_bare_path_tuple_is_refused_rather_than_coerced():
    with pytest.raises(PlanRefused):
        _evidence(residue=())


# ---------------------------------------------------------------------------
# PR-20260911-4 — the public transition helpers are audited
# ---------------------------------------------------------------------------


def test_advance_refuses_to_release_without_a_release_outcome():
    """The review's second reproduction: `advance(RUNNING, RELEASED)`."""
    with pytest.raises(PlanRefused):
        advance(current=ReservationState.RUNNING, target=ReservationState.RELEASED)


def test_advance_refuses_to_admit_without_an_admission_decision():
    with pytest.raises(PlanRefused):
        advance(current=ReservationState.REQUESTED, target=ReservationState.ADMITTED)


def test_advance_refuses_a_release_outcome_that_quarantined():
    quarantined = release(
        request=_request(),
        current_state=ReservationState.RUNNING,
        evidence=_evidence(residue=None),
    )

    with pytest.raises(PlanRefused):
        advance(
            current=ReservationState.RUNNING,
            target=ReservationState.RELEASED,
            decision=quarantined,
        )


def test_advance_refuses_an_admission_decision_that_refused():
    refused = _admit(lifecycle=LifecycleHistory(host=TARGET))

    with pytest.raises(PlanRefused):
        advance(
            current=ReservationState.REQUESTED,
            target=ReservationState.ADMITTED,
            decision=refused,
        )


def test_advance_refuses_the_wrong_kind_of_decision():
    released = release(
        request=_request(),
        current_state=ReservationState.RUNNING,
        evidence=_evidence(),
    )

    with pytest.raises(PlanRefused):
        advance(
            current=ReservationState.REQUESTED,
            target=ReservationState.ADMITTED,
            decision=released,
        )


def test_advance_admits_and_releases_on_the_corresponding_validated_decision():
    """The positive control. Both guarded edges, each with its own decision."""
    decision = _admit()
    assert (
        advance(
            current=ReservationState.REQUESTED,
            target=ReservationState.ADMITTED,
            decision=decision,
        )
        is ReservationState.ADMITTED
    )

    outcome = release(
        request=_request(),
        current_state=ReservationState.RUNNING,
        evidence=_evidence(),
    )
    assert (
        advance(
            current=ReservationState.RUNNING,
            target=ReservationState.RELEASED,
            decision=outcome,
        )
        is ReservationState.RELEASED
    )


def test_quarantine_and_recovery_stay_unguarded():
    """A guard that made quarantine harder to reach would point the wrong way."""
    assert (
        advance(current=ReservationState.RUNNING, target=ReservationState.QUARANTINED)
        is ReservationState.QUARANTINED
    )
    assert (
        advance(current=ReservationState.RUNNING, target=ReservationState.RECOVERING)
        is ReservationState.RECOVERING
    )
    assert set(GUARDED_TRANSITIONS) == {
        ReservationState.ADMITTED,
        ReservationState.RELEASED,
    }


def test_a_decision_supplied_for_an_unguarded_transition_is_refused():
    with pytest.raises(PlanRefused):
        advance(
            current=ReservationState.RUNNING,
            target=ReservationState.RECOVERING,
            decision=_admit(),
        )


def test_quarantine_survives_a_lost_lock_and_an_elapsed_deadline():
    """Neither event has an edge out of quarantine, and neither creates one."""
    quarantined = release(
        request=_request(),
        current_state=ReservationState.RUNNING,
        evidence=_evidence(lock_held_by=None, residue=None),
    )
    assert quarantined.state is ReservationState.QUARANTINED

    after_deadline = deadline_reached(
        request=_request(),
        current_state=ReservationState.QUARANTINED,
        now="2026-09-12T00:00:00Z",
    )
    assert after_deadline.state is ReservationState.QUARANTINED
    with pytest.raises(PlanRefused):
        advance(
            current=ReservationState.QUARANTINED, target=ReservationState.RELEASED
        )


# ---------------------------------------------------------------------------
# What these decisions are not
# ---------------------------------------------------------------------------


def test_the_module_says_it_persists_and_enforces_nothing():
    joined = " ".join(DECISIONS_DO_NOT_PERSIST)

    assert "persist nothing" in joined
    assert "is not a reservation" in joined


def test_the_adapter_responsibilities_are_named_separately_and_not_implemented():
    joined = " ".join(ADAPTER_RESPONSIBILITIES).lower()

    for owed in ("cooperative lock", "durable lifecycle record", "inventory", "enforcing"):
        assert owed in joined


def test_real_execution_stays_refused_under_every_positive_control():
    """The refusal is unconditional and a repaired admission does not clear it."""
    for history in (_first_use(), _released_predecessor()):
        decision = _admit(
            request=_request(real_execution=True), lifecycle=history
        )
        assert decision.admitted is False
        assert REAL_EXECUTION_REFUSAL in decision.refusals


# ---------------------------------------------------------------------------
# PR-20260911-R2-1 — a contradictory lifecycle record must not admit
#
# The re-review's reproduction: a readable, complete history, a free lock, a
# complete inventory and a matching ReleaseRecord, with `predecessor_state` set
# to RUNNING or QUARANTINED, returned `admitted=True`. The disposition was read
# and the state beside it was not, so a release record was allowed to override
# the state it contradicted.
#
# The rule these cases assert is the one the repair implements: the lifecycle
# record is validated as a **coherent whole** — state, disposition, predecessor
# identity and attached evidence must agree — **before** any admitting branch is
# chosen. A contradiction is refused, not resolved in favour of reuse.
# ---------------------------------------------------------------------------


#: Every predecessor state the re-review names, paired with RELEASED, plus the
#: valid control. `True` is the one combination that may admit.
RELEASED_DISPOSITION_STATE_TABLE = (
    (ReservationState.ADMITTED, False),
    (ReservationState.RUNNING, False),
    (ReservationState.RECOVERING, False),
    (ReservationState.QUARANTINED, False),
    (ReservationState.REQUESTED, False),
    (None, False),
    (ReservationState.RELEASED, True),
)


@pytest.mark.parametrize("state, admits", RELEASED_DISPOSITION_STATE_TABLE)
def test_a_released_disposition_admits_only_a_released_state(state, admits):
    """PR-20260911-R2-1, as a table. Everything but RELEASED is contradictory."""
    decision = _admit(lifecycle=_released_predecessor(predecessor_state=state))

    assert decision.admitted is admits
    if not admits:
        assert any("contradictory" in reason for reason in decision.refusals)


def test_the_reviews_exact_reproduction_no_longer_admits():
    """The reviewer's own input: a matching release record, varying only state."""
    for state in (ReservationState.RUNNING, ReservationState.QUARANTINED):
        decision = admit(
            request=_request(),
            inventory=HostInventory(complete=True, taken_at="2026-09-11T08:59:00Z"),
            lock=LockView(),
            approved_target_identity=TARGET,
            lifecycle=_released_predecessor(predecessor_state=state),
        )

        assert decision.admitted is False, state
        assert any("contradictory" in reason for reason in decision.refusals)


def test_a_release_record_does_not_override_a_contradictory_state():
    """The record is complete, readable and bound. The state still refuses."""
    decision = _admit(lifecycle=_released_predecessor(predecessor_state=ReservationState.RUNNING))

    assert decision.admitted is False
    joined = " ".join(decision.refusals)
    assert "'released'" in joined and "'running'" in joined


def test_the_valid_released_control_still_admits():
    decision = _admit(lifecycle=_released_predecessor())

    assert decision.admitted is True
    assert decision.state is ReservationState.ADMITTED


def test_the_wrong_host_wrong_target_and_wrong_reservation_release_tests_are_retained():
    """R2-1 requires the three existing release-record bindings to survive."""
    wrong_reservation = _admit(
        lifecycle=_released_predecessor(
            release_record=ReleaseRecord(
                reservation_id="RES-SOMEBODY-ELSE",
                host=TARGET,
                target_identity=TARGET,
                released_at="2026-09-11T08:30:00Z",
                recorded_by="another executor",
            )
        )
    )
    wrong_host = _admit(
        lifecycle=_released_predecessor(
            release_record=ReleaseRecord(
                reservation_id="RES-0",
                host="some-other-host",
                target_identity=TARGET,
                released_at="2026-09-11T08:30:00Z",
                recorded_by="executor of RES-0",
            )
        )
    )
    wrong_target = _admit(
        lifecycle=_released_predecessor(
            release_record=ReleaseRecord(
                reservation_id="RES-0",
                host=TARGET,
                target_identity="some-other-target",
                released_at="2026-09-11T08:30:00Z",
                recorded_by="executor of RES-0",
            )
        )
    )

    for decision in (wrong_reservation, wrong_host, wrong_target):
        assert decision.admitted is False


# --- verified first use, audited ------------------------------------------


@pytest.mark.parametrize(
    "overrides, expected",
    (
        ({"predecessor_state": ReservationState.RUNNING}, "contradictory"),
        ({"predecessor_id": "RES-0"}, "One of the two is wrong"),
        (
            {
                "release_record": ReleaseRecord(
                    reservation_id="RES-0",
                    host=TARGET,
                    target_identity=TARGET,
                    released_at="2026-09-11T08:30:00Z",
                    recorded_by="executor of RES-0",
                )
            },
            "carries a release record",
        ),
        ({"operator_recovery_reference": "ops-recovery-01"}, "recovery reference"),
    ),
)
def test_verified_first_use_carries_no_incompatible_evidence(overrides, expected):
    """A first use that also carries predecessor or recovery evidence refuses."""
    decision = _admit(lifecycle=_first_use(**overrides))

    assert decision.admitted is False
    assert any(expected in reason for reason in decision.refusals)


def test_verified_first_use_stays_distinguishable_from_missing_history():
    """The claim admits; not knowing refuses. They are different inputs."""
    claimed = _admit(lifecycle=_first_use())
    unclassified = _admit(
        lifecycle=LifecycleHistory(host=TARGET, readable=True, complete=True)
    )
    unread = _admit(lifecycle=LifecycleHistory(host=TARGET))

    assert claimed.admitted is True
    assert unclassified.admitted is False
    assert any("disposition is unknown" in r for r in unclassified.refusals)
    assert unread.admitted is False
    assert any("could not be read" in r for r in unread.refusals)


# --- operator recovery, audited -------------------------------------------


def _recovered(**overrides) -> LifecycleHistory:
    fields = {
        "host": TARGET,
        "readable": True,
        "complete": True,
        "predecessor_id": "RES-0",
        "predecessor_state": ReservationState.QUARANTINED,
        "disposition": PredecessorDisposition.OPERATOR_RECOVERED,
        "operator_recovery_reference": "ops-recovery-2026-09-11-01",
        "target_identity": TARGET,
        "recovery_authored_by": "peter duscha, operations owner",
    }
    fields.update(overrides)
    return LifecycleHistory(**fields)


def test_operator_recovery_must_name_the_predecessor_it_recovered():
    decision = _admit(
        request=_request(reservation_id="RES-2"),
        lifecycle=_recovered(predecessor_id=""),
    )

    assert decision.admitted is False
    assert any("names no predecessor" in reason for reason in decision.refusals)


@pytest.mark.parametrize(
    "state",
    (
        ReservationState.RUNNING,
        ReservationState.RELEASED,
        ReservationState.ADMITTED,
        ReservationState.RECOVERING,
        None,
    ),
)
def test_operator_recovery_requires_a_quarantined_predecessor(state):
    """A recovery entry is appended to a quarantine. Any other state disagrees."""
    decision = _admit(
        request=_request(reservation_id="RES-2"),
        lifecycle=_recovered(predecessor_state=state),
    )

    assert decision.admitted is False
    assert any("contradictory" in reason for reason in decision.refusals)


def test_operator_recovery_carrying_a_release_record_refuses():
    decision = _admit(
        request=_request(reservation_id="RES-2"),
        lifecycle=_recovered(
            release_record=ReleaseRecord(
                reservation_id="RES-0",
                host=TARGET,
                target_identity=TARGET,
                released_at="2026-09-11T08:30:00Z",
                recorded_by="executor of RES-0",
            )
        ),
    )

    assert decision.admitted is False
    assert any("carries a release record" in reason for reason in decision.refusals)


def test_operator_recovery_preserves_the_quarantined_reservations_history():
    """The quarantined run stays quarantined: only a new reservation admits."""
    resumed = _admit(request=_request(reservation_id="RES-0"), lifecycle=_recovered())
    fresh = _admit(request=_request(reservation_id="RES-2"), lifecycle=_recovered())

    assert resumed.admitted is False
    assert any("never resumes the quarantined run" in r for r in resumed.refusals)
    assert fresh.admitted is True


# --- the refusing dispositions, audited for fall-through -------------------


@pytest.mark.parametrize(
    "disposition, state",
    (
        (PredecessorDisposition.ACTIVE, ReservationState.ADMITTED),
        (PredecessorDisposition.ACTIVE, ReservationState.RUNNING),
        (PredecessorDisposition.RECOVERING, ReservationState.RECOVERING),
        (PredecessorDisposition.QUARANTINED, ReservationState.QUARANTINED),
    ),
)
def test_a_coherent_refusing_disposition_still_refuses(disposition, state):
    """Coherence is not admission: these records agree with themselves and refuse."""
    decision = _admit(
        lifecycle=LifecycleHistory(
            host=TARGET,
            readable=True,
            complete=True,
            predecessor_id="RES-0",
            predecessor_state=state,
            disposition=disposition,
            target_identity=TARGET,
        )
    )

    assert decision.admitted is False


def test_an_active_predecessor_carrying_a_release_record_refuses_twice():
    """Stale release metadata beside a later active state is the R2-1 shape."""
    decision = _admit(
        lifecycle=LifecycleHistory(
            host=TARGET,
            readable=True,
            complete=True,
            predecessor_id="RES-0",
            predecessor_state=ReservationState.RUNNING,
            disposition=PredecessorDisposition.ACTIVE,
            target_identity=TARGET,
            release_record=ReleaseRecord(
                reservation_id="RES-0",
                host=TARGET,
                target_identity=TARGET,
                released_at="2026-09-11T08:30:00Z",
                recorded_by="executor of RES-0",
            ),
        )
    )

    assert decision.admitted is False
    assert any("carries a release record" in reason for reason in decision.refusals)
    assert any("still active on this host" in reason for reason in decision.refusals)


def test_a_malformed_lifecycle_value_refuses_rather_than_falling_through():
    """A value outside the vocabulary is not a value the branches may compare."""
    malformed_disposition = _admit(
        lifecycle=LifecycleHistory(
            host=TARGET, readable=True, complete=True, disposition="released"
        )
    )
    malformed_state = _admit(
        lifecycle=_released_predecessor(predecessor_state="released")
    )

    for decision in (malformed_disposition, malformed_state):
        assert decision.admitted is False
        assert any("malformed" in reason for reason in decision.refusals)


def test_every_admitting_disposition_is_covered_by_a_stated_shape():
    """The accepted combinations are stated in code, not inferred from branches."""
    assert set(LIFECYCLE_SHAPES) == set(PredecessorDisposition)
    assert VALIDATED_LIFECYCLE_OUTCOMES == ADMITTING_DISPOSITIONS
    for disposition, shape in LIFECYCLE_SHAPES.items():
        assert shape.admits is (disposition in VALIDATED_LIFECYCLE_OUTCOMES)


def test_the_shared_validator_and_admit_agree():
    """R2-4: participants and the executor share one decision, not two."""
    for history, expected in (
        (_first_use(), True),
        (_released_predecessor(), True),
        (_released_predecessor(predecessor_state=ReservationState.RUNNING), False),
        (LifecycleHistory(host=TARGET), False),
    ):
        validation = validate_lifecycle(
            history=history, host=TARGET, target_identity=TARGET
        )
        decision = _admit(lifecycle=history)

        assert validation.admits is expected
        assert decision.admitted is expected


# --- PR-20260911-R3-3: the binding and the attributable evidence ------------
#
# These exercise `validate_lifecycle` **directly**, and deliberately not through
# the storage model. The stored-record parser refuses a wrong-target record
# before the validator ever sees one, so a test that went through the parser
# would pass with this rule deleted — which it did, until these were added. The
# rule is defence in depth and it needs its own regression.


def _admitting_histories():
    return (
        ("verified first use", _first_use()),
        ("a released predecessor", _released_predecessor()),
        ("an operator recovery", _recovered()),
    )


@pytest.mark.parametrize(
    "label, history", _admitting_histories(), ids=[row[0] for row in _admitting_histories()]
)
def test_an_admitting_history_bound_to_another_target_refuses(label, history):
    """The same hostname is not the same approved target — R3-3's finding.

    Before this pass `LifecycleHistory` had no target field at all, so FIRST_USE
    and OPERATOR_RECOVERED compared nothing and RELEASED compared only inside
    its own `ReleaseRecord`.
    """
    validation = validate_lifecycle(
        history=history, host=TARGET, target_identity="oracle-test-rebuilt"
    )

    assert validation.admits is False
    assert any("is bound to target" in reason for reason in validation.refusals)


@pytest.mark.parametrize(
    "label, history", _admitting_histories(), ids=[row[0] for row in _admitting_histories()]
)
def test_an_admitting_history_with_no_binding_at_all_refuses(label, history):
    """An unbound record is evidence about an unnamed target, not a wildcard."""
    unbound = LifecycleHistory(
        **{
            **{
                name: getattr(history, name)
                for name in (
                    "host",
                    "readable",
                    "complete",
                    "predecessor_id",
                    "predecessor_state",
                    "disposition",
                    "release_record",
                    "operator_recovery_reference",
                    "first_use_attested_by",
                    "first_use_basis",
                    "recovery_authored_by",
                )
            },
            "target_identity": "",
        }
    )

    validation = validate_lifecycle(
        history=unbound, host=TARGET, target_identity=TARGET
    )

    assert validation.admits is False
    assert any(
        "names no approved target identity" in reason
        for reason in validation.refusals
    )


def test_a_first_use_without_its_attestation_refuses_at_the_validator():
    """The author and the basis both travel, and both are required."""
    for missing in ("first_use_attested_by", "first_use_basis"):
        validation = validate_lifecycle(
            history=_first_use(**{missing: ""}),
            host=TARGET,
            target_identity=TARGET,
        )

        assert validation.admits is False, missing
        assert validation.coherent is False


def test_an_operator_recovery_without_a_named_author_refuses():
    """The reference says which recovery; the author says whose. Both required."""
    validation = validate_lifecycle(
        history=_recovered(recovery_authored_by=""),
        host=TARGET,
        target_identity=TARGET,
    )

    assert validation.admits is False
    assert any("names nobody as having performed it" in r for r in validation.refusals)


def test_a_predecessor_record_carrying_a_first_use_attestation_refuses():
    """A host cannot both have a predecessor and never have been reserved."""
    validation = validate_lifecycle(
        history=_released_predecessor(
            first_use_attested_by="somebody", first_use_basis="a fresh image"
        ),
        host=TARGET,
        target_identity=TARGET,
    )

    assert validation.admits is False
    assert validation.coherent is False
    assert any("never have been reserved" in reason for reason in validation.refusals)


def test_every_admitting_shape_requires_the_binding_and_its_evidence():
    """Stated in the table rather than left to the branches that read it."""
    for disposition in VALIDATED_LIFECYCLE_OUTCOMES:
        shape = LIFECYCLE_SHAPES[disposition]
        assert shape.target_binding is EvidenceRule.REQUIRED, disposition

    first_use = LIFECYCLE_SHAPES[PredecessorDisposition.VERIFIED_FIRST_USE]
    recovered = LIFECYCLE_SHAPES[PredecessorDisposition.OPERATOR_RECOVERED]
    assert first_use.first_use_attestation is EvidenceRule.REQUIRED
    assert recovered.recovery_author is EvidenceRule.REQUIRED
    for disposition, shape in LIFECYCLE_SHAPES.items():
        if disposition is not PredecessorDisposition.VERIFIED_FIRST_USE:
            assert shape.first_use_attestation is not EvidenceRule.REQUIRED
