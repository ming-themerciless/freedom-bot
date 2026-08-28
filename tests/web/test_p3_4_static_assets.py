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


#: Every top-level directory this guard **watches**, because production
#: behaviour, deployment behaviour or game rules live in it.
#:
#: **`tools/` added 2026-08-28 (N-30), and the list completed at the same time.**
#: The guard was extended one layer per finding — `domain/` for N-27, `tools/`
#: for N-30 — and each extension was made after a change had already passed
#: undeclared through the gap. Two instances of one class is enough: every
#: top-level directory in the repository is now either watched here or named in
#: `NON_PRODUCTION_DIRECTORIES` below, and
#: `test_the_scope_guard_watches_every_production_layer_in_the_repository`
#: fails on a directory that is in neither.
#:
#: **`infra/` and `foundry-module/` are a deliberate widening, not an absorption.**
#: Both carry accepted, reviewed P3.5 changes (HSTS in C-P3.5-Y, module 1.0.9 and
#: the version ranges in C-P3.5-X/Z, `MemoryMax=2G` in C-P3.5-Z), and both are
#: deployment surfaces where an undeclared edit reaches production directly. They
#: are declared file by file below rather than exempted by prefix, and the
#: widening is raised for the reviewer in change-log C-P3.5-AD rather than left
#: to be noticed.
WATCHED_PRODUCTION_PREFIXES = (
    "adapters/",
    "application/",
    "connectors/",
    "domain/",
    "ext/",
    "foundry-module/",
    "helpers/",
    "infra/",
    "migrations/",
    "models/",
    "tools/",
)

#: Production modules that sit at the repository root rather than in a layer.
WATCHED_PRODUCTION_FILES = frozenset({"main.py", "config.py"})

#: Top-level directories that are not production: documentation, the test suite
#: itself, the frozen §12.1 prototype, and build/interpreter artefacts. Named
#: explicitly so that "not watched" is a decision on the record rather than an
#: omission — which is precisely what N-27 and N-30 turned out to be.
NON_PRODUCTION_DIRECTORIES = frozenset(
    {"docs", "tests", "design-prototype", "__pycache__", "venv", "venv-web"}
)

#: Paths inside a watched prefix that this guard does not police, each because
#: another control owns it: P3.4's own asset inventory (the tests at the top of
#: this file), the template allowlist below, and the Foundry module's test suite,
#: which is test code living inside a production directory.
UNPOLICED_WITHIN_WATCHED = (
    "adapters/web/static/",
    "foundry-module/tests/",
)

#: Templates P3.4 and P3.5 are permitted to change.
PERMITTED_TEMPLATES = frozenset({
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
})

#: Production files P3.5 is permitted to change, each for a named accepted
#: finding. P3.4's rule was "the frontend package does not touch the backend",
#: and it still holds for frontend work. P3.5 is a backend package and changes
#: backend files by design, so the exception is enumerated here rather than left
#: to erode the guard.
#:
#: Renamed from `PERMITTED_P3_5_BACKEND` on 2026-08-28: it now covers deployment
#: artefacts and the Foundry module as well, and "backend" had stopped describing
#: it.
PERMITTED_P3_5_PRODUCTION = {
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
    # --- 2026-08-27. Deployment compatibility widened from exact equality to
    # scoped ranges (Foundry generation, game-system major.minor) after the
    # 14.365 -> 14.367 upgrade stopped submission. Authorized by the Acceptance
    # Authority; full account in change-log C-P3.5-Z. Declared here because the
    # same commit added `domain/` to this guard's watched prefixes (N-27).
    "domain/foundry.py",
    # --- 2026-08-27. N-45's soft warning, implemented after the measurement
    # showed the register had described a control that did not exist (F6's shape:
    # documented, never emitted). Authorized by the Acceptance Authority; full
    # account in change-log C-P3.5-Z.
    "application/worker/runtime.py",
    # --- 2026-08-27, EX-11 handoff task 2. **Documentation only, no runtime
    # behaviour**: the module docstring still stated `MemoryMax=1G` and described
    # peak memory as unmeasured, after C-P3.5-Z raised N-47 to 2G and TC-PERF-01
    # measured a real 32-Actor folder at 302 MiB. Declared rather than exempted,
    # because a docstring in `application/` is the layer this guard exists to
    # watch and "it is only a comment" is how the next real change gets in.
    "application/worker/__init__.py",
    # S-9/S4: a failed redemption is classified for the audit, not for the caller.
    "application/web/breakglass.py",
    "adapters/web/repositories.py",
    # S-4/S5: `identity_provider` is a bounded probe rather than a literal.
    "application/web/providers.py",
    "adapters/web/discord_provider.py",
    # --- 2026-08-28, `tools/` declared for the first time (N-30). Only the two
    # entry points genuinely changed by P3.5 are here. `tools/breakglass_
    # observation.py` and `tools/startup_refusal_probe.py` were assessed as the
    # handoff required and are **not** declared: both are committed at HEAD and
    # neither is modified in the working tree this guard reads, so declaring them
    # would assert a change that is not there.
    #
    # N-7 / N-13 / N-29 / N-31: the deployed portal entry point, and the file
    # carrying the access-log confidentiality control. This is the change that
    # passed undeclared and produced N-30. N-31 (2026-08-28) is a further edit to
    # the same file for the same control — the retained method is withheld when
    # it carries an address — and it is declared here rather than treated as
    # covered by the existing entry, because the declaration is per change.
    "tools/portal_server.py",
    # N-28: the harness that measures against N-47 now reads the ceiling from the
    # shipped worker unit instead of restating it as a literal.
    "tools/snapshot_perf_harness.py",
    # --- 2026-08-28, `infra/` and `foundry-module/` declared for the first time
    # (N-30 item 5). Each entry is an accepted, deployed P3.5 change; none is new
    # work, and the widening itself is raised in C-P3.5-AD.
    #
    # N-22 / C-P3.5-Y: HSTS added to both proxy configurations.
    "infra/caddy/freedom-blades-portal.caddy.tmpl",
    "infra/caddy/freedom-blades-test.caddy",
    # N-47 / C-P3.5-Z: `MemoryMax` raised to 2G, and the header comment that
    # `tools/snapshot_perf_harness.py` now parses the ceiling out of.
    "infra/systemd/freedom-worker.service.tmpl",
    # C-P3.5-X / C-P3.5-Z: module 1.0.9 and the OD-14 v1.6 version ranges.
    "foundry-module/module.json",
    "foundry-module/package.json",
    "foundry-module/scripts/bundle.js",
    "foundry-module/scripts/settings.js",
}


