"""The reservation record of runner contract r6 §§5.4–5.6 and §5.10, on disk.

## What this module adds, and what it deliberately does not

`lifecycle_storage` already carries the whole of the record's meaning: §5.5's
bounded, versioned codec; §5.5's history order rules walked as a state machine
over `reservation.TRANSITIONS`; the derivation that carries stored evidence into
`reservation.validate_lifecycle`; §5.6's publication order and re-seal; and
§5.10's verified-first-use initialization. It carries all of it over an injected
filesystem whose model implementation is a dictionary.

**This module supplies the other implementation of that filesystem and adds no
rule.** It is deliberately thin, and the thinness is the design: r6 §5.13's
closing sentence is that no layer trusts another's input and that the
reservation and participant checks run on both sides of the store. A mechanism
with its own copy of those checks would be a second reader, and a second reader
is a second chance for the two to disagree — which is, in one sentence, R3-1,
R4-1, R4-2 and R5-1.

So what is here is: the binding of a real directory to a real record name, the
initialization entry point with its refusals and recoveries intact, and the
per-entry publication helpers the executor and the operator paths call. The
comparisons, the ordering and the refusal vocabulary are imported.

## Publication, and the one fact a writer legitimately has

§5.6's order is bytes, rename, containing entry — in that order, every time.
Between the rename and the barrier the record is readable and would not survive
a power loss, and **no artefact a reader can consult answers the question**: an
existing name proves a rename happened, and a stored boolean proves only that
somebody wrote a boolean. `PublicationOutcome.barriers` therefore says what this
writer's own calls returned and nothing else, and §5.5's *"no stored durability
flag, in any form"* is intact here as well.

The successor's re-seal is what closes the gap, and it lives in `host_lock`
because it is the reader's obligation rather than the writer's.

## What it does not do

It creates no directory, provisions nothing, and refuses on an absent record
rather than initializing one implicitly: initialization is a separate, named
operation with an operator's attestation in it, and `initialize()` is the only
way out of absent. It starts no process, takes no lock — the caller must already
hold one — and **no participant path here removes a temporary another
publication left**. The one exception is named and attributed:
`remove_publication_temporary` is r6 §6.2's operator recovery for T1, it takes
the `(st_dev, st_ino)` comparison as a required argument, and it removes exactly
the temporary and never the record — *added 2026-09-15, D1 remediation*.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from ..lifecycle_storage import (
    FIRST_USE_RECOVERY,
    PUBLICATION_UNCERTAINTY,
    RESEAL_CONTRACT,
    RESERVATION_KINDS,
    DurableRecordStore,
    EntryKind,
    FirstUseEvidence,
    InitializationOutcome,
    ParsedHistory,
    PublicationOutcome,
    PublicationTemporary,
    RecordEntry,
    TemporaryRemoval,
    initialize_first_use_record,
    parse_history,
)
from ..provisioning import LABORATORY_LAYOUT
from .descriptors import PosixFilesystem

#: The fields each reservation entry kind carries beyond the six common ones,
#: restated here only as the argument names this module's helpers take. The
#: authority is `lifecycle_storage.KIND_FIELDS`, and a disagreement between the
#: two is caught by the codec rather than tolerated: an entry carrying a field
#: outside the kind's set is `MALFORMED` and refuses before a byte is written.
RESERVATION_ENTRY_KINDS = RESERVATION_KINDS


@dataclass(slots=True)
class ReservationRecord:
    """`/var/lib/freedom-blades/laboratory/lifecycle.json`, bound to a directory.

    `directory_object_id` is the identity the descriptor inventory recorded when
    it opened the laboratory directory, so the record is bound to **the object
    the inventory verified** rather than to a pathname re-resolved at each call.
    """

    filesystem: PosixFilesystem
    directory_object_id: str
    host: str
    target_identity: str
    name: str = LABORATORY_LAYOUT.record_name
    label: str = (
        f"{LABORATORY_LAYOUT.laboratory_directory}/{LABORATORY_LAYOUT.record_name}"
    )
    _store: DurableRecordStore | None = field(default=None, init=False)

    @property
    def store(self) -> DurableRecordStore:
        """The shared publication path, over this module's filesystem.

        It is exposed rather than wrapped because `read_and_admit` takes a
        `DurableRecordStore`, and handing it one built here is what makes the
        mechanism's admission the model's admission rather than a second one.
        """
        if self._store is None:
            self._store = DurableRecordStore(
                self.filesystem,
                directory=self.directory_object_id,
                name=self.name,
                label=self.label,
                kinds=RESERVATION_ENTRY_KINDS,
            )
        return self._store

    # -- reading ---------------------------------------------------------------

    def present(self) -> bool:
        """Whether the final name resolves. **A name, not a durability claim.**"""
        return self.store.present()

    def temporary_present(self) -> bool:
        """Whether an interrupted publication left a temporary behind.

        It is reported and never removed **by a participant**. §2.13.2b's
        precedent is that an artifact whose provenance nobody has established is
        named by absolute path for an operator rather than cleaned by the next
        run, and `observe_publication_temporary` is what an operator compares
        before touching either name.
        """
        return self.store.temporary_present()

    def observe_publication_temporary(self) -> PublicationTemporary:
        """r6 §6.2's `(st_dev, st_ino)` comparison over this record's two names.

        Read-only, and it is the same call `read_and_admit` makes: the record's
        admission and the operator's recovery compare the same two names through
        the same function rather than through two that can disagree.
        """
        return self.store.observe_publication_temporary()

    def reseal(self) -> None:
        """§5.6's obligation: `fsync` the containing entry before reading it.

        It needs read and search on the directory and **no write permission on
        anything**, which is what lets an ordinary participant discharge it
        against a root-written record. A failure refuses.
        """
        self.store.reseal()

    def read(self) -> ParsedHistory:
        """Parse the stored bytes under §5.5's bounded schema.

        A refusal returns **no entries at all**. Handing back the prefix that
        parsed is precisely how a truncated history gets read as a shorter one,
        and a shorter history can end on an admitting entry.
        """
        return parse_history(
            self.store.read_record_bytes(),
            permitted_kinds=RESERVATION_ENTRY_KINDS,
            host=self.host,
            target_identity=self.target_identity,
        )

    # -- writing ---------------------------------------------------------------

    def initialize(
        self,
        *,
        approved_host: str,
        approved_target_identity: str,
        evidence: FirstUseEvidence,
        attested_at: str,
        host_previously_used: bool = False,
        fail_at: str = "",
    ) -> InitializationOutcome:
        """§5.10's verified first use — **a provisioning operation**.

        The creator is the operator provisioning the host, as root, out of band.
        It is not the harness and not a participant, and this method exists so
        that the operator's tool and the model run the same code rather than two
        implementations of one rule.

        Every refusal carries its own recovery from `FIRST_USE_RECOVERY`, and
        the dangerous one is `prior_use_not_excluded`: a missing record on a host
        that has been used is **never** reinitialized as first use.
        """
        return initialize_first_use_record(
            self.store,
            host=self.host,
            target_identity=self.target_identity,
            approved_host=approved_host,
            approved_target_identity=approved_target_identity,
            evidence=evidence,
            attested_at=attested_at,
            host_previously_used=host_previously_used,
            fail_at=fail_at,
        )

    # -- the one operator recovery -------------------------------------------

    def remove_publication_temporary(
        self,
        *,
        comparison: PublicationTemporary | None,
        author: str,
        reference: str,
    ) -> TemporaryRemoval:
        """T1's operator recovery — **the only removal this module performs**.

        It is not a participant's path and no admission reaches it: the module's
        standing rule is that it *never removes a temporary another publication
        left*, and this is the one attributed exception r6 §6.2's table names,
        performed by the operator who established what the two names are. The
        comparison is the argument, so an unobserved one cannot reach `unlinkat`.
        """
        return self.store.remove_publication_temporary(
            comparison=comparison, author=author, reference=reference
        )

    def append(
        self,
        *,
        kind: EntryKind,
        author: str,
        at: str,
        fields: Mapping[str, str],
        fail_at: str = "",
    ) -> PublicationOutcome:
        """Append one entry, preserving every prior one verbatim.

        The stored bytes are parsed first and the prior entries are
        re-serialized exactly, so the only difference between the old file and
        the new one is the entry at the end. A stored history that will not
        parse **refuses**: there is nothing to extend, and replacing it would
        substitute a history this writer invented for one nobody read.

        The proposed history is checked **before any byte is written**, so a
        refused append leaves the stored bytes exactly as they were and leaves
        no temporary behind.
        """
        entry = RecordEntry(
            sequence=1,
            kind=kind,
            host=self.host,
            target=self.target_identity,
            author=author,
            at=at,
            fields=dict(fields),
        )
        return self.store.append(
            entry,
            host=self.host,
            target_identity=self.target_identity,
            fail_at=fail_at,
        )

    def admit_reservation(
        self, *, reservation_id: str, author: str, at: str, fail_at: str = ""
    ) -> PublicationOutcome:
        """`admitted` — and it precedes the first effect of any kind."""
        return self.append(
            kind=EntryKind.ADMITTED,
            author=author,
            at=at,
            fields={"reservation": reservation_id},
            fail_at=fail_at,
        )

    def start_running(
        self, *, reservation_id: str, author: str, at: str, fail_at: str = ""
    ) -> PublicationOutcome:
        """`running` — and it precedes the first **mutating** step."""
        return self.append(
            kind=EntryKind.RUNNING,
            author=author,
            at=at,
            fields={"reservation": reservation_id},
            fail_at=fail_at,
        )

    def quarantine(
        self,
        *,
        reservation_id: str,
        reason: str,
        author: str,
        at: str,
        fail_at: str = "",
    ) -> PublicationOutcome:
        """`quarantined` — terminal, and no successor is named.

        An **absent** quarantine record is never an ending: a crash before one
        could be written leaves the previous entry standing, and the previous
        entry refuses.
        """
        return self.append(
            kind=EntryKind.QUARANTINED,
            author=author,
            at=at,
            fields={"reservation": reservation_id, "reason": reason},
            fail_at=fail_at,
        )

    def recovering(
        self,
        *,
        reservation_id: str,
        recovery_owner: str,
        author: str,
        at: str,
        fail_at: str = "",
    ) -> PublicationOutcome:
        """`recovering` — a deadline moves a run here and authorizes nobody."""
        return self.append(
            kind=EntryKind.RECOVERING,
            author=author,
            at=at,
            fields={"reservation": reservation_id, "recovery_owner": recovery_owner},
            fail_at=fail_at,
        )

    def operator_recovered(
        self,
        *,
        recovers: str,
        reference: str,
        author: str,
        at: str,
        fail_at: str = "",
    ) -> PublicationOutcome:
        """`operator_recovered` — an attributed addition, never a revival.

        The quarantine entry stays where it is. The recovery permits a **new**
        reservation; it neither revives nor rewrites the terminal one it
        recovers, and the recovered identity is never reused.
        """
        return self.append(
            kind=EntryKind.OPERATOR_RECOVERED,
            author=author,
            at=at,
            fields={"recovers": recovers, "reference": reference},
            fail_at=fail_at,
        )


__all__ = [
    "FIRST_USE_RECOVERY",
    "PUBLICATION_UNCERTAINTY",
    "RESEAL_CONTRACT",
    "RESERVATION_ENTRY_KINDS",
    "PublicationTemporary",
    "ReservationRecord",
    "TemporaryRemoval",
]
