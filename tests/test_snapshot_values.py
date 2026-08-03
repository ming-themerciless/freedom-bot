"""`different` and `unable to compare` are distinct answers, always."""
from __future__ import annotations

import pytest

from domain.snapshot_values import (
    Comparison,
    ComparisonOutcome,
    ItemIdentity,
    ItemSet,
    Unavailable,
    UnsupportedComparisonError,
    compare,
    normalize_token,
)


def outcome(kind, snapshot, database) -> ComparisonOutcome:
    return compare(kind, snapshot, database).outcome


# -- normalisation -------------------------------------------------------------


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ("Smith", "smith"),
        ("  Common  Sign   Language ", "common sign language"),
        ("Ölfass", "ölfass"),
        ("élan", "élan"),
    ],
)
def test_normalisation_is_applied_to_both_sides(left, right):
    assert normalize_token(left) == normalize_token(right)


def test_normalisation_does_not_merely_lowercase():
    # Full case folding, so the fold is at least as wide as `lower()`.
    assert normalize_token("STRASSE") == normalize_token("Straße")


# -- unavailability ------------------------------------------------------------


@pytest.mark.parametrize(
    "kind",
    [
        Comparison.EXACT_TEXT,
        Comparison.NORMALIZED_TEXT,
        Comparison.IDENTIFIER,
        Comparison.INTEGER,
        Comparison.BOOLEAN,
        Comparison.IDENTIFIER_SET,
        Comparison.ABILITY_SCORES,
        Comparison.MAGIC_ITEM_SET,
    ],
)
def test_an_unavailable_side_is_never_a_match_or_a_difference(kind):
    result = compare(kind, Unavailable("the export omits it"), "anything")

    assert result.outcome is ComparisonOutcome.UNABLE_TO_COMPARE
    assert "the export omits it" in result.reason
    assert result.is_difference is False


def test_an_unavailable_database_side_is_reported_as_such():
    result = compare(Comparison.INTEGER, 3, Unavailable("never bootstrapped"))

    assert result.outcome is ComparisonOutcome.UNABLE_TO_COMPARE
    assert result.reason.startswith("database:")


def test_a_not_comparable_field_refuses_to_be_compared():
    with pytest.raises(UnsupportedComparisonError):
        compare(Comparison.NOT_COMPARABLE, 1, 1)


# -- scalars -------------------------------------------------------------------


def test_exact_text_is_character_for_character():
    assert outcome(Comparison.EXACT_TEXT, "Aria", "Aria") is ComparisonOutcome.MATCH
    assert outcome(Comparison.EXACT_TEXT, "Aria", "aria") is ComparisonOutcome.DIFFERENT


def test_normalized_text_ignores_case_and_spacing():
    assert outcome(Comparison.NORMALIZED_TEXT, "Half  Elf", "half elf") is ComparisonOutcome.MATCH
    assert outcome(Comparison.NORMALIZED_TEXT, "Half Elf", "Tiefling") is ComparisonOutcome.DIFFERENT


def test_identifiers_compare_as_identifiers():
    assert outcome(Comparison.IDENTIFIER, "sorcerer", "Sorcerer") is ComparisonOutcome.MATCH
    assert outcome(Comparison.IDENTIFIER, "sorcerer", "wizard") is ComparisonOutcome.DIFFERENT


def test_integers_refuse_a_non_integer_rather_than_coercing_it():
    assert outcome(Comparison.INTEGER, 9, 9) is ComparisonOutcome.MATCH
    assert outcome(Comparison.INTEGER, 9, 10) is ComparisonOutcome.DIFFERENT
    assert outcome(Comparison.INTEGER, "9", 9) is ComparisonOutcome.UNABLE_TO_COMPARE
    # bool is an int subclass and must not pass as one.
    assert outcome(Comparison.INTEGER, True, 1) is ComparisonOutcome.UNABLE_TO_COMPARE


def test_booleans_are_compared_strictly():
    assert outcome(Comparison.BOOLEAN, True, True) is ComparisonOutcome.MATCH
    assert outcome(Comparison.BOOLEAN, True, False) is ComparisonOutcome.DIFFERENT
    assert outcome(Comparison.BOOLEAN, 1, True) is ComparisonOutcome.UNABLE_TO_COMPARE


# -- identifier sets -----------------------------------------------------------


def test_identifier_sets_are_unordered_and_normalised():
    assert (
        outcome(Comparison.IDENTIFIER_SET, ["Common", "elvish"], {"elvish", "common"})
        is ComparisonOutcome.MATCH
    )


def test_a_missing_member_is_a_difference():
    assert (
        outcome(Comparison.IDENTIFIER_SET, ["common"], {"common", "druidic"})
        is ComparisonOutcome.DIFFERENT
    )


