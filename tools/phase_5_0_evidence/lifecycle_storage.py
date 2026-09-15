"""A bounded synthetic model of the proposed **laboratory lifecycle** — one
connected path from provisioning through admission, operation, crash, recovery
and reuse, over records a reader actually parses.

## What it answers

**PR-20260911-R2-4**, carried forward: the seven participants apply one
allowlist of validated lifecycle outcomes, by calling
`reservation.validate_lifecycle()` — *the same function `reservation.admit()`
calls* — and verified first use is modelled as a provisioning operation with its
own refusals and recoveries.

**PR-20260911-R3-1**, the publication/restart gap. Publication renames before it
synchronizes the containing entry, so between those two points the record is
readable and would not survive a power loss, and the only party that knows is
the writer whose memory a restart destroys. `PUBLICATION_UNCERTAINTY` states the
mechanism, `RESEAL_CONTRACT` states the correction — the successor establishes
the entry's durability under the lock, with read permission and no write
permission, or refuses pending an attributable operator recovery — and
`AdmissionPolicy` keeps revision 3's protocol as the negative control.
`SyntheticFilesystem.restart_process()` is the process-only restart, kept
distinct from `crash()`, which is the power loss.

**PR-20260911-R3-2**, every participant's interrupted effects.
`PARTICIPANT_PROFILES` gives all seven an identity, a lifecycle writer, a lock
lifetime, declared effects, completion conditions, a recovery and its
unperformed proof obligations. `RunLedger` is the durable in-progress and
completion accounting: the non-reusable state is persisted before the first
relevant effect, reusable completion is published only after the stated
conditions are observed, and an unsettled or unreadable run refuses **every**
successor including the harness and the environment reset.
`NOT_COMPLETION_EVIDENCE` is the list of things that never end a run.

**PR-20260911-R3-3**, the binding between stored evidence and admission.
`RecordEntry`, `serialize_history` and `parse_history` are a bounded, versioned
record schema; `check_history_semantics` and `HISTORY_ORDER_RULES` are its order
rules; and `derive_lifecycle_history` carries the host, the approved target, the
first-use attester and basis, the release record's author and the recovery's
reference and author out of the stored bytes and into the shared validator. A
malformed, truncated, unsupported, contradictory, missing-binding or
wrong-binding record refuses and is never normalized into a success.

**PR-20260911-R4-1**, the stale terminal entry. `check_reservation_history`
walks the history as a state machine over `reservation.TRANSITIONS` — the
accepted table, not a second one — carrying the **current reservation** and its
current state. A transition naming any other reservation, a transition of a
reservation that already reached a terminal state, a duplicate terminal event, a
reused identity and a repeated operator recovery each refuse, and
`derive_lifecycle_history` reads the current reservation rather than the last
entry. A stale `released A` appended while `B` is running no longer retires B.

**PR-20260911-R4-2**, the unbound participant completion.
`check_participant_history` is the one participant-history validator: it
requires a start, a stable run, participant and identity, the binding to the
file's own name, one terminal entry, and completion evidence whose **content**
names this run, this participant's exact conditions and an observer.
`CompletionEvidence` is that bounded encoding, so an empty or arbitrary string
is not proof. The required conditions come from the **stored start**, never from
the completion caller, and an absent ledger refuses instead of reading as empty.

**PR-20260911-R4-3**, the unreachable terminal order.
`TERMINAL_PUBLICATION_ORDER` states the achievable one — decide, publish
RELEASED, complete the harness's run, release the lock — and
`conclude_reservation` performs it. The harness's two completion conditions are
`lifecycle_owned_conditions`, **derived** from those two operations' own return
values, and an observation that injects one is refused.

**Both checks run on both sides.** `DurableRecordStore` looks its record type's
check up in `HISTORY_SEMANTICS` and applies it to the history it is about to
write, before any byte is written, so an invalid append leaves the stored bytes
intact; every reader applies the same function to the history it read, so a
syntactically valid invalid history refuses even where a corrected writer could
no longer produce one.

## The connected path, and the constructors that are not it

`initialize_first_use_record` → `DurableRecordStore` → `read_and_admit` consumes
the bytes its initializer or predecessor wrote. `UNIT_TEST_CONSTRUCTORS` names
the two helpers that build a `LifecycleHistory` instead of reading one; they are
useful for table-driven unit tests and **a test that uses one is not end to
end**, which is exactly the claim R3-1 and R3-3 found unsupported.

## What it is not

**Nothing here provisions anything, and nothing here reads a live host.** Every
object is created inside the in-memory `durability_model.SyntheticFilesystem`;
no path is created, no mode is set, no identity is added and no host is touched.
The parser parses bytes it is handed. `PROPOSED_PROVISIONING` states the
provisioning delta and every row of it is unapproved.

**No function in this module observes the model's durable-state map.** A reader
that could ask whether an entry is durable would be a reader with an observation
no real participant can make, and giving the model one would hide R3-1 again
rather than model it. The test oracle may look; this module may not, and
`test_r3_lifecycle.py` asserts that against this file's syntax tree.

`MODEL_LIMITS` from `durability_model` is carried in every result: these are
proposal-model observations, not evidence about the target and not authority to
build anything.

## Isolation

Planning tier. No process, no file, no socket, no database, no product import.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Sequence

from .durability_model import (
    MODEL_LIMITS,
    DescriptorMode,
    ModelRefused,
    SyntheticFilesystem,
    digest,
)
from .errors import PlanRefused
from .reservation import (
    PARTICIPATING_ENTRY_POINTS,
    TRANSITIONS,
    VALIDATED_LIFECYCLE_OUTCOMES,
    LifecycleHistory,
    LifecycleValidation,
    LockView,
    PredecessorDisposition,
    QuarantineRecord,
    ReleaseEvidence,
    ReleaseRecord,
    ReservationRequest,
    ReservationState,
    release,
    validate_lifecycle,
)


class Participant(str, Enum):
    """The seven entry points that must serialize on the one cooperative lock.

    They are the keys of `reservation.PARTICIPATING_ENTRY_POINTS`, named here so
    a table-driven check can enumerate them and so a participant added there
    without being considered here fails a test rather than being skipped.
    """

    BOT_SUITE = "tests/test_*.py (bot suite)"
    WEB_SUITE = "tests/web (web suite)"
    FOUNDRY_TESTS = "foundry-module/tests (node --test)"
    SYNCHRONIZATION = "docs/operations/disposable-test-server.md §3.2 synchronization"
    DEPENDENCY_UPDATE = "docs/operations/disposable-test-server.md §3.5 dependency updates"
    ENVIRONMENT_RESET = "docs/operations/disposable-test-server.md §4 environment reset"
    HARNESS_CLI = "tools/phase_5_0_evidence/execution/cli.py"

    @property
    def writes_the_record(self) -> bool:
        """Only the executor publishes lifecycle state. Six only serialize."""
        return self is Participant.HARNESS_CLI


#: Every participant, in the order the contract lists them.
PARTICIPANTS: tuple[Participant, ...] = tuple(Participant)

#: **The one allowlist, restated where a participant model reads it.** It is
#: `reservation.VALIDATED_LIFECYCLE_OUTCOMES` and not a copy of it: a second list
#: would be a second rule, and a second rule is how the executor and the ordinary
#: participants came to disagree in revision 2.
ADMITTING_OUTCOMES = VALIDATED_LIFECYCLE_OUTCOMES

#: Why a free process lock authorizes nothing, stated for the participant that
#: sees one. `flock(2)` releases a crashed holder's lock when its descriptors
#: close, which is why the lock and the durable record are two objects.
FREE_LOCK_AUTHORIZES_NOTHING = (
    "The cooperative lock is a persistent provisioned inode and the lock is on "
    "the open file description. A crashed holder's lock is released by the "
    "kernel, so a free lock is compatible with a predecessor that never released.",
    "No expiry authorizes reuse. An elapsed deadline moves a run to RECOVERING "
    "and names a recovery owner; it admits nobody.",
    "The durable history is a separate object and it is what decides. ADMITTED "
    "is active and refuses reuse even though the process lock is free.",
    "Unknown, malformed, incomplete and contradictory history refuses as well, "
    "under the same validation the executor uses.",
)


@dataclass(frozen=True, slots=True)
class ParticipantDecision:
    """Whether one participant may proceed, and every reason it may not."""

    participant: Participant
    may_proceed: bool
    refusals: tuple[str, ...] = ()
    validation: LifecycleValidation | None = None
    limits: tuple[str, ...] = MODEL_LIMITS

    def __post_init__(self) -> None:
        if self.may_proceed and self.refusals:
            raise PlanRefused(
                "A participant that may proceed carries no refusal, for the same "
                "reason an AdmissionDecision that admits carries none."
            )
        if not self.may_proceed and not self.refusals:
            raise PlanRefused("A refusal names why.")


def participant_may_proceed(
    *,
    participant: Participant,
    history: LifecycleHistory,
    lock: LockView,
    host: str,
    target_identity: str,
    quarantine: QuarantineRecord | None = None,
) -> ParticipantDecision:
    """Apply the one allowlist to one participant.

    **The shared semantics — R2-4.** The lifecycle half of this decision is
    `reservation.validate_lifecycle()`, which is the function
    `reservation.admit()` calls. There is no participant-specific denylist, no
    "ordinary participants may also proceed when …" clause, and no state that
    refuses the executor and admits a test suite.

    Three things are checked on top of it, and each is about the participant
    rather than about the history:

    * the **lock**, which every participant must find free or held by nobody.
      *Wait or refuse*, never proceed;
    * a **quarantine record**, which refuses every participant and refuses the
      environment reset especially: a reset would destroy the residue the
      quarantine exists to preserve; and
    * nothing else. A participant that only reads is still a writer the next
      inventory cannot account for.
    """
    refusals: list[str] = []

    validation = validate_lifecycle(
        history=history, host=host, target_identity=target_identity
    )
    refusals.extend(validation.refusals)
    if validation.admits and history.disposition not in ADMITTING_OUTCOMES:
        refusals.append(
            "the validated outcome is not in the allowlist "
            f"{sorted(value.value for value in ADMITTING_OUTCOMES)}."
        )

    if lock.observation_failed:
        refusals.append(
            "the cooperative lock could not be read. A lock whose state is "
            "unknown is not an unheld lock."
        )
    elif lock.held_by is not None:
        refusals.append(
            f"the cooperative lock is held by {lock.held_by!r}. The rule for all "
            "seven participants is wait or refuse, never proceed."
        )

    if quarantine is not None and quarantine.host == host:
        refusals.append(
            f"host {host!r} carries a quarantine record from reservation "
            f"{quarantine.reservation_id!r}. No participant proceeds against a "
            "quarantined host."
        )
        if participant is Participant.ENVIRONMENT_RESET:
            refusals.append(
                "the environment reset refuses especially: a reset would destroy "
                "the residue the quarantine exists to preserve."
            )

    return ParticipantDecision(
        participant=participant,
        may_proceed=not refusals,
        refusals=tuple(refusals),
        validation=validation,
    )


# ---------------------------------------------------------------------------
# Verified first use, as a provisioning operation
# ---------------------------------------------------------------------------


#: The proposed provisioning delta this model describes. **Every row is
#: unapproved**, nothing here provisions anything, and the model creates these
#: objects only inside an in-memory `SyntheticFilesystem`.
PROPOSED_PROVISIONING = (
    (
        "creator",
        "the operator provisioning the disposable host, as root, out of band. "
        "Not the harness, not a participant, and not a side effect of a run.",
    ),
    (
        "authority",
        "the maintainer's approval of the §7 provisioning delta. It is not "
        "approved, and an unapproved provisioning step is a refusal rather than "
        "a default.",
    ),
    (
        "path",
        "/var/lib/freedom-blades/laboratory/lifecycle.json, in the directory the "
        "runner contract §5.4 specifies. Outside /run, because a record that "
        "vanished on reboot would make every crashed run look like a first use.",
    ),
    (
        "ownership and modes",
        "root:freedomlab, 0640, in a 0750 root:freedomlab directory: written by "
        "the executor as root and readable by the six other participants.",
    ),
    (
        "binding",
        "the record names the host and the approved target identity it is about, "
        "and a record read for another host or target is evidence about that one.",
    ),
    (
        "creation rule",
        "exclusive creation with no overwrite. An existing record is never "
        "reinitialized, and the attempt refuses.",
    ),
    (
        "durability",
        "the record's bytes are synchronized and its entry in the containing "
        "directory is synchronized, in that order, before it is treated as "
        "existing at all.",
    ),
    (
        "evidence of first use",
        "an operator attestation naming who established that this host has never "
        "been reserved, and how. The claim is positive; its absence is not it.",
    ),
)


class FirstUseRefusal(str, Enum):
    """Why an initialization refused, as a closed vocabulary.

    A typed refusal rather than a message, because three of these have different
    recoveries and a caller that could not tell them apart would pick the wrong
    one.
    """

    #: A record already exists. Never overwritten, never reinitialized.
    ALREADY_INITIALIZED = "already_initialized"
    #: The host has been used before and the record is missing. **This is the
    #: dangerous one.** Missing history on a previously used host must never be
    #: reinitialized as first use.
    PRIOR_USE_NOT_EXCLUDED = "prior_use_not_excluded"
    #: An earlier initialization was interrupted and left a temporary behind.
    INTERRUPTED_INITIALIZATION = "interrupted_initialization"
    #: Nobody attested that this host has never been reserved.
    NO_FIRST_USE_EVIDENCE = "no_first_use_evidence"
    #: The record would be bound to a host or target other than this one.
    BINDING_MISMATCH = "binding_mismatch"
    #: A durability barrier did not succeed.
    NOT_DURABLE = "not_durable"


@dataclass(frozen=True, slots=True)
class FirstUseEvidence:
    """What supports the claim that this host has never been reserved.

    `prior_use_excluded` has no default that means yes, and `attested_by` is
    required with it: a first use is a claim somebody makes, and an unattributed
    claim is an assertion with no author.
    """

    prior_use_excluded: bool = False
    attested_by: str = ""
    #: How prior use was excluded — a fresh image, a rebuild reference, an
    #: operator's account. Recorded so the claim remains attributable.
    basis: str = ""

    def missing(self) -> tuple[str, ...]:
        missing: list[str] = []
        if not self.prior_use_excluded:
            missing.append("prior use of this host was not excluded")
        if not self.attested_by.strip():
            missing.append("nobody is named as having attested it")
        if not self.basis.strip():
            missing.append("no basis for the exclusion is recorded")
        return tuple(missing)


@dataclass(frozen=True, slots=True)
class InitializationOutcome:
    """What one modelled initialization concluded.

    `recovery` is populated on every refusal, because R2-4 asks for the recovery
    as well as the refusal: an interrupted initialization and an unexcluded prior
    use are both refusals and they are not the same problem.
    """

    initialized: bool
    refusal: FirstUseRefusal | None = None
    reasons: tuple[str, ...] = ()
    recovery: tuple[str, ...] = ()
    #: **What this writer knows, and only this writer.** Both barriers returned
    #: success in this process. It is not stored, no reader can observe it, and
    #: it dies with the process — PR-20260911-R3-1.
    durable: bool = False
    barriers: tuple[str, ...] = ()
    limits: tuple[str, ...] = MODEL_LIMITS


#: The recovery for each refusal, named rather than left to a reader.
FIRST_USE_RECOVERY: Mapping[FirstUseRefusal, tuple[str, ...]] = {
    FirstUseRefusal.ALREADY_INITIALIZED: (
        "Read the existing record. It is the history, and initialization is not "
        "how a history is replaced.",
        "If the existing record is unreadable, that is an operator task against "
        "the durable store, not a reason to create a second record.",
    ),
    FirstUseRefusal.PRIOR_USE_NOT_EXCLUDED: (
        "Treat the host as having an unknown predecessor. Every participant "
        "refuses, which is the correct fail-closed state.",
        "Recover by establishing what the predecessor was — an operator task — "
        "or by a separately approved rebuild of the host, after which first use "
        "can be attested on the rebuild's own evidence.",
        "Never reinitialize a missing record as first use on a host that has "
        "been used. That is the refusal this exists for.",
    ),
    FirstUseRefusal.INTERRUPTED_INITIALIZATION: (
        "The temporary is reported by absolute path and is not removed "
        "automatically.",
        "If the final record name does not resolve, nothing was published: an "
        "operator removes the temporary after establishing that, and "
        "initialization is then attempted again from the beginning.",
        "If the final record name resolves to the same inode as the temporary, "
        "the exclusive publication stopped between its link and its unlink "
        "(runner contract r6 §6.2, amendment D1) and the record was published. "
        "An operator removes only the temporary; initialization is not repeated, "
        "and the next participant's re-seal establishes the record's durability.",
        "If the final name resolves to any other object, neither case holds, and "
        "the host stays refused until an operator establishes what it is.",
    ),
    FirstUseRefusal.NO_FIRST_USE_EVIDENCE: (
        "Obtain the attestation. A first use is a positive claim about the host, "
        "and its absence is not the claim.",
    ),
    FirstUseRefusal.BINDING_MISMATCH: (
        "Correct the host or target the record would be bound to. A record for "
        "another host is evidence about that host.",
    ),
    FirstUseRefusal.NOT_DURABLE: (
        "Nothing is treated as initialized. The bytes, or the entry, or both did "
        "not reach durable storage, and a record that a power loss would remove "
        "is not a record any participant may be admitted on.",
    ),
}


def initialize_first_use_record(
    record: "DurableRecordStore",
    *,
    host: str,
    target_identity: str,
    approved_host: str,
    approved_target_identity: str,
    evidence: FirstUseEvidence,
    attested_at: str = "2026-09-11T08:00:00Z",
    host_previously_used: bool = False,
    fail_at: str = "",
) -> InitializationOutcome:
    """Create the initial verified-first-use record, or refuse with a recovery.

    The order, and every step is a refusal rather than a fallback:

    1. **evidence** — somebody attested that this host has never been reserved,
       and named how. Without it there is no first use to record;
    2. **binding** — the record would be bound to the approved host and approved
       target, or it is refused. **This is `BINDING_MISMATCH`'s enforcing path**,
       which PR-20260911-R3-3 found declared and unimplemented;
    3. **prior use** — a host that has been used before is never reinitialized as
       first use, however absent its record is;
    4. **interrupted initialization** — a leftover temporary means an earlier
       attempt did not finish. It is reported, not cleaned, and it refuses;
    5. **exclusive creation** — no-overwrite semantics, so an existing final
       record refuses before anything is written; and
    6. **durability** — the record's bytes are synchronized, the rename is
       issued, and the containing directory is synchronized.

    **What `durable` on the outcome means, exactly.** It means both barriers
    returned success *in this process*. It is not stored, not readable by
    anybody else, and it dies with this process — which is PR-20260911-R3-1, and
    why the successor's obligation is `RESEAL_CONTRACT` rather than reading a
    flag somebody wrote down.

    `fail_at` injects a failure at `"record-data"`, `"rename"` or
    `"record-entry"`, which are the three points an interruption can reach.
    """
    if evidence.missing():
        return InitializationOutcome(
            initialized=False,
            refusal=FirstUseRefusal.NO_FIRST_USE_EVIDENCE,
            reasons=tuple(
                f"first use is not supported: {reason}"
                for reason in evidence.missing()
            ),
            recovery=FIRST_USE_RECOVERY[FirstUseRefusal.NO_FIRST_USE_EVIDENCE],
        )
    mismatched: list[str] = []
    if host != approved_host:
        mismatched.append(
            f"the record would name host {host!r} and the approved host is "
            f"{approved_host!r}."
        )
    if target_identity != approved_target_identity:
        mismatched.append(
            f"the record would be bound to target {target_identity!r} and the "
            f"approved target is {approved_target_identity!r}. A first-use "
            "record bound to the wrong target admits every later run against "
            "evidence collected about a different one."
        )
    if mismatched:
        return InitializationOutcome(
            initialized=False,
            refusal=FirstUseRefusal.BINDING_MISMATCH,
            reasons=tuple(mismatched),
            recovery=FIRST_USE_RECOVERY[FirstUseRefusal.BINDING_MISMATCH],
        )
    if host_previously_used:
        return InitializationOutcome(
            initialized=False,
            refusal=FirstUseRefusal.PRIOR_USE_NOT_EXCLUDED,
            reasons=(
                f"host {host!r} has been reserved before and its lifecycle record "
                "is missing. Missing history on a previously used host is not "
                "first use: it is a history that was lost, and reinitializing it "
                "would convert an unknown predecessor into a clean one.",
            ),
            recovery=FIRST_USE_RECOVERY[FirstUseRefusal.PRIOR_USE_NOT_EXCLUDED],
        )
    if record.temporary_present():
        return InitializationOutcome(
            initialized=False,
            refusal=FirstUseRefusal.INTERRUPTED_INITIALIZATION,
            reasons=(
                f"a temporary {record.temporary!r} is present, so an earlier "
                "initialization was interrupted. It is reported and not removed "
                "automatically, on the §2.13.2b precedent.",
            ),
            recovery=FIRST_USE_RECOVERY[FirstUseRefusal.INTERRUPTED_INITIALIZATION],
        )
    if record.present():
        return InitializationOutcome(
            initialized=False,
            refusal=FirstUseRefusal.ALREADY_INITIALIZED,
            reasons=(
                f"a lifecycle record {record.name!r} already exists. Exclusive "
                "creation refuses rather than overwriting, because the existing "
                "record is the history.",
            ),
            recovery=FIRST_USE_RECOVERY[FirstUseRefusal.ALREADY_INITIALIZED],
        )

    entry = RecordEntry(
        sequence=1,
        kind=EntryKind.FIRST_USE,
        host=host,
        target=target_identity,
        author=evidence.attested_by,
        at=attested_at,
        fields={"basis": evidence.basis},
    )
    outcome = record.publish((entry,), exclusive=True, fail_at=fail_at)
    if not outcome.published:
        return InitializationOutcome(
            initialized=False,
            refusal=FirstUseRefusal.NOT_DURABLE,
            reasons=outcome.reasons,
            recovery=FIRST_USE_RECOVERY[FirstUseRefusal.NOT_DURABLE]
            + FIRST_USE_RECOVERY[FirstUseRefusal.INTERRUPTED_INITIALIZATION],
            barriers=outcome.barriers,
        )
    return InitializationOutcome(
        initialized=True,
        durable=True,
        barriers=outcome.barriers,
        reasons=(
            f"a verified-first-use record for host {host!r} and target "
            f"{target_identity!r} was created exclusively, attested by "
            f"{evidence.attested_by!r}, and both its bytes and its directory "
            "entry barriers returned success in this process before it was "
            "treated as existing.",
        ),
    )


#: How records stay attributable and historical entries survive an update, which
#: R2-4 asks to be explained rather than assumed.
RECORD_ATTRIBUTION = (
    "Every entry names the reservation it is about, the host and approved target "
    "it is bound to, who wrote it and when. An entry with no author is an "
    "assertion with no author and is refused on read.",
    "Nothing deletes or rewrites a prior entry. A state change is a new entry "
    "appended after the previous one, so the history is the file and the current "
    "state is its last coherent entry.",
    "An operator recovery is an appended entry naming the recovery reference. "
    "The quarantined reservation stays quarantined in its own entry and is never "
    "resumed, which is why OPERATOR_RECOVERED requires a QUARANTINED predecessor.",
    "A release record is appended only after release() returns RELEASED, and it "
    "names the reservation, host and target it is a release of. It is the only "
    "thing that turns a predecessor into an admitting one.",
    "The persistent lock inode and the durable history are separate objects and "
    "neither does the other's job. No expiry and no free lock authorizes reuse.",
)


#: **These two constructors build a history; they do not read one.**
#:
#: PR-20260911-R3-1 and -R3-3 both landed partly because a test that claimed to
#: exercise the whole path called `environment_reset_history(HOST)` and handed
#: the result to the decision, so no stored byte was ever parsed and the
#: storage-to-admission gap had nothing to show up in. They are kept because a
#: table-driven unit test over thirteen histories is a useful thing and building
#: thirteen files would obscure it — but they are **unit-test constructors** and
#: a test that uses one may not claim to be end to end. The connected path is
#: `initialize_first_use_record` → `DurableRecordStore` → `read_and_admit`, and
#: it consumes the bytes its initializer or predecessor wrote.
UNIT_TEST_CONSTRUCTORS = (
    "crash_between_admitted_and_running",
    "environment_reset_history",
)


def crash_between_admitted_and_running(
    host: str, predecessor_id: str, *, target_identity: str = ""
) -> LifecycleHistory:
    """The record a crash leaves between the two publications — R2-4's case.

    A **unit-test constructor**, per `UNIT_TEST_CONSTRUCTORS`. It states a
    history; it reads none.

    `DURABLE_RECORD_ORDERING` item 1 publishes ADMITTED before the first effect
    of any kind, and item 2 publishes RUNNING before the first mutation-bearing
    step. A crash between them leaves this: a durable ADMITTED, a process lock
    the kernel released, and no release record. Every participant refuses.
    """
    return LifecycleHistory(
        host=host,
        readable=True,
        complete=True,
        predecessor_id=predecessor_id,
        predecessor_state=ReservationState.ADMITTED,
        disposition=PredecessorDisposition.ACTIVE,
        target_identity=target_identity or host,
        read_at="after the restart",
        read_by="the next participant",
    )


def environment_reset_history(
    host: str, *, target_identity: str = "", attested_by: str = "", basis: str = ""
) -> LifecycleHistory:
    """A fresh, provisioned, never-reserved host, as the record states it.

    A **unit-test constructor**, per `UNIT_TEST_CONSTRUCTORS`. It constructs a
    history rather than reading one, so **a test built on it is not evidence
    that storage and admission are connected** and must not claim to be.
    """
    return LifecycleHistory(
        host=host,
        readable=True,
        complete=True,
        disposition=PredecessorDisposition.VERIFIED_FIRST_USE,
        target_identity=target_identity or host,
        first_use_attested_by=attested_by or "peter duscha, operations owner",
        first_use_basis=basis or "the host was rebuilt from a fresh image",
        read_at="at provisioning",
        read_by="the operator",
    )


def survey(
    *,
    history: LifecycleHistory,
    lock: LockView,
    host: str,
    target_identity: str,
    quarantine: QuarantineRecord | None = None,
    participants: Sequence[Participant] = PARTICIPANTS,
) -> tuple[ParticipantDecision, ...]:
    """Apply the one allowlist to every participant over the same observations.

    The table-driven check R2-4 asks for. Every participant sees the same
    history, the same lock and the same quarantine, and the property the tests
    assert is that they **agree**: there is no state on which the executor
    refuses and a test suite proceeds, and none on which the reverse holds.
    """
    return tuple(
        participant_may_proceed(
            participant=participant,
            history=history,
            lock=lock,
            host=host,
            target_identity=target_identity,
            quarantine=quarantine,
        )
        for participant in participants
    )



# ---------------------------------------------------------------------------
# The record schema — PR-20260911-R3-3
# ---------------------------------------------------------------------------


#: The first line of every lifecycle record. A reader that does not find it
#: exactly is reading something else and refuses rather than guessing.
RECORD_MAGIC = "freedom-blades-laboratory-lifecycle"

#: The schema this model writes. A record declaring any other version is refused
#: as unsupported: an older reader must not interpret a newer record's fields by
#: the meanings it happens to know.
#:
#: **Raised from 1 to 2 in r6 — PR-20260911-R5-1.** A `participant_started`
#: entry now carries the reservation the run owns, so a schema-1 run file means
#: something this reader cannot supply: it has no reservation field, and reading
#: it as a run with *no* reservation would be reading an r5 harness run as one
#: the binding check happens to permit. The version is what makes that a named
#: refusal rather than a reinterpretation.
RECORD_SCHEMA_VERSION = 2

#: Every version this reader accepts. One, today, and the set exists so that
#: adding a version is a decision rather than a silent widening. **It does not
#: contain 1**: r5's records are refused as `UNSUPPORTED_SCHEMA`, not read under
#: the new meanings, and §5.5 of the contract states the consequence.
SUPPORTED_SCHEMA_VERSIONS = frozenset({RECORD_SCHEMA_VERSION})

#: The line that ends a complete history. **This is the truncation detector.**
#: A record whose bytes stop early parses into a coherent-looking prefix and is
#: refused because the terminator is absent, rather than being read as a shorter
#: history that happens to end on an admitting entry.
HISTORY_TERMINATOR = "end-history"

ENTRY_BEGIN = "begin-entry"
ENTRY_END = "end-entry"


class EntryKind(str, Enum):
    """What one appended history entry says happened.

    A closed vocabulary. An entry whose kind is outside it is malformed and the
    whole record refuses: an unrecognised entry is a statement about the host
    this reader cannot evaluate, and skipping it would let a writer hide a run
    behind a kind the reader does not know.
    """

    #: The provisioning entry. Always first, and never appended later.
    FIRST_USE = "first_use"
    #: Published before the first effect of any kind.
    ADMITTED = "admitted"
    #: Published before the first mutation-bearing step.
    RUNNING = "running"
    #: Published only after `release()` returns RELEASED.
    RELEASED = "released"
    #: Published on any failure path, as an addition.
    QUARANTINED = "quarantined"
    #: The deadline passed or the run crashed and recovery has an owner.
    RECOVERING = "recovering"
    #: Appended over a quarantine by an operator. The quarantine entry stays.
    OPERATOR_RECOVERED = "operator_recovered"
    #: A participant's non-reusable state, persisted before its first effect.
    PARTICIPANT_STARTED = "participant_started"
    #: A participant's reusable completion, published only after its stated
    #: conditions were observed.
    PARTICIPANT_COMPLETED = "participant_completed"
    #: An operator's attributable recovery of an interrupted participant run.
    PARTICIPANT_RECOVERED = "participant_recovered"


#: The kinds the reservation record may contain.
RESERVATION_KINDS = frozenset(
    {
        EntryKind.FIRST_USE,
        EntryKind.ADMITTED,
        EntryKind.RUNNING,
        EntryKind.RELEASED,
        EntryKind.QUARANTINED,
        EntryKind.RECOVERING,
        EntryKind.OPERATOR_RECOVERED,
    }
)

#: The kinds a participant run file may contain.
PARTICIPANT_KINDS = frozenset(
    {
        EntryKind.PARTICIPANT_STARTED,
        EntryKind.PARTICIPANT_COMPLETED,
        EntryKind.PARTICIPANT_RECOVERED,
    }
)

#: The fields every entry carries, whatever its kind. `sequence` is the history
#: order, `author` and `at` are the attribution, and `host`/`target` are the
#: binding R3-3 found missing.
COMMON_FIELDS = ("sequence", "kind", "host", "target", "author", "at")

#: The additional fields each kind requires. The permitted set for a kind is
#: exactly the common fields plus these: a field outside it is malformed, which
#: is what makes the schema **bounded** rather than merely documented.
KIND_FIELDS: Mapping[EntryKind, tuple[str, ...]] = {
    EntryKind.FIRST_USE: ("basis",),
    EntryKind.ADMITTED: ("reservation",),
    EntryKind.RUNNING: ("reservation",),
    EntryKind.RELEASED: ("reservation", "released_at"),
    EntryKind.QUARANTINED: ("reservation", "reason"),
    EntryKind.RECOVERING: ("reservation", "recovery_owner"),
    EntryKind.OPERATOR_RECOVERED: ("recovers", "reference"),
    EntryKind.PARTICIPANT_STARTED: (
        "run",
        "participant",
        "identity",
        "reservation",
        "effects",
    ),
    EntryKind.PARTICIPANT_COMPLETED: ("run", "participant", "identity", "evidence"),
    EntryKind.PARTICIPANT_RECOVERED: ("run", "participant", "identity", "reference"),
}


class RecordRefusal(str, Enum):
    """Why a reader refused a stored record, as a closed vocabulary.

    Each value is a different thing for an operator to go and fix, which is why
    they are not one `malformed`. **None of them normalizes into success**: there
    is no value here that means *proceed with what could be read*.
    """

    #: The record is not there at all, or could not be read.
    ABSENT = "absent"
    #: The bytes are not this schema's shape.
    MALFORMED = "malformed"
    #: The bytes stop before the history terminator.
    TRUNCATED = "truncated"
    #: The schema version is outside `SUPPORTED_SCHEMA_VERSIONS`.
    UNSUPPORTED_SCHEMA = "unsupported_schema"
    #: Two entries disagree about the host, the target or the sequence.
    CONTRADICTORY = "contradictory"
    #: The entries are not a strictly increasing, first-use-rooted history.
    HISTORY_ORDER = "history_order"
    #: An entry carries no binding at all.
    MISSING_BINDING = "missing_binding"
    #: The record is bound to another host or another approved target.
    WRONG_BINDING = "wrong_binding"


@dataclass(frozen=True, slots=True)
class RecordEntry:
    """One appended entry, after parsing or before serialization.

    `fields` is the bounded key/value payload; `kind` and `sequence` are lifted
    out because the parser needs them before it can check anything else.
    """

    sequence: int
    kind: EntryKind
    host: str
    target: str
    author: str
    at: str
    fields: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.sequence < 1:
            raise PlanRefused("A history entry is numbered from 1.")
        for name in ("host", "target", "author", "at"):
            if not str(getattr(self, name)).strip():
                raise PlanRefused(
                    f"A history entry needs a {name}. An entry with no {name} is "
                    "an assertion with no author, no time or no binding, and R3-3 "
                    "is what happens when one of those is dropped in transit."
                )
        permitted = set(KIND_FIELDS[self.kind])
        supplied = set(self.fields)
        if supplied != permitted:
            raise PlanRefused(
                f"a {self.kind.value!r} entry carries exactly "
                f"{sorted(permitted)} beyond the common fields, and this one "
                f"carries {sorted(supplied)}."
            )

    def get(self, name: str) -> str:
        return str(self.fields.get(name, ""))


def serialize_history(entries: Sequence[RecordEntry]) -> bytes:
    """The exact bytes of a history, deterministically.

    One line per field, one terminator per entry, one terminator per history.
    Deterministic because the field order is the schema's order rather than a
    dictionary's: two writers of the same history produce the same bytes, which
    is what lets a reader's digest of what it saw mean anything.
    """
    lines = [RECORD_MAGIC, f"schema={RECORD_SCHEMA_VERSION}"]
    for entry in entries:
        lines.append(ENTRY_BEGIN)
        lines.append(f"sequence={entry.sequence}")
        lines.append(f"kind={entry.kind.value}")
        lines.append(f"host={entry.host}")
        lines.append(f"target={entry.target}")
        lines.append(f"author={entry.author}")
        lines.append(f"at={entry.at}")
        for name in KIND_FIELDS[entry.kind]:
            lines.append(f"{name}={entry.get(name)}")
        lines.append(ENTRY_END)
    lines.append(HISTORY_TERMINATOR)
    return ("\n".join(lines) + "\n").encode("utf-8")


@dataclass(frozen=True, slots=True)
class ParsedHistory:
    """What a reader made of the bytes it was handed.

    `entries` is populated only when the parse succeeded completely. A refusal
    carries no partial entry list, because a partial history is exactly the
    input that would let a reader stop on a convenient admitting entry.
    """

    ok: bool
    entries: tuple[RecordEntry, ...] = ()
    refusal: RecordRefusal | None = None
    reasons: tuple[str, ...] = ()
    #: The digest of the bytes that were parsed, so a later reader's account of
    #: what it saw is comparable with this one's.
    source_digest: str = ""
    limits: tuple[str, ...] = MODEL_LIMITS

    def __post_init__(self) -> None:
        if self.ok and self.refusal is not None:
            raise PlanRefused("A successful parse carries no refusal.")
        if not self.ok and self.refusal is None:
            raise PlanRefused("A refused parse names which refusal it is.")
        if not self.ok and self.entries:
            raise PlanRefused(
                "A refused parse returns no entries. Handing back the prefix that "
                "parsed is how a truncated history gets read as a shorter one."
            )


def _refused(refusal: RecordRefusal, *reasons: str, digest_hex: str = "") -> ParsedHistory:
    return ParsedHistory(
        ok=False, refusal=refusal, reasons=tuple(reasons), source_digest=digest_hex
    )


def parse_history(
    raw: bytes | None,
    *,
    permitted_kinds: frozenset,
    host: str,
    target_identity: str,
) -> ParsedHistory:
    """Parse supplied bytes into a bounded history, or refuse and say why.

    **This parses bytes somebody handed in. It reads no live host state.** The
    caller obtained them from the model's store through a descriptor it holds;
    this function sees a byte string and nothing else.

    The refusals, in the order they are reached, and none of them falls through
    to a success:

    1. **absent** — there were no bytes;
    2. **malformed** — the magic line, the schema line, an entry boundary, a
       `key=value` line, a kind, a duplicate key or a field outside the kind's
       bounded set;
    3. **unsupported schema** — a version this reader does not implement;
    4. **truncated** — the history terminator is missing, or an entry is not
       closed. A record whose tail was lost is refused rather than read as the
       shorter history its surviving prefix spells;
    5. **history order** — sequences that are not 1..N strictly increasing, or a
       record whose first entry is not a first use;
    6. **contradictory** — two entries that disagree about the host or target;
    7. **missing binding** — an entry with an empty host or target; and
    8. **wrong binding** — a record about another host or another approved
       target. This is R3-3's case, and it refuses here rather than being
       compared away later.
    """
    if raw is None:
        return _refused(
            RecordRefusal.ABSENT,
            "there is no lifecycle record to read. An absent record is not an "
            "empty history, and initialization is the only way out of it.",
        )
    digest_hex = digest(raw)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        return _refused(
            RecordRefusal.MALFORMED,
            f"the record's bytes are not UTF-8: {error}.",
            digest_hex=digest_hex,
        )
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if not lines or lines[0] != RECORD_MAGIC:
        return _refused(
            RecordRefusal.MALFORMED,
            f"the record does not begin with {RECORD_MAGIC!r}. These are bytes "
            "from somewhere else, and reading them as a history is how an "
            "unrelated file becomes an admitting record.",
            digest_hex=digest_hex,
        )
    if len(lines) < 2 or not lines[1].startswith("schema="):
        return _refused(
            RecordRefusal.MALFORMED,
            "the record declares no schema version.",
            digest_hex=digest_hex,
        )
    declared = lines[1].split("=", 1)[1]
    if not declared.isdigit():
        return _refused(
            RecordRefusal.MALFORMED,
            f"the record's schema version {declared!r} is not a number.",
            digest_hex=digest_hex,
        )
    if int(declared) not in SUPPORTED_SCHEMA_VERSIONS:
        return _refused(
            RecordRefusal.UNSUPPORTED_SCHEMA,
            f"the record declares schema {declared} and this reader implements "
            f"{sorted(SUPPORTED_SCHEMA_VERSIONS)}. A reader that interpreted a "
            "newer record by the meanings it happens to know would be guessing.",
            digest_hex=digest_hex,
        )
    if lines[-1] != HISTORY_TERMINATOR:
        return _refused(
            RecordRefusal.TRUNCATED,
            f"the record does not end with {HISTORY_TERMINATOR!r}, so its bytes "
            "stop early. A truncated history is refused rather than read as the "
            "shorter history its surviving prefix spells — which is the record a "
            "power loss leaves when the entry was made durable and the bytes "
            "were not.",
            digest_hex=digest_hex,
        )

    entries: list[RecordEntry] = []
    index = 2
    while index < len(lines) - 1:
        if lines[index] != ENTRY_BEGIN:
            return _refused(
                RecordRefusal.MALFORMED,
                f"line {index + 1} is {lines[index]!r} where an entry was "
                f"expected to begin with {ENTRY_BEGIN!r}.",
                digest_hex=digest_hex,
            )
        index += 1
        payload: dict[str, str] = {}
        closed = False
        while index < len(lines) - 1:
            line = lines[index]
            index += 1
            if line == ENTRY_END:
                closed = True
                break
            if "=" not in line:
                return _refused(
                    RecordRefusal.MALFORMED,
                    f"the entry line {line!r} is not a key=value pair.",
                    digest_hex=digest_hex,
                )
            key, value = line.split("=", 1)
            if not key or key in payload:
                return _refused(
                    RecordRefusal.MALFORMED,
                    f"the entry repeats or omits the key {key!r}. A duplicated "
                    "key has two meanings and a reader that took the last one "
                    "would be choosing.",
                    digest_hex=digest_hex,
                )
            payload[key] = value
        if not closed:
            return _refused(
                RecordRefusal.TRUNCATED,
                f"an entry begun at line {index} is never closed with "
                f"{ENTRY_END!r}.",
                digest_hex=digest_hex,
            )
        missing = [name for name in COMMON_FIELDS if name not in payload]
        if missing:
            return _refused(
                RecordRefusal.MALFORMED,
                f"an entry omits the required field(s) {missing}.",
                digest_hex=digest_hex,
            )
        try:
            kind = EntryKind(payload["kind"])
        except ValueError:
            return _refused(
                RecordRefusal.MALFORMED,
                f"the entry kind {payload['kind']!r} is not one of "
                f"{sorted(value.value for value in EntryKind)}. An unrecognised "
                "entry is refused rather than skipped: skipping it hides the run "
                "it describes.",
                digest_hex=digest_hex,
            )
        if kind not in permitted_kinds:
            return _refused(
                RecordRefusal.MALFORMED,
                f"a {kind.value!r} entry is not permitted in this record, which "
                f"carries {sorted(value.value for value in permitted_kinds)}.",
                digest_hex=digest_hex,
            )
        if not payload["sequence"].isdigit():
            return _refused(
                RecordRefusal.MALFORMED,
                f"the entry sequence {payload['sequence']!r} is not a number.",
                digest_hex=digest_hex,
            )
        extra = set(payload) - set(COMMON_FIELDS) - set(KIND_FIELDS[kind])
        absent = set(KIND_FIELDS[kind]) - set(payload)
        if extra or absent:
            return _refused(
                RecordRefusal.MALFORMED,
                f"a {kind.value!r} entry carries exactly "
                f"{sorted(KIND_FIELDS[kind])} beyond the common fields; this one "
                f"adds {sorted(extra)} and omits {sorted(absent)}. The schema is "
                "bounded, so an unknown field is a refusal rather than something "
                "to ignore.",
                digest_hex=digest_hex,
            )
        if not payload["host"].strip() or not payload["target"].strip():
            return _refused(
                RecordRefusal.MISSING_BINDING,
                "an entry carries an empty host or target. A record that does "
                "not say which host and which approved target it is about is "
                "evidence about neither.",
                digest_hex=digest_hex,
            )
        try:
            entries.append(
                RecordEntry(
                    sequence=int(payload["sequence"]),
                    kind=kind,
                    host=payload["host"],
                    target=payload["target"],
                    author=payload["author"],
                    at=payload["at"],
                    fields={name: payload[name] for name in KIND_FIELDS[kind]},
                )
            )
        except PlanRefused as refusal:
            return _refused(
                RecordRefusal.MALFORMED, str(refusal), digest_hex=digest_hex
            )

    if not entries:
        return _refused(
            RecordRefusal.HISTORY_ORDER,
            "the record contains no entries at all. A history with nothing in it "
            "is not a first use; a first use is a positive claim somebody made.",
            digest_hex=digest_hex,
        )
    for position, entry in enumerate(entries, start=1):
        if entry.sequence != position:
            return _refused(
                RecordRefusal.HISTORY_ORDER,
                f"entry {position} is numbered {entry.sequence}. A history is "
                "1..N strictly increasing, so a gap is a lost entry and a repeat "
                "is two statements claiming the same place.",
                digest_hex=digest_hex,
            )
    if entries[0].kind is not EntryKind.FIRST_USE and permitted_kinds is RESERVATION_KINDS:
        return _refused(
            RecordRefusal.HISTORY_ORDER,
            f"the record's first entry is {entries[0].kind.value!r} and a "
            "reservation history is rooted in a first use. A history whose "
            "beginning is missing establishes nothing about the runs it omits.",
            digest_hex=digest_hex,
        )
    first = entries[0]
    for entry in entries[1:]:
        if entry.host != first.host or entry.target != first.target:
            return _refused(
                RecordRefusal.CONTRADICTORY,
                f"entry {entry.sequence} is bound to "
                f"{entry.host!r}/{entry.target!r} and entry 1 to "
                f"{first.host!r}/{first.target!r}. One file describing two hosts "
                "or two targets is refused rather than reconciled.",
                digest_hex=digest_hex,
            )
    if first.host != host:
        return _refused(
            RecordRefusal.WRONG_BINDING,
            f"the record is about host {first.host!r} and this is {host!r}. A "
            "history read for another host is evidence about that host.",
            digest_hex=digest_hex,
        )
    if first.target != target_identity:
        return _refused(
            RecordRefusal.WRONG_BINDING,
            f"the record is bound to approved target {first.target!r} and this "
            f"run is of {target_identity!r}. **This is PR-20260911-R3-3**: a "
            "history for the same hostname is not a history for another approved "
            "target, and admitting on it lets evidence collected against one "
            "target authorize a run against a different one.",
            digest_hex=digest_hex,
        )
    return ParsedHistory(
        ok=True, entries=tuple(entries), source_digest=digest_hex
    )


# ---------------------------------------------------------------------------
# The durable store, and the publication/restart gap — PR-20260911-R3-1
# ---------------------------------------------------------------------------


#: **What a writer knows, and what dies with it.**
#:
#: R3-1's mechanism in one paragraph. Publication is write, synchronize the
#: bytes, rename, synchronize the containing directory. If the last barrier
#: fails, the writer knows the record is not durable and the *name is already
#: visible*. A process-only restart — not a power loss — then leaves a reader a
#: readable, coherent record and no way at all to learn that its publication
#: never completed, because the only party that knew was the process that died.
PUBLICATION_UNCERTAINTY = (
    "A rename is visible immediately and durable only when the containing "
    "directory's entry is synchronized. Between those two points the record is "
    "readable and would not survive a power loss.",
    "The writer's outcome is in the writer's memory. A process-only restart "
    "destroys it and leaves the filesystem exactly as it was, so the next "
    "reader sees the visible record and not the failure.",
    "An existing name proves a rename happened. It does not prove the "
    "subsequent barrier succeeded, and neither does a boolean stored inside the "
    "record: the writer would have had to survive to write it.",
    "So the reader may not ask whether the record is durable. It must make it "
    "durable, or refuse — which is the whole of RESEAL_CONTRACT.",
)

#: **The correction — who re-establishes durability, and with what permission.**
#:
#: The re-seal is `fsync` on an `O_RDONLY` descriptor for the *containing
#: directory*. It needs read and search on that directory and **no write
#: permission on anything**, so the six ordinary participants can perform it
#: against the root-written record exactly as the executor can. That is why the
#: proposal does not need ordinary users to be able to write the record, which
#: is the permission implication R3-1 asked to be resolved rather than assumed.
RESEAL_CONTRACT = (
    "Who: any participant that holds the cooperative lock, as `ubuntu`. It is "
    "the first thing done after the lock is taken and before the record's "
    "content is acted on.",
    "What: `fsync` on a separately opened O_RDONLY descriptor for the record's "
    "containing directory, which makes whatever the name currently resolves to "
    "durable. It is idempotent: re-sealing an already durable entry is a "
    "successful no-op, so the reader never has to know which case it is in.",
    "Which bytes: none. The re-seal covers the **parent entry** only. The "
    "record's own bytes are the writer's barrier, and the writer issues it "
    "before the rename, so a visible final name implies that barrier returned "
    "success — a design inference from the specified order, not an observation.",
    "Permission: read and search on the record's directory. No write permission "
    "on the record, the directory or anything else, so the root-written record "
    "stays root-written and ordinary participants still discharge the "
    "obligation.",
    "If it fails: refuse. The participant publishes nothing, takes nothing, and "
    "names the record's recovery owner. A failed barrier is an attributable "
    "operator recovery, never a reason to continue on the visible name.",
    "What it does not establish: that the bytes behind the name are complete. "
    "A power loss that kept the entry and lost the bytes leaves a truncated "
    "record, and `parse_history` refuses it as TRUNCATED rather than reading "
    "the shorter history its surviving prefix spells.",
)


class AdmissionPolicy(str, Enum):
    """Whether a successor establishes durability or trusts the visible name.

    Two values, because the second one is the **negative control**. A matrix in
    which revision 3's protocol also passes is a matrix that is not testing the
    correction.
    """

    #: Revision 3. Read the record, validate it, proceed. This is the protocol
    #: PR-20260911-R3-1 found, and the model keeps it so the corrected property
    #: has something to fail against.
    R3_TRUSTS_THE_VISIBLE_RECORD = "r3_trusts_the_visible_record"
    #: Revision 4. Take the lock, re-seal the parent entry, then read, parse and
    #: validate. Refuse if the re-seal fails.
    R4_ESTABLISHES_DURABILITY_UNDER_THE_LOCK = "r4_establishes_durability_under_the_lock"


class PublicationRefusal(str, Enum):
    """Why a publication refused."""

    #: A barrier did not return success. Nothing is treated as published.
    NOT_DURABLE = "not_durable"
    #: A temporary from an earlier attempt is present.
    INTERRUPTED_PUBLICATION = "interrupted_publication"
    #: The history being written does not extend the one that is stored.
    WOULD_OVERWRITE_HISTORY = "would_overwrite_history"
    #: An exclusive creation found the final name already there.
    ALREADY_PUBLISHED = "already_published"
    #: The stored history could not be read, so there is nothing to append to.
    UNREADABLE_PREDECESSOR = "unreadable_predecessor"
    #: The history this publication would write is not a valid history under the
    #: record's own semantics — **PR-20260911-R4-1 and -R4-2**. Nothing is
    #: written, so the stored bytes are exactly what they were.
    INVALID_HISTORY = "invalid_history"


@dataclass(frozen=True, slots=True)
class PublicationOutcome:
    """What one publication attempt concluded, as its writer knows it.

    **`barriers` is the writer's knowledge and it is not evidence anybody else
    can read.** It lists the barriers that returned success *in this process*.
    A reader has no access to it, which is the point of R3-1: the reader gets
    the filesystem, and the filesystem does not carry this tuple.
    """

    published: bool
    refusal: PublicationRefusal | None = None
    reasons: tuple[str, ...] = ()
    barriers: tuple[str, ...] = ()
    limits: tuple[str, ...] = MODEL_LIMITS

    def __post_init__(self) -> None:
        if self.published and self.refusal is not None:
            raise PlanRefused("A publication that succeeded carries no refusal.")
        if not self.published and self.refusal is None:
            raise PlanRefused("A refused publication names which refusal it is.")


class DurableRecordStore:
    """One appended-to record file in one provisioned directory.

    It models the two objects the contract needs — the reservation record and a
    participant's run file — with one publication path, because they have the
    same durability obligation and giving them two would be giving them two
    chances to disagree.

    **It never consults the model's durable-state map.** Everything it does is
    something a real participant could do with the descriptors it holds:
    `openat`, `read`, `create`, `write`, `fsync`, `renameat`. A test may look at
    the oracle; this may not, and `test_the_reader_uses_no_oracle_observation`
    asserts that against the module's source.
    """

    def __init__(
        self,
        filesystem: SyntheticFilesystem,
        *,
        directory: str,
        name: str,
        label: str,
        kinds: frozenset = RESERVATION_KINDS,
    ) -> None:
        self._fs = filesystem
        self._directory = directory
        self._name = name
        self._label = label
        #: Which record this is — `RESERVATION_KINDS` or `PARTICIPANT_KINDS`.
        #: The store knows it rather than being told at each call, because the
        #: parse, the semantic check and the publication must all agree about
        #: what is being written, and three parameters are three chances to
        #: disagree.
        self._kinds = kinds
        #: Injected failure of the re-seal barrier, so the refusal path has a
        #: test. A real failure is an I/O error from `fsync`.
        self.reseal_fails = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def kinds(self) -> frozenset:
        return self._kinds

    def semantic_problems(self, entries: Sequence[RecordEntry]) -> tuple[str, ...]:
        """The record type's own semantic check, over a complete history.

        The same function on both sides of the store: `publish` runs it over the
        history it is about to write, and every reader runs it over the history
        it read. A store whose kinds have no check refuses rather than
        publishing an unchecked history.
        """
        check = HISTORY_SEMANTICS.get(self._kinds)
        if check is None:
            return (
                f"{self._label!r} declares entry kinds "
                f"{sorted(value.value for value in self._kinds)}, for which no "
                "semantic check is registered. An unchecked history is refused "
                "rather than published.",
            )
        return tuple(check(entries, self._name))

    @property
    def temporary(self) -> str:
        return f"{self._name}.tmp"

    def _path_fd(self) -> int:
        return self._fs.open_directory(
            self._directory, DescriptorMode.O_PATH, self._label
        ).number

    def _sync_fd(self) -> int:
        return self._fs.open_directory(
            self._directory, DescriptorMode.O_RDONLY, self._label
        ).number

    def present(self) -> bool:
        """Whether the final name resolves. A name, not a durability claim."""
        return self._fs.fstatat(self._path_fd(), self._name) is not None

    def temporary_present(self) -> bool:
        return self._fs.fstatat(self._path_fd(), self.temporary) is not None

    def read_record_bytes(self) -> bytes | None:
        """The record's bytes, through a descriptor, or `None` if absent.

        **Named `read_record_bytes` and not `read_bytes` deliberately.**
        `test_no_execution.py::test_no_module_opens_reads_or_writes_a_file`
        refuses the attribute name `read_bytes` anywhere in the planning tier,
        because it cannot tell `pathlib.Path.read_bytes` from a method that
        merely borrows the name — and a guard that had to tell them apart would
        be a guard with an exception in it. The refusal is a stop condition, so
        the method is renamed rather than the guard relaxed.
        """
        try:
            fd = self._fs.openat(
                self._path_fd(), self._name, DescriptorMode.O_RDONLY
            ).number
        except ModelRefused:
            return None
        return self._fs.read(fd)

    def reseal(self) -> None:
        """Make the currently visible entry durable — the R3-1 obligation.

        `fsync` on the containing directory's O_RDONLY descriptor. It is
        idempotent, needs no write permission, and raises when it fails so the
        caller refuses rather than continuing on a visible name.
        """
        if self.reseal_fails:
            raise ModelRefused(
                f"the durability barrier on {self._label}'s containing directory "
                "did not return success, so this participant cannot establish "
                "that the visible record would survive a power loss. It refuses "
                "and names the recovery owner rather than proceeding."
            )
        self._fs.fsync(self._sync_fd(), barrier=f"reseal:{self._label}")

    def publish(
        self,
        entries: Sequence[RecordEntry],
        *,
        exclusive: bool = False,
        fail_at: str = "",
    ) -> PublicationOutcome:
        """Write a complete history and make it durable, or refuse.

        Order, and it is the contract's: **check the history's semantics**,
        create the temporary exclusively, write the bytes, **synchronize the
        bytes**, rename onto the final name, **synchronize the containing
        entry**. `fail_at` injects a failure at `"record-data"`, `"rename"` or
        `"record-entry"` — the three points an interruption can reach, and the
        third is R3-1's.

        **The semantic check comes first and it comes before any byte is
        written** — PR-20260911-R4-1 and -R4-2. An invalid append leaves the
        stored bytes exactly as they were: no temporary is created, no rename is
        issued, and the refusal names every rule the proposed history breaks.
        """
        problems = self.semantic_problems(entries)
        if problems:
            return PublicationOutcome(
                published=False,
                refusal=PublicationRefusal.INVALID_HISTORY,
                reasons=(
                    f"the history this publication would write to {self._name!r} "
                    "is not a valid history under this record's own semantics, so "
                    "nothing was written and the stored bytes are unchanged.",
                )
                + problems,
            )
        path_fd = self._path_fd()
        if self.temporary_present():
            return PublicationOutcome(
                published=False,
                refusal=PublicationRefusal.INTERRUPTED_PUBLICATION,
                reasons=(
                    f"a temporary {self.temporary!r} is present, so an earlier "
                    "publication was interrupted. It is reported and not removed "
                    "automatically, on the §2.13.2b precedent.",
                ),
            )
        if exclusive and self.present():
            return PublicationOutcome(
                published=False,
                refusal=PublicationRefusal.ALREADY_PUBLISHED,
                reasons=(
                    f"{self._name!r} already exists. Exclusive creation refuses "
                    "rather than overwriting, because the existing record is the "
                    "history.",
                ),
            )

        crossed: list[str] = []
        try:
            fd = self._fs.create_file(path_fd, self.temporary).number
            self._fs.write(fd, serialize_history(entries))
            if fail_at == "record-data":
                raise ModelRefused(
                    "injected failure before the record's bytes were synchronized."
                )
            self._fs.fsync(fd, barrier=f"{self._label}:record-data")
            crossed.append("record-data")
            if fail_at == "rename":
                raise ModelRefused(
                    "injected failure after the bytes were synchronized and "
                    "before the rename. The temporary survives and the record "
                    "does not."
                )
            self._fs.renameat(
                path_fd,
                self.temporary,
                path_fd,
                self._name,
                noreplace=exclusive,
            )
            if fail_at == "record-entry":
                raise ModelRefused(
                    "injected failure after the rename and before the containing "
                    "directory was synchronized. **The record is visible and it "
                    "is not durable**, and this process is the only party that "
                    "knows. This is PR-20260911-R3-1."
                )
            self._fs.fsync(self._sync_fd(), barrier=f"{self._label}:record-entry")
            crossed.append("record-entry")
        except ModelRefused as refusal:
            return PublicationOutcome(
                published=False,
                refusal=PublicationRefusal.NOT_DURABLE,
                reasons=(str(refusal),),
                barriers=tuple(crossed),
            )
        return PublicationOutcome(published=True, barriers=tuple(crossed))

    def append(
        self,
        entry: RecordEntry,
        *,
        host: str,
        target_identity: str,
        fail_at: str = "",
    ) -> PublicationOutcome:
        """Append one entry to the stored history, preserving every prior one.

        The stored bytes are parsed first and the prior entries are re-serialized
        **verbatim**, so no publication can rewrite history: the only difference
        between the old file and the new one is the entry at the end. A stored
        history that will not parse refuses — there is nothing to extend, and
        replacing it would be exactly the overwrite R3-1 forbids recovery from
        performing.

        The extended history then goes through `publish`, which refuses it if
        the appended entry does not follow from the stored ones. **A refused
        append leaves the existing bytes intact**, which is what makes the
        proposed-entry check and the stored-history check the same check rather
        than two that could drift.
        """
        parsed = parse_history(
            self.read_record_bytes(),
            permitted_kinds=self._kinds,
            host=host,
            target_identity=target_identity,
        )
        if not parsed.ok:
            return PublicationOutcome(
                published=False,
                refusal=PublicationRefusal.UNREADABLE_PREDECESSOR,
                reasons=(
                    f"the stored history refused as {parsed.refusal.value!r}, so "
                    "there is nothing to append to. Publishing over it would "
                    "replace a history nobody has read with one this writer "
                    "invented, which is the overwrite recovery must never "
                    "perform.",
                )
                + parsed.reasons,
            )
        extended = tuple(parsed.entries) + (
            RecordEntry(
                sequence=len(parsed.entries) + 1,
                kind=entry.kind,
                host=entry.host,
                target=entry.target,
                author=entry.author,
                at=entry.at,
                fields=dict(entry.fields),
            ),
        )
        if tuple(extended[: len(parsed.entries)]) != tuple(parsed.entries):
            return PublicationOutcome(
                published=False,
                refusal=PublicationRefusal.WOULD_OVERWRITE_HISTORY,
                reasons=("the new history does not extend the stored one.",),
            )
        return self.publish(extended, fail_at=fail_at)


# ---------------------------------------------------------------------------
# History semantics and the derived decision input — PR-20260911-R3-3
# ---------------------------------------------------------------------------


#: The order rules this protocol needs, and no more. **This is not a generic
#: event store.** Each rule exists because breaking it produces a history that
#: would otherwise admit somebody, and each is checked over the whole parsed
#: history rather than over the entry a reader happens to stop on.
HISTORY_ORDER_RULES = (
    "A first use appears once, at sequence 1, and is never appended later. A "
    "second one would be the claim that a used host had never been used.",
    "A history has one **current reservation** at a time — the one the most "
    "recent `admitted` entry named — and every `running`, `released`, "
    "`quarantined` and `recovering` entry names that reservation. An entry "
    "naming any other one is refused rather than filed against it.",
    "A transition of the current reservation is legal only when it appears in "
    "`reservation.TRANSITIONS`. There is no second transition table here: the "
    "accepted state machine is the one the reservation module already states, "
    "and a history that disagrees with it is refused.",
    "`released` and `quarantined` are terminal and name no successor, so a "
    "further entry for a finished reservation — a duplicate terminal event, a "
    "stale release, a repeated operator recovery — is refused rather than read "
    "as a later state. **This is PR-20260911-R4-1**: a stale `released A` "
    "appended while `B` is running must never retire B.",
    "A reservation id is used once. A new `admitted` may not name an id this "
    "history has already seen, so a terminal identity never reappears as a "
    "fresh run.",
    "An `admitted` entry is published only when the current reservation admits "
    "a successor: there is none, it `released`, or it was `quarantined` and an "
    "operator recovery has been appended for it. `admitted`, `running`, "
    "`recovering` and an unrecovered `quarantined` all refuse.",
    "An `operator_recovered` entry names the **current** reservation, that "
    "reservation is `quarantined`, and it has not been recovered already. The "
    "quarantine entry stays where it is: the recovery is an attributed "
    "addition that permits a **new** reservation, and it neither revives nor "
    "rewrites the terminal one it recovers.",
    "The **current reservation and its current state** are the decision input. "
    "A reader never takes the last entry on trust and never selects an earlier, "
    "more convenient admitting one, and a history whose order these rules "
    "refuse produces no decision input at all.",
)

#: The reservation state each reservation-bearing entry kind publishes.
#:
#: `first_use` has none — it is the provisioning entry and not a reservation —
#: and `operator_recovered` has none either, because it is an attributed
#: addition to a quarantine rather than a transition of the reservation it
#: recovers. Keeping both out of this table is what preserves the distinction
#: between *the quarantined run's terminal state* and *permission for a new run*.
ENTRY_STATES: Mapping[EntryKind, ReservationState] = {
    EntryKind.ADMITTED: ReservationState.ADMITTED,
    EntryKind.RUNNING: ReservationState.RUNNING,
    EntryKind.RELEASED: ReservationState.RELEASED,
    EntryKind.QUARANTINED: ReservationState.QUARANTINED,
    EntryKind.RECOVERING: ReservationState.RECOVERING,
}

#: The states from which `reservation.TRANSITIONS` names no successor. Derived
#: from that table rather than restated, so a change there cannot leave a second
#: list of terminal states quietly disagreeing with the first.
TERMINAL_STATES = frozenset(
    state for state, successors in TRANSITIONS.items() if not successors
)


@dataclass(frozen=True, slots=True)
class ReservationHistoryState:
    """The current reservation a stored history describes, or why it is not one.

    **PR-20260911-R4-1.** The previous checker remembered whether an id had ever
    been admitted and the derivation took the final entry, so a stale `released`
    for a finished reservation appended after a newer `admitted`/`running` pair
    both passed the check and became the decision. The current reservation and
    its current state are carried here instead, and the derivation reads them
    rather than the tail.
    """

    ok: bool
    problems: tuple[str, ...] = ()
    #: The provisioning entry, when the history is rooted in one.
    first_use: RecordEntry | None = None
    #: The reservation the most recent `admitted` entry named, and the state its
    #: own most recent entry left it in.
    current_id: str = ""
    current_state: ReservationState | None = None
    #: The entry that established `current_state`.
    current_entry: RecordEntry | None = None
    #: The operator recovery appended for the current reservation, if any.
    recovery_entry: RecordEntry | None = None
    #: Every reservation an operator recovery has been appended for.
    recovered: tuple[str, ...] = ()

    @property
    def current_is_recovered(self) -> bool:
        return bool(self.current_id) and self.current_id in self.recovered


def _admits_a_successor(
    current_state: ReservationState | None,
    current_id: str,
    recovered: Sequence[str],
) -> bool:
    """Whether a new reservation may be admitted over the current one.

    Three cases and no fourth: there is no reservation yet, the current one
    `released`, or the current one was `quarantined` and an operator recovery
    has been appended for it. `admitted`, `running`, `recovering` and an
    unrecovered `quarantined` all refuse, which is the same allowlist
    `reservation.ADMITTING_DISPOSITIONS` states one level up.
    """
    if current_state is None:
        return True
    if current_state is ReservationState.RELEASED:
        return True
    return (
        current_state is ReservationState.QUARANTINED and current_id in recovered
    )


def check_reservation_history(
    entries: Sequence[RecordEntry],
) -> ReservationHistoryState:
    """Walk a reservation history as a state machine and report every break.

    One pass, carrying the current reservation, its current state and the
    recoveries appended so far. Every rule in `HISTORY_ORDER_RULES` is checked
    here, against `reservation.TRANSITIONS`, and a break stops that entry from
    advancing the machine rather than being recorded and walked past — so one
    invalid entry cannot leave the state it would have set behind it.
    """
    problems: list[str] = []
    first_use: RecordEntry | None = None
    seen: set[str] = set()
    recovered: list[str] = []
    current_id = ""
    current_state: ReservationState | None = None
    current_entry: RecordEntry | None = None
    recovery_entry: RecordEntry | None = None

    for entry in entries:
        if entry.kind is EntryKind.FIRST_USE:
            if entry.sequence != 1:
                problems.append(
                    f"entry {entry.sequence} claims a verified first use and is "
                    "not the first entry. A host with a history has been used."
                )
                continue
            first_use = entry
            continue

        if entry.kind is EntryKind.ADMITTED:
            reservation = entry.get("reservation").strip()
            if not reservation:
                problems.append(
                    f"entry {entry.sequence} admits a reservation it does not "
                    "name. An unnamed reservation cannot be released, "
                    "quarantined or recovered by anybody."
                )
                continue
            if not _admits_a_successor(current_state, current_id, recovered):
                problems.append(
                    f"entry {entry.sequence} admits {reservation!r} while the "
                    f"current reservation {current_id!r} is "
                    f"{current_state.value!r}. A reservation is admitted over a "
                    "first use, a released predecessor, or a quarantine an "
                    "operator has recovered, and over nothing else."
                )
                continue
            if reservation in seen:
                problems.append(
                    f"entry {entry.sequence} admits {reservation!r}, which this "
                    "history has already used. A reservation id is used once, so "
                    "a terminal identity never reappears as a fresh run."
                )
                continue
            seen.add(reservation)
            current_id = reservation
            current_state = ReservationState.ADMITTED
            current_entry = entry
            recovery_entry = None
            continue

        if entry.kind in ENTRY_STATES:
            reservation = entry.get("reservation").strip()
            target_state = ENTRY_STATES[entry.kind]
            if current_state is None:
                problems.append(
                    f"entry {entry.sequence} is a {entry.kind.value!r} for "
                    f"reservation {reservation!r}, which this history never "
                    "admitted. A run that was never admitted here is a run this "
                    "record does not cover."
                )
                continue
            if reservation != current_id:
                problems.append(
                    f"entry {entry.sequence} is a {entry.kind.value!r} for "
                    f"reservation {reservation!r} and the current reservation is "
                    f"{current_id!r} in state {current_state.value!r}. "
                    "**PR-20260911-R4-1**: a stale entry belonging to an earlier "
                    "reservation is refused rather than filed as the current "
                    "one's state, because reading it as one retires a run that "
                    "never ended."
                )
                continue
            if current_state in TERMINAL_STATES:
                problems.append(
                    f"entry {entry.sequence} transitions reservation "
                    f"{reservation!r} after it reached {current_state.value!r}, "
                    "which is terminal and names no successor. A duplicate "
                    "terminal event and a stale repetition of one are the same "
                    "refusal, and neither is a resumption."
                )
                continue
            if target_state not in TRANSITIONS[current_state]:
                problems.append(
                    f"entry {entry.sequence} moves reservation {reservation!r} "
                    f"from {current_state.value!r} to {target_state.value!r}, "
                    "which `reservation.TRANSITIONS` does not contain. The "
                    "accepted successors are "
                    f"{sorted(state.value for state in TRANSITIONS[current_state])}."
                )
                continue
            current_state = target_state
            current_entry = entry
            continue

        recovers = entry.get("recovers").strip()
        if current_state is not ReservationState.QUARANTINED or recovers != current_id:
            problems.append(
                f"entry {entry.sequence} recovers reservation {recovers!r}, and "
                f"the current reservation is {current_id or 'none'} in state "
                f"{current_state.value if current_state is not None else 'none'}. "
                "An operator recovery is appended to the applicable quarantined "
                "predecessor. It is not permission to revive or rewrite a "
                "terminal reservation, and it is not a statement somebody may "
                "repeat over a later run."
            )
            continue
        if recovers in recovered:
            problems.append(
                f"entry {entry.sequence} recovers reservation {recovers!r} a "
                "second time. One quarantine has one recovery, and repeating it "
                "is the stale-entry case under another name."
            )
            continue
        recovered.append(recovers)
        recovery_entry = entry

    return ReservationHistoryState(
        ok=not problems,
        problems=tuple(problems),
        first_use=first_use,
        current_id=current_id,
        current_state=current_state,
        current_entry=current_entry,
        recovery_entry=recovery_entry,
        recovered=tuple(recovered),
    )


def check_history_semantics(entries: Sequence[RecordEntry]) -> tuple[str, ...]:
    """Every way a syntactically valid reservation history is still not one.

    The reasons alone, for callers that only accumulate refusals.
    `check_reservation_history` is the same walk with its result kept.
    """
    return check_reservation_history(entries).problems


def derive_lifecycle_history(
    parsed: ParsedHistory, *, host: str, read_by: str, read_at: str
) -> LifecycleHistory:
    """Turn a parsed reservation history into the shared validator's input.

    **This is the connection R3-3 found missing.** The binding, the attester,
    the basis, the release record's author and the recovery's reference and
    author all travel from the stored bytes into `LifecycleHistory`, so
    `reservation.validate_lifecycle()` sees the evidence the record actually
    carries rather than a constructed summary of it.

    A history the parser refused, or one whose order is not a history, produces
    an **unreadable** input. That refuses, and it refuses without inventing a
    disposition from whatever could be read.

    **The input is the current reservation, not the last entry — R4-1.** The
    walk in `check_reservation_history` says which reservation is current and
    what state it is in, and this reads that. Taking the tail was what let a
    stale `released` for a finished reservation, appended after a newer
    `admitted`/`running` pair, report the newer run as retired.
    """
    if not parsed.ok:
        return LifecycleHistory(host=host, readable=False, read_by=read_by, read_at=read_at)
    state = check_reservation_history(parsed.entries)
    if not state.ok or state.first_use is None:
        return LifecycleHistory(
            host=host,
            readable=True,
            complete=False,
            read_by=read_by,
            read_at=read_at,
        )

    root = state.first_use
    common = {
        "host": root.host,
        "readable": True,
        "complete": True,
        "target_identity": root.target,
        "read_by": read_by,
        "read_at": read_at,
    }
    if state.current_state is None:
        return LifecycleHistory(
            disposition=PredecessorDisposition.VERIFIED_FIRST_USE,
            first_use_attested_by=root.author,
            first_use_basis=root.get("basis"),
            **common,
        )
    current = state.current_entry
    if state.current_state is ReservationState.RELEASED:
        return LifecycleHistory(
            predecessor_id=state.current_id,
            predecessor_state=ReservationState.RELEASED,
            disposition=PredecessorDisposition.RELEASED,
            release_record=ReleaseRecord(
                reservation_id=state.current_id,
                host=current.host,
                target_identity=current.target,
                released_at=current.get("released_at"),
                recorded_by=current.author,
            ),
            **common,
        )
    if state.current_state is ReservationState.QUARANTINED:
        if state.current_is_recovered:
            recovery = state.recovery_entry
            return LifecycleHistory(
                predecessor_id=state.current_id,
                predecessor_state=ReservationState.QUARANTINED,
                disposition=PredecessorDisposition.OPERATOR_RECOVERED,
                operator_recovery_reference=recovery.get("reference"),
                recovery_authored_by=recovery.author,
                **common,
            )
        return LifecycleHistory(
            predecessor_id=state.current_id,
            predecessor_state=ReservationState.QUARANTINED,
            disposition=PredecessorDisposition.QUARANTINED,
            **common,
        )
    if state.current_state is ReservationState.RECOVERING:
        return LifecycleHistory(
            predecessor_id=state.current_id,
            predecessor_state=ReservationState.RECOVERING,
            disposition=PredecessorDisposition.RECOVERING,
            **common,
        )
    return LifecycleHistory(
        predecessor_id=state.current_id,
        predecessor_state=state.current_state,
        disposition=PredecessorDisposition.ACTIVE,
        **common,
    )


# ---------------------------------------------------------------------------
# Every participant's interrupted effects — PR-20260911-R3-2
# ---------------------------------------------------------------------------


#: **The two things that are never completion evidence**, named where the
#: completion check reads them. R3-2's sentence, in the model.
NOT_COMPLETION_EVIDENCE = (
    "A free cooperative lock. `flock(2)` associates the lock with the open file "
    "description, so the kernel releases it when the holder's descriptors close "
    "— which happens whether the run finished or was killed.",
    "A wrapper's exit status. The wrapper is a client. Its children, its "
    "server-side transactions and the tree it was halfway through writing do "
    "not exit with it, and a zero status from a process that spawned survivors "
    "reports the wrapper's own fate and nothing else.",
    "An elapsed deadline. A deadline moves a run to RECOVERING and names a "
    "recovery owner. It is never takeover authority.",
    "An absent quarantine record. A crash before one could be written leaves the "
    "previous entry standing, which is why absence is not an ending.",
)


@dataclass(frozen=True, slots=True)
class ParticipantProfile:
    """One entry point's identity, effects, completion evidence and recovery.

    R3-2 asks for this per participant rather than for the executor alone,
    because the six that only serialized were the six whose interrupted effects
    nothing accounted for.
    """

    participant: Participant
    identity: str
    lifecycle_writer: str
    lock_lifetime: str
    effects: tuple[str, ...]
    completion_conditions: tuple[str, ...]
    recovery: tuple[str, ...]
    #: What a future target check would have to establish before this
    #: participant's completion condition could be observed for real. Named
    #: rather than assumed, because none of them has been performed.
    proof_obligations: tuple[str, ...]
    #: The completion conditions this model **owns** and therefore derives from
    #: the operations it performed, rather than accepting as an injected
    #: observation — **PR-20260911-R4-3**. Only the harness has any: its two
    #: conditions are facts about the reservation it is concluding, and injecting
    #: them is how a completion came to assert a release that had not been
    #: published. Every other participant's conditions are external observations
    #: of processes, backends and trees, and those stay injected and
    #: attributable because this model cannot verify them.
    lifecycle_owned_conditions: tuple[str, ...] = ()

    def external_conditions(self) -> tuple[str, ...]:
        """The conditions an observer supplies. The complement of the owned set."""
        owned = set(self.lifecycle_owned_conditions)
        return tuple(
            condition
            for condition in self.completion_conditions
            if condition not in owned
        )


#: The harness's two completion conditions, named once so the profile, the
#: derivation and the contract cite the same strings rather than three copies.
HARNESS_RELEASE_DECIDED = "`release()` returned RELEASED on observed evidence"
HARNESS_RELEASE_PUBLISHED = "the release entry reached durable storage"


PARTICIPANT_PROFILES: Mapping[Participant, ParticipantProfile] = {
    Participant.BOT_SUITE: ParticipantProfile(
        participant=Participant.BOT_SUITE,
        identity="`ubuntu`, one pytest process and its children",
        lifecycle_writer="its own run file, under the group-writable run directory",
        lock_lifetime="from before the first test collects until the process exits",
        effects=(
            "rows, sequences and temporary schemas in the disposable database",
            "server-side transactions and advisory locks held by backends the "
            "suite opened",
            "temporary trees the fixtures wrote under the repository",
        ),
        completion_conditions=(
            "the pytest process and every child it spawned have exited",
            "no backend attributable to this run remains on the disposable "
            "database",
            "the fixtures' temporary trees were removed and the removal observed",
        ),
        recovery=(
            "An operator terminates nothing. The residue is reported by name, "
            "the disposable test schema is dropped and recreated under an "
            "attributed recovery entry, and only then is the run recorded "
            "recovered.",
        ),
        proof_obligations=(
            "That a backend on the disposable cluster can be attributed to one "
            "run at all. Unconfirmed on the target.",
        ),
    ),
    Participant.WEB_SUITE: ParticipantProfile(
        participant=Participant.WEB_SUITE,
        identity="`ubuntu`, one pytest process and its children",
        lifecycle_writer="its own run file",
        lock_lifetime="from before the first test collects until the process exits",
        effects=(
            "the same disposable database the bot suite uses — finding F-6, which "
            "is why the two run serially",
            "server-side transactions opened by the application under test",
            "temporary trees and uploaded fixtures",
        ),
        completion_conditions=(
            "the pytest process and every child it spawned have exited",
            "no backend attributable to this run remains on the disposable "
            "database",
            "the fixtures' temporary trees were removed and the removal observed",
        ),
        recovery=(
            "As the bot suite, and the shared database means a recovery for "
            "either is a recovery both must wait for.",
        ),
        proof_obligations=(
            "That the two suites' backends are distinguishable from one another "
            "on the shared cluster. Unconfirmed on the target.",
        ),
    ),
    Participant.FOUNDRY_TESTS: ParticipantProfile(
        participant=Participant.FOUNDRY_TESTS,
        identity="`ubuntu`, one `node --test` process and its workers",
        lifecycle_writer="its own run file",
        lock_lifetime="from before the runner starts until it exits",
        effects=(
            "worker processes the test runner spawned",
            "temporary trees under the module directory",
        ),
        completion_conditions=(
            "the runner and every worker have exited",
            "the temporary trees were removed and the removal observed",
        ),
        recovery=(
            "The surviving workers are reported by name and left alone. An "
            "operator establishes what they are before anything is removed.",
        ),
        proof_obligations=(
            "That `node --test` workers are enumerable as children of the "
            "runner on the target. Unconfirmed.",
        ),
    ),
    Participant.SYNCHRONIZATION: ParticipantProfile(
        participant=Participant.SYNCHRONIZATION,
        identity="`ubuntu`, one `rsync` invocation",
        lifecycle_writer="its own run file",
        lock_lifetime="from before the transfer starts until the tree is consistent",
        effects=(
            "a partially replaced working tree — **the effect that outlives the "
            "wrapper most obviously**, because a killed `rsync` leaves files from "
            "two revisions side by side and temporaries among them",
        ),
        completion_conditions=(
            "the transfer reported success",
            "a whole-tree consistency check against the source revision passed "
            "after it",
            "no transfer temporary remains in the destination tree",
        ),
        recovery=(
            "Re-run the complete synchronization from the source of truth under "
            "an attributed recovery entry. A partial tree is never repaired by "
            "the next participant's assumption that it is fine.",
        ),
        proof_obligations=(
            "What the whole-tree consistency check is, concretely, on the "
            "target, and that it is cheap enough to run every time. Unspecified "
            "and unconfirmed.",
        ),
    ),
    Participant.DEPENDENCY_UPDATE: ParticipantProfile(
        participant=Participant.DEPENDENCY_UPDATE,
        identity="`ubuntu`, one `uv pip install` invocation",
        lifecycle_writer="its own run file",
        lock_lifetime="for the whole installation",
        effects=(
            "a partially updated virtual environment: some distributions "
            "replaced, some not, and a package left half-unpacked",
        ),
        completion_conditions=(
            "the installer reported success",
            "an environment consistency check over the locked set passed after it",
        ),
        recovery=(
            "Reinstall the complete locked set under an attributed recovery "
            "entry. A half-updated environment is not made whole by a suite "
            "that happens to import successfully.",
        ),
        proof_obligations=(
            "That the environment consistency check detects a half-unpacked "
            "distribution rather than only a missing one. Unconfirmed.",
        ),
    ),
    Participant.ENVIRONMENT_RESET: ParticipantProfile(
        participant=Participant.ENVIRONMENT_RESET,
        identity="`ubuntu`, escalating where the reset needs it",
        lifecycle_writer="its own run file",
        lock_lifetime="for the whole reset",
        effects=(
            "destruction of database and filesystem state — **the most dangerous "
            "participant to interrupt**, because its effect is the removal of "
            "the evidence an earlier interruption left",
        ),
        completion_conditions=(
            "every reset step reported success",
            "the post-reset state was observed to match the declared baseline",
        ),
        recovery=(
            "Re-run the reset under an attributed recovery entry, and only after "
            "establishing that nothing unresolved was pending when it was "
            "interrupted.",
            "**A reset never runs while a quarantine or an unsettled run exists.** "
            "It would destroy the residue they exist to preserve, and the reset "
            "is refused especially rather than merely refused.",
        ),
        proof_obligations=(
            "That the declared post-reset baseline is observable at all on the "
            "target. Unconfirmed.",
        ),
    ),
    Participant.HARNESS_CLI: ParticipantProfile(
        participant=Participant.HARNESS_CLI,
        identity="`ubuntu`, escalating to root for the reviewed effects",
        lifecycle_writer=(
            "the reservation record, as root, **and** its own run file. It is the "
            "only participant that writes both"
        ),
        lock_lifetime=(
            "for the whole reservation, across provisioning, execution, capture, "
            "restoration and cleanup"
        ),
        effects=(
            "the reviewed configuration mutation and its restoration",
            "the disposable root and everything created under it",
            "the recovery store outside the disposable root",
        ),
        completion_conditions=(
            HARNESS_RELEASE_DECIDED,
            HARNESS_RELEASE_PUBLISHED,
        ),
        recovery=(
            "The quarantine entry stays quarantined and an operator appends an "
            "attributed recovery. The recovered reservation's own id is never "
            "reused.",
        ),
        proof_obligations=(
            "Every §9.3 implementation check, none of which has been performed.",
        ),
        lifecycle_owned_conditions=(
            HARNESS_RELEASE_DECIDED,
            HARNESS_RELEASE_PUBLISHED,
        ),
    ),
}


#: **The durable reservation binding — PR-20260911-R5-1.**
#:
#: r5 stored the reservation on the *completion* and checked only that the field
#: was not empty. There was no stored fact to check it against, so a release of
#: reservation A settled an already-started harness run B: the run id came from
#: the caller, the reservation came from the caller, and nothing compared them.
#: The binding is now a field of the **start**, which is published before the
#: run's first effect and is never rewritten, and every later statement about
#: the run is compared with it.
RESERVATION_BINDING = (
    "The harness's `participant_started` entry **names the reservation the run "
    "owns**, durably, before the run's first effect. It is a field of the "
    "record's bounded schema, not a convention over the run's name.",
    "Terminal publication requires **exact equality** among five values: the "
    "reservation in the stored start, `ReservationRequest.reservation_id`, "
    "`ReleasePublication.reservation_id`, `CompletionEvidence.reservation_id` "
    "and the reservation the terminal result reports.",
    "The run id stays bound to the stored start and to the file's own name, as "
    "r5 already required. The reservation binding is **additional** to it, "
    "because a run id that is stable says nothing about which reservation the "
    "run belongs to.",
    "**No identity is inferred from a run name.** A prefix, a suffix or any "
    "other string convention over the filename is not checked, is not relied "
    "on and is not part of this contract. `RES-1-harness` is a name; the "
    "stored field is the fact.",
    "The six participants whose completion conditions are external **carry the "
    "field empty**, and an empty value is required rather than tolerated. One "
    "shape, validated in both directions: a reservation on a run that does not "
    "own lifecycle conditions is a binding it never established.",
    "The check runs **before an append and on read**. A safe writer does not "
    "excuse an unsafe reader of records written by r5 or by a corrupt "
    "implementation, so planted bytes that mismatch refuse on the reader's "
    "path too and block every successor.",
    "The writer **reads the stored start before deriving anything**. A "
    "caller's participant, run id, reservation and release publication are "
    "checked claims; the completion profile and the reservation written into "
    "the evidence come from the stored entry.",
)


#: The separator between the fields of an encoded completion evidence string.
#: No participant, condition, run id, reservation id or observer name in this
#: model contains it, so a decoded field is the field that was encoded rather
#: than a guess at where one ended.
EVIDENCE_SEPARATOR = "|"


@dataclass(frozen=True, slots=True)
class CompletionEvidence:
    """What a `participant_completed` entry actually claims, as a parsed object.

    **PR-20260911-R4-2's evidence half.** Revision 4 wrote the conditions into a
    free-text field and the reader checked that the field was there. An empty
    string, or any other string, was therefore proof as long as the entry's kind
    said `completed`. This is a bounded encoding with a decoder that refuses
    anything else, so the reader can check the evidence's **content** — which
    run it is about, which conditions it claims, and who observed them.
    """

    run_id: str
    observed_by: str
    conditions: tuple[str, ...]
    #: The reservation the conditions are about, for a participant whose
    #: completion conditions are lifecycle-owned. Empty for the six whose
    #: conditions are observations of their own processes and trees.
    reservation_id: str = ""

    def encode(self) -> str:
        parts = [
            f"run={self.run_id}",
            f"reservation={self.reservation_id}",
            f"observed-by={self.observed_by}",
        ]
        parts.extend(f"condition={condition}" for condition in self.conditions)
        return EVIDENCE_SEPARATOR.join(parts)

    @classmethod
    def decode(cls, text: str) -> "CompletionEvidence | None":
        """The encoded evidence, or `None` for anything that is not it.

        `None` rather than a partially populated object, for the same reason
        `parse_history` returns no entries on a refusal: handing back what could
        be read is how an arbitrary string becomes a claim.
        """
        run: str | None = None
        reservation: str | None = None
        observer: str | None = None
        conditions: list[str] = []
        for part in text.split(EVIDENCE_SEPARATOR):
            if "=" not in part:
                return None
            key, value = part.split("=", 1)
            if key == "run":
                if run is not None:
                    return None
                run = value
            elif key == "reservation":
                if reservation is not None:
                    return None
                reservation = value
            elif key == "observed-by":
                if observer is not None:
                    return None
                observer = value
            elif key == "condition":
                conditions.append(value)
            else:
                return None
        if run is None or reservation is None or observer is None:
            return None
        return cls(
            run_id=run,
            observed_by=observer,
            conditions=tuple(conditions),
            reservation_id=reservation,
        )


def reservation_field_problems(
    value: str, profile: ParticipantProfile, *, sequence: int
) -> tuple[str, ...]:
    """Whether one stored `reservation` field is this participant's own shape.

    **PR-20260911-R5-1's schema half.** There is one representation and it is
    validated in both directions: a participant whose completion conditions are
    lifecycle-owned carries a reservation identity, and a participant whose
    conditions are external carries the field **empty**. Neither is optional,
    because a field that may or may not be populated carries no information —
    which is exactly the state r5's completion field was in.

    The grammar is bounded rather than merely non-empty. A value that is not its
    own stripped form is two values a reader would have to choose between, and a
    value containing the evidence separator or a line break cannot survive the
    codecs that carry it, so both refuse here rather than at the point where the
    comparison would quietly fail.
    """
    problems: list[str] = []
    if not profile.lifecycle_owned_conditions:
        if value != "":
            problems.append(
                f"entry {sequence} starts {profile.participant.value!r} and names "
                f"reservation {value!r}. This participant's completion conditions "
                "are observations of its own processes and trees, so its run owns "
                "no reservation and the field is required to be empty. A "
                "reservation it never established is a binding a later reader "
                "would compare against."
            )
        return tuple(problems)
    if not value.strip():
        problems.append(
            f"entry {sequence} starts {profile.participant.value!r} and names no "
            "reservation. **PR-20260911-R5-1**: this participant's completion "
            "conditions are facts about the reservation it concludes, so the run "
            "must durably say which reservation it owns before it issues an "
            "effect. A missing or empty binding is refused rather than treated as "
            "a run that will be told later which release settles it."
        )
        return tuple(problems)
    if value != value.strip():
        problems.append(
            f"entry {sequence} names reservation {value!r}, which is not its own "
            "stripped form. Two spellings of one identity are two values a "
            "comparison would have to choose between."
        )
    if EVIDENCE_SEPARATOR in value:
        problems.append(
            f"entry {sequence} names reservation {value!r}, which contains "
            f"{EVIDENCE_SEPARATOR!r} — the completion evidence's field separator. "
            "An identity that cannot survive the codec that carries it is refused "
            "here rather than where the comparison would silently fail."
        )
    if "\n" in value or "\r" in value:
        problems.append(
            f"entry {sequence} names a reservation containing a line break. The "
            "record is line-oriented, so such a value is not one field."
        )
    return tuple(problems)


@dataclass(frozen=True, slots=True)
class ParticipantRunState:
    """What one run file says about one run, or why it is not a run history.

    **PR-20260911-R4-2.** Revision 4 had no such object: `complete()` took the
    caller's participant, chose that participant's conditions, and appended to
    the caller's filename, comparing none of the three with the stored start.
    The survey then declared a file settled from its last entry's kind alone, so
    a lone `participant_completed` entry with no start was a settled run.
    """

    ok: bool
    problems: tuple[str, ...] = ()
    run_id: str = ""
    participant: "Participant | None" = None
    identity: str = ""
    #: The reservation the **stored start** says this run owns — the durable
    #: fact PR-20260911-R5-1 found missing. Empty for the six participants whose
    #: completion conditions are external, and empty on a refused state because
    #: a refused history reports no facts about the run.
    reservation_id: str = ""
    phase: "RunPhase | None" = None
    start: RecordEntry | None = None
    terminal: RecordEntry | None = None
    evidence: CompletionEvidence | None = None


def check_participant_history(
    entries: Sequence[RecordEntry], *, run_id: str = ""
) -> ParticipantRunState:
    """Validate one participant run history, for writers and for the survey.

    The rules, and each one closes a path R4-2 reproduced or named:

    1. a run **begins with a start**. A terminal entry with no start is a
       completion of a run nothing recorded beginning;
    2. the participant is one of the seven, and it is **stable** across entries.
       The required conditions come from the operation that started, never from
       a value the completion caller supplies;
    3. the identity is stable and is the participant's declared identity;
    4. the run id is stable and **binds to the file it is stored in**, so a run
       filed under another run's name is evidence about that run;
    5. there is **at most one terminal entry**, and no second start. A repeated
       or incompatible terminal event refuses;
    6. a completion's evidence **decodes, names this run, lists exactly this
       participant's conditions and names an observer**. Field presence is not
       the check; content and completeness are;
    7. the **start names the reservation the run owns** in the shape its profile
       requires — an identity for the harness, empty for the six — and a
       completion's evidence names **exactly that reservation**.
       **PR-20260911-R5-1**: r5 checked that the completion's reservation field
       was non-empty and had nothing stored to compare it with, so a release of
       reservation A settled an already-started harness run B; and
    8. a recovery carries its reference, and the same binding rules apply to it
       as to a completion.

    Host and target agreement across entries, and against the run this reader is
    performing, is `parse_history`'s `CONTRADICTORY`/`WRONG_BINDING` pair and is
    not repeated here.
    """
    if not entries:
        return ParticipantRunState(
            ok=False,
            problems=(
                "a run file with no entries records no run, and an empty file is "
                "not an absent one.",
            ),
        )

    start = entries[0]
    if start.kind is not EntryKind.PARTICIPANT_STARTED:
        return ParticipantRunState(
            ok=False,
            problems=(
                f"the run file begins with a {start.kind.value!r} entry and a run "
                "begins with a `participant_started` entry. **PR-20260911-R4-2**: "
                "a terminal entry with no start is a completion of a run nothing "
                "recorded beginning, and reading it as settled settles a run that "
                "may still be issuing effects.",
            ),
        )

    problems: list[str] = []
    declared = start.get("participant")
    try:
        participant = Participant(declared)
    except ValueError:
        return ParticipantRunState(
            ok=False,
            problems=(
                f"the run was started by {declared!r}, which is not one of the "
                f"seven participants "
                f"{sorted(value.value for value in Participant)}. An unknown "
                "participant has no declared effects, no completion conditions "
                "and no recovery, so nothing can establish that its run ended.",
            ),
        )

    profile = PARTICIPANT_PROFILES[participant]
    run = start.get("run").strip()
    if not run:
        problems.append(
            f"entry {start.sequence} starts a run it does not name. A run with no "
            "id cannot be completed, recovered or reported by anybody."
        )
    elif run_id and run != run_id:
        problems.append(
            f"the run file is named {run_id!r} and its entries are about run "
            f"{run!r}. A run record filed under another run's name is evidence "
            "about that run, and surveying it as this one accounts for neither."
        )
    if start.get("identity") != profile.identity:
        problems.append(
            f"entry {start.sequence} records identity {start.get('identity')!r} "
            f"and {declared!r} runs as {profile.identity!r}. An identity that "
            "disagrees with the participant's is a run this profile does not "
            "describe."
        )
    reservation = start.get("reservation")
    problems.extend(
        reservation_field_problems(reservation, profile, sequence=start.sequence)
    )

    terminal: RecordEntry | None = None
    for entry in entries[1:]:
        if entry.kind is EntryKind.PARTICIPANT_STARTED:
            problems.append(
                f"entry {entry.sequence} starts run {run!r} a second time. A run "
                "begins once, and a second start is either two runs in one file "
                "or a rewrite of the first one's account of itself."
            )
            continue
        if terminal is not None:
            problems.append(
                f"entry {entry.sequence} is a second terminal entry "
                f"({entry.kind.value!r}) after a {terminal.kind.value!r}. A run "
                "ends once: a duplicate terminal event, and a recovery appended "
                "over a completion, are the same refusal."
            )
            continue
        if entry.get("run").strip() != run:
            problems.append(
                f"entry {entry.sequence} is a {entry.kind.value!r} for run "
                f"{entry.get('run')!r} and this file's run is {run!r}."
            )
            continue
        if entry.get("participant") != declared:
            problems.append(
                f"entry {entry.sequence} ends run {run!r} as "
                f"{entry.get('participant')!r} and the run was started as "
                f"{declared!r}. **PR-20260911-R4-2**: the conditions a completion "
                "must satisfy come from the operation that started, so another "
                "participant's evidence never settles this one — Foundry "
                "completion does not observe the web suite's database backends."
            )
            continue
        if entry.get("identity") != start.get("identity"):
            problems.append(
                f"entry {entry.sequence} records identity "
                f"{entry.get('identity')!r} and the run started as "
                f"{start.get('identity')!r}. A changed identity between the start "
                "and the ending is two runs, not one."
            )
            continue
        terminal = entry

    evidence: CompletionEvidence | None = None
    if terminal is not None and terminal.kind is EntryKind.PARTICIPANT_COMPLETED:
        evidence = CompletionEvidence.decode(terminal.get("evidence"))
        if evidence is None:
            problems.append(
                f"entry {terminal.sequence} carries completion evidence that is "
                "not this model's evidence at all. An empty or arbitrary string "
                "does not become proof because the entry's kind says completed."
            )
        else:
            if evidence.run_id != run:
                problems.append(
                    f"entry {terminal.sequence} carries evidence about run "
                    f"{evidence.run_id!r} and this run is {run!r}. Evidence is "
                    "bound to the run it was collected for."
                )
            if not evidence.observed_by.strip():
                problems.append(
                    f"entry {terminal.sequence} names nobody as having observed "
                    "the completion conditions. An unattributed observation is an "
                    "assertion with no author."
                )
            if evidence.conditions != tuple(profile.completion_conditions):
                problems.append(
                    f"entry {terminal.sequence} claims conditions "
                    f"{list(evidence.conditions)} and {declared!r}'s completion "
                    f"requires exactly {list(profile.completion_conditions)}. The "
                    "check is completeness of the content, not presence of the "
                    "field."
                )
            if evidence.reservation_id != reservation:
                problems.append(
                    f"entry {terminal.sequence} carries evidence about reservation "
                    f"{evidence.reservation_id!r} and run {run!r} was started for "
                    f"reservation {reservation!r}. **PR-20260911-R5-1**: the "
                    "reservation a completion names is compared with the one the "
                    "stored start owns, so a release of one reservation cannot "
                    "settle another reservation's harness run. r5 checked only "
                    "that the field was populated, which is a check with nothing "
                    "on the other side of it."
                )
                if not profile.lifecycle_owned_conditions:
                    problems.append(
                        f"entry {terminal.sequence} completes {declared!r}, whose "
                        "conditions are observations of its own processes and "
                        "trees. A reservation on its evidence claims a binding it "
                        "did not establish, and its start requires the field "
                        "empty."
                    )
                elif not evidence.reservation_id.strip():
                    problems.append(
                        f"entry {terminal.sequence} completes {declared!r}, whose "
                        "completion conditions are facts about the reservation it "
                        "concluded, and names no reservation. Lifecycle-owned "
                        "evidence carries the reservation it is bound to, so the "
                        "binding can be checked rather than assumed."
                    )
    if terminal is not None and terminal.kind is EntryKind.PARTICIPANT_RECOVERED:
        if not terminal.get("reference").strip():
            problems.append(
                f"entry {terminal.sequence} recovers run {run!r} and names no "
                "recovery. An unattributable recovery is how an unknown "
                "predecessor becomes a clean one."
            )

    phase = RunPhase.IN_PROGRESS
    if terminal is not None and terminal.kind is EntryKind.PARTICIPANT_COMPLETED:
        phase = RunPhase.COMPLETED
    elif terminal is not None:
        phase = RunPhase.RECOVERED

    return ParticipantRunState(
        ok=not problems,
        problems=tuple(problems),
        run_id=run,
        participant=participant,
        identity=start.get("identity"),
        reservation_id=reservation if not problems else "",
        phase=phase,
        start=start,
        terminal=terminal,
        evidence=evidence,
    )


#: **The semantic check for each record type, chosen by the record's own kinds.**
#:
#: It is a table rather than an argument so that no publication path can be
#: written without one: `DurableRecordStore` looks its own check up here, and a
#: store whose kinds are outside this mapping refuses rather than publishing
#: unchecked. The same functions validate a proposed append before publication
#: and a complete stored history on read, which is R4-1's and R4-2's shared
#: requirement — a safe writer does not excuse an unsafe reader, and a safe
#: reader does not excuse publishing a contradictory history.
HISTORY_SEMANTICS = {
    RESERVATION_KINDS: lambda entries, name: check_reservation_history(
        entries
    ).problems,
    PARTICIPANT_KINDS: lambda entries, name: check_participant_history(
        entries, run_id=name
    ).problems,
}


class RunPhase(str, Enum):
    """Where one participant's run stands in the durable ledger."""

    #: Persisted **before the first relevant effect**. Non-reusable: a successor
    #: refuses while it stands.
    IN_PROGRESS = "in_progress"
    #: Published **after** the stated completion conditions were observed.
    COMPLETED = "completed"
    #: An operator's attributed recovery of an interrupted run. The in-progress
    #: entry stays in the file.
    RECOVERED = "recovered"