def status_paths(lines: list[str]) -> list[str]:
    """The paths in `git status --short` output, one per non-empty line.

    **Parsing corrected 2026-08-23 (P3.5).** This previously did `line.strip()`
    before slicing `line[:2]` and `line[3:]`, and porcelain status codes are two
    columns wide: a *modified* file arrives as `" M path"`, so stripping the
    leading space shifted the slice and yielded `"pplication/..."`. The guard
    therefore never caught a modification to a tracked file — only untracked
    ones, whose `"?? "` prefix happens to survive the strip. It was asserting far
    less than it claimed for the whole of P3.4.

    **Extracted from the test on 2026-08-28 (N-30)** so the forms git actually
    emits — modified, added, untracked, renamed, and a path containing a space,
    which git quotes — can be asserted against synthetic input instead of against
    whatever the working tree happens to contain when someone runs the suite.
    """
    paths: list[str] = []
    for line in lines:
        if not line.strip():
            continue
        # Deliberately not stripped first: the first two columns are the status
        # field, and for a modified file the first of them is a space.
        path = line[3:]
        # A rename arrives as "old -> new"; the destination is what was written.
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path.strip().strip('"'))
    return paths


def scope_violation(path: str) -> str | None:
    """Why `path` is an undeclared production change, or `None` if it is not.

    **A function of a path, and of nothing else (N-30).** The guard used to be a
    loop inside the test, so the only way to demonstrate it was to observe the
    current working tree passing — which shows that it ran, not that it can fail.
    Both N-27 and N-30 were cases where it ran and could not fail. A pure function
    can be handed a path that is not in the tree, which is what
    `test_the_scope_guard_rejects_an_undeclared_synthetic_path` does.
    """
    if path in PERMITTED_P3_5_PRODUCTION:
        return None
    if path.startswith("adapters/web/templates/"):
        if path in PERMITTED_TEMPLATES:
            return None
        return f"Unpermitted template modification detected in working tree: {path}"
    if any(path.startswith(prefix) for prefix in UNPOLICED_WITHIN_WATCHED):
        return None
    for prefix in WATCHED_PRODUCTION_PREFIXES:
        if path.startswith(prefix):
            layer = prefix.rstrip("/")
            return f"Unpermitted {layer} modification detected in working tree: {path}"
    if path in WATCHED_PRODUCTION_FILES:
        return f"Unpermitted root-module modification detected in working tree: {path}"
    return None


def test_no_unrelated_production_files_modified() -> None:
    """11. No production or template file in the working tree is undeclared.

    The decision is `scope_violation`'s; this test supplies the working tree and
    reports the first path it rejects. `domain/` was added 2026-08-27 (N-27),
    `tools/` and the remaining production layers 2026-08-28 (N-30).
    """
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    for path in status_paths(result.stdout.splitlines()):
        violation = scope_violation(path)
        if violation is not None:
            pytest.fail(violation)

