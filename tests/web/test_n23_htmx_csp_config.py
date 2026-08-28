"""N-23: HTMX must not inject an inline style the CSP forbids.

Found on 2026-08-26 by an operator reading a browser console during the SP-29
gate-off window — a class of defect parsed-DOM automation cannot produce, because
it does not execute HTMX inside an engine enforcing a policy:

    htmx-2.0.10.min.js:1 Applying inline style violates the following Content
    Security Policy directive 'style-src 'self''. … The action has been blocked.

Nothing broke: no template uses `hx-indicator`, and the stylesheet defines no
`.htmx-indicator` rules. The violation mattered because a console with a
permanent error in it is one where the next error is missed.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BASE_TEMPLATE = ROOT / "adapters" / "web" / "templates" / "base.html"


def test_the_config_disables_indicator_style_injection() -> None:
    markup = BASE_TEMPLATE.read_text(encoding="utf-8")

    match = re.search(
        r"""<meta\s+name=["']htmx-config["']\s+content=(["'])(.*?)\1""", markup
    )
    assert match, "base.html carries no htmx-config meta tag"

    config = json.loads(match.group(2))
    assert config["includeIndicatorStyles"] is False


def test_the_config_precedes_the_htmx_script() -> None:
    """Ordering is the whole mechanism.

    HTMX reads the meta tag when it initialises. A tag placed after the script
    would parse as valid JSON, assert cleanly here, and do nothing at all.
    """
    markup = BASE_TEMPLATE.read_text(encoding="utf-8")

    meta_at = markup.find('name="htmx-config"')
    script_at = markup.find("htmx-2.0.10")
    assert meta_at != -1 and script_at != -1
    assert meta_at < script_at, "the config must appear before the htmx script"


def test_no_template_relies_on_the_feature_being_disabled() -> None:
    """The reason this is safe, asserted rather than assumed.

    Turning indicator styles off is only harmless while nothing uses
    `hx-indicator`. If a later template adds one, this fails and whoever added it
    learns they must style `.htmx-indicator` in the stylesheet themselves.
    """
    # The *attribute*, not the bare word: base.html's own comment explains the
    # feature by name, and matching that would make this check permanently red
    # for documenting itself.
    attribute = re.compile(r"""\bhx-indicator\s*=""")
    templates = (ROOT / "adapters" / "web" / "templates").rglob("*.html")
    offenders = [
        path.relative_to(ROOT)
        for path in templates
        if attribute.search(path.read_text(encoding="utf-8"))
    ]

    assert offenders == [], (
        "these templates use hx-indicator, whose styling is disabled by the "
        f"N-23 config: {offenders}. Define .htmx-indicator in the stylesheet."
    )


@pytest.mark.anyio
async def test_a_rendered_page_carries_the_config(client) -> None:
    """The template is not the served page; this checks what a browser receives."""
    response = await client.get("/v1/login")

    assert response.status_code == 200
    body = response.text
    assert 'name="htmx-config"' in body
    assert "includeIndicatorStyles" in body
    assert body.find('name="htmx-config"') < body.find("htmx-2.0.10")
