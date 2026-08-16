"""Migration 0009 rehearsed against real PostgreSQL: up, down and up again.

OD-44 adds the only Phase 3 revision whose downgrade is **lossy in a way an
operator has to act on**, and a rehearsal that only proved "the statements run"
would hide that. So this module asserts the consequence as well as the mechanics:

1. `0008 → 0009` adds the two columns, the foreign key, the unique index and the
   check constraint, and a bound Discord OAuth session can be created;
2. `0009 → 0008` drops them. **The session rows survive** — the table returns to
   exactly its pre-0009 shape — but which transaction produced which session, and
   every `completion_claimed_at`, are gone and are not recoverable;
3. `0008 → 0009` again **refuses**, naming the number of unbindable sessions and
   the one statement that resolves it, and leaves the database at 0008 rather
   than half-applying. That is the cost, stated as an executable fact rather than
   as a warning in a docstring: a downgrade past 0009 ends every Discord OAuth
   login, because those sessions must be **deleted** — not merely revoked — before
   the binding can be restored;
4. after the documented remedy, the re-upgrade succeeds and the binding column is
   back, still empty. Nothing reconstructs it, and nothing pretends to.

The rehearsal runs Alembic in a subprocess through the same guarded helper the
rest of the suite uses, so the static target guard and the live Unix-socket
identity check both apply. It restores `head` before it returns.
"""
from __future__ import annotations

from hashlib import sha256
from subprocess import CalledProcessError
from uuid import UUID, uuid4

import pytest
from sqlalchemy import inspect, text

from tests.conftest import run_alembic

pytestmark = pytest.mark.database

BINDING_COLUMN = "oauth_transaction_id"
CLAIM_COLUMN = "completion_claimed_at"

#: OD-44 condition 2. The objects that make a rotation chain linear, added by the
#: same revision because the partial completion index is only safe with them.
ROTATION_INDEX = "uq_sessions_rotated_from_session_id"
ROTATION_CONSTRAINTS = (
    "fk_sessions_rotation_account_method",
    "fk_sessions_rotation_oauth_binding",
    "uq_sessions_rotation_identity",
    "uq_sessions_rotation_binding",
)


def _columns(engine, table: str) -> set[str]:
    return {column["name"] for column in inspect(engine).get_columns(table)}


def _indexes(engine, table: str) -> set[str]:
    return {index["name"] for index in inspect(engine).get_indexes(table)}


def _constraints(engine, table: str) -> set[str]:
    """Every constraint the catalogue holds for a table, by name.

    Read from `pg_constraint` rather than assembled from the inspector's typed
    accessors: what is being asserted is that the database *has* these objects,
    and a helper that only looked at foreign keys would quietly stop covering the
    unique keys they reference.
    """
    with engine.connect() as connection:
        return set(
            connection.execute(
                text(
                    "SELECT conname FROM pg_constraint "
                    " WHERE conrelid = CAST(:table AS regclass)"
                ),
                {"table": table},
            ).scalars()
        )


def _seed_bound_session(connection) -> tuple[UUID, UUID, UUID]:
    """One account, one consumed-and-claimed transaction, one session bound to it."""
    account_id, transaction_id, session_id = uuid4(), uuid4(), uuid4()
    connection.execute(
        text(
            "INSERT INTO platform_accounts (id, status, is_protected_admin) "
            "VALUES (:id, 'active', false)"
        ),
        {"id": account_id},
    )
    connection.execute(
        text(
            """
            INSERT INTO oauth_transactions (
                id, state_hash, key_version, return_path, provider_key,
                created_at, expires_at, consumed_at, completion_claimed_at
            ) VALUES (
                :id, :state_hash, 1, '/v1/characters', 'discord',
                now(), now() + interval '10 minutes', now(), now()
            )
            """
        ),
        {"id": transaction_id, "state_hash": sha256(transaction_id.bytes).digest()},
    )
    connection.execute(
        text(
            """
            INSERT INTO sessions (
                id, token_hash, platform_account_id, auth_method,
                created_at, last_seen_at, idle_expires_at, absolute_expires_at,
                privilege_fingerprint, oauth_transaction_id
            ) VALUES (
                :id, :token_hash, :account, 'discord_oauth',
                now(), now(), now() + interval '60 minutes',
                now() + interval '12 hours', :fingerprint, :transaction
            )
            """
        ),
        {
            "id": session_id,
            "token_hash": sha256(session_id.bytes).digest(),
            "account": account_id,
            "fingerprint": sha256(b"fingerprint").digest(),
            "transaction": transaction_id,
        },
    )
    return account_id, transaction_id, session_id


