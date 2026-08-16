"""Session lifecycle: creation, rotation, expiry, revocation (SM-02).

Four properties, each of which is a mechanism rather than a habit:

1. **The cookie is not the session id.** The cookie carries 256 bits of random
   token; the row carries its SHA-256. A database read yields nothing a browser
   could present, and the id that appears in `rotated_from_session_id` and in
   audit records is not a credential.
2. **Rotation is insert + revoke, never an in-place id change**, and the chain it
   builds is **linear**. A stolen cookie value is dead the instant rotation
   happens, the chain stays auditable, and no session can acquire two successors:
   the predecessor is read under a row lock and revoked in the same statement
   sequence that inserts its one successor, while a partial unique index and two
   composite foreign keys refuse a branch or a crossing independently of this
   code (OD-44 condition 2).
3. **Expiry is evaluated server-side on every request.** There is no cache of
   "this session was valid"; that cache is exactly what would let a revoked
   session serve one more request.
4. **An idle refresh can never pass the absolute bound, and neither can a
   rotation — and neither may act on a session that is already past either
   bound.** Liveness is a `now()` comparison, so both operations put it in the
   single conditional statement that performs the write, where no caller can
   pass a stale answer: a record resolved while the session was valid cannot
   refresh or rotate it a minute after its idle window closed. The idle clamp is
   in the `UPDATE` statement, and a check
   constraint refuses the row if it ever is not. A rotation inherits the
   predecessor's absolute expiration rather than taking a fresh one, so one login
   has one absolute bound however many times it rotates, and only a session still
   inside both of its bounds may be rotated at all.
5. **A session's idle window is a property of the session, not of the caller —
   and not of what the caller can build either.** The refresh duration is not a
   parameter at any layer, and there is no object anywhere that pairs an
   authentication method with a duration. `SessionPolicy` holds five validated
   numbers with fixed roles; which of them a method gets is decided by
   `session_class_of()`, an explicit table in `application/web/capabilities.py`.
   The conditional `UPDATE` selects from that using the `auth_method` **the row
   carries**. One policy is derived per repository, from one `SessionSettings`,
   and the service takes the repository's rather than accepting its own.

Rotation fires on a **detected privilege change** (N-08), and the fingerprint it
compares is recomputed from a fresh capability resolution — never read back from
the session row it is about to replace.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from application.audit import ActorCapability, AuditEvent, AuditSource
from application.web.capabilities import (
    AuthMethod,
    SessionClass,
    WebAuthorizationContext,
    session_class_of,
)
from application.web.config import SessionSettings, validate_session_policy_values
from application.web.crypto import mint_token, token_hash


@dataclass(frozen=True, slots=True)
class IssuedSession:
    """A new session, and the one moment its token exists outside the browser."""

    session_id: UUID
    token: str
    idle_expires_at: datetime
    absolute_expires_at: datetime


@dataclass(frozen=True, slots=True)
class SessionBounds:
    """One method's two windows, as `begin()` and `rotate()` propose them."""

    idle: timedelta
    absolute: timedelta


