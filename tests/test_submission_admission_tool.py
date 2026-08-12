"""The settlement tool as an operator actually runs it. C-24 finishing pass.

Three defects motivated this file, and each of them was invisible to a test that
called `open_admission()` with a prebuilt engine:

1. **The documented commands could not run.** The runbook showed
   `DATABASE_URL='postgresql+psycopg:///freedom'`, while `DatabaseSettings`
   validates the database name against `APP_ENVIRONMENT` and defaults that to
   `development`. Copied out of the page, the settlement command refused before
   settlement began — with exit code 2, at the worst possible moment. So the
   documented *shape* is exercised here, parsed out of the runbook itself, far
   enough to prove configuration validation accepts it.
2. **The correlation columns named nothing.** The admission row took
   `gen_random_uuid()` while `_audit()` minted a separate UUID, so
   `correlation_id` and `closed_correlation_id` could not identify the
   append-only events they exist to point at. The tests below join the two.
3. **Expected failures escaped as tracebacks.** A `lock_timeout` is a documented
   **Unsettled** outcome, not a crash, and an operator settling an episode has to
   be able to tell "nothing was closed, retry" from "nothing was closed,
   escalate" without reading a stack trace or being shown a connection string.

Everything here is synthetic and local: the disposable `freedom_test` database,
placeholder role names, and no real credential anywhere.
"""
from __future__ import annotations

import re
from pathlib import Path
from uuid import UUID

import pytest
from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.exc import DBAPIError, OperationalError, ProgrammingError

from adapters.database.config import EXPECTED_DATABASES
from adapters.database.safety import UnsafeDatabaseTargetError
from application.admissions import ADMISSION_LOCK_KEY, PRE_FENCE_PRINCIPAL
from application.foundry.audit_policy import ADMISSION_CLOSED, ADMISSION_OPENED
from tests.test_runtime_grants_live import RUNTIME_ROLE, grant_statements
from tools import submission_admission as tool

ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs" / "operations" / "foundry-snapshot-submission.md"

PRINCIPAL = "foundry-the-guild"
RECOVERY_PRINCIPAL = "foundry-the-guild-r1"

# =============================================================================
# 1. The documented commands are accepted by configuration validation
# =============================================================================


def _shell_commands(markdown: str) -> list[str]:
    """Every command in every ```bash block, with continuations joined.

    Deliberately reads the runbook rather than a copy of it. A test holding its
    own copy of the documented command proves the copy is well formed and says
    nothing about the page an operator will actually read at 2 a.m.
    """
    commands: list[str] = []
    for block in re.findall(r"```bash\n(.*?)```", markdown, flags=re.DOTALL):
        pending: list[str] = []
        for raw in block.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.endswith("\\"):
                pending.append(line[:-1].strip())
                continue
            pending.append(line)
            commands.append(" ".join(pending))
            pending = []
        if pending:
            commands.append(" ".join(pending))
    return commands


ASSIGNMENT = re.compile(r"^([A-Z][A-Z0-9_]*)=(?:'([^']*)'|\"([^\"]*)\"|(\S+))$")


def _leading_environment(command: str) -> dict[str, str]:
    """The `NAME=value` assignments a shell would apply to this command."""
    environment: dict[str, str] = {}
    for token in command.split():
        match = ASSIGNMENT.match(token)
        if match is None:
            break
        name, single, double, bare = match.groups()
        environment[name] = next(
            value for value in (single, double, bare) if value is not None
        )
    return environment


def documented_invocations() -> list[tuple[str, dict[str, str]]]:
    return [
        (command, _leading_environment(command))
        for command in _shell_commands(RUNBOOK.read_text(encoding="utf-8"))
        if "tools.submission_admission" in command
    ]


def test_the_runbook_documents_admission_commands_at_all():
    """Guards the parser. A test that silently matched nothing would pass."""
    invocations = documented_invocations()
    assert len(invocations) >= 4, (
        "the runbook should document show/open/close; the parser found "
        f"{len(invocations)} invocation(s)"
    )
    subcommands = {
        command.split("tools.submission_admission", 1)[1].split()[0]
        for command, _ in invocations
    }
    assert {"show", "open", "close"} <= subcommands


@pytest.mark.parametrize(
    ("command", "environment"),
    documented_invocations(),
    ids=lambda value: None,
)
def test_every_documented_invocation_is_accepted_by_configuration_validation(
    command: str, environment: dict[str, str]
):
    """**The defect this file exists for.** The page must be runnable.

    `build_engine` is the whole configuration path the tool takes before it
    connects: `DatabaseSettings.from_mapping` resolves `APP_ENVIRONMENT`, the
    URL and the ambient libpq environment into one target, checks the database
    name against the environment, and applies the connection policy. If a
    documented command cannot get past it, the command refuses with exit code 2
    and settles nothing.

    `create_engine` opens no connection, so this proves acceptance without
    touching a database — which is what lets it cover the *production* form.
    """
    engine = tool.build_engine(environment)
    try:
        assert engine.url.database == EXPECTED_DATABASES[
            environment.get("APP_ENVIRONMENT", "development")
        ]
    finally:
        engine.dispose()


