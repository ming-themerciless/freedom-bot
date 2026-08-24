"""Tests for P3.5 Frontend Completion (F-15 WebAuthn Emergency Sign-in & F-17 Shell Presentation).

Verifies:
1. Truthful progressive enhancement and accessible UI elements in emergency.html (G35-01)
2. CSP-compliant visibility mutation: zero style attributes and zero .style/cssText mutation (G35-02)
3. Constrained refusal presentation and non-enumeration guarantees (G35-03)
4. Server-owned shell navigation and logout form presentation and accessibility (G35-06)
5. Static asset integrity manifest, content fingerprints, and base template wiring
6. Structural security guards and falsification tests
"""

import hashlib
import re
from pathlib import Path
from bs4 import BeautifulSoup
import jinja2
import pytest

from application.web.view_models import EmergencyLoginView
from application.web.shell import ShellView, ShellLink, ShellNav

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = ROOT / "adapters" / "web" / "templates"
STATIC_DIR = ROOT / "adapters" / "web" / "static"
MANIFEST_PATH = STATIC_DIR / "asset-integrity.sha256"


def get_jinja_env() -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
        undefined=jinja2.StrictUndefined,
    )


# ===========================================================================
# 1. Template Structure and Progressive Enhancement (G35-01 & G35-02)
# ===========================================================================


def test_emergency_template_contains_truthful_progressive_enhancement_elements() -> None:
    """F-15 / G35-01: emergency.html renders no-JS safe initial state with hidden button."""
    env = get_jinja_env()
    template = env.get_template("emergency.html")

    view = EmergencyLoginView(
        state="ready",
        webauthn_supported_hint=True,
        recovery_form_available=True,
        failure=None,
    )
    rendered = template.render(view=view, shell=ShellView(authenticated=False, navigation=()))
    soup = BeautifulSoup(rendered, "html.parser")

    # 1. Button present but hidden initially via boolean attribute
    btn = soup.find(id="webauthn-signin-btn")
    assert btn is not None, "webauthn-signin-btn missing"
    assert btn.name == "button"
    assert btn.get("type") == "button"
    assert "form-submit" in btn.get("class", [])
    assert "auth-button-webauthn" in btn.get("class", [])
    assert btn.get("aria-describedby") == "webauthn-desc"
    assert btn.has_attr("hidden"), "Initial markup must have hidden attribute on WebAuthn button"
    assert "Use security key" in btn.get_text()

    # 2. No-JS fallback message present and visible (not hidden)
    fallback = soup.find(id="webauthn-fallback-msg")
    assert fallback is not None, "webauthn-fallback-msg missing"
    assert not fallback.has_attr("hidden"), "Fallback message must be visible without JavaScript"
    assert "requires browser script support" in fallback.get_text()

    # 3. Unsupported browser message present and hidden
    unsupported = soup.find(id="webauthn-unsupported-msg")
    assert unsupported is not None, "webauthn-unsupported-msg missing"
    assert unsupported.has_attr("hidden"), "Unsupported message must be hidden initially"

    # 4. Live status message container present and hidden
    status = soup.find(id="webauthn-status-msg")
    assert status is not None, "webauthn-status-msg missing"
    assert status.get("role") == "status"
    assert status.get("aria-live") == "polite"
    assert "auth-status-message" in status.get("class", [])
    assert status.has_attr("hidden"), "Status container must be hidden initially"

    # 5. Zero style attributes across the entire rendered template
    styled_elements = soup.find_all(lambda tag: tag.has_attr("style"))
    assert len(styled_elements) == 0, f"Found CSP-violating style attributes in: {styled_elements}"


def test_emergency_template_when_webauthn_hint_false() -> None:
    """F-15: When webauthn_supported_hint is False, sign-in button is not rendered."""
    env = get_jinja_env()
    template = env.get_template("emergency.html")

    view = EmergencyLoginView(
        state="ready",
        webauthn_supported_hint=False,
        recovery_form_available=True,
        failure=None,
    )
    rendered = template.render(view=view, shell=ShellView(authenticated=False, navigation=()))
    soup = BeautifulSoup(rendered, "html.parser")

    assert soup.find(id="webauthn-signin-btn") is None
    assert "Security key sign-in is not available." in rendered


