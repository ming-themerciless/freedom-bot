"""The one place in the harness that writes a file the run did not copy.

`boundary.py` is the one place a process starts. This is the one place bytes are
put on disk by the harness itself, and it exists as a separate module for the
same reason: a reviewer asking *"what can this thing write, and where?"* has one
file to read rather than a call graph to trace.

## What it can write, and why that set cannot grow by accident

`materialize()` takes bytes and a destination, and it refuses both unless they
are the reviewed ones. There are four independent checks, and each would have to
be defeated separately:

1. **The planning tier already fixed the content.** The bytes come from
   `materialization.MaterializedFile`, whose construction verifies them against a
   **digest written as a constant** — so an edited rule is a `PlanRefused` at
   import, before any of this runs, and the digest is inside the review manifest.
2. **The executor already fixed the destination.** It compares the step's
   destination with `DisposableTarget.config_path(filename)` immediately before
   calling here, so a destination that is not the approved disposable instance's
   own configuration path never reaches this module.
3. **This module re-derives the destination's admissibility from scratch**, from
   `targets.POSTGRES_CONFIG_FILES` and `targets.validate_postgres_config_
   directory`, without consulting the plan. A plan that had been edited to name
   `/etc/passwd`, `postgresql.conf`, a production hierarchy, the repository
   worktree or a path with a relative segment is refused here as well as there.
4. **It re-hashes the bytes it was handed.** The digest travels with the content
   and is compared again at the last possible moment, so content that changed
   between the manifest and the write is refused rather than installed.

There is no parameter that widens any of them, no `force`, and no code path that
creates a file: the destination must already exist as a **regular file**, which
is exactly the pre-change file the reviewed capture step has just copied.

## What it deliberately cannot do

Create a file, follow a symbolic link, write outside a PostgreSQL configuration
directory, write `postgresql.conf`, append, write more than
`materialization.MAX_MATERIALIZED_BYTES`, read a host file, start a process,
compose a shell string, or run at all when it is not armed or when the process is
not effective UID and GID 0. Each of those is a test.

## Why the write is `O_TRUNC` on the existing inode rather than a replace

An atomic `rename` over the destination would give the file a **new inode**, and
the reviewed cleanup restores by `install`ing the byte-exact capture back over
the same path. Keeping the inode means the only thing that changes is the
content, the owner, the group and the mode — all four of which the restore sets
back — so there is nothing left for a reviewer to reason about that the declared
mutation does not already cover.

## What a refusal says

One of `MATERIALIZATION_FAILURES`: a short, fixed classification, exactly as
`boundary.LAUNCH_FAILURES` is. No path, no account name, no numeric id and no
operating-system message is ever returned, because the classification is what
reaches a run outcome and an evidence artifact must carry none of those.
"""
from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import dataclass, field
from typing import Protocol

from ..errors import TargetRefused
from ..materialization import MAX_MATERIALIZED_BYTES
from ..targets import POSTGRES_CONFIG_FILES, validate_postgres_config_directory
from .boundary import (
    IdentityLookup,
    IdentityRefusal,
    SystemIdentityLookup,
)

#: A materializer that is not armed writes nothing. The CLI arms one on exactly
#: one line, inside the `--execute` branch.
MATERIALIZER_NOT_ARMED = "materializer-not-armed"
#: The bytes handed in do not hash to the digest that travelled with them.
MATERIALIZATION_DIGEST_MISMATCH = "content-digest-mismatch"
#: The content is longer than the reviewed bound, or empty.
MATERIALIZATION_CONTENT_REFUSED = "content-not-reviewed"
#: The destination is not a file in a PostgreSQL configuration directory that
#: this harness materializes.
MATERIALIZATION_DESTINATION_NOT_REVIEWED = "destination-not-reviewed"
#: The destination does not exist, is not a regular file, or is a symbolic link.
MATERIALIZATION_OBJECT_TYPE = "existing-object-type-mismatch"
#: The pre-change capture this destination is restored from was not taken.
MATERIALIZATION_CAPTURE_INCOMPLETE = "capture-incomplete"
#: The process is not effective UID and GID 0.
MATERIALIZATION_ROOT_UNAVAILABLE = "root-identity-unavailable"
#: The owner or group the reviewed file names does not resolve on this host.
MATERIALIZATION_IDENTITY_UNKNOWN = "identity-unknown"
#: The write, the ownership change, the mode change or the flush failed.
MATERIALIZATION_WRITE_FAILED = "write-failed"
#: Recorded by the executor when a materialization failed its
#: immediately-before-execution revalidation and was therefore never attempted.
MATERIALIZATION_VALIDATION_REFUSED = "validation-refused"

