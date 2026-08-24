"""Comprehensive test suite for P3.4 Step 4: authentication and system-state pages.

Remediated per Phase 3 Step 4 Remediation 02 (R1):
- Added autouse yield-based clean_between_cases fixture performing post-test character cleanup via clean_p3_2_tables.
- Added non-database structural test and shared validation helper proving clean_between_cases executes
  strictly after yield for database tests and never resolves migrated_database for non-database tests.
- Added deterministic falsifications for cleanup-before-yield and missing-cleanup fixtures.
- Retains database-marked VM-22 HTTP byte-identity test, VM-04 4-combination availability checks,
  R-09 exact inventory, autoescaping probes, security rules, and untouched template digests.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from uuid import UUID, uuid4

import jinja2
import pytest
from starlette.requests import Request

from application.web.view_models import (
    ConflictView,
    Correlation,
    DegradedProvider,
    DenialCategory,
    DeniedReason,
    DeniedView,
    EmergencyFailure,
    EmergencyLoginView,
    FieldError,
    Instant,
    LoginFailure,
    LoginPageView,
    NonMemberView,
    ProviderOption,
    SafeErrorView,
    SafeText,
    ServiceDegradedView,
    ValidationView,
)
from tests.web.conftest import link_discord, make_account
from tests.web.portal_fixtures import (
    OTHER_MEMBER_SUBJECT,
    clean_p3_2_tables,
    grant_link,
    make_character,
    seed_callers,
    seed_discord_member,
)

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = ROOT / "adapters" / "web" / "templates"
STATIC_ROOT = ROOT / "adapters" / "web" / "static"
MANIFEST_PATH = STATIC_ROOT / "asset-integrity.sha256"

from tests.web.template_digests import NON_STEP_4_TEMPLATE_DIGESTS
from application.web.shell import ANONYMOUS_SHELL



@pytest.fixture(autouse=True)
def clean_between_cases(request):
    """Leave the character tables as the migration left them, after every test (R1).

    Yields first so test execution runs, then resolves migrated_database only if
    the test requested it, and invokes the shared clean_p3_2_tables helper.
    """
    yield
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)


def get_jinja_env() -> jinja2.Environment:
    environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_ROOT)),
        autoescape=True,
        undefined=jinja2.StrictUndefined,
    )
    # The server-owned shell (C35-05) is supplied by `RequestAuthority.render()`
    # on every real full-page render. These tests render templates in isolation,
    # with no request boundary to derive one, so the anonymous shell is the
    # default here. A context value overrides a global, so a test supplying its
    # own shell — and production, which always does — is unaffected. That
    # production always passes one explicitly is asserted separately, so this
    # default cannot hide a regression in the wiring.
    environment.globals.setdefault("shell", ANONYMOUS_SHELL)
    return environment


def make_request(path: str = "/v1/login") -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": [(b"host", b"testserver")],
    }
    return Request(scope)


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


# ===========================================================================
# Shared Production Validation Helpers
# ===========================================================================

def validate_auth_page_structure(rendered_html: str, expected_title_snippet: str, expected_h1: str) -> None:
    """Validator: asserts document structure, title, single h1, heading order, and landmarks."""
    # 1. Title
    title_match = re.search(r"<title>(.*?)</title>", rendered_html, flags=re.DOTALL)
    assert title_match, "Missing <title> tag in rendered HTML"
    assert expected_title_snippet in title_match.group(1), (
        f"Expected '{expected_title_snippet}' in title, got '{title_match.group(1)}'"
    )

    # 2. Exactly one <h1>
    h1_matches = re.findall(r"<h1\b[^>]*>(.*?)</h1>", rendered_html, flags=re.DOTALL)
    assert len(h1_matches) == 1, f"Expected exactly one <h1>, found {len(h1_matches)}: {h1_matches}"
    h1_clean = re.sub(r"<[^>]+>", "", h1_matches[0]).strip()
    assert h1_clean == expected_h1, f"Expected <h1> '{expected_h1}', got '{h1_clean}'"

    # 3. Landmark order
    header_pos = rendered_html.find("<header")
    nav_pos = rendered_html.find("<nav")
    main_pos = rendered_html.find('<main id="main-content"')
    footer_pos = rendered_html.find("<footer")
    assert header_pos != -1 and nav_pos != -1 and main_pos != -1 and footer_pos != -1
    assert header_pos < nav_pos < main_pos < footer_pos, "Invalid landmark order"


def validate_r09_recovery_form(rendered_html: str) -> None:
    """Validator: asserts R-09 form method, action, and EXACT successful named fields set {'token'}."""
    form_match = re.search(r'<form\b([^>]*)>(.*?)</form>', rendered_html, flags=re.DOTALL)
    assert form_match, "Missing emergency recovery <form>"
    attrs, body = form_match.group(1), form_match.group(2)

    assert 'method="post"' in attrs or "method='post'" in attrs, "Recovery form must be method='post'"
    assert 'action="/v1/auth/emergency/recovery"' in attrs or "action='/v1/auth/emergency/recovery'" in attrs, (
        "Recovery form action must be '/v1/auth/emergency/recovery'"
    )

    # Find all input/select/textarea/button names
    named_elements = re.findall(r'<(?:input|select|textarea|button)\b[^>]*\bname=["\']([^"\']+)["\']', body)
    named_set = set(named_elements)
    assert named_set == {"token"}, f"R-09 recovery form named fields must be exactly {{'token'}}, got {named_set}"

    # Specific prohibited field assertions
    assert "csrf_token" not in named_set, "csrf_token must not be present in emergency recovery form"
    assert "username" not in named_set, "username must not be present in emergency recovery form"
    assert "account" not in named_set, "account must not be present in emergency recovery form"

    # Input constraints
    input_match = re.search(r'<input\b[^>]*\bname=["\']token["\'][^>]*>', body)
    assert input_match, "Missing token input"
    input_tag = input_match.group(0)
    assert 'type="password"' in input_tag or "type='password'" in input_tag, "Token input must be type='password'"
    assert 'autocomplete="off"' in input_tag or "autocomplete='off'" in input_tag, "Token input must have autocomplete='off'"
    assert "required" in input_tag, "Token input must be required"


def validate_emergency_page_availability(
    rendered_html: str,
    *,
    webauthn_expected: bool,
    recovery_expected: bool,
) -> None:
    """Validator (F3): asserts conditional rendering of WebAuthn and recovery sections per VM-04 facts."""
    # 1. WebAuthn section checks
    webauthn_match = re.search(r'<section\s+data-section="webauthn"[^>]*>(.*?)</section>', rendered_html, flags=re.DOTALL)
    assert webauthn_match, "Missing <section data-section=\"webauthn\">"
    webauthn_body = webauthn_match.group(1)

    if webauthn_expected:
        assert "Present an enrolled security key." in webauthn_body, "Missing WebAuthn instruction text"
        assert "Security key sign-in is not available." not in webauthn_body
    else:
        assert "Security key sign-in is not available." in webauthn_body, "Missing WebAuthn unavailable notice"
        assert "Present an enrolled security key." not in webauthn_body

    # 2. Recovery section checks
    recovery_match = re.search(r'<section\s+data-section="recovery"[^>]*>(.*?)</section>', rendered_html, flags=re.DOTALL)
    assert recovery_match, "Missing <section data-section=\"recovery\">"
    recovery_body = recovery_match.group(1)

    if recovery_expected:
        assert "<form" in recovery_body, "Recovery section must contain recovery form when available"
        validate_r09_recovery_form(rendered_html)
        assert "Recovery token sign-in is not available." not in recovery_body
    else:
        assert "<form" not in recovery_body, "Recovery form must not be present when recovery_form_available is False"
        assert "Recovery token sign-in is not available." in recovery_body, "Missing recovery unavailable notice"

    # 3. Non-enumeration oracle checks
    prohibited_oracle_terms = [
        "credential_nickname",
        "grant_state",
        "account_id",
        "caller_state",
        "grant_id",
        "grant_expires_at",
    ]
    for term in prohibited_oracle_terms:
        assert term not in rendered_html, f"Prohibited oracle detail '{term}' found in emergency view"


def validate_denied_page_minimization(rendered_html: str) -> None:
    """Validator: asserts VM-22 generic denial renders ONLY state, reason.category, and navigation link."""
    # Must contain category
    assert 'data-state="denied"' in rendered_html
    assert 'data-reason="' in rendered_html
    assert "/v1/characters" in rendered_html

    # Prohibited disclosures on generic denial page (VM-22 / TC-OBJ-07)
    uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    uuids_found = re.findall(uuid_pattern, rendered_html, flags=re.IGNORECASE)
    assert len(uuids_found) == 0, f"Prohibited UUID/correlation disclosure found in VM-22: {uuids_found}"

    assert "Reference" not in rendered_html, "Correlation reference must not appear on generic denial page"
    assert "checked_at" not in rendered_html
    assert "guild" not in rendered_html
    assert "role" not in rendered_html
    assert "capability" not in rendered_html


def validate_validation_page_anchors(rendered_html: str) -> None:
    """Validator: asserts validation summary container is focusable and contains no broken anchors."""
    assert 'class="validation-summary"' in rendered_html
    assert 'tabindex="-1"' in rendered_html or "tabIndex='-1'" in rendered_html or 'tabindex="-1"' in rendered_html

    # Check that any fragment anchors (#id) correspond to an id present in the document
    href_targets = re.findall(r'<a\b[^>]*\bhref=["\']#([^"\']+)["\']', rendered_html)
    for target in href_targets:
        assert f'id="{target}"' in rendered_html or f"id='{target}'" in rendered_html, (
            f"Broken fragment target link #{target} in validation view"
        )


def validate_autoescaped_rendering(rendered_html: str, dangerous_tag: str) -> None:
    """Validator: asserts unescaped HTML element tag (e.g. <script> or <img onerror) is absent from output."""
    assert dangerous_tag not in rendered_html, f"Unescaped tag '{dangerous_tag}' found in rendered output"


def validate_database_teardown_fixture(fixture_func) -> None:
    """Validator (R1): proves fixture executes clean_p3_2_tables strictly AFTER yield for database tests."""
    raw_func = getattr(fixture_func, "__wrapped__", fixture_func)
    executed_statements: list[str] = []

    class DummyConnection:
        def execute(self, stmt, *args, **kwargs):
            executed_statements.append(str(stmt))
            return None

    class DummyEngine:
        def __init__(self):
            self.begun = False

        def begin(self):
            self.begun = True
            class ContextManager:
                def __enter__(self_inner):
                    return DummyConnection()
                def __exit__(self_inner, exc_type, exc_val, exc_tb):
                    pass
            return ContextManager()

    # 1. Test behavior when migrated_database is present
    dummy_engine = DummyEngine()

    class DummyRequestWithDb:
        def __init__(self):
            self.fixturenames = ["client", "settings", "migrated_database"]
            self.resolved = False

        def getfixturevalue(self, name: str):
            if name == "migrated_database":
                self.resolved = True
                return dummy_engine
            raise KeyError(name)

    req_with_db = DummyRequestWithDb()
    gen = raw_func(req_with_db)

    # Before yield: no cleanup, no engine resolution
    next(gen)
    assert not req_with_db.resolved, "Teardown cleanup must occur after yield, not before yield"
    assert len(executed_statements) == 0, "Teardown cleanup must occur after yield, not before yield"

    # After yield: engine must be resolved and cleanup executed
    try:
        next(gen)
    except StopIteration:
        pass
    assert req_with_db.resolved, "Post-test database teardown was not executed after yield"
    assert dummy_engine.begun, "Engine.begin() was not invoked during post-test cleanup"
    assert len(executed_statements) > 0, "clean_p3_2_tables cleanup statements were not executed"

    # 2. Test behavior when migrated_database is NOT present (must not request engine)
    class DummyRequestWithoutDb:
        def __init__(self):
            self.fixturenames = ["client", "settings"]
            self.resolved = False

        def getfixturevalue(self, name: str):
            if name == "migrated_database":
                self.resolved = True
                return dummy_engine
            raise KeyError(name)

    req_without_db = DummyRequestWithoutDb()
    gen_no_db = raw_func(req_without_db)
    next(gen_no_db)
    try:
        next(gen_no_db)
    except StopIteration:
        pass
    assert not req_without_db.resolved, "Non-database test must not request or touch migrated_database"


# ===========================================================================
# 1. Rendering of all 8 templates with representative view models
# ===========================================================================

def test_login_rendering_all_branches() -> None:
    """VM-01 / R-02: login.html renders ready, degraded, failure, and emergency access states."""
    env = get_jinja_env()
    template = env.get_template("login.html")

    # Case A: Ready with enabled/disabled providers and emergency access link
    vm_ready = LoginPageView(
        state="ready",
        providers=(
            ProviderOption(key="discord", display_name="Discord", start_path="/v1/auth/discord/start", enabled=True),
            ProviderOption(key="mock", display_name="Mock Auth", start_path="/v1/auth/mock/start", enabled=False),
        ),
        emergency_access_available=True,
    )
    rendered_a = template.render(view=vm_ready, request=make_request())
    validate_auth_page_structure(rendered_a, "Sign in", "Sign in")
    assert 'href="/v1/auth/discord/start"' in rendered_a
    assert 'data-provider="mock"' in rendered_a
    assert "Mock Auth is not available." in rendered_a
    assert 'href="/v1/auth/emergency"' in rendered_a
    assert "<form" not in rendered_a, "Login must not be a POST form"
    assert "https://discord.com" not in rendered_a, "No remote Discord URLs"

    # Case B: Degraded provider state
    vm_degraded = LoginPageView(
        state="ready",
        providers=(ProviderOption(key="discord", display_name="Discord", start_path="/v1/auth/discord/start", enabled=False),),
        emergency_access_available=False,
        degraded=DegradedProvider(
            provider_key="discord",
            since=Instant(iso_utc="2026-08-20T12:00:00Z", display="2026-08-20 12:00 UTC"),
            message_code="provider_unreachable",
        ),
    )
    rendered_b = template.render(view=vm_degraded, request=make_request())
    assert 'data-state="degraded"' in rendered_b
    assert 'data-code="provider_unreachable"' in rendered_b
    assert 'class="auth-emergency-link"' not in rendered_b
    assert "Server Administrator emergency access" not in rendered_b

    # Case C: Login failure state
    corr_id = uuid4()
    vm_failed = LoginPageView(
        state="error",
        providers=(),
        emergency_access_available=False,
        failure=LoginFailure(code="state_mismatch", correlation=Correlation(id=corr_id)),
    )
    rendered_c = template.render(view=vm_failed, request=make_request())
    assert 'data-state="error"' in rendered_c
    assert 'data-code="state_mismatch"' in rendered_c
    assert str(corr_id) in rendered_c


@pytest.mark.parametrize(
    "webauthn_supported,recovery_available,has_failure",
    [
        (True, True, False),
        (True, False, False),
        (False, True, False),
        (False, False, False),
        (True, True, True),
        (False, False, True),
    ],
)
def test_emergency_access_rendering_all_combinations(
    webauthn_supported: bool,
    recovery_available: bool,
    has_failure: bool,
) -> None:
    """VM-04 / R-06 / R-09 (F3): emergency.html renders all 4 boolean availability combinations and failure states."""
    env = get_jinja_env()
    template = env.get_template("emergency.html")

    corr_id = uuid4() if has_failure else None
    failure_obj = EmergencyFailure(code="consumed", correlation=Correlation(id=corr_id)) if has_failure else None

    vm = EmergencyLoginView(
        state="error" if has_failure else "ready",
        webauthn_supported_hint=webauthn_supported,
        recovery_form_available=recovery_available,
        failure=failure_obj,
    )
    rendered = template.render(view=vm, request=make_request("/v1/auth/emergency"))
    validate_auth_page_structure(rendered, "Emergency access", "Server Administrator emergency access")
    validate_emergency_page_availability(
        rendered,
        webauthn_expected=webauthn_supported,
        recovery_expected=recovery_available,
    )

    if has_failure:
        assert 'data-state="error"' in rendered
        assert 'data-code="consumed"' in rendered
        assert str(corr_id) in rendered
    else:
        assert 'data-state="error"' not in rendered
        assert 'class="alert alert-danger"' not in rendered


def test_non_member_rendering() -> None:
    """VM-02: non_member.html renders guild name, timestamp, correlation, and recovery link."""
    env = get_jinja_env()
    template = env.get_template("non_member.html")
    corr_id = uuid4()
    vm = NonMemberView(
        state="denied",
        reason=DeniedReason(category=DenialCategory.NOT_A_MEMBER),
        guild_display_name="Freedom Blades Guild",
        checked_at=Instant(iso_utc="2026-08-20T12:00:00Z", display="2026-08-20 12:00 UTC"),
        correlation=Correlation(id=corr_id),
    )
    rendered = template.render(view=vm, request=make_request())
    validate_auth_page_structure(rendered, "Not a member", "You are not currently a member")
    assert 'data-state="denied"' in rendered
    assert 'data-reason="not_a_member"' in rendered
    assert "Freedom Blades Guild" in rendered
    assert "2026-08-20 12:00 UTC" in rendered
    assert str(corr_id) in rendered
    assert 'href="/v1/login"' in rendered


def test_degraded_rendering() -> None:
    """VM-03: degraded.html renders fail-closed state, subsystem, and correlation."""
    env = get_jinja_env()
    template = env.get_template("degraded.html")
    corr_id = uuid4()
    vm = ServiceDegradedView(
        state="error",
        reason=DeniedReason(category=DenialCategory.SERVICE_DEGRADED),
        subsystem="identity_provider",
        grace_expired=True,
        correlation=Correlation(id=corr_id),
    )
    rendered = template.render(view=vm, request=make_request())
    validate_auth_page_structure(rendered, "Temporarily unavailable", "Authorization cannot be confirmed")
    assert 'data-state="error"' in rendered
    assert 'data-reason="service_degraded"' in rendered
    assert 'data-subsystem="identity_provider"' in rendered
    assert str(corr_id) in rendered


def test_denied_rendering_and_minimization() -> None:
    """VM-22: denied.html renders minimized denial without correlation, guild, or timestamps."""
    env = get_jinja_env()
    template = env.get_template("denied.html")
    vm = DeniedView(
        state="denied",
        reason=DeniedReason(category=DenialCategory.NOT_AVAILABLE),
    )
    rendered = template.render(view=vm, request=make_request())
    validate_auth_page_structure(rendered, "Not available", "Not available")
    validate_denied_page_minimization(rendered)


def test_conflict_rendering_and_conditional_scope() -> None:
    """VM-19: conflict.html renders stale conflict, correlation, and current scope without mutation controls."""
    env = get_jinja_env()
    template = env.get_template("conflict.html")
    corr_id = uuid4()

    # Create mock current view model with stale_reason and confirm scope
    class MockConfirm:
        checksum_full = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        profile_version = "v1.2.0"
        folder = type("Folder", (), {"folder_id": "f-101", "folder_path": SafeText("actors/heroes")})

    class MockCurrent:
        state = "ready"
        stale_reason = type("Stale", (), {"code": "snapshot_changed"})
        confirm = MockConfirm()

    vm = ConflictView(
        state="stale",
        conflict="stale_version",
        current=MockCurrent(),
        correlation=Correlation(id=corr_id),
    )
    rendered = template.render(view=vm, request=make_request())
    validate_auth_page_structure(rendered, "The page moved on", "Somebody changed this first")
    assert 'data-state="stale"' in rendered
    assert 'data-conflict="stale_version"' in rendered
    assert str(corr_id) in rendered
    assert 'data-field="stale-reason"' in rendered
    assert 'data-code="snapshot_changed"' in rendered
    assert 'data-field="confirm-scope"' in rendered
    assert "actors/heroes" in rendered
    assert "<form" not in rendered, "Conflict page must not contain a mutation form"


def test_validation_rendering_and_anchors() -> None:
    """VM-21: validation.html renders bounded field errors, focusable summary, and no broken links."""
    env = get_jinja_env()
    template = env.get_template("validation.html")
    vm = ValidationView(
        state="invalid",
        form=object(),
        errors=(
            FieldError(field="token", code="required"),
            FieldError(field="nickname", code="too_long", limit=80),
        ),
    )
    rendered = template.render(view=vm, request=make_request())
    validate_auth_page_structure(rendered, "Check the form", "That could not be accepted")
    validate_validation_page_anchors(rendered)
    assert 'data-field="token"' in rendered
    assert 'data-code="required"' in rendered
    assert 'data-field="nickname"' in rendered
    assert 'data-code="too_long"' in rendered
    assert "(80)" in rendered


def test_error_rendering() -> None:
    """VM-20: error.html renders safe error code and correlation without diagnostic leaks."""
    env = get_jinja_env()
    template = env.get_template("error.html")
    corr_id = uuid4()
    vm = SafeErrorView(
        state="error",
        correlation=Correlation(id=corr_id),
        message_code="unexpected_error",
    )
    rendered = template.render(view=vm, request=make_request())
    validate_auth_page_structure(rendered, "Something went wrong", "Something went wrong")
    assert 'data-state="error"' in rendered
    assert 'data-code="unexpected_error"' in rendered
    assert str(corr_id) in rendered
    assert "Traceback" not in rendered
    assert "Exception" not in rendered
    assert "SELECT " not in rendered


# ===========================================================================
# 2. Database-backed HTTP test: VM-22 absent vs inaccessible byte identity
# ===========================================================================

@pytest.mark.database
async def test_vm22_http_absent_and_inaccessible_byte_identity(client, settings, migrated_database):
    """F1 / D-03-6 / TC-OBJ-07: Inaccessible, absent, and malformed characters answer 404 with byte-identical bodies."""
    callers = seed_callers(migrated_database, settings, states=("U", "M", "C"))
    with migrated_database.begin() as connection:
        clean_p3_2_tables(connection)
        mine = make_character(connection, display_name="Alia Storm")
        theirs = make_character(connection, display_name="Someone Elses")
        grant_link(
            connection,
            character_id=mine,
            account_id=callers["M"].account_id,
            granted_by=callers["C"].account_id,
            default_character=True,
        )
        other_account = make_account(connection, label="other-member")
        seed_discord_member(connection, subject=OTHER_MEMBER_SUBJECT, username="other.one")
        link_discord(connection, other_account, OTHER_MEMBER_SUBJECT)
        grant_link(
            connection,
            character_id=theirs,
            account_id=other_account,
            granted_by=callers["C"].account_id,
        )

    member = callers["M"]
    inaccessible = await client.get(f"/v1/characters/{theirs}", cookies=member.cookies(settings))
    absent = await client.get(f"/v1/characters/{uuid4()}", cookies=member.cookies(settings))
    malformed = await client.get("/v1/characters/not-a-uuid", cookies=member.cookies(settings))

    assert inaccessible.status_code == absent.status_code == malformed.status_code == 404
    assert inaccessible.content == absent.content == malformed.content

    # Assert rendered body passes positive VM-22 minimization validator
    validate_denied_page_minimization(inaccessible.text)

    # Assert specific identifying facts are absent
    for leak in (str(theirs), str(mine), "Someone Elses", "Alia Storm"):
        assert leak not in inaccessible.text, f"Identifying fact '{leak}' leaked into denial response"


# ===========================================================================
# 3. Non-database structural test: Teardown fixture order and contract (R1)
# ===========================================================================

def test_teardown_order_positive() -> None:
    """R1: Verify real clean_between_cases fixture executes cleanup strictly after yield."""
    validate_database_teardown_fixture(clean_between_cases)


# ===========================================================================
# 4. Adversarial autoescaping checks across all user-influenced fields
# ===========================================================================

@pytest.mark.parametrize(
    "probe",
    [
        "<script>alert('xss')</script>",
        '"><img src=x onerror=alert(1)>',
        "{{ 7 * 7 }}",
        '"><script>alert(document.cookie)</script>',
        "A" * 300,
        "\u202Ereversed\u202C",
        "e\u0301cole",  # NFD
        "école",        # NFC
    ],
)
def test_adversarial_probes_render_inert_across_views(probe: str) -> None:
    """TC-UI-06: Adversarial probes in user-influenced fields render inert with autoescaping."""
    env = get_jinja_env()

    # 1. Login provider display name
    vm_login = LoginPageView(
        state="ready",
        providers=(ProviderOption(key="p1", display_name=probe, start_path="/v1/auth/start", enabled=True),),
        emergency_access_available=False,
    )
    rendered_login = env.get_template("login.html").render(view=vm_login, request=make_request())
    assert "<script>" not in rendered_login
    assert "<img src=x" not in rendered_login
    if "<script" in probe:
        assert "&lt;script" in rendered_login
    if "<img" in probe:
        assert "&lt;img" in rendered_login

    # 2. Non-member guild display name
    vm_non_member = NonMemberView(
        state="denied",
        reason=DeniedReason(category=DenialCategory.NOT_A_MEMBER),
        guild_display_name=probe,
        checked_at=Instant(iso_utc="2026-08-20T00:00:00Z", display=probe),
        correlation=Correlation(id=uuid4()),
    )
    rendered_nm = env.get_template("non_member.html").render(view=vm_non_member, request=make_request())
    assert "<script>" not in rendered_nm
    assert "<img src=x" not in rendered_nm

    # 3. Validation field error
    vm_val = ValidationView(
        state="invalid",
        form=object(),
        errors=(FieldError(field=probe, code="malformed"),),
    )
    rendered_val = env.get_template("validation.html").render(view=vm_val, request=make_request())
    assert "<script>" not in rendered_val
    assert "<img src=x" not in rendered_val


# ===========================================================================
# 5. Untouched template preservation & full template corpus security
# ===========================================================================

def test_non_step_4_templates_remain_byte_identical() -> None:
    """14. All 15 non-Step-4 child/fragment templates match expected immutable implementation hashes."""
    for filename, expected_sha in NON_STEP_4_TEMPLATE_DIGESTS.items():
        template_path = TEMPLATE_ROOT / filename
        assert template_path.is_file(), f"Non-Step-4 template '{filename}' missing"
        actual_sha = compute_sha256(template_path)
        assert actual_sha == expected_sha, (
            f"Digest mismatch on non-Step-4 template '{filename}': expected {expected_sha}, got {actual_sha}"
        )


# ===========================================================================
# 6. Falsifications through shared production validators
# ===========================================================================

def test_falsification_r09_extra_field_fails() -> None:
    """Falsification: Adding an unexpected field (e.g. csrf_token) to R-09 fails recovery validator."""
    env = get_jinja_env()
    vm = EmergencyLoginView(state="ready", webauthn_supported_hint=True, recovery_form_available=True)
    rendered = env.get_template("emergency.html").render(view=vm, request=make_request())
    mutated = rendered.replace(
        'name="token"',
        'name="token"><input type="hidden" name="csrf_token" value="abc"',
    )

    with pytest.raises(AssertionError, match=r"R-09 recovery form named fields must be exactly \{'token'\}"):
        validate_r09_recovery_form(mutated)


def test_falsification_emergency_form_rendered_when_unavailable_fails() -> None:
    """Falsification (F3): Injecting a recovery form when recovery_form_available=False fails availability validator."""
    env = get_jinja_env()
    vm = EmergencyLoginView(state="ready", webauthn_supported_hint=False, recovery_form_available=False)
    rendered = env.get_template("emergency.html").render(view=vm, request=make_request())
    # Mutate to force a recovery form into the unavailable recovery section
    mutated = rendered.replace(
        "<p>Recovery token sign-in is not available.</p>",
        '<form method="post" action="/v1/auth/emergency/recovery"><input name="token" type="password" required></form>',
    )

    with pytest.raises(AssertionError, match=r"Recovery form must not be present when recovery_form_available is False"):
        validate_emergency_page_availability(mutated, webauthn_expected=False, recovery_expected=False)


def test_falsification_denied_correlation_leak_fails() -> None:
    """Falsification: Adding a correlation reference to VM-22 fails minimization validator."""
    env = get_jinja_env()
    vm = DeniedView(state="denied", reason=DeniedReason(category=DenialCategory.NOT_AVAILABLE))
    rendered = env.get_template("denied.html").render(view=vm, request=make_request())
    mutated = rendered.replace(
        "This is not available to you.",
        f"This is not available to you. Reference {uuid4()}.",
    )

    with pytest.raises(AssertionError, match=r"Prohibited UUID/correlation disclosure found in VM-22"):
        validate_denied_page_minimization(mutated)


def test_falsification_validation_broken_anchor_fails() -> None:
    """Falsification: Adding a broken fragment link to validation view fails anchor validator."""
    env = get_jinja_env()
    vm = ValidationView(state="invalid", form=object(), errors=(FieldError(field="f", code="required"),))
    rendered = env.get_template("validation.html").render(view=vm, request=make_request())
    mutated = rendered.replace('class="validation-summary"', 'class="validation-summary"><a href="#nonexistent-target">Jump</a>')

    with pytest.raises(AssertionError, match=r"Broken fragment target link #nonexistent-target in validation view"):
        validate_validation_page_anchors(mutated)


def test_falsification_teardown_before_yield_rejected() -> None:
    """Falsification (R1): Moving cleanup before yield fails teardown validator."""
    def bad_fixture_cleanup_before_yield(request):
        if "migrated_database" in request.fixturenames:
            engine = request.getfixturevalue("migrated_database")
            with engine.begin() as connection:
                clean_p3_2_tables(connection)
        yield

    with pytest.raises(AssertionError, match=r"Teardown cleanup must occur after yield, not before yield"):
        validate_database_teardown_fixture(bad_fixture_cleanup_before_yield)


def test_falsification_teardown_missing_rejected() -> None:
    """Falsification (R1): Missing post-test cleanup fails teardown validator."""
    def bad_fixture_no_cleanup(request):
        yield

    with pytest.raises(AssertionError, match=r"Post-test database teardown was not executed after yield"):
        validate_database_teardown_fixture(bad_fixture_no_cleanup)
