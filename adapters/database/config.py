from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from adapters.database.safety import (
    ConnectionIdentity,
    ConnectionPolicy,
    UnsafeDatabaseTargetError,
    require_target_policy,
    resolve_connection_identity,
)

EXPECTED_DATABASES = {
    "development": "freedom_dev",
    "test": "freedom_test",
    "staging": "freedom_staging",
    "production": "freedom_production",
}


@dataclass(frozen=True, slots=True)
class DatabaseSettings:
    environment: str
    url: str
    identity: ConnectionIdentity

    @classmethod
    def from_mapping(
        cls,
        values: Mapping[str, str],
        *,
        environment: str,
        variable: str = "DATABASE_URL",
        environ: Mapping[str, str] | None = None,
        policy: ConnectionPolicy = ConnectionPolicy.UNIX_SOCKET_ONLY,
    ) -> DatabaseSettings:
        """Validate a connection target before anything connects to it.

        `environ` is the ambient libpq environment. It is resolved into the
        target rather than ignored, because a URL that omits a host inherits one
        from `PGHOST`, and migrations create and drop tables. `PGHOSTADDR` is
        resolved too, and it applies even to a URL that *does* name a host:
        libpq dials `hostaddr` and keeps `host` only for authentication, so an
        inherited address turns the documented socket URL into a TCP connection.

        `policy` defaults to `UNIX_SOCKET_ONLY` — fail closed — because the only
        caller today is `migrations/env.py`, and a migration changes the schema.
        A TCP loopback URL is refused there: it cannot be distinguished from an
        SSH local port forward to another host's PostgreSQL. A future *runtime*
        consumer that creates and drops nothing may pass
        `ConnectionPolicy.SOCKET_OR_LOOPBACK` explicitly, which checks the target
        is not a named remote host and claims nothing more than that.
        """
        expected_database = EXPECTED_DATABASES.get(environment)
        if expected_database is None:
            raise ValueError(f"Unknown application environment: {environment!r}.")
        url = values.get(variable)
        if not url:
            raise ValueError(f"{variable} is required for {environment}.")

        identity = resolve_connection_identity(url, environ=environ, variable=variable)
        if not identity.backend.startswith("postgresql"):
            raise ValueError(f"{variable} must use PostgreSQL.")
        if identity.database != expected_database:
            raise ValueError(
                f"{environment} must use database {expected_database!r}, "
                f"not {identity.database!r}."
            )
        require_target_policy(
            identity, policy=policy, subject=f"{environment} PostgreSQL ({variable})"
        )
        return cls(environment=environment, url=url, identity=identity)


__all__ = [
    "EXPECTED_DATABASES",
    "ConnectionPolicy",
    "DatabaseSettings",
    "UnsafeDatabaseTargetError",
]
