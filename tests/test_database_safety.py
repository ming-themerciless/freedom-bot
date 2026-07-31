"""The safety boundary that stands between `pytest` and a destroyed database.

Codex Phase 1 finding 1: comparing `TEST_DATABASE_URL` and `DATABASE_URL` as raw
strings lets two textually different but equivalent URLs name the same database,
after which the suite runs `alembic downgrade base`.

Codex Phase 1 second re-review finding: the guard then accepted any *loopback*
target, statically and live, and claimed that inspecting `inet_server_addr()`
and `inet_client_addr()` caught SSH port forwarding. It does not.
`ssh -L 5432:localhost:5432 elsewhere` puts a remote PostgreSQL server on
`127.0.0.1:5432` here, and that server reports loopback at both ends exactly as
a local one does. Destructive targets therefore require a Unix-domain socket —
a file on this host, which no TCP tunnel can present.

These tests are deliberately free of any database connection so they run in the
non-database suite, where a broken guard is found before anything can act on it.
"""
from __future__ import annotations

import pytest

from adapters.database.safety import (
    ConnectionIdentity,
    ConnectionPolicy,
    TargetLocality,
    UnsafeDatabaseTargetError,
    assert_disposable_target,
    redact,
    resolve_connection_identity,
    verify_connected_unix_socket_target,
)

TEST_DATABASE = "freedom_test"

NO_LIBPQ_ENVIRONMENT: dict[str, str] = {}

#: The refusal a TCP target earns under the destructive (default) policy.
NOT_A_SOCKET = "Unix-domain socket"


def assert_disposable(url: str, **kwargs) -> ConnectionIdentity:
    kwargs.setdefault("environ", NO_LIBPQ_ENVIRONMENT)
    return assert_disposable_target(url, expected_database=TEST_DATABASE, **kwargs)


# --------------------------------------------------------------------------
# Allowed: the documented local disposable test configuration
#
# All of these are the Unix-domain socket: no host at all (libpq's default
# socket directory) or an explicit socket directory.
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg:///freedom_test",
        "postgresql:///freedom_test",
        "postgresql+psycopg://freedom_test_app@/freedom_test",
        "postgresql+psycopg://freedom_test_app@/freedom_test?host=/var/run/postgresql",
        "postgresql+psycopg://freedom_test_app@/freedom_test?host=/run/postgresql&port=5432",
    ],
)
def test_the_documented_local_disposable_configuration_is_allowed(url):
    identity = assert_disposable(url)

    assert identity.database == TEST_DATABASE
    assert identity.is_local
    assert identity.is_unix_socket


# --------------------------------------------------------------------------
# Refused: TCP loopback, which cannot be told apart from a forwarded port
#
# These fixtures run `alembic downgrade base`. A URL that selects TCP — even to
# 127.0.0.1 — may reach a PostgreSQL server on another machine through an SSH
# local port forward, a pooler or any other proxy, so it is refused before the
# suite can act on it.
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "url",
    [
        # The form named in the finding.
        "postgresql+psycopg://user@127.0.0.1/freedom_test",
        "postgresql+psycopg://freedom_test_app@localhost/freedom_test",
        "postgresql+psycopg://freedom_test_app@127.0.0.1:5432/freedom_test",
        "postgresql+psycopg://freedom_test_app@[::1]:5432/freedom_test",
        "postgresql+psycopg://app@/freedom_test?host=127.0.0.1",
        "postgresql+psycopg://app@/freedom_test?hostaddr=127.0.0.1",
    ],
)
def test_a_tcp_loopback_target_is_refused_for_destructive_operations(url):
    with pytest.raises(UnsafeDatabaseTargetError, match=NOT_A_SOCKET) as raised:
        assert_disposable(url)

    assert "forward" in str(raised.value), "the refusal says why loopback is not enough"


