"""Observe a startup refusal (S-01…S-11) without restarting the portal.

    sudo bash -c 'set -a; . /etc/freedom-blades/portal.env; set +a; \
      WEB_ALLOWED_HOSTS="*" \
      /opt/freedom-blades/runtime/venv-web/bin/python -m tools.startup_refusal_probe'

Written for **SP-08 / TC-OPS-04**, which requires every environment-separation
check to be *demonstrated failing on deliberately wrong configuration*.

## Why this exists rather than twelve service restarts

The obvious procedure is to edit one variable in the deployed environment file,
restart `freedom-web`, read the refusal, restore, and restart again — twelve
times. That works, and it costs twelve deliberate outages of the staging portal
with a single backup copy of the environment file standing between the sitting
and a portal that will not come back.

This probe calls `WebSettings.from_environment` — **the same function the
deployed process calls at startup**, under the same interpreter, against the same
environment file — with exactly one variable overridden by the caller. It opens
no socket, touches no service and leaves nothing behind.

**What that buys, and what it does not.** It is evidence at the *configuration*
layer: this build, this configuration, this refusal. It is **not** evidence that
systemd, the unit file and the supervisor behave correctly when a refusal
happens. That chain is proved once, by one real restart-to-failure, and the
procedure that uses this probe says so rather than implying the probe covers it.

## Why the output is safe to paste into an evidence document

`ConfigurationError` is value-free by construction — its own docstring is "Startup
refused. Carries every problem found, and no value" — and every problem names
variables only. This module prints that error and **nothing else**: it never
prints, iterates or summarises the environment it read. That matters because the
environment it read contains every secret the portal holds.

## S-12, S-13, S-14 and S-15 are not reachable here

They are not configuration checks. S-12 needs the artifact filesystem, S-14 a
database connection and S-15 a credential query — all in `run_resource_checks` —
and S-13 is a module-graph property enforced by a test. Each is observed where it
lives, and this probe deliberately does not pretend to cover them.
"""
from __future__ import annotations

import argparse
import os
import sys

from application.web.config import ConfigurationError, ProcessRole, WebSettings

EXIT_ACCEPTED = 0
EXIT_REFUSED = 1


def probe(environ: "os._Environ[str] | dict[str, str]", role: ProcessRole) -> tuple[int, str]:
    """Return `(exit_code, message)` for this environment. Never returns a value."""
    try:
        WebSettings.from_environment(environ, process=role)
    except ConfigurationError as error:
        return EXIT_REFUSED, str(error)
    return EXIT_ACCEPTED, (
        "NO REFUSAL - this configuration was accepted. If a refusal was expected, "
        "the override did not reach this process."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.startup_refusal_probe",
        description=(
            "Print the startup refusal for this process's environment. "
            "Opens no socket and changes nothing."
        ),
    )
    parser.add_argument(
        "--role",
        choices=("web", "worker"),
        default="web",
        help="Which process role to evaluate. S-11 refuses each in the other's direction.",
    )
    arguments = parser.parse_args(argv)
    role = ProcessRole.WORKER if arguments.role == "worker" else ProcessRole.WEB

    code, message = probe(os.environ, role)
    print(message)
    if code == EXIT_ACCEPTED:
        print(
            "(expected a refusal? check that the override was exported into this "
            "process, not into the parent shell)",
            file=sys.stderr,
        )
    return code


if __name__ == "__main__":  # pragma: no cover - operator entry point
    raise SystemExit(main())
