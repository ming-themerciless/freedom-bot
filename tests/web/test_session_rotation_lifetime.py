"""TC-AUTH-18: a rotation cannot revive an expired session or extend a login.

Codex's independent re-review of the OD-44 provider-binding remediation found
that `SessionRepository.rotate()` described its locked predecessor as *live* while
checking only `revoked_at IS NULL`. Two consequences, and both of them are here:

1. **Revival.** `revoked_at IS NULL` says only that nobody has *ended* the
   session. An idle- or absolute-expired row stays unrevoked until some read
   observes it, so a caller holding a `SessionRecord` resolved while the session
   was valid could rotate it afterwards and receive a live successor — the
   expired session back, with the same account, capabilities and OAuth binding.
   The tests for this deliberately never re-resolve the token: `resolve()`
   refusing the record first is not the control, because the record is a value
   the caller already holds.
2. **Unbounded extension.** The successor was created with
   `absolute_expires_at = now + bounds.absolute`, so each privilege-change
   rotation restarted the clock. Repeated rotations extended one login without
   limit — defeating N-07 for an ordinary session and directly violating N-15's
   "15-minute idle, 60-minute absolute expiry; rotate on login; no extension
   beyond the absolute bound" for a break-glass one. The successor now inherits
   the predecessor's absolute expiration exactly, so a chain has one absolute
   bound and the login at its root sets it.

Every timestamp here is injected. `begin()`, `resolve()` and `rotate()` all take
`now`, so an expiry is reached by advancing a value rather than by waiting, and
there is no sleep in this module.

**On the two expiry predicates.** `ck_sessions_idle_within_absolute` makes
`idle_expires_at <= absolute_expires_at` true of every row, so for any row the
database will accept, `idle_expires_at > :now` already implies
`absolute_expires_at > :now`. The absolute predicate is therefore unobservable
through ordinary rows, and a test suite that only used them would leave "delete
the absolute predicate" an equivalent mutant. One test below drops that check
constraint inside a transaction it rolls back, which is the only way to present
the locked read with a row whose idle window is live and whose absolute bound has
passed. It is not a state the application can reach today; it is what the
absolute predicate exists to refuse if a later migration ever relaxes the clamp.
"""
from __future__ import annotations

import inspect
import threading
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, select, text

from adapters.database.tables import audit_events, sessions
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

#: N-06/N-07 for an ordinary session and N-15 for a break-glass one, as the test
#: environment configures them. Named rather than inlined so a policy change
#: shows up as one edit and not as a hunt through arithmetic.
ORDINARY_IDLE = timedelta(minutes=60)
ORDINARY_ABSOLUTE = timedelta(hours=12)
EMERGENCY_IDLE = timedelta(minutes=15)
EMERGENCY_ABSOLUTE = timedelta(minutes=60)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def oauth_context(account_id: UUID, *capabilities) -> WebAuthorizationContext:
    return WebAuthorizationContext(
        account_id=account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        capabilities=frozenset(capabilities or (ActorCapability.GUILD_MEMBER,)),
        administrator_scope=AdministratorScope.FULL,
        membership=MembershipProjection(
            guild_id=TEST_GUILD_ID,
            is_member=True,
            role_ids=frozenset(),
            observed_at=utcnow(),
        ),
    )


def break_glass_context(
    account_id: UUID,
    *capabilities,
    auth_method: AuthMethod = AuthMethod.WEBAUTHN,
) -> WebAuthorizationContext:
    return WebAuthorizationContext(
        account_id=account_id,
        auth_method=auth_method,
        capabilities=frozenset(
            capabilities or (ActorCapability.PLATFORM_ADMINISTRATOR,)
        ),
        administrator_scope=AdministratorScope.EMERGENCY_CONTINUITY,
        membership=None,
    )


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


def _rotation_audits(connection) -> list[str]:
    return list(
        connection.execute(
            select(audit_events.c.entity_id).where(
                audit_events.c.action == "auth.session.rotated"
            )
        ).scalars()
    )


def _begin_oauth_session(composition, migrated_database, *, at: datetime):
    """A root Discord OAuth session created at an injected instant."""
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        transaction_id = seed_oauth_transaction(connection, claimed=True)
        issued = composition.services(connection).session_service.begin(
            context=oauth_context(account_id),
            now=at,
            correlation_id=uuid4(),
            oauth_transaction_id=transaction_id,
        )
    return account_id, transaction_id, issued


