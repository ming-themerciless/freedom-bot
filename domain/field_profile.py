"""The exhaustive, versioned Foundry field profile (plan §6.5).

Two classifications, one per side of the boundary, and every field has exactly
one of each that applies to it.

| Snapshot path gets | Meaning |
|---|---|
| `snapshot-only` | read from the immutable snapshot for display or calculation; no independently editable database representation exists |
| `reported` | read and reported against a named profile field; what the report *says* depends on that field's authority, not on the path |
| `ignored` | deliberately not read |

| Profile field gets | Meaning |
|---|---|
| `database_authority` | an accepted typed PostgreSQL value exists, so a real comparison is possible and the field's own `difference_direction` says which side a difference makes stale |
| `legacy_authority_deferred` | no accepted typed PostgreSQL authority exists yet. The field names the migration package that owns it, and **no equality comparison is performed or reported** |

The split matters. A path says *where a value is read from*; a field says *what
the platform is entitled to claim about it*. Keeping those separate is what
stopped the previous design from reporting a legacy field as "matching" against
a value nobody had ever entered.

**There is no correction classification here, and no writable mode.** Phase 2
imports identity, mappings and provenance; it corrects nothing. A field group
becomes correctable when the typed package that owns it introduces its domain
model and passes its migration/cutover gate (plan §6.2, §12 Phase 5). ADR 0008's
profile-driven store was rejected on 2026-08-02, and with it every notion that
the profile could authorise a write.

Five properties are enforced here rather than trusted:

1. **Unknown paths are reported and are never readable as classified.**
   `classify` answers `None` for a path no rule covers, and `unknown_paths`
   enumerates every path in a parsed Actor that no rule covers. Nothing consults
   a `None` and proceeds.
2. **A new supported field without a classification fails closed.** Because the
   check is *enumerate the document, subtract the rules*, a `dnd5e` schema
   change that adds a key produces an unknown path rather than silence.
3. **A deferred field cannot be compared.** `comparison_for` raises rather than
   answering, so a caller cannot accidentally obtain `NOT_COMPARABLE` and treat
   it as "no difference". Absence of authority is not agreement.
4. **A deferred field names its owning package**, and the package must be one
   the controlled migration manifest recognises.
5. **A field with database authority states which record a difference makes
   stale.** `difference_direction` has no default, so a new comparable field
   cannot inherit "Foundry is out of date" from the field that happened to be
   written first. `character.display_name` is authored in Foundry and its
   difference means the *platform's* display record is stale.

The profile carries a **version**, and that version is stored on every preview,
import, comparison and calculation. Changing any row changes the version, which
makes every outstanding preview stale.

This module imports nothing outside the standard library and
`domain.snapshot_values`.
"""
from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum

from domain.snapshot_values import Comparison


class SnapshotMode(Enum):
    SNAPSHOT_ONLY = "snapshot-only"
    #: Read and reported against a named profile field. Whether that report is a
    #: comparison or a deferral is the *field's* business, not the path's.
    REPORTED = "reported"
    IGNORED = "ignored"

    @property
    def is_reported(self) -> bool:
        return self is SnapshotMode.REPORTED


class FieldAuthority(Enum):
    """Who is entitled to answer for a field's current value today."""

    #: An accepted typed PostgreSQL value exists, so a difference is a real
    #: difference. *Which side* the difference makes stale is the field's own
    #: `difference_direction` and is not implied by this classification.
    DATABASE = "database_authority"
    #: No accepted typed PostgreSQL authority exists. The accepted legacy path
    #: remains authoritative until the owning package migrates the field once
    #: into its normalized relational model (plan §1, §15; baseline v1.1/v1.5).
    LEGACY_DEFERRED = "legacy_authority_deferred"


