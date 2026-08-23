"""Tests for P3.4 Step 9 job status, cancellation and apply confirmation views.

Covers:

1. VM-15 / R-43: `job_status.html`, the navigable page.
   - Every accepted job state rendered honestly: queued, running, completed,
     stale, failed, cancelled.
   - Preview and apply jobs distinguished; `confirm` never inferred from `kind`,
     `job_state`, result counts or timestamps.
   - Bounded reconciliation summary, closed-vocabulary issue codes, bounded
     blocked entries; no artifact bytes, exception text or unbounded warnings.
2. R-44: `job_status_fragment.html`, the polled fragment and R-43's body.
   - `hx-get`/`hx-trigger`/`hx-swap` present for `queued` and `running` only.
   - The interval is the server's `poll_min_seconds`, agreeing with
     `Retry-After`; polling markup is absent in every terminal state.
   - No JavaScript, no inline handlers, no client-built URLs; a manual refresh
     path exists for nonterminal jobs.
3. R-45: Council cancellation control.
   - Exact POST action and exactly `{csrf_token}`; rendered only when
     `view.cancel_available`.
   - CSRF, Origin, content type, 4 KiB body bound, caller matrix, accepted
     cancellation, terminal and committed-effect conflicts, audit cardinality.
4. R-46: Council apply confirmation control.
   - Exact POST action and exactly `{csrf_token, preview_token, nonce}`;
     rendered only when `view.confirm` is present.
   - The **stable** preview-job-derived nonce, and the convergence it buys:
     double-click, lost-response retry and a second browser produce one apply
     job, one effect and one queue audit event.
   - CSRF, Origin, content type, 8 KiB body bound, missing token/nonce, caller
     matrix, non-enumeration, enqueue-not-inline.
   - Expired preview, moved folder/profile/checksum scope, blocking result and a
     running apply each apply nothing.
5. Security and matrix enforcement.
   - Direct-call caller matrices for R-43, R-44, R-45, R-46 (U, N, M, C, A, CA,
     BG, AC), never reached through the page that carries the control.
   - Cross-Council visibility and non-Council non-reachability.
   - Malformed/absent identifiers, byte-identical denials and exact headers.
   - Adversarial XSS in every external text and attribute context.
   - Structural AST validation of post-yield cleanup discipline.
   - All 23 template digests, Step 9 selector ownership, asset manifest.
"""
from __future__ import annotations

import ast
import dataclasses
import hashlib
import inspect
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote
from uuid import UUID, uuid4

import jinja2
import pytest
from sqlalchemy import text
from starlette.requests import Request

from adapters.web.import_routes import _submitted_apply_nonce
from application.audit import ActorCapability
from application.web.jobs import JobKind, JobState
from application.web.view_models import (
    Actor,
    BlockedEntry,
    ConfirmScope,
    Correlation,
    FolderChoice,
    Instant,
    IssueCount,
    JobFailure,
    JobProgress,
    JobStatusView,
    ReconciliationSummary,
    SafeText,
    StaleReason,
)
from tests import foundry_fixtures as fx
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

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = ROOT / "adapters" / "web" / "templates"
STATIC_ROOT = ROOT / "adapters" / "web" / "static"
MANIFEST_PATH = STATIC_ROOT / "asset-integrity.sha256"

FORM = "application/x-www-form-urlencoded"

#: N-27's six, as the vocabulary this suite parametrizes over. There is no
#: seventh, and a state added without a rendering branch fails here.
ALL_JOB_STATES: tuple[str, ...] = (
    "queued",
    "running",
    "completed",
    "stale",
    "failed",
    "cancelled",
)
#: The two the fragment may poll in. Everything else is terminal, and a terminal
#: job's fragment must contain no polling attribute at all.
LIVE_JOB_STATES: tuple[str, ...] = ("queued", "running")
TERMINAL_JOB_STATES: tuple[str, ...] = tuple(
    state for state in ALL_JOB_STATES if state not in LIVE_JOB_STATES
)

from tests.web.template_digests import P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS


# Contract §6.2 authoritative caller matrix for R-43…R-46, plus AC, which §6.2's
# columns do not carry because continuity scope is N-65's rule rather than a
# capability: every import, preview, apply and job route refuses it.
ACCEPTED_ROUTE_CALLER_MATRIX: dict[str, dict[str, int]] = {
    "R-43": {"U": 303, "N": 403, "M": 403, "C": 200, "A": 403, "CA": 200, "BG": 403, "AC": 403},
    "R-44": {"U": 401, "N": 403, "M": 403, "C": 200, "A": 403, "CA": 200, "BG": 403, "AC": 403},
    "R-45": {"U": 401, "N": 403, "M": 403, "C": 303, "A": 403, "CA": 303, "BG": 403, "AC": 403},
    "R-46": {"U": 401, "N": 403, "M": 403, "C": 303, "A": 403, "CA": 303, "BG": 403, "AC": 403},
}

#: The accepted per-route body bounds from §6.2's `Body` column.
R45_BODY_BOUND = 4 * 1024
R46_BODY_BOUND = 8 * 1024

STEP_9_SELECTORS: tuple[str, ...] = (
    ".card",
    ".page-header",
    ".page-title-row",
    ".page-title",
    ".page-description",
    ".section-title",
    ".section-subtitle",
    ".detail-section",
    ".data-grid",
    ".data-item",
    ".data-label",
    ".data-value",
    ".totals-card",
    ".totals-dl",
    ".totals-item",
    ".totals-dt",
    ".totals-dd",
    ".profile-item-list",
    ".profile-entry-item",
    ".profile-entry-main",
    ".profile-key",
    ".candidate-list",
    ".candidate-item",
    ".confirm-form",
    ".confirm-summary-box",
    ".confirm-summary-text",
    ".action-form",
    ".form-actions",
    ".alert",
    ".alert-sm",
    ".alert-info",
    ".alert-warning",
    ".alert-danger",
    ".badge",
    ".badge-sm",
    ".badge-info",
    ".badge-primary",
    ".badge-secondary",
    ".badge-success",
    ".badge-warning",
    ".badge-danger",
    ".btn",
    ".btn-primary",
    ".btn-secondary",
    ".btn-danger",
    ".btn-sm",
    ".reference-code",
    ".validation-code",
    ".cursor-nav",
    ".font-mono",
    ".text-xs",
    ".text-sm",
    ".text-muted",
)

PROHIBITED_STEP_9_SELECTORS: tuple[str, ...] = (
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
    "set-cookie",
    "x-frame-options",
)

#: Every shape of client-side authority the fragment must not acquire. Checked as
#: substrings over the template source, which is coarse deliberately: none of
#: them has a legitimate use here, so there is no false positive to trade away.
FORBIDDEN_SCRIPT_MARKERS: tuple[str, ...] = (
    "<script",
    "javascript:",
    "hx-on",
    "onclick",
    "onload",
    "onerror=",
    "onsubmit",
    "hx-vals",
    "hx-headers",
    "eval(",
    "websocket",
    "hx-ws",
    "hx-sse",
    "localstorage",
    "sessionstorage",
    "document.cookie",
)


# ===========================================================================
# Helpers
# ===========================================================================

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
    """Strip Jinja `{# ... #}` comments to inspect active template markup."""
    return re.sub(r"\{#.*?#\}", " ", template_text, flags=re.DOTALL)


def strip_jinja_statements(template_text: str) -> str:
    """Strip `{% ... %}` tags, replacing each with a **space**.

    Replacing rather than deleting is the whole point. `class="badge {% if x
    %}badge-danger{% else %}badge-warning{% endif %}"` has two class tokens in
    it, and deleting the tags would fuse them into the single nonexistent token
    `badge-dangerbadge-warning` — a coverage check that then reported a missing
    selector that no template ever names.
    """
    return re.sub(r"\{%.*?%\}", " ", template_text, flags=re.DOTALL)


def extract_active_css_classes(css_text: str) -> set[str]:
    """Every class selector in an active (non-commented) CSS rule."""
    active_css = strip_css_comments(css_text)
    active_classes: set[str] = set()
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", active_css):
        for sel_part in m.group(1).split(","):
            for cls in re.findall(r"(?:\A|[^\w\-.])\.([a-zA-Z0-9_\-]+)", sel_part):
                active_classes.add("." + cls)
    return active_classes


def extract_active_template_classes(template_texts: list[str]) -> set[str]:
    """Every class token a template can emit, from **both** branches of a test."""
    active_classes: set[str] = set()
    for template_text in template_texts:
        stripped = strip_jinja_statements(strip_jinja_comments(template_text))
        for m in re.finditer(r"\bclass=(['\"])(.*?)\1", stripped, flags=re.DOTALL):
            for token in re.findall(r"[a-zA-Z0-9_\-]+", m.group(2)):
                active_classes.add("." + token)
    return active_classes


def make_request(path: str = "/v1/council/jobs/00000000-0000-0000-0000-000000000000") -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": [(b"host", b"testserver")],
    }
    return Request(scope)


def assert_identical_denial_responses(res1: Any, res2: Any, *, status: int = 404) -> None:
    """Status, byte-identical body, exact security headers, no disclosure headers."""
    assert res1.status_code == res2.status_code == status, (
        f"Status mismatch in denial responses: {res1.status_code} != {res2.status_code}"
    )
    assert res1.content == res2.content, "Body content mismatch in denial responses"

    for forbidden in FORBIDDEN_DENIAL_HEADERS:
        assert forbidden not in res1.headers, f"Forbidden header '{forbidden}' in first denial"
        assert forbidden not in res2.headers, f"Forbidden header '{forbidden}' in second denial"

    for req_header, expected_val in EXACT_DENIAL_HEADERS.items():
        assert req_header in res1.headers, f"Missing header '{req_header}' in first denial"
        assert req_header in res2.headers, f"Missing header '{req_header}' in second denial"
        v1, v2 = res1.headers[req_header], res2.headers[req_header]
        assert v1 == expected_val, f"First denial '{req_header}' mismatch: {v1!r} != {expected_val!r}"
        assert v2 == expected_val, f"Second denial '{req_header}' mismatch: {v2!r} != {expected_val!r}"


# ===========================================================================
# Route caller matrix validator (§6.2) and negative probes
# ===========================================================================

def validate_route_caller_matrix(matrix: dict[str, dict[str, int]]) -> None:
    expected_routes = {"R-43", "R-44", "R-45", "R-46"}
    assert set(matrix) == expected_routes, f"Matrix route set mismatch: {set(matrix)}"

    expected_callers = {"U", "N", "M", "C", "A", "CA", "BG", "AC"}
    navigation_routes = {"R-43"}
    mutation_routes = {"R-45", "R-46"}

    for route, row in matrix.items():
        assert set(row) == expected_callers, f"Route {route} missing {expected_callers - set(row)}"

        if route in navigation_routes:
            assert row["U"] == 303, f"Navigation route {route} must redirect U, got {row['U']}"
        else:
            # R-44 included: an HTMX fragment answers `401`, because a `303`
            # swapped into a fragment target would render the login page inside
            # the job screen.
            assert row["U"] == 401, f"Non-navigation route {route} must return 401 for U, got {row['U']}"

        assert row["N"] == 403, f"Route {route} must refuse N with 403, got {row['N']}"
        assert row["M"] == 403, f"Route {route} must refuse M with 403, got {row['M']}"

        # Council-only, all four. The Platform Administrator is refused even on
        # the reads: an administrator alone cannot apply an import, and the job
        # surface is where an import is confirmed.
        assert row["A"] == 403, f"Route {route} is Council-only and must refuse A, got {row['A']}"
        assert row["BG"] == 403, f"Route {route} must refuse break-glass, got {row['BG']}"
        assert row["AC"] == 403, f"Route {route} must refuse continuity scope, got {row['AC']}"

        success = 200 if route not in mutation_routes else 303
        assert row["C"] == success, f"Route {route} must permit C with {success}, got {row['C']}"
        assert row["CA"] == success, f"Route {route} must permit CA with {success}, got {row['CA']}"


def test_structural_route_caller_matrix_valid() -> None:
    validate_route_caller_matrix(ACCEPTED_ROUTE_CALLER_MATRIX)


def test_the_transcribed_matrix_agrees_with_the_accepted_contract_document() -> None:
    """The transcription above is checked against §6.2 rather than trusted.

    `test_p3_3_matrix.py` parses the same table for the same reason: a
    transcription is a second copy of a contract, and a second copy is a place
    for the two to disagree quietly.
    """
    contract = (ROOT / "docs" / "contracts" / "phase-3-route-authorization-contract.md").read_text()
    section = contract.split("### 6.2 P3.3 matrix", 1)[1].split("### 6.3", 1)[0]
    states = ("U", "N", "M", "C", "A", "CA", "BG")
    row_re = re.compile(r"^\|\s*(R-\d+)\s*\|\s*`([^`]+)`\s*\|(.+)\|\s*$", re.MULTILINE)

    parsed: dict[str, dict[str, str]] = {}
    for match in row_re.finditer(section):
        cells = [cell.strip() for cell in match.group(3).split("|")]
        parsed[match.group(1)] = dict(zip(states, cells[: len(states)]))
    assert {"R-43", "R-44", "R-45", "R-46"} <= set(parsed), "the §6.2 matrix could not be parsed"

    for route, row in ACCEPTED_ROUTE_CALLER_MATRIX.items():
        for state in states:
            cell = parsed[route][state]
            if cell.startswith("✓"):
                # A permitted cell is not one status: a permitted GET is 200 and
                # a permitted mutation is 303. The transcription carries which.
                assert row[state] in (200, 303), f"{route}/{state} permitted, transcribed {row[state]}"
            else:
                found = re.search(r"(\d{3})", cell)
                assert found is not None, f"{route}/{state} refusal cell has no status: {cell!r}"
                assert row[state] == int(found.group(1)), (
                    f"{route}/{state} transcribed {row[state]}, contract says {found.group(1)}"
                )


def test_falsification_matrix_rejects_administrator_success() -> None:
    mutated = {k: dict(v) for k, v in ACCEPTED_ROUTE_CALLER_MATRIX.items()}
    mutated["R-46"]["A"] = 303
    with pytest.raises(AssertionError, match=r"R-46 is Council-only and must refuse A"):
        validate_route_caller_matrix(mutated)


def test_falsification_matrix_rejects_fragment_redirect_for_u() -> None:
    mutated = {k: dict(v) for k, v in ACCEPTED_ROUTE_CALLER_MATRIX.items()}
    mutated["R-44"]["U"] = 303
    with pytest.raises(AssertionError, match=r"R-44 must return 401 for U"):
        validate_route_caller_matrix(mutated)


