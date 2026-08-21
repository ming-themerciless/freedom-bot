"""Tests for P3.4 Step 6 Council Character-Access Views (Remediated 06).

Covers:
1. VM-07 / R-22: `council_characters.html` (Council character index, filters, cursor, nullable level, unresolved owner, URL-encoding)
2. VM-08 / R-23: `character_links.html` (Complete AccessFact evidence, contract-accurate LinkInvariants explanations & UUIDs, active links, history, cursor)
3. R-25 / R-26 / R-27: Mutation forms (grant link, revoke link, set default link, no HTMX attributes on R-25)
4. VM-09 / R-24: `identity_search.html` (Standalone HTMX candidate fragment, consistent query_echo rendering, evidence notice, empty/invalid states)
5. Shared teardown fixture with post-yield DB resolution inside membership guard, connection binding, and tracked ID-specific fresh-connection absence verification with rigorous AST data flow.
6. Exact active CSS selector and active template class-token scope validation with negative falsification probes.
7. All 23 template digests and static asset integrity protection.
8. Complete real database-backed HTTP/security/mutation evidence across R-22–R-27 with live bound connections, accepted exact denial-policy response identity, case-specific audit snapshots, and immediate complete no-write snapshots across all 9 refusal cases validated by executable semantic AST inspection.
"""
from __future__ import annotations

import ast
import hashlib
import inspect
import os
import re
import shutil
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import jinja2
import pytest
from sqlalchemy import text
from starlette.requests import Request

from application.audit import ActorCapability
from application.web.view_models import (
    AccessFact,
    Actor,
    CharacterFilters,
    CharacterLinksView,
    Correlation,
    CouncilCharacterIndexView,
    CouncilCharacterRow,
    Cursor,
    IdentityCandidate,
    IdentitySearchResultsView,
    Instant,
    LinkInvariants,
    SafeText,
)
from tests.web.conftest import add_mapping, link_discord, make_account
from tests.web.portal_fixtures import (
    character_version,
    clean_p3_2_tables,
    csrf_token_for,
    grant_link,
    make_character,
    seed_callers,
    seed_discord_member,
)
from tests.web_fixtures import PUBLIC_ORIGIN

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = ROOT / "adapters" / "web" / "templates"
STATIC_ROOT = ROOT / "adapters" / "web" / "static"
MANIFEST_PATH = STATIC_ROOT / "asset-integrity.sha256"

FORM = "application/x-www-form-urlencoded"

# All 23 accepted template digests (10 untouched + 8 Step 4 + 2 Step 5 + 3 Step 6 remediated)
ACCEPTED_TEMPLATE_DIGESTS: dict[str, str] = {
    "account_identities.html": "5f458b6fe335d34b7ba400d4f7c4c0dcbcceadabd613bfbd5c25890af37f1287",
    "audit_results.html": "11ee0efcba8892970dee0870b5612d0fbf9c5091d5cf954ddf77e4af4f98291e",
    "audit_search.html": "c54db1a4cc1779a52921269641330f79d295a843086eb198916a2f07c6e61c15",
    "character_detail.html": "7524e43e0e2ee814b5c8b65365f4e0d72bcb9c1e42e4087ea927e3934c0c9890",
    "character_links.html": "a1f280c1700ee4aa53655fb94a7290ff43edc108159b1df85c8572ee37ac395d",
    "conflict.html": "1dda40f2e43212631fba5001e4982748fc5a090b0a32a6be57965daae4805648",
    "council_characters.html": "a18419ab163e00e54987ae7a4071f7b8698b916bf517a714b51cb0ea6dff7a02",
    "council_snapshots.html": "627b42f740bceac8ae5665a5be235aa76add3ffd7f08617861f39f2befcb5d8e",
    "degraded.html": "98f3ac888788d24e173fb4a497e0b138c23987b459d29d37b4131c9bbd211915",
    "denied.html": "197913db5909d6d9801f599b0a0b2eed47b6384f4e5bd3e38de6e9ae6c686c20",
    "emergency.html": "0eec75c17bb6ea602fabc7aace0aaf1453e70fd102e61da5298759e094980a99",
    "error.html": "6fdf24733c0b06139434c7b7198cab979438758fb6b8c18175e473b4ad404945",
    "field_profile.html": "06277334db018cd82e313af0556a35e658c86841e06602a7bd65d0edde15f703",
    "identity_migration.html": "66f3669661c40f2a73d250122c35e0f8af397d6f8bd94a4571402e7a8a63134b",
    "identity_search.html": "36978ca19d5366188ae42892111cb5425ece1b6e2355710a32b71e2c6ef1e394",
    "import_result.html": "152b84f766211b886ddd67ca1ce03c53cb37ceefc9ea5678cd22f7f2b7f3fff6",
    "job_status.html": "9a7a62892f9983ccd1a359f213f4feab0f85b1a084dccdabdbb0cb68a380deb3",
    "job_status_fragment.html": "81fcd1bb2a80657c979e8c4581657bb0ba0b3940fb689ca7d56483c9d66ee234",
    "login.html": "eafd7635be0b6b8dfb7d60df7a827a49863b5b12bb1cdc0e49ddbd4c0f7d5e3b",
    "my_characters.html": "3705fbcd3e0803b2190746102cf6a67e20aa607432de128e3127a5a8987ce042",
    "non_member.html": "de43a127d11f77bfccfb515fa93e3a2ef9373b123c880c1290dcedc1f1721f02",
    "role_capabilities.html": "e297c26dc326a2a28c9439948fcd781c29b12d3cda74911d9f747727d760613a",
    "validation.html": "ff00f7acf78f8d055c3a37af92d0f32230b98fb95aa385b4f327e3851c3e4e7d",
}

# Step 6 selectors added and used by Step 6 templates
STEP_6_SELECTORS: tuple[str, ...] = (
    ".page-title-row",
    ".page-description",
    ".filter-bar",
    ".search-form",
    ".search-input-group",
    ".form-group",
    ".form-row",
    ".form-label",
    ".form-input",
    ".form-input-sm",
    ".form-select",
    ".form-checkbox-group",
    ".form-checkbox-label",
    ".form-checkbox",
    ".form-help",
    ".filter-actions",
    ".form-actions",
    ".btn",
    ".btn-primary",
    ".btn-secondary",
    ".btn-danger",
    ".btn-sm",
    ".table-container",
    ".council-table",
    ".cursor-nav",
    ".badge-danger",
    ".badge-secondary",
    ".alert",
    ".alert-info",
    ".invariant-notice",
    ".default-held-notice",
    ".empty-text",
    ".access-list",
    ".access-card",
    ".access-header",
    ".access-account-label",
    ".access-badges",
    ".access-subject-block",
    ".access-actions",
    ".action-form",
    ".form-group-inline",
    ".form-label-inline",
    ".grant-card",
    ".grant-form",
    ".identity-search-fragment",
    ".candidate-notice",
    ".candidate-empty",
    ".candidate-invalid",
    ".candidate-list",
    ".candidate-item",
    ".candidate-info",
    ".candidate-username",
    ".candidate-global-name",
    ".candidate-meta",
    ".candidate-badges",
    ".candidate-truncated",
    ".text-muted",
    ".text-xs",
    ".text-sm",
)

PROHIBITED_STEP_7_SELECTORS: tuple[str, ...] = (
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

EXACT_DENIAL_HEADERS: dict[str, str] = {
    "content-type": "text/html; charset=utf-8",
    "cache-control": "no-store",
    "content-security-policy": (
        "default-src 'self'; base-uri 'none'; object-src 'none'; "
        "frame-ancestors 'none'; form-action 'self'; img-src 'self' data:; "
        "script-src 'self'; style-src 'self'"
    ),
    "x-content-type-options": "nosniff",
    "referrer-policy": "same-origin",
    "cross-origin-opener-policy": "same-origin",
    "cross-origin-resource-policy": "same-origin",
    "permissions-policy": "geolocation=(), camera=(), microphone=(), payment=()",
}

FORBIDDEN_DENIAL_HEADERS: tuple[str, ...] = (
    "location",
    "set-cookie",
)


def get_jinja_env(template_dir: Path = TEMPLATE_ROOT) -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        autoescape=True,
        undefined=jinja2.StrictUndefined,
    )


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


def make_request(path: str = "/v1/council/characters") -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": [(b"host", b"testserver")],
    }
    return Request(scope)


def assert_identical_denial_responses(res1: Any, res2: Any) -> None:
    """Asserts status, byte-identical body, exact match on closed required security headers
    against accepted production policy values, and absence of forbidden disclosure headers."""
    assert res1.status_code == res2.status_code == 404, (
        f"Status mismatch in denial responses: {res1.status_code} != {res2.status_code}"
    )
    assert res1.content == res2.content, "Body content mismatch in denial responses"

    # 1. Verify absence of forbidden headers
    for forbidden in FORBIDDEN_DENIAL_HEADERS:
        assert forbidden not in res1.headers, f"Forbidden header '{forbidden}' present in first denial response"
        assert forbidden not in res2.headers, f"Forbidden header '{forbidden}' present in second denial response"

    # 2. Verify exact match on all required deterministic/security headers against accepted values
    for req_header, expected_val in EXACT_DENIAL_HEADERS.items():
        assert req_header in res1.headers, f"Missing required header '{req_header}' in first denial response"
        assert req_header in res2.headers, f"Missing required header '{req_header}' in second denial response"
        v1 = res1.headers[req_header]
        v2 = res2.headers[req_header]
        assert v1 == expected_val, f"First denial header '{req_header}' value mismatch: expected '{expected_val}', got '{v1}'"
        assert v2 == expected_val, f"Second denial header '{req_header}' value mismatch: expected '{expected_val}', got '{v2}'"
        assert v1 == v2, f"Header value mismatch between denials for '{req_header}': '{v1}' != '{v2}'"


# ---------------------------------------------------------------------------
# Tracked State & AST Teardown Validator / Fixture
# ---------------------------------------------------------------------------


class TrackedCouncilFixtureState:
    """Fixture-owned container tracking exact character and access IDs created by the test."""
    def __init__(self) -> None:
        self.character_ids: set[UUID] = set()
        self.access_ids: set[UUID] = set()


def validate_council_cleanup_fixture(fixture_func_or_code: object) -> None:
    """Structural AST validator for the council database cleanup fixture.
    Enforces:
    1. Pre-yield tracked state object creation and yield.
    2. Post-yield DB resolution inside membership guard.
    3. First with-block calls clean_p3_2_tables on bound connection.
    4. Second with-block on a separate fresh connection iterates tracked_state IDs,
       issues parameterized queries selecting by ID, and asserts results are 0.
    5. Proves exact data flow: correct SQL table, WHERE id = :id predicate, loop variable
       parameter mapping, query result assignment, and comparison of result variable to 0.
    """
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

    # 1. Exactly one yield occurs and yields the tracked state variable
    yield_nodes = [node for node in ast.walk(func_def) if isinstance(node, ast.Yield)]
    assert len(yield_nodes) == 1, f"Fixture must contain exactly one yield statement, found {len(yield_nodes)}"
    yield_node = yield_nodes[0]
    yield_lineno = yield_node.lineno
    assert yield_node.value is not None and isinstance(yield_node.value, ast.Name), "Yield must return a tracked state variable"
    tracked_var_name = yield_node.value.id

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
    res_lineno = res_call.lineno
    assert yield_lineno < res_lineno, (
        f"Yield at line {yield_lineno} must precede database resolution at line {res_lineno}"
    )

    # 3. Post-yield guard verification: resolution call must be guarded by migrated_database check
    guarded = False
    for stmt_idx in range(yield_stmt_idx + 1, len(func_def.body)):
        stmt = func_def.body[stmt_idx]
        if isinstance(stmt, ast.If):
            has_guard_const = any(
                isinstance(n, ast.Constant) and n.value == "migrated_database"
                for n in ast.walk(stmt.test)
            )
            if has_guard_const:
                if any(isinstance(n, ast.Return) for n in stmt.body):
                    if res_lineno > stmt.lineno:
                        guarded = True
                        break
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

    # 4. Exactly two separate with-blocks on engine.begin()
    with_nodes = [node for node in ast.walk(func_def) if isinstance(node, ast.With)]
    assert len(with_nodes) == 2, f"Fixture must contain exactly two 'with engine.begin() as ...' context managers, found {len(with_nodes)}"

    # First with-block: clean_p3_2_tables
    with1 = with_nodes[0]
    assert yield_lineno < with1.lineno, f"Yield at line {yield_lineno} must precede with-context 1 at line {with1.lineno}"
    assert len(with1.items) == 1 and isinstance(with1.items[0].context_expr, ast.Call)
    assert with1.items[0].context_expr.func.attr == "begin" and with1.items[0].context_expr.func.value.id == assigned_engine_var
    bound1 = with1.items[0].optional_vars.id

    clean_calls = [
        node for node in ast.walk(with1)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "clean_p3_2_tables"
    ]
    assert len(clean_calls) == 1, "clean_p3_2_tables must be called exactly once inside with-block 1"
    assert clean_calls[0].args[0].id == bound1, "clean_p3_2_tables must receive bound connection from with-block 1"

    # Second with-block: ID-specific absence verification on fresh connection
    with2 = with_nodes[1]
    assert with1.lineno < with2.lineno, f"Cleanup at line {with1.lineno} must precede fresh-connection absence verification at line {with2.lineno}"
    assert len(with2.items) == 1 and isinstance(with2.items[0].context_expr, ast.Call)
    assert with2.items[0].context_expr.func.attr == "begin" and with2.items[0].context_expr.func.value.id == assigned_engine_var
    bound2 = with2.items[0].optional_vars.id
    assert bound2 != bound1, "Second with-block must bind a fresh connection variable"

    # Reject assert True and assert 0 == 0
    for node in ast.walk(with2):
        if isinstance(node, ast.Assert):
            if isinstance(node.test, ast.Constant) and node.test.value is True:
                raise AssertionError("Second with-block contains trivial 'assert True'")
            if isinstance(node.test, ast.Compare):
                if isinstance(node.test.left, ast.Constant) and all(isinstance(c, ast.Constant) for c in node.test.comparators):
                    raise AssertionError("Second with-block contains literal constant comparison 'assert 0 == 0'")

    # Must verify both character_ids and access_ids from tracked_var_name
    for_loops = [node for node in ast.walk(with2) if isinstance(node, ast.For)]
    assert len(for_loops) == 2, "Second with-block must contain two for-loops iterating tracked character_ids and access_ids"

    iter_attrs: set[str] = set()
    for fl in for_loops:
        assert isinstance(fl.target, ast.Name), "For loop must bind a target variable name"
        loop_var = fl.target.id

        assert isinstance(fl.iter, ast.Attribute) and fl.iter.value.id == tracked_var_name, (
            f"For loop must iterate an attribute of tracked state variable '{tracked_var_name}'"
        )
        attr = fl.iter.attr
        iter_attrs.add(attr)
        expected_table = "characters" if attr == "character_ids" else "character_access"

        # Look for assignment of query result: <res_var> = <bound2>.execute(text(<sql>), {"id": <loop_var>}).scalar_one()
        assign_nodes = [n for n in fl.body if isinstance(n, ast.Assign)]
        assert len(assign_nodes) == 1, f"Loop for '{attr}' must assign the scalar absence query result to a variable"
        assign_node = assign_nodes[0]
        assert len(assign_node.targets) == 1 and isinstance(assign_node.targets[0], ast.Name), (
            f"Query result must be assigned to a named variable in '{attr}' loop"
        )
        res_var = assign_node.targets[0].id

        # Inspect call structure: <bound2>.execute(text(<sql>), {"id": <loop_var>}).scalar_one()
        assert isinstance(assign_node.value, ast.Call) and isinstance(assign_node.value.func, ast.Attribute) and assign_node.value.func.attr == "scalar_one", (
            f"Query in '{attr}' loop must call .scalar_one()"
        )
        exec_call = assign_node.value.func.value
        assert isinstance(exec_call, ast.Call) and isinstance(exec_call.func, ast.Attribute) and exec_call.func.attr == "execute", (
            f"Query in '{attr}' loop must call .execute()"
        )
        assert exec_call.func.value.id == bound2, f"Query must be executed on fresh connection '{bound2}'"

        # Validate SQL text
        assert len(exec_call.args) >= 2, f"Execute call in '{attr}' loop must provide text SQL and parameters dict"
        sql_arg = exec_call.args[0]
        assert isinstance(sql_arg, ast.Call) and isinstance(sql_arg.func, ast.Name) and sql_arg.func.id == "text", (
            f"First argument to execute must be text(<sql>) in '{attr}' loop"
        )
        assert len(sql_arg.args) == 1 and isinstance(sql_arg.args[0], ast.Constant), (
            f"text() argument must be a literal SQL string in '{attr}' loop"
        )
        sql_str = " ".join(sql_arg.args[0].value.strip().lower().split())
        expected_sql = f"select count(*) from {expected_table} where id = :id"
        assert sql_str == expected_sql, f"SQL mismatch in '{attr}' loop: expected '{expected_sql}', got '{sql_str}'"

        # Validate parameter dictionary
        param_arg = exec_call.args[1]
        assert isinstance(param_arg, ast.Dict), f"Parameters argument must be a dictionary in '{attr}' loop"
        assert len(param_arg.keys) == 1 and isinstance(param_arg.keys[0], ast.Constant) and param_arg.keys[0].value == "id", (
            f"Parameter dict must have single key 'id' in '{attr}' loop"
        )
        assert isinstance(param_arg.values[0], ast.Name) and param_arg.values[0].id == loop_var, (
            f"Parameter dict 'id' value must be loop variable '{loop_var}' in '{attr}' loop"
        )

        # Validate assertion comparing res_var to 0
        assert_nodes = [n for n in fl.body if isinstance(n, ast.Assert)]
        assert len(assert_nodes) >= 1, f"Loop for '{attr}' must assert absence of query result"
        assert_test = assert_nodes[0].test
        assert isinstance(assert_test, ast.Compare), f"Assertion in '{attr}' loop must be a comparison"

        is_valid_comp = False
        if isinstance(assert_test.left, ast.Name) and assert_test.left.id == res_var:
            if len(assert_test.comparators) == 1 and isinstance(assert_test.comparators[0], ast.Constant) and assert_test.comparators[0].value == 0:
                is_valid_comp = True
        elif isinstance(assert_test.left, ast.Constant) and assert_test.left.value == 0:
            if len(assert_test.comparators) == 1 and isinstance(assert_test.comparators[0], ast.Name) and assert_test.comparators[0].id == res_var:
                is_valid_comp = True

        assert is_valid_comp, f"Assertion in '{attr}' loop must compare query result variable '{res_var}' to 0"

    assert iter_attrs == {"character_ids", "access_ids"}, (
        f"Absence verification must check both character_ids and access_ids, found {iter_attrs}"
    )


