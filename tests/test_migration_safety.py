"""What Alembic proves about its target before it runs a migration.

Codex Phase 1 re-review finding: `migrations/env.py` validated the *URL* and then
connected, without ever asking the resulting connection where it had landed. A
URL is not a connection — a `localhost` remapped in `/etc/hosts`, a port-forward,
a pooler, or a multi-host failover target can put the migration on a server the
URL never named.

Codex Phase 1 second re-review finding: the live check then *accepted* a loopback
TCP connection and the comments claimed that catches SSH port forwarding. It does
not. `ssh -L 5432:localhost:5432 elsewhere` puts a remote PostgreSQL server on
this host's `127.0.0.1:5432`, and that server answers `inet_server_addr()` and
`inet_client_addr()` with loopback exactly as a local one would. Online
migrations therefore require the Unix-domain socket, statically and live.

`migrations/env.py` now runs `verify_connected_unix_socket_target` on the
established connection, before `context.run_migrations()`. These tests drive
Alembic through its own command API, in-process, so what is exercised is the real
`env.py` and not a re-implementation of it.

The online tests make the live check *lie* by substituting the query it sends to
the server. That is the only way to produce a wrong-database or non-socket answer
without actually connecting somewhere unsafe, and it proves the thing that
matters: `env.py` asks the question and refuses the answer.

Offline (`--sql`) mode cannot perform the live check at all, because it never
connects. Its tests below pin down what it does instead: the full static
validation, plus a warning carried in the generated script.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import sqlalchemy
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from adapters.database import safety
from adapters.database.safety import UnsafeDatabaseTargetError

ROOT = Path(__file__).resolve().parents[1]

#: A socket directory that does not exist. It satisfies the static checks — an
#: absolute socket path — and no connection through it can succeed, so offline
#: mode producing a complete script with this configured is what proves it never
#: opened a connection.
UNREACHABLE_LOCAL_URL = (
    "postgresql+psycopg://app@/freedom_test?host=/nonexistent/freedom-socket"
)

#: Substituted for `CONNECTED_TARGET_QUERY`: a real query against the real test
#: database that returns the answer a *misdirected* connection would give.
LANDED_IN_ANOTHER_DATABASE = """
SELECT 'freedom_production' AS database_name,
       true AS unix_socket,
       '' AS server_address,
       '' AS client_address
"""

LANDED_ON_A_REMOTE_SERVER = """
SELECT 'freedom_test' AS database_name,
       false AS unix_socket,
       '10.0.0.5' AS server_address,
       '10.0.0.9' AS client_address
"""

#: The answer a forwarded port produces: the expected database, loopback at both
#: ends, and a server that may be on another machine entirely.
LANDED_ON_TCP_LOOPBACK = """
SELECT 'freedom_test' AS database_name,
       false AS unix_socket,
       '127.0.0.1' AS server_address,
       '127.0.0.1' AS client_address
"""

#: The URL form the finding named: statically loopback, and refused before
#: Alembic opens any connection at all.
TCP_LOOPBACK_URL = "postgresql+psycopg://user@127.0.0.1/freedom_test"


@pytest.fixture()
def alembic_config() -> Config:
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "migrations"))
    return config


def table_names(engine) -> set[str]:
    return set(inspect(engine).get_table_names())


# --------------------------------------------------------------------------
# The URL is refused before Alembic connects at all
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("command_name", "keywords"),
    [("upgrade", {}), ("downgrade", {}), ("upgrade", {"sql": True})],
)
def test_alembic_refuses_a_tcp_loopback_url(
    monkeypatch, capsys, alembic_config, command_name, keywords
):
    """`postgresql+psycopg://user@127.0.0.1/freedom_test` never reaches a server.

    Statically loopback is statically TCP, and a TCP target cannot be shown to be
    the PostgreSQL server on this host. The refusal happens in
    `database_settings()`, before `engine_from_config`, so no connection is
    attempted online and no script is emitted offline.
    """
    monkeypatch.setenv("DATABASE_URL", TCP_LOOPBACK_URL)
    monkeypatch.setenv("APP_ENVIRONMENT", "test")
    revision = "base" if command_name == "downgrade" else "head"

    with pytest.raises(ValueError, match="Unix-domain socket"):
        getattr(command, command_name)(alembic_config, revision, **keywords)

    assert "CREATE TABLE" not in capsys.readouterr().out


def test_alembic_refuses_a_loopback_host_inherited_from_libpq(
    monkeypatch, alembic_config
):
    """The documented socket URL is only a socket while PGHOST leaves it alone."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg:///freedom_test")
    monkeypatch.setenv("APP_ENVIRONMENT", "test")
    monkeypatch.setenv("PGHOST", "127.0.0.1")

    with pytest.raises(ValueError, match="Unix-domain socket"):
        command.upgrade(alembic_config, "head")


