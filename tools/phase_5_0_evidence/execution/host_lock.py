"""The cooperative host lock of runner contract r6 §5.3, and the reader order
of §5.6, over a real lock inode and real records.

## The adapter r2 withdrew, and what replaced it

Revision 1 proposed `open(O_CREAT|O_EXCL)` on a path in a root-owned directory.
The September 11 review withdrew it: an ordinary participant cannot create or
unlink an entry there, so the protocol's first act was one the protocol's own
identity could not perform. The replacement in r6 §5.3 is a **persistent
provisioned inode** plus `flock`:

* the lock file is created by `systemd-tmpfiles` at boot, from a provisioned
  fragment, and is **never created and never unlinked by a participant**;
* a participant opens it `O_RDWR` — **no `O_CREAT`, no `O_EXCL`** — and takes
  `flock(LOCK_EX)`; and
* **an absent lock refuses.** An absent lock means the host was not
  provisioned, and creating it is a provisioning act rather than a
  participant's.

`flock(2)` associates the lock with the **open file description** and the kernel
releases it when the holder's descriptors close. That is a feature here, and it
is also exactly why the lock cannot be the reservation: a crashed holder's lock
is released whether the run finished or was killed. **The record decides, not
the lock**, and `FREE_LOCK_AUTHORIZES_NOTHING` carries that sentence into every
result this module returns.

## What the session does, in the order §5.6 states it

```text
acquire the lock  →  re-seal the record's parent entry
                  →  re-seal the ledger's parent entry
                  →  read the record's bytes through a descriptor
                  →  parse       (§5.5's bounded schema)
                  →  check order (§5.5's history rules)
                  →  validate    (reservation.validate_lifecycle)
                  →  survey      (§5.11's ledger)
                  →  decide
```

**No participant reads before it re-seals, and no participant writes before it
reads.** `LaboratorySession.admit()` performs exactly that sequence by calling
`lifecycle_storage.read_and_admit`, which is the same function the synthetic
model runs. There is deliberately no second implementation of the decision: a
mechanism with its own copy of the admission rules would be a second reader that
can drift from the first, and every finding from R3-1 to R5-1 is a drift between
two readers of one fact.

## Fail-closed, and the three things that are not evidence

A held lock, an unreadable lock and an unprovisioned lock all refuse. So does an
absent record, a malformed one, a contradictory one, an `ADMITTED` or `RUNNING`
predecessor, an unsettled run and an **absent ledger**. None of the following is
ever sufficient reuse evidence, and each has its own refusal: a free process
lock, an elapsed deadline, a clean wrapper exit, an absent quarantine record.

## What it does not do

It creates nothing, provisions nothing, kills nothing and never breaks a lock.
There is no timeout that takes the lock, no `LOCK_NB` in a loop that gives up
and proceeds, and no path on which a refusal becomes a retry. It reaches no
network, opens no database and starts no process.
"""
from __future__ import annotations

import errno
import fcntl
import os
from dataclasses import dataclass, field

from ..lifecycle_storage import (
    FREE_LOCK_AUTHORIZES_NOTHING,
    Participant,
    SuccessorAdmission,
    read_and_admit,
)
from ..provisioning import LABORATORY_LAYOUT, LaboratoryLayout
from ..reservation import LOCK_LIMITS, LockView, QuarantineRecord
from .descriptors import DescriptorInventory, PosixFilesystem
from .lifecycle_record import ReservationRecord
from .run_ledger import ParticipantRunLedger

#: The refusal a lock operation reports. Fixed, short and safe: an operator sees
#: which rule refused, and never a path, a holder's command line or an
#: operating-system message.
LOCK_ABSENT = "lock-absent"
LOCK_PERMISSION_DENIED = "lock-permission-denied"
LOCK_HELD = "lock-held-by-another-participant"
LOCK_UNREADABLE = "lock-unreadable"
LOCK_NOT_HELD = "lock-not-held-by-this-participant"
LOCK_WRONG_OBJECT_TYPE = "lock-not-a-regular-file"

LOCK_REFUSALS: frozenset[str] = frozenset(
    {
        LOCK_ABSENT,
        LOCK_PERMISSION_DENIED,
        LOCK_HELD,
        LOCK_UNREADABLE,
        LOCK_NOT_HELD,
        LOCK_WRONG_OBJECT_TYPE,
    }
)

#: What the adapter refuses to do, stated where a reader of it will see it.
ADAPTER_REFUSES_TO = (
    "create the lock file. An absent lock means the host was not provisioned, "
    "and provisioning is an operator's act performed out of band.",
    "unlink or replace the lock file. It is a persistent inode with a stable "
    "identity, and a participant that replaced it would be excluding nobody.",
    "break, steal or time out a lock another participant holds. There is no "
    "deadline here, because a deadline is not takeover authority.",
    "retry a refusal. `LOCK_NB` is used once, to distinguish contention from "
    "failure; it is never used in a loop that gives up and proceeds.",
)


