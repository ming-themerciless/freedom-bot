"""Phase 4 WP-3 — balanced, append-only ledger semantics.

Everything here is about what cannot be built. A transaction that does not
balance, that mixes resources, that carries a float, that moves nothing, or that
edits an accepted entry is not a thing this domain can hold — the refusal is at
construction, so there is no window in which an invalid transaction exists and
is later rejected.

The policy invariants that need the *current* state — a held balance that may
not go negative, a version that may not be stale — belong to the aggregate and
are tested in `tests/test_p4_ledger_service.py`.
"""
from __future__ import annotations

import dataclasses
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from domain.ledger import (
    ACCOUNT_NAME_MAX_LENGTH,
    REASON_MAX_LENGTH,
    AccountKind,
    AccountRef,
    LedgerEntry,
    LedgerError,
    LedgerTransaction,
    ResourceKind,
    kind_of,
    utc,
    zero_of,
)
from domain.money import Money
from domain.resources import Downtime, Moradinium

BOOK = UUID("11111111-1111-4111-8111-111111111111")
OTHER_BOOK = UUID("22222222-2222-4222-8222-222222222222")
NOW = datetime(2026, 8, 29, 12, 0, tzinfo=timezone.utc)


def held(name: str = "wallet", book: UUID = BOOK) -> AccountRef:
    return AccountRef(book, name, AccountKind.HELD)


def counterparty(name: str = "income", book: UUID = BOOK) -> AccountRef:
    return AccountRef(book, name, AccountKind.COUNTERPARTY)


def transaction(**overrides) -> LedgerTransaction:
    fields = {
        "entries": (
            LedgerEntry(held(), Money(500)),
            LedgerEntry(counterparty(), Money(-500)),
        ),
        "reason": "Mission reward",
        "occurred_at": NOW,
        "correlation_id": uuid4(),
    }
    fields.update(overrides)
    return LedgerTransaction(**fields)


# --- resources ----------------------------------------------------------------


@pytest.mark.parametrize(
    "amount, kind",
    [
        (Money(1), ResourceKind.MONEY),
        (Money(-1), ResourceKind.MONEY),
        (Moradinium(3), ResourceKind.MORADINIUM),
        (Downtime(5000), ResourceKind.DOWNTIME),
    ],
)
def test_every_quantity_names_its_resource(amount, kind):
    assert kind_of(amount) is kind


@pytest.mark.parametrize(
    "amount", [1, 1.0, Decimal("1"), "1", True, None, 500.0, object()]
)
def test_a_value_that_is_not_a_quantity_is_refused(amount):
    """Floats, Decimals and bare ints are refused here rather than coerced."""
    with pytest.raises(LedgerError) as refusal:
        kind_of(amount)

    assert refusal.value.code == "unsupported_resource"


def test_the_resource_mapping_covers_every_declared_kind():
    """A fourth resource cannot be half-added: the fold would have no zero."""
    for kind in ResourceKind:
        assert kind_of(zero_of(kind)) is kind


def test_a_money_subclass_is_refused_rather_than_treated_as_money():
    """A subclass redefining addition would be summed by rules nothing can see."""

    class Discounted(Money):
        pass

    with pytest.raises(LedgerError) as refusal:
        kind_of(Discounted(100))

    assert refusal.value.code == "unsupported_resource"


# --- accounts -----------------------------------------------------------------


def test_an_account_names_its_book_its_name_and_its_side():
    account = held("wallet")

    assert account.book_id == BOOK
    assert account.name == "wallet"
    assert account.is_held is True
    assert counterparty().is_held is False


@pytest.mark.parametrize("blank", ["", "   ", "\t"])
def test_an_account_requires_a_name(blank):
    with pytest.raises(LedgerError) as refusal:
        AccountRef(BOOK, blank, AccountKind.HELD)

    assert refusal.value.code == "invalid_account"


def test_an_account_name_is_bounded():
    assert AccountRef(BOOK, "a" * ACCOUNT_NAME_MAX_LENGTH, AccountKind.HELD)

    with pytest.raises(LedgerError) as refusal:
        AccountRef(BOOK, "a" * (ACCOUNT_NAME_MAX_LENGTH + 1), AccountKind.HELD)

    assert refusal.value.code == "invalid_account"


