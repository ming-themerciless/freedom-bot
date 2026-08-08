"""Serve the snapshot submission endpoint for a supervised rehearsal.

    FREEDOM_SNAPSHOT_ARTIFACT_ROOT=/srv/freedom/snapshots \
    FREEDOM_SNAPSHOT_PRINCIPALS='foundry-the-guild|foundry:snapshot:submit|<sha256>' \
    FREEDOM_SNAPSHOT_ALLOWED_ORIGINS='https://foundry1.example.org' \
    APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' \
      ./venv/bin/python -m tools.snapshot_api --port 8757

`FREEDOM_SNAPSHOT_ALLOWED_ORIGINS` is optional and empty by default. It is
needed only for a rehearsal driven from a **browser**; the documented `curl`
smoke test sends no `Origin` and is unaffected by it.

**This is not the production server.** It is `wsgiref.simple_server`, which is
single-threaded, has no request timeout of its own, and is documented by Python
as a reference implementation. It exists so that the maintainer-supervised
transport rehearsal in `docs/operations/foundry-snapshot-submission.md` can be
performed against a real endpoint without first standing up the Phase 3 web
process. Phase 3 runs the same WSGI application under the managed `freedom-web`
service.

Two properties are enforced here rather than left to the operator:

- **it binds to loopback only.** TLS termination and the public listener are
  Caddy's job on this host (ADR 0002), and a directly exposed development server
  would be an unauthenticated-by-accident path to an endpoint that accepts a
  64 MiB body;
- **it prints no secret.** The startup summary names the configured principal
  *ids*, the artifact root and the bound port. Not the credential, not the
  database URL, not a digest.

Expected failures print a short message and a distinct exit code. Nothing here
prints a connection string, a credential, an artifact byte or a traceback.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from collections.abc import Sequence
from wsgiref.simple_server import WSGIRequestHandler, make_server

from adapters.database.safety import UnsafeDatabaseTargetError
from adapters.http.composition import ConfigurationError, build_application
from adapters.http.credentials import CredentialError

logger = logging.getLogger(__name__)

EXIT_OK = 0
#: Configuration was refused. Nothing was served.
EXIT_MISCONFIGURED = 2
#: The requested bind address is not loopback.
EXIT_REFUSED_BIND = 3

LOOPBACK = ("127.0.0.1", "::1", "localhost")


class _QuietHandler(WSGIRequestHandler):
    """A request log that cannot carry a credential or an artifact.

    The default handler writes the full request line to stderr. The request line
    of a preview carries a checksum and a query string, and a future route's
    might carry more; `log_message` is overridden to a fixed line so the access
    log states that a request happened and its status, and nothing else.
    """

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        status = args[1] if len(args) > 1 else "-"
        sys.stderr.write(f"request handled status={status}\n")


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Loopback address to bind. Non-loopback addresses are refused.",
    )
    parser.add_argument("--port", type=int, default=8757, help="TCP port to bind.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_arguments(argv)

    if arguments.host not in LOOPBACK:
        print(
            f"Refusing to bind {arguments.host}: this rehearsal server binds "
            "loopback only. Terminate TLS and expose the endpoint through Caddy, "
            "as docs/operations/topology.md describes.",
            file=sys.stderr,
        )
        return EXIT_REFUSED_BIND

    try:
        composition = build_application(os.environ)
    except (ConfigurationError, CredentialError, ValueError, UnsafeDatabaseTargetError) as error:
        print(f"Configuration refused: {error}", file=sys.stderr)
        return EXIT_MISCONFIGURED

    principals = ", ".join(composition.principal_ids) or "(none configured)"
    origins = ", ".join(composition.allowed_origins) or (
        "(none — no browser origin may submit; a non-browser caller is unaffected)"
    )
    print(
        f"Snapshot submission endpoint on http://{arguments.host}:{arguments.port}\n"
        f"  artifact root: {composition.artifact_root}\n"
        f"  principals:    {principals}\n"
        f"  browser origins: {origins}\n"
        "  preview route: disabled (needs the Phase 3 authentication boundary)\n"
        "Rehearsal server only. Stop it with Ctrl-C.",
        # Flushed because stdout is block-buffered when redirected to a file,
        # and an operator who redirects the log would otherwise see nothing at
        # all until the process exits — including whether it started.
        flush=True,
    )
    try:
        with make_server(
            arguments.host,
            arguments.port,
            composition.application,
            handler_class=_QuietHandler,
        ) as server:
            server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        composition.dispose()
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
