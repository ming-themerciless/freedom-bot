"""Bounded proposal models for the September 11 re-review — R2-2, R2-3 and R2-4.

**Every test in this file is a model test.** It exercises
`tools/phase_5_0_evidence/durability_model.py` and
`tools/phase_5_0_evidence/lifecycle_storage.py`, which are deterministic
in-memory arrangements of rules proposed in runner contract **revision 3**. The
mechanism those rules describe is **not built**: there is no privileged
mechanism, no filesystem writer, no lock adapter and no operational integration,
and nothing here creates one.

So a passing row here establishes exactly one thing — that the proposed rule is
constructible and falsifiable, and that a deliberately defective arrangement is
classified as failing rather than passing. It establishes **nothing** about
Linux runtime behaviour, about `oracle-test`, or about EH-R16-1, and it closes no
finding. `durability_model.IMPLEMENTATION_CHECKS_NOT_PERFORMED` names the checks
that would establish the real property, and none of them has been performed.

Three negative controls carry the weight, and without them the rest would prove
nothing:

* `test_the_revision_2_sequence_fails_the_corrected_property` — the omitted
  recovery-parent barrier must **fail**;
* `test_the_post_check_cannot_tell_the_two_removals_apart` — the post-check must
  be shown **unable** to detect the substitution; and
* `test_fsync_on_an_o_path_descriptor_is_refused` — the invalid operation
  revision 2 specified must **refuse**.
"""
from __future__ import annotations

import pytest

from tools.phase_5_0_evidence.durability_model import (
    IMPLEMENTATION_CHECKS_NOT_PERFORMED,
    MODEL_LIMITS,
    NOT_A_BARRIER,
    OMITTED_R2_BARRIER,
    O_PATH_PERMITTED_OPERATIONS,
    O_PATH_REFUSED_OPERATIONS,
    PUBLICATION_BARRIERS,
    REMOVAL_EVIDENCE_CLAIMS,
    RESTORATION_BARRIERS,
    BarrierPolicy,
    DescriptorMode,
    ModelRefused,
    Quiescence,
    RecoveryPublisher,
    RecoveryRecord,
    RemovalObservation,
    RemovalRefusal,
    Substitution,
    SyntheticFilesystem,
    digest,
    discover_recovery,
    remove_by_name,
    restore_configuration,
)
from tools.phase_5_0_evidence.lifecycle_storage import (
    ADMITTING_OUTCOMES,
    FREE_LOCK_AUTHORIZES_NOTHING,
    UNIT_TEST_CONSTRUCTORS,
    DurableRecordStore,
    PARTICIPANTS,
    PROPOSED_PROVISIONING,
    RECORD_ATTRIBUTION,
    RESERVATION_KINDS,
    FirstUseEvidence,
    FirstUseRefusal,
    Participant,
    crash_between_admitted_and_running,
    environment_reset_history,
    initialize_first_use_record,
    participant_may_proceed,
    survey,
)
from tools.phase_5_0_evidence.reservation import (
    LifecycleHistory,
    LockView,
    PredecessorDisposition,
    QuarantineRecord,
    ReleaseRecord,
    ReservationState,
)

HOST = "oracle-test"
RUN_ID = "run-2026-09-11-01"
ORIGINAL_CONFIG = b"local all postgres peer\n"
REVIEWED_CONFIG = b"local all disposable peer map=reviewed\n"


# ---------------------------------------------------------------------------
# A provisioned host, durably
# ---------------------------------------------------------------------------


class Laboratory:
    """A synthetic host with the two provisioned roots the design needs.

    Both are created and then made durable, because both are **provisioned** —
    they exist before any run and survive a reboot. Nothing a run creates is made
    durable here; that is what the sequences under test are for.
    """

    def __init__(self) -> None:
        self.fs = SyntheticFilesystem()
        root = self.fs.open_directory(self.fs.root, DescriptorMode.O_PATH, "").number
        root_sync = self.fs.open_directory(
            self.fs.root, DescriptorMode.O_RDONLY, ""
        ).number

        self.recovery_parent = self.fs.mkdirat(root, "recovery")
        self.config_directory = self.fs.mkdirat(root, "pgconf")
        self.fs.fsync(root_sync)

        self.config_path_fd = self.fs.open_directory(
            self.config_directory, DescriptorMode.O_PATH, "/etc/postgresql/16/main"
        ).number
        self.config_sync_fd = self.fs.open_directory(
            self.config_directory, DescriptorMode.O_RDONLY, "/etc/postgresql/16/main"
        ).number

        config_fd = self.fs.create_file(
            self.config_path_fd, "pg_hba.conf", ORIGINAL_CONFIG
        ).number
        self.fs.fsync(config_fd)
        self.fs.fsync(self.config_sync_fd)

    # -- the modelled first configuration mutation, M1 ----------------------

    def apply_m1(self) -> None:
        """Replace the configuration. Only ever called when permitted."""
        temporary_fd = self.fs.create_file(
            self.config_path_fd, "pg_hba.conf.tmp"
        ).number
        self.fs.write(temporary_fd, REVIEWED_CONFIG)
        self.fs.fsync(temporary_fd)
        self.fs.renameat(
            self.config_path_fd, "pg_hba.conf.tmp", self.config_path_fd, "pg_hba.conf"
        )
        self.fs.fsync(self.config_sync_fd)

    def configuration_now(self) -> bytes:
        state = self.fs.now()
        object_id = state.resolve(self.config_directory, "pg_hba.conf")
        return dict(state.data).get(object_id or "", b"")

    def source_fd(self) -> int:
        return self.fs.openat(
            self.config_path_fd, "pg_hba.conf", DescriptorMode.O_RDONLY
        ).number