class DifferenceDirection(Enum):
    """Which record a difference makes stale, per field.

    Database authority means the platform holds an accepted typed value. It does
    **not** follow that the platform's value is the newer one, and treating the
    two as the same thing is how a report ends up telling an operator to undo a
    change a player legitimately made.

    Each member's value is the reconciliation issue code raised for it, so a
    field's declared direction and the code an operator reads are the same fact
    rather than two that have to be kept in step by hand. A future field
    authored outside the platform adds a member here; it must not borrow
    `PLATFORM_DISPLAY_NAME_STALE`, which names one specific field's evidence.
    """

    #: The platform is where the value is authored and maintained, so a
    #: difference means the Foundry Actor has drifted from it. The operator's
    #: remedy is to update Foundry.
    FOUNDRY_OUT_OF_DATE = "foundry_out_of_date"
    #: `character.display_name` only. Foundry is where players rename a
    #: character, and the import wrote the platform's copy from an *earlier*
    #: Actor name — so a difference means the platform display record has not
    #: caught up. Identity is the external Actor id and is unaffected (OD-42),
    #: and there is nothing for the operator to undo in Foundry.
    PLATFORM_DISPLAY_NAME_STALE = "platform_display_name_stale"


class FieldProfileError(ValueError):
    """The profile is internally inconsistent, or was asked something unsafe."""


@dataclass(frozen=True, slots=True)
class ProfileField:
    """One field the profile knows about, and what may be claimed about it."""

    key: str
    label: str
    authority: FieldAuthority
    #: How this field's two representations are compared. Required for a
    #: `DATABASE` field and forbidden for a deferred one — a deferred field has
    #: nothing to compare against, and declaring a rule for it would invite a
    #: caller to use one.
    comparison: Comparison = Comparison.NOT_COMPARABLE
    #: Which record a difference makes stale. Required for a `DATABASE` field
    #: and forbidden for a deferred one. Required rather than defaulted because
    #: the default would be a guess about authorship, and the wrong guess tells
    #: an operator to undo a legitimate change on the other side.
    difference_direction: DifferenceDirection | None = None
    #: The migration package accountable for this field, from
    #: `docs/project-management/data-migration-register.md`. Required for a
    #: deferred field so a report can name who will migrate it, and forbidden
    #: for a field that already has database authority.
    owning_package: str | None = None
    #: Where the legacy value lives today, for documentation and reconciliation
    #: with the migration register. **Not** an allowlist and not consulted by
    #: any read or write path; the register is authoritative for the mapping.
    legacy_source: str | None = None
    #: Rule or discovery reference supporting the classification.
    source: str = ""

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise FieldProfileError("A profile field requires a key.")

        if self.authority is FieldAuthority.LEGACY_DEFERRED:
            if not self.owning_package:
                raise FieldProfileError(
                    f"{self.key}: a deferred field must name the migration "
                    "package accountable for it, so a report can say who owns "
                    "the value rather than leaving it orphaned."
                )
            if self.comparison is not Comparison.NOT_COMPARABLE:
                raise FieldProfileError(
                    f"{self.key}: a deferred field declares a comparison rule. "
                    "There is no accepted typed value to compare against, so a "
                    "rule here could only produce a fabricated verdict."
                )
            if self.difference_direction is not None:
                raise FieldProfileError(
                    f"{self.key}: a deferred field declares which record a "
                    "difference makes stale. No difference can be established "
                    "for it, so the declaration could only be acted on wrongly."
                )
        else:
            if self.owning_package:
                raise FieldProfileError(
                    f"{self.key}: a field with database authority names a "
                    "migration package. It has already been migrated, or it was "
                    "never a legacy field; it cannot be both."
                )
            if self.comparison is Comparison.NOT_COMPARABLE:
                raise FieldProfileError(
                    f"{self.key}: a field with database authority declares no "
                    "comparison rule, so nothing could ever be reported for it."
                )
            if self.difference_direction is None:
                raise FieldProfileError(
                    f"{self.key}: a field with database authority does not say "
                    "which record a difference makes stale. Database authority "
                    "is not by itself a claim that the platform holds the newer "
                    "value, and assuming it does would tell an operator to undo "
                    "a change made on the other side."
                )

    @property
    def is_deferred(self) -> bool:
        return self.authority is FieldAuthority.LEGACY_DEFERRED

    def stales(self, direction: DifferenceDirection) -> bool:
        """Whether a difference in this field makes `direction`'s record stale."""
        return self.difference_direction is direction


