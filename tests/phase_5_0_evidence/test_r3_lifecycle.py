"""The complete lifecycle, over records a reader parses — R3-1, R3-2 and R3-3.

**Every test in this file is a model test.** It exercises
`tools/phase_5_0_evidence/lifecycle_storage.py` and
`tools/phase_5_0_evidence/durability_model.py`, which are deterministic
in-memory arrangements of rules proposed in runner contract **revision 4**. The
mechanism those rules describe is **not built**: no privileged mechanism, no
filesystem writer, no lock adapter and no operational integration exists, and
nothing here creates one. A passing row establishes that the proposed rule is
constructible and falsifiable, and **nothing** about Linux, about `oracle-test`
or about EH-R16-1.

What separates this file from `test_r2_proposal_models.py` is that the scenarios
are **connected**. A successful scenario writes its record, reads those bytes
back through a descriptor, parses them with the shared schema, validates them
with `reservation.validate_lifecycle()`, performs injected effects, publishes
completion and admits a successor from the stored evidence. A failure scenario
follows the same path through interruption, restart and recovery. The two
`UNIT_TEST_CONSTRUCTORS` are not used here at all.

Four negative controls carry the weight:

* `test_the_revision_3_protocol_admits_on_a_record_a_power_loss_removes` — the
  uncorrected protocol must **fail** the corrected property;
* `test_a_clean_wrapper_exit_and_a_free_lock_are_not_completion_evidence` — the
  two things R3-2 names must be shown **not** to settle a run;
* `test_a_first_use_history_for_another_target_refuses` — R3-3's reproduction,
  which admitted seven of seven before this pass; and
* `test_the_lifecycle_model_makes_no_oracle_observation` — the reader must be
  shown unable to consult the durable-state map a real participant cannot see.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

from tools.phase_5_0_evidence.durability_model import (
    DescriptorMode,
    ModelRefused,
    SyntheticFilesystem,
)
from tools.phase_5_0_evidence.lifecycle_storage import (
    ENTRY_STATES,
    HISTORY_ORDER_RULES,
    HISTORY_TERMINATOR,
    KIND_FIELDS,
    NOT_COMPLETION_EVIDENCE,
    PARTICIPANTS,
    PARTICIPANT_KINDS,
    PARTICIPANT_PROFILES,
    PUBLICATION_UNCERTAINTY,
    RECORD_MAGIC,
    RESEAL_CONTRACT,
    RESERVATION_KINDS,
    SUPPORTED_SCHEMA_VERSIONS,
    TERMINAL_STATES,
    AdmissionPolicy,
    CompletionObservation,
    DurableRecordStore,
    EntryKind,
    FirstUseEvidence,
    FirstUseRefusal,
    Participant,
    PublicationRefusal,
    CompletionEvidence,
    RecordEntry,
    RecordRefusal,
    RunLedger,
    TERMINAL_PUBLICATION_ORDER,
    check_history_semantics,
    check_participant_history,
    check_reservation_history,
    conclude_reservation,
    derive_lifecycle_history,
    initialize_first_use_record,
    parse_history,
    read_and_admit,
    serialize_history,
)
from tools.phase_5_0_evidence.reservation import (
    LockView,
    PredecessorDisposition,
    QuarantineRecord,
    ReleaseEvidence,
    ReservationRequest,
    ReservationState,
    ResidueObservation,
)

from tests.phase_5_0_evidence.lifecycle_fixtures import (
    ATTESTER,
    BASIS,
    HOST,
    OTHER_TARGET,
    TARGET,
    Laboratory,
    observed as _observed,
)

MODULE = pathlib.Path("tools/phase_5_0_evidence/lifecycle_storage.py")


# ---------------------------------------------------------------------------
# R3-1 — the publication/restart gap
# ---------------------------------------------------------------------------


def test_the_reviewers_reproduction_still_reproduces_against_the_writer():
    """The exact input the R3 review reported, unchanged and still true.

    The writer's outcome is NOT_DURABLE, the final record is visible, its entry
    is not durable, and a retry says ALREADY_INITIALIZED. **This is not the
    defect's repair**; it is the state the successor protocol now has to cope
    with, and it is asserted so that a change which quietly removed the window
    would fail here rather than pass silently.
    """
    laboratory = Laboratory()

    outcome = laboratory.initialize(fail_at="record-entry")

    assert outcome.initialized is False
    assert outcome.refusal is FirstUseRefusal.NOT_DURABLE
    assert outcome.barriers == ("record-data",)
    assert laboratory.record_is_visible() is True
    assert laboratory.record_entry_is_durable() is False
    assert laboratory.initialize().refusal is FirstUseRefusal.ALREADY_INITIALIZED


def test_a_process_restart_and_a_power_loss_are_different_events():
    """The distinction that hid the finding, asserted rather than described."""
    restarted = Laboratory()
    restarted.initialize(fail_at="record-entry")
    restarted.fs.restart_process()
    assert restarted.record_is_visible() is True

    lost = Laboratory()
    lost.initialize(fail_at="record-entry")
    lost.fs.crash()
    assert lost.record_is_visible() is False


def test_the_revision_3_protocol_admits_on_a_record_a_power_loss_removes():
    """**The negative control.** Revision 3's successor must fail this property.

    It reads the visible record, validates it, and proceeds. A power loss then
    removes the record, and the host is left used, historyless and — because a
    used host is never reinitialized as first use — permanently unadmitting.
    """
    laboratory = Laboratory()
    laboratory.initialize(fail_at="record-entry")
    laboratory.fs.restart_process()

    admission = laboratory.admit(
        participant=Participant.BOT_SUITE,
        policy=AdmissionPolicy.R3_TRUSTS_THE_VISIBLE_RECORD,
    )

    assert admission.may_proceed is True
    assert admission.resealed is False

    laboratory.fs.crash()
    assert laboratory.record_is_visible() is False
    after = laboratory.admit(
        participant=Participant.BOT_SUITE,
        policy=AdmissionPolicy.R3_TRUSTS_THE_VISIBLE_RECORD,
    )
    assert after.may_proceed is False
    assert after.parsed.refusal is RecordRefusal.ABSENT


def test_a_successor_establishes_the_durability_the_writer_could_not():
    """Revision 4's correction, and the property revision 3 fails above."""
    laboratory = Laboratory()
    laboratory.initialize(fail_at="record-entry")
    laboratory.fs.restart_process()

    admission = laboratory.admit(participant=Participant.BOT_SUITE)

    assert admission.resealed is True
    assert admission.may_proceed is True
    assert laboratory.record_entry_is_durable() is True

    laboratory.fs.crash()
    assert laboratory.record_is_visible() is True
    assert laboratory.admit(participant=Participant.BOT_SUITE).may_proceed is True


