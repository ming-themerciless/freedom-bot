"""The durable reservation-to-harness binding — PR-20260911-R5-1.

**Every test in this file is a model test.** It exercises
`tools/phase_5_0_evidence/lifecycle_storage.py` over the in-memory
`durability_model.SyntheticFilesystem`. The mechanism these rules describe is
**not built**: there is no privileged mechanism, no real filesystem writer, no
lock adapter and no operational integration, and nothing here creates one. A
passing row establishes that the proposed rule is constructible and falsifiable,
and **nothing** about Linux, about `oracle-test` or about EH-R16-1.

One property carries this file and it was reproduced against the submitted
revision 5 before it was repaired.

* **R5-1** — `test_the_reviewers_wrong_reservation_completion_reproduction`.
  Revision 5's `CompletionEvidence` carried a reservation id for the harness and
  `check_participant_history()` checked only that it was **non-empty**. The
  stored `participant_started` entry carried no reservation at all, and
  `conclude_reservation()` took an independent caller-supplied `run_id`. So a
  release of reservation `A` published a valid RELEASED entry and then a valid
  completion into an already-started harness run `B`, the survey reported `B`
  completed, and the final conjunction admitted a successor. The reviewer's
  trace returned `{'concluded': True, 'release': True, 'completion': True,
  'completed': ('B-harness',)}`.

The repair is one durable fact and one comparison. The harness's start **names
the reservation the run owns**, and terminal publication requires exact equality
among the stored start, the reservation request, the release publication, the
completion evidence and the reservation the terminal result reports.

**Both sides, every case.** `plant_run` writes bytes around every writer-side
check, so a run file a corrected writer can no longer produce still reaches a
reader. A safe writer does not excuse an unsafe reader of records written by r5
or by a corrupt implementation, which is why the planted-byte audit below is not
a duplicate of the writer rows above it.

**No identity is inferred from a run name.** No test here relies on a prefix, a
suffix or any other convention over a run's filename, and
`test_the_binding_is_not_inferred_from_the_run_name` is the control that would
fail if one were introduced.
"""
from __future__ import annotations

import pytest

from tools.phase_5_0_evidence.lifecycle_storage import (
    EVIDENCE_SEPARATOR,
    HARNESS_RELEASE_DECIDED,
    HARNESS_RELEASE_PUBLISHED,
    PARTICIPANTS,
    PARTICIPANT_PROFILES,
    RECORD_MAGIC,
    RECORD_SCHEMA_VERSION,
    RESERVATION_BINDING,
    SUPPORTED_SCHEMA_VERSIONS,
    TERMINAL_PUBLICATION_ORDER,
    CompletionEvidence,
    CompletionObservation,
    EntryKind,
    Participant,
    PublicationOutcome,
    PublicationRefusal,
    RecordRefusal,
    ReleasePublication,
    RunPhase,
    check_participant_history,
    reservation_field_problems,
)
from tools.phase_5_0_evidence.reservation import (
    PredecessorDisposition,
    ReservationState,
)

from tests.phase_5_0_evidence.lifecycle_fixtures import (
    ATTESTER,
    Laboratory,
    observed,
    plant_bytes,
    plant_run,
    run_entry,
)

HARNESS_CONDITIONS = tuple(
    PARTICIPANT_PROFILES[Participant.HARNESS_CLI].completion_conditions
)


# ---------------------------------------------------------------------------
# Builders, so a case reads as the run file it is about
# ---------------------------------------------------------------------------


def _started(laboratory, run, participant, **overrides):
    return run_entry(
        laboratory,
        EntryKind.PARTICIPANT_STARTED,
        sequence=1,
        run=run,
        participant=participant,
        author="root" if participant is Participant.HARNESS_CLI else "ubuntu",
        at="t1",
        effects="; ".join(PARTICIPANT_PROFILES[participant].effects),
        **overrides,
    )


def _completed(laboratory, run, participant, *, reservation=None, **overrides):
    profile = PARTICIPANT_PROFILES[participant]
    if reservation is None:
        reservation = "RES-1" if profile.lifecycle_owned_conditions else ""
    evidence = CompletionEvidence(
        run_id=run,
        observed_by="the operator, post-run sweep",
        conditions=tuple(profile.completion_conditions),
        reservation_id=reservation,
    ).encode()
    return run_entry(
        laboratory,
        EntryKind.PARTICIPANT_COMPLETED,
        sequence=2,
        run=run,
        participant=participant,
        author="root" if participant is Participant.HARNESS_CLI else "ubuntu",
        at="t4",
        evidence=evidence,
        **overrides,
    )


def _publication(reservation, *, released=True, durable=True):
    """A release publication as its own writer observed it.

    Constructed here rather than obtained from `conclude_reservation`, because
    these rows exercise `RunLedger.complete()` directly — the path a caller
    could reach with a publication for one reservation and a run started for
    another.
    """
    return ReleasePublication(
        reservation_id=reservation,
        decision=(
            ReservationState.RELEASED if released else ReservationState.QUARANTINED
        ),
        publication=PublicationOutcome(
            published=durable,
            barriers=("record-data", "record-entry") if durable else ("record-data",),
        ),
    )


