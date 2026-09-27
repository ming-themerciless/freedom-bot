"""The journal generation lifecycle: the writer's disk-only validation, the
refusal each §2.13.6 condition produces on both sides, creation-failure and
cleanup-failure classification, and the recovery path.

Two actors, two refusals, and they are different refusals (§2.13.6). **W** is the
writer, at start and before each dispatch; its refusal is *refuse new Sheet
mutations*. **C** is the coordinator, at `observe`; its refusal is *record no
`dispatch_journal_clear` row*, which makes the activation trigger refuse.

## What this classifier models, and what it does not

`validate_generation()` is Algorithm **V-W** of §2.13.5b, steps **W1 … W16**
including **W11a**, evaluated over typed facts a verifier read from disk. Each
step names its own refusal code, and the first step that refuses is the result —
so a combined fault is classified exactly as the writer would refuse it, in the
writer's order, and not in an order this module found convenient.

The coordinator's **C-a** is W1 … W16 read-only, and it refuses with *"the
matching `J-xx` row"* and records no evidence. That is the coordinator verdict
this module returns. It does **not** model:

* **W17/W18** — the writer's one append and its re-read. They are runtime
  behaviour (`J-14`, `J-15`), not a reading of disk;
* **C-b … C-f** — the seal-bytes digest, the registered head and its sixteen
  compared values, and the unresolved set. They need PostgreSQL (`J-16`, `J-20`,
  `J-28`), so a verdict with no disk refusal is **not** clear evidence: it is
  *"C-a would not refuse"* and nothing more;
* `J-01`, which is a reboot rather than a refusal.

So this is **not** "the refusals P5.0-R5 needs evidence for". §2.13.6 has
twenty-eight rows; this module classifies the ones **V-W** can observe from disk,
and says so in every verdict.

## Why a reset can never look like an empty history

§2.13.5: a fresh journal file with no records is indistinguishable from a
deliberately emptied one **unless the generation is anchored outside the file**.
It is: the seal is `chattr +i`, record 0's `prev_hash` **is** `seal_body_digest`,
and the registered row in PostgreSQL carries the same values. So an emptied
journal fails **W13** (`SW-J04`) against a genesis the writer derives, and a
replaced journal fails **W7** (`SW-J11`) against `fstat` — two different codes,
because §2.13.6 J-04 and J-11 are two different conditions and stop condition
**10h** forbids a detector that fires only when some other, differently named
field happens to differ.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from .errors import ObservationRefused
from .records import CaseRole, CleanupState, EvidenceRecord, Outcome, Status

BAND = "journal"

#: **N5.0-21**, accepted under OD-63: the free-space floor **W12** refuses below.
N5_0_21_FREE_BYTES = 1 << 30

#: **W1**: the `current` symbolic link is a relative name of this shape, in the
#: same directory, or the writer refuses.
_CURRENT_NAME = re.compile(r"[0-9]{6}\.journal")


class VWStep(str, Enum):
    """Algorithm V-W's steps, **in the order the writer performs them**.

    Declaration order is the precedence order: `validate_generation()` evaluates
    them in exactly this sequence and stops at the first refusal. `W11A` sits
    between `W11` and `W12` because revision 12 inserted it there.
    """

    W1 = "W1"
    W2 = "W2"
    W3 = "W3"
    W4 = "W4"
    W5 = "W5"
    W6 = "W6"
    W7 = "W7"
    W8 = "W8"
    W9 = "W9"
    W10 = "W10"
    W11 = "W11"
    W11A = "W11a"
    W12 = "W12"
    W13 = "W13"
    W14 = "W14"
    W15 = "W15"
    W16 = "W16"


class JournalFault(str, Enum):
    """Every disk-observable fault **V-W** distinguishes, one member per cause.

    Two members may share a §2.13.6 row where the design gives one row two causes
    — `J-04` is an empty file *or* a record 0 that is not the derived genesis —
    and they remain two members because a case must say which one it produced.
    """

    CURRENT_UNRESOLVED = "current_unresolved"
    SEAL_MISSING = "seal_missing"
    SEAL_UNREADABLE = "seal_unreadable"
    SEAL_STRUCTURE = "seal_structure"
    PROBE_REPORT = "probe_report"
    GENESIS_DERIVATION = "genesis_derivation"
    SEAL_MUTABLE = "seal_mutable"
    JOURNAL_MISSING = "journal_missing"
    JOURNAL_UNREADABLE = "journal_unreadable"
    INODE_REPLACED = "inode_replaced"
    OWNER_OR_MODE = "owner_or_mode"
    APPEND_FLAG_ABSENT = "append_flag_absent"
    HOST_MISMATCH = "host_mismatch"
    DEPLOYMENT_STALE = "deployment_stale"
    SOURCE_MANIFEST_MISMATCH = "source_manifest_mismatch"
    PROVENANCE_INVALID = "provenance_invalid"
    FILESYSTEM_FULL_OR_READ_ONLY = "filesystem_full_or_read_only"
    EMPTY_JOURNAL = "empty_journal"
    GENESIS_RECORD_MISMATCH = "genesis_record_mismatch"
    MALFORMED_RECORD = "malformed_record"
    CROSS_GENERATION = "cross_generation"
    DUPLICATE_SEQUENCE = "duplicate_sequence"
    SEQUENCE_GAP = "sequence_gap"
    CHAIN_BROKEN = "chain_broken"
    NON_MONOTONIC_TIME = "non_monotonic_time"
    TORN_TAIL = "torn_tail"
    GENERATION_SEALED = "generation_sealed"


@dataclass(frozen=True, slots=True)
class FaultRefusal:
    """What one fault produces: the V-W step, and each actor's refusal."""

    step: VWStep
    #: The §2.13.6 row the condition is.
    row: str
    #: The writer's `SW-Jnn` code, from §2.13.5b's step table.
    writer_refusal: str
    #: The coordinator's refusal: **C-a**'s *"matching `J-xx` row"*, except for a
    #: torn tail, which §2.13.6 J-02 and **C-e** count as one unresolved entry.
    coordinator_refusal: str
    what: str


