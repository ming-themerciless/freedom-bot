"""TC-BG-18: every counted break-glass refusal writes exactly one audit event.

Raised as S-5 by the 2026-08-24 supervised session and confirmed as S1 by the
independent security review. The defect was found by reading the rows a real
ceremony wrote, not by reading code: the operator was shown a correlation
reference for a rate-limited emergency attempt, and the reference resolved to
nothing at all, because the limiter boundaries returned a `429` or a redirect
and wrote no audit record.

That is the exact inverse of what the control is for. SM-03's accepted statement
is that **every** emergency attempt and outcome is audited, and an attacker who
reached a limiter could make the emergency audit stream fall silent at precisely
the moment the defensive control activated.

Every test here drives the real routes against PostgreSQL and asserts three
things about each boundary: that a row exists, that there is exactly **one** of
it, and that it carries the correlation id the caller was actually shown.
"""
from __future__ import annotations

import pytest
from sqlalchemy import select
from webauthn.helpers import bytes_to_base64url

from adapters.database.tables import audit_events
from application.audit import ActorCapability
from application.web.crypto import mint_token, token_hash
from tests.web.conftest import enroll_credential, issue_grant, make_account, utcnow
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


def _from(address: str) -> dict:
    """Headers for one request from one source address (see TC-BG-16's note)."""
    return {"origin": PUBLIC_ORIGIN, "x-forwarded-for": address}


def _refusals(engine, *, reason: str | None = None):
    """Every `auth.emergency.refused` row, optionally narrowed to one reason."""
    with engine.connect() as connection:
        rows = connection.execute(
            select(
                audit_events.c.correlation_id,
                audit_events.c.payload,
                audit_events.c.actor_capability,
                audit_events.c.actor_platform_account_id,
                audit_events.c.actor_discord_user_id,
                audit_events.c.entity_type,
            ).where(audit_events.c.action == "auth.emergency.refused")
        ).mappings().all()
    if reason is None:
        return list(rows)
    return [row for row in rows if row["payload"].get("reason") == reason]


def _correlation_of(response) -> str:
    """The reference the caller was shown, from wherever this route puts it."""
    if response.headers.get("content-type", "").startswith("application/json"):
        return response.json()["correlation_id"]
    location = response.headers["location"]
    return location.split("correlation=", 1)[1].split("&", 1)[0]


def _assert_one_refusal_matching(engine, response, *, reason: str, account_id=None):
    """The three properties every counted refusal owes, asserted together."""
    matching = _refusals(engine, reason=reason)
    assert len(matching) == 1, f"expected exactly one {reason} event, got {matching}"
    row = matching[0]
    assert str(row["correlation_id"]) == _correlation_of(response)
    assert row["actor_capability"] == ActorCapability.SYSTEM.value
    # No caller is identified by one of these rows, and nothing the caller sent
    # appears in it: the payload carries a closed reason and nothing else.
    assert row["actor_discord_user_id"] is None
    assert set(row["payload"]) <= {"reason"}
    if account_id is None:
        assert row["actor_platform_account_id"] is None
    else:
        assert row["actor_platform_account_id"] == account_id


# ---------------------------------------------------------------------------
# R-07 — challenge issuance
# ---------------------------------------------------------------------------


async def test_the_challenge_limiter_refusal_is_audited_once(
    client, migrated_database, faulted_provider
):
    """N-32's issuance budget, refused and recorded.

    The ten permitted issuances write nothing — they are not refusals — so the
    single row this leaves behind is the eleventh attempt's, and it is the whole
    audit trail of a boundary that used to leave none.
    """
    for attempt in range(10):
        allowed = await client.post(
            "/v1/auth/emergency/webauthn/options",
            json={},
            headers=_from("198.51.100.10"),
        )
        assert allowed.status_code == 200, attempt

    refused = await client.post(
        "/v1/auth/emergency/webauthn/options",
        json={},
        headers=_from("198.51.100.10"),
    )
    assert refused.status_code == 429
    assert refused.json()["error"] == "rate_limited"

    assert len(_refusals(migrated_database)) == 1
    _assert_one_refusal_matching(
        migrated_database, refused, reason="challenge_rate_limited_ip"
    )


# ---------------------------------------------------------------------------
# R-08 — assertion verification
# ---------------------------------------------------------------------------


async def test_the_assertion_address_limiter_refusal_is_audited_once(
    client, migrated_database, faulted_provider, protected_account
):
    """N-32's per-address assertion budget, refused and recorded."""
    for attempt in range(5):
        spent = await client.post(
            "/v1/auth/emergency/webauthn/verify",
            json={},
            headers=_from("198.51.100.20"),
        )
        assert spent.status_code == 403, attempt

    refused = await client.post(
        "/v1/auth/emergency/webauthn/verify",
        json={},
        headers=_from("198.51.100.20"),
    )
    assert refused.status_code == 429
    _assert_one_refusal_matching(
        migrated_database, refused, reason="assertion_rate_limited_ip"
    )


async def test_the_per_account_budget_refusal_names_the_account_it_protected(
    client, migrated_database, faulted_provider, authenticator, protected_account
):
    """N-32's per-account budget, refused, recorded, and **attributed**.

    The account id is the forensically useful half: an operator reading this row
    learns that the protected administrator account is the one under sustained
    attack, rather than that some address somewhere was throttled. It is a
    reference to one of our own rows — never anything the caller supplied.
    """
    payload = {"rawId": bytes_to_base64url(authenticator.credential_id)}
    for attempt in range(10):
        spent = await client.post(
            "/v1/auth/emergency/webauthn/verify",
            json=payload,
            headers=_from(f"203.0.113.{attempt + 1}"),
        )
        assert spent.status_code == 403, attempt

    refused = await client.post(
        "/v1/auth/emergency/webauthn/verify",
        json=payload,
        headers=_from("203.0.113.200"),
    )
    assert refused.status_code == 429
    _assert_one_refusal_matching(
        migrated_database,
        refused,
        reason="assertion_rate_limited_account",
        account_id=protected_account,
    )