def _begin_break_glass_session(
    composition, migrated_database, *, at: datetime, auth_method: AuthMethod
):
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        issued = composition.services(connection).session_service.begin(
            context=break_glass_context(account_id, auth_method=auth_method),
            now=at,
            correlation_id=uuid4(),
        )
    return account_id, issued


def _stale_record(composition, migrated_database, token: str, *, at: datetime):
    """Resolve while the session is still valid, and keep the result.

    This is the whole shape of the defect: the caller obtains a legitimate record
    and then uses it later. Nothing re-resolves it in between, because a caller
    that re-resolved would be relying on `resolve()` rather than on the operation
    under test.
    """
    with migrated_database.begin() as connection:
        return composition.services(connection).session_service.resolve(token, now=at)


def _assert_refused_and_untouched(migrated_database, predecessor_id: UUID, before):
    """A refusal creates nothing, rewrites nothing and records nothing."""
    with migrated_database.connect() as connection:
        after = _row(connection, predecessor_id)
        assert _successors(connection, predecessor_id) == [], (
            "a refused rotation must not create a successor"
        )
        assert _rotation_audits(connection) == [], (
            "a refused rotation must not write a rotation audit event"
        )
    # Terminal data specifically: a refused rotation must not revoke a row it
    # declined to rotate, and must not overwrite a revocation already recorded.
    assert after["revoked_at"] == before["revoked_at"]
    assert after["revocation_reason"] == before["revocation_reason"]
    assert after["idle_expires_at"] == before["idle_expires_at"]
    assert after["absolute_expires_at"] == before["absolute_expires_at"]


# ---------------------------------------------------------------------------
# TC-AUTH-18a — an expired predecessor cannot be rotated from a stale record
# ---------------------------------------------------------------------------


def test_an_idle_expired_oauth_predecessor_cannot_be_rotated_from_a_stale_record(
    migrated_database, composition
):
    """TC-AUTH-18a. Sixty-one minutes after a login whose idle window is sixty.

    The row is not revoked — nothing has read it since it expired — so
    `revoked_at IS NULL` is still true of it. That is exactly why the predicate
    was insufficient.
    """
    start = utcnow()
    account_id, _, root = _begin_oauth_session(
        composition, migrated_database, at=start
    )
    record = _stale_record(composition, migrated_database, root.token, at=start)
    with migrated_database.connect() as connection:
        before = _row(connection, root.session_id)
    assert before["revoked_at"] is None, "the premise: an expired but unrevoked row"

    with pytest.raises(SessionRotationRefused):
        with migrated_database.begin() as connection:
            composition.services(connection).session_service.rotate(
                record=record,
                context=oauth_context(account_id),
                now=start + ORDINARY_IDLE + timedelta(minutes=1),
            )

    _assert_refused_and_untouched(migrated_database, root.session_id, before)


def test_an_absolute_expired_oauth_predecessor_cannot_be_rotated_from_a_stale_record(
    migrated_database, composition
):
    """TC-AUTH-18a. Past N-07's twelve hours, which no refresh can move."""
    start = utcnow()
    account_id, _, root = _begin_oauth_session(
        composition, migrated_database, at=start
    )
    record = _stale_record(composition, migrated_database, root.token, at=start)
    with migrated_database.connect() as connection:
        before = _row(connection, root.session_id)

    with pytest.raises(SessionRotationRefused):
        with migrated_database.begin() as connection:
            composition.services(connection).session_service.rotate(
                record=record,
                context=oauth_context(account_id),
                now=start + ORDINARY_ABSOLUTE + timedelta(minutes=1),
            )

    _assert_refused_and_untouched(migrated_database, root.session_id, before)


def test_an_idle_expired_break_glass_predecessor_cannot_be_rotated(
    migrated_database, composition
):
    """TC-AUTH-18a. N-15's fifteen minutes, on the session type it matters most for.

    A break-glass session is an emergency, not a way of working. Reviving one
    sixteen minutes later would hand back `platform_administrator` under
    emergency-continuity scope on the strength of a record the operator still had
    in hand.
    """
    start = utcnow()
    account_id, root = _begin_break_glass_session(
        composition, migrated_database, at=start, auth_method=AuthMethod.WEBAUTHN
    )
    record = _stale_record(composition, migrated_database, root.token, at=start)
    with migrated_database.connect() as connection:
        before = _row(connection, root.session_id)

    with pytest.raises(SessionRotationRefused):
        with migrated_database.begin() as connection:
            composition.services(connection).session_service.rotate(
                record=record,
                context=break_glass_context(account_id),
                now=start + EMERGENCY_IDLE + timedelta(minutes=1),
            )

    _assert_refused_and_untouched(migrated_database, root.session_id, before)