#: Each fault's refusals, transcribed from §2.13.5b's V-W table and §2.13.6.
#:
#: Two readings are recorded rather than hidden. **An unreadable seal** is named
#: by both J-12 (*"unreadable file or seal"*) and J-17 (*"seal … unreadable"*);
#: V-W assigns `SW-J17` to W2, which is where the read fails, so this table
#: follows the step. **A torn tail** refuses at the writer as `SW-J02`, and the
#: coordinator counts it into the unresolved set (J-02's C column, C-e), which is
#: `J-20`. Both are named in the C-P5.0-R5-R1 handback for review.
FAULT_REFUSALS: Mapping[JournalFault, FaultRefusal] = {
    JournalFault.CURRENT_UNRESOLVED: FaultRefusal(
        VWStep.W1, "J-03", "SW-J03", "J-03",
        "`current` is absent or does not name ^[0-9]{6}\\.journal$ in the same directory"),
    JournalFault.SEAL_MISSING: FaultRefusal(
        VWStep.W2, "J-17", "SW-J17", "J-17", "the seal is absent"),
    JournalFault.SEAL_UNREADABLE: FaultRefusal(
        VWStep.W2, "J-17", "SW-J17", "J-17",
        "the seal cannot be opened or read (EACCES, EIO)"),
    JournalFault.SEAL_STRUCTURE: FaultRefusal(
        VWStep.W3, "J-24", "SW-J24", "J-24",
        "unknown body format_version, unsupported or short binding, or a byte "
        "after the binding"),
    JournalFault.PROBE_REPORT: FaultRefusal(
        VWStep.W4, "J-25", "SW-J25", "J-25",
        "the embedded probe report does not hash to SB.probe_report_digest, or is "
        "not an admissible four-stage pass"),
    JournalFault.GENESIS_DERIVATION: FaultRefusal(
        VWStep.W5, "J-24", "SW-J24", "J-24",
        "the genesis derived from SB does not equal BND.genesis_record_digest"),
    JournalFault.SEAL_MUTABLE: FaultRefusal(
        VWStep.W6, "J-17", "SW-J17", "J-17", "the seal lacks FS_IMMUTABLE_FL"),
    JournalFault.JOURNAL_MISSING: FaultRefusal(
        VWStep.W7, "J-03", "SW-J03", "J-03", "the journal file is absent (ENOENT)"),
    JournalFault.JOURNAL_UNREADABLE: FaultRefusal(
        VWStep.W7, "J-12", "SW-J12", "J-12",
        "the journal file cannot be opened or read (EACCES, EIO)"),
    JournalFault.INODE_REPLACED: FaultRefusal(
        VWStep.W7, "J-11", "SW-J11", "J-11",
        "fstat's (st_dev, st_ino) differs from BND — the journal was replaced"),
    JournalFault.OWNER_OR_MODE: FaultRefusal(
        VWStep.W8, "J-05", "SW-J05", "J-05",
        "st_uid, st_gid or the permission bits differ from SB"),
    JournalFault.APPEND_FLAG_ABSENT: FaultRefusal(
        VWStep.W9, "J-06", "SW-J06", "J-06",
        "FS_APPEND_FL is absent, or FS_IOC_GETFLAGS is unsupported"),
    JournalFault.HOST_MISMATCH: FaultRefusal(
        VWStep.W10, "J-23", "SW-J23", "J-23",
        "/etc/machine-id differs from SB.host_machine_id (the unforged case only)"),
    JournalFault.DEPLOYMENT_STALE: FaultRefusal(
        VWStep.W11, "J-22", "SW-J22", "J-22",
        "the deployment manifest digest differs from SB.writer_deployment_digest"),
    JournalFault.SOURCE_MANIFEST_MISMATCH: FaultRefusal(
        VWStep.W11A, "J-27", "SW-J27", "J-27",
        "the deployed region-S manifest digest differs from SB.source_manifest_digest"),
    JournalFault.PROVENANCE_INVALID: FaultRefusal(
        VWStep.W11A, "J-26", "SW-J26", "J-26",
        "the provenance record is absent, not root:root 0444, malformed, or "
        "disagrees with SB"),
    JournalFault.FILESYSTEM_FULL_OR_READ_ONLY: FaultRefusal(
        VWStep.W12, "J-13", "SW-J13", "J-13",
        "ST_RDONLY is set or free bytes are below N5.0-21"),
    JournalFault.EMPTY_JOURNAL: FaultRefusal(
        VWStep.W13, "J-04", "SW-J04", "J-04", "the journal holds no record 0"),
    JournalFault.GENESIS_RECORD_MISMATCH: FaultRefusal(
        VWStep.W13, "J-04", "SW-J04", "J-04",
        "record 0 is not byte-identical to the genesis record derived from SB"),
    JournalFault.MALFORMED_RECORD: FaultRefusal(
        VWStep.W14, "J-07", "SW-J07", "J-07",
        "a record's format_version is unknown or it does not parse"),
    JournalFault.CROSS_GENERATION: FaultRefusal(
        VWStep.W14, "J-18", "SW-J18", "J-18",
        "a record's generation_id is not SB's"),
    JournalFault.DUPLICATE_SEQUENCE: FaultRefusal(
        VWStep.W14, "J-10", "SW-J10", "J-10", "two records share a seq"),
    JournalFault.SEQUENCE_GAP: FaultRefusal(
        VWStep.W14, "J-08", "SW-J08", "J-08", "seq is not exactly +1"),
    JournalFault.CHAIN_BROKEN: FaultRefusal(
        VWStep.W14, "J-09", "SW-J09", "J-09",
        "prev_hash is not the predecessor's record_hash, or record_hash does not "
        "verify"),
    JournalFault.NON_MONOTONIC_TIME: FaultRefusal(
        VWStep.W14, "J-21", "SW-J21", "J-21", "a record's at precedes its predecessor's"),
    JournalFault.TORN_TAIL: FaultRefusal(
        VWStep.W15, "J-02", "SW-J02", "J-20",
        "a short or unverifiable tail record; the generation is suspect"),
    JournalFault.GENERATION_SEALED: FaultRefusal(
        VWStep.W16, "J-19", "SW-J19", "J-19", "the last record's kind is seal"),
}


