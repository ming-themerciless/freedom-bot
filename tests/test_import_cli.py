"""The operator entry point's contract: defaults, exit codes and its report.

Importing this module must not require Google credentials or a database, which
is why the tool defers its Sheets client import until it has a validated target.

The failure tests below assert two things about every expected operational
failure: that it produces a defined non-zero exit code, and that the operator
sees none of the detail — no DSN, no credential, no SQL, no Google response
body, no traceback. An import is run from a terminal whose scrollback and CI
log are not a safe place for any of those.
"""
from __future__ import annotations

import io
import json
import logging
import re
import sys
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError

from adapters.safe_logging import log_expected_failure
from adapters.sheets import read_only
from adapters.sheets.character_import import SheetLayoutError
from adapters.sheets.read_only import (
    FALLBACK_NOTE,
    READ_ONLY_CREDENTIAL_VARIABLE,
    READ_ONLY_NOTE,
    SHEET_ID_VARIABLE,
    ReaderSelection,
    SheetCredentialError,
    build_values_reader,
)
from application.errors import ConcurrencyConflictError
from application.imports import (
    ImportIssue,
    ImportIssueSeverity,
    SheetCharacterImportOutcome,
    SheetImportAction,
    SheetImportEntry,
)
from tools import import_sheet_characters as cli
from tools.import_sheet_characters import EXIT_BLOCKED, EXIT_OK, parse_arguments, render


def outcome(*, entries=(), issues=(), dry_run=True, applied=False):
    return SheetCharacterImportOutcome(
        sheet_tab="Characters",
        entries=tuple(entries),
        issues=tuple(issues),
        correlation_id=uuid4(),
        dry_run=dry_run,
        applied=applied,
    )


def test_the_default_run_is_a_dry_run():
    arguments = parse_arguments([])

    assert arguments.apply is False
    assert arguments.tab == "Characters"


def test_apply_is_opt_in():
    assert parse_arguments(["--apply"]).apply is True


def test_a_clean_dry_run_says_nothing_was_written():
    report = render(
        outcome(
            entries=[
                SheetImportEntry(3, "Test Smith A", SheetImportAction.CREATED, uuid4())
            ]
        )
    )

    assert "created   1" in report
    assert "Nothing was written" in report


def test_a_refused_run_says_so_and_lists_the_errors():
    report = render(
        outcome(
            entries=[SheetImportEntry(3, "Test Smith A", SheetImportAction.BLOCKED)],
            issues=[
                ImportIssue(3, "Character Name (short)", "dangling_mapping", "Gone."),
                ImportIssue(
                    4,
                    "Player Name",
                    "owner_unresolved",
                    "No Sheet player.",
                    severity=ImportIssueSeverity.WARNING,
                ),
            ],
            dry_run=False,
        )
    )

    assert "1 error(s), 1 warning(s)" in report
    assert "ERROR  row 3 [dangling_mapping]" in report
    assert "warn   row 4 [owner_unresolved]" in report
    assert "Refused. Nothing was written" in report


def test_an_applied_run_says_the_changes_are_committed():
    report = render(outcome(dry_run=False, applied=True))

    assert "Applied." in report


def test_the_exit_codes_are_distinct():
    codes = {
        EXIT_OK,
        EXIT_BLOCKED,
        cli.EXIT_MISCONFIGURED,
        cli.EXIT_SHEET_UNAVAILABLE,
        cli.EXIT_DATABASE_UNAVAILABLE,
        cli.EXIT_CONFLICT,
    }
    assert len(codes) == 6


# --------------------------------------------------------------------------- #
# Expected operational failures
# --------------------------------------------------------------------------- #

#: Shapes that must never reach the operator's terminal. A DSN, a bearer token,
#: a private key header, a SQL statement, or a Python traceback frame.
LEAKS = re.compile(
    r"postgresql(\+\w+)?://|BEGIN [A-Z ]*PRIVATE KEY|Traceback \(most recent"
    r"|File \"/|\bINSERT INTO\b|\bSELECT\b .*\bFROM\b|Bearer ",
    re.IGNORECASE,
)


#: Captured before any fixture replaces it, so a test can exercise the real
#: translation while everything around it stays injected.
REAL_READ_SHEET_ROWS = cli.read_sheet_rows


