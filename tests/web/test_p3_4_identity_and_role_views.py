"""Tests for P3.4 Step 7 Identity and Role Administration Views.

Covers:
1. VM-10 / R-28 / R-29 / R-30: `identity_migration.html`
   - Run metadata, dry-run notice, balanced totals (balances() equations).
   - Proposals list, 4 decision states (confirmed-and-active, confirmed-and-revoked, rejected, outstanding).
   - Candidate count & truncation reporting, fixed resulting_access_kind = "co_owner", evidence-only notices.
   - R-29 confirm form (csrf_token, version, reason; no version/candidate/subject body authority).
   - R-30 reject form (csrf_token, reason; no version).
2. VM-11 / R-31: `field_profile.html`
   - Strict read-only presentation (zero forms, zero inputs).
   - Unknown-path policy code "reported_never_writable".
   - Bounded field classifications (database_authority vs legacy_authority_deferred with owning_package).
   - Bounded snapshot paths with snapshot_mode.
3. VM-12 / R-32 / R-33 / R-34 / R-38: `role_capabilities.html`
   - Full administrator vs emergency continuity scopes.
   - Protected bootstrap mapping (revocable=False, protected=True, trigger explanation).
   - R-33 create mapping form (csrf_token, role_id, capability restricted to available_capabilities, reason).
   - R-34 revoke mapping form (csrf_token, version, reason; conditional on revocable).
   - R-38 ratify mapping form (csrf_token, version, reason; conditional on ratifiable).
   - Emergency continuity allowlist notice and N-67 restriction to platform_administrator.
4. VM-13 / R-35 / R-36 / R-37: `account_identities.html`
   - Caller account ID and bounded linked identities list (provider, full own subject_display, dates, state).
   - Retired identities visible without unlink control.
   - R-36 authenticated 200 HTML (state="denied", additional_provider="no_additional_provider"), unauthenticated 303 to login, BG/AC refused 403.
   - R-37 unlink form (csrf_token only; conditional on active and absent unlink_blocked_reason).
   - Unlink blocked reasons: last_usable_identity and emergency_session.
5. Strict XSS escaping for all dynamic / untrusted text across all 4 templates.
6. Shared teardown fixture with post-yield DB resolution inside membership guard, connection binding, and tracked ID-specific fresh-connection absence verification with rigorous AST data flow.
7. Exact active CSS selector and active template class-token scope validation with negative falsification probes.
8. All 23 template digests and static asset integrity protection.
9. Contract-derived route-authorization matrix validator (§5.2) with negative probes enforcing form mutation U=401, R-31 A=200, and R-32 BG=200.
10. Database-backed HTTP/security/mutation evidence across R-28–R-38 with live bound connections, accepted exact denial-policy response identity, case-specific audit snapshots, complete post-success event and audit attribution, and immediate complete no-write snapshots across refusal cases validated by executable semantic AST inspection.
"""
from __future__ import annotations

import ast
import hashlib
import inspect
import os
import re
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import jinja2
import pytest
from sqlalchemy import insert, text
from starlette.requests import Request

from adapters.database.tables import (
    external_identities,
    identity_link_proposal_candidates,
    identity_link_proposals,
    identity_migration_runs,
    role_capability_mapping_events,
    role_capability_mappings,
)
from application.audit import ActorCapability
from application.web.view_models import (
    AccessFact,
    AccountIdentitiesView,
    Actor,
    Correlation,
    CouncilCharacterRow,
    Cursor,
    FieldProfileView,
    IdentityMigrationView,
    Instant,
    LinkedIdentity,
    LinkProposal,
    MigrationRun,
    MigrationTotals,
    ProfileFieldRow,
    ProfilePathRow,
    ProviderOption,
    RoleCapabilityView,
    RoleMappingRow,
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

from tests.web.template_digests import P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS
from application.web.shell import ANONYMOUS_SHELL


# Contract §5.2 Authoritative Caller Matrix for R-28 through R-38
ACCEPTED_ROUTE_CALLER_MATRIX: dict[str, dict[str, int]] = {
    "R-28": {"U": 303, "N": 403, "M": 403, "C": 200, "A": 403, "CA": 200, "BG": 403, "AC": 403},
    "R-29": {"U": 401, "N": 403, "M": 403, "C": 303, "A": 403, "CA": 303, "BG": 403, "AC": 403},
    "R-30": {"U": 401, "N": 403, "M": 403, "C": 303, "A": 403, "CA": 303, "BG": 403, "AC": 403},
    "R-31": {"U": 303, "N": 403, "M": 403, "C": 200, "A": 200, "CA": 200, "BG": 403, "AC": 403},
    "R-32": {"U": 303, "N": 403, "M": 403, "C": 403, "A": 200, "CA": 200, "BG": 200, "AC": 200},
    "R-33": {"U": 401, "N": 403, "M": 403, "C": 403, "A": 303, "CA": 303, "BG": 303, "AC": 303},
    "R-34": {"U": 401, "N": 403, "M": 403, "C": 403, "A": 303, "CA": 303, "BG": 303, "AC": 303},
    "R-35": {"U": 303, "N": 200, "M": 200, "C": 200, "A": 200, "CA": 200, "BG": 200, "AC": 200},
    "R-36": {"U": 303, "N": 200, "M": 200, "C": 200, "A": 200, "CA": 200, "BG": 403, "AC": 403},
    "R-37": {"U": 401, "N": 303, "M": 303, "C": 303, "A": 303, "CA": 303, "BG": 403, "AC": 403},
    "R-38": {"U": 401, "N": 403, "M": 403, "C": 403, "A": 303, "CA": 303, "BG": 403, "AC": 403},
}

# Step 7 selectors added and used by Step 7 templates
STEP_7_SELECTORS: tuple[str, ...] = (
    ".migration-run-card",
    ".totals-card",
    ".totals-dl",
    ".totals-item",
    ".totals-dt",
    ".totals-dd",
    ".totals-balance-status",
    ".proposal-list",
    ".proposal-card",
    ".proposal-header",
    ".proposal-char-info",
    ".proposal-char-name",
    ".proposal-evidence-badges",
    ".proposal-subject-row",
    ".candidates-block",
    ".proposal-status-block",
    ".alert-sm",
    ".proposal-actions",
    ".confirm-summary-box",
    ".confirm-summary-text",
    ".confirm-form",
    ".reject-form",
    ".profile-list-card",
    ".profile-item-list",
    ".profile-entry-item",
    ".profile-entry-main",
    ".profile-key",
    ".profile-path",
    ".profile-separator",
    ".identity-separator",
    ".unratified-badge",
    ".mapping-list",
    ".mapping-card",
    ".mapping-header",
    ".mapping-title-group",
    ".mapping-snowflake",
    ".mapping-role-label",
    ".mapping-badges",
    ".mapping-meta",
    ".mapping-actions",
    ".create-mapping-card",
    ".create-mapping-form",
    ".identity-list",
    ".identity-card",
    ".identity-header",
    ".identity-title-group",
    ".identity-provider-name",
    ".identity-subject",
    ".identity-badges",
    ".identity-meta",
    ".identity-actions",
    ".additional-provider-card",
    ".section-subtitle",
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
    # The accepted N-26 policy uses CSP `frame-ancestors 'none'` and
    # deliberately omits the duplicate legacy header (TC-SEC-05).
    "x-frame-options",
)


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


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


def make_request(path: str = "/v1/council/identity-migration") -> Request:
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
    expected_routes = {"R-28", "R-29", "R-30", "R-31", "R-32", "R-33", "R-34", "R-35", "R-36", "R-37", "R-38"}
    assert set(matrix.keys()) == expected_routes, f"Matrix route set mismatch: expected {expected_routes}, got {set(matrix.keys())}"

    expected_callers = {"U", "N", "M", "C", "A", "CA", "BG", "AC"}
    mutation_routes = {"R-29", "R-30", "R-33", "R-34", "R-37", "R-38"}
    nav_routes = {"R-28", "R-31", "R-32", "R-35", "R-36"}

    for r_code, row in matrix.items():
        assert set(row.keys()) == expected_callers, f"Route {r_code} missing callers: {expected_callers - set(row.keys())}"

        # 1. Check Unauthenticated status
        if r_code in mutation_routes:
            assert row["U"] == 401, f"Mutation route {r_code} must return 401 for U, got {row['U']}"
        elif r_code in nav_routes:
            assert row["U"] == 303, f"Navigation route {r_code} must return 303 for U, got {row['U']}"

        # 2. Check AC equals BG across every single route
        assert row["AC"] == row["BG"], f"Route {r_code} AC status ({row['AC']}) must match BG status ({row['BG']})"

    # Specific contract invariants
    assert matrix["R-31"]["A"] == 200, f"R-31 Administrator caller must receive 200, got {matrix['R-31']['A']}"
    assert matrix["R-32"]["BG"] == 200, f"R-32 Break-glass caller must receive 200, got {matrix['R-32']['BG']}"
    assert matrix["R-36"]["BG"] == 403, f"R-36 Break-glass caller must receive 403, got {matrix['R-36']['BG']}"
    assert matrix["R-37"]["BG"] == 403, f"R-37 Break-glass caller must receive 403, got {matrix['R-37']['BG']}"
    assert matrix["R-38"]["BG"] == 403, f"R-38 Break-glass caller must receive 403, got {matrix['R-38']['BG']}"


def test_structural_route_caller_matrix_valid() -> None:
    validate_route_caller_matrix(ACCEPTED_ROUTE_CALLER_MATRIX)


def test_falsification_matrix_rejects_mutation_u_redirect_303() -> None:
    tampered = {k: dict(v) for k, v in ACCEPTED_ROUTE_CALLER_MATRIX.items()}
    tampered["R-29"]["U"] = 303
    with pytest.raises(AssertionError, match=r"Mutation route R-29 must return 401 for U, got 303"):
        validate_route_caller_matrix(tampered)


def test_falsification_matrix_rejects_r31_a_forbidden_403() -> None:
    tampered = {k: dict(v) for k, v in ACCEPTED_ROUTE_CALLER_MATRIX.items()}
    tampered["R-31"]["A"] = 403
    with pytest.raises(AssertionError, match=r"R-31 Administrator caller must receive 200, got 403"):
        validate_route_caller_matrix(tampered)


def test_falsification_matrix_rejects_r32_bg_forbidden_403() -> None:
    tampered = {k: dict(v) for k, v in ACCEPTED_ROUTE_CALLER_MATRIX.items()}
    tampered["R-32"]["BG"] = 403
    tampered["R-32"]["AC"] = 403
    with pytest.raises(AssertionError, match=r"R-32 Break-glass caller must receive 200, got 403"):
        validate_route_caller_matrix(tampered)


def test_falsification_matrix_rejects_missing_caller() -> None:
    tampered = {k: dict(v) for k, v in ACCEPTED_ROUTE_CALLER_MATRIX.items()}
    del tampered["R-35"]["AC"]
    with pytest.raises(AssertionError, match=r"Route R-35 missing callers"):
        validate_route_caller_matrix(tampered)


def _inspect_client_call_caller(call_node: ast.Call, context_desc: str) -> str:
    """Inspects an executed client.get/post AST Call node and extracts the validated caller tag.

    Rules:
    - For U (unauthenticated):
      * 'cookies' keyword must be omitted or be exactly 'u.cookies(settings)' where u is the unauthenticated seed caller.
      * No direct 'Cookie' header (case-insensitive) may be present in 'headers'.
      * Any other cookies expression (e.g. m.cookies(settings), literal dict, unknown var) is strictly rejected.
    - For authenticated callers (N, M, C, A, CA, BG, AC):
      * 'cookies' keyword must be present and have shape '<caller>.cookies(settings)'.
      * Returned tag is <caller>.upper().
    """
    kw = {k.arg: k.value for k in call_node.keywords}

    # Check headers for direct Cookie header
    if "headers" in kw:
        h_val = kw["headers"]
        if isinstance(h_val, ast.Dict):
            for k in h_val.keys:
                if isinstance(k, ast.Constant) and isinstance(k.value, str) and k.value.lower() == "cookie":
                    raise AssertionError(f"{context_desc}: Unauthenticated U request must not contain direct 'Cookie' header")

    cookie_kw = kw.get("cookies")
    if cookie_kw is None:
        return "U"

    if isinstance(cookie_kw, ast.Call) and isinstance(cookie_kw.func, ast.Attribute):
        if cookie_kw.func.attr == "cookies":
            caller_name = getattr(cookie_kw.func.value, "id", None)
            if caller_name:
                caller_tag = caller_name.upper()
                if caller_tag in {"U", "N", "M", "C", "A", "CA", "BG", "AC"}:
                    return caller_tag

    raise AssertionError(f"{context_desc}: Invalid cookies expression {ast.dump(cookie_kw)}")


def validate_matrix_execution_in_db_test(src_or_func: Any) -> None:
    """Verifies that every single cell in ACCEPTED_ROUTE_CALLER_MATRIX is explicitly
    executed in test_database_backed_identity_and_role_views_and_mutations with the
    exact caller and asserting the exact expected status code."""
    if isinstance(src_or_func, str):
        src = src_or_func
    else:
        src = inspect.getsource(src_or_func)
    tree = ast.parse(src)

    func_defs = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "test_database_backed_identity_and_role_views_and_mutations" in func_defs, "Database test missing"
    db_func = func_defs["test_database_backed_identity_and_role_views_and_mutations"]

    # Search for all pattern matches of form `res_<route>_<caller> = await client.<method>(...)`
    # and subsequent `assert res_<route>_<caller>.status_code == <expected>`
    executed_cells: dict[str, dict[str, int]] = {}
    assigned_callers: dict[str, set[str]] = {}

    for stmt in db_func.body:
        # Pattern 1: res_r<num>_<caller> = await client.get/post(...)
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
            t_name = stmt.targets[0].id
            m = re.match(r"^res_r(\d+)_([a-z0-9_]+)$", t_name)
            if m:
                r_num = m.group(1)
                r_code = f"R-{r_num}"
                var_caller_tag = m.group(2).upper()
                if var_caller_tag in {"U", "N", "M", "C", "A", "CA", "BG", "AC"}:
                    val = stmt.value
                    if isinstance(val, ast.Await) and isinstance(val.value, ast.Call):
                        actual_caller = _inspect_client_call_caller(val.value, f"Variable '{t_name}'")
                        assert actual_caller == var_caller_tag, (
                            f"Variable '{t_name}' specifies caller '{var_caller_tag}' but passes '{actual_caller}' in cookies"
                        )
                        if r_code not in assigned_callers:
                            assigned_callers[r_code] = set()
                        assert var_caller_tag not in assigned_callers[r_code], (
                            f"Duplicate execution of caller '{var_caller_tag}' for route '{r_code}'"
                        )
                        assigned_callers[r_code].add(var_caller_tag)

        # Pattern 2: assert (await client.<method>(...)).status_code == <expected>
        # or assert res_r<num>_<caller>.status_code == <expected>
        if isinstance(stmt, ast.Assert) and isinstance(stmt.test, ast.Compare):
            left = stmt.test.left
            status_val = None
            if len(stmt.test.comparators) == 1 and isinstance(stmt.test.comparators[0], ast.Constant):
                status_val = stmt.test.comparators[0].value

            if isinstance(left, ast.Attribute) and left.attr == "status_code":
                # Case A: res_r<num>_<caller>.status_code
                if isinstance(left.value, ast.Name):
                    m = re.match(r"^res_r(\d+)_([a-z0-9_]+)$", left.value.id)
                    if m:
                        r_num = m.group(1)
                        r_code = f"R-{r_num}"
                        caller_tag = m.group(2).upper()
                        if caller_tag in {"U", "N", "M", "C", "A", "CA", "BG", "AC"}:
                            if r_code not in executed_cells:
                                executed_cells[r_code] = {}
                            assert caller_tag not in executed_cells[r_code], (
                                f"Duplicate execution of caller '{caller_tag}' for route '{r_code}'"
                            )
                            executed_cells[r_code][caller_tag] = status_val

                # Case B: (await client.get/post(...)).status_code
                elif isinstance(left.value, ast.Await) and isinstance(left.value.value, ast.Call):
                    call_node = left.value.value
                    if len(call_node.args) >= 1:
                        path_arg = call_node.args[0]
                        path_str = ""
                        if isinstance(path_arg, ast.Constant):
                            path_str = path_arg.value
                        elif isinstance(path_arg, ast.JoinedStr):
                            # e.g. f"/v1/council/identity-migration/{prop1_id}/confirm"
                            for part in path_arg.values:
                                if isinstance(part, ast.Constant):
                                    path_str += part.value
                        
                        r_match = None
                        if "/v1/council/identity-migration/" in path_str and "/confirm" in path_str:
                            r_match = "R-29"
                        elif "/v1/council/identity-migration/" in path_str and "/reject" in path_str:
                            r_match = "R-30"
                        elif path_str.startswith("/v1/council/identity-migration"):
                            r_match = "R-28"
                        elif path_str.startswith("/v1/council/field-profile"):
                            r_match = "R-31"
                        elif path_str.startswith("/v1/admin/role-capabilities") and "/revoke" in path_str:
                            r_match = "R-34"
                        elif path_str.startswith("/v1/admin/role-capabilities") and "/ratify" in path_str:
                            r_match = "R-38"
                        elif path_str.startswith("/v1/admin/role-capabilities"):
                            r_match = "R-32" if call_node.func.attr == "get" else "R-33"
                        elif path_str.startswith("/v1/account/identities/link/start"):
                            r_match = "R-36"
                        elif "/v1/account/identities/" in path_str and "/unlink" in path_str:
                            r_match = "R-37"
                        elif path_str.startswith("/v1/account/identities"):
                            r_match = "R-35"

                        if r_match:
                            actual_caller = _inspect_client_call_caller(call_node, f"Inline request for route '{r_match}'")
                            if actual_caller in {"U", "N", "M", "C", "A", "CA", "BG", "AC"}:
                                if r_match not in executed_cells:
                                    executed_cells[r_match] = {}
                                assert actual_caller not in executed_cells[r_match], (
                                    f"Duplicate execution of caller '{actual_caller}' for route '{r_match}'"
                                )
                                executed_cells[r_match][actual_caller] = status_val

    # Verify that all cells from ACCEPTED_ROUTE_CALLER_MATRIX are in executed_cells and match expected status
    for r_code, expected_row in ACCEPTED_ROUTE_CALLER_MATRIX.items():
        assert r_code in executed_cells, f"Route '{r_code}' not executed in database test"
        for caller_tag, expected_status in expected_row.items():
            assert caller_tag in executed_cells[r_code], (
                f"Route '{r_code}' caller '{caller_tag}' missing execution in database test"
            )
            actual_status = executed_cells[r_code][caller_tag]
            assert actual_status == expected_status, (
                f"Route '{r_code}' caller '{caller_tag}' status mismatch: expected {expected_status}, executed assertion {actual_status}"
            )


def test_structural_matrix_execution_in_db_test() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    validate_matrix_execution_in_db_test(src)


def test_falsification_db_test_missing_cell_fails() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "assert (await client.get(\"/v1/council/identity-migration\", cookies=ac.cookies(settings))).status_code == 403",
        "# cell omitted",
    )
    with pytest.raises(AssertionError, match=r"Route 'R-28' caller 'AC' missing execution"):
        validate_matrix_execution_in_db_test(tampered)


