"""RP-11's durable storage: the capture root, its barriers and its publications.

This module owns everything RP-11 writes: the exclusive creation of a pass's
capture root and its fixed subdirectories (C-6, X-1), the exclusive creation of
an act's two stream files (C-2), their completion and barriers (P-2, P-3), their
digests (P-4), and the publication of a record or an index state (P-5 … P-8,
X-1 … X-3). It starts no process — `boundary.StreamCaptureLauncher` does that —
and it validates no retained evidence — `retention_check` does that.

## One narrow seam, with a stage label on every call

Every filesystem operation goes through `CaptureFilesystem`, and every call
carries a `stage` label naming the contract step it performs (`P-6:file-barrier`,
`X-2:publish`, …). The production implementation, `PosixCaptureFilesystem`,
ignores the label. A test wraps it and fails, or interrupts, exactly one labelled
stage, deterministically, while every other call still reaches the real
filesystem. That is how the suite proves each stage's failure behaviour without
a production path that has a test mode.

## What a failure means here

An `OSError` from a stage becomes `StoreFailure(stage, classification)`. The
store never retries a stage, never repeats a barrier, never renames, rewrites,
truncates or removes anything, and never republishes. After a failure it only
answers one question for the final state: **which names does it know exist?**
A name is known when the call that created it returned success, or when a
creating call failed and a no-follow `lstat` of that exact name shows a regular
file whose identity is the one this store was creating. A creating call that
failed before any entry existed leaves no known name, so it is never recorded as
an unadmitted object (§9.5.3). An entry that already existed at a name the store
was about to create — `EEXIST` — is not this store's and is never recorded:
B0-RA then finds it unaccounted and stops, which is the fail-closed direction.

## Interruption

`CaptureInterrupted` models the mechanism or the repository host stopping in
the middle of a stage (C-15). It is a `BaseException`, so no `except Exception`
in RP-11 can absorb it, and nothing in this module catches it. In production it
is never raised: a real crash simply ends the process. It exists so the suite
can show that after an interruption no further filesystem call is made.

## The creation-time checks

* **The root.** Parsed by `capture_contract.parse_capture_root` (absolute, no
  `.`/`..`/empty component, a conservative character set). Every ancestor is
  opened one component at a time from `/`, relative to the previous descriptor,
  with `O_NOFOLLOW|O_DIRECTORY`: a symbolic link anywhere on the path refuses.
  No lexical normalization and no `resolve()` is used as the boundary.
* **Forbidden locations (C-6).** The root may not lie within `/tmp`, within the
  worktree, or overlap another pass's root. Checked lexically on the parsed
  components **and** by identity: the `(st_dev, st_ino)` of every ancestor
  descriptor actually opened is compared with the identity of each forbidden
  directory, so a bind mount or a symbolic link elsewhere cannot place the root
  inside one.
* **Exclusive creation.** `mkdirat` and `openat(O_CREAT|O_EXCL|O_NOFOLLOW)`: an
  existing root, subdirectory or stream file refuses. Each created object is
  re-opened no-follow and its `fstat` compared with the entry's `lstat`.
* **Modes (C-7).** Every directory must be exactly `0700` and every file exactly
  `0600`, owned by the effective UID. A creation whose mode differs — an
  unusual umask — is refused rather than `chmod`ed.
"""
from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import dataclass, field
from typing import Protocol

from ..capture_contract import (
    DIRECTORY_MODE,
    FILE_MODE,
    SUBDIRECTORIES,
    ObjectType,
    parse_capture_root,
    roots_overlap,
    sha256_hex,
)
from ..errors import HarnessError
from .descriptors import link_unnamed_descriptor

#: The locations C-6 forbids for every pass. The worktree is added per
#: repository by `RootPolicy.for_repository`.
DEFAULT_FORBIDDEN_ANCESTORS = ("/tmp",)