def test_a_failed_re_seal_refuses_pending_an_attributable_recovery():
    """If the successor cannot establish durability it takes nothing."""
    laboratory = Laboratory()
    laboratory.initialize(fail_at="record-entry")
    laboratory.fs.restart_process()
    laboratory.record.reseal_fails = True

    admission = laboratory.admit(participant=Participant.WEB_SUITE)

    assert admission.may_proceed is False
    assert admission.resealed is False
    assert any("did not return success" in reason for reason in admission.refusals)
    assert any(
        "attributable operator recovery" in reason for reason in admission.refusals
    )


def test_the_re_seal_needs_no_write_permission_and_says_so():
    """The permission implication R3-1 asked to be resolved, not assumed."""
    joined = " ".join(RESEAL_CONTRACT)

    assert "No write permission" in joined
    assert "idempotent" in joined
    assert "parent entry" in joined
    assert "TRUNCATED" in joined


def test_the_record_carries_no_durability_claim_a_reader_could_believe():
    """An existing name and a stored boolean are both refused as proof."""
    joined = " ".join(PUBLICATION_UNCERTAINTY)

    assert "does not prove the" in joined
    assert "neither does a boolean stored inside the record" in joined
    laboratory = Laboratory()
    laboratory.initialize()
    stored = laboratory.record.read_record_bytes().decode("utf-8")
    assert "durable" not in stored


def test_a_concurrent_participant_arriving_during_initialization_waits():
    """Wait or refuse, never proceed, and never re-seal somebody else's record."""
    laboratory = Laboratory()

    admission = laboratory.admit(
        participant=Participant.SYNCHRONIZATION,
        lock=LockView(held_by="the operator initializing the host"),
    )

    assert admission.may_proceed is False
    assert admission.resealed is False
    assert any("wait or refuse" in reason for reason in admission.refusals)


def test_a_successful_durable_initialization_admits_every_participant():
    """The successful control, reading the bytes the initializer wrote."""
    laboratory = Laboratory()
    assert laboratory.initialize().initialized is True

    for participant in PARTICIPANTS:
        admission = laboratory.admit(participant=participant)
        assert admission.may_proceed is True, participant
        assert admission.parsed.ok is True
        assert admission.history.disposition is (
            PredecessorDisposition.VERIFIED_FIRST_USE
        )
        assert admission.history.first_use_attested_by == ATTESTER


