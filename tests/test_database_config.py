import pytest

from adapters.database.config import ConnectionPolicy, DatabaseSettings


def test_staging_accepts_only_its_separate_socket_database():
    settings = DatabaseSettings.from_mapping(
        {
            "DATABASE_URL": (
                "postgresql+psycopg://freedom_staging_app:synthetic@/freedom_staging"
            )
        },
        environment="staging",
    )

    assert settings.environment == "staging"


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg:///freedom_test",
        "postgresql+psycopg://freedom_test_app@/freedom_test",
        "postgresql+psycopg://freedom_test_app@/freedom_test?host=/var/run/postgresql",
    ],
)
def test_local_socket_forms_are_accepted(url):
    """The documented migration form has no host at all — a Unix-domain socket."""
    settings = DatabaseSettings.from_mapping({"DATABASE_URL": url}, environment="test")

    assert settings.environment == "test"


# --------------------------------------------------------------------------
# Codex Phase 1 second re-review finding: loopback is not proof of a local
# server, and this is the class every Alembic invocation goes through.
#
# `postgresql+psycopg://user@127.0.0.1/freedom_test` is what an SSH local port
# forward to another host's PostgreSQL looks like from here, and the server at
# the far end reports loopback addresses too. Migrations change the schema, so
# the socket is required and the default policy is the strict one.
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("environment", "url"),
    [
        ("test", "postgresql+psycopg://user@127.0.0.1/freedom_test"),
        ("test", "postgresql+psycopg://user@localhost/freedom_test"),
        ("test", "postgresql+psycopg://user@[::1]:5432/freedom_test"),
        ("test", "postgresql+psycopg://user@/freedom_test?host=127.0.0.1"),
        ("test", "postgresql+psycopg://user@/freedom_test?hostaddr=127.0.0.1"),
        ("development", "postgresql+psycopg://user@127.0.0.1:5432/freedom_dev"),
        ("staging", "postgresql+psycopg://user@127.0.0.1/freedom_staging"),
        ("production", "postgresql+psycopg://user@127.0.0.1/freedom_production"),
    ],
)
def test_a_tcp_loopback_migration_target_is_refused(environment, url):
    with pytest.raises(ValueError, match="Unix-domain socket") as raised:
        DatabaseSettings.from_mapping({"DATABASE_URL": url}, environment=environment)

    assert "forward" in str(raised.value), "the refusal says why loopback is not enough"


def test_a_loopback_target_inherited_from_libpq_is_refused():
    """The socket form is only a socket while PGHOST leaves it alone."""
    with pytest.raises(ValueError, match="Unix-domain socket"):
        DatabaseSettings.from_mapping(
            {"DATABASE_URL": "postgresql+psycopg:///freedom_dev"},
            environment="development",
            environ={"PGHOST": "127.0.0.1"},
        )


# --------------------------------------------------------------------------
# Codex Phase 1 third re-review finding: `host` and `hostaddr` are two libpq
# parameters, and `PGHOSTADDR` applies whenever the URL sets no `hostaddr` —
# including when the URL sets `host`. A socket URL plus an inherited address is
# a TCP connection, and every Alembic invocation resolves its target through
# this class, so it has to be refused here.
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "address", ["127.0.0.1", "::1", "203.0.113.9", "10.0.0.5"]
)
@pytest.mark.parametrize(
    ("environment", "url"),
    [
        ("test", "postgresql+psycopg:///freedom_test?host=/var/run/postgresql"),
        ("development", "postgresql+psycopg://app@/freedom_dev?host=/run/postgresql"),
        ("staging", "postgresql+psycopg:///freedom_staging?host=/var/run/postgresql"),
        (
            "production",
            "postgresql+psycopg://app@/freedom_production?host=/var/run/postgresql",
        ),
    ],
)
def test_a_socket_migration_url_with_an_inherited_host_address_is_refused(
    environment, url, address
):
    """The documented socket form is only a socket while PGHOSTADDR leaves it alone."""
    with pytest.raises(ValueError, match="Unix-domain socket directory"):
        DatabaseSettings.from_mapping(
            {"DATABASE_URL": url},
            environment=environment,
            environ={"PGHOSTADDR": address},
        )


@pytest.mark.parametrize(
    "policy", [ConnectionPolicy.UNIX_SOCKET_ONLY, ConnectionPolicy.SOCKET_OR_LOOPBACK]
)
def test_the_socket_and_address_contradiction_is_refused_under_every_policy(policy):
    with pytest.raises(ValueError, match="Unix-domain socket directory"):
        DatabaseSettings.from_mapping(
            {"DATABASE_URL": "postgresql+psycopg:///freedom_dev?host=/var/run/postgresql"},
            environment="development",
            environ={"PGHOSTADDR": "127.0.0.1"},
            policy=policy,
        )


def test_a_hostless_migration_url_with_an_inherited_host_address_is_refused():
    """No `host` at all is libpq's default socket — until PGHOSTADDR is set."""
    with pytest.raises(ValueError, match="Unix-domain socket"):
        DatabaseSettings.from_mapping(
            {"DATABASE_URL": "postgresql+psycopg:///freedom_dev"},
            environment="development",
            environ={"PGHOSTADDR": "127.0.0.1"},
        )


def test_a_refused_socket_and_address_url_does_not_echo_the_password():
    with pytest.raises(ValueError) as raised:
        DatabaseSettings.from_mapping(
            {
                "DATABASE_URL": "postgresql+psycopg://migration_role:hunter2@"
                "/freedom_dev?host=/var/run/postgresql"
            },
            environment="development",
            environ={"PGHOSTADDR": "203.0.113.9"},
        )

    message = str(raised.value)
    assert "hunter2" not in message
    assert "migration_role" not in message