def _running_reservation(laboratory, reservation, run, *, at="t1"):
    """Initialize, admit, start the harness's run, and go RUNNING."""
    assert laboratory.initialize().initialized is True
    assert laboratory.append(
        EntryKind.ADMITTED,
        author=f"executor {reservation}",
        at=at,
        reservation=reservation,
    ).published is True
    assert laboratory.begin_harness(run, reservation, at=at).published is True
    assert laboratory.append(
        EntryKind.RUNNING,
        author=f"executor {reservation}",
        at="t2",
        reservation=reservation,
    ).published is True


# ---------------------------------------------------------------------------
# R5-1 — the reviewer's reproduction, through the fixture and the public APIs
# ---------------------------------------------------------------------------


def test_the_reviewers_wrong_reservation_completion_reproduction():
    """**PR-20260911-R5-1, exactly as the re-review reproduced it.**

    ```text
    initialize
    ADMITTED A
    begin B-harness as HARNESS_CLI
    RUNNING A
    conclude_reservation(reservation=A, run_id=B-harness)
    ```

    r5 returned `concluded=True`, published both entries and marked `B-harness`
    completed. The binding is now checked **before the release decision**, so
    neither terminal entry is published: A's record is untouched, B's started
    bytes are untouched, and B still blocks every successor.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.append(
        EntryKind.ADMITTED, author="executor A", at="t1", reservation="A"
    )
    assert laboratory.begin_harness("B-harness", "B", at="t1").published is True
    laboratory.append(
        EntryKind.RUNNING, author="executor A", at="t2", reservation="A"
    )
    record_before = laboratory.record.read_record_bytes()
    run_before = laboratory.ledger.read_run("B-harness").parsed.source_digest

    outcome = laboratory.conclude("A", "B-harness")

    # Nothing was decided and nothing was published.
    assert outcome.concluded is False
    assert outcome.release_entry is None
    assert outcome.completion is None
    assert outcome.reservation_id == "A"
    assert outcome.run_id == "B-harness"
    assert outcome.decision is ReservationState.RUNNING
    assert any("PR-20260911-R5-1" in reason for reason in outcome.refusals)
    assert any(
        "was started for reservation 'B'" in reason for reason in outcome.refusals
    )

    # Both objects' stored bytes are exactly what they were.
    assert laboratory.record.read_record_bytes() == record_before
    assert laboratory.ledger.read_run("B-harness").parsed.source_digest == run_before

    # B is still in progress, so it blocks every successor including the harness
    # and the environment reset.
    survey = laboratory.ledger.survey()
    assert survey.unsettled == ("B-harness",)
    assert survey.completed == ()
    assert survey.settled is False
    for successor in PARTICIPANTS:
        refused = laboratory.admit(participant=successor, reservation_id="C")
        assert refused.may_proceed is False, successor
        assert refused.runs.unsettled == ("B-harness",), successor


def test_the_refused_conclusion_leaves_a_released_entry_nowhere():
    """What happens to A's RELEASED entry: **it is never published.**

    The binding is step 0 of `TERMINAL_PUBLICATION_ORDER`, before the release
    decision, so the release-before-completion order is not entered at all. The
    reservation stays RUNNING, which refuses every successor on its own, and no
    intermediate state is created for an operator to unwind. This is stated
    rather than left to inference, because the alternative placement — checking
    the binding at the completion — would publish RELEASED and then refuse,
    leaving a reservation that reads terminal beside a run that cannot settle.
    """
    laboratory = Laboratory()
    _running_reservation(laboratory, "A", "A-harness")
    assert laboratory.begin_harness("B-harness", "B", at="t3").published is True
    before = laboratory.record.read_record_bytes()

    outcome = laboratory.conclude("A", "B-harness")

    assert outcome.release_entry is None
    assert b"released" not in laboratory.record.read_record_bytes()
    assert laboratory.record.read_record_bytes() == before
    successor = laboratory.admit(reservation_id="C")
    assert successor.may_proceed is False
    assert successor.history.predecessor_state is ReservationState.RUNNING


def test_the_bounded_attributable_recovery_of_the_refused_conclusion():
    """The two runs are then settled the only ways the contract allows.

    B is recovered by an attributed operator entry — B's own reservation is not
    concluded by A's release, and the recovery is what ends its run. A is then
    concluded against **its own** harness run, and the successor admits. Nothing
    is rewritten and no identity is reused.
    """
    laboratory = Laboratory()
    _running_reservation(laboratory, "A", "A-harness")
    assert laboratory.begin_harness("B-harness", "B", at="t3").published is True
    assert laboratory.conclude("A", "B-harness").concluded is False

    assert laboratory.ledger.recover(
        run_id="B-harness",
        participant=Participant.HARNESS_CLI,
        author=ATTESTER,
        at="t5",
        reference="ops-2026-09-11-11",
    ).published is True

    concluded = laboratory.conclude("A", "A-harness")

    assert concluded.concluded is True
    assert concluded.completion.published is True
    survey = laboratory.ledger.survey()
    assert survey.completed == ("A-harness",)
    assert survey.recovered == ("B-harness",)
    assert survey.settled is True
    laboratory.fs.restart_process()
    assert laboratory.admit(reservation_id="C").may_proceed is True


def test_the_wrong_reservation_completion_refuses_at_the_ledger_writer_too():
    """The same defect one layer down, where `conclude_reservation` is bypassed.

    A caller holding a release publication for `A` and a run started for `B` is
    the shape of the reviewer's trace without the conclusion helper. The ledger
    refuses it on the stored start, so the repair is not a check that lives only
    in the higher-level function.
    """
    laboratory = Laboratory()
    _running_reservation(laboratory, "A", "A-harness")
    assert laboratory.begin_harness("B-harness", "B", at="t3").published is True
    before = laboratory.ledger.read_run("B-harness").parsed.source_digest

    refused = laboratory.ledger.complete(
        run_id="B-harness",
        participant=Participant.HARNESS_CLI,
        author="root",
        at="t4",
        observation=observed(Participant.HARNESS_CLI),
        release_publication=_publication("A"),
    )

    assert refused.published is False
    assert refused.refusal is PublicationRefusal.NOT_DURABLE
    assert any("PR-20260911-R5-1" in reason for reason in refused.reasons)
    assert laboratory.ledger.read_run("B-harness").parsed.source_digest == before
    assert laboratory.ledger.survey().unsettled == ("A-harness", "B-harness")


# ---------------------------------------------------------------------------
# The stored binding, written and read
# ---------------------------------------------------------------------------


def test_the_harness_start_durably_names_its_reservation():
    """The durable fact r5 did not store, read back from the stored bytes."""
    laboratory = Laboratory()
    _running_reservation(laboratory, "RES-1", "RES-1-harness")

    laboratory.fs.restart_process()
    stored = laboratory.ledger.read_run("RES-1-harness")

    assert stored.ok is True
    assert stored.state.participant is Participant.HARNESS_CLI
    assert stored.state.reservation_id == "RES-1"
    assert stored.state.phase is RunPhase.IN_PROGRESS
    assert b"reservation=RES-1" in laboratory.ledger._store(
        "RES-1-harness"
    ).read_record_bytes()


@pytest.mark.parametrize(
    "participant", PARTICIPANTS, ids=[p.name for p in PARTICIPANTS]
)
def test_every_participants_start_carries_its_own_shape_of_the_field(participant):
    """One representation, validated in both directions, for all seven.

    The harness carries an identity; the six carry the field **empty**. Neither
    is optional: a field that may or may not be populated carries no
    information, which is the state r5's completion field was in.
    """
    profile = PARTICIPANT_PROFILES[participant]
    laboratory = Laboratory()
    laboratory.initialize()

    owned = bool(profile.lifecycle_owned_conditions)
    right = laboratory.ledger.begin(
        run_id="run-1",
        participant=participant,
        author="ubuntu",
        at="t1",
        reservation_id="RES-1" if owned else "",
    )
    assert right.published is True

    wrong = laboratory.ledger.begin(
        run_id="run-2",
        participant=participant,
        author="ubuntu",
        at="t1",
        reservation_id="" if owned else "RES-1",
    )
    assert wrong.published is False
    assert wrong.refusal is PublicationRefusal.INVALID_HISTORY
    assert laboratory.ledger.survey().unsettled == ("run-1",)


@pytest.mark.parametrize(
    "label,value,expected",
    [
        ("an identity", "RES-1", ()),
        ("nothing at all", "", ("names no reservation",)),
        ("only whitespace", "   ", ("names no reservation",)),
        ("a padded identity", " RES-1 ", ("not its own stripped form",)),
        (
            "the evidence separator",
            f"RES{EVIDENCE_SEPARATOR}1",
            ("field separator",),
        ),
        ("a line break", "RES-1\nRES-2", ("line break",)),
    ],
)
def test_the_stored_reservation_grammar_is_bounded(label, value, expected):
    """The field's grammar, so a comparison has something well-formed to compare.

    A value that is not its own stripped form is two spellings of one identity,
    and a value carrying the evidence separator or a line break cannot survive
    the codecs that transport it. Both refuse here rather than where the
    comparison would quietly fail.
    """
    problems = reservation_field_problems(
        value, PARTICIPANT_PROFILES[Participant.HARNESS_CLI], sequence=1
    )

    if not expected:
        assert problems == (), label
        return
    assert problems, label
    for fragment in expected:
        assert any(fragment in problem for problem in problems), (label, problems)


def test_a_harness_start_with_no_reservation_refuses_at_the_writer():
    """Missing and empty are the same refusal, and neither writes a byte."""
    laboratory = Laboratory()
    laboratory.initialize()

    empty = laboratory.ledger.begin(
        run_id="RES-1-harness",
        participant=Participant.HARNESS_CLI,
        author="root",
        at="t1",
        reservation_id="",
    )
    omitted = laboratory.ledger.begin(
        run_id="RES-2-harness",
        participant=Participant.HARNESS_CLI,
        author="root",
        at="t1",
    )

    for outcome in (empty, omitted):
        assert outcome.published is False
        assert outcome.refusal is PublicationRefusal.INVALID_HISTORY
        assert any("PR-20260911-R5-1" in reason for reason in outcome.reasons)
    assert laboratory.ledger.survey().settled is True
    assert laboratory.ledger.survey().unsettled == ()


# ---------------------------------------------------------------------------
# The planted-byte reader audit — a safe writer excuses no reader
# ---------------------------------------------------------------------------


PLANTED_RUNS = [
    (
        "a harness start naming no reservation",
        "RES-1-harness",
        lambda lab: (_started(lab, "RES-1-harness", Participant.HARNESS_CLI, reservation=""),),
        "names no reservation",
    ),
    (
        "a harness start whose reservation is whitespace",
        "RES-1-harness",
        lambda lab: (
            _started(lab, "RES-1-harness", Participant.HARNESS_CLI, reservation="  "),
        ),
        "names no reservation",
    ),
    (
        "a harness start whose reservation is padded",
        "RES-1-harness",
        lambda lab: (
            _started(lab, "RES-1-harness", Participant.HARNESS_CLI, reservation=" RES-1"),
        ),
        "not its own stripped form",
    ),
    (
        "a completion naming a different reservation from its start",
        "RES-1-harness",
        lambda lab: (
            _started(lab, "RES-1-harness", Participant.HARNESS_CLI, reservation="RES-1"),
            _completed(lab, "RES-1-harness", Participant.HARNESS_CLI, reservation="RES-2"),
        ),
        "PR-20260911-R5-1",
    ),
    (
        "a completion naming no reservation over a bound start",
        "RES-1-harness",
        lambda lab: (
            _started(lab, "RES-1-harness", Participant.HARNESS_CLI, reservation="RES-1"),
            _completed(lab, "RES-1-harness", Participant.HARNESS_CLI, reservation=""),
        ),
        "names no reservation",
    ),
    (
        "a web start carrying a reservation",
        "web-1",
        lambda lab: (
            _started(lab, "web-1", Participant.WEB_SUITE, reservation="RES-1"),
        ),
        "required to be empty",
    ),
    (
        "a web completion carrying a reservation",
        "web-1",
        lambda lab: (
            _started(lab, "web-1", Participant.WEB_SUITE),
            _completed(lab, "web-1", Participant.WEB_SUITE, reservation="RES-1"),
        ),
        "did not establish",
    ),
    (
        "a reset start carrying a reservation",
        "reset-1",
        lambda lab: (
            _started(lab, "reset-1", Participant.ENVIRONMENT_RESET, reservation="RES-1"),
        ),
        "required to be empty",
    ),
]


@pytest.mark.parametrize(
    "label,name,build,expected",
    PLANTED_RUNS,
    ids=[row[0] for row in PLANTED_RUNS],
)
def test_the_planted_reservation_binding_audit(label, name, build, expected):
    """Each mismatching run file refuses on **read** and blocks every successor.

    These are bytes the corrected writer cannot produce. They are the records r5
    published and the records a corrupt implementation would publish, so the
    reader refuses them on its own rather than relying on the writer's repair.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    plant_run(laboratory, name, build(laboratory))

    stored = laboratory.ledger.read_run(name)
    survey = laboratory.ledger.survey()

    assert stored.ok is False, label
    assert any(expected in reason for reason in stored.refusals), (label, stored.refusals)
    assert survey.invalid == (name,), label
    assert survey.completed == (), label
    assert survey.settled is False, label
    for successor in PARTICIPANTS:
        refused = laboratory.admit(participant=successor, reservation_id="RES-9")
        assert refused.may_proceed is False, (label, successor)
        assert refused.runs.invalid == (name,), (label, successor)