@dataclass(frozen=True, slots=True)
class SnapshotField:
    """One classified path — or path subtree — inside an exported Actor.

    A path ending in `.*` classifies that subtree. Exact rules beat prefix
    rules, and a longer prefix beats a shorter one, so a subtree can be ignored
    wholesale while one path inside it is reported.
    """

    path: str
    mode: SnapshotMode
    #: The profile field this path is read for. Required for a reported path and
    #: forbidden for any other, which `FieldProfile` enforces.
    profile_field: str | None = None
    #: The name later roll consumers ask for, for a snapshot-only input that the
    #: platform actually reads. `None` means "read for display or not at all".
    roll_input: str | None = None
    note: str = ""

    @property
    def is_prefix(self) -> bool:
        return self.path.endswith(".*")

    @property
    def prefix(self) -> str:
        return self.path[:-2] if self.is_prefix else self.path


@dataclass(frozen=True, slots=True)
class UnknownPath:
    """A path present in a parsed Actor that no profile rule classifies."""

    path: str
    #: How many document leaves collapsed onto this canonical path.
    occurrences: int = 1


@dataclass(frozen=True)
class FieldProfile:
    """A versioned, exhaustive classification of both sides of the boundary."""

    version: str
    fields: Mapping[str, ProfileField]
    snapshot_fields: Sequence[SnapshotField]
    #: Explicitly reviewed vocabulary bridges, Foundry key → platform token.
    #: Never a fuzzy match: an unlisted key stays as itself and is compared as
    #: itself, so a wrong guess cannot silently rewrite a proficiency list.
    aliases: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise FieldProfileError("A field profile requires a version.")

        seen: set[str] = set()
        for rule in self.snapshot_fields:
            if rule.path in seen:
                raise FieldProfileError(
                    f"{rule.path} is classified twice. Every supported snapshot "
                    "path has exactly one snapshot mode."
                )
            seen.add(rule.path)

            if rule.mode.is_reported:
                if rule.profile_field is None:
                    raise FieldProfileError(
                        f"{rule.path} is reported but names no profile field."
                    )
                if rule.profile_field not in self.fields:
                    raise FieldProfileError(
                        f"{rule.path} reports against unknown profile field "
                        f"{rule.profile_field!r}."
                    )
            else:
                if rule.profile_field is not None:
                    raise FieldProfileError(
                        f"{rule.path} is {rule.mode.value} and must name no "
                        "profile field: a value that is not reported has "
                        "nowhere to be reported to."
                    )
                if rule.mode is SnapshotMode.IGNORED and rule.roll_input:
                    raise FieldProfileError(
                        f"{rule.path} is ignored and cannot be a roll input."
                    )

        reported_targets = {
            rule.profile_field
            for rule in self.snapshot_fields
            if rule.mode.is_reported
        }
        for profile_field in self.fields.values():
            if profile_field.key not in reported_targets:
                raise FieldProfileError(
                    f"{profile_field.key} is defined but no snapshot path feeds "
                    "it. An unreachable field cannot be reported and would "
                    "silently drop out of the reconciliation."
                )

    # -- lookup ---------------------------------------------------------------

    def classify(self, path: str) -> SnapshotField | None:
        """The rule covering `path`, or `None` when nothing does.

        `None` is the fail-closed answer. A caller that receives it reports the
        path and stops; it never falls back to a default mode, because the
        default a reader would assume — "probably ignorable" — is exactly what
        would let a new field appear unreviewed.
        """
        for rule in self.snapshot_fields:
            if not rule.is_prefix and rule.path == path:
                return rule

        best: SnapshotField | None = None
        for rule in self.snapshot_fields:
            if not rule.is_prefix:
                continue
            prefix = rule.prefix
            if path == prefix or path.startswith(f"{prefix}."):
                if best is None or len(rule.prefix) > len(best.prefix):
                    best = rule
        return best

    def profile_field(self, key: str) -> ProfileField:
        try:
            return self.fields[key]
        except KeyError:
            raise FieldProfileError(
                f"{key!r} is not a field in profile {self.version}."
            ) from None

    def comparison_for(self, key: str) -> Comparison:
        """How to compare `key`, or a refusal when the field is deferred.

        Deliberately raises rather than answering `NOT_COMPARABLE`. A caller
        holding that value would be one `if` away from treating "we have no
        authority here" as "these agree", which is the exact fabrication the
        deferred classification exists to prevent.
        """
        profile_field = self.profile_field(key)
        if profile_field.is_deferred:
            raise FieldProfileError(
                f"{key} has no accepted typed PostgreSQL authority; its value "
                f"remains on the legacy path owned by package "
                f"{profile_field.owning_package}. It is reported as "
                f"{FieldAuthority.LEGACY_DEFERRED.value} and never compared."
            )
        return profile_field.comparison

    def reported_fields(self) -> tuple[ProfileField, ...]:
        """Every field a snapshot is read for, in a stable order."""
        keys = {
            rule.profile_field
            for rule in self.snapshot_fields
            if rule.mode.is_reported and rule.profile_field
        }
        return tuple(self.fields[key] for key in sorted(keys))

    def comparable_fields(self) -> tuple[ProfileField, ...]:
        """Fields with accepted typed authority, so a real comparison exists."""
        return tuple(
            profile_field
            for profile_field in self.reported_fields()
            if not profile_field.is_deferred
        )

    def deferred_fields(self) -> tuple[ProfileField, ...]:
        """Fields reported as `legacy_authority_deferred`, with their owners."""
        return tuple(
            profile_field
            for profile_field in self.reported_fields()
            if profile_field.is_deferred
        )

    def owning_packages(self) -> Mapping[str, str]:
        """Deferred field key → the migration package accountable for it."""
        return {
            profile_field.key: profile_field.owning_package or ""
            for profile_field in self.deferred_fields()
        }

    def roll_inputs(self) -> Mapping[str, SnapshotField]:
        return {
            rule.roll_input: rule
            for rule in self.snapshot_fields
            if rule.roll_input
        }

    def alias(self, token: str) -> str:
        """Bridge one Foundry vocabulary key, or return it unchanged."""
        return self.aliases.get(token, token)

    # -- exhaustiveness -------------------------------------------------------

    def unknown_paths(
        self, actor: Mapping[str, object], *, limit: int = 50
    ) -> tuple[UnknownPath, ...]:
        """Every canonical path in `actor` that no rule classifies.

        This is the fail-closed check. It enumerates the document and subtracts
        the profile, rather than asking the profile what it expects — so a field
        the profile has never heard of appears here instead of nowhere.

        `limit` bounds the report. The count of paths beyond it is preserved by
        the caller, which reports the total separately; an unbounded list of a
        3 MB Actor's leaves is not a diagnostic anybody reads.
        """
        counts: dict[str, int] = {}
        for path in iter_actor_paths(actor):
            if self.classify(path) is None:
                counts[path] = counts.get(path, 0) + 1
        ordered = sorted(counts.items())
        return tuple(
            UnknownPath(path=path, occurrences=count)
            for path, count in ordered[:limit]
        )


