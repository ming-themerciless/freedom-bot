"""EH-R1, EH-R2 and EH-R2-1, asserted as regressions.

The findings are about what a record can be made to *say*, so most tests here are
a construction that must be refused rather than a computation that must be right.

**EH-R2-1 changed the shape of every one of them, and EH-R3-1 is what happened
when that change was not carried through.** A record no longer carries a
caller-supplied `positive_control_status`; it declares a `CaseRole` and, when that
role is `DEPENDENT`, carries the control's **record**. So a test about a failed
control now has to *build a failed control* — which is the point: the fixture that
used to be the string `"failed"` is now a record that classifies as failed from
its own observations, and nothing weaker will do.

Every construction below therefore declares its role explicitly. A test whose name
says it exercises a failed control supplies a control record that failed; a test
whose name says a reference is malformed is otherwise a valid dependent case, so
that it reaches the rule it is named for rather than tripping over a second
missing field on the way.
"""
from __future__ import annotations

import json

import pytest

from tools.phase_5_0_evidence import EVIDENCE_SCHEMA_VERSION
from tools.phase_5_0_evidence.errors import ObservationRefused
from tools.phase_5_0_evidence.records import (
    CaseRole,
    CleanupState,
    EvidenceRecord,
    ObservedIdentity,
    OperationKind,
    Outcome,
    Status,
    classify,
    deserialize_records,
    index_by_case_id,
    records_digest,
    serialize_records,
    summarize,
    validate_artifact,
)


def identity(**overrides) -> ObservedIdentity:
    base = dict(
        uid=1001,
        gid=1001,
        groups=frozenset({1001, 5000}),
        cap_prm=0x200,
        cap_eff=0x200,
        cap_inh=0x200,
        cap_amb=0x200,
        cap_bnd=0x200,
        securebits=0x4,
        no_new_privs=0,
    )
    base.update(overrides)
    return ObservedIdentity(**base)


def record(**overrides) -> EvidenceRecord:
    """A standalone record — a read, needing no control and usable as none.

    `STANDALONE` is the default here because it is the inert role: it names no
    control and may not be referenced as one, so a test that wants a place in the
    reference graph has to say so.
    """
    base = dict(
        case_id="C-1",
        band="filesystem",
        target_identity="freedomsheet",
        operation="open(O_WRONLY)",
        expected=Outcome.returned(),
        observed=Outcome.returned(),
        case_role=CaseRole.STANDALONE,
    )
    base.update(overrides)
    return EvidenceRecord.for_case(**base)


def control(**overrides) -> EvidenceRecord:
    """A record the band declared a **control**, passing unless told otherwise."""
    base = dict(case_id="C-1", case_role=CaseRole.CONTROL)
    base.update(overrides)
    return record(**base)


def dependent(control_record: EvidenceRecord, **overrides) -> EvidenceRecord:
    """A record interpreted beside `control_record`, and beside nothing else."""
    base = dict(
        case_id="P-1",
        band=control_record.band,
        expected=Outcome.refused("EPERM"),
        observed=Outcome.refused("EPERM"),
        case_role=CaseRole.DEPENDENT,
        positive_control_case_id=control_record.case_id,
        positive_control=control_record,
    )
    base.update(overrides)
    return record(**base)


#: The three ways a control can fail to be a passing control, each built from
#: observations rather than asserted. This is the EH-R3-1 correction in one place:
#: the parametrisation used to be `[Status.FAILED, Status.INCONCLUSIVE,
#: Status.NOT_RUN]` — three strings a caller chose — and it is now three records.
def failed_control() -> EvidenceRecord:
    return control(expected=Outcome.returned(), observed=Outcome.refused("EPERM"))


def inconclusive_control() -> EvidenceRecord:
    return control(identity=identity(cap_amb=0x0), expected_identity=identity())


def not_run_control() -> EvidenceRecord:
    return control(observed=None)


NON_PASSING_CONTROLS = [
    ("failed", failed_control),
    ("inconclusive", inconclusive_control),
    ("not_run", not_run_control),
]


# ---------------------------------------------------------------------------
# EH-R1 — the classifier is authoritative
# ---------------------------------------------------------------------------


