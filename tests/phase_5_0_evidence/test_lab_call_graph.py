"""The executable harness call graph — PR-20260914-LABI-R1-1.

## What this module is

Codex's re-review of C-P5.0-LAB-I-R1 accepted the two safety repairs and found
the third finding unrepaired **in the call graph**. The CLI constructed a
`ParticipantIntegration` and handed it to `ExecutingRunner(session=...)`, then
called `runner.execute()` itself; no caller ever invoked `run_harness()` or
`run()`, so the only production calls to `session.admit()` were inside two
unused methods. The executor's guard asked whether `session` was non-`None` and
`run_id` non-empty, which `session=object()` satisfies — so the armed path could
have reached its first effect without taking the lock or publishing
`participant_started`.

Every test here was written against the submitted tree, where each one fails:
the guard accepted `object()`, `execute_under_reservation` did not exist and
`run_harness` took its release evidence as an argument. The handback records the
verbatim before-and-after.

## Structural and behavioural, paired

The prompt for the previous round was explicit that a source substring is not
proof of ordering, and this re-review repeated it: the CLI composition test must
*observe* admit → durable start → executor → terminal sequence rather than
assert construction. So the composition tests below drive the real
`ParticipantIntegration` over a laboratory under `tmp_path` and read the
**durable files** the protocol wrote, in the order the run reached them.

## What it is not

Nothing here provisions anything, starts a process, reaches a database or
observes `oracle-test`. `is_executable` stays `False` and `REAL_EXECUTION_REFUSAL`
stands: closing a fail-open call graph is not permission to walk it.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.phase_5_0_evidence.harness_fixtures import (
    RecordingEffects,
    runnable_plan,
    supply_reviewed_e7_facts,
    load_test_source_bytes,
)
from tests.phase_5_0_evidence.lab_fixtures import (
    AT,
    ATTESTER,
    BASIS,
    HOST,
    TARGET_IDENTITY,
    bind,
    build_laboratory,
)
from tools.phase_5_0_evidence import case_runtime, reservation as reservation_module
from tools.phase_5_0_evidence.approved_target import CONFIRMATION_TOKEN
from tools.phase_5_0_evidence.cleanup import CleanupOutcome
from tools.phase_5_0_evidence.concrete_plan import build_concrete_plan
from tools.phase_5_0_evidence.durability_model import Quiescence
from tools.phase_5_0_evidence.execution import cli as cli_module
from tools.phase_5_0_evidence.execution.boundary import RecordingBoundary
from tools.phase_5_0_evidence.execution.cli import execute_under_reservation
from tools.phase_5_0_evidence.execution.descriptors import (
    DescriptorInventory,
    PosixFilesystem,
)
from tools.phase_5_0_evidence.execution.executor import (
    DescriptorBoundEffects,
    ExecutingRunner,
    ExecutorRefused,
    RunOutcome,
)
from tools.phase_5_0_evidence.execution.materializer import RecordingMaterializer
from tools.phase_5_0_evidence.execution.participants import (
    PARTICIPANT_START_NOT_DURABLE,
    EffectPermit,
    HarnessObservations,
    ParticipantIntegration,
    ParticipantRefused,
)
from tools.phase_5_0_evidence.lifecycle_storage import (
    EntryKind,
    FirstUseEvidence,
    Participant,
    RunPhase,
)
from tools.phase_5_0_evidence.reservation import (
    ReservationRequest,
    ReservationState,
    ResidueObservation,
)
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES, ReviewManifest

SOURCES = load_test_source_bytes()

#: The two reviewed target facts, as a run would have them. Each gate is
#: asserted against its **shipped** unconfirmed value elsewhere; this module is
#: about the call graph, so it is given them rather than blocked on them.
REVIEWED_INTERPRETER_DIGEST = "5" * 64
REVIEWED_INTERPRETER_REAL_PATH = "/opt/fb-reviewed/python3.12"

RESERVATION = "RES-LABI-R1"
RUN_ID = "RUN-LABI-R1"
OBSERVER = "the operations owner"


@pytest.fixture(autouse=True)
def _the_reviewed_target_facts_are_supplied(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        case_runtime, "EXPECTED_INTERPRETER_SHA256", REVIEWED_INTERPRETER_DIGEST
    )
    monkeypatch.setattr(
        case_runtime,
        "EXPECTED_INTERPRETER_REAL_PATH",
        REVIEWED_INTERPRETER_REAL_PATH,
    )
    supply_reviewed_e7_facts(monkeypatch)


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


def _armed_effects(inventory: DescriptorInventory) -> DescriptorBoundEffects:
    """The **real** issuer, armed, over an empty inventory.

    The guard checks the type rather than an attribute looked up by name, so a
    duck-typed double must not be able to trip it either. It is never asked to
    issue anything: every test below refuses before the first step.
    """
    return DescriptorBoundEffects(
        inventory=inventory, filesystem=PosixFilesystem(inventory), armed=True
    )


def _runner(*, effects, **overrides) -> ExecutingRunner:
    """A real executor over the fixture plan, with a boundary that starts nothing."""
    plan = runnable_plan()
    keywords = dict(
        plan=plan,
        boundary=RecordingBoundary(),
        materializer=RecordingMaterializer(),
        effects=effects,
        reviewed_digest=ReviewManifest.build(plan, SOURCES).digest(),
        confirmation_token=CONFIRMATION_TOKEN,
        source_bytes=dict(SOURCES),
        run_id=RUN_ID,
        reservation_id=RESERVATION,
    )
    keywords.update(overrides)
    return ExecutingRunner(**keywords)


def _initialized(lab):
    """A laboratory whose reservation record admits a successor."""
    bound = bind(lab)
    try:
        outcome = bound.record.initialize(
            approved_host=HOST,
            approved_target_identity=TARGET_IDENTITY,
            evidence=FirstUseEvidence(
                prior_use_excluded=True, attested_by=ATTESTER, basis=BASIS
            ),
            attested_at=AT,
        )
        assert outcome.initialized and outcome.durable, outcome
    finally:
        bound.close()
    return lab


def _integration(lab) -> ParticipantIntegration:
    """The production integration point, over the fixture's layout."""
    return ParticipantIntegration(
        participant=Participant.HARNESS_CLI,
        host=HOST,
        target_identity=TARGET_IDENTITY,
        author="the harness",
        at=AT,
        layout=lab.layout,
        reservation_id=RESERVATION,
        wait_for_lock=False,
    )


