#!/usr/bin/env python3
"""Deterministic, non-interactive runner for the fresh R-5 successor R5 assignment.

The accepted R3 procedure fed each block to a shell through a terminal heredoc.
Antigravity's background terminal never delivered that input and returned exit
0 only after an interactive EOF (FRESH-R3-HS-1); the mandatory S12.start
closeout was then skipped (FRESH-R3-HS-2). This runner removes the terminal
from the delivery path without changing a command.

Under R5 (C-P5.0-R5-RP11-FRESH-R5-R4-D1, finding FRESH-R4-HS-1) the runner and
blocks are unchanged in behaviour. Only the identifiers, the consumed run list,
the pinned launcher digests the blocks carry and the `cc1.v` fixture's length
and digest move, because `build.sh` now fixes GCC's two garbage-collector
parameters and the fixture was re-derived.

* Every block is a pinned static resource under ``tools/r5_runner/blocks/``.
  Its bytes, with only ``<RUN>`` substituted, are written to the standard input
  of exactly the process R3 names (``/bin/bash --noprofile --norc -s``, or the
  same behind ``ssh oracle-test``) through a pipe that is then closed. That is
  the input the quoted heredoc delivered. Nobody types, pastes or sends EOF.
* The synchronization command is a pinned argument vector, run without a shell.
* The runner owns what the executor previously decided by reading: the order,
  exactly-once attempts, the first terminal condition, the pass outputs that no
  exit status encodes, and the unconditional S12 closeout.
* It writes one handback: the attestation and identity record before step 1,
  the body after S12.start, then hands the file to the S12.end block, which
  appends the closing record. It never writes to the file again.

It is stdlib-only and self-contained so that it runs under ``python3 -I -B``.
It adds no timestamp of its own: every required timestamp comes from a block.
"""

from __future__ import annotations

import dataclasses
import datetime
import enum
import hashlib
import os
import re
import secrets
import signal
import stat
import subprocess
import sys
from pathlib import Path
from types import FrameType
from typing import Callable, Iterable, Protocol, Sequence

# ---------------------------------------------------------------------------
# Fixed identifiers (assignment R5 §3.5, §5, §12)
# ---------------------------------------------------------------------------

REPOSITORY_ROOT = Path("/opt/freedom-blades/platform")
RUNNER = "tools/r5_runner/r5run.py"
RESOURCE_DIRECTORY = "tools/r5_runner/blocks"
ASSIGNMENT = "docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r5.md"
HANDBACK = "docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r5-handback.md"
WORK_ID = "C-P5.0-R5-RP11-FRESH-R5-R5"
#: The assignment revision named in the handback and in the runner's messages.
REVISION = "R5"
EXECUTOR = "Gemini"

#: Run identifiers that are consumed and may never be reused (assignment R5 §5).
CONSUMED_RUN_IDS = (
    "p5-r5-fresh-20261002T184800Z-7e9b2d41",
    "p5-r5-fresh-20261003T191400Z-9c3f71e2",
    "p5-r5-fresh-20261003T234834Z-4fc93046",
)
RUN_ID_PATTERN = re.compile(r"p5-r5-fresh-\d{8}T\d{6}Z-[0-9a-f]{8}")

#: SHA-256 and byte length of every controlled file other than the runner,
#: whose own identity is supplied on the command line from the assignment.
PINS: dict[str, tuple[str, int]] = {
    "tools/r5_runner/blocks/s01.sh": (
        "119e3d924fe4020588311df6404f927fdf356f47d4cc709bf8e74d13a23c81fd",
        11516,
    ),
    "tools/r5_runner/blocks/s02.sh": (
        "a0cda6026583275d45c1a8b88cc0ed77ba97a9973408d66990469901ef78d264",
        7000,
    ),
    "tools/r5_runner/blocks/s03.sh": (
        "2d4c39b8ccf9d84afc4a439b08611ce3f5bca32a3b97021bb6caca8d8759676b",
        1560,
    ),
    "tools/r5_runner/blocks/s04a.sh": (
        "1a948d6758f6ece09dbafc8f250a5682ec2b096cbed814eb25a8ed57657ef0a1",
        1172,
    ),
    "tools/r5_runner/blocks/s04b-start.sh": (
        "55ab56d97581e442bf24c3ebe6ab9e6b6714a1aaac04f0f0d620e3d45d4aff85",
        240,
    ),
    "tools/r5_runner/blocks/s04b-sync.argv": (
        "7dddbaef33807f4158792c7270d5a6d7e38049938a87953c7c905c44c8738050",
        313,
    ),
    "tools/r5_runner/blocks/s04b-end.sh": (
        "a77be397cf2b9a00737f25a5c4d4e17dc706e2d5478353f9afc2dbdbb95c261e",
        232,
    ),
    "tools/r5_runner/blocks/s04c.sh": (
        "4110a1c52f28f8996fde2d674716749c3be79dba572c193839279a79c2c814b7",
        4420,
    ),
    "tools/r5_runner/blocks/s04d.sh": (
        "1cbd8aca86b11d0405f657b42ca36a14898ddca2694f7e5912cb6aae69ab06ea",
        8708,
    ),
    "tools/r5_runner/blocks/s05.sh": (
        "7750e2502d7ecea05350d3d596b15d59b0b7243789502cc954592862ff4cb64b",
        3231,
    ),
    "tools/r5_runner/blocks/s06-s07.sh": (
        "58a63f9cefb8323b339e92dd3f799e2570291803792c705a4face97eacc49868",
        3193,
    ),
    "tools/r5_runner/blocks/s08.sh": (
        "c55ada18c1cd607189e7f6ef4d99de4e4589ee1d78208a643006caf900464878",
        2440,
    ),
    "tools/r5_runner/blocks/s09.sh": (
        "46bbcd1f6eee93531d08350699b83f71897e3c40cea35c2eedde54c517d02dc6",
        1588,
    ),
    "tools/r5_runner/blocks/s10.sh": (
        "6502636bf63a5194574ca553e3ca8c2ac3889e2d2bfe97c76e890f60731828f7",
        2029,
    ),
    "tools/r5_runner/blocks/s11.sh": (
        "1a0004523890ce3d19be1fd87353bbc5ea692d9a65e07a431045f819290e8bc2",
        10066,
    ),
    "tools/r5_runner/blocks/s12-start.sh": (
        "bf495fd370a236b04295e955ce083e63fd4ead1fa8e2fabe4ca788a21f1f2aa3",
        240,
    ),
    "tools/r5_runner/blocks/s12-end.sh": (
        "9aaf1069e4637e3b342712cb33817c4282c1fa8efef8296f54974c6dd59d46db",
        1283,
    ),
    "tests/test_r5_runner.py": (
        "95647bb82646550ffd09e4a693136a6ff1dac20bbfd137cde017ed4544a3154f",
        35674,
    ),
}

LOCAL_BASH = ("/bin/bash", "--noprofile", "--norc", "-s")
REMOTE_BASH = ("ssh", "oracle-test", "/bin/bash", "--noprofile", "--norc", "-s")

TIMESTAMP = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"
#: The `cc1.v` fixture re-derived under FRESH-R4-HS-1 (assignment R5 §3.1).
BASELINE_SHA256 = "e99cee65a228339e304d4e578643de409961539a8240230d4e41bb1baf6bb13a"
BASELINE_LENGTH = 5305