def _publish(
    laboratory: Laboratory,
    *,
    policy: BarrierPolicy = BarrierPolicy.R3_COMPLETE,
    fail_at: str = "",
    run_id: str = RUN_ID,
):
    publisher = RecoveryPublisher(
        laboratory.fs,
        recovery_parent=laboratory.recovery_parent,
        policy=policy,
        fail_at=fail_at,
    )
    return publisher.publish(
        run_id=run_id,
        source_fd=laboratory.source_fd(),
        source_identity="dev=8:1 ino=4711",
        destination="/etc/postgresql/16/main/pg_hba.conf",
    )


# ---------------------------------------------------------------------------
# R2-2 — descriptor modes, and the operation revision 2 could not perform
# ---------------------------------------------------------------------------


def test_fsync_on_an_o_path_descriptor_is_refused():
    """The invalid-operation control. Revision 2 required exactly this call.

    `bin_fd` and `pgconf_fd` were both defined `O_PATH`, and P2 then required
    `fsync(bin_fd)` while restoration required `fsync(pgconf_fd)`. Neither is an
    operation `open(2)` permits on an `O_PATH` descriptor.
    """
    laboratory = Laboratory()
    o_path = laboratory.config_path_fd

    with pytest.raises(ModelRefused) as refusal:
        laboratory.fs.fsync(o_path)

    assert "EBADF" in str(refusal.value)
    assert "PR-20260911-R2-2" in str(refusal.value)


def test_a_separate_o_rdonly_descriptor_is_the_synchronizable_one():
    """The corrected design's answer, and the two descriptors are distinct."""
    laboratory = Laboratory()

    traversal = laboratory.fs.describe(laboratory.config_path_fd)
    synchronizable = laboratory.fs.describe(laboratory.config_sync_fd)

    assert traversal.mode is DescriptorMode.O_PATH
    assert synchronizable.mode is DescriptorMode.O_RDONLY
    assert traversal.object_id == synchronizable.object_id
    laboratory.fs.fsync(laboratory.config_sync_fd)


def test_the_o_path_operation_lists_separate_what_is_permitted_from_what_is_not():
    assert "fsync" in O_PATH_REFUSED_OPERATIONS
    assert "fsync" not in O_PATH_PERMITTED_OPERATIONS
    assert any("dirfd" in operation for operation in O_PATH_PERMITTED_OPERATIONS)


def test_a_synchronizable_descriptor_is_bound_by_comparison_not_by_pathname():
    """R2-2's other requirement: no unchecked lookup is reintroduced.

    The second open resolves one component relative to the held O_PATH parent and
    the result is compared with the identity the chain recorded. A substitution
    between the two opens is therefore refused rather than synchronized.
    """
    laboratory = Laboratory()
    publisher = RecoveryPublisher(
        laboratory.fs, recovery_parent=laboratory.recovery_parent
    )
    parent_path_fd = laboratory.fs.open_directory(
        laboratory.recovery_parent, DescriptorMode.O_PATH, "recovery"
    ).number
    created = laboratory.fs.mkdirat(parent_path_fd, "decoy")

    laboratory.fs.renameat(parent_path_fd, "decoy", parent_path_fd, "moved-away")
    laboratory.fs.mkdirat(parent_path_fd, "decoy")

    with pytest.raises(ModelRefused) as refusal:
        publisher._sync_descriptor(parent_path_fd, "decoy", created)

    assert "not bound to the intended directory" in str(refusal.value)


# ---------------------------------------------------------------------------
# R2-2 — the barrier graph, injected at every barrier
# ---------------------------------------------------------------------------