@pytest.mark.parametrize(("command", "environment"), documented_invocations(), ids=lambda v: None)
def test_every_documented_invocation_names_its_environment_and_database(
    command: str, environment: dict[str, str]
):
    """The pairing is the safety boundary, so the page must state both halves.

    `APP_ENVIRONMENT` defaults to `development`; a command that names a
    production URL without it is refused, and a command that names neither
    reaches `freedom_dev`. Either is a wrong answer during a settlement, so
    every documented invocation names both explicitly.
    """
    assert "APP_ENVIRONMENT" in environment, command
    assert "DATABASE_URL" in environment, command
    assert (
        environment["DATABASE_URL"].count("freedom") == 1
    ), f"{command} should name exactly one database"


def test_the_documented_production_command_is_refused_without_its_environment():
    """The defect, reproduced: the old page's shape still refuses.

    This is the failure an operator met when copying the previous runbook. It is
    kept as a test rather than deleted with the documentation, because the
    refusal is the *correct* behaviour and must not be softened to make an
    example work.
    """
    with pytest.raises(ValueError) as refusal:
        tool.build_engine(
            {"DATABASE_URL": "postgresql+psycopg://__OWNER_ROLE__@/freedom_production"}
        )

    assert "freedom_dev" in str(refusal.value)
    assert "freedom_production" in str(refusal.value)


def test_the_old_documented_url_is_refused_in_every_environment():
    """`postgresql+psycopg:///freedom` is not a database this platform has."""
    for environment_name in EXPECTED_DATABASES:
        with pytest.raises(ValueError):
            tool.build_engine(
                {
                    "APP_ENVIRONMENT": environment_name,
                    "DATABASE_URL": "postgresql+psycopg:///freedom",
                }
            )


def test_a_named_remote_host_is_refused():
    """The tool's `SOCKET_OR_LOOPBACK` policy, exercised through `build_engine`."""
    with pytest.raises(UnsafeDatabaseTargetError):
        tool.build_engine(
            {
                "APP_ENVIRONMENT": "production",
                "DATABASE_URL": "postgresql+psycopg://__OWNER_ROLE__@db.example.org/freedom_production",
            }
        )


def test_main_reports_an_unusable_target_as_exit_two_without_echoing_the_url(
    monkeypatch, capsys
):
    monkeypatch.setenv("APP_ENVIRONMENT", "production")
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+psycopg://secret_user:hunter2@/freedom_dev"
    )

    code = tool.main(["show"])

    assert code == tool.EXIT_UNSAFE_TARGET
    captured = capsys.readouterr()
    assert "hunter2" not in captured.err
    assert "secret_user" not in captured.err
    assert "postgresql+psycopg://" not in captured.err


def test_the_runbook_documents_every_exit_code_the_tool_can_return():
    """Exit codes are an operator interface; an undocumented one is a defect."""
    runbook = RUNBOOK.read_text(encoding="utf-8")
    codes = {
        tool.EXIT_OK,
        tool.EXIT_REFUSED,
        tool.EXIT_UNSAFE_TARGET,
        tool.EXIT_CANNOT_CONNECT,
        tool.EXIT_INSUFFICIENT_PRIVILEGE,
        tool.EXIT_LOCK_TIMEOUT,
        tool.EXIT_DATABASE_FAILURE,
        tool.EXIT_OUTCOME_UNKNOWN,
    }
    assert codes == set(range(8)), "the exit codes should be a dense, small set"
    table = runbook.split("**Exit codes.**", 1)[1].split("###", 1)[0]
    for code in sorted(codes):
        assert f"| {code} |" in table, f"exit code {code} is not documented"
    assert "Unsettled" in table
    assert "Outcome unknown" in table, (
        "the ambiguous outcome must be named in the table an operator reads, "
        "not only in the tool's own docstring"
    )


# =============================================================================
# 2. Failure classification — deterministic, and never a false success
# =============================================================================


class _FakeDiagnostic:
    def __init__(self, message_primary: str | None) -> None:
        self.message_primary = message_primary


class _FakeDriverError(Exception):
    def __init__(self, sqlstate: str | None, primary: str | None = None) -> None:
        super().__init__(primary or "")
        self.sqlstate = sqlstate
        self.diag = _FakeDiagnostic(primary)


def _dbapi_error(sqlstate: str | None, primary: str | None = None) -> DBAPIError:
    """A `DBAPIError` carrying `statement` and `params`, exactly as a real one does.

    The statement and parameters are supplied on purpose: `str()` of a
    SQLAlchemy `DBAPIError` appends them, so a message built from the exception
    would leak SQL into operator output. These tests assert it does not.
    """
    return DBAPIError(
        statement="UPDATE submission_admissions SET state = 'closed' WHERE id = %(id)s",
        params={"id": "6f1c0e4e-0000-0000-0000-000000000000"},
        orig=_FakeDriverError(sqlstate, primary),
    )


def _before_the_transaction() -> tool.CommandProgress:
    """A command that never established a transaction. Nothing was written."""
    return tool.CommandProgress()


def _after_the_transaction_began() -> tool.CommandProgress:
    """A command whose transaction was established before the failure."""
    progress = tool.CommandProgress()
    progress.transaction_began()
    return progress


