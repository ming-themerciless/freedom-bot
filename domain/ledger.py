"""Balanced, append-only movement of a game resource.

Every change to a tracked balance is a **transaction**: two or more signed
entries that sum to zero in one resource. Nothing here adds to a balance without
taking the same amount from somewhere, so "where did this come from" always has
an answer, and a total that has drifted is a defect that can be located rather
than a number nobody can reconstruct.

**Signed integers, one unit, one resource.** An entry's amount is a `Money`,
`Moradinium` or `Downtime` value object — a whole count of a named smallest unit
(`domain/quantities.py`). A transaction holds exactly one of those types.
Mixing them is refused rather than coerced: 5 copper and 5 Moradinium are not
ten of anything, and a rate between them is a Council-adjustable game policy
that no arithmetic here may imply (RC-A7 is deliberately not implemented).

**The invariants live here, at the transaction boundary, not in the numbers.**
`Money(-500)` is a perfectly good value — it is the debit half of a transfer, and
a numeric type that refused it would make a transfer inexpressible. What may not
happen is a *transaction* that does not balance, or one that drives a held
balance below zero. The first is enforced at construction below; the second needs
the current balance and so belongs to the aggregate — see
`application/ledger.py`.

**History is append-only, and there is nothing here to update or delete it.**
A correction is a `compensate()` transaction: a new, later transaction that
reverses an earlier one and names it. The original stays exactly as it was
accepted, which is the product invariant (`.agents/AGENTS.md`: "Corrections use
explicit compensating actions rather than erased history") and the reason an
audit trail can be believed at all.

**Time is injected.** `occurred_at` is supplied by the caller, never read from a
clock here; a domain that reads the clock cannot be tested at a boundary.

**What this deliberately does not decide.** It does not enumerate the platform's
accounts. An account is an opaque `(book, name)` identity supplied by the caller,
with one structural distinction — held versus counterparty — that double-entry
needs in order to express "insufficient resources" at all. Which accounts a
character has, and what a mission reward or a sale posts to, are game-economy
decisions owned by the Phase 5 packages that migrate those fields.

This module imports nothing outside the standard library and `domain`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from domain.money import Money
from domain.resources import Downtime, Moradinium

#: The longest an account name may be. Bounded because it is an identity that
#: gets rendered and recorded, not free text.
ACCOUNT_NAME_MAX_LENGTH = 60

#: The longest a stated reason may be, for the same reason.
REASON_MAX_LENGTH = 200


class LedgerError(ValueError):
    """A ledger transaction cannot be constructed as stated. Nothing happened.

    A `ValueError`, and raised at construction: an unbalanced transaction is not
    a thing that exists and then fails to post. `code` is a stable name a caller
    branches on and an adapter translates.
    """

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class ResourceKind(Enum):
    """The resources this ledger can move, each with one value type.

    A closed set, because a transaction's resource is written into a receipt and
    an audit payload and an operator filters on it. It is not a chart of
    accounts and implies no conversion between its members.
    """

    MONEY = "money"
    MORADINIUM = "moradinium"
    DOWNTIME = "downtime"


#: The one mapping between a resource and the type that counts it. Both
#: directions are derived from it, so a fourth resource cannot be half-added.
_TYPES: dict[ResourceKind, type] = {
    ResourceKind.MONEY: Money,
    ResourceKind.MORADINIUM: Moradinium,
    ResourceKind.DOWNTIME: Downtime,
}
_KINDS: dict[type, ResourceKind] = {value: key for key, value in _TYPES.items()}

#: Every quantity type a ledger entry may carry.
Quantity = Money | Moradinium | Downtime


def kind_of(amount: object) -> ResourceKind:
    """The resource `amount` counts, or refuse.

    `type(...)` rather than `isinstance`, deliberately: a subclass of `Money`
    that redefined addition would be accepted by `isinstance` and would then be
    summed by rules this module cannot see. A ledger is the wrong place to be
    generous about types.
    """
    kind = _KINDS.get(type(amount))
    if kind is None:
        raise LedgerError(
            "unsupported_resource",
            f"A ledger entry carries Money, Moradinium or Downtime, not "
            f"{type(amount).__name__}. Whole counts of a named smallest unit "
            "only — a float, a Decimal or a bare int is refused here rather "
            "than coerced.",
        )
    return kind


def zero_of(kind: ResourceKind) -> Quantity:
    """The additive identity for `kind`, so a fold has somewhere to start."""
    return _TYPES[kind].zero()


class AccountKind(Enum):
    """Whether an account holds value or is where value crosses the boundary.

    This is double-entry's own distinction, not a Freedom Blades one:

    - **`HELD`** — a balance the platform tracks on someone's behalf. It may
      never go negative, which is what makes "insufficient resources" a
      refusal rather than a debt nobody agreed to. It is the same rule
      `Resource.deduct` enforces in the live bot today
      (`models/resource.py:66`).
    - **`COUNTERPARTY`** — the other side of a movement into or out of the
      tracked set: what a mission paid out, what a purchase consumed, what a
      mine produced. It is unbounded by construction, because bounding it would
      mean the platform claimed to know the world's balance.

    Which named accounts of each kind a character has is a Phase 5 decision. The
    ledger only needs to know which side of the boundary an account sits on.
    """

    HELD = "held"
    COUNTERPARTY = "counterparty"


#: Not `order=True`: `AccountKind` is an enum and enums are not ordered, so a
#: generated comparison would raise the first time anything sorted a list of
#: accounts. Order comes from the caller, where it means something.
@dataclass(frozen=True, slots=True)
class AccountRef:
    """A stable account identity: which book, which account, which side.

    `book_id` is the aggregate. Every account named by one transaction belongs
    to one book, so a transaction has exactly one optimistic-concurrency
    precondition — see `LedgerTransaction`.
    """

    book_id: UUID
    name: str
    kind: AccountKind

    def __post_init__(self) -> None:
        if not isinstance(self.book_id, UUID):
            raise LedgerError(
                "invalid_account",
                "A ledger book is identified by a stable UUID, not by "
                f"{type(self.book_id).__name__}.",
            )
        if not isinstance(self.kind, AccountKind):
            raise LedgerError(
                "invalid_account",
                f"An account names its kind as an AccountKind, not "
                f"{type(self.kind).__name__}.",
            )
        name = self.name if isinstance(self.name, str) else ""
        if not name.strip():
            raise LedgerError("invalid_account", "An account requires a name.")
        if len(name) > ACCOUNT_NAME_MAX_LENGTH:
            raise LedgerError(
                "invalid_account",
                f"An account name is at most {ACCOUNT_NAME_MAX_LENGTH} "
                f"characters; this one is {len(name)}.",
            )
        if any(character < " " or character == "\x7f" for character in name):
            raise LedgerError(
                "invalid_account",
                "An account name must be printable text: it is recorded in "
                "append-only history and a control character would corrupt "
                "every later rendering of that row.",
            )

    @property
    def is_held(self) -> bool:
        return self.kind is AccountKind.HELD

    def __str__(self) -> str:
        """Diagnostics only. Not a player-facing rendering."""
        return f"{self.name}@{self.book_id}"


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    """One signed movement on one account. Immutable once accepted.

    There is no `id` here. An entry is not addressable on its own: it exists only
    as part of the transaction that balanced it, and giving it an identity would
    invite a caller to reference — and eventually to try to correct — half of a
    balanced pair.
    """

    account: AccountRef
    amount: Quantity

    def __post_init__(self) -> None:
        if not isinstance(self.account, AccountRef):
            raise LedgerError(
                "invalid_entry",
                f"A ledger entry posts to an AccountRef, not "
                f"{type(self.account).__name__}.",
            )
        # Raises `LedgerError("unsupported_resource")` for anything else,
        # including the `float` and `Decimal` that `domain/quantities.py`
        # refuses one layer down.
        kind_of(self.amount)
        if self.amount.is_zero:
            raise LedgerError(
                "empty_entry",
                "A ledger entry of zero moves nothing and records nothing. If "
                "the intent is that nothing happened, post no transaction.",
            )

    @property
    def kind(self) -> ResourceKind:
        return kind_of(self.amount)

    def negated(self) -> LedgerEntry:
        """The same movement, reversed — the building block of a correction."""
        return LedgerEntry(account=self.account, amount=-self.amount)


@dataclass(frozen=True, slots=True)
class LedgerTransaction:
    """Two or more entries that balance to zero in one resource.

    Constructing one is what enforces the invariants; there is no separate
    `validate()` a caller could forget to call, and no way to hold an
    unbalanced transaction at all.
    """

    entries: tuple[LedgerEntry, ...]
    reason: str
    occurred_at: datetime
    correlation_id: UUID
    #: The transaction this one reverses, when it is a correction. Set only by
    #: `compensate()`; history is corrected forward, never in place.
    compensates: UUID | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        entries = tuple(self.entries)
        object.__setattr__(self, "entries", entries)

        if len(entries) < 2:
            raise LedgerError(
                "unbalanced_transaction",
                "A ledger transaction is at least two entries: value moves "
                "between accounts, and a single entry has nowhere for it to "
                "have come from.",
            )
        for entry in entries:
            if not isinstance(entry, LedgerEntry):
                raise LedgerError(
                    "invalid_entry",
                    f"A ledger transaction holds LedgerEntry values, not "
                    f"{type(entry).__name__}.",
                )

        kinds = {entry.kind for entry in entries}
        if len(kinds) != 1:
            raise LedgerError(
                "mixed_resources",
                "A ledger transaction moves one resource. This one mixes "
                f"{sorted(kind.value for kind in kinds)}, and no rate between "
                "them exists in the platform to balance it with.",
            )

        books = {entry.account.book_id for entry in entries}
        if len(books) != 1:
            raise LedgerError(
                "cross_book_transaction",
                "Every account in one transaction belongs to one book, so the "
                "transaction has one optimistic-concurrency precondition. A "
                "movement between two books needs both books' preconditions "
                "checked together and is owned by the package that introduces "
                "it (character-to-character trade is package 5.8).",
            )

        kind = kinds.pop()
        total = zero_of(kind)
        for entry in entries:
            total = total + entry.amount
        if not total.is_zero:
            raise LedgerError(
                "unbalanced_transaction",
                f"A ledger transaction must balance to zero. This one nets "
                f"{total}, so value would appear or vanish without a "
                "counterparty.",
            )

        reason = self.reason if isinstance(self.reason, str) else ""
        if not reason.strip():
            raise LedgerError(
                "invalid_reason",
                "A ledger transaction states why it happened. An append-only "
                "history nobody can read back is not an audit trail.",
            )
        if len(reason) > REASON_MAX_LENGTH:
            raise LedgerError(
                "invalid_reason",
                f"A reason is at most {REASON_MAX_LENGTH} characters; this one "
                f"is {len(reason)}.",
            )
        if any(character < " " or character == "\x7f" for character in reason):
            raise LedgerError(
                "invalid_reason",
                "A reason must be printable text: it is recorded verbatim in "
                "append-only history.",
            )

        if not isinstance(self.occurred_at, datetime):
            raise LedgerError(
                "invalid_timestamp",
                "A ledger transaction is stamped with the time it happened, "
                f"supplied by the caller's clock, not {type(self.occurred_at).__name__}.",
            )
        if self.occurred_at.tzinfo is None or (
            self.occurred_at.utcoffset() is None
        ):
            raise LedgerError(
                "invalid_timestamp",
                "A ledger timestamp is timezone-aware UTC. A naive datetime "
                "means a different instant on every host that reads it.",
            )
        if not isinstance(self.correlation_id, UUID):
            raise LedgerError(
                "invalid_correlation_id",
                "A ledger transaction carries the correlation id of the command "
                "that produced it, so the entry, the receipt and the audit row "
                "can be tied together.",
            )
        if self.compensates is not None and not isinstance(self.compensates, UUID):
            raise LedgerError(
                "invalid_compensation",
                "A compensating transaction names the transaction it reverses "
                "by id.",
            )
        if self.compensates == self.id:
            raise LedgerError(
                "invalid_compensation",
                "A transaction cannot compensate itself.",
            )
        if not isinstance(self.id, UUID):
            raise LedgerError(
                "invalid_transaction_id",
                "A ledger transaction is identified by a stable UUID.",
            )

    # -- inspection -------------------------------------------------------- #

    @property
    def kind(self) -> ResourceKind:
        """The one resource this transaction moves."""
        return self.entries[0].kind

    @property
    def book_id(self) -> UUID:
        """The aggregate this transaction is posted to."""
        return self.entries[0].account.book_id

    @property
    def is_compensation(self) -> bool:
        return self.compensates is not None

    def effect_on(self, account: AccountRef) -> Quantity:
        """The net movement this transaction makes on one account.

        Summed rather than taken from the first matching entry: one transaction
        may legitimately touch one account more than once, and answering from
        the first would understate it.
        """
        total = zero_of(self.kind)
        for entry in self.entries:
            if entry.account == account:
                total = total + entry.amount
        return total

    def accounts(self) -> tuple[AccountRef, ...]:
        """Every account this transaction touches, each once, in a stable order."""
        seen: list[AccountRef] = []
        for entry in self.entries:
            if entry.account not in seen:
                seen.append(entry.account)
        return tuple(seen)

    # -- correction -------------------------------------------------------- #

    def compensate(
        self,
        *,
        reason: str,
        occurred_at: datetime,
        correlation_id: UUID,
    ) -> LedgerTransaction:
        """A new transaction that reverses this one and names it.

        This is the *only* correction there is. There is no `amend`, no
        `void` and no `delete`: the original transaction remains exactly as it
        was accepted, and the ledger reads as what happened followed by what was
        done about it.

        A compensation of a compensation is permitted and is not a special case —
        somebody may correct a correction, and refusing that would leave the only
        way out being to edit history.
        """
        return LedgerTransaction(
            entries=tuple(entry.negated() for entry in self.entries),
            reason=reason,
            occurred_at=occurred_at,
            correlation_id=correlation_id,
            compensates=self.id,
        )


def utc(moment: datetime) -> datetime:
    """Normalise an aware datetime to UTC, refusing a naive one.

    A convenience for callers holding a clock in another zone. It refuses rather
    than assuming UTC, because assuming is how a naive local timestamp becomes a
    wrong instant that nothing later can detect.
    """
    if not isinstance(moment, datetime) or moment.tzinfo is None:
        raise LedgerError(
            "invalid_timestamp",
            "A ledger timestamp must be timezone-aware. A naive datetime means "
            "a different instant on every host that reads it.",
        )
    return moment.astimezone(timezone.utc)


__all__ = [
    "ACCOUNT_NAME_MAX_LENGTH",
    "REASON_MAX_LENGTH",
    "AccountKind",
    "AccountRef",
    "LedgerEntry",
    "LedgerError",
    "LedgerTransaction",
    "Quantity",
    "ResourceKind",
    "kind_of",
    "utc",
    "zero_of",
]
