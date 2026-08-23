"""Tests for P3.4 Step 8 Snapshots and Preview Entry Views.

Covers:
1. VM-14 / R-40: `council_snapshots.html`
   - Honest ready and empty states.
   - 50-snapshot and 50-folder bounds, opaque cursor token URL encoding.
   - Short/full checksum visibility without artifact/download links or raw bytes.
   - Core version, system ID/version, actor counts, size in bytes without unit drift.
   - Exported and received times, received_via status.
   - Selected/unselected folder presentation and path_observed honesty.
   - Applied status and JobStamp presentation across kinds and states.
2. R-41: Administrator folder selection form
   - Exact POST method and action `/v1/admin/snapshots/{snapshot_id}/folder`.
   - Exact named inputs `{csrf_token, folder_id}` with no client-side authority.
   - Invalidation notice and atomic invalidation of nonterminal jobs and completed previews.
   - Conditional rendering from `view.can_select_folder`.
3. R-42: Council preview creation form
   - Exact POST method and action `/v1/council/snapshots/{snapshot_id}/preview-jobs`.
   - Exact named inputs `{csrf_token, nonce}` with server-rendered nonce.
   - Double-click retry idempotency (single job, single audit event) vs distinct nonce.
   - Conditional rendering from `view.can_preview` and `row.selected_folder`.
4. Security and Matrix Enforcement
   - Direct-call caller matrices for R-40, R-41, R-42 (U, N, M, C, A, CA, BG, AC).
   - CSRF, Origin, Content-Type, body size bounds (4 KiB), 404 non-enumeration.
   - Adversarial XSS autoescaping in every external attribute and text context.
   - Exact denial headers and byte identity on 404 responses.
   - Structural AST validation of post-yield cleanup discipline.
   - All 23 template digests and static asset manifest integrity.
"""
from __future__ import annotations

import ast
import dataclasses
import hashlib
import inspect
import os
import re
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import jinja2
import pytest
from sqlalchemy import text
from starlette.requests import Request

from application.audit import ActorCapability
from application.web.jobs import (
    JobKind,
    JobState,
    mint_preview_nonce,
    parse_preview_nonce,
)
from application.web.view_models import (
    PREVIEW_NONCE_BOUND,
    Correlation,
    Cursor,
    FolderChoice,
    Instant,
    JobStamp,
    SafeText,
    SnapshotListView,
    SnapshotRow,
)
from tests import foundry_fixtures as fx
from tests.web.conftest import add_mapping, link_discord, make_account
from tests.web.p3_3_fixtures import (
    FIXTURE_FOLDER_PATH,
    clean_p3_3_tables,
    complete_preview,
    seed_import,
    seed_job,
    seed_snapshot,
    select_folder,
)
from tests.web.portal_fixtures import clean_p3_2_tables, csrf_token_for, seed_callers
from tests.web_fixtures import PUBLIC_ORIGIN

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = ROOT / "adapters" / "web" / "templates"
STATIC_ROOT = ROOT / "adapters" / "web" / "static"
MANIFEST_PATH = STATIC_ROOT / "asset-integrity.sha256"

FORM = "application/x-www-form-urlencoded"

#: A stand-in for one render's minted VM-14 `preview_nonce` in the direct-Jinja
#: tests. Shaped like the real thing (`PREVIEW_NONCE_BOUND` URL-safe characters)
#: so a template that silently truncated or re-derived it would be visible here.
SAMPLE_PREVIEW_NONCE = "s" * PREVIEW_NONCE_BOUND

from tests.web.template_digests import P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS


# Contract §5.2 Authoritative Caller Matrix for R-40, R-41, R-42
ACCEPTED_ROUTE_CALLER_MATRIX: dict[str, dict[str, int]] = {
    "R-40": {"U": 303, "N": 403, "M": 403, "C": 200, "A": 200, "CA": 200, "BG": 403, "AC": 403},
    "R-41": {"U": 401, "N": 403, "M": 403, "C": 403, "A": 303, "CA": 303, "BG": 403, "AC": 403},
    "R-42": {"U": 401, "N": 403, "M": 403, "C": 303, "A": 403, "CA": 303, "BG": 403, "AC": 403},
}

STEP_8_SELECTORS: tuple[str, ...] = (
    ".page-header",
    ".page-title-row",
    ".page-title",
    ".page-description",
    ".badge",
    ".badge-warning",
    ".badge-info",
    ".badge-secondary",
    ".badge-sm",
    ".empty-card",
    ".empty-icon",
    ".empty-text",
    ".table-container",
    ".council-table",
    ".font-mono",
    ".text-xs",
    ".text-sm",
    ".text-muted",
    ".btn",
    ".btn-primary",
    ".btn-secondary",
    ".btn-sm",
    ".action-form",
    ".form-group-inline",
    ".form-label-inline",
    ".form-select",
    ".form-select-sm",
    ".cursor-nav",
)

PROHIBITED_STEP_8_SELECTORS: tuple[str, ...] = (
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
    "content-type": "application/json",
    "x-content-type-options": "nosniff",
    "referrer-policy": "same-origin",
    "cross-origin-opener-policy": "same-origin",
    "cross-origin-resource-policy": "same-origin",
    "cache-control": "no-store",
    "permissions-policy": "geolocation=(), camera=(), microphone=(), payment=()",
}

FORBIDDEN_DENIAL_HEADERS: tuple[str, ...] = (
    "location",
    "set-cookie",
    "x-frame-options",
)


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def get_jinja_env() -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_ROOT)),
        autoescape=True,
        undefined=jinja2.StrictUndefined,
    )


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


def make_request(path: str = "/v1/council/snapshots") -> Request:
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

    for forbidden in FORBIDDEN_DENIAL_HEADERS:
        assert forbidden not in res1.headers, f"Forbidden header '{forbidden}' present in first denial response"
        assert forbidden not in res2.headers, f"Forbidden header '{forbidden}' present in second denial response"

    for req_header, expected_val in EXACT_DENIAL_HEADERS.items():
        assert req_header in res1.headers, f"Missing required header '{req_header}' in first denial response"
        assert req_header in res2.headers, f"Missing required header '{req_header}' in second denial response"
        v1 = res1.headers[req_header]
        v2 = res2.headers[req_header]
        assert v1 == expected_val, f"First denial header '{req_header}' value mismatch: expected '{expected_val}', got '{v1}'"
        assert v2 == expected_val, f"Second denial header '{req_header}' value mismatch: expected '{expected_val}', got '{v2}'"
        assert v1 == v2, f"Header value mismatch between denials for '{req_header}': '{v1}' != '{v2}'"


# ===========================================================================
# Route Authorization Matrix Validator (§5.2) & Negative Probes
# ===========================================================================

def validate_route_caller_matrix(matrix: dict[str, dict[str, int]]) -> None:
    expected_routes = {"R-40", "R-41", "R-42"}
    assert set(matrix.keys()) == expected_routes, f"Matrix route set mismatch: expected {expected_routes}, got {set(matrix.keys())}"

    expected_callers = {"U", "N", "M", "C", "A", "CA", "BG", "AC"}
    mutation_routes = {"R-41", "R-42"}
    nav_routes = {"R-40"}

    for r_code, row in matrix.items():
        assert set(row.keys()) == expected_callers, f"Route {r_code} missing callers: {expected_callers - set(row.keys())}"

        if r_code in mutation_routes:
            assert row["U"] == 401, f"Mutation route {r_code} must return 401 for U, got {row['U']}"
        elif r_code in nav_routes:
            assert row["U"] == 303, f"Navigation route {r_code} must return 303 for U, got {row['U']}"

        assert row["N"] == 403, f"Route {r_code} must refuse N with 403, got {row['N']}"
        assert row["M"] == 403, f"Route {r_code} must refuse M with 403, got {row['M']}"

        # Route specific capability requirements
        if r_code == "R-40":
            assert row["C"] == 200 and row["A"] == 200 and row["CA"] == 200, "R-40 permits C, A, and CA"
            assert row["BG"] == 403 and row["AC"] == 403, "R-40 refuses emergency continuity"
        elif r_code == "R-41":
            assert row["C"] == 403, "R-41 refuses Council"
            assert row["A"] == 303 and row["CA"] == 303, "R-41 permits Administrator"
            assert row["BG"] == 403 and row["AC"] == 403, "R-41 refuses emergency continuity"
        elif r_code == "R-42":
            assert row["A"] == 403, "R-42 refuses Administrator"
            assert row["C"] == 303 and row["CA"] == 303, "R-42 permits Council"
            assert row["BG"] == 403 and row["AC"] == 403, "R-42 refuses emergency continuity"


