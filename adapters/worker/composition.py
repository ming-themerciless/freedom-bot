"""The worker's composition root: one settings graph, one engine, one store.

The same discipline the web composition root established, for the second
process. In particular:

**One process-lifetime settings authority.** `WorkerComposition` takes the
canonical settings graph and canonicalises it again through
`canonical_web_settings`, so every number it uses is one read of a validated
field. It reads **no** environment variable of its own, builds no second engine,
and constructs no identity provider at all — a worker has no browser, no session
and no OAuth flow, so a provider here would be an authority nobody asked for.

**No Google dependency enters this runtime.** The worker imports the Foundry
snapshot path and the Phase 3 identity tables. It does not import
`connectors/sheets.py`, `application/sheet_import.py` or anything under
`adapters/sheets/`, and a structural test asserts that rather than this paragraph.

**S-11 in the other direction.** The web process refuses to start with
`WORKER_ENABLED=true`; this composition refuses to start with it false. Both
processes run the same code from the same virtualenv, and the one variable that
distinguishes them refuses the mistake in whichever direction it is made.

## N-54's pool, as constants

`pool_size=2, max_overflow=0, statement_timeout=120s` is the accepted worker pool
(N-54), and unlike N-53's web pool it has no settings type and no environment
variable — the register defines it once. It is written here as named constants
citing the policy rather than as an operator-tunable value, for the same reason
N-46's preview window and N-24's retention are constants: inventing a variable
would make an accepted number an operator's to weaken.

The 120-second statement timeout is deliberately far above the web process's ten:
the apply transaction is the only long statement in the platform, and bounding it
at the web value would abort exactly the commit this process exists to make.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from sqlalchemy import Connection, Engine, create_engine

from adapters.artifacts.filesystem import FilesystemArtifactStore, TrustedAncestors
from adapters.database.unit_of_work import SqlAlchemyUnitOfWork
from adapters.web.repositories import (
    AccountRepository,
    MembershipProjectionRepository,
    ReconciliationJobRepository,
    RoleMappingRepository,
    SnapshotReadRepository,
    WebAuditRepository,
)
from application.foundry.import_service import SnapshotImportService
from application.web.config import (
    ConfigurationError,
    ConfigurationProblem,
    WebSettings,
    WorkerSettings,
    canonical_settings,
    canonical_web_settings,
)
from application.worker.authorization import WorkerAuthorizationPort
from application.worker.execution import JobExecutor
from domain.foundry import OBSERVED_DEPLOYMENT, SupportedDeployment
from domain.foundry_profile import PROFILE as FIELD_PROFILE

#: N-54. The worker's pool, and the one long statement timeout in the platform.
WORKER_POOL_SIZE = 2
WORKER_MAX_OVERFLOW = 0
WORKER_STATEMENT_TIMEOUT_MS = 120_000


@dataclass(frozen=True, slots=True)
class JobServices:
    """Every repository the worker needs, bound to one connection.

    A frozen record rather than a bag of positional arguments, so a caller that
    reaches for something the worker has no business touching — a session, a
    credential, an OAuth transaction — finds it is not here.
    """

    accounts: AccountRepository
    membership: MembershipProjectionRepository
    mappings: RoleMappingRepository
    snapshots: SnapshotReadRepository
    jobs: ReconciliationJobRepository
    audit: WebAuditRepository


class WorkerComposition:
    """Holds the worker's process-lifetime objects and builds its per-job ones."""

    __slots__ = (
        "_settings",
        "_worker",
        "_engine",
        "_owns_engine",
        "_artifacts",
        "_deployment",
        "_closed",
    )

    def __init__(
        self,
        settings: WebSettings,
        *,
        engine: Engine | None = None,
        deployment: SupportedDeployment = OBSERVED_DEPLOYMENT,
        ancestors: TrustedAncestors | None = None,
    ) -> None:
        self._settings = canonical_web_settings(settings)
        # Read once, into an exact base type, before anything uses a number from
        # it. A subclass whose second read answers differently cannot reach the
        # lease, the heartbeat, the attempt cap or the queue bound.
        self._worker = canonical_settings(self._settings.worker, WorkerSettings)
        if not self._worker.enabled:
            raise ConfigurationError(
                [
                    ConfigurationProblem(
                        message=(
                            "must be true in a freedom-worker process. It is the "
                            "one variable that distinguishes this process from "
                            "freedom-web, and a worker started with it false "
                            "would claim no job while appearing to run — the "
                            "mirror image of S-11, which refuses a web process "
                            "that claims jobs."
                        ),
                        variables=("WORKER_ENABLED",),
                        refusal="S-11",
                    )
                ]
            )
        if self._worker.artifact_root is None:
            raise ConfigurationError(
                [
                    ConfigurationProblem(
                        message=(
                            "must name the restricted snapshot artifact store. "
                            "The worker is the process that reads artifacts, so "
                            "without it every job would fail with "
                            "artifact_unavailable — which is a refusal about the "
                            "artifact rather than about the configuration that "
                            "was never set."
                        ),
                        variables=("WORKER_ARTIFACT_ROOT",),
                        refusal="S-12",
                    )
                ]
            )

        self._deployment = deployment
        self._owns_engine = engine is None
        self._engine = engine if engine is not None else self._build_engine()
        try:
            self._artifacts = FilesystemArtifactStore(
                Path(self._worker.artifact_root), ancestors=ancestors
            )
            # Ownership, mode, symlinks, hard links and trusted ancestors, proven
            # at startup rather than on the first job an operator is waiting for.
            self._artifacts.ensure_ready()
        except BaseException:
            if self._owns_engine:
                self._engine.dispose()
            raise
        self._closed = False

    def _build_engine(self) -> Engine:
        return create_engine(
            self._settings.database.url,
            pool_size=WORKER_POOL_SIZE,
            max_overflow=WORKER_MAX_OVERFLOW,
            pool_pre_ping=True,
            connect_args={
                "options": f"-c statement_timeout={WORKER_STATEMENT_TIMEOUT_MS}"
            },
        )

    # -- what the runtime asks for ----------------------------------------
    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def settings(self) -> WebSettings:
        return self._settings

    @property
    def worker(self) -> WorkerSettings:
        return self._worker

    @property
    def artifacts(self) -> FilesystemArtifactStore:
        return self._artifacts

    def jobs(self, connection: Connection) -> ReconciliationJobRepository:
        return ReconciliationJobRepository(
            connection,
            lease_seconds=self._worker.lease_seconds,
            max_attempts=self._worker.max_attempts,
        )

    def audit(self, connection: Connection) -> WebAuditRepository:
        return WebAuditRepository(connection)

    def job_services(self, connection: Connection) -> JobServices:
        return JobServices(
            accounts=AccountRepository(connection),
            membership=MembershipProjectionRepository(connection),
            mappings=RoleMappingRepository(connection),
            snapshots=SnapshotReadRepository(
                connection, profile_version=FIELD_PROFILE.version
            ),
            jobs=self.jobs(connection),
            audit=self.audit(connection),
        )

    def executor(
        self,
        *,
        clock: Callable[[], datetime] | None = None,
        fences: Callable | None = None,
    ) -> JobExecutor:
        """One executor, holding the **existing** Phase 2 import service.

        `SnapshotImportService` is constructed with the same profile, the same
        deployment pin and the same unit-of-work shape the Phase 2 operator path
        uses. There is no second importer, no second field-ownership system and
        no second calculation path — this composition only decides which process
        calls it.

        `fences` builds the apply's commit fence from `(job_id, owner,
        pending_result)`. `None` means the production `JobLeaseFence`, and the
        parameter exists so the race suite can wrap that same fence in explicit
        barriers and drive the interleaving at the commit boundary
        deterministically. It is a seam for *evidence*, not a substitution: what
        the barrier wraps is the production object, and a test that replaced it
        would be proving nothing.

        `pending_result` is the bounded summary and blocked-entry list the run
        produced, which the fence writes into `reconciliation_jobs.effect_result`
        in the same statement as `effect_committed_at` — so an effect that becomes
        durable always leaves behind the result a later recovery can publish from
        it, without re-running the attempt.
        """
        from application.worker.runtime import utcnow

        authorization = WorkerAuthorizationPort(
            engine=self._engine,
            services=self.job_services,
            guild_id=self._settings.discord.guild_id,
            clock=clock or utcnow,
            cache_seconds=self._settings.bounds.membership_cache_seconds,
        )
        imports = SnapshotImportService(
            lambda: SqlAlchemyUnitOfWork(self._engine),
            deployment=self._deployment,
            profile=FIELD_PROFILE,
            authorization=authorization,
        )
        return JobExecutor(
            imports=imports,
            artifacts=self._artifacts,
            profile_version=FIELD_PROFILE.version,
            fences=fences,
        )

    # -- lifecycle ---------------------------------------------------------
    def close(self) -> None:
        """Release the artifact store's root descriptor and the owned engine.

        The store holds a directory descriptor for the life of the process — that
        descriptor is what stops a pathname replacement redirecting a read — so
        its lifetime is composition's to end. Idempotent, because a graceful
        shutdown and an exception unwind can both reach it.
        """
        if self._closed:
            return
        self._closed = True
        try:
            self._artifacts.close()
        finally:
            if self._owns_engine:
                self._engine.dispose()

    def __enter__(self) -> "WorkerComposition":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()


__all__ = [
    "WORKER_MAX_OVERFLOW",
    "WORKER_POOL_SIZE",
    "WORKER_STATEMENT_TIMEOUT_MS",
    "JobServices",
    "WorkerComposition",
]
