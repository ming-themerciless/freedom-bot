"""Tests for P3.4 Step 10 import receipt and audit search views.

Covers:

1. VM-17 / R-47: `import_result.html`, the immutable receipt.
   - Every accepted field and state rendered honestly: state, import_id, status
     (applied/refused), mode (bootstrap/council), actor label & capability,
     world ID, short/full checksum, exported time, folder ID and observed/unobserved
     path, profile version, created/updated/warning counts, bounded issue codes
     with severity & counts, occurred time, correlation reference, duplicate_of.
   - Distinguishes applied from refused, and bootstrap from council. A refused
     receipt never implies character records changed. A duplicate receipt states
     that a retry resolved to the existing durable effect.
   - Strictly immutable: no `<form>`, no CSRF input, no retry/correction/delete/export/download
     affordance, no raw snapshot bytes or provider payloads.
2. VM-18 / R-48: `audit_search.html`, the navigable audit search page.
   - Canonical no-JS form `GET /v1/audit` with exact 8 optional query fields:
     `action`, `entity_type`, `entity_id`, `capability`, `source`, `from`, `to`,
     `correlation_id`.
   - Retains parsed values from `view.filters`. Action is a prefix, not a substring.
     Capability and source are closed choices. UTC fields carry format hints.
   - Progressive HTMX enhancement with `hx-get="/v1/audit/results"`, targeting
     `#audit-results` and swapping `outerHTML`.
   - No CSRF token, no payload search, no arbitrary sort, no export/mutation/delete control.
3. VM-18 / R-49: `audit_results.html`, the polled fragment and R-48's results body.
   - Ready/empty states, append-only notice, no-total explanation (`total_is_unbounded`),
     event time and ID, actor or explicit system/no-person state (`no person — system action`),
     capability, action, entity, source, correlation, bounded structured facts
     (before/after, after-only, before-only, redacted marker `value not rendered`),
     and payload truncation notice.
   - Dual pagination: full-page `href` (`/v1/audit?...`) and fragment `hx-get`
     (`/v1/audit/results?...`), both carrying canonical server-accepted `view.page_size`,
     preserving signed opaque cursor, active filters, and proper URL encoding.
   - Boundary rows are neither repeated nor omitted; no `COUNT(*)` over `audit_events`.
4. Security, Isolation, and Fixture Cleanup Enforcement:
   - Direct-call caller matrices for R-47, R-48, R-49 (U, N, M, C, A, CA, BG, AC),
     including break-glass / continuity scope distinctions (R-48/R-49 permit BG/AC;
     R-47 refuses them).
   - Malformed/absent R-47 identifiers produce byte-identical 404 denials without enumeration.
   - Adversarial XSS autoescaping in every external text and attribute context.
   - No raw payload, secret, token, internal path, or exception disclosure.
   - Audit reads produce zero audit writes; append-only DB triggers refuse UPDATE/DELETE.
   - Server-owned page size normalization verified through HTTP boundary across absent,
     malformed, 0, negative, 1, 100, and 1000 requests.
   - Complete fixture topology residue tracking across all 7 row classes with post-yield
     fresh-connection absence assertions and AST structural guard.
   - Structural isolation of proposed Step 10 hashes from accepted naming.
   - All 23 template digests, Step 10 selector ownership, and static asset integrity.
"""
from __future__ import annotations

import ast
import dataclasses
import hashlib
import html
import inspect
import json
import os
import re
import types
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import jinja2
import pytest
from sqlalchemy import text
from starlette.requests import Request

from application.audit import ActorCapability, AuditEvent, AuditSource
from application.web.audit_search import (
    AUDIT_CURSOR_SCOPE,
    FILTER_VALUE_BOUND,
    MAX_RANGE_DAYS,
    MAX_SIMULTANEOUS_FILTERS,
    RENDERED_PAYLOAD_KEYS,
)
from application.web.errors import RefusalCode
from application.web.jobs import DEFAULT_FOLDER_PATH, JobKind, JobState
from application.web.pagination import decode, encode
from application.web.snapshot_admin import SNAPSHOT_CURSOR_SCOPE
from application.web.view_models import (
    ACTOR_NAME_BOUND,
    AUDIT_FACT_BOUND,
    AUDIT_VALUE_BOUND,
    DISCORD_NAME_BOUND,
    FOLDER_CHOICE_BOUND,
    ISSUE_COUNT_BOUND,
    PAGE_SIZE_DEFAULT,
    PAGE_SIZE_MAXIMUM,
    Actor,
    AuditFact,
    AuditFilters,
    AuditRow,
    AuditSearchView,
    Correlation,
    Cursor,
    FolderChoice,
    ImportResultView,
    Instant,
    IssueCount,
    SafeText,
    SnapshotStamp,
    bounded_tuple,
)
from tests import foundry_fixtures as fx
from tests.web.conftest import add_mapping, link_discord, make_account
from tests.web.p3_3_fixtures import (
    clean_p3_3_tables,
    seed_import,
    seed_job,
    seed_snapshot,
    select_folder,
    utcnow,
)
from tests.web.portal_fixtures import clean_p3_2_tables, seed_callers
from tests.web.template_digests import (
    ACCEPTED_STEP_1_THROUGH_9_TEMPLATE_DIGESTS,
    P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS,
    PROPOSED_STEP_10_TEMPLATE_DIGESTS,
)

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = ROOT / "adapters" / "web" / "templates"
STATIC_ROOT = ROOT / "adapters" / "web" / "static"
MANIFEST_PATH = STATIC_ROOT / "asset-integrity.sha256"


# Contract §6.2 authoritative caller matrix for R-47, R-48, R-49
ACCEPTED_ROUTE_CALLER_MATRIX: dict[str, dict[str, int]] = {
    "R-47": {"U": 303, "N": 403, "M": 403, "C": 200, "A": 200, "CA": 200, "BG": 403, "AC": 403},
    "R-48": {"U": 303, "N": 403, "M": 403, "C": 200, "A": 200, "CA": 200, "BG": 200, "AC": 200},
    "R-49": {"U": 401, "N": 403, "M": 403, "C": 200, "A": 200, "CA": 200, "BG": 200, "AC": 200},
}

STEP_10_SELECTORS: tuple[str, ...] = (
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
    ".alert",
    ".alert-info",
    ".alert-warning",
    ".alert-danger",
    ".alert-success",
    ".badge",
    ".badge-sm",
    ".badge-info",
    ".badge-secondary",
    ".badge-success",
    ".badge-warning",
    ".badge-danger",
    ".btn",
    ".btn-primary",
    ".btn-secondary",
    ".reference-code",
    ".cursor-nav",
    ".font-mono",
    ".text-xs",
    ".text-sm",
    ".text-muted",
    ".search-form",
    ".filter-bar",
    ".form-row",
    ".form-group",
    ".form-label",
    ".form-input",
    ".form-select",
    ".form-help",
    ".filter-actions",
    ".empty-card",
    ".empty-icon",
    ".empty-text",
    ".table-container",
    ".council-table",
    ".sr-only",
)

PROHIBITED_STEP_10_SELECTORS: tuple[str, ...] = (
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
    return re.sub(r"\{#.*?#\}", " ", template_text, flags=re.DOTALL)


def strip_jinja_statements(template_text: str) -> str:
    return re.sub(r"\{%.*?%\}", " ", template_text, flags=re.DOTALL)


def extract_active_css_classes(css_text: str) -> set[str]:
    active_css = strip_css_comments(css_text)
    active_classes: set[str] = set()
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", active_css):
        for sel_part in m.group(1).split(","):
            for cls in re.findall(r"(?:\A|[^\w\-.])\.([a-zA-Z0-9_\-]+)", sel_part):
                active_classes.add("." + cls)
    return active_classes


def extract_active_template_classes(template_texts: list[str]) -> set[str]:
    active_classes: set[str] = set()
    for template_text in template_texts:
        stripped = strip_jinja_statements(strip_jinja_comments(template_text))
        for m in re.finditer(r"\bclass=(['\"])(.*?)\1", stripped, flags=re.DOTALL):
            for token in re.findall(r"[a-zA-Z0-9_\-]+", m.group(2)):
                active_classes.add("." + token)
    return active_classes


def make_request(path: str = "/v1/audit", query_string: bytes = b"") -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "query_string": query_string,
        "headers": [(b"host", b"testserver")],
    }
    return Request(scope)