def test_falsification_db_test_wrong_caller_fails() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "res_r35_ca = await client.get(\"/v1/account/identities\", cookies=ca.cookies(settings))",
        "res_r35_ca = await client.get(\"/v1/account/identities\", cookies=c.cookies(settings))",
    )
    with pytest.raises(AssertionError, match=r"Variable 'res_r35_ca' specifies caller 'CA' but passes 'C' in cookies"):
        validate_matrix_execution_in_db_test(tampered)


def test_falsification_db_test_status_mismatch_fails() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "assert res_r31_a.status_code == 200",
        "assert res_r31_a.status_code == 403",
    )
    with pytest.raises(AssertionError, match=r"Route 'R-31' caller 'A' status mismatch: expected 200, executed assertion 403"):
        validate_matrix_execution_in_db_test(tampered)


def test_falsification_db_test_duplicate_caller_fails() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "res_r35_ca = await client.get(\"/v1/account/identities\", cookies=ca.cookies(settings))",
        "res_r35_c = await client.get(\"/v1/account/identities\", cookies=c.cookies(settings))",
    )
    with pytest.raises(AssertionError, match=r"Duplicate execution of caller 'C' for route 'R-35'"):
        validate_matrix_execution_in_db_test(tampered)


def test_falsification_db_test_assigned_u_with_m_cookies_fails() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "res_r35_n = await client.get(\"/v1/account/identities\", cookies=n.cookies(settings))",
        "res_r35_u = await client.get(\"/v1/account/identities\", cookies=m.cookies(settings))",
    )
    with pytest.raises(AssertionError, match=r"Variable 'res_r35_u' specifies caller 'U' but passes 'M' in cookies"):
        validate_matrix_execution_in_db_test(tampered)


def test_falsification_db_test_inline_u_with_ca_cookies_fails() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "assert (await client.get(\"/v1/council/identity-migration\", cookies=u.cookies(settings))).status_code == 303",
        "assert (await client.get(\"/v1/council/identity-migration\", cookies=ca.cookies(settings))).status_code == 303",
    )
    with pytest.raises(AssertionError, match=r"Route 'R-28' caller 'U' missing execution in database test|Duplicate execution of caller 'CA' for route 'R-28'"):
        validate_matrix_execution_in_db_test(tampered)


def test_falsification_db_test_u_with_literal_cookies_dict_fails() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "assert (await client.get(\"/v1/council/identity-migration\", cookies=u.cookies(settings))).status_code == 303",
        "assert (await client.get(\"/v1/council/identity-migration\", cookies={\"session\": \"forged\"})).status_code == 303",
    )
    with pytest.raises(AssertionError, match=r"Invalid cookies expression"):
        validate_matrix_execution_in_db_test(tampered)


def test_falsification_db_test_u_with_direct_cookie_header_fails() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "assert (await client.post(f\"/v1/council/identity-migration/{prop1_c_id}/confirm\", cookies=u.cookies(settings), headers={\"content-type\": FORM, \"origin\": PUBLIC_ORIGIN}, content=\"version=0&reason=test\")).status_code == 401",
        "assert (await client.post(f\"/v1/council/identity-migration/{prop1_c_id}/confirm\", cookies=u.cookies(settings), headers={\"content-type\": FORM, \"origin\": PUBLIC_ORIGIN, \"Cookie\": \"session=forged\"}, content=\"version=0&reason=test\")).status_code == 401",
    )
    with pytest.raises(AssertionError, match=r"Unauthenticated U request must not contain direct 'Cookie' header"):
        validate_matrix_execution_in_db_test(tampered)


# ===========================================================================
# Fixture State & Teardown AST Validator
# ===========================================================================

class TrackedStep7FixtureState:
    def __init__(self) -> None:
        self.character_ids: set[UUID] = set()
        self.access_ids: set[UUID] = set()


def validate_step7_cleanup_fixture(func_or_src: Any) -> None:
    """Verifies that cleanup teardown strictly adheres to structural AST rules."""
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

    assert len(res_call.args) == 1 and isinstance(res_call.args[0], ast.Constant) and res_call.args[0].value == "migrated_database", (
        "Database resolution argument must be literal string 'migrated_database'"
    )

    guard_idx = -1
    res_idx = -1
    for i, stmt in enumerate(func_def.body):
        if stmt is guard_node:
            guard_idx = i
        if any(node is res_call for node in ast.walk(stmt)):
            res_idx = i
    assert guard_idx != -1 and res_idx != -1 and guard_idx < res_idx, "Database resolution must be guarded by membership check"

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

    for node in ast.walk(with2):
        if isinstance(node, ast.Assert):
            if isinstance(node.test, ast.Constant) and node.test.value is True:
                raise AssertionError("Second with-block contains trivial 'assert True'")
            if isinstance(node.test, ast.Compare):
                if isinstance(node.test.left, ast.Constant) and all(isinstance(c, ast.Constant) for c in node.test.comparators):
                    raise AssertionError("Second with-block contains literal constant comparison 'assert 0 == 0'")

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

        assign_nodes = [n for n in fl.body if isinstance(n, ast.Assign)]
        assert len(assign_nodes) == 1, f"Loop for '{attr}' must assign the scalar absence query result to a variable"
        assign_node = assign_nodes[0]
        assert len(assign_node.targets) == 1 and isinstance(assign_node.targets[0], ast.Name), (
            f"Query result must be assigned to a named variable in '{attr}' loop"
        )
        res_var = assign_node.targets[0].id

        assert isinstance(assign_node.value, ast.Call) and isinstance(assign_node.value.func, ast.Attribute) and assign_node.value.func.attr == "scalar_one", (
            f"Query in '{attr}' loop must call .scalar_one()"
        )
        exec_call = assign_node.value.func.value
        assert isinstance(exec_call, ast.Call) and isinstance(exec_call.func, ast.Attribute) and exec_call.func.attr == "execute", (
            f"Query in '{attr}' loop must call .execute()"
        )
        assert exec_call.func.value.id == bound2, f"Query must be executed on fresh connection '{bound2}'"

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

        param_arg = exec_call.args[1]
        assert isinstance(param_arg, ast.Dict), f"Parameters argument must be a dictionary in '{attr}' loop"
        assert len(param_arg.keys) == 1 and isinstance(param_arg.keys[0], ast.Constant) and param_arg.keys[0].value == "id", (
            f"Parameter dict must have single key 'id' in '{attr}' loop"
        )
        assert isinstance(param_arg.values[0], ast.Name) and param_arg.values[0].id == loop_var, (
            f"Parameter dict 'id' value must be loop variable '{loop_var}' in '{attr}' loop"
        )

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
def clean_between_step7_cases(request):
    """Guaranteed post-yield teardown and ID-specific fresh-connection absence verification."""
    tracked_state = TrackedStep7FixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    from tests.web.portal_fixtures import clean_p3_2_tables

    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
        # Append-only in production; the schema owner may truncate only for
        # disposable-test reset, matching the shared portal cleanup fixture.
        connection.execute(text("TRUNCATE role_capability_mapping_events"))
        connection.execute(text("DELETE FROM role_capability_mappings WHERE protected = false"))
        connection.execute(text("DELETE FROM external_identities WHERE linked_by_account_id IS NOT NULL"))

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


# ===========================================================================
# Fixture data factories
# ===========================================================================

def make_sample_migration_view(
    *,
    balances: bool = True,
    empty: bool = False,
    candidate_count: int = 1,
    candidates_truncated: bool = False,
) -> IdentityMigrationView:
    instant = Instant(iso_utc="2026-08-20T12:00:00Z", display="2026-08-20 12:00 UTC")
    run = MigrationRun(
        run_id=UUID("11111111-1111-1111-1111-111111111111"),
        produced_at=instant,
        source_snapshot="snapshot-2026-08-20.csv",
        dry_run=True,
        profile_version="1.0.0",
    )

    totals = MigrationTotals(
        source_characters=10 if balances else 12,
        source_players=8,
        proposed=4,
        ambiguous=1,
        unresolved=1,
        confirmed=2,
        confirmed_revoked=1,
        rejected=1,
        already_linked=4,
        outstanding=2,
    )

    if empty:
        return IdentityMigrationView(
            state="empty",
            run=run,
            proposals=(),
            cursor=Cursor(token="cur-0", has_more=False),
            totals=totals,
            csrf_token="csrf-mig-token",
        )

    char1 = CouncilCharacterRow(
        character_id=UUID("22222222-2222-2222-2222-222222222222"),
        display_name=SafeText(value="Theron Vance"),
        level=5,
        active=True,
        active_owner=Actor(
            account_id=UUID("33333333-3333-3333-3333-333333333333"),
            label=SafeText(value="AdminUser"),
            capability=ActorCapability.PLATFORM_ADMINISTRATOR,
        ),
        active_link_count=1,
        unresolved_owner=False,
        links_path="/v1/council/characters/22222222-2222-2222-2222-222222222222/links",
    )

    p1 = LinkProposal(
        proposal_id=UUID("44444444-4444-4444-4444-444444444441"),
        character=char1,
        character_version=1,
        sheet_player_name=SafeText(value="Alice"),
        sheet_discord_name=SafeText(value="alice_discord"),
        active_dm_flag=True,
        proposed_subject="123456789012345678",
        resolution="proposed",
        candidate_subjects=("123456789012345678",) if candidate_count > 0 else (),
        candidate_subjects_truncated=candidates_truncated,
        candidate_count=candidate_count,
        resulting_access_kind="co_owner",
        confirmable=True,
        decided=False,
        link_state=None,
    )

    p2 = LinkProposal(
        proposal_id=UUID("44444444-4444-4444-4444-444444444442"),
        character=char1,
        character_version=1,
        sheet_player_name=SafeText(value="Bob"),
        sheet_discord_name=SafeText(value="bob_discord"),
        active_dm_flag=False,
        proposed_subject=None,
        resolution="ambiguous",
        candidate_subjects=("222222222222222222", "333333333333333333"),
        candidate_subjects_truncated=False,
        candidate_count=2,
        resulting_access_kind="co_owner",
        confirmable=False,
        decided=False,
        link_state=None,
    )

    p3 = LinkProposal(
        proposal_id=UUID("44444444-4444-4444-4444-444444444443"),
        character=char1,
        character_version=1,
        sheet_player_name=SafeText(value="Charlie"),
        sheet_discord_name=None,
        active_dm_flag=False,
        proposed_subject="444444444444444444",
        resolution="confirmed",
        candidate_subjects=("444444444444444444",),
        candidate_subjects_truncated=False,
        candidate_count=1,
        resulting_access_kind="co_owner",
        confirmable=True,
        decided=True,
        link_state="active",
    )

    p4 = LinkProposal(
        proposal_id=UUID("44444444-4444-4444-4444-444444444444"),
        character=char1,
        character_version=1,
        sheet_player_name=SafeText(value="Dave"),
        sheet_discord_name=None,
        active_dm_flag=False,
        proposed_subject="555555555555555555",
        resolution="confirmed",
        candidate_subjects=("555555555555555555",),
        candidate_subjects_truncated=False,
        candidate_count=1,
        resulting_access_kind="co_owner",
        confirmable=True,
        decided=True,
        link_state="revoked",
    )

    p5 = LinkProposal(
        proposal_id=UUID("44444444-4444-4444-4444-444444444445"),
        character=char1,
        character_version=1,
        sheet_player_name=SafeText(value="Eve"),
        sheet_discord_name=None,
        active_dm_flag=False,
        proposed_subject=None,
        resolution="rejected",
        candidate_subjects=(),
        candidate_subjects_truncated=False,
        candidate_count=0,
        resulting_access_kind="co_owner",
        confirmable=False,
        decided=True,
        link_state=None,
    )

    return IdentityMigrationView(
        state="ready",
        run=run,
        proposals=(p1, p2, p3, p4, p5),
        cursor=Cursor(token="cursor-token-mig-next", has_more=True),
        totals=totals,
        csrf_token="csrf-mig-token",
    )


def make_sample_field_profile_view() -> FieldProfileView:
    fields = (
        ProfileFieldRow(
            field_key="attributes.level",
            authority="database_authority",
            difference_direction=None,
            owning_package=None,
        ),
        ProfileFieldRow(
            field_key="inventory.items",
            authority="legacy_authority_deferred",
            difference_direction="foundry_stale",
            owning_package="inventory_pkg_v1",
        ),
    )
    paths = (
        ProfilePathRow(
            path="system.attributes",
            snapshot_mode="reported",
            reports_field="attributes.level",
        ),
        ProfilePathRow(
            path="system.flags",
            snapshot_mode="snapshot-only",
            reports_field=None,
        ),
    )
    return FieldProfileView(
        state="ready",
        profile_version="1.0.4",
        paths=paths,
        fields=fields,
    )


def make_sample_role_capability_view(
    *, scope: str = "full", empty: bool = False
) -> RoleCapabilityView:
    instant = Instant(iso_utc="2026-08-20T12:00:00Z", display="2026-08-20 12:00 UTC")
    admin_actor = Actor(
        account_id=UUID("55555555-5555-5555-5555-555555555555"),
        label=SafeText(value="AdminUser"),
        capability=ActorCapability.PLATFORM_ADMINISTRATOR,
    )

    if empty:
        return RoleCapabilityView(
            state="empty",
            guild_id="1052698198180892733",
            administrator_scope="full",
            mappings=(),
            available_capabilities=(
                ActorCapability.PLATFORM_ADMINISTRATOR,
                ActorCapability.GUILD_COUNCIL,
            ),
            csrf_token="csrf-role-token",
            unratified_count=0,
        )

    m1 = RoleMappingRow(
        mapping_id=UUID("66666666-6666-6666-6666-666666666661"),
        role_snowflake="1124405581298552933",
        capability=ActorCapability.PLATFORM_ADMINISTRATOR,
        protected=True,
        provenance="ordinary",
        revocable=False,
        ratifiable=False,
        created_by=admin_actor,
        created_under_auth_method="discord_oauth",
        created_at=instant,
        version=1,
        role_label=SafeText(value="Bootstrap Admin Role"),
    )

    m2 = RoleMappingRow(
        mapping_id=UUID("66666666-6666-6666-6666-666666666662"),
        role_snowflake="223456789012345678",
        capability=ActorCapability.GUILD_COUNCIL,
        protected=False,
        provenance="ordinary",
        revocable=True,
        ratifiable=False,
        created_by=admin_actor,
        created_under_auth_method="discord_oauth",
        created_at=instant,
        version=2,
        role_label=SafeText(value="Council Officer"),
    )

    m3 = RoleMappingRow(
        mapping_id=UUID("66666666-6666-6666-6666-666666666663"),
        role_snowflake="333456789012345678",
        capability=ActorCapability.PLATFORM_ADMINISTRATOR,
        protected=False,
        provenance="emergency_continuity",
        revocable=True,
        ratifiable=True if scope == "full" else False,
        created_by=admin_actor,
        created_under_auth_method="webauthn",
        created_at=instant,
        version=1,
        role_label=SafeText(value="Break-Glass Temp Admin"),
    )

    return RoleCapabilityView(
        state="ready",
        guild_id="1052698198180892733",
        administrator_scope="full" if scope == "full" else "emergency_continuity",
        mappings=(m1, m2, m3),
        available_capabilities=(
            (ActorCapability.PLATFORM_ADMINISTRATOR, ActorCapability.GUILD_COUNCIL)
            if scope == "full"
            else (ActorCapability.PLATFORM_ADMINISTRATOR,)
        ),
        csrf_token="csrf-role-token",
        unratified_count=1,
        scope_notice_code="emergency_continuity_allowlist" if scope != "full" else None,
    )


def make_sample_account_identities_view(
    *,
    unlink_blocked: str | None = None,
    state: str = "ready",
) -> AccountIdentitiesView:
    instant = Instant(iso_utc="2026-08-20T12:00:00Z", display="2026-08-20 12:00 UTC")
    id1 = LinkedIdentity(
        identity_id=UUID("77777777-7777-7777-7777-777777777771"),
        provider_key="discord",
        provider_display_name="Discord",
        subject_display="123456789012345678",
        linked_at=instant,
        state="active",
        is_current_session_identity=True,
        last_authenticated_at=instant,
    )
    id2 = LinkedIdentity(
        identity_id=UUID("77777777-7777-7777-7777-777777777772"),
        provider_key="discord",
        provider_display_name="Discord",
        subject_display="999888777666555444",
        linked_at=instant,
        state="retired",
        is_current_session_identity=False,
        last_authenticated_at=None,
    )
    return AccountIdentitiesView(
        state=state,  # type: ignore[arg-type]
        account_id=UUID("88888888-8888-8888-8888-888888888888"),
        identities=(id1, id2),
        additional_provider="no_additional_provider",
        unlink_blocked_reason=unlink_blocked,  # type: ignore[arg-type]
        csrf_token="csrf-account-token",
    )


