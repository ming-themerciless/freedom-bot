"""Phase 4 — money and resource value objects.

Covers the Phase 4 acceptance criterion *"money uses integer copper"* and the
handover's *"value construction, conversion, arithmetic and refusal tests"* and
*"table-driven boundary tests proving integer-copper and no-float invariants"*.

The refusal tests are the load-bearing half. A value object whose constructor
accepts a `float` has not moved the problem anywhere — it has renamed it.
"""
from __future__ import annotations

import pytest

from domain.money import (
    COPPER_PER_GOLD,
    COPPER_PER_PLATINUM,
    COPPER_PER_SILVER,
    Money,
    sum_money,
)
from domain.quantities import QuantityError, whole_number
from domain.resources import DOWNTIME_UNITS_PER_DAY, Downtime, Moradinium


# --------------------------------------------------------------------------- #
# The no-float invariant, as a table over every constructor
# --------------------------------------------------------------------------- #

#: Everything a caller might plausibly pass that is not a whole number. `True`
#: is first because `isinstance(True, int)` is the trap this guards.
REJECTED_VALUES = [
    pytest.param(True, id="bool-true"),
    pytest.param(False, id="bool-false"),
    pytest.param(5.0, id="float-integral"),
    pytest.param(0.1, id="float-fractional"),
    pytest.param(float("nan"), id="float-nan"),
    pytest.param(float("inf"), id="float-inf"),
    pytest.param("5", id="str-numeric"),
    pytest.param("", id="str-empty"),
    pytest.param(None, id="none"),
    pytest.param([1], id="list"),
]


@pytest.mark.parametrize("value", REJECTED_VALUES)
def test_money_refuses_anything_but_a_whole_number(value):
    with pytest.raises(QuantityError):
        Money(value)


@pytest.mark.parametrize("value", REJECTED_VALUES)
@pytest.mark.parametrize("denomination", ["platinum", "gold", "silver", "copper"])
def test_from_denominations_refuses_anything_but_whole_numbers(denomination, value):
    with pytest.raises(QuantityError):
        Money.from_denominations(**{denomination: value})


@pytest.mark.parametrize("value", REJECTED_VALUES)
def test_moradinium_refuses_anything_but_a_whole_number(value):
    with pytest.raises(QuantityError):
        Moradinium(value)


@pytest.mark.parametrize("value", REJECTED_VALUES)
def test_downtime_refuses_anything_but_a_whole_number(value):
    with pytest.raises(QuantityError):
        Downtime(value)
    with pytest.raises(QuantityError):
        Downtime.from_days(value)


def test_the_decimal_type_is_refused_as_well():
    """Exact, but still not this type's job.

    Accepting `Decimal` would put a conversion policy in the domain for
    whichever call site happened to pass one. The adapter converts explicitly.
    """
    from decimal import Decimal

    with pytest.raises(QuantityError):
        Money(Decimal("5"))


def test_whole_number_names_the_field_it_refused():
    with pytest.raises(QuantityError, match="Money.copper"):
        Money(1.5)
    with pytest.raises(QuantityError, match="platinum"):
        Money.from_denominations(platinum=1.5)


def test_whole_number_passes_an_int_through_unchanged():
    assert whole_number(-7, name="x") == -7


# --------------------------------------------------------------------------- #
# Conversion — the platform's one rate table
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("denominations", "copper"),
    [
        ({}, 0),
        ({"copper": 1}, 1),
        ({"silver": 1}, 10),
        ({"gold": 1}, 100),
        ({"platinum": 1}, 1000),
        ({"platinum": 2, "gold": 3, "silver": 4, "copper": 5}, 2345),
        ({"silver": 10}, 100),
        ({"copper": -5}, -5),
        ({"gold": -1, "copper": 1}, -99),
    ],
)
def test_denomination_rates(denominations, copper):
    assert Money.from_denominations(**denominations) == Money(copper)


def test_the_rate_constants_match_the_platforms_existing_table():
    """`models/exchange.py` has always used pp=1000, gp=100, sp=10, cp=1.

    Pinned against the legacy module so the new domain cannot drift from the
    conversion the live bot performs.
    """
    from models.exchange import RATES_IN_COPPER

    assert RATES_IN_COPPER["pp"] == COPPER_PER_PLATINUM == 1000
    assert RATES_IN_COPPER["gp"] == COPPER_PER_GOLD == 100
    assert RATES_IN_COPPER["sp"] == COPPER_PER_SILVER == 10
    assert RATES_IN_COPPER["cp"] == 1


def test_equal_value_is_equal_regardless_of_how_it_was_built():
    """OD-50's other half: as a *value*, ten silver and one gold are equal.

    The counters differ and the rendering differs — that is
    `tests/test_p4_characterization.py` — but the value does not, which is why
    the domain holds copper and the adapter holds the counters.
    """
    assert Money.from_denominations(silver=10) == Money.from_denominations(gold=1)
    assert Money.from_denominations(silver=10) == Money(100)