@pytest.mark.parametrize("command", ["open", "close", "show"])
def test_a_connection_failure_is_exit_three_and_says_nothing_was_written(command):
    """No SQLSTATE **and no transaction** means nothing ever reached a server."""
    failure = tool.classify_database_failure(
        _dbapi_error(None), command=command, progress=_before_the_transaction()
    )

    assert failure.exit_code == tool.EXIT_CANNOT_CONNECT
    assert "Could not reach the database" in failure.message
    assert "APP_ENVIRONMENT" in failure.message


def test_a_lock_timeout_on_close_is_exit_five_and_named_unsettled():
    """The documented **Unsettled** outcome, and the one that is safe to retry."""
    failure = tool.classify_database_failure(
        _dbapi_error(tool.SQLSTATE_LOCK_NOT_AVAILABLE, "canceling statement due to lock timeout"),
        command="close",
        progress=_after_the_transaction_began(),
    )

    assert failure.exit_code == tool.EXIT_LOCK_TIMEOUT
    assert "Unsettled" in failure.message
    assert "safe to retry" in failure.message
    assert "No generation was closed" in failure.message
    assert tool.SQLSTATE_LOCK_NOT_AVAILABLE in failure.message


def test_a_lock_timeout_on_open_is_exit_five_and_opens_nothing():
    failure = tool.classify_database_failure(
        _dbapi_error(tool.SQLSTATE_LOCK_NOT_AVAILABLE),
        command="open",
        progress=_after_the_transaction_began(),
    )

    assert failure.exit_code == tool.EXIT_LOCK_TIMEOUT
    assert "No generation was opened" in failure.message


def test_insufficient_privilege_is_exit_four_and_names_the_owner_requirement():
    failure = tool.classify_database_failure(
        _dbapi_error(
            tool.SQLSTATE_INSUFFICIENT_PRIVILEGE,
            "permission denied for table submission_admissions",
        ),
        command="close",
        progress=_after_the_transaction_began(),
    )

    assert failure.exit_code == tool.EXIT_INSUFFICIENT_PRIVILEGE
    assert "owns" in failure.message
    assert "runtime" in failure.message
    assert "permission denied for table submission_admissions" in failure.message


def test_any_other_database_failure_is_exit_six_and_reports_its_sqlstate():
    failure = tool.classify_database_failure(
        _dbapi_error("40001", "could not serialize access due to concurrent update"),
        command="close",
        progress=_after_the_transaction_began(),
    )

    assert failure.exit_code == tool.EXIT_DATABASE_FAILURE
    assert "did not commit" in failure.message
    assert "40001" in failure.message


@pytest.mark.parametrize(
    "sqlstate",
    [None, tool.SQLSTATE_LOCK_NOT_AVAILABLE, tool.SQLSTATE_INSUFFICIENT_PRIVILEGE, "40001"],
)
@pytest.mark.parametrize("command", ["open", "close", "show"])
def test_no_classified_failure_leaks_sql_or_claims_success(sqlstate, command):
    """The two properties every branch must have, asserted over every branch.

    A message that claimed a closure would authorize a fresh export against a
    generation that is still open, which is the whole failure B-1 is about; and
    a message carrying the statement would put table names, bound parameters and
    — for another statement — potentially a connection string into an operator's
    terminal and their incident notes.

    Every branch here is reached with the transaction rolled back — a server
    SQLSTATE means the server answered, and a missing one *with no transaction
    established* means nothing was ever sent — so each may state that nothing
    happened. The one branch that may not is covered on its own below.
    """
    failure = tool.classify_database_failure(
        _dbapi_error(sqlstate, "a primary message"),
        command=command,
        progress=_before_the_transaction(),
    )
    negation = {
        "open": "No generation was opened",
        "close": "No generation was closed",
        "show": "Nothing was read",
    }[command]

    assert failure.exit_code != tool.EXIT_OK
    assert negation in failure.message, "a failure must state that nothing happened"
    assert "UPDATE submission_admissions" not in failure.message
    assert "6f1c0e4e" not in failure.message
    assert "Traceback" not in failure.message
    # The success wording `main` prints on exit 0, which no failure may borrow.
    assert "Closed generation" not in failure.message
    assert "Opened generation" not in failure.message


# =============================================================================
# 2b. An absent SQLSTATE is not proof that nothing committed
# =============================================================================
#
# The second finding of the C-24 independent review. A `DBAPIError` with no
# SQLSTATE means the client heard nothing back — and a connection can be lost
# while PostgreSQL is processing or acknowledging `COMMIT`, so the server may
# have committed while the client sees only an error. The tool used to read that
# absence as "could not connect" and tell the operator, for `close`, that no
# generation was closed and the fence was unchanged. That is the one claim it
# must never make on this evidence: an operator who believes it authorizes a
# fresh export against a generation that may already be settled.