def test_an_absolute_expired_webauthn_predecessor_cannot_be_rotated(
    migrated_database, composition
):
    """TC-AUTH-18a. N-15's sixty-minute absolute bound, WebAuthn."""
    start = utcnow()
    account_id, root = _begin_break_glass_session(
        composition, migrated_database, at=start, auth_method=AuthMethod.WEBAUTHN
    )
    record = _stale_record(composition, migrated_database, root.token, at=start)
    with migrated_database.connect() as connection:
        before = _row(connection, root.session_id)

    with pytest.raises(SessionRotationRefused):
        with migrated_database.begin() as connection:
            composition.services(connection).session_service.rotate(
                record=record,
                context=break_glass_context(account_id),
                now=start + EMERGENCY_ABSOLUTE + timedelta(minutes=1),
            )

    _assert_refused_and_untouched(migrated_database, root.session_id, before)


def test_an_absolute_expired_recovery_grant_predecessor_cannot_be_rotated(
    migrated_database, composition
):
    """TC-AUTH-18a. The same bound on the other break-glass method.

    `recovery_grant` is tested separately from `webauthn` rather than assumed to
    behave the same way: they are distinct `auth_method` values, and the bounds
    are selected by `AuthMethod.is_break_glass` rather than by an equality.
    """
    start = utcnow()
    account_id, root = _begin_break_glass_session(
        composition,
        migrated_database,
        at=start,
        auth_method=AuthMethod.RECOVERY_GRANT,
    )
    record = _stale_record(composition, migrated_database, root.token, at=start)
    with migrated_database.connect() as connection:
        before = _row(connection, root.session_id)

    with pytest.raises(SessionRotationRefused):
        with migrated_database.begin() as connection:
            composition.services(connection).session_service.rotate(
                record=record,
                context=break_glass_context(
                    account_id, auth_method=AuthMethod.RECOVERY_GRANT
                ),
                now=start + EMERGENCY_ABSOLUTE + timedelta(minutes=1),
            )

    _assert_refused_and_untouched(migrated_database, root.session_id, before)


def test_a_refused_rotation_does_not_rewrite_an_existing_expiry_revocation(
    migrated_database, composition
):
    """TC-AUTH-18a. The predecessor's terminal data survives the refusal intact.

    Here the row *has* been observed after expiry, so `resolve()` marked it
    `expired`. A rotation arriving afterwards with the stale record must leave
    that record of *why* the session ended alone: rewriting it to
    `privilege_change` would make an expired session look like a rotated one in
    exactly the history an incident investigation reads.
    """
    start = utcnow()
    account_id, _, root = _begin_oauth_session(
        composition, migrated_database, at=start
    )
    record = _stale_record(composition, migrated_database, root.token, at=start)

    expired_at = start + ORDINARY_IDLE + timedelta(minutes=1)
    with migrated_database.begin() as connection:
        assert (
            composition.services(connection).session_service.resolve(
                root.token, now=expired_at
            )
            is None
        )
    with migrated_database.connect() as connection:
        before = _row(connection, root.session_id)
    assert before["revocation_reason"] == "expired"

    with pytest.raises(SessionRotationRefused):
        with migrated_database.begin() as connection:
            composition.services(connection).session_service.rotate(
                record=record,
                context=oauth_context(account_id),
                now=expired_at,
                reason="privilege_change",
            )

    _assert_refused_and_untouched(migrated_database, root.session_id, before)


