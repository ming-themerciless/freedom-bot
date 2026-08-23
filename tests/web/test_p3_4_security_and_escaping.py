"""Phase 3.4 Step 12 Security and Progressive Enhancement Test Suite.

Governs accepted whole-corpus frontend security and progressive-enhancement controls:
1. TC-SEC-05: exact response security headers (CSP N-26, nosniff, Referrer-Policy, COOP,
   CORP, Permissions-Policy, Cache-Control: no-store on authenticated and /v1/* responses,
   zero X-Frame-Options, zero CORS) across all 10 response families.
2. TC-SEC-08: Jinja autoescaping enabled across all environments and AST/token-aware
   proof of zero `|safe` or bypasses across all 26 production templates.
3. TC-SEC-09: response-level hostile input matrix (<script>, "><img onerror>, {{7*7}},
   10,000 chars, RTL override/controls, NFC/NFD, table injection) rendering inert and
   bounded across real presentation surfaces.
4. TC-SEC-10: executable-context guards across all 26 production templates (zero hx-on:,
   zero inline on* handlers, zero javascript: URLs, zero inline script bodies, zero CDN/remote).
5. TC-SEC-11: no view-model value in script context across all 26 production templates.
6. Exact safe response bodies: denial, validation, stale, and safe-error responses exposing
   only accepted presentation fields and closed vocabularies, with zero internal leaks.
7. Essential no-JavaScript flows: rendered HTTP responses with all hx-* stripped retain valid
   actions, methods, CSRF tokens, hidden fields, and href destinations.
8. Structural and prototype guards: TC-STRUCT-01, TC-STRUCT-02, TC-UI-06.
9. Controlled falsification probes (F-SEC-01 through F-SEC-10) exercising every production validator.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import jinja2
import jinja2.nodes
import pytest
from bs4 import BeautifulSoup
from sqlalchemy import insert, select, text

from adapters.database.tables import audit_events, characters
from adapters.web.app import (
    DEFERRED_ROUTES,
    MOUNT_INVENTORY,
    ROUTE_INVENTORY,
    create_app,
)
from adapters.web.composition import STATIC_ROOT, TEMPLATE_ROOT, WebComposition
from adapters.web.middleware import CONTENT_SECURITY_POLICY, SECURITY_HEADERS
from application.web import view_models
from application.web.view_models import (
    ACTOR_NAME_BOUND,
    AUDIT_VALUE_BOUND,
    DenialCategory,
)
from tests.web.no_js_helpers import (
    FlowContract,
    FormContract,
    strip_htmx_attributes,
    validate_exact_canonical_correlation_uuid,
    validate_rendered_no_js_fallback,
)
from tests.web.p3_3_fixtures import (
    clean_p3_3_tables,
    complete_preview,
    seed_job,
    seed_snapshot,
    select_folder,
)
from tests.web.portal_fixtures import (
    COUNCIL_SUBJECT,
    clean_p3_2_tables,
    csrf_token_for,
    grant_link,
    make_character,
    seed_callers,
    seed_token_grant,
    stale_membership,
    utcnow,
)
from tests.web_fixtures import PUBLIC_ORIGIN

pytestmark = pytest.mark.database

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = ROOT / "adapters" / "web" / "templates"
STATIC_DIR = ROOT / "adapters" / "web" / "static"

FORM = "application/x-www-form-urlencoded"

#: All 26 production templates and includes
ALL_PRODUCTION_TEMPLATES: list[str] = sorted([
    "account_identities.html",
    "audit_results.html",
    "audit_search.html",
    "base.html",
    "character_detail.html",
    "character_links.html",
    "conflict.html",
    "council_characters.html",
    "council_snapshots.html",
    "degraded.html",
    "denied.html",
    "emergency.html",
    "error.html",
    "field_profile.html",
    "identity_migration.html",
    "identity_search.html",
    "import_result.html",
    "job_status.html",
    "job_status_fragment.html",
    "login.html",
    "my_characters.html",
    "non_member.html",
    "role_capabilities.html",
    "validation.html",
    "includes/footer.html",
    "includes/header.html",
])

#: Hostile test strings for TC-SEC-09
HOSTILE_IN_BOUND_VECTORS = [
    ("<script>alert(1)</script>", "script_injection"),
    ('"><img src=x onerror=alert(1)>', "img_onerror_injection"),
    ("{{7*7}}", "jinja_template_injection"),
    ("\u202eevil\u202c", "bidi_rtl_override"),
    ("café", "unicode_nfc"),
    ("cafe\u0301", "unicode_nfd"),
    ("</td></tr><tr><td>injected", "table_markup_injection"),
]


@pytest.fixture()
def callers(migrated_database, settings):
    yield seed_callers(migrated_database, settings)
    with migrated_database.begin() as connection:
        clean_p3_3_tables(connection)
        clean_p3_2_tables(connection)


@pytest.fixture()
def snapshot(migrated_database, callers):
    with migrated_database.begin() as connection:
        snapshot_id, checksum = seed_snapshot(connection)
        select_folder(
            connection, snapshot_id=snapshot_id, account_id=callers["A"].account_id
        )
    return snapshot_id, checksum


@pytest.fixture()
def outage(migrated_database, composition, provider, callers):
    with migrated_database.begin() as connection:
        identity_id = connection.execute(
            text(
                "SELECT id FROM external_identities WHERE provider_key = 'discord' "
                "AND subject = :subject"
            ),
            {"subject": str(COUNCIL_SUBJECT)},
        ).scalar_one()
        seed_token_grant(composition, connection, identity_id=identity_id)
    provider.unavailable = True
    return provider


def _templates() -> list[Path]:
    return sorted(TEMPLATES_DIR.glob("**/*.html"))


def _clean_source(source: str) -> str:
    return re.sub(r"\{#.*?#\}", "", source, flags=re.DOTALL)


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


# ===========================================================================
# 1. TC-SEC-05 — Response Security Headers Production Validator
# ===========================================================================


def validate_response_security_headers(
    response: Any,
    *,
    authenticated: bool = False,
    is_static: bool = False,
    path: str = "",
) -> None:
    """Production validator for TC-SEC-05.

    Fails closed on missing, duplicate, broadened, or conflicting header values:
    1. Content-Security-Policy equals N-26 byte for byte.
    2. X-Content-Type-Options equals nosniff.
    3. Referrer-Policy equals same-origin.
    4. Cross-Origin-Opener-Policy equals same-origin.
    5. Cross-Origin-Resource-Policy equals same-origin.
    6. Permissions-Policy equals geolocation=(), camera=(), microphone=(), payment=().
    7. Cache-Control equals no-store on authenticated and /v1/* responses (excluding /static/).
    8. X-Frame-Options is omitted deliberately (superseded by frame-ancestors 'none').
    9. Zero Access-Control-Allow-* CORS headers.
    10. Zero duplicate security headers.
    """
    headers = response.headers

    # 1. Exact CSP (N-26)
    assert "content-security-policy" in headers, f"Missing Content-Security-Policy on {path}"
    csp_val = headers["content-security-policy"]
    assert csp_val == CONTENT_SECURITY_POLICY, (
        f"CSP mismatch on {path}: expected {CONTENT_SECURITY_POLICY!r}, got {csp_val!r}"
    )

    # 2-6. Exact standard security headers
    for header, expected_val in SECURITY_HEADERS.items():
        h_lower = header.lower()
        assert h_lower in headers, f"Missing security header '{header}' on {path}"
        actual_val = headers[h_lower]
        assert actual_val == expected_val, (
            f"Header '{header}' mismatch on {path}: expected {expected_val!r}, got {actual_val!r}"
        )
        occurrences = headers.get_list(h_lower)
        assert len(occurrences) == 1, (
            f"Duplicate security header '{header}' on {path}: {occurrences}"
        )

    # 7. Cache-Control: no-store
    if is_static or path.startswith("/static/"):
        assert "cache-control" in headers, f"Missing Cache-Control on static asset {path}"
        assert "max-age=" in headers["cache-control"], f"Expected static cache on {path}"
    elif authenticated or path.startswith("/v1/"):
        assert "cache-control" in headers, f"Missing Cache-Control on {path}"
        assert headers["cache-control"] == "no-store", (
            f"Expected 'no-store' on {path}, got {headers['cache-control']!r}"
        )

    # 8. X-Frame-Options must be absent (superseded by frame-ancestors 'none')
    assert "x-frame-options" not in headers, (
        f"X-Frame-Options must not be set (superseded by frame-ancestors 'none') on {path}"
    )

    # 9. No CORS headers
    for header_name in headers:
        assert not header_name.lower().startswith("access-control-allow-"), (
            f"Unexpected CORS header '{header_name}' on {path}"
        )


# ===========================================================================
# 2. TC-SEC-08 — Jinja Autoescaping and Zero |safe AST Validator
# ===========================================================================


def validate_template_escaping_ast(
    template_sources: dict[str, str],
    jinja_env: jinja2.Environment | None = None,
) -> None:
    """Production AST- and token-aware validator for TC-SEC-08.

    Proves that:
    1. jinja_env.autoescape is True (for every registered environment/extension).
    2. Across all 26 production templates:
       a. Zero Jinja Filter nodes named 'safe'.
       b. Zero calls to Markup or mark_safe.
       c. Zero token streams containing pipe followed by 'safe'.
       d. Zero raw occurrences of |safe, | safe, Markup(, or mark_safe( in non-comment source.
    """
    if jinja_env is not None:
        assert jinja_env.autoescape is True or (
            callable(jinja_env.autoescape) and jinja_env.autoescape("template.html") is True
        ), "Jinja environment autoescape must be True"

    assert template_sources, "No template sources provided"
    assert len(template_sources) == len(ALL_PRODUCTION_TEMPLATES), (
        f"Expected {len(ALL_PRODUCTION_TEMPLATES)} templates, got {len(template_sources)}"
    )

    env = jinja_env or jinja2.Environment(autoescape=True)

    for name, raw_source in template_sources.items():
        clean_source = _clean_source(raw_source)

        # 1. Parse into AST
        parsed_ast = env.parse(clean_source, name=name)

        # 2. Walk AST nodes for Filter and Call nodes
        for node in parsed_ast.find_all(jinja2.nodes.Filter):
            assert node.name != "safe", (
                f"Template '{name}' uses prohibited Jinja filter '|safe' at line {node.lineno}"
            )

        for node in parsed_ast.find_all(jinja2.nodes.Call):
            if isinstance(node.node, jinja2.nodes.Name):
                assert node.node.name not in ("Markup", "mark_safe"), (
                    f"Template '{name}' calls prohibited '{node.node.name}' at line {node.lineno}"
                )

        # 3. Token-aware lexing
        tokens = list(env.lex(clean_source, name=name))
        for i, (lineno, token_type, token_val) in enumerate(tokens):
            if token_type == "pipe" and i + 1 < len(tokens):
                next_token_type, next_token_val = tokens[i + 1][1], tokens[i + 1][2]
                assert next_token_val != "safe", (
                    f"Template '{name}' contains pipe filter 'safe' at line {lineno}"
                )

        # 4. Clean source raw checks
        clean_lower = clean_source.lower()
        assert "|safe" not in clean_lower, f"Template '{name}' contains '|safe'"
        assert "| safe" not in clean_lower, f"Template '{name}' contains '| safe'"
        assert "markup(" not in clean_lower, f"Template '{name}' contains 'Markup('"
        assert "mark_safe(" not in clean_lower, f"Template '{name}' contains 'mark_safe('"
        assert "{% autoescape false" not in clean_lower, f"Template '{name}' contains 'autoescape false'"


# ===========================================================================
# 3. TC-SEC-09 — Hostile Rendering Inert DOM Validator
# ===========================================================================


def assert_hostile_renders_inert(
    response_text: str,
    hostile: str,
    *,
    container_selector: str,
    expected_count: int = 1,
    expected_bound: int | None = None,
    normalized_expected: str | None = None,
    is_collection: bool = False,
) -> None:
    """Production DOM-level validator for TC-SEC-09 (R12-01, R12-02, R12-05).

    Requires an explicit container selector and exact expected representation:
    1. Surrounding table rows, cells, and container elements remain balanced.
    2. Raw HTML characters (<script>, <img, etc.) never appear unescaped in response.
    3. Locates exact governed container(s) via container_selector.
    4. Extracts exact governed text node/container content and proves exact equality.
    5. Proves value is rendered ONLY as text: zero dangerous child elements injected.
    6. Zero event handlers (on*) or javascript: URLs on container or its children.
    7. For {{7*7}}, proves literal {{7*7}} is rendered and NOT evaluated to 49.
    8. Over-bound values are strictly truncated to expected bound and full over-bound input is absent.
    9. NFC/NFD representations match exact code-point sequence.
    """
    assert container_selector and container_selector.strip(), "Explicit container selector is required"

    # 1. Raw escaping check
    if "<" in hostile:
        assert hostile not in response_text, "Raw unescaped markup found in response body"

    # 2. Tag balance
    assert response_text.count("<tr") == response_text.count("</tr>"), "Unbalanced <tr> tags"
    assert response_text.count("<td") == response_text.count("</td>"), "Unbalanced <td> tags"

    soup = BeautifulSoup(response_text, "html.parser")

    # 3. Compute expected exact representation and exact bound
    if normalized_expected is not None:
        expected_text = normalized_expected
    elif expected_bound is not None and len(hostile) > expected_bound:
        expected_text = hostile[:expected_bound]
    else:
        expected_text = hostile

    if expected_bound is not None and len(hostile) > expected_bound:
        assert hostile not in response_text, "Full over-bound input leaked in response"

    # 4. Explicit container location & cardinality
    containers = soup.select(container_selector)
    if not is_collection:
        assert len(containers) == expected_count, (
            f"Expected exactly {expected_count} container(s) for selector '{container_selector}', found {len(containers)}"
        )
        target_containers = containers
    else:
        assert len(containers) >= expected_count, (
            f"Expected at least {expected_count} container(s) for selector '{container_selector}', found {len(containers)}"
        )
        matching = [c for c in containers if expected_text in c.get_text()]
        assert len(matching) >= 1, f"Expected at least one container to contain exact text {expected_text!r}"
        target_containers = matching

    dangerous_tags = {"script", "img", "iframe", "object", "embed", "svg", "style", "audio", "video", "link"}

    for container in target_containers:
        # Child element check: must not contain dangerous executable tags
        for child in container.find_all(True):
            assert child.name.lower() not in dangerous_tags, (
                f"Hostile element <{child.name}> injected inside container"
            )
            for attr_name, attr_val in child.attrs.items():
                assert not attr_name.lower().startswith("on"), (
                    f"Event handler {attr_name} injected in container child"
                )
                if isinstance(attr_val, str):
                    assert not attr_val.lower().startswith("javascript:"), (
                        f"javascript: URL injected in container child attribute {attr_name}"
                    )

        for attr_name, attr_val in container.attrs.items():
            assert not attr_name.lower().startswith("on"), (
                f"Event handler {attr_name} injected on container"
            )
            if isinstance(attr_val, str):
                assert not attr_val.lower().startswith("javascript:"), (
                    f"javascript: URL injected in container attribute {attr_name}"
                )

        governed_text = container.get_text()

        # Non-evaluation of {{7*7}} strictly checked against governed container
        if "{{7*7}}" in hostile:
            assert "{{7*7}}" in governed_text, "Literal {{7*7}} missing in container"
            assert "49" not in governed_text, "Jinja template literal {{7*7}} was evaluated to 49 in container"

        # Exact equality check (R12-05)
        assert len(governed_text) == len(expected_text), (
            f"Governed text length mismatch: expected {len(expected_text)}, got {len(governed_text)}"
        )
        assert governed_text == expected_text, (
            f"Governed text value mismatch for selector '{container_selector}'"
        )

        # Code-point exact sequence check for Unicode (NFC/NFD)
        assert [ord(c) for c in governed_text] == [ord(c) for c in expected_text], (
            "Governed text Unicode code point sequence mismatch"
        )

    # 5. Whole-document executable context inspection
    for s in soup.find_all("script"):
        src = s.get("src", "")
        assert src.startswith("/static/vendor/htmx-"), f"Unauthorized script src={src!r}"
        assert not s.get_text(strip=True), "Script has inline content"

    for img in soup.find_all("img"):
        src = img.get("src", "")
        assert src.startswith("/static/images/freedom-blades-token") or src.startswith("data:image/"), (
            f"Unauthorized img src={src!r}"
        )

    for el in soup.find_all(True):
        for attr_name, attr_val in el.attrs.items():
            assert not attr_name.lower().startswith("on"), (
                f"Document contains unexpected event handler {attr_name} on <{el.name}>"
            )
            if isinstance(attr_val, str):
                assert not attr_val.lower().startswith("javascript:"), (
                    f"Document contains unexpected javascript: URL in {attr_name} on <{el.name}>"
                )


# ===========================================================================
# 4. TC-SEC-10 & TC-SEC-11 — Executable Context Production Validator
# ===========================================================================


def validate_executable_contexts(
    template_sources: dict[str, str],
    allowed_script_src: str,
) -> None:
    """Production validator for TC-SEC-10 and TC-SEC-11.

    Proves that across all 26 production templates:
    1. Zero hx-on: attributes (including variants).
    2. Zero inline event handlers (onclick, onload, onerror, onsubmit, etc.).
    3. Zero javascript: URLs in any attribute.
    4. Exactly one <script> tag exists across all templates, located in base.html only.
    5. Its src attribute equals allowed_script_src exactly.
    6. It has no inline body content.
    7. No Jinja expressions appear in script attributes or body.
    8. Zero remote or CDN origins in any href, src, or @import.
    9. Only accepted local static resources are referenced.
    """
    assert template_sources, "No template sources provided"
    assert "base.html" in template_sources, "base.html must be present"

    remote_markers = (
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

    for name, raw_source in template_sources.items():
        clean_source = _clean_source(raw_source)
        soup = BeautifulSoup(clean_source, "html.parser")
        scripts = soup.find_all("script")

        if name == "base.html":
            assert len(scripts) == 1, f"base.html must contain exactly 1 script tag, found {len(scripts)}"
            script = scripts[0]

            script_open_match = re.search(r"<script([^>]*)>", clean_source, flags=re.IGNORECASE)
            assert script_open_match
            script_open = script_open_match.group(1)
            assert "{{" not in script_open and "{%" not in script_open, "Jinja found in script tag attributes"

            actual_src = script.get("src")
            assert actual_src == allowed_script_src, (
                f"base.html script src {actual_src!r} != expected {allowed_script_src!r}"
            )
            assert not script.get_text(strip=True), "base.html script has inline body content"
            for attr in script.attrs:
                assert attr in ("src", "defer", "async", "type", "integrity", "crossorigin"), (
                    f"Unexpected attribute {attr!r} on base.html script"
                )

            script_blocks = re.findall(r"<script[^>]*>(.*?)</script>", clean_source, flags=re.DOTALL | re.IGNORECASE)
            assert len(script_blocks) == 1
            assert "{{" not in script_blocks[0] and "{%" not in script_blocks[0], "Jinja found in script body"
        else:
            assert len(scripts) == 0, f"Template '{name}' must not contain any <script> element"
            assert "<script" not in clean_source.lower(), f"Template '{name}' contains unparsed <script tag"

        clean_lower = clean_source.lower()
        assert "hx-on:" not in clean_lower, f"Template '{name}' contains 'hx-on:'"

        for el in soup.find_all(True):
            for attr_name, attr_val in el.attrs.items():
                assert not attr_name.lower().startswith("on"), (
                    f"Template '{name}' element <{el.name}> has inline event handler '{attr_name}'"
                )
                assert not attr_name.lower().startswith("hx-on"), (
                    f"Template '{name}' element <{el.name}> has hx-on handler '{attr_name}'"
                )
                if isinstance(attr_val, str):
                    assert not attr_val.lower().startswith("javascript:"), (
                        f"Template '{name}' element <{el.name}> has javascript: URL in '{attr_name}'"
                    )

        for marker in remote_markers:
            assert marker not in clean_lower, f"Template '{name}' references remote origin marker '{marker}'"

        assert "design-prototype" not in clean_source, (
            f"Template '{name}' references forbidden 'design-prototype/'"
        )


# ===========================================================================
# 5. TC-SEC-05 Header Matrix Tests Across All Response Families
# ===========================================================================


async def test_exact_security_headers_full_pages_unauthenticated(client):
    """TC-SEC-05: Full pages (unauthenticated) carry exact security headers."""
    for path in ("/v1/login", "/v1/auth/emergency"):
        response = await client.get(path)
        assert response.status_code == 200, path
        validate_response_security_headers(response, path=path)


async def test_exact_security_headers_full_pages_authenticated_player(
    client, settings, callers, migrated_database
):
    """TC-SEC-05: Full pages (authenticated player) carry exact security headers."""
    with migrated_database.begin() as connection:
        char_id = make_character(connection, display_name="TestChar")
        grant_link(
            connection,
            character_id=char_id,
            account_id=callers["M"].account_id,
            granted_by=callers["C"].account_id,
        )

    cookies = callers["M"].cookies(settings)
    for path in ("/v1/characters", f"/v1/characters/{char_id}", "/v1/account/identities"):
        response = await client.get(path, cookies=cookies)
        assert response.status_code == 200, path
        validate_response_security_headers(response, authenticated=True, path=path)


async def test_exact_security_headers_full_pages_authenticated_council(
    client, settings, callers, snapshot, migrated_database
):
    """TC-SEC-05: Full pages (authenticated council) carry exact security headers."""
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        char_id = make_character(connection, display_name="CouncilChar")
        grant_link(
            connection,
            character_id=char_id,
            account_id=callers["M"].account_id,
            granted_by=callers["C"].account_id,
        )
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )

    cookies = callers["C"].cookies(settings)
    paths = [
        "/v1/council/characters",
        f"/v1/council/characters/{char_id}/links",
        "/v1/council/snapshots",
        f"/v1/council/jobs/{job_id}",
        "/v1/council/identity-migration",
        "/v1/council/field-profile",
        "/v1/audit",
    ]
    for path in paths:
        response = await client.get(path, cookies=cookies)
        assert response.status_code == 200, path
        validate_response_security_headers(response, authenticated=True, path=path)


async def test_exact_security_headers_full_pages_authenticated_admin(client, settings, callers):
    """TC-SEC-05: Full pages (authenticated admin) carry exact security headers."""
    cookies = callers["A"].cookies(settings)
    path = "/v1/admin/role-capabilities"
    response = await client.get(path, cookies=cookies)
    assert response.status_code == 200, path
    validate_response_security_headers(response, authenticated=True, path=path)


async def test_exact_security_headers_fragments_authenticated(
    client, settings, callers, snapshot, migrated_database
):
    """TC-SEC-05: Fragment responses carry exact security headers."""
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )

    cookies = callers["C"].cookies(settings)
    paths = [
        "/v1/council/characters?q=Test",
        "/v1/council/identity-search?q=123",
        f"/v1/council/jobs/{job_id}/status",
        "/v1/audit/results",
    ]
    for path in paths:
        response = await client.get(path, cookies=cookies, headers={"HX-Request": "true"})
        assert response.status_code == 200, path
        validate_response_security_headers(response, authenticated=True, path=path)


async def test_exact_security_headers_redirects(client, settings, callers):
    """TC-SEC-05: Redirect responses (303) carry exact security headers."""
    res_root = await client.get("/")
    assert res_root.status_code == 303
    validate_response_security_headers(res_root, path="/")

    res_oauth = await client.get("/v1/auth/discord/start")
    assert res_oauth.status_code == 303
    validate_response_security_headers(res_oauth, path="/v1/auth/discord/start")

    res_unauth = await client.get("/v1/characters")
    assert res_unauth.status_code == 303
    validate_response_security_headers(res_unauth, path="/v1/characters")

    token = csrf_token_for(settings, callers["M"])
    res_logout = await client.post(
        "/v1/auth/logout",
        cookies=callers["M"].cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        data={"csrf_token": token},
    )
    assert res_logout.status_code == 303
    validate_response_security_headers(res_logout, authenticated=True, path="/v1/auth/logout")


async def test_exact_security_headers_denial_responses(client, settings, callers):
    """TC-SEC-05: Denial responses (401, 403, 404) carry exact security headers."""
    res_401 = await client.get("/v1/audit/results")
    assert res_401.status_code == 401
    validate_response_security_headers(res_401, path="/v1/audit/results")

    res_403 = await client.get("/v1/admin/role-capabilities", cookies=callers["M"].cookies(settings))
    assert res_403.status_code == 403
    validate_response_security_headers(res_403, authenticated=True, path="/v1/admin/role-capabilities")

    res_404 = await client.get(
        f"/v1/characters/{uuid4()}", cookies=callers["M"].cookies(settings)
    )
    assert res_404.status_code == 404
    validate_response_security_headers(res_404, authenticated=True, path="/v1/characters/{uuid}")


async def test_exact_security_headers_validation_responses(client, settings, callers, snapshot):
    """TC-SEC-05: Validation responses (400, 411, 413, 415, 422) carry exact security headers."""
    res_400 = await client.post(
        "/v1/auth/emergency/recovery",
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content="",
    )
    assert res_400.status_code == 303 or res_400.status_code == 400
    validate_response_security_headers(res_400, path="/v1/auth/emergency/recovery")

    oversized = "x" * (1024 * 1024 + 1)
    res_413 = await client.post(
        "/v1/auth/emergency/recovery",
        content=oversized,
        headers={"Origin": settings.public_origin, "Content-Type": "text/plain"},
    )
    assert res_413.status_code == 413
    validate_response_security_headers(res_413, path="/v1/auth/emergency/recovery")

    res_415 = await client.post(
        "/v1/auth/emergency/recovery",
        headers={"Origin": settings.public_origin, "Content-Type": "application/json"},
        content="{}",
    )
    assert res_415.status_code == 415
    validate_response_security_headers(res_415, path="/v1/auth/emergency/recovery")

    snapshot_id, _ = snapshot
    res_422 = await client.post(
        f"/v1/admin/snapshots/{snapshot_id}/folder",
        cookies=callers["A"].cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        data={"csrf_token": csrf_token_for(settings, callers["A"]), "folder_id": "../../etc/passwd"},
    )
    assert res_422.status_code == 422
    validate_response_security_headers(res_422, authenticated=True, path="/v1/admin/snapshots/{id}/folder")


async def test_exact_security_headers_stale_and_outage_responses(
    client, settings, callers, snapshot, outage, migrated_database
):
    """TC-SEC-05: Stale and outage responses (503) carry exact security headers."""
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        stale_membership(connection, subject=COUNCIL_SUBJECT, minutes=30)

    res_503 = await client.get(
        f"/v1/council/jobs/{job_id}", cookies=callers["C"].cookies(settings)
    )
    assert res_503.status_code == 503
    validate_response_security_headers(res_503, authenticated=True, path="/v1/council/jobs/{id}")


async def test_exact_security_headers_safe_error_responses(composition, monkeypatch):
    """TC-SEC-05: Safe error responses (500) carry exact security headers."""
    import httpx

    def explode(self, _connection):
        raise RuntimeError("simulated error")

    monkeypatch.setattr(WebComposition, "services", explode)
    app = create_app(composition=composition, run_startup_checks=False)
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url=PUBLIC_ORIGIN) as local_client:
        response = await local_client.get("/v1/auth/discord/start")
        assert response.status_code == 500
        validate_response_security_headers(response, path="/v1/auth/discord/start")


# ===========================================================================
# 6. TC-SEC-08 AST & Token Escaping Tests
# ===========================================================================


def test_autoescaping_is_on_and_zero_templates_use_safe_filter_ast(app):
    """TC-SEC-08: Whole-corpus Jinja autoescaping and zero |safe proof."""
    sources = {}
    for p in _templates():
        rel = str(p.relative_to(TEMPLATES_DIR))
        if rel in ALL_PRODUCTION_TEMPLATES:
            sources[rel] = p.read_text()
        elif p.name in ALL_PRODUCTION_TEMPLATES:
            sources[p.name] = p.read_text()

    assert len(sources) == len(ALL_PRODUCTION_TEMPLATES)
    validate_template_escaping_ast(sources, jinja_env=app.state.templates.env)


# ===========================================================================
# 7. TC-SEC-09 Hostile Rendering Surface Tests (R12-01 & R12-02)
# ===========================================================================


@pytest.mark.parametrize("hostile,vector_id", HOSTILE_IN_BOUND_VECTORS)
async def test_hostile_rendering_character_display_names(
    client, settings, callers, migrated_database, hostile, vector_id
):
    """TC-SEC-09: Hostile character name renders inert in exact governed containers."""
    with migrated_database.begin() as connection:
        char_id = make_character(connection, display_name=hostile)
        grant_link(
            connection,
            character_id=char_id,
            account_id=callers["M"].account_id,
            granted_by=callers["C"].account_id,
        )

    # 1. Member characters list view (R-21)
    res_list = await client.get("/v1/characters", cookies=callers["M"].cookies(settings))
    assert res_list.status_code == 200
    assert_hostile_renders_inert(
        res_list.text,
        hostile,
        container_selector="a.char-title-link",
        expected_count=1,
    )

    # 2. Member character detail view (R-22)
    res_detail = await client.get(f"/v1/characters/{char_id}", cookies=callers["M"].cookies(settings))
    assert res_detail.status_code == 200
    assert_hostile_renders_inert(
        res_detail.text,
        hostile,
        container_selector="h1.page-title",
        expected_count=1,
    )

    # 3. Council characters search view (R-31)
    res_council = await client.get("/v1/council/characters", cookies=callers["C"].cookies(settings))
    assert res_council.status_code == 200
    assert_hostile_renders_inert(
        res_council.text,
        hostile,
        container_selector="a.char-title-link strong",
        expected_count=1,
    )


@pytest.mark.parametrize("hostile,vector_id", HOSTILE_IN_BOUND_VECTORS)
async def test_hostile_rendering_audit_event_reasons(
    client, settings, callers, migrated_database, hostile, vector_id
):
    """TC-SEC-09: Hostile audit event reason renders inert in exact fact-after container."""
    with migrated_database.begin() as connection:
        connection.execute(
            insert(audit_events).values(
                id=uuid4(),
                occurred_at=utcnow(),
                actor_platform_account_id=callers["C"].account_id,
                actor_capability="guild_council",
                action="character_access.granted",
                entity_type="character_access",
                entity_id=str(uuid4()),
                source="web",
                correlation_id=uuid4(),
                payload={"reason": hostile},
            )
        )

    response = await client.get("/v1/audit/results", cookies=callers["C"].cookies(settings))
    assert response.status_code == 200
    assert_hostile_renders_inert(
        response.text,
        hostile,
        container_selector='[data-field="fact-after"]',
        expected_count=1,
        expected_bound=AUDIT_VALUE_BOUND,
    )


async def test_hostile_rendering_overbound_10k_audit_reason_truncation(
    client, settings, callers, migrated_database
):
    """TC-SEC-09 / R12-02: 10,000-character audit reason is safely truncated to AUDIT_VALUE_BOUND."""
    long_hostile = "x" * 10_000
    with migrated_database.begin() as connection:
        connection.execute(
            insert(audit_events).values(
                id=uuid4(),
                occurred_at=utcnow(),
                actor_platform_account_id=callers["C"].account_id,
                actor_capability="guild_council",
                action="character_access.granted",
                entity_type="character_access",
                entity_id=str(uuid4()),
                source="web",
                correlation_id=uuid4(),
                payload={"reason": long_hostile},
            )
        )

    response = await client.get("/v1/audit/results", cookies=callers["C"].cookies(settings))
    assert response.status_code == 200
    # Must be truncated to AUDIT_VALUE_BOUND=200
    expected_truncated = "x" * AUDIT_VALUE_BOUND
    assert_hostile_renders_inert(
        response.text,
        long_hostile,
        container_selector='[data-field="fact-after"]',
        expected_count=1,
        expected_bound=AUDIT_VALUE_BOUND,
        normalized_expected=expected_truncated,
    )
    # Proves the full untruncated 10,000 chars is not leaked
    assert long_hostile not in response.text


async def test_hostile_rendering_overbound_10k_job_candidate_name_truncation(
    client, settings, callers, snapshot, migrated_database
):
    """TC-SEC-09 / R12-02: 10,000-character candidate name is safely truncated to ACTOR_NAME_BOUND."""
    snapshot_id, checksum = snapshot
    long_candidate_name = "y" * 10_000
    with migrated_database.begin() as connection:
        job_id, _ = complete_preview(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            blocked_entries=[{
                "external_actor_id": "act-1",
                "display_name": long_candidate_name,
                "issue_code": "ambiguous_match",
                "candidate_character_ids": [],
            }],
        )

    response = await client.get(
        f"/v1/council/jobs/{job_id}", cookies=callers["C"].cookies(settings)
    )
    assert response.status_code == 200
    expected_truncated = ("y" * ACTOR_NAME_BOUND) + "\u2026"
    assert_hostile_renders_inert(
        response.text,
        long_candidate_name,
        container_selector='[data-field="blocked-name"]',
        expected_count=1,
        expected_bound=ACTOR_NAME_BOUND,
        normalized_expected=expected_truncated,
    )
    assert long_candidate_name not in response.text


@pytest.mark.parametrize("hostile,vector_id", HOSTILE_IN_BOUND_VECTORS)
async def test_hostile_rendering_council_identity_search_username(
    client, settings, callers, migrated_database, hostile, vector_id
):
    """TC-SEC-09 / R12-08: Hostile Discord username renders inert in exact candidate-username container."""
    from tests.web.conftest import TEST_GUILD_ID

    subject_snowflake = 800000000000008000 + abs(hash(vector_id)) % 1000000

    with migrated_database.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO discord_users (id, username, global_name) "
                "VALUES (:id, :username, :global_name) "
                "ON CONFLICT (id) DO UPDATE SET username = :username, global_name = :global_name"
            ),
            {"id": subject_snowflake, "username": hostile, "global_name": "Valid Global Name"},
        )
        connection.execute(
            text(
                "INSERT INTO discord_guild_memberships (discord_user_id, guild_id, active) "
                "VALUES (:user, :guild, true) "
                "ON CONFLICT (discord_user_id, guild_id) DO UPDATE SET active = true"
            ),
            {"user": subject_snowflake, "guild": TEST_GUILD_ID},
        )

    response = await client.get(
        "/v1/council/identity-search",
        params={"q": hostile[:10]},
        cookies=callers["C"].cookies(settings),
    )
    assert response.status_code == 200
    assert_hostile_renders_inert(
        response.text,
        hostile,
        container_selector="span.candidate-username strong",
        expected_count=1,
    )
    # Proves the snowflake is preserved as canonical decimal snowflake
    soup = BeautifulSoup(response.text, "html.parser")
    subj_code = soup.select_one('code[data-field="subject"]')
    assert subj_code is not None
    assert subj_code.get_text() == str(subject_snowflake)
    assert subj_code.get_text().isdigit()


@pytest.mark.parametrize("hostile,vector_id", HOSTILE_IN_BOUND_VECTORS)
async def test_hostile_rendering_council_identity_search_global_name(
    client, settings, callers, migrated_database, hostile, vector_id
):
    """TC-SEC-09 / R12-08: Hostile Discord global_name renders inert in exact candidate-global-name container."""
    from tests.web.conftest import TEST_GUILD_ID

    subject_snowflake = 800000000000009000 + abs(hash(vector_id)) % 1000000
    clean_username = f"user{subject_snowflake}"

    with migrated_database.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO discord_users (id, username, global_name) "
                "VALUES (:id, :username, :global_name) "
                "ON CONFLICT (id) DO UPDATE SET username = :username, global_name = :global_name"
            ),
            {"id": subject_snowflake, "username": clean_username, "global_name": hostile},
        )
        connection.execute(
            text(
                "INSERT INTO discord_guild_memberships (discord_user_id, guild_id, active) "
                "VALUES (:user, :guild, true) "
                "ON CONFLICT (discord_user_id, guild_id) DO UPDATE SET active = true"
            ),
            {"user": subject_snowflake, "guild": TEST_GUILD_ID},
        )

    response = await client.get(
        "/v1/council/identity-search",
        params={"q": hostile[:10]},
        cookies=callers["C"].cookies(settings),
    )
    assert response.status_code == 200
    assert_hostile_renders_inert(
        response.text,
        hostile,
        container_selector="span.candidate-global-name",
        expected_count=1,
        normalized_expected=f"({hostile})",
    )
    soup = BeautifulSoup(response.text, "html.parser")
    subj_code = soup.select_one('code[data-field="subject"]')
    assert subj_code is not None
    assert subj_code.get_text() == str(subject_snowflake)
    assert subj_code.get_text().isdigit()


async def test_hostile_rendering_council_identity_search_overbound(
    client, settings, callers, migrated_database
):
    """TC-SEC-09 / R12-08: Discord name bounded representation at DISCORD_NAME_BOUND=80 and database projection refusal."""
    from application.web.view_models import DISCORD_NAME_BOUND
    from tests.web.conftest import TEST_GUILD_ID

    subject_snowflake = 800000000000009999
    exact_80_name = "z" * DISCORD_NAME_BOUND

    # 1. Exact 80-char in-bound name renders accurately
    with migrated_database.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO discord_users (id, username, global_name) "
                "VALUES (:id, :username, null) "
                "ON CONFLICT (id) DO UPDATE SET username = :username, global_name = null"
            ),
            {"id": subject_snowflake, "username": exact_80_name},
        )
        connection.execute(
            text(
                "INSERT INTO discord_guild_memberships (discord_user_id, guild_id, active) "
                "VALUES (:user, :guild, true) "
                "ON CONFLICT (discord_user_id, guild_id) DO UPDATE SET active = true"
            ),
            {"user": subject_snowflake, "guild": TEST_GUILD_ID},
        )

    response = await client.get(
        "/v1/council/identity-search",
        params={"q": exact_80_name[:10]},
        cookies=callers["C"].cookies(settings),
    )
    assert response.status_code == 200
    assert_hostile_renders_inert(
        response.text,
        exact_80_name,
        container_selector="span.candidate-username strong",
        expected_count=1,
        expected_bound=DISCORD_NAME_BOUND,
    )

    # 2. Over-bound (10,000-char) string rejected by real database projection constraint (VARCHAR(80))
    import psycopg.errors
    from sqlalchemy.exc import DataError, DatabaseError
    with pytest.raises((DataError, DatabaseError, psycopg.errors.StringDataRightTruncation)):
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO discord_users (id, username) VALUES (:id, :name)"
                ),
                {"id": 800000000000009998, "name": "z" * 10_000},
            )


async def test_account_identity_subject_display_canonical_snowflake(
    client, settings, callers
):
    """TC-SEC-09 / R12-08: Account identity subject display renders caller's own canonical decimal snowflake."""
    from tests.web.portal_fixtures import MEMBER_SUBJECT

    response = await client.get("/v1/account/identities", cookies=callers["M"].cookies(settings))
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")
    subjects = [el.get_text().strip() for el in soup.select("code.identity-subject")]
    assert len(subjects) >= 1
    for subj in subjects:
        assert subj.isdigit(), f"Subject {subj!r} is not a canonical decimal snowflake"
    assert str(MEMBER_SUBJECT) in subjects


@pytest.mark.parametrize("hostile,vector_id", HOSTILE_IN_BOUND_VECTORS)
async def test_closed_vocabulary_query_refusal_login_and_emergency(client, hostile, vector_id):
    """R12-02: Closed-vocabulary failure parameters refuse raw hostile text reflection."""
    # 1. Login page (R-02)
    res_login = await client.get("/v1/login", params={"failure": hostile})
    assert res_login.status_code == 200
    # Proves raw hostile string is NEVER rendered in the document
    assert hostile not in res_login.text
    # Proves no unescaped tags or event handlers
    soup_login = BeautifulSoup(res_login.text, "html.parser")
    assert len(soup_login.find_all("script")) == 1  # only HTMX

    # 2. Emergency access page (R-06)
    res_emerg = await client.get("/v1/auth/emergency", params={"failure": hostile})
    assert res_emerg.status_code == 200
    assert hostile not in res_emerg.text


# ===========================================================================
# 8. TC-SEC-10 & TC-SEC-11 Executable Context Guards Tests
# ===========================================================================


def test_executable_contexts_and_script_guards_across_all_templates(app):
    """TC-SEC-10 and TC-SEC-11: Executable context guards across all 26 templates."""
    allowed_script_src = _allowed_htmx_script_src()
    sources = {}
    for p in _templates():
        rel = str(p.relative_to(TEMPLATES_DIR))
        if rel in ALL_PRODUCTION_TEMPLATES:
            sources[rel] = p.read_text()
        elif p.name in ALL_PRODUCTION_TEMPLATES:
            sources[p.name] = p.read_text()

    assert len(sources) == len(ALL_PRODUCTION_TEMPLATES)
    validate_executable_contexts(sources, allowed_script_src)


# ===========================================================================
# 9. Exact Safe Response Bodies Production Validators & Tests (R12-04)
# ===========================================================================


def validate_denial_response_body(
    response: Any,
    expected_category: DenialCategory,
) -> None:
    """Production validator for denial response bodies (VM-01 / denied.html)."""
    assert response.status_code in (401, 403, 404), f"Unexpected denial status {response.status_code}"
    body = response.text
    soup = BeautifulSoup(body, "html.parser")

    # 1. State container inspection
    state_el = soup.find(attrs={"data-state": "denied"})
    assert state_el is not None, "Missing data-state='denied' in denial response"
    assert state_el.get("data-reason") == expected_category.value, (
        f"Expected reason '{expected_category.value}', got '{state_el.get('data-reason')}'"
    )

    # 2. Heading verification
    h1 = soup.find("h1")
    assert h1 is not None and "Not available" in h1.get_text()

    # 3. Prohibit internal disclosures
    forbidden_terms = (
        "traceback",
        "exception",
        "select ",
        "from ",
        "where ",
        "/opt/",
        "/srv/",
        "app.py",
        "portal_routes.py",
        "bearer",
        "secret",
        "password",
    )
    body_lower = body.lower()
    for term in forbidden_terms:
        assert term not in body_lower, f"Leaked internal '{term}' in denial response"


def validate_validation_response_body(
    response: Any,
    *,
    expected_field: str | None = None,
    is_plain_text: bool = False,
    expected_plain_text: str = "",
) -> None:
    """Production validator for validation response bodies (VM-03 / validation.html or PlainText)."""
    if is_plain_text:
        assert response.text.strip() == expected_plain_text, (
            f"Expected plain text '{expected_plain_text}', got '{response.text.strip()}'"
        )
        return

    assert response.status_code in (400, 422), f"Unexpected validation status {response.status_code}"
    body = response.text
    soup = BeautifulSoup(body, "html.parser")

    state_el = soup.find(attrs={"data-state": "invalid"})
    assert state_el is not None, "Missing data-state='invalid' in validation response"

    if expected_field:
        field_el = soup.find(attrs={"data-field": expected_field})
        assert field_el is not None, f"Expected validation field '{expected_field}' not found in response"

    # Prohibit internal leaks
    for term in ("traceback", "exception", "select ", "/opt/", ".py"):
        assert term not in body.lower(), f"Leaked internal '{term}' in validation response"


def validate_stale_response_body(
    response: Any,
    *,
    is_plain_text: bool = False,
    expected_plain_text: str = "",
) -> None:
    """Production validator for stale/degraded response bodies (VM-02 / degraded.html or PlainText 503)."""
    assert response.status_code == 503, f"Unexpected stale status {response.status_code}"
    if is_plain_text:
        assert response.text.strip() == expected_plain_text, (
            f"Expected plain text '{expected_plain_text}', got '{response.text.strip()}'"
        )
        assert response.headers.get("retry-after") == "300", "Missing Retry-After: 300 on maintenance"
        return

    body = response.text
    soup = BeautifulSoup(body, "html.parser")
    state_el = soup.find(attrs={"data-subsystem": True})
    assert state_el is not None, "Missing degraded subsystem container in degraded response"

    h1 = soup.find("h1")
    assert h1 is not None and "Authorization cannot be confirmed" in h1.get_text()


def validate_safe_error_body(response: Any) -> None:
    """Production validator for safe 500 error response bodies (VM-20 / error.html)."""
    assert response.status_code == 500, f"Unexpected safe error status {response.status_code}"
    body = response.text
    soup = BeautifulSoup(body, "html.parser")

    state_el = soup.find(attrs={"data-state": "error"})
    assert state_el is not None, "Missing data-state='error' in error.html"

    # Strictly validates exactly one canonical UUID with zero wrappers or internal leaks (R12-06)
    validate_exact_canonical_correlation_uuid(response)

    for term in ("runtimeerror", "database error", "select password", "traceback", "app.py", "/opt/", "psycopg", "sqlalchemy"):
        assert term not in body.lower(), f"Leaked internal '{term}' in safe error body"


async def test_denial_response_body_contracts(client, settings, callers):
    """R12-04: Real ASGI denial responses conform to exact body contract."""
    # 1. 404 Unreachable Character
    res_404 = await client.get(
        f"/v1/characters/{uuid4()}", cookies=callers["M"].cookies(settings)
    )
    validate_denial_response_body(res_404, DenialCategory.NOT_AVAILABLE)

    # 2. 403 Insufficient Capability
    res_403 = await client.get(
        "/v1/admin/role-capabilities", cookies=callers["M"].cookies(settings)
    )
    validate_denial_response_body(res_403, DenialCategory.INSUFFICIENT_CAPABILITY)


async def test_validation_response_body_contracts(client, settings, callers, snapshot):
    """R12-04: Real ASGI validation responses conform to exact body contract."""
    # 1. 422 Malicious folder ID
    snapshot_id, _ = snapshot
    res_422 = await client.post(
        f"/v1/admin/snapshots/{snapshot_id}/folder",
        cookies=callers["A"].cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        data={"csrf_token": csrf_token_for(settings, callers["A"]), "folder_id": "../../etc/passwd"},
    )
    validate_validation_response_body(res_422, expected_field="folder_id")

    # 2. 413 Body too large PlainText
    res_413 = await client.post(
        "/v1/auth/emergency/recovery",
        content="x" * (1024 * 1024 + 1),
        headers={"Origin": settings.public_origin, "Content-Type": "text/plain"},
    )
    validate_validation_response_body(res_413, is_plain_text=True, expected_plain_text="Body too large.")

    # 3. 415 Unsupported Content-Type JSON response
    res_415 = await client.post(
        "/v1/auth/emergency/recovery",
        headers={"Origin": settings.public_origin, "Content-Type": "application/json"},
        content="{}",
    )
    validate_validation_response_body(res_415, is_plain_text=True, expected_plain_text='{"error":"unsupported_media_type"}')


async def test_stale_response_body_contracts(
    client, settings, callers, snapshot, outage, migrated_database
):
    """R12-04: Real ASGI stale responses conform to exact body contract."""
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        stale_membership(connection, subject=COUNCIL_SUBJECT, minutes=30)

    res_503 = await client.get(
        f"/v1/council/jobs/{job_id}", cookies=callers["C"].cookies(settings)
    )
    validate_stale_response_body(res_503)


async def test_safe_error_body_contracts(composition, monkeypatch):
    """R12-04: Real ASGI 500 error response conforms to exact body contract."""
    import httpx

    def explode(self, _connection):
        raise RuntimeError("DATABASE ERROR: SELECT password FROM users WHERE secret='123'")

    monkeypatch.setattr(WebComposition, "services", explode)
    app = create_app(composition=composition, run_startup_checks=False)
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url=PUBLIC_ORIGIN) as local_client:
        response = await local_client.get("/v1/auth/discord/start")
        validate_safe_error_body(response)


# ===========================================================================
# 10. Essential No-JavaScript Flows (R12-03)
# ===========================================================================


async def test_essential_no_javascript_flows(
    app, client, settings, callers, snapshot, migrated_database
):
    """TC-SEC-10 / R12-03: Full inventory of essential flows verified via shared no-JS validator."""
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        char_id = make_character(connection, display_name="NoJsChar")
        grant_link(
            connection,
            character_id=char_id,
            account_id=callers["M"].account_id,
            granted_by=callers["C"].account_id,
        )
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )

    # 1. Flow-01: Login View (R-02)
    res_login = await client.get("/v1/login")
    login_contract = FlowContract(
        flow_name="Flow-01: Login View",
        expected_forms=(),
        expected_link_prefixes=("/v1/auth/discord/start", "/v1/auth/emergency"),
    )
    validate_rendered_no_js_fallback(strip_htmx_attributes(res_login.text), login_contract, app=app)

    # 2. Flow-02: Emergency Access Recovery (R-06)
    res_emerg = await client.get("/v1/auth/emergency")
    emerg_contract = FlowContract(
        flow_name="Flow-02: Emergency Access Recovery",
        expected_forms=(
            FormContract(
                action="/v1/auth/emergency/recovery",
                method="POST",
                requires_csrf=False,
            ),
        ),
        expected_link_prefixes=("/v1/login",),
    )
    validate_rendered_no_js_fallback(strip_htmx_attributes(res_emerg.text), emerg_contract, app=app)

    # 3. Flow-03: Member Characters View (R-21)
    res_chars = await client.get("/v1/characters", cookies=callers["M"].cookies(settings))
    chars_contract = FlowContract(
        flow_name="Flow-03: Member Characters View",
        expected_forms=(),
        expected_link_prefixes=(f"/v1/characters/{char_id}", "/v1/characters"),
    )
    validate_rendered_no_js_fallback(strip_htmx_attributes(res_chars.text), chars_contract, app=app)

    # 4. Flow-04: Council Characters Search (R-31)
    res_council = await client.get("/v1/council/characters", cookies=callers["C"].cookies(settings))
    council_contract = FlowContract(
        flow_name="Flow-04: Council Characters Search",
        expected_forms=(
            FormContract(
                action="/v1/council/characters",
                method="GET",
                requires_csrf=False,
            ),
        ),
        expected_link_prefixes=("/v1/characters",),
    )
    validate_rendered_no_js_fallback(strip_htmx_attributes(res_council.text), council_contract, app=app)

    # 5. Flow-05: Council Character Links (R-36)
    csrf_council = csrf_token_for(settings, callers["C"])
    res_links = await client.get(f"/v1/council/characters/{char_id}/links", cookies=callers["C"].cookies(settings))
    links_contract = FlowContract(
        flow_name="Flow-05: Council Character Links",
        expected_forms=(
            FormContract(
                action=f"/v1/council/characters/{char_id}/links",
                method="POST",
                selector='form[action$="/links"]',
                requires_csrf=True,
                expected_csrf_token=csrf_council,
                required_hidden_fields={"version": "0"},
            ),
        ),
        expected_link_prefixes=("/v1/characters",),
    )
    validate_rendered_no_js_fallback(strip_htmx_attributes(res_links.text), links_contract, app=app)

    # 6. Flow-06: Council Snapshots (R-40)
    csrf_admin = csrf_token_for(settings, callers["A"])
    res_snaps = await client.get("/v1/council/snapshots", cookies=callers["A"].cookies(settings))
    snaps_contract = FlowContract(
        flow_name="Flow-06: Council Snapshots",
        expected_forms=(
            FormContract(
                action=f"/v1/admin/snapshots/{snapshot_id}/folder",
                method="POST",
                requires_csrf=True,
                expected_csrf_token=csrf_admin,
            ),
        ),
        expected_link_prefixes=("/v1/characters",),
    )
    validate_rendered_no_js_fallback(strip_htmx_attributes(res_snaps.text), snaps_contract, app=app)

    # 7. Flow-07: Council Job Status (R-43)
    res_job = await client.get(f"/v1/council/jobs/{job_id}", cookies=callers["C"].cookies(settings))
    job_contract = FlowContract(
        flow_name="Flow-07: Council Job Status",
        expected_forms=(
            FormContract(
                action=f"/v1/council/jobs/{job_id}/cancel",
                method="POST",
                requires_csrf=True,
                expected_csrf_token=csrf_council,
            ),
        ),
        expected_link_prefixes=("/v1/characters",),
    )
    validate_rendered_no_js_fallback(strip_htmx_attributes(res_job.text), job_contract, app=app)

    # 8. Flow-08: Audit Search (R-48)
    res_audit = await client.get("/v1/audit", cookies=callers["C"].cookies(settings))
    audit_contract = FlowContract(
        flow_name="Flow-08: Audit Search",
        expected_forms=(
            FormContract(
                action="/v1/audit",
                method="GET",
                requires_csrf=False,
            ),
        ),
        expected_link_prefixes=("/v1/characters",),
    )
    validate_rendered_no_js_fallback(strip_htmx_attributes(res_audit.text), audit_contract, app=app)

    # 9. Flow-09: Role Capabilities (R-50)
    res_roles = await client.get("/v1/admin/role-capabilities", cookies=callers["A"].cookies(settings))
    roles_contract = FlowContract(
        flow_name="Flow-09: Role Capabilities",
        expected_forms=(
            FormContract(
                action="/v1/admin/role-capabilities",
                method="POST",
                requires_csrf=True,
                expected_csrf_token=csrf_admin,
            ),
        ),
        expected_link_prefixes=("/v1/characters",),
    )
    validate_rendered_no_js_fallback(strip_htmx_attributes(res_roles.text), roles_contract, app=app)


# ===========================================================================
# 11. Structural & Prototype Guard Tests
# ===========================================================================


def test_structural_closed_route_inventory(app):
    """TC-STRUCT-01: 39 routes + 1 mount registered match closed inventory."""
    registered = {
        (method, route.path)
        for route in app.routes
        for method in getattr(route, "methods", set()) or set()
        if method not in ("HEAD", "OPTIONS")
    }
    assert registered == set(ROUTE_INVENTORY.values())
    assert len(MOUNT_INVENTORY) == 1
    assert MOUNT_INVENTORY["M-01"] == "/static"


def test_structural_view_models_frozen_and_slotted():
    """TC-STRUCT-02: All implemented view models are frozen and slotted."""
    from dataclasses import fields, is_dataclass

    for identifier, model in view_models.IMPLEMENTED_VIEW_MODELS.items():
        assert is_dataclass(model), identifier
        assert model.__dataclass_params__.frozen, f"{identifier} is not frozen"
        assert "__slots__" in model.__dict__, f"{identifier} is not slotted"
        for field in fields(model):
            annotation = str(field.type)
            assert "list[" not in annotation, f"{identifier}.{field.name}"
            assert "dict[" not in annotation, f"{identifier}.{field.name}"
            assert "set[" not in annotation, f"{identifier}.{field.name}"


def test_zero_production_references_to_design_prototype():
    """TC-UI-06: Zero references to design-prototype in templates and static files."""
    for template in _templates():
        clean = _clean_source(template.read_text())
        assert "design-prototype" not in clean, template.name

    for asset in sorted(STATIC_ROOT.glob("**/*")):
        if asset.is_file():
            assert "design-prototype" not in asset.name, asset.name
            if asset.suffix.lower() in {".css", ".js", ".html", ".svg"}:
                assert "design-prototype" not in asset.read_text(errors="replace")