async def test_the_per_credential_budget_refusal_names_no_account_and_no_credential(
    client, migrated_database, faulted_provider, protected_account
):
    """The same boundary for a credential id that resolves to nothing.

    Two properties at once. The audit **distinguishes** it from the account
    bucket, which is what an investigator needs; the caller **cannot**, which is
    the account-existence property `check_credential` exists for — so the id the
    caller invented appears in no row, and no account is named.
    """
    invented = b"no-such-credential-id-000099"
    payload = {"rawId": bytes_to_base64url(invented)}
    for attempt in range(10):
        spent = await client.post(
            "/v1/auth/emergency/webauthn/verify",
            json=payload,
            headers=_from(f"203.0.114.{attempt + 1}"),
        )
        assert spent.status_code == 403, attempt

    refused = await client.post(
        "/v1/auth/emergency/webauthn/verify",
        json=payload,
        headers=_from("203.0.114.200"),
    )
    assert refused.status_code == 429
    _assert_one_refusal_matching(
        migrated_database, refused, reason="assertion_rate_limited_credential"
    )
    for row in _refusals(migrated_database):
        assert invented.hex() not in str(row["payload"])


async def test_a_malformed_body_is_counted_and_audited(
    client, migrated_database, faulted_provider
):
    """A body that is not JSON is a counted attempt, not a free probe.

    It used to be refused *before* the limiter, which made it the one emergency
    refusal an attacker could repeat without spending anything — and being
    unbounded, it could not safely be audited either. Counting it first makes it
    both counted and recordable, and N-32 bounds how many rows it can cause.
    """
    refused = await client.post(
        "/v1/auth/emergency/webauthn/verify",
        content=b"{not json",
        headers={**_from("198.51.100.30"), "content-type": "application/json"},
    )
    assert refused.status_code == 400
    assert refused.json()["error"] == "invalid"
    _assert_one_refusal_matching(
        migrated_database, refused, reason="malformed_request_body"
    )


# ---------------------------------------------------------------------------
# R-09 — recovery redemption
# ---------------------------------------------------------------------------


async def test_the_recovery_address_limiter_refusal_is_audited_once(
    client, migrated_database, faulted_provider, protected_account
):
    """N-33's per-address budget, refused and recorded."""
    data = {"token": mint_token()}
    for attempt in range(3):
        spent = await client.post(
            "/v1/auth/emergency/recovery", data=data, headers=_from("198.51.100.40")
        )
        assert "failure=rate_limited" not in spent.headers["location"], attempt

    refused = await client.post(
        "/v1/auth/emergency/recovery", data=data, headers=_from("198.51.100.40")
    )
    assert "failure=rate_limited" in refused.headers["location"]
    _assert_one_refusal_matching(
        migrated_database, refused, reason="recovery_rate_limited_ip"
    )


async def test_an_empty_recovery_token_is_counted_and_audited(
    client, migrated_database, faulted_provider, protected_account
):
    """An empty `token` field is a counted attempt, for the malformed-body reason."""
    refused = await client.post(
        "/v1/auth/emergency/recovery",
        data={"token": ""},
        headers=_from("198.51.100.50"),
    )
    assert refused.status_code == 303
    assert "failure=invalid" in refused.headers["location"]
    _assert_one_refusal_matching(
        migrated_database, refused, reason="recovery_token_absent"
    )


async def test_a_refused_attempt_writes_one_event_and_not_two(
    client, composition, migrated_database, faulted_provider, protected_account
):
    """The at-most-once property of the recorder, at a boundary that has both kinds.

    The per-grant cap is described by the *service* as a `FailureAudit` and
    committed by the *route*; the per-address limiter is recorded by the route
    directly. One attempt can only ever produce one row, whichever of the two
    reaches the recorder first — which is what makes a reviewer counting refused
    emergency attempts able to count rows.
    """
    token = mint_token()
    with migrated_database.begin() as connection:
        issue_grant(connection, protected_account, token_hash=token_hash(token))
        # Invalidated through the repository, as TC-BG-17 does: this is the state
        # C-01 leaves a superseded grant in, so every attempt below reaches the
        # row and every one of them is refused.
        composition.services(connection).grants.invalidate_all(
            account_id=protected_account, reason="superseded_by_new_grant"
        )

    # Five attempts from five addresses spend the per-grant cap without ever
    # meeting the per-address budget; the sixth is the cap's own refusal.
    for attempt in range(5):
        await client.post(
            "/v1/auth/emergency/recovery",
            data={"token": token},
            headers=_from(f"203.0.115.{attempt + 1}"),
        )
    sixth = await client.post(
        "/v1/auth/emergency/recovery",
        data={"token": token},
        headers=_from("203.0.115.200"),
    )
    assert "failure=rate_limited" in sixth.headers["location"]

    correlation = _correlation_of(sixth)
    for_this_attempt = [
        row
        for row in _refusals(migrated_database)
        if str(row["correlation_id"]) == correlation
    ]
    assert len(for_this_attempt) == 1
    assert for_this_attempt[0]["payload"]["reason"] == "grant_attempt_cap"