def _clean(connection, account_id: UUID, transaction_id: UUID, session_id: UUID) -> None:
    """Children first: the binding foreign key is `RESTRICT` by design."""
    connection.execute(text("DELETE FROM sessions WHERE id = :id"), {"id": session_id})
    connection.execute(
        text("DELETE FROM oauth_transactions WHERE id = :id"), {"id": transaction_id}
    )
    connection.execute(
        text("DELETE FROM platform_accounts WHERE id = :id"), {"id": account_id}
    )


def test_0009_upgrades_downgrades_and_re_upgrades_with_its_documented_cost(
    database_url, migrated_database
):
    """The full rehearsal, including what the downgrade costs a populated database."""
    engine = migrated_database
    ids: tuple[UUID, UUID, UUID] | None = None
    try:
        # --- 1. head: the binding exists and a bound session is insertable ----
        assert BINDING_COLUMN in _columns(engine, "sessions")
        assert CLAIM_COLUMN in _columns(engine, "oauth_transactions")
        assert "uq_sessions_oauth_transaction_id" in _indexes(engine, "sessions")
        assert ROTATION_INDEX in _indexes(engine, "sessions")
        assert set(ROTATION_CONSTRAINTS) <= _constraints(engine, "sessions")

        with engine.begin() as connection:
            ids = _seed_bound_session(connection)
        account_id, transaction_id, session_id = ids

        # --- 2. downgrade: the columns go, the sessions stay ------------------
        run_alembic(database_url, "downgrade", "0008")

        assert BINDING_COLUMN not in _columns(engine, "sessions")
        assert CLAIM_COLUMN not in _columns(engine, "oauth_transactions")
        assert ROTATION_INDEX not in _indexes(engine, "sessions")
        assert not set(ROTATION_CONSTRAINTS) & _constraints(engine, "sessions")
        with engine.connect() as connection:
            survived = connection.execute(
                text("SELECT count(*) FROM sessions WHERE id = :id"), {"id": session_id}
            ).scalar_one()
            # Pre-0009 shape restored exactly: a `discord_oauth` session with no
            # transaction column is what this table looked like before OD-44, so
            # the row is not merely tolerated — it is ordinary.
            transactions = connection.execute(
                text("SELECT count(*) FROM oauth_transactions WHERE id = :id"),
                {"id": transaction_id},
            ).scalar_one()
        assert survived == 1, "a downgrade must not destroy live sessions"
        assert transactions == 1

        # --- 3. the re-upgrade REFUSES, and says why --------------------------
        # This is the cost, and it is a refusal rather than a silent repair: the
        # surviving session cannot be bound, because the transaction that
        # produced it is no longer recorded anywhere. Revoking it would not help;
        # the constraint is evaluated over every row.
        with pytest.raises(CalledProcessError) as refusal:
            run_alembic(database_url, "upgrade", "head")
        message = refusal.value.stderr
        assert "Revision 0009 refused" in message
        assert "1 Discord OAuth session row(s)" in message
        assert "DELETE FROM sessions WHERE auth_method = 'discord_oauth';" in message

        with engine.connect() as connection:
            still_at_0008 = BINDING_COLUMN not in _columns(engine, "sessions")
            survived = connection.execute(
                text("SELECT count(*) FROM sessions WHERE id = :id"), {"id": session_id}
            ).scalar_one()
        assert still_at_0008, "a refused revision must not half-apply"
        assert survived == 1, "and must not delete anything on its way out"

        # --- 4. the documented remedy, and the re-upgrade succeeds ------------
        with engine.begin() as connection:
            connection.execute(text("DELETE FROM sessions WHERE auth_method = 'discord_oauth'"))
        run_alembic(database_url, "upgrade", "head")

        assert BINDING_COLUMN in _columns(engine, "sessions")
        with engine.connect() as connection:
            claim = connection.execute(
                text(
                    "SELECT completion_claimed_at FROM oauth_transactions WHERE id = :id"
                ),
                {"id": transaction_id},
            ).scalar_one()
            sessions_left = connection.execute(
                text("SELECT count(*) FROM sessions WHERE id = :id"), {"id": session_id}
            ).scalar_one()
        assert claim is None, "the claim timestamp is not recoverable either"
        assert sessions_left == 0, "the remedy ended that login, as documented"
        ids = (account_id, transaction_id, session_id)
    finally:
        # `head` again whatever happened, so the session-scoped fixture is not
        # left holding a database at another revision for every later test.
        run_alembic(database_url, "upgrade", "head")
        if ids is not None:
            with engine.begin() as connection:
                _clean(connection, *ids)