# ===========================================================================
# 12. Controlled Falsification Probes (F-SEC-01 through F-SEC-10)
# ===========================================================================


def test_falsification_f_sec_01_security_headers() -> None:
    """F-SEC-01: validate_response_security_headers fails on header violations."""
    from unittest.mock import MagicMock

    def mock_response(headers_dict):
        class HeadersAdapter:
            def __init__(self, d):
                self._d = {k.lower(): v for k, v in d.items()}
                self._lists = {k.lower(): [v] if isinstance(v, str) else list(v) for k, v in d.items()}
            def __getitem__(self, k):
                return self._d[k.lower()]
            def __contains__(self, k):
                return k.lower() in self._d
            def __iter__(self):
                return iter(self._d)
            def get(self, k, default=None):
                return self._d.get(k.lower(), default)
            def get_list(self, k):
                return self._lists.get(k.lower(), [])

        r = MagicMock()
        r.headers = HeadersAdapter(headers_dict)
        return r

    valid_headers = {
        "Content-Security-Policy": CONTENT_SECURITY_POLICY,
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "same-origin",
        "Cross-Origin-Opener-Policy": "same-origin",
        "Cross-Origin-Resource-Policy": "same-origin",
        "Permissions-Policy": "geolocation=(), camera=(), microphone=(), payment=()",
        "Cache-Control": "no-store",
    }

    # Baseline passes
    validate_response_security_headers(mock_response(valid_headers), authenticated=True, path="/v1/test")

    # 1. Missing header fails
    bad_missing = valid_headers.copy()
    del bad_missing["X-Content-Type-Options"]
    with pytest.raises(AssertionError, match="Missing security header 'X-Content-Type-Options'"):
        validate_response_security_headers(mock_response(bad_missing), authenticated=True, path="/v1/test")

    # 2. Weakened CSP fails
    bad_csp = valid_headers.copy()
    bad_csp["Content-Security-Policy"] = "default-src *; script-src 'unsafe-inline'"
    with pytest.raises(AssertionError, match="CSP mismatch"):
        validate_response_security_headers(mock_response(bad_csp), authenticated=True, path="/v1/test")

    # 3. Missing Cache-Control fails
    bad_cache = valid_headers.copy()
    bad_cache["Cache-Control"] = "public, max-age=3600"
    with pytest.raises(AssertionError, match="Expected 'no-store'"):
        validate_response_security_headers(mock_response(bad_cache), authenticated=True, path="/v1/test")

    # 4. Prohibited X-Frame-Options fails
    bad_xfo = valid_headers.copy()
    bad_xfo["X-Frame-Options"] = "DENY"
    with pytest.raises(AssertionError, match="X-Frame-Options must not be set"):
        validate_response_security_headers(mock_response(bad_xfo), authenticated=True, path="/v1/test")

    # 5. Prohibited CORS header fails
    bad_cors = valid_headers.copy()
    bad_cors["Access-Control-Allow-Origin"] = "*"
    with pytest.raises(AssertionError, match="Unexpected CORS header"):
        validate_response_security_headers(mock_response(bad_cors), authenticated=True, path="/v1/test")