def test_the_positive_sequence_crosses_every_barrier_and_permits_the_mutation():
    laboratory = Laboratory()

    outcome = _publish(laboratory)

    assert outcome.published is True
    assert outcome.mutation_permitted is True
    assert outcome.refusals == ()
    assert set(outcome.barriers_crossed) == {
        barrier.name for barrier in PUBLICATION_BARRIERS
    }
    assert outcome.barriers_crossed[0] == OMITTED_R2_BARRIER
    assert outcome.limits == MODEL_LIMITS


@pytest.mark.parametrize(
    "barrier", [barrier.name for barrier in PUBLICATION_BARRIERS]
)
def test_failure_at_any_barrier_prevents_the_first_configuration_mutation(barrier):
    """R2-2's governing rule, injected one barrier at a time."""
    laboratory = Laboratory()

    outcome = _publish(laboratory, fail_at=barrier)

    assert outcome.published is False
    assert outcome.mutation_permitted is False
    assert barrier not in outcome.barriers_crossed
    assert any("injected failure at barrier" in reason for reason in outcome.refusals)

    if outcome.mutation_permitted:  # pragma: no cover - the guard under test
        laboratory.apply_m1()
    assert laboratory.configuration_now() == ORIGINAL_CONFIG


@pytest.mark.parametrize("stage", ("create-run-directory", "capture-read"))
def test_failure_before_any_barrier_prevents_the_mutation_too(stage):
    laboratory = Laboratory()

    outcome = _publish(laboratory, fail_at=stage)

    assert outcome.mutation_permitted is False
    assert laboratory.configuration_now() == ORIGINAL_CONFIG


def test_every_declared_barrier_names_what_it_makes_durable_and_why():
    for barrier in PUBLICATION_BARRIERS + RESTORATION_BARRIERS:
        assert barrier.kind in {"data", "entry"}
        assert barrier.subject.strip()
        assert len(barrier.why) > 40


def test_a_read_back_and_a_rename_are_stated_not_to_be_barriers():
    joined = " ".join(NOT_A_BARRIER)

    assert "read-back" in joined or "read-back of the stored copy" in joined
    assert "rename" in joined
    assert "digest" in joined


# ---------------------------------------------------------------------------
# R2-2 — the crash property, and the sequence that must fail it
# ---------------------------------------------------------------------------


def test_a_crash_after_a_successful_publication_leaves_a_usable_recovery_basis():
    """The property the corrected barrier graph exists to provide."""
    laboratory = Laboratory()
    outcome = _publish(laboratory)
    assert outcome.mutation_permitted is True

    laboratory.fs.crash()
    discovery = discover_recovery(
        laboratory.fs, recovery_parent=laboratory.recovery_parent, run_id=RUN_ID
    )

    assert discovery.discoverable is True
    assert discovery.record_present is True
    assert discovery.copy_present is True
    assert discovery.verifiable is True
    assert discovery.usable is True
    assert RUN_ID in discovery.listing


def test_the_revision_2_sequence_fails_the_corrected_property():
    """**The negative control.** The omitted parent barrier must fail this.

    Revision 2 synchronized the copy, the record and the run directory, and never
    synchronized the recovery parent. Its own contents are therefore durable and
    its **entry** is not, so restart discovery by listing the recovery parent
    does not find the advertised recovery basis.
    """
    laboratory = Laboratory()
    outcome = _publish(laboratory, policy=BarrierPolicy.R2_OMITTED_PARENT)

    assert outcome.published is False
    assert outcome.mutation_permitted is False
    assert OMITTED_R2_BARRIER not in outcome.barriers_crossed
    assert any(OMITTED_R2_BARRIER in reason for reason in outcome.refusals)

    laboratory.fs.crash()
    discovery = discover_recovery(
        laboratory.fs, recovery_parent=laboratory.recovery_parent, run_id=RUN_ID
    )

    assert discovery.discoverable is False
    assert discovery.usable is False
    assert RUN_ID not in discovery.listing


def test_syncing_the_childs_contents_is_not_the_parents_entry_barrier():
    """Stated as a difference between two observations, not as a claim."""
    laboratory = Laboratory()
    _publish(laboratory, policy=BarrierPolicy.R2_OMITTED_PARENT)

    before = laboratory.fs.now()
    run_object = before.resolve(laboratory.recovery_parent, RUN_ID)
    assert run_object is not None
    assert before.resolve(run_object, "copy") is not None

    laboratory.fs.crash()
    after = laboratory.fs.now()
    assert after.resolve(laboratory.recovery_parent, RUN_ID) is None


# ---------------------------------------------------------------------------
# R2-2 — restoration, and the rename that is not a durable restoration
# ---------------------------------------------------------------------------


