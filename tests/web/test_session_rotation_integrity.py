"""TC-AUTH-16: OD-44 condition 2 — a rotation chain is linear and does not cross.

Peter's 2026-08-14 approval of the partial unique index

    UNIQUE (oauth_transaction_id) WHERE rotated_from_session_id IS NULL

is conditional. The predicate deliberately lets *rotated* sessions share the
transaction id their root was bound to, because a rotation is the same login; that
is only safe if the set of rows allowed to share it is exactly one linear chain
per login. If a session could acquire two successors, or a rotation could change
account, authentication method or OAuth binding, the predicate would be a hole in
the completion binding rather than an accommodation of N-08.

So these tests are about the shape of the chain, from three directions:

- **the database with the application bypassed** — raw `INSERT`s prove that the
  partial unique index and the two composite rotation foreign keys refuse a
  branch, a cross-account rotation, a cross-method rotation and a cross-binding
  rotation whatever the application believes;
- **the service** — a revoked, already-rotated, unknown or foreign predecessor is
  a typed `SessionRotationRefused`, not an `IntegrityError` surfacing as a `500`
  and not a silently improvised second chain;
- **two real connections** — the one-successor transition is proved by racing it.
  The loser blocks on the winner's row lock, re-evaluates when it is released and
  is refused. There is no sleep in this module.

The liveness rule is the one fact PostgreSQL cannot state declaratively — "still
live" is a `now()` comparison — so it lives in the single locked repository
operation, and the tests for it go through that operation rather than through a
constraint.
"""
from __future__ import annotations

import inspect
import threading
from datetime import timedelta
from hashlib import sha256
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import IntegrityError

from adapters.database.tables import sessions
from adapters.web.repositories import SessionRepository
from application.audit import ActorCapability
from application.web.capabilities import (
    AdministratorScope,
    AuthMethod,
    MembershipProjection,
    WebAuthorizationContext,
)
from application.web.sessions import SessionRotationRefused, SessionService
from tests.web.conftest import make_account, seed_oauth_transaction, utcnow
from tests.web_fixtures import TEST_GUILD_ID

pytestmark = pytest.mark.database


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def oauth_context(account_id: UUID, *capabilities) -> WebAuthorizationContext:
    """A Discord OAuth context. Distinct capability sets give distinct fingerprints."""
    return WebAuthorizationContext(
        account_id=account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        capabilities=frozenset(capabilities),
        administrator_scope=AdministratorScope.FULL,
        membership=MembershipProjection(
            guild_id=TEST_GUILD_ID,
            is_member=True,
            role_ids=frozenset(),
            observed_at=utcnow(),
        ),
    )


def break_glass_context(
    account_id: UUID, *capabilities, auth_method: AuthMethod = AuthMethod.WEBAUTHN
) -> WebAuthorizationContext:
    return WebAuthorizationContext(
        account_id=account_id,
        auth_method=auth_method,
        capabilities=frozenset(capabilities or (ActorCapability.PLATFORM_ADMINISTRATOR,)),
        administrator_scope=AdministratorScope.EMERGENCY_CONTINUITY,
        membership=None,
    )


def _insert_session(
    connection,
    *,
    account_id: UUID,
    auth_method: str,
    oauth_transaction_id: UUID | None,
    rotated_from: UUID | None = None,
) -> UUID:
    """A session row written with the application entirely out of the way.

    The constraint tests need this: a test that reached the database through
    `SessionService` would prove what the service does, and what is under test
    here is what the database refuses when the service is not there to be
    trusted.
    """
    session_id = uuid4()
    now = utcnow()
    connection.execute(
        text(
            """
            INSERT INTO sessions (
                id, token_hash, platform_account_id, auth_method,
                created_at, last_seen_at, idle_expires_at, absolute_expires_at,
                privilege_fingerprint, rotated_from_session_id, oauth_transaction_id
            ) VALUES (
                :id, :token_hash, :account, :auth_method,
                :now, :now, :idle, :absolute,
                :fingerprint, :rotated_from, :transaction
            )
            """
        ),
        {
            "id": session_id,
            "token_hash": sha256(session_id.bytes).digest(),
            "account": account_id,
            "auth_method": auth_method,
            "now": now,
            "idle": now + timedelta(minutes=60),
            "absolute": now + timedelta(hours=12),
            "fingerprint": sha256(b"fingerprint").digest(),
            "rotated_from": rotated_from,
            "transaction": oauth_transaction_id,
        },
    )
    return session_id


