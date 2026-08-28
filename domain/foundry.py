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

    OD-14, controlled baseline v1.6: the connector serves one deployment and is
    not distributed, so it fails closed on anything it was not authorized for.
    What "anything" means was narrowed on 2026-08-27 and is **not** exact
    equality of the whole tuple:

    - `world_id` and `system_id` match **exactly** — they are identities;
    - Foundry core is accepted across its **generation**, numeric `14.x`;
    - dnd5e is accepted across **major.minor**, numeric `5.3.x`;
    - a malformed version, or one outside those ranges, **fails closed**.

    So a build or patch inside the accepted ranges no longer stops imports; a
    generation change, a system minor or major change, an identity change or an
    unparsable version still does, and that visible checkpoint is the feature.

    **Structural acceptance here is not a semantic compatibility claim.** OD-14
    keeps an operational obligation that this class cannot discharge: every
    deployed upgrade, in range or not, still owes a real export and preview with
    warnings and diagnostics inspected and recorded.
    """

    world_id: str
    core_version: str
    system_id: str
    system_version: str

    #: How many leading dot-separated components of each version must match.
    #:
    #: **Changed 2026-08-27 from exact equality (change-log C-P3.5-Z).** Exact
    #: matching stopped submission on every Foundry build — which is what
    #: happened on the 14.365 → 14.367 upgrade, and the refusal worked. It also
    #: means a bug-fix release costs a controlled change, a module re-release and
    #: a maintainer's evening.
    #:
    #: The ranges are scoped to where each product's breaking changes actually
    #: land, rather than opened uniformly:
    #:
    #: - **Foundry core: the generation** (`14.x`). Builds within a generation are
    #:   fixes to the application. `module.json` already declares
    #:   `"minimum": "14", "maximum": "14"`, so this aligns the module's own check
    #:   with a compatibility statement it was already making.
    #: - **Game system: major and minor** (`5.3.x`). The system defines the Actor
    #:   schema, so this is the half where a real change would hurt: `5.3.4` is
    #:   accepted, `5.4.0` still stops for a decision.
    #: - **`world_id` and `system_id` remain exact.** They are identities, not
    #:   versions.
    _CORE_COMPONENTS = 1
    _SYSTEM_COMPONENTS = 2

    @staticmethod
    def _series(value: str, components: int) -> tuple[str, ...] | None:
        """The leading `components` of a dotted version, or `None` if malformed.

        `None` is never equal to anything, including another `None`, because
        callers compare the returned tuples — so an unparsable version on either
        side is a mismatch. **Fail closed:** a version this cannot read is one
        whose compatibility it cannot judge.
        """
        parts = value.split(".")
        if len(parts) < components:
            return None
        # **Every** component is validated, not only the compared prefix. An
        # earlier draft checked the head alone, which accepted `14.x` and
        # `5.3.3-beta` because their tails were never read — and a prerelease
        # game system is exactly the case that should stop and ask, since a beta
        # is where an Actor schema is most likely to move.
        if not all(part.isdigit() for part in parts):
            return None
        return tuple(parts[:components])

    def _compatible(self, observed: str, supported: str, components: int) -> bool:
        left = self._series(observed, components)
        right = self._series(supported, components)
        return left is not None and right is not None and left == right

    def mismatches(self, world: WorldIdentity) -> tuple[str, ...]:
        """Every way `world` is incompatible with this deployment, named individually.

        A tuple rather than a bool: an operator handed "unsupported version"
        cannot tell which half moved, and both halves upgrade independently
        (foundry-mapping.md §3).

        **Compatibility, not equality, since 2026-08-27.** See
        `_CORE_COMPONENTS` for which part of each version is compared and why.
        Each message names the accepted *series* rather than the exact reference
        version, so an operator reading a refusal learns what would be accepted
        rather than only what was expected.
        """
        differences: list[str] = []
        if world.world_id != self.world_id:
            differences.append(
                f"world id {world.world_id!r} (expected {self.world_id!r})"
            )
        if not self._compatible(
            world.core_version, self.core_version, self._CORE_COMPONENTS
        ):
            series = self._series(self.core_version, self._CORE_COMPONENTS)
            expected = f"{'.'.join(series)}.x" if series else self.core_version
            differences.append(
                f"Foundry core {world.core_version!r} "
                f"(expected the {expected} series)"
            )
        if world.system_id != self.system_id:
            differences.append(
                f"game system {world.system_id!r} (expected {self.system_id!r})"
            )
        if not self._compatible(
            world.system_version, self.system_version, self._SYSTEM_COMPONENTS
        ):
            series = self._series(self.system_version, self._SYSTEM_COMPONENTS)
            expected = f"{'.'.join(series)}.x" if series else self.system_version
            differences.append(
                f"system version {world.system_version!r} "
                f"(expected the {expected} series)"
            )
        return tuple(differences)


#: The deployment observed in Phase 0 and confirmed by the maintainer. It is a
#: default for configuration, not a hard-coded constant: callers accept a
#: `SupportedDeployment` and this is what the operations documentation tells an
#: operator to configure.
#:
#: **Core version moved 14.365 -> 14.367 on 2026-08-27** after the Operations
#: Owner upgraded Foundry and the module refused to export (finding N-25). The
#: refusal was the control working: `mismatches()` compared exact strings at the
#: time, so a patch release stopped submission until somebody decided. That
#: decision is change-log C-P3.5-X, and this constant is its result.
#:
#: **`mismatches()` no longer compares exact strings** — C-P3.5-Z, later the same
#: day, replaced exact equality with the OD-14 v1.6 ranges (`SupportedDeployment`
#: states them). A build inside Foundry `14.x` and dnd5e `5.3.x` would no longer
#: stop submission the way `14.367` did; a generation or system-minor change, an
#: identity change or a malformed version still does. This constant therefore
#: names the observed **reference**, not the boundary of what is accepted.
#:
#: **What was NOT re-verified, and it matters:** the module's API usage was read
#: against the installed **14.365.0** source (`foundry-module/scripts/*.js`
#: header comments, which are provenance and are deliberately unchanged). Nobody
#: has re-read 14.367's source. The acceptance rests on the server-side parser
#: still validating schema version, canonical encoding, exporter identity, folder
#: graph, Actor identity and every N-20 limit — so a genuine schema change would
#: surface as a parse refusal, not as silent corruption.
#:
#: `system_version` is unchanged because the module's refusal named the core
#: version alone; `mismatches()` reports every incompatible field, so a system
#: upgrade would have appeared in the same message and did not.
OBSERVED_DEPLOYMENT = SupportedDeployment(
    world_id="the-guild",
    core_version="14.367",
    system_id="dnd5e",
    system_version="5.3.3",
)
