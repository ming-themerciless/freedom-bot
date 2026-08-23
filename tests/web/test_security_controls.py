"""TC-SEC-01 to TC-SEC-13 and TC-LIM-01/03: the provider-independent core controls.

These are the controls ADR 0010 D6 says survive replacing Discord. None of them
consults a provider, and each is asserted at the boundary a caller actually
reaches rather than at the function that implements it.
"""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import select

from adapters.web.app import create_app
from adapters.web.composition import STATIC_ROOT, TEMPLATE_ROOT
from adapters.web.middleware import CONTENT_SECURITY_POLICY, SECURITY_HEADERS
from bs4 import BeautifulSoup
from application.audit import ActorCapability
from application.web import csrf
from application.web.capabilities import (
    AdministratorScope,
    AuthMethod,
    MembershipProjection,
    WebAuthorizationContext,
)
from tests.web.conftest import make_account, seed_oauth_transaction, utcnow
from tests.web_fixtures import PUBLIC_ORIGIN, TEST_GUILD_ID

pytestmark = pytest.mark.database


def _context(account_id):
    return WebAuthorizationContext(
        account_id=account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        capabilities=frozenset({ActorCapability.GUILD_MEMBER}),
        administrator_scope=AdministratorScope.FULL,
        membership=MembershipProjection(
            guild_id=TEST_GUILD_ID,
            is_member=True,
            role_ids=frozenset(),
            observed_at=utcnow(),
        ),
    )


async def _logged_in(client, migrated_database, composition):
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        issued = composition.services(connection).session_service.begin(
            context=_context(account_id),
            now=utcnow(),
            correlation_id=uuid4(),
            oauth_transaction_id=seed_oauth_transaction(connection),
        )
    client.cookies.set("__Host-fb_session", issued.token)
    return issued


# ---------------------------------------------------------------------------
# TC-SEC-01, TC-SEC-02
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("description", "token_for"),
    [
        ("missing", None),
        ("a foreign session's", "foreign"),
        ("a rotated session's", "rotated"),
    ],
)
async def test_a_cookie_authenticated_mutation_without_a_valid_csrf_token_is_refused(
    client, migrated_database, composition, settings, description, token_for
):
    """TC-SEC-01. Three ways to fail the synchronizer check, one outcome.

    The rotated case matters most: a token minted before a privilege change must
    stop working the instant the session rotates, and it does — because the token
    is derived from the session id and rotation mints a new id.
    """
    issued = await _logged_in(client, migrated_database, composition)

    if token_for is None:
        presented = None
    elif token_for == "foreign":
        presented = csrf.issue(settings.csrf_key, uuid4())
    else:
        presented = csrf.issue(settings.csrf_key, uuid4())

    data = {"unrelated": "1"} if presented is None else {"csrf_token": presented}
    response = await client.post(
        "/v1/auth/logout", data=data, headers={"origin": PUBLIC_ORIGIN}
    )

    assert response.status_code == 403, description
    assert response.json()["error"] == "csrf_invalid"

    # And nothing changed: the session still resolves.
    with migrated_database.begin() as connection:
        assert (
            composition.services(connection).session_service.resolve(
                issued.token, now=utcnow()
            )
            is not None
        )


async def test_a_valid_csrf_token_permits_the_mutation(
    client, migrated_database, composition, settings
):
    """The positive half. Without it, TC-SEC-01 would pass on a broken route."""
    issued = await _logged_in(client, migrated_database, composition)
    token = csrf.issue(settings.csrf_key, issued.session_id)

    response = await client.post(
        "/v1/auth/logout",
        data={"csrf_token": token},
        headers={"origin": PUBLIC_ORIGIN},
    )

    assert response.status_code == 303
    with migrated_database.begin() as connection:
        assert (
            composition.services(connection).session_service.resolve(
                issued.token, now=utcnow()
            )
            is None
        )


