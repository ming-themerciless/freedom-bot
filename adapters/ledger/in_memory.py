"""An in-memory ledger, and the unit of work that keeps it honest.

**This is a reference implementation, not a production authority.** OD-48 rules
that Phase 4 adds no physical ledger table and no migration: the wallet fields
belong to package 5.2, downtime to 5.5 and living costs to 5.3, and a Phase 4
table would pre-empt that ownership. So the ledger this repository has today
holds its transactions in process memory, and every claim about the ledger's
*durability* is owed by the package that gives it a table.

**It does not claim cross-store atomicity, because it cannot provide it.** Two
stores — process memory and PostgreSQL — cannot be committed atomically without
a protocol neither of them speaks. What this adapter provides instead is stated
exactly, and is a property it can actually enforce:

> One writer at a time. A unit of work's postings are validated, its durable
> half is committed, and only then are the postings made visible — all three
> inside one critical section on the book. A durable commit that fails leaves
> the book exactly as it was, because nothing was ever added to it.

That is the whole of the change made for review finding **P4-R1**. The previous
shape published first, released the lock, committed the durable half, and on
failure deleted the last *N* transactions. A concurrent caller appending in that
window was visible before any commit and could be deleted by another caller's
rollback. There is no `retract` here now, positional or otherwise: **rollback of
a published posting is not a thing this class can be asked to do**, which is a
stronger guarantee than a correct implementation of it would have been.

What the ordering above buys, property by property:

1. **No uncommitted posting is externally visible.** `_transactions` is an
   immutable tuple rebound in one assignment, and it is rebound only after the
   durable commit has returned. A reader — another unit of work opening, a
   balance query, a test — sees committed history or the history before it, and
   never a posting that is still deciding.

2. **A failed durable commit leaves none of that caller's effects.** The append
   never happens. The receipt and audit row are rolled back by the inner unit of
   work that owns them.

3. **A concurrent caller that succeeded stays intact.** Writers serialize on the
   book, so the only transactions in the tuple are ones whose durable half
   already committed. Nothing removes them.

4. **Versions and balances describe surviving committed history**, because they
   are derived from that tuple and nothing else. There is no stored total to
   drift.

5. **A rollback never removes another unit of work's transaction**, because no
   rollback removes anything at all.

6. **Receipt, audit and effect cannot disagree**, in the one direction this
   adapter can enforce: no posting exists without its receipt. See the honest
   limit below for the other direction.

7. **Stale-version and duplicate-identity outcomes stay typed.** The version
   precondition is decided in the same critical section as the append, and it
   raises `ConcurrencyConflictError`; a repeated transaction identity raises
   `UniquenessConflict("ledger_transaction.id")`, the rule name
   `adapters/database/translation.py` uses for a primary-key violation on a real
   table.

**The honest limit, stated rather than discovered at review.** A process that
died between the durable commit returning and the tuple being rebound would
leave a receipt with no posting. For *this* adapter that window is unobservable:
the book is process memory and dies with the process, so the surviving state is
a database receipt and no ledger at all. It becomes real the moment the ledger
has a table — and at that point both halves belong in **one** database
transaction, which is exactly what OD-48 defers to package 5.0 or 5.2. Nothing
in `application/ledger.py` assumes an in-memory ledger, so that is a change of
adapter rather than of use case.

**Readers do not take the writer's lock**, deliberately. A reader that blocked
behind an in-flight commit could not be used to assert that an in-flight posting
is invisible — the assertion would hang instead of failing — and a test that can
only hang is not a regression test. Reading one immutable tuple needs no lock.

Append-only is structural: `LedgerBook` exposes no update, no delete and no
retraction, and the tuple it hands out cannot be mutated by whoever receives it.
"""
from __future__ import annotations

import threading
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from uuid import UUID

from application.errors import ConcurrencyConflictError, UniquenessConflict
from application.repositories import AuditRepository, IdempotencyRepository
from domain.ledger import AccountRef, LedgerTransaction, Quantity, ResourceKind, zero_of

#: One unit of work's postings, each with the book version it was decided
#: against. The pair is what `committing` validates and then applies.
Pending = Sequence[tuple[LedgerTransaction, int]]


