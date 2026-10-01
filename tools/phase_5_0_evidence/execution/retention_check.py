"""RP-11's read-only verification of a retained capture root: X-4 and B0-RA.

Two entry points share one verifier:

* `verify_final_state` re-applies **X-4** (§9.5.2) to a pass's own root after
  its X-3 attempt succeeded. The capture mechanism calls it to decide the X-4
  validity line of its handback.
* `RetentionCheck` is **B0-RA** (§7.1): before Pass B creates its root, it
  authenticates the digest-pinned Pass A handback, takes the fixed contract
  fields from it, requires the supplied Pass A root to equal the recorded root
  byte for byte, re-derives the final state's SHA-256, re-applies X-4, and
  compares one complete recursive enumeration of the root with the accounted
  set in both directions. It runs once. A second `run()` refuses.

## What it may do, and what it cannot

It lists names and object types, and it reads and digests the bytes of
**admitted** objects only: the final state, its chain, the listed records and
the stream files they bind. An admitted record or index state is read through
its **final** name; its staging name is proved to be the same inode by `lstat`
metadata, which proves the same bytes without a second read. `ReadOnlyFilesystem` is the whole of its access,
and it has no operation that writes, creates, renames, links, truncates,
removes or changes a mode, owner or timestamp; `PosixReadOnlyFilesystem` opens
every file and directory `O_RDONLY`. For an unadmitted object and for a
recorded subdirectory it establishes presence, exact relative name and type —
by `lstat`, never by opening — and never unchanged bytes or metadata. An
unadmitted object is never opened, read or digested.

Reading bytes updates access times where the filesystem's mount options say
so. That is a property of reading, which the contract permits, and nothing
here depends on or reports an access time.

## How names are resolved

Nothing is resolved from a path string after the root. The root itself is
opened one component at a time from `/` with `O_NOFOLLOW|O_DIRECTORY`, each
relative to the previous descriptor. Every entry is `lstat`ed relative to its
directory's descriptor and never followed; a directory is descended into by
`openat(O_NOFOLLOW|O_DIRECTORY)` and its `fstat` must be the identity the
`lstat` reported. An admitted file is opened `O_NOFOLLOW|O_NONBLOCK` relative
to the descriptors of its verified ancestors, and its `fstat` must again be the
enumerated identity. No lexical normalization and no `resolve()` is involved.

## What stops the check

* a symbolic link, FIFO, socket, device or any type no category expects — they
  are recorded by type and never followed or opened, and condition 5 then finds
  them unaccounted or mismatched;
* a **path alias**, with exactly one narrow exception (C-P5.0-R5-RP11-I1-R3).
  A regular file may have link count two, and share its inode with one other
  entry, **only** when the two entries are the recorded staging and final name
  of one object. For an **admitted** pair X-4 then requires both names present,
  one inode equal to the recorded `(st_dev, st_ino)`, regular, owned by the
  recorded `owner_uid`, mode `0600`, link count two and — through the final
  name — the recorded digest (`pair-*` reasons). For a pair *F* records as
  **unadmitted** (maintainer Option-1 decision
  `C-P5.0-R5-RP11-I1-R3-D2`, 2026-09-28) only metadata is compared:
  both recorded names present, regular, one inode between them, link count two,
  shared with no other name; nothing is opened, read or digested, and no
  identity is compared, because none is recorded. Everything else — a third
  link, a link count above two, a cross-object alias, one pair member's inode
  shared with anything but its partner, an unrecorded name at link count two,
  a directory whose identity was already seen — is `path-alias`;
* an entry on another device: the root was **escaped** through a mount;
* a name component that is empty, `.`, `..`, or contains `/` or NUL, or a
  listing that names one entry twice: an **ambiguous name**;
* **change during enumeration or verification**: each directory's identity,
  modification time, change time and link count are compared before and after
  it is listed; each admitted file's identity, size and times are compared with
  the enumeration and before and after it is read; and after every digest the
  whole tree is enumerated a **second** time and must equal the first exactly,
  and the root path is re-walked and must still reach the same directory;
* any exception at all: an **incomplete** enumeration, digest, parse or
  comparison.

## The residual this does not close

The two enumerations and the per-object time comparisons detect a change that
alters a name, a type, an identity, a size or a timestamp between the first
listing and the last. A change that alters none of those — a same-size
rewrite of an admitted file between its read and the second enumeration that
also restores its modification and change times — cannot be made by an
unprivileged process: setting `st_ctime` is not possible from user space, and
any write moves it. The check therefore relies on the kernel's change-time
update, on the operator's account owning the `0700` root, and on the
filesystem's timestamp granularity being finer than the interval between two
changes it must tell apart. It establishes retention **at the moment of the
check only**, as B0-RA states, and monitors nothing afterwards.
"""
from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import dataclass
from typing import Protocol