def test_the_downgrade_is_reversible_on_an_empty_database(database_url, migrated_database):
    """The ordinary reversibility rule, with no rows to complicate it.

    Separated from the rehearsal above deliberately: the interesting statement in
    that test is the *cost*, and a reader should be able to see that revision 0009
    is plainly reversible without having to hold the populated case in their head
    at the same time.
    """
    engine = migrated_database
    try:
        run_alembic(database_url, "downgrade", "0008")
        assert BINDING_COLUMN not in _columns(engine, "sessions")
        assert CLAIM_COLUMN not in _columns(engine, "oauth_transactions")
        assert "uq_sessions_oauth_transaction_id" not in _indexes(engine, "sessions")

        run_alembic(database_url, "upgrade", "0009")
        assert BINDING_COLUMN in _columns(engine, "sessions")
        assert CLAIM_COLUMN in _columns(engine, "oauth_transactions")
        assert "uq_sessions_oauth_transaction_id" in _indexes(engine, "sessions")
        assert ROTATION_INDEX in _indexes(engine, "sessions")
        assert set(ROTATION_CONSTRAINTS) <= _constraints(engine, "sessions")
    finally:
        run_alembic(database_url, "upgrade", "head")


def test_the_binding_foreign_key_declares_restrict(migrated_database):
    """N-04's reaper must not be able to orphan a session (schema §9.1).

    Asserted from the catalogue rather than from the migration source, because
    what protects a live session is the constraint the database holds, not the
    argument the revision passed.
    """
    with migrated_database.connect() as connection:
        rule = connection.execute(
            text(
                """
                SELECT confdeltype FROM pg_constraint
                 WHERE conname = 'fk_sessions_oauth_transaction_id_oauth_transactions'
                """
            )
        ).scalar_one()
    assert rule == "r", "the binding foreign key must be RESTRICT"


def test_a_bound_session_survives_the_transactions_expiry_window(migrated_database):
    """A live session outlives N-04's ten minutes, and the reaper must cope.

    The transaction expires long before the session does — ten minutes against
    twelve hours — so `purge_expired` will meet a referenced row in ordinary
    operation, not only in a contrived test. It must refuse rather than orphan,
    which is what `RESTRICT` buys and what the operations document tells an
    operator to expect.
    """
    from sqlalchemy.exc import IntegrityError

    with migrated_database.begin() as connection:
        ids = _seed_bound_session(connection)

    try:
        with pytest.raises(IntegrityError, match="fk_sessions_oauth_transaction_id"):
            with migrated_database.begin() as connection:
                connection.execute(
                    text("DELETE FROM oauth_transactions WHERE expires_at < :before"),
                    {"before": "9999-01-01"},
                )
    finally:
        with migrated_database.begin() as connection:
            _clean(connection, *ids)


def test_the_rotation_keys_declare_restrict_and_reference_the_predecessors_own_values(
    migrated_database,
):
    """OD-44 condition 2, read from the catalogue rather than from the revision.

    What makes a rotation unable to cross an account, a method or a login is the
    pair of composite foreign keys the database holds — not the arguments the
    revision passed — so the columns each one carries are asserted from
    `pg_constraint`. A key that had quietly lost a column would still be present
    under its name and would still be `RESTRICT`, and only this comparison would
    notice.
    """
    expected = {
        "fk_sessions_rotation_account_method": (
            ["rotated_from_session_id", "platform_account_id", "auth_method"],
            ["id", "platform_account_id", "auth_method"],
        ),
        "fk_sessions_rotation_oauth_binding": (
            ["rotated_from_session_id", "oauth_transaction_id"],
            ["id", "oauth_transaction_id"],
        ),
    }
    with migrated_database.connect() as connection:
        for name, (referencing, referenced) in expected.items():
            row = connection.execute(
                text(
                    """
                    SELECT confdeltype,
                           (SELECT array_agg(attname ORDER BY ordinality)
                              FROM unnest(conkey) WITH ORDINALITY AS k(attnum, ordinality)
                              JOIN pg_attribute
                                ON pg_attribute.attrelid = conrelid
                               AND pg_attribute.attnum = k.attnum) AS referencing,
                           (SELECT array_agg(attname ORDER BY ordinality)
                              FROM unnest(confkey) WITH ORDINALITY AS k(attnum, ordinality)
                              JOIN pg_attribute
                                ON pg_attribute.attrelid = confrelid
                               AND pg_attribute.attnum = k.attnum) AS referenced
                      FROM pg_constraint
                     WHERE conname = :name
                    """
                ),
                {"name": name},
            ).mappings().one()
            assert row["confdeltype"] == "r", f"{name} must be RESTRICT"
            assert list(row["referencing"]) == referencing
            assert list(row["referenced"]) == referenced


