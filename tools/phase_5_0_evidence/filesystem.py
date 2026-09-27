"""Check **C-3**: the four-stage append-only capability probe of §2.13.2a, and
the attribution table that says what each observation means.

The requirement the section states is the whole of this module: *"each expected
refusal must be attributable to `FS_APPEND_FL` and to nothing else, and no
destructive operation may ever touch live evidence."*

## The four stages, and why the order is load-bearing

* **Stage 1 — the control stage.** Six cases on a file with the arena's ownership
  and mode and **no** `+a`. Its only job is to prove that ordinary permissions are
  not the reason for anything Stage 2 observes. **If any control case fails, the
  probe result is `inconclusive`, never `passed`.**
* **Stage 2 — the capability stage.** Nine cases on an identical file that root
  has given `FS_APPEND_FL`. Each is interpreted only beside the Stage-1 control
  that proved the same operation permitted without the flag.
* **Stage 3 — storage attribution.** `M-1` reads the `/proc/mounts` entry
  covering the journal path; `M-2` reads `statvfs`. Together they establish that
  the filesystem is not `tmpfs`, is backed by a block device and is not read-only
  — so an `EROFS` elsewhere is not the mount.
* **Stage 4 — sandbox attribution.** `S4-0` proves the exact target writable with
  the sandbox removed; `S4-1` and `S4-2` run inside the transient unit; `S4-3`
  compares the complete normalized applied property set with the deployed
  unit's, in `unit_sandbox.py`, which is the only way S4-3 is classified. **`S4-0` precedes
  `S4-2` in every execution**, and a Stage-4 report in which `S4-2` passes while
  `S4-0` is not present-and-passing is refused.

## The attribution table, encoded

`attribute_observation()` is §2.13.2a's table as a function. It is the place the
three interesting mistakes are refused:

* `EACCES` in Stage 2 means **discretionary access control**, not append-only
  enforcement — Stage 1 exists so it cannot occur, and where it does the target is
  mis-provisioned and the result is `inconclusive`;
* `EROFS` in `S4-2` with `S4-0` failing or absent means **nothing attributable** —
  revision 7 would have recorded it as a pass, and that is the R7-B defect;
* `S4-2` **succeeding** is a **failed** stage, not a benign one: the sandbox did
  not deny.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .errors import ObservationRefused
from .records import (
    CaseRole,
    CleanupState,
    EvidenceRecord,
    Outcome,
    Status,
)

BAND = "filesystem"


@dataclass(frozen=True, slots=True)
class ProbeCase:
    """One case of §2.13.2a, with the control the section names for it.

    `role` is declared, not inferred. The Stage-1 cases are called `C-1 … C-6`
    and the `identity` band has cases called `C-1` too, so "it starts with C" is
    not a statement about what a case is — and a control that is only a control
    because of its name cannot be validated. The table below is checked against
    itself at import: a `DEPENDENT` names a control, a `CONTROL` and a
    `STANDALONE` name none, and every named control is a case this band declares
    a `CONTROL`.
    """

    case_id: str
    stage: int
    operation: str
    expected: Outcome
    #: The Stage-1 case that proved this operation permitted without the flag, or
    #: `S4-0` for `S4-2`. `None` for a case that is itself a control or a read.
    control_case_id: str | None = None
    rationale: str = ""
    #: Declared, and checked against `control_case_id` here rather than trusted.
    role: CaseRole = CaseRole.STANDALONE

    def __post_init__(self) -> None:
        names_control = self.control_case_id is not None
        if (self.role is CaseRole.DEPENDENT) != names_control:
            raise ObservationRefused(
                f"Case {self.case_id!r} declares role {self.role.value!r} and "
                f"{'names' if names_control else 'names no'} control. A dependent "
                "case names exactly one control, and a control or a read names "
                "none — the role and the reference say the same thing or the "
                "table is wrong."
            )


#: Stage 1 — every case is a control, and every case must succeed.
STAGE_1: tuple[ProbeCase, ...] = (
    ProbeCase("C-1", 1, "open(O_WRONLY) then pwrite at offset 0", Outcome.returned(),
              rationale="the byte at offset 0 changes", role=CaseRole.CONTROL),
    ProbeCase("C-2", 1, "open(O_WRONLY|O_TRUNC)", Outcome.returned(),
              rationale="the file is empty afterwards", role=CaseRole.CONTROL),
    ProbeCase("C-3", 1, "ftruncate(fd, 0)", Outcome.returned(), role=CaseRole.CONTROL),
    ProbeCase("C-4", 1, "rename within …/probe", Outcome.returned(), role=CaseRole.CONTROL),
    ProbeCase("C-5", 1, "unlink", Outcome.returned(), role=CaseRole.CONTROL),
    ProbeCase("C-6", 1, "open(O_WRONLY|O_APPEND), write, fsync", Outcome.returned(),
              role=CaseRole.CONTROL),
)

#: Stage 2 — nine cases, each against the Stage-1 control that isolates it.
STAGE_2: tuple[ProbeCase, ...] = (
    ProbeCase("P-1", 2, "open(O_WRONLY) without O_APPEND", Outcome.refused("EPERM"), "C-1",
              "may_open() refuses a writable non-append open on an append-only "
              "inode. DAC would have given EACCES, and C-1 proved DAC permits it.",
              role=CaseRole.DEPENDENT),
    ProbeCase("P-2", 2, "open(O_WRONLY|O_APPEND|O_TRUNC)", Outcome.refused("EPERM"), "C-2",
              "O_TRUNC on an append-only inode is refused even with O_APPEND.",
              role=CaseRole.DEPENDENT),
    ProbeCase("P-3", 2, "ftruncate on an O_APPEND fd", Outcome.refused("EPERM"), "C-3",
              "IS_APPEND(inode) is checked in the truncate path.",
              role=CaseRole.DEPENDENT),
    ProbeCase("P-4", 2, "rename within …/probe", Outcome.refused("EPERM"), "C-4",
              "may_delete()/may_create() refuse on an append-only victim; C-4 "
              "proved the directory permits renames.",
              role=CaseRole.DEPENDENT),
    ProbeCase("P-5", 2, "unlink", Outcome.refused("EPERM"), "C-5",
              "as P-4; C-5 proved the directory permits unlinking.",
              role=CaseRole.DEPENDENT),
    ProbeCase("P-6", 2, "open(O_WRONLY|O_APPEND), write, fsync", Outcome.returned(), "C-6",
              "the capability must permit the one operation the writer needs, and "
              "the bytes are at the old EOF.",
              role=CaseRole.DEPENDENT),
    ProbeCase("P-7", 2, "pwrite(fd, …, offset 0) on an O_APPEND fd", Outcome.returned(), "C-6",
              "Deliberately not a refusal. POSIX requires O_APPEND to ignore the "
              "offset, so a design expecting EPERM here would be wrong; what is "
              "asserted is that the bytes land at EOF, read back.",
              role=CaseRole.DEPENDENT),
    ProbeCase("P-8", 2, "FS_IOC_SETFLAGS clearing FS_APPEND_FL", Outcome.refused("EPERM"), None,
              "The arena file is owned by the writer's uid, so the owner half (A10) "
              "is satisfied and the missing prerequisite is CAP_LINUX_IMMUTABLE "
              "alone. A subsequent FS_IOC_GETFLAGS must still report FS_APPEND_FL, "
              "which is what distinguishes 'refused' from 'silently ignored'."),
    ProbeCase("P-9", 2, "FS_IOC_GETFLAGS", Outcome.read("FS_APPEND_FL"), None,
              "ENOTTY or EOPNOTSUPP here means the filesystem does not implement "
              "the flag interface at all, and is a failed probe, not a passing one."),
)

#: Stage 3 — read-only storage attribution, as root.
STAGE_3: tuple[ProbeCase, ...] = (
    ProbeCase("M-1", 3, "read the /proc/mounts entry covering the journal path",
              Outcome.read("block-backed non-tmpfs, rw"), None,
              "it names a non-tmpfs filesystem backed by a block device and does "
              "not carry `ro`."),
    ProbeCase("M-2", 3, "statvfs on the journal directory", Outcome.read("ST_RDONLY clear"), None,
              "the directory's st_dev is recorded as probe_device, and "
              "init-generation later asserts the journal file it creates has the "
              "same st_dev (step C6)."),
)

#: Stage 4 — sandbox attribution. `S4-0` is the positive DAC control for `S4-2`.
STAGE_4: tuple[ProbeCase, ...] = (
    ProbeCase("S4-0", 4,
              "append, rename and unlink on the exact …/probe-ro targets, as "
              "freedomsheet through setpriv, outside any unit",
              Outcome.returned(), None,
              "Holds everything else fixed — same uid, absolute path, inode, "
              "directory, mount, mode and ownership — with only the sandbox "
              "removed. That is the shape of Stage 1's control, applied to the one "
              "stage revision 7 left without one.",
              role=CaseRole.CONTROL),
    ProbeCase("S4-1", 4,
              "open(O_WRONLY|O_APPEND), write, fsync on an arena file inside the "
              "substituted ReadWritePaths=",
              Outcome.returned(), None),
    ProbeCase("S4-2", 4,
              "the same append to …/probe-ro/s4-2.target, outside the substituted "
              "ReadWritePaths= and inside ProtectSystem=strict's read-only tree",
              Outcome.refused("EROFS"), "S4-0",
              "EROFS and nothing else. EACCES means discretionary permissions "
              "refused it — which S4-0 has just excluded — so EACCES is "
              "inconclusive, not a pass. Success is a failed stage.",
              role=CaseRole.DEPENDENT),
    ProbeCase("S4-3", 4,
              "systemctl show on the transient unit, compared with the deployed "
              "unit file and its drop-ins under a closed directive allowlist",
              Outcome.read("the complete normalized applied property set equals the "
                           "deployed unit's, except the single ReadWritePaths= "
                           "substitution to the canonical probe path, under the "
                           "recorded systemd identity"), None,
              "A mismatch is inconclusive: the transient unit did not exercise the "
              "sandbox the writer will run under, so S4-1 and S4-2 attest nothing "
              "about it. Classified only by unit_sandbox.classify_sandbox_attestation."),
)

ALL_CASES: Mapping[str, ProbeCase] = {
    case.case_id: case for case in (*STAGE_1, *STAGE_2, *STAGE_3, *STAGE_4)
}


def _validate_case_table() -> None:
    """Every declared control reference in this band names a declared control.

    Run at import, so a table that names a read as a control fails on the day it
    is written rather than on the day a record is classified against it.
    """
    for case in ALL_CASES.values():
        if case.control_case_id is None:
            continue
        control = ALL_CASES.get(case.control_case_id)
        if control is None:
            raise ObservationRefused(
                f"Case {case.case_id!r} names control {case.control_case_id!r}, "
                "which is not a case in this band."
            )
        if control.role is not CaseRole.CONTROL:
            raise ObservationRefused(
                f"Case {case.case_id!r} names {case.control_case_id!r} as its "
                f"control, but that case is declared a {control.role.value}."
            )


_validate_case_table()


def attribute_observation(case_id: str, observed: Outcome) -> tuple[str, str]:
    """§2.13.2a's attribution table, as a function.

    Returns `(means, does_not_mean)`. It does not decide the case's status —
    `records.classify` does that, from the expected outcome and the control — but
    it is what a reviewer reads beside the status to see that the refusal was
    interpreted the way the section interprets it.
    """
    case = ALL_CASES.get(case_id)
    if case is None:
        raise ObservationRefused(f"{case_id!r} is not a §2.13.2a case.")
    errno_name = observed.errno_name
    if errno_name == "EACCES":
        return (
            "discretionary access control — the identity lacks permission on the "
            "file or its directory",
            "append-only enforcement, and not sandbox enforcement either. Stage 1 "
            "exists so this cannot occur in Stage 2 and S4-0 so it cannot occur in "
            "S4-2; where it does, the target is mis-provisioned.",
        )
    if errno_name == "EROFS":
        if case.case_id == "S4-2":
            return (
                "systemd's ProtectSystem=strict read-only bind, with the path "
                "outside ReadWritePaths= — but only beside a passing S4-0",
                "a read-only mount (M-1/M-2 establish the filesystem is writable) "
                "and not DAC (S4-0 establishes the exact target is writable by this "
                "uid on this mount with the sandbox removed).",
            )
        return (
            "a read-only mount, or the systemd bind",
            "append-only enforcement. M-1/M-2 establish the first is not the case.",
        )
    if errno_name == "EPERM":
        if case.stage == 2 and case.case_id == "P-8":
            return (
                "CAP_LINUX_IMMUTABLE is absent from the caller — the expected state "
                "for the writer",
                "that the attribute is set; P-9 establishes that separately.",
            )
        return (
            "append-only enforcement, with FS_IOC_GETFLAGS reporting FS_APPEND_FL",
            "anything about discretionary permissions, which Stage 1 excluded.",
        )
    if errno_name in ("ENOTTY", "EOPNOTSUPP", "ENOTSUP"):
        return (
            "the filesystem has no flag interface at all",
            "anything about append-only. It is a failed probe, not a passing one.",
        )
    if observed.succeeded and case.case_id == "S4-2":
        return (
            "the sandbox did not deny a write outside ReadWritePaths=",
            "nothing benign. The writer's sandbox is not doing what the design "
            "relies on.",
        )
    if observed.succeeded:
        return ("the operation was permitted", "—")
    return ("an unexpected refusal", "nothing attributable; the cause is not one "
                                     "the attribution table recognises.")


def attribution_refusal_for(case_id: str, observed: Outcome) -> str | None:
    """When an observation is not attributable to the boundary the case tests.

    Two shapes, both from §2.13.2a's attribution table, and both computed from the
    observation rather than chosen:

    * `EACCES` in Stage 2 or in `S4-2`, where Stage 1 and `S4-0` have already
      proved discretionary access permits the operation. The target is
      mis-provisioned, and the result is `inconclusive`.
    * an `S4-3` directive-set mismatch, which means the transient unit did not
      exercise the sandbox the writer will run under, so `S4-1` and `S4-2` attest
      nothing about it.
    """
    case = ALL_CASES.get(case_id)
    if case is None:
        raise ObservationRefused(f"{case_id!r} is not a §2.13.2a case.")
    if observed.errno_name == "EACCES" and (case.stage == 2 or case.case_id == "S4-2"):
        return (
            "EACCES means discretionary access control refused this operation, and "
            f"{'Stage 1' if case.stage == 2 else 'S4-0'} has already proved it "
            "permitted on this target. The target is mis-provisioned, so the "
            "observation attributes nothing to the boundary under test."
        )
    return None


def classify_probe_case(
    case_id: str,
    observed: Outcome | None,
    *,
    control: EvidenceRecord | None = None,
    target_identity: str = "freedomsheet",
    detail: Mapping[str, object] | None = None,
) -> EvidenceRecord:
    """One probe case, interpreted only beside the control §2.13.2a names.

    `control` is the control's **record**, not its status: EH-R2-1. The status is
    read off the record the control produced, so a caller cannot state a control
    result the control did not have, and the record a dependent case is
    classified beside is the record the artifact publishes.
    """
    case = ALL_CASES.get(case_id)
    if case is None:
        raise ObservationRefused(f"{case_id!r} is not a §2.13.2a case.")
    if case_id == "S4-3":
        # C-P5.0-R5-R1: S4-3's result is a comparison of typed inputs, not a
        # supplied outcome string. Accepting one here let a caller state the
        # expected text and receive a pass.
        raise ObservationRefused(
            "S4-3 is classified only by "
            "unit_sandbox.classify_sandbox_attestation(), from the deployed unit, "
            "its recorded digest, the applied property set and the systemd "
            "identity. A supplied outcome is not S4-3 evidence."
        )
    if case.control_case_id is not None and control is None:
        raise ObservationRefused(
            f"Case {case_id!r} names control {case.control_case_id!r}; that "
            "control's record must be supplied, because the negative result is "
            "not interpreted at all when the control did not pass."
        )
    extra: dict[str, str | int | bool | None] = {"stage": case.stage}
    if case.rationale:
        extra["rationale"] = case.rationale
    if observed is not None:
        means, does_not_mean = attribute_observation(case_id, observed)
        extra["attribution"] = means
        extra["does_not_mean"] = does_not_mean
    for key, value in (detail or {}).items():
        extra[key] = value  # type: ignore[assignment]
    refusal = None if observed is None else attribution_refusal_for(case_id, observed)
    return EvidenceRecord.for_case(
        case_id=case_id,
        band=BAND,
        target_identity=target_identity,
        operation=case.operation,
        preconditions=(
            "the arena is root:freedomsheet 0770 and each probe file is "
            "freedomsheet:freedomsheet 0600",
            "no live journal, seal or archive is touched by any case",
        ),
        expected=case.expected,
        observed=observed,
        case_role=case.role,
        positive_control_case_id=case.control_case_id,
        positive_control=control,
        attribution_refusal=refusal,
        cleanup_state=CleanupState.NOT_APPLICABLE,
        detail=extra,
    )


def stage_status(records: Sequence[EvidenceRecord], stage: int) -> Status:
    """A stage's status, on §2.13.2a's rule that one failing control sinks it.

    A stage with no record is `NOT_RUN`. A stage with any `FAILED` is `FAILED`.
    A stage with any `INCONCLUSIVE` — which is what a failing Stage-1 control
    produces for everything downstream — is `INCONCLUSIVE`. Only an all-passing
    stage passes.
    """
    in_stage = [
        record
        for record in records
        if record.case_id in ALL_CASES and ALL_CASES[record.case_id].stage == stage
    ]
    if not in_stage:
        return Status.NOT_RUN
    statuses = {record.status for record in in_stage}
    if Status.FAILED in statuses:
        return Status.FAILED
    if Status.INCONCLUSIVE in statuses or Status.NOT_RUN in statuses:
        return Status.INCONCLUSIVE
    return Status.PASSED


def stage_four_ordering_holds(records: Sequence[EvidenceRecord]) -> bool:
    """`S4-0` present and passing whenever `S4-2` passed.

    *"A Stage-4 report in which S4-2 is a pass while S4-0 is not present-and-passing
    is refused at Algorithm C step C2 and again by the writer at W4."*
    """
    by_id = {record.case_id: record for record in records}
    s4_2 = by_id.get("S4-2")
    if s4_2 is None or s4_2.status is not Status.PASSED:
        return True
    s4_0 = by_id.get("S4-0")
    return s4_0 is not None and s4_0.status is Status.PASSED


def probe_report_admissible(records: Sequence[EvidenceRecord]) -> tuple[bool, str]:
    """Whether Algorithm C step **C2** would admit this report.

    All four stages present, every case passed, and the Stage-4 ordering rule
    satisfied. This is the single gate before any persistent artifact exists, and
    it returns the reason rather than a bare boolean so a refusal names its cause.
    """
    for stage in (1, 2, 3, 4):
        status = stage_status(records, stage)
        if status is not Status.PASSED:
            return False, f"Stage {stage} is {status.value}; C2 admits only a report whose four stages all passed."
    if not stage_four_ordering_holds(records):
        return False, "S4-2 passed without a present-and-passing S4-0, so its EROFS is not attributable."
    return True, "All four stages passed and S4-0 precedes and supports S4-2."


__all__ = [
    "ALL_CASES",
    "BAND",
    "ProbeCase",
    "STAGE_1",
    "STAGE_2",
    "STAGE_3",
    "STAGE_4",
    "attribute_observation",
    "attribution_refusal_for",
    "classify_probe_case",
    "probe_report_admissible",
    "stage_four_ordering_holds",
    "stage_status",
]
