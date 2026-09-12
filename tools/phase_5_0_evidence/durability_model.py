"""A bounded synthetic model of the proposed runner's **durability and removal**
rules — findings **PR-20260911-R2-2** and **PR-20260911-R2-3**.

## What this is, said before anything else

It is a **model of a proposal**, and it is nothing else. Revision 3 of the runner
contract specifies a descriptor design, a barrier graph and a removal procedure
that **are not built**: no privileged mechanism, no filesystem writer, no lock
adapter and no operational integration exists, and this module creates none of
them. What it provides is a deterministic in-memory arrangement in which those
rules can be *stated precisely enough to be falsified*, and a place to inject a
failure at every barrier the contract names.

`MODEL_LIMITS` carries that in every result, and the distinction it rests on is
the same one `feasibility` draws:

* a model can establish that a rule is **constructible and falsifiable** — that
  the ordering has a meaning, that omitting a barrier is detectable, and that a
  deliberately defective sequence really is classified as failing; and
* a model cannot establish **Linux runtime behaviour**. Nothing here observes a
  real descriptor mode, a real filesystem, a real `fsync` or a real crash. The
  implementation checks that would are enumerated in
  `IMPLEMENTATION_CHECKS_NOT_PERFORMED` and **none of them has been performed**.

## The three things it models

**1. Descriptor modes, because R2-2 is a descriptor mistake.** Revision 2 opened
the whole directory chain with `O_PATH` and then required `fsync(bin_fd)` and
`fsync(pgconf_fd)`. `open(2)` enumerates what an `O_PATH` descriptor may be used
for, and synchronizing it is not among them. So the proposed normal installation
failed at its own directory durability barrier, and restoration failed the same
way after it had already replaced a destination. `DescriptorMode` is therefore an
explicit value on every descriptor here, and `SyntheticFilesystem.fsync` refuses
an `O_PATH` descriptor — which is the invalid-operation control the corrected
design has to survive.

**2. Volatile and durable state, held apart.** A barrier is only meaningful if
something is lost without it. So the model carries two namespaces and two data
maps: what a reader sees now, and what would survive a power loss.
`SyntheticFilesystem.crash()` discards the first and keeps the second. A
directory entry becomes durable when its **containing directory** is
synchronized; a file's bytes become durable when **that file** is synchronized.
Those are two different barriers on two different objects, and revision 2's
omitted recovery-parent synchronization is exactly the case where doing the
second is mistaken for doing the first.

**3. Names and objects, held apart — R2-3.** `unlink(2)` removes a *name*, and a
post-check can observe only whether a name resolves. It cannot observe which
object the removal took. The model therefore tracks objects by identity and the
namespace separately, so a test can assert the thing the production observation
actually learns (a name is absent) without borrowing the thing only the test
oracle knows (which object went).

## Isolation

Planning tier. No process, no file, no socket, no database, no product import.
Every "filesystem" here is a dictionary, every "descriptor" is an integer into a
table this module owns, and `crash()` is an assignment.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from .errors import PlanRefused

#: What this module's results are not, carried in every one of them.
MODEL_LIMITS = (
    "These are proposal-model results. The mechanism they model is not built, "
    "not accepted and not implemented, and nothing here is evidence for "
    "EH-R16-1 or for any package requirement.",
    "No Linux syscall was invoked, no real descriptor was opened in any mode, no "
    "filesystem was written and no crash occurred. A passing row establishes "
    "that the proposed rule is constructible and falsifiable, and nothing about "
    "the behaviour of the target.",
    "The documented semantics the model imitates are cited from the primary "
    "manual pages in the runner contract. Where the model and a manual page "
    "would disagree, the manual page is right and the disagreement is a defect "
    "in this module.",
)

#: The checks that would establish the real property, kept separate from the
#: model so the two are never read as one. **None has been performed**, and
#: performing any of them needs authorization this pass does not hold.
IMPLEMENTATION_CHECKS_NOT_PERFORMED = (
    "That an `O_PATH` descriptor really refuses `fsync` with EBADF on the target "
    "kernel, and that the separately opened O_RDONLY directory descriptor really "
    "accepts it.",
    "That the target filesystem implements `fsync` on a directory as the "
    "containing-entry barrier the design relies on, and that it supports "
    "`RENAME_NOREPLACE` — one of the twelve unconfirmed target facts.",
    "That a real power loss after a successful capture publication leaves the "
    "recovery parent listing the run directory, and the run directory listing a "
    "verifiable copy and record.",
    "That a real restoration interrupted between the rename and the directory "
    "synchronization leaves the destination at its previous content.",
    "Every one of these belongs to the eventual implementation review and the "
    "separately authorized target work. None is performed here.",
)


class ModelRefused(PlanRefused):
    """The model refused an operation, naming the documented reason it would fail.

    It is a `PlanRefused` so a caller that catches the package's refusals catches
    this one too, and a distinct class so a test can assert that the refusal came
    from the modelled rule rather than from a mistake in the test's arrangement.
    """


class DescriptorMode(str, Enum):
    """The open modes the contract distinguishes, because R2-2 turns on them."""

    #: Obtained with `O_PATH`. `open(2)` permits it as the `dirfd` argument of the
    #: `*at()` calls, as an `fstat`/`fstatfs` subject, for `close`, `fchdir`,
    #: duplication, descriptor-flag operations and `SCM_RIGHTS`. It permits
    #: neither reading nor writing nor `ioctl`, and **it is not a synchronizable
    #: descriptor**.
    O_PATH = "O_PATH"
    #: A real read descriptor. Readable, and synchronizable — which is why the
    #: corrected design opens one for every directory it must synchronize.
    O_RDONLY = "O_RDONLY"
    #: A real write descriptor.
    O_WRONLY = "O_WRONLY"


#: The operations this model permits on an `O_PATH` descriptor, named after
#: `open(2)`'s list so a reviewer can compare the two directly.
O_PATH_PERMITTED_OPERATIONS = (
    "use as the dirfd argument of an *at() call",
    "fstat of the object the descriptor refers to",
    "duplication and descriptor-flag operations",
    "close",
)

#: The operations this model refuses on an `O_PATH` descriptor. `fsync` is the
#: one PR-20260911-R2-2 is about: revision 2 required it on `bin_fd` and on
#: `pgconf_fd`, both of which it had defined as `O_PATH`.
O_PATH_REFUSED_OPERATIONS = (
    "read",
    "write",
    "fsync",
    "ioctl",
)


# ---------------------------------------------------------------------------
# The synthetic filesystem: names, objects, and what survives a power loss
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Descriptor:
    """One open descriptor, with the mode it was obtained in.

    It refers to an **object identity**, not to a name, which is the documented
    property the whole design leans on: a descriptor keeps referring to the
    object it was opened on after the name is replaced.
    """

    number: int
    object_id: str
    mode: DescriptorMode
    #: What the descriptor was opened as, for refusal messages only. It is never
    #: re-resolved: the model resolves a name exactly once, when the descriptor
    #: is created.
    label: str = ""


@dataclass(frozen=True, slots=True)
class Barrier:
    """One durability barrier the contract names, and what it makes durable."""

    name: str
    #: `"data"` — the bytes of one file; `"entry"` — the entries of one directory.
    kind: str
    subject: str
    why: str


@dataclass(frozen=True, slots=True)
class ObservedState:
    """What a reader can see of the model's namespace and data at one moment."""

    entries: Mapping[tuple[str, str], str]
    data: Mapping[str, bytes]

    def resolve(self, parent_id: str, name: str) -> str | None:
        """The object a name resolves to now, or `None` for absent."""
        return dict(self.entries).get((parent_id, name))

    def listing(self, parent_id: str) -> tuple[str, ...]:
        """What `readdir` of one directory would return. The discovery path."""
        return tuple(
            sorted(name for (parent, name) in self.entries if parent == parent_id)
        )


