"""Shared fixtures for the RP-11 capture and retention suites.

Everything here works under a pytest temporary directory. Nothing names a fixed
`/tmp` path, reads the process environment, reaches a network, a database or a
host, or constructs a launcher that runs anything but the current interpreter
with inert arguments.

* `FaultFilesystem` wraps the real `PosixCaptureFilesystem` and fails, or
  interrupts, exactly one labelled stage at one occurrence. Every call is
  logged with its stage, and every call made after an injected interruption is
  logged separately, so a test can assert that none was made.
* `ScriptedLauncher` stands in for the process launcher where a test is about
  storage rather than about a process: it writes fixed bytes into the sinks the
  mechanism supplies and reports what a real launch would.
* `RecordingReadOnlyFilesystem` wraps the verifier's read-only filesystem, logs
  every call and can run a mutation hook at a chosen call, which is how the
  race tests change the tree mid-verification.

## Descriptors the suite leaves behind — C-P5.0-R5-RP11-I1-R3-R1

Three things this suite does deliberately leave a descriptor open in the pytest
process, and none of them is a production release defect:

* an **interruption** models the mechanism's process ending, so the mechanism
  makes no further call, not even a close (C-15); a real crash has the kernel
  close them, and the suite's process does not end;
* a test that inspects an **open session** never ends it, and ending it would
  add the X-3 write the test is not about; and
* the fault modes `"fail"` on a close stage and `"after"` on an opening stage
  withhold a real close or discard the descriptor the real call returned.

Before this was tracked the RP-11 capture suite left 618 descriptors open, which
exhausted a 1024 soft limit in one whole-package process (RP11-I1-R3-2).
`FaultFilesystem` therefore records every descriptor the real filesystem hands
out through it, with the identity it had, and `release_suite_descriptors`
closes the ones still open **after** the test body — outside `_invoke`, so the
"no call after an interruption" log is unchanged — and only where the number
still refers to the recorded object. The autouse fixture
`rp11_release_descriptors` calls it; each RP-11 test module imports it.
"""
from __future__ import annotations

import errno
import hashlib
import os
import stat
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Iterator

import pytest

from tools.phase_5_0_evidence.execution.boundary import StreamCaptureLauncher, StreamCaptureResult
from tools.phase_5_0_evidence.execution.capture_mechanism import (
    ActRequest,
    CaptureSession,
    GenesisRequest,
    create_capture_session,
)
from tools.phase_5_0_evidence.execution.capture_store import (
    CaptureInterrupted,
    PosixCaptureFilesystem,
    RootPolicy,
)
from tools.phase_5_0_evidence.execution.retention_check import PosixReadOnlyFilesystem

PASS_A = "C-P5.0-R5-OP1-A"
PASS_B = "C-P5.0-R5-OP1-B"
TOOL_SHA256 = "5" * 64
PYTHON = sys.executable
#: The one environment every real launch in these suites receives. Explicit,
#: small, and read from nowhere.
INERT_ENVIRONMENT = {"LC_ALL": "C", "LANG": "C"}


