"""Shared PostgreSQL fixtures.

These fixtures run `alembic downgrade base`, which drops every table, so they
refuse to run against anything but the disposable test database named in
`docs/operations/database-development.md`.

The refusal is deliberately two-layered, because neither layer is sufficient
alone:

1. **Static** — `adapters.database.safety.assert_disposable_target` resolves
   `TEST_DATABASE_URL` *and the ambient libpq environment* into a normalised
   `ConnectionIdentity`, then compares that identity against `DATABASE_URL`.
   Comparing URLs as strings is not enough: `postgresql:///freedom_test` and
   `postgresql+psycopg:///freedom_test` are the same database. Under the default
   `UNIX_SOCKET_ONLY` policy it also refuses a TCP URL, loopback included — and
   a URL is TCP whenever `PGHOSTADDR` is set, because libpq dials `hostaddr` and
   keeps `host` only for authentication. `?host=/var/run/postgresql` beside an
   inherited `PGHOSTADDR` is therefore refused, not accepted as a socket.
2. **Runtime** — `verify_connected_unix_socket_target` asks the server which
   database the connection actually landed in, and requires the connection to be
   a Unix-domain socket, *before* the first destructive command. That catches
   what no amount of string parsing can: a remapped `localhost` or an inherited
   `PGHOST`. It cannot replace layer 1, because by the time a connection exists
   the credentials have already been offered to whatever server answered.

**Why the socket, and not merely loopback.** `ssh -L 5432:localhost:5432` binds
`127.0.0.1:5432` on this host and carries the session to a PostgreSQL server
elsewhere. That server reports loopback for both `inet_server_addr()` and
`inet_client_addr()`, because from its point of view the connection arrives from
sshd on its own loopback interface. So a loopback address proves nothing about
where the server is, and these fixtures run `alembic downgrade base`. A
Unix-domain socket is a file on this machine, which a TCP tunnel cannot present.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import Engine, create_engine, text

from adapters.database.config import EXPECTED_DATABASES
from adapters.database.metadata import metadata
from application.admissions import ADMISSION_LOCK_KEY
from adapters.database.safety import (
    ConnectionPolicy,
    UnsafeDatabaseTargetError,
    assert_disposable_target,
    verify_connected_unix_socket_target,
)
from adapters.database import tables  # noqa: F401 - registers tables on metadata

ROOT = Path(__file__).resolve().parents[1]
TEST_ENVIRONMENT = "test"
TEST_URL_VARIABLE = "TEST_DATABASE_URL"
EXPECTED_TEST_DATABASE = EXPECTED_DATABASES[TEST_ENVIRONMENT]

#: Passed to Alembic unchanged, minus anything that could redirect the child to
#: a target the parent did not validate.
UNSAFE_CHILD_VARIABLES = ("PGSERVICE", "PGSERVICEFILE", "PGOPTIONS")


def resolve_test_database_url() -> str:
    """Return the disposable test database URL, or refuse to continue.

    A URL that is not the local disposable test database **fails** the run
    rather than skipping it: a skip would let a misconfigured suite look green
    while the guard was the only thing that stopped it destroying a database.

    `TEST_DATABASE_URL` must name the Unix-domain socket — `postgresql+psycopg:
    ///freedom_test`, or an explicit `?host=/var/run/postgresql`. A loopback TCP
    URL is refused, not because loopback is remote, but because nothing here can
    tell it apart from a forwarded port.
    """
    url = os.environ.get(TEST_URL_VARIABLE)
    if not url:
        pytest.skip(
            f"{TEST_URL_VARIABLE} is not configured for a disposable PostgreSQL database."
        )
    try:
        assert_disposable_target(
            url,
            expected_database=EXPECTED_TEST_DATABASE,
            runtime_url=os.environ.get("DATABASE_URL"),
            variable=TEST_URL_VARIABLE,
            policy=ConnectionPolicy.UNIX_SOCKET_ONLY,
        )
    except UnsafeDatabaseTargetError as error:
        pytest.fail(f"Refusing to run destructive database tests: {error}")
    return url


def run_alembic(url: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    """Run Alembic in a subprocess against `url`, as a deployment would.

    The child inherits the parent's environment so it resolves the same target
    the parent validated, except for the libpq variables that could point it
    somewhere else.
    """
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in UNSAFE_CHILD_VARIABLES
    }
    environment["DATABASE_URL"] = url
    environment["APP_ENVIRONMENT"] = TEST_ENVIRONMENT
    return subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope="session")
def database_url() -> str:
    return resolve_test_database_url()


@pytest.fixture(scope="session")
def migrated_database(database_url: str) -> Engine:
    """A PostgreSQL database migrated from empty to head, exactly as deployed."""
    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            verify_connected_unix_socket_target(
                connection, expected_database=EXPECTED_TEST_DATABASE
            )
    except UnsafeDatabaseTargetError as error:
        engine.dispose()
        pytest.fail(f"Refusing to run destructive database tests: {error}")

    run_alembic(database_url, "downgrade", "base")
    run_alembic(database_url, "upgrade", "head")
    yield engine
    engine.dispose()


@pytest.fixture()
def db_connection(migrated_database: Engine):
    """A connection whose transaction is always rolled back.

    Tests are therefore order-independent and leave no rows behind.
    """
    connection = migrated_database.connect()
    transaction = connection.begin()
    try:
        yield connection
    finally:
        transaction.rollback()
        connection.close()


@pytest.fixture()
def committed_database(migrated_database: Engine) -> Engine:
    """For tests that must commit for real; every table is emptied afterwards."""
    yield migrated_database
    table_list = ", ".join(sorted(metadata.tables))
    with migrated_database.begin() as connection:
        connection.execute(text(f"TRUNCATE TABLE {table_list} RESTART IDENTITY CASCADE"))


def open_admission(
    engine: Engine, principal_id: str, *, generation: int = 1, state: str = "open"
) -> UUID:
    """Insert an admission generation for `principal_id`. Returns its id.

    The PostgreSQL counterpart of `tests.fakes.admit`, and required by every
    database-backed test that expects a submission to succeed: migration 0005
    makes an acceptance impossible without one. Written directly rather than
    through `tools.submission_admission` so a test can also create the states an
    operator cannot — a generation that is closed from the start, for instance —
    which is what the fence's negative cases need.
    """
    admission_id = uuid4()
    closed = state == "closed"
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO submission_admissions (
                    id, generation, principal_id, state,
                    opened_by, open_reason, correlation_id,
                    closed_at, closed_by, close_reason, closed_correlation_id
                ) VALUES (
                    :id, :generation, :principal, :state,
                    'tests', 'Synthetic admission for an automated test.',
                    gen_random_uuid(),
                    CASE WHEN :closed THEN now() END,
                    CASE WHEN :closed THEN 'tests' END,
                    CASE WHEN :closed THEN 'Closed by the test that created it.' END,
                    CASE WHEN :closed THEN gen_random_uuid() END
                )
                """
            ),
            {
                "id": admission_id,
                "generation": generation,
                "principal": principal_id,
                "state": state,
                "closed": closed,
            },
        )
    return admission_id