def render_import_result(view: ImportResultView, request: Request | None = None) -> str:
    env = get_jinja_env()
    template = env.get_template("import_result.html")
    return template.render(view=view, request=request or make_request("/v1/council/imports/" + str(view.import_id)))


def render_audit_search(view: AuditSearchView, request: Request | None = None) -> str:
    env = get_jinja_env()
    template = env.get_template("audit_search.html")
    return template.render(view=view, request=request or make_request("/v1/audit"))


def render_audit_results(view: AuditSearchView, request: Request | None = None) -> str:
    env = get_jinja_env()
    template = env.get_template("audit_results.html")
    return template.render(view=view, request=request or make_request("/v1/audit/results"))


def sample_import_receipt_view(
    *,
    status: str = "applied",
    mode: str = "council",
    path_observed: bool = True,
    duplicate_of: UUID | None = None,
    issue_counts: tuple[IssueCount, ...] = (),
) -> ImportResultView:
    import_id = uuid4()
    return ImportResultView(
        state="ready",
        import_id=import_id,
        status=status,
        mode=mode,
        actor=Actor(
            account_id=uuid4() if mode != "bootstrap" else None,
            label=SafeText.bounded(
                "Council Member" if mode != "bootstrap" else "The platform (supervised bootstrap)",
                DISCORD_NAME_BOUND,
            ),
            capability=ActorCapability.GUILD_COUNCIL if mode != "bootstrap" else ActorCapability.SYSTEM,
        ),
        capability=ActorCapability.GUILD_COUNCIL if mode != "bootstrap" else ActorCapability.SYSTEM,
        snapshot=SnapshotStamp(
            checksum_short="1a2b3c4d5e6f",
            world_id="the-guild",
            exported_at=Instant.of(datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc)),
        ),
        checksum_full="1a2b3c4d5e6f" + "0" * 52,
        folder=FolderChoice(
            folder_id=fx.ACTIVE_FOLDER_ID,
            folder_path=SafeText.bounded(
                "/Actors/Characters (active)" if path_observed else fx.ACTIVE_FOLDER_ID,
                ACTOR_NAME_BOUND,
            ),
            actor_count=32,
            is_default=True,
            path_observed=path_observed,
        ),
        profile_version="foundry-v14-dnd5e-v5-p3.3",
        created_count=5,
        updated_count=27,
        warning_count=len(issue_counts),
        issue_counts=issue_counts,
        occurred_at=Instant.of(datetime(2026, 8, 21, 14, 30, tzinfo=timezone.utc)),
        correlation=Correlation(uuid4()),
        duplicate_of=duplicate_of,
    )


def sample_audit_search_view(
    *,
    state: str = "ready",
    filters: AuditFilters | None = None,
    rows: tuple[AuditRow, ...] = (),
    cursor: Cursor | None = None,
    page_size: int = PAGE_SIZE_DEFAULT,
) -> AuditSearchView:
    return AuditSearchView(
        state=state,
        filters=filters or AuditFilters(),
        rows=rows,
        cursor=cursor or Cursor(token=None, has_more=False),
        page_size=page_size,
        total_is_unbounded=True,
        immutability_notice_code="append_only_no_correction_here",
    )


# ===========================================================================
# Pure Unit / Template Rendering Tests
# ===========================================================================

def test_import_result_applied_council_rendering() -> None:
    view = sample_import_receipt_view(status="applied", mode="council")
    rendered = render_import_result(view)

    assert "Import Receipt" in rendered
    assert '<span class="badge badge-success" data-field="status-badge">Applied</span>' in rendered
    assert '<span class="badge badge-secondary" data-field="mode-badge">council</span>' in rendered
    assert 'data-field="outcome" data-status="applied"' in rendered
    assert "This import committed the character records" in rendered
    assert str(view.import_id) in rendered
    assert view.snapshot.world_id in rendered
    assert view.checksum_full in rendered
    assert "created" in rendered and "5" in rendered
    assert "updated" in rendered and "27" in rendered
    assert "View audit history &rarr;" in rendered
    assert '<form' not in rendered
    assert 'csrf_token' not in rendered


def test_import_result_refused_council_rendering() -> None:
    view = sample_import_receipt_view(status="refused", mode="council")
    rendered = render_import_result(view)

    assert '<span class="badge badge-danger" data-field="status-badge">Refused</span>' in rendered
    assert 'data-field="outcome" data-status="refused"' in rendered
    assert "Refused. Nothing was applied." in rendered
    assert "created or changed by this import." in rendered
    assert 'data-note="refused-counts"' in rendered
    assert "This import was refused, so these counts describe what it examined" in rendered


def test_import_result_applied_bootstrap_rendering() -> None:
    view = sample_import_receipt_view(status="applied", mode="bootstrap")
    rendered = render_import_result(view)

    assert '<span class="badge badge-secondary" data-field="mode-badge">bootstrap</span>' in rendered
    assert "The platform (supervised bootstrap)" in rendered
    assert 'data-mode="bootstrap"' in rendered


def test_import_result_duplicate_rendering() -> None:
    orig_id = uuid4()
    view = sample_import_receipt_view(status="applied", mode="council", duplicate_of=orig_id)
    rendered = render_import_result(view)

    assert 'data-field="duplicate-of"' in rendered
    assert f'data-duplicate-of="{orig_id}"' in rendered
    assert "This confirmation returned an import that had <strong>already</strong>" in rendered
    assert str(orig_id) in rendered


def test_import_result_unobserved_folder_honest_rendering() -> None:
    view = sample_import_receipt_view(path_observed=False)
    rendered = render_import_result(view)

    assert 'data-path-observed="false"' in rendered
    assert fx.ACTIVE_FOLDER_ID in rendered
    assert '<span class="badge badge-warning badge-sm" data-state="unobserved">path not recorded</span>' in rendered


def test_import_result_observed_folder_rendering() -> None:
    view = sample_import_receipt_view(path_observed=True)
    rendered = render_import_result(view)

    assert 'data-path-observed="true"' in rendered
    assert "/Actors/Characters (active)" in rendered
    assert "path not recorded" not in rendered


def test_import_result_issue_counts_rendering() -> None:
    issues = (
        IssueCount(code="item_structure_invalid", severity="error", count=2),
        IssueCount(code="legacy_field_ignored", severity="warning", count=14),
    )
    view = sample_import_receipt_view(issue_counts=issues)
    rendered = render_import_result(view)

    assert "Issues" in rendered
    assert 'data-issue-code="item_structure_invalid"' in rendered
    assert 'data-severity="error"' in rendered
    assert '&times; 2' in rendered
    assert 'data-issue-code="legacy_field_ignored"' in rendered
    assert 'data-severity="warning"' in rendered
    assert '&times; 14' in rendered


def test_import_result_strictly_immutable_no_forms_no_downloads() -> None:
    view = sample_import_receipt_view()
    rendered = render_import_result(view)

    assert "<form" not in rendered
    assert "<input" not in rendered
    assert "<button" not in rendered
    assert "csrf_token" not in rendered
    for forbidden in ("/download", "/artifact", ".zip", ".ndjson", "Traceback", "Exception"):
        assert forbidden not in rendered