@dataclass(frozen=True, slots=True)
class CompletionObservation:
    """Somebody's statement that this participant's conditions were observed.

    `wrapper_exit_status` and `lock_released` are carried **so that the model
    can refuse them**. Neither contributes to completion, and
    `test_a_clean_wrapper_exit_is_not_completion_evidence` is the assertion.
    """

    observed_by: str
    observed: Mapping[str, bool] = field(default_factory=dict)
    wrapper_exit_status: int | None = None
    lock_released: bool = False

    def missing(
        self,
        profile: ParticipantProfile,
        *,
        derived: Mapping[str, bool] | None = None,
    ) -> tuple[str, ...]:
        """Every stated condition this observation, plus `derived`, leaves open.

        `derived` carries the facts the model **owns** and computed from its own
        preceding operations — PR-20260911-R4-3. They are kept separate from
        `observed` so that a caller cannot supply one of them, and so that a
        reader of a refusal can tell an unmade external observation from a
        lifecycle fact that is not yet true.
        """
        facts: dict[str, bool] = dict(self.observed)
        if derived:
            facts.update(derived)
        gaps = [
            condition
            for condition in profile.completion_conditions
            if not facts.get(condition, False)
        ]
        if not self.observed_by.strip():
            gaps.append(
                "nobody is named as having observed the completion conditions"
            )
        return tuple(gaps)

    def injected_lifecycle_facts(
        self, profile: ParticipantProfile
    ) -> tuple[str, ...]:
        """Every lifecycle-owned condition this observation tried to supply.

        **PR-20260911-R4-3's reproduction, refused at the writer.** The harness's
        two conditions are facts about the reservation it is concluding. Setting
        them on an injected observation is how a completion published at T11
        asserted a release that T12 had not yet published, and how the green test
        masked the contradiction.
        """
        return tuple(
            f"{condition!r} is a lifecycle-owned fact: it is derived from the "
            "release decision and the release publication this process performed, "
            "and an injected observation of it is a statement about a step that "
            "may not have happened yet."
            for condition in profile.lifecycle_owned_conditions
            if condition in self.observed
        )