def _row(connection, session_id: UUID):
    return (
        connection.execute(select(sessions).where(sessions.c.id == session_id))
        .mappings()
        .one()
    )


def _successors(connection, predecessor_id: UUID) -> list[UUID]:
    return list(
        connection.execute(
            select(sessions.c.id).where(
                sessions.c.rotated_from_session_id == predecessor_id
            )
        ).scalars()
    )


def _live_sessions(connection, account_id: UUID) -> list[UUID]:
    return list(
        connection.execute(
            select(sessions.c.id).where(
                sessions.c.platform_account_id == account_id,
                sessions.c.revoked_at.is_(None),
            )
        ).scalars()
    )


def _begin_oauth_session(composition, migrated_database, *capabilities):
    """A root Discord OAuth session and the transaction it is bound to."""
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        transaction_id = seed_oauth_transaction(connection, claimed=True)
        issued = composition.services(connection).session_service.begin(
            context=oauth_context(account_id, *capabilities),
            now=utcnow(),
            correlation_id=uuid4(),
            oauth_transaction_id=transaction_id,
        )
    return account_id, transaction_id, issued


# ---------------------------------------------------------------------------
# TC-AUTH-16a — the rotations that must keep working
# ---------------------------------------------------------------------------


def test_an_oauth_rotation_chain_stays_linear_and_carries_one_binding(
    migrated_database, composition
):
    """TC-AUTH-16a. Two rotations of one login: one chain, one live session, one claim.

    N-08 is the reason the partial index exists, so the first thing to establish
    is that it still works — twice, because a chain of length two is where a
    second-generation rotation would branch if the predecessor lookup were wrong.
    """
    account_id, transaction_id, root = _begin_oauth_session(
        composition, migrated_database, ActorCapability.GUILD_MEMBER
    )

    with migrated_database.begin() as connection:
        services = composition.services(connection)
        record = services.session_service.resolve(root.token, now=utcnow())
        first = services.session_service.rotate_if_privileges_changed(
            record=record,
            context=oauth_context(
                account_id, ActorCapability.GUILD_MEMBER, ActorCapability.GUILD_COUNCIL
            ),
            now=utcnow(),
            correlation_id=uuid4(),
        )
    assert first is not None

    with migrated_database.begin() as connection:
        services = composition.services(connection)
        record = services.session_service.resolve(first.token, now=utcnow())
        second = services.session_service.rotate_if_privileges_changed(
            record=record,
            context=oauth_context(account_id, ActorCapability.GUILD_MEMBER),
            now=utcnow(),
            correlation_id=uuid4(),
        )
    assert second is not None

    with migrated_database.connect() as connection:
        rows = {
            "root": _row(connection, root.session_id),
            "first": _row(connection, first.session_id),
            "second": _row(connection, second.session_id),
        }
        live = _live_sessions(connection, account_id)

    assert [row["oauth_transaction_id"] for row in rows.values()] == [transaction_id] * 3
    assert rows["first"]["rotated_from_session_id"] == root.session_id
    assert rows["second"]["rotated_from_session_id"] == first.session_id
    assert rows["root"]["revocation_reason"] == "privilege_change"
    assert rows["first"]["revocation_reason"] == "privilege_change"
    assert rows["second"]["revoked_at"] is None
    # The whole point of insert-then-revoke in one transaction: never two.
    assert live == [second.session_id]