class SyntheticFilesystem:
    """A namespace and a data store, each with a volatile and a durable half.

    The rules, and each one is a modelled reading of a documented semantic rather
    than an observation of one:

    * a **directory entry** created, renamed or removed is visible immediately
      and becomes durable only when its **containing directory** is synchronized;
    * a **file's bytes** are visible immediately and become durable only when
      **that file** is synchronized;
    * `fsync` on an `O_PATH` descriptor is refused; and
    * `crash()` discards everything that is not durable, and objects that no
      durable entry reaches are gone with it.

    The second rule and the first are separate on purpose. Revision 2's §2.3
    synchronized the captures and the run directory and treated the run
    directory's own entry in the recovery parent as covered by that. It is not,
    and `BarrierPolicy.R2_OMITTED_PARENT` exists so the model can show the
    difference rather than assert it.
    """

    def __init__(self) -> None:
        self._directories: set[str] = set()
        self._entries: dict[tuple[str, str], str] = {}
        self._data: dict[str, bytes] = {}
        self._durable_entries: dict[tuple[str, str], str] = {}
        self._durable_data: dict[str, bytes] = {}
        self._descriptors: dict[int, Descriptor] = {}
        self._next_descriptor = 3
        self._next_object = 0
        #: Every barrier the model actually crossed, in order. The evidence a
        #: test reads to assert that a sequence reached the barriers it claims.
        self.crossed: list[str] = []
        self.root = self._new_object(is_directory=True)
        self._durable_entries[("", self.root)] = self.root
        self._entries[("", self.root)] = self.root

    # -- object and descriptor bookkeeping ---------------------------------

    def _new_object(self, *, is_directory: bool) -> str:
        self._next_object += 1
        object_id = f"{'dir' if is_directory else 'file'}-{self._next_object}"
        if is_directory:
            self._directories.add(object_id)
        else:
            self._data[object_id] = b""
        return object_id

    def _descriptor(self, number: int) -> Descriptor:
        if number not in self._descriptors:
            raise ModelRefused(
                f"descriptor {number} is not open. The model hands out "
                "descriptors and refuses a number a caller invented, which is "
                "the contract's rule that a step needing a descriptor it was not "
                "given refuses rather than opening a path to obtain one."
            )
        return self._descriptors[number]

    def _open_descriptor(
        self, object_id: str, mode: DescriptorMode, label: str
    ) -> Descriptor:
        number = self._next_descriptor
        self._next_descriptor += 1
        descriptor = Descriptor(
            number=number, object_id=object_id, mode=mode, label=label
        )
        self._descriptors[number] = descriptor
        return descriptor

    def describe(self, number: int) -> Descriptor:
        """The descriptor a caller holds, so a test can read its mode and object.

        Public because the mode is the point of R2-2: a reviewer must be able to
        see that the descriptor a sequence synchronizes is the O_RDONLY one.
        """
        return self._descriptor(number)

    def entry_is_durable(self, dirfd: int, name: str) -> bool:
        """Whether this name would still resolve after a power loss."""
        parent = self._directory_descriptor(dirfd)
        return (parent.object_id, name) in self._durable_entries

    def close(self, number: int) -> None:
        self._descriptor(number)
        del self._descriptors[number]

    # -- namespace operations ----------------------------------------------

    def mkdirat(self, dirfd: int, name: str) -> str:
        """Exclusive directory creation. `EEXIST` is the refusal, and success is
        the ownership proof the contract calls **B1**."""
        parent = self._directory_descriptor(dirfd)
        if (parent.object_id, name) in self._entries:
            raise ModelRefused(
                f"EEXIST: {name!r} already exists under {parent.label or parent.object_id!r}. "
                "Exclusive creation is refused rather than satisfied by the "
                "object that is already there."
            )
        created = self._new_object(is_directory=True)
        self._entries[(parent.object_id, name)] = created
        return created

    def create_file(self, dirfd: int, name: str, data: bytes = b"") -> Descriptor:
        """`openat(dirfd, name, O_CREAT|O_EXCL|O_WRONLY|O_NOFOLLOW)`."""
        parent = self._directory_descriptor(dirfd)
        if (parent.object_id, name) in self._entries:
            raise ModelRefused(
                f"EEXIST: {name!r} already exists under "
                f"{parent.label or parent.object_id!r}."
            )
        created = self._new_object(is_directory=False)
        self._entries[(parent.object_id, name)] = created
        self._data[created] = data
        return self._open_descriptor(
            created, DescriptorMode.O_WRONLY, f"{parent.label}/{name}"
        )

    def openat(
        self, dirfd: int, name: str, mode: DescriptorMode
    ) -> Descriptor:
        """Open an existing entry relative to a held directory descriptor.

        **This is the only lookup in the model**, and it resolves exactly one
        component relative to a descriptor the caller already holds. There is no
        operation here that resolves a pathname from the root, which is the
        property the contract's descriptor chain exists to provide.
        """
        parent = self._directory_descriptor(dirfd)
        object_id = self._entries.get((parent.object_id, name))
        if object_id is None:
            raise ModelRefused(
                f"ENOENT: {name!r} does not resolve under "
                f"{parent.label or parent.object_id!r}."
            )
        return self._open_descriptor(
            object_id, mode, f"{parent.label}/{name}"
        )

    def fstatat(self, dirfd: int, name: str) -> str | None:
        """What the name resolves to now, or `None`.

        **This is all a post-unlink check can see — PR-20260911-R2-3.** It reports
        a name's current resolution. It does not report which object a previous
        `unlinkat` removed, and the model gives it no way to.
        """
        parent = self._directory_descriptor(dirfd)
        return self._entries.get((parent.object_id, name))

    def renameat(
        self,
        old_dirfd: int,
        old_name: str,
        new_dirfd: int,
        new_name: str,
        *,
        noreplace: bool = False,
    ) -> None:
        old_parent = self._directory_descriptor(old_dirfd)
        new_parent = self._directory_descriptor(new_dirfd)
        object_id = self._entries.get((old_parent.object_id, old_name))
        if object_id is None:
            raise ModelRefused(f"ENOENT: {old_name!r} does not resolve.")
        if noreplace and (new_parent.object_id, new_name) in self._entries:
            raise ModelRefused(
                f"EEXIST: RENAME_NOREPLACE and {new_name!r} already exists. The "
                "flag protects the destination; it says nothing about the "
                "identity of the source."
            )
        del self._entries[(old_parent.object_id, old_name)]
        self._entries[(new_parent.object_id, new_name)] = object_id

    def unlinkat(self, dirfd: int, name: str) -> None:
        """Remove a **name**.

        The model resolves `name` at the time of the call, as `unlink(2)` states,
        and removes whatever it resolves to now. There is no flag here that binds
        the final component to a previously observed object, because there is
        none in the syscall either.
        """
        parent = self._directory_descriptor(dirfd)
        if (parent.object_id, name) not in self._entries:
            raise ModelRefused(f"ENOENT: {name!r} does not resolve.")
        del self._entries[(parent.object_id, name)]

    # -- content ------------------------------------------------------------

    def write(self, fd: int, data: bytes) -> None:
        descriptor = self._descriptor(fd)
        if descriptor.mode is not DescriptorMode.O_WRONLY:
            raise ModelRefused(
                f"EBADF: descriptor {fd} was obtained {descriptor.mode.value} and "
                "a write needs a write descriptor."
            )
        self._data[descriptor.object_id] = data

    def read(self, fd: int) -> bytes:
        descriptor = self._descriptor(fd)
        if descriptor.mode is DescriptorMode.O_PATH:
            raise ModelRefused(
                f"EBADF: descriptor {fd} was obtained O_PATH. `open(2)` permits "
                f"{list(O_PATH_PERMITTED_OPERATIONS)} on such a descriptor and "
                f"refuses {list(O_PATH_REFUSED_OPERATIONS)}."
            )
        return self._data.get(descriptor.object_id, b"")

    # -- the barrier --------------------------------------------------------

    def fsync(self, fd: int, *, barrier: str = "") -> None:
        """The durability barrier, and the operation R2-2 found on the wrong kind
        of descriptor.

        A directory descriptor makes that directory's **entries** durable. A file
        descriptor makes that file's **bytes** durable. An `O_PATH` descriptor is
        refused, because synchronizing one is not among the operations `open(2)`
        permits on it.
        """
        descriptor = self._descriptor(fd)
        if descriptor.mode is DescriptorMode.O_PATH:
            raise ModelRefused(
                f"EBADF: `fsync` on descriptor {fd}, which was obtained O_PATH "
                f"as {descriptor.label or descriptor.object_id!r}. `open(2)` "
                f"permits {list(O_PATH_PERMITTED_OPERATIONS)} on an O_PATH "
                "descriptor and this is not one of them. This is "
                "PR-20260911-R2-2: revision 2 assigned O_PATH to `bin_fd` and "
                "`pgconf_fd` and then required `fsync` on both."
            )
        if descriptor.object_id in self._directories:
            for (parent, name), object_id in self._entries.items():
                if parent == descriptor.object_id:
                    self._durable_entries[(parent, name)] = object_id
            for (parent, name) in list(self._durable_entries):
                if parent == descriptor.object_id and (
                    parent,
                    name,
                ) not in self._entries:
                    del self._durable_entries[(parent, name)]
        else:
            self._durable_data[descriptor.object_id] = self._data.get(
                descriptor.object_id, b""
            )
        if barrier:
            self.crossed.append(barrier)

    # -- observation and crash ---------------------------------------------

    def _directory_descriptor(self, fd: int) -> Descriptor:
        descriptor = self._descriptor(fd)
        if descriptor.object_id not in self._directories:
            raise ModelRefused(
                f"ENOTDIR: descriptor {fd} does not refer to a directory."
            )
        return descriptor

    def now(self) -> ObservedState:
        """What a reader sees at this moment, durable or not."""
        return ObservedState(entries=dict(self._entries), data=dict(self._data))

    def durable(self) -> ObservedState:
        """What would survive a power loss, without taking one."""
        return ObservedState(
            entries=dict(self._durable_entries), data=dict(self._durable_data)
        )

    def open_directory(
        self, object_id: str, mode: DescriptorMode, label: str = ""
    ) -> Descriptor:
        """A descriptor on a directory the model already holds by identity.

        It exists for the provisioned roots the run does not create — the
        recovery parent and the configuration directory — and it takes an
        **object identity**, never a pathname, so no unchecked lookup enters the
        model through the back door.
        """
        if object_id not in self._directories:
            raise ModelRefused(f"{object_id!r} is not a directory in this model.")
        return self._open_descriptor(object_id, mode, label)

    def restart_process(self) -> "SyntheticFilesystem":
        """Lose the process and keep the filesystem — **PR-20260911-R3-1**.

        This is **not** `crash()`, and conflating the two is what hid the finding.
        A power loss discards everything no barrier made durable. A process that
        dies — killed, `SIGSEGV`, a wrapper that exits, an interpreter that
        aborts — takes its memory and its open file descriptions with it and
        **leaves the filesystem exactly as the last successful operation left
        it**, unsynchronized entries included.

        So this method discards descriptors and nothing else. What a successor
        then reads is the visible namespace, which is precisely the state R3-1
        names: a first-use record whose rename succeeded, whose containing
        directory was never synchronized, and whose writer's in-memory
        `NOT_DURABLE` outcome died with the writer.

        The two events are modelled separately and are never called for each
        other. A test that wants a power loss calls `crash()`; a test that wants
        a restart calls this; a test that wants both calls this and then that,
        in that order, which is the sequence a reader has to survive.
        """
        self._descriptors = {}
        return self

    def crash(self) -> "SyntheticFilesystem":
        """Discard everything that is not durable, and return this filesystem.

        Objects no durable entry reaches are gone, which is the point: a run
        directory whose entry in the recovery parent was never synchronized is
        not discoverable afterwards however carefully its own contents were
        written.
        """
        self._entries = dict(self._durable_entries)
        reachable = {self.root}
        frontier = [self.root]
        while frontier:
            parent = frontier.pop()
            for (holder, _name), object_id in self._entries.items():
                if holder == parent and object_id not in reachable:
                    reachable.add(object_id)
                    frontier.append(object_id)
        self._data = {
            object_id: self._durable_data.get(object_id, b"")
            for object_id in self._data
            if object_id in reachable
        }
        self._durable_data = {
            object_id: value
            for object_id, value in self._durable_data.items()
            if object_id in reachable
        }
        self._directories = {
            object_id for object_id in self._directories if object_id in reachable
        }
        self._descriptors = {}
        return self