def test_a_complete_restoration_is_durable_and_says_so():
    laboratory = Laboratory()
    _publish(laboratory)
    laboratory.apply_m1()
    assert laboratory.configuration_now() == REVIEWED_CONFIG

    outcome = restore_configuration(
        laboratory.fs,
        config_path_fd=laboratory.config_path_fd,
        config_sync_fd=laboratory.config_sync_fd,
        destinations=(("pg_hba.conf", ORIGINAL_CONFIG),),
    )

    assert outcome.renamed is True
    assert outcome.durable is True
    assert "restore-entry" in outcome.barriers_crossed
    assert laboratory.configuration_now() == ORIGINAL_CONFIG


def test_a_rename_without_its_directory_barrier_is_not_a_durable_restoration():
    """Failure after a restoration rename and before its directory sync."""
    laboratory = Laboratory()
    _publish(laboratory)
    laboratory.apply_m1()

    outcome = restore_configuration(
        laboratory.fs,
        config_path_fd=laboratory.config_path_fd,
        config_sync_fd=laboratory.config_sync_fd,
        destinations=(("pg_hba.conf", ORIGINAL_CONFIG),),
        fail_at="restore-entry",
    )

    assert outcome.renamed is True
    assert outcome.durable is False
    assert laboratory.configuration_now() == ORIGINAL_CONFIG

    laboratory.fs.crash()
    assert laboratory.configuration_now() == REVIEWED_CONFIG


def test_a_restoration_interrupted_before_its_rename_leaves_the_destination_alone():
    laboratory = Laboratory()
    _publish(laboratory)
    laboratory.apply_m1()

    outcome = restore_configuration(
        laboratory.fs,
        config_path_fd=laboratory.config_path_fd,
        config_sync_fd=laboratory.config_sync_fd,
        destinations=(("pg_hba.conf", ORIGINAL_CONFIG),),
        fail_at="restore-data",
    )

    assert outcome.renamed is False
    assert outcome.durable is False
    assert laboratory.configuration_now() == REVIEWED_CONFIG


def test_a_multi_file_restoration_interrupted_between_renames_is_mixed():
    """Which is why the post-reload verification is a separate observation."""
    laboratory = Laboratory()
    second_fd = laboratory.fs.create_file(
        laboratory.config_path_fd, "pg_ident.conf", b"original ident\n"
    ).number
    laboratory.fs.fsync(second_fd)
    laboratory.fs.fsync(laboratory.config_sync_fd)

    outcome = restore_configuration(
        laboratory.fs,
        config_path_fd=laboratory.config_path_fd,
        config_sync_fd=laboratory.config_sync_fd,
        destinations=(
            ("pg_hba.conf", b"restored hba\n"),
            ("pg_ident.conf", b"restored ident\n"),
        ),
        fail_at="between-renames:0",
    )

    assert outcome.renamed is True
    assert outcome.durable is False
    assert outcome.reload_verified is False
    state = laboratory.fs.now()
    hba = state.resolve(laboratory.config_directory, "pg_hba.conf")
    ident = state.resolve(laboratory.config_directory, "pg_ident.conf")
    assert dict(state.data)[hba] == b"restored hba\n"
    assert dict(state.data)[ident] == b"original ident\n"


def test_a_record_naming_another_destination_restores_nowhere():
    """A matching digest is not sufficient: the destination is part of the binding."""
    laboratory = Laboratory()
    _publish(laboratory)
    laboratory.fs.crash()

    state = laboratory.fs.now()
    run_object = state.resolve(laboratory.recovery_parent, RUN_ID)
    record = RecoveryRecord.decoded(
        dict(state.data)[state.resolve(run_object, "record")]
    )
    copy_bytes = dict(state.data)[state.resolve(run_object, "copy")]

    assert record.destination == "/etc/postgresql/16/main/pg_hba.conf"
    assert digest(copy_bytes) == record.content_digest

    elsewhere = RecoveryRecord(
        run_id=record.run_id,
        destination="/etc/postgresql/16/main/pg_ident.conf",
        source_identity=record.source_identity,
        content_digest=record.content_digest,
        byte_length=record.byte_length,
        captured_by=record.captured_by,
    )
    assert elsewhere.content_digest == record.content_digest
    assert elsewhere.destination != record.destination


def test_a_malformed_recovery_record_is_refused_rather_than_guessed():
    with pytest.raises(ModelRefused):
        RecoveryRecord.decoded(b"not|a|record")


def test_the_implementation_checks_are_listed_separately_and_unperformed():
    joined = " ".join(IMPLEMENTATION_CHECKS_NOT_PERFORMED).lower()

    assert "none is performed here" in joined
    assert "rename_noreplace" in joined
    assert any("proposal-model" in limit for limit in MODEL_LIMITS)


# ---------------------------------------------------------------------------
# R2-3 — what the post-unlink check can and cannot establish
# ---------------------------------------------------------------------------


