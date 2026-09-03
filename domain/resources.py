"""Non-monetary resources, each with an explicit smallest unit.

Two quantities, two units, both integers:

| Quantity | Smallest unit | Why that unit |
|---|---|---|
| `Moradinium` | one piece | The Sheet stores a whole count and every rule that touches it (mining, tribute, trade) moves whole pieces |
| `Downtime` | one **thousandth of a day** | OD-08: downtime is recorded to three decimals, which is exactly the thousandth-day |

**Downtime is where the live bot and the accepted unit disagree**, and this type
is the correction. `models/resource.py` loads column I through
`helpers.utils.safe_number`, producing a Python `float`: a value with four
decimals is accepted silently even though it is finer than any unit the platform
recognises, and an unparseable cell becomes `0.0` with no report. **OD-49**
rules that the domain quantity is an integer count of thousandth-days and
refuses anything else — no rounding, because rounding here is the same silent
coercion wearing a different hat.

What the *adapter* does with a Sheet cell that cannot be represented is a
separate decision, also OD-49: it marks the value explicitly as an invalid
persisted value and the command renders what it renders today. Refusing in the
domain and preserving the player's view are not in tension; they happen at
different boundaries.

**Sign.** Both types may be negative, for the reason given in `domain.money`: a
ledger entry is signed, and the rule that a balance may not go negative belongs
to whatever holds the balance.

This module imports nothing outside the standard library.
"""
from __future__ import annotations

from dataclasses import dataclass

from domain.quantities import whole_number

#: OD-08's ruling, as a constant rather than a magic number.
DOWNTIME_UNITS_PER_DAY = 1000


@dataclass(frozen=True, slots=True, order=True)
class Moradinium:
    """A signed whole number of Moradinium pieces."""

    pieces: int

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "pieces", whole_number(self.pieces, name="Moradinium.pieces")
        )

    @classmethod
    def zero(cls) -> Moradinium:
        return cls(0)

    def __add__(self, other: object) -> Moradinium:
        if not isinstance(other, Moradinium):
            return NotImplemented
        return Moradinium(self.pieces + other.pieces)

    def __sub__(self, other: object) -> Moradinium:
        if not isinstance(other, Moradinium):
            return NotImplemented
        return Moradinium(self.pieces - other.pieces)

    def __neg__(self) -> Moradinium:
        return Moradinium(-self.pieces)

    @property
    def is_zero(self) -> bool:
        return self.pieces == 0

    @property
    def is_negative(self) -> bool:
        return self.pieces < 0

    def __str__(self) -> str:
        """Diagnostics only."""
        return f"{self.pieces} Moradinium"


@dataclass(frozen=True, slots=True, order=True)
class Downtime:
    """A signed whole number of thousandth-days (OD-08, OD-49)."""

    thousandth_days: int

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "thousandth_days",
            whole_number(self.thousandth_days, name="Downtime.thousandth_days"),
        )

    @classmethod
    def zero(cls) -> Downtime:
        return cls(0)

    @classmethod
    def from_days(cls, days: int) -> Downtime:
        """Whole days only. A fractional day is expressed in thousandths."""
        return cls(whole_number(days, name="days") * DOWNTIME_UNITS_PER_DAY)

    @property
    def whole_days(self) -> int:
        """Days floor-divided, for rules that consume downtime in day multiples.

        Floor division, and negative values floor toward minus infinity as
        Python does — stated because a rule that spends downtime must not be
        handed a rounded-up day it has not got.
        """
        return self.thousandth_days // DOWNTIME_UNITS_PER_DAY

    def __add__(self, other: object) -> Downtime:
        if not isinstance(other, Downtime):
            return NotImplemented
        return Downtime(self.thousandth_days + other.thousandth_days)

    def __sub__(self, other: object) -> Downtime:
        if not isinstance(other, Downtime):
            return NotImplemented
        return Downtime(self.thousandth_days - other.thousandth_days)

    def __neg__(self) -> Downtime:
        return Downtime(-self.thousandth_days)

    @property
    def is_zero(self) -> bool:
        return self.thousandth_days == 0

    @property
    def is_negative(self) -> bool:
        return self.thousandth_days < 0

    def __str__(self) -> str:
        """Diagnostics only. Not the player-facing rendering, which OD-49
        requires to stay exactly as `models/resource.py` produces it today."""
        return f"{self.thousandth_days}/1000 days"
