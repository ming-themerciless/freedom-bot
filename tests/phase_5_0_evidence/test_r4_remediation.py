"""Transitions, participant binding and terminal order — R4-1, R4-2 and R4-3.

**Every test in this file is a model test.** It exercises
`tools/phase_5_0_evidence/lifecycle_storage.py` over the in-memory
`durability_model.SyntheticFilesystem`. The mechanism those rules describe is
**not built**: there is no privileged mechanism, no real filesystem writer, no
lock adapter and no operational integration, and nothing here creates one. A
passing row establishes that the proposed rule is constructible and falsifiable,
and **nothing** about Linux, about `oracle-test` or about EH-R16-1.

Three properties carry this file, and each was reproduced against the submitted
revision 4 before it was repaired.

* **R4-1** — `test_the_reviewers_stale_release_reproduction` and
  `test_the_reviewers_stale_recovery_reproduction`. A stale terminal entry for a
  finished reservation, appended after a newer `admitted`/`running` pair,
  retired the newer run and admitted a third reservation. It must now refuse at
  the writer *and* at the reader.
* **R4-2** — `test_the_reviewers_cross_participant_completion_reproduction`. A
  web run started as the web suite was completed as the Foundry suite on Foundry
  evidence, and admitted. It must now refuse without touching the web run's
  stored bytes, and every successor must still refuse.
* **R4-3** — `test_the_terminal_publications_have_a_reachable_successful_path`
  and the intermediate-state rows. Revision 4's declared sequence completed the
  harness participant before publishing the release its completion required, so
  no process could obtain its own stated observation.

**Every adversarial history is exercised on both sides.** `plant_record` and
`plant_run` write bytes around the writer, so a history a corrected writer can
no longer produce still reaches a reader — which is the half of each finding
that a writer-only repair would leave open.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

from tools.phase_5_0_evidence.lifecycle_storage import (
    HARNESS_RELEASE_DECIDED,
    HARNESS_RELEASE_PUBLISHED,
    PARTICIPANTS,
    PARTICIPANT_PROFILES,
    TERMINAL_PUBLICATION_ORDER,
    UNIT_TEST_CONSTRUCTORS,
    CompletionEvidence,
    CompletionObservation,
    EntryKind,
    Participant,
    PublicationRefusal,
    RunPhase,
    check_participant_history,
    check_reservation_history,
)
from tools.phase_5_0_evidence.reservation import (
    PredecessorDisposition,
    ReservationState,
)

from tests.phase_5_0_evidence.lifecycle_fixtures import (
    ATTESTER,
    BASIS,
    HOST,
    TARGET,
    Laboratory,
    first_use_entry,
    observed,
    plant_bytes,
    plant_record,
    plant_run,
    reservation_entry,
    run_entry,
)


# ---------------------------------------------------------------------------
# Small builders, so a case reads as the history it is about
# ---------------------------------------------------------------------------


def _admitted(laboratory, sequence, reservation, at="t"):
    return reservation_entry(
        laboratory,
        EntryKind.ADMITTED,
        sequence=sequence,
        author=f"executor {reservation}",
        at=at,
        reservation=reservation,
    )


def _running(laboratory, sequence, reservation, at="t"):
    return reservation_entry(
        laboratory,
        EntryKind.RUNNING,
        sequence=sequence,
        author=f"executor {reservation}",
        at=at,
        reservation=reservation,
    )


def _released(laboratory, sequence, reservation, at="t"):
    return reservation_entry(
        laboratory,
        EntryKind.RELEASED,
        sequence=sequence,
        author=f"executor {reservation}",
        at=at,
        reservation=reservation,
        released_at=at,
    )


def _quarantined(laboratory, sequence, reservation, at="t"):
    return reservation_entry(
        laboratory,
        EntryKind.QUARANTINED,
        sequence=sequence,
        author=f"executor {reservation}",
        at=at,
        reservation=reservation,
        reason="the executor stopped between RUNNING and any release",
    )


def _recovering(laboratory, sequence, reservation, at="t"):
    return reservation_entry(
        laboratory,
        EntryKind.RECOVERING,
        sequence=sequence,
        author=ATTESTER,
        at=at,
        reservation=reservation,
        recovery_owner=ATTESTER,
    )


def _recovered(laboratory, sequence, reservation, at="t", reference="ops-2026-09-11-06"):
    return reservation_entry(
        laboratory,
        EntryKind.OPERATOR_RECOVERED,
        sequence=sequence,
        author=ATTESTER,
        at=at,
        recovers=reservation,
        reference=reference,
    )


def _owned_reservation(participant, reservation):
    """The reservation a participant's start must carry: its own, or nothing.

    **PR-20260911-R5-1.** The six participants whose completion conditions are
    external carry the field empty, and the shape is required in both directions,
    so a parametrized control states it per participant rather than always.
    """
    profile = PARTICIPANT_PROFILES[participant]
    return reservation if profile.lifecycle_owned_conditions else ""


def _started(laboratory, run, participant, **overrides):
    profile = PARTICIPANT_PROFILES[participant]
    return run_entry(
        laboratory,
        EntryKind.PARTICIPANT_STARTED,
        sequence=1,
        run=run,
        participant=participant,
        effects="; ".join(profile.effects),
        **overrides,
    )


def _completed(laboratory, run, participant, *, sequence=2, evidence=None, **overrides):
    profile = PARTICIPANT_PROFILES[participant]
    if evidence is None:
        evidence = CompletionEvidence(
            run_id=run,
            observed_by="the operator, post-run sweep",
            conditions=tuple(profile.completion_conditions),
            reservation_id="RES-1" if profile.lifecycle_owned_conditions else "",
        ).encode()
    return run_entry(
        laboratory,
        EntryKind.PARTICIPANT_COMPLETED,
        sequence=sequence,
        run=run,
        participant=participant,
        evidence=evidence,
        **overrides,
    )


def _recovered_run(laboratory, run, participant, *, sequence=2, reference="ops-1", **overrides):
    return run_entry(
        laboratory,
        EntryKind.PARTICIPANT_RECOVERED,
        sequence=sequence,
        run=run,
        participant=participant,
        author=ATTESTER,
        reference=reference,
        **overrides,
    )


# ---------------------------------------------------------------------------
# R4-1 — the reviewer's two reproductions, at the writer and at the reader
# ---------------------------------------------------------------------------


def test_the_reviewers_stale_release_reproduction():
    """**The exact stored history the R4 review reported.**

    ```text
    FIRST_USE → ADMITTED A → RELEASED A → ADMITTED B → RUNNING B → RELEASED A
    ```

    Before the repair the writer published that entry, the reader took the final
    RELEASED, reported A released, lost the unresolved B and admitted C. Both
    halves are asserted: the append refuses and leaves the bytes intact, and the
    same history planted directly around the writer still refuses on read.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    assert laboratory.append(
        EntryKind.ADMITTED, author="executor A", at="t1", reservation="A"
    ).published is True
    assert laboratory.append(
        EntryKind.RELEASED, author="executor A", at="t2", reservation="A", released_at="t2"
    ).published is True
    assert laboratory.append(
        EntryKind.ADMITTED, author="executor B", at="t3", reservation="B"
    ).published is True
    assert laboratory.append(
        EntryKind.RUNNING, author="executor B", at="t4", reservation="B"
    ).published is True
    before = laboratory.record.read_record_bytes()

    stale = laboratory.append(
        EntryKind.RELEASED, author="executor A", at="t5", reservation="A", released_at="t5"
    )

    assert stale.published is False
    assert stale.refusal is PublicationRefusal.INVALID_HISTORY
    assert any("PR-20260911-R4-1" in reason for reason in stale.reasons)
    # An invalid append leaves the existing bytes exactly as they were.
    assert laboratory.record.read_record_bytes() == before

    # B is still the current reservation and it is still running, so C refuses.
    successor = laboratory.admit(reservation_id="C")
    assert successor.may_proceed is False
    assert successor.history.disposition is PredecessorDisposition.ACTIVE
    assert successor.history.predecessor_id == "B"
    assert successor.history.predecessor_state is ReservationState.RUNNING


