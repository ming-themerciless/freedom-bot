from __future__ import annotations
from .resource import Resource
from .actor import Actor
from connectors.sheets import batch_update

class Trade:
    def __init__(self, buyer: Actor | None=None, seller: Actor | None=None, price: Resource | None=None):
        self.buyer = buyer
        self.seller = seller
        self.price = price or Resource()

    def perform_trade(self):
        if self.buyer is self.seller and self.buyer is not None:
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
        batch_update(updates)
