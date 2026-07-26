import pytest

from models import resource as resource_module
from models.resource import Resource


def test_natural_twenty_earnings_preserve_half_gold(monkeypatch):
    monkeypatch.setattr(resource_module, "roll_dice", lambda *args, **kwargs: ([20], 20))
    resources = Resource(downtime=5)

    rolls = resources.earn_money(bot=None, downtime=5)

    assert rolls == [(20, 20, 42.0)]
    assert resources.gold == 42
    assert resources.silver == 0
    assert resources.downtime == 0


def test_natural_twenty_preserves_fractional_coin(monkeypatch):
    monkeypatch.setattr(resource_module, "roll_dice", lambda *args, **kwargs: ([20], 10))
    resources = Resource(downtime=5)

    resources.earn_money(bot=None, downtime=5)

    assert resources.gold == 10
    assert resources.silver == 5
    assert resources.copper == 0


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