def test_the_stale_release_history_refuses_on_read_as_well():
    """The same six entries, planted around the writer, still refuse.

    A corrected writer can no longer produce this history. A record written by an
    earlier revision, or corrupted into this shape, is still readable — so the
    reader carries the same check rather than relying on the writer's.
    """
    laboratory = Laboratory()
    plant_record(
        laboratory,
        (
            first_use_entry(laboratory),
            _admitted(laboratory, 2, "A", at="t1"),
            _released(laboratory, 3, "A", at="t2"),
            _admitted(laboratory, 4, "B", at="t3"),
            _running(laboratory, 5, "B", at="t4"),
            _released(laboratory, 6, "A", at="t5"),
        ),
    )

    admission = laboratory.admit(reservation_id="C")

    assert admission.parsed.ok is True, "the bytes are syntactically valid"
    assert admission.may_proceed is False
    assert admission.history.complete is False
    assert admission.history.disposition is PredecessorDisposition.UNKNOWN
    assert any("PR-20260911-R4-1" in reason for reason in admission.refusals)


def test_the_reviewers_stale_recovery_reproduction():
    """The analogous stale operator-recovery entry, both sides.

    An operator recovery is an attributed addition for the applicable
    quarantined predecessor. Repeating it while a later reservation is running
    is the same defect wearing a different entry kind.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.append(EntryKind.ADMITTED, author="x", at="t1", reservation="A")
    laboratory.append(
        EntryKind.QUARANTINED, author="x", at="t2", reservation="A", reason="crash"
    )
    laboratory.append(
        EntryKind.OPERATOR_RECOVERED,
        author=ATTESTER,
        at="t3",
        recovers="A",
        reference="ops-1",
    )
    laboratory.append(EntryKind.ADMITTED, author="y", at="t4", reservation="B")
    laboratory.append(EntryKind.RUNNING, author="y", at="t5", reservation="B")
    before = laboratory.record.read_record_bytes()

    stale = laboratory.append(
        EntryKind.OPERATOR_RECOVERED,
        author=ATTESTER,
        at="t6",
        recovers="A",
        reference="ops-1",
    )

    assert stale.published is False
    assert stale.refusal is PublicationRefusal.INVALID_HISTORY
    assert laboratory.record.read_record_bytes() == before
    assert laboratory.admit(reservation_id="C").may_proceed is False

    planted = Laboratory()
    plant_record(
        planted,
        (
            first_use_entry(planted),
            _admitted(planted, 2, "A", at="t1"),
            _quarantined(planted, 3, "A", at="t2"),
            _recovered(planted, 4, "A", at="t3"),
            _admitted(planted, 5, "B", at="t4"),
            _running(planted, 6, "B", at="t5"),
            _recovered(planted, 7, "A", at="t6"),
        ),
    )
    admission = planted.admit(reservation_id="C")
    assert admission.parsed.ok is True
    assert admission.may_proceed is False
    assert any(
        "applicable quarantined predecessor" in reason
        for reason in admission.refusals
    )


#: The bounded table-driven audit R4-1 asks for: every illegal stored history,
#: the fragment its refusal must name, and — for the three legal rows — the
#: disposition it must derive. Each row is planted around the writer, so the
#: reader is what is under test.
TRANSITION_AUDIT = (
    (
        "a stale release while a newer reservation runs",
        lambda lab: (
            _admitted(lab, 2, "A"),
            _released(lab, 3, "A"),
            _admitted(lab, 4, "B"),
            _running(lab, 5, "B"),
            _released(lab, 6, "A"),
        ),
        "PR-20260911-R4-1",
        None,
    ),
    (
        "a running entry naming a reservation that is not the current one",
        lambda lab: (
            _admitted(lab, 2, "A"),
            _released(lab, 3, "A"),
            _admitted(lab, 4, "B"),
            _running(lab, 5, "A"),
        ),
        "the current reservation is 'B'",
        None,
    ),
    (
        "a transition after the current reservation released",
        lambda lab: (
            _admitted(lab, 2, "A"),
            _released(lab, 3, "A"),
            _running(lab, 4, "A"),
        ),
        "terminal and names no successor",
        None,
    ),
    (
        "a transition after the current reservation quarantined",
        lambda lab: (
            _admitted(lab, 2, "A"),
            _quarantined(lab, 3, "A"),
            _running(lab, 4, "A"),
        ),
        "terminal and names no successor",
        None,
    ),
    (
        "a duplicate release",
        lambda lab: (
            _admitted(lab, 2, "A"),
            _released(lab, 3, "A"),
            _released(lab, 4, "A"),
        ),
        "duplicate terminal event",
        None,
    ),
    (
        "a duplicate quarantine",
        lambda lab: (
            _admitted(lab, 2, "A"),
            _quarantined(lab, 3, "A"),
            _quarantined(lab, 4, "A"),
        ),
        "duplicate terminal event",
        None,
    ),
    (
        "a repeated operator recovery of the same quarantine",
        lambda lab: (
            _admitted(lab, 2, "A"),
            _quarantined(lab, 3, "A"),
            _recovered(lab, 4, "A"),
            _recovered(lab, 5, "A"),
        ),
        "a second time",
        None,
    ),
    (
        "a terminal identity admitted again",
        lambda lab: (
            _admitted(lab, 2, "A"),
            _released(lab, 3, "A"),
            _admitted(lab, 4, "A"),
        ),
        "already used",
        None,
    ),
    (
        "an admission while the current reservation is admitted",
        lambda lab: (_admitted(lab, 2, "A"), _admitted(lab, 3, "B")),
        "while the current reservation 'A' is 'admitted'",
        None,
    ),
    (
        "an admission over an unrecovered quarantine",
        lambda lab: (
            _admitted(lab, 2, "A"),
            _quarantined(lab, 3, "A"),
            _admitted(lab, 4, "B"),
        ),
        "while the current reservation 'A' is 'quarantined'",
        None,
    ),
    (
        "an admission while the current reservation is recovering",
        lambda lab: (
            _admitted(lab, 2, "A"),
            _recovering(lab, 3, "A"),
            _admitted(lab, 4, "B"),
        ),
        "while the current reservation 'A' is 'recovering'",
        None,
    ),
    (
        "a recovering run moved back to running",
        lambda lab: (
            _admitted(lab, 2, "A"),
            _running(lab, 3, "A"),
            _recovering(lab, 4, "A"),
            _running(lab, 5, "A"),
        ),
        "`reservation.TRANSITIONS` does not contain",
        None,
    ),
    (
        "a running entry for a reservation never admitted",
        lambda lab: (_running(lab, 2, "A"),),
        "which this history never admitted",
        None,
    ),
    (
        "an operator recovery of a reservation never quarantined",
        lambda lab: (_admitted(lab, 2, "A"), _recovered(lab, 3, "A")),
        "applicable quarantined predecessor",
        None,
    ),
    (
        "an operator recovery naming an earlier reservation",
        lambda lab: (
            _admitted(lab, 2, "A"),
            _quarantined(lab, 3, "A"),
            _recovered(lab, 4, "A"),
            _admitted(lab, 5, "B"),
            _quarantined(lab, 6, "B"),
            _recovered(lab, 7, "A"),
        ),
        "applicable quarantined predecessor",
        None,
    ),
    # -- the legal rows. A matrix in which nothing passes tests nothing. -----
    (
        "a first use and no reservation yet",
        lambda lab: (),
        "",
        PredecessorDisposition.VERIFIED_FIRST_USE,
    ),
    (
        "three sequential reservations, each released",
        lambda lab: (
            _admitted(lab, 2, "A"),
            _running(lab, 3, "A"),
            _released(lab, 4, "A"),
            _admitted(lab, 5, "B"),
            _running(lab, 6, "B"),
            _released(lab, 7, "B"),
            _admitted(lab, 8, "C"),
            _running(lab, 9, "C"),
            _released(lab, 10, "C"),
        ),
        "",
        PredecessorDisposition.RELEASED,
    ),
    (
        "a quarantine, its recovery, and a released successor",
        lambda lab: (
            _admitted(lab, 2, "A"),
            _running(lab, 3, "A"),
            _quarantined(lab, 4, "A"),
            _recovered(lab, 5, "A"),
            _admitted(lab, 6, "B"),
            _running(lab, 7, "B"),
            _released(lab, 8, "B"),
        ),
        "",
        PredecessorDisposition.RELEASED,
    ),
    (
        "a quarantine and its recovery, awaiting a new run",
        lambda lab: (
            _admitted(lab, 2, "A"),
            _quarantined(lab, 3, "A"),
            _recovered(lab, 4, "A"),
        ),
        "",
        PredecessorDisposition.OPERATOR_RECOVERED,
    ),
    (
        "an unrecovered quarantine",
        lambda lab: (_admitted(lab, 2, "A"), _quarantined(lab, 3, "A")),
        "",
        PredecessorDisposition.QUARANTINED,
    ),
    (
        "a run that reached its deadline",
        lambda lab: (
            _admitted(lab, 2, "A"),
            _running(lab, 3, "A"),
            _recovering(lab, 4, "A"),
        ),
        "",
        PredecessorDisposition.RECOVERING,
    ),
)


@pytest.mark.parametrize(
    "label, build, expected, disposition",
    TRANSITION_AUDIT,
    ids=[row[0] for row in TRANSITION_AUDIT],
)
def test_the_reservation_transition_audit(label, build, expected, disposition):
    """Every legal and illegal stored reservation history, read from bytes."""
    laboratory = Laboratory()
    plant_record(laboratory, (first_use_entry(laboratory),) + tuple(build(laboratory)))

    admission = laboratory.admit(reservation_id="NEXT")

    assert admission.parsed.ok is True, f"{label}: the bytes must parse"
    if disposition is None:
        assert admission.may_proceed is False, label
        assert admission.history.complete is False, label
        assert any(expected in reason for reason in admission.refusals), (
            label,
            admission.refusals,
        )
        return
    assert admission.history.complete is True, label
    assert admission.history.disposition is disposition, label
    admits = disposition in {
        PredecessorDisposition.VERIFIED_FIRST_USE,
        PredecessorDisposition.RELEASED,
        PredecessorDisposition.OPERATOR_RECOVERED,
    }
    assert admission.may_proceed is admits, (label, admission.refusals)


def test_a_duplicate_terminal_delivery_refuses_explicitly():
    """**The stated policy: duplicate delivery refuses; it is not idempotent.**

    R4-1 permits either an idempotent handling that appends no new terminal event
    and hides no newer run, or an explicit refusal. This model refuses, because
    idempotence here would mean deciding that two entries a reader cannot
    distinguish describe one event — and the record is append-only, so the
    second delivery would either add an entry the first already covers or be
    silently discarded. Neither is a decision a reader should take alone.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.append(EntryKind.ADMITTED, author="x", at="t1", reservation="A")
    first = laboratory.append(
        EntryKind.RELEASED, author="x", at="t2", reservation="A", released_at="t2"
    )
    assert first.published is True
    before = laboratory.record.read_record_bytes()

    again = laboratory.append(
        EntryKind.RELEASED, author="x", at="t2", reservation="A", released_at="t2"
    )

    assert again.published is False
    assert again.refusal is PublicationRefusal.INVALID_HISTORY
    assert any("duplicate terminal event" in reason for reason in again.reasons)
    assert laboratory.record.read_record_bytes() == before
    # The first release still stands, so the next reservation is admitted on it.
    assert laboratory.admit(reservation_id="B").may_proceed is True


