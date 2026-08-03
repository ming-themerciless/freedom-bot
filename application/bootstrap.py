"""The one-time supervised bootstrap, and the gate that closes behind it.

Plan §6.5, *bootstrap is one-time*: the supervised path is available only
against an empty/uninitialized Manager dataset, requires an explicit bootstrap
flag and a named supervisor, and disables itself after the first successful
import. Later imports always require current Guild Council authorization.

**This gate covers the first supervised *snapshot* import and nothing else.**
The Sheet-era value bootstrap it also gated was rejected scope under controlled
baseline v1.1 and has been removed: Phase 2 does not migrate Sheet-era state, so
there is no longer anything for a bootstrap to carry over except the identity,
mappings and provenance an ordinary import establishes. What the supervised mode
buys is the *first* import, before any Council member can be authorized against
an empty dataset — which is exactly what plan §6.4 describes.

Three things make that hold, and none of them is "the code remembers":

1. **The dataset is checked, not assumed.** `is_dataset_empty` asks PostgreSQL
   whether any character, mapping or snapshot row exists. A process restart
   cannot reopen the window.
2. **Completion is a row, and the row is a singleton.** `platform_initialization`
   has a boolean primary key constrained to `true`, so a second initialization
   is a primary-key violation rather than a second row. The runtime role cannot
   update, delete or truncate it.
3. **The gate is asked again at apply.** Availability is not a value the caller
   carries from a previous check.

The gate is deliberately *not* an authorization bypass. It permits exactly one
operation — initializing an empty dataset under a named supervisor — and once
that has happened every later import needs a currently authorized Council
member, which is the ordinary path.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID, uuid4

from application.audit import ActorCapability, AuditEvent, AuditSource
from application.authorization import SupervisedBootstrap
from application.repositories import UnitOfWork
from application.snapshots import PlatformInitialization
from domain.field_profile import FieldProfile

BOOTSTRAP_ENTITY = "platform"
BOOTSTRAP_COMPLETED = "bootstrap.completed"
BOOTSTRAP_REFUSED = "bootstrap.refused"


class BootstrapUnavailable(RuntimeError):
    """The supervised bootstrap cannot run, and why."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class BootstrapState:
    available: bool
    reason: str
    initialization: PlatformInitialization | None = None


class BootstrapGate:
    """Answers, from the database, whether the bootstrap may still run."""

    def __init__(
        self,
        unit_of_work_factory: Callable[[], UnitOfWork],
        *,
        profile: FieldProfile,
        correlation_ids: Callable[[], UUID] = uuid4,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._profile = profile
        self._correlation_ids = correlation_ids

    def state(self) -> BootstrapState:
        with self._unit_of_work_factory() as unit_of_work:
            initialization = unit_of_work.initialization.get()
            empty = unit_of_work.initialization.is_dataset_empty()
            unit_of_work.rollback()

        if initialization is not None:
            return BootstrapState(
                available=False,
                reason=(
                    "The Manager was initialized on "
                    f"{initialization.initialized_at} under supervisor "
                    f"{initialization.supervisor!r}. The bootstrap disables "
                    "itself after its first success; later imports require one "
                    "currently authorized Guild Council member."
                ),
                initialization=initialization,
            )
        if not empty:
            return BootstrapState(
                available=False,
                reason=(
                    "The Manager dataset already holds characters, mappings, "
                    "snapshots or history. The supervised bootstrap runs only "
                    "against an uninitialized dataset, so that it can never be "
                    "used to reach an existing one without authorization."
                ),
            )
        return BootstrapState(available=True, reason="The dataset is uninitialized.")

    def require_available(self, *, supervisor: SupervisedBootstrap) -> None:
        """Refuse unless the bootstrap may run right now."""
        state = self.state()
        if not state.available:
            raise BootstrapUnavailable("bootstrap_unavailable", state.reason)
        # Constructing the supervisor already validated the name; naming it here
        # keeps the requirement visible at the call site.
        assert supervisor.supervisor

    def complete(
        self,
        unit_of_work: UnitOfWork,
        *,
        supervisor: SupervisedBootstrap,
        snapshot_checksum: str | None,
        correlation_id: UUID,
    ) -> PlatformInitialization:
        """Close the gate, inside the caller's transaction.

        Written in the *same* transaction as the import it completes, so a
        rolled-back bootstrap leaves the gate open and a committed one closes
        it. There is no window in which the platform is initialized but the
        import that initialized it is not.
        """
        initialization = PlatformInitialization(
            supervisor=supervisor.supervisor,
            profile_version=self._profile.version,
            correlation_id=correlation_id,
            snapshot_checksum=snapshot_checksum,
        )
        unit_of_work.initialization.record(initialization)
        unit_of_work.audit.record(
            AuditEvent(
                action=BOOTSTRAP_COMPLETED,
                entity_type=BOOTSTRAP_ENTITY,
                entity_id="freedom-blades-manager",
                source=AuditSource.IMPORT,
                actor_capability=ActorCapability.SYSTEM,
                correlation_id=correlation_id,
                payload={
                    "supervisor": supervisor.supervisor,
                    "profile_version": self._profile.version,
                    "snapshot_checksum": snapshot_checksum,
                },
            )
        )
        return initialization

    def record_refusal(self, *, reason: str, supervisor: str, code: str) -> UUID:
        """One safe attempted/refused event, in its own transaction."""
        correlation_id = self._correlation_ids()
        with self._unit_of_work_factory() as unit_of_work:
            unit_of_work.audit.record(
                AuditEvent(
                    action=BOOTSTRAP_REFUSED,
                    entity_type=BOOTSTRAP_ENTITY,
                    entity_id="freedom-blades-manager",
                    source=AuditSource.IMPORT,
                    actor_capability=ActorCapability.SYSTEM,
                    correlation_id=correlation_id,
                    payload={
                        "supervisor": supervisor,
                        "refusal_code": code,
                        "reason": reason,
                        "applied": False,
                    },
                )
            )
            unit_of_work.commit()
        return correlation_id