def test_an_expected_success_observed_as_a_refusal_cannot_be_serialized_as_passed() -> None:
    derived = record(expected=Outcome.returned(), observed=Outcome.refused("EPERM"))
    assert derived.status is Status.FAILED

    with pytest.raises(ObservationRefused) as refusal:
        EvidenceRecord(
            case_id="C-1",
            band="filesystem",
            target_identity="freedomsheet",
            preconditions=(),
            operation="open(O_WRONLY)",
            expected=Outcome.returned(),
            observed=Outcome.refused("EPERM"),
            status=Status.PASSED,
            cleanup_state=CleanupState.NOT_APPLICABLE,
            case_role=CaseRole.STANDALONE,
            reason="Observed returned, as expected.",
        )
    assert "contradict itself" in str(refusal.value)


def test_an_identity_mismatch_is_inconclusive_and_can_be_neither_passed_nor_failed() -> None:
    mismatched = record(
        identity=identity(cap_amb=0x0),
        expected_identity=identity(),
        observed=Outcome.returned(),
    )
    assert mismatched.status is Status.INCONCLUSIVE
    assert "cap_amb" in mismatched.reason

    for asserted in (Status.PASSED, Status.FAILED):
        with pytest.raises(ObservationRefused):
            EvidenceRecord(
                case_id="C-1",
                band="capability",
                target_identity="E2",
                preconditions=(),
                operation="FS_IOC_SETFLAGS",
                expected=Outcome.returned(),
                observed=Outcome.returned(),
                status=asserted,
                cleanup_state=CleanupState.NOT_APPLICABLE,
                case_role=CaseRole.STANDALONE,
                identity=identity(cap_amb=0x0),
                expected_identity=identity(),
                reason="anything",
            )


@pytest.mark.parametrize(
    "label, build_control", NON_PASSING_CONTROLS, ids=[c[0] for c in NON_PASSING_CONTROLS]
)
def test_a_negative_case_whose_control_did_not_pass_cannot_be_passed(
    label: str, build_control
) -> None:
    """The control is a **record**, and its status is read off it.

    Each control below is built from its own observations and classifies as
    failed, inconclusive or not-run without anyone saying so; the dependent case
    beside it is inconclusive; and a hand-built record asserting `passed` beside
    the same control is refused.
    """
    control_record = build_control()
    assert control_record.status is not Status.PASSED

    derived = dependent(control_record)
    assert derived.status is Status.INCONCLUSIVE
    assert control_record.status.value in derived.reason

    with pytest.raises(ObservationRefused):
        EvidenceRecord(
            case_id="P-1",
            band="filesystem",
            target_identity="freedomsheet",
            preconditions=(),
            operation="open(O_WRONLY)",
            expected=Outcome.refused("EPERM"),
            observed=Outcome.refused("EPERM"),
            status=Status.PASSED,
            cleanup_state=CleanupState.NOT_APPLICABLE,
            case_role=CaseRole.DEPENDENT,
            positive_control_case_id=control_record.case_id,
            positive_control=control_record,
            reason="Observed EPERM, as expected.",
        )


def test_a_passing_control_lets_an_otherwise_matching_dependent_case_pass() -> None:
    """The other half of the rule, so the three inconclusive cases above are not
    simply *"a dependent case can never pass"*."""
    passing = control()
    assert passing.status is Status.PASSED
    assert dependent(passing).status is Status.PASSED


def test_an_absent_observation_is_not_run_and_never_passed() -> None:
    assert record(observed=None).status is Status.NOT_RUN

    with pytest.raises(ObservationRefused):
        EvidenceRecord(
            case_id="C-1",
            band="filesystem",
            target_identity="freedomsheet",
            preconditions=(),
            operation="open(O_WRONLY)",
            expected=Outcome.returned(),
            observed=None,
            status=Status.PASSED,
            cleanup_state=CleanupState.NOT_APPLICABLE,
            case_role=CaseRole.STANDALONE,
            reason="Observed returned, as expected.",
        )


@pytest.mark.parametrize("field", ["status", "reason"])
def test_tampering_with_a_serialized_status_or_reason_is_refused_on_read_back(field: str) -> None:
    raw = serialize_records([record(expected=Outcome.returned(), observed=Outcome.refused("EPERM"))])
    payload = json.loads(raw)
    payload[0][field] = "passed" if field == "status" else "Observed returned, as expected."
    tampered = (json.dumps(payload) + "\n").encode("utf-8")

    with pytest.raises(ObservationRefused):
        deserialize_records(tampered)


