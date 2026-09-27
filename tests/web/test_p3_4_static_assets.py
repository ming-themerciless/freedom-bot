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


#: Production files **Phase 4** adds, declared for the same reason P3.5's are:
#: this guard watches `adapters/`, `application/` and `domain/`, Phase 4 is a
#: backend package that adds production code in all three by design, and the
#: guard's own rule is that an exception is enumerated rather than left to erode
#: it. Authority: the Phase 4 authorization recorded in change-log `C-P3.5-AK`,
#: with the package scope in `docs/review/phase-4-package-plan.md` §2.1.
#:
#: **The directory entry `adapters/ledger/` was withdrawn on 2026-09-08**
#: (finding PR-20260907-R2-3). It existed because `git status --short` collapses a
#: wholly untracked directory to one trailing-slash entry, so the modules inside
#: it never reached this guard — and an allowlist that accepts the collapsed
#: entry then approves every file the collapse hid, including files nobody
#: declared. The discovery below uses `--untracked-files=all`, which never
#: collapses, so no directory entry is needed and none is kept: the three modules
#: are declared individually, exactly as they are now that the directory is
#: tracked.
#:
#: **Four of these were undeclared from the WP-1 delivery on 2026-08-28 until
#: 2026-08-29**, and this guard was failing for them the whole time. Nobody saw
#: it because WP-0 and WP-1 ran the bot suite only, on the reasoning that a
#: package adding no web code cannot affect the web suite — which is exactly the
#: reasoning this guard exists to refute, since it reads the working tree rather
#: than the web application. Recorded in `docs/review/phase-4-submission.md`
#: rather than quietly fixed.
PERMITTED_PHASE_4_PRODUCTION = frozenset({
    # WP-1: framework-free money and resource value objects (OD-49, OD-50).
    "domain/quantities.py",
    "domain/money.py",
    "domain/resources.py",
    # WP-3: balanced, append-only ledger semantics.
    "domain/ledger.py",
    # WP-2: the command envelope, typed results and typed failures.
    "application/commands.py",
    # WP-3: the consumer-owned ledger boundary and its concrete Phase 4 service.
    "application/ledger.py",
    # WP-3: the in-memory reference ledger. OD-48 adds no table, so this is the
    # only ledger adapter in the repository.
    "adapters/ledger/__init__.py",
    "adapters/ledger/in_memory.py",
    # WP-3: the four Phase 4 ledger payload keys classified for the audit
    # projection, which the `test_every_payload_key_this_repository_writes_is_
    # classified` regression requires of any new `AuditEvent` payload. The
    # P4-R2 remediation adds a fifth, `service_principal_id`.
    "application/web/audit_search.py",
    # --- Remediation R1, 2026-08-29: the Codex findings P4-R1…P4-R3.
    #
    # Two further tracked production modules change, both narrowly and both
    # named in the remediation brief's "narrowly necessary accepted
    # authorization" allowance. Declared here for the same reason the four
    # above are: this guard's rule is that an exception is enumerated with its
    # reason, not left to erode the guard.
    #
    # `application/idempotency.py` gains `canonical_request_hash`, the typed,
    # length-delimited, schema-versioned encoding P4-R3 requires. The existing
    # `request_hash` is unchanged and keeps its one caller.
    "application/idempotency.py",
    # `application/service_principals.py` has its identifier rule extracted
    # into `validate_principal_id` so the Phase 4 ledger principal applies the
    # same rule rather than a copy of it. Behaviour-preserving: no scope is
    # added, and the accepted Foundry credential vocabulary is untouched.
    "application/service_principals.py",
})