def digest(data: bytes) -> str:
    """SHA-256 of the bytes handed in, and of nothing re-read from a name."""
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# The publication sequence — PR-20260911-R2-2
# ---------------------------------------------------------------------------


class BarrierPolicy(str, Enum):
    """Which barrier set a modelled publication crosses."""

    #: Revision 3's complete set. Every barrier below is crossed, in order.
    R3_COMPLETE = "r3_complete"
    #: Revision 2's set, reproduced so the corrected property can be shown to
    #: fail against it. It synchronizes the copy, the record and the run
    #: directory, and **never synchronizes the recovery parent**, so the run
    #: directory's own entry is not durable when the first configuration
    #: mutation is permitted.
    R2_OMITTED_PARENT = "r2_omitted_parent"


#: The complete durability dependency graph for a capture publication, in the
#: order the corrected contract requires. Each barrier names what it makes
#: durable and why nothing later may proceed without it.
#:
#: The two that revision 2 did not have are `recovery-parent-entry` and the
#: explicit separation of the copy's **data** barrier from its **entry** barrier.
PUBLICATION_BARRIERS = (
    Barrier(
        name="recovery-parent-entry",
        kind="entry",
        subject="the recovery parent directory",
        why=(
            "the new <run-id> directory's own entry lives in the recovery "
            "parent. Synchronizing the run directory makes its contents durable "
            "and says nothing about whether the parent still lists it after a "
            "power loss, so restart discovery by listing the recovery parent is "
            "not guaranteed to find the advertised recovery basis without this. "
            "This is the barrier PR-20260911-R2-2 found omitted."
        ),
    ),
    Barrier(
        name="copy-data",
        kind="data",
        subject="the captured copy",
        why="the captured bytes are not durable until the file itself is synchronized",
    ),
    Barrier(
        name="copy-entry",
        kind="entry",
        subject="the run directory",
        why=(
            "the copy's name under <run-id> is an entry in <run-id>, and an "
            "entry is made durable by synchronizing its containing directory"
        ),
    ),
    Barrier(
        name="record-data",
        kind="data",
        subject="the recovery record",
        why=(
            "the record binds the digest to the source identity and the "
            "destination. A copy whose record did not survive is bytes nobody "
            "can verify or place"
        ),
    ),
    Barrier(
        name="record-entry",
        kind="entry",
        subject="the run directory",
        why="the record's name under <run-id> is an entry in <run-id>",
    ),
)