def _removal_laboratory() -> tuple[Laboratory, int, str]:
    """A parent directory holding one object **A** at the name to be removed."""
    laboratory = Laboratory()
    parent_fd = laboratory.fs.open_directory(
        laboratory.config_directory, DescriptorMode.O_PATH, "R/journal"
    ).number
    original = laboratory.fs.create_file(parent_fd, "subject", b"A").object_id
    return laboratory, parent_fd, original


def test_the_intended_removal_succeeds_under_the_declared_exclusion_premise():
    """The positive control: verified quiescence, no substitution, A removed."""
    laboratory, parent_fd, original = _removal_laboratory()

    observation = remove_by_name(
        laboratory.fs,
        parent_fd=parent_fd,
        name="subject",
        expected_identity=original,
        quiescence=Quiescence.verified(observed_by="executor, between cases"),
    )

    assert isinstance(observation, RemovalObservation)
    assert observation.removal_issued is True
    assert observation.pre_check_identity == original
    assert observation.post_check_absent is True
    assert laboratory.fs.now().resolve(laboratory.config_directory, "subject") is None


def test_the_exact_counterexample_removes_b_and_leaves_a_alive():
    """A renamed away, B installed at the name, unlink takes B.

    A, B and the namespace are tracked separately. The assertions below are the
    **oracle's**: the production observation learns none of them.
    """
    laboratory, parent_fd, original = _removal_laboratory()
    substitution = Substitution(moved_to="subject-moved-away")

    observation = remove_by_name(
        laboratory.fs,
        parent_fd=parent_fd,
        name="subject",
        expected_identity=original,
        quiescence=Quiescence.verified(observed_by="executor, between cases"),
        substitute=substitution,
    )

    state = laboratory.fs.now()
    assert state.resolve(laboratory.config_directory, "subject-moved-away") == original
    assert substitution.installed != original
    assert substitution.installed not in state.entries.values()
    assert isinstance(observation, RemovalObservation)
    assert observation.post_check_absent is True
    assert observation.detected_substitution is False


def test_the_post_check_cannot_tell_the_two_removals_apart():
    """**The negative control for R2-3.** The two observations are identical.

    Revision 2 §1.4.5 step 3 and §9 row 3 promised the post-check would detect
    the event and report both identities. It reports neither, because ENOENT
    after the substituted removal is the same ENOENT as after the intended one.
    """
    clean_laboratory, clean_parent, clean_original = _removal_laboratory()
    clean = remove_by_name(
        clean_laboratory.fs,
        parent_fd=clean_parent,
        name="subject",
        expected_identity=clean_original,
        quiescence=Quiescence.verified(observed_by="executor"),
    )

    substituted_laboratory, substituted_parent, substituted_original = (
        _removal_laboratory()
    )
    substituted = remove_by_name(
        substituted_laboratory.fs,
        parent_fd=substituted_parent,
        name="subject",
        expected_identity=substituted_original,
        quiescence=Quiescence.verified(observed_by="executor"),
        substitute=Substitution(moved_to="subject-moved-away"),
    )

    assert clean.indistinguishable_from(substituted)
    assert not hasattr(substituted, "removed_identity")


def test_a_substitution_before_the_pre_check_is_genuinely_detected():
    """Prevention and detection stay apart: the pre-check is the real detector."""
    laboratory, parent_fd, original = _removal_laboratory()
    laboratory.fs.renameat(parent_fd, "subject", parent_fd, "moved")
    replacement = laboratory.fs.create_file(parent_fd, "subject").object_id

    observation = remove_by_name(
        laboratory.fs,
        parent_fd=parent_fd,
        name="subject",
        expected_identity=original,
        quiescence=Quiescence.verified(observed_by="executor"),
    )

    assert isinstance(observation, RemovalObservation)
    assert observation.detected_substitution is True
    assert observation.removal_issued is False
    assert observation.pre_check_identity == replacement
    assert laboratory.fs.now().resolve(laboratory.config_directory, "subject") is not None


@pytest.mark.parametrize(
    "quiescence, expected",
    (
        (Quiescence.not_observed(), "was not made"),
        (
            Quiescence(
                observed=True,
                processes_ended=False,
                transactions_settled=True,
                transient_units_inactive=True,
                observed_by="executor",
            ),
            "observed false",
        ),
        (
            Quiescence(
                observed=True,
                processes_ended=True,
                transactions_settled=None,
                transient_units_inactive=True,
                observed_by="executor",
            ),
            "was not observed",
        ),
    ),
)
def test_unobserved_false_or_incomplete_quiescence_refuses_the_effect(
    quiescence, expected
):
    """Prevention is a prerequisite, and failing it refuses rather than detects."""
    laboratory, parent_fd, original = _removal_laboratory()

    outcome = remove_by_name(
        laboratory.fs,
        parent_fd=parent_fd,
        name="subject",
        expected_identity=original,
        quiescence=quiescence,
        residue_paths=("/opt/freedom-blades/evidence/run/journal/subject",),
        dependent_work=("L4 classification", "reservation release"),
    )

    assert isinstance(outcome, RemovalRefusal)
    assert outcome.refused is True
    assert any(expected in reason for reason in outcome.reasons)
    assert outcome.residue == (
        "/opt/freedom-blades/evidence/run/journal/subject",
    )
    assert outcome.dependent_work_refused == (
        "L4 classification",
        "reservation release",
    )
    assert outcome.cleanup_state == "S-B"
    assert outcome.independent_recovery_preserved is True
    assert laboratory.fs.now().resolve(laboratory.config_directory, "subject") is not None