#: The **Package 5.0 pre-implementation evidence harness**, authorized on
#: 2026-09-02 by the Operations Owner
#: (`docs/review/phase-5-0-evidence-harness-authorization-draft.md`) as evidence
#: scaffolding only.
#:
#: **A separate allowlist, deliberately.** It is not folded into
#: `PERMITTED_PHASE_4_PRODUCTION` because it is a different package under a
#: different authorization, and one list holding both would make revoking either
#: an edit to the other's entries. `WATCHED_PRODUCTION_PREFIXES` is unchanged:
#: `tools/` stays watched in full, and every other new `tools/` path is still
#: refused — `test_the_scope_guard_still_refuses_an_unrelated_tools_path` proves
#: that against synthetic paths that are not in this tree.
#:
#: **Every module is declared by name, and no directory entry is (finding
#: PR-20260907-R2-3, 2026-09-08).** The two collapsed entries this list used to
#: carry — `tools/phase_5_0_evidence/` and `tools/phase_5_0_evidence/execution/`
#: — were not a convenience. `git status --short` collapses a wholly untracked
#: directory to one trailing-slash entry, the allowlist accepted that entry, and
#: the guard therefore never inspected a single file inside the package. Six
#: modules of this submission were undeclared for exactly as long as the
#: directory stayed untracked, and the guard passed the whole time. The discovery
#: below now uses `--untracked-files=all`, which enumerates every file, and the
#: escape hatch is removed rather than left unused.
#:
#: **The six that were hidden**, reconciled against the submission that owns
#: them: each is a covered source in
#: `docs/review/phase-5-0-evidence-harness-review-manifest.json`, which pins its
#: SHA-256 and is the artifact Codex reviews, and each is described in the R13
#: implementation handback. They are inside the same bounded authorization as the
#: modules that were already declared — not new work, and not authorized by the
#: prompt that declares them. Their entries carry that reason below.
#:
#: The harness plans, classifies and serializes. Its planning tier executes
#: nothing: no module in it imports `subprocess`, a shell, a socket, an HTTP
#: client or a database driver, and
#: `tests/phase_5_0_evidence/test_no_execution.py` asserts that by reading the
#: source.
PERMITTED_PHASE_5_0_EVIDENCE_HARNESS = frozenset({
    "tools/phase_5_0_evidence/__init__.py",
    "tools/phase_5_0_evidence/errors.py",
    "tools/phase_5_0_evidence/records.py",
    "tools/phase_5_0_evidence/targets.py",
    "tools/phase_5_0_evidence/plan.py",
    "tools/phase_5_0_evidence/cleanup.py",
    "tools/phase_5_0_evidence/sudoers.py",
    "tools/phase_5_0_evidence/hba.py",
    "tools/phase_5_0_evidence/identity.py",
    "tools/phase_5_0_evidence/capability.py",
    "tools/phase_5_0_evidence/filesystem.py",
    "tools/phase_5_0_evidence/manifest.py",
    "tools/phase_5_0_evidence/provenance.py",
    "tools/phase_5_0_evidence/journal.py",
    # The concrete-plan stage, 2026-09-05. The canonical approved target, the
    # generator that turns the reviewed template into exact argument vectors,
    # the capture policies that bound what a run may record, and the review
    # manifest whose digest the executor requires.
    "tools/phase_5_0_evidence/approved_target.py",
    "tools/phase_5_0_evidence/capture.py",
    "tools/phase_5_0_evidence/concrete_plan.py",
    "tools/phase_5_0_evidence/review_manifest.py",
    # **R13, EH-R13-4.** The required-case table and the coverage check that
    # refuses a plan in which a required evidence case is neither produced by a
    # step nor declared unresolved. Pure data and one comparison.
    "tools/phase_5_0_evidence/required_cases.py",
    # --- The four planning-tier modules the collapsed directory entry hid until
    # 2026-09-08 (PR-20260907-R2-3). All four are covered sources in the review
    # manifest and were submitted with the revisions named beside them.
    #
    # R11 conflict C-5: the four disposable names, their declared substitution
    # sites, and the rule that nothing else in a reviewed vector may change.
    "tools/phase_5_0_evidence/binding.py",
    # R11 conflict C-2, Option B: the named-interpreter vector and the closed
    # grammar for what may follow it.
    "tools/phase_5_0_evidence/case_runtime.py",
    # R12/R13: the typed, closed semantic expectation contracts the executor
    # compares an observation against.
    "tools/phase_5_0_evidence/expectations.py",
    # R11 conflict C-4: the closed table of every byte sequence the harness may
    # put on disk. Planning tier, so it cannot write anything itself.
    "tools/phase_5_0_evidence/materialization.py",
    # The **execution tier**, added by the concrete-plan stage and declared
    # separately because it is the part that can start a process. It is submitted
    # for Codex's pre-execution review and has not been run:
    # `tests/phase_5_0_evidence/test_no_execution.py` enumerates both tiers,
    # holds every planning module to the no-process rule, and permits
    # `subprocess` in exactly one file — `execution/boundary.py`.
    "tools/phase_5_0_evidence/execution/__init__.py",
    "tools/phase_5_0_evidence/execution/boundary.py",
    "tools/phase_5_0_evidence/execution/cli.py",
    "tools/phase_5_0_evidence/execution/executor.py",
    # --- The two execution-tier modules the collapsed entry hid, same finding.
    #
    # C-2's payload: the single-file reviewed case program, copied byte for byte
    # to `<root>/bin/case`, so its source digest is its installation digest.
    "tools/phase_5_0_evidence/execution/case_program.py",
    # C-4's writing half: the one place the harness puts bytes on disk, and it
    # can only write what `materialization.py` already fixed.
    "tools/phase_5_0_evidence/execution/materializer.py",
    # **R13, EH-R13-5.** The run-record writer. It is in the execution tier
    # because it writes a file on the harness's behalf: the CLI used to report
    # `artifact written : True` and write nothing at all, and this is the
    # bounded, sanitized, read-back-and-validated path that claim now needs.
    "tools/phase_5_0_evidence/execution/artifact.py",
    # --- R16, conflict C-7, authorized 2026-09-09. The supplied-observation
    # ingestion stage, in two modules and deliberately not one.
    #
    # The **importer and classifier**, planning tier: a strict, versioned,
    # bounded schema with no free-text field, bound to the target, the run and
    # the review-manifest digest its caller supplies, and connected to the
    # `provenance` and `journal` classifiers. It imports nothing from the
    # execution tier at all.
    "tools/phase_5_0_evidence/observations.py",
    # The **ingestion entry point**, execution tier because it reads a payload
    # from a path and writes the classified artifact to one — and for no other
    # reason. It imports no `boundary`, no `executor` and no `materializer`, and
    # it does not import `cli`; `test_no_execution.py` asserts that against its
    # syntax tree, which is what stops a supplied observation reaching the
    # component that constructs the process boundary.
    "tools/phase_5_0_evidence/execution/evidence_cli.py",
    # --- C-P5.0-LAB-1, the reserved disposable laboratory, 2026-09-11. Two
    # planning-tier modules, both declared here because `tools/` is watched and
    # a new file under it is a declaration rather than a path that slips in.
    #
    # The bounded evidence-only producers for the three C-7 cases: deterministic
    # in-memory models with injected faults, their positive and negative
    # controls, and the feasibility-versus-product-evidence dispositions they
    # produce. It imports nothing from the product tree and nothing from the
    # execution tier, which `test_feasibility.py` asserts against its syntax
    # tree. It resolves no required case: all three stay declared unresolved.
    "tools/phase_5_0_evidence/feasibility.py",
    # The whole-host reservation state machine, the cooperative admission
    # decision and the release conditions. It decides and does not act: every
    # observation it reads arrives as an argument from a caller that made it, and
    # it takes no lock, starts no process and kills nothing.
    "tools/phase_5_0_evidence/reservation.py",
    # --- The September 11 re-review, PR-20260911-R2-2/-R2-3/-R2-4. Two further
    # planning-tier modules, declared here for the same reason: a new file under
    # a watched prefix is a declaration, not a path that slips in.
    #
    # **Neither is mechanism.** Both are bounded synthetic models of rules
    # proposed in runner contract revision 3, which is submitted and not built.
    #
    # The durability and removal model: a namespace and a data store with
    # separate volatile and durable halves, explicit descriptor modes, the
    # publication and restoration barrier graphs, and the name-based removal
    # whose post-check the re-review found overclaimed. Its whole "filesystem" is
    # a dictionary, so it opens nothing, synchronizes nothing and removes
    # nothing, which `test_no_execution.py` asserts against its syntax tree.
    "tools/phase_5_0_evidence/durability_model.py",
    # The lifecycle storage model: the seven participants under one allowlist of
    # validated lifecycle outcomes, shared with `reservation.validate_lifecycle`
    # rather than copied, and the proposed verified-first-use initialization
    # modelled over the filesystem above. **It provisions nothing.**
    "tools/phase_5_0_evidence/lifecycle_storage.py",
    # --- C-P5.0-LAB-I, the bounded repository implementation of runner contract
    # r6's reserved-laboratory mechanism, authorized 2026-09-13. Six files,
    # declared here for the same reason as every row above: a new file under a
    # watched prefix is a declaration, not a path that slips in.
    #
    # **They are mechanism, and they provision nothing.** Every path any of them
    # opens is one a caller hands it, so the production constants under `/run`
    # and `/var/lib` stay definitions and no object is created under either.
    # `tests/phase_5_0_evidence/test_lab_implementation.py` asserts that against
    # both the source and the filesystem.
    #
    # The r6 §1.3 descriptor custody chain: each directory held twice, the
    # synchronizable descriptor bound by comparison rather than assumed, and an
    # unregistered descriptor refused rather than dereferenced. Execution tier,
    # because it opens files and issues durability barriers on them.
    "tools/phase_5_0_evidence/execution/descriptors.py",
    # The r6 §5.3 cooperative lock adapter over the **pre-existing** provisioned
    # inode: open existing, `flock`, re-seal, read, parse, validate, survey,
    # refuse. It creates no lock, unlinks none, and breaks none.
    "tools/phase_5_0_evidence/execution/host_lock.py",
    # The reservation record on disk, and the run ledger on disk. Both are thin:
    # the rules they write under are `lifecycle_storage`'s, imported rather than
    # restated, so the mechanism and the model are one reader rather than two
    # that can drift.
    "tools/phase_5_0_evidence/execution/lifecycle_record.py",
    "tools/phase_5_0_evidence/execution/run_ledger.py",
    # The r6 §2.2 independent recovery store: captures published outside the
    # disposable root, across all five ordered barriers, with the recovery
    # parent's own entry barrier that revision 2 omitted.
    "tools/phase_5_0_evidence/execution/participants.py",
    "tools/phase_5_0_evidence/execution/recovery_store.py",
    # The r6 §7 provisioning **definitions**, planning tier and pure data. It
    # creates no group, writes no file, installs no fragment, changes no mode and
    # runs no command; all eleven items remain unapproved and unapplied.
    "tools/phase_5_0_evidence/provisioning.py",
    # --- C-P5.0-LAB-V6-R1, the V6 provisioning remediation, authorized
    # 2026-09-16. One new file, declared here for the same reason as every row
    # above.
    #
    # The applier for the r6 §7 **directory** items, execution tier. It is the
    # one module in this repository that creates a provisioned directory, and it
    # creates four: exclusive `mkdirat`, `fchown` and `fchmod` on the held
    # descriptor, then the parent's containing-entry barrier. It refuses V7 by
    # name, refuses an absent or non-exclusive parent rather than creating one,
    # verifies an existing object instead of repairing it, and takes every path
    # and every identity as an argument — so the suite drives it over a
    # temporary directory and **nothing here has been applied to any host**.
    "tools/phase_5_0_evidence/execution/provisioner.py",
    # --- C-P5.0-LAB-V6-P-R1, the provisioning entry point, authorized
    # 2026-09-18. One new file, declared here for the same reason as every row
    # above.
    #
    # The **operator entry point** for the applier directly above, and the only
    # route by which anything outside the test suite reaches it. Its absence is
    # what stopped the C-P5.0-LAB-V6-P operational pass before its first
    # mutation (RAID LAB-V6-P1). It arms that applier on one explicit
    # command-line flag and on nothing else, calls the production
    # `directory_targets()` with no arguments, renders the returned run through
    # a closed vocabulary, and applies nothing without the flag: no account
    # database and no filesystem is read on that path. It performs none of the
    # operator steps V1, V2 and V3, initializes no lifecycle record, offers no
    # rollback and cannot reach the executing runner — and **nothing here has
    # been applied to any host**.
    "tools/phase_5_0_evidence/execution/provisioning_cli.py",
    # --- C-P5.0-LAB-I3-R2, the I3 controlled-write verifier, authorized
    # 2026-09-19 under the C-P5.0-LAB-I3-D1 ruling. Two new files, declared here
    # for the same reason as every row above.
    #
    # The separately armed mechanism: one fixed harmless payload per reviewed
    # publication context — T1, r6 §2.3.3, T6 and P2 — created exclusively,
    # linked through the one reviewed `linkat` primitive, observed under both
    # names and removed through identity comparisons; and, solely for P2, the
    # transient canonical `R` and `R/bin` decision B's narrow exception permits.
    # Every path, account and `/proc` read reaches it through a seam, so the
    # suite drives it over a temporary directory and **nothing here has been run
    # on any host**.
    "tools/phase_5_0_evidence/execution/i3_verifier.py",
    # Its only operator entry point. It arms the verifier on one I3-specific
    # command-line flag and on nothing else, reads neither the account database
    # nor the filesystem without it, changes no identity or capability, and
    # renders only a closed vocabulary.
    "tools/phase_5_0_evidence/execution/i3_verifier_cli.py",
    # --- C-P5.0-R5-R1, classifier and Stage-4 prerequisites, assigned
    # 2026-09-23. One new file, declared here for the same reason as every row
    # above.
    #
    # §2.13.2a S4-3 as typed, fail-closed comparison: a closed directive and
    # drop-in allowlist, refusal of duplicate or unknown authority-bearing
    # directives, the substituted `ReadWritePaths=` fixed to the canonical probe
    # path, the complete normalized applied property set, and invalidation on a
    # systemd identity change. Planning tier: it reads no file, runs no
    # `systemctl` and inspects no unit — every input is supplied and untrusted.
    "tools/phase_5_0_evidence/unit_sandbox.py",
})