def _request() -> ReservationRequest:
    return ReservationRequest(
        reservation_id=RESERVATION,
        owner="the operations owner",
        host=HOST,
        target_identity=TARGET_IDENTITY,
        requested_at=AT,
        deadline="2026-09-13T20:00:00Z",
        recovery_owner="the operations owner",
        real_execution=False,
    )


def _issued_permit(lab, *, run_id: str = RUN_ID) -> EffectPermit:
    """A genuinely issued permit, obtained by running rather than by building.

    **Corrected for PR-20260914-LABI-R1-2.** An earlier version of this
    docstring said a test *cannot* construct one. It can — `_grant_permit` and
    `_PERMIT_GRANT` are readable module attributes, and
    `test_lab_live_authority.py` constructs both forms deliberately. What a
    constructed one lacks is the live invocation, so this still drives a real
    pass over the fixture laboratory: the tests below are about the **value**
    binding, and a genuine permit is the honest input for them.
    """
    issued: list[EffectPermit] = []

    def work(permit: EffectPermit) -> HarnessObservations:
        issued.append(permit)
        return HarnessObservations(
            residue=ResidueObservation.empty(observed_by=OBSERVER),
            configuration_restored=True,
            child_processes_ended=True,
            database_transactions_settled=True,
        )

    _integration(lab).run_harness(
        run_id=run_id, work=work, request=_request(), observed_by=OBSERVER
    )
    assert issued and issued[0].issued
    return issued[0]


