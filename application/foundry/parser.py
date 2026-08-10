"""Parse and validate a snapshot bundle. Runs outside any transaction.

Everything this module refuses is refused *before* a state-change transaction is
opened, so a malformed, wrong-world or wrong-version artifact can never leave a
partially applied import behind: there is nothing to roll back.

The refusals fall into four groups, and each has its own code so an operator is
told what to fix rather than "import failed":

- **shape** — not JSON, not the documented bundle, an unknown top-level key;
- **deployment** — wrong world, or a (core, system) version tuple this Manager
  was not built for, failing closed with both observed and expected named;
- **folder graph** — duplicate, missing, cyclic or unselected folders;
- **Actor identity** — missing, malformed or duplicate `_id`, or an Actor
  outside the exported selection.

Ambiguity is always a refusal. A duplicate Actor id, a duplicate folder id and a
folder whose parent is absent are each a blocking issue, because the only way to
proceed past one is to guess which record was meant — and the record being
guessed at is a character.
"""
from __future__ import annotations

import json
import math
import re
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

from application.foundry.artifact import SnapshotArtifact, SnapshotRejected
from domain.foundry import (
    EXPORT_SCHEMA,
    SUPPORTED_SCHEMA_VERSIONS,
    FolderIdentity,
    FoundryActorId,
    FoundryFolderId,
    InvalidIdentityError,
    SnapshotChecksum,
    SupportedDeployment,
    WorldIdentity,
)

_REQUIRED_TOP_LEVEL = frozenset(
    {
        "schema",
        "schemaVersion",
        "exporter",
        "exportedAt",
        "world",
        "selectedFolderIds",
        "folders",
        "actors",
    }
)

_REQUIRED_WORLD_KEYS = frozenset(
    {"id", "title", "coreVersion", "systemId", "systemVersion"}
)

_REQUIRED_ACTOR_KEYS = frozenset({"id", "folderId", "name", "system", "items"})
_OPTIONAL_ACTOR_KEYS = frozenset({"img"})

_REQUIRED_FOLDER_KEYS = frozenset({"id", "name", "parentId"})

_SEMVER_ISH = re.compile(r"^[0-9A-Za-z.+-]{1,32}$")


@dataclass(frozen=True, slots=True)
class BundleLimits:
    """Structural bounds from the export contract, §1 and §2.5."""

    max_actors: int = 500
    max_folders: int = 64
    max_selected_folders: int = 8
    max_items_per_actor: int = 4000

    def __post_init__(self) -> None:
        if min(
            self.max_actors,
            self.max_folders,
            self.max_selected_folders,
            self.max_items_per_actor,
        ) <= 0:
            raise ValueError("Bundle limits must be positive.")


@dataclass(frozen=True, slots=True)
class ExporterVersion:
    id: str
    version: str

    def describe(self) -> str:
        return f"{self.id} {self.version}"


@dataclass(frozen=True, slots=True)
class SnapshotFolder:
    folder_id: FoundryFolderId
    name: str
    parent_id: FoundryFolderId | None


@dataclass(frozen=True, slots=True)
class SnapshotActor:
    """One exported Actor, with its identity separated from its document."""

    actor_id: FoundryActorId
    folder_id: FoundryFolderId
    name: str
    document: Mapping[str, object]

    def item_types(self) -> tuple[str, ...]:
        items = self.document.get("items")
        if not isinstance(items, Sequence):
            return ()
        return tuple(
            sorted(
                {
                    str(entry["type"])
                    for entry in items
                    if isinstance(entry, Mapping) and isinstance(entry.get("type"), str)
                }
            )
        )


