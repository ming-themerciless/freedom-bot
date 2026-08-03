"""Compare one snapshot folder against PostgreSQL, deterministically.

Reconciliation reads. It changes nothing, and it is the same computation whether
it runs for a preview or immediately before an apply — which is what lets the
apply re-check its inputs rather than trusting a report it was handed.

Five rules shape the output, and each exists because its opposite is a way to
lose a character:

1. **A mapping is never inferred from a name.** An Actor with no external
   mapping is a *create candidate*, not a name-matched update. If one or more
   existing characters already claim that display name, the entry is **blocked**
   and a human resolves it — creating a second character would silently
   duplicate a player, and re-keying an existing mapping would be a guess.
2. **An ambiguous candidate lookup fails closed.** Under OD-42 a display name is
   not an identity and several characters may share one, so "which of these did
   the exporter mean?" is a question the importer must refuse rather than answer.
   Every candidate is named in the issue; none is chosen.
3. **An absent Actor deletes nothing.** A character mapped in this world whose
   Actor is not in the snapshot produces a warning and stays exactly as it is:
   mapped, active, untouched.
4. **A field with no accepted typed authority is reported, never compared.**
   It produces a `legacy_authority_deferred` row naming the package that owns
   its migration. No verdict is offered, because none has been earned: the
   platform holds no value to disagree with.
5. **Unknown snapshot paths are reported per Actor** and are never writable.

The report is ordered by Actor id so two runs over the same inputs produce
byte-identical output.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from application.foundry.extraction import SnapshotActorView
from application.foundry.parser import ParsedSnapshot, SnapshotActor
from application.snapshots import ExternalActorMapping
from domain.field_profile import FieldProfile, SnapshotMode, UnknownPath
from domain.foundry import FolderIdentity
from domain.identity import Character
from domain.names import DisplayName
from domain.snapshot_values import (
    ComparisonOutcome,
    ComparisonResult,
    Unavailable,
    compare,
)


class IssueSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"


class ActorOutcome(Enum):
    #: The Actor maps to a character; its fields were compared.
    MAPPED = "mapped"
    #: No mapping exists; applying would create a character and a mapping.
    UNMAPPED = "unmapped"
    #: Something needs a human decision. Applying commits nothing.
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class ReconciliationIssue:
    code: str
    message: str
    severity: IssueSeverity = IssueSeverity.ERROR
    actor_id: str | None = None
    character_id: UUID | None = None

    @property
    def is_error(self) -> bool:
        return self.severity is IssueSeverity.ERROR


@dataclass(frozen=True, slots=True)
class FieldComparison:
    """One field with accepted typed authority, compared against the snapshot.

    There is no `correctable` flag any more, and its absence is the point:
    nothing in Phase 2 can write a character field, so a report has no selection
    to offer.
    """

    field_key: str
    label: str
    result: ComparisonResult

    @property
    def warns_foundry_is_out_of_date(self) -> bool:
        return self.result.outcome is ComparisonOutcome.DIFFERENT


@dataclass(frozen=True, slots=True)
class DeferredField:
    """One field whose authority is still the legacy path.

    Deliberately **not** a `FieldComparison`. A separate type is what stops a
    caller iterating comparisons and silently treating "no verdict" as "no
    difference": there is no `result` here to misread.

    `snapshot_has_value` records only whether Foundry holds anything for the
    field — not what it holds. The value is of no use in Phase 2 because nothing
    can act on it, and keeping it out of the report keeps Actor field data out of
    the import summary and the audit record that quotes it.
    """

    field_key: str
    label: str
    owning_package: str
    snapshot_has_value: bool
    #: Why the snapshot could not supply a value, when it could not. Never the
    #: value itself.
    unavailable_reason: str | None = None


@dataclass(frozen=True, slots=True)
class ActorEntry:
    actor_id: str
    actor_name: str
    folder_id: str
    outcome: ActorOutcome
    character_id: UUID | None = None
    comparisons: tuple[FieldComparison, ...] = ()
    deferred: tuple[DeferredField, ...] = ()
    unknown_paths: tuple[UnknownPath, ...] = ()

    @property
    def differences(self) -> tuple[FieldComparison, ...]:
        return tuple(
            comparison
            for comparison in self.comparisons
            if comparison.warns_foundry_is_out_of_date
        )

    @property
    def uncomparable(self) -> tuple[FieldComparison, ...]:
        return tuple(
            comparison
            for comparison in self.comparisons
            if comparison.result.outcome is ComparisonOutcome.UNABLE_TO_COMPARE
        )


@dataclass(frozen=True, slots=True)
class AbsentCharacter:
    """A mapped character whose Actor is not in this snapshot's folder."""

    character_id: UUID
    display_name: str
    external_actor_id: str