def test_a_planted_matching_harness_pair_is_read_as_settled():
    """The preserved positive control for the audit above.

    A planted start and completion that agree about the reservation read as a
    completed run, so the new rule refuses mismatches rather than refusing
    whenever a reservation is mentioned.
    """
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
        at="t4",
        reservation="RES-1",
        released_at="t4",
    )
    plant_run(
        laboratory,
        "RES-1-harness",
        (
            _started(laboratory, "RES-1-harness", Participant.HARNESS_CLI, reservation="RES-1"),
            _completed(laboratory, "RES-1-harness", Participant.HARNESS_CLI, reservation="RES-1"),
        ),
    )

    stored = laboratory.ledger.read_run("RES-1-harness")
    survey = laboratory.ledger.survey()

    assert stored.ok is True
    assert stored.state.reservation_id == "RES-1"
    assert stored.state.phase is RunPhase.COMPLETED
    assert survey.completed == ("RES-1-harness",)
    assert survey.settled is True
    assert laboratory.admit(reservation_id="RES-2").may_proceed is True


def test_an_r5_participant_start_refuses_as_an_unsupported_schema():
    """The compatibility consequence, asserted rather than described.

    An r5 run file declares `schema=1` and carries no reservation field. Reading
    it under r6's meanings would read an r5 harness run as one whose binding
    happens to be whatever the reader defaults to, so the version refuses it by
    name. It counts as unreadable and blocks, and an operator's attributed
    recovery is the only way past it.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    profile = PARTICIPANT_PROFILES[Participant.HARNESS_CLI]
    r5_bytes = (
        "\n".join(
            [
                RECORD_MAGIC,
                "schema=1",
                "begin-entry",
                "sequence=1",
                "kind=participant_started",
                f"host={laboratory.host}",
                f"target={laboratory.target}",
                "author=root",
                "at=t1",
                "run=RES-1-harness",
                "participant=harness_cli",
                f"identity={profile.identity}",
                f"effects={'; '.join(profile.effects)}",
                "end-entry",
                "end-history",
            ]
        )
        + "\n"
    ).encode("utf-8")
    plant_bytes(laboratory, laboratory.runs_directory, "RES-1-harness", r5_bytes)

    stored = laboratory.ledger.read_run("RES-1-harness")
    survey = laboratory.ledger.survey()

    assert stored.ok is False
    assert stored.parsed.refusal is RecordRefusal.UNSUPPORTED_SCHEMA
    assert survey.unreadable == ("RES-1-harness",)
    assert survey.settled is False
    assert laboratory.admit(reservation_id="RES-2").may_proceed is False


def test_a_current_schema_start_without_the_field_refuses_as_malformed():
    """The bounded field set, which is what makes the field required at all.

    A record declaring this schema and omitting the reservation is malformed —
    not a start with an unknown binding. The schema is bounded in both
    directions: an unknown field refuses and a missing one refuses.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    profile = PARTICIPANT_PROFILES[Participant.HARNESS_CLI]
    raw = (
        "\n".join(
            [
                RECORD_MAGIC,
                f"schema={RECORD_SCHEMA_VERSION}",
                "begin-entry",
                "sequence=1",
                "kind=participant_started",
                f"host={laboratory.host}",
                f"target={laboratory.target}",
                "author=root",
                "at=t1",
                "run=RES-1-harness",
                "participant=harness_cli",
                f"identity={profile.identity}",
                f"effects={'; '.join(profile.effects)}",
                "end-entry",
                "end-history",
            ]
        )
        + "\n"
    ).encode("utf-8")
    plant_bytes(laboratory, laboratory.runs_directory, "RES-1-harness", raw)

    stored = laboratory.ledger.read_run("RES-1-harness")

    assert stored.ok is False
    assert stored.parsed.refusal is RecordRefusal.MALFORMED
    assert any("reservation" in reason for reason in stored.parsed.reasons)
    assert laboratory.ledger.survey().unreadable == ("RES-1-harness",)


