"""The seven-participant run ledger of r6 §§5.11–5.12, on disk.

## The rule this object exists for

**R3-2.** Revision 3 had one participant writing the reservation record and six
merely serializing on the lock, and drew the consequence out loud: *"a test suite
that crashes leaves no lifecycle record at all … the next suite proceeds."* Those
six include the two database suites, the synchronization, the dependency update
and the environment reset. A synchronization wrapper that dies having replaced
half a tree, or a database suite that dies with a server-side transaction
unsettled, left the previous record unchanged and the next participant took a
free lock and proceeded. Calling the interrupted operation a test rather than a
reservation does not establish that its effects ended.

So **every one of the seven writes its own run entry**: durable in-progress
state *before* its first relevant effect, and durable completion *only after* its
exact completion evidence holds. An unsettled or unreadable run refuses every
successor — the harness and the environment reset included — until a recovery is
published. No exemption is proposed for any participant, and the reset's is
refused **especially**, because it is the one whose effect is the removal of the
evidence an earlier interruption left.

## What is never completion evidence

A free lock, a wrapper's exit status, an elapsed deadline and an absent
quarantine record. Each has produced an incident class in the reviews that led
here, and `lifecycle_storage.NOT_COMPLETION_EVIDENCE` states all four where a
reader of the ledger will see them.

## The reservation binding — R5-1

The `participant_started` entry names the reservation the run owns. It is
published before the run's first effect, it is never rewritten, and it is the
only fact the protocol keeps about which reservation a run belongs to. The
harness carries an identity; the six carry the field **exactly empty**; and the
completion's evidence must name **exactly** the reservation the stored start
owns — equality, both ways, not containment and not presence.

**No filename convention is adopted**, and that is a decision rather than an
omission: a run named `RES-9-harness` and started for `RES-1` belongs to
`RES-1`. A convention would be a second place the binding could be read from,
and a second place is a second chance for the two to disagree.

## What this module adds

The same answer as `lifecycle_record`: the real filesystem, and no second copy
of a rule. `lifecycle_storage.RunLedger` carries §5.11.1's validator applied on
both the writer's and the survey's side, and `conclude_reservation` carries
§5.12's four steps with step 0's binding check ahead of the release decision. A
mechanism with its own participant validator would be the drift R4-2 is about.

## What it does not do

It observes no process, no database backend and no tree. Those are the six
participants' **external** conditions: injected, attributable, and collected in
r6 §9.3's I9 as unconfirmed proof obligations. A validated run history
establishes that somebody stated the right conditions for the right run and was
named doing it; it establishes nothing about the host.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..lifecycle_storage import (
    NOT_COMPLETION_EVIDENCE,
    PARTICIPANT_PROFILES,
    TERMINAL_PUBLICATION_ORDER,
    CompletionObservation,
    Participant,
    PublicationOutcome,
    PublicationTemporary,
    ReleasePublication,
    RunLedger,
    RunLedgerSurvey,
    StoredRun,
    TemporaryRemoval,
    TerminalPublication,
    conclude_reservation,
)
from ..provisioning import LABORATORY_LAYOUT
from ..reservation import ReleaseEvidence, ReservationRequest, ReservationState
from .descriptors import PosixFilesystem
from .lifecycle_record import ReservationRecord


@dataclass(slots=True)
class ParticipantRunLedger:
    """`/var/lib/freedom-blades/laboratory/runs/<run-id>`, one file per run.

    `directory_object_id` is the identity the inventory recorded when it adopted
    the runs directory, so every entry is written relative to a descriptor that
    was verified once rather than to a pathname resolved at each call.
    """

    filesystem: PosixFilesystem
    directory_object_id: str
    host: str
    target_identity: str
    label: str = (
        f"{LABORATORY_LAYOUT.laboratory_directory}/"
        f"{LABORATORY_LAYOUT.runs_directory_name}"
    )
    _ledger: RunLedger | None = field(default=None, init=False)

    @property
    def ledger(self) -> RunLedger:
        """The shared ledger, over this module's filesystem.

        Exposed rather than wrapped for the reason `ReservationRecord.store` is:
        `read_and_admit` and `conclude_reservation` take a `RunLedger`, and
        handing them one built here is what makes the mechanism's accounting the
        model's accounting rather than a second one.
        """
        if self._ledger is None:
            self._ledger = RunLedger(
                self.filesystem,
                directory=self.directory_object_id,
                host=self.host,
                target_identity=self.target_identity,
                label=self.label,
            )
        return self._ledger

    # -- in-progress and completion ------------------------------------------

    def begin(
        self,
        *,
        run_id: str,
        participant: Participant,
        author: str,
        at: str,
        reservation_id: str = "",
        fail_at: str = "",
    ) -> PublicationOutcome:
        """Persist the run's non-reusable state **before its first effect**.

        Exclusive creation, both barriers. The caller issues no effect until
        this returns `published`: a run whose start was never durable is a run
        whose effects nothing accounts for.

        The reservation binding is checked by the same participant validator the
        survey applies, so a harness start with no reservation and a suite start
        carrying one both refuse as an invalid history and write nothing.
        """
        return self.ledger.begin(
            run_id=run_id,
            participant=participant,
            author=author,
            at=at,
            reservation_id=reservation_id,
            fail_at=fail_at,
        )

    def complete(
        self,
        *,
        run_id: str,
        participant: Participant,
        observation: CompletionObservation,
        author: str,
        at: str,
        release_publication: ReleasePublication | None = None,
        fail_at: str = "",
    ) -> PublicationOutcome:
        """Publish completion **only after** the stated conditions are observed.

        The completion profile, the required conditions and the reservation
        written into the evidence all come from the **stored start**. A caller's
        participant, run id and reservation are checked claims: each is compared
        with the stored record, and a disagreement refuses without writing a
        byte.
        """
        return self.ledger.complete(
            run_id=run_id,
            participant=participant,
            observation=observation,
            author=author,
            at=at,
            release_publication=release_publication,
            fail_at=fail_at,
        )

    def recover(
        self,
        *,
        run_id: str,
        participant: Participant,
        reference: str,
        author: str,
        at: str,
        fail_at: str = "",
    ) -> PublicationOutcome:
        """An attributed operator recovery for an interrupted run.

        A crashed run blocks until its recovery is **published**, which is a
        bounded operator action with a named owner rather than an indefinite
        dead end. The recovered run's own identity is never reused.
        """
        return self.ledger.recover(
            run_id=run_id,
            participant=participant,
            reference=reference,
            author=author,
            at=at,
            fail_at=fail_at,
        )

    # -- reading ---------------------------------------------------------------

    def survey(self) -> RunLedgerSurvey:
        """Every run file, validated. **An absent ledger is never an empty one.**

        A leftover publication temporary is reported and not removed, and it
        blocks. A run file that parses and is not a run history is `invalid` and
        blocks exactly as an unsettled run does.
        """
        return self.ledger.survey()

    def read_run(self, run_id: str) -> StoredRun:
        """The validated stored history of one run, for the binding check.

        It is what a writer reads **before** it derives anything: the profile,
        the required conditions and the reservation all come from the stored
        start, and a caller's are checked claims compared with it.
        """
        return self.ledger.read_run(run_id)

    def reseal(self) -> None:
        """§5.6's obligation for the ledger's containing entry."""
        self.ledger.reseal()

    # -- the one operator recovery — r6 §6.2, T6 ------------------------------

    def observe_publication_temporary(self, run_id: str) -> PublicationTemporary:
        """r6 §6.2's `(st_dev, st_ino)` comparison over one run file's names."""
        return self.ledger.observe_publication_temporary(run_id)

    def remove_publication_temporary(
        self,
        run_id: str,
        *,
        comparison: PublicationTemporary | None,
        author: str,
        reference: str,
    ) -> TemporaryRemoval:
        """T6's operator recovery: remove the temporary, settle nothing.

        No participant reaches this and the survey's refusal is unchanged. After
        it the run is visible as started and unsettled, and it still blocks every
        successor until T16's attributed `participant_recovered` settles it.
        """
        return self.ledger.remove_publication_temporary(
            run_id, comparison=comparison, author=author, reference=reference
        )


@dataclass(frozen=True, slots=True)
class TerminalSequence:
    """§5.12's four steps, over a real record and a real ledger.

    | Step | What happens |
    |---|---|
    | **0** | check the reservation binding. A mismatch refuses and **publishes nothing** |
    | 1 | evaluate the release decision — RELEASED, or quarantine |
    | 2 | publish the reservation's `released` entry durably |
    | 3 | publish the harness participant's completion, whose two conditions are exactly the outcomes of steps 1 and 2 |
    | 4 | release the lock — here and nowhere earlier |

    **Why step 0 comes first.** It is the cheapest check and the one whose
    failure is entirely the caller's error. Checking the binding at step 3
    instead would publish RELEASED durably and then refuse the completion,
    leaving a reservation that reads terminal beside a run that can never be
    settled by it — a state needing an operator recovery for a mistake a
    comparison could have caught before any byte was written.

    **Why no half of this authorizes reuse.** Before step 2 the record still
    says `running`, which refuses every successor. Between steps 2 and 3 the
    record says `released` **and** the executor's own run is still
    `participant_started` in the ledger, and an unsettled run refuses every
    successor including the harness and the environment reset. Only after step 3
    do both halves hold.

    Step 4 is the caller's: this object publishes, and `host_lock.HostLock`
    releases. They are kept apart so that releasing the lock cannot be mistaken
    for concluding the reservation.
    """

    record: ReservationRecord
    ledger: ParticipantRunLedger
    order: tuple[str, ...] = TERMINAL_PUBLICATION_ORDER

    def conclude(
        self,
        *,
        request: ReservationRequest,
        current_state: ReservationState,
        evidence: ReleaseEvidence,
        run_id: str,
        author: str,
        at: str,
        observed_by: str,
        fail_release_at: str = "",
        fail_completion_at: str = "",
    ) -> TerminalPublication:
        """Run the sequence. The decision is `conclude_reservation`'s."""
        return conclude_reservation(
            record=self.record.store,
            ledger=self.ledger.ledger,
            request=request,
            current_state=current_state,
            evidence=evidence,
            run_id=run_id,
            author=author,
            at=at,
            observed_by=observed_by,
            fail_release_at=fail_release_at,
            fail_completion_at=fail_completion_at,
        )


def profile_for(participant: Participant):
    """The participant's declared identity and its exact completion conditions."""
    return PARTICIPANT_PROFILES[participant]


__all__ = [
    "NOT_COMPLETION_EVIDENCE",
    "TERMINAL_PUBLICATION_ORDER",
    "ParticipantRunLedger",
    "TerminalSequence",
    "profile_for",
]
