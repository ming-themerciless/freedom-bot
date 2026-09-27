"""The I3 controlled-write verifier — C-P5.0-LAB-I3-R2, under C-P5.0-LAB-I3-D1.

## What this module is, and the sentence that bounds it

Runner contract r6 §9.3's **I3** is *"that exclusive publication's `linkat`
succeeds on the target's filesystems under their hard-link policy"*. V6 observed
the prerequisites and does not close it; only a controlled write in the exact
target filesystem can. This module is the mechanism for that write and for
nothing else: one fixed harmless payload, published exclusively under a unique
name in each of the four reviewed publication contexts, observed with both names
present, and removed through identity comparisons before success is reported.

| Context | Directory | Identity | Temporary created | File, immediately before `linkat` |
|---|---|---|---|---|
| **T1** — the first-use record, r6 §5.10 | V4, the laboratory directory | root | `EXCLUSIVE_CREATION_MODE` | creator-owned, mode `EXCLUSIVE_CREATION_MODE` |
| **§2.3.3** — the capture publication | V5, the recovery parent | root | `EXCLUSIVE_CREATION_MODE` | creator-owned, mode `recovery_store.STORED_OBJECT_MODE` |
| **T6** — `participant_started`, r6 §5.11 | V9, the run ledger | `ubuntu` | `EXCLUSIVE_CREATION_MODE` | creator-owned, group inherited from V9's setgid bit, mode `EXCLUSIVE_CREATION_MODE` |
| **P2** — the case program, r6 §1.4.2 | canonical `R/bin` | root | `CASE_PROGRAM_TEMPORARY_MODE`, `0500` | `root:root 0555` — `case_runtime`'s P2 constants |

The **creation** column and the **final** column are separate values, and only
P2 distinguishes them — C-P5.0-LAB-I3-R3, 2026-09-20. The mode the temporary
pathname is created with constrains nothing that follows: the writable
descriptor `openat` returned is what the payload is written to, synchronized
on, and `fchown`ed and `fchmod`ed, so P2 reaches `root:root 0555` and is read
back at `0555` before `linkat` regardless of its `0500` creation mode.

Every publication relies on `proc_sys_fs(5)`'s **filesystem-UID owner
condition**: the process whose filesystem UID links the file is the file's
owner. For P2 that is Peter's C-P5.0-LAB-I3-D1 ruling. The verifier observes
the condition — the file's `st_uid` read back from the descriptor that created
it, compared with the filesystem UID `/proc/self/status` reports — and **it
attributes the link to nothing else**.

## Capability state is evidence, never attribution

The same ruling keeps P2's actual operation-time capability state as evidence.
`/proc/self/status` is read at admission and again **immediately before each
`linkat`**, and the five masks — `CapInh`, `CapPrm`, `CapEff`, `CapBnd`,
`CapAmb` — and `NoNewPrivs` are recorded exactly. `classify_capabilities` reads
each mask from its own field and from no other, so **`CapBnd` is never read as
`CapEff`**: a bounding-set membership says a capability remains obtainable, not
that it is in force. The classification names `CAP_DAC_OVERRIDE`,
`CAP_DAC_READ_SEARCH` and `CAP_FOWNER` in each mask separately.

**This verifier does not isolate, require or prove `CAP_FOWNER`.** A root process
holding effective `CAP_DAC_OVERRIDE` also satisfies the read-and-write branch of
the protected-hardlink rule, and `CAP_FOWNER` satisfies a third, so a link that
succeeds under root cannot say which branch the kernel took. What it can say is
that the owner condition was observed to hold. `NOT_ATTRIBUTION` is that
sentence, and every rendering carries it.

`securebits` is part of the reviewed identity contract and is **not** observed
here: the kernel exposes it only through `prctl(2)`, and the one `ctypes`
exception in this package belongs to `case_program._prctl_get_securebits`.
Widening it is a separate approval; `SECUREBITS_NOT_OBSERVED` says so.

## Two gates, independently

Nothing is armed by default. `armed` is `False`, `run()` refuses before its
first read when it is not `True`, and every creating effect re-checks it. The
operator entry point, `i3_verifier_cli`, arms this object from its I3-specific
command-line flag and from nothing else, and returns before constructing it
when the flag is absent. Deleting either gate leaves the other.

## Admission: everything is observed before the first write

The host is the approved target's kernel nodename, kernel release and
architecture — the nodename, because that is what `uname(2)` reports, and never
the operational SSH alias `host`, which no local observation can see; the
account lookup resolves every reviewed name; `/proc/self/status` proves the
invocation's identity — real, effective, saved **and filesystem** uid and gid —
and agrees with `getresuid`/`getresgid`; the masks are observed, well-formed and
internally consistent; `fs.protected_hardlinks` is exactly `1`; every directory
on the path is held by descriptor, one no-follow component at a time below the
one provisioned root (`/var/lib`), and is exactly the reviewed type, owner,
group and mode; each one's mount is the approved target's filesystem type and
device, mounted read-write; canonical `R` is absent; no earlier verifier's name
is present; and each unique name is outside every lifecycle, ledger, recovery
and case-program grammar and unoccupied. **Any mismatch refuses before the
first write**, and the refusal is one member of `ADMISSION_REFUSALS`.

## Decision B's narrow exception, and nothing wider

C-P5.0-LAB-I3-D1 lets this verifier — and nothing else outside the reviewed
concrete plan — temporarily create canonical `R` (`root:root 0700`) and
`R/bin` (`root:root 0755`) solely for I3. Both are created by exclusive
`mkdirat`, owned and moded on a descriptor, read back, barriered and recorded by
`(st_dev, st_ino)`; both are removed only by name after an immediately
preceding identity comparison and an emptiness check. A foreign, replaced or
non-empty directory is never removed. The verifier holds `R`'s parent under its
own role name; it never registers `plan.EVIDENCE_ROLE`, whose production
registration stays deferred (decision D).

## Partial states, closed

Every object this invocation creates is a `TrackedObject` from the moment it
exists: its identity when one was established, and the fate cleanup gave it. A
failure at any stage records `(stage, classification)` once — the first causal
one — and guarded cleanup removes exactly the tracked objects whose identity
still matches, in reverse order, each followed by its containing-entry barrier.
An object whose identity was never established, a name that now resolves to
another object, a directory that is not empty, a removal or barrier that fails
and a descriptor that is not released are each reported and are each
non-success. A bounded final survey lists every directory the invocation held
and fails the run on any verifier name or on `R`.

## What it does not do

It starts no process, changes no identity or capability, reads no environment
value, writes no byte outside the four reviewed directories and the transient
`R`/`R/bin`, initializes no V7 record, invokes no participant or harness, runs
no generated vector and uses no `--execute`. A verified invocation confirms the
publication behaviour of this kernel and filesystem for the contexts it ran;
**closing I3 is a maintainer decision on reviewed evidence, not a return value.**
"""
from __future__ import annotations

import hashlib
import os
import re
import stat
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Protocol

from ..approved_target import APPROVED_TARGET_FACTS
from ..capability import (
    CAP_DAC_OVERRIDE,
    CAP_DAC_READ_SEARCH,
    CAP_FOWNER,
    CAPABILITY_NAMES,
)
from ..case_runtime import (
    CASE_PROGRAM_GROUP,
    CASE_PROGRAM_MODE,
    CASE_PROGRAM_OWNER,
    CASE_PROGRAM_RELATIVE_PATH,
    CASE_PROGRAM_TEMPORARY_MODE,
)
from ..durability_model import DescriptorMode
from ..provisioning import (
    EVIDENCE_ROOT,
    LABORATORY_GROUP,
    LABORATORY_LAYOUT,
    PARTICIPANT_IDENTITY,
    LaboratoryLayout,
    items_by_id,
)
from .descriptors import (
    DESCRIPTOR_OBJECT_ABSENT,
    DESCRIPTOR_OBJECT_EXISTS,
    EXCLUSIVE_CREATION_MODE,
    DescriptorInventory,
    DescriptorRefused,
    PosixFilesystem,
)
from .provisioner import OwnershipLookup
from .recovery_store import RECORD_SUFFIX, STORED_OBJECT_MODE, TEMPORARY_SUFFIX

# ---------------------------------------------------------------------------
# The fixed payload and the names
# ---------------------------------------------------------------------------

#: The only bytes this verifier writes. Fixed, ASCII, harmless, and removed
#: before success is reported.
PAYLOAD = (
    b"Freedom Blades Package 5.0 I3 controlled-write verification payload, "
    b"version 1. Harmless, fixed, and removed before success.\n"
)

#: Its SHA-256, pinned. `run()` refuses before the first write if `PAYLOAD` no
#: longer hashes to it, and the suite asserts the pair.
PAYLOAD_SHA256 = "d3daa410d7889c5a04baff5159d8ce0ae621309b3ef5ebb85000042ddac1617a"

#: Every verifier name begins with this. A leading dot places it outside the run
#: identifier grammar, which begins with a letter or digit.
NAME_PREFIX = ".fb-i3-verify-"
TEMPORARY_NAME_SUFFIX = "-staged"
PUBLISHED_NAME_SUFFIX = "-linked"

#: The nonce is 16 bytes from the injected source, rendered as 32 lower-case
#: hexadecimal digits.
NONCE_BYTES = 16

_NAME_SHAPE = re.compile(r"\A\.fb-i3-verify-[0-9a-f]{32}-(?:staged|linked)\Z")
_NONCE_SHAPE = re.compile(r"\A[0-9a-f]{32}\Z")

#: The account every reviewed effect step runs as — r6 §7.2(2), `run_as="root"`.
ROOT_ACCOUNT = "root"

#: Decision B's narrow exception, as C-P5.0-LAB-I3-D1 states it: canonical `R`
#: is `root:root 0700` and `R/bin` is `root:root 0755` while this verifier holds
#: them.
CANONICAL_OWNER = "root"
CANONICAL_GROUP = "root"
CANONICAL_ROOT_MODE = 0o700
CANONICAL_BIN_MODE = 0o755

#: Read bounds for the three host files. A file longer than its bound is not a
#: file this verifier has established it can read, and it refuses.
STATUS_LIMIT = 64 * 1024
MOUNTINFO_LIMIT = 1024 * 1024
POLICY_LIMIT = 64

