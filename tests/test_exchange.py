import pytest

from models.exchange import calculate_exchange


@pytest.mark.parametrize(
    ("from_denomination", "to_denomination", "amount", "expected"),
    [
        ("pp", "gp", 2, {"platinum": -2, "gold": 20, "silver": 0, "copper": 0}),
        ("gp", "sp", 3, {"platinum": 0, "gold": -3, "silver": 30, "copper": 0}),
        ("sp", "cp", 4, {"platinum": 0, "gold": 0, "silver": -4, "copper": 40}),
        ("gp", "pp", 15, {"platinum": 1, "gold": -10, "silver": 0, "copper": 0}),
    ],
)
def test_exchange_preserves_value(
    from_denomination,
    to_denomination,
    amount,
    expected,
):
    wallet = {"platinum": 20, "gold": 20, "silver": 20, "copper": 20}

    assert (
        calculate_exchange(from_denomination, to_denomination, amount, wallet)
        == expected
    )


@pytest.mark.parametrize(
    ("from_denomination", "to_denomination", "amount", "message"),
    [
        ("gp", "sp", 0, "positive integer"),
        ("gp", "gp", 1, "to itself"),
        ("invalid", "gp", 1, "Invalid denomination"),
        ("gp", "sp", 2, "Not enough GP"),
    ],
)
def test_exchange_rejects_invalid_requests(
    from_denomination,
    to_denomination,
    amount,
    message,
):
    wallet = {"platinum": 0, "gold": 1, "silver": 0, "copper": 0}

    with pytest.raises(ValueError, match=message):
        calculate_exchange(from_denomination, to_denomination, amount, wallet)
