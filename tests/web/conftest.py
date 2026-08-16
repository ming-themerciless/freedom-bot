"""Fixtures for the portal suite.

Run with the **web** virtualenv, which is the one that has FastAPI:

    TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \\
      ./venv-web/bin/python -m pytest tests/web

Everything here builds on `tests/conftest.py`'s disposable-database guards. Those
guards are not re-implemented: a second copy of the "is this really the throwaway
database?" reasoning would be a second place for it to be wrong.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy import delete, insert, text

from adapters.database.tables import (
    audit_events,
    auth_rate_limits,
    external_identities,
    oauth_token_grants,
    oauth_transactions,
    platform_accounts,
    recovery_grants,
    role_capability_mapping_events,
    role_capability_mappings,
    sessions,
    webauthn_challenges,
    webauthn_credentials,
)
from adapters.web.app import create_app
from adapters.web.composition import WebComposition
from tests.web_fixtures import (
    BOOTSTRAP_ADMIN_ROLE_ID,
    COUNCIL_ROLE_ID,
    FakeDiscordProvider,
    PUBLIC_ORIGIN,
    TEST_GUILD_ID,
    web_settings,
)

pytestmark = pytest.mark.database

#: Emptied between tests, children first. `role_capability_mappings` is **not**
#: here: the protected bootstrap row is inserted by migration 0006 and cannot be
#: deleted by any caller — that is the whole point of it — so the cleanup deletes
#: only the non-protected rows instead.
#:
#: `sessions` precedes `oauth_transactions` from OD-44 onward: the binding
#: foreign key is `RESTRICT`, so a transaction a session still names cannot be
#: deleted first. That ordering requirement is the constraint doing its job, and
#: the cleanup obeys it rather than weakening it to `CASCADE`.
_SCRUBBED_TABLES = (
    oauth_token_grants,
    recovery_grants,
    webauthn_challenges,
    webauthn_credentials,
    auth_rate_limits,
    sessions,
    oauth_transactions,
)

#: Emptied with `TRUNCATE`, not `DELETE`. Both are append-only: migration 0002's
#: trigger refuses `UPDATE` and `DELETE` on them **for the schema owner too**,
#: and deliberately does not cover `TRUNCATE`, which the runtime role is denied
#: by grant instead. That asymmetry exists precisely so a disposable test
#: database can be reset while the application can never empty history.
_APPEND_ONLY_TABLES = ("audit_events", "role_capability_mapping_events")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@pytest.fixture()
def settings(tmp_path):
    return web_settings(tmp_path)


@pytest.fixture()
def provider():
    return FakeDiscordProvider(role_ids=frozenset())


@pytest.fixture()
def composition(settings, provider, migrated_database):
    composition = WebComposition(
        settings=settings, engine=migrated_database, provider=provider
    )
    yield composition


@pytest.fixture()
def app(composition, settings):
    return create_app(settings, composition=composition, run_startup_checks=False)


@pytest.fixture()
async def client(app):
    """An in-process ASGI client. No socket, no server, no `requests`."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url=PUBLIC_ORIGIN, follow_redirects=False
    ) as instance:
        yield instance


@pytest.fixture(autouse=True)
def clean_portal_tables(request):
    """Leave the identity tables as the migration left them, after every test.

    It takes `request` rather than `migrated_database` directly, and resolves the
    engine only for tests that already needed one. An autouse fixture that
    depended on the database unconditionally would make **every** test in this
    directory skip when `TEST_DATABASE_URL` is unset — including the structural
    and configuration tests that need no database at all — and a suite that
    reports 197 skips where 40 of them could have run is a suite whose evidence
    nobody can read.

    `audit_events` is append-only and its trigger refuses `DELETE` for the owner
    too, so it is emptied with `TRUNCATE` — which the trigger does not cover and
    the runtime role is denied by grant. That asymmetry is deliberate in
    migration 0002 precisely so a disposable test database can be reset while the
    application can never empty history.
    """
    yield
    if "migrated_database" not in request.fixturenames:
        return
    migrated_database = request.getfixturevalue("migrated_database")
    with migrated_database.begin() as connection:
        connection.execute(
            text(f"TRUNCATE TABLE {', '.join(_APPEND_ONLY_TABLES)}")
        )
        for table in _SCRUBBED_TABLES:
            connection.execute(delete(table))
        connection.execute(
            delete(role_capability_mappings).where(
                ~role_capability_mappings.c.protected
            )
        )
        connection.execute(delete(external_identities))
        connection.execute(delete(platform_accounts))
        connection.execute(text("DELETE FROM discord_membership_roles"))
        connection.execute(text("DELETE FROM discord_guild_memberships"))
        connection.execute(text("DELETE FROM discord_users"))


# ---------------------------------------------------------------------------
# Seeding helpers
# ---------------------------------------------------------------------------


def make_account(connection, *, protected: bool = False, label: str | None = None) -> UUID:
    account_id = uuid4()
    connection.execute(
        insert(platform_accounts).values(
            id=account_id,
            status="active",
            is_protected_admin=protected,
            display_label=label,
        )
    )
    return account_id