def _clean_outcome() -> RunOutcome:
    """A finished run whose cleanup reached S-C and left nothing."""
    return RunOutcome(
        steps=(),
        cleanup_steps=(),
        cleanup=CleanupOutcome(
            state="S-C", exit_code=0, residue=(), message="cleanup complete"
        ),
    )


class _RecordingRunner:
    """An executor double that records **when** it ran, not merely that it did.

    It reads the laboratory's durable files at the moment the work reaches it,
    so the assertions below are about the order the protocol actually took
    rather than about the order the source is written in.
    """

    def __init__(self, lab, *, outcome: RunOutcome | None = None, raises=None) -> None:
        self.lab = lab
        self.permits: list[EffectPermit] = []
        self.run_file_at_execute: bool | None = None
        self.record_at_execute: bytes = b""
        self.executed = 0
        self.observed: list[tuple[str, str]] = []
        self._outcome = outcome if outcome is not None else _clean_outcome()
        self._raises = raises

    def accept_permit(self, permit: EffectPermit) -> None:
        self.permits.append(permit)

    def execute(self) -> RunOutcome:
        self.executed += 1
        self.run_file_at_execute = (self.lab.runs_directory / RUN_ID).exists()
        self.record_at_execute = self.lab.record_path.read_bytes()
        if self._raises is not None:
            raise self._raises
        return self._outcome

    def run_observations(
        self, outcome: RunOutcome, *, observed_by: str, searched_at: str
    ) -> HarnessObservations:
        self.observed.append((observed_by, searched_at))
        assert outcome is self._outcome
        return HarnessObservations(
            residue=ResidueObservation.empty(
                observed_by=observed_by, searched_at=searched_at
            ),
            configuration_restored=True,
        )


# ---------------------------------------------------------------------------
# 1. The guard the re-review reproduced
# ---------------------------------------------------------------------------


def test_an_armed_executor_with_a_sentinel_session_reaches_no_effect() -> None:
    """**Behavioural, the finding.** `session=object()`, and no effect is reached.

    The re-review's exact reproduction: an armed `DescriptorBoundEffects`, a
    non-empty run id, and any object at all in `session`. The old guard accepted
    it. The run now refuses at `execute()` — before the first step, so the
    boundary is asked to start nothing, the materializer to write nothing and
    the issuer to issue nothing.
    """
    inventory = DescriptorInventory()
    try:
        runner = _runner(
            effects=_armed_effects(inventory), session=object(), run_id="RUN-1"
        )
        with pytest.raises(ExecutorRefused) as refusal:
            runner.execute()
        assert "accounts for the run" in str(refusal.value)
        assert runner.boundary.calls == []
        assert runner.materializer.requests == []
    finally:
        inventory.close()


def test_a_real_integration_without_a_permit_reaches_no_effect(tmp_path) -> None:
    """**Behavioural.** The integration point alone is not the protocol.

    Holding a genuine `ParticipantIntegration` proves that one was constructed.
    It does not prove that the lock was taken or that a start was published, and
    the permit is the only object that says so.
    """
    lab = _initialized(build_laboratory(tmp_path))
    inventory = DescriptorInventory()
    try:
        runner = _runner(effects=_armed_effects(inventory), session=_integration(lab))
        with pytest.raises(ExecutorRefused) as refusal:
            runner.execute()
        assert "issued by the participant integration point" in str(refusal.value)
        assert runner.boundary.calls == []
        # Nothing was published: the guard refused before the protocol began.
        assert not (lab.runs_directory / RUN_ID).exists()
    finally:
        inventory.close()


def test_a_permit_cannot_be_constructed_granted() -> None:
    """**Behavioural.** `granted=True` on its own refuses at construction.

    **What this proves, and what it does not — PR-20260914-LABI-R1-2.** It
    proves that *omitting* the marker refuses, which catches an accidental
    `granted=True`. It does **not** prove that a caller cannot obtain the
    marker: it can, `_PERMIT_GRANT` is readable, and the re-review said so.
    The property that closes the path is `EffectPermit.consume`'s, and
    `test_lab_live_authority.py` is where it is asserted — starting with a
    permit built from exactly those readable attributes.
    """
    with pytest.raises(ParticipantRefused) as refusal:
        EffectPermit(
            participant=Participant.HARNESS_CLI,
            run_id=RUN_ID,
            reservation_id=RESERVATION,
            granted=True,
        )
    assert refusal.value.classification == PARTICIPANT_START_NOT_DURABLE

    ungranted = EffectPermit(participant=Participant.HARNESS_CLI, run_id=RUN_ID)
    assert ungranted.issued is False
    with pytest.raises(ParticipantRefused):
        ungranted.require()