def test_a_refused_rotation_through_the_n08_path_writes_no_audit_event(
    migrated_database, composition
):
    """TC-AUTH-18a. The route N-08 will actually take, and its audit consequence.

    `rotate_if_privileges_changed` records `auth.session.rotated` *after* the
    rotation succeeds. The refusal has to reach the caller as an exception rather
    than as a `None`, or the audit would describe a rotation that did not happen —
    and `None` already means "nothing changed" on this method.
    """
    start = utcnow()
    account_id, _, root = _begin_oauth_session(
        composition, migrated_database, at=start
    )
    record = _stale_record(composition, migrated_database, root.token, at=start)
    with migrated_database.connect() as connection:
        before = _row(connection, root.session_id)

    with pytest.raises(SessionRotationRefused):
        with migrated_database.begin() as connection:
            composition.services(connection).session_service.rotate_if_privileges_changed(
                record=record,
                context=oauth_context(
                    account_id,
                    ActorCapability.GUILD_MEMBER,
                    ActorCapability.GUILD_COUNCIL,
                ),
                now=start + ORDINARY_IDLE + timedelta(minutes=1),
                correlation_id=uuid4(),
            )

    _assert_refused_and_untouched(migrated_database, root.session_id, before)


# ---------------------------------------------------------------------------
# TC-AUTH-18b — one chain, one absolute bound, set by the login at its root
# ---------------------------------------------------------------------------


def test_a_multi_generation_oauth_chain_keeps_the_root_absolute_bound(
    migrated_database, composition
):
    """TC-AUTH-18b. Three generations, one absolute expiration, idle clamped to it.

    Each rotation happens while the predecessor is comfortably live, so nothing
    here is about refusal: it is about what the successor is *given*. If the
    successor took `now + bounds.absolute`, the third row would end nearly three
    hours later than the first, which is the extension the finding describes.
    """
    start = utcnow()
    account_id, transaction_id, root = _begin_oauth_session(
        composition, migrated_database, at=start
    )
    root_absolute = root.absolute_expires_at
    assert root_absolute == start + ORDINARY_ABSOLUTE

    # Each rotation happens inside the previous row's idle window — 50, 100 and
    # 150 minutes against windows that close at 60, 110 and 160 — so the chain is
    # built by rotating live sessions, which is the only way to reach generation
    # three at all.
    issued = [root]
    for offset, capabilities in (
        (timedelta(minutes=50), (ActorCapability.GUILD_MEMBER, ActorCapability.GUILD_COUNCIL)),
        (timedelta(minutes=100), (ActorCapability.GUILD_MEMBER,)),
        (timedelta(minutes=150), (ActorCapability.PLATFORM_ADMINISTRATOR,)),
    ):
        at = start + offset
        with migrated_database.begin() as connection:
            services = composition.services(connection)
            record = services.session_service.resolve(issued[-1].token, now=at)
            assert record is not None, "the predecessor must still be live to rotate"
            successor = services.session_service.rotate(
                record=record,
                context=oauth_context(account_id, *capabilities),
                now=at,
                reason="privilege_change",
            )
        assert successor.absolute_expires_at == root_absolute, (
            "a rotation may not extend the login's absolute bound"
        )
        assert successor.idle_expires_at == min(at + ORDINARY_IDLE, root_absolute)
        issued.append(successor)

    with migrated_database.connect() as connection:
        rows = [_row(connection, session.session_id) for session in issued]

    # Every row in the chain, including the root, ends at the same instant — and
    # the reported bounds are the persisted ones, not the ones the service
    # proposed.
    assert [row["absolute_expires_at"] for row in rows] == [root_absolute] * 4
    for session, row in zip(issued, rows):
        assert row["idle_expires_at"] == session.idle_expires_at
        assert row["absolute_expires_at"] == session.absolute_expires_at
        assert row["idle_expires_at"] <= row["absolute_expires_at"]
    assert [row["oauth_transaction_id"] for row in rows] == [transaction_id] * 4
    assert [row["revoked_at"] is None for row in rows] == [False, False, False, True]