#: The final survey reads at most this many entries per directory. A listing
#: longer than the bound is a survey this verifier could not complete.
SURVEY_LIMIT = 4096

#: The three capabilities whose membership is classified in every mask.
OBSERVED_CAPABILITIES: tuple[int, ...] = (
    CAP_DAC_OVERRIDE,
    CAP_DAC_READ_SEARCH,
    CAP_FOWNER,
)

#: Carried by every rendering. It is the one statement about attribution this
#: verifier makes.
NOT_ATTRIBUTION = (
    "Capability masks are recorded as evidence and are never attribution. This "
    "verifier does not isolate, require or prove CAP_FOWNER, and it never reads "
    "CapBnd as CapEff. Each publication relies on the protected-hardlink "
    "filesystem-UID owner condition, which is observed; a root link that "
    "succeeds cannot show which permitted branch the kernel took."
)

#: Why the twelfth identity key is absent.
SECUREBITS_NOT_OBSERVED = (
    "securebits is not observed: the kernel exposes it only through prctl(2), "
    "and the one ctypes exception in this package belongs to the case program."
)

# ---------------------------------------------------------------------------
# Closed vocabularies
# ---------------------------------------------------------------------------


class Invocation(str, Enum):
    """The two reviewed identities. **They are separate invocations.**"""

    ROOT = ROOT_ACCOUNT
    PARTICIPANT = PARTICIPANT_IDENTITY


class ContextId(str, Enum):
    T1 = "T1"
    CAPTURE = "S2.3.3"
    T6 = "T6"
    P2 = "P2"


#: Which contexts each invocation runs, in order. P2 is last because it is the
#: one that creates and removes canonical `R`.
INVOCATION_CONTEXTS: dict[Invocation, tuple[ContextId, ...]] = {
    Invocation.ROOT: (ContextId.T1, ContextId.CAPTURE, ContextId.P2),
    Invocation.PARTICIPANT: (ContextId.T6,),
}


class Stage(str, Enum):
    """Every point at which the procedure's state changes or is observed."""

    ADMISSION = "admission"
    ROOT_CREATE = "canonical-root-create"
    ROOT_OWNERSHIP = "canonical-root-ownership-and-mode"
    ROOT_BARRIER = "canonical-root-entry-barrier"
    BIN_CREATE = "canonical-bin-create"
    BIN_OWNERSHIP = "canonical-bin-ownership-and-mode"
    BIN_BARRIER = "canonical-bin-entry-barrier"
    CANONICAL_MOUNT = "canonical-mount-observation"
    TEMPORARY_CREATE = "temporary-exclusive-create"
    PAYLOAD_WRITE = "payload-write"
    DATA_BARRIER = "payload-data-barrier"
    OWNERSHIP_MODE = "ownership-and-mode"
    TEMPORARY_VERIFY = "temporary-read-back"
    WRITE_RELEASE = "write-descriptor-release"
    OPERATION_STATE = "operation-time-process-state"
    LINK = "exclusive-link"
    TWO_NAMES = "two-name-observation"
    TEMPORARY_REMOVE = "temporary-guarded-removal"
    PUBLISHED_OBSERVE = "published-single-name-observation"
    PUBLISHED_REMOVE = "published-guarded-removal"
    ENTRY_BARRIER = "containing-entry-barrier"
    ABSENCE = "absence-observation"
    BIN_REMOVE = "canonical-bin-guarded-removal"
    BIN_REMOVE_BARRIER = "canonical-bin-removal-barrier"
    ROOT_REMOVE = "canonical-root-guarded-removal"
    ROOT_REMOVE_BARRIER = "canonical-root-removal-barrier"
    ROOT_ABSENCE = "canonical-root-absence-observation"
    CLEANUP = "failure-cleanup"


class Status(str, Enum):
    """The one answer an invocation gives. Only `VERIFIED` is success."""

    VERIFIED = "verified"
    NOT_ARMED = "not-armed"
    REFUSED_BEFORE_WRITE = "refused-before-write"
    FAILED_NO_RESIDUE = "failed-no-residue"
    FAILED_OPERATOR_ATTENTION = "failed-operator-attention"


class ContextStatus(str, Enum):
    VERIFIED = "verified"
    FAILED = "failed"
    NOT_ATTEMPTED = "not-attempted"


class ObjectKind(str, Enum):
    TEMPORARY = "temporary-name"
    PUBLISHED = "published-name"
    CANONICAL_ROOT = "canonical-root"
    CANONICAL_BIN = "canonical-bin"


class ObjectFate(str, Enum):
    """What happened to one tracked object. `REMOVED` is the only clean fate."""

    REMOVED = "removed"
    PRESENT = "present-not-removed"
    UNIDENTIFIED = "residue-identity-never-established"
    REPLACED = "residue-name-resolves-to-another-object"
    VANISHED = "name-absent-before-removal"
    NOT_EMPTY = "residue-directory-not-empty"
    REMOVAL_FAILED = "residue-removal-failed"
    REMOVAL_UNCONFIRMED = "residue-removal-not-confirmed"


# Admission refusals: every one is decided before the first write.
NOT_ARMED = "verifier-not-armed"
INVOCATION_NOT_RECOGNIZED = "invocation-not-recognized"
PAYLOAD_DIGEST_MISMATCH = "payload-digest-mismatch"
TARGET_MISMATCH = "target-mismatch"
TARGET_UNOBSERVABLE = "target-unobservable"
LAYOUT_NOT_DERIVABLE = "layout-not-derivable"
ACCOUNT_UNRESOLVED = "account-unresolved"
STATUS_UNOBSERVABLE = "process-status-unobservable"
IDENTITY_MISMATCH = "identity-mismatch"
GROUP_MEMBERSHIP_MISSING = "group-membership-missing"
CAPABILITY_UNOBSERVABLE = "capability-state-unobservable"
CAPABILITY_INCONSISTENT = "capability-state-inconsistent"
POLICY_UNOBSERVABLE = "hardlink-policy-unobservable"
POLICY_MISMATCH = "hardlink-policy-mismatch"
MOUNT_UNOBSERVABLE = "mount-unobservable"
MOUNT_MISMATCH = "mount-mismatch"
DIRECTORY_UNOBSERVABLE = "directory-unobservable"
DIRECTORY_ABSENT = "directory-absent"
DIRECTORY_WRONG_TYPE = "directory-wrong-type"
DIRECTORY_WRONG_OWNER = "directory-wrong-owner"
DIRECTORY_WRONG_GROUP = "directory-wrong-group"
DIRECTORY_WRONG_MODE = "directory-wrong-mode"
PARENT_UNSAFE = "state-parent-unsafe"
BARRIER_UNAVAILABLE = "barrier-descriptor-unavailable"
CANONICAL_ROOT_PRESENT = "canonical-root-present"
PRIOR_RESIDUE = "prior-verifier-residue"
NONCE_UNAVAILABLE = "nonce-unavailable"
NAME_NOT_ADMISSIBLE = "name-not-admissible"
NAME_OCCUPIED = "name-occupied"
ADMISSION_UNCLASSIFIED = "unclassified-admission-failure"

ADMISSION_REFUSALS: frozenset[str] = frozenset(
    {
        NOT_ARMED,
        INVOCATION_NOT_RECOGNIZED,
        PAYLOAD_DIGEST_MISMATCH,
        TARGET_MISMATCH,
        TARGET_UNOBSERVABLE,
        LAYOUT_NOT_DERIVABLE,
        ACCOUNT_UNRESOLVED,
        STATUS_UNOBSERVABLE,
        IDENTITY_MISMATCH,
        GROUP_MEMBERSHIP_MISSING,
        CAPABILITY_UNOBSERVABLE,
        CAPABILITY_INCONSISTENT,
        POLICY_UNOBSERVABLE,
        POLICY_MISMATCH,
        MOUNT_UNOBSERVABLE,
        MOUNT_MISMATCH,
        DIRECTORY_UNOBSERVABLE,
        DIRECTORY_ABSENT,
        DIRECTORY_WRONG_TYPE,
        DIRECTORY_WRONG_OWNER,
        DIRECTORY_WRONG_GROUP,
        DIRECTORY_WRONG_MODE,
        PARENT_UNSAFE,
        BARRIER_UNAVAILABLE,
        CANONICAL_ROOT_PRESENT,
        PRIOR_RESIDUE,
        NONCE_UNAVAILABLE,
        NAME_NOT_ADMISSIBLE,
        NAME_OCCUPIED,
        ADMISSION_UNCLASSIFIED,
    }
)

# Stage failures: every one is decided after the first write was attempted.
OPERATION_FAILED = "operation-failed"
OBJECT_EXISTS = "object-exists"
OBJECT_IDENTITY_MISMATCH = "object-identity-mismatch"
OBSERVATION_MISMATCH = "observation-mismatch"
OUTCOME_UNCERTAIN = "outcome-uncertain"
OWNER_CONDITION_NOT_OBSERVED = "owner-condition-not-observed"
PROCESS_STATE_CHANGED = "process-state-changed"
DESCRIPTOR_NOT_RELEASED = "descriptor-not-released"
STAGE_UNCLASSIFIED = "unclassified-stage-failure"

STAGE_FAILURES: frozenset[str] = frozenset(
    {
        OPERATION_FAILED,
        OBJECT_EXISTS,
        OBJECT_IDENTITY_MISMATCH,
        OBSERVATION_MISMATCH,
        OUTCOME_UNCERTAIN,
        OWNER_CONDITION_NOT_OBSERVED,
        PROCESS_STATE_CHANGED,
        DESCRIPTOR_NOT_RELEASED,
        STAGE_UNCLASSIFIED,
    }
)


class _Refusal(Exception):
    """An admission refusal. Carries a classification and nothing else."""

    def __init__(self, classification: str) -> None:
        if classification not in ADMISSION_REFUSALS:
            classification = ADMISSION_UNCLASSIFIED
        self.classification = classification
        super().__init__(classification)