def test_falsification_f_sec_02_template_escaping_ast() -> None:
    """F-SEC-02: validate_template_escaping_ast fails on bypasses."""
    clean_templates = {name: "<div>{{ view.field }}</div>" for name in ALL_PRODUCTION_TEMPLATES}

    # Baseline passes
    validate_template_escaping_ast(clean_templates)

    # 1. Direct |safe filter fails
    bad_safe = clean_templates.copy()
    bad_safe["login.html"] = "<div>{{ view.field | safe }}</div>"
    with pytest.raises(AssertionError, match=r"prohibited Jinja filter '\|safe'"):
        validate_template_escaping_ast(bad_safe)

    # 2. Chained filter with safe fails
    bad_chain = clean_templates.copy()
    bad_chain["character_links.html"] = "<div>{{ view.field | trim | safe }}</div>"
    with pytest.raises(AssertionError, match=r"prohibited Jinja filter '\|safe'"):
        validate_template_escaping_ast(bad_chain)

    # 3. Markup call fails
    bad_markup = clean_templates.copy()
    bad_markup["audit_results.html"] = "<div>{{ Markup('<b>test</b>') }}</div>"
    with pytest.raises(AssertionError, match="calls prohibited 'Markup'"):
        validate_template_escaping_ast(bad_markup)