#: Every value `MaterializationResult.failure` may take. Fixed, safe and short,
#: for the same reason `LAUNCH_FAILURES` is.
MATERIALIZATION_FAILURES: frozenset[str] = frozenset(
    {
        MATERIALIZER_NOT_ARMED,
        MATERIALIZATION_DIGEST_MISMATCH,
        MATERIALIZATION_CONTENT_REFUSED,
        MATERIALIZATION_DESTINATION_NOT_REVIEWED,
        MATERIALIZATION_OBJECT_TYPE,
        MATERIALIZATION_CAPTURE_INCOMPLETE,
        MATERIALIZATION_ROOT_UNAVAILABLE,
        MATERIALIZATION_IDENTITY_UNKNOWN,
        MATERIALIZATION_WRITE_FAILED,
        MATERIALIZATION_VALIDATION_REFUSED,
    }
)


@dataclass(frozen=True, slots=True)
class MaterializationResult:
    """What a materializer reports. A boolean and a fixed classification."""

    applied: bool
    failure: str = ""


def _refusal(classification: str) -> MaterializationResult:
    return MaterializationResult(applied=False, failure=classification)


class FileMaterializer(Protocol):
    """The seam every test injects across.

    `step_id` is passed so a materializer can attribute a write to the reviewed
    step it came from, and `sha256` travels beside `content` so the digest can be
    re-checked at the point of the write rather than trusted from upstream.
    """

    def materialize(
        self,
        *,
        step_id: str,
        destination: str,
        content: bytes,
        sha256: str,
        owner: str,
        group: str,
        mode: int,
    ) -> MaterializationResult: ...


@dataclass(slots=True)
class RecordingMaterializer:
    """Records what it was asked to write, and writes nothing.

    This is what a dry run uses, and it is the **default** on `ExecutingRunner`,
    so an executor constructed without a materializer by mistake refuses the
    materialization rather than performing it — the step is then unsatisfied, the
    run stops, and the derived cleanup runs. It fails closed in the direction
    that leaves the host alone.
    """

    requests: list[tuple[str, str, str]] = field(default_factory=list)

    def materialize(
        self,
        *,
        step_id: str,
        destination: str,
        content: bytes,
        sha256: str,
        owner: str,
        group: str,
        mode: int,
    ) -> MaterializationResult:
        self.requests.append((step_id, destination, sha256))
        return _refusal(MATERIALIZER_NOT_ARMED)


