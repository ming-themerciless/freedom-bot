"""The journal generation lifecycle: creation, sealing, registration, and the
five refusals P5.0-R5 needs evidence for — missing, corrupt, reset, stale and
cross-generation — plus the recovery path.

Two actors, two refusals, and they are different refusals (§2.13.6). **W** is the
writer, at start and before each dispatch; its refusal is *refuse new Sheet
mutations*. **C** is the coordinator, at `observe`; its refusal is *record no
`dispatch_journal_clear` row*, which makes the activation trigger refuse.

## Why a reset can never look like an empty history

§2.13.5: a fresh journal file with no records is indistinguishable from a
deliberately emptied one **unless the generation is anchored outside the file**.
It is: `seal_body_digest` is sealed under `chattr +i`, record 0's `prev_hash`
**is** that digest, and the registered row in PostgreSQL carries the same values.
So an emptied journal fails `W13` against a genesis it can no longer derive, and
a replaced journal fails `W7` against `fstat`.

`classify_generation_state()` is that comparison, and it is written so that each
of the five conditions produces its **own named refusal code** rather than a
generic failure — because §2.13.6's whole point is that a refusal names the field
it refused on, and stop condition **10h** forbids a detector that fires only when
some other, differently named field happens to differ.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from .errors import ObservationRefused
from .records import CaseRole, CleanupState, EvidenceRecord, Outcome, Status

BAND = "journal"

#: The writer's refusal family, and the coordinator's. They are separate because
#: the actors are separate and their refusals mean different things.
WRITER_REFUSALS: Mapping[str, str] = {
    "SW-J04": "record 0 does not derive from the seal body — the seal was altered "
              "with the journal left alone (F-1a), or the genesis record was "
              "altered with the seal left alone (F-2)",
    "SW-J09": "a mid-chain record was rewritten in place",
    "SW-J11": "fstat's st_dev or st_ino does not equal BND.journal_device / "
              "BND.journal_inode — the journal file was replaced (F-5, F-10, F-11)",
    "SW-J17": "the seal is unreadable, so the writer cannot perform the startup "
              "validation §2.13.5b requires of it",
    "SW-J22": "the deployed writer's manifest digest does not equal "
              "SB.writer_deployment_digest — redeployed without a rotation (F-6)",
    "SW-J23": "/etc/machine-id does not equal SB.host_machine_id",
    "SW-J24": "the binding is longer or shorter than SB.binding_format_version "
              "permits, or BND.genesis_record_digest disagrees with the value "
              "derived from SB",
    "SW-J25": "the probe report inside the seal does not hash to "
              "SB.probe_report_digest",
    "SW-J26": "PVR is absent, malformed, wrongly owned, wrongly moded, or names a "
              "different commit",
    "SW-J27": "a deployed region-S byte changed, or a file belonging to neither "
              "region was added to the deployed root",
}

COORDINATOR_REFUSALS: Mapping[str, str] = {
    "J-16": "a value read from disk disagrees with the registered row",
    "J-17": "the seal does not derive its own genesis",
    "J-26": "PVR or APR is absent, malformed or disagreeing at observe",
    "J-28": "no approved_source_revisions row matches the seal's revision",
}


class GenerationCondition(str, Enum):
    """The five conditions P5.0-R5 needs evidence for, plus the healthy one."""

    HEALTHY = "healthy"
    #: The journal file, the seal or the `current` symlink is absent.
    MISSING = "missing"
    #: A record does not hash to its recorded `record_hash`, or the seal body does
    #: not hash to `seal_body_digest`.
    CORRUPT = "corrupt"
    #: The journal is present, well-formed and **empty** — the case §2.13.5 says
    #: is indistinguishable from a fresh one without an external anchor.
    RESET = "reset"
    #: The seal describes a deployment or a generation older than the one running.
    STALE = "stale"
    #: A record's `generation_id` is not the seal body's.
    CROSS_GENERATION = "cross_generation"


#: Which refusal each condition must produce, on which side. A condition with no
#: named code cannot be classified, which is stop condition 10h applied to this
#: module: a detector that fires without naming the field it fired on is not a
#: detector for that field.
CONDITION_REFUSALS: Mapping[GenerationCondition, tuple[str, str]] = {
    GenerationCondition.MISSING: ("SW-J17", "J-16"),
    GenerationCondition.CORRUPT: ("SW-J04", "J-17"),
    GenerationCondition.RESET: ("SW-J04", "J-16"),
    GenerationCondition.STALE: ("SW-J22", "J-16"),
    GenerationCondition.CROSS_GENERATION: ("SW-J09", "J-16"),
}


@dataclass(frozen=True, slots=True)
class SealBody:
    """`SB`, the anchor. Every field here is one the writer compares from disk
    with no database reachable."""

    generation_id: str
    binding_format_version: int
    seal_body_digest: str
    genesis_record_digest: str
    journal_device: int
    journal_inode: int
    host_machine_id: str
    writer_deployment_digest: str
    probe_report_digest: str
    source_manifest_digest: str
    predecessor_close_digest: str | None


@dataclass(frozen=True, slots=True)
class JournalObservation:
    """What the writer actually found on disk at start."""

    journal_present: bool
    seal_present: bool
    current_symlink_present: bool
    record_count: int
    genesis_prev_hash: str | None
    first_record_generation_id: str | None
    observed_device: int | None
    observed_inode: int | None
    chain_intact: bool
    observed_deployment_digest: str
    observed_machine_id: str


def diagnose(seal: SealBody, observation: JournalObservation) -> GenerationCondition:
    """Which of §2.13.6's conditions the observation is.

    The order matters and is the writer's own: presence, then identity of the
    inode, then the chain, then the anchor, then the deployment. A missing seal is
    diagnosed before a chain check that would need to read it.
    """
    if not (observation.journal_present and observation.seal_present and observation.current_symlink_present):
        return GenerationCondition.MISSING
    if (
        observation.observed_device != seal.journal_device
        or observation.observed_inode != seal.journal_inode
    ):
        # A replaced inode is F-5/F-10/F-11 and is refused by name at W7.
        return GenerationCondition.CORRUPT
    if observation.record_count == 0:
        return GenerationCondition.RESET
    if (
        observation.first_record_generation_id is not None
        and observation.first_record_generation_id != seal.generation_id
    ):
        return GenerationCondition.CROSS_GENERATION
    if not observation.chain_intact or observation.genesis_prev_hash != seal.seal_body_digest:
        return GenerationCondition.CORRUPT
    if observation.observed_deployment_digest != seal.writer_deployment_digest:
        return GenerationCondition.STALE
    return GenerationCondition.HEALTHY


def classify_generation_state(
    *,
    case_id: str,
    seal: SealBody,
    observation: JournalObservation,
    expected_condition: GenerationCondition,
) -> EvidenceRecord:
    """One lifecycle case: what the writer found, and which refusal it produced.

    The expected outcome is the **named refusal code**, not a bare failure, so a
    case that refuses for the wrong reason fails rather than passing. That is the
    §2.13.6 property the design's claims rest on: the writer's refusal tells a
    responder *what was done*.
    """
    observed_condition = diagnose(seal, observation)
    expected_code = (
        "no refusal"
        if expected_condition is GenerationCondition.HEALTHY
        else CONDITION_REFUSALS[expected_condition][0]
    )
    observed_code = (
        "no refusal"
        if observed_condition is GenerationCondition.HEALTHY
        else CONDITION_REFUSALS[observed_condition][0]
    )
    return EvidenceRecord.for_case(
        case_id=case_id,
        band=BAND,
        target_identity="the writer, at V-W, from disk with no database reachable",
        operation="validate the generation against the sealed binding",
        preconditions=(
            "the seal is chattr +i and the journal chattr +a",
            "no startup check performs a destructive operation against live evidence",
        ),
        expected=Outcome.read(f"{expected_condition.value}:{expected_code}"),
        observed=Outcome.read(f"{observed_condition.value}:{observed_code}"),
        case_role=CaseRole.STANDALONE,
        cleanup_state=CleanupState.NOT_APPLICABLE,
        detail={
            "coordinator_refusal": (
                None
                if observed_condition is GenerationCondition.HEALTHY
                else CONDITION_REFUSALS[observed_condition][1]
            ),
            "record_count": observation.record_count,
            "note": WRITER_REFUSALS.get(observed_code, ""),
        },
    )


@dataclass(frozen=True, slots=True)
class RecoveryStep:
    """One step of §2.13.2b's named operator recovery.

    The procedure is a **named operator procedure**, not an automatic clean: *"No
    separately named privileged cleanup command is introduced, and the automatic
    clean is withdrawn."*
    """

    order: int
    action: str
    rationale: str


RECOVERY_PROCEDURE: tuple[RecoveryStep, ...] = (
    RecoveryStep(1, "read the reported residue paths from the non-zero exit",
                 "the residue is named by absolute path with the operation that "
                 "failed and its errno"),
    RecoveryStep(2, "lsattr each reported artifact",
                 "so the operator learns whether FS_IMMUTABLE_FL or FS_APPEND_FL is "
                 "why removal failed"),
    RecoveryStep(3, "as root, clear FS_IMMUTABLE_FL or FS_APPEND_FL where that is why",
                 "a second automatic attempt by the same code with the same "
                 "authority has no reason to succeed"),
    RecoveryStep(4, "remove the artifacts and then the directories",
                 "one named object at a time; no recursive removal is expressible"),
    RecoveryStep(5, "re-run verify-capability",
                 "both verify-capability and init-generation C0 refuse while …/probe "
                 "or …/probe-ro exists, so the state cannot be walked past from "
                 "either direction"),
)


def classify_recovery(completed_steps: Sequence[int], residue_after: Sequence[str]) -> EvidenceRecord:
    """Whether the recovery procedure actually cleared the S-B state."""
    expected_order = tuple(step.order for step in RECOVERY_PROCEDURE)
    performed = tuple(completed_steps)
    residue = tuple(sorted(residue_after))
    return EvidenceRecord.for_case(
        case_id="JNL-30-recovery",
        band=BAND,
        target_identity="the Operations Owner",
        operation="the §2.13.2b named operator recovery procedure",
        preconditions=("the run left state S-B and named its residue by absolute path",),
        expected=Outcome.read(f"steps {expected_order} completed, no residue"),
        observed=Outcome.read(
            f"steps {performed} completed, "
            + ("no residue" if not residue else f"{len(residue)} paths remain")
        ),
        case_role=CaseRole.STANDALONE,
        cleanup_state=CleanupState.CLEAN if not residue else CleanupState.RESIDUE,
        detail={
            "first_remaining": residue[0] if residue else None,
            "note": "A planted residue from a crashed run is reported and refused, "
                    "never cleaned and never reused (JNL-30).",
        },
    )


#: The four artifacts §2.13.3 puts under `…/journal`, and the order a record
#: names them in. A generation exists when they do; §2.13.5a's R7-A requires that
#: a failure at any stage leaves none of them.
GENERATION_ARTIFACTS = ("journal", "seal", "current", "close")

#: The five points §2.13.5a's R7-A injects a failure at, and the §2.13.2b
#: cleanup that follows them.
FAILURE_STAGES = ("stage-1", "stage-2", "stage-3", "stage-4", "cleanup")

#: The two §2.13.2b cleanup-failure situations `JNL-47`'s recovery case has to
#: keep apart, and what each one's exit code and prior probe result are. They are
#: **expectations**, taken from the reviewed design: a supplied observation is
#: compared with the row, and never the other way round.
CLEANUP_FAILURE_VARIANTS: Mapping[str, tuple[int, str]] = {
    "cleanup-failure-after-probe-failure": (
        3,
        "a probe stage had already failed, so the run was heading for S-A; "
        "cleanup then did not complete, which is S-B and supersedes it",
    ),
    "cleanup-failure-after-passing-probe": (
        3,
        "every probe stage passed, so the run was heading for S-C; cleanup then "
        "did not complete, which is S-B — a passing probe does not make residue "
        "acceptable",
    ),
}


def classify_stage_failure(
    *,
    stage: str,
    artifacts_present: Sequence[str],
    generation_row_present: bool,
) -> EvidenceRecord:
    """`JNL-47`: a failure at one stage leaves no generation — §2.13.5a **R7-A**.

    One record per stage, because *"a failure injected in each of Stage 1 …
    Stage 4 and in cleanup"* is five separate situations and a single record
    covering all five would be five claims nobody could tell apart.

    The expected outcome is fixed: **no journal, no seal, no `current` symbolic
    link, no `.close` manifest and no registration row**. It is stated here from
    the reviewed design, so a stage that left something behind is a failed case
    rather than a differently expected one.
    """
    if stage not in FAILURE_STAGES:
        raise ObservationRefused(
            f"{stage!r} is not one of the stages §2.13.5a injects a failure at: "
            f"{list(FAILURE_STAGES)}."
        )
    present = tuple(sorted(set(artifacts_present)))
    unknown = tuple(name for name in present if name not in GENERATION_ARTIFACTS)
    if unknown:
        raise ObservationRefused(
            f"{list(unknown)} are not generation artifacts; §2.13.3 names "
            f"{list(GENERATION_ARTIFACTS)}."
        )
    observed = (
        "no generation artifact and no registration row"
        if not present and not generation_row_present
        else ",".join((*present, *(("registration row",) if generation_row_present else ())))
    )
    return EvidenceRecord.for_case(
        case_id=f"JNL-47-{stage}",
        band=BAND,
        target_identity="init-generation, with a failure injected at this stage",
        operation=f"list …/journal and query for a generation row after a {stage} failure",
        preconditions=(
            "the failure is injected at exactly one stage",
            "no artifact is created before the stage that failed",
        ),
        expected=Outcome.read("no generation artifact and no registration row"),
        observed=Outcome.read(observed),
        case_role=CaseRole.STANDALONE,
        cleanup_state=CleanupState.CLEAN if not present else CleanupState.RESIDUE,
        detail={
            "stage": stage,
            "artifact_count": len(present),
            "generation_row_present": generation_row_present,
            "note": "A generation is created or it is not; a partial one is the "
                    "state §2.13.5a's creation order exists to make unreachable.",
        },
    )


def classify_cleanup_failure_state(
    *,
    variant: str,
    exit_code: int,
    state: str,
    residue_path_count: int,
    generation_present: bool,
    database_row_present: bool,
    next_run_refuses: bool,
    residue_recovery_named: bool,
    configuration_capture_retained: bool,
    configuration_recovery_named: bool,
) -> EvidenceRecord:
    """`JNL-47`: the two §2.13.2b cleanup failures, kept apart — R16.

    §2.13.2b's requirement is that *cleanup failure after a probe-stage failure*
    and *cleanup failure after a fully passing probe* are **distinguished**, and
    that each asserts its exit status, safe path reporting, generation and
    database absence, residue state, next-run behaviour and the named operator
    recovery. The two are one state on the host and two different things to say
    about the run, which is why one record covering both would answer neither.

    Every clause is compared. `S-B` is the state, `3` is its exit code, residue
    is named rather than counted away, no generation artifact and no database row
    may exist, the next invocation refuses rather than cleaning, and the recovery
    procedure is reported. A record that satisfies six of the seven is a failed
    case.

    **The recovery clause is compared per cause — runner contract r6 §8.1.** Two
    named recoveries exist and they are for different things: the five-step
    residue recovery and the four-step configuration recovery. The clause is
    satisfied when the run names *the procedure that applies to the state it
    reached*, so residue present requires the residue procedure and a retained
    configuration capture requires the configuration procedure, independently.
    One boolean over both would let a run that named the wrong procedure satisfy
    the clause, which is the shape of LAB-1 one level up.
    """
    expectation = CLEANUP_FAILURE_VARIANTS.get(variant)
    if expectation is None:
        raise ObservationRefused(
            f"{variant!r} is not one of the §2.13.2b cleanup-failure situations: "
            f"{sorted(CLEANUP_FAILURE_VARIANTS)}."
        )
    expected_code, why = expectation
    residue_present = residue_path_count > 0
    #: Each cause that is present must name its own procedure. A cause that is
    #: absent requires nothing, and never excuses one that is present.
    residue_recovery_satisfied = residue_recovery_named if residue_present else True
    configuration_recovery_satisfied = (
        configuration_recovery_named if configuration_capture_retained else True
    )
    holds = (
        exit_code == expected_code
        and state == "S-B"
        and residue_present
        and not generation_present
        and not database_row_present
        and next_run_refuses
        and residue_recovery_satisfied
        and configuration_recovery_satisfied
    )
    if residue_recovery_satisfied and configuration_recovery_satisfied:
        recovery_phrase = "recovery named"
    else:
        unnamed = []
        if not residue_recovery_satisfied:
            unnamed.append("residue")
        if not configuration_recovery_satisfied:
            unnamed.append("configuration")
        recovery_phrase = f"{' and '.join(unnamed)} recovery not named"
    return EvidenceRecord.for_case(
        case_id=f"JNL-47-{variant}",
        band=BAND,
        target_identity="the harness, after a cleanup that did not complete",
        operation="classify the §2.13.2b state the run reported and what it left",
        preconditions=(
            "cleanup did not complete",
            why,
        ),
        expected=Outcome.read(
            "S-B, exit 3, residue named by absolute path, no generation "
            "artifact, no database row, the next run refuses, and the named "
            "operator recovery is reported"
        ),
        observed=Outcome.read(
            "S-B, exit 3, residue named by absolute path, no generation "
            "artifact, no database row, the next run refuses, and the named "
            "operator recovery is reported"
            if holds
            else f"{state}, exit {exit_code}, {residue_path_count} residue "
            f"path(s), generation {'present' if generation_present else 'absent'}, "
            f"database row {'present' if database_row_present else 'absent'}, "
            f"next run {'refuses' if next_run_refuses else 'proceeds'}, "
            f"{recovery_phrase}"
        ),
        case_role=CaseRole.STANDALONE,
        cleanup_state=CleanupState.RESIDUE,
        detail={
            "variant": variant,
            "residue_path_count": residue_path_count,
            "note": "The two situations leave the host in the same place and mean "
                    "different things about what ran, so they are separate "
                    "records rather than one.",
        },
    )


def p5_0_r5_evidence_complete(records: Sequence[EvidenceRecord]) -> tuple[bool, str]:
    """Whether the journal band covers every condition P5.0-R5 needs.

    It reports coverage and nothing more. **It does not close P5.0-R5**, does not
    recommend closing it, and returning `True` means only that a record exists for
    each condition — Codex decides independently whether the evidence supports
    closure, and this harness cannot.
    """
    seen: set[str] = set()
    for record in records:
        if record.band != BAND or record.observed is None:
            continue
        value = record.observed.value or ""
        seen.add(value.split(":", 1)[0])
    required = {
        condition.value
        for condition in GenerationCondition
        if condition is not GenerationCondition.HEALTHY
    }
    missing = sorted(required - seen)
    if missing:
        return False, f"No evidence record for: {', '.join(missing)}."
    return True, (
        "A record exists for every condition. This is coverage, not a closure "
        "recommendation: P5.0-R5 remains Blocking and only Codex's independent "
        "review can dispose of it."
    )


__all__ = [
    "BAND",
    "CLEANUP_FAILURE_VARIANTS",
    "CONDITION_REFUSALS",
    "COORDINATOR_REFUSALS",
    "GenerationCondition",
    "JournalObservation",
    "RECOVERY_PROCEDURE",
    "RecoveryStep",
    "SealBody",
    "WRITER_REFUSALS",
    "FAILURE_STAGES",
    "GENERATION_ARTIFACTS",
    "classify_cleanup_failure_state",
    "classify_generation_state",
    "classify_recovery",
    "classify_stage_failure",
    "diagnose",
    "p5_0_r5_evidence_complete",
]
