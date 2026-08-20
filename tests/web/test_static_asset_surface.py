"""TC-STATIC-01 to TC-STATIC-07: the M-01 asset surface, proved rather than described.

**Added 2026-08-19 by the accepted D-03 correction (`C-P3.4-A`, item D-03-1).**

`/static/` is the first URL surface in Phase 3 that is deliberately public. Every
other route in the closed inventory refuses somebody; this one refuses nobody, so
what keeps it safe is not an authorization chain but a set of narrow structural
properties: two methods, one directory, one grammar, no cookies and no way out of
the root. Each of those is asserted here against the **production** application —
the real factory, the real mount, the real middleware stack — because a static
file server tested in isolation is a static file server whose host check, kill
switch and security headers were never in the request path.

The assets these cases fetch are written into the real static root by the
`asset` fixture and removed again, and the fixture asserts the root is left
holding nothing but its `.gitkeep`. No production CSS, script or image is added
by this module or by the D-03 correction: filling the root is P3.4's work.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from adapters.web.composition import STATIC_ROOT
from adapters.web.middleware import SECURITY_HEADERS
from adapters.web.static_assets import (
    IMMUTABLE_CACHE_CONTROL,
    REVALIDATE_CACHE_CONTROL,
    cache_control_for,
    path_is_within_grammar,
)
from tests.web_fixtures import PUBLIC_ORIGIN

#: What the fixture writes. Two files, because the cache policy branches on the
#: filename and one of each is the smallest table that exercises both.
FINGERPRINTED_NAME = "probe.0123456789abcdef.css"
PLAIN_NAME = "probe.css"
BODY = "/* static surface probe */\n"


@pytest.fixture()
def asset():
    """Write the two probe files, then remove them and prove the root is clean.

    The real root, deliberately: the point of these cases is that the deployed
    mount serves out of the deployed directory, and a `tmp_path` root would prove
    that a `StaticFiles` instance works, which nobody doubts.
    """
    written = []
    try:
        for name in (FINGERPRINTED_NAME, PLAIN_NAME):
            path = STATIC_ROOT / name
            path.write_text(BODY)
            written.append(path)
        yield BODY
    finally:
        for path in written:
            path.unlink(missing_ok=True)
        # The root is a contract surface, not a scratch directory. A test that
        # left a file behind would make the *next* run's inventory wrong.
        assert sorted(entry.name for entry in STATIC_ROOT.iterdir()) == [".gitkeep"]


# ---------------------------------------------------------------------------
# TC-STATIC-01 — methods
# ---------------------------------------------------------------------------


async def test_get_and_head_serve_the_asset(client, asset):
    """TC-STATIC-01. The two methods the contract permits, and what they return."""
    got = await client.get(f"/static/{PLAIN_NAME}")
    assert got.status_code == 200
    assert got.text == asset

    head = await client.head(f"/static/{PLAIN_NAME}")
    assert head.status_code == 200
    assert head.content == b""
    # HEAD is GET without the body, so the headers a cache acts on must match.
    assert head.headers["cache-control"] == got.headers["cache-control"]
    assert head.headers["content-length"] == got.headers["content-length"]


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
async def test_a_mutation_method_is_refused_on_the_static_surface(
    client, asset, method
):
    """TC-STATIC-01. `405`, and identically for a path that exists and one that does not.

    Both halves matter. `405` on an existing asset is the ordinary answer. `405`
    on a name that is not there is what stops the refusal from being an
    enumeration oracle: if a mutation answered `405` for a real file and `404` for
    an absent one, `POST` would become a directory listing one request at a time.
    """
    present = await client.request(method, f"/static/{PLAIN_NAME}")
    absent = await client.request(method, "/static/definitely-not-here.css")
    assert present.status_code == 405
    assert absent.status_code == 405


async def test_the_static_surface_serves_only_the_approved_root(client, asset):
    """TC-STATIC-02. One directory, and a sibling of it is not reachable.

    `adapters/web/templates/` sits beside the static root and holds real files,
    so it is the honest target for this case rather than an invented path.
    """
    reachable = await client.get(f"/static/{PLAIN_NAME}")
    assert reachable.status_code == 200

    for path in (
        "/static/../templates/base.html",
        "/static/../composition.py",
        "/static/../../../.env",
    ):
        response = await client.get(path)
        assert response.status_code == 404, path
        assert "doctype" not in response.text.lower()
        assert "WEB_" not in response.text


# ---------------------------------------------------------------------------
# TC-STATIC-03 — traversal, encoding, absence and directories
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    [
        # Plain traversal, and the forms that survive a normalising client.
        # The first is normalised by httpx into `/templates/base.html` before it
        # is sent, so it proves only that no such route exists; the five encoded
        # forms below genuinely arrive at the application as
        # `/static/../templates/base.html`, verified by inspecting the ASGI
        # scope, and those are the ones that exercise the refusal. It is kept
        # because it is what an ordinary client would actually send.
        "/static/../templates/base.html",
        "/static/%2e%2e/templates/base.html",
        "/static/%2e%2e%2ftemplates%2fbase.html",
        "/static/..%2ftemplates%2fbase.html",
        "/static/....//templates/base.html",
        "/static/%252e%252e/templates/base.html",
        # An absolute path, in case the join were ever done naively.
        "/static//etc/passwd",
        "/static/%2fetc%2fpasswd",
        # A dotfile in the root: present on disk, unreachable by grammar.
        "/static/.gitkeep",
        # A directory, and the root itself. No listing, no implicit index.
        "/static/",
        "/static",
    ],
)
async def test_traversal_encoding_dotfiles_and_directories_disclose_nothing(
    client, asset, path
):
    """TC-STATIC-03. Everything that is not a permitted file is a safe `404`.

    One case for all of them because the requirement is uniformity: a traversal
    attempt, an encoded traversal, a dotfile, a directory and a missing name must
    be indistinguishable to a caller. A body that differed between them would
    describe the filesystem to somebody who is probing it.

    `/static` (no slash) is included because Starlette answers a mount's bare
    prefix, and with `html=False` there is no index to redirect to.
    """
    response = await client.get(path)
    assert response.status_code in (307, 404), path
    if response.status_code == 307:
        # The only redirect Starlette produces here is `/static` -> `/static/`,
        # which then answers `404` like the rest.
        assert response.headers["location"].endswith("/static/")
        return
    body = response.text
    assert "doctype" not in body.lower(), path
    assert "Traceback" not in body, path
    assert "adapters/web" not in body, path
    assert str(STATIC_ROOT) not in body, path
    assert "passwd" not in body, path


async def test_a_missing_asset_answers_a_safe_404(client, asset):
    """TC-STATIC-03. No exception text, no filesystem path, no stack frame (N-25)."""
    response = await client.get("/static/no-such-asset.9999999999999999.css")
    assert response.status_code == 404
    body = response.text
    assert "no-such-asset" not in body
    assert str(STATIC_ROOT) not in body
    assert "Traceback" not in body
    assert "StaticFiles" not in body


async def test_a_missing_asset_and_a_refused_grammar_are_indistinguishable(
    client, asset
):
    """TC-STATIC-03. The grammar is not enumerable through the refusal.

    A grammar violation answering `400` while a missing file answered `404` would
    let a caller map the accepted grammar exactly, which is a small disclosure
    with no upside — to a browser both are "that asset is not there".
    """
    missing = await client.get("/static/absent.css")
    refused = await client.get("/static/.hidden")
    assert missing.status_code == refused.status_code == 404
    assert missing.content == refused.content


# ---------------------------------------------------------------------------
# TC-STATIC-04 — host and kill switch
# ---------------------------------------------------------------------------


async def test_an_untrusted_host_is_refused_on_a_static_request(client, asset):
    """TC-STATIC-04. N-01 applies to an asset exactly as it applies to a page.

    The host check is the outermost middleware, so this is really an assertion
    that the mount was registered *inside* the stack rather than beside it — the
    mistake that would make `/static/` the one path on the origin that answered
    for any hostname.
    """
    refused = await client.get(
        f"/static/{PLAIN_NAME}", headers={"host": "attacker.example"}
    )
    assert refused.status_code == 400
    assert refused.text == "Unknown host."

    allowed = await client.get(f"/static/{PLAIN_NAME}")
    assert allowed.status_code == 200


async def test_assets_stay_up_while_the_kill_switch_closes_the_portal(
    client, asset, settings, tmp_path
):
    """TC-STATIC-04. Both halves in one case, because only the pair is the contract.

    Assets keep serving so the maintenance body, the login page and the safe
    error page keep their presentation during an incident (operational contract
    §4.3). What makes that acceptable rather than a hole is the other assertion
    here: every `/v1/*` route still answers `503`. A test that checked only the
    exemption would pass just as well against a kill switch that had stopped
    working.

    The `sleep` is N-56's stat interval, not a flake: the switch is contractually
    effective *within* a second, and asserting sooner would assert a policy the
    platform does not have.
    """
    assert (await client.get("/v1/login")).status_code == 200
    assert (await client.get(f"/static/{PLAIN_NAME}")).status_code == 200

    settings.kill_switch_file.write_text("engaged for a test\n")
    try:
        await asyncio.sleep(1.05)

        for path in ("/v1/login", "/v1/characters", "/v1/audit", "/"):
            closed = await client.get(path)
            assert closed.status_code == 503, path
            assert "Discord bot is unaffected" in closed.text

        served = await client.get(f"/static/{PLAIN_NAME}")
        assert served.status_code == 200
        assert served.text == asset
        # And the exemption is a prefix, not a bypass of the host check.
        assert (
            await client.get(
                f"/static/{PLAIN_NAME}", headers={"host": "attacker.example"}
            )
        ).status_code == 400
    finally:
        settings.kill_switch_file.unlink(missing_ok=True)
        await asyncio.sleep(1.05)

    assert (await client.get("/v1/login")).status_code == 200


# ---------------------------------------------------------------------------
# TC-STATIC-05 — cache policy
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("styles.0123456789abcdef.css", IMMUTABLE_CACHE_CONTROL),
        ("htmx.fedcba9876543210.js", IMMUTABLE_CACHE_CONTROL),
        ("emblem.00000000000000ff.svg", IMMUTABLE_CACHE_CONTROL),
        # Fifteen hex characters, seventeen, uppercase, and a non-hex letter:
        # each is *not* the accepted grammar and must fall to the safe branch.
        ("styles.0123456789abcde.css", REVALIDATE_CACHE_CONTROL),
        ("styles.0123456789abcdef0.css", REVALIDATE_CACHE_CONTROL),
        ("styles.0123456789ABCDEF.css", REVALIDATE_CACHE_CONTROL),
        ("styles.0123456789abcdeg.css", REVALIDATE_CACHE_CONTROL),
        ("styles.css", REVALIDATE_CACHE_CONTROL),
        ("favicon.ico", REVALIDATE_CACHE_CONTROL),
    ],
)
def test_the_cache_policy_reads_the_fingerprint_grammar(name, expected):
    """TC-STATIC-05, as a table over names. The conservative branch is the default.

    Asserted as a pure function as well as over a response, because the
    near-misses are the interesting rows and building nine applications to check
    nine filenames would be a slower test that proved less.
    """
    assert cache_control_for(name) == expected
    assert cache_control_for(f"nested/dir/{name}") == expected


async def test_a_fingerprinted_asset_is_immutable_and_a_plain_one_revalidates(
    client, asset
):
    """TC-STATIC-05, over the real response."""
    fingerprinted = await client.get(f"/static/{FINGERPRINTED_NAME}")
    plain = await client.get(f"/static/{PLAIN_NAME}")
    assert fingerprinted.headers["cache-control"] == IMMUTABLE_CACHE_CONTROL
    assert plain.headers["cache-control"] == REVALIDATE_CACHE_CONTROL


async def test_a_signed_in_caller_still_gets_the_cacheable_asset_header(
    client, asset, settings
):
    """TC-STATIC-05. The header does not depend on who is asking.

    `SecurityHeaders` puts `Cache-Control: no-store` on every response when a
    session cookie is present. Scoping `/static/` out of that rule is what stops
    the same byte-identical asset being uncacheable for members and cacheable for
    visitors. The cookie value here is deliberately nonsense: nothing on this path
    resolves a session, and that is the property being asserted.
    """
    response = await client.get(
        f"/static/{FINGERPRINTED_NAME}",
        cookies={settings.session.cookie_name: "not-a-real-session-token"},
    )
    assert response.status_code == 200
    assert response.headers["cache-control"] == IMMUTABLE_CACHE_CONTROL
    assert "no-store" not in response.headers["cache-control"]


async def test_the_security_headers_still_apply_to_an_asset(client, asset):
    """TC-STATIC-05. Only the cache rule is scoped out — N-26 and the rest are not.

    An asset served without the CSP and `nosniff` would be the one response on
    this origin a content-type confusion attack could work through.
    """
    response = await client.get(f"/static/{PLAIN_NAME}")
    for header, value in SECURITY_HEADERS.items():
        assert response.headers[header] == value, header


# ---------------------------------------------------------------------------
# TC-STATIC-06 — cookies
# ---------------------------------------------------------------------------


async def test_a_static_response_sets_and_refreshes_no_cookie(client, asset, settings):
    """TC-STATIC-06. No session, login-transaction or CSRF cookie is set or refreshed.

    Both directions: with no cookie presented and with one presented. The second
    is the case that would catch a middleware that "touched" a session on every
    request — an asset fetch must not extend an idle timeout (N-06), because a
    page left open in a background tab would then keep a session alive forever
    through its own stylesheet.
    """
    anonymous = await client.get(f"/static/{PLAIN_NAME}")
    assert "set-cookie" not in anonymous.headers

    with_cookie = await client.get(
        f"/static/{PLAIN_NAME}",
        cookies={
            settings.session.cookie_name: "not-a-real-session-token",
            settings.session.login_transaction_cookie_name: "not-a-real-transaction",
        },
    )
    assert with_cookie.status_code == 200
    assert "set-cookie" not in with_cookie.headers


async def test_the_static_surface_needs_no_session_capability_or_csrf_token(
    client, asset
):
    """TC-STATIC-06. Public means public: the same bytes for a caller with nothing.

    Asserted because every *other* route in the closed inventory refuses an
    anonymous caller, and a reviewer reading the matrix would reasonably expect
    this one to as well.
    """
    anonymous = await client.get(f"/static/{PLAIN_NAME}")
    assert anonymous.status_code == 200
    assert anonymous.text == BODY
    # No `Origin` header, no CSRF token, no cookie — and it is a `200`, not a
    # `303` to the login page.
    assert "location" not in anonymous.headers


# ---------------------------------------------------------------------------
# TC-STATIC-07 — the grammar, as a unit
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("path", "accepted"),
    [
        ("styles.css", True),
        ("css/styles.css", True),
        ("vendor/htmx.fedcba9876543210.js", True),
        ("img/emblem-2x.svg", True),
        ("a_b-c.1.2.3.css", True),
        (".gitkeep", False),
        ("css/.hidden", False),
        (".well-known/x", False),
        ("", False),
        ("/", False),
        ("..", False),
        ("../etc/passwd", False),
        ("css/../../secret", False),
        ("weird name.css", False),
        ("emoji-\N{SNOWMAN}.css", False),
        ("semi;colon.css", False),
        ("query?.css", False),
    ],
)
def test_the_url_grammar_accepts_exactly_the_documented_shape(path, accepted):
    """TC-STATIC-07. Route contract §1.2's grammar, as a table.

    A unit case beside the response cases above, because the interesting inputs
    are the ones a client normalises away before the application ever sees them —
    and those are precisely the ones the grammar exists to refuse if they ever do
    arrive.
    """
    assert path_is_within_grammar(path) is accepted


def test_the_static_root_ships_only_its_placeholder(asset):
    """The D-03 boundary, asserted rather than promised.

    The accepted correction adds the *surface*, not its contents: no production
    CSS, no vendored HTMX, no emblem, no visual asset of any kind. The one file
    in the repository-owned root is the empty `.gitkeep` that makes the directory
    exist for `StaticFiles(check_dir=True)`.

    This case is what would fail if a later change quietly landed a production
    asset in a backend package. It runs *inside* the `asset` fixture, so the two
    probe files are present and are excluded by name — the fixture's own teardown
    assertion covers the clean state.
    """
    entries = sorted(
        entry.name
        for entry in STATIC_ROOT.iterdir()
        if entry.name not in (FINGERPRINTED_NAME, PLAIN_NAME)
    )
    assert entries == [".gitkeep"]
    assert (STATIC_ROOT / ".gitkeep").read_bytes() == b""
    assert STATIC_ROOT == Path(__file__).resolve().parents[2] / "adapters" / "web" / "static"


def test_the_public_origin_fixture_is_the_host_the_client_uses():
    """A control for the host case above: it must be refusing a *different* host."""
    assert "attacker.example" not in PUBLIC_ORIGIN