#: Every classification a `StoreFailure` may carry.
STORE_FAILURES = frozenset(
    {
        "forbidden-location",
        "overlapping-root",
        "open-refused",
        "object-exists",
        "create-failed",
        "verify-failed",
        "mode-mismatch",
        "identity-mismatch",
        "write-failed",
        "digest-failed",
        "size-mismatch",
        "file-barrier-failed",
        "directory-barrier-failed",
        "publication-exists",
        "publication-failed",
        "close-failed",
    }
)

_DIGEST_CHUNK = 1 << 20


class CaptureInterrupted(BaseException):
    """The mechanism or the repository host stopped mid-stage (C-15).

    Raised only by an injected seam; never caught by RP-11.
    """


class StoreFailure(HarnessError):
    """A storage stage did not succeed. Never retried, never repaired."""

    def __init__(self, stage: str, classification: str) -> None:
        if classification not in STORE_FAILURES:
            raise ValueError(f"unknown store failure {classification!r}")
        self.stage = stage
        self.classification = classification
        super().__init__(f"{stage}: {classification}")


class CaptureFilesystem(Protocol):
    """The only filesystem operations RP-11 performs. Each names its stage."""

    def open_directory(self, dir_fd: int | None, name: str, *, stage: str) -> int: ...

    def stat_path(self, path: str, *, stage: str) -> os.stat_result | None: ...

    def lstat_at(self, dir_fd: int, name: str, *, stage: str) -> os.stat_result | None: ...

    def fstat(self, fd: int, *, stage: str) -> os.stat_result: ...

    def mkdir_exclusive(self, dir_fd: int, name: str, mode: int, *, stage: str) -> None: ...

    def create_exclusive(self, dir_fd: int, name: str, mode: int, *, stage: str) -> int: ...

    def create_unnamed(self, dir_fd: int, mode: int, *, stage: str) -> int: ...

    def open_read(self, dir_fd: int, name: str, *, stage: str) -> int: ...

    def write_all(self, fd: int, data: bytes, *, stage: str) -> None: ...

    def digest(self, fd: int, *, stage: str) -> tuple[str, int]: ...

    def fsync(self, fd: int, *, stage: str) -> None: ...

    def link_unnamed(self, fd: int, dir_fd: int, name: str, *, stage: str) -> None: ...

    def close(self, fd: int, *, stage: str) -> None: ...


class PosixCaptureFilesystem:
    """The real filesystem. The stage label is accepted and ignored."""

    _DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC

    def open_directory(self, dir_fd: int | None, name: str, *, stage: str) -> int:
        if dir_fd is None:
            if name != "/":
                raise ValueError("only `/` is opened without a directory descriptor")
            return os.open("/", self._DIRECTORY_FLAGS)
        return os.open(name, self._DIRECTORY_FLAGS, dir_fd=dir_fd)

    def stat_path(self, path: str, *, stage: str) -> os.stat_result | None:
        try:
            return os.stat(path)
        except FileNotFoundError:
            return None

    def lstat_at(self, dir_fd: int, name: str, *, stage: str) -> os.stat_result | None:
        try:
            return os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
        except FileNotFoundError:
            return None

    def fstat(self, fd: int, *, stage: str) -> os.stat_result:
        return os.fstat(fd)

    def mkdir_exclusive(self, dir_fd: int, name: str, mode: int, *, stage: str) -> None:
        os.mkdir(name, mode, dir_fd=dir_fd)

    def create_exclusive(self, dir_fd: int, name: str, mode: int, *, stage: str) -> int:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
        return os.open(name, flags, mode, dir_fd=dir_fd)

    def create_unnamed(self, dir_fd: int, mode: int, *, stage: str) -> int:
        return os.open(".", os.O_TMPFILE | os.O_WRONLY | os.O_CLOEXEC, mode, dir_fd=dir_fd)

    def open_read(self, dir_fd: int, name: str, *, stage: str) -> int:
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_NOCTTY | os.O_CLOEXEC
        return os.open(name, flags, dir_fd=dir_fd)

    def write_all(self, fd: int, data: bytes, *, stage: str) -> None:
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            view = view[written:]

    def digest(self, fd: int, *, stage: str) -> tuple[str, int]:
        hasher = hashlib.sha256()
        offset = 0
        while True:
            chunk = os.pread(fd, _DIGEST_CHUNK, offset)
            if not chunk:
                return hasher.hexdigest(), offset
            hasher.update(chunk)
            offset += len(chunk)

    def fsync(self, fd: int, *, stage: str) -> None:
        os.fsync(fd)

    def link_unnamed(self, fd: int, dir_fd: int, name: str, *, stage: str) -> None:
        link_unnamed_descriptor(fd, dir_fd, name)

    def close(self, fd: int, *, stage: str) -> None:
        os.close(fd)


