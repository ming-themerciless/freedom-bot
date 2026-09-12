"""The provisioned laboratory these lifecycle models are exercised in.

One fixture, shared by `test_r3_lifecycle.py` and `test_r4_remediation.py`, so
the two files exercise the **same** arrangement rather than two that could
drift. It creates the two provisioned durable objects contract §5.4 names —
the reservation record and the run-ledger directory — inside an in-memory
`durability_model.SyntheticFilesystem`, and nothing else.

**Nothing here provisions anything and nothing reads a live host.** No path is
created, no mode is set, no identity is added and no host is touched.

The planting helpers write bytes into the model's store **through the model's
own write path and around every writer-side check**. That is deliberate: a safe
writer does not excuse an unsafe reader, so the regressions must be able to hand
a reader a syntactically valid history that a corrected writer would refuse to
produce.
"""
from __future__ import annotations

from typing import Sequence

from tools.phase_5_0_evidence.durability_model import (
    DescriptorMode,
    SyntheticFilesystem,
)
from tools.phase_5_0_evidence.lifecycle_storage import (
    KIND_FIELDS,
    PARTICIPANT_KINDS,
    PARTICIPANT_PROFILES,
    RESERVATION_KINDS,
    CompletionObservation,
    DurableRecordStore,
    EntryKind,
    FirstUseEvidence,
    Participant,
    RecordEntry,
    RunLedger,
    conclude_reservation,
    initialize_first_use_record,
    read_and_admit,
    serialize_history,
)
from tools.phase_5_0_evidence.reservation import (
    LockView,
    ReleaseEvidence,
    ReservationRequest,
    ReservationState,
    ResidueObservation,
)

HOST = "oracle-test"
TARGET = "oracle-test"
OTHER_TARGET = "oracle-test-rebuilt-2026-09-12"
ATTESTER = "peter duscha, operations owner"
#: The reservation a planted harness run is bound to unless a case states its
#: own. It matches `_completed`'s default so a planted valid pair agrees.
DEFAULT_RESERVATION = "RES-1"
BASIS = "the host was rebuilt from a fresh image on 2026-09-11"

# ---------------------------------------------------------------------------
# A provisioned laboratory, and nothing else
# ---------------------------------------------------------------------------