@pytest.mark.parametrize(
    "environ",
    [
        {"PGHOST": "localhost"},
        {"PGHOST": "127.0.0.1"},
        {"PGHOSTADDR": "127.0.0.1"},
    ],
)
def test_a_loopback_target_inherited_from_libpq_is_refused(environ):
    """A hostless URL is only a socket while the environment leaves it alone."""
    with pytest.raises(UnsafeDatabaseTargetError, match=NOT_A_SOCKET):
        assert_disposable("postgresql+psycopg:///freedom_test", environ=environ)


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg://user@127.0.0.1/freedom_test",
        "postgresql+psycopg://freedom_test_app@localhost/freedom_test",
    ],
)
def test_the_weaker_policy_still_accepts_loopback_and_says_no_more_than_that(url):
    """The boundary the policy parameter draws, pinned from the other side.

    `SOCKET_OR_LOOPBACK` remains correct for a future *runtime* connection that
    creates and drops nothing. It is never what a destructive caller asks for,
    which is why it has to be requested explicitly.
    """
    identity = assert_disposable(url, policy=ConnectionPolicy.SOCKET_OR_LOOPBACK)

    assert identity.is_local
    assert not identity.is_unix_socket
    assert identity.locality is TargetLocality.TCP_LOOPBACK


def test_a_local_disposable_target_is_allowed_beside_a_different_runtime_database():
    identity = assert_disposable(
        "postgresql+psycopg:///freedom_test",
        runtime_url="postgresql+psycopg:///freedom_dev",
    )

    assert identity.database == TEST_DATABASE


# --------------------------------------------------------------------------
# Refused: the test URL and the runtime URL identify the same database
# --------------------------------------------------------------------------


def test_identical_urls_are_refused():
    url = "postgresql+psycopg:///freedom_test"

    with pytest.raises(UnsafeDatabaseTargetError, match="same database"):
        assert_disposable(url, runtime_url=url)


@pytest.mark.parametrize(
    ("test_url", "runtime_url"),
    [
        # The finding as reported: different driver, same database.
        ("postgresql+psycopg:///freedom_test", "postgresql:///freedom_test"),
        ("postgresql:///freedom_test", "postgresql+psycopg:///freedom_test"),
        # Loopback spelled three ways, plus the implicit default port. The test
        # URL itself must be a socket now; the *runtime* URL is only ever
        # compared, so it keeps covering every loopback spelling.
        (
            "postgresql+psycopg://a@/freedom_test",
            "postgresql+psycopg://b@127.0.0.1:5432/freedom_test",
        ),
        (
            "postgresql+psycopg:///freedom_test",
            "postgresql+psycopg://b@[::1]:5432/freedom_test",
        ),
        (
            "postgresql+psycopg:///freedom_test",
            "postgresql+psycopg://b@localhost/freedom_test",
        ),
        # A Unix socket and loopback on the same host: collapsed on purpose, so
        # that choosing the other spelling cannot make the destructive target
        # look distinct from the runtime one.
        (
            "postgresql+psycopg:///freedom_test",
            "postgresql+psycopg://app@127.0.0.1/freedom_test",
        ),
        (
            "postgresql+psycopg://a@/freedom_test?host=/var/run/postgresql",
            "postgresql+psycopg:///freedom_test",
        ),
        # Different credentials do not make it a different database.
        (
            "postgresql+psycopg://test_role:one@/freedom_test",
            "postgresql+psycopg://app_role:two@127.0.0.1/freedom_test",
        ),
        # The database named in a query parameter rather than the path.
        (
            "postgresql+psycopg:///freedom_test",
            "postgresql+psycopg://app@127.0.0.1/?dbname=freedom_test",
        ),
    ],
)
def test_equivalent_but_textually_different_urls_are_refused(test_url, runtime_url):
    assert test_url != runtime_url, "the point of this case is that the strings differ"

    with pytest.raises(UnsafeDatabaseTargetError, match="same database"):
        assert_disposable(test_url, runtime_url=runtime_url)


def test_a_different_port_is_a_different_database_and_is_allowed():
    """Two clusters on one host are genuinely distinct targets.

    A port distinguishes socket files as well as TCP ports: libpq names the
    socket `.s.PGSQL.<port>`.
    """
    identity = assert_disposable(
        "postgresql+psycopg://app@/freedom_test?port=5433",
        runtime_url="postgresql+psycopg://app@/freedom_test?port=5432",
    )

    assert identity.port == 5433


# --------------------------------------------------------------------------
# Refused: a database that is not the expected disposable one
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg:///freedom_production",
        "postgresql+psycopg:///freedom_staging",
        "postgresql+psycopg:///freedom_dev",
        "postgresql+psycopg://app@127.0.0.1/postgres",
        "postgresql+psycopg://app@127.0.0.1/?dbname=freedom_production",
    ],
)
def test_a_database_that_is_not_the_disposable_one_is_refused(url):
    with pytest.raises(UnsafeDatabaseTargetError, match="must name the disposable"):
        assert_disposable(url)