class _Failure(Exception):
    """A stage failure. Carries the stage and a classification, nothing else."""

    def __init__(self, stage: Stage, classification: str) -> None:
        if classification not in STAGE_FAILURES:
            classification = STAGE_UNCLASSIFIED
        self.stage = stage
        self.classification = classification
        super().__init__(f"{stage.value}: {classification}")


# ---------------------------------------------------------------------------
# Host observations
# ---------------------------------------------------------------------------


class HostProbe(Protocol):
    """The five reads admission makes of the host, the process and the kernel.

    `ProcHostProbe` is the production one. A test injects another, which is how
    malformed host data reaches the parsers without a malformed host.
    """

    def status(self) -> bytes:
        """`/proc/self/status`, bounded."""

    def protected_hardlinks(self) -> bytes:
        """`/proc/sys/fs/protected_hardlinks`, bounded."""

    def mountinfo(self) -> bytes:
        """`/proc/self/mountinfo`, bounded."""

    def process_ids(self) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        """`(getresuid(), getresgid())`."""

    def host(self) -> tuple[str, str, str]:
        """`uname(2)`'s node name, release and machine.

        The first element is the **kernel nodename**, not the SSH alias: it is
        compared with `APPROVED_TARGET_FACTS.kernel_nodename`. `uname(2)` cannot
        observe an alias, which lives in the operator's SSH configuration.
        """


def _read_bounded(path: str, limit: int) -> bytes:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            total += len(chunk)
            if total > limit:
                raise OSError("bounded read exceeded")
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


class ProcHostProbe:
    """Reads the three `/proc` files and the process's own ids. Nothing else.

    Construction reads nothing; each method reads when it is called.
    """

    def status(self) -> bytes:
        return _read_bounded("/proc/self/status", STATUS_LIMIT)

    def protected_hardlinks(self) -> bytes:
        return _read_bounded("/proc/sys/fs/protected_hardlinks", POLICY_LIMIT)

    def mountinfo(self) -> bytes:
        return _read_bounded("/proc/self/mountinfo", MOUNTINFO_LIMIT)

    def process_ids(self) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        return tuple(os.getresuid()), tuple(os.getresgid())  # type: ignore[return-value]

    def host(self) -> tuple[str, str, str]:
        facts = os.uname()
        return facts.nodename, facts.release, facts.machine


@dataclass(frozen=True, slots=True)
class ProcessStatus:
    """The identity and capability fields of `/proc/self/status`, parsed.

    `uids` and `gids` are `(real, effective, saved, filesystem)`. The
    filesystem uid is the one the protected-hardlink owner condition compares.
    """

    uids: tuple[int, int, int, int]
    gids: tuple[int, int, int, int]
    groups: frozenset[int]
    cap_inh: int
    cap_prm: int
    cap_eff: int
    cap_bnd: int
    cap_amb: int
    no_new_privs: int


_STATUS_KEYS = (
    "Uid",
    "Gid",
    "Groups",
    "CapInh",
    "CapPrm",
    "CapEff",
    "CapBnd",
    "CapAmb",
    "NoNewPrivs",
)
_DECIMAL = re.compile(r"\A[0-9]{1,10}\Z")
_MASK = re.compile(r"\A[0-9a-f]{16}\Z")


def parse_status(raw: bytes) -> ProcessStatus:
    """Parse the nine fields, exactly once each, or refuse.

    A field that is absent, repeated or not in its kernel shape — four decimal
    ids, a decimal group list, sixteen hexadecimal digits per mask, `0` or `1`
    for `NoNewPrivs` — is `STATUS_UNOBSERVABLE` or `CAPABILITY_UNOBSERVABLE`,
    never a default.
    """
    if not isinstance(raw, bytes) or len(raw) > STATUS_LIMIT:
        raise _Refusal(STATUS_UNOBSERVABLE)
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError:
        raise _Refusal(STATUS_UNOBSERVABLE) from None
    found: dict[str, str] = {}
    for line in text.split("\n"):
        key, separator, value = line.partition(":")
        if not separator or key not in _STATUS_KEYS:
            continue
        if key in found:
            raise _Refusal(
                CAPABILITY_UNOBSERVABLE if key.startswith("Cap") else STATUS_UNOBSERVABLE
            )
        found[key] = value.strip()
    for key in ("Uid", "Gid", "Groups"):
        if key not in found:
            raise _Refusal(STATUS_UNOBSERVABLE)
    uids = _four_ids(found["Uid"])
    gids = _four_ids(found["Gid"])
    group_fields = found["Groups"].split()
    if not all(_DECIMAL.match(item) for item in group_fields):
        raise _Refusal(STATUS_UNOBSERVABLE)
    masks: dict[str, int] = {}
    for key in ("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb"):
        value = found.get(key)
        if value is None or not _MASK.match(value):
            raise _Refusal(CAPABILITY_UNOBSERVABLE)
        masks[key] = int(value, 16)
    no_new_privs = found.get("NoNewPrivs")
    if no_new_privs not in ("0", "1"):
        raise _Refusal(CAPABILITY_UNOBSERVABLE)
    return ProcessStatus(
        uids=uids,
        gids=gids,
        groups=frozenset(int(item, 10) for item in group_fields),
        cap_inh=masks["CapInh"],
        cap_prm=masks["CapPrm"],
        cap_eff=masks["CapEff"],
        cap_bnd=masks["CapBnd"],
        cap_amb=masks["CapAmb"],
        no_new_privs=int(no_new_privs, 10),
    )


def _four_ids(value: str) -> tuple[int, int, int, int]:
    fields = value.split()
    if len(fields) != 4 or not all(_DECIMAL.match(item) for item in fields):
        raise _Refusal(STATUS_UNOBSERVABLE)
    real, effective, saved, filesystem = (int(item, 10) for item in fields)
    return real, effective, saved, filesystem


@dataclass(frozen=True, slots=True)
class CapabilityMembership:
    """One capability's membership in each of the five masks, separately."""

    capability: int
    inheritable: bool
    permitted: bool
    effective: bool
    bounding: bool
    ambient: bool

    @property
    def name(self) -> str:
        return CAPABILITY_NAMES[self.capability]


@dataclass(frozen=True, slots=True)
class CapabilityEvidence:
    """The five masks and `NoNewPrivs`, exactly as observed, and a classification.

    It is **evidence**. Nothing in this module derives an authorization from
    it, and `NOT_ATTRIBUTION` is the statement that travels with it.
    """

    cap_inh: int
    cap_prm: int
    cap_eff: int
    cap_bnd: int
    cap_amb: int
    no_new_privs: int
    memberships: tuple[CapabilityMembership, ...]


def classify_capabilities(status: ProcessStatus) -> CapabilityEvidence:
    """Each mask from its own field, and from no other.

    **This is the single point at which masks become a classification.**
    `effective` is read from `CapEff` and `bounding` from `CapBnd`, so a change
    to the bounding set alone cannot change what is reported as effective.
    """
    memberships = tuple(
        CapabilityMembership(
            capability=capability,
            inheritable=bool(status.cap_inh >> capability & 1),
            permitted=bool(status.cap_prm >> capability & 1),
            effective=bool(status.cap_eff >> capability & 1),
            bounding=bool(status.cap_bnd >> capability & 1),
            ambient=bool(status.cap_amb >> capability & 1),
        )
        for capability in OBSERVED_CAPABILITIES
    )
    return CapabilityEvidence(
        cap_inh=status.cap_inh,
        cap_prm=status.cap_prm,
        cap_eff=status.cap_eff,
        cap_bnd=status.cap_bnd,
        cap_amb=status.cap_amb,
        no_new_privs=status.no_new_privs,
        memberships=memberships,
    )


def capabilities_consistent(status: ProcessStatus) -> bool:
    """The two invariants `capabilities(7)` states for any process.

    The effective set is a subset of the permitted set, and the ambient set is
    a subset of both the permitted and the inheritable sets. A status that
    violates either is not a state a kernel reports, so it refuses.
    """
    if status.cap_eff & ~status.cap_prm:
        return False
    if status.cap_amb & ~(status.cap_prm & status.cap_inh):
        return False
    return True


@dataclass(frozen=True, slots=True)
class MountEntry:
    major: int
    minor: int
    fstype: str
    source: str
    options: frozenset[str]


def parse_mountinfo(raw: bytes) -> tuple[MountEntry, ...]:
    """`proc_pid_mountinfo(5)`, strictly: every line or none."""
    if not isinstance(raw, bytes) or len(raw) > MOUNTINFO_LIMIT:
        raise _Refusal(MOUNT_UNOBSERVABLE)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise _Refusal(MOUNT_UNOBSERVABLE) from None
    entries: list[MountEntry] = []
    for line in text.split("\n"):
        if not line:
            continue
        fields = line.split(" ")
        try:
            separator = fields.index("-", 6)
        except ValueError:
            raise _Refusal(MOUNT_UNOBSERVABLE) from None
        if len(fields) < separator + 3:
            raise _Refusal(MOUNT_UNOBSERVABLE)
        major, colon, minor = fields[2].partition(":")
        if not colon or not _DECIMAL.match(major) or not _DECIMAL.match(minor):
            raise _Refusal(MOUNT_UNOBSERVABLE)
        entries.append(
            MountEntry(
                major=int(major, 10),
                minor=int(minor, 10),
                fstype=fields[separator + 1],
                source=fields[separator + 2],
                options=frozenset(fields[5].split(",")),
            )
        )
    if not entries:
        raise _Refusal(MOUNT_UNOBSERVABLE)
    return tuple(entries)


def mount_matches(device: int, mounts: tuple[MountEntry, ...]) -> bool:
    """Every mount of this device is the approved filesystem, read-write.

    The expected type and source are the approved target's own facts, read
    rather than restated. At least one entry must match the device.
    """
    matching = [
        entry
        for entry in mounts
        if (entry.major, entry.minor) == (os.major(device), os.minor(device))
    ]
    if not matching:
        return False
    return all(
        entry.fstype == APPROVED_TARGET_FACTS.filesystem_type
        and entry.source == APPROVED_TARGET_FACTS.filesystem_device
        and "rw" in entry.options
        and "ro" not in entry.options
        for entry in matching
    )