def test_a_break_glass_rotation_stays_unbound_to_any_oauth_transaction(
    migrated_database, composition
):
    """TC-AUTH-16a. SM-03's sessions rotate too, and name no transaction.

    The composite binding foreign key does not apply to a row whose
    `oauth_transaction_id` is null, so this is the case where the account and
    method key is the only structural equality control — and the check constraint
    independently keeps the successor unbound.
    """
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        root = composition.services(connection).session_service.begin(
            context=break_glass_context(account_id),
            now=utcnow(),
            correlation_id=uuid4(),
        )

    with migrated_database.begin() as connection:
        services = composition.services(connection)
        record = services.session_service.resolve(root.token, now=utcnow())
        rotated = services.session_service.rotate(
            record=record,
            context=break_glass_context(account_id),
            now=utcnow(),
        )

    with migrated_database.connect() as connection:
        successor = _row(connection, rotated.session_id)
        predecessor = _row(connection, root.session_id)
        live = _live_sessions(connection, account_id)

    assert successor["oauth_transaction_id"] is None
    assert successor["auth_method"] == AuthMethod.WEBAUTHN.value
    assert successor["rotated_from_session_id"] == root.session_id
    assert predecessor["revoked_at"] is not None
    assert live == [rotated.session_id]


# ---------------------------------------------------------------------------
# TC-AUTH-16b — the service refuses what it cannot rotate
# ---------------------------------------------------------------------------


def test_a_second_rotation_of_the_same_predecessor_is_refused(
    migrated_database, composition
):
    """TC-AUTH-16b. One successor, and the second attempt is typed rather than fatal.

    This is the sequential form of the race below: a caller holding a `record`
    resolved before the first rotation tries again afterwards. The predecessor is
    revoked and already has a successor, so the locked read matches zero rows and
    the caller is refused — no branch, and no `IntegrityError` reaching a route.
    """
    account_id, _, root = _begin_oauth_session(
        composition, migrated_database, ActorCapability.GUILD_MEMBER
    )

    with migrated_database.begin() as connection:
        services = composition.services(connection)
        stale_record = services.session_service.resolve(root.token, now=utcnow())
        services.session_service.rotate(
            record=stale_record,
            context=oauth_context(account_id, ActorCapability.GUILD_MEMBER),
            now=utcnow(),
        )

    with pytest.raises(SessionRotationRefused):
        with migrated_database.begin() as connection:
            composition.services(connection).session_service.rotate(
                record=stale_record,
                context=oauth_context(account_id, ActorCapability.GUILD_MEMBER),
                now=utcnow(),
            )

    with migrated_database.connect() as connection:
        assert len(_successors(connection, root.session_id)) == 1
        assert len(_live_sessions(connection, account_id)) == 1


def test_a_revoked_predecessor_cannot_be_rotated(migrated_database, composition):
    """TC-AUTH-16b. Liveness, which is the rule no constraint can carry.

    A logged-out or operator-revoked session must not be able to mint a successor:
    that would resurrect a session the platform has already ended, with the same
    account, capabilities and OAuth binding.
    """
    account_id, _, root = _begin_oauth_session(
        composition, migrated_database, ActorCapability.GUILD_MEMBER
    )

    with migrated_database.begin() as connection:
        services = composition.services(connection)
        record = services.session_service.resolve(root.token, now=utcnow())
        services.sessions_repository.revoke(root.session_id, reason="operator", at=utcnow())

    with pytest.raises(SessionRotationRefused):
        with migrated_database.begin() as connection:
            composition.services(connection).session_service.rotate(
                record=record,
                context=oauth_context(account_id, ActorCapability.GUILD_MEMBER),
                now=utcnow(),
            )

    with migrated_database.connect() as connection:
        assert _successors(connection, root.session_id) == []
        assert _live_sessions(connection, account_id) == []


def test_an_unknown_predecessor_cannot_be_rotated(migrated_database, composition):
    """TC-AUTH-16b. An id that names no row is a refusal, not an orphan successor."""
    with migrated_database.begin() as connection:
        account_id = make_account(connection)

    class _Absent:
        id = uuid4()
        privilege_fingerprint = b"\x00" * 32
        oauth_transaction_id = None

    with pytest.raises(SessionRotationRefused):
        with migrated_database.begin() as connection:
            composition.services(connection).session_service.rotate(
                record=_Absent(),
                context=break_glass_context(account_id),
                now=utcnow(),
            )

    with migrated_database.connect() as connection:
        assert _live_sessions(connection, account_id) == []