@dataclass(frozen=True, slots=True)
class RootPolicy:
    """Where a capture root may not be (C-6)."""

    forbidden_ancestors: tuple[str, ...]
    other_pass_roots: tuple[str, ...] = ()

    @classmethod
    def for_repository(
        cls, worktree: str, other_pass_roots: tuple[str, ...] = ()
    ) -> "RootPolicy":
        return cls((*DEFAULT_FORBIDDEN_ANCESTORS, worktree), tuple(other_pass_roots))


@dataclass(frozen=True, slots=True)
class PublicationStages:
    """The stage label of each step of one publication sequence."""

    create: str
    verify: str
    write: str
    file_barrier: str
    publish: str
    directory_barrier: str
    close: str

    @classmethod
    def uniform(cls, prefix: str) -> "PublicationStages":
        return cls(
            create=f"{prefix}:create",
            verify=f"{prefix}:verify",
            write=f"{prefix}:write",
            file_barrier=f"{prefix}:file-barrier",
            publish=f"{prefix}:publish",
            directory_barrier=f"{prefix}:directory-barrier",
            close=f"{prefix}:close",
        )


#: P-5 … P-8, in the draft's own step numbers.
RECORD_STAGES = PublicationStages(
    create="P-5:create",
    verify="P-5:verify",
    write="P-5:write",
    file_barrier="P-6:file-barrier",
    publish="P-7:publish",
    directory_barrier="P-8:directory-barrier",
    close="P-8:close",
)
GENESIS_STAGES = PublicationStages.uniform("X-1:genesis")
ADVANCE_STAGES = PublicationStages.uniform("X-2")
FINAL_STAGES = PublicationStages.uniform("X-3")

#: The label of every descriptor closed on a path that has already failed. It is
#: cleanup, not a contract step, so no test fails it and no failure of it is
#: reported: closing a descriptor writes nothing under the root.
CLEANUP_STAGE = "cleanup:close"
PROBE_STAGE = "probe"


def _split_absolute(path: str) -> tuple[str, ...]:
    return tuple(part for part in path.split("/") if part)


def _identity(facts: os.stat_result) -> tuple[int, int]:
    return (facts.st_dev, facts.st_ino)


