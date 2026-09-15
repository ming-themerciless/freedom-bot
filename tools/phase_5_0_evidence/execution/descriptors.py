"""The descriptor custody chain of runner contract r6 §1.3, over real files.

## Why this module exists

`PR-20260911-1` established that revision 1's remedy was not a remedy: comparing
a held descriptor's `fstat` with the `fstat` recorded when *that same descriptor*
was opened compares a value with itself, so it succeeds for every input
including the one it was meant to detect (r6 §1.1(1)). What survives is the
narrower and true half — **a descriptor refers to the open file description, and
a later change to the pathname does not change it** — and r6 §1.2 builds three
protections on it:

* **B1 exclusive creation** — `mkdirat`/`openat` with `O_CREAT|O_EXCL|
  O_NOFOLLOW`. Success proves nothing existed at that name, so the object is
  this run's by construction;
* **B2 descriptor-bound effect** — obtain a descriptor for the final object,
  verify it, then issue the effect on the **descriptor**; and
* **B3 exclusion** — issue the effect only inside a verified quiescence window.

This module owns B1 and B2. B3 is the executor's, because quiescence is an
observation about processes rather than about descriptors.

## The two descriptors per directory, and what makes the second one honest

r6 §1.3.2 holds every directory **twice**:

| | Traversal | Synchronizable |
|---|---|---|
| Flags | `O_PATH\\|O_NOFOLLOW\\|O_DIRECTORY` | `O_RDONLY\\|O_NOFOLLOW\\|O_DIRECTORY` |
| Permitted | only as the `dirfd` of an `*at()` call, and `fstat` of itself | only `fsync`, and `fstat` of itself |
| Transfer | inherited by a step whose case enumerates it | **never** |

`open(2)` lists what an `O_PATH` description permits and states that `read`,
`write`, `fchmod`, `fchown`, `ioctl` and `mmap` fail with `EBADF`. **`fsync` is
not in the permitted list**, which is why revision 2's `fsync(bin_fd)` and
`fsync(pgconf_fd)` were calls that cannot succeed — PR-20260911-R2-2. So the
barrier needs a second, differently-moded descriptor, and the re-review's
question was how obtaining it avoids reintroducing an unchecked pathname lookup.

Three properties, and all three are implemented below:

1. **one component, relative to a descriptor already held.** There is no lookup
   from `/`: the prefix is bound by the parent's traversal descriptor, exactly
   as `unlink(2)` describes the prefix being bound;
2. **the result is compared, not assumed.** The identity recorded when the
   traversal descriptor was opened is compared with the new descriptor's
   `fstat`. A mismatch **refuses the publication**; it does not retry and does
   not fall back to a path; and
3. **the residual interval is named.** Between the `openat` and the `fstat` the
   entry could have been replaced, in which case the `fstat` reports the
   replacement and the effect refuses. That is detection, and the interval is
   covered by B3 for directories an experimental identity can reach and by the
   administrator-only premise for the rest.

`bind_synchronizable()` is that sequence and `_compare` is that comparison. A
directory whose synchronizable descriptor is not bound has **no barrier**, and
`fsync_entry()` refuses rather than falling back to the traversal descriptor.

## What the inventory refuses

A `DIRFD` argument is an **index into a table the executor declared**, never a
number a caller chooses. `dirfd_for_index()` refuses an index outside the
declared table, and `transfer_table()` refuses to put a synchronizable
descriptor in a transferred set at all — the narrowing r2 did not state, whose
consequence is that a step that cannot `fsync` cannot make a durability claim
the executor did not make.

## Two amendments to r6, D1 and D2 — approved 2026-09-15

Both began as deviations this module reported. Peter approved them as runner
contract r6 amendments D1 and D2 on 2026-09-15, and r6 now specifies them.

**D1 — exclusive publication is `linkat` + `unlinkat`.** `RENAME_NOREPLACE` is
not reachable from Python 3.12's `os` module, and `ctypes` is refused outside
`case_program.py` by a structural guard that is a stop condition rather than an
obstacle to route around. `link(2)` fails with `EEXIST` when the destination
exists, so the exclusivity is the kernel's and not a check this module performs.
A stop between the two calls leaves the final name **already published** and the
temporary beside it as a second name for the same inode. `renameat` below raises
when the unlink fails, so that state is never reported as a successful
publication, and r6 §6.2 names what each reader of a leftover temporary does.
`EXCLUSIVE_PUBLICATION_SUBSTITUTE` states it where a reader of the publication
path will see it.

**D2 — the listing descriptor, r6 §1.3.3's D20.** §2.5's recovery discovery and
§5.11's ledger survey list a directory, and r6 as first accepted enumerated no
descriptor for `readdir`. `listing()` opens a short-lived descriptor
`.`-relative to the traversal descriptor, uses it for one `os.listdir`, and
closes it. It resolves no name and reaches no object the traversal descriptor
does not already refer to. `LISTING_DESCRIPTOR` states it, and `CONTRACT_GAPS`
is now empty.

## What this module does not do

It provisions nothing, creates no path under `/run` or `/var/lib`, starts no
process and takes no lock. Every root it opens is a path a caller hands it, so a
test drives the whole chain over a temporary directory and the production
constants stay data. It makes no claim about what a real power loss retains:
`fsync` is issued where the contract requires a barrier, and whether the target
filesystem implements a directory `fsync` as the containing-entry barrier is
preflight item **V8**, unperformed.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Sequence

from ..durability_model import Descriptor, DescriptorMode, ModelRefused

#: The classification a refusal carries. Short, fixed and safe: an operator sees
#: which rule refused and which **role** it refused for, never a path, never a
#: byte of hostile content and never an operating-system message.
DESCRIPTOR_NOT_REGISTERED = "descriptor-not-registered"
DESCRIPTOR_MODE_REFUSED = "descriptor-mode-refused"
DESCRIPTOR_IDENTITY_MISMATCH = "descriptor-identity-mismatch"
DESCRIPTOR_ALREADY_REGISTERED = "descriptor-already-registered"
DESCRIPTOR_NOT_BOUND = "synchronizable-descriptor-not-bound"
DESCRIPTOR_OPEN_REFUSED = "descriptor-open-refused"
DESCRIPTOR_BARRIER_FAILED = "durability-barrier-failed"
DESCRIPTOR_TRANSFER_REFUSED = "descriptor-transfer-refused"
DESCRIPTOR_OBJECT_EXISTS = "object-already-exists"
DESCRIPTOR_OBJECT_ABSENT = "object-absent"
DESCRIPTOR_OPERATION_REFUSED = "operation-refused"

#: Every value a `DescriptorRefused.classification` may take.
DESCRIPTOR_REFUSALS: frozenset[str] = frozenset(
    {
        DESCRIPTOR_NOT_REGISTERED,
        DESCRIPTOR_MODE_REFUSED,
        DESCRIPTOR_IDENTITY_MISMATCH,
        DESCRIPTOR_ALREADY_REGISTERED,
        DESCRIPTOR_NOT_BOUND,
        DESCRIPTOR_OPEN_REFUSED,
        DESCRIPTOR_BARRIER_FAILED,
        DESCRIPTOR_TRANSFER_REFUSED,
        DESCRIPTOR_OBJECT_EXISTS,
        DESCRIPTOR_OBJECT_ABSENT,
        DESCRIPTOR_OPERATION_REFUSED,
    }
)

#: Stated where a reader of the exclusive publication path will see it.
EXCLUSIVE_PUBLICATION_SUBSTITUTE = (
    "Runner contract r6 amendment D1, approved 2026-09-15: exclusive "
    "publication is `linkat` followed by `unlinkat` of the temporary, in place "
    "of `renameat2(…, RENAME_NOREPLACE)`. Python 3.12's `os` module exposes "
    "`renameat` and not `renameat2`, and the one `ctypes` exception in this "
    "repository is granted to `case_program._prctl_get_securebits` and to "
    "nothing else.",
    "`link(2)` fails with EEXIST when the destination exists, so the final name "
    "is claimed exclusively by the kernel rather than by a check this module "
    "performs, and no window exists in which the final name resolves to "
    "something this run did not write.",
    "The exact difference: a stop between the two calls leaves the final name "
    "already published, with the synchronized bytes, and the temporary beside "
    "it as a second name for the same inode. `renameat2` has no such state. "
    "This module raises rather than returning when the unlink fails, so the "
    "publication never reports success, and every reader of a leftover "
    "temporary refuses and removes nothing; r6 §6.2 names each reader.",
    "V6 no longer asks about `RENAME_NOREPLACE`. It observes what `linkat` needs "
    "from the target instead: hard-link support on each filesystem that holds "
    "an exclusive publication, and the `fs.protected_hardlinks` policy. V6 "
    "remains unconfirmed and is not closed by this statement.",
)

#: Runner contract r6 amendment D2, approved 2026-09-15: the listing descriptor.
LISTING_DESCRIPTOR = (
    "r6 §2.5 discovers recovery bases by listing the recovery parent and §5.11 "
    "surveys the ledger by listing its directory. r6 §1.3.3's D20 is the "
    "descriptor for that `readdir`.",
    "`DescriptorInventory.listing` opens D20 `.`-relative to the traversal "
    "descriptor, performs one `os.listdir` on it and closes it. It resolves no "
    "name and reaches no object the traversal descriptor does not already refer "
    "to, and it is never retained, transferred, synchronized or used as a "
    "`dirfd`.",
    "It is not authority to widen any other descriptor's permitted uses.",
)

#: Where the accepted design does not answer an operation it requires. Reported
#: rather than resolved: a gap in an accepted contract is a defect to raise. The
#: one gap this module reported, the listing descriptor, is r6 amendment D2.
CONTRACT_GAPS: tuple[str, ...] = ()


class DescriptorRefused(ModelRefused):
    """A descriptor-bound operation refused, with a fixed classification.

    **It subclasses `ModelRefused` deliberately.** `lifecycle_storage`'s
    publication path is one path shared by the synthetic model and by this
    mechanism, and it refuses on `ModelRefused`. Two exception types would be
    two refusal paths that can drift, which is the shape of every finding from
    R4-1 onward. The name is the model's for historical reasons; the sharing is
    the point.

    `classification` is one of `DESCRIPTOR_REFUSALS` and `role` is an inventory
    role name. Neither carries a path, a byte of content or an operating-system
    message, so a refusal is safe to put in an operator-facing artifact.
    """

    def __init__(self, classification: str, role: str, detail: str = "") -> None:
        if classification not in DESCRIPTOR_REFUSALS:
            raise ModelRefused(
                f"{classification!r} is not one of the descriptor refusals. The "
                "vocabulary is closed so that an operator-facing refusal cannot "
                "acquire a new meaning by being raised."
            )
        self.classification = classification
        self.role = role
        message = f"{classification}: {role}"
        if detail:
            message = f"{message} — {detail}"
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class ObjectIdentity:
    """`(st_dev, st_ino)` — what a directory entry resolved to when it was read.

    It is a **recorded fact about one lookup**, and its only use is to be
    compared with a later lookup's result. It is never re-derived from the
    descriptor that produced it, because that comparison is r6 §1.1(1)'s
    withdrawn one: a value against itself.
    """

    device: int
    inode: int

    @classmethod
    def of(cls, fd: int) -> "ObjectIdentity":
        facts = os.fstat(fd)
        return cls(device=facts.st_dev, inode=facts.st_ino)

    @property
    def object_id(self) -> str:
        """The identity as the shared filesystem vocabulary spells it."""
        return f"{self.device}:{self.inode}"


@dataclass(slots=True)
class DirectoryHandle:
    """One directory, held twice, with the identity its lookup recorded.

    `parent_role` and `name` are how the synchronizable descriptor is obtained:
    one component, relative to the parent's traversal descriptor. A root opened
    from a pathname has neither, and its synchronizable descriptor is obtained
    from the same pathname and compared with the recorded identity — a genuine
    comparison, because the second resolution is a second lookup.
    """

    role: str
    identity: ObjectIdentity
    traversal_fd: int
    #: The path this root was opened from, for a provisioned root only. It is
    #: used for exactly one re-resolution, in `bind_synchronizable`, and for
    #: nothing else: no effect is ever issued against it.
    root_path: str = ""
    parent_role: str = ""
    name: str = ""
    synchronizable_fd: int | None = None

    @property
    def bound(self) -> bool:
        return self.synchronizable_fd is not None


@dataclass(frozen=True, slots=True)
class TransferEntry:
    """One row of the table a step is handed, naming what index 3+n refers to.

    `number` is the executor's own descriptor for that role — the source of the
    `dup2` the child performs into `index`. It is carried here because the
    boundary is the one object that launches, and a table that named a role the
    boundary could not resolve would be a declaration nothing enforced.
    """

    index: int
    role: str
    mode: DescriptorMode
    number: int | None = None


_DIRECTORY_TRAVERSAL_FLAGS = os.O_PATH | os.O_NOFOLLOW | os.O_DIRECTORY
_DIRECTORY_SYNC_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY
#: The first descriptor number a transferred table may occupy. 0, 1 and 2 are
#: the standard streams and are never part of a declared set.
FIRST_TRANSFERRED_DESCRIPTOR = 3


class DescriptorInventory:
    """The r6 §1.3.3 inventory, held open for the run.

    Every directory is registered under a **role name** — `evidence`, `root`,
    `bin`, `journal`, `recovery`, `runstore`, `lifecycle`, `runs` — and every
    operation below names a role rather than a path. The only pathnames this
    class ever sees are the provisioned roots a caller opens it on, which is
    what lets a test drive the whole chain over a temporary directory while the
    production constants stay data.
    """

    def __init__(self) -> None:
        self._directories: dict[str, DirectoryHandle] = {}
        self._by_object: dict[str, str] = {}
        self._transfer: tuple[TransferEntry, ...] = ()
        self._closed = False

    # -- registration --------------------------------------------------------

    def open_provisioned_root(self, role: str, path: str) -> DirectoryHandle:
        """Open a directory this run did not create, by the path it is named by.

        A provisioned root — the evidence parent, the PostgreSQL configuration
        directory, the recovery parent, the laboratory directory, the ledger
        directory — exists before the run and is not created by it, so **B1 is
        not available** and the traversal descriptor is obtained by resolving a
        pathname. The exposure that leaves is administrator-only for every root
        in the inventory, which r6 §10 records as an assumption rather than as
        something this mechanism establishes.
        """
        self._require_open()
        self._require_unregistered(role)
        traversal = self._open(role, path, _DIRECTORY_TRAVERSAL_FLAGS)
        handle = DirectoryHandle(
            role=role,
            identity=ObjectIdentity.of(traversal),
            traversal_fd=traversal,
            root_path=path,
        )
        self._register(handle)
        return handle

    def create_directory(
        self, *, parent_role: str, name: str, role: str, mode: int = 0o700
    ) -> DirectoryHandle:
        """**B1.** `mkdirat(parent, name, mode)`, exclusively.

        `EEXIST` is the refusal and success *is* the ownership proof: nothing
        existed at that name, so the object is this run's by construction. The
        traversal descriptor is opened on the result immediately and held for
        the run, so every later effect under this directory is relative to a
        descriptor rather than to a name.
        """
        self._require_open()
        self._require_unregistered(role)
        parent = self.directory(parent_role)
        _require_component(name, role)
        try:
            os.mkdir(name, mode, dir_fd=parent.traversal_fd)
        except FileExistsError:
            raise DescriptorRefused(
                DESCRIPTOR_OBJECT_EXISTS,
                role,
                "exclusive creation found an entry already at the name, so this "
                "run cannot establish that the object is its own",
            ) from None
        except OSError:
            raise DescriptorRefused(DESCRIPTOR_OPEN_REFUSED, role) from None
        traversal = self._openat(role, parent.traversal_fd, name, _DIRECTORY_TRAVERSAL_FLAGS)
        handle = DirectoryHandle(
            role=role,
            identity=ObjectIdentity.of(traversal),
            traversal_fd=traversal,
            parent_role=parent_role,
            name=name,
        )
        self._register(handle)
        return handle

    def adopt_directory(
        self, *, parent_role: str, name: str, role: str
    ) -> DirectoryHandle:
        """Hold an existing directory that lives under a directory already held.

        Used for a provisioned child the run does not create — the ledger
        directory under the laboratory directory, a recovery run directory a
        restart rediscovers. The lookup resolves **one component** under a held
        descriptor, and the identity it records is what the synchronizable
        descriptor is later compared against.
        """
        self._require_open()
        self._require_unregistered(role)
        parent = self.directory(parent_role)
        _require_component(name, role)
        traversal = self._openat(
            role, parent.traversal_fd, name, _DIRECTORY_TRAVERSAL_FLAGS
        )
        handle = DirectoryHandle(
            role=role,
            identity=ObjectIdentity.of(traversal),
            traversal_fd=traversal,
            parent_role=parent_role,
            name=name,
        )
        self._register(handle)
        return handle

    # -- the synchronizable descriptor, bound by comparison ------------------

    def bind_synchronizable(self, role: str) -> int:
        """r6 §1.3.2: open the second descriptor and **compare** its identity.

        The second open resolves the same single component under the same held
        parent — or, for a provisioned root, the same pathname — and its
        `fstat` is compared with the identity the first lookup recorded. A
        mismatch means the entry was replaced between the two opens, and it
        **refuses**: no retry, no fallback to a path, and no publication.
        """
        self._require_open()
        handle = self.directory(role)
        if handle.bound:
            return int(handle.synchronizable_fd or 0)
        if handle.parent_role:
            parent = self.directory(handle.parent_role)
            fd = self._openat(role, parent.traversal_fd, handle.name, _DIRECTORY_SYNC_FLAGS)
        else:
            fd = self._open(role, handle.root_path, _DIRECTORY_SYNC_FLAGS)
        found = ObjectIdentity.of(fd)
        if found != handle.identity:
            os.close(fd)
            raise DescriptorRefused(
                DESCRIPTOR_IDENTITY_MISMATCH,
                role,
                "the second lookup reached a different object from the one the "
                "first recorded, so the barrier would land on something this "
                "run did not verify",
            )
        handle.synchronizable_fd = fd
        return fd

    def fsync_entry(self, role: str) -> None:
        """The containing-entry barrier, on the `O_RDONLY` descriptor.

        It refuses rather than falling back to the traversal descriptor when the
        synchronizable one is not bound, because `fsync` on an `O_PATH`
        description fails with `EBADF` — the call revision 2 required twice and
        that cannot succeed.
        """
        self._require_open()
        handle = self.directory(role)
        if not handle.bound:
            raise DescriptorRefused(
                DESCRIPTOR_NOT_BOUND,
                role,
                "no synchronizable descriptor is bound for this directory, so "
                "there is no barrier to issue and the effect that depends on it "
                "refuses",
            )
        try:
            os.fsync(int(handle.synchronizable_fd or 0))
        except OSError:
            raise DescriptorRefused(DESCRIPTOR_BARRIER_FAILED, role) from None

    # -- lookup and hand-out --------------------------------------------------

    def directory(self, role: str) -> DirectoryHandle:
        handle = self._directories.get(role)
        if handle is None:
            raise DescriptorRefused(DESCRIPTOR_NOT_REGISTERED, role)
        return handle

    def roles(self) -> tuple[str, ...]:
        return tuple(sorted(self._directories))

    def traversal(self, role: str) -> int:
        return self.directory(role).traversal_fd

    def declare_transfer(self, roles: Sequence[str]) -> tuple[TransferEntry, ...]:
        """Declare the table a step inherits, starting at descriptor 3.

        **No synchronizable descriptor is ever in a transferred set.** The rule
        is enforced here rather than left to the caller's discipline, because a
        step that could `fsync` could make a durability claim the executor did
        not make — which is exactly the asymmetry r6 §5.12 relies on.
        """
        self._require_open()
        entries: list[TransferEntry] = []
        for offset, role in enumerate(roles):
            handle = self.directory(role)
            entries.append(
                TransferEntry(
                    index=FIRST_TRANSFERRED_DESCRIPTOR + offset,
                    role=handle.role,
                    # **The traversal descriptor, and only ever it.** The
                    # synchronizable one is never in a transferred set: a step
                    # that could `fsync` could make a durability claim the
                    # executor did not make.
                    mode=DescriptorMode.O_PATH,
                    number=handle.traversal_fd,
                )
            )
        self._transfer = tuple(entries)
        return self._transfer

    @property
    def transfer(self) -> tuple[TransferEntry, ...]:
        return self._transfer

    def refuse_synchronizable_transfer(self, role: str) -> None:
        """Stated as its own method so the rule has one call site and one test."""
        raise DescriptorRefused(
            DESCRIPTOR_TRANSFER_REFUSED,
            role,
            "a synchronizable descriptor is never transferred, so a step cannot "
            "make a durability claim the executor did not make",
        )

    def dirfd_for_index(self, index: int) -> int:
        """Resolve a case program's `DIRFD` argument. **An index, never a number.**

        The `DIRFD` argument kind is an index into the table this run declared
        and into nothing else. An index outside it refuses; a step that needs a
        descriptor it was not given refuses too, and never opens a path to
        obtain one.
        """
        self._require_open()
        for entry in self._transfer:
            if entry.index == index:
                return self.traversal(entry.role)
        raise DescriptorRefused(
            DESCRIPTOR_NOT_REGISTERED,
            str(index),
            "the index is outside the table this run declared, and a descriptor "
            "that was not declared is not one this step may use",
        )

    # -- directory listing, the enumerated addition --------------------------

    def listing(self, role: str) -> tuple[str, ...]:
        """One `readdir`, through a short-lived `.`-relative descriptor.

        r6 §1.3.3's D20; see `LISTING_DESCRIPTOR`. The descriptor is opened
        relative to the traversal descriptor already held, is used for exactly
        one listing, and is closed before this method returns.
        """
        self._require_open()
        handle = self.directory(role)
        try:
            fd = os.open(".", _DIRECTORY_SYNC_FLAGS, dir_fd=handle.traversal_fd)
        except OSError:
            raise DescriptorRefused(DESCRIPTOR_OPEN_REFUSED, role) from None
        try:
            return tuple(sorted(os.listdir(fd)))
        except OSError:
            raise DescriptorRefused(DESCRIPTOR_OPERATION_REFUSED, role) from None
        finally:
            os.close(fd)

    # -- lifetime -------------------------------------------------------------

    def close(self) -> None:
        """Close every descriptor. Idempotent, and it never raises."""
        for handle in self._directories.values():
            for fd in (handle.synchronizable_fd, handle.traversal_fd):
                if fd is None:
                    continue
                try:
                    os.close(fd)
                except OSError:  # pragma: no cover - a closed descriptor
                    pass
        self._directories = {}
        self._by_object = {}
        self._transfer = ()
        self._closed = True

    def __enter__(self) -> "DescriptorInventory":
        return self

    def __exit__(self, *_exception: object) -> None:
        self.close()

    # -- internals ------------------------------------------------------------

    def role_for_object(self, object_id: str) -> str:
        role = self._by_object.get(object_id)
        if role is None:
            raise DescriptorRefused(DESCRIPTOR_NOT_REGISTERED, object_id)
        return role

    def _register(self, handle: DirectoryHandle) -> None:
        self._directories[handle.role] = handle
        self._by_object[handle.identity.object_id] = handle.role

    def _require_unregistered(self, role: str) -> None:
        if role in self._directories:
            raise DescriptorRefused(DESCRIPTOR_ALREADY_REGISTERED, role)

    def _require_open(self) -> None:
        if self._closed:
            raise DescriptorRefused(
                DESCRIPTOR_NOT_REGISTERED,
                "inventory",
                "the inventory has been closed, and a closed inventory holds no "
                "descriptor any effect may be bound to",
            )

    @staticmethod
    def _open(role: str, path: str, flags: int) -> int:
        if not path:
            raise DescriptorRefused(DESCRIPTOR_OPEN_REFUSED, role)
        try:
            return os.open(path, flags)
        except OSError:
            raise DescriptorRefused(DESCRIPTOR_OPEN_REFUSED, role) from None

    @staticmethod
    def _openat(role: str, dirfd: int, name: str, flags: int) -> int:
        try:
            return os.open(name, flags, dir_fd=dirfd)
        except FileNotFoundError:
            raise DescriptorRefused(DESCRIPTOR_OBJECT_ABSENT, role) from None
        except OSError:
            raise DescriptorRefused(DESCRIPTOR_OPEN_REFUSED, role) from None


def _require_component(name: str, role: str) -> None:
    """One path component: no separator, no `.`, no `..`, no empty string.

    The check is here as well as at the planner because this is the last place
    before the syscall, and a component that could carry a separator would be a
    pathname the prefix binding does not cover.
    """
    if (
        not name
        or "/" in name
        or name in (".", "..")
        or "\0" in name
        or name != name.strip()
    ):
        raise DescriptorRefused(
            DESCRIPTOR_OPERATION_REFUSED,
            role,
            "a name is exactly one path component, so a separator or a relative "
            "segment cannot reach past the descriptor that binds the prefix",
        )


# ---------------------------------------------------------------------------
# The filesystem surface the record stores are written against
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _PosixView:
    """What a reader sees now. `listing` is a real `readdir`; there is no other.

    It deliberately has **no durable-state accessor**. `durability_model`'s
    `ObservedState` has two — `now()` and `durable()` — because a test needs to
    see what a power loss would keep. A reader with the second one would be a
    reader holding a fact the mechanism does not have, which is PR-20260911-R3-1
    in one sentence, so this view offers only the first.
    """

    inventory: "DescriptorInventory"

    def listing(self, parent_id: str) -> tuple[str, ...]:
        return self.inventory.listing(self.inventory.role_for_object(parent_id))


class PosixFilesystem:
    """The real filesystem behind `lifecycle_storage`'s record stores.

    **The point of this class is that there is no second set of rules.**
    `DurableRecordStore` and `RunLedger` carry r6 §§5.5, 5.11 and 5.12 — the
    codec, the history order rules, the participant validator, the publication
    order and the terminal sequence — over an injected filesystem. Giving the
    mechanism its own copy of those rules would be giving the protocol two
    readers that can drift, which is the shape of R4-1, R4-2 and R5-1. So the
    mechanism is this object: the same stores, the same validators, real
    descriptors underneath.

    Every method resolves at most one component, relative to a descriptor the
    inventory already holds. There is no operation here that resolves a pathname
    from the root.
    """

    def __init__(self, inventory: DescriptorInventory) -> None:
        self._inventory = inventory
        self._descriptors: dict[int, Descriptor] = {}

    @property
    def inventory(self) -> DescriptorInventory:
        return self._inventory

    # -- directories ---------------------------------------------------------

    def open_directory(
        self, object_id: str, mode: DescriptorMode, label: str = ""
    ) -> Descriptor:
        """The **held** descriptor for a registered directory, in one mode.

        It opens nothing: the inventory opened both descriptors once, at the
        directory's creation or adoption, and holds them for the run. A caller
        that asks for the synchronizable one before it is bound is refused
        rather than handed the traversal one.
        """
        role = self._inventory.role_for_object(object_id)
        handle = self._inventory.directory(role)
        if mode is DescriptorMode.O_PATH:
            return self._track(handle.traversal_fd, object_id, mode, label or role)
        if mode is DescriptorMode.O_RDONLY:
            fd = self._inventory.bind_synchronizable(role)
            return self._track(fd, object_id, mode, label or role)
        raise DescriptorRefused(
            DESCRIPTOR_MODE_REFUSED,
            role,
            "a directory is held as a traversal descriptor and a synchronizable "
            "one, and in no third mode",
        )

    def mkdirat(self, dirfd: int, name: str, mode: int = 0o700) -> str:
        parent = self._directory_descriptor(dirfd)
        role = self._inventory.role_for_object(parent.object_id)
        _require_component(name, role)
        try:
            os.mkdir(name, mode, dir_fd=dirfd)
        except FileExistsError:
            raise DescriptorRefused(DESCRIPTOR_OBJECT_EXISTS, role) from None
        except OSError:
            raise DescriptorRefused(DESCRIPTOR_OPEN_REFUSED, role) from None
        facts = os.stat(name, dir_fd=dirfd, follow_symlinks=False)
        return f"{facts.st_dev}:{facts.st_ino}"

    # -- files ----------------------------------------------------------------

    def create_file(self, dirfd: int, name: str, data: bytes = b"") -> Descriptor:
        """**B1 for a file.** `O_CREAT|O_EXCL|O_WRONLY|O_NOFOLLOW`, mode 0600.

        `O_EXCL` proves the temporary name was free, so the bytes that follow go
        into an object this run created and into nothing that was already there.
        """
        parent = self._directory_descriptor(dirfd)
        role = self._inventory.role_for_object(parent.object_id)
        _require_component(name, role)
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW
        try:
            fd = os.open(name, flags, 0o600, dir_fd=dirfd)
        except FileExistsError:
            raise DescriptorRefused(DESCRIPTOR_OBJECT_EXISTS, role) from None
        except OSError:
            raise DescriptorRefused(DESCRIPTOR_OPEN_REFUSED, role) from None
        descriptor = self._track(fd, self._identity(fd), DescriptorMode.O_WRONLY, name)
        if data:
            self.write(fd, data)
        return descriptor

    def openat(self, dirfd: int, name: str, mode: DescriptorMode) -> Descriptor:
        parent = self._directory_descriptor(dirfd)
        role = self._inventory.role_for_object(parent.object_id)
        _require_component(name, role)
        if mode is DescriptorMode.O_RDONLY:
            flags = os.O_RDONLY | os.O_NOFOLLOW
        elif mode is DescriptorMode.O_WRONLY:
            flags = os.O_WRONLY | os.O_NOFOLLOW
        else:
            flags = os.O_PATH | os.O_NOFOLLOW
        try:
            fd = os.open(name, flags, dir_fd=dirfd)
        except FileNotFoundError:
            raise DescriptorRefused(DESCRIPTOR_OBJECT_ABSENT, role) from None
        except OSError:
            raise DescriptorRefused(DESCRIPTOR_OPEN_REFUSED, role) from None
        return self._track(fd, self._identity(fd), mode, name)

    def fstatat(self, dirfd: int, name: str) -> str | None:
        """What the name resolves to now, or `None`.

        **This is all a post-unlink check can see — PR-20260911-R2-3.** It
        reports a name's current resolution. It does not report which object a
        previous `unlinkat` removed, and nothing here gives it a way to.
        """
        parent = self._directory_descriptor(dirfd)
        role = self._inventory.role_for_object(parent.object_id)
        _require_component(name, role)
        try:
            facts = os.stat(name, dir_fd=dirfd, follow_symlinks=False)
        except FileNotFoundError:
            return None
        except OSError:
            raise DescriptorRefused(DESCRIPTOR_OPERATION_REFUSED, role) from None
        return f"{facts.st_dev}:{facts.st_ino}"

    def renameat(
        self,
        source_dirfd: int,
        source_name: str,
        destination_dirfd: int,
        destination_name: str,
        *,
        noreplace: bool = False,
    ) -> None:
        """Publish the temporary onto the final name.

        `noreplace=False` is a plain `renameat`. `noreplace=True` is the
        `linkat`/`unlinkat` substitute `EXCLUSIVE_PUBLICATION_SUBSTITUTE`
        describes: the kernel refuses the link when the destination exists, so
        the exclusivity is not a check this module performs.
        """
        source_parent = self._directory_descriptor(source_dirfd)
        destination_parent = self._directory_descriptor(destination_dirfd)
        source_role = self._inventory.role_for_object(source_parent.object_id)
        destination_role = self._inventory.role_for_object(destination_parent.object_id)
        _require_component(source_name, source_role)
        _require_component(destination_name, destination_role)
        if noreplace:
            try:
                os.link(
                    source_name,
                    destination_name,
                    src_dir_fd=source_dirfd,
                    dst_dir_fd=destination_dirfd,
                    follow_symlinks=False,
                )
            except FileExistsError:
                raise DescriptorRefused(
                    DESCRIPTOR_OBJECT_EXISTS, destination_role
                ) from None
            except OSError:
                raise DescriptorRefused(
                    DESCRIPTOR_OPERATION_REFUSED, destination_role
                ) from None
            try:
                os.unlink(source_name, dir_fd=source_dirfd)
            except OSError:
                raise DescriptorRefused(
                    DESCRIPTOR_OPERATION_REFUSED, source_role
                ) from None
            return
        try:
            os.rename(
                source_name,
                destination_name,
                src_dir_fd=source_dirfd,
                dst_dir_fd=destination_dirfd,
            )
        except OSError:
            raise DescriptorRefused(
                DESCRIPTOR_OPERATION_REFUSED, destination_role
            ) from None

    def unlinkat(self, dirfd: int, name: str, *, directory: bool = False) -> None:
        """Remove one named entry. **Not bindable, and this says so.**

        `unlinkat` resolves its final component at the time of the call and no
        flag binds that component to a previously observed inode. r6 §1.4.5 is
        the whole argument: the pre-check detects, the removal is covered by B3
        or refused, and the post-check is an absence check and nothing more.
        """
        parent = self._directory_descriptor(dirfd)
        role = self._inventory.role_for_object(parent.object_id)
        _require_component(name, role)
        try:
            os.unlink(name, dir_fd=dirfd) if not directory else os.rmdir(
                name, dir_fd=dirfd
            )
        except OSError:
            raise DescriptorRefused(DESCRIPTOR_OPERATION_REFUSED, role) from None

    # -- bytes ----------------------------------------------------------------

    def write(self, fd: int, data: bytes) -> None:
        descriptor = self._descriptor(fd)
        if descriptor.mode is not DescriptorMode.O_WRONLY:
            raise DescriptorRefused(
                DESCRIPTOR_MODE_REFUSED,
                descriptor.label,
                "a write goes to a descriptor opened for writing, and an O_PATH "
                "description permits no write at all",
            )
        written = 0
        while written < len(data):
            try:
                written += os.write(fd, data[written:])
            except OSError:
                raise DescriptorRefused(
                    DESCRIPTOR_OPERATION_REFUSED, descriptor.label
                ) from None

    def read(self, fd: int) -> bytes:
        descriptor = self._descriptor(fd)
        if descriptor.mode is not DescriptorMode.O_RDONLY:
            raise DescriptorRefused(
                DESCRIPTOR_MODE_REFUSED,
                descriptor.label,
                "a read comes from a descriptor opened for reading, and an "
                "O_PATH description permits no read at all",
            )
        chunks: list[bytes] = []
        try:
            os.lseek(fd, 0, os.SEEK_SET)
            while True:
                chunk = os.read(fd, 65536)
                if not chunk:
                    break
                chunks.append(chunk)
        except OSError:
            raise DescriptorRefused(
                DESCRIPTOR_OPERATION_REFUSED, descriptor.label
            ) from None
        return b"".join(chunks)

    def fsync(self, fd: int, *, barrier: str = "") -> None:
        """A durability barrier, refused on an `O_PATH` description.

        The kernel refuses it too, with `EBADF`. It is refused here as well so
        that the rule is a rule of this mechanism rather than an accident of
        which kernel the mechanism happens to run on — and so a test can
        observe the refusal without depending on one.
        """
        descriptor = self._descriptor(fd)
        if descriptor.mode is DescriptorMode.O_PATH:
            raise DescriptorRefused(
                DESCRIPTOR_MODE_REFUSED,
                descriptor.label,
                "`fsync` is not among the operations `open(2)` permits on an "
                "O_PATH description, so this call cannot succeed and the "
                "barrier it would have been does not exist",
            )
        try:
            os.fsync(fd)
        except OSError:
            raise DescriptorRefused(
                DESCRIPTOR_BARRIER_FAILED, barrier or descriptor.label
            ) from None

    def close(self, number: int) -> None:
        descriptor = self._descriptor(number)
        self._descriptors.pop(number, None)
        if self._is_inventory_descriptor(descriptor):
            # The inventory owns its two descriptors for the whole run and
            # closes them itself. Releasing one here would take a barrier away
            # from every later publication.
            return
        try:
            os.close(number)
        except OSError:  # pragma: no cover - already closed
            pass

    def describe(self, number: int) -> Descriptor:
        return self._descriptor(number)

    def now(self) -> _PosixView:
        return _PosixView(inventory=self._inventory)

    # -- internals ------------------------------------------------------------

    def _is_inventory_descriptor(self, descriptor: Descriptor) -> bool:
        for role in self._inventory.roles():
            handle = self._inventory.directory(role)
            if descriptor.number in (handle.traversal_fd, handle.synchronizable_fd):
                return True
        return False

    def _track(
        self, fd: int, object_id: str, mode: DescriptorMode, label: str
    ) -> Descriptor:
        descriptor = Descriptor(number=fd, object_id=object_id, mode=mode, label=label)
        self._descriptors[fd] = descriptor
        return descriptor

    def _descriptor(self, number: int) -> Descriptor:
        """The descriptor's recorded mode, or a refusal.

        Two sources, and no third. A descriptor this filesystem issued is in its
        own table; a directory descriptor the **inventory** holds for the run is
        recovered from the inventory, with the mode that inventory opened it in.
        A number from anywhere else is refused: an unregistered descriptor is
        never used as one, which is what makes `DIRFD` an index into a declared
        table rather than a number a caller chooses.
        """
        descriptor = self._descriptors.get(number)
        if descriptor is not None:
            return descriptor
        for role in self._inventory.roles():
            handle = self._inventory.directory(role)
            if number == handle.traversal_fd:
                return Descriptor(
                    number=number,
                    object_id=handle.identity.object_id,
                    mode=DescriptorMode.O_PATH,
                    label=role,
                )
            if handle.synchronizable_fd is not None and number == handle.synchronizable_fd:
                return Descriptor(
                    number=number,
                    object_id=handle.identity.object_id,
                    mode=DescriptorMode.O_RDONLY,
                    label=role,
                )
        raise DescriptorRefused(
            DESCRIPTOR_NOT_REGISTERED,
            str(number),
            "the descriptor was issued neither by this filesystem nor by the "
            "inventory, and an unregistered descriptor is never used as one",
        )

    def _directory_descriptor(self, fd: int) -> Descriptor:
        descriptor = self._descriptor(fd)
        if descriptor.object_id not in self._inventory_object_ids():
            raise DescriptorRefused(
                DESCRIPTOR_NOT_REGISTERED,
                descriptor.label,
                "the descriptor does not refer to a directory this inventory "
                "registered, so it is not one an *at() call may traverse",
            )
        if descriptor.mode is not DescriptorMode.O_PATH:
            raise DescriptorRefused(
                DESCRIPTOR_MODE_REFUSED,
                descriptor.label,
                "the synchronizable descriptor's permitted uses are `fsync` and "
                "`fstat` of itself; traversal is the other descriptor's job, so "
                "a reader can tell the two apart by their use sites",
            )
        return descriptor

    def _inventory_object_ids(self) -> frozenset[str]:
        return frozenset(
            self._inventory.directory(role).identity.object_id
            for role in self._inventory.roles()
        )

    @staticmethod
    def _identity(fd: int) -> str:
        return ObjectIdentity.of(fd).object_id


__all__ = [
    "CONTRACT_GAPS",
    "LISTING_DESCRIPTOR",
    "DESCRIPTOR_ALREADY_REGISTERED",
    "DESCRIPTOR_BARRIER_FAILED",
    "DESCRIPTOR_IDENTITY_MISMATCH",
    "DESCRIPTOR_MODE_REFUSED",
    "DESCRIPTOR_NOT_BOUND",
    "DESCRIPTOR_NOT_REGISTERED",
    "DESCRIPTOR_OBJECT_ABSENT",
    "DESCRIPTOR_OBJECT_EXISTS",
    "DESCRIPTOR_OPEN_REFUSED",
    "DESCRIPTOR_OPERATION_REFUSED",
    "DESCRIPTOR_REFUSALS",
    "DESCRIPTOR_TRANSFER_REFUSED",
    "EXCLUSIVE_PUBLICATION_SUBSTITUTE",
    "FIRST_TRANSFERRED_DESCRIPTOR",
    "DescriptorInventory",
    "DescriptorRefused",
    "DirectoryHandle",
    "ObjectIdentity",
    "PosixFilesystem",
    "TransferEntry",
]