class _DisposableEngine:
    def __init__(self) -> None:
        self.disposed = 0

    def dispose(self) -> None:
        self.disposed += 1


class _Harness:
    def __init__(self, engine: _DisposableEngine) -> None:
        self.engine = engine
        self.run = lambda **_: outcome(dry_run=True, applied=False)


@pytest.fixture()
def cli_harness(monkeypatch):
    """`main()` with its engine and Sheet client injected, and a fake service.

    The service is faked rather than the `execute_import` wrapper, so the
    translation from an SQLAlchemy failure to an exit code is the code under
    test rather than something the test stands in for.
    """
    harness = _Harness(_DisposableEngine())

    class FakeService:
        def __init__(self, unit_of_work_factory, **kwargs) -> None:
            self.unit_of_work_factory = unit_of_work_factory

        def run(self, report, *, sheet_tab, dry_run):
            return harness.run(report=report, sheet_tab=sheet_tab, dry_run=dry_run)

    monkeypatch.setattr(cli, "build_engine", lambda: harness.engine)
    monkeypatch.setattr(cli, "SheetCharacterImportService", FakeService)
    monkeypatch.setattr(
        cli,
        "build_values_reader",
        lambda environ: ReaderSelection(
            read_values=lambda a1_range, value_render_option="UNFORMATTED_VALUE": [],
            read_only_credential=True,
            note=READ_ONLY_NOTE,
        ),
    )
    monkeypatch.setattr(
        cli, "read_sheet_rows", lambda selection, *, tab, cell_range: []
    )
    return harness


def _raising(error: Exception):
    def run(**_):
        raise error

    return run


@pytest.mark.parametrize(
    ("error", "expected_code"),
    [
        (
            OperationalError(
                "SELECT characters.id FROM characters",
                {},
                Exception('connection to server at "localhost" failed'),
            ),
            cli.EXIT_DATABASE_UNAVAILABLE,
        ),
        (
            IntegrityError(
                "INSERT INTO sheet_row_mappings", {}, Exception("duplicate key")
            ),
            cli.EXIT_CONFLICT,
        ),
        (
            ConcurrencyConflictError("Character was changed by another transaction."),
            cli.EXIT_CONFLICT,
        ),
    ],
)
def test_an_expected_database_failure_is_a_safe_message_and_a_defined_code(
    cli_harness, capsys, error, expected_code
):
    cli_harness.run = _raising(error)

    assert cli.main([]) == expected_code

    captured = capsys.readouterr()
    assert not LEAKS.search(captured.err), captured.err
    assert not LEAKS.search(captured.out), captured.out
    assert "Nothing was written" in captured.err
    # The engine is released even on the failure path.
    assert cli_harness.engine.disposed == 1


def test_an_unreadable_sheet_is_a_safe_message_and_a_defined_code(
    cli_harness, monkeypatch, capsys
):
    def unreadable(a1_range, value_render_option="UNFORMATTED_VALUE"):
        raise OSError("[Errno 101] Network is unreachable: sheets.googleapis.com")

    monkeypatch.setattr(
        cli,
        "build_values_reader",
        lambda environ: ReaderSelection(
            read_values=unreadable, read_only_credential=True, note=READ_ONLY_NOTE
        ),
    )
    monkeypatch.setattr(cli, "read_sheet_rows", REAL_READ_SHEET_ROWS)

    assert cli.main([]) == cli.EXIT_SHEET_UNAVAILABLE

    captured = capsys.readouterr()
    assert "Nothing was written" in captured.err
    assert "Errno 101" not in captured.err
    assert "sheets.googleapis.com" not in captured.err
    assert not LEAKS.search(captured.err)
    assert cli_harness.engine.disposed == 1


def test_a_refused_sheet_layout_is_reported_as_misconfiguration(
    cli_harness, monkeypatch, capsys
):
    def refuse(selection, *, tab, cell_range):
        raise SheetLayoutError("Expected column A to be 'Character Name (short)'.")

    monkeypatch.setattr(cli, "read_sheet_rows", refuse)

    assert cli.main([]) == cli.EXIT_MISCONFIGURED
    assert "Sheet layout refused" in capsys.readouterr().err