@dataclass(frozen=True, slots=True)
class ReconciliationReport:
    snapshot_checksum: str
    folder: FolderIdentity
    profile_version: str
    exporter: str
    entries: tuple[ActorEntry, ...]
    absent: tuple[AbsentCharacter, ...]
    issues: tuple[ReconciliationIssue, ...]
    canonical_encoding: bool

    @property
    def blocked(self) -> bool:
        """Any error at all refuses the whole apply. The run is the unit."""
        return any(issue.is_error for issue in self.issues)

    @property
    def error_count(self) -> int:
        return sum(issue.is_error for issue in self.issues)

    @property
    def warning_count(self) -> int:
        return sum(not issue.is_error for issue in self.issues)

    def count(self, outcome: ActorOutcome) -> int:
        return sum(entry.outcome is outcome for entry in self.entries)

    def entry_for(self, actor_id: str) -> ActorEntry | None:
        for entry in self.entries:
            if entry.actor_id == actor_id:
                return entry
        return None

    def summary(self) -> dict[str, object]:
        """A bounded, safe summary for the immutable import record.

        Deliberately counts and identifiers only. No Actor field values, no raw
        snapshot content, nothing another player's private state could ride in
        on — the audit record identifies the snapshot by checksum and the
        artifact stays in the restricted store.
        """
        return {
            "snapshot_checksum": self.snapshot_checksum,
            "folder_id": str(self.folder.folder_id),
            "folder_path": self.folder.path,
            "profile_version": self.profile_version,
            "exporter": self.exporter,
            "canonical_encoding": self.canonical_encoding,
            "actors": len(self.entries),
            "mapped": self.count(ActorOutcome.MAPPED),
            "unmapped": self.count(ActorOutcome.UNMAPPED),
            "blocked": self.count(ActorOutcome.BLOCKED),
            "absent": len(self.absent),
            "errors": self.error_count,
            "warnings": self.warning_count,
            "issue_codes": sorted({issue.code for issue in self.issues}),
            "fields_out_of_date": sorted(
                {
                    comparison.field_key
                    for entry in self.entries
                    for comparison in entry.differences
                }
            ),
            # Field keys and their owning packages — never values, and never a
            # verdict. This is what makes the audit record able to say "these
            # fields were seen and deliberately not compared, and here is who
            # will migrate them" without quoting a single Actor's data.
            "legacy_authority_deferred": {
                row.field_key: row.owning_package
                for entry in self.entries
                for row in entry.deferred
            },
        }


class ReconciliationSource:
    """What reconciliation needs to read, gathered once per run.

    Passed in rather than fetched, so the same computation can run against a
    fake and against PostgreSQL and be the same computation.
    """

    __slots__ = ("_mappings", "_characters", "_claims")

    def __init__(
        self,
        *,
        mappings: Sequence[ExternalActorMapping],
        characters: Mapping[UUID, Character],
        name_claims: Mapping[str, Sequence[UUID]],
    ) -> None:
        self._mappings = {mapping.external_actor_id: mapping for mapping in mappings}
        self._characters = dict(characters)
        #: Identity key (`domain/names.py`) → **every** character holding it.
        #:
        #: A sequence, not a single id. `characters.display_name` carries no
        #: database uniqueness rule and, under OD-42, deliberately never will:
        #: two characters may legitimately share a name. A single-valued lookup
        #: would silently drop all but one of them and let an ambiguous case
        #: present as an unambiguous one.
        self._claims = {
            key: tuple(values) for key, values in name_claims.items()
        }

    def mapping_for(self, actor_id: str) -> ExternalActorMapping | None:
        return self._mappings.get(actor_id)

    def mappings(self) -> tuple[ExternalActorMapping, ...]:
        return tuple(
            sorted(self._mappings.values(), key=lambda entry: entry.external_actor_id)
        )

    def character(self, character_id: UUID) -> Character | None:
        return self._characters.get(character_id)

    def characters_claiming(self, display_name: str) -> tuple[UUID, ...]:
        """Every character already holding this display name, in a stable order.

        Empty means the name is free. One means a single candidate — which is
        still not a match, because a name is not an identity. More than one is
        the ambiguous case the run fails closed on.
        """
        return tuple(
            sorted(self._claims.get(DisplayName(display_name).identity_key, ()), key=str)
        )