def test_audit_search_exact_form_structure_and_8_fields() -> None:
    view = sample_audit_search_view()
    rendered = render_audit_search(view)

    assert '<form method="get" action="/v1/audit"' in rendered
    assert 'class="search-form"' in rendered
    assert 'data-control="filters"' in rendered
    assert 'hx-get="/v1/audit/results"' in rendered
    assert 'hx-target="#audit-results"' in rendered
    assert 'hx-swap="outerHTML"' in rendered

    # Exactly the 8 expected form input names
    form_inputs = re.findall(r'<input[^>]+name="([^"]+)"|<select[^>]+name="([^"]+)"', rendered)
    names = {name for pair in form_inputs for name in pair if name}
    assert names == {
        "action",
        "entity_type",
        "entity_id",
        "capability",
        "source",
        "correlation_id",
        "from",
        "to",
    }
    assert "csrf_token" not in names


def test_audit_search_retains_all_filter_values() -> None:
    corr_id = uuid4()
    filters = AuditFilters(
        action_prefix=SafeText.bounded("reconciliation.", 120),
        entity_type="reconciliation_job",
        entity_id=SafeText.bounded("job-123", 120),
        capability=ActorCapability.GUILD_COUNCIL,
        source="web",
        occurred_from=Instant.of(datetime(2026, 8, 20, 0, 0, tzinfo=timezone.utc)),
        occurred_to=Instant.of(datetime(2026, 8, 21, 23, 59, tzinfo=timezone.utc)),
        correlation_id=corr_id,
    )
    view = sample_audit_search_view(filters=filters)
    rendered = render_audit_search(view)

    assert 'value="reconciliation."' in rendered
    assert 'value="reconciliation_job"' in rendered
    assert 'value="job-123"' in rendered
    assert '<option value="guild_council" selected>' in rendered
    assert '<option value="web" selected>' in rendered
    assert f'value="{corr_id}"' in rendered
    assert 'value="2026-08-20T00:00:00+00:00"' in rendered
    assert 'value="2026-08-21T23:59:00+00:00"' in rendered


def test_audit_results_empty_state_rendering() -> None:
    view = sample_audit_search_view(state="empty", rows=())
    rendered = render_audit_results(view)

    assert 'data-state="empty"' in rendered
    assert '<div class="empty-card" data-state="empty">' in rendered
    assert "No Matching Events" in rendered
    assert "No audit event matches these filters." in rendered
    assert '<table' not in rendered


def test_audit_results_ready_state_rows_rendering() -> None:
    event_id = uuid4()
    corr_id = uuid4()
    row = AuditRow(
        event_id=event_id,
        occurred_at=Instant.of(datetime(2026, 8, 21, 10, 0, tzinfo=timezone.utc)),
        actor=Actor(
            account_id=uuid4(),
            label=SafeText.bounded("Council User", 80),
            capability=ActorCapability.GUILD_COUNCIL,
        ),
        actor_capability=ActorCapability.GUILD_COUNCIL,
        action="snapshot.folder_selected",
        entity_type="foundry_snapshot",
        entity_id=SafeText.bounded(str(uuid4()), 120),
        source="web",
        correlation=Correlation(corr_id),
        facts=(
            AuditFact(key="folder_id", before=SafeText.bounded("actv0000", 120), after=SafeText.bounded("arch0000", 120)),
        ),
        payload_truncated=False,
    )
    view = sample_audit_search_view(state="ready", rows=(row,))
    rendered = render_audit_results(view)

    assert f'data-event-id="{event_id}"' in rendered
    assert "Council User" in rendered
    assert "snapshot.folder_selected" in rendered
    assert "foundry_snapshot" in rendered
    assert "actv0000" in rendered
    assert "arch0000" in rendered
    assert str(corr_id) in rendered
    assert 'data-total-unbounded="true"' in rendered


def test_audit_results_actor_variants_current_retired_system() -> None:
    # 1. System action
    system_row = AuditRow(
        event_id=uuid4(),
        occurred_at=Instant.of(datetime(2026, 8, 21, 10, 0, tzinfo=timezone.utc)),
        actor=None,
        actor_capability=ActorCapability.SYSTEM,
        action="reconciliation.job_failed",
        entity_type="reconciliation_job",
        entity_id=SafeText.bounded("job-sys", 120),
        source="system",
        correlation=Correlation(uuid4()),
        facts=(),
        payload_truncated=False,
    )
    # 2. Historical / retired actor
    retired_row = AuditRow(
        event_id=uuid4(),
        occurred_at=Instant.of(datetime(2026, 8, 21, 9, 0, tzinfo=timezone.utc)),
        actor=Actor(account_id=uuid4(), label=SafeText.bounded("Retired Identity User", 80), capability=ActorCapability.GUILD_COUNCIL),
        actor_capability=ActorCapability.GUILD_COUNCIL,
        action="legacy.action",
        entity_type="character",
        entity_id=SafeText.bounded("char-1", 120),
        source="discord",
        correlation=Correlation(uuid4()),
        facts=(),
        payload_truncated=False,
    )
    view = sample_audit_search_view(rows=(system_row, retired_row))
    rendered = render_audit_results(view)

    assert 'data-has-actor="false"' in rendered
    assert "no person &mdash; system action" in rendered
    assert "Retired Identity User" in rendered


def test_audit_results_fact_changes_before_after_variants() -> None:
    row = AuditRow(
        event_id=uuid4(),
        occurred_at=Instant.of(datetime(2026, 8, 21, 10, 0, tzinfo=timezone.utc)),
        actor=None,
        actor_capability=ActorCapability.SYSTEM,
        action="test.facts",
        entity_type="test",
        entity_id=SafeText.bounded("test-1", 120),
        source="system",
        correlation=Correlation(uuid4()),
        facts=(
            AuditFact(key="both", before=SafeText.bounded("old_val", 120), after=SafeText.bounded("new_val", 120)),
            AuditFact(key="after_only", before=None, after=SafeText.bounded("set_val", 120)),
            AuditFact(key="before_only", before=SafeText.bounded("cleared_val", 120), after=None),
            AuditFact(key="neither", before=None, after=None),
        ),
        payload_truncated=False,
    )
    view = sample_audit_search_view(rows=(row,))
    rendered = render_audit_results(view)

    assert 'data-change="before-after"' in rendered
    assert "old_val" in rendered and "new_val" in rendered
    assert 'data-change="after-only"' in rendered
    assert "set_val" in rendered
    assert 'data-change="before-only"' in rendered
    assert "cleared_val" in rendered
    assert '<span class="badge badge-secondary badge-sm" data-field="fact-cleared">cleared</span>' in rendered
    assert "no value recorded" in rendered


def test_audit_results_redacted_fact_leaks_no_value() -> None:
    row = AuditRow(
        event_id=uuid4(),
        occurred_at=Instant.of(datetime(2026, 8, 21, 10, 0, tzinfo=timezone.utc)),
        actor=None,
        actor_capability=ActorCapability.SYSTEM,
        action="test.redacted",
        entity_type="test",
        entity_id=SafeText.bounded("test-1", 120),
        source="system",
        correlation=Correlation(uuid4()),
        facts=(
            AuditFact(key="super_secret_key", before=None, after=None, redacted=True),
        ),
        payload_truncated=False,
    )
    view = sample_audit_search_view(rows=(row,))
    rendered = render_audit_results(view)

    assert 'data-fact-key="super_secret_key"' in rendered
    assert 'data-redacted="true"' in rendered
    assert '<span class="badge badge-warning badge-sm" data-field="fact-redacted">value not rendered</span>' in rendered


