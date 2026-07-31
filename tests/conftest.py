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

import pytest
from sqlalchemy import Engine, create_engine, text

from adapters.database.config import EXPECTED_DATABASES
from adapters.database.metadata import metadata
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