def reconcile(
    snapshot: ParsedSnapshot,
    *,
    folder_id: str,
    profile: FieldProfile,
    source: ReconciliationSource,
    unknown_path_limit: int = 20,
) -> ReconciliationReport:
    """Compare `folder_id` of `snapshot` against the database. Writes nothing."""
    folder = snapshot.folder_identity(folder_id)
    actors = sorted(snapshot.actors_in(folder_id), key=lambda a: str(a.actor_id))

    entries: list[ActorEntry] = []
    issues: list[ReconciliationIssue] = []

    for actor in actors:
        entry = _reconcile_actor(
            actor,
            profile=profile,
            source=source,
            issues=issues,
            unknown_path_limit=unknown_path_limit,
        )
        entries.append(entry)

    present = {str(actor.actor_id) for actor in actors}
    absent: list[AbsentCharacter] = []
    for mapping in source.mappings():
        if mapping.external_actor_id in present:
            continue
        character = source.character(mapping.character_id)
        display_name = character.display_name if character else "(unknown)"
        absent.append(
            AbsentCharacter(
                character_id=mapping.character_id,
                display_name=display_name,
                external_actor_id=mapping.external_actor_id,
            )
        )
        # A warning, never an instruction. The Actor may have been moved to
        # another folder, or the export may simply be older than the character.
        issues.append(
            ReconciliationIssue(
                code="absent_from_snapshot",
                message=(
                    f"Character {mapping.character_id} is mapped to Foundry Actor "
                    f"{mapping.external_actor_id}, which this snapshot's folder "
                    "does not contain. Nothing is deleted, deactivated or "
                    "unmapped; a separate Council correction is required to "
                    "change that state."
                ),
                severity=IssueSeverity.WARNING,
                actor_id=mapping.external_actor_id,
                character_id=mapping.character_id,
            )
        )

    if not snapshot.canonical_encoding:
        issues.append(
            ReconciliationIssue(
                code="non_canonical_encoding",
                message=(
                    "The artifact is not in the contract's canonical encoding. "
                    "It is still a valid snapshot with its own identity, but two "
                    "exports of an unchanged world will not compare equal until "
                    "the exporter canonicalises its output."
                ),
                severity=IssueSeverity.WARNING,
            )
        )

    return ReconciliationReport(
        snapshot_checksum=snapshot.checksum.hex_digest,
        folder=folder,
        profile_version=profile.version,
        exporter=snapshot.exporter.describe(),
        entries=tuple(entries),
        absent=tuple(sorted(absent, key=lambda entry: entry.external_actor_id)),
        issues=tuple(issues),
        canonical_encoding=snapshot.canonical_encoding,
    )


