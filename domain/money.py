"""Money, as an exact integer count of copper pieces.

One representation, one unit: `Money` is a signed whole number of copper
pieces. Every other denomination is a *rate* against it, and the rates are the
platform's single conversion table — the same one `models/exchange.py` has
always used and the same one the legacy `models/money.py` encodes.

**What this type deliberately does not do: decompose a value back into
denominations.** Construction from pp/gp/sp/cp exists because the Sheet stores
four counters and an adapter has to turn them into a value. The reverse does
not exist, and its absence is the decision recorded as **OD-50**: two wallets
holding one hundred copper — ten silver, or one gold — are the same *value* and
different *representations*, and the Sheet's stored counters are what a player
sees. Anything that rendered a canonical decomposition would silently rewrite
what many characters' wallets look like. Rendering belongs to the adapter that
holds the stored counters; this type holds the value.

**Sign.** `Money` may be negative. A ledger entry is signed, and debt is a real
game concept (RC-D4). The rule that a *balance* may not go negative belongs to
the thing that holds a balance, not to the number itself — enforcing it here
would make it impossible to express the debit half of a transfer.

This module imports nothing outside the standard library.
"""
from __future__ import annotations

from dataclasses import dataclass

from domain.quantities import QuantityError, whole_number

#: The platform's only conversion table, in copper.
COPPER_PER_PLATINUM = 1000
COPPER_PER_GOLD = 100
COPPER_PER_SILVER = 10
COPPER_PER_COPPER = 1


@dataclass(frozen=True, slots=True, order=True)
class Money:
    """A signed exact amount, counted in copper pieces."""

    copper: int

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "copper", whole_number(self.copper, name="Money.copper")
        )

    # -- construction ------------------------------------------------------ #

    @classmethod
    def zero(cls) -> Money:
        return cls(0)

    @classmethod
    def from_denominations(
        cls,
        *,
        platinum: int = 0,
        gold: int = 0,
        silver: int = 0,
        copper: int = 0,
    ) -> Money:
        """Build a value from coin counts. The reverse is deliberately absent."""
        return cls(
            whole_number(platinum, name="platinum") * COPPER_PER_PLATINUM
            + whole_number(gold, name="gold") * COPPER_PER_GOLD
            + whole_number(silver, name="silver") * COPPER_PER_SILVER
            + whole_number(copper, name="copper") * COPPER_PER_COPPER
        )

    # -- arithmetic -------------------------------------------------------- #

    def __add__(self, other: object) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.copper + other.copper)

    def __sub__(self, other: object) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.copper - other.copper)

    def __neg__(self) -> Money:
        return Money(-self.copper)

    def __mul__(self, count: int) -> Money:
        """Repeat an amount a whole number of times.

        Multiplication by a fraction or a percentage is **not** offered. A rule
        that takes a percentage of a price — the sale percentage, for one —
        needs a stated rounding policy, and that policy belongs with the rule
        rather than being implied by an operator here.
        """
        if isinstance(count, bool) or not isinstance(count, int):
            return NotImplemented
        return Money(self.copper * count)

    __rmul__ = __mul__

    # -- inspection -------------------------------------------------------- #

    @property
    def is_zero(self) -> bool:
        return self.copper == 0

    @property
    def is_negative(self) -> bool:
        return self.copper < 0

    def __str__(self) -> str:
        """Diagnostics only. This is not a player-facing rendering."""
        return f"{self.copper}cp"


def sum_money(amounts: object) -> Money:
    """Total an iterable of `Money`, refusing anything else in it.

    `sum()` would start from the integer `0` and fail on the first addition with
    a `TypeError` naming `int`, which reads like a defect in `Money`. This
    starts from zero money and names the offending element instead.
    """
    total = Money.zero()
    for index, amount in enumerate(amounts):
        if not isinstance(amount, Money):
            raise QuantityError(
                f"sum_money received {type(amount).__name__} at position "
                f"{index}; every element must be Money."
            )
        total += amount
    return total