def test_structural_route_caller_matrix_valid() -> None:
    validate_route_caller_matrix(ACCEPTED_ROUTE_CALLER_MATRIX)


def test_falsification_matrix_rejects_mutation_u_redirect_303() -> None:
    mutated = {k: dict(v) for k, v in ACCEPTED_ROUTE_CALLER_MATRIX.items()}
    mutated["R-41"]["U"] = 303
    with pytest.raises(AssertionError, match=r"Mutation route R-41 must return 401 for U"):
        validate_route_caller_matrix(mutated)


def test_falsification_matrix_rejects_r41_c_success_303() -> None:
    mutated = {k: dict(v) for k, v in ACCEPTED_ROUTE_CALLER_MATRIX.items()}
    mutated["R-41"]["C"] = 303
    with pytest.raises(AssertionError, match=r"R-41 refuses Council"):
        validate_route_caller_matrix(mutated)


def test_falsification_matrix_rejects_r42_a_success_303() -> None:
    mutated = {k: dict(v) for k, v in ACCEPTED_ROUTE_CALLER_MATRIX.items()}
    mutated["R-42"]["A"] = 303
    with pytest.raises(AssertionError, match=r"R-42 refuses Administrator"):
        validate_route_caller_matrix(mutated)


def test_falsification_matrix_rejects_missing_caller() -> None:
    mutated = {k: dict(v) for k, v in ACCEPTED_ROUTE_CALLER_MATRIX.items()}
    del mutated["R-40"]["BG"]
    with pytest.raises(AssertionError, match=r"Route R-40 missing callers"):
        validate_route_caller_matrix(mutated)


# ===========================================================================
# Form Field Exactness Validators & Negative Probes
# ===========================================================================

def validate_form_exactness(
    html: str,
    *,
    expected_action_pattern: str,
    expected_named_fields: set[str],
    expected_method: str = "post",
) -> None:
    """Validates that a form with action matching expected_action_pattern has exact method
    and exact set of named controls with no extras or duplicates."""
    form_matches = list(re.finditer(r"<form\b([^>]*)>(.*?)</form>", html, flags=re.DOTALL | re.IGNORECASE))
    target_form = None
    for m in form_matches:
        attrs = m.group(1)
        action_m = re.search(r'action=(["\'])(.*?)\1', attrs)
        if action_m and re.search(expected_action_pattern, action_m.group(2)):
            target_form = m
            break

    assert target_form is not None, f"Form with action matching '{expected_action_pattern}' not found"
    attrs_str = target_form.group(1)
    body_str = target_form.group(2)

    method_m = re.search(r'method=(["\'])(.*?)\1', attrs_str, flags=re.IGNORECASE)
    assert method_m is not None, "Form must specify a method attribute"
    assert method_m.group(2).lower() == expected_method.lower(), f"Form method expected {expected_method}, got {method_m.group(2)}"

    named_fields: list[str] = []
    # Match input, select, textarea with name="..."
    for control_m in re.finditer(r"<(?:input|select|textarea)\b([^>]*)>", body_str, flags=re.IGNORECASE):
        c_attrs = control_m.group(1)
        name_m = re.search(r'name=(["\'])(.*?)\1', c_attrs)
        if name_m:
            named_fields.append(name_m.group(2))

    assert len(named_fields) == len(set(named_fields)), f"Duplicate named fields found in form: {named_fields}"
    assert set(named_fields) == expected_named_fields, f"Form named fields mismatch: expected {expected_named_fields}, got {set(named_fields)}"


PREVIEW_FORM_RE = re.compile(
    r"<form\b[^>]*action=([\"'])(?P<action>/v1/council/snapshots/(?P<snapshot_id>[^/\"']+)/preview-jobs)\1[^>]*>"
    r"(?P<body>.*?)</form>",
    flags=re.DOTALL | re.IGNORECASE,
)
NONCE_INPUT_RE = re.compile(
    r"<input\b[^>]*\bname=([\"'])nonce\1[^>]*>", flags=re.IGNORECASE
)
VALUE_ATTR_RE = re.compile(r"\bvalue=([\"'])(?P<value>.*?)\1", flags=re.DOTALL)


def extract_preview_nonces(html: str) -> dict[str, str]:
    """Every R-42 form's rendered nonce, keyed by the snapshot in its own action.

    Scoped to the `preview-jobs` action deliberately: `job_status_fragment.html`
    also renders an input named `nonce` (R-46, Step 9), and a bare search for
    `name="nonce"` would happily read that one and call it evidence.
    """
    found: dict[str, str] = {}
    for form in PREVIEW_FORM_RE.finditer(html):
        snapshot_id = form.group("snapshot_id")
        inputs = NONCE_INPUT_RE.findall(form.group("body"))
        assert len(inputs) == 1, (
            f"R-42 form for {snapshot_id} must carry exactly one nonce input, "
            f"found {len(inputs)}"
        )
        tag = NONCE_INPUT_RE.search(form.group("body")).group(0)
        value_m = VALUE_ATTR_RE.search(tag)
        assert value_m is not None, f"R-42 nonce input for {snapshot_id} has no value"
        found[snapshot_id] = value_m.group("value")
    assert found, "no R-42 preview form was rendered"
    return found


def assert_nonces_are_server_minted(
    nonces: dict[str, str], *, folder_ids: dict[str, str]
) -> None:
    """The three properties a rendered nonce must have, in one place.

    Nonempty, within its documented bound, and **not** the deterministic
    `snapshot_id:folder_id` the template used to invent — that value is stable
    for the life of a snapshot/folder pair, so every deliberate preview after the
    first collapsed onto the first job's request key.
    """
    for snapshot_id, nonce in nonces.items():
        assert nonce, f"R-42 nonce for {snapshot_id} is empty"
        folder_id = folder_ids[snapshot_id]
        # Checked before the bound, so a template that returned to the derived
        # value fails on *what it is* rather than incidentally on its length.
        assert nonce != f"{snapshot_id}:{folder_id}", (
            f"R-42 nonce for {snapshot_id} is the derived snapshot:folder value"
        )
        assert snapshot_id not in nonce, (
            f"R-42 nonce for {snapshot_id} embeds the snapshot id"
        )
        assert folder_id not in nonce, (
            f"R-42 nonce for {snapshot_id} embeds the folder id"
        )
        assert len(nonce) <= PREVIEW_NONCE_BOUND, (
            f"R-42 nonce for {snapshot_id} exceeds PREVIEW_NONCE_BOUND "
            f"({len(nonce)} > {PREVIEW_NONCE_BOUND})"
        )


def test_form_field_exactness_validators() -> None:
    sample_view = make_sample_snapshot_view(can_select_folder=True, can_preview=True)
    env = get_jinja_env()
    template = env.get_template("council_snapshots.html")
    rendered = template.render(view=sample_view, request=make_request())

    # R-41: {csrf_token, folder_id}
    validate_form_exactness(
        rendered,
        expected_action_pattern=r"/v1/admin/snapshots/[^/]+/folder",
        expected_named_fields={"csrf_token", "folder_id"},
    )

    # R-42: {csrf_token, nonce}
    validate_form_exactness(
        rendered,
        expected_action_pattern=r"/v1/council/snapshots/[^/]+/preview-jobs",
        expected_named_fields={"csrf_token", "nonce"},
    )


def test_falsification_r41_duplicate_field_fails() -> None:
    html = """
    <form method="post" action="/v1/admin/snapshots/11111111-1111-1111-1111-111111111111/folder">
      <input type="hidden" name="csrf_token" value="tok">
      <input type="text" name="folder_id" value="f1">
      <input type="text" name="folder_id" value="f2">
    </form>
    """
    with pytest.raises(AssertionError, match=r"Duplicate named fields found"):
        validate_form_exactness(
            html,
            expected_action_pattern=r"/v1/admin/snapshots/[^/]+/folder",
            expected_named_fields={"csrf_token", "folder_id"},
        )


def test_falsification_r41_extra_field_fails() -> None:
    html = """
    <form method="post" action="/v1/admin/snapshots/11111111-1111-1111-1111-111111111111/folder">
      <input type="hidden" name="csrf_token" value="tok">
      <input type="text" name="folder_id" value="f1">
      <input type="text" name="actor_count" value="32">
    </form>
    """
    with pytest.raises(AssertionError, match=r"Form named fields mismatch"):
        validate_form_exactness(
            html,
            expected_action_pattern=r"/v1/admin/snapshots/[^/]+/folder",
            expected_named_fields={"csrf_token", "folder_id"},
        )