def test_a_database_inherited_from_pgdatabase_is_still_checked():
    """A URL naming no database resolves one from libpq, and it is validated."""
    with pytest.raises(UnsafeDatabaseTargetError, match="must name the disposable"):
        assert_disposable(
            "postgresql+psycopg://app@127.0.0.1/",
            environ={"PGDATABASE": "freedom_production"},
        )


def test_a_target_with_no_database_at_all_is_refused():
    with pytest.raises(UnsafeDatabaseTargetError, match="names no database"):
        assert_disposable("postgresql+psycopg://app@127.0.0.1/")


def test_a_non_postgresql_target_is_refused():
    with pytest.raises(UnsafeDatabaseTargetError, match="must use PostgreSQL"):
        assert_disposable("sqlite:///freedom_test")


# --------------------------------------------------------------------------
# Refused: remote and otherwise unsafe targets
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg://app:secret@db.example.org/freedom_test",
        "postgresql+psycopg://app@10.0.0.5:5432/freedom_test",
        "postgresql+psycopg://app@192.168.1.10/freedom_test",
        "postgresql+psycopg://app@/freedom_test?host=db.internal",
    ],
)
def test_a_remote_target_is_refused(url):
    with pytest.raises(UnsafeDatabaseTargetError, match="must be local to this host"):
        assert_disposable(url)


@pytest.mark.parametrize(
    "environ",
    [
        {"PGHOST": "db.example.org"},
        {"PGHOST": "10.0.0.5"},
        {"PGHOSTADDR": "10.0.0.5"},
        # PGHOSTADDR wins over a loopback PGHOST, exactly as libpq resolves it.
        {"PGHOST": "localhost", "PGHOSTADDR": "203.0.113.9"},
    ],
)
def test_a_hostless_url_redirected_by_libpq_is_refused(environ):
    """`postgresql:///freedom_test` has no host of its own; the environment supplies one."""
    with pytest.raises(UnsafeDatabaseTargetError, match="must be local to this host"):
        assert_disposable("postgresql+psycopg:///freedom_test", environ=environ)


@pytest.mark.parametrize(
    "environ",
    [
        {"PGSERVICE": "freedom"},
        {"PGSERVICEFILE": "/home/someone/.pg_service.conf"},
    ],
)
def test_a_target_defined_by_a_service_file_is_refused(environ):
    """A service file moves the target outside this repository; fail closed."""
    with pytest.raises(UnsafeDatabaseTargetError, match="cannot be verified"):
        assert_disposable("postgresql+psycopg:///freedom_test", environ=environ)


# --------------------------------------------------------------------------
# Refused: a target that names more than one server or more than one database
#
# Codex Phase 1 re-review finding: `resolve_connection_identity` inspected only
# the *first* value of a repeated `host` query parameter, so
# `…/freedom_production?host=127.0.0.1&host=db.example.org` was classified local
# while psycopg's multi-host failover could connect to `db.example.org`.
#
# The policy is rejection, not per-host validation: the documented topology is a
# single loopback-only cluster per environment and no failover target is
# approved, so a target that cannot be reduced to one server and one database is
# refused. Multiple *local* hosts are refused too — the policy is about how many
# targets there are, not about which ones happen to be safe.
# --------------------------------------------------------------------------

MULTI_TARGET = "failover|more than one"


def test_the_reported_finding_url_is_refused():
    """The exact URL from the finding, which previously resolved as local."""
    url = (
        "postgresql+psycopg://app@/freedom_production"
        "?host=127.0.0.1&host=db.example.org"
    )

    with pytest.raises(UnsafeDatabaseTargetError, match=MULTI_TARGET):
        resolve_connection_identity(url, environ=NO_LIBPQ_ENVIRONMENT)