class LockRefused(Exception):
    """The cooperative lock will not be taken, with a fixed classification."""

    def __init__(self, classification: str, detail: str = "") -> None:
        if classification not in LOCK_REFUSALS:
            raise ValueError(
                f"{classification!r} is not one of the lock refusals. The "
                "vocabulary is closed so an operator-facing refusal cannot "
                "acquire a new meaning by being raised."
            )
        self.classification = classification
        super().__init__(f"{classification}: {detail}" if detail else classification)


@dataclass(slots=True)
class HostLock:
    """One participant's hold on the provisioned lock inode.

    `wait` chooses between the contract's two permitted behaviours and there is
    no third. `wait=False` takes the lock or refuses with `LOCK_HELD`;
    `wait=True` blocks in `flock(LOCK_EX)` until the holder releases it. Neither
    proceeds past a held lock, which is the rule for all seven participants.
    """

    path: str = LABORATORY_LAYOUT.lock_path
    wait: bool = False
    _fd: int | None = field(default=None, init=False)

    @property
    def held(self) -> bool:
        return self._fd is not None

    def acquire(self) -> None:
        """Open the existing inode and take the exclusive lock, or refuse."""
        if self.held:
            return
        try:
            fd = os.open(self.path, os.O_RDWR | os.O_NOFOLLOW)
        except FileNotFoundError:
            raise LockRefused(
                LOCK_ABSENT,
                "the provisioned lock inode does not exist, so this host was "
                "not provisioned for the reservation protocol. A participant "
                "does not create it",
            ) from None
        except PermissionError:
            raise LockRefused(
                LOCK_PERMISSION_DENIED,
                "the lock exists and this identity may not open it, which is "
                "what a missing group membership looks like",
            ) from None
        except OSError:
            raise LockRefused(LOCK_UNREADABLE) from None

        try:
            if not _is_regular_file(fd):
                raise LockRefused(
                    LOCK_WRONG_OBJECT_TYPE,
                    "the lock's name resolves to something other than a regular "
                    "file, so it is not the provisioned inode",
                )
            flags = fcntl.LOCK_EX if self.wait else fcntl.LOCK_EX | fcntl.LOCK_NB
            try:
                fcntl.flock(fd, flags)
            except OSError as failure:
                if failure.errno in (errno.EWOULDBLOCK, errno.EAGAIN, errno.EACCES):
                    raise LockRefused(
                        LOCK_HELD,
                        "another participant holds the reservation. The rule for "
                        "all seven is wait or refuse, never proceed",
                    ) from None
                raise LockRefused(LOCK_UNREADABLE) from None
        except BaseException:
            os.close(fd)
            raise
        self._fd = fd

    def release(self) -> None:
        """Release and close. Idempotent, and it never raises.

        Releasing the lock is **not** evidence that the run ended. The release
        decision and the participant's completion are published before this is
        reached, and `reservation.release` is what requires their evidence.
        """
        fd, self._fd = self._fd, None
        if fd is None:
            return
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        except OSError:  # pragma: no cover - the close releases it regardless
            pass
        try:
            os.close(fd)
        except OSError:  # pragma: no cover - already closed
            pass

    def view(self) -> LockView:
        """What this participant observed of the lock.

        It reports **free** while this participant holds it, because that is the
        truthful observation from inside the hold: the admission decision the
        view feeds asks whether *another* participant is running, and this one
        has already excluded that by holding the lock. A participant that does
        not hold it never reaches an admission decision at all — `acquire()`
        raised first.
        """
        if not self.held:
            raise LockRefused(
                LOCK_NOT_HELD,
                "this participant does not hold the lock, so it has made no "
                "observation of it and must not supply one",
            )
        return LockView()

    def __enter__(self) -> "HostLock":
        self.acquire()
        return self

    def __exit__(self, *_exception: object) -> None:
        self.release()


def _is_regular_file(fd: int) -> bool:
    import stat

    return stat.S_ISREG(os.fstat(fd).st_mode)