@pytest.mark.parametrize("command", ["open", "close"])
def test_a_connection_lost_after_the_transaction_began_is_an_unknown_outcome(command):
    """**The finding.** Exit 7, and no claim in either direction."""
    failure = tool.classify_database_failure(
        _dbapi_error(None),
        command=command,
        progress=_after_the_transaction_began(),
    )

    assert failure.exit_code == tool.EXIT_OUTCOME_UNKNOWN
    assert "Outcome unknown" in failure.message
    assert "Unsettled" in failure.message
    # The verification it must send the operator to, before anything else.
    assert "`show`" in failure.message
    assert "audit event" in failure.message


@pytest.mark.parametrize("command", ["open", "close"])
def test_an_unknown_outcome_never_claims_the_transition_did_not_commit(command):
    """The wording, asserted as prohibitions rather than trusted to review.

    Each phrase below is a claim about durable state that this evidence cannot
    support. The old classification made two of them.
    """
    failure = tool.classify_database_failure(
        _dbapi_error(None, "a primary message"),
        command=command,
        progress=_after_the_transaction_began(),
    )
    message = failure.message

    for prohibited in (
        "No generation was closed",
        "No generation was opened",
        "the fence is unchanged",
        "did not commit",
        "Could not reach the database",
        "Nothing was written",
    ):
        assert prohibited not in message, f"an unknown outcome claimed: {prohibited}"
    # And it is still an expected operational condition, not a crash report.
    assert "UPDATE submission_admissions" not in message
    assert "6f1c0e4e" not in message
    assert "Traceback" not in message
    assert "Closed generation" not in message
    assert "Opened generation" not in message


def test_an_unknown_close_says_a_verified_close_may_simply_be_repeated():
    """`close` is idempotent — *after* verification, which is the ordering."""
    failure = tool.classify_database_failure(
        _dbapi_error(None), command="close", progress=_after_the_transaction_began()
    )

    assert "idempotent" in failure.message
    assert "fresh export" in failure.message


def test_an_unknown_open_says_it_must_be_verified_before_another_is_attempted():
    """A credential holds at most one admission for all time, so a blind second
    `open` is refused permanently — the operator has to look first."""
    failure = tool.classify_database_failure(
        _dbapi_error(None), command="open", progress=_after_the_transaction_began()
    )

    assert "verified before" in failure.message
    assert "at most one admission" in failure.message


def test_show_has_no_ambiguous_outcome_because_it_writes_nothing():
    """The ambiguity is about durability, and a read has none to be unsure of."""
    failure = tool.classify_database_failure(
        _dbapi_error(None), command="show", progress=_after_the_transaction_began()
    )

    assert failure.exit_code == tool.EXIT_CANNOT_CONNECT
    assert "Nothing was read" in failure.message


def test_progress_is_recorded_rather_than_inferred():
    """The classification's input is a fact this run recorded, not a guess."""
    progress = tool.CommandProgress()
    assert progress.began is False
    progress.transaction_began()
    assert progress.began is True


# =============================================================================
# 3. Against a real PostgreSQL: correlation, and the failures an operator meets
# =============================================================================

pytest_plugins = ()


def _engine_as_runtime_role(url: str) -> Engine:
    """An engine that assumes the restricted runtime role on every connection.

    This is how the privilege case is reproduced without inventing a login: the
    tool's own code path runs unchanged, and PostgreSQL answers as it would for
    an operator who used the service's `DATABASE_URL` by mistake — which is the
    realistic version of this error.
    """
    engine = create_engine(url)

    @event.listens_for(engine, "connect")
    def _assume_role(dbapi_connection, _record):  # pragma: no cover - event hook
        cursor = dbapi_connection.cursor()
        cursor.execute(f"SET ROLE {RUNTIME_ROLE}")
        cursor.close()

    return engine


@pytest.fixture()
def tool_engine(committed_database: Engine, database_url: str, monkeypatch):
    """`build_engine` replaced by the test's own engine, and nothing else.

    `main()` is exercised for real — argument parsing, dispatch, printing, exit
    codes and the `except DBAPIError` clause. Only the engine is substituted, so
    that a test can choose which role connects. Configuration validation is
    covered separately above, against the documented environment rather than
    this one.
    """

    def _install(engine: Engine) -> None:
        monkeypatch.setattr(tool, "build_engine", lambda _environ: engine)

    return _install


def _rows(engine: Engine, sql: str, **parameters):
    with engine.connect() as connection:
        return connection.execute(text(sql), parameters).mappings().all()


ADMISSION_ROW = """
SELECT generation, state, correlation_id, closed_correlation_id
  FROM submission_admissions WHERE principal_id = :principal
"""

EVENTS = """
SELECT action, correlation_id, entity_id, payload
  FROM audit_events WHERE action = :action ORDER BY occurred_at
"""


@pytest.mark.database
def test_opening_writes_one_correlation_id_to_the_row_and_its_audit_event(
    committed_database: Engine,
):
    """**The correlation defect.** One transition, one identifier, both records.

    Before this, the row held a SQL-generated UUID and the event an unrelated
    one, so `correlation_id` could not be used to find the append-only event it
    names — which is the only thing the column is for.
    """
    engine = committed_database
    generation = tool.open_admission(
        engine,
        principal_id=PRINCIPAL,
        operator="A. Operator",
        reason="Initial generation for an automated test.",
    )

    row = _rows(engine, ADMISSION_ROW, principal=PRINCIPAL)[0]
    events = _rows(engine, EVENTS, action=ADMISSION_OPENED)

    assert generation == row["generation"] == 1
    assert row["state"] == "open"
    assert row["closed_correlation_id"] is None
    assert len(events) == 1
    assert events[0]["correlation_id"] == row["correlation_id"]
    assert events[0]["entity_id"] == PRINCIPAL
    assert events[0]["payload"]["admission_generation"] == generation