@pytest.mark.parametrize("name", ["wal\nlet", "wal\x00let", "\x7f"])
def test_an_account_name_must_be_printable(name):
    """It is recorded in append-only history and must stay renderable."""
    with pytest.raises(LedgerError) as refusal:
        AccountRef(BOOK, name, AccountKind.HELD)

    assert refusal.value.code == "invalid_account"


@pytest.mark.parametrize("book", ["Brightlantern", str(BOOK), 1, None])
def test_a_book_is_identified_by_a_uuid(book):
    """Display names are mutable and are not identities."""
    with pytest.raises(LedgerError) as refusal:
        AccountRef(book, "wallet", AccountKind.HELD)

    assert refusal.value.code == "invalid_account"


def test_an_account_kind_is_a_value_not_a_string():
    with pytest.raises(LedgerError) as refusal:
        AccountRef(BOOK, "wallet", "held")

    assert refusal.value.code == "invalid_account"


def test_accounts_are_equal_by_value():
    assert held("wallet") == held("wallet")
    assert held("wallet") != held("escrow")
    assert held("wallet") != counterparty("wallet")
    assert held("wallet") != held("wallet", OTHER_BOOK)


# --- entries ------------------------------------------------------------------


def test_an_entry_is_immutable():
    entry = LedgerEntry(held(), Money(500))

    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.amount = Money(600)


def test_an_entry_of_zero_is_refused():
    """Zero moves nothing and records nothing; post no transaction instead."""
    for zero in (Money(0), Moradinium(0), Downtime(0)):
        with pytest.raises(LedgerError) as refusal:
            LedgerEntry(held(), zero)

        assert refusal.value.code == "empty_entry"


def test_an_entry_must_post_to_an_account_reference():
    with pytest.raises(LedgerError) as refusal:
        LedgerEntry("wallet", Money(500))

    assert refusal.value.code == "invalid_entry"


@pytest.mark.parametrize("amount", [500, 500.0, Decimal("5.00"), "500"])
def test_an_entry_amount_must_be_a_typed_quantity(amount):
    with pytest.raises(LedgerError) as refusal:
        LedgerEntry(held(), amount)

    assert refusal.value.code == "unsupported_resource"


def test_negating_an_entry_reverses_it_and_keeps_its_account():
    entry = LedgerEntry(held(), Money(500))

    reversed_entry = entry.negated()

    assert reversed_entry.account == entry.account
    assert reversed_entry.amount == Money(-500)


def test_an_entry_has_no_identity_of_its_own():
    """An entry exists only as part of the transaction that balanced it.

    Giving it an id would invite a caller to reference — and then to try to
    correct — one half of a balanced pair.
    """
    assert "id" not in LedgerEntry.__dataclass_fields__


# --- balance ------------------------------------------------------------------


def test_a_balanced_transaction_is_accepted():
    posted = transaction()

    assert posted.kind is ResourceKind.MONEY
    assert posted.book_id == BOOK
    assert len(posted.entries) == 2


@pytest.mark.parametrize(
    "entries",
    [
        (LedgerEntry(held(), Money(500)), LedgerEntry(counterparty(), Money(-400))),
        (LedgerEntry(held(), Money(500)), LedgerEntry(counterparty(), Money(-600))),
        (
            LedgerEntry(held(), Money(500)),
            LedgerEntry(held("escrow"), Money(-200)),
            LedgerEntry(counterparty(), Money(-200)),
        ),
    ],
)
def test_an_unbalanced_transaction_is_refused(entries):
    """Value would appear or vanish without a counterparty."""
    with pytest.raises(LedgerError) as refusal:
        transaction(entries=entries)

    assert refusal.value.code == "unbalanced_transaction"


def test_a_single_entry_transaction_is_refused():
    """One entry has nowhere for the value to have come from."""
    with pytest.raises(LedgerError) as refusal:
        transaction(entries=(LedgerEntry(held(), Money(500)),))

    assert refusal.value.code == "unbalanced_transaction"


def test_an_empty_transaction_is_refused():
    with pytest.raises(LedgerError) as refusal:
        transaction(entries=())

    assert refusal.value.code == "unbalanced_transaction"


def test_a_transaction_balancing_across_three_accounts_is_accepted():
    posted = transaction(
        entries=(
            LedgerEntry(held("wallet"), Money(-1000)),
            LedgerEntry(counterparty("goods"), Money(700)),
            LedgerEntry(counterparty("tax"), Money(300)),
        )
    )

    assert len(posted.accounts()) == 3