@dataclass(frozen=True, slots=True)
class RunLedgerSurvey:
    """What the durable participant ledger says about every run it holds.

    `unsettled` is the set that blocks every successor — **including the harness
    and the environment reset**, which is R3-2's requirement and not a courtesy
    the six extend to each other.
    """

    unsettled: tuple[str, ...] = ()
    unreadable: tuple[str, ...] = ()
    #: Run files that parsed and are not run histories — a terminal entry with
    #: no start, a completion by another participant, a changed identity, a run
    #: filed under another run's name, evidence that is not evidence.
    #: **PR-20260911-R4-2.** They block exactly as an unsettled run does: an
    #: invalid account of a run is not an account that it ended.
    invalid: tuple[str, ...] = ()
    completed: tuple[str, ...] = ()
    recovered: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    limits: tuple[str, ...] = MODEL_LIMITS

    @property
    def settled(self) -> bool:
        return not self.unsettled and not self.unreadable and not self.invalid


@dataclass(frozen=True, slots=True)
class StoredRun:
    """What the ledger's own bytes say about one run, before a writer acts on it.

    **PR-20260911-R5-1's writer half.** r5's `complete()` took the caller's
    participant, chose that participant's profile, derived the lifecycle facts
    from the caller's release publication and appended to the caller's filename.
    Every one of those is a claim, and the stored start is the only place the
    protocol keeps the answers. A writer therefore reads it **first** and derives
    the profile, the required conditions and the reservation from it.
    """

    run_id: str
    ok: bool
    refusals: tuple[str, ...] = ()
    parsed: ParsedHistory | None = None
    state: ParticipantRunState | None = None
    limits: tuple[str, ...] = MODEL_LIMITS

    def __post_init__(self) -> None:
        if self.ok and (self.refusals or self.state is None):
            raise PlanRefused(
                "A readable stored run carries its validated state and no refusal."
            )
        if not self.ok and not self.refusals:
            raise PlanRefused("A refusal names why.")