def test_the_transition_table_is_the_reservation_modules_own():
    """No second, contradictory transition table is introduced here."""
    laboratory = Laboratory()
    entries = (
        first_use_entry(laboratory),
        _admitted(laboratory, 2, "A"),
        _running(laboratory, 3, "A"),
        _released(laboratory, 4, "A"),
    )

    state = check_reservation_history(entries)

    assert state.ok is True
    assert state.current_id == "A"
    assert state.current_state is ReservationState.RELEASED
    assert state.current_is_recovered is False
    assert state.first_use is entries[0]


# ---------------------------------------------------------------------------
# R4-2 — participant history binding, and the required ledger
# ---------------------------------------------------------------------------


def test_the_reviewers_cross_participant_completion_reproduction():
    """**The exact reproduction the R4 review reported.**

    ```text
    begin web-1 as WEB_SUITE
    complete web-1 as FOUNDRY_TESTS with only Foundry conditions observed
    ```

    Foundry completion does not observe the web suite's database backends or
    fixture cleanup. Before the repair the completion published and admission
    returned True with an unfinished web run outstanding.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    assert laboratory.ledger.begin(
        run_id="web-1", participant=Participant.WEB_SUITE, author="ubuntu", at="t1"
    ).published is True
    before = laboratory.ledger.survey()
    assert before.unsettled == ("web-1",)
    assert laboratory.admit(reservation_id="RES-1").may_proceed is False

    wrong = laboratory.ledger.complete(
        run_id="web-1",
        participant=Participant.FOUNDRY_TESTS,
        author="ubuntu",
        at="t2",
        observation=observed(Participant.FOUNDRY_TESTS),
    )

    assert wrong.published is False
    assert wrong.refusal is PublicationRefusal.INVALID_HISTORY
    assert any("PR-20260911-R4-2" in reason for reason in wrong.reasons)

    # The web run's stored history is untouched and every successor still refuses.
    after = laboratory.ledger.survey()
    assert after.unsettled == ("web-1",)
    assert after.completed == ()
    for successor in PARTICIPANTS:
        refused = laboratory.admit(participant=successor, reservation_id="RES-1")
        assert refused.may_proceed is False, successor
        assert refused.runs.unsettled == ("web-1",), successor


def test_a_terminal_run_file_with_no_start_refuses_on_read():
    """The reader's half: a lone completion entry is not a settled run.

    A corrected writer cannot produce this file — `begin` is the only exclusive
    creator and `complete` appends to what it read — so it is planted directly.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    plant_run(
        laboratory,
        "orphan-1",
        (_completed(laboratory, "orphan-1", Participant.WEB_SUITE, sequence=1),),
    )

    survey = laboratory.ledger.survey()

    assert survey.settled is False
    assert survey.invalid == ("orphan-1",)
    assert survey.completed == ()
    assert any("no start" in reason for reason in survey.reasons)
    assert laboratory.admit(reservation_id="RES-1").may_proceed is False