@pytest.mark.parametrize("stage", ("record-data", "rename", "record-entry"))
def test_every_publication_point_carries_the_same_uncertainty(stage):
    """ADMITTED, RUNNING, release and recovery publish the same way.

    So the same window exists at each, and the same re-seal closes it. The test
    walks a reservation to RUNNING, injects the failure at one of the three
    points of the **release** publication, restarts the process and asserts that
    the successor's re-seal makes whatever is visible survive a power loss.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.append(
        EntryKind.ADMITTED, author="executor RES-1", at="t1", reservation="RES-1"
    )
    laboratory.append(
        EntryKind.RUNNING, author="executor RES-1", at="t2", reservation="RES-1"
    )

    outcome = laboratory.append(
        EntryKind.RELEASED,
        author="executor RES-1",
        at="t3",
        reservation="RES-1",
        released_at="t3",
        fail_at=stage,
    )
    assert outcome.published is False
    assert outcome.refusal is PublicationRefusal.NOT_DURABLE

    laboratory.fs.restart_process()
    admission = laboratory.admit(participant=Participant.BOT_SUITE)
    assert admission.resealed is True

    visible_before = laboratory.record.read_record_bytes()
    laboratory.fs.crash()
    assert laboratory.record.read_record_bytes() == visible_before


def test_a_release_that_never_reached_its_barrier_still_refuses_a_successor():
    """The RUNNING entry stands, so the successor refuses and names the run."""
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.append(
        EntryKind.ADMITTED, author="executor RES-1", at="t1", reservation="RES-1"
    )
    laboratory.append(
        EntryKind.RUNNING, author="executor RES-1", at="t2", reservation="RES-1"
    )
    laboratory.append(
        EntryKind.RELEASED,
        author="executor RES-1",
        at="t3",
        reservation="RES-1",
        released_at="t3",
        fail_at="rename",
    )
    laboratory.fs.restart_process()

    admission = laboratory.admit(participant=Participant.DEPENDENCY_UPDATE)

    assert admission.may_proceed is False
    assert admission.history.disposition is PredecessorDisposition.ACTIVE
    assert admission.history.predecessor_state is ReservationState.RUNNING
    assert any("still active on this host" in reason for reason in admission.refusals)


def test_recovery_never_overwrites_a_valid_prior_history():
    """Every appended entry preserves every earlier one, byte for byte."""
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.append(
        EntryKind.ADMITTED, author="executor RES-1", at="t1", reservation="RES-1"
    )
    laboratory.append(
        EntryKind.QUARANTINED,
        author="executor RES-1",
        at="t2",
        reservation="RES-1",
        reason="a capture failed and residue remains",
    )
    before = parse_history(
        laboratory.record.read_record_bytes(),
        permitted_kinds=RESERVATION_KINDS,
        host=HOST,
        target_identity=TARGET,
    )

    laboratory.append(
        EntryKind.OPERATOR_RECOVERED,
        author=ATTESTER,
        at="t3",
        recovers="RES-1",
        reference="ops-recovery-2026-09-11-01",
    )
    after = parse_history(
        laboratory.record.read_record_bytes(),
        permitted_kinds=RESERVATION_KINDS,
        host=HOST,
        target_identity=TARGET,
    )

    assert after.entries[: len(before.entries)] == before.entries
    assert after.entries[-1].kind is EntryKind.OPERATOR_RECOVERED
    quarantine = [e for e in after.entries if e.kind is EntryKind.QUARANTINED]
    assert quarantine and quarantine[0].get("reason")


def test_an_unreadable_history_is_never_replaced_by_a_recovery():
    """A recovery that cannot read the history has nothing to append to."""
    laboratory = Laboratory()
    laboratory.initialize()
    _corrupt(laboratory, lambda text: text.replace(HISTORY_TERMINATOR, ""))

    outcome = laboratory.append(
        EntryKind.OPERATOR_RECOVERED,
        author=ATTESTER,
        at="t3",
        recovers="RES-1",
        reference="ops-recovery-2026-09-11-01",
    )

    assert outcome.published is False
    assert outcome.refusal is PublicationRefusal.UNREADABLE_PREDECESSOR
    assert any("overwrite recovery must never perform" in r for r in outcome.reasons)


def test_a_partial_history_refuses_rather_than_selecting_an_earlier_entry():
    """A truncated tail is refused, not read as the shorter history it spells.

    The history ends on an admitting `released` entry, then on a refusing
    `admitted` one. Dropping the last entry would leave a record that admits, so
    a reader that accepted a truncated file would be selecting the convenient
    prefix. It refuses instead.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    for reservation, kinds in (
        ("RES-1", (EntryKind.ADMITTED, EntryKind.RUNNING)),
        ("RES-1", (EntryKind.RELEASED,)),
        ("RES-2", (EntryKind.ADMITTED,)),
    ):
        for kind in kinds:
            extra = {"reservation": reservation}
            if kind is EntryKind.RELEASED:
                extra["released_at"] = "t9"
            laboratory.append(kind, author="executor", at="t", **extra)

    assert laboratory.admit().may_proceed is False

    # The prefix this truncation leaves ends on the admitting `released` entry,
    # so a reader that accepted a short history would proceed on it. That is the
    # whole reason the terminator exists, and it is asserted rather than assumed.
    whole = laboratory.record.read_record_bytes().decode("utf-8")
    prefix = whole[: whole.rindex("begin-entry")] + f"{HISTORY_TERMINATOR}\n"
    would_have_admitted = parse_history(
        prefix.encode("utf-8"),
        permitted_kinds=RESERVATION_KINDS,
        host=HOST,
        target_identity=TARGET,
    )
    assert would_have_admitted.ok is True
    assert would_have_admitted.entries[-1].kind is EntryKind.RELEASED

    _corrupt(
        laboratory,
        lambda text: text[: text.rindex("begin-entry")],
    )
    admission = laboratory.admit()

    assert admission.may_proceed is False
    assert admission.parsed.refusal is RecordRefusal.TRUNCATED