def test_a_refused_read_only_credential_is_reported_as_misconfiguration(
    cli_harness, monkeypatch, capsys
):
    def refuse(environ):
        raise SheetCredentialError(
            f"{READ_ONLY_CREDENTIAL_VARIABLE} must be valid single-line JSON."
        )

    monkeypatch.setattr(cli, "build_values_reader", refuse)

    assert cli.main([]) == cli.EXIT_MISCONFIGURED
    captured = capsys.readouterr()
    assert "Sheet credential refused" in captured.err
    assert not LEAKS.search(captured.err)


def test_a_clean_run_still_exits_zero_and_releases_the_engine(cli_harness, capsys):
    assert cli.main([]) == EXIT_OK
    assert cli_harness.engine.disposed == 1
    assert "Dry run" in capsys.readouterr().out


def test_a_run_that_reports_errors_exits_blocked(cli_harness):
    cli_harness.run = lambda **_: outcome(
        issues=[ImportIssue(3, "Character Name (short)", "dangling_mapping", "Gone.")],
        dry_run=False,
    )

    assert cli.main([]) == EXIT_BLOCKED


# --------------------------------------------------------------------------- #
# Credential scope: the importer only reads, and says which credential it used
# --------------------------------------------------------------------------- #


def test_without_a_read_only_credential_the_shared_one_is_used_and_announced():
    selection = build_values_reader(
        {}, read_only_factory=_unused_factory, shared_factory=lambda: _marker_reader
    )

    assert selection.read_values is _marker_reader
    assert selection.read_only_credential is False
    assert selection.note == FALLBACK_NOTE


def test_a_configured_read_only_credential_is_preferred():
    selection = build_values_reader(
        {
            READ_ONLY_CREDENTIAL_VARIABLE: '{"type": "service_account"}',
            SHEET_ID_VARIABLE: "test-sheet-id",
        },
        read_only_factory=lambda credential, sheet_id: _marker_reader,
        shared_factory=_unused_factory,
    )

    assert selection.read_values is _marker_reader
    assert selection.read_only_credential is True


def test_a_read_only_credential_without_a_spreadsheet_id_is_refused():
    with pytest.raises(SheetCredentialError):
        build_values_reader(
            {READ_ONLY_CREDENTIAL_VARIABLE: '{"type": "service_account"}'},
            read_only_factory=_unused_factory,
            shared_factory=_unused_factory,
        )


def test_a_blank_read_only_credential_falls_back_rather_than_failing():
    selection = build_values_reader(
        {READ_ONLY_CREDENTIAL_VARIABLE: "   "},
        read_only_factory=_unused_factory,
        shared_factory=lambda: _marker_reader,
    )

    assert selection.read_only_credential is False


def _marker_reader(a1_range, value_render_option="UNFORMATTED_VALUE"):
    raise AssertionError("the marker reader is never called")


def _unused_factory(*args, **kwargs):
    raise AssertionError("this factory must not be used")


# --------------------------------------------------------------------------- #
# Malformed read-only credentials
#
# `SHEET_READONLY_SERVICE_ACCOUNT_JSON` is operator-supplied, so every way it can
# be wrong must reach the operator as the documented misconfiguration code and a
# safe message. Google's construction raises `MalformedError`, `InvalidValue` and
# `binascii.Error` — and quotes the offending field value back in the message —
# so neither the exception nor a traceback may be rendered.
#
# All of this is synthetic and non-secret: the "keys" below are obviously fake
# strings, no real service account exists, and nothing here reaches the network.
# Credential construction fails long before any client is built or any request
# is made.
# --------------------------------------------------------------------------- #

#: A structurally complete service-account document whose private key is not a
#: key. Enough to get past the field-presence check and fail in the crypto layer.
SYNTHETIC_UNUSABLE_CREDENTIAL = json.dumps(
    {
        "type": "service_account",
        "project_id": "synthetic-test-project",
        "private_key_id": "0000000000000000000000000000000000000000",
        "private_key": "-----BEGIN PRIVATE KEY-----\nnot-a-key\n-----END PRIVATE KEY-----\n",
        "client_email": "synthetic@synthetic-test-project.iam.invalid",
        "token_uri": "https://oauth2.invalid/token",
    }
)