#: The barrier revision 2 omitted, named once so a test does not spell it again.
OMITTED_R2_BARRIER = "recovery-parent-entry"

#: What is **not** a durability barrier, stated because revision 2's §2.3 step 7
#: reads like one. Re-reading the stored copy and digesting it establishes that
#: the bytes written are the bytes captured. It establishes nothing about whether
#: either survives a power loss, and a sequence that performs it in place of a
#: barrier has performed no barrier.
NOT_A_BARRIER = (
    "a read-back of the stored copy",
    "a digest comparison",
    "a successful rename",
)


@dataclass(frozen=True, slots=True)
class PublicationOutcome:
    """What one modelled capture publication concluded.

    `mutation_permitted` is the whole point: no first configuration mutation may
    occur until both the recoverable bytes and all the metadata needed to
    discover and verify them after a crash are durably published.
    """

    published: bool
    mutation_permitted: bool
    barriers_crossed: tuple[str, ...]
    refusals: tuple[str, ...] = ()
    run_directory: str = ""
    captured_digest: str = ""
    limits: tuple[str, ...] = MODEL_LIMITS


@dataclass(frozen=True, slots=True)
class RecoveryDiscovery:
    """What a restarted executor, or a human, finds after a power loss.

    Three separate questions, and revision 2's sequence fails the first while
    passing the other two — which is precisely why they are three fields and not
    one boolean.
    """

    #: Does listing the recovery parent still show this run's directory?
    discoverable: bool
    #: Are the record and the copy both present in it?
    record_present: bool
    copy_present: bool
    #: Does the surviving copy still digest to what the surviving record says?
    verifiable: bool
    listing: tuple[str, ...] = ()

    @property
    def usable(self) -> bool:
        """A recovery basis is usable only if all four hold."""
        return (
            self.discoverable
            and self.record_present
            and self.copy_present
            and self.verifiable
        )