def _reconcile_actor(
    actor: SnapshotActor,
    *,
    profile: FieldProfile,
    source: ReconciliationSource,
    issues: list[ReconciliationIssue],
    unknown_path_limit: int,
) -> ActorEntry:
    actor_id = str(actor.actor_id)
    view = SnapshotActorView(actor, profile)
    unknown = view.unknown_paths(limit=unknown_path_limit)
    if unknown:
        # Reported, and never writable: `classify` answered `None` for each of
        # these, so no correction can name one.
        issues.append(
            ReconciliationIssue(
                code="unknown_snapshot_path",
                message=(
                    f"Actor {actor_id} carries {len(unknown)} path(s) the field "
                    f"profile {profile.version} does not classify: "
                    f"{', '.join(path.path for path in unknown)}. They are "
                    "reported and are never written. Classify them in the "
                    "profile before relying on them."
                ),
                severity=IssueSeverity.WARNING,
                actor_id=actor_id,
            )
        )

    mapping = source.mapping_for(actor_id)
    if mapping is None:
        return _reconcile_unmapped(actor, view, source=source, issues=issues, unknown=unknown)

    character = source.character(mapping.character_id)
    if character is None:
        issues.append(
            ReconciliationIssue(
                code="dangling_mapping",
                message=(
                    f"Foundry Actor {actor_id} is mapped to character "
                    f"{mapping.character_id}, which no longer exists. Resolve the "
                    "mapping before importing."
                ),
                actor_id=actor_id,
                character_id=mapping.character_id,
            )
        )
        return ActorEntry(
            actor_id=actor_id,
            actor_name=actor.name,
            folder_id=str(actor.folder_id),
            outcome=ActorOutcome.BLOCKED,
            character_id=mapping.character_id,
            unknown_paths=unknown,
        )

    comparisons = _compare_fields(view, character, profile=profile)
    deferred = _deferred_fields(view, profile=profile)
    for entry in deferred:
        issues.append(
            ReconciliationIssue(
                code="legacy_authority_deferred",
                message=(
                    f"Actor {actor_id}: {entry.label} is not compared. No accepted "
                    f"typed PostgreSQL authority exists for it yet, so the accepted "
                    f"legacy path remains authoritative and package "
                    f"{entry.owning_package} owns its migration. Foundry "
                    + (
                        "holds a value for it."
                        if entry.snapshot_has_value
                        else f"supplies no value for it ({entry.unavailable_reason})."
                    )
                ),
                severity=IssueSeverity.WARNING,
                actor_id=actor_id,
                character_id=character.id,
            )
        )
    for comparison in comparisons:
        if comparison.warns_foundry_is_out_of_date:
            issues.append(
                ReconciliationIssue(
                    code="foundry_out_of_date",
                    message=(
                        f"Actor {actor_id}: {comparison.label} is "
                        f"{comparison.result.snapshot_display!r} in Foundry and "
                        f"{comparison.result.database_display!r} in the database, "
                        "which is authoritative. Update the Foundry Actor "
                        "manually; the platform writes nothing back."
                    ),
                    severity=IssueSeverity.WARNING,
                    actor_id=actor_id,
                    character_id=character.id,
                )
            )
        elif comparison.result.outcome is ComparisonOutcome.UNABLE_TO_COMPARE:
            issues.append(
                ReconciliationIssue(
                    code="unable_to_compare",
                    message=(
                        f"Actor {actor_id}: {comparison.label} could not be "
                        f"compared — {comparison.result.reason}. This is neither "
                        "agreement nor disagreement."
                    ),
                    severity=IssueSeverity.WARNING,
                    actor_id=actor_id,
                    character_id=character.id,
                )
            )

    return ActorEntry(
        actor_id=actor_id,
        actor_name=actor.name,
        folder_id=str(actor.folder_id),
        outcome=ActorOutcome.MAPPED,
        character_id=character.id,
        comparisons=comparisons,
        deferred=deferred,
        unknown_paths=unknown,
    )


def _reconcile_unmapped(
    actor: SnapshotActor,
    view: SnapshotActorView,
    *,
    source: ReconciliationSource,
    issues: list[ReconciliationIssue],
    unknown: tuple[UnknownPath, ...],
) -> ActorEntry:
    actor_id = str(actor.actor_id)
    claimants = source.characters_claiming(actor.name)
    if claimants:
        # The single most dangerous case in the whole import. Two readings —
        # "this is that character, awaiting its mapping" and "these are
        # different characters that share a name" — produce identical evidence,
        # and a Foundry Actor id is no help because the character does not have
        # one yet. Mapping is a deliberate, audited Council act (ADR 0006), and
        # under OD-42 a shared display name is legitimate rather than a defect;
        # this is where the import stops and says so.
        #
        # Every claimant is named. Reporting one of several would make an
        # ambiguous situation look settled, which is the failure this refusal
        # exists to prevent.
        named = ", ".join(str(candidate) for candidate in claimants)
        issues.append(
            ReconciliationIssue(
                code="unmapped_name_collision",
                message=(
                    f"Foundry Actor {actor_id} is named {actor.name!r}, which "
                    f"{len(claimants)} existing character(s) already claim "
                    f"({named}), and the Actor has no mapping. A display name is "
                    "not an identity, so the platform cannot tell whether this is "
                    "one of them awaiting its mapping or a different character "
                    "that shares the name. Importing would either duplicate a "
                    "character or adopt one by name. Establish the mapping "
                    "deliberately, then import again."
                ),
                actor_id=actor_id,
                # Named individually above. A single id here would imply the
                # importer had picked one.
                character_id=claimants[0] if len(claimants) == 1 else None,
            )
        )
        return ActorEntry(
            actor_id=actor_id,
            actor_name=actor.name,
            folder_id=str(actor.folder_id),
            outcome=ActorOutcome.BLOCKED,
            unknown_paths=unknown,
        )

    return ActorEntry(
        actor_id=actor_id,
        actor_name=actor.name,
        folder_id=str(actor.folder_id),
        outcome=ActorOutcome.UNMAPPED,
        unknown_paths=unknown,
    )