# --------------------------------------------------------------------------
# Codex Phase 1 third re-review finding: an inherited PGHOSTADDR
#
# `PGHOSTADDR` is the default for libpq's `hostaddr`, and `hostaddr` outranks
# `host`. So the documented socket URL, with PGHOSTADDR set, is a TCP connection
# to that address — and a remote one would receive the migration role's
# credentials. The live check in `env.py` cannot help: it runs after `connect()`,
# by which point the credentials have already been offered. Both modes therefore
# have to refuse *before* an engine exists.
# --------------------------------------------------------------------------

#: The two documented socket spellings, which PGHOSTADDR silently converts to
#: TCP.
SOCKET_URLS = [
    "postgresql+psycopg:///freedom_test",
    "postgresql+psycopg://app@/freedom_test?host=/var/run/postgresql",
]


def forbid_engine_creation(*arguments, **keywords):
    raise AssertionError(
        "migrations/env.py created an engine for a target it had not proven safe"
    )


@pytest.mark.parametrize("address", ["127.0.0.1", "::1", "203.0.113.9"])
@pytest.mark.parametrize("url", SOCKET_URLS)
@pytest.mark.parametrize("command_name", ["upgrade", "downgrade"])
def test_online_alembic_refuses_an_inherited_host_address_before_connecting(
    monkeypatch, alembic_config, url, address, command_name
):
    """No engine, therefore no connection, therefore no credential leaves this host.

    `engine_from_config` is replaced with a function that fails the test if it is
    ever reached. `migrations/env.py` imports it when Alembic execs the module,
    so this substitution is the real one the migration would have used.
    """
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("APP_ENVIRONMENT", "test")
    monkeypatch.setenv("PGHOSTADDR", address)
    monkeypatch.setattr(sqlalchemy, "engine_from_config", forbid_engine_creation)
    revision = "base" if command_name == "downgrade" else "head"

    with pytest.raises(ValueError, match="Unix-domain socket"):
        getattr(command, command_name)(alembic_config, revision)


@pytest.mark.parametrize("address", ["127.0.0.1", "203.0.113.9"])
@pytest.mark.parametrize("url", SOCKET_URLS)
def test_offline_alembic_emits_no_script_for_an_inherited_host_address(
    monkeypatch, capsys, alembic_config, url, address
):
    """Offline mode cannot check a connection, so the static check is all it has.

    Nothing is emitted — not the migration, and not even the warning banner,
    because the target is resolved before anything is printed.
    """
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("APP_ENVIRONMENT", "test")
    monkeypatch.setenv("PGHOSTADDR", address)

    with pytest.raises(ValueError, match="Unix-domain socket"):
        command.upgrade(alembic_config, "head", sql=True)

    emitted = capsys.readouterr().out
    assert "CREATE TABLE" not in emitted, "no DDL may be emitted"
    assert "ALTER TABLE" not in emitted
    assert "alembic_version" not in emitted
    assert "Generated by Alembic" not in emitted, "not even the banner"


