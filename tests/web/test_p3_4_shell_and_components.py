"""Tests and production validation helpers for P3.4 Step 3 and Step 4: shared shell, design system, and auth templates.

Remediated per Phase 3 Step 4 Remediation 03 (R3):
- Implemented robust CSS comment stripping (strip_css_comments) with unterminated comment safety.
- Refactored validate_step4_selectors_usage to parse active class selectors outside declaration blocks
  and after stripping CSS block comments.
- Added parameterized falsifications for comment-only mentions (single-line, multiline, prose), longer class
  names (.auth-card-extra), and declaration values (content: ".auth-card"), asserting the exact required failure message:
  "Selector '.auth-card' is not defined as an active CSS class selector in stylesheet".
- Added positive probes for real active selectors, surrounding comments, and multiple unrelated comments.
- Added falsification for unterminated block comments.
- Retained token-aware template matching, .auth-lead usage falsification, later-step selector falsification,
  child template digest protections, and all shell/security guards.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
import jinja2
import pytest
from starlette.requests import Request

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = ROOT / "adapters" / "web" / "templates"
STATIC_ROOT = ROOT / "adapters" / "web" / "static"
MANIFEST_PATH = STATIC_ROOT / "asset-integrity.sha256"
VISUAL_FREEZE_MANIFEST = ROOT / "docs" / "review" / "phase-3-visual-freeze-manifest.sha256"

FRAGMENT_TEMPLATES: frozenset[str] = frozenset({
    "audit_results.html",
    "identity_search.html",
    "job_status_fragment.html",
})

from tests.web.template_digests import (
    P3_4_IMPLEMENTATION_INCLUDE_DIGESTS,
    P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS,
)


# Step 4 Authorized & Actually Used Selectors (must be used in templates)
STEP_4_SELECTORS: tuple[str, ...] = (
    ".auth-wrapper",
    ".auth-card",
    ".auth-title",
    ".auth-actions",
    ".auth-provider-link",
    ".auth-provider-disabled",
    ".auth-emergency-link",
    ".auth-links",
    ".auth-meta",
    ".reference-code",
    ".auth-section",
    ".auth-form",
    ".form-group",
    ".form-label",
    ".form-input",
    ".form-submit",
    ".validation-summary",
    ".validation-list",
    ".validation-item",
    ".validation-field",
    ".validation-code",
    ".validation-limit",
    ".conflict-details",
    ".conflict-scope-info",
)

# Prohibited Later-Step Selectors (Step 7+)
PROHIBITED_LATER_STEP_SELECTORS: tuple[str, ...] = (
    ".user-status-pill",
    ".user-avatar",
    ".mobile-menu-btn",
    ".char-portrait-thumb",
    ".char-portrait-hero",
    ".avatar-portrait-fallback",
    ".char-card-media",
    ".char-card-portrait",
    ".char-card-body",
    ".profile-identity-group",
    ".profile-freshness-block",
    ".progress-bar-track",
    ".progress-bar-fill",
    ".progress-step-row",
    ".progress-step-card",
    ".step-number",
    ".step-title",
    ".diff-container",
    ".diff-box",
    ".diff-title",
    ".dialog-overlay",
    ".dialog-box",
    ".dialog-header",
    ".dialog-footer",
    ".dialog-close-btn",
    ".htmx-indicator",
    ".htmx-request",
    ".council-console-card",
)


def get_jinja_env(template_dir: Path = TEMPLATE_ROOT) -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        autoescape=True,
        undefined=jinja2.StrictUndefined,
    )


def make_request(path: str = "/v1/characters") -> Request:
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


def strip_jinja_comments(template_text: str) -> str:
    """Strip Jinja {# ... #} comments to inspect active template code."""
    return re.sub(r"\{#.*?#\}", "", template_text, flags=re.DOTALL)


def strip_css_comments(css_text: str) -> str:
    """Strip CSS block comments /* ... */ across lines and fail safely on unterminated comments (R3)."""
    pos = 0
    result_parts: list[str] = []
    while pos < len(css_text):
        start = css_text.find("/*", pos)
        if start == -1:
            result_parts.append(css_text[pos:])
            break
        result_parts.append(css_text[pos:start])
        end = css_text.find("*/", start + 2)
        assert end != -1, "Unterminated CSS block comment detected in stylesheet"
        pos = end + 2
    return "".join(result_parts)


def remove_css_rule(css_text: str, selector: str) -> str:
    """Helper to remove a specific selector's rule block from CSS text in-memory."""
    pattern = rf"(?m)^\s*{re.escape(selector)}\s*\{{[^}}]*\}}\s*"
    return re.sub(pattern, "", css_text)


# ===========================================================================
# Production Validation Helpers (Used by both positive and negative tests)
# ===========================================================================

def validate_child_templates_preservation(templates_dir: Path) -> None:
    """Validator: asserts all 23 templates exist with exact SHA-256 and extend base."""
    found_templates = {
        p.name: compute_sha256(p)
        for p in templates_dir.glob("*.html")
        if p.name != "base.html"
    }

    # 1. Exact set equality
    expected_names = set(P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS.keys())
    actual_names = set(found_templates.keys())
    assert actual_names == expected_names, (
        f"Child template set mismatch: extra={actual_names - expected_names}, missing={expected_names - actual_names}"
    )

    # 2. Exact digest equality for every template
    for name, expected_sha in sorted(P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS.items()):
        actual_sha = found_templates[name]
        assert actual_sha == expected_sha, (
            f"Digest mismatch for template '{name}': expected {expected_sha}, got {actual_sha}"
        )

    # 3. Structural inheritance check for page templates vs fragments
    for name in actual_names:
        content = (templates_dir / name).read_text(encoding="utf-8")
        if name in FRAGMENT_TEMPLATES:
            continue
        assert '{% extends "base.html" %}' in content or "{% extends 'base.html' %}" in content, (
            f"Page template '{name}' must extend base.html"
        )


def validate_shared_includes_preservation(templates_dir: Path) -> None:
    """Validator: asserts shared includes (header, footer) and base shell match exact SHA-256 digests."""
    for rel_path, expected_sha in sorted(P3_4_IMPLEMENTATION_INCLUDE_DIGESTS.items()):
        target_file = templates_dir / rel_path
        assert target_file.is_file(), f"Expected include/base file '{rel_path}' does not exist"
        actual_sha = compute_sha256(target_file)
        assert actual_sha == expected_sha, (
            f"Digest mismatch for include/base '{rel_path}': expected {expected_sha}, got {actual_sha}"
        )


def validate_landmark_order_and_skip_link(rendered_html: str) -> None:
    """Validator: landmark order, unique main-content target, and first focusable skip link."""
    body_idx = rendered_html.find("<body")
    assert body_idx != -1, "Missing <body> tag"
    after_body = rendered_html[body_idx:]

    # Skip link existence
    skip_link_match = re.search(r'<a\s+href="#main-content"\s+class="skip-link">([^<]+)</a>', after_body)
    assert skip_link_match, "Missing skip link targeting #main-content"
    skip_link_pos = after_body.find(skip_link_match.group(0))

    # Skip link must be the very first focusable element inside body
    first_focusable = re.search(r'<(a|button|input|select|textarea|summary)\b', after_body)
    assert first_focusable is not None, "No focusable elements found in body"
    assert first_focusable.start() == skip_link_pos, (
        f"Skip link must be the very first focusable element inside body, but found <{first_focusable.group(1)}> before it"
    )

    # Landmark existence and order
    header_pos = rendered_html.find("<header")
    nav_pos = rendered_html.find("<nav")
    main_pos = rendered_html.find('<main id="main-content"')
    footer_pos = rendered_html.find("<footer")

    assert header_pos != -1, "Missing <header> landmark"
    assert nav_pos != -1, "Missing <nav> landmark"
    assert main_pos != -1, "Missing <main id=\"main-content\"> landmark"
    assert footer_pos != -1, "Missing <footer> landmark"
    assert header_pos < nav_pos < main_pos < footer_pos, (
        f"Incorrect landmark order: header({header_pos}) -> nav({nav_pos}) -> main({main_pos}) -> footer({footer_pos})"
    )

    # Unique main target id
    assert rendered_html.count('id="main-content"') == 1, (
        f"Target id 'main-content' missing or not unique (count={rendered_html.count('id=\"main-content\"')})"
    )


def validate_aria_current_uniqueness(
    rendered_header: str,
    expected_active_text: str | None = None,
    *,
    expected_count: int = 1,
) -> None:
    """Validator: exactly one nav link has aria-current='page' (matching text if given), or expected_count."""
    current_count = rendered_header.count('aria-current="page"')
    if expected_count == 1:
        assert current_count == 1, (
            f"Expected exactly one aria-current='page', found {current_count}"
        )
    else:
        assert current_count == expected_count, (
            f"Expected exactly {expected_count} aria-current='page', found {current_count}"
        )

    if expected_count > 0 and expected_active_text is not None:
        match = re.search(r'<a\s+[^>]*aria-current="page"[^>]*>([^<]+)</a>', rendered_header)
        assert match, "Could not extract link text for aria-current='page'"
        active_text = match.group(1).strip()
        assert active_text == expected_active_text, (
            f"Expected active nav item '{expected_active_text}', got '{active_text}'"
        )


def validate_template_security_rules(rel_name: str, raw_content: str) -> None:
    """Validator: enforces TC-UI-06 (no |safe, no hx-on:, no inline event handlers, no remote origins/fonts, no inline script)."""
    # 1. |safe filter check
    assert not re.search(r"\|\s*safe\b", raw_content), (
        f"Forbidden '|safe' filter in {rel_name}"
    )

    # 2. Check active template code (excluding Jinja comments)
    active_code = strip_jinja_comments(raw_content)

    # B1: Reject ordinary HTML inline event handler attributes (e.g. onclick=, onerror =, ONLOAD=)
    handler_match = re.search(r"(?i)\b(on[a-z]+)\s*=", active_code)
    assert not handler_match, (
        f"Forbidden inline event handler attribute '{handler_match.group(1)}' in {rel_name}"
    )

    # Reject HTMX inline handlers
    assert "hx-on:" not in active_code, f"Forbidden 'hx-on:' attribute in {rel_name}"
    assert "data-hx-on:" not in active_code, f"Forbidden 'data-hx-on:' in {rel_name}"

    # Reject prototype references and remote URLs / fonts
    assert "design-prototype" not in active_code, f"Forbidden 'design-prototype' reference in {rel_name}"
    assert "http://" not in active_code, f"Forbidden 'http://' reference in {rel_name}"
    assert "https://" not in active_code, f"Forbidden 'https://' reference in {rel_name}"
    assert "fonts.googleapis.com" not in active_code, f"Forbidden remote font in {rel_name}"

    # Inline executable script tags check
    scripts = re.findall(r"<script\b([^>]*)>(.*?)</script>", active_code, flags=re.DOTALL)
    for attrs, body in scripts:
        assert 'src="/static/' in attrs, f"Inline or non-static script in {rel_name}: {attrs}"
        assert not body.strip(), f"Inline script body not allowed in {rel_name}: {body}"


def validate_base_includes(base_content: str) -> None:
    """Validator: verifies static includes and rejects dynamic or ignore-missing includes."""
    # 1. Reject 'ignore missing'
    assert "ignore missing" not in base_content, "Forbidden 'ignore missing' directive in base template"

    # 2. Reject dynamic include expressions (e.g. {% include some_var %})
    include_tags = re.findall(r"\{%\s*include\s+([^%]+)%\}", base_content)
    for tag in include_tags:
        cleaned = tag.strip().split()[0] if tag.strip() else ""
        assert cleaned.startswith(('"', "'")), f"Dynamic include expression detected: '{cleaned}'"

    # 3. Verify exact static include tags exist
    assert '{% include "includes/header.html" %}' in base_content or "{% include 'includes/header.html' %}" in base_content, (
        "Missing static include for header.html"
    )
    assert '{% include "includes/footer.html" %}' in base_content or "{% include 'includes/footer.html' %}" in base_content, (
        "Missing static include for footer.html"
    )


def validate_no_unsupported_head_extra_block(base_content: str) -> None:
    """Validator (F2): verifies unneeded head_extra block is absent while retaining title and content blocks."""
    assert "head_extra" not in base_content, "Forbidden unsupported 'head_extra' block in base.html"
    assert "{% block title %}" in base_content, "Missing required 'title' block in base.html"
    assert "{% block content %}" in base_content, "Missing required 'content' block in base.html"


def validate_css_fingerprint(css_path: Path) -> None:
    """Validator: asserts CSS filename fingerprint equals first 12 lowercase hex of content SHA-256."""
    name = css_path.name
    match = re.match(r"^freedom-blades\.([0-9a-f]{12})\.css$", name)
    assert match, f"Invalid CSS filename format: {name}"
    expected_fp = match.group(1)
    actual_sha = compute_sha256(css_path)
    assert actual_sha[:12] == expected_fp, (
        f"Fingerprint mismatch in {name}: filename has {expected_fp}, actual SHA-256 begins with {actual_sha[:12]}"
    )


def validate_manifest_integrity(manifest_path: Path, resolution_root: Path) -> None:
    """Validator (B2): asserts all entries in asset-integrity.sha256 match file digests under resolution_root."""
    manifest_text = manifest_path.read_text(encoding="utf-8")
    lines = [
        line.strip() for line in manifest_text.splitlines()
        if line.strip() and not line.startswith("#")
    ]
    assert len(lines) >= 3, f"Manifest must contain at least 3 asset entries, found {len(lines)}"

    for line in lines:
        parts = line.split(maxsplit=1)
        assert len(parts) == 2, f"Invalid manifest entry: '{line}'"
        expected_sha, rel_path = parts[0], parts[1]
        target_file = resolution_root / rel_path
        assert target_file.is_file(), f"Manifest target file does not exist or is not a file: {target_file}"
        actual_sha = compute_sha256(target_file)
        assert actual_sha == expected_sha, (
            f"Manifest integrity check failed for '{rel_path}': expected {expected_sha}, got {actual_sha}"
        )


def validate_css_scope_and_primitives(css_text: str) -> None:
    """Validator (F2): enforces required foundation, shell, and Step 4 selectors, and rejects later-step selectors."""
    active_css = strip_css_comments(css_text)

    # 1. Step 2 Foundation Selectors
    for req in [
        ":root", "--fb-color-bg-base", ".skip-link", ":focus-visible",
        ".card", ".alert", ".table-container", ".fb-blade-divider",
        "prefers-reduced-motion",
    ]:
        assert req in active_css, f"Missing required foundation selector: {req}"

    # 2. Step 3 Shell Selectors
    for req in [
        ".app-header", ".app-header-top", ".brand-title", ".brand-emblem",
        ".app-navigation", ".nav-menu", ".nav-link", ".main-container",
        ".app-footer",
    ]:
        assert req in active_css, f"Missing required shell selector: {req}"

    # 3. Step 4 Actually Used Selectors (no .auth-lead)
    for sel in STEP_4_SELECTORS:
        assert sel in active_css, f"Missing required Step 4 selector: {sel}"

    # 4. Prohibited Unused Step 4 Selector (.auth-lead)
    assert ".auth-lead" not in active_css, "Prohibited unused Step 4 selector found in CSS: .auth-lead"

    # 5. Prohibited Later-Step Selectors (Step 5+)
    for prohibited in PROHIBITED_LATER_STEP_SELECTORS:
        assert prohibited not in active_css, f"Prohibited later-step selector found in CSS: {prohibited}"


def validate_step4_selectors_usage(
    templates_dir: Path,
    css_text: str,
    selectors: tuple[str, ...] | set[str] | list[str] = STEP_4_SELECTORS,
) -> None:
    """Validator (R2/R3): proves every supplied Step 4 selector is defined in active CSS and used as an exact class token in Step 4 templates."""
    # 1. Strip CSS comments safely before validating active selector definitions
    active_css = strip_css_comments(css_text)

    # 2. Extract active class selectors from rule selector positions (outside declaration blocks { ... })
    active_class_selectors: set[str] = set()
    for match in re.finditer(r"([^{}]+)\{([^{}]*)\}", active_css):
        selector_group = match.group(1)
        for sel_part in selector_group.split(","):
            found_classes = re.findall(r"(?:\A|[^\w\-.])(\.[a-zA-Z0-9_\-]+)", sel_part)
            for cls in found_classes:
                active_class_selectors.add(cls)

    # 3. Collect all exact class attribute tokens from all 8 Step 4 templates (excluding Jinja comments)
    step4_template_names = [
        "login.html", "emergency.html", "non_member.html", "degraded.html",
        "denied.html", "conflict.html", "validation.html", "error.html",
    ]
    all_used_class_tokens: set[str] = set()
    for name in step4_template_names:
        raw_tmpl = (templates_dir / name).read_text(encoding="utf-8")
        active_code = strip_jinja_comments(raw_tmpl)
        class_attrs = re.findall(r'\bclass=["\']([^"\']+)["\']', active_code)
        for attr_val in class_attrs:
            for token in attr_val.split():
                all_used_class_tokens.add(token.strip())

    for sel in selectors:
        # A. Selector must be present as a real active CSS class selector in stylesheet
        assert sel in active_class_selectors, (
            f"Selector '{sel}' is not defined as an active CSS class selector in stylesheet"
        )

        # B. Exact class token must be used in at least one of the 8 Step 4 templates
        class_name = sel.lstrip(".")
        assert class_name in all_used_class_tokens, (
            f"Step 4 selector '{sel}' is not used by any of the eight Step 4 templates"
        )


# ===========================================================================
# Positive Test Suite
# ===========================================================================

def test_child_templates_preservation_positive() -> None:
    """1. All 23 child/fragment templates match implementation digests."""
    validate_child_templates_preservation(TEMPLATE_ROOT)


def test_shared_includes_preservation_positive() -> None:
    """1b. All shared includes (header, footer) and base shell match implementation digests."""
    validate_shared_includes_preservation(TEMPLATE_ROOT)


def test_base_references_exact_manifest_assets() -> None:
    """2. base.html references exactly the manifest-listed CSS, HTMX with defer, and emblem icon."""
    base_content = (TEMPLATE_ROOT / "base.html").read_text(encoding="utf-8")

    # Read manifest entries
    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    manifest_lines = [
        line.split() for line in manifest_text.splitlines()
        if line.strip() and not line.startswith("#")
    ]
    manifest_files = {parts[1]: parts[0] for parts in manifest_lines}

    # Verify CSS reference
    css_rel = [k for k in manifest_files if k.startswith("adapters/web/static/css/")][0]
    css_filename = Path(css_rel).name
    assert f'href="/static/css/{css_filename}"' in base_content

    # Verify emblem icon reference
    img_rel = [k for k in manifest_files if k.startswith("adapters/web/static/images/")][0]
    img_filename = Path(img_rel).name
    assert f'href="/static/images/{img_filename}"' in base_content

    # Verify HTMX reference with defer
    vendor_rel = [k for k in manifest_files if k.startswith("adapters/web/static/vendor/")][0]
    vendor_filename = Path(vendor_rel).name
    assert f'src="/static/vendor/{vendor_filename}"' in base_content
    assert re.search(rf'<script\s+defer\s+src="/static/vendor/{re.escape(vendor_filename)}"></script>', base_content), (
        "HTMX script tag must have 'defer' and no inline script"
    )

    # No remote origin or CDN
    assert "http://" not in base_content
    assert "https://" not in base_content


def test_asset_integrity_manifest_positive() -> None:
    """B2. Production asset-integrity manifest verifies successfully against production ROOT."""
    validate_manifest_integrity(MANIFEST_PATH, ROOT)


def test_landmark_order_and_skip_link_positive() -> None:
    """3 & 4. Landmark sequence: skip-link -> header -> nav -> main(#main-content) -> footer."""
    env = get_jinja_env()
    template = env.get_template("base.html")
    rendered = template.render(request=make_request("/v1/characters"))
    validate_landmark_order_and_skip_link(rendered)

    # Shell includes must NOT introduce an <h1> (each page owns its own <h1>)
    header_footer_only = env.get_template("includes/header.html").render(request=make_request()) + \
                         env.get_template("includes/footer.html").render(request=make_request())
    assert "<h1" not in header_footer_only, "Shared shell must not contain an <h1> tag"


@pytest.mark.parametrize(
    "path,expected_active_text,expected_count",
    [
        ("/v1/characters", "Characters", 1),
        ("/v1/characters/123e4567-e89b-12d3-a456-426614174000", "Characters", 1),
        ("/v1/auth/emergency", "Emergency Access", 1),
        ("/v1/auth/emergency/webauthn", "Emergency Access", 1),
        ("/v1/login", "Login", 1),
        ("/v1/auth/discord/start", "Login", 1),
        ("/", "Login", 1),
        # Unmapped/non-destination paths render zero current items on primary nav
        ("/v1/council/queue", None, 0),
        ("/v1/admin/audit-log", None, 0),
        ("/not-found", None, 0),
        ("/error", None, 0),
    ],
)
def test_aria_current_page_selection_positive(
    path: str, expected_active_text: str | None, expected_count: int
) -> None:
    """5. Exactly one nav item has aria-current='page' for matching paths, and zero for unmapped paths."""
    env = get_jinja_env()
    template = env.get_template("includes/header.html")
    rendered = template.render(request=make_request(path))
    validate_aria_current_uniqueness(
        rendered, expected_active_text=expected_active_text, expected_count=expected_count
    )


def test_shell_rendering_introduces_no_contextual_facts() -> None:
    """6. Shell introduces no username, guild, role, capability, emergency, or environment facts."""
    env = get_jinja_env()
    template = env.get_template("base.html")
    rendered = template.render(request=make_request("/v1/characters"))

    forbidden_terms = [
        "Synthetic Reviewer",
        "Discord",
        "Administrator",
        "Council Member",
        "Role",
        "Capability",
        "Break-glass active",
        "Emergency session",
        "Correlation ID",
        "Environment:",
    ]
    for term in forbidden_terms:
        assert term not in rendered, f"Forbidden contextual fact '{term}' found in shell rendering"


def test_templates_obey_security_rules_positive() -> None:
    """7 & 10. Entire template corpus obeys TC-UI-06 security rules."""
    for template_path in TEMPLATE_ROOT.rglob("*.html"):
        raw_content = template_path.read_text(encoding="utf-8")
        rel_name = str(template_path.relative_to(TEMPLATE_ROOT))
        validate_template_security_rules(rel_name, raw_content)


def test_security_rules_harmless_probes_pass_positive() -> None:
    """B1. Proves harmless non-handler text and attributes (e.g. nonce, on in text) do not raise false positives."""
    harmless_cases = [
        '<script nonce="rAnd0m123" src="/static/vendor/htmx-2.0.10.71ea67185bfa.min.js"></script>',
        '<p>This feature is on by default and handles onload documentation.</p>',
        '<div data-action="toggle-on">Enabled</div>',
        '<section class="accordion-item"></section>',
        '{# {% include "x.html" %} comment mentioning onclick="test" is safe #}',
        '<button type="button">Plain Button</button>',
    ]
    for i, snippet in enumerate(harmless_cases):
        validate_template_security_rules(f"harmless_probe_{i}.html", snippet)


def test_includes_are_static_positive() -> None:
    """11. Includes are static, without 'ignore missing' or dynamic filenames."""
    base_content = (TEMPLATE_ROOT / "base.html").read_text(encoding="utf-8")
    validate_base_includes(base_content)


def test_no_unsupported_head_extra_block_positive() -> None:
    """F2. base.html contains no unsupported head_extra block and retains required blocks."""
    base_content = (TEMPLATE_ROOT / "base.html").read_text(encoding="utf-8")
    validate_no_unsupported_head_extra_block(base_content)


def test_navigation_uses_ordinary_anchors_without_js_toggle() -> None:
    """8. Navigation is made from ordinary anchors with no JavaScript menu toggle."""
    header_content = (TEMPLATE_ROOT / "includes" / "header.html").read_text(encoding="utf-8")

    assert "<button" not in header_content, "Header must not have button elements (no JS mobile menu toggle)"
    assert "onclick" not in header_content
    assert "mobile-menu" not in header_content
    assert re.findall(r'<a\s+href="[^"]+"\s+class="nav-link', header_content), "Must contain standard nav-link anchors"


def test_css_scope_and_primitives_positive() -> None:
    """9. CSS contains permitted foundation/shell/auth selectors and no later-step component classes."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1
    css_path = css_files[0]
    validate_css_fingerprint(css_path)

    css_text = css_path.read_text(encoding="utf-8")
    validate_css_scope_and_primitives(css_text)
    validate_step4_selectors_usage(TEMPLATE_ROOT, css_text, STEP_4_SELECTORS)


def test_positive_css_comment_handling_probes() -> None:
    """R3: Positive probes proving real selector outside comments, surrounding comments, and multiple comments pass."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1
    prod_css = css_files[0].read_text(encoding="utf-8")

    # Probe 1: Real .auth-card { ... } outside comments is accepted (baseline check)
    validate_step4_selectors_usage(TEMPLATE_ROOT, prod_css, (".auth-card",))

    # Probe 2: Comments before and after a real selector do not hide it
    probe_2_css = prod_css + "\n/* Header comment before rule */\n.auth-card { padding: 2rem; }\n/* Footer comment after rule */\n"
    validate_step4_selectors_usage(TEMPLATE_ROOT, probe_2_css, (".auth-card",))

    # Probe 3: Multiple unrelated single-line and multiline comments do not affect active selector detection
    probe_3_css = (
        "/* Comment 1 */\n"
        + prod_css
        + "\n/* Multiline\n Unrelated\n Comment 2 */\n"
        + "/* Comment 3 */\n"
    )
    validate_step4_selectors_usage(TEMPLATE_ROOT, probe_3_css, STEP_4_SELECTORS)


# ===========================================================================
# Deterministic Falsification Test Suite (Exercising the real validators)
# ===========================================================================

def test_falsification_1a_skip_link_target_missing() -> None:
    """Falsification 1a: Removing skip-link target #main-content fails landmark validator."""
    env = get_jinja_env()
    rendered = env.get_template("base.html").render(request=make_request())
    mutated = rendered.replace('id="main-content"', 'id="other-content"')

    with pytest.raises(AssertionError, match=r"Missing <main id=\"main-content\"> landmark"):
        validate_landmark_order_and_skip_link(mutated)


def test_falsification_1b_skip_link_moved_after_focusable_element() -> None:
    """Falsification 1b: Moving skip link after another focusable element fails validator."""
    env = get_jinja_env()
    rendered = env.get_template("base.html").render(request=make_request())
    # Prepend another anchor before the skip link inside body
    mutated = rendered.replace("<body>", '<body><a href="/other">Early focusable link</a>')

    with pytest.raises(AssertionError, match=r"Skip link must be the very first focusable element inside body"):
        validate_landmark_order_and_skip_link(mutated)


def test_falsification_1c_reversed_landmark_order() -> None:
    """Falsification 1c: Swapping landmark positions fails landmark order check."""
    env = get_jinja_env()
    rendered = env.get_template("base.html").render(request=make_request())
    # Move footer before main
    mutated = rendered.replace('<main id="main-content"', '<footer class="app-footer"></footer><main id="main-content"')

    with pytest.raises(AssertionError, match=r"Incorrect landmark order"):
        validate_landmark_order_and_skip_link(mutated)


def test_falsification_2_multiple_aria_current_detected() -> None:
    """Falsification 2: Adding a second aria-current='page' fails uniqueness validator."""
    env = get_jinja_env()
    rendered = env.get_template("includes/header.html").render(request=make_request("/v1/characters"))
    mutated = rendered.replace('class="nav-link nav-link-login"', 'class="nav-link nav-link-login" aria-current="page"')

    with pytest.raises(AssertionError, match=r"Expected exactly one aria-current='page', found 2"):
        validate_aria_current_uniqueness(mutated)


@pytest.mark.parametrize(
    "bad_snippet,expected_attr",
    [
        ('<button onclick="alert(1)">x</button>', "onclick"),
        ('<img src="/icon.png" onerror = "handleError()">', "onerror"),
        ('<body ONLOAD=\'initializePage()\'>', "ONLOAD"),
        ('<div onMouseOver="doHover()"></div>', "onMouseOver"),
        ('<input type="text" onfocus="handleFocus()">', "onfocus"),
    ],
)
def test_falsification_3_inline_event_handlers_rejected(bad_snippet: str, expected_attr: str) -> None:
    """Falsification 3 (B1): Inline HTML event handlers are rejected with specific attribute reason."""
    with pytest.raises(AssertionError, match=rf"Forbidden inline event handler attribute '{re.escape(expected_attr)}' in test\.html"):
        validate_template_security_rules("test.html", bad_snippet)


def test_falsification_3_forbidden_patterns_detected() -> None:
    """Falsification 3: Each forbidden corpus class fails security validator with exact error."""
    # 3a: |safe filter
    with pytest.raises(AssertionError, match=r"Forbidden '\|safe' filter"):
        validate_template_security_rules("test.html", "<div>{{ value | safe }}</div>")

    # 3b: hx-on: inline handler
    with pytest.raises(AssertionError, match=r"Forbidden 'hx-on:' attribute"):
        validate_template_security_rules("test.html", '<button hx-on:click="doSomething()">Click</button>')

    # 3c: Remote origin (https://)
    with pytest.raises(AssertionError, match=r"Forbidden 'https://' reference"):
        validate_template_security_rules("test.html", '<link rel="stylesheet" href="https://cdn.example.com/style.css">')

    # 3d: Remote Google font
    with pytest.raises(AssertionError, match=r"Forbidden remote font"):
        validate_template_security_rules("test.html", '<link href="fonts.googleapis.com/css2" rel="stylesheet">')

    # 3e: design-prototype reference
    with pytest.raises(AssertionError, match=r"Forbidden 'design-prototype' reference"):
        validate_template_security_rules("test.html", '<img src="design-prototype/assets/token.png">')

    # 3f: Inline executable script tag
    with pytest.raises(AssertionError, match=r"Inline or non-static script"):
        validate_template_security_rules("test.html", '<script>alert(1);</script>')


def test_falsification_4a_ignore_missing_include() -> None:
    """Falsification 4a: Adding 'ignore missing' to includes fails include validator."""
    base_content = (TEMPLATE_ROOT / "base.html").read_text(encoding="utf-8")
    mutated = base_content.replace('{% include "includes/footer.html" %}', '{% include "includes/footer.html" ignore missing %}')

    with pytest.raises(AssertionError, match=r"Forbidden 'ignore missing' directive in base template"):
        validate_base_includes(mutated)


def test_falsification_4b_dynamic_include_detected() -> None:
    """Falsification 4b: Adding dynamic include variable fails include validator."""
    base_content = (TEMPLATE_ROOT / "base.html").read_text(encoding="utf-8")
    mutated = base_content.replace('{% include "includes/header.html" %}', '{% include dynamic_header_var %}')

    with pytest.raises(AssertionError, match=r"Dynamic include expression detected: 'dynamic_header_var'"):
        validate_base_includes(mutated)


def test_falsification_5_css_byte_tampering_fails_fingerprint_and_manifest(tmp_path: Path) -> None:
    """Falsification 5 (B2): CSS byte tampering strictly fails manifest integrity and fingerprint validators."""
    # 1. Create bounded temporary root containing identical repository-relative files named in manifest
    tmp_root = tmp_path / "repo"
    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    manifest_lines = [
        line.strip() for line in manifest_text.splitlines()
        if line.strip() and not line.startswith("#")
    ]
    for line in manifest_lines:
        rel_path = line.split(maxsplit=1)[1]
        source_file = ROOT / rel_path
        dest_file = tmp_root / rel_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        dest_file.write_bytes(source_file.read_bytes())

    # 2. Copy production manifest without changing any digest or path
    temp_manifest = tmp_root / "adapters" / "web" / "static" / "asset-integrity.sha256"
    temp_manifest.write_bytes(MANIFEST_PATH.read_bytes())
    assert compute_sha256(temp_manifest) == compute_sha256(MANIFEST_PATH), "Copied manifest must be byte-identical"

    # 3. Confirm shared manifest helper passes against temporary root before mutation
    validate_manifest_integrity(temp_manifest, tmp_root)

    # 4. Append or alter one byte in temporary CSS only
    css_rel = [parts.split(maxsplit=1)[1] for parts in manifest_lines if parts.split(maxsplit=1)[1].endswith(".css")][0]
    temp_css = tmp_root / css_rel
    temp_css.write_bytes(temp_css.read_bytes() + b"\n/* falsification byte tamper */")

    # 5. Pass unchanged copied manifest and temporary root through shared helper; assert path-specific digest mismatch
    with pytest.raises(AssertionError, match=rf"Manifest integrity check failed for '{re.escape(css_rel)}'"):
        validate_manifest_integrity(temp_manifest, tmp_root)

    # 6. Independently pass mutated temporary CSS through fingerprint validator; assert fingerprint mismatch
    with pytest.raises(AssertionError, match=rf"Fingerprint mismatch in {re.escape(temp_css.name)}"):
        validate_css_fingerprint(temp_css)

    # 7. Prove production CSS and manifest hashes remain unchanged
    prod_css = ROOT / css_rel
    assert compute_sha256(prod_css) == "58a9b9eed003c44b0b4e63d25910ecd704cdac03b0dcea6d2e105d63b8756649"
    assert compute_sha256(MANIFEST_PATH) == "299a8a26ec64e862677e61e46cb432c632fc3d9dc48c29f0648dc03b9f31bf2b"


def test_falsification_f2_unsupported_head_extra_block_fails() -> None:
    """Falsification (F2): Introducing head_extra block fails F2 validator."""
    mutated_base = (TEMPLATE_ROOT / "base.html").read_text(encoding="utf-8") + "\n{% block head_extra %}{% endblock %}"
    with pytest.raises(AssertionError, match=r"Forbidden unsupported 'head_extra' block"):
        validate_no_unsupported_head_extra_block(mutated_base)


def test_falsification_f3_child_template_byte_mutation_fails(tmp_path: Path) -> None:
    """Falsification (F3): Mutating one byte of a child template fails preservation validator with digest mismatch."""
    # Copy all 23 templates to tmp_path
    for filename in P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS:
        source = TEMPLATE_ROOT / filename
        dest = tmp_path / filename
        dest.write_bytes(source.read_bytes())

    # Mutate 1 byte of account_identities.html in tmp_path
    target_path = tmp_path / "account_identities.html"
    target_path.write_bytes(target_path.read_bytes() + b" ")

    with pytest.raises(AssertionError, match=r"Digest mismatch for template 'account_identities.html'"):
        validate_child_templates_preservation(tmp_path)


def test_falsification_later_step_css_selector_rejected() -> None:
    """Falsification (F2): Appending a representative later-step selector fails shared CSS scope validator."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1
    css_text = css_files[0].read_text(encoding="utf-8")

    mutated_css = css_text + "\n.char-portrait-hero { width: 120px; height: 120px; }\n"
    with pytest.raises(AssertionError, match=r"Prohibited later-step selector found in CSS: \.char-portrait-hero"):
        validate_css_scope_and_primitives(mutated_css)


def test_falsification_unused_step4_selector_rejected() -> None:
    """Falsification (R2): Passing an unused selector (.auth-lead) directly to validate_step4_selectors_usage fails."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1
    css_text = css_files[0].read_text(encoding="utf-8")

    mutated_css = css_text + "\n.auth-lead { font-size: 1rem; }\n"
    expanded_selectors = STEP_4_SELECTORS + (".auth-lead",)

    with pytest.raises(
        AssertionError,
        match=r"Step 4 selector '\.auth-lead' is not used by any of the eight Step 4 templates",
    ):
        validate_step4_selectors_usage(TEMPLATE_ROOT, mutated_css, expanded_selectors)


@pytest.mark.parametrize(
    "mutation_suffix",
    [
        # 1. Single-line CSS block comment
        "/* .auth-card { padding: 1rem; } */\n",
        # 2. Multiline CSS block comment
        "/*\n .auth-card {\n   padding: 1rem;\n }\n*/\n",
        # 3. Prose inside a CSS block comment
        "/* Note: .auth-card is the card container for login. */\n",
        # 4. Longer/different selector name (.auth-card-extra)
        ".auth-card-extra { padding: 1rem; }\n",
        # 5. Declaration/string value rather than selector
        'body { content: ".auth-card"; }\n',
    ],
)
def test_falsification_comment_or_non_selector_rejected(mutation_suffix: str) -> None:
    """Falsification (R3): Proves .auth-card is rejected when appearing only as a comment, prose, longer name, or value."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1
    prod_css = css_files[0].read_text(encoding="utf-8")

    # Remove real .auth-card rule from production CSS in memory
    css_without_rule = remove_css_rule(prod_css, ".auth-card")
    assert ".auth-card" not in strip_css_comments(css_without_rule), "Real .auth-card rule must be removed before test"

    # Append the comment/non-selector mutation
    mutated_css = css_without_rule + "\n" + mutation_suffix

    with pytest.raises(
        AssertionError,
        match=r"Selector '\.auth-card' is not defined as an active CSS class selector in stylesheet",
    ):
        validate_step4_selectors_usage(TEMPLATE_ROOT, mutated_css, (".auth-card",))


def test_falsification_unterminated_comment_rejected() -> None:
    """Falsification (R3): Unterminated CSS block comment fails safely with specific error."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1
    prod_css = css_files[0].read_text(encoding="utf-8")

    mutated_css = prod_css + "\n/* Unterminated comment block\n.auth-card { padding: 1rem; }\n"

    with pytest.raises(
        AssertionError,
        match=r"Unterminated CSS block comment detected in stylesheet",
    ):
        validate_step4_selectors_usage(TEMPLATE_ROOT, mutated_css, (".auth-card",))


def test_shared_include_digest_falsification_fails_on_mutation(tmp_path: Path) -> None:
    """Falsification: a 1-byte mutation to header.html fails include digest validation."""
    import shutil
    mock_templates = tmp_path / "templates"
    shutil.copytree(TEMPLATE_ROOT, mock_templates)

    # Clean verification passes
    validate_shared_includes_preservation(mock_templates)

    # Mutate header.html by 1 byte
    header_file = mock_templates / "includes" / "header.html"
    header_content = header_file.read_text(encoding="utf-8")
    header_file.write_text(header_content + "\n", encoding="utf-8")

    with pytest.raises(AssertionError, match="Digest mismatch for include/base 'includes/header.html'"):
        validate_shared_includes_preservation(mock_templates)