def test_the_lifecycle_model_makes_no_oracle_observation():
    """No modelled participant may read what only the test oracle can see.

    `entry_is_durable` and `durable()` report the model's durable-state map,
    which is an observation no real reader can make. A module that consulted one
    would be answering R3-1 with a fact the mechanism does not have, so the
    absence is asserted against the source rather than promised in prose.
    """
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    attributes = {
        node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
    }

    assert "entry_is_durable" not in attributes
    assert "durable" not in attributes


# ---------------------------------------------------------------------------
# R3-2 — every participant's interrupted effects
# ---------------------------------------------------------------------------


def test_every_participant_has_an_identity_writer_lifetime_and_recovery():
    """All seven, and a participant added without a profile fails here."""
    assert set(PARTICIPANT_PROFILES) == set(PARTICIPANTS)
    for participant, profile in PARTICIPANT_PROFILES.items():
        assert profile.participant is participant
        assert profile.identity.strip()
        assert profile.lifecycle_writer.strip()
        assert profile.lock_lifetime.strip()
        assert profile.effects
        assert profile.completion_conditions
        assert profile.recovery
        assert profile.proof_obligations


def test_the_non_reusable_state_is_persisted_before_the_first_effect():
    """`begin` is exclusive and durable, and it is what a successor reads."""
    laboratory = Laboratory()
    laboratory.initialize()

    outcome = laboratory.ledger.begin(
        run_id="web-2026-09-11-01",
        participant=Participant.WEB_SUITE,
        author="ubuntu",
        at="t1",
    )

    assert outcome.published is True
    assert outcome.barriers == ("record-data", "record-entry")
    survey = laboratory.ledger.survey()
    assert survey.unsettled == ("web-2026-09-11-01",)
    assert survey.settled is False


def test_a_clean_wrapper_exit_and_a_free_lock_are_not_completion_evidence():
    """**The negative control R3-2 names in its own words.**"""
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.ledger.begin(
        run_id="sync-1", participant=Participant.SYNCHRONIZATION, author="ubuntu", at="t1"
    )

    outcome = laboratory.ledger.complete(
        run_id="sync-1",
        participant=Participant.SYNCHRONIZATION,
        author="ubuntu",
        at="t2",
        observation=CompletionObservation(
            observed_by="the wrapper", wrapper_exit_status=0, lock_released=True
        ),
    )

    assert outcome.published is False
    assert laboratory.ledger.survey().unsettled == ("sync-1",)
    joined = " ".join(NOT_COMPLETION_EVIDENCE)
    assert "free cooperative lock" in joined
    assert "wrapper's exit status" in joined
    assert "elapsed deadline" in joined


PARTICIPANT_INTERRUPTIONS = (
    (
        "a wrapper that died with a child surviving",
        Participant.BOT_SUITE,
        "the pytest process and every child it spawned have exited",
    ),
    (
        "a wrapper that died with a server-side transaction unsettled",
        Participant.WEB_SUITE,
        "no backend attributable to this run remains on the disposable database",
    ),
    (
        "a partial synchronization",
        Participant.SYNCHRONIZATION,
        "a whole-tree consistency check against the source revision passed after it",
    ),
    (
        "an interrupted dependency update",
        Participant.DEPENDENCY_UPDATE,
        "an environment consistency check over the locked set passed after it",
    ),
    (
        "an interrupted environment reset",
        Participant.ENVIRONMENT_RESET,
        "the post-reset state was observed to match the declared baseline",
    ),
)


@pytest.mark.parametrize(
    "label, participant, unobserved",
    PARTICIPANT_INTERRUPTIONS,
    ids=[row[0] for row in PARTICIPANT_INTERRUPTIONS],
)
def test_an_uncertain_predecessor_blocks_every_successor(
    label, participant, unobserved
):
    """One condition unobserved, and all seven refuse — the harness included."""
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.ledger.begin(
        run_id="run-1", participant=participant, author="ubuntu", at="t1"
    )
    refused = laboratory.ledger.complete(
        run_id="run-1",
        participant=participant,
        author="ubuntu",
        at="t2",
        observation=_observed(participant, unobserved=unobserved),
    )
    assert refused.published is False
    assert any(unobserved in reason for reason in refused.reasons)
    laboratory.fs.restart_process()

    for successor in PARTICIPANTS:
        admission = laboratory.admit(participant=successor)
        assert admission.may_proceed is False, (label, successor)
        assert admission.runs.unsettled == ("run-1",)
        assert any("blocks every successor" in r for r in admission.refusals)


def test_clean_completion_admits_the_next_participant():
    """The successful control, so the ledger is not shown refusing everything."""
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.ledger.begin(
        run_id="foundry-1", participant=Participant.FOUNDRY_TESTS, author="ubuntu", at="t1"
    )

    completed = laboratory.ledger.complete(
        run_id="foundry-1",
        participant=Participant.FOUNDRY_TESTS,
        author="ubuntu",
        at="t2",
        observation=_observed(Participant.FOUNDRY_TESTS),
    )

    assert completed.published is True
    assert laboratory.ledger.survey().settled is True
    for successor in PARTICIPANTS:
        assert laboratory.admit(participant=successor).may_proceed is True