@pytest.mark.parametrize(
    ("case", "url"),
    [
        (
            "local then remote",
            "postgresql+psycopg://app@/freedom_test?host=127.0.0.1&host=db.example.org",
        ),
        (
            "remote then local",
            "postgresql+psycopg://app@/freedom_test?host=db.example.org&host=127.0.0.1",
        ),
        (
            "two local hosts",
            "postgresql+psycopg://app@/freedom_test?host=127.0.0.1&host=localhost",
        ),
        (
            "socket then remote",
            "postgresql+psycopg://app@/freedom_test?host=/var/run/postgresql&host=db.example.org",
        ),
        (
            "three hosts",
            "postgresql+psycopg://app@/freedom_test"
            "?host=127.0.0.1&host=db.example.org&host=::1",
        ),
    ],
)
def test_a_repeated_host_parameter_is_refused(case, url):
    with pytest.raises(UnsafeDatabaseTargetError, match=MULTI_TARGET) as raised:
        assert_disposable(url)

    assert "host" in str(raised.value), case


@pytest.mark.parametrize(
    "url",
    [
        # The comma-separated spelling, in the query …
        "postgresql+psycopg://app@/freedom_test?host=127.0.0.1,db.example.org",
        "postgresql+psycopg://app@/freedom_test?host=db.example.org,127.0.0.1",
        "postgresql+psycopg://app@/freedom_test?host=127.0.0.1,localhost",
        # … and in the URL authority, where SQLAlchemy reports it as one host.
        "postgresql+psycopg://app@127.0.0.1,db.example.org/freedom_test",
        "postgresql+psycopg://app@localhost,127.0.0.1/freedom_test",
        # `hostaddr` is the address libpq dials; it takes a list too.
        "postgresql+psycopg://app@/freedom_test?hostaddr=127.0.0.1,203.0.113.9",
    ],
)
def test_a_comma_separated_host_list_is_refused(url):
    with pytest.raises(UnsafeDatabaseTargetError, match=MULTI_TARGET):
        assert_disposable(url)


@pytest.mark.parametrize(
    "environ",
    [
        {"PGHOST": "127.0.0.1,db.example.org"},
        {"PGHOST": "db.example.org,127.0.0.1"},
        {"PGHOST": "127.0.0.1,localhost"},
        {"PGHOSTADDR": "127.0.0.1,203.0.113.9"},
    ],
)
def test_a_multi_host_libpq_environment_is_refused(environ):
    """A hostless URL inherits the list, so the environment carries it too."""
    with pytest.raises(UnsafeDatabaseTargetError, match=MULTI_TARGET):
        assert_disposable("postgresql+psycopg:///freedom_test", environ=environ)


@pytest.mark.parametrize(
    ("field", "url", "environ"),
    [
        ("port", "postgresql+psycopg://app@127.0.0.1/freedom_test?port=5432&port=5433", {}),
        ("port", "postgresql+psycopg://app@127.0.0.1/freedom_test?port=5432,5433", {}),
        ("port", "postgresql+psycopg:///freedom_test", {"PGPORT": "5432,5433"}),
        ("database", "postgresql+psycopg://app@127.0.0.1/?dbname=freedom_test&dbname=freedom_production", {}),
    ],
)
def test_a_repeated_port_or_database_is_refused(field, url, environ):
    """One target means one server *and* one database, not merely one host."""
    with pytest.raises(UnsafeDatabaseTargetError, match=MULTI_TARGET) as raised:
        assert_disposable(url, environ=environ)

    assert field in str(raised.value)


@pytest.mark.parametrize(
    ("url", "field"),
    [
        # The URL authority looks local; the query parameter is what psycopg
        # actually connects to. Verified against psycopg 3: the parameter wins.
        ("postgresql+psycopg://127.0.0.1/freedom_test?host=db.example.org", "host"),
        ("postgresql+psycopg://db.example.org/freedom_test?host=127.0.0.1", "host"),
        # The path names one database and the query names another.
        ("postgresql+psycopg:///freedom_test?dbname=freedom_production", "database"),
        ("postgresql+psycopg:///freedom_production?dbname=freedom_test", "database"),
        ("postgresql+psycopg://app@127.0.0.1:5432/freedom_test?port=5433", "port"),
    ],
)
def test_a_url_that_names_one_component_twice_is_refused(url, field):
    with pytest.raises(UnsafeDatabaseTargetError, match="more than one") as raised:
        assert_disposable(url)

    assert field in str(raised.value)


