"""The one place the platform decides what counts as a valid quantity.

Every game quantity in this package — money, Moradinium, downtime — is an
**integer count of a named smallest unit**. This module holds the rule that
makes that true, so there is one definition rather than one per type.

**Why `bool` is refused.** `isinstance(True, int)` is `True` in Python, so
`Money(True)` would silently mean one copper piece. A flag arriving where an
amount belongs is a programming error, and reading it as `1` hides it.

**Why `float` is refused even when it looks whole.** `.agents/AGENTS.md`: money
is never calculated or persisted in binary floating point. `Money(5.0)` would
work and `Money(0.1 + 0.2)` would not, which is the worst kind of rule — one
that holds for the values a developer tries by hand. The refusal is
unconditional so there is no boundary to get wrong. Converting an external
decimal value into a unit count is an **adapter's** job, done explicitly, where
the rounding policy is visible and testable.

**Why `Decimal` is refused too.** It is exact, so the argument against `float`
does not apply — but accepting it would put a conversion policy here, silently,
for whichever call site passed one. The adapter converts; the domain counts.

This module imports nothing outside the standard library.
"""
from __future__ import annotations


class QuantityError(ValueError):
    """A quantity cannot be constructed from this value.

    A `ValueError`, because callers that already treat bad input as a value
    problem keep working. The message names the field and what was offered so a
    failure is diagnosable without a debugger, and never carries anything but
    the type name and the amount.
    """


def whole_number(value: object, *, name: str) -> int:
    """Return `value` as an `int`, or refuse.

    Accepts `int` and nothing else. `bool` is rejected explicitly because it is
    a subclass of `int`.
    """
    if isinstance(value, bool):
        raise QuantityError(
            f"{name} must be a whole number, not a boolean. "
            "A flag is not an amount."
        )
    if not isinstance(value, int):
        raise QuantityError(
            f"{name} must be a whole number of its smallest unit, not "
            f"{type(value).__name__}. Convert at the adapter boundary, where "
            "the rounding policy is explicit."
        )
    return value
