from __future__ import annotations

from typing import TYPE_CHECKING

from .resource import Resource

if TYPE_CHECKING:
    from .actor import Actor

class Trade:
    def __init__(self, buyer: Actor | None=None, seller: Actor | None=None, price: Resource | None=None):
        self.buyer = buyer
        self.seller = seller
        self.price = price or Resource()

    @staticmethod
    def _is_same_actor(buyer: Actor, seller: Actor) -> bool:
        if buyer.row_index is not None and seller.row_index is not None:
            return buyer.row_index == seller.row_index
        return buyer.name.strip().casefold() == seller.name.strip().casefold()

    def perform_trade(self):
        if (
            self.buyer is not None
            and self.seller is not None
            and self._is_same_actor(self.buyer, self.seller)
        ):
            raise ValueError("Buyer and seller must be different actors.")

        # Validate both in memory before issuing the single persistence request.
        if self.buyer:
            self.buyer.resources.deduct(
                platinum=self.price.platinum,
                gold=self.price.gold,
                silver=self.price.silver,
                copper=self.price.copper,
                moradinium=self.price.moradinium
            )
        if self.seller:
            self.seller.resources.add(
                platinum=self.price.platinum,
                gold=self.price.gold,
                silver=self.price.silver,
                copper=self.price.copper,
                moradinium=self.price.moradinium
            )

        updates = []
        if self.buyer:
            updates.extend(self.buyer.sheet_updates())
        if self.seller:
            updates.extend(self.seller.sheet_updates())

        from connectors.sheets import batch_update

        batch_update(updates)