@dataclass(slots=True)
class LaboratorySession:
    """One participant's whole pass: lock, re-seal, read, decide.

    It assembles the real stores over `PosixFilesystem` and hands them to
    `lifecycle_storage.read_and_admit`, which is the decision. The assembly is
    this module's job; the decision is emphatically not, and there is no rule
    here that the synthetic model does not also apply.
    """

    participant: Participant
    host: str
    target_identity: str
    read_by: str
    read_at: str
    layout: LaboratoryLayout = LABORATORY_LAYOUT
    reservation_id: str = ""
    quarantine: QuarantineRecord | None = None
    wait_for_lock: bool = False
    _lock: HostLock | None = field(default=None, init=False)
    _inventory: DescriptorInventory | None = field(default=None, init=False)
    _record: ReservationRecord | None = field(default=None, init=False)
    _ledger: ParticipantRunLedger | None = field(default=None, init=False)

    # -- lifetime -------------------------------------------------------------

    def open(self) -> None:
        """Take the lock, then hold the four descriptors the pass needs.

        The lock comes **first**. Opening the record's directory before the lock
        would be reading state a concurrent participant may be publishing into.
        """
        if self._lock is not None:
            return
        lock = HostLock(path=self.layout.lock_path, wait=self.wait_for_lock)
        lock.acquire()
        inventory = DescriptorInventory()
        try:
            laboratory = inventory.open_provisioned_root(
                "laboratory", self.layout.laboratory_directory
            )
            runs = inventory.adopt_directory(
                parent_role="laboratory",
                name=self.layout.runs_directory_name,
                role="runs",
            )
        except BaseException:
            inventory.close()
            lock.release()
            raise
        filesystem = PosixFilesystem(inventory)
        self._lock = lock
        self._inventory = inventory
        self._record = ReservationRecord(
            filesystem=filesystem,
            directory_object_id=laboratory.identity.object_id,
            name=self.layout.record_name,
            host=self.host,
            target_identity=self.target_identity,
        )
        # **The ledger the session hands out is `ParticipantRunLedger`**, not a
        # bare `RunLedger`: one object owns the begin/complete/recover/survey
        # protocol for all seven participants, and the admission decision is
        # given the same object the integration points write through. A session
        # that built one ledger and handed the decision another would be the
        # two-readers drift every finding since R3-1 is about.
        self._ledger = ParticipantRunLedger(
            filesystem=filesystem,
            directory_object_id=runs.identity.object_id,
            host=self.host,
            target_identity=self.target_identity,
            label=(
                f"{self.layout.laboratory_directory}/"
                f"{self.layout.runs_directory_name}"
            ),
        )

    def close(self) -> None:
        """Release the descriptors, then the lock, in that order. Never raises."""
        if self._inventory is not None:
            self._inventory.close()
        self._inventory = None
        self._record = None
        self._ledger = None
        if self._lock is not None:
            self._lock.release()
        self._lock = None

    @property
    def holds_lock(self) -> bool:
        """Whether this session is holding the cooperative lock **right now**.

        It exists because a release's evidence names the lock's holder, and the
        only honest answer to *"who holds it"* is one the holder derives from
        its own open descriptor. A caller that supplied the answer would be
        asserting the very fact the release is checking — and `release()`
        refuses a release whose lock is held by somebody else precisely so that
        an early release cannot pass for a held one.
        """
        lock = self._lock
        return lock is not None and lock.held

    def __enter__(self) -> "LaboratorySession":
        self.open()
        return self

    def __exit__(self, *_exception: object) -> None:
        self.close()

    # -- the objects the pass writes through ---------------------------------

    @property
    def record(self) -> ReservationRecord:
        if self._record is None:
            raise LockRefused(
                LOCK_NOT_HELD,
                "the session is not open, so no record is held and nothing may "
                "be read or published through it",
            )
        return self._record

    @property
    def ledger(self) -> ParticipantRunLedger:
        if self._ledger is None:
            raise LockRefused(
                LOCK_NOT_HELD,
                "the session is not open, so no ledger is held and no run may "
                "be begun, completed or surveyed",
            )
        return self._ledger

    # -- the decision ---------------------------------------------------------

    def admit(self) -> SuccessorAdmission:
        """§5.6's order, through the one shared admission function.

        Every refusal it can return is named in r6 §5.9 and none of them is
        recoverable here: a refused admission is a refusal, not a retry.
        """
        lock = self._lock
        if lock is None:
            raise LockRefused(
                LOCK_NOT_HELD,
                "a participant decides admission while holding the lock, and "
                "this session holds none",
            )
        return read_and_admit(
            participant=self.participant,
            record=self.record.store,
            ledger=self.ledger.ledger,
            lock=lock.view(),
            host=self.host,
            target_identity=self.target_identity,
            read_by=self.read_by,
            read_at=self.read_at,
            reservation_id=self.reservation_id,
            quarantine=self.quarantine,
        )


__all__ = [
    "ADAPTER_REFUSES_TO",
    "FREE_LOCK_AUTHORIZES_NOTHING",
    "LOCK_ABSENT",
    "LOCK_HELD",
    "LOCK_LIMITS",
    "LOCK_NOT_HELD",
    "LOCK_PERMISSION_DENIED",
    "LOCK_REFUSALS",
    "LOCK_UNREADABLE",
    "LOCK_WRONG_OBJECT_TYPE",
    "HostLock",
    "LaboratorySession",
    "LockRefused",
]
