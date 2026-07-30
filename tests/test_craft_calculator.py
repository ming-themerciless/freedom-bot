import math

import pytest

from helpers.craft_calculator import calculate_craft


@pytest.mark.parametrize("base_price", [-1, -0.01, math.inf, -math.inf, math.nan])
def test_standard_craft_rejects_invalid_base_price(base_price):
    with pytest.raises(ValueError, match="Base price must be a non-negative finite number"):
        calculate_craft(
            craft_type="non-consumable",
            rarity="standard",
            tool="Smith's Tools",
            tool_level="journeyman",
            quantity=1,
            item_name="Test item",
            base_price=base_price,
        )


def test_zero_base_price_remains_valid():
    result = calculate_craft(
        craft_type="non-consumable",
        rarity="standard",
        tool="Smith's Tools",
        tool_level="journeyman",
        quantity=1,
        item_name="Test item",
        base_price=0,
    )

    assert result["gp_cost"] == 0
    assert result["dt_cost"] == 0


# --- Masterpieces, homebrew rules 6.3.3.1 (PDF p.17) ---


def _masterpiece(rarity, tool_level="master", craft_type="non-consumable"):
    return calculate_craft(
        craft_type=craft_type,
        rarity=rarity,
        tool="Smith's Tools",
        tool_level=tool_level,
        quantity=1,
        item_name="Test masterpiece",
        is_masterpiece=True,
    )


def test_masterpiece_is_a_rare_item_costing_no_downtime():
    result = _masterpiece("rare")

    assert result["gp_cost"] == 2000.0
    assert result["moradinium_cost"] == 16
    assert result["dt_cost"] == 0.0
    assert result["is_legendary_project"] is False


@pytest.mark.parametrize("rarity", ["standard", "common", "uncommon", "very rare", "legendary"])
def test_masterpiece_rejects_any_rarity_other_than_rare(rarity):
    with pytest.raises(ValueError, match="Masterpiece must be a rare item"):
        _masterpiece(rarity)


def test_masterpiece_requires_master_level():
    # Uses a rarity an expert may otherwise craft, so the masterpiece guard is
    # what rejects this rather than the general tool/rarity gate.
    with pytest.raises(ValueError, match="Master level"):
        _masterpiece("common", tool_level="expert")


def test_non_master_is_stopped_by_the_rarity_gate_before_the_masterpiece_check():
    """An expert cannot craft rare at all, masterpiece or not."""
    with pytest.raises(ValueError, match="insufficient to craft a rare item"):
        _masterpiece("rare", tool_level="expert")


def test_masterpiece_must_be_non_consumable():
    with pytest.raises(ValueError, match="non-consumable"):
        _masterpiece("rare", craft_type="consumable")


# --- Crafting reputation, homebrew rules 6.3.3.1 (PDF p.17) ---


@pytest.mark.parametrize(
    "rarity, craft_type, expected_crp",
    [
        ("common", "non-consumable", 2.5),
        ("common", "consumable", 0.5),
        ("uncommon", "non-consumable", 7.5),
        ("uncommon", "consumable", 1.5),
        # Only common and uncommon items earn reputation.
        ("rare", "non-consumable", 0.0),
        ("standard", "consumable", 0.0),
    ],
)
def test_crp_table(rarity, craft_type, expected_crp):
    result = calculate_craft(
        craft_type=craft_type,
        rarity=rarity,
        tool="Smith's Tools",
        tool_level="master",
        quantity=1,
        item_name="Test item",
        base_price=10,
    )

    assert result["earned_crp"] == expected_crp


def test_crp_scales_with_quantity():
    result = calculate_craft(
        craft_type="non-consumable",
        rarity="uncommon",
        tool="Smith's Tools",
        tool_level="expert",
        quantity=4,
        item_name="Test item",
    )

    assert result["earned_crp"] == 30.0


def test_holding_any_master_rank_stops_all_reputation_gain():
    """A character may only ever master one tool, so further CRP cannot be spent.

    Confirmed as a Guild Council ruling on 2026-07-29 (rule-catalogue RC-07).
    Do not "fix" this by reading the CRP table in isolation.
    """
    result = calculate_craft(
        craft_type="non-consumable",
        rarity="uncommon",
        tool="Jeweler's Tools",
        tool_level="expert",
        quantity=1,
        item_name="Test item",
        has_master_tool=True,
    )

    assert result["earned_crp"] == 0.0
    # The craft itself still costs full price; only the reputation is withheld.
    assert result["gp_cost"] == 200.0
    assert result["moradinium_cost"] == 4


def test_reputation_still_accrues_before_any_master_rank():
    result = calculate_craft(
        craft_type="non-consumable",
        rarity="uncommon",
        tool="Jeweler's Tools",
        tool_level="expert",
        quantity=1,
        item_name="Test item",
        has_master_tool=False,
    )

    assert result["earned_crp"] == 7.5


def test_ordinary_rare_craft_still_costs_downtime():
    """The zero-downtime allowance belongs to the masterpiece, not to rare items."""
    result = calculate_craft(
        craft_type="non-consumable",
        rarity="rare",
        tool="Smith's Tools",
        tool_level="master",
        quantity=1,
        item_name="Test item",
    )

    assert result["dt_cost"] == 5.0