#: Valid JSON, valid service-account *shape*, missing the required fields.
SYNTHETIC_INCOMPLETE_CREDENTIAL = json.dumps(
    {"type": "service_account", "project_id": "synthetic-test-project"}
)

#: Anything the operator may plausibly paste that is not a JSON object.
SYNTHETIC_NOT_AN_OBJECT = '["synthetic", "not", "an", "object"]'

#: Truncated: what a shell that ate the closing brace produces.
SYNTHETIC_INVALID_JSON = '{"type": "service_account", "private_key": "-----BEGIN'

CREDENTIAL_CASES = {
    "invalid JSON": SYNTHETIC_INVALID_JSON,
    "valid JSON that is not an object": SYNTHETIC_NOT_AN_OBJECT,
    "incomplete service account": SYNTHETIC_INCOMPLETE_CREDENTIAL,
    "unusable private key": SYNTHETIC_UNUSABLE_CREDENTIAL,
}


@pytest.fixture()
def google_libraries():
    """Skip rather than pass vacuously where the Google libraries are absent."""
    pytest.importorskip("google.oauth2.service_account")
    pytest.importorskip("google.auth.exceptions")


@pytest.mark.parametrize(
    "credential", CREDENTIAL_CASES.values(), ids=list(CREDENTIAL_CASES)
)
def test_a_malformed_read_only_credential_is_refused_not_raised(
    google_libraries, credential
):
    """The adapter translates it, so nothing propagates out of the reader."""
    with pytest.raises(SheetCredentialError):
        build_values_reader(
            {
                READ_ONLY_CREDENTIAL_VARIABLE: credential,
                SHEET_ID_VARIABLE: "synthetic-sheet-id",
            },
            shared_factory=_unused_factory,
        )


@pytest.mark.parametrize(
    "credential", CREDENTIAL_CASES.values(), ids=list(CREDENTIAL_CASES)
)
def test_a_malformed_read_only_credential_exits_misconfigured_and_says_nothing(
    google_libraries, cli_harness, monkeypatch, capsys, credential
):
    """The documented exit code, and an operator-safe terminal.

    `build_values_reader` is restored to the real one so the translation is the
    code under test; only the database engine stays injected.
    """
    monkeypatch.setattr(cli, "build_values_reader", build_values_reader)
    monkeypatch.setenv(READ_ONLY_CREDENTIAL_VARIABLE, credential)
    monkeypatch.setenv(SHEET_ID_VARIABLE, "synthetic-sheet-id")

    assert cli.main([]) == cli.EXIT_MISCONFIGURED

    captured = capsys.readouterr()
    assert "Sheet credential refused" in captured.err
    assert not LEAKS.search(captured.err), captured.err
    assert not LEAKS.search(captured.out), captured.out
    # None of the configured document reaches the operator: not the key body,
    # not the service-account address, not the project.
    for secret in ("not-a-key", "synthetic@", "synthetic-test-project", "BEGIN"):
        assert secret not in captured.err
        assert secret not in captured.out
    # The engine is released even though the run never reached the Sheet.
    assert cli_harness.engine.disposed == 1


def test_the_unusable_credential_case_really_does_reach_googles_construction(
    google_libraries,
):
    """Guards the test above from passing for the wrong reason.

    If Google ever accepted this document, the misconfiguration path would be
    tested by a case that no longer exercises it.
    """
    from google.oauth2 import service_account

    with pytest.raises(ValueError):
        service_account.Credentials.from_service_account_info(
            json.loads(SYNTHETIC_UNUSABLE_CREDENTIAL), scopes=["synthetic"]
        )


def test_a_missing_google_library_is_a_refusal_rather_than_an_import_error(
    monkeypatch,
):
    """`SHEET_READONLY_SERVICE_ACCOUNT_JSON` set without the libraries installed."""
    monkeypatch.setitem(sys.modules, "google.oauth2", None)

    with pytest.raises(SheetCredentialError) as refusal:
        build_values_reader(
            {
                READ_ONLY_CREDENTIAL_VARIABLE: SYNTHETIC_INCOMPLETE_CREDENTIAL,
                SHEET_ID_VARIABLE: "synthetic-sheet-id",
            },
            shared_factory=_unused_factory,
        )

    assert "Google API libraries" in str(refusal.value)