def test_a_recovery_with_no_start_refuses_on_read():
    """The same rule applies to recovery as to completion."""
    laboratory = Laboratory()
    laboratory.initialize()
    plant_run(
        laboratory,
        "orphan-2",
        (_recovered_run(laboratory, "orphan-2", Participant.BOT_SUITE, sequence=1),),
    )

    survey = laboratory.ledger.survey()

    assert survey.invalid == ("orphan-2",)
    assert survey.recovered == ()
    assert laboratory.admit(reservation_id="RES-1").may_proceed is False


#: Every way a syntactically valid run file is still not a run history, planted
#: around the writer so the reader is what is under test. The final rows are the
#: valid controls.
PARTICIPANT_AUDIT = (
    (
        "a completion by another participant",
        "web-1",
        lambda lab: (
            _started(lab, "web-1", Participant.WEB_SUITE),
            _completed(lab, "web-1", Participant.FOUNDRY_TESTS),
        ),
        "PR-20260911-R4-2",
    ),
    (
        "a completion naming another run",
        "web-1",
        lambda lab: (
            _started(lab, "web-1", Participant.WEB_SUITE),
            _completed(lab, "web-9", Participant.WEB_SUITE),
        ),
        "and this file's run is 'web-1'",
    ),
    (
        "a run filed under another run's name",
        "web-1",
        lambda lab: (
            _started(lab, "web-2", Participant.WEB_SUITE),
            _completed(lab, "web-2", Participant.WEB_SUITE),
        ),
        "filed under another run's name",
    ),
    (
        "an identity that changed between start and completion",
        "web-1",
        lambda lab: (
            _started(lab, "web-1", Participant.WEB_SUITE),
            _completed(lab, "web-1", Participant.WEB_SUITE, identity="somebody else"),
        ),
        "A changed identity between the start and the ending",
    ),
    (
        "a start whose identity is not the participant's",
        "web-1",
        lambda lab: (
            _started(lab, "web-1", Participant.WEB_SUITE, identity="root"),
        ),
        "disagrees with the participant's",
    ),
    (
        "an unknown participant",
        "web-1",
        lambda lab: (
            run_entry(
                lab,
                EntryKind.PARTICIPANT_STARTED,
                sequence=1,
                run="web-1",
                participant=Participant.WEB_SUITE,
                identity="whoever",
                effects="something",
            ).__class__(
                sequence=1,
                kind=EntryKind.PARTICIPANT_STARTED,
                host=lab.host,
                target=lab.target,
                author="ubuntu",
                at="t1",
                fields={
                    "run": "web-1",
                    "participant": "tests/somebody-elses-suite",
                    "identity": "whoever",
                    "reservation": "",
                    "effects": "something",
                },
            ),
        ),
        "not one of the seven participants",
    ),
    (
        "an empty evidence string",
        "web-1",
        lambda lab: (
            _started(lab, "web-1", Participant.WEB_SUITE),
            _completed(lab, "web-1", Participant.WEB_SUITE, evidence=""),
        ),
        "does not become proof",
    ),
    (
        "an arbitrary evidence string",
        "web-1",
        lambda lab: (
            _started(lab, "web-1", Participant.WEB_SUITE),
            _completed(lab, "web-1", Participant.WEB_SUITE, evidence="all fine"),
        ),
        "does not become proof",
    ),
    (
        "evidence that omits a condition",
        "web-1",
        lambda lab: (
            _started(lab, "web-1", Participant.WEB_SUITE),
            _completed(
                lab,
                "web-1",
                Participant.WEB_SUITE,
                evidence=CompletionEvidence(
                    run_id="web-1",
                    observed_by="the operator",
                    conditions=PARTICIPANT_PROFILES[
                        Participant.WEB_SUITE
                    ].completion_conditions[:1],
                ).encode(),
            ),
        ),
        "completeness of the content",
    ),
    (
        "evidence about another run",
        "web-1",
        lambda lab: (
            _started(lab, "web-1", Participant.WEB_SUITE),
            _completed(
                lab,
                "web-1",
                Participant.WEB_SUITE,
                evidence=CompletionEvidence(
                    run_id="web-9",
                    observed_by="the operator",
                    conditions=PARTICIPANT_PROFILES[
                        Participant.WEB_SUITE
                    ].completion_conditions,
                ).encode(),
            ),
        ),
        "Evidence is bound to the run it was collected for",
    ),
    (
        "evidence nobody observed",
        "web-1",
        lambda lab: (
            _started(lab, "web-1", Participant.WEB_SUITE),
            _completed(
                lab,
                "web-1",
                Participant.WEB_SUITE,
                evidence=CompletionEvidence(
                    run_id="web-1",
                    observed_by="",
                    conditions=PARTICIPANT_PROFILES[
                        Participant.WEB_SUITE
                    ].completion_conditions,
                ).encode(),
            ),
        ),
        "names nobody as having observed",
    ),
    (
        "an ordinary participant claiming a reservation binding",
        "web-1",
        lambda lab: (
            _started(lab, "web-1", Participant.WEB_SUITE),
            _completed(
                lab,
                "web-1",
                Participant.WEB_SUITE,
                evidence=CompletionEvidence(
                    run_id="web-1",
                    observed_by="the operator",
                    conditions=PARTICIPANT_PROFILES[
                        Participant.WEB_SUITE
                    ].completion_conditions,
                    reservation_id="RES-1",
                ).encode(),
            ),
        ),
        "claims a binding it did not establish",
    ),
    (
        "a harness completion with no reservation named",
        "harness-1",
        lambda lab: (
            _started(lab, "harness-1", Participant.HARNESS_CLI),
            _completed(
                lab,
                "harness-1",
                Participant.HARNESS_CLI,
                evidence=CompletionEvidence(
                    run_id="harness-1",
                    observed_by="the operator",
                    conditions=PARTICIPANT_PROFILES[
                        Participant.HARNESS_CLI
                    ].completion_conditions,
                ).encode(),
            ),
        ),
        "names no reservation",
    ),
    (
        "a duplicate terminal entry",
        "web-1",
        lambda lab: (
            _started(lab, "web-1", Participant.WEB_SUITE),
            _completed(lab, "web-1", Participant.WEB_SUITE),
            _completed(lab, "web-1", Participant.WEB_SUITE, sequence=3),
        ),
        "A run ends once",
    ),
    (
        "a recovery appended over a completion",
        "web-1",
        lambda lab: (
            _started(lab, "web-1", Participant.WEB_SUITE),
            _completed(lab, "web-1", Participant.WEB_SUITE),
            _recovered_run(lab, "web-1", Participant.WEB_SUITE, sequence=3),
        ),
        "A run ends once",
    ),
    (
        "a second start",
        "web-1",
        lambda lab: (
            _started(lab, "web-1", Participant.WEB_SUITE),
            run_entry(
                lab,
                EntryKind.PARTICIPANT_STARTED,
                sequence=2,
                run="web-1",
                participant=Participant.WEB_SUITE,
                effects="again",
            ),
        ),
        "A run begins once",
    ),
    (
        "a recovery with no reference",
        "web-1",
        lambda lab: (
            _started(lab, "web-1", Participant.WEB_SUITE),
            _recovered_run(lab, "web-1", Participant.WEB_SUITE, reference=" "),
        ),
        "names no recovery",
    ),
)