class LedgerBook:
    """The committed ledger: every accepted transaction, in acceptance order.

    Shared by every unit of work built over it, exactly as one database is
    shared by every session — which is what lets two racing threads in the
    concurrency tests contend for one authority instead of each winning its own.
    """

    def __init__(self) -> None:
        #: Immutable, and rebound rather than mutated. A reader holds whichever
        #: tuple was current when it looked, which is a consistent history; a
        #: list being appended to is not.
        self._transactions: tuple[LedgerTransaction, ...] = ()
        #: Held by one committing unit of work at a time, across its durable
        #: commit. Readers never take it — see the module docstring.
        self._writer = threading.Lock()

    # -- the committed state ------------------------------------------------ #

    def snapshot(self) -> tuple[LedgerTransaction, ...]:
        """Committed history as of now. Never blocks, never sees pending work."""
        return self._transactions

    @contextmanager
    def committing(self, pending: Pending) -> Iterator[None]:
        """Hold the book across one unit of work's durable commit.

        The body of the `with` statement is the durable half. On the way in,
        every pending posting is checked against committed history under the
        writer lock; on the way out — only if the body returned — they are
        appended, still under the same lock. A body that raises appends nothing
        and leaves the book byte-identical to what it was.

        Validation refuses the whole batch rather than the offending element: a
        commit is all-or-nothing, and applying the first of two before
        discovering that the second collides would leave exactly the
        half-applied state a unit of work exists to prevent.
        """
        with self._writer:
            self._require_acceptable(pending)
            yield
            if pending:
                self._transactions = self._transactions + tuple(
                    transaction for transaction, _ in pending
                )

    def _require_acceptable(self, pending: Pending) -> None:
        """Every precondition, decided where the append will happen.

        A version compared when a transaction *opened* is a reading, and two
        callers who both read version 3 would both pass such a comparison. This
        one is made inside the critical section that appends, which is what a
        conditional `UPDATE … WHERE version = :expected` does in one statement
        against a real table (`SqlAlchemyCharacterRepository.save`).

        Called only with `self._writer` held.
        """
        committed = self._transactions
        identities = {transaction.id for transaction in committed}
        versions: dict[UUID, int] = {}
        for transaction, expected_version in pending:
            if transaction.id in identities:
                raise UniquenessConflict("ledger_transaction.id")
            book_id = transaction.book_id
            current = versions.get(book_id)
            if current is None:
                current = _version_of(committed, book_id)
            if expected_version != current:
                raise ConcurrencyConflictError(
                    f"Ledger book {book_id} is at version {current}; this "
                    f"command was decided against version {expected_version}. "
                    "Nothing was posted."
                )
            versions[book_id] = current + 1
            identities.add(transaction.id)

    # -- inspection, for tests and diagnostics ------------------------------ #
    #
    # Deliberately on the concrete book and **not** on `LedgerRepository`. The
    # protocol carries only what `LedgerCommandService` calls; a reader that
    # exists for the tests belongs where the tests can reach it without becoming
    # part of the boundary every future adapter must implement.

    def version_of(self, book_id: UUID) -> int:
        return _version_of(self.snapshot(), book_id)

    def transactions_for(self, book_id: UUID) -> tuple[LedgerTransaction, ...]:
        return tuple(
            transaction
            for transaction in self.snapshot()
            if transaction.book_id == book_id
        )

    def balance(self, account: AccountRef, kind: ResourceKind) -> Quantity:
        return _fold(self.snapshot(), account, kind)


def _version_of(
    transactions: tuple[LedgerTransaction, ...], book_id: UUID
) -> int:
    """How many transactions a book has accepted: its optimistic version."""
    return sum(
        1 for transaction in transactions if transaction.book_id == book_id
    )


def _fold(
    transactions: tuple[LedgerTransaction, ...],
    account: AccountRef,
    kind: ResourceKind,
) -> Quantity:
    """A balance is derived from history, never stored beside it.

    Storing a running total would create a second authority for the same fact,
    and the two would eventually disagree with nothing to say which was right.
    A stored total is a performance decision for the package that measures a
    need for one.
    """
    total = zero_of(kind)
    for transaction in transactions:
        if transaction.kind is not kind:
            continue
        total = total + transaction.effect_on(account)
    return total