from ..capture_contract import (
    FILE_MODE,
    FINAL,
    OPEN,
    X3_SUCCEEDED,
    X4_VALID,
    AccountedObject,
    CaptureContractRefused,
    CaptureRecord,
    IndexState,
    ObjectType,
    RelativeName,
    accounted_objects,
    final_state_number,
    is_final_state_name,
    is_record_name,
    object_type_of_mode,
    open_state_name,
    parse_capture_root,
    parse_handback_binding,
    require_identifier,
    require_sha256,
)
from ..errors import HarnessError

#: The conditions, numbered as B0-RA numbers them. `0` is the handback itself,
#: which precedes the five.
CONDITION_HANDBACK = 0
CONDITION_ROOT_EQUALITY = 1
CONDITION_PRESENCE = 2
CONDITION_FINAL_DIGEST = 3
CONDITION_X4 = 4
CONDITION_NAME_AGREEMENT = 5

#: Stated on every result, passed or failed.
EVIDENTIARY_LIMIT = (
    "For each listed record, bound stream file and index state, the bytes were "
    "re-digested through its final name, and its staging name was proved to be "
    "the same recorded inode by metadata. For an unadmitted object and a "
    "recorded subdirectory, only "
    "presence at the recorded relative name with the recorded object type was "
    "established; no unadmitted object was opened, read or digested, and its "
    "bytes and metadata are not established. Retention is established at the "
    "moment of the check only."
)


class RetentionRefused(HarnessError):
    """B0-RA was asked to run a second time."""


class ReadOnlyFilesystem(Protocol):
    """Everything the verifier may do. There is no write here, by construction."""

    def read_file(self, path: str) -> bytes: ...

    def open_directory(self, dir_fd: int | None, name: bytes) -> int: ...

    def list_names(self, dir_fd: int) -> tuple[bytes, ...]: ...

    def lstat_at(self, dir_fd: int, name: bytes) -> os.stat_result: ...

    def open_file(self, dir_fd: int, name: bytes) -> int: ...

    def fstat(self, fd: int) -> os.stat_result: ...

    def read_all(self, fd: int) -> bytes: ...

    def close(self, fd: int) -> None: ...


_READ_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_NOCTTY | os.O_CLOEXEC
_DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC


class PosixReadOnlyFilesystem:
    """The real filesystem, opened read-only and never followed."""

    def read_file(self, path: str) -> bytes:
        fd = os.open(path, _READ_FLAGS)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise OSError("not a regular file")
            return self.read_all(fd)
        finally:
            os.close(fd)

    def open_directory(self, dir_fd: int | None, name: bytes) -> int:
        if dir_fd is None:
            if name != b"/":
                raise ValueError("only `/` is opened without a directory descriptor")
            return os.open(b"/", _DIRECTORY_FLAGS)
        return os.open(name, _DIRECTORY_FLAGS, dir_fd=dir_fd)

    def list_names(self, dir_fd: int) -> tuple[bytes, ...]:
        return tuple(os.fsencode(name) for name in os.listdir(dir_fd))

    def lstat_at(self, dir_fd: int, name: bytes) -> os.stat_result:
        return os.stat(name, dir_fd=dir_fd, follow_symlinks=False)

    def open_file(self, dir_fd: int, name: bytes) -> int:
        return os.open(name, _READ_FLAGS, dir_fd=dir_fd)

    def fstat(self, fd: int) -> os.stat_result:
        return os.fstat(fd)

    def read_all(self, fd: int) -> bytes:
        chunks: list[bytes] = []
        offset = 0
        while True:
            chunk = os.pread(fd, 1 << 20, offset)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
            offset += len(chunk)

    def close(self, fd: int) -> None:
        os.close(fd)


@dataclass(frozen=True, slots=True)
class RetentionResult:
    """The outcome, with every name in either set difference."""

    passed: bool
    failed_condition: int | None
    reason: str
    observed_not_recorded: tuple[str, ...] = ()
    recorded_not_observed: tuple[str, ...] = ()
    type_mismatches: tuple[str, ...] = ()
    evidentiary_limit: str = EVIDENTIARY_LIMIT


