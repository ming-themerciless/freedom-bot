"""TC-SESS-01 to TC-SESS-10: creation, rotation, expiry, revocation, CSRF.

The through-line: **nothing about a session's authority is read back from the
session row.** Expiry is evaluated server-side on every request, the privilege
fingerprint is recomputed from a fresh capability resolution, and the CSRF token
is derived rather than stored. A test that passed by reading a cached value back
would prove only that the cache is consistent with itself.
"""
from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select, text

from adapters.database.tables import audit_events, oauth_token_grants, sessions
from application.audit import ActorCapability
from application.web import csrf
from application.web.capabilities import (
    AdministratorScope,
    AuthMethod,
    MembershipProjection,
    WebAuthorizationContext,
)
from application.web.crypto import token_hash
from tests.web.conftest import (
    link_discord,
    make_account,
    seed_membership,
    seed_oauth_transaction,
    utcnow,
)
from tests.web_fixtures import TEST_GUILD_ID

pytestmark = pytest.mark.database


def _context(account_id, *, capabilities=(ActorCapability.GUILD_MEMBER,), scope=AdministratorScope.FULL):
    return WebAuthorizationContext(
        account_id=account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        capabilities=frozenset(capabilities),
        administrator_scope=scope,
        membership=MembershipProjection(
            guild_id=TEST_GUILD_ID,
            is_member=True,
            role_ids=frozenset(),
            observed_at=utcnow(),
        ),
    )


# ---------------------------------------------------------------------------
# TC-SESS-01
# ---------------------------------------------------------------------------


def test_the_cookie_value_is_not_the_session_id_and_the_row_holds_its_hash(
    migrated_database, composition
):
    """TC-SESS-01. A database read yields nothing a browser could present."""
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        services = composition.services(connection)
        issued = services.session_service.begin(
            context=_context(account_id),
            now=utcnow(),
            correlation_id=uuid4(),
            oauth_transaction_id=seed_oauth_transaction(connection),
        )

    assert issued.token != str(issued.session_id)
    with migrated_database.connect() as connection:
        row = connection.execute(
            select(sessions).where(sessions.c.id == issued.session_id)
        ).mappings().one()
    assert bytes(row["token_hash"]) == token_hash(issued.token)
    assert issued.token not in str(dict(row))


# ---------------------------------------------------------------------------
# TC-SESS-02, TC-SESS-03
# ---------------------------------------------------------------------------


def test_a_detected_capability_change_rotates_and_revokes_the_old_row(
    migrated_database, composition
):
    """TC-SESS-03. Insert + revoke, never an in-place id change.

    Also proves the rotation *chain* is auditable: the new row names the old one,
    so an investigation can follow a session back to the login that started it.
    """
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        services = composition.services(connection)
        original = services.session_service.begin(
            context=_context(account_id),
            now=utcnow(),
            correlation_id=uuid4(),
            oauth_transaction_id=seed_oauth_transaction(connection),
        )

    promoted = _context(
        account_id,
        capabilities=(ActorCapability.GUILD_MEMBER, ActorCapability.GUILD_COUNCIL),
    )
    with migrated_database.begin() as connection:
        services = composition.services(connection)
        record = services.session_service.resolve(original.token, now=utcnow())
        rotated = services.session_service.rotate_if_privileges_changed(
            record=record, context=promoted, now=utcnow(), correlation_id=uuid4()
        )

    assert rotated is not None
    assert rotated.session_id != original.session_id
    assert rotated.token != original.token

    with migrated_database.connect() as connection:
        old = connection.execute(
            select(sessions).where(sessions.c.id == original.session_id)
        ).mappings().one()
        new = connection.execute(
            select(sessions).where(sessions.c.id == rotated.session_id)
        ).mappings().one()
    assert old["revoked_at"] is not None
    assert old["revocation_reason"] == "privilege_change"
    assert new["rotated_from_session_id"] == original.session_id

    # The pre-rotation cookie is dead immediately, not merely eventually.
    with migrated_database.begin() as connection:
        assert (
            composition.services(connection).session_service.resolve(
                original.token, now=utcnow()
            )
            is None
        )


def test_an_unchanged_fingerprint_does_not_rotate(migrated_database, composition):
    """The other half of N-08: rotation is idempotent per request.

    Without this, every request would mint a session and the table would grow
    once per page view.
    """
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        services = composition.services(connection)
        issued = services.session_service.begin(
            context=_context(account_id),
            now=utcnow(),
            correlation_id=uuid4(),
            oauth_transaction_id=seed_oauth_transaction(connection),
        )
    with migrated_database.begin() as connection:
        services = composition.services(connection)
        record = services.session_service.resolve(issued.token, now=utcnow())
        assert (
            services.session_service.rotate_if_privileges_changed(
                record=record,
                context=_context(account_id),
                now=utcnow(),
                correlation_id=uuid4(),
            )
            is None
        )