def test_a_permit_for_another_run_does_not_account_for_this_one(tmp_path) -> None:
    """**Behavioural.** Equality on all three, both ways — r6 §5.11.1's rule.

    A genuinely issued permit is still another run's accounting when it names
    another run or another reservation, and an executor that accepted one would
    be running on somebody else's durable start.
    """
    lab = _initialized(build_laboratory(tmp_path))
    permit = _issued_permit(lab)
    inventory = DescriptorInventory()
    try:
        runner = _runner(
            effects=_armed_effects(inventory),
            session=_integration(lab),
            run_id="OTHER-RUN",
            permit=permit,
        )
        with pytest.raises(ExecutorRefused) as refusal:
            runner.execute()
        assert "does not bind this run" in str(refusal.value)
        assert runner.boundary.calls == []
    finally:
        inventory.close()


def test_only_the_permit_s_reservation_differs_and_it_still_refuses(
    tmp_path,
) -> None:
    """**Behavioural, one conjunct.** The permit's own reservation is compared.

    Everything else agrees: the integration point, the executor and the run id
    all name `RES-OTHER`, and only the permit was issued for `RES-LABI-R1`. It
    is still another reservation's durable start, and it is still refused — so
    the equality on the permit's reservation is load-bearing on its own rather
    than shadowed by the session comparison beside it.
    """
    lab = _initialized(build_laboratory(tmp_path))
    permit = _issued_permit(lab)
    other_session = _integration(lab)
    other_session.reservation_id = "RES-OTHER"

    inventory = DescriptorInventory()
    try:
        runner = _runner(
            effects=_armed_effects(inventory),
            session=other_session,
            run_id=RUN_ID,
            reservation_id="RES-OTHER",
            permit=permit,
        )
        with pytest.raises(ExecutorRefused) as refusal:
            runner.execute()
        assert "does not bind this run" in str(refusal.value)
        assert runner.boundary.calls == []
    finally:
        inventory.close()


def test_the_permit_and_the_integration_point_name_one_participant(
    tmp_path,
) -> None:
    """**Behavioural, one conjunct.** The two halves must be the same participant.

    A harness permit held beside a *web suite* integration point binds this run
    id and this reservation perfectly well, and it is still a run whose durable
    start was published by something other than what is now accounting for it.
    """
    lab = _initialized(build_laboratory(tmp_path))
    permit = _issued_permit(lab)
    not_the_harness = ParticipantIntegration(
        participant=Participant.WEB_SUITE,
        host=HOST,
        target_identity=TARGET_IDENTITY,
        author="the web suite",
        at=AT,
        layout=lab.layout,
        reservation_id=RESERVATION,
    )
    inventory = DescriptorInventory()
    try:
        runner = _runner(
            effects=_armed_effects(inventory),
            session=not_the_harness,
            permit=permit,
        )
        with pytest.raises(ExecutorRefused) as refusal:
            runner.execute()
        assert "different participants" in str(refusal.value)
        assert runner.boundary.calls == []
    finally:
        inventory.close()


def test_a_second_hand_off_refuses(tmp_path) -> None:
    """One run, one durable start, one hand-off."""
    lab = _initialized(build_laboratory(tmp_path))
    permit = _issued_permit(lab)
    inventory = DescriptorInventory()
    try:
        runner = _runner(effects=_armed_effects(inventory), session=_integration(lab))
        runner.accept_permit(permit)
        with pytest.raises(ExecutorRefused) as refusal:
            runner.accept_permit(permit)
        assert "already been handed its permit" in str(refusal.value)

        # And an unissued permit never gets that far.
        fresh = _runner(effects=_armed_effects(inventory), session=_integration(lab))
        with pytest.raises(ExecutorRefused):
            fresh.accept_permit(
                EffectPermit(participant=Participant.HARNESS_CLI, run_id=RUN_ID)
            )
    finally:
        inventory.close()