@dataclass(frozen=True, slots=True)
class _Facts:
    object_type: ObjectType
    device: int
    inode: int
    links: int
    size: int
    mtime_ns: int
    ctime_ns: int
    owner: int
    permissions: int

    @classmethod
    def of(cls, facts: os.stat_result) -> "_Facts":
        return cls(
            object_type=object_type_of_mode(facts.st_mode),
            device=facts.st_dev,
            inode=facts.st_ino,
            links=facts.st_nlink,
            size=facts.st_size,
            mtime_ns=facts.st_mtime_ns,
            ctime_ns=facts.st_ctime_ns,
            owner=facts.st_uid,
            permissions=stat.S_IMODE(facts.st_mode),
        )

    @property
    def identity(self) -> tuple[int, int]:
        return (self.device, self.inode)


class _Stop(Exception):
    def __init__(
        self,
        condition: int,
        reason: str,
        *,
        observed_not_recorded: tuple[str, ...] = (),
        recorded_not_observed: tuple[str, ...] = (),
        type_mismatches: tuple[str, ...] = (),
    ) -> None:
        super().__init__(reason)
        self.condition = condition
        self.reason = reason
        self.observed_not_recorded = observed_not_recorded
        self.recorded_not_observed = recorded_not_observed
        self.type_mismatches = type_mismatches

    def result(self) -> RetentionResult:
        return RetentionResult(
            passed=False,
            failed_condition=self.condition,
            reason=self.reason,
            observed_not_recorded=self.observed_not_recorded,
            recorded_not_observed=self.recorded_not_observed,
            type_mismatches=self.type_mismatches,
        )


