"""Deterministic normalisation and comparison of snapshot values.

Reconciliation has to answer one question per field — *does the Foundry Actor
still agree with the database?* — and there are **three** honest answers, not
two:

| Answer | Meaning |
|---|---|
| `MATCH` | both sides carry the same value under this field's comparison rule |
| `DIFFERENT` | both sides carry a value and the values disagree |
| `UNABLE_TO_COMPARE` | one side is missing, malformed, or has no stable identity |

Collapsing the third into either of the others is the defect this module exists
to prevent. Reported as `MATCH`, an unreadable value silently claims agreement.
Reported as `DIFFERENT`, it tells a Council member to update a Foundry Actor
that may already be correct — and after enough false warnings the real ones stop
being read.

Two comparisons need naming explicitly.

**Identifier sets** (skill proficiencies, languages, tool proficiencies, weapon
proficiencies) are compared as *sets of normalised identifiers*, never as the
free text either side displays. `dnd5e` keys them (`acr`, `common`, `smith`);
the Sheet holds whatever a human typed. Normalisation is NFC, case folding and
whitespace collapse, applied to both sides through the one function here.

**Magic items** are compared on **stable catalogue identity** — a source plus an
upstream identifier, or an explicit alias — and never on a player-authored name.
Name-based fuzzy matching produces false positives on exactly the high-value
items where a mistake matters most
([field-ownership.md §8](../docs/rules/field-ownership.md)). An item with no
stable identity on either side is *unidentifiable*, and it makes the set
comparison `UNABLE_TO_COMPARE` rather than inventing an answer — unless the
identifiable parts already disagree, in which case the disagreement is a fact
that the unidentifiable remainder cannot take back.

This module imports nothing outside the standard library.
"""
from __future__ import annotations

import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum

_NORMAL_FORM = "NFC"


def normalize_token(value: str) -> str:
    """The one normalisation applied to both sides of an identifier comparison.

    NFC first so canonically equivalent spellings are one token, then case
    folding, then whitespace collapse. Applied to *both* sides through this
    function: a normalisation used on one side only is not a comparison rule,
    it is a bug with a table.
    """
    normalized = unicodedata.normalize(_NORMAL_FORM, value)
    return " ".join(normalized.casefold().split())


class ComparisonOutcome(Enum):
    MATCH = "match"
    DIFFERENT = "different"
    #: Neither agreement nor disagreement could be established.
    UNABLE_TO_COMPARE = "unable_to_compare"


class Comparison(Enum):
    """How a field's two representations are compared."""

    #: Character-for-character. Used where the exporter is the only writer.
    EXACT_TEXT = "exact_text"
    #: NFC + case fold + whitespace collapse.
    NORMALIZED_TEXT = "normalized_text"
    #: A stable machine identifier such as `system.identifier` on a class item.
    IDENTIFIER = "identifier"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    #: An unordered set of normalised identifiers.
    IDENTIFIER_SET = "identifier_set"
    #: The six ability scores, compared per ability.
    ABILITY_SCORES = "ability_scores"
    #: A set of items compared on stable catalogue identity only.
    MAGIC_ITEM_SET = "magic_item_set"
    #: The field is not compared at all: snapshot-only, or ignored.
    NOT_COMPARABLE = "not_comparable"


@dataclass(frozen=True, slots=True)
class Unavailable:
    """A value one side cannot supply, with the reason a report should print.

    Deliberately a value rather than `None`: `None` is a legitimate stored value
    for several fields, and a sentinel that also means "absent" is how a missing
    input becomes a silent zero.
    """

    reason: str


@dataclass(frozen=True, slots=True)
class ItemIdentity:
    """Stable identity for one owned item, or the absence of one.

    `source` plus `upstream_id` is the catalogue identity plan §7.4 will key on.
    `alias` is an explicitly reviewed mapping for an item that predates the
    catalogue. `display_name` is carried for the report only and takes no part in
    equality, because comparing on it is precisely what this type prevents.
    """

    source: str | None = None
    upstream_id: str | None = None
    alias: str | None = None
    display_name: str = field(default="", compare=False)

    @property
    def is_stable(self) -> bool:
        return bool(self.alias) or bool(self.source and self.upstream_id)

    def describe(self) -> str:
        if self.alias:
            return f"alias:{self.alias}"
        if self.source and self.upstream_id:
            return f"{self.source}:{self.upstream_id}"
        return f"unidentified item {self.display_name!r}"


