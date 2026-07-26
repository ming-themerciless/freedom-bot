from decimal import Decimal

import pytest

from models.money import Money


@pytest.mark.parametrize(
    ("gold", "expected"),
    [
        (0, (0, 0, 0)),
        ("0.01", (0, 0, 1)),
        ("0.1", (0, 1, 0)),
        ("10.5", (10, 5, 0)),
        (Decimal("3.55"), (3, 5, 5)),
    ],
)
def test_gold_conversion_is_exact(gold, expected):
    assert Money.from_gold(gold).gold_denominations() == expected


def test_denominations_round_trip():
    value = Money.from_denominations(platinum=2, gold=3, silver=4, copper=5)

    assert value.copper == 2345
    assert value.denominations() == (2, 3, 4, 5)


def test_money_is_immutable():
    value = Money(100)

    with pytest.raises(AttributeError):
        value.copper = 200
