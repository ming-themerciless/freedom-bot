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


# ---------------------------------------------------------------------------
# The generated systemd units — C1, 2026-08-25
# ---------------------------------------------------------------------------
#
# F5 was a worker unit that could never start, and the repair reached the
# template and the operations guide but not `infra/staging/setup-portal-host.sh`,
# which is the template's only executable consumer. A unit template and the
# installer that fills it in are one contract, and nothing checked that they
# still agreed: the corrected template asked for a placeholder the installer had
# never heard of, so the supported provisioning path would have written
# `EnvironmentFile=__WORKER_ENVIRONMENT_FILE__` into `/etc/systemd/system` and the
# manual repair on the staging host would have been unreproducible from here.
#
# These tests render each unit the way the installer renders it — from the
# installer's own substitution list and its own settings, not from a second copy
# of either — and check the result.

INSTALLER = ROOT / "infra" / "staging" / "setup-portal-host.sh"
PLACEHOLDER = re.compile(r"__[A-Z0-9_]+__")


def _installer_settings() -> dict[str, str]:
    """The `KEY="value"` assignments at the top of the installer, `${…}` resolved."""
    raw = dict(
        re.findall(r'^([A-Z][A-Z0-9_]*)="([^"]*)"', INSTALLER.read_text(), re.M)
    )
    resolved: dict[str, str] = {}

    def resolve(name: str, seen: frozenset[str] = frozenset()) -> str:
        if name in resolved:
            return resolved[name]
        assert name not in seen, f"{name} refers to itself"
        value = re.sub(
            r"\$\{([A-Z][A-Z0-9_]*)\}",
            lambda match: resolve(match.group(1), seen | {name}),
            raw[name],
        )
        resolved[name] = value
        return value

    for key in raw:
        resolve(key)
    return resolved


def _installer_substitutions() -> dict[str, str]:
    """Placeholder -> value, exactly as `install_unit()`'s `sed` fills them in."""
    settings = _installer_settings()
    pairs = re.findall(
        r'-e "s\|(__[A-Z0-9_]+__)\|\$\{([A-Z][A-Z0-9_]*)\}\|g"', INSTALLER.read_text()
    )
    assert pairs, "no substitutions found in the installer; these checks would pass vacuously"
    return {placeholder: settings[variable] for placeholder, variable in pairs}


def _installed_units() -> list[tuple[Path, str]]:
    """The templates the installer installs, and the unit names it installs them as."""
    # Trailing arguments are tolerated rather than required: the installer used to
    # pass a third one, and a collection error there would have hidden the
    # placeholder failure below behind a parsing failure of this test's own.
    calls = re.findall(
        r'^install_unit\s+"\$REPO_ROOT/(\S+?)"\s+(\S+?)(?:\s.*)?$',
        INSTALLER.read_text(),
        re.M,
    )
    assert calls, "no install_unit calls found; these checks would pass vacuously"
    return [(ROOT / template, target) for template, target in calls]


def _render(template: Path) -> str:
    text = template.read_text()
    for placeholder, value in _installer_substitutions().items():
        text = text.replace(placeholder, value)
    return text


def _directives(unit_text: str) -> list[str]:
    """Settings only. A `#` comment explaining a placeholder is documentation."""
    return [
        line
        for line in unit_text.splitlines()
        if line.strip() and not line.lstrip().startswith(("#", ";"))
    ]


@pytest.mark.parametrize("template,target", _installed_units(), ids=lambda value: str(value))
def test_the_installer_resolves_every_placeholder_in_the_units_it_installs(
    template: Path, target: str
):
    """C1. The exact defect: a template placeholder the installer never substitutes.

    Rendered from the installer's own `sed` list, so adding a placeholder to a
    template without teaching the installer about it fails here rather than on the
    host — where it arrives as a unit that parses, loads, and starts a process with
    a literal `__PLACEHOLDER__` for a file path.
    """
    unresolved = sorted(
        {match.group() for line in _directives(_render(template)) for match in PLACEHOLDER.finditer(line)}
    )
    assert not unresolved, (
        f"{target} would be installed carrying {', '.join(unresolved)}. "
        f"Add the substitution to install_unit() in {INSTALLER.relative_to(ROOT)}: "
        "the template and the installer are one contract."
    )


