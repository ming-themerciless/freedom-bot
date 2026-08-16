"""C-06: engage or release the operator kill switch (N-56).

    python -m tools.portal_kill_switch on  --operator "…" --reason "…"
    python -m tools.portal_kill_switch off --operator "…" --reason "…"
    python -m tools.portal_kill_switch status

Layer 1 of the three-layer switch in the operational contract §4.3, and the only
one that is a file rather than a service action. **It leaves the Discord bot and
Foundry running**, which is the property that makes it usable during a portal
incident: the community keeps its bot while the web perimeter is closed.

Every route except `/healthz` answers `503` with a static maintenance body while
the file exists. Health stays up deliberately — it is on the loopback bind, is
not published by Caddy, and is what an operator watches while recovering.

The file's *presence* is the switch; its contents are a note for whoever finds
it. The web process `stat`s it at most once per second per process, so engaging
takes effect within a second and costs one syscall.
"""
from __future__ import annotations

import argparse
import os
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

EXIT_OK = 0
EXIT_REFUSED = 1
EXIT_USAGE = 4

VARIABLE = "WEB_KILL_SWITCH_FILE"


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("on", "off"):
        command = sub.add_parser(name)
        command.add_argument("--operator", required=True)
        command.add_argument("--reason", required=True)
    sub.add_parser("status")
    return parser.parse_args(argv)


def switch_path(environ=None) -> Path | None:
    values = environ if environ is not None else os.environ
    raw = (values.get(VARIABLE) or "").strip()
    if not raw:
        return None
    return Path(raw)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_arguments(argv)
    path = switch_path()
    if path is None:
        print(f"Refused: {VARIABLE} is not set, so there is no switch to operate.")
        return EXIT_USAGE
    if not path.is_absolute():
        print(f"Refused: {VARIABLE} must be an absolute path.")
        return EXIT_USAGE

    if arguments.command == "status":
        print("engaged" if path.exists() else "released")
        return EXIT_OK

    if arguments.command == "on":
        path.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).isoformat()
        # A note for whoever finds the file, not a record: the durable record is
        # the operator's own log. The switch is the file's existence.
        path.write_text(
            f"Freedom Blades portal kill switch engaged at {stamp}\n"
            f"operator: {arguments.operator}\n"
            f"reason: {arguments.reason}\n"
            "The Discord bot and Foundry are unaffected. Release with:\n"
            "  python -m tools.portal_kill_switch off --operator ... --reason ...\n"
        )
        print(f"Kill switch engaged: {path}")
        print("Every portal route except /healthz now answers 503 within one second.")
        print("The Discord bot and Foundry are unaffected.")
        return EXIT_OK

    if not path.exists():
        print("Kill switch was already released.")
        return EXIT_OK
    path.unlink()
    print(f"Kill switch released: {path}")
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover - entry point
    raise SystemExit(main())