@pytest.mark.database
def test_closing_correlates_its_own_transition_and_leaves_the_opening_alone(
    committed_database: Engine,
):
    """The closure's identifier is its own, and the opening's is untouched."""
    engine = committed_database
    tool.open_admission(
        engine,
        principal_id=PRINCIPAL,
        operator="A. Operator",
        reason="Initial generation for an automated test.",
    )
    opened = _rows(engine, ADMISSION_ROW, principal=PRINCIPAL)[0]["correlation_id"]

    generation, changed = tool.close_admission(
        engine,
        principal_id=PRINCIPAL,
        operator="B. Operator",
        reason="Settling a synthetic episode.",
    )

    row = _rows(engine, ADMISSION_ROW, principal=PRINCIPAL)[0]
    closures = _rows(engine, EVENTS, action=ADMISSION_CLOSED)

    assert (generation, changed) == (1, True)
    assert row["state"] == "closed"
    assert row["correlation_id"] == opened, "the opening's correlation was rewritten"
    assert row["closed_correlation_id"] != opened
    assert len(closures) == 1
    assert closures[0]["correlation_id"] == row["closed_correlation_id"]
    assert closures[0]["payload"]["operator"] == "B. Operator"


@pytest.mark.database
def test_the_correlation_columns_join_to_exactly_one_event_each(
    committed_database: Engine,
):
    """The property stated as a join, which is how an operator would use it."""
    engine = committed_database
    tool.open_admission(
        engine,
        principal_id=PRINCIPAL,
        operator="A. Operator",
        reason="Initial generation for an automated test.",
    )
    tool.close_admission(
        engine,
        principal_id=PRINCIPAL,
        operator="A. Operator",
        reason="Settling a synthetic episode.",
    )

    joined = _rows(
        engine,
        """
        SELECT opened.action AS opened_action, closed.action AS closed_action
          FROM submission_admissions AS admission
          JOIN audit_events AS opened
            ON opened.correlation_id = admission.correlation_id
          JOIN audit_events AS closed
            ON closed.correlation_id = admission.closed_correlation_id
         WHERE admission.principal_id = :principal
        """,
        principal=PRINCIPAL,
    )

    assert len(joined) == 1
    assert joined[0]["opened_action"] == ADMISSION_OPENED
    assert joined[0]["closed_action"] == ADMISSION_CLOSED


@pytest.mark.database
def test_a_second_close_writes_no_second_event_and_no_second_correlation(
    committed_database: Engine,
):
    """Idempotent, and idempotent all the way into append-only history.

    A second closure is not an error — two operators settling one episode must
    reach the same state — but it is also not a transition, so it must not mint
    an identifier or write an event for one that did not happen.
    """
    engine = committed_database
    tool.open_admission(
        engine,
        principal_id=PRINCIPAL,
        operator="A. Operator",
        reason="Initial generation for an automated test.",
    )
    tool.close_admission(
        engine, principal_id=PRINCIPAL, operator="A. Operator", reason="First closure."
    )
    first = _rows(engine, ADMISSION_ROW, principal=PRINCIPAL)[0]

    generation, changed = tool.close_admission(
        engine, principal_id=PRINCIPAL, operator="C. Operator", reason="Second closure."
    )

    second = _rows(engine, ADMISSION_ROW, principal=PRINCIPAL)[0]
    assert (generation, changed) == (1, False)
    assert second["closed_correlation_id"] == first["closed_correlation_id"]
    assert len(_rows(engine, EVENTS, action=ADMISSION_CLOSED)) == 1


@pytest.mark.database
def test_a_lock_timeout_while_closing_exits_five_and_closes_nothing(
    committed_database: Engine, tool_engine, capsys
):
    """**The Unsettled outcome, against a real lock.**

    Another session holds the exclusive advisory lock the closure needs, so the
    closure waits and is cancelled by its own `lock_timeout`. That is a
    documented operator outcome, not a crash, and before this pass it escaped
    `AdmissionToolError` and reached the operator as a traceback.

    The `lock_timeout` is shortened for the test only — through a session
    setting on the blocked connection, not by changing the tool — so that a test
    does not wait 15 s to observe a wait.
    """
    engine = committed_database
    tool.open_admission(
        engine,
        principal_id=PRINCIPAL,
        operator="A. Operator",
        reason="Initial generation for an automated test.",
    )

    quick = create_engine(engine.url)

    @event.listens_for(quick, "connect")
    def _impatient(dbapi_connection, _record):  # pragma: no cover - event hook
        cursor = dbapi_connection.cursor()
        cursor.execute("SET lock_timeout = '250ms'")
        cursor.close()

    tool_engine(quick)

    blocker = create_engine(engine.url)
    try:
        with blocker.begin() as holding:
            holding.execute(
                text("SELECT pg_advisory_xact_lock(:key)"),
                {"key": ADMISSION_LOCK_KEY},
            )
            code = tool.main(
                [
                    "close",
                    "--principal",
                    PRINCIPAL,
                    "--operator",
                    "A. Operator",
                    "--reason",
                    "Settling a synthetic episode.",
                ]
            )
    finally:
        blocker.dispose()
        quick.dispose()

    captured = capsys.readouterr()
    assert code == tool.EXIT_LOCK_TIMEOUT
    assert "Unsettled" in captured.err
    assert "No generation was closed" in captured.err
    assert "safe to retry" in captured.err
    assert "Traceback" not in captured.err
    assert "SELECT" not in captured.err and "UPDATE" not in captured.err
    assert captured.out == ""

    # The decisive assertion: the fence is exactly as it was.
    row = _rows(engine, ADMISSION_ROW, principal=PRINCIPAL)[0]
    assert row["state"] == "open"
    assert row["closed_correlation_id"] is None
    assert _rows(engine, EVENTS, action=ADMISSION_CLOSED) == []