def test_a_rotation_into_another_account_is_refused_by_the_service(
    migrated_database, composition
):
    """TC-AUTH-16b. The caller's account is checked against the locked row.

    A context resolved for a different account cannot rotate this session. The
    composite foreign key would refuse the insert anyway — the next test proves it
    — but an `IntegrityError` at that point would surface as a `500` where a typed
    refusal belongs, and the successor would have been built from the wrong values
    before the database caught it.
    """
    account_id, _, root = _begin_oauth_session(
        composition, migrated_database, ActorCapability.GUILD_MEMBER
    )
    with migrated_database.begin() as connection:
        other_account_id = make_account(connection)

    with migrated_database.begin() as connection:
        services = composition.services(connection)
        record = services.session_service.resolve(root.token, now=utcnow())

    with pytest.raises(SessionRotationRefused):
        with migrated_database.begin() as connection:
            composition.services(connection).session_service.rotate(
                record=record,
                context=oauth_context(other_account_id, ActorCapability.GUILD_MEMBER),
                now=utcnow(),
            )

    with migrated_database.connect() as connection:
        assert _successors(connection, root.session_id) == []
        assert _live_sessions(connection, other_account_id) == []
        # And the predecessor is untouched: a refused rotation revokes nothing.
        assert _row(connection, root.session_id)["revoked_at"] is None


def test_a_rotation_into_another_authentication_method_is_refused_by_the_service(
    migrated_database, composition
):
    """TC-AUTH-16b. A Discord session cannot become a break-glass one, or the reverse.

    Authentication method decides the session's bounds (N-15 against N-06/N-07)
    and its capability scope, so a rotation that changed it would be a privilege
    transition disguised as a refresh.
    """
    account_id, _, root = _begin_oauth_session(
        composition, migrated_database, ActorCapability.GUILD_MEMBER
    )

    with migrated_database.begin() as connection:
        services = composition.services(connection)
        record = services.session_service.resolve(root.token, now=utcnow())

    with pytest.raises(SessionRotationRefused):
        with migrated_database.begin() as connection:
            composition.services(connection).session_service.rotate(
                record=record,
                context=break_glass_context(account_id),
                now=utcnow(),
            )

    with migrated_database.connect() as connection:
        assert _successors(connection, root.session_id) == []
        assert _row(connection, root.session_id)["revoked_at"] is None


# ---------------------------------------------------------------------------
# TC-AUTH-16c — the database, with the application bypassed entirely
# ---------------------------------------------------------------------------


def test_the_database_refuses_a_second_successor_for_one_session(
    migrated_database, composition
):
    """TC-AUTH-16c. `uq_sessions_rotated_from_session_id`: no branch, ever.

    Two live descendants of one login would each carry the same OAuth binding and
    each be a valid credential, which is exactly what the completion binding
    exists to make impossible.
    """
    _, transaction_id, root = _begin_oauth_session(
        composition, migrated_database, ActorCapability.GUILD_MEMBER
    )
    with migrated_database.connect() as connection:
        account_id = _row(connection, root.session_id)["platform_account_id"]

    with migrated_database.begin() as connection:
        _insert_session(
            connection,
            account_id=account_id,
            auth_method="discord_oauth",
            oauth_transaction_id=transaction_id,
            rotated_from=root.session_id,
        )

    with pytest.raises(IntegrityError, match="uq_sessions_rotated_from_session_id"):
        with migrated_database.begin() as connection:
            _insert_session(
                connection,
                account_id=account_id,
                auth_method="discord_oauth",
                oauth_transaction_id=transaction_id,
                rotated_from=root.session_id,
            )


def test_the_database_refuses_a_rotation_that_changes_account(
    migrated_database, composition
):
    """TC-AUTH-16c. `fk_sessions_rotation_account_method`, on the account column."""
    _, transaction_id, root = _begin_oauth_session(
        composition, migrated_database, ActorCapability.GUILD_MEMBER
    )

    with pytest.raises(IntegrityError, match="fk_sessions_rotation_account_method"):
        with migrated_database.begin() as connection:
            other_account_id = make_account(connection)
            _insert_session(
                connection,
                account_id=other_account_id,
                auth_method="discord_oauth",
                oauth_transaction_id=transaction_id,
                rotated_from=root.session_id,
            )