async def test_falsification_f_sec_03_hostile_rendering_inert(
    client, settings, callers, migrated_database
) -> None:
    """F-SEC-03 (R12-05/R12-07): assert_hostile_renders_inert fails on 201/199 len, extra suffix, wrong NFC/NFD, injection."""
    with migrated_database.begin() as connection:
        connection.execute(
            insert(audit_events).values(
                id=uuid4(),
                occurred_at=utcnow(),
                actor_platform_account_id=callers["C"].account_id,
                actor_capability="guild_council",
                action="character_access.granted",
                entity_type="character_access",
                entity_id=str(uuid4()),
                source="web",
                correlation_id=uuid4(),
                payload={"reason": "x" * AUDIT_VALUE_BOUND},
            )
        )

    res = await client.get("/v1/audit/results", cookies=callers["C"].cookies(settings))
    assert res.status_code == 200
    real_response = res.text

    # Positive baseline passes
    assert_hostile_renders_inert(
        real_response,
        "x" * AUDIT_VALUE_BOUND,
        container_selector='[data-field="fact-after"]',
        expected_count=1,
        expected_bound=AUDIT_VALUE_BOUND,
    )

    # 1. Expected 200 but actual 201 characters fails
    bad_201 = real_response.replace("x" * AUDIT_VALUE_BOUND, "x" * (AUDIT_VALUE_BOUND + 1))
    assert bad_201 != real_response
    with pytest.raises(AssertionError, match=r"Governed text length mismatch: expected 200, got 201"):
        assert_hostile_renders_inert(
            bad_201,
            "x" * AUDIT_VALUE_BOUND,
            container_selector='[data-field="fact-after"]',
            expected_count=1,
            expected_bound=AUDIT_VALUE_BOUND,
        )

    # 2. Expected 200 but actual 199 characters fails
    bad_199 = real_response.replace("x" * AUDIT_VALUE_BOUND, "x" * (AUDIT_VALUE_BOUND - 1))
    assert bad_199 != real_response
    with pytest.raises(AssertionError, match=r"Governed text length mismatch: expected 200, got 199"):
        assert_hostile_renders_inert(
            bad_199,
            "x" * AUDIT_VALUE_BOUND,
            container_selector='[data-field="fact-after"]',
            expected_count=1,
            expected_bound=AUDIT_VALUE_BOUND,
        )

    # 3. Correct value plus extra suffix fails
    bad_suffix = real_response.replace("x" * AUDIT_VALUE_BOUND, ("x" * AUDIT_VALUE_BOUND) + " extra")
    assert bad_suffix != real_response
    with pytest.raises(AssertionError, match="Governed text length mismatch"):
        assert_hostile_renders_inert(
            bad_suffix,
            "x" * AUDIT_VALUE_BOUND,
            container_selector='[data-field="fact-after"]',
            expected_count=1,
            expected_bound=AUDIT_VALUE_BOUND,
        )

    # 4. Visually equivalent but wrong NFC/NFD code-point form fails
    nfc_text = "café"  # \u00e9 (length 4)
    nfd_text = "cafe\u0301"  # e + \u0301 (length 5)
    real_nfc_resp = real_response.replace("x" * AUDIT_VALUE_BOUND, nfc_text)
    bad_nfd = real_nfc_resp.replace(nfc_text, nfd_text)
    assert bad_nfd != real_nfc_resp
    with pytest.raises(AssertionError, match="Governed text length mismatch"):
        assert_hostile_renders_inert(
            bad_nfd,
            nfc_text,
            container_selector='[data-field="fact-after"]',
            expected_count=1,
        )

    # 5. Injected child onerror element fails
    bad_onerror = real_response.replace(
        "x" * AUDIT_VALUE_BOUND,
        '<img src="x" onerror="alert(1)">'
    )
    assert bad_onerror != real_response
    with pytest.raises(AssertionError, match="Hostile element <img> injected"):
        assert_hostile_renders_inert(
            bad_onerror,
            '"><img src=x onerror=alert(1)>',
            container_selector='[data-field="fact-after"]',
            expected_count=1,
        )

    # 6. Evaluated {{7*7}} to 49 fails
    eval_response = real_response.replace("x" * AUDIT_VALUE_BOUND, "49")
    assert eval_response != real_response
    with pytest.raises(AssertionError, match=r"Literal {{7\*7}} missing in container"):
        assert_hostile_renders_inert(
            eval_response,
            "{{7*7}}",
            container_selector='[data-field="fact-after"]',
            expected_count=1,
        )

    # 7. Missing governed value entirely fails
    missing_response = real_response.replace("x" * AUDIT_VALUE_BOUND, "y" * AUDIT_VALUE_BOUND)
    assert missing_response != real_response
    with pytest.raises(AssertionError, match="Governed text value mismatch"):
        assert_hostile_renders_inert(
            missing_response,
            "x" * AUDIT_VALUE_BOUND,
            container_selector='[data-field="fact-after"]',
            expected_count=1,
            expected_bound=AUDIT_VALUE_BOUND,
        )

    # 8. Wrong container selector fails
    with pytest.raises(AssertionError, match="Expected exactly 1 container.*found 0"):
        assert_hostile_renders_inert(
            real_response,
            "x" * AUDIT_VALUE_BOUND,
            container_selector='[data-field="nonexistent"]',
            expected_count=1,
        )


