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

**That sentence described an intention rather than the code until 2026-08-25
(finding F6, correction C2).** The warning was returned, assigned to
`composition.startup_warnings`, and read by nothing: no route, no log line, no
health check. A staging account down to one credential started normally and
answered `/healthz` byte-identically to a healthy two-credential one, permanently.
`build_health_view` now carries `break_glass_credentials`, and the lifespan logs
every warning it is handed, so the sentence above is now two mechanisms rather
than a claim.

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

    # **Made real by P3.3.** Both were reported `ok` with nothing to check while
    # the worker did not exist; the names stayed in VM-16's closed vocabulary for
    # this package to fill in, and it does.
    worker_ok, leases_ok = _worker_liveness(engine, database_ok)
    checks.append(HealthCheck(name="worker_heartbeat", ok=worker_ok))
    checks.append(HealthCheck(name="expired_leases", ok=leases_ok))
    # **A probe's answer, not a literal** (2026-08-24, S-4/S5). The caller
    # performs the bounded, unauthenticated reachability check — it is network
    # work and this function is synchronous — and hands the boolean here. This
    # function has never decided the value and still does not; what changed is
    # that R-10 stopped passing `True` unconditionally, which made the one check
    # an operator consults during a Discord outage report `ok` throughout it.
    checks.append(HealthCheck(name="identity_provider", ok=provider_ok))
    checks.append(
        HealthCheck(name="kill_switch", ok=_kill_switch_absent(settings.kill_switch_file))
    )
    # **F6, corrected 2026-08-25 (C2).** S-15 is a refusal in production and a
    # warning elsewhere, and the warning went nowhere — so the one condition that
    # decides whether the emergency route can be used at all was invisible on
    # exactly the hosts where it is allowed to be false. A-05 A-4 requires
    # `/healthz` to report the shortfall; this is where it reports it.
    #
    # Queried fresh rather than read from the startup warning: a credential
    # retired an hour after startup is the same shortfall, and a health endpoint
    # answering from a snapshot taken at boot would say the portal is ready
    # because it was ready once.
    checks.append(
        HealthCheck(
            name="break_glass_credentials",
            ok=database_ok and _break_glass_ready(engine),
        )
    )

    status = "ok" if all(check.ok for check in checks) else "degraded"
    return HealthView(
        status=status,
        checks=tuple(checks),
        version=WEB_APPLICATION_VERSION,
        environment=settings.environment.value,
    )


def _worker_liveness(engine, database_ok: bool) -> tuple[bool, bool]:
    """The two signals the operational contract §5 asks a monitor to watch.

    Both are **numbers only**: no job id, no requester, no checksum, no queue
    contents. A health endpoint that named the work in flight would be a health
    endpoint that discloses who is importing what to anything that can reach the
    loopback port.

    ## `worker_heartbeat` — is anything claiming work?

    There is no direct answer available. A worker with nothing to do writes
    nothing, and inventing a liveness row would be inventing a fact the process
    could keep writing while wedged.

    The honest observable is the **consequence** of a dead worker: a job that has
    been `queued` for longer than a live worker would have taken to claim it. The
    bound is `N-23 + N-44` — one lease plus one reaper interval — which is the
    same figure the recovery argument uses, and it is deliberately generous: this
    check answers "nothing is draining the queue", not "the worker is healthy".

    An empty queue therefore reports `ok`, and that is stated rather than hidden:
    **this check cannot distinguish an idle worker from an absent one when there
    is no work.** A monitor that needs that distinction watches the systemd unit,
    which is the thing that actually knows.

    ## `expired_leases` — is the reaper running?

    Under the corrected N-43 the reaper is the **only** writer of the expiry
    transition, so a stalled reaper is the one way a job can sit unterminated
    (SM-05). The oldest expired lease should never be older than `N-23 + N-44`;
    if it is, nothing is reaping and a Council member is watching a spinner over
    a job nobody is running.
    """
    from application.web.jobs import REAPER_INTERVAL_SECONDS

    if not database_ok:
        # Nothing can be concluded without the database, and reporting `ok`
        # would be reporting a check that did not run. The database check has
        # already failed, so the status is degraded either way.
        return False, False

    # N-23's exact lease plus N-44's interval. Read from the register's own
    # constants rather than restated, so a change to either moves this too.
    tolerance = LEASE_SECONDS + REAPER_INTERVAL_SECONDS
    try:
        with engine.connect() as connection:
            oldest_queued = connection.execute(
                text(
                    "SELECT EXTRACT(EPOCH FROM max(now() - queued_at)) "
                    "FROM reconciliation_jobs WHERE state = 'queued'"
                )
            ).scalar_one_or_none()
            oldest_expired = connection.execute(
                text(
                    "SELECT EXTRACT(EPOCH FROM max(now() - lease_expires_at)) "
                    "FROM reconciliation_jobs "
                    "WHERE state = 'running' AND lease_expires_at < now()"
                )
            ).scalar_one_or_none()
    except Exception:  # noqa: BLE001 - the answer is a boolean either way
        return False, False

    worker_ok = oldest_queued is None or float(oldest_queued) <= tolerance
    leases_ok = oldest_expired is None or float(oldest_expired) <= tolerance
    return worker_ok, leases_ok


def _break_glass_ready(engine) -> bool:
    """N-13's floor, as a boolean and nothing more.

    A failure to *ask* is reported as not-ready for the same reason `_worker_liveness`
    reports `False` when the database is unreachable: a check that could not run has
    not passed, and "ok" would be an answer this process does not have.

    The count itself never leaves this function. `False` says the portal is not
    ready to be exposed, which is the operator's cue; how many credentials the
    protected administrator holds — one, or none, or none because the account does
    not exist yet — is a detail the enrollment tool states on the host to the
    person running it, and VM-16 has never carried a count of anything.
    """
    try:
        return _enabled_credential_count(engine) >= MINIMUM_ENROLLED_CREDENTIALS
    except Exception:  # noqa: BLE001 - the answer is a boolean either way
        return False


def _kill_switch_absent(kill_switch_file) -> bool:
    """Is the switch absent? **Unreadable counts as engaged** (C35-04, F-13).

    `Path.exists()` raises rather than answering when the process cannot traverse
    the directory, so the unguarded call turned a permissions fault on one path
    into a `500` for the whole endpoint — and a health endpoint that fails closed
    on a permissions fault is least useful exactly when an operator most needs it.

    The guard is deliberately not "unreadable means healthy". If this process
    cannot see the switch, it cannot know the switch is off, and a monitor told
    "ok" by a process that cannot read its own kill switch has been told
    something false. So the check fails, `/healthz` reports `degraded` with
    `kill_switch: false`, and the operator is pointed at a real fault.

    Nothing about the path, the exception or the permissions reaches the response:
    VM-16 carries check names and booleans, and that is all it has ever carried.

    Enforcement is unaffected. This is the health *view*; whether the portal
    refuses traffic is decided by the kill-switch middleware, which is a separate
    reader with its own behaviour.
    """
    try:
        return not kill_switch_file.exists()
    except OSError:
        # PermissionError is the observed case; ENOTDIR, ELOOP and a stale network
        # mount arrive at the same conclusion through the same door.
        return False


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


#: N-23's exact lease, as `WorkerSettings` pins it. Named here so the health
#: tolerance below reads as the policy it is rather than as a magic number.
LEASE_SECONDS = 60

__all__ = [
    "LEASE_SECONDS",
    "MINIMUM_ENROLLED_CREDENTIALS",
    "StartupWarning",
    "build_health_view",
    "migration_head",
    "run_resource_checks",
]
