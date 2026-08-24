"""C35-05 / R35-17: the server-owned shell, across every accepted caller state.

Navigation is presentation. Route guards remain the authority, and the last two
tests here exist to prove those are two different things: hiding a link authorizes
nothing, and showing one bypasses nothing.
"""

from __future__ import annotations

from uuid import uuid4

import pathlib
import re

import pytest

from application.web.capabilities import (
    ActorCapability,
    AdministratorScope,
    AuthMethod,
    WebAuthorizationContext,
)
from application.web.shell import (
    ANONYMOUS_SHELL,
    ShellNav,
    resolve_current,
    shell_for,
    with_current,
)


def _context(*capabilities: ActorCapability, method: AuthMethod = AuthMethod.DISCORD_OAUTH,
             scope: AdministratorScope = AdministratorScope.FULL) -> WebAuthorizationContext:
    return WebAuthorizationContext(
        account_id=uuid4(),
        auth_method=method,
        capabilities=frozenset(capabilities),
        administrator_scope=scope,
        membership=None,
    )


MEMBER = ActorCapability.GUILD_MEMBER
COUNCIL = ActorCapability.GUILD_COUNCIL
ADMIN = ActorCapability.PLATFORM_ADMINISTRATOR

#: The accepted matrix, as navigation. Derived from the route contract's §5.2/§6
#: rows for R-20, R-22, R-32, R-35 and R-40 — not from what looks reasonable.
CALLER_STATES = {
    "N non-member": ((), {ShellNav.IDENTITIES}),
    "A' administrator, not a guild member": (
        (ADMIN,), {ShellNav.IDENTITIES, ShellNav.ROLE_CAPABILITIES}
    ),
    "M member": ((MEMBER,), {ShellNav.IDENTITIES, ShellNav.CHARACTERS}),
    "C council": (
        (MEMBER, COUNCIL),
        {ShellNav.IDENTITIES, ShellNav.CHARACTERS, ShellNav.COUNCIL_CHARACTERS,
         ShellNav.SNAPSHOTS},
    ),
    # A guild member holding the administrator role: `_member_read` refuses them
    # Characters, and `COUNCIL_OR_ADMINISTRATOR` admits them Snapshots.
    "A administrator": (
        (MEMBER, ADMIN),
        {ShellNav.IDENTITIES, ShellNav.SNAPSHOTS, ShellNav.ROLE_CAPABILITIES},
    ),
    "CA council+administrator": (
        (MEMBER, COUNCIL, ADMIN),
        {ShellNav.IDENTITIES, ShellNav.CHARACTERS, ShellNav.COUNCIL_CHARACTERS,
         ShellNav.SNAPSHOTS, ShellNav.ROLE_CAPABILITIES},
    ),
}


@pytest.mark.parametrize("state", list(CALLER_STATES), ids=list(CALLER_STATES))
def test_each_caller_state_is_offered_exactly_its_accepted_destinations(state):
    capabilities, expected = CALLER_STATES[state]
    shell = shell_for(_context(*capabilities), csrf_token="t")
    assert {link.id for link in shell.navigation} == expected


def test_the_anonymous_shell_offers_only_anonymous_destinations():
    assert {link.id for link in ANONYMOUS_SHELL.navigation} == {
        ShellNav.LOGIN, ShellNav.EMERGENCY
    }
    assert ANONYMOUS_SHELL.authenticated is False
    assert ANONYMOUS_SHELL.logout_csrf_token is None
    assert ANONYMOUS_SHELL.logout_available is False


def test_an_authenticated_caller_is_never_offered_login():
    for capabilities, _ in CALLER_STATES.values():
        shell = shell_for(_context(*capabilities), csrf_token="t")
        assert ShellNav.LOGIN not in {link.id for link in shell.navigation}, (
            "showing Login to a signed-in caller is the defect this contract removes"
        )


def test_platform_administrator_does_not_acquire_council_navigation():
    """R-20 and R-22 are `✗ 403` for `A`. The frame must agree with the matrix."""
    shell = shell_for(_context(MEMBER, ADMIN), csrf_token="t")
    offered = {link.id for link in shell.navigation}
    assert ShellNav.CHARACTERS not in offered
    assert ShellNav.COUNCIL_CHARACTERS not in offered


def test_break_glass_is_offered_only_what_its_scope_permits():
    """N-65: a continuity-scoped caller reaches identity/capability administration.

    Not characters, not Council anything. Emergency authority restores
    administrative continuity; it does not become game authority.
    """
    shell = shell_for(
        _context(ADMIN, method=AuthMethod.WEBAUTHN,
                 scope=AdministratorScope.EMERGENCY_CONTINUITY),
        csrf_token="t",
    )
    offered = {link.id for link in shell.navigation}
    assert offered == {ShellNav.ROLE_CAPABILITIES, ShellNav.IDENTITIES}, (
        "R-40 refuses `BG`, so snapshots must not be offered either"
    )


# ---------------------------------------------------------------------------
# Logout and its token
# ---------------------------------------------------------------------------


def test_a_valid_session_gets_logout_and_the_session_s_own_token():
    shell = shell_for(_context(MEMBER), csrf_token="token-for-this-session")
    assert shell.authenticated is True
    assert shell.logout_available is True
    assert shell.logout_csrf_token == "token-for-this-session"