@dataclass(frozen=True, slots=True)
class RecoveryRecord:
    """The binding between stored bytes and where they came from and go.

    A copy whose digest matches but whose record names a different destination is
    restored nowhere: the destination is part of the binding, not a convenience.
    """

    run_id: str
    destination: str
    source_identity: str
    content_digest: str
    byte_length: int
    captured_by: str

    def encoded(self) -> bytes:
        return (
            f"{self.run_id}|{self.destination}|{self.source_identity}|"
            f"{self.content_digest}|{self.byte_length}|{self.captured_by}"
        ).encode("utf-8")

    @classmethod
    def decoded(cls, raw: bytes) -> "RecoveryRecord":
        parts = raw.decode("utf-8").split("|")
        if len(parts) != 6:
            raise ModelRefused(
                "the recovery record is malformed. A record that cannot be "
                "parsed is not a record that can verify anything."
            )
        return cls(
            run_id=parts[0],
            destination=parts[1],
            source_identity=parts[2],
            content_digest=parts[3],
            byte_length=int(parts[4]),
            captured_by=parts[5],
        )


class RecoveryPublisher:
    """The corrected §2.3 sequence, as something a test can step through.

    **The descriptor rule it demonstrates — R2-2's required correction.** Every
    directory is held twice and for two different jobs:

    * an **O_PATH** descriptor, obtained once, used only as the `dirfd` of the
      `*at()` calls. It is the traversal reference, and `open(2)` permits it in
      that role; and
    * an **O_RDONLY** descriptor for any directory that must be synchronized,
      obtained by `openat(<the O_PATH parent>, name, O_RDONLY)` — *relative to
      the descriptor already held*, never by a fresh pathname lookup — and then
      `fstat`ed and compared with the identity recorded when the O_PATH
      descriptor was opened. A mismatch refuses.

    That is how a usable directory descriptor is obtained without reintroducing
    the unchecked lookup the chain exists to remove: the second open resolves one
    component relative to a held reference, and its result is bound to the
    intended object by comparison rather than by assumption.
    """

    def __init__(
        self,
        filesystem: SyntheticFilesystem,
        *,
        recovery_parent: str,
        policy: BarrierPolicy = BarrierPolicy.R3_COMPLETE,
        fail_at: str = "",
    ) -> None:
        self.fs = filesystem
        self.recovery_parent = recovery_parent
        self.policy = policy
        #: The barrier name, or operation name, at which this run is made to
        #: fail. `""` injects nothing and is the positive control.
        self.fail_at = fail_at
        self._barriers: list[str] = []

    # -- the descriptor rule, applied ---------------------------------------

    def _sync_descriptor(self, parent_path_fd: int, name: str, expected: str) -> int:
        """An O_RDONLY directory descriptor bound to the object it should be.

        Obtained relative to the held O_PATH parent and then compared with the
        identity recorded for that entry. The comparison is the binding; without
        it the second open would be the unchecked lookup R2-2 warns about.
        """
        descriptor = self.fs.openat(parent_path_fd, name, DescriptorMode.O_RDONLY)
        if descriptor.object_id != expected:
            raise ModelRefused(
                f"the O_RDONLY descriptor opened for {name!r} refers to "
                f"{descriptor.object_id!r} and the chain recorded "
                f"{expected!r}. The name was substituted between the two opens, "
                "so the synchronizable descriptor is not bound to the intended "
                "directory and the publication refuses."
            )
        return descriptor.number

    def _barrier(self, name: str, fd: int) -> None:
        if name not in {barrier.name for barrier in PUBLICATION_BARRIERS}:
            raise ModelRefused(f"{name!r} is not a declared publication barrier.")
        if self.fail_at == name:
            raise ModelRefused(
                f"injected failure at barrier {name!r}. The sequence stops here "
                "and no configuration mutation is permitted."
            )
        self.fs.fsync(fd, barrier=name)
        self._barriers.append(name)

    # -- the sequence -------------------------------------------------------

    def publish(
        self,
        *,
        run_id: str,
        source_fd: int,
        source_identity: str,
        destination: str,
        captured_by: str = "executor",
    ) -> PublicationOutcome:
        """Capture one configuration file and publish it durably, or refuse.

        Ordered exactly as the corrected contract requires, and every failure
        below refuses **before** the first configuration mutation:

        1. open the recovery parent's synchronizable descriptor;
        2. create `<run-id>` exclusively;
        3. **barrier `recovery-parent-entry`** — the new directory's entry;
        4. read the source into one held buffer and digest **that buffer**;
        5. write the copy, **barrier `copy-data`**, rename, **barrier
           `copy-entry`**;
        6. write the record, **barrier `record-data`**, rename, **barrier
           `record-entry`**;
        7. re-read the stored copy and compare. This is a **verification**, not a
           barrier — `NOT_A_BARRIER` says so; and
        8. only now is the mutation permitted.
        """
        refusals: list[str] = []
        try:
            parent_path_fd = self.fs.open_directory(
                self.recovery_parent, DescriptorMode.O_PATH, "recovery"
            ).number
            parent_sync_fd = self.fs.open_directory(
                self.recovery_parent, DescriptorMode.O_RDONLY, "recovery"
            ).number

            if self.fail_at == "create-run-directory":
                raise ModelRefused(
                    "injected failure creating the run directory. Nothing was "
                    "captured and no mutation is permitted."
                )
            run_object = self.fs.mkdirat(parent_path_fd, run_id)

            if self.policy is BarrierPolicy.R3_COMPLETE:
                self._barrier("recovery-parent-entry", parent_sync_fd)

            run_path_fd = self._bind(parent_path_fd, run_id, run_object)
            run_sync_fd = self._sync_descriptor(parent_path_fd, run_id, run_object)

            if self.fail_at == "capture-read":
                raise ModelRefused(
                    "injected failure reading the source. A short read is not "
                    "retried, because a retry reads a possibly different file."
                )
            buffer = self.fs.read(source_fd)
            content_digest = digest(buffer)

            copy_fd = self.fs.create_file(run_path_fd, "copy.tmp").number
            self.fs.write(copy_fd, buffer)
            self._barrier("copy-data", copy_fd)
            self.fs.renameat(
                run_path_fd, "copy.tmp", run_path_fd, "copy", noreplace=True
            )
            self._barrier("copy-entry", run_sync_fd)

            record = RecoveryRecord(
                run_id=run_id,
                destination=destination,
                source_identity=source_identity,
                content_digest=content_digest,
                byte_length=len(buffer),
                captured_by=captured_by,
            )
            record_fd = self.fs.create_file(run_path_fd, "record.tmp").number
            self.fs.write(record_fd, record.encoded())
            self._barrier("record-data", record_fd)
            self.fs.renameat(
                run_path_fd, "record.tmp", run_path_fd, "record", noreplace=True
            )
            self._barrier("record-entry", run_sync_fd)

            stored = self.fs.read(
                self.fs.openat(run_path_fd, "copy", DescriptorMode.O_RDONLY).number
            )
            if digest(stored) != content_digest:
                raise ModelRefused(
                    "the stored copy does not digest to the captured buffer. "
                    "This is a verification and not a barrier, and it refuses."
                )
        except ModelRefused as refusal:
            refusals.append(str(refusal))
            return PublicationOutcome(
                published=False,
                mutation_permitted=False,
                barriers_crossed=tuple(self._barriers),
                refusals=tuple(refusals),
            )

        required = {barrier.name for barrier in PUBLICATION_BARRIERS}
        missing = sorted(required - set(self._barriers))
        if missing:
            refusals.append(
                f"these publication barriers were not crossed: {missing}. No "
                "first configuration mutation may occur until both the "
                "recoverable bytes and all the metadata needed to discover and "
                "verify them after a crash are durably published."
            )
        return PublicationOutcome(
            published=not missing,
            mutation_permitted=not missing,
            barriers_crossed=tuple(self._barriers),
            refusals=tuple(refusals),
            run_directory=run_object,
            captured_digest=content_digest,
        )

    def _bind(self, parent_path_fd: int, name: str, expected: str) -> int:
        """The O_PATH traversal descriptor for a directory just created."""
        descriptor = self.fs.openat(parent_path_fd, name, DescriptorMode.O_PATH)
        if descriptor.object_id != expected:
            raise ModelRefused(
                f"the O_PATH descriptor opened for {name!r} refers to "
                f"{descriptor.object_id!r} rather than the object just created."
            )
        return descriptor.number