def test_the_removal_evidence_claims_are_stated_and_corrected():
    joined = " ".join(REMOVAL_EVIDENCE_CLAIMS)

    assert "cannot establish which object the removal took" in joined
    assert "indistinguishable" in joined
    assert "detection limit" in joined
    assert "not a claim that discretionary access control constrains root" in joined
    assert "trusted-administrator premise is retained" in joined


# ---------------------------------------------------------------------------
# R2-4 — one allowlist, seven participants
# ---------------------------------------------------------------------------


def _released(**overrides) -> LifecycleHistory:
    fields = {
        "host": HOST,
        "readable": True,
        "complete": True,
        "predecessor_id": "RES-0",
        "predecessor_state": ReservationState.RELEASED,
        "disposition": PredecessorDisposition.RELEASED,
        "release_record": ReleaseRecord(
            reservation_id="RES-0",
            host=HOST,
            target_identity=HOST,
            released_at="2026-09-11T08:30:00Z",
            recorded_by="executor of RES-0",
        ),
        "target_identity": HOST,
    }
    fields.update(overrides)
    return LifecycleHistory(**fields)


def _recovered() -> LifecycleHistory:
    return LifecycleHistory(
        host=HOST,
        readable=True,
        complete=True,
        predecessor_id="RES-0",
        predecessor_state=ReservationState.QUARANTINED,
        disposition=PredecessorDisposition.OPERATOR_RECOVERED,
        operator_recovery_reference="ops-recovery-2026-09-11-01",
        target_identity=HOST,
        recovery_authored_by="peter duscha, operations owner",
    )


#: Every case R2-4 names, applied to all seven participants.
PARTICIPANT_TABLE = (
    ("fresh provisioned first use", environment_reset_history(HOST), True),
    ("a released predecessor", _released(), True),
    ("an operator-recovered predecessor", _recovered(), True),
    (
        "a crash after durable ADMITTED and before RUNNING",
        crash_between_admitted_and_running(HOST, "RES-0"),
        False,
    ),
    (
        "a running predecessor",
        LifecycleHistory(
            host=HOST,
            readable=True,
            complete=True,
            predecessor_id="RES-0",
            predecessor_state=ReservationState.RUNNING,
            disposition=PredecessorDisposition.ACTIVE,
        ),
        False,
    ),
    (
        "a recovering predecessor",
        LifecycleHistory(
            host=HOST,
            readable=True,
            complete=True,
            predecessor_id="RES-0",
            predecessor_state=ReservationState.RECOVERING,
            disposition=PredecessorDisposition.RECOVERING,
        ),
        False,
    ),
    (
        "a quarantined predecessor",
        LifecycleHistory(
            host=HOST,
            readable=True,
            complete=True,
            predecessor_id="RES-0",
            predecessor_state=ReservationState.QUARANTINED,
            disposition=PredecessorDisposition.QUARANTINED,
        ),
        False,
    ),
    ("an absent record", LifecycleHistory(host=HOST), False),
    (
        "an unreadable record claiming first use",
        LifecycleHistory(
            host=HOST,
            readable=False,
            disposition=PredecessorDisposition.VERIFIED_FIRST_USE,
        ),
        False,
    ),
    (
        "an incomplete record",
        LifecycleHistory(
            host=HOST,
            readable=True,
            complete=False,
            disposition=PredecessorDisposition.VERIFIED_FIRST_USE,
        ),
        False,
    ),
    (
        "an unclassified predecessor",
        LifecycleHistory(host=HOST, readable=True, complete=True),
        False,
    ),
    (
        "a malformed disposition",
        LifecycleHistory(host=HOST, readable=True, complete=True, disposition="released"),
        False,
    ),
    (
        "a contradictory released record",
        _released(predecessor_state=ReservationState.RUNNING),
        False,
    ),
)


@pytest.mark.parametrize(
    "label, history, expected",
    PARTICIPANT_TABLE,
    ids=[row[0] for row in PARTICIPANT_TABLE],
)
def test_all_seven_participants_share_one_allowlist(label, history, expected):
    """No participant is left with a weaker rule than the executor."""
    decisions = survey(
        history=history, lock=LockView(), host=HOST, target_identity=HOST
    )

    assert len(decisions) == 7
    assert {decision.participant for decision in decisions} == set(PARTICIPANTS)
    for decision in decisions:
        assert decision.may_proceed is expected, (label, decision.participant)
        if not expected:
            assert decision.refusals