def parse_policy(raw: bytes) -> int:
    """`fs.protected_hardlinks`, which is exactly one digit and a newline."""
    if raw in (b"0\n", b"1\n"):
        return int(raw[:1])
    raise _Refusal(POLICY_UNOBSERVABLE)


# ---------------------------------------------------------------------------
# The layout
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class I3Layout:
    """Where the four contexts live, as one provisioned root and components.

    `state_parent` is the only pathname opened; every other directory is one
    component under a descriptor already held.
    """

    state_parent: str
    state_root_name: str
    laboratory_name: str
    runs_name: str
    recovery_name: str
    canonical_root_name: str
    bin_name: str


def _split(path: str) -> tuple[str, str]:
    if not isinstance(path, str) or not path.startswith("/") or path.endswith("/"):
        raise _Refusal(LAYOUT_NOT_DERIVABLE)
    parent, _, name = path.rpartition("/")
    if not name or name in (".", ".."):
        raise _Refusal(LAYOUT_NOT_DERIVABLE)
    return parent or "/", name


def i3_layout(
    *,
    layout: LaboratoryLayout = LABORATORY_LAYOUT,
    evidence_root: str = EVIDENCE_ROOT,
) -> I3Layout:
    """Derive the four contexts' directories from the reviewed definitions.

    The laboratory and recovery directories must share one parent (V12), and
    that parent and canonical `R` must share one parent. Nothing here restates a
    path: the production values are `LABORATORY_LAYOUT` and `EVIDENCE_ROOT`,
    which reads the approved target's root.
    """
    state_root, laboratory_name = _split(layout.laboratory_directory)
    recovery_root, recovery_name = _split(layout.recovery_directory)
    if recovery_root != state_root or laboratory_name == recovery_name:
        raise _Refusal(LAYOUT_NOT_DERIVABLE)
    state_parent, state_root_name = _split(state_root)
    evidence_parent, canonical_root_name = _split(evidence_root)
    if evidence_parent != state_parent or canonical_root_name == state_root_name:
        raise _Refusal(LAYOUT_NOT_DERIVABLE)
    bin_name, separator, _case = CASE_PROGRAM_RELATIVE_PATH.partition("/")
    if not separator or not bin_name:
        raise _Refusal(LAYOUT_NOT_DERIVABLE)
    return I3Layout(
        state_parent=state_parent,
        state_root_name=state_root_name,
        laboratory_name=laboratory_name,
        runs_name=layout.runs_directory_name,
        recovery_name=recovery_name,
        canonical_root_name=canonical_root_name,
        bin_name=bin_name,
    )


def verifier_names(nonce: str) -> tuple[str, str]:
    """`(temporary, published)` for one nonce."""
    return (
        f"{NAME_PREFIX}{nonce}{TEMPORARY_NAME_SUFFIX}",
        f"{NAME_PREFIX}{nonce}{PUBLISHED_NAME_SUFFIX}",
    )


def name_is_admissible(name: str) -> bool:
    """A verifier name, and outside every grammar a reader of the directory has.

    The run-identifier grammar begins with a letter or digit; the lifecycle
    record, the ledger and the recovery store treat a `.tmp` suffix as an
    interrupted publication and a `.record` suffix as a recovery record; the
    case program is `bin/case`. A verifier name begins with a dot, ends with
    `-staged` or `-linked`, and so is none of them.
    """
    return (
        isinstance(name, str)
        and bool(_NAME_SHAPE.match(name))
        and not name[:1].isalnum()
        and not name.endswith(TEMPORARY_SUFFIX)
        and not name.endswith(RECORD_SUFFIX)
        and name != LABORATORY_LAYOUT.record_name
        and name != f"{LABORATORY_LAYOUT.record_name}{TEMPORARY_SUFFIX}"
        and name != CASE_PROGRAM_RELATIVE_PATH.rpartition("/")[2]
    )


# ---------------------------------------------------------------------------
# What a run returns
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class TrackedObject:
    """One object this invocation created, from the moment it exists."""

    context: ContextId
    kind: ObjectKind
    #: `st_dev:st_ino`, or `""` when the identity was never established.
    identity: str
    fate: ObjectFate = ObjectFate.PRESENT


@dataclass(frozen=True, slots=True)
class ContextOutcome:
    context: ContextId
    status: ContextStatus
    nonce: str = ""
    completed: tuple[Stage, ...] = ()
    failed_stage: Stage | None = None
    failure: str = ""
    object_identity: str = ""
    link_count_with_both_names: int = 0
    link_count_after_temporary_removed: int = 0
    payload_matched: bool = False
    owner_condition_observed: bool = False
    file_mode: int = -1
    applied_ownership: bool = False
    capability_at_link: CapabilityEvidence | None = None
    objects: tuple[TrackedObject, ...] = ()
    cleanup_barrier_failures: int = 0
    descriptor_release_failures: int = 0


@dataclass(frozen=True, slots=True)
class SurveyResult:
    performed: bool
    #: Verifier names found in the directories this invocation held.
    verifier_names_found: int = 0
    canonical_root_present: bool = False
    failed: bool = False


@dataclass(frozen=True, slots=True)
class VerificationRun:
    invocation: Invocation | None
    status: Status
    refusal: str = ""
    capability_at_admission: CapabilityEvidence | None = None
    hardlink_policy: int = -1
    contexts: tuple[ContextOutcome, ...] = ()
    survey: SurveyResult = SurveyResult(performed=False)
    unreleased_roles: int = 0

    @property
    def verified(self) -> bool:
        return self.status is Status.VERIFIED


# ---------------------------------------------------------------------------
# The mechanism
# ---------------------------------------------------------------------------

#: Inventory role names. **None is `plan.EVIDENCE_ROLE`**: its production
#: registration stays deferred (decision D), and this verifier holds `R`'s
#: parent under its own name.
_STATE_PARENT = "i3-state-parent"
_STATE_ROOT = "i3-state-root"
_LABORATORY = "i3-laboratory"
_RUNS = "i3-runs"
_RECOVERY = "i3-recovery"
_CANONICAL_ROOT = "i3-canonical-root"
_CANONICAL_BIN = "i3-canonical-bin"

_FOREIGN_WRITE_BITS = stat.S_IWGRP | stat.S_IWOTH


@dataclass(frozen=True, slots=True)
class _ContextPlan:
    context: ContextId
    directory_role: str
    nonce: str
    temporary: str
    published: str
    file_uid: int
    file_gid: int
    #: The mode applied to the write descriptor and observed on both names.
    file_mode: int
    #: The mode the exclusive `openat` creates the temporary *pathname* with.
    #: `EXCLUSIVE_CREATION_MODE` for T1, §2.3.3 and T6; P2 alone carries
    #: `CASE_PROGRAM_TEMPORARY_MODE` — C-P5.0-LAB-I3-R3, 2026-09-20.
    creation_mode: int
    apply_ownership: bool


@dataclass(slots=True)
class _Session:
    invocation: Invocation
    layout: I3Layout
    inventory: DescriptorInventory
    filesystem: PosixFilesystem
    status: ProcessStatus
    mounts: tuple[MountEntry, ...]
    root_uid: int
    root_gid: int
    plans: tuple[_ContextPlan, ...]
    events: list[tuple[ContextId, Stage]]


@dataclass(slots=True)
class _ContextRecord:
    plan: _ContextPlan
    completed: list[Stage] = field(default_factory=list)
    objects: list[TrackedObject] = field(default_factory=list)
    failed_stage: Stage | None = None
    failure: str = ""
    link_count_two: int = 0
    link_count_one: int = 0
    payload_matched: bool = False
    owner_condition_observed: bool = False
    capability_at_link: CapabilityEvidence | None = None
    cleanup_barrier_failures: int = 0
    release_failures: int = 0
    identity: str = ""


def _same_object(recorded: str, facts: os.stat_result | None) -> bool:
    """**The one identity comparison every guarded removal makes.**

    A recorded identity that was never established compares equal to nothing.
    """
    if not recorded or facts is None:
        return False
    return f"{facts.st_dev}:{facts.st_ino}" == recorded


def _lstat_at(dirfd: int, name: str) -> os.stat_result | None:
    """`fstatat(dirfd, name, AT_SYMLINK_NOFOLLOW)`, or `None` when absent.

    `PosixFilesystem.fstatat` returns the identity alone; the two-name
    observation also needs the type, owner, group, mode and link count, so this
    reads the whole record through the same descriptor-relative, no-follow
    call. Any failure other than absence raises.
    """
    try:
        return os.stat(name, dir_fd=dirfd, follow_symlinks=False)
    except FileNotFoundError:
        return None


