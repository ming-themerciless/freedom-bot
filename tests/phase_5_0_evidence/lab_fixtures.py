"""A provisioned laboratory over a temporary directory.

Every object the reserved-laboratory mechanism needs — the lock inode, the
laboratory directory, the ledger directory, the recovery parent and a stand-in
PostgreSQL configuration directory — built under `tmp_path` and torn down with
it.

**This is what makes the mechanism testable without provisioning anything.**
C-P5.0-LAB-I authorizes repository changes and local tests and forbids creating
any object under `/run` or `/var/lib`, and the modules under test take their
layout as data for exactly that reason: `provisioning.LABORATORY_LAYOUT` is the
production definition a maintainer approves, and this builds a different one
whose paths are all inside a directory pytest removes.

A fixture is not evidence about `oracle-test`. Nothing here observes the target,
and a file created here says nothing about whether V3, V4, V5, V7 or V9 has ever
been applied — they have not.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.phase_5_0_evidence.execution.descriptors import (
    DescriptorInventory,
    PosixFilesystem,
)
from tools.phase_5_0_evidence.execution.host_lock import LaboratorySession
from tools.phase_5_0_evidence.execution.lifecycle_record import ReservationRecord
from tools.phase_5_0_evidence.execution.recovery_store import (
    ConfigurationCaptureSet,
    RecoveryStore,
)
from tools.phase_5_0_evidence.execution.run_ledger import ParticipantRunLedger
from tools.phase_5_0_evidence.lifecycle_storage import Participant
from tools.phase_5_0_evidence.provisioning import LaboratoryLayout

#: The host and approved target every fixture binds to. They are the strings the
#: contract uses, and they are compared exactly: a record naming another host or
#: another target is evidence about something else.
HOST = "oracle-test"
TARGET_IDENTITY = "oracle-test"
#: Another approved target, for the cross-target refusals. A history for the same
#: hostname is not a history for another approved target — R3-3.
OTHER_TARGET = "oracle-test-rebuild"

ATTESTER = "peter duscha, operations owner"
BASIS = "the host was rebuilt from a fresh image on 2026-09-13"
AT = "2026-09-13T08:00:00Z"


@dataclass(frozen=True, slots=True)
class Laboratory:
    """A provisioned laboratory and the paths a test needs to reach into it."""

    layout: LaboratoryLayout
    root: Path

    @property
    def laboratory_directory(self) -> Path:
        return Path(self.layout.laboratory_directory)

    @property
    def runs_directory(self) -> Path:
        return self.laboratory_directory / self.layout.runs_directory_name

    @property
    def record_path(self) -> Path:
        return self.laboratory_directory / self.layout.record_name

    @property
    def recovery_directory(self) -> Path:
        return Path(self.layout.recovery_directory)

    @property
    def lock_path(self) -> Path:
        return Path(self.layout.lock_path)

    @property
    def configuration_directory(self) -> Path:
        return self.root / "pgconf"

    def session(
        self,
        participant: Participant = Participant.HARNESS_CLI,
        *,
        target_identity: str = TARGET_IDENTITY,
        reservation_id: str = "",
        read_by: str = "the harness",
        read_at: str = AT,
    ) -> LaboratorySession:
        return LaboratorySession(
            participant=participant,
            host=HOST,
            target_identity=target_identity,
            read_by=read_by,
            read_at=read_at,
            layout=self.layout,
            reservation_id=reservation_id,
        )


def build_laboratory(root: Path, *, with_lock: bool = True) -> Laboratory:
    """Create the five provisioned objects under `root`.

    `with_lock=False` leaves the lock inode absent, which is what an
    unprovisioned host looks like to a participant — and which every participant
    refuses on rather than creating.
    """
    laboratory = root / "var" / "laboratory"
    laboratory.mkdir(parents=True)
    (laboratory / "runs").mkdir()
    (root / "var" / "recovery").mkdir(parents=True)
    run_directory = root / "run"
    run_directory.mkdir()
    if with_lock:
        (run_directory / "laboratory.lock").write_bytes(b"")
    configuration = root / "pgconf"
    configuration.mkdir()
    (configuration / "pg_hba.conf").write_bytes(b"local all all peer\n")
    (configuration / "pg_ident.conf").write_bytes(b"# ident map\n")
    return Laboratory(
        layout=LaboratoryLayout(
            laboratory_directory=str(laboratory),
            runs_directory_name="runs",
            record_name="lifecycle.json",
            recovery_directory=str(root / "var" / "recovery"),
            lock_path=str(run_directory / "laboratory.lock"),
        ),
        root=root,
    )


@dataclass(frozen=True, slots=True)
class Bound:
    """An open inventory and the four objects built over it.

    `close()` releases every descriptor. It is a plain object rather than a
    context manager so a test can hold it across an explicit close and assert
    what a closed inventory refuses.
    """

    inventory: DescriptorInventory
    filesystem: PosixFilesystem
    record: ReservationRecord
    ledger: ParticipantRunLedger

    def close(self) -> None:
        self.inventory.close()


def bind(lab: Laboratory, *, target_identity: str = TARGET_IDENTITY) -> Bound:
    """Hold the laboratory and ledger directories and build the two stores."""
    inventory = DescriptorInventory()
    laboratory = inventory.open_provisioned_root(
        "laboratory", lab.layout.laboratory_directory
    )
    runs = inventory.adopt_directory(
        parent_role="laboratory", name=lab.layout.runs_directory_name, role="runs"
    )
    filesystem = PosixFilesystem(inventory)
    return Bound(
        inventory=inventory,
        filesystem=filesystem,
        record=ReservationRecord(
            filesystem=filesystem,
            directory_object_id=laboratory.identity.object_id,
            name=lab.layout.record_name,
            host=HOST,
            target_identity=target_identity,
        ),
        ledger=ParticipantRunLedger(
            filesystem=filesystem,
            directory_object_id=runs.identity.object_id,
            host=HOST,
            target_identity=target_identity,
        ),
    )


#: The fixture laboratory's reviewed configuration components. They are the two
#: files `targets.POSTGRES_CONFIG_FILES` names, under the fixture's stand-in
#: configuration directory rather than the target's.
REVIEWED_CAPTURE_COMPONENTS = ("pg_hba.conf", "pg_ident.conf")


def capture_set(lab: Laboratory) -> ConfigurationCaptureSet:
    """The reviewed capture set for this laboratory — **PR-20260913-LABI-1**.

    It is built here, at the fixture's integration boundary, for the same reason
    production builds it at the CLI's: the set is a property of the reviewed
    target, and a publication that let its caller choose one is the defect the
    finding reproduced.
    """
    return ConfigurationCaptureSet(
        directory=str(lab.configuration_directory),
        components=REVIEWED_CAPTURE_COMPONENTS,
    )


def recovery_store(lab: Laboratory, bound: Bound) -> RecoveryStore:
    """A recovery store over the fixture's parent, with the configuration held.

    The reviewed capture set is bound here. A store this function returns will
    publish the two reviewed components to their two reviewed destinations and
    refuse every other request.
    """
    bound.inventory.open_provisioned_root("pgconf", str(lab.configuration_directory))
    store = RecoveryStore(
        inventory=bound.inventory,
        filesystem=bound.filesystem,
        parent_path=lab.layout.recovery_directory,
        capture_set=capture_set(lab),
    )
    store.open_parent()
    return store


__all__ = [
    "AT",
    "ATTESTER",
    "BASIS",
    "HOST",
    "OTHER_TARGET",
    "REVIEWED_CAPTURE_COMPONENTS",
    "TARGET_IDENTITY",
    "Bound",
    "Laboratory",
    "bind",
    "build_laboratory",
    "capture_set",
    "recovery_store",
]