def test_the_linear_rotation_index_is_unique_and_scoped_to_rotations(migrated_database):
    """The branching control, with its predicate — the predicate is the whole point.

    A table-wide unique index over `rotated_from_session_id` would refuse every
    root session but the first, because they all carry null. `WHERE
    rotated_from_session_id IS NOT NULL` is what makes "one successor per
    predecessor" expressible, and an index silently created without it would pass
    a name check while breaking every login.
    """
    with migrated_database.connect() as connection:
        definition = connection.execute(
            text("SELECT indexdef FROM pg_indexes WHERE indexname = :name"),
            {"name": ROTATION_INDEX},
        ).scalar_one()
    assert "UNIQUE INDEX" in definition
    assert "rotated_from_session_id" in definition
    assert "WHERE (rotated_from_session_id IS NOT NULL)" in definition


def test_the_re_upgrade_refuses_a_branched_rotation_chain_it_cannot_describe(
    database_url, migrated_database
):
    """The second precondition: a chain that branched before 0009 existed.

    `ADD CONSTRAINT` validates existing rows, so a database carrying a branch
    would meet a constraint name where it needs a cause and a remedy. The revision
    counts first and refuses with both — and leaves the database at 0008 rather
    than half-applying, exactly as the unbindable-session precondition does.

    The branch is created at 0008, where nothing forbade it. Break-glass sessions
    are used because the unbindable-session precondition would otherwise refuse
    first and this test would prove that one twice.
    """
    engine = migrated_database
    account_id, first, second, third = uuid4(), uuid4(), uuid4(), uuid4()
    try:
        run_alembic(database_url, "downgrade", "0008")
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO platform_accounts (id, status, is_protected_admin) "
                    "VALUES (:id, 'active', false)"
                ),
                {"id": account_id},
            )
            for session_id, rotated_from in (
                (first, None),
                (second, first),
                (third, first),  # the branch
            ):
                connection.execute(
                    text(
                        """
                        INSERT INTO sessions (
                            id, token_hash, platform_account_id, auth_method,
                            created_at, last_seen_at, idle_expires_at,
                            absolute_expires_at, privilege_fingerprint,
                            rotated_from_session_id
                        ) VALUES (
                            :id, :token_hash, :account, 'webauthn',
                            now(), now(), now() + interval '15 minutes',
                            now() + interval '60 minutes', :fingerprint, :rotated_from
                        )
                        """
                    ),
                    {
                        "id": session_id,
                        "token_hash": sha256(session_id.bytes).digest(),
                        "account": account_id,
                        "fingerprint": sha256(b"fingerprint").digest(),
                        "rotated_from": rotated_from,
                    },
                )

        with pytest.raises(CalledProcessError) as refusal:
            run_alembic(database_url, "upgrade", "head")
        message = refusal.value.stderr
        assert "Revision 0009 refused" in message
        assert "1 session(s) have more than one successor" in message
        assert "DELETE FROM sessions WHERE rotated_from_session_id IS NOT NULL;" in message
        assert ROTATION_INDEX not in _indexes(engine, "sessions"), (
            "a refused revision must not half-apply"
        )

        # The documented remedy, and then the upgrade goes through.
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM sessions WHERE rotated_from_session_id IS NOT NULL")
            )
        run_alembic(database_url, "upgrade", "head")
        assert ROTATION_INDEX in _indexes(engine, "sessions")
    finally:
        run_alembic(database_url, "upgrade", "head")
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM sessions WHERE platform_account_id = :id"),
                {"id": account_id},
            )
            connection.execute(
                text("DELETE FROM platform_accounts WHERE id = :id"), {"id": account_id}
            )