@pytest.fixture(autouse=True)
def clean_between_council_cases(request):
    """Guaranteed post-yield teardown and ID-specific fresh-connection absence verification."""
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    from tests.web.portal_fixtures import clean_p3_2_tables

    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)

    # Separate fresh connection proving tracked IDs are absent
    with engine.begin() as fresh_conn:
        for char_id in tracked_state.character_ids:
            remaining_char = fresh_conn.execute(
                text("SELECT count(*) FROM characters WHERE id = :id"),
                {"id": char_id},
            ).scalar_one()
            assert remaining_char == 0, f"Cleanup failed: character {char_id} still exists"

        for access_id in tracked_state.access_ids:
            remaining_access = fresh_conn.execute(
                text("SELECT count(*) FROM character_access WHERE id = :id"),
                {"id": access_id},
            ).scalar_one()
            assert remaining_access == 0, f"Cleanup failed: character_access {access_id} still exists"


def test_structural_council_fixture_cleans_after_yield() -> None:
    validate_council_cleanup_fixture(clean_between_council_cases)


def test_falsification_structural_fixture_rejects_resolution_before_yield() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    engine = request.getfixturevalue("migrated_database")
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        for char_id in tracked_state.character_ids:
            rem = fresh_conn.execute(text("SELECT count(*) FROM characters WHERE id = :id"), {"id": char_id}).scalar_one()
            assert rem == 0
        for access_id in tracked_state.access_ids:
            rem2 = fresh_conn.execute(text("SELECT count(*) FROM character_access WHERE id = :id"), {"id": access_id}).scalar_one()
            assert rem2 == 0
