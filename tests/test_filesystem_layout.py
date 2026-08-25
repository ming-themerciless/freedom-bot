"""The active deployment layout names the platform, not its original adapter."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ACTIVE_PATH_FILES = (
    ROOT / ".env.example",
    ROOT / "README.md",
    ROOT / "design-prototype" / "README.md",
    ROOT / "infra" / "caddy" / "freedom-blades-test.caddy",
    ROOT / "infra" / "staging" / "enable-test-site.sh",
    ROOT / "infra" / "staging" / "portal-run.sh",
    ROOT / "infra" / "staging" / "setup-portal-host.sh",
    ROOT / "infra" / "systemd" / "freedom-bot.service.tmpl",
    ROOT / "infra" / "systemd" / "freedom-web.service.tmpl",
    ROOT / "infra" / "systemd" / "freedom-worker.service.tmpl",
    ROOT / "docs" / "operations" / "break-glass-credential-custody.md",
    ROOT / "docs" / "operations" / "foundry-snapshot-import.md",
    ROOT / "docs" / "operations" / "foundry-snapshot-submission.md",
    ROOT / "docs" / "operations" / "portal-discord-setup.md",
    ROOT / "docs" / "operations" / "topology.md",
    ROOT / "docs" / "operations" / "web-portal.md",
)


def test_active_deployment_files_do_not_name_legacy_roots():
    legacy = ("/opt/discord-bots", "/srv/freedom/", "/etc/freedom-web")
    findings = []
    for path in ACTIVE_PATH_FILES:
        text = path.read_text()
        for value in legacy:
            if value in text:
                findings.append(f"{path.relative_to(ROOT)}: {value}")
    assert not findings, "active deployment paths still use the legacy layout:\n" + "\n".join(findings)


def test_canonical_layout_is_wired_into_active_deployment_files():
    combined = "\n".join(path.read_text() for path in ACTIVE_PATH_FILES)
    for required in (
        "/opt/freedom-blades/platform",
        "/opt/freedom-blades/runtime/venv-bot",
        "/opt/freedom-blades/runtime/venv-web",
        "/srv/freedom-blades/snapshots",
        "/srv/freedom-blades/web",
        "/etc/freedom-blades",
    ):
        assert required in combined, f"active deployment files do not carry {required}"
