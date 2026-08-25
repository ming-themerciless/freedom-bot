"""TC-OPS-18: `/healthz` asks the identity provider, rather than asserting it.

Raised as S-4 by the 2026-08-24 supervised session and confirmed as S5 by the
independent security review. The session deliberately severed the portal's
egress to Discord, verified the outage in both directions, completed two real
break-glass ceremonies under it — and throughout, `/healthz` reported

    "identity_provider": true

because the route passed `provider_ok=True`, a literal. The one check an
operator consults to find out whether the identity provider is reachable said
"yes" during the outage break-glass exists to survive. A constant is not a
health signal, and VM-16's vocabulary promises a check.

Two layers are covered. The **adapter** must make a bounded, unauthenticated,
side-effect-free request and answer a boolean for every outcome including its
own failure; the **route** must carry that boolean into the report and degrade
the whole endpoint when it is false.

Nothing here opens a socket: the adapter runs over `httpx.MockTransport`, which
is the layer below it, and the route runs against the suite's provider double.
"""
from __future__ import annotations

import httpx
import pytest

from adapters.web.discord_provider import (
    HEALTH_PROBE_TIMEOUT_SECONDS,
    DiscordIdentityProvider,
)
from tests.web.conftest import enroll_credential, make_account
from tests.web_fixtures import web_settings

PROBE_PATH = "/gateway"


def _provider(tmp_path, handler) -> DiscordIdentityProvider:
    settings = web_settings(tmp_path).discord
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return DiscordIdentityProvider(settings, client=client)


# ---------------------------------------------------------------------------
# The adapter
# ---------------------------------------------------------------------------


async def test_the_probe_asks_the_least_privileged_documented_endpoint(tmp_path):
    """Unauthenticated, read-only, and carrying no secret of ours.

    The request is inspected rather than only its answer: a probe that presented
    the client secret, an access token or an OAuth scope would be a credential
    exposed on a path that runs on every health poll, and no amount of correct
    boolean would make that acceptable.
    """
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"url": "wss://gateway.example"})

    provider = _provider(tmp_path, handler)
    assert await provider.probe() is True

    assert len(seen) == 1
    request = seen[0]
    assert request.method == "GET"
    assert request.url.path.endswith(PROBE_PATH)
    assert "authorization" not in {name.lower() for name in request.headers}
    assert request.url.query == b""
    body = request.content.decode()
    for forbidden in ("client_secret", "client_id", "scope", "access_token"):
        assert forbidden not in body


@pytest.mark.parametrize("status", [200, 204, 400, 401, 404])
async def test_an_answer_means_reachable_whatever_it_says(tmp_path, status):
    """A 4xx is Discord *replying*. The platform is not degraded by a changed shape."""
    provider = _provider(tmp_path, lambda request: httpx.Response(status))
    assert await provider.probe() is True


@pytest.mark.parametrize("status", [429, 500, 502, 503])
async def test_throttling_and_server_faults_are_unavailable(tmp_path, status):
    """The same classification `_get` uses, so the adapter means one thing by it."""
    provider = _provider(tmp_path, lambda request: httpx.Response(status))
    assert await provider.probe() is False


@pytest.mark.parametrize(
    "error",
    [
        httpx.ConnectError("refused"),
        httpx.ReadTimeout("timed out"),
        httpx.ConnectTimeout("timed out"),
    ],
    ids=["refused", "read_timeout", "connect_timeout"],
)
async def test_a_transport_failure_answers_false_and_does_not_raise(tmp_path, error):
    """The severed-egress case from the supervised session, at the adapter.

    `curl` from the portal's service account answered in one millisecond with
    exit code 7. This is that, and the honest report of it is `False`.
    """

    def handler(request: httpx.Request) -> httpx.Response:
        raise error

    provider = _provider(tmp_path, handler)
    assert await provider.probe() is False


async def test_the_probe_answers_false_rather_than_propagating_any_failure(tmp_path):
    """A probe is total. `/healthz` must not become a `500` during a degradation.

    The whole purpose of the endpoint is to answer while something is wrong, so
    the one broad catch in this adapter is here, and this is what it buys.
    """

    def handler(request: httpx.Request) -> httpx.Response:
        raise RuntimeError("something entirely unexpected")

    provider = _provider(tmp_path, handler)
    assert await provider.probe() is False


async def test_the_probe_is_bounded_more_tightly_than_an_ordinary_request(tmp_path):
    """A hanging provider must not hold the health endpoint open.

    The ceiling is asserted against the *request's* timeout rather than the
    client's, because the client carries the configured API timeout for logins —
    the point of the correction is that this one call does not inherit it.
    """
    seen: list[float | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.extensions.get("timeout", {}).get("read"))
        return httpx.Response(200)

    settings = web_settings(tmp_path).discord
    provider = _provider(tmp_path, handler)
    assert await provider.probe() is True

    assert seen == [min(HEALTH_PROBE_TIMEOUT_SECONDS, settings.api_timeout_seconds)]
    assert HEALTH_PROBE_TIMEOUT_SECONDS <= settings.api_timeout_seconds


# ---------------------------------------------------------------------------
# The route
# ---------------------------------------------------------------------------


@pytest.mark.database
async def test_healthz_reports_the_provider_as_reachable_when_it_is(
    client, provider, migrated_database
):
    """The ordinary case, and proof the question is asked at all.

    **Seeded since 2026-08-25 (C2).** `200` here means *every* check passed, and
    one of them is now `break_glass_credentials` — so the ordinary case is a portal
    with the two enrolled credentials N-13 requires, not an empty database. The
    shortfall answer has its own regressions in
    `tests/web/test_break_glass_health_reporting.py`.
    """
    with migrated_database.begin() as connection:
        account_id = make_account(connection, protected=True, label="Server Administrator")
        for index in range(2):
            enroll_credential(
                connection,
                account_id,
                credential_id=f"probe-credential-{index}".encode(),
                public_key=f"probe-public-key-{index}".encode(),
                nickname=f"probe-{index}",
            )

    response = await client.get("/healthz")

    assert response.status_code == 200
    assert response.json()["checks"]["identity_provider"] is True
    assert provider.probe_calls == [True]


@pytest.mark.database
async def test_healthz_degrades_when_the_provider_is_unreachable(client, provider):
    """The supervised session's outage, as `/healthz` should have reported it.

    `degraded` and `503`, so a monitor watching the endpoint sees the outage
    instead of being told everything is fine — and the response still carries
    only check names and booleans, which is all VM-16 has ever permitted.
    """
    provider.unavailable = True

    response = await client.get("/healthz")
    body = response.json()

    assert response.status_code == 503
    assert body["status"] == "degraded"
    assert body["checks"]["identity_provider"] is False
    # Every other check still answers for itself: the provider being down is not
    # allowed to become an opinion about the database.
    assert body["checks"]["database"] is True
    assert body["checks"]["migrations"] is True
    assert set(map(type, body["checks"].values())) == {bool}