@pytest.mark.parametrize(
    "label, name, build, expected",
    PARTICIPANT_AUDIT,
    ids=[row[0] for row in PARTICIPANT_AUDIT],
)
def test_the_participant_history_audit(label, name, build, expected):
    """Every invalid run history blocks, and names which rule it breaks."""
    laboratory = Laboratory()
    laboratory.initialize()
    plant_run(laboratory, name, build(laboratory))

    survey = laboratory.ledger.survey()

    assert survey.settled is False, label
    assert survey.invalid == (name,), label
    assert any(expected in reason for reason in survey.reasons), (
        label,
        survey.reasons,
    )
    # The invalid predecessor refuses **every** successor, harness and reset
    # included, which is R3-2's rule applied to R4-2's new blocking class.
    for successor in PARTICIPANTS:
        assert laboratory.admit(
            participant=successor, reservation_id="RES-9"
        ).may_proceed is False, (label, successor)


def test_a_wrong_host_or_target_run_file_refuses():
    """The run file's binding is checked against the run being performed."""
    laboratory = Laboratory()
    laboratory.initialize()
    other = Laboratory(host="oracle-test-rebuilt", target="oracle-test-rebuilt")
    plant_run(
        laboratory,
        "web-1",
        (
            _started(other, "web-1", Participant.WEB_SUITE),
            _completed(other, "web-1", Participant.WEB_SUITE),
        ),
    )

    survey = laboratory.ledger.survey()

    assert survey.unreadable == ("web-1",)
    assert survey.settled is False
    assert laboratory.admit(reservation_id="RES-1").may_proceed is False


def test_a_missing_ledger_refuses_rather_than_reading_as_empty():
    """**R4-2's second path.** `ledger=None` admitted with a web run outstanding.

    Contract §5.8 requires the ledger for every participant, so unavailable
    accounting is a refusal. The intentionally isolated reservation-layer unit
    path is `participant_may_proceed`, which is a separate, labelled function.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.ledger.begin(
        run_id="web-1", participant=Participant.WEB_SUITE, author="ubuntu", at="t1"
    )

    omitted = laboratory.admit(reservation_id="RES-1", ledger=None)

    assert omitted.may_proceed is False
    assert omitted.runs is None
    assert any("PR-20260911-R4-2" in reason for reason in omitted.refusals)
    assert any(
        "never an empty, settled ledger" in reason for reason in omitted.refusals
    )


def test_an_unreadable_ledger_refuses():
    """A run file that will not parse blocks exactly as an unsettled one does."""
    laboratory = Laboratory()
    laboratory.initialize()
    plant_bytes(laboratory, laboratory.runs_directory, "web-1", b"not a record\n")

    survey = laboratory.ledger.survey()

    assert survey.unreadable == ("web-1",)
    assert laboratory.admit(reservation_id="RES-1").may_proceed is False


def test_a_valid_provisioned_observed_empty_ledger_still_admits():
    """**The preserved control.** An empty ledger that was read is not a refusal.

    The refusal is for a ledger that was *not supplied*. A provisioned ledger
    directory with no run files in it was surveyed, found empty, and admits — so
    the new rule is not "refuse whenever accounting is inconvenient".
    """
    laboratory = Laboratory()
    laboratory.initialize()

    survey = laboratory.ledger.survey()
    admission = laboratory.admit(reservation_id="RES-1")

    assert survey.settled is True
    assert (survey.unsettled, survey.unreadable, survey.invalid) == ((), (), ())
    assert admission.may_proceed is True
    assert admission.runs is not None


@pytest.mark.parametrize(
    "participant", PARTICIPANTS, ids=[p.name for p in PARTICIPANTS]
)
def test_every_participant_completes_and_recovers(participant):
    """The matching success and recovery controls, for all seven.

    The harness's completion goes through the terminal publication order because
    its conditions are lifecycle-owned; the other six observe their own external
    conditions. Both paths settle the ledger and admit the next participant.
    """
    completed = Laboratory()
    completed.initialize()
    completed.append(
        EntryKind.ADMITTED, author="executor RES-1", at="t1", reservation="RES-1"
    )
    completed.ledger.begin(
        run_id="run-1",
        participant=participant,
        author="ubuntu",
        at="t1",
        reservation_id=_owned_reservation(participant, "RES-1"),
    )
    completed.append(
        EntryKind.RUNNING, author="executor RES-1", at="t2", reservation="RES-1"
    )

    if participant is Participant.HARNESS_CLI:
        outcome = completed.conclude("RES-1", "run-1")
        assert outcome.concluded is True
    else:
        assert completed.ledger.complete(
            run_id="run-1",
            participant=participant,
            author="ubuntu",
            at="t3",
            observation=observed(participant),
        ).published is True
        assert completed.append(
            EntryKind.RELEASED,
            author="executor RES-1",
            at="t4",
            reservation="RES-1",
            released_at="t4",
        ).published is True

    completed.fs.restart_process()
    survey = completed.ledger.survey()
    assert survey.completed == ("run-1",)
    assert survey.settled is True
    assert completed.admit(reservation_id="RES-2").may_proceed is True

    # The same participant, interrupted, then recovered by an operator.
    recovered = Laboratory()
    recovered.initialize()
    recovered.ledger.begin(
        run_id="run-1",
        participant=participant,
        author="ubuntu",
        at="t1",
        reservation_id=_owned_reservation(participant, "RES-1"),
    )
    recovered.fs.restart_process()
    assert recovered.admit(reservation_id="RES-2").may_proceed is False
    assert recovered.ledger.recover(
        run_id="run-1",
        participant=participant,
        author=ATTESTER,
        at="t2",
        reference="ops-2026-09-11-07",
    ).published is True
    assert recovered.ledger.survey().recovered == ("run-1",)
    assert recovered.admit(reservation_id="RES-2").may_proceed is True


def test_a_recovered_runs_identity_is_not_reused():
    """A recovered run file is terminal; the next run takes a new id."""
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.ledger.begin(
        run_id="run-1", participant=Participant.BOT_SUITE, author="ubuntu", at="t1"
    )
    laboratory.ledger.recover(
        run_id="run-1",
        participant=Participant.BOT_SUITE,
        author=ATTESTER,
        at="t2",
        reference="ops-1",
    )

    reused = laboratory.ledger.begin(
        run_id="run-1", participant=Participant.BOT_SUITE, author="ubuntu", at="t3"
    )

    assert reused.published is False
    assert reused.refusal is PublicationRefusal.ALREADY_PUBLISHED
    assert laboratory.ledger.survey().recovered == ("run-1",)
    assert laboratory.ledger.begin(
        run_id="run-2", participant=Participant.BOT_SUITE, author="ubuntu", at="t4"
    ).published is True


def test_the_completion_profile_comes_from_the_stored_start():
    """The caller's participant is a checked claim, never the source of truth."""
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.ledger.begin(
        run_id="run-1", participant=Participant.BOT_SUITE, author="ubuntu", at="t1"
    )
    plant = laboratory.ledger.survey()
    assert plant.unsettled == ("run-1",)

    # The caller claims the Foundry suite and supplies its conditions in full.
    # Those conditions are a strict subset of nothing the bot suite requires, and
    # the binding check refuses before the evidence is even considered.
    refused = laboratory.ledger.complete(
        run_id="run-1",
        participant=Participant.FOUNDRY_TESTS,
        author="ubuntu",
        at="t2",
        observation=observed(Participant.FOUNDRY_TESTS),
    )

    assert refused.published is False
    state = check_participant_history(
        [_started(laboratory, "run-1", Participant.BOT_SUITE)], run_id="run-1"
    )
    assert state.ok is True
    assert state.participant is Participant.BOT_SUITE
    assert state.phase is RunPhase.IN_PROGRESS