@pytest.mark.database
def test_a_connection_failure_exits_three_without_naming_the_target(
    committed_database: Engine, tool_engine, capsys
):
    """Nothing is read and nothing is written, and the message says so.

    The unreachable target is a socket directory that does not exist, which
    keeps this local and disposable: no port is dialled and no server is
    contacted.
    """
    unreachable = create_engine(
        "postgresql+psycopg:///freedom_test"
        "?host=/nonexistent/claude-c24-no-such-socket-dir"
    )
    tool_engine(unreachable)
    try:
        code = tool.main(["show"])
    finally:
        unreachable.dispose()

    captured = capsys.readouterr()
    assert code == tool.EXIT_CANNOT_CONNECT
    assert "Could not reach the database" in captured.err
    assert "Nothing was read" in captured.err
    assert "Traceback" not in captured.err
    assert "claude-c24-no-such-socket-dir" not in captured.err


@pytest.mark.database
@pytest.mark.parametrize("command", ["open", "close"])
def test_the_restricted_runtime_role_cannot_settle_and_exits_four(
    committed_database: Engine, tool_engine, capsys, command: str
):
    """The least-privilege control, met at the CLI instead of as a traceback.

    The runtime role holds `SELECT` on `submission_admissions` and nothing else —
    that asymmetry is what keeps the fence enforced rather than advisory — so an
    operator who reaches for the service's own `DATABASE_URL` is refused. The
    refusal has to say *why*, because the fix is to re-run as the schema owner.
    """
    engine = committed_database
    with engine.begin() as owner:
        exists = owner.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :role"), {"role": RUNTIME_ROLE}
        ).scalar()
        if not exists:
            pytest.skip(f"{RUNTIME_ROLE} does not exist on this cluster")
        # The real deployment artifact, rendered for the test role — not a
        # hand-written GRANT pair. The schema fixture migrates from empty and
        # drops each table's ACL with it, so the privileges have to be
        # (re)established here, and applying the template is what makes this
        # evidence about what is deployed.
        for statement in grant_statements():
            owner.execute(text(statement))
    tool.open_admission(
        engine,
        principal_id=PRINCIPAL,
        operator="A. Operator",
        reason="Initial generation for an automated test.",
    )

    restricted = _engine_as_runtime_role(str(engine.url))
    tool_engine(restricted)
    try:
        code = tool.main(
            [
                command,
                "--principal",
                RECOVERY_PRINCIPAL if command == "open" else PRINCIPAL,
                "--operator",
                "A. Operator",
                "--reason",
                "An attempt from the wrong role.",
            ]
        )
    finally:
        restricted.dispose()

    captured = capsys.readouterr()
    assert code == tool.EXIT_INSUFFICIENT_PRIVILEGE
    assert "privilege" in captured.err
    assert "owns" in captured.err
    assert "Traceback" not in captured.err
    assert captured.out == ""

    row = _rows(engine, ADMISSION_ROW, principal=PRINCIPAL)[0]
    assert row["state"] == "open", "the fence changed under a refused command"
    assert _rows(engine, EVENTS, action=ADMISSION_CLOSED) == []


@pytest.mark.database
def test_a_successful_close_still_exits_zero_and_says_so(
    committed_database: Engine, tool_engine, capsys
):
    """The control for every failure test above: success is still success."""
    engine = committed_database
    tool_engine(engine)
    tool.open_admission(
        engine,
        principal_id=PRINCIPAL,
        operator="A. Operator",
        reason="Initial generation for an automated test.",
    )

    code = tool.main(
        [
            "close",
            "--principal",
            PRINCIPAL,
            "--operator",
            "A. Operator",
            "--reason",
            "Settling a synthetic episode.",
        ]
    )

    captured = capsys.readouterr()
    assert code == tool.EXIT_OK
    assert "Closed generation 1" in captured.out
    assert captured.err == ""


# =============================================================================
# 3b. The four injection points of the commit-ambiguity model
# =============================================================================


