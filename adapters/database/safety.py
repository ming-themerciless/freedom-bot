"""Connection-identity safety boundary for destructive database operations.

`alembic downgrade base` and `DROP SCHEMA public CASCADE` destroy a database.
Before either runs, the caller has to be able to prove *which* database it is
about to destroy. A URL string is not that proof:

- `postgresql:///freedom_test` and `postgresql+psycopg:///freedom_test` name the
  same database while comparing unequal as strings, so a raw `!=` check between
  a test URL and a runtime URL can pass while both point at one database;
- a URL that omits a host, a host address, a port or a database inherits it from
  libpq's environment (`PGHOST`, `PGHOSTADDR`, `PGPORT`, `PGDATABASE`), so the
  target is not a property of the URL alone — and `host` and `hostaddr` are two
  *separate* parameters, each with its own environment default, so naming one of
  them in the URL does not stop the environment supplying the other;
- `PGSERVICE`/`PGSERVICEFILE` move the target definition into a file outside
  this repository entirely; and
- one URL can name *several* targets. libpq supports multi-host failover, so
  `?host=127.0.0.1&host=db.example.org` is two servers, and a check that reads
  only the first value calls that target local while the connection may reach
  `db.example.org`. A URL can also name one component twice with different
  values — `postgresql+psycopg://127.0.0.1/db?host=db.example.org` connects to
  `db.example.org`, not to `127.0.0.1`.

**`hostaddr` outranks `host`, and this module got that wrong.** libpq documents
them as separate parameters: `hostaddr` is the address the connection is *made
to*, and when it is set, `host` is not used to find the server at all — it
becomes a name used only for authentication. So

    PGHOSTADDR=127.0.0.1
    DATABASE_URL='postgresql+psycopg:///freedom_test?host=/var/run/postgresql'

is a **TCP connection to 127.0.0.1**, not the Unix-domain socket the URL names,
and this was confirmed against psycopg on this host rather than reasoned about.
An earlier revision consulted `PGHOSTADDR` only when the URL supplied no host of
any kind, so that configuration passed static validation as a socket while the
credentials went to whatever server `PGHOSTADDR` pointed at. `host` and
`hostaddr` are therefore resolved independently below and combined afterwards,
and the combination *socket directory plus any host address* is refused outright
rather than merely reclassified: a configuration whose two halves describe
different transports cannot be what the operator meant.

Neither is a loopback *address* that proof, and an earlier version of this module
claimed otherwise:

    An SSH local port forward binds 127.0.0.1:5432 on this host and carries the
    session to a PostgreSQL server somewhere else. That server sees a connection
    arriving from sshd on its own loopback interface, so `inet_server_addr()`
    and `inet_client_addr()` both report loopback — the same answer a genuinely
    local TCP connection gives. A connection pooler or any other TCP proxy has
    the same shape. **Inspecting the addresses of a TCP connection cannot tell a
    local server from a tunnel to a remote one.**

So the destructive and schema-changing workflows in this repository — online
Alembic migrations, the destructive integration-test fixtures, and the
backup/restore drill — require a PostgreSQL **Unix-domain socket**, statically
and then again on the live connection. A Unix socket is a file on this host: a
TCP tunnel cannot present one, and a server reached through one reports null
addresses at both ends.

`ConnectionPolicy` makes that requirement explicit at every call site, because
the weaker "loopback or socket" check remains correct for an *ordinary* runtime
connection, which creates and drops nothing. What the weaker policy does not do
is prove the server is on this machine, and nothing here says it does.

**The residual, stated rather than hidden.** Requiring a socket closes the
tunnel and proxy paths above; it is not an absolute proof of locality. A
deliberately forwarded Unix socket (`ssh -L /tmp/s:/remote/s`) would still
present a socket whose server reports null addresses. That is a hostile,
hand-built configuration on the operator's own host rather than the ordinary
`ssh -L 5432:localhost:5432` accident this guard exists to refuse, and no
in-process check can exclude it.

This module resolves a URL *plus* the ambient libpq environment into one
normalised `ConnectionIdentity`, and provides
`verify_connected_unix_socket_target`, which asks the server where the
connection actually landed before anything is dropped.

No function here puts a password into a message, a log line or a file. Errors
name the database, the host token and the port — never the URL, unless it has
been rendered through `redact`.
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy.engine import make_url

DEFAULT_POSTGRESQL_PORT = 5432

#: Every form that reaches a PostgreSQL server on this host normalises to this
#: single token: no host at all (libpq's default Unix-domain socket), an
#: explicit socket directory, and the loopback names and addresses. They are
#: collapsed deliberately. Two of them may in principle be different clusters,
#: but treating them as the same identity is the conservative direction: it can
#: only ever cause a destructive operation to be *refused*, never allowed.
LOCAL_HOST_TOKEN = "local"

LOOPBACK_HOSTS = frozenset(
    {"localhost", "127.0.0.1", "::1", "[::1]", "0:0:0:0:0:0:0:1"}
)


class TargetLocality(Enum):
    """How a resolved target would be reached — not merely where it appears to be.

    The distinction the previous guard did not make: `UNIX_SOCKET` is a file on
    this host and cannot be a tunnel to another machine, whereas `TCP_LOOPBACK`
    is an address on this host that an SSH local port forward, a pooler or any
    other proxy can bind while the server lives elsewhere.
    """

    UNIX_SOCKET = "the local Unix-domain socket"
    TCP_LOOPBACK = "TCP loopback"
    REMOTE = "a remote TCP host"


class ConnectionPolicy(Enum):
    """How strictly a target must prove it is the PostgreSQL server on this host.

    `UNIX_SOCKET_ONLY` is required for every destructive or schema-changing
    workflow — online migrations, the destructive test fixtures, the
    backup/restore drill — because those create, drop and destroy, and a TCP
    connection cannot be shown to reach a local server.

    `SOCKET_OR_LOOPBACK` is the weaker check that suits an *ordinary* runtime
    connection, which changes no schema. It proves the target is not a named
    remote host. It does **not** prove the server is on this machine.
    """

    UNIX_SOCKET_ONLY = "unix-socket-only"
    SOCKET_OR_LOOPBACK = "socket-or-loopback"

#: libpq variables that define the target somewhere this process cannot read,
#: so a destructive operation cannot prove where it would connect.
UNRESOLVABLE_LIBPQ_VARIABLES = ("PGSERVICE", "PGSERVICEFILE")

#: libpq variables that fill in whatever the URL leaves unset. They are resolved
#: into the identity rather than ignored, so a hostile `PGHOST` is caught.
#:
#: Each fills in *its own* parameter. `PGHOSTADDR` is the default for `hostaddr`,
#: not a fallback for `host`, so it applies whenever the connection string does
#: not set `hostaddr` — including when the string does set `host`.
INHERITED_LIBPQ_VARIABLES = ("PGHOSTADDR", "PGHOST", "PGPORT", "PGDATABASE")

#: URL query parameters that move the target definition outside this repository,
#: exactly as `PGSERVICE` does. psycopg passes `?service=` straight to libpq, so
#: it is refused for the same reason the variable is.
UNRESOLVABLE_QUERY_PARAMETERS = ("service",)

#: The separator libpq uses for a multi-host (failover) list.
#:
#: A target may be spelled as a list in four places, and every one of them means
#: the connection can land on a server no static check inspected:
#:
#:     ?host=127.0.0.1&host=db.example.org   SQLAlchemy renders a tuple
#:     ?host=127.0.0.1,db.example.org        one comma-separated value
#:     //127.0.0.1,db.example.org/freedom_x  the same list in the URL authority
#:     PGHOST=127.0.0.1,db.example.org       the same list in the environment
#:
#: `docs/operations/database-development.md` documents one loopback-only cluster
#: per environment, and no failover target is approved. So every multi-valued
#: spelling is refused outright rather than partially validated: a target that
#: cannot be reduced to one server and one database is not provable here, and an
#: unprovable target is refused.
MULTI_VALUE_SEPARATOR = ","


class UnsafeDatabaseTargetError(ValueError):
    """A destructive target could not be proven safe.

    A `ValueError` subclass so existing callers that catch `ValueError` around
    configuration validation keep working.
    """


def redact(url: str) -> str:
    """Render a URL with its password replaced, for a message a human will read."""
    try:
        return make_url(url).render_as_string(hide_password=True)
    except Exception:  # pragma: no cover - defensive; never echo the raw URL
        return "<unparsable database URL>"


def _sole_value(value: object, *, field: str, source: str) -> str | None:
    """Collapse a possibly repeated URL query parameter to a single value.

    SQLAlchemy renders `?host=a&host=b` as the tuple `('a', 'b')`. Taking
    `value[0]` and calling the target resolved is precisely the hole this guard
    exists to close, so a repeated parameter is refused instead.
    """
    if isinstance(value, (tuple, list)):
        if not value:
            return None
        if len(value) > 1:
            rendered = ", ".join(repr(str(item)) for item in value)
            raise UnsafeDatabaseTargetError(
                f"{source} is set {len(value)} times ({rendered}). libpq reads a "
                f"repeated {field} as a failover list and may use any entry, so "
                f"the target cannot be proven before connecting. Name exactly "
                f"one {field}."
            )
        value = value[0]
    if value is None:
        return None
    return str(value).strip() or None


def _reject_value_list(value: str | None, *, field: str, source: str) -> str | None:
    """Refuse the comma-separated spelling of the same failover list."""
    if value and MULTI_VALUE_SEPARATOR in value:
        raise UnsafeDatabaseTargetError(
            f"{source} is the list {value!r}. libpq reads a comma-separated "
            f"{field} as a failover list and may use any entry, so the target "
            f"cannot be proven before connecting. Name exactly one {field}."
        )
    return value


def _one_target_component(
    candidates: tuple[tuple[str, str | None], ...],
    *,
    field: str,
    variable: str,
) -> str | None:
    """Fold the several places one URL can name a component into one value.

    A URL may name the host in its authority *and* in a `host=` query parameter,
    and the driver does not use the one a reader would expect:
    `postgresql+psycopg://127.0.0.1/freedom_test?host=db.example.org` connects to
    `db.example.org`. Rather than encode that precedence and trust it to hold
    across drivers and versions, a URL that names one component twice with
    different values is refused as undecidable.

    This is about one component spelled twice. `hostaddr` is **not** a second
    spelling of `host` — it is a separate libpq parameter with its own
    environment default and its own precedence — so it is resolved on its own and
    folded in by `_dialled_target`, not listed as a candidate here.
    """
    present = [(source, value) for source, value in candidates if value]
    if not present:
        return None
    if len({value for _, value in present}) > 1:
        rendered = ", ".join(f"{source} {value!r}" for source, value in present)
        raise UnsafeDatabaseTargetError(
            f"{variable} names more than one {field} ({rendered}). Which one the "
            f"driver connects to is not decidable here, so the target cannot be "
            f"proven. Name exactly one {field}."
        )
    return present[0][1]


def _normalise_host(host: str | None) -> str:
    if host is None:
        return LOCAL_HOST_TOKEN
    stripped = host.strip()
    if not stripped:
        return LOCAL_HOST_TOKEN
    if stripped.startswith("/"):
        return LOCAL_HOST_TOKEN
    lowered = stripped.lower()
    if lowered in LOOPBACK_HOSTS:
        return LOCAL_HOST_TOKEN
    return lowered


def _normalise_address(hostaddr: str) -> str:
    """Collapse a loopback `hostaddr` into the local token, and nothing else.

    Deliberately *not* `_normalise_host`: that treats a leading `/` as the local
    socket, and `hostaddr` is never a socket. A `hostaddr` that looks like a path
    is a misconfiguration libpq will reject, and it must not borrow the local
    token on its way there.
    """
    lowered = hostaddr.strip().lower()
    if lowered in LOOPBACK_HOSTS:
        return LOCAL_HOST_TOKEN
    return lowered


def _address_locality(hostaddr: str) -> TargetLocality:
    """`hostaddr` is an address, and an address is always a TCP connection."""
    if hostaddr.strip().lower() in LOOPBACK_HOSTS:
        return TargetLocality.TCP_LOOPBACK
    return TargetLocality.REMOTE


def _locality(host: str | None) -> TargetLocality:
    """Classify *how* the resolved host would be reached.

    Kept separate from `_normalise_host` on purpose. The host token collapses a
    socket and loopback into one identity so that two URLs naming the same
    database still compare equal; this says which of the two forms was asked
    for, which is what the destructive policy turns on.
    """
    if host is None:
        return TargetLocality.UNIX_SOCKET
    stripped = host.strip()
    if not stripped or stripped.startswith("/"):
        return TargetLocality.UNIX_SOCKET
    if stripped.lower() in LOOPBACK_HOSTS:
        return TargetLocality.TCP_LOOPBACK
    return TargetLocality.REMOTE


def _dialled_target(
    host: str | None,
    hostaddr: str | None,
    *,
    hostaddr_source: str,
    variable: str,
) -> tuple[str, TargetLocality]:
    """Fold libpq's two host parameters into the one target that will be dialled.

    libpq's precedence, not a guess at it: when `hostaddr` is set, it is the
    address the connection is made to and `host` is used only for
    authentication. When it is not set, `host` decides — a socket directory, a
    loopback name, a remote name, or nothing at all, which is libpq's default
    socket directory.

    The one combination that is refused rather than resolved is a **Unix-domain
    socket directory in `host` together with any `hostaddr`**. Precedence alone
    would quietly reclassify it as TCP, and both halves of the target token
    would still read as local for a loopback address — which is exactly how
    `?host=/var/run/postgresql` with an inherited `PGHOSTADDR=127.0.0.1` passed
    as a socket. A socket and an address are different transports, so a
    configuration naming both names no single provable target.
    """
    if hostaddr is None:
        return _normalise_host(host), _locality(host)

    if host is not None and _locality(host) is TargetLocality.UNIX_SOCKET:
        raise UnsafeDatabaseTargetError(
            f"{variable} names the Unix-domain socket directory {host!r}, and "
            f"{hostaddr_source} names the host address {hostaddr!r}. libpq "
            "connects to the host address and uses the host only for "
            "authentication, so this is a TCP connection to "
            f"{hostaddr!r} — the socket directory is never used and the "
            "credentials go to whatever server answers at that address. Remove "
            f"{hostaddr_source} to use the socket, or name a TCP target "
            "explicitly and accept the policy that applies to it."
        )

    return _normalise_address(hostaddr), _address_locality(hostaddr)


@dataclass(frozen=True, slots=True)
class ConnectionIdentity:
    """What a connection string plus its environment actually resolves to.

    Deliberately excludes the username and the password: two URLs that differ
    only in who connects still reach the same database, and a destructive
    operation cares about the database, not the login.

    `locality` is excluded from equality (`compare=False`) for the same reason
    `host` collapses a socket and loopback into one token:
    `postgresql:///freedom_test` and `postgresql://app@127.0.0.1/freedom_test`
    are one database, and a test URL must not be allowed to look distinct from
    the runtime URL merely by choosing the other spelling. Policy reads
    `locality`; identity comparison does not.
    """

    backend: str
    host: str
    port: int
    database: str
    locality: TargetLocality = field(compare=False)

    @property
    def is_unix_socket(self) -> bool:
        return self.locality is TargetLocality.UNIX_SOCKET

    @property
    def is_local(self) -> bool:
        """A socket or a loopback address — *not* proof of a server on this host."""
        return self.host == LOCAL_HOST_TOKEN

    def locality_description(self) -> str:
        """How this target would be reached, named the way a refusal should name it."""
        if self.locality is TargetLocality.REMOTE:
            return f"{self.locality.value}, {self.host!r}"
        return self.locality.value

    def describe(self) -> str:
        """A safe rendering: no username, no password, no full URL."""
        return (
            f"{self.backend} database {self.database!r} over "
            f"{self.locality_description()}, port {self.port}"
        )


def resolve_connection_identity(
    url: str,
    *,
    environ: Mapping[str, str] | None = None,
    variable: str = "DATABASE_URL",
) -> ConnectionIdentity:
    """Resolve `url` against the ambient libpq environment.

    Raises `UnsafeDatabaseTargetError` when the target cannot be determined at
    all — including when it resolves to more than one server or more than one
    database — which is the fail-closed direction for a caller that is about to
    drop something.
    """
    environ = os.environ if environ is None else environ

    for name in UNRESOLVABLE_LIBPQ_VARIABLES:
        if environ.get(name):
            raise UnsafeDatabaseTargetError(
                f"{name} is set, so the connection target for {variable} is defined "
                "outside this repository and cannot be verified before a destructive "
                f"operation. Unset {name} and name the target explicitly."
            )

    try:
        parsed = make_url(url)
    except Exception as error:  # noqa: BLE001 - the message may contain the URL
        raise UnsafeDatabaseTargetError(
            f"{variable} is not a parsable database URL ({type(error).__name__})."
        ) from None

    for name in UNRESOLVABLE_QUERY_PARAMETERS:
        if parsed.query.get(name):
            raise UnsafeDatabaseTargetError(
                f"{variable} sets {name!r}, so the connection target is defined "
                "outside this repository and cannot be verified before a "
                f"destructive operation. Remove {name!r} and name the target "
                "explicitly."
            )

    def query_component(name: str, *, field: str, listable: bool) -> str | None:
        source = f"{variable}'s {name}= parameter"
        value = _sole_value(parsed.query.get(name), field=field, source=source)
        if listable:
            value = _reject_value_list(value, field=field, source=source)
        return value

    # `host` and `hostaddr` are two libpq parameters, not two spellings of one.
    # Each is resolved on its own — URL first, then its own environment default —
    # and only then combined, because `PGHOSTADDR` applies whenever the URL sets
    # no `hostaddr`, *including* when the URL sets `host`. Folding them together
    # here is what let a socket URL inherit a TCP address and still be called a
    # socket.
    host = _one_target_component(
        (
            ("the host= parameter", query_component("host", field="host", listable=True)),
            (
                "the URL authority",
                _reject_value_list(
                    parsed.host, field="host", source=f"{variable}'s URL host"
                ),
            ),
        ),
        field="host",
        variable=variable,
    )
    if host is None:
        host = _reject_value_list(
            environ.get("PGHOST") or None, field="host", source="PGHOST"
        )

    hostaddr = query_component("hostaddr", field="host address", listable=True)
    hostaddr_source = f"{variable}'s hostaddr= parameter"
    if hostaddr is None:
        hostaddr = _reject_value_list(
            environ.get("PGHOSTADDR") or None,
            field="host address",
            source="PGHOSTADDR",
        )
        hostaddr_source = "PGHOSTADDR"

    host_token, locality = _dialled_target(
        host, hostaddr, hostaddr_source=hostaddr_source, variable=variable
    )

    raw_port = _one_target_component(
        (
            ("the port= parameter", query_component("port", field="port", listable=True)),
            (
                "the URL authority",
                str(parsed.port) if parsed.port is not None else None,
            ),
        ),
        field="port",
        variable=variable,
    ) or _reject_value_list(
        environ.get("PGPORT") or None, field="port", source="PGPORT"
    )
    if raw_port is None:
        port = DEFAULT_POSTGRESQL_PORT
    else:
        try:
            port = int(raw_port)
        except ValueError:
            raise UnsafeDatabaseTargetError(
                f"{variable} resolves to a non-numeric port."
            ) from None

    database = _one_target_component(
        (
            ("the dbname= parameter", query_component("dbname", field="database", listable=False)),
            ("the URL path", parsed.database),
        ),
        field="database",
        variable=variable,
    ) or (environ.get("PGDATABASE") or None)
    if not database:
        raise UnsafeDatabaseTargetError(
            f"{variable} names no database, so the destructive target is unknown."
        )

    return ConnectionIdentity(
        backend=parsed.get_backend_name(),
        host=host_token,
        port=port,
        database=database,
        locality=locality,
    )


def require_target_policy(
    identity: ConnectionIdentity,
    *,
    policy: ConnectionPolicy,
    subject: str,
) -> None:
    """Apply `policy` to an already-resolved target, or refuse.

    `subject` names what is being validated (a variable, or an environment and
    its variable) and appears at the front of the refusal message. It must never
    be a raw URL: these messages are read by humans and printed by scripts.
    """
    if policy is ConnectionPolicy.UNIX_SOCKET_ONLY:
        if identity.is_unix_socket:
            return
        raise UnsafeDatabaseTargetError(
            f"{subject} must be local to this host and must connect through the "
            "PostgreSQL Unix-domain socket (no host at all, or an absolute socket "
            f"directory); it resolves to {identity.locality_description()}. A TCP "
            "connection cannot be shown to reach a PostgreSQL server on this "
            "machine: an SSH local port forward, a pooler or any proxy can bind "
            "127.0.0.1:5432 here and carry the session to a remote server, which "
            "then reports loopback addresses of its own. Destructive and "
            "schema-changing operations therefore require the socket."
        )

    if not identity.is_local:
        raise UnsafeDatabaseTargetError(
            f"{subject} must be loopback-only on this shared host; it resolves to "
            f"host {identity.host!r}."
        )


def assert_disposable_target(
    url: str,
    *,
    expected_database: str,
    runtime_url: str | None = None,
    environ: Mapping[str, str] | None = None,
    variable: str = "TEST_DATABASE_URL",
    policy: ConnectionPolicy = ConnectionPolicy.UNIX_SOCKET_ONLY,
) -> ConnectionIdentity:
    """Refuse anything but the local, disposable database named `expected_database`.

    Checks, in order: the target resolves at all; it is PostgreSQL; it is the
    expected disposable database; it satisfies `policy`; and it is not the same
    database the runtime is configured to use, compared by resolved identity
    rather than by string.

    `policy` defaults to `UNIX_SOCKET_ONLY` because every caller of this function
    is about to drop tables, and a TCP loopback URL cannot be distinguished from
    a forwarded port. A caller that genuinely only reads must say so explicitly.
    Passing the static check is necessary and not sufficient: the caller must
    still run `verify_connected_unix_socket_target` on the connection it will
    use.
    """
    identity = resolve_connection_identity(url, environ=environ, variable=variable)

    if not identity.backend.startswith("postgresql"):
        raise UnsafeDatabaseTargetError(
            f"{variable} must use PostgreSQL, not {identity.backend!r}."
        )
    if identity.database != expected_database:
        raise UnsafeDatabaseTargetError(
            f"{variable} must name the disposable database {expected_database!r}, "
            f"not {identity.database!r}."
        )
    require_target_policy(identity, policy=policy, subject=variable)

    if runtime_url:
        runtime_identity = resolve_connection_identity(
            runtime_url, environ=environ, variable="DATABASE_URL"
        )
        if runtime_identity == identity:
            raise UnsafeDatabaseTargetError(
                f"{variable} and DATABASE_URL resolve to the same database "
                f"({identity.describe()}); these operations drop every table."
            )

    return identity


CONNECTED_TARGET_QUERY = """
SELECT current_database() AS database_name,
       inet_server_addr() IS NULL AND inet_client_addr() IS NULL AS unix_socket,
       COALESCE(host(inet_server_addr()), '') AS server_address,
       COALESCE(host(inet_client_addr()), '') AS client_address