def iter_actor_paths(actor: Mapping[str, object]) -> Iterator[str]:
    """Canonical leaf paths of one exported Actor.

    The canonicalisation, which the profile's rules are written against:

    - a mapping contributes `parent.key`;
    - the embedded `items` array collapses by **document type** —
      `items[type=class].system.identifier` — because an item's meaning comes
      from its type, not from its position, and a position-keyed path would make
      every reordering look like a schema change;
    - any other array collapses to `key[]`;
    - an empty mapping or array is itself a leaf, so a subtree that exists but
      is empty is still classified.
    """
    yield from _walk(actor, prefix="")


def _walk(value: object, *, prefix: str) -> Iterator[str]:
    if isinstance(value, Mapping):
        if not value:
            if prefix:
                yield prefix
            return
        for key in sorted(str(name) for name in value):
            child = f"{key}" if not prefix else f"{prefix}.{key}"
            yield from _walk(value[key], prefix=child)
        return

    if isinstance(value, (list, tuple)):
        if not value:
            if prefix:
                yield prefix
            return
        for entry in value:
            if prefix.endswith("items") and isinstance(entry, Mapping):
                document_type = entry.get("type")
                selector = (
                    str(document_type) if isinstance(document_type, str) and document_type
                    else "?"
                )
                yield from _walk(entry, prefix=f"{prefix}[type={selector}]")
            else:
                yield from _walk(entry, prefix=f"{prefix}[]")
        return

    if prefix:
        yield prefix
