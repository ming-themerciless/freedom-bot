"""Tests for P3.4 Step 2 static asset foundation and remediation.

Verifies:
1. Closed static asset inventory (manifest, 1 CSS, 1 emblem, 1 vendor HTMX).
2. Agreement between inventory and rejection of undeclared 5th asset / directory.
3. Asset filename fingerprint grammar (<stem>.<12 hex>.<ext>) and exact SHA-256 match.
4. asset-integrity.sha256 manifest validity.
5. Exact HTMX provenance (project URL, distribution URL, version, full digest, filename).
6. Deterministic rejection / falsification of mutated provenance facts.
7. Guild emblem source provenance and visual freeze alignment.
8. CSS foundation scope: presence of permitted foundation primitives and absence of
   prohibited component selectors (shell, navigation, profile, dialog, buttons, badges,
   progress, diff, HTMX components, etc.).
9. Absence of WCAG, audit, or conformance claims in the stylesheet.
10. Absence of remote origins, @import, remote fonts, data:/javascript: URLs, source maps,
    or design-prototype references in production CSS/JS.
11. Non-modification of templates, backend python, routes, view models, or configuration.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = ROOT / "adapters" / "web" / "static"
MANIFEST_PATH = STATIC_DIR / "asset-integrity.sha256"
VISUAL_FREEZE_MANIFEST = ROOT / "docs" / "review" / "phase-3-visual-freeze-manifest.sha256"
FROZEN_EMBLEM_SOURCE = ROOT / "design-prototype" / "assets" / "freedom-blades-token.png"

# Required exact HTMX facts (F2)
HTMX_PROJECT_URL = "https://github.com/bigskysoftware/htmx"
HTMX_DIST_URL = "https://raw.githubusercontent.com/bigskysoftware/htmx/v2.0.10/dist/htmx.min.js"
HTMX_VERSION = "2.0.10"
HTMX_DIGEST = "71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de"
HTMX_FILENAME = "htmx-2.0.10.71ea67185bfa.min.js"

# Prohibited component selectors in Step 6 CSS (later-step work)
PROHIBITED_CSS_SELECTORS = [
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
]


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def test_static_corpus_equals_closed_step_2_inventory_exactly() -> None:
    """1. The static directory contains exactly the allowlisted Step 2 files and subdirectories."""
    assert STATIC_DIR.exists(), "Static directory must exist"
    assert not (STATIC_DIR / ".gitkeep").exists(), ".gitkeep must be removed once assets exist"

    found_files = sorted(
        str(p.relative_to(STATIC_DIR))
        for p in STATIC_DIR.rglob("*")
        if p.is_file()
    )

    # Expected: 1 manifest + 1 CSS + 1 image + 1 vendor JS + 1 application JS
    assert len(found_files) == 5, f"Unexpected files found in static corpus: {found_files}"
    assert "asset-integrity.sha256" in found_files

    css_files = [f for f in found_files if f.startswith("css/")]
    image_files = [f for f in found_files if f.startswith("images/")]
    vendor_files = [f for f in found_files if f.startswith("vendor/")]
    js_files = [f for f in found_files if f.startswith("js/")]

    assert len(css_files) == 1, f"Expected exactly one CSS file, got: {css_files}"
    assert len(image_files) == 1, f"Expected exactly one image file, got: {image_files}"
    assert len(vendor_files) == 1, f"Expected exactly one vendor JS file, got: {vendor_files}"
    assert len(js_files) == 1, f"Expected exactly one JS file, got: {js_files}"

    # Verify top-level entries
    top_entries = sorted(entry.name for entry in STATIC_DIR.iterdir())
    assert top_entries == ["asset-integrity.sha256", "css", "images", "js", "vendor"]


def test_every_asset_filename_has_required_fingerprint_grammar() -> None:
    """2. Every asset filename satisfies the 12-hex fingerprint grammar."""
    for p in STATIC_DIR.rglob("*"):
        if p.is_file() and p.name != "asset-integrity.sha256":
            stem_and_ext = p.name
            if stem_and_ext.endswith(".min.js"):
                base_part = stem_and_ext[:-7]
                parts = base_part.split(".")
                assert len(parts) >= 2, f"Invalid fingerprinted filename format: {stem_and_ext}"
                fingerprint = parts[-1]
                assert len(fingerprint) == 12 and all(c in "0123456789abcdef" for c in fingerprint), (
                    f"Invalid 12-hex fingerprint in {stem_and_ext}"
                )
            else:
                parts = stem_and_ext.split(".")
                assert len(parts) >= 3, f"Invalid fingerprinted filename format: {stem_and_ext}"
                fingerprint = parts[-2]
                assert len(fingerprint) == 12 and all(c in "0123456789abcdef" for c in fingerprint), (
                    f"Invalid 12-hex fingerprint in {stem_and_ext}"
                )


def test_every_filename_fingerprint_equals_first_12_hex_of_sha256() -> None:
    """3. Each asset's filename fingerprint matches the first 12 characters of its SHA-256."""
    for p in STATIC_DIR.rglob("*"):
        if p.is_file() and p.name != "asset-integrity.sha256":
            actual_sha = compute_sha256(p)
            expected_fingerprint = actual_sha[:12]
            if p.name.endswith(".min.js"):
                assert f".{expected_fingerprint}.min.js" in p.name, (
                    f"Fingerprint mismatch on {p.name}: expected {expected_fingerprint} from {actual_sha}"
                )
            else:
                assert f".{expected_fingerprint}." in p.name, (
                    f"Fingerprint mismatch on {p.name}: expected {expected_fingerprint} from {actual_sha}"
                )


