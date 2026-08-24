"""TC-BG-21: a refused redemption is one answer to the caller and four to the audit.

Raised as S-9 by the 2026-08-24 supervised session and confirmed as S4 by the
independent security review. SP-21 proved the *behaviour* — a host-issued grant
was used exactly once, refused on replay, and refused again after expiry — and
in proving it exposed the forensic gap: both refusals wrote **byte-identical**
audit payloads, `{"reason": "grant_not_live"}`, naming no grant at all.

Those two events mean opposite things. A replayed grant is somebody presenting a
token that has already been spent, which is a compromise signal. An expired one
is an operator who was slow, which is a Tuesday. An incident reviewer reading
the audit could not tell them apart, and could not tell *which grant* either
concerned.

The caller must continue to see neither distinction — that is deliberate and
unchanged — so the whole correction lives on the audit side:

* the single conditional `UPDATE` still decides consumption, alone;
* a **read-only** classification runs only after it has matched zero rows; and
* the response stays the same neutral `invalid`, with no new timing branch.
"""
from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select

from adapters.database.tables import audit_events, recovery_grants
from application.web.crypto import mint_token, token_hash
from application.web.errors import AuthenticationFailure
from tests.web.conftest import issue_grant, make_account, utcnow
from tests.web_fixtures import PUBLIC_ORIGIN

pytestmark = pytest.mark.database


@pytest.fixture()
def faulted_provider(provider):
    provider.unavailable = True
    return provider


@pytest.fixture()
def protected_account(migrated_database):
    with migrated_database.begin() as connection:
        return make_account(
            connection, protected=True, label="Server Administrator"
        )


def _from(address: str) -> dict:
    return {"origin": PUBLIC_ORIGIN, "x-forwarded-for": address}


def _refusal_payloads(engine):
    with engine.connect() as connection:
        return connection.execute(
            select(audit_events.c.payload).where(
                audit_events.c.action == "auth.emergency.refused"
            )
        ).scalars().all()


async def _redeem(client, token, *, address):
    return await client.post(
        "/v1/auth/emergency/recovery", data={"token": token}, headers=_from(address)
    )


async def test_a_replayed_grant_is_audited_as_consumed_and_names_its_record(
    client, migrated_database, faulted_provider, protected_account
):
    """The compromise signal. Same `invalid` to the caller, `consumed` to the audit."""
    token = mint_token()
    with migrated_database.begin() as connection:
        grant_id = issue_grant(
            connection, protected_account, token_hash=token_hash(token)
        )

    first = await _redeem(client, token, address="198.51.100.61")
    assert first.headers["location"] == "/v1/admin/role-capabilities"

    replay = await _redeem(client, token, address="198.51.100.62")
    assert replay.status_code == 303
    assert "failure=invalid" in replay.headers["location"]

    payloads = _refusal_payloads(migrated_database)
    assert len(payloads) == 1
    assert payloads[0] == {"reason": "consumed", "grant_record_id": str(grant_id)}


async def test_an_expired_grant_is_audited_as_expired_and_names_its_record(
    client, migrated_database, faulted_provider, protected_account
):
    """The delay. Indistinguishable from a replay outside, distinct inside.

    The grant is aged by moving its `expires_at` behind `now` rather than by
    waiting: the property under test is which branch the classification takes,
    and a fifteen-minute test would be evidence of nothing better.
    """
    token = mint_token()
    with migrated_database.begin() as connection:
        grant_id = issue_grant(
            connection, protected_account, token_hash=token_hash(token)
        )
        connection.execute(
            recovery_grants.update()
            .where(recovery_grants.c.id == grant_id)
            .values(
                created_at=utcnow() - timedelta(minutes=30),
                expires_at=utcnow() - timedelta(minutes=20),
            )
        )

    refused = await _redeem(client, token, address="198.51.100.63")
    assert refused.status_code == 303
    assert "failure=invalid" in refused.headers["location"]

    payloads = _refusal_payloads(migrated_database)
    assert len(payloads) == 1
    assert payloads[0] == {"reason": "expired", "grant_record_id": str(grant_id)}


async def test_an_invalidated_grant_is_audited_as_invalidated(
    client, composition, migrated_database, faulted_provider, protected_account
):
    """N-61's superseded grant — the state a stale token an attacker holds is in."""
    token = mint_token()
    with migrated_database.begin() as connection:
        grant_id = issue_grant(
            connection, protected_account, token_hash=token_hash(token)
        )
        composition.services(connection).grants.invalidate_all(
            account_id=protected_account, reason="superseded_by_new_grant"
        )

    refused = await _redeem(client, token, address="198.51.100.64")
    assert "failure=invalid" in refused.headers["location"]

    payloads = _refusal_payloads(migrated_database)
    assert len(payloads) == 1
    assert payloads[0] == {"reason": "invalidated", "grant_record_id": str(grant_id)}