def _lost_connection() -> DBAPIError:
    """What a lost connection looks like from here: **no SQLSTATE at all**.

    The statement and parameters are carried exactly as SQLAlchemy carries them,
    so that a message built out of the exception would leak SQL. These tests
    assert none is.
    """
    return DBAPIError(
        statement="COMMIT",
        params={"id": "6f1c0e4e-0000-0000-0000-000000000000"},
        orig=_FakeDriverError(None),
        connection_invalidated=True,
    )


class _FailingConnection:
    """Runs every statement for real until the Nth, which loses the connection."""

    def __init__(self, wrapped, at_statement: int) -> None:
        self._wrapped = wrapped
        self._at_statement = at_statement
        self._seen = 0

    def __getattr__(self, name):
        return getattr(self._wrapped, name)

    def execute(self, *args, **kwargs):
        self._seen += 1
        if self._seen == self._at_statement:
            raise _lost_connection()
        return self._wrapped.execute(*args, **kwargs)


class _FailsAtPhase:
    """An engine whose transaction fails at one named phase, with no SQLSTATE.

    A **narrow double at the transaction boundary**, and it is worth stating
    exactly what each phase models, because a double is not evidence about
    PostgreSQL's internals and nothing here is offered as such:

    `connect` — the connection is never established, so no transaction begins.
    In reality nothing was written, and the tool may say so.

    `statement` — the connection is lost partway through the transaction, before
    any `COMMIT` is sent. In reality nothing committed; the tool reports the
    outcome as unknown regardless, which is the conservative direction this
    correction chose deliberately, and the test below proves the database is in
    fact untouched.

    `acknowledgement` — **the transaction commits for real, against the real
    database**, and the error is raised in place of the acknowledgement the
    client never hears. Nothing else models the case the correction exists for:
    the server committed and the client holds only an error. What is simulated
    is the loss of the *reply*, not any behaviour of PostgreSQL.
    """

    def __init__(self, engine: Engine, phase: str, *, at_statement: int = 0) -> None:
        self._engine = engine
        self._phase = phase
        self._at_statement = at_statement

    @property
    def url(self):
        return self._engine.url

    def connect(self):
        return self._engine.connect()

    def dispose(self) -> None:  # the tool disposes in its `finally`
        return None

    def begin(self) -> "_FailingTransaction":
        return _FailingTransaction(self._engine, self._phase, self._at_statement)


class _FailingTransaction:
    def __init__(self, engine: Engine, phase: str, at_statement: int) -> None:
        self._engine = engine
        self._phase = phase
        self._at_statement = at_statement
        self._context = None

    def __enter__(self):
        if self._phase == "connect":
            raise _lost_connection()
        self._context = self._engine.begin()
        connection = self._context.__enter__()
        if self._phase == "statement":
            return _FailingConnection(connection, self._at_statement)
        return connection

    def __exit__(self, exc_type, exc, traceback_):
        suppressed = self._context.__exit__(exc_type, exc, traceback_)
        if self._phase == "acknowledgement" and exc_type is None:
            # The commit above has already happened. This is the reply going
            # missing, which is the whole of what the client can observe.
            raise _lost_connection()
        return suppressed


def _close(argv_reason: str = "Settling a synthetic episode.") -> int:
    return tool.main(
        [
            "close",
            "--principal",
            PRINCIPAL,
            "--operator",
            "A. Operator",
            "--reason",
            argv_reason,
        ]
    )


@pytest.mark.database
def test_a_failure_before_the_transaction_may_still_say_nothing_was_closed(
    committed_database: Engine, tool_engine, capsys
):
    """Injection point 1, through the **real driver**: no connection, no doubt.

    The unreachable target is a socket directory that does not exist, so no port
    is dialled and no server is contacted. Nothing was established, so the sound
    claim is available and the tool makes it.
    """
    engine = committed_database
    tool.open_admission(
        engine,
        principal_id=PRINCIPAL,
        operator="A. Operator",
        reason="Initial generation for an automated test.",
    )
    unreachable = create_engine(
        "postgresql+psycopg:///freedom_test"
        "?host=/nonexistent/claude-c24-no-such-socket-dir"
    )
    tool_engine(unreachable)
    try:
        code = _close()
    finally:
        unreachable.dispose()

    captured = capsys.readouterr()
    assert code == tool.EXIT_CANNOT_CONNECT
    assert "No generation was closed and the fence is unchanged" in captured.err
    assert "Outcome unknown" not in captured.err
    assert "Traceback" not in captured.err

    row = _rows(engine, ADMISSION_ROW, principal=PRINCIPAL)[0]
    assert row["state"] == "open"


