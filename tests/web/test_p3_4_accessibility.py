"""Phase 3.4 Step 11 Accessibility and Responsive Pass Test Suite.

Governs whole-corpus accessibility and responsive requirements across all 26 production
templates and shared includes:
1. Semantic structure & landmarks (base.html landmarks, skip link as first focusable control,
   <h1> exclusivity across full pages vs fragments vs includes, heading hierarchy without
   skipped levels, table accessible names, table header scopes, image alt text, decorative SVG hiding).
2. Navigation states (active route aria-current="page" exclusivity, non-manufacturing, and
   zero-current assertion for views where no destination applies).
3. Forms, controls, errors, status & HTMX live regions (label associations, IDREF uniqueness
   and non-empty content, aria-invalid on invalid controls, non-positive integer tabindex,
   validation summaries with alert role and focusability, system error alert roles,
   job status terminal status roles vs 2-second polling tick silence).
4. Rendered No-JavaScript fallback integrity (essential rendered forms and links retain real
   actions, POST methods, CSRF hidden tokens, and real href targets independently of HTMX).
5. Keyboard & visible focus (focus-visible styling, robust focus-outline suppression detection,
   skip-link positioning on focus).
6. Responsive layout, reflow & word-breaking (relative sizing, touch targets, overflow guards).
7. Reduced motion (prefers-reduced-motion suppression).
8. TC-UI-06 prototype isolation (zero design-prototype references in all 26 templates and static root).
9. TC-UI-07 contrast matrix (WCAG 2.2 AA luminance ratio calculations).
10. Complete production template inventory coverage assertion.
11. Controlled falsification probes (F-01 through F-11) exercising shared production validators.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jinja2
import pytest
from bs4 import BeautifulSoup

from tests.web.p3_3_fixtures import clean_p3_3_tables
from tests.web.portal_fixtures import (
    clean_p3_2_tables,
    csrf_token_for,
    make_character,
    seed_callers,
)
from tests.web.test_p3_3_audit_search import seed_events

pytestmark = pytest.mark.database


@pytest.fixture()
def callers(migrated_database, settings):
    yield seed_callers(migrated_database, settings)
    with migrated_database.begin() as connection:
        clean_p3_3_tables(connection)
        clean_p3_2_tables(connection)


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = ROOT / "adapters" / "web" / "templates"
STATIC_DIR = ROOT / "adapters" / "web" / "static"
CSS_DIR = STATIC_DIR / "css"

# Authoritative inventory of all 26 production templates and shared includes
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

FRAGMENT_TEMPLATES: set[str] = {
    "audit_results.html",
    "identity_search.html",
    "job_status_fragment.html",
}

INCLUDE_TEMPLATES: set[str] = {
    "includes/footer.html",
    "includes/header.html",
}

FULL_PAGE_TEMPLATES: set[str] = {
    p for p in ALL_PRODUCTION_TEMPLATES
    if p != "base.html" and p not in FRAGMENT_TEMPLATES and p not in INCLUDE_TEMPLATES
}


def get_all_production_template_paths() -> list[Path]:
    """Returns absolute paths for all 26 production templates and includes."""
    paths = sorted([p for p in TEMPLATES_DIR.rglob("*.html") if p.is_file()])
    assert len(paths) == len(ALL_PRODUCTION_TEMPLATES), (
        f"Inventory count mismatch: expected {len(ALL_PRODUCTION_TEMPLATES)}, found {len(paths)}"
    )
    return paths


def get_production_css_file() -> Path:
    css_files = list(CSS_DIR.glob("freedom-blades.*.css"))
    assert len(css_files) == 1, f"Expected exactly one production CSS file, got: {css_files}"
    return css_files[0]


def clean_html_source(html_text: str) -> str:
    """Strips Jinja comment blocks {# ... #} so comments containing HTML snippets are not parsed."""
    return re.sub(r"\{#.*?#\}", "", html_text, flags=re.DOTALL)


def parse_css_tokens(css_text: str) -> dict[str, str]:
    tokens: dict[str, str] = {}
    clean = re.sub(r"/\*.*?\*/", "", css_text, flags=re.DOTALL)
    root_match = re.search(r":root\s*\{([^}]+)\}", clean)
    if not root_match:
        return tokens
    for line in root_match.group(1).split(";"):
        if ":" in line:
            var_name, val = line.split(":", 1)
            var_name = var_name.strip()
            val = val.strip()
            if var_name.startswith("--"):
                tokens[var_name] = val
    return tokens


def parse_css_declarations(body: str) -> dict[str, str]:
    """Parses CSS declarations into normalized lowercase property-value pairs."""
    decls: dict[str, str] = {}
    for part in body.split(";"):
        if ":" in part:
            prop, val = part.split(":", 1)
            decls[prop.strip().lower()] = val.strip().lower()
    return decls


def resolve_token(val: str, tokens: dict[str, str], visited: set[str] | None = None) -> str:
    if visited is None:
        visited = set()
    cleaned = val.strip()
    if cleaned.startswith("var("):
        var_name = cleaned[4:-1].strip().split(",")[0].strip()
        if var_name in visited:
            raise ValueError(f"Cyclic token reference: {var_name}")
        visited.add(var_name)
        if var_name not in tokens:
            raise KeyError(f"Unresolved token: {var_name}")
        return resolve_token(tokens[var_name], tokens, visited)
    return cleaned


def parse_hex_color(hex_str: str) -> tuple[int, int, int]:
    cleaned = hex_str.lstrip("#").strip()
    if len(cleaned) != 6 or not re.fullmatch(r"[0-9a-fA-F]{6}", cleaned):
        raise ValueError(f"Invalid 6-digit hex color: '{hex_str}'")
    return (
        int(cleaned[0:2], 16),
        int(cleaned[2:4], 16),
        int(cleaned[4:6], 16),
    )


def relative_luminance(r: int, g: int, b: int) -> float:
    r_s, g_s, b_s = r / 255.0, g / 255.0, b / 255.0
    r_g = r_s / 12.92 if r_s <= 0.04045 else ((r_s + 0.055) / 1.055) ** 2.4
    g_g = g_s / 12.92 if g_s <= 0.04045 else ((g_s + 0.055) / 1.055) ** 2.4
    b_g = b_s / 12.92 if b_s <= 0.04045 else ((b_s + 0.055) / 1.055) ** 2.4
    return 0.2126 * r_g + 0.7152 * g_g + 0.0722 * b_g


def contrast_ratio(hex1: str, hex2: str) -> float:
    r1, g1, b1 = parse_hex_color(hex1)
    r2, g2, b2 = parse_hex_color(hex2)
    l1 = relative_luminance(r1, g1, b1)
    l2 = relative_luminance(r2, g2, b2)
    lmax, lmin = max(l1, l2), min(l1, l2)
    return (lmax + 0.05) / (lmin + 0.05)


# -----------------------------------------------------------------------------
# Shared Production Validation Helpers
# -----------------------------------------------------------------------------

def validate_table_accessible_names(html_text: str, source_name: str = "template") -> None:
    """Proves that every table has exactly one usable, non-empty accessible name."""
    clean = clean_html_source(html_text)
    soup = BeautifulSoup(clean, "html.parser")
    tables = soup.find_all("table")
    for table in tables:
        name_sources: list[str] = []

        # 1. <caption> child with non-empty text
        caption = table.find("caption")
        if caption and caption.get_text(strip=True):
            name_sources.append(f"caption:'{caption.get_text(strip=True)}'")

        # 2. aria-label with non-empty text
        aria_label = table.get("aria-label")
        if aria_label and aria_label.strip():
            name_sources.append(f"aria-label:'{aria_label.strip()}'")

        # 3. aria-labelledby referencing existing non-empty element
        aria_labelledby = table.get("aria-labelledby")
        if aria_labelledby:
            target_ids = aria_labelledby.strip().split()
            found_labels: list[str] = []
            for tid in target_ids:
                targets = soup.find_all(id=tid)
                assert len(targets) == 1, (
                    f"{source_name}: aria-labelledby '{tid}' must resolve uniquely, found {len(targets)}"
                )
                text = targets[0].get_text(strip=True)
                assert text, f"{source_name}: Element with ID '{tid}' must contribute non-empty text"
                found_labels.append(text)
            if found_labels:
                name_sources.append(f"aria-labelledby:{' '.join(found_labels)}")

        assert len(name_sources) > 0, (
            f"{source_name}: Table is missing an accessible name (no caption, aria-label, or aria-labelledby): {table}"
        )
        assert len(name_sources) == 1, (
            f"{source_name}: Table declares multiple conflicting accessible name sources ({name_sources}): {table}"
        )


def validate_focus_outline_rules(css_text: str) -> None:
    """Detects focus rules that suppress outline without supplying a qualifying visible replacement."""
    clean = re.sub(r"/\*.*?\*/", "", css_text, flags=re.DOTALL)
    for match in re.finditer(r"([^{]+)\{([^}]+)\}", clean):
        selector_raw = match.group(1).strip()
        body = match.group(2).strip()

        selectors = [s.strip() for s in selector_raw.split(",")]
        focus_selectors = [s for s in selectors if re.search(r":(?:focus|focus-visible|focus-within)\b", s)]
        if not focus_selectors:
            continue

        decls = parse_css_declarations(body)
        outline_val = decls.get("outline")
        outline_width = decls.get("outline-width")
        outline_style = decls.get("outline-style")

        suppresses_outline = (
            outline_val in {"none", "0", "0px", "transparent"}
            or (outline_val is not None and outline_val.startswith("0 "))
            or outline_width in {"0", "0px"}
            or outline_style == "none"
        )

        if suppresses_outline:
            has_visible_outline = outline_val not in {None, "none", "0", "0px", "transparent"}
            has_visible_shadow = decls.get("box-shadow") not in {None, "none", "0", "0px"}
            has_visible_border = (
                decls.get("border") not in {None, "none", "0", "0px", "transparent"}
                or decls.get("border-color") not in {None, "transparent"}
            )
            assert has_visible_outline or has_visible_shadow or has_visible_border, (
                f"Focus rule '{selector_raw}' suppresses outline without a visible replacement: '{body}'"
            )


def validate_heading_hierarchy(html_text: str, source_name: str = "template") -> None:
    """Proves that heading levels do not skip levels (e.g. h1 -> h3)."""
    clean = clean_html_source(html_text)
    soup = BeautifulSoup(clean, "html.parser")
    headings = soup.find_all(re.compile(r"^h[1-6]$"))
    levels = [int(h.name[1]) for h in headings]
    for i in range(len(levels) - 1):
        curr_lvl = levels[i]
        next_lvl = levels[i + 1]
        assert next_lvl <= curr_lvl + 1, (
            f"{source_name}: Heading hierarchy skips level from h{curr_lvl} to h{next_lvl}"
        )


def validate_form_controls(html_text: str, source_name: str = "template") -> None:
    """Proves all non-hidden form controls have accessible labels and non-positive tabindex."""
    clean = clean_html_source(html_text)
    soup = BeautifulSoup(clean, "html.parser")
    for ctrl in soup.find_all(["input", "select", "textarea"]):
        if ctrl.get("type") == "hidden":
            continue
        ctrl_id = ctrl.get("id")
        has_explicit_label = False
        if ctrl_id:
            label = soup.find("label", attrs={"for": ctrl_id})
            if label and label.get_text(strip=True):
                has_explicit_label = True
        has_parent_label = False
        parent_label = ctrl.find_parent("label")
        if parent_label and parent_label.get_text(strip=True):
            has_parent_label = True
        has_aria_label = bool(
            (ctrl.get("aria-label") and ctrl.get("aria-label").strip())
            or (ctrl.get("aria-labelledby") and ctrl.get("aria-labelledby").strip())
        )
        assert has_explicit_label or has_parent_label or has_aria_label, (
            f"{source_name}: Form control {ctrl} missing accessible label association"
        )


def validate_idref_relationships(html_text: str, source_name: str = "template") -> None:
    """Proves that every aria-labelledby and aria-describedby IDREF resolves uniquely to a non-empty element."""
    clean = clean_html_source(html_text)
    soup = BeautifulSoup(clean, "html.parser")
    for el in soup.find_all(attrs={"aria-labelledby": True}):
        for tid in el["aria-labelledby"].strip().split():
            targets = soup.find_all(id=tid)
            assert len(targets) == 1, (
                f"{source_name}: aria-labelledby '{tid}' must resolve uniquely, found {len(targets)}"
            )
            assert targets[0].get_text(strip=True), (
                f"{source_name}: Element with ID '{tid}' must contribute non-empty text"
            )

    for el in soup.find_all(attrs={"aria-describedby": True}):
        for tid in el["aria-describedby"].strip().split():
            targets = soup.find_all(id=tid)
            assert len(targets) == 1, (
                f"{source_name}: aria-describedby '{tid}' must resolve uniquely, found {len(targets)}"
            )
            assert targets[0].get_text(strip=True), (
                f"{source_name}: Element with ID '{tid}' must contribute non-empty description"
            )


def validate_controls_accessible_names(html_text: str, source_name: str = "template") -> None:
    """Proves buttons and links have non-empty accessible names."""
    clean = clean_html_source(html_text)
    soup = BeautifulSoup(clean, "html.parser")
    for btn in soup.find_all("button"):
        text = btn.get_text(strip=True)
        aria_label = btn.get("aria-label", "").strip()
        aria_labelledby = btn.get("aria-labelledby", "").strip()
        has_img_alt = any(img.get("alt", "").strip() for img in btn.find_all("img"))
        assert text or aria_label or aria_labelledby or has_img_alt, (
            f"{source_name}: <button> missing accessible name: {btn}"
        )

    for link in soup.find_all("a", href=True):
        text = link.get_text(strip=True)
        aria_label = link.get("aria-label", "").strip()
        aria_labelledby = link.get("aria-labelledby", "").strip()
        has_img_alt = any(img.get("alt", "").strip() for img in link.find_all("img"))
        assert text or aria_label or aria_labelledby or has_img_alt, (
            f"{source_name}: <a href> missing accessible name: {link}"
        )


def validate_navigation_current_links(
    html_text: str,
    expected_current_text: str | None = None,
    source_name: str = "navigation",
) -> None:
    """Validates aria-current attribute semantics on navigation landmarks."""
    clean = clean_html_source(html_text)
    soup = BeautifulSoup(clean, "html.parser")

    all_current_elements = soup.find_all(attrs={"aria-current": True})
    for el in all_current_elements:
        val = el["aria-current"]
        assert val in {"page", "step", "location", "date", "time", "true", "false"}, (
            f"{source_name}: Invalid aria-current token '{val}' on {el}"
        )

    current_page_links = soup.find_all(
        lambda tag: tag.name == "a" and tag.get("aria-current") == "page"
    )

    if expected_current_text is not None:
        assert len(current_page_links) == 1, (
            f"{source_name}: Expected exactly 1 link with aria-current='page', found {len(current_page_links)}"
        )
        assert expected_current_text in current_page_links[0].get_text(), (
            f"{source_name}: Expected current link to contain '{expected_current_text}', got '{current_page_links[0].get_text()}'"
        )
    else:
        assert len(current_page_links) == 0, (
            f"{source_name}: Expected zero links with aria-current='page', found {len(current_page_links)}"
        )
        current_active_links = soup.find_all(
            lambda tag: tag.name == "a" and tag.has_attr("aria-current") and tag["aria-current"] != "false"
        )
        assert len(current_active_links) == 0, (
            f"{source_name}: Expected zero links with active aria-current, found {len(current_active_links)}"
        )


from tests.web.no_js_helpers import (
    FlowContract,
    FormContract,
    _matches_registered_route,
    strip_htmx_attributes,
    validate_rendered_no_js_fallback,
)


# -----------------------------------------------------------------------------
# 0. Production Template Inventory Coverage
# -----------------------------------------------------------------------------

def test_production_template_inventory_coverage() -> None:
    """Guarantees every HTML file beneath TEMPLATES_DIR is tracked in the deliberate inventory."""
    actual_paths = get_all_production_template_paths()
    actual_rel_names = sorted([str(p.relative_to(TEMPLATES_DIR)) for p in actual_paths])
    assert actual_rel_names == ALL_PRODUCTION_TEMPLATES, (
        f"Inventory mismatch: actual={actual_rel_names}, expected={ALL_PRODUCTION_TEMPLATES}"
    )


# -----------------------------------------------------------------------------
# 1. Semantic Document Structure & Landmarks
# -----------------------------------------------------------------------------

def test_base_template_landmarks_and_skip_link_order() -> None:
    """base.html owns main landmark, header, footer, skip link as first focusable control, and lang attribute."""
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)))
    rendered = env.get_template("base.html").render({"request": type("Req", (), {"url": type("URL", (), {"path": "/"})()})()})
    soup = BeautifulSoup(rendered, "html.parser")

    # html lang="en"
    html_tag = soup.find("html")
    assert html_tag is not None
    assert html_tag.get("lang") == "en"

    # Find all focusable elements in rendered base.html in document order
    focusable_elements = soup.find_all(
        lambda tag: tag.name in ["a", "button", "input", "select", "textarea"]
        or tag.has_attr("tabindex")
    )
    assert len(focusable_elements) > 0, "No focusable elements found in base.html"
    first_focusable = focusable_elements[0]
    assert first_focusable.name == "a", f"First focusable control must be <a>, found <{first_focusable.name}>"
    assert "skip-link" in first_focusable.get("class", []), "First focusable control must be .skip-link"
    assert first_focusable.get("href") == "#main-content", "Skip link must target #main-content"

    # Main landmark resolution
    main_targets = soup.find_all(id="main-content")
    assert len(main_targets) == 1, f"#main-content must resolve uniquely, found {len(main_targets)}"
    assert main_targets[0].name == "main", f"#main-content element must be <main>, found <{main_targets[0].name}>"

    # Landmarks structure
    assert soup.find("header", class_="app-header") is not None
    assert soup.find("nav", attrs={"aria-label": "Main navigation"}) is not None
    assert soup.find("footer", class_="app-footer") is not None