def test_a_single_host_repeated_with_the_same_value_is_not_ambiguous():
    """Saying the same thing twice names one target, so it resolves.

    Resolution and policy are separate steps: this URL names one target (it is
    not ambiguous), and it is still refused for a destructive operation because
    that one target is TCP.
    """
    identity = resolve_connection_identity(
        "postgresql+psycopg://127.0.0.1/freedom_test?host=127.0.0.1",
        environ=NO_LIBPQ_ENVIRONMENT,
    )

    assert identity.is_local
    assert identity.locality is TargetLocality.TCP_LOOPBACK

    with pytest.raises(UnsafeDatabaseTargetError, match=NOT_A_SOCKET):
        assert_disposable("postgresql+psycopg://127.0.0.1/freedom_test?host=127.0.0.1")


def test_a_remote_hostaddr_is_refused():
    """`hostaddr` is the address libpq dials, so it decides locality."""
    with pytest.raises(UnsafeDatabaseTargetError, match="must be local to this host"):
        assert_disposable("postgresql+psycopg://app@/freedom_test?hostaddr=203.0.113.9")


def test_a_local_hostaddr_is_refused_because_it_is_still_tcp():
    """A loopback `hostaddr` is an address, and an address means a TCP session."""
    with pytest.raises(UnsafeDatabaseTargetError, match=NOT_A_SOCKET):
        assert_disposable("postgresql+psycopg://app@/freedom_test?hostaddr=127.0.0.1")


# --------------------------------------------------------------------------
# `host` and `hostaddr` are two libpq parameters, not two spellings of one
#
# Codex Phase 1 third re-review finding: `PGHOSTADDR` was consulted only when the
# URL supplied no host at all. libpq does not work that way. `hostaddr` is the
# address the connection is *made to*; when it is set, `host` is used only for
# authentication. So
#
#     PGHOSTADDR=127.0.0.1
#     DATABASE_URL='postgresql+psycopg:///freedom_test?host=/var/run/postgresql'
#
# passed static validation as a Unix-domain socket while psycopg dialled TCP to
# 127.0.0.1 — verified on this host, not reasoned about. An inherited *remote*
# PGHOSTADDR would have sent the credentials to that server. The live check
# cannot cover this: it only runs once a connection exists, which is already too
# late.
#
# The socket-directory-plus-address combination is refused at resolution, under
# every policy, because a socket and an address are different transports and a
# configuration naming both names no single provable target.
# --------------------------------------------------------------------------

#: The refusal that combination earns, whichever half supplied the address.
SOCKET_PLUS_ADDRESS = "Unix-domain socket directory"


@pytest.mark.parametrize(
    "environ",
    [
        pytest.param({"PGHOSTADDR": "127.0.0.1"}, id="loopback"),
        pytest.param({"PGHOSTADDR": "::1"}, id="ipv6-loopback"),
        pytest.param({"PGHOSTADDR": "203.0.113.9"}, id="remote"),
        pytest.param({"PGHOSTADDR": "10.0.0.5"}, id="private-remote"),
        # `host` names the socket in the environment too.
        pytest.param(
            {"PGHOST": "/var/run/postgresql", "PGHOSTADDR": "127.0.0.1"},
            id="socket-pghost-plus-loopback",
        ),
    ],
)
@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg:///freedom_test?host=/var/run/postgresql",
        "postgresql+psycopg://freedom_test_app@/freedom_test?host=/run/postgresql",
        "postgresql+psycopg:///freedom_test",
    ],
)
def test_a_socket_target_combined_with_an_inherited_host_address_is_refused(url, environ):
    """The reported finding, in every combination of its two halves.

    The hostless URL is included: it is the *documented* configuration, and it
    is a socket only while the environment leaves it alone.
    """
    with pytest.raises(UnsafeDatabaseTargetError) as raised:
        assert_disposable(url, environ=environ)

    message = str(raised.value)
    assert "socket" in message, "the refusal says what was asked for"
    assert environ["PGHOSTADDR"] in message or NOT_A_SOCKET in message


@pytest.mark.parametrize(
    "url",
    [
        # The address supplied by the URL rather than by the environment.
        "postgresql+psycopg:///freedom_test?host=/var/run/postgresql&hostaddr=127.0.0.1",
        "postgresql+psycopg:///freedom_test?hostaddr=203.0.113.9&host=/var/run/postgresql",
    ],
)
def test_a_socket_host_beside_a_url_host_address_is_refused(url):
    with pytest.raises(UnsafeDatabaseTargetError, match=SOCKET_PLUS_ADDRESS):
        assert_disposable(url)