class _Verifier:
    """One verification of one root. Holds only descriptors it opened itself."""

    def __init__(self, filesystem: ReadOnlyFilesystem) -> None:
        self._fs = filesystem
        self._condition = CONDITION_PRESENCE
        self._root_fd: int | None = None
        self._root_facts: _Facts | None = None
        self._first: dict[RelativeName, _Facts] = {}

    @property
    def condition(self) -> int:
        return self._condition

    # -- the root --------------------------------------------------------------

    def _walk_root(self, capture_root: str) -> int:
        components = parse_capture_root(capture_root)
        current = self._fs.open_directory(None, b"/")
        try:
            for component in components:
                following = self._fs.open_directory(current, os.fsencode(component))
                self._fs.close(current)
                current = following
        except Exception:
            self._close_quietly(current)
            raise
        return current

    def open_root(self, capture_root: str) -> None:
        self._condition = CONDITION_PRESENCE
        try:
            fd = self._walk_root(capture_root)
        except (OSError, ValueError):
            raise _Stop(CONDITION_PRESENCE, "root-absent-or-not-a-directory") from None
        self._root_fd = fd
        facts = _Facts.of(self._fs.fstat(fd))
        if facts.object_type is not ObjectType.DIRECTORY:
            raise _Stop(CONDITION_PRESENCE, "root-not-a-directory")
        self._root_facts = facts

    def close(self) -> None:
        if self._root_fd is not None:
            self._close_quietly(self._root_fd)
            self._root_fd = None

    # -- enumeration -----------------------------------------------------------

    def enumerate(self) -> dict[RelativeName, _Facts]:
        """One complete recursive enumeration, or a `_Stop`."""
        assert self._root_fd is not None and self._root_facts is not None
        root_facts = self._root_facts
        entries: dict[RelativeName, _Facts] = {}
        seen_directories = {root_facts.identity}
        seen_identities: dict[tuple[int, int], list[RelativeName]] = {}
        pending: list[tuple[int, RelativeName | None, _Facts, bool]] = [
            (self._root_fd, None, root_facts, False)
        ]
        while pending:
            fd, prefix, expected, owned = pending.pop()
            try:
                before = _Facts.of(self._fs.fstat(fd))
                if before != expected and prefix is not None:
                    raise _Stop(CONDITION_NAME_AGREEMENT, "changed-during-enumeration")
                if before.identity != expected.identity:
                    raise _Stop(CONDITION_NAME_AGREEMENT, "changed-during-enumeration")
                names = self._fs.list_names(fd)
                if len(names) != len(set(names)):
                    raise _Stop(CONDITION_NAME_AGREEMENT, "ambiguous-name")
                for component in sorted(names):
                    try:
                        name = (
                            prefix.child(component)
                            if prefix is not None
                            else RelativeName((component,))
                        )
                    except CaptureContractRefused:
                        raise _Stop(CONDITION_NAME_AGREEMENT, "ambiguous-name") from None
                    facts = _Facts.of(self._fs.lstat_at(fd, component))
                    if facts.device != root_facts.device:
                        raise _Stop(CONDITION_NAME_AGREEMENT, "escapes-the-root")
                    if facts.identity in seen_directories:
                        raise _Stop(CONDITION_NAME_AGREEMENT, "path-alias")
                    if facts.object_type is ObjectType.REGULAR:
                        # One or two names only. Whether a second name is the
                        # recorded partner is decided against R, by `_aliases`.
                        if facts.links not in (1, 2):
                            raise _Stop(CONDITION_NAME_AGREEMENT, "path-alias")
                        if len(seen_identities.get(facts.identity, ())) >= facts.links:
                            raise _Stop(CONDITION_NAME_AGREEMENT, "path-alias")
                    elif facts.identity in seen_identities:
                        raise _Stop(CONDITION_NAME_AGREEMENT, "path-alias")
                    seen_identities.setdefault(facts.identity, []).append(name)
                    entries[name] = facts
                    if facts.object_type is ObjectType.DIRECTORY:
                        child = self._fs.open_directory(fd, component)
                        child_facts = _Facts.of(self._fs.fstat(child))
                        if child_facts != facts:
                            self._close_quietly(child)
                            raise _Stop(CONDITION_NAME_AGREEMENT, "changed-during-enumeration")
                        seen_directories.add(facts.identity)
                        pending.append((child, name, facts, True))
                after = _Facts.of(self._fs.fstat(fd))
                if after != before:
                    raise _Stop(CONDITION_NAME_AGREEMENT, "changed-during-enumeration")
            except Exception:
                for item in pending:
                    if item[3]:
                        self._close_quietly(item[0])
                if owned:
                    self._close_quietly(fd)
                raise
            if owned:
                self._close_quietly(fd)
        return entries

    # -- reading an admitted object --------------------------------------------

    def read_admitted(self, name: RelativeName, snapshot: dict[RelativeName, _Facts]) -> bytes:
        """The bytes of an admitted regular file, bound to its enumerated identity."""
        assert self._root_fd is not None
        expected = snapshot.get(name)
        if expected is None or expected.object_type is not ObjectType.REGULAR:
            raise _Stop(self._condition, "admitted-object-absent-or-not-regular")
        opened: list[int] = []
        try:
            current = self._root_fd
            for depth in range(1, len(name.components)):
                directory = RelativeName(name.components[:depth])
                current = self._fs.open_directory(current, name.components[depth - 1])
                opened.append(current)
                if _Facts.of(self._fs.fstat(current)) != snapshot.get(directory):
                    raise _Stop(CONDITION_NAME_AGREEMENT, "changed-during-verification")
            fd = self._fs.open_file(current, name.components[-1])
            opened.append(fd)
            before = _Facts.of(self._fs.fstat(fd))
            if before != expected:
                raise _Stop(CONDITION_NAME_AGREEMENT, "changed-during-verification")
            data = self._fs.read_all(fd)
            after = _Facts.of(self._fs.fstat(fd))
            if after != before or len(data) != before.size:
                raise _Stop(CONDITION_NAME_AGREEMENT, "changed-during-verification")
            return data
        finally:
            for fd in reversed(opened):
                self._close_quietly(fd)

    # -- X-4 -------------------------------------------------------------------

    def verify(
        self,
        *,
        capture_root: str,
        final_state: str,
        final_sha256: str,
        pass_id: str,
        bidirectional: bool,
    ) -> None:
        self.open_root(capture_root)
        self._condition = CONDITION_NAME_AGREEMENT
        first = self.enumerate()
        self._first = first

        self._condition = CONDITION_PRESENCE
        final_name = RelativeName.created(final_state)
        present = first.get(final_name)
        if present is None or present.object_type is not ObjectType.REGULAR:
            raise _Stop(CONDITION_PRESENCE, "final-state-absent")

        self._condition = CONDITION_FINAL_DIGEST
        final_bytes = self.read_admitted(final_name, first)
        if hashlib.sha256(final_bytes).hexdigest() != final_sha256:
            raise _Stop(CONDITION_FINAL_DIGEST, "final-state-digest-mismatch")

        self._condition = CONDITION_X4
        finals = [name for name in first if is_final_state_name(name)]
        if len(finals) != 1:
            raise _Stop(CONDITION_X4, "not-the-only-final-state")
        try:
            final = IndexState.from_bytes(final_bytes)
        except CaptureContractRefused:
            raise _Stop(CONDITION_X4, "final-state-invalid") from None
        if (
            final.status != FINAL
            or final.name != final_state
            or final.state_number != final_state_number(final_state)
            or final.capture_root != capture_root
            or final.pass_id != pass_id
        ):
            raise _Stop(CONDITION_X4, "final-state-does-not-match-its-binding")

        expected_digest = final.previous_state_sha256
        chain: list[IndexState] = []
        for number in reversed(range(final.state_number)):
            state_name = RelativeName.created(open_state_name(number))
            if state_name not in first:
                raise _Stop(CONDITION_X4, "chain-state-absent")
            data = self.read_admitted(state_name, first)
            if hashlib.sha256(data).hexdigest() != expected_digest:
                raise _Stop(CONDITION_X4, "chain-broken")
            try:
                state = IndexState.from_bytes(data)
            except CaptureContractRefused:
                raise _Stop(CONDITION_X4, "chain-state-invalid") from None
            if (
                state.status != OPEN
                or state.state_number != number
                or state.pass_id != final.pass_id
                or state.capture_root != final.capture_root
                or state.tool_sha256 != final.tool_sha256
                or state.owner_uid != final.owner_uid
                or state.records != final.records[:number]
            ):
                raise _Stop(CONDITION_X4, "chain-inconsistent")
            chain.insert(0, state)
            expected_digest = state.previous_state_sha256

        records: list[CaptureRecord] = []
        for entry in final.records:
            record_name = RelativeName.created(entry.name)
            if record_name not in first:
                raise _Stop(CONDITION_X4, "record-absent")
            data = self.read_admitted(record_name, first)
            if hashlib.sha256(data).hexdigest() != entry.sha256:
                raise _Stop(CONDITION_X4, "record-digest-mismatch")
            try:
                record = CaptureRecord.from_bytes(data)
            except CaptureContractRefused:
                raise _Stop(CONDITION_X4, "record-invalid") from None
            if record.capture_seq != entry.capture_seq or record.pass_id != final.pass_id:
                raise _Stop(CONDITION_X4, "record-does-not-match-its-entry")
            for binding in (record.stdout, record.stderr):
                stream = RelativeName.created(binding.name)
                if stream not in first:
                    raise _Stop(CONDITION_X4, "stream-absent")
                data = self.read_admitted(stream, first)
                if len(data) != binding.size or hashlib.sha256(data).hexdigest() != binding.sha256:
                    raise _Stop(CONDITION_X4, "stream-digest-mismatch")
            records.append(record)

        try:
            accounted = accounted_objects(final, chain, records)
        except CaptureContractRefused:
            raise _Stop(CONDITION_NAME_AGREEMENT, "duplicate-accounted-name") from None
        self._admitted_pairs(first, accounted, final.owner_uid)
        unaccounted_records = sorted(
            name.display for name in first if is_record_name(name) and name not in accounted
        )
        if unaccounted_records:
            raise _Stop(
                CONDITION_X4,
                "published-record-not-accounted",
                observed_not_recorded=tuple(unaccounted_records),
            )

        self._condition = CONDITION_NAME_AGREEMENT
        _aliases(first, accounted)

        if bidirectional:
            self._condition = CONDITION_NAME_AGREEMENT
            observed_not_recorded = tuple(
                sorted(name.display for name in first if name not in accounted)
            )
            recorded_not_observed = tuple(
                sorted(name.display for name in accounted if name not in first)
            )
            type_mismatches = tuple(
                sorted(
                    f"{name.display}: expected {accounted[name].object_type.value}, "
                    f"observed {facts.object_type.value}"
                    for name, facts in first.items()
                    if name in accounted and accounted[name].object_type is not facts.object_type
                )
            )
            if observed_not_recorded or recorded_not_observed or type_mismatches:
                raise _Stop(
                    CONDITION_NAME_AGREEMENT,
                    "name-sets-disagree",
                    observed_not_recorded=observed_not_recorded,
                    recorded_not_observed=recorded_not_observed,
                    type_mismatches=type_mismatches,
                )

        self._condition = CONDITION_NAME_AGREEMENT
        if self.enumerate() != first:
            raise _Stop(CONDITION_NAME_AGREEMENT, "changed-during-verification")
        try:
            again = self._walk_root(capture_root)
        except (OSError, ValueError):
            raise _Stop(CONDITION_PRESENCE, "root-replaced-during-verification") from None
        try:
            assert self._root_facts is not None
            if _Facts.of(self._fs.fstat(again)).identity != self._root_facts.identity:
                raise _Stop(CONDITION_PRESENCE, "root-replaced-during-verification")
        finally:
            self._close_quietly(again)

    def _admitted_pairs(
        self,
        first: dict[RelativeName, _Facts],
        accounted: dict[RelativeName, AccountedObject],
        owner_uid: int,
    ) -> None:
        """X-4 for every admitted pair: both names, the recorded inode, link
        count two, regular, the recorded owner and `0600`. The bytes were
        already digested through the final name, and one inode is one content."""
        self._condition = CONDITION_X4
        for name, item in sorted(accounted.items()):
            if not item.admitted_pair:
                continue
            facts = first.get(name)
            if facts is None:
                raise _Stop(CONDITION_X4, "pair-member-absent", recorded_not_observed=(name.display,))
            if facts.object_type is not ObjectType.REGULAR:
                raise _Stop(CONDITION_X4, "pair-member-not-regular")
            if facts.identity != item.identity:
                raise _Stop(CONDITION_X4, "pair-identity-mismatch")
            if facts.links != 2:
                raise _Stop(CONDITION_X4, "pair-link-count")
            if facts.owner != owner_uid or facts.permissions != FILE_MODE:
                raise _Stop(CONDITION_X4, "pair-owner-or-mode")

    def _close_quietly(self, fd: int) -> None:
        try:
            self._fs.close(fd)
        except (OSError, ValueError):
            pass