@dataclass(frozen=True, slots=True)
class SystemMaterializer:
    """The real one. Not the default anywhere; the CLI arms it on `--execute`.

    The account database is read through the same injected `IdentityLookup` the
    process boundary uses, so there is one reader of `pwd`/`grp` in this package
    and one place a test replaces to exercise every branch below without touching
    a real account.
    """

    #: A materializer that is not armed writes nothing, so an executor
    #: constructed with a real one by mistake still cannot change a file.
    armed: bool = False
    lookup: IdentityLookup = field(default_factory=SystemIdentityLookup)

    def materialize(
        self,
        *,
        step_id: str,
        destination: str,
        content: bytes,
        sha256: str,
        owner: str,
        group: str,
        mode: int,
    ) -> MaterializationResult:
        if not self.armed:
            return _refusal(MATERIALIZER_NOT_ARMED)
        if not content or len(content) > MAX_MATERIALIZED_BYTES:
            return _refusal(MATERIALIZATION_CONTENT_REFUSED)
        if hashlib.sha256(content).hexdigest() != (sha256 or "").strip().lower():
            return _refusal(MATERIALIZATION_DIGEST_MISMATCH)
        if not self._destination_is_reviewed(destination):
            return _refusal(MATERIALIZATION_DESTINATION_NOT_REVIEWED)

        try:
            euid, egid = self.lookup.effective_ids()
        except OSError:
            return _refusal(MATERIALIZATION_ROOT_UNAVAILABLE)
        if euid != 0 or egid != 0:
            return _refusal(MATERIALIZATION_ROOT_UNAVAILABLE)

        try:
            uid, _primary = self.lookup.account(owner)
            gid = self.lookup.group_id(group)
        except IdentityRefusal:
            return _refusal(MATERIALIZATION_IDENTITY_UNKNOWN)

        try:
            existing = os.lstat(destination)
        except OSError:
            # Absent, or unreadable. Either way the byte-exact pre-change capture
            # cannot have been taken from it, so there is nothing to restore.
            return _refusal(MATERIALIZATION_OBJECT_TYPE)
        if not stat.S_ISREG(existing.st_mode):
            return _refusal(MATERIALIZATION_OBJECT_TYPE)

        try:
            self._write(destination, content, uid, gid, mode)
        except OSError:
            return _refusal(MATERIALIZATION_WRITE_FAILED)
        return MaterializationResult(applied=True)

    @staticmethod
    def _destination_is_reviewed(destination: str) -> bool:
        """Re-derived here, from the guards, without consulting the plan.

        `validate_postgres_config_directory` is what refuses `/`, every entry of
        `FORBIDDEN_ROOTS` and every ancestor of one, the repository worktree, a
        relative segment, a glob, a shell metacharacter and a directory that is
        not a PostgreSQL instance's. The filename check is what refuses
        `postgresql.conf` and everything else.
        """
        directory, separator, filename = destination.rpartition("/")
        if not separator or filename not in POSTGRES_CONFIG_FILES:
            return False
        try:
            normalized = validate_postgres_config_directory(directory)
        except TargetRefused:
            return False
        return normalized == directory

    @staticmethod
    def _write(destination: str, content: bytes, uid: int, gid: int, mode: int) -> None:
        """Truncate the existing regular file and write the reviewed bytes.

        `O_NOFOLLOW` is what makes the `lstat` above meaningful: without it a
        symbolic link swapped in between the check and the write would be
        followed. `O_CREAT` is deliberately absent — this replaces content in a
        file the capture step has already copied, and it never brings one into
        existence.
        """
        descriptor = os.open(destination, os.O_WRONLY | os.O_TRUNC | os.O_NOFOLLOW)
        try:
            written = 0
            while written < len(content):
                written += os.write(descriptor, content[written:])
            os.fchown(descriptor, uid, gid)
            os.fchmod(descriptor, mode)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


__all__ = [
    "FileMaterializer",
    "MATERIALIZATION_CAPTURE_INCOMPLETE",
    "MATERIALIZATION_CONTENT_REFUSED",
    "MATERIALIZATION_DESTINATION_NOT_REVIEWED",
    "MATERIALIZATION_DIGEST_MISMATCH",
    "MATERIALIZATION_FAILURES",
    "MATERIALIZATION_IDENTITY_UNKNOWN",
    "MATERIALIZATION_OBJECT_TYPE",
    "MATERIALIZATION_ROOT_UNAVAILABLE",
    "MATERIALIZATION_VALIDATION_REFUSED",
    "MATERIALIZATION_WRITE_FAILED",
    "MATERIALIZER_NOT_ARMED",
    "MaterializationResult",
    "RecordingMaterializer",
    "SystemMaterializer",
]