def test_the_database_refuses_a_rotation_that_changes_authentication_method(
    migrated_database, composition
):
    """TC-AUTH-16c. The same key, on the method column.

    The successor also has to drop the transaction id to satisfy
    `ck_sessions_oauth_transaction_binding`, which is what makes this the exact
    escape a `discord_oauth` chain would attempt: shed the binding by changing
    method. The account-and-method key refuses it, so the pair of constraints
    closes on both sides.
    """
    _, _, root = _begin_oauth_session(
        composition, migrated_database, ActorCapability.GUILD_MEMBER
    )
    with migrated_database.connect() as connection:
        account_id = _row(connection, root.session_id)["platform_account_id"]

    with pytest.raises(IntegrityError, match="fk_sessions_rotation_account_method"):
        with migrated_database.begin() as connection:
            _insert_session(
                connection,
                account_id=account_id,
                auth_method="webauthn",
                oauth_transaction_id=None,
                rotated_from=root.session_id,
            )


def test_the_database_refuses_a_rotation_that_changes_the_oauth_binding(
    migrated_database, composition
):
    """TC-AUTH-16c. `fk_sessions_rotation_oauth_binding`: the login cannot change.

    A rotation that named a different transaction would be a session attesting a
    login it does not descend from, and — because rotated rows are outside the
    root-session unique index — it would do so without meeting that index at all.
    """
    _, _, root = _begin_oauth_session(
        composition, migrated_database, ActorCapability.GUILD_MEMBER
    )
    with migrated_database.connect() as connection:
        account_id = _row(connection, root.session_id)["platform_account_id"]

    with pytest.raises(IntegrityError, match="fk_sessions_rotation_oauth_binding"):
        with migrated_database.begin() as connection:
            other_transaction_id = seed_oauth_transaction(connection, claimed=True)
            _insert_session(
                connection,
                account_id=account_id,
                auth_method="discord_oauth",
                oauth_transaction_id=other_transaction_id,
                rotated_from=root.session_id,
            )


def test_a_row_cannot_be_labelled_a_rotation_to_reuse_another_logins_transaction(
    migrated_database, composition
):
    """TC-AUTH-16c. The evasion the partial index would otherwise permit.

    The root-session unique index only sees rows with
    `rotated_from_session_id IS NULL`. So the way to obtain a second session for
    an already-completed transaction is to *call the row a rotation* — of any
    session at all, including one belonging to a different login. The binding
    foreign key refuses it: a rotation's transaction id must be the one its named
    predecessor carries, and the unrelated session carries a different one.
    """
    _, first_transaction_id, first_root = _begin_oauth_session(
        composition, migrated_database, ActorCapability.GUILD_MEMBER
    )
    _, _, second_root = _begin_oauth_session(
        composition, migrated_database, ActorCapability.GUILD_MEMBER
    )
    with migrated_database.connect() as connection:
        second_account_id = _row(connection, second_root.session_id)[
            "platform_account_id"
        ]

    with pytest.raises(IntegrityError, match="fk_sessions_rotation_oauth_binding"):
        with migrated_database.begin() as connection:
            _insert_session(
                connection,
                account_id=second_account_id,
                auth_method="discord_oauth",
                # The first login's transaction, on a row claiming to descend from
                # the second login's session.
                oauth_transaction_id=first_transaction_id,
                rotated_from=second_root.session_id,
            )
    # And the direct route — a second *root* for that transaction — is still the
    # completion binding's own unique index.
    with pytest.raises(IntegrityError, match="uq_sessions_oauth_transaction_id"):
        with migrated_database.begin() as connection:
            _insert_session(
                connection,
                account_id=second_account_id,
                auth_method="discord_oauth",
                oauth_transaction_id=first_transaction_id,
            )


def test_the_database_refuses_a_rotation_of_a_session_that_does_not_exist(
    migrated_database, composition
):
    """TC-AUTH-16c. A predecessor reference must name a row, not a plausible UUID.

    Refused by the single-column `rotated_from_session_id` key that predates
    OD-44 — it is evaluated first, and it is the narrower statement of the same
    fact. The composite keys below it add *equality* with the predecessor; they
    were never the ones establishing that a predecessor exists.
    """
    with pytest.raises(
        IntegrityError, match="fk_sessions_rotated_from_session_id_sessions"
    ):
        with migrated_database.begin() as connection:
            account_id = make_account(connection)
            _insert_session(
                connection,
                account_id=account_id,
                auth_method="webauthn",
                oauth_transaction_id=None,
                rotated_from=uuid4(),
            )