def test_falsification_r42_wrong_action_fails() -> None:
    html = """
    <form method="post" action="/v1/council/snapshots/11111111-1111-1111-1111-111111111111/wrong-endpoint">
      <input type="hidden" name="csrf_token" value="tok">
      <input type="hidden" name="nonce" value="n1">
    </form>
    """
    with pytest.raises(AssertionError, match=r"Form with action matching .* not found"):
        validate_form_exactness(
            html,
            expected_action_pattern=r"/v1/council/snapshots/[^/]+/preview-jobs",
            expected_named_fields={"csrf_token", "nonce"},
        )


# ===========================================================================
# Structural AST Checks for Post-Yield Cleanup Discipline
# ===========================================================================

@dataclass
class TrackedStep8FixtureState:
    snapshot_ids: set[UUID] = field(default_factory=set)
    job_ids: set[UUID] = field(default_factory=set)


def inspect_step8_cleanup_fixture_ast(func_or_src: Any) -> None:
    if isinstance(func_or_src, str):
        tree = ast.parse(func_or_src)
    else:
        src = inspect.getsource(func_or_src)
        tree = ast.parse(src)

    func_def = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))

    # 1. Yield must exist
    yield_nodes = [node for node in ast.walk(func_def) if isinstance(node, ast.Yield)]
    assert len(yield_nodes) == 1, "Fixture must contain exactly one yield statement"
    yield_node = yield_nodes[0]
    yield_lineno = yield_node.lineno

    assert isinstance(yield_node.value, ast.Name), "Yield must return tracked state variable"
    tracked_var_name = yield_node.value.id

    # 2. Guard: if 'migrated_database' not in request.fixturenames: return
    if_nodes = [node for node in ast.walk(func_def) if isinstance(node, ast.If)]
    assert len(if_nodes) >= 1, "Fixture must guard database cleanup with an if-statement"
    guard_node = if_nodes[0]
    assert yield_lineno < guard_node.lineno, f"Yield at line {yield_lineno} must precede guard at line {guard_node.lineno}"

    # 3. Database resolution: request.getfixturevalue('migrated_database')
    res_calls = [
        node for node in ast.walk(func_def)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "getfixturevalue"
    ]
    assert len(res_calls) == 1, "Fixture must call request.getfixturevalue exactly once"
    res_call = res_calls[0]
    assert yield_lineno < res_call.lineno, f"Yield at line {yield_lineno} must precede database resolution at line {res_call.lineno}"
    assert len(res_call.args) == 1 and isinstance(res_call.args[0], ast.Constant) and res_call.args[0].value == "migrated_database"

    assigned_engine_var = None
    for node in ast.walk(func_def):
        if isinstance(node, ast.Assign) and any(n is res_call for n in ast.walk(node.value)):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                assigned_engine_var = node.targets[0].id
                break
    assert assigned_engine_var is not None, "Database resolution result must be assigned to an engine variable"

    # 4. Context managers on engine.begin()
    with_nodes = [node for node in ast.walk(func_def) if isinstance(node, ast.With)]
    assert len(with_nodes) == 2, f"Fixture must contain exactly two with-blocks on engine.begin(), found {len(with_nodes)}"

    # First with-block: clean_p3_3_tables and clean_p3_2_tables
    with1 = with_nodes[0]
    bound1 = with1.items[0].optional_vars.id
    clean_p3_3_calls = [
        node for node in ast.walk(with1)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "clean_p3_3_tables"
    ]
    assert len(clean_p3_3_calls) == 1, "clean_p3_3_tables must be called in with-block 1"
    assert clean_p3_3_calls[0].args[0].id == bound1

    # Second with-block: tracked entity absence verification on fresh connection
    with2 = with_nodes[1]
    bound2 = with2.items[0].optional_vars.id
    assert bound2 != bound1, "Second with-block must bind a fresh connection"

    for_loops = [node for node in ast.walk(with2) if isinstance(node, ast.For)]
    assert len(for_loops) >= 2, "Second with-block must iterate tracked snapshot_ids and job_ids"


@pytest.fixture(autouse=True)
def clean_between_step8_cases(request):
    """Guaranteed post-yield teardown and ID-specific fresh-connection absence verification."""
    tracked_state = TrackedStep8FixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return

    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_3_tables(connection)
        clean_p3_2_tables(connection)

    with engine.begin() as fresh_conn:
        for snap_id in tracked_state.snapshot_ids:
            remaining = fresh_conn.execute(
                text("SELECT count(*) FROM foundry_snapshots WHERE id = :id"),
                {"id": snap_id},
            ).scalar_one()
            assert remaining == 0, f"Cleanup failed: snapshot {snap_id} still exists"

        for j_id in tracked_state.job_ids:
            remaining = fresh_conn.execute(
                text("SELECT count(*) FROM reconciliation_jobs WHERE id = :id"),
                {"id": j_id},
            ).scalar_one()
            assert remaining == 0, f"Cleanup failed: job {j_id} still exists"


def test_structural_step8_fixture_cleans_after_yield() -> None:
    inspect_step8_cleanup_fixture_ast(clean_between_step8_cases)


def test_falsification_structural_fixture_rejects_resolution_before_yield() -> None:
    bad_code = """
def clean_between_step8_cases(request):
    engine = request.getfixturevalue("migrated_database")
    tracked_state = TrackedStep8FixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    with engine.begin() as connection:
        clean_p3_3_tables(connection)
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        for s in tracked_state.snapshot_ids:
            assert fresh_conn.execute(text("SELECT count(*) FROM foundry_snapshots WHERE id = :id"), {"id": s}).scalar_one() == 0
        for j in tracked_state.job_ids:
            assert fresh_conn.execute(text("SELECT count(*) FROM reconciliation_jobs WHERE id = :id"), {"id": j}).scalar_one() == 0
"""
    with pytest.raises(AssertionError, match=r"Yield at line .* must precede database resolution"):
        inspect_step8_cleanup_fixture_ast(bad_code)


# ===========================================================================
# Sample View Factories
# ===========================================================================

def make_sample_snapshot_view(
    *,
    state: str = "ready",
    can_select_folder: bool = True,
    can_preview: bool = True,
    has_more: bool = False,
    path_observed: bool = True,
    selected: bool = True,
    has_job: bool = True,
    row_count: int = 1,
    preview_nonce: str = SAMPLE_PREVIEW_NONCE,
) -> SnapshotListView:
    snapshots = []
    for i in range(row_count):
        snap_id = uuid4()
        folder_a = FolderChoice(
            folder_id=f"folder_active_{i}",
            folder_path=SafeText.bounded(f"/Actors/Characters/Active {i}", 120),
            actor_count=12,
            is_default=True,
            path_observed=path_observed,
        )
        folder_b = FolderChoice(
            folder_id=f"folder_archive_{i}",
            folder_path=SafeText.bounded(f"/Actors/Characters/Archive {i}", 120),
            actor_count=4,
            is_default=False,
            path_observed=path_observed,
        )
        job = None
        if has_job:
            job = JobStamp(
                job_id=uuid4(),
                kind=JobKind.PREVIEW,
                state=JobState.COMPLETED,
                updated_at=Instant.of(datetime(2026, 8, 21, 10, 0, tzinfo=timezone.utc)),
            )

        row = SnapshotRow(
            snapshot_id=snap_id,
            checksum_short="a1b2c3d4e5f6",
            checksum_full="a1b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890abcdef",
            world_id="the-guild",
            world_title=SafeText.bounded("The Guild Campaign", 120),
            core_version="12.331",
            system_id="dnd5e",
            system_version="3.3.1",
            actor_count=16,
            size_bytes=1048576,
            exported_at=Instant.of(datetime(2026, 8, 20, 18, 30, tzinfo=timezone.utc)),
            received_at=Instant.of(datetime(2026, 8, 20, 18, 45, tzinfo=timezone.utc)),
            received_via="foundry_module",
            selected_folder=folder_a if selected else None,
            selectable_folders=(folder_a, folder_b),
            applied=False,
            latest_job=job,
        )
        snapshots.append(row)

    return SnapshotListView(
        state="empty" if state == "empty" or not snapshots else "ready",
        snapshots=() if state == "empty" else tuple(snapshots),
        cursor=Cursor(has_more=has_more, token="cur_tok_opaque_xyz123" if has_more else None),
        can_select_folder=can_select_folder,
        can_preview=can_preview,
        csrf_token="test_csrf_token_val",
        preview_nonce=preview_nonce,
    )


# ===========================================================================
# Direct Jinja Render Tests
# ===========================================================================

