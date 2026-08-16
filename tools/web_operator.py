"""Shared plumbing for the portal's host-local operator commands.

The four commands in `tools/` that administer emergency access — C-01, C-02,
C-03 and C-07 — all need the same three things, and each of the three is a
control rather than a convenience:

1. **A validated database target.** They reach the same `adapters/database`
   validator every other database entry point uses, so a command cannot be
   pointed at production by an inherited `PGHOST` any more than a migration can.
2. **A named operator.** Every audit record these commands write says *who* ran
   it. An emergency action attributed to "the system" is an emergency action
   nobody can be asked about afterwards.
3. **Host authority, and no HTTP.** None of these is exposed as a route (route
   contract §1, §8; TC-BG-10). That is the whole boundary of ADR 0010 D8: the
   recovery path requires existing host authority and cannot be reached from the
   internet. A remote API protected by an API key would convert "an attacker
   needs host access" into "an attacker needs one secret", and that secret would
   live in a file on this host anyway.
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

from sqlalchemy import Engine, create_engine

from adapters.database.config import DatabaseSettings
from adapters.database.safety import ConnectionPolicy, UnsafeDatabaseTargetError

EXIT_OK = 0
EXIT_REFUSED = 1
EXIT_UNSAFE_TARGET = 2
EXIT_CANNOT_CONNECT = 3
EXIT_USAGE = 4

#: The variable these commands read. They deliberately use the **web** process's
#: database URL rather than the bot's: they administer the portal's credentials,
#: and an operator who has only the bot's configuration to hand should be told
#: so rather than silently connect somewhere.
DATABASE_VARIABLE = "WEB_DATABASE_URL"
ENVIRONMENT_VARIABLE = "WEB_ENVIRONMENT"


@dataclass(frozen=True, slots=True)
class TargetRefused(Exception):
    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.message


def resolve_engine(environ: Mapping[str, str] | None = None) -> Engine:
    """Validate the target, then connect. **In that order**, and it matters.

    Establishing a connection is what sends the credentials, so an unsafe target
    has to be refused during *resolution* rather than after. The same reasoning
    the migration guards already carry, reused rather than re-derived.
    """
    values = dict(environ if environ is not None else os.environ)
    environment = values.get(ENVIRONMENT_VARIABLE, "development")
    try:
        settings = DatabaseSettings.from_mapping(
            values,
            environment=environment,
            variable=DATABASE_VARIABLE,
            policy=ConnectionPolicy.SOCKET_OR_LOOPBACK,
        )
    except (ValueError, UnsafeDatabaseTargetError) as error:
        raise TargetRefused(str(error)) from error
    return create_engine(settings.url, pool_pre_ping=True)


def require_operator(name: str | None) -> str:
    """Every emergency action names a human. There is no default."""
    if not name or not name.strip():
        raise TargetRefused(
            "--operator is required: an emergency action attributed to nobody is "
            "an emergency action nobody can be asked about."
        )
    if len(name) > 120:
        raise TargetRefused("--operator is at most 120 characters.")
    return name.strip()


__all__ = [
    "DATABASE_VARIABLE",
    "ENVIRONMENT_VARIABLE",
    "EXIT_CANNOT_CONNECT",
    "EXIT_OK",
    "EXIT_REFUSED",
    "EXIT_UNSAFE_TARGET",
    "EXIT_USAGE",
    "TargetRefused",
    "require_operator",
    "resolve_engine",
]