@dataclass(frozen=True, slots=True)
class SessionPolicy:
    """The validated session-governance numbers, derived once and then fixed.

    **This is not the deleted `SessionIdlePolicy`** (removed 2026-08-15 by the
    idle-policy-construction remediation), and the difference is the point:

    - it holds **numbers with fixed roles**, never a method-to-duration pairing.
      There is no mapping, no tuple of pairs, no `__iter__` — so there is nothing
      for a caller to supply, and nothing for a subclass to override. Finding F2
      turned on `SessionIdlePolicy.__iter__` being both overridable and the thing
      the refresh SQL was generated from; a subclass could inherit the supported
      factory, replace the SQL's mapping, and leave `for_method()` still
      reporting fifteen minutes. Which duration each method gets is now
      `session_class_of()` — a table in `application/web/capabilities.py` that no
      instance of anything can restate;
    - it is **derived, never injected**. `SessionRepository` builds it from a
      `SessionSettings` and owns it; nothing accepts one from a caller. So the
      hole a subclass of *this* type could open — override `__post_init__`, skip
      validation — has no way in.

    `derive()` is the supported construction and reads each configured number
    exactly once. That matters against a `SessionSettings` subclass whose fields
    are properties: whatever such a property answers, it answers once, and that
    one answer is what is validated *and* what reaches the SQL. There is no
    second read for it to answer differently.

    `__post_init__` re-checks the register so that a directly constructed
    instance is valid too. That is not a guard against a caller — there is no
    supported caller — but against a future edit that introduces one, and against
    a `dataclasses.replace()` of a valid policy.

    **Both checks are one shared definition** (2026-08-15,
    session-policy numeric-validation remediation). `derive()` and
    `__post_init__` call `_validate_policy_values`, which calls
    `validate_session_policy_values` in `application/web/config.py` — the same
    function `SessionSettings.__post_init__` calls. "Reads each number once" is
    only worth something if the one read is validated completely, and it was not:
    the check here had been restated as two ordering comparisons, so a non-finite
    `max_sessions_per_account` satisfied both and disabled N-66 at
    `_enforce_session_limit`.
    """

    ordinary_idle: timedelta
    ordinary_absolute: timedelta
    emergency_idle: timedelta
    emergency_absolute: timedelta
    max_sessions_per_account: int

    def __post_init__(self) -> None:
        _validate_policy_values(
            ordinary_idle_minutes=_whole_minutes(self.ordinary_idle, "ordinary_idle"),
            absolute_hours=_whole_hours(self.ordinary_absolute, "ordinary_absolute"),
            emergency_idle_minutes=_whole_minutes(
                self.emergency_idle, "emergency_idle"
            ),
            emergency_absolute_minutes=_whole_minutes(
                self.emergency_absolute, "emergency_absolute"
            ),
            max_sessions_per_account=self.max_sessions_per_account,
        )

    @classmethod
    def derive(cls, settings: SessionSettings) -> "SessionPolicy":
        """The one supported construction: read configuration once, validate, fix.

        Raises `TypeError` if `settings` is not `SessionSettings` — a duck type
        would be a way to supply numbers that never met the register — and
        `ValueError` if any number it reads is not one the register accepts.

        **`isinstance` is not the whole check, and treating it as one was the
        defect** (2026-08-15). Subclasses are accepted here deliberately, so what
        this method reads is not necessarily what `SessionSettings.__post_init__`
        observed: a subclass whose field is a property, or whose
        `__getattribute__` answers differently on a later read, passes inherited
        construction validation with a stored integer and then hands *this* read
        whatever it likes. Reading once closes the "checked one value, used
        another" half; the other half is that the one value read must be held to
        the **same type and range rule** the settings gate applies, which is why
        the validation below is the shared definition and not a local restatement
        of it. Before the correction it was a local restatement missing the type
        rule, and `float("nan")` passed both of its comparisons.
        """
        if not isinstance(settings, SessionSettings):
            raise TypeError(
                "session bounds are derived from SessionSettings, which "
                f"validates the accepted register at construction, not from {settings!r}"
            )
        # Each attribute is read exactly once, into a local. Everything below —
        # validation and the durations the SQL is generated from — uses the
        # local, so a property that answered differently on a second read has no
        # second read to answer.
        idle_minutes = settings.idle_minutes
        absolute_hours = settings.absolute_hours
        emergency_idle_minutes = settings.emergency_idle_minutes
        emergency_absolute_minutes = settings.emergency_absolute_minutes
        max_sessions_per_account = settings.max_sessions_per_account
        _validate_policy_values(
            ordinary_idle_minutes=idle_minutes,
            absolute_hours=absolute_hours,
            emergency_idle_minutes=emergency_idle_minutes,
            emergency_absolute_minutes=emergency_absolute_minutes,
            max_sessions_per_account=max_sessions_per_account,
        )
        return cls(
            ordinary_idle=timedelta(minutes=idle_minutes),
            ordinary_absolute=timedelta(hours=absolute_hours),
            emergency_idle=timedelta(minutes=emergency_idle_minutes),
            emergency_absolute=timedelta(minutes=emergency_absolute_minutes),
            max_sessions_per_account=max_sessions_per_account,
        )

    def idle_for(self, auth_method: AuthMethod) -> timedelta:
        """N-06's window or N-15's, by explicit classification.

        `session_class_of()` raises for a method nobody classified rather than
        returning either window, so a future authentication method reaches this
        as a refusal and not as a default.
        """
        return (
            self.emergency_idle
            if session_class_of(auth_method) is SessionClass.BREAK_GLASS
            else self.ordinary_idle
        )

    def absolute_for(self, auth_method: AuthMethod) -> timedelta:
        """N-07's twelve hours or N-15's sixty minutes, by the same classification."""
        return (
            self.emergency_absolute
            if session_class_of(auth_method) is SessionClass.BREAK_GLASS
            else self.ordinary_absolute
        )

    def bounds_for(self, auth_method: AuthMethod) -> SessionBounds:
        return SessionBounds(
            idle=self.idle_for(auth_method), absolute=self.absolute_for(auth_method)
        )


