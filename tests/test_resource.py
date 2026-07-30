import pytest

from models import resource as resource_module
from models.resource import Resource


def test_natural_twenty_adds_twenty_percent_to_earnings(monkeypatch):
    """Homebrew rules 6.6 (PDF p.28): a natural 20 raises earnings by 20%."""
    monkeypatch.setattr(resource_module, "roll_dice", lambda *args, **kwargs: ([20], 20))
    resources = Resource(downtime=5)

    rolls = resources.earn_money(bot=None, downtime=5)

    # A roll total of 20 falls in the 16-20 band, paying 28gp; +20% is 33.6gp.
    assert rolls == [(20, 20, 33.6)]
    assert (resources.gold, resources.silver, resources.copper) == (33, 6, 0)
    assert resources.downtime == 0


def test_natural_twenty_preserves_fractional_coin(monkeypatch):
    monkeypatch.setattr(resource_module, "roll_dice", lambda *args, **kwargs: ([20], 10))
    resources = Resource(downtime=5)

    resources.earn_money(bot=None, downtime=5)

    # The 0-10 band pays 7gp; +20% is 8.4gp, which must not lose the 4sp.
    assert (resources.gold, resources.silver, resources.copper) == (8, 4, 0)


@pytest.mark.parametrize(
    "roll_total, expected_gold",
    [
        (0, 7),
        (10, 7),
        (11, 14),
        (15, 14),
        (16, 28),
        (20, 28),
        (21, 56),
        (25, 56),
        (26, 112),
        (40, 112),
    ],
)
def test_earning_bands_match_the_rules_table(monkeypatch, roll_total, expected_gold):
    """Homebrew rules 6.6 (PDF p.28) earnings table, at every band boundary."""
    monkeypatch.setattr(
        resource_module, "roll_dice", lambda *a, **k: ([1], roll_total)
    )
    resources = Resource(downtime=5)

    resources.earn_money(bot=None, downtime=5)

    assert resources.gold == expected_gold
    assert (resources.silver, resources.copper) == (0, 0)


@pytest.mark.parametrize(
    "deduction",
    [
        {"platinum": -1},
        {"gold": -1},
        {"silver": -1},
        {"copper": -1},
    ],
)
def test_negative_currency_deduction_cannot_credit_wallet(deduction):
    resources = Resource(platinum=1, gold=1, silver=1, copper=1)

    with pytest.raises(ValueError, match="cannot be negative"):
        resources.deduct(**deduction)

    assert resources.format_coins() == "1pp, 1gp, 1sp, 1cp"


def test_deduct_breaks_larger_coins_and_preserves_total_value():
    resources = Resource(platinum=1)

    resources.deduct(gold=3, silver=4, copper=5)

    assert (resources.platinum, resources.gold, resources.silver, resources.copper) == (
        0,
        6,
        5,
        5,
    )


def test_failed_deduction_does_not_mutate_any_resource():
    resources = Resource(gold=1, moradinium=5)

    with pytest.raises(ValueError, match="Not enough currency"):
        resources.deduct(gold=2, moradinium=3)

    assert resources.gold == 1
    assert resources.moradinium == 5


@pytest.mark.parametrize("downtime", [-5, 0, 4, 6, 15])
def test_validate_downtime_rejects_invalid_or_unavailable_amounts(downtime):
    resources = Resource(downtime=10)

    with pytest.raises(ValueError):
        resources.validate_downtime(downtime)


# --- Selling, homebrew rules 4.1 / 4.1.1 / 4.2.1 (PDF p.11-12) ---


def _sell(monkeypatch, roll, total, **kwargs):
    """Run one sale and return the resulting wallet in copper."""
    monkeypatch.setattr(resource_module, "roll_dice", lambda *a, **k: ([roll], total))
    resources = Resource()
    resources.sale(bot=None, item="Test item", **kwargs)
    return (
        resources.gold * 100 + resources.silver * 10 + resources.copper
    )


def test_sale_base_percentage_is_one_hundred_and_forty(monkeypatch):
    assert _sell(monkeypatch, roll=1, total=0, crafting_cost=100) == 140 * 100


def test_sale_never_drops_below_the_base_percentage(monkeypatch):
    """A negative haggling total must not sell below 140% of crafting cost."""
    assert _sell(monkeypatch, roll=1, total=-4, crafting_cost=100) == 140 * 100


def test_sale_haggling_adds_roll_to_the_percentage(monkeypatch):
    assert _sell(monkeypatch, roll=15, total=15, crafting_cost=100) == 155 * 100


def test_sale_percentage_is_capped_at_one_hundred_and_eighty(monkeypatch):
    assert _sell(monkeypatch, roll=19, total=60, crafting_cost=100) == 180 * 100


def test_natural_twenty_stacks_past_the_cap(monkeypatch):
    assert _sell(monkeypatch, roll=20, total=60, crafting_cost=100) == 190 * 100


def test_own_shop_reaches_the_maximum_percentage(monkeypatch):
    """The PDF worked example on p.12: 140 + 20 + 10 + 20 = 190%, 25gp -> 47gp 5sp."""
    total_copper = _sell(
        monkeypatch,
        roll=20,
        total=20,
        crafting_cost=25,
        point_of_sale="your own shop",
    )

    assert total_copper == 4750  # 47gp 5sp