class RunLedger:
    """The durable in-progress/completion accounting for all seven participants.

    One file per run, in a provisioned group-writable directory, appended to with
    the same codec and the same publication barriers as the reservation record.
    A run file's **last** entry is its phase.

    **Why a second object rather than more entries in the reservation record.**
    The reservation record is written by the executor as root. Six participants
    run as `ubuntu` and cannot write it, so accounting for their effects inside
    it would require making it group-writable — a permission change that buys
    nothing, because the thing that must survive is the *record*, and a
    group-writable record is one any participant can replace. The ledger is a
    separate group-writable directory instead, and the reservation record keeps
    its stricter mode.

    **What the modes do not do, stated rather than implied.** All seven
    participants run as the same OS user and that user holds passwordless
    `sudo`, so neither the directory's mode nor the record's constrains a
    participant that chooses to ignore the protocol. The modes prevent accidents
    and misdirected writes. Separating the participants' identities would be a
    real barrier and it is a permission decision nobody has taken; it is named
    in the contract's delta as unapproved rather than assumed here.
    """

    def __init__(
        self,
        filesystem: SyntheticFilesystem,
        *,
        directory: str,
        host: str,
        target_identity: str,
        label: str = "/var/lib/freedom-blades/laboratory/runs",
    ) -> None:
        self._fs = filesystem
        self._directory = directory
        self._host = host
        self._target = target_identity
        self._label = label
        self.reseal_fails = False

    def _store(self, run_id: str) -> DurableRecordStore:
        store = DurableRecordStore(
            self._fs,
            directory=self._directory,
            name=run_id,
            label=f"{self._label}/{run_id}",
            kinds=PARTICIPANT_KINDS,
        )
        store.reseal_fails = self.reseal_fails
        return store

    def _entry(
        self,
        *,
        kind: EntryKind,
        run_id: str,
        participant: Participant,
        author: str,
        at: str,
        extra: Mapping[str, str],
    ) -> RecordEntry:
        profile = PARTICIPANT_PROFILES[participant]
        fields = {
            "run": run_id,
            "participant": participant.value,
            "identity": profile.identity,
        }
        fields.update(extra)
        return RecordEntry(
            sequence=1,
            kind=kind,
            host=self._host,
            target=self._target,
            author=author,
            at=at,
            fields=fields,
        )

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

        Exclusive creation, both barriers. The caller issues no effect until this
        returns `published`; a run whose start was never durable is a run whose
        effects nothing accounts for, which is the ordering R3-2 requires and the
        reason it is stated as *before*, not *around*.

        **`reservation_id` is the durable binding — PR-20260911-R5-1.** The
        harness must supply the reservation this run owns, and the other six must
        leave it empty. Neither is enforced here by an early return: the entry
        goes through `publish`, whose semantic check is
        `check_participant_history`, so the writer's rule and the reader's rule
        are the same function rather than two that can drift. A missing, empty or
        misshapen binding therefore refuses as `invalid_history` and writes
        nothing.
        """
        profile = PARTICIPANT_PROFILES[participant]
        entry = self._entry(
            kind=EntryKind.PARTICIPANT_STARTED,
            run_id=run_id,
            participant=participant,
            author=author,
            at=at,
            extra={
                "reservation": reservation_id,
                "effects": "; ".join(profile.effects),
            },
        )
        return self._store(run_id).publish(
            (entry,), exclusive=True, fail_at=fail_at
        )

    def read_run(self, run_id: str) -> StoredRun:
        """Read one run's stored bytes and validate them as that run's history.

        The reader every writer uses before it derives a lifecycle-owned fact,
        and the same parse and the same validator the survey runs. It reads
        through a descriptor and consults no oracle: a writer has no more access
        to the model's durable-state map than a successor does.
        """
        parsed = parse_history(
            self._store(run_id).read_record_bytes(),
            permitted_kinds=PARTICIPANT_KINDS,
            host=self._host,
            target_identity=self._target,
        )
        if not parsed.ok:
            return StoredRun(
                run_id=run_id,
                ok=False,
                refusals=(
                    f"run {run_id!r} refused as {parsed.refusal.value!r}: "
                    + " ".join(parsed.reasons),
                ),
                parsed=parsed,
            )
        state = check_participant_history(parsed.entries, run_id=run_id)
        if not state.ok:
            return StoredRun(
                run_id=run_id,
                ok=False,
                refusals=(
                    f"run {run_id!r} parsed and is not a run history: "
                    + " ".join(state.problems),
                ),
                parsed=parsed,
                state=state,
            )
        return StoredRun(run_id=run_id, ok=True, parsed=parsed, state=state)

    def _reservation_binding_problems(
        self,
        profile: ParticipantProfile,
        reservation: str,
        release_publication: "ReleasePublication | None",
    ) -> tuple[str, ...]:
        """Whether the release publication is about the run's own reservation.

        **PR-20260911-R5-1, at the writer.** The stored start says which
        reservation this run owns. A release publication offered as its
        completion must name exactly that one, and a mismatch refuses before any
        byte is written, so the wrong completion is never published and the run's
        started bytes are left as they were.
        """
        if release_publication is None or not profile.lifecycle_owned_conditions:
            return ()
        if release_publication.reservation_id == reservation:
            return ()
        return (
            f"the release publication concluded reservation "
            f"{release_publication.reservation_id!r} and this run was started for "
            f"reservation {reservation!r}. **PR-20260911-R5-1**: a release of one "
            "reservation does not settle another reservation's harness run, and "
            "the stored start is what the claim is checked against. Nothing is "
            "written and the run stays in progress, so it continues to block "
            "every successor until it is completed or an operator recovers it.",
        )

    def _derived_lifecycle_facts(
        self,
        profile: ParticipantProfile,
        release_publication: "ReleasePublication | None",
    ) -> tuple[dict[str, bool], tuple[str, ...]]:
        """The lifecycle-owned conditions, computed from earlier operations.

        **PR-20260911-R4-3.** The harness's two conditions are the return of
        `reservation.release()` and the return of the reservation record's
        release publication, both performed by this process while it holds the
        lock. They are the writer's own knowledge of its own calls — the one
        durability fact a writer legitimately has, and precisely the fact a
        *successor* does not, which is why a successor re-seals rather than
        reading it.

        Nothing here consults the model's durable-state map, and no participant
        but the harness has an owned condition to derive.
        """
        if not profile.lifecycle_owned_conditions:
            if release_publication is not None:
                return {}, (
                    f"{profile.participant.value!r} has no lifecycle-owned "
                    "completion condition, so a terminal publication is not part "
                    "of its evidence. Its conditions are observations of its own "
                    "processes, backends and trees.",
                )
            return {}, ()
        if release_publication is None:
            return {}, (
                f"{profile.participant.value!r}'s completion conditions are facts "
                "about the reservation this run concluded, and no terminal "
                "publication was supplied. They are derived from the release "
                "decision and the release publication, never injected.",
            )
        return (
            {
                HARNESS_RELEASE_DECIDED: release_publication.released,
                HARNESS_RELEASE_PUBLISHED: release_publication.entry_is_published,
            },
            (),
        )

    def complete(
        self,
        *,
        run_id: str,
        participant: Participant,
        author: str,
        at: str,
        observation: CompletionObservation,
        release_publication: "ReleasePublication | None" = None,
        fail_at: str = "",
    ) -> PublicationOutcome:
        """Publish reusable completion, and only on observed conditions.

        A condition the observer did not state is a condition that was not
        observed, and the publication refuses naming each gap. A zero exit status
        and a released lock are carried on the observation and contribute
        nothing.

        Two things changed in r5. **The lifecycle-owned conditions are derived**
        from `release_publication` rather than injected, and an observation that
        supplies one is refused — PR-20260911-R4-3. And the evidence is written
        as a bounded `CompletionEvidence` naming this run, this participant's
        exact conditions and the observer, so a reader checks its content rather
        than its presence — PR-20260911-R4-2.

        **The participant binding is not trusted from this call.** `append` sends
        the extended history through `check_participant_history`, which compares
        it with the **stored start**, so completing a web run as the Foundry
        suite refuses at publication and leaves the web run's bytes intact.

        **r6 reads the stored start before it derives anything —
        PR-20260911-R5-1.** The profile whose conditions must hold, and the
        reservation written into the evidence, both come from the stored entry
        rather than from this call's arguments. A caller's `participant`,
        `run_id`, reservation and `release_publication` are checked claims: the
        participant must match the stored one, and the release publication must
        name the reservation the stored start owns. r5 derived the profile from
        the caller and copied the reservation off the publication, so a release
        of reservation A produced valid-looking evidence for a run started for
        reservation B.
        """
        stored = self.read_run(run_id)
        if not stored.ok:
            return PublicationOutcome(
                published=False,
                refusal=PublicationRefusal.UNREADABLE_PREDECESSOR,
                reasons=(
                    f"the stored start of run {run_id!r} is not a readable run "
                    "history, so there is nothing to derive a completion from and "
                    "nothing was written. A completion is a statement about a run "
                    "somebody recorded beginning.",
                )
                + stored.refusals,
            )
        state = stored.state
        stored_participant = state.participant if state is not None else None
        if stored_participant is not participant:
            started_as = (
                stored_participant.value if stored_participant is not None else None
            )
            return PublicationOutcome(
                published=False,
                refusal=PublicationRefusal.INVALID_HISTORY,
                reasons=(
                    f"this call completes run {run_id!r} as "
                    f"{participant.value!r} and the stored start records "
                    f"{started_as!r}. **PR-20260911-R4-2**: the "
                    "conditions a completion must satisfy come from the operation "
                    "that started, so the caller's participant is a checked claim "
                    "and another participant's evidence never settles this one. "
                    "Nothing was written and the stored bytes are unchanged.",
                ),
            )
        profile = PARTICIPANT_PROFILES[stored_participant]
        reservation = state.reservation_id
        derived, derivation_problems = self._derived_lifecycle_facts(
            profile, release_publication
        )
        gaps = (
            observation.injected_lifecycle_facts(profile)
            + derivation_problems
            + self._reservation_binding_problems(
                profile, reservation, release_publication
            )
            + observation.missing(profile, derived=derived)
        )
        if gaps:
            return PublicationOutcome(
                published=False,
                refusal=PublicationRefusal.NOT_DURABLE,
                reasons=(
                    f"completion of {participant.value!r} was not established: "
                    f"{list(gaps)}. A run publishes reusable completion only "
                    "after its stated conditions hold, and "
                    f"{NOT_COMPLETION_EVIDENCE[0]}",
                ),
            )
        evidence = CompletionEvidence(
            run_id=state.run_id,
            observed_by=observation.observed_by,
            conditions=tuple(profile.completion_conditions),
            reservation_id=reservation,
        )
        entry = self._entry(
            kind=EntryKind.PARTICIPANT_COMPLETED,
            run_id=run_id,
            participant=participant,
            author=author,
            at=at,
            extra={"evidence": evidence.encode()},
        )
        return self._store(run_id).append(
            entry,
            host=self._host,
            target_identity=self._target,
            fail_at=fail_at,
        )

    def recover(
        self,
        *,
        run_id: str,
        participant: Participant,
        author: str,
        at: str,
        reference: str,
        fail_at: str = "",
    ) -> PublicationOutcome:
        """Append an operator's attributed recovery of an interrupted run.

        The in-progress entry stays in the file: the quarantine history of a run
        is preserved, and recovery is the entry that follows it rather than a
        replacement for it. A recovery with no named author or no reference
        refuses, because an unattributable recovery is how an unknown
        predecessor becomes a clean one.
        """
        if not author.strip() or not reference.strip():
            return PublicationOutcome(
                published=False,
                refusal=PublicationRefusal.NOT_DURABLE,
                reasons=(
                    "a recovery names who performed it and which recovery it "
                    "was. An unattributed recovery is an assertion with no "
                    "author.",
                ),
            )
        entry = self._entry(
            kind=EntryKind.PARTICIPANT_RECOVERED,
            run_id=run_id,
            participant=participant,
            author=author,
            at=at,
            extra={"reference": reference},
        )
        return self._store(run_id).append(
            entry,
            host=self._host,
            target_identity=self._target,
            fail_at=fail_at,
        )

    def reseal(self) -> None:
        """Make the ledger directory's own entries durable, per RESEAL_CONTRACT."""
        if self.reseal_fails:
            raise ModelRefused(
                f"the durability barrier on {self._label} did not return "
                "success, so this participant cannot establish that the run "
                "entries it is about to read would survive a power loss."
            )
        self._fs.fsync(
            self._fs.open_directory(
                self._directory, DescriptorMode.O_RDONLY, self._label
            ).number,
            barrier=f"reseal:{self._label}",
        )

    def survey(self) -> RunLedgerSurvey:
        """Read every run file and classify it, fail-closed.

        A run file that will not parse counts as **unreadable**, not as absent,
        and an unreadable run blocks exactly as an unsettled one does. A leftover
        publication temporary is an interrupted publication and blocks too: a run
        that was starting when its writer died is a run whose effects may have
        begun.

        **The phase comes from the validated history, not from the last entry —
        PR-20260911-R4-2.** Revision 4 declared a file settled from its final
        entry's kind, so a lone `participant_completed` entry with no start, a
        completion by another participant and a completion carrying an empty
        evidence string all read as settled runs. Every file now goes through
        `check_participant_history`, bound to the name it is stored under, and a
        file that is not a run history is `invalid` and blocks.
        """
        unsettled: list[str] = []
        unreadable: list[str] = []
        invalid: list[str] = []
        completed: list[str] = []
        recovered: list[str] = []
        reasons: list[str] = []

        for name in self._fs.now().listing(self._directory):
            if name.endswith(".tmp"):
                unreadable.append(name)
                reasons.append(
                    f"{name!r} is a publication temporary, so a run entry was "
                    "being written when its writer stopped. It is reported and "
                    "not removed, and it blocks until an operator establishes "
                    "what it was."
                )
                continue
            parsed = parse_history(
                self._store(name).read_record_bytes(),
                permitted_kinds=PARTICIPANT_KINDS,
                host=self._host,
                target_identity=self._target,
            )
            if not parsed.ok:
                unreadable.append(name)
                reasons.append(
                    f"run {name!r} refused as {parsed.refusal.value!r}: "
                    + " ".join(parsed.reasons)
                )
                continue
            state = check_participant_history(parsed.entries, run_id=name)
            if not state.ok:
                invalid.append(name)
                reasons.append(
                    f"run {name!r} parsed and is not a run history: "
                    + " ".join(state.problems)
                    + " An invalid account of a run is not an account that it "
                    "ended, so it blocks until an operator establishes what it "
                    "was."
                )
                continue
            if state.phase is RunPhase.COMPLETED:
                completed.append(name)
            elif state.phase is RunPhase.RECOVERED:
                recovered.append(name)
            else:
                unsettled.append(name)
                reasons.append(
                    f"run {name!r} ({state.start.get('participant')}) is still "
                    "in progress in the durable ledger. Its declared effects are "
                    f"{state.start.get('effects')!r}, and nothing has published "
                    "that they ended."
                )
        return RunLedgerSurvey(
            unsettled=tuple(sorted(unsettled)),
            unreadable=tuple(sorted(unreadable)),
            invalid=tuple(sorted(invalid)),
            completed=tuple(sorted(completed)),
            recovered=tuple(sorted(recovered)),
            reasons=tuple(reasons),
        )