def test_render_snapshot_list_ready_state() -> None:
    view = make_sample_snapshot_view(state="ready", can_select_folder=True, can_preview=True)
    env = get_jinja_env()
    rendered = env.get_template("council_snapshots.html").render(view=view, request=make_request())

    assert '<table class="council-table" data-state="ready">' in rendered
    assert "a1b2c3d4e5f6" in rendered
    assert 'title="a1b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890abcdef"' in rendered
    assert "The Guild Campaign" in rendered
    assert "(the-guild)" in rendered
    assert "12.331" in rendered
    assert "dnd5e 3.3.1" in rendered
    assert "16" in rendered
    assert "1048576 bytes" in rendered
    assert "foundry_module" in rendered
    assert "/Actors/Characters/Active 0" in rendered
    assert 'data-control="folder-selection"' in rendered
    assert 'data-control="preview"' in rendered
    assert "/v1/admin/snapshots/" in rendered
    assert "/v1/council/snapshots/" in rendered
    assert "/artifact" not in rendered
    assert "/download" not in rendered


def test_render_snapshot_list_empty_state() -> None:
    view = make_sample_snapshot_view(state="empty")
    env = get_jinja_env()
    rendered = env.get_template("council_snapshots.html").render(view=view, request=make_request())

    assert '<div class="empty-card" data-state="empty">' in rendered
    assert "No submitted snapshot is awaiting an import." in rendered
    assert '<table class="council-table"' not in rendered
    assert 'data-control="folder-selection"' not in rendered
    assert 'data-control="preview"' not in rendered


def test_render_snapshot_list_unobserved_path() -> None:
    view = make_sample_snapshot_view(path_observed=False)
    env = get_jinja_env()
    rendered = env.get_template("council_snapshots.html").render(view=view, request=make_request())

    assert 'data-path-observed="false"' in rendered
    assert "path awaiting preview" in rendered
    assert "folder_active_0" in rendered


def test_render_snapshot_list_unselected_folder() -> None:
    view = make_sample_snapshot_view(selected=False)
    env = get_jinja_env()
    rendered = env.get_template("council_snapshots.html").render(view=view, request=make_request())

    assert '<span data-state="unselected" class="text-muted text-xs">No folder selected</span>' in rendered
    # Preview form MUST NOT be rendered when selected_folder is None
    assert 'data-control="preview"' not in rendered


def test_render_snapshot_list_controls_omitted_when_not_permitted() -> None:
    view_no_admin = make_sample_snapshot_view(can_select_folder=False, can_preview=True)
    env = get_jinja_env()
    rendered_no_admin = env.get_template("council_snapshots.html").render(view=view_no_admin, request=make_request())
    assert 'data-control="folder-selection"' not in rendered_no_admin
    assert 'data-control="preview"' in rendered_no_admin

    view_no_council = make_sample_snapshot_view(can_select_folder=True, can_preview=False)
    rendered_no_council = env.get_template("council_snapshots.html").render(view=view_no_council, request=make_request())
    assert 'data-control="folder-selection"' in rendered_no_council
    assert 'data-control="preview"' not in rendered_no_council


def test_render_snapshot_list_cursor_pagination() -> None:
    view = make_sample_snapshot_view(has_more=True)
    env = get_jinja_env()
    rendered = env.get_template("council_snapshots.html").render(view=view, request=make_request())

    assert 'rel="next"' in rendered
    assert '/v1/council/snapshots?cursor=cur_tok_opaque_xyz123' in rendered


def test_render_preview_form_submits_the_view_supplied_nonce() -> None:
    """The template submits VM-14's value and derives nothing of its own."""
    view = make_sample_snapshot_view(row_count=3, can_preview=True)
    env = get_jinja_env()
    rendered = env.get_template("council_snapshots.html").render(
        view=view, request=make_request()
    )

    nonces = extract_preview_nonces(rendered)
    assert len(nonces) == 3, "one R-42 form per selected-folder row"
    assert_nonces_are_server_minted(
        nonces,
        folder_ids={
            str(row.snapshot_id): row.selected_folder.folder_id
            for row in view.snapshots
        },
    )
    # One rendered response, one identity: every form on the page submits it.
    assert set(nonces.values()) == {view.preview_nonce}


def test_render_preview_form_reflects_a_distinct_nonce_per_render() -> None:
    """Two renders of the **same rows** carry different values.

    The rows are built once and re-wrapped, so nothing but the minted value
    differs between the two renders — a template that derived the nonce from row
    data would produce two identical pages here, which is exactly the defect.
    """
    env = get_jinja_env()
    template = env.get_template("council_snapshots.html")

    base = make_sample_snapshot_view(preview_nonce=mint_preview_nonce())
    second = dataclasses.replace(base, preview_nonce=mint_preview_nonce())
    assert base.preview_nonce != second.preview_nonce
    assert base.snapshots == second.snapshots, "the rows must be identical"

    first_nonces = extract_preview_nonces(
        template.render(view=base, request=make_request())
    )
    second_nonces = extract_preview_nonces(
        template.render(view=second, request=make_request())
    )
    assert set(first_nonces.values()) == {base.preview_nonce}
    assert set(second_nonces.values()) == {second.preview_nonce}
    assert set(first_nonces.values()).isdisjoint(set(second_nonces.values())), (
        "separate renders reused one nonce"
    )


def test_mint_preview_nonce_is_opaque_bounded_and_unrepeated() -> None:
    """The primitive's own properties, asserted once rather than assumed."""
    minted = [mint_preview_nonce() for _ in range(64)]
    assert len(set(minted)) == 64, "mint_preview_nonce repeated a value"
    for nonce in minted:
        assert len(nonce) == PREVIEW_NONCE_BOUND
        assert re.fullmatch(r"[A-Za-z0-9_-]+", nonce), (
            f"nonce {nonce!r} is not URL/form-safe"
        )


def test_falsification_row_derived_nonce_is_rejected() -> None:
    """The guard that fails if the template returns to `snapshot_id:folder_id`."""
    snapshot_id = "11111111-1111-1111-1111-111111111111"
    folder_id = "folder_active_0"
    html = f"""
    <form method="post" action="/v1/council/snapshots/{snapshot_id}/preview-jobs">
      <input type="hidden" name="csrf_token" value="tok">
      <input type="hidden" name="nonce" value="{snapshot_id}:{folder_id}">
    </form>
    """
    nonces = extract_preview_nonces(html)
    with pytest.raises(AssertionError, match=r"is the derived snapshot:folder value"):
        assert_nonces_are_server_minted(
            nonces, folder_ids={snapshot_id: folder_id}
        )


def test_falsification_separate_renders_reusing_one_nonce_is_rejected() -> None:
    """The guard that fails if two deliberate renders repeat one identity."""
    first = {"11111111-1111-1111-1111-111111111111": "shared-nonce-value"}
    second = {"11111111-1111-1111-1111-111111111111": "shared-nonce-value"}
    with pytest.raises(AssertionError, match=r"separate renders reused one nonce"):
        assert set(first.values()).isdisjoint(set(second.values())), (
            "separate renders reused one nonce"
        )


def test_falsification_r42_nonce_from_another_route_is_not_matched() -> None:
    """The extractor must not read R-46's (Step 9) input and call it R-42's."""
    html = """
    <form method="post" action="/v1/council/jobs/abc/apply">
      <input type="hidden" name="csrf_token" value="tok">
      <input type="hidden" name="preview_token" value="pt">
      <input type="hidden" name="nonce" value="an-r46-nonce">
    </form>
    """
    with pytest.raises(AssertionError, match=r"no R-42 preview form was rendered"):
        extract_preview_nonces(html)


def test_adversarial_escaping_on_snapshots_template() -> None:
    env = get_jinja_env()
    template = env.get_template("council_snapshots.html")

    xss_payload = '<script>alert("xss")</script><img src=x onerror=alert(1)>"\'&<>'
    snap_id = uuid4()
    folder = FolderChoice(
        folder_id=f"folder_{xss_payload}",
        folder_path=SafeText.bounded(f"/Actors/{xss_payload}", 120),
        actor_count=5,
        is_default=True,
        path_observed=True,
    )
    row = SnapshotRow(
        snapshot_id=snap_id,
        checksum_short="123456789abc",
        checksum_full="123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0",
        world_id=f"world_{xss_payload}",
        world_title=SafeText.bounded(f"World {xss_payload}", 120),
        core_version=f"v_{xss_payload}",
        system_id=f"sys_{xss_payload}",
        system_version=f"ver_{xss_payload}",
        actor_count=10,
        size_bytes=2048,
        exported_at=Instant.of(datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc)),
        received_at=Instant.of(datetime(2026, 8, 20, 12, 5, tzinfo=timezone.utc)),
        received_via="operator",
        selected_folder=folder,
        selectable_folders=(folder,),
        applied=False,
        latest_job=None,
    )
    view = SnapshotListView(
        state="ready",
        snapshots=(row,),
        cursor=Cursor(has_more=False, token=None),
        can_select_folder=True,
        can_preview=True,
        csrf_token=f"csrf_{xss_payload}",
        # The nonce is server-minted and never carries caller text, but the
        # template must escape it like every other external attribute value:
        # this asserts the *rendering* is safe rather than trusting the mint.
        preview_nonce=f"nonce_{xss_payload}",
    )

    rendered = template.render(view=view, request=make_request())

    # Raw script or img tags must never appear unescaped
    assert "<script>alert" not in rendered
    assert "<img src=x" not in rendered
    assert "&lt;script&gt;alert" in rendered
    assert "&lt;img src=x" in rendered