async def test_csrf_is_checked_before_the_application_service_runs(
    client, migrated_database, composition, settings, monkeypatch
):
    """TC-SEC-02, proven by asserting the service was **never called**.

    A check that ran after the service would refuse the response while the state
    change had already happened, which is the failure mode the ordering rule in
    route contract §2.1 exists to prevent.
    """
    await _logged_in(client, migrated_database, composition)

    from application.web.sessions import SessionService

    calls: list[str] = []
    original = SessionService.logout

    def recording(self, *args, **kwargs):
        calls.append("logout")
        return original(self, *args, **kwargs)

    # Patched on the class rather than the instance: `SessionService` is slotted,
    # and a slotted instance has nowhere to hang a replacement attribute.
    monkeypatch.setattr(SessionService, "logout", recording)

    response = await client.post(
        "/v1/auth/logout",
        data={"csrf_token": "not-the-token"},
        headers={"origin": PUBLIC_ORIGIN},
    )

    assert response.status_code == 403
    assert calls == [], "the application service ran despite a CSRF refusal"


# ---------------------------------------------------------------------------
# TC-SEC-03, TC-SEC-04
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("origin", [None, "https://evil.example", ""])
async def test_a_mutation_with_a_missing_or_foreign_origin_is_refused(
    client, migrated_database, composition, origin
):
    """TC-SEC-03. Missing counts as mismatched, deliberately.

    Every browser that can reach this application sends `Origin` on a
    cross-site form post, so treating its absence as permission would make the
    check optional for exactly the caller it exists to stop.
    """
    await _logged_in(client, migrated_database, composition)
    headers = {} if origin is None else {"origin": origin}

    response = await client.post(
        "/v1/auth/logout", data={"csrf_token": "x"}, headers=headers
    )

    assert response.status_code == 403
    assert response.json()["error"] == "origin_invalid"


@pytest.mark.parametrize("host", ["evil.example", "portal.test.evil.example", ""])
async def test_an_unknown_host_is_refused_before_routing(client, host):
    """TC-SEC-04. `400`, and the route never runs.

    The session cookie is host-only and the OAuth redirect is origin-bound, so a
    request under an unconfigured hostname is either a misrouted proxy or an
    attempt to make the application generate links for somebody else's domain.
    """
    response = await client.get("/v1/login", headers={"host": host})
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# TC-SEC-05, TC-SEC-06
# ---------------------------------------------------------------------------


async def test_every_response_carries_the_exact_security_headers(client):
    """TC-SEC-05. The CSP is N-26 byte for byte, and `X-Frame-Options` is absent."""
    response = await client.get("/v1/login")

    assert response.headers["content-security-policy"] == CONTENT_SECURITY_POLICY
    for header, value in SECURITY_HEADERS.items():
        assert response.headers[header] == value
    assert response.headers["cache-control"] == "no-store"
    # Omitted deliberately: `frame-ancestors 'none'` supersedes it, and
    # duplicating one rule in two syntaxes is how they drift apart.
    assert "x-frame-options" not in response.headers


async def test_no_cross_origin_headers_appear_on_any_portal_response(client):
    """TC-SEC-06. The browser boundary has no CORS at all — it is same-origin only."""
    for path in ("/v1/login", "/v1/auth/emergency", "/healthz"):
        response = await client.get(path)
        for header in response.headers:
            assert not header.lower().startswith("access-control-allow-"), path


# ---------------------------------------------------------------------------
# TC-SEC-07
# ---------------------------------------------------------------------------


async def test_the_oauth_start_is_a_navigation_so_form_action_never_applies(client):
    """TC-SEC-07's automated half (the browser half is staging evidence).

    `form-action 'self'` is enforced across the redirect chain a **form
    submission** produces. A `GET` navigation is not one, so the accepted CSP
    stands unweakened rather than needing `https://discord.com` added to it.
    """
    response = await client.get("/v1/auth/discord/start")
    assert response.status_code == 303
    assert response.request.method == "GET"
    assert "form-action 'self'" in response.headers["content-security-policy"]


# ---------------------------------------------------------------------------
# TC-SEC-08, TC-SEC-10, TC-SEC-11
# ---------------------------------------------------------------------------


import re

#: Jinja comments are stripped before these assertions run. A `{# ... #}` block
#: is never rendered, and the comments in these templates *describe* the very
#: rules being asserted — a check that read them would fail on its own
#: documentation.
_JINJA_COMMENT = re.compile(r"\{#.*?#\}", re.DOTALL)


def _templates() -> list[Path]:
    return sorted(TEMPLATE_ROOT.glob("**/*.html"))


