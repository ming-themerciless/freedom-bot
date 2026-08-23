"""Tests for P3.4 Step 5: Ordinary-Member Character Pages (my_characters.html and character_detail.html).

Verifies:
1. Strict Jinja rendering of actual templates with VM-05 and VM-06 shapes across all states.
2. VM-05 ready, empty, and truncated states; stable detail_path navigation; portrait initials; default/access/active facts.
3. TC-VM-05: level=None renders as "not recorded" on both pages and cannot be mistaken for numeric zero.
4. TC-STRUCT-01 / OD-31: Zero forms, editable controls, mutation actions, hidden inputs, button-styled links, or POST routes.
5. VM-06 snapshot fields: present/absent distinctions, closed unavailable reasons, and authority classifications.
6. TC-VM-03: Every deferred field renders owning package, no value, and no control (inspected per-entry).
7. Provenance (mapped/unmapped snapshot, profile version, external actor ID), optional long name, viewer access kind (including Council-by-role as None), and bounded access facts.
8. Portrait markup: accessible fallback, no character image URL, no remote network request.
9. Exact bounds: VM-05 <= 50; VM-06 snapshot <= 200, deferred <= 200, access <= 25.
10. Adversarial autoescaping: user-influenced strings render inert and escaped.
11. R-20 / R-21 HTTP behavior with disposable PostgreSQL database (including R-20 empty and populated states, R-21 detail, and 404 byte non-enumeration).
12. All 23 templates match implementation digests.
13. CSS fingerprint, asset-integrity manifest, Step 5 selector usage and template presence, and absence of Step 6+ / button selectors.
14. Deterministic falsifications exercising shared production validators: None as 0, injected mutation form, deferred fabricated value, deferred control, portrait image URL, hidden authoritative field, button-styled duplicate action, unused selector, prohibited selector, CSS comment mentions, longer selector names, declaration values, Jinja comment mentions, longer template tokens, unterminated CSS comments, and CSS byte tampering in temporary path.
15. Autouse database cleanup finalizer with connection-binding context manager and strengthened structural AST verification proving database resolution and cleanup occur strictly after yield inside the guarded path.
"""
from __future__ import annotations

import ast
import hashlib
import inspect
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

import jinja2
import pytest
from starlette.requests import Request

from application.web.view_models import (
    ACCESS_FACT_BOUND,
    FIELD_BOUND,
    MY_CHARACTERS_BOUND,
    AccessFact,
    Actor,
    CharacterDetailView,
    CharacterPortrait,
    CharacterSummary,
    Correlation,
    Instant,
    MigrationDeferred,
    MyCharactersView,
    Provenance,
    SafeText,
    SnapshotField,
    SnapshotStamp,
    bounded_tuple,
)

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = ROOT / "adapters" / "web" / "templates"
STATIC_ROOT = ROOT / "adapters" / "web" / "static"
MANIFEST_PATH = STATIC_ROOT / "asset-integrity.sha256"

from tests.web.template_digests import P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS


# Step 5 selectors added and actually used by Step 5 templates
STEP_5_SELECTORS: tuple[str, ...] = (
    ".page-header",
    ".page-title",
    ".empty-card",
    ".empty-icon",
    ".character-card",
    ".char-card-header",
    ".char-portrait-fallback",
    ".portrait-initials",
    ".char-title-group",
    ".char-title",
    ".char-title-link",
    ".char-badges",
    ".char-details-list",
    ".char-detail-item",
    ".profile-hero",
    ".profile-identity",
    ".profile-identity-text",
    ".profile-long-name",
    ".profile-badges",
    ".profile-version",
    ".detail-section",
    ".section-title",
    ".data-grid",
    ".data-item",
    ".data-label",
    ".data-value",
    ".provenance-details",
    ".provenance-item",
    ".badge",
    ".badge-primary",
    ".badge-success",
    ".badge-warning",
    ".badge-info",
    ".badge-deferred",
    ".badge-sm",
    ".font-mono",
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
    ".char-card-actions",
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


# ===========================================================================
# Fixtures & Environment
# ===========================================================================

@pytest.fixture(autouse=True)
def clean_between_member_cases(request):
    """Leave the character tables clean after database tests (R1/F3/R2-1/R3-1).

    Yields first so test execution runs, then resolves migrated_database only if
    the test requested it, and invokes the shared clean_p3_2_tables helper with a connection.
    """
    yield
    if "migrated_database" not in request.fixturenames:
        return
    from tests.web.portal_fixtures import clean_p3_2_tables
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)


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


def strip_css_comments(css_text: str) -> str:
    """Strictly strip all /* ... */ block comments from CSS."""
    result_parts: list[str] = []
    pos = 0
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


def strip_jinja_comments(template_text: str) -> str:
    """Strip Jinja {# ... #} comments to inspect active template markup."""
    return re.sub(r"\{#.*?#\}", "", template_text, flags=re.DOTALL)


def extract_active_css_classes(css_text: str) -> set[str]:
    """Extract all active CSS class selectors from rules (outside comments)."""
    active_css = strip_css_comments(css_text)
    active_classes: set[str] = set()
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", active_css):
        rule_header = m.group(1)
        for sel_part in rule_header.split(","):
            for cls in re.findall(r"(?:\A|[^\w\-.])\.([a-zA-Z0-9_\-]+)", sel_part):
                active_classes.add("." + cls)
    return active_classes


def extract_active_template_classes(template_texts: list[str]) -> set[str]:
    """Extract all exact active class tokens from templates (outside Jinja comments)."""
    active_classes: set[str] = set()
    for template_text in template_texts:
        stripped = strip_jinja_comments(template_text)
        for m in re.finditer(r"\bclass=(['\"])(.*?)\1", stripped):
            val = m.group(2)
            for token in re.findall(r"[a-zA-Z0-9_\-]+", val):
                active_classes.add("." + token)
    return active_classes


def remove_css_selector_rule_in_memory(css_text: str, selector: str) -> str:
    """Helper to remove a specific selector rule from CSS text in memory for negative testing."""
    pattern = rf"(?ms)^[^{{}}]*?{re.escape(selector)}[^{{}}]*?\{{[^{{}}]*?\}}"
    mutated, n = re.subn(pattern, "", css_text)
    assert n >= 1, f"Failed to remove rule for {selector} in memory"
    active_classes = extract_active_css_classes(mutated)
    assert selector not in active_classes, f"Selector {selector} still present in active CSS after removal"
    return mutated


# ===========================================================================
# Validation Helpers
# ===========================================================================