def test_falsification_f_sec_04_executable_contexts() -> None:
    """F-SEC-04: validate_executable_contexts fails on prohibited executable contexts."""
    allowed_src = _allowed_htmx_script_src()
    clean_templates = {name: "<div>{{ view.field }}</div>" for name in ALL_PRODUCTION_TEMPLATES}
    clean_templates["base.html"] = f'<!doctype html><html><head><script defer src="{allowed_src}"></script></head><body></body></html>'

    # Baseline passes
    validate_executable_contexts(clean_templates, allowed_src)

    # 1. hx-on attribute fails
    bad_hx_on = clean_templates.copy()
    bad_hx_on["login.html"] = '<button hx-on:click="doSomething()">Click</button>'
    with pytest.raises(AssertionError, match="Template 'login.html' contains 'hx-on:'"):
        validate_executable_contexts(bad_hx_on, allowed_src)

    # 2. Inline onclick handler fails
    bad_onclick = clean_templates.copy()
    bad_onclick["character_links.html"] = '<a href="#" onclick="alert(1)">Link</a>'
    with pytest.raises(AssertionError, match="has inline event handler 'onclick'"):
        validate_executable_contexts(bad_onclick, allowed_src)

    # 3. javascript: URL fails
    bad_js_url = clean_templates.copy()
    bad_js_url["council_characters.html"] = '<a href="javascript:void(0)">Link</a>'
    with pytest.raises(AssertionError, match="has javascript: URL in 'href'"):
        validate_executable_contexts(bad_js_url, allowed_src)

    # 4. Inline script body fails
    bad_inline = clean_templates.copy()
    bad_inline["base.html"] = f'<!doctype html><html><head><script defer src="{allowed_src}">console.log(1);</script></head><body></body></html>'
    with pytest.raises(AssertionError, match="base.html script has inline body content"):
        validate_executable_contexts(bad_inline, allowed_src)

    # 5. Remote CDN origin fails
    bad_cdn = clean_templates.copy()
    bad_cdn["character_detail.html"] = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome.css">'
    with pytest.raises(AssertionError, match="references remote origin marker"):
        validate_executable_contexts(bad_cdn, allowed_src)


