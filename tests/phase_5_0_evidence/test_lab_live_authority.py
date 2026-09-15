"""The executor's authority must be **live**, not merely genuine — LABI-R1-2.

## What this module is

The re-review of PR-20260914-LABI-R1-1 accepted the call-graph repair and found
the replacement authority insufficient. Two reproductions:

* **A — the token is constructible.** `participants._PERMIT_GRANT` is an
  ordinary readable module attribute and `participants._grant_permit` an
  ordinary callable one. A leading underscore is not an access boundary in
  Python, so an accepted `EffectPermit` could be built without ever taking the
  lock or publishing a start.
* **B — a genuine permit is replayable.** The permit a work callback receives
  stays `issued=True` for ever. Handed back to an armed executor after
  `run_harness()` had published both terminal entries and released the lock, it
  still satisfied a guard that only compared types and values.

Both reach `_require_accounted_run()` past a check that establishes nothing
about **now**: r6 §§5.6–5.7 require T9 to happen while the executor holds the
lock and the current T6/T7/T8 state stands, not merely after such a state
existed at some earlier time.

## The property these tests assert

The first effect is reachable only while **this** integration point is inside
**this** `work` invocation: it owns an open session, that session still holds
the cooperative lock, the stored run is present, valid, the harness, bound to
this reservation and still in progress, the reservation record is in its T8
`running` state, and the authority has not already been spent. Every one of
those is read at the last moment before effects, through the authoritative
record and ledger readers rather than a second copy of them.

## One issuance, one consumption — PR-20260914-LABI-R2-1

The re-review of that correction found the one-shot claim still open. Inside
the live callback, `_issue_authority()` could be called again after the genuine
permit was spent, or a fully bound permit could be assigned to the integration
point's `_authority` registration, and a second armed executor then reached the
plan under the same durable start. Both reproductions are kept below. Section
3b adds the controls: issuance refuses when no invocation is running, when it is
offered anything but that invocation, and a second time before or after the
spend; a replaced registration refuses even the genuine authority; writing back
every ordinary attribute of the reachable object graph does not re-arm a spent
one; and the end of the work — by return, exception or interruption — revokes it
while the invocation is still on the stack.

## What is not claimed

**Python provides no language-level secrecy and nothing here pretends it
does.** `_PERMIT_GRANT` can be read, `_grant_permit` can be called and
`EffectPermit` can be constructed with any field values a caller likes. The
tests below construct all three. What they prove is that a reconstructed object
carries none of the **live** state the executor consults, and that an object
which once carried it carries it no longer.

## What it is not

Nothing here provisions anything, starts a process, reaches a database or
observes `oracle-test`. Every path is under `tmp_path`, `is_executable` stays
`False` and `REAL_EXECUTION_REFUSAL` stands.
"""
from __future__ import annotations

import enum

import pytest