def test_falsification_unescaped_xss_payload_fails() -> None:
    html_raw_xss = '<div data-field="world"><script>alert(1)</script></div>'
    with pytest.raises(AssertionError, match=r"Raw script tag found unescaped"):
        assert "<script>alert" not in html_raw_xss, "Raw script tag found unescaped"


# ===========================================================================
# Integrity and Digest Verification Tests
# ===========================================================================

def test_template_digests_match_implementation_corpus() -> None:
    found_templates = {
        p.name: compute_sha256(p)
        for p in TEMPLATE_ROOT.glob("*.html")
        if p.name != "base.html" and not p.name.startswith(".")
    }

    assert set(found_templates.keys()) == set(P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS.keys())
    for name, expected_sha in P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS.items():
        assert found_templates[name] == expected_sha, f"Digest mismatch for template '{name}'"


def test_asset_integrity_manifest_verification() -> None:
    assert MANIFEST_PATH.exists(), "Manifest file asset-integrity.sha256 missing"
    lines = [
        line.strip()
        for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert len(lines) == 3
    for line in lines:
        parts = line.split()
        assert len(parts) == 2
        digest, rel_path = parts[0], parts[1]
        target_path = ROOT / rel_path
        assert target_path.is_file(), f"Asset '{rel_path}' missing"
        actual_sha = compute_sha256(target_path)
        assert actual_sha == digest, f"Asset integrity failure for {rel_path}: {actual_sha} != {digest}"


def test_step_8_selectors_used_and_prohibited_excluded() -> None:
    css_file = next(STATIC_ROOT.glob("css/freedom-blades.*.css"))
    css_text = css_file.read_text()
    active_css = extract_active_css_classes(css_text)

    # Active selectors in template
    template_text = (TEMPLATE_ROOT / "council_snapshots.html").read_text()
    active_tmpl_classes = extract_active_template_classes([template_text])

    for sel in active_tmpl_classes:
        assert sel in active_css, f"Template class '{sel}' not defined in stylesheet"

    for prohibited in PROHIBITED_STEP_8_SELECTORS:
        assert prohibited not in active_css, f"Prohibited selector '{prohibited}' found in stylesheet"


# ===========================================================================
# Database-Backed HTTP Tests
# ===========================================================================

@pytest.mark.skipif(
    "TEST_DATABASE_URL" not in os.environ,
    reason="TEST_DATABASE_URL is not configured for a disposable PostgreSQL database.",
)
@pytest.mark.database
async def test_database_backed_snapshot_views_and_mutations(
    client, settings, migrated_database, clean_between_step8_cases
) -> None:
    """Comprehensive executable test suite for R-40, R-41, and R-42 using disposable PostgreSQL."""
    tracked_state: TrackedStep8FixtureState = clean_between_step8_cases
    callers = seed_callers(migrated_database, settings)
    u = callers["U"]
    n = callers["N"]
    m = callers["M"]
    c = callers["C"]
    a = callers["A"]
    ca = callers["CA"]
    bg = callers["BG"]
    ac = callers["AC"]

    # 1. Arrange baseline test data in database
    with migrated_database.begin() as connection:
        snap_id, snap_checksum = seed_snapshot(
            connection, folder_ids=(fx.ACTIVE_FOLDER_ID, fx.ARCHIVE_FOLDER_ID)
        )
        tracked_state.snapshot_ids.add(snap_id)

        # Seed an applied snapshot with distinct payload to verify R-40 filtering
        applied_snap_id, applied_checksum = seed_snapshot(
            connection,
            payload=b"distinct_applied_payload_content_123",
            folder_ids=(fx.ACTIVE_FOLDER_ID,),
        )
        tracked_state.snapshot_ids.add(applied_snap_id)
        seed_import(
            connection,
            snapshot_id=applied_snap_id,
            account_id=a.account_id,
            checksum=applied_checksum,
        )

    # -----------------------------------------------------------------------
    # R-40 Caller Matrix & Content Tests
    # -----------------------------------------------------------------------
    # U: 303 to login
    res_u = await client.get("/v1/council/snapshots", cookies=u.cookies(settings))
    assert res_u.status_code == 303
    assert res_u.headers["location"] == "/v1/login"

    # N: 403
    res_n = await client.get("/v1/council/snapshots", cookies=n.cookies(settings))
    assert res_n.status_code == 403

    # M: 403
    res_m = await client.get("/v1/council/snapshots", cookies=m.cookies(settings))
    assert res_m.status_code == 403

    # BG / AC: 403
    res_bg = await client.get("/v1/council/snapshots", cookies=bg.cookies(settings))
    assert res_bg.status_code == 403
    res_ac = await client.get("/v1/council/snapshots", cookies=ac.cookies(settings))
    assert res_ac.status_code == 403

    # C: 200 (without folder selected -> no preview control yet)
    res_c = await client.get("/v1/council/snapshots", cookies=c.cookies(settings))
    assert res_c.status_code == 200
    assert str(snap_id) in res_c.text
    assert snap_checksum in res_c.text
    assert str(applied_snap_id) not in res_c.text
    assert 'data-control="folder-selection"' not in res_c.text
    assert 'data-control="preview"' not in res_c.text  # no folder selected yet

    # A: 200 (with folder selection form)
    res_a = await client.get("/v1/council/snapshots", cookies=a.cookies(settings))
    assert res_a.status_code == 200
    assert 'data-control="folder-selection"' in res_a.text
    assert 'data-control="preview"' not in res_a.text

    # CA: 200
    res_ca = await client.get("/v1/council/snapshots", cookies=ca.cookies(settings))
    assert res_ca.status_code == 200

    # -----------------------------------------------------------------------
    # R-41 Folder Selection Mutation & Security Tests
    # -----------------------------------------------------------------------
    folder_action = f"/v1/admin/snapshots/{snap_id}/folder"

    # Missing CSRF
    res_no_csrf = await client.post(
        folder_action,
        cookies=a.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=f"folder_id={fx.ACTIVE_FOLDER_ID}",
    )
    assert res_no_csrf.status_code == 403
    assert res_no_csrf.json()["error"] == "csrf_invalid"

    # Missing Origin
    res_no_orig = await client.post(
        folder_action,
        cookies=a.cookies(settings),
        headers={"Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, a)}&folder_id={fx.ACTIVE_FOLDER_ID}",
    )
    assert res_no_orig.status_code == 403
    assert res_no_orig.json()["error"] == "origin_invalid"

    # Invalid Content-Type
    res_bad_ct = await client.post(
        folder_action,
        cookies=a.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": "application/json"},
        content=b"{}",
    )
    assert res_bad_ct.status_code == 415

    # Body too large (> 4 KiB)
    large_payload = "a" * (5 * 1024)
    res_large = await client.post(
        folder_action,
        cookies=a.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM, "Content-Length": str(len(large_payload))},
        content=large_payload,
    )
    assert res_large.status_code == 413

    # Missing folder_id -> 422
    res_missing_f = await client.post(
        folder_action,
        cookies=a.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, a)}&folder_id=",
    )
    assert res_missing_f.status_code == 422

    # Malformed snapshot ID -> 404
    res_bad_uuid = await client.post(
        "/v1/admin/snapshots/not-a-uuid/folder",
        cookies=a.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, a)}&folder_id={fx.ACTIVE_FOLDER_ID}",
    )
    assert res_bad_uuid.status_code == 404
    assert res_bad_uuid.json()["error"] == "object_not_reachable"

    # Unreachable snapshot ID -> 404
    res_absent_uuid = await client.post(
        f"/v1/admin/snapshots/{uuid4()}/folder",
        cookies=a.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, a)}&folder_id={fx.ACTIVE_FOLDER_ID}",
    )
    assert res_absent_uuid.status_code == 404
    assert res_absent_uuid.json()["error"] == "snapshot_absent"

    # R-41 Caller Matrix Direct Calls
    for role, caller in callers.items():
        expected_st = ACCEPTED_ROUTE_CALLER_MATRIX["R-41"][role]
        post_res = await client.post(
            folder_action,
            cookies=caller.cookies(settings) if role != "U" else {},
            headers={"Origin": settings.public_origin, "Content-Type": FORM} if role != "U" else {},
            content=f"csrf_token={csrf_token_for(settings, caller) if role != 'U' else ''}&folder_id={fx.ACTIVE_FOLDER_ID}",
        )
        assert post_res.status_code == expected_st, f"R-41 caller {role} status mismatch: expected {expected_st}, got {post_res.status_code}"

    # Seed an active job to prove atomic invalidation on folder change
    with migrated_database.begin() as connection:
        active_job_id = seed_job(
            connection,
            snapshot_id=snap_id,
            account_id=c.account_id,
            checksum=snap_checksum,
            kind=JobKind.PREVIEW,
            state=JobState.QUEUED,
        )
        tracked_state.job_ids.add(active_job_id)

    # Successful folder selection by Administrator A (changing to ARCHIVE folder triggers invalidation)
    res_folder_ok = await client.post(
        folder_action,
        cookies=a.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, a)}&folder_id={fx.ARCHIVE_FOLDER_ID}",
    )
    assert res_folder_ok.status_code == 303
    assert res_folder_ok.headers["location"] == "/v1/council/snapshots"

    # Verify atomic invalidation in database: queued job transitioned to stale
    with migrated_database.begin() as connection:
        job_st = connection.execute(
            text("SELECT state, stale_reason FROM reconciliation_jobs WHERE id = :id"),
            {"id": active_job_id},
        ).mappings().one()
        assert job_st["state"] == "stale"
        assert job_st["stale_reason"] == "folder_changed"

    # -----------------------------------------------------------------------
    # R-42 Preview Creation Mutation, Security & Idempotency Tests
    # -----------------------------------------------------------------------
    preview_action = f"/v1/council/snapshots/{snap_id}/preview-jobs"
    # A real minted nonce, not a hand-shaped string. R-42 admits exactly what
    # R-40 mints, so a fixture that used `f"{snap_id}:nonce_12345"` would now be
    # testing the refusal path while claiming to test the success path.
    test_nonce = mint_preview_nonce()

    # Missing CSRF
    res_prev_no_csrf = await client.post(
        preview_action,
        cookies=c.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=f"nonce={test_nonce}",
    )
    assert res_prev_no_csrf.status_code == 403
    assert res_prev_no_csrf.json()["error"] == "csrf_invalid"

    # Missing Origin
    res_prev_no_orig = await client.post(
        preview_action,
        cookies=c.cookies(settings),
        headers={"Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, c)}&nonce={test_nonce}",
    )
    assert res_prev_no_orig.status_code == 403
    assert res_prev_no_orig.json()["error"] == "origin_invalid"

    # Missing nonce -> 422
    res_prev_no_nonce = await client.post(
        preview_action,
        cookies=c.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, c)}&nonce=",
    )
    assert res_prev_no_nonce.status_code == 422

    # Malformed snapshot ID -> 404
    res_prev_bad_uuid = await client.post(
        "/v1/council/snapshots/not-a-uuid/preview-jobs",
        cookies=c.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, c)}&nonce={test_nonce}",
    )
    assert res_prev_bad_uuid.status_code == 404
    assert res_prev_bad_uuid.json()["error"] == "object_not_reachable"

    # Unreachable snapshot ID -> 404
    res_prev_absent = await client.post(
        f"/v1/council/snapshots/{uuid4()}/preview-jobs",
        cookies=c.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, c)}&nonce={test_nonce}",
    )
    assert res_prev_absent.status_code == 404
    assert res_prev_absent.json()["error"] == "snapshot_absent"

    # R-42 Caller Matrix Direct Calls
    for role, caller in callers.items():
        expected_st = ACCEPTED_ROUTE_CALLER_MATRIX["R-42"][role]
        post_res = await client.post(
            preview_action,
            cookies=caller.cookies(settings) if role != "U" else {},
            headers={"Origin": settings.public_origin, "Content-Type": FORM} if role != "U" else {},
            content=f"csrf_token={csrf_token_for(settings, caller) if role != 'U' else ''}&nonce={mint_preview_nonce()}",
        )
        assert post_res.status_code == expected_st, f"R-42 caller {role} status mismatch: expected {expected_st}, got {post_res.status_code}"

    # Successful preview creation by Council C
    res_prev_ok = await client.post(
        preview_action,
        cookies=c.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, c)}&nonce={test_nonce}",
    )
    assert res_prev_ok.status_code == 303
    job_redirect_location = res_prev_ok.headers["location"]
    assert job_redirect_location.startswith("/v1/council/jobs/")
    created_job_id = UUID(job_redirect_location.split("/")[-1])
    tracked_state.job_ids.add(created_job_id)

    # Idempotency / Double-click retry with exact same nonce
    res_prev_retry = await client.post(
        preview_action,
        cookies=c.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, c)}&nonce={test_nonce}",
    )
    assert res_prev_retry.status_code == 303
    assert res_prev_retry.headers["location"] == job_redirect_location

    # Verify single job row and single audit event in database
    with migrated_database.begin() as connection:
        job_count = connection.execute(
            text("SELECT count(*) FROM reconciliation_jobs WHERE id = :j"),
            {"j": created_job_id},
        ).scalar_one()
        assert job_count == 1

        audit_count = connection.execute(
            text("SELECT count(*) FROM audit_events WHERE action = 'reconciliation.job_queued' AND entity_id = :j"),
            {"j": str(created_job_id)},
        ).scalar_one()
        assert audit_count == 1