def test_a_transport_failure_building_the_client_is_reported_as_unreadable(
    cli_harness, monkeypatch, capsys
):
    """A proxy or DNS failure while building the client is not a bad credential.

    It gets the documented "could not be read" code rather than a traceback or a
    misleading "credential refused".
    """

    def unreachable(environ):
        raise OSError("[Errno -2] Name or service not known: sheets.googleapis.com")

    monkeypatch.setattr(cli, "build_values_reader", unreachable)

    assert cli.main([]) == cli.EXIT_SHEET_UNAVAILABLE

    captured = capsys.readouterr()
    assert "Nothing was written" in captured.err
    assert "Errno -2" not in captured.err
    assert not LEAKS.search(captured.err)
    assert cli_harness.engine.disposed == 1


# --------------------------------------------------------------------------- #
# The Google *client* library, separately from google-auth
#
# `google-auth` and `google-api-python-client` are distinct distributions. A
# partial install can therefore satisfy the credential half and fail at the
# discovery import that comes after it, which would reach the operator as an
# `ImportError` traceback rather than the documented dependency refusal.
#
# Neither test needs a real service-account key or a network: the credential is
# replaced by a sentinel, so the only thing under test is what happens at the
# import that follows it.
# --------------------------------------------------------------------------- #


@pytest.fixture()
def credentials_without_a_key(monkeypatch):
    """`_read_only_credentials` replaced by a sentinel, so no key is needed."""
    sentinel = object()
    monkeypatch.setattr(read_only, "_read_only_credentials", lambda raw: sentinel)
    return sentinel


def _hide_module(monkeypatch, name: str) -> None:
    """Make `import name` fail the way an uninstalled distribution does."""
    monkeypatch.setitem(sys.modules, name, None)


def test_a_missing_google_client_library_is_a_refusal_rather_than_an_import_error(
    credentials_without_a_key, monkeypatch
):
    _hide_module(monkeypatch, "googleapiclient.discovery")

    with pytest.raises(SheetCredentialError) as refusal:
        build_values_reader(
            {
                READ_ONLY_CREDENTIAL_VARIABLE: SYNTHETIC_INCOMPLETE_CREDENTIAL,
                SHEET_ID_VARIABLE: "synthetic-sheet-id",
            },
            shared_factory=_unused_factory,
        )

    assert "Google API libraries" in str(refusal.value)


def test_a_missing_google_client_library_exits_misconfigured(
    credentials_without_a_key, cli_harness, monkeypatch, capsys
):
    """The same documented exit code as the missing credential library."""
    _hide_module(monkeypatch, "googleapiclient.discovery")
    monkeypatch.setattr(cli, "build_values_reader", build_values_reader)
    monkeypatch.setenv(READ_ONLY_CREDENTIAL_VARIABLE, SYNTHETIC_INCOMPLETE_CREDENTIAL)
    monkeypatch.setenv(SHEET_ID_VARIABLE, "synthetic-sheet-id")

    assert cli.main([]) == cli.EXIT_MISCONFIGURED

    captured = capsys.readouterr()
    assert "Sheet credential refused" in captured.err
    assert "Google API libraries" in captured.err
    assert not LEAKS.search(captured.err), captured.err
    assert cli_harness.engine.disposed == 1


def test_the_client_library_guard_does_not_swallow_an_unrelated_import_error(
    credentials_without_a_key, monkeypatch
):
    """Only the discovery import is guarded, not this repository's own imports.

    A defect elsewhere must not be reported to an operator as a missing
    dependency, so the guard is proven to be around one import rather than
    around the function.
    """
    monkeypatch.setattr(
        read_only,
        "_read_only_credentials",
        lambda raw: (_ for _ in ()).throw(ImportError("a defect, not a dependency")),
    )

    with pytest.raises(ImportError):
        read_only._build_read_only_reader("{}", "synthetic-sheet-id")