def test_completion_evidence_decodes_only_its_own_encoding():
    """The codec's own boundary, so the content check has something to stand on."""
    evidence = CompletionEvidence(
        run_id="run-1",
        observed_by="the operator",
        conditions=("one", "two"),
        reservation_id="RES-1",
    )

    assert CompletionEvidence.decode(evidence.encode()) == evidence
    assert CompletionEvidence.decode("") is None
    assert CompletionEvidence.decode("all conditions observed") is None
    assert CompletionEvidence.decode("run=a|observed-by=b") is None
    assert CompletionEvidence.decode("run=a|run=b|reservation=|observed-by=c") is None
    assert CompletionEvidence.decode("run=a|reservation=|observed-by=c|what=x") is None


# ---------------------------------------------------------------------------
# R4-3 — an achievable order between the two terminal publications
# ---------------------------------------------------------------------------


def test_the_terminal_publication_order_is_stated_with_its_argument():
    """The order, why neither half alone authorizes reuse, and the alternative."""
    joined = " ".join(TERMINAL_PUBLICATION_ORDER)

    assert "Evaluate the release decision" in joined
    assert "Publish the reservation's RELEASED entry durably" in joined
    assert "Publish the harness participant's completion" in joined
    assert "no instant of this sequence admits anybody on one satisfied half" in joined
    assert "What a restart between the two publications finds" in joined
    assert "Why not the reverse order" in joined


def test_the_terminal_publications_have_a_reachable_successful_path():
    """**R4-3's correction.** The harness obtains its own required observation.

    Nothing injects `release durable` while the record says RUNNING. The two
    conditions are the return values of the release decision and of the release
    publication, both performed here, in that order.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.append(
        EntryKind.ADMITTED, author="executor RES-1", at="t1", reservation="RES-1"
    )
    laboratory.begin_harness("RES-1-harness", "RES-1", at="t1")
    laboratory.append(
        EntryKind.RUNNING, author="executor RES-1", at="t2", reservation="RES-1"
    )

    outcome = laboratory.conclude("RES-1", "RES-1-harness")

    assert outcome.decision is ReservationState.RELEASED
    assert outcome.release_entry.published is True
    assert outcome.release_entry.barriers == ("record-data", "record-entry")
    assert outcome.completion.published is True
    assert outcome.concluded is True

    parsed = laboratory.ledger.survey()
    assert parsed.completed == ("RES-1-harness",)
    admission = laboratory.admit(reservation_id="RES-2")
    assert admission.may_proceed is True
    assert admission.history.disposition is PredecessorDisposition.RELEASED


def test_an_injected_lifecycle_fact_is_refused():
    """The observation that made revision 4's green test meaningless.

    `_observed(HARNESS_CLI)` set both future facts to True. The writer now
    refuses an observation that supplies either of them.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.begin_harness("harness-1", "RES-1", at="t1")

    injected = laboratory.ledger.complete(
        run_id="harness-1",
        participant=Participant.HARNESS_CLI,
        author="root",
        at="t2",
        observation=CompletionObservation(
            observed_by="the executor",
            observed={
                HARNESS_RELEASE_DECIDED: True,
                HARNESS_RELEASE_PUBLISHED: True,
            },
        ),
    )

    assert injected.published is False
    assert any("lifecycle-owned fact" in reason for reason in injected.reasons)
    assert laboratory.ledger.survey().unsettled == ("harness-1",)


def test_a_completion_without_a_terminal_publication_refuses():
    """The harness cannot complete before it has published anything."""
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.begin_harness("harness-1", "RES-1", at="t1")

    early = laboratory.ledger.complete(
        run_id="harness-1",
        participant=Participant.HARNESS_CLI,
        author="root",
        at="t2",
        observation=CompletionObservation(observed_by="the executor"),
    )

    assert early.published is False
    assert any("never injected" in reason for reason in early.reasons)


def test_a_refused_release_decision_publishes_neither_half():
    """Step 1's fail-closed half: the reservation stays where it was."""
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.append(
        EntryKind.ADMITTED, author="executor RES-1", at="t1", reservation="RES-1"
    )
    laboratory.begin_harness("RES-1-harness", "RES-1", at="t1")
    laboratory.append(
        EntryKind.RUNNING, author="executor RES-1", at="t2", reservation="RES-1"
    )
    before = laboratory.record.read_record_bytes()

    outcome = laboratory.conclude(
        "RES-1",
        "RES-1-harness",
        evidence=laboratory.release_evidence("RES-1", child_processes_ended=False),
    )

    assert outcome.decision is ReservationState.QUARANTINED
    assert outcome.release_entry is None
    assert outcome.completion is None
    assert outcome.concluded is False
    assert laboratory.record.read_record_bytes() == before
    successor = laboratory.admit(reservation_id="RES-2")
    assert successor.may_proceed is False
    assert successor.history.predecessor_state is ReservationState.RUNNING