def test_a_verified_recovery_admits_a_new_run_without_a_dead_end():
    """An interruption is not permanent, and recovery is attributable."""
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.ledger.begin(
        run_id="reset-1", participant=Participant.ENVIRONMENT_RESET, author="ubuntu", at="t1"
    )
    laboratory.fs.restart_process()
    assert laboratory.admit(participant=Participant.BOT_SUITE).may_proceed is False

    unattributed = laboratory.ledger.recover(
        run_id="reset-1",
        participant=Participant.ENVIRONMENT_RESET,
        author="",
        at="t2",
        reference="ops-recovery-2026-09-11-02",
    )
    assert unattributed.published is False

    recovered = laboratory.ledger.recover(
        run_id="reset-1",
        participant=Participant.ENVIRONMENT_RESET,
        author=ATTESTER,
        at="t3",
        reference="ops-recovery-2026-09-11-02",
    )

    assert recovered.published is True
    assert laboratory.ledger.survey().recovered == ("reset-1",)
    assert laboratory.admit(participant=Participant.BOT_SUITE).may_proceed is True


def test_a_recovery_preserves_the_interrupted_runs_own_history():
    """The in-progress entry stays. Recovery is appended, never a replacement."""
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.ledger.begin(
        run_id="dep-1", participant=Participant.DEPENDENCY_UPDATE, author="ubuntu", at="t1"
    )
    laboratory.ledger.recover(
        run_id="dep-1",
        participant=Participant.DEPENDENCY_UPDATE,
        author=ATTESTER,
        at="t2",
        reference="ops-recovery-2026-09-11-03",
    )

    parsed = parse_history(
        DurableRecordStore(
            laboratory.fs,
            directory=laboratory.runs_directory,
            name="dep-1",
            label="runs/dep-1",
        ).read_record_bytes(),
        permitted_kinds=PARTICIPANT_KINDS,
        host=HOST,
        target_identity=TARGET,
    )

    assert [entry.kind for entry in parsed.entries] == [
        EntryKind.PARTICIPANT_STARTED,
        EntryKind.PARTICIPANT_RECOVERED,
    ]
    assert parsed.entries[0].get("effects")
    assert parsed.entries[-1].author == ATTESTER


def test_a_recovered_runs_own_identity_is_never_reused():
    """Exclusive creation refuses the id, so a recovery cannot be resumed."""
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.ledger.begin(
        run_id="bot-1", participant=Participant.BOT_SUITE, author="ubuntu", at="t1"
    )
    laboratory.ledger.recover(
        run_id="bot-1",
        participant=Participant.BOT_SUITE,
        author=ATTESTER,
        at="t2",
        reference="ops-recovery-2026-09-11-04",
    )

    reused = laboratory.ledger.begin(
        run_id="bot-1", participant=Participant.BOT_SUITE, author="ubuntu", at="t3"
    )

    assert reused.published is False
    assert reused.refusal is PublicationRefusal.ALREADY_PUBLISHED


def test_an_interrupted_ledger_publication_blocks_and_is_not_cleaned():
    """A leftover temporary is a run that may have begun. It is reported."""
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.ledger.begin(
        run_id="web-1",
        participant=Participant.WEB_SUITE,
        author="ubuntu",
        at="t1",
        fail_at="record-data",
    )
    laboratory.fs.restart_process()

    survey = laboratory.ledger.survey()

    assert survey.unreadable == ("web-1.tmp",)
    assert any("not removed" in reason for reason in survey.reasons)
    assert laboratory.admit(participant=Participant.HARNESS_CLI).may_proceed is False


def test_the_environment_reset_refuses_especially_while_a_quarantine_exists():
    """A reset would destroy the residue the quarantine exists to preserve."""
    laboratory = Laboratory()
    laboratory.initialize()

    admission = laboratory.admit(
        participant=Participant.ENVIRONMENT_RESET,
        quarantine=QuarantineRecord(
            host=HOST, reservation_id="RES-0", reason="residue remains"
        ),
    )

    assert admission.may_proceed is False
    assert any("refuses especially" in reason for reason in admission.refusals)


def test_the_proof_obligations_are_named_and_unperformed():
    """R3-2's future target evidence, named rather than assumed away."""
    joined = " ".join(
        obligation
        for profile in PARTICIPANT_PROFILES.values()
        for obligation in profile.proof_obligations
    )

    assert joined.count("nconfirmed") >= 5
    assert "none of which has been performed" in joined


# ---------------------------------------------------------------------------
# R3-3 — stored evidence bound to admission
# ---------------------------------------------------------------------------


def test_a_first_use_history_for_another_target_refuses():
    """**R3-3's reproduction.** Before this pass it admitted seven of seven."""
    laboratory = Laboratory()
    assert laboratory.initialize().initialized is True

    for participant in PARTICIPANTS:
        matching = laboratory.admit(participant=participant, target_identity=TARGET)
        other = laboratory.admit(participant=participant, target_identity=OTHER_TARGET)

        assert matching.may_proceed is True, participant
        assert other.may_proceed is False, participant
        assert other.parsed.refusal is RecordRefusal.WRONG_BINDING