# --------------------------------------------------------------------------- #
# Arithmetic, and the refusal of mixed types
# --------------------------------------------------------------------------- #


def test_money_arithmetic_is_exact_and_signed():
    assert Money(100) + Money(5) == Money(105)
    assert Money(100) - Money(150) == Money(-50)
    assert -Money(7) == Money(-7)
    assert Money(7) * 3 == Money(21)
    assert 3 * Money(7) == Money(21)


def test_money_orders_by_value():
    assert Money(1) < Money(2)
    assert max(Money(-5), Money(0), Money(3)) == Money(3)


@pytest.mark.parametrize(
    ("left", "right"),
    [
        (Money(1), Moradinium(1)),
        (Money(1), Downtime(1)),
        (Moradinium(1), Downtime(1)),
        (Moradinium(1), Money(1)),
        (Downtime(1), Money(1)),
    ],
)
def test_mixing_resource_types_is_refused(left, right):
    """One copper is not one Moradinium is not one thousandth of a day."""
    with pytest.raises(TypeError):
        left + right
    with pytest.raises(TypeError):
        left - right


@pytest.mark.parametrize("scalar", [1, 0, -1])
def test_money_multiplies_only_by_a_whole_count(scalar):
    assert Money(5) * scalar == Money(5 * scalar)


@pytest.mark.parametrize("scalar", [1.5, 2.0, True, "2"])
def test_money_refuses_fractional_or_untyped_scaling(scalar):
    """A percentage of a price needs a stated rounding policy, which belongs
    with the rule, not with an operator here."""
    with pytest.raises(TypeError):
        Money(100) * scalar


def test_money_and_a_bare_int_do_not_add():
    with pytest.raises(TypeError):
        Money(1) + 1


def test_sum_money_totals_and_names_a_bad_element():
    assert sum_money([Money(1), Money(2), Money(-3)]) == Money.zero()
    assert sum_money([]) == Money.zero()

    with pytest.raises(QuantityError, match="position 1"):
        sum_money([Money(1), 2])


# --------------------------------------------------------------------------- #
# Immutability
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("value", "field"),
    [
        (Money(1), "copper"),
        (Moradinium(1), "pieces"),
        (Downtime(1), "thousandth_days"),
    ],
)
def test_quantities_are_immutable(value, field):
    with pytest.raises((AttributeError, TypeError)):
        setattr(value, field, 999)


# --------------------------------------------------------------------------- #
# Downtime's unit — OD-08 and OD-49
# --------------------------------------------------------------------------- #


def test_the_downtime_unit_is_the_thousandth_day():
    assert DOWNTIME_UNITS_PER_DAY == 1000
    assert Downtime.from_days(1) == Downtime(1000)
    assert Downtime.from_days(5) == Downtime(5000)


@pytest.mark.parametrize(
    ("thousandths", "whole_days"),
    [(0, 0), (999, 0), (1000, 1), (1500, 1), (5000, 5), (-1, -1), (-1000, -1)],
)
def test_whole_days_floors_including_below_zero(thousandths, whole_days):
    """Floor division, stated explicitly: a rule spending downtime must never be
    handed a rounded-up day the character has not got."""
    assert Downtime(thousandths).whole_days == whole_days


def test_downtime_arithmetic_stays_in_thousandths():
    assert Downtime.from_days(5) - Downtime(1) == Downtime(4999)
    assert Downtime(1) + Downtime(2) == Downtime(3)


def test_a_fractional_day_must_be_expressed_in_thousandths():
    """`from_days(0.5)` is refused; `Downtime(500)` is how you say half a day."""
    with pytest.raises(QuantityError):
        Downtime.from_days(0.5)

    assert Downtime(500).whole_days == 0


# --------------------------------------------------------------------------- #
# Zero and sign helpers
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "zero", [Money.zero(), Moradinium.zero(), Downtime.zero()]
)
def test_zero_constructors(zero):
    assert zero.is_zero
    assert not zero.is_negative


@pytest.mark.parametrize(
    ("negative", "positive"),
    [
        (Money(-1), Money(1)),
        (Moradinium(-1), Moradinium(1)),
        (Downtime(-1), Downtime(1)),
    ],
)
def test_sign_inspection(negative, positive):
    assert negative.is_negative
    assert not positive.is_negative
    assert not negative.is_zero


def test_negative_values_are_representable_because_a_ledger_entry_is_signed():
    """Deliberate: the no-negative-balance rule belongs to whatever holds a
    balance, not to the number. Enforcing it here would make the debit half of a
    transfer inexpressible."""
    debit, credit = Money(-500), Money(500)

    assert debit + credit == Money.zero()