#: Every interruption between and inside the two terminal publications, with
#: what a restarted successor then finds. The point of the table is that the
#: outcome differs by row and each row is stated: an intermediate state either
#: refuses, or has been completed by a barrier the successor itself re-seals.
#: Nothing here admits on one satisfied half.
#:
#: `temporary` names the publication temporary a failure before the rename
#: leaves behind. It is reported and **never removed automatically**, so the
#: recovery for those rows begins with an operator removing it — the §2.13.2b
#: precedent, modelled rather than assumed away.
TERMINAL_INTERRUPTIONS = (
    (
        "before the release bytes were synchronized",
        "record-data",
        "",
        "record",
        False,
    ),
    (
        "after the release bytes and before the rename",
        "rename",
        "",
        "record",
        False,
    ),
    (
        "after the release rename and before its directory barrier",
        "record-entry",
        "",
        None,
        False,
    ),
    (
        "before the completion bytes were synchronized",
        "",
        "record-data",
        "run",
        False,
    ),
    (
        "after the completion bytes and before the rename",
        "",
        "rename",
        "run",
        False,
    ),
    (
        "after the completion rename and before its directory barrier",
        "",
        "record-entry",
        None,
        True,
    ),
)


@pytest.mark.parametrize(
    "label, fail_release_at, fail_completion_at, temporary, admits_after_restart",
    TERMINAL_INTERRUPTIONS,
    ids=[row[0] for row in TERMINAL_INTERRUPTIONS],
)
def test_no_intermediate_terminal_state_authorizes_reuse(
    label, fail_release_at, fail_completion_at, temporary, admits_after_restart
):
    """Every point inside the two publications refuses, or is completed safely.

    A process restart is used rather than a power loss: it is the case that
    destroys the writer's memory and leaves the filesystem exactly as it was, so
    the successor sees the visible record and not the failure. Power loss stays a
    distinct scenario and is exercised separately.

    The last row is the one that **does** admit, and it is the correction from
    R3-1 doing its work rather than a hole: the completion entry was renamed, the
    successor re-seals the ledger's parent entry under the lock, and the run is
    settled. The reservation is RELEASED and the run is COMPLETED, so both halves
    hold. Every other row leaves one half open and refuses.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.append(
        EntryKind.ADMITTED, author="executor RES-1", at="t1", reservation="RES-1"
    )
    laboratory.begin_harness("RES-1-harness", "RES-1", at="t1")
    laboratory.append(
        EntryKind.RUNNING, author="executor RES-1", at="t2", reservation="RES-1"
    )

    outcome = laboratory.conclude(
        "RES-1",
        "RES-1-harness",
        fail_release_at=fail_release_at,
        fail_completion_at=fail_completion_at,
    )

    assert outcome.concluded is False, label
    assert outcome.refusals, label

    laboratory.fs.restart_process()

    for successor in PARTICIPANTS:
        admission = laboratory.admit(participant=successor, reservation_id="RES-2")
        assert admission.may_proceed is admits_after_restart, (label, successor)
        # The prior history is preserved in every case: the record still parses
        # and is still rooted in the first use nobody overwrote.
        assert admission.parsed.ok is True, label
        assert admission.parsed.entries[0].kind is EntryKind.FIRST_USE, label

    if admits_after_restart:
        return

    # --- the bounded, attributable recovery for this intermediate state ----
    if temporary == "record":
        assert laboratory.record.temporary_present() is True, label
        laboratory.remove_temporary(laboratory.directory, "lifecycle.json.tmp")
    elif temporary == "run":
        assert laboratory.ledger.survey().unreadable == ("RES-1-harness.tmp",), label
        laboratory.remove_temporary(laboratory.runs_directory, "RES-1-harness.tmp")

    released = laboratory.admit(reservation_id="RES-2").history.predecessor_state
    if released is not ReservationState.RELEASED:
        # The release never became visible, so the reservation is quarantined
        # and recovered as a reservation before anything else may run.
        assert laboratory.append(
            EntryKind.QUARANTINED,
            author=ATTESTER,
            at="t5",
            reservation="RES-1",
            reason=f"the executor stopped {label}",
        ).published is True
        assert laboratory.append(
            EntryKind.OPERATOR_RECOVERED,
            author=ATTESTER,
            at="t6",
            recovers="RES-1",
            reference="ops-2026-09-11-08",
        ).published is True
    assert laboratory.ledger.recover(
        run_id="RES-1-harness",
        participant=Participant.HARNESS_CLI,
        author=ATTESTER,
        at="t7",
        reference="ops-2026-09-11-08",
    ).published is True

    recovered = laboratory.admit(reservation_id="RES-2")
    assert recovered.may_proceed is True, (label, recovered.refusals)


def test_a_restart_between_the_two_terminal_publications_is_blocked_by_the_ledger():
    """The named intermediate state, on its own, with the argument asserted.

    The reservation record says RELEASED and the harness's run is still started.
    The release alone does not admit anybody, because the ledger blocks — which
    is exactly the claim `TERMINAL_PUBLICATION_ORDER` makes for the window.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.append(
        EntryKind.ADMITTED, author="executor RES-1", at="t1", reservation="RES-1"
    )
    laboratory.begin_harness("RES-1-harness", "RES-1", at="t1")
    laboratory.append(
        EntryKind.RUNNING, author="executor RES-1", at="t2", reservation="RES-1"
    )
    # The release publishes; the process dies before the completion is written.
    assert laboratory.append(
        EntryKind.RELEASED,
        author="executor RES-1",
        at="t4",
        reservation="RES-1",
        released_at="t4",
    ).published is True
    laboratory.fs.restart_process()

    blocked = laboratory.admit(reservation_id="RES-2")

    assert blocked.history.disposition is PredecessorDisposition.RELEASED
    assert blocked.may_proceed is False
    assert blocked.runs.unsettled == ("RES-1-harness",)
    assert any("blocks every successor" in reason for reason in blocked.refusals)

    assert laboratory.ledger.recover(
        run_id="RES-1-harness",
        participant=Participant.HARNESS_CLI,
        author=ATTESTER,
        at="t5",
        reference="ops-2026-09-11-09",
    ).published is True
    assert laboratory.admit(reservation_id="RES-2").may_proceed is True


def test_a_power_loss_in_the_window_remains_a_distinct_scenario():
    """Power loss removes what the restart keeps, and it is not the same event."""
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.append(
        EntryKind.ADMITTED, author="executor RES-1", at="t1", reservation="RES-1"
    )
    laboratory.begin_harness("RES-1-harness", "RES-1", at="t1")
    laboratory.append(
        EntryKind.RUNNING, author="executor RES-1", at="t2", reservation="RES-1"
    )
    laboratory.conclude("RES-1", "RES-1-harness", fail_release_at="record-entry")

    assert laboratory.record_is_visible() is True
    assert b"released" in laboratory.record.read_record_bytes()

    laboratory.fs.crash()

    # The release entry is gone. The record is at RUNNING and refuses, and the
    # started harness run refuses as well. Nothing was admitted on half a state.
    admission = laboratory.admit(reservation_id="RES-2")
    assert admission.may_proceed is False
    assert admission.history.predecessor_state is ReservationState.RUNNING