# ---------------------------------------------------------------------------
# 2. The negative control — one reversal, and the regression fails
# ---------------------------------------------------------------------------


def test_the_presence_control_admits_the_sentinel_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """**Negative control.** Restore only the presence-only check.

    This is the guard as the re-review found it: refuse when `session is None`
    or the run id is empty, and otherwise proceed. With it in place the armed
    executor accepts `session=object()` and walks on into the run — which is
    what the regression above exists to prevent, and the reversal makes that
    regression fail rather than merely look different.
    """

    def presence_only(self) -> None:
        issuer = self.effects
        if not isinstance(issuer, DescriptorBoundEffects) or not issuer.armed:
            return
        if self.session is None or not self.run_id:
            raise ExecutorRefused("unaccounted")

    monkeypatch.setattr(ExecutingRunner, "_require_accounted_run", presence_only)
    inventory = DescriptorInventory()
    try:
        runner = _runner(
            effects=_armed_effects(inventory), session=object(), run_id="RUN-1"
        )
        outcome = runner.execute()
        # The guard did not refuse: the run reached the step loop and the
        # boundary was asked to start the reviewed plan's first command.
        assert runner.boundary.calls, "the reversal should reach the boundary"
        assert isinstance(outcome, RunOutcome)
    finally:
        inventory.close()


# ---------------------------------------------------------------------------
# 3. The composition, observed rather than asserted
# ---------------------------------------------------------------------------


def test_the_composition_admits_starts_executes_then_publishes(tmp_path) -> None:
    """**Behavioural.** admit → durable start → executor → terminal, observed.

    The double reads the laboratory's durable files at the moment the work
    reaches it. The run file already exists — the start was published **before**
    the executor ran — and the reservation record does not yet carry a release
    entry, because §5.12's steps 1 to 3 happen after the work returns and before
    the lock is released.
    """
    lab = _initialized(build_laboratory(tmp_path))
    integration = _integration(lab)
    runner = _RecordingRunner(lab)

    harness = execute_under_reservation(
        integration=integration,
        runner=runner,
        request=_request(),
        run_id=RUN_ID,
        quiescence=Quiescence.verified(observed_by=OBSERVER),
        observed_by=OBSERVER,
        searched_at=AT,
    )

    # The executor ran exactly once, on a permit bound to this run.
    assert runner.executed == 1
    assert len(runner.permits) == 1
    permit = runner.permits[0]
    assert permit.binds(
        participant=Participant.HARNESS_CLI,
        run_id=RUN_ID,
        reservation_id=RESERVATION,
    )

    # The durable start preceded it, and the release did not.
    assert runner.run_file_at_execute is True
    assert b"released" not in runner.record_at_execute

    # §5.12 published both halves, and the lock is released afterwards.
    assert harness.terminal is not None
    assert harness.terminal.decision is ReservationState.RELEASED
    assert harness.released is True
    assert harness.run.completed is True
    assert harness.run.unsettled is False
    assert integration._session is None

    bound = bind(lab)
    try:
        parsed = bound.record.read()
        assert parsed.ok
        assert parsed.entries[-1].kind is EntryKind.RELEASED
        stored = bound.ledger.read_run(RUN_ID)
        assert stored.ok
        assert stored.state.phase is RunPhase.COMPLETED
    finally:
        bound.close()


