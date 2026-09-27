"""RP-11's fixed contract: names, the byte-safe name representation, the
canonical encodings of a record and an index state, and the handback binding.

The controlling requirements are the R5-amended P5.0-R5 operational-evidence
draft, `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`
at SHA-256 `5e06a388…`, §9.5 (C-1 … C-15, P-1 … P-8, X-1 … X-4) and §7.1 B0-RA.
This module is the **data** half of RP-11. It opens no file, starts no process
and imports nothing from `execution/`; the storage, the process launcher and the
retention check live there and import this.

## The layout under a pass's capture root

Every name the mechanism ever creates follows one fixed rule, so B0-RA can form
the accounted set from the final state and these rules alone:

| Relative name | Object | Created |
|---|---|---|
| `index`, `records`, `streams`, `streams/stdout`, `streams/stderr` | directory | X-1, before the genesis state, each followed by a directory barrier on its container |
| `streams/stdout/NNNNNN`, `streams/stderr/NNNNNN` | the act's two stream files | P-1, exclusively |
| `records/NNNNNN.json` | the act's per-act record | P-5 … P-8 |
| `index/NNNNNN.open.json` | open index state *I*-*n* (genesis is `000000`) | X-1 / X-2 |
| `index/NNNNNN.final.json` | the final state *F* | X-3 |

`NNNNNN` is the six-digit, zero-padded `capture_seq` or state number. An open
state's number equals the number of records it lists, and *F*'s number is the
last durable open state's number plus one, so an open and a final state never
share a name.

**Every subdirectory is created in X-1**, before the genesis state is
published. C-6 requires the creation of *any* subdirectory to be made durable
before the genesis state, so no act creates one. The nesting is still two deep,
which is what the recursive comparison has to handle.

**There is no temporary name.** Maintainer decision, 2026-09-27, on the P-7
publication primitive: a record or index state is written into an *unnamed*
`O_TMPFILE` inode in the directory that will hold it, synchronized, and then
given its first and only name by one `linkat` that fails with `EEXIST` rather
than replace anything. No reader can mistake an unfinished file for a published
one because an unfinished file has no name at all, and a failure before the link
leaves nothing behind. This is a stated deviation from P-5's "temporary name"
and P-7's "rename", recorded in the RP-11 handback for review.

## The one relative-name representation

A relative name is **the tuple of its components as raw bytes**, and two names
are the same name exactly when those tuples are equal. There is no decoding, no
case folding, no Unicode normalization and no path normalization anywhere in the
comparison. A component is non-empty, contains neither `/` (0x2F) nor NUL, and
is neither `.` nor `..`; an observed directory entry that violates that is an
ambiguous name and stops B0-RA.

Every name the mechanism **creates** is ASCII and matches the grammar above, so
its text form is its bytes. An observed name is displayed by escaping every byte
outside 0x21 … 0x7E, and the backslash, as `\\xHH`, and joining components with
`/`. That display form is injective, so a reported set difference can never show
two different observed names as one.

## Canonical encodings

A record and an index state are one line of JSON: keys sorted, no insignificant
whitespace, ASCII only with `\\u` escapes, no floating-point value, and a single
trailing newline. A parser **re-encodes what it parsed and requires the same
bytes**, so a document has exactly one accepted encoding; a duplicate key, a
reordered key, extra whitespace or a non-canonical escape is refused rather than
read. The SHA-256 of those exact bytes is the object's digest.

## The handback binding

B0-RA takes the Pass A capture root, the final state's name, the capture index
SHA-256 and the X-3 and X-4 lines from the digest-pinned Pass A handback, "as
recorded and never re-typed, inferred or supplied by the operator". The §14
template's prose lines are not a parseable format — a root path followed by a
full stop is ambiguous — so RP-11 fixes one: a single fenced block,
`HandbackBinding.render()`, that the Pass A handback carries verbatim, and that
`parse_handback_binding` reads and nothing else. Pinning that block into §14 is
an amendment of the draft, which this pass does not make; it is returned as an
open question.
"""
from __future__ import annotations

import hashlib
import json
import re
import stat
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Iterable, Mapping, Sequence

from .errors import HarnessError

# ---------------------------------------------------------------------------
# Schema identifiers
# ---------------------------------------------------------------------------

RECORD_SCHEMA = "rp11-capture-record/1"
INDEX_SCHEMA = "rp11-capture-index/1"
BINDING_FORMAT = "rp11-capture-binding/1"
TOOL_DIGEST_SCHEMA = "rp11-capture-tool/1"

#: The opening line of the handback binding block, exactly. It may occur once.
BINDING_FENCE = "```rp11-capture-binding"
BINDING_FENCE_CLOSE = "```"

# ---------------------------------------------------------------------------
# Bounds and grammars
# ---------------------------------------------------------------------------

SEQUENCE_WIDTH = 6
MAX_SEQUENCE = 999_999
#: The largest per-stream bound a caller may declare (C-2). A bound is part of
#: each act's request and of its record; this is only the ceiling on it.
MAX_STREAM_BOUND_BYTES = 1 << 30
MAX_ARGV_ELEMENTS = 4096
MAX_ROOT_LENGTH = 4096

