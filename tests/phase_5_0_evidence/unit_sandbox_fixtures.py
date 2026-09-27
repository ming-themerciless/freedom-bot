"""Fixtures for §2.13.2a S4-3: a deployed writer unit transcribed from §2.13.3,
and the applied property set a transient unit carrying it would show.

Values are written out here rather than derived from `unit_sandbox`, so a test
comparing them with the module is a comparison and not a restatement.
"""
from __future__ import annotations

from tools.phase_5_0_evidence.unit_sandbox import (
    DeployedUnit,
    SystemdIdentity,
    UnitFile,
    classify_sandbox_attestation,
)

#: §2.13.3's hardened unit, with the lifecycle lines any real unit carries.
DESIGN_UNIT_TEXT = """\
# freedom-sheet-writer.service — §2.13.3
[Unit]
Description=Freedom Blades Sheet writer
After=network-online.target

[Service]
Type=simple
ExecStart=/opt/freedom-blades/sheet-writer/bin/freedom-sheet-writer
User=freedomsheet
Group=freedomsheet
NoNewPrivileges=true
CapabilityBoundingSet=
AmbientCapabilities=
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
ProtectProc=invisible
RestrictSUIDSGID=true
ReadOnlyPaths=/var/lib/freedom-sheet-writer
ReadWritePaths=/var/lib/freedom-sheet-writer/journal
KillSignal=SIGTERM
TimeoutStopSec=45
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""

#: The arena of the approved target, written out.
PROBE = "/var/lib/fb-evidence-p5-0/probe"

APPLIED_LINES = {
    "User": "freedomsheet",
    "Group": "freedomsheet",
    "NoNewPrivileges": "yes",
    "CapabilityBoundingSet": "",
    "AmbientCapabilities": "",
    "ProtectSystem": "strict",
    "ProtectHome": "yes",
    "PrivateTmp": "yes",
    "ProtectProc": "invisible",
    "RestrictSUIDSGID": "yes",
    "ReadOnlyPaths": "/var/lib/freedom-sheet-writer",
    "ReadWritePaths": PROBE,
}

SYSTEMD = SystemdIdentity(
    systemd_version="259", package="systemd", package_version="259.1-1ubuntu1"
)


def unit(text: str = DESIGN_UNIT_TEXT, *drop_ins: UnitFile) -> DeployedUnit:
    return DeployedUnit(UnitFile("freedom-sheet-writer.service", text), tuple(drop_ins))


def applied_show(**overrides: str | None) -> str:
    """The `systemctl show` text; an override of `None` omits that property."""
    lines = dict(APPLIED_LINES)
    lines.update(overrides)
    return "\n".join(f"{k}={v}" for k, v in lines.items() if v is not None) + "\n"


def classify(
    deployed: DeployedUnit | None = None,
    *,
    recorded_unit_digest: str | None = None,
    recorded_substitution: str = PROBE,
    show: str | None = None,
    systemd: SystemdIdentity = SYSTEMD,
):
    deployed = deployed or unit()
    return classify_sandbox_attestation(
        deployed=deployed,
        recorded_unit_digest=(
            deployed.digest() if recorded_unit_digest is None else recorded_unit_digest
        ),
        recorded_substitution=recorded_substitution,
        applied_show=applied_show() if show is None else show,
        systemd=systemd,
    )