class FixedClock:
    """C-4's client clock, deterministic. One microsecond per reading."""

    source = "rp11-test-clock"

    def __init__(self) -> None:
        self._moment = datetime(2026, 9, 27, 12, 0, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        self._moment += timedelta(microseconds=1)
        return self._moment


#: Every `FaultFilesystem` created since the last release, so the autouse
#: fixture can close what each one still holds.
_TRACKED: list["FaultFilesystem"] = []

#: The methods whose real call returns a new descriptor.
_OPENING_METHODS = frozenset({"open_directory", "create_exclusive", "open_read"})


class FaultFilesystem:
    """The real filesystem, with one stage failed or interrupted on purpose.

    `mode` is `"fail"` (raise `EIO` instead of the call), `"after"` (make the
    call, then raise `EIO` — an error reported after the effect), `"exists"`
    (raise `EEXIST` instead of the call) or `"interrupt"` (raise
    `CaptureInterrupted` instead of the call). For `write_all` only, three
    **false-success** modes write the wrong bytes and report success, as a
    lying or partial write would: `"short"` (all but the last byte), `"empty"`
    (nothing) and `"corrupt"` (the same length, first byte changed).
    """

    FALSE_WRITES = ("short", "empty", "corrupt")

    def __init__(
        self,
        *,
        stage: str | None = None,
        mode: str = "fail",
        occurrence: int = 1,
        inner: PosixCaptureFilesystem | None = None,
        stat_path_override: Callable[[str], os.stat_result | None] | None = None,
    ) -> None:
        self.inner = inner or PosixCaptureFilesystem()
        self.stage = stage
        self.mode = mode
        self.occurrence = occurrence
        self.calls: list[tuple[str, str]] = []
        self.after_interrupt: list[tuple[str, str]] = []
        self.triggered = False
        self._seen = 0
        self._stat_path_override = stat_path_override
        #: Descriptor number → the `(st_dev, st_ino)` it referred to when the
        #: real call returned it. Removed when a real close of it succeeds.
        self.held: dict[int, tuple[int, int]] = {}
        _TRACKED.append(self)

    def stages(self) -> list[str]:
        return [stage for _, stage in self.calls]

    def _invoke(self, method: str, stage: str, operation):  # type: ignore[no-untyped-def]
        if self.triggered and self.mode == "interrupt":
            self.after_interrupt.append((method, stage))
        self.calls.append((method, stage))
        if not self.triggered and stage == self.stage:
            self._seen += 1
            if self._seen == self.occurrence:
                self.triggered = True
                if self.mode == "interrupt":
                    raise CaptureInterrupted(stage)
                if self.mode == "exists":
                    raise FileExistsError(errno.EEXIST, "injected")
                if self.mode == "after":
                    self._hold(method, operation())
                raise OSError(errno.EIO, "injected")
        return self._hold(method, operation())

    def _hold(self, method: str, result):  # type: ignore[no-untyped-def]
        if method in _OPENING_METHODS and isinstance(result, int):
            facts = os.fstat(result)
            self.held[result] = (facts.st_dev, facts.st_ino)
        return result

    def release_held(self) -> None:
        """Close every descriptor still held, only if it is still the same object.

        Called after the test body, never through `_invoke`. A number whose
        object no longer matches was closed elsewhere and may have been reused,
        so it is left alone rather than closed.
        """
        held, self.held = self.held, {}
        for fd, identity in held.items():
            try:
                facts = os.fstat(fd)
            except OSError:
                continue
            if (facts.st_dev, facts.st_ino) == identity:
                os.close(fd)

    def open_directory(self, dir_fd, name, *, stage):  # type: ignore[no-untyped-def]
        return self._invoke("open_directory", stage, lambda: self.inner.open_directory(dir_fd, name, stage=stage))

    def stat_path(self, path, *, stage):  # type: ignore[no-untyped-def]
        if self._stat_path_override is not None:
            return self._invoke("stat_path", stage, lambda: self._stat_path_override(path))
        return self._invoke("stat_path", stage, lambda: self.inner.stat_path(path, stage=stage))

    def lstat_at(self, dir_fd, name, *, stage):  # type: ignore[no-untyped-def]
        return self._invoke("lstat_at", stage, lambda: self.inner.lstat_at(dir_fd, name, stage=stage))

    def fstat(self, fd, *, stage):  # type: ignore[no-untyped-def]
        return self._invoke("fstat", stage, lambda: self.inner.fstat(fd, stage=stage))

    def mkdir_exclusive(self, dir_fd, name, mode, *, stage):  # type: ignore[no-untyped-def]
        return self._invoke("mkdir_exclusive", stage, lambda: self.inner.mkdir_exclusive(dir_fd, name, mode, stage=stage))

    def create_exclusive(self, dir_fd, name, mode, *, stage):  # type: ignore[no-untyped-def]
        return self._invoke("create_exclusive", stage, lambda: self.inner.create_exclusive(dir_fd, name, mode, stage=stage))

    def open_read(self, dir_fd, name, *, stage):  # type: ignore[no-untyped-def]
        return self._invoke("open_read", stage, lambda: self.inner.open_read(dir_fd, name, stage=stage))

    def write_all(self, fd, data, *, stage):  # type: ignore[no-untyped-def]
        if self.mode in self.FALSE_WRITES and not self.triggered and stage == self.stage:
            self.calls.append(("write_all", stage))
            self.triggered = True
            wrong = {
                "short": data[:-1],
                "empty": b"",
                "corrupt": bytes([data[0] ^ 0xFF]) + data[1:],
            }[self.mode]
            if wrong:
                self.inner.write_all(fd, wrong, stage=stage)
            return None
        return self._invoke("write_all", stage, lambda: self.inner.write_all(fd, data, stage=stage))

    def digest(self, fd, *, stage):  # type: ignore[no-untyped-def]
        return self._invoke("digest", stage, lambda: self.inner.digest(fd, stage=stage))

    def fsync(self, fd, *, stage):  # type: ignore[no-untyped-def]
        return self._invoke("fsync", stage, lambda: self.inner.fsync(fd, stage=stage))

    def link_exclusive(self, dir_fd, source, destination, *, stage):  # type: ignore[no-untyped-def]
        return self._invoke(
            "link_exclusive",
            stage,
            lambda: self.inner.link_exclusive(dir_fd, source, destination, stage=stage),
        )

    def close(self, fd, *, stage):  # type: ignore[no-untyped-def]
        result = self._invoke("close", stage, lambda: self.inner.close(fd, stage=stage))
        self.held.pop(fd, None)
        return result


def release_suite_descriptors() -> None:
    """Close what every tracked `FaultFilesystem` still holds, then forget them."""
    tracked = list(_TRACKED)
    _TRACKED.clear()
    for filesystem in tracked:
        filesystem.release_held()


@pytest.fixture(autouse=True)
def rp11_release_descriptors() -> Iterator[None]:
    """After each test, release the descriptors the suite left open on purpose."""
    yield
    release_suite_descriptors()


@dataclass
class ScriptedLauncher:
    """Writes scripted bytes into the mechanism's sinks. Starts no process."""

    outputs: list[tuple[bytes, bytes, int]] = field(default_factory=list)
    started: bool = True
    bound_exceeded: bool = False
    complete: bool = True
    calls: list[tuple[str, ...]] = field(default_factory=list)

    def launch(self, argv, *, environment, stdout, stderr, stream_bound_bytes, drain_seconds=5.0):  # type: ignore[no-untyped-def]
        self.calls.append(tuple(argv))
        if not self.started:
            return StreamCaptureResult(False, "capture-start-failed", None, 0, 0, False, False)
        index = len(self.calls) - 1
        out, err, code = (
            self.outputs[index] if index < len(self.outputs) else (b"out-%d" % index, b"err-%d" % index, 0)
        )
        if out:
            stdout.write(out)
        if err:
            stderr.write(err)
        return StreamCaptureResult(True, "", code, len(out), len(err), self.bound_exceeded, self.complete)


@dataclass
class CountingLauncher:
    """The real, armed launcher, counted."""

    inner: StreamCaptureLauncher = field(default_factory=lambda: StreamCaptureLauncher(armed=True))
    calls: list[tuple[str, ...]] = field(default_factory=list)

    def launch(self, argv, **keywords):  # type: ignore[no-untyped-def]
        self.calls.append(tuple(argv))
        return self.inner.launch(argv, **keywords)


def python_argv(program: str, *arguments: str) -> tuple[str, ...]:
    """The current interpreter, isolated, running an inert inline program."""
    return (PYTHON, "-I", "-S", "-c", program, *arguments)


def writes(out: bytes, err: bytes, code: int = 0) -> tuple[str, ...]:
    """A fixture program that writes exactly `out` and `err` and exits `code`."""
    program = (
        "import sys;"
        f"sys.stdout.buffer.write({out!r});sys.stdout.flush();"
        f"sys.stderr.buffer.write({err!r});sys.stderr.flush();"
        f"sys.exit({code})"
    )
    return python_argv(program)


def act(step: str, argv: tuple[str, ...], *, bound: int = 4096, drain: float = 5.0) -> ActRequest:
    return ActRequest(
        step_or_case_id=step,
        argv=argv,
        environment=dict(INERT_ENVIRONMENT),
        stream_bound_bytes=bound,
        drain_seconds=drain,
    )


@dataclass
class Host:
    """A stand-in repository host under a pytest temporary directory."""

    base: Path
    worktree: Path
    forbidden_tmp: Path

    @classmethod
    def under(cls, tmp_path: Path) -> "Host":
        base = tmp_path / "host"
        worktree = tmp_path / "worktree"
        forbidden = tmp_path / "forbidden-tmp"
        for path in (base, worktree, forbidden):
            path.mkdir()
        return cls(base=base, worktree=worktree, forbidden_tmp=forbidden)

    def policy(self, *others: str) -> RootPolicy:
        return RootPolicy((str(self.forbidden_tmp), str(self.worktree)), tuple(others))

    def root(self, name: str = "capture-a") -> str:
        return str(self.base / name)


def open_session(
    host: Host,
    *,
    root: str | None = None,
    pass_id: str = PASS_A,
    filesystem=None,  # type: ignore[no-untyped-def]
    launcher=None,  # type: ignore[no-untyped-def]
    others: tuple[str, ...] = (),
    verifier_filesystem=None,  # type: ignore[no-untyped-def]
) -> CaptureSession:
    return create_capture_session(
        GenesisRequest(
            capture_root=root or host.root(),
            pass_id=pass_id,
            tool_sha256=TOOL_SHA256,
            policy=host.policy(*others),
        ),
        # A `FaultFilesystem` with no stage is the real filesystem, unchanged,
        # with the descriptors it hands out tracked for release after the test.
        filesystem=filesystem if filesystem is not None else FaultFilesystem(),
        launcher=launcher if launcher is not None else ScriptedLauncher(),
        clock=FixedClock(),
        verifier_filesystem=verifier_filesystem,
    )


def write_handback(path: Path, session: CaptureSession, *, prose: str = "") -> str:
    """A Pass A handback carrying the binding block; returns its SHA-256."""
    text = (
        "# Claude handback — C-P5.0-R5-OP1-A (test fixture)\n\n"
        + prose
        + "## 2. Measured facts\n\n"
        + session.binding().render()
        + "\nEnd of fixture.\n"
    )
    path.write_bytes(text.encode("utf-8"))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(root: str) -> dict[str, tuple]:
    """Every entry under `root`, never followed: type, mode, identity, size,
    times and — for regular files only — the SHA-256 of the bytes.

    This is the suite's own observation, independent of the verifier, and it is
    how a test proves that the verifier changed nothing.
    """
    facts: dict[str, tuple] = {}
    for directory, names, files in os.walk(root, followlinks=False):
        for name in sorted(names + files):
            path = os.path.join(directory, name)
            info = os.lstat(path)
            digest = None
            if stat.S_ISREG(info.st_mode) and info.st_mode & 0o400:
                digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
            facts[os.path.relpath(path, root)] = (
                stat.S_IFMT(info.st_mode),
                stat.S_IMODE(info.st_mode),
                info.st_ino,
                info.st_nlink,
                info.st_size,
                info.st_mtime_ns,
                info.st_ctime_ns,
                digest,
            )
    return facts


def names_under(root: str) -> set[str]:
    return set(tree(root))


class RecordingReadOnlyFilesystem:
    """The verifier's real read-only filesystem, logged, with an optional hook.

    `hook(method, count, arguments)` runs **before** the wrapped call; `count`
    is how many times that method has been called so far, including this one.
    """

    def __init__(self, hook: Callable[[str, int, tuple], None] | None = None) -> None:
        self.inner = PosixReadOnlyFilesystem()
        self.calls: list[tuple[str, tuple]] = []
        self.hook = hook
        self._counts: dict[str, int] = {}
        self.opened_files: list[bytes] = []

    def _record(self, method: str, arguments: tuple) -> None:
        self._counts[method] = self._counts.get(method, 0) + 1
        self.calls.append((method, arguments))
        if self.hook is not None:
            self.hook(method, self._counts[method], arguments)

    def read_file(self, path):  # type: ignore[no-untyped-def]
        self._record("read_file", (path,))
        return self.inner.read_file(path)

    def open_directory(self, dir_fd, name):  # type: ignore[no-untyped-def]
        self._record("open_directory", (name,))
        return self.inner.open_directory(dir_fd, name)

    def list_names(self, dir_fd):  # type: ignore[no-untyped-def]
        self._record("list_names", ())
        return self.inner.list_names(dir_fd)

    def lstat_at(self, dir_fd, name):  # type: ignore[no-untyped-def]
        self._record("lstat_at", (name,))
        return self.inner.lstat_at(dir_fd, name)

    def open_file(self, dir_fd, name):  # type: ignore[no-untyped-def]
        self._record("open_file", (name,))
        self.opened_files.append(name)
        return self.inner.open_file(dir_fd, name)

    def fstat(self, fd):  # type: ignore[no-untyped-def]
        self._record("fstat", ())
        return self.inner.fstat(fd)

    def read_all(self, fd):  # type: ignore[no-untyped-def]
        self._record("read_all", ())
        return self.inner.read_all(fd)

    def close(self, fd):  # type: ignore[no-untyped-def]
        self._record("close", ())
        return self.inner.close(fd)
