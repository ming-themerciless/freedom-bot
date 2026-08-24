"""TC-AUTH-09/10, TC-BG-11 and TC-OUT-01 to TC-OUT-04.

Two subjects that share one property: **failing closed is the answer, and failing
closed must not itself destroy state.** A rate limiter that refused everybody
would be a denial of service; a provider outage that wrote "not a member" into
the projection would revoke a guild.
"""
from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select, text

from adapters.database.tables import auth_rate_limits, discord_guild_memberships
from adapters.web.repositories import (
    MembershipProjectionRepository,
    RateLimitRepository,
)
from application.audit import ActorCapability
from application.web.capabilities import (
    AuthMethod,
    MembershipProjection,
    resolve_capabilities,
)
from application.web.providers import ProviderUnavailable
from application.web.rate_limit import LimitedAction, RateLimiter
from tests.web.conftest import seed_membership, utcnow
from tests.web_fixtures import COUNCIL_ROLE_ID, PUBLIC_ORIGIN, TEST_GUILD_ID

pytestmark = pytest.mark.database


# ---------------------------------------------------------------------------
# TC-AUTH-09
# ---------------------------------------------------------------------------


async def test_the_eleventh_oauth_start_from_one_address_is_refused(client):
    """TC-AUTH-09, starts half. N-18: ten per source address per ten minutes."""
    for attempt in range(10):
        response = await client.get("/v1/auth/discord/start")
        assert response.status_code == 303, attempt
        assert "discord.example" in response.headers["location"], attempt

    eleventh = await client.get("/v1/auth/discord/start")
    assert eleventh.status_code == 303
    assert "failure=rate_limited" in eleventh.headers["location"]
    assert "retry-after" in eleventh.headers


async def test_the_twenty_first_callback_from_one_address_is_refused(client):
    """TC-AUTH-09, callbacks half. Twenty, because a callback is cheaper to lose."""
    for _ in range(20):
        response = await client.get("/auth/discord/callback")
        assert "failure=rate_limited" not in response.headers.get("location", "")

    twenty_first = await client.get("/auth/discord/callback")
    assert "failure=rate_limited" in twenty_first.headers["location"]


# ---------------------------------------------------------------------------
# TC-AUTH-10
# ---------------------------------------------------------------------------


def test_the_limiter_counts_across_processes(
    database_url, migrated_database, settings
):
    """TC-AUTH-10. Two instances sharing one database enforce **one** budget.

    This is the property §7 of the delivery plan required and an in-process
    limiter cannot have: two processes each counting to ten is a budget of
    twenty. The counter is one `INSERT … ON CONFLICT DO UPDATE … RETURNING`, so
    two processes cannot both read nine and both write ten.
    """
    second_engine = create_engine(database_url)
    now = utcnow()
    decisions = []
    try:
        for index in range(11):
            # One short transaction per check, alternating engines. Holding both
            # transactions open would not model two processes: the second's
            # `INSERT … ON CONFLICT` would block on the first's uncommitted row
            # for the same key, which is a lock wait rather than a budget.
            engine = migrated_database if index % 2 == 0 else second_engine
            with engine.begin() as connection:
                decisions.append(
                    RateLimiter(
                        RateLimitRepository(connection),
                        settings.rate_limits,
                        settings.client_digest_key,
                    ).check_ip(
                        LimitedAction.OAUTH_START, client_ip="203.0.113.9", now=now
                    )
                )
    finally:
        second_engine.dispose()

    allowed = [decision for decision in decisions if decision.allowed]
    assert len(allowed) == 10, "the two instances did not share one budget"
    assert decisions[-1].allowed is False
    assert decisions[-1].count == 11


def test_the_bucket_name_carries_a_keyed_digest_and_never_the_address(
    migrated_database, settings
):
    """N-30's storage rule. An unkeyed hash of an IPv4 address is the address.

    The space is small enough to enumerate in seconds, so the key is what makes
    the digest a digest rather than an encoding.
    """
    address = "203.0.113.42"
    with migrated_database.begin() as connection:
        RateLimiter(
            RateLimitRepository(connection),
            settings.rate_limits,
            settings.client_digest_key,
        ).check_ip(LimitedAction.OAUTH_START, client_ip=address, now=utcnow())

    with migrated_database.connect() as connection:
        buckets = connection.execute(select(auth_rate_limits.c.bucket)).scalars().all()
    assert buckets
    for bucket in buckets:
        assert address not in bucket
        assert bucket.startswith("oauth_start:ip:")