def test_stale_release_evidence_from_another_reservation_refuses():
    """A release of RES-1 does not conclude RES-2, at either layer.

    `reservation.release()` refuses the mismatched evidence, so no release entry
    and no completion is published, and the second reservation stays running.
    """
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
    laboratory.append(
        EntryKind.ADMITTED, author="executor RES-2", at="t3", reservation="RES-2"
    )
    laboratory.begin_harness("RES-2-harness", "RES-2", at="t3")
    laboratory.append(
        EntryKind.RUNNING, author="executor RES-2", at="t4", reservation="RES-2"
    )

    outcome = laboratory.conclude(
        "RES-2",
        "RES-2-harness",
        evidence=laboratory.release_evidence("RES-1", lock_held_by="RES-2"),
    )

    assert outcome.decision is ReservationState.QUARANTINED
    assert outcome.release_entry is None
    assert any("releases nothing here" in reason for reason in outcome.refusals)
    successor = laboratory.admit(reservation_id="RES-3")
    assert successor.may_proceed is False
    assert successor.history.predecessor_id == "RES-2"


# ---------------------------------------------------------------------------
# The corrected full lifecycle, from a fresh process, over stored bytes
# ---------------------------------------------------------------------------


def test_three_sequential_reservations_from_stored_bytes_only():
    """**Not one fresh run: three, each reading what the last one wrote.**

    Every decision in this trace is taken from bytes a predecessor published,
    through a process restart before each admission, so no lifecycle fact is
    manufactured beside the store. The second reservation is interrupted and
    recovered; the first and third conclude normally through the corrected
    terminal order.
    """
    laboratory = Laboratory()
    assert laboratory.initialize().initialized is True

    # --- RES-1: a complete, successful reservation ------------------------
    laboratory.fs.restart_process()
    first = laboratory.admit(reservation_id="RES-1")
    assert first.may_proceed is True
    assert first.history.disposition is PredecessorDisposition.VERIFIED_FIRST_USE
    assert first.history.first_use_attested_by == ATTESTER
    assert first.history.first_use_basis == BASIS

    laboratory.append(
        EntryKind.ADMITTED, author="executor RES-1", at="t1", reservation="RES-1"
    )
    laboratory.begin_harness("RES-1-harness", "RES-1", at="t1")
    laboratory.append(
        EntryKind.RUNNING, author="executor RES-1", at="t2", reservation="RES-1"
    )
    assert laboratory.conclude("RES-1", "RES-1-harness").concluded is True

    # --- RES-2: the web suite runs, is interrupted, and is recovered -------
    laboratory.fs.restart_process()
    second = laboratory.admit(participant=Participant.WEB_SUITE, reservation_id="RES-2")
    assert second.may_proceed is True
    assert second.history.disposition is PredecessorDisposition.RELEASED
    assert second.history.predecessor_id == "RES-1"

    laboratory.append(
        EntryKind.ADMITTED, author="executor RES-2", at="t5", reservation="RES-2"
    )
    laboratory.ledger.begin(
        run_id="RES-2-web", participant=Participant.WEB_SUITE, author="ubuntu", at="t5"
    )
    laboratory.append(
        EntryKind.RUNNING, author="executor RES-2", at="t6", reservation="RES-2"
    )
    laboratory.fs.restart_process()

    for successor in PARTICIPANTS:
        assert laboratory.admit(
            participant=successor, reservation_id="RES-3"
        ).may_proceed is False, successor

    laboratory.append(
        EntryKind.QUARANTINED,
        author=ATTESTER,
        at="t7",
        reservation="RES-2",
        reason="the web suite stopped with a backend unaccounted for",
    )
    laboratory.ledger.recover(
        run_id="RES-2-web",
        participant=Participant.WEB_SUITE,
        author=ATTESTER,
        at="t8",
        reference="ops-2026-09-11-10",
    )
    laboratory.append(
        EntryKind.OPERATOR_RECOVERED,
        author=ATTESTER,
        at="t9",
        recovers="RES-2",
        reference="ops-2026-09-11-10",
    )

    # --- RES-3: admitted on the recovery, and concluded normally ----------
    laboratory.fs.restart_process()
    third = laboratory.admit(reservation_id="RES-3")
    assert third.may_proceed is True
    assert third.history.disposition is PredecessorDisposition.OPERATOR_RECOVERED
    assert third.history.predecessor_id == "RES-2"
    assert third.history.recovery_authored_by == ATTESTER

    laboratory.append(
        EntryKind.ADMITTED, author="executor RES-3", at="t10", reservation="RES-3"
    )
    laboratory.begin_harness("RES-3-harness", "RES-3", at="t10")
    laboratory.append(
        EntryKind.RUNNING, author="executor RES-3", at="t11", reservation="RES-3"
    )
    assert laboratory.conclude("RES-3", "RES-3-harness").concluded is True

    laboratory.fs.restart_process()
    fourth = laboratory.admit(participant=Participant.BOT_SUITE, reservation_id="RES-4")
    assert fourth.may_proceed is True
    assert fourth.history.predecessor_id == "RES-3"
    assert fourth.runs.settled is True
    assert sorted(fourth.runs.completed) == ["RES-1-harness", "RES-3-harness"]
    assert fourth.runs.recovered == ("RES-2-web",)

    # No retired identity may be admitted again. Identity reuse is refused at
    # the publication that would record it, which is the layer that owns the
    # history: `admit()` decides whether *a* successor may proceed, and the
    # record decides which identities have already been spent.
    for retired in ("RES-1", "RES-2", "RES-3"):
        reused = laboratory.append(
            EntryKind.ADMITTED, author="executor", at="t20", reservation=retired
        )
        assert reused.published is False, retired
        assert reused.refusal is PublicationRefusal.INVALID_HISTORY, retired
        assert any("already used" in reason for reason in reused.reasons), retired

    kinds = [entry.kind for entry in fourth.parsed.entries]
    assert kinds == [
        EntryKind.FIRST_USE,
        EntryKind.ADMITTED,
        EntryKind.RUNNING,
        EntryKind.RELEASED,
        EntryKind.ADMITTED,
        EntryKind.RUNNING,
        EntryKind.QUARANTINED,
        EntryKind.OPERATOR_RECOVERED,
        EntryKind.ADMITTED,
        EntryKind.RUNNING,
        EntryKind.RELEASED,
    ]


def test_no_test_here_manufactures_a_lifecycle_fact_beside_the_store():
    """The module's own control, asserted against its syntax tree.

    Every history this file plants goes through `serialize_history` into the
    model's store and is read back through a descriptor. No test constructs a
    `LifecycleHistory` beside the store, and the two `UNIT_TEST_CONSTRUCTORS` are
    not used here. It is read from the AST rather than the text so that this
    docstring may name the things it forbids.
    """
    tree = ast.parse(
        pathlib.Path(__file__).read_text(encoding="utf-8"), filename=__file__
    )
    names = {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert "LifecycleHistory" not in names
    assert not (names & set(UNIT_TEST_CONSTRUCTORS))