#: Where a comparable field's accepted typed value is read from.
#:
#: Exactly one field has database authority today — `character.display_name`,
#: which the import writes itself at character creation — so this is a table of
#: one rather than a lookup over a state model. It is a table rather than a
#: special case so that the second entry, whenever a package migrates one, is an
#: added row instead of a rewritten function.
_DATABASE_VALUES = {
    "character.display_name": lambda character: character.display_name,
}


def _compare_fields(
    view: SnapshotActorView, character: Character, *, profile: FieldProfile
) -> tuple[FieldComparison, ...]:
    """Compare only the fields the platform actually has authority for."""
    comparisons: list[FieldComparison] = []
    for profile_field in profile.comparable_fields():
        read = _DATABASE_VALUES.get(profile_field.key)
        if read is None:
            raise LookupError(
                f"{profile_field.key} claims database authority but this module "
                "has no way to read its accepted typed value. A field cannot be "
                "compared against a value nobody can fetch."
            )
        comparisons.append(
            FieldComparison(
                field_key=profile_field.key,
                label=profile_field.label,
                result=compare(
                    # `comparison_for` rather than the field's attribute: it
                    # raises for a deferred field, so this loop cannot silently
                    # start comparing one if the profile changes underneath it.
                    profile.comparison_for(profile_field.key),
                    view.value_for(profile_field.key),
                    read(character),
                ),
            )
        )
    return tuple(comparisons)


def _deferred_fields(
    view: SnapshotActorView, *, profile: FieldProfile
) -> tuple[DeferredField, ...]:
    """Report every field whose authority is still the legacy path.

    Presence only. The snapshot value is deliberately not carried into the
    report: nothing in Phase 2 can act on it, and leaving it out keeps Actor
    field data out of the import summary and the audit record built from it.
    """
    rows: list[DeferredField] = []
    for profile_field in profile.deferred_fields():
        value = view.value_for(profile_field.key)
        unavailable = isinstance(value, Unavailable)
        rows.append(
            DeferredField(
                field_key=profile_field.key,
                label=profile_field.label,
                owning_package=profile_field.owning_package or "",
                snapshot_has_value=not unavailable,
                unavailable_reason=value.reason if unavailable else None,
            )
        )
    return tuple(rows)


def relink_fingerprint(view: SnapshotActorView, actor: SnapshotActor) -> str:
    """A human-verifiable fingerprint, for re-linking after a world rebuild.

    A Foundry `_id` does not survive a world rebuild (ADR 0006), so the mapping
    stores name plus class and level at mapping time. It is evidence for a human
    re-establishing a link — never an identity, and never matched automatically.
    """
    from domain.snapshot_values import Unavailable

    class_identifier = view.value_for("character.class")
    level = view.value_for("character.level")
    parts = [actor.name]
    parts.append(
        "class unknown" if isinstance(class_identifier, Unavailable) else str(class_identifier)
    )
    parts.append("level unknown" if isinstance(level, Unavailable) else f"level {level}")
    return " / ".join(parts)[:255]


def snapshot_only_paths(profile: FieldProfile) -> tuple[str, ...]:
    """Every path a calculation may read but nothing may write."""
    return tuple(
        sorted(
            rule.path
            for rule in profile.snapshot_fields
            if rule.mode is SnapshotMode.SNAPSHOT_ONLY
        )
    )