def test_a_string_is_not_a_set_of_identifiers():
    assert (
        outcome(Comparison.IDENTIFIER_SET, "common", {"common"})
        is ComparisonOutcome.UNABLE_TO_COMPARE
    )


def test_empty_sets_match_each_other():
    assert outcome(Comparison.IDENTIFIER_SET, [], set()) is ComparisonOutcome.MATCH


# -- ability scores ------------------------------------------------------------


def scores(**overrides) -> dict[str, int]:
    base = {"str": 10, "dex": 10, "con": 10, "int": 10, "wis": 10, "cha": 10}
    base.update(overrides)
    return base


def test_ability_scores_match_when_every_ability_agrees():
    assert outcome(Comparison.ABILITY_SCORES, scores(), scores()) is ComparisonOutcome.MATCH


def test_one_differing_ability_is_a_difference():
    assert (
        outcome(Comparison.ABILITY_SCORES, scores(cha=20), scores())
        is ComparisonOutcome.DIFFERENT
    )


def test_an_incomplete_ability_set_is_never_compared_against_a_complete_one():
    partial = scores()
    partial.pop("cha")

    result = compare(Comparison.ABILITY_SCORES, partial, scores())

    assert result.outcome is ComparisonOutcome.UNABLE_TO_COMPARE
    assert "cha" in result.reason


def test_a_non_numeric_ability_is_unable_to_compare():
    assert (
        outcome(Comparison.ABILITY_SCORES, scores(str="sixteen"), scores())
        is ComparisonOutcome.UNABLE_TO_COMPARE
    )


# -- magic items ---------------------------------------------------------------


def stable(name: str, upstream: str) -> ItemIdentity:
    return ItemIdentity(source="FBH", upstream_id=upstream, display_name=name)


def unstable(name: str) -> ItemIdentity:
    return ItemIdentity(display_name=name)


def test_items_are_compared_on_catalogue_identity_not_on_name():
    snapshot = ItemSet.of([stable("Ring of Warmth", "ring-warmth")])
    database = ItemSet.of([stable("A Warm Ring", "ring-warmth")])

    assert outcome(Comparison.MAGIC_ITEM_SET, snapshot, database) is ComparisonOutcome.MATCH


def test_a_differing_identity_is_a_difference_even_when_names_agree():
    snapshot = ItemSet.of([stable("Ring of Warmth", "ring-warmth")])
    database = ItemSet.of([stable("Ring of Warmth", "ring-cold")])

    assert outcome(Comparison.MAGIC_ITEM_SET, snapshot, database) is ComparisonOutcome.DIFFERENT


def test_an_explicit_alias_establishes_identity():
    snapshot = ItemSet.of([ItemIdentity(alias="fb:sunblade", display_name="Sunblade")])
    database = ItemSet.of([ItemIdentity(alias="fb:sunblade", display_name="Sun Blade")])

    assert outcome(Comparison.MAGIC_ITEM_SET, snapshot, database) is ComparisonOutcome.MATCH


def test_an_item_without_stable_identity_makes_the_set_unable_to_compare():
    snapshot = ItemSet.of([stable("Ring of Warmth", "ring-warmth"), unstable("Curio")])
    database = ItemSet.of([stable("Ring of Warmth", "ring-warmth")])

    result = compare(Comparison.MAGIC_ITEM_SET, snapshot, database)

    assert result.outcome is ComparisonOutcome.UNABLE_TO_COMPARE
    assert "stable catalogue identity" in result.reason
    assert "alias" in result.reason


def test_a_known_disagreement_outranks_an_unidentifiable_remainder():
    # The identifiable halves already disagree; an unidentified extra cannot
    # make that untrue, so the answer stays `different`.
    snapshot = ItemSet.of([stable("Ring", "ring-a"), unstable("Curio")])
    database = ItemSet.of([stable("Ring", "ring-b")])

    assert outcome(Comparison.MAGIC_ITEM_SET, snapshot, database) is ComparisonOutcome.DIFFERENT


def test_two_empty_inventories_match():
    assert (
        outcome(Comparison.MAGIC_ITEM_SET, ItemSet.of([]), ItemSet.of([]))
        is ComparisonOutcome.MATCH
    )


def test_a_bare_list_is_not_an_item_set():
    result = compare(Comparison.MAGIC_ITEM_SET, ["Ring"], ItemSet.of([]))

    assert result.outcome is ComparisonOutcome.UNABLE_TO_COMPARE
    assert "catalogue identity" in result.reason


def test_item_identity_stability_requires_both_halves():
    assert ItemIdentity(source="FBH", upstream_id="x").is_stable is True
    assert ItemIdentity(source="FBH").is_stable is False
    assert ItemIdentity(upstream_id="x").is_stable is False
    assert ItemIdentity(alias="fb:x").is_stable is True


def test_display_names_never_take_part_in_identity():
    assert stable("One Name", "same") == stable("Another Name", "same")
