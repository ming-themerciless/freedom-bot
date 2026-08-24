"""The server-owned shell: what the page frame may show this caller. (C35-05)

Every full-page render receives one of these. It exists because the shared header
previously rendered the same three links to everybody — so a signed-in
administrator was shown "Login", no template offered a way to sign out, and the
administration surface was reachable only by typing a URL (F-17).

**Navigation is presentation, never authorization.** Every route keeps its own
guard, and those guards remain the authority. Hiding a link denies nothing and
showing one grants nothing; the matrix below exists so the frame does not offer a
caller a door that will be shut in their face, and does not hide one they are
entitled to use.

The link set is derived strictly from the accepted route-authorization matrix
(§5.2 and §6), row by row, and no destination is listed here whose row was not
read. Its columns are `U N M C A CA BG`:

| Destination | Route | May reach it |
|---|---|---|
| My Characters | R-20 | M, C, CA |
| Council characters | R-22 | C, CA |
| Snapshots | R-40 | C, A, CA |
| Role capabilities | R-32 | A, CA, **BG** |
| Account identities | R-35 | every authenticated caller, **BG** included |

Two consequences worth stating rather than leaving to be noticed:

- **Platform administrator does not acquire Council navigation.** R-20 and R-22 are
  `✗ 403` for `A`, so an administrator is offered neither, exactly as the capability
  model intends.
- **Break-glass is offered only what N-65 permits it**: role capabilities and
  account identities. Not characters, not snapshots, not Council anything.

`Login` appears only for an anonymous caller. The route permits it in every state,
but offering it to someone already signed in is the defect this contract exists to
remove. `Emergency access` is likewise anonymous-only: it is reachable by anyone,
and putting it in an authenticated frame would be clutter rather than a control.
Both are presentation decisions, recorded here because they are decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from application.web.capabilities import AdministratorScope


class ShellNav(str, Enum):
    """The closed vocabulary of destinations the frame may offer.

    Closed on purpose: a template cannot introduce a link, and a reviewer can read
    every destination the shell is capable of naming in one place.
    """

    LOGIN = "login"
    EMERGENCY = "emergency"
    CHARACTERS = "characters"
    COUNCIL_CHARACTERS = "council_characters"
    SNAPSHOTS = "snapshots"
    ROLE_CAPABILITIES = "role_capabilities"
    IDENTITIES = "identities"


#: Label, path, and the path prefixes that make the destination the current page.
#:
#: The prefixes are not always the destination's own path. `Login` is the current
#: page throughout the sign-in journey — `/v1/auth/discord/start` and `/` included —
#: which is the behaviour P3.4 accepted, and it is preserved rather than quietly
#: dropped. Emergency access sits *under* `/v1/auth/`, so it would collide; the
#: resolver takes the longest match, which is why `/v1/auth/emergency` marks
#: emergency and not login.
_DESTINATIONS: dict[ShellNav, tuple[str, str, tuple[str, ...]]] = {
    ShellNav.LOGIN: ("Login", "/v1/login", ("/v1/login", "/v1/auth/", "/")),
    ShellNav.EMERGENCY: ("Emergency Access", "/v1/auth/emergency", ("/v1/auth/emergency",)),
    ShellNav.CHARACTERS: ("Characters", "/v1/characters", ("/v1/characters",)),
    ShellNav.COUNCIL_CHARACTERS: (
        "Council characters", "/v1/council/characters", ("/v1/council/characters",)
    ),
    ShellNav.SNAPSHOTS: ("Snapshots", "/v1/council/snapshots", ("/v1/council/snapshots",)),
    ShellNav.ROLE_CAPABILITIES: (
        "Role capabilities", "/v1/admin/role-capabilities", ("/v1/admin/role-capabilities",)
    ),
    ShellNav.IDENTITIES: ("My account", "/v1/account/identities", ("/v1/account/identities",)),
}


@dataclass(frozen=True, slots=True)
class ShellLink:
    """One offered destination. Immutable, and carries no authority of its own."""

    id: ShellNav
    label: str
    href: str
    active_prefixes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ShellView:
    """What the frame may render for this caller.

    `logout_csrf_token` is present **only** when a valid authenticated session
    exists, because that is the only circumstance in which logout is a legal
    action. It is never minted for an anonymous, missing, malformed, expired or
    revoked session: those never produce a `RequestGate`, and this view is built
    from a gate or not at all.
    """

    authenticated: bool
    navigation: tuple[ShellLink, ...]
    logout_csrf_token: str | None = None
    #: Where the brand/home link points. **Server-owned** (R35-22): the template
    #: previously hard-coded `/v1/characters` for any authenticated caller, which
    #: offered an administrator-only or continuity-scoped caller a door R-20
    #: refuses. It is always one of this caller's own offered destinations.
    home_href: str = _DESTINATIONS[ShellNav.LOGIN][1]
    #: The one destination marked as the current page, or none. Resolved server-side
    #: by longest prefix, so "exactly one is current" is a property of this type
    #: rather than something a template has to be trusted to get right.
    current: ShellNav | None = None

    @property
    def logout_available(self) -> bool:
        return self.authenticated and self.logout_csrf_token is not None


def navigation_for(*identifiers: ShellNav) -> tuple[ShellLink, ...]:
    """Build links for the named destinations, with their accepted paths and prefixes.

    Public because a link is not a bag of strings a caller should assemble by hand:
    a link built without its `active_prefixes` renders but can never be the current
    page, which is a silent defect rather than a loud one.
    """
    return tuple(
        ShellLink(
            id=identifier,
            label=_DESTINATIONS[identifier][0],
            href=_DESTINATIONS[identifier][1],
            active_prefixes=_DESTINATIONS[identifier][2],
        )
        for identifier in identifiers
    )


def _matches(path: str, prefix: str) -> bool:
    if prefix == "/":
        return path == "/"
    return path == prefix or path.startswith(prefix.rstrip("/") + "/")


def resolve_current(path: str, navigation: tuple[ShellLink, ...]) -> ShellNav | None:
    """Which offered destination is the current page. Longest match wins.

    Returns at most one, so the frame cannot mark two — the accessibility property
    the P3.4 tests assert, held here rather than in a template.
    """
    best: tuple[int, ShellNav] | None = None
    for link in navigation:
        for prefix in link.active_prefixes:
            if _matches(path, prefix) and (best is None or len(prefix) > best[0]):
                best = (len(prefix), link.id)
    return None if best is None else best[1]


#: Presentation order, and the preference order for the home destination. The
#: first destination a caller is offered is the one their brand link points at, so
#: this list is the rule R35-22 asks to be documented rather than inferred.
_PRESENTATION_ORDER = (
    ShellNav.CHARACTERS,
    ShellNav.COUNCIL_CHARACTERS,
    ShellNav.SNAPSHOTS,
    ShellNav.ROLE_CAPABILITIES,
    ShellNav.IDENTITIES,
)


ANONYMOUS_SHELL = ShellView(
    authenticated=False,
    navigation=navigation_for(ShellNav.LOGIN, ShellNav.EMERGENCY),
    logout_csrf_token=None,
    home_href=_DESTINATIONS[ShellNav.LOGIN][1],
)


def with_current(shell: ShellView, path: str) -> ShellView:
    """The same shell, told which page it is being rendered on."""
    return ShellView(
        authenticated=shell.authenticated,
        navigation=shell.navigation,
        logout_csrf_token=shell.logout_csrf_token,
        home_href=shell.home_href,
        current=resolve_current(path, shell.navigation),
    )


def session_only_shell(*, csrf_token: str) -> ShellView:
    """An authenticated frame that asserts nothing about capability.

    Used where a valid session exists but its **current** authority is not known
    to be fresh: a public full page that must not make a provider call to draw a
    header, and a refusal raised by a refresh that failed without invalidating the
    session.

    It offers exactly the destination that needs no capability at all — R-35, which
    admits every authenticated caller — plus sign-out. It never shows a privileged
    link on the strength of capabilities a failed or skipped refresh was supposed
    to revalidate. "The session is valid" and "the capabilities are current" are
    two different statements, and conflating them is how a frame ends up offering
    Council to somebody who lost it.
    """
    navigation = navigation_for(ShellNav.IDENTITIES)
    return ShellView(
        authenticated=True,
        navigation=navigation,
        logout_csrf_token=csrf_token,
        home_href=navigation[0].href,
    )


def shell_for(context, *, csrf_token: str) -> ShellView:
    """Derive the shell from the **final** authority the route decision used.

    `context` is the context returned by the preamble's step 4 — after any
    provider/membership refresh — and it is the same object `authorize()` is given.
    Deriving from anything earlier (R35-20) would let navigation and authorization
    disagree whenever a refresh added or, more importantly, **removed** authority:
    a caller whose Council role was revoked seconds ago would still be offered
    Council destinations by a frame reading a pre-refresh snapshot.

    `csrf_token` is the session-bound token and the only session material the shell
    carries. No gate, engine, repository, refresh object or capability service is
    passed here, so none of them can reach a template.
    """
    # N-65. A continuity-scoped caller is every break-glass session, plus an
    # ordinary-provider session whose administrator capability descends only from
    # emergency-provenance mappings. Its surface is identity/capability
    # administration and audit read — and the route matrix agrees: R-32 and R-35
    # admit `BG`, while R-20, R-22 and R-40 refuse it. Reading the scope rather
    # than only the capability set is what keeps the frame from offering an
    # emergency administrator a door R-40 will shut.
    continuity_scoped = context.administrator_scope is AdministratorScope.EMERGENCY_CONTINUITY

    permitted: set[ShellNav] = {ShellNav.IDENTITIES}  # R-35: every authenticated caller

    if not continuity_scoped:
        # R-20/R-21, `Requirement.MEMBER_READ`, mirroring `access_control._member_read`
        # rather than paraphrasing it: guild membership is required, and an
        # administrator who is **not** also Council is refused. `CA` reaches these
        # routes through Council, which is why the test is "administrator and not
        # Council" rather than "administrator" — the operational role is not a
        # game-data role, and being an administrator grants no standing to read a
        # character sheet.
        if context.guild_member and not (
            context.platform_administrator and not context.guild_council
        ):
            permitted.add(ShellNav.CHARACTERS)
        # R-22, `Requirement.COUNCIL`.
        if context.guild_council:
            permitted.add(ShellNav.COUNCIL_CHARACTERS)
        # R-40, `Requirement.COUNCIL_OR_ADMINISTRATOR`: membership **and** one of
        # the two capabilities, in that order.
        if context.guild_member and (
            context.guild_council or context.platform_administrator
        ):
            permitted.add(ShellNav.SNAPSHOTS)

    # R-32: administrator, including a break-glass administrator.
    if context.platform_administrator:
        permitted.add(ShellNav.ROLE_CAPABILITIES)

    offered = tuple(nav for nav in _PRESENTATION_ORDER if nav in permitted)
    navigation = navigation_for(*offered)
    return ShellView(
        authenticated=True,
        navigation=navigation,
        logout_csrf_token=csrf_token,
        # The first destination this caller is actually offered. Never a fixed
        # path, so it cannot name somewhere they would be refused.
        home_href=navigation[0].href,
    )


__all__ = [
    "ANONYMOUS_SHELL",
    "ShellLink",
    "ShellNav",
    "ShellView",
    "navigation_for",
    "resolve_current",
    "session_only_shell",
    "shell_for",
    "with_current",
]