# ---------------------------------------------------------------------------
# Exact equality among the five values, in every direction
# ---------------------------------------------------------------------------


DISAGREEMENTS = [
    ("the request names another reservation", "RES-1", "RES-9", "RES-1"),
    ("the request names the earlier reservation", "RES-9", "RES-1", "RES-9"),
]


@pytest.mark.parametrize(
    "label,started_for,concluding,publication",
    DISAGREEMENTS,
    ids=[row[0] for row in DISAGREEMENTS],
)
def test_a_request_disagreeing_with_the_stored_start_refuses(
    label, started_for, concluding, publication
):
    """`ReservationRequest.reservation_id` against the stored start, both ways.

    The direction matters because a check written as *"the start's reservation is
    a prefix of, or contained in, the request"* would pass one of these rows. The
    rule is exact equality.
    """
    laboratory = Laboratory()
    _running_reservation(laboratory, started_for, "harness-run")

    outcome = laboratory.conclude(concluding, "harness-run")

    assert outcome.concluded is False, label
    assert outcome.release_entry is None, label
    assert any("PR-20260911-R5-1" in reason for reason in outcome.refusals), label
    assert laboratory.ledger.survey().unsettled == ("harness-run",), label


@pytest.mark.parametrize(
    "label,started_for,published",
    [
        ("a later reservation's publication", "RES-1", "RES-2"),
        ("an earlier reservation's publication", "RES-2", "RES-1"),
        ("an empty publication identity", "RES-1", ""),
    ],
)
def test_a_release_publication_disagreeing_with_the_start_refuses(
    label, started_for, published
):
    """`ReleasePublication.reservation_id` against the stored start, both ways."""
    laboratory = Laboratory()
    _running_reservation(laboratory, started_for, "harness-run")

    refused = laboratory.ledger.complete(
        run_id="harness-run",
        participant=Participant.HARNESS_CLI,
        author="root",
        at="t4",
        observation=observed(Participant.HARNESS_CLI),
        release_publication=_publication(published),
    )

    assert refused.published is False, label
    assert any("PR-20260911-R5-1" in reason for reason in refused.reasons), label
    assert laboratory.ledger.read_run("harness-run").state.phase is RunPhase.IN_PROGRESS