def _whole_minutes(value: timedelta, name: str) -> int:
    if not isinstance(value, timedelta):
        raise ValueError(f"{name} must be a timedelta, not {value!r}")
    seconds = value.total_seconds()
    if seconds % 60:
        raise ValueError(f"{name} must be a whole number of minutes, not {value}")
    return int(seconds // 60)


def _whole_hours(value: timedelta, name: str) -> int:
    if not isinstance(value, timedelta):
        raise ValueError(f"{name} must be a timedelta, not {value!r}")
    seconds = value.total_seconds()
    if seconds % 3600:
        raise ValueError(f"{name} must be a whole number of hours, not {value}")
    return int(seconds // 3600)


def _validate_policy_values(
    *,
    # Annotated `object` rather than `int` on purpose. These parameters are where
    # unvalidated numbers arrive — that is the function's entire job — and an
    # `int` annotation here would be a claim about the values that nothing
    # enforces at runtime. The check below is the enforcement; the annotation is
    # honest about the input.
    ordinary_idle_minutes: object,
    absolute_hours: object,
    emergency_idle_minutes: object,
    emergency_absolute_minutes: object,
    max_sessions_per_account: object,
) -> None:
    """The accepted register, checked at the boundary these numbers govern sessions.

    The second of two gates. `SessionSettings` refuses an out-of-register value at
    its own construction (finding F1), and this refuses one here — because the
    thing that must hold is a property of *the numbers that reach the refresh
    statement and the session limit*, and a free function reading locals is the
    one form of that check no subclass can override and no property can answer
    twice.

    **It is the same check, not a second one** (corrected 2026-08-15,
    session-policy numeric-validation remediation). This function used to restate
    the register as two ordering comparisons, and two ordering comparisons are not
    the whole-number rule the settings gate applies: `float("nan")` is neither
    `< 1` nor `> ceiling`, so it survived as `max_sessions_per_account`, and
    `len(live) >= maximum` in `_enforce_session_limit` was then false for every
    live-session count — N-66 revoked nothing. The register's type and range
    semantics now have one definition, `validate_session_policy_values` in
    `application/web/config.py`, and both gates call it. Restating it here is
    exactly the drift that produced the defect.

    It deliberately does **not** require the emergency idle window to be shorter
    than the ordinary one. `WEB_SESSION_IDLE_MINUTES` may fall to 1 while
    `WEB_EMERGENCY_SESSION_IDLE_MINUTES` ceilings at 15, so that ordering is a
    property of some accepted configurations rather than of all of them, and
    inventing it here would refuse a configuration the contract allows.
    """
    validate_session_policy_values(
        {
            "idle_minutes": ordinary_idle_minutes,
            "absolute_hours": absolute_hours,
            "emergency_idle_minutes": emergency_idle_minutes,
            "emergency_absolute_minutes": emergency_absolute_minutes,
            "max_sessions_per_account": max_sessions_per_account,
        },
        subject="session bounds",
    )


class SessionRotationRefused(Exception):
    """A rotation that cannot be performed, refused rather than improvised.

    Raised when the predecessor is unknown, revoked, **idle-expired**,
    **absolute-expired**, already rotated, or does not belong to the account and
    authentication method the caller resolved. The caller's correct response is
    to end the session, not to retry: every one of those states means the session
    presenting itself is no longer the live one, and issuing a second successor
    is precisely the branch OD-44 condition 2 forbids.

    The two expiry states were added on 2026-08-14. A caller holding a
    `SessionRecord` resolved while the session was valid could otherwise rotate
    it after either bound had passed and receive a live successor — an expired
    session revived rather than ended.

    It is deliberately **not** `None`. `rotate_if_privileges_changed` already uses
    `None` for "nothing changed", and a refusal that shared that value would be a
    refusal a caller could not distinguish from success.
    """


@dataclass(frozen=True, slots=True)
class RefreshedSession:
    """The bounds an accepted idle refresh left on the row.

    Reported rather than recomputed: the idle expiration is clamped to the
    absolute bound inside the conditional write, so `now + bounds.idle` is not
    the value the row has whenever the clamp bites. `absolute_expires_at` is the
    unchanged bound the login set — touch never writes it.
    """

    session_id: UUID
    idle_expires_at: datetime
    absolute_expires_at: datetime


class SessionTouchRefused(Exception):
    """An idle refresh that cannot be performed, refused rather than ignored.

    Raised when the session is unknown, revoked, **idle-expired** or
    **absolute-expired**. The caller's correct response is the same as for
    `SessionRotationRefused`: **end the session — clear the cookie and treat the
    request as unauthenticated — and do not retry it as though still
    authenticated.** Every one of those states means the session presenting
    itself is no longer live, and a refresh that proceeded would be an expired
    session revived.

    Added on 2026-08-15 with the touch-lifetime correction. The repository
    previously returned nothing at all, so a zero-row update — the exact shape of
    a refused refresh — was indistinguishable from a successful one, and the
    service reported success for a write that never happened.

    "Not this authentication method" left the list on 2026-08-15 when the
    duration stopped being an argument. The method is no longer something a
    caller asserts and the statement checks; it is read from the row to choose
    the window. A row whose method the configured policy does not govern is still
    refused here — see `SessionRepository.touch()` — but no reachable row has one.
    """


class SessionService:
    """Owns every write to `sessions`. Transactions belong to the caller."""

    __slots__ = ("_sessions", "_tokens", "_audit", "_policy")

    def __init__(self, *, sessions, token_grants, audit) -> None:
        """Bounds come **from the repository**, and are not a second argument.

        Corrected 2026-08-15 (idle-policy-construction remediation, finding F3).
        This constructor previously took `settings` and `idle_policy` of its own
        beside the repository, and nothing required them to agree with the
        repository's. Correct wiring at the two production construction sites was
        real but was not an invariant: a supported caller could build the
        repository from one `SessionSettings` and the service from another and
        get a graph that creates sessions under one idle window and refreshes
        them under a different one. Reading the repository's policy makes "one
        bounds source" a property of the type rather than of the callers — there
        is no second source to disagree, because there is no second argument.

        The direction is deliberate: the repository is the layer that must have
        the numbers (they are compiled into its refresh statement), so it is the
        one that derives them, and this service consumes what it derived.
        """
        self._sessions = sessions
        self._tokens = token_grants
        self._audit = audit
        self._policy: SessionPolicy = sessions.policy

    @property
    def policy(self) -> SessionPolicy:
        """The repository's policy — the same object, exposed so wiring is assertable."""
        return self._policy

    # -- bounds -----------------------------------------------------------
    def bounds_for(self, auth_method: AuthMethod) -> SessionBounds:
        """N-06/N-07 for an ordinary session; N-15 for a break-glass one.

        A break-glass session is short because it is an emergency, not a way of
        working: fifteen minutes idle, sixty absolute, and **no extension beyond
        the absolute bound** whatever the operator is in the middle of.

        Both halves come from the repository's `SessionPolicy`, which is the same
        object the refresh statement was generated from. This method is what
        `begin()` and `rotate()` use to *propose* bounds for a row they are
        creating; a refresh proposes nothing, because the row already names its
        method.
        """
        return self._policy.bounds_for(auth_method)

    # -- creation ---------------------------------------------------------
    def begin(
        self,
        *,
        context: WebAuthorizationContext,
        now: datetime,
        correlation_id: UUID,
        client_ip_hash: bytes | None = None,
        user_agent_digest: bytes | None = None,
        oauth_transaction_id: UUID | None = None,
    ) -> IssuedSession:
        """Create a **new** session and enforce N-66 in the same transaction.

        The eleventh live session for an account revokes the oldest and audits
        the revocation. That bounds both the session table and the population of
        stolen sessions that could be live at once; auditing it is what lets an
        account holder who never used eleven browsers notice.

        **This method cannot produce a rotation** (OD-44 condition 2). It took a
        `rotated_from` argument until the re-review; rotation is now `rotate()`,
        whose predecessor read is locked and whose successor inherits the
        predecessor's account, method and OAuth binding instead of accepting
        them. The separation is the control: "this row is a rotation of that one"
        is the label that carries an OAuth binding past the root-session unique
        index, and a creation path that accepts it as an argument is a creation
        path that can be told to lie.

        **`oauth_transaction_id` is not validated here** (OD-44). A
        `discord_oauth` session that names no transaction, and a break-glass
        session that names one, are both refused by
        `ck_sessions_oauth_transaction_binding` when the row is inserted. A
        Python guard in front of it would be a second copy of the rule that could
        drift from the enforcing one, and it is the database copy that a future
        session-creation path cannot route around.
        """
        self._enforce_session_limit(context.account_id, now=now, correlation_id=correlation_id)

        bounds = self.bounds_for(context.auth_method)
        token = mint_token()
        absolute_expires_at = now + bounds.absolute
        session_id = self._sessions.create(
            account_id=context.account_id,
            auth_method=context.auth_method,
            token_hash=token_hash(token),
            idle_expires_at=now + bounds.idle,
            absolute_expires_at=absolute_expires_at,
            privilege_fingerprint=context.privilege_fingerprint,
            client_ip_hash=client_ip_hash,
            user_agent_digest=user_agent_digest,
            oauth_transaction_id=oauth_transaction_id,
        )
        return IssuedSession(
            session_id=session_id,
            token=token,
            idle_expires_at=min(now + bounds.idle, absolute_expires_at),
            absolute_expires_at=absolute_expires_at,
        )

    def rotate(
        self,
        *,
        record,
        context: WebAuthorizationContext,
        now: datetime,
        reason: str = "rotation",
        client_ip_hash: bytes | None = None,
        user_agent_digest: bytes | None = None,
    ) -> IssuedSession:
        """Replace one live session with its single successor, atomically.

        The whole state transition is one repository call, because it is one
        transition: the predecessor is locked, the successor is inserted from the
        predecessor's own account, authentication method, OAuth binding and
        absolute expiration, and the predecessor is revoked — in the caller's
        transaction, with no window in which two live sessions exist for one
        login.

        **Rotation does not restart the clock** (corrected 2026-08-14). Only the
        *idle* window is proposed here, as `now + bounds.idle`; the successor's
        absolute expiration is the predecessor's, read under the row lock, and
        the idle window is clamped to it by the repository. This method therefore
        computes no absolute expiration and passes none: a chain of privilege
        rotations lives exactly as long as the login at its root, which is what
        N-07 says for an ordinary session and what N-15 says — "no extension
        beyond the absolute bound" — for a break-glass one. The bounds reported
        in the returned `IssuedSession` are the ones the row was given, not the
        ones this method proposed.

        **N-66 is not re-enforced here, and that is not an omission.** A rotation
        replaces a session rather than adding one, so the live population is
        unchanged and the bound cannot be crossed by rotating. Running the limit
        would be actively wrong: if the predecessor were the account's oldest live
        session it would be the row the limit revoked, and the rotation would then
        refuse its own predecessor.

        Raises `SessionRotationRefused` when the predecessor is not a live —
        unrevoked and within **both** its idle and absolute bounds — unrotated
        session of this account and authentication method.
        """
        bounds = self.bounds_for(context.auth_method)
        token = mint_token()
        rotated = self._sessions.rotate(
            predecessor_id=record.id,
            expected_account_id=context.account_id,
            expected_auth_method=context.auth_method,
            token_hash=token_hash(token),
            idle_expires_at=now + bounds.idle,
            privilege_fingerprint=context.privilege_fingerprint,
            now=now,
            revocation_reason=reason,
            client_ip_hash=client_ip_hash,
            user_agent_digest=user_agent_digest,
        )
        if rotated is None:
            raise SessionRotationRefused(
                "the session being rotated is not live, unrotated and this "
                "account's under this authentication method"
            )
        return IssuedSession(
            session_id=rotated.id,
            token=token,
            idle_expires_at=rotated.idle_expires_at,
            absolute_expires_at=rotated.absolute_expires_at,
        )

    def _enforce_session_limit(
        self, account_id: UUID, *, now: datetime, correlation_id: UUID
    ) -> None:
        live = self._sessions.live_sessions(account_id, now=now)
        maximum = self._policy.max_sessions_per_account
        while len(live) >= maximum:
            oldest = live.pop(0)
            self._sessions.revoke(oldest.id, reason="session_limit", at=now)
            self._audit.record(
                AuditEvent(
                    action="auth.session.revoked",
                    entity_type="session",
                    entity_id=str(oldest.id),
                    source=AuditSource.WEB,
                    actor_capability=ActorCapability.SYSTEM,
                    correlation_id=correlation_id,
                    payload={"reason": "session_limit", "limit": maximum},
                )
            )

    # -- resolution and rotation -----------------------------------------
    def resolve(self, token: str, *, now: datetime):
        return self._sessions.resolve(token_hash(token), now=now)

    def touch(self, record, *, now: datetime) -> RefreshedSession:
        """Refresh one live session's idle window under **its own** idle policy.

        **This method chooses no duration** (corrected 2026-08-15, second
        session-lifetime review). The first correction had it select the window
        with `bounds_for(record.auth_method)` and pass `idle` and
        `expected_auth_method` to the repository, which verified the method. That
        made *this* path correct while leaving the repository API able to pair a
        break-glass row's true method with N-06's sixty minutes — a matching
        method beside a false duration, which the equality predicate could not
        see. The repository now selects the window from the method persisted on
        the row, out of the policy it was constructed with, so there is no
        duration to pass and no way for this method or any other caller to
        propose one.

        The `record` is still the parameter rather than a bare id, and
        deliberately: it is the caller's evidence that it resolved a session
        before continuing it, and taking an id back would invite a caller to
        refresh a session it never resolved. Its `auth_method` is **not** sent to
        the repository — the row's own column is the authority, and a second copy
        travelling as an argument is the thing that could disagree with it.

        Only the *idle* window moves, and only to `LEAST(now + idle,
        absolute_expires_at)`. Repeated refreshes never pass, or change, the
        absolute bound the login set.

        Raises `SessionTouchRefused` when the conditional write matches no row —
        the session is unknown, revoked, or past either bound. Nothing is written
        in that case, and the caller must **end the session, clear the cookie and
        not retry as authenticated**.
        """
        refreshed = self._sessions.touch(record.id, now=now)
        if refreshed is None:
            raise SessionTouchRefused(
                "the session being refreshed is not live: it is unknown, "
                "revoked, or past its idle or absolute bound"
            )
        return RefreshedSession(
            session_id=refreshed.id,
            idle_expires_at=refreshed.idle_expires_at,
            absolute_expires_at=refreshed.absolute_expires_at,
        )

    def rotate_if_privileges_changed(
        self,
        *,
        record,
        context: WebAuthorizationContext,
        now: datetime,
        correlation_id: UUID,
        client_ip_hash: bytes | None = None,
        user_agent_digest: bytes | None = None,
    ) -> IssuedSession | None:
        """N-08. Returns a new session when the fingerprint moved, else `None`.

        The comparison is against a fingerprint computed from a **fresh**
        resolution. Reading the capability set back from the session row would
        make the check compare a value to itself, which is how a privilege change
        goes undetected.

        **The OAuth binding is carried forward, not re-established** (OD-44). A
        rotated session is the same login: it descends from the transaction the
        completion claimed, and no second claim is made or possible. The unique
        index that refuses a second *completion* is scoped to non-rotated rows
        precisely so this chain can exist — and OD-44 condition 2 is what makes
        that scoping safe, by refusing any chain that branches or crosses.

        The binding is not passed *in* any more: `rotate()` reads it from the
        locked predecessor row. A caller that resolved a stale `record` therefore
        cannot bind the successor to a transaction the predecessor does not name,
        and `SessionRotationRefused` reaches the caller instead.
        """
        if record.privilege_fingerprint == context.privilege_fingerprint:
            return None
        issued = self.rotate(
            record=record,
            context=context,
            now=now,
            reason="privilege_change",
            client_ip_hash=client_ip_hash,
            user_agent_digest=user_agent_digest,
        )
        self._audit.record(
            AuditEvent(
                action="auth.session.rotated",
                entity_type="session",
                entity_id=str(issued.session_id),
                source=AuditSource.WEB,
                actor_capability=ActorCapability.SYSTEM,
                correlation_id=correlation_id,
                actor_platform_account_id=context.account_id,
                payload={
                    "reason": "privilege_change",
                    "previous_session_id": str(record.id),
                },
            )
        )
        return issued

    # -- termination ------------------------------------------------------
    def logout(
        self, *, record, account_id: UUID, now: datetime, correlation_id: UUID
    ) -> None:
        """Revoke, delete the stored provider tokens (N-11), audit — one transaction.

        The audit event shares the transaction deliberately: an unrecorded
        revocation is exactly the record an incident investigation needs, so a
        logout that cannot be recorded fails and the user is told to retry.
        """
        self._sessions.revoke(record.id, reason="logout", at=now)
        self._tokens.delete_for_account(account_id)
        self._audit.record(
            AuditEvent(
                action="auth.logout",
                entity_type="session",
                entity_id=str(record.id),
                source=AuditSource.WEB,
                actor_capability=ActorCapability.GUILD_MEMBER,
                correlation_id=correlation_id,
                actor_platform_account_id=account_id,
                payload={"auth_method": record.auth_method.value},
            )
        )

    def revoke_every_session(
        self, *, account_id: UUID, now: datetime, correlation_id: UUID, operator: str
    ) -> int:
        """C-07, after a suspected compromise. Also deletes the provider tokens."""
        revoked = self._sessions.revoke_all_for_account(
            account_id, reason="operator", at=now
        )
        self._tokens.delete_for_account(account_id)
        self._audit.record(
            AuditEvent(
                action="auth.session.revoked_all",
                entity_type="platform_account",
                entity_id=str(account_id),
                source=AuditSource.SYSTEM,
                actor_capability=ActorCapability.SYSTEM,
                correlation_id=correlation_id,
                payload={"revoked": revoked, "operator": operator},
            )
        )
        return revoked


__all__ = [
    "IssuedSession",
    "RefreshedSession",
    "SessionBounds",
    "SessionPolicy",
    "SessionRotationRefused",
    "SessionService",
    "SessionTouchRefused",
]