"""


def verify_connected_unix_socket_target(connection, *, expected_database: str) -> None:
    """Ask the server where this connection landed, before any DDL runs.

    The static checks reason about strings and environment variables. This one
    reasons about the live connection, so it also catches what no amount of URL
    parsing can: a `localhost` remapped in `/etc/hosts`, a `PGHOST` the caller
    never inspected, or a failover target that chose its second host.

    Both halves of the target are checked, and the second half is strict:

    - `current_database()` really is `expected_database`; and
    - the connection really is a **Unix-domain socket** — `inet_server_addr()`
      and `inet_client_addr()` both null.

    A loopback TCP connection is refused rather than accepted. The addresses of
    a TCP connection prove nothing about locality: an SSH local port forward
    delivers the session to a remote server, and that server answers with
    loopback at both ends exactly as a local one would. A Unix socket is a file
    on this host, which a TCP tunnel cannot present.

    Callers that create or drop objects must run this on the *same* connection
    those statements will use. Validating one connection and running DDL on
    another proves nothing.
    """
    database_name, unix_socket, server_address, client_address = connection.exec_driver_sql(
        CONNECTED_TARGET_QUERY
    ).one()

    if database_name != expected_database:
        raise UnsafeDatabaseTargetError(
            f"The connection landed in database {database_name!r}, not the "
            f"expected {expected_database!r}. Refusing to continue."
        )
    if not unix_socket:
        raise UnsafeDatabaseTargetError(
            f"The connection to {expected_database!r} is not a PostgreSQL "
            f"Unix-domain socket: the server reports address {server_address!r} "
            f"and the client {client_address!r}. A TCP connection — including one "
            "whose addresses are loopback — cannot be distinguished from a "
            "forwarded port or a proxy to a server on another machine. Refusing "
            "to continue."
        )