@dataclass(slots=True)
class I3ControlledWriteVerifier:
    """The separately armed I3 verifier. Unarmed by default.

    `lookup`, `probe` and `nonce` are the account, `/proc` and randomness seams;
    `layout` is where the four contexts live. `events` records every completed
    stage in order, which is how the suite asserts the reviewed order.
    """

    lookup: OwnershipLookup
    probe: HostProbe
    armed: bool = False
    layout: I3Layout | None = None
    nonce: Callable[[], bytes] = field(default=lambda: os.urandom(NONCE_BYTES))
    events: list[tuple[ContextId, Stage]] = field(default_factory=list)

    # -- the in-code gate -----------------------------------------------------

    def _require_armed(self) -> None:
        """**The second, independent effect gate.** `armed` must be exactly
        `True`; it is re-checked before every creating effect."""
        if self.armed is not True:
            raise _Refusal(NOT_ARMED)

    # -- the run --------------------------------------------------------------

    def run(self, invocation: Invocation | str) -> VerificationRun:
        try:
            self._require_armed()
        except _Refusal:
            return VerificationRun(
                invocation=None, status=Status.NOT_ARMED, refusal=NOT_ARMED
            )
        try:
            chosen = Invocation(invocation)
        except ValueError:
            return VerificationRun(
                invocation=None,
                status=Status.REFUSED_BEFORE_WRITE,
                refusal=INVOCATION_NOT_RECOGNIZED,
            )
        inventory = DescriptorInventory()
        filesystem = PosixFilesystem(inventory)
        try:
            session = self._admit(chosen, inventory, filesystem)
        except _Refusal as refusal:
            unreleased = inventory.release_all()
            return VerificationRun(
                invocation=chosen,
                status=Status.REFUSED_BEFORE_WRITE,
                refusal=refusal.classification,
                unreleased_roles=len(unreleased),
            )
        except Exception:  # noqa: BLE001 - admission writes nothing; say only that
            unreleased = inventory.release_all()
            return VerificationRun(
                invocation=chosen,
                status=Status.REFUSED_BEFORE_WRITE,
                refusal=ADMISSION_UNCLASSIFIED,
                unreleased_roles=len(unreleased),
            )
        capability = classify_capabilities(session.status)
        outcomes: list[ContextOutcome] = []
        stopped = False
        for plan in session.plans:
            if stopped:
                outcomes.append(
                    ContextOutcome(
                        context=plan.context,
                        status=ContextStatus.NOT_ATTEMPTED,
                        nonce=plan.nonce,
                    )
                )
                continue
            outcome = self._run_context(session, plan)
            outcomes.append(outcome)
            if outcome.status is not ContextStatus.VERIFIED:
                stopped = True
        survey = self._survey(session)
        unreleased = inventory.release_all()
        status = final_status(tuple(outcomes), survey, len(unreleased))
        return VerificationRun(
            invocation=chosen,
            status=status,
            capability_at_admission=capability,
            hardlink_policy=1,
            contexts=tuple(outcomes),
            survey=survey,
            unreleased_roles=len(unreleased),
        )

    # -- admission ------------------------------------------------------------

    def _admit(
        self,
        invocation: Invocation,
        inventory: DescriptorInventory,
        filesystem: PosixFilesystem,
    ) -> _Session:
        if hashlib.sha256(PAYLOAD).hexdigest() != PAYLOAD_SHA256:
            raise _Refusal(PAYLOAD_DIGEST_MISMATCH)
        # The exact target: the approved **kernel nodename**, kernel and
        # architecture, read from the approved target's facts rather than
        # restated. The nodename is what `uname(2)` reports, so it is what the
        # observation is compared with; `APPROVED_TARGET_FACTS.host` is the SSH
        # alias from runbook §2 and is deliberately not compared here — that
        # substitution is what refused C-P5.0-LAB-I3-R4 with `target-mismatch`,
        # and Peter's Option A decision of 2026-09-20 separated the two facts.
        try:
            host = tuple(self.probe.host())
        except Exception:  # noqa: BLE001
            raise _Refusal(TARGET_UNOBSERVABLE) from None
        if host != (
            APPROVED_TARGET_FACTS.kernel_nodename,
            APPROVED_TARGET_FACTS.active_kernel,
            APPROVED_TARGET_FACTS.architecture,
        ):
            raise _Refusal(TARGET_MISMATCH)
        layout = self.layout if self.layout is not None else i3_layout()
        items = items_by_id()

        account = invocation.value
        uid, gid = self._account(account)
        root_uid, _root_primary = self._account(ROOT_ACCOUNT)
        root_gid = self._group(CANONICAL_GROUP)
        laboratory_gid = self._group(LABORATORY_GROUP)
        case_uid, _case_primary = self._account(CASE_PROGRAM_OWNER)
        case_gid = self._group(CASE_PROGRAM_GROUP)

        status = self._observe_status()
        if status.uids != (uid, uid, uid, uid) or status.gids != (gid, gid, gid, gid):
            raise _Refusal(IDENTITY_MISMATCH)
        try:
            resuid, resgid = self.probe.process_ids()
        except Exception:  # noqa: BLE001 - an unobservable id is a refusal
            raise _Refusal(STATUS_UNOBSERVABLE) from None
        if tuple(resuid) != status.uids[:3] or tuple(resgid) != status.gids[:3]:
            raise _Refusal(IDENTITY_MISMATCH)
        if invocation is Invocation.PARTICIPANT and laboratory_gid not in status.groups:
            raise _Refusal(GROUP_MEMBERSHIP_MISSING)
        if not capabilities_consistent(status):
            raise _Refusal(CAPABILITY_INCONSISTENT)

        try:
            policy = parse_policy(self.probe.protected_hardlinks())
        except _Refusal:
            raise
        except Exception:  # noqa: BLE001
            raise _Refusal(POLICY_UNOBSERVABLE) from None
        if policy != 1:
            raise _Refusal(POLICY_MISMATCH)

        try:
            mounts = parse_mountinfo(self.probe.mountinfo())
        except _Refusal:
            raise
        except Exception:  # noqa: BLE001
            raise _Refusal(MOUNT_UNOBSERVABLE) from None

        # The provisioned root: `R`'s parent and V12's parent. Root-owned and
        # not group- or other-writable, which is r6 §1.4.1's [A] observed.
        state_parent = self._open_root(inventory, _STATE_PARENT, layout.state_parent)
        if not stat.S_ISDIR(state_parent.st_mode):
            raise _Refusal(DIRECTORY_WRONG_TYPE)
        if state_parent.st_uid != root_uid or state_parent.st_mode & _FOREIGN_WRITE_BITS:
            raise _Refusal(PARENT_UNSAFE)
        held: list[str] = [_STATE_PARENT]

        def adopt(parent: str, name: str, role: str, item_id: str) -> None:
            item = items[item_id]
            facts = self._adopt(inventory, parent, name, role)
            if not stat.S_ISDIR(facts.st_mode):
                raise _Refusal(DIRECTORY_WRONG_TYPE)
            if facts.st_uid != self._account(item.owner)[0]:
                raise _Refusal(DIRECTORY_WRONG_OWNER)
            if facts.st_gid != self._group(item.group):
                raise _Refusal(DIRECTORY_WRONG_GROUP)
            if stat.S_IMODE(facts.st_mode) != item.mode:
                raise _Refusal(DIRECTORY_WRONG_MODE)
            held.append(role)

        adopt(_STATE_PARENT, layout.state_root_name, _STATE_ROOT, "V12")
        adopt(_STATE_ROOT, layout.laboratory_name, _LABORATORY, "V4")
        if invocation is Invocation.ROOT:
            adopt(_STATE_ROOT, layout.recovery_name, _RECOVERY, "V5")
            publication_roles = (_LABORATORY, _RECOVERY)
        else:
            adopt(_LABORATORY, layout.runs_name, _RUNS, "V9")
            publication_roles = (_RUNS,)

        for role in held:
            try:
                device = os.fstat(inventory.traversal(role)).st_dev
            except OSError:
                raise _Refusal(MOUNT_UNOBSERVABLE) from None
            if not mount_matches(device, mounts):
                raise _Refusal(MOUNT_MISMATCH)

        barrier_roles = publication_roles + (
            (_STATE_PARENT,) if invocation is Invocation.ROOT else ()
        )
        for role in barrier_roles:
            try:
                inventory.bind_synchronizable(role)
            except DescriptorRefused:
                raise _Refusal(BARRIER_UNAVAILABLE) from None

        if invocation is Invocation.ROOT:
            present = self._lstat_admission(
                inventory.traversal(_STATE_PARENT), layout.canonical_root_name
            )
            if present is not None:
                raise _Refusal(CANONICAL_ROOT_PRESENT)
        for role in publication_roles:
            if any(name.startswith(NAME_PREFIX) for name in self._listing(inventory, role)):
                raise _Refusal(PRIOR_RESIDUE)

        plans: list[_ContextPlan] = []
        for context in INVOCATION_CONTEXTS[invocation]:
            nonce = self._nonce_text()
            temporary, published = verifier_names(nonce)
            if not (name_is_admissible(temporary) and name_is_admissible(published)):
                raise _Refusal(NAME_NOT_ADMISSIBLE)
            # `created` is the temporary pathname's creation mode; `mode` is the
            # mode applied to the descriptor and observed on both names. Only
            # P2 distinguishes them — C-P5.0-LAB-I3-R3.
            created = EXCLUSIVE_CREATION_MODE
            if context is ContextId.T1:
                role, file_uid, file_gid, mode, own = _LABORATORY, uid, gid, EXCLUSIVE_CREATION_MODE, False
            elif context is ContextId.CAPTURE:
                role, file_uid, file_gid, mode, own = _RECOVERY, uid, gid, STORED_OBJECT_MODE, False
            elif context is ContextId.T6:
                role, file_uid, file_gid, mode, own = _RUNS, uid, laboratory_gid, EXCLUSIVE_CREATION_MODE, False
            else:
                role, file_uid, file_gid, mode, own = (
                    _CANONICAL_BIN,
                    case_uid,
                    case_gid,
                    int(CASE_PROGRAM_MODE, 8),
                    True,
                )
                created = int(CASE_PROGRAM_TEMPORARY_MODE, 8)
            if role != _CANONICAL_BIN:
                traversal = inventory.traversal(role)
                for name in (temporary, published):
                    if self._lstat_admission(traversal, name) is not None:
                        raise _Refusal(NAME_OCCUPIED)
            plans.append(
                _ContextPlan(
                    context=context,
                    directory_role=role,
                    nonce=nonce,
                    temporary=temporary,
                    published=published,
                    file_uid=file_uid,
                    file_gid=file_gid,
                    file_mode=mode,
                    creation_mode=created,
                    apply_ownership=own,
                )
            )
        # The owner condition compares the file's owner with the linking
        # process's filesystem uid, so every file this invocation links must be
        # owned by exactly that uid.
        if any(plan.file_uid != status.uids[3] for plan in plans):
            raise _Refusal(IDENTITY_MISMATCH)
        return _Session(
            invocation=invocation,
            layout=layout,
            inventory=inventory,
            filesystem=filesystem,
            status=status,
            mounts=mounts,
            root_uid=root_uid,
            root_gid=root_gid,
            plans=tuple(plans),
            events=self.events,
        )

    def _account(self, name: str) -> tuple[int, int]:
        try:
            uid, gid = self.lookup.account(name)
        except Exception:  # noqa: BLE001 - the lookup's text is never shown
            raise _Refusal(ACCOUNT_UNRESOLVED) from None
        return int(uid), int(gid)

    def _group(self, name: str) -> int:
        try:
            return int(self.lookup.group_id(name))
        except Exception:  # noqa: BLE001
            raise _Refusal(ACCOUNT_UNRESOLVED) from None

    def _observe_status(self) -> ProcessStatus:
        try:
            raw = self.probe.status()
        except Exception:  # noqa: BLE001
            raise _Refusal(STATUS_UNOBSERVABLE) from None
        return parse_status(raw)

    def _nonce_text(self) -> str:
        try:
            raw = self.nonce()
        except Exception:  # noqa: BLE001
            raise _Refusal(NONCE_UNAVAILABLE) from None
        if not isinstance(raw, bytes) or len(raw) != NONCE_BYTES:
            raise _Refusal(NONCE_UNAVAILABLE)
        text = raw.hex()
        if not _NONCE_SHAPE.match(text):
            raise _Refusal(NONCE_UNAVAILABLE)
        return text

    @staticmethod
    def _open_root(inventory: DescriptorInventory, role: str, path: str) -> os.stat_result:
        try:
            handle = inventory.open_provisioned_root(role, path)
            return os.fstat(handle.traversal_fd)
        except DescriptorRefused as refusal:
            if refusal.classification == DESCRIPTOR_OBJECT_ABSENT:
                raise _Refusal(DIRECTORY_ABSENT) from None
            raise _Refusal(DIRECTORY_UNOBSERVABLE) from None
        except OSError:
            raise _Refusal(DIRECTORY_UNOBSERVABLE) from None

    @staticmethod
    def _adopt(
        inventory: DescriptorInventory, parent: str, name: str, role: str
    ) -> os.stat_result:
        try:
            handle = inventory.adopt_directory(parent_role=parent, name=name, role=role)
            return os.fstat(handle.traversal_fd)
        except DescriptorRefused as refusal:
            if refusal.classification == DESCRIPTOR_OBJECT_ABSENT:
                raise _Refusal(DIRECTORY_ABSENT) from None
        except OSError:
            raise _Refusal(DIRECTORY_UNOBSERVABLE) from None
        # `O_DIRECTORY|O_NOFOLLOW` refused the name. A symbolic link or any
        # other non-directory there is the wrong type and is never followed;
        # anything else is an observation that did not complete.
        try:
            facts = _lstat_at(inventory.traversal(parent), name)
        except (OSError, DescriptorRefused):
            raise _Refusal(DIRECTORY_UNOBSERVABLE) from None
        if facts is not None and not stat.S_ISDIR(facts.st_mode):
            raise _Refusal(DIRECTORY_WRONG_TYPE)
        raise _Refusal(DIRECTORY_UNOBSERVABLE)

    @staticmethod
    def _lstat_admission(dirfd: int, name: str) -> os.stat_result | None:
        try:
            return _lstat_at(dirfd, name)
        except OSError:
            raise _Refusal(DIRECTORY_UNOBSERVABLE) from None

    @staticmethod
    def _listing(inventory: DescriptorInventory, role: str) -> tuple[str, ...]:
        try:
            names = inventory.listing(role)
        except DescriptorRefused:
            raise _Refusal(DIRECTORY_UNOBSERVABLE) from None
        if len(names) > SURVEY_LIMIT:
            raise _Refusal(DIRECTORY_UNOBSERVABLE)
        return names

    # -- one context ----------------------------------------------------------

    def _run_context(self, session: _Session, plan: _ContextPlan) -> ContextOutcome:
        record = _ContextRecord(plan=plan)
        try:
            if plan.context is ContextId.P2:
                self._create_canonical(session, record)
            self._publish_observe_remove(session, record)
            if plan.context is ContextId.P2:
                self._remove_canonical(session, record)
        except _Failure as failure:
            self._fail(record, failure.stage, failure.classification)
        except _Refusal:
            self._fail(record, self._current(record), STAGE_UNCLASSIFIED)
        except Exception:  # noqa: BLE001 - classified, and cleanup still runs
            self._fail(record, self._current(record), STAGE_UNCLASSIFIED)
        if record.failed_stage is not None:
            self._cleanup(session, record)
        return ContextOutcome(
            context=plan.context,
            status=(
                ContextStatus.VERIFIED
                if record.failed_stage is None
                else ContextStatus.FAILED
            ),
            nonce=plan.nonce,
            completed=tuple(record.completed),
            failed_stage=record.failed_stage,
            failure=record.failure,
            object_identity=record.identity,
            link_count_with_both_names=record.link_count_two,
            link_count_after_temporary_removed=record.link_count_one,
            payload_matched=record.payload_matched,
            owner_condition_observed=record.owner_condition_observed,
            file_mode=plan.file_mode,
            applied_ownership=plan.apply_ownership,
            capability_at_link=record.capability_at_link,
            objects=tuple(record.objects),
            cleanup_barrier_failures=record.cleanup_barrier_failures,
            descriptor_release_failures=record.release_failures,
        )

    @staticmethod
    def _current(record: _ContextRecord) -> Stage:
        order = list(Stage)
        if not record.completed:
            return Stage.ADMISSION
        index = order.index(record.completed[-1])
        return order[min(index + 1, len(order) - 1)]

    @staticmethod
    def _fail(record: _ContextRecord, stage: Stage, classification: str) -> None:
        """The first causal failure wins; a later one never replaces it."""
        if record.failed_stage is None:
            record.failed_stage = stage
            record.failure = (
                classification if classification in STAGE_FAILURES else STAGE_UNCLASSIFIED
            )

    def _done(self, session: _Session, record: _ContextRecord, stage: Stage) -> None:
        record.completed.append(stage)
        session.events.append((record.plan.context, stage))

    def _release(self, session: _Session, record: _ContextRecord, number: int) -> bool:
        released = session.filesystem.release(number)
        if not released:
            record.release_failures += 1
        return released

    # -- canonical R and R/bin -------------------------------------------------

    def _create_canonical(self, session: _Session, record: _ContextRecord) -> None:
        layout = session.layout
        self._create_directory(
            session,
            record,
            parent_role=_STATE_PARENT,
            name=layout.canonical_root_name,
            role=_CANONICAL_ROOT,
            kind=ObjectKind.CANONICAL_ROOT,
            mode=CANONICAL_ROOT_MODE,
            stages=(Stage.ROOT_CREATE, Stage.ROOT_OWNERSHIP, Stage.ROOT_BARRIER),
        )
        self._create_directory(
            session,
            record,
            parent_role=_CANONICAL_ROOT,
            name=layout.bin_name,
            role=_CANONICAL_BIN,
            kind=ObjectKind.CANONICAL_BIN,
            mode=CANONICAL_BIN_MODE,
            stages=(Stage.BIN_CREATE, Stage.BIN_OWNERSHIP, Stage.BIN_BARRIER),
        )
        for role in (_CANONICAL_ROOT, _CANONICAL_BIN):
            try:
                device = os.fstat(session.inventory.traversal(role)).st_dev
            except OSError:
                raise _Failure(Stage.CANONICAL_MOUNT, OPERATION_FAILED) from None
            if not mount_matches(device, session.mounts):
                raise _Failure(Stage.CANONICAL_MOUNT, OBSERVATION_MISMATCH)
        try:
            session.inventory.bind_synchronizable(_CANONICAL_BIN)
        except DescriptorRefused:
            raise _Failure(Stage.CANONICAL_MOUNT, OPERATION_FAILED) from None
        self._done(session, record, Stage.CANONICAL_MOUNT)

    def _create_directory(
        self,
        session: _Session,
        record: _ContextRecord,
        *,
        parent_role: str,
        name: str,
        role: str,
        kind: ObjectKind,
        mode: int,
        stages: tuple[Stage, Stage, Stage],
    ) -> None:
        create, ownership, barrier = stages
        self._require_armed()
        inventory = session.inventory
        parent_fd = inventory.traversal(parent_role)
        try:
            handle = inventory.create_directory(
                parent_role=parent_role, name=name, role=role, mode=mode
            )
        except DescriptorRefused as refusal:
            if refusal.classification == DESCRIPTOR_OBJECT_EXISTS:
                # Somebody else's object. Never tracked, never removed.
                raise _Failure(create, OBJECT_EXISTS) from None
            self._track_unidentified_if_present(record, kind, parent_fd, name)
            raise _Failure(create, OUTCOME_UNCERTAIN) from None
        tracked = TrackedObject(
            context=record.plan.context, kind=kind, identity=handle.identity.object_id
        )
        record.objects.append(tracked)
        self._done(session, record, create)

        try:
            descriptor = session.filesystem.openat(parent_fd, name, DescriptorMode.O_RDONLY)
        except DescriptorRefused:
            raise _Failure(ownership, OPERATION_FAILED) from None
        failure: _Failure | None = None
        try:
            if descriptor.object_id != tracked.identity:
                failure = _Failure(ownership, OBJECT_IDENTITY_MISMATCH)
            else:
                os.fchown(descriptor.number, session.root_uid, session.root_gid)
                os.fchmod(descriptor.number, mode)
                facts = os.fstat(descriptor.number)
                if (
                    not stat.S_ISDIR(facts.st_mode)
                    or facts.st_uid != session.root_uid
                    or facts.st_gid != session.root_gid
                    or stat.S_IMODE(facts.st_mode) != mode
                    or facts.st_nlink != 2
                ):
                    failure = _Failure(ownership, OBSERVATION_MISMATCH)
        except OSError:
            failure = _Failure(ownership, OPERATION_FAILED)
        released = self._release(session, record, descriptor.number)
        if failure is not None:
            raise failure
        if not released:
            raise _Failure(ownership, DESCRIPTOR_NOT_RELEASED)
        self._done(session, record, ownership)

        try:
            inventory.fsync_entry(parent_role)
        except DescriptorRefused:
            raise _Failure(barrier, OPERATION_FAILED) from None
        self._done(session, record, barrier)
        if role == _CANONICAL_ROOT:
            try:
                inventory.bind_synchronizable(_CANONICAL_ROOT)
            except DescriptorRefused:
                raise _Failure(barrier, OPERATION_FAILED) from None

    def _track_unidentified_if_present(
        self, record: _ContextRecord, kind: ObjectKind, dirfd: int, name: str
    ) -> None:
        try:
            present = _lstat_at(dirfd, name)
        except OSError:
            present = None
            # Unknown whether anything is there: account for it as unidentified.
            record.objects.append(
                TrackedObject(
                    context=record.plan.context,
                    kind=kind,
                    identity="",
                    fate=ObjectFate.UNIDENTIFIED,
                )
            )
            return
        if present is not None:
            record.objects.append(
                TrackedObject(
                    context=record.plan.context,
                    kind=kind,
                    identity="",
                    fate=ObjectFate.UNIDENTIFIED,
                )
            )

    # -- the publication, the observation and the removal ----------------------

    def _publish_observe_remove(self, session: _Session, record: _ContextRecord) -> None:
        plan = record.plan
        fs = session.filesystem
        traversal = session.inventory.traversal(plan.directory_role)

        # 1. Exclusive temporary creation — B1.
        self._require_armed()
        try:
            descriptor = fs.create_file(
                traversal, plan.temporary, mode=plan.creation_mode
            )
        except DescriptorRefused as refusal:
            if refusal.classification == DESCRIPTOR_OBJECT_EXISTS:
                raise _Failure(Stage.TEMPORARY_CREATE, OBJECT_EXISTS) from None
            self._track_unidentified_if_present(
                record, ObjectKind.TEMPORARY, traversal, plan.temporary
            )
            raise _Failure(Stage.TEMPORARY_CREATE, OUTCOME_UNCERTAIN) from None
        except OSError:
            self._track_unidentified_if_present(
                record, ObjectKind.TEMPORARY, traversal, plan.temporary
            )
            raise _Failure(Stage.TEMPORARY_CREATE, OUTCOME_UNCERTAIN) from None
        temporary = TrackedObject(
            context=plan.context, kind=ObjectKind.TEMPORARY, identity=descriptor.object_id
        )
        record.objects.append(temporary)
        record.identity = descriptor.object_id
        self._done(session, record, Stage.TEMPORARY_CREATE)

        # 2–5. Complete write, data barrier, ownership/mode, read-back — all on
        # the descriptor that created the object.
        failure: _Failure | None = None
        stage = Stage.PAYLOAD_WRITE
        try:
            fs.write(descriptor.number, PAYLOAD)
            self._done(session, record, Stage.PAYLOAD_WRITE)
            stage = Stage.DATA_BARRIER
            fs.fsync(descriptor.number, barrier="i3-payload-data")
            self._done(session, record, Stage.DATA_BARRIER)
            stage = Stage.OWNERSHIP_MODE
            if plan.apply_ownership:
                os.fchown(descriptor.number, plan.file_uid, plan.file_gid)
            os.fchmod(descriptor.number, plan.file_mode)
            self._done(session, record, Stage.OWNERSHIP_MODE)
            stage = Stage.TEMPORARY_VERIFY
            facts = os.fstat(descriptor.number)
            if (
                not stat.S_ISREG(facts.st_mode)
                or f"{facts.st_dev}:{facts.st_ino}" != temporary.identity
                or facts.st_uid != plan.file_uid
                or facts.st_gid != plan.file_gid
                or stat.S_IMODE(facts.st_mode) != plan.file_mode
                or facts.st_nlink != 1
                or facts.st_size != len(PAYLOAD)
            ):
                failure = _Failure(Stage.TEMPORARY_VERIFY, OBSERVATION_MISMATCH)
            elif facts.st_uid != session.status.uids[3]:
                # The owner condition, observed: the linking process's
                # filesystem uid owns the file.
                failure = _Failure(Stage.TEMPORARY_VERIFY, OWNER_CONDITION_NOT_OBSERVED)
            else:
                record.owner_condition_observed = True
                self._done(session, record, Stage.TEMPORARY_VERIFY)
        except DescriptorRefused:
            failure = _Failure(stage, OPERATION_FAILED)
        except OSError:
            failure = _Failure(stage, OPERATION_FAILED)
        released = self._release(session, record, descriptor.number)
        if failure is not None:
            raise failure
        if not released:
            raise _Failure(Stage.WRITE_RELEASE, DESCRIPTOR_NOT_RELEASED)
        self._done(session, record, Stage.WRITE_RELEASE)

        # 6. The process state at the operation, observed again.
        try:
            now = self._observe_status()
        except _Refusal:
            raise _Failure(Stage.OPERATION_STATE, OPERATION_FAILED) from None
        if now != session.status:
            raise _Failure(Stage.OPERATION_STATE, PROCESS_STATE_CHANGED)
        record.capability_at_link = classify_capabilities(now)
        self._done(session, record, Stage.OPERATION_STATE)

        # 7. The exclusive link — the one reviewed primitive.
        try:
            fs.linkat(traversal, plan.temporary, traversal, plan.published)
        except DescriptorRefused as refusal:
            if refusal.classification == DESCRIPTOR_OBJECT_EXISTS:
                # Occupied: never overwritten, never tracked, never removed.
                raise _Failure(Stage.LINK, OBJECT_EXISTS) from None
            self._track_published_if_ours(record, traversal, temporary.identity)
            raise _Failure(Stage.LINK, OPERATION_FAILED) from None
        published = TrackedObject(
            context=plan.context, kind=ObjectKind.PUBLISHED, identity=temporary.identity
        )
        record.objects.append(published)
        self._done(session, record, Stage.LINK)

        # 8. Both names present: one inode, a regular file, link count two, the
        # reviewed owner/group/mode, and the exact bytes through each name.
        self._observe_two_names(session, record, traversal, temporary.identity)
        self._done(session, record, Stage.TWO_NAMES)

        # 9. The temporary, then the published name, each guarded.
        self._guarded_remove(
            session, record, temporary, traversal, plan.temporary, Stage.TEMPORARY_REMOVE
        )
        self._done(session, record, Stage.TEMPORARY_REMOVE)
        try:
            single = _lstat_at(traversal, plan.published)
        except OSError:
            raise _Failure(Stage.PUBLISHED_OBSERVE, OPERATION_FAILED) from None
        if not _same_object(published.identity, single) or single.st_nlink != 1:
            raise _Failure(Stage.PUBLISHED_OBSERVE, OBSERVATION_MISMATCH)
        record.link_count_one = single.st_nlink
        self._done(session, record, Stage.PUBLISHED_OBSERVE)
        self._guarded_remove(
            session, record, published, traversal, plan.published, Stage.PUBLISHED_REMOVE
        )
        self._done(session, record, Stage.PUBLISHED_REMOVE)

        # 10. The containing-directory barrier, then absence of both names.
        try:
            session.inventory.fsync_entry(plan.directory_role)
        except DescriptorRefused:
            raise _Failure(Stage.ENTRY_BARRIER, OPERATION_FAILED) from None
        self._done(session, record, Stage.ENTRY_BARRIER)
        try:
            leftover = [
                _lstat_at(traversal, name) for name in (plan.temporary, plan.published)
            ]
        except OSError:
            raise _Failure(Stage.ABSENCE, OPERATION_FAILED) from None
        if any(facts is not None for facts in leftover):
            raise _Failure(Stage.ABSENCE, OBSERVATION_MISMATCH)
        self._done(session, record, Stage.ABSENCE)

    def _track_published_if_ours(
        self, record: _ContextRecord, traversal: int, identity: str
    ) -> None:
        """After a `linkat` that reported failure, account for its final name.

        The same inode at the final name is ours and is tracked; anything else
        is somebody else's and is left alone; an unobservable name is accounted
        as unidentified.
        """
        plan = record.plan
        try:
            facts = _lstat_at(traversal, plan.published)
        except OSError:
            record.objects.append(
                TrackedObject(
                    context=plan.context,
                    kind=ObjectKind.PUBLISHED,
                    identity="",
                    fate=ObjectFate.UNIDENTIFIED,
                )
            )
            return
        if _same_object(identity, facts):
            record.objects.append(
                TrackedObject(
                    context=plan.context, kind=ObjectKind.PUBLISHED, identity=identity
                )
            )

    def _observe_two_names(
        self, session: _Session, record: _ContextRecord, traversal: int, identity: str
    ) -> None:
        plan = record.plan
        fs = session.filesystem
        stage = Stage.TWO_NAMES
        for name in (plan.temporary, plan.published):
            try:
                facts = _lstat_at(traversal, name)
            except OSError:
                raise _Failure(stage, OPERATION_FAILED) from None
            if not _same_object(identity, facts):
                raise _Failure(stage, OBJECT_IDENTITY_MISMATCH)
            if (
                not stat.S_ISREG(facts.st_mode)
                or facts.st_nlink != 2
                or facts.st_uid != plan.file_uid
                or facts.st_gid != plan.file_gid
                or stat.S_IMODE(facts.st_mode) != plan.file_mode
            ):
                raise _Failure(stage, OBSERVATION_MISMATCH)
            record.link_count_two = facts.st_nlink
        for name in (plan.temporary, plan.published):
            try:
                descriptor = fs.openat(traversal, name, DescriptorMode.O_RDONLY)
            except DescriptorRefused:
                raise _Failure(stage, OPERATION_FAILED) from None
            failure: _Failure | None = None
            try:
                if descriptor.object_id != identity:
                    failure = _Failure(stage, OBJECT_IDENTITY_MISMATCH)
                else:
                    content = fs.read(descriptor.number)
                    if (
                        content != PAYLOAD
                        or hashlib.sha256(content).hexdigest() != PAYLOAD_SHA256
                    ):
                        failure = _Failure(stage, OBSERVATION_MISMATCH)
            except DescriptorRefused:
                failure = _Failure(stage, OPERATION_FAILED)
            released = self._release(session, record, descriptor.number)
            if failure is not None:
                raise failure
            if not released:
                raise _Failure(stage, DESCRIPTOR_NOT_RELEASED)
        record.payload_matched = True

    def _guarded_remove(
        self,
        session: _Session,
        record: _ContextRecord,
        tracked: TrackedObject,
        parent_fd: int,
        name: str,
        stage: Stage,
        *,
        directory_role: str = "",
    ) -> None:
        """Remove one tracked object by name, after an immediately preceding
        identity comparison — and for a directory, an emptiness check.

        A name that no longer resolves to the recorded object is never removed.
        The post-removal observation is an absence check and nothing more
        (r6 §1.4.5): it cannot say which object the removal took.
        """
        try:
            facts = _lstat_at(parent_fd, name)
        except OSError:
            tracked.fate = ObjectFate.REMOVAL_FAILED
            raise _Failure(stage, OPERATION_FAILED) from None
        if facts is None:
            tracked.fate = ObjectFate.VANISHED
            raise _Failure(stage, OBJECT_IDENTITY_MISMATCH)
        if not _same_object(tracked.identity, facts):
            tracked.fate = ObjectFate.REPLACED
            raise _Failure(stage, OBJECT_IDENTITY_MISMATCH)
        if directory_role:
            try:
                contents = session.inventory.listing(directory_role)
            except DescriptorRefused:
                tracked.fate = ObjectFate.REMOVAL_FAILED
                raise _Failure(stage, OPERATION_FAILED) from None
            if contents:
                tracked.fate = ObjectFate.NOT_EMPTY
                raise _Failure(stage, OBSERVATION_MISMATCH)
        try:
            session.filesystem.unlinkat(parent_fd, name, directory=bool(directory_role))
        except DescriptorRefused:
            tracked.fate = ObjectFate.REMOVAL_FAILED
            raise _Failure(stage, OPERATION_FAILED) from None
        try:
            after = _lstat_at(parent_fd, name)
        except OSError:
            tracked.fate = ObjectFate.REMOVAL_UNCONFIRMED
            raise _Failure(stage, OPERATION_FAILED) from None
        if after is not None:
            tracked.fate = ObjectFate.REMOVAL_UNCONFIRMED
            raise _Failure(stage, OBSERVATION_MISMATCH)
        tracked.fate = ObjectFate.REMOVED

    def _remove_canonical(self, session: _Session, record: _ContextRecord) -> None:
        layout = session.layout
        inventory = session.inventory
        root = self._tracked(record, ObjectKind.CANONICAL_ROOT)
        bin_ = self._tracked(record, ObjectKind.CANONICAL_BIN)
        self._guarded_remove(
            session,
            record,
            bin_,
            inventory.traversal(_CANONICAL_ROOT),
            layout.bin_name,
            Stage.BIN_REMOVE,
            directory_role=_CANONICAL_BIN,
        )
        self._done(session, record, Stage.BIN_REMOVE)
        try:
            inventory.fsync_entry(_CANONICAL_ROOT)
        except DescriptorRefused:
            raise _Failure(Stage.BIN_REMOVE_BARRIER, OPERATION_FAILED) from None
        self._done(session, record, Stage.BIN_REMOVE_BARRIER)
        self._guarded_remove(
            session,
            record,
            root,
            inventory.traversal(_STATE_PARENT),
            layout.canonical_root_name,
            Stage.ROOT_REMOVE,
            directory_role=_CANONICAL_ROOT,
        )
        self._done(session, record, Stage.ROOT_REMOVE)
        try:
            inventory.fsync_entry(_STATE_PARENT)
        except DescriptorRefused:
            raise _Failure(Stage.ROOT_REMOVE_BARRIER, OPERATION_FAILED) from None
        self._done(session, record, Stage.ROOT_REMOVE_BARRIER)
        try:
            present = _lstat_at(inventory.traversal(_STATE_PARENT), layout.canonical_root_name)
        except OSError:
            raise _Failure(Stage.ROOT_ABSENCE, OPERATION_FAILED) from None
        if present is not None:
            raise _Failure(Stage.ROOT_ABSENCE, OBSERVATION_MISMATCH)
        self._done(session, record, Stage.ROOT_ABSENCE)

    @staticmethod
    def _tracked(record: _ContextRecord, kind: ObjectKind) -> TrackedObject:
        for tracked in record.objects:
            if tracked.kind is kind:
                return tracked
        raise _Failure(Stage.ROOT_REMOVE, STAGE_UNCLASSIFIED)

    # -- cleanup after a failure ----------------------------------------------

    def _cleanup(self, session: _Session, record: _ContextRecord) -> None:
        """Guarded removal of exactly this context's objects, in reverse order.

        Only objects still `PRESENT` with an established identity are candidates;
        every other fate is already final. Each directory that lost an entry
        receives its containing-entry barrier after its children, and a barrier
        that fails is counted, not retried.
        """
        layout = session.layout
        plan = record.plan
        inventory = session.inventory
        for tracked in reversed(record.objects):
            if tracked.fate is not ObjectFate.PRESENT:
                continue
            if not tracked.identity:
                tracked.fate = ObjectFate.UNIDENTIFIED
                continue
            if tracked.kind in (ObjectKind.TEMPORARY, ObjectKind.PUBLISHED):
                parent_role = plan.directory_role
                name = (
                    plan.temporary
                    if tracked.kind is ObjectKind.TEMPORARY
                    else plan.published
                )
                directory_role = ""
            elif tracked.kind is ObjectKind.CANONICAL_BIN:
                parent_role, name, directory_role = (
                    _CANONICAL_ROOT,
                    layout.bin_name,
                    _CANONICAL_BIN,
                )
            else:
                parent_role, name, directory_role = (
                    _STATE_PARENT,
                    layout.canonical_root_name,
                    _CANONICAL_ROOT,
                )
            try:
                parent_fd = inventory.traversal(parent_role)
            except DescriptorRefused:
                tracked.fate = ObjectFate.REMOVAL_FAILED
                continue
            try:
                self._guarded_remove(
                    session,
                    record,
                    tracked,
                    parent_fd,
                    name,
                    Stage.CLEANUP,
                    directory_role=directory_role,
                )
            except _Failure:
                continue
            try:
                inventory.fsync_entry(parent_role)
            except DescriptorRefused:
                record.cleanup_barrier_failures += 1

    # -- the final survey -----------------------------------------------------

    def _survey(self, session: _Session) -> SurveyResult:
        """Every directory this invocation held, listed once, bounded.

        A verifier name anywhere, or canonical `R` present at the end of a root
        invocation, fails the run. The survey removes nothing.
        """
        layout = session.layout
        inventory = session.inventory
        found = 0
        failed = False
        roles = [
            role
            for role in (_LABORATORY, _RECOVERY, _RUNS)
            if role in inventory.roles()
        ]
        for role in roles:
            try:
                names = inventory.listing(role)
            except DescriptorRefused:
                failed = True
                continue
            if len(names) > SURVEY_LIMIT:
                failed = True
                continue
            found += sum(1 for name in names if name.startswith(NAME_PREFIX))
        root_present = False
        if session.invocation is Invocation.ROOT:
            try:
                root_present = (
                    _lstat_at(
                        inventory.traversal(_STATE_PARENT), layout.canonical_root_name
                    )
                    is not None
                )
            except (OSError, DescriptorRefused):
                failed = True
        return SurveyResult(
            performed=True,
            verifier_names_found=found,
            canonical_root_present=root_present,
            failed=failed,
        )


