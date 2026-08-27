"""C-11 and C-12: observe the N-13 credential threshold, below and at it.

One harness serves both A-05 criterion 4a and criterion 4b (SP-27), because the
two differ only in the environment marker and the database, and `S-15` is the
same check in both:

    if settings.environment.is_production:   -> ConfigurationProblem (refusal)
    else:                                    -> StartupWarning

**No socket is ever opened by this module.** `run_resource_checks` is a plain
function (`application/web/startup.py:80`), so the production branch is reached
without uvicorn, without a bind and without a route. That is what makes criterion
4b's pre-exposure observation possible at all, and it is the correction Codex
finding B-1 forced (decision D-o, change-log C-P3.5-U).

## What it will not do

- It refuses any database but the one the requested environment is bound to, by
  handing the target to the application's own settings validator rather than
  re-implementing the rule.
- For `production` it additionally refuses unless the database is **empty of
  real data** and the operator acknowledges it as disposable, and every
  subcommand after `seed` refuses unless this harness's own marker table is
  present. A database this harness did not prepare cannot be operated on.
- It never reads, prints or stores credential material. The synthetic credential
  id and public key are random bytes generated here, never a real authenticator's.
- The secret keys the settings graph requires are generated per invocation with
  `secrets.token_bytes`, so there is no key material in this file and none
  survives the process.

## The criterion-4a defect this harness exposes

Criterion 4a asks for the observation "under `WEB_ENVIRONMENT=staging`" and "on
a **disposable** database". **Those two cannot both hold.** `DatabaseSettings`
binds each environment to exactly one database name (`adapters/database/config.py:66`):
`staging` must be `freedom_staging`, which on this host is the deployed staging
database holding the protected account's two **real** credentials — the very
records 4a says must never be manipulated.

The harness does not paper over this. Ask it for `staging` and it will be refused
by S-01, visibly, which is the correct behaviour to demonstrate. The disposition
of the criterion is recorded as finding **N-10** and is Peter's to decide; it is
not resolved by this code.
"""
from __future__ import annotations

import argparse
import base64
import secrets
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import NullPool

from adapters.database.config import EXPECTED_DATABASES
from application.web.config import (
    PRODUCTION_GUILD_ID,
    PRODUCTION_ORIGIN,
    PRODUCTION_REDIRECT_URI,
    ConfigurationError,
    ProcessRole,
    WebSettings,
)
from application.web.startup import run_resource_checks

#: The environments this harness will operate. `staging` is deliberately absent:
#: see the module docstring and finding N-10.
SUPPORTED_ENVIRONMENTS = ("development", "test", "production")

#: Tables whose emptiness is the strong guard for the `production` target. A real
#: production database cannot be empty here: bootstrap writes audit rows before
#: anybody can sign in.
REAL_DATA_TABLES = (
    "audit_events",
    "characters",
    "character_access",
    "discord_users",
    "sessions",
    "snapshot_imports",
    "foundry_snapshots",
    "reconciliation_jobs",
)

MARKER_TABLE = "breakglass_observation_marker"

#: The operator label written on every synthetic credential, and the value the
#: clear-down matches on. A credential this harness did not create is never
#: touched.
SYNTHETIC_OPERATOR = "sp27-synthetic-observation"


class ObservationRefused(RuntimeError):
    """The harness refused. The message says which guard fired."""


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ephemeral_key() -> str:
    """A 32-byte key, base64, generated per invocation and never recorded.

    Not a secret in any meaningful sense — the process serves no traffic and
    exits — but generated rather than written down so this file contains no key
    material for anyone to copy into somewhere it would matter.
    """
    return base64.b64encode(secrets.token_bytes(32)).decode("ascii")


def database_url_for(environment: str) -> str:
    try:
        return f"postgresql+psycopg:///{EXPECTED_DATABASES[environment]}"
    except KeyError:
        raise ObservationRefused(f"Unknown environment {environment!r}.") from None