def test_admitted_refuses_reuse_even_though_the_process_lock_is_free():
    """The state revision 2's denylist omitted, with the lock explicitly free."""
    decisions = survey(
        history=crash_between_admitted_and_running(HOST, "RES-0"),
        lock=LockView(held_by=None),
        host=HOST,
        target_identity=HOST,
    )

    for decision in decisions:
        assert decision.may_proceed is False
        assert any("still active on this host" in r for r in decision.refusals)
        assert any("'admitted'" in r for r in decision.refusals)


def test_a_held_lock_makes_every_participant_wait_or_refuse():
    decisions = survey(
        history=_released(),
        lock=LockView(held_by="RES-9", holder_owner="another executor"),
        host=HOST,
        target_identity=HOST,
    )

    for decision in decisions:
        assert decision.may_proceed is False
        assert any("wait or refuse, never proceed" in r for r in decision.refusals)


def test_an_unreadable_lock_is_not_an_unheld_lock_for_a_participant_either():
    decisions = survey(
        history=_released(),
        lock=LockView(observation_failed=True),
        host=HOST,
        target_identity=HOST,
    )

    for decision in decisions:
        assert decision.may_proceed is False


def test_the_environment_reset_refuses_especially_while_a_quarantine_exists():
    quarantine = QuarantineRecord(
        host=HOST,
        reservation_id="RES-0",
        reason="residue was not accounted for.",
        residue=("/opt/freedom-blades/evidence/run/journal/000001.seal",),
    )

    decisions = survey(
        history=_released(),
        lock=LockView(),
        host=HOST,
        target_identity=HOST,
        quarantine=quarantine,
    )

    for decision in decisions:
        assert decision.may_proceed is False
    reset = next(
        decision
        for decision in decisions
        if decision.participant is Participant.ENVIRONMENT_RESET
    )
    assert any("destroy the residue" in reason for reason in reset.refusals)


def test_only_the_executor_writes_the_lifecycle_record():
    writers = [
        participant for participant in PARTICIPANTS if participant.writes_the_record
    ]

    assert writers == [Participant.HARNESS_CLI]


def test_the_participants_are_exactly_the_contracts_seven_entry_points():
    from tools.phase_5_0_evidence.reservation import PARTICIPATING_ENTRY_POINTS

    assert {participant.value for participant in PARTICIPANTS} == set(
        PARTICIPATING_ENTRY_POINTS
    )


def test_the_allowlist_is_the_reservation_modules_own_and_not_a_copy():
    from tools.phase_5_0_evidence.reservation import VALIDATED_LIFECYCLE_OUTCOMES

    assert ADMITTING_OUTCOMES is VALIDATED_LIFECYCLE_OUTCOMES


def test_no_expiry_and_no_free_lock_authorizes_reuse():
    joined = " ".join(FREE_LOCK_AUTHORIZES_NOTHING)

    assert "No expiry authorizes reuse" in joined
    assert "ADMITTED is active" in joined
    assert "malformed" in joined


def test_records_stay_attributable_and_history_survives_an_update():
    joined = " ".join(RECORD_ATTRIBUTION)

    assert "Nothing deletes or rewrites a prior entry" in joined
    assert "appended" in joined
    assert "separate objects" in joined


# ---------------------------------------------------------------------------
# R2-4 — verified first use as a provisioning operation
# ---------------------------------------------------------------------------


class Store:
    """The provisioned lifecycle directory, empty, with the record object."""

    def __init__(self) -> None:
        self.fs = SyntheticFilesystem()
        root = self.fs.open_directory(self.fs.root, DescriptorMode.O_PATH, "").number
        root_sync = self.fs.open_directory(
            self.fs.root, DescriptorMode.O_RDONLY, ""
        ).number
        self.directory = self.fs.mkdirat(root, "laboratory")
        self.fs.fsync(root_sync)
        self.path_fd = self.fs.open_directory(
            self.directory, DescriptorMode.O_PATH, "/var/lib/freedom-blades/laboratory"
        ).number
        self.record = DurableRecordStore(
            self.fs,
            directory=self.directory,
            name="lifecycle.json",
            label="/var/lib/freedom-blades/laboratory",
            kinds=RESERVATION_KINDS,
        )


def _attested() -> FirstUseEvidence:
    return FirstUseEvidence(
        prior_use_excluded=True,
        attested_by="peter duscha, operations owner",
        basis="the host was rebuilt from a fresh image on 2026-09-11",
    )


