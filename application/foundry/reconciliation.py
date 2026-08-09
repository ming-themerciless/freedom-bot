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
6. **A difference names the record that is stale, and that record is the
   field's business.** The direction comes from the profile field's declared
   `difference_direction`, not from the fact that the platform has authority.
   `character.display_name` is authored in Foundry, so its difference makes the
   *platform's* display record stale; reporting it as "Foundry is out of date"
   would ask an operator to undo a rename a player deliberately made.

The report is ordered by Actor id so two runs over the same inputs produce
byte-identical output.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from uuid import UUID

from application.foundry.extraction import SnapshotActorView
from application.foundry.parser import ParsedSnapshot, SnapshotActor
from application.snapshots import ExternalActorMapping
from domain.field_profile import (
    DifferenceDirection,
    FieldProfile,
    SnapshotMode,
    UnknownPath,
)
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


#: Every issue code the reconciliation can produce. A closed vocabulary,
#: because `issue_codes` goes into an append-only audit payload: a caller
#: filters on it, and an unlisted value would be a free-text field arriving
#: under a vocabulary's name (I-2).
ISSUE_CODES = frozenset(
    {
        "absent_from_snapshot",
        "dangling_mapping",
        "foundry_out_of_date",
        "legacy_authority_deferred",
        "non_canonical_encoding",
        "platform_display_name_stale",
        "unable_to_compare",
        "unknown_snapshot_path",
        "unmapped_name_collision",
    }
)


@dataclass(frozen=True, slots=True)
class ReconciliationIssue:
    code: str
    message: str
    severity: IssueSeverity = IssueSeverity.ERROR
    actor_id: str | None = None
    character_id: UUID | None = None

    def __post_init__(self) -> None:
        if self.code not in ISSUE_CODES:
            raise ValueError(
                f"{self.code!r} is not a declared reconciliation issue code. "
                "Add it to ISSUE_CODES, which is what keeps the audit payload's "
                "`issue_codes` a vocabulary rather than free text."
            )

    @property
    def is_error(self) -> bool:
        return self.severity is IssueSeverity.ERROR