def link_discord(connection, account_id: UUID, subject: int, *, state: str = "active") -> UUID:
    identity_id = uuid4()
    connection.execute(
        insert(external_identities).values(
            id=identity_id,
            platform_account_id=account_id,
            provider_key="discord",
            subject=str(subject),
            state=state,
            retired_at=utcnow() if state == "retired" else None,
            audit_correlation_id=uuid4(),
        )
    )
    return identity_id


def seed_membership(
    connection, *, discord_user_id: int, role_ids: frozenset[int] = frozenset()
) -> None:
    connection.execute(
        text(
            "INSERT INTO discord_users (id, username) VALUES (:id, :name) "
            "ON CONFLICT (id) DO NOTHING"
        ),
        {"id": discord_user_id, "name": f"member-{discord_user_id}"},
    )
    connection.execute(
        text(
            "INSERT INTO discord_guild_memberships (discord_user_id, guild_id, active) "
            "VALUES (:user, :guild, true) "
            "ON CONFLICT (discord_user_id, guild_id) DO UPDATE SET active = true"
        ),
        {"user": discord_user_id, "guild": TEST_GUILD_ID},
    )
    for role_id in role_ids:
        connection.execute(
            text(
                "INSERT INTO discord_membership_roles (discord_user_id, guild_id, role_id) "
                "VALUES (:user, :guild, :role) ON CONFLICT DO NOTHING"
            ),
            {"user": discord_user_id, "guild": TEST_GUILD_ID, "role": role_id},
        )


def add_mapping(
    connection,
    *,
    role_id: int,
    capability: str,
    created_by: UUID,
    scope: str = "full",
    auth_method: str = "discord_oauth",
) -> UUID:
    """Insert a mapping directly, for tests about what resolution does with one."""
    mapping_id = uuid4()
    provenance = "emergency_continuity" if scope == "emergency_continuity" else "ordinary"
    connection.execute(
        insert(role_capability_mappings).values(
            id=mapping_id,
            guild_id=TEST_GUILD_ID,
            role_id=role_id,
            capability=capability,
            protected=False,
            active=True,
            created_by_account_id=created_by,
            created_under_auth_method=auth_method,
            created_under_scope=scope,
            provenance=provenance,
            reason="synthetic mapping for a test",
            audit_correlation_id=uuid4(),
        )
    )
    return mapping_id


def seed_oauth_transaction(
    connection,
    *,
    consumed: bool = True,
    claimed: bool = False,
    expires_in_minutes: int = 10,
    return_path: str = "/v1/characters",
    provider_key: str = "discord",
) -> UUID:
    """An `oauth_transactions` row in a chosen state. Returns its id.

    OD-44 makes `sessions.oauth_transaction_id` required for every
    `discord_oauth` session, so a test that wants such a session needs a
    transaction for it to name. Written directly rather than through the service
    so a test can also produce the states the service never produces — an
    unconsumed row, or one that has already been claimed — which is exactly what
    the refusal cases need.

    `consumed` erases the verifier as the real consumption statement does, because
    `ck_oauth_transactions_consumed_has_no_verifier` refuses a consumed row that
    kept one.

    `provider_key` is settable because the OD-44 re-review's first finding is
    about exactly this column: the completion claim compares it against the
    provider that verified the identity being completed, so a test needs to be
    able to record a transaction for a provider other than the one it will
    complete with.
    """
    transaction_id = uuid4()
    now = utcnow()
    connection.execute(
        insert(oauth_transactions).values(
            id=transaction_id,
            state_hash=sha256(transaction_id.bytes).digest(),
            pkce_verifier_ciphertext=None if consumed else b"synthetic-ciphertext",
            nonce=None if consumed else b"synthetic-12b",
            key_version=1,
            return_path=return_path,
            provider_key=provider_key,
            created_at=now,
            expires_at=now + timedelta(minutes=expires_in_minutes),
            consumed_at=now if consumed else None,
            completion_claimed_at=now if claimed else None,
        )
    )
    return transaction_id


def enroll_credential(
    connection, account_id: UUID, *, credential_id: bytes, public_key: bytes, nickname: str
) -> UUID:
    record_id = uuid4()
    connection.execute(
        insert(webauthn_credentials).values(
            id=record_id,
            platform_account_id=account_id,
            credential_id=credential_id,
            public_key=public_key,
            sign_count=0,
            nickname=nickname,
            created_by_operator="synthetic-operator",
        )
    )
    return record_id


def issue_grant(
    connection,
    account_id: UUID,
    *,
    token_hash: bytes,
    expires_in_minutes: int = 10,
    consumed: bool = False,
) -> UUID:
    grant_id = uuid4()
    now = utcnow()
    connection.execute(
        insert(recovery_grants).values(
            id=grant_id,
            platform_account_id=account_id,
            token_hash=token_hash,
            purpose="emergency_login",
            created_at=now,
            expires_at=now + timedelta(minutes=expires_in_minutes),
            created_by_operator="synthetic-operator",
            audit_correlation_id=uuid4(),
        )
    )
    return grant_id


__all__ = [
    "BOOTSTRAP_ADMIN_ROLE_ID",
    "COUNCIL_ROLE_ID",
    "TEST_GUILD_ID",
    "add_mapping",
    "enroll_credential",
    "issue_grant",
    "link_discord",
    "make_account",
    "seed_membership",
    "seed_oauth_transaction",
    "utcnow",
]