def _initialize(store: Store, **overrides):
    fields = {
        "host": HOST,
        "target_identity": HOST,
        "approved_host": HOST,
        "approved_target_identity": HOST,
        "evidence": _attested(),
    }
    fields.update(overrides)
    return initialize_first_use_record(store.record, **fields)


def test_fresh_provisioned_first_use_initializes_durably():
    """The successful control revision 2's fresh-install path could not reach."""
    store = Store()

    outcome = _initialize(store)

    assert outcome.initialized is True
    assert outcome.durable is True
    assert outcome.refusal is None
    assert outcome.barriers == ("record-data", "record-entry")
    # The oracle's observation, which no modelled participant may make.
    assert store.fs.entry_is_durable(store.path_fd, "lifecycle.json") is True

    store.fs.crash()
    assert store.fs.now().resolve(store.directory, "lifecycle.json") is not None


def test_a_constructed_first_use_history_admits_every_participant():
    """A **unit test** over a constructed history, and deliberately labelled one.

    It builds a `LifecycleHistory` with `environment_reset_history` and hands it
    to the allowlist. It reads no stored byte, so **it is not evidence that
    storage and admission are connected** and it makes no end-to-end claim: the
    version of this test that did make one is withdrawn, because
    PR-20260911-R3-1 and -R3-3 are exactly the gaps a constructed history cannot
    detect. The connected path is
    `test_r3_lifecycle.py::test_a_complete_successful_lifecycle_admits_a_successor_from_stored_evidence`.
    """
    decisions = survey(
        history=environment_reset_history(HOST),
        lock=LockView(),
        host=HOST,
        target_identity=HOST,
    )

    assert all(decision.may_proceed for decision in decisions)
    assert "environment_reset_history" in UNIT_TEST_CONSTRUCTORS


def test_an_existing_record_is_never_reinitialized():
    store = Store()
    assert _initialize(store).initialized is True

    outcome = _initialize(store)

    assert outcome.initialized is False
    assert outcome.refusal is FirstUseRefusal.ALREADY_INITIALIZED
    assert outcome.recovery


def test_missing_history_on_a_previously_used_host_is_never_first_use():
    """R2-4's named case, and the one a convenience would get wrong."""
    store = Store()

    outcome = _initialize(store, host_previously_used=True)

    assert outcome.initialized is False
    assert outcome.refusal is FirstUseRefusal.PRIOR_USE_NOT_EXCLUDED
    assert any("never reinitialize" in step.lower() for step in outcome.recovery)
    assert store.fs.now().resolve(store.directory, "lifecycle.json") is None


@pytest.mark.parametrize(
    "evidence",
    (
        FirstUseEvidence(),
        FirstUseEvidence(prior_use_excluded=True),
        FirstUseEvidence(prior_use_excluded=True, attested_by="somebody"),
    ),
)
def test_first_use_without_a_complete_attestation_refuses(evidence):
    store = Store()

    outcome = _initialize(store, evidence=evidence)

    assert outcome.initialized is False
    assert outcome.refusal is FirstUseRefusal.NO_FIRST_USE_EVIDENCE


@pytest.mark.parametrize("stage", ("record-data", "rename", "record-entry"))
def test_an_interrupted_initialization_publishes_nothing_and_refuses(stage):
    store = Store()

    outcome = _initialize(store, fail_at=stage)

    assert outcome.initialized is False
    assert outcome.refusal is FirstUseRefusal.NOT_DURABLE
    assert outcome.recovery

    store.fs.crash()
    assert store.fs.now().resolve(store.directory, "lifecycle.json") is None


def test_a_leftover_temporary_is_reported_and_not_cleaned():
    store = Store()
    _initialize(store, fail_at="record-data")

    outcome = _initialize(store)

    assert outcome.initialized is False
    assert outcome.refusal is FirstUseRefusal.INTERRUPTED_INITIALIZATION
    assert any("not removed automatically" in step for step in outcome.recovery)


def test_a_host_with_no_record_refuses_every_participant_until_it_is_initialized():
    """The absent record refuses, and initialization is the only way out."""
    decisions = survey(
        history=LifecycleHistory(host=HOST),
        lock=LockView(),
        host=HOST,
        target_identity=HOST,
    )

    assert not any(decision.may_proceed for decision in decisions)
    for decision in decisions:
        assert any("could not be read" in reason for reason in decision.refusals)


def test_the_provisioning_delta_is_stated_and_unapproved():
    keys = {row[0] for row in PROPOSED_PROVISIONING}

    assert {
        "creator",
        "authority",
        "path",
        "ownership and modes",
        "binding",
        "creation rule",
        "durability",
        "evidence of first use",
    } <= keys
    joined = " ".join(value for _key, value in PROPOSED_PROVISIONING)
    assert "not approved" in joined
    assert "never reinitialized" in joined