# --------------------------------------------------------------------------- #
# Debug logging retains nothing either
#
# The fixed operator-facing strings above are only half of the guarantee. An
# expected failure also produces a diagnostic log line, and an exception attached
# to it — by `exc_info=`, by interpolation, or by `%s` — puts the same private-key
# fragment, DSN, SQL statement or Google response body into journald, a CI job
# log or a log collector. Debug logging is still logging: `logging.lastResort`
# suppressing DEBUG by default only means the disclosure is invisible until
# somebody turns logging on.
#
# Every case below plants a synthetic canary inside the exception's message, so
# the assertions fail if either the message or a traceback is retained anywhere.
# The canaries are invented strings; no real credential, database or player data
# appears in this file.
# --------------------------------------------------------------------------- #

#: Planted in an exception message. If this string reaches a log record, a
#: terminal or a formatted traceback, the exception was retained.
CANARY_KEY_MATERIAL = "CANARY-PRIVATE-KEY-MATERIAL-9f2a"
CANARY_SERVICE_ACCOUNT = "canary-account@synthetic-canary-project.iam.invalid"
CANARY_DSN = "postgresql+psycopg://canary_user:CANARY-DB-PASSWORD-3e11@localhost/canary_db"
CANARY_SQL = "SELECT canary_column FROM canary_table WHERE id = 'CANARY-SQL-7c04'"
CANARY_HOST = "canary-host-5b93.sheets.googleapis.invalid"

#: A service-account document whose `private_key` is a JSON object rather than a
#: PEM string. Google's `InvalidValue` renders the offending value back verbatim
#: — `"{'canary': '…'} could not be converted to unicode"` — which is exactly the
#: disclosure this section exists to prevent.
SYNTHETIC_CANARY_CREDENTIAL = json.dumps(
    {
        "type": "service_account",
        "project_id": "synthetic-canary-project",
        "private_key_id": "0000000000000000000000000000000000000000",
        "private_key": {"canary": CANARY_KEY_MATERIAL},
        "client_email": CANARY_SERVICE_ACCOUNT,
        "token_uri": "https://oauth2.invalid/token",
    }
)


@pytest.fixture()
def debug_log():
    """Root logging at DEBUG, formatted the way a real handler formats it.

    The formatter is the point: `logging.Formatter` appends `record.exc_text`
    whenever a record carries `exc_info`, so a traceback shows up in this stream
    exactly as it would in journald or a CI log.
    """
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))
    root = logging.getLogger()
    previous_level = root.level
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)
    try:
        yield stream
    finally:
        root.removeHandler(handler)
        root.setLevel(previous_level)


def _assert_nothing_leaked(*, canaries, debug_log, caplog, captured):
    """No canary in any log stream, and no record carrying an exception."""
    surfaces = {
        "debug log": debug_log.getvalue(),
        "caplog": caplog.text,
        "stdout": captured.out,
        "stderr": captured.err,
    }
    for canary in canaries:
        for name, text in surfaces.items():
            assert canary not in text, f"{canary!r} reached {name}: {text}"
    for name, text in surfaces.items():
        assert not LEAKS.search(text), f"{name}: {text}"
    for record in caplog.records:
        assert record.exc_info is None, record.exc_info
        assert record.exc_text is None, record.exc_text


@pytest.mark.parametrize(
    ("error", "expected_code", "category"),
    [
        (
            OperationalError(CANARY_SQL, {}, Exception(f"could not connect: {CANARY_DSN}")),
            cli.EXIT_DATABASE_UNAVAILABLE,
            "database_unavailable",
        ),
        (
            IntegrityError(CANARY_SQL, {}, Exception(f"duplicate key: {CANARY_DSN}")),
            cli.EXIT_CONFLICT,
            "import_conflict",
        ),
        (
            ConcurrencyConflictError(f"stale row while running {CANARY_SQL}"),
            cli.EXIT_CONFLICT,
            "import_conflict",
        ),
    ],
)
def test_a_database_failure_leaves_nothing_in_the_logs_at_debug(
    cli_harness, debug_log, caplog, capsys, error, expected_code, category
):
    caplog.set_level(logging.DEBUG)
    cli_harness.run = _raising(error)

    assert cli.main([]) == expected_code

    _assert_nothing_leaked(
        canaries=(CANARY_SQL, CANARY_DSN, "CANARY-DB-PASSWORD-3e11", "canary_table"),
        debug_log=debug_log,
        caplog=caplog,
        captured=capsys.readouterr(),
    )
    # Not vacuous: the safe diagnostic really was recorded.
    assert category in debug_log.getvalue()
    assert type(error).__name__ in debug_log.getvalue()