#: `pass_id` and `step_or_case_id`. The same shape as `participants.RUN_IDENTIFIER`.
IDENTIFIER = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
#: A stop reason recorded in a terminal status: a short fixed-vocabulary token,
#: never an operating-system message, a path or a byte of command output.
REASON = re.compile(r"\A[a-z0-9][a-z0-9-]{0,63}\Z")
SHA256_HEX = re.compile(r"\A[0-9a-f]{64}\Z")
UTC_TIMESTAMP = re.compile(
    r"\A[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z\Z"
)
#: One component of a capture root. Deliberately narrower than POSIX: the root
#: is written byte for byte into a Markdown handback and compared byte for byte
#: by B0-RA, so a character that needs quoting, a leading dot, `.` and `..` are
#: all refused rather than represented.
ROOT_COMPONENT = re.compile(r"\A[A-Za-z0-9_-][A-Za-z0-9._-]{0,254}\Z")
#: One component of a name the mechanism creates.
CREATED_COMPONENT = re.compile(r"\A[a-z0-9][a-z0-9._-]{0,63}\Z")

# ---------------------------------------------------------------------------
# The fixed layout
# ---------------------------------------------------------------------------

INDEX_DIRECTORY = "index"
RECORDS_DIRECTORY = "records"
STREAMS_DIRECTORY = "streams"
STDOUT_DIRECTORY = "streams/stdout"
STDERR_DIRECTORY = "streams/stderr"

#: Every subdirectory, in creation order: a parent always precedes its child.
SUBDIRECTORIES = (
    INDEX_DIRECTORY,
    RECORDS_DIRECTORY,
    STREAMS_DIRECTORY,
    STDOUT_DIRECTORY,
    STDERR_DIRECTORY,
)

#: C-7.
DIRECTORY_MODE = 0o700
FILE_MODE = 0o600

STDOUT = "stdout"
STDERR = "stderr"
STREAMS = (STDOUT, STDERR)

_STREAM_NAME = re.compile(r"\Astreams/(stdout|stderr)/([0-9]{6})\Z")
_RECORD_NAME = re.compile(r"\Arecords/([0-9]{6})\.json\Z")
_OPEN_STATE_NAME = re.compile(r"\Aindex/([0-9]{6})\.open\.json\Z")
_FINAL_STATE_NAME = re.compile(r"\Aindex/([0-9]{6})\.final\.json\Z")

# ---------------------------------------------------------------------------
# Refusal
# ---------------------------------------------------------------------------

#: Every classification a `CaptureContractRefused` may carry.
CONTRACT_REFUSALS = frozenset(
    {
        "malformed-identifier",
        "malformed-root",
        "malformed-name",
        "malformed-document",
        "non-canonical-document",
        "duplicate-key",
        "schema-mismatch",
        "sequence-out-of-range",
        "record-list-gap",
        "stream-name-mismatch",
        "duplicate-accounted-name",
        "malformed-binding",
        "binding-absent",
        "binding-ambiguous",
        "malformed-timestamp",
        "malformed-digest",
        "malformed-argv",
        "source-set-mismatch",
    }
)


class CaptureContractRefused(HarnessError):
    """A value or document does not satisfy the RP-11 contract.

    `classification` is one of `CONTRACT_REFUSALS`. The message is for an
    operator reading a traceback and carries no byte of a stream.
    """

    def __init__(self, classification: str, detail: str = "") -> None:
        if classification not in CONTRACT_REFUSALS:
            raise ValueError(f"unknown contract refusal {classification!r}")
        self.classification = classification
        super().__init__(f"{classification}: {detail}" if detail else classification)


def _require(condition: bool, classification: str, detail: str = "") -> None:
    if not condition:
        raise CaptureContractRefused(classification, detail)


# ---------------------------------------------------------------------------
# Identifiers, digests, timestamps
# ---------------------------------------------------------------------------


def require_identifier(value: object, what: str) -> str:
    _require(
        isinstance(value, str) and bool(IDENTIFIER.match(value)),
        "malformed-identifier",
        what,
    )
    return value  # type: ignore[return-value]


def require_sha256(value: object, what: str) -> str:
    _require(
        isinstance(value, str) and bool(SHA256_HEX.match(value)),
        "malformed-digest",
        what,
    )
    return value  # type: ignore[return-value]


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def format_utc(moment: datetime) -> str:
    """C-4's `YYYY-MM-DDTHH:MM:SS.ffffffZ`, from an aware UTC instant only."""
    offset = moment.utcoffset()
    _require(
        offset is not None and offset.total_seconds() == 0,
        "malformed-timestamp",
        "the client clock must supply an aware UTC instant",
    )
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _require_timestamp(value: object, what: str) -> str:
    _require(
        isinstance(value, str) and bool(UTC_TIMESTAMP.match(value)),
        "malformed-timestamp",
        what,
    )
    return value  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Capture roots
# ---------------------------------------------------------------------------