from tests.phase_5_0_evidence.harness_fixtures import (
    runnable_plan,
    supply_reviewed_e7_facts,
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
from tools.phase_5_0_evidence import case_runtime
from tools.phase_5_0_evidence.approved_target import CONFIRMATION_TOKEN
from tools.phase_5_0_evidence.durability_model import Quiescence
from tools.phase_5_0_evidence.execution import participants as participants_module
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
)
from tools.phase_5_0_evidence.execution.host_lock import LaboratorySession
from tools.phase_5_0_evidence.execution.materializer import RecordingMaterializer
from tools.phase_5_0_evidence.execution.participants import (
    PARTICIPANT_AUTHORITY_NOT_LIVE,
    EffectPermit,
    HarnessObservations,
    ParticipantIntegration,
    ParticipantRefused,
)
from tools.phase_5_0_evidence.lifecycle_storage import (
    PARTICIPANT_PROFILES,
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

SOURCES = {name: f"# {name}\n".encode("utf-8") for name in COVERED_SOURCES}

REVIEWED_INTERPRETER_DIGEST = "5" * 64
REVIEWED_INTERPRETER_REAL_PATH = "/opt/fb-reviewed/python3.12"

RESERVATION = "RES-LABI-R2"
RUN_ID = "RUN-LABI-R2"
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


def _initialized(tmp_path):
    """A laboratory whose reservation record admits a successor."""
    lab = build_laboratory(tmp_path)
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


def _integration(lab, *, reservation_id: str = RESERVATION) -> ParticipantIntegration:
    return ParticipantIntegration(
        participant=Participant.HARNESS_CLI,
        host=HOST,
        target_identity=TARGET_IDENTITY,
        author="the harness",
        at=AT,
        layout=lab.layout,
        reservation_id=reservation_id,
        wait_for_lock=False,
    )


def _request(*, reservation_id: str = RESERVATION) -> ReservationRequest:
    return ReservationRequest(
        reservation_id=reservation_id,
        owner=OBSERVER,
        host=HOST,
        target_identity=TARGET_IDENTITY,
        requested_at=AT,
        deadline="2026-09-13T20:00:00Z",
        recovery_owner=OBSERVER,
        real_execution=False,
    )


def _clean_observations() -> HarnessObservations:
    return HarnessObservations(
        residue=ResidueObservation.empty(observed_by=OBSERVER, searched_at=AT),
        configuration_restored=True,
        child_processes_ended=True,
        database_transactions_settled=True,
    )


class _ArmedRun:
    """A real executor holding a **real**, armed descriptor-bound effect issuer.

    The guard is a type check rather than an attribute lookup, so a duck-typed
    double must not be able to satisfy or to trip it. The issuer is never asked
    to issue anything: every refusal below happens before the first step, and
    the assertions say so by reading the boundary, the materializer and the
    issuer's own record of what it created.
    """

    def __init__(
        self,
        *,
        session,
        permit,
        run_id: str = RUN_ID,
        reservation_id: str = RESERVATION,
    ) -> None:
        self.inventory = DescriptorInventory()
        self.effects = DescriptorBoundEffects(
            inventory=self.inventory,
            filesystem=PosixFilesystem(self.inventory),
            armed=True,
        )
        plan = runnable_plan()
        self.runner = ExecutingRunner(
            plan=plan,
            boundary=RecordingBoundary(),
            materializer=RecordingMaterializer(),
            effects=self.effects,
            reviewed_digest=ReviewManifest.build(plan, SOURCES).digest(),
            confirmation_token=CONFIRMATION_TOKEN,
            source_bytes=dict(SOURCES),
            run_id=run_id,
            reservation_id=reservation_id,
            session=session,
            permit=permit,
        )

    def close(self) -> None:
        self.inventory.close()

    def reached_nothing(self) -> None:
        """No command, no materialization and no descriptor-bound object."""
        assert self.runner.boundary.calls == []
        assert self.runner.materializer.requests == []
        assert self.effects._recorded == {}


def _refuses(*, session, permit, run_id: str = RUN_ID, reservation_id=RESERVATION):
    """Drive an armed executor, require a refusal, and prove nothing was reached."""
    armed = _ArmedRun(
        session=session,
        permit=permit,
        run_id=run_id,
        reservation_id=reservation_id,
    )
    try:
        with pytest.raises(ExecutorRefused) as refusal:
            armed.runner.execute()
        armed.reached_nothing()
        return str(refusal.value)
    finally:
        armed.close()


def _run_file(lab, run_id: str = RUN_ID):
    return lab.runs_directory / run_id


def _stored_state(lab, run_id: str = RUN_ID):
    bound = bind(lab)
    try:
        return bound.ledger.read_run(run_id)
    finally:
        bound.close()


def _record_entries(lab):
    bound = bind(lab)
    try:
        parsed = bound.record.read()
        assert parsed.ok, parsed.reasons
        return tuple(entry.kind for entry in parsed.entries)
    finally:
        bound.close()


def _complete_run(lab, *, run_id: str = RUN_ID, reservation_id: str = RESERVATION):
    """One whole successful harness pass, returning the permit its work kept.

    This is reproduction B's first half: a genuinely issued permit, retained by
    the callback that received it and handed back after `run_harness()` has
    published both terminal entries and released the lock.
    """
    kept: list[EffectPermit] = []
    integration = _integration(lab, reservation_id=reservation_id)

    def work(permit: EffectPermit) -> HarnessObservations:
        kept.append(permit)
        return _clean_observations()

    harness = integration.run_harness(
        run_id=run_id,
        work=work,
        request=_request(reservation_id=reservation_id),
        observed_by=OBSERVER,
    )
    assert harness.released is True
    assert harness.run.completed is True
    assert kept and kept[0].issued
    return integration, kept[0]


# ---------------------------------------------------------------------------
# 1. Reproduction A — the token is constructible, and it authorizes nothing
# ---------------------------------------------------------------------------


def test_a_permit_built_from_the_module_attributes_authorizes_nothing(
    tmp_path,
) -> None:
    """**Reproduction A, verbatim.** Read the sentinel, build the permit, refuse.

    `_PERMIT_GRANT` is readable, `EffectPermit.grant` is a public field, and the
    object this builds binds the harness participant, this run and this
    reservation exactly. It is still not evidence that a start was published:
    no `ledger.begin()` ran, so there is no live invocation for it to belong to.
    """
    lab = _initialized(tmp_path)
    permit = EffectPermit(
        participant=Participant.HARNESS_CLI,
        run_id=RUN_ID,
        reservation_id=RESERVATION,
        granted=True,
        grant=participants_module._PERMIT_GRANT,
    )

    message = _refuses(session=_integration(lab), permit=permit)
    assert "live" in message

    # Nothing durable was created, because nothing durable was ever begun.
    assert not _run_file(lab).exists()
    assert _record_entries(lab) == (EntryKind.FIRST_USE,)


def test_calling_the_grant_factory_directly_authorizes_nothing(tmp_path) -> None:
    """**Reproduction A, the other half.** `_grant_permit` is importable too.

    A module-private name is a convention. The factory can be called, and what
    it returns without a durable start is an object with the right fields and
    no live invocation behind it.
    """
    lab = _initialized(tmp_path)
    permit = participants_module._grant_permit(
        participant=Participant.HARNESS_CLI,
        run_id=RUN_ID,
        reservation_id=RESERVATION,
    )
    assert permit.issued is True
    assert permit.binds(
        participant=Participant.HARNESS_CLI,
        run_id=RUN_ID,
        reservation_id=RESERVATION,
    )

    message = _refuses(session=_integration(lab), permit=permit)
    assert "live" in message
    assert not _run_file(lab).exists()


# ---------------------------------------------------------------------------
# 2. Reproduction B — a genuine permit is not replayable
# ---------------------------------------------------------------------------


def test_a_retained_permit_refuses_against_its_own_closed_integration(
    tmp_path,
) -> None:
    """**Reproduction B, verbatim.** The permit the work kept, used afterwards.

    `run_harness()` has published both terminal entries and released the lock.
    The permit is the genuine one, the integration point is the one that issued
    it, and the pair authorizes nothing: T9 may only happen while the lock is
    held and the run is in progress, and neither is true any more.
    """
    lab = _initialized(tmp_path)
    integration, permit = _complete_run(lab)
    before = _run_file(lab).read_bytes()

    message = _refuses(session=integration, permit=permit)
    assert "live" in message

    # The completed durable state is exactly as the successful run left it.
    assert _run_file(lab).read_bytes() == before
    assert _stored_state(lab).state.phase is RunPhase.COMPLETED
    assert _record_entries(lab)[-1] is EntryKind.RELEASED


def test_a_retained_permit_refuses_against_an_equivalent_new_integration(
    tmp_path,
) -> None:
    """**Reproduction B, the harder half.** Equal fields are not the same object.

    A freshly constructed `ParticipantIntegration` carries the same participant,
    host, target and reservation as the one that ran. Every value the old guard
    compared agrees. It has held no lock and published no start, and an
    authority that was issued to another invocation does not transfer to it.
    """
    lab = _initialized(tmp_path)
    _integration_that_ran, permit = _complete_run(lab)
    twin = _integration(lab)
    assert twin.participant is _integration_that_ran.participant
    assert twin.reservation_id == _integration_that_ran.reservation_id
    before = _run_file(lab).read_bytes()

    message = _refuses(session=twin, permit=permit)
    assert "live" in message
    assert _run_file(lab).read_bytes() == before


def test_a_retained_permit_refuses_after_the_stored_run_is_completed(
    tmp_path,
) -> None:
    """The stored run settled, and the integration point is opened again.

    An adversary with module access can reopen the integration point: the
    reservation was released, so a successor is admitted and a new session
    holds the lock. The retained permit still authorizes nothing — it belongs
    to an invocation that ended, and the run it names is no longer in progress.
    """
    lab = _initialized(tmp_path)
    integration, permit = _complete_run(lab)
    assert _stored_state(lab).state.phase is RunPhase.COMPLETED

    session = integration._open()  # a live session, held lock, wrong moment
    try:
        assert session.holds_lock is True
        message = _refuses(session=integration, permit=permit)
        assert "live" in message
    finally:
        integration.close()


def test_a_retained_permit_refuses_after_an_attributed_recovery(tmp_path) -> None:
    """Replay after the run was recovered rather than completed.

    The work raised, so the durable start is unsettled; an operator publishes an
    attributed `participant_recovered` entry for it. The retained permit names a
    run that is recovered, not in progress, and the executor refuses.
    """
    lab = _initialized(tmp_path)
    kept: list[EffectPermit] = []
    integration = _integration(lab)

    def work(permit: EffectPermit) -> HarnessObservations:
        kept.append(permit)
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        integration.run_harness(
            run_id=RUN_ID, work=work, request=_request(), observed_by=OBSERVER
        )
    assert _stored_state(lab).state.phase is RunPhase.IN_PROGRESS

    recovery = _integration(lab).recover(
        run_id=RUN_ID, reference="INC-LABI-R2 operator recovery"
    )
    assert recovery.published, recovery.reasons
    assert _stored_state(lab).state.phase is RunPhase.RECOVERED
    before = _run_file(lab).read_bytes()

    message = _refuses(session=integration, permit=kept[0])
    assert "live" in message
    assert _run_file(lab).read_bytes() == before


def test_a_retained_permit_refuses_once_its_own_invocation_has_returned(
    tmp_path,
) -> None:
    """**The revocation conjunct.** Every durable fact still holds, and it refuses.

    The work raised, so the run is still `participant_started`, the reservation
    record still says `running`, and the very session object the authority was
    issued over can be opened again. The only thing that changed is that the
    invocation the authority belonged to has returned — and that alone is
    enough, because authority is scoped to the synchronous call, not to the
    state that happened to surround it.
    """
    lab = _initialized(tmp_path)
    kept: list[EffectPermit] = []
    sessions: list[object] = []
    integration = _integration(lab)

    def work(permit: EffectPermit) -> HarnessObservations:
        kept.append(permit)
        sessions.append(integration._session)
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        integration.run_harness(
            run_id=RUN_ID, work=work, request=_request(), observed_by=OBSERVER
        )

    # Put the exact session back, holding the lock again, with the durable
    # state untouched: in progress, bound to this reservation, record running.
    session = sessions[0]
    session.open()
    integration._session = session
    try:
        assert session.holds_lock is True
        assert _stored_state(lab).state.phase is RunPhase.IN_PROGRESS
        assert _record_entries(lab)[-1] is EntryKind.RUNNING
        message = _refuses(session=integration, permit=kept[0])
        assert "live" in message
    finally:
        integration.close()


# ---------------------------------------------------------------------------
# 3. Inside the live invocation — one conjunct removed at a time
# ---------------------------------------------------------------------------


def _inside_the_work(lab, perturb, *, run_id: str = RUN_ID):
    """Drive the armed executor from **inside** the one live work invocation.

    Everything the protocol requires is genuinely true when the callback is
    entered — the lock is held, the start is durable, the reservation is
    running — and `perturb` removes exactly one of those before the executor is
    driven. The message the executor refused with is returned, so each test can
    name the conjunct that caught it.
    """
    messages: list[str] = []
    integration = _integration(lab)

    def durable_bytes() -> bytes | None:
        path = _run_file(lab, run_id)
        return path.read_bytes() if path.exists() else None

    def work(permit: EffectPermit) -> HarnessObservations:
        perturb(integration, integration._session)
        before = durable_bytes()
        messages.append(_refuses(session=integration, permit=permit, run_id=run_id))
        # A refused executor writes nothing, in the ledger or anywhere else.
        assert durable_bytes() == before
        return _clean_observations()

    try:
        integration.run_harness(
            run_id=run_id, work=work, request=_request(), observed_by=OBSERVER
        )
    except Exception:  # the perturbed tail may refuse; the executor is the subject
        pass
    finally:
        integration.close()
    assert messages, "the work was never reached"
    return messages[0]


def test_a_closed_session_inside_the_work_reaches_no_effect(tmp_path) -> None:
    """**One conjunct.** The integration point must own an **open** session."""
    lab = _initialized(tmp_path)
    message = _inside_the_work(lab, lambda integration, session: integration.close())
    assert "open session" in message


def test_a_reopened_session_inside_the_work_reaches_no_effect(tmp_path) -> None:
    """**One conjunct.** It must be the session the authority was issued over.

    The callback drops the cooperative lock and takes it again. Every value
    agrees afterwards — the integration point is the same object, it owns an
    open session, that session holds the lock, and the durable state is
    untouched. In the gap the lock was **free**, so another participant may have
    run between T8 and T9, and the authority is not authority over a different
    hold.
    """
    lab = _initialized(tmp_path)

    def drop_and_retake_the_lock(integration, session) -> None:
        integration.close()
        reopened = integration._open()
        assert reopened is not session
        assert reopened.holds_lock is True

    message = _inside_the_work(lab, drop_and_retake_the_lock)
    assert "open session" in message


def test_a_released_lock_inside_the_work_reaches_no_effect(tmp_path) -> None:
    """**One conjunct.** The session must still be **holding** the lock.

    The session object is still there and still carries its record and its
    ledger. `flock(2)` was released, so another participant could already be
    running, and r6 §5.7 puts T9 strictly inside the hold.
    """
    lab = _initialized(tmp_path)

    def release_the_lock(integration, session) -> None:
        session._lock.release()
        assert session.holds_lock is False

    message = _inside_the_work(lab, release_the_lock)
    assert "cooperative lock" in message


def test_an_absent_stored_run_inside_the_work_reaches_no_effect(tmp_path) -> None:
    """**One conjunct.** The durable start must still be there to be read."""
    lab = _initialized(tmp_path)

    def remove_the_run_file(integration, session) -> None:
        _run_file(lab).unlink()

    message = _inside_the_work(lab, remove_the_run_file)
    assert "stored run" in message


def test_an_unreadable_stored_run_inside_the_work_reaches_no_effect(
    tmp_path,
) -> None:
    """**One conjunct.** A run file that will not parse is not a run in progress."""
    lab = _initialized(tmp_path)

    def corrupt_the_run_file(integration, session) -> None:
        _run_file(lab).write_bytes(b"not a participant run history\n")

    message = _inside_the_work(lab, corrupt_the_run_file)
    assert "stored run" in message


def test_a_wrong_participant_stored_run_reaches_no_effect(tmp_path) -> None:
    """**One conjunct.** The stored start must be the **harness's** own.

    The file under this run's name is replaced with a valid web-suite start. It
    parses, it validates, it is in progress — and it is another participant's
    accounting, so it does not account for the executor's effects.
    """
    lab = _initialized(tmp_path)

    def restart_as_the_web_suite(integration, session) -> None:
        _run_file(lab).unlink()
        bound = bind(lab)
        try:
            published = bound.ledger.begin(
                run_id=RUN_ID,
                participant=Participant.WEB_SUITE,
                author="the web suite",
                at=AT,
                reservation_id="",
            )
            assert published.published, published.reasons
        finally:
            bound.close()

    message = _inside_the_work(lab, restart_as_the_web_suite)
    assert "another participant" in message


def test_a_differently_bound_stored_run_reaches_no_effect(tmp_path) -> None:
    """**One conjunct.** The stored start must own **this** reservation.

    A valid harness start for another reservation is still a durable start; it
    is another reservation's, and r6 §5.11.1's P7 binding is equality both ways.
    """
    lab = _initialized(tmp_path)

    def restart_for_another_reservation(integration, session) -> None:
        _run_file(lab).unlink()
        bound = bind(lab)
        try:
            published = bound.ledger.begin(
                run_id=RUN_ID,
                participant=Participant.HARNESS_CLI,
                author="the harness",
                at=AT,
                reservation_id="RES-SOMEBODY-ELSE",
            )
            assert published.published, published.reasons
        finally:
            bound.close()

    message = _inside_the_work(lab, restart_for_another_reservation)
    assert "another reservation" in message


def test_a_settled_stored_run_inside_the_work_reaches_no_effect(tmp_path) -> None:
    """**One conjunct.** The stored run must still be **in progress**.

    An attributed recovery is published for this very run while the work holds
    the lock. The run is now recovered rather than started, and a recovered run
    is one an operator has already accounted for.
    """
    lab = _initialized(tmp_path)

    def recover_the_run(integration, session) -> None:
        published = session.ledger.recover(
            run_id=RUN_ID,
            participant=Participant.HARNESS_CLI,
            reference="INC-LABI-R2 operator recovery",
            author="the harness",
            at=AT,
        )
        assert published.published, published.reasons

    message = _inside_the_work(lab, recover_the_run)
    assert "in progress" in message


def test_a_reservation_that_is_not_running_reaches_no_effect(tmp_path) -> None:
    """**One conjunct.** The record must be in its T8 `running` state.

    The reservation is quarantined while the work holds the lock. The ledger
    still says the run is in progress, so only the reservation-state conjunct
    can catch this — and r6 §5.7 puts T9 after T8 and before T11.
    """
    lab = _initialized(tmp_path)

    def quarantine_the_reservation(integration, session) -> None:
        published = session.record.quarantine(
            reservation_id=RESERVATION,
            reason="an operator quarantined the host mid-run",
            author="the harness",
            at=AT,
        )
        assert published.published, published.reasons

    message = _inside_the_work(lab, quarantine_the_reservation)
    assert "running state" in message


def test_the_same_live_authority_cannot_be_consumed_twice(tmp_path) -> None:
    """**One conjunct.** One durable start, one executor, one set of effects.

    The first armed executor is driven and spends the authority. A second armed
    executor, in the same live invocation, with the same genuine permit and the
    same integration point, is refused: a second consumption would be a second
    run of the reviewed effects under one accounting entry.
    """
    lab = _initialized(tmp_path)
    reached: list[int] = []
    messages: list[str] = []
    integration = _integration(lab)

    def work(permit: EffectPermit) -> HarnessObservations:
        first = _ArmedRun(session=integration, permit=permit)
        try:
            first.runner.execute()
            reached.append(len(first.runner.boundary.calls))
        finally:
            first.close()
        messages.append(_refuses(session=integration, permit=permit))
        return _clean_observations()

    integration.run_harness(
        run_id=RUN_ID, work=work, request=_request(), observed_by=OBSERVER
    )
    assert reached and reached[0] > 0, "the first executor must reach the plan"
    assert "live" in messages[0]


def test_the_live_invocation_cannot_issue_a_second_authority(tmp_path) -> None:
    """A spent authority must not be replaceable under the same T6--T8 state.

    The integration object and its session remain reachable from the callback.
    Calling the integration's issuing path again must not turn one durable start
    into authority for a second execution.
    """
    lab = _initialized(tmp_path)
    integration = _integration(lab)

    def work(permit: EffectPermit) -> HarnessObservations:
        first = _ArmedRun(session=integration, permit=permit)
        try:
            first.runner.execute()
            assert first.runner.boundary.calls
        finally:
            first.close()

        # **C-P5.0-LAB-I-R2 — the one edit to this reproduction.** Issuance is
        # a single transition of the invocation, so the same call with the same
        # arguments now refuses *at issuance*, before a permit is constructed or
        # registered, instead of returning a replacement for the executor to
        # refuse. The attack is unchanged. A second armed executor is still
        # driven under the same start, with the only permit the callback holds.
        with pytest.raises(ParticipantRefused) as refused:
            integration._issue_authority(
                integration._session,
                run_id=RUN_ID,
                reservation_id=RESERVATION,
            )
        assert refused.value.classification == PARTICIPANT_AUTHORITY_NOT_LIVE
        assert integration._authority is permit
        second = _ArmedRun(session=integration, permit=permit)
        try:
            with pytest.raises(ExecutorRefused):
                second.runner.execute()
            second.reached_nothing()
        finally:
            second.close()
        return _clean_observations()

    integration.run_harness(
        run_id=RUN_ID, work=work, request=_request(), observed_by=OBSERVER
    )


def test_the_live_registration_cannot_be_replaced_by_mutable_state(tmp_path) -> None:
    """Writing the documented live-state fields must not mint authority."""
    lab = _initialized(tmp_path)
    integration = _integration(lab)

    def work(original: EffectPermit) -> HarnessObservations:
        replacement = participants_module._grant_permit(
            participant=Participant.HARNESS_CLI,
            run_id=RUN_ID,
            reservation_id=RESERVATION,
            issuer=integration,
            session=integration._session,
        )
        integration._authority = replacement
        armed = _ArmedRun(session=integration, permit=replacement)
        try:
            with pytest.raises(ExecutorRefused):
                armed.runner.execute()
            armed.reached_nothing()
        finally:
            armed.close()
        return _clean_observations()

    integration.run_harness(
        run_id=RUN_ID, work=work, request=_request(), observed_by=OBSERVER
    )


# ---------------------------------------------------------------------------
# 3b. One issuance and one consumption per invocation — PR-20260914-LABI-R2-1
# ---------------------------------------------------------------------------


def _armed_reaches_the_plan(integration, permit) -> None:
    """One armed executor that must be **allowed**, and must reach the plan."""
    armed = _ArmedRun(session=integration, permit=permit)
    try:
        armed.runner.execute()
        assert armed.runner.boundary.calls, "the genuine authority must reach the plan"
    finally:
        armed.close()


def _start_by_hand(integration):
    """T2, T6, T7 and T8 genuinely performed — but **outside** `run_harness`."""
    session = integration._open()
    begun = session.ledger.begin(
        run_id=RUN_ID,
        participant=Participant.HARNESS_CLI,
        author="the harness",
        at=AT,
        reservation_id=RESERVATION,
    )
    assert begun.published, begun.reasons
    admitted = session.record.admit_reservation(
        reservation_id=RESERVATION, author="the harness", at=AT
    )
    assert admitted.published, admitted.reasons
    running = session.record.start_running(
        reservation_id=RESERVATION, author="the harness", at=AT
    )
    assert running.published, running.reasons
    return session


def test_issuance_outside_a_live_invocation_refuses_and_registers_nothing(
    tmp_path,
) -> None:
    """**Issuance, absent invocation.** Every durable fact holds; no call is running.

    The lock is held, the start is durable and the record says `running`, all
    genuinely published. What is missing is the work invocation itself, and
    issuance is a transition *of* an invocation: it refuses before a permit is
    constructed or registered. A bound permit assigned to the registration by
    hand is no invocation's either.
    """
    lab = _initialized(tmp_path)
    integration = _integration(lab)
    session = _start_by_hand(integration)
    try:
        assert session.holds_lock is True
        assert _stored_state(lab).state.phase is RunPhase.IN_PROGRESS
        assert _record_entries(lab)[-1] is EntryKind.RUNNING

        with pytest.raises(ParticipantRefused) as refused:
            integration._issue_authority(
                session, run_id=RUN_ID, reservation_id=RESERVATION
            )
        assert refused.value.classification == PARTICIPANT_AUTHORITY_NOT_LIVE
        assert integration._authority is None

        forged = participants_module._grant_permit(
            participant=Participant.HARNESS_CLI,
            run_id=RUN_ID,
            reservation_id=RESERVATION,
            issuer=integration,
            session=session,
        )
        integration._authority = forged
        before = _run_file(lab).read_bytes()
        assert "live" in _refuses(session=integration, permit=forged)
        assert _run_file(lab).read_bytes() == before
    finally:
        integration.close()


@pytest.mark.parametrize(
    "wrong",
    ["another integration point", "another session", "another run", "another reservation"],
)
def test_issuance_bound_to_anything_but_the_live_invocation_refuses(
    tmp_path, wrong
) -> None:
    """**Issuance, wrong invocation.** Nothing is registered, anywhere.

    Each row offers the issuing path something other than the invocation that is
    running: an equal-looking twin integration point, a session that is not the
    invocation's, or another run or reservation. Each refuses, the twin
    registers nothing, and the genuine authority is untouched and still reaches
    the plan exactly once.
    """
    lab = _initialized(tmp_path)
    integration = _integration(lab)
    twin = _integration(lab)
    reached: list[str] = []

    def work(permit: EffectPermit) -> HarnessObservations:
        issuer = integration
        offered = integration._session
        keywords = {"run_id": RUN_ID, "reservation_id": RESERVATION}
        if wrong == "another integration point":
            issuer = twin
        elif wrong == "another session":
            offered = lab.session(reservation_id=RESERVATION)
        elif wrong == "another run":
            keywords["run_id"] = "RUN-LABI-R2-OTHER"
        else:
            keywords["reservation_id"] = "RES-LABI-R2-OTHER"

        with pytest.raises(ParticipantRefused) as refused:
            issuer._issue_authority(offered, **keywords)
        assert refused.value.classification == PARTICIPANT_AUTHORITY_NOT_LIVE
        assert twin._authority is None
        assert integration._authority is permit

        _armed_reaches_the_plan(integration, permit)
        reached.append(_refuses(session=integration, permit=permit))
        return _clean_observations()

    integration.run_harness(
        run_id=RUN_ID, work=work, request=_request(), observed_by=OBSERVER
    )
    assert reached and "live" in reached[0]


@pytest.mark.parametrize("wrong", ["session", "run", "reservation"])
def test_a_first_issuance_bound_to_anything_but_its_invocation_refuses(
    tmp_path, wrong
) -> None:
    """**Issuance, wrong state before the first issue.** The record's own check.

    Inside `run_harness` the record reaches `OPEN` only for the issuance that
    method performs with its own facts, so the binding comparison is exercised
    here on the record directly: an `OPEN` record offered another session, run
    or reservation refuses, constructs nothing and stays issuable. The record is
    not reachable from any running invocation's callback, and one built by a test
    lives in no frame, so it grants nothing an executor would accept.
    """
    lab = _initialized(tmp_path)
    integration = _integration(lab)
    session = integration._open()
    try:
        record = participants_module._WorkInvocation(
            integration=integration,
            session=session,
            run_id=RUN_ID,
            reservation_id=RESERVATION,
        )
        offered = {"session": session, "run_id": RUN_ID, "reservation_id": RESERVATION}
        if wrong == "session":
            offered["session"] = lab.session(reservation_id=RESERVATION)
        elif wrong == "run":
            offered["run_id"] = "RUN-LABI-R2-OTHER"
        else:
            offered["reservation_id"] = "RES-LABI-R2-OTHER"

        with pytest.raises(ParticipantRefused) as refused:
            record.issue(**offered)
        assert refused.value.classification == PARTICIPANT_AUTHORITY_NOT_LIVE
        assert not record.owns(EffectPermit(participant=Participant.HARNESS_CLI, run_id=RUN_ID))

        issued = record.issue(session=session, run_id=RUN_ID, reservation_id=RESERVATION)
        assert record.owns(issued)
        assert integration._authority is None
    finally:
        integration.close()


def test_a_second_issuance_before_consumption_refuses_and_the_first_is_spent_once(
    tmp_path,
) -> None:
    """**Issuance-once, before the spend.** The regression for that control.

    The genuine authority has been issued and not yet consumed. A second issuance
    refuses and leaves the registration exactly as it was; the genuine authority
    then reaches the plan once, and a second consumption of it refuses.
    """
    lab = _initialized(tmp_path)
    integration = _integration(lab)
    second: list[str] = []

    def work(permit: EffectPermit) -> HarnessObservations:
        with pytest.raises(ParticipantRefused) as refused:
            integration._issue_authority(
                integration._session, run_id=RUN_ID, reservation_id=RESERVATION
            )
        assert refused.value.classification == PARTICIPANT_AUTHORITY_NOT_LIVE
        assert integration._authority is permit

        _armed_reaches_the_plan(integration, permit)
        second.append(_refuses(session=integration, permit=permit))
        return _clean_observations()

    harness = integration.run_harness(
        run_id=RUN_ID, work=work, request=_request(), observed_by=OBSERVER
    )
    assert second and "live" in second[0]
    assert harness.released is True


@pytest.mark.parametrize("registration", ["cleared", "a bound constructed permit"])
def test_a_replaced_registration_refuses_even_the_genuine_authority(
    tmp_path, registration
) -> None:
    """**Registration integrity, the other direction.** Tampering fails closed.

    The genuine, unspent permit is offered, inside its own invocation, after the
    callback overwrote the integration point's registration. Consumption requires
    the registration, the invocation's record and the permit to be one object, so
    a registration nobody issued refuses even the authority that was issued.
    """
    lab = _initialized(tmp_path)
    integration = _integration(lab)
    messages: list[str] = []

    def work(permit: EffectPermit) -> HarnessObservations:
        if registration == "cleared":
            integration._authority = None
        else:
            integration._authority = participants_module._grant_permit(
                participant=Participant.HARNESS_CLI,
                run_id=RUN_ID,
                reservation_id=RESERVATION,
                issuer=integration,
                session=integration._session,
            )
        before = _run_file(lab).read_bytes()
        messages.append(_refuses(session=integration, permit=permit))
        assert _run_file(lab).read_bytes() == before
        return _clean_observations()

    integration.run_harness(
        run_id=RUN_ID, work=work, request=_request(), observed_by=OBSERVER
    )
    assert messages and "live" in messages[0]


def _reachable_attributes(*roots) -> list[tuple[object, dict[str, object]]]:
    """Every ordinary attribute of every package object reachable from `roots`.

    Slots and `__dict__` entries, followed transitively through objects defined
    in `tools.phase_5_0_evidence`. This is the callback's object graph as the
    re-review defined it: what ordinary attribute reads reach, without frames,
    closures, `gc` or code objects.
    """
    found: dict[int, tuple[object, dict[str, object]]] = {}
    pending = list(roots)
    while pending:
        candidate = pending.pop()
        kind = type(candidate)
        if (
            id(candidate) in found
            or isinstance(candidate, (type, enum.Enum))
            or not kind.__module__.startswith("tools.phase_5_0_evidence")
        ):
            continue
        values: dict[str, object] = {}
        for klass in kind.__mro__:
            slots = getattr(klass, "__slots__", ())
            for name in (slots,) if isinstance(slots, str) else slots:
                try:
                    values[name] = object.__getattribute__(candidate, name)
                except AttributeError:
                    continue
        values.update(getattr(candidate, "__dict__", {}))
        found[id(candidate)] = (candidate, values)
        pending.extend(values.values())
    return list(found.values())


def test_restoring_every_reachable_attribute_does_not_re_arm_a_spent_authority(
    tmp_path,
) -> None:
    """**Invocation ownership.** The spend is not a fact about the object graph.

    At issuance the callback records every ordinary attribute of every object it
    can reach from the permit and the integration point — the registration, the
    session, the lock, the record, the ledger and the permit itself. It spends the
    authority, writes **every one of those attributes back** with
    `object.__setattr__`, and drives a second armed executor. It refuses, because
    the spend was recorded in state none of those attributes holds.
    """
    lab = _initialized(tmp_path)
    integration = _integration(lab)
    messages: list[str] = []

    def work(permit: EffectPermit) -> HarnessObservations:
        snapshot = _reachable_attributes(permit, integration)
        assert any(candidate is integration for candidate, _ in snapshot)
        assert any(candidate is integration._session for candidate, _ in snapshot)

        _armed_reaches_the_plan(integration, permit)
        for candidate, values in snapshot:
            for name, value in values.items():
                object.__setattr__(candidate, name, value)

        messages.append(_refuses(session=integration, permit=permit))
        return _clean_observations()

    integration.run_harness(
        run_id=RUN_ID, work=work, request=_request(), observed_by=OBSERVER
    )
    assert messages and "live" in messages[0]


class _SessionWithAHook(LaboratorySession):
    """A real session that runs one test action at its first use after the work.

    The action is armed by the work immediately before it returns or raises, and
    it fires at the next `record` access or at `close()`, whichever comes first —
    both inside `run_harness`, after T9 has ended and before the lock is released.
    """

    def _fire(self) -> None:
        action = self.__dict__.pop("after_work", None)
        if action is not None:
            action()

    @property
    def record(self):
        self._fire()
        return LaboratorySession.record.fget(self)

    def close(self) -> None:
        self._fire()
        LaboratorySession.close(self)


@pytest.mark.parametrize(
    "ending", ["returned", "returned something else", "raised", "interrupted"]
)
def test_the_end_of_the_work_revokes_the_authority_inside_the_invocation(
    tmp_path, ending
) -> None:
    """**Revocation.** Return, exception and interruption each end the authority.

    The retained, **unspent** genuine permit is offered while `run_harness` is
    still on the stack, the same session still holds the lock, the run is still
    in progress and the record still says `running`. Nothing durable has changed;
    only the work has ended. It refuses.
    """
    lab = _initialized(tmp_path)
    hooked: list[LaboratorySession] = []

    def session_factory() -> LaboratorySession:
        hooked.append(
            _SessionWithAHook(
                participant=Participant.HARNESS_CLI,
                host=HOST,
                target_identity=TARGET_IDENTITY,
                read_by="the harness",
                read_at=AT,
                layout=lab.layout,
                reservation_id=RESERVATION,
            )
        )
        return hooked[-1]

    integration = ParticipantIntegration(
        participant=Participant.HARNESS_CLI,
        host=HOST,
        target_identity=TARGET_IDENTITY,
        author="the harness",
        at=AT,
        layout=lab.layout,
        reservation_id=RESERVATION,
        wait_for_lock=False,
        session_factory=session_factory,
    )
    kept: list[EffectPermit] = []
    messages: list[str] = []

    def after_work() -> None:
        session = hooked[0]
        restored = integration._session is None
        if restored:  # `close()` detaches it first; put the same session back
            integration._session = session
        try:
            assert session.holds_lock is True
            assert _stored_state(lab).state.phase is RunPhase.IN_PROGRESS
            assert _record_entries(lab)[-1] is EntryKind.RUNNING
            before = _run_file(lab).read_bytes()
            messages.append(_refuses(session=integration, permit=kept[0]))
            assert _run_file(lab).read_bytes() == before
        finally:
            if restored:
                integration._session = None

    def work(permit: EffectPermit):
        kept.append(permit)
        integration._session.after_work = after_work
        if ending == "returned":
            return _clean_observations()
        if ending == "returned something else":
            return {"not": "observations"}
        if ending == "raised":
            raise RuntimeError("the work failed")
        raise KeyboardInterrupt

    expected = {
        "returned": None,
        "returned something else": ParticipantRefused,
        "raised": RuntimeError,
        "interrupted": KeyboardInterrupt,
    }[ending]
    if expected is None:
        integration.run_harness(
            run_id=RUN_ID, work=work, request=_request(), observed_by=OBSERVER
        )
    else:
        with pytest.raises(expected):
            integration.run_harness(
                run_id=RUN_ID, work=work, request=_request(), observed_by=OBSERVER
            )
    assert messages and "live" in messages[0]


def test_a_non_harness_invocation_issues_once_as_well(tmp_path) -> None:
    """The six share the transition: `run()` issues exactly once too."""
    lab = _initialized(tmp_path)
    suite = ParticipantIntegration(
        participant=Participant.WEB_SUITE,
        host=HOST,
        target_identity=TARGET_IDENTITY,
        author="the web suite",
        at=AT,
        layout=lab.layout,
    )
    conditions = {
        condition: True
        for condition in PARTICIPANT_PROFILES[
            Participant.WEB_SUITE
        ].external_conditions()
    }
    refusals: list[str] = []

    def work(permit: EffectPermit):
        with pytest.raises(ParticipantRefused) as refused:
            suite._issue_authority(
                suite._session, run_id="RUN-WEB-R2", reservation_id=""
            )
        refusals.append(refused.value.classification)
        assert suite._authority is permit
        return conditions

    outcome = suite.run(run_id="RUN-WEB-R2", work=work, observed_by=OBSERVER)
    assert refusals == [PARTICIPANT_AUTHORITY_NOT_LIVE]
    assert outcome.started is True


# ---------------------------------------------------------------------------
# 4. The positive composition — the real thing still runs, exactly once
# ---------------------------------------------------------------------------


def test_the_real_composition_reaches_the_armed_executor_exactly_once(
    tmp_path,
) -> None:
    """**Positive.** A remediation that refused everything would pass §3 too.

    The real `execute_under_reservation` drives a real `ExecutingRunner` holding
    a real armed `DescriptorBoundEffects`. The executor is reached once, between
    T8 and T10a, while the lock is held and the stored run is in progress; the
    durable files read from inside the run say so; and §5.12's two terminal
    halves are published before the lock is released.
    """
    lab = _initialized(tmp_path)
    integration = _integration(lab)
    armed = _ArmedRun(session=integration, permit=None)
    observed: dict[str, object] = {}

    class _Observed:
        """The real runner, with the durable state read at the moment it runs.

        A wrapper rather than a double: `execute()` below is the production
        method, holding the production armed issuer. What is added is the
        reading of the laboratory's own files immediately before it, so the
        ordering assertion is about the run rather than about the source.
        """

        def __init__(self, runner) -> None:
            self.runner = runner

        def accept_permit(self, permit):
            return self.runner.accept_permit(permit)

        def execute(self):
            observed["run_in_progress"] = (
                _stored_state(lab).state.phase is RunPhase.IN_PROGRESS
            )
            observed["record"] = _record_entries(lab)
            observed["lock_held"] = integration._session.holds_lock
            observed["executions"] = int(observed.get("executions", 0)) + 1
            return self.runner.execute()

        def run_observations(self, outcome, *, observed_by, searched_at):
            return self.runner.run_observations(
                outcome, observed_by=observed_by, searched_at=searched_at
            )

    try:
        harness = execute_under_reservation(
            integration=integration,
            runner=_Observed(armed.runner),
            request=_request(),
            run_id=RUN_ID,
            quiescence=Quiescence.verified(observed_by=OBSERVER),
            observed_by=OBSERVER,
            searched_at=AT,
        )
    finally:
        armed.close()

    # T8 had happened and T10a–T12 had not, at the moment the executor ran.
    assert observed["executions"] == 1
    assert observed["run_in_progress"] is True
    assert observed["lock_held"] is True
    assert observed["record"][-1] is EntryKind.RUNNING

    # The armed issuer was genuinely reached: the guard did not refuse.
    assert armed.runner.boundary.calls

    # Both terminal halves, then the lock.
    assert harness.terminal is not None
    assert harness.run.started is True
    assert integration._session is None
    assert _record_entries(lab)[-1] in (
        EntryKind.RELEASED,
        EntryKind.QUARANTINED,
    )


def test_this_suite_builds_over_no_production_path() -> None:
    """Every path is under `tmp_path`; the three production roots are absent."""
    from pathlib import Path

    from tools.phase_5_0_evidence.provisioning import LABORATORY_LAYOUT

    for path in (
        Path(LABORATORY_LAYOUT.lock_path),
        Path(LABORATORY_LAYOUT.laboratory_directory),
        Path(LABORATORY_LAYOUT.recovery_directory),
    ):
        assert not path.exists(), path


def test_the_standing_operational_gates_are_all_still_closed() -> None:
    """Closing a fail-open authority check closes no gate and opens no permission."""
    from tools.phase_5_0_evidence import reservation as reservation_module
    from tools.phase_5_0_evidence.concrete_plan import build_concrete_plan

    plan = build_concrete_plan()
    assert plan.is_executable is False
    assert reservation_module.REAL_EXECUTION_REFUSAL
    assert "C-7" in plan.conflicts()
    assert ReservationState.RUNNING is ReservationState("running")