# ===========================================================================
# 1. Direct Jinja Rendering Tests (VM-10 to VM-13)
# ===========================================================================

def test_render_identity_migration_ready_state() -> None:
    """VM-10 / R-28: Renders run metadata, control totals, balance status, proposals, and forms."""
    env = get_jinja_env()
    vm = make_sample_migration_view()
    rendered = env.get_template("identity_migration.html").render(view=vm, request=make_request())

    assert 'data-run-id="11111111-1111-1111-1111-111111111111"' in rendered
    assert 'data-dry-run="true"' in rendered
    assert 'data-balances="true"' in rendered
    assert 'data-total="source_characters">10' in rendered
    assert 'data-total="confirmed">2' in rendered
    assert 'data-total="confirmed_revoked">1' in rendered
    assert 'data-total="already_linked">4' in rendered

    # Proposals checks
    assert 'data-proposal-id="44444444-4444-4444-4444-444444444441"' in rendered
    assert 'data-resolution="proposed"' in rendered
    assert 'data-confirmable="true"' in rendered
    assert 'data-stage="outstanding"' in rendered
    assert 'Player: Alice' in rendered
    assert 'Sheet Discord: alice_discord' in rendered
    assert 'Active DM: true' in rendered
    assert 'data-field="subject">123456789012345678</code>' in rendered

    # R-29 confirm form
    assert 'action="/v1/council/identity-migration/44444444-4444-4444-4444-444444444441/confirm"' in rendered
    assert 'name="version" value="1"' in rendered
    assert 'name="reason"' in rendered
    assert 'data-field="confirm-access-kind">co_owner' in rendered

    # R-30 reject form
    assert 'action="/v1/council/identity-migration/44444444-4444-4444-4444-444444444441/reject"' in rendered

    # Pagination
    assert 'href="/v1/council/identity-migration?cursor=cursor-token-mig-next"' in rendered


def test_render_identity_migration_decision_states() -> None:
    """VM-10: Verifies 4 decision states including confirmed-active vs confirmed-revoked."""
    env = get_jinja_env()
    vm = make_sample_migration_view()
    rendered = env.get_template("identity_migration.html").render(view=vm, request=make_request())

    # Confirmed and active (p3)
    assert 'data-status="confirmed-and-active"' in rendered
    assert 'data-link-state="active"' in rendered
    assert "Confirmed. This character's access row was created by the confirmation and is active now." in rendered

    # Confirmed and revoked (p4)
    assert 'data-status="confirmed-and-revoked"' in rendered
    assert 'data-link-state="revoked"' in rendered
    assert "Confirmed, and the access row this confirmation created has since been revoked." in rendered

    # Rejected (p5)
    assert 'data-status="rejected"' in rendered
    assert "Rejected. Nothing was created for this proposal." in rendered

    # Outstanding (p1, p2)
    assert 'data-status="outstanding"' in rendered


def test_render_identity_migration_candidate_truncation() -> None:
    """VM-10: Truncated candidates notice is rendered with reported bounds."""
    env = get_jinja_env()
    vm = make_sample_migration_view(candidate_count=15, candidates_truncated=True)
    rendered = env.get_template("identity_migration.html").render(view=vm, request=make_request())

    assert 'data-candidates-truncated="true"' in rendered
    assert 'data-candidate-count="15"' in rendered
    assert 'data-notice="candidates-truncated"' in rendered
    assert "Showing 1 of 15 recorded candidates" in rendered


def test_render_identity_migration_unbalanced_totals() -> None:
    """VM-10: Unbalanced totals reflect in data-balances attribute."""
    env = get_jinja_env()
    vm = make_sample_migration_view(balances=False)
    rendered = env.get_template("identity_migration.html").render(view=vm, request=make_request())

    assert 'data-balances="false"' in rendered
    assert "Reconciliation Discrepancy" in rendered


def test_render_identity_migration_empty_state() -> None:
    """VM-10: Empty proposal state renders cleanly."""
    env = get_jinja_env()
    vm = make_sample_migration_view(empty=True)
    rendered = env.get_template("identity_migration.html").render(view=vm, request=make_request())

    assert 'data-state="empty"' in rendered
    assert "No Proposals" in rendered


def test_render_identity_migration_forms_omitted_when_decided() -> None:
    """VM-10: Neither confirm nor reject forms appear on decided proposals."""
    env = get_jinja_env()
    vm = make_sample_migration_view()
    rendered = env.get_template("identity_migration.html").render(view=vm, request=make_request())

    # Proposals 3, 4, 5 are decided — must not have forms
    assert 'action="/v1/council/identity-migration/44444444-4444-4444-4444-444444444443/confirm"' not in rendered
    assert 'action="/v1/council/identity-migration/44444444-4444-4444-4444-444444444443/reject"' not in rendered
    assert 'action="/v1/council/identity-migration/44444444-4444-4444-4444-444444444444/confirm"' not in rendered
    assert 'action="/v1/council/identity-migration/44444444-4444-4444-4444-444444444445/confirm"' not in rendered


def test_render_identity_migration_confirm_form_omitted_when_not_confirmable() -> None:
    """VM-10: Ambiguous outstanding proposal has reject form but NOT confirm form."""
    env = get_jinja_env()
    vm = make_sample_migration_view()
    rendered = env.get_template("identity_migration.html").render(view=vm, request=make_request())

    # Proposal 2 is ambiguous/not confirmable
    assert 'action="/v1/council/identity-migration/44444444-4444-4444-4444-444444444442/confirm"' not in rendered
    assert 'action="/v1/council/identity-migration/44444444-4444-4444-4444-444444444442/reject"' in rendered


def test_render_field_profile_structure() -> None:
    """VM-11 / R-31: Renders profile version, unknown path policy, fields and paths."""
    env = get_jinja_env()
    vm = make_sample_field_profile_view()
    rendered = env.get_template("field_profile.html").render(view=vm, request=make_request("/v1/council/field-profile"))

    assert "Field profile 1.0.4" in rendered
    assert 'data-policy="reported_never_writable"' in rendered
    assert 'data-field-key="attributes.level"' in rendered
    assert 'data-authority="database_authority"' in rendered
    assert 'data-field-key="inventory.items"' in rendered
    assert 'data-authority="legacy_authority_deferred"' in rendered
    assert 'data-owning-package="inventory_pkg_v1"' in rendered
    assert 'data-path="system.attributes"' in rendered
    assert 'data-mode="reported"' in rendered
    assert 'data-path="system.flags"' in rendered
    assert 'data-mode="snapshot-only"' in rendered


def test_render_field_profile_no_forms() -> None:
    """VM-11: Proves strictly that field_profile.html contains zero forms and zero inputs."""
    env = get_jinja_env()
    vm = make_sample_field_profile_view()
    rendered = env.get_template("field_profile.html").render(view=vm, request=make_request("/v1/council/field-profile"))

    assert "<form" not in rendered
    assert "<input" not in rendered
    assert "<button" not in rendered
    assert "<select" not in rendered
    assert "<textarea" not in rendered


def test_render_role_capabilities_full_admin() -> None:
    """VM-12 / R-32: Renders full admin scope, role mappings, create/revoke/ratify forms."""
    env = get_jinja_env()
    vm = make_sample_role_capability_view(scope="full")
    rendered = env.get_template("role_capabilities.html").render(view=vm, request=make_request("/v1/admin/role-capabilities"))

    assert 'data-scope="full"' in rendered
    assert 'data-unratified="1"' in rendered
    assert 'data-notice="protected_bootstrap_mapping"' in rendered
    assert 'Unratified mappings: 1' in rendered

    # Protected bootstrap mapping (m1) — no revoke form
    assert 'data-mapping-id="66666666-6666-6666-6666-666666666661"' in rendered
    assert 'data-protected="true"' in rendered
    assert 'data-revocable="false"' in rendered
    assert 'action="/v1/admin/role-capabilities/66666666-6666-6666-6666-666666666661/revoke"' not in rendered

    # Ordinary revocable mapping (m2) — revoke form present, ratify absent
    assert 'data-mapping-id="66666666-6666-6666-6666-666666666662"' in rendered
    assert 'action="/v1/admin/role-capabilities/66666666-6666-6666-6666-666666666662/revoke"' in rendered
    assert 'action="/v1/admin/role-capabilities/66666666-6666-6666-6666-666666666662/ratify"' not in rendered

    # Emergency ratifiable mapping (m3) — ratify form present
    assert 'data-mapping-id="66666666-6666-6666-6666-666666666663"' in rendered
    assert 'action="/v1/admin/role-capabilities/66666666-6666-6666-6666-666666666663/ratify"' in rendered

    # Create mapping form (R-33)
    assert 'action="/v1/admin/role-capabilities"' in rendered
    assert 'name="role_id"' in rendered
    assert 'name="capability"' in rendered
    assert 'value="platform_administrator"' in rendered
    assert 'value="guild_council"' in rendered


def test_render_role_capabilities_emergency_continuity() -> None:
    """VM-12: Emergency continuity restricts capabilities and omits ratification forms."""
    env = get_jinja_env()
    vm = make_sample_role_capability_view(scope="emergency_continuity")
    rendered = env.get_template("role_capabilities.html").render(view=vm, request=make_request("/v1/admin/role-capabilities"))

    assert 'data-scope="emergency_continuity"' in rendered
    assert 'data-scope-notice="emergency_continuity_allowlist"' in rendered
    assert "authority is emergency-derived" in rendered

    # In emergency continuity, ratify form is absent
    assert 'action="/v1/admin/role-capabilities/66666666-6666-6666-6666-666666666663/ratify"' not in rendered

    # Capability select has only platform_administrator
    assert 'value="platform_administrator"' in rendered
    assert 'value="guild_council"' not in rendered


def test_render_account_identities_ready_state() -> None:
    """VM-13 / R-35: Renders account ID, identities list, active unlink form, and single provider note."""
    env = get_jinja_env()
    vm = make_sample_account_identities_view()
    rendered = env.get_template("account_identities.html").render(view=vm, request=make_request("/v1/account/identities"))

    assert "88888888-8888-8888-8888-888888888888" in rendered
    assert 'data-identity-id="77777777-7777-7777-7777-777777777771"' in rendered
    assert 'data-current="true"' in rendered
    assert "123456789012345678" in rendered
    assert "Current Session" in rendered

    # Active identity (id1) has unlink form
    assert 'action="/v1/account/identities/77777777-7777-7777-7777-777777777771/unlink"' in rendered

    # Retired identity (id2) has NO unlink form
    assert 'data-identity-id="77777777-7777-7777-7777-777777777772"' in rendered
    assert 'action="/v1/account/identities/77777777-7777-7777-7777-777777777772/unlink"' not in rendered

    # Single provider notice
    assert "Phase 3 has one sign-in provider" in rendered


def test_render_account_identities_unlink_blocked_reasons() -> None:
    """VM-13: Unlink forms are omitted when blocked by last_usable_identity or emergency_session."""
    env = get_jinja_env()

    # Case 1: last_usable_identity
    vm1 = make_sample_account_identities_view(unlink_blocked="last_usable_identity")
    rendered1 = env.get_template("account_identities.html").render(view=vm1, request=make_request("/v1/account/identities"))
    assert 'data-unlink-blocked="last_usable_identity"' in rendered1
    assert "Unlinking is blocked: this account has only one usable sign-in identity" in rendered1
    assert 'action="/v1/account/identities/77777777-7777-7777-7777-777777777771/unlink"' not in rendered1

    # Case 2: emergency_session
    vm2 = make_sample_account_identities_view(unlink_blocked="emergency_session")
    rendered2 = env.get_template("account_identities.html").render(view=vm2, request=make_request("/v1/account/identities"))
    assert 'data-unlink-blocked="emergency_session"' in rendered2
    assert "Unlinking is blocked: identity modifications are prohibited during an emergency continuity session" in rendered2
    assert 'action="/v1/account/identities/77777777-7777-7777-7777-777777777771/unlink"' not in rendered1


def test_render_account_identities_r36_denied_state() -> None:
    """VM-13 / R-36: Answers 200 HTML with state=denied and explains additional provider refusal."""
    env = get_jinja_env()
    vm = make_sample_account_identities_view(state="denied")
    rendered = env.get_template("account_identities.html").render(view=vm, request=make_request("/v1/account/identities/link/start"))

    assert 'data-state="denied"' in rendered
    assert "Linking an additional identity is unavailable or refused" in rendered


# ===========================================================================
# 2. XSS & Hostile Input Escaping Tests
# ===========================================================================

def assert_text_escaped_in_html(rendered_html: str, raw_payload: str, expected_escaped: str) -> None:
    """Helper asserting raw hostile string is strictly absent and properly escaped in HTML."""
    assert raw_payload not in rendered_html, f"Raw hostile payload {raw_payload!r} found unescaped in HTML"
    assert expected_escaped in rendered_html, f"Expected escaped entity {expected_escaped!r} missing from HTML"


def test_adversarial_escaping_on_step7_templates() -> None:
    """Proves HTML / script injection payloads are escaped in all dynamic text fields."""
    env = get_jinja_env()
    xss_payload = '<script>alert("pwned")</script>'
    xss_escaped = '&lt;script&gt;alert(&#34;pwned&#34;)&lt;/script&gt;'

    # 1. Identity migration
    char = CouncilCharacterRow(
        character_id=UUID("22222222-2222-2222-2222-222222222222"),
        display_name=SafeText(value=xss_payload),
        level=1,
        active=True,
        active_owner=None,
        active_link_count=0,
        unresolved_owner=True,
        links_path="/test",
    )
    p = LinkProposal(
        proposal_id=UUID("44444444-4444-4444-4444-444444444441"),
        character=char,
        character_version=1,
        sheet_player_name=SafeText(value=xss_payload),
        sheet_discord_name=SafeText(value=xss_payload),
        active_dm_flag=False,
        proposed_subject=xss_payload,
        resolution="proposed",
        candidate_subjects=(xss_payload,),
        candidate_subjects_truncated=False,
        candidate_count=1,
        resulting_access_kind="co_owner",
        confirmable=True,
        decided=False,
        link_state=None,
    )
    vm_mig = IdentityMigrationView(
        state="ready",
        run=None,
        proposals=(p,),
        cursor=Cursor(token="t", has_more=False),
        totals=MigrationTotals(0, 0, 0, 0, 0, 0, 0, 0, 0),
        csrf_token="tok",
    )
    rend_mig = env.get_template("identity_migration.html").render(view=vm_mig, request=make_request())
    assert_text_escaped_in_html(rend_mig, "<script>", "&lt;script&gt;")

    # 2. Field profile
    vm_prof = FieldProfileView(
        state="ready",
        profile_version=xss_payload,
        paths=(ProfilePathRow(path=xss_payload, snapshot_mode="reported"),),
        fields=(ProfileFieldRow(field_key=xss_payload, authority="legacy_authority_deferred", owning_package=xss_payload),),
    )
    rend_prof = env.get_template("field_profile.html").render(view=vm_prof, request=make_request())
    assert_text_escaped_in_html(rend_prof, "<script>", "&lt;script&gt;")

    # 3. Role capabilities
    actor = Actor(
        account_id=UUID("55555555-5555-5555-5555-555555555555"),
        label=SafeText(value=xss_payload),
        capability=ActorCapability.PLATFORM_ADMINISTRATOR,
    )
    mapping = RoleMappingRow(
        mapping_id=UUID("66666666-6666-6666-6666-666666666661"),
        role_snowflake=xss_payload,
        capability=ActorCapability.PLATFORM_ADMINISTRATOR,
        protected=False,
        provenance="ordinary",
        revocable=True,
        ratifiable=False,
        created_by=actor,
        created_under_auth_method="discord_oauth",
        created_at=Instant(iso_utc="2026-08-20T00:00:00Z", display="2026-08-20 00:00 UTC"),
        version=1,
        role_label=SafeText(value=xss_payload),
    )
    vm_role = RoleCapabilityView(
        state="ready",
        guild_id=xss_payload,
        administrator_scope="full",
        mappings=(mapping,),
        available_capabilities=(ActorCapability.PLATFORM_ADMINISTRATOR,),
        csrf_token="tok",
        unratified_count=0,
    )
    rend_role = env.get_template("role_capabilities.html").render(view=vm_role, request=make_request())
    assert_text_escaped_in_html(rend_role, "<script>", "&lt;script&gt;")

    # 4. Account identities
    id_entry = LinkedIdentity(
        identity_id=UUID("77777777-7777-7777-7777-777777777771"),
        provider_key="discord",
        provider_display_name=xss_payload,
        subject_display=xss_payload,
        linked_at=Instant(iso_utc="2026-08-20T00:00:00Z", display="2026-08-20 00:00 UTC"),
        state="active",
        is_current_session_identity=True,
    )
    vm_ident = AccountIdentitiesView(
        state="ready",
        account_id=UUID("88888888-8888-8888-8888-888888888888"),
        identities=(id_entry,),
        additional_provider="no_additional_provider",
        csrf_token="tok",
    )
    rend_ident = env.get_template("account_identities.html").render(view=vm_ident, request=make_request())
    assert_text_escaped_in_html(rend_ident, "<script>", "&lt;script&gt;")


def test_falsification_unescaped_xss_payload_fails() -> None:
    bad_rendered = '<div><script>alert("pwned")</script></div>'
    with pytest.raises(AssertionError, match=r"Raw hostile payload '<script>' found unescaped in HTML"):
        assert_text_escaped_in_html(bad_rendered, "<script>", "&lt;script&gt;")


# ===========================================================================
# 3. Form Validation & Structure Helpers
# ===========================================================================

def _extract_form_names_and_method(form_html: str) -> tuple[str, str, list[str]]:
    action_match = re.search(r'<form\b[^>]*\baction="([^"]+)"', form_html, re.IGNORECASE)
    assert action_match is not None, "Form action missing"
    action = action_match.group(1)

    method_match = re.search(r'<form\b[^>]*\bmethod="([^"]+)"', form_html, re.IGNORECASE)
    assert method_match is not None, "Form method missing"
    method = method_match.group(1).upper()

    inputs = re.findall(r'<input\b[^>]*\bname="([^"]+)"', form_html, re.IGNORECASE)
    textareas = re.findall(r'<textarea\b[^>]*\bname="([^"]+)"', form_html, re.IGNORECASE)
    selects = re.findall(r'<select\b[^>]*\bname="([^"]+)"', form_html, re.IGNORECASE)
    return action, method, inputs + textareas + selects