def test_no_session_means_no_logout_and_no_token():
    """Missing, malformed, expired and revoked all arrive here identically.

    `open_request()` raises `SessionAbsent` for every one of them, so no gate is
    produced, so `render()` uses the anonymous shell. The absence of a token is
    structural — there is no code path that mints one without a live session.
    """
    assert ANONYMOUS_SHELL.logout_csrf_token is None
    assert ANONYMOUS_SHELL.logout_available is False


# ---------------------------------------------------------------------------
# Current page
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path,expected",
    [
        ("/v1/login", ShellNav.LOGIN),
        ("/v1/auth/discord/start", ShellNav.LOGIN),
        ("/", ShellNav.LOGIN),
        ("/v1/auth/emergency", ShellNav.EMERGENCY),
        ("/v1/auth/emergency/webauthn", ShellNav.EMERGENCY),
        ("/not-found", None),
    ],
)
def test_the_current_page_is_resolved_by_longest_match(path, expected):
    """Emergency sits under `/v1/auth/`, which Login also claims. Longest wins."""
    assert resolve_current(path, ANONYMOUS_SHELL.navigation) is expected


def test_at_most_one_destination_is_ever_current():
    every_path = ["/", "/v1/login", "/v1/auth/emergency", "/v1/characters",
                  "/v1/characters/abc", "/v1/council/characters", "/v1/council/snapshots",
                  "/v1/admin/role-capabilities", "/v1/account/identities", "/nowhere"]
    shell = shell_for(_context(MEMBER, COUNCIL, ADMIN), csrf_token="t")
    for path in every_path:
        current = with_current(shell, path).current
        assert current is None or current in {link.id for link in shell.navigation}


# ---------------------------------------------------------------------------
# Presentation is not authorization
# ---------------------------------------------------------------------------


async def test_hiding_a_link_does_not_deny_the_route(client):
    """An anonymous caller is offered no Characters link — and the route still guards.

    If navigation were the control, removing the link would be the denial. It is
    not: the route refuses on its own, which is what makes the shell safe to be
    merely presentational.
    """
    assert ShellNav.CHARACTERS not in {link.id for link in ANONYMOUS_SHELL.navigation}

    response = await client.get("/v1/characters", follow_redirects=False)

    assert response.status_code in (303, 401, 403), (
        "the route guard, not the navigation, is what refuses an anonymous caller"
    )


async def test_rendering_a_link_would_not_bypass_a_guard(client):
    """The converse: a destination present in the closed vocabulary is still guarded.

    `ShellNav` naming a destination grants nothing. An unauthenticated request for
    the administration surface is refused by its own guard regardless of what any
    frame chose to render.
    """
    assert ShellNav.ROLE_CAPABILITIES in set(ShellNav)

    response = await client.get("/v1/admin/role-capabilities", follow_redirects=False)

    assert response.status_code in (303, 401, 403)


def test_continuity_scope_strips_council_navigation_even_from_a_council_holder():
    """Scope outranks capability in the frame, as it does at the route.

    An administrator whose scope is emergency continuity is refused R-20, R-22 and
    R-40 whatever else they hold, so the frame offers none of them.
    """
    shell = shell_for(
        _context(MEMBER, COUNCIL, ADMIN, method=AuthMethod.WEBAUTHN,
                 scope=AdministratorScope.EMERGENCY_CONTINUITY),
        csrf_token="t",
    )
    assert {link.id for link in shell.navigation} == {
        ShellNav.ROLE_CAPABILITIES, ShellNav.IDENTITIES
    }


# ---------------------------------------------------------------------------
# R35-22: the brand destination is server-owned and always reachable
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("state", list(CALLER_STATES), ids=list(CALLER_STATES))
def test_the_brand_destination_is_one_this_caller_may_reach(state):
    """The template used to hard-code `/v1/characters` for anyone authenticated.

    R-20 refuses that to an administrator-only caller, so the frame offered a door
    that answers 403. The home destination is now one of the caller's own offered
    links, by construction.
    """
    capabilities, _ = CALLER_STATES[state]
    shell = shell_for(_context(*capabilities), csrf_token="t")
    assert shell.home_href in {link.href for link in shell.navigation}


def test_an_administrator_only_caller_is_not_sent_to_characters():
    shell = shell_for(_context(MEMBER, ADMIN), csrf_token="t")
    assert shell.home_href != "/v1/characters"


def test_a_continuity_scoped_caller_is_not_sent_to_characters():
    shell = shell_for(
        _context(ADMIN, method=AuthMethod.WEBAUTHN,
                 scope=AdministratorScope.EMERGENCY_CONTINUITY),
        csrf_token="t",
    )
    assert shell.home_href != "/v1/characters"
    assert shell.home_href in {link.href for link in shell.navigation}


def test_the_anonymous_brand_destination_is_an_anonymous_route():
    assert ANONYMOUS_SHELL.home_href == "/v1/login"


def test_no_template_manufactures_a_path_outside_the_shell_vocabulary():
    """Every href the header can emit comes from the shell."""
    header = (
        pathlib.Path(__file__).resolve().parents[2]
        / "adapters/web/templates/includes/header.html"
    ).read_text()
    literal_hrefs = re.findall(r'href="(/[^"{]*)"', header)
    assert literal_hrefs == [], f"the header hard-codes destinations: {literal_hrefs}"