def test_a_transaction_touching_one_account_twice_nets_its_effect():
    """Answering from the first matching entry would understate it."""
    wallet = held("wallet")
    posted = transaction(
        entries=(
            LedgerEntry(wallet, Money(-1000)),
            LedgerEntry(wallet, Money(250)),
            LedgerEntry(counterparty(), Money(750)),
        )
    )

    assert posted.effect_on(wallet) == Money(-750)
    assert posted.accounts() == (wallet, counterparty())


def test_an_untouched_account_has_no_effect():
    assert transaction().effect_on(held("escrow")) == Money(0)


# --- one resource, one book ---------------------------------------------------


def test_a_transaction_mixing_resources_is_refused():
    """5 copper and 5 Moradinium are not ten of anything.

    A rate between them is Council-adjustable game policy (RC-A7, deliberately
    not implemented), so no arithmetic here may imply one.
    """
    with pytest.raises(LedgerError) as refusal:
        transaction(
            entries=(
                LedgerEntry(held(), Money(500)),
                LedgerEntry(counterparty(), Moradinium(-500)),
            )
        )

    assert refusal.value.code == "mixed_resources"


@pytest.mark.parametrize(
    "amount, opposite",
    [
        (Moradinium(3), Moradinium(-3)),
        (Downtime(5000), Downtime(-5000)),
    ],
)
def test_every_resource_can_be_posted(amount, opposite):
    posted = transaction(
        entries=(LedgerEntry(held(), amount), LedgerEntry(counterparty(), opposite))
    )

    assert posted.kind is kind_of(amount)


def test_a_transaction_spanning_two_books_is_refused():
    """One transaction, one aggregate, one optimistic-concurrency precondition.

    A movement between two books needs both books' preconditions checked
    together, which is owned by the package that introduces it (package 5.8 for
    character-to-character trade).
    """
    with pytest.raises(LedgerError) as refusal:
        transaction(
            entries=(
                LedgerEntry(held("wallet", BOOK), Money(500)),
                LedgerEntry(held("wallet", OTHER_BOOK), Money(-500)),
            )
        )

    assert refusal.value.code == "cross_book_transaction"


# --- reason, time and correlation ---------------------------------------------


@pytest.mark.parametrize("blank", ["", "   ", "\n\t"])
def test_a_transaction_states_why_it_happened(blank):
    with pytest.raises(LedgerError) as refusal:
        transaction(reason=blank)

    assert refusal.value.code == "invalid_reason"


def test_a_reason_is_bounded_and_printable():
    assert transaction(reason="r" * REASON_MAX_LENGTH)

    with pytest.raises(LedgerError) as refusal:
        transaction(reason="r" * (REASON_MAX_LENGTH + 1))
    assert refusal.value.code == "invalid_reason"

    with pytest.raises(LedgerError) as refusal:
        transaction(reason="two\nlines")
    assert refusal.value.code == "invalid_reason"


def test_a_naive_timestamp_is_refused():
    """A naive datetime is a different instant on every host that reads it."""
    with pytest.raises(LedgerError) as refusal:
        transaction(occurred_at=datetime(2026, 8, 29, 12, 0))

    assert refusal.value.code == "invalid_timestamp"


@pytest.mark.parametrize("moment", ["2026-08-29", 1756468800, None])
def test_a_timestamp_must_be_a_datetime(moment):
    with pytest.raises(LedgerError) as refusal:
        transaction(occurred_at=moment)

    assert refusal.value.code == "invalid_timestamp"


def test_a_non_utc_aware_timestamp_is_accepted_as_the_instant_it_names():
    """Aware is the requirement; the zone is the caller's business."""
    berlin = timezone(timedelta(hours=2))
    posted = transaction(occurred_at=datetime(2026, 8, 29, 14, 0, tzinfo=berlin))

    assert posted.occurred_at == NOW


def test_utc_normalises_an_aware_moment_and_refuses_a_naive_one():
    berlin = timezone(timedelta(hours=2))

    assert utc(datetime(2026, 8, 29, 14, 0, tzinfo=berlin)) == NOW

    with pytest.raises(LedgerError) as refusal:
        utc(datetime(2026, 8, 29, 12, 0))
    assert refusal.value.code == "invalid_timestamp"


def test_a_transaction_carries_its_command_correlation_id():
    correlation = uuid4()

    assert transaction(correlation_id=correlation).correlation_id == correlation