def test_an_unreadable_sheet_leaves_nothing_in_the_logs_at_debug(
    cli_harness, debug_log, caplog, capsys, monkeypatch
):
    caplog.set_level(logging.DEBUG)

    def unreadable(a1_range, value_render_option="UNFORMATTED_VALUE"):
        raise OSError(f"[Errno 101] Network is unreachable: {CANARY_HOST}")

    monkeypatch.setattr(
        cli,
        "build_values_reader",
        lambda environ: ReaderSelection(
            read_values=unreadable, read_only_credential=True, note=READ_ONLY_NOTE
        ),
    )
    monkeypatch.setattr(cli, "read_sheet_rows", REAL_READ_SHEET_ROWS)

    assert cli.main([]) == cli.EXIT_SHEET_UNAVAILABLE

    _assert_nothing_leaked(
        canaries=(CANARY_HOST, "Errno 101"),
        debug_log=debug_log,
        caplog=caplog,
        captured=capsys.readouterr(),
    )
    assert "sheet_read_failed" in debug_log.getvalue()


def test_a_transport_failure_building_the_client_leaves_nothing_in_the_logs(
    cli_harness, debug_log, caplog, capsys, monkeypatch
):
    caplog.set_level(logging.DEBUG)

    def unreachable(environ):
        raise OSError(f"[Errno -2] Name or service not known: {CANARY_HOST}")

    monkeypatch.setattr(cli, "build_values_reader", unreachable)

    assert cli.main([]) == cli.EXIT_SHEET_UNAVAILABLE

    _assert_nothing_leaked(
        canaries=(CANARY_HOST, "Errno -2"),
        debug_log=debug_log,
        caplog=caplog,
        captured=capsys.readouterr(),
    )
    assert "sheets_client_unreachable" in debug_log.getvalue()


def test_a_refused_credential_leaves_no_key_material_in_the_logs_at_debug(
    google_libraries, cli_harness, debug_log, caplog, capsys, monkeypatch
):
    """The whole point, end to end: Google quotes the key, and nothing keeps it."""
    caplog.set_level(logging.DEBUG)
    monkeypatch.setattr(cli, "build_values_reader", build_values_reader)
    monkeypatch.setenv(READ_ONLY_CREDENTIAL_VARIABLE, SYNTHETIC_CANARY_CREDENTIAL)
    monkeypatch.setenv(SHEET_ID_VARIABLE, "synthetic-sheet-id")

    assert cli.main([]) == cli.EXIT_MISCONFIGURED

    _assert_nothing_leaked(
        canaries=(
            CANARY_KEY_MATERIAL,
            CANARY_SERVICE_ACCOUNT,
            "synthetic-canary-project",
        ),
        debug_log=debug_log,
        caplog=caplog,
        captured=capsys.readouterr(),
    )
    assert "read_only_credential_refused" in debug_log.getvalue()


def test_the_canary_credential_really_is_quoted_back_by_google(google_libraries):
    """Guards the test above from passing because the canary was never there.

    If Google ever stopped rendering the offending value, the leak test would
    still pass while proving nothing.
    """
    from google.oauth2 import service_account

    with pytest.raises(ValueError) as refusal:
        service_account.Credentials.from_service_account_info(
            json.loads(SYNTHETIC_CANARY_CREDENTIAL), scopes=["synthetic"]
        )

    assert CANARY_KEY_MATERIAL in str(refusal.value)


def test_the_safe_diagnostic_records_the_category_and_class_and_nothing_else(
    debug_log, caplog
):
    """`log_expected_failure` itself: two fixed facts, no exception."""
    caplog.set_level(logging.DEBUG)
    logger = logging.getLogger("tests.safe_logging")

    log_expected_failure(logger, "synthetic_category", ValueError(CANARY_KEY_MATERIAL))

    written = debug_log.getvalue()
    assert "synthetic_category" in written
    assert "ValueError" in written
    assert CANARY_KEY_MATERIAL not in written
    assert CANARY_KEY_MATERIAL not in caplog.text
    assert [record.exc_info for record in caplog.records] == [None]