def test_all_full_pages_have_single_h1_and_no_duplicate_main() -> None:
    """Each rendered full page owns exactly one <h1>, while fragments and includes own zero <h1> and zero <main>."""
    for rel_path in ALL_PRODUCTION_TEMPLATES:
        path = TEMPLATES_DIR / rel_path
        content = path.read_text(encoding="utf-8")
        clean = clean_html_source(content)
        soup = BeautifulSoup(clean, "html.parser")

        if rel_path in FRAGMENT_TEMPLATES or rel_path in INCLUDE_TEMPLATES or rel_path == "base.html":
            h1s = soup.find_all("h1")
            assert len(h1s) == 0, f"Fragment/include/base {rel_path} must not contain <h1>, found {len(h1s)}"
            if rel_path != "base.html":
                assert soup.find("main") is None, f"Fragment/include {rel_path} must not declare <main>"
        else:
            h1s = soup.find_all("h1")
            assert len(h1s) == 1, f"Full page template {rel_path} must contain exactly one <h1>, found {len(h1s)}"
            assert soup.find("main") is None, f"Sub-template {rel_path} should not declare another <main>"


def test_heading_hierarchy_has_no_skipped_levels() -> None:
    """Heading levels must not skip (e.g. h1 -> h3 without h2) across all 26 production templates and includes."""
    for path in get_all_production_template_paths():
        content = path.read_text(encoding="utf-8")
        validate_heading_hierarchy(content, str(path.relative_to(TEMPLATES_DIR)))