EXIT_PASS = 0
EXIT_HARD_STOP = 1
EXIT_CLOSEOUT_INCOMPLETE = 2
EXIT_REFUSED = 3
EXIT_INVALID_RUN = 20


# ---------------------------------------------------------------------------
# The plan
# ---------------------------------------------------------------------------


class Transport(enum.Enum):
    LOCAL = "local bash"
    REMOTE = "ssh oracle-test bash"
    SYNC = "rsync"

    @property
    def host(self) -> str:
        return "oracle-test" if self is Transport.REMOTE else "repository host"


class Kind(enum.Enum):
    STEP = "step block"
    STAMP = "timestamp block"
    SYNC = "synchronization command"
    CLOSE = "closing block"


@dataclasses.dataclass(frozen=True)
class Invocation:
    """One separately invoked process of assignment R5 §6, in plan order."""

    scope: str
    resource: str
    transport: Transport
    kind: Kind


def _block(scope: str, name: str, transport: Transport, kind: Kind) -> Invocation:
    return Invocation(scope, f"{RESOURCE_DIRECTORY}/{name}", transport, kind)


OPERATIONAL_PLAN: tuple[Invocation, ...] = (
    _block("S1", "s01.sh", Transport.LOCAL, Kind.STEP),
    _block("S2", "s02.sh", Transport.REMOTE, Kind.STEP),
    _block("S3", "s03.sh", Transport.REMOTE, Kind.STEP),
    _block("S4a", "s04a.sh", Transport.REMOTE, Kind.STEP),
    _block("S4b.start", "s04b-start.sh", Transport.LOCAL, Kind.STAMP),
    _block("S4b.sync", "s04b-sync.argv", Transport.SYNC, Kind.SYNC),
    _block("S4b.end", "s04b-end.sh", Transport.LOCAL, Kind.STAMP),
    _block("S4c", "s04c.sh", Transport.LOCAL, Kind.STEP),
    _block("S4d", "s04d.sh", Transport.REMOTE, Kind.STEP),
    _block("S5", "s05.sh", Transport.REMOTE, Kind.STEP),
    _block("S6-S7", "s06-s07.sh", Transport.REMOTE, Kind.STEP),
    _block("S8", "s08.sh", Transport.REMOTE, Kind.STEP),
    _block("S9", "s09.sh", Transport.REMOTE, Kind.STEP),
    _block("S10", "s10.sh", Transport.REMOTE, Kind.STEP),
    _block("S11", "s11.sh", Transport.REMOTE, Kind.STEP),
)
CLOSE_START = _block("S12.start", "s12-start.sh", Transport.LOCAL, Kind.STAMP)
CLOSE_END = _block("S12.end", "s12-end.sh", Transport.LOCAL, Kind.CLOSE)
FULL_PLAN: tuple[Invocation, ...] = OPERATIONAL_PLAN + (CLOSE_START, CLOSE_END)


# ---------------------------------------------------------------------------
# Errors and records
# ---------------------------------------------------------------------------


class Refusal(Exception):
    """A pre-run refusal: nothing has run, no handback exists, no host was touched."""


class PlanViolation(Exception):
    """The runner tried to repeat or reorder an attempt. Always a defect."""


class HandbackSealed(Exception):
    """A write was attempted after the body was final."""


class Interrupted(Exception):
    def __init__(self, signum: int) -> None:
        super().__init__(f"signal {signum}")
        self.signum = signum


@dataclasses.dataclass(frozen=True)
class Completed:
    """What one process returned: the true status and both streams, separately."""

    returncode: int | None
    stdout: bytes
    stderr: bytes
    interrupted_by: int | None = None
    start_error: str | None = None


@dataclasses.dataclass(frozen=True)
class Record:
    invocation: Invocation
    argv: tuple[str, ...]
    stdin_sha256: str | None
    stdin_length: int | None
    completed: Completed

    @property
    def stdout_text(self) -> str:
        return _decode(self.completed.stdout)

    @property
    def lines(self) -> list[str]:
        return self.stdout_text.split("\n")


class Verdict(enum.Enum):
    PASS = "PASS"
    INVALID_RUN = "INVALID RUN"
    HARD_STOP = "HARD STOP"


@dataclasses.dataclass(frozen=True)
class Condition:
    """A terminal or stop condition, in the order it was found."""

    scope: str
    verdict: Verdict
    reason: str
    evidence: str = ""


def _decode(data: bytes) -> str:
    return data.decode("utf-8", errors="backslashreplace")


def _lossless(data: bytes) -> bool:
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class VerifiedFile:
    path: str
    sha256: str
    length: int


@dataclasses.dataclass(frozen=True)
class Identity:
    """The verified bytes of every controlled file, read once and kept.

    Execution uses these in-memory bytes, so a file changed after verification
    cannot be what is sent.
    """

    runner: VerifiedFile
    files: tuple[VerifiedFile, ...]
    resources: dict[str, bytes]


def _read_regular(root: Path, relative: str) -> bytes:
    path = root / relative
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        raise Refusal(f"{relative} is missing") from None
    if not stat.S_ISREG(mode):
        raise Refusal(f"{relative} is not a regular file")
    return path.read_bytes()


def verify_identity(root: Path, expected_runner_sha256: str) -> Identity:
    """Verify the runner, every resource and every focused test, or refuse."""
    runner_bytes = _read_regular(root, RUNNER)
    runner_digest = _sha256(runner_bytes)
    if runner_digest != expected_runner_sha256:
        raise Refusal(
            f"{RUNNER} has SHA-256 {runner_digest}, not the assignment's "
            f"{expected_runner_sha256}"
        )
    verified = []
    resources: dict[str, bytes] = {}
    for relative, (digest, length) in sorted(PINS.items()):
        data = _read_regular(root, relative)
        if _sha256(data) != digest or len(data) != length:
            raise Refusal(
                f"{relative} has SHA-256 {_sha256(data)} and {len(data)} bytes, "
                f"not the pinned {digest} and {length}"
            )
        verified.append(VerifiedFile(relative, digest, length))
        if relative.startswith(RESOURCE_DIRECTORY + "/"):
            resources[relative] = data
    _verify_runner_tree(root)
    missing = sorted({i.resource for i in FULL_PLAN} - set(resources))
    if missing:
        raise Refusal(f"the plan names unpinned resources: {missing}")
    return Identity(
        VerifiedFile(RUNNER, runner_digest, len(runner_bytes)), tuple(verified), resources
    )


def _verify_runner_tree(root: Path) -> None:
    """The runner directory holds exactly the runner and the pinned resources."""
    top = root / "tools/r5_runner"
    want = {RUNNER} | {p for p in PINS if p.startswith("tools/r5_runner/")}
    have = set()
    for directory, subdirectories, files in os.walk(top):
        subdirectories[:] = [d for d in subdirectories if d != "__pycache__"]
        for name in subdirectories + files:
            path = Path(directory) / name
            if path.is_symlink():
                raise Refusal(f"{path.relative_to(root)} is a link")
        for name in files:
            have.add(str((Path(directory) / name).relative_to(root)))
    if have != want:
        raise Refusal(
            f"tools/r5_runner differs from the pinned set: extra {sorted(have - want)}, "
            f"missing {sorted(want - have)}"
        )


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------


class Executor(Protocol):
    def run(self, scope: str, argv: Sequence[str], stdin: bytes | None) -> Completed: ...