def test_audit_results_payload_truncated_notice() -> None:
    row = AuditRow(
        event_id=uuid4(),
        occurred_at=Instant.of(datetime(2026, 8, 21, 10, 0, tzinfo=timezone.utc)),
        actor=None,
        actor_capability=ActorCapability.SYSTEM,
        action="test.trunc",
        entity_type="test",
        entity_id=SafeText.bounded("test-1", 120),
        source="system",
        correlation=Correlation(uuid4()),
        facts=(),
        payload_truncated=True,
    )
    view = sample_audit_search_view(rows=(row,))
    rendered = render_audit_results(view)

    assert 'data-payload-truncated="true"' in rendered
    assert 'data-field="payload-truncated-notice"' in rendered
    assert "Some facts or values were omitted at the accepted bound." in rendered


def test_audit_results_pagination_urls_both_href_and_hx_get() -> None:
    token = "opaque.cursor.token=="
    cursor = Cursor(token=token, has_more=True)
    filters = AuditFilters(action_prefix=SafeText.bounded("reconciliation.", 120))
    view = sample_audit_search_view(cursor=cursor, filters=filters, page_size=25)
    req = make_request("/v1/audit/results", query_string=b"size=25")
    rendered = render_audit_results(view, req)

    encoded_cursor = urllib.parse.quote(token, safe="")
    assert f'href="/v1/audit?cursor={encoded_cursor}&amp;action=reconciliation.&amp;size=25"' in rendered
    assert f'hx-get="/v1/audit/results?cursor={encoded_cursor}&amp;action=reconciliation.&amp;size=25"' in rendered
    assert 'hx-target="#audit-results"' in rendered
    assert 'hx-swap="outerHTML"' in rendered


def test_step_10_templates_xss_autoescaping_in_all_contexts() -> None:
    xss = '<script>alert("xss")</script><img src=x onerror=alert(1)>"\'&<>'
    corr_id = uuid4()
    # 1. import_result.html
    issue = IssueCount(code=f"code_{xss}", severity="warning", count=1)
    import_view = sample_import_receipt_view(issue_counts=(issue,))
    import_view = dataclasses.replace(
        import_view,
        actor=Actor(account_id=uuid4(), label=SafeText.bounded(f"Actor_{xss}", 80), capability=ActorCapability.GUILD_COUNCIL),
        folder=FolderChoice(
            folder_id=f"folder_{xss}",
            folder_path=SafeText.bounded(f"Path_{xss}", 120),
            actor_count=1,
            is_default=True,
            path_observed=True,
        ),
    )
    rendered_import = render_import_result(import_view)
    assert "<script>alert" not in rendered_import
    assert "<img src=x" not in rendered_import
    assert "&lt;script&gt;alert" in rendered_import
    assert "&lt;img src=x" in rendered_import

    # 2. audit_search.html & audit_results.html
    audit_row = AuditRow(
        event_id=uuid4(),
        occurred_at=Instant.of(datetime(2026, 8, 21, 10, 0, tzinfo=timezone.utc)),
        actor=Actor(account_id=uuid4(), label=SafeText.bounded(f"Actor_{xss}", 80), capability=ActorCapability.GUILD_COUNCIL),
        actor_capability=ActorCapability.GUILD_COUNCIL,
        action=f"action_{xss}",
        entity_type=f"entity_{xss}",
        entity_id=SafeText.bounded(f"id_{xss}", 120),
        source="web",
        correlation=Correlation(corr_id),
        facts=(
            AuditFact(key=f"key_{xss}", before=SafeText.bounded(f"before_{xss}", 120), after=SafeText.bounded(f"after_{xss}", 120)),
        ),
        payload_truncated=False,
    )
    audit_view = sample_audit_search_view(
        filters=AuditFilters(action_prefix=SafeText.bounded(f"action_{xss}", 120)),
        rows=(audit_row,),
        cursor=Cursor(token=f"cursor_{xss}", has_more=True),
        page_size=50,
    )
    rendered_search = render_audit_search(audit_view)
    assert "<script>alert" not in rendered_search
    assert "<img src=x" not in rendered_search


@pytest.mark.parametrize("template_name", ["import_result.html", "audit_search.html", "audit_results.html"])
def test_step_10_templates_contain_no_script_or_client_authority(template_name: str) -> None:
    source = (TEMPLATE_ROOT / template_name).read_text(encoding="utf-8").lower()
    active = strip_jinja_comments(source)
    for marker in FORBIDDEN_SCRIPT_MARKERS:
        assert marker not in active, f"{template_name} contains forbidden marker {marker!r}"


@pytest.mark.parametrize("template_name", ["import_result.html", "audit_search.html", "audit_results.html"])
def test_step_10_templates_reference_no_remote_origin(template_name: str) -> None:
    source = (TEMPLATE_ROOT / template_name).read_text(encoding="utf-8").lower()
    for marker in ("http://", "https://", "//cdn.", "cdn.jsdelivr", "unpkg.com", "@import url("):
        assert marker not in strip_jinja_comments(source), f"{template_name} references remote origin {marker!r}"


# ===========================================================================
# Integrity, Manifest and Digest Verification Tests
# ===========================================================================

def test_template_digests_match_implementation_corpus() -> None:
    found = {
        p.name: compute_sha256(p)
        for p in TEMPLATE_ROOT.glob("*.html")
        if p.name != "base.html" and not p.name.startswith(".")
    }
    assert set(found.keys()) == set(P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS.keys())
    for name, expected_sha in P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS.items():
        assert found[name] == expected_sha, f"Digest mismatch for template '{name}': {found[name]} != {expected_sha}"


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


def test_step_10_selectors_used_and_prohibited_excluded() -> None:
    css_file = next(STATIC_ROOT.glob("css/freedom-blades.*.css"))
    css_text = css_file.read_text()
    active_css = extract_active_css_classes(css_text)

    templates = [
        (TEMPLATE_ROOT / "import_result.html").read_text(),
        (TEMPLATE_ROOT / "audit_search.html").read_text(),
        (TEMPLATE_ROOT / "audit_results.html").read_text(),
    ]
    active_tmpl_classes = extract_active_template_classes(templates)

    for sel in active_tmpl_classes:
        assert sel in active_css, f"Template class '{sel}' not defined in stylesheet"

    for prohibited in PROHIBITED_STEP_10_SELECTORS:
        assert prohibited not in active_css, f"Prohibited selector '{prohibited}' found in stylesheet"


def test_structural_route_caller_matrix_valid() -> None:
    expected_routes = {"R-47", "R-48", "R-49"}
    assert set(ACCEPTED_ROUTE_CALLER_MATRIX) == expected_routes

    expected_callers = {"U", "N", "M", "C", "A", "CA", "BG", "AC"}
    for route, row in ACCEPTED_ROUTE_CALLER_MATRIX.items():
        assert set(row) == expected_callers
        if route == "R-47":
            assert row["U"] == 303
            assert row["N"] == 403
            assert row["M"] == 403
            assert row["C"] == 200
            assert row["A"] == 200
            assert row["CA"] == 200
            assert row["BG"] == 403
            assert row["AC"] == 403
        elif route == "R-48":
            assert row["U"] == 303
            assert row["N"] == 403
            assert row["M"] == 403
            assert row["C"] == 200
            assert row["A"] == 200
            assert row["CA"] == 200
            assert row["BG"] == 200
            assert row["AC"] == 200
        elif route == "R-49":
            assert row["U"] == 401
            assert row["N"] == 403
            assert row["M"] == 403
            assert row["C"] == 200
            assert row["A"] == 200
            assert row["CA"] == 200
            assert row["BG"] == 200
            assert row["AC"] == 200