def test_the_generated_worker_unit_reads_the_worker_file_after_the_shared_one():
    """F5's mechanism, in the unit the supported installer actually produces.

    Order is the whole property. `systemd.exec(5)`: "If the same variable is set
    twice from these files, the files will be read in the order they are specified
    and the later setting will override the earlier setting." The shared portal
    file sets `WORKER_ENABLED=false` — S-11 requires that, because it is also
    `freedom-web`'s file — so the worker's own file must be read second or the
    worker refuses itself on every start.
    """
    settings = _installer_settings()
    worker = _render(ROOT / "infra" / "systemd" / "freedom-worker.service.tmpl")
    files = [
        line.split("=", 1)[1]
        for line in _directives(worker)
        if line.startswith("EnvironmentFile=")
    ]

    assert files == [settings["ENV_FILE"], settings["WORKER_ENV_FILE"]], (
        "the worker unit must read the shared portal file first and the worker's "
        f"own file second; it reads {files}"
    )
    assert all(path.startswith("/") for path in files), "both paths must be absolute"


def test_no_generated_unit_sets_worker_enabled_with_an_environment_line():
    """F5's cause, kept out of the units and out of the installer.

    `Environment=` loses to `EnvironmentFile=` unconditionally, so this spelling
    does not fail loudly — it produces a unit that reads as though it were
    configured correctly and a process that refuses itself with S-11. The
    installer used to append exactly this line to the worker unit.
    """
    for template, target in _installed_units():
        for line in _directives(_render(template)):
            assert not re.match(r"Environment=\s*WORKER_ENABLED=", line), (
                f"{target} sets WORKER_ENABLED with Environment=, which the shared "
                "EnvironmentFile overrides. Use a second EnvironmentFile listed after it."
            )
    # The templates are only half of it. The installer used to *append* the line
    # after rendering — `install_unit … "WORKER_ENABLED=true"` and a `printf` of a
    # second `[Service]` section — so a check that read only the templates would
    # have passed throughout the defect. It writes no `Environment=` line at all
    # now, and none of the three units needs one.
    for line in INSTALLER.read_text().splitlines():
        if line.lstrip().startswith("#"):
            continue
        assert "Environment=" not in line, (
            f"the installer writes an Environment= line into a unit: {line.strip()!r}. "
            "It loses to every EnvironmentFile the unit reads."
        )


def test_the_installer_provisions_the_worker_environment_file_it_substitutes():
    """A path substituted into a unit but never created is a unit that fails to start.

    `EnvironmentFile=` without a leading `-` is mandatory: systemd fails the unit
    if the file is absent. The installer must therefore write it, and must write
    the one line the file exists for.
    """
    installer = INSTALLER.read_text()
    assert re.search(r"printf 'WORKER_ENABLED=true\\n' > \"\$WORKER_ENV_FILE\"", installer), (
        "the installer must create the worker environment file with WORKER_ENABLED=true"
    )
    assert 'chmod 640 "$WORKER_ENV_FILE"' in installer, "the worker file needs a deliberate mode"
    assert 'chown root:"$SERVICE_GROUP" "$WORKER_ENV_FILE"' in installer, (
        "the worker file needs a deliberate owner"
    )
    # Idempotence: an existing file is confirmed, never silently rewritten — the
    # same promise this script makes about the shared environment file. The
    # existence test covers a symlink too (C3): `-f` alone follows the link and
    # would answer for its target, so a link would have fallen through to the
    # creation branch and been written *through*.
    assert 'if [ -e "$WORKER_ENV_FILE" ] || [ -L "$WORKER_ENV_FILE" ]; then' in installer, (
        "the installer must check for an existing worker environment file first, "
        "symlinks included"
    )
    # What that branch then does is C3's subject and is executed, not grepped, by
    # tests/test_worker_env_file.py.
    assert "worker_env_file_problem" in installer