#: The **live Freedom bot crafting defect fix**, authorized on 2026-09-05
#: by maintainer direction under `.agents/AGENTS.md` product direction item 1
#: ("keep the live Freedom bot reliable").
#:
#: Resolves vocabulary mismatch between Sheet column X (artisan vocabulary, e.g.
#: "Expert Herbalist") and column Y / /craft dropdown (tool vocabulary, e.g.
#: "Herbalism Kit") by normalising aliases in `Skills._clean_tool_name()`.
#:
#: **A separate allowlist, deliberately.** It is not folded into any package
#: allowlist because it is an operational live-bot maintenance fix.
PERMITTED_LIVE_BOT_DEFECT_FIXES = frozenset({
    "models/skills.py",
})


#: Bounded repository maintenance fix to `infra/postgresql/backup-restore-drill.sh`
#: authorized under `phase-5-0-gemini-disposable-server-remediation-r2-prompt.md`
#: (DS-R2-1) to preserve standard PostgreSQL 16 schema ownership and ACL semantics.
PERMITTED_DISPOSABLE_SERVER_REMEDIATION = frozenset({
    "infra/postgresql/backup-restore-drill.sh",
})


class MalformedStatusRecord(ValueError):
    """A `git status` payload that does not parse as complete records.

    Raised rather than skipped: a record this parser cannot read is a change it
    cannot classify, and silently dropping it is the failure class this guard
    exists to refuse (N-27, N-30, PR-20260907-R2-3, PR-20260908-R3-3).
    """


#: The exact command the discovery runs. Named so the tests can assert that the
#: production path uses the machine-readable form and nothing else.
STATUS_COMMAND = (
    "git",
    "status",
    "--porcelain=v1",
    "-z",
    "--untracked-files=all",
)


