"""Operator entry point for the Phase 2 character identity import.

    python -m tools.import_sheet_characters              # dry run, writes nothing
    python -m tools.import_sheet_characters --apply      # commits, if nothing is blocked

The Sheet is opened **read-only**: this tool reads one values range and never
calls `batch_update`. The database write is the only write, and it is
all-or-nothing — a run reporting any error commits nothing, including the rows
that were valid.

Expected operational failures — an unreachable Sheet, a refused credential, an
unavailable database, a concurrent import — are reported as a short message and
a distinct exit code. They never print a connection string, a credential, raw
SQL, a Google response body or a traceback, because an import is run by an
operator whose terminal, shell history and CI log are not the right place for
any of those. Nor are they logged: at every logging level, including DEBUG, the
only diagnostic recorded is a fixed failure category and the exception's class
name (see `adapters/safe_logging.py`). Debug logging is still logging, and a
traceback retained by journald or a CI job is the same disclosure as a printed
one.

See `docs/operations/sheet-import.md` for the procedure and the meaning of each
reported code.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from collections.abc import Sequence

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from adapters.database.config import DatabaseSettings
from adapters.database.safety import ConnectionPolicy, UnsafeDatabaseTargetError
from adapters.database.unit_of_work import SqlAlchemyUnitOfWork
from adapters.safe_logging import log_expected_failure
from adapters.sheets.character_import import (
    FIRST_DATA_ROW,
    SheetLayoutError,
    parse_character_rows,
    rows_from_values,
)
from adapters.sheets.read_only import (
    ReaderSelection,
    SheetCredentialError,
    build_values_reader,
)
from application.errors import ConcurrencyConflictError
from application.imports import (
    ImportIssueSeverity,
    SheetCharacterImportOutcome,
    SheetImportAction,
)
from application.sheet_import import SheetCharacterImportService

logger = logging.getLogger(__name__)

DEFAULT_TAB = "Characters"
DEFAULT_RANGE = "A1:AL150"

EXIT_OK = 0
#: The run reported errors and wrote nothing. A dry run that would fail exits
#: this way too, so a rehearsal can be scripted without parsing the report.
EXIT_BLOCKED = 1
#: The database target, credential or Sheet layout was refused before importing.
EXIT_MISCONFIGURED = 2
#: The Sheet could not be read: network, credential, quota or permission.
EXIT_SHEET_UNAVAILABLE = 3
#: The database could not be reached or refused the work.
EXIT_DATABASE_UNAVAILABLE = 4
#: Another writer changed the same rows, or a second import ran concurrently.
EXIT_CONFLICT = 5

#: Operator-facing text for each expected failure. Deliberately fixed strings:
#: the underlying exception may carry a DSN, a service-account address or a
#: Google error body, none of which belong in a terminal or a CI log.
SHEET_UNAVAILABLE_MESSAGE = (
    "The Sheet could not be read. Check network access, the service account's "
    "permission on the spreadsheet, and the configured spreadsheet id, then "
    "re-run. Nothing was written."
)
DATABASE_UNAVAILABLE_MESSAGE = (
    "The database could not be reached or refused the import. Check that "
    "PostgreSQL is running and that DATABASE_URL names the intended database, "
    "then re-run. Nothing was written."
)
CONFLICT_MESSAGE = (
    "The import conflicted with another change: a second import, or an edit "
    "made while this run was in progress. Nothing was written; re-run once the "
    "other change has finished."
)


class ImportCommandError(RuntimeError):
    """An expected operational failure, already translated for the operator."""

    def __init__(self, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tab", default=DEFAULT_TAB, help="Sheet tab and mapping key.")
    parser.add_argument(
        "--range",
        dest="cell_range",
        default=DEFAULT_RANGE,
        help="A1 range within the tab, starting at the header row.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit the import. Without it, the run is a rehearsal and is rolled back.",
    )
    return parser.parse_args(argv)


def build_engine():
    """Resolve and validate the database target before connecting to it.

    The importer creates and updates rows but changes no schema, so a loopback
    target is permitted here where a migration would refuse one.
    """
    settings = DatabaseSettings.from_mapping(
        os.environ,
        environment=os.environ.get("APP_ENVIRONMENT", "development"),
        environ=os.environ,
        policy=ConnectionPolicy.SOCKET_OR_LOOPBACK,
    )
    return create_engine(settings.url)


def sheet_failure_types() -> tuple[type[BaseException], ...]:
    """Exception types that mean "the Sheet could not be read".

    Resolved at call time and tolerant of a missing Google library, so that
    `--help`, a configuration error and the test suite never require the
    dependency to be installed.
    """
    types: list[type[BaseException]] = [OSError, TimeoutError]
    try:  # pragma: no cover - depends on the installed Google libraries
        from googleapiclient.errors import Error as GoogleApiError

        types.append(GoogleApiError)
    except ImportError:  # pragma: no cover
        pass
    try:  # pragma: no cover
        from google.auth.exceptions import GoogleAuthError

        types.append(GoogleAuthError)
    except ImportError:  # pragma: no cover
        pass
    return tuple(types)


def read_sheet_rows(
    selection: ReaderSelection, *, tab: str, cell_range: str
) -> list[dict[str, str]]:
    """Read and shape the tab, translating expected read failures."""
    try:
        values = selection.read_values(f"{tab}!{cell_range}")
    except sheet_failure_types() as error:
        log_expected_failure(logger, "sheet_read_failed", error)
        raise ImportCommandError(
            SHEET_UNAVAILABLE_MESSAGE, EXIT_SHEET_UNAVAILABLE
        ) from error
    # A layout refusal is this repository's own message and names only columns.
    return rows_from_values(values, first_data_row=FIRST_DATA_ROW)


def execute_import(
    engine, rows: list[dict[str, str]], *, tab: str, apply: bool
) -> SheetCharacterImportOutcome:
    """Run the import, translating expected database and concurrency failures.

    Rollback is not conditional on this translation: the unit of work rolls back
    and closes its session on any exception leaving its block, so an error here
    is always a run that wrote nothing.
    """
    service = SheetCharacterImportService(lambda: SqlAlchemyUnitOfWork(engine))
    try:
        return service.run(
            parse_character_rows(rows, first_row_number=FIRST_DATA_ROW),
            sheet_tab=tab,
            dry_run=not apply,
        )
    except (ConcurrencyConflictError, IntegrityError) as error:
        log_expected_failure(logger, "import_conflict", error)
        raise ImportCommandError(CONFLICT_MESSAGE, EXIT_CONFLICT) from error
    except SQLAlchemyError as error:
        log_expected_failure(logger, "database_unavailable", error)
        raise ImportCommandError(
            DATABASE_UNAVAILABLE_MESSAGE, EXIT_DATABASE_UNAVAILABLE
        ) from error


def render(outcome: SheetCharacterImportOutcome) -> str:
    lines = [
        f"Sheet tab:      {outcome.sheet_tab}",
        f"Correlation id: {outcome.correlation_id}",
        f"Mode:           {'dry run' if outcome.dry_run else 'apply'}",
        "",
        "  created   {created}\n  updated   {updated}\n  unchanged {unchanged}\n  blocked   {blocked}".format(
            created=outcome.count(SheetImportAction.CREATED),
            updated=outcome.count(SheetImportAction.UPDATED),
            unchanged=outcome.count(SheetImportAction.UNCHANGED),
            blocked=outcome.count(SheetImportAction.BLOCKED),
        ),
    ]
    if outcome.issues:
        lines.append("")
        lines.append(f"{outcome.error_count} error(s), {outcome.warning_count} warning(s):")
        for issue in sorted(outcome.issues, key=lambda i: (i.row_number, i.field)):
            marker = "ERROR " if issue.severity is ImportIssueSeverity.ERROR else "warn  "
            lines.append(f"  {marker} row {issue.row_number} [{issue.code}] {issue.message}")
    lines.append("")
    if outcome.applied:
        lines.append("Applied. The changes above are committed.")
    elif outcome.dry_run:
        lines.append("Dry run. Nothing was written. Re-run with --apply to commit.")
    else:
        lines.append("Refused. Nothing was written: resolve the errors above and re-run.")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_arguments(argv)

    try:
        engine = build_engine()
    except (ValueError, UnsafeDatabaseTargetError) as error:
        print(f"Database configuration refused: {error}", file=sys.stderr)
        return EXIT_MISCONFIGURED

    try:
        try:
            selection = build_values_reader(os.environ)
        except SheetCredentialError as error:
            # A fixed, operator-facing string; `read_only.py` never renders the
            # underlying Google error, which can quote credential material.
            print(f"Sheet credential refused: {error}", file=sys.stderr)
            return EXIT_MISCONFIGURED
        except sheet_failure_types() as error:
            # Building the client can also fail for transport reasons — the
            # discovery document, a proxy, DNS. That is the Sheet being
            # unreachable rather than a bad credential, and it gets the code
            # that says so instead of a traceback.
            log_expected_failure(logger, "sheets_client_unreachable", error)
            raise ImportCommandError(
                SHEET_UNAVAILABLE_MESSAGE, EXIT_SHEET_UNAVAILABLE
            ) from error
        print(selection.note, file=sys.stderr)

        try:
            rows = read_sheet_rows(
                selection, tab=arguments.tab, cell_range=arguments.cell_range
            )
        except SheetLayoutError as error:
            print(f"Sheet layout refused: {error}", file=sys.stderr)
            return EXIT_MISCONFIGURED

        outcome = execute_import(
            engine, rows, tab=arguments.tab, apply=arguments.apply
        )
    except ImportCommandError as error:
        print(str(error), file=sys.stderr)
        return error.exit_code
    finally:
        engine.dispose()

    print(render(outcome))
    return EXIT_BLOCKED if outcome.has_errors else EXIT_OK


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