@dataclass
class CaptureRootStore:
    """One pass's capture root, held open by descriptor for the pass."""

    filesystem: CaptureFilesystem
    capture_root: str
    _known: dict[str, ObjectType] = field(default_factory=dict)
    _identities: dict[str, tuple[int, int]] = field(default_factory=dict)
    _directories: dict[str, int] = field(default_factory=dict)

    # -- what the final state records -----------------------------------------

    @property
    def known_objects(self) -> dict[str, ObjectType]:
        """Every name this store knows exists under the root, with its type."""
        return dict(self._known)

    # -- X-1: the root and its subdirectories ---------------------------------

    def create_root(self, policy: RootPolicy) -> None:
        components = parse_capture_root(self.capture_root)
        for forbidden in policy.forbidden_ancestors:
            prefix = _split_absolute(forbidden)
            if components[: len(prefix)] == prefix:
                raise StoreFailure("X-1:policy", "forbidden-location")
        for other in policy.other_pass_roots:
            if roots_overlap(self.capture_root, other):
                raise StoreFailure("X-1:policy", "overlapping-root")
        forbidden_identities: set[tuple[int, int]] = set()
        for path in (*policy.forbidden_ancestors, *policy.other_pass_roots):
            facts = self._call(
                "X-1:forbidden-identity",
                "open-refused",
                lambda path=path: self.filesystem.stat_path(path, stage="X-1:forbidden-identity"),
            )
            if facts is not None:
                forbidden_identities.add(_identity(facts))

        current = self._call(
            "X-1:open-ancestor",
            "open-refused",
            lambda: self.filesystem.open_directory(None, "/", stage="X-1:open-ancestor"),
        )
        try:
            for component in components[:-1]:
                following = self._call(
                    "X-1:open-ancestor",
                    "open-refused",
                    lambda component=component: self.filesystem.open_directory(
                        current, component, stage="X-1:open-ancestor"
                    ),
                )
                self._close_quietly(current)
                current = following
                facts = self._call(
                    "X-1:verify-ancestor",
                    "verify-failed",
                    lambda: self.filesystem.fstat(current, stage="X-1:verify-ancestor"),
                )
                if _identity(facts) in forbidden_identities:
                    raise StoreFailure("X-1:verify-ancestor", "forbidden-location")
            leaf = components[-1]
            self._make_directory(current, leaf, "", stage="X-1:create-root")
            self._barrier(current, "X-1:root-entry-barrier", "directory-barrier-failed")
        except Exception:
            self._close_quietly(current)
            raise
        self._close_quietly(current)
        for name in SUBDIRECTORIES:
            parent, _, leaf = name.rpartition("/")
            container = self._directories[parent]
            self._make_directory(container, leaf, name, stage="X-1:create-subdirectory")
            self._barrier(container, "X-1:subdirectory-entry-barrier", "directory-barrier-failed")

    def _make_directory(self, container: int, leaf: str, name: str, *, stage: str) -> None:
        try:
            self.filesystem.mkdir_exclusive(container, leaf, DIRECTORY_MODE, stage=stage)
        except FileExistsError:
            raise StoreFailure(stage, "object-exists") from None
        except OSError:
            raise StoreFailure(stage, "create-failed") from None
        if name:
            self._known[name] = ObjectType.DIRECTORY
        verify = stage.replace("create", "verify")
        opened = self._call(
            verify,
            "open-refused",
            lambda: self.filesystem.open_directory(container, leaf, stage=verify),
        )
        self._directories[name] = opened
        facts = self._call(verify, "verify-failed", lambda: self.filesystem.fstat(opened, stage=verify))
        entry = self._call(
            verify, "verify-failed", lambda: self.filesystem.lstat_at(container, leaf, stage=verify)
        )
        if entry is None or _identity(entry) != _identity(facts) or not stat.S_ISDIR(facts.st_mode):
            raise StoreFailure(verify, "identity-mismatch")
        self._require_mode(facts, DIRECTORY_MODE, verify)

    # -- P-1 … P-4: the stream files ------------------------------------------

    def create_stream_file(self, name: str, *, create_stage: str, verify_stage: str) -> int:
        directory, _, leaf = name.rpartition("/")
        container = self._directories[directory]
        try:
            fd = self.filesystem.create_exclusive(container, leaf, FILE_MODE, stage=create_stage)
        except FileExistsError:
            raise StoreFailure(create_stage, "object-exists") from None
        except OSError:
            self._probe_regular(container, leaf, name, None)
            raise StoreFailure(create_stage, "create-failed") from None
        self._known[name] = ObjectType.REGULAR
        try:
            facts = self._call(
                verify_stage, "verify-failed", lambda: self.filesystem.fstat(fd, stage=verify_stage)
            )
            if not stat.S_ISREG(facts.st_mode) or facts.st_nlink != 1:
                raise StoreFailure(verify_stage, "identity-mismatch")
            self._require_mode(facts, FILE_MODE, verify_stage)
            self._identities[name] = _identity(facts)
        except Exception:
            self._close_quietly(fd)
            raise
        return fd

    def write(self, fd: int, data: bytes, *, stage: str) -> None:
        self._call(stage, "write-failed", lambda: self.filesystem.write_all(fd, data, stage=stage))

    def complete_stream(
        self,
        name: str,
        write_fd: int,
        *,
        close_stage: str,
        reopen_stage: str,
        verify_stage: str,
        barrier_stage: str,
    ) -> int:
        """P-2: close to further writing, reopen read-only, verify, file barrier.

        The descriptor the child wrote through is closed first, so the file is
        closed to further writing by this process before its barrier. The
        read-only descriptor the barrier is issued on is opened no-follow by the
        stream's exact name and must be the inode created in P-1.
        """
        directory, _, leaf = name.rpartition("/")
        container = self._directories[directory]
        self._call(close_stage, "close-failed", lambda: self.filesystem.close(write_fd, stage=close_stage))
        read_fd = self._call(
            reopen_stage,
            "open-refused",
            lambda: self.filesystem.open_read(container, leaf, stage=reopen_stage),
        )
        try:
            facts = self._call(
                verify_stage, "verify-failed", lambda: self.filesystem.fstat(read_fd, stage=verify_stage)
            )
            if (
                not stat.S_ISREG(facts.st_mode)
                or facts.st_nlink != 1
                or _identity(facts) != self._identities.get(name)
            ):
                raise StoreFailure(verify_stage, "identity-mismatch")
            self._barrier(read_fd, barrier_stage, "file-barrier-failed")
        except Exception:
            self._close_quietly(read_fd)
            raise
        return read_fd

    def directory_barrier(self, directory: str, *, stage: str) -> None:
        self._barrier(self._directories[directory], stage, "directory-barrier-failed")

    def digest_stream(self, read_fd: int, expected_size: int, *, stage: str) -> tuple[str, int]:
        """P-4: the SHA-256 of exactly the completed file's bytes.

        The size the digest covers must equal the byte count the launcher
        delivered and the size `fstat` reports before and after, and the file
        must not change while it is read. Anything else is a digest failure.
        """
        before = self._call(stage, "digest-failed", lambda: self.filesystem.fstat(read_fd, stage=stage))
        digest, size = self._call(stage, "digest-failed", lambda: self.filesystem.digest(read_fd, stage=stage))
        after = self._call(stage, "digest-failed", lambda: self.filesystem.fstat(read_fd, stage=stage))
        if (
            size != expected_size
            or before.st_size != size
            or after.st_size != size
            or before.st_mtime_ns != after.st_mtime_ns
            or before.st_ctime_ns != after.st_ctime_ns
        ):
            raise StoreFailure(stage, "size-mismatch")
        return digest, size

    def close(self, fd: int, *, stage: str) -> None:
        self._call(stage, "close-failed", lambda: self.filesystem.close(fd, stage=stage))

    # -- P-5 … P-8, X-1 genesis, X-2, X-3: one publication sequence -----------

    def publish(self, name: str, data: bytes, *, stages: PublicationStages) -> str:
        """Publish `data` at `name` by the unnamed-file sequence; return its SHA-256.

        1. `O_TMPFILE` in the destination directory, mode `0600`, verified
           unnamed (`st_nlink == 0`), regular and correctly owned;
        2. write every byte; 3. file barrier; 4. one `linkat` that refuses with
        `EEXIST` rather than replace; 5. directory barrier; 6. close.

        The publication has succeeded only when step 5 has. A failure before
        step 4 leaves no entry at all. A failure at or after step 4 that left
        the name in place leaves a known, unadmitted object.
        """
        directory, _, leaf = name.rpartition("/")
        container = self._directories[directory]
        fd = self._call(
            stages.create,
            "create-failed",
            lambda: self.filesystem.create_unnamed(container, FILE_MODE, stage=stages.create),
        )
        try:
            facts = self._call(
                stages.verify, "verify-failed", lambda: self.filesystem.fstat(fd, stage=stages.verify)
            )
            if not stat.S_ISREG(facts.st_mode) or facts.st_nlink != 0:
                raise StoreFailure(stages.verify, "identity-mismatch")
            self._require_mode(facts, FILE_MODE, stages.verify)
            self._call(
                stages.write, "write-failed", lambda: self.filesystem.write_all(fd, data, stage=stages.write)
            )
            self._barrier(fd, stages.file_barrier, "file-barrier-failed")
            try:
                self.filesystem.link_unnamed(fd, container, leaf, stage=stages.publish)
            except FileExistsError:
                raise StoreFailure(stages.publish, "publication-exists") from None
            except (OSError, ValueError):
                self._probe_regular(container, leaf, name, _identity(facts))
                raise StoreFailure(stages.publish, "publication-failed") from None
            self._known[name] = ObjectType.REGULAR
            self._identities[name] = _identity(facts)
            self._barrier(container, stages.directory_barrier, "directory-barrier-failed")
        except Exception:
            # Ordinary failures only. After an interruption nothing more is
            # called at all, not even a close.
            self._close_quietly(fd)
            raise
        self.close(fd, stage=stages.close)
        return sha256_hex(data)

    # -- the end of the pass ---------------------------------------------------

    def release(self) -> None:
        """Close every held directory descriptor. Writes nothing."""
        for fd in self._directories.values():
            self._close_quietly(fd)
        self._directories.clear()

    # -- internals -------------------------------------------------------------

    def _call(self, stage: str, classification: str, operation):  # type: ignore[no-untyped-def]
        try:
            return operation()
        except StoreFailure:
            raise
        except (OSError, ValueError):
            raise StoreFailure(stage, classification) from None

    def _barrier(self, fd: int, stage: str, classification: str) -> None:
        self._call(stage, classification, lambda: self.filesystem.fsync(fd, stage=stage))

    def _require_mode(self, facts: os.stat_result, mode: int, stage: str) -> None:
        if stat.S_IMODE(facts.st_mode) != mode or facts.st_uid != os.geteuid():
            raise StoreFailure(stage, "mode-mismatch")

    def _probe_regular(
        self, container: int, leaf: str, name: str, expected: tuple[int, int] | None
    ) -> None:
        """After a creating call failed: does an entry of ours exist at `name`?

        Recorded only when a no-follow `lstat` shows a regular file and — where
        the creating call had an inode — that inode. A probe that cannot answer
        records nothing; B0-RA then fails closed on whatever is there.
        """
        try:
            facts = self.filesystem.lstat_at(container, leaf, stage=PROBE_STAGE)
        except (OSError, ValueError):
            return
        if facts is None or not stat.S_ISREG(facts.st_mode):
            return
        if expected is not None and _identity(facts) != expected:
            return
        self._known[name] = ObjectType.REGULAR

    def _close_quietly(self, fd: int) -> None:
        try:
            self.filesystem.close(fd, stage=CLEANUP_STAGE)
        except (OSError, ValueError):
            pass


__all__ = [
    "ADVANCE_STAGES",
    "CLEANUP_STAGE",
    "DEFAULT_FORBIDDEN_ANCESTORS",
    "FINAL_STAGES",
    "GENESIS_STAGES",
    "RECORD_STAGES",
    "STORE_FAILURES",
    "CaptureFilesystem",
    "CaptureInterrupted",
    "CaptureRootStore",
    "PosixCaptureFilesystem",
    "PublicationStages",
    "RootPolicy",
    "StoreFailure",
]
