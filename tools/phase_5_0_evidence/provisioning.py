"""Repository-owned provisioning **definitions** for runner contract r6 §7.

## What this module is, and the sentence that bounds it

r6 §7 lists ten items the reserved laboratory needs and marks every one
**unapproved**. Seven of them are things somebody would *create* — a group, a
membership, a `systemd-tmpfiles` fragment, four directories and one initialized
record. Three are things somebody would *observe* on the target: V6, V8 and V10.

This module writes the seven down **as data a reviewer can read**, so that the
thing being approved or refused is a definition rather than a paragraph. It is
the same discipline the rest of this package applies to argument vectors: the
reviewed artifact is the exact text, pinned, and the tool that would apply it is
a separate decision.

**Nothing here is applied.** There is no function in this module that creates a
group, writes a file, installs a fragment, changes a mode or runs a command, and
`tests/phase_5_0_evidence/test_no_execution.py` asserts that against the source
rather than trusting this sentence. A definition is an input to the maintainer
decision r6 §7 asks for; it is not that decision, and it is not permission to
take it.

**V6, V8 and V10 are not here, and their absence is deliberate.** They are
*unconfirmed target facts* — what exclusive publication's `linkat` needs from
the target's filesystems, whether a directory `fsync` behaves as the
containing-entry barrier there, and whether all seven participants really run as
`ubuntu`. A fact is confirmed by observing the target under a separate
authorization, never by writing a constant. Putting a value here would be
exactly the substitution EH-R16-4 refused in a different costume, so
`UNCONFIRMED_TARGET_FACTS` names them and carries no value.

## Why the layout is data rather than five string constants

Every path below is also what the mechanism opens. `LABORATORY_LAYOUT` is the
production one and it is what a provisioning review approves; a test builds a
layout over a temporary directory and drives the identical code. That is what
keeps the mechanism testable without creating a single object under `/run` or
`/var/lib`, which this authorization does not permit and this module does not
do.

## The shared identity, recorded honestly

Peter's 2026-09-12 direction is that all seven participants use the shared
`ubuntu` identity and that no separate identities are wanted. The modes below
are therefore **accident guards and not barriers between the participants**: all
seven are the same UID and that UID holds passwordless `sudo`, so neither the
record's mode nor the ledger's constrains a participant that chooses to ignore
the protocol. `IDENTITY_NOTE` says that where a reader of the modes will see it,
because a mode table read without it looks like a protection it is not.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .errors import PlanRefused


class ProvisioningKind(str, Enum):
    """What kind of object an item defines. Closed: four kinds, no fifth."""

    GROUP = "group"
    GROUP_MEMBERSHIP = "group_membership"
    DIRECTORY = "directory"
    TMPFILES_FRAGMENT = "tmpfiles_fragment"
    INITIALIZED_RECORD = "initialized_record"


@dataclass(frozen=True, slots=True)
class ProvisioningItem:
    """One r6 §7 item, as the definition a maintainer would approve or refuse.

    `approved` is `False` on every item and there is no constructor argument
    that sets it. The field exists so the answer to *"is this approved?"* is a
    value in the artifact rather than an absence a reader has to interpret, and
    it is not settable here because approval is a maintainer's act recorded in a
    decision register, not a literal an implementer types.
    """

    item_id: str
    kind: ProvisioningKind
    #: The object, exactly: a group name, a path, a fragment's own path.
    subject: str
    owner: str
    group: str
    #: The octal mode, or `-1` where the kind has none (a group, a membership).
    mode: int
    #: Why the contract needs it, in the contract's own terms.
    rationale: str
    #: The contract section that requires it.
    source: str
    #: The exact content a fragment or an initialized record would carry, where
    #: the item has content. Empty for a directory, a group or a membership.
    content: str = ""

    @property
    def approved(self) -> bool:
        """Always `False`. r6 §7 marks every item unapproved and so does this."""
        return False

    def __post_init__(self) -> None:
        for name in ("item_id", "subject", "rationale", "source"):
            if not getattr(self, name).strip():
                raise PlanRefused(f"A provisioning item needs a {name}.")
        if self.kind in (ProvisioningKind.GROUP, ProvisioningKind.GROUP_MEMBERSHIP):
            if self.mode != -1:
                raise PlanRefused(
                    f"{self.item_id} is a {self.kind.value} and carries a file "
                    "mode. A mode on an object that has none is a value nobody "
                    "can check."
                )
        elif self.mode < 0 or self.mode > 0o7777:
            raise PlanRefused(f"{self.item_id} carries no readable file mode.")
        if self.kind in (
            ProvisioningKind.TMPFILES_FRAGMENT,
            ProvisioningKind.INITIALIZED_RECORD,
        ) and not self.content.strip():
            raise PlanRefused(
                f"{self.item_id} defines content and supplies none. A fragment "
                "or a record whose bytes are not stated is not a definition."
            )
        if self.kind in (
            ProvisioningKind.GROUP,
            ProvisioningKind.GROUP_MEMBERSHIP,
            ProvisioningKind.DIRECTORY,
        ) and self.content:
            raise PlanRefused(
                f"{self.item_id} is a {self.kind.value} and carries content."
            )


#: The system group ordinary participants need to open the lock without `sudo`.
LABORATORY_GROUP = "freedomlab"
#: The identity r6 §5.2 records for all seven participants. It is an **[A]** and
#: preflight item V10, not a fact this repository establishes.
PARTICIPANT_IDENTITY = "ubuntu"

#: The `systemd-tmpfiles` fragment's own path, and the two entries it re-creates
#: at every boot. `/run` is a tmpfs, so a one-off `mkdir` would silently stop
#: existing — which is why the lock's directory and inode are a boot-time
#: artifact rather than something a participant creates.
TMPFILES_FRAGMENT_PATH = "/etc/tmpfiles.d/freedom-blades-laboratory.conf"
TMPFILES_FRAGMENT_CONTENT = (
    "d /run/freedom-blades 0750 root freedomlab -\n"
    "f /run/freedom-blades/laboratory.lock 0660 root freedomlab -\n"
)


@dataclass(frozen=True, slots=True)
class LaboratoryLayout:
    """Where the reservation record, the ledger, the lock and the store live.

    The production instance is `LABORATORY_LAYOUT`. A test builds one over a
    temporary directory and drives the same mechanism, which is what lets the
    lifecycle, ledger and recovery paths be exercised without creating a single
    object under `/run` or `/var/lib`.
    """

    #: `/var/lib/freedom-blades/laboratory` — the reservation record's directory.
    laboratory_directory: str
    #: `/var/lib/freedom-blades/laboratory/runs` — the per-run ledger directory.
    runs_directory_name: str
    #: The reservation record's filename inside `laboratory_directory`.
    record_name: str
    #: `/var/lib/freedom-blades/recovery` — the independent store's parent.
    recovery_directory: str
    #: `/run/freedom-blades/laboratory.lock` — the provisioned lock inode.
    lock_path: str

    def __post_init__(self) -> None:
        for name in (
            "laboratory_directory",
            "runs_directory_name",
            "record_name",
            "recovery_directory",
            "lock_path",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise PlanRefused(f"A laboratory layout needs a {name}.")
        for name in ("runs_directory_name", "record_name"):
            value = getattr(self, name)
            if "/" in value or value in (".", ".."):
                raise PlanRefused(
                    f"{name} is one path component, so it cannot reach past the "
                    "descriptor that binds its prefix."
                )


#: The production layout. **It is a definition, not a claim that these paths
#: exist**: V3, V4, V5 and V9 are unapproved and unprovisioned, and every
#: participant refuses on an absent lock or record rather than creating one.
LABORATORY_LAYOUT = LaboratoryLayout(
    laboratory_directory="/var/lib/freedom-blades/laboratory",
    runs_directory_name="runs",
    record_name="lifecycle.json",
    recovery_directory="/var/lib/freedom-blades/recovery",
    lock_path="/run/freedom-blades/laboratory.lock",
)

#: The first-use record's shape, as r6 §5.5 spells it. The attester's name, the
#: basis and the approved target are **the operator's to supply**, so the
#: definition carries the field names and a placeholder rather than values: a
#: first-use attestation this repository wrote would be an attestation nobody
#: made, which is exactly what §5.10 requires the validator to refuse.
FIRST_USE_RECORD_TEMPLATE = (
    "freedom-blades-laboratory-lifecycle\n"
    "schema=2\n"
    "begin-entry\n"
    "sequence=1\n"
    "kind=first_use\n"
    "host=<the host this record is about>\n"
    "target=<the approved target identity>\n"
    "author=<the attester's name and role>\n"
    "at=<the attestation's UTC instant>\n"
    "basis=<what makes prior use excluded, in the attester's own words>\n"
    "end-entry\n"
    "end-history\n"
)


#: The seven r6 §7 items this repository can define. V6, V8 and V10 are absent
#: because they are observations of the target rather than objects to create.
PROVISIONING_ITEMS: tuple[ProvisioningItem, ...] = (
    ProvisioningItem(
        item_id="V1",
        kind=ProvisioningKind.GROUP,
        subject=LABORATORY_GROUP,
        owner="root",
        group="",
        mode=-1,
        rationale=(
            "so ordinary participants can open the cooperative lock without "
            "`sudo`. The lock is opened `O_RDWR` on an existing inode, so what "
            "a participant needs is read and write on the file and search on "
            "its directory — which group membership provides and which no "
            "elevation is required for."
        ),
        source="r6 §7 V1; §5.3",
    ),
    ProvisioningItem(
        item_id="V2",
        kind=ProvisioningKind.GROUP_MEMBERSHIP,
        subject=f"{PARTICIPANT_IDENTITY} in {LABORATORY_GROUP}",
        owner="root",
        group=LABORATORY_GROUP,
        mode=-1,
        rationale=(
            "it is every participant's identity under the 2026-09-12 shared-"
            "identity direction. That all seven really run as this identity is "
            "preflight item V10 and is unconfirmed; this membership is what the "
            "design needs **if** they do, and it is not evidence that they do."
        ),
        source="r6 §7 V2; §5.2",
    ),
    ProvisioningItem(
        item_id="V3",
        kind=ProvisioningKind.TMPFILES_FRAGMENT,
        subject=TMPFILES_FRAGMENT_PATH,
        owner="root",
        group="root",
        mode=0o644,
        rationale=(
            "`/run` is a tmpfs and does not survive reboot, so a one-off "
            "`mkdir` would silently stop existing. The fragment re-creates the "
            "directory and the lock inode at every boot with the stated owner "
            "and mode. The lock is **never created and never unlinked by a "
            "participant**: an absent lock means the host was not provisioned, "
            "and creating one is a provisioning act."
        ),
        source="r6 §7 V3; §5.3",
        content=TMPFILES_FRAGMENT_CONTENT,
    ),
    ProvisioningItem(
        item_id="V4",
        kind=ProvisioningKind.DIRECTORY,
        subject=LABORATORY_LAYOUT.laboratory_directory,
        owner="root",
        group=LABORATORY_GROUP,
        mode=0o750,
        rationale=(
            "the durable reservation record must survive reboot, so it is not "
            "in `/run`. Group read is what lets all seven read it and what lets "
            "any of them re-seal its containing entry; the record itself stays "
            "root-written."
        ),
        source="r6 §7 V4; §5.4",
    ),
    ProvisioningItem(
        item_id="V5",
        kind=ProvisioningKind.DIRECTORY,
        subject=LABORATORY_LAYOUT.recovery_directory,
        owner="root",
        group="root",
        mode=0o700,
        rationale=(
            "the independent recovery store of §2.2. `0700 root:root` is what "
            "makes it unreachable by any experimental identity, including by "
            "descriptor, so a capture's custody does not depend on the "
            "disposable root whose safety is in question."
        ),
        source="r6 §7 V5; §2.2",
    ),
    ProvisioningItem(
        item_id="V7",
        kind=ProvisioningKind.INITIALIZED_RECORD,
        subject=(
            f"{LABORATORY_LAYOUT.laboratory_directory}/"
            f"{LABORATORY_LAYOUT.record_name}"
        ),
        owner="root",
        group=LABORATORY_GROUP,
        mode=0o640,
        rationale=(
            "without a verified-first-use record the fresh-install path has no "
            "reachable successful control: an absent record refuses and "
            "initialization is the only way out of absent. It is created "
            "exclusively and durably, bound to the host **and** the approved "
            "target, on a named operator attestation — and it is created by the "
            "operator provisioning the host, never by the harness and never by "
            "a participant."
        ),
        source="r6 §7 V7; §5.10",
        content=FIRST_USE_RECORD_TEMPLATE,
    ),
    ProvisioningItem(
        item_id="V9",
        kind=ProvisioningKind.DIRECTORY,
        subject=(
            f"{LABORATORY_LAYOUT.laboratory_directory}/"
            f"{LABORATORY_LAYOUT.runs_directory_name}"
        ),
        owner="root",
        group=LABORATORY_GROUP,
        mode=0o3770,
        rationale=(
            "every participant must be able to publish its own in-progress and "
            "completion state, and the reservation record must not become "
            "group-writable to allow it. Setgid makes each run entry "
            "group-owned so every participant can read it; sticky means only an "
            "entry's owner may remove or rename it."
        ),
        source="r6 §7 V9; §5.11",
    ),
)

#: The three r6 §7 items this repository **cannot** define, and why. Each is an
#: observation of the target, and each stays unconfirmed.
UNCONFIRMED_TARGET_FACTS: tuple[tuple[str, str], ...] = (
    (
        "V6",
        "what exclusive publication's `linkat` needs from the target, observed "
        "read-only: the filesystem type under each directory that holds an "
        "exclusive publication, and the value of `fs.protected_hardlinks`. "
        "Re-scoped by r6 amendment D1 from `RENAME_NOREPLACE`, which no "
        "publication uses — see "
        "`execution.descriptors.EXCLUSIVE_PUBLICATION_SUBSTITUTE`. The fact "
        "remains unconfirmed and this definition does not close it.",
    ),
    (
        "V8",
        "whether `fsync` on an `O_RDONLY` directory descriptor behaves as the "
        "containing-entry barrier on the target's filesystem. Every barrier in "
        "§§2.3, 2.4, 5.6 and 5.12 rests on it, for all seven participants.",
    ),
    (
        "V10",
        "whether all seven participants really run as `ubuntu`. The ledger's "
        "whole attribution rests on it, and the shared-identity design choice "
        "is a decision about what is wanted rather than an observation of what "
        "is.",
    ),
)

#: Where a reader of the mode table will see it.
IDENTITY_NOTE = (
    "All seven participants are intended to run as the same OS user, and that "
    "user holds passwordless `sudo`. Neither the record's mode nor the "
    "ledger's constrains a participant that chooses to ignore the protocol.",
    "The modes prevent accidental and misdirected writes, and they are a guard "
    "against a future identity split and against an unrelated user. They are "
    "not a barrier between the participants and are not relied on as one.",
    "Separating the seven identities would be a real barrier. It is a "
    "permission decision nobody has taken; the maintainer chose not to take it "
    "on 2026-09-12, and that choice is recorded rather than re-argued here.",
)

#: Stated once, at the top of anything that renders these definitions.
NOT_APPLIED = (
    "Every item above is a **definition for review**. None is applied, and "
    "nothing in this module applies one: it creates no group, writes no file, "
    "installs no fragment, changes no mode and runs no command.",
    "r6 §7 marks all ten items unapproved. The 2026-09-12 direction accepts the "
    "ten-item set as the **design basis** and explicitly does not authorize "
    "applying any of them.",
    "Approval is a maintainer's act recorded in the decision register. A "
    "definition in a repository is an input to it.",
)


def items_by_id() -> dict[str, ProvisioningItem]:
    """The definitions, keyed. A convenience for a reviewer, and no more."""
    return {item.item_id: item for item in PROVISIONING_ITEMS}


def defined_item_ids() -> tuple[str, ...]:
    return tuple(item.item_id for item in PROVISIONING_ITEMS)


def unconfirmed_fact_ids() -> tuple[str, ...]:
    return tuple(identifier for identifier, _why in UNCONFIRMED_TARGET_FACTS)


__all__ = [
    "FIRST_USE_RECORD_TEMPLATE",
    "IDENTITY_NOTE",
    "LABORATORY_GROUP",
    "LABORATORY_LAYOUT",
    "LaboratoryLayout",
    "NOT_APPLIED",
    "PARTICIPANT_IDENTITY",
    "PROVISIONING_ITEMS",
    "ProvisioningItem",
    "ProvisioningKind",
    "TMPFILES_FRAGMENT_CONTENT",
    "TMPFILES_FRAGMENT_PATH",
    "UNCONFIRMED_TARGET_FACTS",
    "defined_item_ids",
    "items_by_id",
    "unconfirmed_fact_ids",
]
