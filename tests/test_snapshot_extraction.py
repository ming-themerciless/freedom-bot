"""Extraction refuses rather than defaulting, and identifies rather than guessing."""
from __future__ import annotations

from copy import deepcopy

import pytest

from application.foundry.artifact import ingest_bytes
from application.foundry.extraction import SnapshotActorView
from application.foundry.parser import parse_snapshot
from domain.foundry import OBSERVED_DEPLOYMENT
from domain.foundry_profile import PROFILE
from domain.snapshot_values import ItemSet, Unavailable
from tests import foundry_fixtures as fx


def view(actor_document) -> SnapshotActorView:
    document = fx.bundle(actors=(actor_document,))
    snapshot = parse_snapshot(
        ingest_bytes(fx.encode(document)), deployment=OBSERVED_DEPLOYMENT
    )
    return SnapshotActorView(snapshot.actors[0], PROFILE)


def unavailable(value) -> Unavailable:
    assert isinstance(value, Unavailable), f"expected Unavailable, got {value!r}"
    return value


# -- identity and progression --------------------------------------------------


def test_class_is_read_from_the_identifier_not_the_display_name():
    document = fx.actor(class_identifier="sorcerer", class_name="Sorceress")

    assert view(document).value_for("character.class") == "sorcerer"


def test_a_class_without_an_identifier_refuses_rather_than_using_its_name():
    document = deepcopy(fx.actor())
    for item in document["items"]:
        if item["type"] == "class":
            item["system"].pop("identifier")

    reason = unavailable(view(document).value_for("character.class")).reason

    assert "system.identifier" in reason
    assert "display name" in reason


def test_a_multiclassed_actor_is_unable_to_compare_rather_than_first_class_wins():
    document = deepcopy(fx.actor())
    document["items"].append(
        fx.item("class", "Warlock", identifier="warlock", levels=3)
    )

    reason = unavailable(view(document).value_for("character.class")).reason

    assert "multiclassed" in reason


def test_level_is_the_sum_of_class_levels():
    document = deepcopy(fx.actor(level=9))
    document["items"].append(
        fx.item("class", "Warlock", identifier="warlock", levels=3)
    )

    assert view(document).value_for("character.level") == 12


def test_a_class_without_levels_refuses_rather_than_defaulting_to_one():
    document = deepcopy(fx.actor())
    for item in document["items"]:
        if item["type"] == "class":
            item["system"].pop("levels")

    assert isinstance(view(document).value_for("character.level"), Unavailable)


def test_two_race_items_are_ambiguous_and_never_resolved_by_choosing_one():
    document = deepcopy(fx.actor())
    document["items"].append(fx.item("race", "Synthetic Tiefling"))

    reason = unavailable(view(document).value_for("character.race")).reason

    assert "2 race items" in reason


def test_a_missing_background_refuses_rather_than_returning_an_empty_string():
    document = deepcopy(fx.actor())
    document["items"] = [
        item for item in document["items"] if item["type"] != "background"
    ]

    assert isinstance(view(document).value_for("character.background"), Unavailable)


def test_ability_scores_are_read_from_value_and_never_from_a_derived_modifier():
    scores = view(fx.actor()).value_for("character.ability_scores")

    assert scores == {"str": 16, "dex": 8, "con": 14, "int": 10, "wis": 12, "cha": 20}


def test_a_missing_ability_refuses_the_whole_set():
    document = deepcopy(fx.actor())
    document["system"]["abilities"].pop("cha")

    reason = unavailable(view(document).value_for("character.ability_scores")).reason

    assert "cha" in reason


def test_feats_are_a_set_of_names():
    document = fx.actor(feats=("Synthetic Alertness", "Invented Toughness"))

    assert view(document).value_for("character.feats") == frozenset(
        {"Synthetic Alertness", "Invented Toughness"}
    )


def test_no_feats_is_an_empty_set_not_an_unavailable():
    # An Actor genuinely may have no feats, and the export says so by carrying
    # no feat items. That is a value, not a missing input.
    assert view(fx.actor(feats=())).value_for("character.feats") == frozenset()


# -- proficiencies -------------------------------------------------------------


def test_tool_keys_are_bridged_through_the_reviewed_alias_table():
    held = view(fx.actor()).value_for("proficiencies.tools")

    assert held == frozenset({"smith", "alchemist", "disguise", "scroll"})


def test_a_tool_at_level_zero_is_not_held():
    document = fx.actor(tools={"smith": 1, "weaver": 0})

    assert view(document).value_for("proficiencies.tools") == frozenset({"smith"})


def test_a_non_numeric_tool_level_refuses_the_set():
    document = fx.actor(tools={"smith": "journeyman"})

    assert isinstance(view(document).value_for("proficiencies.tools"), Unavailable)


def test_custom_languages_are_read_alongside_the_srd_keys():
    held = view(fx.actor()).value_for("proficiencies.languages")

    assert held == frozenset({"common", "elvish", "Common Sign Language"})


