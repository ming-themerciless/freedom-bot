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
import re
from collections.abc import Mapping, Sequence
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


def canonical_bytes(document: Mapping[str, object]) -> bytes:
    """The contract's canonical encoding of a parsed document.

    Used only to *report* whether the artifact already matched it. The Manager
    never re-encodes an artifact and calls the result the same snapshot.
    """
    text = json.dumps(
        document,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )
    return (text + "\n").encode("utf-8")


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
        canonical_encoding=canonical_bytes(document) == artifact.raw_bytes(),
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