def test_an_attribution_refusal_can_only_move_a_result_away_from_passed() -> None:
    """The one caller-supplied input to `classify` beyond the observations.

    It is safe because it is one-directional: there is no value of it that turns a
    failure into a pass. Asserted rather than argued.
    """
    for expected, observed in (
        (Outcome.returned(), Outcome.returned()),
        (Outcome.returned(), Outcome.refused("EPERM")),
        (Outcome.refused("EPERM"), Outcome.refused("EACCES")),
    ):
        status, _ = classify(
            expected=expected, observed=observed, attribution_refusal="mis-provisioned"
        )
        assert status is Status.INCONCLUSIVE


def test_a_record_carrying_non_scalar_detail_is_refused() -> None:
    with pytest.raises(ObservationRefused) as refusal:
        record(detail={"content": ["a", "file"]})
    assert "do not belong in an evidence artifact" in str(refusal.value)


# ---------------------------------------------------------------------------
# EH-R2-1 — the control is a cross-record fact, and the role is declared
# ---------------------------------------------------------------------------


def test_the_serialized_schema_carries_no_duplicated_control_status() -> None:
    """The finding's root cause, asserted as an absence.

    EH-R2-1 was that a dependent record stored a copy of its control's status and
    classification trusted the copy. Recomputing from the copy proved nothing, so
    the copy is gone from the schema — and this test is what keeps a future edit
    from reintroducing it as a *"presentational"* field.
    """
    passing = control()
    stored = json.loads(serialize_records([passing, dependent(passing)]))
    for item in stored:
        assert "positive_control_status" not in item
    assert stored[1]["positive_control_case_id"] == "C-1"
    assert {item["case_role"] for item in stored} == {"control", "dependent"}


def test_a_role_and_a_reference_that_disagree_are_refused_in_either_direction() -> None:
    """Naming a reference says *"this case needs a control"*. It does not say
    *"this case may be used as one"*, so both facts are declared and compared."""
    with pytest.raises(ObservationRefused) as no_reference:
        record(case_role=CaseRole.DEPENDENT)
    assert "names no positive control" in str(no_reference.value)

    for role in (CaseRole.STANDALONE, CaseRole.CONTROL):
        with pytest.raises(ObservationRefused) as unwanted:
            record(case_role=role, positive_control_case_id="C-9")
        assert "names a positive control" in str(unwanted.value)


def test_a_dependent_case_given_no_control_record_is_refused() -> None:
    with pytest.raises(ObservationRefused) as refusal:
        record(case_role=CaseRole.DEPENDENT, positive_control_case_id="C-9")
    assert "was not given that record" in str(refusal.value)


def test_a_case_that_names_itself_as_its_own_control_is_refused() -> None:
    passing = control()
    with pytest.raises(ObservationRefused) as refusal:
        dependent(passing, case_id="C-1")
    assert "names itself" in str(refusal.value)


def test_a_reference_resolved_to_the_wrong_record_is_refused() -> None:
    passing = control()
    with pytest.raises(ObservationRefused) as refusal:
        record(
            case_id="P-1",
            case_role=CaseRole.DEPENDENT,
            positive_control_case_id="C-2",
            positive_control=passing,
        )
    assert "was given case 'C-1'" in str(refusal.value)


def test_a_control_from_another_band_is_refused() -> None:
    """`filesystem` and `identity` both have a case called `C-1`, so an unscoped
    id resolves to whichever band happens to be read first."""
    elsewhere = control(band="identity")
    with pytest.raises(ObservationRefused) as refusal:
        dependent(elsewhere, band="filesystem")
    assert "band 'identity'" in str(refusal.value)


def test_an_inadmissible_control_reference_is_refused() -> None:
    """A read is not a control. The band has to have declared one."""
    read = record(case_id="C-1", case_role=CaseRole.STANDALONE)
    with pytest.raises(ObservationRefused) as refusal:
        record(
            case_id="P-1",
            band="filesystem",
            expected=Outcome.refused("EPERM"),
            observed=Outcome.refused("EPERM"),
            case_role=CaseRole.DEPENDENT,
            positive_control_case_id="C-1",
            positive_control=read,
        )
    assert "that case is a standalone" in str(refusal.value)


