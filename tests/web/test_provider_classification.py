"""What the **real** `DiscordIdentityProvider` does with every answer Discord can give.

The portal's refusal boundary can only classify what the adapter classifies, and
`FakeDiscordProvider` raises the classified exceptions directly — so it proves the
route's behaviour and says nothing about which HTTP answers produce which
exception. These tests drive the production adapter through
`httpx.MockTransport`, which is the layer below it: no socket is opened, no host
is resolved, and **no real Discord application or guild is contacted**.

The distinction being tested is load-bearing. `ProviderUnavailable` must never be
written into the membership projection as an absence — a 429 storm classified as
"not a member" would revoke a guild (TC-OUT-04). `ProviderRefused` is a definite
negative answer. And a payload the adapter cannot read is `ProviderRefused` too,
rather than the unhandled `500` it used to be: a proxy error page, a version
change or a truncated body is expected behaviour at a network boundary, and N-25
forbids answering the browser with internal detail.

One answer is deliberately neither: a `404` from the guild-member read is a
**fact** — this person authorized the application and is not in the guild.
"""
from __future__ import annotations

import json

import httpx
import pytest

from adapters.web.discord_provider import DiscordIdentityProvider
from application.web.providers import (
    ProviderRefused,
    ProviderTokens,
    ProviderUnavailable,
)
from tests.web_fixtures import TEST_GUILD_ID, web_settings

# Nothing in this module touches the database or opens a socket.

TOKEN_PATH = "/oauth2/token"
USER_PATH = "/users/@me"
MEMBER_PATH = f"/users/@me/guilds/{TEST_GUILD_ID}/member"

VALID_TOKEN_BODY = {
    "access_token": "provider-access-token",
    "refresh_token": "provider-refresh-token",
    "expires_in": 604800,
    "scope": "identify guilds.members.read",
}
VALID_USER_BODY = {"id": "700000000000000009", "username": "someone"}
VALID_MEMBER_BODY = {"roles": ["900000000000000003"]}


def _provider(tmp_path, handler) -> DiscordIdentityProvider:
    settings = web_settings(tmp_path).discord
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return DiscordIdentityProvider(settings, client=client)


def _tokens() -> ProviderTokens:
    from datetime import datetime, timedelta, timezone

    return ProviderTokens(
        # The Discord adapter refuses another provider's tokens before its first
        # request, so a token result for `verify()` has to name it.
        provider_key="discord",
        access_token="provider-access-token",
        refresh_token=None,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        scopes="identify guilds.members.read",
    )


def _router(script: dict[str, object]):
    """Answer each path suffix from a script.

    An unscripted request raises rather than defaulting: a test that reaches a
    call it did not plan for is a test whose subject moved, and a permissive
    default would hide that.
    """

    def handler(request: httpx.Request) -> httpx.Response:
        for suffix, answer in script.items():
            if request.url.path.endswith(suffix):
                if isinstance(answer, Exception):
                    raise answer
                assert isinstance(answer, httpx.Response)
                return answer
        raise AssertionError(f"unscripted request to {request.url}")

    return handler


def _json(status: int, body) -> httpx.Response:
    return httpx.Response(
        status,
        content=json.dumps(body).encode(),
        headers={"content-type": "application/json"},
    )


def _raw(status: int, body: bytes, content_type: str = "text/html") -> httpx.Response:
    return httpx.Response(status, content=body, headers={"content-type": content_type})