def validate_member_cleanup_fixture(fixture_func_or_code: object) -> None:
    """Structural AST validator for the member database cleanup fixture (R2-2 / R3-1)."""
    if callable(fixture_func_or_code):
        src = inspect.getsource(fixture_func_or_code)
    else:
        src = str(fixture_func_or_code)
    tree = ast.parse(src)
    func_def = tree.body[0]
    assert isinstance(func_def, ast.FunctionDef), "Expected a function definition"

    # Verify fixture takes 'request' parameter
    arg_names = [a.arg for a in func_def.args.args]
    assert "request" in arg_names, "Fixture must accept 'request' parameter"

    # 1. Exactly one yield occurs
    yield_nodes = [node for node in ast.walk(func_def) if isinstance(node, ast.Yield)]
    assert len(yield_nodes) == 1, f"Fixture must contain exactly one yield statement, found {len(yield_nodes)}"
    yield_lineno = yield_nodes[0].lineno

    # Find the top-level body statement containing the yield
    yield_stmt_idx = None
    for idx, stmt in enumerate(func_def.body):
        if any(node is yield_nodes[0] for node in ast.walk(stmt)):
            yield_stmt_idx = idx
            break
    assert yield_stmt_idx is not None, "Yield must be located in fixture body"

    # 2. Exactly one database resolution call with semantic shape request.getfixturevalue("migrated_database")
    res_calls: list[ast.Call] = []
    for node in ast.walk(func_def):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "getfixturevalue":
                res_calls.append(node)
            elif isinstance(node.func, ast.Name) and "migrated_database" in [
                getattr(a, "value", None) for a in node.args if isinstance(a, ast.Constant)
            ]:
                res_calls.append(node)

    assert len(res_calls) == 1, f"Expected exactly one database resolution call, found {len(res_calls)}"
    res_call = res_calls[0]
    assert isinstance(res_call.func, ast.Attribute), "Database resolution must be a method call (getfixturevalue)"
    assert isinstance(res_call.func.value, ast.Name) and res_call.func.value.id == "request", (
        f"Database resolution receiver must be 'request', got '{getattr(res_call.func.value, 'id', None)}'"
    )
    assert res_call.func.attr == "getfixturevalue", (
        f"Database resolution method must be 'getfixturevalue', got '{res_call.func.attr}'"
    )
    assert len(res_call.args) == 1 and isinstance(res_call.args[0], ast.Constant) and res_call.args[0].value == "migrated_database", (
        "Database resolution argument must be literal string 'migrated_database'"
    )
    assert len(res_call.keywords) == 0, "Database resolution must not have keyword arguments"
    res_lineno = res_call.lineno

    # Resolution call must be strictly AFTER yield
    assert yield_lineno < res_lineno, (
        f"Yield at line {yield_lineno} must precede database resolution at line {res_lineno}"
    )

    # 3. Post-yield guard verification: resolution call must be guarded by migrated_database check occurring after yield
    guarded = False
    for stmt_idx in range(yield_stmt_idx + 1, len(func_def.body)):
        stmt = func_def.body[stmt_idx]
        if isinstance(stmt, ast.If):
            has_guard_const = any(
                isinstance(n, ast.Constant) and n.value == "migrated_database"
                for n in ast.walk(stmt.test)
            )
            if has_guard_const:
                # Early return guard
                if any(isinstance(n, ast.Return) for n in stmt.body):
                    if res_lineno > stmt.lineno:
                        guarded = True
                        break
                # Wrapping if-block
                if any(n is res_call for n in ast.walk(stmt)):
                    guarded = True
                    break

    assert guarded, "Database resolution must be guarded by 'migrated_database' check occurring after yield"

    # Find the variable name receiving the resolution
    assigned_engine_var = None
    for node in ast.walk(func_def):
        if isinstance(node, ast.Assign) and any(n is res_call for n in ast.walk(node.value)):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                assigned_engine_var = node.targets[0].id
                break
    assert assigned_engine_var is not None, "Database resolution result must be assigned to an engine variable"

    # 4. Engine opens a transaction/context yielding a connection (with engine.begin() as connection:)
    with_nodes = [node for node in ast.walk(func_def) if isinstance(node, ast.With)]
    assert len(with_nodes) == 1, "Fixture must contain exactly one 'with engine.begin() as connection:' context manager"
    with_node = with_nodes[0]
    assert yield_lineno < with_node.lineno, f"Yield at line {yield_lineno} must precede with-context at line {with_node.lineno}"

    assert len(with_node.items) == 1, "With statement must have exactly one context item"
    with_item = with_node.items[0]
    ctx_expr = with_item.context_expr
    assert isinstance(ctx_expr, ast.Call) and isinstance(ctx_expr.func, ast.Attribute), (
        "With context must be a method call on the resolved engine (e.g. engine.begin())"
    )
    assert ctx_expr.func.attr == "begin", f"With context method must be 'begin', got '{ctx_expr.func.attr}'"
    assert isinstance(ctx_expr.func.value, ast.Name) and ctx_expr.func.value.id == assigned_engine_var, (
        f"With context must call .begin() on resolved engine variable '{assigned_engine_var}', got '{getattr(ctx_expr.func.value, 'id', None)}'"
    )

    assert with_item.optional_vars is not None and isinstance(with_item.optional_vars, ast.Name), (
        "With context must bind a connection variable (e.g. 'as connection')"
    )
    conn_var_name = with_item.optional_vars.id

    # 5. clean_p3_2_tables is called inside the with-block receiving conn_var_name
    clean_calls = [
        node for node in ast.walk(func_def)
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "clean_p3_2_tables"
    ]
    assert len(clean_calls) == 1, "Fixture must call clean_p3_2_tables exactly once"
    clean_call = clean_calls[0]
    clean_lineno = clean_call.lineno
    assert yield_lineno < clean_lineno, f"Yield at line {yield_lineno} must precede cleanup at line {clean_lineno}"

    is_inside_with = any(node is clean_call for item in with_node.body for node in ast.walk(item))
    assert is_inside_with, "clean_p3_2_tables call must be inside the with-block"

    assert len(clean_call.args) == 1 and isinstance(clean_call.args[0], ast.Name), (
        "clean_p3_2_tables must take 1 variable argument"
    )
    assert clean_call.args[0].id == conn_var_name, (
        f"clean_p3_2_tables must receive connection '{conn_var_name}', got '{clean_call.args[0].id}'"
    )


def validate_zero_mutation_controls(rendered_html: str, template_name: str) -> None:
    """Assert zero forms, editable inputs, buttons, textareas, selects, button classes, or mutation methods exist."""
    assert "<form" not in rendered_html, f"Forbidden <form> found in {template_name}"
    assert "<input" not in rendered_html, f"Forbidden <input> found in {template_name}"
    assert "<textarea" not in rendered_html, f"Forbidden <textarea> found in {template_name}"
    assert "<select" not in rendered_html, f"Forbidden <select> found in {template_name}"
    assert "<button" not in rendered_html, f"Forbidden <button> found in {template_name}"
    assert 'class="btn' not in rendered_html and "class='btn" not in rendered_html, (
        f"Forbidden button-styled element found in {template_name}"
    )
    assert 'role="button"' not in rendered_html, f"Forbidden role='button' found in {template_name}"
    assert 'data-authority="guild_council"' not in rendered_html, (
        f"Forbidden hidden council authority found in member view {template_name}"
    )
    assert 'method="post"' not in rendered_html.lower(), f"Forbidden POST method found in {template_name}"
    assert "csrf" not in rendered_html.lower(), f"Forbidden CSRF token found in {template_name}"