def test_a_duplicate_case_id_in_one_artifact_is_refused() -> None:
    twice = [record(case_id="C-1"), record(case_id="C-1", observed=Outcome.refused("EPERM"))]
    with pytest.raises(ObservationRefused) as refusal:
        index_by_case_id(twice)
    assert "appears twice" in str(refusal.value)
    with pytest.raises(ObservationRefused):
        serialize_records(twice)


def test_an_artifact_whose_control_is_absent_from_it_is_refused() -> None:
    """A control in another artifact is a control this artifact cannot show."""
    passing = control()
    with pytest.raises(ObservationRefused) as refusal:
        serialize_records([dependent(passing)])
    assert "does not contain" in str(refusal.value)


def test_an_artifact_whose_control_record_is_not_the_one_it_publishes_is_refused() -> None:
    """Per-record rules cannot see this: the dependent case was classified beside
    a control that satisfies every one of them and is not in the artifact."""
    published = control()
    fabricated = control(detail={"note": "a different run"})
    assert fabricated != published
    with pytest.raises(ObservationRefused) as refusal:
        validate_artifact([published, dependent(fabricated)])
    assert "not the 'C-1' this artifact holds" in str(refusal.value)


@pytest.mark.parametrize(
    "label, build_control", NON_PASSING_CONTROLS, ids=[c[0] for c in NON_PASSING_CONTROLS]
)
def test_a_stored_artifact_cannot_be_edited_into_a_pass_by_its_control(
    label: str, build_control
) -> None:
    """The replacement for *"changing the duplicated status cannot create a pass"*.

    There is no duplicated status left to change, so the only way to make the
    dependent record's stored `passed` true is to forge a whole control record
    that classifies as passed from its own observations. Editing the dependent
    record's status is refused, and so is editing the control's.
    """
    control_record = build_control()
    stored = json.loads(serialize_records([control_record, dependent(control_record)]))

    stored[1]["status"] = "passed"
    stored[1]["reason"] = "Observed EPERM, as expected."
    with pytest.raises(ObservationRefused):
        deserialize_records((json.dumps(stored) + "\n").encode("utf-8"))

    stored[0]["status"] = "passed"
    with pytest.raises(ObservationRefused):
        deserialize_records((json.dumps(stored) + "\n").encode("utf-8"))


def test_a_self_referential_or_cyclic_stored_artifact_is_refused() -> None:
    """Checked before anything is constructed, so a cycle is reported as a cycle
    rather than by recursing into it."""
    passing = control()
    stored = json.loads(serialize_records([passing, dependent(passing)]))

    itself = [dict(stored[1], positive_control_case_id="P-1")]
    with pytest.raises(ObservationRefused) as loop:
        deserialize_records((json.dumps(itself) + "\n").encode("utf-8"))
    assert "names itself" in str(loop.value)

    cycle = [
        dict(stored[0], case_role="dependent", positive_control_case_id="P-1"),
        stored[1],
    ]
    with pytest.raises(ObservationRefused) as cyclic:
        deserialize_records((json.dumps(cycle) + "\n").encode("utf-8"))
    assert "form a cycle" in str(cyclic.value)


def test_a_stored_reference_to_a_record_the_artifact_lacks_is_refused() -> None:
    passing = control()
    stored = json.loads(serialize_records([passing, dependent(passing)]))
    with pytest.raises(ObservationRefused) as refusal:
        deserialize_records((json.dumps([stored[1]]) + "\n").encode("utf-8"))
    assert "does not contain" in str(refusal.value)


def test_record_order_does_not_affect_what_a_reference_resolves_to() -> None:
    """Records are built control-first, so a dependent case stored before its
    control resolves to the same record and classifies the same way."""
    passing = control()
    forwards = serialize_records([passing, dependent(passing)])
    backwards_payload = list(reversed(json.loads(forwards)))
    backwards = (json.dumps(backwards_payload) + "\n").encode("utf-8")

    restored = {r.case_id: r for r in deserialize_records(backwards)}
    assert restored["P-1"].status is Status.PASSED
    assert restored["P-1"].positive_control == restored["C-1"]


