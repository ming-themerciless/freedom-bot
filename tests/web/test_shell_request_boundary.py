"""C35-05 / R35-23: the shell at the real request boundary, not in isolation.

The unit tests in `test_shell_navigation_contract.py` prove `shell_for()` maps a
context to a set of links. They prove nothing about the lifecycle: which context
the boundary actually passes it, when the shell is attached relative to the
capability decision, or what a browser receives. That is what these do — through
the real preamble, session resolution, membership refresh, `authorize()`,
`RequestAuthority.render()`, the template, and the logout route.

Every case runs against the guarded disposable PostgreSQL database.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from bs4 import BeautifulSoup
from sqlalchemy import text

from tests.web.portal_fixtures import clean_p3_2_tables, seed_callers, utcnow

#: R-35 admits every authenticated caller, break-glass included, so it is the one
#: page on which every state can be compared without the page itself refusing.
UNIVERSAL_PAGE = "/v1/account/identities"


@pytest.fixture()
def callers(migrated_database, settings):
    yield seed_callers(migrated_database, settings)
    with migrated_database.begin() as connection:
        clean_p3_2_tables(connection)


def _frame(html: str) -> dict:
    """What a browser would actually see in the page frame."""
    soup = BeautifulSoup(html, "html.parser")
    header = soup.find("header", class_="app-header")
    assert header is not None, "the page rendered without a frame"
    links = {a.get_text(strip=True): a["href"] for a in header.select("nav a")}
    logout = header.select_one('form[action="/v1/auth/logout"]')
    token = logout.select_one('input[name="csrf_token"]') if logout else None
    brand = header.select_one("a.brand-title")
    return {
        "links": links,
        "logout": logout is not None,
        "logout_method": (logout.get("method") or "").lower() if logout else None,
        "token": token["value"] if token is not None else None,
        "home": brand["href"] if brand else None,
        "current": [a.get_text(strip=True) for a in header.select('nav a[aria-current="page"]')],
    }


# ---------------------------------------------------------------------------
# 1-4: no valid session ever yields an authenticated frame
# ---------------------------------------------------------------------------


async def test_an_anonymous_caller_receives_the_anonymous_frame(client):
    response = await client.get("/v1/login")
    frame = _frame(response.text)

    assert response.status_code == 200
    assert set(frame["links"]) == {"Login", "Emergency Access"}
    assert frame["logout"] is False
    assert frame["token"] is None
    assert frame["home"] == "/v1/login"


async def test_a_malformed_session_cookie_receives_the_anonymous_frame(client, settings):
    response = await client.get(
        "/v1/login", cookies={settings.session.cookie_name: "not-a-real-session"}
    )
    frame = _frame(response.text)

    assert set(frame["links"]) == {"Login", "Emergency Access"}
    assert frame["logout"] is False
    assert frame["token"] is None


@pytest.mark.parametrize("how", ["expired", "revoked"], ids=["expired", "revoked"])
async def test_an_expired_or_revoked_session_receives_the_anonymous_frame(
    client, settings, callers, migrated_database, how
):
    caller = callers["M"]
    with migrated_database.begin() as connection:
        if how == "expired":
            # Idle expiry only: `ck_sessions_absolute_after_creation` refuses an
            # absolute bound at or before creation, and rightly so — a row like
            # that could never have been issued.
            connection.execute(
                text("UPDATE sessions SET idle_expires_at = :t WHERE id = :id"),
                {"t": utcnow() - timedelta(hours=1), "id": caller.session_id},
            )
        else:
            # `operator`, from the closed vocabulary `ck_sessions_revocation_reason`
            # enforces. An invented reason is refused by the database.
            connection.execute(
                text("UPDATE sessions SET revoked_at = :t, revocation_reason = 'operator'"
                     " WHERE id = :id"),
                {"t": utcnow(), "id": caller.session_id},
            )

    response = await client.get(UNIVERSAL_PAGE, cookies=caller.cookies(settings),
                                follow_redirects=False)

    assert response.status_code == 303, "an unusable session is redirected, not served"
    if response.text.strip():
        frame = _frame(response.text)
        assert frame["logout"] is False, "a revoked session was still offered sign-out"


# ---------------------------------------------------------------------------
# 5-11: every authenticated caller state, as rendered
# ---------------------------------------------------------------------------

EXPECTED_LINKS = {
    "N": {"My account"},
    "M": {"Characters", "My account"},
    "C": {"Characters", "Council characters", "Snapshots", "My account"},
    "A": {"Snapshots", "Role capabilities", "My account"},
    "CA": {"Characters", "Council characters", "Snapshots", "Role capabilities", "My account"},
    "BG": {"Role capabilities", "My account"},
    "AC": {"Role capabilities", "My account"},
}


@pytest.mark.parametrize("state", sorted(EXPECTED_LINKS), ids=sorted(EXPECTED_LINKS))
async def test_each_caller_state_receives_its_accepted_frame(client, settings, callers, state):
    caller = callers[state]

    response = await client.get(UNIVERSAL_PAGE, cookies=caller.cookies(settings))
    frame = _frame(response.text)

    assert response.status_code == 200
    assert set(frame["links"]) == EXPECTED_LINKS[state]
    assert "Login" not in frame["links"], "a signed-in caller was shown Login"
    assert frame["logout"] is True
    assert frame["logout_method"] == "post"
    assert frame["token"], "a valid session rendered no logout token"
    assert frame["home"] in set(frame["links"].values())
    assert len(frame["current"]) <= 1, "more than one destination was marked current"


async def test_administrator_is_not_offered_council_destinations(client, settings, callers):
    """R-20 and R-22 are `✗ 403` for `A`; the frame must agree."""
    response = await client.get(UNIVERSAL_PAGE, cookies=callers["A"].cookies(settings))
    links = _frame(response.text)["links"]

    assert "Characters" not in links
    assert "Council characters" not in links


@pytest.mark.parametrize("state", ["BG", "AC"], ids=["break-glass", "continuity"])
async def test_continuity_scope_is_offered_only_its_accepted_surface(
    client, settings, callers, state
):
    """N-65: identity/capability administration, and nothing of the game."""
    response = await client.get(UNIVERSAL_PAGE, cookies=callers[state].cookies(settings))
    links = _frame(response.text)["links"]

    assert set(links) == {"Role capabilities", "My account"}
    assert links["Role capabilities"] == "/v1/admin/role-capabilities"


# ---------------------------------------------------------------------------
# 14: an authenticated denial keeps its authenticated frame
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "state,path",
    [
        ("A", "/v1/characters"),          # R-20: administrator is refused
        ("M", "/v1/admin/role-capabilities"),  # R-32: member is refused
        ("BG", "/v1/council/snapshots"),  # R-40: break-glass is refused
    ],
    ids=["administrator-denied-characters", "member-denied-administration",
         "continuity-denied-snapshots"],
)
async def test_a_denied_page_still_carries_the_authenticated_frame(
    client, settings, callers, state, path
):
    """The defect R35-21 names: a 403 rendered before the shell was attached.

    A signed-in administrator refused a Council page was shown "Login" and no way
    to sign out, mid-session, because the shell was attached after `authorize()`.
    """
    response = await client.get(path, cookies=callers[state].cookies(settings),
                                follow_redirects=False)

    assert response.status_code == 403
    frame = _frame(response.text)
    assert frame["logout"] is True, "a denial page dropped the caller's session frame"
    assert frame["token"], "a denial page dropped the logout token"
    assert "Login" not in frame["links"], "a denial page offered Login to a signed-in caller"
    assert set(frame["links"]) == EXPECTED_LINKS[state], (
        "the denial page's frame disagrees with the caller's accepted navigation"
    )


async def test_a_denial_page_leaks_no_authority_detail(client, settings, callers):
    response = await client.get("/v1/characters", cookies=callers["A"].cookies(settings),
                                follow_redirects=False)
    body = response.text

    for leak in ("guild_council", "platform_administrator", "administrator_scope",
                 "GUILD_MEMBER", str(callers["A"].account_id), str(callers["A"].session_id)):
        assert leak not in body, f"the denial page disclosed {leak!r}"



async def _post_logout(client, settings, caller, token):
    """A logout exactly as the rendered form issues it.

    A mutation carries a same-origin `Origin` and the form content type; without
    them the boundary refuses at step 2 and the test would be measuring the origin
    check while claiming to measure CSRF.
    """
    body = "" if token is None else f"csrf_token={token}"
    return await client.post(
        "/v1/auth/logout",
        cookies=caller.cookies(settings),
        headers={
            "Origin": settings.public_origin,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        content=body,
        follow_redirects=False,
    )


# ---------------------------------------------------------------------------
# 16-18: logout is real, and its token is the session's
# ---------------------------------------------------------------------------


async def test_the_rendered_token_logs_the_caller_out(client, settings, callers):
    caller = callers["M"]
    page = await client.get(UNIVERSAL_PAGE, cookies=caller.cookies(settings))
    token = _frame(page.text)["token"]

    response = await _post_logout(client, settings, caller, token)

    assert response.status_code in (303, 302)
    after = await client.get(UNIVERSAL_PAGE, cookies=caller.cookies(settings),
                             follow_redirects=False)
    assert after.status_code == 303, "the session survived its own logout"


@pytest.mark.parametrize(
    "token", [None, "", "not-the-token"], ids=["missing", "empty", "wrong"]
)
async def test_logout_refuses_a_token_that_is_not_the_session_s(
    client, settings, callers, token
):
    caller = callers["C"]
    response = await _post_logout(client, settings, caller, token)

    assert response.status_code == 403
    still_here = await client.get(UNIVERSAL_PAGE, cookies=caller.cookies(settings))
    assert still_here.status_code == 200, "a refused logout ended the session anyway"


async def test_logout_refuses_another_session_s_token(client, settings, callers):
    """A token is bound to its own session, so one caller cannot log another out."""
    other = await client.get(UNIVERSAL_PAGE, cookies=callers["C"].cookies(settings))
    other_token = _frame(other.text)["token"]

    response = await _post_logout(client, settings, callers["M"], other_token)

    assert response.status_code == 403


# ---------------------------------------------------------------------------
# 19-20: presentation is not authorization, proved with real sessions
# ---------------------------------------------------------------------------


async def test_hiding_a_link_does_not_deny_a_route_the_caller_may_reach(
    client, settings, callers
):
    """`N` is offered only `My account` — and may still reach what R-35 admits."""
    frame = _frame((await client.get(UNIVERSAL_PAGE,
                                     cookies=callers["N"].cookies(settings))).text)
    assert set(frame["links"]) == {"My account"}

    permitted = await client.get(UNIVERSAL_PAGE, cookies=callers["N"].cookies(settings))
    assert permitted.status_code == 200, (
        "navigation is presentation; the route decides, and it permits this one"
    )


async def test_constructing_a_link_does_not_admit_a_forbidden_route(
    client, settings, callers
):
    """The member is not offered administration, and typing the URL does not help."""
    frame = _frame((await client.get(UNIVERSAL_PAGE,
                                     cookies=callers["M"].cookies(settings))).text)
    assert "Role capabilities" not in frame["links"]

    forbidden = await client.get(
        "/v1/admin/role-capabilities", cookies=callers["M"].cookies(settings),
        follow_redirects=False,
    )
    assert forbidden.status_code == 403


# ---------------------------------------------------------------------------
# 12-13: the shell follows the FINAL context, not the one the session opened with
# ---------------------------------------------------------------------------
# R35-20. The preamble produces two authorities: `gate.context`, captured when the
# session was opened, and `context`, returned by `_close()` after a provider
# refresh and handed to `authorize()`. The shell was built from the first.
#
# **What these prove, exactly:** that the shell is built from `_close()`'s return
# value. They drive the refresh at its seam, because `_refresh_plan()` returns
# `None` without a stored OAuth token grant and the seeded callers have none — so
# a real Discord round-trip is **not** exercised here. That remains uncovered, and
# is recorded as such rather than implied by these passing.


@pytest.fixture()
def refreshing(monkeypatch, migrated_database):
    """Force the preamble down its refresh branch and control what it resolves to.

    Two things are needed for that branch to be taken at all: the projection must
    be stale past N-09, or no refresh is planned; and a token grant must exist, or
    `_refresh_plan()` returns `None`. The first is done for real by ageing the
    rows; the second is substituted, because the seeded callers have no stored
    OAuth grant.
    """
    from application.web import access_control
    from adapters.web import portal_routes

    with migrated_database.begin() as connection:
        connection.execute(
            text("UPDATE discord_guild_memberships SET observed_at = :t"),
            {"t": utcnow() - timedelta(hours=1)},
        )

    monkeypatch.setattr(
        access_control, "_refresh_plan",
        lambda services, account_id, subject: access_control.MembershipRefresh(grant=object()),
    )

    async def _no_provider_call(composition, gate):
        return None

    monkeypatch.setattr(portal_routes, "_observe_membership", _no_provider_call)

    def install(transform):
        def _close(composition, gate, observation, settings, mutation):
            return transform(gate.context)
        monkeypatch.setattr(portal_routes, "_close", _close)

    return install


def _without(context, capability):
    from dataclasses import replace
    return replace(context, capabilities=frozenset(context.capabilities) - {capability})


def _with(context, capability):
    from dataclasses import replace
    return replace(context, capabilities=frozenset(context.capabilities) | {capability})


async def test_a_refresh_that_removes_council_removes_council_navigation(
    client, settings, callers, refreshing
):
    """The security-significant direction: authority taken away."""
    from application.audit import ActorCapability

    # No "before" request: the fixture has already aged the projection, so any
    # request now takes the refresh branch. The baseline that `C` is offered
    # Council is established by test_each_caller_state_receives_its_accepted_frame.
    caller = callers["C"]
    refreshing(lambda context: _without(context, ActorCapability.GUILD_COUNCIL))

    after = await client.get(UNIVERSAL_PAGE, cookies=caller.cookies(settings))
    frame = _frame(after.text)

    assert after.status_code == 200
    assert "Council characters" not in frame["links"], (
        "the frame offered Council destinations from the pre-refresh context, while "
        "authorization used the post-refresh one"
    )
    assert "Snapshots" not in frame["links"]

    denied = await client.get("/v1/council/characters", cookies=caller.cookies(settings),
                              follow_redirects=False)
    assert denied.status_code == 403, "the route and the frame must agree"


async def test_a_refresh_that_adds_council_adds_council_navigation(
    client, settings, callers, refreshing
):
    from application.audit import ActorCapability

    caller = callers["M"]
    refreshing(lambda context: _with(context, ActorCapability.GUILD_COUNCIL))

    after = await client.get(UNIVERSAL_PAGE, cookies=caller.cookies(settings))
    frame = _frame(after.text)

    assert after.status_code == 200
    assert "Council characters" in frame["links"], (
        "the frame did not follow authority the refresh granted"
    )
    permitted = await client.get("/v1/council/characters", cookies=caller.cookies(settings))
    assert permitted.status_code == 200, "navigation and authorization disagree"


async def test_a_refresh_that_removes_membership_removes_member_navigation(
    client, settings, callers, refreshing
):
    from application.audit import ActorCapability

    caller = callers["M"]
    refreshing(lambda context: _without(context, ActorCapability.GUILD_MEMBER))

    response = await client.get(UNIVERSAL_PAGE, cookies=caller.cookies(settings),
                                follow_redirects=False)

    assert response.status_code == 200
    assert "Characters" not in _frame(response.text)["links"], (
        "a caller who is no longer a member was still offered member destinations"
    )


# ---------------------------------------------------------------------------
# R35-26: public full pages carry the caller's own frame
# ---------------------------------------------------------------------------
# `/v1/login` and `/v1/auth/emergency` run no protected preamble, so before this
# they rendered the anonymous frame to everybody. A signed-in caller visiting the
# login page was offered "Login" and shown no way to sign out — the remaining half
# of F-17.

PUBLIC_PAGES = ["/v1/login", "/v1/auth/emergency"]


@pytest.mark.parametrize("path", PUBLIC_PAGES)
async def test_a_public_page_is_anonymous_for_an_anonymous_caller(client, path):
    frame = _frame((await client.get(path)).text)

    assert set(frame["links"]) == {"Login", "Emergency Access"}
    assert frame["logout"] is False
    assert frame["token"] is None
    assert frame["home"] == "/v1/login"


@pytest.mark.parametrize("path", PUBLIC_PAGES)
@pytest.mark.parametrize("state", ["M", "A", "BG"], ids=["member", "administrator", "break-glass"])
async def test_a_public_page_carries_a_valid_session_s_own_frame(
    client, settings, callers, path, state
):
    response = await client.get(path, cookies=callers[state].cookies(settings))
    frame = _frame(response.text)

    assert response.status_code == 200
    assert frame["logout"] is True, "a signed-in caller was shown no way to sign out"
    assert frame["logout_method"] == "post"
    assert frame["token"], "no logout token on a public page for a valid session"
    assert "Login" not in frame["links"], "a signed-in caller was offered Login"
    assert frame["home"] in set(frame["links"].values())


@pytest.mark.parametrize("path", PUBLIC_PAGES)
@pytest.mark.parametrize("cookie", ["not-a-session", ""], ids=["malformed", "empty"])
async def test_a_public_page_is_anonymous_for_an_unusable_cookie(
    client, settings, path, cookie
):
    response = await client.get(path, cookies={settings.session.cookie_name: cookie})
    frame = _frame(response.text)

    assert set(frame["links"]) == {"Login", "Emergency Access"}
    assert frame["logout"] is False
    assert frame["token"] is None


@pytest.mark.parametrize("path", PUBLIC_PAGES)
@pytest.mark.parametrize("how", ["expired", "revoked"])
async def test_a_public_page_is_anonymous_for_an_expired_or_revoked_session(
    client, settings, callers, migrated_database, path, how
):
    caller = callers["M"]
    with migrated_database.begin() as connection:
        if how == "expired":
            connection.execute(
                text("UPDATE sessions SET idle_expires_at = :t WHERE id = :id"),
                {"t": utcnow() - timedelta(hours=1), "id": caller.session_id},
            )
        else:
            connection.execute(
                text("UPDATE sessions SET revoked_at = :t, revocation_reason = 'operator'"
                     " WHERE id = :id"),
                {"t": utcnow(), "id": caller.session_id},
            )

    frame = _frame((await client.get(path, cookies=caller.cookies(settings))).text)

    assert frame["logout"] is False, "an unusable session was still offered sign-out"
    assert frame["token"] is None
    assert set(frame["links"]) == {"Login", "Emergency Access"}


async def test_a_public_page_gives_a_stale_caller_the_conservative_frame(
    client, settings, callers, migrated_database
):
    """Drawing a header must not make a provider call.

    When the projection is stale — exactly when a protected preamble would refresh
    — a public page offers only what needs no capability at all, rather than
    privileged links resting on authority nobody revalidated.
    """
    caller = callers["C"]
    with migrated_database.begin() as connection:
        connection.execute(
            text("UPDATE discord_guild_memberships SET observed_at = :t"),
            {"t": utcnow() - timedelta(hours=1)},
        )

    frame = _frame((await client.get("/v1/login", cookies=caller.cookies(settings))).text)

    assert frame["logout"] is True, "the session is valid, so sign-out must be offered"
    assert set(frame["links"]) == {"My account"}, (
        "a stale caller was offered capability-dependent destinations on a public page"
    )
    assert "Council characters" not in frame["links"]


async def test_a_public_page_logout_token_actually_works(client, settings, callers):
    caller = callers["M"]
    token = _frame((await client.get("/v1/login", cookies=caller.cookies(settings))).text)["token"]

    response = await _post_logout(client, settings, caller, token)

    assert response.status_code in (303, 302)
    after = await client.get(UNIVERSAL_PAGE, cookies=caller.cookies(settings),
                             follow_redirects=False)
    assert after.status_code == 303, "the session survived a logout from a public page"


# ---------------------------------------------------------------------------
# R35-27: a refusal raised by a failed refresh keeps a safe authenticated frame
# ---------------------------------------------------------------------------


async def test_a_service_degraded_refusal_keeps_a_safe_authenticated_frame(
    client, settings, callers, monkeypatch, migrated_database
):
    """A Discord outage mid-session must not tell the caller they are logged out.

    The frame is the conservative one, not the caller's full set: the refresh that
    would have revalidated their capabilities is what failed.
    """
    from application.web import access_control
    from application.web.errors import ServiceDegraded
    from adapters.web import portal_routes

    with migrated_database.begin() as connection:
        connection.execute(
            text("UPDATE discord_guild_memberships SET observed_at = :t"),
            {"t": utcnow() - timedelta(hours=1)},
        )
    monkeypatch.setattr(
        access_control, "_refresh_plan",
        lambda services, account_id, subject: access_control.MembershipRefresh(grant=object()),
    )

    async def _observe(composition, gate):
        return None

    def _close_fails(composition, gate, observation, settings_, mutation):
        raise ServiceDegraded()

    monkeypatch.setattr(portal_routes, "_observe_membership", _observe)
    monkeypatch.setattr(portal_routes, "_close", _close_fails)

    caller = callers["C"]
    response = await client.get(UNIVERSAL_PAGE, cookies=caller.cookies(settings),
                                follow_redirects=False)

    assert response.status_code == 503
    frame = _frame(response.text)
    assert frame["logout"] is True, (
        "a degraded page told a caller with a live session that they were signed out"
    )
    assert frame["token"], "the degraded page carried no logout token"
    assert "Login" not in frame["links"]
    assert set(frame["links"]) == {"My account"}, (
        "a failed refresh must not leave privileged links standing on stale authority"
    )


async def test_a_degraded_page_leaks_no_authority_or_provider_detail(
    client, settings, callers, monkeypatch, migrated_database
):
    from application.web import access_control
    from application.web.errors import ServiceDegraded
    from adapters.web import portal_routes

    with migrated_database.begin() as connection:
        connection.execute(
            text("UPDATE discord_guild_memberships SET observed_at = :t"),
            {"t": utcnow() - timedelta(hours=1)},
        )
    monkeypatch.setattr(
        access_control, "_refresh_plan",
        lambda services, account_id, subject: access_control.MembershipRefresh(grant=object()),
    )

    async def _observe(composition, gate):
        return None

    monkeypatch.setattr(portal_routes, "_observe_membership", _observe)
    monkeypatch.setattr(
        portal_routes, "_close",
        lambda *a, **k: (_ for _ in ()).throw(ServiceDegraded()),
    )

    caller = callers["C"]
    body = (await client.get(UNIVERSAL_PAGE, cookies=caller.cookies(settings),
                             follow_redirects=False)).text

    for leak in ("guild_council", "platform_administrator", "ServiceDegraded",
                 "Traceback", "discord.com", str(caller.account_id), str(caller.session_id)):
        assert leak not in body, f"the degraded page disclosed {leak!r}"


# ---------------------------------------------------------------------------
# R35-32/R35-34: session absence is not infrastructure failure
# ---------------------------------------------------------------------------
# `_attach_public_shell` caught every `Exception` and returned, so a database
# outage, a repository fault or a plain programming error became a cheerful
# anonymous page. The portal would have looked *fine* while its session store was
# unreachable, and the signed-in operator — the one person positioned to notice —
# would have been silently logged out instead of told.

SECURITY_HEADERS_REQUIRED = ("content-security-policy", "x-content-type-options",
                             "referrer-policy")


@pytest.mark.parametrize("path", PUBLIC_PAGES)
async def test_no_cookie_performs_no_session_lookup(client, path, monkeypatch):
    """An anonymous visitor must not touch session storage to read a public page."""
    from adapters.web import portal_routes

    def _must_not_run(*args, **kwargs):  # pragma: no cover - the assertion is that it does not
        raise AssertionError("a request with no cookie resolved a session")

    monkeypatch.setattr(portal_routes, "_open", _must_not_run)

    response = await client.get(path)

    assert response.status_code == 200
    frame = _frame(response.text)
    assert set(frame["links"]) == {"Login", "Emergency Access"}
    assert frame["logout"] is False


@pytest.mark.parametrize("path", PUBLIC_PAGES)
@pytest.mark.parametrize(
    "token", ["not-a-token", "a" * 200, "%%%%", "00000000-0000-4000-8000-000000000000"],
    ids=["malformed", "overlong", "non-ascii-ish", "unknown-but-well-formed"],
)
async def test_an_unusable_token_renders_the_anonymous_shell(client, settings, path, token):
    response = await client.get(path, cookies={settings.session.cookie_name: token})

    assert response.status_code == 200
    frame = _frame(response.text)
    assert set(frame["links"]) == {"Login", "Emergency Access"}
    assert frame["logout"] is False
    assert frame["token"] is None


@pytest.mark.parametrize("path", PUBLIC_PAGES)
async def test_a_degraded_session_store_does_not_render_an_anonymous_success(
    client, settings, callers, monkeypatch, path
):
    """The defect, stated as a test: infrastructure failure must not look like success."""
    from adapters.web import portal_routes
    from application.web.errors import ServiceDegraded

    def _degraded(composition, settings_, token):
        raise ServiceDegraded()

    monkeypatch.setattr(portal_routes, "_open", _degraded)

    response = await client.get(path, cookies=callers["M"].cookies(settings))

    assert response.status_code == 503, (
        "a degraded session store rendered an anonymous 200; the portal looked healthy "
        "while it could not resolve anybody"
    )
    for header in SECURITY_HEADERS_REQUIRED:
        assert header in response.headers, f"the degraded page dropped {header}"
    assert response.headers.get("cache-control") == "no-store"


@pytest.mark.parametrize("path", PUBLIC_PAGES)
async def test_an_unexpected_error_reaches_the_safe_error_boundary(
    client, settings, callers, monkeypatch, path
):
    """A programming error must not be laundered into an anonymous page."""
    from adapters.web import portal_routes

    def _boom(composition, settings_, token):
        raise RuntimeError("synthetic invariant violation")

    monkeypatch.setattr(portal_routes, "_open", _boom)

    # A transport that returns the application's own error response instead of
    # re-raising, so the *boundary's* answer can be inspected. The default
    # `raise_app_exceptions=True` is right for the rest of the suite — it stops a
    # swallowed fault looking like a pass — but here the response is the subject.
    import httpx

    transport = httpx.ASGITransport(app=client._transport.app, raise_app_exceptions=False)
    async with httpx.AsyncClient(
        transport=transport, base_url=str(client.base_url)
    ) as inspecting:
        response = await inspecting.get(
            path, cookies=callers["M"].cookies(settings), follow_redirects=False
        )

    assert response.status_code == 500, "an unexpected error was swallowed into a 200"
    body = response.text
    for leak in ("synthetic invariant violation", "RuntimeError", "Traceback",
                 "portal_routes", "freedom_test", "SELECT"):
        assert leak not in body, f"the error page disclosed {leak!r}"
    for header in SECURITY_HEADERS_REQUIRED:
        assert header in response.headers
    assert response.headers.get("cache-control") == "no-store"


@pytest.mark.parametrize("path", PUBLIC_PAGES)
async def test_cancellation_is_not_converted_into_anonymous_rendering(
    client, settings, callers, monkeypatch, path
):
    """`BaseException` is never caught here, so cancellation keeps its semantics."""
    import asyncio

    from adapters.web import portal_routes

    def _cancelled(composition, settings_, token):
        raise asyncio.CancelledError()

    monkeypatch.setattr(portal_routes, "_open", _cancelled)

    # The request ends without a rendered page, which is the point: cancellation
    # is not laundered into an anonymous `200`. The transport reports it as "no
    # response returned" once the `BaseException` has travelled through the stack
    # uncaught.
    with pytest.raises((asyncio.CancelledError, RuntimeError)) as raised:
        await client.get(path, cookies=callers["M"].cookies(settings))

    assert isinstance(raised.value, asyncio.CancelledError) or (
        "No response returned" in str(raised.value)
    ), f"cancellation produced something else entirely: {raised.value!r}"


@pytest.mark.parametrize("path", PUBLIC_PAGES)
async def test_a_degraded_or_error_page_discloses_no_caller_material(
    client, settings, callers, monkeypatch, path
):
    from adapters.web import portal_routes
    from application.web.errors import ServiceDegraded

    caller = callers["C"]
    cookie_value = caller.cookies(settings)[settings.session.cookie_name]
    monkeypatch.setattr(
        portal_routes, "_open",
        lambda *a, **k: (_ for _ in ()).throw(ServiceDegraded()),
    )

    body = (await client.get(path, cookies=caller.cookies(settings))).text

    for leak in (cookie_value, str(caller.account_id), str(caller.session_id),
                 "guild_council", "platform_administrator", "discord.com",
                 "ServiceDegraded", "Traceback"):
        assert leak not in body, f"the degraded page disclosed {leak!r}"


async def test_a_protected_request_still_resolves_its_session_once(
    client, settings, callers, monkeypatch
):
    """The public helper must not layer a second resolution over the preamble."""
    from adapters.web import portal_routes

    calls = []
    original = portal_routes._open

    def _counting(composition, settings_, token):
        calls.append(token)
        return original(composition, settings_, token)

    monkeypatch.setattr(portal_routes, "_open", _counting)

    response = await client.get(UNIVERSAL_PAGE, cookies=callers["M"].cookies(settings))

    assert response.status_code == 200
    assert len(calls) == 1, f"the session was resolved {len(calls)} times on one request"