@pytest.mark.parametrize(
    "auth_method", [AuthMethod.WEBAUTHN, AuthMethod.RECOVERY_GRANT]
)
def test_a_break_glass_rotation_keeps_its_root_bound_and_names_no_transaction(
    migrated_database, composition, auth_method
):
    """TC-AUTH-18b. N-15 in full: sixty minutes from the login, whatever happens.

    The `oauth_transaction_id` assertion travels with this one because the two
    properties are inherited by the same statement from the same locked row: a
    successor that took a fresh absolute bound would be a successor built from
    somewhere other than its predecessor, and this is the cheapest place to say
    that the OAuth-free chains stayed OAuth-free while the lifetime was fixed.
    """
    start = utcnow()
    account_id, root = _begin_break_glass_session(
        composition, migrated_database, at=start, auth_method=auth_method
    )
    assert root.absolute_expires_at == start + EMERGENCY_ABSOLUTE

    at = start + timedelta(minutes=10)
    with migrated_database.begin() as connection:
        services = composition.services(connection)
        record = services.session_service.resolve(root.token, now=at)
        successor = services.session_service.rotate(
            record=record,
            context=break_glass_context(account_id, auth_method=auth_method),
            now=at,
        )

    assert successor.absolute_expires_at == root.absolute_expires_at
    assert successor.idle_expires_at == at + EMERGENCY_IDLE

    with migrated_database.connect() as connection:
        row = _row(connection, successor.session_id)
    assert row["absolute_expires_at"] == root.absolute_expires_at
    assert row["idle_expires_at"] == successor.idle_expires_at
    assert row["oauth_transaction_id"] is None
    assert row["auth_method"] == auth_method.value
    assert row["rotated_from_session_id"] == root.session_id


def test_a_rotation_at_the_absolute_boundary_cannot_reach_past_it(
    migrated_database, composition
):
    """TC-AUTH-18b. One minute before the bound, and then the bound holds.

    The successor's idle window would run to 74 minutes if it were not clamped to
    the inherited absolute expiration. It is clamped to 60, and one minute after
    that instant the successor cannot itself be rotated — which is the assertion
    that closes the loop: no sequence of rotations reaches past the bound the
    login set.
    """
    start = utcnow()
    account_id, root = _begin_break_glass_session(
        composition, migrated_database, at=start, auth_method=AuthMethod.WEBAUTHN
    )
    boundary = start + EMERGENCY_ABSOLUTE
    just_before = boundary - timedelta(minutes=1)

    # Ordinary requests refresh the idle window, and the clamp holds it to the
    # absolute bound — so the session is still live one minute before the
    # boundary, which is the state this test needs to rotate from.
    #
    # Each refresh gives this WebAuthn session N-15's fifteen minutes, not
    # N-06's sixty (corrected 2026-08-15: the setup previously took one
    # sixty-minute touch, which reached the boundary only by violating N-15).
    # Staying live for fifty-nine minutes therefore takes a *sequence* of
    # refreshes, each inside the window the last one opened — which is the
    # honest shape of the request traffic this test stands in for, and it
    # additionally shows that repeated refreshes converge on the bound instead
    # of passing it.
    for minutes in (10, 20, 30, 40, 50):
        with migrated_database.begin() as connection:
            services = composition.services(connection)
            at = start + timedelta(minutes=minutes)
            refreshed = services.session_service.touch(
                services.session_service.resolve(root.token, now=at), now=at
            )
            assert refreshed.absolute_expires_at == boundary, (
                "no refresh moves the absolute bound the login set"
            )
    with migrated_database.connect() as connection:
        assert _row(connection, root.session_id)["idle_expires_at"] == boundary

    with migrated_database.begin() as connection:
        services = composition.services(connection)
        record = services.session_service.resolve(root.token, now=just_before)
        successor = services.session_service.rotate(
            record=record, context=break_glass_context(account_id), now=just_before
        )
    assert successor.absolute_expires_at == boundary
    assert successor.idle_expires_at == boundary, (
        "the successor's idle window is clamped to the inherited absolute bound"
    )

    stale = _stale_record(composition, migrated_database, successor.token, at=just_before)
    with pytest.raises(SessionRotationRefused):
        with migrated_database.begin() as connection:
            composition.services(connection).session_service.rotate(
                record=stale,
                context=break_glass_context(account_id),
                now=boundary + timedelta(seconds=1),
            )

    with migrated_database.connect() as connection:
        assert _successors(connection, successor.session_id) == []


# ---------------------------------------------------------------------------
# TC-AUTH-18c — the absolute predicate, made observable
# ---------------------------------------------------------------------------


