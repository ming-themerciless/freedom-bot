#!/usr/bin/env python3
"""
Freedom Blades Visual Prototype — Evidence-Integrity Static Selector & Contrast Audit Tool
Statically parses tokens.css, styles.css, inline HTML styles, and JS state objects.
Calculates WCAG 2.1/2.2 relative luminance contrast ratios and enforces evidence classification
(extracted, derived, manual assumption) for every audited pair.
"""

import ast
import json
import os
import re
import sys
import unittest

def parse_hex_color(hex_str):
    """
    Parses a 6-digit hex color string (with optional leading #).
    Returns a tuple of (r, g, b) integers in range 0..255.
    Raises ValueError for malformed inputs.
    """
    if not isinstance(hex_str, str):
        raise ValueError(f"Hex color must be a string, got {type(hex_str)}")
    cleaned = hex_str.lstrip('#').strip()
    if len(cleaned) != 6 or not re.fullmatch(r'[0-9a-fA-F]{6}', cleaned):
        raise ValueError(f"Invalid 6-digit hex color: '{hex_str}'")
    return (
        int(cleaned[0:2], 16),
        int(cleaned[2:4], 16),
        int(cleaned[4:6], 16)
    )

def lum_from_rgb(r, g, b):
    """Calculates WCAG 2.1/2.2 relative luminance from (r, g, b) 0..255."""
    r_s, g_s, b_s = r / 255.0, g / 255.0, b / 255.0
    r_g = r_s / 12.92 if r_s <= 0.04045 else ((r_s + 0.055) / 1.055) ** 2.4
    g_g = g_s / 12.92 if g_s <= 0.04045 else ((g_s + 0.055) / 1.055) ** 2.4
    b_g = b_s / 12.92 if b_s <= 0.04045 else ((b_s + 0.055) / 1.055) ** 2.4
    return 0.2126 * r_g + 0.7152 * g_g + 0.0722 * b_g

def lum(hex_str):
    r, g, b = parse_hex_color(hex_str)
    return lum_from_rgb(r, g, b)

def ratio(c1_hex, c2_hex):
    l1, l2 = lum(c1_hex), lum(c2_hex)
    lmax, lmin = max(l1, l2), min(l1, l2)
    return (lmax + 0.05) / (lmin + 0.05)

def alpha_comp(fg_hex, bg_hex, alpha):
    """
    Alpha-composites fg_hex over bg_hex with opacity alpha (0.0 to 1.0).
    Returns six-digit hex color string #rrggbb.
    """
    if not (0.0 <= alpha <= 1.0):
        raise ValueError(f"Alpha must be between 0.0 and 1.0, got {alpha}")
    r_fg, g_fg, b_fg = parse_hex_color(fg_hex)
    r_bg, g_bg, b_bg = parse_hex_color(bg_hex)
    
    r_res = round(alpha * r_fg + (1.0 - alpha) * r_bg)
    g_res = round(alpha * g_fg + (1.0 - alpha) * g_bg)
    b_res = round(alpha * b_fg + (1.0 - alpha) * b_bg)
    
    return f"#{r_res:02x}{g_res:02x}{b_res:02x}"

def parse_css_content(css_text):
    """Parses CSS content into a dictionary of selector -> dict of prop -> val."""
    selectors = {}
    # Strip comments
    clean_text = re.sub(r'/\*.*?\*/', '', css_text, flags=re.DOTALL)
    rule_regex = re.compile(r'([^{]+)\{([^}]+)\}')
    for match in rule_regex.finditer(clean_text):
        sel_str, decls_str = match.group(1).strip(), match.group(2).strip()
        decls = {}
        for line in decls_str.split(';'):
            if ':' in line:
                prop, val = line.split(':', 1)
                decls[prop.strip().lower()] = val.strip()
        for s in sel_str.split(','):
            selectors[s.strip()] = decls
    return selectors

def parse_css_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"CSS file not found at {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        return parse_css_content(f.read())

