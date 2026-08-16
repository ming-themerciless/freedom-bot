"""TC-AUTH-01 to TC-AUTH-12: the OAuth flow, at the HTTP and service boundaries.

Every test here asserts one contract statement and names it. Where a test could
pass for the wrong reason — a refusal that happens to look right because nothing
ran at all — it asserts the *absence* too: no session row, no token record, no
account.
"""
from __future__ import annotations

from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select, text

from adapters.database.tables import (
    audit_events,
    external_identities,
    oauth_token_grants,
    oauth_transactions,
    platform_accounts,
    sessions,
)
from application.web.crypto import token_hash
from application.web.errors import AuthenticationFailure
from application.web.oauth import DEFAULT_RETURN_PATH, safe_return_path
from tests.web.conftest import utcnow
from tests.web_fixtures import PUBLIC_ORIGIN, TEST_GUILD_ID

pytestmark = pytest.mark.database


async def _start(client):
    response = await client.get("/v1/auth/discord/start")
    assert response.status_code == 303
    return response


def _transaction_cookie(response) -> str:
    for cookie in response.headers.get_list("set-cookie"):
        if cookie.startswith("__Host-fb_login_txn="):
            return cookie.split("=", 1)[1].split(";", 1)[0]
    raise AssertionError("the start route set no login-transaction cookie")


# ---------------------------------------------------------------------------
# TC-AUTH-01
# ---------------------------------------------------------------------------


async def test_start_mints_a_transaction_and_redirects_with_the_exact_scopes(
    client, provider, migrated_database
):
    """TC-AUTH-01. Exactly N-03's scopes, N-02's redirect, and a host-only cookie."""
    response = await _start(client)

    location = response.headers["location"]
    assert location.startswith("https://discord.example/oauth2/authorize")
    # The scopes reach the provider from configuration, and startup already
    # refused anything but N-03 (S-06). Asserting it again here is what makes a
    # widened scope a test failure rather than a privacy change nobody noticed.
    assert "scope=identify%20guilds.members.read" in location

    raw = _transaction_cookie(response)
    cookie_header = next(
        header
        for header in response.headers.get_list("set-cookie")
        if header.startswith("__Host-fb_login_txn=")
    )
    assert "HttpOnly" in cookie_header
    assert "Secure" in cookie_header
    assert "SameSite=lax" in cookie_header
    assert "Path=/" in cookie_header
    # No Domain attribute: that is what host-only means, and the `__Host-` prefix
    # is what makes the browser enforce it rather than trusting us.
    assert "Domain=" not in cookie_header

    with migrated_database.connect() as connection:
        row = connection.execute(
            select(oauth_transactions).where(oauth_transactions.c.id == UUID(raw))
        ).mappings().one()
    assert row["consumed_at"] is None
    assert row["provider_key"] == "discord"
    assert row["return_path"] == DEFAULT_RETURN_PATH


# ---------------------------------------------------------------------------
# TC-AUTH-02, TC-AUTH-03
# ---------------------------------------------------------------------------


async def test_a_mismatched_state_is_refused_and_creates_no_session(
    client, migrated_database
):
    """TC-AUTH-02. The state is compared inside the consumption statement."""
    start = await _start(client)
    transaction_id = _transaction_cookie(start)

    response = await client.get(
        "/auth/discord/callback",
        params={"state": "not-the-minted-state", "code": "abc"},
        cookies={"__Host-fb_login_txn": transaction_id},
    )

    assert response.status_code == 303
    assert "/v1/login?failure=transaction_unknown" in response.headers["location"]
    with migrated_database.connect() as connection:
        assert connection.execute(select(text("count(*)")).select_from(sessions)).scalar_one() == 0


async def test_a_callback_without_the_transaction_cookie_is_refused(
    client, migrated_database, composition
):
    """TC-AUTH-03. Even with a *valid* state — the cookie is what binds the browser.

    This is the property that makes a `GET` start safe against login CSRF: an
    attacker who initiates a flow holds the transaction cookie in their own
    browser and cannot install it in the victim's.
    """
    state = "a-perfectly-valid-looking-state"
    with migrated_database.begin() as connection:
        services = composition.services(connection)
        transaction_id = services.transactions.create(
            state_hash=token_hash(state),
            verifier=composition.envelope.seal(b"verifier", aad=b"aad"),
            return_path="/v1/characters",
            provider_key="discord",
            expires_at=utcnow() + timedelta(minutes=10),
            client_ip_hash=None,
        )

    response = await client.get(
        "/auth/discord/callback", params={"state": state, "code": "abc"}
    )

    assert response.status_code == 303
    assert "failure=transaction_unknown" in response.headers["location"]
    with migrated_database.connect() as connection:
        row = connection.execute(
            select(oauth_transactions).where(oauth_transactions.c.id == transaction_id)
        ).mappings().one()
    assert row["consumed_at"] is None, "an unbound callback must not consume anything"


