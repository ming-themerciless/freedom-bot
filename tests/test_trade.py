from types import SimpleNamespace

import pytest

from models.resource import Resource
from models.trade import Trade


@pytest.mark.parametrize(
    ("buyer_name", "seller_name"),
    [
        ("Aria", "Aria"),
        ("Aria", " aria "),
        ("ARIA", "aria"),
    ],
)
def test_trade_rejects_same_actor_name_before_mutation(buyer_name, seller_name):
    buyer = SimpleNamespace(
        name=buyer_name,
        row_index=None,
        resources=Resource(gold=100),
    )
    seller = SimpleNamespace(
        name=seller_name,
        row_index=None,
        resources=Resource(gold=100),
    )

    with pytest.raises(ValueError, match="Buyer and seller must be different"):
        Trade(buyer=buyer, seller=seller, price=Resource(gold=10)).perform_trade()

    assert buyer.resources.gold == 100
    assert seller.resources.gold == 100


def test_trade_rejects_same_loaded_sheet_row_before_mutation():
    buyer = SimpleNamespace(
        name="Old display name",
        row_index=17,
        resources=Resource(gold=100),
    )
    seller = SimpleNamespace(
        name="New display name",
        row_index=17,
        resources=Resource(gold=100),
    )

    with pytest.raises(ValueError, match="Buyer and seller must be different"):
        Trade(buyer=buyer, seller=seller, price=Resource(gold=10)).perform_trade()

    assert buyer.resources.gold == 100
    assert seller.resources.gold == 100