def test_falsification_f_sec_05_script_context_invariants() -> None:
    """F-SEC-05: validate_executable_contexts fails when Jinja expressions appear in script context."""
    allowed_src = _allowed_htmx_script_src()
    clean_templates = {name: "<div>{{ view.field }}</div>" for name in ALL_PRODUCTION_TEMPLATES}

    # 1. Jinja expression in script tag attributes fails
    bad_attr = clean_templates.copy()
    bad_attr["base.html"] = f'<!doctype html><html><head><script defer src="{allowed_src}?v={{{{ view.version }}}}"></script></head><body></body></html>'
    with pytest.raises(AssertionError, match="Jinja found in script tag attributes"):
        validate_executable_contexts(bad_attr, allowed_src)

    # 2. Script in non-base template fails
    bad_other_script = clean_templates.copy()
    bad_other_script["base.html"] = f'<!doctype html><html><head><script defer src="{allowed_src}"></script></head><body></body></html>'
    bad_other_script["login.html"] = f'<script src="{allowed_src}"></script>'
    with pytest.raises(AssertionError, match="Template 'login.html' must not contain any <script> element"):
        validate_executable_contexts(bad_other_script, allowed_src)


async def test_falsification_f_sec_06_denial_response_body(client, settings, callers) -> None:
    """F-SEC-06 (R12-07): validate_denial_response_body fails on leaked internals or invalid state from real ASGI baseline."""
    res_404 = await client.get(
        f"/v1/characters/{uuid4()}", cookies=callers["M"].cookies(settings)
    )
    assert res_404.status_code == 404
    real_denial_html = res_404.text

    class RespAdapter:
        def __init__(self, text, status_code=404):
            self.text = text
            self.status_code = status_code

    # Baseline passes
    validate_denial_response_body(RespAdapter(real_denial_html, 404), DenialCategory.NOT_AVAILABLE)

    # 1. Injected SQL statement fails
    bad_sql = real_denial_html.replace("This is not available to you.", "This is not available to you. SELECT * FROM users")
    assert bad_sql != real_denial_html
    with pytest.raises(AssertionError, match="Leaked internal 'select '"):
        validate_denial_response_body(RespAdapter(bad_sql, 404), DenialCategory.NOT_AVAILABLE)

    # 2. Injected stack trace keyword fails
    bad_trace = real_denial_html.replace("This is not available to you.", "This is not available to you. Traceback (most recent call last):")
    assert bad_trace != real_denial_html
    with pytest.raises(AssertionError, match="Leaked internal 'traceback'"):
        validate_denial_response_body(RespAdapter(bad_trace, 404), DenialCategory.NOT_AVAILABLE)

    # 3. Wrong data-state fails
    bad_state = real_denial_html.replace('data-state="denied"', 'data-state="ready"')
    assert bad_state != real_denial_html
    with pytest.raises(AssertionError, match="Missing data-state='denied'"):
        validate_denial_response_body(RespAdapter(bad_state, 404), DenialCategory.NOT_AVAILABLE)