def validate_r29_confirm_form(form_html: str) -> None:
    action, method, names = _extract_form_names_and_method(form_html)
    assert re.match(r"^/v1/council/identity-migration/[a-f0-9\-]+/confirm$", action), f"R-29 action mismatch: {action}"
    assert method == "POST", f"R-29 method must be POST, got {method}"
    assert len(names) == len(set(names)) == 3, f"R-29 field names multiplicity mismatch: {names}"
    assert set(names) == {"csrf_token", "version", "reason"}, f"R-29 form fields mismatch: {names}"


def validate_r30_reject_form(form_html: str) -> None:
    action, method, names = _extract_form_names_and_method(form_html)
    assert re.match(r"^/v1/council/identity-migration/[a-f0-9\-]+/reject$", action), f"R-30 action mismatch: {action}"
    assert method == "POST", f"R-30 method must be POST, got {method}"
    assert len(names) == len(set(names)) == 2, f"R-30 field names multiplicity mismatch: {names}"
    assert set(names) == {"csrf_token", "reason"}, f"R-30 form fields mismatch: {names}"


def validate_r33_create_role_form(form_html: str) -> None:
    action, method, names = _extract_form_names_and_method(form_html)
    assert action == "/v1/admin/role-capabilities", f"R-33 action mismatch: {action}"
    assert method == "POST", f"R-33 method must be POST, got {method}"
    assert len(names) == len(set(names)) == 4, f"R-33 field names multiplicity mismatch: {names}"
    assert set(names) == {"csrf_token", "role_id", "capability", "reason"}, f"R-33 form fields mismatch: {names}"


def validate_r34_revoke_role_form(form_html: str) -> None:
    action, method, names = _extract_form_names_and_method(form_html)
    assert re.match(r"^/v1/admin/role-capabilities/[a-f0-9\-]+/revoke$", action), f"R-34 action mismatch: {action}"
    assert method == "POST", f"R-34 method must be POST, got {method}"
    assert len(names) == len(set(names)) == 3, f"R-34 field names multiplicity mismatch: {names}"
    assert set(names) == {"csrf_token", "version", "reason"}, f"R-34 form fields mismatch: {names}"


def validate_r38_ratify_role_form(form_html: str) -> None:
    action, method, names = _extract_form_names_and_method(form_html)
    assert re.match(r"^/v1/admin/role-capabilities/[a-f0-9\-]+/ratify$", action), f"R-38 action mismatch: {action}"
    assert method == "POST", f"R-38 method must be POST, got {method}"
    assert len(names) == len(set(names)) == 3, f"R-38 field names multiplicity mismatch: {names}"
    assert set(names) == {"csrf_token", "version", "reason"}, f"R-38 form fields mismatch: {names}"


def validate_r37_unlink_form(form_html: str) -> None:
    action, method, names = _extract_form_names_and_method(form_html)
    assert re.match(r"^/v1/account/identities/[a-f0-9\-]+/unlink$", action), f"R-37 action mismatch: {action}"
    assert method == "POST", f"R-37 method must be POST, got {method}"
    assert len(names) == len(set(names)) == 1, f"R-37 field names multiplicity mismatch: {names}"
    assert set(names) == {"csrf_token"}, f"R-37 form fields mismatch: {names}"


def test_form_field_exactness_validators() -> None:
    """Verifies all form field extractors pass on rendered production templates."""
    env = get_jinja_env()

    # R-29 and R-30
    vm_mig = make_sample_migration_view()
    rend_mig = env.get_template("identity_migration.html").render(view=vm_mig, request=make_request())
    confirm_form = re.search(r'(<form[^>]+action="/v1/council/identity-migration/[^/]+/confirm".*?</form>)', rend_mig, re.DOTALL)
    assert confirm_form is not None
    validate_r29_confirm_form(confirm_form.group(1))

    reject_form = re.search(r'(<form[^>]+action="/v1/council/identity-migration/[^/]+/reject".*?</form>)', rend_mig, re.DOTALL)
    assert reject_form is not None
    validate_r30_reject_form(reject_form.group(1))

    # R-33, R-34, R-38
    vm_role = make_sample_role_capability_view(scope="full")
    rend_role = env.get_template("role_capabilities.html").render(view=vm_role, request=make_request())
    create_form = re.search(r'(<form[^>]+action="/v1/admin/role-capabilities"[^>]*class="create-mapping-form".*?</form>)', rend_role, re.DOTALL)
    assert create_form is not None
    validate_r33_create_role_form(create_form.group(1))

    revoke_form = re.search(r'(<form[^>]+action="/v1/admin/role-capabilities/[^/]+/revoke".*?</form>)', rend_role, re.DOTALL)
    assert revoke_form is not None
    validate_r34_revoke_role_form(revoke_form.group(1))

    ratify_form = re.search(r'(<form[^>]+action="/v1/admin/role-capabilities/[^/]+/ratify".*?</form>)', rend_role, re.DOTALL)
    assert ratify_form is not None
    validate_r38_ratify_role_form(ratify_form.group(1))

    # R-37
    vm_ident = make_sample_account_identities_view()
    rend_ident = env.get_template("account_identities.html").render(view=vm_ident, request=make_request())
    unlink_form = re.search(r'(<form[^>]+action="/v1/account/identities/[^/]+/unlink".*?</form>)', rend_ident, re.DOTALL)
    assert unlink_form is not None
    validate_r37_unlink_form(unlink_form.group(1))


def test_falsification_r29_duplicate_field_fails() -> None:
    bad_form = '<form method="post" action="/v1/council/identity-migration/44444444-4444-4444-4444-444444444441/confirm"><input name="csrf_token"><input name="version"><input name="reason"><input name="version"></form>'
    with pytest.raises(AssertionError, match=r"multiplicity mismatch"):
        validate_r29_confirm_form(bad_form)


def test_falsification_r29_extra_field_fails() -> None:
    bad_form = '<form method="post" action="/v1/council/identity-migration/44444444-4444-4444-4444-444444444441/confirm"><input name="csrf_token"><input name="version"><input name="reason"><input name="candidate"></form>'
    with pytest.raises(AssertionError, match=r"R-29 field names multiplicity mismatch"):
        validate_r29_confirm_form(bad_form)


def test_falsification_r30_with_version_fails() -> None:
    bad_form = '<form method="post" action="/v1/council/identity-migration/44444444-4444-4444-4444-444444444441/reject"><input name="csrf_token"><input name="version"><input name="reason"></form>'
    with pytest.raises(AssertionError, match=r"R-30 field names multiplicity mismatch"):
        validate_r30_reject_form(bad_form)


def test_falsification_form_get_method_fails() -> None:
    bad_form = '<form method="get" action="/v1/council/identity-migration/44444444-4444-4444-4444-444444444441/confirm"><input name="csrf_token"><input name="version"><input name="reason"></form>'
    with pytest.raises(AssertionError, match=r"R-29 method must be POST, got GET"):
        validate_r29_confirm_form(bad_form)


def test_falsification_form_wrong_action_fails() -> None:
    bad_form = '<form method="post" action="/v1/wrong/confirm"><input name="csrf_token"><input name="version"><input name="reason"></form>'
    with pytest.raises(AssertionError, match=r"R-29 action mismatch"):
        validate_r29_confirm_form(bad_form)


# ===========================================================================
# 4. AST Structural Fixture & Falsification Tests
# ===========================================================================

def test_structural_step7_fixture_cleans_after_yield() -> None:
    validate_step7_cleanup_fixture(clean_between_step7_cases)


def test_falsification_structural_fixture_rejects_resolution_before_yield() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    engine = request.getfixturevalue("migrated_database")
    tracked_state = TrackedStep7FixtureState()
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
        validate_step7_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_resolution_outside_guard() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedStep7FixtureState()
    yield tracked_state
    engine = request.getfixturevalue("migrated_database")
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
    with pytest.raises(AssertionError, match=r"Database resolution must be guarded"):
        validate_step7_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_resolution_of_different_fixture_name() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedStep7FixtureState()
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
        validate_step7_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_missing_cleanup_after_yield() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedStep7FixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
"""
    with pytest.raises(AssertionError, match=r"Fixture must contain exactly two 'with engine.begin\(\) as \.\.\.' context managers"):
        validate_step7_cleanup_fixture(bad_fixture)


def test_falsification_structural_fixture_rejects_engine_passed_directly() -> None:
    bad_fixture = """
def bad_clean_fixture(request):
    tracked_state = TrackedStep7FixtureState()
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
    with pytest.raises(AssertionError, match=r"clean_p3_2_tables must receive bound connection"):
        validate_step7_cleanup_fixture(bad_fixture)


# ===========================================================================
# 5. Static Asset Integrity & Template Digests Tests
# ===========================================================================

def test_template_digests_match_implementation_corpus() -> None:
    """All 23 child and fragment templates match exact implementation SHA-256 digests."""
    found_templates = {
        p.name: compute_sha256(p)
        for p in TEMPLATE_ROOT.glob("*.html")
        if p.name != "base.html" and not p.name.startswith(".")
    }
    assert set(found_templates.keys()) == set(P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS.keys())
    for name, expected_sha in P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS.items():
        assert found_templates[name] == expected_sha, (
            f"Digest mismatch for '{name}': expected {expected_sha}, got {found_templates[name]}"
        )