def test_asset_integrity_manifest_verifies_successfully() -> None:
    """4. `sha256sum -c asset-integrity.sha256` passes cleanly."""
    assert MANIFEST_PATH.exists(), "Manifest file must exist"
    result = subprocess.run(
        ["sha256sum", "-c", str(MANIFEST_PATH.relative_to(ROOT))],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"sha256sum check failed:\n{result.stderr}\n{result.stdout}"
    assert "OK" in result.stdout

    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    assert "asset-integrity.sha256" not in manifest_text
    assert ".gitkeep" not in manifest_text


def parse_htmx_provenance_from_manifest(manifest_text: str) -> dict[str, str]:
    """Parse exact HTMX provenance fields from manifest header comments."""
    for line in manifest_text.splitlines():
        if line.startswith("# HTMX:"):
            # Expected format: # HTMX: project: <url>, distribution source: <url>, version: <ver>, upstream and local SHA-256: <hash>
            line_body = line[len("# HTMX:"):].strip()
            parts = [p.strip() for p in line_body.split(",") if p.strip()]
            data = {}
            for part in parts:
                if ":" in part:
                    k, v = part.split(":", 1)
                    data[k.strip()] = v.strip()
            return data
    return {}


def test_htmx_exact_provenance_and_version_match() -> None:
    """5. Vendored HTMX version, exact project URL, distribution source, filename, and digest match F2."""
    vendor_files = list((STATIC_DIR / "vendor").glob("htmx-*.js"))
    assert len(vendor_files) == 1, "Expected exactly one HTMX file in vendor/"
    htmx_file = vendor_files[0]

    assert htmx_file.name == HTMX_FILENAME, f"Expected filename {HTMX_FILENAME}, got {htmx_file.name}"

    digest = compute_sha256(htmx_file)
    assert digest == HTMX_DIGEST, f"Digest mismatch on HTMX: expected {HTMX_DIGEST}, got {digest}"

    content = htmx_file.read_text(encoding="utf-8", errors="ignore")
    assert f'version:"{HTMX_VERSION}"' in content or f'version: "{HTMX_VERSION}"' in content

    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    prov = parse_htmx_provenance_from_manifest(manifest_text)

    assert prov.get("project") == HTMX_PROJECT_URL, f"Project URL mismatch: {prov.get('project')}"
    assert prov.get("distribution source") == HTMX_DIST_URL, f"Distribution source mismatch: {prov.get('distribution source')}"
    assert prov.get("version") == HTMX_VERSION, f"Version mismatch: {prov.get('version')}"
    assert prov.get("upstream and local SHA-256") == HTMX_DIGEST, f"Digest mismatch in manifest: {prov.get('upstream and local SHA-256')}"
    assert "unpkg" not in manifest_text, "Prohibited unpkg CDN URL must not appear in manifest"


def validate_htmx_provenance_strict(manifest_text: str, vendor_file: Path) -> None:
    """Strict validator used to test deterministic rejection of mutated provenance."""
    prov = parse_htmx_provenance_from_manifest(manifest_text)
    if prov.get("project") != HTMX_PROJECT_URL:
        raise ValueError(f"Invalid project URL: {prov.get('project')}")
    if prov.get("distribution source") != HTMX_DIST_URL:
        raise ValueError(f"Invalid distribution source: {prov.get('distribution source')}")
    if prov.get("version") != HTMX_VERSION:
        raise ValueError(f"Invalid version: {prov.get('version')}")
    if prov.get("upstream and local SHA-256") != HTMX_DIGEST:
        raise ValueError(f"Invalid digest in manifest: {prov.get('upstream and local SHA-256')}")
    if vendor_file.name != HTMX_FILENAME:
        raise ValueError(f"Invalid filename: {vendor_file.name}")
    if compute_sha256(vendor_file) != HTMX_DIGEST:
        raise ValueError("Content hash mismatch")


def test_provenance_falsification_cases() -> None:
    """6. Mutations of each provenance fact are detected deterministically."""
    valid_text = MANIFEST_PATH.read_text(encoding="utf-8")
    valid_vendor = STATIC_DIR / "vendor" / HTMX_FILENAME

    # Baseline must pass
    validate_htmx_provenance_strict(valid_text, valid_vendor)

    # Mutation 1: wrong project URL (e.g. unpkg)
    bad_project = valid_text.replace(HTMX_PROJECT_URL, "https://unpkg.com/htmx.org")
    with pytest.raises(ValueError, match="Invalid project URL"):
        validate_htmx_provenance_strict(bad_project, valid_vendor)

    # Mutation 2: wrong distribution source URL
    bad_dist = valid_text.replace(HTMX_DIST_URL, "https://unpkg.com/htmx.org@2.0.10/dist/htmx.min.js")
    with pytest.raises(ValueError, match="Invalid distribution source"):
        validate_htmx_provenance_strict(bad_dist, valid_vendor)

    # Mutation 3: wrong version
    bad_ver = valid_text.replace(f"version: {HTMX_VERSION}", "version: 2.0.9")
    with pytest.raises(ValueError, match="Invalid version"):
        validate_htmx_provenance_strict(bad_ver, valid_vendor)

    # Mutation 4: wrong digest in manifest
    mutated_digest = HTMX_DIGEST[:-1] + ("0" if HTMX_DIGEST[-1] != "0" else "1")
    bad_digest = valid_text.replace(HTMX_DIGEST, mutated_digest)
    with pytest.raises(ValueError, match="Invalid digest in manifest"):
        validate_htmx_provenance_strict(bad_digest, valid_vendor)

    # Mutation 5: wrong vendor filename
    fake_path = STATIC_DIR / "vendor" / "htmx-2.0.10.wronghash123.min.js"
    with pytest.raises(ValueError, match="Invalid filename"):
        validate_htmx_provenance_strict(valid_text, fake_path)


def test_emblem_provenance_matches_frozen_source() -> None:
    """7. Guild emblem derivative matches frozen source in design-prototype."""
    image_files = list((STATIC_DIR / "images").glob("freedom-blades-token.*.png"))
    assert len(image_files) == 1, "Expected exactly one guild emblem image"
    emblem_file = image_files[0]

    source_sha = compute_sha256(FROZEN_EMBLEM_SOURCE)
    emblem_sha = compute_sha256(emblem_file)

    assert source_sha == emblem_sha, "Emblem derivative must match frozen source"

    freeze_text = VISUAL_FREEZE_MANIFEST.read_text()
    assert f"{source_sha}  design-prototype/assets/freedom-blades-token.png" in freeze_text or source_sha in freeze_text


def test_css_contains_only_permitted_foundation_and_no_prohibited_selectors() -> None:
    """8. CSS contains required foundation/shell primitives and NO Step 4/later component selectors."""
    css_files = list((STATIC_DIR / "css").glob("*.css"))
    assert len(css_files) == 1, f"Expected exactly one CSS file, got: {css_files}"
    css_text = css_files[0].read_text(encoding="utf-8")

    # Permitted foundation primitives
    assert ":root" in css_text
    assert "--fb-color-bg-base" in css_text
    assert "--fb-color-text-main" in css_text
    assert "--fb-color-primary" in css_text
    assert "-apple-system" in css_text
    assert ":focus-visible" in css_text
    assert "--fb-focus-ring" in css_text
    assert ".skip-link" in css_text
    assert ".sr-only" in css_text
    assert ".card" in css_text
    assert ".card-grid" in css_text
    assert ".alert" in css_text
    assert ".alert-info" in css_text
    assert ".table-container" in css_text
    assert "overflow-x: auto" in css_text
    assert ".fb-blade-divider" in css_text
    assert "prefers-reduced-motion" in css_text

    # Permitted Step 3 shell primitives
    assert ".app-header" in css_text
    assert ".app-header-top" in css_text
    assert ".brand-title" in css_text
    assert ".brand-emblem" in css_text
    assert ".app-navigation" in css_text
    assert ".nav-menu" in css_text
    assert ".nav-link" in css_text
    assert ".nav-link-login" in css_text
    assert ".main-container" in css_text
    assert ".app-footer" in css_text
    assert ".app-footer-inner" in css_text

    # Prohibited component selectors (Step 4+ / later work)
    for sel in PROHIBITED_CSS_SELECTORS:
        assert sel not in css_text, f"Prohibited component selector found in stylesheet: {sel}"


def test_css_makes_no_wcag_or_audit_claims() -> None:
    """9. CSS contains NO 'WCAG 2.2 AA Audited' or equivalent audit/conformance claim."""
    css_files = list((STATIC_DIR / "css").glob("*.css"))
    assert len(css_files) == 1
    css_text = css_files[0].read_text(encoding="utf-8")

    assert "WCAG" not in css_text, "Prohibited 'WCAG' claim found in stylesheet"
    assert "Audited" not in css_text, "Prohibited 'Audited' claim found in stylesheet"
    assert "audited" not in css_text, "Prohibited 'audited' claim found in stylesheet"
    assert "Conformance" not in css_text, "Prohibited 'Conformance' claim found in stylesheet"
    assert "conformance" not in css_text, "Prohibited 'conformance' claim found in stylesheet"


def test_css_and_js_contain_no_forbidden_patterns() -> None:
    """10. CSS and JS contain no remote URLs, @import, remote fonts, data:/javascript: URLs, or design-prototype references."""
    for p in STATIC_DIR.rglob("*"):
        if p.is_file() and p.suffix in (".css", ".js"):
            text = p.read_text(encoding="utf-8", errors="ignore")
            assert "@import" not in text, f"@import found in {p.name}"
            assert "http://" not in text, f"http:// found in {p.name}"
            assert "https://" not in text, f"https:// found in production asset {p.name}"
            assert "design-prototype" not in text, f"design-prototype reference found in {p.name}"
            assert "sourceMappingURL" not in text, f"source map reference found in {p.name}"

            if p.suffix == ".css":
                assert "data:" not in text, f"data: URL found in {p.name}"
                assert "javascript:" not in text, f"javascript: URL found in {p.name}"


#: Backend files P3.5 is permitted to change, each for a named accepted finding.
#: P3.4's rule was "the frontend package does not touch the backend", and it still
#: holds for frontend work. P3.5 is a backend package and changes backend files by
#: design, so the exception is enumerated here rather than left to erode the guard.
PERMITTED_P3_5_BACKEND = {
    # C35-05 / R35-17: the server-owned shell contract and its two wiring points.
    "application/web/shell.py",
    "adapters/web/app.py",
    "adapters/web/portal_routes.py",
    "adapters/web/import_routes.py",
    # C35-04 / F-13: an unreadable kill switch degrades health instead of breaking it.
    "application/web/startup.py",
    # C35-05: VM-23 registered in the view-model registry the guards read.
    "application/web/view_models.py",
    # --- 2026-08-24 supervised-session remediation. One entry per finding from
    # `docs/review/phase-3-p3-5-supervised-session-codex-review.md` and its
    # security companion, so the guard names why each file was opened rather
    # than growing a general backend exemption.
    #
    # S-5/S1: every counted emergency refusal writes one durable audit event.
    "application/web/refusals.py",
    "application/web/errors.py",
    "application/web/oauth.py",
    # S-6/S2: logout attribution derived from the persisted authentication method.
    "application/web/capabilities.py",
    "application/web/sessions.py",
    # S-7/S3: N-32's issuance and assertion budgets separated.
    "application/web/rate_limit.py",
    "application/web/config.py",
    # S-9/S4: a failed redemption is classified for the audit, not for the caller.
    "application/web/breakglass.py",
    "adapters/web/repositories.py",
    # S-4/S5: `identity_provider` is a bounded probe rather than a literal.
    "application/web/providers.py",
    "adapters/web/discord_provider.py",
}


def test_no_unrelated_production_files_modified() -> None:
    """11. No template or backend file changes outside the allowlists.

    **Parsing corrected 2026-08-23 (P3.5).** This previously did
    `line.strip()` before slicing `line[:2]` and `line[3:]`, and porcelain status
    codes are two columns wide: a *modified* file arrives as `" M path"`, so
    stripping the leading space shifted the slice and yielded `"pplication/..."`.
    The guard therefore never caught a modification to a tracked file — only
    untracked ones, whose `"?? "` prefix happens to survive the strip. It was
    asserting far less than it claimed for the whole of P3.4.
    """
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Deliberately not stripped: the first two columns are the status field, and
    # for a modified file the first of them is a space.
    lines = [line for line in result.stdout.splitlines() if line.strip()]

    permitted_templates = {
        "adapters/web/templates/base.html",
        "adapters/web/templates/includes/",
        "adapters/web/templates/includes/header.html",
        "adapters/web/templates/includes/footer.html",
        "adapters/web/templates/login.html",
        "adapters/web/templates/emergency.html",
        "adapters/web/templates/non_member.html",
        "adapters/web/templates/degraded.html",
        "adapters/web/templates/denied.html",
        "adapters/web/templates/conflict.html",
        "adapters/web/templates/validation.html",
        "adapters/web/templates/error.html",
        "adapters/web/templates/my_characters.html",
        "adapters/web/templates/character_detail.html",
    }

    for line in lines:
        path = line[3:].strip().strip('"')
        # A rename arrives as "old -> new"; the destination is what was written.
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path.startswith("adapters/web/templates/") and path not in permitted_templates:
            pytest.fail(f"Unpermitted template modification detected in working tree: {path}")
        if path.startswith("adapters/") and not (
            path.startswith("adapters/web/static/")
            or path.startswith("adapters/web/templates/")
            or path in PERMITTED_P3_5_BACKEND
        ):
            pytest.fail(f"Unpermitted adapters modification detected in working tree: {path}")
        if path.startswith("application/") and path not in PERMITTED_P3_5_BACKEND:
            pytest.fail(f"Unpermitted application modification detected in working tree: {path}")
