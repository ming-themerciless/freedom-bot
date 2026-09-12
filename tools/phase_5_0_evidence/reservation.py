"""Whole-host reservation, cooperative admission, and the release that is never
assumed — direction **C-P5.0-LAB-1**.

## What this is, and the three things it is not

Peter's 2026-09-10 direction replaces the proposed VM controller with an
**exclusively reserved disposable laboratory**: the whole of `oracle-test`,
including `freedom_test` and `freedom_dev`, is held by one accountable executor
for the length of a run, and every other agent, maintainer, CI job,
synchronization and dependency update waits for a verified release.

This module is the **decision half** of that: the state machine, the
owner/target contract, the admission rules and the release conditions, written
as pure functions over injected observations so every one of them can be tested
with an injected effect and none of them can touch a host.

It is emphatically **not** three things the direction rules out:

* **not a VM manager, a distributed scheduler or a lease service.** It is one
  record about one host. There is no election, no renewal protocol, no remote
  party and no takeover;
* **not a claim that root cannot interfere.** Host administrators are trusted to
  obey the reservation. That is an *operational exclusion*, and the direction is
  explicit that it is *"not a claim that root is technically unable to
  interfere."* Nothing here revokes a permission from anybody, and no polling
  scheme in it is offered as proof against a malicious host root; and
* **not a general privileged shell.** It runs nothing. `admit()` returns a
  decision and `release()` returns a state.

## Why a lock is not enough, and why there is still a lock

A cooperative lock establishes that every participant that *asks* is serialized.
It establishes nothing about a writer that never asked. So admission has two
halves and needs both:

1. the **lock**, which excludes every cooperating entry point — the project's
   test runners, the synchronization step and the harness itself, enumerated in
   `PARTICIPATING_ENTRY_POINTS`; and
2. the **inventory**, which accounts for every session, test process, timer and
   service that is actually running. Each one is a required service, a reviewed
   test process, or a reason to refuse.

`UNKNOWN` is a refusal and never anything else. The direction is explicit about
what must *not* follow from it: *"Never kill an unknown process or disable an
unknown service to obtain admission."* So `admit()` returns a refusal naming the
writer, and the operator decides. There is no `force`, no `--kill-stale` and no
argument that would add one.

## Why a free lock is not a released predecessor — the September 11 correction

The first version of this module admitted on three observations: a lock nobody
held, an inventory that was complete with nothing unknown, and no quarantine
record in hand. Finding **PR-20260911-3** showed that those three cannot
distinguish a host nobody has ever reserved from one whose executor died in the
middle of a run, because the process lock disappears with the process either way
and a quiet inventory is compatible with a server-side transaction the run left
open.

So admission now takes a fourth observation, `LifecycleHistory`, and it has no
default. Admission requires a **positive statement about the predecessor** —
verified first use, or a verified release bound to this host and that
reservation, or a completed operator recovery — and refuses on missing history,
unreadable history, incomplete history, an unclassified predecessor and an
active, recovering or quarantined one. `DURABLE_RECORD_ORDERING` states the
ordering the record must be written in for any of that to mean anything, and in
particular why the **absence of a quarantine record is never evidence** that a
predecessor ended.

Finding **PR-20260911-4** was the same mistake on the way out: the residue check
had no *not made* value, so a caller who never looked released the host, and
`advance()` moved a reservation to `RELEASED` on nothing but a table lookup.
`ResidueObservation` gives the search its three states and `GUARDED_TRANSITIONS`
makes the two transitions that grant something require the decision that
establishes it.

## Why an expiry cannot release anything

A crash, an expired deadline or a released process lock says that a *parent*
stopped. It says nothing about child processes, about a server-side transaction
that has not committed yet, or about a restoration that was half done.

So there is no transition from an expired or crashed run to `RELEASED`, and none
from `QUARANTINED` to anything reusable. An uncertain run goes to `RECOVERING`
and then to `QUARANTINED` unless an operator attestation establishes all three
of: that every child process ended, that residue is accounted for, and that
restoration was verified or a separately approved rebuild was performed.
`QUARANTINED` has no outgoing edge at all — *"Lock release or timeout cannot make
quarantine reusable."*

## What this decides, and what would have to exist for it to matter

These are pure functions. They persist nothing, take no lock and enforce
nothing, and an `AdmissionDecision` that admits is not a reservation:
`DECISIONS_DO_NOT_PERSIST` says so where a caller will read it, and
`ADAPTER_RESPONSIBILITIES` names what an eventual adapter owns — the lock, the
durable record and its ordering, the inventory, the real release observations,
and any enforcement at all. **None of that is implemented in this pass**, and no
claim here is that a reservation is enforced by anything today.

## Isolation

Planning tier. No process, no file, no socket, no database, no product import.
Every observation — the lock's holder, the host inventory, the durable lifecycle
record, the clock, whether a child process ended — arrives as an argument from a
caller that made it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Sequence

from .errors import PlanRefused

#: The one cooperative lock, named once. It is an ordinary file on the
#: disposable host under a path no experiment writes to, and it is **advisory**:
#: it excludes participants that take it and nobody else, which is the whole of
#: what a cooperative lock can do.
HOST_LOCK_PATH = "/run/freedom-blades/laboratory.lock"

#: Every project entry point that must take `HOST_LOCK_PATH` before it touches
#: the disposable host, and what it does when the lock is held.
#:
#: The rule is the same for all of them and it is *wait or refuse*, never
#: proceed: a run that skipped the lock because it was "only reading" is a writer
#: the next inventory cannot account for.
PARTICIPATING_ENTRY_POINTS: Mapping[str, str] = {
    "tests/test_*.py (bot suite)": (
        "takes the lock for the whole serial bot run and releases it after the "
        "last test; refuses to start while another reservation holds it"
    ),
    "tests/web (web suite)": (
        "takes the lock for the whole serial web run. It shares one disposable "
        "database with the bot suite — finding F-6 — so the two are serialized "
        "by this lock as well as by the run-suites procedure"
    ),
    "foundry-module/tests (node --test)": (
        "takes the lock. It touches no database, and it is still a participant: "
        "a reservation is of the whole host, not of the database"
    ),
    "docs/operations/disposable-test-server.md §3.2 synchronization": (
        "takes the lock before rsync and holds it until the tree is consistent. "
        "A synchronization during another reservation substitutes the source "
        "under a running experiment, which is the defect class EH-R16-1 is about"
    ),
    "docs/operations/disposable-test-server.md §3.5 dependency updates": (
        "takes the lock. `uv pip install` rewrites the interpreter the reviewed "
        "case program runs under"
    ),
    "docs/operations/disposable-test-server.md §4 environment reset": (
        "takes the lock, and additionally refuses while a quarantine record "
        "exists: a reset that erased the residue an operator has not accounted "
        "for would destroy the evidence the quarantine exists to preserve"
    ),
    "tools/phase_5_0_evidence/execution/cli.py": (
        "takes the lock for the reservation, not merely for the run, and holds "
        "it across provisioning, execution, capture, restoration and cleanup"
    ),
}

#: What the lock does **not** do, stated where a reader of the lock will see it.
LOCK_LIMITS = (
    "The lock is advisory and cooperative. It excludes entry points that take "
    "it and nothing else.",
    "It revokes no permission. Manual root access to the disposable host remains "
    "a trusted operational premise, exactly as it is today; an administrator who "
    "ignores the reservation is not prevented by this mechanism and is not "
    "claimed to be.",
    "Holding it is not evidence that the host is quiet. That is what the "
    "inventory is for, and an inventory with an unaccounted writer refuses "
    "admission however the lock stands.",
    "Releasing it is not evidence that the run ended. Release requires the "
    "separate observations in `ReleaseEvidence`.",
)


class ReservationState(str, Enum):
    """The six states the direction names, and no seventh.

    `QUARANTINED` is terminal. Every other state has at least one successor and
    it has none, which is the structural form of *"an uncertain run stays
    quarantined until the operator establishes termination, accounts for residue
    and verifies restoration or separately approved rebuild."*
    """

    REQUESTED = "requested"
    ADMITTED = "admitted"
    RUNNING = "running"
    RECOVERING = "recovering"
    RELEASED = "released"
    QUARANTINED = "quarantined"


#: The transitions this machine admits. A pair absent from this table is not a
#: transition, and `advance()` refuses it by name rather than by falling through.
#:
#: Three absences are the load-bearing ones:
#:
#: * `QUARANTINED` maps to the empty set — nothing reuses a quarantined host;
#: * `RUNNING` does **not** map to `RELEASED` directly in this table's reading of
#:   a *crash*; it maps there only through `release()`, which requires evidence;
#: * `RECOVERING` does not map to `ADMITTED`. Recovery ends a reservation; it
#:   never resumes one.
TRANSITIONS: Mapping[ReservationState, frozenset[ReservationState]] = {
    ReservationState.REQUESTED: frozenset(
        {ReservationState.ADMITTED, ReservationState.QUARANTINED}
    ),
    ReservationState.ADMITTED: frozenset(
        {ReservationState.RUNNING, ReservationState.RELEASED,
         ReservationState.RECOVERING, ReservationState.QUARANTINED}
    ),
    ReservationState.RUNNING: frozenset(
        {ReservationState.RELEASED, ReservationState.RECOVERING,
         ReservationState.QUARANTINED}
    ),
    ReservationState.RECOVERING: frozenset(
        {ReservationState.RELEASED, ReservationState.QUARANTINED}
    ),
    ReservationState.RELEASED: frozenset(),
    ReservationState.QUARANTINED: frozenset(),
}


class WriterDisposition(str, Enum):
    """What an inventoried writer is, from a closed vocabulary of three.

    There is no `IGNORED` and no `PROBABLY_FINE`. A writer nobody classified is
    `UNKNOWN`, and `UNKNOWN` refuses admission.
    """

    #: A service the host requires and the reservation does not disturb.
    REQUIRED_SERVICE = "required_service"
    #: A test process belonging to this reservation's own reviewed plan.
    REVIEWED_TEST_PROCESS = "reviewed_test_process"
    #: Anything else. A reason to refuse, and never a reason to kill anything.
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class Writer:
    """One session, process, timer or service the inventory found."""

    name: str
    kind: str
    disposition: WriterDisposition
    #: Who accounted for it, and against what. Empty for `UNKNOWN`, because an
    #: unaccounted writer is precisely one nobody attributed.
    accounted_by: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.kind.strip():
            raise PlanRefused("An inventoried writer has a name and a kind.")
        if self.disposition is WriterDisposition.UNKNOWN and self.accounted_by.strip():
            raise PlanRefused(
                f"Writer {self.name!r} is declared unknown and also accounted "
                "for. One of the two is wrong, and guessing which is how an "
                "unaccounted writer becomes an accounted one."
            )
        if self.disposition is not WriterDisposition.UNKNOWN and not self.accounted_by.strip():
            raise PlanRefused(
                f"Writer {self.name!r} is classified {self.disposition.value!r} "
                "and names nobody who classified it. A disposition with no "
                "author is an assertion with no author."
            )


@dataclass(frozen=True, slots=True)
class HostInventory:
    """What was actually running on the host when admission was considered.

    `complete` is a separate observation and it defaults to `False`. An inventory
    that could not be taken in full is not an empty inventory: it is an unknown
    one, and it refuses.
    """

    writers: tuple[Writer, ...] = ()
    complete: bool = False
    taken_at: str = ""

    def unknown(self) -> tuple[str, ...]:
        return tuple(
            writer.name
            for writer in self.writers
            if writer.disposition is WriterDisposition.UNKNOWN
        )


@dataclass(frozen=True, slots=True)
class LockView:
    """What the caller observed of `HOST_LOCK_PATH`.

    `held_by` is a reservation id or `None`. `observation_failed` is the third
    possibility and it is not the same as `None`: a lock nobody could read is
    not an unheld lock.
    """

    held_by: str | None = None
    holder_owner: str = ""
    observation_failed: bool = False


class PredecessorDisposition(str, Enum):
    """What the durable lifecycle record says about the run before this one.

    **PR-20260911-3.** The submitted `admit()` had no such input. It read the
    process lock, the inventory and an optional quarantine argument, and a
    readable free lock with a complete inventory was enough to admit. Those three
    observations cannot distinguish a host nobody has ever reserved from one
    whose executor died mid-run: the lock disappears with the process either way,
    the inventory can be quiet while a server-side transaction is still open, and
    an absent quarantine argument is the absence of a record, not the presence of
    a release.

    So admission now requires a statement about the predecessor, drawn from a
    closed vocabulary in which **exactly two values admit** and every other value
    — including not knowing — refuses.
    """

    #: No reservation has ever been made against this host, and the record that
    #: says so was read and is complete. **Admits.**
    VERIFIED_FIRST_USE = "verified_first_use"
    #: The predecessor reached `RELEASED` and a release record says so.
    #: **Admits**, and only when that record binds to this host and that
    #: reservation.
    RELEASED = "released"
    #: The predecessor is `ADMITTED` or `RUNNING` in the durable record.
    #: Refuses, whatever the process lock says.
    ACTIVE = "active"
    #: The predecessor reached its deadline or crashed and is `RECOVERING`.
    #: Refuses; recovery is somebody's task, not a successor's permission.
    RECOVERING = "recovering"
    #: The predecessor quarantined the host. Refuses.
    QUARANTINED = "quarantined"
    #: An operator completed the recorded recovery of a quarantined predecessor.
    #: **Admits a new reservation**, never the quarantined one.
    OPERATOR_RECOVERED = "operator_recovered"
    #: The record was read and its predecessor state is not classifiable.
    #: Refuses, and it is the default: a disposition nobody supplied is not a
    #: clean host.
    UNKNOWN = "unknown"


#: The only three dispositions that admit, named once so a reader does not have
#: to infer the set from the branches below.
ADMITTING_DISPOSITIONS = frozenset(
    {
        PredecessorDisposition.VERIFIED_FIRST_USE,
        PredecessorDisposition.RELEASED,
        PredecessorDisposition.OPERATOR_RECOVERED,
    }
)

#: The same set under the name **PR-20260911-R2-4** asks for: *one explicit
#: allowlist of validated lifecycle outcomes*, shared by all seven participants
#: rather than re-derived per entry point.
#:
#: Two words in that phrase are load-bearing and neither is decorative.
#: **Allowlist**: a disposition outside this set refuses, including a disposition
#: nobody recognised, so there is no fall-through. **Validated**: membership is
#: necessary and not sufficient — the record carrying the disposition must first
#: be coherent under `LIFECYCLE_SHAPES`, which is the whole of R2-1.
VALIDATED_LIFECYCLE_OUTCOMES = ADMITTING_DISPOSITIONS


@dataclass(frozen=True, slots=True)
class ReleaseRecord:
    """A durable record that one named reservation released one named host.

    It carries the host, the target and the reservation it is about because a
    release is not a fact about *a* host: a record naming another host or another
    reservation is evidence about something else, and reading it as this host's
    release is how a crashed predecessor becomes an admitted successor.
    """

    reservation_id: str
    host: str
    target_identity: str
    released_at: str
    recorded_by: str

    def __post_init__(self) -> None:
        for name in ("reservation_id", "host", "target_identity", "released_at", "recorded_by"):
            if not getattr(self, name).strip():
                raise PlanRefused(
                    f"A release record needs a {name}. A release nobody recorded, "
                    "of no stated host, at no stated time is not a release record."
                )


@dataclass(frozen=True, slots=True)
class LifecycleHistory:
    """The durable lifecycle record, as somebody read it.

    Every field is an observation of a record, and the defaults are the
    fail-closed ones: unread, incomplete, and a predecessor nobody classified.
    A caller that supplies nothing therefore refuses, which is the opposite of
    the submitted behaviour.

    **`readable=False` is not an empty history.** A record that could not be read
    is unknown, exactly as an unreadable lock is not an unheld lock.
    """

    #: The host the record is about. Compared with the request's host, because a
    #: record read for another host says nothing about this one.
    host: str
    readable: bool = False
    #: Whether the record covers every reservation made against this host. A
    #: partial history establishes nothing about the runs it does not contain.
    complete: bool = False
    predecessor_id: str = ""
    predecessor_state: ReservationState | None = None
    disposition: PredecessorDisposition = PredecessorDisposition.UNKNOWN
    release_record: ReleaseRecord | None = None
    #: The operator recovery reference, required by `OPERATOR_RECOVERED`.
    operator_recovery_reference: str = ""
    read_at: str = ""
    read_by: str = ""

    # -- the binding and the attributable evidence — PR-20260911-R3-3 --------
    #
    # The re-review found that a record carried its host and lost everything
    # else between storage and decision. Target identity travelled only inside a
    # `ReleaseRecord`, so `VERIFIED_FIRST_USE` and `OPERATOR_RECOVERED` admitted
    # against **any** target on a matching hostname; and the first-use evidence's
    # author and basis never reached the validator at all. These four fields are
    # the missing halves, and `LIFECYCLE_SHAPES` states for each disposition
    # whether each is required or forbidden.

    #: The approved target identity this record is bound to. Empty means *no
    #: binding was recorded*, which is a refusal for every admitting disposition
    #: rather than a wildcard: an unbound record is evidence about an unnamed
    #: target.
    target_identity: str = ""
    #: Who attested that this host had never been reserved, for a first use.
    first_use_attested_by: str = ""
    #: How they established it — a fresh image, a rebuild reference. A claim
    #: with an author and no basis is an assertion.
    first_use_basis: str = ""
    #: Who performed the operator recovery the record claims. The reference says
    #: *which* recovery; this says *whose*, and R3-3 requires both to survive
    #: the trip from storage to decision.
    recovery_authored_by: str = ""


#: How the durable record must be ordered for the decisions below to mean
#: anything — **PR-20260911-3's second half**, stated in the contract because
#: this module implements no writer and cannot enforce it.
#:
#: The failure it exists for: an executor takes the host, issues effects, and
#: dies before it can publish a quarantine record. If the durable record is
#: written at the *end* of a run, nothing on the host then says a run happened,
#: and the next admission sees a free lock and a quiet inventory — the exact
#: input PR-20260911-3 reproduced.
DURABLE_RECORD_ORDERING = (
    "1. The reservation record reaches durable storage — written, `fsync`ed, and "
    "its directory `fsync`ed — carrying state ADMITTED and this reservation's "
    "id, owner, host, target and deadline, **before the first effect of any "
    "kind is issued against the host**. Admission is a decision; the record is "
    "what makes the decision survive the decider.",
    "2. The transition to RUNNING is published the same way before the first "
    "mutation-bearing step. Between (1) and (2) the record already refuses "
    "every successor, so the ordering is fail-closed at every instant.",
    "3. A quarantine record is published on any failure path. It is an "
    "**addition** to the durable state, never a precondition of it: a crash "
    "before it can be written leaves the record at RUNNING, which refuses "
    "admission. Absence of a quarantine record is therefore never evidence that "
    "a predecessor ended.",
    "4. A release record is published only after `release()` returns RELEASED, "
    "and it names the reservation, the host and the target it is a release of. "
    "It is the only thing that turns a predecessor into an admitting one.",
    "5. Nothing deletes or rewrites a prior record. Recovery of a quarantined "
    "host appends an operator-recovery entry naming the reference; the "
    "quarantined reservation stays quarantined and is never resumed.",
)


#: What an eventual adapter owns, kept explicitly apart from what this module
#: does. None of it is implemented here, and this pass implements none of it.
ADAPTER_RESPONSIBILITIES = (
    "Taking and holding the cooperative lock, and releasing it. This module "
    "reads a `LockView` somebody else produced.",
    "Writing, `fsync`ing and reading back the durable lifecycle record in the "
    "order `DURABLE_RECORD_ORDERING` states, including the release record and "
    "the operator-recovery entry.",
    "Taking the host inventory: enumerating sessions, processes, timers and "
    "services, and presenting each for an operator's disposition.",
    "Observing the release conditions on a real host — that children exited, "
    "that server-side transactions settled, that residue was searched for, and "
    "that the configuration is restored and in force after reload.",
    "Enforcing anything at all. These functions return decisions; a decision "
    "that nobody acts on reserves nothing.",
)


#: What these decisions are **not**, stated where a caller of them will see it.
DECISIONS_DO_NOT_PERSIST = (
    "These are pure functions over injected observations. They persist nothing, "
    "lock nothing and enforce nothing.",
    "An `AdmissionDecision` with `admitted=True` is not a reservation. It "
    "becomes one when an adapter has taken the lock and published the durable "
    "record, and not before.",
    "A `ReleaseOutcome` of RELEASED is not a released host until the release "
    "record it justifies is durable.",
)


@dataclass(frozen=True, slots=True)
class QuarantineRecord:
    """A durable record that some earlier run left the host in an unknown state.

    It is keyed by host rather than by reservation, because what it says is
    *"this host is not reusable"*, which is not a fact about whoever created it.
    """

    host: str
    reservation_id: str
    reason: str
    residue: tuple[str, ...] = ()
    #: Only an operator recovery clears this, and clearing it starts a **new**
    #: reservation. It never resumes the quarantined one.
    cleared_by_operator: bool = False


@dataclass(frozen=True, slots=True)
class ReservationRequest:
    """Who is asking, for what host, against which target, until when."""

    reservation_id: str
    owner: str
    host: str
    target_identity: str
    requested_at: str
    #: The reservation deadline. The direction requires one to be specified, and
    #: what it is *for* is reporting: reaching it moves the run to `RECOVERING`,
    #: and it authorizes nobody to take the host.
    deadline: str
    recovery_owner: str
    #: Whether this reservation intends to run the real, mutation-bearing
    #: boundary. `False` is the local synthetic pass.
    real_execution: bool = False

    def __post_init__(self) -> None:
        for name in (
            "reservation_id",
            "owner",
            "host",
            "target_identity",
            "requested_at",
            "deadline",
            "recovery_owner",
        ):
            if not getattr(self, name).strip():
                raise PlanRefused(
                    f"A reservation request needs a {name}. There is no default "
                    "owner, no default target and no default deadline: a "
                    "reservation nobody is accountable for is not a reservation."
                )


@dataclass(frozen=True, slots=True)
class AdmissionDecision:
    """Admitted, or refused with every reason rather than the first one.

    Refusals are plural deliberately. A caller that fixed one reason and retried
    would otherwise discover the next one a run at a time, and each rediscovery
    is a fresh opportunity to route around it.
    """

    admitted: bool
    state: ReservationState
    refusals: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.admitted and self.refusals:
            raise PlanRefused(
                "An admitted decision carries no refusal. A decision that "
                "admits while naming a reason not to is the shape of a warning "
                "that was ignored."
            )
        if not self.admitted and not self.refusals:
            raise PlanRefused("A refusal names why.")


#: The refusal a real-execution request receives while EH-R16-1 is unremedied.
#: It is unconditional and it is not a target fact: the defect is that execution
#: and cleanup revalidate the command vector rather than the identity of the
#: object a pathname now resolves to, and a reservation does not repair it.
REAL_EXECUTION_REFUSAL = (
    "Real execution is refused while EH-R16-1 is open. Reservation excludes "
    "unrelated cooperative work; it does not make an ownership-dependent effect "
    "safe against substitution by this run's own experimental writers, which is "
    "what the finding is about. The refusal is unconditional and is not cleared "
    "by a preflight, a green suite or an exclusive host."
)


class EvidenceRule(str, Enum):
    """Whether a piece of attached lifecycle evidence must be there, must not be,
    or says nothing either way.

    There is no fourth value, and in particular there is no *optional*: a field
    that may or may not accompany a disposition is a field whose presence carries
    no information, and R2-1 is what happens when a decision is taken from a
    field like that.
    """

    REQUIRED = "required"
    FORBIDDEN = "forbidden"
    #: Only `UNKNOWN` uses this. A record nobody classified constrains nothing,
    #: and it refuses for that reason rather than for a contradiction.
    UNCONSTRAINED = "unconstrained"


@dataclass(frozen=True, slots=True)
class LifecycleShape:
    """What a **coherent** lifecycle record looks like for one disposition.

    **PR-20260911-R2-1.** The submitted `admit()` chose an admitting branch from
    `disposition` alone and then validated only that branch's own evidence. So a
    record saying *"the predecessor is RUNNING"* and *"the predecessor is
    released, here is the release record"* in the same breath was resolved in
    favour of the second half, and admitted. Varying nothing but
    `predecessor_state` across RUNNING, QUARANTINED and RELEASED produced
    `admitted=True` three times.

    The repair is this table. A record is checked against the shape of its
    declared disposition **as a whole — state, predecessor identity and every
    attached piece of evidence — before any branch is selected**, and a record
    that disagrees with itself is refused rather than normalized into a
    successful disposition. `admits` is then applied only to a record that was
    coherent in the first place.
    """

    #: Whether a coherent record of this shape admits a successor at all.
    admits: bool
    #: The predecessor states this disposition may be paired with. `None` is a
    #: member where *no state recorded* is the coherent reading.
    permitted_states: frozenset
    #: Whether the record must name the predecessor it is about.
    predecessor_identity: EvidenceRule
    release_record: EvidenceRule
    recovery_reference: EvidenceRule
    #: Whether the record must name the approved target it is bound to —
    #: **PR-20260911-R3-3**. Required for every disposition that makes a positive
    #: statement about a run, so that no admitting disposition can travel from
    #: storage to decision without its binding.
    target_binding: EvidenceRule
    #: Whether the record must carry the first-use attestation's author and
    #: basis. Required by `VERIFIED_FIRST_USE` and forbidden everywhere else,
    #: because an attestation beside a released or recovered predecessor
    #: describes a host that was both never used and used.
    first_use_attestation: EvidenceRule
    #: Whether the record must name who performed the recovery it claims.
    recovery_author: EvidenceRule
    #: Why this shape is what it is, quoted in the refusal so a caller reading
    #: one refusal does not have to come back here to understand it.
    rationale: str


#: The accepted combinations, stated explicitly rather than left to be inferred
#: from a chain of `elif`s — which is what let R2-1 through.
#:
#: Read a row as one sentence: *a record whose disposition is X is coherent only
#: when its predecessor state is one of these, its identity is present/absent as
#: stated, and each piece of evidence is present/absent as stated.* Three rows
#: admit and four refuse, and **coherence and admission are separate**: a
#: perfectly coherent ACTIVE record refuses, and an incoherent RELEASED record
#: refuses for a different reason.
LIFECYCLE_SHAPES: Mapping[PredecessorDisposition, LifecycleShape] = {
    PredecessorDisposition.VERIFIED_FIRST_USE: LifecycleShape(
        admits=True,
        permitted_states=frozenset({None}),
        predecessor_identity=EvidenceRule.FORBIDDEN,
        release_record=EvidenceRule.FORBIDDEN,
        recovery_reference=EvidenceRule.FORBIDDEN,
        target_binding=EvidenceRule.REQUIRED,
        first_use_attestation=EvidenceRule.REQUIRED,
        recovery_author=EvidenceRule.FORBIDDEN,
        rationale=(
            "a verified first use is the claim that no reservation has ever been "
            "made against this host, so there is no predecessor to name, nothing "
            "to have released and nothing to have recovered. Evidence of any of "
            "the three contradicts the claim, and it is a claim rather than an "
            "absence: an unread or unclassified record refuses instead"
        ),
    ),
    PredecessorDisposition.RELEASED: LifecycleShape(
        admits=True,
        permitted_states=frozenset({ReservationState.RELEASED}),
        predecessor_identity=EvidenceRule.REQUIRED,
        release_record=EvidenceRule.REQUIRED,
        recovery_reference=EvidenceRule.FORBIDDEN,
        target_binding=EvidenceRule.REQUIRED,
        first_use_attestation=EvidenceRule.FORBIDDEN,
        recovery_author=EvidenceRule.FORBIDDEN,
        rationale=(
            "a released predecessor is RELEASED in the durable record **and** has "
            "the release record to show for it. A release record beside any other "
            "state is stale metadata next to a later state, and reading it as a "
            "release is exactly PR-20260911-R2-1"
        ),
    ),
    PredecessorDisposition.OPERATOR_RECOVERED: LifecycleShape(
        admits=True,
        permitted_states=frozenset({ReservationState.QUARANTINED}),
        predecessor_identity=EvidenceRule.REQUIRED,
        release_record=EvidenceRule.FORBIDDEN,
        recovery_reference=EvidenceRule.REQUIRED,
        target_binding=EvidenceRule.REQUIRED,
        first_use_attestation=EvidenceRule.FORBIDDEN,
        recovery_author=EvidenceRule.REQUIRED,
        rationale=(
            "an operator recovery is an entry **appended to a quarantine**, so "
            "the predecessor it names stays QUARANTINED and the recovery "
            "reference is what carries the operator's account. A recovered "
            "predecessor in any other state, or one that also carries a release "
            "record, describes a history that did not happen"
        ),
    ),
    PredecessorDisposition.ACTIVE: LifecycleShape(
        admits=False,
        permitted_states=frozenset(
            {ReservationState.ADMITTED, ReservationState.RUNNING}
        ),
        predecessor_identity=EvidenceRule.REQUIRED,
        release_record=EvidenceRule.FORBIDDEN,
        recovery_reference=EvidenceRule.FORBIDDEN,
        target_binding=EvidenceRule.REQUIRED,
        first_use_attestation=EvidenceRule.FORBIDDEN,
        recovery_author=EvidenceRule.FORBIDDEN,
        rationale=(
            "an active predecessor is ADMITTED or RUNNING. **ADMITTED is active** "
            "— PR-20260911-R2-4 — because the durable record reaches ADMITTED "
            "before the first effect of any kind, so a crash between ADMITTED and "
            "RUNNING leaves a free process lock and a host that has been touched"
        ),
    ),
    PredecessorDisposition.RECOVERING: LifecycleShape(
        admits=False,
        permitted_states=frozenset({ReservationState.RECOVERING}),
        predecessor_identity=EvidenceRule.REQUIRED,
        release_record=EvidenceRule.FORBIDDEN,
        recovery_reference=EvidenceRule.FORBIDDEN,
        target_binding=EvidenceRule.REQUIRED,
        first_use_attestation=EvidenceRule.FORBIDDEN,
        recovery_author=EvidenceRule.FORBIDDEN,
        rationale=(
            "a recovering predecessor is RECOVERING, and recovery is a task with "
            "a named owner rather than a successor's permission"
        ),
    ),
    PredecessorDisposition.QUARANTINED: LifecycleShape(
        admits=False,
        permitted_states=frozenset({ReservationState.QUARANTINED}),
        predecessor_identity=EvidenceRule.REQUIRED,
        release_record=EvidenceRule.FORBIDDEN,
        recovery_reference=EvidenceRule.FORBIDDEN,
        target_binding=EvidenceRule.REQUIRED,
        first_use_attestation=EvidenceRule.FORBIDDEN,
        recovery_author=EvidenceRule.FORBIDDEN,
        rationale=(
            "a quarantined predecessor is QUARANTINED and stays so. The recovery "
            "reference belongs to OPERATOR_RECOVERED, which is the appended entry "
            "rather than a rewrite of this one"
        ),
    ),
    PredecessorDisposition.UNKNOWN: LifecycleShape(
        admits=False,
        permitted_states=frozenset({None, *ReservationState}),
        predecessor_identity=EvidenceRule.UNCONSTRAINED,
        release_record=EvidenceRule.UNCONSTRAINED,
        recovery_reference=EvidenceRule.UNCONSTRAINED,
        target_binding=EvidenceRule.UNCONSTRAINED,
        first_use_attestation=EvidenceRule.UNCONSTRAINED,
        recovery_author=EvidenceRule.UNCONSTRAINED,
        rationale=(
            "a record nobody classified constrains nothing, so nothing in it can "
            "be contradictory. It refuses because it is unclassified, which is a "
            "different refusal from a contradiction and is reported as one"
        ),
    ),
}


@dataclass(frozen=True, slots=True)
class LifecycleValidation:
    """The shared verdict on one durable lifecycle record.

    **PR-20260911-R2-4** asks that the seven participants and the executor share
    one decision rather than an allowlist for the executor and a weaker denylist
    for everybody else. This is that decision, and `validate_lifecycle()` is the
    only place it is made: `admit()` calls it, and so does every participant
    model of the proposed storage protocol.

    `coherent` and `admits` are separate because they answer different questions.
    A coherent ACTIVE record is coherent and does not admit. An incoherent
    RELEASED record does not admit *and* tells the operator that the durable
    record disagrees with itself, which is a different thing to go and fix.
    """

    coherent: bool
    admits: bool
    refusals: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.admits and self.refusals:
            raise PlanRefused(
                "A lifecycle validation that admits carries no refusal, for the "
                "same reason an AdmissionDecision that admits carries none."
            )
        if self.admits and not self.coherent:
            raise PlanRefused(
                "An incoherent record cannot admit. Admission is applied to a "
                "record that agrees with itself, which is PR-20260911-R2-1."
            )


def _describe_state(state: object) -> str:
    return repr(state.value) if isinstance(state, ReservationState) else repr(state)


def _malformed_value_refusals(history: LifecycleHistory) -> list[str]:
    """Values outside the closed vocabularies, refused before any comparison.

    The branches this replaces compared with `is`, so a plain string carrying the
    right *text* — `disposition="released"` — matched no branch, produced no
    refusal and **admitted**. An unrecognised value is not a value a decision may
    be taken from, so it is named here and the record is refused as malformed
    rather than compared further.
    """
    malformed: list[str] = []
    if not isinstance(history.disposition, PredecessorDisposition):
        malformed.append(
            f"the record's disposition {history.disposition!r} is malformed: it "
            "is not one of "
            f"{sorted(value.value for value in PredecessorDisposition)}. An "
            "unrecognised value is refused rather than compared, because a "
            "comparison it matches nothing in falls through to admission."
        )
    if history.predecessor_state is not None and not isinstance(
        history.predecessor_state, ReservationState
    ):
        malformed.append(
            f"the record's predecessor state {history.predecessor_state!r} is "
            "malformed: it is not one of "
            f"{sorted(state.value for state in ReservationState)} and it is not "
            "absent."
        )
    return malformed


def _coherence_refusals(
    *,
    history: LifecycleHistory,
    shape: LifecycleShape,
    host: str,
    target_identity: str,
) -> list[str]:
    """Every way this record disagrees with the shape of its own disposition."""
    disposition = history.disposition
    refusals: list[str] = []

    if history.predecessor_state not in shape.permitted_states:
        permitted = sorted(
            "none" if state is None else state.value
            for state in shape.permitted_states
        )
        refusals.append(
            f"the record's disposition is {disposition.value!r} and its "
            f"predecessor state is {_describe_state(history.predecessor_state)}. "
            "The two are contradictory, and a contradictory lifecycle record is "
            "refused rather than resolved in favour of reuse: "
            f"{disposition.value!r} may be paired only with {permitted}. Because "
            f"{shape.rationale}."
        )

    named = bool(history.predecessor_id.strip())
    if shape.predecessor_identity is EvidenceRule.REQUIRED and not named:
        refusals.append(
            f"the record's disposition is {disposition.value!r} and it names no "
            "predecessor. A statement about a predecessor that does not say which "
            "predecessor is not a statement a successor may be admitted on."
        )
    if shape.predecessor_identity is EvidenceRule.FORBIDDEN and named:
        refusals.append(
            f"the record's disposition is {disposition.value!r}, which names no "
            f"predecessor, and the record also names {history.predecessor_id!r} "
            f"(state {_describe_state(history.predecessor_state)}). One of the "
            "two is wrong, and guessing which is how an unreleased run becomes a "
            "first use."
        )

    record = history.release_record
    if shape.release_record is EvidenceRule.REQUIRED:
        if record is None:
            refusals.append(
                f"the record says reservation {history.predecessor_id!r} was "
                "released and carries no release record to show for it. A state "
                "word is not the durable evidence; the release record is."
            )
        else:
            if record.reservation_id != history.predecessor_id:
                refusals.append(
                    f"the release record is of reservation "
                    f"{record.reservation_id!r} and the predecessor is "
                    f"{history.predecessor_id!r}. A release of another "
                    "reservation releases nothing here."
                )
            if record.host != host:
                refusals.append(
                    f"the release record names host {record.host!r} and this "
                    f"reservation is of {host!r}."
                )
            if record.target_identity != target_identity:
                refusals.append(
                    f"the release record names target {record.target_identity!r} "
                    f"and this reservation is of {target_identity!r}."
                )
    if shape.release_record is EvidenceRule.FORBIDDEN and record is not None:
        refusals.append(
            f"the record's disposition is {disposition.value!r} and it also "
            f"carries a release record for {record.reservation_id!r}. Because "
            f"{shape.rationale}."
        )

    bound = history.target_identity.strip()
    if shape.target_binding is EvidenceRule.REQUIRED:
        if not bound:
            refusals.append(
                f"the record's disposition is {disposition.value!r} and it names "
                "no approved target identity. A lifecycle record binds a host "
                "**and** the target it was reserved for, and an unbound record "
                "is evidence about an unnamed target rather than about this "
                "one. This is PR-20260911-R3-3."
            )
        elif bound != target_identity:
            refusals.append(
                f"the record is bound to target {bound!r} and this reservation "
                f"is of {target_identity!r}. A history for the same hostname is "
                "not a history for another approved target: admitting on it is "
                "how evidence collected against one target authorizes a run "
                "against a different one."
            )
    if shape.target_binding is EvidenceRule.FORBIDDEN and bound:
        refusals.append(
            f"the record's disposition is {disposition.value!r} and it carries a "
            f"target binding {bound!r}. Because {shape.rationale}."
        )

    attested_by = history.first_use_attested_by.strip()
    basis = history.first_use_basis.strip()
    if shape.first_use_attestation is EvidenceRule.REQUIRED:
        if not attested_by:
            refusals.append(
                "the record claims a verified first use and names nobody as "
                "having attested it. A first use is a positive claim about the "
                "host and an unattributed claim has no author."
            )
        if not basis:
            refusals.append(
                "the record claims a verified first use and records no basis "
                "for it. A named attester with no stated basis — a fresh image, "
                "a rebuild reference — is an assertion rather than evidence."
            )
    if shape.first_use_attestation is EvidenceRule.FORBIDDEN and (
        attested_by or basis
    ):
        refusals.append(
            f"the record's disposition is {disposition.value!r} and it also "
            f"carries a first-use attestation by {attested_by or 'nobody'!r} on "
            f"basis {basis or 'nothing'!r}. A host cannot both have a "
            f"predecessor and never have been reserved. Because {shape.rationale}."
        )

    recovered_by = history.recovery_authored_by.strip()
    if shape.recovery_author is EvidenceRule.REQUIRED and not recovered_by:
        refusals.append(
            "the record claims an operator recovery and names nobody as having "
            "performed it. The reference says which recovery; it does not say "
            "whose, and both are required to remain attributable."
        )
    if shape.recovery_author is EvidenceRule.FORBIDDEN and recovered_by:
        refusals.append(
            f"the record's disposition is {disposition.value!r} and it also "
            f"names {recovered_by!r} as having performed a recovery. Because "
            f"{shape.rationale}."
        )

    referenced = bool(history.operator_recovery_reference.strip())
    if shape.recovery_reference is EvidenceRule.REQUIRED and not referenced:
        refusals.append(
            "the record claims an operator recovery and names no recovery "
            "reference. An unattributed recovery is an assertion with no author, "
            "and it is the one that would clear a quarantine."
        )
    if shape.recovery_reference is EvidenceRule.FORBIDDEN and referenced:
        refusals.append(
            f"the record's disposition is {disposition.value!r} and it also "
            "carries an operator recovery reference "
            f"{history.operator_recovery_reference!r}. Because {shape.rationale}."
        )
    return refusals


def _disposition_refusals(
    *, history: LifecycleHistory, reservation_id: str
) -> list[str]:
    """Why a *coherent* record of a refusing disposition still refuses.

    These are the September 11 texts, unchanged in substance. What changed is
    when they run: a record reaches them only after it has been shown to agree
    with itself, so none of them is the thing standing between a contradictory
    history and admission any more.
    """
    disposition = history.disposition
    refusals: list[str] = []
    if disposition is PredecessorDisposition.UNKNOWN:
        refusals.append(
            "the predecessor's disposition is unknown. A predecessor nobody "
            "classified is not an absent predecessor, and admission requires a "
            "positive statement drawn from "
            f"{sorted(value.value for value in VALIDATED_LIFECYCLE_OUTCOMES)}."
        )
    elif disposition is PredecessorDisposition.ACTIVE:
        refusals.append(
            f"the durable record says reservation {history.predecessor_id!r} is "
            f"still active on this host (state "
            f"{_describe_state(history.predecessor_state)}). A free process lock "
            "does not contradict that: the lock dies with the process whether or "
            "not the run finished, and its child processes and server-side "
            "transactions do not."
        )
    elif disposition is PredecessorDisposition.RECOVERING:
        refusals.append(
            f"the durable record says reservation {history.predecessor_id!r} is "
            "recovering. Recovery is a task with a named owner; it is not a "
            "successor's permission to take the host."
        )
    elif disposition is PredecessorDisposition.QUARANTINED:
        refusals.append(
            f"the durable record says reservation {history.predecessor_id!r} "
            "quarantined this host. No elapsed time, released lock or quiet "
            "inventory makes a quarantined host reusable."
        )
    elif (
        disposition is PredecessorDisposition.OPERATOR_RECOVERED
        and reservation_id
        and history.predecessor_id.strip() == reservation_id
    ):
        refusals.append(
            f"this request reuses the recovered reservation's own id "
            f"{reservation_id!r}. A completed operator recovery permits a **new** "
            "reservation against the host; it never resumes the quarantined run, "
            "which stays quarantined."
        )
    return refusals


def validate_lifecycle(
    *,
    history: LifecycleHistory,
    host: str,
    target_identity: str,
    reservation_id: str = "",
) -> LifecycleValidation:
    """Validate one durable lifecycle record as a coherent whole, then decide.

    **The one decision, shared.** `admit()` calls this, and so does every
    participant in the proposed storage protocol — PR-20260911-R2-4's requirement
    that ordinary participants are not left with a weaker denylist than the
    executor. `reservation_id` is the caller's own, supplied only by a caller
    that has one; it is used for the single check that needs it, which is that an
    operator recovery never resumes the reservation it recovered.

    **The order is the correction — PR-20260911-R2-1.** Four stages, and the
    first three run before any admitting branch is selected:

    1. is this record about this host, was it read, and is it complete;
    2. are its values inside the closed vocabularies at all;
    3. does it agree with itself, under `LIFECYCLE_SHAPES`; and only then
    4. does its disposition appear in `VALIDATED_LIFECYCLE_OUTCOMES`.

    The submitted version ran (4) first and validated only the selected branch's
    own evidence, so a release record was allowed to override the state it
    contradicted. Nothing here normalizes a contradiction into a successful
    disposition: a record that disagrees with itself refuses, and it refuses
    saying which two halves disagree.

    Nothing else stands in for the record. A free process lock is not a release —
    the lock disappears when the process does, whether or not the run finished. A
    complete inventory is not a release — a server-side transaction the run
    opened has no process of its own. An elapsed deadline is not a release —
    `deadline_reached()` moves a run to RECOVERING and authorizes nobody. And an
    absent quarantine argument is not a release — it is the absence of a record,
    and `DURABLE_RECORD_ORDERING` item 3 is the reason a crash can produce
    exactly that absence while a run is still active.
    """
    refusals: list[str] = []

    if history.host != host:
        refusals.append(
            f"the lifecycle record that was read is for host {history.host!r} and "
            f"this reservation is of {host!r}. A history read for another host is "
            "evidence about that host. Binding it to this one is how a crashed "
            "predecessor becomes an admitted successor."
        )
    if not history.readable:
        refusals.append(
            "the durable lifecycle record could not be read. A record whose "
            "state is unknown is not an empty record, exactly as an unreadable "
            "lock is not an unheld lock."
        )
        return LifecycleValidation(
            coherent=False, admits=False, refusals=tuple(refusals)
        )
    if not history.complete:
        refusals.append(
            "the durable lifecycle record is not complete. A partial history "
            "establishes nothing about the reservations it does not contain, and "
            "the one it does not contain is the one that matters."
        )

    malformed = _malformed_value_refusals(history)
    if malformed:
        refusals.extend(malformed)
        return LifecycleValidation(
            coherent=False, admits=False, refusals=tuple(refusals)
        )

    shape = LIFECYCLE_SHAPES[history.disposition]
    incoherent = _coherence_refusals(
        history=history, shape=shape, host=host, target_identity=target_identity
    )
    refusals.extend(incoherent)
    refusals.extend(
        _disposition_refusals(history=history, reservation_id=reservation_id)
    )

    admits = (
        not refusals
        and shape.admits
        and history.disposition in VALIDATED_LIFECYCLE_OUTCOMES
    )
    return LifecycleValidation(
        coherent=not incoherent and not malformed,
        admits=admits,
        refusals=tuple(refusals),
    )


def admit(
    *,
    request: ReservationRequest,
    inventory: HostInventory,
    lock: LockView,
    approved_target_identity: str,
    lifecycle: LifecycleHistory,
    quarantine: QuarantineRecord | None = None,
    ownership_remedy_accepted: bool = False,
) -> AdmissionDecision:
    """Decide admission, fail-closed, from observations somebody made.

    Every argument is an observation and none of them is taken. There is no
    parameter that skips a check, and the function performs no I/O of any kind:
    a caller that could not observe the lock says so through
    `LockView.observation_failed`, a caller that could not complete the inventory
    says so through `HostInventory.complete`, and a caller that could not read
    the durable lifecycle record says so through `LifecycleHistory.readable`.

    **`lifecycle` has no default and that is deliberate — PR-20260911-3.** A
    default would be a statement about the predecessor that nobody made, and the
    finding is precisely that such a statement was being inferred from a free
    lock. A caller who has not read the record must say so and be refused.

    **The lifecycle half is `validate_lifecycle()` — PR-20260911-R2-1 and -R2-4.**
    It is a separate function because the seven participants of
    `PARTICIPATING_ENTRY_POINTS` need exactly the same verdict and must not get a
    weaker one, and it validates the record as a coherent whole before any
    admitting branch is chosen.
    """
    refusals: list[str] = list(
        validate_lifecycle(
            history=lifecycle,
            host=request.host,
            target_identity=request.target_identity,
            reservation_id=request.reservation_id,
        ).refusals
    )

    if request.target_identity != approved_target_identity:
        refusals.append(
            f"the request names target {request.target_identity!r} and the "
            f"approved target is {approved_target_identity!r}. A reservation is "
            "of one named host and is not transferable to another."
        )

    if quarantine is not None and quarantine.host == request.host:
        if quarantine.cleared_by_operator:
            refusals.append(
                f"host {request.host!r} carries a quarantine record from "
                f"reservation {quarantine.reservation_id!r} that an operator has "
                "cleared. A cleared quarantine permits a **new** reservation to "
                "be requested after the recorded recovery; it does not admit "
                "this one, which was requested against the quarantined host."
            )
        else:
            refusals.append(
                f"host {request.host!r} is quarantined by reservation "
                f"{quarantine.reservation_id!r}: {quarantine.reason} Residue: "
                f"{list(quarantine.residue)}. No lock release and no elapsed "
                "time makes a quarantined host reusable."
            )

    if lock.observation_failed:
        refusals.append(
            f"the cooperative lock at {HOST_LOCK_PATH} could not be read. A "
            "lock whose state is unknown is not an unheld lock."
        )
    elif lock.held_by is not None and lock.held_by != request.reservation_id:
        refusals.append(
            f"the cooperative lock is held by reservation {lock.held_by!r} "
            f"(owner {lock.holder_owner or 'unrecorded'!r}). A second executor "
            "waits for a verified release; it does not take the host."
        )

    if not inventory.complete:
        refusals.append(
            "the host inventory is not complete. Admission requires that every "
            "relevant session, test process, timer and service was enumerated "
            "and accounted for; a partial enumeration establishes nothing about "
            "what it did not reach."
        )
    unknown = inventory.unknown()
    if unknown:
        refusals.append(
            f"these writers are unaccounted for: {list(unknown)}. Each must be "
            "identified as a required service or a reviewed test process by an "
            "operator. It is not killed, not disabled and not waited out."
        )

    if request.real_execution and not ownership_remedy_accepted:
        refusals.append(REAL_EXECUTION_REFUSAL)

    if refusals:
        return AdmissionDecision(
            admitted=False, state=ReservationState.REQUESTED, refusals=tuple(refusals)
        )
    return AdmissionDecision(admitted=True, state=ReservationState.ADMITTED)


@dataclass(frozen=True, slots=True)
class ResidueObservation:
    """Whether anybody looked for residue, and what they found.

    **PR-20260911-4.** `ReleaseEvidence.residue` used to be a bare tuple
    defaulting to `()`, so a caller that never looked for residue was
    indistinguishable from one that looked and found none — and the first of
    those released the host. Every other observation on the release already had
    an explicit *not made* value; this one did not.

    Three states, and only the middle one contributes to a release:

    * **not made** — `ResidueObservation.not_made()`, or the field left `None`.
      Quarantines, and is reported as an unmade observation;
    * **observed empty** — `ResidueObservation.empty(observed_by=…)`. Somebody
      searched, the search was complete, and there was nothing; and
    * **observed present** — `ResidueObservation.found(paths, observed_by=…)`.
      Quarantines, and §2.13.2b is explicit that the residue is reported and
      never cleaned automatically.

    `complete` is separate from `observed` for the same reason `HostInventory`
    separates them: a search that could not cover everything did not establish
    the absence of what it did not reach.
    """

    observed: bool
    paths: tuple[str, ...] = ()
    complete: bool = False
    observed_by: str = ""
    searched_at: str = ""

    def __post_init__(self) -> None:
        if not self.observed and (self.paths or self.complete or self.observed_by.strip()):
            raise PlanRefused(
                "An unmade residue observation carries no paths, no completeness "
                "claim and no observer. A search nobody performed cannot have a "
                "result."
            )
        if self.observed and not self.observed_by.strip():
            raise PlanRefused(
                "A residue observation names who made it. An observation with no "
                "author is an assertion with no author."
            )

    @classmethod
    def not_made(cls) -> "ResidueObservation":
        return cls(observed=False)

    @classmethod
    def empty(cls, *, observed_by: str, searched_at: str = "") -> "ResidueObservation":
        return cls(
            observed=True, paths=(), complete=True,
            observed_by=observed_by, searched_at=searched_at,
        )

    @classmethod
    def found(
        cls, paths: Sequence[str], *, observed_by: str, searched_at: str = "",
        complete: bool = True,
    ) -> "ResidueObservation":
        return cls(
            observed=True, paths=tuple(paths), complete=complete,
            observed_by=observed_by, searched_at=searched_at,
        )


@dataclass(frozen=True, slots=True)
class ReleaseEvidence:
    """The observations a release requires, each made rather than inferred.

    The direction's sentence this exists for: *"A crash, expired reservation or
    released process lock does not imply that child processes or server
    transactions ended."* So none of these defaults to `True`, and `None` — an
    observation nobody made — is treated exactly like `False` and reported
    separately, because *"it was not checked"* and *"it was checked and was
    false"* are different things to tell an operator.
    """

    #: The reservation whose release this is.
    reservation_id: str
    #: The target the run actually ran against, as observed at release.
    target_identity: str
    #: The lock's holder at release.
    lock_held_by: str | None
    #: Every process the run started, observed to have exited. `None` means the
    #: observation was not made.
    child_processes_ended: bool | None = None
    #: Every server-side transaction the run opened, observed settled. A command
    #: exiting does not settle a transaction the server still holds open.
    database_transactions_settled: bool | None = None
    #: The residue search and its result. `None` — nobody searched — is treated
    #: exactly like the other unmade observations, which is PR-20260911-4.
    residue: ResidueObservation | None = None
    #: Whether configuration restoration was verified in force after reload.
    configuration_restored: bool | None = None

    def __post_init__(self) -> None:
        if self.residue is not None and not isinstance(self.residue, ResidueObservation):
            raise PlanRefused(
                "`residue` is a ResidueObservation or None, not a bare sequence "
                "of paths. A bare empty tuple is the shape that made *nobody "
                "looked* indistinguishable from *somebody looked and found "
                "nothing* — PR-20260911-4 — and it is refused rather than "
                "coerced."
            )

    @property
    def residue_paths(self) -> tuple[str, ...]:
        """The paths a completed search found. Empty when nobody searched."""
        return self.residue.paths if self.residue is not None else ()

    def unmade_observations(self) -> tuple[str, ...]:
        unmade = []
        if self.child_processes_ended is None:
            unmade.append("child_processes_ended")
        if self.database_transactions_settled is None:
            unmade.append("database_transactions_settled")
        if self.configuration_restored is None:
            unmade.append("configuration_restored")
        if self.residue is None or not self.residue.observed:
            unmade.append("residue")
        return tuple(unmade)


@dataclass(frozen=True, slots=True)
class ReleaseOutcome:
    """What the release attempt concluded, and why."""

    state: ReservationState
    reasons: tuple[str, ...] = ()
    quarantine: QuarantineRecord | None = None


def release(
    *,
    request: ReservationRequest,
    current_state: ReservationState,
    evidence: ReleaseEvidence,
) -> ReleaseOutcome:
    """Release the reservation, or quarantine the host.

    There are exactly two outcomes and no third. A release that cannot establish
    all of its conditions does not *fail* — failing would leave the reservation
    where it was, and where it was is a state in which somebody else eventually
    takes the host. It quarantines, which is a durable record that the host is
    not reusable until an operator says otherwise.
    """
    if current_state is ReservationState.QUARANTINED:
        return ReleaseOutcome(
            state=ReservationState.QUARANTINED,
            reasons=(
                "the reservation is already quarantined. Quarantine has no "
                "outgoing transition and a release attempt does not create one.",
            ),
        )
    if current_state not in (
        ReservationState.ADMITTED,
        ReservationState.RUNNING,
        ReservationState.RECOVERING,
    ):
        raise PlanRefused(
            f"A reservation in state {current_state.value!r} is not releasable; "
            f"{sorted(state.value for state in TRANSITIONS)} names the states "
            "and their successors."
        )

    problems: list[str] = []

    if evidence.reservation_id != request.reservation_id:
        problems.append(
            f"the release names reservation {evidence.reservation_id!r} and this "
            f"reservation is {request.reservation_id!r}. A release of another "
            "reservation releases nothing here."
        )
    if evidence.target_identity != request.target_identity:
        problems.append(
            f"the run reports target {evidence.target_identity!r} and the "
            f"reservation is of {request.target_identity!r}. A run that reached "
            "a different host is not evidence about this one, and the mismatch "
            "is itself unaccounted activity."
        )
    if evidence.lock_held_by != request.reservation_id:
        problems.append(
            f"the cooperative lock is held by {evidence.lock_held_by!r} rather "
            f"than by {request.reservation_id!r}. Either it was released early — "
            "in which case another participant may have entered while this run "
            "was still active — or it was taken by somebody else."
        )

    unmade = evidence.unmade_observations()
    if unmade:
        problems.append(
            f"these observations were not made: {list(unmade)}. An unmade "
            "observation is not a passed one, and a parent command exiting is "
            "not any of them. `residue` appears here when nobody searched: a "
            "caller that never looked for residue is not a caller that observed "
            "none — PR-20260911-4."
        )
    if evidence.child_processes_ended is False:
        problems.append(
            "a process this run started has not exited. An orphaned child can "
            "write after its parent returns, so dependent cleanup and the next "
            "reservation would both be operating on a host somebody is using."
        )
    if evidence.database_transactions_settled is False:
        problems.append(
            "a server-side transaction this run opened has not settled. The "
            "command exiting says the client stopped waiting; it does not say "
            "the server finished."
        )
    if evidence.configuration_restored is False:
        problems.append(
            "the disposable PostgreSQL instance's configuration was not "
            "observed restored and in force after reload."
        )
    if evidence.residue is not None and evidence.residue.observed:
        if not evidence.residue.complete:
            problems.append(
                "the residue search did not complete. A partial search "
                "establishes nothing about the paths it did not reach, and it is "
                "not the observed-empty result a release needs."
            )
        if evidence.residue.paths:
            problems.append(
                f"the run left residue: {list(evidence.residue.paths)}. §2.13.2b "
                "is explicit that it is reported and never cleaned automatically."
            )

    if problems:
        return ReleaseOutcome(
            state=ReservationState.QUARANTINED,
            reasons=tuple(problems),
            quarantine=QuarantineRecord(
                host=request.host,
                reservation_id=request.reservation_id,
                reason=" ".join(problems),
                residue=evidence.residue_paths,
            ),
        )
    return ReleaseOutcome(state=ReservationState.RELEASED)


@dataclass(frozen=True, slots=True)
class OperatorAttestation:
    """What an operator must establish before a recovering run may be released.

    The direction names three things and this carries exactly those three, plus
    who said so. There is no partial credit: `complete` is the conjunction.
    """

    operator: str
    termination_established: bool = False
    residue_accounted: bool = False
    restoration_verified_or_rebuilt: bool = False

    @property
    def complete(self) -> bool:
        return (
            bool(self.operator.strip())
            and self.termination_established
            and self.residue_accounted
            and self.restoration_verified_or_rebuilt
        )

    def missing(self) -> tuple[str, ...]:
        missing = []
        if not self.operator.strip():
            missing.append("operator")
        if not self.termination_established:
            missing.append("termination_established")
        if not self.residue_accounted:
            missing.append("residue_accounted")
        if not self.restoration_verified_or_rebuilt:
            missing.append("restoration_verified_or_rebuilt")
        return tuple(missing)


def deadline_reached(
    *, request: ReservationRequest, current_state: ReservationState, now: str
) -> ReleaseOutcome:
    """What reaching the reservation deadline does, which is not very much.

    It moves a live reservation to `RECOVERING` and names the recovery owner.
    It releases nothing, admits nobody and takes nothing: *"A lock expiry or
    crashed executor does not authorize takeover."*

    Times are compared as ISO-8601 strings, which sort lexically when they are
    the same shape. The caller supplies both, and the caller is the only thing
    here that knows what time it is.
    """
    if current_state in (ReservationState.RELEASED, ReservationState.QUARANTINED):
        return ReleaseOutcome(state=current_state)
    if now < request.deadline:
        return ReleaseOutcome(state=current_state)
    return ReleaseOutcome(
        state=ReservationState.RECOVERING,
        reasons=(
            f"the reservation deadline {request.deadline!r} passed at {now!r}. "
            f"The recovery owner is {request.recovery_owner!r}. This authorizes "
            "no takeover: whether the run's processes and transactions ended is "
            "unknown until somebody observes it, and until then the host is not "
            "available to anybody.",
        ),
    )


def recover(
    *,
    request: ReservationRequest,
    attestation: OperatorAttestation,
    evidence: ReleaseEvidence | None = None,
) -> ReleaseOutcome:
    """Conclude a `RECOVERING` reservation: released, or quarantined.

    An incomplete attestation quarantines. A complete one still has to satisfy
    `release()`'s conditions, because an operator establishing that processes
    ended is not an operator establishing that the target matched or that the
    lock was still held.
    """
    if not attestation.complete:
        reason = (
            "the operator attestation is incomplete: "
            f"{list(attestation.missing())} not established. An uncertain run "
            "stays quarantined until termination, residue and restoration are "
            "all established."
        )
        return ReleaseOutcome(
            state=ReservationState.QUARANTINED,
            reasons=(reason,),
            quarantine=QuarantineRecord(
                host=request.host,
                reservation_id=request.reservation_id,
                reason=reason,
                residue=evidence.residue_paths if evidence else (),
            ),
        )
    if evidence is None:
        reason = (
            "the attestation is complete and no release evidence accompanies "
            "it. An operator's account of the recovery is not an observation of "
            "the target, the lock or the residue."
        )
        return ReleaseOutcome(
            state=ReservationState.QUARANTINED,
            reasons=(reason,),
            quarantine=QuarantineRecord(
                host=request.host,
                reservation_id=request.reservation_id,
                reason=reason,
            ),
        )
    return release(
        request=request,
        current_state=ReservationState.RECOVERING,
        evidence=evidence,
    )


#: The two transitions that may not be taken on a caller's say-so, and the
#: decision each one requires — **PR-20260911-4's second half**.
#:
#: The submitted `advance()` checked only the table, so
#: `advance(RUNNING, RELEASED)` returned RELEASED with no evidence at all, while
#: the table's own comment said release was possible only through `release()`.
#: A comment is not a guard. These are.
GUARDED_TRANSITIONS: Mapping[ReservationState, str] = {
    ReservationState.ADMITTED: (
        "an AdmissionDecision from admit() whose `admitted` is True and whose "
        "`state` is ADMITTED"
    ),
    ReservationState.RELEASED: (
        "a ReleaseOutcome from release() or recover() whose `state` is RELEASED"
    ),
}


def advance(
    *,
    current: ReservationState,
    target: ReservationState,
    decision: "AdmissionDecision | ReleaseOutcome | None" = None,
) -> ReservationState:
    """Apply a transition, refusing one the table does not contain **and one the
    corresponding decision does not support**.

    Two refusals, and they are different. The table refuses an edge that does not
    exist — `QUARANTINED` to anything, `RECOVERING` back to `ADMITTED`. The guard
    refuses an edge that exists but was taken without the decision that
    establishes it: a reservation is not admitted because a caller passed
    `ADMITTED`, and a host is not released because a caller passed `RELEASED`.

    The unguarded targets — `RUNNING`, `RECOVERING`, `QUARANTINED` — stay
    unguarded on purpose. Every one of them is a move *towards* caution, and a
    guard that made quarantine harder to reach would be a guard pointing the
    wrong way.
    """
    permitted = TRANSITIONS[current]
    if target not in permitted:
        raise PlanRefused(
            f"{current.value!r} does not transition to {target.value!r}. The "
            f"permitted successors are {sorted(state.value for state in permitted)}, "
            "and an absent edge is a refusal rather than a case the machine "
            "falls through."
        )
    required = GUARDED_TRANSITIONS.get(target)
    if required is None:
        if decision is not None:
            raise PlanRefused(
                f"a decision was supplied for the transition to "
                f"{target.value!r}, which is not a guarded transition. "
                f"{sorted(state.value for state in GUARDED_TRANSITIONS)} are the "
                "guarded ones, and passing a decision for another target is "
                "either a mistake about which transition this is or an attempt "
                "to make one decision justify a different move."
            )
        return target

    if decision is None:
        raise PlanRefused(
            f"the transition to {target.value!r} requires {required}, and none "
            "was supplied. A public transition helper that moved a reservation "
            "there on a caller's say-so would make every check in admit() and "
            "release() optional — PR-20260911-4."
        )
    if target is ReservationState.ADMITTED:
        if not isinstance(decision, AdmissionDecision):
            raise PlanRefused(
                f"the transition to {target.value!r} requires {required}; a "
                f"{type(decision).__name__} is not one."
            )
        if not decision.admitted or decision.state is not ReservationState.ADMITTED:
            raise PlanRefused(
                "the admission decision supplied did not admit "
                f"({decision.refusals!r}). A refusal is not a weaker admission."
            )
        return target
    if not isinstance(decision, ReleaseOutcome):
        raise PlanRefused(
            f"the transition to {target.value!r} requires {required}; a "
            f"{type(decision).__name__} is not one."
        )
    if decision.state is not ReservationState.RELEASED:
        raise PlanRefused(
            f"the release outcome supplied concluded {decision.state.value!r} "
            f"rather than released ({decision.reasons!r}). A quarantine is not a "
            "release that needs a second opinion."
        )
    return target


__all__ = [
    "ADAPTER_RESPONSIBILITIES",
    "ADMITTING_DISPOSITIONS",
    "AdmissionDecision",
    "DECISIONS_DO_NOT_PERSIST",
    "DURABLE_RECORD_ORDERING",
    "EvidenceRule",
    "GUARDED_TRANSITIONS",
    "HOST_LOCK_PATH",
    "HostInventory",
    "LIFECYCLE_SHAPES",
    "LOCK_LIMITS",
    "LifecycleHistory",
    "LifecycleShape",
    "LifecycleValidation",
    "LockView",
    "OperatorAttestation",
    "PARTICIPATING_ENTRY_POINTS",
    "PredecessorDisposition",
    "QuarantineRecord",
    "REAL_EXECUTION_REFUSAL",
    "ReleaseEvidence",
    "ReleaseOutcome",
    "ReleaseRecord",
    "ReservationRequest",
    "ReservationState",
    "ResidueObservation",
    "TRANSITIONS",
    "VALIDATED_LIFECYCLE_OUTCOMES",
    "Writer",
    "WriterDisposition",
    "admit",
    "advance",
    "deadline_reached",
    "recover",
    "release",
    "validate_lifecycle",
]