@dataclass(frozen=True, slots=True)
class ParsedSnapshot:
    """A validated bundle. Every identity in it has already been proven unique."""

    checksum: SnapshotChecksum
    #: The size of the artifact's original bytes, carried so the immutable
    #: record can state it without the parsed snapshot holding the bytes.
    size_bytes: int
    schema_version: int
    exporter: ExporterVersion
    exported_at: datetime
    world: WorldIdentity
    folders: Mapping[str, SnapshotFolder]
    selected_folder_ids: tuple[str, ...]
    actors: tuple[SnapshotActor, ...]
    #: `True` when the bytes are byte-identical to their canonical re-encoding.
    #: Not a refusal: a differently-encoded bundle is a valid snapshot with its
    #: own identity. It is surfaced as a preview warning because a
    #: non-canonical exporter makes two exports of an unchanged world differ.
    canonical_encoding: bool

    def folder(self, folder_id: str) -> SnapshotFolder:
        try:
            return self.folders[folder_id]
        except KeyError:
            raise SnapshotRejected(
                "unknown_folder",
                f"Folder {folder_id!r} is not present in this snapshot.",
                checksum=self.checksum,
            ) from None

    def folder_path(self, folder_id: str) -> str:
        """`/actors/Parent/Child`. Built from ids; names are display only."""
        names: list[str] = []
        seen: set[str] = set()
        current: str | None = folder_id
        while current is not None:
            if current in seen:  # pragma: no cover - the graph is acyclic here
                raise SnapshotRejected(
                    "folder_cycle",
                    "The folder graph contains a cycle.",
                    checksum=self.checksum,
                )
            seen.add(current)
            node = self.folder(current)
            names.append(node.name)
            current = str(node.parent_id) if node.parent_id is not None else None
        return "/actors/" + "/".join(reversed(names))

    def folder_identity(self, folder_id: str) -> FolderIdentity:
        return FolderIdentity(
            folder_id=self.folder(folder_id).folder_id,
            path=self.folder_path(folder_id),
        )

    def selectable_folders(self) -> tuple[FolderIdentity, ...]:
        """What a Platform Administrator may choose between, in a stable order."""
        return tuple(
            self.folder_identity(folder_id)
            for folder_id in sorted(self.selected_folder_ids)
        )

    def actors_in(self, folder_id: str) -> tuple[SnapshotActor, ...]:
        if folder_id not in self.selected_folder_ids:
            raise SnapshotRejected(
                "folder_not_selected",
                f"Folder {folder_id!r} was not exported in this snapshot, so no "
                "import can be based on it.",
                checksum=self.checksum,
            )
        return tuple(
            actor for actor in self.actors if str(actor.folder_id) == folder_id
        )


#: An object key JavaScript gives numeric precedence to during ordinary object
#: enumeration. ECMAScript's **array index**, not its "integer index": a
#: canonical decimal integer in `[0, 2**32 - 2]`, so `"01"`, `"1.0"`, `"-1"` and
#: `" 1"` are ordinary string keys, and so is every canonical decimal at or
#: above `"4294967295"`.
#:
#: The upper bound is the whole point of this constant, and it was wrong until
#: 2026-08-10 (change-log C-12, correcting C-10). `OrdinaryOwnPropertyKeys`
#: hoists the keys that are *array indices* — `ToString(ToUint32(P)) is P` and
#: `ToUint32(P) ≠ 2**32 - 1` — and nothing else. `2**53 - 1` is the bound on a
#: safe integer and on an *integer index*, which is a `String.prototype`/typed-
#: array concept that ordinary object enumeration never consults. Using it made
#: Python sort `"5000000000"` before `"10000000000"` while the exporter, for
#: which both are ordinary string keys, emits them in code-point order — the
#: opposite way round.
_ARRAY_INDEX = re.compile(r"^(0|[1-9][0-9]*)$")
_MAX_ARRAY_INDEX = 2**32 - 2


def _is_array_index(key: str) -> bool:
    return bool(_ARRAY_INDEX.match(key)) and int(key) <= _MAX_ARRAY_INDEX