class Laboratory:
    """The two provisioned durable objects the contract needs, and no run state.

    Both directories are created and made durable because both are
    **provisioned**: they exist before any run and survive a reboot. Nothing a
    run writes is made durable here — that is what the sequences under test are
    for.
    """

    def __init__(self, *, host: str = HOST, target: str = TARGET) -> None:
        self.fs = SyntheticFilesystem()
        self.host = host
        self.target = target
        root = self.fs.open_directory(self.fs.root, DescriptorMode.O_PATH, "").number
        root_sync = self.fs.open_directory(
            self.fs.root, DescriptorMode.O_RDONLY, ""
        ).number
        self.directory = self.fs.mkdirat(root, "laboratory")
        self.fs.fsync(root_sync)

        directory_path = self.fs.open_directory(
            self.directory, DescriptorMode.O_PATH, ""
        ).number
        directory_sync = self.fs.open_directory(
            self.directory, DescriptorMode.O_RDONLY, ""
        ).number
        self.runs_directory = self.fs.mkdirat(directory_path, "runs")
        self.fs.fsync(directory_sync)

        self.record = DurableRecordStore(
            self.fs,
            directory=self.directory,
            name="lifecycle.json",
            label="/var/lib/freedom-blades/laboratory",
            kinds=RESERVATION_KINDS,
        )
        self.ledger = RunLedger(
            self.fs,
            directory=self.runs_directory,
            host=host,
            target_identity=target,
        )

    # -- the oracle. Tests may use these; the module may not ----------------

    def record_entry_is_durable(self) -> bool:
        return self.fs.entry_is_durable(
            self.fs.open_directory(
                self.directory, DescriptorMode.O_PATH, ""
            ).number,
            "lifecycle.json",
        )

    def record_is_visible(self) -> bool:
        return self.fs.now().resolve(self.directory, "lifecycle.json") is not None

    # -- the operations a participant performs ------------------------------

    def initialize(self, **overrides):
        fields = {
            "host": self.host,
            "target_identity": self.target,
            "approved_host": self.host,
            "approved_target_identity": self.target,
            "evidence": FirstUseEvidence(
                prior_use_excluded=True, attested_by=ATTESTER, basis=BASIS
            ),
        }
        fields.update(overrides)
        return initialize_first_use_record(self.record, **fields)

    def append(self, kind: EntryKind, *, author: str, at: str, fail_at: str = "", **fields):
        return self.record.append(
            RecordEntry(
                sequence=1,
                kind=kind,
                host=self.host,
                target=self.target,
                author=author,
                at=at,
                fields={name: fields[name] for name in KIND_FIELDS[kind]},
            ),
            host=self.host,
            target_identity=self.target,
            fail_at=fail_at,
        )

    def remove_temporary(self, directory: str, name: str) -> None:
        """An operator removing a reported publication temporary, by name.

        §2.13.2b's precedent is that a leftover temporary is **reported and not
        removed automatically**. It is therefore an attributed operator step in
        the recovery, and it is modelled as one here rather than being cleaned up
        behind a test's back.
        """
        path_fd = self.fs.open_directory(directory, DescriptorMode.O_PATH, "").number
        self.fs.unlinkat(path_fd, name)
        self.fs.fsync(
            self.fs.open_directory(directory, DescriptorMode.O_RDONLY, "").number
        )

    # -- the terminal publications, in the achievable order — R4-3 ----------

    def request(self, reservation_id: str) -> ReservationRequest:
        return ReservationRequest(
            reservation_id=reservation_id,
            owner="root, the executor",
            host=self.host,
            target_identity=self.target,
            requested_at="2026-09-11T10:00:00Z",
            deadline="2026-09-11T14:00:00Z",
            recovery_owner=ATTESTER,
        )

    def release_evidence(self, reservation_id: str, **overrides) -> ReleaseEvidence:
        """Every release observation made. These are **external** observations.

        The run's children, its server-side transactions, its residue and its
        restored configuration are facts about the host, injected here and
        attributable to a named observer, exactly as the six ordinary
        participants' completion conditions are. What r5 stops injecting is the
        *lifecycle's own* facts — the release decision and its publication.
        """
        fields = {
            "reservation_id": reservation_id,
            "target_identity": self.target,
            "lock_held_by": reservation_id,
            "child_processes_ended": True,
            "database_transactions_settled": True,
            "residue": ResidueObservation.empty(
                observed_by="the operator, post-run sweep", searched_at="t3"
            ),
            "configuration_restored": True,
        }
        fields.update(overrides)
        return ReleaseEvidence(**fields)

    def conclude(self, reservation_id: str, run_id: str, **overrides):
        fields = {
            "record": self.record,
            "ledger": self.ledger,
            "request": self.request(reservation_id),
            "current_state": ReservationState.RUNNING,
            "evidence": self.release_evidence(reservation_id),
            "run_id": run_id,
            "author": f"executor {reservation_id}",
            "at": "t4",
            "observed_by": "the operator, post-run sweep",
        }
        fields.update(overrides)
        return conclude_reservation(**fields)

    def begin_harness(self, run_id: str, reservation_id: str, **overrides):
        """Begin the harness's own run, bound to the reservation it owns.

        One helper rather than the argument repeated at every call site, because
        **PR-20260911-R5-1** is exactly what happens when the binding is optional
        somewhere.
        """
        fields = {
            "run_id": run_id,
            "participant": Participant.HARNESS_CLI,
            "author": "root",
            "at": "t1",
            "reservation_id": reservation_id,
        }
        fields.update(overrides)
        return self.ledger.begin(**fields)

    def admit(self, participant: Participant = Participant.HARNESS_CLI, **overrides):
        fields = {
            "participant": participant,
            "record": self.record,
            "ledger": self.ledger,
            "lock": LockView(),
            "host": self.host,
            "target_identity": self.target,
            "read_by": "a fresh process with no prior memory",
            "read_at": "2026-09-11T12:00:00Z",
        }
        fields.update(overrides)
        return read_and_admit(**fields)