# ---------------------------------------------------------------------------
# TC-SESS-04
# ---------------------------------------------------------------------------


def test_idle_and_absolute_expiry_both_refuse_and_neither_can_be_extended(
    migrated_database, composition
):
    """TC-SESS-04. An idle refresh never extends past the absolute bound."""
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        services = composition.services(connection)
        issued = services.session_service.begin(
            context=_context(account_id),
            now=utcnow(),
            correlation_id=uuid4(),
            oauth_transaction_id=seed_oauth_transaction(connection),
        )

    # Idle expiry.
    with migrated_database.begin() as connection:
        services = composition.services(connection)
        assert (
            services.session_service.resolve(
                issued.token, now=utcnow() + timedelta(minutes=61)
            )
            is None
        )

    # A fresh session, refreshed repeatedly, still dies at the absolute bound.
    with migrated_database.begin() as connection:
        services = composition.services(connection)
        second = services.session_service.begin(
            context=_context(account_id),
            now=utcnow(),
            correlation_id=uuid4(),
            oauth_transaction_id=seed_oauth_transaction(connection),
        )
    for offset in (30, 60, 90):
        with migrated_database.begin() as connection:
            services = composition.services(connection)
            record = services.session_service.resolve(
                second.token, now=utcnow() + timedelta(minutes=offset)
            )
            assert record is not None
            services.session_service.touch(
                record, now=utcnow() + timedelta(minutes=offset)
            )

    with migrated_database.connect() as connection:
        row = connection.execute(
            select(sessions).where(sessions.c.id == second.session_id)
        ).mappings().one()
    assert row["idle_expires_at"] <= row["absolute_expires_at"]

    with migrated_database.begin() as connection:
        assert (
            composition.services(connection).session_service.resolve(
                second.token, now=utcnow() + timedelta(hours=13)
            )
            is None
        )


def test_a_break_glass_session_carries_the_shorter_bounds(
    migrated_database, composition
):
    """N-15. Fifteen minutes idle, sixty absolute — and no extension beyond it."""
    with migrated_database.begin() as connection:
        account_id = make_account(connection, protected=True)
        services = composition.services(connection)
        issued = services.session_service.begin(
            context=WebAuthorizationContext(
                account_id=account_id,
                auth_method=AuthMethod.WEBAUTHN,
                capabilities=frozenset({ActorCapability.PLATFORM_ADMINISTRATOR}),
                administrator_scope=AdministratorScope.EMERGENCY_CONTINUITY,
                membership=None,
            ),
            now=utcnow(),
            correlation_id=uuid4(),
        )
    lifetime = issued.absolute_expires_at - utcnow()
    assert timedelta(minutes=59) < lifetime <= timedelta(minutes=60)
    assert issued.idle_expires_at - utcnow() <= timedelta(minutes=15)


# ---------------------------------------------------------------------------
# TC-SESS-05
# ---------------------------------------------------------------------------


def test_logout_revokes_the_session_and_deletes_the_stored_tokens(
    migrated_database, composition
):
    """TC-SESS-05. N-11's deletion is part of logging out, not a later sweep."""
    from application.web.crypto import token_grant_aad

    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        identity_id = link_discord(connection, account_id, 700000000000000123)
        services = composition.services(connection)
        grant_id = uuid4()
        services.tokens.replace(
            external_identity_id=identity_id,
            access=composition.envelope.seal(
                b"access", aad=token_grant_aad(grant_id, identity_id, 1)
            ),
            refresh=None,
            scopes="identify guilds.members.read",
            access_expires_at=utcnow() + timedelta(hours=1),
            grant_id=grant_id,
        )
        issued = services.session_service.begin(
            context=_context(account_id),
            now=utcnow(),
            correlation_id=uuid4(),
            oauth_transaction_id=seed_oauth_transaction(connection),
        )

    with migrated_database.begin() as connection:
        services = composition.services(connection)
        record = services.session_service.resolve(issued.token, now=utcnow())
        services.session_service.logout(
            record=record,
            account_id=account_id,
            now=utcnow(),
            correlation_id=uuid4(),
        )

    with migrated_database.connect() as connection:
        assert (
            connection.execute(select(text("count(*)")).select_from(oauth_token_grants)).scalar_one()
            == 0
        )
        actions = connection.execute(select(audit_events.c.action)).scalars().all()
    assert "auth.logout" in actions

    with migrated_database.begin() as connection:
        assert (
            composition.services(connection).session_service.resolve(
                issued.token, now=utcnow()
            )
            is None
        )


# ---------------------------------------------------------------------------
# TC-SESS-08
# ---------------------------------------------------------------------------