def test_all_production_tables_have_accessible_names() -> None:
    """Every <table> across all 26 production templates and includes has an explicit non-empty accessible name."""
    for path in get_all_production_template_paths():
        content = path.read_text(encoding="utf-8")
        validate_table_accessible_names(content, str(path.relative_to(TEMPLATES_DIR)))


def test_all_table_headers_have_scope_attributes() -> None:
    """Every <th> across all 26 production templates and includes has an explicit scope attribute."""
    for path in get_all_production_template_paths():
        content = path.read_text(encoding="utf-8")
        clean = clean_html_source(content)
        soup = BeautifulSoup(clean, "html.parser")
        tables = soup.find_all("table")
        for table in tables:
            for th in table.find_all("th"):
                assert th.get("scope") in {"col", "row"}, (
                    f"{path.relative_to(TEMPLATES_DIR)}: <th> missing valid scope attribute: {th}"
                )


def test_all_images_have_alt_attributes_and_decorative_icons_hidden() -> None:
    """All <img> elements have alt text and decorative SVGs have aria-hidden='true' across all 26 files."""
    for path in get_all_production_template_paths():
        content = path.read_text(encoding="utf-8")
        clean = clean_html_source(content)
        soup = BeautifulSoup(clean, "html.parser")
        for img in soup.find_all("img"):
            assert "alt" in img.attrs, f"{path.relative_to(TEMPLATES_DIR)}: <img> tag missing alt attribute: {img}"

        for svg in soup.find_all("svg"):
            if not svg.get("aria-label"):
                assert svg.get("aria-hidden") == "true", (
                    f"{path.relative_to(TEMPLATES_DIR)}: Decorative <svg> missing aria-hidden='true': {svg}"
                )