def test_an_initialization_bound_to_the_wrong_target_refuses():
    """`BINDING_MISMATCH` now has an enforcing branch — R3-3 asked for one."""
    laboratory = Laboratory()

    outcome = laboratory.initialize(target_identity=OTHER_TARGET)

    assert outcome.initialized is False
    assert outcome.refusal is FirstUseRefusal.BINDING_MISMATCH
    assert laboratory.record_is_visible() is False
    assert outcome.recovery


@pytest.mark.parametrize(
    "evidence",
    (
        FirstUseEvidence(prior_use_excluded=True, attested_by=ATTESTER),
        FirstUseEvidence(prior_use_excluded=True, basis=BASIS),
    ),
    ids=("no basis", "no attester"),
)
def test_a_first_use_without_a_complete_attestation_refuses(evidence):
    """The attestation travels, so an incomplete one cannot be written at all."""
    laboratory = Laboratory()

    outcome = laboratory.initialize(evidence=evidence)

    assert outcome.initialized is False
    assert outcome.refusal is FirstUseRefusal.NO_FIRST_USE_EVIDENCE


def test_the_attestation_survives_the_trip_from_bytes_to_decision():
    """The author and basis reach the validator, which R3-3 found they did not."""
    laboratory = Laboratory()
    laboratory.initialize()

    admission = laboratory.admit()

    assert admission.history.first_use_attested_by == ATTESTER
    assert admission.history.first_use_basis == BASIS
    assert admission.history.target_identity == TARGET
    assert admission.validation.admits is True


def test_a_release_and_a_recovery_carry_their_author_and_reference():
    """Both admitting dispositions keep their attributable evidence."""
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.append(
        EntryKind.ADMITTED, author="executor RES-1", at="t1", reservation="RES-1"
    )
    laboratory.append(
        EntryKind.RELEASED,
        author="executor RES-1",
        at="t2",
        reservation="RES-1",
        released_at="t2",
    )

    released = laboratory.admit(reservation_id="RES-2")
    assert released.may_proceed is True
    assert released.history.release_record.recorded_by == "executor RES-1"
    assert released.history.release_record.target_identity == TARGET

    laboratory.append(
        EntryKind.ADMITTED, author="executor RES-2", at="t3", reservation="RES-2"
    )
    laboratory.append(
        EntryKind.QUARANTINED,
        author="executor RES-2",
        at="t4",
        reservation="RES-2",
        reason="residue remains",
    )
    laboratory.append(
        EntryKind.OPERATOR_RECOVERED,
        author=ATTESTER,
        at="t5",
        recovers="RES-2",
        reference="ops-recovery-2026-09-11-05",
    )

    recovered = laboratory.admit(reservation_id="RES-3")
    assert recovered.may_proceed is True
    assert recovered.history.recovery_authored_by == ATTESTER
    assert (
        recovered.history.operator_recovery_reference == "ops-recovery-2026-09-11-05"
    )
    assert laboratory.admit(reservation_id="RES-2").may_proceed is False


def test_a_history_round_trips_through_serialization_and_parsing():
    """The bytes a writer produces are the bytes a reader accepts, exactly."""
    entries = (
        RecordEntry(
            sequence=1,
            kind=EntryKind.FIRST_USE,
            host=HOST,
            target=TARGET,
            author=ATTESTER,
            at="t0",
            fields={"basis": BASIS},
        ),
        RecordEntry(
            sequence=2,
            kind=EntryKind.ADMITTED,
            host=HOST,
            target=TARGET,
            author="executor RES-1",
            at="t1",
            fields={"reservation": "RES-1"},
        ),
    )
    raw = serialize_history(entries)

    parsed = parse_history(
        raw, permitted_kinds=RESERVATION_KINDS, host=HOST, target_identity=TARGET
    )

    assert parsed.ok is True
    assert parsed.entries == entries
    assert serialize_history(parsed.entries) == raw
    assert parsed.source_digest


def _corrupt(laboratory: Laboratory, transform) -> None:
    """Rewrite the stored record's bytes in place, as tampering would.

    It goes through the model's own write path, so what a later reader sees is a
    record with different bytes at the same name — which is exactly what a
    tamper, a truncating power loss or a partially written file produces.
    """
    fs = laboratory.fs
    path_fd = fs.open_directory(laboratory.directory, DescriptorMode.O_PATH, "").number
    original = laboratory.record.read_record_bytes().decode("utf-8")
    fs.unlinkat(path_fd, "lifecycle.json")
    fd = fs.create_file(path_fd, "lifecycle.json").number
    fs.write(fd, transform(original).encode("utf-8"))
    fs.fsync(fd)
    fs.fsync(
        fs.open_directory(laboratory.directory, DescriptorMode.O_RDONLY, "").number
    )