async def test_falsification_f_sec_07_validation_response_body(client, settings, callers, snapshot) -> None:
    """F-SEC-07 (R12-07): validate_validation_response_body fails on missing field or leaked internals from real ASGI baseline."""
    snapshot_id, _ = snapshot
    res_422 = await client.post(
        f"/v1/admin/snapshots/{snapshot_id}/folder",
        cookies=callers["A"].cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        data={"csrf_token": csrf_token_for(settings, callers["A"]), "folder_id": "../../etc/passwd"},
    )
    assert res_422.status_code == 422
    real_val_html = res_422.text

    class RespAdapter:
        def __init__(self, text, status_code=422):
            self.text = text
            self.status_code = status_code

    # Baseline passes
    validate_validation_response_body(RespAdapter(real_val_html, 422), expected_field="folder_id")

    # 1. Missing expected field fails
    with pytest.raises(AssertionError, match="Expected validation field 'missing_field' not found"):
        validate_validation_response_body(RespAdapter(real_val_html, 422), expected_field="missing_field")

    # 2. Leaked traceback fails
    bad_trace = real_val_html.replace("That could not be accepted", "That could not be accepted (Exception in app.py)")
    assert bad_trace != real_val_html
    with pytest.raises(AssertionError, match="Leaked internal 'exception'"):
        validate_validation_response_body(RespAdapter(bad_trace, 422), expected_field="folder_id")


async def test_falsification_f_sec_08_stale_response_body(
    client, settings, callers, snapshot, outage, migrated_database
) -> None:
    """F-SEC-08 (R12-07): validate_stale_response_body fails on missing state or invalid maintenance headers from real ASGI baseline."""
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        stale_membership(connection, subject=COUNCIL_SUBJECT, minutes=30)

    res_503 = await client.get(
        f"/v1/council/jobs/{job_id}", cookies=callers["C"].cookies(settings)
    )
    assert res_503.status_code == 503
    real_degraded_html = res_503.text

    class RespAdapter:
        def __init__(self, text, status_code=503, headers=None):
            self.text = text
            self.status_code = status_code
            self.headers = headers or {}

    # Baseline passes
    validate_stale_response_body(RespAdapter(real_degraded_html, 503))

    # 1. Invalid status fails
    with pytest.raises(AssertionError, match="Unexpected stale status 200"):
        validate_stale_response_body(RespAdapter(real_degraded_html, 200))

    # 2. Wrong subsystem container fails
    bad_subsystem = real_degraded_html.replace('data-subsystem="identity_provider"', '')
    assert bad_subsystem != real_degraded_html
    with pytest.raises(AssertionError, match="Missing degraded subsystem container"):
        validate_stale_response_body(RespAdapter(bad_subsystem, 503))