def parse_capture_root(text: object) -> tuple[str, ...]:
    """The root's components, or a refusal. No normalization is applied.

    Absolute; no empty, `.` or `..` component; no trailing slash; every
    component matches `ROOT_COMPONENT`. `/` itself is not a capture root.
    """
    _require(isinstance(text, str), "malformed-root", "not a string")
    assert isinstance(text, str)
    _require(0 < len(text) <= MAX_ROOT_LENGTH, "malformed-root", "length")
    _require(text.startswith("/"), "malformed-root", "not absolute")
    components = tuple(text.split("/")[1:])
    _require(bool(components), "malformed-root", "no component")
    for component in components:
        _require(
            bool(ROOT_COMPONENT.match(component)),
            "malformed-root",
            "a component is empty, `.`, `..` or outside the root grammar",
        )
    return components


def roots_overlap(first: str, second: str) -> bool:
    """True when the two roots are equal or one lies within the other (C-6)."""
    a = parse_capture_root(first)
    b = parse_capture_root(second)
    shorter = min(len(a), len(b))
    return a[:shorter] == b[:shorter]


# ---------------------------------------------------------------------------
# Relative names
# ---------------------------------------------------------------------------


class ObjectType(str, Enum):
    """An object's type as `lstat` reports it. Symbolic links are never followed."""

    REGULAR = "regular"
    DIRECTORY = "directory"
    SYMLINK = "symlink"
    FIFO = "fifo"
    SOCKET = "socket"
    CHARACTER_DEVICE = "character-device"
    BLOCK_DEVICE = "block-device"
    UNKNOWN = "unknown"


def object_type_of_mode(mode: int) -> ObjectType:
    if stat.S_ISREG(mode):
        return ObjectType.REGULAR
    if stat.S_ISDIR(mode):
        return ObjectType.DIRECTORY
    if stat.S_ISLNK(mode):
        return ObjectType.SYMLINK
    if stat.S_ISFIFO(mode):
        return ObjectType.FIFO
    if stat.S_ISSOCK(mode):
        return ObjectType.SOCKET
    if stat.S_ISCHR(mode):
        return ObjectType.CHARACTER_DEVICE
    if stat.S_ISBLK(mode):
        return ObjectType.BLOCK_DEVICE
    return ObjectType.UNKNOWN


def _escape_component(component: bytes) -> str:
    return "".join(
        chr(byte) if 0x21 <= byte <= 0x7E and byte != 0x5C else f"\\x{byte:02x}"
        for byte in component
    )


@dataclass(frozen=True, slots=True, order=True)
class RelativeName:
    """A name under a capture root: the tuple of its raw-byte components."""

    components: tuple[bytes, ...]

    def __post_init__(self) -> None:
        _require(bool(self.components), "malformed-name", "no component")
        for component in self.components:
            _require(
                isinstance(component, bytes)
                and component not in (b"", b".", b"..")
                and b"/" not in component
                and b"\0" not in component,
                "malformed-name",
                "a component is empty, `.`, `..`, or contains `/` or NUL",
            )

    @classmethod
    def created(cls, text: str) -> "RelativeName":
        """A name the mechanism creates or a final state accounts for.

        ASCII, every component in `CREATED_COMPONENT`. This is how every name a
        record, an index state or a binding carries is parsed.
        """
        _require(isinstance(text, str) and text.isascii(), "malformed-name", "not ASCII")
        parts = text.split("/")
        for part in parts:
            _require(
                bool(CREATED_COMPONENT.match(part)),
                "malformed-name",
                "a component is outside the created-name grammar",
            )
        return cls(tuple(part.encode("ascii") for part in parts))

    def child(self, component: bytes) -> "RelativeName":
        return RelativeName((*self.components, component))

    @property
    def display(self) -> str:
        """The injective display form: printable ASCII kept, all else `\\xHH`."""
        return "/".join(_escape_component(part) for part in self.components)

    @property
    def parent(self) -> "RelativeName | None":
        return RelativeName(self.components[:-1]) if len(self.components) > 1 else None


def stream_name(capture_seq: int, stream: str) -> str:
    _require_sequence(capture_seq, minimum=1)
    _require(stream in STREAMS, "malformed-name", "unknown stream")
    return f"{STREAMS_DIRECTORY}/{stream}/{capture_seq:0{SEQUENCE_WIDTH}d}"


def record_name(capture_seq: int) -> str:
    _require_sequence(capture_seq, minimum=1)
    return f"{RECORDS_DIRECTORY}/{capture_seq:0{SEQUENCE_WIDTH}d}.json"


def open_state_name(state_number: int) -> str:
    _require_sequence(state_number, minimum=0)
    return f"{INDEX_DIRECTORY}/{state_number:0{SEQUENCE_WIDTH}d}.open.json"


def final_state_name(state_number: int) -> str:
    _require_sequence(state_number, minimum=1)
    return f"{INDEX_DIRECTORY}/{state_number:0{SEQUENCE_WIDTH}d}.final.json"


def final_state_number(name: str) -> int:
    """The state number a final-state name carries, or a refusal."""
    match = _FINAL_STATE_NAME.match(name) if isinstance(name, str) else None
    _require(match is not None, "malformed-name", "not a final-state name")
    assert match is not None
    number = int(match.group(1))
    _require_sequence(number, minimum=1)
    return number


def is_final_state_name(name: RelativeName) -> bool:
    try:
        text = b"/".join(name.components).decode("ascii")
    except UnicodeDecodeError:
        return False
    return bool(_FINAL_STATE_NAME.match(text))