TAMPERS = (
    (
        "a different approved target",
        lambda text: text.replace(f"target={TARGET}", f"target={OTHER_TARGET}"),
        RecordRefusal.WRONG_BINDING,
    ),
    (
        "an emptied binding",
        lambda text: text.replace(f"target={TARGET}", "target="),
        RecordRefusal.MISSING_BINDING,
    ),
    (
        "a removed attestation basis",
        lambda text: text.replace(f"basis={BASIS}\n", ""),
        RecordRefusal.MALFORMED,
    ),
    (
        "an added field the schema does not have",
        lambda text: text.replace("end-entry", "durable=true\nend-entry", 1),
        RecordRefusal.MALFORMED,
    ),
    (
        "a truncated tail",
        lambda text: text.replace(f"{HISTORY_TERMINATOR}\n", ""),
        RecordRefusal.TRUNCATED,
    ),
    (
        "an unclosed entry",
        lambda text: text.replace("end-entry\n", "", 1),
        RecordRefusal.TRUNCATED,
    ),
    (
        "a schema version this reader does not implement",
        lambda text: text.replace("schema=2", "schema=99"),
        RecordRefusal.UNSUPPORTED_SCHEMA,
    ),
    (
        "a missing magic line",
        lambda text: text.replace(f"{RECORD_MAGIC}\n", ""),
        RecordRefusal.MALFORMED,
    ),
    (
        "an unrecognised entry kind",
        lambda text: text.replace("kind=first_use", "kind=probably_fine"),
        RecordRefusal.MALFORMED,
    ),
    (
        "a renumbered sequence",
        lambda text: text.replace("sequence=1", "sequence=7"),
        RecordRefusal.HISTORY_ORDER,
    ),
)


@pytest.mark.parametrize(
    "label, transform, expected", TAMPERS, ids=[row[0] for row in TAMPERS]
)
def test_a_tampered_record_refuses_and_is_never_normalized(label, transform, expected):
    """Ten stored-field tampers, and the subsequent reader refuses every one."""
    laboratory = Laboratory()
    laboratory.initialize()
    _corrupt(laboratory, transform)

    admission = laboratory.admit(participant=Participant.BOT_SUITE)

    assert admission.parsed.refusal is expected, label
    assert admission.may_proceed is False
    assert admission.parsed.entries == ()


def test_a_record_naming_two_hosts_is_refused_rather_than_reconciled():
    """One file describing two hosts is contradictory, not a merge problem."""
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.append(
        EntryKind.ADMITTED, author="executor RES-1", at="t1", reservation="RES-1"
    )
    _corrupt(laboratory, lambda text: text.replace(f"host={HOST}", "host=elsewhere", 1))

    admission = laboratory.admit()

    assert admission.parsed.refusal is RecordRefusal.CONTRADICTORY
    assert admission.may_proceed is False


HISTORY_ORDER_CASES = (
    (
        "a second first use",
        (EntryKind.FIRST_USE,),
        "claims a verified first use and is not the first entry",
    ),
    (
        "a running entry for a reservation never admitted",
        (EntryKind.RUNNING,),
        "which this history never admitted",
    ),
    (
        "a recovery of a reservation never quarantined",
        (EntryKind.OPERATOR_RECOVERED,),
        "appended to the applicable quarantined predecessor",
    ),
    (
        "a release of a reservation never admitted",
        (EntryKind.RELEASED,),
        "which this history never admitted",
    ),
    (
        "a second admission while the first reservation is running",
        (EntryKind.ADMITTED, EntryKind.RUNNING, EntryKind.ADMITTED),
        "while the current reservation 'RES-9' is 'running'",
    ),
)


@pytest.mark.parametrize(
    "label, kinds, expected",
    HISTORY_ORDER_CASES,
    ids=[row[0] for row in HISTORY_ORDER_CASES],
)
def test_a_history_that_is_not_one_produces_no_decision_input(label, kinds, expected):
    """The order rules refuse before a disposition is derived from the tail."""
    entries = [
        RecordEntry(
            sequence=1,
            kind=EntryKind.FIRST_USE,
            host=HOST,
            target=TARGET,
            author=ATTESTER,
            at="t0",
            fields={"basis": BASIS},
        )
    ]
    for offset, kind in enumerate(kinds, start=2):
        fields = {name: "RES-9" for name in KIND_FIELDS[kind]}
        if kind is EntryKind.FIRST_USE:
            fields = {"basis": BASIS}
        entries.append(
            RecordEntry(
                sequence=offset,
                kind=kind,
                host=HOST,
                target=TARGET,
                author="executor",
                at=f"t{offset}",
                fields=fields,
            )
        )

    problems = check_history_semantics(entries)
    derived = derive_lifecycle_history(
        parse_history(
            serialize_history(entries),
            permitted_kinds=RESERVATION_KINDS,
            host=HOST,
            target_identity=TARGET,
        ),
        host=HOST,
        read_by="a successor",
        read_at="t",
    )

    assert any(expected in problem for problem in problems), label
    assert derived.complete is False


