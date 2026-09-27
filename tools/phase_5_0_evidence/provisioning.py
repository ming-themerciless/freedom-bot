"""Repository-owned provisioning **definitions** for runner contract r6 §7.

## What this module is, and the sentence that bounds it

r6 §7 lists **eleven** items the reserved laboratory needs. **Eight** of them are
things somebody would *create* — a group, a membership, a `systemd-tmpfiles`
fragment, **four** directories and one initialized record. Three are things
somebody would *observe* on the target: V6, V8 and V10.

**The eighth creatable item is V12 — C-P5.0-LAB-V6-D, 2026-09-17.** It defines
the persistent `/var/lib/freedom-blades` parent before V4 and V5. The maintainer
withdrew V11 and `/opt/freedom-blades/evidence`; the sole canonical disposable
run root `R` is the already approved `/var/lib/fb-evidence-p5-0`. That run root
is created by the reviewed plan, not by prerequisite provisioning. The
production `EVIDENCE_ROLE` remains deliberately unregistered until its real
consumer receives separate implementation and review authority.

This module writes the eight down **as data a reviewer can read**, so that the
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

**The mechanism that would apply the directory items is a different module.**
`execution/provisioner.py` is in the execution tier because it creates
directories; it takes every path and every identity as an argument, it applies
only the directory items of `RELEASED_PREREQUISITE_SUBSET`, and it refuses V7
by name. This module stays data so that the reviewed definition and the thing
that would act on it are two files a reviewer can read apart.

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

from .approved_target import APPROVED_TARGET
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
    #: **How the object comes into existence, exactly.** The syscalls or the
    #: command, in order. Required of every item — C-P5.0-LAB-V6-R1: an item
    #: whose creation mechanism is not stated is an item whose applier chooses
    #: one, and `/opt/freedom-blades/evidence` was exactly that.
    creation: str = ""
    #: **What a reboot does to it.** A `/run` object is re-created by the
    #: `systemd-tmpfiles` fragment; an object on the root filesystem survives.
    #: Required, because *"it exists"* and *"it exists after a reboot"* are two
    #: different facts and only one of them is a provisioning property.
    persistence: str = ""
    #: **The read-only observation that confirms it**, and nothing wider. It is
    #: what the post-provision V6 re-observation performs for this item.
    verification: str = ""
    #: **How it is reversed**, exactly, and what the reversal refuses to touch.
    rollback: str = ""
    #: The exact content a fragment or an initialized record would carry, where
    #: the item has content. Empty for a directory, a group or a membership.
    content: str = ""

    @property
    def approved(self) -> bool:
        """Always `False`. r6 §7 marks every item unapproved and so does this."""
        return False

    def __post_init__(self) -> None:
        for name in (
            "item_id",
            "subject",
            "rationale",
            "source",
            "creation",
            "persistence",
            "verification",
            "rollback",
        ):
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


#: The sole canonical disposable evidence root approved by the maintainer.
#: Prerequisite provisioning does not create it; the reviewed concrete plan does.
#:
#: **It is read from the approved target rather than restated** — C-P5.0-LAB-V6-D
#: review. The maintainer's disposition is that `R` *is* the approved target's
#: root, so a second literal here would be a second place for that one value to
#: be changed, and the way the two stop agreeing. Same reason as
#: `delta_item_count()`.
EVIDENCE_ROOT = APPROVED_TARGET.root_path

#: Persistent parent for the reservation record and independent recovery store.
STATE_ROOT = "/var/lib/freedom-blades"


#: The eight r6 §7 items this repository can define. V6, V8 and V10 are absent
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
        creation=(
            "`groupadd --system freedomlab`, as root, out of band. It is an "
            "operator step: this repository creates no group, and "
            "`execution/provisioner.py` applies directory items only."
        ),
        persistence=(
            "`/etc/group` is on the root filesystem, so the group survives "
            "reboot. Nothing re-creates it and nothing needs to."
        ),
        verification=(
            "`getent group freedomlab` resolves to exactly one entry, and the "
            "gid it reports is the gid every group-owned item below is verified "
            "against. Read-only."
        ),
        rollback=(
            "`groupdel freedomlab`, after V2's membership is removed and after "
            "every object group-owned by it has been removed or re-owned. A "
            "group deleted while an object still carries its gid leaves an "
            "object owned by a number that resolves to no name, which the "
            "verification refuses rather than reads past."
        ),
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
        creation=(
            "`usermod --append --groups freedomlab ubuntu`, as root, out of "
            "band. `--append` is load-bearing: the plain `--groups` form "
            "**replaces** the supplementary set, and V6 observed `ubuntu` in "
            "`adm`, `cdrom`, `sudo`, `dip` and `lxd` — so the plain form would "
            "silently remove `sudo` from the identity the whole design runs as."
        ),
        persistence=(
            "`/etc/group` survives reboot, but an **already running** session "
            "keeps the supplementary set it was created with. The membership "
            "takes effect for a participant started after it, which is why the "
            "verification reads the participant's own process credentials and "
            "not only the account database."
        ),
        verification=(
            "the account database lists `freedomlab` for `ubuntu` **and** still "
            "lists the five groups V6 observed, and a participant's own "
            "`/proc/self/status` `Groups:` line carries the gid V1 resolves to. "
            "Read-only. It confirms the membership; it does not confirm V10."
        ),
        rollback=(
            "`gpasswd --delete ubuntu freedomlab`. It removes one membership "
            "and touches no other group, which is the reversal of the "
            "`--append` above rather than of a set assignment."
        ),
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
        creation=(
            "write `TMPFILES_FRAGMENT_CONTENT` to the fragment path as root, "
            "`0644 root:root`, then create the two entries it describes from "
            "that one fragment. An operator step: this repository writes "
            "nothing under `/etc` and creates nothing under `/run`."
        ),
        persistence=(
            "the fragment itself is on the root filesystem and survives; the "
            "two objects it describes are on tmpfs and are **re-created at "
            "every boot** from it. This is the one item whose objects are "
            "expected to be absent before the boot that follows it."
        ),
        verification=(
            "read the fragment's bytes back and compare them with "
            "`TMPFILES_FRAGMENT_CONTENT` exactly; then `/run/freedom-blades` is "
            "a directory `0750 root:freedomlab` and "
            "`/run/freedom-blades/laboratory.lock` a regular file "
            "`0660 root:freedomlab`. Read-only, and it takes no lock."
        ),
        rollback=(
            "remove the fragment, then remove the two `/run` entries, in that "
            "order — the reverse order re-creates them at the next boot. The "
            "removal refuses while any participant holds the lock: releasing "
            "another participant's `flock` by unlinking its inode is exactly "
            "the takeover r6 §5.3 forbids."
        ),
        content=TMPFILES_FRAGMENT_CONTENT,
    ),
    ProvisioningItem(
        item_id="V12",
        kind=ProvisioningKind.DIRECTORY,
        subject=STATE_ROOT,
        owner="root",
        group="root",
        mode=0o755,
        rationale=(
            "the persistent parent of V4's laboratory directory and V5's "
            "independent recovery directory. V6 observed it absent; defining "
            "it explicitly prevents either child applier from inventing an "
            "implicit parent. It is not the disposable evidence root `R`."
        ),
        source="r6 §7 V12; §2.2; §5.4; C-P5.0-LAB-V6-D",
        creation=(
            "as root, before V4 and V5, using the same exclusive `mkdirat`, "
            "descriptor `fchown`/`fchmod`, read-back and parent-barrier sequence "
            "as every directory item. `EEXIST` is verified, never adopted."
        ),
        persistence=(
            "under `/var/lib` on the root filesystem, so it survives reboot; "
            "no `systemd-tmpfiles` rule recreates it."
        ),
        verification=(
            "read-only and without following a symbolic link: a directory, "
            "`root:root`, `0755`, containing only the reviewed `laboratory` "
            "and `recovery` children when they exist."
        ),
        rollback=(
            "non-recursive `rmdir` after V9, V4 and V5 have been removed, only "
            "while empty and only after the recorded `(st_dev, st_ino)` matches."
        ),
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
        creation=(
            "as root, out of band, by the same exclusive `mkdirat` plus "
            "descriptor `fchown`/`fchmod` plus parent-barrier sequence, after "
            "V12 has created and verified `/var/lib/freedom-blades`."
        ),
        persistence=(
            "`/var/lib` is on the same ext4 root filesystem V6 observed, so it "
            "survives reboot. That is the property that makes it, and not "
            "`/run`, the reservation record's home."
        ),
        verification=(
            "read-only: a directory, `root:freedomlab`, `0750`, holding at most "
            "`runs` and `lifecycle.json`. Group read and search are what the "
            "re-seal needs; that a participant holding only those can really "
            "`fsync` the entry is implementation check **I8** and is not "
            "confirmed by observing a mode."
        ),
        rollback=(
            "non-recursive `rmdir`, after V9 and after V7's record are gone, on "
            "the same recorded-identity guard. It refuses while the reservation "
            "record exists: removing the directory out from under a record is "
            "how a used host loses the history that refuses reuse."
        ),
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
        creation=(
            "as root, out of band, **after V4**, by the same sequence. The "
            "setgid and sticky bits are applied by the `fchmod` on the held "
            "descriptor rather than by the `mkdirat` mode argument, because "
            "`mkdir(2)` masks its mode with the umask and a set-group-ID bit "
            "set through a mode argument is not a bit a reviewer can predict."
        ),
        persistence=(
            "as V4: on the root filesystem, surviving reboot. A ledger that did "
            "not survive would make every restart an empty accounting, and r6 "
            "§5.9 refuses an absent ledger precisely so that cannot read as "
            "nothing having been outstanding."
        ),
        verification=(
            "read-only: a directory, `root:freedomlab`, `st_mode & 0o7777 == "
            "0o3770` — both the setgid and the sticky bit, checked as bits and "
            "not as a rendered string — and no run file inside it on a freshly "
            "provisioned host."
        ),
        rollback=(
            "non-recursive `rmdir`, **before** V4's, on the same guard, and "
            "only while it holds no run file. A run file inside it is an "
            "unsettled or unrecovered run and is the operator's to account for "
            "under r6 §5.11 before anything is removed."
        ),
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
        creation=(
            "as root, out of band, by the same sequence. Its parent "
            "`/var/lib/freedom-blades` is the reviewed V12 item and must be "
            "created and verified first."
        ),
        persistence=(
            "on the root filesystem, surviving reboot — which is the whole "
            "point of an *independent* store: a restarted executor and a human "
            "both have to be able to find it after a power loss."
        ),
        verification=(
            "read-only: a directory, `root:root`, `0700`, and its per-run "
            "children — where any exist — `root:root 0700` with `0400` capture "
            "and record files. The absence of any group or other bit is the "
            "property §2.2 rests on, and it is checked as bits."
        ),
        rollback=(
            "non-recursive `rmdir` on the same guard, and only while it is "
            "empty. A recovery basis inside it is the only copy of a "
            "pre-mutation configuration; §2.5's disposal is an operator "
            "decision per run id and is never part of reversing provisioning."
        ),
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
        creation=(
            "§5.10's exclusive publication: `O_CREAT|O_EXCL` on the temporary, "
            "the bytes written and synchronized, then `linkat` of the final "
            "name, `unlinkat` of the temporary and the containing entry's "
            "barrier. **It is excluded from this release** — `V7_EXCLUSION` — "
            "because that `linkat` is the first real exclusive publication on "
            "the target and I3 is unconfirmed."
        ),
        persistence=(
            "on the root filesystem under V4, surviving reboot. Visibility and "
            "durability are different: a record that reached its final name "
            "without its directory barrier is readable and would not survive a "
            "power loss, which is R3-1 and why §5.6 makes the next reader "
            "re-seal it."
        ),
        verification=(
            "read-only: a regular file, `root:freedomlab`, `0640`, "
            "`st_nlink == 1`, **no `lifecycle.json.tmp` beside it**, and bytes "
            "that parse under §5.5's bounded schema to exactly one `first_use` "
            "entry bound to this host and the approved target. **While V7 is "
            "excluded the expected observation is that the file is absent**, "
            "and that absence is the fail-closed state `V7_EXCLUSION` names."
        ),
        rollback=(
            "there is none, and that is the contract rather than an omission. "
            "§5.10's `prior_use_not_excluded` says a used host is **never "
            "reinitialized**: the record is the only evidence that no earlier "
            "run is outstanding, so removing it to start again destroys that "
            "evidence. The reversal of a wrong first-use record is an "
            "attributed operator recovery appended to it, or a rebuilt host."
        ),
        content=FIRST_USE_RECORD_TEMPLATE,
    ),
)


#: The prior V11 parent and location conflicts were resolved by the maintainer's
#: 2026-09-17 disposition. V12 is now the explicit persistent parent.
EVIDENCE_ROOT_TRACE: tuple[str, ...] = (
    "`R` is `/var/lib/fb-evidence-p5-0`, the approved target root, and is "
    "created by the reviewed concrete plan rather than prerequisite provisioning.",
    "Decision B's one narrow exception, C-P5.0-LAB-I3-D1: the separately armed "
    "I3 controlled-write verifier may temporarily create `R` (`root:root 0700`) "
    "and `R/bin` (`root:root 0755`) solely for I3, and removes both through "
    "identity comparisons before it may report success. It is not prerequisite "
    "provisioning and creates no general second creator of `R`.",
    "V11 and `/opt/freedom-blades/evidence` are withdrawn; no ownership change "
    "to `/opt/freedom-blades` is required or authorized.",
    "`EVIDENCE_ROLE` remains unregistered until a separately reviewed real "
    "production participant consumes it.",
)
PREREQUISITE_PARENTS: tuple[tuple[str, str, str], ...] = ()
UNRECONCILED_CONTRACT_DISCREPANCIES: tuple[tuple[str, str], ...] = ()

#: **The prerequisite subset Peter approved on 2026-09-17**, in the order it
#: would be applied. `approved` on each item stays `False`: approval is a
#: maintainer act recorded in the decision register, the approval is
#: conditioned on independent Codex technical and security acceptance of this
#: remediation, and a literal in a repository is not that record.
#:
#: The order is parent-before-child and identity-before-object: the group must
#: resolve before anything group-owned is created, V4 must exist before its
#: `runs` child, and V12 must precede both of its children.
RELEASED_PREREQUISITE_SUBSET: tuple[str, ...] = (
    "V1",
    "V2",
    "V3",
    "V12",
    "V4",
    "V9",
    "V5",
)

#: The subset `execution/provisioner.py` itself applies: the directory items,
#: and only those. V1 and V2 are account-database changes, V3 writes under
#: `/etc` and creates objects on tmpfs, and this repository does neither.
APPLIED_DIRECTORY_ITEMS: tuple[str, ...] = ("V12", "V4", "V9", "V5")

#: **V7 is excluded from this provisioning release, and this is the stop
#: condition that keeps the resulting host fail-closed.**
V7_EXCLUSION: tuple[str, ...] = (
    "**What is excluded.** V7 — the initialized `lifecycle.json` — is not "
    "applied by this release and is not applied by "
    "`execution/provisioner.py`, which refuses it by name. Nothing in this "
    "repository initializes the reservation record.",
    "**Why.** §5.10's first use is an exclusive publication: bytes, `fsync`, "
    "`linkat` of the final name, `unlinkat` of the temporary, directory "
    "barrier. That `linkat` is the **first real exclusive publication on the "
    "target**, and whether it succeeds there is implementation check **I3**. "
    "The released V6 survey observed the prerequisites — ext4 on both future "
    "location families, `fs.protected_hardlinks=1` — and explicitly does not "
    "close I3; a controlled write verification requires separate authorization "
    "before execution. Initializing the record would perform that verification "
    "under another name.",
    "**The stop condition, and what an absent record leaves.** With V1–V5, V9 "
    "and V12 applied and V7 absent, the host is provisioned and **closed**. "
    "r6 §5.9's *record absent or unreadable* refuses, and it refuses **all "
    "seven participants**: `lifecycle_storage.read_and_admit` is the one "
    "admission path, `host_lock.LaboratorySession.admit` is the only caller, "
    "and `execution/participants.py` returns before any participant's work is "
    "called. §5.10 states that initialization is the only way out of absent, "
    "and that it is the operator's act, out of band, on a named attestation — "
    "never the harness's and never a participant's. So the absence is not a "
    "gap the next run fills: it is the fail-closed state, and it stays until "
    "V7 receives its own release.",
    "**What may not be inferred from a successful provisioning.** That the "
    "directories exist says nothing about I3, nothing about V8's directory "
    "barrier, nothing about V10's identity and nothing about `plan."
    "is_executable`, which stays `False` with `reservation."
    "REAL_EXECUTION_REFUSAL` unconditional. A provisioned host is a host on "
    "which the refusals can finally be reached honestly, not a host that may "
    "run anything.",
)

#: **The read-only post-provision verification — r6 §7's V6, re-observed.**
#:
#: One ordered procedure, every step read-only. It creates no link, takes no
#: lock, writes nothing and runs no controlled write verification, so it
#: **cannot** close I3 and does not claim to. Each row is `(what, how, what it
#: establishes, what it does not)`.
VERIFICATION_PROCEDURE: tuple[tuple[str, str, str, str], ...] = (
    (
        "the execution identity",
        "read the observing process's own `/proc/self/status` `Uid:`, `Gid:` "
        "and `Groups:` lines, and resolve each gid through the account "
        "database.",
        "which identity performed this observation, and which supplementary "
        "groups it actually holds — which is what V2's membership has to be "
        "confirmed against, because an already running session keeps the set it "
        "started with.",
        "it does not confirm **V10**. One process's identity is not evidence "
        "about the other six participants, and this procedure surveys one.",
    ),
    (
        "the capability state",
        "read the same file's `CapInh`, `CapPrm`, `CapEff`, `CapBnd` and "
        "`CapAmb` masks, and `NoNewPrivs`.",
        "whether the observing identity holds any capability, as capability "
        "evidence recorded beside the hard-link policy. No publication in this "
        "design depends on a capability: under C-P5.0-LAB-I3-D1 every exclusive "
        "publication, P2 included, relies on the filesystem-UID owner "
        "condition.",
        "a mask read under `ubuntu` says nothing about a root process's mask, "
        "and `CapBnd` is never evidence of `CapEff`. P2's actual operation-time "
        "masks are observed by the I3 controlled-write verifier in its own "
        "root invocation, as evidence and not as attribution.",
    ),
    (
        "the hard-link policy",
        "read `/proc/sys/fs/protected_hardlinks`.",
        "which branch of `proc_sys_fs(5)` applies to every exclusive "
        "publication on this host.",
        "**it creates no link.** A policy value is a precondition, not a "
        "successful `linkat`. **I3 stays unconfirmed.**",
    ),
    (
        "the mount and filesystem identity",
        "for each provisioned directory, read the filesystem type and the "
        "mount point its path resolves through, without following a symbolic "
        "link.",
        "that the object is on the filesystem the durability and hard-link "
        "arguments were made about, and that it did not land on a tmpfs or a "
        "separate mount somebody added.",
        "a filesystem type is not a `fsync` semantic. Whether a directory "
        "`fsync` is the containing-entry barrier there is **V8/I2**, and it is "
        "unperformed.",
    ),
    (
        "each item's exact type, owner, group and mode",
        "`fstatat(<parent>, <name>, AT_SYMLINK_NOFOLLOW)` and compare "
        "`S_ISDIR`, `st_uid`, `st_gid` and `st_mode & 0o7777` with the item's "
        "own values — `verify()` in `execution/provisioner.py` is exactly this "
        "comparison, and it reads the values from `PROVISIONING_ITEMS` rather "
        "than restating them.",
        "that each object is the object the reviewed item defines, bit for "
        "bit, including V9's setgid and sticky bits.",
        "it establishes nothing about what may reach the object **through its "
        "parent**, which is the next row and the one V6 could not confirm.",
    ),
    (
        "each item's parent",
        "`fstat` the parent and read `st_uid` and `st_mode & 0o022`.",
        "whether the entry itself is root-only. A directory `0700 root:root` "
        "under a parent an ordinary identity may write is not a root-only "
        "object: the parent's write permission governs renaming and unlinking "
        "the entry.",
        "nothing about the object's contents, and nothing about a replacement "
        "that happens after the observation. r6 §1.4.1 concedes that detection "
        "is all a later `fstatat` can offer.",
    ),
    (
        "the group and its membership",
        "resolve `freedomlab` in the account database to exactly one gid, and "
        "confirm that gid is the `st_gid` every group-owned item carries and "
        "that `ubuntu` is listed in it.",
        "V1 and V2, and that no group-owned object carries a gid that resolves "
        "to no name.",
        "it does not confirm that a participant holding only group read and "
        "search can `fsync` the entry. That is **I8**, and §5.6 rests on it.",
    ),
    (
        "V7's absence",
        "`fstatat` `lifecycle.json` and `lifecycle.json.tmp` under V4 and "
        "expect **both absent**.",
        "that the release stopped where `V7_EXCLUSION` says it stops, and that "
        "the host is in the fail-closed state r6 §5.9 refuses on.",
        "a present record would not be a success here — it would be an "
        "unattributed initialization, and §5.10's `prior_use_not_excluded` "
        "makes that a stop rather than a state to read.",
    ),
)

#: The three r6 §7 items this repository **cannot** define, and why. Each is an
#: observation of the target, and each stays unconfirmed.
UNCONFIRMED_TARGET_FACTS: tuple[tuple[str, str], ...] = (
    (
        "V6",
        "a **read-only prerequisite survey** of what exclusive publication's "
        "`linkat` needs from the target — Peter's disposition of 2026-09-15, on "
        "Codex's recommendation. It may record the filesystem and mount type "
        "under each directory that holds an exclusive publication, the value of "
        "`fs.protected_hardlinks`, the execution identity, the file ownership "
        "and mode assumptions, and the relevant capability state. It creates no "
        "link: a write probe is not read-only and is not part of V6. **It does "
        "not prove that the real `linkat` publication succeeds and it does not "
        "close I3.** A controlled write verification requires separate "
        "authorization before execution. Re-scoped by r6 amendment D1 from "
        "`RENAME_NOREPLACE`, which no publication uses — see "
        "`execution.descriptors.EXCLUSIVE_PUBLICATION_SUBSTITUTE`. **Performed "
        "on 2026-09-16 and not closed:** the survey found both future location "
        "families on the same ext4 root mount and `fs.protected_hardlinks=1`, "
        "and found every exact publication directory and the `freedomlab` group "
        "**absent**, so their required ownership and mode assumptions could not "
        "be confirmed on the target. It remains performed-but-not-closed until "
        "the accepted provisioning is applied and the read-only survey is "
        "repeated — `VERIFICATION_PROCEDURE` is that repetition. The fact "
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
    "r6 §7 marks all eleven items unapproved and the `approved` property above "
    "returns `False` for every one. The 2026-09-12 direction accepts the set as "
    "the **design basis** and explicitly does not authorize applying any of "
    "them.",
    "**Peter approved a prerequisite subset on 2026-09-16 and revised it on "
    "2026-09-17** — `RELEASED_PREREQUISITE_SUBSET` is the revised one: "
    "C-P5.0-LAB-V6-D withdrew V11 and put V12 before V4 and V5, and V7 stays "
    "excluded from both. That approval is conditioned on independent Codex "
    "technical and security acceptance of this remediation, and it did not "
    "reach this pass as authority to apply anything: C-P5.0-LAB-V6-D is "
    "repository-local, and no object was created on any host.",
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


def delta_item_count() -> int:
    """Every r6 §7 item, defined or observed. **The number is derived.**

    It is a function rather than a literal because the count is stated in a
    contract, in two review artifacts and in three test modules, and a literal
    is how six copies of a number stop agreeing. `PROVISIONING_ITEMS` and
    `UNCONFIRMED_TARGET_FACTS` are the two halves and there is no third.
    """
    return len(PROVISIONING_ITEMS) + len(UNCONFIRMED_TARGET_FACTS)


def released_items() -> tuple[ProvisioningItem, ...]:
    """The approved prerequisite subset, in application order.

    Reads `RELEASED_PREREQUISITE_SUBSET` against the definitions, so an id in
    the subset that names no item is a failure here rather than an omission at
    the point somebody tries to apply it.
    """
    known = items_by_id()
    return tuple(known[identifier] for identifier in RELEASED_PREREQUISITE_SUBSET)


def excluded_item_ids() -> tuple[str, ...]:
    """Defined items this release does **not** apply. Today: V7, and only V7."""
    return tuple(
        item.item_id
        for item in PROVISIONING_ITEMS
        if item.item_id not in RELEASED_PREREQUISITE_SUBSET
    )


__all__ = [
    "APPLIED_DIRECTORY_ITEMS",
    "EVIDENCE_ROOT",
    "EVIDENCE_ROOT_TRACE",
    "FIRST_USE_RECORD_TEMPLATE",
    "IDENTITY_NOTE",
    "LABORATORY_GROUP",
    "LABORATORY_LAYOUT",
    "LaboratoryLayout",
    "NOT_APPLIED",
    "PARTICIPANT_IDENTITY",
    "PREREQUISITE_PARENTS",
    "PROVISIONING_ITEMS",
    "ProvisioningItem",
    "ProvisioningKind",
    "RELEASED_PREREQUISITE_SUBSET",
    "STATE_ROOT",
    "TMPFILES_FRAGMENT_CONTENT",
    "TMPFILES_FRAGMENT_PATH",
    "UNCONFIRMED_TARGET_FACTS",
    "UNRECONCILED_CONTRACT_DISCREPANCIES",
    "V7_EXCLUSION",
    "VERIFICATION_PROCEDURE",
    "defined_item_ids",
    "delta_item_count",
    "excluded_item_ids",
    "items_by_id",
    "released_items",
    "unconfirmed_fact_ids",
]