def test_falsification_matrix_rejects_continuity_success() -> None:
    mutated = {k: dict(v) for k, v in ACCEPTED_ROUTE_CALLER_MATRIX.items()}
    mutated["R-45"]["AC"] = 303
    with pytest.raises(AssertionError, match=r"R-45 must refuse continuity scope"):
        validate_route_caller_matrix(mutated)


def test_falsification_matrix_rejects_missing_caller() -> None:
    mutated = {k: dict(v) for k, v in ACCEPTED_ROUTE_CALLER_MATRIX.items()}
    del mutated["R-43"]["BG"]
    with pytest.raises(AssertionError, match=r"Route R-43 missing"):
        validate_route_caller_matrix(mutated)


# ===========================================================================
# Form exactness and polling extractors, with negative probes
# ===========================================================================

def _forms(html: str) -> list[re.Match[str]]:
    return list(re.finditer(r"<form\b([^>]*)>(.*?)</form>", html, flags=re.DOTALL | re.IGNORECASE))


def validate_form_exactness(
    html: str,
    *,
    expected_action_pattern: str,
    expected_named_fields: set[str],
    expected_method: str = "post",
) -> dict[str, str]:
    """Exact method and exact named-control set for one form; returns its values.

    Duplicates are a failure rather than a set-collapse: two inputs named `nonce`
    submit two values, and a browser sends both.
    """
    target = None
    for m in _forms(html):
        action_m = re.search(r'action=(["\'])(.*?)\1', m.group(1))
        if action_m and re.search(expected_action_pattern, action_m.group(2)):
            target = m
            break
    assert target is not None, f"Form with action matching '{expected_action_pattern}' not found"

    method_m = re.search(r'method=(["\'])(.*?)\1', target.group(1), flags=re.IGNORECASE)
    assert method_m is not None, "Form must specify a method attribute"
    assert method_m.group(2).lower() == expected_method.lower(), (
        f"Form method expected {expected_method}, got {method_m.group(2)}"
    )

    named: list[str] = []
    values: dict[str, str] = {}
    for control in re.finditer(
        r"<(?:input|select|textarea|button)\b([^>]*)>", target.group(2), flags=re.IGNORECASE
    ):
        attrs = control.group(1)
        name_m = re.search(r'name=(["\'])(.*?)\1', attrs)
        if not name_m:
            continue
        named.append(name_m.group(2))
        value_m = re.search(r'value=(["\'])(.*?)\1', attrs, flags=re.DOTALL)
        values[name_m.group(2)] = value_m.group(2) if value_m else ""

    assert len(named) == len(set(named)), f"Duplicate named fields in form: {named}"
    assert set(named) == expected_named_fields, (
        f"Form named fields mismatch: expected {expected_named_fields}, got {set(named)}"
    )
    return values


def extract_polling_attributes(html: str) -> dict[str, str | None]:
    """The fragment's polling attributes, or `None` for each absent one."""
    def attr(name: str) -> str | None:
        m = re.search(rf'\b{name}=(["\'])(.*?)\1', html, flags=re.DOTALL)
        return m.group(2) if m else None

    return {
        "hx-get": attr("hx-get"),
        "hx-trigger": attr("hx-trigger"),
        "hx-swap": attr("hx-swap"),
    }


def assert_polling_enabled(html: str, *, job_id: Any, interval: int) -> None:
    attrs = extract_polling_attributes(html)
    assert attrs["hx-get"] == f"/v1/council/jobs/{job_id}/status", (
        f"polling must target R-44 for this job, got {attrs['hx-get']!r}"
    )
    # The exact string the accepted P3.3 evidence also asserts: a static
    # template interval, never a client-computed one.
    assert attrs["hx-trigger"] == f"every {interval}s", (
        f"poll interval must be the server's {interval}s, got {attrs['hx-trigger']!r}"
    )
    assert attrs["hx-swap"] == "outerHTML", (
        f"the whole fragment must be replaced, got {attrs['hx-swap']!r}"
    )
    assert 'data-polling="true"' in html


def assert_polling_absent(html: str) -> None:
    """A terminal job's fragment carries no polling attribute in any form.

    Asserted as absence of the attribute names rather than as a disabled value:
    an `hx-trigger` present but empty is still a browser being handed a polling
    instruction to interpret.
    """
    for attribute in ("hx-get", "hx-trigger", "hx-swap"):
        assert attribute not in html, f"terminal job still carries {attribute}"
    assert 'data-polling="false"' in html


def test_form_field_exactness_and_polling_validators() -> None:
    env = get_jinja_env()
    template = env.get_template("job_status.html")

    confirmable = make_job_view(job_state="completed", with_result=True, with_confirm=True)
    rendered = template.render(view=confirmable, request=make_request())
    values = validate_form_exactness(
        rendered,
        expected_action_pattern=rf"/v1/council/jobs/{confirmable.job_id}/apply",
        expected_named_fields={"csrf_token", "preview_token", "nonce"},
    )
    assert values["preview_token"] == confirmable.confirm.preview_token
    assert values["nonce"] == str(confirmable.job_id)

    cancellable = make_job_view(job_state="queued", cancel_available=True)
    rendered = template.render(view=cancellable, request=make_request())
    validate_form_exactness(
        rendered,
        expected_action_pattern=rf"/v1/council/jobs/{cancellable.job_id}/cancel",
        expected_named_fields={"csrf_token"},
    )
    assert_polling_enabled(
        rendered, job_id=cancellable.job_id, interval=cancellable.poll_after_seconds
    )


def test_falsification_r45_extra_field_fails() -> None:
    html = """
    <form method="post" action="/v1/council/jobs/11111111-1111-1111-1111-111111111111/cancel">
      <input type="hidden" name="csrf_token" value="tok">
      <input type="hidden" name="reason" value="because">
    </form>
    """
    with pytest.raises(AssertionError, match=r"Form named fields mismatch"):
        validate_form_exactness(
            html,
            expected_action_pattern=r"/v1/council/jobs/[^/]+/cancel",
            expected_named_fields={"csrf_token"},
        )


def test_falsification_r46_browser_owned_scope_field_fails() -> None:
    """A checksum in the apply body is browser-owned scope, and is refused here."""
    html = """
    <form method="post" action="/v1/council/jobs/11111111-1111-1111-1111-111111111111/apply">
      <input type="hidden" name="csrf_token" value="tok">
      <input type="hidden" name="preview_token" value="pt">
      <input type="hidden" name="nonce" value="n">
      <input type="hidden" name="checksum_full" value="deadbeef">
    </form>
    """
    with pytest.raises(AssertionError, match=r"Form named fields mismatch"):
        validate_form_exactness(
            html,
            expected_action_pattern=r"/v1/council/jobs/[^/]+/apply",
            expected_named_fields={"csrf_token", "preview_token", "nonce"},
        )


def test_falsification_r46_duplicate_nonce_fails() -> None:
    html = """
    <form method="post" action="/v1/council/jobs/11111111-1111-1111-1111-111111111111/apply">
      <input type="hidden" name="csrf_token" value="tok">
      <input type="hidden" name="preview_token" value="pt">
      <input type="hidden" name="nonce" value="n1">
      <input type="hidden" name="nonce" value="n2">
    </form>
    """
    with pytest.raises(AssertionError, match=r"Duplicate named fields"):
        validate_form_exactness(
            html,
            expected_action_pattern=r"/v1/council/jobs/[^/]+/apply",
            expected_named_fields={"csrf_token", "preview_token", "nonce"},
        )


def test_falsification_r45_wrong_action_fails() -> None:
    html = """
    <form method="post" action="/v1/council/jobs/11111111-1111-1111-1111-111111111111/abort">
      <input type="hidden" name="csrf_token" value="tok">
    </form>
    """
    with pytest.raises(AssertionError, match=r"Form with action matching .* not found"):
        validate_form_exactness(
            html,
            expected_action_pattern=r"/v1/council/jobs/[^/]+/cancel",
            expected_named_fields={"csrf_token"},
        )


def test_falsification_polling_on_a_terminal_fragment_is_rejected() -> None:
    html = '<section data-job-state="completed" data-polling="false" hx-trigger="every 2s"></section>'
    with pytest.raises(AssertionError, match=r"terminal job still carries hx-trigger"):
        assert_polling_absent(html)


def test_falsification_client_computed_poll_interval_is_rejected() -> None:
    job_id = uuid4()
    html = (
        f'<section hx-get="/v1/council/jobs/{job_id}/status" '
        'hx-trigger="every 1s" hx-swap="outerHTML" data-polling="true"></section>'
    )
    with pytest.raises(AssertionError, match=r"poll interval must be the server's 2s"):
        assert_polling_enabled(html, job_id=job_id, interval=2)


# ===========================================================================
# Structural AST checks for post-yield cleanup discipline
# ===========================================================================

@dataclass
class TrackedStep9FixtureState:
    snapshot_ids: set[UUID] = field(default_factory=set)
    job_ids: set[UUID] = field(default_factory=set)