def _canonical_key_order(keys: Iterable[str]) -> list[str]:
    """ECMAScript own-property order over an object's keys.

    Array-index keys first, ascending **numerically**; then every other key by
    code point. The second half is ours — ECMAScript would use insertion order
    there, which is not a property a canonical form may depend on — but the
    first half is the language's, and no exporter running in a browser can
    deviate from it.

    A canonical decimal above `_MAX_ARRAY_INDEX` belongs to the *second* group.
    It looks numeric and sorts as text, which is exactly the case the previous
    bound got wrong.
    """
    # Materialised: this walks `keys` twice, and a generator would be empty on
    # the second pass — which silently encodes every object as `{}`.
    all_keys = list(keys)
    indices = sorted((k for k in all_keys if _is_array_index(k)), key=int)
    names = sorted(k for k in all_keys if not _is_array_index(k))
    return indices + names


def _nfc_keys(value: Mapping[object, object], path: str) -> dict[str, object]:
    """Each key under its NFC form, refusing two that share one.

    The contract normalises every string to NFC, keys included, so `é` as U+00E9
    and as U+0065 U+0301 are one key in the canonical form and two in the source
    document. Emitting both would produce a document carrying the same key twice
    — not a canonical form of anything — and a conforming exporter refuses to
    produce such an artifact at all (`nfc_key_collision`), so an artifact that
    contains one did not come from one.

    Refused rather than merged, matching the exporter: the two keys are
    different properties of a Foundry document, and no rule in this repository
    says which one an operator meant. Ambiguity is a refusal here as everywhere
    else in this module.
    """
    by_canonical: dict[str, object] = {}
    for key in value:
        canonical = unicodedata.normalize("NFC", str(key))
        if canonical in by_canonical:
            raise SnapshotRejected(
                "nfc_key_collision",
                f"{path} has two keys that are different strings but share one "
                "Unicode NFC form, so the artifact has no canonical form and "
                "one of the two values could not be preserved. It cannot have "
                "come from a conforming exporter.",
            )
        by_canonical[canonical] = value[key]
    return by_canonical


def _double(value: int | float, path: str) -> float:
    """The IEEE-754 double a JavaScript parser would have read this number as.

    Every number in the export contract is a double, because the only supported
    exporter is a browser and JavaScript has no other number. `json.loads` does
    not agree: it reads an integer literal as an arbitrary-precision `int`, so
    `9007199254740993` survives in Python and is `9007199254740992` in the
    exporter. Re-encoding from the Python value would report such an artifact
    canonical against bytes no exporter could have produced, so the literal is
    put through the double first and the difference shows up as the
    non-canonical warning it is.

    A literal outside the double range — `1e999`, or an integer of 400 digits —
    reads as an infinity in both languages, and that is a **refusal** rather
    than a warning: `canonical.js` refuses to emit it (`non_finite_number`),
    JSON cannot express it, and the only encodings available would change the
    value. Unlike a `-0`, which has the canonical form `0`, such a document has
    no canonical form at all.
    """
    try:
        number = float(value)
    except OverflowError:
        # An integer literal too large for a double. `JSON.parse` reads the same
        # literal as an infinity, so the two agree on the refusal below.
        number = float("inf")
    if not math.isfinite(number):
        raise SnapshotRejected(
            "non_finite_number",
            f"{path} is a number outside the range JSON can represent, so the "
            "artifact has no canonical form. It cannot have come from a "
            "conforming exporter, which refuses to emit one.",
        )
    return number


def _normalised(value: object, path: str = "$") -> object:
    """`canonical.js`'s `normalise`: NFC, canonical key order, doubles.

    Kept a separate pass from `_serialise` for the same reason the exporter
    keeps the two apart — the order the bytes come out in is then a property of
    this function, not a sort buried in the encoder.
    """
    if isinstance(value, Mapping):
        by_canonical = _nfc_keys(value, path)
        return {
            key: _normalised(by_canonical[key], f"{path}.{key}")
            for key in _canonical_key_order(by_canonical)
        }
    if isinstance(value, (list, tuple)):
        return [
            _normalised(item, f"{path}[{index}]") for index, item in enumerate(value)
        ]
    if isinstance(value, str):
        # §1 normalises *every* string, not only keys. Without this a decomposed
        # string value would be reproduced verbatim and the artifact reported
        # canonical, when the only supported exporter would have emitted the
        # composed form and different bytes.
        return unicodedata.normalize("NFC", value)
    # `bool` is a subclass of `int`, and `True` is not the number 1 here.
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float)):
        return _double(value, path)
    return value