@dataclass(frozen=True, slots=True)
class ItemSet:
    """Owned items split into those with a stable identity and those without."""

    identified: frozenset[ItemIdentity]
    unidentified: tuple[ItemIdentity, ...] = ()

    @classmethod
    def of(cls, items: Iterable[ItemIdentity]) -> ItemSet:
        identified: set[ItemIdentity] = set()
        unidentified: list[ItemIdentity] = []
        for item in items:
            if item.is_stable:
                identified.add(item)
            else:
                unidentified.append(item)
        return cls(
            identified=frozenset(identified),
            unidentified=tuple(
                sorted(unidentified, key=lambda entry: entry.display_name)
            ),
        )

    def describe(self) -> str:
        parts = sorted(entry.describe() for entry in self.identified)
        if self.unidentified:
            parts.append(f"+{len(self.unidentified)} without stable identity")
        return ", ".join(parts) if parts else "(none)"


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    """One field's answer, in the form a reconciliation report prints."""

    outcome: ComparisonOutcome
    snapshot_display: str
    database_display: str
    #: Why the comparison could not be made. Set only for `UNABLE_TO_COMPARE`.
    reason: str | None = None

    @property
    def is_difference(self) -> bool:
        return self.outcome is ComparisonOutcome.DIFFERENT


class UnsupportedComparisonError(ValueError):
    """A comparison kind was applied to a value shape it cannot read."""


def _display(value: object) -> str:
    if isinstance(value, Unavailable):
        return "(unavailable)"
    if isinstance(value, ItemSet):
        return value.describe()
    if isinstance(value, frozenset | set | tuple | list):
        return ", ".join(sorted(str(item) for item in value)) or "(none)"
    if isinstance(value, Mapping):
        return ", ".join(f"{key}={value[key]}" for key in sorted(value)) or "(none)"
    if value is None:
        return "(none)"
    return str(value)


def _unable(snapshot: object, database: object, reason: str) -> ComparisonResult:
    return ComparisonResult(
        outcome=ComparisonOutcome.UNABLE_TO_COMPARE,
        snapshot_display=_display(snapshot),
        database_display=_display(database),
        reason=reason,
    )


def _decide(
    equal: bool, snapshot: object, database: object
) -> ComparisonResult:
    return ComparisonResult(
        outcome=ComparisonOutcome.MATCH if equal else ComparisonOutcome.DIFFERENT,
        snapshot_display=_display(snapshot),
        database_display=_display(database),
    )


def _as_identifier_set(value: object, side: str) -> frozenset[str] | Unavailable:
    if isinstance(value, Unavailable):
        return value
    if isinstance(value, str) or not isinstance(value, Iterable):
        return Unavailable(
            f"the {side} value is {type(value).__name__}, not a set of identifiers"
        )
    tokens = {normalize_token(str(item)) for item in value}
    return frozenset(token for token in tokens if token)


def _as_integer(value: object, side: str) -> int | Unavailable:
    if isinstance(value, Unavailable):
        return value
    if isinstance(value, bool) or not isinstance(value, int):
        return Unavailable(f"the {side} value is not a whole number")
    return value


