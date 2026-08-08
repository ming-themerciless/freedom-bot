"""Turn driver and ORM exceptions into typed application errors, once.

A concurrent apply can lose on any of six uniqueness rules, and before this
module the loser escaped as a raw `sqlalchemy.exc.IntegrityError` whose string
form carries the failing statement, its bound parameters and the driver's own
message. That reached the caller, the operator and anything that logged it.

Two decisions are worth stating.

**The translation wraps the session, not each repository method.** A repository
that forgets to wrap one `execute` would leak, and there is no test that can see
the omission. `TranslatingSession` is the only session the unit of work hands
out, so every statement any repository issues passes through here.

**The mapping is from database constraint name to a stable application rule
name**, and it is exhaustive over the uniqueness rules in the retained schema.
An unrecognised constraint is *not* guessed at: it becomes
`UniquenessConflict("unknown")`, which callers treat as an unresolvable
conflict and refuse on, rather than as a duplicate of something they can name.
`tests/test_database_translation.py` checks the mapping against the live
migrated schema, so a new unique index that nobody classified fails the suite.
"""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from application.errors import PersistenceError, UniquenessConflict

#: PostgreSQL constraint/index name → the rule name application code branches on.
#:
#: The keys are what the database reports; the values are vocabulary this
#: codebase owns. Keeping them separate is what lets an index be renamed without
#: rewriting the import service, and stops an index name — which is schema
#: detail — being recorded in an audit row.
CONSTRAINT_RULES = {
    "uq_snapshot_imports_request_key": "snapshot_import.request_key",
    "uq_snapshot_imports_applied_input": "snapshot_import.applied_input",
    "uq_foundry_snapshots_checksum": "foundry_snapshot.checksum",
    "uq_external_actor_mappings_world_id_external_actor_id": "external_actor_mapping.world_actor",
    "uq_external_actor_mappings_character_id_world_id": "external_actor_mapping.character_world",
    "uq_sheet_row_mappings_sheet_tab_row_index": "sheet_row_mapping.sheet_row",
    "uq_sheet_row_mappings_character_id_sheet_tab": "sheet_row_mapping.character_tab",
    "uq_idempotency_keys_scope_key": "idempotency_key.scope_key",
    "uq_character_access_one_active_link": "character_access.active_link",
    "uq_character_access_one_active_owner": "character_access.active_owner",
    "uq_character_access_one_active_default_per_user": "character_access.active_default",
    "pk_platform_initialization": "platform_initialization.singleton",
    "pk_characters": "character.id",
    "pk_snapshot_imports": "snapshot_import.id",
    "pk_foundry_snapshots": "foundry_snapshot.id",
    "pk_external_actor_mappings": "external_actor_mapping.id",
    "pk_audit_events": "audit_event.id",
    "pk_discord_users": "discord_user.id",
    "pk_sheet_row_mappings": "sheet_row_mapping.id",
    "pk_character_access": "character_access.id",
    "pk_idempotency_keys": "idempotency_key.id",
    "pk_discord_guild_memberships": "discord_guild_membership.id",
    "pk_discord_membership_roles": "discord_membership_role.id",
}

#: What a conflict is called when the constraint is one nobody classified. It is
#: a name, not an excuse: a caller cannot resolve it into a duplicate, because it
#: cannot say which winning row to re-read.
UNKNOWN_RULE = "unknown"

#: The SQLSTATEs that actually mean "somebody else already holds this identity":
#: `unique_violation` and `exclusion_violation`.
#:
#: `IntegrityError` is wider than that. A foreign-key, check or not-null
#: violation is also an `IntegrityError`, and none of them is a lost race — they
#: are the database refusing something the application should never have
#: attempted. Classifying by exception class alone would file each of them as a
#: conflict, and a caller resolving conflicts by re-reading "the winning row"
#: would then look for a winner that does not exist. They become
#: `PersistenceError`, which no caller may resolve into a duplicate.
CONFLICT_SQLSTATES = frozenset({"23505", "23P01"})


def _sqlstate(error: SQLAlchemyError) -> str | None:
    return getattr(getattr(error, "orig", None), "sqlstate", None)


def _constraint_name(error: IntegrityError) -> str | None:
    """The violated constraint, from the driver's structured diagnostics.

    Read from `psycopg`'s `Diagnostic` object rather than parsed out of the
    message text: the message is localisable and carries the offending values,
    and matching on it would mean handling that content in order to classify it.
    """
    diagnostic = getattr(getattr(error, "orig", None), "diag", None)
    return getattr(diagnostic, "constraint_name", None)


def rule_for(error: IntegrityError) -> str:
    return CONSTRAINT_RULES.get(_constraint_name(error) or "", UNKNOWN_RULE)


@contextmanager
def translating(session: Session) -> Iterator[None]:
    """Run a statement; let no driver exception out.

    The rollback happens here, before the raise. A PostgreSQL transaction is
    aborted after an error and rejects every later statement in it, so a caller
    that catches the typed error and wants to re-read the winning row would
    otherwise be handed an unusable connection.
    """
    try:
        yield
    except IntegrityError as error:
        state = _sqlstate(error)
        rule = rule_for(error)
        session.rollback()
        # `from None`: chaining would put the failing statement and its bound
        # parameters back into any traceback that is rendered or logged.
        if state in CONFLICT_SQLSTATES:
            raise UniquenessConflict(rule) from None
        raise PersistenceError(state) from None
    except SQLAlchemyError as error:
        state = _sqlstate(error)
        session.rollback()
        raise PersistenceError(state) from None


class TranslatingSession:
    """The session repositories are given. No driver exception escapes it.

    It is a deliberate narrow proxy rather than a `Session` subclass: the
    surface the repositories and the unit of work actually use is small, and
    keeping it small is what makes "every path is translated" reviewable by
    reading this class.

    Every failure rolls the transaction back **here**, before raising. A
    PostgreSQL transaction is aborted after an error and will reject every
    later statement in it; a caller that catches the typed error and wants to
    re-read the winning row needs a usable connection, and leaving the rollback
    to a later `__exit__` would not give it one.
    """

    __slots__ = ("_session",)

    def __init__(self, session: Session) -> None:
        self._session = session

    def execute(self, statement: Any, *args: Any, **kwargs: Any) -> Any:
        with translating(self._session):
            return self._session.execute(statement, *args, **kwargs)

    def flush(self, *args: Any, **kwargs: Any) -> None:
        with translating(self._session):
            self._session.flush(*args, **kwargs)

    def commit(self) -> None:
        with translating(self._session):
            self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

    def close(self) -> None:
        self._session.close()