def test_the_published_evidence_is_taken_from_the_stored_start():
    """`CompletionEvidence.reservation_id` is derived, not copied from the caller.

    The caller cannot choose it: the writer reads the stored start and writes
    that value. So the fourth of the five values agrees with the first by
    construction, and the reader's comparison is what catches bytes written by
    anything else.
    """
    laboratory = Laboratory()
    _running_reservation(laboratory, "RES-1", "RES-1-harness")

    concluded = laboratory.conclude("RES-1", "RES-1-harness")

    assert concluded.concluded is True
    stored = laboratory.ledger.read_run("RES-1-harness")
    assert stored.state.evidence.reservation_id == "RES-1"
    assert stored.state.evidence.run_id == "RES-1-harness"
    assert stored.state.evidence.conditions == HARNESS_CONDITIONS
    assert concluded.reservation_id == "RES-1"


def test_the_terminal_result_reports_the_reservation_it_concluded():
    """The fifth value: the terminal result's own reservation identity."""
    laboratory = Laboratory()
    _running_reservation(laboratory, "RES-1", "RES-1-harness")

    concluded = laboratory.conclude("RES-1", "RES-1-harness")

    assert concluded.reservation_id == "RES-1"
    assert concluded.run_id == "RES-1-harness"
    assert concluded.release_entry.published is True
    assert concluded.completion.published is True