class InMemoryLedgerRepository:
    """One unit of work's view of the book: committed history plus its own work."""

    def __init__(self, book: LedgerBook) -> None:
        self._book = book
        self._committed = book.snapshot()
        self._pending: list[tuple[LedgerTransaction, int]] = []

    # -- LedgerRepository --------------------------------------------------- #

    def version_of(self, book_id: UUID) -> int:
        return _version_of(self._all(), book_id)

    def balance_of(self, account: AccountRef, kind: ResourceKind) -> Quantity:
        return _fold(self._all(), account, kind)

    def append(self, transaction: LedgerTransaction, *, expected_version: int) -> None:
        if any(existing.id == transaction.id for existing in self._all()):
            raise UniquenessConflict("ledger_transaction.id")
        # The precondition is carried, not decided: it is re-checked in
        # `LedgerBook.committing`, under the lock, where the append happens.
        self._pending.append((transaction, expected_version))

    def get(self, transaction_id: UUID) -> LedgerTransaction | None:
        for transaction in self._all():
            if transaction.id == transaction_id:
                return transaction
        return None

    # -- the unit of work's own hooks --------------------------------------- #

    def pending(self) -> tuple[tuple[LedgerTransaction, int], ...]:
        return tuple(self._pending)

    def discard(self) -> None:
        self._pending.clear()

    def _all(self) -> tuple[LedgerTransaction, ...]:
        """Committed history as it was when this transaction opened, plus its own.

        The committed half is read once, at construction, rather than on every
        call: a transaction that saw a different history from one statement to
        the next would be reading at an isolation level this repository has not
        got, and the version precondition it computes would mean nothing.
        """
        return self._committed + tuple(
            transaction for transaction, _ in self._pending
        )


class LedgerUnitOfWork:
    """A `UnitOfWork` for durable records, plus a ledger, committed in order.

    The database half — the idempotency receipt and the audit event — is whatever
    unit of work is handed in: the real `SqlAlchemyUnitOfWork` against
    PostgreSQL, or the in-memory `FakeUnitOfWork` for the application tests. The
    ledger half is the reference book above.

    **`commit()` is one critical section on the book, and the durable commit
    happens inside it.** The preconditions are decided first, the durable half
    commits second, the postings become visible third. So:

    - a durable-half failure leaves no posting, because the append never
      happened rather than because a compensating deletion put it back;
    - a posting that failed its precondition is never followed by a receipt
      claiming success, because the durable commit is not reached; and
    - a concurrent caller either finished before this one started, or starts
      after it finished. It cannot interleave, and nothing this unit of work
      does can remove its work.

    The residual window — a process death between the durable commit and the
    append — is stated in the module docstring, along with why it is
    unobservable here and what closes it when the ledger gets a table.
    """

    def __init__(self, book: LedgerBook, inner) -> None:
        self._book = book
        self._inner = inner
        self._entered = False

    # -- LedgerUnitOfWork --------------------------------------------------- #

    ledger: InMemoryLedgerRepository
    idempotency: IdempotencyRepository
    audit: AuditRepository

    def __enter__(self) -> LedgerUnitOfWork:
        self._inner.__enter__()
        self._entered = True
        self.ledger = InMemoryLedgerRepository(self._book)
        # Delegated rather than copied: these are the *inner* unit of work's
        # repositories, joined to its transaction, so the receipt and the audit
        # row are written by the session that commits them.
        self.idempotency = self._inner.idempotency
        self.audit = self._inner.audit
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if exc_type is not None:
            self.rollback()
        self._entered = False
        self._inner.__exit__(exc_type, exc, traceback)

    def commit(self) -> None:
        self._require_entered()
        pending = self.ledger.pending()
        try:
            with self._book.committing(pending):
                self._inner.commit()
        finally:
            # Whatever happened, this unit of work is finished with its pending
            # work: applied and now committed history, or refused and gone.
            self.ledger.discard()

    def rollback(self) -> None:
        if self._entered:
            self.ledger.discard()
        self._inner.rollback()

    def _require_entered(self) -> None:
        if not self._entered:
            raise RuntimeError("The unit of work must be entered before use.")


def unit_of_work_factory(book: LedgerBook, inner_factory):
    """A factory the service calls once per attempt.

    Takes the *inner* factory rather than an inner unit of work: a unit of work
    is one transaction, and handing the same one to two attempts would make the
    second attempt commit the first's work.
    """

    def factory() -> LedgerUnitOfWork:
        return LedgerUnitOfWork(book, inner_factory())

    return factory