def inspect_step9_cleanup_fixture_ast(func_or_src: Any) -> None:
    """The cleanup must resolve the database **after** the yield, not before.

    A fixture that resolved `migrated_database` before yielding would make every
    test in this module depend on a configured database, including the many that
    need none — and a suite that reports skips where it could have reported
    evidence is a suite nobody can read.
    """
    tree = ast.parse(func_or_src) if isinstance(func_or_src, str) else ast.parse(
        inspect.getsource(func_or_src)
    )
    func_def = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))

    yields = [node for node in ast.walk(func_def) if isinstance(node, ast.Yield)]
    assert len(yields) == 1, "Fixture must contain exactly one yield statement"
    yield_node = yields[0]
    assert isinstance(yield_node.value, ast.Name), "Yield must return the tracked state variable"

    if_nodes = [node for node in ast.walk(func_def) if isinstance(node, ast.If)]
    assert if_nodes, "Fixture must guard database cleanup with an if-statement"
    assert yield_node.lineno < if_nodes[0].lineno, (
        f"Yield at line {yield_node.lineno} must precede guard at line {if_nodes[0].lineno}"
    )

    res_calls = [
        node
        for node in ast.walk(func_def)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "getfixturevalue"
    ]
    assert len(res_calls) == 1, "Fixture must call request.getfixturevalue exactly once"
    res_call = res_calls[0]
    assert yield_node.lineno < res_call.lineno, (
        f"Yield at line {yield_node.lineno} must precede database resolution at line {res_call.lineno}"
    )
    assert (
        len(res_call.args) == 1
        and isinstance(res_call.args[0], ast.Constant)
        and res_call.args[0].value == "migrated_database"
    )

    with_nodes = [node for node in ast.walk(func_def) if isinstance(node, ast.With)]
    assert len(with_nodes) == 2, (
        f"Fixture must contain exactly two with-blocks on engine.begin(), found {len(with_nodes)}"
    )
    first, second = with_nodes
    bound_first = first.items[0].optional_vars.id
    cleaners = {
        node.func.id
        for node in ast.walk(first)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert {"clean_p3_3_tables", "clean_p3_2_tables"} <= cleaners, (
        "both P3.3 and P3.2 table cleaners must run in with-block 1"
    )
    bound_second = second.items[0].optional_vars.id
    assert bound_second != bound_first, "Second with-block must bind a fresh connection"

    loops = [node for node in ast.walk(second) if isinstance(node, ast.For)]
    assert len(loops) >= 2, "Second with-block must iterate tracked snapshot_ids and job_ids"


@pytest.fixture(autouse=True)
def clean_between_step9_cases(request):
    """Guaranteed post-yield teardown, then fresh-connection absence verification.

    Everything Step 9 can create is reachable from a snapshot or a job:
    `clean_p3_3_tables` removes jobs, results, imports, selections and snapshots
    together, and `clean_p3_2_tables` the callers. The second connection then
    re-asks, on a connection that never saw the cleanup transaction, whether the
    specific rows this test created are gone.
    """
    tracked_state = TrackedStep9FixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return

    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_3_tables(connection)
        clean_p3_2_tables(connection)

    with engine.begin() as fresh_conn:
        for snapshot_id in tracked_state.snapshot_ids:
            remaining = fresh_conn.execute(
                text("SELECT count(*) FROM foundry_snapshots WHERE id = :id"),
                {"id": snapshot_id},
            ).scalar_one()
            assert remaining == 0, f"Cleanup failed: snapshot {snapshot_id} still exists"

        for job_id in tracked_state.job_ids:
            for table in ("reconciliation_jobs", "reconciliation_job_results"):
                column = "id" if table == "reconciliation_jobs" else "job_id"
                remaining = fresh_conn.execute(
                    text(f"SELECT count(*) FROM {table} WHERE {column} = :id"),
                    {"id": job_id},
                ).scalar_one()
                assert remaining == 0, f"Cleanup failed: {table} row for {job_id} still exists"


def test_structural_step9_fixture_cleans_after_yield() -> None:
    inspect_step9_cleanup_fixture_ast(clean_between_step9_cases)


def test_falsification_structural_fixture_rejects_resolution_before_yield() -> None:
    bad_code = """
def clean_between_step9_cases(request):
    engine = request.getfixturevalue("migrated_database")
    tracked_state = TrackedStep9FixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    with engine.begin() as connection:
        clean_p3_3_tables(connection)
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        for s in tracked_state.snapshot_ids:
            assert fresh_conn.execute(text("SELECT 1"), {"id": s}).scalar_one() == 0
        for j in tracked_state.job_ids:
            assert fresh_conn.execute(text("SELECT 1"), {"id": j}).scalar_one() == 0
"""
    with pytest.raises(AssertionError, match=r"Yield at line .* must precede database resolution"):
        inspect_step9_cleanup_fixture_ast(bad_code)


# ===========================================================================
# Sample view factory
# ===========================================================================

SAMPLE_CHECKSUM = "b1946ac92492d2347c6235b4d2611184b1946ac92492d2347c6235b4d2611184"
SAMPLE_PREVIEW_TOKEN = "sample-preview-token-digest"
SAMPLE_PROFILE_VERSION = "2026-08-09.1"
SAMPLE_POLL_SECONDS = 2


def make_summary(
    *,
    blocked: int = 0,
    issue_counts: tuple[IssueCount, ...] = (),
    blocked_entries: tuple[BlockedEntry, ...] = (),
) -> ReconciliationSummary:
    return ReconciliationSummary(
        actor_count=32,
        mapped=28,
        unmapped=3,
        blocked=blocked,
        absent=1,
        would_create=3,
        would_update=28,
        issue_counts=issue_counts,
        blocked_entries=blocked_entries,
    )


def make_confirm(
    *,
    blocked: bool = False,
    path_observed: bool = True,
    preview_token: str = SAMPLE_PREVIEW_TOKEN,
) -> ConfirmScope:
    return ConfirmScope(
        preview_token=preview_token,
        checksum_full=SAMPLE_CHECKSUM,
        folder=FolderChoice(
            folder_id=fx.ACTIVE_FOLDER_ID,
            folder_path=SafeText.bounded(FIXTURE_FOLDER_PATH, 120),
            actor_count=32,
            is_default=True,
            path_observed=path_observed,
        ),
        profile_version=SAMPLE_PROFILE_VERSION,
        expires_at=Instant.of(datetime(2026, 9, 20, 18, 30, tzinfo=timezone.utc)),
        would_create=3,
        would_update=28,
        blocked=blocked,
    )


def make_job_view(
    *,
    job_state: str = "queued",
    kind: str = "preview",
    job_id: UUID | None = None,
    progress: JobProgress | None = ...,
    attempts: int = 1,
    with_result: bool = False,
    result: ReconciliationSummary | None = None,
    stale_code: str | None = None,
    failure_code: str | None = None,
    cancel_available: bool = False,
    with_confirm: bool = False,
    confirm: ConfirmScope | None = None,
    csrf_token: str = "sample_csrf_token",
    poll_after_seconds: int = SAMPLE_POLL_SECONDS,
) -> JobStatusView:
    """One VM-15 in a chosen state, built the way the service builds it.

    `progress` defaults to the service's own rule — a step for a live job and
    `None` for a terminal one — so a caller that does not care about progress
    gets a view production could actually produce, and a caller that does care
    passes one explicitly.
    """
    identifier = job_id or uuid4()
    if progress is ...:
        progress = (
            JobProgress(
                step="queued" if job_state == "queued" else "parsing",
                percent=None,
                updated_at=Instant.of(datetime(2026, 8, 21, 10, 0, tzinfo=timezone.utc)),
            )
            if job_state in LIVE_JOB_STATES
            else None
        )
    page_state = {
        "queued": "loading",
        "running": "loading",
        "stale": "stale",
        "failed": "error",
    }.get(job_state, "ready")

    return JobStatusView(
        state=page_state,
        job_id=identifier,
        kind=kind,
        job_state=job_state,
        progress=progress,
        requested_by=Actor(
            account_id=uuid4(),
            label=SafeText.bounded("Council Member", 80),
            capability=ActorCapability.GUILD_COUNCIL,
        ),
        requested_at=Instant.of(datetime(2026, 8, 21, 9, 55, tzinfo=timezone.utc)),
        attempts=attempts,
        poll_after_seconds=poll_after_seconds,
        result=result if result is not None else (make_summary() if with_result else None),
        stale_reason=StaleReason(code=stale_code) if stale_code else None,
        failure=(
            JobFailure(code=failure_code, correlation=Correlation(uuid4()))
            if failure_code
            else None
        ),
        cancel_available=cancel_available,
        confirm=confirm if confirm is not None else (make_confirm() if with_confirm else None),
        csrf_token=csrf_token,
        correlation=Correlation(uuid4()),
    )


def render_page(view: JobStatusView) -> str:
    return get_jinja_env().get_template("job_status.html").render(
        view=view, request=make_request()
    )


def render_fragment(view: JobStatusView) -> str:
    return get_jinja_env().get_template("job_status_fragment.html").render(
        view=view, request=make_request()
    )


# ===========================================================================
# Direct Jinja render evidence — every accepted state
# ===========================================================================

@pytest.mark.parametrize("job_state", ALL_JOB_STATES)
def test_every_accepted_job_state_renders_its_own_identity(job_state: str) -> None:
    """All six of N-27's states render, and each says which it is."""
    view = make_job_view(
        job_state=job_state,
        with_result=job_state in ("completed", "stale"),
        stale_code="folder_changed" if job_state == "stale" else None,
        failure_code="parse_refused" if job_state == "failed" else None,
    )
    rendered = render_page(view)
    assert f'data-job-state="{job_state}"' in rendered
    assert f'data-job-id="{view.job_id}"' in rendered
    assert f'data-attempts="{view.attempts}"' in rendered
    assert f'data-poll-after="{view.poll_after_seconds}"' in rendered
    assert str(view.correlation.id) in rendered


@pytest.mark.parametrize("job_state", LIVE_JOB_STATES)
def test_live_states_poll_on_the_server_interval(job_state: str) -> None:
    view = make_job_view(job_state=job_state, poll_after_seconds=7)
    for rendered in (render_page(view), render_fragment(view)):
        assert_polling_enabled(rendered, job_id=view.job_id, interval=7)
        # The no-JavaScript path exists next to the enhanced one.
        assert 'data-control="manual-refresh"' in rendered
        assert f'href="/v1/council/jobs/{view.job_id}"' in rendered


@pytest.mark.parametrize("job_state", TERMINAL_JOB_STATES)
def test_terminal_states_carry_no_polling_and_no_refresh_control(job_state: str) -> None:
    """A settled job is not a question worth asking every two seconds forever."""
    view = make_job_view(
        job_state=job_state,
        with_result=job_state in ("completed", "stale"),
        stale_code="preview_expired" if job_state == "stale" else None,
        failure_code="timeout" if job_state == "failed" else None,
    )
    for rendered in (render_page(view), render_fragment(view)):
        assert_polling_absent(rendered)
        assert 'data-control="manual-refresh"' not in rendered


def test_a_terminal_state_says_that_nothing_was_applied() -> None:
    """Stale, failed and cancelled each say it, rather than leaving it inferred."""
    for view in (
        make_job_view(job_state="stale", stale_code="snapshot_changed", with_result=True),
        make_job_view(job_state="failed", failure_code="attempts_exhausted"),
        make_job_view(job_state="cancelled"),
    ):
        rendered = render_fragment(view)
        assert "Nothing was applied" in rendered, view.job_state


def test_stale_and_failure_render_only_their_closed_vocabulary_code() -> None:
    stale = make_job_view(job_state="stale", stale_code="aggregate_version_changed")
    rendered = render_fragment(stale)
    assert 'data-field="stale-reason"' in rendered
    assert 'data-code="aggregate_version_changed"' in rendered

    failed = make_job_view(job_state="failed", failure_code="artifact_unavailable")
    rendered = render_fragment(failed)
    assert 'data-field="failure"' in rendered
    assert 'data-code="artifact_unavailable"' in rendered
    assert str(failed.failure.correlation.id) in rendered


def test_progress_without_a_percent_is_indeterminate_and_labelled() -> None:
    """`percent is None` is the production case, and it must not be invented."""
    view = make_job_view(
        job_state="running",
        progress=JobProgress(
            step="parsing",
            percent=None,
            updated_at=Instant.of(datetime(2026, 8, 21, 10, 5, tzinfo=timezone.utc)),
        ),
    )
    rendered = render_fragment(view)
    assert 'data-field="progress"' in rendered
    assert 'data-step="parsing"' in rendered
    # Empty, because there is no percent — not `0`, which would be a claim.
    assert 'data-percent=""' in rendered
    # An indeterminate <progress> carries no value attribute at all.
    indeterminate = re.search(r"<progress\b([^>]*)>", rendered)
    assert indeterminate is not None, "an indeterminate progress element must be present"
    assert "value=" not in indeterminate.group(1)
    assert "aria-label=" in indeterminate.group(1)
    assert "%" not in rendered.split('data-field="progress"')[1].split("</p>")[0]


def test_progress_with_a_real_percent_is_bounded_and_labelled() -> None:
    """The branch VM-15 permits, asserted rather than assumed unreachable."""
    view = make_job_view(
        job_state="running",
        progress=JobProgress(
            step="reconciling",
            percent=42,
            updated_at=Instant.of(datetime(2026, 8, 21, 10, 6, tzinfo=timezone.utc)),
        ),
    )
    rendered = render_fragment(view)
    assert 'data-percent="42"' in rendered
    element = re.search(r"<progress\b([^>]*)>", rendered)
    assert element is not None
    assert 'value="42"' in element.group(1)
    assert 'max="100"' in element.group(1)
    assert "aria-label=" in element.group(1)
    assert "42% complete" in rendered


def test_the_confirmation_control_appears_only_when_the_view_carries_a_scope() -> None:
    """`confirm` decides it. `kind`, `job_state` and the counts do not.

    The negative half is the one that matters: a completed preview **with a
    result and would-create counts** but no `ConfirmScope` is exactly the shape a
    template would be tempted to infer confirmability from, and it must render no
    apply form at all.
    """
    confirmable = make_job_view(job_state="completed", with_result=True, with_confirm=True)
    rendered = render_fragment(confirmable)
    assert 'data-control="confirm"' in rendered
    assert f'action="/v1/council/jobs/{confirmable.job_id}/apply"' in rendered

    not_confirmable = make_job_view(job_state="completed", with_result=True, with_confirm=False)
    rendered = render_fragment(not_confirmable)
    assert 'data-control="confirm"' not in rendered
    assert "/apply" not in rendered
    # …and the result it does have is still rendered, so the absence is the
    # control's, not the whole summary's.
    assert 'data-field="summary"' in rendered


def test_an_apply_job_is_not_a_confirmable_preview() -> None:
    """Kind is presentation; confirmability is the server's decision."""
    apply_job = make_job_view(kind="apply", job_state="completed", with_result=True)
    rendered = render_fragment(apply_job)
    assert 'data-job-kind="apply"' in rendered
    assert "Import apply" in rendered
    assert 'data-control="confirm"' not in rendered

    preview = make_job_view(kind="preview", job_state="completed", with_result=True, with_confirm=True)
    rendered = render_fragment(preview)
    assert 'data-job-kind="preview"' in rendered
    assert "Import preview" in rendered
    assert 'data-control="confirm"' in rendered


def test_the_cancel_control_appears_only_when_the_view_allows_it() -> None:
    available = make_job_view(job_state="running", cancel_available=True)
    rendered = render_fragment(available)
    assert 'data-control="cancel"' in rendered
    assert f'action="/v1/council/jobs/{available.job_id}/cancel"' in rendered

    unavailable = make_job_view(job_state="running", cancel_available=False)
    rendered = render_fragment(unavailable)
    assert 'data-control="cancel"' not in rendered
    assert "/cancel" not in rendered


def test_the_bounded_summary_renders_every_accepted_count() -> None:
    summary = make_summary(
        blocked=2,
        issue_counts=(
            IssueCount(code="unmapped_name_collision", severity="error", count=2),
            IssueCount(code="portrait_missing", severity="warning", count=5),
        ),
        blocked_entries=(
            BlockedEntry(
                external_actor_id="A" * 16,
                display_name=SafeText.bounded("Alia of the Vale", 120),
                issue_code="unmapped_name_collision",
                candidate_character_ids=(uuid4(), uuid4()),
            ),
        ),
    )
    view = make_job_view(job_state="completed", result=summary)
    rendered = render_fragment(view)

    for count_name, value in (
        ("actor_count", 32),
        ("mapped", 28),
        ("unmapped", 3),
        ("blocked", 2),
        ("absent", 1),
        ("would_create", 3),
        ("would_update", 28),
    ):
        assert f'data-count="{count_name}"' in rendered, count_name
        assert str(value) in rendered

    assert 'data-issue-code="unmapped_name_collision"' in rendered
    assert 'data-severity="error"' in rendered
    assert 'data-issue-code="portrait_missing"' in rendered
    assert 'data-severity="warning"' in rendered
    assert 'data-field="blocked-entries"' in rendered
    assert "Alia of the Vale" in rendered
    assert 'data-candidate-count="2"' in rendered


def test_a_bounded_actor_name_states_that_it_was_truncated() -> None:
    """§3.2's 120 characters, and the cut said out loud rather than hidden."""
    entry = BlockedEntry(
        external_actor_id="B" * 16,
        display_name=SafeText.bounded("n" * 400, 120),
        issue_code="unmapped_name_collision",
        candidate_character_ids=(),
    )
    assert entry.display_name.truncated is True
    view = make_job_view(job_state="completed", result=make_summary(blocked=1, blocked_entries=(entry,)))
    rendered = render_fragment(view)
    assert 'data-truncated="true"' in rendered
    assert "&hellip;" in rendered
    assert "n" * 400 not in rendered


def test_the_confirmation_scope_shows_what_is_being_committed() -> None:
    view = make_job_view(job_state="completed", with_result=True, with_confirm=True)
    rendered = render_fragment(view)

    assert f'data-checksum="{SAMPLE_CHECKSUM}"' in rendered
    assert f'data-folder-id="{fx.ACTIVE_FOLDER_ID}"' in rendered
    assert f'data-profile-version="{SAMPLE_PROFILE_VERSION}"' in rendered
    assert FIXTURE_FOLDER_PATH in rendered
    assert view.confirm.expires_at.display in rendered
    assert 'data-field="confirm-would-create"' in rendered
    assert 'data-field="confirm-would-update"' in rendered
    assert 'data-blocked="false"' in rendered
    # The token is a hidden form value and never presented as readable text.
    assert f'name="preview_token" value="{SAMPLE_PREVIEW_TOKEN}"' in rendered
    assert f">{SAMPLE_PREVIEW_TOKEN}<" not in rendered


def test_an_unobserved_confirmation_folder_renders_as_an_identifier() -> None:
    """`path_observed` honesty survives into the confirmation, where it matters most."""
    view = make_job_view(
        job_state="completed",
        with_result=True,
        confirm=make_confirm(path_observed=False),
    )
    rendered = render_fragment(view)
    assert 'data-path-observed="false"' in rendered
    assert "path awaiting preview" in rendered


def test_a_blocking_result_explains_the_refusal_and_offers_no_override() -> None:
    view = make_job_view(
        job_state="completed",
        result=make_summary(blocked=4),
        confirm=make_confirm(blocked=True),
    )
    rendered = render_fragment(view)
    assert 'data-blocked="true"' in rendered
    assert 'data-field="blocked-notice"' in rendered
    assert "Applying will refuse" in rendered
    # The form is still exactly three fields: there is no override to send.
    validate_form_exactness(
        rendered,
        expected_action_pattern=rf"/v1/council/jobs/{view.job_id}/apply",
        expected_named_fields={"csrf_token", "preview_token", "nonce"},
    )


# ===========================================================================
# The R-46 nonce: stable by design, and asserted as such
# ===========================================================================

def test_the_apply_nonce_is_the_preview_job_identity_and_is_stable() -> None:
    """R-46 converges; it does not diverge like R-42.

    One completed preview may produce only one durable effect, so every
    resubmission of this form — a double-click, a retried lost response, a second
    browser — must carry the identical request identity. Re-rendering the same
    job must therefore reproduce the same value, which is the property a
    per-render mint would destroy.
    """
    view = make_job_view(job_state="completed", with_result=True, with_confirm=True)
    first = validate_form_exactness(
        render_fragment(view),
        expected_action_pattern=rf"/v1/council/jobs/{view.job_id}/apply",
        expected_named_fields={"csrf_token", "preview_token", "nonce"},
    )
    second = validate_form_exactness(
        render_fragment(view),
        expected_action_pattern=rf"/v1/council/jobs/{view.job_id}/apply",
        expected_named_fields={"csrf_token", "preview_token", "nonce"},
    )
    assert first["nonce"] == second["nonce"] == str(view.job_id)


def test_two_different_previews_carry_two_different_apply_nonces() -> None:
    """Stable is not constant: the identity is *this* preview's, not a literal."""
    one = make_job_view(job_state="completed", with_result=True, with_confirm=True)
    other = make_job_view(job_state="completed", with_result=True, with_confirm=True)
    assert one.job_id != other.job_id

    values = []
    for view in (one, other):
        values.append(
            validate_form_exactness(
                render_fragment(view),
                expected_action_pattern=rf"/v1/council/jobs/{view.job_id}/apply",
                expected_named_fields={"csrf_token", "preview_token", "nonce"},
            )["nonce"]
        )
    assert values[0] != values[1]
    assert values == [str(one.job_id), str(other.job_id)]


def test_falsification_a_randomised_apply_nonce_would_be_caught() -> None:
    """The guard that fails if Step 8's per-render R-42 mint is copied into R-46.

    Two renders of one preview are simulated with two freshly minted values —
    which is exactly what a per-render nonce would produce — and run through the
    same extractor and the same assertion the positive test uses.
    """
    job_id = uuid4()

    def render_with(nonce: str) -> str:
        return f"""
        <form method="post" action="/v1/council/jobs/{job_id}/apply">
          <input type="hidden" name="csrf_token" value="tok">
          <input type="hidden" name="preview_token" value="pt">
          <input type="hidden" name="nonce" value="{nonce}">
        </form>
        """

    fields = {"csrf_token", "preview_token", "nonce"}
    pattern = rf"/v1/council/jobs/{job_id}/apply"
    first = validate_form_exactness(
        render_with(str(uuid4())), expected_action_pattern=pattern, expected_named_fields=fields
    )["nonce"]
    second = validate_form_exactness(
        render_with(str(uuid4())), expected_action_pattern=pattern, expected_named_fields=fields
    )["nonce"]

    with pytest.raises(AssertionError, match=r"apply nonce must be the preview job identity"):
        assert first == second == str(job_id), (
            "apply nonce must be the preview job identity, stable across renders"
        )


# ===========================================================================
# Client-side authority, escaping and disclosure
# ===========================================================================

@pytest.mark.parametrize("template_name", ["job_status.html", "job_status_fragment.html"])
def test_step_9_templates_contain_no_script_or_client_authority(template_name: str) -> None:
    """HTMX enhances polling. It is not authorization and it is not scripting."""
    source = (TEMPLATE_ROOT / template_name).read_text(encoding="utf-8").lower()
    active = strip_jinja_comments(source)
    for marker in FORBIDDEN_SCRIPT_MARKERS:
        assert marker not in active, f"{template_name} contains forbidden marker {marker!r}"


@pytest.mark.parametrize("template_name", ["job_status.html", "job_status_fragment.html"])
def test_step_9_templates_reference_no_remote_origin(template_name: str) -> None:
    source = (TEMPLATE_ROOT / template_name).read_text(encoding="utf-8").lower()
    for marker in ("http://", "https://", "//cdn.", "cdn.jsdelivr", "unpkg.com", "@import url("):
        assert marker not in strip_jinja_comments(source), (
            f"{template_name} references a remote origin via {marker!r}"
        )


def test_adversarial_escaping_in_every_external_context() -> None:
    """Every value that can carry hostile text, at its worst, in one render."""
    payload = '<script>alert("xss")</script><img src=x onerror=alert(1)>"\'&<>{{7*7}}'
    entry = BlockedEntry(
        external_actor_id=f"actor_{payload}",
        display_name=SafeText.bounded(f"Name {payload}", 120),
        issue_code=f"issue_{payload}",
        candidate_character_ids=(),
    )
    confirm = ConfirmScope(
        preview_token=f"token_{payload}",
        checksum_full=f"checksum_{payload}",
        folder=FolderChoice(
            folder_id=f"folder_{payload}",
            folder_path=SafeText.bounded(f"/Actors/{payload}", 120),
            actor_count=1,
            is_default=True,
            path_observed=True,
        ),
        profile_version=f"profile_{payload}",
        expires_at=Instant.of(datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)),
        would_create=1,
        would_update=0,
        blocked=True,
    )
    view = make_job_view(
        job_state="completed",
        result=make_summary(
            blocked=1,
            issue_counts=(IssueCount(code=f"code_{payload}", severity="error", count=1),),
            blocked_entries=(entry,),
        ),
        confirm=confirm,
        csrf_token=f"csrf_{payload}",
        cancel_available=True,
    )
    view = dataclasses.replace(
        view,
        requested_by=Actor(
            account_id=uuid4(),
            label=SafeText.bounded(f"Actor {payload}", 80),
            capability=ActorCapability.GUILD_COUNCIL,
        ),
    )
    rendered = render_page(view)

    # No element from the value. The escaped text is inert and is expected to be
    # present; what must not be present is markup.
    assert "<script>alert" not in rendered
    assert "<img src=x" not in rendered
    assert "&lt;script&gt;alert" in rendered
    assert "&lt;img src=x" in rendered
    # Jinja escapes output; it does not re-parse it as source.
    assert "{{7*7}}" in rendered
    # Nothing broke out of an attribute into a new one.
    assert rendered.count("<form") == rendered.count("</form>")
    assert rendered.count("<section") == rendered.count("</section>")