def test_asset_integrity_manifest_verification() -> None:
    """asset-integrity.sha256 manifest is intact and valid."""
    assert MANIFEST_PATH.exists()
    lines = [
        line.strip()
        for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert len(lines) == 4
    for line in lines:
        parts = line.split()
        assert len(parts) == 2
        digest, rel_path = parts[0], parts[1]
        target_path = ROOT / rel_path
        assert target_path.is_file(), f"Asset '{rel_path}' missing"
        actual_sha = compute_sha256(target_path)
        assert actual_sha == digest, f"Digest mismatch on '{rel_path}': expected {digest}, got {actual_sha}"


def validate_step7_stylesheet_and_template_classes(css_text: str, template_texts: list[str]) -> None:
    """Strictly validates active CSS rules against template class tokens."""
    active_css = extract_active_css_classes(css_text)
    active_templates = extract_active_template_classes(template_texts)

    for sel in STEP_7_SELECTORS:
        assert sel in active_css, f"Active CSS rule '{sel}' missing from stylesheet rules"
        assert sel in active_templates, f"Active class token '{sel}' missing from Step 7 templates"

    for prohibited in PROHIBITED_STEP_7_SELECTORS:
        assert prohibited not in active_css, f"Prohibited selector '{prohibited}' found in stylesheet rules"


def test_step_7_selectors_used_and_prohibited_excluded() -> None:
    """Stylesheet contains all Step 7 selectors in active rules and zero prohibited Step 8+ selectors."""
    css_files = list((STATIC_ROOT / "css").glob("freedom-blades.*.css"))
    assert len(css_files) == 1
    css_text = css_files[0].read_text(encoding="utf-8")

    step7_templates = [
        (TEMPLATE_ROOT / "identity_migration.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "field_profile.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "role_capabilities.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "account_identities.html").read_text(encoding="utf-8"),
    ]
    validate_step7_stylesheet_and_template_classes(css_text, step7_templates)


def test_falsification_css_selector_only_in_comment_fails() -> None:
    css_with_comment_only = "/* .migration-run-card { color: red; } */\n.other { color: blue; }"
    with pytest.raises(AssertionError, match=r"Active CSS rule '\.migration-run-card' missing"):
        validate_step7_stylesheet_and_template_classes(css_with_comment_only, ["class='migration-run-card'"])


def test_falsification_css_selector_missing_from_templates_fails() -> None:
    css_files = list((STATIC_ROOT / "css").glob("freedom-blades.*.css"))
    css_text = css_files[0].read_text(encoding="utf-8")
    with pytest.raises(AssertionError, match=r"Active class token '.*' missing from Step 7 templates"):
        validate_step7_stylesheet_and_template_classes(css_text, ["<div class='nothing'></div>"])


def test_falsification_prohibited_selector_in_active_css_fails() -> None:
    css_files = list((STATIC_ROOT / "css").glob("freedom-blades.*.css"))
    bad_css = css_files[0].read_text(encoding="utf-8") + "\n.diff-box { display: flex; }"
    step7_templates = [
        (TEMPLATE_ROOT / "identity_migration.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "field_profile.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "role_capabilities.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "account_identities.html").read_text(encoding="utf-8"),
    ]
    with pytest.raises(AssertionError, match=r"Prohibited selector '\.diff-box' found"):
        validate_step7_stylesheet_and_template_classes(bad_css, step7_templates)


# ===========================================================================
# 6. Database Snapshot Helpers & Refusal Sequence AST Validation
# ===========================================================================

def snapshot_r29_state(connection: Any, proposal_id: UUID, character_id: UUID, target_account_id: UUID) -> tuple[str, int, int, int]:
    """Returns (proposal_resolution, character_version, matching_access_count, case_specific_audit_count)."""
    v = character_version(connection, character_id)
    resolution = connection.execute(
        text("SELECT resolution FROM identity_link_proposals WHERE id = :id"),
        {"id": proposal_id},
    ).scalar_one()
    access_count = connection.execute(
        text("SELECT count(*) FROM character_access WHERE character_id = :cid AND platform_account_id = :aid"),
        {"cid": character_id, "aid": target_account_id},
    ).scalar_one()
    audit_count = connection.execute(
        text("SELECT count(*) FROM audit_events WHERE action = 'identity_migration.confirmed' AND entity_type = 'identity_link_proposal' AND entity_id = :id"),
        {"id": str(proposal_id)},
    ).scalar_one()
    return (str(resolution), v, access_count, audit_count)


def snapshot_r30_state(connection: Any, proposal_id: UUID, character_id: UUID) -> tuple[str, int, int]:
    """Returns (proposal_resolution, character_version, case_specific_audit_count)."""
    v = character_version(connection, character_id)
    resolution = connection.execute(
        text("SELECT resolution FROM identity_link_proposals WHERE id = :id"),
        {"id": proposal_id},
    ).scalar_one()
    audit_count = connection.execute(
        text("SELECT count(*) FROM audit_events WHERE action = 'identity_migration.rejected' AND entity_type = 'identity_link_proposal' AND entity_id = :id"),
        {"id": str(proposal_id)},
    ).scalar_one()
    return (str(resolution), v, audit_count)


def snapshot_r33_state(connection: Any, guild_id: int, role_id: int, capability: str) -> tuple[int, int, int]:
    """Returns (active_mapping_count, applied_event_count, case_specific_audit_count)."""
    mapping_count = connection.execute(
        text("SELECT count(*) FROM role_capability_mappings WHERE guild_id = :gid AND role_id = :rid AND capability = :cap AND active = true"),
        {"gid": guild_id, "rid": role_id, "cap": capability},
    ).scalar_one()
    event_count = connection.execute(
        text("SELECT count(*) FROM role_capability_mapping_events WHERE guild_id = :gid AND role_id = :rid AND capability = :cap AND outcome = 'applied'"),
        {"gid": guild_id, "rid": role_id, "cap": capability},
    ).scalar_one()
    audit_count = connection.execute(
        text("SELECT count(*) FROM audit_events WHERE action = 'role_capability.mapped' AND entity_type = 'role_capability_mapping'"),
        {},
    ).scalar_one()
    return (int(mapping_count), int(event_count), int(audit_count))


def snapshot_r34_state(connection: Any, mapping_id: UUID) -> tuple[bool, int, int, int]:
    """Returns (mapping_active, mapping_version, applied_event_count, case_specific_audit_count)."""
    row = connection.execute(
        text("SELECT active, version FROM role_capability_mappings WHERE id = :id"),
        {"id": mapping_id},
    ).mappings().one()
    event_count = connection.execute(
        text("SELECT count(*) FROM role_capability_mapping_events WHERE mapping_id = :id AND operation = 'revoke' AND outcome = 'applied'"),
        {"id": mapping_id},
    ).scalar_one()
    audit_count = connection.execute(
        text("SELECT count(*) FROM audit_events WHERE action = 'role_capability.revoked' AND entity_type = 'role_capability_mapping' AND entity_id = :id"),
        {"id": str(mapping_id)},
    ).scalar_one()
    return (bool(row["active"]), int(row["version"]), int(event_count), int(audit_count))


def snapshot_r38_state(connection: Any, mapping_id: UUID) -> tuple[str, int, int, int]:
    """Returns (mapping_provenance, mapping_version, applied_event_count, case_specific_audit_count)."""
    row = connection.execute(
        text("SELECT provenance, version FROM role_capability_mappings WHERE id = :id"),
        {"id": mapping_id},
    ).mappings().one()
    event_count = connection.execute(
        text("SELECT count(*) FROM role_capability_mapping_events WHERE mapping_id = :id AND operation = 'ratify' AND outcome = 'applied'"),
        {"id": mapping_id},
    ).scalar_one()
    audit_count = connection.execute(
        text("SELECT count(*) FROM audit_events WHERE action = 'role_capability.ratified' AND entity_type = 'role_capability_mapping' AND entity_id = :id"),
        {"id": str(mapping_id)},
    ).scalar_one()
    return (str(row["provenance"]), int(row["version"]), int(event_count), int(audit_count))


def snapshot_r37_state(connection: Any, identity_id: UUID) -> tuple[str, int]:
    """Returns (identity_state, case_specific_applied_audit_count)."""
    row = connection.execute(
        text("SELECT state FROM external_identities WHERE id = :id"),
        {"id": identity_id},
    ).mappings().one()
    audit_count = connection.execute(
        text("SELECT count(*) FROM audit_events WHERE action = 'identity.unlinked' AND entity_type = 'external_identity' AND entity_id = :id"),
        {"id": str(identity_id)},
    ).scalar_one()
    return (str(row["state"]), int(audit_count))


def validate_step7_refusal_snapshots_and_sequences(src_or_func: Any) -> None:
    """Verifies that all Step 7 refusal cases execute exact before/after snapshot data flow."""
    if isinstance(src_or_func, str):
        src = src_or_func
    else:
        src = inspect.getsource(src_or_func)
    tree = ast.parse(src)

    func_defs = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    # 1. Validate snapshot_r29_state AST
    assert "snapshot_r29_state" in func_defs, "snapshot_r29_state definition missing"
    f29 = func_defs["snapshot_r29_state"]
    assert [a.arg for a in f29.args.args] == ["connection", "proposal_id", "character_id", "target_account_id"], "snapshot_r29_state args mismatch"

    v29_assign = None
    for n in f29.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            if isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == "character_version":
                v29_assign = n.targets[0].id
                break
    assert v29_assign is not None, "snapshot_r29_state missing character_version"

    audit29_assign = None
    for n in f29.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            if isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "scalar_one":
                inner = n.value.func.value
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) and inner.func.attr == "execute":
                    if inner.args and isinstance(inner.args[0], ast.Call) and getattr(inner.args[0].func, "id", None) == "text":
                        sql_text = inner.args[0].args[0].value if inner.args[0].args and isinstance(inner.args[0].args[0], ast.Constant) else ""
                        norm_sql = " ".join(sql_text.strip().lower().split())
                        if "from audit_events" in norm_sql:
                            assert "action = 'identity_migration.confirmed'" in norm_sql, "snapshot_r29_state must require action 'identity_migration.confirmed'"
                            assert "entity_type = 'identity_link_proposal'" in norm_sql, "snapshot_r29_state must require entity_type 'identity_link_proposal'"
                            audit29_assign = n.targets[0].id

    assert audit29_assign is not None, "snapshot_r29_state missing audit_events query"

    # 2. Validate snapshot_r30_state AST
    assert "snapshot_r30_state" in func_defs, "snapshot_r30_state definition missing"
    f30 = func_defs["snapshot_r30_state"]
    assert [a.arg for a in f30.args.args] == ["connection", "proposal_id", "character_id"], "snapshot_r30_state args mismatch"

    audit30_assign = None
    for n in f30.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            if isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "scalar_one":
                inner = n.value.func.value
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) and inner.func.attr == "execute":
                    if inner.args and isinstance(inner.args[0], ast.Call) and getattr(inner.args[0].func, "id", None) == "text":
                        sql_text = inner.args[0].args[0].value if inner.args[0].args and isinstance(inner.args[0].args[0], ast.Constant) else ""
                        norm_sql = " ".join(sql_text.strip().lower().split())
                        if "from audit_events" in norm_sql:
                            assert "action = 'identity_migration.rejected'" in norm_sql, "snapshot_r30_state must require action 'identity_migration.rejected'"
                            assert "entity_type = 'identity_link_proposal'" in norm_sql, "snapshot_r30_state must require entity_type 'identity_link_proposal'"
                            audit30_assign = n.targets[0].id

    assert audit30_assign is not None, "snapshot_r30_state missing audit_events query"

    # 3. Validate snapshot_r33_state AST
    assert "snapshot_r33_state" in func_defs, "snapshot_r33_state definition missing"
    f33 = func_defs["snapshot_r33_state"]
    assert [a.arg for a in f33.args.args] == ["connection", "guild_id", "role_id", "capability"], "snapshot_r33_state args mismatch"

    audit33_assign = None
    for n in f33.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            if isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "scalar_one":
                inner = n.value.func.value
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) and inner.func.attr == "execute":
                    if inner.args and isinstance(inner.args[0], ast.Call) and getattr(inner.args[0].func, "id", None) == "text":
                        sql_text = inner.args[0].args[0].value if inner.args[0].args and isinstance(inner.args[0].args[0], ast.Constant) else ""
                        norm_sql = " ".join(sql_text.strip().lower().split())
                        if "from audit_events" in norm_sql:
                            assert "action = 'role_capability.mapped'" in norm_sql, "snapshot_r33_state must require action 'role_capability.mapped'"
                            assert "entity_type = 'role_capability_mapping'" in norm_sql, "snapshot_r33_state must require entity_type 'role_capability_mapping'"
                            audit33_assign = n.targets[0].id

    assert audit33_assign is not None, "snapshot_r33_state missing audit_events query"

    # 4. Validate snapshot_r34_state AST
    assert "snapshot_r34_state" in func_defs, "snapshot_r34_state definition missing"
    f34 = func_defs["snapshot_r34_state"]
    assert [a.arg for a in f34.args.args] == ["connection", "mapping_id"], "snapshot_r34_state args mismatch"

    audit34_assign = None
    for n in f34.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            if isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "scalar_one":
                inner = n.value.func.value
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) and inner.func.attr == "execute":
                    if inner.args and isinstance(inner.args[0], ast.Call) and getattr(inner.args[0].func, "id", None) == "text":
                        sql_text = inner.args[0].args[0].value if inner.args[0].args and isinstance(inner.args[0].args[0], ast.Constant) else ""
                        norm_sql = " ".join(sql_text.strip().lower().split())
                        if "from audit_events" in norm_sql:
                            assert "action = 'role_capability.revoked'" in norm_sql, "snapshot_r34_state must require action 'role_capability.revoked'"
                            assert "entity_type = 'role_capability_mapping'" in norm_sql, "snapshot_r34_state must require entity_type 'role_capability_mapping'"
                            audit34_assign = n.targets[0].id

    assert audit34_assign is not None, "snapshot_r34_state missing audit_events query"

    # 5. Validate snapshot_r38_state AST
    assert "snapshot_r38_state" in func_defs, "snapshot_r38_state definition missing"
    f38 = func_defs["snapshot_r38_state"]
    assert [a.arg for a in f38.args.args] == ["connection", "mapping_id"], "snapshot_r38_state args mismatch"

    audit38_assign = None
    for n in f38.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            if isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "scalar_one":
                inner = n.value.func.value
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) and inner.func.attr == "execute":
                    if inner.args and isinstance(inner.args[0], ast.Call) and getattr(inner.args[0].func, "id", None) == "text":
                        sql_text = inner.args[0].args[0].value if inner.args[0].args and isinstance(inner.args[0].args[0], ast.Constant) else ""
                        norm_sql = " ".join(sql_text.strip().lower().split())
                        if "from audit_events" in norm_sql:
                            assert "action = 'role_capability.ratified'" in norm_sql, "snapshot_r38_state must require action 'role_capability.ratified'"
                            assert "entity_type = 'role_capability_mapping'" in norm_sql, "snapshot_r38_state must require entity_type 'role_capability_mapping'"
                            audit38_assign = n.targets[0].id

    assert audit38_assign is not None, "snapshot_r38_state missing audit_events query"

    # 6. Validate snapshot_r37_state AST
    assert "snapshot_r37_state" in func_defs, "snapshot_r37_state definition missing"
    f37 = func_defs["snapshot_r37_state"]
    assert [a.arg for a in f37.args.args] == ["connection", "identity_id"], "snapshot_r37_state args mismatch"

    audit37_assign = None
    for n in f37.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            if isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "scalar_one":
                inner = n.value.func.value
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) and inner.func.attr == "execute":
                    if inner.args and isinstance(inner.args[0], ast.Call) and getattr(inner.args[0].func, "id", None) == "text":
                        sql_text = inner.args[0].args[0].value if inner.args[0].args and isinstance(inner.args[0].args[0], ast.Constant) else ""
                        norm_sql = " ".join(sql_text.strip().lower().split())
                        if "from audit_events" in norm_sql:
                            assert "action = 'identity.unlinked'" in norm_sql, "snapshot_r37_state must require action 'identity.unlinked'"
                            assert "entity_type = 'external_identity'" in norm_sql, "snapshot_r37_state must require entity_type 'external_identity'"
                            audit37_assign = n.targets[0].id

    assert audit37_assign is not None, "snapshot_r37_state missing audit_events query"

    # 7. Validate refusal sequences inside test_database_backed_identity_and_role_views_and_mutations
    assert "test_database_backed_identity_and_role_views_and_mutations" in func_defs, "database test definition missing"
    db_func = func_defs["test_database_backed_identity_and_role_views_and_mutations"]

    expected_sequences: dict[str, dict[str, Any]] = {
        "r29_no_csrf": {
            "helper": "snapshot_r29_state",
            "expected_status": 403,
            "args": ("prop1_c_id", "c1_c", "target_acc"),
        },
        "r29_bad_csrf": {
            "helper": "snapshot_r29_state",
            "expected_status": 403,
            "args": ("prop1_c_id", "c1_c", "target_acc"),
        },
        "r29_bad_origin": {
            "helper": "snapshot_r29_state",
            "expected_status": 403,
            "args": ("prop1_c_id", "c1_c", "target_acc"),
        },
        "r29_stale": {
            "helper": "snapshot_r29_state",
            "expected_status": 409,
            "args": ("prop1_c_id", "c1_c", "target_acc"),
        },
        "r29_non_confirmable": {
            "helper": "snapshot_r29_state",
            "expected_status": 409,
            "args": ("prop2_c_id", "c2_c", "target_acc"),
        },
        "r30_no_csrf": {
            "helper": "snapshot_r30_state",
            "expected_status": 403,
            "args": ("prop2_c_id", "c2_c"),
        },
        "r30_bad_csrf": {
            "helper": "snapshot_r30_state",
            "expected_status": 403,
            "args": ("prop2_c_id", "c2_c"),
        },
        "r30_bad_origin": {
            "helper": "snapshot_r30_state",
            "expected_status": 403,
            "args": ("prop2_c_id", "c2_c"),
        },
        "r33_no_csrf": {
            "helper": "snapshot_r33_state",
            "expected_status": 403,
            "args": ("settings.discord.guild_id", "800000000000000401", "'guild_council'"),
        },
        "r33_bad_csrf": {
            "helper": "snapshot_r33_state",
            "expected_status": 403,
            "args": ("settings.discord.guild_id", "800000000000000401", "'guild_council'"),
        },
        "r33_bad_origin": {
            "helper": "snapshot_r33_state",
            "expected_status": 403,
            "args": ("settings.discord.guild_id", "800000000000000401", "'guild_council'"),
        },
        "r33_ac_denied": {
            "helper": "snapshot_r33_state",
            "expected_status": 403,
            "args": ("settings.discord.guild_id", "800000000000000401", "'guild_council'"),
        },
        "r34_no_csrf": {
            "helper": "snapshot_r34_state",
            "expected_status": 403,
            "args": ("map_ord_a_id",),
        },
        "r34_bad_csrf": {
            "helper": "snapshot_r34_state",
            "expected_status": 403,
            "args": ("map_ord_a_id",),
        },
        "r34_bad_origin": {
            "helper": "snapshot_r34_state",
            "expected_status": 403,
            "args": ("map_ord_a_id",),
        },
        "r34_stale": {
            "helper": "snapshot_r34_state",
            "expected_status": 409,
            "args": ("map_ord_a_id",),
        },
        "r34_protected": {
            "helper": "snapshot_r34_state",
            "expected_status": 403,
            "args": ("map_boot_id",),
        },
        "r38_no_csrf": {
            "helper": "snapshot_r38_state",
            "expected_status": 403,
            "args": ("map_emerg_bg_id",),
        },
        "r38_bad_csrf": {
            "helper": "snapshot_r38_state",
            "expected_status": 403,
            "args": ("map_emerg_bg_id",),
        },
        "r38_bad_origin": {
            "helper": "snapshot_r38_state",
            "expected_status": 403,
            "args": ("map_emerg_bg_id",),
        },
        "r38_stale": {
            "helper": "snapshot_r38_state",
            "expected_status": 409,
            "args": ("map_emerg_bg_id",),
        },
        "r38_ac_refused": {
            "helper": "snapshot_r38_state",
            "expected_status": 403,
            "args": ("map_emerg_bg_id",),
        },
        "r37_no_csrf": {
            "helper": "snapshot_r37_state",
            "expected_status": 403,
            "args": ("m_extra_id",),
        },
        "r37_bad_csrf": {
            "helper": "snapshot_r37_state",
            "expected_status": 403,
            "args": ("m_extra_id",),
        },
        "r37_bad_origin": {
            "helper": "snapshot_r37_state",
            "expected_status": 403,
            "args": ("m_extra_id",),
        },
        "r37_emergency_session": {
            "helper": "snapshot_r37_state",
            "expected_status": 403,
            "args": ("bg_id",),
        },
        "r37_already_retired": {
            "helper": "snapshot_r37_state",
            "expected_status": 409,
            "args": ("m_retired_id",),
        },
    }

    for case_prefix, spec in expected_sequences.items():
        before_var = f"{case_prefix}_snap_before"
        after_var = f"{case_prefix}_snap_after"
        res_var = f"res_{case_prefix}"

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

        assert len(db_func.body) > before_stmt_idx + 3, f"Missing after snapshot with-block for '{case_prefix}'"
        after_with_block = db_func.body[before_stmt_idx + 3]
        assert isinstance(after_with_block, ast.With), f"Intervening statement detected between status assertion and after snapshot for '{case_prefix}'"

        after_conn_name = after_with_block.items[0].optional_vars.id
        assert before_conn_name != after_conn_name, f"Case '{case_prefix}' must use distinct before/after connection variables"

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