class ArtifactRead(str, Enum):
    """The result of opening and reading one artifact — W2 and W7."""

    OK = "ok"
    ENOENT = "ENOENT"
    EACCES = "EACCES"
    EIO = "EIO"


class FlagRead(str, Enum):
    """`FS_IOC_GETFLAGS` for one flag. **Unsupported is a refusal**, not an
    absence of information (W9)."""

    PRESENT = "present"
    ABSENT = "absent"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True, slots=True)
class SealBody:
    """`SB` and `BND`, the anchor. Every field is one V-W compares from disk with
    no database reachable."""

    generation_id: str
    binding_format_version: int
    seal_body_digest: str
    #: `BND.genesis_record_digest`.
    genesis_record_digest: str
    #: `BND.journal_device` and `BND.journal_inode`.
    journal_device: int
    journal_inode: int
    journal_uid: int
    journal_gid: int
    journal_mode: int
    host_machine_id: str
    writer_deployment_digest: str
    probe_report_digest: str
    source_manifest_digest: str
    predecessor_close_digest: str | None


@dataclass(frozen=True, slots=True)
class ChainRecord:
    """One journal record as **W13/W14** read it."""

    format_known: bool
    generation_id: str
    seq: int
    prev_hash: str
    record_hash: str
    #: Whether `record_hash` verifies over the record's canonical bytes.
    hash_verifies: bool
    #: `at`, as a comparable UTC instant (nanoseconds since the epoch).
    at: int
    kind: str