def test_emergency_template_non_enumeration_invariants() -> None:
    """F-15 / VM-04: emergency.html never discloses user identity or credential counts."""
    env = get_jinja_env()
    template = env.get_template("emergency.html")

    view = EmergencyLoginView(
        state="ready",
        webauthn_supported_hint=True,
        recovery_form_available=True,
        failure=None,
    )
    rendered = template.render(view=view, shell=ShellView(authenticated=False, navigation=()))

    forbidden_terms = ["admin@", "user_id", "credential_id", "key_nickname", "enrolled_keys"]
    for term in forbidden_terms:
        assert term not in rendered.lower(), f"Potential enumeration oracle in emergency.html: {term}"


# ===========================================================================
# 2. Shell Navigation and Logout Presentation (F-17 & G35-06)
# ===========================================================================


def test_shell_header_logout_form_presentation_and_accessibility() -> None:
    """F-17: Header logout form provides accessible, semantic sign-out control."""
    env = get_jinja_env()
    template = env.get_template("includes/header.html")

    # Render authenticated shell
    shell = ShellView(
        authenticated=True,
        navigation=(ShellLink(id=ShellNav.CHARACTERS, label="Characters", href="/v1/characters"),),
        logout_csrf_token="test-csrf-token-12345",
        home_href="/v1/characters",
        current=ShellNav.CHARACTERS,
    )
    rendered = template.render(shell=shell)
    soup = BeautifulSoup(rendered, "html.parser")

    # Verify logout form
    form = soup.find("form", class_="nav-logout-form")
    assert form is not None, "nav-logout-form missing"
    assert form.get("method") == "post"
    assert form.get("action") == "/v1/auth/logout"

    # Verify CSRF token input
    csrf_input = form.find("input", {"name": "csrf_token"})
    assert csrf_input is not None, "csrf_token input missing from logout form"
    assert csrf_input.get("type") == "hidden"
    assert csrf_input.get("value") == "test-csrf-token-12345"

    # Verify button styling and text
    btn = form.find("button", class_="nav-logout")
    assert btn is not None, "nav-logout button missing"
    assert btn.get("type") == "submit"
    assert "Sign out" in btn.get_text()


# ===========================================================================
# 3. Static Asset Integrity and Structural CSP Guards (G35-02 & G35-05)
# ===========================================================================