def test_the_sweep_removes_windows_older_than_the_retention(
    migrated_database, settings
):
    """N-31. Bounds the table's growth without introducing a scheduler."""
    with migrated_database.begin() as connection:
        RateLimitRepository(connection).increment(
            bucket="oauth_start:ip:stale", window_start=utcnow() - timedelta(hours=3)
        )
        RateLimitRepository(connection).increment(
            bucket="oauth_start:ip:fresh", window_start=utcnow()
        )

    with migrated_database.begin() as connection:
        removed = RateLimiter(
            RateLimitRepository(connection),
            settings.rate_limits,
            settings.client_digest_key,
        ).sweep(now=utcnow())

    assert removed == 1
    with migrated_database.connect() as connection:
        remaining = connection.execute(select(auth_rate_limits.c.bucket)).scalars().all()
    assert remaining == ["oauth_start:ip:fresh"]


# ---------------------------------------------------------------------------
# TC-BG-11
# ---------------------------------------------------------------------------


async def test_the_sixth_webauthn_assertion_from_one_address_is_refused(client):
    """TC-BG-11, N-32's per-address assertion half.

    Deliberately lower than N-18: the credential set is two keys held by one
    person, so five attempts in ten minutes from one address is already unusual.

    It is driven through **R-08**, since 2026-08-24 (finding S-7/S3). It used to
    be driven through R-07, which was possible only because both routes shared
    one bucket — so the test that was supposed to prove the assertion budget
    proved it by never making an assertion. Now that the two are separate,
    counting to five here means counting five verification attempts.
    """
    for attempt in range(5):
        response = await client.post(
            "/v1/auth/emergency/webauthn/verify",
            json={},
            headers={"origin": PUBLIC_ORIGIN},
        )
        # A payload with no credential id is refused `invalid` — the point is
        # that the attempt was *counted*, not that it got anywhere.
        assert response.status_code == 403, attempt

    sixth = await client.post(
        "/v1/auth/emergency/webauthn/verify",
        json={},
        headers={"origin": PUBLIC_ORIGIN},
    )
    assert sixth.status_code == 429
    assert sixth.json()["error"] == "rate_limited"
    assert "retry-after" in sixth.headers


async def test_the_eleventh_challenge_from_one_address_is_refused(client):
    """N-32's issuance half, separate from the assertion half (S-7/S3).

    Ten rather than five, and the difference is the finding: minting a challenge
    inserts one short-lived row and verifies nothing, so it is bounded for
    availability and storage while the guess below it is bounded for security.
    While they shared five units, a cancelled prompt spent the guessing budget
    and a completed ceremony spent two of it — about two ceremonies per window
    on the path that exists for the outage.
    """
    for attempt in range(10):
        response = await client.post(
            "/v1/auth/emergency/webauthn/options",
            json={},
            headers={"origin": PUBLIC_ORIGIN},
        )
        assert response.status_code == 200, attempt

    eleventh = await client.post(
        "/v1/auth/emergency/webauthn/options",
        json={},
        headers={"origin": PUBLIC_ORIGIN},
    )
    assert eleventh.status_code == 429
    assert eleventh.json()["error"] == "rate_limited"
    assert "retry-after" in eleventh.headers


async def test_a_full_ceremony_spends_one_unit_of_each_budget(client):
    """The arithmetic S-7 was about, asserted rather than reasoned.

    Ten complete issue-then-verify pairs from one address: every issuance is
    served, and the assertion budget — not the issuance budget — is what stops
    the sixth verification. A cancelled ceremony (an issuance with no
    verification) therefore costs the operator nothing they need for the next
    attempt, which is the availability property the finding asked for.
    """
    issued = 0
    verified = 0
    for _ in range(10):
        options = await client.post(
            "/v1/auth/emergency/webauthn/options",
            json={},
            headers={"origin": PUBLIC_ORIGIN},
        )
        if options.status_code == 200:
            issued += 1
        verify = await client.post(
            "/v1/auth/emergency/webauthn/verify",
            json={},
            headers={"origin": PUBLIC_ORIGIN},
        )
        if verify.status_code != 429:
            verified += 1

    assert issued == 10
    assert verified == 5


async def test_the_fourth_recovery_attempt_from_one_address_is_refused(client):
    """TC-BG-11, N-33's per-address half. A grant is single use; three tries is generous."""
    data = {"token": "not-a-real-token"}
    headers = {"origin": PUBLIC_ORIGIN}
    for _ in range(3):
        response = await client.post(
            "/v1/auth/emergency/recovery", data=data, headers=headers
        )
        assert "failure=rate_limited" not in response.headers.get("location", "")

    fourth = await client.post(
        "/v1/auth/emergency/recovery", data=data, headers=headers
    )
    assert "failure=rate_limited" in fourth.headers["location"]