@pytest.mark.parametrize("correlation", [str(uuid4()), 1, None])
def test_a_correlation_id_must_be_a_uuid(correlation):
    with pytest.raises(LedgerError) as refusal:
        transaction(correlation_id=correlation)

    assert refusal.value.code == "invalid_correlation_id"


# --- append-only and compensation ---------------------------------------------


def test_history_offers_no_update_or_delete():
    """The invariant, asserted against the type rather than described in prose."""
    forbidden = {
        "update",
        "delete",
        "remove",
        "amend",
        "void",
        "set_amount",
        "edit",
        "reverse_in_place",
    }

    assert not forbidden & set(dir(LedgerTransaction))
    assert not forbidden & set(dir(LedgerEntry))


def test_an_accepted_transaction_cannot_be_mutated():
    posted = transaction()

    with pytest.raises(dataclasses.FrozenInstanceError):
        posted.reason = "Something else"
    with pytest.raises(dataclasses.FrozenInstanceError):
        posted.entries = ()


def test_the_entries_tuple_cannot_be_mutated_by_whoever_holds_it():
    entries = [
        LedgerEntry(held(), Money(500)),
        LedgerEntry(counterparty(), Money(-500)),
    ]
    posted = transaction(entries=entries)

    entries.append(LedgerEntry(held(), Money(1)))

    assert len(posted.entries) == 2
    with pytest.raises(TypeError):
        posted.entries[0] = LedgerEntry(held(), Money(1))


def test_a_compensation_reverses_every_entry_and_names_the_original():
    original = transaction()
    later = NOW + timedelta(days=1)
    correlation = uuid4()

    correction = original.compensate(
        reason="Reward applied twice", occurred_at=later, correlation_id=correlation
    )

    assert correction.compensates == original.id
    assert correction.id != original.id
    assert correction.is_compensation is True
    assert correction.occurred_at == later
    assert correction.correlation_id == correlation
    assert correction.effect_on(held()) == Money(-500)
    assert correction.effect_on(counterparty()) == Money(500)


def test_a_compensation_leaves_the_original_exactly_as_accepted():
    original = transaction()
    before = dataclasses.replace(original)

    original.compensate(reason="Undo", occurred_at=NOW, correlation_id=uuid4())

    assert original == before
    assert original.compensates is None
    assert original.is_compensation is False


def test_a_compensation_is_itself_balanced():
    original = transaction(
        entries=(
            LedgerEntry(held("wallet"), Money(-1000)),
            LedgerEntry(counterparty("goods"), Money(700)),
            LedgerEntry(counterparty("tax"), Money(300)),
        )
    )

    correction = original.compensate(
        reason="Purchase reversed", occurred_at=NOW, correlation_id=uuid4()
    )

    assert len(correction.entries) == 3


def test_a_compensation_of_a_compensation_is_permitted():
    """Somebody may correct a correction; refusing it would leave editing as
    the only way out."""
    original = transaction()
    first = original.compensate(reason="Undo", occurred_at=NOW, correlation_id=uuid4())

    second = first.compensate(
        reason="The undo was itself wrong", occurred_at=NOW, correlation_id=uuid4()
    )

    assert second.compensates == first.id
    assert second.effect_on(held()) == Money(500)


def test_a_compensation_reason_is_validated_like_any_other():
    with pytest.raises(LedgerError) as refusal:
        transaction().compensate(
            reason="  ", occurred_at=NOW, correlation_id=uuid4()
        )

    assert refusal.value.code == "invalid_reason"


def test_a_transaction_cannot_compensate_itself():
    identity = uuid4()

    with pytest.raises(LedgerError) as refusal:
        transaction(id=identity, compensates=identity)

    assert refusal.value.code == "invalid_compensation"


@pytest.mark.parametrize("compensates", [str(uuid4()), 1, "the previous one"])
def test_a_compensation_names_its_original_by_id(compensates):
    with pytest.raises(LedgerError) as refusal:
        transaction(compensates=compensates)

    assert refusal.value.code == "invalid_compensation"


def test_a_transaction_is_identified_by_a_uuid():
    with pytest.raises(LedgerError) as refusal:
        transaction(id="tx-1")

    assert refusal.value.code == "invalid_transaction_id"


def test_two_transactions_built_the_same_way_have_different_identities():
    assert transaction().id != transaction().id
