"""The repository-owned integration point for all seven participants — r6 §5.

## The finding this answers

**PR-20260913-LABI-3.** The session, the reservation record, the run ledger, the
recovery store and the descriptor-bound effect issuer existed and were consumed
only by their own tests. `reservation.PARTICIPATING_ENTRY_POINTS` named seven
entry points that must serialize on one cooperative lock and account for their
own runs; none of them did, so the protocol was enforced by nothing — even if
the standing execution refusals were later removed.

This module is where the seven meet the protocol. It is **one** object, because
r6 §5.11 proposes no exemption for any participant and refuses the environment
reset's especially: a second integration with a shorter sequence would be the
exemption, written as code.

## The sequence, and it is §5.6's

```text
take or wait for the lock
  → re-seal the record's parent entry
  → re-seal the ledger's parent entry
  → read, parse, check order, validate, survey, decide
  → refuse unless admitted                       — before the first effect
  → publish this participant's `participant_started` durably
  → issue effects                                — only now, and only with a permit
  → observe this participant's exact completion conditions
  → publish completion durably
  → release the lock
```

Every step is `LaboratorySession`'s or `ParticipantRunLedger`'s. This module
**adds no rule**: it orders the calls, hands out the permit and refuses. A
mechanism with its own copy of the admission or completion rules would be the
second reader every finding since R3-1 has been about.

## What the permit is for

A participant's work is a callable, and it receives an `EffectPermit`. The
permit is a **reference to the live invocation it was issued inside**, not a
value that stands in for one. `EffectPermit.consume()` is what a consumer spends
before its first effect, and whether it may be spent is decided by the running
invocation's own record, not by anything the permit or this object carries.

## One issuance, one spend — PR-20260914-LABI-R2-1

The previous correction kept the one-shot state **on the object graph the work
callback holds**: a registration field on this object, cleared on consumption,
and an issuing method that assigned a new one. The re-review drove a second
armed executor through both — calling `_issue_authority()` again after the spend,
and assigning a fully bound permit to `_authority` — under the same session, lock
and durable T6–T8 state. Clearing a replaceable reference revoked an object; it
recorded nothing about the invocation.

So each call of `run()` or `run_harness()` now creates one `_WorkInvocation`,
held **only as a local variable of that call** and referenced by no permit, no
integration point, no session and no executor. It has four states and two
transitions that move forward only:

```text
OPEN ──issue──▶ ISSUED ──spend──▶ SPENT
  └──────────────┴────────────────┴──end──▶ ENDED     (return, exception, interrupt)
```

`_issue_authority` and `EffectPermit.consume` find that record through the
invocation's **activation record** — the `run`/`run_harness` frame on the calling
stack whose `self` is this integration point — rather than through an attribute.
Issuance is refused unless that record exists and is `OPEN`; consumption is
refused unless it exists, is `ISSUED`, and its issued permit, this object's
registration and the offered permit are one object. A spend moves it to `SPENT`
and the end of the work to `ENDED`, and nothing moves it back.

## The trust boundary, stated precisely

**This is not a security boundary against code running in the same
interpreter, and no such boundary exists here.** A callback executes arbitrary
Python with this process's credentials. It can rebind
`ExecutingRunner._require_accounted_run` or `EffectPermit.consume` — the
call-graph suite's own negative control does exactly that — reach and alter the
invocation's frame and its record through `sys._getframe`, `inspect`, traceback
objects or `gc`, or call `os` and `subprocess` itself and never touch the
executor. Nothing inside one Python process can prevent any of those.

What the mechanism establishes is narrower, and it is tested rather than
asserted: **through ordinary construction, method calls and attribute
assignment** — `object.__setattr__` on frozen and slotted objects included — on
every object reachable from the callback's arguments and from
`ExecutingRunner.session`, a durable start's invocation issues one authority and
a consumer spends it once. Writing every such attribute back to its value at
issuance does not re-arm a spent authority, because the spend is not stored in
any of them. An adversarial boundary would need the work to run in another
process that holds no descriptor on the lock, the record or the effects, which
is an architectural change this authorization does not make.

## The harness, and the two call-graph findings

**PR-20260914-LABI-R1-1.** Building these objects and then driving the executor
beside them enforces nothing: the executor guard accepted the presence of *any*
object as proof that a run was accounted for, so `session=object()` satisfied
it. `run_harness()` below **owns** the executable harness call.

**PR-20260914-LABI-R1-2, and this is the correction that matters.** Replacing
that guard with a *token* was not enough either, and the re-review reproduced
both halves of why. `_PERMIT_GRANT` is an ordinary readable module attribute and
`_grant_permit` an ordinary callable one, so a permit that passed every value
comparison could be built without opening a session; and a genuine permit stayed
valid for ever, so a work callback could keep one and drive an armed executor
after both terminal entries were published and the lock released.

**Python provides no access boundary here and this module does not claim one.**
What it claims instead is that authority is **live and one-shot**: a consumer's
first effect requires that this integration point is inside the work invocation
the authority was issued for, that it owns an open session, that the session
still holds the cooperative lock, that the stored run is this participant's,
bound to this reservation and still in progress, that the reservation is in r6
§5.7's T8 `running` state, and that the authority has not already been spent.
A forged, copied or retained object satisfies none of those, and a genuine one
satisfies them for exactly as long as they are true.

## What it does not do

It starts no process, synchronizes no tree, installs no distribution and resets
no environment. **The six non-harness participants' work is injected**, and
under C-P5.0-LAB-I-R1 it is injected only by tests over `tmp_path`: this
authorization does not permit invoking any of them against a real participant.
It observes no process, no database backend and no tree either — those are the
six participants' external conditions, injected and attributable, and r6 §9.3's
**I9** collects them as unconfirmed proof obligations for all five it names.

An interrupted or unreadable run blocks **every** successor, the harness and the
environment reset included, until an attributable recovery is published. That is
not enforced here: it is enforced by `read_and_admit`'s survey, which this
module calls before anything else and never skips.
"""
from __future__ import annotations

import enum
import re
import sys
from dataclasses import dataclass, field
from typing import Callable, Mapping

from ..durability_model import Quiescence
from ..errors import PlanRefused
from ..lifecycle_storage import (
    PARTICIPANT_PROFILES,
    CompletionObservation,
    Participant,
    PublicationOutcome,
    RunPhase,
    SuccessorAdmission,
    TerminalPublication,
    check_reservation_history,
)
from ..provisioning import LABORATORY_LAYOUT, LaboratoryLayout
from ..reservation import (
    PARTICIPATING_ENTRY_POINTS,
    QuarantineRecord,
    ReleaseEvidence,
    ReservationRequest,
    ReservationState,
    ResidueObservation,
)
from .host_lock import LaboratorySession, LockRefused
from .run_ledger import TerminalSequence