def test_the_executor_is_reached_only_through_the_protocol(tmp_path) -> None:
    """**Behavioural.** A refused admission never reaches the executor.

    An unsettled predecessor refuses the survey, so the harness is not admitted;
    the work is never called, the executor never runs and nothing is published
    for this run.
    """
    lab = _initialized(build_laboratory(tmp_path))
    blocked = ParticipantIntegration(
        participant=Participant.WEB_SUITE,
        host=HOST,
        target_identity=TARGET_IDENTITY,
        author="the web suite",
        at=AT,
        layout=lab.layout,
    )
    from tools.phase_5_0_evidence.lifecycle_storage import PARTICIPANT_PROFILES

    conditions = {
        condition: False
        for condition in PARTICIPANT_PROFILES[
            Participant.WEB_SUITE
        ].external_conditions()
    }
    unsettled = blocked.run(
        run_id="RUN-OPEN",
        work=lambda permit: (permit.require(), conditions)[1],
        observed_by=OBSERVER,
    )
    assert unsettled.unsettled

    runner = _RecordingRunner(lab)
    harness = execute_under_reservation(
        integration=_integration(lab),
        runner=runner,
        request=_request(),
        run_id=RUN_ID,
        quiescence=Quiescence.verified(observed_by=OBSERVER),
        observed_by=OBSERVER,
        searched_at=AT,
    )
    assert runner.executed == 0
    assert runner.permits == []
    assert harness.run.admitted is False
    assert harness.terminal is None
    assert not (lab.runs_directory / RUN_ID).exists()


def test_an_exception_in_the_work_leaves_the_durable_start_unsettled(
    tmp_path,
) -> None:
    """**Behavioural.** An interrupted run blocks every successor.

    The work raises, so no completion and no release is published. The lock is
    released — it is not the reservation — and the durable `participant_started`
    entry stays in progress, which is what refuses the next participant until an
    attributable recovery is published.
    """
    lab = _initialized(build_laboratory(tmp_path))
    integration = _integration(lab)
    runner = _RecordingRunner(lab, raises=KeyboardInterrupt())

    with pytest.raises(KeyboardInterrupt):
        execute_under_reservation(
            integration=integration,
            runner=runner,
            request=_request(),
            run_id=RUN_ID,
            quiescence=Quiescence.verified(observed_by=OBSERVER),
            observed_by=OBSERVER,
            searched_at=AT,
        )

    assert integration._session is None  # the lock was released
    bound = bind(lab)
    try:
        stored = bound.ledger.read_run(RUN_ID)
        assert stored.ok
        assert stored.state.phase is RunPhase.IN_PROGRESS
        parsed = bound.record.read()
        assert all(entry.kind is not EntryKind.RELEASED for entry in parsed.entries)
        survey = bound.ledger.survey()
        assert RUN_ID in survey.unsettled
        assert survey.settled is False
    finally:
        bound.close()


# ---------------------------------------------------------------------------
# 4. The release evidence is derived from the run, not supplied to it
# ---------------------------------------------------------------------------


def test_the_release_evidence_comes_from_the_cleanup_outcome() -> None:
    """**Behavioural.** Residue and restoration are the executor's own result."""
    inventory = DescriptorInventory()
    try:
        runner = _runner(effects=RecordingEffects())
        clean = runner.run_observations(
            _clean_outcome(), observed_by=OBSERVER, searched_at=AT
        )
        assert clean.residue.observed and clean.residue.complete
        assert clean.residue.paths == ()
        assert clean.configuration_restored is True

        dirty = RunOutcome(
            steps=(),
            cleanup_steps=(),
            cleanup=CleanupOutcome(
                state="S-B",
                exit_code=3,
                residue=("/var/lib/fb-evidence-p5-0",),
                message="cleanup could not complete",
                configuration_risk=("pg_hba.conf may still be in force",),
            ),
        )
        observations = runner.run_observations(
            dirty, observed_by=OBSERVER, searched_at=AT
        )
        assert observations.residue.paths == ("/var/lib/fb-evidence-p5-0",)
        assert observations.configuration_restored is False
        # And that evidence quarantines rather than releases.
        outcome = reservation_module.release(
            request=_request(),
            current_state=ReservationState.RUNNING,
            evidence=reservation_module.ReleaseEvidence(
                reservation_id=RESERVATION,
                target_identity=TARGET_IDENTITY,
                lock_held_by=RESERVATION,
                child_processes_ended=True,
                database_transactions_settled=True,
                residue=observations.residue,
                configuration_restored=observations.configuration_restored,
            ),
        )
        assert outcome.state is ReservationState.QUARANTINED
    finally:
        inventory.close()