# ---------------------------------------------------------------------------
# EH-R2 — one closed outcome grammar
# ---------------------------------------------------------------------------

VALID_FORMS = [
    ("syscall success", Outcome.returned()),
    ("syscall refusal", Outcome.refused("EPERM")),
    ("command success", Outcome.exited(0)),
    ("command refusal", Outcome.exited(3)),
    ("observation", Outcome.read("FS_APPEND_FL")),
    (
        "documented nonzero success",
        Outcome.exited(2, nonzero_success_rationale="a documented case requires it"),
    ),
]


@pytest.mark.parametrize("label, outcome", VALID_FORMS, ids=[f[0] for f in VALID_FORMS])
def test_every_valid_outcome_form_round_trips(label: str, outcome: Outcome) -> None:
    assert Outcome.from_mapping(outcome.to_mapping()) == outcome


REJECTED = [
    (
        "two representations",
        dict(kind=OperationKind.SYSCALL, succeeded=False, errno_name="EPERM", exit_status=1),
    ),
    (
        "three representations",
        dict(
            kind=OperationKind.SYSCALL,
            succeeded=False,
            errno_name="EPERM",
            exit_status=0,
            value="x",
        ),
    ),
    ("errno with success", dict(kind=OperationKind.SYSCALL, succeeded=True, errno_name="EPERM")),
    ("exit zero as refusal", dict(kind=OperationKind.COMMAND, succeeded=False, exit_status=0)),
    (
        "nonzero exit as success without a rationale",
        dict(kind=OperationKind.COMMAND, succeeded=True, exit_status=3),
    ),
    (
        "nonzero exit as success with a blank rationale",
        dict(
            kind=OperationKind.COMMAND,
            succeeded=True,
            exit_status=3,
            nonzero_success_rationale="   ",
        ),
    ),
    ("blank errno", dict(kind=OperationKind.SYSCALL, succeeded=False, errno_name="  ")),
    ("non-symbolic errno", dict(kind=OperationKind.SYSCALL, succeeded=False, errno_name="1")),
    ("lower-case errno", dict(kind=OperationKind.SYSCALL, succeeded=False, errno_name="eperm")),
    ("unknown errno", dict(kind=OperationKind.SYSCALL, succeeded=False, errno_name="ENOTAREALERRNO")),
    ("syscall refusal with no errno", dict(kind=OperationKind.SYSCALL, succeeded=False)),
    ("syscall carrying an exit status", dict(kind=OperationKind.SYSCALL, succeeded=True, exit_status=0)),
    ("command with no exit status", dict(kind=OperationKind.COMMAND, succeeded=True)),
    ("command carrying a value", dict(kind=OperationKind.COMMAND, succeeded=True, value="x")),
    ("observation with no value", dict(kind=OperationKind.OBSERVATION, succeeded=True)),
    ("observation that failed", dict(kind=OperationKind.OBSERVATION, succeeded=False, value="x")),
    (
        "rationale on a syscall",
        dict(kind=OperationKind.SYSCALL, succeeded=True, nonzero_success_rationale="why"),
    ),
    ("exit status out of range", dict(kind=OperationKind.COMMAND, succeeded=False, exit_status=999)),
]


@pytest.mark.parametrize("label, kwargs", REJECTED, ids=[r[0] for r in REJECTED])
def test_every_rejected_outcome_combination_is_refused(label: str, kwargs: dict) -> None:
    with pytest.raises(ObservationRefused):
        Outcome(**kwargs)


def test_deserialization_refuses_an_unknown_field_rather_than_discarding_it() -> None:
    mapping = dict(Outcome.returned().to_mapping())
    mapping["signal"] = 9
    with pytest.raises(ObservationRefused) as refusal:
        Outcome.from_mapping(mapping)
    assert "unknown" in str(refusal.value)


def test_deserialization_refuses_a_missing_field_rather_than_defaulting_it() -> None:
    mapping = dict(Outcome.returned().to_mapping())
    del mapping["exit_status"]
    with pytest.raises(ObservationRefused):
        Outcome.from_mapping(mapping)