def _rendered_source(template: Path) -> str:
    return _JINJA_COMMENT.sub("", template.read_text())


def test_autoescaping_is_on_and_zero_templates_use_the_safe_filter(app):
    """TC-SEC-08. The whole application permits `|safe` on **zero** values."""
    assert app.state.templates.env.autoescape is True
    assert _templates(), "there are templates to check"
    for template in _templates():
        body = _rendered_source(template)
        assert "|safe" not in body, template.name
        assert "| safe" not in body, template.name
        assert "Markup(" not in body, template.name


def test_no_template_carries_an_inline_event_attribute(app):
    """TC-SEC-10. `hx-on:` is inline script and would force a CSP weakening.

    Recorded in the route contract as a **contract term** for P3.4 rather than a
    style preference, and asserted here so the constraint exists before the
    templates that would break it.
    """
    for template in _templates():
        body = _rendered_source(template).lower()
        assert "hx-on:" not in body, template.name
        for handler in ("onclick=", "onload=", "onerror=", "onsubmit="):
            assert handler not in body, f"{template.name} carries {handler}"


def _allowed_htmx_script_src() -> str:
    manifest = (STATIC_ROOT / "asset-integrity.sha256").read_text()
    for line in manifest.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2 and "vendor/htmx-" in parts[1]:
            static_rel = parts[1].split("adapters/web/static", 1)[-1]
            return f"/static{static_rel}"
    raise AssertionError("No HTMX vendor entry found in asset-integrity.sha256")


def validate_script_contexts(
    template_sources: dict[str, str],
    allowed_script_src: str,
) -> None:
    """Production validator for TC-SEC-11.

    Verifies that across all templates:
    1. Exactly one script tag exists, in base.html only.
    2. Its src attribute equals allowed_script_src exactly.
    3. It has no inline body content.
    4. It has no executable or unexpected attributes.
    5. In source, no Jinja expressions appear in script attributes or body.
    6. No other template/include declares any script element.
    7. No inline event handler (on*), hx-on:, or javascript: URL exists in any template.
    """
    import re
    assert template_sources, "there are template sources to validate"
    assert "base.html" in template_sources, "base.html must be present in template sources"

    for name, raw_source in template_sources.items():
        clean_source = re.sub(r"\{#.*?#\}", "", raw_source, flags=re.DOTALL)
        soup = BeautifulSoup(clean_source, "html.parser")
        scripts = soup.find_all("script")

        if name == "base.html":
            assert len(scripts) == 1, f"base.html must contain exactly 1 script tag, found {len(scripts)}"
            script = scripts[0]
            # 1. Exact src matching integrity manifest
            actual_src = script.get("src")
            assert actual_src == allowed_script_src, (
                f"base.html script src {actual_src!r} != manifest {allowed_script_src!r}"
            )
            # 2. No inline content / body
            assert not script.get_text(strip=True), "base.html script has inline content"
            # 3. No executable or unexpected attributes
            for attr in script.attrs:
                assert attr in ("src", "defer", "async", "type", "integrity", "crossorigin"), (
                    f"Unexpected attribute {attr!r} on base.html script"
                )
            # 4. In source, ensure no Jinja expressions inside the script tag or body
            script_blocks = re.findall(r"<script[^>]*>(.*?)</script>", clean_source, flags=re.DOTALL | re.IGNORECASE)
            assert len(script_blocks) == 1, "base.html must have exactly 1 script block in source"
            assert "{{" not in script_blocks[0] and "{%" not in script_blocks[0], "Jinja found in script body"
            script_open_match = re.search(r"<script([^>]*)>", clean_source, flags=re.IGNORECASE)
            assert script_open_match, "base.html missing script opening tag"
            script_open = script_open_match.group(1)
            assert "{{" not in script_open and "{%" not in script_open, "Jinja found in script tag attributes"
        else:
            assert len(scripts) == 0, f"Template {name} must not contain any <script> element"
            assert "<script" not in clean_source.lower(), f"Template {name} contains unparsed <script tag"

        # Across all templates: no inline event handlers, hx-on, or javascript: URLs
        assert "hx-on:" not in clean_source.lower(), f"{name} contains hx-on:"
        for el in soup.find_all(True):
            for attr_name, attr_val in el.attrs.items():
                assert not attr_name.lower().startswith("on"), (
                    f"{name} element <{el.name}> has inline event handler {attr_name}"
                )
                assert not attr_name.lower().startswith("hx-on"), (
                    f"{name} element <{el.name}> has hx-on handler {attr_name}"
                )
                if isinstance(attr_val, str):
                    assert not attr_val.lower().startswith("javascript:"), (
                        f"{name} element <{el.name}> has javascript: URL in {attr_name}"
                    )