def test_an_unobserved_quiescence_quarantines_the_reservation(tmp_path) -> None:
    """**Behavioural.** r6 §1.6's unmade observations are never passed ones.

    Nobody observed that the run's processes exited or that its transactions
    settled, so the release cannot establish its conditions and quarantines.
    Both terminal entries are withheld and the harness run stays unsettled.
    """
    lab = _initialized(build_laboratory(tmp_path))
    runner = _RecordingRunner(lab)
    harness = execute_under_reservation(
        integration=_integration(lab),
        runner=runner,
        request=_request(),
        run_id=RUN_ID,
        quiescence=Quiescence.not_observed(),
        observed_by=OBSERVER,
        searched_at=AT,
    )
    assert runner.executed == 1
    assert harness.terminal is not None
    assert harness.terminal.decision is ReservationState.QUARANTINED
    assert harness.released is False
    assert harness.run.unsettled is True


def test_the_lock_holder_is_read_from_the_open_descriptor(tmp_path) -> None:
    """**Behavioural, one conjunct.** An early release cannot pass for a held lock.

    `release()` refuses when the cooperative lock is held by anybody other than
    the reservation, which is the check that catches a run that let go of the
    host while it was still active. The only honest answer to *"who holds it"*
    comes from the holder's own open descriptor: a session that is not open
    reports no holder, and the release then quarantines instead of releasing.
    """
    lab = _initialized(build_laboratory(tmp_path))
    integration = _integration(lab)
    observations = HarnessObservations(
        residue=ResidueObservation.empty(observed_by=OBSERVER),
        configuration_restored=True,
        child_processes_ended=True,
        database_transactions_settled=True,
    )

    closed = lab.session(reservation_id=RESERVATION)
    assert closed.holds_lock is False
    withheld = integration._release_evidence(closed, observations)
    assert withheld.lock_held_by is None
    assert (
        reservation_module.release(
            request=_request(),
            current_state=ReservationState.RUNNING,
            evidence=withheld,
        ).state
        is ReservationState.QUARANTINED
    )

    with closed as open_session:
        assert open_session.holds_lock is True
        held = integration._release_evidence(open_session, observations)
    assert held.lock_held_by == RESERVATION
    assert (
        reservation_module.release(
            request=_request(),
            current_state=ReservationState.RUNNING,
            evidence=held,
        ).state
        is ReservationState.RELEASED
    )


def test_an_unobserved_quiescence_is_never_an_observed_one() -> None:
    """**Behavioural, one conjunct.** *Not checked* does not become *checked*.

    r6 §1.6 is explicit that none of the three defaults to true and that an
    observation nobody made is not one that passed. A `Quiescence` whose values
    say `True` while nobody observed them, and one that names no observer, both
    reach the release as unmade — because the observation, not the value, is
    what a release compares.
    """
    run_facts = HarnessObservations(
        residue=ResidueObservation.empty(observed_by=OBSERVER),
        configuration_restored=True,
    )

    unobserved = run_facts.with_quiescence(
        Quiescence(
            observed=False,
            processes_ended=True,
            transactions_settled=True,
            transient_units_inactive=True,
            observed_by=OBSERVER,
        )
    )
    assert unobserved.child_processes_ended is None
    assert unobserved.database_transactions_settled is None

    unattributed = run_facts.with_quiescence(
        Quiescence(
            observed=True,
            processes_ended=True,
            transactions_settled=True,
            transient_units_inactive=True,
            observed_by="   ",
        )
    )
    assert unattributed.child_processes_ended is None
    assert unattributed.database_transactions_settled is None

    observed = run_facts.with_quiescence(Quiescence.verified(observed_by=OBSERVER))
    assert observed.child_processes_ended is True
    assert observed.database_transactions_settled is True
    # The run's own facts are carried through unchanged either way.
    assert observed.residue is run_facts.residue
    assert observed.configuration_restored is True