#: The barriers that make a removal durable. A failure at one of them leaves
#: nothing in the namespace and still needs an operator.
_REMOVAL_BARRIER_STAGES: frozenset[Stage] = frozenset(
    {Stage.ENTRY_BARRIER, Stage.BIN_REMOVE_BARRIER, Stage.ROOT_REMOVE_BARRIER}
)


def final_status(
    contexts: tuple[ContextOutcome, ...], survey: SurveyResult, unreleased: int
) -> Status:
    """**The single point at which accounting becomes an answer.**

    `VERIFIED` needs every context verified, every tracked object removed, no
    cleanup barrier or descriptor failure, and a clean completed survey.
    `FAILED_NO_RESIDUE` is a failure after which every object this invocation
    created was removed, every barrier held, every descriptor was released and
    the survey is clean. Anything else needs an operator.
    """
    clean = (
        survey.performed
        and not survey.failed
        and survey.verifier_names_found == 0
        and not survey.canonical_root_present
        and unreleased == 0
        and all(
            outcome.cleanup_barrier_failures == 0
            and outcome.descriptor_release_failures == 0
            and all(obj.fate is ObjectFate.REMOVED for obj in outcome.objects)
            for outcome in contexts
        )
    )
    if not clean:
        return Status.FAILED_OPERATOR_ATTENTION
    if any(outcome.failed_stage in _REMOVAL_BARRIER_STAGES for outcome in contexts):
        # Every object is gone from the namespace, but the barrier that makes
        # the removal durable did not hold: after a power loss a name could
        # reappear. That is not a clean state to report.
        return Status.FAILED_OPERATOR_ATTENTION
    attempted = [
        outcome for outcome in contexts if outcome.status is not ContextStatus.NOT_ATTEMPTED
    ]
    if contexts and all(outcome.status is ContextStatus.VERIFIED for outcome in contexts):
        return Status.VERIFIED
    if any(
        outcome.status is ContextStatus.FAILED and outcome.failure == OBJECT_EXISTS
        for outcome in attempted
    ):
        # An occupied name was somebody else's object: nothing of ours is left,
        # but an unexplained object is, and an operator must look at it.
        return Status.FAILED_OPERATOR_ATTENTION
    return Status.FAILED_NO_RESIDUE


__all__ = [
    "ADMISSION_REFUSALS",
    "CANONICAL_BIN_MODE",
    "CANONICAL_ROOT_MODE",
    "INVOCATION_CONTEXTS",
    "NAME_PREFIX",
    "NOT_ATTRIBUTION",
    "OBSERVED_CAPABILITIES",
    "PAYLOAD",
    "PAYLOAD_SHA256",
    "SECUREBITS_NOT_OBSERVED",
    "STAGE_FAILURES",
    "CapabilityEvidence",
    "CapabilityMembership",
    "ContextId",
    "ContextOutcome",
    "ContextStatus",
    "HostProbe",
    "I3ControlledWriteVerifier",
    "I3Layout",
    "Invocation",
    "ObjectFate",
    "ObjectKind",
    "ProcHostProbe",
    "ProcessStatus",
    "Stage",
    "Status",
    "SurveyResult",
    "TrackedObject",
    "VerificationRun",
    "capabilities_consistent",
    "classify_capabilities",
    "final_status",
    "i3_layout",
    "mount_matches",
    "name_is_admissible",
    "parse_mountinfo",
    "parse_policy",
    "parse_status",
    "verifier_names",
]