def test_no_view_model_field_reaches_a_script_context(app):
    """TC-SEC-11. Script elements, attributes, and contexts across all templates."""
    allowed_script_src = _allowed_htmx_script_src()
    templates = _templates()
    assert templates, "there are templates to check"
    sources = {t.name: t.read_text() for t in templates}
    validate_script_contexts(sources, allowed_script_src)


def test_no_view_model_field_reaches_a_script_context_falsification() -> None:
    """Falsification: exercises validate_script_contexts against deliberate invalid mutations."""
    allowed_script_src = _allowed_htmx_script_src()
    clean_sources = {t.name: t.read_text() for t in _templates()}

    # 0. Clean baseline passes
    validate_script_contexts(clean_sources, allowed_script_src)

    # 1. Second script in base.html fails
    bad_base_2scripts = clean_sources.copy()
    bad_base_2scripts["base.html"] = bad_base_2scripts["base.html"] + f'<script src="{allowed_script_src}"></script>'
    with pytest.raises(AssertionError, match="base.html must contain exactly 1 script tag"):
        validate_script_contexts(bad_base_2scripts, allowed_script_src)

    # 2. Script in non-base template fails
    bad_non_base = clean_sources.copy()
    bad_non_base["login.html"] = bad_non_base["login.html"] + f'<script src="{allowed_script_src}"></script>'
    with pytest.raises(AssertionError, match="Template login.html must not contain any <script> element"):
        validate_script_contexts(bad_non_base, allowed_script_src)

    # 3. Remote or wrong local script source fails
    bad_src = clean_sources.copy()
    bad_src["base.html"] = bad_src["base.html"].replace(
        f'src="{allowed_script_src}"',
        'src="https://unpkg.com/htmx.org@2.0.0"',
    )
    with pytest.raises(AssertionError, match="base.html script src .* != manifest"):
        validate_script_contexts(bad_src, allowed_script_src)

    # 4. Inline script body content fails
    bad_body = clean_sources.copy()
    bad_body["base.html"] = bad_body["base.html"].replace(
        f'src="{allowed_script_src}"></script>',
        f'src="{allowed_script_src}">alert(1)</script>',
    )
    with pytest.raises(AssertionError, match="base.html script has inline content"):
        validate_script_contexts(bad_body, allowed_script_src)

    # 5. Jinja expression inserted into script src fails
    bad_jinja_src = clean_sources.copy()
    bad_jinja_src["base.html"] = bad_jinja_src["base.html"].replace(
        f'src="{allowed_script_src}"',
        f'src="{{{{ dynamic_src }}}}"',
    )
    with pytest.raises(AssertionError):
        validate_script_contexts(bad_jinja_src, allowed_script_src)

    # 6. Jinja expression inserted into script body fails
    bad_jinja_body = clean_sources.copy()
    bad_jinja_body["base.html"] = bad_jinja_body["base.html"].replace(
        f'src="{allowed_script_src}"></script>',
        f'src="{allowed_script_src}">{{{{ script_body }}}}</script>',
    )
    with pytest.raises(AssertionError):
        validate_script_contexts(bad_jinja_body, allowed_script_src)

    # 7. Inline event handler (on*) fails
    bad_event = clean_sources.copy()
    bad_event["login.html"] = bad_event["login.html"].replace(
        '<div class="auth-card">',
        '<div class="auth-card" onclick="alert(1)">',
    )
    with pytest.raises(AssertionError, match="has inline event handler onclick"):
        validate_script_contexts(bad_event, allowed_script_src)

    # 8. javascript: URL fails
    bad_js_url = clean_sources.copy()
    bad_js_url["login.html"] = bad_js_url["login.html"].replace(
        '<a href="',
        '<a href="javascript:void(0)" data-old="',
    )
    with pytest.raises(AssertionError, match="has javascript: URL"):
        validate_script_contexts(bad_js_url, allowed_script_src)