def _shortest_decimal(value: float) -> tuple[str, int]:
    """`(s, n)`: the digits ECMAScript's `Number::toString` calls `s`, and `n`.

    `s` is the shortest digit string that reads back as `value`, with no leading
    or trailing zeros, and `n` positions the decimal point: `value` is
    `0.s × 10**n`. `repr` supplies the digits — CPython and every JavaScript
    engine compute the same shortest round-tripping decimal — and this only
    re-reads them out of Python's formatting, which is the part that differs.
    """
    mantissa, _, exponent = repr(value).partition("e")
    whole, _, fraction = mantissa.partition(".")
    # Leading zeros are positional and must be counted out of `n`; trailing ones
    # are not part of the shortest digit string.
    digits = (whole + fraction).lstrip("0")
    return digits.rstrip("0"), len(digits) + int(exponent or "0") - len(fraction)


def _ecmascript_number(value: float) -> str:
    """`Number::toString(value, 10)`, which is what `JSON.stringify` emits.

    Python's own float formatting is *not* that, and the difference is not
    cosmetic: it decides whether `canonical_encoding` is true for a conforming
    export. `repr` switches to exponent notation at `1e16` and below `1e-4`
    where ECMAScript switches at `1e21` and below `1e-6`, and it pads the
    exponent to two digits. So the exporter writes `100000000000000000000` and
    `1e-7` where Python wrote `1e+20` and `1e-07`, and every conforming artifact
    carrying such a number was reported non-canonical. dnd5e has fractional
    values — encumbrance multipliers, spell scaling, currency weight — so this
    was reachable by ordinary data, not only by a contrived document.

    The clauses below are ECMAScript 2024 §6.1.6.1.20 steps 5–10 in order, and
    are the whole specification for base 10 given `s`, `k` and `n`.
    """
    if value == 0:
        # Covers `-0.0`: `Number::toString` step 2 makes it "0" as well. A
        # document containing one therefore *has* a canonical form and is
        # reported non-canonical rather than refused — the sign cannot survive
        # JSON in either language, which is why `canonical.js` refuses to
        # *produce* one (`negative_zero`) and nothing here refuses to read one.
        return "0"
    if value < 0:
        return f"-{_ecmascript_number(-value)}"

    digits, point = _shortest_decimal(value)
    k, n = len(digits), point
    if k <= n <= 21:
        return digits + "0" * (n - k)
    if 0 < n <= 21:
        return f"{digits[:n]}.{digits[n:]}"
    if -6 < n <= 0:
        return f"0.{'0' * -n}{digits}"
    exponent = n - 1
    mantissa = digits if k == 1 else f"{digits[0]}.{digits[1:]}"
    return f"{mantissa}e{'+' if exponent >= 0 else '-'}{abs(exponent)}"


def _serialise(value: object) -> str:
    """`canonical.js`'s `serialise`: the contract's separators, no re-sorting.

    Written out rather than handed to `json.dumps` for the reason the exporter
    does not hand it to `JSON.stringify`: the number formatting is the contract
    and must be this module's own statement of it. `json.dumps` is still used
    for individual strings, where Python and ECMAScript escape identically.

    Keys arrive in canonical order from `_normalised` and are not re-sorted
    here; re-sorting would hide a `_normalised` that stopped doing it.
    """
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, float):
        return _ecmascript_number(value)
    if isinstance(value, list):
        return f"[{','.join(_serialise(item) for item in value)}]"
    if isinstance(value, dict):
        body = ",".join(
            f"{json.dumps(key, ensure_ascii=False)}:{_serialise(item)}"
            for key, item in value.items()
        )
        return f"{{{body}}}"
    # Unreachable from `parse_snapshot`, whose input is always `json.loads`
    # output that `_normalised` has already reduced to this domain.
    raise TypeError(f"{type(value).__name__} is not a JSON value.")