def test_a_refused_host_address_migration_does_not_echo_the_password(
    monkeypatch, capsys, alembic_config
):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://migration_role:hunter2@/freedom_test"
        "?host=/var/run/postgresql",
    )
    monkeypatch.setenv("APP_ENVIRONMENT", "test")
    monkeypatch.setenv("PGHOSTADDR", "203.0.113.9")

    with pytest.raises(ValueError) as raised:
        command.upgrade(alembic_config, "head", sql=True)

    captured = capsys.readouterr()
    for output in (str(raised.value), captured.out, captured.err):
        assert "hunter2" not in output
        assert "migration_role" not in output


# --------------------------------------------------------------------------
# Online: the live check, on the connection the migration would use
# --------------------------------------------------------------------------


@pytest.mark.database
def test_online_migrations_refuse_a_connection_that_landed_in_another_database(
    monkeypatch, alembic_config, database_url, migrated_database
):
    """`downgrade base` drops every table. It must not reach the wrong database."""
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("APP_ENVIRONMENT", "test")
    monkeypatch.setattr(safety, "CONNECTED_TARGET_QUERY", LANDED_IN_ANOTHER_DATABASE)

    before = table_names(migrated_database)
    assert "characters" in before, "the fixture should have migrated to head"

    with pytest.raises(UnsafeDatabaseTargetError, match="not the expected"):
        command.downgrade(alembic_config, "base")

    assert table_names(migrated_database) == before, "the downgrade must not have run"


@pytest.mark.database
def test_online_migrations_refuse_a_connection_that_is_not_local(
    monkeypatch, alembic_config, database_url, migrated_database
):
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("APP_ENVIRONMENT", "test")
    monkeypatch.setattr(safety, "CONNECTED_TARGET_QUERY", LANDED_ON_A_REMOTE_SERVER)

    before = table_names(migrated_database)

    with pytest.raises(UnsafeDatabaseTargetError, match="Unix-domain socket"):
        command.downgrade(alembic_config, "base")

    assert table_names(migrated_database) == before


@pytest.mark.database
def test_online_migrations_refuse_a_live_loopback_connection(
    monkeypatch, alembic_config, database_url, migrated_database
):
    """The finding, at the live layer: expected database, loopback both ends.

    A forwarded port answers exactly this, so the migration is refused and every
    table survives.
    """
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("APP_ENVIRONMENT", "test")
    monkeypatch.setattr(safety, "CONNECTED_TARGET_QUERY", LANDED_ON_TCP_LOOPBACK)

    before = table_names(migrated_database)
    assert "characters" in before, "the fixture should have migrated to head"

    with pytest.raises(UnsafeDatabaseTargetError, match="Unix-domain socket"):
        command.downgrade(alembic_config, "base")

    assert table_names(migrated_database) == before, "the downgrade must not have run"


@pytest.mark.database
def test_online_migrations_run_against_a_verified_local_target(
    monkeypatch, alembic_config, database_url, migrated_database
):
    """The positive control: a real socket connection to `freedom_test` is accepted.

    The documented development configuration is a Unix-domain socket, and the
    server's own answer has to satisfy the live check, or nothing below runs.

    It also asserts the migrations *commit*. The live check runs a query on the
    migration's own connection, which implicitly begins a transaction; if that
    read is left open, Alembic nests inside it and the DDL is discarded when the
    connection closes. A guard that silently turns every migration into a no-op
    would otherwise look exactly like a working one.
    """
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("APP_ENVIRONMENT", "test")

    command.downgrade(alembic_config, "base")
    assert "characters" not in table_names(migrated_database)

    command.upgrade(alembic_config, "head")
    assert "characters" in table_names(migrated_database)


@pytest.mark.database
def test_the_live_check_accepts_this_hosts_real_connection(migrated_database):
    """The unfaked query, against the real connection, answers 'Unix socket'.

    The fake-connection tests in `test_database_safety.py` cover the accepted and
    refused answers in isolation. This one confirms the real server really does
    report null addresses over the documented socket configuration, so the guard
    is not passing only because the fakes agree with it.
    """
    with migrated_database.connect() as connection:
        safety.verify_connected_unix_socket_target(
            connection, expected_database="freedom_test"
        )

        row = connection.exec_driver_sql(safety.CONNECTED_TARGET_QUERY).one()

    database_name, unix_socket, server_address, client_address = row
    assert database_name == "freedom_test"
    assert unix_socket, "the destructive fixtures require a Unix-domain socket"
    assert (server_address, client_address) == ("", "")


