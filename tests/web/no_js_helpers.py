"""Shared No-JavaScript Fallback Validation Helpers.

Provides canonical contract types and validation routines for progressive-enhancement
and no-JavaScript fallback testing across Phase 3.4 test suites.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class FormContract:
    """Declared expectation for a server-rendered HTML form."""

    action: str
    method: str
    selector: str | None = None
    requires_csrf: bool = False
    expected_csrf_token: str | None = None
    required_hidden_fields: dict[str, str | None] | None = None
    allowed_hidden_fields: frozenset[str] | None = None


@dataclass(frozen=True)
class FlowContract:
    """Declared expectation for an essential application user flow."""

    flow_name: str
    expected_forms: tuple[FormContract, ...] = ()
    expected_link_prefixes: tuple[str, ...] = ()


def clean_html_source(html_text: str) -> str:
    """Strips Jinja comment blocks {# ... #} so comments containing HTML snippets are not parsed."""
    return re.sub(r"\{#.*?#\}", "", html_text, flags=re.DOTALL)


def strip_htmx_attributes(html_text: str) -> str:
    """Removes all hx-* attributes from in-memory HTML to test non-JS fallback purity."""
    soup = BeautifulSoup(html_text, "html.parser")
    for tag in soup.find_all(True):
        hx_attrs = [attr for attr in list(tag.attrs.keys()) if attr.lower().startswith("hx-")]
        for attr in hx_attrs:
            del tag[attr]
    return str(soup)


def _matches_registered_route(app: Any, action_path: str, expected_method: str) -> bool:
    """Checks if action_path matches an app.routes registration (supporting {param} patterns)."""
    expected_method = expected_method.upper()
    action_clean = action_path.split("?", 1)[0]
    for route in getattr(app, "routes", []):
        r_path = getattr(route, "path", None)
        r_methods = getattr(route, "methods", None)
        if not r_path or not r_methods:
            continue
        if expected_method not in {m.upper() for m in r_methods}:
            continue
        if r_path == action_clean:
            return True
        pattern = "^" + re.sub(r"\{[^}]+\}", r"[^/]+", r_path) + "$"
        if re.match(pattern, action_clean):
            return True
    return False


def validate_rendered_no_js_fallback(
    rendered_html: str,
    contract: FlowContract,
    app: Any | None = None,
) -> None:
    """Proves rendered forms and links retain valid actions, POST methods, CSRF tokens, exact hidden fields, and non-empty hrefs."""
    clean = clean_html_source(rendered_html)
    soup = BeautifulSoup(clean, "html.parser")

    # 1. Form fallbacks
    for expected in contract.expected_forms:
        if expected.selector:
            matching_forms = soup.select(expected.selector)
            assert len(matching_forms) == 1, (
                f"{contract.flow_name}: Expected exactly 1 form matching selector '{expected.selector}', found {len(matching_forms)}"
            )
            form = matching_forms[0]
        else:
            matching_forms = [
                f for f in soup.find_all("form")
                if f.get("action") == expected.action and f.get("method", "").upper() == expected.method.upper()
            ]
            assert len(matching_forms) == 1, (
                f"{contract.flow_name}: Expected exactly 1 form with action='{expected.action}' and method='{expected.method}', found {len(matching_forms)}"
            )
            form = matching_forms[0]

        action = form.get("action")
        assert action, f"{contract.flow_name}: Form missing action attribute: {form}"
        assert not action.startswith("javascript:"), f"{contract.flow_name}: Form action uses javascript: URL: {action}"
        assert action != "#", f"{contract.flow_name}: Form action uses placeholder '#' destination: {form}"
        assert action == expected.action, (
            f"{contract.flow_name}: Expected form action '{expected.action}', got '{action}'"
        )

        method = form.get("method", "").upper()
        assert method in {"GET", "POST"}, f"{contract.flow_name}: Form has non-standard method '{method}': {form}"
        assert method == expected.method.upper(), (
            f"{contract.flow_name}: Expected form method '{expected.method}', got '{method}'"
        )

        if app is not None:
            assert _matches_registered_route(app, action, method), (
                f"{contract.flow_name}: Form action '{action}' with method '{method}' is not a registered route in app.routes"
            )

        # Determine the complete set of permitted hidden input names for this form
        if expected.allowed_hidden_fields is not None:
            permitted_hidden_names = set(expected.allowed_hidden_fields)
        else:
            permitted_hidden_names = set()
            if expected.requires_csrf:
                permitted_hidden_names.add("csrf_token")
            if expected.required_hidden_fields:
                permitted_hidden_names.update(expected.required_hidden_fields.keys())

        # Inspect all hidden input elements in the selected form
        all_hidden_inputs = form.find_all("input", attrs={"type": "hidden"})
        for hidden_input in all_hidden_inputs:
            h_name = hidden_input.get("name")
            assert h_name and h_name.strip(), (
                f"{contract.flow_name}: Form contains hidden input missing or with empty 'name' attribute: {hidden_input}"
            )
            assert h_name in permitted_hidden_names, (
                f"{contract.flow_name}: Form contains unrecognized hidden input '{h_name}' not in allowed hidden fields {sorted(permitted_hidden_names)}: {hidden_input}"
            )

        if expected.requires_csrf:
            csrf_inputs = form.find_all("input", attrs={"name": "csrf_token", "type": "hidden"})
            assert len(csrf_inputs) == 1, (
                f"{contract.flow_name}: Expected exactly 1 hidden input named 'csrf_token', found {len(csrf_inputs)}"
            )
            csrf_val = csrf_inputs[0].get("value", "")
            assert csrf_val.strip(), f"{contract.flow_name}: Hidden CSRF token value is empty"
            if expected.expected_csrf_token is not None:
                assert csrf_val == expected.expected_csrf_token, (
                    f"{contract.flow_name}: CSRF token mismatch: expected {expected.expected_csrf_token}, got {csrf_val}"
                )
        else:
            csrf_inputs = form.find_all("input", attrs={"name": "csrf_token", "type": "hidden"})
            assert len(csrf_inputs) == 0, (
                f"{contract.flow_name}: CSRF token input unexpectedly present on CSRF-exempt form: {form}"
            )

        if expected.required_hidden_fields:
            for field_name, expected_val in expected.required_hidden_fields.items():
                hidden_inputs = form.find_all("input", attrs={"type": "hidden", "name": field_name})
                assert len(hidden_inputs) == 1, (
                    f"{contract.flow_name}: Expected exactly 1 hidden input '{field_name}', found {len(hidden_inputs)}"
                )
                actual_val = hidden_inputs[0].get("value")
                assert actual_val is not None, (
                    f"{contract.flow_name}: Hidden field '{field_name}' missing value attribute"
                )
                if expected_val is not None:
                    assert actual_val == expected_val, (
                        f"{contract.flow_name}: Hidden field '{field_name}' mismatch: expected '{expected_val}', got '{actual_val}'"
                    )

    # 2. Link fallbacks
    all_links = soup.find_all("a")
    for link in all_links:
        if link.has_attr("href"):
            href = link["href"]
            assert href.strip(), f"{contract.flow_name}: Link has empty href: {link}"
            assert not href.startswith("javascript:"), f"{contract.flow_name}: Link uses javascript: URL: {href}"
            if link.get("role") != "button" and "skip-link" not in link.get("class", []):
                assert href != "#", f"{contract.flow_name}: Interactive link uses placeholder '#' destination: {link}"

    for prefix in contract.expected_link_prefixes:
        matching = [l for l in all_links if l.get("href", "").startswith(prefix)]
        assert len(matching) >= 1, (
            f"{contract.flow_name}: Expected link with prefix '{prefix}', none found"
        )
        if app is not None:
            base_prefix = prefix.split("?", 1)[0]
            assert _matches_registered_route(app, base_prefix, "GET"), (
                f"{contract.flow_name}: Expected link route '{base_prefix}' is not a registered GET route in app.routes"
            )

    # 3. No inline event handlers or script-created actions
    for tag in soup.find_all(True):
        for attr in tag.attrs:
            assert not attr.lower().startswith("on"), f"{contract.flow_name}: Found forbidden inline event handler '{attr}': {tag}"
            assert not attr.lower().startswith("hx-on"), f"{contract.flow_name}: Found forbidden 'hx-on:' handler '{attr}': {tag}"


def validate_exact_canonical_correlation_uuid(response: Any) -> UUID:
    """The correlation id shown in the rendered response, strictly validated.

    Requirements:
    1. Exactly one .reference-code element in the response.
    2. Exactly one direct text node (NavigableString), no child markup, comments, or mixed content.
    3. Non-empty string.
    4. Exact plain canonical lowercase hyphenated UUID: raw_text == str(UUID(raw_text)).
       Rejects whitespace, uppercase, braces, URNs, unhyphenated hex, and prose wrappers.
    """
    from bs4 import Comment, NavigableString

    soup = BeautifulSoup(response.text, "html.parser")
    ref_elements = soup.select(".reference-code")
    if not ref_elements:
        raise AssertionError("no correlation reference element (.reference-code) in the rendered response")
    if len(ref_elements) > 1:
        raise AssertionError(f"expected exactly one correlation reference element (.reference-code), found {len(ref_elements)}")

    el = ref_elements[0]
    if len(el.contents) != 1 or not isinstance(el.contents[0], NavigableString) or isinstance(el.contents[0], Comment):
        raise AssertionError(f"correlation reference element contains child markup, comments, or mixed content: {el.contents!r}")

    raw_text = str(el.contents[0])
    if not raw_text:
        raise AssertionError("correlation reference element (.reference-code) is empty")

    try:
        parsed = UUID(raw_text)
    except ValueError as exc:
        raise AssertionError(f"correlation reference text {raw_text!r} is not a valid UUID") from exc

    if raw_text != str(parsed):
        raise AssertionError(f"correlation reference text {raw_text!r} is not in exact canonical UUID format")

    return parsed