def parse_status_records(payload: str) -> list[tuple[str, str, str | None]]:
    """`(status, path, origin)` for every record in a `git status -z` payload.

    **Machine-readable, because the human-readable form is ambiguous (finding
    PR-20260908-R3-3).** The previous parser read `git status --short`, split any
    path containing ` -> ` on that substring and kept the right-hand side, and
    stripped `"` characters from the ends. All three are guesses about a
    filename, and every one of them is wrong for a filename that is allowed to
    contain those characters:

    * an untracked `tools/extra -> outside.py` was read as `outside.py`, which
      matches no watched prefix, so a new file in a watched layer was invisible;
    * `--short` display-escapes a path with unusual bytes and wraps it in quotes,
      so the quotes were stripped from a *display* form rather than decoded, and
      a path genuinely containing a quote lost it; and
    * a rename's ` -> ` is only a separator when the status actually says `R`.

    `--porcelain=v1 -z` has none of that. Records are NUL delimited, paths are
    emitted verbatim with no quoting or escaping whatever bytes they contain, and
    a rename or copy is two records: the entry `XY <new>` followed by a bare
    `<old>`. That is the documented format, so the parser reads fields rather
    than hunting for punctuation.

    A truncated or otherwise unreadable payload raises `MalformedStatusRecord`.
    """
    records = payload.split("\0")
    if records and records[-1] == "":
        # A well-formed payload terminates its last record, so the split leaves
        # one trailing empty string. Anything else is a truncated read.
        records.pop()
    elif records:
        raise MalformedStatusRecord(
            "the status payload did not end with a record terminator"
        )

    entries: list[tuple[str, str, str | None]] = []
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        # `XY` then one space then a non-empty path: four characters at minimum.
        if len(record) < 4 or record[2] != " ":
            raise MalformedStatusRecord(f"not a status record: {record!r}")
        status, path = record[:2], record[3:]
        origin: str | None = None
        # A rename or a copy is scored in either column, and only those two
        # statuses carry a second record. Nothing is inferred from the path.
        if "R" in status or "C" in status:
            if index >= len(records):
                raise MalformedStatusRecord(
                    f"a rename or copy record carried no origin path: {record!r}"
                )
            origin = records[index]
            index += 1
            if not origin:
                raise MalformedStatusRecord(
                    f"a rename or copy record carried an empty origin path: {record!r}"
                )
        entries.append((status, path, origin))
    return entries


def record_paths(entries: list[tuple[str, str, str | None]]) -> list[str]:
    """Every path a set of status records puts in front of the guard.

    **A rename contributes both endpoints, a copy only its destination**, and the
    difference is the reason each is handled explicitly rather than by one rule
    (PR-20260908-R3-3 item 2):

    * a rename **removes** its origin. Moving `tools/portal_server.py` to
      `notes/portal_server.py` deletes a watched production source, and reading
      only the destination would classify that as an untouched `notes/` path —
      the removal would be concealed by the move.
    * a copy **leaves** its origin exactly as it was. Reporting it would assert a
      change to a file that did not change, which is the opposite error.
    """
    paths: list[str] = []
    for status, path, origin in entries:
        paths.append(path)
        if origin is not None and "R" in status:
            paths.append(origin)
    return paths


def working_tree_paths(root: Path) -> list[str]:
    """Every changed or untracked path in `root`, one per file.

    **`--untracked-files=all` is load-bearing (finding PR-20260907-R2-3).** The
    default `git status` collapses a wholly untracked directory to a single
    trailing-slash entry, so `?? tools/phase_5_0_evidence/` stood in for
    twenty-eight files and the guard inspected none of them. With the collapsed
    entry allowlisted, an undeclared module inside that directory was not merely
    unnoticed — it was structurally invisible, and adding one could never make
    this guard fail. Six such files were in the submitted tree.

    **`--porcelain=v1 -z` is load-bearing too (finding PR-20260908-R3-3).** The
    output is read as bytes and decoded with `surrogateescape`, so a path that is
    not valid UTF-8 round-trips instead of raising or being replaced. Nothing is
    split on whitespace, on a newline or on an arrow.

    Extracted as a function so the discovery itself can be exercised against a
    synthetic repository rather than only against whatever this working tree
    happens to contain.
    """
    result = subprocess.run(list(STATUS_COMMAND), cwd=root, capture_output=True)
    assert result.returncode == 0, result.stderr.decode("utf-8", "surrogateescape")
    payload = result.stdout.decode("utf-8", "surrogateescape")
    return record_paths(parse_status_records(payload))


