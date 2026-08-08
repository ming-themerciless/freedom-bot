"""Typed persistence failures the application is allowed to see.

Adapters translate driver and ORM exceptions into these before they cross the
boundary (`.agents/AGENTS.md`: "Return typed domain/application errors"). Two
things follow, and both are load-bearing for the import path.

**Nothing carrying SQL, bound parameters, Actor values, a connection string, a
traceback or a driver class name reaches application code.** The messages here
are written, not derived from the exception that caused them, and the causing
exception is deliberately dropped (`raise ... from None`) rather than chained —
a chained `__cause__` puts the original statement and its parameters back into
any traceback that gets rendered or logged.

**A lost race is distinguishable from a broken database.** `UniquenessConflict`
means another transaction got there first, which is an expected outcome a caller
can resolve by re-reading the winning row. `PersistenceError` means something
else went wrong, and a caller must not quietly translate it into "somebody else
already did this" — mislabelling a failure as a duplicate is how an import that
never happened gets reported as a successful no-op.
"""
from __future__ import annotations


class ConcurrencyConflictError(RuntimeError):
    """The aggregate changed after the caller read it."""


class UniquenessConflict(RuntimeError):
    """Another transaction already holds the identity this one tried to claim.

    `rule` is a stable application-level name for the uniqueness rule that was
    violated — `"snapshot_import.request_key"`, not the PostgreSQL index name
    and not the statement. Callers branch on it; it is safe to record.

    The transaction is already rolled back by the time this is raised. There is
    nothing partially written to clean up, and nothing to commit.
    """

    def __init__(self, rule: str) -> None:
        # "to the database", explicitly. These errors are raised by the database
        # adapter and describe a rolled-back transaction, but the snapshot
        # submission path reaches them *after* an artifact has been written to
        # the filesystem, and an unqualified "nothing was written" would be read
        # there as a claim about all durable state (review finding I-1).
        super().__init__(
            f"Another transaction already claimed {rule}. Nothing was written "
            "to the database by this attempt."
        )
        self.rule = rule


class PersistenceError(RuntimeError):
    """The database could not complete the work, and the transaction rolled back.

    Deliberately *not* a conflict. This is the controlled boundary for an
    unexpected failure: a caller may report it, retry it or give up, but it must
    never be resolved into a duplicate receipt.

    `sqlstate` is the standard five-character SQLSTATE class when the driver
    supplied one. It is a classification, not content: it names *what kind* of
    error occurred without naming the statement, the parameters or the server.
    """

    def __init__(self, sqlstate: str | None = None) -> None:
        detail = f" (SQLSTATE {sqlstate})" if sqlstate else ""
        super().__init__(
            "The database could not complete this operation and the transaction "
            f"was rolled back{detail}. Nothing was written to the database."
        )
        self.sqlstate = sqlstate