def test_falsification_unescaped_payload_would_be_caught() -> None:
    raw = '<div data-field="failure"><script>alert(1)</script></div>'
    with pytest.raises(AssertionError, match=r"Raw script tag found unescaped"):
        assert "<script>alert" not in raw, "Raw script tag found unescaped"


def test_no_artifact_download_or_raw_disclosure_surface_exists() -> None:
    """The checksum names a document a Council member cannot download."""
    view = make_job_view(
        job_state="completed",
        with_result=True,
        with_confirm=True,
        cancel_available=False,
    )
    rendered = render_page(view)
    for forbidden in ("/artifact", "/download", "Traceback", ".ndjson", ".zip", "/var/", "/opt/"):
        assert forbidden not in rendered, f"{forbidden!r} reachable from the job page"


def test_the_page_title_carries_no_job_identity() -> None:
    """A UUID has no business in a tab title, a history entry or a screenshot."""
    view = make_job_view(job_state="running")
    rendered = render_page(view)
    title = re.search(r"<title>(.*?)</title>", rendered, flags=re.DOTALL)
    assert title is not None
    assert str(view.job_id) not in title.group(1)


# ===========================================================================
# Integrity and digest verification
# ===========================================================================

def test_template_digests_match_implementation_corpus() -> None:
    found = {
        p.name: compute_sha256(p)
        for p in TEMPLATE_ROOT.glob("*.html")
        if p.name != "base.html" and not p.name.startswith(".")
    }
    assert set(found) == set(P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS)
    for name, expected in P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS.items():
        assert found[name] == expected, f"Digest mismatch for template '{name}'"


def test_asset_integrity_manifest_verification() -> None:
    """Step 9 adds no asset, so the accepted three must still verify byte for byte."""
    assert MANIFEST_PATH.exists(), "Manifest file asset-integrity.sha256 missing"
    lines = [
        line.strip()
        for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert len(lines) == 3
    for line in lines:
        digest, rel_path = line.split()
        target = ROOT / rel_path
        assert target.is_file(), f"Asset '{rel_path}' missing"
        assert compute_sha256(target) == digest, f"Asset integrity failure for {rel_path}"


def test_step_9_selectors_used_and_prohibited_excluded() -> None:
    """Every class the Step 9 templates emit is defined; no later-step selector exists."""
    css_files = list((STATIC_ROOT / "css").glob("freedom-blades.*.css"))
    assert len(css_files) == 1
    active_css = extract_active_css_classes(css_files[0].read_text(encoding="utf-8"))

    template_texts = [
        (TEMPLATE_ROOT / "job_status.html").read_text(encoding="utf-8"),
        (TEMPLATE_ROOT / "job_status_fragment.html").read_text(encoding="utf-8"),
    ]
    used = extract_active_template_classes(template_texts)

    for selector in sorted(used):
        assert selector in active_css, f"Template class '{selector}' not defined in stylesheet"
    for selector in STEP_9_SELECTORS:
        assert selector in active_css, f"Accepted Step 9 selector '{selector}' missing from CSS"
        assert selector in used, f"Accepted Step 9 selector '{selector}' unused by the templates"
    for prohibited in PROHIBITED_STEP_9_SELECTORS:
        assert prohibited not in active_css, f"Prohibited selector '{prohibited}' found in stylesheet"


def test_falsification_a_class_absent_from_the_stylesheet_is_rejected() -> None:
    css = ".card{color:red}"
    active_css = extract_active_css_classes(css)
    used = extract_active_template_classes(['<div class="card invented-component"></div>'])
    missing = sorted(sel for sel in used if sel not in active_css)
    assert missing == [".invented-component"]


def test_falsification_class_extraction_keeps_both_branches_of_a_conditional() -> None:
    """The bug the space-substitution avoids, asserted as a property."""
    template = '<span class="badge {% if x %}badge-danger{% else %}badge-warning{% endif %} badge-sm">'
    used = extract_active_template_classes([template])
    assert {".badge", ".badge-danger", ".badge-warning", ".badge-sm"} == used
    assert ".badge-dangerbadge-warning" not in used


# ===========================================================================
# Database-backed HTTP evidence
# ===========================================================================

requires_database = pytest.mark.skipif(
    "TEST_DATABASE_URL" not in os.environ,
    reason="TEST_DATABASE_URL is not configured for a disposable PostgreSQL database.",
)

LIVE_PREVIEW_TOKEN = "live-token"

#: The exact append-only action names the P3.3 services record, read from
#: `application/web/jobs.py` rather than guessed. A cardinality assertion against
#: an action nobody writes counts zero twice and passes for the wrong reason.
APPLY_REQUESTED = "reconciliation.apply_requested"
CANCEL_REQUESTED = "reconciliation.job_cancel_requested"
PREVIEW_QUEUED = "reconciliation.job_queued"


def post(client, settings, caller, path, body: str = "", *, headers=None, content=None):
    """One mutation, built from the route table rather than from a rendered page.

    Route contract §2.2's rule, kept in the helper so no case can quietly forget
    it: a success must not depend on a control having been rendered any more than
    a refusal must depend on one not having been.
    """
    request_headers = {"Origin": settings.public_origin, "Content-Type": FORM}
    if headers is not None:
        request_headers = headers
    if content is None:
        content = f"csrf_token={csrf_token_for(settings, caller)}"
        if body:
            content = f"{content}&{body}"
    return client.post(
        path, cookies=caller.cookies(settings), headers=request_headers, content=content
    )


def count_audit(engine, action: str, entity_id: Any) -> int:
    with engine.begin() as connection:
        return connection.execute(
            text("SELECT count(*) FROM audit_events WHERE action = :a AND entity_id = :e"),
            {"a": action, "e": str(entity_id)},
        ).scalar_one()


def apply_jobs_for(engine, snapshot_id: UUID) -> list[dict[str, Any]]:
    with engine.begin() as connection:
        return [
            dict(row)
            for row in connection.execute(
                text(
                    "SELECT id, state, parent_job_id, request_key FROM reconciliation_jobs "
                    "WHERE snapshot_id = :s AND kind = 'apply' ORDER BY queued_at"
                ),
                {"s": snapshot_id},
            ).mappings()
        ]


def job_row(engine, job_id: UUID) -> dict[str, Any]:
    with engine.begin() as connection:
        return dict(
            connection.execute(
                text(
                    "SELECT state, stale_reason, failure_code, finished_at, "
                    "cancel_requested_at, effect_committed_at "
                    "FROM reconciliation_jobs WHERE id = :id"
                ),
                {"id": job_id},
            )
            .mappings()
            .one()
        )


@pytest.fixture()
def step9_world(migrated_database, settings, clean_between_step9_cases):
    """A snapshot with a selected folder, a confirmable preview and a live job.

    Everything created here is tracked, so the autouse fixture can prove after
    the yield that each row is gone from a connection that never saw the cleanup.
    """
    tracked: TrackedStep9FixtureState = clean_between_step9_cases
    callers = seed_callers(migrated_database, settings)
    with migrated_database.begin() as connection:
        snapshot_id, checksum = seed_snapshot(
            connection, folder_ids=(fx.ACTIVE_FOLDER_ID, fx.ARCHIVE_FOLDER_ID)
        )
        tracked.snapshot_ids.add(snapshot_id)
        select_folder(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["A"].account_id,
            folder_id=fx.ACTIVE_FOLDER_ID,
        )
        preview_id, result_id = complete_preview(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            preview_token=LIVE_PREVIEW_TOKEN,
        )
        tracked.job_ids.add(preview_id)
        queued_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            state=JobState.QUEUED,
        )
        tracked.job_ids.add(queued_id)
    return {
        "callers": callers,
        "tracked": tracked,
        "snapshot_id": snapshot_id,
        "checksum": checksum,
        "preview_job_id": preview_id,
        "result_id": result_id,
        "queued_job_id": queued_id,
    }


# -- R-43 and R-44: reads ---------------------------------------------------