def discover_recovery(
    filesystem: SyntheticFilesystem, *, recovery_parent: str, run_id: str
) -> RecoveryDiscovery:
    """What listing the recovery parent finds, over whatever survived.

    It is deliberately written against the filesystem's **current** namespace, so
    a caller runs `crash()` first and then calls this: the discovery a restarted
    executor performs is the discovery this models, and it has no access to the
    executor's memory or to `R`.
    """
    state = filesystem.now()
    listing = state.listing(recovery_parent)
    run_object = state.resolve(recovery_parent, run_id)
    if run_object is None:
        return RecoveryDiscovery(
            discoverable=False,
            record_present=False,
            copy_present=False,
            verifiable=False,
            listing=listing,
        )
    copy_object = state.resolve(run_object, "copy")
    record_object = state.resolve(run_object, "record")
    verifiable = False
    if copy_object is not None and record_object is not None:
        raw = dict(state.data).get(record_object, b"")
        try:
            record = RecoveryRecord.decoded(raw)
        except ModelRefused:
            verifiable = False
        else:
            stored = dict(state.data).get(copy_object, b"")
            verifiable = digest(stored) == record.content_digest
    return RecoveryDiscovery(
        discoverable=True,
        record_present=record_object is not None,
        copy_present=copy_object is not None,
        verifiable=verifiable,
        listing=listing,
    )


# ---------------------------------------------------------------------------
# Restoration — the rename that is not yet durable
# ---------------------------------------------------------------------------