# ---------------------------------------------------------------------------
# The exchange
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("label", "answer", "expected"),
    [
        ("transport failure", httpx.ConnectError("no route to host"), ProviderUnavailable),
        ("read timeout", httpx.ReadTimeout("timed out"), ProviderUnavailable),
        ("429 rate limited", _json(429, {"retry_after": 3}), ProviderUnavailable),
        ("500 internal", _json(500, {"message": "boom"}), ProviderUnavailable),
        ("503 unavailable", _raw(503, b"<html>maintenance</html>"), ProviderUnavailable),
        ("400 invalid grant", _json(400, {"error": "invalid_grant"}), ProviderRefused),
        ("401 unauthorized", _json(401, {"error": "invalid_client"}), ProviderRefused),
        ("200 with no access token", _json(200, {"token_type": "Bearer"}), ProviderRefused),
        ("200 with a null access token", _json(200, {"access_token": None}), ProviderRefused),
        ("200 that is not JSON", _raw(200, b"<html>proxy error</html>"), ProviderRefused),
        ("200 that is a JSON array", _json(200, [1, 2, 3]), ProviderRefused),
        ("200 that is a JSON string", _json(200, "ok"), ProviderRefused),
        ("200 with an empty body", _raw(200, b"", "application/json"), ProviderRefused),
    ],
)
async def test_the_exchange_classifies_every_provider_answer(
    tmp_path, label, answer, expected
):
    """Outage and refusal are separated at the adapter, where the status lives."""
    provider = _provider(tmp_path, _router({TOKEN_PATH: answer}))
    try:
        with pytest.raises(expected):
            await provider.exchange(code="a-code", code_verifier="a-verifier")
    finally:
        await provider.aclose()


async def test_a_refusal_carries_none_of_the_providers_body(tmp_path):
    """N-25 at the boundary: the provider's text goes nowhere, not even into `str(error)`."""
    secret_body = {"error": "invalid_grant", "hint": "client_secret=SUPERSECRET"}
    provider = _provider(
        tmp_path, _router({TOKEN_PATH: _json(400, secret_body)})
    )
    try:
        with pytest.raises(ProviderRefused) as raised:
            await provider.exchange(code="a-code", code_verifier="a-verifier")
    finally:
        await provider.aclose()
    assert "SUPERSECRET" not in str(raised.value)
    assert "invalid_grant" not in str(raised.value)


@pytest.mark.parametrize(
    ("expires_in", "at_least_seconds"),
    [(604800, 604800), ("3600", 3600), ("soon", 60), (None, 60), (0, 60), (-5, 60)],
)
async def test_an_unreadable_lifetime_is_clamped_rather_than_raised(
    tmp_path, expires_in, at_least_seconds
):
    """A lifetime the adapter cannot read is a *short* lifetime, not a failure.

    The token is usable and the platform simply refreshes sooner. Raising here
    would turn a cosmetic provider change into a login outage.
    """
    from datetime import datetime, timezone

    body = dict(VALID_TOKEN_BODY, expires_in=expires_in)
    provider = _provider(
        tmp_path, _router({TOKEN_PATH: _json(200, body)})
    )
    try:
        tokens = await provider.exchange(code="a-code", code_verifier="a-verifier")
    finally:
        await provider.aclose()
    lifetime = (tokens.expires_at - datetime.now(timezone.utc)).total_seconds()
    assert lifetime >= at_least_seconds - 5


# ---------------------------------------------------------------------------
# Verification: the identity read
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("label", "answer", "expected"),
    [
        ("transport failure", httpx.ConnectError("down"), ProviderUnavailable),
        ("429", _json(429, {}), ProviderUnavailable),
        ("502", _raw(502, b"bad gateway"), ProviderUnavailable),
        ("401", _json(401, {"message": "401: Unauthorized"}), ProviderRefused),
        ("not JSON", _raw(200, b"<html/>"), ProviderRefused),
        ("a JSON array", _json(200, [{"id": "1"}]), ProviderRefused),
        ("no id at all", _json(200, {"username": "someone"}), ProviderRefused),
        ("a non-numeric id", _json(200, {"id": "not-a-snowflake"}), ProviderRefused),
        ("an id that is an object", _json(200, {"id": {"nested": 1}}), ProviderRefused),
        ("an empty id", _json(200, {"id": ""}), ProviderRefused),
    ],
)
async def test_the_identity_read_classifies_every_provider_answer(
    tmp_path, label, answer, expected
):
    """A malformed subject is a refusal. An identity is the one thing never guessed at."""
    provider = _provider(
        tmp_path,
        _router({TOKEN_PATH: _json(200, VALID_TOKEN_BODY), USER_PATH: answer}),
    )
    try:
        with pytest.raises(expected):
            await provider.verify(_tokens())
    finally:
        await provider.aclose()