async def test_a_token_matching_no_grant_stays_unknown_and_names_nothing(
    client, migrated_database, faulted_provider, protected_account
):
    """`unknown` is a real answer, and the row it names is no row.

    An invented token must not acquire a grant reference by accident, because a
    reference is a claim that some grant was involved. It also must not be
    distinguishable to the caller from any of the three above.
    """
    refused = await _redeem(client, mint_token(), address="198.51.100.65")
    assert "failure=invalid" in refused.headers["location"]

    payloads = _refusal_payloads(migrated_database)
    assert len(payloads) == 1
    assert payloads[0] == {"reason": "unknown"}


async def test_the_four_outcomes_are_one_answer_to_the_caller(
    client, composition, migrated_database, faulted_provider, protected_account
):
    """The disclosure half, asserted as equality rather than described.

    Consumed, expired, invalidated and unknown must produce the same status, the
    same failure code and the same shape of response. Only the correlation
    reference differs, and it differs on every request by design.

    The four states are staged **one at a time** because N-61 allows the account
    only one live grant: an expired-but-unconsumed grant still occupies that
    slot, which is the index doing its job rather than an inconvenience.
    """
    seen = []

    def observe(response):
        location = response.headers["location"]
        seen.append((response.status_code, location.split("&correlation=", 1)[0]))

    # Consumed: redeemed once, then replayed.
    consumed = mint_token()
    with migrated_database.begin() as connection:
        issue_grant(connection, protected_account, token_hash=token_hash(consumed))
    await _redeem(client, consumed, address="203.0.116.1")
    observe(await _redeem(client, consumed, address="203.0.116.2"))

    # Expired: issued into the freed slot, then aged past its ceiling.
    expired = mint_token()
    with migrated_database.begin() as connection:
        aged = issue_grant(
            connection, protected_account, token_hash=token_hash(expired)
        )
        connection.execute(
            recovery_grants.update()
            .where(recovery_grants.c.id == aged)
            .values(
                created_at=utcnow() - timedelta(minutes=30),
                expires_at=utcnow() - timedelta(minutes=20),
            )
        )
    observe(await _redeem(client, expired, address="203.0.116.3"))

    # Invalidated: the aged row is superseded, which frees the slot for one that
    # is invalidated while still inside its window.
    invalidated = mint_token()
    with migrated_database.begin() as connection:
        services = composition.services(connection)
        services.grants.invalidate_all(
            account_id=protected_account, reason="superseded_by_new_grant"
        )
    with migrated_database.begin() as connection:
        services = composition.services(connection)
        issue_grant(
            connection, protected_account, token_hash=token_hash(invalidated)
        )
        services.grants.invalidate_all(
            account_id=protected_account, reason="superseded_by_new_grant"
        )
    observe(await _redeem(client, invalidated, address="203.0.116.4"))

    # Unknown: a well-formed token matching no row at all.
    observe(await _redeem(client, mint_token(), address="203.0.116.5"))

    assert len(set(seen)) == 1, seen
    assert seen[0] == (303, "/v1/auth/emergency?failure=invalid")

    reasons = sorted(
        payload["reason"] for payload in _refusal_payloads(migrated_database)
    )
    assert reasons == ["consumed", "expired", "invalidated", "unknown"]


def test_the_classification_never_consumes_and_never_writes(
    migrated_database, composition, faulted_provider, protected_account
):
    """The property that makes the correction safe: the read changes nothing.

    Atomic consumption is still the single conditional `UPDATE`. This asserts it
    directly — a live grant classified twice is still live, still unconsumed,
    and its attempt counter is untouched, because `classify_refusal` reads.
    """
    token = mint_token()
    with migrated_database.begin() as connection:
        grant_id = issue_grant(
            connection, protected_account, token_hash=token_hash(token)
        )

    with migrated_database.begin() as connection:
        grants = composition.services(connection).grants
        for _ in range(2):
            refusal = grants.classify_refusal(
                token_hash=token_hash(token), now=utcnow()
            )
            # A live grant reaches this only through a lost race, and the branch
            # says so; what matters here is that asking did nothing.
            assert refusal.grant_id == grant_id

    with migrated_database.connect() as connection:
        row = connection.execute(
            select(recovery_grants).where(recovery_grants.c.id == grant_id)
        ).mappings().one()
    assert row["consumed_at"] is None
    assert row["invalidated_at"] is None
    assert row["attempt_count"] == 0


def test_no_token_or_hash_reaches_a_refusal_payload(
    migrated_database, composition, faulted_provider, protected_account
):
    """N-14's rule, re-asserted for the payload that gained a field.

    The correction added a grant **record id**. It must not have added anything
    derived from the token, whose hash is the one thing in the row that could be
    replayed against the table.
    """
    token = mint_token()
    hashed = token_hash(token)
    with migrated_database.begin() as connection:
        issue_grant(connection, protected_account, token_hash=hashed)
        composition.services(connection).grants.invalidate_all(
            account_id=protected_account, reason="superseded_by_new_grant"
        )

    with pytest.raises(AuthenticationFailure) as refusal:
        with migrated_database.begin() as connection:
            composition.services(connection).break_glass.redeem_recovery_grant(
                token=token,
                now=utcnow(),
                correlation_id=uuid4(),
                client_ip_hash=None,
                user_agent_digest=None,
            )

    assert refusal.value.code == "invalid"
    rendered = str(refusal.value.audit.payload)
    assert token not in rendered
    assert hashed.hex() not in rendered