@dataclass(frozen=True, slots=True)
class FieldComparison:
    """One field with accepted typed authority, compared against the snapshot.

    There is no `correctable` flag any more, and its absence is the point:
    nothing in Phase 2 can write a character field, so a report has no selection
    to offer.

    `direction` is carried from the profile field rather than derived here. A
    reader asking "what does this difference mean?" gets the field's own answer,
    and there is no place left where a caller could assume one.
    """

    field_key: str
    label: str
    result: ComparisonResult
    direction: DifferenceDirection

    @property
    def differs(self) -> bool:
        """The two records disagree. *Which* is stale is `direction`'s answer."""
        return self.result.outcome is ComparisonOutcome.DIFFERENT

    @property
    def stales_platform_display_name(self) -> bool:
        return (
            self.differs
            and self.direction is DifferenceDirection.PLATFORM_DISPLAY_NAME_STALE
        )

    @property
    def warns_foundry_is_out_of_date(self) -> bool:
        """A difference that genuinely means the Foundry Actor has drifted.

        Narrower than `differs`, and deliberately so: this used to be a synonym
        for it, which is what made every difference read as "update Foundry".
        """
        return self.differs and self.direction is DifferenceDirection.FOUNDRY_OUT_OF_DATE


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
        """Every field whose two records disagree, in either direction."""
        return tuple(
            comparison for comparison in self.comparisons if comparison.differs
        )

    @property
    def stale_platform_display_name(self) -> bool:
        """The Actor was renamed in Foundry and the platform copy has not caught up."""
        return any(
            comparison.stales_platform_display_name
            for comparison in self.comparisons
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


class ReconciliationFactsError(ValueError):
    """A stored summary could not be read back as reconciliation facts.

    Raised while reconstructing the immutable result of an import that has
    already committed. It names the keys and the types that were wrong and never
    the values, because the thing being read is an append-only row whose content
    is not for an error message.

    It fails **closed** on purpose. A retry that cannot be answered with the
    original operation's own facts must not be answered with invented ones, and
    an absent or mistyped key in a durable summary is a fault an operator has to
    see rather than one the service papers over.
    """


#: Every key `ReconciliationFacts` is made of, and the type each must have.
#:
#: One table, used by both directions: `summary()` writes exactly these keys and
#: `from_summary()` requires exactly these keys. A field added to the facts
#: without a row here cannot round-trip, and a row here without a field fails the
#: construction — which is what stops the durable summary and the in-memory
#: result drifting apart.
_FACT_TYPES: Mapping[str, type | tuple[type, ...]] = MappingProxyType(
    {
        "snapshot_checksum": str,
        "folder_id": str,
        "folder_path": str,
        "profile_version": str,
        "exporter": str,
        "canonical_encoding": bool,
        "actors": int,
        "mapped": int,
        "unmapped": int,
        "blocked": int,
        "absent": int,
        "errors": int,
        "warnings": int,
        "issue_codes": tuple,
        "fields_differing": tuple,
        "stale_platform_display_names": int,
        "legacy_authority_deferred": Mapping,
    }
)


@dataclass(frozen=True, slots=True)
class ReconciliationFacts:
    """The bounded reconciliation facts of one run, as a value rather than a run.

    This is the part of a reconciliation that is **durable**. It is what
    `snapshot_imports.summary` has always stored, given a type: counts,
    identifiers and closed vocabularies, and deliberately no Actor value, no
    field value, no name and no prose.

    It exists because of finding B-1R. `ImportOutcome` used to carry a live
    `ReconciliationReport`, and a retry of an already-applied operation had
    nowhere to get one except by reconciling the artifact against the database
    *as it stands now* — which describes a different moment from the one the
    receipt's import id, correlation id and counts describe. A retry now carries
    these facts, read back from the row the original apply wrote, so every field
    of the returned result answers for the same instant.

    The full `ReconciliationReport` is not durable and deliberately never will
    be: its per-Actor entries, comparison displays and issue messages quote Actor
    data, which the audit-content ruling keeps out of append-only history. So the
    immutable result is the bounded facts, and the narrative report belongs to
    the run that computed it.
    """

    snapshot_checksum: str
    folder_id: str
    folder_path: str
    profile_version: str
    exporter: str
    canonical_encoding: bool
    actors: int
    mapped: int
    unmapped: int
    blocked: int
    absent: int
    errors: int
    warnings: int
    issue_codes: tuple[str, ...]
    fields_differing: tuple[str, ...]
    stale_platform_display_names: int
    legacy_authority_deferred: Mapping[str, str]

    @property
    def is_blocked(self) -> bool:
        return self.errors > 0

    def summary(self) -> dict[str, object]:
        """The JSON-safe rendering these facts are stored and compared as.

        Lists rather than tuples, and a plain dictionary, because this is what
        goes into a `jsonb` column and comes back out of one. `from_summary()`
        is its exact inverse, and a test holds the round trip.
        """
        return {
            "snapshot_checksum": self.snapshot_checksum,
            "folder_id": self.folder_id,
            "folder_path": self.folder_path,
            "profile_version": self.profile_version,
            "exporter": self.exporter,
            "canonical_encoding": self.canonical_encoding,
            "actors": self.actors,
            "mapped": self.mapped,
            "unmapped": self.unmapped,
            "blocked": self.blocked,
            "absent": self.absent,
            "errors": self.errors,
            "warnings": self.warnings,
            "issue_codes": list(self.issue_codes),
            "fields_differing": list(self.fields_differing),
            "stale_platform_display_names": self.stale_platform_display_names,
            "legacy_authority_deferred": dict(self.legacy_authority_deferred),
        }

    @classmethod
    def from_summary(cls, summary: object) -> ReconciliationFacts:
        """Read a stored summary back, validating every key and type.

        Not a cast. A `jsonb` column is a mapping of whatever was put in it, and
        turning one into a typed result without checking would mean a receipt
        whose "original facts" were whatever the row happened to hold. Every
        declared key must be present with the right type, and no undeclared key
        may be, so a summary written by a different version of this code is a
        visible failure rather than a partially-populated result.
        """
        if not isinstance(summary, Mapping):
            raise ReconciliationFactsError(
                "A stored reconciliation summary must be a mapping of the "
                f"declared keys; this one is a {type(summary).__name__}."
            )
        missing = sorted(set(_FACT_TYPES) - set(summary))
        unknown = sorted(set(summary) - set(_FACT_TYPES))
        if missing or unknown:
            raise ReconciliationFactsError(
                "A stored reconciliation summary does not match the declared "
                "reconciliation facts: "
                + (f"missing key(s) {missing}. " if missing else "")
                + (f"undeclared key(s) {unknown}. " if unknown else "")
                + "The original result cannot be reconstructed and nothing was "
                "invented in its place."
            )
        values = {name: _checked(name, summary[name]) for name in _FACT_TYPES}
        return cls(**values)  # type: ignore[arg-type]


def _checked(name: str, value: object) -> object:
    """One summary value, coerced to its declared type or refused.

    Sequences arrive from `jsonb` as lists and are narrowed to tuples; mappings
    are copied behind a read-only view. Nothing else is converted — a count that
    arrived as a string is a fault, not something to parse.
    """
    expected = _FACT_TYPES[name]
    if expected is tuple:
        if not isinstance(value, (list, tuple)) or not all(
            isinstance(item, str) for item in value
        ):
            raise ReconciliationFactsError(
                f"{name!r} in a stored reconciliation summary must be a "
                "sequence of strings."
            )
        return tuple(value)
    if expected is Mapping:
        if not isinstance(value, Mapping) or not all(
            isinstance(key, str) and isinstance(item, str)
            for key, item in value.items()
        ):
            raise ReconciliationFactsError(
                f"{name!r} in a stored reconciliation summary must be a mapping "
                "of strings to strings."
            )
        return MappingProxyType(dict(value))
    if expected is bool:
        if not isinstance(value, bool):
            raise ReconciliationFactsError(
                f"{name!r} in a stored reconciliation summary must be a boolean."
            )
        return value
    if expected is int:
        # `bool` is an `int` in Python and would pass silently; a count that was
        # written as `True` is a fault worth seeing.
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ReconciliationFactsError(
                f"{name!r} in a stored reconciliation summary must be a "
                "non-negative integer."
            )
        return value
    if not isinstance(value, str):
        raise ReconciliationFactsError(
            f"{name!r} in a stored reconciliation summary must be a string."
        )
    return value


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

    def facts(self) -> ReconciliationFacts:
        """The durable part of this report, as a value.

        Deliberately counts, identifiers and closed vocabularies only. No Actor
        field values, no raw snapshot content, nothing another player's private
        state could ride in on — the audit record identifies the snapshot by
        checksum and the artifact stays in the restricted store.

        Built from this report's own fields rather than from `summary()`, so a
        caller that replaces the rendering cannot change what the facts *are*.
        """
        return ReconciliationFacts(
            snapshot_checksum=self.snapshot_checksum,
            folder_id=str(self.folder.folder_id),
            folder_path=self.folder.path,
            profile_version=self.profile_version,
            exporter=self.exporter,
            canonical_encoding=self.canonical_encoding,
            actors=len(self.entries),
            mapped=self.count(ActorOutcome.MAPPED),
            unmapped=self.count(ActorOutcome.UNMAPPED),
            blocked=self.count(ActorOutcome.BLOCKED),
            absent=len(self.absent),
            errors=self.error_count,
            warnings=self.warning_count,
            issue_codes=tuple(sorted({issue.code for issue in self.issues})),
            # Field **keys** of everything that disagreed, in either direction,
            # and never the values on either side. It was called
            # `fields_out_of_date`, which asserted a direction the summary had
            # not established; `issue_codes` carries the direction, per field,
            # in the vocabulary the operator reads.
            fields_differing=tuple(
                sorted(
                    {
                        comparison.field_key
                        for entry in self.entries
                        for comparison in entry.differences
                    }
                )
            ),
            # A count, not a list of names. How many mapped characters were
            # renamed in Foundry since the platform recorded them is useful
            # operational scale; which ones is in the report, not the audit row.
            stale_platform_display_names=sum(
                entry.stale_platform_display_name for entry in self.entries
            ),
            # Field keys and their owning packages — never values, and never a
            # verdict. This is what makes the audit record able to say "these
            # fields were seen and deliberately not compared, and here is who
            # will migrate them" without quoting a single Actor's data.
            legacy_authority_deferred=MappingProxyType(
                {
                    row.field_key: row.owning_package
                    for entry in self.entries
                    for row in entry.deferred
                }
            ),
        )

    def summary(self) -> dict[str, object]:
        """A bounded, safe summary for the immutable import record.

        The JSON rendering of `facts()`, and the only thing written to
        `snapshot_imports.summary` — which is what makes that column readable
        back as the original result of the import that wrote it.
        """
        return self.facts().summary()


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
    readers: ComparableFieldReaders,
    unknown_path_limit: int = 20,
) -> ReconciliationReport:
    """Compare `folder_id` of `snapshot` against the database. Writes nothing.

    `readers` is required rather than defaulted: defaulting it here would put
    the composition decision back inside the run, which is exactly what made a
    missing reader an import-time failure instead of a startup one.
    """
    folder = snapshot.folder_identity(folder_id)
    actors = sorted(snapshot.actors_in(folder_id), key=lambda a: str(a.actor_id))

    entries: list[ActorEntry] = []
    issues: list[ReconciliationIssue] = []

    for actor in actors:
        entry = _reconcile_actor(
            actor,
            profile=profile,
            source=source,
            readers=readers,
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
                    "It is still a valid snapshot with its own identity, and "
                    "byte-for-byte duplicate detection is unaffected: an "
                    "exporter's own output is deterministic, so re-exporting an "
                    "unchanged world still yields the same bytes. What this "
                    "warns about is comparability *between* exporters. Report "
                    "it with the exporter id and version."
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
    readers: ComparableFieldReaders,
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

    comparisons = _compare_fields(view, character, profile=profile, readers=readers)
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
        if comparison.differs:
            issues.append(
                _difference_issue(comparison, actor_id=actor_id, character=character)
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


def _difference_issue(
    comparison: FieldComparison, *, actor_id: str, character: Character
) -> ReconciliationIssue:
    """One difference, reported in the direction the field actually runs.

    The code is the profile field's `difference_direction`, so a field cannot
    be reported under a direction it did not declare and a new direction cannot
    be added without giving an operator a message for it.
    """
    if comparison.direction is DifferenceDirection.PLATFORM_DISPLAY_NAME_STALE:
        return ReconciliationIssue(
            code=DifferenceDirection.PLATFORM_DISPLAY_NAME_STALE.value,
            message=(
                f"Actor {actor_id}: {comparison.label} is "
                f"{comparison.result.snapshot_display!r} in Foundry and "
                f"{comparison.result.database_display!r} in the platform's "
                "display record. Foundry is where a character is renamed, so "
                "the platform record is the stale one. Do not change the "
                "Foundry Actor. Identity is the external Actor id and is "
                "unaffected: the character stays mapped to this Actor (OD-42). "
                "Phase 2 reports the rename and updates nothing; the display "
                "record is corrected by the package that owns it."
            ),
            severity=IssueSeverity.WARNING,
            actor_id=actor_id,
            character_id=character.id,
        )
    return ReconciliationIssue(
        code=DifferenceDirection.FOUNDRY_OUT_OF_DATE.value,
        message=(
            f"Actor {actor_id}: {comparison.label} is "
            f"{comparison.result.snapshot_display!r} in Foundry and "
            f"{comparison.result.database_display!r} in the database, which is "
            "authoritative for this field. Update the Foundry Actor manually; "
            "the platform writes nothing back."
        ),
        severity=IssueSeverity.WARNING,
        actor_id=actor_id,
        character_id=character.id,
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
#:
#: It lives here and not on `FieldProfile` deliberately: a reader is a function
#: over the persistence-facing `Character`, and the domain profile must stay
#: independent of it.
DATABASE_VALUE_READERS: Mapping[str, Callable[[Character], object]] = MappingProxyType(
    {
        "character.display_name": lambda character: character.display_name,
    }
)


class ReconciliationConfigurationError(ValueError):
    """The reconciliation was composed with a profile it cannot read.

    A configuration fault, raised while the service is being built. It carries
    field keys and the profile version — no Actor data, no snapshot content and
    no database detail — because it is safe to surface at startup.
    """


class ComparableFieldReaders:
    """The readers for one profile's database-authority fields, validated once.

    This is what turns "a field with no reader" from a `LookupError` raised in
    the middle of an import into a composition that refuses to exist. The check
    is over `profile.comparable_fields()`, so a profile that gives a new field
    database authority without anyone registering a reader for it fails at
    construction — before an operator has confirmed anything and before a
    transaction is open.
    """

    __slots__ = ("_readers", "_profile_version")

    def __init__(
        self,
        readers: Mapping[str, Callable[[Character], object]],
        *,
        profile: FieldProfile,
    ) -> None:
        missing = sorted(
            profile_field.key
            for profile_field in profile.comparable_fields()
            if profile_field.key not in readers
        )
        if missing:
            raise ReconciliationConfigurationError(
                f"Field profile {profile.version} gives database authority to "
                f"{', '.join(missing)}, and the reconciliation has no way to "
                "read the accepted typed value of "
                f"{'them' if len(missing) > 1 else 'it'}. A field cannot be "
                "compared against a value nobody can fetch. Register a reader, "
                "or leave the field's authority deferred until its owning "
                "package migrates it."
            )
        self._readers = dict(readers)
        self._profile_version = profile.version

    @classmethod
    def default(cls, profile: FieldProfile) -> ComparableFieldReaders:
        return cls(DATABASE_VALUE_READERS, profile=profile)

    def read(self, key: str, character: Character) -> object:
        return self._readers[key](character)


def _compare_fields(
    view: SnapshotActorView,
    character: Character,
    *,
    profile: FieldProfile,
    readers: ComparableFieldReaders,
) -> tuple[FieldComparison, ...]:
    """Compare only the fields the platform actually has authority for.

    No missing-reader branch: `readers` was validated against this profile when
    the service was composed, so by the time a run reaches here every comparable
    field is readable.
    """
    return tuple(
        FieldComparison(
            field_key=profile_field.key,
            label=profile_field.label,
            result=compare(
                # `comparison_for` rather than the field's attribute: it raises
                # for a deferred field, so this loop cannot silently start
                # comparing one if the profile changes underneath it.
                profile.comparison_for(profile_field.key),
                view.value_for(profile_field.key),
                readers.read(profile_field.key, character),
            ),
            # Read off the field, never assumed from its authority. The profile
            # refuses to construct a database-authority field without one, so
            # this is never `None`.
            direction=profile_field.difference_direction,
        )
        for profile_field in profile.comparable_fields()
    )


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