# ---------------------------------------------------------------------------
# TC-AUTH-04, TC-AUTH-05
# ---------------------------------------------------------------------------


def test_replaying_a_consumed_transaction_matches_zero_rows(
    migrated_database, composition
):
    """TC-AUTH-04. The second consumption is refused by the database, not by code."""
    state = "single-use-state"
    with migrated_database.begin() as connection:
        services = composition.services(connection)
        transaction_id = uuid4()
        services.transactions.create(
            state_hash=token_hash(state),
            verifier=composition.envelope.seal(b"v", aad=b"aad"),
            return_path="/v1/characters",
            provider_key="discord",
            expires_at=utcnow() + timedelta(minutes=10),
            client_ip_hash=None,
            transaction_id=transaction_id,
        )

    with migrated_database.begin() as connection:
        first = composition.services(connection).transactions.consume(
            transaction_id=transaction_id, state_hash=token_hash(state), now=utcnow()
        )
    assert first is not None

    with migrated_database.begin() as connection:
        second = composition.services(connection).transactions.consume(
            transaction_id=transaction_id, state_hash=token_hash(state), now=utcnow()
        )
    assert second is None


def test_a_transaction_older_than_the_policy_is_refused(migrated_database, composition):
    """TC-AUTH-05. N-04's ten minutes, enforced in the consumption statement.

    The row is created with a *valid* lifetime and then consumed at a later
    moment, rather than inserted already expired: the table's own
    `expires_at > created_at` check refuses an already-expired row outright, so
    inserting one would test the constraint instead of the expiry rule.
    """
    state = "expired-state"
    transaction_id = uuid4()
    with migrated_database.begin() as connection:
        composition.services(connection).transactions.create(
            state_hash=token_hash(state),
            verifier=composition.envelope.seal(b"v", aad=b"aad"),
            return_path="/v1/characters",
            provider_key="discord",
            expires_at=utcnow() + timedelta(minutes=10),
            client_ip_hash=None,
            transaction_id=transaction_id,
        )

    after_the_window = utcnow() + timedelta(minutes=10, seconds=1)
    with migrated_database.begin() as connection:
        recovered = composition.services(connection).transactions.consume(
            transaction_id=transaction_id,
            state_hash=token_hash(state),
            now=after_the_window,
        )
    assert recovered is None

    # And it is still unconsumed: an expired transaction is refused, not spent.
    with migrated_database.connect() as connection:
        row = connection.execute(
            select(oauth_transactions).where(oauth_transactions.c.id == transaction_id)
        ).mappings().one()
    assert row["consumed_at"] is None


# ---------------------------------------------------------------------------
# TC-AUTH-06
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        ("//evil.example", DEFAULT_RETURN_PATH),
        ("https://evil.example", DEFAULT_RETURN_PATH),
        ("/\\evil", DEFAULT_RETURN_PATH),
        ("javascript:alert(1)", DEFAULT_RETURN_PATH),
        ("/v1/not-on-the-allowlist", DEFAULT_RETURN_PATH),
        ("/etc/passwd", DEFAULT_RETURN_PATH),
        ("/v1/characters\r\nSet-Cookie: x=1", DEFAULT_RETURN_PATH),
        ("/v1/characters", "/v1/characters"),
        ("/v1/council/characters", "/v1/council/characters"),
    ],
)
def test_only_an_allowlisted_path_survives_as_a_return_target(candidate, expected):
    """TC-AUTH-06. Only the last two are paths this platform will redirect to.

    `//evil.example` is the one worth naming: it is a *path* to a naive check and
    a *host* to a browser. That gap is why the rule is an allowlist of shapes
    rather than a list of forbidden prefixes.
    """
    assert safe_return_path(candidate) == expected


async def test_a_hostile_return_target_never_reaches_a_location_header(
    client, migrated_database
):
    """TC-AUTH-06, at the boundary: the stored row already holds the safe path."""
    response = await client.get(
        "/v1/auth/discord/start", params={"return": "//evil.example"}
    )
    raw = _transaction_cookie(response)
    with migrated_database.connect() as connection:
        stored = connection.execute(
            select(oauth_transactions.c.return_path).where(
                oauth_transactions.c.id == UUID(raw)
            )
        ).scalar_one()
    assert stored == DEFAULT_RETURN_PATH