@pytest.mark.skipif(
    "TEST_DATABASE_URL" not in os.environ,
    reason="TEST_DATABASE_URL is not configured for a disposable PostgreSQL database.",
)
@pytest.mark.database
async def test_rendered_r42_nonce_is_server_minted_per_render(
    client, settings, migrated_database, clean_between_step8_cases
) -> None:
    """The R-42 browser contract, end to end, from the bytes R-40 actually sent.

    The existing idempotency evidence above constructs its nonce by hand, which
    proves the backend primitive and nothing about the page. This test never
    invents one: every value it submits is extracted from a real R-40 response,
    so a template that re-derived the nonce from row data — the defect this
    closes — fails here even though the primitive is untouched.
    """
    tracked_state: TrackedStep8FixtureState = clean_between_step8_cases
    callers = seed_callers(migrated_database, settings)
    council = callers["C"]
    administrator = callers["A"]

    # 1. A reachable unapplied snapshot with a folder already selected, so the
    #    Council caller's page renders the R-42 form on the first request.
    with migrated_database.begin() as connection:
        snapshot_id, _checksum = seed_snapshot(
            connection, folder_ids=(fx.ACTIVE_FOLDER_ID, fx.ARCHIVE_FOLDER_ID)
        )
        tracked_state.snapshot_ids.add(snapshot_id)
        select_folder(
            connection,
            snapshot_id=snapshot_id,
            account_id=administrator.account_id,
            folder_id=fx.ACTIVE_FOLDER_ID,
        )

    preview_action = f"/v1/council/snapshots/{snapshot_id}/preview-jobs"
    folder_ids = {str(snapshot_id): fx.ACTIVE_FOLDER_ID}

    async def render_and_extract() -> str:
        """One deliberate R-40 render, and that response's own R-42 nonce."""
        response = await client.get(
            "/v1/council/snapshots", cookies=council.cookies(settings)
        )
        assert response.status_code == 200
        # 4. The successful form's named fields are exactly {csrf_token, nonce}.
        validate_form_exactness(
            response.text,
            expected_action_pattern=(
                rf"/v1/council/snapshots/{snapshot_id}/preview-jobs"
            ),
            expected_named_fields={"csrf_token", "nonce"},
        )
        # 2/3. Narrowly located, then checked for the three properties.
        nonces = extract_preview_nonces(response.text)
        assert set(nonces) == {str(snapshot_id)}
        assert_nonces_are_server_minted(nonces, folder_ids=folder_ids)
        return nonces[str(snapshot_id)]

    async def submit(nonce: str) -> str:
        response = await client.post(
            preview_action,
            cookies=council.cookies(settings),
            headers={"Origin": settings.public_origin, "Content-Type": FORM},
            content=(
                f"csrf_token={csrf_token_for(settings, council)}"
                f"&nonce={urllib.parse.quote(nonce, safe='')}"
            ),
        )
        assert response.status_code == 303
        location = response.headers["location"]
        assert location.startswith("/v1/council/jobs/")
        return location

    def queue_events(job_id: UUID) -> int:
        with migrated_database.begin() as connection:
            return connection.execute(
                text(
                    "SELECT count(*) FROM audit_events "
                    "WHERE action = 'reconciliation.job_queued' AND entity_id = :j"
                ),
                {"j": str(job_id)},
            ).scalar_one()

    def jobs_for_snapshot() -> set[UUID]:
        with migrated_database.begin() as connection:
            return {
                row[0]
                for row in connection.execute(
                    text(
                        "SELECT id FROM reconciliation_jobs "
                        "WHERE snapshot_id = :s AND kind = 'preview'"
                    ),
                    {"s": snapshot_id},
                )
            }

    # -- the same rendered form, submitted twice ---------------------------
    first_nonce = await render_and_extract()

    # 5. Two submissions of *that one rendered form* resolve to one job.
    first_location = await submit(first_nonce)
    retry_location = await submit(first_nonce)
    assert retry_location == first_location, (
        "resubmitting one rendered form must return the existing job's redirect"
    )

    first_job_id = UUID(first_location.rsplit("/", 1)[-1])
    tracked_state.job_ids.add(first_job_id)

    # 6. One durable job, one queue audit event.
    assert jobs_for_snapshot() == {first_job_id}
    assert queue_events(first_job_id) == 1

    # -- a separately rendered form ----------------------------------------
    # 7. A second deliberate render mints a different identity for the same row.
    second_nonce = await render_and_extract()
    assert second_nonce != first_nonce, (
        "a separately rendered R-40 response reused the first render's nonce"
    )

    # 8. And it creates a distinct job with exactly one additional queue event.
    second_location = await submit(second_nonce)
    assert second_location != first_location
    second_job_id = UUID(second_location.rsplit("/", 1)[-1])
    tracked_state.job_ids.add(second_job_id)

    assert jobs_for_snapshot() == {first_job_id, second_job_id}
    assert queue_events(second_job_id) == 1
    assert queue_events(first_job_id) == 1, (
        "the second preview must not have added an event to the first job"
    )

    # The identity is a digest, never the submitted text: R-42 hashes the nonce
    # with server-read facts, so neither rendered value is durable anywhere.
    with migrated_database.begin() as connection:
        keys = {
            row[0]
            for row in connection.execute(
                text(
                    "SELECT request_key FROM reconciliation_jobs "
                    "WHERE id IN (:a, :b)"
                ),
                {"a": first_job_id, "b": second_job_id},
            )
        }
    assert len(keys) == 2, "two deliberate previews must hold two request keys"
    for key in keys:
        assert first_nonce not in key and second_nonce not in key, (
            "the raw nonce text must not be persisted in request_key"
        )