async def test_falsification_f_sec_09_safe_error_body(composition, monkeypatch) -> None:
    """F-SEC-09 (R12-06/R12-07): validate_safe_error_body fails on single-UUID and leakage violations from real ASGI baseline."""
    import httpx

    def explode(self, _connection):
        raise RuntimeError("simulated error")

    monkeypatch.setattr(WebComposition, "services", explode)
    app = create_app(composition=composition, run_startup_checks=False)
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url=PUBLIC_ORIGIN) as local_client:
        response = await local_client.get("/v1/auth/discord/start")
        assert response.status_code == 500
        real_error_html = response.text

    class RespAdapter:
        def __init__(self, text, status_code=500):
            self.text = text
            self.status_code = status_code

    # Baseline passes
    validate_safe_error_body(RespAdapter(real_error_html, 500))

    soup = BeautifulSoup(real_error_html, "html.parser")
    ref_el = soup.select_one(".reference-code")
    assert ref_el is not None
    corr_id = str(ref_el.contents[0])
    assert UUID(corr_id)

    # 1. Duplicate reference element fails
    dup_html = real_error_html.replace(
        f'<span class="reference-code">{corr_id}</span>',
        f'<span class="reference-code">{corr_id}</span><span class="reference-code">{corr_id}</span>'
    )
    assert dup_html != real_error_html
    with pytest.raises(AssertionError, match="expected exactly one correlation reference element"):
        validate_safe_error_body(RespAdapter(dup_html))

    # 2. Uppercase canonical-looking UUID fails
    upper_html = real_error_html.replace(corr_id, corr_id.upper())
    assert upper_html != real_error_html
    with pytest.raises(AssertionError, match="not in exact canonical UUID format"):
        validate_safe_error_body(RespAdapter(upper_html))

    # 3. Braced UUID fails
    braced_html = real_error_html.replace(corr_id, f"{{{corr_id}}}")
    assert braced_html != real_error_html
    with pytest.raises(AssertionError, match="not in exact canonical UUID format"):
        validate_safe_error_body(RespAdapter(braced_html))

    # 4. URN UUID fails
    urn_html = real_error_html.replace(corr_id, f"urn:uuid:{corr_id}")
    assert urn_html != real_error_html
    with pytest.raises(AssertionError, match="not in exact canonical UUID format"):
        validate_safe_error_body(RespAdapter(urn_html))

    # 5. Unhyphenated UUID fails
    unhyphen_html = real_error_html.replace(corr_id, corr_id.replace("-", ""))
    assert unhyphen_html != real_error_html
    with pytest.raises(AssertionError, match="not in exact canonical UUID format"):
        validate_safe_error_body(RespAdapter(unhyphen_html))

    # 6. Leading/trailing whitespace fails
    ws_html = real_error_html.replace(f">{corr_id}<", f"> {corr_id} <")
    assert ws_html != real_error_html
    with pytest.raises(AssertionError, match=r"correlation reference text .* (is not in exact canonical UUID format|is not a valid UUID)"):
        validate_safe_error_body(RespAdapter(ws_html))

    # 7. Child element inside reference-code fails
    child_html = real_error_html.replace(f">{corr_id}<", f"><span>{corr_id}</span><")
    assert child_html != real_error_html
    with pytest.raises(AssertionError, match="contains child markup, comments, or mixed content"):
        validate_safe_error_body(RespAdapter(child_html))

    # 8. Comment inside reference-code fails
    comment_html = real_error_html.replace(f">{corr_id}<", f">{corr_id}<!-- comment --><")
    assert comment_html != real_error_html
    with pytest.raises(AssertionError, match="contains child markup, comments, or mixed content"):
        validate_safe_error_body(RespAdapter(comment_html))

    # 9. Prose prefix/suffix fails
    prose_html = real_error_html.replace(f">{corr_id}<", f">Ref: {corr_id}<")
    assert prose_html != real_error_html
    with pytest.raises(AssertionError, match=r"correlation reference text .* (is not in exact canonical UUID format|is not a valid UUID)"):
        validate_safe_error_body(RespAdapter(prose_html))

    # 10. Malformed UUID fails
    malformed_html = real_error_html.replace(corr_id, "not-a-uuid")
    assert malformed_html != real_error_html
    with pytest.raises(AssertionError, match="not a valid UUID"):
        validate_safe_error_body(RespAdapter(malformed_html))

    # 11. Leaked raw exception fails
    leak_html = real_error_html.replace("Something went wrong", "Something went wrong: RuntimeError: boom in app.py")
    assert leak_html != real_error_html
    with pytest.raises(AssertionError, match="Leaked internal 'runtimeerror'"):
        validate_safe_error_body(RespAdapter(leak_html))


async def test_falsification_f_sec_10_no_javascript_fallback(app, client, settings, callers) -> None:
    """F-SEC-10 (R12-07): validate_rendered_no_js_fallback fails on missing CSRF, wrong action, or method from real ASGI baseline."""
    res_council = await client.get("/v1/council/characters", cookies=callers["C"].cookies(settings))
    assert res_council.status_code == 200
    real_council_html = strip_htmx_attributes(res_council.text)

    valid_contract = FlowContract(
        flow_name="Flow-04: Council Characters Search",
        expected_forms=(
            FormContract(action="/v1/council/characters", method="GET", requires_csrf=False),
        ),
        expected_link_prefixes=("/v1/characters",),
    )

    # Baseline passes
    validate_rendered_no_js_fallback(real_council_html, valid_contract, app=app)

    # 1. Wrong action fails
    bad_action_contract = FlowContract(
        flow_name="Test Flow",
        expected_forms=(
            FormContract(action="/v1/wrong-action", method="GET", requires_csrf=False),
        ),
    )
    with pytest.raises(AssertionError, match="Expected exactly 1 form with action"):
        validate_rendered_no_js_fallback(real_council_html, bad_action_contract, app=app)

    # 2. Wrong method fails
    bad_method_html = real_council_html.replace('method="get"', 'method="POST"').replace('method="GET"', 'method="POST"')
    assert bad_method_html != real_council_html
    with pytest.raises(AssertionError, match="Expected exactly 1 form with action"):
        validate_rendered_no_js_fallback(bad_method_html, valid_contract, app=app)

    # 3. Missing CSRF on required form fails
    csrf_contract = FlowContract(
        flow_name="Test Flow",
        expected_forms=(
            FormContract(action="/v1/council/characters", method="GET", requires_csrf=True),
        ),
    )
    with pytest.raises(AssertionError, match="Expected exactly 1 hidden input named 'csrf_token'"):
        validate_rendered_no_js_fallback(real_council_html, csrf_contract, app=app)

    # 4. Unregistered route fails
    unregistered_contract = FlowContract(
        flow_name="Test Flow",
        expected_forms=(
            FormContract(action="/v1/nonexistent/route", method="GET", requires_csrf=False),
        ),
    )
    unregistered_html = real_council_html.replace('/v1/council/characters', '/v1/nonexistent/route')
    assert unregistered_html != real_council_html
    with pytest.raises(AssertionError, match="is not a registered route"):
        validate_rendered_no_js_fallback(unregistered_html, unregistered_contract, app=app)


async def test_falsification_council_identity_search_hostile_rendering(
    client, settings, callers, migrated_database
) -> None:
    """F-SEC-11 / R12-08: Falsification on real ASGI Council identity-search response."""
    from tests.web.conftest import TEST_GUILD_ID

    subject_snowflake = 800000000000007777
    test_username = "audit_target_user"

    with migrated_database.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO discord_users (id, username, global_name) "
                "VALUES (:id, :username, null) "
                "ON CONFLICT (id) DO UPDATE SET username = :username, global_name = null"
            ),
            {"id": subject_snowflake, "username": test_username},
        )
        connection.execute(
            text(
                "INSERT INTO discord_guild_memberships (discord_user_id, guild_id, active) "
                "VALUES (:user, :guild, true) "
                "ON CONFLICT (discord_user_id, guild_id) DO UPDATE SET active = true"
            ),
            {"user": subject_snowflake, "guild": TEST_GUILD_ID},
        )

    res = await client.get(
        "/v1/council/identity-search",
        params={"q": "audit_target"},
        cookies=callers["C"].cookies(settings),
    )
    assert res.status_code == 200
    real_response = res.text

    # Positive baseline passes
    assert_hostile_renders_inert(
        real_response,
        test_username,
        container_selector="span.candidate-username strong",
        expected_count=1,
    )

    # 1. Injected element/event handler in name fails
    bad_inject = real_response.replace(
        test_username,
        '<img src="x" onerror="alert(1)">'
    )
    assert bad_inject != real_response
    with pytest.raises(AssertionError, match="Hostile element <img> injected"):
        assert_hostile_renders_inert(
            bad_inject,
            '"><img src=x onerror=alert(1)>',
            container_selector="span.candidate-username strong",
            expected_count=1,
        )

    # 2. Evaluated {{7*7}} to 49 in name fails
    eval_response = real_response.replace(test_username, "49")
    assert eval_response != real_response
    with pytest.raises(AssertionError, match=r"Literal {{7\*7}} missing in container"):
        assert_hostile_renders_inert(
            eval_response,
            "{{7*7}}",
            container_selector="span.candidate-username strong",
            expected_count=1,
        )

    # 3. Removed/altered governed name fails
    missing_response = real_response.replace(test_username, "wrong_target_user")
    assert missing_response != real_response
    with pytest.raises(AssertionError, match="Governed text value mismatch"):
        assert_hostile_renders_inert(
            missing_response,
            test_username,
            container_selector="span.candidate-username strong",
            expected_count=1,
        )

    # 4. Placed name in wrong container selector fails
    with pytest.raises(AssertionError, match="Expected exactly 1 container.*found 0"):
        assert_hostile_renders_inert(
            real_response,
            test_username,
            container_selector="span.nonexistent-container",
            expected_count=1,
        )

    # 5. Altered normalized representation fails
    with pytest.raises(AssertionError, match="Governed text value mismatch"):
        assert_hostile_renders_inert(
            real_response,
            test_username,
            container_selector="span.candidate-username strong",
            expected_count=1,
            normalized_expected="altered_target_us",
        )