def validate_level_rendering_strict(rendered_html: str, expected_level: int | None) -> None:
    """Assert level=None renders strictly as 'not recorded' and never as 0 or empty."""
    if expected_level is None:
        assert "not recorded" in rendered_html, "Missing 'not recorded' for null level"
        assert "Level 0" not in rendered_html, "Null level must not render as 'Level 0'"
        level_field_match = re.search(r'data-field="level"[^>]*>([^<]*)<', rendered_html)
        if level_field_match:
            level_text = level_field_match.group(1).strip()
            assert "0" not in level_text, "Null level must not render as numeric '0'"
            assert "not recorded" in level_text, "Level field text must contain 'not recorded'"
    else:
        assert str(expected_level) in rendered_html, f"Expected level {expected_level} in rendered HTML"


def validate_deferred_fields_strict(rendered_html: str, deferred_fields: tuple[MigrationDeferred, ...]) -> None:
    """Assert every deferred field renders owning package, 'migration deferred', NO value, and NO controls."""
    for field in deferred_fields:
        entry_match = re.search(
            rf'<div[^>]*data-field-key="{re.escape(field.field_key)}"[^>]*>(.*?)</div>',
            rendered_html,
            flags=re.DOTALL,
        )
        assert entry_match, f"Deferred field entry for '{field.field_key}' not found in rendered HTML"
        entry_html = entry_match.group(0)

        # 1. Exact owning package attribute and label text
        assert f'data-owning-package="{field.owning_package}"' in entry_html, (
            f"Missing data-owning-package='{field.owning_package}' on deferred entry '{field.field_key}'"
        )
        assert f"(package {field.owning_package})" in entry_html, (
            f"Missing '(package {field.owning_package})' text in deferred entry '{field.field_key}'"
        )

        # 2. Exact migration deferred marker
        assert "migration deferred" in entry_html, (
            f"Missing 'migration deferred' in deferred entry '{field.field_key}'"
        )

        # 3. No displayed value beyond standard package marker presentation
        val_match = re.search(r'<span class="data-value"[^>]*>(.*?)</span>', entry_html, flags=re.DOTALL)
        assert val_match, f"Missing data-value span in deferred entry '{field.field_key}'"
        val_text = val_match.group(1).strip()
        expected_val_text = f"migration deferred (package {field.owning_package})"
        assert val_text == expected_val_text, (
            f"Deferred field '{field.field_key}' must have value text exactly '{expected_val_text}', got '{val_text}'"
        )

        # 4. Zero controls or forms in the entry
        for forbidden in ("<form", "<input", "<button", "<select", "<textarea", "contenteditable", "action=", "method="):
            assert forbidden not in entry_html.lower(), (
                f"Forbidden control '{forbidden}' found in deferred entry '{field.field_key}'"
            )


def validate_portrait_fallback_strict(rendered_html: str) -> None:
    """Assert portrait fallback contains accessible label/initials and NO character portrait <img> or remote assets."""
    img_tags = re.findall(r"<img\b[^>]*>", rendered_html)
    for tag in img_tags:
        assert 'class="brand-emblem"' in tag or "freedom-blades-token" in tag, (
            f"Forbidden non-emblem <img> element found in rendered HTML: {tag}"
        )
    assert ".jpg" not in rendered_html and ".jpeg" not in rendered_html and ".webp" not in rendered_html


def validate_css_and_template_selector_scope(
    css_text: str,
    template_texts: list[str],
    required_selectors: tuple[str, ...] = STEP_5_SELECTORS,
    prohibited_selectors: tuple[str, ...] = PROHIBITED_LATER_STEP_SELECTORS,
) -> None:
    """Assert CSS and template class usage: exact active definition in CSS and exact active usage in templates (R2-3)."""
    active_css_classes = extract_active_css_classes(css_text)
    active_template_classes = extract_active_template_classes(template_texts)

    # 1. Every required selector must be actively defined in CSS
    for req in required_selectors:
        assert req in active_css_classes, f"Missing required Step 5 selector in active CSS: {req}"

    # 2. Every required selector must be actively used in at least one Step 5 template
    for req in required_selectors:
        assert req in active_template_classes, f"Required selector '{req}' is not used in any Step 5 template"

    # 3. Prohibited selectors must not be defined or present in active CSS
    active_css_stripped = strip_css_comments(css_text)
    for prohibited in prohibited_selectors:
        assert prohibited not in active_css_classes, f"Prohibited selector found in active CSS rules: {prohibited}"
        assert prohibited not in active_css_stripped, f"Prohibited selector found in CSS text: {prohibited}"