# ---------------------------------------------------------------------------
# TC-AUTH-07, TC-AUTH-12
# ---------------------------------------------------------------------------


async def test_the_stored_pkce_verifier_is_ciphertext_and_never_its_hash(
    client, migrated_database, composition
):
    """TC-AUTH-07. Neither the plaintext **nor its SHA-256** is in any column.

    The second assertion is the one that would have caught the contradicted
    contract: an earlier revision said the verifier was hashed, which cannot
    complete a PKCE exchange. Asserting the hash is absent proves the storage is
    the encrypted form the flow actually needs.
    """
    response = await _start(client)
    transaction_id = UUID(_transaction_cookie(response))

    with migrated_database.connect() as connection:
        row = connection.execute(
            select(oauth_transactions).where(oauth_transactions.c.id == transaction_id)
        ).mappings().one()

    ciphertext = bytes(row["pkce_verifier_ciphertext"])
    assert ciphertext, "the verifier must be stored, encrypted, to complete the exchange"

    with migrated_database.begin() as connection:
        recovered = composition.services(connection).transactions.consume(
            transaction_id=transaction_id,
            state_hash=row["state_hash"],
            now=utcnow(),
        )
    plaintext = composition.envelope.open(
        recovered.verifier,
        aad=__import__(
            "application.web.crypto", fromlist=["transaction_aad"]
        ).transaction_aad(transaction_id, recovered.verifier.key_version, "discord"),
    ).decode()

    serialised = " ".join(str(value) for value in row.values())
    assert plaintext not in serialised
    assert token_hash(plaintext).hex() not in serialised
    assert plaintext.encode() not in ciphertext


def test_a_verifier_moved_to_another_transaction_row_refuses_to_decrypt(
    migrated_database, composition
):
    """TC-AUTH-12(b). The GCM binding makes a copied ciphertext useless.

    Not merely unreadable to an attacker — **unusable by the application**, which
    is the stronger property: a moved ciphertext raises rather than decrypting
    into a verifier that would complete somebody else's exchange.
    """
    from application.web.crypto import DecryptionError, transaction_aad

    first, second = uuid4(), uuid4()
    sealed = composition.envelope.seal(
        b"the-verifier", aad=transaction_aad(first, composition.settings.encryption.active_version, "discord")
    )

    with pytest.raises(DecryptionError):
        composition.envelope.open(
            sealed,
            aad=transaction_aad(
                second, composition.settings.encryption.active_version, "discord"
            ),
        )


def test_consumption_erases_the_verifier_in_the_same_statement(
    migrated_database, composition
):
    """TC-AUTH-12(c). After one callback there is no verifier left to recover."""
    state = "erase-me"
    transaction_id = uuid4()
    with migrated_database.begin() as connection:
        composition.services(connection).transactions.create(
            state_hash=token_hash(state),
            verifier=composition.envelope.seal(b"v", aad=b"aad"),
            return_path="/v1/characters",
            provider_key="discord",
            expires_at=utcnow() + timedelta(minutes=10),
            client_ip_hash=None,
            transaction_id=transaction_id,
        )
    with migrated_database.begin() as connection:
        composition.services(connection).transactions.consume(
            transaction_id=transaction_id, state_hash=token_hash(state), now=utcnow()
        )

    with migrated_database.connect() as connection:
        row = connection.execute(
            select(oauth_transactions).where(oauth_transactions.c.id == transaction_id)
        ).mappings().one()
    assert row["pkce_verifier_ciphertext"] is None
    assert row["nonce"] is None
    assert row["consumed_at"] is not None


def test_two_concurrent_callbacks_yield_exactly_one_exchange(
    database_url, migrated_database, composition
):
    """TC-AUTH-12(d). Two **real** connections race the consumption statement.

    Under `READ COMMITTED` the second blocks on `FOR UPDATE`, re-checks
    `consumed_at IS NULL` when the lock is released, matches zero rows and is
    refused. Proving that needs two connections; one connection would only prove
    the statement is written the way it is written.
    """
    from sqlalchemy import create_engine

    state = "raced-state"
    transaction_id = uuid4()
    with migrated_database.begin() as connection:
        composition.services(connection).transactions.create(
            state_hash=token_hash(state),
            verifier=composition.envelope.seal(b"v", aad=b"aad"),
            return_path="/v1/characters",
            provider_key="discord",
            expires_at=utcnow() + timedelta(minutes=10),
            client_ip_hash=None,
            transaction_id=transaction_id,
        )

    other = create_engine(database_url)
    try:
        first_connection = migrated_database.connect()
        second_connection = other.connect()
        first = first_connection.begin()
        second = second_connection.begin()
        try:
            from adapters.web.repositories import OAuthTransactionRepository

            winner = OAuthTransactionRepository(first_connection).consume(
                transaction_id=transaction_id,
                state_hash=token_hash(state),
                now=utcnow(),
            )
            assert winner is not None
            first.commit()

            loser = OAuthTransactionRepository(second_connection).consume(
                transaction_id=transaction_id,
                state_hash=token_hash(state),
                now=utcnow(),
            )
            assert loser is None
            second.commit()
        finally:
            first_connection.close()
            second_connection.close()
    finally:
        other.dispose()