def test_the_work_cannot_name_another_reservation_or_target(tmp_path) -> None:
    """**Behavioural.** The three identity fields are derived, not returned.

    `HarnessObservations` carries no reservation, no target and no lock holder,
    so a work callable cannot supply the halves `reservation.release` compares.
    A request for another reservation refuses before the lock is taken.
    """
    lab = _initialized(build_laboratory(tmp_path))
    assert not hasattr(HarnessObservations(), "reservation_id")
    integration = _integration(lab)
    other = ReservationRequest(
        reservation_id="RES-SOMEBODY-ELSE",
        owner="the operations owner",
        host=HOST,
        target_identity=TARGET_IDENTITY,
        requested_at=AT,
        deadline="2026-09-13T20:00:00Z",
        recovery_owner="the operations owner",
    )
    with pytest.raises(ParticipantRefused):
        integration.run_harness(
            run_id=RUN_ID,
            work=lambda permit: HarnessObservations(),
            request=other,
            observed_by=OBSERVER,
        )
    assert not (lab.runs_directory / RUN_ID).exists()


def test_a_work_that_returns_something_else_publishes_no_release(tmp_path) -> None:
    """The harness's work returns observations, or the conclusion refuses."""
    lab = _initialized(build_laboratory(tmp_path))
    integration = _integration(lab)
    with pytest.raises(ParticipantRefused):
        integration.run_harness(
            run_id=RUN_ID,
            work=lambda permit: {"everything": True},
            request=_request(),
            observed_by=OBSERVER,
        )
    bound = bind(lab)
    try:
        stored = bound.ledger.read_run(RUN_ID)
        assert stored.state.phase is RunPhase.IN_PROGRESS
    finally:
        bound.close()


# ---------------------------------------------------------------------------
# 5. Structural — one orchestration path, and the executor is inside it
# ---------------------------------------------------------------------------


def _function(name: str) -> ast.FunctionDef:
    tree = ast.parse(Path(cli_module.__file__).read_text(encoding="utf-8"))
    return next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == name
    )


def _attribute_calls(tree: ast.AST) -> set[str]:
    return {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }


def test_the_orchestration_path_calls_the_participant_protocol() -> None:
    """**Structural.** `run_harness` is called, and `main` does not drive the run."""
    orchestration = _function("execute_under_reservation")
    assert "run_harness" in _attribute_calls(orchestration)
    assert {"accept_permit", "execute", "run_observations"} <= _attribute_calls(
        orchestration
    )
    assert "execute_under_reservation" in {
        node.func.id
        for node in ast.walk(_function("main"))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }


def test_the_executor_is_driven_from_inside_the_work_closure() -> None:
    """**Structural.** `runner.execute()` appears only inside `work`.

    The re-review's order — construct, then call `runner.execute()` beside the
    integration — is what this excludes. Every `execute()` call site in the CLI
    is inside the closure `run_harness` invokes after the durable start.
    """
    module = ast.parse(Path(cli_module.__file__).read_text(encoding="utf-8"))
    work = next(
        node
        for node in ast.walk(module)
        if isinstance(node, ast.FunctionDef) and node.name == "work"
    )
    inside = {id(node) for node in ast.walk(work)}
    for node in ast.walk(module):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "execute"
        ):
            assert id(node) in inside, ast.unparse(node)


def test_the_standing_operational_gates_are_all_still_closed() -> None:
    """Closing a call graph closes no gate and opens no permission."""
    plan = build_concrete_plan()
    assert plan.is_executable is False
    assert reservation_module.REAL_EXECUTION_REFUSAL
    assert "C-7" in plan.conflicts()


def test_this_suite_builds_over_no_production_path() -> None:
    """Every path is under `tmp_path`; the three production roots are absent."""
    from tools.phase_5_0_evidence.provisioning import LABORATORY_LAYOUT

    for path in (
        Path(LABORATORY_LAYOUT.lock_path),
        Path(LABORATORY_LAYOUT.laboratory_directory),
        Path(LABORATORY_LAYOUT.recovery_directory),
    ):
        assert not path.exists(), path