def canonical_bytes(document: Mapping[str, object]) -> bytes:
    """The contract's canonical encoding of a parsed document.

    Used only to *report* whether the artifact already matched it. The Manager
    never re-encodes an artifact and calls the result the same snapshot.

    **Key order is ECMAScript's, not `sort_keys=True`** — RA-2, 2026-08-09.
    The previous lexicographic order made this flag false for every real world:
    dnd5e keys scale-value advancements by class level, so an Actor with a class
    reaching level 10 carries `{"1": …, "4": …, "10": …}`, and a browser exporter
    emits those numerically however it sorts, because `Object.keys` hoists
    array-index keys. Lexicographic order wanted `"1","10","4"`, which no
    conforming JavaScript exporter can produce. A canonical form that the only
    supported exporter cannot satisfy is a defect in the form.

    **The hoisting stops at `2**32 - 2`** — C-12, 2026-08-10. Only array indices
    are hoisted, so a larger canonical decimal is an ordinary string key and
    sorts by code point. `_MAX_ARRAY_INDEX` says why in full.

    **Every string is normalised to NFC, keys included** — C-16, 2026-08-10.
    Reporting is still all this does, with one exception: a document whose keys
    collide under NFC has no canonical form, and that is a refusal
    (`nfc_key_collision`) rather than a flag. `_nfc_keys` says why.

    **Numbers are ECMAScript's, not `json.dumps`'s** — C-17, 2026-08-10. This
    used `json.dumps`, whose float formatting is a different function from
    `JSON.stringify`'s at both ends of the exponent range: the exporter emits
    `1e20` as `100000000000000000000` and `1e-7` as `1e-7`, Python as `1e+20`
    and `1e-07`. `_ecmascript_number` states the rule the exporter obeys, and
    `_double` reads every literal as the double the exporter would have. The
    second exception to reporting lives there: a literal outside the double
    range has no canonical form either (`non_finite_number`).
    """
    return f"{_serialise(_normalised(document))}\n".encode("utf-8")