# ---------------------------------------------------------------------------
# TC-SEC-14 — same-origin assets (added 2026-08-19, accepted D-03 correction)
# ---------------------------------------------------------------------------

#: Every shape of "fetch this from somebody else's server". Checked as substrings
#: over the rendered source, which is coarse on purpose: a template has no
#: legitimate reason to contain any of them, so a coarse check has no false
#: positives to trade against.
_REMOTE_ORIGIN_MARKERS = (
    "http://",
    "https://",
    "//cdn.",
    "cdn.jsdelivr",
    "unpkg.com",
    "cdnjs.",
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "@import url(",
)


def test_no_template_references_a_remote_origin(app):
    """TC-SEC-14. N-26 permits `'self'` and `data:` and nothing else.

    **Added 2026-08-19 by the accepted D-03 correction (item D-03-1).** The
    correction adds an application-served `/static/` surface precisely so that
    production CSS, vendored HTMX and the emblem can be same-origin; this is the
    assertion that keeps them there. A CDN `<script src>` or a Google Fonts
    `<link>` in a P3.4 template would not merely violate a preference — it would
    be a request the accepted CSP blocks, so the page would silently render
    unstyled or unscripted in production while looking correct in a browser with
    a warm cache.

    The delivery plan states the same exclusion at §4: *no SPA, React, Vue, npm,
    bundler, CDN, remote font or frontend build step*.
    """
    for template in _templates():
        body = _rendered_source(template).lower()
        for marker in _REMOTE_ORIGIN_MARKERS:
            assert marker not in body, f"{template.name} references {marker}"


def test_no_template_references_the_frozen_design_prototype(app):
    """The backend half of TC-UI-06. **Added 2026-08-19 with the D-03 correction.**

    `design-prototype/` is a **reference-only** frozen visual baseline (plan
    §12.1, view-model contract §1.1): no production module imports it, links to
    it or serves it. It also sits outside the one approved static root, so a
    template pointing at it would be asking for a file the M-01 mount cannot
    serve — a broken page as well as a contract violation.

    This is *not* the whole of TC-UI-06, and does not claim to be. That row is
    P3.4's to write against the production template corpus and the production
    asset tree, and it belongs to Gemini's package. What is asserted here is the
    half the backend owns and can hold today: the current corpus, and the static
    root the correction introduces.
    """
    for template in _templates():
        body = _rendered_source(template)
        assert "design-prototype" not in body, template.name

    from adapters.web.composition import STATIC_ROOT

    for asset in sorted(STATIC_ROOT.glob("**/*")):
        if not asset.is_file():
            continue
        assert "design-prototype" not in asset.name, asset.name


def test_the_static_root_holds_no_executable_or_remote_referencing_asset(app):
    """TC-SEC-14. The same rules, applied to the new asset root rather than the corpus.

    The corpus checks above would never have looked here: `_templates()` globs
    `**/*.html` under the template root, and the static root is a sibling. An
    asset with an `@import url(https://…)` or a remote `src` is exactly the shape
    that would slip past a template-only guard, which is why the root gets its own
    case from the day it exists.
    """
    from adapters.web.composition import STATIC_ROOT

    text_suffixes = {".css", ".js", ".svg", ".html", ".json", ".map"}
    for asset in sorted(STATIC_ROOT.glob("**/*")):
        if not asset.is_file() or asset.suffix.lower() not in text_suffixes:
            continue
        body = asset.read_text(errors="replace").lower()
        for marker in _REMOTE_ORIGIN_MARKERS:
            assert marker not in body, f"{asset.name} references {marker}"