def compare(
    kind: Comparison, snapshot_value: object, database_value: object
) -> ComparisonResult:
    """Compare one field's two representations under `kind`.

    Either argument may be `Unavailable`, which always yields
    `UNABLE_TO_COMPARE` carrying that side's reason. That is the path a missing
    or malformed snapshot input takes, and it is why no caller ever has to
    substitute a zero, an empty set or "no proficiency".
    """
    if kind is Comparison.NOT_COMPARABLE:
        raise UnsupportedComparisonError(
            "A snapshot-only or ignored field is never compared. Asking for a "
            "comparison here means a profile row classified it wrongly."
        )

    if isinstance(snapshot_value, Unavailable):
        return _unable(
            snapshot_value, database_value, f"snapshot: {snapshot_value.reason}"
        )
    if isinstance(database_value, Unavailable):
        return _unable(
            snapshot_value, database_value, f"database: {database_value.reason}"
        )

    if kind is Comparison.EXACT_TEXT:
        return _decide(str(snapshot_value) == str(database_value), snapshot_value, database_value)

    if kind in (Comparison.NORMALIZED_TEXT, Comparison.IDENTIFIER):
        return _decide(
            normalize_token(str(snapshot_value)) == normalize_token(str(database_value)),
            snapshot_value,
            database_value,
        )

    if kind is Comparison.INTEGER:
        left = _as_integer(snapshot_value, "snapshot")
        right = _as_integer(database_value, "database")
        if isinstance(left, Unavailable):
            return _unable(snapshot_value, database_value, left.reason)
        if isinstance(right, Unavailable):
            return _unable(snapshot_value, database_value, right.reason)
        return _decide(left == right, snapshot_value, database_value)

    if kind is Comparison.BOOLEAN:
        if not isinstance(snapshot_value, bool) or not isinstance(database_value, bool):
            return _unable(
                snapshot_value, database_value, "one side is not a boolean"
            )
        return _decide(snapshot_value == database_value, snapshot_value, database_value)

    if kind is Comparison.IDENTIFIER_SET:
        left = _as_identifier_set(snapshot_value, "snapshot")
        right = _as_identifier_set(database_value, "database")
        if isinstance(left, Unavailable):
            return _unable(snapshot_value, database_value, left.reason)
        if isinstance(right, Unavailable):
            return _unable(snapshot_value, database_value, right.reason)
        return _decide(left == right, left, right)

    if kind is Comparison.ABILITY_SCORES:
        return _compare_ability_scores(snapshot_value, database_value)

    if kind is Comparison.MAGIC_ITEM_SET:
        return _compare_item_sets(snapshot_value, database_value)

    raise UnsupportedComparisonError(f"No comparison is defined for {kind!r}.")


#: The six `dnd5e` ability keys, in the order a report prints them.
ABILITIES = ("str", "dex", "con", "int", "wis", "cha")


def _compare_ability_scores(snapshot_value: object, database_value: object) -> ComparisonResult:
    if not isinstance(snapshot_value, Mapping) or not isinstance(database_value, Mapping):
        return _unable(
            snapshot_value, database_value, "ability scores are compared as a mapping"
        )
    missing = [
        ability
        for ability in ABILITIES
        if ability not in snapshot_value or ability not in database_value
    ]
    if missing:
        # A partial set is never compared against a complete one: the absent
        # abilities would silently read as agreeing.
        return _unable(
            snapshot_value,
            database_value,
            f"ability scores are incomplete ({', '.join(missing)} missing)",
        )
    for ability in ABILITIES:
        left = _as_integer(snapshot_value[ability], "snapshot")
        right = _as_integer(database_value[ability], "database")
        if isinstance(left, Unavailable):
            return _unable(snapshot_value, database_value, f"{ability}: {left.reason}")
        if isinstance(right, Unavailable):
            return _unable(snapshot_value, database_value, f"{ability}: {right.reason}")
    equal = all(
        snapshot_value[ability] == database_value[ability] for ability in ABILITIES
    )
    return _decide(equal, snapshot_value, database_value)


def _compare_item_sets(snapshot_value: object, database_value: object) -> ComparisonResult:
    if not isinstance(snapshot_value, ItemSet) or not isinstance(database_value, ItemSet):
        return _unable(
            snapshot_value,
            database_value,
            "magic items are compared as an ItemSet, keyed on catalogue identity",
        )

    if snapshot_value.identified != database_value.identified:
        # A disagreement between the identifiable parts is a fact. Items without
        # stable identity cannot make it untrue, so this outranks the refusal
        # below rather than being masked by it.
        return _decide(False, snapshot_value, database_value)

    unidentified = len(snapshot_value.unidentified) + len(database_value.unidentified)
    if unidentified:
        return _unable(
            snapshot_value,
            database_value,
            f"{unidentified} item(s) carry no stable catalogue identity, so the "
            "sets cannot be proven equal. Add an explicit alias rather than "
            "matching on the displayed name.",
        )
    return _decide(True, snapshot_value, database_value)