def parse_snapshot(
    artifact: SnapshotArtifact,
    *,
    deployment: SupportedDeployment,
    limits: BundleLimits | None = None,
) -> ParsedSnapshot:
    """Validate `artifact` against the export contract and `deployment`."""
    limits = limits or BundleLimits()
    checksum = artifact.checksum

    def refuse(code: str, message: str) -> SnapshotRejected:
        return SnapshotRejected(code, message, checksum=checksum)

    try:
        document = json.loads(artifact.text())
    except ValueError as error:
        # The parser message can quote the document, so only the position is
        # carried through; the offending text is not.
        position = getattr(error, "pos", None)
        where = f" near character {position}" if position is not None else ""
        raise refuse(
            "malformed_json", f"The artifact is not valid JSON{where}."
        ) from None

    if not isinstance(document, Mapping):
        raise refuse(
            "unexpected_top_level",
            "The artifact's top level is not a JSON object.",
        )

    present = set(document)
    missing = sorted(_REQUIRED_TOP_LEVEL - present)
    if missing:
        raise refuse(
            "missing_top_level_key",
            f"The bundle is missing required key(s): {', '.join(missing)}.",
        )
    unknown = sorted(present - _REQUIRED_TOP_LEVEL)
    if unknown:
        # Refused rather than ignored: an artifact carrying something the
        # Manager does not understand has not been reviewed by anyone, and the
        # contract forbids every collection but actors and folders.
        raise refuse(
            "unknown_top_level_key",
            f"The bundle carries unsupported top-level key(s): "
            f"{', '.join(unknown)}. Only the documented export bundle is "
            "accepted.",
        )

    if document["schema"] != EXPORT_SCHEMA:
        raise refuse(
            "unsupported_schema",
            f"The bundle declares schema {document['schema']!r}; this Manager "
            f"reads {EXPORT_SCHEMA!r}.",
        )

    schema_version = document["schemaVersion"]
    if not isinstance(schema_version, int) or isinstance(schema_version, bool):
        raise refuse(
            "unsupported_schema_version", "`schemaVersion` must be an integer."
        )
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise refuse(
            "unsupported_schema_version",
            f"The bundle uses exporter schema version {schema_version}; this "
            f"Manager supports "
            f"{', '.join(str(v) for v in sorted(SUPPORTED_SCHEMA_VERSIONS))}. "
            "Validate the new exporter and update the pin deliberately.",
        )

    exporter = _parse_exporter(document["exporter"], refuse)
    exported_at = _parse_timestamp(document["exportedAt"], refuse)
    world = _parse_world(document["world"], refuse)

    differences = deployment.mismatches(world)
    if differences:
        raise refuse(
            "unsupported_deployment",
            "The snapshot was taken from a deployment this Manager is not "
            f"configured for: {'; '.join(differences)}. Nothing was imported.",
        )

    folders = _parse_folders(document["folders"], limits, refuse)
    selected = _parse_selection(document["selectedFolderIds"], folders, limits, refuse)
    actors = _parse_actors(document["actors"], selected, limits, refuse)

    # `canonical_bytes` reports; it refuses only when the document has no
    # canonical form at all, which today means an NFC key collision. Re-raised
    # through `refuse` so the refusal carries the checksum of the exact bytes,
    # like every other refusal in this module.
    try:
        canonical = canonical_bytes(document)
    except SnapshotRejected as rejection:
        raise refuse(rejection.code, str(rejection)) from None

    return ParsedSnapshot(
        checksum=checksum,
        size_bytes=artifact.size_bytes,
        schema_version=schema_version,
        exporter=exporter,
        exported_at=exported_at,
        world=world,
        folders=folders,
        selected_folder_ids=selected,
        actors=actors,
        canonical_encoding=canonical == artifact.raw_bytes(),
    )


def _parse_exporter(value: object, refuse) -> ExporterVersion:
    if not isinstance(value, Mapping) or set(value) != {"id", "version"}:
        raise refuse(
            "malformed_exporter", "`exporter` must hold exactly `id` and `version`."
        )
    identifier, version = value["id"], value["version"]
    if not isinstance(identifier, str) or not identifier.strip():
        raise refuse("malformed_exporter", "`exporter.id` must be a non-empty string.")
    if not isinstance(version, str) or not _SEMVER_ISH.fullmatch(version):
        raise refuse(
            "malformed_exporter",
            "`exporter.version` must be a short version string.",
        )
    return ExporterVersion(id=identifier, version=version)


def _parse_timestamp(value: object, refuse) -> datetime:
    if not isinstance(value, str):
        raise refuse("malformed_timestamp", "`exportedAt` must be a string.")
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        raise refuse(
            "malformed_timestamp",
            "`exportedAt` must be an RFC 3339 UTC instant such as "
            "'2026-08-02T09:15:00Z'.",
        ) from None
    if parsed.tzinfo is None:
        raise refuse(
            "malformed_timestamp", "`exportedAt` must carry a UTC offset."
        )
    return parsed


def _parse_world(value: object, refuse) -> WorldIdentity:
    if not isinstance(value, Mapping):
        raise refuse("malformed_world", "`world` must be an object.")
    if set(value) != _REQUIRED_WORLD_KEYS:
        expected = ", ".join(sorted(_REQUIRED_WORLD_KEYS))
        raise refuse(
            "malformed_world", f"`world` must hold exactly: {expected}."
        )
    for key in sorted(_REQUIRED_WORLD_KEYS):
        if not isinstance(value[key], str) or not value[key].strip():
            raise refuse(
                "malformed_world", f"`world.{key}` must be a non-empty string."
            )
    try:
        return WorldIdentity(
            world_id=value["id"],
            title=value["title"],
            core_version=value["coreVersion"],
            system_id=value["systemId"],
            system_version=value["systemVersion"],
        )
    except InvalidIdentityError as error:
        raise refuse("malformed_world", str(error)) from None


