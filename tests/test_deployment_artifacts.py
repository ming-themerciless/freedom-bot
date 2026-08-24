"""Repository deployment artifacts carry no credential, and publish no health.

Added 2026-08-23 by the P3.5 C35 remediation. Both properties were violated by
artifacts this package authored, and neither was checkable by any existing test.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CADDY_DIR = ROOT / "infra" / "caddy"
CADDY_ARTIFACTS = sorted(CADDY_DIR.glob("*.caddy")) + sorted(CADDY_DIR.glob("*.example"))

#: Anything that would let a reader authenticate, or shorten a search that could.
#: A bcrypt verifier is the specific mistake C35-01 caught; the rest are the
#: neighbouring shapes, because the next credential to be pasted into a config
#: will not be a bcrypt hash.
CREDENTIAL_PATTERNS = {
    "bcrypt verifier": re.compile(r"\$2[aby]\$[0-9]{2}\$[./A-Za-z0-9]{20,}"),
    "argon2 verifier": re.compile(r"\$argon2[id]{1,2}\$"),
    "sha-crypt verifier": re.compile(r"\$[56]\$[./A-Za-z0-9]{8,}\$"),
    "private key block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "bearer token": re.compile(r"(?i)\bauthorization\s*:\s*bearer\s+\S+"),
}


def test_repository_caddy_artifacts_are_present_to_be_checked():
    """A vacuous pass is the failure mode this whole module is exposed to."""
    assert CADDY_ARTIFACTS, "no Caddy artifacts found; the checks below would pass vacuously"


@pytest.mark.parametrize("path", CADDY_ARTIFACTS, ids=lambda p: p.name)
def test_no_credential_material_in_repository_caddy_artifacts(path: Path):
    """C35-01. The verifier lives on the host, never here.

    The failure message names the artifact and the *class* of secret, and never
    the match itself: a test that printed the credential it found would put it in
    every CI log that ran it.
    """
    text = path.read_text()
    for description, pattern in CREDENTIAL_PATTERNS.items():
        assert not pattern.search(text), (
            f"{path.relative_to(ROOT)} contains a {description}. Credential material "
            "belongs in a host-local fragment outside the repository — see "
            "infra/staging/rotate-test-gate.sh. Rotate it: committing it spent it."
        )


def test_the_test_site_gate_is_imported_rather_than_inlined():
    """C35-01. The mechanism, not only the absence of today's mistake."""
    site = CADDY_DIR / "freedom-blades-test.caddy"
    text = site.read_text()
    assert "import /etc/caddy/freedom-blades-test.gate" in text, (
        "the site must import a host-local gate fragment, so that an absent gate "
        "fails the configuration closed rather than serving the site unprotected"
    )
    assert not re.search(r"^\tbasic_auth \{", text, re.M), (
        "the gate must not be inlined in the repository artifact"
    )


def test_health_is_refused_before_the_catch_all_proxy():
    """C35-02. `/healthz` is loopback-only and is never published.

    Order is the property, not mere presence: a refusal written after the
    catch-all `handle` would never be reached, and the site would proxy health to
    anyone who asked. Asserted on the file's own ordering; the adapted-JSON route
    indices are recorded in the remediation handoff.
    """
    text = (CADDY_DIR / "freedom-blades-test.caddy").read_text()

    health_matcher = text.find("@health path")
    health_handle = text.find("handle @health")
    proxy = text.find("reverse_proxy")
    first_other_handle = min(
        (position for position in (text.find("handle /enrol*"), text.find("handle {")) if position != -1),
        default=-1,
    )

    assert health_matcher != -1 and health_handle != -1, "no health refusal is defined"
    assert proxy != -1, "no proxy is defined; this test would pass vacuously"
    assert health_matcher < health_handle < proxy, "the health refusal must precede the proxy"
    assert first_other_handle != -1 and health_handle < first_other_handle, (
        "the health refusal must be the first handle block, or another block can "
        "claim the request first"
    )
    for form in ("/healthz", "/healthz/", "/healthz/*"):
        assert form in text, f"the matcher does not cover {form}"


CEREMONY = ROOT / "infra" / "ceremony" / "passkey-registration.html"


def test_the_registration_ceremony_requires_a_discoverable_credential():
    """C35-06. The empty allow-list at R-07 is a control, and this is its cost.

    R-07 answers with `allowCredentials: []` so that an unauthenticated caller
    learns nothing about which credentials exist. The consequence is that the
    browser has no hint at sign-in and can only offer a **discoverable**
    credential, so registration must demand one. `preferred` permits an
    authenticator to return a non-discoverable credential that registers cleanly
    and can then never be offered at login.
    """
    text = CEREMONY.read_text()
    assert "residentKey: 'required'" in text, "the ceremony must require a discoverable credential"
    assert "requireResidentKey: true" in text, "the legacy spelling must be sent too"
    assert "residentKey: 'preferred'" not in text
    assert "userVerification: 'required'" in text


def test_the_registration_ceremony_asks_for_no_account_identifier():
    """C35-06. Registration must not become the enumeration channel either."""
    text = CEREMONY.read_text()
    # Object keys, not the words: the page explains `allowCredentials` in a comment,
    # and a check that cannot tell an explanation from a call is a check that will
    # be silenced rather than satisfied the next time someone documents a control.
    for forbidden in ("allowCredentials:", "excludeCredentials:"):
        assert forbidden not in text, (
            f"the registration page must not send {forbidden}: it would reveal which "
            "credentials are already enrolled"
        )
    assert "/v1/auth/emergency/webauthn/" not in text, (
        "the registration page is host-local scaffolding and must reach no portal "
        "route: enrollment has no HTTP surface (TC-BG-10)"
    )
    assert "fetch(" not in text and "XMLHttpRequest" not in text, (
        "the registration page must transmit nothing"
    )
    assert "location.hostname" in text, "the relying party must be the page's own origin"