# ---------------------------------------------------------------------------
# R-42 nonce boundary — the submitted value, admitted only as the minted shape
# ---------------------------------------------------------------------------

#: Every submitted `nonce` R-42 must refuse, named by what is wrong with it.
#:
#: Built from `PREVIEW_NONCE_BOUND` rather than from the literal 43, so the
#: off-by-one cases stay off by one if the accepted width ever moves. `None`
#: means "send no `nonce` field at all", which is a different request from one
#: carrying an empty value and is refused for a different reason.
MALFORMED_R42_NONCES: list[tuple[str, str | None]] = [
    ("absent", None),
    ("empty", ""),
    ("one_short", "a" * (PREVIEW_NONCE_BOUND - 1)),
    ("one_long", "a" * (PREVIEW_NONCE_BOUND + 1)),
    ("far_too_long", "a" * (PREVIEW_NONCE_BOUND * 4)),
    # Right width, wrong alphabet. base64url has no padding, no `+` and no `/`,
    # so each of these is a value the platform never minted.
    ("padding", "a" * (PREVIEW_NONCE_BOUND - 1) + "="),
    ("solidus", "a" * (PREVIEW_NONCE_BOUND - 1) + "/"),
    ("plus", "a" * (PREVIEW_NONCE_BOUND - 1) + "+"),
    ("dot", "a" * (PREVIEW_NONCE_BOUND - 1) + "."),
    ("colon", "a" * (PREVIEW_NONCE_BOUND - 1) + ":"),
    # Whitespace at the right width, and whitespace that would *become* the
    # right width if the boundary trimmed it. The second pair is the point: a
    # boundary that stripped would turn both into an accepted 43-character
    # value, which is precisely the normalization VM-14 forbids.
    ("inner_space", "a" * (PREVIEW_NONCE_BOUND - 1) + " "),
    ("leading_space_padded", " " + "a" * PREVIEW_NONCE_BOUND),
    ("trailing_space_padded", "a" * PREVIEW_NONCE_BOUND + " "),
    ("surrounding_whitespace_padded", "\t" + "a" * PREVIEW_NONCE_BOUND + "\n"),
    ("newline", "a" * (PREVIEW_NONCE_BOUND - 1) + "\n"),
    # Control characters, at the accepted width.
    ("null_byte", "a" * (PREVIEW_NONCE_BOUND - 1) + "\x00"),
    ("carriage_return", "a" * (PREVIEW_NONCE_BOUND - 1) + "\r"),
    # Non-ASCII at the accepted *character* width, which is a longer byte
    # sequence — the case a length check on bytes would admit.
    ("unicode", "a" * (PREVIEW_NONCE_BOUND - 1) + "é"),
    ("homoglyph", "a" * (PREVIEW_NONCE_BOUND - 1) + "А"),  # Cyrillic capital A
    ("emoji", "a" * (PREVIEW_NONCE_BOUND - 1) + "🙂"),
    # Shaped like the fixture the idempotency evidence used to invent, which is
    # what made the missing validation invisible.
    ("hand_shaped", "nonce_12345"),
]


@pytest.mark.skipif(
    "TEST_DATABASE_URL" not in os.environ,
    reason="TEST_DATABASE_URL is not configured for a disposable PostgreSQL database.",
)
@pytest.mark.database
@pytest.mark.parametrize(
    "case, submitted", MALFORMED_R42_NONCES, ids=[c for c, _ in MALFORMED_R42_NONCES]
)
async def test_r42_refuses_every_nonce_that_is_not_the_minted_shape(
    client,
    settings,
    migrated_database,
    clean_between_step8_cases,
    case: str,
    submitted: str | None,
) -> None:
    """VM-14, at the request boundary, **without rendering R-40 first**.

    The gap this closes: R-42 stripped the submitted value and checked it was
    not empty, so any text at all was a request identity. Every existing piece of
    idempotency evidence went through a form the server had rendered, or through
    a hand-built string the route happened to accept, and neither can see a
    boundary that admits arbitrary input — which is why this test is a direct
    `POST` that never fetches the page.

    Refusal is the accepted `422` validation response, and it must cost nothing:
    the assertions below read `reconciliation_jobs` and `audit_events` on a fresh
    connection afterwards, because "refused" and "refused without effect" are
    different claims and only the second one is the contract.
    """
    tracked_state: TrackedStep8FixtureState = clean_between_step8_cases
    callers = seed_callers(migrated_database, settings)
    council = callers["C"]
    administrator = callers["A"]

    with migrated_database.begin() as connection:
        snapshot_id, _checksum = seed_snapshot(
            connection, folder_ids=(fx.ACTIVE_FOLDER_ID,)
        )
        tracked_state.snapshot_ids.add(snapshot_id)
        select_folder(
            connection,
            snapshot_id=snapshot_id,
            account_id=administrator.account_id,
            folder_id=fx.ACTIVE_FOLDER_ID,
        )

    body = f"csrf_token={csrf_token_for(settings, council)}"
    if submitted is not None:
        body += f"&nonce={urllib.parse.quote(submitted, safe='')}"
    # R-42's accepted body bound is 4 KiB; every case above stays inside it, so
    # what is being proved is the nonce rule and not the size middleware.
    assert len(body.encode()) < 4096

    response = await client.post(
        f"/v1/council/snapshots/{snapshot_id}/preview-jobs",
        cookies=council.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=body,
    )

    assert response.status_code == 422, f"{case} was not refused as invalid input"

    # No job, and no success audit effect. Read on a fresh connection, after the
    # request completed, for the same reason R-37's durability cases do.
    with migrated_database.begin() as connection:
        assert (
            connection.execute(
                text(
                    "SELECT count(*) FROM reconciliation_jobs WHERE snapshot_id = :s"
                ),
                {"s": snapshot_id},
            ).scalar_one()
            == 0
        ), f"{case} enqueued a job"
        assert (
            connection.execute(
                text(
                    "SELECT count(*) FROM audit_events "
                    "WHERE action = 'reconciliation.job_queued'"
                )
            ).scalar_one()
            == 0
        ), f"{case} recorded a queued-job audit event"