def test_the_order_rules_are_stated_and_bounded():
    """Stated for this protocol, and not a generic event-storage system."""
    joined = " ".join(HISTORY_ORDER_RULES)

    assert "The **current reservation and its current state** are the decision input" in joined
    assert "never selects an earlier, more convenient admitting one" in joined
    assert "`reservation.TRANSITIONS`" in joined
    assert "PR-20260911-R4-1" in joined
    # The transition table is the reservation module's, not a second one here.
    assert TERMINAL_STATES == frozenset(
        {ReservationState.RELEASED, ReservationState.QUARANTINED}
    )
    assert set(ENTRY_STATES) | {EntryKind.FIRST_USE, EntryKind.OPERATOR_RECOVERED} == set(
        RESERVATION_KINDS
    )
    assert SUPPORTED_SCHEMA_VERSIONS == frozenset({2})
    assert set(KIND_FIELDS) == set(EntryKind)


# ---------------------------------------------------------------------------
# The two complete lifecycle traces
# ---------------------------------------------------------------------------


def test_a_complete_successful_lifecycle_admits_a_successor_from_stored_evidence():
    """Initialization, admission, operation, completion, release, reuse.

    Every step reads the bytes the previous one wrote. Nothing is constructed
    beside the store, and the successor's admission rests on the predecessor's
    stored release rather than on a history this test built.
    """
    laboratory = Laboratory()
    assert laboratory.initialize().initialized is True

    first = laboratory.admit(reservation_id="RES-1")
    assert first.may_proceed is True
    assert first.history.disposition is PredecessorDisposition.VERIFIED_FIRST_USE

    assert laboratory.append(
        EntryKind.ADMITTED, author="executor RES-1", at="t1", reservation="RES-1"
    ).published is True
    assert laboratory.begin_harness("RES-1-harness", "RES-1").published is True
    assert laboratory.append(
        EntryKind.RUNNING, author="executor RES-1", at="t2", reservation="RES-1"
    ).published is True

    # The two terminal publications, in the order R4-3 requires: the release
    # decision, then the durable RELEASED entry, then the harness's completion —
    # whose conditions are derived from the first two rather than injected.
    concluded = laboratory.conclude("RES-1", "RES-1-harness")

    assert concluded.decision is ReservationState.RELEASED
    assert concluded.release_entry.published is True
    assert concluded.completion.published is True
    assert concluded.concluded is True
    assert concluded.refusals == ()

    laboratory.fs.restart_process()
    successor = laboratory.admit(
        participant=Participant.WEB_SUITE, reservation_id="RES-2"
    )

    assert successor.may_proceed is True
    assert successor.resealed is True
    assert successor.history.disposition is PredecessorDisposition.RELEASED
    assert successor.history.predecessor_id == "RES-1"
    assert successor.history.release_record.recorded_by == "executor RES-1"
    assert successor.runs.settled is True
    assert [entry.kind for entry in successor.parsed.entries] == [
        EntryKind.FIRST_USE,
        EntryKind.ADMITTED,
        EntryKind.RUNNING,
        EntryKind.RELEASED,
    ]


def test_a_complete_failed_lifecycle_refuses_then_recovers_then_admits():
    """Interruption, restart, refusal, attributable recovery, reuse.

    The same path as the successful trace, through a crash. Nothing takes the
    host because time passed, a lock was free or a process died, and the
    recovery that eventually admits is somebody's appended, attributed entry.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.append(
        EntryKind.ADMITTED, author="executor RES-1", at="t1", reservation="RES-1"
    )
    laboratory.begin_harness("RES-1-harness", "RES-1")
    laboratory.append(
        EntryKind.RUNNING, author="executor RES-1", at="t2", reservation="RES-1"
    )

    # The executor dies here. Its memory goes; the filesystem does not.
    laboratory.fs.restart_process()

    blocked = laboratory.admit(participant=Participant.BOT_SUITE, reservation_id="RES-2")
    assert blocked.may_proceed is False
    assert blocked.history.disposition is PredecessorDisposition.ACTIVE
    assert blocked.runs.unsettled == ("RES-1-harness",)

    laboratory.append(
        EntryKind.QUARANTINED,
        author=ATTESTER,
        at="t3",
        reservation="RES-1",
        reason="the executor stopped between RUNNING and any release",
    )
    assert laboratory.admit(reservation_id="RES-2").may_proceed is False

    laboratory.ledger.recover(
        run_id="RES-1-harness",
        participant=Participant.HARNESS_CLI,
        author=ATTESTER,
        at="t4",
        reference="ops-recovery-2026-09-11-06",
    )
    laboratory.append(
        EntryKind.OPERATOR_RECOVERED,
        author=ATTESTER,
        at="t5",
        recovers="RES-1",
        reference="ops-recovery-2026-09-11-06",
    )

    admitted = laboratory.admit(
        participant=Participant.SYNCHRONIZATION, reservation_id="RES-2"
    )
    assert admitted.may_proceed is True
    assert admitted.history.disposition is PredecessorDisposition.OPERATOR_RECOVERED
    assert admitted.history.recovery_authored_by == ATTESTER

    # The recovered reservation itself is never resumed.
    assert laboratory.admit(reservation_id="RES-1").may_proceed is False
    kinds = [entry.kind for entry in admitted.parsed.entries]
    assert EntryKind.QUARANTINED in kinds