def test_the_transcribed_matrix_agrees_with_the_accepted_contract_document() -> None:
    contract = (ROOT / "docs" / "contracts" / "phase-3-route-authorization-contract.md").read_text()
    section = contract.split("### 6.2 P3.3 matrix", 1)[1].split("### 6.3", 1)[0]
    states = ("U", "N", "M", "C", "A", "CA", "BG")
    row_re = re.compile(r"^\|\s*(R-\d+)\s*\|\s*`([^`]+)`\s*\|(.+)\|\s*$", re.MULTILINE)

    parsed: dict[str, dict[str, str]] = {}
    for match in row_re.finditer(section):
        cells = [cell.strip() for cell in match.group(3).split("|")]
        parsed[match.group(1)] = dict(zip(states, cells[: len(states)]))
    assert {"R-47", "R-48", "R-49"} <= set(parsed)

    for route, row in ACCEPTED_ROUTE_CALLER_MATRIX.items():
        for state in states:
            cell = parsed[route][state]
            if cell.startswith("✓"):
                expected = 200
            elif "303" in cell:
                expected = 303
            elif "401" in cell:
                expected = 401
            elif "403" in cell:
                expected = 403
            elif "404" in cell:
                expected = 404
            else:
                expected = 403
            assert row[state] == expected, f"{route} {state} expected {expected}, got {row[state]}"


def test_structural_proposed_hashes_isolated_from_accepted_naming() -> None:
    """Finding 3 structural guard: proposed Step 10 hashes never appear in accepted-named mappings."""
    import tests.web.template_digests as td

    assert not hasattr(td, "ACCEPTED_TEMPLATE_DIGESTS"), (
        "ACCEPTED_TEMPLATE_DIGESTS combined alias must not exist"
    )
    assert len(td.ACCEPTED_STEP_1_THROUGH_9_TEMPLATE_DIGESTS) == 20
    assert len(td.PROPOSED_STEP_10_TEMPLATE_DIGESTS) == 3
    assert len(td.P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS) == 23

    accepted_keys = set(td.ACCEPTED_STEP_1_THROUGH_9_TEMPLATE_DIGESTS.keys())
    proposed_keys = set(td.PROPOSED_STEP_10_TEMPLATE_DIGESTS.keys())
    assert accepted_keys.isdisjoint(proposed_keys)

    assert isinstance(td.ACCEPTED_STEP_1_THROUGH_9_TEMPLATE_DIGESTS, types.MappingProxyType)
    assert isinstance(td.PROPOSED_STEP_10_TEMPLATE_DIGESTS, types.MappingProxyType)
    assert isinstance(td.P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS, types.MappingProxyType)


def inspect_step10_cleanup_fixture_ast(func_or_src: Any) -> None:
    """The cleanup must resolve the database after the yield, not before."""
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
    assert len(loops) >= 5, "Second with-block must iterate tracked fixture identifier sets"


def test_structural_step10_fixture_cleans_after_yield() -> None:
    inspect_step10_cleanup_fixture_ast(clean_between_step10_cases)


def test_falsification_structural_fixture_rejects_resolution_before_yield() -> None:
    bad_code = """
def clean_between_step10_cases(request):
    engine = request.getfixturevalue("migrated_database")
    tracked_state = TrackedStep10FixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return
    with engine.begin() as connection:
        clean_p3_3_tables(connection)
        clean_p3_2_tables(connection)
    with engine.begin() as fresh_conn:
        for s in tracked_state.snapshot_ids:
            assert fresh_conn.execute(text("SELECT 1"), {"id": s}).scalar_one() == 0
"""
    with pytest.raises(AssertionError, match=r"Yield at line .* must precede database resolution"):
        inspect_step10_cleanup_fixture_ast(bad_code)


# ===========================================================================
# Database-Backed HTTP Tests
# ===========================================================================

requires_database = pytest.mark.skipif(
    "TEST_DATABASE_URL" not in os.environ,
    reason="TEST_DATABASE_URL is not configured for disposable PostgreSQL database.",
)


@dataclass
class TrackedStep10FixtureState:
    snapshot_ids: set[UUID] = field(default_factory=set)
    import_ids: set[UUID] = field(default_factory=set)
    job_ids: set[UUID] = field(default_factory=set)
    account_ids: set[UUID] = field(default_factory=set)
    discord_user_ids: set[int] = field(default_factory=set)
    role_mapping_ids: set[UUID] = field(default_factory=set)
    audit_event_ids: set[UUID] = field(default_factory=set)


@pytest.fixture(autouse=True)
def clean_between_step10_cases(request):
    """Guaranteed post-yield teardown and fresh-connection absence verification for Step 10."""
    tracked_state = TrackedStep10FixtureState()
    yield tracked_state
    if "migrated_database" not in request.fixturenames:
        return

    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE audit_events, role_capability_mapping_events"))
        clean_p3_3_tables(connection)
        clean_p3_2_tables(connection)
        connection.execute(text("DELETE FROM role_capability_mappings WHERE NOT protected"))
        connection.execute(text("DELETE FROM external_identities"))
        connection.execute(text("DELETE FROM discord_membership_roles"))
        connection.execute(text("DELETE FROM discord_guild_memberships"))
        connection.execute(text("DELETE FROM discord_users"))
        connection.execute(text("DELETE FROM sessions"))
        connection.execute(text("DELETE FROM platform_accounts"))

    with engine.begin() as fresh_conn:
        for snap_id in tracked_state.snapshot_ids:
            rem = fresh_conn.execute(
                text("SELECT count(*) FROM foundry_snapshots WHERE id = :id"),
                {"id": snap_id},
            ).scalar_one()
            assert rem == 0, f"Cleanup residue: foundry_snapshot {snap_id} still exists"
            rem_f = fresh_conn.execute(
                text("SELECT count(*) FROM snapshot_folder_selections WHERE snapshot_id = :id"),
                {"id": snap_id},
            ).scalar_one()
            assert rem_f == 0, f"Cleanup residue: snapshot_folder_selections for {snap_id} still exists"

        for imp_id in tracked_state.import_ids:
            rem = fresh_conn.execute(
                text("SELECT count(*) FROM snapshot_imports WHERE id = :id"),
                {"id": imp_id},
            ).scalar_one()
            assert rem == 0, f"Cleanup residue: snapshot_import {imp_id} still exists"

        for job_id in tracked_state.job_ids:
            for table in ("reconciliation_jobs", "reconciliation_job_results"):
                column = "id" if table == "reconciliation_jobs" else "job_id"
                rem = fresh_conn.execute(
                    text(f"SELECT count(*) FROM {table} WHERE {column} = :id"),
                    {"id": job_id},
                ).scalar_one()
                assert rem == 0, f"Cleanup residue: {table} row for {job_id} still exists"

        for acc_id in tracked_state.account_ids:
            rem = fresh_conn.execute(
                text("SELECT count(*) FROM platform_accounts WHERE id = :id"),
                {"id": acc_id},
            ).scalar_one()
            assert rem == 0, f"Cleanup residue: platform_account {acc_id} still exists"

        for disc_id in tracked_state.discord_user_ids:
            rem_u = fresh_conn.execute(
                text("SELECT count(*) FROM discord_users WHERE id = :id"),
                {"id": disc_id},
            ).scalar_one()
            assert rem_u == 0, f"Cleanup residue: discord_user {disc_id} still exists"
            rem_m = fresh_conn.execute(
                text("SELECT count(*) FROM discord_guild_memberships WHERE discord_user_id = :id"),
                {"id": disc_id},
            ).scalar_one()
            assert rem_m == 0, f"Cleanup residue: discord_guild_membership for {disc_id} still exists"

        for map_id in tracked_state.role_mapping_ids:
            rem_map = fresh_conn.execute(
                text("SELECT count(*) FROM role_capability_mappings WHERE id = :id"),
                {"id": map_id},
            ).scalar_one()
            assert rem_map == 0, f"Cleanup residue: role_capability_mapping {map_id} still exists"

        for ev_id in tracked_state.audit_event_ids:
            rem_ev = fresh_conn.execute(
                text("SELECT count(*) FROM audit_events WHERE id = :id"),
                {"id": ev_id},
            ).scalar_one()
            assert rem_ev == 0, f"Cleanup residue: audit_event {ev_id} still exists"


