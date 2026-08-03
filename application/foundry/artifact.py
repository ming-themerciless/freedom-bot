"""Bounded, safe ingestion of a snapshot artifact — everything before parsing.

The order of operations here is the contract, not an implementation detail:

1. bound the size, before the bytes are held or hashed;
2. compute the **SHA-256 of the original bytes**, so the artifact has an
   identity even when the next step refuses it and an audit record can name
   *which* artifact was refused;
3. refuse archives, executables and anything else whose leading bytes say it is
   not a JSON document;
4. decode as UTF-8, rejecting a byte-order mark;
5. bound the nesting depth by scanning, *before* handing the text to a parser
   that would recurse through it.

Only then does `parser.py` run, and it runs outside any database transaction.

**Nothing here logs artifact content.** A snapshot holds every active
character's mechanics; a refusal message names the checksum, the limit and the
offset, never the bytes. `SnapshotArtifact` deliberately has no `__repr__` that
could put the document into a traceback.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from domain.foundry import SnapshotChecksum

#: 64 MiB. A real Actor is 1.1–3.3 MB of JSON (foundry-mapping F-F5), so this
#: holds a plausible active folder with headroom while keeping the refusal far
#: below anything that could exhaust memory.
DEFAULT_MAX_BYTES = 64 * 1024 * 1024

#: Deep enough for any `dnd5e` Actor, shallow enough that a parser cannot be
#: driven into unbounded recursion by a hand-built document.
DEFAULT_MAX_DEPTH = 64

#: Read in fixed chunks so a file that grew between `stat` and `read` still
#: cannot be pulled into memory past the bound.
_CHUNK = 1024 * 1024

#: Leading byte signatures that are certainly not a JSON document. Refused by
#: shape rather than by extension, because an extension is caller-supplied.
_REFUSED_SIGNATURES: tuple[tuple[bytes, str], ...] = (
    (b"PK\x03\x04", "a ZIP archive"),
    (b"PK\x05\x06", "an empty ZIP archive"),
    (b"PK\x07\x08", "a spanned ZIP archive"),
    (b"\x1f\x8b", "a gzip archive"),
    (b"BZh", "a bzip2 archive"),
    (b"\xfd7zXZ\x00", "an xz archive"),
    (b"7z\xbc\xaf\x27\x1c", "a 7-Zip archive"),
    (b"Rar!\x1a\x07", "a RAR archive"),
    (b"ustar", "a tar archive"),
    (b"\x7fELF", "an ELF executable"),
    (b"MZ", "a DOS/Windows executable"),
    (b"\xca\xfe\xba\xbe", "a Mach-O or Java class file"),
    (b"\xcf\xfa\xed\xfe", "a Mach-O executable"),
    (b"#!", "an executable script"),
    (b"%PDF", "a PDF document"),
    (b"\x89PNG", "a PNG image"),
    (b"SQLite format 3\x00", "an SQLite database"),
)

_UTF8_BOM = b"\xef\xbb\xbf"

#: An artifact file name is a bare name with a `.json` suffix. Anything
#: carrying a path separator, a parent reference, a control character or a
#: second extension is refused before it is used for anything at all.
_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}\.json$")


class SnapshotRejected(ValueError):
    """An artifact was refused before parsing.

    Carries the checksum when one was computed, so a refusal can be audited
    against the exact bytes that were refused.
    """

    def __init__(
        self, code: str, message: str, *, checksum: SnapshotChecksum | None = None
    ) -> None:
        super().__init__(message)
        self.code = code
        self.checksum = checksum


@dataclass(frozen=True, slots=True)
class IngestionLimits:
    max_bytes: int = DEFAULT_MAX_BYTES
    max_depth: int = DEFAULT_MAX_DEPTH

    def __post_init__(self) -> None:
        if self.max_bytes <= 0 or self.max_depth <= 0:
            raise ValueError("Ingestion limits must be positive.")


class SnapshotArtifact:
    """The original bytes of one artifact, with its identity.

    Immutable by construction and by discipline: the bytes are never handed out
    for modification, the checksum is computed once from them, and there is no
    setter. `text()` decodes; it does not re-encode, because a re-encoded
    document is a different artifact whatever it looks like.
    """

    __slots__ = ("_raw", "_checksum", "_source_name")

    def __init__(
        self, raw: bytes, checksum: SnapshotChecksum, *, source_name: str | None = None
    ) -> None:
        self._raw = bytes(raw)
        self._checksum = checksum
        self._source_name = source_name

    @property
    def checksum(self) -> SnapshotChecksum:
        return self._checksum

    @property
    def size_bytes(self) -> int:
        return len(self._raw)

    @property
    def source_name(self) -> str | None:
        """The validated file name, when the artifact came from one."""
        return self._source_name

    def raw_bytes(self) -> bytes:
        """The original bytes, for storage. Never for logging or display."""
        return self._raw

    def text(self) -> str:
        return self._raw.decode("utf-8")

    def verify(self) -> None:
        """Re-derive the checksum from the bytes and refuse a mismatch.

        Cheap insurance at the boundary between ingestion and storage: an
        artifact whose stored checksum no longer describes its bytes must never
        be presented as the snapshot that checksum identifies.
        """
        actual = hashlib.sha256(self._raw).hexdigest()
        if actual != self._checksum.hex_digest:
            raise SnapshotRejected(
                "checksum_mismatch",
                "The artifact's bytes do not hash to its recorded checksum. It "
                "is a different snapshot and cannot inherit this identity.",
                checksum=self._checksum,
            )

    def __repr__(self) -> str:  # pragma: no cover - trivial, but load-bearing
        # Deliberately never renders content: this object appears in tracebacks.
        return (
            f"<SnapshotArtifact checksum={self._checksum.short} "
            f"bytes={self.size_bytes}>"
        )


def safe_artifact_name(name: str) -> str:
    """Validate a caller-supplied artifact file name, or refuse it.

    Path-bearing input is refused rather than sanitised. Stripping a `../` and
    continuing is how a traversal becomes a stored file with an innocent name;
    the operator who supplied it is the one who should decide what they meant.
    """
    if not _SAFE_NAME.fullmatch(name):
        raise SnapshotRejected(
            "unsafe_artifact_name",
            "A snapshot file name must be a bare name ending in '.json', "
            "without directories, parent references or control characters.",
        )
    return name


def ingest_bytes(
    data: bytes,
    *,
    limits: IngestionLimits | None = None,
    source_name: str | None = None,
) -> SnapshotArtifact:
    """Turn raw bytes into an identified artifact, or refuse them."""
    limits = limits or IngestionLimits()
    if source_name is not None:
        source_name = safe_artifact_name(source_name)

    if not data:
        raise SnapshotRejected("empty_artifact", "The artifact is empty.")
    if len(data) > limits.max_bytes:
        raise SnapshotRejected(
            "artifact_too_large",
            f"The artifact is {len(data)} bytes, over the {limits.max_bytes}-byte "
            "limit. It was not parsed.",
        )

    # The identity is fixed here, before anything below can reject it, so a
    # refusal is auditable against exactly these bytes.
    checksum = SnapshotChecksum.of(data)

    _refuse_non_json_container(data, checksum)
    text = _decode(data, checksum)
    _bound_depth(text, limits.max_depth, checksum)

    return SnapshotArtifact(data, checksum, source_name=source_name)


def read_artifact(
    path: Path, *, limits: IngestionLimits | None = None
) -> SnapshotArtifact:
    """Read an artifact from disk under the same bounds.

    The size is bounded twice — once from `stat`, once while reading — because
    a file can grow between the two, and the second bound is the one that holds.
    """
    limits = limits or IngestionLimits()
    name = safe_artifact_name(path.name)

    try:
        size = path.stat().st_size
    except OSError as error:
        raise SnapshotRejected(
            "artifact_unreadable",
            "The artifact could not be read. Check that the path names a "
            "readable file.",
        ) from error
    if size > limits.max_bytes:
        raise SnapshotRejected(
            "artifact_too_large",
            f"The artifact is {size} bytes, over the {limits.max_bytes}-byte "
            "limit. It was not read.",
        )

    chunks: list[bytes] = []
    total = 0
    try:
        with path.open("rb") as handle:
            while chunk := handle.read(_CHUNK):
                total += len(chunk)
                if total > limits.max_bytes:
                    raise SnapshotRejected(
                        "artifact_too_large",
                        "The artifact grew past the size limit while it was "
                        "being read. It was not parsed.",
                    )
                chunks.append(chunk)
    except OSError as error:
        raise SnapshotRejected(
            "artifact_unreadable",
            "The artifact could not be read. Check that the path names a "
            "readable file.",
        ) from error

    return ingest_bytes(b"".join(chunks), limits=limits, source_name=name)


def _refuse_non_json_container(data: bytes, checksum: SnapshotChecksum) -> None:
    for signature, description in _REFUSED_SIGNATURES:
        # `ustar` sits at offset 257 in a tar header; the rest are leading.
        offset = 257 if signature == b"ustar" else 0
        if data[offset : offset + len(signature)] == signature:
            raise SnapshotRejected(
                "unsupported_container",
                f"The artifact is {description}, not a snapshot bundle. Only the "
                "documented JSON export bundle is accepted; archives and "
                "executables are refused unopened.",
                checksum=checksum,
            )
    if data.startswith(_UTF8_BOM):
        raise SnapshotRejected(
            "byte_order_mark",
            "The artifact begins with a UTF-8 byte-order mark. The export "
            "contract requires UTF-8 without one, because the mark changes the "
            "bytes and therefore the snapshot identity.",
            checksum=checksum,
        )
    if b"\x00" in data[:4096]:
        raise SnapshotRejected(
            "binary_artifact",
            "The artifact contains NUL bytes and is not a text document.",
            checksum=checksum,
        )


def _decode(data: bytes, checksum: SnapshotChecksum) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as error:
        # The offset is reported; the bytes at it are not.
        raise SnapshotRejected(
            "invalid_encoding",
            f"The artifact is not valid UTF-8 (first bad byte at offset "
            f"{error.start}).",
            checksum=checksum,
        ) from None


def _bound_depth(text: str, max_depth: int, checksum: SnapshotChecksum) -> None:
    """Refuse excessive nesting before a recursive parser ever sees the text.

    Scanned rather than parsed: `json.loads` recurses, so discovering the depth
    by parsing is discovering it too late. String contents are skipped so that a
    brace inside a name cannot be mistaken for structure.
    """
    depth = 0
    in_string = False
    escaped = False
    for index, character in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if character == '"':
            in_string = True
        elif character in "{[":
            depth += 1
            if depth > max_depth:
                raise SnapshotRejected(
                    "excessive_nesting",
                    f"The artifact nests deeper than {max_depth} levels (at "
                    f"character {index}). It was not parsed.",
                    checksum=checksum,
                )
        elif character in "}]":
            depth -= 1
            if depth < 0:
                raise SnapshotRejected(
                    "malformed_json",
                    f"The artifact closes a structure that was never opened (at "
                    f"character {index}).",
                    checksum=checksum,
                )
    if in_string or depth != 0:
        raise SnapshotRejected(
            "malformed_json",
            "The artifact ends inside an unterminated structure.",
            checksum=checksum,
        )