#: Every entry point, keyed by the participant that runs it. Built from
#: `reservation.PARTICIPATING_ENTRY_POINTS` and `Participant` rather than
#: written out, so an entry point added to one and not the other fails here.
PARTICIPANT_ENTRY_POINTS: Mapping[Participant, str] = {
    participant: PARTICIPATING_ENTRY_POINTS[participant.value]
    for participant in Participant
}

#: The six that do **not** write the reservation record. They carry the start's
#: reservation field **exactly empty** — r6 §5.11.1's P9 — and they wait for the
#: lock rather than refusing, because the rule for all seven is *wait or refuse,
#: never proceed* and a suite that refused on contention would simply not run.
NON_HARNESS_PARTICIPANTS: tuple[Participant, ...] = tuple(
    participant for participant in Participant if not participant.writes_the_record
)

#: The refusals an integration point reports. Fixed, short and safe: an operator
#: sees which rule refused and never a path, a holder or an operating-system
#: message.
PARTICIPANT_LOCK_REFUSED = "cooperative-lock-refused"
PARTICIPANT_NOT_ADMITTED = "admission-refused"
PARTICIPANT_START_NOT_DURABLE = "participant-start-not-durable"
PARTICIPANT_CONDITIONS_UNMET = "completion-conditions-not-observed"
PARTICIPANT_COMPLETION_NOT_DURABLE = "completion-not-durable"
PARTICIPANT_RUN_ID_REFUSED = "run-identifier-refused"
PARTICIPANT_WORK_FAILED = "participant-work-did-not-return"
#: r6 §5.7's T7 or T8 did not reach durable storage. Only the harness can raise
#: it: the six write no reservation entry at all.
PARTICIPANT_RESERVATION_NOT_DURABLE = "reservation-entry-not-durable"
#: **PR-20260914-LABI-R1-2.** The authority offered for a first effect is not the
#: authority of a work invocation that is running **now**. It covers a forged
#: object, a retained one, a copied one and a genuine one offered twice.
PARTICIPANT_AUTHORITY_NOT_LIVE = "run-authority-not-live"

PARTICIPANT_REFUSALS: frozenset[str] = frozenset(
    {
        PARTICIPANT_LOCK_REFUSED,
        PARTICIPANT_NOT_ADMITTED,
        PARTICIPANT_START_NOT_DURABLE,
        PARTICIPANT_CONDITIONS_UNMET,
        PARTICIPANT_COMPLETION_NOT_DURABLE,
        PARTICIPANT_RUN_ID_REFUSED,
        PARTICIPANT_WORK_FAILED,
        PARTICIPANT_RESERVATION_NOT_DURABLE,
        PARTICIPANT_AUTHORITY_NOT_LIVE,
    }
)

#: Why a live authority was refused, as a closed set of fixed sentences. Each
#: names **one** conjunct and none of them carries a path, a stored byte, an
#: operating-system message or a value the caller chose: an operator is told
#: which rule refused, and a hostile caller learns nothing it did not supply.
AUTHORITY_NOT_THIS_INVOCATION = (
    "this is not the authority the running invocation issued. It was issued by "
    "another integration point or constructed beside the invocation, or the "
    "integration point's registration no longer names it"
)
#: **PR-20260914-LABI-R2-1.** Issuance and consumption are transitions of one
#: work invocation, and these name which transition refused and why.
AUTHORITY_NO_LIVE_INVOCATION = (
    "no work invocation of this integration point is running, so there is no "
    "invocation for an authority to be issued by or spent in"
)
AUTHORITY_ALREADY_ISSUED = (
    "this invocation has already issued its one authority. Issuance is a single "
    "transition, and a second attempt constructs and registers nothing"
)
AUTHORITY_ISSUANCE_NOT_BOUND = (
    "issuance names another session, run or reservation than the running "
    "invocation's own"
)
AUTHORITY_ALREADY_SPENT = (
    "this invocation's one authority has already been spent. One durable start "
    "authorizes one execution of the reviewed effects"
)
AUTHORITY_INVOCATION_ENDED = (
    "the work this authority was issued for has returned, raised or been "
    "interrupted, so its T9 is over"
)
AUTHORITY_NO_OPEN_SESSION = (
    "the integration point owns no open session, so it holds no cooperative "
    "lock and no descriptor on the record or the ledger"
)
AUTHORITY_LOCK_NOT_HELD = (
    "the cooperative lock is no longer held by this session, and an effect "
    "issued outside the hold is one another participant may be racing"
)
AUTHORITY_RUN_NOT_READABLE = (
    "the stored run is absent, unreadable, or not a valid run history"
)
AUTHORITY_RUN_WRONG_PARTICIPANT = (
    "the stored run was started by another participant, so it is another "
    "participant's accounting"
)
AUTHORITY_RUN_WRONG_RESERVATION = (
    "the stored run is bound to another reservation, and r6 §5.11.1's P7 "
    "binding is equality both ways"
)
AUTHORITY_RUN_NOT_IN_PROGRESS = (
    "the stored run is no longer in progress, so it has already been settled "
    "or recovered and accounts for no further effect"
)
AUTHORITY_RESERVATION_NOT_RUNNING = (
    "the reservation record is not in the running state r6 §5.7 places T9 "
    "inside, for exactly this reservation"
)

AUTHORITY_REFUSALS: tuple[str, ...] = (
    AUTHORITY_NOT_THIS_INVOCATION,
    AUTHORITY_NO_LIVE_INVOCATION,
    AUTHORITY_ALREADY_ISSUED,
    AUTHORITY_ISSUANCE_NOT_BOUND,
    AUTHORITY_ALREADY_SPENT,
    AUTHORITY_INVOCATION_ENDED,
    AUTHORITY_NO_OPEN_SESSION,
    AUTHORITY_LOCK_NOT_HELD,
    AUTHORITY_RUN_NOT_READABLE,
    AUTHORITY_RUN_WRONG_PARTICIPANT,
    AUTHORITY_RUN_WRONG_RESERVATION,
    AUTHORITY_RUN_NOT_IN_PROGRESS,
    AUTHORITY_RESERVATION_NOT_RUNNING,
)

#: The shape a run identifier may take before it becomes a filename, a role
#: label or a field in a refusal. **The reviewer asked for this bound**: a run
#: id is caller-supplied, it is written into a ledger filename, into the
#: recovery store's directory name and into the `runstore:<run-id>` role a
#: refusal names, and an unbounded one would put caller text in all three.
RUN_IDENTIFIER = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")