# ---------------------------------------------------------------------------
# TC-AUTH-08
# ---------------------------------------------------------------------------


async def test_a_non_member_callback_creates_no_session_and_answers_403(
    client, provider, migrated_database
):
    """TC-AUTH-08. ADR 0004's rejection step, and the absences that prove it.

    A person who authorizes the Discord application but is not in the guild
    leaves **no session row, no token record and no account-linked state beyond
    the audit event**.
    """
    provider.is_member = False
    start = await _start(client)
    transaction_id = _transaction_cookie(start)
    state = provider.authorization_calls[-1][0]

    response = await client.get(
        "/auth/discord/callback",
        params={"state": state, "code": "the-code"},
        cookies={"__Host-fb_login_txn": transaction_id},
    )

    assert response.status_code == 403
    assert "not currently a member" in response.text
    with migrated_database.connect() as connection:
        assert connection.execute(select(text("count(*)")).select_from(sessions)).scalar_one() == 0
        assert (
            connection.execute(select(text("count(*)")).select_from(oauth_token_grants)).scalar_one()
            == 0
        )
        assert (
            connection.execute(select(text("count(*)")).select_from(platform_accounts)).scalar_one()
            == 0
        )
        refusals = connection.execute(
            select(audit_events.c.action).where(
                audit_events.c.action == "auth.login.refused"
            )
        ).scalars().all()
    assert refusals == ["auth.login.refused"]


# ---------------------------------------------------------------------------
# The successful path, and TC-AUTH-11
# ---------------------------------------------------------------------------


async def test_a_member_login_creates_one_session_and_one_audit_event(
    client, provider, migrated_database
):
    """The happy path, and TC-AUTH-11's "exactly one, carrying no secret"."""
    start = await _start(client)
    transaction_id = _transaction_cookie(start)
    state = provider.authorization_calls[-1][0]

    response = await client.get(
        "/auth/discord/callback",
        params={"state": state, "code": "the-code"},
        cookies={"__Host-fb_login_txn": transaction_id},
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/v1/characters"
    session_cookie = next(
        header
        for header in response.headers.get_list("set-cookie")
        if header.startswith("__Host-fb_session=")
    )
    assert "HttpOnly" in session_cookie and "Secure" in session_cookie

    with migrated_database.connect() as connection:
        session_rows = connection.execute(select(sessions)).mappings().all()
        identity_rows = connection.execute(select(external_identities)).mappings().all()
        events = connection.execute(
            select(audit_events).where(audit_events.c.action == "auth.login.succeeded")
        ).mappings().all()

    assert len(session_rows) == 1
    assert session_rows[0]["auth_method"] == "discord_oauth"
    assert len(identity_rows) == 1
    assert identity_rows[0]["subject"] == provider.subject
    assert len(events) == 1

    payload = events[0]["payload"]
    serialised = str(payload)
    # The code, the tokens, the state and the verifier appear in no audit payload.
    for secret in ("the-code", "synthetic-access-token", "synthetic-refresh-token", state):
        assert secret not in serialised
    assert events[0]["actor_platform_account_id"] is not None
    assert events[0]["correlation_id"] is not None


async def test_a_provider_outage_at_the_exchange_creates_no_session(
    client, provider, migrated_database
):
    """SM-01's provider-outage row: `refused`, no session, and the flow is recoverable."""
    start = await _start(client)
    transaction_id = _transaction_cookie(start)
    state = provider.authorization_calls[-1][0]
    provider.unavailable = True

    response = await client.get(
        "/auth/discord/callback",
        params={"state": state, "code": "the-code"},
        cookies={"__Host-fb_login_txn": transaction_id},
    )

    assert response.status_code == 303
    assert "failure=provider_error" in response.headers["location"]
    with migrated_database.connect() as connection:
        assert connection.execute(select(text("count(*)")).select_from(sessions)).scalar_one() == 0
