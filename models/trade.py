from __future__ import annotations
from .resource import Resource
from .actor import Actor

class Trade:
    def __init__(self, buyer: Actor | None=None, seller: Actor | None=None, price: Resource | None=None):
        self.buyer = buyer
        self.seller = seller
        self.price = price or Resource()

    def perform_trade(self):
        if self.buyer:
            self.buyer.resources.deduct(
                platinum=self.price.platinum,
                gold=self.price.gold,
                silver=self.price.silver,
                copper=self.price.copper,
                moradinium=self.price.moradinium
            )
            self.buyer.save_to_sheet()
        if self.seller:
            self.seller.resources.add(
                platinum=self.price.platinum,
                gold=self.price.gold,
                silver=self.price.silver,
                copper=self.price.copper,
                moradinium=self.price.moradinium
            )
            self.seller.save_to_sheet()