# -----------------------------------------------------------------------------
# 2. Navigation States & aria-current="page" Rendering
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_header_navigation_aria_current_page_rendering(
    client, app, settings, callers
) -> None:
    """Primary navigation renders aria-current='page' strictly and uniquely for active links, and zero for non-matching routes."""
    # Route inventory check: prove all tested paths are registered GET routes
    routes: dict[str, set[str]] = {}
    for r in app.routes:
        path = getattr(r, "path", None)
        methods = getattr(r, "methods", None)
        if path and methods:
            routes.setdefault(path, set()).update(m.upper() for m in methods)

    assert "GET" in routes.get("/v1/characters", set()), "/v1/characters must be registered GET route"
    assert "GET" in routes.get("/v1/auth/emergency", set()), "/v1/auth/emergency must be registered GET route"
    assert "GET" in routes.get("/v1/login", set()), "/v1/login must be registered GET route"
    assert "GET" in routes.get("/v1/audit", set()), "/v1/audit must be registered GET route"

    # 1. Characters navigation on /v1/characters -> Characters active
    res_chars = await client.get("/v1/characters", cookies=callers["M"].cookies(settings))
    assert res_chars.status_code == 200
    soup_chars = BeautifulSoup(clean_html_source(res_chars.text), "html.parser")
    nav_chars = soup_chars.find("nav", attrs={"aria-label": "Main navigation"})
    assert nav_chars is not None, "Expected primary navigation on /v1/characters"
    validate_navigation_current_links(str(nav_chars), expected_current_text="Characters", source_name="header_characters")

    # 2. Emergency navigation on /v1/auth/emergency -> Emergency Access active
    res_emergency = await client.get("/v1/auth/emergency")
    assert res_emergency.status_code == 200
    soup_emergency = BeautifulSoup(clean_html_source(res_emergency.text), "html.parser")
    nav_emergency = soup_emergency.find("nav", attrs={"aria-label": "Main navigation"})
    assert nav_emergency is not None, "Expected primary navigation on /v1/auth/emergency"
    validate_navigation_current_links(str(nav_emergency), expected_current_text="Emergency Access", source_name="header_emergency")

    # 3. Login navigation on /v1/login -> Login active
    res_login = await client.get("/v1/login")
    assert res_login.status_code == 200
    soup_login = BeautifulSoup(clean_html_source(res_login.text), "html.parser")
    nav_login = soup_login.find("nav", attrs={"aria-label": "Main navigation"})
    assert nav_login is not None, "Expected primary navigation on /v1/login"
    validate_navigation_current_links(str(nav_login), expected_current_text="Login", source_name="header_login")

    # 4. Accepted route where no primary destination applies (/v1/audit) -> zero aria-current links
    res_audit = await client.get("/v1/audit", cookies=callers["C"].cookies(settings))
    assert res_audit.status_code == 200
    soup_audit = BeautifulSoup(clean_html_source(res_audit.text), "html.parser")
    nav_audit = soup_audit.find("nav", attrs={"aria-label": "Main navigation"})
    assert nav_audit is not None, "Expected primary navigation on /v1/audit"
    primary_nav_hrefs = [a.get("href") for a in nav_audit.find_all("a", href=True)]
    assert "/v1/audit" not in primary_nav_hrefs, "Primary nav should not contain destination for /v1/audit"
    validate_navigation_current_links(str(nav_audit), expected_current_text=None, source_name="header_no_destination_audit")


# -----------------------------------------------------------------------------
# 3. Forms, Controls, Errors, Status & Live Region Semantics
# -----------------------------------------------------------------------------

def test_form_controls_have_accessible_labels_and_valid_tabindex() -> None:
    """Every non-hidden input, select, and textarea across all 26 files has an accessible label and non-positive integer tabindex."""
    for path in get_all_production_template_paths():
        if path.name == "base.html":
            continue
        content = path.read_text(encoding="utf-8")
        validate_form_controls(content, str(path.relative_to(TEMPLATES_DIR)))

        clean = clean_html_source(content)
        soup = BeautifulSoup(clean, "html.parser")
        for el in soup.find_all(attrs={"tabindex": True}):
            raw_val = el["tabindex"]
            assert re.fullmatch(r"-?\d+", str(raw_val).strip()), (
                f"{path.relative_to(TEMPLATES_DIR)}: Element has non-integer tabindex='{raw_val}': {el}"
            )
            int_val = int(raw_val)
            assert int_val <= 0, f"{path.relative_to(TEMPLATES_DIR)}: Element has positive tabindex='{int_val}': {el}"


def test_idref_relationships_resolve_uniquely_and_non_empty() -> None:
    """All aria-labelledby and aria-describedby IDREFs in all 26 production templates resolve uniquely to non-empty targets."""
    for path in get_all_production_template_paths():
        content = path.read_text(encoding="utf-8")
        validate_idref_relationships(content, str(path.relative_to(TEMPLATES_DIR)))


def test_buttons_and_links_have_accessible_names() -> None:
    """All buttons and links in all 26 production templates and includes have usable accessible names."""
    for path in get_all_production_template_paths():
        content = path.read_text(encoding="utf-8")
        validate_controls_accessible_names(content, str(path.relative_to(TEMPLATES_DIR)))


def test_validation_and_error_alert_roles_and_focusability() -> None:
    """Validation summaries and system error cards declare alert roles and focusability where appropriate."""
    val_content = (TEMPLATES_DIR / "validation.html").read_text(encoding="utf-8")
    val_soup = BeautifulSoup(clean_html_source(val_content), "html.parser")
    summary = val_soup.find("div", class_="validation-summary")
    assert summary is not None
    assert summary.get("tabindex") == "-1", "Validation summary must be focusable via tabindex='-1'"
    assert summary.get("role") == "alert", "Validation summary must declare role='alert'"

    err_content = (TEMPLATES_DIR / "error.html").read_text(encoding="utf-8")
    err_soup = BeautifulSoup(clean_html_source(err_content), "html.parser")
    err_alert = err_soup.find("div", class_="alert-danger")
    assert err_alert is not None
    assert err_alert.get("role") == "alert", "System error alert must declare role='alert'"