def test_the_strict_socket_policy_is_the_default():
    """Fail closed: a caller has to ask for the weaker check by name."""
    url = "postgresql+psycopg://user@127.0.0.1/freedom_dev"

    with pytest.raises(ValueError, match="Unix-domain socket"):
        DatabaseSettings.from_mapping({"DATABASE_URL": url}, environment="development")

    settings = DatabaseSettings.from_mapping(
        {"DATABASE_URL": url},
        environment="development",
        policy=ConnectionPolicy.SOCKET_OR_LOOPBACK,
    )

    assert settings.identity.is_local
    assert not settings.identity.is_unix_socket


def test_an_unknown_environment_is_refused():
    with pytest.raises(ValueError, match="Unknown application environment"):
        DatabaseSettings.from_mapping(
            {"DATABASE_URL": "postgresql+psycopg:///freedom_dev"},
            environment="prod",
        )


def test_a_missing_url_is_refused():
    with pytest.raises(ValueError, match="DATABASE_URL is required"):
        DatabaseSettings.from_mapping({}, environment="development")


@pytest.mark.parametrize(
    ("environment", "url", "message"),
    [
        (
            "staging",
            "postgresql+psycopg://app:synthetic@127.0.0.1/freedom_production",
            "must use database 'freedom_staging'",
        ),
        (
            "development",
            "postgresql+psycopg://app:synthetic@127.0.0.1/freedom_production",
            "must use database 'freedom_dev'",
        ),
        (
            "test",
            "postgresql+psycopg://app:synthetic@127.0.0.1/freedom_production",
            "must use database 'freedom_test'",
        ),
        (
            "test",
            "sqlite:///freedom_test",
            "must use PostgreSQL",
        ),
        (
            "production",
            "postgresql+psycopg://app:synthetic@db.example/freedom_production",
            "Unix-domain socket",
        ),
        (
            "development",
            "postgresql+psycopg://app:synthetic@10.0.0.5/freedom_dev",
            "Unix-domain socket",
        ),
    ],
)
def test_database_configuration_fails_closed(environment, url, message):
    with pytest.raises(ValueError, match=message):
        DatabaseSettings.from_mapping(
            {"DATABASE_URL": url},
            environment=environment,
        )


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg://app:synthetic@db.example/freedom_dev",
        "postgresql+psycopg://app:synthetic@10.0.0.5/freedom_dev",
    ],
)
def test_the_weaker_policy_still_refuses_a_named_remote_host(url):
    """What `SOCKET_OR_LOOPBACK` does claim, kept under test alongside what it does not."""
    with pytest.raises(ValueError, match="loopback-only"):
        DatabaseSettings.from_mapping(
            {"DATABASE_URL": url},
            environment="development",
            policy=ConnectionPolicy.SOCKET_OR_LOOPBACK,
        )


# --------------------------------------------------------------------------
# Multi-target URLs, on the path Alembic uses
#
# Codex Phase 1 re-review finding: the guard read only the first value of a
# repeated `host` parameter, so the URL below resolved as local while psycopg's
# multi-host failover could reach `db.example.org`. `migrations/env.py` runs
# every Alembic invocation through this class, so the refusal has to happen
# here, not only in `assert_disposable_target`.
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("environment", "url"),
    [
        # The finding, verbatim.
        (
            "production",
            "postgresql+psycopg://app@/freedom_production"
            "?host=127.0.0.1&host=db.example.org",
        ),
        (
            "production",
            "postgresql+psycopg://app@/freedom_production"
            "?host=db.example.org&host=127.0.0.1",
        ),
        # Every other spelling of the same list.
        (
            "development",
            "postgresql+psycopg://app@/freedom_dev?host=127.0.0.1,db.example.org",
        ),
        (
            "development",
            "postgresql+psycopg://app@127.0.0.1,db.example.org/freedom_dev",
        ),
        # Two local hosts are still two hosts.
        (
            "test",
            "postgresql+psycopg://app@/freedom_test?host=127.0.0.1&host=localhost",
        ),
        # One component named twice, with different values.
        (
            "test",
            "postgresql+psycopg://127.0.0.1/freedom_test?host=db.example.org",
        ),
        (
            "test",
            "postgresql+psycopg:///freedom_test?dbname=freedom_production",
        ),
    ],
)
def test_a_multi_target_migration_url_is_refused(environment, url):
    with pytest.raises(ValueError, match="failover|more than one"):
        DatabaseSettings.from_mapping({"DATABASE_URL": url}, environment=environment)


def test_a_multi_host_libpq_environment_is_refused_for_migrations():
    with pytest.raises(ValueError, match="failover"):
        DatabaseSettings.from_mapping(
            {"DATABASE_URL": "postgresql+psycopg:///freedom_dev"},
            environment="development",
            environ={"PGHOST": "127.0.0.1,db.example.org"},
        )


def test_a_refused_migration_url_does_not_echo_the_password():
    urls = [
        "postgresql+psycopg://app:hunter2@/freedom_dev?host=127.0.0.1&host=db.example.org",
        "postgresql+psycopg://app:hunter2@/freedom_dev?host=127.0.0.1,db.example.org",
        "postgresql+psycopg://app:hunter2@127.0.0.1/freedom_dev?dbname=freedom_production",
        "postgresql+psycopg://app:hunter2@db.example.org/freedom_dev",
    ]
    for url in urls:
        with pytest.raises(ValueError) as raised:
            DatabaseSettings.from_mapping(
                {"DATABASE_URL": url}, environment="development"
            )
        assert "hunter2" not in str(raised.value)
