from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


@dataclass(frozen=True, slots=True)
class Money:
    """An exact monetary value stored in the smallest supported unit."""

    copper: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.copper, int):
            raise TypeError("Money.copper must be an integer.")

    @classmethod
    def from_gold(cls, gold: int | float | str | Decimal) -> Money:
        try:
            value = Decimal(str(gold))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Invalid gold amount: {gold!r}") from exc
        copper = int((value * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        return cls(copper)

    @classmethod
    def from_denominations(
        cls,
        *,
        platinum: int = 0,
        gold: int = 0,
        silver: int = 0,
        copper: int = 0,
    ) -> Money:
        values = (platinum, gold, silver, copper)
        if not all(isinstance(value, int) for value in values):
            raise TypeError("Money denominations must be integers.")
        return cls(platinum * 1000 + gold * 100 + silver * 10 + copper)

    def denominations(self) -> tuple[int, int, int, int]:
        """Return a canonical pp/gp/sp/cp representation."""
        sign = -1 if self.copper < 0 else 1
        remainder = abs(self.copper)
        platinum, remainder = divmod(remainder, 1000)
        gold, remainder = divmod(remainder, 100)
        silver, copper = divmod(remainder, 10)
        return tuple(sign * value for value in (platinum, gold, silver, copper))

    def gold_denominations(self) -> tuple[int, int, int]:
        """Return gp/sp/cp without promoting gold into platinum."""
        sign = -1 if self.copper < 0 else 1
        remainder = abs(self.copper)
        gold, remainder = divmod(remainder, 100)
        silver, copper = divmod(remainder, 10)
        return sign * gold, sign * silver, sign * copper

    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.copper + other.copper)

    def __sub__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.copper - other.copper)