class SubprocessExecutor:
    """Runs one process with no terminal, no shell and no interactive input.

    * ``start_new_session`` gives the child no controlling terminal, so nothing
      in it (``ssh`` included) can prompt on one; a prompt fails instead.
    * Standard input is the block's bytes through a pipe that ``communicate``
      closes, or ``/dev/null`` for the synchronization command.
    * Standard output and standard error are captured separately, and the
      status is the one ``waitpid`` reports for this process.
    """

    def __init__(self, cwd: Path) -> None:
        self._cwd = cwd

    def run(self, scope: str, argv: Sequence[str], stdin: bytes | None) -> Completed:
        try:
            process = subprocess.Popen(
                list(argv),
                stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self._cwd,
                start_new_session=True,
                close_fds=True,
            )
        except OSError as exc:
            return Completed(None, b"", b"", start_error=f"{type(exc).__name__}: {exc}")
        try:
            stdout, stderr = process.communicate(stdin)
        except Interrupted as interrupted:
            _terminate_group(process)
            stdout, stderr = process.communicate()
            return Completed(process.returncode, stdout, stderr, interrupted.signum)
        return Completed(process.returncode, stdout, stderr)


def _terminate_group(process: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass


class AttemptLedger:
    """Exactly one attempt per scope, strictly in plan order."""

    def __init__(self, plan: Sequence[Invocation]) -> None:
        self._order = [i.scope for i in plan]
        self._attempted: list[str] = []

    def attempt(self, scope: str) -> None:
        if scope in self._attempted:
            raise PlanViolation(f"{scope} was already attempted")
        position = self._order.index(scope)
        if self._attempted and position <= self._order.index(self._attempted[-1]):
            raise PlanViolation(f"{scope} would run out of order after {self._attempted[-1]}")
        self._attempted.append(scope)

    @property
    def attempted(self) -> tuple[str, ...]:
        return tuple(self._attempted)


class HandbackFile:
    """The one handback: created once, given its body once, then sealed."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._created = False
        self._sealed = False

    @property
    def path(self) -> Path:
        return self._path

    @property
    def sealed(self) -> bool:
        return self._sealed

    def create(self, text: str) -> None:
        if self._created:
            raise HandbackSealed("the handback was already created")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        descriptor = os.open(self._path, flags, 0o644)
        self._created = True
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)

    def append_body(self, text: str) -> None:
        if self._sealed or not self._created:
            raise HandbackSealed("the handback body is final")
        self._sealed = True
        descriptor = os.open(self._path, os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)

    def seal(self) -> None:
        self._sealed = True


# ---------------------------------------------------------------------------
# Evaluation: R3's pass conditions, applied mechanically
# ---------------------------------------------------------------------------


def expected_labels(resource: bytes) -> tuple[str, ...]:
    """Every ``<label> exit=%s`` that ``r5_block`` prints, in textual order.

    ``r5_end`` and ``r5_close`` are defined before ``r5_block`` in every block,
    and their lines are checked separately (``r5_close`` writes only into the
    handback), so only the text from ``r5_block() {`` onwards is read.
    """
    text = _decode(resource)
    body = text[text.index("r5_block() {") :]
    return tuple(re.findall(r"printf '([^'%\n]+) exit=%s\\n'", body))


def _find(lines: list[str], wanted: str) -> list[int]:
    return [index for index, line in enumerate(lines) if line == wanted]


def _matching(lines: list[str], pattern: str) -> list[str]:
    compiled = re.compile(pattern)
    return [line for line in lines if compiled.fullmatch(line)]


def _segment(lines: list[str], after: str, before: str) -> list[str] | None:
    """The output lines printed between two status lines, or None if absent."""
    start, end = _find(lines, after), _find(lines, before)
    if len(start) != 1 or len(end) != 1 or end[0] <= start[0]:
        return None
    return lines[start[0] + 1 : end[0]]


def _first_nonzero_label(record: Record, labels: Iterable[str]) -> str | None:
    wanted = set(labels)
    for line in record.lines:
        match = re.fullmatch(r"(.+) exit=(\d+)", line)
        if match and match.group(1) in wanted and match.group(2) != "0":
            return line
    return None


def _timestamp_lines(invocation: Invocation) -> tuple[str, ...]:
    scope = invocation.scope
    if invocation.kind is Kind.STEP:
        starts = (rf"{re.escape(scope)}\.start start_utc={TIMESTAMP}",)
        if scope == "S1":
            starts = (rf"RUN\.start start_utc={TIMESTAMP}",) + starts
        return starts + (rf"{re.escape(scope)}\.end end_utc={TIMESTAMP}",)
    if invocation.kind is Kind.STAMP:
        which = "end_utc" if scope.endswith(".end") else "start_utc"
        return (rf"{re.escape(scope)} {which}={TIMESTAMP}",)
    return ()


def _valid_timestamp(line: str) -> bool:
    value = line.rsplit("=", 1)[1]
    try:
        datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return True


def evidence_gaps(record: Record, resource: bytes) -> list[str]:
    """Required lines that are missing, malformed, duplicated or out of order.

    For a passing block this is every ``<label> exit=0`` of ``r5_block`` in
    order, the closing ``block exit=0`` line and, for timed scopes, the
    timestamp and ``final exit`` lines. For a failing block only the
    timestamps and the ``final exit`` line are required, because the block
    stops at its first nonzero check.
    """
    invocation, lines = record.invocation, record.lines
    status = record.completed.returncode
    gaps: list[str] = []
    for pattern in _timestamp_lines(invocation):
        found = _matching(lines, pattern)
        if len(found) != 1:
            gaps.append(f"timestamp line /{pattern}/ printed {len(found)} times")
        elif not _valid_timestamp(found[0]):
            gaps.append(f"malformed timestamp: {found[0]}")
    if invocation.kind is Kind.STEP:
        finals = _matching(lines, rf"{re.escape(invocation.scope)} final exit=(\d+)")
        if len(finals) != 1:
            gaps.append(f"`{invocation.scope} final exit=` printed {len(finals)} times")
        elif finals[0] != f"{invocation.scope} final exit={status}":
            gaps.append(f"`{finals[0]}` disagrees with the invoking status {status}")
    if status != 0:
        return gaps
    required = [f"{label} exit=0" for label in expected_labels(resource)]
    if invocation.kind is Kind.CLOSE:
        required.insert(1, "handback_body=present")
    required.append(f"{invocation.scope} block exit=0")
    if invocation.kind is Kind.STEP:
        required += [f"{invocation.scope}.end date exit=0", f"{invocation.scope} final exit=0"]
    position = -1
    for line in required:
        hits = _find(lines, line)
        if len(hits) != 1:
            gaps.append(f"`{line}` printed {len(hits)} times")
        elif hits[0] <= position:
            gaps.append(f"`{line}` out of order")
        else:
            position = hits[0]
    return gaps


def _s1_git_status(record: Record) -> list[str]:
    """S1.3: the reproduced lines must match git_status_lines and its digest."""
    raw = record.completed.stdout
    head = b"S1.2 git-rev-parse exit=0\n"
    if raw.count(head) != 1:
        return ["S1.3 output cannot be located"]
    tail = raw.split(head, 1)[1]
    match = re.search(rb"(?m)^git_status_lines=(\d+)\ngit_status_sha256=([0-9a-f]{64})\n", tail)
    if match is None:
        return ["S1.3 git_status_lines/git_status_sha256 lines absent"]
    status_bytes = tail[: match.start()]
    count, digest = int(match.group(1)), match.group(2).decode()
    problems = []
    reproduced = status_bytes.count(b"\n")
    if reproduced != count:
        problems.append(f"S1.3 reproduced {reproduced} lines, not {count}")
    if _sha256(status_bytes) != digest:
        problems.append("S1.3 reproduced bytes do not match git_status_sha256")
    return problems


def s1_git_status_lines(record: Record) -> str | None:
    raw = record.completed.stdout
    head = b"S1.2 git-rev-parse exit=0\n"
    if raw.count(head) != 1:
        return None
    tail = raw.split(head, 1)[1]
    match = re.search(rb"(?m)^git_status_sha256=[0-9a-f]{64}\n", tail)
    return _decode(tail[: match.end()]) if match else None


def _s5_root_mode(record: Record, run_id: str) -> list[str]:
    output = _segment(record.lines, "S5.7 ldconfig exit=0", "S5.8 root-stat exit=0")
    want = re.compile(rf"755 \S+ /var/tmp/{re.escape(run_id)}-root")
    if output is None or len(output) != 1 or not want.fullmatch(output[0]):
        return [f"S5.8 does not show mode 755 for the root: {output!r}"]
    return []


def _s9_exact(record: Record) -> list[str]:
    problems = []
    length = _segment(record.lines, "S9.start date exit=0", "S9.1 cc1v-length exit=0")
    if length != [str(BASELINE_LENGTH)]:
        problems.append(f"S9.1 printed {length!r}, not [{str(BASELINE_LENGTH)!r}]")
    for line in (
        f"actual_sha256:   {BASELINE_SHA256}",
        "is_identical:    True",
        "verdict:         PASS",
    ):
        if len(_find(record.lines, line)) != 1:
            problems.append(f"cc1check output lacks `{line}`")
    return problems


#: S11's end-of-run observations and the step-2 observations they must equal
#: byte for byte (R3 §6 step 11): (S11 after, S11 label, S2 after, S2 label).
END_OF_RUN_PAIRS = (
    ("S11.7 date exit=0", "S11.8 uname exit=0", "S2.1 date exit=0", "S2.2 uname exit=0"),
    (
        "S11.8 uname exit=0",
        "S11.9 cpuinfo-first-processor exit=0",
        "S2.4 lscpu exit=0",
        "S2.5 cpuinfo-first-processor exit=0",
    ),
    (
        "S11.9 cpuinfo-first-processor exit=0",
        "S11.10 bwrap-version exit=0",
        "S2.5 cpuinfo-first-processor exit=0",
        "S2.6 bwrap-version exit=0",
    ),
    (
        "S11.10 bwrap-version exit=0",
        "S11.11 bwrap-sha256 exit=0",
        "S2.7 bwrap-stat exit=0",
        "S2.8 bwrap-sha256 exit=0",
    ),
)


def end_of_run_comparison(s11: Record, s2: Record) -> list[tuple[str, bool]]:
    results = []
    for after, label, s2_after, s2_label in END_OF_RUN_PAIRS:
        end = _segment(s11.lines, after, label)
        start = _segment(s2.lines, s2_after, s2_label)
        same = end is not None and start is not None and end == start
        results.append((f"{label.split(' exit=')[0]} = {s2_label.split(' exit=')[0]}", same))
    return results


# ---------------------------------------------------------------------------
# The run
# ---------------------------------------------------------------------------


def new_run_id(now: datetime.datetime, token: str) -> str:
    run_id = f"p5-r5-fresh-{now:%Y%m%dT%H%M%SZ}-{token}"
    if not RUN_ID_PATTERN.fullmatch(run_id) or run_id in CONSUMED_RUN_IDS:
        raise Refusal(f"unusable run identifier {run_id}")
    return run_id


@dataclasses.dataclass
class RunResult:
    run_id: str
    verdict: Verdict
    conditions: list[Condition]
    records: list[Record]
    closeout_complete: bool
    exit_code: int


class Runner:
    """One run of assignment R5 §6, from the attestation to the S12.end block."""

    def __init__(
        self,
        *,
        root: Path,
        identity: Identity,
        executor: Executor,
        run_id: str,
        interpreter: str,
        progress: Callable[[str], None] = lambda message: None,
    ) -> None:
        self._root = root
        self._identity = identity
        self._executor = executor
        self._run_id = run_id
        self._interpreter = interpreter
        self._progress = progress
        self._ledger = AttemptLedger(FULL_PLAN)
        self._handback = HandbackFile(root / HANDBACK)
        self._records: list[Record] = []
        self._conditions: list[Condition] = []
        self._notes: list[str] = []
        self._closing = False

    # -- public ------------------------------------------------------------

    @property
    def closing(self) -> bool:
        return self._closing

    @property
    def handback(self) -> HandbackFile:
        return self._handback

    def note(self, message: str) -> None:
        self._notes.append(message)

    def run(self) -> RunResult:
        """Write the attestation, run the operational plan, then always close."""
        try:
            self._handback.create(render_header(self._identity, self._run_id, self._interpreter))
        except OSError as exc:
            raise Refusal(f"the handback could not be created: {exc}") from None
        try:
            self._run_operational()
        except Interrupted as interrupted:
            self._stop("runner", f"the runner received signal {interrupted.signum}")
        except Exception as exc:  # noqa: BLE001 - any defect still closes the run
            self._stop("runner", f"runner internal error: {type(exc).__name__}: {exc}")
        finally:
            closeout_complete = self._closeout()
        verdict = self.verdict()
        if not closeout_complete:
            code = EXIT_CLOSEOUT_INCOMPLETE
        else:
            code = {
                Verdict.PASS: EXIT_PASS,
                Verdict.INVALID_RUN: EXIT_INVALID_RUN,
                Verdict.HARD_STOP: EXIT_HARD_STOP,
            }[verdict]
        return RunResult(
            self._run_id, verdict, list(self._conditions), list(self._records),
            closeout_complete, code,
        )

    def verdict(self) -> Verdict:
        verdicts = {c.verdict for c in self._conditions}
        if Verdict.HARD_STOP in verdicts:
            return Verdict.HARD_STOP
        if Verdict.INVALID_RUN in verdicts:
            return Verdict.INVALID_RUN
        return Verdict.PASS

    # -- operational steps -------------------------------------------------

    def _run_operational(self) -> None:
        for invocation in OPERATIONAL_PLAN:
            if self._conditions and not self._s4b_end_due(invocation):
                return
            self._execute(invocation)

    def _s4b_end_due(self, invocation: Invocation) -> bool:
        """R3 §6 step 4b: S4b.end follows the synchronization whatever its status."""
        return (
            invocation.scope == "S4b.end"
            and bool(self._records)
            and self._records[-1].invocation.scope == "S4b.sync"
        )

    def _stop(self, scope: str, reason: str, evidence: str = "") -> None:
        self._conditions.append(Condition(scope, Verdict.HARD_STOP, reason, evidence))

    def _prepare(self, invocation: Invocation) -> tuple[tuple[str, ...], bytes | None]:
        resource = self._identity.resources[invocation.resource]
        if invocation.kind is Kind.SYNC:
            argv = tuple(
                line.replace("<RUN>", self._run_id)
                for line in _decode(resource).split("\n")
                if line
            )
            return argv, None
        stdin = resource.replace(b"<RUN>", self._run_id.encode("ascii"))
        prefix = REMOTE_BASH if invocation.transport is Transport.REMOTE else LOCAL_BASH
        return prefix, stdin

    def _execute(self, invocation: Invocation) -> Record:
        self._ledger.attempt(invocation.scope)
        argv, stdin = self._prepare(invocation)
        self._progress(f"{invocation.scope} started")
        completed = self._executor.run(invocation.scope, argv, stdin)
        record = Record(
            invocation,
            argv,
            _sha256(stdin) if stdin is not None else None,
            len(stdin) if stdin is not None else None,
            completed,
        )
        self._records.append(record)
        self._conditions.extend(self._evaluate(record))
        self._progress(f"{invocation.scope} status={completed.returncode}")
        return record

    def _record(self, scope: str) -> Record | None:
        return next((r for r in self._records if r.invocation.scope == scope), None)

    def _evaluate(self, record: Record) -> list[Condition]:
        invocation, completed = record.invocation, record.completed
        scope = invocation.scope
        if completed.start_error is not None:
            return [Condition(scope, Verdict.HARD_STOP, "the process could not be started", completed.start_error)]
        if completed.interrupted_by is not None:
            return [Condition(scope, Verdict.HARD_STOP, f"interrupted by signal {completed.interrupted_by}")]
        if invocation.kind is Kind.SYNC:
            if completed.returncode != 0:
                return [Condition(scope, Verdict.HARD_STOP, f"synchronization exited {completed.returncode}")]
            return []
        resource = self._identity.resources[invocation.resource]
        gaps = evidence_gaps(record, resource)
        status = completed.returncode
        if status != 0:
            first = _first_nonzero_label(record, expected_labels(resource)) or f"invoking status {status}"
            invalid = (
                scope == "S3"
                and status == 20
                and not gaps
                and first == "S3.1 qualification exit=20"
            )
            verdict = Verdict.INVALID_RUN if invalid else Verdict.HARD_STOP
            reason = f"{scope} exited {status}"
            if gaps:
                reason += "; missing evidence: " + "; ".join(gaps)
            return [Condition(scope, verdict, reason, first)]
        if gaps:
            return [
                Condition(
                    scope, Verdict.HARD_STOP,
                    f"{scope} exited 0 but its required evidence is missing ({REVISION} §8.3)",
                    "; ".join(gaps),
                )
            ]
        problems = self._specific_pass_output(record)
        if problems:
            return [Condition(scope, Verdict.HARD_STOP, f"{scope} pass output not met", "; ".join(problems))]
        return []

    def _specific_pass_output(self, record: Record) -> list[str]:
        scope = record.invocation.scope
        if scope == "S1":
            return _s1_git_status(record)
        if scope == "S5":
            return _s5_root_mode(record, self._run_id)
        if scope == "S9":
            return _s9_exact(record)
        if scope == "S11":
            s2 = self._record("S2")
            if s2 is None:
                return ["S2 record absent"]
            return [
                f"{name} differs (unexplained environmental difference)"
                for name, same in end_of_run_comparison(record, s2)
                if not same
            ]
        return []

    # -- closeout ----------------------------------------------------------

    def _closeout(self) -> bool:
        """S12.start, the body, S12.end: always, in that order, once each."""
        self._closing = True
        try:
            self._execute(CLOSE_START)
        except Exception as exc:  # noqa: BLE001
            self._stop("S12.start", f"runner internal error: {type(exc).__name__}: {exc}")
        try:
            body = render_body(self)
        except Exception as exc:  # noqa: BLE001
            body = render_fallback_body(self, f"{type(exc).__name__}: {exc}")
        try:
            self._handback.append_body(body)
        except Exception as exc:  # noqa: BLE001
            self._stop("S12 body", f"the handback body could not be written: {type(exc).__name__}: {exc}")
        finally:
            self._handback.seal()
        try:
            record = self._execute(CLOSE_END)
        except Exception as exc:  # noqa: BLE001
            self._stop("S12.end", f"runner internal error: {type(exc).__name__}: {exc}")
            return False
        return record.completed.returncode == 0 and not any(
            c.scope == "S12.end" for c in self._conditions
        )

    # -- rendering inputs --------------------------------------------------

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def records(self) -> tuple[Record, ...]:
        return tuple(self._records)

    @property
    def conditions(self) -> tuple[Condition, ...]:
        return tuple(self._conditions)

    @property
    def notes(self) -> tuple[str, ...]:
        return tuple(self._notes)

    def record_for(self, scope: str) -> Record | None:
        return self._record(scope)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _fence(text: str) -> str:
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    marker = "`" * max(3, longest + 1)
    if not text.endswith("\n"):
        text += "\n"
    return f"{marker}text\n{text}{marker}\n"


ATTESTATION = """\
## 1. Executor identity and §2 independence attestation

I, {executor}, execute this run under assignment {revision} and make this attestation
by invoking the runner with `--executor {executor} --attest-independence`,
before step 1 and before any host action:

1. I did not implement, co-author or remediate I-7 or I-7-R1;
2. I have not reused, and will not use, any earlier build root, package cache,
   checkout, work directory, build output, trace, evidence or scratch
   directory;
3. I have read the controlling assignment (`{assignment}`) and the acceptance
   record that names me; and
4. this run is wholly fresh. I have not read, reused, copied, compared against
   or inherited any resource or artifact from my earlier R-5 run
   (`/tmp/r5-*-gemini-f8a1` on `oracle-test`), my B1 run
   (`/tmp/p5-b1-repro-20261001t190454z-*` on the repository host), my stopped
   fresh R-5 run `p5-r5-fresh-20261002T184800Z-7e9b2d41` (formerly
   `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-*` on `oracle-test`, deleted by
   Codex on 2026-10-03; any surviving copy is equally forbidden), my consumed
   R3 run `p5-r5-fresh-20261003T191400Z-9c3f71e2`, which created no
   `oracle-test` path, or my consumed R4 run
   `p5-r5-fresh-20261003T234834Z-4fc93046` (its retained
   `/var/tmp/p5-r5-fresh-20261003T234834Z-4fc93046-*` paths on `oracle-test`).
   That includes roots, caches, checkouts, outputs, `cc1.v` bytes, manifests,
   traces, logs and pytest temporary directories.
"""


def render_header(identity: Identity, run_id: str, interpreter: str) -> str:
    rows = [identity.runner, *identity.files]
    table = "\n".join(f"| `{f.path}` | {f.length} | `{f.sha256}` | OK |" for f in rows)
    return (
        f"# Fresh R-5 successor {REVISION} independent static-launcher rebuild handback\n\n"
        f"Execution work ID: `{WORK_ID}`\n"
        f"Run identifier: `{run_id}`\n"
        f"Executor: {EXECUTOR}\n"
        f"Controlling assignment: [`{ASSIGNMENT}`]({Path(ASSIGNMENT).name})\n"
        f"Written by: `{RUNNER}` on the executor's single invocation (assignment {REVISION} §13)\n\n"
        "---\n\n"
        "## 0. Runner identity, verified before any host action\n\n"
        "The runner verified these files before writing this file and before step 1.\n"
        "Every block that follows was sent from the verified in-memory bytes.\n\n"
        "| File | Bytes | SHA-256 | Result |\n|---|---:|---|---|\n"
        f"{table}\n\n"
        f"Interpreter: `{interpreter}`; flags: isolated=1, dont_write_bytecode=1.\n\n"
        "---\n\n"
        + ATTESTATION.format(executor=EXECUTOR, assignment=ASSIGNMENT, revision=REVISION)
        + "\n---\n"
    )


TIMED_SCOPES = (
    ("whole run", "RUN", "repository host"),
    ("step 1", "S1", "repository host"),
    ("step 2", "S2", "oracle-test"),
    ("step 3", "S3", "oracle-test"),
    ("step 4a", "S4a", "oracle-test"),
    ("step 4b", "S4b", "repository host"),
    ("step 4c", "S4c", "repository host"),
    ("step 4d", "S4d", "oracle-test"),
    ("step 5", "S5", "oracle-test"),
    ("steps 6/7 combined", "S6-S7", "oracle-test"),
    ("step 8", "S8", "oracle-test"),
    ("step 9", "S9", "oracle-test"),
    ("step 10", "S10", "oracle-test"),
    ("step 11", "S11", "oracle-test"),
    ("step 12", "S12", "repository host"),
)


def _stamp(record: Record | None, pattern: str) -> str:
    if record is None:
        return "not run"
    found = _matching(record.lines, pattern)
    if len(found) == 1:
        return f"`{found[0]}`"
    return f"absent (invoking status {record.completed.returncode})"


def _status(record: Record | None) -> str:
    if record is None:
        return "not run"
    return f"invoking status {record.completed.returncode}"


def _timestamp_row(runner: Runner, label: str, scope: str, host: str) -> str:
    record = runner.record_for
    if scope == "RUN":
        start = _stamp(record("S1"), rf"RUN\.start start_utc={TIMESTAMP}")
        return f"| {label} | `RUN.start` / `RUN.end` | {host} | {start} | in closing record | {_status(record('S1'))} |"
    if scope == "S4b":
        start = _stamp(record("S4b.start"), rf"S4b\.start start_utc={TIMESTAMP}")
        end = _stamp(record("S4b.end"), rf"S4b\.end end_utc={TIMESTAMP}")
        status = "; ".join(
            f"{name}: {_status(record(name))}" for name in ("S4b.start", "S4b.sync", "S4b.end")
        )
        return f"| {label} | `S4b.start` / `S4b.end` | {host} | {start} | {end} | {status} |"
    if scope == "S12":
        start = _stamp(record("S12.start"), rf"S12\.start start_utc={TIMESTAMP}")
        return f"| {label} | `S12.start` / `S12.end` | {host} | {start} | in closing record | S12.start: {_status(record('S12.start'))}; S12.end: in closing record |"
    rec = record(scope)
    start = _stamp(rec, rf"{re.escape(scope)}\.start start_utc={TIMESTAMP}")
    end = _stamp(rec, rf"{re.escape(scope)}\.end end_utc={TIMESTAMP}")
    final = _matching(rec.lines, rf"{re.escape(scope)} final exit=\d+") if rec else []
    status = _status(rec) + (f"; `{final[0]}`" if len(final) == 1 else "")
    return f"| {label} | `{scope}.start` / `{scope}.end` | {host} | {start} | {end} | {status} |"


def _lines_between(record: Record | None, after: str, before: str) -> str:
    if record is None:
        return "not run"
    segment = _segment(record.lines, after, before)
    return "absent" if segment is None else "\n".join(segment)


def _pick(
    record: Record | None,
    scope: str,
    labels: Sequence[str],
    keep: Callable[[str], bool] = lambda line: False,
) -> str:
    """The named labels' status lines and the result lines `keep` selects.

    These are copies for orientation; the complete transcript is in §6.
    """
    if record is None:
        return f"[{scope}] not run\n"
    chosen = [
        line
        for line in record.lines
        if keep(line) or (line.split(" ", 1)[0] in labels and re.search(r" exit=\d+$", line))
    ]
    return f"[{scope}]\n" + ("\n".join(chosen) if chosen else "absent") + "\n"


def _transcript(record: Record) -> str:
    invocation, completed = record.invocation, record.completed
    parts = [
        f"### {invocation.scope} — {invocation.kind.value}, {invocation.transport.host}\n",
        f"* argv: `{' '.join(record.argv)}`",
        f"* resource: `{invocation.resource}`",
    ]
    if record.stdin_sha256 is not None:
        parts.append(
            f"* standard input: the resource with `<RUN>` substituted, "
            f"{record.stdin_length} bytes, SHA-256 `{record.stdin_sha256}`; then closed"
        )
    else:
        parts.append("* standard input: `/dev/null`")
    parts.append(f"* invoking status: `{completed.returncode}`")
    if completed.start_error:
        parts.append(f"* start error: `{completed.start_error}`")
    if completed.interrupted_by is not None:
        parts.append(f"* interrupted by signal {completed.interrupted_by}; process group terminated")
    for name, data in (("stdout", completed.stdout), ("stderr", completed.stderr)):
        parts.append(
            f"* {name}: {len(data)} bytes, SHA-256 `{_sha256(data)}`, "
            f"{'valid UTF-8' if _lossless(data) else 'not valid UTF-8; shown with backslash escapes'}"
        )
    text = "\n".join(parts) + "\n\n"
    if invocation.kind is Kind.SYNC:
        summary = [
            line for line in record.lines
            if line.startswith("sent ") or line.startswith("total size is ")
        ]
        text += (
            f"Per {REVISION} §10.1 only the exit status and rsync's closing summary lines are "
            "embedded; the per-file list and standard error are withheld and are "
            "identified only by the digests above.\n\n"
        )
        text += _fence("\n".join(summary) if summary else "summary lines absent")
        return text
    text += "stdout:\n\n" + _fence(record.stdout_text or "(empty)")
    text += "\nstderr:\n\n" + _fence(_decode(completed.stderr) or "(empty)")
    return text


def _answer(runner: Runner, scopes: Sequence[str]) -> str:
    failing = [c for c in runner.conditions if c.scope in scopes]
    if failing:
        return f"no — {failing[0].reason}"
    if any(runner.record_for(s) is None for s in scopes):
        return "not reached"
    return "yes"


def _timestamps_answer(runner: Runner) -> str:
    missing = []
    for _label, scope, _host in TIMED_SCOPES:
        row = _timestamp_row(runner, "", scope, "")
        cells = [cell.strip() for cell in row.split("|")[1:-1]]
        for name, cell in (("start", cells[3]), ("end", cells[4])):
            if not cell.startswith("`") and cell != "in closing record":
                missing.append(f"{scope} {name} {cell}")
    return "yes" if not missing else "no — " + "; ".join(missing)


def render_body(runner: Runner) -> str:
    record = runner.record_for
    run_id = runner.run_id
    verdict = runner.verdict()
    out: list[str] = []
    add = out.append

    add("\n## 2. Timestamps\n")
    add("Copied by the runner from the transcripts of §6; no value comes from any other source.\n")
    add("| Scope | Producing label | Host | Start | End | Status |\n|---|---|---|---|---|---|")
    for label, scope, host in TIMED_SCOPES:
        add(_timestamp_row(runner, label, scope, host))

    add("\n## 3. Repository state\n")
    s1 = record("S1")
    add(f"Commit (S1.2): `{_lines_between(s1, 'S1.1 cd exit=0', 'S1.2 git-rev-parse exit=0')}`\n")
    add("Complete S1.3 output, every line of `git status --short --untracked-files=all`"
        " followed by `git_status_lines` and `git_status_sha256`, extracted from the"
        " step-1 transcript:\n")
    git_status = s1_git_status_lines(s1) if s1 else None
    add(_fence(git_status if git_status is not None else "absent"))
    if s1 is not None and s1.completed.returncode == 0:
        problems = _s1_git_status(s1)
        add(f"Runner check of line count and digest: {'; '.join(problems) if problems else 'equal'}.\n")
    add("S1.4, S1.5, S1.6, S1.7, S1.8, S4c.2, S4c.3, S4d.3 and S4d.4 result lines:\n")
    results = (
        "repository_state=", "rows ", "launcher_tree ", "package_lines ", "archive_snapshot=",
        "build_root_manifest_sha256=", "entry_mechanism=", "30 ",
    )
    add(_fence(
        _pick(s1, "S1", ("S1.4", "S1.5", "S1.6", "S1.7", "S1.8"), lambda l: l.startswith(results))
        + _pick(record("S4c"), "S4c", ("S4c.2", "S4c.3"), lambda l: l.startswith(results))
        + _pick(record("S4d"), "S4d", ("S4d.1", "S4d.3", "S4d.4"), lambda l: l.startswith(results))
    ))

    add("\n## 4. Host-assumption variation and diagnostic context\n")
    s3 = record("S3")
    qualification = "\n".join(l for l in s3.lines if l.startswith("HA-")) if s3 else "not run"
    add("S3.1 output:\n")
    add(_fence(qualification))
    observed = {line.split("=", 1)[0]: line.split("=", 1)[1] for line in qualification.split("\n") if "=" in line and line.startswith("HA-")}
    add("| HA | Reference (§3.4) | Observed (S3.1) | Qualifies (S3.1) |\n|---|---|---|---|")
    add(f"| HA-1 | `6.8.0-139-generic` | `{observed.get('HA-1 kernel_release', 'not observed')}` | {observed.get('HA-1 qualifies', 'not observed')} |")
    add(f"| HA-2 | `AMD EPYC-Milan Processor` | `{observed.get('HA-2 model_names', 'not observed')}` | {observed.get('HA-2 qualifies', 'not observed')} |")
    add(f"| HA-3 | bubblewrap `0.9.0`, fixed `enter.py` vector | see S2.6–S2.9 in §6 | {observed.get('HA-3 qualifies', 'not observed')} |\n")
    add("Step-2 observations (S2.1–S2.25), including the S2.15–S2.18d diagnostic context and the"
        " `/var/tmp` preflight, are in the step-2 transcript in §6.\n")
    s11, s2 = record("S11"), record("S2")
    if s11 is not None and s2 is not None and s11.completed.returncode == 0:
        add("End-of-run observations against step 2 (byte equality of the printed lines):\n")
        for name, same in end_of_run_comparison(s11, s2):
            add(f"* {name}: {'equal' if same else 'DIFFERENT'}")
        add("")
    else:
        add("End-of-run observations: not reached.\n")

    add("\n## 5. Created paths\n")
    add(f"* repository host: `{HANDBACK}`, regular file, created by the runner for this handback.")
    if record("S4a") is None:
        add("* `oracle-test`: step 4a did not run, so the runner created no `oracle-test` path.\n")
    else:
        add("* `oracle-test` modes, owners and groups at creation (S4a.2), checkout after synchronization (S4d.1),"
            " root (S5.8), at the end (S11.5) and sizes (S11.6), copied from §6:\n")
        stats = []
        for scope in ("S4a", "S4d", "S5", "S11"):
            rec = record(scope)
            if rec is not None:
                stats += [l for l in rec.lines if f"/var/tmp/{run_id}-" in l and not l.startswith(("cd ", "S"))]
        add(_fence("\n".join(stats) if stats else "none printed"))

    add("\n## 6. Invocation transcripts\n")
    add("Every invocation, exactly as run and in order, with its true status and both streams."
        " The S12.end block is evidenced by its closing record.\n")
    for rec in runner.records:
        add(_transcript(rec))

    add("\n## 7. Synchronization, download source, resolve and cache accounting\n")
    add(f"* synchronization: {_status(record('S4b.sync'))}; summary lines in §6 (`S4b.sync`).")
    add("* download source: `https://snapshot.ubuntu.com/ubuntu/20261001T000000Z/`, fixed by the pinned"
        " `provision.py` and the `--snapshot` argument of S5.2.")
    add("* resolve and cache accounting (S5.2–S5.6):\n")
    s5 = record("S5")
    add(_fence(
        _pick(s5, "S5", ("S5.2", "S5.4", "S5.5", "S5.6", "S5.7", "S5.8"), lambda l: l.startswith("cache_entries "))
    ))

    add("\n## 8. Same-invocation R-1/R-2 evidence\n")
    add("`build.stdout` and `build.stderr` are displayed verbatim by S6.3 in the steps-6/7 transcript (§6). Result lines:\n")
    root_tmp = (f"/var/tmp/{run_id}-root/tmp ", f"/var/tmp/{run_id}-root/var/tmp ")
    add(_fence(_pick(
        record("S6-S7"), "S6-S7",
        ("S6.2", "S6.3", "S6.4", "S6.5", "S7.1", "S7.2", "S7.3", "S7.4"),
        lambda l: l.startswith(("r1-manifest ", "ld_so_preload=") + root_tmp)
        or l.endswith(f"/var/tmp/{run_id}-evidence/regenerated.manifest"),
    )))

    add("\n## 9. Normative output digests\n")
    s8 = record("S8")
    add(_fence(_pick(
        s8, "S8", ("S8.2", "S8.3", "S8.4"),
        lambda l: l.endswith((" OK", " MISMATCH", "judged in step 9")) or l.startswith("missing_from_build_stdout"),
    )))

    add("\n## 10. Diagnostic `cc1.v` comparison\n")
    add("The complete `cc1check.py` output is displayed by S9.4 in the step-9 transcript (§6). Result lines:\n")
    s9 = record("S9")
    add(_fence(
        f"[S9.1] cc1.v length: {_lines_between(s9, 'S9.start date exit=0', 'S9.1 cc1v-length exit=0')}\n"
        + _pick(
            s9, "S9", ("S9.1", "S9.3", "S9.4"),
            lambda l: l.startswith(("baseline_sha256:", "actual_sha256:", "is_identical:", "total_diffs:", "verdict:")),
        )
    ))

    add("\n## 11. Corroborating tests\n")
    add("The complete pytest output, every warning and the summary line are displayed by S10.3 in the"
        " step-10 transcript (§6). The runner does not classify warnings: under §6 step 10 the two known"
        " pytest-asyncio configuration warnings are expected and every other warning is for the reviewer.\n")
    add(_fence(_pick(record("S10"), "S10", ("S10.2", "S10.3", "S10.4"), lambda l: l.startswith("tests="))))

    add("\n## 12. Stopped, invalid or unexplained conditions\n")
    if runner.conditions:
        first = runner.conditions[0]
        add(f"First condition: **{first.verdict.value}** at `{first.scope}` — {first.reason}.\n")
        if first.evidence:
            add("Quoted exactly:\n")
            add(_fence(first.evidence))
        for later in runner.conditions[1:]:
            add(f"* later: {later.verdict.value} at `{later.scope}` — {later.reason}" + (f" (`{later.evidence}`)" if later.evidence else ""))
        attempted = {r.invocation.scope for r in runner.records}
        not_run = [i.scope for i in OPERATIONAL_PLAN if i.scope not in attempted]
        add(f"\nNot run after the first condition: {', '.join(not_run) if not_run else 'none'}.\n")
    else:
        add("None.\n")
    for note in runner.notes:
        add(f"* runner note: {note}")

    add("\n## 13. Retained evidence and cleanup state\n")
    add(f"* the handback `{HANDBACK}` is the evidence of record ({REVISION} §10.1).")
    if record("S4a") is not None:
        add(f"* step 4a ran: directories were created under `oracle-test:/var/tmp/{run_id}-*`, and"
            " `oracle-test`'s `/var/tmp` changed.")
    if record("S4b.sync") is not None:
        add(f"* the synchronization ran: the repository working tree was sent to `oracle-test:/var/tmp/{run_id}-checkout/`.")
    if record("S4a") is None:
        add("* no `oracle-test` path was created by this run.")
    add("* S11.4 evidence digests: " + ("in the step-11 transcript (§6)." if record("S11") else "not reached."))
    add("* cleanup state: nothing was deleted. Everything stays in place pending review and"
        " Peter Duscha's direction. The host is not claimed to be in its pre-run state.\n")

    add("\n## 14. Verdict\n")
    add(f"**{verdict.value}** (precedence: HARD STOP over INVALID RUN over PASS, §8). The verdict of record is"
        " HARD STOP if this handback does not end with the exact closing record of §6 step 12.\n")
    operational = [i.scope for i in OPERATIONAL_PLAN]
    add("| §8.1 condition | Answer |\n|---|---|")
    add("| 1. independence attestation | complete (§1, written before step 1) |")
    add(f"| 2. every invocation ran in order, once, exit 0, with its pass output | {_answer(runner, operational)} |")
    add(f"| 3. every timed scope has its start and end values | {_timestamps_answer(runner)}; step-12 end, whole-run end and closing record: in closing record |")
    add(f"| 4. HA-1 or HA-2 qualified; start and end observations agree | {_answer(runner, ['S3', 'S11'])} |")
    add(f"| 5. same-invocation R-1/R-2 gate and manifest equality | {_answer(runner, ['S6-S7'])} |")
    add(f"| 6. four normative outputs and listing | {_answer(runner, ['S8'])} |")
    add(f"| 7. `cc1.v` byte-identical (`cc1check.py` PASS) | {_answer(runner, ['S9'])} |")
    add(f"| 8. 12 tests, 0 failures, 0 errors, 0 skipped | {_answer(runner, ['S10'])} |")
    nine = "no — see §12" if runner.conditions else "no mechanical difference found; pytest warnings (§11) are for reviewer determination"
    add(f"| 9. no unexplained difference remains | {nine} |\n")

    add("\n## 15. Operational and governance statements\n")
    add("* RP-11 remains unwired and unmet.\n* `plan.is_executable=False`.\n* PO-9 and PO-14 remain open.\n"
        "* Package 5.0 is not ready.\n* No installation, operational, harness `--execute`, privileged,"
        " commit or push authority was exercised.\n")

    add("\n## 16. Stop\n")
    add("The runner hands this file to the S12.end block, which appends the closing record. Nothing"
        " edits this file afterwards. The run stops pending Codex's independent review and Peter"
        " Duscha's decision.\n")
    return "\n".join(out)


def render_fallback_body(runner: Runner, error: str) -> str:
    """A body that cannot fail: the raw transcripts, if the full renderer did."""
    parts = [
        "\n## 2–16. Body (fallback rendering)\n",
        f"The full renderer failed (`{error}`). The verdict of record is **HARD STOP** for"
        " missing evidence. Every captured transcript follows verbatim.\n",
    ]
    for rec in runner.records:
        try:
            parts.append(_transcript(rec))
        except Exception:  # noqa: BLE001
            parts.append(f"### {rec.invocation.scope}\n\n(transcript could not be rendered)\n")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


USAGE = (
    "usage: python3 -I -B tools/r5_runner/r5run.py --executor Gemini "
    "--attest-independence --expect-runner-sha256 <64 hex>"
)


def parse_arguments(argv: Sequence[str]) -> str:
    """Accept exactly the one invocation of R5 §13; return the runner digest."""
    if (
        len(argv) != 5
        or argv[0:3] != ["--executor", EXECUTOR, "--attest-independence"]
        or argv[3] != "--expect-runner-sha256"
        or not re.fullmatch(r"[0-9a-f]{64}", argv[4])
    ):
        raise Refusal(f"arguments {list(argv)!r} are not the assignment's invocation; {USAGE}")
    return argv[4]


def check_interpreter(flags: object, version: tuple[int, ...]) -> None:
    if getattr(flags, "isolated", 0) != 1 or getattr(flags, "dont_write_bytecode", 0) != 1:
        raise Refusal("the runner must be started with python3 -I -B")
    if tuple(version[:2]) < (3, 10):
        raise Refusal("the runner requires Python 3.10 or later")


def _install_signal_handlers(runner: Runner) -> None:
    def interrupt(signum: int, frame: FrameType | None) -> None:
        if runner.closing:
            runner.note(f"signal {signum} received during closeout and deferred")
            return
        raise Interrupted(signum)

    def hangup(signum: int, frame: FrameType | None) -> None:
        runner.note("SIGHUP received and ignored; the run does not depend on a terminal")

    signal.signal(signal.SIGINT, interrupt)
    signal.signal(signal.SIGTERM, interrupt)
    signal.signal(signal.SIGHUP, hangup)


def _say(message: str) -> None:
    print(f"r5run: {message}", flush=True)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        check_interpreter(sys.flags, tuple(sys.version_info))
        expected = parse_arguments(arguments)
        if Path(__file__).resolve() != (REPOSITORY_ROOT / RUNNER).resolve():
            raise Refusal(f"the runner must be executed from {REPOSITORY_ROOT / RUNNER}")
        identity = verify_identity(REPOSITORY_ROOT, expected)
        if os.path.lexists(REPOSITORY_ROOT / HANDBACK):
            raise Refusal(f"{HANDBACK} already exists; this run identity is consumed")
        run_id = new_run_id(datetime.datetime.now(datetime.timezone.utc), secrets.token_hex(4))
    except Refusal as refusal:
        _say(f"REFUSED before any host action: {refusal}")
        _say("no block ran, no handback was written; stop and report")
        return EXIT_REFUSED
    runner = Runner(
        root=REPOSITORY_ROOT,
        identity=identity,
        executor=SubprocessExecutor(REPOSITORY_ROOT),
        run_id=run_id,
        interpreter=f"{sys.executable} {sys.version.split()[0]}",
        progress=_say,
    )
    _install_signal_handlers(runner)
    _say(f"run {run_id} started; identity verified")
    try:
        result = runner.run()
    except Refusal as refusal:
        _say(f"REFUSED before any host action: {refusal}")
        _say("no block ran; stop and report")
        return EXIT_REFUSED
    _say(
        f"verdict={result.verdict.value}; closeout="
        f"{'complete' if result.closeout_complete else 'INCOMPLETE'}; "
        f"handback={HANDBACK}; exit={result.exit_code}"
    )
    _say("the run is over; do not re-invoke, edit the handback or run anything else")
    return result.exit_code


if __name__ == "__main__":
    sys.exit(main())
