"""Snapshot-only inputs for later roll consumers, with their provenance.

Plan §6.5's *snapshot-backed calculations* invariant has two halves, and both
live here:

- **every calculation records what it used** — the snapshot checksum, the
  exporter version and the field-profile version travel with the value, so a
  result can always be traced back to the artifact it was computed from; and
- **a missing, malformed or unsupported input is a typed refusal**, never a
  substituted zero, empty set or "no proficiency". `require` raises;
  `optional` answers `None` and says why. Neither ever invents a value.

There is deliberately no setter anywhere in this module. A snapshot-only field
is readable and is not writable — that is what the classification *means*, and
an editable projection would be the "independently editable duplicate character
model" the maintainer ruled out.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from application.foundry.extraction import SnapshotActorView
from application.foundry.parser import ParsedSnapshot
from application.snapshots import ExternalActorMapping
from domain.field_profile import FieldProfile, SnapshotMode
from domain.snapshot_values import Unavailable


class MissingSnapshotInput(LookupError):
    """A required snapshot input is absent, malformed or unsupported.

    Typed rather than a sentinel, because the whole point is that a caller
    cannot accidentally carry on with a default.
    """

    def __init__(self, name: str, reason: str) -> None:
        super().__init__(f"{name}: {reason}")
        self.name = name
        self.reason = reason


@dataclass(frozen=True, slots=True)
class SnapshotProvenance:
    """What a calculation was computed from."""

    checksum: str
    exporter: str
    exported_at: datetime
    profile_version: str

    def as_facts(self) -> dict[str, str]:
        """The provenance a result or an audit record carries."""
        return {
            "snapshot_checksum": self.checksum,
            "exporter": self.exporter,
            "exported_at": self.exported_at.isoformat(),
            "profile_version": self.profile_version,
        }


@dataclass(frozen=True, slots=True)
class RollInput:
    name: str
    value: object
    provenance: SnapshotProvenance


class ActorProjection:
    """Read-only access to one Actor's snapshot-only inputs."""

    __slots__ = ("_view", "_provenance", "_profile")

    def __init__(
        self,
        view: SnapshotActorView,
        provenance: SnapshotProvenance,
        profile: FieldProfile,
    ) -> None:
        self._view = view
        self._provenance = provenance
        self._profile = profile

    @property
    def provenance(self) -> SnapshotProvenance:
        return self._provenance

    def available(self) -> tuple[str, ...]:
        return tuple(sorted(self._profile.roll_inputs()))

    def require(self, name: str) -> RollInput:
        """The input, or a typed refusal. Never a default."""
        self._require_snapshot_only(name)
        value = self._view.roll_input(name)
        if isinstance(value, Unavailable):
            raise MissingSnapshotInput(name, value.reason)
        return RollInput(name=name, value=value, provenance=self._provenance)

    def optional(self, name: str) -> RollInput | None:
        """The input, or `None` — for a caller that has a documented fallback.

        Still not a substituted value: the caller receives nothing and decides,
        visibly, what to do about it.
        """
        self._require_snapshot_only(name)
        value = self._view.roll_input(name)
        if isinstance(value, Unavailable):
            return None
        return RollInput(name=name, value=value, provenance=self._provenance)

    def skill_proficiency(self, skill: str) -> RollInput:
        """0 none, 1 proficient, 2 expertise — or a refusal for an unknown skill."""
        levels = self.require("skill_proficiencies").value
        assert isinstance(levels, dict)  # guaranteed by the extractor
        if skill not in levels:
            raise MissingSnapshotInput(
                "skill_proficiencies",
                f"the snapshot records no skill {skill!r} for this Actor, and a "
                "missing skill is not the same as no proficiency",
            )
        return RollInput(
            name=f"skill_proficiencies.{skill}",
            value=levels[skill],
            provenance=self._provenance,
        )

    def _require_snapshot_only(self, name: str) -> None:
        rule = self._profile.roll_inputs().get(name)
        if rule is None:
            raise MissingSnapshotInput(
                name,
                f"profile {self._profile.version} exposes no roll input of that "
                "name",
            )
        if rule.mode is not SnapshotMode.SNAPSHOT_ONLY:  # pragma: no cover
            # The profile's own invariants already forbid this; the check is
            # here so a future profile change cannot quietly make a compared or
            # correctable field readable as an unaudited roll input.
            raise MissingSnapshotInput(name, "that field is not snapshot-only")


class SnapshotProjection:
    """Snapshot-only inputs for the characters a snapshot maps to.

    Built from one parsed snapshot and the mappings that were established from
    it. A character with no mapping has no projection — never an empty one,
    because an empty projection reads exactly like an Actor with nothing
    recorded.
    """

    __slots__ = ("_snapshot", "_profile", "_by_character", "_provenance")

    def __init__(
        self,
        snapshot: ParsedSnapshot,
        *,
        profile: FieldProfile,
        mappings: tuple[ExternalActorMapping, ...],
    ) -> None:
        self._snapshot = snapshot
        self._profile = profile
        self._provenance = SnapshotProvenance(
            checksum=snapshot.checksum.hex_digest,
            exporter=snapshot.exporter.describe(),
            exported_at=snapshot.exported_at,
            profile_version=profile.version,
        )
        actors = {str(actor.actor_id): actor for actor in snapshot.actors}
        self._by_character = {
            mapping.character_id: actors[mapping.external_actor_id]
            for mapping in mappings
            if mapping.external_actor_id in actors
        }

    @property
    def provenance(self) -> SnapshotProvenance:
        return self._provenance

    def for_character(self, character_id: UUID) -> ActorProjection:
        actor = self._by_character.get(character_id)
        if actor is None:
            raise MissingSnapshotInput(
                "actor",
                f"character {character_id} has no Actor in snapshot "
                f"{self._provenance.checksum[:12]}. A calculation that needs "
                "snapshot inputs cannot proceed without one",
            )
        return ActorProjection(
            SnapshotActorView(actor, self._profile), self._provenance, self._profile
        )

    def characters(self) -> tuple[UUID, ...]:
        return tuple(sorted(self._by_character, key=str))
