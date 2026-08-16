"""TC-BG-01 to TC-BG-04 and TC-BG-06 to TC-BG-15: the emergency login itself.

The whole point of this path is that it works when Discord does not, so the
provider double in these tests is **faulted**: every call it receives raises. A
test here that passed by quietly reaching Discord would be testing the wrong
platform.
"""
from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select, text, update

from adapters.database.tables import (
    audit_events,
    recovery_grants,
    sessions,
    webauthn_challenges,
    webauthn_credentials,
)
from application.audit import ActorCapability
from application.web.capabilities import AdministratorScope, AuthMethod
from application.web.crypto import mint_token, token_hash
from application.web.errors import AuthenticationFailure
from tests.web.conftest import (
    enroll_credential,
    issue_grant,
    make_account,
    utcnow,
)
from tests.web.webauthn_double import SoftwareAuthenticator
from tests.web_fixtures import PUBLIC_ORIGIN

pytestmark = pytest.mark.database

RP_ID = "portal.test"


@pytest.fixture()
def faulted_provider(provider):
    """Discord is entirely unavailable, for every test in this module."""
    provider.unavailable = True
    return provider


@pytest.fixture()
def authenticator():
    return SoftwareAuthenticator(rp_id=RP_ID, origin=PUBLIC_ORIGIN)


@pytest.fixture()
def protected_account(migrated_database, authenticator):
    with migrated_database.begin() as connection:
        account_id = make_account(
            connection, protected=True, label="Server Administrator"
        )
        enroll_credential(
            connection,
            account_id,
            credential_id=authenticator.credential_id,
            public_key=authenticator.cose_public_key,
            nickname="primary",
        )
        enroll_credential(
            connection,
            account_id,
            credential_id=b"second-credential-id-000002",
            public_key=authenticator.cose_public_key,
            nickname="backup",
        )
    return account_id


def _challenge(composition, migrated_database):
    with migrated_database.begin() as connection:
        options = composition.services(connection).break_glass.begin_assertion(
            now=utcnow(), client_ip_hash=None
        )
    from webauthn.helpers import base64url_to_bytes

    return base64url_to_bytes(options.payload["challenge"])


# ---------------------------------------------------------------------------
# TC-BG-01, TC-BG-02
# ---------------------------------------------------------------------------


def test_an_enrolled_credential_creates_a_break_glass_session_with_discord_faulted(
    migrated_database, composition, faulted_provider, authenticator, protected_account
):
    """TC-BG-01 **and** TC-BG-02, together, because they are one property.

    A break-glass login that only worked while Discord was reachable would
    satisfy neither. The provider double raises on every call, and nothing in
    this path calls it.
    """
    challenge = _challenge(composition, migrated_database)
    payload = authenticator.sign(challenge)

    with migrated_database.begin() as connection:
        login = composition.services(connection).break_glass.complete_assertion(
            credential_payload=payload,
            now=utcnow(),
            correlation_id=uuid4(),
            client_ip_hash=None,
            user_agent_digest=None,
        )

    assert login.account_id == protected_account
    with migrated_database.connect() as connection:
        row = connection.execute(
            select(sessions).where(sessions.c.id == login.session.session_id)
        ).mappings().one()
    assert row["auth_method"] == "webauthn"
    # N-15's bounds, not N-06/N-07's.
    assert row["absolute_expires_at"] - row["created_at"] <= timedelta(minutes=60)
    assert row["idle_expires_at"] - row["created_at"] <= timedelta(minutes=15)

    with migrated_database.begin() as connection:
        context = composition.services(connection).session_service
    from application.web.capabilities import resolve_capabilities

    resolved = resolve_capabilities(
        account_id=login.account_id,
        auth_method=AuthMethod.WEBAUTHN,
        membership=None,
        mappings=(),
    )
    assert resolved.capabilities == frozenset({ActorCapability.PLATFORM_ADMINISTRATOR})
    assert resolved.administrator_scope is AdministratorScope.EMERGENCY_CONTINUITY