@pytest.mark.skipif(
    "TEST_DATABASE_URL" not in os.environ,
    reason="TEST_DATABASE_URL is not configured for a disposable PostgreSQL database.",
)
@pytest.mark.database
async def test_r42_refuses_an_oversized_nonce_inside_the_accepted_body_bound(
    client, settings, migrated_database, clean_between_step8_cases
) -> None:
    """A nonce as large as R-42's 4 KiB body allows is still refused, and cheaply.

    Separate from the table above because the interesting property is that the
    request is *admissible*: it passes the guard's body bound, so the refusal is
    the nonce rule doing the work rather than the size middleware answering first
    and hiding the fact that the rule was never consulted.
    """
    tracked_state: TrackedStep8FixtureState = clean_between_step8_cases
    callers = seed_callers(migrated_database, settings)
    council = callers["C"]
    administrator = callers["A"]

    with migrated_database.begin() as connection:
        snapshot_id, _checksum = seed_snapshot(
            connection, folder_ids=(fx.ACTIVE_FOLDER_ID,)
        )
        tracked_state.snapshot_ids.add(snapshot_id)
        select_folder(
            connection,
            snapshot_id=snapshot_id,
            account_id=administrator.account_id,
            folder_id=fx.ACTIVE_FOLDER_ID,
        )

    prefix = f"csrf_token={csrf_token_for(settings, council)}&nonce="
    # As long as the accepted body bound permits, and no longer: a 413 would
    # prove the middleware works, not the boundary.
    body = prefix + "A" * (4000 - len(prefix))
    assert len(body.encode()) < 4096

    response = await client.post(
        f"/v1/council/snapshots/{snapshot_id}/preview-jobs",
        cookies=council.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=body,
    )
    assert response.status_code == 422

    with migrated_database.begin() as connection:
        assert (
            connection.execute(
                text("SELECT count(*) FROM reconciliation_jobs WHERE snapshot_id = :s"),
                {"s": snapshot_id},
            ).scalar_one()
            == 0
        )


@pytest.mark.skipif(
    "TEST_DATABASE_URL" not in os.environ,
    reason="TEST_DATABASE_URL is not configured for a disposable PostgreSQL database.",
)
@pytest.mark.database
async def test_r42_refuses_a_body_carrying_two_nonce_fields(
    client, settings, migrated_database, clean_between_step8_cases
) -> None:
    """Two `nonce` keys is not a request with a nonce, it is an ambiguous request.

    A form body may repeat a key, and the parsed mapping resolves the repeat by
    precedence rather than by refusing it. A body carrying one minted nonce and
    one hostile value would therefore be admitted on whichever the parser kept —
    and R-42 needs the request to have *one* identity, so both orderings are
    refused rather than resolved.
    """
    tracked_state: TrackedStep8FixtureState = clean_between_step8_cases
    callers = seed_callers(migrated_database, settings)
    council = callers["C"]
    administrator = callers["A"]

    with migrated_database.begin() as connection:
        snapshot_id, _checksum = seed_snapshot(
            connection, folder_ids=(fx.ACTIVE_FOLDER_ID,)
        )
        tracked_state.snapshot_ids.add(snapshot_id)
        select_folder(
            connection,
            snapshot_id=snapshot_id,
            account_id=administrator.account_id,
            folder_id=fx.ACTIVE_FOLDER_ID,
        )

    minted = mint_preview_nonce()
    hostile = "b" * PREVIEW_NONCE_BOUND
    for first, second in ((minted, hostile), (hostile, minted), (minted, minted)):
        response = await client.post(
            f"/v1/council/snapshots/{snapshot_id}/preview-jobs",
            cookies=council.cookies(settings),
            headers={"Origin": settings.public_origin, "Content-Type": FORM},
            content=(
                f"csrf_token={csrf_token_for(settings, council)}"
                f"&nonce={first}&nonce={second}"
            ),
        )
        assert response.status_code == 422, (
            "a body with two nonce fields has no single request identity"
        )

    with migrated_database.begin() as connection:
        assert (
            connection.execute(
                text("SELECT count(*) FROM reconciliation_jobs WHERE snapshot_id = :s"),
                {"s": snapshot_id},
            ).scalar_one()
            == 0
        )


@pytest.mark.skipif(
    "TEST_DATABASE_URL" not in os.environ,
    reason="TEST_DATABASE_URL is not configured for a disposable PostgreSQL database.",
)
@pytest.mark.database
async def test_r42_denial_precedence_is_unchanged_by_the_nonce_rule(
    client, settings, migrated_database, clean_between_step8_cases
) -> None:
    """A perfect nonce buys nothing, and a malformed one is not a shortcut.

    Both halves matter. The first is the contract's: possession of a request
    identity is not authorization, so an unauthenticated or non-Council caller
    submitting a genuinely minted nonce is still refused by the guard, with the
    guard's status. The second is the *new* rule's: adding validation must not
    let a malformed body answer `422` **before** the guard has refused, which
    would turn the validation response into an oracle for "this snapshot exists"
    reachable without Council authority.
    """
    tracked_state: TrackedStep8FixtureState = clean_between_step8_cases
    callers = seed_callers(migrated_database, settings)
    administrator = callers["A"]

    with migrated_database.begin() as connection:
        snapshot_id, _checksum = seed_snapshot(
            connection, folder_ids=(fx.ACTIVE_FOLDER_ID,)
        )
        tracked_state.snapshot_ids.add(snapshot_id)
        select_folder(
            connection,
            snapshot_id=snapshot_id,
            account_id=administrator.account_id,
            folder_id=fx.ACTIVE_FOLDER_ID,
        )

    action = f"/v1/council/snapshots/{snapshot_id}/preview-jobs"

    for role, caller in callers.items():
        expected = ACCEPTED_ROUTE_CALLER_MATRIX["R-42"][role]
        if expected == 303:
            continue
        for nonce in (mint_preview_nonce(), "not-a-minted-nonce"):
            response = await client.post(
                action,
                cookies=caller.cookies(settings) if role != "U" else {},
                headers=(
                    {"Origin": settings.public_origin, "Content-Type": FORM}
                    if role != "U"
                    else {}
                ),
                content=(
                    f"csrf_token={csrf_token_for(settings, caller) if role != 'U' else ''}"
                    f"&nonce={nonce}"
                ),
            )
            assert response.status_code == expected, (
                f"R-42 caller {role} must be refused by the guard, not by the "
                f"nonce rule (nonce={nonce!r})"
            )

    # And CSRF still precedes the nonce rule, both ways round.
    council = callers["C"]
    for nonce in (mint_preview_nonce(), "malformed"):
        response = await client.post(
            action,
            cookies=council.cookies(settings),
            headers={"Origin": settings.public_origin, "Content-Type": FORM},
            content=f"csrf_token=wrong&nonce={nonce}",
        )
        assert response.status_code == 403
        assert response.json()["error"] == "csrf_invalid"

    with migrated_database.begin() as connection:
        assert (
            connection.execute(
                text("SELECT count(*) FROM reconciliation_jobs WHERE snapshot_id = :s"),
                {"s": snapshot_id},
            ).scalar_one()
            == 0
        )


def test_r42_accepts_exactly_the_shape_r40_mints() -> None:
    """The shared rule, exercised directly: `mint` and `parse` are one contract.

    A unit-level companion to the HTTP cases, and the reason the route carries no
    literal `43` of its own — the width and the alphabet are stated once, in
    `application.web.jobs`, and both halves read the same statement.
    """
    for _ in range(64):
        minted = mint_preview_nonce()
        assert len(minted) == PREVIEW_NONCE_BOUND
        assert parse_preview_nonce(minted) == minted

    assert parse_preview_nonce("A" * PREVIEW_NONCE_BOUND) == "A" * PREVIEW_NONCE_BOUND
    assert parse_preview_nonce("-_" * 21 + "z") == "-_" * 21 + "z"

    # Nothing is normalized into acceptance, and nothing that is not text is
    # coerced into it.
    assert parse_preview_nonce(" " + "a" * PREVIEW_NONCE_BOUND) is None
    assert parse_preview_nonce("a" * PREVIEW_NONCE_BOUND + "\n") is None
    assert parse_preview_nonce(None) is None
    assert parse_preview_nonce(b"a" * PREVIEW_NONCE_BOUND) is None
    assert parse_preview_nonce(object()) is None