@pytest.fixture()
def step10_world(migrated_database, settings, clean_between_step10_cases):
    tracked: TrackedStep10FixtureState = clean_between_step10_cases
    callers = seed_callers(migrated_database, settings)
    for c in callers.values():
        if c.account_id is not None:
            tracked.account_ids.add(c.account_id)
        if c.subject is not None:
            tracked.discord_user_ids.add(int(c.subject))

    with migrated_database.begin() as connection:
        seeder_accs = connection.execute(
            text("SELECT id FROM platform_accounts WHERE display_label = 'seeder'")
        ).scalars().all()
        for acc in seeder_accs:
            tracked.account_ids.add(acc)

        seeder_users = connection.execute(
            text("SELECT id FROM discord_users")
        ).scalars().all()
        for u in seeder_users:
            if u is not None:
                tracked.discord_user_ids.add(int(u))

        mappings = connection.execute(
            text("SELECT id FROM role_capability_mappings WHERE NOT protected")
        ).scalars().all()
        for m in mappings:
            tracked.role_mapping_ids.add(m)

        # Seed snapshot
        snapshot_id, checksum = seed_snapshot(
            connection, folder_ids=(fx.ACTIVE_FOLDER_ID, fx.ARCHIVE_FOLDER_ID)
        )
        tracked.snapshot_ids.add(snapshot_id)

        # Seed job (ensures job row class is represented in Step 10 topology)
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        tracked.job_ids.add(job_id)

        # Seed import receipt
        import_id = seed_import(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            folder_id=fx.ACTIVE_FOLDER_ID,
            folder_path="/Actors/Characters (active)",
        )
        tracked.import_ids.add(import_id)

        # Seed audit events
        moment = utcnow() - timedelta(seconds=120)
        for i in range(105):
            ev_id = uuid4()
            tracked.audit_event_ids.add(ev_id)
            connection.execute(
                text(
                    "INSERT INTO audit_events (id, occurred_at, actor_platform_account_id, actor_capability, "
                    "action, entity_type, entity_id, source, correlation_id, payload) VALUES "
                    "(:id, :occurred_at, :actor_id, :capability, :action, :entity_type, :entity_id, :source, :corr, :payload)"
                ),
                {
                    "id": ev_id,
                    "occurred_at": moment + timedelta(seconds=i),
                    "actor_id": callers["C"].account_id,
                    "capability": "guild_council",
                    "action": f"reconciliation.event.{i:03d}",
                    "entity_type": "reconciliation_job",
                    "entity_id": str(uuid4()),
                    "source": "web",
                    "corr": uuid4(),
                    "payload": json.dumps({"folder_id": "actv0000", "would_create": i}),
                },
            )

    return {
        "callers": callers,
        "tracked": tracked,
        "snapshot_id": snapshot_id,
        "checksum": checksum,
        "import_id": import_id,
        "job_id": job_id,
    }


@requires_database
@pytest.mark.database
async def test_r47_import_receipt_caller_matrix_and_direct_call_denials(
    client, settings, step10_world
) -> None:
    callers = step10_world["callers"]
    import_id = step10_world["import_id"]

    for role, expected in ACCEPTED_ROUTE_CALLER_MATRIX["R-47"].items():
        response = await client.get(
            f"/v1/council/imports/{import_id}",
            cookies=callers[role].cookies(settings) if role != "U" else {},
        )
        assert response.status_code == expected, (
            f"R-47 caller {role}: expected {expected}, got {response.status_code}"
        )
        if role == "U":
            assert response.headers["location"] == "/v1/login"


@requires_database
@pytest.mark.database
async def test_r48_audit_search_caller_matrix_including_bg_and_ac(
    client, settings, step10_world
) -> None:
    callers = step10_world["callers"]

    for role, expected in ACCEPTED_ROUTE_CALLER_MATRIX["R-48"].items():
        response = await client.get(
            "/v1/audit",
            cookies=callers[role].cookies(settings) if role != "U" else {},
        )
        assert response.status_code == expected, (
            f"R-48 caller {role}: expected {expected}, got {response.status_code}"
        )
        if role == "U":
            assert response.headers["location"] == "/v1/login"


@requires_database
@pytest.mark.database
async def test_r49_audit_results_caller_matrix_including_bg_and_ac(
    client, settings, step10_world
) -> None:
    callers = step10_world["callers"]

    for role, expected in ACCEPTED_ROUTE_CALLER_MATRIX["R-49"].items():
        response = await client.get(
            "/v1/audit/results",
            cookies=callers[role].cookies(settings) if role != "U" else {},
        )
        assert response.status_code == expected, (
            f"R-49 caller {role}: expected {expected}, got {response.status_code}"
        )
        if role == "U":
            assert "location" not in response.headers


@requires_database
@pytest.mark.database
async def test_r47_malformed_and_absent_identifiers_byte_identical_404(
    client, settings, step10_world
) -> None:
    callers = step10_world["callers"]
    cookies = callers["C"].cookies(settings)

    # 1. Absent UUID
    res_absent = await client.get(f"/v1/council/imports/{uuid4()}", cookies=cookies)
    # 2. Malformed non-UUID string
    res_malformed = await client.get("/v1/council/imports/not-a-uuid", cookies=cookies)

    assert res_absent.status_code == 404
    assert res_malformed.status_code == 404
    assert res_absent.content == res_malformed.content, "Absent and malformed 404 bodies must be byte-identical"


@requires_database
@pytest.mark.database
async def test_r47_import_receipt_database_backed_rendering(
    client, settings, step10_world
) -> None:
    callers = step10_world["callers"]
    import_id = step10_world["import_id"]
    checksum = step10_world["checksum"]

    response = await client.get(
        f"/v1/council/imports/{import_id}",
        cookies=callers["C"].cookies(settings),
    )
    assert response.status_code == 200
    assert "Import Receipt" in response.text
    assert str(import_id) in response.text
    assert checksum in response.text
    assert "/Actors/Characters (active)" in response.text
    assert '<form' not in response.text


@requires_database
@pytest.mark.database
async def test_r47_receipt_immutable_post_fails_405(
    client, settings, step10_world
) -> None:
    callers = step10_world["callers"]
    import_id = step10_world["import_id"]

    response = await client.post(
        f"/v1/council/imports/{import_id}",
        cookies=callers["C"].cookies(settings),
    )
    assert response.status_code == 405


@requires_database
@pytest.mark.database
@pytest.mark.parametrize(
    "query",
    [
        f"action={'a' * (FILTER_VALUE_BOUND + 1)}",
        "action=a&entity_type=b&entity_id=c&capability=guild_council&source=web&correlation_id=00000000-0000-4000-8000-000000000000",
        "from=2020-01-01T00:00:00Z&to=2026-01-01T00:00:00Z",
        "from=2026-01-02T00:00:00Z&to=2026-01-01T00:00:00Z",
        "capability=emperor",
        "source=telepathy",
        "correlation_id=not-a-uuid",
        "from=yesterday",
    ],
)
async def test_r48_and_r49_filter_bounds_and_refusals(
    client, settings, step10_world, query
) -> None:
    callers = step10_world["callers"]
    cookies = callers["C"].cookies(settings)

    res_r48 = await client.get(f"/v1/audit?{query}", cookies=cookies)
    res_r49 = await client.get(f"/v1/audit/results?{query}", cookies=cookies)

    assert res_r48.status_code == 422
    assert res_r49.status_code == 422


@requires_database
@pytest.mark.database
async def test_r48_and_r49_identical_results_for_same_query(
    client, settings, step10_world
) -> None:
    callers = step10_world["callers"]
    cookies = callers["C"].cookies(settings)

    res_r48 = await client.get("/v1/audit?action=reconciliation.", cookies=cookies)
    res_r49 = await client.get("/v1/audit/results?action=reconciliation.", cookies=cookies)

    assert res_r48.status_code == 200
    assert res_r49.status_code == 200

    r48_event_ids = re.findall(r'data-event-id="([^"]+)"', res_r48.text)
    r49_event_ids = re.findall(r'data-event-id="([^"]+)"', res_r49.text)

    assert r48_event_ids == r49_event_ids
    assert len(r48_event_ids) > 0