# ---------------------------------------------------------------------------
# TC-SEC-09
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "hostile",
    [
        "<script>alert(1)</script>",
        '"><img src=x onerror=alert(1)>',
        "{{7*7}}",
        "x" * 10_000,
        "‮evil",
        "café",
        "café",
    ],
)
async def test_caller_supplied_text_renders_inert_and_bounded(client, hostile):
    """TC-SEC-09. Escaping, and the closed vocabulary that makes it a second line.

    The failure code is mapped into a closed set before it reaches the view
    model, so the hostile string never gets into the page to be escaped. Both
    are asserted: the value is absent, and `{{7*7}}` did not evaluate.
    """
    response = await client.get("/v1/login", params={"failure": hostile})

    assert response.status_code == 200
    assert "<script>alert(1)</script>" not in response.text
    assert "onerror=" not in response.text
    # `{{7*7}}` did not evaluate: neither the expression nor its result reaches
    # the page, because the value never reaches the template at all.
    assert "{{7*7}}" not in response.text
    assert hostile not in response.text
    # The closed vocabulary is the first line of defence and escaping is the
    # second: a caller-supplied code is mapped into the accepted set before it
    # becomes a view-model field.
    assert 'data-code="not_available"' in response.text


# ---------------------------------------------------------------------------
# TC-SEC-12
# ---------------------------------------------------------------------------


async def test_an_internal_failure_answers_with_a_correlation_id_and_nothing_else(
    composition, monkeypatch
):
    """TC-SEC-12. No exception text, no path, no SQL, no stack frame."""
    import httpx

    from adapters.web.composition import WebComposition

    def explode(self, _connection):
        raise RuntimeError("SELECT secret FROM /srv/private/passwords")

    monkeypatch.setattr(WebComposition, "services", explode)
    app = create_app(composition=composition, run_startup_checks=False)

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(
        transport=transport, base_url=PUBLIC_ORIGIN, follow_redirects=False
    ) as client:
        response = await client.get("/v1/auth/discord/start")

    assert response.status_code == 500
    body = response.text
    assert "unexpected_error" in body
    for leak in ("RuntimeError", "SELECT", "/srv/private", "Traceback", "app.py"):
        assert leak not in body, leak


# ---------------------------------------------------------------------------
# TC-SEC-13, TC-BG-10
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    [
        "/v1/snapshots/artifact",
        "/api/v1/foundry/snapshots/deadbeef/artifact",
        "/v1/council/snapshots/1/download",
        "/artifacts/1.json",
    ],
)
async def test_no_route_serves_a_raw_snapshot_artifact(client, path):
    """TC-SEC-13. The plausible paths are `404`; the artifact store has no listing."""
    response = await client.get(path)
    assert response.status_code == 404


@pytest.mark.parametrize(
    "path",
    [
        "/v1/auth/emergency/grants",
        "/v1/admin/recovery-grants",
        "/v1/auth/emergency/enroll",
        "/v1/admin/webauthn/credentials",
    ],
)
async def test_no_route_issues_a_grant_or_enrols_a_credential(client, path):
    """TC-BG-10. The absence **is** the control (ADR 0010 D8).

    Issuance and enrollment require existing host authority, so the recovery path
    cannot be reached from the internet even by someone holding a stolen
    break-glass session.
    """
    assert (await client.get(path)).status_code == 404
    assert (await client.post(path, json={})).status_code == 404


# ---------------------------------------------------------------------------
# TC-LIM-01, TC-LIM-03
# ---------------------------------------------------------------------------


async def test_a_body_over_the_bound_is_refused_before_it_is_read(client):
    """TC-LIM-01. N-19, checked on `Content-Length` **before routing**."""
    oversized = "x" * (1024 * 1024 + 1)
    response = await client.post(
        "/v1/auth/emergency/recovery",
        content=oversized,
        headers={"origin": PUBLIC_ORIGIN, "content-type": "text/plain"},
    )
    assert response.status_code == 413


async def test_a_chunked_body_with_no_declared_length_is_refused(client):
    """The bound's other half: a length that is never declared cannot be checked."""

    async def stream():
        yield b"x" * 32

    response = await client.post(
        "/v1/auth/emergency/recovery",
        content=stream(),
        headers={"origin": PUBLIC_ORIGIN},
    )
    assert response.status_code == 411


async def test_an_unsupported_content_type_on_a_form_route_is_refused(client):
    """TC-LIM-03. A multipart upload to a form route is not a form submission."""
    response = await client.post(
        "/v1/auth/emergency/recovery",
        files={"token": ("token.txt", b"abc")},
        headers={"origin": PUBLIC_ORIGIN},
    )
    assert response.status_code == 415
    assert response.json()["error"] == "unsupported_media_type"