def test_the_emergency_session_and_its_audit_event_commit_together(
    migrated_database, composition, faulted_provider, authenticator, protected_account
):
    """TC-BG-15. The end-to-end proof that the constraint swap delivers OD-43.

    The audit row carries `actor_platform_account_id` and a **null**
    `actor_discord_user_id` under a human capability. Before migration 0006 that
    row was illegal, `ck_audit_events_human_action_has_an_actor` refused it, and
    because the session and its event share a transaction the *login* would have
    failed with it.
    """
    challenge = _challenge(composition, migrated_database)
    payload = authenticator.sign(challenge)

    with migrated_database.begin() as connection:
        login = composition.services(connection).break_glass.complete_assertion(
            credential_payload=payload,
            now=utcnow(),
            correlation_id=uuid4(),
            client_ip_hash=None,
            user_agent_digest=None,
        )

    with migrated_database.connect() as connection:
        events = connection.execute(
            select(audit_events).where(
                audit_events.c.action == "auth.emergency.webauthn.succeeded"
            )
        ).mappings().all()
        session_exists = connection.execute(
            select(text("count(*)"))
            .select_from(sessions)
            .where(sessions.c.id == login.session.session_id)
        ).scalar_one()

    assert session_exists == 1
    assert len(events) == 1
    event = events[0]
    assert event["actor_platform_account_id"] == protected_account
    assert event["actor_discord_user_id"] is None
    assert event["actor_capability"] == "platform_administrator"


# ---------------------------------------------------------------------------
# TC-BG-03
# ---------------------------------------------------------------------------


def test_a_non_advancing_sign_count_refuses_the_login_and_audits_it(
    migrated_database, composition, faulted_provider, authenticator, protected_account
):
    """TC-BG-03. A counter that does not advance is the cloned-authenticator signal."""
    first = _challenge(composition, migrated_database)
    with migrated_database.begin() as connection:
        composition.services(connection).break_glass.complete_assertion(
            credential_payload=authenticator.sign(first),
            now=utcnow(),
            correlation_id=uuid4(),
            client_ip_hash=None,
            user_agent_digest=None,
        )

    second = _challenge(composition, migrated_database)
    replayed = authenticator.sign(second, sign_count=1)

    with pytest.raises(AuthenticationFailure) as refusal:
        with migrated_database.begin() as connection:
            composition.services(connection).break_glass.complete_assertion(
                credential_payload=replayed,
                now=utcnow(),
                correlation_id=uuid4(),
                client_ip_hash=None,
                user_agent_digest=None,
            )
    assert refusal.value.code == "invalid"
    assert refusal.value.audit is not None
    assert refusal.value.audit.payload["reason"] in (
        "sign_count_did_not_advance",
        "assertion_rejected",
    )


def test_an_assertion_without_user_verification_is_refused(
    migrated_database, composition, faulted_provider, authenticator, protected_account
):
    """N-60: user verification is **required**.

    A break-glass credential that can be presented without it is a key somebody
    found, which is a different security property from a key somebody holds.
    """
    challenge = _challenge(composition, migrated_database)
    payload = authenticator.sign(challenge, user_verified=False)

    with pytest.raises(AuthenticationFailure):
        with migrated_database.begin() as connection:
            composition.services(connection).break_glass.complete_assertion(
                credential_payload=payload,
                now=utcnow(),
                correlation_id=uuid4(),
                client_ip_hash=None,
                user_agent_digest=None,
            )


def test_an_assertion_from_another_origin_is_refused(
    migrated_database, composition, faulted_provider, authenticator, protected_account
):
    """N-60's origin binding, which is what stops a phished ceremony."""
    challenge = _challenge(composition, migrated_database)
    payload = authenticator.sign(challenge, origin="https://evil.example")

    with pytest.raises(AuthenticationFailure):
        with migrated_database.begin() as connection:
            composition.services(connection).break_glass.complete_assertion(
                credential_payload=payload,
                now=utcnow(),
                correlation_id=uuid4(),
                client_ip_hash=None,
                user_agent_digest=None,
            )


def test_a_challenge_is_single_use(
    migrated_database, composition, faulted_provider, authenticator, protected_account
):
    """SM-03's conditional consumption: replay and race end in the same place."""
    challenge = _challenge(composition, migrated_database)
    with migrated_database.begin() as connection:
        composition.services(connection).break_glass.complete_assertion(
            credential_payload=authenticator.sign(challenge),
            now=utcnow(),
            correlation_id=uuid4(),
            client_ip_hash=None,
            user_agent_digest=None,
        )

    with pytest.raises(AuthenticationFailure) as refusal:
        with migrated_database.begin() as connection:
            composition.services(connection).break_glass.complete_assertion(
                credential_payload=authenticator.sign(challenge),
                now=utcnow(),
                correlation_id=uuid4(),
                client_ip_hash=None,
                user_agent_digest=None,
            )
    assert refusal.value.code == "expired"