def _parse_folders(
    value: object, limits: BundleLimits, refuse
) -> dict[str, SnapshotFolder]:
    if not isinstance(value, list):
        raise refuse("malformed_folders", "`folders` must be an array.")
    if not value:
        raise refuse("malformed_folders", "`folders` must not be empty.")
    if len(value) > limits.max_folders:
        raise refuse(
            "too_many_folders",
            f"The bundle carries {len(value)} folders, over the "
            f"{limits.max_folders} the contract allows.",
        )

    folders: dict[str, SnapshotFolder] = {}
    for index, entry in enumerate(value):
        if not isinstance(entry, Mapping) or set(entry) != _REQUIRED_FOLDER_KEYS:
            raise refuse(
                "malformed_folders",
                f"Folder at position {index} must hold exactly id, name and "
                "parentId.",
            )
        try:
            folder_id = FoundryFolderId(str(entry["id"]))
        except InvalidIdentityError as error:
            raise refuse("malformed_folder_id", str(error)) from None
        if str(folder_id) in folders:
            raise refuse(
                "duplicate_folder_id",
                f"Folder id {folder_id} appears more than once. A duplicate "
                "identity cannot be resolved without guessing which folder was "
                "meant.",
            )
        name = entry["name"]
        if not isinstance(name, str) or not name.strip():
            raise refuse(
                "malformed_folders", f"Folder {folder_id} has no usable name."
            )
        parent_raw = entry["parentId"]
        parent: FoundryFolderId | None = None
        if parent_raw is not None:
            try:
                parent = FoundryFolderId(str(parent_raw))
            except InvalidIdentityError as error:
                raise refuse("malformed_folder_id", str(error)) from None
        folders[str(folder_id)] = SnapshotFolder(
            folder_id=folder_id, name=name, parent_id=parent
        )

    for folder in folders.values():
        if folder.parent_id is not None and str(folder.parent_id) not in folders:
            raise refuse(
                "unknown_parent_folder",
                f"Folder {folder.folder_id} names parent {folder.parent_id}, "
                "which the bundle does not contain. A folder path cannot be "
                "presented without it.",
            )

    _refuse_cycles(folders, refuse)
    return folders


def _refuse_cycles(folders: Mapping[str, SnapshotFolder], refuse) -> None:
    for start in folders:
        seen: set[str] = set()
        current: str | None = start
        while current is not None:
            if current in seen:
                raise refuse(
                    "folder_cycle",
                    f"The folder graph contains a cycle through {current}.",
                )
            seen.add(current)
            parent = folders[current].parent_id
            current = str(parent) if parent is not None else None


def _parse_selection(
    value: object,
    folders: Mapping[str, SnapshotFolder],
    limits: BundleLimits,
    refuse,
) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise refuse(
            "malformed_selection", "`selectedFolderIds` must be an array."
        )
    if not value:
        raise refuse(
            "empty_selection",
            "`selectedFolderIds` is empty, so the bundle exports no folder and "
            "there is nothing to select.",
        )
    if len(value) > limits.max_selected_folders:
        raise refuse(
            "too_many_selected_folders",
            f"The bundle selects {len(value)} folders, over the "
            f"{limits.max_selected_folders} the contract allows. Export a "
            "bounded set deliberately rather than the whole world.",
        )
    selected: list[str] = []
    for entry in value:
        identifier = str(entry)
        if identifier in selected:
            raise refuse(
                "duplicate_selected_folder",
                f"Folder {identifier} is selected more than once.",
            )
        if identifier not in folders:
            raise refuse(
                "unknown_selected_folder",
                f"Selected folder {identifier} is not present in `folders`.",
            )
        selected.append(identifier)
    return tuple(selected)


