"""Building the submission application from configuration, once, at startup.

Composition is deliberately in the adapter layer and deliberately in one place.
Application services take their dependencies through constructors and read no
environment variable, so this module is the only thing that knows what
`FREEDOM_SNAPSHOT_ARTIFACT_ROOT` is called — which is what makes the services
testable with a temporary directory and a fake unit of work.

**Everything is validated before the first request, not during one.** An absent
artifact root, an artifact root another account can read, a filesystem that
cannot `fsync` a directory, a malformed principal entry, a malformed browser
origin, an unsupported database target: each raises here, at startup, where an
operator is watching. A misconfiguration discovered on request 1,000 is a
misconfiguration that has been silently half-working, and two of these — the
storage permissions and the durability guarantee — would otherwise be discovered
by the first upload of every active character's mechanics.

**There is no production preview composition, and that is the point.** The
Council preview needs an `AuthorizationPort` that resolves current Discord guild
membership and role, which is Phase 3 work and does not exist. `build_application`
therefore composes no preview service, and the route answers `503
authentication_unavailable`. Tests build their own composition with a test
authorization adapter; there is no environment variable that turns one on in
production, because there is nothing correct for it to turn on.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import Engine, create_engine

from adapters.artifacts.filesystem import FilesystemArtifactStore, TrustedAncestors
from adapters.database.config import DatabaseSettings
from adapters.database.safety import ConnectionPolicy
from adapters.database.unit_of_work import SqlAlchemyUnitOfWork
from adapters.http.cors import CorsPolicy
from adapters.http.credentials import ServicePrincipalRegistry
from adapters.http.wsgi import SnapshotSubmissionApplication
from application.artifacts import ArtifactStorageError
from application.foundry.submission import SnapshotSubmissionService
from domain.foundry import OBSERVED_DEPLOYMENT, SupportedDeployment

#: Absolute path to the restricted artifact store. Required: there is no default,
#: because every default would be a guess about which filesystem should hold
#: every exported Actor's mechanics.
ARTIFACT_ROOT_VARIABLE = "FREEDOM_SNAPSHOT_ARTIFACT_ROOT"


class ConfigurationError(ValueError):
    """The service cannot be composed from this configuration."""


@dataclass(frozen=True, slots=True)
class Composition:
    """What was built, so a caller can serve it and shut it down cleanly."""

    application: SnapshotSubmissionApplication
    engine: Engine
    artifacts: FilesystemArtifactStore
    artifact_root: Path
    principal_ids: tuple[str, ...]
    #: The browser origins permitted to drive a submission. Empty means none,
    #: which is the default and is what a non-browser rehearsal runs with.
    allowed_origins: tuple[str, ...] = ()

    def dispose(self) -> None:
        """Release everything this composition holds open.

        The artifact store holds a directory descriptor for the life of the
        service — that descriptor is what stops a pathname replacement
        redirecting a write (S-B-2) — so its lifetime is composition's to end.
        Closing it here rather than leaving it to the garbage collector is the
        difference between a defined lifecycle and a hope.
        """
        self.artifacts.close()
        self.engine.dispose()


def build_application(
    environ: Mapping[str, str],
    *,
    deployment: SupportedDeployment = OBSERVED_DEPLOYMENT,
    ancestors: TrustedAncestors | None = None,
) -> Composition:
    """Compose the submission endpoint, or refuse to start.

    `ancestors` is a test seam, in the same sense `deployment` is: it bounds the
    startup walk over the directories *above* the artifact root, so that a test
    about descriptor ownership is not also a test about who owns `/` on the
    machine it runs on. **It is read from no environment variable.** Production
    passes nothing and the store walks to `/` — see `TrustedAncestors` and
    `docs/operations/foundry-snapshot-submission.md` §5.6.
    """
    root = (environ.get(ARTIFACT_ROOT_VARIABLE) or "").strip()
    if not root:
        raise ConfigurationError(
            f"{ARTIFACT_ROOT_VARIABLE} must name an absolute directory outside "
            "this repository for the restricted snapshot artifact store. See "
            "docs/operations/foundry-snapshot-submission.md."
        )
    try:
        artifacts = FilesystemArtifactStore(Path(root), ancestors=ancestors)
    except ValueError as error:
        raise ConfigurationError(f"{ARTIFACT_ROOT_VARIABLE} is unusable: {error}") from None
    try:
        # Ownership, mode, type, trusted ancestors and directory-`fsync`
        # support, proven now rather than during the first upload of every
        # active character's mechanics. This is also where the store anchors
        # itself to a root directory descriptor, so a refusal here must not
        # leave one open: `close()` is unconditional.
        artifacts.ensure_ready()
    except ArtifactStorageError as error:
        artifacts.close()
        raise ConfigurationError(
            f"{ARTIFACT_ROOT_VARIABLE} is not usable as restricted storage "
            f"({error.reason}). See docs/operations/foundry-snapshot-submission.md "
            "§5.6 for the required directory state."
        ) from None

    # From here on the store holds a descriptor, so every remaining refusal —
    # a malformed origin, a malformed principal, an unsupported database target
    # — has to release it before the exception leaves this function.
    try:
        cors = CorsPolicy.from_mapping(environ)
        credentials = ServicePrincipalRegistry.from_mapping(environ)

        settings = DatabaseSettings.from_mapping(
            environ,
            environment=environ.get("APP_ENVIRONMENT", "development"),
            environ=environ,
            policy=ConnectionPolicy.SOCKET_OR_LOOPBACK,
        )
        engine = create_engine(settings.url)
    except BaseException:
        artifacts.close()
        raise

    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(engine)

    submissions = SnapshotSubmissionService(
        factory, deployment=deployment, artifacts=artifacts
    )
    return Composition(
        application=SnapshotSubmissionApplication(
            submissions,
            credentials,
            cors=cors,
            # No preview service and no user resolver. See the module docstring:
            # the Phase 3 authentication boundary does not exist, so the route
            # fails closed rather than being served by something invented here.
            preview=None,
            preview_user_resolver=None,
        ),
        engine=engine,
        artifacts=artifacts,
        artifact_root=artifacts.root,
        principal_ids=credentials.principal_ids,
        allowed_origins=cors.origins,
    )