@dataclass(frozen=True, slots=True)
class JournalObservation:
    """What a V-W reader found on disk — facts, never verdicts about them.

    One field group per step, so a fault is always the comparison of a reading
    with the seal and never a flag somebody set. A step whose inputs could not be
    read because an earlier step refused is still typed; its value is simply
    never consulted.
    """

    #: W1 — `readlink("…/journal/current")`, or `None` when it does not resolve.
    current_target: str | None
    #: W2 — opening and reading the seal.
    seal_read: ArtifactRead
    #: W3 — the body `format_version` is one this build knows, and the binding
    #: parses at `SB.binding_format_version` with no byte after it.
    seal_format_supported: bool
    binding_length_exact: bool
    #: W4 — the recomputed probe-report digest, and whether the report is a
    #: supported, complete, all-passing four-stage report whose S4-3 attestation
    #: still holds under this host's systemd identity
    #: (`unit_sandbox.revalidate_sandbox_attestation`; §2.13.2a S4-3 condition 4).
    probe_report_digest: str
    probe_report_admissible: bool
    #: W5 — the genesis record digest this reader derived from `SB` alone.
    derived_genesis_digest: str
    #: W6 — `FS_IMMUTABLE_FL` on the seal.
    seal_immutable: FlagRead
    #: W7 — opening the journal, and `fstat` on it.
    journal_read: ArtifactRead
    journal_device: int | None
    journal_inode: int | None
    #: W8.
    journal_uid: int | None
    journal_gid: int | None
    journal_mode: int | None
    #: W9 — `FS_APPEND_FL` on the journal.
    append_flag: FlagRead
    #: W10.
    machine_id: str
    #: W11 — `deployment_manifest_digest()` over this process's deployed manifest.
    deployment_digest: str
    #: W11a — `deployed_source_manifest_digest()`, then the provenance record.
    deployed_source_manifest_digest: str
    provenance_valid: bool
    #: W12.
    filesystem_read_only: bool
    free_bytes: int
    #: W13 — digest of record 0's bytes, or `None` for an empty file.
    record_zero_digest: str | None
    #: W13/W14 — every complete record, in file order, record 0 first.
    records: tuple[ChainRecord, ...]
    #: W15 — a short or unverifiable tail after the last complete record.
    torn_tail: bool

    def __post_init__(self) -> None:
        if not isinstance(self.records, tuple):
            raise ObservationRefused(
                "A journal observation carries its records as a tuple, so the "
                "verdict is over the records that were read and nothing appended "
                "after."
            )
        if self.journal_read is ArtifactRead.OK and (
            self.journal_device is None or self.journal_inode is None
        ):
            raise ObservationRefused(
                "A journal that was opened has an st_dev and an st_ino; W7 "
                "compares both, so an observation missing either is incomplete."
            )
        if (self.record_zero_digest is None) != (not self.records):
            raise ObservationRefused(
                "record_zero_digest is present exactly when a record 0 was read."
            )


@dataclass(frozen=True, slots=True)
class GenerationVerdict:
    """V-W's result and C-a's, for one observation."""

    #: `None` when no modelled step refused.
    fault: JournalFault | None
    step: VWStep | None
    writer_refusal: str | None
    coordinator_refusal: str | None

    @property
    def coordinator_records_clear_evidence(self) -> bool:
        """Always `False` from this module.

        A refusal records no evidence by definition; and **no refusal at C-a is
        not clear evidence** either, because C-b … C-f need the seal bytes and
        PostgreSQL, which this module does not model.
        """
        return False