# ---------------------------------------------------------------------------
# Verification: the guild-member read
# ---------------------------------------------------------------------------


async def test_a_404_from_the_member_read_is_a_fact_and_not_an_outage(tmp_path):
    """The one non-2xx answer that is not an error: this person is not in the guild."""
    provider = _provider(
        tmp_path,
        _router({USER_PATH: _json(200, VALID_USER_BODY), MEMBER_PATH: _json(404, {})}),
    )
    try:
        identity = await provider.verify(_tokens())
    finally:
        await provider.aclose()
    assert identity.membership is not None
    assert identity.membership.is_member is False
    assert identity.membership.role_ids == frozenset()


@pytest.mark.parametrize(
    ("label", "answer", "expected"),
    [
        ("transport failure", httpx.ConnectTimeout("down"), ProviderUnavailable),
        ("429", _json(429, {}), ProviderUnavailable),
        ("500", _json(500, {}), ProviderUnavailable),
        ("403", _json(403, {"message": "Missing Access"}), ProviderRefused),
        ("not JSON", _raw(200, b"nope"), ProviderRefused),
        ("a JSON array", _json(200, ["roles"]), ProviderRefused),
    ],
)
async def test_the_member_read_classifies_every_other_provider_answer(
    tmp_path, label, answer, expected
):
    """An outage during the member read must never be recorded as an absence."""
    provider = _provider(
        tmp_path,
        _router({USER_PATH: _json(200, VALID_USER_BODY), MEMBER_PATH: answer}),
    )
    try:
        with pytest.raises(expected):
            await provider.verify(_tokens())
    finally:
        await provider.aclose()


@pytest.mark.parametrize(
    ("roles", "expected"),
    [
        (["900000000000000003"], {900000000000000003}),
        ([], set()),
        (None, set()),
        ("900000000000000003", set()),
        ({"a": "b"}, set()),
        (["not-a-snowflake", "900000000000000003"], {900000000000000003}),
        ([True, False], set()),
        ([{"id": "900000000000000003"}], set()),
    ],
)
async def test_an_unreadable_roles_array_yields_fewer_roles_and_never_more(
    tmp_path, roles, expected
):
    """Fails closed. A role id that cannot be read is a role that was not granted.

    It is deliberately not an exception either: an unexpected roles shape would
    otherwise lock every member out of the portal on a provider change, and the
    conservative reading — no capability from a role we cannot name — is safe.
    """
    provider = _provider(
        tmp_path,
        _router(
            {
                USER_PATH: _json(200, VALID_USER_BODY),
                MEMBER_PATH: _json(200, {"roles": roles}),
            }
        ),
    )
    try:
        identity = await provider.verify(_tokens())
    finally:
        await provider.aclose()
    assert identity.membership is not None
    assert identity.membership.is_member is True
    assert identity.membership.role_ids == frozenset(expected)


async def test_a_complete_verification_reads_the_subject_and_the_roles(tmp_path):
    """The positive control: without it, every assertion above could pass vacuously."""
    provider = _provider(
        tmp_path,
        _router(
            {
                USER_PATH: _json(200, VALID_USER_BODY),
                MEMBER_PATH: _json(200, VALID_MEMBER_BODY),
            }
        ),
    )
    try:
        identity = await provider.verify(_tokens())
    finally:
        await provider.aclose()
    assert identity.provider_key == "discord"
    assert identity.subject == "700000000000000009"
    assert identity.username == "someone"
    assert identity.membership is not None
    assert identity.membership.is_member is True
    assert identity.membership.role_ids == frozenset({900000000000000003})