def close_admission(engine: Engine, principal_id: str) -> None:
    """Close a generation the way `tools.submission_admission close` does.

    **`FOR UPDATE` before the `UPDATE`, and that is not a style choice.** A plain
    update of a non-key column takes `FOR NO KEY UPDATE`, which does not conflict
    with the `KEY SHARE` lock an acceptance's foreign key holds — so a closure
    written without this line would pass straight through a submission that was
    already waiting. Measured on this host; see
    `tests/test_submission_admission_postgresql.py`.
    """
    with engine.begin() as connection:
        # The exclusive advisory lock first, then `FOR UPDATE`, in that order —
        # the same pair, in the same order, that `tools.submission_admission`
        # takes. A helper that took only one of them would let a test pass
        # against a fence the real closure does not have.
        connection.execute(
            text("SELECT pg_advisory_xact_lock(:key)"), {"key": ADMISSION_LOCK_KEY}
        )
        connection.execute(
            text(
                "SELECT id FROM submission_admissions "
                "WHERE principal_id = :principal FOR UPDATE"
            ),
            {"principal": principal_id},
        )
        connection.execute(
            text(
                """
                UPDATE submission_admissions
                SET state = 'closed', closed_at = now(), closed_by = 'tests',
                    close_reason = 'Settlement, in a test.',
                    closed_correlation_id = gen_random_uuid()
                WHERE principal_id = :principal AND state = 'open'
                """
            ),
            {"principal": principal_id},
        )