# ---------------------------------------------------------------------------
# TC-OUT-01 to TC-OUT-04
# ---------------------------------------------------------------------------


def _projection(observed_at):
    return MembershipProjection(
        guild_id=TEST_GUILD_ID,
        is_member=True,
        role_ids=frozenset({COUNCIL_ROLE_ID}),
        observed_at=observed_at,
    )


def test_a_projection_within_the_grace_still_authorizes_a_read(settings):
    """TC-OUT-01. N-10: protected reads proceed for at most fifteen minutes.

    The grace is measured from the last **successful** observation, not from the
    moment the outage was noticed — which is the only definition that cannot be
    extended by the outage continuing.
    """
    now = utcnow()
    projection = _projection(now - timedelta(minutes=14))

    assert not projection.is_fresh(
        now=now, cache_seconds=settings.bounds.membership_cache_seconds
    )
    assert projection.within_grace(
        now=now, grace_seconds=settings.bounds.membership_grace_seconds
    )


def test_a_projection_past_the_grace_authorizes_nothing(settings):
    """TC-OUT-03. After the grace, fail closed — no cached role is proof."""
    now = utcnow()
    projection = _projection(now - timedelta(minutes=16))

    assert not projection.within_grace(
        now=now, grace_seconds=settings.bounds.membership_grace_seconds
    )


def test_a_provider_failure_never_writes_an_absence(migrated_database):
    """TC-OUT-04. "Refresh failed" and "membership absent" are different facts.

    The projection writer is only ever called with a *successful* observation.
    A 429 storm recorded as `is_member = false` would revoke a guild, which is
    why the outage path raises instead of writing.
    """
    discord_id = 700000000000020001
    with migrated_database.begin() as connection:
        seed_membership(
            connection, discord_user_id=discord_id, role_ids=frozenset({COUNCIL_ROLE_ID})
        )

    with migrated_database.connect() as connection:
        before = MembershipProjectionRepository(connection).load(
            discord_user_id=discord_id, guild_id=TEST_GUILD_ID
        )
    assert before.is_member

    # The adapter's failure path raises; nothing here calls `record`.
    with pytest.raises(ProviderUnavailable):
        raise ProviderUnavailable("429 from the provider")

    with migrated_database.connect() as connection:
        after = MembershipProjectionRepository(connection).load(
            discord_user_id=discord_id, guild_id=TEST_GUILD_ID
        )
        rows = connection.execute(
            select(discord_guild_memberships.c.active).where(
                discord_guild_memberships.c.discord_user_id == discord_id
            )
        ).scalars().all()
    assert after.is_member
    assert rows == [True]


def test_a_revoked_membership_removes_every_capability(migrated_database):
    """TC-SESS-06 / caller state `N`. The session survives; the authority does not.

    That is the distinction SM-02's outage row draws: authentication did not
    fail, authorization freshness did — and when the projection says *not a
    member*, the answer is no capability at all rather than a stale one.
    """
    account_id = uuid4()
    revoked = MembershipProjection(
        guild_id=TEST_GUILD_ID,
        is_member=False,
        role_ids=frozenset({COUNCIL_ROLE_ID}),
        observed_at=utcnow(),
    )
    context = resolve_capabilities(
        account_id=account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        membership=revoked,
        mappings=(),
    )
    assert context.capabilities == frozenset()
    assert not context.guild_member
    assert not context.guild_council


def test_a_role_revoked_at_the_provider_stops_granting_capability(migrated_database):
    """TC-SESS-06. Capability comes from the *current* projection, every time.

    Nothing reads a role from the session row, so removing the role from the
    projection is sufficient — there is no second place holding a copy that would
    have to be invalidated as well.
    """
    from application.web.capabilities import MappingProvenance, RoleCapabilityMapping

    council = RoleCapabilityMapping(
        id=uuid4(),
        guild_id=TEST_GUILD_ID,
        role_id=COUNCIL_ROLE_ID,
        capability=ActorCapability.GUILD_COUNCIL,
        provenance=MappingProvenance.ORDINARY,
    )
    account_id = uuid4()

    with_role = resolve_capabilities(
        account_id=account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        membership=_projection(utcnow()),
        mappings=[council],
    )
    assert with_role.guild_council

    without_role = resolve_capabilities(
        account_id=account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        membership=MembershipProjection(
            guild_id=TEST_GUILD_ID,
            is_member=True,
            role_ids=frozenset(),
            observed_at=utcnow(),
        ),
        mappings=[council],
    )
    assert not without_role.guild_council
    assert without_role.guild_member
    # A different capability set is a different fingerprint, which is what N-08
    # rotates on.
    assert with_role.privilege_fingerprint != without_role.privilege_fingerprint