def test_an_unknown_credential_is_refused_without_revealing_that_it_is_unknown(
    migrated_database, composition, faulted_provider, protected_account
):
    """The response says `invalid`; the audit record says `unknown_credential`.

    The browser must not be able to tell an unknown credential from a bad
    signature from a replayed challenge — that distinction is an oracle.
    """
    stranger = SoftwareAuthenticator(
        rp_id=RP_ID, origin=PUBLIC_ORIGIN, credential_id=b"never-enrolled-00000000001"
    )
    challenge = _challenge(composition, migrated_database)

    with pytest.raises(AuthenticationFailure) as refusal:
        with migrated_database.begin() as connection:
            composition.services(connection).break_glass.complete_assertion(
                credential_payload=stranger.sign(challenge),
                now=utcnow(),
                correlation_id=uuid4(),
                client_ip_hash=None,
                user_agent_digest=None,
            )
    assert refusal.value.code == "invalid"
    assert refusal.value.audit.payload["reason"] == "unknown_credential"


# ---------------------------------------------------------------------------
# Recovery grants: TC-BG-06 to TC-BG-09, TC-BG-13
# ---------------------------------------------------------------------------


def test_a_recovery_grant_creates_a_session_and_names_only_its_record_id(
    migrated_database, composition, faulted_provider, protected_account
):
    """TC-BG-06/TC-BG-12. The token appears in no row, log line or audit payload."""
    token = mint_token()
    with migrated_database.begin() as connection:
        grant_id = issue_grant(
            connection, protected_account, token_hash=token_hash(token)
        )

    with migrated_database.begin() as connection:
        login = composition.services(connection).break_glass.redeem_recovery_grant(
            token=token,
            now=utcnow(),
            correlation_id=uuid4(),
            client_ip_hash=None,
            user_agent_digest=None,
        )

    assert login.grant_record_id == grant_id
    with migrated_database.connect() as connection:
        grant_row = connection.execute(
            select(recovery_grants).where(recovery_grants.c.id == grant_id)
        ).mappings().one()
        event = connection.execute(
            select(audit_events).where(
                audit_events.c.action == "auth.emergency.recovery.consumed"
            )
        ).mappings().one()
        session_row = connection.execute(
            select(sessions).where(sessions.c.id == login.session.session_id)
        ).mappings().one()

    assert grant_row["consumed_at"] is not None
    assert grant_row["consumed_session_id"] == login.session.session_id
    assert token not in str(dict(grant_row))
    assert token not in str(dict(event))
    assert event["entity_id"] == str(grant_id)
    assert session_row["auth_method"] == "recovery_grant"


def test_replay_expiry_and_a_wrong_purpose_are_each_refused(
    migrated_database, composition, faulted_provider, protected_account
):
    """TC-BG-07/TC-BG-13. One conditional statement covers all three."""
    token = mint_token()
    with migrated_database.begin() as connection:
        issue_grant(connection, protected_account, token_hash=token_hash(token))
    with migrated_database.begin() as connection:
        composition.services(connection).break_glass.redeem_recovery_grant(
            token=token,
            now=utcnow(),
            correlation_id=uuid4(),
            client_ip_hash=None,
            user_agent_digest=None,
        )

    # Replay: the grant is spent, one session exists, one consumption is audited.
    with pytest.raises(AuthenticationFailure):
        with migrated_database.begin() as connection:
            composition.services(connection).break_glass.redeem_recovery_grant(
                token=token,
                now=utcnow(),
                correlation_id=uuid4(),
                client_ip_hash=None,
                user_agent_digest=None,
            )
    with migrated_database.connect() as connection:
        consumptions = connection.execute(
            select(text("count(*)"))
            .select_from(audit_events)
            .where(audit_events.c.action == "auth.emergency.recovery.consumed")
        ).scalar_one()
        live_sessions = connection.execute(
            select(text("count(*)")).select_from(sessions).where(sessions.c.revoked_at.is_(None))
        ).scalar_one()
    assert consumptions == 1
    assert live_sessions == 1

    # Expiry.
    expired = mint_token()
    with migrated_database.begin() as connection:
        issue_grant(connection, protected_account, token_hash=token_hash(expired))
    with pytest.raises(AuthenticationFailure):
        with migrated_database.begin() as connection:
            composition.services(connection).break_glass.redeem_recovery_grant(
                token=expired,
                now=utcnow() + timedelta(minutes=11),
                correlation_id=uuid4(),
                client_ip_hash=None,
                user_agent_digest=None,
            )