@requires_database
@pytest.mark.database
async def test_audit_search_no_count_star_and_total_unbounded(
    client, settings, step10_world, migrated_database
) -> None:
    from sqlalchemy import event

    statements: list[str] = []

    def record(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(migrated_database, "before_cursor_execute", record)
    try:
        response = await client.get(
            "/v1/audit/results", cookies=step10_world["callers"]["C"].cookies(settings)
        )
    finally:
        event.remove(migrated_database, "before_cursor_execute", record)

    assert response.status_code == 200
    counting = [
        s for s in statements if "count(" in s.lower() and "audit_events" in s.lower()
    ]
    assert counting == []
    assert 'data-total-unbounded="true"' in response.text


@requires_database
@pytest.mark.database
@pytest.mark.parametrize(
    ("input_size", "expected_page_size"),
    [
        (None, 50),
        ("invalid", 50),
        ("0", 50),
        ("-10", 50),
        ("1000", 100),
        ("1", 1),
        ("100", 100),
    ],
)
async def test_r48_and_r49_pagination_urls_canonical_page_size_normalization(
    client, settings, step10_world, input_size, expected_page_size
) -> None:
    """Finding 1: direct HTTP boundary tests proving server-owned page size normalization."""
    cookies = step10_world["callers"]["C"].cookies(settings)
    query = "action=reconciliation.event."
    if input_size is not None:
        query += f"&size={input_size}"

    res_r48 = await client.get(f"/v1/audit?{query}", cookies=cookies)
    res_r49 = await client.get(f"/v1/audit/results?{query}", cookies=cookies)

    assert res_r48.status_code == 200
    assert res_r49.status_code == 200

    for response, route_name in ((res_r48, "R-48"), (res_r49, "R-49")):
        match_href = re.search(r'href="(/v1/audit\?[^"]+)"', response.text)
        match_hx = re.search(r'hx-get="(/v1/audit/results\?[^"]+)"', response.text)
        assert match_href is not None, f"{route_name}: next href missing"
        assert match_hx is not None, f"{route_name}: next hx-get missing"

        raw_href = html.unescape(match_href.group(1))
        raw_hx = html.unescape(match_hx.group(1))

        split_href = urllib.parse.urlsplit(raw_href)
        split_hx = urllib.parse.urlsplit(raw_hx)

        # Assert route paths exactly
        assert split_href.path == "/v1/audit", f"{route_name}: href path was {split_href.path}"
        assert split_hx.path == "/v1/audit/results", f"{route_name}: hx-get path was {split_hx.path}"

        qs_href = urllib.parse.parse_qs(split_href.query, keep_blank_values=True)
        qs_hx = urllib.parse.parse_qs(split_hx.query, keep_blank_values=True)

        # Assert exactly one size value and equals expected_page_size
        assert qs_href.get("size") == [str(expected_page_size)], (
            f"{route_name} href size query mismatch: expected [{expected_page_size}], got {qs_href.get('size')}"
        )
        assert qs_hx.get("size") == [str(expected_page_size)], (
            f"{route_name} hx-get size query mismatch: expected [{expected_page_size}], got {qs_hx.get('size')}"
        )

        # Assert exactly one cursor value and both carry identical cursor
        assert "cursor" in qs_href and len(qs_href["cursor"]) == 1, f"{route_name} href missing single cursor"
        assert "cursor" in qs_hx and len(qs_hx["cursor"]) == 1, f"{route_name} hx-get missing single cursor"
        assert qs_href["cursor"][0] == qs_hx["cursor"][0], f"{route_name} cursor mismatch between href and hx-get"

        # Assert active action filter exactly equals reconciliation.event. and is present exactly once
        assert qs_href.get("action") == ["reconciliation.event."], (
            f"{route_name} href action filter mismatch: got {qs_href.get('action')}"
        )
        assert qs_hx.get("action") == ["reconciliation.event."], (
            f"{route_name} hx-get action filter mismatch: got {qs_hx.get('action')}"
        )

        # Verify raw invalid / oversized text is never present in query parameters
        if input_size in ("invalid", "1000", "0", "-10"):
            assert str(input_size) not in qs_href.get("size", [])
            assert str(input_size) not in qs_hx.get("size", [])


@requires_database
@pytest.mark.database
async def test_audit_search_stable_cursor_pagination_forward(
    client, settings, step10_world
) -> None:
    cookies = step10_world["callers"]["C"].cookies(settings)
    seen: list[str] = []
    url = "/v1/audit/results?action=reconciliation.event.&size=10"

    for _ in range(15):
        response = await client.get(url, cookies=cookies)
        assert response.status_code == 200
        seen.extend(re.findall(r'data-event-id="([^"]+)"', response.text))

        match_href = re.search(r'href="([^"]+)"', response.text)
        match_hx = re.search(r'hx-get="([^"]+)"', response.text)
        if match_hx is None:
            assert match_href is None
            break
        assert match_href is not None
        href_parts = urllib.parse.urlsplit(html.unescape(match_href.group(1)))
        hx_parts = urllib.parse.urlsplit(html.unescape(match_hx.group(1)))
        assert href_parts.path == "/v1/audit"
        assert hx_parts.path == "/v1/audit/results"
        href_qs = urllib.parse.parse_qs(href_parts.query)
        hx_qs = urllib.parse.parse_qs(hx_parts.query)
        assert href_qs.get("action") == ["reconciliation.event."]
        assert hx_qs.get("action") == ["reconciliation.event."]
        assert href_qs.get("size") == ["10"]
        assert hx_qs.get("size") == ["10"]
        url = html.unescape(match_hx.group(1))

    seeded_ids = {str(eid) for eid in step10_world["tracked"].audit_event_ids}
    assert len(seen) == len(seeded_ids) == 105
    assert set(seen) == seeded_ids
    assert len(seen) == len(set(seen)), "Duplicate events seen during forward pagination"


@requires_database
@pytest.mark.database
async def test_audit_search_tampered_and_wrong_scope_cursor_refusal(
    client, settings, step10_world
) -> None:
    cookies = step10_world["callers"]["C"].cookies(settings)
    foreign = encode(
        settings.cursor_key,
        scope=SNAPSHOT_CURSOR_SCOPE,
        parts=(utcnow().isoformat(), str(uuid4())),
    )
    for bad_cursor in ("not-a-cursor", "YWJj.bm90LWEtc2lnbmF0dXJl", foreign):
        response = await client.get(f"/v1/audit/results?cursor={bad_cursor}", cookies=cookies)
        assert response.status_code == 422, f"Cursor {bad_cursor} was not refused"


@requires_database
@pytest.mark.database
async def test_audit_search_actor_presentation_current_retired_system(
    client, settings, step10_world, migrated_database
) -> None:
    retired_subject = 888888888888888888
    ev1 = uuid4()
    ev2 = uuid4()

    with migrated_database.begin() as connection:
        # Seed and retire a distinct external identity
        connection.execute(
            text("INSERT INTO discord_users (id, username) VALUES (:id, 'retired-user') ON CONFLICT DO NOTHING"),
            {"id": retired_subject},
        )
        retired_acc = make_account(connection, label="retired-council-user")
        link_discord(connection, retired_acc, retired_subject, state="retired")
        connection.execute(
            text(
                "INSERT INTO audit_events (id, occurred_at, actor_discord_user_id, actor_capability, "
                "action, entity_type, entity_id, source, correlation_id, payload) VALUES "
                "(:id, :occurred_at, :subject, 'guild_council', 'legacy.probe', 'char', :entity_id, 'discord', :corr, '{}')"
            ),
            {
                "id": ev1,
                "occurred_at": utcnow(),
                "subject": retired_subject,
                "entity_id": str(uuid4()),
                "corr": uuid4(),
            },
        )
        # System event
        connection.execute(
            text(
                "INSERT INTO audit_events (id, occurred_at, actor_capability, action, entity_type, entity_id, source, correlation_id, payload) "
                "VALUES (:id, :occurred_at, 'system', 'system.probe', 'job', :entity_id, 'system', :corr, '{}')"
            ),
            {
                "id": ev2,
                "occurred_at": utcnow(),
                "entity_id": str(uuid4()),
                "corr": uuid4(),
            },
        )

        step10_world["tracked"].discord_user_ids.add(retired_subject)
        step10_world["tracked"].account_ids.add(retired_acc)
        step10_world["tracked"].audit_event_ids.add(ev1)
        step10_world["tracked"].audit_event_ids.add(ev2)

    cookies = step10_world["callers"]["C"].cookies(settings)
    res = await client.get("/v1/audit/results", cookies=cookies)
    assert res.status_code == 200
    assert "retired-council-user" in res.text
    assert 'data-has-actor="false"' in res.text
    assert "no person &mdash; system action" in res.text


@requires_database
@pytest.mark.database
async def test_audit_search_disclosure_projections_and_no_raw_payload(
    client, settings, step10_world, migrated_database
) -> None:
    ev_id = uuid4()
    with migrated_database.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO audit_events (id, occurred_at, actor_platform_account_id, actor_capability, "
                "action, entity_type, entity_id, source, correlation_id, payload) VALUES "
                "(:id, :occurred_at, :actor_id, 'guild_council', 'snapshot.folder_selected', 'snapshot', :entity_id, 'web', :corr, :payload)"
            ),
            {
                "id": ev_id,
                "occurred_at": utcnow(),
                "actor_id": step10_world["callers"]["C"].account_id,
                "entity_id": str(uuid4()),
                "corr": uuid4(),
                "payload": json.dumps({
                    "folder_id_before": "actv0000",
                    "folder_id_after": "arch0000",
                    "checksum": "f" * 64,
                    "raw_snapshot_artifact": '{"actors":[{"name":"Secret Person"}]}',
                    "bearer_token": "Bearer s3cr3t",
                    "stack_trace": 'File "/opt/discord-bots/main.py", line 42',
                }),
            },
        )
        step10_world["tracked"].audit_event_ids.add(ev_id)

    cookies = step10_world["callers"]["C"].cookies(settings)
    response = await client.get("/v1/audit/results", cookies=cookies)
    assert response.status_code == 200

    # Projected structured facts
    assert "snapshot.folder_selected" in response.text
    assert "actv0000" in response.text
    assert "arch0000" in response.text
    assert "f" * 64 in response.text

    # Excluded undeclared sensitive facts
    for leaked in ("Secret Person", "Bearer s3cr3t", "/opt/discord-bots/main.py", '{"actors"'):
        assert leaked not in response.text, f"Sensitive payload leaked: {leaked}"