# ---------------------------------------------------------------------------
# The terminal publications, and the order between them — PR-20260911-R4-3
# ---------------------------------------------------------------------------


#: **The order between the two terminal publications, and why it is this one.**
#:
#: Revision 4 declared T11 (participant completion) before T12 (RELEASED) while
#: the harness's completion profile required the release to have been decided
#: *and* published. No process could obtain that observation in that order, and
#: the successful test hid it by injecting both facts at t3 while the reservation
#: record still said RUNNING. Moving an assertion would not have fixed it: the
#: sequence itself had no reachable successful path.
TERMINAL_PUBLICATION_ORDER = (
    "0. **Check the reservation binding against the stored start**, before any "
    "publication. The run this conclusion names must be a readable harness run, "
    "still in progress, whose stored `participant_started` entry owns exactly "
    "the reservation being concluded. A mismatch refuses here, so **no release "
    "entry and no completion is published** and the reservation stays where it "
    "was. **This is PR-20260911-R5-1**: r5 had no such step, took the run id "
    "from the caller, and published a valid release of A followed by a valid "
    "completion into an already-started run B.",
    "1. **Evaluate the release decision.** `reservation.release()` over the "
    "observed evidence returns RELEASED or quarantines. A refused decision "
    "publishes no release entry and no completion, so neither half is reached.",
    "2. **Publish the reservation's RELEASED entry durably**, under the lock, "
    "bytes then rename then containing entry. The executor is the writer, so "
    "the success of its own barriers is knowledge it legitimately has.",
    "3. **Publish the harness participant's completion**, whose two conditions "
    "are exactly the outcomes of steps 1 and 2 and are derived from them. It "
    "names the reservation it concluded, so the binding can be checked.",
    "4. **Release the lock**, last, so both publications happened under it.",
    "**Why reuse is not authorized by either half alone.** Before step 2 the "
    "reservation record still says RUNNING, and RUNNING refuses every "
    "successor. Between steps 2 and 3 the reservation says RELEASED and the "
    "harness's run is still `participant_started` in the ledger, and an "
    "unsettled run refuses every successor including the harness and the "
    "environment reset. So no instant of this sequence admits anybody on one "
    "satisfied half.",
    "**What a restart between the two publications finds.** The RELEASED entry, "
    "whose durability the successor re-establishes under the lock or refuses "
    "(R3-1), and an unsettled harness run that blocks it regardless. The "
    "bounded recovery is an operator's attributed `participant_recovered` entry "
    "for that run, after which a new reservation is admitted on the stored "
    "release. Nothing is rewritten and the quarantine path is unaffected.",
    "**Why not the reverse order.** Completing the participant first would "
    "require its evidence to assert a release that had not been published, "
    "which is the contradiction R4-3 found. Weakening the harness's completion "
    "conditions to drop the publication requirement would let a run be settled "
    "while the record still said RUNNING, so the reservation's own state and "
    "the ledger would disagree about the same run.",
)