def build_settings(environment: str, database_url: str) -> WebSettings:
    """Settings for `environment`, from identifiers only.

    For `production` the origin, redirect URI and guild are the **accepted
    production identifiers** imported from `application.web.config`, where they
    already exist so that S-02 and S-07 can refuse an impostor. They are
    identifiers, not secrets. The client secret is a syntactically valid
    synthetic value that is deliberately not one of the `.env.example`
    placeholders S-07 refuses — and is never the real one.
    """
    if environment == "staging":
        raise ObservationRefused(
            "Refusing 'staging' before connecting to anything. Each environment "
            "is bound to exactly one database name, so a staging-marked "
            f"observation must target {EXPECTED_DATABASES['staging']!r} — which on "
            "this host is the deployed staging database holding the protected "
            "account's two REAL credentials, the records A-05 criterion 4a "
            "forbids manipulating. This harness will not connect to it. The "
            "criterion's disposition is finding N-10 and is the Security "
            "Reviewer's to decide."
        )
    if environment not in SUPPORTED_ENVIRONMENTS:
        raise ObservationRefused(
            f"{environment!r} is not one of {', '.join(SUPPORTED_ENVIRONMENTS)}."
        )
    if environment == "production":
        origin = PRODUCTION_ORIGIN
        redirect = PRODUCTION_REDIRECT_URI
        guild = str(PRODUCTION_GUILD_ID)
    else:
        origin = "https://portal.invalid"
        redirect = "https://portal.invalid/auth/discord/callback"
        guild = "900000000000000001"
    host = origin.split("//", 1)[1]

    values = {
        "WEB_ENVIRONMENT": environment,
        "WEB_PUBLIC_ORIGIN": origin,
        "WEB_ALLOWED_HOSTS": host,
        "WEB_KILL_SWITCH_FILE": f"/tmp/breakglass-observation-{uuid4().hex}",
        "WEB_SECRET_KEY_CSRF": _ephemeral_key(),
        "WEB_SECRET_KEY_CURSOR": _ephemeral_key(),
        "WEB_SECRET_KEY_CLIENT_DIGEST": _ephemeral_key(),
        "WEB_DATABASE_URL": database_url,
        "WEB_PROVIDER_REGISTRY": "discord",
        "WEB_DISCORD_CLIENT_ID": "1234567890",
        "WEB_DISCORD_CLIENT_SECRET": "synthetic-observation-value-not-a-credential",
        "WEB_DISCORD_REDIRECT_URI": redirect,
        "WEB_DISCORD_SCOPES": "identify,guilds.members.read",
        "WEB_DISCORD_GUILD_ID": guild,
        "WEB_BOOTSTRAP_ADMIN_ROLE_ID": "900000000000000002",
        "WEB_WEBAUTHN_RP_ID": host,
        "WEB_TOKEN_ENCRYPTION_KEYS": f"1:{_ephemeral_key()}",
        "WEB_TOKEN_ENCRYPTION_ACTIVE_VERSION": "1",
        "WEB_COOKIE_SECURE": "true",
    }
    return WebSettings.from_environment(values, process=ProcessRole.WEB)


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------