def validate_asset_manifest_and_fingerprint(static_dir: Path, manifest_path: Path) -> None:
    """Assert asset-integrity manifest exists and all static assets match their exact fingerprints and SHA-256."""
    assert manifest_path.is_file(), f"Manifest file missing: {manifest_path}"
    manifest_lines = [
        line.strip()
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert len(manifest_lines) == 3, f"Expected exactly 3 manifest entries, got: {len(manifest_lines)}"

    for line in manifest_lines:
        expected_sha, rel_path = line.split(maxsplit=1)
        rel_to_static = Path(rel_path).relative_to("adapters/web/static") if rel_path.startswith("adapters/web/static/") else Path(rel_path)
        target_file = static_dir / rel_to_static
        assert target_file.is_file(), f"Asset file missing: {target_file} (rel: {rel_path})"
        actual_sha = compute_sha256(target_file)
        assert actual_sha == expected_sha, (
            f"Manifest integrity check failed for '{rel_path}': expected {expected_sha}, got {actual_sha}"
        )

        if target_file.suffix == ".css":
            match = re.match(r"^freedom-blades\.([0-9a-f]{12})\.css$", target_file.name)
            assert match, f"Invalid CSS filename format: {target_file.name}"
            fp = match.group(1)
            assert actual_sha[:12] == fp, f"Fingerprint mismatch in {target_file.name}: expected {actual_sha[:12]}, got {fp}"


# ===========================================================================
# 1. Direct Jinja Rendering Tests: VM-05 (my_characters.html)
# ===========================================================================

def make_sample_character_summary(
    display_name: str = "Thorin Stonehelm",
    level: int | None = 7,
    active: bool = True,
    access_kind: str = "owner",
    is_default: bool = True,
    has_snapshot: bool = True,
    char_id: UUID | None = None,
) -> CharacterSummary:
    cid = char_id or uuid4()
    portrait = CharacterPortrait.for_name(display_name)
    stamp = (
        SnapshotStamp(
            checksum_short="e3b0c44298fc",
            world_id="the-guild",
            exported_at=Instant.of(datetime(2026, 8, 12, 21, 45, tzinfo=timezone.utc)),
        )
        if has_snapshot
        else None
    )
    return CharacterSummary(
        character_id=cid,
        display_name=SafeText(display_name),
        level=level,
        active=active,
        access_kind=access_kind,  # type: ignore[arg-type]
        is_default=is_default,
        portrait=portrait,
        detail_path=f"/v1/characters/{cid}",
        last_snapshot=stamp,
    )


def test_my_characters_ready_state_rendering() -> None:
    """1. VM-05 ready state renders roster, active/inactive badges, access kinds, default status, snapshot stamp, and stable links."""
    env = get_jinja_env()
    template = env.get_template("my_characters.html")

    c1 = make_sample_character_summary("Thorin Stonehelm", level=7, active=True, access_kind="owner", is_default=True)
    c2 = make_sample_character_summary("Valerius Dawnblade", level=None, active=False, access_kind="delegate", is_default=False, has_snapshot=False)

    vm = MyCharactersView(
        state="ready",
        characters=(c1, c2),
        truncated=False,
        default_character_id=c1.character_id,
    )

    rendered = template.render(view=vm, request=make_request("/v1/characters"))

    # Landmark and title
    assert '<h1 class="page-title">My Characters</h1>' in rendered
    assert "<title>My Characters — Freedom Blades</title>" in rendered

    # Character 1 facts
    assert "Thorin Stonehelm" in rendered
    assert f'href="{c1.detail_path}"' in rendered
    assert "Active" in rendered
    assert "Owner" in rendered
    assert "Default Character" in rendered
    assert "Level:" in rendered
    assert "7" in rendered
    assert "TS" in rendered
    assert 'aria-label="Portrait unavailable for Thorin Stonehelm"' in rendered
    assert "e3b0c44298fc" in rendered
    assert "the-guild" in rendered

    # Character 2 facts (null level, inactive, delegate, no default, no snapshot)
    assert "Valerius Dawnblade" in rendered
    assert f'href="{c2.detail_path}"' in rendered
    assert "Inactive" in rendered
    assert "Delegate" in rendered
    assert "VD" in rendered
    assert "not recorded" in rendered

    # Security & structure checks
    validate_zero_mutation_controls(rendered, "my_characters.html")
    validate_portrait_fallback_strict(rendered)
    assert 'data-truncated="true"' not in rendered


def test_my_characters_empty_state_rendering() -> None:
    """2. VM-05 empty state renders first-class message and zero self-service controls."""
    env = get_jinja_env()
    template = env.get_template("my_characters.html")

    vm = MyCharactersView(
        state="empty",
        characters=(),
        truncated=False,
    )

    rendered = template.render(view=vm, request=make_request("/v1/characters"))

    assert 'data-state="empty"' in rendered
    assert "You have no linked characters. Guild Council manages character links." in rendered
    assert "No Linked Characters Found" in rendered
    validate_zero_mutation_controls(rendered, "my_characters.html")


def test_my_characters_truncated_state_rendering() -> None:
    """3. VM-05 truncated state renders bounded notice without search/paging controls."""
    env = get_jinja_env()
    template = env.get_template("my_characters.html")

    chars = tuple(make_sample_character_summary(f"Hero {i}") for i in range(50))
    vm = MyCharactersView(
        state="ready",
        characters=chars,
        truncated=True,
    )

    rendered = template.render(view=vm, request=make_request("/v1/characters"))

    assert 'data-truncated="true"' in rendered
    assert "Only the first entries are shown." in rendered
    validate_zero_mutation_controls(rendered, "my_characters.html")


# ===========================================================================
# 2. Direct Jinja Rendering Tests: VM-06 (character_detail.html)
# ===========================================================================

def make_sample_character_detail_view(
    display_name: str = "Thorin Stonehelm",
    long_name: str | None = "Thorin of Clan Stonehelm",
    level: int | None = 7,
    active: bool = True,
    viewer_access_kind: str | None = "owner",
    version: int = 42,
    has_snapshot_provenance: bool = True,
) -> CharacterDetailView:
    char_id = uuid4()
    now = Instant.of(datetime(2026, 8, 12, 21, 45, tzinfo=timezone.utc))

    snapshot_fields = (
        SnapshotField(
            field_key="species",
            label="Species",
            value=SafeText("Dwarf"),
            authority="database_authority",
        ),
        SnapshotField(
            field_key="subclass",
            label="Subclass",
            value=SafeText("Oath of Devotion"),
            authority="snapshot_only",
        ),
        SnapshotField(
            field_key="spell_slots",
            label="Spell Slots",
            value=None,
            authority="snapshot_only",
            unavailable_reason="absent_in_snapshot",
        ),
        SnapshotField(
            field_key="custom_feat",
            label="Custom Feat",
            value=None,
            authority="snapshot_only",
            unavailable_reason="unsupported_type",
        ),
    )

    deferred_fields = (
        MigrationDeferred(field_key="copper_balance", owning_package="5.2"),
        MigrationDeferred(field_key="guild_rank", owning_package="6.1"),
    )

    access_facts = (
        AccessFact(
            access_id=uuid4(),
            account=Actor(account_id=uuid4(), label=SafeText("Member Alpha"), capability="ordinary_member"),
            access_kind="owner",
            active=True,
            is_default=True,
            granted_by=Actor(account_id=uuid4(), label=SafeText("Council Elder"), capability="guild_council"),
            granted_at=now,
            reason=SafeText("Primary character ownership link"),
            correlation=Correlation(id=uuid4()),
            discord_subject_display="secret-snowflake-12345",  # MUST NOT LEAK
        ),
    )

    provenance = Provenance(
        snapshot=(
            SnapshotStamp(
                checksum_short="e3b0c44298fc",
                world_id="the-guild",
                exported_at=now,
            )
            if has_snapshot_provenance
            else None
        ),
        profile_version="2026-08-09.1",
        world_id="the-guild",
        external_actor_id="Actor.abc123xyz",
    )

    return CharacterDetailView(
        state="ready",
        character_id=char_id,
        display_name=SafeText(display_name),
        long_name=SafeText(long_name) if long_name else None,
        level=level,
        active=active,
        portrait=CharacterPortrait.for_name(display_name),
        snapshot_fields=snapshot_fields,
        deferred_fields=deferred_fields,
        access=access_facts,
        provenance=provenance,
        viewer_access_kind=viewer_access_kind,  # type: ignore[arg-type]
        version=version,
    )


def test_character_detail_populated_rendering() -> None:
    """4. VM-06 renders all fields, snapshot authority, deferred packages, access facts, and provenance."""
    env = get_jinja_env()
    template = env.get_template("character_detail.html")

    vm = make_sample_character_detail_view()
    rendered = template.render(view=vm, request=make_request(f"/v1/characters/{vm.character_id}"))

    # Title and page heading
    assert "<title>Thorin Stonehelm — Freedom Blades</title>" in rendered
    assert '<h1 class="page-title">Thorin Stonehelm</h1>' in rendered

    # Hero section facts
    assert "Thorin of Clan Stonehelm" in rendered
    assert "Level 7" in rendered
    assert "Active" in rendered
    assert "Access: owner" in rendered
    assert "Version 42" in rendered
    assert "TS" in rendered
    assert 'aria-label="Portrait unavailable for Thorin Stonehelm"' in rendered

    # Snapshot fields section
    assert "Platform-authoritative fields" in rendered
    assert 'data-section="snapshot-fields"' in rendered
    assert "Species" in rendered
    assert "Dwarf" in rendered
    assert "database_authority" in rendered
    assert "Subclass" in rendered
    assert "Oath of Devotion" in rendered
    assert "snapshot_only" in rendered

    # Unavailable reasons
    assert 'data-unavailable="absent_in_snapshot"' in rendered
    assert "not available (absent_in_snapshot)" in rendered
    assert 'data-unavailable="unsupported_type"' in rendered
    assert "not available (unsupported_type)" in rendered

    # Deferred fields
    validate_deferred_fields_strict(rendered, vm.deferred_fields)

    # Access facts & snowflake non-leakage
    assert "Who may reach this character" in rendered
    assert 'data-section="access"' in rendered
    assert "Member Alpha" in rendered
    assert "Primary character ownership link" in rendered
    assert "secret-snowflake-12345" not in rendered, "Discord snowflake leaked to member view"

    # Provenance
    assert "Provenance" in rendered
    assert "Snapshot e3b0c44298fc from world the-guild" in rendered
    assert "Profile version: 2026-08-09.1" in rendered
    assert "Actor.abc123xyz" in rendered

    # Security & controls
    validate_zero_mutation_controls(rendered, "character_detail.html")
    validate_portrait_fallback_strict(rendered)


def test_character_detail_null_level_and_council_access_and_unmapped_provenance() -> None:
    """5. VM-06 renders level=None as 'not recorded', Council viewer access fallback, and unmapped snapshot."""
    env = get_jinja_env()
    template = env.get_template("character_detail.html")

    vm = make_sample_character_detail_view(
        display_name="Valerius Dawnblade",
        long_name=None,
        level=None,
        active=False,
        viewer_access_kind=None,  # Council viewer
        has_snapshot_provenance=False,
    )
    rendered = template.render(view=vm, request=make_request(f"/v1/characters/{vm.character_id}"))

    # Level strictly "not recorded" (TC-VM-05)
    validate_level_rendering_strict(rendered, None)
    assert "Level 0" not in rendered

    # Council access fallback
    assert "Access: Council (by role)" in rendered

    # Inactive badge
    assert "Inactive" in rendered

    # Long name absent
    assert 'data-field="long_name"' not in rendered

    # Unmapped provenance notice
    assert "No Foundry snapshot is mapped to this character." in rendered

    # Security
    validate_zero_mutation_controls(rendered, "character_detail.html")


# ===========================================================================
# 3. View Model Bounds Verification
# ===========================================================================

def test_view_model_bounds_enforced_by_constructors() -> None:
    """9. View models enforce maximum collection bounds."""
    # Test VM-05 bound: 50 items
    chars_51 = [make_sample_character_summary(f"Hero {i}") for i in range(51)]
    bounded_c, trunc_c = bounded_tuple(chars_51, MY_CHARACTERS_BOUND)
    assert len(bounded_c) == 50
    assert trunc_c is True

    # Test VM-06 snapshot bound: 200 items
    fields_201 = [
        SnapshotField(field_key=f"k{i}", label=f"L{i}", value=SafeText("v"), authority="snapshot_only")
        for i in range(201)
    ]
    bounded_f, trunc_f = bounded_tuple(fields_201, FIELD_BOUND)
    assert len(bounded_f) == 200
    assert trunc_f is True

    # Test VM-06 access bound: 25 items
    now = Instant.of(datetime(2026, 8, 12, tzinfo=timezone.utc))
    access_26 = [
        AccessFact(
            access_id=uuid4(),
            account=Actor(account_id=uuid4(), label=SafeText(f"A{i}"), capability="ordinary_member"),
            access_kind="viewer",
            active=True,
            is_default=False,
            granted_by=Actor(account_id=uuid4(), label=SafeText("Admin"), capability="guild_council"),
            granted_at=now,
            reason=SafeText("Reason"),
            correlation=Correlation(id=uuid4()),
        )
        for i in range(26)
    ]
    bounded_acc, trunc_acc = bounded_tuple(access_26, ACCESS_FACT_BOUND)
    assert len(bounded_acc) == 25
    assert trunc_acc is True


# ===========================================================================
# 4. Adversarial Autoescaping
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
def test_adversarial_probes_render_inert_in_member_views(probe: str) -> None:
    """10. Adversarial input strings render inert and autoescaped across member views."""
    env = get_jinja_env()

    # 1. Test VM-05
    c = make_sample_character_summary(display_name=probe)
    vm_05 = MyCharactersView(state="ready", characters=(c,), truncated=False)
    rendered_05 = env.get_template("my_characters.html").render(view=vm_05, request=make_request())
    scripts_05 = re.findall(r"<script\b([^>]*)>(.*?)</script>", rendered_05, flags=re.DOTALL)
    for attrs, body in scripts_05:
        assert 'src="/static/vendor/' in attrs and not body.strip(), f"Injected script found: {attrs} -> {body}"
    assert "<img src=x" not in rendered_05
    validate_portrait_fallback_strict(rendered_05)
    validate_zero_mutation_controls(rendered_05, "my_characters.html")

    # 2. Test VM-06
    vm_06 = make_sample_character_detail_view(display_name=probe, long_name=probe)
    rendered_06 = env.get_template("character_detail.html").render(view=vm_06, request=make_request())
    scripts_06 = re.findall(r"<script\b([^>]*)>(.*?)</script>", rendered_06, flags=re.DOTALL)
    for attrs, body in scripts_06:
        assert 'src="/static/vendor/' in attrs and not body.strip(), f"Injected script found: {attrs} -> {body}"
    assert "<img src=x" not in rendered_06
    validate_portrait_fallback_strict(rendered_06)
    validate_zero_mutation_controls(rendered_06, "character_detail.html")


# ===========================================================================
# 5. Template Digests and CSS Selector Validation
# ===========================================================================

def test_all_23_templates_match_exact_implementation_digests() -> None:
    """12. All 23 templates match implementation digests."""
    found_templates = {
        p.name: compute_sha256(p)
        for p in TEMPLATE_ROOT.glob("*.html")
        if p.name != "base.html"
    }
    assert set(found_templates.keys()) == set(P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS.keys())
    for name, expected_sha in P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS.items():
        assert found_templates[name] == expected_sha, (
            f"Digest mismatch for template '{name}': expected {expected_sha}, got {found_templates[name]}"
        )


def test_css_fingerprint_manifest_and_step5_selectors() -> None:
    """13. CSS content fingerprint, asset manifest, and Step 5 selector definition and template usage verify cleanly."""
    validate_asset_manifest_and_fingerprint(STATIC_ROOT, MANIFEST_PATH)

    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1, f"Expected exactly one CSS file, got: {css_files}"
    css_text = css_files[0].read_text(encoding="utf-8")

    template_texts = [
        (TEMPLATE_ROOT / "my_characters.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "character_detail.html").read_text(encoding="utf-8"),
    ]
    validate_css_and_template_selector_scope(css_text, template_texts, STEP_5_SELECTORS, PROHIBITED_LATER_STEP_SELECTORS)


# ===========================================================================
# 6. Database-Backed HTTP Tests (R-20 / R-21)
# ===========================================================================

@pytest.mark.database
async def test_r20_r21_http_behavior_with_database(client, settings, migrated_database):
    """11. R-20 member roster (empty and populated) and R-21 character detail & 404 byte identity."""
    from tests.web.portal_fixtures import (
        clean_p3_2_tables,
        grant_link,
        link_discord,
        make_account,
        make_character,
        seed_callers,
        seed_discord_member,
    )

    callers = seed_callers(migrated_database, settings, states=("U", "M", "C"))
    member = callers["M"]
    unauthenticated = callers["U"]

    with migrated_database.begin() as connection:
        clean_p3_2_tables(connection)
        c1 = make_character(connection, display_name="Thorin Stonehelm", level=7)
        c2 = make_character(connection, display_name="Valerius Dawnblade", level=None)

    # 1. R-20 empty state over HTTP for ordinary member with zero character links
    res_r20_empty = await client.get("/v1/characters", cookies=member.cookies(settings))
    assert res_r20_empty.status_code == 200
    assert 'data-state="empty"' in res_r20_empty.text
    assert "You have no linked characters. Guild Council manages character links." in res_r20_empty.text
    validate_zero_mutation_controls(res_r20_empty.text, "my_characters.html")

    # Unauthenticated redirect to login
    res_r20_u = await client.get("/v1/characters", cookies=unauthenticated.cookies(settings))
    assert res_r20_u.status_code == 303
    assert res_r20_u.headers["location"] == "/v1/login"

    # Now grant links to member
    with migrated_database.begin() as connection:
        grant_link(
            connection,
            character_id=c1,
            account_id=member.account_id,
            granted_by=callers["C"].account_id,
            default_character=True,
        )
        grant_link(
            connection,
            character_id=c2,
            account_id=member.account_id,
            granted_by=callers["C"].account_id,
            default_character=False,
        )

        other_char = make_character(connection, display_name="Other Char")
        other_account = make_account(connection, label="other-member")
        seed_discord_member(connection, subject=800000000000000001, username="other.one")
        link_discord(connection, other_account, 800000000000000001)
        grant_link(
            connection,
            character_id=other_char,
            account_id=other_account,
            granted_by=callers["C"].account_id,
        )

    # 2. R-20 populated roster over HTTP
    res_r20 = await client.get("/v1/characters", cookies=member.cookies(settings))
    assert res_r20.status_code == 200
    assert "Thorin Stonehelm" in res_r20.text
    assert "Valerius Dawnblade" in res_r20.text
    assert "not recorded" in res_r20.text
    validate_zero_mutation_controls(res_r20.text, "my_characters.html")

    # 3. R-21 character detail over HTTP
    res_r21 = await client.get(f"/v1/characters/{c1}", cookies=member.cookies(settings))
    assert res_r21.status_code == 200
    assert "Thorin Stonehelm" in res_r21.text
    assert "Level 7" in res_r21.text
    validate_zero_mutation_controls(res_r21.text, "character_detail.html")

    # 4. R-21 inaccessible vs absent vs malformed 404 byte identity
    res_inaccessible = await client.get(f"/v1/characters/{other_char}", cookies=member.cookies(settings))
    res_absent = await client.get(f"/v1/characters/{uuid4()}", cookies=member.cookies(settings))
    res_malformed = await client.get("/v1/characters/not-a-uuid", cookies=member.cookies(settings))

    assert res_inaccessible.status_code == res_absent.status_code == res_malformed.status_code == 404
    assert res_inaccessible.content == res_absent.content == res_malformed.content
    assert "Other Char" not in res_inaccessible.text


# ===========================================================================
# 7. Structural Fixture Verification (R2-2 / R3-1)
# ===========================================================================

def test_structural_member_fixture_cleans_after_yield() -> None:
    """R2-2 / R3-1 positive: autouse fixture passes strengthened structural validator."""
    validate_member_cleanup_fixture(clean_between_member_cases)


def test_falsification_structural_fixture_rejects_resolution_before_yield() -> None:
    """R3-1 falsification 1: rejects fixture resolving database before yield (Codex probe)."""
    bad_fixture_code = """
def bad_clean_fixture(request):
    engine = request.getfixturevalue("migrated_database")
    yield
    if "migrated_database" not in request.fixturenames:
        return
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
"""
    with pytest.raises(AssertionError, match=r"Yield at line \d+ must precede database resolution at line \d+"):
        validate_member_cleanup_fixture(bad_fixture_code)


def test_falsification_structural_fixture_rejects_resolution_outside_guard() -> None:
    """R3-1 falsification 2: rejects fixture resolving database outside membership guard."""
    bad_fixture_code = """
def bad_clean_fixture(request):
    yield
    engine = request.getfixturevalue("migrated_database")
    if "migrated_database" not in request.fixturenames:
        return
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
"""
    with pytest.raises(AssertionError, match=r"Database resolution must be guarded by 'migrated_database' check occurring after yield"):
        validate_member_cleanup_fixture(bad_fixture_code)


def test_falsification_structural_fixture_rejects_resolution_of_different_fixture_name() -> None:
    """R3-1 falsification 3: rejects fixture resolving a different fixture name."""
    bad_fixture_code = """
def bad_clean_fixture(request):
    yield
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("other_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
"""
    with pytest.raises(AssertionError, match=r"Database resolution argument must be literal string 'migrated_database'"):
        validate_member_cleanup_fixture(bad_fixture_code)


def test_falsification_structural_fixture_rejects_resolution_through_different_receiver_or_method() -> None:
    """R3-1 falsification 4: rejects fixture resolving database via non-standard helper."""
    bad_fixture_code = """
def bad_clean_fixture(request):
    yield
    if "migrated_database" not in request.fixturenames:
        return
    engine = resolve_fixture("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
"""
    with pytest.raises(AssertionError, match=r"Database resolution must be a method call \(getfixturevalue\)"):
        validate_member_cleanup_fixture(bad_fixture_code)


def test_falsification_structural_fixture_rejects_resolution_feeding_different_engine_variable() -> None:
    """R3-1 falsification 5: rejects fixture where resolution feeds a different engine variable."""
    bad_fixture_code = """
def bad_clean_fixture(request):
    yield
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with other_engine.begin() as connection:
        clean_p3_2_tables(connection)
"""
    with pytest.raises(AssertionError, match=r"With context must call \.begin\(\) on resolved engine variable 'engine'"):
        validate_member_cleanup_fixture(bad_fixture_code)


def test_falsification_structural_fixture_rejects_cleanup_before_yield() -> None:
    """R2-2 falsification 1: structural validator rejects bad fixture where cleanup is before yield."""
    bad_fixture_code = """
def bad_clean_fixture(request):
    if "migrated_database" in request.fixturenames:
        engine = request.getfixturevalue("migrated_database")
        with engine.begin() as connection:
            clean_p3_2_tables(connection)
    yield
"""
    with pytest.raises(AssertionError, match=r"Yield at line \d+ must precede database resolution at line \d+"):
        validate_member_cleanup_fixture(bad_fixture_code)


def test_falsification_structural_fixture_rejects_missing_cleanup_after_yield() -> None:
    """R2-2 falsification 2: structural validator rejects bad fixture that yields but omits cleanup."""
    bad_fixture_code = """
def bad_clean_fixture(request):
    yield
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
"""
    with pytest.raises(AssertionError, match=r"Fixture must contain exactly one 'with engine\.begin\(\) as connection:' context manager"):
        validate_member_cleanup_fixture(bad_fixture_code)


def test_falsification_structural_fixture_rejects_engine_passed_directly() -> None:
    """R2-2 falsification 3: structural validator rejects bad fixture passing engine directly without begin context."""
    bad_fixture_code = """
def bad_clean_fixture(request):
    yield
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    clean_p3_2_tables(engine)
"""
    with pytest.raises(AssertionError, match=r"Fixture must contain exactly one 'with engine\.begin\(\) as connection:' context manager"):
        validate_member_cleanup_fixture(bad_fixture_code)


# ===========================================================================
# 8. Deterministic Falsification Suite (R2-3 / F4 / F5)
# ===========================================================================

def test_falsification_level_rendered_as_zero_rejected() -> None:
    """14a. Falsification: Rendering null level as numeric 0 fails level validator."""
    bad_html = '<span data-field="level">0</span>'
    with pytest.raises(AssertionError, match=r"Missing 'not recorded' for null level"):
        validate_level_rendering_strict(bad_html, None)

    bad_html_with_not_recorded = '<span data-field="level">0 not recorded</span>'
    with pytest.raises(AssertionError, match=r"Null level must not render as numeric '0'"):
        validate_level_rendering_strict(bad_html_with_not_recorded, None)


def test_falsification_injected_mutation_form_rejected() -> None:
    """14b. Falsification: Injected mutation form in template fails zero-mutation validator."""
    bad_html = '<div><h1>My Characters</h1><form action="/v1/characters" method="post"><button type="submit">Add</button></form></div>'
    with pytest.raises(AssertionError, match=r"Forbidden <form> found in test_page\.html"):
        validate_zero_mutation_controls(bad_html, "test_page.html")


def test_falsification_deferred_fabricated_value_rejected() -> None:
    """14c1. Falsification (F4): Deferred field carrying a fabricated value fails deferred validator."""
    deferred = (MigrationDeferred(field_key="copper_balance", owning_package="5.2"),)
    bad_html = (
        '<div class="data-grid" data-section="deferred-fields">'
        '<div class="data-item" data-field-key="copper_balance" data-owning-package="5.2">'
        '<span class="data-label">copper_balance:</span>'
        '<span class="data-value">500 gp &mdash; migration deferred (package 5.2)</span>'
        '</div></div>'
    )
    with pytest.raises(AssertionError, match=r"Deferred field 'copper_balance' must have value text exactly"):
        validate_deferred_fields_strict(bad_html, deferred)


def test_falsification_deferred_injected_control_rejected() -> None:
    """14c2. Falsification (F4): Deferred field carrying an editable/hidden control fails deferred validator."""
    deferred = (MigrationDeferred(field_key="copper_balance", owning_package="5.2"),)
    bad_html = (
        '<div class="data-grid" data-section="deferred-fields">'
        '<div class="data-item" data-field-key="copper_balance" data-owning-package="5.2">'
        '<span class="data-label">copper_balance:</span>'
        '<span class="data-value">migration deferred (package 5.2)</span>'
        '<input type="hidden" name="copper_balance" value="500">'
        '</div></div>'
    )
    with pytest.raises(AssertionError, match=r"Forbidden control '<input' found in deferred entry 'copper_balance'"):
        validate_deferred_fields_strict(bad_html, deferred)


def test_falsification_portrait_image_url_rejected() -> None:
    """14d. Falsification: Injected non-emblem portrait <img> tag fails portrait fallback validator."""
    bad_html = '<div><img src="/static/portraits/thorin.png" alt="Thorin"></div>'
    with pytest.raises(AssertionError, match=r"Forbidden non-emblem <img> element found in rendered HTML"):
        validate_portrait_fallback_strict(bad_html)


def test_falsification_hidden_authoritative_field_rejected() -> None:
    """14e. Falsification (F5): Injected hidden authoritative control fails zero-mutation validator."""
    bad_html = '<div><div data-authority="guild_council">Council Override</div></div>'
    with pytest.raises(AssertionError, match=r"Forbidden hidden council authority found in member view"):
        validate_zero_mutation_controls(bad_html, "test_page.html")


def test_falsification_btn_styled_duplicate_action_rejected() -> None:
    """14f. Falsification (F5): Injected button-styled duplicate action fails zero-mutation validator."""
    bad_html = '<article class="character-card"><a href="/v1/characters/1" class="btn btn-secondary btn-sm">View details</a></article>'
    with pytest.raises(AssertionError, match=r"Forbidden button-styled element found in test_page\.html"):
        validate_zero_mutation_controls(bad_html, "test_page.html")


def test_falsification_genuine_active_and_used_selector_passes() -> None:
    """R2-3 positive: Genuine production CSS and Step 5 templates pass full selector validator."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1
    css_text = css_files[0].read_text(encoding="utf-8")
    template_texts = [
        (TEMPLATE_ROOT / "my_characters.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "character_detail.html").read_text(encoding="utf-8"),
    ]
    validate_css_and_template_selector_scope(css_text, template_texts, STEP_5_SELECTORS, PROHIBITED_LATER_STEP_SELECTORS)


def test_falsification_permitted_active_selector_not_used_in_template_fails() -> None:
    """R2-3 negative: Permitted active selector that is NOT used in either Step 5 template fails validator."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1
    css_text = css_files[0].read_text(encoding="utf-8") + "\n.extra-permitted-badge { color: blue; }\n"
    template_texts = [
        (TEMPLATE_ROOT / "my_characters.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "character_detail.html").read_text(encoding="utf-8"),
    ]
    mutated_required = STEP_5_SELECTORS + (".extra-permitted-badge",)
    with pytest.raises(AssertionError, match=r"Required selector '\.extra-permitted-badge' is not used in any Step 5 template"):
        validate_css_and_template_selector_scope(css_text, template_texts, mutated_required, PROHIBITED_LATER_STEP_SELECTORS)


def test_falsification_selector_mentioned_only_in_single_line_css_comment_fails() -> None:
    """R2-3 negative: Selector mentioned only in a single-line CSS comment fails validator."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1
    orig_css = css_files[0].read_text(encoding="utf-8")
    mutated_css = remove_css_selector_rule_in_memory(orig_css, ".empty-icon")
    mutated_css += "\n/* .empty-icon { color: red; } */\n"
    template_texts = [
        (TEMPLATE_ROOT / "my_characters.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "character_detail.html").read_text(encoding="utf-8"),
    ]
    with pytest.raises(AssertionError, match=r"Missing required Step 5 selector in active CSS: \.empty-icon"):
        validate_css_and_template_selector_scope(mutated_css, template_texts, STEP_5_SELECTORS, PROHIBITED_LATER_STEP_SELECTORS)


def test_falsification_selector_mentioned_only_in_multiline_css_comment_fails() -> None:
    """R2-3 negative: Selector mentioned only in a multiline CSS comment fails validator."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1
    orig_css = css_files[0].read_text(encoding="utf-8")
    mutated_css = remove_css_selector_rule_in_memory(orig_css, ".empty-icon")
    mutated_css += "\n/*\n * Multiline prose comment mentioning .empty-icon style\n */\n"
    template_texts = [
        (TEMPLATE_ROOT / "my_characters.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "character_detail.html").read_text(encoding="utf-8"),
    ]
    with pytest.raises(AssertionError, match=r"Missing required Step 5 selector in active CSS: \.empty-icon"):
        validate_css_and_template_selector_scope(mutated_css, template_texts, STEP_5_SELECTORS, PROHIBITED_LATER_STEP_SELECTORS)


def test_falsification_longer_selector_name_not_matching_exact_token_fails() -> None:
    """R2-3 negative: Longer selector name (prefix match) does not satisfy exact required selector."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1
    orig_css = css_files[0].read_text(encoding="utf-8")
    mutated_css = remove_css_selector_rule_in_memory(orig_css, ".character-card")
    mutated_css += "\n.character-card-extra { display: block; }\n"
    template_texts = [
        (TEMPLATE_ROOT / "my_characters.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "character_detail.html").read_text(encoding="utf-8"),
    ]
    with pytest.raises(AssertionError, match=r"Missing required Step 5 selector in active CSS: \.character-card"):
        validate_css_and_template_selector_scope(mutated_css, template_texts, STEP_5_SELECTORS, PROHIBITED_LATER_STEP_SELECTORS)


def test_falsification_declaration_string_value_not_matching_rule_header_fails() -> None:
    """R2-3 negative: Selector name in declaration property/string value does not satisfy rule definition."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1
    orig_css = css_files[0].read_text(encoding="utf-8")
    mutated_css = remove_css_selector_rule_in_memory(orig_css, ".character-card")
    mutated_css += '\n.unrelated-rule { --custom-val: ".character-card"; }\n'
    template_texts = [
        (TEMPLATE_ROOT / "my_characters.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "character_detail.html").read_text(encoding="utf-8"),
    ]
    with pytest.raises(AssertionError, match=r"Missing required Step 5 selector in active CSS: \.character-card"):
        validate_css_and_template_selector_scope(mutated_css, template_texts, STEP_5_SELECTORS, PROHIBITED_LATER_STEP_SELECTORS)


def test_falsification_class_appearing_only_in_jinja_comment_fails() -> None:
    """R2-3 negative: Class appearing only in a Jinja comment does not satisfy template usage."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1
    css_text = css_files[0].read_text(encoding="utf-8")

    # Remove empty-icon from active template HTML and put it only in a Jinja comment
    tmpl1_raw = (TEMPLATE_ROOT / "my_characters.html").read_text(encoding="utf-8")
    tmpl1_mutated = tmpl1_raw.replace('class="empty-icon"', 'class="removed-icon"')
    tmpl1_mutated += "\n{# <div class=\"empty-icon\">Commented out</div> #}\n"
    tmpl2 = (TEMPLATE_ROOT / "character_detail.html").read_text(encoding="utf-8")

    with pytest.raises(AssertionError, match=r"Required selector '\.empty-icon' is not used in any Step 5 template"):
        validate_css_and_template_selector_scope(css_text, [tmpl1_mutated, tmpl2], STEP_5_SELECTORS, PROHIBITED_LATER_STEP_SELECTORS)


def test_falsification_longer_template_class_token_fails() -> None:
    """R2-3 negative: Longer template class token does not satisfy exact required selector."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1
    css_text = css_files[0].read_text(encoding="utf-8")

    tmpl1_raw = (TEMPLATE_ROOT / "my_characters.html").read_text(encoding="utf-8")
    tmpl1_mutated = tmpl1_raw.replace('class="card character-card"', 'class="card character-card-extra"')
    tmpl2 = (TEMPLATE_ROOT / "character_detail.html").read_text(encoding="utf-8")

    with pytest.raises(AssertionError, match=r"Required selector '\.character-card' is not used in any Step 5 template"):
        validate_css_and_template_selector_scope(css_text, [tmpl1_mutated, tmpl2], STEP_5_SELECTORS, PROHIBITED_LATER_STEP_SELECTORS)


def test_falsification_unterminated_css_block_comment_fails_safely() -> None:
    """R2-3 negative: Unterminated CSS block comment fails safely with explicit error."""
    bad_css = "body { margin: 0; }\n/* unterminated block comment\n.empty-icon { color: red; }\n"
    with pytest.raises(AssertionError, match=r"Unterminated CSS block comment detected in stylesheet"):
        strip_css_comments(bad_css)


def test_falsification_prohibited_later_step_css_selector_rejected() -> None:
    """14g1. Falsification (F5): Injected later-step selector fails CSS scope check."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1
    css_text = css_files[0].read_text(encoding="utf-8") + "\n.council-console-card { background: red; }\n"
    template_texts = [
        (TEMPLATE_ROOT / "my_characters.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "character_detail.html").read_text(encoding="utf-8"),
    ]
    with pytest.raises(AssertionError, match=r"Prohibited selector found in active CSS rules: \.council-console-card"):
        validate_css_and_template_selector_scope(css_text, template_texts, STEP_5_SELECTORS, PROHIBITED_LATER_STEP_SELECTORS)


def test_falsification_unused_button_css_selector_rejected() -> None:
    """14g2. Falsification (F5): Injected unused later-step selector fails CSS scope check."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1
    css_text = css_files[0].read_text(encoding="utf-8") + "\n.diff-box { display: flex; }\n"
    template_texts = [
        (TEMPLATE_ROOT / "my_characters.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "character_detail.html").read_text(encoding="utf-8"),
    ]
    with pytest.raises(AssertionError, match=r"Prohibited selector found in active CSS rules: \.diff-box"):
        validate_css_and_template_selector_scope(css_text, template_texts, STEP_5_SELECTORS, PROHIBITED_LATER_STEP_SELECTORS)


def test_falsification_css_byte_tampering_fails_manifest_and_fingerprint_shared_helper(tmp_path: Path) -> None:
    """14h. Falsification (F5): Temporary CSS byte tampering fails shared manifest/fingerprint validator."""
    tmp_static = tmp_path / "static"
    tmp_static.mkdir(parents=True)
    tmp_manifest = tmp_static / "asset-integrity.sha256"

    # Copy files
    for item in STATIC_ROOT.rglob("*"):
        if item.is_file():
            rel = item.relative_to(STATIC_ROOT)
            dest = tmp_static / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(item.read_bytes())

    # 1. Shared helper passes on exact copy
    validate_asset_manifest_and_fingerprint(tmp_static, tmp_manifest)

    # 2. Tamper 1 byte in temporary CSS
    temp_css_files = list((tmp_static / "css").glob("*.css"))
    assert len(temp_css_files) == 1
    temp_css = temp_css_files[0]
    temp_css.write_bytes(temp_css.read_bytes() + b"\n/* tamper */")

    # 3. Shared helper fails with manifest mismatch
    with pytest.raises(AssertionError, match=r"Manifest integrity check failed"):
        validate_asset_manifest_and_fingerprint(tmp_static, tmp_manifest)

    # 4. Production bytes remain completely untouched
    prod_css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(prod_css_files) == 1
    assert compute_sha256(prod_css_files[0]) == "58a9b9eed003c44b0b4e63d25910ecd704cdac03b0dcea6d2e105d63b8756649"
    assert compute_sha256(MANIFEST_PATH) == "299a8a26ec64e862677e61e46cb432c632fc3d9dc48c29f0648dc03b9f31bf2b"