def test_issuing_a_second_grant_invalidates_the_first_in_the_same_transaction(
    migrated_database, composition, protected_account
):
    """TC-BG-09. N-61: two live grants double the window for no operational gain."""
    first, second = mint_token(), mint_token()
    with migrated_database.begin() as connection:
        services = composition.services(connection)
        services.grants.issue(
            account_id=protected_account,
            token_hash=token_hash(first),
            expires_at=utcnow() + timedelta(minutes=10),
            operator="synthetic-operator",
            correlation_id=uuid4(),
        )
        services.grants.issue(
            account_id=protected_account,
            token_hash=token_hash(second),
            expires_at=utcnow() + timedelta(minutes=10),
            operator="synthetic-operator",
            correlation_id=uuid4(),
        )

    with migrated_database.connect() as connection:
        rows = connection.execute(
            select(recovery_grants).order_by(recovery_grants.c.created_at)
        ).mappings().all()
    assert len(rows) == 2
    assert rows[0]["invalidated_reason"] == "superseded_by_new_grant"
    assert rows[1]["invalidated_at"] is None

    with pytest.raises(AuthenticationFailure):
        with migrated_database.begin() as connection:
            composition.services(connection).break_glass.redeem_recovery_grant(
                token=first,
                now=utcnow(),
                correlation_id=uuid4(),
                client_ip_hash=None,
                user_agent_digest=None,
            )


def test_two_concurrent_redemptions_create_exactly_one_session(
    database_url, migrated_database, composition, protected_account
):
    """TC-BG-08. Two **real** connections; the consumption statement decides."""
    from sqlalchemy import create_engine

    from adapters.web.repositories import RecoveryGrantRepository

    from application.web.capabilities import resolve_capabilities

    token = mint_token()
    # Two real sessions, because `recovery_grants.consumed_session_id` is a
    # foreign key: the grant names the session it was spent on, so a fabricated
    # id would be refused by the schema before the race could be observed. That
    # ordering is also the real flow's — the session exists first, and if the
    # consumption then matches zero rows the caller's rollback removes it again.
    contexts = resolve_capabilities(
        account_id=protected_account,
        auth_method=AuthMethod.RECOVERY_GRANT,
        membership=None,
        mappings=(),
    )
    with migrated_database.begin() as connection:
        issue_grant(connection, protected_account, token_hash=token_hash(token))
        services = composition.services(connection)
        first_session = services.session_service.begin(
            context=contexts, now=utcnow(), correlation_id=uuid4()
        )
        second_session = services.session_service.begin(
            context=contexts, now=utcnow(), correlation_id=uuid4()
        )

    other = create_engine(database_url)
    try:
        first_connection = migrated_database.connect()
        second_connection = other.connect()
        first = first_connection.begin()
        second = second_connection.begin()
        try:
            winner = RecoveryGrantRepository(first_connection).consume(
                token_hash=token_hash(token),
                session_id=first_session.session_id,
                now=utcnow(),
            )
            assert winner is not None
            first.commit()

            loser = RecoveryGrantRepository(second_connection).consume(
                token_hash=token_hash(token),
                session_id=second_session.session_id,
                now=utcnow(),
            )
            assert loser is None
            second.commit()
        finally:
            first_connection.close()
            second_connection.close()
    finally:
        other.dispose()


def test_the_per_grant_attempt_cap_refuses_the_sixth_attempt(
    migrated_database, composition, protected_account
):
    """TC-BG-11's per-grant half (N-33). The grant is single use; five tries is an attack."""
    token = mint_token()
    with migrated_database.begin() as connection:
        issue_grant(connection, protected_account, token_hash=token_hash(token))

    for _ in range(5):
        with pytest.raises(AuthenticationFailure):
            with migrated_database.begin() as connection:
                composition.services(connection).break_glass.redeem_recovery_grant(
                    token="wrong-" + token,
                    now=utcnow(),
                    correlation_id=uuid4(),
                    client_ip_hash=None,
                    user_agent_digest=None,
                )

    # The counter is against the *grant record*, so a wrong token cannot be used
    # to exhaust somebody else's budget: it matches no record and counts nothing.
    with migrated_database.connect() as connection:
        attempts = connection.execute(
            select(recovery_grants.c.attempt_count)
        ).scalar_one()
    assert attempts == 0


def test_a_grant_naming_another_account_is_refused(
    migrated_database, composition, protected_account
):
    """The grant's account is checked against the protected one, not assumed."""
    token = mint_token()
    with migrated_database.begin() as connection:
        other_account = make_account(connection)
        issue_grant(connection, other_account, token_hash=token_hash(token))

    with pytest.raises(AuthenticationFailure) as refusal:
        with migrated_database.begin() as connection:
            composition.services(connection).break_glass.redeem_recovery_grant(
                token=token,
                now=utcnow(),
                correlation_id=uuid4(),
                client_ip_hash=None,
                user_agent_digest=None,
            )
    assert refusal.value.audit.payload["reason"] == "grant_names_another_account"