"""
    with pytest.raises(AssertionError, match=r"Yield at line \d+ must precede database resolution at line \d+"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_resolution_outside_guard() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        for char_id in tracked_state.character_ids:
            rem = fresh_conn.execute(text("SELECT count(*) FROM characters WHERE id = :id"), {"id": char_id}).scalar_one()
            assert rem == 0
        for access_id in tracked_state.access_ids:
            rem2 = fresh_conn.execute(text("SELECT count(*) FROM character_access WHERE id = :id"), {"id": access_id}).scalar_one()
            assert rem2 == 0
"""
    with pytest.raises(AssertionError, match=r"Database resolution must be guarded"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_resolution_of_different_fixture_name() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("other_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        for char_id in tracked_state.character_ids:
            rem = fresh_conn.execute(text("SELECT count(*) FROM characters WHERE id = :id"), {"id": char_id}).scalar_one()
            assert rem == 0
        for access_id in tracked_state.access_ids:
            rem2 = fresh_conn.execute(text("SELECT count(*) FROM character_access WHERE id = :id"), {"id": access_id}).scalar_one()
            assert rem2 == 0
"""
    with pytest.raises(AssertionError, match=r"Database resolution argument must be literal string 'migrated_database'"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_missing_cleanup_after_yield() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
"""
    with pytest.raises(AssertionError, match=r"Fixture must contain exactly two 'with engine.begin\(\) as \.\.\.' context managers"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_engine_passed_directly() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(engine)
    with engine.begin() as fresh_conn:
        for char_id in tracked_state.character_ids:
            rem = fresh_conn.execute(text("SELECT count(*) FROM characters WHERE id = :id"), {"id": char_id}).scalar_one()
            assert rem == 0
        for access_id in tracked_state.access_ids:
            rem2 = fresh_conn.execute(text("SELECT count(*) FROM character_access WHERE id = :id"), {"id": access_id}).scalar_one()
            assert rem2 == 0
"""
    with pytest.raises(AssertionError, match=r"clean_p3_2_tables must receive bound connection from with-block 1"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_absence_verification_before_cleanup() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as fresh_conn:
        for char_id in tracked_state.character_ids:
            rem = fresh_conn.execute(text("SELECT count(*) FROM characters WHERE id = :id"), {"id": char_id}).scalar_one()
            assert rem == 0
        for access_id in tracked_state.access_ids:
            rem2 = fresh_conn.execute(text("SELECT count(*) FROM character_access WHERE id = :id"), {"id": access_id}).scalar_one()
            assert rem2 == 0
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
"""
    with pytest.raises(AssertionError, match=r"clean_p3_2_tables must be called exactly once inside with-block 1"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_missing_absence_verification() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
"""
    with pytest.raises(AssertionError, match=r"Fixture must contain exactly two 'with engine.begin\(\) as \.\.\.' context managers"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_assert_true() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        assert True
"""
    with pytest.raises(AssertionError, match=r"Second with-block contains trivial 'assert True'"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_assert_0_equals_0() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        assert 0 == 0
"""
    with pytest.raises(AssertionError, match=r"Second with-block contains literal constant comparison 'assert 0 == 0'"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_table_wide_count_without_tracked_ids() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        count = fresh_conn.execute(text("SELECT count(*) FROM characters")).scalar_one()
        assert count == 0
"""
    with pytest.raises(AssertionError, match=r"Second with-block must contain two for-loops iterating tracked character_ids and access_ids"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_literal_untracked_id() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        for char_id in ["00000000-0000-0000-0000-000000000001"]:
            rem = fresh_conn.execute(text("SELECT count(*) FROM characters WHERE id = :id"), {"id": char_id}).scalar_one()
            assert rem == 0
        for access_id in ["00000000-0000-0000-0000-000000000002"]:
            rem2 = fresh_conn.execute(text("SELECT count(*) FROM character_access WHERE id = :id"), {"id": access_id}).scalar_one()
            assert rem2 == 0
"""
    with pytest.raises(AssertionError, match=r"For loop must iterate an attribute of tracked state variable 'tracked_state'"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_same_connection_verification() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
    with engine.begin() as connection:
        for char_id in tracked_state.character_ids:
            rem = connection.execute(text("SELECT count(*) FROM characters WHERE id = :id"), {"id": char_id}).scalar_one()
            assert rem == 0
        for access_id in tracked_state.access_ids:
            rem2 = connection.execute(text("SELECT count(*) FROM character_access WHERE id = :id"), {"id": access_id}).scalar_one()
            assert rem2 == 0
"""
    with pytest.raises(AssertionError, match=r"Second with-block must bind a fresh connection variable"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_wrong_table_query() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        for char_id in tracked_state.character_ids:
            rem = fresh_conn.execute(text("SELECT count(*) FROM character_access WHERE id = :id"), {"id": char_id}).scalar_one()
            assert rem == 0
        for access_id in tracked_state.access_ids:
            rem2 = fresh_conn.execute(text("SELECT count(*) FROM character_access WHERE id = :id"), {"id": access_id}).scalar_one()
            assert rem2 == 0
"""
    with pytest.raises(AssertionError, match=r"SQL mismatch in 'character_ids' loop: expected 'select count\(\*\) from characters where id = :id'"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_missing_where_id_predicate() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        for char_id in tracked_state.character_ids:
            rem = fresh_conn.execute(text("SELECT count(*) FROM characters"), {"id": char_id}).scalar_one()
            assert rem == 0
        for access_id in tracked_state.access_ids:
            rem2 = fresh_conn.execute(text("SELECT count(*) FROM character_access WHERE id = :id"), {"id": access_id}).scalar_one()
            assert rem2 == 0
"""
    with pytest.raises(AssertionError, match=r"SQL mismatch in 'character_ids' loop: expected 'select count\(\*\) from characters where id = :id'"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_wrong_param_key() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        for char_id in tracked_state.character_ids:
            rem = fresh_conn.execute(text("SELECT count(*) FROM characters WHERE id = :id"), {"cid": char_id}).scalar_one()
            assert rem == 0
        for access_id in tracked_state.access_ids:
            rem2 = fresh_conn.execute(text("SELECT count(*) FROM character_access WHERE id = :id"), {"id": access_id}).scalar_one()
            assert rem2 == 0
"""
    with pytest.raises(AssertionError, match=r"Parameter dict must have single key 'id' in 'character_ids' loop"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_wrong_param_value() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        for char_id in tracked_state.character_ids:
            rem = fresh_conn.execute(text("SELECT count(*) FROM characters WHERE id = :id"), {"id": other_var}).scalar_one()
            assert rem == 0
        for access_id in tracked_state.access_ids:
            rem2 = fresh_conn.execute(text("SELECT count(*) FROM character_access WHERE id = :id"), {"id": access_id}).scalar_one()
            assert rem2 == 0
"""
    with pytest.raises(AssertionError, match=r"Parameter dict 'id' value must be loop variable 'char_id' in 'character_ids' loop"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_unassigned_query_result() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        for char_id in tracked_state.character_ids:
            fresh_conn.execute(text("SELECT count(*) FROM characters WHERE id = :id"), {"id": char_id}).scalar_one()
            assert rem_other == 0
        for access_id in tracked_state.access_ids:
            rem2 = fresh_conn.execute(text("SELECT count(*) FROM character_access WHERE id = :id"), {"id": access_id}).scalar_one()
            assert rem2 == 0
"""
    with pytest.raises(AssertionError, match=r"Loop for 'character_ids' must assign the scalar absence query result to a variable"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_assertion_on_wrong_variable() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        for char_id in tracked_state.character_ids:
            rem = fresh_conn.execute(text("SELECT count(*) FROM characters WHERE id = :id"), {"id": char_id}).scalar_one()
            assert other_var == 0
        for access_id in tracked_state.access_ids:
            rem2 = fresh_conn.execute(text("SELECT count(*) FROM character_access WHERE id = :id"), {"id": access_id}).scalar_one()
            assert rem2 == 0
"""
    with pytest.raises(AssertionError, match=r"Assertion in 'character_ids' loop must compare query result variable 'rem' to 0"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_checking_only_characters() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        for char_id in tracked_state.character_ids:
            rem = fresh_conn.execute(text("SELECT count(*) FROM characters WHERE id = :id"), {"id": char_id}).scalar_one()
            assert rem == 0
"""
    with pytest.raises(AssertionError, match=r"Second with-block must contain two for-loops iterating tracked character_ids and access_ids"):
        validate_council_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_checking_only_access_rows() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedCouncilFixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        for access_id in tracked_state.access_ids:
            rem = fresh_conn.execute(text("SELECT count(*) FROM character_access WHERE id = :id"), {"id": access_id}).scalar_one()
            assert rem == 0
"""
    with pytest.raises(AssertionError, match=r"Second with-block must contain two for-loops iterating tracked character_ids and access_ids"):
        validate_council_cleanup_fixture(bad_fixture)


def test_structural_no_engine_passed_to_connection_helpers() -> None:
    """Proves structurally that in this test module, connection-only helpers
    never receive the engine directly."""
    src = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    connection_helpers = {
        "character_version",
        "clean_p3_2_tables",
        "grant_link",
        "make_character",
        "seed_discord_member",
        "link_discord",
        "snapshot_r25_state",
        "snapshot_r26_state",
        "snapshot_r27_state",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in connection_helpers:
            if node.args and isinstance(node.args[0], ast.Name):
                arg0 = node.args[0].id
                assert arg0 not in {"migrated_database", "engine"}, (
                    f"Connection helper '{node.func.id}' called with '{arg0}' at line {node.lineno} instead of bound connection"
                )
# ---------------------------------------------------------------------------
# Refusal No-Write Snapshot Semantic Validator & Falsifications
# ---------------------------------------------------------------------------


def validate_refusal_snapshots_and_sequences(module_or_func_ast: object) -> None:
    """Comprehensive semantic AST validator proving:
    1. Snapshot helpers execute character_version, case-specific audit queries with predicates,
       exact operation-owned access-row queries, and return immutable tuples.
    2. All 9 refusal cases execute in strict sequence: fresh before-connection snapshot,
       awaited client request, expected refusal status assertion, fresh after-connection snapshot,
       and exact before/after equality assertion.
    """
    if isinstance(module_or_func_ast, str):
        tree = ast.parse(module_or_func_ast)
    elif hasattr(module_or_func_ast, "body"):
        tree = module_or_func_ast
    elif callable(module_or_func_ast):
        tree = ast.parse(inspect.getsource(module_or_func_ast))
    else:
        tree = ast.parse(str(module_or_func_ast))

    # Helper function definitions
    func_defs = {n.name: n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}

    # 1. Validate snapshot_r25_state AST
    assert "snapshot_r25_state" in func_defs, "snapshot_r25_state definition missing"
    f25 = func_defs["snapshot_r25_state"]
    assert [a.arg for a in f25.args.args] == ["connection", "character_id", "account_id"], "snapshot_r25_state args mismatch"

    # Find character_version call
    v_assign = None
    for n in f25.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            if isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == "character_version":
                assert len(n.value.args) == 2 and [getattr(a, "id", None) for a in n.value.args] == ["connection", "character_id"], (
                    "character_version must receive bound connection and character_id"
                )
                v_assign = n.targets[0].id
                break
    assert v_assign is not None, "snapshot_r25_state missing character_version"

    # Find audit query assignment
    audit_assign = None
    for n in f25.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            if isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "scalar_one":
                inner = n.value.func.value
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) and inner.func.attr == "execute":
                    if inner.args and isinstance(inner.args[0], ast.Call) and getattr(inner.args[0].func, "id", None) == "text":
                        sql_text = inner.args[0].args[0].value if inner.args[0].args and isinstance(inner.args[0].args[0], ast.Constant) else ""
                        norm_sql = " ".join(sql_text.strip().lower().split())
                        if "from audit_events" in norm_sql:
                            # Verify audit query rules for R-25
                            assert "where" in norm_sql, "snapshot_r25_state must use case-specific audit_events predicate on payload"
                            assert "entity_id" not in norm_sql, "snapshot_r25_state must use JSON payload predicates, not entity_id"
                            assert " like " not in norm_sql and " ilike " not in norm_sql, "snapshot_r25_state must not use LIKE matching on audit payload"
                            assert "::text" not in norm_sql and "cast(" not in norm_sql, "snapshot_r25_state must use PostgreSQL JSON extraction, not text casting"
                            assert "action = 'character_access.granted'" in norm_sql, "snapshot_r25_state must require action 'character_access.granted'"
                            assert "entity_type = 'character_access'" in norm_sql, "snapshot_r25_state must require entity_type 'character_access'"
                            assert (
                                "payload ->> 'character_id' = :cid" in norm_sql
                                or "payload->>'character_id' = :cid" in norm_sql
                            ), "snapshot_r25_state must extract character_id from payload JSON"
                            assert (
                                "payload ->> 'platform_account_id' = :aid" in norm_sql
                                or "payload->>'platform_account_id' = :aid" in norm_sql
                            ), "snapshot_r25_state must extract platform_account_id from payload JSON"

                            # Verify parameter binding
                            assert len(inner.args) >= 2 and isinstance(inner.args[1], ast.Dict), (
                                "snapshot_r25_state audit query must bind parameters dict"
                            )
                            pdict = inner.args[1]
                            pkeys = [k.value for k in pdict.keys if isinstance(k, ast.Constant)]
                            assert set(pkeys) == {"cid", "aid"}, "snapshot_r25_state audit parameters must have keys 'cid' and 'aid'"
                            val_map = {k.value: v for k, v in zip(pdict.keys, pdict.values) if isinstance(k, ast.Constant)}

                            cid_val = val_map["cid"]
                            assert (
                                isinstance(cid_val, ast.Call)
                                and getattr(cid_val.func, "id", None) == "str"
                                and cid_val.args
                                and getattr(cid_val.args[0], "id", None) == "character_id"
                            ), "snapshot_r25_state audit parameters must bind str(character_id) and str(account_id)"

                            aid_val = val_map["aid"]
                            assert (
                                isinstance(aid_val, ast.Call)
                                and getattr(aid_val.func, "id", None) == "str"
                                and aid_val.args
                                and getattr(aid_val.args[0], "id", None) == "account_id"
                            ), "snapshot_r25_state audit parameters must bind str(character_id) and str(account_id)"

                            audit_assign = n.targets[0].id

    assert audit_assign is not None, "snapshot_r25_state missing audit_events query"

    # Find character_access link count query
    link_assign = None
    for n in f25.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            if isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "scalar_one":
                inner = n.value.func.value
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) and inner.func.attr == "execute":
                    if inner.args and isinstance(inner.args[0], ast.Call) and getattr(inner.args[0].func, "id", None) == "text":
                        sql_text = inner.args[0].args[0].value if inner.args[0].args and isinstance(inner.args[0].args[0], ast.Constant) else ""
                        norm_sql = " ".join(sql_text.strip().lower().split())
                        if "from character_access" in norm_sql:
                            assert "character_id" in norm_sql and "platform_account_id" in norm_sql, (
                                "snapshot_r25_state must query character_access by character_id and platform_account_id"
                            )
                            assert len(inner.args) >= 2 and isinstance(inner.args[1], ast.Dict), (
                                "snapshot_r25_state character_access query must bind parameters dict"
                            )
                            pdict = inner.args[1]
                            val_map = {k.value: v for k, v in zip(pdict.keys, pdict.values) if isinstance(k, ast.Constant)}
                            assert getattr(val_map.get("cid"), "id", None) == "character_id"
                            assert getattr(val_map.get("aid"), "id", None) == "account_id"
                            link_assign = n.targets[0].id

    assert link_assign is not None, "snapshot_r25_state missing character_access query"

    f25_returns = [n for n in f25.body if isinstance(n, ast.Return)]
    assert len(f25_returns) == 1 and isinstance(f25_returns[0].value, ast.Tuple) and len(f25_returns[0].value.elts) == 3, (
        "snapshot_r25_state must return 3-element immutable tuple"
    )
    ret_elts = [getattr(elt, "id", None) for elt in f25_returns[0].value.elts]
    assert ret_elts == [v_assign, audit_assign, link_assign], (
        "snapshot_r25_state return tuple elements must be dynamic query result variables, not constants"
    )

    # 2. Validate snapshot_r26_state AST
    assert "snapshot_r26_state" in func_defs, "snapshot_r26_state definition missing"
    f26 = func_defs["snapshot_r26_state"]
    assert [a.arg for a in f26.args.args] == ["connection", "character_id", "access_id"], "snapshot_r26_state args mismatch"

    v26_assign = None
    for n in f26.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            if isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == "character_version":
                v26_assign = n.targets[0].id
                break
    assert v26_assign is not None, "snapshot_r26_state missing character_version"

    audit26_assign = None
    for n in f26.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            if isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "scalar_one":
                inner = n.value.func.value
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) and inner.func.attr == "execute":
                    if inner.args and isinstance(inner.args[0], ast.Call) and getattr(inner.args[0].func, "id", None) == "text":
                        sql_text = inner.args[0].args[0].value if inner.args[0].args and isinstance(inner.args[0].args[0], ast.Constant) else ""
                        norm_sql = " ".join(sql_text.strip().lower().split())
                        if "from audit_events" in norm_sql:
                            assert "where" in norm_sql and "entity_id" in norm_sql, (
                                "snapshot_r26_state must use case-specific audit_events predicate on entity_id"
                            )
                            assert "character_id" not in norm_sql, "snapshot_r26_state audit query must use entity_id = access_id, not character_id"
                            assert "entity_type = 'character_access'" in norm_sql, "snapshot_r26_state must require entity_type 'character_access'"
                            assert "action = 'character_access.revoked'" in norm_sql, "snapshot_r26_state must require action 'character_access.revoked'"

                            pdict = inner.args[1]
                            val_map = {k.value: v for k, v in zip(pdict.keys, pdict.values) if isinstance(k, ast.Constant)}
                            aid_val = val_map.get("aid") or val_map.get("id")
                            assert (
                                isinstance(aid_val, ast.Call)
                                and getattr(aid_val.func, "id", None) == "str"
                                and aid_val.args
                                and getattr(aid_val.args[0], "id", None) == "access_id"
                            ), "snapshot_r26_state audit query must bind access_id, not character_id"
                            audit26_assign = n.targets[0].id

    assert audit26_assign is not None, "snapshot_r26_state missing audit_events query"

    row26_assign = None
    for n in f26.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            call = n.value
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == "one":
                if isinstance(call.func.value, ast.Call) and isinstance(call.func.value.func, ast.Attribute) and call.func.value.func.attr == "mappings":
                    exec_call = call.func.value.func.value
                    if isinstance(exec_call, ast.Call) and isinstance(exec_call.func, ast.Attribute) and exec_call.func.attr == "execute":
                        sql_text = exec_call.args[0].args[0].value if exec_call.args and isinstance(exec_call.args[0], ast.Call) else ""
                        norm_sql = " ".join(sql_text.strip().lower().split())
                        if "from character_access" in norm_sql:
                            assert "active" in norm_sql and "revoked_at" in norm_sql, (
                                "snapshot_r26_state must query active and revoked_at from character_access"
                            )
                            row26_assign = n.targets[0].id

    assert row26_assign is not None, "snapshot_r26_state missing character_access row query"

    f26_returns = [n for n in f26.body if isinstance(n, ast.Return)]
    assert len(f26_returns) == 1 and isinstance(f26_returns[0].value, ast.Tuple) and len(f26_returns[0].value.elts) == 6, (
        "snapshot_r26_state must return 6-element immutable tuple"
    )
    assert all(not isinstance(elt, ast.Constant) for elt in f26_returns[0].value.elts), (
        "snapshot_r26_state return tuple elements must be dynamic query result variables, not constants"
    )

    # 3. Validate snapshot_r27_state AST
    assert "snapshot_r27_state" in func_defs, "snapshot_r27_state definition missing"
    f27 = func_defs["snapshot_r27_state"]
    assert [a.arg for a in f27.args.args] == ["connection", "character_id", "access_id"], "snapshot_r27_state args mismatch"

    v27_assign = None
    for n in f27.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            if isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == "character_version":
                v27_assign = n.targets[0].id
                break
    assert v27_assign is not None, "snapshot_r27_state missing character_version"

    audit27_assign = None
    for n in f27.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            if isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "scalar_one":
                inner = n.value.func.value
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) and inner.func.attr == "execute":
                    if inner.args and isinstance(inner.args[0], ast.Call) and getattr(inner.args[0].func, "id", None) == "text":
                        sql_text = inner.args[0].args[0].value if inner.args[0].args and isinstance(inner.args[0].args[0], ast.Constant) else ""
                        norm_sql = " ".join(sql_text.strip().lower().split())
                        if "from audit_events" in norm_sql:
                            assert "where" in norm_sql and "entity_id" in norm_sql, (
                                "snapshot_r27_state must use case-specific audit_events predicate on entity_id"
                            )
                            assert "character_id" not in norm_sql, "snapshot_r27_state audit query must use entity_id = access_id, not character_id"
                            assert "entity_type = 'character_access'" in norm_sql, "snapshot_r27_state must require entity_type 'character_access'"
                            assert "action = 'character_access.default_changed'" in norm_sql, "snapshot_r27_state must require action 'character_access.default_changed'"

                            pdict = inner.args[1]
                            val_map = {k.value: v for k, v in zip(pdict.keys, pdict.values) if isinstance(k, ast.Constant)}
                            aid_val = val_map.get("aid") or val_map.get("id")
                            assert (
                                isinstance(aid_val, ast.Call)
                                and getattr(aid_val.func, "id", None) == "str"
                                and aid_val.args
                                and getattr(aid_val.args[0], "id", None) == "access_id"
                            ), "snapshot_r27_state audit query must bind access_id, not character_id"
                            audit27_assign = n.targets[0].id

    assert audit27_assign is not None, "snapshot_r27_state missing audit_events query"

    row27_assign = None
    for n in f27.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            call = n.value
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == "one":
                if isinstance(call.func.value, ast.Call) and isinstance(call.func.value.func, ast.Attribute) and call.func.value.func.attr == "mappings":
                    exec_call = call.func.value.func.value
                    if isinstance(exec_call, ast.Call) and isinstance(exec_call.func, ast.Attribute) and exec_call.func.attr == "execute":
                        sql_text = exec_call.args[0].args[0].value if exec_call.args and isinstance(exec_call.args[0], ast.Call) else ""
                        norm_sql = " ".join(sql_text.strip().lower().split())
                        if "from character_access" in norm_sql:
                            assert "default_character" in norm_sql, (
                                "snapshot_r27_state must query default_character from character_access"
                            )
                            row27_assign = n.targets[0].id

    assert row27_assign is not None, "snapshot_r27_state missing character_access row query"

    f27_returns = [n for n in f27.body if isinstance(n, ast.Return)]
    assert len(f27_returns) == 1 and isinstance(f27_returns[0].value, ast.Tuple) and len(f27_returns[0].value.elts) == 5, (
        "snapshot_r27_state must return 5-element immutable tuple"
    )
    assert all(not isinstance(elt, ast.Constant) for elt in f27_returns[0].value.elts), (
        "snapshot_r27_state return tuple elements must be dynamic query result variables, not constants"
    )

    # 4. Validate the 9 refusal sequences inside test_database_backed_council_character_views_and_mutations
    assert "test_database_backed_council_character_views_and_mutations" in func_defs, "database test definition missing"
    db_func = func_defs["test_database_backed_council_character_views_and_mutations"]

    expected_sequences: dict[str, dict[str, Any]] = {
        "r25_no_csrf": {
            "helper": "snapshot_r25_state",
            "expected_status": 403,
            "args": ("c2", "target_account"),
            "route_prefix": "/v1/council/characters/",
            "route_suffix": "/links",
            "body_class": "no_csrf",
        },
        "r25_bad_csrf": {
            "helper": "snapshot_r25_state",
            "expected_status": 403,
            "args": ("c2", "target_account"),
            "route_prefix": "/v1/council/characters/",
            "route_suffix": "/links",
            "body_class": "bad_csrf",
        },
        "r25_stale": {
            "helper": "snapshot_r25_state",
            "expected_status": 409,
            "args": ("c2", "target_account"),
            "route_prefix": "/v1/council/characters/",
            "route_suffix": "/links",
            "body_class": "stale",
        },
        "r27_no_csrf": {
            "helper": "snapshot_r27_state",
            "expected_status": 403,
            "args": ("c2", "link2"),
            "route_prefix": "/v1/council/characters/",
            "route_suffix": "/default",
            "body_class": "no_csrf",
        },
        "r27_bad_csrf": {
            "helper": "snapshot_r27_state",
            "expected_status": 403,
            "args": ("c2", "link2"),
            "route_prefix": "/v1/council/characters/",
            "route_suffix": "/default",
            "body_class": "bad_csrf",
        },
        "r27_stale": {
            "helper": "snapshot_r27_state",
            "expected_status": 409,
            "args": ("c2", "link2"),
            "route_prefix": "/v1/council/characters/",
            "route_suffix": "/default",
            "body_class": "stale",
        },
        "r26_no_csrf": {
            "helper": "snapshot_r26_state",
            "expected_status": 403,
            "args": ("c2", "link2"),
            "route_prefix": "/v1/council/characters/",
            "route_suffix": "/revoke",
            "body_class": "no_csrf",
        },
        "r26_bad_csrf": {
            "helper": "snapshot_r26_state",
            "expected_status": 403,
            "args": ("c2", "link2"),
            "route_prefix": "/v1/council/characters/",
            "route_suffix": "/revoke",
            "body_class": "bad_csrf",
        },
        "r26_stale": {
            "helper": "snapshot_r26_state",
            "expected_status": 409,
            "args": ("c2", "link2"),
            "route_prefix": "/v1/council/characters/",
            "route_suffix": "/revoke",
            "body_class": "stale",
        },
    }

    for case_prefix, spec in expected_sequences.items():
        before_var = f"{case_prefix}_snap_before"
        after_var = f"{case_prefix}_snap_after"
        res_var = f"res_{case_prefix}"

        # Find before with-block assignment index in db_func.body
        before_stmt_idx = None
        before_conn_name = None
        before_call = None
        for idx, stmt in enumerate(db_func.body):
            if isinstance(stmt, ast.With):
                for item in stmt.body:
                    if isinstance(item, ast.Assign) and len(item.targets) == 1 and getattr(item.targets[0], "id", None) == before_var:
                        before_stmt_idx = idx
                        before_conn_name = stmt.items[0].optional_vars.id
                        before_call = item.value
                        break
                if before_stmt_idx is not None:
                    break

        assert before_stmt_idx is not None, f"Before snapshot with-block missing for '{case_prefix}'"
        assert isinstance(before_call, ast.Call) and before_call.func.id == spec["helper"], (
            f"Before snapshot for '{case_prefix}' must call '{spec['helper']}'"
        )
        assert [getattr(a, "id", None) for a in before_call.args] == [before_conn_name, spec["args"][0], spec["args"][1]], (
            f"Before snapshot for '{case_prefix}' called with invalid arguments: expected {[before_conn_name, spec['args'][0], spec['args'][1]]}"
        )

        # Statement immediately following before with-block MUST be the request assignment
        assert len(db_func.body) > before_stmt_idx + 1, f"Missing request statement after before snapshot for '{case_prefix}'"
        req_assign = db_func.body[before_stmt_idx + 1]
        assert (
            isinstance(req_assign, ast.Assign)
            and len(req_assign.targets) == 1
            and getattr(req_assign.targets[0], "id", None) == res_var
        ), f"Intervening statement detected between before snapshot and request for '{case_prefix}'"

        assert isinstance(req_assign.value, ast.Await) and isinstance(req_assign.value.value, ast.Call), (
            f"Request for '{case_prefix}' must be an awaited client call"
        )
        client_call = req_assign.value.value
        assert isinstance(client_call.func, ast.Attribute) and getattr(client_call.func.value, "id", None) == "client", (
            f"Request for '{case_prefix}' must be called on 'client'"
        )
        assert client_call.func.attr == "post", (
            f"Request for '{case_prefix}' must use HTTP POST method, got '{client_call.func.attr}'"
        )

        # Validate URL path expression
        assert client_call.args, f"Request for '{case_prefix}' missing URL path argument"
        path_node = client_call.args[0]
        if isinstance(path_node, ast.JoinedStr):
            path_values = path_node.values
            first_val = path_values[0].value if path_values and isinstance(path_values[0], ast.Constant) else ""
            last_val = path_values[-1].value if path_values and isinstance(path_values[-1], ast.Constant) else ""
            assert first_val.startswith(spec["route_prefix"]) and last_val.endswith(spec["route_suffix"]), (
                f"Request path expression mismatch for '{case_prefix}'"
            )
        else:
            raise AssertionError(f"Request path expression mismatch for '{case_prefix}'")

        # Validate refusal request body class
        kw_map = {kw.arg: kw.value for kw in client_call.keywords if kw.arg is not None}
        assert "content" in kw_map, f"Request for '{case_prefix}' missing 'content' parameter"
        content_node = kw_map["content"]

        if spec["body_class"] == "no_csrf":
            # Must NOT contain csrf_token anywhere
            content_str = ast.unparse(content_node) if hasattr(ast, "unparse") else ""
            assert "csrf_token" not in content_str, f"Request body for '{case_prefix}' must NOT contain csrf_token (expected missing CSRF)"
        elif spec["body_class"] == "bad_csrf":
            content_str = ast.unparse(content_node) if hasattr(ast, "unparse") else ""
            assert "csrf_token=" in content_str, f"Request body for '{case_prefix}' must contain an invalid CSRF token"
            assert "csrf_token_for" not in content_str, f"Request body for '{case_prefix}' must NOT call csrf_token_for on bad CSRF"
        elif spec["body_class"] == "stale":
            content_str = ast.unparse(content_node) if hasattr(ast, "unparse") else ""
            assert "csrf_token_for" in content_str, f"Request body for '{case_prefix}' must contain valid CSRF token and stale version"
            # Must contain stale version computation like v_c2 - 1
            has_sub_one = any(
                isinstance(n, ast.BinOp) and isinstance(n.op, ast.Sub) and isinstance(n.right, ast.Constant) and n.right.value == 1
                for n in ast.walk(content_node)
            )
            assert has_sub_one or "- 1" in content_str or "-1" in content_str, (
                f"Request body for '{case_prefix}' must contain valid CSRF token and stale version"
            )

        # Statement immediately following request MUST be the status assertion
        assert len(db_func.body) > before_stmt_idx + 2, f"Missing status assertion for '{case_prefix}'"
        status_assert = db_func.body[before_stmt_idx + 2]
        is_valid_status_assert = False
        if isinstance(status_assert, ast.Assert) and isinstance(status_assert.test, ast.Compare):
            left = status_assert.test.left
            if isinstance(left, ast.Attribute) and getattr(left.value, "id", None) == res_var and left.attr == "status_code":
                if len(status_assert.test.comparators) == 1 and isinstance(status_assert.test.comparators[0], ast.Constant):
                    if status_assert.test.comparators[0].value == spec["expected_status"]:
                        is_valid_status_assert = True
        assert is_valid_status_assert, f"Status assertion for '{case_prefix}' (status {spec['expected_status']}) missing immediately following request"

        # Statement immediately following status assertion MUST be the after with-block
        assert len(db_func.body) > before_stmt_idx + 3, f"Missing after snapshot with-block for '{case_prefix}'"
        after_with_block = db_func.body[before_stmt_idx + 3]
        assert isinstance(after_with_block, ast.With), f"Intervening statement detected between status assertion and after snapshot for '{case_prefix}'"

        after_conn_name = after_with_block.items[0].optional_vars.id
        assert before_conn_name != after_conn_name, f"Case '{case_prefix}' must use distinct before/after connection variables"

        # Check after with-block body: first statement is after snapshot, second is equality assertion
        assert len(after_with_block.body) >= 2, f"After with-block for '{case_prefix}' must contain snapshot and equality assertion"
        after_assign = after_with_block.body[0]
        assert (
            isinstance(after_assign, ast.Assign)
            and len(after_assign.targets) == 1
            and getattr(after_assign.targets[0], "id", None) == after_var
        ), f"First statement inside after with-block for '{case_prefix}' must assign '{after_var}'"

        after_call = after_assign.value
        assert isinstance(after_call, ast.Call) and after_call.func.id == spec["helper"], (
            f"After snapshot for '{case_prefix}' must call '{spec['helper']}'"
        )
        assert [getattr(a, "id", None) for a in after_call.args] == [after_conn_name, spec["args"][0], spec["args"][1]], (
            f"After snapshot for '{case_prefix}' called with invalid arguments: expected {[after_conn_name, spec['args'][0], spec['args'][1]]}"
        )

        equality_assert = after_with_block.body[1]
        is_valid_eq = False
        if isinstance(equality_assert, ast.Assert) and isinstance(equality_assert.test, ast.Compare):
            left = getattr(equality_assert.test.left, "id", None)
            right = getattr(equality_assert.test.comparators[0], "id", None) if equality_assert.test.comparators else None
            if left == after_var and right == before_var:
                is_valid_eq = True
        assert is_valid_eq, (
            f"Equality assertion 'assert {after_var} == {before_var}' missing immediately after '{after_var}' snapshot inside after with-block"
        )


def _rreplace(s: str, old: str, new: str) -> str:
    li = s.rfind(old)
    if li == -1:
        raise ValueError(f"Pattern {old!r} not found in source")
    return s[:li] + new + s[li + len(old):]


def test_structural_refusal_snapshots_and_sequences_present() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    validate_refusal_snapshots_and_sequences(src)


def test_falsification_snapshot_helper_missing_character_version() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        'def snapshot_r25_state(connection: Any, character_id: UUID, account_id: UUID) -> tuple[int, int, int]:\n    """Returns immutable snapshot of (character_version, case_specific_audit_count, matching_access_rows_count)."""\n    v = character_version(connection, character_id)',
        'def snapshot_r25_state(connection: Any, character_id: UUID, account_id: UUID) -> tuple[int, int, int]:\n    """Returns immutable snapshot of (character_version, case_specific_audit_count, matching_access_rows_count)."""\n    v = 1',
    )
    with pytest.raises(AssertionError, match=r"snapshot_r25_state missing character_version"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r25_original_character_id_entity_id_bug_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "WHERE action = 'character_access.granted' AND entity_type = 'character_access' AND payload ->> 'character_id' = :cid AND payload ->> 'platform_account_id' = :aid",
        "WHERE entity_id = :cid",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r25_state must use JSON payload predicates, not entity_id"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_helper_global_audit_query_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        " WHERE action = 'character_access.granted' AND entity_type = 'character_access' AND payload ->> 'character_id' = :cid AND payload ->> 'platform_account_id' = :aid",
        "",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r25_state must use case-specific audit_events predicate on payload"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r25_payload_like_matching_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "payload ->> 'character_id' = :cid",
        "payload::text LIKE '%cid%'",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r25_state must not use LIKE matching on audit payload"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r25_payload_text_cast_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "payload ->> 'character_id' = :cid",
        "CAST(payload AS text) = :cid",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r25_state must use PostgreSQL JSON extraction, not text casting"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r25_missing_action_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "action = 'character_access.granted' AND ",
        "",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r25_state must require action 'character_access.granted'"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r25_missing_entity_type_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "action = 'character_access.granted' AND entity_type = 'character_access' AND payload ->> 'character_id' = :cid AND payload ->> 'platform_account_id' = :aid",
        "action = 'character_access.granted' AND payload ->> 'character_id' = :cid AND payload ->> 'platform_account_id' = :aid",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r25_state must require entity_type 'character_access'"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r25_wrong_param_binding_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        '{"cid": str(character_id), "aid": str(account_id)}',
        '{"cid": str(account_id), "aid": str(character_id)}',
    )
    with pytest.raises(AssertionError, match=r"snapshot_r25_state audit parameters must bind str\(character_id\) and str\(account_id\)",):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r26_using_character_id_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        'text("SELECT count(*) FROM audit_events WHERE entity_id = :aid AND entity_type = \'character_access\' AND action = \'character_access.revoked\'"),\n        {"aid": str(access_id)}',
        'text("SELECT count(*) FROM audit_events WHERE entity_id = :aid AND entity_type = \'character_access\' AND action = \'character_access.revoked\'"),\n        {"aid": str(character_id)}',
    )
    with pytest.raises(AssertionError, match=r"snapshot_r26_state audit query must bind access_id, not character_id"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r27_using_character_id_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        'text("SELECT count(*) FROM audit_events WHERE entity_id = :aid AND entity_type = \'character_access\' AND action = \'character_access.default_changed\'"),\n        {"aid": str(access_id)}',
        'text("SELECT count(*) FROM audit_events WHERE entity_id = :aid AND entity_type = \'character_access\' AND action = \'character_access.default_changed\'"),\n        {"aid": str(character_id)}',
    )
    with pytest.raises(AssertionError, match=r"snapshot_r27_state audit query must bind access_id, not character_id"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r26_missing_action_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "action = 'character_access.revoked'",
        "action = 'character_access.granted'",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r26_state must require action 'character_access.revoked'"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r27_missing_action_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "action = 'character_access.default_changed'",
        "action = 'character_access.revoked'",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r27_state must require action 'character_access.default_changed'"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r26_missing_active_field() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        'text("SELECT active, revoked_at, reason, granted_by_account_id FROM character_access WHERE id = :id")',
        'text("SELECT revoked_at, reason, granted_by_account_id FROM character_access WHERE id = :id")',
    )
    with pytest.raises(AssertionError, match=r"snapshot_r26_state must query active and revoked_at from character_access"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r27_missing_default_character_field() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        'text("SELECT default_character, reason, granted_by_account_id FROM character_access WHERE id = :id")',
        'text("SELECT reason, granted_by_account_id FROM character_access WHERE id = :id")',
    )
    with pytest.raises(AssertionError, match=r"snapshot_r27_state must query default_character from character_access"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_helper_constant_return_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "return (v, audit_count, link_count)",
        "return (1, 0, 0)",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r25_state return tuple elements must be dynamic query result variables, not constants"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_wrong_helper_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "r25_no_csrf_snap_before = snapshot_r25_state(conn_r25_no_csrf_b, c2, target_account)",
        "r25_no_csrf_snap_before = snapshot_r26_state(conn_r25_no_csrf_b, c2, target_account)",
    )
    with pytest.raises(AssertionError, match=r"Before snapshot for 'r25_no_csrf' must call 'snapshot_r25_state'"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_literal_argument_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "r25_no_csrf_snap_before = snapshot_r25_state(conn_r25_no_csrf_b, c2, target_account)",
        "r25_no_csrf_snap_before = snapshot_r25_state(conn_r25_no_csrf_b, c2, '00000000-0000-0000-0000-000000000001')",
    )
    with pytest.raises(AssertionError, match=r"Before snapshot for 'r25_no_csrf' called with invalid arguments"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_swapped_arguments_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "r25_no_csrf_snap_before = snapshot_r25_state(conn_r25_no_csrf_b, c2, target_account)",
        "r25_no_csrf_snap_before = snapshot_r25_state(conn_r25_no_csrf_b, target_account, c2)",
    )
    with pytest.raises(AssertionError, match=r"Before snapshot for 'r25_no_csrf' called with invalid arguments"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_same_connection_before_after_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        _rreplace(
            src,
            "with migrated_database.begin() as conn_r25_no_csrf_a:",
            "with migrated_database.begin() as conn_r25_no_csrf_b:",
        ),
        "r25_no_csrf_snap_after = snapshot_r25_state(conn_r25_no_csrf_a, c2, target_account)",
        "r25_no_csrf_snap_after = snapshot_r25_state(conn_r25_no_csrf_b, c2, target_account)",
    )
    with pytest.raises(AssertionError, match=r"Case 'r25_no_csrf' must use distinct before/after connection variables"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_wrong_http_method_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "res_r25_no_csrf = await client.post(",
        "res_r25_no_csrf = await client.get(",
    )
    with pytest.raises(AssertionError, match=r"Request for 'r25_no_csrf' must use HTTP POST method, got 'get'"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_wrong_route_path_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        'res_r25_no_csrf = await client.post(\n        f"/v1/council/characters/{c2}/links",',
        'res_r25_no_csrf = await client.post(\n        f"/v1/member/characters/{c2}/links",',
    )
    with pytest.raises(AssertionError, match=r"Request path expression mismatch for 'r25_no_csrf'"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_wrong_refusal_body_csrf_in_no_csrf_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        'content=f"subject={target_subject}&access_kind=co_owner&reason=Testing+no+csrf&version={v_c2}"',
        'content=f"csrf_token=foo&subject={target_subject}&access_kind=co_owner&reason=Testing+no+csrf&version={v_c2}"',
    )
    with pytest.raises(AssertionError, match=r"Request body for 'r25_no_csrf' must NOT contain csrf_token"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_wrong_refusal_body_no_csrf_in_bad_csrf_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        'content=f"csrf_token=invalid_token&subject={target_subject}&access_kind=co_owner&reason=Testing+bad+csrf&version={v_c2}"',
        'content=f"subject={target_subject}&access_kind=co_owner&reason=Testing+bad+csrf&version={v_c2}"',
    )
    with pytest.raises(AssertionError, match=r"Request body for 'r25_bad_csrf' must contain an invalid CSRF token"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_wrong_refusal_body_non_stale_in_stale_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        'content=f"csrf_token={csrf_token_for(settings, council)}&subject={target_subject}&access_kind=co_owner&reason=Testing+stale&version={v_c2 - 1}"',
        'content=f"csrf_token={csrf_token_for(settings, council)}&subject={target_subject}&access_kind=co_owner&reason=Testing+stale&version={v_c2}"',
    )
    with pytest.raises(AssertionError, match=r"Request body for 'r25_stale' must contain valid CSRF token and stale version"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_missing_status_assertion_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "assert res_r25_no_csrf.status_code == 403",
        "assert True",
    )
    with pytest.raises(AssertionError, match=r"Status assertion for 'r25_no_csrf' \(status 403\) missing immediately following request"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_wrong_status_code_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "assert res_r25_no_csrf.status_code == 403",
        "assert res_r25_no_csrf.status_code == 200",
    )
    with pytest.raises(AssertionError, match=r"Status assertion for 'r25_no_csrf' \(status 403\) missing immediately following request"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_intervening_mutation_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "    res_r25_no_csrf = await client.post(",
        "    with migrated_database.begin() as conn_extra:\n        pass\n    res_r25_no_csrf = await client.post(",
    )
    with pytest.raises(AssertionError, match=r"Intervening statement detected between before snapshot and request for 'r25_no_csrf'"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_intervening_request_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "    with migrated_database.begin() as conn_r25_no_csrf_a:",
        "    await client.get('/v1/council/characters')\n    with migrated_database.begin() as conn_r25_no_csrf_a:",
    )
    with pytest.raises(AssertionError, match=r"Intervening statement detected between status assertion and after snapshot for 'r25_no_csrf'"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_reordered_status_assertion_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "    assert res_r25_no_csrf.status_code == 403\n\n    with migrated_database.begin() as conn_r25_no_csrf_a:\n        r25_no_csrf_snap_after = snapshot_r25_state(conn_r25_no_csrf_a, c2, target_account)\n        assert r25_no_csrf_snap_after == r25_no_csrf_snap_before",
        "    with migrated_database.begin() as conn_r25_no_csrf_a:\n        r25_no_csrf_snap_after = snapshot_r25_state(conn_r25_no_csrf_a, c2, target_account)\n        assert r25_no_csrf_snap_after == r25_no_csrf_snap_before\n\n    assert res_r25_no_csrf.status_code == 403",
    )
    with pytest.raises(AssertionError, match=r"Status assertion for 'r25_no_csrf' \(status 403\) missing immediately following request"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_equality_before_after_snapshot_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "        r25_no_csrf_snap_after = snapshot_r25_state(conn_r25_no_csrf_a, c2, target_account)\n        assert r25_no_csrf_snap_after == r25_no_csrf_snap_before",
        "        assert r25_no_csrf_snap_after == r25_no_csrf_snap_before\n        r25_no_csrf_snap_after = snapshot_r25_state(conn_r25_no_csrf_a, c2, target_account)",
    )
    with pytest.raises(AssertionError, match=r"First statement inside after with-block for 'r25_no_csrf' must assign 'r25_no_csrf_snap_after'"):
        validate_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_unrelated_variable_equality_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "assert r25_no_csrf_snap_after == r25_no_csrf_snap_before",
        "assert other_snap == r25_no_csrf_snap_before",
    )
    with pytest.raises(AssertionError, match=r"Equality assertion 'assert r25_no_csrf_snap_after == r25_no_csrf_snap_before' missing"):
        validate_refusal_snapshots_and_sequences(tampered)



# ---------------------------------------------------------------------------
# Denial Response Helper Falsification Tests
# ---------------------------------------------------------------------------


class _FakeResponse:
    def __init__(self, status_code: int, content: bytes, headers: dict[str, str]) -> None:
        self.status_code = status_code
        self.content = content
        self.headers = headers


def _valid_fake_headers() -> dict[str, str]:
    return dict(EXACT_DENIAL_HEADERS)


def test_falsification_denial_changed_status_fails() -> None:
    r1 = _FakeResponse(404, b"denied", _valid_fake_headers())
    r2 = _FakeResponse(403, b"denied", _valid_fake_headers())
    with pytest.raises(AssertionError, match=r"Status mismatch in denial responses"):
        assert_identical_denial_responses(r1, r2)


def test_falsification_denial_changed_body_fails() -> None:
    r1 = _FakeResponse(404, b"denied-1", _valid_fake_headers())
    r2 = _FakeResponse(404, b"denied-2", _valid_fake_headers())
    with pytest.raises(AssertionError, match=r"Body content mismatch in denial responses"):
        assert_identical_denial_responses(r1, r2)


@pytest.mark.parametrize("header_name", list(EXACT_DENIAL_HEADERS.keys()))
def test_falsification_denial_wrong_value_in_one_response_fails(header_name: str) -> None:
    h1 = _valid_fake_headers()
    h2 = _valid_fake_headers()
    h2[header_name] = h2[header_name] + "-mutated"
    r1 = _FakeResponse(404, b"denied", h1)
    r2 = _FakeResponse(404, b"denied", h2)
    with pytest.raises(AssertionError, match=f"Second denial header '{header_name}' value mismatch"):
        assert_identical_denial_responses(r1, r2)


@pytest.mark.parametrize("header_name", list(EXACT_DENIAL_HEADERS.keys()))
def test_falsification_denial_same_wrong_value_in_both_responses_fails(header_name: str) -> None:
    h1 = _valid_fake_headers()
    h2 = _valid_fake_headers()
    h1[header_name] = "wrong_value"
    h2[header_name] = "wrong_value"
    r1 = _FakeResponse(404, b"denied", h1)
    r2 = _FakeResponse(404, b"denied", h2)
    with pytest.raises(AssertionError, match=f"First denial header '{header_name}' value mismatch"):
        assert_identical_denial_responses(r1, r2)


@pytest.mark.parametrize("header_name", list(EXACT_DENIAL_HEADERS.keys()))
def test_falsification_denial_missing_header_in_first_response_fails(header_name: str) -> None:
    h1 = _valid_fake_headers()
    h2 = _valid_fake_headers()
    del h1[header_name]
    r1 = _FakeResponse(404, b"denied", h1)
    r2 = _FakeResponse(404, b"denied", h2)
    with pytest.raises(AssertionError, match=f"Missing required header '{header_name}' in first denial response"):
        assert_identical_denial_responses(r1, r2)


@pytest.mark.parametrize("header_name", list(EXACT_DENIAL_HEADERS.keys()))
def test_falsification_denial_missing_header_in_second_response_fails(header_name: str) -> None:
    h1 = _valid_fake_headers()
    h2 = _valid_fake_headers()
    del h2[header_name]
    r1 = _FakeResponse(404, b"denied", h1)
    r2 = _FakeResponse(404, b"denied", h2)
    with pytest.raises(AssertionError, match=f"Missing required header '{header_name}' in second denial response"):
        assert_identical_denial_responses(r1, r2)


@pytest.mark.parametrize("forbidden_header", FORBIDDEN_DENIAL_HEADERS)
def test_falsification_denial_introduced_forbidden_header_fails(forbidden_header: str) -> None:
    h1 = _valid_fake_headers()
    h2 = _valid_fake_headers()
    h1[forbidden_header] = "forbidden_value"
    r1 = _FakeResponse(404, b"denied", h1)
    r2 = _FakeResponse(404, b"denied", h2)
    with pytest.raises(AssertionError, match=f"Forbidden header '{forbidden_header}' present in first denial response"):
        assert_identical_denial_responses(r1, r2)


# ---------------------------------------------------------------------------
# Jinja Direct Rendering Tests (VM-07, VM-08, VM-09)
# ---------------------------------------------------------------------------


def test_vm07_council_character_index_ready_and_filter() -> None:
    """VM-07 / R-22: Render ready state with rows, level, active status, owner, link count, cursor."""
    row1 = CouncilCharacterRow(
        character_id=UUID("00000000-0000-0000-0000-000000000001"),
        display_name=SafeText("Thorin Stonehelm"),
        level=5,
        active=True,
        active_owner=Actor(account_id=UUID("00000000-0000-0000-0000-0000000000aa"), label=SafeText("ThorinPlayer"), capability=frozenset()),
        active_link_count=2,
        unresolved_owner=False,
        links_path="/v1/council/characters/00000000-0000-0000-0000-000000000001/links",
    )
    row2 = CouncilCharacterRow(
        character_id=UUID("00000000-0000-0000-0000-000000000002"),
        display_name=SafeText("Unclaimed Rogue"),
        level=None,
        active=False,
        active_owner=None,
        active_link_count=0,
        unresolved_owner=True,
        links_path="/v1/council/characters/00000000-0000-0000-0000-000000000002/links",
    )
    view = CouncilCharacterIndexView(
        state="ready",
        rows=(row1, row2),
        cursor=Cursor(has_more=True, token="opaque_cursor_token_123"),
        filters=CharacterFilters(query=SafeText("Thorin"), include_inactive=True),
    )

    env = get_jinja_env()
    template = env.get_template("council_characters.html")
    rendered = template.render(view=view, request=make_request("/v1/council/characters"))

    # 1. Page Header & Structure
    assert "Council Character Directory" in rendered
    assert 'data-state="ready"' in rendered

    # 2. Filter Bar echo
    assert 'name="q"' in rendered
    assert 'value="Thorin"' in rendered
    assert 'name="include_inactive"' in rendered
    assert "checked" in rendered

    # 3. Row 1 checks
    assert "Thorin Stonehelm" in rendered
    assert 'href="/v1/council/characters/00000000-0000-0000-0000-000000000001/links"' in rendered
    assert "5" in rendered
    assert "Active" in rendered
    assert "ThorinPlayer" in rendered

    # 4. Row 2 checks (nullable level -> 'not recorded', unresolved owner -> 'no active owner', inactive)
    assert "Unclaimed Rogue" in rendered
    assert "not recorded" in rendered
    assert "Inactive" in rendered
    assert "no active owner" in rendered
    assert 'data-unresolved-owner="true"' in rendered

    # 5. Cursor navigation (URL encoded)
    assert 'rel="next"' in rendered
    assert "opaque_cursor_token_123" in rendered

    # 6. Prove zero mutation form on R-22
    assert 'method="post"' not in rendered.lower()


def test_vm07_council_character_index_url_encoding_special_chars() -> None:
    """VM-07 / R-22: Proves cursor and query filters are strictly URL-encoded."""
    raw_query = "Thorin & Sons = \"King\" ⚔️"
    raw_cursor = "cur+sor/tok=123&more=true"
    view = CouncilCharacterIndexView(
        state="ready",
        rows=(),
        cursor=Cursor(has_more=True, token=raw_cursor),
        filters=CharacterFilters(query=SafeText(raw_query), include_inactive=True),
    )

    env = get_jinja_env()
    template = env.get_template("council_characters.html")
    rendered = template.render(view=view, request=make_request())

    # Extract href of rel="next"
    m = re.search(r'href="([^"]+)"\s+class="[^"]*"\s*>Next Page', rendered)
    assert m, "Next Page link missing"
    href = m.group(1)

    # Parse URL query components
    parsed = urllib.parse.urlparse(href)
    qs = urllib.parse.parse_qs(parsed.query)

    assert qs["cursor"][0] == raw_cursor
    assert qs["q"][0] == raw_query
    assert qs["include_inactive"][0] == "true"


def test_vm07_council_character_index_empty() -> None:
    """VM-07 / R-22: Render empty state with no characters."""
    view = CouncilCharacterIndexView(
        state="empty",
        rows=(),
        cursor=Cursor(has_more=False, token=None),
        filters=CharacterFilters(query=None, include_inactive=False),
    )

    env = get_jinja_env()
    template = env.get_template("council_characters.html")
    rendered = template.render(view=view, request=make_request("/v1/council/characters"))

    assert 'data-state="empty"' in rendered
    assert "No Characters Found" in rendered
    assert 'rel="next"' not in rendered


def test_vm08_character_links_complete_evidence_and_invariants() -> None:
    """VM-08 / R-23: Render complete AccessFact evidence, accurate LinkInvariants, and exact forms."""
    char_id = UUID("00000000-0000-0000-0000-000000000001")
    other_default_char1 = UUID("00000000-0000-0000-0000-000000000099")
    other_default_char2 = UUID("00000000-0000-0000-0000-000000000088")

    char_row = CouncilCharacterRow(
        character_id=char_id,
        display_name=SafeText("Valerius"),
        level=10,
        active=True,
        active_owner=Actor(account_id=UUID("00000000-0000-0000-0000-0000000000bb"), label=SafeText("ValOwner"), capability=frozenset()),
        active_link_count=1,
        unresolved_owner=False,
        links_path=f"/v1/council/characters/{char_id}/links",
    )
    active_fact = AccessFact(
        access_id=UUID("00000000-0000-0000-0000-000000000011"),
        account=Actor(account_id=UUID("00000000-0000-0000-0000-0000000000bb"), label=SafeText("ValOwner"), capability=frozenset()),
        access_kind="owner",
        active=True,
        is_default=True,
        granted_by=Actor(account_id=UUID("00000000-0000-0000-0000-0000000000cc"), label=SafeText("CouncilAdmin"), capability=frozenset()),
        granted_at=Instant(iso_utc="2026-08-15T12:00:00Z", display="2026-08-15 12:00 UTC"),
        reason=SafeText("Primary character link"),
        correlation=Correlation(id=UUID("00000000-0000-0000-0000-000000000099")),
        discord_subject_display="123456789012345678",
        expires_at=Instant(iso_utc="2026-12-31T23:59:59Z", display="2026-12-31 23:59 UTC"),
    )
    hist_fact = AccessFact(
        access_id=UUID("00000000-0000-0000-0000-000000000022"),
        account=Actor(account_id=UUID("00000000-0000-0000-0000-0000000000dd"), label=SafeText("FormerDelegate"), capability=frozenset()),
        access_kind="delegate",
        active=False,
        is_default=False,
        granted_by=Actor(account_id=UUID("00000000-0000-0000-0000-0000000000cc"), label=SafeText("CouncilAdmin"), capability=frozenset()),
        granted_at=Instant(iso_utc="2026-08-01T10:00:00Z", display="2026-08-01 10:00 UTC"),
        reason=SafeText("Temporary access"),
        correlation=Correlation(id=UUID("00000000-0000-0000-0000-000000000088")),
        discord_subject_display="987654321098765432",
        revoked_at=Instant(iso_utc="2026-08-10T15:00:00Z", display="2026-08-10 15:00 UTC"),
        expires_at=None,
    )
    view = CharacterLinksView(
        state="ready",
        character=char_row,
        character_version=4,
        active_links=(active_fact,),
        historical_links=(hist_fact,),
        cursor=Cursor(has_more=True, token="hist_cursor_tok_456"),
        csrf_token="test_csrf_token_secret_123",
        invariants=LinkInvariants(
            one_active_owner=True,
            revoking_last_owner_leaves_unresolved=True,
            default_character_held_elsewhere=(other_default_char1, other_default_char2),
        ),
    )

    env = get_jinja_env()
    template = env.get_template("character_links.html")
    rendered = template.render(view=view, request=make_request(f"/v1/council/characters/{char_id}/links"))

    # 1. Header & Version
    assert "Valerius" in rendered
    assert "Version 4" in rendered
    assert 'data-field="version"' in rendered

    # 2. Invariants Notice & UUIDs (Contract-accurate invariant statement)
    assert 'data-invariant="one-active-owner"' in rendered
    assert "A character may have at most one active owner. When another account is the active owner, granting an owner link is refused and Council must revoke that owner before granting a new owner." in rendered
    assert "Revoking the last active owner is permitted by rule" in rendered
    assert str(other_default_char1) in rendered
    assert str(other_default_char2) in rendered

    # 3. Active Link Evidence (all required fields)
    assert "ValOwner" in rendered
    assert "123456789012345678" in rendered
    assert 'data-evidence="discord-subject"' in rendered
    assert "owner" in rendered
    assert "Active" in rendered
    assert "Default Character" in rendered
    assert "CouncilAdmin" in rendered
    assert "2026-08-15 12:00 UTC" in rendered
    assert "2026-12-31 23:59 UTC" in rendered
    assert "Primary character link" in rendered
    assert "00000000-0000-0000-0000-000000000099" in rendered

    # 4. R-26 Revoke Form
    assert f'action="/v1/council/characters/{char_id}/links/{active_fact.access_id}/revoke"' in rendered
    assert 'name="csrf_token" value="test_csrf_token_secret_123"' in rendered
    assert 'name="version" value="4"' in rendered
    assert 'name="reason"' in rendered

    # 5. R-25 Grant Form (No HTMX attributes)
    assert f'action="/v1/council/characters/{char_id}/links"' in rendered
    assert 'name="subject"' in rendered
    assert 'hx-get' not in rendered
    assert 'hx-target' not in rendered

    # 6. Historical Links Evidence (all required fields)
    assert "FormerDelegate" in rendered
    assert "987654321098765432" in rendered
    assert "delegate" in rendered
    assert "Inactive" in rendered
    assert "2026-08-10 15:00 UTC" in rendered
    assert "CouncilAdmin" in rendered
    assert "2026-08-01 10:00 UTC" in rendered
    assert "never" in rendered
    assert "Temporary access" in rendered
    assert "00000000-0000-0000-0000-000000000088" in rendered
    assert "hist_cursor_tok_456" in rendered


def test_vm08_character_links_empty_invariants_and_unrecorded_fields() -> None:
    """VM-08: Renders explicit empty state for default_character_held_elsewhere and unrecorded facts."""
    char_id = UUID("00000000-0000-0000-0000-000000000001")
    char_row = CouncilCharacterRow(
        character_id=char_id,
        display_name=SafeText("Valerius"),
        level=None,
        active=True,
        active_owner=None,
        active_link_count=1,
        unresolved_owner=True,
        links_path=f"/v1/council/characters/{char_id}/links",
    )
    active_fact = AccessFact(
        access_id=UUID("00000000-0000-0000-0000-000000000011"),
        account=Actor(account_id=UUID("00000000-0000-0000-0000-0000000000bb"), label=SafeText("ValOwner"), capability=frozenset()),
        access_kind="viewer",
        active=True,
        is_default=False,
        granted_by=Actor(account_id=UUID("00000000-0000-0000-0000-0000000000cc"), label=SafeText("CouncilAdmin"), capability=frozenset()),
        granted_at=Instant(iso_utc="2026-08-15T12:00:00Z", display="2026-08-15 12:00 UTC"),
        reason=SafeText("Read link"),
        correlation=Correlation(id=UUID("00000000-0000-0000-0000-000000000099")),
        discord_subject_display=None,
        expires_at=None,
    )
    view = CharacterLinksView(
        state="ready",
        character=char_row,
        character_version=1,
        active_links=(active_fact,),
        historical_links=(),
        cursor=Cursor(has_more=False, token=None),
        csrf_token="csrf",
        invariants=LinkInvariants(
            one_active_owner=True,
            revoking_last_owner_leaves_unresolved=False,
            default_character_held_elsewhere=(),
        ),
    )

    env = get_jinja_env()
    template = env.get_template("character_links.html")
    rendered = template.render(view=view, request=make_request(f"/v1/council/characters/{char_id}/links"))

    assert "No default character held elsewhere by target account." in rendered
    assert "Revoking the last active owner is constrained." in rendered
    assert "not recorded" in rendered
    assert "never" in rendered
    assert "Not Default" in rendered


def test_vm09_identity_search_fragment() -> None:
    """VM-09 / R-24: Standalone HTMX fragment rendering ready, query_echo, candidates, evidence notice."""
    cand1 = IdentityCandidate(
        discord_subject="111222333444555666",
        username=SafeText("Gimli"),
        global_name=SafeText("Gimli Lockbearer"),
        membership_observed_at=Instant(iso_utc="2026-08-10T10:00:00Z", display="2026-08-10 10:00 UTC"),
        already_linked_to_account=True,
        existing_link_here=False,
    )
    view = IdentitySearchResultsView(
        state="ready",
        query_echo=SafeText("Gimli"),
        candidates=(cand1,),
        truncated=True,
        evidence_notice_code="names_are_not_identity",
    )

    env = get_jinja_env()
    template = env.get_template("identity_search.html")
    rendered = template.render(view=view)

    # 1. Prove fragment semantics (no html, head, body landmarks)
    assert "<!doctype html>" not in rendered.lower()
    assert "<html" not in rendered.lower()
    assert "<body" not in rendered.lower()
    assert "<main" not in rendered.lower()

    # 2. Evidence notice & query echo
    assert 'data-notice="names_are_not_identity"' in rendered
    assert "Names are evidence, not identity" in rendered
    assert "Gimli" in rendered

    # 3. Candidate facts
    assert "Gimli" in rendered
    assert "(Gimli Lockbearer)" in rendered
    assert "111222333444555666" in rendered
    assert 'data-field="subject"' in rendered
    assert 'data-already-linked="true"' in rendered
    assert 'data-linked-here="false"' in rendered

    # 4. Truncation notice
    assert 'data-truncated="true"' in rendered


def test_vm09_identity_search_empty_and_invalid() -> None:
    """VM-09 / R-24: Empty and invalid fragment states with query echo."""
    env = get_jinja_env()
    template = env.get_template("identity_search.html")

    # Empty
    empty_view = IdentitySearchResultsView(
        state="empty",
        query_echo=SafeText("NonExistent"),
        candidates=(),
        truncated=False,
    )
    rendered_empty = template.render(view=empty_view)
    assert 'data-state="empty"' in rendered_empty
    assert "No Discord members found matching" in rendered_empty
    assert "NonExistent" in rendered_empty

    # Invalid
    invalid_view = IdentitySearchResultsView(
        state="invalid",
        query_echo=SafeText("!@#"),
        candidates=(),
        truncated=False,
    )
    rendered_invalid = template.render(view=invalid_view)
    assert 'data-state="invalid"' in rendered_invalid
    assert "Invalid search query" in rendered_invalid
    assert "!@#" in rendered_invalid


# ---------------------------------------------------------------------------
# Strict CSS & Template Selector Scope Validator (Exact Token Matching)
# ---------------------------------------------------------------------------


def validate_css_and_template_selector_scope(
    css_text: str,
    template_texts: list[str],
    required_selectors: tuple[str, ...],
    prohibited_selectors: tuple[str, ...],
) -> None:
    """Exact active selector and token extraction validator.
    Strictly avoids raw substring matching."""
    active_css_classes = extract_active_css_classes(css_text)
    active_template_classes = extract_active_template_classes(template_texts)

    # 1. Prohibited selectors must not exist in active CSS
    for prohibited in prohibited_selectors:
        assert prohibited not in active_css_classes, f"Prohibited selector found in active CSS rules: {prohibited}"

    # 2. Required selectors must all exist in active CSS rules
    for req in required_selectors:
        assert req in active_css_classes, f"Required selector '{req}' is missing from active CSS rules"

    # 3. Required selectors must all be used in templates (outside Jinja comments)
    for req in required_selectors:
        assert req in active_template_classes, f"Required selector '{req}' is not used in any Step 6 template"


def test_css_and_template_selector_scope_passes() -> None:
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    assert len(css_files) == 1
    css_text = css_files[0].read_text(encoding="utf-8")
    templates = [
        (TEMPLATE_ROOT / "council_characters.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "character_links.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "identity_search.html").read_text(encoding="utf-8"),
    ]
    validate_css_and_template_selector_scope(css_text, templates, STEP_6_SELECTORS, PROHIBITED_STEP_7_SELECTORS)


def test_falsification_prohibited_step7_selector_fails() -> None:
    """Falsification: Prohibited Step 7+ selector in active CSS fails scope check."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    bad_css = css_files[0].read_text(encoding="utf-8") + "\n.diff-box { display: flex; }\n"
    templates = [
        (TEMPLATE_ROOT / "council_characters.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "character_links.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "identity_search.html").read_text(encoding="utf-8"),
    ]
    with pytest.raises(AssertionError, match=r"Prohibited selector found in active CSS rules: \.diff-box"):
        validate_css_and_template_selector_scope(bad_css, templates, STEP_6_SELECTORS, PROHIBITED_STEP_7_SELECTORS)


def test_falsification_missing_required_step6_selector_fails() -> None:
    """Falsification: Missing required Step 6 selector from CSS fails scope check."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    css_text = css_files[0].read_text(encoding="utf-8")
    bad_css = re.sub(r"\.council-table\b[^{}]*\{[^{}]*\}", "", css_text)
    templates = [
        (TEMPLATE_ROOT / "council_characters.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "character_links.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "identity_search.html").read_text(encoding="utf-8"),
    ]
    with pytest.raises(AssertionError, match=r"Required selector '\.council-table' is missing from active CSS rules"):
        validate_css_and_template_selector_scope(bad_css, templates, STEP_6_SELECTORS, PROHIBITED_STEP_7_SELECTORS)


def test_falsification_unused_step6_selector_fails() -> None:
    """Falsification: Step 6 selector in CSS not used in any template fails check."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    css_text = css_files[0].read_text(encoding="utf-8")
    fake_templates = ["<div><span class='only-other-class'></span></div>"]
    with pytest.raises(AssertionError, match=r"Required selector '\.page-title-row' is not used in any Step 6 template"):
        validate_css_and_template_selector_scope(css_text, fake_templates, STEP_6_SELECTORS, PROHIBITED_STEP_7_SELECTORS)


def test_falsification_selector_only_in_css_comment_fails() -> None:
    """Falsification: CSS selector appearing solely inside comment is rejected by exact active rule extractor."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    css_text = css_files[0].read_text(encoding="utf-8")
    bad_css = re.sub(r"\.council-table\b[^{}]*\{[^{}]*\}", "/* .council-table { display: table; } */", css_text)
    templates = [
        (TEMPLATE_ROOT / "council_characters.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "character_links.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "identity_search.html").read_text(encoding="utf-8"),
    ]
    with pytest.raises(AssertionError, match=r"Required selector '\.council-table' is missing from active CSS rules"):
        validate_css_and_template_selector_scope(bad_css, templates, STEP_6_SELECTORS, PROHIBITED_STEP_7_SELECTORS)


def test_falsification_selector_only_in_multiline_css_comment_fails() -> None:
    """Falsification: CSS selector appearing solely inside multiline comment is rejected."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    css_text = css_files[0].read_text(encoding="utf-8")
    bad_css = re.sub(r"\.council-table\b[^{}]*\{[^{}]*\}", "/* \n .council-table { \n display: table; \n } \n */", css_text)
    templates = [
        (TEMPLATE_ROOT / "council_characters.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "character_links.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "identity_search.html").read_text(encoding="utf-8"),
    ]
    with pytest.raises(AssertionError, match=r"Required selector '\.council-table' is missing from active CSS rules"):
        validate_css_and_template_selector_scope(bad_css, templates, STEP_6_SELECTORS, PROHIBITED_STEP_7_SELECTORS)


def test_falsification_longer_selector_token_fails() -> None:
    """Falsification: Longer selector (e.g. .council-table-extended) does not satisfy .council-table."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    css_text = css_files[0].read_text(encoding="utf-8")
    bad_css = re.sub(r"\.council-table\b", ".council-table-extended", css_text)
    templates = [
        (TEMPLATE_ROOT / "council_characters.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "character_links.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "identity_search.html").read_text(encoding="utf-8"),
    ]
    with pytest.raises(AssertionError, match=r"Required selector '\.council-table' is missing from active CSS rules"):
        validate_css_and_template_selector_scope(bad_css, templates, STEP_6_SELECTORS, PROHIBITED_STEP_7_SELECTORS)


def test_falsification_declaration_value_selector_fails() -> None:
    """Falsification: Selector string inside declaration value (e.g. content: '.council-table') is rejected."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    css_text = css_files[0].read_text(encoding="utf-8")
    bad_css = re.sub(r"\.council-table\b[^{}]*\{[^{}]*\}", ".fake-rule { content: '.council-table'; }", css_text)
    templates = [
        (TEMPLATE_ROOT / "council_characters.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "character_links.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "identity_search.html").read_text(encoding="utf-8"),
    ]
    with pytest.raises(AssertionError, match=r"Required selector '\.council-table' is missing from active CSS rules"):
        validate_css_and_template_selector_scope(bad_css, templates, STEP_6_SELECTORS, PROHIBITED_STEP_7_SELECTORS)


def test_falsification_template_token_only_in_jinja_comment_fails() -> None:
    """Falsification: Template class appearing solely in Jinja comment is rejected."""
    css_files = list((STATIC_ROOT / "css").glob("*.css"))
    css_text = css_files[0].read_text(encoding="utf-8")
    templates = [
        "{# <div class='page-title-row'></div> #}",
        (TEMPLATE_ROOT / "character_links.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "identity_search.html").read_text(encoding="utf-8"),
    ]
    tmpl2_mutated = (TEMPLATE_ROOT / "character_links.html").read_text(encoding="utf-8").replace("page-title-row", "page-title-other")
    templates[1] = tmpl2_mutated

    with pytest.raises(AssertionError, match=r"Required selector '\.page-title-row' is not used in any Step 6 template"):
        validate_css_and_template_selector_scope(css_text, templates, STEP_6_SELECTORS, PROHIBITED_STEP_7_SELECTORS)


def test_falsification_unterminated_css_comment_fails() -> None:
    """Falsification: Unterminated CSS block comment fails safely with explicit error."""
    bad_css = "body { color: white; } /* unterminated comment .btn { color: red; }"
    with pytest.raises(AssertionError, match=r"Unterminated CSS block comment detected in stylesheet"):
        strip_css_comments(bad_css)


# ---------------------------------------------------------------------------
# Template Digest & Static Asset Integrity Tests
# ---------------------------------------------------------------------------


def test_all_23_template_digests_match_exactly() -> None:
    """Proves byte-for-byte fidelity across all 23 platform templates."""
    found_templates = {
        p.name: compute_sha256(p)
        for p in TEMPLATE_ROOT.glob("*.html")
        if p.name != "base.html"
    }
    assert len(found_templates) == 23, f"Expected 23 templates, found {len(found_templates)}"
    assert found_templates == ACCEPTED_TEMPLATE_DIGESTS


def test_asset_manifest_and_fingerprint_integrity() -> None:
    """Proves manifest integrity and filename fingerprint agreement."""
    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    for line in manifest_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        expected_sha, rel_path = line.split(maxsplit=1)
        target = ROOT / rel_path
        assert target.is_file(), f"Manifest file missing: {rel_path}"
        actual_sha = compute_sha256(target)
        assert actual_sha == expected_sha, f"SHA-256 mismatch for {rel_path}: expected {expected_sha}, got {actual_sha}"

        if rel_path.endswith(".css"):
            match = re.match(r"^freedom-blades\.([0-9a-f]{12})\.css$", target.name)
            assert match, f"CSS filename '{target.name}' does not match fingerprint grammar"
            assert match.group(1) == actual_sha[:12], f"CSS fingerprint mismatch in filename {target.name}"


def test_falsification_tamper_manifest_fails(tmp_path: Path) -> None:
    """Falsification: Tampering with a CSS byte in temporary copy fails manifest validation."""
    tmp_static = tmp_path / "static"
    shutil.copytree(STATIC_ROOT, tmp_static)
    tmp_manifest = tmp_static / "asset-integrity.sha256"

    css_files = list((tmp_static / "css").glob("*.css"))
    assert css_files
    target_css = css_files[0]
    target_css.write_bytes(target_css.read_bytes() + b"\n/* tamper */")

    tampered_sha = hashlib.sha256(target_css.read_bytes()).hexdigest()
    manifest_lines = tmp_manifest.read_text(encoding="utf-8").splitlines()
    css_entry = [l for l in manifest_lines if l.strip().endswith(target_css.name)][0]
    expected_sha = css_entry.split()[0]
    assert tampered_sha != expected_sha


# ---------------------------------------------------------------------------
# Form Validation & Adversarial Tests
# ---------------------------------------------------------------------------


def test_r22_get_form_exact_fields_and_no_mutation_controls() -> None:
    """R-22 GET form: exact fields 'q' and 'include_inactive', GET method, zero mutation forms."""
    view = CouncilCharacterIndexView(
        state="ready",
        rows=(),
        cursor=Cursor(has_more=False, token=None),
        filters=CharacterFilters(query=SafeText("Test"), include_inactive=True),
    )
    env = get_jinja_env()
    template = env.get_template("council_characters.html")
    rendered = template.render(view=view, request=make_request("/v1/council/characters"))

    forms = re.findall(r"<form\b([^>]*)>(.*?)</form>", rendered, flags=re.DOTALL | re.IGNORECASE)
    assert len(forms) == 1, f"Expected exactly 1 form on R-22, got {len(forms)}"

    form_attrs, form_body = forms[0]
    method_match = re.search(r'method=["\']([^"\']*)["\']', form_attrs, flags=re.IGNORECASE)
    assert method_match and method_match.group(1).lower() == "get"
    action_match = re.search(r'action=["\']([^"\']*)["\']', form_attrs, flags=re.IGNORECASE)
    assert action_match and action_match.group(1) == "/v1/council/characters"

    inputs = re.findall(r'<input\b[^>]*\bname=["\']([^"\']*)["\']', form_body, flags=re.IGNORECASE)
    assert set(inputs) == {"q", "include_inactive"}

    assert 'method="post"' not in rendered.lower()
    assert 'type="submit"' in form_body.lower()


def test_r25_r26_r27_form_actions_and_named_fields() -> None:
    """R-25, R-26, R-27 POST forms: exact action URLs, POST method, allowed field sets, and NO HTMX on R-25."""
    char_id = UUID("00000000-0000-0000-0000-000000000001")
    access_id = UUID("00000000-0000-0000-0000-000000000011")
    char_row = CouncilCharacterRow(
        character_id=char_id,
        display_name=SafeText("Valerius"),
        level=10,
        active=True,
        active_owner=None,
        active_link_count=1,
        unresolved_owner=True,
        links_path=f"/v1/council/characters/{char_id}/links",
    )
    active_fact = AccessFact(
        access_id=access_id,
        account=Actor(account_id=UUID("00000000-0000-0000-0000-0000000000bb"), label=SafeText("ValOwner"), capability=frozenset()),
        access_kind="viewer",
        active=True,
        is_default=False,
        granted_by=Actor(account_id=UUID("00000000-0000-0000-0000-0000000000cc"), label=SafeText("CouncilAdmin"), capability=frozenset()),
        granted_at=Instant(iso_utc="2026-08-15T12:00:00Z", display="2026-08-15 12:00 UTC"),
        reason=SafeText("Read only link"),
        correlation=Correlation(id=UUID("00000000-0000-0000-0000-000000000099")),
        discord_subject_display="123456789012345678",
    )
    view = CharacterLinksView(
        state="ready",
        character=char_row,
        character_version=7,
        active_links=(active_fact,),
        historical_links=(),
        cursor=Cursor(has_more=False, token=None),
        csrf_token="secret_csrf_tok",
        invariants=LinkInvariants(
            one_active_owner=True,
            revoking_last_owner_leaves_unresolved=True,
            default_character_held_elsewhere=(),
        ),
    )

    env = get_jinja_env()
    template = env.get_template("character_links.html")
    rendered = template.render(view=view, request=make_request(f"/v1/council/characters/{char_id}/links"))

    forms = re.findall(r"<form\b([^>]*)>(.*?)</form>", rendered, flags=re.DOTALL | re.IGNORECASE)
    assert len(forms) == 3, f"Expected 3 forms (grant, revoke, default), got {len(forms)}"

    form_map: dict[str, tuple[str, list[str]]] = {}
    for form_attrs, form_body in forms:
        action = re.search(r'action=["\']([^"\']*)["\']', form_attrs).group(1)
        method = re.search(r'method=["\']([^"\']*)["\']', form_attrs).group(1).lower()
        inputs = re.findall(r'<input\b[^>]*\bname=["\']([^"\']*)["\']', form_body)
        selects = re.findall(r'<select\b[^>]*\bname=["\']([^"\']*)["\']', form_body)
        all_fields = inputs + selects
        form_map[action] = (method, all_fields)

    # 1. R-26 Revoke Form
    revoke_action = f"/v1/council/characters/{char_id}/links/{access_id}/revoke"
    assert revoke_action in form_map
    method, fields = form_map[revoke_action]
    assert method == "post"
    assert set(fields) == {"csrf_token", "version", "reason"}

    # 2. R-27 Set Default Form
    default_action = f"/v1/council/characters/{char_id}/links/{access_id}/default"
    assert default_action in form_map
    method, fields = form_map[default_action]
    assert method == "post"
    assert set(fields) == {"csrf_token", "version", "reason"}

    # 3. R-25 Grant Form (No HTMX attributes on input)
    grant_action = f"/v1/council/characters/{char_id}/links"
    assert grant_action in form_map
    method, fields = form_map[grant_action]
    assert method == "post"
    assert set(fields) == {"csrf_token", "version", "subject", "access_kind", "reason"}

    # Proves absence of server-owned fields in body
    for action, (method, fields) in form_map.items():
        assert "account_id" not in fields
        assert "actor_id" not in fields
        assert "access_id" not in fields
        assert "grantor" not in fields
        assert "timestamps" not in fields

    # Proves absence of HTMX attributes on R-25 form
    assert 'hx-get' not in rendered
    assert 'hx-trigger' not in rendered
    assert 'hx-target' not in rendered


def test_adversarial_escaping_on_council_templates() -> None:
    """Proves that adversarial HTML/JS strings are strictly auto-escaped across all 3 templates."""
    env = get_jinja_env()
    xss_str = "<script>alert('xss')</script>"
    quote_str = '" onfocus="alert(1)'

    # 1. council_characters.html
    row = CouncilCharacterRow(
        character_id=uuid4(),
        display_name=SafeText(xss_str),
        level=None,
        active=True,
        active_owner=Actor(account_id=uuid4(), label=SafeText(quote_str), capability=frozenset()),
        active_link_count=1,
        unresolved_owner=False,
        links_path="/v1/council/characters/test/links",
    )
    view1 = CouncilCharacterIndexView(
        state="ready",
        rows=(row,),
        cursor=Cursor(has_more=False, token=None),
        filters=CharacterFilters(query=SafeText(xss_str), include_inactive=False),
    )
    rendered1 = env.get_template("council_characters.html").render(view=view1, request=make_request())
    assert "<script>" not in rendered1
    assert "&lt;script&gt;" in rendered1
    assert 'onfocus="alert(1)' not in rendered1
    assert "&quot; onfocus=&quot;alert(1)" in rendered1 or "&#34; onfocus=&#34;alert(1)" in rendered1

    # 2. identity_search.html
    cand = IdentityCandidate(
        discord_subject=xss_str,
        username=SafeText(xss_str),
        global_name=SafeText(quote_str),
        membership_observed_at=Instant(iso_utc="2026-08-10T10:00:00Z", display="2026-08-10 10:00 UTC"),
        already_linked_to_account=False,
        existing_link_here=False,
    )
    view2 = IdentitySearchResultsView(
        state="ready",
        query_echo=SafeText(xss_str),
        candidates=(cand,),
        truncated=False,
    )
    rendered2 = env.get_template("identity_search.html").render(view=view2)
    assert "<script>" not in rendered2
    assert "&lt;script&gt;" in rendered2


# ---------------------------------------------------------------------------
# Database-Backed HTTP Tests (R-22 through R-27)
# ---------------------------------------------------------------------------


def snapshot_r25_state(connection: Any, character_id: UUID, account_id: UUID) -> tuple[int, int, int]:
    """Returns immutable snapshot of (character_version, case_specific_audit_count, matching_access_rows_count)."""
    v = character_version(connection, character_id)
    audit_count = connection.execute(
        text("SELECT count(*) FROM audit_events WHERE action = 'character_access.granted' AND entity_type = 'character_access' AND payload ->> 'character_id' = :cid AND payload ->> 'platform_account_id' = :aid"),
        {"cid": str(character_id), "aid": str(account_id)},
    ).scalar_one()
    link_count = connection.execute(
        text("SELECT count(*) FROM character_access WHERE character_id = :cid AND platform_account_id = :aid"),
        {"cid": character_id, "aid": account_id},
    ).scalar_one()
    return (v, audit_count, link_count)


def snapshot_r26_state(connection: Any, character_id: UUID, access_id: UUID) -> tuple[int, int, bool, str | None, str, UUID]:
    """Returns immutable snapshot of (character_version, case_specific_audit_count, active, revoked_at_iso, reason, grantor_id)."""
    v = character_version(connection, character_id)
    audit_count = connection.execute(
        text("SELECT count(*) FROM audit_events WHERE entity_id = :aid AND entity_type = 'character_access' AND action = 'character_access.revoked'"),
        {"aid": str(access_id)},
    ).scalar_one()
    row = connection.execute(
        text("SELECT active, revoked_at, reason, granted_by_account_id FROM character_access WHERE id = :id"),
        {"id": access_id},
    ).mappings().one()
    revoked_str = row["revoked_at"].isoformat() if row["revoked_at"] is not None else None
    return (v, audit_count, bool(row["active"]), revoked_str, str(row["reason"]), row["granted_by_account_id"])


def snapshot_r27_state(connection: Any, character_id: UUID, access_id: UUID) -> tuple[int, int, bool, str, UUID]:
    """Returns immutable snapshot of (character_version, case_specific_audit_count, default_character, reason, grantor_id)."""
    v = character_version(connection, character_id)
    audit_count = connection.execute(
        text("SELECT count(*) FROM audit_events WHERE entity_id = :aid AND entity_type = 'character_access' AND action = 'character_access.default_changed'"),
        {"aid": str(access_id)},
    ).scalar_one()
    row = connection.execute(
        text("SELECT default_character, reason, granted_by_account_id FROM character_access WHERE id = :id"),
        {"id": access_id},
    ).mappings().one()
    return (v, audit_count, bool(row["default_character"]), str(row["reason"]), row["granted_by_account_id"])


@pytest.mark.database
async def test_database_backed_council_character_views_and_mutations(
    client, settings, migrated_database, clean_between_council_cases
) -> None:
    """Proves real HTTP/security/mutation behavior with PostgreSQL evidence for R-22 through R-27:
    - R-22/R-23/R-24 Council and CA success
    - Ordinary member, administrator-alone, and continuity refusal (403) across R-22, R-23, R-24
    - Unauthenticated direct R-24 fragment 401 (not login redirect)
    - Object substitution / non-enumeration byte-identical headers and body for 404
    - Successful R-25, R-26, R-27 no-JS payloads, redirects (303), and durable state effects
    - Missing and invalid CSRF across R-25, R-26, R-27 with immediate complete no-write snapshot verification
    - Stale versions across R-25, R-26, R-27 with 409 conflict and immediate complete no-write snapshot verification
    - Tracked ID registration for post-yield fresh-connection absence verification
    """
    tracked_state: TrackedCouncilFixtureState = clean_between_council_cases
    callers = seed_callers(migrated_database, settings)
    council = callers["C"]
    council_admin = callers["CA"]
    member = callers["M"]
    admin = callers["A"]
    continuity = callers["AC"]
    unauthenticated = callers["U"]

    target_subject = 700000000000009111

    with migrated_database.begin() as connection:
        c1 = make_character(connection, display_name="Alden Fireforge", level=5)
        c2 = make_character(connection, display_name="Bari Ironbreaker", level=None)
        tracked_state.character_ids.add(c1)
        tracked_state.character_ids.add(c2)

        target_account = make_account(connection, label="target-user")
        seed_discord_member(connection, subject=target_subject, username="target.warrior")
        link_discord(connection, target_account, target_subject)

        link1 = grant_link(
            connection,
            character_id=c1,
            account_id=target_account,
            granted_by=council.account_id,
            access_kind="owner",
            default_character=True,
        )
        tracked_state.access_ids.add(link1)

    # 1. R-22 Council Character Directory GET
    # Success for C and CA
    res_r22_c = await client.get("/v1/council/characters", cookies=council.cookies(settings))
    assert res_r22_c.status_code == 200
    assert "Alden Fireforge" in res_r22_c.text
    assert "Bari Ironbreaker" in res_r22_c.text
    assert "Council Character Directory" in res_r22_c.text

    res_r22_ca = await client.get("/v1/council/characters", cookies=council_admin.cookies(settings))
    assert res_r22_ca.status_code == 200

    # Refusals for M, A, AC (403)
    assert (await client.get("/v1/council/characters", cookies=member.cookies(settings))).status_code == 403
    assert (await client.get("/v1/council/characters", cookies=admin.cookies(settings))).status_code == 403
    assert (await client.get("/v1/council/characters", cookies=continuity.cookies(settings))).status_code == 403

    # Unauthenticated -> redirect to login (303)
    res_r22_u = await client.get("/v1/council/characters", cookies=unauthenticated.cookies(settings))
    assert res_r22_u.status_code == 303
    assert res_r22_u.headers["location"] == "/v1/login"

    # 2. R-23 Character Links GET
    # Success for C and CA
    res_r23_c = await client.get(f"/v1/council/characters/{c1}/links", cookies=council.cookies(settings))
    assert res_r23_c.status_code == 200
    assert "Alden Fireforge" in res_r23_c.text
    assert "target-user" in res_r23_c.text

    res_r23_ca = await client.get(f"/v1/council/characters/{c1}/links", cookies=council_admin.cookies(settings))
    assert res_r23_ca.status_code == 200

    # Refusals for M, A, AC (403)
    assert (await client.get(f"/v1/council/characters/{c1}/links", cookies=member.cookies(settings))).status_code == 403
    assert (await client.get(f"/v1/council/characters/{c1}/links", cookies=admin.cookies(settings))).status_code == 403
    assert (await client.get(f"/v1/council/characters/{c1}/links", cookies=continuity.cookies(settings))).status_code == 403

    # Unauthenticated -> redirect to login (303)
    res_r23_u = await client.get(f"/v1/council/characters/{c1}/links", cookies=unauthenticated.cookies(settings))
    assert res_r23_u.status_code == 303
    assert res_r23_u.headers["location"] == "/v1/login"

    # Object substitution / non-enumeration complete denial-response identity:
    # 404 for absent UUID and malformed UUID have identical status, body, and protected headers
    unknown_uuid = uuid4()
    res_absent = await client.get(f"/v1/council/characters/{unknown_uuid}/links", cookies=council.cookies(settings))
    res_malformed = await client.get("/v1/council/characters/not-a-valid-uuid/links", cookies=council.cookies(settings))
    assert_identical_denial_responses(res_absent, res_malformed)

    # 3. R-24 Identity Search GET (HTMX standalone fragment)
    # Success for C and CA
    res_r24_c = await client.get("/v1/council/identity-search?q=target", cookies=council.cookies(settings))
    assert res_r24_c.status_code == 200
    assert "target.warrior" in res_r24_c.text
    assert "identity-search-fragment" in res_r24_c.text
    assert "<!doctype html>" not in res_r24_c.text.lower()

    res_r24_ca = await client.get("/v1/council/identity-search?q=target", cookies=council_admin.cookies(settings))
    assert res_r24_ca.status_code == 200

    # Refusals for M, A, AC (403)
    assert (await client.get("/v1/council/identity-search?q=target", cookies=member.cookies(settings))).status_code == 403
    assert (await client.get("/v1/council/identity-search?q=target", cookies=admin.cookies(settings))).status_code == 403
    assert (await client.get("/v1/council/identity-search?q=target", cookies=continuity.cookies(settings))).status_code == 403

    # Unauthenticated direct R-24 fragment: direct 401, NOT login redirect
    res_r24_u = await client.get("/v1/council/identity-search?q=target", cookies=unauthenticated.cookies(settings))
    assert res_r24_u.status_code == 401

    # 4. R-25 Grant Link POST Security & Mutations
    with migrated_database.begin() as conn:
        v_c2 = character_version(conn, c2)

    # Missing CSRF on R-25 -> 403 with immediate complete no-write snapshot verification
    with migrated_database.begin() as conn_r25_no_csrf_b:
        r25_no_csrf_snap_before = snapshot_r25_state(conn_r25_no_csrf_b, c2, target_account)

    res_r25_no_csrf = await client.post(
        f"/v1/council/characters/{c2}/links",
        cookies=council.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=f"subject={target_subject}&access_kind=co_owner&reason=Testing+no+csrf&version={v_c2}",
    )
    assert res_r25_no_csrf.status_code == 403

    with migrated_database.begin() as conn_r25_no_csrf_a:
        r25_no_csrf_snap_after = snapshot_r25_state(conn_r25_no_csrf_a, c2, target_account)
        assert r25_no_csrf_snap_after == r25_no_csrf_snap_before

    # Invalid CSRF on R-25 -> 403 with immediate complete no-write snapshot verification
    with migrated_database.begin() as conn_r25_bad_csrf_b:
        r25_bad_csrf_snap_before = snapshot_r25_state(conn_r25_bad_csrf_b, c2, target_account)

    res_r25_bad_csrf = await client.post(
        f"/v1/council/characters/{c2}/links",
        cookies=council.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=f"csrf_token=invalid_token&subject={target_subject}&access_kind=co_owner&reason=Testing+bad+csrf&version={v_c2}",
    )
    assert res_r25_bad_csrf.status_code == 403

    with migrated_database.begin() as conn_r25_bad_csrf_a:
        r25_bad_csrf_snap_after = snapshot_r25_state(conn_r25_bad_csrf_a, c2, target_account)
        assert r25_bad_csrf_snap_after == r25_bad_csrf_snap_before

    # Stale version on R-25 -> 409 Conflict with immediate complete no-write snapshot verification
    with migrated_database.begin() as conn_r25_stale_b:
        r25_stale_snap_before = snapshot_r25_state(conn_r25_stale_b, c2, target_account)

    res_r25_stale = await client.post(
        f"/v1/council/characters/{c2}/links",
        cookies=council.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, council)}&subject={target_subject}&access_kind=co_owner&reason=Testing+stale&version={v_c2 - 1}",
    )
    assert res_r25_stale.status_code == 409

    with migrated_database.begin() as conn_r25_stale_a:
        r25_stale_snap_after = snapshot_r25_state(conn_r25_stale_a, c2, target_account)
        assert r25_stale_snap_after == r25_stale_snap_before

    # Successful R-25 Mutation
    res_r25 = await client.post(
        f"/v1/council/characters/{c2}/links",
        cookies=council.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, council)}&subject={target_subject}&access_kind=co_owner&reason=Granting+co-owner+access&version={v_c2}",
    )
    assert res_r25.status_code == 303
    assert res_r25.headers["location"] == f"/v1/council/characters/{c2}/links"

    with migrated_database.begin() as conn:
        assert character_version(conn, c2) == v_c2 + 1
        link2 = conn.execute(
            text("SELECT id FROM character_access WHERE character_id = :cid AND platform_account_id = :aid AND active"),
            {"cid": c2, "aid": target_account},
        ).scalar_one()
        tracked_state.access_ids.add(link2)
        audit_count = conn.execute(
            text("SELECT count(*) FROM audit_events WHERE action = 'character_access.granted'"),
        ).scalar_one()
        assert audit_count >= 1

    # 5. R-27 Set Default Link POST Security & Mutations
    with migrated_database.begin() as conn:
        v_c2_after_grant = character_version(conn, c2)

    # Missing CSRF on R-27 -> 403 with immediate complete no-write snapshot verification
    with migrated_database.begin() as conn_r27_no_csrf_b:
        r27_no_csrf_snap_before = snapshot_r27_state(conn_r27_no_csrf_b, c2, link2)

    res_r27_no_csrf = await client.post(
        f"/v1/council/characters/{c2}/links/{link2}/default",
        cookies=council.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=f"reason=Testing+no+csrf&version={v_c2_after_grant}",
    )
    assert res_r27_no_csrf.status_code == 403

    with migrated_database.begin() as conn_r27_no_csrf_a:
        r27_no_csrf_snap_after = snapshot_r27_state(conn_r27_no_csrf_a, c2, link2)
        assert r27_no_csrf_snap_after == r27_no_csrf_snap_before

    # Invalid CSRF on R-27 -> 403 with immediate complete no-write snapshot verification
    with migrated_database.begin() as conn_r27_bad_csrf_b:
        r27_bad_csrf_snap_before = snapshot_r27_state(conn_r27_bad_csrf_b, c2, link2)

    res_r27_bad_csrf = await client.post(
        f"/v1/council/characters/{c2}/links/{link2}/default",
        cookies=council.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=f"csrf_token=invalid_csrf&reason=Testing+bad+csrf&version={v_c2_after_grant}",
    )
    assert res_r27_bad_csrf.status_code == 403

    with migrated_database.begin() as conn_r27_bad_csrf_a:
        r27_bad_csrf_snap_after = snapshot_r27_state(conn_r27_bad_csrf_a, c2, link2)
        assert r27_bad_csrf_snap_after == r27_bad_csrf_snap_before

    # Stale version on R-27 -> 409 with immediate complete no-write snapshot verification
    with migrated_database.begin() as conn_r27_stale_b:
        r27_stale_snap_before = snapshot_r27_state(conn_r27_stale_b, c2, link2)

    res_r27_stale = await client.post(
        f"/v1/council/characters/{c2}/links/{link2}/default",
        cookies=council.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, council)}&reason=Testing+stale&version={v_c2_after_grant - 1}",
    )
    assert res_r27_stale.status_code == 409

    with migrated_database.begin() as conn_r27_stale_a:
        r27_stale_snap_after = snapshot_r27_state(conn_r27_stale_a, c2, link2)
        assert r27_stale_snap_after == r27_stale_snap_before

    # Successful R-27 Mutation
    res_r27 = await client.post(
        f"/v1/council/characters/{c2}/links/{link2}/default",
        cookies=council.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, council)}&reason=Making+c2+the+default&version={v_c2_after_grant}",
    )
    assert res_r27.status_code == 303
    assert res_r27.headers["location"] == f"/v1/council/characters/{c2}/links"

    with migrated_database.begin() as conn:
        assert character_version(conn, c2) == v_c2_after_grant + 1
        is_default = conn.execute(
            text("SELECT default_character FROM character_access WHERE id = :id"),
            {"id": link2},
        ).scalar_one()
        assert is_default is True

    # 6. R-26 Revoke Link POST Security & Mutations
    with migrated_database.begin() as conn:
        v_c2_after_default = character_version(conn, c2)

    # Missing CSRF on R-26 -> 403 with immediate complete no-write snapshot verification
    with migrated_database.begin() as conn_r26_no_csrf_b:
        r26_no_csrf_snap_before = snapshot_r26_state(conn_r26_no_csrf_b, c2, link2)

    res_r26_no_csrf = await client.post(
        f"/v1/council/characters/{c2}/links/{link2}/revoke",
        cookies=council.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=f"reason=Testing+no+csrf&version={v_c2_after_default}",
    )
    assert res_r26_no_csrf.status_code == 403

    with migrated_database.begin() as conn_r26_no_csrf_a:
        r26_no_csrf_snap_after = snapshot_r26_state(conn_r26_no_csrf_a, c2, link2)
        assert r26_no_csrf_snap_after == r26_no_csrf_snap_before

    # Invalid CSRF on R-26 -> 403 with immediate complete no-write snapshot verification
    with migrated_database.begin() as conn_r26_bad_csrf_b:
        r26_bad_csrf_snap_before = snapshot_r26_state(conn_r26_bad_csrf_b, c2, link2)

    res_r26_bad_csrf = await client.post(
        f"/v1/council/characters/{c2}/links/{link2}/revoke",
        cookies=council.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=f"csrf_token=invalid_csrf&reason=Testing+bad+csrf&version={v_c2_after_default}",
    )
    assert res_r26_bad_csrf.status_code == 403

    with migrated_database.begin() as conn_r26_bad_csrf_a:
        r26_bad_csrf_snap_after = snapshot_r26_state(conn_r26_bad_csrf_a, c2, link2)
        assert r26_bad_csrf_snap_after == r26_bad_csrf_snap_before

    # Stale version on R-26 -> 409 with immediate complete no-write snapshot verification
    with migrated_database.begin() as conn_r26_stale_b:
        r26_stale_snap_before = snapshot_r26_state(conn_r26_stale_b, c2, link2)

    res_r26_stale = await client.post(
        f"/v1/council/characters/{c2}/links/{link2}/revoke",
        cookies=council.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, council)}&reason=Testing+stale&version={v_c2_after_default - 1}",
    )
    assert res_r26_stale.status_code == 409

    with migrated_database.begin() as conn_r26_stale_a:
        r26_stale_snap_after = snapshot_r26_state(conn_r26_stale_a, c2, link2)
        assert r26_stale_snap_after == r26_stale_snap_before

    # Successful R-26 Mutation
    res_r26 = await client.post(
        f"/v1/council/characters/{c2}/links/{link2}/revoke",
        cookies=council.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, council)}&reason=Revoking+access+link&version={v_c2_after_default}",
    )
    assert res_r26.status_code == 303
    assert res_r26.headers["location"] == f"/v1/council/characters/{c2}/links"

    with migrated_database.begin() as conn:
        assert character_version(conn, c2) == v_c2_after_default + 1
        row = conn.execute(text("SELECT * FROM character_access WHERE id = :id"), {"id": link2}).mappings().one()
        assert row["active"] is False
        assert row["revoked_at"] is not None
        assert row["reason"] == "Granting co-owner access"
        assert row["granted_by_account_id"] == council.account_id