def test_several_custom_entries_are_split_on_the_dnd5e_separator():
    document = fx.actor(custom_languages="Druidic; Common Sign Language")

    held = view(document).value_for("proficiencies.languages")

    assert {"Druidic", "Common Sign Language"} <= set(held)


def test_a_missing_trait_block_refuses_rather_than_reporting_no_languages():
    document = deepcopy(fx.actor())
    document["system"]["traits"].pop("languages")

    assert isinstance(view(document).value_for("proficiencies.languages"), Unavailable)


def test_weapon_proficiencies_are_read_from_their_own_trait():
    document = fx.actor(weapon_proficiencies=("sim", "mar"))

    assert view(document).value_for("proficiencies.special_weapons") == frozenset(
        {"sim", "mar"}
    )


# -- currency ------------------------------------------------------------------


def test_currency_converts_to_integer_copper():
    document = fx.actor(currency={"pp": 1, "gp": 23, "sp": 4, "cp": 5, "ep": 0})

    assert view(document).value_for("wallet.balance_copper") == 1000 + 2300 + 40 + 5


def test_nonzero_electrum_is_an_anomaly_and_is_never_converted():
    document = fx.actor(currency={"pp": 0, "gp": 1, "sp": 0, "cp": 0, "ep": 3})

    reason = unavailable(view(document).value_for("wallet.balance_copper")).reason

    assert "electrum" in reason
    assert "never converted" in reason


def test_a_negative_denomination_refuses_rather_than_being_clamped():
    document = fx.actor(currency={"pp": 0, "gp": -1, "sp": 0, "cp": 0, "ep": 0})

    assert isinstance(view(document).value_for("wallet.balance_copper"), Unavailable)


def test_a_missing_currency_block_refuses_rather_than_reading_as_zero():
    document = deepcopy(fx.actor())
    document["system"].pop("currency")

    assert isinstance(view(document).value_for("wallet.balance_copper"), Unavailable)


# -- magic items ---------------------------------------------------------------


def test_only_items_with_a_real_rarity_are_magic_items():
    items = view(fx.actor()).value_for("inventory.magic_items")

    assert isinstance(items, ItemSet)
    assert {identity.upstream_id for identity in items.identified} == {"synthetic-band"}


def test_a_magic_item_without_stable_identity_is_kept_but_unidentified():
    document = fx.actor(
        magic_items=(fx.magic_item("Nameless Trinket", identifier=None, book=None),)
    )

    items = view(document).value_for("inventory.magic_items")

    assert items.identified == frozenset()
    assert [entry.display_name for entry in items.unidentified] == ["Nameless Trinket"]


def test_a_common_item_is_mundane_and_stays_out_of_the_comparison():
    document = fx.actor(magic_items=(fx.magic_item("Torch", rarity="common"),))

    items = view(document).value_for("inventory.magic_items")

    assert items.identified == frozenset()
    assert items.unidentified == ()


# -- snapshot-only roll inputs -------------------------------------------------


def test_skill_proficiencies_are_readable_as_a_roll_input():
    assert view(fx.actor()).roll_input("skill_proficiencies") == {
        "acr": 0,
        "ath": 1,
        "prc": 2,
    }


def test_a_missing_skill_block_refuses_rather_than_reporting_no_proficiency():
    document = deepcopy(fx.actor())
    document["system"].pop("skills")

    reason = unavailable(view(document).roll_input("skill_proficiencies")).reason

    assert "system.skills" in reason


def test_an_out_of_range_skill_level_refuses_rather_than_clamping():
    document = fx.actor(skills={"acr": 7})

    assert isinstance(view(document).roll_input("skill_proficiencies"), Unavailable)


def test_bastion_facilities_report_what_was_observed():
    facilities = view(fx.actor()).roll_input("bastion_facilities")

    assert facilities == (
        {"name": "Synthetic Scriptorium", "subtype": "scriptorium", "size": "roomy"},
    )


def test_no_recorded_facilities_is_an_empty_observation_not_a_finding():
    document = deepcopy(fx.actor())
    document["items"] = [
        item for item in document["items"] if item["type"] != "facility"
    ]

    # Absence is not evidence of absence: the caller receives an empty
    # observation, never a claim that the character has no Bastion.
    assert view(document).roll_input("bastion_facilities") == ()


def test_an_unknown_roll_input_name_refuses():
    reason = unavailable(view(fx.actor()).roll_input("invented")).reason

    assert "no roll input" in reason


def test_an_unknown_profile_field_has_no_extractor():
    reason = unavailable(view(fx.actor()).value_for("character.invented")).reason

    assert "no snapshot extractor" in reason


@pytest.mark.parametrize(
    "profile_field",
    sorted(entry.key for entry in PROFILE.reported_fields()),
)
def test_every_reported_field_is_extractable_from_the_fixture(profile_field):
    """Deferred fields are extracted too — that is how presence is determined.

    The reconciliation row records *whether* Foundry holds a value, never the
    value itself, and it can only answer that by asking the extractor. A field
    with no extractor would report "Foundry supplies nothing" for every Actor,
    which is a false statement rather than a missing one.
    """
    value = view(fx.actor()).value_for(profile_field)

    assert not isinstance(value, Unavailable), value
