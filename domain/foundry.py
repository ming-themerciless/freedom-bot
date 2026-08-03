"""Identity value objects for the offline Foundry snapshot (plan §6.4).

Nothing here reads a file, a database or a network. These are the things a
snapshot *is*: a checksum, a world, a folder, an Actor id — each one validated
at construction so an invalid identity cannot be carried around and discovered
later.

The rule this module exists to hold is that **an identity is never a name**.
A Foundry Actor id identifies an Actor; its `name` is a display value a player
edits. A folder id identifies a folder; two folders may legitimately carry one
name under different parents. Every comparison here is on the id.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

#: The fixed `schema` string of the Council-side export bundle. See
#: `docs/rules/foundry-export-contract.md`.
EXPORT_SCHEMA = "freedom-blades.foundry-export"

#: The bundle schema versions this Manager was built for. Anything else fails
#: closed, naming both the observed and the expected value — a newer exporter is
#: a deliberate checkpoint, not a degraded import (ADR 0006).
SUPPORTED_SCHEMA_VERSIONS = frozenset({1})

#: Foundry document ids are 16 characters of `[A-Za-z0-9]`. The same shape is
#: enforced by the `external_actor_mappings` check constraint, so a value that
#: passes here cannot be refused by the database later.
_DOCUMENT_ID = re.compile(r"^[A-Za-z0-9]{16}$")

_SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")


class InvalidIdentityError(ValueError):
    """A snapshot identity could not be constructed from the supplied value."""


@dataclass(frozen=True, slots=True)
class SnapshotChecksum:
    """The SHA-256 of an artifact's original bytes — the snapshot's identity.

    Computed *before* parsing, so it identifies exactly what arrived rather than
    what a parser made of it. Changing one byte produces a different checksum
    and therefore a different snapshot (plan §6.4).
    """

    hex_digest: str

    def __post_init__(self) -> None:
        if not _SHA256_HEX.fullmatch(self.hex_digest):
            raise InvalidIdentityError(
                "A snapshot checksum is 64 lowercase hexadecimal characters."
            )

    @classmethod
    def of(cls, data: bytes) -> SnapshotChecksum:
        return cls(hashlib.sha256(data).hexdigest())

    @property
    def short(self) -> str:
        """The first 12 characters, for a message a human reads.

        Never used for comparison or storage: two artifacts sharing a prefix are
        two artifacts.
        """
        return self.hex_digest[:12]

    def __str__(self) -> str:
        return self.hex_digest


@dataclass(frozen=True, slots=True)
class FoundryDocumentId:
    """A Foundry document id: the mapping key, never the identity (ADR 0006)."""

    value: str

    def __post_init__(self) -> None:
        if not _DOCUMENT_ID.fullmatch(self.value):
            raise InvalidIdentityError(
                "A Foundry document id is exactly 16 alphanumeric characters; "
                f"{self.value!r} is not. A per-Actor Foundry export writes "
                '"_id": null and keeps the real id only in its filename, so a '
                "file shaped that way is refused rather than name-matched."
            )

    def __str__(self) -> str:
        return self.value


class FoundryActorId(FoundryDocumentId):
    """A Foundry Actor `_id`."""

    __slots__ = ()


class FoundryFolderId(FoundryDocumentId):
    """A Foundry Folder `_id`."""

    __slots__ = ()


@dataclass(frozen=True, slots=True)
class FolderIdentity:
    """A folder is its stable id *together with* its displayed path.

    The maintainer requirement is explicit: folder identity never uses the name
    alone. The id is what is compared and stored; the path is what a Council
    member confirms in a preview, and what makes `Characters (active)` under two
    different parents distinguishable.
    """

    folder_id: FoundryFolderId
    path: str

    def __post_init__(self) -> None:
        if not self.path.startswith("/"):
            raise InvalidIdentityError("A folder path is absolute and starts with '/'.")

    def describe(self) -> str:
        return f"{self.path} ({self.folder_id})"


@dataclass(frozen=True, slots=True)
class WorldIdentity:
    """What a bundle claims about the world and the software that wrote it."""

    world_id: str
    title: str
    core_version: str
    system_id: str
    system_version: str

    def __post_init__(self) -> None:
        for field_name in ("world_id", "core_version", "system_id", "system_version"):
            if not getattr(self, field_name).strip():
                raise InvalidIdentityError(f"A snapshot world requires {field_name}.")

    @property
    def version_tuple(self) -> tuple[str, str, str]:
        """Compatibility is keyed on the tuple, never on one member (ADR 0006)."""
        return (self.core_version, self.system_id, self.system_version)

    def describe(self) -> str:
        return (
            f"world {self.world_id!r}, Foundry core {self.core_version}, "
            f"system {self.system_id} {self.system_version}"
        )


@dataclass(frozen=True, slots=True)
class SupportedDeployment:
    """The one deployment this Manager accepts, held in configuration.

    OD-14: the connector serves one deployment and is not distributed, so it
    pins the deployed tuple and fails closed on anything else. A Foundry or
    system upgrade deliberately stops imports until the pin is updated; that
    visible checkpoint is the feature.
    """

    world_id: str
    core_version: str
    system_id: str
    system_version: str

    def mismatches(self, world: WorldIdentity) -> tuple[str, ...]:
        """Every way `world` differs from this deployment, named individually.

        A tuple rather than a bool: an operator handed "unsupported version"
        cannot tell which half moved, and both halves upgrade independently
        (foundry-mapping.md §3).
        """
        differences: list[str] = []
        if world.world_id != self.world_id:
            differences.append(
                f"world id {world.world_id!r} (expected {self.world_id!r})"
            )
        if world.core_version != self.core_version:
            differences.append(
                f"Foundry core {world.core_version!r} (expected {self.core_version!r})"
            )
        if world.system_id != self.system_id:
            differences.append(
                f"game system {world.system_id!r} (expected {self.system_id!r})"
            )
        if world.system_version != self.system_version:
            differences.append(
                f"system version {world.system_version!r} "
                f"(expected {self.system_version!r})"
            )
        return tuple(differences)


#: The deployment observed in Phase 0 and confirmed by the maintainer. It is a
#: default for configuration, not a hard-coded constant: callers accept a
#: `SupportedDeployment` and this is what the operations documentation tells an
#: operator to configure.
OBSERVED_DEPLOYMENT = SupportedDeployment(
    world_id="the-guild",
    core_version="14.365",
    system_id="dnd5e",
    system_version="5.3.3",
)