def test_a_record_field_this_schema_does_not_know_is_refused_rather_than_ignored() -> None:
    """The record-level counterpart, and the reason a stale `positive_control_
    status` in a stored artifact cannot be quietly tolerated."""
    stored = json.loads(serialize_records([record()]))
    stored[0]["positive_control_status"] = "passed"
    with pytest.raises(ObservationRefused) as refusal:
        deserialize_records((json.dumps(stored) + "\n").encode("utf-8"))
    assert "positive_control_status" in str(refusal.value)


def test_an_unknown_case_role_is_refused() -> None:
    stored = json.loads(serialize_records([record()]))
    stored[0]["case_role"] = "witness"
    with pytest.raises(ObservationRefused) as refusal:
        deserialize_records((json.dumps(stored) + "\n").encode("utf-8"))
    assert "not a case role" in str(refusal.value)


def test_a_kind_mismatch_between_expected_and_observed_fails_rather_than_comparing() -> None:
    """`P-9` expects a value and can observe an `ENOTTY`. That is a failed probe."""
    derived = record(expected=Outcome.read("FS_APPEND_FL"), observed=Outcome.refused("ENOTTY"))
    assert derived.status is Status.FAILED
    assert "syscall result" in derived.reason


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


def test_serialization_is_byte_identical_for_the_same_observations() -> None:
    first = [record(), record(case_id="C-2", observed=Outcome.refused("EPERM"),
                             expected=Outcome.refused("EPERM"))]
    second = [record(), record(case_id="C-2", observed=Outcome.refused("EPERM"),
                              expected=Outcome.refused("EPERM"))]
    assert serialize_records(first) == serialize_records(second)
    assert records_digest(first) == records_digest(second)
    assert serialize_records(first).endswith(b"\n")


def test_the_digest_changes_when_the_evidence_changes() -> None:
    passing = [record()]
    failing = [record(observed=Outcome.refused("EPERM"))]
    assert records_digest(passing) != records_digest(failing)


def test_a_full_round_trip_preserves_every_field() -> None:
    isolating = control(
        case_id="JNL-50-4-control",
        band="capability",
        target_identity="E2",
        operation="FS_IOC_SETFLAGS clearing FS_IMMUTABLE_FL on a freedomsheet-owned file",
        expected=Outcome.returned(),
        observed=Outcome.returned(),
        identity=identity(),
        expected_identity=identity(),
        cleanup_state=CleanupState.CLEAN,
    )
    original = record(
        case_id="JNL-50-4",
        band="capability",
        target_identity="E2",
        operation="FS_IOC_SETFLAGS clearing FS_IMMUTABLE_FL on the root-owned seal",
        expected=Outcome.refused("EPERM"),
        observed=Outcome.refused("EPERM"),
        identity=identity(),
        expected_identity=identity(),
        case_role=CaseRole.DEPENDENT,
        positive_control_case_id="JNL-50-4-control",
        positive_control=isolating,
        preconditions=("the launching bounding set holds every required capability",),
        cleanup_state=CleanupState.CLEAN,
        detail={"path": "/var/lib/fb-evidence-r1/journal/000001.seal", "inode_owner": "root"},
    )
    assert original.status is Status.PASSED

    restored = deserialize_records(serialize_records([isolating, original]))
    assert restored == (isolating, original)
    assert restored[1].positive_control == restored[0]


def test_an_artifact_from_another_schema_version_is_refused() -> None:
    payload = json.loads(serialize_records([record()]))
    payload[0]["schema_version"] = EVIDENCE_SCHEMA_VERSION + 1
    with pytest.raises(ObservationRefused):
        deserialize_records((json.dumps(payload) + "\n").encode("utf-8"))


def test_summarize_counts_every_status_in_a_fixed_order() -> None:
    counts = summarize(
        [
            record(),
            record(case_id="C-2", observed=Outcome.refused("EPERM")),
            record(case_id="C-3", observed=None),
        ]
    )
    assert list(counts) == ["passed", "failed", "inconclusive", "not_run"]
    assert counts == {"passed": 1, "failed": 1, "inconclusive": 0, "not_run": 1}


def test_an_identity_mask_that_is_not_an_integer_is_refused() -> None:
    with pytest.raises(ObservationRefused):
        identity(cap_bnd="0x200")
    with pytest.raises(ObservationRefused):
        identity(groups={1001})