def _table_counts(connection, tables: tuple[str, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for table in tables:
        exists = connection.execute(
            text("SELECT to_regclass(:name)"), {"name": f"public.{table}"}
        ).scalar()
        if exists is None:
            continue
        counts[table] = int(
            connection.execute(text(f"SELECT count(*) FROM {table}")).scalar_one()
        )
    return counts


def assert_disposable(connection, environment: str, *, acknowledged: bool) -> None:
    """Refuse anything that could be a real database.

    The settings graph has already refused a target whose name does not match the
    environment. What it cannot know is whether a correctly-named database is the
    real one, and for `production` that is the whole question.
    """
    if environment != "production":
        return
    if not acknowledged:
        raise ObservationRefused(
            "A production-marked exercise needs --acknowledge-disposable: the "
            "operator's statement that this database was created for SP-27 and "
            "will be dropped at teardown."
        )
    populated = {
        table: count
        for table, count in _table_counts(connection, REAL_DATA_TABLES).items()
        if count
    }
    if populated:
        detail = ", ".join(f"{table}={count}" for table, count in sorted(populated.items()))
        raise ObservationRefused(
            "Refusing to touch this database: it carries rows a disposable SP-27 "
            f"database cannot have ({detail}). A real production database is never "
            "empty of audit history."
        )


def assert_prepared_by_this_harness(connection) -> None:
    marker = connection.execute(
        text("SELECT to_regclass(:name)"), {"name": f"public.{MARKER_TABLE}"}
    ).scalar()
    if marker is None:
        raise ObservationRefused(
            f"This database carries no {MARKER_TABLE}. Only a database prepared "
            "by this harness's `seed` can be operated on."
        )


# ---------------------------------------------------------------------------
# Synthetic state
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CredentialCount:
    enabled: int
    total: int


def _protected_account_id(connection):
    return connection.execute(
        text("SELECT id FROM platform_accounts WHERE is_protected_admin")
    ).scalar_one_or_none()


def count_credentials(connection) -> CredentialCount:
    account_id = _protected_account_id(connection)
    if account_id is None:
        return CredentialCount(enabled=0, total=0)
    row = connection.execute(
        text(
            "SELECT count(*) FILTER (WHERE disabled_at IS NULL), count(*) "
            "FROM webauthn_credentials WHERE platform_account_id = :account"
        ),
        {"account": account_id},
    ).one()
    return CredentialCount(enabled=int(row[0]), total=int(row[1]))


def _assert_no_foreign_credentials(connection) -> None:
    """Never operate on a credential this harness did not create."""
    foreign = connection.execute(
        text(
            "SELECT count(*) FROM webauthn_credentials "
            "WHERE created_by_operator <> :operator"
        ),
        {"operator": SYNTHETIC_OPERATOR},
    ).scalar_one()
    if foreign:
        raise ObservationRefused(
            f"This database holds {foreign} credential(s) this harness did not "
            "create. A-05 criterion 4a forbids manipulating the protected "
            "account's real credentials; refusing before any write."
        )


def seed(connection, *, credentials: int) -> CredentialCount:
    """Create the marker, the protected account and `credentials` synthetic keys."""
    _assert_no_foreign_credentials(connection)
    connection.execute(
        text(
            f"CREATE TABLE IF NOT EXISTS {MARKER_TABLE} ("
            "  created_at timestamptz NOT NULL DEFAULT now(),"
            "  purpose text NOT NULL)"
        )
    )
    connection.execute(
        text(f"INSERT INTO {MARKER_TABLE} (purpose) VALUES (:purpose)"),
        {"purpose": "A-05 criterion 4a/4b observation. Disposable. Drop at teardown."},
    )

    account_id = _protected_account_id(connection)
    if account_id is None:
        account_id = uuid4()
        connection.execute(
            text(
                "INSERT INTO platform_accounts (id, status, is_protected_admin, display_label) "
                "VALUES (:id, 'active', true, :label)"
            ),
            {"id": account_id, "label": "synthetic protected admin (observation)"},
        )

    for _ in range(credentials):
        connection.execute(
            text(
                "INSERT INTO webauthn_credentials "
                "(id, platform_account_id, credential_id, public_key, created_by_operator, nickname) "
                "VALUES (:id, :account, :credential_id, :public_key, :operator, :nickname)"
            ),
            {
                "id": uuid4(),
                "account": account_id,
                # Random bytes. Not a key, not derived from one, and never a real
                # authenticator's identifier.
                "credential_id": secrets.token_bytes(32),
                "public_key": secrets.token_bytes(64),
                "operator": SYNTHETIC_OPERATOR,
                "nickname": "synthetic-observation",
            },
        )
    connection.commit()
    return count_credentials(connection)


def clear(connection) -> None:
    """Remove only what this harness created."""
    assert_prepared_by_this_harness(connection)
    _assert_no_foreign_credentials(connection)
    connection.execute(
        text("DELETE FROM webauthn_credentials WHERE created_by_operator = :operator"),
        {"operator": SYNTHETIC_OPERATOR},
    )
    connection.execute(
        text(
            "DELETE FROM platform_accounts WHERE is_protected_admin "
            "AND display_label = :label"
        ),
        {"label": "synthetic protected admin (observation)"},
    )
    connection.execute(text(f"DROP TABLE IF EXISTS {MARKER_TABLE}"))
    connection.commit()


# ---------------------------------------------------------------------------
# The observation itself
# ---------------------------------------------------------------------------


def observe(settings: WebSettings, engine) -> tuple[str, list[str]]:
    """Call `run_resource_checks` and report what S-15 did.

    Returns `(outcome, lines)` where outcome is `refused` or `passed`. A refusal
    is the expected result below the threshold in production; a pass is the
    expected result at it.
    """
    try:
        warnings = run_resource_checks(settings, engine)
    except ConfigurationError as error:
        lines = [str(error)]
        for problem in getattr(error, "problems", ()):  # pragma: no branch
            lines.append(
                f"  refusal={problem.refusal} variables={','.join(problem.variables)} "
                f"message={problem.message}"
            )
        return "refused", lines
    return "passed", [
        f"  warning refusal={warning.refusal} message={warning.message}"
        for warning in warnings
    ] or ["  no warnings"]


# ---------------------------------------------------------------------------
# Operator entry point
# ---------------------------------------------------------------------------


def _connect(settings: WebSettings):
    return create_engine(settings.database.url, poolclass=NullPool)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.breakglass_observation",
        description=(
            "Observe the N-13 credential threshold below and at it. Opens no "
            "socket and serves no traffic."
        ),
    )
    parser.add_argument(
        "--environment",
        required=True,
        help=(
            "One of "
            + ", ".join(SUPPORTED_ENVIRONMENTS)
            + ". 'staging' is refused with an explanation; see finding N-10."
        ),
    )
    parser.add_argument(
        "--acknowledge-disposable",
        action="store_true",
        help="Required for a production-marked exercise (SP-27).",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    seeder = subcommands.add_parser("seed", help="Create synthetic account and credentials.")
    seeder.add_argument("--credentials", type=int, default=1)
    subcommands.add_parser("count", help="Report enabled and total credentials.")
    subcommands.add_parser("check", help="Run the resource checks and report S-15.")
    subcommands.add_parser("clear", help="Remove only what this harness created.")

    arguments = parser.parse_args(argv)

    try:
        settings = build_settings(
            arguments.environment, database_url_for(arguments.environment)
        )
    except ConfigurationError as error:
        print(f"REFUSED by the application's own settings validator:\n{error}", file=sys.stderr)
        return 1
    except ObservationRefused as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 1

    if arguments.environment == "production" and not arguments.acknowledge_disposable:
        # Checked before a connection is attempted, so the refusal is the first
        # thing that happens rather than the second.
        print(
            "REFUSED: a production-marked exercise needs --acknowledge-disposable: "
            "the operator's statement that this database was created for SP-27 and "
            "will be dropped at teardown.",
            file=sys.stderr,
        )
        return 1

    engine = _connect(settings)
    try:
        with engine.connect() as connection:
            assert_disposable(
                connection,
                arguments.environment,
                acknowledged=arguments.acknowledge_disposable,
            )
            if arguments.command == "seed":
                counts = seed(connection, credentials=arguments.credentials)
            else:
                if arguments.command != "count":
                    assert_prepared_by_this_harness(connection)
                counts = count_credentials(connection)

            print(f"observed at      {_stamp()}")
            print(f"environment      {arguments.environment}")
            print(f"database         {EXPECTED_DATABASES[arguments.environment]}")
            print(f"enabled creds    {counts.enabled} (total {counts.total})")

            if arguments.command == "check":
                print("listener         none — run_resource_checks called directly")
                outcome, lines = observe(settings, engine)
                print(f"outcome          {outcome}")
                for line in lines:
                    print(line)
            elif arguments.command == "clear":
                clear(connection)
                print("cleared          synthetic credentials, account and marker removed")
        return 0
    except ObservationRefused as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 1
    except OperationalError as error:
        # A missing database is the ordinary state before SP-27 step 1 creates
        # it. A page of SQLAlchemy traceback in an evidence transcript helps
        # nobody, and the cause is one line.
        print(
            f"REFUSED: could not connect to "
            f"{EXPECTED_DATABASES[arguments.environment]}: "
            f"{str(error.orig).strip().splitlines()[-1]}",
            file=sys.stderr,
        )
        return 1
    finally:
        engine.dispose()


if __name__ == "__main__":  # pragma: no cover - operator entry point
    raise SystemExit(main())