def observed(
    participant: Participant, *, unobserved: str = "", **overrides
) -> CompletionObservation:
    """Every **external** completion condition observed, except the one named.

    `unobserved` removes exactly one condition, so a refusal is attributable to
    that condition rather than to an empty observation. Supplying a condition
    the profile does not have is an error rather than a silent no-op.

    **It supplies no lifecycle-owned condition — PR-20260911-R4-3.** The
    harness's two conditions are facts about the reservation it is concluding,
    derived from the release decision and the release publication. This helper
    previously set both to True at t3 while the record still said RUNNING, which
    is what made the successful trace's stated order unreachable and its green
    row meaningless.
    """
    profile = PARTICIPANT_PROFILES[participant]
    observed = {condition: True for condition in profile.external_conditions()}
    if unobserved:
        assert unobserved in observed, unobserved
        observed[unobserved] = False
    fields = {"observed_by": "the operator, post-run sweep", "observed": observed}
    fields.update(overrides)
    return CompletionObservation(**fields)


# ---------------------------------------------------------------------------
# Direct stored-byte input — around the writer, into the reader
# ---------------------------------------------------------------------------


def _write(fs: SyntheticFilesystem, directory: str, name: str, raw: bytes) -> None:
    """Replace one stored object's bytes, durably, through the model's own path.

    What a later reader sees is a record with different bytes at the same name,
    which is what a tamper, a truncating power loss or a writer from an earlier
    revision produces. No writer-side semantic check runs.
    """
    path_fd = fs.open_directory(directory, DescriptorMode.O_PATH, "").number
    if fs.fstatat(path_fd, name) is not None:
        fs.unlinkat(path_fd, name)
    fd = fs.create_file(path_fd, name).number
    fs.write(fd, raw)
    fs.fsync(fd)
    fs.fsync(fs.open_directory(directory, DescriptorMode.O_RDONLY, "").number)


def plant_bytes(
    laboratory: "Laboratory", directory: str, name: str, raw: bytes
) -> None:
    """Store arbitrary bytes at one name, for the unreadable-record cases."""
    _write(laboratory.fs, directory, name, raw)


def plant_record(laboratory: "Laboratory", entries: Sequence[RecordEntry]) -> None:
    """Store a complete reservation history without a writer's approval."""
    _write(laboratory.fs, laboratory.directory, "lifecycle.json", serialize_history(entries))


def plant_run(
    laboratory: "Laboratory", name: str, entries: Sequence[RecordEntry]
) -> None:
    """Store a complete participant run file without a writer's approval."""
    _write(laboratory.fs, laboratory.runs_directory, name, serialize_history(entries))


def reservation_entry(
    laboratory: "Laboratory",
    kind: EntryKind,
    *,
    sequence: int,
    author: str = "executor",
    at: str = "t",
    **fields: str,
) -> RecordEntry:
    return RecordEntry(
        sequence=sequence,
        kind=kind,
        host=laboratory.host,
        target=laboratory.target,
        author=author,
        at=at,
        fields={name: fields[name] for name in KIND_FIELDS[kind]},
    )


def first_use_entry(laboratory: "Laboratory") -> RecordEntry:
    return reservation_entry(
        laboratory, EntryKind.FIRST_USE, sequence=1, author=ATTESTER, at="t0", basis=BASIS
    )


def run_entry(
    laboratory: "Laboratory",
    kind: EntryKind,
    *,
    sequence: int,
    run: str,
    participant: Participant,
    author: str = "ubuntu",
    at: str = "t",
    identity: str | None = None,
    **fields: str,
) -> RecordEntry:
    """One participant-run entry, with the profile's own defaults filled in.

    `reservation` defaults to the shape the participant's profile requires —
    `DEFAULT_RESERVATION` for the harness, empty for the six — so a planted
    **valid** run needs no boilerplate and every mismatch case states its own
    value explicitly. **PR-20260911-R5-1.**
    """
    payload = {
        "run": run,
        "participant": participant.value,
        "identity": (
            identity
            if identity is not None
            else PARTICIPANT_PROFILES[participant].identity
        ),
    }
    if kind is EntryKind.PARTICIPANT_STARTED:
        payload["reservation"] = (
            DEFAULT_RESERVATION
            if PARTICIPANT_PROFILES[participant].lifecycle_owned_conditions
            else ""
        )
    payload.update({name: fields[name] for name in KIND_FIELDS[kind] if name in fields})
    return RecordEntry(
        sequence=sequence,
        kind=kind,
        host=laboratory.host,
        target=laboratory.target,
        author=author,
        at=at,
        fields=payload,
    )