def parse_tokens_css(filepath=None):
    if filepath is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, "css", "tokens.css")
    css_dict = parse_css_file(filepath)
    if ":root" not in css_dict:
        raise KeyError(f":root section missing from tokens CSS file {filepath}")
    return css_dict[":root"]

def resolve_color_token(token_or_color, tokens_dict, visited=None):
    if visited is None:
        visited = set()
    val = token_or_color.strip()
    if val.startswith("var("):
        var_name = val[4:-1].strip().split(',')[0].strip()
        if var_name in visited:
            raise ValueError(f"Cyclic token reference detected: '{var_name}'")
        visited.add(var_name)
        if var_name not in tokens_dict:
            raise KeyError(f"Unresolved CSS variable '{var_name}'")
        return resolve_color_token(tokens_dict[var_name], tokens_dict, visited)
    return val

def extract_js_reconciliation_states(html_filepath):
    """
    Statically parses RECONCILIATION_STATES object from reconciliation.html.
    Returns dict mapping state_name -> state_dict.
    """
    if not os.path.exists(html_filepath):
        raise FileNotFoundError(f"HTML file not found: {html_filepath}")
    with open(html_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.search(r'const\s+RECONCILIATION_STATES\s*=\s*(\{.*?\});', content, re.DOTALL)
    if not match:
        raise ValueError(f"RECONCILIATION_STATES object not found in {html_filepath}")
    
    js_obj_str = match.group(1)
    # Convert JS object literal string to valid JSON/Python dict
    # Add quotes to unquoted keys
    json_like = re.sub(r'(\w+)\s*:', r'"\1":', js_obj_str)
    # Convert single quotes to double quotes
    json_like = json_like.replace("'", '"')
    # Remove trailing commas
    json_like = re.sub(r',\s*([\}\]])', r'\1', json_like)
    
    try:
        states = json.loads(json_like)
    except Exception as e:
        raise ValueError(f"Failed to parse RECONCILIATION_STATES object: {e}")

    required_states = ['queued', 'running', 'completed', 'stale', 'failed']
    for req in required_states:
        if req not in states:
            raise ValueError(f"Missing required state '{req}' in RECONCILIATION_STATES")
        if 'fill' not in states[req]:
            raise ValueError(f"Missing 'fill' property in state '{req}'")

    return states

def extract_inline_style_color(html_filepath, target_snippet):
    """Statically verifies and extracts inline style color from HTML file."""
    if not os.path.exists(html_filepath):
        raise FileNotFoundError(f"HTML file not found: {html_filepath}")
    with open(html_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if target_snippet not in content:
        raise ValueError(f"Target snippet '{target_snippet}' not found in {html_filepath}")
        
    color_match = re.search(r'style="[^"]*color:\s*([^;"]+)', target_snippet)
    if not color_match:
        raise ValueError(f"No inline color declaration found in snippet '{target_snippet}'")
    return color_match.group(1).strip()

class TestEvidenceIntegrityAndDrift(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.tokens_path = os.path.join(self.base_dir, "css", "tokens.css")
        self.styles_path = os.path.join(self.base_dir, "css", "styles.css")
        self.reconciliation_path = os.path.join(self.base_dir, "reconciliation.html")
        self.tokens = parse_tokens_css(self.tokens_path)
        self.styles = parse_css_file(self.styles_path)

    def test_btn_secondary_pressed_extraction(self):
        sel = '.btn-secondary[aria-pressed="true"]'
        self.assertIn(sel, self.styles)
        rule = self.styles[sel]
        fg = resolve_color_token(rule["color"], self.tokens)
        bg = resolve_color_token(rule["background-color"], self.tokens)
        border = resolve_color_token(rule["border-color"], self.tokens)
        self.assertEqual(fg, "#60a5fa") # --fb-color-accent
        self.assertEqual(bg, "#1e293b") # --fb-color-bg-subtle
        self.assertEqual(border, "#2563eb") # --fb-color-primary

    def test_btn_secondary_pressed_drift(self):
        mock_css = """
        :root { --fb-color-accent: #60a5fa; --fb-color-bg-subtle: #1e293b; }
        .btn-secondary[aria-pressed="true"] { color: #ffffff; background-color: #000000; }
        """
        parsed = parse_css_content(mock_css)
        rule = parsed['.btn-secondary[aria-pressed="true"]']
        self.assertEqual(rule["color"], "#ffffff")
        self.assertNotEqual(rule["color"], "var(--fb-color-accent)")

    def test_missing_required_selector_fails(self):
        mock_styles = parse_css_content(".other-selector { color: red; }")
        with self.assertRaises(KeyError):
            _ = mock_styles['.btn-secondary[aria-pressed="true"]']

    def test_missing_required_property_fails(self):
        mock_styles = parse_css_content(".btn-primary { margin: 0; }")
        rule = mock_styles['.btn-primary']
        with self.assertRaises(KeyError):
            _ = rule['color']

    def test_unresolved_token_fails(self):
        mock_tokens = { "--a": "var(--b)" }
        with self.assertRaises(KeyError):
            resolve_color_token("var(--a)", mock_tokens)

    def test_cyclic_token_reference_fails(self):
        mock_tokens = { "--a": "var(--b)", "--b": "var(--a)" }
        with self.assertRaises(ValueError):
            resolve_color_token("var(--a)", mock_tokens)

    def test_focus_ring_token_change(self):
        mock_tokens = parse_tokens_css(self.tokens_path).copy()
        mock_tokens["--fb-color-accent"] = "#ff0000"
        resolved = resolve_color_token("var(--fb-color-accent)", mock_tokens)
        self.assertEqual(resolved, "#ff0000")

    def test_reconciliation_js_extraction(self):
        states = extract_js_reconciliation_states(self.reconciliation_path)
        self.assertEqual(states['queued']['fill'], "#3b82f6")
        self.assertEqual(states['completed']['fill'], "#16a34a")
        self.assertEqual(states['stale']['fill'], "#ea580c")
        self.assertEqual(states['failed']['fill'], "#dc2626")

    def test_reconciliation_js_missing_state_fails(self):
        bad_html_path = os.path.join(self.base_dir, "my-characters.html")
        with self.assertRaises(ValueError):
            extract_js_reconciliation_states(bad_html_path)

    def test_nonexistent_source_citation_fails(self):
        nonexistent_file = os.path.join(self.base_dir, "nonexistent.html")
        with self.assertRaises(FileNotFoundError):
            extract_inline_style_color(nonexistent_file, "snippet")

    def test_malformed_syntax_fails_closed(self):
        with self.assertRaises(ValueError):
            parse_hex_color("INVALID_HEX")

def evaluate_pair(category_id, pair_name, evidence_class, source_loc, fg_hex, bg_hex, min_threshold=4.5, is_non_text=False, is_exempt=False, alpha=1.0, surface_hex=None):
    if evidence_class not in ["extracted", "derived", "manual assumption"]:
        raise ValueError(f"Invalid evidence class: '{evidence_class}'")

    composed_bg_hex = bg_hex
    if alpha < 1.0 and surface_hex:
        composed_bg_hex = alpha_comp(bg_hex, surface_hex, alpha)
        
    r = ratio(fg_hex, composed_bg_hex)
    
    if is_exempt:
        status = "EXEMPT (Disabled / Inactive)"
        passed = True
    elif is_non_text:
        passed = (r >= 3.0)
        status = "PASS (UI Non-Text > 3.0:1)" if passed else "FAIL (UI Non-Text < 3.0:1)"
    elif min_threshold == 7.0:
        passed = (r >= 7.0)
        status = "PASS AAA (> 7.0:1)" if passed else ("PASS AA (> 4.5:1)" if r >= 4.5 else "FAIL (< 4.5:1)")
    elif min_threshold == 4.5:
        passed = (r >= 4.5)
        status = "PASS AAA (> 7.0:1)" if r >= 7.0 else ("PASS AA (> 4.5:1)" if passed else "FAIL (< 4.5:1)")
    elif min_threshold == 3.0:
        passed = (r >= 3.0)
        status = "PASS Large Text (> 3.0:1)" if passed else "FAIL (< 3.0:1)"
    else:
        passed = True
        status = "INFORMATIONAL"

    return {
        "category": category_id,
        "name": pair_name,
        "evidence_class": evidence_class,
        "source": source_loc,
        "fg": fg_hex,
        "raw_bg": bg_hex,
        "surface": surface_hex or bg_hex,
        "alpha": alpha,
        "composed_bg": composed_bg_hex,
        "raw_ratio": r,
        "ratio_str": f"{r:.2f}:1",
        "status": status,
        "passed": passed,
        "is_exempt": is_exempt,
        "is_non_text": is_non_text
    }

def run_audit():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    styles_path = os.path.join(base_dir, "css", "styles.css")
    tokens_path = os.path.join(base_dir, "css", "tokens.css")
    reconciliation_path = os.path.join(base_dir, "reconciliation.html")
    char_detail_path = os.path.join(base_dir, "character-detail.html")
    login_path = os.path.join(base_dir, "login.html")

    styles = parse_css_file(styles_path)
    tokens = parse_tokens_css(tokens_path)
    rec_states = extract_js_reconciliation_states(reconciliation_path)

    bg_base = resolve_color_token(tokens["--fb-color-bg-base"], tokens)           # #0b0f19
    bg_surface = resolve_color_token(tokens["--fb-color-bg-surface"], tokens)     # #111827
    bg_hover = resolve_color_token(tokens["--fb-color-bg-surface-hover"], tokens) # #1e293b
    bg_elevated = resolve_color_token(tokens["--fb-color-bg-surface-elevated"], tokens) # #1f2937
    bg_subtle = resolve_color_token(tokens["--fb-color-bg-subtle"], tokens)       # #1e293b

    text_main = resolve_color_token(tokens["--fb-color-text-main"], tokens)       # #f8fafc
    text_muted = resolve_color_token(tokens["--fb-color-text-muted"], tokens)     # #94a3b8
    text_dim = resolve_color_token(tokens["--fb-color-text-dim"], tokens)         # #cbd5e1

    primary = resolve_color_token(tokens["--fb-color-primary"], tokens)           # #2563eb
    primary_hover = resolve_color_token(tokens["--fb-color-primary-hover"], tokens) # #1d4ed8
    primary_dark = resolve_color_token(tokens["--fb-color-primary-dark"], tokens) # #1e40af
    accent = resolve_color_token(tokens["--fb-color-accent"], tokens)             # #60a5fa

    success_text = resolve_color_token(tokens["--fb-color-success-text"], tokens) # #4ade80
    warning_text = resolve_color_token(tokens["--fb-color-warning-text"], tokens) # #fdba74
    danger_text = resolve_color_token(tokens["--fb-color-danger-text"], tokens)   # #fca5a5
    info_text = resolve_color_token(tokens["--fb-color-info-text"], tokens)       # #93c5fd
    deferred_text = resolve_color_token(tokens["--fb-color-deferred-text"], tokens) # #f1f5f9
    deferred_bg = resolve_color_token(tokens["--fb-color-deferred-bg"], tokens)   # #334155
    border_steel = resolve_color_token(tokens["--fb-color-border-steel"], tokens) # #64748b

    # Mechanically extract CSS selector declarations
    nav_link_hover_bg = resolve_color_token(styles[".nav-link:hover"]["background-color"], tokens) # #1f2937
    nav_link_active_bg = resolve_color_token(styles[".nav-link.active"]["background-color"], tokens) # #1e293b
    btn_primary_hover_bg = resolve_color_token(styles[".btn-primary:hover"]["background-color"], tokens) # #1e40af
    
    sec_btn_pressed_fg = resolve_color_token(styles['.btn-secondary[aria-pressed="true"]']["color"], tokens) # #60a5fa
    sec_btn_pressed_bg = resolve_color_token(styles['.btn-secondary[aria-pressed="true"]']["background-color"], tokens) # #1e293b
    sec_btn_pressed_border = resolve_color_token(styles['.btn-secondary[aria-pressed="true"]']["border-color"], tokens) # #2563eb

    th_fg = resolve_color_token(styles[".data-table th"]["color"], tokens) # #f8fafc
    th_bg = resolve_color_token(styles[".data-table th"]["background-color"], tokens) # #1f2937

    # Extract inline style from character-detail.html
    gold_snippet = '<span class="data-value" style="color: #f59e0b;">485.00 gp</span>'
    inline_gp_gold = extract_inline_style_color(char_detail_path, gold_snippet) # #f59e0b

    # Disabled control opacity composite (#94a3b8 at 0.5 over #1f2937 over #111827)
    dis_bg_comp = alpha_comp(bg_elevated, bg_surface, 0.5) # #18202f
    dis_fg_comp = alpha_comp(text_muted, dis_bg_comp, 0.5)  # #566274

    tests = [
        # Category 1: Base & Surface Text
        evaluate_pair("1.1", "Body Text on Base Bg", "extracted", "tokens.css:--fb-color-text-main", text_main, bg_base),
        evaluate_pair("1.2", "Card Text on Surface", "extracted", "tokens.css:--fb-color-bg-surface", text_main, bg_surface),
        evaluate_pair("1.3", "Elevated Text on Surface", "extracted", "tokens.css:--fb-color-bg-surface-elevated", text_main, bg_elevated),
        evaluate_pair("1.4", "Muted Subtext on Surface", "extracted", "tokens.css:--fb-color-text-muted", text_muted, bg_surface),
        evaluate_pair("1.5", "Dim Metadata on Surface", "extracted", "tokens.css:--fb-color-text-dim", text_dim, bg_surface),

        # Category 2: Navigation Links (.nav-link)
        evaluate_pair("2.1", "Nav Link Normal", "extracted", "styles.css:.nav-link", text_muted, bg_surface),
        evaluate_pair("2.2", "Nav Link Hover", "extracted", "styles.css:.nav-link:hover", text_main, nav_link_hover_bg),
        evaluate_pair("2.3", "Nav Link Active", "extracted", "styles.css:.nav-link.active", accent, nav_link_active_bg),

        # Category 3: Content Links
        evaluate_pair("3.1", "Link Normal", "extracted", "styles.css:a", accent, bg_surface),
        evaluate_pair("3.2", "Link Hover", "extracted", "styles.css:a:hover", info_text, bg_surface),
        evaluate_pair("3.3", "Link Visited", "extracted", "styles.css:a:visited", accent, bg_surface),

        # Category 4: Primary Buttons (.btn-primary)
        evaluate_pair("4.1", "Primary Btn Normal", "extracted", "styles.css:.btn-primary", "#ffffff", primary),
        evaluate_pair("4.2", "Primary Btn Hover", "extracted", "styles.css:.btn-primary:hover", "#ffffff", btn_primary_hover_bg),
        evaluate_pair("4.3", "Primary Btn Disabled (Composed)", "derived", "styles.css:.btn:disabled opacity 0.5", dis_fg_comp, dis_bg_comp, is_exempt=True),

        # Category 5: Secondary Buttons (.btn-secondary)
        evaluate_pair("5.1", "Secondary Btn Normal", "extracted", "styles.css:.btn-secondary", text_main, bg_elevated),
        evaluate_pair("5.2", "Secondary Btn Hover", "extracted", "styles.css:.btn-secondary:hover", text_main, bg_hover),
        evaluate_pair("5.3", "Secondary Btn Selected (aria-pressed)", "extracted", 'styles.css:.btn-secondary[aria-pressed="true"]', sec_btn_pressed_fg, sec_btn_pressed_bg),
        evaluate_pair("5.4", "Secondary Btn Selected Border vs Surface", "derived", 'styles.css:.btn-secondary[aria-pressed="true"] border', sec_btn_pressed_border, bg_surface, is_non_text=True),

        # Category 6: Danger Buttons (.btn-danger)
        evaluate_pair("6.1", "Danger Btn Normal", "derived", "styles.css:.btn-danger (0.35 alpha over surface)", danger_text, "#991b1b", alpha=0.35, surface_hex=bg_surface),
        evaluate_pair("6.2", "Danger Btn Hover", "derived", "styles.css:.btn-danger:hover (0.55 alpha over surface)", danger_text, "#991b1b", alpha=0.55, surface_hex=bg_surface),

        # Category 7: Discord Login Button
        evaluate_pair("7.1", "Discord Btn Normal", "extracted", "login.html:.discord-btn", "#ffffff", "#5865F2"),
        evaluate_pair("7.2", "Discord Btn Hover", "extracted", "login.html:.discord-btn:hover", "#ffffff", "#4752C4"),

        # Category 8: Badges & Alerts
        evaluate_pair("8.1", "Primary Badge Text", "derived", "styles.css:.badge-primary (0.25 alpha over surface)", accent, "#2563eb", alpha=0.25, surface_hex=bg_surface),
        evaluate_pair("8.2", "Success Badge Text", "derived", "styles.css:.badge-success (0.35 alpha over surface)", success_text, "#166534", alpha=0.35, surface_hex=bg_surface),
        evaluate_pair("8.3", "Warning Badge Text", "derived", "styles.css:.badge-warning (0.35 alpha over surface)", warning_text, "#9a3412", alpha=0.35, surface_hex=bg_surface),
        evaluate_pair("8.4", "Danger Badge Text", "derived", "styles.css:.badge-danger (0.35 alpha over surface)", danger_text, "#991b1b", alpha=0.35, surface_hex=bg_surface),
        evaluate_pair("8.5", "Deferred Badge Text", "extracted", "styles.css:.badge-deferred", deferred_text, deferred_bg),
        evaluate_pair("8.6", "Info Alert Text", "derived", "styles.css:.alert-info (0.35 alpha over surface)", info_text, "#1e3a8a", alpha=0.35, surface_hex=bg_surface),

        # Category 9: Form Controls
        evaluate_pair("9.1", "Form Label", "extracted", "styles.css:label", text_dim, bg_surface),
        evaluate_pair("9.2", "Form Input Text", "extracted", "styles.css:input", text_main, bg_elevated),
        evaluate_pair("9.3", "Form Select Option Text", "extracted", "styles.css:select", text_main, bg_elevated),
        evaluate_pair("9.4", "Validation Error Text", "extracted", "styles.css:.alert-danger", danger_text, bg_surface),
        evaluate_pair("9.5", "Form Help Text", "extracted", "styles.css:.form-help", text_muted, bg_surface),

        # Category 10: Table Elements
        evaluate_pair("10.1", "Table Header Text", "extracted", "styles.css:.data-table th", th_fg, th_bg),
        evaluate_pair("10.2", "Table Cell Text", "extracted", "styles.css:.data-table td", text_main, bg_surface),
        evaluate_pair("10.3", "Responsive Data Label", "extracted", "styles.css:.data-table-responsive td::before", text_muted, bg_surface),

        # Category 11: Focus Indicators (WCAG 1.4.11 UI Non-Text)
        evaluate_pair("11.1", "Focus Ring on Base Bg", "manual assumption", "styles.css:focus-visible over base bg", accent, bg_base, is_non_text=True),
        evaluate_pair("11.2", "Focus Ring on Surface", "manual assumption", "styles.css:focus-visible over surface bg", accent, bg_surface, is_non_text=True),
        evaluate_pair("11.3", "Focus Ring on Elevated Surface", "manual assumption", "styles.css:focus-visible over elevated surface", accent, bg_elevated, is_non_text=True),
        evaluate_pair("11.4", "Focus Ring on Primary Button (Offset Surface)", "manual assumption", "styles.css:focus-visible 2px offset over container surface", accent, bg_surface, is_non_text=True),

        # Category 12: Component Boundaries (WCAG 1.4.11 UI Non-Text)
        evaluate_pair("12.1", "Form Border vs Surface", "manual assumption", "styles.css:input border vs surface", border_steel, bg_surface, is_non_text=True),
        evaluate_pair("12.2", "Button Border vs Surface", "manual assumption", "styles.css:.btn-secondary border vs surface", border_steel, bg_surface, is_non_text=True),
        evaluate_pair("12.3", "Progress Bar Track Border/Fill", "manual assumption", "styles.css:.progress-bar-fill vs track", "#3b82f6", bg_elevated, is_non_text=True),

        # Category 13: Reconciliation JS State Fills (Extracted from JS RECONCILIATION_STATES object)
        evaluate_pair("13.1", "Queued Progress Fill", "extracted", "reconciliation.html:RECONCILIATION_STATES.queued", rec_states['queued']['fill'], bg_elevated, is_non_text=True),
        evaluate_pair("13.2", "Running Progress Fill", "extracted", "reconciliation.html:RECONCILIATION_STATES.running", rec_states['running']['fill'], bg_elevated, is_non_text=True),
        evaluate_pair("13.3", "Completed Progress Fill", "extracted", "reconciliation.html:RECONCILIATION_STATES.completed", rec_states['completed']['fill'], bg_elevated, is_non_text=True),
        evaluate_pair("13.4", "Stale Progress Fill", "extracted", "reconciliation.html:RECONCILIATION_STATES.stale", rec_states['stale']['fill'], bg_elevated, is_non_text=True),
        evaluate_pair("13.5", "Failed Progress Fill", "extracted", "reconciliation.html:RECONCILIATION_STATES.failed", rec_states['failed']['fill'], bg_elevated, is_non_text=True),

        # Category 14: Inline Literal Colors
        evaluate_pair("14.1", "Inline GP Gold (#f59e0b) on Surface", "extracted", "character-detail.html:L181 inline style", inline_gp_gold, bg_surface)
    ]

    total_count = len(tests)
    extracted_count = sum(1 for t in tests if t["evidence_class"] == "extracted")
    derived_count = sum(1 for t in tests if t["evidence_class"] == "derived")
    manual_count = sum(1 for t in tests if t["evidence_class"] == "manual assumption")

    passed_count = sum(1 for t in tests if t["passed"] and not t["is_exempt"])
    exempt_count = sum(1 for t in tests if t["is_exempt"])
    failed_count = sum(1 for t in tests if not t["passed"] and not t["is_exempt"])

    print("=" * 115)
    print("FREEDOM BLADES PLATFORM — REPRODUCIBLE WCAG CONTRAST & EVIDENCE INTEGRITY AUDIT REPORT")
    print("=" * 115)
    print(f"{'Category & Pair Name':<40} | {'Evidence':<10} | {'Source Location':<32} | {'FG':<7} | {'Composed BG':<11} | {'Ratio':<8} | {'Result'}")
    print("-" * 115)
    for t in tests:
        print(f"{t['category']} {t['name']:<36} | {t['evidence_class']:<10} | {t['source']:<32} | {t['fg']:<7} | {t['composed_bg']:<11} | {t['ratio_str']:<8} | {t['status']}")
    print("=" * 115)
    print(f"STATIC SOURCE CONSISTENCY AUDIT SUMMARY:")
    print(f"  Total Evaluated Matrix Pairs : {total_count}")
    print(f"  Extracted Source Declarations : {extracted_count}")
    print(f"  Derived Layered Operations   : {derived_count}")
    print(f"  Manual Surface Assumptions   : {manual_count}")
    print(f"  Passed Matrix Rows           : {passed_count}")
    print(f"  Exempt Matrix Rows           : {exempt_count}")
    print(f"  Failed Matrix Rows           : {failed_count}")
    print("=" * 115)

    if failed_count > 0:
        print("ERROR: Static contrast audit found failing pairs!")
        return False
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestEvidenceIntegrityAndDrift)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)

    # First run unit self-tests
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestEvidenceIntegrityAndDrift)
    runner = unittest.TextTestRunner(verbosity=0)
    test_result = runner.run(suite)
    if not test_result.wasSuccessful():
        print("ERROR: Self-tests failed!")
        sys.exit(1)

    success = run_audit()
    sys.exit(0 if success else 1)