def _diagnose(seal: SealBody, obs: JournalObservation) -> JournalFault | None:
    """V-W in the writer's order. The first refusing step is the answer."""
    # W1
    if obs.current_target is None or not _CURRENT_NAME.fullmatch(obs.current_target):
        return JournalFault.CURRENT_UNRESOLVED
    # W2
    if obs.seal_read is ArtifactRead.ENOENT:
        return JournalFault.SEAL_MISSING
    if obs.seal_read is not ArtifactRead.OK:
        return JournalFault.SEAL_UNREADABLE
    # W3
    if not (obs.seal_format_supported and obs.binding_length_exact):
        return JournalFault.SEAL_STRUCTURE
    # W4
    if obs.probe_report_digest != seal.probe_report_digest or not obs.probe_report_admissible:
        return JournalFault.PROBE_REPORT
    # W5
    if obs.derived_genesis_digest != seal.genesis_record_digest:
        return JournalFault.GENESIS_DERIVATION
    # W6
    if obs.seal_immutable is not FlagRead.PRESENT:
        return JournalFault.SEAL_MUTABLE
    # W7
    if obs.journal_read is ArtifactRead.ENOENT:
        return JournalFault.JOURNAL_MISSING
    if obs.journal_read is not ArtifactRead.OK:
        return JournalFault.JOURNAL_UNREADABLE
    if (obs.journal_device, obs.journal_inode) != (seal.journal_device, seal.journal_inode):
        return JournalFault.INODE_REPLACED
    # W8
    if (obs.journal_uid, obs.journal_gid, obs.journal_mode) != (
        seal.journal_uid,
        seal.journal_gid,
        seal.journal_mode,
    ):
        return JournalFault.OWNER_OR_MODE
    # W9
    if obs.append_flag is not FlagRead.PRESENT:
        return JournalFault.APPEND_FLAG_ABSENT
    # W10
    if obs.machine_id != seal.host_machine_id:
        return JournalFault.HOST_MISMATCH
    # W11
    if obs.deployment_digest != seal.writer_deployment_digest:
        return JournalFault.DEPLOYMENT_STALE
    # W11a — the manifest comparison first, then the provenance record.
    if obs.deployed_source_manifest_digest != seal.source_manifest_digest:
        return JournalFault.SOURCE_MANIFEST_MISMATCH
    if not obs.provenance_valid:
        return JournalFault.PROVENANCE_INVALID
    # W12
    if obs.filesystem_read_only or obs.free_bytes < N5_0_21_FREE_BYTES:
        return JournalFault.FILESYSTEM_FULL_OR_READ_ONLY
    # W13
    if not obs.records:
        return JournalFault.EMPTY_JOURNAL
    if obs.record_zero_digest != obs.derived_genesis_digest:
        return JournalFault.GENESIS_RECORD_MISMATCH
    # W14 — each record against SB and its predecessor, in the order the step
    # lists its checks.
    seen: set[int] = {obs.records[0].seq}
    for previous, record in zip(obs.records, obs.records[1:]):
        if not record.format_known:
            return JournalFault.MALFORMED_RECORD
        if record.generation_id != seal.generation_id:
            return JournalFault.CROSS_GENERATION
        if record.seq in seen:
            return JournalFault.DUPLICATE_SEQUENCE
        if record.seq != previous.seq + 1:
            return JournalFault.SEQUENCE_GAP
        if record.prev_hash != previous.record_hash or not record.hash_verifies:
            return JournalFault.CHAIN_BROKEN
        if record.at < previous.at:
            return JournalFault.NON_MONOTONIC_TIME
        seen.add(record.seq)
    # W15
    if obs.torn_tail:
        return JournalFault.TORN_TAIL
    # W16
    if obs.records[-1].kind == "seal":
        return JournalFault.GENERATION_SEALED
    return None


def validate_generation(seal: SealBody, observation: JournalObservation) -> GenerationVerdict:
    """Algorithm V-W over one observation, and C-a's matching refusal."""
    fault = _diagnose(seal, observation)
    if fault is None:
        return GenerationVerdict(None, None, None, None)
    refusal = FAULT_REFUSALS[fault]
    return GenerationVerdict(
        fault, refusal.step, refusal.writer_refusal, refusal.coordinator_refusal
    )