# --------------------------------------------------------------------------
# Offline (--sql): no connection exists, so no live check is possible
# --------------------------------------------------------------------------


def test_offline_migrations_never_connect_and_say_so(monkeypatch, capsys, alembic_config):
    """A complete script is produced with nothing listening on the configured port.

    That is the proof that offline mode does not connect — and therefore the
    reason it cannot verify its target. The limitation travels with the script
    rather than living only in a document.
    """
    monkeypatch.setenv("DATABASE_URL", UNREACHABLE_LOCAL_URL)
    monkeypatch.setenv("APP_ENVIRONMENT", "test")

    command.upgrade(alembic_config, "head", sql=True)

    script = capsys.readouterr().out

    assert script.lstrip().startswith("--"), "the warning must be valid SQL comments"
    assert "offline" in script.lower()
    assert "NOTHING HERE PROVES WHICH SERVER OR DATABASE" in script
    assert "current_database()" in script, "the operator is told how to check"
    assert "Both addresses must be NULL" in script, "and what a safe answer is"
    assert "Loopback addresses are NOT sufficient" in script, "and what is not one"
    assert "CREATE TABLE characters" in script, "the script itself is still complete"


@pytest.mark.parametrize(
    ("url", "environment", "message"),
    [
        # The reported finding, in the mode that cannot check a connection.
        (
            "postgresql+psycopg://app@/freedom_test?host=127.0.0.1&host=db.example.org",
            "test",
            "failover",
        ),
        (
            "postgresql+psycopg://app@/freedom_test?host=127.0.0.1,db.example.org",
            "test",
            "failover",
        ),
        (
            "postgresql+psycopg://127.0.0.1/freedom_test?host=db.example.org",
            "test",
            "more than one",
        ),
        (
            "postgresql+psycopg:///freedom_test?dbname=freedom_production",
            "test",
            "more than one",
        ),
        # Static checks that offline mode shares with online mode.
        (
            "postgresql+psycopg://app@db.example.org/freedom_test",
            "test",
            "Unix-domain socket",
        ),
        (
            "postgresql+psycopg://user@127.0.0.1/freedom_test",
            "test",
            "Unix-domain socket",
        ),
        (
            "postgresql+psycopg:///freedom_production",
            "development",
            "must use database 'freedom_dev'",
        ),
    ],
)
def test_offline_migrations_refuse_a_target_they_cannot_verify(
    monkeypatch, capsys, alembic_config, url, environment, message
):
    """Offline mode cannot check a connection, so the static checks are all it has.

    They are the same ones online mode runs, and they are what make offline mode
    safe to *generate*: an unverifiable target never produces a script at all.
    """
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("APP_ENVIRONMENT", environment)

    with pytest.raises(ValueError, match=message):
        command.upgrade(alembic_config, "head", sql=True)

    assert "CREATE TABLE" not in capsys.readouterr().out


def test_a_refused_migration_does_not_echo_the_password(
    monkeypatch, capsys, alembic_config
):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://app:hunter2@/freedom_test?host=127.0.0.1&host=db.example.org",
    )
    monkeypatch.setenv("APP_ENVIRONMENT", "test")

    with pytest.raises(ValueError) as raised:
        command.upgrade(alembic_config, "head", sql=True)

    captured = capsys.readouterr()
    assert "hunter2" not in str(raised.value)
    assert "hunter2" not in captured.out
    assert "hunter2" not in captured.err


def test_a_missing_database_url_is_refused(monkeypatch, alembic_config):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("APP_ENVIRONMENT", "test")

    with pytest.raises(RuntimeError, match="DATABASE_URL is required"):
        command.upgrade(alembic_config, "head", sql=True)