def _parse_actors(
    value: object,
    selected: tuple[str, ...],
    limits: BundleLimits,
    refuse,
) -> tuple[SnapshotActor, ...]:
    if not isinstance(value, list):
        raise refuse("malformed_actors", "`actors` must be an array.")
    if len(value) > limits.max_actors:
        raise refuse(
            "too_many_actors",
            f"The bundle carries {len(value)} Actors, over the "
            f"{limits.max_actors} the contract allows.",
        )

    actors: list[SnapshotActor] = []
    seen: dict[str, int] = {}
    for index, entry in enumerate(value):
        if not isinstance(entry, Mapping):
            raise refuse(
                "malformed_actors", f"Actor at position {index} is not an object."
            )
        present = set(entry)
        missing = sorted(_REQUIRED_ACTOR_KEYS - present)
        if missing:
            raise refuse(
                "malformed_actor",
                f"Actor at position {index} is missing: {', '.join(missing)}.",
            )
        unknown = sorted(present - _REQUIRED_ACTOR_KEYS - _OPTIONAL_ACTOR_KEYS)
        if unknown:
            # Enforces contract §3 at the Actor level: no ownership block, no
            # `_stats`, no flags, nothing carrying a Foundry user id.
            raise refuse(
                "unknown_actor_key",
                f"Actor at position {index} carries unsupported key(s): "
                f"{', '.join(unknown)}. The contract permits id, folderId, "
                "name, img, system and items only.",
            )

        raw_id = entry["id"]
        if raw_id is None:
            raise refuse(
                "missing_actor_id",
                f"Actor at position {index} has a null id. A per-Actor Foundry "
                'export writes "_id": null and keeps the real id only in its '
                "filename; export the bundle through the documented macro "
                "instead. An Actor is never identified by its name.",
            )
        try:
            actor_id = FoundryActorId(str(raw_id))
        except InvalidIdentityError as error:
            raise refuse("malformed_actor_id", str(error)) from None
        if str(actor_id) in seen:
            raise refuse(
                "duplicate_actor_id",
                f"Actor id {actor_id} appears at positions {seen[str(actor_id)]} "
                f"and {index}. A duplicate identity is ambiguous and is never "
                "resolved by choosing one.",
            )
        seen[str(actor_id)] = index

        try:
            folder_id = FoundryFolderId(str(entry["folderId"]))
        except InvalidIdentityError as error:
            raise refuse("malformed_folder_id", str(error)) from None
        if str(folder_id) not in selected:
            raise refuse(
                "actor_outside_selection",
                f"Actor {actor_id} sits in folder {folder_id}, which is not one "
                "of the exported folders.",
            )

        name = entry["name"]
        if not isinstance(name, str) or not name.strip():
            raise refuse(
                "malformed_actor", f"Actor {actor_id} has no usable name."
            )
        system = entry["system"]
        if not isinstance(system, Mapping):
            raise refuse(
                "malformed_actor", f"Actor {actor_id} has no `system` object."
            )
        items = entry["items"]
        if not isinstance(items, list):
            raise refuse(
                "malformed_actor", f"Actor {actor_id} has no `items` array."
            )
        if len(items) > limits.max_items_per_actor:
            raise refuse(
                "too_many_items",
                f"Actor {actor_id} carries {len(items)} embedded items, over "
                f"the {limits.max_items_per_actor} limit.",
            )
        for position, item in enumerate(items):
            if not isinstance(item, Mapping):
                raise refuse(
                    "malformed_actor",
                    f"Actor {actor_id} item {position} is not an object.",
                )
            document_type = item.get("type")
            if not isinstance(document_type, str) or not document_type.strip():
                raise refuse(
                    "malformed_actor",
                    f"Actor {actor_id} item {position} has no document type. An "
                    "untyped item cannot be classified, and an unclassified "
                    "item is never read.",
                )

        actors.append(
            SnapshotActor(
                actor_id=actor_id,
                folder_id=folder_id,
                name=name,
                document=entry,
            )
        )

    return tuple(actors)