def test_the_absolute_predicate_refuses_a_row_whose_idle_window_outlives_it(
    migrated_database, composition
):
    """TC-AUTH-18c. Defense in depth, proved by removing the depth for one transaction.

    `ck_sessions_idle_within_absolute` means no row the database accepts can have
    a live idle window and a passed absolute bound, so the absolute predicate in
    the locked read cannot be reached through the application. That makes it
    untestable *and* unfalsifiable, which is the same thing as untested. So this
    test drops the constraint, builds the row the constraint forbids, and rolls
    the whole transaction back — schema included, because PostgreSQL DDL is
    transactional. Nothing outside this transaction ever sees either the missing
    constraint or the row.

    What it establishes: if a later migration ever relaxes the clamp, or an
    unclamped write path appears, the absolute bound is still enforced at the one
    operation that decides whether a session may continue.
    """
    start = utcnow()
    account_id, _, root = _begin_oauth_session(
        composition, migrated_database, at=start
    )
    record = _stale_record(composition, migrated_database, root.token, at=start)
    # An absolute bound five minutes out, an idle window two hours out, and a
    # rotation ten minutes in: the only combination that isolates the absolute
    # predicate. `ck_sessions_absolute_after_creation` still holds, so the row is
    # otherwise exactly what the schema expects.
    at = start + timedelta(minutes=10)

    with migrated_database.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(
                text(
                    "ALTER TABLE sessions "
                    "DROP CONSTRAINT ck_sessions_idle_within_absolute"
                )
            )
            connection.execute(
                sessions.update()
                .where(sessions.c.id == root.session_id)
                .values(
                    idle_expires_at=start + timedelta(hours=2),
                    absolute_expires_at=start + timedelta(minutes=5),
                )
            )
            with pytest.raises(SessionRotationRefused):
                composition.services(connection).session_service.rotate(
                    record=record, context=oauth_context(account_id), now=at
                )
            assert _successors(connection, root.session_id) == []
        finally:
            transaction.rollback()

    # The constraint is back, and so is the row: the test bought its evidence
    # without leaving anything behind for the next one to trip over.
    with migrated_database.connect() as connection:
        constraint = connection.execute(
            text(
                "SELECT conname FROM pg_constraint "
                "WHERE conname = 'ck_sessions_idle_within_absolute'"
            )
        ).scalar_one_or_none()
        assert constraint == "ck_sessions_idle_within_absolute"
        assert _row(connection, root.session_id)["absolute_expires_at"] == (
            start + ORDINARY_ABSOLUTE
        )


# ---------------------------------------------------------------------------
# TC-AUTH-18d — concurrency, against real PostgreSQL
# ---------------------------------------------------------------------------


def test_concurrent_rotation_still_produces_one_winner_and_one_typed_refusal(
    database_url, migrated_database, composition
):
    """TC-AUTH-18d. The added predicates did not cost the one-successor property.

    Two connections rotate one live session at the same injected instant. The
    loser blocks on the winner's row lock, re-evaluates under `READ COMMITTED`
    when the winner commits, and is refused — and the survivor still carries the
    root's absolute bound rather than a bound set by whichever thread won.
    """
    start = utcnow()
    account_id, _, root = _begin_oauth_session(
        composition, migrated_database, at=start
    )
    at = start + timedelta(minutes=30)
    record = _stale_record(composition, migrated_database, root.token, at=at)

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
                    now=at,
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
        assert len(successors) == 1, "a rotation race may not branch the chain"
        successor = _row(connection, successors[0])
    assert successor["absolute_expires_at"] == root.absolute_expires_at
    assert successor["idle_expires_at"] == at + ORDINARY_IDLE


# ---------------------------------------------------------------------------
# TC-AUTH-18e — the absolute bound is not a caller's to state
# ---------------------------------------------------------------------------


def test_no_rotation_path_accepts_an_absolute_expiration():
    """TC-AUTH-18e. Asserted from the signatures, because a comment would not fail.

    The successor's absolute expiration is derivable from the locked predecessor,
    so a parameter for it would be a way to say something the repository already
    knows better — and the only thing a caller could add by supplying one is a
    later value. `begin()` still takes bounds, because a root session has no
    predecessor to inherit from; that is the distinction the two paths exist to
    keep.
    """
    for callable_ in (SessionRepository.rotate, SessionService.rotate):
        parameters = set(inspect.signature(callable_).parameters)
        assert "absolute_expires_at" not in parameters, (
            f"{callable_.__qualname__} must derive the absolute bound from the "
            "predecessor, not accept one"
        )
    # And the idle window still is a caller's to propose, because it is measured
    # from the rotation rather than inherited — it is merely clamped.
    assert "idle_expires_at" in set(
        inspect.signature(SessionRepository.rotate).parameters
    )