class ParticipantRefused(PlanRefused):
    """An integration point refused, with a fixed classification."""

    def __init__(self, classification: str, detail: str = "") -> None:
        if classification not in PARTICIPANT_REFUSALS:
            raise PlanRefused(
                f"{classification!r} is not one of the participant refusals. "
                "The vocabulary is closed so an operator-facing refusal cannot "
                "acquire a new meaning by being raised."
            )
        self.classification = classification
        #: The fixed sentence beside the classification, kept as an attribute so
        #: a caller that re-raises in its own vocabulary can quote the rule that
        #: refused without re-deriving it or parsing the message back apart.
        self.detail = detail
        super().__init__(f"{classification}: {detail}" if detail else classification)


def validate_run_identifier(run_id: str) -> str:
    """Bound a caller's run id **before** it becomes a name anybody stores.

    It is refused rather than sanitized: a value that has to be cleaned up is a
    value somebody chose, and the three places this one lands — a ledger
    filename, a recovery directory and a refusal's role label — each deserve a
    name nobody had to repair.
    """
    if not isinstance(run_id, str) or not RUN_IDENTIFIER.match(run_id):
        raise ParticipantRefused(
            PARTICIPANT_RUN_ID_REFUSED,
            "a run identifier is 1 to 64 characters of letters, digits, dot, "
            "dash and underscore, beginning with a letter or a digit",
        )
    return run_id


#: A marker the issuing path stamps onto a permit. It is a **convention, not a
#: secret**, and the correction below says so where a reader will see it.
#:
#: **PR-20260914-LABI-R1-2 — what this is not.** Python has no access boundary
#: here. `_PERMIT_GRANT` is an ordinary readable module attribute,
#: `_grant_permit` an ordinary callable one, and `EffectPermit.grant` a public
#: dataclass field, so a caller can read the first, call the second, and
#: construct a permit whose `issued` is `True` and whose `binds()` returns
#: `True`. The re-review did exactly that. **No claim of secrecy is made for
#: it.** It is kept because it costs nothing and it catches an accidental
#: `granted=True`; the property the executor actually relies on is
#: `consume()`'s, which is about live state rather than about possession.
_PERMIT_GRANT = object()