@dataclass(frozen=True, slots=True)
class ReleasePublication:
    """What the executor observed of its own terminal publication.

    Two facts and no third, and each is the return value of a call this process
    made: what `reservation.release()` decided, and what publishing the RELEASED
    entry returned. **Neither is read back from the record and neither consults
    the model's durable-state map**, because a reader has access to neither —
    that asymmetry is R3-1 and it is preserved here rather than softened.
    """

    reservation_id: str
    decision: ReservationState
    decision_reasons: tuple[str, ...] = ()
    publication: PublicationOutcome | None = None

    @property
    def released(self) -> bool:
        return self.decision is ReservationState.RELEASED

    @property
    def entry_is_published(self) -> bool:
        """Whether this process's own barriers both returned success.

        The containing-directory barrier is the one that matters: a rename
        without it leaves the entry visible and not durable, which is exactly
        the state a successor must re-seal.
        """
        return (
            self.publication is not None
            and self.publication.published
            and "record-entry" in self.publication.barriers
        )


@dataclass(frozen=True, slots=True)
class TerminalPublication:
    """The result of concluding one reservation in the order above."""

    reservation_id: str
    run_id: str
    decision: ReservationState
    decision_reasons: tuple[str, ...] = ()
    release_entry: PublicationOutcome | None = None
    completion: PublicationOutcome | None = None
    refusals: tuple[str, ...] = ()
    limits: tuple[str, ...] = MODEL_LIMITS

    @property
    def concluded(self) -> bool:
        """Both terminal publications reached durable storage."""
        return (
            self.release_entry is not None
            and self.release_entry.published
            and self.completion is not None
            and self.completion.published
        )