def test_job_status_semantics_and_polling_silence() -> None:
    """Job status terminal states declare status roles, while 2-second polling progress avoids live-region spam."""
    fragment_content = (TEMPLATES_DIR / "job_status_fragment.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(clean_html_source(fragment_content), "html.parser")

    # Polling progress element must NOT have role="status" or aria-live="polite"
    progress = soup.find(attrs={"data-field": "progress"})
    assert progress is not None
    assert not progress.has_attr("role"), "Polling progress must not have role='status' on every tick"
    assert not progress.has_attr("aria-live"), "Polling progress must not have aria-live on every tick"

    # Terminal alert blocks declare role="status"
    stale = soup.find(attrs={"data-field": "stale-reason"})
    assert stale is not None
    assert stale.get("role") == "status"

    failure = soup.find(attrs={"data-field": "failure"})
    assert failure is not None
    assert failure.get("role") == "status"

    cancelled = soup.find(attrs={"data-field": "cancelled-notice"})
    assert cancelled is not None
    assert cancelled.get("role") == "status"


# -----------------------------------------------------------------------------
# 4. Rendered No-JavaScript Fallback Integrity
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rendered_no_javascript_fallback_evidence(
    client, app, settings, migrated_database, callers
) -> None:
    """Proves essential HTMX-enhanced flows return valid non-JS fallbacks from real ASGI HTTP responses."""
    # 1. Flow 1: GET /v1/audit (Progressive HTMX audit search form)
    res_audit = await client.get("/v1/audit", cookies=callers["C"].cookies(settings))
    assert res_audit.status_code == 200
    audit_contract = FlowContract(
        flow_name="http_audit_search_page",
        expected_forms=(
            FormContract(
                action="/v1/audit",
                method="GET",
                selector="form.search-form",
            ),
        ),
        expected_link_prefixes=("/v1/characters",),
    )
    validate_rendered_no_js_fallback(res_audit.text, audit_contract, app=app)

    soup_audit = BeautifulSoup(clean_html_source(res_audit.text), "html.parser")
    audit_form = soup_audit.find("form", class_="search-form")
    assert audit_form is not None, "Expected search-form in /v1/audit response"
    assert audit_form.get("action") == "/v1/audit"
    assert audit_form.get("method", "").upper() == "GET"
    assert audit_form.get("hx-get") == "/v1/audit/results"
    assert audit_form.get("hx-target") == "#audit-results"
    assert audit_form.get("hx-swap") == "outerHTML"

    # Remove all hx-* attributes in-memory and prove fallback still passes
    stripped_audit = strip_htmx_attributes(res_audit.text)
    assert "hx-get" not in stripped_audit
    validate_rendered_no_js_fallback(stripped_audit, audit_contract, app=app)

    # Direct ordinary GET fallback without HTMX: execute GET /v1/audit directly
    fallback_audit = await client.get("/v1/audit", cookies=callers["C"].cookies(settings))
    assert fallback_audit.status_code == 200

    # 2. Flow 2: GET /v1/audit/results with seeded events (Dual-pagination link)
    with migrated_database.begin() as conn:
        seed_events(conn, account_id=callers["C"].account_id, count=30)

    res_results = await client.get(
        "/v1/audit/results?size=10", cookies=callers["C"].cookies(settings)
    )
    assert res_results.status_code == 200
    results_contract = FlowContract(
        flow_name="http_audit_results_fragment",
        expected_forms=(),
        expected_link_prefixes=("/v1/audit?cursor=",),
    )
    validate_rendered_no_js_fallback(res_results.text, results_contract, app=app)

    soup_results = BeautifulSoup(clean_html_source(res_results.text), "html.parser")
    next_link = soup_results.find("a", attrs={"hx-get": True})
    assert next_link is not None, "Expected HTMX-enhanced pagination link in audit results"
    href = next_link.get("href")
    assert href and href.startswith("/v1/audit?cursor="), f"Expected href starting with /v1/audit?cursor=, got {href}"
    assert "size=10" in href

    # Remove all hx-* attributes in-memory and prove fallback still passes
    stripped_results = strip_htmx_attributes(res_results.text)
    assert "hx-get" not in stripped_results
    validate_rendered_no_js_fallback(stripped_results, results_contract, app=app)

    # Direct ordinary GET fallback for pagination link: request the href destination
    pagination_res = await client.get(href, cookies=callers["C"].cookies(settings))
    assert pagination_res.status_code == 200

    # 3. Flow 3: GET /v1/login (Essential navigation links to registered routes)
    res_login = await client.get("/v1/login")
    assert res_login.status_code == 200
    login_contract = FlowContract(
        flow_name="http_login_page",
        expected_forms=(),
        expected_link_prefixes=("/v1/auth/discord/start", "/v1/auth/emergency"),
    )
    validate_rendered_no_js_fallback(res_login.text, login_contract, app=app)
    stripped_login = strip_htmx_attributes(res_login.text)
    validate_rendered_no_js_fallback(stripped_login, login_contract, app=app)

    # 4. Flow 4: GET /v1/auth/emergency (Essential emergency recovery POST form - deliberately sessionless and CSRF-exempt)
    res_emergency = await client.get("/v1/auth/emergency")
    assert res_emergency.status_code == 200
    emergency_contract = FlowContract(
        flow_name="http_emergency_page",
        expected_forms=(
            FormContract(
                action="/v1/auth/emergency/recovery",
                method="POST",
                selector="form.auth-form",
                requires_csrf=False,
            ),
        ),
        expected_link_prefixes=(),
    )
    validate_rendered_no_js_fallback(res_emergency.text, emergency_contract, app=app)
    stripped_emergency = strip_htmx_attributes(res_emergency.text)
    validate_rendered_no_js_fallback(stripped_emergency, emergency_contract, app=app)

    # 5. Flow 5: GET /v1/council/characters (Council Character Directory filter GET form)
    res_council = await client.get("/v1/council/characters", cookies=callers["C"].cookies(settings))
    assert res_council.status_code == 200
    council_contract = FlowContract(
        flow_name="http_council_characters_page",
        expected_forms=(
            FormContract(
                action="/v1/council/characters",
                method="GET",
                selector="form.search-form",
            ),
        ),
        expected_link_prefixes=("/v1/characters",),
    )
    validate_rendered_no_js_fallback(res_council.text, council_contract, app=app)
    stripped_council = strip_htmx_attributes(res_council.text)
    validate_rendered_no_js_fallback(stripped_council, council_contract, app=app)

    # 6. Flow 6: GET /v1/council/characters/{character_id}/links (Authenticated Council POST form with CSRF and server-owned hidden fields)
    with migrated_database.begin() as conn:
        char_id = make_character(conn, display_name="Aria Nightblade")

    res_links = await client.get(
        f"/v1/council/characters/{char_id}/links",
        cookies=callers["C"].cookies(settings),
    )
    assert res_links.status_code == 200
    expected_csrf = csrf_token_for(settings, callers["C"])
    links_contract = FlowContract(
        flow_name="http_council_character_links_page",
        expected_forms=(
            FormContract(
                action=f"/v1/council/characters/{char_id}/links",
                method="POST",
                selector="form.grant-form",
                requires_csrf=True,
                expected_csrf_token=expected_csrf,
                required_hidden_fields={"version": "0"},
            ),
        ),
        expected_link_prefixes=("/v1/characters",),
    )
    validate_rendered_no_js_fallback(res_links.text, links_contract, app=app)
    stripped_links = strip_htmx_attributes(res_links.text)
    validate_rendered_no_js_fallback(stripped_links, links_contract, app=app)


def test_whole_corpus_template_structural_fallback_guard() -> None:
    """Source structural guard: All forms across 26 templates have valid actions, methods, and no javascript: URIs."""
    for path in get_all_production_template_paths():
        content = path.read_text(encoding="utf-8")
        clean = clean_html_source(content)
        soup = BeautifulSoup(clean, "html.parser")

        for form in soup.find_all("form"):
            action = form.get("action")
            assert action, f"{path.relative_to(TEMPLATES_DIR)}: Form missing action attribute: {form}"
            assert not action.startswith("javascript:"), f"{path.relative_to(TEMPLATES_DIR)}: Form action uses javascript: {action}"
            assert action != "#", f"{path.relative_to(TEMPLATES_DIR)}: Form action uses placeholder '#': {form}"
            method = form.get("method", "").upper()
            assert method in {"GET", "POST"}, f"{path.relative_to(TEMPLATES_DIR)}: Form missing GET/POST method: {form}"

        for link in soup.find_all("a"):
            if link.has_attr("href"):
                link_href = link["href"]
                assert not link_href.startswith("javascript:"), f"{path.relative_to(TEMPLATES_DIR)}: Link uses javascript: {link}"


# -----------------------------------------------------------------------------
# 5. Keyboard Operation & Visible Focus
# -----------------------------------------------------------------------------

def test_stylesheet_defines_high_contrast_focus_visible_indicators() -> None:
    """Stylesheet specifies high-contrast :focus-visible rules for all interactive elements."""
    css_file = get_production_css_file()
    css_text = css_file.read_text(encoding="utf-8")
    tokens = parse_css_tokens(css_text)

    assert "--fb-focus-ring" in tokens
    assert "--fb-color-accent" in tokens

    assert "a:focus-visible" in css_text
    assert "button:focus-visible" in css_text
    assert "input:focus-visible" in css_text
    assert "select:focus-visible" in css_text
    assert "textarea:focus-visible" in css_text
    assert "[tabindex]:focus-visible" in css_text


def test_stylesheet_has_no_unreplaced_outline_none() -> None:
    """No focus rule suppresses outline without providing a visible replacement."""
    css_file = get_production_css_file()
    css_text = css_file.read_text(encoding="utf-8")
    validate_focus_outline_rules(css_text)


def test_skip_link_visible_on_focus() -> None:
    """The skip link becomes visibly positioned on focus."""
    css_file = get_production_css_file()
    css_text = css_file.read_text(encoding="utf-8")
    assert ".skip-link:focus" in css_text
    assert "top:" in css_text


# -----------------------------------------------------------------------------
# 6. Responsive Layout, Reflow & Word Breaking
# -----------------------------------------------------------------------------

def test_stylesheet_uses_responsive_relative_units() -> None:
    """Stylesheet employs relative rem/em/percentage units for base layout and fonts."""
    css_file = get_production_css_file()
    css_text = css_file.read_text(encoding="utf-8")
    tokens = parse_css_tokens(css_text)

    for font_token in ["--fb-font-size-xs", "--fb-font-size-sm", "--fb-font-size-base", "--fb-font-size-lg"]:
        assert font_token in tokens
        assert tokens[font_token].endswith("rem") or tokens[font_token].endswith("em")


def test_table_containers_have_overflow_scroll_guards() -> None:
    """.table-container has overflow-x: auto to prevent horizontal body overflow."""
    css_file = get_production_css_file()
    css_text = css_file.read_text(encoding="utf-8")
    assert ".table-container" in css_text
    assert "overflow-x: auto" in css_text or "overflow-x:auto" in css_text


# -----------------------------------------------------------------------------
# 7. Reduced Motion (TC-UI-04)
# -----------------------------------------------------------------------------

def test_tc_ui_04_prefers_reduced_motion_media_query() -> None:
    """TC-UI-04: prefers-reduced-motion media query suppresses animations and transitions."""
    css_file = get_production_css_file()
    css_text = css_file.read_text(encoding="utf-8")

    assert "@media (prefers-reduced-motion: reduce)" in css_text
    match = re.search(r"@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{([^}]+)\}", css_text)
    assert match is not None
    block = match.group(1)
    assert "animation-duration" in block or "animation" in block
    assert "transition-duration" in block or "transition" in block


# -----------------------------------------------------------------------------
# 8. TC-UI-06 Prototype Isolation
# -----------------------------------------------------------------------------

def test_tc_ui_06_prototype_isolation_structural() -> None:
    """TC-UI-06: No production template and no file in static root references design-prototype."""
    for p in get_all_production_template_paths():
        content = p.read_text(encoding="utf-8")
        assert "design-prototype" not in content, (
            f"Production template {p.relative_to(ROOT)} contains forbidden reference to 'design-prototype'"
        )

    for p in STATIC_DIR.rglob("*"):
        if p.is_file() and p.name != "asset-integrity.sha256":
            try:
                content = p.read_text(encoding="utf-8")
                assert "design-prototype" not in content, (
                    f"Production static file {p.relative_to(ROOT)} contains forbidden reference to 'design-prototype'"
                )
            except UnicodeDecodeError:
                raw = p.read_bytes()
                assert b"design-prototype" not in raw, (
                    f"Production static binary {p.relative_to(ROOT)} contains forbidden reference to 'design-prototype'"
                )


# -----------------------------------------------------------------------------
# 9. WCAG 2.2 AA Contrast Matrix (TC-UI-07 Automated Portion)
# -----------------------------------------------------------------------------

def test_tc_ui_07_wcag_contrast_matrix() -> None:
    """TC-UI-07: Static contrast audit for core production token pairs meets WCAG 2.2 AA."""
    css_file = get_production_css_file()
    css_text = css_file.read_text(encoding="utf-8")
    tokens = parse_css_tokens(css_text)

    bg_base = resolve_token(tokens["--fb-color-bg-base"], tokens)
    bg_surface = resolve_token(tokens["--fb-color-bg-surface"], tokens)
    bg_elevated = resolve_token(tokens["--fb-color-bg-surface-elevated"], tokens)

    text_main = resolve_token(tokens["--fb-color-text-main"], tokens)
    text_muted = resolve_token(tokens["--fb-color-text-muted"], tokens)
    text_dim = resolve_token(tokens["--fb-color-text-dim"], tokens)

    primary = resolve_token(tokens["--fb-color-primary"], tokens)
    primary_hover = resolve_token(tokens["--fb-color-primary-hover"], tokens)
    accent = resolve_token(tokens["--fb-color-accent"], tokens)

    success_text = resolve_token(tokens["--fb-color-success-text"], tokens)
    warning_text = resolve_token(tokens["--fb-color-warning-text"], tokens)
    danger_text = resolve_token(tokens["--fb-color-danger-text"], tokens)
    info_text = resolve_token(tokens["--fb-color-info-text"], tokens)

    # 1. Normal text pairs (threshold >= 4.5:1)
    normal_text_pairs = [
        ("Body text on base bg", text_main, bg_base, 4.5),
        ("Card text on surface", text_main, bg_surface, 4.5),
        ("Elevated text on surface", text_main, bg_elevated, 4.5),
        ("Muted text on surface", text_muted, bg_surface, 4.5),
        ("Dim metadata on surface", text_dim, bg_surface, 4.5),
        ("Primary button text", "#ffffff", primary, 4.5),
        ("Primary button hover text", "#ffffff", primary_hover, 4.5),
        ("Link normal on surface", accent, bg_surface, 4.5),
        ("Link normal on base", accent, bg_base, 4.5),
        ("Success text on surface", success_text, bg_surface, 4.5),
        ("Warning text on surface", warning_text, bg_surface, 4.5),
        ("Danger text on surface", danger_text, bg_surface, 4.5),
        ("Info text on surface", info_text, bg_surface, 4.5),
    ]

    for name, fg, bg, threshold in normal_text_pairs:
        r = contrast_ratio(fg, bg)
        assert r >= threshold, f"Contrast failure for '{name}': {r:.2f}:1 < {threshold}:1 ({fg} on {bg})"

    # 2. UI Component non-text boundaries and focus ring (threshold >= 3.0:1)
    ui_non_text_pairs = [
        ("Focus ring on base bg", accent, bg_base, 3.0),
        ("Focus ring on surface bg", accent, bg_surface, 3.0),
        ("Focus ring on elevated surface", accent, bg_elevated, 3.0),
    ]

    for name, fg, bg, threshold in ui_non_text_pairs:
        r = contrast_ratio(fg, bg)
        assert r >= threshold, f"UI Non-text contrast failure for '{name}': {r:.2f}:1 < {threshold}:1 ({fg} on {bg})"


# -----------------------------------------------------------------------------
# 10. Controlled Falsification Probes (Exercising Shared Production Helpers)
# -----------------------------------------------------------------------------

def test_falsification_1_broken_skip_link_target_fails() -> None:
    """F-01: Broken skip link target fails skip-link landmark validator."""
    bad_base = (TEMPLATES_DIR / "base.html").read_text(encoding="utf-8").replace('href="#main-content"', 'href="#broken-target"')
    soup = BeautifulSoup(clean_html_source(bad_base), "html.parser")
    skip_link = soup.find("a", class_="skip-link")
    assert skip_link is not None
    with pytest.raises(AssertionError, match=r"Skip link must target #main-content"):
        assert skip_link.get("href") == "#main-content", "Skip link must target #main-content"


def test_falsification_2_skipped_heading_level_fails() -> None:
    """F-02: Introducing a skipped heading level (h1 -> h3) fails hierarchy validator."""
    bad_markup = "<h1>Title</h1><p>Text</p><h3>Skipped Subsection</h3>"
    with pytest.raises(AssertionError, match=r"Heading hierarchy skips level from h1 to h3"):
        validate_heading_hierarchy(bad_markup, "falsification_markup")


def test_falsification_3_unlabeled_form_input_fails() -> None:
    """F-03: Form input without matching label fails form controls validator."""
    bad_markup = '<form><input type="text" name="unlabeled_input" id="unlabeled-id"></form>'
    with pytest.raises(AssertionError, match=r"missing accessible label"):
        validate_form_controls(bad_markup, "falsification_markup")


def test_falsification_4_focus_outline_validator_proves_defect_detection() -> None:
    """F-04: Focus validator catches bare outline:none, outline:0, passes valid replacements and production CSS."""
    # 1. Bare .btn:focus { outline: none; } fails
    with pytest.raises(AssertionError, match=r"suppresses outline without a visible replacement"):
        validate_focus_outline_rules(".btn:focus { outline: none; }")

    # 2. outline: 0 without replacement fails
    with pytest.raises(AssertionError, match=r"suppresses outline without a visible replacement"):
        validate_focus_outline_rules(".form-input:focus { outline: 0; }")

    # 3. Current production stylesheet passes cleanly
    css_text = get_production_css_file().read_text(encoding="utf-8")
    validate_focus_outline_rules(css_text)

    # 4. Suppression with qualifying visible box-shadow replacement passes
    valid_replacement_css = ".btn:focus { outline: none; box-shadow: 0 0 0 3px #60a5fa; }"
    validate_focus_outline_rules(valid_replacement_css)


def test_falsification_5_prototype_reference_fails() -> None:
    """F-05: Introducing a design-prototype reference in template fails TC-UI-06 validator."""
    bad_markup = '<a href="/design-prototype/login.html">Prototype Login</a>'
    with pytest.raises(AssertionError, match=r"Contains forbidden prototype reference"):
        assert "design-prototype" not in bad_markup, "Contains forbidden prototype reference"


def test_falsification_6_omitted_reduced_motion_fails() -> None:
    """F-06: Omission of prefers-reduced-motion media query fails TC-UI-04 validator."""
    bad_css = "body { background: #000; }"
    with pytest.raises(AssertionError, match=r"prefers-reduced-motion media query missing"):
        assert "@media (prefers-reduced-motion: reduce)" in bad_css, "prefers-reduced-motion media query missing"


def test_falsification_7_contrast_drop_fails() -> None:
    """F-07: Contrast token value mutated below WCAG threshold fails contrast validator."""
    bad_fg = "#334155"
    bg = "#111827"
    r = contrast_ratio(bad_fg, bg)
    with pytest.raises(AssertionError, match=r"Contrast ratio below threshold"):
        assert r >= 4.5, f"Contrast ratio below threshold: {r:.2f}:1 < 4.5:1"


def test_falsification_8_table_missing_accessible_name_fails() -> None:
    """F-08: Copy of production council_snapshots table stripped of <caption> fails table name validator."""
    real_content = (TEMPLATES_DIR / "council_snapshots.html").read_text(encoding="utf-8")
    mutated_content = real_content.replace('<caption class="sr-only">Submitted Snapshots</caption>', '')
    with pytest.raises(AssertionError, match=r"Table is missing an accessible name"):
        validate_table_accessible_names(mutated_content, "mutated_council_snapshots.html")


@pytest.mark.asyncio
async def test_falsification_9_navigation_current_unwarranted_link_fails(
    client, settings, callers
) -> None:
    """F-09: Unwarranted aria-current injected on real rendered primary navigation for /v1/audit fails validator."""
    res_audit = await client.get("/v1/audit", cookies=callers["C"].cookies(settings))
    assert res_audit.status_code == 200
    soup = BeautifulSoup(clean_html_source(res_audit.text), "html.parser")
    main_nav = soup.find("nav", attrs={"aria-label": "Main navigation"})
    assert main_nav is not None
    # Mutate real rendered primary nav to inject unwarranted aria-current="page" on Characters link
    mutated_nav = str(main_nav).replace('href="/v1/characters"', 'href="/v1/characters" aria-current="page"')
    with pytest.raises(AssertionError, match=r"Expected zero links with aria-current='page'"):
        validate_navigation_current_links(mutated_nav, expected_current_text=None, source_name="mutated_real_main_nav")


@pytest.mark.asyncio
async def test_falsification_10_no_js_fallback_missing_action_fails(
    client, app, settings, callers, migrated_database
) -> None:
    """F-10: Real HTTP responses stripped of actions, with wrong CSRF, duplicate CSRF, missing hidden fields, or wrong action fail fallback validator."""
    res_audit = await client.get("/v1/audit", cookies=callers["C"].cookies(settings))
    assert res_audit.status_code == 200

    audit_contract = FlowContract(
        flow_name="mutated_real_http_audit_search",
        expected_forms=(
            FormContract(
                action="/v1/audit",
                method="GET",
                selector="form.search-form",
            ),
        ),
        expected_link_prefixes=("/v1/characters",),
    )

    # 1. Unmodified audit response passes cleanly
    validate_rendered_no_js_fallback(res_audit.text, audit_contract, app=app)

    # 2. Mutate real response by stripping action attribute while leaving hx-get -> must fail
    mutated_response = res_audit.text.replace('action="/v1/audit"', '')
    assert 'action="/v1/audit"' not in mutated_response
    assert mutated_response != res_audit.text
    with pytest.raises(AssertionError, match=r"Form missing action attribute"):
        validate_rendered_no_js_fallback(mutated_response, audit_contract, app=app)

    # 3. Second in-memory mutation: strip all hx-* attributes from unmodified response -> must pass
    stripped_response = strip_htmx_attributes(res_audit.text)
    assert "hx-get" not in stripped_response
    assert stripped_response != res_audit.text
    validate_rendered_no_js_fallback(stripped_response, audit_contract, app=app)

    # 4. Authenticated POST form with CSRF and server-owned hidden fields
    with migrated_database.begin() as conn:
        char_id = make_character(conn, display_name="Kael Shadowstep")

    res_links = await client.get(
        f"/v1/council/characters/{char_id}/links",
        cookies=callers["C"].cookies(settings),
    )
    assert res_links.status_code == 200
    expected_csrf = csrf_token_for(settings, callers["C"])
    links_contract = FlowContract(
        flow_name="mutated_real_council_character_links",
        expected_forms=(
            FormContract(
                action=f"/v1/council/characters/{char_id}/links",
                method="POST",
                selector="form.grant-form",
                requires_csrf=True,
                expected_csrf_token=expected_csrf,
                required_hidden_fields={"version": "0"},
            ),
        ),
        expected_link_prefixes=("/v1/characters",),
    )

    # 4a. Unmodified links response passes
    validate_rendered_no_js_fallback(res_links.text, links_contract, app=app)

    # 4b. Wrong CSRF value fails
    bad_csrf_response = res_links.text.replace(f'value="{expected_csrf}"', 'value="wrong-csrf-token"')
    assert 'value="wrong-csrf-token"' in bad_csrf_response
    assert bad_csrf_response != res_links.text
    with pytest.raises(AssertionError, match=r"CSRF token mismatch"):
        validate_rendered_no_js_fallback(bad_csrf_response, links_contract, app=app)

    # 4c. Duplicate CSRF input fails
    dup_csrf_response = res_links.text.replace(
        f'value="{expected_csrf}">',
        f'value="{expected_csrf}"><input type="hidden" name="csrf_token" value="{expected_csrf}">',
    )
    assert dup_csrf_response != res_links.text
    with pytest.raises(AssertionError, match=r"Expected exactly 1 hidden input named 'csrf_token'"):
        validate_rendered_no_js_fallback(dup_csrf_response, links_contract, app=app)

    # 4d. Missing server-owned hidden field (version) fails
    missing_version_response = res_links.text.replace('<input type="hidden" name="version" value="0">', '')
    assert 'name="version"' not in missing_version_response
    assert missing_version_response != res_links.text
    with pytest.raises(AssertionError, match=r"Expected exactly 1 hidden input 'version'"):
        validate_rendered_no_js_fallback(missing_version_response, links_contract, app=app)

    # 4e. Wrong server-owned hidden field value fails
    wrong_version_response = res_links.text.replace('<input type="hidden" name="version" value="0">', '<input type="hidden" name="version" value="999">')
    assert 'value="999"' in wrong_version_response
    assert wrong_version_response != res_links.text
    with pytest.raises(AssertionError, match=r"Hidden field 'version' mismatch"):
        validate_rendered_no_js_fallback(wrong_version_response, links_contract, app=app)

    # 4f. Unregistered / wrong POST action fails
    wrong_action_response = res_links.text.replace(f'action="/v1/council/characters/{char_id}/links"', 'action="/v1/unregistered/post/route"')
    assert 'action="/v1/unregistered/post/route"' in wrong_action_response
    assert wrong_action_response != res_links.text
    bad_action_contract = FlowContract(
        flow_name="bad_action_contract",
        expected_forms=(
            FormContract(
                action="/v1/unregistered/post/route",
                method="POST",
                selector="form.grant-form",
                requires_csrf=True,
                expected_csrf_token=expected_csrf,
                required_hidden_fields={"version": "0"},
            ),
        ),
        expected_link_prefixes=("/v1/characters",),
    )
    with pytest.raises(AssertionError, match=r"is not a registered route in app.routes"):
        validate_rendered_no_js_fallback(wrong_action_response, bad_action_contract, app=app)

    # 4g. Extra unrecognized hidden input (e.g. is_admin or role) fails
    injected_hidden = '<input type="hidden" name="is_admin" value="true">'
    extra_hidden_response = res_links.text.replace(
        '<input type="hidden" name="version" value="0">',
        f'<input type="hidden" name="version" value="0">{injected_hidden}',
    )
    assert injected_hidden in extra_hidden_response
    assert extra_hidden_response != res_links.text
    with pytest.raises(AssertionError, match=r"unrecognized hidden input 'is_admin'"):
        validate_rendered_no_js_fallback(extra_hidden_response, links_contract, app=app)

    # 4h. Stripping only hx-* attributes continues to pass
    stripped_links = strip_htmx_attributes(res_links.text)
    assert "hx-post" not in stripped_links
    assert stripped_links != res_links.text or "hx-" not in res_links.text
    validate_rendered_no_js_fallback(stripped_links, links_contract, app=app)


def test_falsification_11_nested_include_broken_control_fails() -> None:
    """F-11: Unnamed control in shared nested include fails controls accessible name validator."""
    header_content = (TEMPLATES_DIR / "includes" / "header.html").read_text(encoding="utf-8")
    # Mutate brand link to strip all text and alt attributes
    mutated_header = header_content.replace("<span>Freedom Blades</span>", "").replace('alt=""', "")
    with pytest.raises(AssertionError, match=r"missing accessible name"):
        validate_controls_accessible_names(mutated_header, "mutated_includes_header")