@dataclass(frozen=True, slots=True)
class EffectPermit:
    """A **live, one-shot** capability for one synchronous work invocation.

    **PR-20260914-LABI-R1-2.** The previous permit was a bearer token: an object
    whose possession was accepted indefinitely. Two things followed, and the
    re-review reproduced both. Its grant could be reconstructed from readable
    module attributes; and a genuinely issued one stayed `issued=True` for ever,
    so a work callback could keep it and drive an armed executor after
    `run_harness()` had published both terminal entries and released the lock.

    So this object carries no authority of its own. The four value fields are
    still the r6 §5.11.1 binding a consumer compares — one participant, one run,
    one reservation — but `consume()` is what the executor spends, and it asks
    the **protocol**, not the permit:

    | Conjunct | Read from |
    |---|---|
    | a work invocation of that integration point is running | the `_WorkInvocation` local to its `run`/`run_harness` frame |
    | this is the authority that invocation issued, and the integration point's registration still names it | the invocation's record **and** `ParticipantIntegration._authority` — one object, all three |
    | that exact integration owns an open session | `ParticipantIntegration._session` |
    | the session still holds the cooperative lock | the session's **own open descriptor** |
    | the stored run is present, valid, this participant's, bound to this reservation and still in progress | `ParticipantRunLedger.read_run` — the authoritative reader |
    | the reservation is in r6 §5.7's T8 `running` state, for this reservation | `check_reservation_history` — the authoritative walker |
    | the invocation's authority is issued, not yet spent, and its work has not ended | the invocation's record, which moves forward only |

    None of those is a fact about this object, and the first two and the last
    are not facts about any object the work callback holds either: the record is
    a local of the invocation, not an attribute. A reconstructed permit is owned
    by no invocation, and a genuine one is spendable once.
    There is deliberately **no second reader**: the two durable facts come from
    the same ledger reader every writer uses and the same reservation walk
    `derive_lifecycle_history` reads.
    """

    participant: Participant
    run_id: str
    reservation_id: str = ""
    granted: bool = False
    #: The marker described above. Compared by identity, excluded from equality
    #: and from `repr`. It is not an access boundary and is not relied on as one.
    grant: object = field(default=None, repr=False, compare=False)
    #: The integration point whose live invocation this permit belongs to, and
    #: the session it was issued over. Both are compared by **identity**, and
    #: both are `None` on anything a caller constructed — which is the whole of
    #: what a reconstructed permit is missing. Excluded from equality and from
    #: `repr`: two permits for one run still compare equal, and a refusal still
    #: prints no object graph.
    issuer: "ParticipantIntegration | None" = field(
        default=None, repr=False, compare=False
    )
    session: "LaboratorySession | None" = field(
        default=None, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        if self.granted and self.grant is not _PERMIT_GRANT:
            raise ParticipantRefused(
                PARTICIPANT_START_NOT_DURABLE,
                "a granted permit is stamped by this module after a durable "
                "`participant_started` publication. Constructing one with "
                "`granted=True` does not publish a start, and a permit that was "
                "not issued is not evidence that one exists",
            )

    @property
    def issued(self) -> bool:
        """Whether this permit carries the issuing path's marker.

        **It is not the authority check**, and it never was a strong one: the
        marker is readable. `consume()` is the check, and `issued` survives only
        as the cheap value-level half `binds()` already used.
        """
        return self.granted and self.grant is _PERMIT_GRANT

    def require(self) -> None:
        if not self.issued:
            raise ParticipantRefused(
                PARTICIPANT_START_NOT_DURABLE,
                "this participant's non-reusable state is not durably "
                "published, so it may not issue its first effect. A run whose "
                "start was never durable is a run whose effects nothing "
                "accounts for",
            )

    def binds(
        self, *, participant: Participant, run_id: str, reservation_id: str
    ) -> bool:
        """Whether this permit is evidence about **exactly** this run.

        Equality on all three, both ways. Not containment, not presence, and not
        *"the same participant will do"* — r6 §5.11.1's binding rule applied to
        the object that carries the start's authority forward.

        It is a **value** comparison and it is not sufficient on its own: a
        forged permit passes it. `consume()` is what establishes that the values
        describe something that is true right now.
        """
        return (
            self.issued
            and self.participant is participant
            and bool(run_id)
            and self.run_id == run_id
            and self.reservation_id == reservation_id
        )

    # -- the live half ---------------------------------------------------------

    def consume(self, *, integration: "ParticipantIntegration") -> None:
        """Spend the running invocation's one authority, or refuse.

        Called immediately before the first effect, by the consumer that is
        about to issue it. `integration` is the consumer's own integration
        point, and it must be **this** one: identity, not an equal-looking twin.

        The conjuncts are taken in the order that makes each one reachable and
        each refusal true. The invocation first, because an authority nobody is
        running has nothing to be spent in; then ownership, then the session,
        the lock and the two durable facts — read through the objects the session
        holds, so they are the state under **this** hold — and only then the
        spend, which is the invocation record's single `ISSUED → SPENT`
        transition.

        **PR-20260914-LABI-R2-1.** Nothing this checks for one-shotness is an
        attribute of the permit, of the integration point or of anything they
        reach. A second `consume()`, a second issuance, a registration replaced
        with a bound constructed permit, and every attribute written back to its
        value at issuance all meet a record that has already moved on. The limit
        of that claim is in the module docstring.
        """
        if (
            not isinstance(integration, ParticipantIntegration)
            or self.issuer is not integration
        ):
            raise ParticipantRefused(
                PARTICIPANT_AUTHORITY_NOT_LIVE, AUTHORITY_NOT_THIS_INVOCATION
            )
        invocation = _live_invocation(integration)
        if invocation is None:
            raise ParticipantRefused(
                PARTICIPANT_AUTHORITY_NOT_LIVE, AUTHORITY_NO_LIVE_INVOCATION
            )
        if integration._authority is not self or not invocation.owns(self):
            raise ParticipantRefused(
                PARTICIPANT_AUTHORITY_NOT_LIVE, AUTHORITY_NOT_THIS_INVOCATION
            )
        session = integration._session
        if session is None or session is not self.session:
            raise ParticipantRefused(
                PARTICIPANT_AUTHORITY_NOT_LIVE, AUTHORITY_NO_OPEN_SESSION
            )
        if not session.holds_lock:
            raise ParticipantRefused(
                PARTICIPANT_AUTHORITY_NOT_LIVE, AUTHORITY_LOCK_NOT_HELD
            )
        self._require_current_durable_state(session)
        invocation.spend()

    def _require_current_durable_state(self, session: "LaboratorySession") -> None:
        """r6 §5.7's T6–T8, re-read under this hold, immediately before T9.

        **No second reader and no second state machine.**
        `ParticipantRunLedger.read_run` is the reader every writer in this
        package already uses before it derives a lifecycle-owned fact, and
        `check_reservation_history` is the walk `derive_lifecycle_history` reads
        the current reservation and its state from. Both are called here rather
        than reimplemented, because a mechanism with its own copy of either is
        the two-readers drift every finding since R3-1 is about.
        """
        stored = session.ledger.read_run(self.run_id)
        state = stored.state
        if not stored.ok or state is None:
            raise ParticipantRefused(
                PARTICIPANT_AUTHORITY_NOT_LIVE, AUTHORITY_RUN_NOT_READABLE
            )
        if state.participant is not self.participant:
            raise ParticipantRefused(
                PARTICIPANT_AUTHORITY_NOT_LIVE, AUTHORITY_RUN_WRONG_PARTICIPANT
            )
        if state.reservation_id != self.reservation_id:
            raise ParticipantRefused(
                PARTICIPANT_AUTHORITY_NOT_LIVE, AUTHORITY_RUN_WRONG_RESERVATION
            )
        if state.phase is not RunPhase.IN_PROGRESS:
            raise ParticipantRefused(
                PARTICIPANT_AUTHORITY_NOT_LIVE, AUTHORITY_RUN_NOT_IN_PROGRESS
            )
        if not self.participant.writes_the_record:
            # The six publish no reservation entry and own no reservation state
            # — r6 §5.11.1's P9 — so there is nothing here for them to be in.
            return
        parsed = session.record.read()
        if not parsed.ok:
            raise ParticipantRefused(
                PARTICIPANT_AUTHORITY_NOT_LIVE, AUTHORITY_RESERVATION_NOT_RUNNING
            )
        history = check_reservation_history(parsed.entries)
        if (
            not history.ok
            or history.current_id != self.reservation_id
            or history.current_state is not ReservationState.RUNNING
        ):
            raise ParticipantRefused(
                PARTICIPANT_AUTHORITY_NOT_LIVE, AUTHORITY_RESERVATION_NOT_RUNNING
            )


def _grant_permit(
    *,
    participant: Participant,
    run_id: str,
    reservation_id: str,
    issuer: "ParticipantIntegration | None" = None,
    session: "LaboratorySession | None" = None,
) -> EffectPermit:
    """Stamp one permit for one durable start.

    `issuer` and `session` default to `None` deliberately, and the default is
    part of the correction rather than a convenience: this function is a
    readable module attribute and calling it directly is one of the two
    reproductions. What such a call produces is a permit with the marker, the
    right values and **no live invocation behind it**, so `consume()` refuses it
    — which is a more honest answer than a `TypeError` about a keyword.
    """
    return EffectPermit(
        participant=participant,
        run_id=run_id,
        reservation_id=reservation_id,
        granted=True,
        grant=_PERMIT_GRANT,
        issuer=issuer,
        session=session,
    )


class _InvocationState(enum.Enum):
    """Where one work invocation's authority is. It only ever moves forward."""

    #: The invocation is running and has issued nothing.
    OPEN = "open"
    #: Its one authority exists and has not been spent.
    ISSUED = "issued"
    #: Its one authority reached a consumer's first effect.
    SPENT = "spent"
    #: Its work returned, raised or was interrupted.
    ENDED = "ended"


class _WorkInvocation:
    """One synchronous work invocation's authority record. **Never an attribute.**

    **PR-20260914-LABI-R2-1.** `run()` and `run_harness()` each create exactly
    one, as a local variable, immediately before issuance. No permit, integration
    point, session or executor refers to it; `_live_invocation` finds it through
    the invocation's own frame. That is the whole of the difference from the
    registration it sits beside: a registration is state on the object graph the
    work callback holds, and this is state of the call the callback is running
    inside.

    Its two transitions are its only mutators, and each checks before it acts:
    `issue` refuses unless `OPEN` and constructs nothing until it has checked;
    `spend` refuses unless `ISSUED`. `end` is unconditional and final.
    """

    __slots__ = (
        "integration",
        "session",
        "participant",
        "run_id",
        "reservation_id",
        "_state",
        "_permit",
    )

    def __init__(
        self,
        *,
        integration: "ParticipantIntegration",
        session: LaboratorySession,
        run_id: str,
        reservation_id: str,
    ) -> None:
        self.integration = integration
        self.session = session
        self.participant = integration.participant
        self.run_id = run_id
        self.reservation_id = reservation_id
        self._state = _InvocationState.OPEN
        self._permit: EffectPermit | None = None

    def issue(
        self, *, session: LaboratorySession, run_id: str, reservation_id: str
    ) -> EffectPermit:
        """The single issuing transition, `OPEN → ISSUED`, or a refusal.

        The state is checked **before** a permit is constructed, so a refused
        issuance leaves nothing behind to register.
        """
        if self._state is not _InvocationState.OPEN:
            raise ParticipantRefused(
                PARTICIPANT_AUTHORITY_NOT_LIVE,
                AUTHORITY_INVOCATION_ENDED
                if self._state is _InvocationState.ENDED
                else AUTHORITY_ALREADY_ISSUED,
            )
        if (
            session is not self.session
            or run_id != self.run_id
            or reservation_id != self.reservation_id
        ):
            raise ParticipantRefused(
                PARTICIPANT_AUTHORITY_NOT_LIVE, AUTHORITY_ISSUANCE_NOT_BOUND
            )
        permit = _grant_permit(
            participant=self.participant,
            run_id=run_id,
            reservation_id=reservation_id,
            issuer=self.integration,
            session=session,
        )
        self._permit = permit
        self._state = _InvocationState.ISSUED
        return permit

    def owns(self, permit: EffectPermit) -> bool:
        """Whether `permit` is the object this invocation issued, with its values."""
        issued = self._permit
        return (
            issued is not None
            and permit is issued
            and permit.participant is self.participant
            and permit.run_id == self.run_id
            and permit.reservation_id == self.reservation_id
        )

    def spend(self) -> None:
        """The single consuming transition, `ISSUED → SPENT`, or a refusal."""
        if self._state is not _InvocationState.ISSUED:
            raise ParticipantRefused(
                PARTICIPANT_AUTHORITY_NOT_LIVE,
                AUTHORITY_ALREADY_SPENT
                if self._state is _InvocationState.SPENT
                else AUTHORITY_INVOCATION_ENDED,
            )
        self._state = _InvocationState.SPENT

    def end(self) -> None:
        """The work returned, raised or was interrupted. Final, and never raises."""
        self._state = _InvocationState.ENDED


def _live_invocation(
    integration: "ParticipantIntegration",
) -> _WorkInvocation | None:
    """The record of `integration`'s running work invocation, from the stack.

    Walks outward from the caller to the nearest `run`/`run_harness` frame whose
    `self` is `integration`, and returns that frame's `invocation` local — or
    `None` when there is no such frame, or it has not reached issuance. Only the
    **nearest** one counts: an inner pass of the same integration point shadows
    an outer one, and a frame that has no record yet refuses rather than falling
    through to an older one.

    It is found here rather than stored on an object so that no attribute any
    work callback can reach holds it. That is not secrecy — the module docstring
    names the introspection that reaches it — it is that ordinary attribute
    access does not.
    """
    frame = sys._getframe(1)
    while frame is not None:
        if any(frame.f_code is code for code in _INVOCATION_CODES):
            scope = frame.f_locals
            if scope.get("self") is integration:
                invocation = scope.get("invocation")
                if (
                    isinstance(invocation, _WorkInvocation)
                    and invocation.integration is integration
                ):
                    return invocation
                return None
        frame = frame.f_back
    return None


@dataclass(frozen=True, slots=True)
class HarnessObservations:
    """What the harness's own pass established, kept apart from who it is about.

    **PR-20260914-LABI-R1-1.** The release evidence used to be handed to
    `run_harness` whole, which meant the reservation, the target and the lock's
    holder — the three facts a release compares against itself — were the
    caller's claims. They are derived by `run_harness` from its own reservation,
    its own target and its own open lock descriptor now; this carries only what
    a run can observe, and `release()` treats every unmade observation exactly
    as it treats a false one.

    The first two come from the executor's **actual** cleanup outcome, and
    `ExecutingRunner.run_observations` is what derives them. The last two are
    external conditions no process in this package can observe — r6 §1.6 — so
    they are made by a named observer or they are `None`, and `None` quarantines.
    """

    residue: "ResidueObservation | None" = None
    configuration_restored: bool | None = None
    child_processes_ended: bool | None = None
    database_transactions_settled: bool | None = None

    def with_quiescence(self, quiescence: "Quiescence") -> "HarnessObservations":
        """The same run facts, plus the external observation somebody made.

        One observation, read once. r6 §1.6's quiescence gates the B3-dependent
        effects and its first two members are two of the release's conditions; a
        second, separately supplied copy of them would be the two-readers drift
        every finding since R3-1 is about.
        """
        established = quiescence.observed and bool(quiescence.observed_by.strip())
        return HarnessObservations(
            residue=self.residue,
            configuration_restored=self.configuration_restored,
            child_processes_ended=(
                quiescence.processes_ended if established else None
            ),
            database_transactions_settled=(
                quiescence.transactions_settled if established else None
            ),
        )


@dataclass(frozen=True, slots=True)
class ParticipantRun:
    """What one participant's pass concluded, and how far it got.

    The four booleans are kept apart on purpose. `admitted` is the decision,
    `started` is a durable publication, `effects_permitted` is whether the work
    was reached at all, and `completed` is a second durable publication. A run
    that is `started` and not `completed` is **unsettled**, and an unsettled run
    refuses every successor — including the harness and the environment reset —
    until an attributable recovery is published.
    """

    entry_point: str
    participant: Participant
    run_id: str
    admitted: bool = False
    started: bool = False
    effects_permitted: bool = False
    completed: bool = False
    refusal: str = ""
    reasons: tuple[str, ...] = ()
    admission: SuccessorAdmission | None = None
    start: PublicationOutcome | None = None
    completion: PublicationOutcome | None = None

    @property
    def unsettled(self) -> bool:
        return self.started and not self.completed


@dataclass(frozen=True, slots=True)
class HarnessRun:
    """The harness's pass, and the terminal publication it concluded with.

    `run` carries the same four facts every participant's does; `terminal` is
    §5.12's own result, kept beside it rather than folded into it because a
    refused conclusion and a refused completion are different states and the
    operator recovery differs.
    """

    run: "ParticipantRun"
    terminal: "TerminalPublication | None" = None

    @property
    def released(self) -> bool:
        """Whether the reservation's `released` entry reached durable storage.

        It is **not** whether a successor may reuse the host. Between §5.12's
        steps 2 and 3 the record says `released` and this run is still
        `participant_started` in the ledger, and an unsettled run refuses every
        successor including the environment reset. Both halves, or neither.
        """
        return bool(
            self.terminal is not None
            and self.terminal.release_entry is not None
            and self.terminal.release_entry.published
        )


#: What one participant's work returns: its external completion conditions, as
#: observed by a named observer. The keys are the profile's exact condition
#: strings, and a missing or false one refuses the completion.
Work = Callable[[EffectPermit], Mapping[str, bool]]

#: What the **harness's** work returns, which is not the same thing. The harness
#: publishes no injected completion observation — r6 §5.12 derives its two
#: conditions — so its work reports what its run established and nothing about
#: its own completion.
HarnessWork = Callable[[EffectPermit], HarnessObservations]


@dataclass(slots=True)
class ParticipantIntegration:
    """One entry point's whole pass through the reservation protocol.

    Construct one per participant. `session_factory` is injected so a test can
    run the complete sequence over a laboratory under `tmp_path`; production
    passes nothing and gets `LaboratorySession` over the provisioned layout,
    which refuses on an absent lock or an absent record rather than creating
    either.
    """

    participant: Participant
    host: str
    target_identity: str
    #: The identity this participant runs as. It is compared with the profile's
    #: declared identity by `lifecycle_storage`'s participant validator, so a
    #: run whose account of who ran it disagrees with its profile refuses.
    author: str
    at: str
    layout: LaboratoryLayout = LABORATORY_LAYOUT
    reservation_id: str = ""
    quarantine: QuarantineRecord | None = None
    #: `True` for the six: the rule is *wait or refuse, never proceed*, and a
    #: suite that refused on contention would simply not run. The harness takes
    #: the lock for the reservation and refuses rather than waiting behind one.
    wait_for_lock: bool = True
    session_factory: Callable[..., LaboratorySession] | None = None
    _session: LaboratorySession | None = field(default=None, init=False)
    #: **PR-20260914-LABI-R1-2 and -R2-1.** The registration: the permit the
    #: running invocation issued, set by that issuance and cleared when the work
    #: returns, raises or is interrupted. It is **not** the one-shot state. Any
    #: holder of this object can assign it, which is what the re-review did, so
    #: `EffectPermit.consume` requires it to be the same object as the invocation
    #: record's issued permit: a replaced registration makes even the genuine
    #: authority refuse, and a registered permit the invocation did not issue
    #: authorizes nothing.
    _authority: "EffectPermit | None" = field(default=None, init=False)

    @property
    def entry_point(self) -> str:
        return PARTICIPANT_ENTRY_POINTS[self.participant]

    @property
    def profile(self):
        """This participant's declared identity and exact completion conditions."""
        return PARTICIPANT_PROFILES[self.participant]

    # -- the pass -------------------------------------------------------------

    def run(self, *, run_id: str, work: Work, observed_by: str) -> ParticipantRun:
        """§5.6's order, and no step of it is optional.

        The work is reached only after a durable start, and the completion is
        published only after this participant's **exact** profile conditions are
        observed. Every earlier refusal returns without calling the work at all,
        so a refused participant has issued no effect to account for.
        """
        run_id = validate_run_identifier(run_id)
        session = self._open()
        try:
            admission = session.admit()
            if not admission.may_proceed:
                return self._refused(
                    run_id,
                    PARTICIPANT_NOT_ADMITTED,
                    admission.refusals,
                    admission=admission,
                )

            start = session.ledger.begin(
                run_id=run_id,
                participant=self.participant,
                author=self.author,
                at=self.at,
                reservation_id=self._start_reservation(),
            )
            if not start.published:
                return self._refused(
                    run_id,
                    PARTICIPANT_START_NOT_DURABLE,
                    start.reasons,
                    admission=admission,
                    start=start,
                )

            invocation = _WorkInvocation(
                integration=self,
                session=session,
                run_id=run_id,
                reservation_id=self._start_reservation(),
            )
            try:
                permit = self._issue_authority(
                    session, run_id=run_id, reservation_id=self._start_reservation()
                )
                observed = work(permit)
            finally:
                # The authority is the invocation's, not the holder's. It ends
                # when the call does, whether it returned, raised or was
                # interrupted.
                self._revoke_authority(invocation)
            if not isinstance(observed, Mapping):
                raise ParticipantRefused(
                    PARTICIPANT_WORK_FAILED,
                    "a participant's work returns the external completion "
                    "conditions it observed, keyed by the profile's own "
                    "condition strings",
                )

            observation = CompletionObservation(
                observed_by=observed_by, observed=dict(observed)
            )
            missing = observation.missing(self.profile)
            if missing:
                return ParticipantRun(
                    entry_point=self.entry_point,
                    participant=self.participant,
                    run_id=run_id,
                    admitted=True,
                    started=True,
                    effects_permitted=True,
                    refusal=PARTICIPANT_CONDITIONS_UNMET,
                    reasons=tuple(missing),
                    admission=admission,
                    start=start,
                )

            completion = session.ledger.complete(
                run_id=run_id,
                participant=self.participant,
                observation=observation,
                author=self.author,
                at=self.at,
            )
            return ParticipantRun(
                entry_point=self.entry_point,
                participant=self.participant,
                run_id=run_id,
                admitted=True,
                started=True,
                effects_permitted=True,
                completed=completion.published,
                refusal=(
                    "" if completion.published else PARTICIPANT_COMPLETION_NOT_DURABLE
                ),
                reasons=() if completion.published else tuple(completion.reasons),
                admission=admission,
                start=start,
                completion=completion,
            )
        finally:
            # Step 4, and it is here rather than earlier: releasing the lock is
            # not evidence that the run ended, and every publication above
            # happens while it is still held.
            self.close()

    def run_harness(
        self,
        *,
        run_id: str,
        work: "HarnessWork",
        request: "ReservationRequest",
        observed_by: str,
    ) -> "HarnessRun":
        """The harness's whole pass, whose tail is §5.12 exactly — steps 0 to 4.

        **PR-20260914-LABI-R1-1.** This method is the executable harness call.
        The CLI does not construct the objects and then drive the executor
        itself: it hands the executor's work to this method, which takes the
        lock, admits, publishes the durable start, issues the permit the
        executor requires, runs the work, derives the release evidence from what
        the work returned, publishes §5.12's two terminal entries and only then
        releases the lock. Constructing the objects without calling their
        protocol is what the re-review found, and there is no longer a path that
        reaches an effect without passing through here.

        The six publish a completion from an injected observation. The harness
        cannot: its two conditions are facts about a release **this process
        performs**, so they are derived from steps 1 and 2 and an injected
        observation of either is refused at the writer. That is r6 §5.12's whole
        argument and PR-20260911-R4-3's repair, and it is why this method exists
        beside `run()` instead of passing different arguments to it.

        | Step | What happens |
        |---|---|
        | **0** | check the reservation binding. A mismatch refuses and **publishes nothing** |
        | 1 | evaluate the release decision — RELEASED, or quarantine |
        | 2 | publish the reservation's `released` entry durably |
        | 3 | publish the harness participant's completion |
        | 4 | release the lock — here and nowhere earlier |

        **What the work may not decide.** It returns `HarnessObservations`, and
        nothing else. The reservation the evidence names, the target it reports
        and the lock's holder are derived below from this integration point's own
        reservation, its own target and its own open lock descriptor — the three
        comparisons `reservation.release` makes are therefore comparisons of the
        protocol against itself rather than of a caller's claim against another.

        **An exception leaves the start unsettled, and that is deliberate.** If
        the work raises — including `KeyboardInterrupt` — no completion and no
        release is published, the `finally` releases the lock, and the durable
        `participant_started` entry blocks every successor until an attributable
        recovery is published. A run that was interrupted mid-effect is exactly
        the run r6 §5.11 refuses to let a successor step over.
        """
        if not self.participant.writes_the_record:
            raise ParticipantRefused(
                PARTICIPANT_NOT_ADMITTED,
                "only the harness concludes a reservation. The six others are "
                "not reservations and publish no reservation entry",
            )
        self._require_request_binding(request)
        run_id = validate_run_identifier(run_id)
        session = self._open()
        try:
            admission = session.admit()
            if not admission.may_proceed:
                return HarnessRun(
                    run=self._refused(
                        run_id,
                        PARTICIPANT_NOT_ADMITTED,
                        admission.refusals,
                        admission=admission,
                    )
                )
            start = session.ledger.begin(
                run_id=run_id,
                participant=self.participant,
                author=self.author,
                at=self.at,
                reservation_id=self._start_reservation(),
            )
            if not start.published:
                return HarnessRun(
                    run=self._refused(
                        run_id,
                        PARTICIPANT_START_NOT_DURABLE,
                        start.reasons,
                        admission=admission,
                        start=start,
                    )
                )
            # **r6 §5.7, T7 and T8.** The reservation's own entries, in the
            # contract's order: `admitted` precedes the first effect of any
            # kind, `running` precedes the first mutating step, and both follow
            # this participant's `participant_started`. Without them the release
            # at the tail would name a reservation the history never admitted,
            # and §5.12 would have no reachable successful path — which is
            # R4-3's defect, in a different entry.
            reservation_entries = self._publish_reservation_entries(session)
            if reservation_entries is not None:
                return HarnessRun(
                    run=self._refused(
                        run_id,
                        PARTICIPANT_RESERVATION_NOT_DURABLE,
                        reservation_entries,
                        admission=admission,
                        start=start,
                    )
                )
            invocation = _WorkInvocation(
                integration=self,
                session=session,
                run_id=run_id,
                reservation_id=self.reservation_id,
            )
            try:
                permit = self._issue_authority(
                    session, run_id=run_id, reservation_id=self.reservation_id
                )
                observations = work(permit)
            finally:
                # **T9 ends here.** Everything below is T10a to T12, and the
                # work's authority does not reach into it: the invocation's
                # record says its work has ended and the registration is
                # cleared, so an object the work kept is refused from this line
                # onward, even while this frame and the lock are still live.
                self._revoke_authority(invocation)
            if not isinstance(observations, HarnessObservations):
                raise ParticipantRefused(
                    PARTICIPANT_WORK_FAILED,
                    "the harness's work returns the observations its own run "
                    "established, as a `HarnessObservations`. A release whose "
                    "evidence came from somewhere other than the run it is "
                    "releasing is the fail-open shape this method exists to "
                    "close",
                )
            terminal = TerminalSequence(
                record=session.record, ledger=session.ledger
            ).conclude(
                request=request,
                # **Derived, not injected.** The admission admitted and this
                # process published the start, so the reservation is running.
                # It is a fact about operations this process performed rather
                # than a state a caller asserted about the record it is writing.
                current_state=ReservationState.RUNNING,
                evidence=self._release_evidence(session, observations),
                run_id=run_id,
                author=self.author,
                at=self.at,
                observed_by=observed_by,
            )
            return HarnessRun(
                run=ParticipantRun(
                    entry_point=self.entry_point,
                    participant=self.participant,
                    run_id=run_id,
                    admitted=True,
                    started=True,
                    effects_permitted=True,
                    completed=terminal.concluded,
                    refusal=(
                        ""
                        if terminal.concluded
                        else PARTICIPANT_COMPLETION_NOT_DURABLE
                    ),
                    reasons=() if terminal.concluded else terminal.refusals,
                    admission=admission,
                    start=start,
                ),
                terminal=terminal,
            )
        finally:
            self.close()

    def recover(self, *, run_id: str, reference: str) -> PublicationOutcome:
        """An attributed operator recovery for an interrupted run.

        A crashed run blocks until its recovery is **published**. This is that
        publication, and it is a bounded operator action with a named owner
        rather than an indefinite dead end. The recovered run's own identity is
        never reused: exclusive creation refuses it.
        """
        run_id = validate_run_identifier(run_id)
        session = self._open()
        try:
            return session.ledger.recover(
                run_id=run_id,
                participant=self.participant,
                reference=reference,
                author=self.author,
                at=self.at,
            )
        finally:
            self.close()

    # -- lifetime -------------------------------------------------------------

    def _open(self) -> LaboratorySession:
        if self._session is not None:  # pragma: no cover - one pass per object
            raise ParticipantRefused(
                PARTICIPANT_LOCK_REFUSED,
                "this integration point is already holding the cooperative lock",
            )
        factory = self.session_factory or self._default_session
        session = factory()
        try:
            session.open()
        except LockRefused as refusal:
            raise ParticipantRefused(
                PARTICIPANT_LOCK_REFUSED, refusal.classification
            ) from None
        self._session = session
        return session

    def _default_session(self) -> LaboratorySession:
        return LaboratorySession(
            participant=self.participant,
            host=self.host,
            target_identity=self.target_identity,
            read_by=self.author,
            read_at=self.at,
            layout=self.layout,
            reservation_id=self.reservation_id,
            quarantine=self.quarantine,
            wait_for_lock=self.wait_for_lock,
        )

    def close(self) -> None:
        session, self._session = self._session, None
        if session is not None:
            session.close()

    # -- the live authority ---------------------------------------------------

    def _issue_authority(
        self, session: LaboratorySession, *, run_id: str, reservation_id: str
    ) -> EffectPermit:
        """Issue the running invocation's one authority, or refuse.

        **PR-20260914-LABI-R2-1.** This used to construct and register a permit
        whenever it was called, so a work callback could call it again after the
        spend. It is now the invocation record's `OPEN → ISSUED` transition:
        with no running invocation of this integration point it refuses, and a
        second attempt — before or after the first authority is spent — refuses
        before any permit is constructed or registered. Only a successful
        issuance writes the registration.
        """
        invocation = _live_invocation(self)
        if invocation is None:
            raise ParticipantRefused(
                PARTICIPANT_AUTHORITY_NOT_LIVE, AUTHORITY_NO_LIVE_INVOCATION
            )
        permit = invocation.issue(
            session=session, run_id=run_id, reservation_id=reservation_id
        )
        self._authority = permit
        return permit

    def _revoke_authority(self, invocation: _WorkInvocation) -> None:
        """End the invocation's authority: its record, then the registration.

        Called from the `finally` around the work, so return, exception and
        interruption all pass through it. It never raises.
        """
        invocation.end()
        self._authority = None

    # -- internals ------------------------------------------------------------

    def _start_reservation(self) -> str:
        """§5.11.1's P9: an identity for the harness, **exactly empty** for six.

        It is derived from the profile rather than taken from the caller, so a
        suite start carrying a reservation and a harness start carrying none
        both refuse as an invalid history — at the writer, before a byte is
        written.
        """
        return self.reservation_id if self.participant.writes_the_record else ""

    def _require_request_binding(self, request: "ReservationRequest") -> None:
        """The reservation this concludes is the one this point took the lock for.

        Checked **before** the lock is taken, because a mismatch is entirely the
        caller's error and refusing it here costs nobody the lock. `release()`
        compares the evidence with the request; this compares the request with
        the integration point, so the three cannot be made to agree by supplying
        two halves of a different reservation.
        """
        mismatches = []
        if request.reservation_id != self.reservation_id:
            mismatches.append("reservation")
        if request.target_identity != self.target_identity:
            mismatches.append("target")
        if request.host != self.host:
            mismatches.append("host")
        if mismatches:
            raise ParticipantRefused(
                PARTICIPANT_NOT_ADMITTED,
                "the reservation being concluded is not the one this "
                f"integration point holds: {mismatches} disagree. Nothing was "
                "locked, read or published",
            )

    def _publish_reservation_entries(
        self, session: LaboratorySession
    ) -> tuple[str, ...] | None:
        """T7 then T8, durably, or the reasons the first of them refused.

        `None` means both reached durable storage. Anything else is returned
        rather than raised so that the caller keeps the run's durable start
        exactly where it is: an entry that was published and one that was not is
        a state an operator recovers, and it is never a state this method tidies
        up by writing more.
        """
        admitted = session.record.admit_reservation(
            reservation_id=self.reservation_id, author=self.author, at=self.at
        )
        if not admitted.published:
            return tuple(admitted.reasons)
        running = session.record.start_running(
            reservation_id=self.reservation_id, author=self.author, at=self.at
        )
        if not running.published:
            return tuple(running.reasons)
        return None

    def _release_evidence(
        self, session: LaboratorySession, observations: "HarnessObservations"
    ) -> ReleaseEvidence:
        """The run's observations, plus three facts the protocol derives.

        `lock_held_by` is derived from the session's **own open descriptor**, so
        an early release cannot pass for a held lock: `release()` refuses when
        the holder is not the reservation, and the only way this reports the
        reservation is that the lock is genuinely still held here.
        """
        return ReleaseEvidence(
            reservation_id=self.reservation_id,
            target_identity=self.target_identity,
            lock_held_by=self.reservation_id if session.holds_lock else None,
            child_processes_ended=observations.child_processes_ended,
            database_transactions_settled=(
                observations.database_transactions_settled
            ),
            residue=observations.residue,
            configuration_restored=observations.configuration_restored,
        )

    def _refused(
        self,
        run_id: str,
        classification: str,
        reasons,
        *,
        admission: SuccessorAdmission | None = None,
        start: PublicationOutcome | None = None,
    ) -> ParticipantRun:
        return ParticipantRun(
            entry_point=self.entry_point,
            participant=self.participant,
            run_id=run_id,
            admitted=admission.may_proceed if admission is not None else False,
            started=bool(start is not None and start.published),
            refusal=classification,
            reasons=tuple(reasons),
            admission=admission,
            start=start,
        )


#: The code of the two methods whose frames own a `_WorkInvocation`. Matched by
#: **identity**, frame by frame: code objects compare equal by structure, so a
#: set membership test would accept any function that happened to compile alike.
_INVOCATION_CODES: tuple[object, ...] = (
    ParticipantIntegration.run.__code__,
    ParticipantIntegration.run_harness.__code__,
)


def integration_for(
    participant: Participant,
    *,
    host: str,
    target_identity: str,
    author: str,
    at: str,
    **keywords,
) -> ParticipantIntegration:
    """One integration point, for one of the seven. There is no eighth.

    A factory rather than seven classes: the sequence is identical for all
    seven, and writing it seven times is how an exemption gets into one of them.
    """
    if not isinstance(participant, Participant):
        raise PlanRefused(
            "an integration point is built for one of the seven participants "
            "`reservation.PARTICIPATING_ENTRY_POINTS` enumerates."
        )
    return ParticipantIntegration(
        participant=participant,
        host=host,
        target_identity=target_identity,
        author=author,
        at=at,
        **keywords,
    )


__all__ = [
    "AUTHORITY_ALREADY_ISSUED",
    "AUTHORITY_ALREADY_SPENT",
    "AUTHORITY_INVOCATION_ENDED",
    "AUTHORITY_ISSUANCE_NOT_BOUND",
    "AUTHORITY_LOCK_NOT_HELD",
    "AUTHORITY_NOT_THIS_INVOCATION",
    "AUTHORITY_NO_LIVE_INVOCATION",
    "AUTHORITY_NO_OPEN_SESSION",
    "AUTHORITY_REFUSALS",
    "AUTHORITY_RESERVATION_NOT_RUNNING",
    "AUTHORITY_RUN_NOT_IN_PROGRESS",
    "AUTHORITY_RUN_NOT_READABLE",
    "AUTHORITY_RUN_WRONG_PARTICIPANT",
    "AUTHORITY_RUN_WRONG_RESERVATION",
    "PARTICIPANT_AUTHORITY_NOT_LIVE",
    "HarnessObservations",
    "HarnessRun",
    "HarnessWork",
    "NON_HARNESS_PARTICIPANTS",
    "PARTICIPANT_COMPLETION_NOT_DURABLE",
    "PARTICIPANT_CONDITIONS_UNMET",
    "PARTICIPANT_ENTRY_POINTS",
    "PARTICIPANT_LOCK_REFUSED",
    "PARTICIPANT_NOT_ADMITTED",
    "PARTICIPANT_REFUSALS",
    "PARTICIPANT_RESERVATION_NOT_DURABLE",
    "PARTICIPANT_RUN_ID_REFUSED",
    "PARTICIPANT_START_NOT_DURABLE",
    "PARTICIPANT_WORK_FAILED",
    "RUN_IDENTIFIER",
    "EffectPermit",
    "ParticipantIntegration",
    "ParticipantRefused",
    "ParticipantRun",
    "Work",
    "integration_for",
    "validate_run_identifier",
]