def conclude_reservation(
    *,
    record: DurableRecordStore,
    ledger: RunLedger,
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
    """Decide the release, publish it, then complete the harness's own run.

    `TERMINAL_PUBLICATION_ORDER` is the argument; this is the order. Every step
    is attempted even when an earlier one leaves an intermediate state, because
    the point of the sequence is that **an intermediate state refuses rather
    than half-authorizing reuse**: a release entry that did not reach its
    barrier leaves `entry_is_published` false, the completion refuses naming it,
    and the run stays unsettled until an operator recovers it.

    `fail_release_at` and `fail_completion_at` inject a failure at
    `"record-data"`, `"rename"` or `"record-entry"` in either publication, which
    is how the crash and barrier-failure cases between the two are exercised.

    **Step 0 is the reservation binding and it comes before the release decision
    — PR-20260911-R5-1.** `run_id` is a caller's claim about which run this
    reservation owns, and the ledger's stored start is the only place the
    protocol records the answer. The claim is checked first, because publishing a
    RELEASED entry for a reservation whose harness run cannot then be settled
    would leave an intermediate state needing an operator recovery for a mistake
    that was detectable before any byte was written. On a mismatch nothing is
    published: the reservation record is untouched, the named run's started bytes
    are unchanged, and that run still blocks every successor.
    """
    stored = ledger.read_run(run_id)
    binding: list[str] = []
    if not stored.ok:
        binding.append(
            f"run {run_id!r} is not a readable harness run history, so this "
            "conclusion cannot establish that the reservation being concluded "
            "owns it."
        )
        binding.extend(stored.refusals)
    else:
        state = stored.state
        if state is None or state.participant is not Participant.HARNESS_CLI:
            started_by = state.participant if state is not None else None
            binding.append(
                f"run {run_id!r} was started by "
                f"{started_by.value if started_by is not None else None!r}, "
                "and the reservation's terminal "
                "publication completes the harness's own run. Another "
                "participant's run is settled by its own observed conditions, "
                "never by a release."
            )
        elif state.reservation_id != request.reservation_id:
            binding.append(
                f"run {run_id!r} was started for reservation "
                f"{state.reservation_id!r} and this conclusion is of "
                f"{request.reservation_id!r}. **PR-20260911-R5-1**: a release "
                "settles the harness run that the stored start says belongs to "
                "the same reservation, and nothing else. Neither terminal entry "
                "is published, the reservation stays where it was, and the named "
                "run stays in progress and keeps blocking every successor."
            )
        elif state.phase is not RunPhase.IN_PROGRESS:
            binding.append(
                f"run {run_id!r} is already {state.phase.value!r} in the durable "
                "ledger. A settled run is not concluded a second time, and a "
                "recovered one is terminal."
            )
    if binding:
        return TerminalPublication(
            reservation_id=request.reservation_id,
            run_id=run_id,
            decision=current_state,
            refusals=tuple(binding)
            + (
                "No release entry and no completion was published, so the "
                "stored bytes of both objects are exactly what they were.",
            ),
        )

    outcome = release(
        request=request, current_state=current_state, evidence=evidence
    )
    if outcome.state is not ReservationState.RELEASED:
        return TerminalPublication(
            reservation_id=request.reservation_id,
            run_id=run_id,
            decision=outcome.state,
            decision_reasons=outcome.reasons,
            refusals=(
                "the release decision did not return RELEASED, so no release "
                "entry is published and the harness's run is not completed. The "
                "reservation stays where it was and every successor refuses on "
                "it, which is the fail-closed half of step 1.",
            )
            + outcome.reasons,
        )

    release_entry = record.append(
        RecordEntry(
            sequence=1,
            kind=EntryKind.RELEASED,
            host=request.host,
            target=request.target_identity,
            author=author,
            at=at,
            fields={"reservation": request.reservation_id, "released_at": at},
        ),
        host=request.host,
        target_identity=request.target_identity,
        fail_at=fail_release_at,
    )
    publication = ReleasePublication(
        reservation_id=request.reservation_id,
        decision=outcome.state,
        decision_reasons=outcome.reasons,
        publication=release_entry,
    )
    completion = ledger.complete(
        run_id=run_id,
        participant=Participant.HARNESS_CLI,
        author=author,
        at=at,
        observation=CompletionObservation(observed_by=observed_by),
        release_publication=publication,
        fail_at=fail_completion_at,
    )

    refusals: list[str] = []
    if not release_entry.published:
        refusals.append(
            "the release entry did not reach durable storage: "
            + " ".join(release_entry.reasons)
        )
    if not completion.published:
        refusals.append(
            "the harness's run was not completed: " + " ".join(completion.reasons)
        )
    return TerminalPublication(
        reservation_id=request.reservation_id,
        run_id=run_id,
        decision=outcome.state,
        decision_reasons=outcome.reasons,
        release_entry=release_entry,
        completion=completion,
        refusals=tuple(refusals),
    )


# ---------------------------------------------------------------------------
# The connected protocol — one reader, from bytes to decision
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SuccessorAdmission:
    """One participant's complete pass from stored bytes to a decision."""

    participant: Participant
    may_proceed: bool
    refusals: tuple[str, ...] = ()
    resealed: bool = False
    parsed: ParsedHistory | None = None
    history: LifecycleHistory | None = None
    validation: LifecycleValidation | None = None
    runs: RunLedgerSurvey | None = None
    limits: tuple[str, ...] = MODEL_LIMITS

    def __post_init__(self) -> None:
        if self.may_proceed and self.refusals:
            raise PlanRefused("An admission that proceeds carries no refusal.")
        if not self.may_proceed and not self.refusals:
            raise PlanRefused("A refusal names why.")


def read_and_admit(
    *,
    participant: Participant,
    record: DurableRecordStore,
    ledger: RunLedger | None,
    lock: LockView,
    host: str,
    target_identity: str,
    read_by: str,
    read_at: str,
    reservation_id: str = "",
    quarantine: QuarantineRecord | None = None,
    policy: AdmissionPolicy = AdmissionPolicy.R4_ESTABLISHES_DURABILITY_UNDER_THE_LOCK,
) -> SuccessorAdmission:
    """The whole successor protocol, in the order a real participant runs it.

    1. **the lock** — free, or wait or refuse. Never proceed past a held one;
    2. **the re-seal** — under `R4_ESTABLISHES_DURABILITY_UNDER_THE_LOCK`,
       `fsync` the record's and the ledger's containing entries before reading
       anything, so whatever this reader is about to act on would survive a
       power loss. A failure is a refusal naming the recovery owner. Under
       `R3_TRUSTS_THE_VISIBLE_RECORD` this step does not happen, which is the
       negative control;
    3. **the bytes** — read the record through a descriptor. Absent refuses, and
       initialization is the only way out of absent;
    4. **the parse** — `parse_history`, which refuses malformed, truncated,
       unsupported, contradictory, missing-binding and wrong-binding records
       rather than normalizing any of them;
    5. **the order** — `check_history_semantics`, so a history that is not one
       produces no decision input and no earlier convenient admitting entry is
       selected;
    6. **the shared validator** — `reservation.validate_lifecycle()`, over a
       `LifecycleHistory` derived from the stored bytes rather than constructed
       beside them. This is the connection R3-3 found missing; and
    7. **the ledger** — every participant's durable in-progress accounting. An
       unsettled, unreadable or invalid run refuses every successor, the harness
       and the environment reset included, until its recovery is published. This
       is R3-2, and **a ledger that was not supplied refuses too** — R4-2's
       second path, where `ledger=None` skipped both the re-seal and the survey
       and admitted with an unfinished web run outstanding.

    Nothing here observes the model's durable-state map, and nothing here reads
    a live host: the only inputs are bytes obtained through a descriptor and
    observations the caller supplies.
    """
    refusals: list[str] = []

    if lock.observation_failed:
        refusals.append(
            "the cooperative lock could not be read. A lock whose state is "
            "unknown is not an unheld lock."
        )
    elif lock.held_by is not None:
        refusals.append(
            f"the cooperative lock is held by {lock.held_by!r}. The rule for all "
            "seven participants is wait or refuse, never proceed."
        )
    if refusals:
        return SuccessorAdmission(
            participant=participant, may_proceed=False, refusals=tuple(refusals)
        )

    resealed = False
    if policy is AdmissionPolicy.R4_ESTABLISHES_DURABILITY_UNDER_THE_LOCK:
        try:
            record.reseal()
            if ledger is not None:
                ledger.reseal()
        except ModelRefused as refusal:
            return SuccessorAdmission(
                participant=participant,
                may_proceed=False,
                refusals=(
                    str(refusal),
                    "This participant refuses pending an attributable operator "
                    "recovery. It does not proceed on the visible record: an "
                    "existing name proves a rename happened and proves nothing "
                    "about the barrier that was supposed to follow it.",
                ),
            )
        resealed = True

    parsed = parse_history(
        record.read_record_bytes(),
        permitted_kinds=RESERVATION_KINDS,
        host=host,
        target_identity=target_identity,
    )
    if not parsed.ok:
        refusals.append(
            f"the stored lifecycle record refused as {parsed.refusal.value!r}."
        )
        refusals.extend(parsed.reasons)
        if parsed.refusal is RecordRefusal.ABSENT:
            refusals.append(
                "Initialization is the only way out of an absent record, and it "
                "refuses on a host that has been used before."
            )
    else:
        refusals.extend(check_history_semantics(parsed.entries))

    history = derive_lifecycle_history(
        parsed, host=host, read_by=read_by, read_at=read_at
    )
    validation = validate_lifecycle(
        history=history,
        host=host,
        target_identity=target_identity,
        reservation_id=reservation_id,
    )
    for reason in validation.refusals:
        if reason not in refusals:
            refusals.append(reason)
    if validation.admits and history.disposition not in ADMITTING_OUTCOMES:
        refusals.append(
            "the validated outcome is not in the allowlist "
            f"{sorted(value.value for value in ADMITTING_OUTCOMES)}."
        )

    survey = ledger.survey() if ledger is not None else None
    if survey is None:
        refusals.append(
            "no durable participant ledger was supplied to this admission. "
            "**PR-20260911-R4-2**: contract §5.8 requires the ledger for every "
            "participant, so unavailable accounting is a refusal and never an "
            "empty, settled ledger. The isolated reservation-layer unit path is "
            "`participant_may_proceed`, which decides a history on its own and "
            "is labelled as deciding nothing about a participant's run."
        )
    elif not survey.settled:
        refusals.append(
            f"the durable participant ledger has unsettled runs "
            f"{list(survey.unsettled)}, unreadable runs "
            f"{list(survey.unreadable)} and invalid runs "
            f"{list(survey.invalid)}. An uncertain predecessor blocks every "
            "successor, this one included, until its recovery is published. "
            f"{NOT_COMPLETION_EVIDENCE[1]}"
        )
        refusals.extend(survey.reasons)

    if quarantine is not None and quarantine.host == host:
        refusals.append(
            f"host {host!r} carries a quarantine record from reservation "
            f"{quarantine.reservation_id!r}. No participant proceeds against a "
            "quarantined host."
        )
        if participant is Participant.ENVIRONMENT_RESET:
            refusals.append(
                "the environment reset refuses especially: a reset would destroy "
                "the residue the quarantine exists to preserve."
            )

    return SuccessorAdmission(
        participant=participant,
        may_proceed=not refusals,
        refusals=tuple(refusals),
        resealed=resealed,
        parsed=parsed,
        history=history,
        validation=validation,
        runs=survey,
    )

__all__ = [
    "ADMITTING_OUTCOMES",
    "AdmissionPolicy",
    "COMMON_FIELDS",
    "CompletionEvidence",
    "CompletionObservation",
    "DurableRecordStore",
    "ENTRY_STATES",
    "EVIDENCE_SEPARATOR",
    "EntryKind",
    "FIRST_USE_RECOVERY",
    "FREE_LOCK_AUTHORIZES_NOTHING",
    "FirstUseEvidence",
    "FirstUseRefusal",
    "HARNESS_RELEASE_DECIDED",
    "HARNESS_RELEASE_PUBLISHED",
    "HISTORY_ORDER_RULES",
    "HISTORY_SEMANTICS",
    "HISTORY_TERMINATOR",
    "InitializationOutcome",
    "KIND_FIELDS",
    "NOT_COMPLETION_EVIDENCE",
    "PARTICIPANTS",
    "PARTICIPANT_KINDS",
    "PARTICIPANT_PROFILES",
    "PARTICIPATING_ENTRY_POINTS",
    "PROPOSED_PROVISIONING",
    "PUBLICATION_UNCERTAINTY",
    "ParsedHistory",
    "Participant",
    "ParticipantDecision",
    "ParticipantProfile",
    "ParticipantRunState",
    "PublicationOutcome",
    "PublicationRefusal",
    "RECORD_ATTRIBUTION",
    "RECORD_MAGIC",
    "RECORD_SCHEMA_VERSION",
    "RESEAL_CONTRACT",
    "RESERVATION_BINDING",
    "RESERVATION_KINDS",
    "RecordEntry",
    "RecordRefusal",
    "ReleasePublication",
    "ReservationHistoryState",
    "RunLedger",
    "RunLedgerSurvey",
    "RunPhase",
    "SUPPORTED_SCHEMA_VERSIONS",
    "StoredRun",
    "SuccessorAdmission",
    "TERMINAL_PUBLICATION_ORDER",
    "TERMINAL_STATES",
    "TerminalPublication",
    "UNIT_TEST_CONSTRUCTORS",
    "check_history_semantics",
    "check_participant_history",
    "check_reservation_history",
    "conclude_reservation",
    "crash_between_admitted_and_running",
    "derive_lifecycle_history",
    "environment_reset_history",
    "initialize_first_use_record",
    "parse_history",
    "participant_may_proceed",
    "read_and_admit",
    "reservation_field_problems",
    "serialize_history",
    "survey",
]