def test_the_eleventh_session_revokes_the_oldest_and_audits_it(
    migrated_database, composition
):
    """TC-SESS-08. N-66 bounds both the table and an undetected stolen population."""
    with migrated_database.begin() as connection:
        account_id = make_account(connection)

    tokens = []
    for index in range(10):
        with migrated_database.begin() as connection:
            services = composition.services(connection)
            tokens.append(
                services.session_service.begin(
                    context=_context(account_id),
                    now=utcnow() + timedelta(seconds=index),
                    correlation_id=uuid4(),
                    oauth_transaction_id=seed_oauth_transaction(connection),
                )
            )

    with migrated_database.begin() as connection:
        services = composition.services(connection)
        services.session_service.begin(
            context=_context(account_id),
            now=utcnow() + timedelta(seconds=11),
            correlation_id=uuid4(),
            oauth_transaction_id=seed_oauth_transaction(connection),
        )

    with migrated_database.connect() as connection:
        oldest = connection.execute(
            select(sessions).where(sessions.c.id == tokens[0].session_id)
        ).mappings().one()
        limit_events = connection.execute(
            select(audit_events).where(
                audit_events.c.action == "auth.session.revoked"
            )
        ).mappings().all()
    assert oldest["revocation_reason"] == "session_limit"
    assert len(limit_events) == 1
    assert limit_events[0]["payload"]["reason"] == "session_limit"


# ---------------------------------------------------------------------------
# TC-SESS-07
# ---------------------------------------------------------------------------


def test_revoking_every_session_for_an_account_refuses_each_on_its_next_request(
    migrated_database, composition
):
    """TC-SESS-07. C-07's effect, at the service boundary the CLI calls."""
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
    issued = []
    for _ in range(3):
        with migrated_database.begin() as connection:
            issued.append(
                composition.services(connection).session_service.begin(
                    context=_context(account_id),
                    now=utcnow(),
                    correlation_id=uuid4(),
                    oauth_transaction_id=seed_oauth_transaction(connection),
                )
            )

    with migrated_database.begin() as connection:
        revoked = composition.services(connection).session_service.revoke_every_session(
            account_id=account_id,
            now=utcnow(),
            correlation_id=uuid4(),
            operator="synthetic-operator",
        )
    assert revoked == 3

    for session in issued:
        with migrated_database.begin() as connection:
            assert (
                composition.services(connection).session_service.resolve(
                    session.token, now=utcnow()
                )
                is None
            )


# ---------------------------------------------------------------------------
# TC-SESS-09, TC-SESS-10
# ---------------------------------------------------------------------------


async def test_the_session_cookie_attributes_are_exactly_the_policy(client, provider):
    """TC-SESS-09. N-05, including the `__Host-` prefix and no `Domain`."""
    start = await client.get("/v1/auth/discord/start")
    transaction = next(
        header.split("=", 1)[1].split(";", 1)[0]
        for header in start.headers.get_list("set-cookie")
        if header.startswith("__Host-fb_login_txn=")
    )
    state = provider.authorization_calls[-1][0]
    response = await client.get(
        "/auth/discord/callback",
        params={"state": state, "code": "c"},
        cookies={"__Host-fb_login_txn": transaction},
    )
    cookie = next(
        header
        for header in response.headers.get_list("set-cookie")
        if header.startswith("__Host-fb_session=")
    )
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "SameSite=lax" in cookie
    assert "Path=/" in cookie
    assert "Domain=" not in cookie


def test_the_csrf_token_is_derived_and_changes_when_the_session_rotates(
    migrated_database, composition, settings
):
    """TC-SESS-10. No column holds it, and rotation changes it structurally.

    The token is `HMAC(key, session_id)`, so "rotates with the session" is a
    consequence of the session id changing rather than something a second write
    has to remember to do.
    """
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        services = composition.services(connection)
        first = services.session_service.begin(
            context=_context(account_id),
            now=utcnow(),
            correlation_id=uuid4(),
            oauth_transaction_id=seed_oauth_transaction(connection),
        )

    token = csrf.issue(settings.csrf_key, first.session_id)
    assert csrf.verify(settings.csrf_key, first.session_id, token)
    assert not csrf.verify(settings.csrf_key, uuid4(), token)
    assert not csrf.verify(settings.csrf_key, first.session_id, None)
    assert not csrf.verify(settings.csrf_key, first.session_id, token + "x")

    with migrated_database.connect() as connection:
        row = connection.execute(
            select(sessions).where(sessions.c.id == first.session_id)
        ).mappings().one()
    assert token not in str(dict(row))

    promoted = _context(
        account_id,
        capabilities=(ActorCapability.GUILD_MEMBER, ActorCapability.GUILD_COUNCIL),
    )
    with migrated_database.begin() as connection:
        services = composition.services(connection)
        record = services.session_service.resolve(first.token, now=utcnow())
        rotated = services.session_service.rotate_if_privileges_changed(
            record=record, context=promoted, now=utcnow(), correlation_id=uuid4()
        )
    assert csrf.issue(settings.csrf_key, rotated.session_id) != token