def is_record_name(name: RelativeName) -> bool:
    try:
        text = b"/".join(name.components).decode("ascii")
    except UnicodeDecodeError:
        return False
    return bool(_RECORD_NAME.match(text))


def _is_unadmittable_name(text: str) -> bool:
    """Only a name the mechanism itself creates by a fixed rule can be unadmitted.

    A stream file, a record or an open index state. Subdirectories are their own
    category and a final state cannot record itself.
    """
    for pattern in (_STREAM_NAME, _RECORD_NAME, _OPEN_STATE_NAME):
        match = pattern.match(text)
        if match is not None:
            return int(match.groups()[-1]) >= (0 if pattern is _OPEN_STATE_NAME else 1)
    return False


def _require_sequence(value: object, *, minimum: int) -> None:
    _require(
        isinstance(value, int)
        and not isinstance(value, bool)
        and minimum <= value <= MAX_SEQUENCE,
        "sequence-out-of-range",
    )


# ---------------------------------------------------------------------------
# Canonical JSON
# ---------------------------------------------------------------------------


def canonical_bytes(document: Mapping[str, object]) -> bytes:
    text = json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    return (text + "\n").encode("ascii")


def _no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    keys = [key for key, _ in pairs]
    _require(len(keys) == len(set(keys)), "duplicate-key")
    return dict(pairs)


def _refuse_constant(_: str) -> object:
    raise CaptureContractRefused("malformed-document", "a non-finite number")


def _refuse_float(_: str) -> object:
    raise CaptureContractRefused("malformed-document", "a floating-point number")


def parse_canonical(data: bytes) -> dict[str, object]:
    """Parse one canonical document, refusing every other encoding of it."""
    _require(isinstance(data, bytes), "malformed-document", "not bytes")
    _require(data.endswith(b"\n") and data.count(b"\n") == 1, "malformed-document", "not one line")
    try:
        text = data.decode("ascii")
        document = json.loads(
            text,
            object_pairs_hook=_no_duplicate_keys,
            parse_constant=_refuse_constant,
            parse_float=_refuse_float,
        )
    except CaptureContractRefused:
        raise
    except (UnicodeDecodeError, ValueError) as error:
        raise CaptureContractRefused("malformed-document", type(error).__name__) from None
    _require(isinstance(document, dict), "malformed-document", "not an object")
    _require(canonical_bytes(document) == data, "non-canonical-document")
    return document


def _exact_keys(document: Mapping[str, object], keys: Iterable[str], what: str) -> None:
    _require(set(document) == set(keys), "schema-mismatch", what)


def _require_int(value: object, what: str, *, minimum: int = 0) -> int:
    _require(
        isinstance(value, int) and not isinstance(value, bool) and value >= minimum,
        "malformed-document",
        what,
    )
    return value  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# argv
# ---------------------------------------------------------------------------


def validate_argv(argv: object) -> tuple[str, ...]:
    """C-1: an explicit, non-empty sequence of strings, `argv[0]` absolute.

    There is no shell anywhere in RP-11, so the command text as issued and the
    vector the client process received are the same object. `argv[0]` must be
    absolute so that no `PATH` lookup chooses what runs.
    """
    _require(
        isinstance(argv, (tuple, list)) and 0 < len(argv) <= MAX_ARGV_ELEMENTS,
        "malformed-argv",
        "argv is an explicit, non-empty sequence",
    )
    assert isinstance(argv, (tuple, list))
    for element in argv:
        _require(
            isinstance(element, str) and "\0" not in element,
            "malformed-argv",
            "every element is a string without NUL",
        )
    _require(argv[0].startswith("/"), "malformed-argv", "argv[0] is absolute")
    return tuple(argv)


# ---------------------------------------------------------------------------
# The per-act record (C-5)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class StreamBinding:
    name: str
    sha256: str
    size: int

    def as_document(self) -> dict[str, object]:
        return {"name": self.name, "sha256": self.sha256, "size": self.size}


@dataclass(frozen=True, slots=True)
class ExitOutcome:
    """C-4: `status` with the exact exit code, or `signal` with its number."""

    kind: str
    value: int

    def __post_init__(self) -> None:
        _require(self.kind in ("status", "signal"), "malformed-document", "exit kind")
        _require_int(self.value, "exit value")

    @classmethod
    def from_returncode(cls, returncode: int) -> "ExitOutcome":
        return cls("signal", -returncode) if returncode < 0 else cls("status", returncode)


_RECORD_KEYS = (
    "argv",
    "capture_seq",
    "clock_source",
    "ended_utc",
    "exit",
    "pass_id",
    "schema",
    "shell",
    "started_utc",
    "stderr",
    "stdout",
    "step_or_case_id",
    "stream_bound_bytes",
)