# ---------------------------------------------------------------------------
# TC-AUTH-16d — the race, against real PostgreSQL
# ---------------------------------------------------------------------------


def test_two_concurrent_rotations_produce_one_successor_and_one_refusal(
    database_url, migrated_database, composition
):
    """TC-AUTH-16d. Two connections, a barrier rendezvous, and no sleep anywhere.

    Both transactions try to rotate the same live session. The winner takes the
    row lock in its `SELECT … FOR UPDATE`, inserts its successor and revokes the
    predecessor. The loser blocks on that lock, re-evaluates `revoked_at IS NULL`
    under `READ COMMITTED` when the winner commits, matches zero rows and is
    refused. The outcome is decided by PostgreSQL rather than by which thread the
    scheduler happened to run first, and the assertion that matters is the last
    one: one live session, not two.
    """
    account_id, transaction_id, root = _begin_oauth_session(
        composition, migrated_database, ActorCapability.GUILD_MEMBER
    )
    with migrated_database.begin() as connection:
        record = composition.services(connection).session_service.resolve(
            root.token, now=utcnow()
        )

    other = create_engine(database_url)
    barrier = threading.Barrier(2)
    outcomes: list[str] = []
    lock = threading.Lock()

    def rotate(engine):
        try:
            with engine.begin() as connection:
                barrier.wait(timeout=30)
                composition.services(connection).session_service.rotate(
                    record=record,
                    context=oauth_context(
                        account_id,
                        ActorCapability.GUILD_MEMBER,
                        ActorCapability.GUILD_COUNCIL,
                    ),
                    now=utcnow(),
                )
            outcome = "rotated"
        except SessionRotationRefused:
            outcome = "refused"
        with lock:
            outcomes.append(outcome)

    try:
        threads = [
            threading.Thread(target=rotate, args=(migrated_database,)),
            threading.Thread(target=rotate, args=(other,)),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30)
            assert not thread.is_alive(), "a rotation did not finish; it is deadlocked"
    finally:
        other.dispose()

    assert sorted(outcomes) == ["refused", "rotated"]

    with migrated_database.connect() as connection:
        successors = _successors(connection, root.session_id)
        live = _live_sessions(connection, account_id)
        predecessor = _row(connection, root.session_id)
    assert len(successors) == 1, "a rotation race may not branch the chain"
    assert live == successors, "exactly one live descendant, and it is the successor"
    assert predecessor["revoked_at"] is not None
    with migrated_database.connect() as connection:
        assert _row(connection, successors[0])["oauth_transaction_id"] == transaction_id


# ---------------------------------------------------------------------------
# TC-AUTH-16e — creation cannot assert a rotation
# ---------------------------------------------------------------------------


def test_no_creation_path_accepts_a_rotation_label():
    """TC-AUTH-16e. `rotated_from_session_id` is written by `rotate()` and nothing else.

    "This row is a rotation of that one" is the label that carries an OAuth
    binding past the root-session unique index. A creation path that took it as an
    argument would be a creation path that could be told to lie, so neither
    `SessionRepository.create` nor `SessionService.begin` has such a parameter —
    asserted from the signatures, because a comment saying so would not fail.
    """
    forbidden = {"rotated_from", "rotated_from_session_id", "revocation_reason_for_old"}
    for callable_ in (SessionRepository.create, SessionService.begin):
        assert not forbidden & set(inspect.signature(callable_).parameters), (
            f"{callable_.__qualname__} must not accept a rotation label"
        )
    # And the one operation that does write it takes no successor values for the
    # facts it must inherit: account, method and binding come from the locked row.
    rotate_parameters = set(inspect.signature(SessionRepository.rotate).parameters)
    assert "oauth_transaction_id" not in rotate_parameters
    assert {"expected_account_id", "expected_auth_method"} <= rotate_parameters