def _aliases(
    first: dict[RelativeName, _Facts], accounted: dict[RelativeName, AccountedObject]
) -> None:
    """The one alias exception, and nothing wider.

    Every regular file's inode is reached by one name at link count one, or by
    exactly two names at link count two that are one another's recorded
    partners in *R*. An accounted pair whose two names are both present must
    share one inode — for an unadmitted pair this is metadata only: nothing is
    opened, read or digested.
    """
    groups: dict[tuple[int, int], list[RelativeName]] = {}
    for name, facts in first.items():
        if facts.object_type is ObjectType.REGULAR:
            groups.setdefault(facts.identity, []).append(name)
    for identity, names in groups.items():
        links = first[names[0]].links
        if len(names) == 1:
            if links != 1:
                raise _Stop(CONDITION_NAME_AGREEMENT, "path-alias")
            continue
        a, b = names
        if (
            links != 2
            or first[b].links != 2
            or a not in accounted
            or b not in accounted
            or accounted[a].partner != b  # partnership is symmetric by construction
        ):
            raise _Stop(CONDITION_NAME_AGREEMENT, "path-alias")
    for name, item in accounted.items():
        partner = item.partner
        if partner is None or name not in first or partner not in first:
            continue
        if first[name].identity != first[partner].identity:
            raise _Stop(CONDITION_NAME_AGREEMENT, "pair-divergent")


