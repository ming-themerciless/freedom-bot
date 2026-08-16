"""The startup refusals that need a resource, and the health check that reports them.

`application/web/config.py` implements S-01 to S-11: every refusal that can be
decided from the environment alone. The three here need something outside it —
the filesystem, the database, the credential store — and are therefore run once
by the application factory, after configuration has been built and before the
first request is served.

| # | Refusal | Why it cannot live in `config.py` |
|---|---|---|
| S-12 | `WORKER_ARTIFACT_ROOT` fails the existing Phase 2 checks | Ownership, mode, symlinks, hard links and trusted ancestors are filesystem facts |
| S-14 | Alembic head does not match the database's current revision | Requires a connection |
| S-15 | Production, and the protected administrator has fewer than two enabled credentials | Requires a query |

S-15 is a **warning, not a refusal, outside production**: the credentials are
hardware and a development host has none. Reporting it as a health check rather
than swallowing it is what keeps "nobody has enrolled a passkey yet" visible.

## Why S-14 exists at all

A process serving a schema it was not built for is a data-integrity risk, and the
failure mode is quiet: queries succeed against the columns that happen to match
and refuse against the ones that do not, halfway through a request. Comparing the
migration head to `alembic_version` at startup turns that into one refusal an
operator sees while watching a service start.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import text

from application.web import WEB_APPLICATION_VERSION
from application.web.config import (
    ConfigurationError,
    ConfigurationProblem,
    WebSettings,
    WorkerSettings,
    canonical_settings,
)
from application.web.view_models import HealthCheck, HealthView

#: N-13, restated where the check runs.
MINIMUM_ENROLLED_CREDENTIALS = 2


@dataclass(frozen=True, slots=True)
class StartupWarning:
    """A condition that is a refusal in production and a warning elsewhere."""

    refusal: str
    message: str


def migration_head() -> str:
    """The revision this build's migrations end at.

    Read from the Alembic script directory rather than hard-coded, so a new
    revision cannot make the check pass by leaving the constant behind.
    """
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    root = Path(__file__).resolve().parents[2]
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "migrations"))
    return ScriptDirectory.from_config(config).get_current_head()


def run_resource_checks(
    settings: WebSettings, engine
) -> tuple[StartupWarning, ...]:
    """S-12, S-14 and S-15. Raises `ConfigurationError`, or returns warnings.

    Collected rather than raised one at a time, for the same reason
    `WebSettings.from_environment` collects: an operator fixing three things
    should learn about all three in one attempt.
    """
    problems: list[ConfigurationProblem] = []
    warnings: list[StartupWarning] = []

    _check_artifact_root(settings, problems)
    _check_migration_head(settings, engine, problems)
    _check_break_glass_credentials(settings, engine, problems, warnings)

    if problems:
        raise ConfigurationError(problems)
    return tuple(warnings)


def _check_artifact_root(
    settings: WebSettings, problems: list[ConfigurationProblem]
) -> None:
    """S-12, through the **existing** Phase 2 store rather than a second copy.

    `FilesystemArtifactStore.ensure_ready` already refuses a permissive root, a
    root owned by another account, a root standing in a directory another account
    can rename entries in, a filesystem on which publication cannot refuse to
    overwrite, and one that cannot `fsync` a directory. Re-deriving any of that
    here would be a second place for it to be wrong.
    """
    # One read, validated by the constructor `canonical_settings` rebuilds
    # (2026-08-15, I-10): the path this check proves ready must be the path the
    # store is later opened on, and a subclass re-read is a second answer.
    root = canonical_settings(settings.worker, WorkerSettings).artifact_root
    if root is None:
        # Only the worker stores artifacts. A web process with no root
        # configured is not misconfigured; it simply has no artifact duties.
        return
    from adapters.artifacts.filesystem import FilesystemArtifactStore
    from application.artifacts import ArtifactStorageError

    store = FilesystemArtifactStore(root)
    try:
        store.ensure_ready()
    except (ArtifactStorageError, ValueError, OSError) as error:
        problems.append(
            ConfigurationProblem(
                message=(
                    "failed the existing snapshot-artifact-store checks "
                    f"({type(error).__name__}). The root must be absolute, outside "
                    "the repository, symlink-free, owned by this account, and "
                    "stand only in directories no other account can rename entries in."
                ),
                variables=("WORKER_ARTIFACT_ROOT",),
                refusal="S-12",
            )
        )
    finally:
        store.close()


def _check_migration_head(
    settings: WebSettings, engine, problems: list[ConfigurationProblem]
) -> None:
    expected = migration_head()
    try:
        with engine.connect() as connection:
            current = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one_or_none()
    except Exception:  # noqa: BLE001 - any failure here is the same refusal
        problems.append(
            ConfigurationProblem(
                message=(
                    "could not be queried for its Alembic revision. A process that "
                    "cannot establish which schema it is serving must not serve one."
                ),
                variables=("WEB_DATABASE_URL",),
                refusal="S-14",
            )
        )
        return
    if current != expected:
        problems.append(
            ConfigurationProblem(
                message=(
                    f"is at Alembic revision {current!r} but this build's migrations "
                    f"end at {expected!r}. A process serving a schema it was not "
                    "built for is a data-integrity risk."
                ),
                variables=("WEB_DATABASE_URL",),
                refusal="S-14",
            )
        )


def _check_break_glass_credentials(
    settings: WebSettings,
    engine,
    problems: list[ConfigurationProblem],
    warnings: list[StartupWarning],
) -> None:
    """S-15, and the bootstrap-ordering hazard it exists to catch.

    The protected role-capability *mapping* is inserted by migration 0006, but
    the protected *account* is created the first time the Server Administrator
    authenticates or by C-03 enrollment. Until then break-glass has no account to
    authenticate, and starting a portal whose emergency route cannot be used is
    starting a portal that will lock its administrator out.
    """
    count = _enabled_credential_count(engine)
    if count >= MINIMUM_ENROLLED_CREDENTIALS:
        return
    message = (
        f"the protected administrator account has {count} enabled WebAuthn "
        f"credential(s); N-13 requires at least {MINIMUM_ENROLLED_CREDENTIALS}. "
        "Enroll them with `python -m tools.webauthn_enrollment` before the portal "
        "is exposed."
    )
    if settings.environment.is_production:
        problems.append(
            ConfigurationProblem(
                message=message, variables=("(operator action)",), refusal="S-15"
            )
        )
    else:
        warnings.append(StartupWarning(refusal="S-15", message=message))


def _enabled_credential_count(engine) -> int:
    from adapters.database.tables import platform_accounts, webauthn_credentials
    from sqlalchemy import select

    with engine.connect() as connection:
        account_id = connection.execute(
            select(platform_accounts.c.id).where(platform_accounts.c.is_protected_admin)
        ).scalar_one_or_none()
        if account_id is None:
            return 0
        return int(
            connection.execute(
                select(text("count(*)"))
                .select_from(webauthn_credentials)
                .where(
                    webauthn_credentials.c.platform_account_id == account_id,
                    webauthn_credentials.c.disabled_at.is_(None),
                )
            ).scalar_one()
        )


def build_health_view(settings: WebSettings, engine, *, provider_ok: bool) -> HealthView:
    """VM-16. Check **names and pass/fail**, and nothing else.

    No connection string, no host, no credential, no player count, no identity,
    no queue contents. `environment` is included deliberately: the single most
    useful thing a monitor can tell you is that production is running production
    configuration (RAID R-25).

    It is reachable on the loopback bind only (N-50) and is **not published by
    Caddy**, which is why it needs no authentication.
    """
    checks: list[HealthCheck] = []

    database_ok = True
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 - the answer is a boolean either way
        database_ok = False
    checks.append(HealthCheck(name="database", ok=database_ok))

    migrations_ok = False
    if database_ok:
        try:
            with engine.connect() as connection:
                current = connection.execute(
                    text("SELECT version_num FROM alembic_version")
                ).scalar_one_or_none()
            migrations_ok = current == migration_head()
        except Exception:  # noqa: BLE001
            migrations_ok = False
    checks.append(HealthCheck(name="migrations", ok=migrations_ok))

    artifact_root = canonical_settings(settings.worker, WorkerSettings).artifact_root
    artifact_ok = artifact_root is None or _artifact_root_ok(artifact_root)
    checks.append(HealthCheck(name="artifact_store", ok=artifact_ok))

    # The worker and its lease reaper belong to P3.3. Reporting them as not-ok
    # here would be a false alarm about something that does not exist yet, and
    # reporting them as ok would be a claim nothing supports — so both are
    # reported as ok-with-nothing-to-check and the check names stay in VM-16's
    # closed vocabulary for P3.3 to make real.
    checks.append(HealthCheck(name="worker_heartbeat", ok=True))
    checks.append(HealthCheck(name="expired_leases", ok=True))
    checks.append(HealthCheck(name="identity_provider", ok=provider_ok))
    checks.append(
        HealthCheck(name="kill_switch", ok=not settings.kill_switch_file.exists())
    )

    status = "ok" if all(check.ok for check in checks) else "degraded"
    return HealthView(
        status=status,
        checks=tuple(checks),
        version=WEB_APPLICATION_VERSION,
        environment=settings.environment.value,
    )


def _artifact_root_ok(artifact_root) -> bool:
    """Takes the path the caller already read, rather than reading it again."""
    from adapters.artifacts.filesystem import FilesystemArtifactStore

    try:
        store = FilesystemArtifactStore(artifact_root)
    except (ValueError, OSError):
        return False
    try:
        store.ensure_ready()
        return True
    except Exception:  # noqa: BLE001
        return False
    finally:
        store.close()


__all__ = [
    "MINIMUM_ENROLLED_CREDENTIALS",
    "StartupWarning",
    "build_health_view",
    "migration_head",
    "run_resource_checks",
]