def test_all_static_assets_match_manifest_and_fingerprints() -> None:
    """F-15/F-17: All static files in adapters/web/static match asset-integrity.sha256 exactly."""
    assert MANIFEST_PATH.is_file(), "asset-integrity.sha256 missing"
    manifest_lines = [
        line.strip()
        for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert len(manifest_lines) == 4, f"Expected 4 static assets in manifest, got {len(manifest_lines)}"

    asset_types_found = set()
    for line in manifest_lines:
        expected_sha, rel_path = line.split(maxsplit=1)
        target_path = ROOT / rel_path
        assert target_path.is_file(), f"Asset {rel_path} does not exist"

        actual_sha = hashlib.sha256(target_path.read_bytes()).hexdigest()
        assert actual_sha == expected_sha, f"SHA-256 mismatch for {rel_path}: {actual_sha} != {expected_sha}"

        # Check 12-hex fingerprint in filename
        filename = target_path.name
        if filename.endswith(".min.js"):
            stem = filename[:-7]
            fp = stem.split(".")[-1]
        else:
            fp = filename.rsplit(".", 2)[-2]
        assert len(fp) == 12 and all(c in "0123456789abcdef" for c in fp), f"Invalid fingerprint {fp} in {filename}"
        assert actual_sha.startswith(fp), f"Fingerprint {fp} does not match prefix of SHA-256 {actual_sha}"

        if rel_path.endswith(".css"):
            asset_types_found.add("css")
        elif rel_path.endswith(".png"):
            asset_types_found.add("image")
        elif "vendor/htmx" in rel_path:
            asset_types_found.add("vendor_js")
        elif "js/webauthn-emergency" in rel_path:
            asset_types_found.add("webauthn_js")

    assert asset_types_found == {"css", "image", "vendor_js", "webauthn_js"}


def test_base_template_references_exact_fingerprinted_assets() -> None:
    """F-15/F-17: base.html links exact fingerprinted CSS and JS assets from the manifest."""
    base_html = (TEMPLATES_DIR / "base.html").read_text(encoding="utf-8")
    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")

    # Extract CSS fingerprint
    css_match = re.search(r"adapters/web/static/css/freedom-blades\.([0-9a-f]{12})\.css", manifest_text)
    assert css_match, "CSS entry not found in manifest"
    css_fp = css_match.group(1)
    assert f"/static/css/freedom-blades.{css_fp}.css" in base_html

    # Extract WebAuthn JS fingerprint
    js_match = re.search(r"adapters/web/static/js/webauthn-emergency\.([0-9a-f]{12})\.js", manifest_text)
    assert js_match, "WebAuthn JS entry not found in manifest"
    js_fp = js_match.group(1)
    assert f"/static/js/webauthn-emergency.{js_fp}.js" in base_html


def test_javascript_client_contains_zero_inline_style_or_eval_mutations() -> None:
    """G35-02 / G35-04: webauthn-emergency script contains no style mutation, eval, or dangerous sinks."""
    js_files = list((STATIC_DIR / "js").glob("webauthn-emergency.*.js"))
    assert len(js_files) == 1
    js_text = js_files[0].read_text(encoding="utf-8")

    # Forbidden style mutations
    assert ".style" not in js_text, "Found .style mutation in client script"
    assert "cssText" not in js_text, "Found cssText mutation in client script"
    assert "setAttribute('style'" not in js_text and 'setAttribute("style"' not in js_text

    # Forbidden execution sinks
    assert "eval(" not in js_text
    assert "innerHTML" not in js_text
    assert "outerHTML" not in js_text
    assert "document.write" not in js_text


def test_css_contains_webauthn_and_logout_presentation_rules() -> None:
    """F-15/F-17: Stylesheet defines rules for WebAuthn controls and navigation logout."""
    css_files = list((STATIC_DIR / "css").glob("freedom-blades.*.css"))
    assert len(css_files) == 1
    css_text = css_files[0].read_text(encoding="utf-8")

    required_selectors = [
        "[hidden]",
        ".nav-logout-form",
        ".nav-logout",
        ".auth-webauthn-actions",
        ".auth-button-webauthn",
        ".auth-status-message",
        ".auth-status-message.is-error",
        ".auth-status-message.is-info",
    ]
    for sel in required_selectors:
        assert sel in css_text, f"CSS missing required rule for {sel}"

    # Focus-visible and accessible states present
    assert ":focus-visible" in css_text
    assert "@media (prefers-reduced-motion" in css_text


def test_javascript_client_structural_security_guards() -> None:
    """G36-03: Structural guards verifying zero cookies, storage, logging, dataset, or URL leaks."""
    js_files = list((STATIC_DIR / "js").glob("webauthn-emergency.*.js"))
    assert len(js_files) == 1
    js_text = js_files[0].read_text(encoding="utf-8")

    # Prohibit cookies and storage
    assert "document.cookie" not in js_text
    assert "localStorage" not in js_text
    assert "sessionStorage" not in js_text

    # Prohibit logging primitives
    assert "console." not in js_text

    # Prohibit dataset / DOM data attribute writes
    assert ".dataset" not in js_text
    assert "setAttribute('data-" not in js_text and 'setAttribute("data-' not in js_text

    # Only R-07 and R-08 endpoints
    fetch_matches = re.findall(r"fetchFn\(\s*['\"]([^'\"]+)['\"]", js_text)
    assert set(fetch_matches) == {
        "/v1/auth/emergency/webauthn/options",
        "/v1/auth/emergency/webauthn/verify",
    }
