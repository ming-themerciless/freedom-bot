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