@dataclass(frozen=True, slots=True)
class CaptureRecord:
    pass_id: str
    capture_seq: int
    step_or_case_id: str
    argv: tuple[str, ...]
    clock_source: str
    started_utc: str
    ended_utc: str
    exit: ExitOutcome
    stream_bound_bytes: int
    stdout: StreamBinding
    stderr: StreamBinding

    def __post_init__(self) -> None:
        require_identifier(self.pass_id, "pass_id")
        _require_sequence(self.capture_seq, minimum=1)
        require_identifier(self.step_or_case_id, "step_or_case_id")
        validate_argv(self.argv)
        _require(
            isinstance(self.clock_source, str) and 0 < len(self.clock_source) <= 200,
            "malformed-document",
            "clock_source",
        )
        _require_timestamp(self.started_utc, "started_utc")
        _require_timestamp(self.ended_utc, "ended_utc")
        _require(
            isinstance(self.stream_bound_bytes, int)
            and 0 < self.stream_bound_bytes <= MAX_STREAM_BOUND_BYTES,
            "malformed-document",
            "stream_bound_bytes",
        )
        for stream, binding in ((STDOUT, self.stdout), (STDERR, self.stderr)):
            _require(
                binding.name == stream_name(self.capture_seq, stream),
                "stream-name-mismatch",
                stream,
            )
            require_sha256(binding.sha256, f"{stream} sha256")
            _require(
                0 <= _require_int(binding.size, f"{stream} size") <= self.stream_bound_bytes,
                "malformed-document",
                f"{stream} size exceeds the declared bound",
            )

    def as_document(self) -> dict[str, object]:
        return {
            "schema": RECORD_SCHEMA,
            "pass_id": self.pass_id,
            "capture_seq": self.capture_seq,
            "step_or_case_id": self.step_or_case_id,
            "argv": list(self.argv),
            "shell": "none",
            "clock_source": self.clock_source,
            "started_utc": self.started_utc,
            "ended_utc": self.ended_utc,
            "exit": {"kind": self.exit.kind, "value": self.exit.value},
            "stream_bound_bytes": self.stream_bound_bytes,
            "stdout": self.stdout.as_document(),
            "stderr": self.stderr.as_document(),
        }

    def to_bytes(self) -> bytes:
        return canonical_bytes(self.as_document())

    @classmethod
    def from_bytes(cls, data: bytes) -> "CaptureRecord":
        document = parse_canonical(data)
        _exact_keys(document, _RECORD_KEYS, "record")
        _require(document["schema"] == RECORD_SCHEMA, "schema-mismatch", "record schema")
        _require(document["shell"] == "none", "schema-mismatch", "a record states no shell")
        exit_document = document["exit"]
        _require(isinstance(exit_document, dict), "malformed-document", "exit")
        assert isinstance(exit_document, dict)
        _exact_keys(exit_document, ("kind", "value"), "exit")
        bindings = []
        for stream in STREAMS:
            item = document[stream]
            _require(isinstance(item, dict), "malformed-document", stream)
            assert isinstance(item, dict)
            _exact_keys(item, ("name", "sha256", "size"), stream)
            bindings.append(
                StreamBinding(name=item["name"], sha256=item["sha256"], size=item["size"])  # type: ignore[arg-type]
            )
        argv = document["argv"]
        _require(isinstance(argv, list), "malformed-argv", "argv is a list")
        return cls(
            pass_id=document["pass_id"],  # type: ignore[arg-type]
            capture_seq=document["capture_seq"],  # type: ignore[arg-type]
            step_or_case_id=document["step_or_case_id"],  # type: ignore[arg-type]
            argv=tuple(argv),  # type: ignore[arg-type]
            clock_source=document["clock_source"],  # type: ignore[arg-type]
            started_utc=document["started_utc"],  # type: ignore[arg-type]
            ended_utc=document["ended_utc"],  # type: ignore[arg-type]
            exit=ExitOutcome(kind=exit_document["kind"], value=exit_document["value"]),  # type: ignore[arg-type]
            stream_bound_bytes=document["stream_bound_bytes"],  # type: ignore[arg-type]
            stdout=bindings[0],
            stderr=bindings[1],
        )


# ---------------------------------------------------------------------------
# Index states (C-14, §9.5.2)
# ---------------------------------------------------------------------------

OPEN = "open"
FINAL = "final"


@dataclass(frozen=True, slots=True)
class IndexEntry:
    capture_seq: int
    name: str
    sha256: str

    def __post_init__(self) -> None:
        _require_sequence(self.capture_seq, minimum=1)
        _require(self.name == record_name(self.capture_seq), "malformed-name", "record name")
        require_sha256(self.sha256, "record sha256")