# --------------------------------------------------------------------------
# N-22 (2026-08-27): the accepted operational contract §4.1 gives Caddy exactly
# two jobs — TLS and HSTS — and HSTS was configured in neither the deployed
# staging file nor the production template. Observed on the wire during the
# SP-29 browser evidence run: no `strict-transport-security` on any response.
#
# These cover **both** files by name. The parametrised CADDY_ARTIFACTS checks
# above glob `*.caddy` and `*.example`, so the production `.tmpl` is outside
# them — which is part of why this went unnoticed.
# --------------------------------------------------------------------------

CADDY_FILES_REQUIRING_HSTS = (
    ROOT / "infra" / "caddy" / "freedom-blades-portal.caddy.tmpl",
    ROOT / "infra" / "caddy" / "freedom-blades-test.caddy",
)

#: The contract's floor: "max-age at least one year".
HSTS_MINIMUM_MAX_AGE = 31536000


@pytest.mark.parametrize("path", CADDY_FILES_REQUIRING_HSTS, ids=lambda p: p.name)
def test_every_served_site_sets_hsts(path: Path) -> None:
    body = path.read_text(encoding="utf-8")

    match = re.search(
        r"""header\s+Strict-Transport-Security\s+"([^"]+)\"""", body
    )
    assert match, f"{path.name} sets no Strict-Transport-Security header (N-22)"

    value = match.group(1)
    age = re.search(r"max-age=(\d+)", value)
    assert age, f"{path.name}'s HSTS value carries no max-age: {value!r}"
    assert int(age.group(1)) >= HSTS_MINIMUM_MAX_AGE, (
        f"{path.name} sets max-age={age.group(1)}, below the contract's "
        f"one-year floor of {HSTS_MINIMUM_MAX_AGE}"
    )


@pytest.mark.parametrize("path", CADDY_FILES_REQUIRING_HSTS, ids=lambda p: p.name)
def test_hsts_does_not_claim_subdomains_or_preload(path: Path) -> None:
    """Both are reserved, and both are hard to walk back.

    **The reason stated here until 2026-08-27 was wrong, and is corrected
    without changing what the test asserts.** It claimed `includeSubDomains`
    "would cover the sibling Foundry hosts under the same registrable domain".
    It would not: the directive binds the sending host and names *beneath* it
    (RFC 6797 §6.1.2), so `foundry1.rpgworld.org` and its peers are siblings of
    the portal names, not subdomains of them, and are unaffected either way. No
    block serves the apex `rpgworld.org`, which is the only place the sibling
    reasoning could have applied.

    The reservation itself stands, on a reason that holds: no name exists
    beneath either portal host, so the directive buys nothing today while
    committing every future name under it to HTTPS-only for a year. `preload` is
    a submission to a browser-vendor list and is close to irreversible. Neither
    may appear without a decision by the Operations Owner.
    """
    body = path.read_text(encoding="utf-8")

    match = re.search(r"""header\s+Strict-Transport-Security\s+"([^"]+)\"""", body)
    assert match
    value = match.group(1).lower()

    assert "includesubdomains" not in value, (
        f"{path.name} claims includeSubDomains; the contract reserves that for "
        "the Operations Owner, and it commits every future name beneath this "
        "host to HTTPS-only for the whole max-age"
    )
    assert "preload" not in value, f"{path.name} claims preload without a decision"


def test_the_application_still_owns_every_other_security_header() -> None:
    """HSTS is the exception, not the start of a habit.

    The contract's "one authority per header" rule is what stops two
    `Content-Security-Policy` headers silently intersecting. If a later change
    adds CSP or the others at the proxy, this fails.
    """
    proxy_owned = {"strict-transport-security", "server"}
    for path in CADDY_FILES_REQUIRING_HSTS:
        for match in re.finditer(r"^\s*header\s+(-?)([A-Za-z-]+)", path.read_text(), re.M):
            name = match.group(2).lower()
            assert name in proxy_owned, (
                f"{path.name} sets {match.group(2)!r} at the proxy. The "
                "application owns every header but HSTS (contract §4.1)."
            )