def _render(fault: JournalFault | None) -> str:
    if fault is None:
        return "no refusal at W1-W16"
    refusal = FAULT_REFUSALS[fault]
    return (
        f"{fault.value}:{refusal.step.value}:{refusal.writer_refusal}/"
        f"{refusal.coordinator_refusal}"
    )


def classify_generation_state(
    *,
    case_id: str,
    seal: SealBody,
    observation: JournalObservation,
    expected_fault: JournalFault | None,
) -> EvidenceRecord:
    """One lifecycle case: which V-W step refused, and with which codes.

    The expected outcome is the **fault, its step and both named refusal
    codes**, so a case that refuses for the wrong reason — or at the right
    code for the wrong cause — fails rather than passing. `expected_fault=None`
    expects no refusal at W1 … W16, which is not a claim that the generation is
    clear: that needs C-b … C-f against PostgreSQL.
    """
    verdict = validate_generation(seal, observation)
    return EvidenceRecord.for_case(
        case_id=case_id,
        band=BAND,
        target_identity="the writer at V-W, and the coordinator at C-a, from disk "
                        "with no database reachable",
        operation="validate the generation against the sealed binding (W1-W16)",
        preconditions=(
            "the seal is chattr +i and the journal chattr +a",
            "no startup check performs a destructive operation against live evidence",
        ),
        expected=Outcome.read(_render(expected_fault)),
        observed=Outcome.read(_render(verdict.fault)),
        case_role=CaseRole.STANDALONE,
        cleanup_state=CleanupState.NOT_APPLICABLE,
        detail={
            "step": None if verdict.step is None else verdict.step.value,
            "writer_refusal": verdict.writer_refusal,
            "coordinator_refusal": verdict.coordinator_refusal,
            "coordinator_records_clear_evidence": verdict.coordinator_records_clear_evidence,
            "record_count": len(observation.records),
            "not_modelled": "W17/W18 and C-b...C-f (PostgreSQL); J-01, J-14, J-15, "
                            "J-16, J-20 except a torn tail, J-28",
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


def modelled_fault_coverage(records: Sequence[EvidenceRecord]) -> tuple[bool, str]:
    """Whether a journal-band record **observed** each fault this module models.

    Deliberately narrow, and named for it. It answers *"has every
    `JournalFault` been observed at least once?"* — the V-W disk-observable
    subset of §2.13.6 — and **nothing about the band, about P5.0-R5 or about
    closure**. §2.13.6 has twenty-eight rows; `J-01`, `J-14`, `J-15`, `J-16`,
    `J-20` (apart from a torn tail) and `J-28` are outside this module, and the
    `JNL-*` band has cases this function never sees. It counts only records whose
    status is `PASSED`, because a fault observed in a failed case is evidence of
    the wrong refusal, not of this one.

    It replaces `p5_0_r5_evidence_complete()`, whose name claimed completeness
    for the band over five conditions. No caller outside the tests used it, so no
    compatibility wrapper is kept.
    """
    seen: set[str] = set()
    for record in records:
        if record.band != BAND or record.observed is None:
            continue
        if record.status is not Status.PASSED:
            continue
        seen.add((record.observed.value or "").split(":", 1)[0])
    missing = sorted(fault.value for fault in JournalFault if fault.value not in seen)
    if missing:
        return False, f"No passing record observed: {', '.join(missing)}."
    return True, (
        "Every modelled V-W fault was observed. This is coverage of this "
        "classifier's subset of §2.13.6, not of the journal band and not a "
        "closure recommendation: P5.0-R5 remains Blocking and only Codex's "
        "independent review can dispose of it."
    )


__all__ = [
    "ArtifactRead",
    "BAND",
    "CLEANUP_FAILURE_VARIANTS",
    "ChainRecord",
    "FAILURE_STAGES",
    "FAULT_REFUSALS",
    "FaultRefusal",
    "FlagRead",
    "GENERATION_ARTIFACTS",
    "GenerationVerdict",
    "JournalFault",
    "JournalObservation",
    "N5_0_21_FREE_BYTES",
    "RECOVERY_PROCEDURE",
    "RecoveryStep",
    "SealBody",
    "VWStep",
    "classify_cleanup_failure_state",
    "classify_generation_state",
    "classify_recovery",
    "classify_stage_failure",
    "modelled_fault_coverage",
    "validate_generation",
]