@dataclass(frozen=True, slots=True)
class Terminal:
    """X-3's terminal status: `completed`, or `stopped` with where and why."""

    status: str
    capture_seq: int | None = None
    step_or_case_id: str | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        if self.status == "completed":
            _require(
                self.capture_seq is None and self.step_or_case_id is None and self.reason is None,
                "malformed-document",
                "a completed pass names no stop",
            )
            return
        _require(self.status == "stopped", "malformed-document", "terminal status")
        _require(
            isinstance(self.reason, str) and bool(REASON.match(self.reason)),
            "malformed-document",
            "stop reason",
        )
        if self.capture_seq is not None:
            _require_sequence(self.capture_seq, minimum=1)
        if self.step_or_case_id is not None:
            require_identifier(self.step_or_case_id, "stop step")

    def as_document(self) -> dict[str, object]:
        return {
            "status": self.status,
            "capture_seq": self.capture_seq,
            "step_or_case_id": self.step_or_case_id,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class UnadmittedObject:
    """An object the mechanism created that is not admitted evidence (C-15).

    Recorded by exact relative name and object type, **with no digest**. The
    type is always `regular`: every name the mechanism can leave unadmitted is a
    file, and B0-RA must refuse every other type outright.
    """

    name: str
    object_type: ObjectType

    def __post_init__(self) -> None:
        RelativeName.created(self.name)
        _require(_is_unadmittable_name(self.name), "malformed-name", "not an unadmittable name")
        _require(self.object_type is ObjectType.REGULAR, "malformed-document", "unadmitted type")


_OPEN_KEYS = (
    "capture_root",
    "pass_id",
    "previous_state_sha256",
    "records",
    "schema",
    "state_number",
    "status",
    "tool_sha256",
)
_FINAL_KEYS = (*_OPEN_KEYS, "subdirectories", "terminal", "unadmitted")


@dataclass(frozen=True, slots=True)
class IndexState:
    pass_id: str
    capture_root: str
    tool_sha256: str
    state_number: int
    previous_state_sha256: str | None
    status: str
    records: tuple[IndexEntry, ...]
    terminal: Terminal | None = None
    subdirectories: tuple[str, ...] | None = None
    unadmitted: tuple[UnadmittedObject, ...] | None = None

    def __post_init__(self) -> None:
        require_identifier(self.pass_id, "pass_id")
        parse_capture_root(self.capture_root)
        require_sha256(self.tool_sha256, "tool_sha256")
        for position, entry in enumerate(self.records, start=1):
            _require(entry.capture_seq == position, "record-list-gap")
        if self.status == OPEN:
            _require_sequence(self.state_number, minimum=0)
            _require(self.state_number == len(self.records), "record-list-gap", "open state size")
            _require(
                (self.state_number == 0) == (self.previous_state_sha256 is None),
                "malformed-document",
                "only the genesis state has no predecessor",
            )
            _require(
                self.terminal is None and self.subdirectories is None and self.unadmitted is None,
                "schema-mismatch",
                "an open state carries no final fields",
            )
        else:
            _require(self.status == FINAL, "schema-mismatch", "status")
            _require_sequence(self.state_number, minimum=1)
            _require(self.state_number == len(self.records) + 1, "record-list-gap", "final size")
            _require(self.previous_state_sha256 is not None, "malformed-document", "predecessor")
            _require(self.terminal is not None, "schema-mismatch", "terminal")
            _require(
                self.subdirectories == tuple(sorted(SUBDIRECTORIES)),
                "schema-mismatch",
                "a final state records exactly the mechanism's subdirectories",
            )
            _require(self.unadmitted is not None, "schema-mismatch", "unadmitted")
            assert self.unadmitted is not None
            names = [item.name for item in self.unadmitted]
            _require(names == sorted(set(names)), "duplicate-accounted-name", "unadmitted")
        if self.previous_state_sha256 is not None:
            require_sha256(self.previous_state_sha256, "previous_state_sha256")

    @property
    def name(self) -> str:
        if self.status == OPEN:
            return open_state_name(self.state_number)
        return final_state_name(self.state_number)

    def as_document(self) -> dict[str, object]:
        document: dict[str, object] = {
            "schema": INDEX_SCHEMA,
            "pass_id": self.pass_id,
            "capture_root": self.capture_root,
            "tool_sha256": self.tool_sha256,
            "state_number": self.state_number,
            "previous_state_sha256": self.previous_state_sha256,
            "status": self.status,
            "records": [[e.capture_seq, e.name, e.sha256] for e in self.records],
        }
        if self.status == FINAL:
            assert self.terminal is not None and self.unadmitted is not None
            document["terminal"] = self.terminal.as_document()
            document["subdirectories"] = list(self.subdirectories or ())
            document["unadmitted"] = [
                {"name": item.name, "type": item.object_type.value} for item in self.unadmitted
            ]
        return document

    def to_bytes(self) -> bytes:
        return canonical_bytes(self.as_document())

    @classmethod
    def from_bytes(cls, data: bytes) -> "IndexState":
        document = parse_canonical(data)
        _require(document.get("schema") == INDEX_SCHEMA, "schema-mismatch", "index schema")
        status = document.get("status")
        _exact_keys(document, _FINAL_KEYS if status == FINAL else _OPEN_KEYS, "index state")
        raw_records = document["records"]
        _require(isinstance(raw_records, list), "malformed-document", "records")
        assert isinstance(raw_records, list)
        entries = []
        for item in raw_records:
            _require(isinstance(item, list) and len(item) == 3, "malformed-document", "entry")
            entries.append(IndexEntry(capture_seq=item[0], name=item[1], sha256=item[2]))
        terminal = subdirectories = unadmitted = None
        if status == FINAL:
            raw_terminal = document["terminal"]
            _require(isinstance(raw_terminal, dict), "malformed-document", "terminal")
            assert isinstance(raw_terminal, dict)
            _exact_keys(raw_terminal, ("capture_seq", "reason", "status", "step_or_case_id"), "terminal")
            terminal = Terminal(**raw_terminal)  # type: ignore[arg-type]
            raw_subdirectories = document["subdirectories"]
            _require(isinstance(raw_subdirectories, list), "malformed-document", "subdirectories")
            subdirectories = tuple(raw_subdirectories)  # type: ignore[arg-type]
            raw_unadmitted = document["unadmitted"]
            _require(isinstance(raw_unadmitted, list), "malformed-document", "unadmitted")
            assert isinstance(raw_unadmitted, list)
            parsed = []
            for item in raw_unadmitted:
                _require(isinstance(item, dict), "malformed-document", "unadmitted item")
                _exact_keys(item, ("name", "type"), "unadmitted item")
                try:
                    kind = ObjectType(item["type"])
                except ValueError:
                    raise CaptureContractRefused("malformed-document", "unadmitted type") from None
                parsed.append(UnadmittedObject(name=item["name"], object_type=kind))
            unadmitted = tuple(parsed)
        return cls(
            pass_id=document["pass_id"],  # type: ignore[arg-type]
            capture_root=document["capture_root"],  # type: ignore[arg-type]
            tool_sha256=document["tool_sha256"],  # type: ignore[arg-type]
            state_number=document["state_number"],  # type: ignore[arg-type]
            previous_state_sha256=document["previous_state_sha256"],  # type: ignore[arg-type]
            status=status,  # type: ignore[arg-type]
            records=tuple(entries),
            terminal=terminal,
            subdirectories=subdirectories,
            unadmitted=unadmitted,
        )


# ---------------------------------------------------------------------------
# The accounted set (B0-RA condition 5)
# ---------------------------------------------------------------------------

CATEGORY_FINAL = "final-state"
CATEGORY_CHAIN = "chain-state"
CATEGORY_RECORD = "record"
CATEGORY_STREAM = "stream"
CATEGORY_SUBDIRECTORY = "subdirectory"
CATEGORY_UNADMITTED = "unadmitted"


@dataclass(frozen=True, slots=True)
class AccountedObject:
    object_type: ObjectType
    category: str


def accounted_objects(
    final: IndexState, records: Sequence[CaptureRecord]
) -> dict[RelativeName, AccountedObject]:
    """*R*: every name *F* and the fixed rules account for, each exactly once.

    *F* itself, each state of *F*'s chain (by the fixed naming rule from its
    number), each listed record, each stream file a listed record binds, each
    recorded subdirectory and each recorded unadmitted object. A name in two
    categories, or twice in one, is `duplicate-accounted-name`.
    """
    _require(final.status == FINAL, "schema-mismatch", "R is formed from a final state")
    assert final.unadmitted is not None and final.subdirectories is not None
    _require(
        [record.capture_seq for record in records]
        == [entry.capture_seq for entry in final.records],
        "record-list-gap",
        "records supplied for R",
    )
    items: list[tuple[str, ObjectType, str]] = [(final.name, ObjectType.REGULAR, CATEGORY_FINAL)]
    items += [
        (open_state_name(number), ObjectType.REGULAR, CATEGORY_CHAIN)
        for number in range(final.state_number)
    ]
    for entry, record in zip(final.records, records):
        items.append((entry.name, ObjectType.REGULAR, CATEGORY_RECORD))
        items.append((record.stdout.name, ObjectType.REGULAR, CATEGORY_STREAM))
        items.append((record.stderr.name, ObjectType.REGULAR, CATEGORY_STREAM))
    items += [(name, ObjectType.DIRECTORY, CATEGORY_SUBDIRECTORY) for name in final.subdirectories]
    items += [(item.name, item.object_type, CATEGORY_UNADMITTED) for item in final.unadmitted]
    accounted: dict[RelativeName, AccountedObject] = {}
    for text, kind, category in items:
        name = RelativeName.created(text)
        _require(name not in accounted, "duplicate-accounted-name", text)
        accounted[name] = AccountedObject(object_type=kind, category=category)
    return accounted


# ---------------------------------------------------------------------------
# The handback binding
# ---------------------------------------------------------------------------

X3_SUCCEEDED = "succeeded"
X3_FAILED = "failed"
X3_NOT_MADE = "not-made"
X4_VALID = "valid"
X4_INCONCLUSIVE = "inconclusive"
NONE = "none"

_BINDING_KEYS = (
    "format",
    "pass_id",
    "capture_root",
    "x3_outcome",
    "x4_validity",
    "final_state",
    "capture_index_sha256",
)


@dataclass(frozen=True, slots=True)
class HandbackBinding:
    """The fixed contract fields B0-RA takes from the Pass A handback."""

    pass_id: str
    capture_root: str
    x3_outcome: str
    x4_validity: str
    final_state: str | None
    capture_index_sha256: str | None

    def __post_init__(self) -> None:
        require_identifier(self.pass_id, "pass_id")
        parse_capture_root(self.capture_root)
        _require(
            self.x3_outcome in (X3_SUCCEEDED, X3_FAILED, X3_NOT_MADE),
            "malformed-binding",
            "x3_outcome",
        )
        _require(self.x4_validity in (X4_VALID, X4_INCONCLUSIVE), "malformed-binding", "x4")
        if self.final_state is not None:
            final_state_number(self.final_state)
        if self.capture_index_sha256 is not None:
            require_sha256(self.capture_index_sha256, "capture_index_sha256")

    def render(self) -> str:
        values = (
            BINDING_FORMAT,
            self.pass_id,
            self.capture_root,
            self.x3_outcome,
            self.x4_validity,
            self.final_state or NONE,
            self.capture_index_sha256 or NONE,
        )
        lines = [BINDING_FENCE]
        lines += [f"{key}: {value}" for key, value in zip(_BINDING_KEYS, values)]
        lines.append(BINDING_FENCE_CLOSE)
        return "\n".join(lines) + "\n"


def parse_handback_binding(data: bytes) -> HandbackBinding:
    """The one binding block of an authenticated handback, and nothing else.

    Exactly one line equal to `BINDING_FENCE`, and the fence text nowhere else;
    exactly the seven keys in their fixed order, each `key: value` with one
    space; the closing fence immediately after. No other line of the handback is
    read.
    """
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise CaptureContractRefused("malformed-binding", "not UTF-8") from None
    _require(text.count("rp11-capture-binding") > 0, "binding-absent")
    lines = text.split("\n")
    openings = [index for index, line in enumerate(lines) if line == BINDING_FENCE]
    _require(
        len(openings) == 1 and text.count(BINDING_FENCE) == 1,
        "binding-ambiguous",
        "the binding block occurs exactly once",
    )
    start = openings[0] + 1
    body = lines[start : start + len(_BINDING_KEYS)]
    _require(len(body) == len(_BINDING_KEYS), "malformed-binding", "truncated")
    _require(
        start + len(_BINDING_KEYS) < len(lines)
        and lines[start + len(_BINDING_KEYS)] == BINDING_FENCE_CLOSE,
        "malformed-binding",
        "the block closes after its seven fields",
    )
    values: dict[str, str] = {}
    for key, line in zip(_BINDING_KEYS, body):
        prefix = f"{key}: "
        _require(line.startswith(prefix), "malformed-binding", key)
        value = line[len(prefix) :]
        _require(
            bool(value) and value == value.strip() and "\r" not in value,
            "malformed-binding",
            key,
        )
        values[key] = value
    _require(values["format"] == BINDING_FORMAT, "malformed-binding", "format")
    return HandbackBinding(
        pass_id=values["pass_id"],
        capture_root=values["capture_root"],
        x3_outcome=values["x3_outcome"],
        x4_validity=values["x4_validity"],
        final_state=None if values["final_state"] == NONE else values["final_state"],
        capture_index_sha256=(
            None if values["capture_index_sha256"] == NONE else values["capture_index_sha256"]
        ),
    )


# ---------------------------------------------------------------------------
# PIN.capture_tool_sha256
# ---------------------------------------------------------------------------

#: The source files that make up the capture mechanism. Their digest is what an
#: index state carries as `tool_sha256` and what A0-08/B0-08 compare with
#: `PIN.capture_tool_sha256`. The value is **supplied from outside** — computed
#: here only so a reviewer can re-derive it — and nothing in RP-11 compares it
#: with an expectation read from this tree.
RP11_SOURCES = (
    "tools/phase_5_0_evidence/capture_contract.py",
    "tools/phase_5_0_evidence/errors.py",
    "tools/phase_5_0_evidence/execution/boundary.py",
    "tools/phase_5_0_evidence/execution/capture_mechanism.py",
    "tools/phase_5_0_evidence/execution/capture_store.py",
    "tools/phase_5_0_evidence/execution/descriptors.py",
    "tools/phase_5_0_evidence/execution/retention_check.py",
)


def capture_tool_sha256(source_bytes: Mapping[str, bytes]) -> str:
    _require(set(source_bytes) == set(RP11_SOURCES), "source-set-mismatch")
    document = {
        "schema": TOOL_DIGEST_SCHEMA,
        "sources": [[name, sha256_hex(source_bytes[name])] for name in RP11_SOURCES],
    }
    return sha256_hex(canonical_bytes(document))


__all__ = [
    "BINDING_FENCE",
    "BINDING_FORMAT",
    "CONTRACT_REFUSALS",
    "DIRECTORY_MODE",
    "FILE_MODE",
    "INDEX_DIRECTORY",
    "MAX_STREAM_BOUND_BYTES",
    "RECORDS_DIRECTORY",
    "RP11_SOURCES",
    "STDERR",
    "STDERR_DIRECTORY",
    "STDOUT",
    "STDOUT_DIRECTORY",
    "STREAMS",
    "SUBDIRECTORIES",
    "X3_FAILED",
    "X3_NOT_MADE",
    "X3_SUCCEEDED",
    "X4_INCONCLUSIVE",
    "X4_VALID",
    "AccountedObject",
    "CaptureContractRefused",
    "CaptureRecord",
    "ExitOutcome",
    "HandbackBinding",
    "IndexEntry",
    "IndexState",
    "ObjectType",
    "RelativeName",
    "StreamBinding",
    "Terminal",
    "UnadmittedObject",
    "accounted_objects",
    "canonical_bytes",
    "capture_tool_sha256",
    "final_state_name",
    "final_state_number",
    "format_utc",
    "is_final_state_name",
    "is_record_name",
    "object_type_of_mode",
    "open_state_name",
    "parse_canonical",
    "parse_capture_root",
    "parse_handback_binding",
    "record_name",
    "require_identifier",
    "require_sha256",
    "roots_overlap",
    "sha256_hex",
    "stream_name",
    "validate_argv",
]