def test_the_binding_is_not_inferred_from_the_run_name():
    """**No prefix, suffix or other string convention is checked.**

    A run named `RES-9-harness` that was started for `RES-1` is a run belonging
    to `RES-1`, and concluding `RES-1` against it succeeds. Concluding `RES-9`
    against it refuses, even though the name spells `RES-9`. This test fails the
    moment an implementation starts reading the reservation out of the filename.
    """
    misleading = Laboratory()
    _running_reservation(misleading, "RES-1", "RES-9-harness")

    wrong = misleading.conclude("RES-9", "RES-9-harness")
    assert wrong.concluded is False
    assert any("PR-20260911-R5-1" in reason for reason in wrong.refusals)

    right = misleading.conclude("RES-1", "RES-9-harness")
    assert right.concluded is True
    assert misleading.ledger.survey().completed == ("RES-9-harness",)


# ---------------------------------------------------------------------------
# The writer reads the stored start before it derives anything
# ---------------------------------------------------------------------------


def test_a_completion_of_a_run_nobody_started_refuses():
    """There is no stored start to derive a profile or a reservation from."""
    laboratory = Laboratory()
    laboratory.initialize()

    refused = laboratory.ledger.complete(
        run_id="RES-1-harness",
        participant=Participant.HARNESS_CLI,
        author="root",
        at="t4",
        observation=observed(Participant.HARNESS_CLI),
        release_publication=_publication("RES-1"),
    )

    assert refused.published is False
    assert refused.refusal is PublicationRefusal.UNREADABLE_PREDECESSOR
    assert any("absent" in reason for reason in refused.reasons)
    assert laboratory.ledger.survey().settled is True


def test_concluding_a_non_harness_run_refuses():
    """A release settles the harness's own run and no other participant's.

    The six participants' runs end on their own observed external conditions. A
    release offered as the web suite's completion is a lifecycle fact asserted
    about a run whose conditions are facts about processes and trees.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    laboratory.append(
        EntryKind.ADMITTED, author="executor RES-1", at="t1", reservation="RES-1"
    )
    assert laboratory.ledger.begin(
        run_id="web-1", participant=Participant.WEB_SUITE, author="ubuntu", at="t1"
    ).published is True
    laboratory.append(
        EntryKind.RUNNING, author="executor RES-1", at="t2", reservation="RES-1"
    )

    outcome = laboratory.conclude("RES-1", "web-1")

    assert outcome.concluded is False
    assert outcome.release_entry is None
    assert any(
        f"was started by {Participant.WEB_SUITE.value!r}" in reason
        for reason in outcome.refusals
    )
    assert laboratory.ledger.survey().unsettled == ("web-1",)


def test_concluding_an_already_settled_run_refuses():
    """A settled run is not concluded twice, and a recovered one is terminal."""
    laboratory = Laboratory()
    _running_reservation(laboratory, "RES-1", "RES-1-harness")
    assert laboratory.conclude("RES-1", "RES-1-harness").concluded is True
    before = laboratory.record.read_record_bytes()

    again = laboratory.conclude("RES-1", "RES-1-harness")

    assert again.concluded is False
    assert again.release_entry is None
    assert any("already 'completed'" in reason for reason in again.refusals)
    assert laboratory.record.read_record_bytes() == before


def test_the_completion_profile_still_comes_from_the_stored_start():
    """R4-2's rule, preserved where the r6 writer now reads the start first.

    The caller's participant is compared with the stored one **before** any
    profile is chosen, so the refusal names the claim rather than the conditions
    that happened not to match.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    assert laboratory.ledger.begin(
        run_id="web-1", participant=Participant.WEB_SUITE, author="ubuntu", at="t1"
    ).published is True

    refused = laboratory.ledger.complete(
        run_id="web-1",
        participant=Participant.FOUNDRY_TESTS,
        author="ubuntu",
        at="t2",
        observation=observed(Participant.FOUNDRY_TESTS),
    )

    assert refused.published is False
    assert refused.refusal is PublicationRefusal.INVALID_HISTORY
    assert any("PR-20260911-R4-2" in reason for reason in refused.reasons)
    assert laboratory.ledger.survey().unsettled == ("web-1",)


# ---------------------------------------------------------------------------
# Preserved controls, and the sequential lifecycle from stored bytes
# ---------------------------------------------------------------------------