@requires_database
@pytest.mark.database
async def test_r43_and_r44_caller_matrices(client, settings, step9_world) -> None:
    """Every cell of §6.2 for both reads, issued directly at the route.

    No case fetches R-43 before R-44 or before a mutation: the guard is what
    refuses, and a suite that navigated first would be testing the template.
    """
    callers = step9_world["callers"]
    job_id = step9_world["queued_job_id"]

    for role, expected in ACCEPTED_ROUTE_CALLER_MATRIX["R-43"].items():
        response = await client.get(
            f"/v1/council/jobs/{job_id}",
            cookies=callers[role].cookies(settings) if role != "U" else {},
        )
        assert response.status_code == expected, (
            f"R-43 caller {role}: expected {expected}, got {response.status_code}"
        )
        if role == "U":
            assert response.headers["location"] == "/v1/login"

    for role, expected in ACCEPTED_ROUTE_CALLER_MATRIX["R-44"].items():
        response = await client.get(
            f"/v1/council/jobs/{job_id}/status",
            cookies=callers[role].cookies(settings) if role != "U" else {},
        )
        assert response.status_code == expected, (
            f"R-44 caller {role}: expected {expected}, got {response.status_code}"
        )
        if role == "U":
            # A fragment, so an absent session is 401 and not a redirect: a 303
            # swapped into the fragment target would render login inside the job.
            assert "location" not in response.headers


@requires_database
@pytest.mark.database
async def test_a_council_member_may_read_a_job_another_council_member_requested(
    client, settings, step9_world
) -> None:
    """Council reach is role-derived (OD-37); import work is Council-wide business."""
    callers = step9_world["callers"]
    job_id = step9_world["queued_job_id"]  # requested by C

    other = await client.get(
        f"/v1/council/jobs/{job_id}", cookies=callers["CA"].cookies(settings)
    )
    assert other.status_code == 200
    assert f'data-job-id="{job_id}"' in other.text

    # And a member who is not Council learns nothing at all from possessing it.
    member = await client.get(
        f"/v1/council/jobs/{job_id}", cookies=callers["M"].cookies(settings)
    )
    assert member.status_code == 403


@requires_database
@pytest.mark.database
async def test_a_job_uuid_is_worth_nothing_to_a_non_council_caller(
    client, settings, step9_world
) -> None:
    """`403` before the object is read, so timing discloses nothing either.

    The real job's id and an id that names nothing must be answered identically
    to a caller who is not Council — otherwise the refusal is an existence
    oracle for anybody holding a UUID.
    """
    callers = step9_world["callers"]
    real = step9_world["queued_job_id"]
    absent = uuid4()

    for role in ("M", "A", "BG", "AC"):
        first = await client.get(
            f"/v1/council/jobs/{real}/status", cookies=callers[role].cookies(settings)
        )
        second = await client.get(
            f"/v1/council/jobs/{absent}/status", cookies=callers[role].cookies(settings)
        )
        assert first.status_code == second.status_code == 403, role
        assert first.content == second.content, f"{role} can distinguish a real job from an absent one"


@requires_database
@pytest.mark.database
async def test_two_unreachable_job_identifiers_are_answered_identically(
    client, settings, step9_world
) -> None:
    """The enumeration property, stated as the thing it actually protects.

    **Not** "malformed and absent are byte-identical." They are not, and the
    accepted backend behaviour is deliberate: a value that is not a UUID never
    reached the repository, and is refused by the parse with
    `object_not_reachable`, while a well-formed id that names nothing is refused
    by the read with `snapshot_absent`. Neither answer varies with *which*
    well-formed id was asked about, which is the only thing an enumerator can
    use — so the assertion is that two different absent ids are indistinguishable
    from each other, and that both refusals carry the accepted denial headers and
    disclose nothing else.
    """
    council = step9_world["callers"]["C"]

    first_absent = await client.get(
        f"/v1/council/jobs/{uuid4()}/status", cookies=council.cookies(settings)
    )
    second_absent = await client.get(
        f"/v1/council/jobs/{uuid4()}/status", cookies=council.cookies(settings)
    )
    assert_identical_denial_responses(first_absent, second_absent)
    assert first_absent.json()["error"] == "snapshot_absent"

    malformed = await client.get(
        "/v1/council/jobs/not-a-uuid/status", cookies=council.cookies(settings)
    )
    assert malformed.status_code == 404
    assert malformed.json()["error"] == "object_not_reachable"
    for header, expected in EXACT_DENIAL_HEADERS.items():
        assert malformed.headers[header] == expected, header
    for forbidden in FORBIDDEN_DENIAL_HEADERS:
        assert forbidden not in malformed.headers

    # The navigable route answers VM-22 HTML, and there the two **are**
    # byte-identical: `denied.html` prints a category and nothing else, so a
    # malformed id and an absent one produce the same page.
    page_malformed = await client.get(
        "/v1/council/jobs/not-a-uuid", cookies=council.cookies(settings)
    )
    page_absent = await client.get(
        f"/v1/council/jobs/{uuid4()}", cookies=council.cookies(settings)
    )
    assert page_malformed.status_code == page_absent.status_code == 404
    assert page_malformed.content == page_absent.content
    # And a correlation id — which differs per request — is not printed, because
    # printing one would make the two distinguishable by exactly what it varies.
    assert b"correlation" not in page_malformed.content.lower()


@requires_database
@pytest.mark.database
async def test_the_live_fragment_polls_on_the_server_interval_and_says_so_twice(
    client, settings, step9_world
) -> None:
    """`Retry-After` and the markup agree, because a browser honours both."""
    council = step9_world["callers"]["C"]
    floor = settings.bounds.poll_min_seconds
    assert floor >= 2, "N-22's accepted floor"

    response = await client.get(
        f"/v1/council/jobs/{step9_world['queued_job_id']}/status",
        cookies=council.cookies(settings),
    )
    assert response.status_code == 200
    assert int(response.headers["Retry-After"]) == floor
    assert_polling_enabled(
        response.text, job_id=step9_world["queued_job_id"], interval=floor
    )
    assert f'data-poll-after="{floor}"' in response.text


@requires_database
@pytest.mark.database
async def test_polling_stops_when_the_job_reaches_a_terminal_state(
    client, settings, migrated_database, step9_world
) -> None:
    """The transition itself, observed through two real responses.

    The same job is read while `queued` and again after it has been cancelled, so
    the evidence is that polling *stops* rather than that two different jobs
    render differently.
    """
    council = step9_world["callers"]["C"]
    job_id = step9_world["queued_job_id"]
    floor = settings.bounds.poll_min_seconds

    live = await client.get(
        f"/v1/council/jobs/{job_id}/status", cookies=council.cookies(settings)
    )
    assert_polling_enabled(live.text, job_id=job_id, interval=floor)

    cancelled = await post(client, settings, council, f"/v1/council/jobs/{job_id}/cancel")
    assert cancelled.status_code == 303

    settled = await client.get(
        f"/v1/council/jobs/{job_id}/status", cookies=council.cookies(settings)
    )
    assert settled.status_code == 200
    assert 'data-job-state="cancelled"' in settled.text
    assert_polling_absent(settled.text)
    # The page R-43 renders agrees with the fragment R-44 answers.
    page = await client.get(
        f"/v1/council/jobs/{job_id}", cookies=council.cookies(settings)
    )
    assert_polling_absent(page.text)


@requires_database
@pytest.mark.database
async def test_a_completed_preview_renders_its_bounded_summary_and_confirm_control(
    client, settings, migrated_database, step9_world
) -> None:
    """The rendered page, from real rows, with nothing artifact-derived in it."""
    council = step9_world["callers"]["C"]
    tracked = step9_world["tracked"]

    with migrated_database.begin() as connection:
        job_id, _ = complete_preview(
            connection,
            snapshot_id=step9_world["snapshot_id"],
            account_id=council.account_id,
            checksum=step9_world["checksum"],
            preview_token="bounded-token",
            summary_overrides={
                "issue_counts": [
                    {"code": "unmapped_name_collision", "severity": "error", "count": 2}
                ]
            },
            blocked_entries=[
                {
                    "external_actor_id": "A" * 16,
                    "display_name": "Alia of the Vale",
                    "issue_code": "unmapped_name_collision",
                    "candidate_character_ids": [],
                }
            ],
        )
        tracked.job_ids.add(job_id)

    response = await client.get(
        f"/v1/council/jobs/{job_id}", cookies=council.cookies(settings)
    )
    assert response.status_code == 200
    assert 'data-job-state="completed"' in response.text
    assert 'data-field="summary"' in response.text
    assert 'data-issue-code="unmapped_name_collision"' in response.text
    assert 'data-severity="error"' in response.text
    assert "Alia of the Vale" in response.text
    assert 'data-control="confirm"' in response.text
    assert_polling_absent(response.text)

    # The exact successful body field set, from the response the browser got.
    values = validate_form_exactness(
        response.text,
        expected_action_pattern=rf"/v1/council/jobs/{job_id}/apply",
        expected_named_fields={"csrf_token", "preview_token", "nonce"},
    )
    assert values["nonce"] == str(job_id), "the apply nonce is the preview job identity"
    assert values["preview_token"] == "bounded-token"

    for forbidden in ("/artifact", "/download", "Traceback", "/opt/", ".ndjson"):
        assert forbidden not in response.text, forbidden


# -- R-45: cancellation -----------------------------------------------------

@requires_database
@pytest.mark.database
async def test_r45_caller_matrix(client, settings, migrated_database, step9_world) -> None:
    """Every cell, each against a job of its own so a success cannot mask a refusal."""
    callers = step9_world["callers"]
    tracked = step9_world["tracked"]

    for role, expected in ACCEPTED_ROUTE_CALLER_MATRIX["R-45"].items():
        with migrated_database.begin() as connection:
            job_id = seed_job(
                connection,
                snapshot_id=step9_world["snapshot_id"],
                account_id=callers["C"].account_id,
                checksum=step9_world["checksum"],
                state=JobState.QUEUED,
            )
            tracked.job_ids.add(job_id)

        path = f"/v1/council/jobs/{job_id}/cancel"
        if role == "U":
            response = await client.post(
                path, headers={"Origin": settings.public_origin, "Content-Type": FORM}, content=""
            )
        else:
            response = await post(client, settings, callers[role], path)
        assert response.status_code == expected, (
            f"R-45 caller {role}: expected {expected}, got {response.status_code}"
        )

        # A refused cancellation changed nothing.
        if expected != 303:
            assert job_row(migrated_database, job_id)["state"] == "queued", role


