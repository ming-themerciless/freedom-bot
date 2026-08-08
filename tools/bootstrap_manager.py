"""Operator entry point for the one-time supervised Manager bootstrap.

    python -m tools.bootstrap_manager --snapshot the-guild.json          # dry run
    python -m tools.bootstrap_manager --snapshot the-guild.json \
        --bootstrap --supervisor "Peter Duscha"                          # applies

**No real import is authorized during development.** This command and the
operations procedure in `docs/operations/foundry-snapshot-import.md` are the
deliverable; the maintainer-supervised rehearsal against the real snapshot is a
separate review-gate check.

The safety properties, and where each is actually enforced:

| Property | Enforced by |
|---|---|
| a named supervisor | `SupervisedBootstrap`, which refuses a blank name |
| an explicit bootstrap flag | this command: `--supervisor` alone does nothing |
| the approved, disposable database target | `adapters.database.config.DatabaseSettings`, before anything connects |
| an uninitialized dataset | a query inside the applying transaction |
| self-disabling afterwards | the `platform_initialization` singleton row |
| not an authorization bypass later | the same row; later imports need a Council member |

Expected operational failures print a short message and a distinct exit code.
They never print a connection string, a credential, raw SQL, snapshot content or
a traceback — an operator's terminal, shell history and CI log are not the right
place for any of those.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from adapters.database.config import DatabaseSettings
from adapters.database.safety import ConnectionPolicy, UnsafeDatabaseTargetError
from adapters.database.unit_of_work import SqlAlchemyUnitOfWork
from adapters.safe_logging import log_expected_failure
from application.authorization import SupervisedBootstrap
from application.bootstrap import BootstrapGate
from application.foundry.artifact import SnapshotRejected, read_artifact
from application.foundry.import_service import (
    ImportRefused,
    SnapshotImportService,
)
from application.foundry.reconciliation import ActorOutcome
from domain.foundry import OBSERVED_DEPLOYMENT, SupportedDeployment
from domain.foundry_profile import PROFILE

logger = logging.getLogger(__name__)

EXIT_OK = 0
#: The run reported blocking issues and wrote nothing.
EXIT_BLOCKED = 1
#: The database target, the artifact or the arguments were refused.
EXIT_MISCONFIGURED = 2
#: The database could not be reached or refused the work.
EXIT_DATABASE_UNAVAILABLE = 4
#: The Manager is already initialized; this path is closed for good.
EXIT_BOOTSTRAP_CLOSED = 6

DATABASE_UNAVAILABLE_MESSAGE = (
    "The database could not be reached or refused the bootstrap. Check that "
    "PostgreSQL is running and that DATABASE_URL names the intended database, "
    "then re-run. Nothing was written."
)


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--snapshot",
        required=True,
        help="Path to the Council-exported snapshot bundle.",
    )
    parser.add_argument(
        "--folder",
        help=(
            "Foundry folder id to import from. Required when the bundle exports "
            "more than one folder; the Manager never chooses for you."
        ),
    )
    parser.add_argument(
        "--bootstrap",
        action="store_true",
        help="Apply the bootstrap. Without it, the run is a rehearsal.",
    )
    parser.add_argument(
        "--supervisor",
        help="The person supervising this bootstrap. Required with --bootstrap.",
    )
    parser.add_argument(
        "--request-key",
        default=None,
        help="Idempotency key for this attempt. Defaults to the snapshot checksum.",
    )
    return parser.parse_args(argv)


def build_engine(environ=None):
    """Resolve and validate the database target before connecting to it."""
    environ = environ if environ is not None else os.environ
    settings = DatabaseSettings.from_mapping(
        environ,
        environment=environ.get("APP_ENVIRONMENT", "development"),
        environ=environ,
        policy=ConnectionPolicy.SOCKET_OR_LOOPBACK,
    )
    return create_engine(settings.url)


def build_services(engine, *, deployment: SupportedDeployment):
    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(engine)

    gate = BootstrapGate(factory, profile=PROFILE)
    imports = SnapshotImportService(
        factory,
        deployment=deployment,
        profile=PROFILE,
        # No authorization port: a supervised bootstrap has no interactive
        # Discord user to resolve, and every later import goes through the
        # Council-authorized path instead of this command.
        bootstrap_gate=gate,
    )
    return imports, gate


def render(preview, outcome=None) -> str:
    """What this run did, printed from the run's own record of it.

    A rehearsal and a fresh apply both have a full reconciliation report, so they
    print the per-issue detail. A **duplicate** does not: it reconciled nothing,
    and its result is the bounded facts the original import recorded (finding
    B-1R). Printing the preview's report beside "already applied" would show the
    operator a reconciliation of the database as it is now under a heading that
    claims to describe an import from some earlier moment — the same mixing of
    two instants the finding is about. So a duplicate prints the original's
    facts and its issue *codes*, and says which import they came from.
    """
    if outcome is not None and outcome.report is None:
        lines = _facts_lines(outcome.reconciliation)
    else:
        lines = _report_lines(outcome.report if outcome else preview.report)
    lines.append("")
    if outcome is not None and outcome.applied:
        lines.append(
            f"Applied. {outcome.created_count} character(s) created, "
            f"correlation {outcome.correlation_id}."
        )
    elif outcome is not None and outcome.duplicate:
        lines.append(
            "Already applied. This exact snapshot, folder and profile version "
            "had been imported; nothing changed. The counts above are the "
            f"original import's own record (import {outcome.import_id}, "
            f"correlation {outcome.correlation_id})."
        )
    else:
        lines.append(
            "Rehearsal. Nothing was written. Re-run with --bootstrap and "
            "--supervisor to apply."
        )
    return "\n".join(lines)


def _report_lines(report) -> list[str]:
    lines = [
        f"Snapshot:       {report.snapshot_checksum}",
        f"Exporter:       {report.exporter}",
        f"Folder:         {report.folder.describe()}",
        f"Field profile:  {report.profile_version}",
        "",
        f"  actors        {len(report.entries)}",
        f"  would create  {report.count(ActorOutcome.UNMAPPED)}",
        f"  already mapped{report.count(ActorOutcome.MAPPED):>3}",
        f"  blocked       {report.count(ActorOutcome.BLOCKED)}",
        f"  absent        {len(report.absent)}",
        "",
        f"{report.error_count} error(s), {report.warning_count} warning(s):",
    ]
    for issue in report.issues:
        marker = "ERROR " if issue.is_error else "warn  "
        lines.append(f"  {marker} [{issue.code}] {issue.message}")
    return lines


def _facts_lines(facts) -> list[str]:
    """The durable facts of an import that has already been applied.

    Codes rather than messages, because a message is written for one moment by
    the run that produced it and this is not that run. The codes are the closed
    vocabulary an operator filters on, and they were recorded at the time.
    """
    lines = [
        f"Snapshot:       {facts.snapshot_checksum}",
        f"Exporter:       {facts.exporter}",
        f"Folder:         {facts.folder_path} ({facts.folder_id})",
        f"Field profile:  {facts.profile_version}",
        "",
        f"  actors        {facts.actors}",
        f"  created       {facts.unmapped}",
        f"  already mapped{facts.mapped:>3}",
        f"  blocked       {facts.blocked}",
        f"  absent        {facts.absent}",
        "",
        f"{facts.errors} error(s), {facts.warnings} warning(s), as recorded:",
    ]
    lines.extend(f"         [{code}]" for code in facts.issue_codes)
    return lines


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_arguments(argv)

    if arguments.bootstrap and not (arguments.supervisor or "").strip():
        print(
            "--bootstrap requires --supervisor to name the person supervising "
            "this one-time initialization. Nothing was written.",
            file=sys.stderr,
        )
        return EXIT_MISCONFIGURED
    if arguments.supervisor and not arguments.bootstrap:
        print(
            "--supervisor names a supervisor but --bootstrap was not given, so "
            "this is a rehearsal. Nothing will be written.",
            file=sys.stderr,
        )

    try:
        artifact = read_artifact(Path(arguments.snapshot))
    except SnapshotRejected as refusal:
        # The refusal message names the limit and the offset, never the bytes.
        print(f"Snapshot refused [{refusal.code}]: {refusal}", file=sys.stderr)
        return EXIT_MISCONFIGURED

    try:
        engine = build_engine()
    except (ValueError, UnsafeDatabaseTargetError) as error:
        print(f"Database configuration refused: {error}", file=sys.stderr)
        return EXIT_MISCONFIGURED

    imports, gate = build_services(engine, deployment=OBSERVED_DEPLOYMENT)
    request_key = arguments.request_key or f"bootstrap:{artifact.checksum}"

    try:
        try:
            state = gate.state()
        except SQLAlchemyError as error:
            log_expected_failure(logger, "database_unavailable", error)
            print(DATABASE_UNAVAILABLE_MESSAGE, file=sys.stderr)
            return EXIT_DATABASE_UNAVAILABLE

        if arguments.bootstrap and not state.available:
            print(state.reason, file=sys.stderr)
            return EXIT_BOOTSTRAP_CLOSED

        try:
            preview = imports.preview(
                artifact, request_key=request_key, folder_id=arguments.folder
            )
        except SnapshotRejected as refusal:
            print(f"Snapshot refused [{refusal.code}]: {refusal}", file=sys.stderr)
            return EXIT_MISCONFIGURED
        except ImportRefused as refusal:
            print(f"Refused [{refusal.code}]: {refusal}", file=sys.stderr)
            return EXIT_BLOCKED

        if not arguments.bootstrap:
            print(render(preview))
            return EXIT_BLOCKED if preview.blocked else EXIT_OK

        try:
            outcome = imports.apply(
                artifact,
                preview,
                bootstrap=SupervisedBootstrap(arguments.supervisor.strip()),
                folder_id=preview.binding.folder_id,
            )
        except ImportRefused as refusal:
            print(f"Refused [{refusal.code}]: {refusal}", file=sys.stderr)
            return (
                EXIT_BOOTSTRAP_CLOSED
                if refusal.code.startswith("bootstrap")
                else EXIT_BLOCKED
            )
        except SQLAlchemyError as error:
            log_expected_failure(logger, "database_unavailable", error)
            print(DATABASE_UNAVAILABLE_MESSAGE, file=sys.stderr)
            return EXIT_DATABASE_UNAVAILABLE
    finally:
        engine.dispose()

    print(render(preview, outcome))
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