def test_a_matching_start_request_release_and_completion_succeeds():
    """The positive control: all five values agree and the successor admits."""
    laboratory = Laboratory()
    _running_reservation(laboratory, "RES-1", "RES-1-harness")

    concluded = laboratory.conclude("RES-1", "RES-1-harness")

    assert concluded.decision is ReservationState.RELEASED
    assert concluded.release_entry.barriers == ("record-data", "record-entry")
    assert concluded.concluded is True
    assert concluded.refusals == ()
    laboratory.fs.restart_process()
    survey = laboratory.ledger.survey()
    assert survey.completed == ("RES-1-harness",)
    assert survey.settled is True
    admission = laboratory.admit(reservation_id="RES-2")
    assert admission.may_proceed is True
    assert admission.history.disposition is PredecessorDisposition.RELEASED


def test_sequential_reservations_with_distinct_harness_runs_from_stored_bytes():
    """Three reservations, three distinct runs, every decision read from bytes.

    A process restart precedes every admission, so nothing carries across from
    the writer that produced the record. Each conclusion is checked against the
    start **its own** reservation published, and the second reservation cannot
    settle the first one's run or be settled by it.
    """
    laboratory = Laboratory()
    laboratory.initialize()

    for index, reservation in enumerate(("RES-1", "RES-2", "RES-3"), start=1):
        run = f"{reservation}-harness"
        laboratory.fs.restart_process()
        admission = laboratory.admit(reservation_id=reservation)
        assert admission.may_proceed is True, reservation
        assert laboratory.append(
            EntryKind.ADMITTED,
            author=f"executor {reservation}",
            at=f"t{index}0",
            reservation=reservation,
        ).published is True
        assert laboratory.begin_harness(run, reservation, at=f"t{index}1").published
        assert laboratory.append(
            EntryKind.RUNNING,
            author=f"executor {reservation}",
            at=f"t{index}2",
            reservation=reservation,
        ).published is True

        # The previous reservation's run may not be settled by this one, and this
        # run may not be settled by any other reservation.
        for other in ("RES-1", "RES-2", "RES-3"):
            if other == reservation:
                continue
            crossed = laboratory.conclude(other, run)
            assert crossed.concluded is False, (reservation, other)
            assert crossed.release_entry is None, (reservation, other)

        laboratory.fs.restart_process()
        assert laboratory.conclude(reservation, run).concluded is True, reservation

    laboratory.fs.restart_process()
    survey = laboratory.ledger.survey()
    assert survey.completed == ("RES-1-harness", "RES-2-harness", "RES-3-harness")
    assert survey.settled is True
    assert laboratory.admit(reservation_id="RES-4").may_proceed is True
    # No retired identity may be readmitted: the reuse refusal is the reservation
    # history's, and it is the append of a second `admitted` that refuses.
    assert laboratory.append(
        EntryKind.ADMITTED, author="executor RES-2", at="t40", reservation="RES-2"
    ).published is False
    assert laboratory.append(
        EntryKind.ADMITTED, author="executor RES-4", at="t40", reservation="RES-4"
    ).published is True


def test_a_failure_between_the_release_and_the_completion_blocks_and_recovers():
    """The intermediate state for a **correctly bound** run, and its recovery.

    The release publication crosses its barriers and the completion's own
    containing-entry barrier fails. The reservation reads RELEASED, the harness's
    run is still started, and the ledger refuses every successor until an
    operator publishes an attributed recovery for it.
    """
    laboratory = Laboratory()
    _running_reservation(laboratory, "RES-1", "RES-1-harness")

    outcome = laboratory.conclude(
        "RES-1", "RES-1-harness", fail_completion_at="rename"
    )

    assert outcome.release_entry.published is True
    assert outcome.completion.published is False
    assert outcome.concluded is False
    assert any("was not completed" in reason for reason in outcome.refusals)

    laboratory.fs.restart_process()
    blocked = laboratory.admit(reservation_id="RES-2")
    assert blocked.history.disposition is PredecessorDisposition.RELEASED
    assert blocked.may_proceed is False
    assert blocked.runs.unreadable == ("RES-1-harness.tmp",)

    laboratory.remove_temporary(laboratory.runs_directory, "RES-1-harness.tmp")
    assert laboratory.ledger.survey().unsettled == ("RES-1-harness",)
    assert laboratory.admit(reservation_id="RES-2").may_proceed is False
    assert laboratory.ledger.recover(
        run_id="RES-1-harness",
        participant=Participant.HARNESS_CLI,
        author=ATTESTER,
        at="t6",
        reference="ops-2026-09-11-12",
    ).published is True
    assert laboratory.admit(reservation_id="RES-2").may_proceed is True


def test_a_recovered_harness_runs_identity_is_not_reused():
    """The preserved r4 control, with the binding on the start."""
    laboratory = Laboratory()
    laboratory.initialize()
    assert laboratory.begin_harness("RES-1-harness", "RES-1").published is True
    assert laboratory.ledger.recover(
        run_id="RES-1-harness",
        participant=Participant.HARNESS_CLI,
        author=ATTESTER,
        at="t2",
        reference="ops-2026-09-11-13",
    ).published is True

    reused = laboratory.begin_harness("RES-1-harness", "RES-1", at="t3")

    assert reused.published is False
    assert reused.refusal is PublicationRefusal.ALREADY_PUBLISHED
    assert laboratory.begin_harness("RES-2-harness", "RES-2", at="t4").published is True