@pytest.mark.database
def test_a_failure_during_the_closure_is_reported_as_an_unknown_outcome(
    committed_database: Engine, tool_engine, capsys
):
    """Injection point 2: lost mid-transaction, before any `COMMIT` was sent.

    Nothing committed — the last assertions read the database and show it — and
    the tool still declines to say so. That is the conservative choice stated in
    the tool's docstring, and this test is where its cost is visible: one `show`
    for an operator, against a false assurance that could authorize a duplicate
    export.
    """
    engine = committed_database
    tool.open_admission(
        engine,
        principal_id=PRINCIPAL,
        operator="A. Operator",
        reason="Initial generation for an automated test.",
    )
    # Statement 4 of `close_admission`: SET LOCAL, advisory lock, SELECT … FOR
    # UPDATE, then the UPDATE itself.
    tool_engine(_FailsAtPhase(engine, "statement", at_statement=4))

    code = _close()

    captured = capsys.readouterr()
    assert code == tool.EXIT_OUTCOME_UNKNOWN
    assert "Outcome unknown" in captured.err
    assert "Unsettled" in captured.err
    assert "No generation was closed" not in captured.err
    assert "fence is unchanged" not in captured.err
    assert "Traceback" not in captured.err
    assert "COMMIT" not in captured.err and "6f1c0e4e" not in captured.err
    assert captured.out == ""

    # The truth the operator learns by verifying, and which the tool did not
    # presume to tell them.
    row = _rows(engine, ADMISSION_ROW, principal=PRINCIPAL)[0]
    assert row["state"] == "open"
    assert _rows(engine, EVENTS, action=ADMISSION_CLOSED) == []


@pytest.mark.database
def test_a_lost_commit_acknowledgement_never_claims_the_fence_is_unchanged(
    committed_database: Engine, tool_engine, capsys
):
    """**Injection point 3, and the decisive one.** The server committed.

    The closure really commits against the real database; only the reply is
    lost. Before this correction the tool printed "No generation was closed and
    the fence is unchanged" over a database in which the generation *was*
    closed — a false assertion about durable state, at the moment an operator is
    deciding whether to authorize a fresh export.
    """
    engine = committed_database
    tool.open_admission(
        engine,
        principal_id=PRINCIPAL,
        operator="A. Operator",
        reason="Initial generation for an automated test.",
    )
    tool_engine(_FailsAtPhase(engine, "acknowledgement"))

    code = _close()

    captured = capsys.readouterr()
    assert code == tool.EXIT_OUTCOME_UNKNOWN
    assert "Outcome unknown" in captured.err
    assert "Unsettled" in captured.err
    assert "`show`" in captured.err
    assert "No generation was closed" not in captured.err
    assert "fence is unchanged" not in captured.err
    assert "did not commit" not in captured.err
    assert "Traceback" not in captured.err
    assert "COMMIT" not in captured.err and "6f1c0e4e" not in captured.err
    # It also does not claim the opposite. Success is a thing the tool prints on
    # exit 0, and this run heard nothing.
    assert captured.out == ""
    assert "Closed generation" not in captured.err

    # And the state the old message denied: it committed.
    row = _rows(engine, ADMISSION_ROW, principal=PRINCIPAL)[0]
    assert row["state"] == "closed"


@pytest.mark.database
def test_verification_after_an_unknown_outcome_finds_the_closure_and_its_evidence(
    committed_database: Engine, tool_engine, capsys
):
    """Injection point 4: the operator does what the message told them to.

    A genuinely committed close whose acknowledgement was lost, then `show`,
    then the correlation join, then the repeat the message says is safe once
    verified. This is the whole recovery path, end to end, and it is the reason
    the ambiguous message is worth more than a wrong certainty.
    """
    engine = committed_database
    tool.open_admission(
        engine,
        principal_id=PRINCIPAL,
        operator="A. Operator",
        reason="Initial generation for an automated test.",
    )
    tool_engine(_FailsAtPhase(engine, "acknowledgement"))
    assert _close() == tool.EXIT_OUTCOME_UNKNOWN
    capsys.readouterr()

    # 1. Reconnect and run `show`.
    tool_engine(engine)
    assert tool.main(["show"]) == tool.EXIT_OK
    listing = capsys.readouterr().out
    assert "closed" in listing
    assert PRINCIPAL in listing

    # 2. Confirm the transition against its append-only event, through the
    #    correlation column the message names.
    joined = _rows(
        engine,
        """
        SELECT event.action, event.payload
          FROM submission_admissions AS admission
          JOIN audit_events AS event
            ON event.correlation_id = admission.closed_correlation_id
         WHERE admission.principal_id = :principal
        """,
        principal=PRINCIPAL,
    )
    assert len(joined) == 1
    assert joined[0]["action"] == ADMISSION_CLOSED
    assert joined[0]["payload"]["operator"] == "A. Operator"

    # 3. The repeat the message calls safe: idempotent, and it writes no second
    #    event for a transition that already happened.
    assert _close() == tool.EXIT_OK
    repeated = capsys.readouterr().out
    assert "already closed" in repeated
    assert len(_rows(engine, EVENTS, action=ADMISSION_CLOSED)) == 1


@pytest.mark.database
def test_the_reserved_pre_fence_principal_is_refused_before_the_database(
    committed_database: Engine, tool_engine, capsys
):
    """Exit 1: refused by the tool, with nothing written."""
    engine = committed_database
    tool_engine(engine)

    code = tool.main(
        [
            "close",
            "--principal",
            PRE_FENCE_PRINCIPAL,
            "--operator",
            "A. Operator",
            "--reason",
            "An attempt to manage generation 0.",
        ]
    )

    captured = capsys.readouterr()
    assert code == tool.EXIT_REFUSED
    assert "reserved" in captured.err
    assert "Traceback" not in captured.err