@requires_database
@pytest.mark.database
async def test_r45_refuses_a_request_that_fails_any_transport_control(
    client, settings, migrated_database, step9_world
) -> None:
    """CSRF, Origin, content type and the accepted 4 KiB body bound."""
    council = step9_world["callers"]["C"]
    job_id = step9_world["queued_job_id"]
    path = f"/v1/council/jobs/{job_id}/cancel"

    missing_csrf = await client.post(
        path,
        cookies=council.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content="",
    )
    assert missing_csrf.status_code == 403
    assert missing_csrf.json()["error"] == "csrf_invalid"

    missing_origin = await client.post(
        path,
        cookies=council.cookies(settings),
        headers={"Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, council)}",
    )
    assert missing_origin.status_code == 403
    assert missing_origin.json()["error"] == "origin_invalid"

    wrong_type = await client.post(
        path,
        cookies=council.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": "application/json"},
        content=b"{}",
    )
    assert wrong_type.status_code == 415

    oversized = "a" * (R45_BODY_BOUND + 1)
    too_large = await client.post(
        path,
        cookies=council.cookies(settings),
        headers={
            "Origin": settings.public_origin,
            "Content-Type": FORM,
            "Content-Length": str(len(oversized)),
        },
        content=oversized,
    )
    assert too_large.status_code == 413

    # Every one of them left the job exactly as it was.
    assert job_row(migrated_database, job_id)["state"] == "queued"


@requires_database
@pytest.mark.database
async def test_a_queued_job_cancels_once_and_audits_once(
    client, settings, migrated_database, step9_world
) -> None:
    """The accepted cancellation, and its audit cardinality under a double-click."""
    council = step9_world["callers"]["C"]
    job_id = step9_world["queued_job_id"]
    path = f"/v1/council/jobs/{job_id}/cancel"

    first = await post(client, settings, council, path)
    assert first.status_code == 303
    assert first.headers["location"] == f"/v1/council/jobs/{job_id}"

    row = job_row(migrated_database, job_id)
    assert row["state"] == "cancelled"
    assert row["finished_at"] is not None
    assert row["effect_committed_at"] is None, "a cancelled job committed nothing"

    audits_after_first = count_audit(migrated_database, CANCEL_REQUESTED, job_id)
    assert audits_after_first == 1, (
        "an accepted cancellation writes exactly one append-only event"
    )

    # The second click. Whatever it answers, it must not cancel a second time or
    # write a second event: the job is already terminal.
    second = await post(client, settings, council, path)
    assert second.status_code in (303, 409)
    assert job_row(migrated_database, job_id)["state"] == "cancelled"
    assert count_audit(migrated_database, CANCEL_REQUESTED, job_id) == audits_after_first


@requires_database
@pytest.mark.database
async def test_a_terminal_job_cannot_be_cancelled_and_says_which_conflict(
    client, settings, migrated_database, step9_world
) -> None:
    """A completed preview is not cancellable, and the page says why (VM-19)."""
    council = step9_world["callers"]["C"]
    preview_id = step9_world["preview_job_id"]

    response = await post(client, settings, council, f"/v1/council/jobs/{preview_id}/cancel")
    assert response.status_code == 409
    assert 'data-state="stale"' in response.text or 'data-conflict=' in response.text
    assert "Nothing was applied" in response.text
    assert job_row(migrated_database, preview_id)["state"] == "completed"

    # The control is not offered on that page either, so the refusal and the
    # rendering agree.
    page = await client.get(
        f"/v1/council/jobs/{preview_id}", cookies=council.cookies(settings)
    )
    assert 'data-control="cancel"' not in page.text


@requires_database
@pytest.mark.database
async def test_a_committed_apply_cannot_be_cancelled_or_rewritten_stale(
    client, settings, migrated_database, step9_world
) -> None:
    """The effect fence, through the route rather than through the repository.

    A `running` apply whose import has already committed is the one case where
    the job's state and the truth disagree: the state says `running`, and the
    truth is that the characters are written. R-45 must refuse it, must not
    change the row, and must not describe it as a cancellation that worked.
    """
    council = step9_world["callers"]["C"]
    tracked = step9_world["tracked"]

    with migrated_database.begin() as connection:
        apply_id = seed_job(
            connection,
            snapshot_id=step9_world["snapshot_id"],
            account_id=council.account_id,
            checksum=step9_world["checksum"],
            kind=JobKind.APPLY,
            state=JobState.RUNNING,
            attempts=1,
            lease_owner="fixture:committed",
            lease_expires_at=datetime.now(timezone.utc) + timedelta(seconds=60),
        )
        tracked.job_ids.add(apply_id)
        # The fence is set the way migration 0013 requires it: the timestamp and
        # the published result move together, because
        # `CHECK ((effect_committed_at IS NULL) = (effect_result IS NULL))` is
        # what stops a row claiming a commit it cannot show.
        connection.execute(
            text(
                "UPDATE reconciliation_jobs SET effect_committed_at = now(), "
                "effect_result = CAST(:payload AS jsonb), version = version + 1 "
                "WHERE id = :id"
            ),
            {
                "id": apply_id,
                "payload": json.dumps({"summary": {"actors": 1}, "blocked_entries": []}),
            },
        )

    before = job_row(migrated_database, apply_id)
    assert before["effect_committed_at"] is not None

    response = await post(client, settings, council, f"/v1/council/jobs/{apply_id}/cancel")
    assert response.status_code == 409

    after = job_row(migrated_database, apply_id)
    assert after["state"] == "running", "a committed apply was not moved by a cancellation"
    assert after["stale_reason"] is None, "a committed apply must not be rewritten stale"
    assert after["effect_committed_at"] == before["effect_committed_at"]
    assert count_audit(migrated_database, CANCEL_REQUESTED, apply_id) == 0


# -- R-46: apply confirmation ----------------------------------------------

@requires_database
@pytest.mark.database
async def test_r46_caller_matrix(client, settings, migrated_database, step9_world) -> None:
    """Every cell, each against its own completed preview.

    A fresh preview per caller, because a permitted cell **enqueues** and the
    one-live-apply fence would otherwise turn the second success into a `409`
    and make the matrix read as a refusal it is not.
    """
    callers = step9_world["callers"]
    tracked = step9_world["tracked"]

    for role, expected in ACCEPTED_ROUTE_CALLER_MATRIX["R-46"].items():
        with migrated_database.begin() as connection:
            snapshot_id, checksum = seed_snapshot(connection, payload=f"matrix-{role}".encode())
            tracked.snapshot_ids.add(snapshot_id)
            select_folder(
                connection,
                snapshot_id=snapshot_id,
                account_id=callers["A"].account_id,
                folder_id=fx.ACTIVE_FOLDER_ID,
            )
            preview_id, _ = complete_preview(
                connection,
                snapshot_id=snapshot_id,
                account_id=callers["C"].account_id,
                checksum=checksum,
                preview_token=LIVE_PREVIEW_TOKEN,
            )
            tracked.job_ids.add(preview_id)

        path = f"/v1/council/jobs/{preview_id}/apply"
        body = f"preview_token={LIVE_PREVIEW_TOKEN}&nonce={preview_id}"
        if role == "U":
            response = await client.post(
                path,
                headers={"Origin": settings.public_origin, "Content-Type": FORM},
                content=body,
            )
        else:
            response = await post(client, settings, callers[role], path, body)
        assert response.status_code == expected, (
            f"R-46 caller {role}: expected {expected}, got {response.status_code}"
        )

        applies = apply_jobs_for(migrated_database, snapshot_id)
        if expected == 303:
            assert len(applies) == 1, f"{role} was permitted and must have enqueued exactly one apply"
            tracked.job_ids.add(applies[0]["id"])
        else:
            assert applies == [], f"{role} was refused and must have enqueued nothing"


@requires_database
@pytest.mark.database
async def test_r46_refuses_a_request_that_fails_any_transport_or_field_control(
    client, settings, migrated_database, step9_world
) -> None:
    """CSRF, Origin, content type, the accepted 8 KiB bound, and both fields."""
    council = step9_world["callers"]["C"]
    preview_id = step9_world["preview_job_id"]
    path = f"/v1/council/jobs/{preview_id}/apply"
    body = f"preview_token={LIVE_PREVIEW_TOKEN}&nonce={preview_id}"

    missing_csrf = await client.post(
        path,
        cookies=council.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=body,
    )
    assert missing_csrf.status_code == 403
    assert missing_csrf.json()["error"] == "csrf_invalid"

    missing_origin = await client.post(
        path,
        cookies=council.cookies(settings),
        headers={"Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, council)}&{body}",
    )
    assert missing_origin.status_code == 403
    assert missing_origin.json()["error"] == "origin_invalid"

    wrong_type = await client.post(
        path,
        cookies=council.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": "application/json"},
        content=b"{}",
    )
    assert wrong_type.status_code == 415

    # R-46's bound is 8 KiB, not R-45's 4 KiB: a body between the two is accepted
    # by the guard, which is what makes the number a real per-route bound rather
    # than a transcription of the neighbouring row.
    between = "p" * (R45_BODY_BOUND + 512)
    within = await post(
        client, settings, council, path, f"{body}&filler={between}"
    )
    assert within.status_code != 413, "R-46 accepts a body R-45 would refuse"

    oversized = "a" * (R46_BODY_BOUND + 1)
    too_large = await client.post(
        path,
        cookies=council.cookies(settings),
        headers={
            "Origin": settings.public_origin,
            "Content-Type": FORM,
            "Content-Length": str(len(oversized)),
        },
        content=oversized,
    )
    assert too_large.status_code == 413

    missing_token = await post(client, settings, council, path, f"preview_token=&nonce={preview_id}")
    assert missing_token.status_code == 422
    missing_nonce = await post(
        client, settings, council, path, f"preview_token={LIVE_PREVIEW_TOKEN}&nonce="
    )
    assert missing_nonce.status_code == 422


@requires_database
@pytest.mark.database
async def test_r46_is_not_reachable_for_a_malformed_or_absent_job(
    client, settings, step9_world
) -> None:
    council = step9_world["callers"]["C"]

    malformed = await post(
        client,
        settings,
        council,
        "/v1/council/jobs/not-a-uuid/apply",
        f"preview_token={LIVE_PREVIEW_TOKEN}&nonce=x",
    )
    assert malformed.status_code == 404
    assert malformed.json()["error"] == "object_not_reachable"

    # Each absent job is confirmed with **its own** canonical nonce, which is what
    # the R-46 form would have rendered had the job existed. Submitting `nonce=x`
    # here, as this case did before the nonce boundary was enforced, now measures
    # the field rule rather than reachability — a shape the production form never
    # emits, and the reason the two denials have to be compared on a request that
    # reaches the object lookup at all.
    first_id, second_id = uuid4(), uuid4()
    first_absent = await post(
        client, settings, council, f"/v1/council/jobs/{first_id}/apply",
        f"preview_token={LIVE_PREVIEW_TOKEN}&nonce={first_id}",
    )
    second_absent = await post(
        client, settings, council, f"/v1/council/jobs/{second_id}/apply",
        f"preview_token={LIVE_PREVIEW_TOKEN}&nonce={second_id}",
    )
    assert_identical_denial_responses(first_absent, second_absent)


@requires_database
@pytest.mark.database
async def test_a_confirmation_enqueues_an_apply_and_never_applies_inline(
    client, settings, migrated_database, step9_world
) -> None:
    """`303` to the **apply** job, and the redirect is the proof it is not inline.

    The confirmation returns before any parsing has happened: the apply is
    `queued`, it names the preview as its parent, and it inherits the preview's
    scope fingerprint — the scope a Council member actually read.
    """
    council = step9_world["callers"]["C"]
    preview_id = step9_world["preview_job_id"]
    tracked = step9_world["tracked"]

    response = await post(
        client,
        settings,
        council,
        f"/v1/council/jobs/{preview_id}/apply",
        f"preview_token={LIVE_PREVIEW_TOKEN}&nonce={preview_id}",
    )
    assert response.status_code == 303
    location = response.headers["location"]
    apply_id = UUID(location.rsplit("/", 1)[-1])
    tracked.job_ids.add(apply_id)
    assert apply_id != preview_id, "the redirect names the apply job, not the preview"

    applies = apply_jobs_for(migrated_database, step9_world["snapshot_id"])
    assert len(applies) == 1
    assert applies[0]["id"] == apply_id
    assert applies[0]["state"] == "queued", "nothing was applied inline"
    assert applies[0]["parent_job_id"] == preview_id

    with migrated_database.begin() as connection:
        fingerprints = connection.execute(
            text(
                "SELECT id, scope_fingerprint FROM reconciliation_jobs WHERE id IN (:a, :b)"
            ),
            {"a": preview_id, "b": apply_id},
        ).mappings().all()
    assert len({bytes(row["scope_fingerprint"]) for row in fingerprints}) == 1, (
        "the apply inherits the confirmed scope rather than recomputing one"
    )

    # And R-43 now renders the apply job as an apply, with no confirm control.
    page = await client.get(
        f"/v1/council/jobs/{apply_id}", cookies=council.cookies(settings)
    )
    assert page.status_code == 200
    assert 'data-job-kind="apply"' in page.text
    assert 'data-control="confirm"' not in page.text


@requires_database
@pytest.mark.database
async def test_a_double_click_and_a_retried_lost_response_converge_on_one_apply(
    client, settings, migrated_database, step9_world
) -> None:
    """The property the **stable** R-46 nonce exists to buy.

    Three submissions of the one rendered form — the double-click, and the retry
    a user makes when a response is lost — carry the identical nonce, produce the
    identical request key, and resolve to one apply job with one queue audit
    event. This is the opposite of R-42, where a separately rendered form must
    create a second job, and the difference is deliberate: one completed preview
    may produce only one durable effect.
    """
    council = step9_world["callers"]["C"]
    preview_id = step9_world["preview_job_id"]
    tracked = step9_world["tracked"]

    # The nonce is not invented here: it is read out of the rendered R-43 page,
    # so what is submitted is what a browser would actually have sent.
    page = await client.get(
        f"/v1/council/jobs/{preview_id}", cookies=council.cookies(settings)
    )
    assert page.status_code == 200
    fields = validate_form_exactness(
        page.text,
        expected_action_pattern=rf"/v1/council/jobs/{preview_id}/apply",
        expected_named_fields={"csrf_token", "preview_token", "nonce"},
    )
    assert fields["nonce"] == str(preview_id)

    body = f"preview_token={fields['preview_token']}&nonce={fields['nonce']}"
    path = f"/v1/council/jobs/{preview_id}/apply"

    locations = []
    for _ in range(3):
        response = await post(client, settings, council, path, body)
        assert response.status_code == 303
        locations.append(response.headers["location"])

    assert len(set(locations)) == 1, f"three submissions produced {set(locations)}"
    apply_id = UUID(locations[0].rsplit("/", 1)[-1])
    tracked.job_ids.add(apply_id)

    applies = apply_jobs_for(migrated_database, step9_world["snapshot_id"])
    assert len(applies) == 1, "one confirmation, one apply job"
    assert applies[0]["id"] == apply_id
    assert count_audit(migrated_database, APPLY_REQUESTED, apply_id) == 1

    # A second render of the same preview reproduces the same identity, which is
    # why reloading the page and confirming again is still the same effect.
    reloaded = await client.get(
        f"/v1/council/jobs/{preview_id}", cookies=council.cookies(settings)
    )
    again = validate_form_exactness(
        reloaded.text,
        expected_action_pattern=rf"/v1/council/jobs/{preview_id}/apply",
        expected_named_fields={"csrf_token", "preview_token", "nonce"},
    )
    assert again["nonce"] == fields["nonce"], "a separate render must not re-mint the apply nonce"


@requires_database
@pytest.mark.database
async def test_a_second_council_member_confirming_concurrently_starts_nothing(
    client, settings, migrated_database, step9_world
) -> None:
    """Two browsers, two Council accounts, one preview — and one apply.

    The second account's request key differs, because the key includes the
    account. The convergence therefore comes from the other fence:
    `uq_reconciliation_jobs_one_live_apply` refuses a second live apply of the
    same input, so the second confirmation is a `409` that starts nothing rather
    than ten seconds of parsing that would discover the first had won.
    """
    callers = step9_world["callers"]
    preview_id = step9_world["preview_job_id"]
    tracked = step9_world["tracked"]
    path = f"/v1/council/jobs/{preview_id}/apply"
    body = f"preview_token={LIVE_PREVIEW_TOKEN}&nonce={preview_id}"

    first = await post(client, settings, callers["C"], path, body)
    assert first.status_code == 303
    apply_id = UUID(first.headers["location"].rsplit("/", 1)[-1])
    tracked.job_ids.add(apply_id)

    second = await post(client, settings, callers["CA"], path, body)
    assert second.status_code == 409, "a concurrent confirmation must not start a second apply"
    assert 'data-conflict="duplicate_request"' in second.text
    assert "Nothing was applied" in second.text

    applies = apply_jobs_for(migrated_database, step9_world["snapshot_id"])
    assert len(applies) == 1, f"two confirmations produced {len(applies)} apply jobs"
    assert count_audit(migrated_database, APPLY_REQUESTED, apply_id) == 1


@requires_database
@pytest.mark.database
async def test_an_expired_preview_applies_nothing_and_names_the_reason(
    client, settings, migrated_database, step9_world
) -> None:
    """N-46, checked before anything else is read."""
    council = step9_world["callers"]["C"]
    tracked = step9_world["tracked"]

    with migrated_database.begin() as connection:
        job_id, _ = complete_preview(
            connection,
            snapshot_id=step9_world["snapshot_id"],
            account_id=council.account_id,
            checksum=step9_world["checksum"],
            preview_token="expiring-token",
            produced_at=datetime.now(timezone.utc) - timedelta(days=400),
        )
        tracked.job_ids.add(job_id)

    response = await post(
        client,
        settings,
        council,
        f"/v1/council/jobs/{job_id}/apply",
        f"preview_token=expiring-token&nonce={job_id}",
    )
    assert response.status_code == 409
    assert "preview_expired" in response.text
    assert "Nothing was applied" in response.text
    assert apply_jobs_for(migrated_database, step9_world["snapshot_id"]) == []
    assert job_row(migrated_database, job_id)["stale_reason"] == "preview_expired"


@requires_database
@pytest.mark.database
async def test_a_folder_change_between_preview_and_confirmation_applies_nothing(
    client, settings, migrated_database, step9_world
) -> None:
    """The mandatory Phase 3 test, seen from the confirmation side.

    The administrator moves the folder after the preview is read. The
    confirmation applies nothing, the preview is marked with the reason that
    moved, and the `409` shows the Council member the exact changed scope rather
    than a bare refusal.
    """
    callers = step9_world["callers"]
    preview_id = step9_world["preview_job_id"]

    moved = await post(
        client,
        settings,
        callers["A"],
        f"/v1/admin/snapshots/{step9_world['snapshot_id']}/folder",
        f"folder_id={fx.ARCHIVE_FOLDER_ID}",
    )
    assert moved.status_code == 303

    response = await post(
        client,
        settings,
        callers["C"],
        f"/v1/council/jobs/{preview_id}/apply",
        f"preview_token={LIVE_PREVIEW_TOKEN}&nonce={preview_id}",
    )
    assert response.status_code == 409
    assert "folder_changed" in response.text
    assert "Nothing was applied" in response.text
    assert apply_jobs_for(migrated_database, step9_world["snapshot_id"]) == []
    assert job_row(migrated_database, preview_id)["stale_reason"] == "folder_changed"


@requires_database
@pytest.mark.database
async def test_a_confirmation_naming_the_wrong_preview_token_applies_nothing(
    client, settings, migrated_database, step9_world
) -> None:
    """The token is one control among four, and a wrong one is refused first."""
    council = step9_world["callers"]["C"]
    preview_id = step9_world["preview_job_id"]

    response = await post(
        client,
        settings,
        council,
        f"/v1/council/jobs/{preview_id}/apply",
        f"preview_token=not-the-stored-token&nonce={preview_id}",
    )
    assert response.status_code == 409
    assert apply_jobs_for(migrated_database, step9_world["snapshot_id"]) == []
    # Nothing moved: a wrong token is not a scope change, so the preview is not
    # rewritten stale on its way to being refused.
    assert job_row(migrated_database, preview_id)["state"] == "completed"


@requires_database
@pytest.mark.database
async def test_a_running_apply_blocks_a_further_confirmation_of_the_same_input(
    client, settings, migrated_database, step9_world
) -> None:
    """The one-live-apply fence, through the route.

    A second *distinct* preview of the same snapshot and folder cannot be
    confirmed while an apply of that input is in flight: previewing underneath it
    would be confirming a scope that is about to move.
    """
    council = step9_world["callers"]["C"]
    tracked = step9_world["tracked"]

    first = await post(
        client,
        settings,
        council,
        f"/v1/council/jobs/{step9_world['preview_job_id']}/apply",
        f"preview_token={LIVE_PREVIEW_TOKEN}&nonce={step9_world['preview_job_id']}",
    )
    assert first.status_code == 303
    apply_id = UUID(first.headers["location"].rsplit("/", 1)[-1])
    tracked.job_ids.add(apply_id)

    with migrated_database.begin() as connection:
        other_preview, _ = complete_preview(
            connection,
            snapshot_id=step9_world["snapshot_id"],
            account_id=council.account_id,
            checksum=step9_world["checksum"],
            preview_token="second-preview-token",
        )
        tracked.job_ids.add(other_preview)

    blocked = await post(
        client,
        settings,
        council,
        f"/v1/council/jobs/{other_preview}/apply",
        f"preview_token=second-preview-token&nonce={other_preview}",
    )
    assert blocked.status_code == 409
    assert len(apply_jobs_for(migrated_database, step9_world["snapshot_id"])) == 1


@requires_database
@pytest.mark.database
async def test_a_confirmation_writes_exactly_one_queue_event_and_no_poll_writes_any(
    client, settings, migrated_database, step9_world
) -> None:
    """Audit cardinality across the whole Step 9 surface, in one place.

    A confirmation is an event. A read is not: R-43 and R-44 are polled at up to
    one request every `poll_min_seconds` per watcher, and auditing that would
    fill an append-only table with the fact that somebody looked.
    """
    council = step9_world["callers"]["C"]
    preview_id = step9_world["preview_job_id"]
    tracked = step9_world["tracked"]

    with migrated_database.begin() as connection:
        before = connection.execute(text("SELECT count(*) FROM audit_events")).scalar_one()

    for _ in range(4):
        assert (
            await client.get(
                f"/v1/council/jobs/{preview_id}", cookies=council.cookies(settings)
            )
        ).status_code == 200
        assert (
            await client.get(
                f"/v1/council/jobs/{preview_id}/status", cookies=council.cookies(settings)
            )
        ).status_code == 200

    with migrated_database.begin() as connection:
        after_reads = connection.execute(text("SELECT count(*) FROM audit_events")).scalar_one()
    assert after_reads == before, "a poll is a read and writes no audit event"

    response = await post(
        client,
        settings,
        council,
        f"/v1/council/jobs/{preview_id}/apply",
        f"preview_token={LIVE_PREVIEW_TOKEN}&nonce={preview_id}",
    )
    assert response.status_code == 303
    apply_id = UUID(response.headers["location"].rsplit("/", 1)[-1])
    tracked.job_ids.add(apply_id)
    assert count_audit(migrated_database, APPLY_REQUESTED, apply_id) == 1


@requires_database
@pytest.mark.database
async def test_the_rendered_page_never_carries_client_side_authority(
    client, settings, step9_world
) -> None:
    """The whole response, from the real route, checked for script and scope fields."""
    council = step9_world["callers"]["C"]
    response = await client.get(
        f"/v1/council/jobs/{step9_world['preview_job_id']}",
        cookies=council.cookies(settings),
    )
    assert response.status_code == 200

    body = response.text.lower()
    for marker in ("hx-on", "onclick", "onsubmit", "javascript:", "hx-vals", "hx-headers", "eval("):
        assert marker not in body, f"the job page carries {marker!r}"

    # The shell's one approved external element is HTMX itself, served
    # same-origin from the accepted manifest, and nothing else is a script.
    scripts = re.findall(r"<script\b[^>]*>", response.text)
    assert len(scripts) == 1, f"expected only the vendored HTMX element, found {scripts}"
    assert "/static/vendor/htmx-" in scripts[0]

    # And no browser-owned scope field reached the apply form.
    validate_form_exactness(
        response.text,
        expected_action_pattern=rf"/v1/council/jobs/{step9_world['preview_job_id']}/apply",
        expected_named_fields={"csrf_token", "preview_token", "nonce"},
    )


# ===========================================================================
# R-46 nonce boundary: exactly one field, exactly the preview job's identity
# ===========================================================================
#
# The remediation of the 2026-08-21 independent review's R-46 finding. The Step 9
# form has always rendered the preview job's UUID as the apply nonce — that is
# the accepted semantic, and `test_the_apply_nonce_is_the_preview_job_identity_and_is_stable`
# above has always asserted it — but the route admitted any non-empty text after
# a `.strip()`. A direct caller could therefore mint several request identities
# for one completed preview, which is precisely the thing a stable nonce exists
# to prevent. PostgreSQL's one-live-apply fence and `uq_snapshot_imports_applied_input`
# still protected the durable effect; they did not make the request boundary
# honest.
#
# Every case below is a **direct** `POST` to R-46 that never fetches R-43 first,
# and every refusal is re-read from the database on a fresh connection: a `422`
# that had already enqueued would be a worse defect than the one being fixed.


def audit_action_total(engine, *actions: str) -> int:
    """Rows for these actions, for a **delta**, because the table is append-only.

    `audit_events` is never truncated between cases — the migration's trigger
    refuses `DELETE`, which is the point of it — so an absolute count is a
    property of the whole session's history. A before/after difference of zero is
    the honest way to say "this request wrote nothing".
    """
    with engine.begin() as connection:
        return connection.execute(
            text("SELECT count(*) FROM audit_events WHERE action = ANY(:a)"),
            {"a": list(actions)},
        ).scalar_one()


def request_keys(engine) -> list[str]:
    with engine.begin() as connection:
        return [
            row[0]
            for row in connection.execute(
                text("SELECT request_key FROM reconciliation_jobs")
            )
        ]


def audit_total(engine) -> int:
    """Every append-only row, for a **delta**.

    `audit_events.id` is a UUID, not a sequence, so "rows written after id N" is
    not a question this table can answer and a high-water mark is not available.
    A total taken before and after is, and it is the stronger claim anyway: it
    covers events of *any* action, not only the two R-46 can write.
    """
    with engine.begin() as connection:
        return connection.execute(
            text("SELECT count(*) FROM audit_events")
        ).scalar_one()


def audit_payload_blob(engine) -> str:
    """Every audit fact in the table, as one blob to search for a marker.

    Reading the payloads rather than counting them, because "no event" and "an
    event that quotes the caller's text" are different failures and only one of
    them is a count. The whole corpus is searched rather than a suffix because
    the marker each case submits is unique to it — an occurrence anywhere is the
    defect, whenever it was written.
    """
    with engine.begin() as connection:
        rows = connection.execute(
            text("SELECT action, payload::text FROM audit_events")
        ).all()
    return "\n".join(f"{action} {payload}" for action, payload in rows)


def nonce_field(value: str) -> str:
    """One `nonce=` pair, percent-encoded, so the *submitted text* is exact.

    Encoding here rather than letting a case write raw bytes into the body means
    a case that submits a space, a newline, a NUL or a Cyrillic character submits
    that character — not whatever an unencoded body happened to parse into.
    """
    return f"nonce={quote(value, safe='')}"


def hostile_apply_nonces(preview_id: UUID) -> dict[str, str]:
    """The submitted `nonce` **body fragment** for each refused case.

    Keyed by case name so a failure names the shape rather than a body. Values
    are body fragments rather than nonce values because three of the cases are
    about field *multiplicity*, which no single value can express.

    Every UUID-derived case is built from `preview_id` itself, so each one is a
    spelling of the right identity that the boundary must still refuse: a
    canonical comparison is only meaningful if `UUID(submitted) == identifier`
    is *not* what is being asked.
    """
    canonical = str(preview_id)
    return {
        # -- absent and empty ---------------------------------------------
        "absent": "",
        "empty": "nonce=",
        # -- another well-formed identity ----------------------------------
        "other_uuid": nonce_field(str(uuid4())),
        "nil_uuid": nonce_field(str(UUID(int=0))),
        # -- spellings Python's UUID() would happily parse ------------------
        "uppercase": nonce_field(canonical.upper()),
        "unhyphenated": nonce_field(canonical.replace("-", "")),
        "braced": nonce_field("{" + canonical + "}"),
        "urn_prefixed": nonce_field(f"urn:uuid:{canonical}"),
        # -- whitespace, which a `.strip()` would have repaired -------------
        "leading_space": nonce_field(f" {canonical}"),
        "trailing_space": nonce_field(f"{canonical} "),
        "surrounding_whitespace": nonce_field(f"\t{canonical}\n"),
        "internal_space": nonce_field(canonical.replace("-", " ", 1)),
        # -- padding and punctuation ---------------------------------------
        "trailing_semicolon": nonce_field(f"{canonical};"),
        "quoted": nonce_field(f'"{canonical}"'),
        "query_appended": nonce_field(f"{canonical}&x=1"),
        # -- control characters at the accepted width ----------------------
        "newline": nonce_field(f"{canonical}\n"),
        "carriage_return": nonce_field(f"{canonical}\r"),
        "null_byte": nonce_field(f"{canonical}\x00"),
        # -- Unicode lookalikes --------------------------------------------
        # U+2010 HYPHEN renders like the ASCII hyphen every UUID contains, so
        # this case exists for any `preview_id` rather than only for one whose
        # hex digits happen to include a letter with a Cyrillic twin.
        "unicode_hyphen": nonce_field(canonical.replace("-", "‐", 1)),
        "zero_width_space": nonce_field(f"{canonical[:8]}​{canonical[8:]}"),
        "emoji_suffix": nonce_field(f"{canonical}\U0001f600"),
        # -- oversized, but inside R-46's accepted 8 KiB bound --------------
        # So the size guard does **not** answer first and the nonce rule is what
        # is actually being measured.
        "oversized_in_bound": nonce_field("a" * 7000),
        "canonical_then_padding": nonce_field(canonical + "a" * 6900),
        # -- multiplicity: two request identities is none --------------------
        "duplicate_identical": f"{nonce_field(canonical)}&{nonce_field(canonical)}",
        "duplicate_canonical_first": f"{nonce_field(canonical)}&{nonce_field(str(uuid4()))}",
        "duplicate_canonical_second": f"{nonce_field(str(uuid4()))}&{nonce_field(canonical)}",
        "duplicate_empty_second": f"{nonce_field(canonical)}&nonce=",
    }


@requires_database
@pytest.mark.database
async def test_r46_admits_only_the_canonical_preview_job_nonce(
    client, settings, migrated_database, step9_world
) -> None:
    """Every refused shape: `422`, no apply job, no audit effect, no echo.

    One preview for the whole table, deliberately: none of these requests may
    reach `enqueue_apply` at all, so none of them can consume the preview or trip
    the one-live-apply fence. If any did, the *next* case would fail for the
    wrong reason — which is itself part of the evidence.
    """
    council = step9_world["callers"]["C"]
    preview_id = step9_world["preview_job_id"]
    path = f"/v1/council/jobs/{preview_id}/apply"

    before_audit = audit_action_total(migrated_database, APPLY_REQUESTED, PREVIEW_QUEUED)
    before_total = audit_total(migrated_database)

    for case, fragment in hostile_apply_nonces(preview_id).items():
        body = f"preview_token={LIVE_PREVIEW_TOKEN}"
        if fragment:
            body = f"{body}&{fragment}"
        response = await post(client, settings, council, path, body)

        assert response.status_code == 422, (
            f"R-46 nonce case {case!r}: expected 422, got {response.status_code}"
        )
        assert 'data-field="nonce"' in response.text, (
            f"R-46 nonce case {case!r} must name the nonce field, not another one"
        )
        assert 'data-field="preview_token"' not in response.text

        applies = apply_jobs_for(migrated_database, step9_world["snapshot_id"])
        assert applies == [], f"R-46 nonce case {case!r} enqueued {len(applies)} applies"

    after_audit = audit_action_total(migrated_database, APPLY_REQUESTED, PREVIEW_QUEUED)
    assert after_audit == before_audit, (
        "a refused nonce wrote a queue/apply audit event"
    )
    assert audit_total(migrated_database) == before_total, (
        "a refused nonce wrote a durable audit fact of some other action"
    )

    # And the accepted submission still works, from the same preview, proving the
    # table above refused shapes rather than refusing the route.
    accepted = await post(
        client,
        settings,
        council,
        path,
        f"preview_token={LIVE_PREVIEW_TOKEN}&nonce={preview_id}",
    )
    assert accepted.status_code == 303
    apply_id = UUID(accepted.headers["location"].rsplit("/", 1)[-1])
    step9_world["tracked"].job_ids.add(apply_id)
    applies = apply_jobs_for(migrated_database, step9_world["snapshot_id"])
    assert len(applies) == 1
    assert count_audit(migrated_database, APPLY_REQUESTED, apply_id) == 1


@requires_database
@pytest.mark.database
async def test_a_refused_r46_nonce_is_never_echoed_anywhere(
    client, settings, migrated_database, step9_world
) -> None:
    """The submitted text reaches no body, header, request key or audit fact.

    A validation response that quoted the caller's input would turn R-46's `422`
    into a reflection surface, and a request key that contained it would put
    caller-chosen text into the durable column finding S-1 established must not
    become an arbitrary text channel.
    """
    council = step9_world["callers"]["C"]
    preview_id = step9_world["preview_job_id"]
    path = f"/v1/council/jobs/{preview_id}/apply"

    marker = "zz-marker-<script>alert(1)</script>-zz"
    before_total = audit_total(migrated_database)

    response = await post(
        client,
        settings,
        council,
        path,
        f"preview_token={LIVE_PREVIEW_TOKEN}&{nonce_field(marker)}",
    )
    assert response.status_code == 422

    assert marker not in response.text
    assert "zz-marker" not in response.text
    assert "<script>alert(1)</script>" not in response.text
    for name, value in response.headers.items():
        assert "zz-marker" not in value, f"the refused nonce reached header {name}"

    assert all("zz-marker" not in key for key in request_keys(migrated_database))
    assert audit_total(migrated_database) == before_total
    assert "zz-marker" not in audit_payload_blob(migrated_database)
    assert apply_jobs_for(migrated_database, step9_world["snapshot_id"]) == []


@requires_database
@pytest.mark.database
async def test_r46_refuses_a_nonce_naming_a_different_real_preview(
    client, settings, migrated_database, step9_world
) -> None:
    """A *valid* nonce for the wrong preview is still refused.

    Stronger than the table's `other_uuid` case: this UUID names a real,
    completed, confirmable preview belonging to the same Council caller. Only the
    path equality separates them, so this is the case that fails if the boundary
    ever validates "is a UUID" instead of "is *this* job".
    """
    callers = step9_world["callers"]
    tracked = step9_world["tracked"]
    preview_id = step9_world["preview_job_id"]

    with migrated_database.begin() as connection:
        other_snapshot, other_checksum = seed_snapshot(
            connection, payload=b"a-second-real-preview"
        )
        tracked.snapshot_ids.add(other_snapshot)
        select_folder(
            connection,
            snapshot_id=other_snapshot,
            account_id=callers["A"].account_id,
            folder_id=fx.ACTIVE_FOLDER_ID,
        )
        other_preview, _ = complete_preview(
            connection,
            snapshot_id=other_snapshot,
            account_id=callers["C"].account_id,
            checksum=other_checksum,
            preview_token=LIVE_PREVIEW_TOKEN,
        )
        tracked.job_ids.add(other_preview)

    crossed = await post(
        client,
        settings,
        callers["C"],
        f"/v1/council/jobs/{preview_id}/apply",
        f"preview_token={LIVE_PREVIEW_TOKEN}&nonce={other_preview}",
    )
    assert crossed.status_code == 422
    assert 'data-field="nonce"' in crossed.text
    assert apply_jobs_for(migrated_database, step9_world["snapshot_id"]) == []
    assert apply_jobs_for(migrated_database, other_snapshot) == []


@requires_database
@pytest.mark.database
async def test_r46_denial_precedence_is_unchanged_by_the_nonce_shape(
    client, settings, migrated_database, step9_world
) -> None:
    """Authorization before validation, for every cell and both nonce shapes.

    A refused caller must receive the guard's status whether their nonce is
    canonical or hostile: a `422` for an unauthorized caller would confirm that
    the job exists and that their nonce was the only thing wrong with the
    request, which is the enumeration oracle §6.3 F-2 refuses to be.

    A fresh preview per caller, for the same reason the caller matrix above uses
    one: a permitted cell enqueues, and the one-live-apply fence would otherwise
    turn the next success into a `409`.
    """
    callers = step9_world["callers"]
    tracked = step9_world["tracked"]

    for role, expected in ACCEPTED_ROUTE_CALLER_MATRIX["R-46"].items():
        with migrated_database.begin() as connection:
            snapshot_id, checksum = seed_snapshot(
                connection, payload=f"nonce-precedence-{role}".encode()
            )
            tracked.snapshot_ids.add(snapshot_id)
            select_folder(
                connection,
                snapshot_id=snapshot_id,
                account_id=callers["A"].account_id,
                folder_id=fx.ACTIVE_FOLDER_ID,
            )
            preview_id, _ = complete_preview(
                connection,
                snapshot_id=snapshot_id,
                account_id=callers["C"].account_id,
                checksum=checksum,
                preview_token=LIVE_PREVIEW_TOKEN,
            )
            tracked.job_ids.add(preview_id)

        path = f"/v1/council/jobs/{preview_id}/apply"
        hostile = f"preview_token={LIVE_PREVIEW_TOKEN}&nonce=browser-a"
        if role == "U":
            response = await client.post(
                path,
                headers={"Origin": settings.public_origin, "Content-Type": FORM},
                content=hostile,
            )
        else:
            response = await post(client, settings, callers[role], path, hostile)

        if expected == 303:
            # A permitted caller is the only one who ever reaches the field rule,
            # and for them the hostile nonce is a `422` that enqueues nothing.
            assert response.status_code == 422, (
                f"permitted caller {role} with a hostile nonce: expected 422, "
                f"got {response.status_code}"
            )
            assert 'data-field="nonce"' in response.text
        else:
            assert response.status_code == expected, (
                f"refused caller {role} with a hostile nonce: expected {expected}, "
                f"got {response.status_code}"
            )
            assert response.status_code != 422, (
                f"caller {role} learned that only their nonce was wrong"
            )

        assert apply_jobs_for(migrated_database, snapshot_id) == [], (
            f"caller {role} with a hostile nonce enqueued an apply"
        )


@requires_database
@pytest.mark.database
async def test_r46_csrf_and_transport_refusals_precede_the_nonce_rule(
    client, settings, migrated_database, step9_world
) -> None:
    """`403`, `415`, `413` and `411` are unchanged by the nonce's shape.

    The multipart case is also the reason `_submitted_apply_nonce`'s non-`str`
    branch is unit-tested rather than driven from here: a multipart body never
    reaches the nonce rule, because the content-type guard answers `415` first.
    """
    council = step9_world["callers"]["C"]
    preview_id = step9_world["preview_job_id"]
    path = f"/v1/council/jobs/{preview_id}/apply"

    for label, nonce in (("canonical", str(preview_id)), ("hostile", "browser-a")):
        body = f"preview_token={LIVE_PREVIEW_TOKEN}&{nonce_field(nonce)}"

        missing_csrf = await client.post(
            path,
            cookies=council.cookies(settings),
            headers={"Origin": settings.public_origin, "Content-Type": FORM},
            content=body,
        )
        assert missing_csrf.status_code == 403, label
        assert missing_csrf.json()["error"] == "csrf_invalid"

        wrong_csrf = await client.post(
            path,
            cookies=council.cookies(settings),
            headers={"Origin": settings.public_origin, "Content-Type": FORM},
            content=f"csrf_token=not-the-token&{body}",
        )
        assert wrong_csrf.status_code == 403, label
        assert wrong_csrf.json()["error"] == "csrf_invalid"

        multipart = await client.post(
            path,
            cookies=council.cookies(settings),
            headers={
                "Origin": settings.public_origin,
                "Content-Type": "multipart/form-data; boundary=----x",
            },
            content=(
                "------x\r\n"
                'Content-Disposition: form-data; name="nonce"; filename="n.txt"\r\n'
                "Content-Type: text/plain\r\n\r\n"
                f"{nonce}\r\n"
                "------x--\r\n"
            ).encode(),
        )
        assert multipart.status_code == 415, label

        oversized = await client.post(
            path,
            cookies=council.cookies(settings),
            headers={
                "Origin": settings.public_origin,
                "Content-Type": FORM,
                "Content-Length": str(R46_BODY_BOUND + 1),
            },
            content="a" * (R46_BODY_BOUND + 1),
        )
        assert oversized.status_code == 413, label

    assert apply_jobs_for(migrated_database, step9_world["snapshot_id"]) == []


@requires_database
@pytest.mark.database
async def test_r46_path_404_precedes_the_nonce_rule(
    client, settings, migrated_database, step9_world
) -> None:
    """A malformed path stays `404`, and the nonce rule is not an existence oracle.

    Two separate properties, and the route's precedence is what makes both hold.

    **Path parsing runs first.** A malformed `job_id` is answered `404
    object_not_reachable` whatever the nonce looks like, so a caller cannot
    discover that the path was the problem by receiving a `422` about the nonce
    instead.

    **The nonce rule runs before the job is read**, so it cannot be used to
    probe for jobs: a hostile nonce is the identical `422` whether the well-formed
    UUID in the path names a real preview or nothing at all, and the canonical
    nonce for an absent job reaches the ordinary `404`. There is no pair of
    requests whose difference reveals whether a job exists — which is the same
    property §6.3 F-2 states for the capability check.
    """
    council = step9_world["callers"]["C"]
    real_preview = step9_world["preview_job_id"]
    absent = uuid4()

    # 1. A malformed path is `404` for every nonce shape, including one that
    #    would be perfectly canonical for some other job.
    for label, nonce in (
        ("canonical_looking", str(uuid4())),
        ("hostile", "browser-a"),
        ("empty", ""),
    ):
        response = await post(
            client,
            settings,
            council,
            "/v1/council/jobs/not-a-uuid/apply",
            f"preview_token={LIVE_PREVIEW_TOKEN}&{nonce_field(nonce)}",
        )
        assert response.status_code == 404, (
            f"malformed path with a {label} nonce: expected 404, got {response.status_code}"
        )
        assert response.json()["error"] == "object_not_reachable"

    # 2. An absent job submitted with its own canonical nonce reaches the
    #    ordinary refusal, unchanged by this remediation.
    self_canonical = await post(
        client,
        settings,
        council,
        f"/v1/council/jobs/{absent}/apply",
        f"preview_token={LIVE_PREVIEW_TOKEN}&nonce={absent}",
    )
    assert self_canonical.status_code == 404, (
        "an unreachable job with a canonical nonce must not become a 422"
    )

    # 3. And a hostile nonce is byte-identical whether the job exists or not, so
    #    the field rule tells a caller nothing the `404` would not have.
    hostile_body = f"preview_token={LIVE_PREVIEW_TOKEN}&nonce=browser-a"
    against_absent = await post(
        client, settings, council, f"/v1/council/jobs/{absent}/apply", hostile_body
    )
    against_real = await post(
        client, settings, council, f"/v1/council/jobs/{real_preview}/apply", hostile_body
    )
    assert against_absent.status_code == 422
    assert against_real.status_code == 422
    # Compared directly rather than through `assert_identical_denial_responses`,
    # which asserts the JSON content type the object-scoped `404` carries: a `422`
    # is the accepted HTML `ValidationView`, so the byte-identity that matters
    # here is of the rendered body.
    assert against_absent.content == against_real.content, (
        "a hostile nonce distinguishes an existing preview from an absent one"
    )
    for forbidden in FORBIDDEN_DENIAL_HEADERS:
        assert forbidden not in against_absent.headers
        assert forbidden not in against_real.headers

    assert apply_jobs_for(migrated_database, step9_world["snapshot_id"]) == []


# -- The boundary rule itself, without a request ----------------------------

class _FakeForm:
    """The two operations R-46's nonce rule uses, and nothing else.

    A stand-in rather than a real `FormData` because the branch under test — a
    submitted value that is not text — is unreachable through HTTP: the
    content-type guard answers `415` to the only body shape that produces one.
    """

    def __init__(self, values: list[object]) -> None:
        self._values = values

    def getlist(self, key: str) -> list[object]:
        assert key == "nonce"
        return list(self._values)


class _FakeUpload:
    """A multipart part. Its `str()` is a repr, which is exactly the trap."""

    def __init__(self, value: str) -> None:
        self.filename = "nonce.txt"
        self._value = value

    def __str__(self) -> str:  # pragma: no cover - must never be consulted
        return self._value


def test_the_apply_nonce_rule_admits_exactly_one_canonical_text_value() -> None:
    identifier = uuid4()
    canonical = str(identifier)

    assert _submitted_apply_nonce(_FakeForm([canonical]), identifier) == canonical

    refused: dict[str, list[object]] = {
        "absent": [],
        "duplicate_identical": [canonical, canonical],
        "duplicate_conflicting": [canonical, str(uuid4())],
        "triplicate": [canonical, canonical, canonical],
        "empty": [""],
        "uppercase": [canonical.upper()],
        "unhyphenated": [canonical.replace("-", "")],
        "braced": ["{" + canonical + "}"],
        "urn": [f"urn:uuid:{canonical}"],
        "padded": [f" {canonical} "],
        "other_uuid": [str(uuid4())],
        "bytes": [canonical.encode()],
        "uuid_object": [identifier],
        "none": [None],
        "upload_part": [_FakeUpload(canonical)],
    }
    for case, values in refused.items():
        assert _submitted_apply_nonce(_FakeForm(values), identifier) is None, (
            f"the R-46 nonce rule admitted {case!r}"
        )


def test_falsification_a_stripping_or_first_wins_apply_nonce_rule_is_caught() -> None:
    """The two defects the remediation removed, rebuilt and shown to be caught.

    Kept as executable code rather than as a note, so the assertions above are
    demonstrably load-bearing: a rule that trims, or one that resolves a repeated
    field by precedence, passes neither of these.
    """
    identifier = uuid4()
    canonical = str(identifier)

    def stripping_rule(form, ident: UUID) -> str | None:
        submitted = form.getlist("nonce")
        if len(submitted) != 1:
            return None
        value = submitted[0]
        if not isinstance(value, str):
            return None
        # The exact defect: the submitted text is trimmed, and the trimmed text is
        # what the request key is then built from.
        repaired = value.strip()
        return repaired if repaired == str(ident) else None

    def first_wins_rule(form, ident: UUID) -> str | None:
        submitted = form.getlist("nonce")
        if not submitted:
            return None
        value = submitted[0]
        return value if isinstance(value, str) and value == str(ident) else None

    padded = _FakeForm([f" {canonical} "])
    assert stripping_rule(padded, identifier) == canonical, "the probe must repair it"
    assert _submitted_apply_nonce(padded, identifier) is None, "the real rule must not"

    repeated = _FakeForm([canonical, str(uuid4())])
    assert first_wins_rule(repeated, identifier) == canonical, "the probe must pick one"
    assert _submitted_apply_nonce(repeated, identifier) is None, "the real rule must not"