def _replace_in_function(src: str, func_name: str, old: str, new: str) -> str:
    pattern = rf"(def {func_name}\b.*?)(?=\ndef |\Z)"
    match = re.search(pattern, src, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Function {func_name} not found in source")
    func_code = match.group(1)
    if old not in func_code:
        raise ValueError(f"Pattern {old!r} not found in function {func_name}")
    modified_func_code = func_code.replace(old, new, 1)
    return src[:match.start(1)] + modified_func_code + src[match.end(1):]


def test_structural_refusal_snapshots_and_sequences_present() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    validate_step7_refusal_snapshots_and_sequences(src)


def test_falsification_snapshot_r29_missing_action_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _replace_in_function(
        src,
        "snapshot_r29_state",
        "action = 'identity_migration.confirmed'",
        "action = 'identity_migration.rejected'",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r29_state must require action 'identity_migration.confirmed'"):
        validate_step7_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r29_wrong_entity_type_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _replace_in_function(
        src,
        "snapshot_r29_state",
        "entity_type = 'identity_link_proposal'",
        "entity_type = 'identity_link_proposals'",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r29_state must require entity_type 'identity_link_proposal'"):
        validate_step7_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r30_missing_action_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _replace_in_function(
        src,
        "snapshot_r30_state",
        "action = 'identity_migration.rejected'",
        "action = 'identity_migration.confirmed'",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r30_state must require action 'identity_migration.rejected'"):
        validate_step7_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r30_wrong_entity_type_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _replace_in_function(
        src,
        "snapshot_r30_state",
        "entity_type = 'identity_link_proposal'",
        "entity_type = 'identity_link_proposals'",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r30_state must require entity_type 'identity_link_proposal'"):
        validate_step7_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r33_missing_action_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _replace_in_function(
        src,
        "snapshot_r33_state",
        "action = 'role_capability.mapped'",
        "action = 'role_capability.revoked'",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r33_state must require action 'role_capability.mapped'"):
        validate_step7_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r33_wrong_entity_type_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _replace_in_function(
        src,
        "snapshot_r33_state",
        "entity_type = 'role_capability_mapping'",
        "entity_type = 'role_capability_mappings'",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r33_state must require entity_type 'role_capability_mapping'"):
        validate_step7_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r34_missing_action_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _replace_in_function(
        src,
        "snapshot_r34_state",
        "action = 'role_capability.revoked'",
        "action = 'role_capability.ratified'",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r34_state must require action 'role_capability.revoked'"):
        validate_step7_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r34_wrong_entity_type_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _replace_in_function(
        src,
        "snapshot_r34_state",
        "entity_type = 'role_capability_mapping'",
        "entity_type = 'role_capability_mappings'",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r34_state must require entity_type 'role_capability_mapping'"):
        validate_step7_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r38_missing_action_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _replace_in_function(
        src,
        "snapshot_r38_state",
        "action = 'role_capability.ratified'",
        "action = 'role_capability.revoked'",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r38_state must require action 'role_capability.ratified'"):
        validate_step7_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r38_wrong_entity_type_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _replace_in_function(
        src,
        "snapshot_r38_state",
        "entity_type = 'role_capability_mapping'",
        "entity_type = 'role_capability_mappings'",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r38_state must require entity_type 'role_capability_mapping'"):
        validate_step7_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r37_missing_action_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _replace_in_function(
        src,
        "snapshot_r37_state",
        "action = 'identity.unlinked'",
        "action = 'identity.linked'",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r37_state must require action 'identity.unlinked'"):
        validate_step7_refusal_snapshots_and_sequences(tampered)


def test_falsification_snapshot_r37_wrong_entity_type_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _replace_in_function(
        src,
        "snapshot_r37_state",
        "entity_type = 'external_identity'",
        "entity_type = 'external_identities'",
    )
    with pytest.raises(AssertionError, match=r"snapshot_r37_state must require entity_type 'external_identity'"):
        validate_step7_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_wrong_helper_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "r29_no_csrf_snap_before = snapshot_r29_state(conn_r29_no_csrf_b, prop1_c_id, c1_c, target_acc)",
        "r29_no_csrf_snap_before = snapshot_r30_state(conn_r29_no_csrf_b, prop1_c_id, c1_c)",
    )
    with pytest.raises(AssertionError, match=r"Before snapshot for 'r29_no_csrf' must call 'snapshot_r29_state'"):
        validate_step7_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_same_connection_before_after_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        _rreplace(
            src,
            "with migrated_database.begin() as conn_r29_no_csrf_a:",
            "with migrated_database.begin() as conn_r29_no_csrf_b:",
        ),
        "r29_no_csrf_snap_after = snapshot_r29_state(conn_r29_no_csrf_a, prop1_c_id, c1_c, target_acc)",
        "r29_no_csrf_snap_after = snapshot_r29_state(conn_r29_no_csrf_b, prop1_c_id, c1_c, target_acc)",
    )
    with pytest.raises(AssertionError, match=r"Case 'r29_no_csrf' must use distinct before/after connection variables"):
        validate_step7_refusal_snapshots_and_sequences(tampered)


def test_falsification_sequence_wrong_http_method_rejected() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    tampered = _rreplace(
        src,
        "res_r29_no_csrf = await client.post(",
        "res_r29_no_csrf = await client.get(",
    )
    with pytest.raises(AssertionError, match=r"Request for 'r29_no_csrf' must use HTTP POST method, got 'get'"):
        validate_step7_refusal_snapshots_and_sequences(tampered)


# ===========================================================================
# 7. Database-Backed HTTP Tests (R-28 through R-38)
# ===========================================================================

@pytest.mark.skipif(
    not os.environ.get("TEST_DATABASE_URL"),
    reason="TEST_DATABASE_URL is not configured for a disposable PostgreSQL database.",
)
@pytest.mark.database
async def test_database_backed_identity_and_role_views_and_mutations(
    client, settings, migrated_database, clean_between_step7_cases
) -> None:
    """Comprehensive executable test suite for R-28 through R-38 using disposable PostgreSQL."""
    tracked_state: TrackedStep7FixtureState = clean_between_step7_cases
    callers = seed_callers(migrated_database, settings)
    u = callers["U"]
    n = callers["N"]
    m = callers["M"]
    c = callers["C"]
    a = callers["A"]
    ca = callers["CA"]
    bg = callers["BG"]
    ac = callers["AC"]

    target_subj = 700000000000009222
    other_subj = 700000000000009555

    with migrated_database.begin() as connection:
        c1_c = make_character(connection, display_name="Theron Vance (C)", level=5)
        c1_ca = make_character(connection, display_name="Theron Vance (CA)", level=5)
        c2_c = make_character(connection, display_name="Lyra Dawnseeker (C)", level=3)
        c2_ca = make_character(connection, display_name="Lyra Dawnseeker (CA)", level=3)
        c3 = make_character(connection, display_name="Garrick Thorne", level=1)
        tracked_state.character_ids.add(c1_c)
        tracked_state.character_ids.add(c1_ca)
        tracked_state.character_ids.add(c2_c)
        tracked_state.character_ids.add(c2_ca)
        tracked_state.character_ids.add(c3)

        target_acc = make_account(connection, label="target-alice")
        seed_discord_member(connection, subject=target_subj, username="target_alice")
        link_discord(connection, target_acc, target_subj)

        other_acc = make_account(connection, label="other-user")
        seed_discord_member(connection, subject=other_subj, username="other_user")
        link_discord(connection, other_acc, other_subj)

        run_id = uuid4()
        connection.execute(
            insert(identity_migration_runs).values(
                id=run_id,
                dry_run=True,
                source_label="Characters!C + Players!A,B,D",
                profile_version="1.0.0",
                source_characters=5,
                source_players=4,
                already_linked=1,
                proposed=2,
                ambiguous=2,
                unresolved=0,
                correlation_id=uuid4(),
            )
        )

        link_c3 = grant_link(
            connection,
            character_id=c3,
            account_id=target_acc,
            granted_by=a.account_id,
            access_kind="owner",
        )
        tracked_state.access_ids.add(link_c3)

        prop1_c_id = uuid4()
        connection.execute(
            insert(identity_link_proposals).values(
                id=prop1_c_id,
                run_id=run_id,
                character_id=c1_c,
                sheet_player_name="Alice Player C",
                sheet_discord_name="alice_discord_c",
                active_dm=True,
                proposed_subject=str(target_subj),
                resolution="proposed",
                audit_correlation_id=uuid4(),
            )
        )
        connection.execute(
            insert(identity_link_proposal_candidates).values(
                id=uuid4(),
                proposal_id=prop1_c_id,
                subject=str(target_subj),
                observed_username="target_alice",
            )
        )

        prop1_ca_id = uuid4()
        connection.execute(
            insert(identity_link_proposals).values(
                id=prop1_ca_id,
                run_id=run_id,
                character_id=c1_ca,
                sheet_player_name="Alice Player CA",
                sheet_discord_name="alice_discord_ca",
                active_dm=True,
                proposed_subject=str(target_subj),
                resolution="proposed",
                audit_correlation_id=uuid4(),
            )
        )
        connection.execute(
            insert(identity_link_proposal_candidates).values(
                id=uuid4(),
                proposal_id=prop1_ca_id,
                subject=str(target_subj),
                observed_username="target_alice",
            )
        )

        prop2_c_id = uuid4()
        connection.execute(
            insert(identity_link_proposals).values(
                id=prop2_c_id,
                run_id=run_id,
                character_id=c2_c,
                sheet_player_name="Bob Player C",
                sheet_discord_name="bob_discord_c",
                active_dm=False,
                proposed_subject=None,
                resolution="ambiguous",
                audit_correlation_id=uuid4(),
            )
        )

        prop2_ca_id = uuid4()
        connection.execute(
            insert(identity_link_proposals).values(
                id=prop2_ca_id,
                run_id=run_id,
                character_id=c2_ca,
                sheet_player_name="Bob Player CA",
                sheet_discord_name="bob_discord_ca",
                active_dm=False,
                proposed_subject=None,
                resolution="ambiguous",
                audit_correlation_id=uuid4(),
            )
        )

        # Protected bootstrap mapping
        map_boot_id = connection.execute(
            text("SELECT id FROM role_capability_mappings WHERE protected = true")
        ).scalar_one()

        map_ord_a_id = uuid4()
        connection.execute(
            insert(role_capability_mappings).values(
                id=map_ord_a_id,
                guild_id=settings.discord.guild_id,
                role_id=800000000000000201,
                capability="guild_council",
                protected=False,
                active=True,
                created_by_account_id=a.account_id,
                created_under_auth_method="discord_oauth",
                created_under_scope="full",
                provenance="ordinary",
                reason="Ordinary council role A",
                audit_correlation_id=uuid4(),
                version=0,
            )
        )

        map_ord_ca_id = uuid4()
        connection.execute(
            insert(role_capability_mappings).values(
                id=map_ord_ca_id,
                guild_id=settings.discord.guild_id,
                role_id=800000000000000202,
                capability="guild_council",
                protected=False,
                active=True,
                created_by_account_id=ca.account_id,
                created_under_auth_method="discord_oauth",
                created_under_scope="full",
                provenance="ordinary",
                reason="Ordinary council role CA",
                audit_correlation_id=uuid4(),
                version=0,
            )
        )

        map_emerg_bg_id = uuid4()
        connection.execute(
            insert(role_capability_mappings).values(
                id=map_emerg_bg_id,
                guild_id=settings.discord.guild_id,
                role_id=800000000000000203,
                capability="platform_administrator",
                protected=False,
                active=True,
                created_by_account_id=ac.account_id,
                created_under_auth_method="webauthn",
                created_under_scope="emergency_continuity",
                provenance="emergency_continuity",
                reason="Emergency admin role BG",
                audit_correlation_id=uuid4(),
                version=0,
            )
        )

        map_emerg_ac_id = uuid4()
        connection.execute(
            insert(role_capability_mappings).values(
                id=map_emerg_ac_id,
                guild_id=settings.discord.guild_id,
                role_id=800000000000000204,
                capability="platform_administrator",
                protected=False,
                active=True,
                created_by_account_id=ac.account_id,
                created_under_auth_method="webauthn",
                created_under_scope="emergency_continuity",
                provenance="emergency_continuity",
                reason="Emergency admin role AC",
                audit_correlation_id=uuid4(),
                version=0,
            )
        )

        map_emerg_to_ratify_a_id = uuid4()
        connection.execute(
            insert(role_capability_mappings).values(
                id=map_emerg_to_ratify_a_id,
                guild_id=settings.discord.guild_id,
                role_id=800000000000000205,
                capability="platform_administrator",
                protected=False,
                active=True,
                created_by_account_id=ac.account_id,
                created_under_auth_method="webauthn",
                created_under_scope="emergency_continuity",
                provenance="emergency_continuity",
                reason="Emergency admin role to ratify A",
                audit_correlation_id=uuid4(),
                version=0,
            )
        )

        map_emerg_to_ratify_ca_id = uuid4()
        connection.execute(
            insert(role_capability_mappings).values(
                id=map_emerg_to_ratify_ca_id,
                guild_id=settings.discord.guild_id,
                role_id=800000000000000206,
                capability="platform_administrator",
                protected=False,
                active=True,
                created_by_account_id=ac.account_id,
                created_under_auth_method="webauthn",
                created_under_scope="emergency_continuity",
                provenance="emergency_continuity",
                reason="Emergency admin role to ratify CA",
                audit_correlation_id=uuid4(),
                version=0,
            )
        )

        # Primary identity for member M
        m_primary_id = connection.execute(
            text("SELECT id FROM external_identities WHERE platform_account_id = :aid AND state = 'active'"),
            {"aid": m.account_id},
        ).scalar_one()

        # Seed secondary active identities for N, M, C, A, CA so each can perform isolated R-37 unlinking
        def add_extra_identity(aid: UUID, subj_suffix: str) -> UUID:
            extra_id = uuid4()
            connection.execute(
                insert(external_identities).values(
                    id=extra_id,
                    platform_account_id=aid,
                    # A second reviewed-provider-shaped identity keeps the
                    # account unlinkable without making the one Discord
                    # subject used for current membership ambiguous.
                    provider_key="oidc:step7.test",
                    subject=f"700000000000009{subj_suffix}",
                    state="active",
                    linked_by_account_id=aid,
                    audit_correlation_id=uuid4(),
                )
            )
            return extra_id

        n_extra_id = add_extra_identity(n.account_id, "111")
        # Keep this distinct from `target_subj`, which already ends in `9222`.
        m_extra_id = add_extra_identity(m.account_id, "212")
        c_extra_id = add_extra_identity(c.account_id, "333")
        a_extra_id = add_extra_identity(a.account_id, "444")
        # Keep this distinct from `other_subj`, which already ends in `9555`.
        ca_extra_id = add_extra_identity(ca.account_id, "515")

        # Already retired identity for member M
        m_retired_id = uuid4()
        connection.execute(
            insert(external_identities).values(
                id=m_retired_id,
                platform_account_id=m.account_id,
                provider_key="discord",
                subject="700000000000009666",
                state="retired",
                retired_at=datetime.now(timezone.utc),
                retired_reason="previously unlinked",
                linked_by_account_id=m.account_id,
                audit_correlation_id=uuid4(),
            )
        )

        # BG deliberately has no provider identity. Use an existing identity as
        # the object probe so this case proves the emergency-session guard runs
        # before object ownership and leaves the row untouched.
        bg_id = m_extra_id
        ac_id = connection.execute(
            text("SELECT id FROM external_identities WHERE platform_account_id = :aid"),
            {"aid": ac.account_id},
        ).scalar_one()

        # Other account identity
        other_identity_id = connection.execute(
            text("SELECT id FROM external_identities WHERE platform_account_id = :aid"),
            {"aid": other_acc},
        ).scalar_one()

    # =========================================================================
    # R-28 Identity Migration Overview (GET) - All 8 Callers
    # =========================================================================
    assert (await client.get("/v1/council/identity-migration", cookies=u.cookies(settings))).status_code == 303
    assert (await client.get("/v1/council/identity-migration", cookies=n.cookies(settings))).status_code == 403
    assert (await client.get("/v1/council/identity-migration", cookies=m.cookies(settings))).status_code == 403
    
    res_r28_c = await client.get("/v1/council/identity-migration", cookies=c.cookies(settings))
    assert res_r28_c.status_code == 200
    assert "Theron Vance (C)" in res_r28_c.text
    
    assert (await client.get("/v1/council/identity-migration", cookies=a.cookies(settings))).status_code == 403
    
    res_r28_ca = await client.get("/v1/council/identity-migration", cookies=ca.cookies(settings))
    assert res_r28_ca.status_code == 200
    assert "Theron Vance (CA)" in res_r28_ca.text

    assert (await client.get("/v1/council/identity-migration", cookies=bg.cookies(settings))).status_code == 403
    assert (await client.get("/v1/council/identity-migration", cookies=ac.cookies(settings))).status_code == 403

    # =========================================================================
    # R-29 Confirm Proposal (POST) - Refusal Snapshots & All 8 Callers
    # =========================================================================
    # Refusal: No CSRF
    with migrated_database.begin() as conn_r29_no_csrf_b:
        r29_no_csrf_snap_before = snapshot_r29_state(conn_r29_no_csrf_b, prop1_c_id, c1_c, target_acc)
    res_r29_no_csrf = await client.post(
        f"/v1/council/identity-migration/{prop1_c_id}/confirm",
        cookies=c.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content="version=0&reason=Confirming+without+CSRF",
    )
    assert res_r29_no_csrf.status_code == 403
    with migrated_database.begin() as conn_r29_no_csrf_a:
        r29_no_csrf_snap_after = snapshot_r29_state(conn_r29_no_csrf_a, prop1_c_id, c1_c, target_acc)
        assert r29_no_csrf_snap_after == r29_no_csrf_snap_before

    # Refusal: Bad CSRF
    with migrated_database.begin() as conn_r29_bad_csrf_b:
        r29_bad_csrf_snap_before = snapshot_r29_state(conn_r29_bad_csrf_b, prop1_c_id, c1_c, target_acc)
    res_r29_bad_csrf = await client.post(
        f"/v1/council/identity-migration/{prop1_c_id}/confirm",
        cookies=c.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content="csrf_token=bad-token&version=0&reason=Confirming+with+bad+CSRF",
    )
    assert res_r29_bad_csrf.status_code == 403
    with migrated_database.begin() as conn_r29_bad_csrf_a:
        r29_bad_csrf_snap_after = snapshot_r29_state(conn_r29_bad_csrf_a, prop1_c_id, c1_c, target_acc)
        assert r29_bad_csrf_snap_after == r29_bad_csrf_snap_before

    # Refusal: Bad Origin
    with migrated_database.begin() as conn_r29_bad_origin_b:
        r29_bad_origin_snap_before = snapshot_r29_state(conn_r29_bad_origin_b, prop1_c_id, c1_c, target_acc)
    res_r29_bad_origin = await client.post(
        f"/v1/council/identity-migration/{prop1_c_id}/confirm",
        cookies=c.cookies(settings),
        headers={"content-type": FORM, "origin": "https://evil.example.com"},
        content=f"csrf_token={csrf_token_for(settings, c)}&version=0&reason=Confirming+with+bad+origin",
    )
    assert res_r29_bad_origin.status_code == 403
    with migrated_database.begin() as conn_r29_bad_origin_a:
        r29_bad_origin_snap_after = snapshot_r29_state(conn_r29_bad_origin_a, prop1_c_id, c1_c, target_acc)
        assert r29_bad_origin_snap_after == r29_bad_origin_snap_before

    # Refusal: Stale Version
    with migrated_database.begin() as conn_r29_stale_b:
        r29_stale_snap_before = snapshot_r29_state(conn_r29_stale_b, prop1_c_id, c1_c, target_acc)
    res_r29_stale = await client.post(
        f"/v1/council/identity-migration/{prop1_c_id}/confirm",
        cookies=c.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, c)}&version=99&reason=Stale+version",
    )
    assert res_r29_stale.status_code == 409
    with migrated_database.begin() as conn_r29_stale_a:
        r29_stale_snap_after = snapshot_r29_state(conn_r29_stale_a, prop1_c_id, c1_c, target_acc)
        assert r29_stale_snap_after == r29_stale_snap_before

    # Refusal: Non-confirmable (ambiguous) proposal
    with migrated_database.begin() as conn_r29_non_conf_b:
        r29_non_confirmable_snap_before = snapshot_r29_state(conn_r29_non_conf_b, prop2_c_id, c2_c, target_acc)
    res_r29_non_confirmable = await client.post(
        f"/v1/council/identity-migration/{prop2_c_id}/confirm",
        cookies=c.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, c)}&version=0&reason=Confirming+ambiguous+proposal",
    )
    assert res_r29_non_confirmable.status_code == 409
    with migrated_database.begin() as conn_r29_non_conf_a:
        r29_non_confirmable_snap_after = snapshot_r29_state(conn_r29_non_conf_a, prop2_c_id, c2_c, target_acc)
        assert r29_non_confirmable_snap_after == r29_non_confirmable_snap_before

    # R-29 All 8 Callers
    assert (await client.post(f"/v1/council/identity-migration/{prop1_c_id}/confirm", cookies=u.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content="version=0&reason=test")).status_code == 401
    assert (await client.post(f"/v1/council/identity-migration/{prop1_c_id}/confirm", cookies=n.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, n)}&version=0&reason=test")).status_code == 403
    assert (await client.post(f"/v1/council/identity-migration/{prop1_c_id}/confirm", cookies=m.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, m)}&version=0&reason=test")).status_code == 403
    assert (await client.post(f"/v1/council/identity-migration/{prop1_c_id}/confirm", cookies=a.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, a)}&version=0&reason=test")).status_code == 403
    assert (await client.post(f"/v1/council/identity-migration/{prop1_c_id}/confirm", cookies=bg.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, bg)}&version=0&reason=test")).status_code == 403
    assert (await client.post(f"/v1/council/identity-migration/{prop1_c_id}/confirm", cookies=ac.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, ac)}&version=0&reason=test")).status_code == 403

    # Success: C confirms proposal 1_c
    res_r29_c = await client.post(
        f"/v1/council/identity-migration/{prop1_c_id}/confirm",
        cookies=c.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, c)}&version=0&reason=Council+C+confirmed",
    )
    assert res_r29_c.status_code == 303

    # Success: CA confirms proposal 1_ca
    res_r29_ca = await client.post(
        f"/v1/council/identity-migration/{prop1_ca_id}/confirm",
        cookies=ca.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, ca)}&version=0&reason=Council+CA+confirmed",
    )
    assert res_r29_ca.status_code == 303

    # Safe 404 on absent proposal
    unknown_prop = uuid4()
    res_abs_prop = await client.post(
        f"/v1/council/identity-migration/{unknown_prop}/confirm",
        cookies=c.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, c)}&version=0&reason=Absent+proposal",
    )
    res_mal_prop = await client.post(
        "/v1/council/identity-migration/not-a-uuid/confirm",
        cookies=c.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, c)}&version=0&reason=Malformed+proposal",
    )
    assert_identical_denial_responses(res_abs_prop, res_mal_prop)

    # =========================================================================
    # R-30 Reject Proposal (POST) - Refusal Snapshots & All 8 Callers
    # =========================================================================
    # Refusal: No CSRF
    with migrated_database.begin() as conn_r30_no_csrf_b:
        r30_no_csrf_snap_before = snapshot_r30_state(conn_r30_no_csrf_b, prop2_c_id, c2_c)
    res_r30_no_csrf = await client.post(
        f"/v1/council/identity-migration/{prop2_c_id}/reject",
        cookies=c.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content="reason=Rejecting+without+CSRF",
    )
    assert res_r30_no_csrf.status_code == 403
    with migrated_database.begin() as conn_r30_no_csrf_a:
        r30_no_csrf_snap_after = snapshot_r30_state(conn_r30_no_csrf_a, prop2_c_id, c2_c)
        assert r30_no_csrf_snap_after == r30_no_csrf_snap_before

    # Refusal: Bad CSRF
    with migrated_database.begin() as conn_r30_bad_csrf_b:
        r30_bad_csrf_snap_before = snapshot_r30_state(conn_r30_bad_csrf_b, prop2_c_id, c2_c)
    res_r30_bad_csrf = await client.post(
        f"/v1/council/identity-migration/{prop2_c_id}/reject",
        cookies=c.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content="csrf_token=bad-token&reason=Rejecting+with+bad+CSRF",
    )
    assert res_r30_bad_csrf.status_code == 403
    with migrated_database.begin() as conn_r30_bad_csrf_a:
        r30_bad_csrf_snap_after = snapshot_r30_state(conn_r30_bad_csrf_a, prop2_c_id, c2_c)
        assert r30_bad_csrf_snap_after == r30_bad_csrf_snap_before

    # Refusal: Bad Origin
    with migrated_database.begin() as conn_r30_bad_origin_b:
        r30_bad_origin_snap_before = snapshot_r30_state(conn_r30_bad_origin_b, prop2_c_id, c2_c)
    res_r30_bad_origin = await client.post(
        f"/v1/council/identity-migration/{prop2_c_id}/reject",
        cookies=c.cookies(settings),
        headers={"content-type": FORM, "origin": "https://evil.example.com"},
        content=f"csrf_token={csrf_token_for(settings, c)}&reason=Rejecting+with+bad+origin",
    )
    assert res_r30_bad_origin.status_code == 403
    with migrated_database.begin() as conn_r30_bad_origin_a:
        r30_bad_origin_snap_after = snapshot_r30_state(conn_r30_bad_origin_a, prop2_c_id, c2_c)
        assert r30_bad_origin_snap_after == r30_bad_origin_snap_before

    # R-30 All 8 Callers
    assert (await client.post(f"/v1/council/identity-migration/{prop2_c_id}/reject", cookies=u.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content="reason=test")).status_code == 401
    assert (await client.post(f"/v1/council/identity-migration/{prop2_c_id}/reject", cookies=n.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, n)}&reason=test")).status_code == 403
    assert (await client.post(f"/v1/council/identity-migration/{prop2_c_id}/reject", cookies=m.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, m)}&reason=test")).status_code == 403
    assert (await client.post(f"/v1/council/identity-migration/{prop2_c_id}/reject", cookies=a.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, a)}&reason=test")).status_code == 403
    assert (await client.post(f"/v1/council/identity-migration/{prop2_c_id}/reject", cookies=bg.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, bg)}&reason=test")).status_code == 403
    assert (await client.post(f"/v1/council/identity-migration/{prop2_c_id}/reject", cookies=ac.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, ac)}&reason=test")).status_code == 403

    # Success: C rejects proposal 2_c
    res_r30_c = await client.post(
        f"/v1/council/identity-migration/{prop2_c_id}/reject",
        cookies=c.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, c)}&reason=Council+C+rejected",
    )
    assert res_r30_c.status_code == 303

    # Success: CA rejects proposal 2_ca
    res_r30_ca = await client.post(
        f"/v1/council/identity-migration/{prop2_ca_id}/reject",
        cookies=ca.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, ca)}&reason=Council+CA+rejected",
    )
    assert res_r30_ca.status_code == 303

    # =========================================================================
    # R-31 Field Profile (GET) - All 8 Callers & Strict Read-Only Proof
    # =========================================================================
    assert (await client.get("/v1/council/field-profile", cookies=u.cookies(settings))).status_code == 303
    assert (await client.get("/v1/council/field-profile", cookies=n.cookies(settings))).status_code == 403
    assert (await client.get("/v1/council/field-profile", cookies=m.cookies(settings))).status_code == 403
    
    res_r31_c = await client.get("/v1/council/field-profile", cookies=c.cookies(settings))
    assert res_r31_c.status_code == 200
    assert "reported_never_writable" in res_r31_c.text

    res_r31_a = await client.get("/v1/council/field-profile", cookies=a.cookies(settings))
    assert res_r31_a.status_code == 200
    assert "reported_never_writable" in res_r31_a.text

    res_r31_ca = await client.get("/v1/council/field-profile", cookies=ca.cookies(settings))
    assert res_r31_ca.status_code == 200
    assert "reported_never_writable" in res_r31_ca.text

    assert (await client.get("/v1/council/field-profile", cookies=bg.cookies(settings))).status_code == 403
    assert (await client.get("/v1/council/field-profile", cookies=ac.cookies(settings))).status_code == 403

    res_r31_post = await client.post("/v1/council/field-profile", cookies=c.cookies(settings))
    assert res_r31_post.status_code == 405

    # =========================================================================
    # R-32 Role Capabilities Overview (GET) - All 8 Callers
    # =========================================================================
    assert (await client.get("/v1/admin/role-capabilities", cookies=u.cookies(settings))).status_code == 303
    assert (await client.get("/v1/admin/role-capabilities", cookies=n.cookies(settings))).status_code == 403
    assert (await client.get("/v1/admin/role-capabilities", cookies=m.cookies(settings))).status_code == 403
    assert (await client.get("/v1/admin/role-capabilities", cookies=c.cookies(settings))).status_code == 403

    res_r32_a = await client.get("/v1/admin/role-capabilities", cookies=a.cookies(settings))
    assert res_r32_a.status_code == 200
    assert 'data-scope="full"' in res_r32_a.text

    res_r32_ca = await client.get("/v1/admin/role-capabilities", cookies=ca.cookies(settings))
    assert res_r32_ca.status_code == 200
    assert 'data-scope="full"' in res_r32_ca.text

    res_r32_bg = await client.get("/v1/admin/role-capabilities", cookies=bg.cookies(settings))
    assert res_r32_bg.status_code == 200
    assert 'data-scope="emergency_continuity"' in res_r32_bg.text

    res_r32_ac = await client.get("/v1/admin/role-capabilities", cookies=ac.cookies(settings))
    assert res_r32_ac.status_code == 200
    assert 'data-scope="emergency_continuity"' in res_r32_ac.text

    # =========================================================================
    # R-33 Create Role Mapping (POST) - Refusal Snapshots & All 8 Callers
    # =========================================================================
    # Refusal: No CSRF
    with migrated_database.begin() as conn_r33_no_csrf_b:
        r33_no_csrf_snap_before = snapshot_r33_state(conn_r33_no_csrf_b, settings.discord.guild_id, 800000000000000401, 'guild_council')
    res_r33_no_csrf = await client.post(
        "/v1/admin/role-capabilities",
        cookies=a.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content="role_id=800000000000000401&capability=guild_council&reason=No+CSRF",
    )
    assert res_r33_no_csrf.status_code == 403
    with migrated_database.begin() as conn_r33_no_csrf_a:
        r33_no_csrf_snap_after = snapshot_r33_state(conn_r33_no_csrf_a, settings.discord.guild_id, 800000000000000401, 'guild_council')
        assert r33_no_csrf_snap_after == r33_no_csrf_snap_before

    # Refusal: Bad CSRF
    with migrated_database.begin() as conn_r33_bad_csrf_b:
        r33_bad_csrf_snap_before = snapshot_r33_state(conn_r33_bad_csrf_b, settings.discord.guild_id, 800000000000000401, 'guild_council')
    res_r33_bad_csrf = await client.post(
        "/v1/admin/role-capabilities",
        cookies=a.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content="csrf_token=bad-token&role_id=800000000000000401&capability=guild_council&reason=Bad+CSRF",
    )
    assert res_r33_bad_csrf.status_code == 403
    with migrated_database.begin() as conn_r33_bad_csrf_a:
        r33_bad_csrf_snap_after = snapshot_r33_state(conn_r33_bad_csrf_a, settings.discord.guild_id, 800000000000000401, 'guild_council')
        assert r33_bad_csrf_snap_after == r33_bad_csrf_snap_before

    # Refusal: Bad Origin
    with migrated_database.begin() as conn_r33_bad_origin_b:
        r33_bad_origin_snap_before = snapshot_r33_state(conn_r33_bad_origin_b, settings.discord.guild_id, 800000000000000401, 'guild_council')
    res_r33_bad_origin = await client.post(
        "/v1/admin/role-capabilities",
        cookies=a.cookies(settings),
        headers={"content-type": FORM, "origin": "https://evil.example.com"},
        content=f"csrf_token={csrf_token_for(settings, a)}&role_id=800000000000000401&capability=guild_council&reason=Bad+Origin",
    )
    assert res_r33_bad_origin.status_code == 403
    with migrated_database.begin() as conn_r33_bad_origin_a:
        r33_bad_origin_snap_after = snapshot_r33_state(conn_r33_bad_origin_a, settings.discord.guild_id, 800000000000000401, 'guild_council')
        assert r33_bad_origin_snap_after == r33_bad_origin_snap_before

    # Refusal: AC caller attempting non-allowlisted capability under N-67
    with migrated_database.begin() as conn_r33_ac_den_b:
        r33_ac_denied_snap_before = snapshot_r33_state(conn_r33_ac_den_b, settings.discord.guild_id, 800000000000000401, 'guild_council')
    res_r33_ac_denied = await client.post(
        "/v1/admin/role-capabilities",
        cookies=ac.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, ac)}&role_id=800000000000000401&capability=guild_council&reason=Attempting+council+role",
    )
    assert res_r33_ac_denied.status_code == 403
    with migrated_database.begin() as conn_r33_ac_den_a:
        r33_ac_denied_snap_after = snapshot_r33_state(conn_r33_ac_den_a, settings.discord.guild_id, 800000000000000401, 'guild_council')
        assert r33_ac_denied_snap_after == r33_ac_denied_snap_before

    # R-33 All 8 Callers
    assert (await client.post("/v1/admin/role-capabilities", cookies=u.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content="role_id=800000000000000401&capability=guild_council&reason=test")).status_code == 401
    assert (await client.post("/v1/admin/role-capabilities", cookies=n.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, n)}&role_id=800000000000000401&capability=guild_council&reason=test")).status_code == 403
    assert (await client.post("/v1/admin/role-capabilities", cookies=m.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, m)}&role_id=800000000000000401&capability=guild_council&reason=test")).status_code == 403
    assert (await client.post("/v1/admin/role-capabilities", cookies=c.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, c)}&role_id=800000000000000401&capability=guild_council&reason=test")).status_code == 403

    # Success A: creates ordinary mapping
    res_r33_a = await client.post(
        "/v1/admin/role-capabilities",
        cookies=a.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, a)}&role_id=800000000000000402&capability=guild_council&reason=Adding+new+officer+A",
    )
    assert res_r33_a.status_code == 303

    # Success CA: creates ordinary mapping
    res_r33_ca = await client.post(
        "/v1/admin/role-capabilities",
        cookies=ca.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, ca)}&role_id=800000000000000405&capability=guild_council&reason=Adding+new+officer+CA",
    )
    assert res_r33_ca.status_code == 303

    # Success BG: creates emergency mapping for platform_administrator (N-67 allowlist)
    res_r33_bg = await client.post(
        "/v1/admin/role-capabilities",
        cookies=bg.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, bg)}&role_id=800000000000000403&capability=platform_administrator&reason=BG+emergency+admin",
    )
    assert res_r33_bg.status_code == 303

    # Success AC: creates emergency mapping for platform_administrator (N-67 allowlist)
    res_r33_ac = await client.post(
        "/v1/admin/role-capabilities",
        cookies=ac.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, ac)}&role_id=800000000000000404&capability=platform_administrator&reason=AC+emergency+admin",
    )
    assert res_r33_ac.status_code == 303

    # =========================================================================
    # R-34 Revoke Role Mapping (POST) - Refusal Snapshots & All 8 Callers
    # =========================================================================
    # Refusal: No CSRF
    with migrated_database.begin() as conn_r34_no_csrf_b:
        r34_no_csrf_snap_before = snapshot_r34_state(conn_r34_no_csrf_b, map_ord_a_id)
    res_r34_no_csrf = await client.post(
        f"/v1/admin/role-capabilities/{map_ord_a_id}/revoke",
        cookies=a.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content="version=0&reason=Revoking+without+CSRF",
    )
    assert res_r34_no_csrf.status_code == 403
    with migrated_database.begin() as conn_r34_no_csrf_a:
        r34_no_csrf_snap_after = snapshot_r34_state(conn_r34_no_csrf_a, map_ord_a_id)
        assert r34_no_csrf_snap_after == r34_no_csrf_snap_before

    # Refusal: Bad CSRF
    with migrated_database.begin() as conn_r34_bad_csrf_b:
        r34_bad_csrf_snap_before = snapshot_r34_state(conn_r34_bad_csrf_b, map_ord_a_id)
    res_r34_bad_csrf = await client.post(
        f"/v1/admin/role-capabilities/{map_ord_a_id}/revoke",
        cookies=a.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content="csrf_token=bad-token&version=0&reason=Revoking+with+bad+CSRF",
    )
    assert res_r34_bad_csrf.status_code == 403
    with migrated_database.begin() as conn_r34_bad_csrf_a:
        r34_bad_csrf_snap_after = snapshot_r34_state(conn_r34_bad_csrf_a, map_ord_a_id)
        assert r34_bad_csrf_snap_after == r34_bad_csrf_snap_before

    # Refusal: Bad Origin
    with migrated_database.begin() as conn_r34_bad_origin_b:
        r34_bad_origin_snap_before = snapshot_r34_state(conn_r34_bad_origin_b, map_ord_a_id)
    res_r34_bad_origin = await client.post(
        f"/v1/admin/role-capabilities/{map_ord_a_id}/revoke",
        cookies=a.cookies(settings),
        headers={"content-type": FORM, "origin": "https://evil.example.com"},
        content=f"csrf_token={csrf_token_for(settings, a)}&version=0&reason=Revoking+with+bad+origin",
    )
    assert res_r34_bad_origin.status_code == 403
    with migrated_database.begin() as conn_r34_bad_origin_a:
        r34_bad_origin_snap_after = snapshot_r34_state(conn_r34_bad_origin_a, map_ord_a_id)
        assert r34_bad_origin_snap_after == r34_bad_origin_snap_before

    # Refusal: Stale Version
    with migrated_database.begin() as conn_r34_stale_b:
        r34_stale_snap_before = snapshot_r34_state(conn_r34_stale_b, map_ord_a_id)
    res_r34_stale = await client.post(
        f"/v1/admin/role-capabilities/{map_ord_a_id}/revoke",
        cookies=a.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, a)}&version=99&reason=Stale+version",
    )
    assert res_r34_stale.status_code == 409
    with migrated_database.begin() as conn_r34_stale_a:
        r34_stale_snap_after = snapshot_r34_state(conn_r34_stale_a, map_ord_a_id)
        assert r34_stale_snap_after == r34_stale_snap_before

    # Refusal: Protected Bootstrap Mapping
    with migrated_database.begin() as conn_r34_prot_b:
        r34_protected_snap_before = snapshot_r34_state(conn_r34_prot_b, map_boot_id)
    res_r34_protected = await client.post(
        f"/v1/admin/role-capabilities/{map_boot_id}/revoke",
        cookies=a.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, a)}&version=0&reason=Revoking+protected+mapping",
    )
    assert res_r34_protected.status_code == 403
    with migrated_database.begin() as conn_r34_prot_a:
        r34_protected_snap_after = snapshot_r34_state(conn_r34_prot_a, map_boot_id)
        assert r34_protected_snap_after == r34_protected_snap_before

    # R-34 All 8 Callers
    assert (await client.post(f"/v1/admin/role-capabilities/{map_ord_a_id}/revoke", cookies=u.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content="version=0&reason=test")).status_code == 401
    assert (await client.post(f"/v1/admin/role-capabilities/{map_ord_a_id}/revoke", cookies=n.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, n)}&version=0&reason=test")).status_code == 403
    assert (await client.post(f"/v1/admin/role-capabilities/{map_ord_a_id}/revoke", cookies=m.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, m)}&version=0&reason=test")).status_code == 403
    assert (await client.post(f"/v1/admin/role-capabilities/{map_ord_a_id}/revoke", cookies=c.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, c)}&version=0&reason=test")).status_code == 403

    # Success A: revokes ordinary mapping map_ord_a_id
    res_r34_a = await client.post(
        f"/v1/admin/role-capabilities/{map_ord_a_id}/revoke",
        cookies=a.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, a)}&version=0&reason=Revoking+ordinary+mapping+A",
    )
    assert res_r34_a.status_code == 303

    # Success CA: revokes ordinary mapping map_ord_ca_id
    res_r34_ca = await client.post(
        f"/v1/admin/role-capabilities/{map_ord_ca_id}/revoke",
        cookies=ca.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, ca)}&version=0&reason=Revoking+ordinary+mapping+CA",
    )
    assert res_r34_ca.status_code == 303

    # Success BG: revokes a dedicated emergency mapping (under N-67), leaving
    # `map_emerg_bg_id` available for the later R-38 refusal matrix.
    res_r34_bg = await client.post(
        f"/v1/admin/role-capabilities/{map_emerg_to_ratify_a_id}/revoke",
        cookies=bg.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, bg)}&version=0&reason=Revoking+emergency+admin+BG",
    )
    assert res_r34_bg.status_code == 303

    # Success AC: revokes emergency admin mapping map_emerg_ac_id (under N-67)
    res_r34_ac = await client.post(
        f"/v1/admin/role-capabilities/{map_emerg_ac_id}/revoke",
        cookies=ac.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, ac)}&version=0&reason=Revoking+emergency+admin+AC",
    )
    assert res_r34_ac.status_code == 303

    # =========================================================================
    # R-35 Account Identities (GET) - All 8 Callers & Data Isolation
    # =========================================================================
    assert (await client.get("/v1/account/identities", cookies=u.cookies(settings))).status_code == 303

    res_r35_n = await client.get("/v1/account/identities", cookies=n.cookies(settings))
    assert res_r35_n.status_code == 200
    assert str(n.account_id) in res_r35_n.text

    res_r35_m = await client.get("/v1/account/identities", cookies=m.cookies(settings))
    assert res_r35_m.status_code == 200
    assert str(m.account_id) in res_r35_m.text

    res_r35_c = await client.get("/v1/account/identities", cookies=c.cookies(settings))
    assert res_r35_c.status_code == 200
    assert str(c.account_id) in res_r35_c.text

    res_r35_a = await client.get("/v1/account/identities", cookies=a.cookies(settings))
    assert res_r35_a.status_code == 200
    assert str(a.account_id) in res_r35_a.text

    res_r35_ca = await client.get("/v1/account/identities", cookies=ca.cookies(settings))
    assert res_r35_ca.status_code == 200
    assert str(ca.account_id) in res_r35_ca.text

    res_r35_bg = await client.get("/v1/account/identities", cookies=bg.cookies(settings))
    assert res_r35_bg.status_code == 200
    assert str(bg.account_id) in res_r35_bg.text

    res_r35_ac = await client.get("/v1/account/identities", cookies=ac.cookies(settings))
    assert res_r35_ac.status_code == 200
    assert str(ac.account_id) in res_r35_ac.text

    # =========================================================================
    # R-36 Additional Provider Link Start (GET) - All 8 Callers & Presentation
    # =========================================================================
    assert (await client.get("/v1/account/identities/link/start", cookies=u.cookies(settings))).status_code == 303

    res_r36_n = await client.get("/v1/account/identities/link/start", cookies=n.cookies(settings))
    assert res_r36_n.status_code == 200
    assert 'data-state="denied"' in res_r36_n.text
    assert "no_additional_provider" in res_r36_n.text

    res_r36_m = await client.get("/v1/account/identities/link/start", cookies=m.cookies(settings))
    assert res_r36_m.status_code == 200
    assert 'data-state="denied"' in res_r36_m.text
    assert "no_additional_provider" in res_r36_m.text

    res_r36_c = await client.get("/v1/account/identities/link/start", cookies=c.cookies(settings))
    assert res_r36_c.status_code == 200
    assert 'data-state="denied"' in res_r36_c.text
    assert "no_additional_provider" in res_r36_c.text

    res_r36_a = await client.get("/v1/account/identities/link/start", cookies=a.cookies(settings))
    assert res_r36_a.status_code == 200
    assert 'data-state="denied"' in res_r36_a.text
    assert "no_additional_provider" in res_r36_a.text

    res_r36_ca = await client.get("/v1/account/identities/link/start", cookies=ca.cookies(settings))
    assert res_r36_ca.status_code == 200
    assert 'data-state="denied"' in res_r36_ca.text
    assert "no_additional_provider" in res_r36_ca.text

    assert (await client.get("/v1/account/identities/link/start", cookies=bg.cookies(settings))).status_code == 403
    assert (await client.get("/v1/account/identities/link/start", cookies=ac.cookies(settings))).status_code == 403

    # =========================================================================
    # R-37 Unlink Identity (POST) - Refusal Snapshots & All 8 Callers
    # =========================================================================
    # Refusal: No CSRF
    with migrated_database.begin() as conn_r37_no_csrf_b:
        r37_no_csrf_snap_before = snapshot_r37_state(conn_r37_no_csrf_b, m_extra_id)
    res_r37_no_csrf = await client.post(
        f"/v1/account/identities/{m_extra_id}/unlink",
        cookies=m.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content="",
    )
    assert res_r37_no_csrf.status_code == 403
    with migrated_database.begin() as conn_r37_no_csrf_a:
        r37_no_csrf_snap_after = snapshot_r37_state(conn_r37_no_csrf_a, m_extra_id)
        assert r37_no_csrf_snap_after == r37_no_csrf_snap_before

    # Refusal: Bad CSRF
    with migrated_database.begin() as conn_r37_bad_csrf_b:
        r37_bad_csrf_snap_before = snapshot_r37_state(conn_r37_bad_csrf_b, m_extra_id)
    res_r37_bad_csrf = await client.post(
        f"/v1/account/identities/{m_extra_id}/unlink",
        cookies=m.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content="csrf_token=bad-token",
    )
    assert res_r37_bad_csrf.status_code == 403
    with migrated_database.begin() as conn_r37_bad_csrf_a:
        r37_bad_csrf_snap_after = snapshot_r37_state(conn_r37_bad_csrf_a, m_extra_id)
        assert r37_bad_csrf_snap_after == r37_bad_csrf_snap_before

    # Refusal: Bad Origin
    with migrated_database.begin() as conn_r37_bad_origin_b:
        r37_bad_origin_snap_before = snapshot_r37_state(conn_r37_bad_origin_b, m_extra_id)
    res_r37_bad_origin = await client.post(
        f"/v1/account/identities/{m_extra_id}/unlink",
        cookies=m.cookies(settings),
        headers={"content-type": FORM, "origin": "https://evil.example.com"},
        content=f"csrf_token={csrf_token_for(settings, m)}",
    )
    assert res_r37_bad_origin.status_code == 403
    with migrated_database.begin() as conn_r37_bad_origin_a:
        r37_bad_origin_snap_after = snapshot_r37_state(conn_r37_bad_origin_a, m_extra_id)
        assert r37_bad_origin_snap_after == r37_bad_origin_snap_before

    # Refusal: Emergency session caller (BG / AC)
    with migrated_database.begin() as conn_r37_emerg_b:
        r37_emergency_session_snap_before = snapshot_r37_state(conn_r37_emerg_b, bg_id)
    res_r37_emergency_session = await client.post(
        f"/v1/account/identities/{bg_id}/unlink",
        cookies=bg.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, bg)}",
    )
    assert res_r37_emergency_session.status_code == 403
    with migrated_database.begin() as conn_r37_emerg_a:
        r37_emergency_session_snap_after = snapshot_r37_state(conn_r37_emerg_a, bg_id)
        assert r37_emergency_session_snap_after == r37_emergency_session_snap_before

    # Refusal: Already retired identity
    with migrated_database.begin() as conn_r37_ret_b:
        r37_already_retired_snap_before = snapshot_r37_state(conn_r37_ret_b, m_retired_id)
    res_r37_already_retired = await client.post(
        f"/v1/account/identities/{m_retired_id}/unlink",
        cookies=m.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, m)}",
    )
    assert res_r37_already_retired.status_code == 409
    with migrated_database.begin() as conn_r37_ret_a:
        r37_already_retired_snap_after = snapshot_r37_state(conn_r37_ret_a, m_retired_id)
        assert r37_already_retired_snap_after == r37_already_retired_snap_before

    # R-37 All 8 Callers (Authorized callers N, M, C, A, CA each unlinks their own eligible secondary identity)
    assert (await client.post(f"/v1/account/identities/{m_extra_id}/unlink", cookies=u.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content="")).status_code == 401
    
    res_r37_n = await client.post(
        f"/v1/account/identities/{n_extra_id}/unlink",
        cookies=n.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, n)}",
    )
    assert res_r37_n.status_code == 303

    res_r37_m = await client.post(
        f"/v1/account/identities/{m_extra_id}/unlink",
        cookies=m.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, m)}",
    )
    assert res_r37_m.status_code == 303

    res_r37_c = await client.post(
        f"/v1/account/identities/{c_extra_id}/unlink",
        cookies=c.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, c)}",
    )
    assert res_r37_c.status_code == 303

    res_r37_a = await client.post(
        f"/v1/account/identities/{a_extra_id}/unlink",
        cookies=a.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, a)}",
    )
    assert res_r37_a.status_code == 303

    res_r37_ca = await client.post(
        f"/v1/account/identities/{ca_extra_id}/unlink",
        cookies=ca.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, ca)}",
    )
    assert res_r37_ca.status_code == 303

    assert (await client.post(f"/v1/account/identities/{bg_id}/unlink", cookies=bg.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, bg)}")).status_code == 403
    assert (await client.post(f"/v1/account/identities/{ac_id}/unlink", cookies=ac.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, ac)}")).status_code == 403

    # Safe 404 on absent vs other account identity (non-enumeration)
    unknown_ident = uuid4()
    res_abs_ident = await client.post(
        f"/v1/account/identities/{unknown_ident}/unlink",
        cookies=m.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, m)}",
    )
    res_other_ident = await client.post(
        f"/v1/account/identities/{other_identity_id}/unlink",
        cookies=m.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, m)}",
    )
    assert_identical_denial_responses(res_abs_ident, res_other_ident)

    # Refusal: Last Usable Identity (now that m_extra_id is retired, m has only 1 active identity: m_primary_id)
    with migrated_database.begin() as conn_last_use_pre:
        m_active_count = conn_last_use_pre.execute(
            text("SELECT count(*) FROM external_identities WHERE platform_account_id = :aid AND state = 'active'"),
            {"aid": m.account_id},
        ).scalar_one()
        assert m_active_count == 1, f"Member account must have exactly 1 active identity before last-usable test, got {m_active_count}"
        
        ident_target_row = conn_last_use_pre.execute(
            text("SELECT platform_account_id, state FROM external_identities WHERE id = :id"),
            {"id": m_primary_id},
        ).mappings().one()
        assert ident_target_row["platform_account_id"] == m.account_id
        assert ident_target_row["state"] == "active"

        # Baseline applied and refusal audit counts
        applied_audit_before = conn_last_use_pre.execute(
            text("SELECT count(*) FROM audit_events WHERE action = 'identity.unlinked' AND entity_id = :id"),
            {"id": str(m_primary_id)},
        ).scalar_one()
        refused_audit_before = conn_last_use_pre.execute(
            text("SELECT count(*) FROM audit_events WHERE action = 'identity.link_refused' AND entity_id = :id"),
            {"id": str(m_primary_id)},
        ).scalar_one()
        assert applied_audit_before == 0
        assert refused_audit_before == 0

    res_r37_last_identity = await client.post(
        f"/v1/account/identities/{m_primary_id}/unlink",
        cookies=m.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, m)}",
    )
    assert res_r37_last_identity.status_code == 409

    with migrated_database.begin() as conn_last_use_post:
        ident_post_row = conn_last_use_post.execute(
            text("SELECT state FROM external_identities WHERE id = :id"),
            {"id": m_primary_id},
        ).mappings().one()
        assert ident_post_row["state"] == "active"

        # Contract-revealing assertion: exactly one durable identity.link_refused audit event
        refused_audit_after = conn_last_use_post.execute(
            text("SELECT count(*) FROM audit_events WHERE action = 'identity.link_refused' AND entity_type = 'external_identity' AND entity_id = :id"),
            {"id": str(m_primary_id)},
        ).scalar_one()
        assert refused_audit_after == 1, (
            "Backend contract conflict: AccountIdentityService.unlink records identity.link_refused and then raises "
            "UnlinkRefused inside unit(), whose transaction rolls back on exception, causing the refusal event to be lost."
        )

        # Applied unlink event remains 0
        applied_audit_after = conn_last_use_post.execute(
            text("SELECT count(*) FROM audit_events WHERE action = 'identity.unlinked' AND entity_id = :id"),
            {"id": str(m_primary_id)},
        ).scalar_one()
        assert applied_audit_after == 0

    # =========================================================================
    # R-38 Ratify Role Mapping (POST) - Refusal Snapshots & All 8 Callers
    # =========================================================================
    # Refusal: No CSRF
    with migrated_database.begin() as conn_r38_no_csrf_b:
        r38_no_csrf_snap_before = snapshot_r38_state(conn_r38_no_csrf_b, map_emerg_bg_id)
    res_r38_no_csrf = await client.post(
        f"/v1/admin/role-capabilities/{map_emerg_bg_id}/ratify",
        cookies=a.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content="version=0&reason=Ratifying+without+CSRF",
    )
    assert res_r38_no_csrf.status_code == 403
    with migrated_database.begin() as conn_r38_no_csrf_a:
        r38_no_csrf_snap_after = snapshot_r38_state(conn_r38_no_csrf_a, map_emerg_bg_id)
        assert r38_no_csrf_snap_after == r38_no_csrf_snap_before

    # Refusal: Bad CSRF
    with migrated_database.begin() as conn_r38_bad_csrf_b:
        r38_bad_csrf_snap_before = snapshot_r38_state(conn_r38_bad_csrf_b, map_emerg_bg_id)
    res_r38_bad_csrf = await client.post(
        f"/v1/admin/role-capabilities/{map_emerg_bg_id}/ratify",
        cookies=a.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content="csrf_token=bad-token&version=0&reason=Ratifying+with+bad+CSRF",
    )
    assert res_r38_bad_csrf.status_code == 403
    with migrated_database.begin() as conn_r38_bad_csrf_a:
        r38_bad_csrf_snap_after = snapshot_r38_state(conn_r38_bad_csrf_a, map_emerg_bg_id)
        assert r38_bad_csrf_snap_after == r38_bad_csrf_snap_before

    # Refusal: Bad Origin
    with migrated_database.begin() as conn_r38_bad_origin_b:
        r38_bad_origin_snap_before = snapshot_r38_state(conn_r38_bad_origin_b, map_emerg_bg_id)
    res_r38_bad_origin = await client.post(
        f"/v1/admin/role-capabilities/{map_emerg_bg_id}/ratify",
        cookies=a.cookies(settings),
        headers={"content-type": FORM, "origin": "https://evil.example.com"},
        content=f"csrf_token={csrf_token_for(settings, a)}&version=0&reason=Ratifying+with+bad+origin",
    )
    assert res_r38_bad_origin.status_code == 403
    with migrated_database.begin() as conn_r38_bad_origin_a:
        r38_bad_origin_snap_after = snapshot_r38_state(conn_r38_bad_origin_a, map_emerg_bg_id)
        assert r38_bad_origin_snap_after == r38_bad_origin_snap_before

    # Refusal: Stale Version
    with migrated_database.begin() as conn_r38_stale_b:
        r38_stale_snap_before = snapshot_r38_state(conn_r38_stale_b, map_emerg_bg_id)
    res_r38_stale = await client.post(
        f"/v1/admin/role-capabilities/{map_emerg_bg_id}/ratify",
        cookies=a.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, a)}&version=99&reason=Stale+version",
    )
    assert res_r38_stale.status_code == 409
    with migrated_database.begin() as conn_r38_stale_a:
        r38_stale_snap_after = snapshot_r38_state(conn_r38_stale_a, map_emerg_bg_id)
        assert r38_stale_snap_after == r38_stale_snap_before

    # Refusal: AC caller attempting ratify
    with migrated_database.begin() as conn_r38_ac_ref_b:
        r38_ac_refused_snap_before = snapshot_r38_state(conn_r38_ac_ref_b, map_emerg_bg_id)
    res_r38_ac_refused = await client.post(
        f"/v1/admin/role-capabilities/{map_emerg_bg_id}/ratify",
        cookies=ac.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, ac)}&version=0&reason=AC+cannot+ratify",
    )
    assert res_r38_ac_refused.status_code == 403
    with migrated_database.begin() as conn_r38_ac_ref_a:
        r38_ac_refused_snap_after = snapshot_r38_state(conn_r38_ac_ref_a, map_emerg_bg_id)
        assert r38_ac_refused_snap_after == r38_ac_refused_snap_before

    # R-38 All 8 Callers
    assert (await client.post(f"/v1/admin/role-capabilities/{map_emerg_bg_id}/ratify", cookies=u.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content="version=0&reason=test")).status_code == 401
    assert (await client.post(f"/v1/admin/role-capabilities/{map_emerg_bg_id}/ratify", cookies=n.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, n)}&version=0&reason=test")).status_code == 403
    assert (await client.post(f"/v1/admin/role-capabilities/{map_emerg_bg_id}/ratify", cookies=m.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, m)}&version=0&reason=test")).status_code == 403
    assert (await client.post(f"/v1/admin/role-capabilities/{map_emerg_bg_id}/ratify", cookies=c.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, c)}&version=0&reason=test")).status_code == 403
    assert (await client.post(f"/v1/admin/role-capabilities/{map_emerg_bg_id}/ratify", cookies=bg.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, bg)}&version=0&reason=test")).status_code == 403
    assert (await client.post(f"/v1/admin/role-capabilities/{map_emerg_bg_id}/ratify", cookies=ac.cookies(settings), headers={"content-type": FORM, "origin": PUBLIC_ORIGIN}, content=f"csrf_token={csrf_token_for(settings, ac)}&version=0&reason=test")).status_code == 403

    # Success A: ratifies the mapping preserved through the refusal matrix.
    res_r38_a = await client.post(
        f"/v1/admin/role-capabilities/{map_emerg_bg_id}/ratify",
        cookies=a.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, a)}&version=0&reason=Ratifying+emergency+role+A",
    )
    assert res_r38_a.status_code == 303

    # Success CA: ratifies emergency mapping map_emerg_to_ratify_ca_id
    res_r38_ca = await client.post(
        f"/v1/admin/role-capabilities/{map_emerg_to_ratify_ca_id}/ratify",
        cookies=ca.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, ca)}&version=0&reason=Ratifying+emergency+role+CA",
    )
    assert res_r38_ca.status_code == 303