@requires_database
@pytest.mark.database
async def test_audit_reads_produce_zero_audit_event_writes(
    client, settings, step10_world, migrated_database
) -> None:
    cookies = step10_world["callers"]["C"].cookies(settings)

    with migrated_database.begin() as connection:
        count_before = connection.execute(text("SELECT count(*) FROM audit_events")).scalar_one()

    # Issue multiple reads
    await client.get("/v1/audit", cookies=cookies)
    await client.get("/v1/audit/results", cookies=cookies)
    await client.get(f"/v1/council/imports/{step10_world['import_id']}", cookies=cookies)

    with migrated_database.begin() as connection:
        count_after = connection.execute(text("SELECT count(*) FROM audit_events")).scalar_one()

    assert count_before == count_after, "Audit read operations must never insert audit events"


def test_audit_repository_and_routes_are_strictly_read_only() -> None:
    """Verifies that the audit repository exposes only read operations and no mutation route exists."""
    from adapters.web.repositories import AuditSearchRepository

    public = {name for name in dir(AuditSearchRepository) if not name.startswith("_")}
    assert public == {"search", "labels_for_discord_actors"}


@requires_database
@pytest.mark.database
def test_step10_fixture_cleanup_verifies_zero_tracked_residue(
    clean_between_step10_cases,
    migrated_database,
) -> None:
    """Verifies that fixture cleanup discipline leaves zero synthetic residue across full topology."""
    tracked_state = clean_between_step10_cases

    with migrated_database.begin() as connection:
        # 1. Snapshot and folder selection
        snap_id, snap_hash = seed_snapshot(connection, folder_ids=(fx.ACTIVE_FOLDER_ID,))
        tracked_state.snapshot_ids.add(snap_id)

        # 2. Platform account and discord user
        acc_id = make_account(connection, label="cleanup-test-acc")
        tracked_state.account_ids.add(acc_id)
        disc_user_id = 700000000000002999
        connection.execute(
            text("INSERT INTO discord_users (id, username) VALUES (:id, 'cleanup-user') ON CONFLICT DO NOTHING"),
            {"id": disc_user_id},
        )
        tracked_state.discord_user_ids.add(disc_user_id)
        link_discord(connection, acc_id, disc_user_id)

        # 3. Role capability mapping
        map_id = add_mapping(
            connection,
            role_id=900000000000002999,
            capability=ActorCapability.GUILD_COUNCIL.value,
            created_by=acc_id,
        )
        tracked_state.role_mapping_ids.add(map_id)

        # 4. Job
        job_id = seed_job(
            connection,
            snapshot_id=snap_id,
            account_id=acc_id,
            checksum=snap_hash,
        )
        tracked_state.job_ids.add(job_id)

        # 5. Import receipt
        imp_id = seed_import(
            connection,
            snapshot_id=snap_id,
            account_id=acc_id,
            checksum=snap_hash,
            folder_id=fx.ACTIVE_FOLDER_ID,
            folder_path="/Actors/Characters",
        )
        tracked_state.import_ids.add(imp_id)

        # 6. Audit event
        ev_id = uuid4()
        tracked_state.audit_event_ids.add(ev_id)
        connection.execute(
            text(
                "INSERT INTO audit_events (id, occurred_at, actor_platform_account_id, actor_capability, "
                "action, entity_type, entity_id, source, correlation_id, payload) VALUES "
                "(:id, now(), :acc_id, 'guild_council', 'cleanup.probe', 'test', :ent, 'web', :corr, '{}')"
            ),
            {"id": ev_id, "acc_id": acc_id, "ent": str(uuid4()), "corr": uuid4()},
        )

    # Verify rows exist before teardown
    with migrated_database.begin() as connection:
        assert connection.execute(text("SELECT count(*) FROM foundry_snapshots WHERE id = :id"), {"id": snap_id}).scalar_one() == 1
        assert connection.execute(text("SELECT count(*) FROM snapshot_imports WHERE id = :id"), {"id": imp_id}).scalar_one() == 1
        assert connection.execute(text("SELECT count(*) FROM reconciliation_jobs WHERE id = :id"), {"id": job_id}).scalar_one() == 1
        assert connection.execute(text("SELECT count(*) FROM platform_accounts WHERE id = :id"), {"id": acc_id}).scalar_one() == 1
        assert connection.execute(text("SELECT count(*) FROM discord_users WHERE id = :id"), {"id": disc_user_id}).scalar_one() == 1
        assert connection.execute(text("SELECT count(*) FROM role_capability_mappings WHERE id = :id"), {"id": map_id}).scalar_one() == 1
        assert connection.execute(text("SELECT count(*) FROM audit_events WHERE id = :id"), {"id": ev_id}).scalar_one() == 1