# ---------------------------------------------------------------------------
# N-30 — the guard must watch `tools/`, and be provable without the working tree
#
# Codex EX-11/EX-12 re-review, 2026-08-28. The guard watched `adapters/`,
# `application/` and `domain/` and not `tools/`, so the N-29 behavioural change
# to `tools/portal_server.py` — the deployed portal entry point, and the file
# carrying the access-log confidentiality control — passed undeclared. That is
# N-27's failure class exactly: a guard that does not watch a layer cannot report
# that it is not watching it. It simply passes, which reads like the layer being
# clean.
#
# Two things follow, and the second is the one that lasts:
#
# 1. `tools/` is watched, and the P3.5 entry points genuinely changed in it are
#    declared with their reasons (`PERMITTED_P3_5_PRODUCTION`); and
# 2. the guard's decision is a **function of a path**, so an undeclared synthetic
#    path can be rejected on demand. Until now the only demonstration available
#    was "the current working tree happens to pass", which proves the guard ran,
#    not that it can fail.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    [
        "tools/portal_server.py",
        "tools/snapshot_perf_harness.py",
        "infra/systemd/freedom-worker.service.tmpl",
        "infra/caddy/freedom-blades-test.caddy",
        "foundry-module/scripts/bundle.js",
        "domain/foundry.py",
        "application/worker/runtime.py",
    ],
)
def test_a_declared_production_path_is_accepted(path: str) -> None:
    """The declared P3.5 changes pass, or the guard is merely noisy."""
    assert scope_violation(path) is None, path


@pytest.mark.parametrize(
    "path, layer",
    [
        ("tools/portal_server_undeclared.py", "tools"),
        ("tools/submission_admission.py", "tools"),
        ("tools/nested/deep/entry_point.py", "tools"),
        ("adapters/web/undeclared_routes.py", "adapters"),
        ("application/web/undeclared_service.py", "application"),
        ("domain/undeclared_rules.py", "domain"),
        ("connectors/sheets.py", "connectors"),
        ("ext/commands/undeclared_cog.py", "ext"),
        ("helpers/calculations.py", "helpers"),
        ("models/character.py", "models"),
        ("migrations/versions/0014_undeclared.py", "migrations"),
        ("infra/systemd/freedom-web.service.tmpl", "infra"),
        ("foundry-module/scripts/undeclared.js", "foundry-module"),
        ("main.py", "root"),
        ("config.py", "root"),
    ],
)
def test_the_scope_guard_rejects_an_undeclared_synthetic_path(path: str, layer: str) -> None:
    """N-30's falsification, and it does not need the working tree to run.

    Each path below is synthetic: none is modified in this tree, so this test
    fails the same way on a clean checkout as on a dirty one. That is the point.
    A guard demonstrated only by "everything currently passes" has been shown to
    run, not to be capable of failing — and N-27 and N-30 are both cases where it
    ran and could not fail.
    """
    violation = scope_violation(path)

    assert violation is not None, f"an undeclared {layer} path must be rejected: {path}"
    assert path in violation


def test_the_scope_guard_watches_every_production_layer_in_the_repository() -> None:
    """The gap N-27 and N-30 are two instances of, closed by enumeration.

    Rather than adding one layer per finding, every top-level directory in the
    repository is classified here as production or not. A new production layer
    therefore fails this test on the day it is created, instead of being found by
    the third reviewer to look for it.
    """
    top_level = {
        entry.name
        for entry in ROOT.iterdir()
        if entry.is_dir() and not entry.name.startswith(".")
    }
    classified = (
        set(prefix.rstrip("/") for prefix in WATCHED_PRODUCTION_PREFIXES)
        | NON_PRODUCTION_DIRECTORIES
    )

    unclassified = {name for name in top_level if name not in classified}
    assert not unclassified, (
        f"top-level directories neither watched nor declared non-production: "
        f"{sorted(unclassified)}"
    )


def test_a_non_production_path_is_not_policed_by_this_guard() -> None:
    """Documentation, tests and the frozen prototype are outside its scope."""
    for path in (
        "docs/project-management/change-log.md",
        "tests/web/test_p3_4_static_assets.py",
        "tests/fixtures/foundry_actor_sample.json",
        "design-prototype/assets/freedom-blades-token.png",
        "foundry-module/tests/projection.test.mjs",
        "README.md",
    ):
        assert scope_violation(path) is None, path


def test_the_static_and_template_layers_keep_their_own_rules() -> None:
    """P3.4's own surfaces are governed by the template allowlist, not by this."""
    assert scope_violation("adapters/web/static/css/portal.abc123456789.css") is None
    assert scope_violation("adapters/web/templates/base.html") is None
    assert scope_violation("adapters/web/templates/unpermitted.html") is not None


@pytest.mark.parametrize(
    "line, expected",
    [
        (" M tools/portal_server.py", "tools/portal_server.py"),
        ("?? tools/new_entry_point.py", "tools/new_entry_point.py"),
        ("M  domain/foundry.py", "domain/foundry.py"),
        ("A  application/web/added.py", "application/web/added.py"),
        ('R  "old name.py" -> "tools/renamed.py"', "tools/renamed.py"),
        ('?? "docs/review/Handover information"', "docs/review/Handover information"),
        (" M docs/project-management/status.md", "docs/project-management/status.md"),
    ],
)
def test_the_porcelain_parser_reads_each_status_form(line: str, expected: str) -> None:
    """The parsing defect P3.5 corrected, pinned against synthetic input.

    Until 2026-08-23 this guard stripped the line before slicing the two-column
    status field, so every *modified* tracked file was read as `"pplication/..."`
    and matched no prefix. It caught untracked files only. The forms below are
    the ones `git status --short` actually emits, asserted directly rather than
    through whatever the working tree happens to contain today.
    """
    assert status_paths([line]) == [expected]