def _run_verifier(
    filesystem: ReadOnlyFilesystem,
    *,
    capture_root: str,
    final_state: str,
    final_sha256: str,
    pass_id: str,
    bidirectional: bool,
) -> RetentionResult:
    verifier = _Verifier(filesystem)
    try:
        verifier.verify(
            capture_root=capture_root,
            final_state=final_state,
            final_sha256=final_sha256,
            pass_id=pass_id,
            bidirectional=bidirectional,
        )
    except _Stop as stop:
        return stop.result()
    except Exception as error:  # noqa: BLE001 - an incomplete check is a stop
        return RetentionResult(
            passed=False,
            failed_condition=verifier.condition,
            reason=f"verification-incomplete:{type(error).__name__}",
        )
    finally:
        verifier.close()
    return RetentionResult(passed=True, failed_condition=None, reason="retained")


def verify_final_state(
    filesystem: ReadOnlyFilesystem,
    *,
    capture_root: str,
    final_state: str,
    final_sha256: str,
    pass_id: str,
) -> RetentionResult:
    """X-4 over a pass's own root, after its X-3 attempt succeeded.

    Barrier success is the caller's knowledge — it made the attempt — and is not
    re-observed here. Everything else X-4 requires is checked against the bytes
    on disk: *F* is the only final state, its chain is intact back to *I*-0, its
    record list equals the last open state's, every listed record and bound
    stream file exists with its digest, every published record under the
    root is listed in *F* or named in it as unadmitted, and every admitted
    record and state is its recorded staging/final pair on the recorded inode,
    with no alias beyond the one exception the module docstring states.
    """
    return _run_verifier(
        filesystem,
        capture_root=capture_root,
        final_state=final_state,
        final_sha256=final_sha256,
        pass_id=pass_id,
        bidirectional=False,
    )