@pytest.mark.parametrize(
    "policy", [ConnectionPolicy.UNIX_SOCKET_ONLY, ConnectionPolicy.SOCKET_OR_LOOPBACK]
)
def test_the_socket_and_address_contradiction_is_refused_under_every_policy(policy):
    """It is refused when the target is *resolved*, not when a policy is applied.

    A loopback `hostaddr` would otherwise satisfy `SOCKET_OR_LOOPBACK` — the
    address really is loopback — while the operator's URL says socket. A
    configuration whose two halves disagree about the transport is refused for
    every caller, however weak that caller's policy is.
    """
    with pytest.raises(UnsafeDatabaseTargetError, match=SOCKET_PLUS_ADDRESS):
        assert_disposable(
            "postgresql+psycopg:///freedom_test?host=/var/run/postgresql",
            environ={"PGHOSTADDR": "127.0.0.1"},
            policy=policy,
        )


@pytest.mark.parametrize(
    "url",
    [
        # SQLAlchemy 2.0 does not percent-decode the URL authority, so this
        # reaches libpq as the *name* '%2Fvar%2Frun%2Fpostgresql' and is a remote
        # target, not a socket. It is refused either way, which is what this
        # asserts: if a future SQLAlchemy decodes it, the socket-plus-address
        # refusal catches it instead.
        "postgresql+psycopg://%2Fvar%2Frun%2Fpostgresql/freedom_test",
        "postgresql+psycopg://app@%2Frun%2Fpostgresql/freedom_test",
    ],
)
@pytest.mark.parametrize(
    "environ",
    [{"PGHOSTADDR": "127.0.0.1"}, {"PGHOSTADDR": "203.0.113.9"}, NO_LIBPQ_ENVIRONMENT],
)
def test_a_socket_like_url_authority_with_an_inherited_address_is_refused(url, environ):
    with pytest.raises(UnsafeDatabaseTargetError):
        assert_disposable(url, environ=environ)


@pytest.mark.parametrize(
    ("url", "environ"),
    [
        # An address beside a *name* is decidable: libpq dials the address and
        # keeps the name for authentication only. It is refused because that
        # address is remote — not because the pair is ambiguous.
        ("postgresql+psycopg://127.0.0.1/freedom_test?hostaddr=203.0.113.9", {}),
        ("postgresql+psycopg://app@/freedom_test?hostaddr=10.0.0.5&host=localhost", {}),
        ("postgresql+psycopg://app@/freedom_test?host=localhost", {"PGHOSTADDR": "10.0.0.5"}),
        ("postgresql+psycopg://127.0.0.1/freedom_test", {"PGHOSTADDR": "203.0.113.9"}),
    ],
)
def test_a_host_address_outranks_a_named_host(url, environ):
    """libpq's precedence, applied rather than approximated.

    These four used to be classified by the *name*, or refused as ambiguous.
    Both readings hid the same thing: the address is what gets dialled, so the
    address is what the policy has to be applied to.
    """
    with pytest.raises(UnsafeDatabaseTargetError, match="must be local to this host"):
        assert_disposable(url, environ=environ)


def test_a_url_host_address_overrides_the_inherited_one():
    """`PGHOSTADDR` is a *default* for `hostaddr`, so an explicit one wins."""
    identity = resolve_connection_identity(
        "postgresql+psycopg://app@/freedom_test?hostaddr=127.0.0.1",
        environ={"PGHOSTADDR": "203.0.113.9"},
    )

    assert identity.locality is TargetLocality.TCP_LOOPBACK
    assert identity.is_local


def test_a_host_address_that_is_not_an_address_does_not_borrow_the_local_token():
    """A `hostaddr` shaped like a path is a misconfiguration, not a socket.

    libpq rejects it at connect time. It must not reach that point classified as
    the local socket on the way, which `_normalise_host` alone would have done.
    """
    identity = resolve_connection_identity(
        "postgresql+psycopg:///freedom_test",
        environ={"PGHOSTADDR": "/var/run/postgresql"},
    )

    assert not identity.is_unix_socket
    assert not identity.is_local
    assert identity.locality is TargetLocality.REMOTE