def scope_violation(path: str) -> str | None:
    """Why `path` is an undeclared production change, or `None` if it is not.

    **A function of a path, and of nothing else (N-30).** The guard used to be a
    loop inside the test, so the only way to demonstrate it was to observe the
    current working tree passing — which shows that it ran, not that it can fail.
    Both N-27 and N-30 were cases where it ran and could not fail. A pure function
    can be handed a path that is not in the tree, which is what
    `test_the_scope_guard_rejects_an_undeclared_synthetic_path` does.
    """
    if path in PERMITTED_P3_5_PRODUCTION or path in PERMITTED_PHASE_4_PRODUCTION:
        return None
    if path in PERMITTED_PHASE_5_0_EVIDENCE_HARNESS:
        return None
    if path in PERMITTED_LIVE_BOT_DEFECT_FIXES:
        return None
    if path in PERMITTED_DISPOSABLE_SERVER_REMEDIATION:
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

    The decision is `scope_violation`'s and the discovery is
    `working_tree_paths`'; this test joins them and reports the first path
    rejected. `domain/` was added 2026-08-27 (N-27), `tools/` and the remaining
    production layers 2026-08-28 (N-30), and the discovery stopped depending on
    git collapsing an untracked directory 2026-09-08 (PR-20260907-R2-3).
    """
    for path in working_tree_paths(ROOT):
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
        # Package 5.0's evidence harness, file by file — the only form there is
        # since PR-20260907-R2-3 withdrew the collapsed-directory entries.
        "tools/phase_5_0_evidence/records.py",
        "tools/phase_5_0_evidence/capability.py",
        "tools/phase_5_0_evidence/binding.py",
        "tools/phase_5_0_evidence/execution/case_program.py",
        # Live Freedom bot crafting defect fix (artisan/tool alias resolution).
        "models/skills.py",
        # Disposable server remediation R2 schema preservation fix.
        "infra/postgresql/backup-restore-drill.sh",
    ],
)
def test_a_declared_production_path_is_accepted(path: str) -> None:
    """The declared P3.5 changes pass, or the guard is merely noisy."""
    assert scope_violation(path) is None, path


def test_the_live_bot_defect_fix_allowlist_is_narrow() -> None:
    """The live-bot defect fix allowlist is separate and strictly enumerated."""
    assert PERMITTED_LIVE_BOT_DEFECT_FIXES == frozenset({"models/skills.py"})
    assert not (PERMITTED_LIVE_BOT_DEFECT_FIXES & PERMITTED_PHASE_5_0_EVIDENCE_HARNESS)
    assert not (PERMITTED_LIVE_BOT_DEFECT_FIXES & PERMITTED_PHASE_4_PRODUCTION)
    assert not (PERMITTED_LIVE_BOT_DEFECT_FIXES & PERMITTED_P3_5_PRODUCTION)


def test_the_disposable_server_remediation_allowlist_is_narrow() -> None:
    """The disposable server remediation allowlist is separate and strictly enumerated."""
    assert PERMITTED_DISPOSABLE_SERVER_REMEDIATION == frozenset({"infra/postgresql/backup-restore-drill.sh"})
    assert not (PERMITTED_DISPOSABLE_SERVER_REMEDIATION & PERMITTED_PHASE_5_0_EVIDENCE_HARNESS)
    assert not (PERMITTED_DISPOSABLE_SERVER_REMEDIATION & PERMITTED_PHASE_4_PRODUCTION)
    assert not (PERMITTED_DISPOSABLE_SERVER_REMEDIATION & PERMITTED_P3_5_PRODUCTION)
    assert not (PERMITTED_DISPOSABLE_SERVER_REMEDIATION & PERMITTED_LIVE_BOT_DEFECT_FIXES)



@pytest.mark.parametrize(
    "path",
    [
        # The obvious neighbour: one character different from a declared file.
        "tools/phase_5_0_evidence_extra.py",
        # A sibling package that merely looks related.
        "tools/phase_5_1_evidence/records.py",
        # A module inside the declared package that is not declared.
        "tools/phase_5_0_evidence/executor.py",
        "tools/phase_5_0_evidence/subprocess_runner.py",
        # A nested directory under the declared package.
        "tools/phase_5_0_evidence/probes/setuid_helper.py",
        # Unrelated new tooling, which is what N-30 was about.
        "tools/migration_authority.py",
        "tools/journal_admin.py",
    ],
)
def test_the_scope_guard_still_refuses_an_unrelated_tools_path(path: str) -> None:
    """EH-R3's falsification: the evidence-harness allowlist is narrow.

    None of these paths exists in this tree, so the test fails the same way on a
    clean checkout as on a dirty one — the N-30 property. What it demonstrates is
    that declaring `tools/phase_5_0_evidence/` did **not** permit `tools/`, did
    not permit a prefix, and did not permit an undeclared module inside the
    declared package. An executing runner added to this harness would have to be
    declared here before the suite would go green, which is the whole point of the
    allowlist being a file list rather than a directory.
    """
    violation = scope_violation(path)

    assert violation is not None, f"an undeclared tools path must be rejected: {path}"
    assert path in violation


def test_the_evidence_harness_allowlist_is_separate_from_the_phase_4_one() -> None:
    """Two authorizations, two lists, and no overlap.

    Folding the harness into `PERMITTED_PHASE_4_PRODUCTION` would make revoking
    one package's authorization an edit to the other's entries. The prompt that
    authorized this work says so directly: do not fold it into the Phase 4
    allowlist.
    """
    assert not (PERMITTED_PHASE_5_0_EVIDENCE_HARNESS & PERMITTED_PHASE_4_PRODUCTION)
    assert not (PERMITTED_PHASE_5_0_EVIDENCE_HARNESS & PERMITTED_P3_5_PRODUCTION)
    assert all(
        path.startswith("tools/phase_5_0_evidence/")
        for path in PERMITTED_PHASE_5_0_EVIDENCE_HARNESS
    )


def test_the_evidence_harness_allowlist_does_not_weaken_the_watched_prefixes() -> None:
    """`tools/` is still watched in full, and no prefix was added to the unpoliced list."""
    assert "tools/" in WATCHED_PRODUCTION_PREFIXES
    assert not any(
        prefix.startswith("tools/") for prefix in UNPOLICED_WITHIN_WATCHED
    )


# ---------------------------------------------------------------------------
# PR-20260907-R2-3 (2026-09-08) — a collapsed untracked directory bypassed the
# guard entirely.
#
# `git status --short` collapses a *wholly untracked* directory to one
# trailing-slash entry. The production allowlists declared those entries, so the
# guard accepted `tools/phase_5_0_evidence/` and never looked at a single file
# inside it. Running the existing `status_paths` and `scope_violation` over both
# status forms showed the difference exactly:
#
#   git status --short                      -> no violation
#   git status --short --untracked-files=all -> six undeclared files
#
#     tools/phase_5_0_evidence/binding.py
#     tools/phase_5_0_evidence/case_runtime.py
#     tools/phase_5_0_evidence/execution/case_program.py
#     tools/phase_5_0_evidence/execution/materializer.py
#     tools/phase_5_0_evidence/expectations.py
#     tools/phase_5_0_evidence/materialization.py
#
# This is N-27's and N-30's failure class once more: a guard that cannot see a
# file cannot report that it is not seeing it — it simply passes, which reads
# like the file being declared. The discovery now enumerates files, and the
# collapsed-directory entries are removed rather than left unused, so the guard's
# result no longer depends on how git chose to summarise the tree.
# ---------------------------------------------------------------------------

#: Every allowlist whose entries name production files. A directory entry in any
#: of them would restore the escape hatch.
PRODUCTION_ALLOWLISTS = {
    "PERMITTED_P3_5_PRODUCTION": PERMITTED_P3_5_PRODUCTION,
    "PERMITTED_PHASE_4_PRODUCTION": PERMITTED_PHASE_4_PRODUCTION,
    "PERMITTED_PHASE_5_0_EVIDENCE_HARNESS": PERMITTED_PHASE_5_0_EVIDENCE_HARNESS,
    "PERMITTED_LIVE_BOT_DEFECT_FIXES": PERMITTED_LIVE_BOT_DEFECT_FIXES,
    "PERMITTED_DISPOSABLE_SERVER_REMEDIATION": PERMITTED_DISPOSABLE_SERVER_REMEDIATION,
}


def test_no_production_allowlist_entry_is_a_directory() -> None:
    """The escape hatch is removed, not merely unused.

    A single trailing-slash entry approves every file the collapse hides, and it
    keeps doing so if the discovery is ever changed back. Declaring files is what
    makes an undeclared sibling fail.
    """
    for name, allowlist in PRODUCTION_ALLOWLISTS.items():
        directories = sorted(entry for entry in allowlist if entry.endswith("/"))
        assert not directories, (name, directories)


def test_the_discovery_enumerates_untracked_files_rather_than_directories() -> None:
    """The discovery reads files, asserted against this repository's own tree.

    `tools/phase_5_0_evidence/` is untracked here, so the default status form
    collapses it. This test does not care which files are present — only that the
    directory itself is never what the guard is handed.
    """
    paths = working_tree_paths(ROOT)

    assert not any(path.endswith("/") for path in paths), (
        "the discovery handed the guard a directory: "
        f"{sorted(p for p in paths if p.endswith('/'))}"
    )
    # And the collapse really is what the default form does, so the switch is
    # not a no-op on this tree. Read through the same machine-readable parser, so
    # the comparison is between the two *untracked-file* settings and not between
    # two different parsers.
    default = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z"], cwd=ROOT, capture_output=True
    )
    assert default.returncode == 0
    collapsed = [
        path
        for path in record_paths(
            parse_status_records(default.stdout.decode("utf-8", "surrogateescape"))
        )
        if path.endswith("/")
    ]
    assert collapsed, "no untracked directory in this tree; this test proves nothing"


def test_every_evidence_harness_source_in_the_tree_is_declared() -> None:
    """The reconciliation, against the files that are actually here.

    The allowlist and the package must match exactly in both directions: a module
    present but undeclared is the finding, and a declared entry naming a module
    that does not exist is an allowlist asserting a change that is not there.
    """
    package = ROOT / "tools" / "phase_5_0_evidence"
    if not package.is_dir():
        pytest.skip("the evidence harness is not present in this tree")

    present = {
        str(path.relative_to(ROOT))
        for path in package.rglob("*.py")
        if "__pycache__" not in path.parts
    }

    assert present == set(PERMITTED_PHASE_5_0_EVIDENCE_HARNESS), {
        "undeclared": sorted(present - set(PERMITTED_PHASE_5_0_EVIDENCE_HARNESS)),
        "declared but absent": sorted(
            set(PERMITTED_PHASE_5_0_EVIDENCE_HARNESS) - present
        ),
    }


def _synthetic_repository(root: Path, files: dict[str, str]) -> None:
    """A temporary Git repository containing `files`, none of them committed.

    Deliberately a *separate* repository rather than a directory inside this one:
    the finding is about a wholly untracked directory, and writing one into this
    worktree would be writing undeclared production paths into the tree the guard
    reads.
    """
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def _commit_everything(root: Path) -> None:
    """Commit the synthetic repository, so tracked forms can exist.

    `git status` reports a modification, a deletion or a rename only against
    something it already tracks, so the end-to-end tests for those forms need a
    commit. Identity is supplied on the command line rather than written to a
    config file, and never from the developer's own global configuration.
    """
    identity = [
        "-c",
        "user.email=scope-guard@example.invalid",
        "-c",
        "user.name=Scope Guard Fixture",
    ]
    subprocess.run(
        ["git", *identity, "add", "--all"], cwd=root, check=True, capture_output=True
    )
    subprocess.run(
        ["git", *identity, "commit", "-q", "-m", "synthetic baseline"],
        cwd=root,
        check=True,
        capture_output=True,
    )


def test_the_discovery_finds_a_file_inside_an_untracked_directory(tmp_path) -> None:
    """**PR-20260907-R2-3 item 4.** Discovery *through* classification.

    The synthetic repository has a nested untracked directory holding one
    undeclared source file. The default status form collapses it to a directory
    the allowlist used to accept; the discovery this guard uses enumerates the
    file, and `scope_violation` then rejects it. Both halves are asserted,
    because the defect lived in the join between them: `scope_violation` would
    have rejected this path all along — it was never given it.
    """
    repository = tmp_path / "synthetic"
    undeclared = "tools/phase_5_0_evidence/probes/setuid_helper.py"
    _synthetic_repository(repository, {undeclared: "# synthetic\n"})

    collapsed = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z"], cwd=repository, capture_output=True
    )
    assert collapsed.returncode == 0
    # The shape of the defect: one directory entry, and the file is not in it.
    assert record_paths(
        parse_status_records(collapsed.stdout.decode("utf-8", "surrogateescape"))
    ) == ["tools/"]

    discovered = working_tree_paths(repository)
    assert undeclared in discovered, discovered

    violations = [
        violation
        for violation in (scope_violation(path) for path in discovered)
        if violation is not None
    ]
    assert len(violations) == 1, violations
    assert undeclared in violations[0]


def test_the_reviewed_file_set_passes_and_one_more_file_does_not(tmp_path) -> None:
    """**PR-20260907-R2-3 item 5.** The positive control, and its falsification.

    A synthetic repository is filled with the exact declared file set — all of it
    untracked, so git would collapse it — and the discovery must produce no
    violation. One extra module is then added inside the same package, and the
    same discovery must reject that one and only that one.

    A direct call to `scope_violation` would show neither: it would pass the
    declared names and reject the extra one whether or not git ever supplied
    them, which is exactly what made the six undeclared files invisible.
    """
    declared = sorted(PERMITTED_PHASE_5_0_EVIDENCE_HARNESS)
    repository = tmp_path / "reviewed"
    _synthetic_repository(repository, {name: "# reviewed\n" for name in declared})

    discovered = working_tree_paths(repository)
    assert set(discovered) == set(declared), sorted(set(discovered) ^ set(declared))
    assert [
        violation
        for violation in (scope_violation(path) for path in discovered)
        if violation is not None
    ] == []

    extra = "tools/phase_5_0_evidence/undeclared_module.py"
    (repository / extra).write_text("# not declared\n", encoding="utf-8")

    discovered = working_tree_paths(repository)
    assert extra in discovered
    violations = [
        violation
        for violation in (scope_violation(path) for path in discovered)
        if violation is not None
    ]
    assert len(violations) == 1, violations
    assert extra in violations[0]


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


# ---------------------------------------------------------------------------
# PR-20260908-R3-3 (2026-09-08) — human-readable status parsing hid a watched
# file.
#
# `status_paths()` treated every ` -> ` substring as a rename separator whatever
# the status said, and ` -> ` is a legal substring of an ordinary filename. Codex
# created a temporary synthetic Git repository holding the untracked file
# `tools/extra -> outside.py` and ran the guard's own functions over it:
#
#     working_tree_paths(repo) -> ['outside.py']
#     scope_violation('outside.py') -> None
#
# The control `tools/extra.py` in the same repository was correctly rejected as
# an unpermitted `tools/` modification, so the guard was working — it was being
# handed a filename that had been rewritten before it ever saw it. That is N-27's
# and N-30's failure class in a third shape: a guard cannot report a file it is
# not given.
#
# The parser now reads `git status --porcelain=v1 -z --untracked-files=all`,
# whose records are NUL delimited and whose paths are emitted verbatim, and it
# reads the documented rename/copy record form rather than looking for
# punctuation inside a name. A record it cannot parse raises rather than being
# dropped.
# ---------------------------------------------------------------------------


def _z(*records: str) -> str:
    """A `git status -z` payload: every record terminated by a NUL."""
    return "".join(f"{record}\0" for record in records)


@pytest.mark.parametrize(
    "record, expected",
    [
        (" M tools/portal_server.py", "tools/portal_server.py"),
        ("?? tools/new_entry_point.py", "tools/new_entry_point.py"),
        ("M  domain/foundry.py", "domain/foundry.py"),
        ("A  application/web/added.py", "application/web/added.py"),
        (" D models/character.py", "models/character.py"),
        ("D  application/web/removed.py", "application/web/removed.py"),
        ("?? docs/review/Handover information", "docs/review/Handover information"),
        (" M docs/project-management/status.md", "docs/project-management/status.md"),
        # The forms the human-readable parser could not read. `-z` emits every
        # one of them verbatim, so the path is the record and nothing else.
        ("?? tools/extra -> outside.py", "tools/extra -> outside.py"),
        ('?? tools/quoted".py', 'tools/quoted".py'),
        ("?? tools/back\\slash.py", "tools/back\\slash.py"),
        ("?? tools/tab\there.py", "tools/tab\there.py"),
        ("?? tools/new\nline.py", "tools/new\nline.py"),
        ("?? tools/nöñ-ascii.py", "tools/nöñ-ascii.py"),
        ("?? tools/ leading-space.py", "tools/ leading-space.py"),
    ],
)
def test_the_record_parser_reads_each_status_form(record: str, expected: str) -> None:
    """Every ordinary status form, asserted against synthetic records.

    The status field is two columns and then one space, so a *modified* file
    arrives as `" M path"` — the defect P3.5 corrected by not stripping the line
    first, and still the reason the path is sliced rather than tokenized. The
    last seven records are PR-20260908-R3-3's: a filename may contain an arrow, a
    quote, a backslash, a tab, a newline, non-ASCII bytes or a leading space, and
    none of them is a field separator in this format.
    """
    entries = parse_status_records(_z(record))

    assert entries == [(record[:2], expected, None)]
    assert record_paths(entries) == [expected]


@pytest.mark.parametrize(
    "status", ["R ", "RM", " R", "RD"], ids=["staged", "staged-modified", "worktree", "staged-deleted"]
)
def test_a_rename_record_reports_both_endpoints(status: str) -> None:
    """**PR-20260908-R3-3 item 2.** A rename removes its origin.

    Reading only the destination would classify moving a watched production
    source into an unwatched directory as a change to the unwatched directory,
    and the removal of the watched file would be concealed by the move. Both
    endpoints reach the guard, so the removal is classified on its own terms.
    """
    entries = parse_status_records(
        _z(f"{status} notes/portal_server.py", "tools/portal_server.py")
    )

    assert entries == [(status, "notes/portal_server.py", "tools/portal_server.py")]
    assert record_paths(entries) == [
        "notes/portal_server.py",
        "tools/portal_server.py",
    ]


@pytest.mark.parametrize("status", ["C ", "CM"], ids=["staged", "staged-modified"])
def test_a_copy_record_reports_only_its_destination(status: str) -> None:
    """The other half of item 2, and it is deliberately not symmetrical.

    A copy leaves its origin exactly as it was, so reporting the origin would
    assert a change to a file that did not change — the opposite error to the one
    the rename case avoids. What matters is that the origin record is *consumed*
    as the second half of one entry rather than read as a status record of its
    own, which is what the two-record format requires.

    Git only reports a copy when `status.renames=copies` is configured, so this
    is asserted against a fixture rather than against a repository whose
    detection would depend on configuration and on similarity scoring.
    """
    entries = parse_status_records(
        _z(f"{status} tools/portal_server_copy.py", "tools/portal_server.py")
    )

    assert entries == [
        (status, "tools/portal_server_copy.py", "tools/portal_server.py")
    ]
    assert record_paths(entries) == ["tools/portal_server_copy.py"]


def test_the_parser_reads_a_rename_beside_ordinary_records() -> None:
    """A payload is a sequence, and the two-record form must not desynchronize it.

    If the origin record were read as a status record, every entry after a rename
    would be misparsed — which is a silent, whole-payload failure rather than one
    wrong path.
    """
    entries = parse_status_records(
        _z(
            " M docs/project-management/status.md",
            "R  tools/renamed.py",
            "tools/original.py",
            "?? tools/untracked.py",
        )
    )

    assert record_paths(entries) == [
        "docs/project-management/status.md",
        "tools/renamed.py",
        "tools/original.py",
        "tools/untracked.py",
    ]


@pytest.mark.parametrize(
    "payload, reason",
    [
        # Truncated mid-payload: the last record has no terminator.
        ("?? tools/a.py\0?? tools/b.py", "record terminator"),
        (" M tools/a.py", "record terminator"),
        # A record too short to carry a status field and a path.
        (_z("??"), "not a status record"),
        (_z("?? "), "not a status record"),
        (_z("x"), "not a status record"),
        # The third column is not the documented space separator.
        (_z("??_tools/a.py"), "not a status record"),
        # A rename whose origin record never arrived.
        (_z("R  tools/renamed.py"), "carried no origin path"),
        (_z("C  tools/copied.py"), "carried no origin path"),
        # A rename whose origin record is empty.
        ("R  tools/renamed.py\0\0", "carried an empty origin path"),
    ],
)
def test_a_malformed_status_record_is_refused_rather_than_dropped(
    payload: str, reason: str
) -> None:
    """**PR-20260908-R3-3 item 2.** Unreadable is a failure, not an empty result.

    Skipping a record this parser cannot read is exactly the shape of the three
    findings this guard has had: a change that is not classified reads as a
    change that is permitted.
    """
    with pytest.raises(MalformedStatusRecord, match=reason):
        parse_status_records(payload)


def test_an_empty_payload_is_a_clean_tree_and_not_an_error() -> None:
    """The positive control for the terminator rule.

    `git status -z` prints nothing at all for a clean tree, and that must parse
    as no records rather than as a truncated payload.
    """
    assert parse_status_records("") == []
    assert record_paths([]) == []


def test_the_discovery_uses_the_machine_readable_form() -> None:
    """No human-readable parsing path remains in production-scope discovery.

    Asserted at the source as well as by behaviour: a regression would most
    likely reintroduce `--short` and a split on an arrow, and the tests above
    would keep passing against the parser while the discovery fed it display
    text.
    """
    assert STATUS_COMMAND == (
        "git",
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
    )
    source = Path(__file__).read_text(encoding="utf-8")
    code = "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith("#")
    )
    # The removed function and the two guesses it made about a filename. Each
    # needle is assembled rather than written out: a literal here would be a
    # substring of this test's own line, so the assertion would fail against
    # itself and prove nothing about the rest of the module.
    removed_parser = "def " + "status_paths("
    arrow_split = "split(" + '" -> "'
    quote_strip = "strip(" + "'\"'" + ")"
    assert removed_parser not in code
    assert arrow_split not in code
    assert quote_strip not in code


# --- Discovery through classification, in temporary synthetic Git repositories.
#
# Each of these builds a *separate* repository under `tmp_path`, runs the real
# `working_tree_paths` over it and then the real `scope_violation`, because the
# defect lived in the join between the two: `scope_violation` would have rejected
# `tools/extra -> outside.py` all along — it was never given it. No synthetic
# unauthorized file is written into this worktree.


#: Filenames that are legal, unusual, and each fatal to one guess the old parser
#: made. `\n` in particular is a record separator in the human-readable form.
HOSTILE_FILENAMES = [
    pytest.param("tools/extra -> outside.py", id="literal-arrow"),
    pytest.param("tools/extra -> outside -> again.py", id="two-arrows"),
    pytest.param("tools/with space.py", id="space"),
    pytest.param("tools/ leading-space.py", id="leading-space"),
    pytest.param("tools/trailing-space .py", id="trailing-space"),
    pytest.param('tools/quoted".py', id="double-quote"),
    pytest.param("tools/'single'.py", id="single-quote"),
    pytest.param("tools/back\\slash.py", id="backslash"),
    pytest.param("tools/tab\there.py", id="tab"),
    pytest.param("tools/new\nline.py", id="newline"),
    pytest.param("tools/nöñ-ascii.py", id="non-ascii"),
    pytest.param("tools/日本語.py", id="cjk"),
    pytest.param("tools/emoji-🗡.py", id="emoji"),
]


@pytest.mark.parametrize("name", HOSTILE_FILENAMES)
def test_an_undeclared_file_with_a_hostile_name_is_still_rejected(
    tmp_path, name: str
) -> None:
    """**PR-20260908-R3-3, the finding itself.** Discovery *through* classification.

    Every one of these is an undeclared file in a watched production layer. The
    guard must reject each by the name git actually holds — not by a name a
    display format or a split produced.
    """
    repository = tmp_path / "hostile"
    _synthetic_repository(repository, {name: "# synthetic\n"})

    discovered = working_tree_paths(repository)

    assert discovered == [name], discovered
    violation = scope_violation(discovered[0])
    assert violation is not None, name
    assert name in violation


def test_the_normal_control_beside_the_hostile_name_is_rejected_too(tmp_path) -> None:
    """Codex's reproduction exactly, both files at once.

    The control `tools/extra.py` was rejected before this correction and the
    hostile neighbour was not, which is what showed the classification was sound
    and the discovery was not. Both must now be rejected, and the count must be
    two — a parser that emitted one path for two files would satisfy a membership
    test.
    """
    repository = tmp_path / "codex"
    hostile = "tools/extra -> outside.py"
    control = "tools/extra.py"
    _synthetic_repository(
        repository, {hostile: "# synthetic\n", control: "# control\n"}
    )

    discovered = working_tree_paths(repository)

    assert sorted(discovered) == sorted([hostile, control]), discovered
    # The name the old parser produced is not among them.
    assert "outside.py" not in discovered
    violations = [
        violation
        for violation in (scope_violation(path) for path in discovered)
        if violation is not None
    ]
    assert len(violations) == 2, violations
    assert any(hostile in violation for violation in violations)
    assert any(control in violation for violation in violations)


def test_a_tracked_modification_and_a_tracked_deletion_are_discovered(
    tmp_path,
) -> None:
    """The ordinary forms, end to end rather than as fixtures.

    A committed tree is required for these to exist at all, so this is the one
    synthetic repository that commits: `git status` reports a modification or a
    deletion only against something it already tracks.
    """
    repository = tmp_path / "tracked"
    _synthetic_repository(
        repository,
        {
            "tools/portal_server.py": "# original\n",
            "domain/foundry.py": "# original\n",
            "docs/notes.md": "# original\n",
        },
    )
    _commit_everything(repository)

    (repository / "tools" / "portal_server.py").write_text("# edited\n", encoding="utf-8")
    (repository / "domain" / "foundry.py").unlink()
    (repository / "docs" / "notes.md").write_text("# edited\n", encoding="utf-8")

    discovered = working_tree_paths(repository)

    assert sorted(discovered) == [
        "docs/notes.md",
        "domain/foundry.py",
        "tools/portal_server.py",
    ], discovered
    # Both are declared P3.5 changes, so neither is a violation; the point is
    # that the discovery produced them at all. `docs/` is not watched.
    assert [
        violation
        for violation in (scope_violation(path) for path in discovered)
        if violation is not None
    ] == []


@pytest.mark.parametrize(
    "origin, destination, expected_violation",
    [
        # Out of a watched area: the destination is unwatched, so reading only
        # the destination would report nothing at all and the removal of an
        # undeclared watched file would be concealed by the move.
        pytest.param(
            "tools/undeclared_tool.py",
            "docs/undeclared_tool.py",
            "tools/undeclared_tool.py",
            id="out-of-watched",
        ),
        # The same move for a *declared* file. It is discovered at both
        # endpoints and is not a violation, which is what keeps the case above
        # attributable to the origin's declaration status rather than to the
        # rename being reported at all.
        pytest.param(
            "tools/portal_server.py",
            "docs/portal_server.py",
            None,
            id="declared-out-of-watched",
        ),
        # Into a watched area, from an unwatched one.
        pytest.param(
            "docs/helper.py",
            "tools/undeclared_helper.py",
            "tools/undeclared_helper.py",
            id="into-watched",
        ),
        # Within a watched area, from a declared file to an undeclared one.
        pytest.param(
            "tools/portal_server.py",
            "tools/renamed_portal_server.py",
            "tools/renamed_portal_server.py",
            id="within-watched",
        ),
    ],
)
def test_a_rename_is_classified_at_both_endpoints(
    tmp_path, origin: str, destination: str, expected_violation: str | None
) -> None:
    """**PR-20260908-R3-3 item 2**, through a real `R` status record.

    Git scores a rename only against the index, so the move is staged here — that
    is what makes git emit the two-record form this parser reads. `git mv` is used
    rather than a hand-built record, so the test exercises what git actually
    emits.

    The declared origin `tools/portal_server.py` is the interesting one: moving it
    out of `tools/` is a change to a declared production file, and the guard must
    still see the path it was declared under.
    """
    repository = tmp_path / "renamed"
    _synthetic_repository(repository, {origin: "# original\n" * 8})
    _commit_everything(repository)

    (repository / destination).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "mv", origin, destination],
        cwd=repository,
        check=True,
        capture_output=True,
    )

    entries = parse_status_records(
        subprocess.run(
            list(STATUS_COMMAND), cwd=repository, capture_output=True
        ).stdout.decode("utf-8", "surrogateescape")
    )
    assert len(entries) == 1, entries
    status, path, recorded_origin = entries[0]
    assert "R" in status, entries
    assert (path, recorded_origin) == (destination, origin)

    discovered = working_tree_paths(repository)
    assert sorted(discovered) == sorted([origin, destination]), discovered

    violations = [
        violation
        for violation in (scope_violation(path) for path in discovered)
        if violation is not None
    ]
    if expected_violation is None:
        assert violations == []
    else:
        assert len(violations) == 1, violations
        assert expected_violation in violations[0]


def test_a_nested_untracked_file_with_a_hostile_name_is_discovered(tmp_path) -> None:
    """Both corrections at once: the collapse and the name.

    `--untracked-files=all` is what produces the file rather than its parent
    directory, and `-z` is what produces its name rather than a display form. A
    regression in either one hides this file, and this is the shape a new probe
    inside the evidence harness would take.
    """
    repository = tmp_path / "nested"
    undeclared = "tools/phase_5_0_evidence/probes/setuid -> helper.py"
    _synthetic_repository(repository, {undeclared: "# synthetic\n"})

    assert working_tree_paths(repository) == [undeclared]
    violation = scope_violation(undeclared)
    assert violation is not None
    assert undeclared in violation