class RetentionCheck:
    """B0-RA: the one-shot, non-mutating Pass A retention verification."""

    def __init__(
        self,
        *,
        handback_path: str,
        handback_sha256: str,
        capture_root: str,
        expected_pass_id: str,
        filesystem: ReadOnlyFilesystem | None = None,
    ) -> None:
        require_sha256(handback_sha256, "handback_sha256")
        require_identifier(expected_pass_id, "expected_pass_id")
        self._handback_path = handback_path
        self._handback_sha256 = handback_sha256
        self._capture_root = capture_root
        self._expected_pass_id = expected_pass_id
        self._filesystem = filesystem if filesystem is not None else PosixReadOnlyFilesystem()
        self._consumed = False

    def run(self) -> RetentionResult:
        if self._consumed:
            raise RetentionRefused("B0-RA runs once and is never retried (§11.3)")
        self._consumed = True
        try:
            return self._run_once()
        except Exception as error:  # noqa: BLE001 - an incomplete check is a stop
            return RetentionResult(
                passed=False,
                failed_condition=CONDITION_HANDBACK,
                reason=f"verification-incomplete:{type(error).__name__}",
            )

    def _run_once(self) -> RetentionResult:
        try:
            data = self._filesystem.read_file(self._handback_path)
        except (OSError, ValueError) as error:
            return RetentionResult(
                passed=False,
                failed_condition=CONDITION_HANDBACK,
                reason=f"handback-unreadable:{type(error).__name__}",
            )
        if hashlib.sha256(data).hexdigest() != self._handback_sha256:
            return _stopped(CONDITION_HANDBACK, "handback-digest-mismatch")
        try:
            binding = parse_handback_binding(data)
        except CaptureContractRefused as refusal:
            return _stopped(CONDITION_HANDBACK, f"handback-binding-{refusal.classification}")
        if binding.pass_id != self._expected_pass_id:
            return _stopped(CONDITION_HANDBACK, "handback-pass-id-mismatch")
        if binding.x3_outcome != X3_SUCCEEDED:
            return _stopped(CONDITION_HANDBACK, "handback-records-no-successful-x3")
        if binding.x4_validity != X4_VALID:
            return _stopped(CONDITION_HANDBACK, "handback-records-no-valid-x4")
        if binding.final_state is None or binding.capture_index_sha256 is None:
            return _stopped(CONDITION_HANDBACK, "handback-records-no-final-state")
        supplied = self._capture_root
        if not isinstance(supplied, str) or os.fsencode(supplied) != os.fsencode(
            binding.capture_root
        ):
            return _stopped(CONDITION_ROOT_EQUALITY, "capture-root-differs-from-the-record")
        return _run_verifier(
            self._filesystem,
            capture_root=binding.capture_root,
            final_state=binding.final_state,
            final_sha256=binding.capture_index_sha256,
            pass_id=binding.pass_id,
            bidirectional=True,
        )


def _stopped(condition: int, reason: str) -> RetentionResult:
    return RetentionResult(passed=False, failed_condition=condition, reason=reason)


__all__ = [
    "CONDITION_FINAL_DIGEST",
    "CONDITION_HANDBACK",
    "CONDITION_NAME_AGREEMENT",
    "CONDITION_PRESENCE",
    "CONDITION_ROOT_EQUALITY",
    "CONDITION_X4",
    "EVIDENTIARY_LIMIT",
    "PosixReadOnlyFilesystem",
    "ReadOnlyFilesystem",
    "RetentionCheck",
    "RetentionRefused",
    "RetentionResult",
    "verify_final_state",
]