def test_stale_release_evidence_from_another_reservation_still_refuses():
    """R4-3's step-1 control, unchanged by the binding.

    The evidence is about `RES-1` and the request concludes `RES-2`, and the run
    is correctly bound to `RES-2`, so the binding passes and the **release
    decision** is what refuses. Neither terminal entry is published.
    """
    laboratory = Laboratory()
    _running_reservation(laboratory, "RES-2", "RES-2-harness")

    outcome = laboratory.conclude(
        "RES-2",
        "RES-2-harness",
        evidence=laboratory.release_evidence("RES-1"),
    )

    assert outcome.decision is not ReservationState.RELEASED
    assert outcome.release_entry is None
    assert outcome.completion is None
    assert laboratory.ledger.survey().unsettled == ("RES-2-harness",)


def test_an_injected_lifecycle_fact_is_still_refused():
    """R4-3's writer control, preserved where the writer now reads the start."""
    laboratory = Laboratory()
    _running_reservation(laboratory, "RES-1", "RES-1-harness")

    injected = laboratory.ledger.complete(
        run_id="RES-1-harness",
        participant=Participant.HARNESS_CLI,
        author="root",
        at="t4",
        observation=CompletionObservation(
            observed_by="the executor",
            observed={
                HARNESS_RELEASE_DECIDED: True,
                HARNESS_RELEASE_PUBLISHED: True,
            },
        ),
        release_publication=_publication("RES-1"),
    )

    assert injected.published is False
    assert any("lifecycle-owned fact" in reason for reason in injected.reasons)
    assert laboratory.ledger.survey().unsettled == ("RES-1-harness",)


@pytest.mark.parametrize(
    "participant",
    [p for p in PARTICIPANTS if p is not Participant.HARNESS_CLI],
    ids=[p.name for p in PARTICIPANTS if p is not Participant.HARNESS_CLI],
)
def test_the_six_still_complete_on_their_own_external_conditions(participant):
    """The preserved control for the participants that own no reservation.

    Their start carries the field empty, their completion carries it empty, and
    nothing about the reservation binding is required of them.
    """
    laboratory = Laboratory()
    laboratory.initialize()
    assert laboratory.ledger.begin(
        run_id="run-1", participant=participant, author="ubuntu", at="t1"
    ).published is True

    completed = laboratory.ledger.complete(
        run_id="run-1",
        participant=participant,
        author="ubuntu",
        at="t3",
        observation=observed(participant),
    )

    assert completed.published is True
    stored = laboratory.ledger.read_run("run-1")
    assert stored.ok is True
    assert stored.state.reservation_id == ""
    assert stored.state.evidence.reservation_id == ""
    assert laboratory.ledger.survey().completed == ("run-1",)


# ---------------------------------------------------------------------------
# The contract text, so a claim and its code cite the same strings
# ---------------------------------------------------------------------------


def test_the_reservation_binding_is_stated_with_its_argument():
    """The rule, the five compared values, and the convention it refuses."""
    joined = " ".join(RESERVATION_BINDING)

    assert "names the reservation the run owns" in joined
    assert "exact equality" in joined
    assert "ReservationRequest.reservation_id" in joined
    assert "ReleasePublication.reservation_id" in joined
    assert "CompletionEvidence.reservation_id" in joined
    assert "No identity is inferred from a run name" in joined
    assert "before an append and on read" in joined
    assert "reads the stored start before deriving anything" in joined


def test_the_terminal_order_states_the_binding_step_first():
    """Step 0 precedes the release decision, and the order says why."""
    joined = " ".join(TERMINAL_PUBLICATION_ORDER)

    assert "Check the reservation binding against the stored start" in joined
    assert "no release entry and no completion is published" in joined
    assert "PR-20260911-R5-1" in joined
    assert TERMINAL_PUBLICATION_ORDER[0].startswith("0. ")
    assert TERMINAL_PUBLICATION_ORDER[1].startswith("1. ")


def test_the_schema_version_records_the_incompatibility():
    """r5's records are refused by name rather than reinterpreted."""
    assert RECORD_SCHEMA_VERSION == 2
    assert SUPPORTED_SCHEMA_VERSIONS == frozenset({2})
    assert 1 not in SUPPORTED_SCHEMA_VERSIONS


def test_the_validator_is_the_same_function_on_both_sides():
    """One check for the writer and the survey, not two that can drift."""
    laboratory = Laboratory()
    laboratory.initialize()
    entries = (
        _started(laboratory, "RES-1-harness", Participant.HARNESS_CLI, reservation="RES-1"),
        _completed(laboratory, "RES-1-harness", Participant.HARNESS_CLI, reservation="RES-2"),
    )

    proposed = laboratory.ledger._store("RES-1-harness").semantic_problems(entries)
    plant_run(laboratory, "RES-1-harness", entries)
    stored = check_participant_history(
        laboratory.ledger.read_run("RES-1-harness").parsed.entries,
        run_id="RES-1-harness",
    )

    assert proposed == stored.problems
    assert any("PR-20260911-R5-1" in problem for problem in proposed)