#: Restoration's barriers, in order. `restore-entry` is the one whose omission
#: makes a rename look like a durable restoration when it is not.
RESTORATION_BARRIERS = (
    Barrier(
        name="restore-data",
        kind="data",
        subject="the restoration temporary",
        why="the bytes are not durable until the temporary itself is synchronized",
    ),
    Barrier(
        name="restore-entry",
        kind="entry",
        subject="the configuration directory",
        why=(
            "the rename replaces an entry in the configuration directory, and an "
            "entry is durable only when that directory is synchronized. A "
            "restoration reported from a rename alone is a restoration that a "
            "power loss can undo"
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class RestorationOutcome:
    """One modelled restoration, with its durability stated separately.

    `renamed` and `durable` are two fields because they are two facts, and
    reporting the first as the second is the failure this models.
    """

    renamed: bool
    durable: bool
    reload_verified: bool
    barriers_crossed: tuple[str, ...] = ()
    refusals: tuple[str, ...] = ()
    limits: tuple[str, ...] = MODEL_LIMITS


def restore_configuration(
    filesystem: SyntheticFilesystem,
    *,
    config_path_fd: int,
    config_sync_fd: int,
    destinations: Sequence[tuple[str, bytes]],
    fail_at: str = "",
    reload_verified: bool = True,
) -> RestorationOutcome:
    """Ordered multi-file restoration over held buffers.

    Every temporary is written before any rename, the renames are then issued in
    a fixed order, and the containing directory is synchronized **after the last
    rename**. A failure injected between a rename and that barrier leaves the
    destination changed in the live namespace and unchanged in the durable one,
    which is the case the contract must not report as a durable restoration.
    """
    crossed: list[str] = []
    refusals: list[str] = []
    renamed = False
    try:
        for index, (name, content) in enumerate(destinations):
            temporary = f"{name}.restore.tmp"
            temporary_fd = filesystem.create_file(config_path_fd, temporary).number
            filesystem.write(temporary_fd, content)
            if fail_at == "restore-data":
                raise ModelRefused(
                    "injected failure before the restoration temporary was "
                    "synchronized. The destination is untouched."
                )
            filesystem.fsync(temporary_fd, barrier="restore-data")
            crossed.append(f"restore-data:{index}")
        for index, (name, _content) in enumerate(destinations):
            filesystem.renameat(
                config_path_fd, f"{name}.restore.tmp", config_path_fd, name
            )
            renamed = True
            if fail_at == f"between-renames:{index}":
                raise ModelRefused(
                    f"injected failure after rename {index} and before the next. "
                    "The configuration is mixed, which is why the post-reload "
                    "verification is a separate observation and failing it is S-B."
                )
        if fail_at == "restore-entry":
            raise ModelRefused(
                "injected failure after the last rename and before the "
                "configuration directory was synchronized. The rename is "
                "visible and it is not durable, and a restoration must not be "
                "reported durable from a rename alone."
            )
        filesystem.fsync(config_sync_fd, barrier="restore-entry")
        crossed.append("restore-entry")
    except ModelRefused as refusal:
        refusals.append(str(refusal))
        return RestorationOutcome(
            renamed=renamed,
            durable=False,
            reload_verified=False,
            barriers_crossed=tuple(crossed),
            refusals=tuple(refusals),
        )
    return RestorationOutcome(
        renamed=True,
        durable=True,
        reload_verified=reload_verified,
        barriers_crossed=tuple(crossed),
    )


# ---------------------------------------------------------------------------
# Removal and what a post-check can see — PR-20260911-R2-3
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Quiescence:
    """The three observations §1.6 requires before any exclusion-dependent effect.

    None defaults to true, and `observed` is separate from the three because a
    quiescence nobody looked for is not a quiescence that failed — it is an
    unmade observation, and the contract refuses on both.
    """

    observed: bool = False
    processes_ended: bool | None = None
    transactions_settled: bool | None = None
    transient_units_inactive: bool | None = None
    observed_by: str = ""

    def missing(self) -> tuple[str, ...]:
        missing: list[str] = []
        if not self.observed:
            missing.append("the quiescence observation was not made")
        if not self.observed_by.strip():
            missing.append("nobody is named as having observed it")
        for name, value in (
            ("processes_ended", self.processes_ended),
            ("transactions_settled", self.transactions_settled),
            ("transient_units_inactive", self.transient_units_inactive),
        ):
            if value is None:
                missing.append(f"{name} was not observed")
            elif value is False:
                missing.append(f"{name} was observed false")
        return tuple(missing)

    @property
    def established(self) -> bool:
        return not self.missing()

    @classmethod
    def verified(cls, *, observed_by: str) -> "Quiescence":
        return cls(
            observed=True,
            processes_ended=True,
            transactions_settled=True,
            transient_units_inactive=True,
            observed_by=observed_by,
        )

    @classmethod
    def not_observed(cls) -> "Quiescence":
        return cls()


@dataclass(frozen=True, slots=True)
class RemovalObservation:
    """What the **production** observation learns, and nothing more.

    Three fields, and the separation is the whole finding:

    * `pre_check_identity` — what the name resolved to before the removal;
    * `post_check_absent` — whether the name resolves afterwards. This is an
      **absence check**. `unlink(2)` removes a name, and a later `fstatat` on
      that name reports the name's resolution; neither reports which object the
      removal took; and
    * `post_check_identity` — the object the name resolves to afterwards, when it
      still resolves to something. `None` is ambiguous by construction: it is
      what a correct removal produces and what the substituted removal produces.

    `detected_substitution` is therefore true only where the **pre**-check caught
    it, never from the post-check's absence.
    """

    pre_check_identity: str | None
    post_check_absent: bool
    post_check_identity: str | None
    removal_issued: bool
    detected_substitution: bool
    refusals: tuple[str, ...] = ()
    limits: tuple[str, ...] = MODEL_LIMITS

    def indistinguishable_from(self, other: "RemovalObservation") -> bool:
        """Whether the two runs are the same to the production observer.

        It compares only what the production observation sees. The oracle's
        knowledge of which object went is not a field here, because the running
        system does not have it.
        """
        return (
            self.pre_check_identity == other.pre_check_identity
            and self.post_check_absent == other.post_check_absent
            and self.post_check_identity == other.post_check_identity
            and self.removal_issued == other.removal_issued
            and self.detected_substitution == other.detected_substitution
        )


@dataclass(frozen=True, slots=True)
class RemovalRefusal:
    """A removal that did not happen, and what survives it.

    §1.7's rule: a refusal before the effect leaves the objects in place, the run
    reports them as residue by absolute path, the §2.13.2b state is **S-B**, and
    independent recovery is untouched because the recovery store is outside the
    disposable root and was published before the first mutation.
    """

    refused: bool
    reasons: tuple[str, ...]
    residue: tuple[str, ...]
    dependent_work_refused: tuple[str, ...]
    cleanup_state: str = "S-B"
    independent_recovery_preserved: bool = True
    limits: tuple[str, ...] = MODEL_LIMITS


def remove_by_name(
    filesystem: SyntheticFilesystem,
    *,
    parent_fd: int,
    name: str,
    expected_identity: str,
    quiescence: Quiescence,
    substitute: "Substitution | None" = None,
    residue_paths: Sequence[str] = (),
    dependent_work: Sequence[str] = (),
) -> "RemovalObservation | RemovalRefusal":
    """The proposed cleanup removal, modelled honestly.

    Order, and each step is either prevention or detection but never both:

    1. **Prevention.** Verified experimental quiescence is a *prerequisite*. If
       it was not observed, was observed false, or was incomplete, the effect and
       every dependent step refuse, the objects are reported as residue and
       independent recovery is preserved. Returns a `RemovalRefusal`.
    2. **Pre-check.** `openat` + compare against the recorded identity. A
       mismatch here is a genuine detection and refuses before the removal.
    3. **Removal.** `unlinkat` resolves the final component at the time of the
       call and removes whatever it resolves to now.
    4. **Post-check.** `fstatat` on the same name. It observes whether a name
       exists. It cannot establish which object the removal took, and this model
       gives it no way to pretend otherwise.

    `substitute` injects a writer acting between (2) and (3). Such a writer is
    excluded by (1) under the declared premise; injecting it demonstrates the
    post-check's **detection limit** and is not a claim that it occurs under
    valid premises, nor a passing safety invariant.
    """
    if not quiescence.established:
        return RemovalRefusal(
            refused=True,
            reasons=tuple(
                f"quiescence is not established: {reason}"
                for reason in quiescence.missing()
            )
            + (
                "verified experimental quiescence is a prerequisite of name-based "
                "removal, and an unobserved, false or incomplete one refuses the "
                "effect and every step that depends on it.",
            ),
            residue=tuple(residue_paths),
            dependent_work_refused=tuple(dependent_work),
        )

    pre_check = filesystem.fstatat(parent_fd, name)
    if pre_check != expected_identity:
        return RemovalObservation(
            pre_check_identity=pre_check,
            post_check_absent=pre_check is None,
            post_check_identity=pre_check,
            removal_issued=False,
            detected_substitution=True,
            refusals=(
                f"the pre-check found {pre_check!r} at {name!r} and the run "
                f"recorded {expected_identity!r}. The removal is refused before "
                "it is issued, and this is the one place a substitution is "
                "actually detected.",
            ),
        )

    if substitute is not None:
        substitute.apply(filesystem, parent_fd=parent_fd, name=name)

    filesystem.unlinkat(parent_fd, name)
    post_check = filesystem.fstatat(parent_fd, name)
    return RemovalObservation(
        pre_check_identity=pre_check,
        post_check_absent=post_check is None,
        post_check_identity=post_check,
        removal_issued=True,
        detected_substitution=False,
    )


@dataclass(slots=True)
class Substitution:
    """A writer that renames the intended object away and installs another.

    The exact counterexample PR-20260911-R2-3 gives: the pre-check succeeds for
    **A**, A is renamed away, **B** is installed at the original name, `unlinkat`
    removes B, and the post-check returns ENOENT — indistinguishable from a
    successful intended removal.

    It carries the name A is moved to so a test can assert that **A survives**,
    which is the other half of the counterexample and the half a post-check
    cannot see either.
    """

    #: Where the intended object is moved to. It is still there afterwards.
    moved_to: str
    #: The object installed at the original name, and the one the removal takes.
    #: It is filled in when the substitution is applied, so a **test oracle** can
    #: assert which object went. The production observation never learns it, and
    #: `RemovalObservation` deliberately has no field for it.
    installed: str = ""

    def apply(
        self, filesystem: SyntheticFilesystem, *, parent_fd: int, name: str
    ) -> str:
        filesystem.renameat(parent_fd, name, parent_fd, self.moved_to)
        self.installed = filesystem.create_file(parent_fd, name).object_id
        return self.installed


#: What the removal design does and does not claim, corrected. Revision 2 §1.4.5
#: step 3 and §9 row 3 promised the post-check would detect the event and report
#: both identities. It does neither.
REMOVAL_EVIDENCE_CLAIMS = (
    "The pre-check is a real detection: it compares the name's current "
    "resolution with the identity this run recorded, and a mismatch refuses "
    "before any removal is issued.",
    "The post-check observes whether a name exists. It cannot establish which "
    "object the removal took, and it cannot report the replacement's identity, "
    "because the object is gone and the name is the only thing left to look at.",
    "A post-check returning ENOENT after a substituted removal is "
    "indistinguishable from a post-check returning ENOENT after the intended "
    "removal. It is therefore not evidence that the intended object was removed.",
    "Prevention is separate and it is verified experimental quiescence, which is "
    "a prerequisite rather than a detector. Unobserved, false or incomplete "
    "quiescence refuses the effect and its dependent work, reports residue by "
    "absolute path and preserves independent recovery.",
    "The trusted-administrator premise is retained and is an operational "
    "exclusion over people. It is not a claim that discretionary access control "
    "constrains root, and no new isolation architecture is proposed to repair "
    "the evidence claim.",
    "An injected substitution demonstrates the check's detection limit. It is "
    "not a passing safety invariant, and it is not a claim that the violation "
    "occurs under valid premises.",
)


__all__ = [
    "Barrier",
    "BarrierPolicy",
    "Descriptor",
    "DescriptorMode",
    "IMPLEMENTATION_CHECKS_NOT_PERFORMED",
    "MODEL_LIMITS",
    "ModelRefused",
    "NOT_A_BARRIER",
    "OMITTED_R2_BARRIER",
    "O_PATH_PERMITTED_OPERATIONS",
    "O_PATH_REFUSED_OPERATIONS",
    "ObservedState",
    "PUBLICATION_BARRIERS",
    "PublicationOutcome",
    "Quiescence",
    "REMOVAL_EVIDENCE_CLAIMS",
    "RESTORATION_BARRIERS",
    "RecoveryDiscovery",
    "RecoveryPublisher",
    "RecoveryRecord",
    "RemovalObservation",
    "RemovalRefusal",
    "RestorationOutcome",
    "Substitution",
    "SyntheticFilesystem",
    "digest",
    "discover_recovery",
    "remove_by_name",
    "restore_configuration",
]