def test_the_socket_and_address_refusal_carries_no_credentials():
    """The finding's URL with a password in it, refused without echoing it."""
    with pytest.raises(UnsafeDatabaseTargetError, match=SOCKET_PLUS_ADDRESS) as raised:
        assert_disposable(
            "postgresql+psycopg://migration_role:hunter2@/freedom_test"
            "?host=/var/run/postgresql",
            environ={"PGHOSTADDR": "203.0.113.9"},
        )

    message = str(raised.value)
    assert "hunter2" not in message
    assert "migration_role" not in message
    assert "postgresql+psycopg://" not in message, "no raw URL either"


@pytest.mark.parametrize("address", ["127.0.0.1", "203.0.113.9"])
@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg:///freedom_test",
        "postgresql+psycopg://app@/freedom_test?host=/var/run/postgresql",
    ],
)
def test_the_destructive_pytest_guard_refuses_an_inherited_host_address(
    monkeypatch, url, address
):
    """The same precedence, on the path that runs `alembic downgrade base`.

    `tests/conftest.py` resolves `TEST_DATABASE_URL` against the ambient libpq
    environment through the same function, so this exercises the real guard the
    destructive fixtures call rather than a re-statement of it. It **fails** the
    run rather than skipping: a skip would let a misconfigured suite look green.
    """
    from tests.conftest import resolve_test_database_url

    monkeypatch.setenv("TEST_DATABASE_URL", url)
    monkeypatch.setenv("PGHOSTADDR", address)
    monkeypatch.delenv("PGHOST", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(pytest.fail.Exception, match="Refusing to run destructive"):
        resolve_test_database_url()


def test_a_service_parameter_in_the_url_is_refused():
    """`?service=` moves the target into a file, exactly as PGSERVICE does."""
    with pytest.raises(UnsafeDatabaseTargetError, match="cannot be verified"):
        assert_disposable("postgresql+psycopg:///freedom_test?service=freedom")


def test_a_single_host_and_port_parameter_pair_is_still_allowed():
    """The rejection is of *lists*, not of the query-parameter form itself."""
    identity = assert_disposable(
        "postgresql+psycopg://app@/freedom_test?host=/var/run/postgresql&port=5433"
    )

    assert identity.is_unix_socket
    assert identity.port == 5433


def test_an_unparsable_url_is_refused_without_echoing_it():
    with pytest.raises(UnsafeDatabaseTargetError) as raised:
        assert_disposable("postgresql+psycopg://app:hunter2@@@:::/freedom_test")

    assert "hunter2" not in str(raised.value)


# --------------------------------------------------------------------------
# Passwords never reach a message
# --------------------------------------------------------------------------


def test_no_refusal_message_contains_a_password():
    cases = [
        ("postgresql+psycopg://app:hunter2@db.example.org/freedom_test", None),
        ("postgresql+psycopg://app:hunter2@127.0.0.1/freedom_production", None),
        (
            "postgresql+psycopg://app:hunter2@127.0.0.1/freedom_test",
            "postgresql://other:hunter2@localhost/freedom_test",
        ),
        # The multi-target refusals render host, port and database values into
        # their messages; none of those fields may carry the credential.
        (
            "postgresql+psycopg://app:hunter2@/freedom_test?host=127.0.0.1&host=db.example.org",
            None,
        ),
        (
            "postgresql+psycopg://app:hunter2@/freedom_test?host=127.0.0.1,db.example.org",
            None,
        ),
        (
            "postgresql+psycopg://app:hunter2@127.0.0.1/freedom_test?host=db.example.org",
            None,
        ),
        (
            "postgresql+psycopg://app:hunter2@127.0.0.1/freedom_test?dbname=freedom_production",
            None,
        ),
        (
            "postgresql+psycopg://app:hunter2@127.0.0.1/freedom_test?service=freedom",
            None,
        ),
    ]
    for url, runtime_url in cases:
        with pytest.raises(UnsafeDatabaseTargetError) as raised:
            assert_disposable(url, runtime_url=runtime_url)
        assert "hunter2" not in str(raised.value)


def test_redact_hides_the_password():
    rendered = redact("postgresql+psycopg://app:hunter2@127.0.0.1/freedom_test")

    assert "hunter2" not in rendered
    assert "freedom_test" in rendered


def test_the_identity_description_carries_no_credentials():
    identity = resolve_connection_identity(
        "postgresql+psycopg://app:hunter2@127.0.0.1/freedom_test",
        environ=NO_LIBPQ_ENVIRONMENT,
    )

    described = identity.describe()

    assert "hunter2" not in described
    assert "app" not in described
    assert "freedom_test" in described


# --------------------------------------------------------------------------
# The runtime check: what the *server* says about the connection
# --------------------------------------------------------------------------


class FakeResult:
    def __init__(self, row):
        self._row = row

    def one(self):
        return self._row


class FakeConnection:
    """Stands in for a SQLAlchemy connection; returns one canned server answer."""

    def __init__(self, row):
        self._row = row

    def exec_driver_sql(self, statement):  # noqa: ARG002 - the statement is fixed
        return FakeResult(self._row)


def test_a_unix_socket_connection_to_the_expected_database_is_accepted():
    verify_connected_unix_socket_target(
        FakeConnection(("freedom_test", True, "", "")),
        expected_database=TEST_DATABASE,
    )


@pytest.mark.parametrize(
    "row",
    [
        ("freedom_test", False, "127.0.0.1", "127.0.0.1"),
        ("freedom_test", False, "::1", "::1"),
    ],
)
def test_a_loopback_connection_to_the_expected_database_is_refused(row):
    """The heart of the finding: this answer used to be accepted.

    Expected database, loopback server, loopback client — and it proves nothing.
    An SSH local port forward to a PostgreSQL server on another machine produces
    precisely this row, because that server sees sshd connecting over its own
    loopback interface. Only null addresses — a Unix-domain socket — distinguish
    a local server, so this is refused.
    """
    with pytest.raises(UnsafeDatabaseTargetError, match=NOT_A_SOCKET) as raised:
        verify_connected_unix_socket_target(
            FakeConnection(row), expected_database=TEST_DATABASE
        )

    assert "forwarded port" in str(raised.value)


def test_a_connection_that_landed_in_another_database_is_refused():
    """The static checks cannot see this: the URL said `freedom_test`."""
    with pytest.raises(UnsafeDatabaseTargetError, match="not the expected"):
        verify_connected_unix_socket_target(
            FakeConnection(("freedom_production", True, "", "")),
            expected_database=TEST_DATABASE,
        )


def test_the_database_is_checked_even_on_a_unix_socket_connection():
    """A socket proves the host, not the database. Both halves are checked."""
    with pytest.raises(UnsafeDatabaseTargetError, match="not the expected"):
        verify_connected_unix_socket_target(
            FakeConnection(("postgres", True, "", "")),
            expected_database=TEST_DATABASE,
        )


@pytest.mark.parametrize(
    "row",
    [
        ("freedom_test", False, "10.0.0.5", "10.0.0.9"),
        ("freedom_test", False, "127.0.0.1", "10.0.0.9"),
        ("freedom_test", False, "203.0.113.7", "127.0.0.1"),
    ],
)
def test_a_connection_that_left_this_host_is_refused(row):
    with pytest.raises(UnsafeDatabaseTargetError, match=NOT_A_SOCKET):
        verify_connected_unix_socket_target(
            FakeConnection(row), expected_database=TEST_DATABASE
        )


# --------------------------------------------------------------------------
# The identity a policy is applied to still ignores the connection form
# --------------------------------------------------------------------------


def test_a_socket_and_a_loopback_url_are_one_identity():
    """Otherwise a destructive target could hide from the runtime comparison.

    The policy reads `locality`; identity equality deliberately does not, so
    `postgresql:///freedom_test` and `postgresql://app@127.0.0.1/freedom_test`
    still compare as the same database.
    """
    socket_identity = resolve_connection_identity(
        "postgresql+psycopg:///freedom_test", environ=NO_LIBPQ_ENVIRONMENT
    )
    loopback_identity = resolve_connection_identity(
        "postgresql+psycopg://app@127.0.0.1:5432/freedom_test",
        environ=NO_LIBPQ_ENVIRONMENT,
    )

    assert socket_identity == loopback_identity
    assert socket_identity.locality is TargetLocality.UNIX_SOCKET
    assert loopback_identity.locality is TargetLocality.TCP_LOOPBACK
