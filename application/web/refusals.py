"""The one place a terminal OAuth callback refusal becomes an audit row.

TC-AUTH-11 requires that a login **and** a login refusal each write *exactly one*
append-only audit event, carrying the correlation id the caller was shown and no
secret. Before this module the rule held only for the two branches that raised
`AuthenticationFailure`; five other terminal exits of R-04 returned a redirect and
wrote nothing, and the green suite did not notice because the provider-outage test
asserted only the redirect and the absence of a session.

The fix is a boundary rather than five more call sites. `OAuthRefusalRecorder` is
constructed once per callback attempt and records **at most one** event for that
attempt, whichever branch reaches it. "At most one" is a property of the object,
not a rule a future editor has to remember: `record` is a no-op after the first
write, so a branch that both raises and passes through the recorder still produces
one row.

## What may appear in a refusal payload

Only two things: a reason drawn from `LoginRefusalReason` below, and — when a
*validated* identifier exists — the id of the OAuth transaction it concerns.

Never the authorization code, the `state`, the PKCE verifier, a provider token,
the raw cookie value, the raw provider response, the client address, exception
text, or any credential material. A malformed transaction cookie is attacker
input and is recorded as the **category** `unbound`, never echoed: an audit reader
learns that a callback arrived without a usable transaction reference, which is
the fact, and the attacker's bytes stay out of the record.

## Why a rate-limited callback is one event and not two

N-18's refusal is a terminal outcome of an authentication attempt, so it is
audited as `auth.login.refused` with reason `rate_limited` — an
authentication-attempt audit, not a separate rate-limit audit and not both.
TC-AUTH-11 says *exactly one* event per attempt, and two events for one refused
callback would break it in the direction that is hardest to notice: a reviewer
counting refusals would double every throttled attempt.

## Why the write is its own transaction

A refused login rolls its work transaction back — that is what "no session was
created" means — so an audit row written inside it would be discarded exactly when
the refusal happened. The recorder therefore opens its own transaction, after the
work transaction is over, and the correlation id carries across.

## Why a failed refusal audit is not swallowed

If the audit write fails, the exception propagates to the safe-error handler and
the caller sees `VM-20` with a correlation id. **No session exists on any of these
paths**, so a failed refusal audit cannot convert a refusal into a successful
login — it converts a refusal into a safe error, which is the same fail-closed
direction SM-01 requires of the success path's audit. It is deliberately not
wrapped in a blanket `except`: a genuine programmer defect here must stay visible.
"""
from __future__ import annotations

from enum import Enum
from uuid import UUID

from application.audit import ActorCapability, AuditEvent, AuditSource
from application.web.errors import AuthenticationFailure

#: The audit action every terminal login refusal writes. One action, so a
#: reviewer counting refusals counts one thing.
LOGIN_REFUSED_ACTION = "auth.login.refused"

#: The entity category used when no validated transaction identifier exists. A
#: stable, non-sensitive word — never the caller's bytes.
UNBOUND_ENTITY_TYPE = "oauth_callback"
UNBOUND_ENTITY_ID = "unbound"

TRANSACTION_ENTITY_TYPE = "oauth_transaction"


class LoginRefusalReason(Enum):
    """The closed, non-secret vocabulary of terminal OAuth callback refusals.

    Deliberately finer than the code the browser is shown. `provider_unavailable`
    and `provider_refused` are one sentence to a user (`provider_error`) and two
    different sentences to an operator deciding whether Discord is down or a
    grant was revoked.
    """

    #: N-18's callback budget was spent for this source address.
    RATE_LIMITED = "rate_limited"
    #: No transaction cookie, no `state`, or no `code` on the callback.
    CALLBACK_PARAMETERS_MISSING = "callback_parameters_missing"
    #: A transaction cookie that is not a UUID. The value itself is never recorded.
    TRANSACTION_COOKIE_MALFORMED = "transaction_cookie_malformed"
    #: The consumption statement matched zero rows: unknown, expired, already
    #: consumed, or a `state` that does not match the row.
    TRANSACTION_NOT_LIVE_OR_STATE_MISMATCH = "transaction_not_live_or_state_mismatch"
    #: The stored ciphertext did not authenticate under this row's AAD binding.
    VERIFIER_BINDING_FAILED = "verifier_binding_failed"
    #: OD-44. The completion claim matched zero rows: the transaction is unknown,
    #: was never consumed, or has already produced its one completion. Recorded
    #: only through `record_failure`, because `OAuthLoginService.complete()`
    #: describes it — the service is the only layer that knows which row refused.
    COMPLETION_NOT_CLAIMABLE = "completion_not_claimable"
    #: Transport failure, timeout, 429 or 5xx from the provider.
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    #: The provider answered definitely and negatively, or unusably: a 4xx on the
    #: exchange, no access token, or a payload this adapter cannot read.
    PROVIDER_REFUSED = "provider_refused"
    #: The person authenticated and is not in the guild (ADR 0004's rejection).
    NOT_A_GUILD_MEMBER = "not_a_guild_member"


#: Every reason a route branch records directly. The two omissions are the ones a
#: service raises as `AuthenticationFailure` with its own described audit, which
#: `record_failure` writes instead — recording them twice is exactly the
#: double-audit TC-AUTH-11 forbids.
ROUTE_RECORDED_REASONS = frozenset(
    {
        LoginRefusalReason.RATE_LIMITED,
        LoginRefusalReason.CALLBACK_PARAMETERS_MISSING,
        LoginRefusalReason.TRANSACTION_COOKIE_MALFORMED,
        LoginRefusalReason.PROVIDER_UNAVAILABLE,
        LoginRefusalReason.PROVIDER_REFUSED,
    }
)


class OAuthRefusalRecorder:
    """One callback attempt's refusal record. Constructed per request.

    Holds the engine rather than a connection: every write it makes is its own
    transaction, because the transaction it is recording the failure of has
    already rolled back.
    """

    __slots__ = ("_engine", "_correlation_id", "_recorded")

    def __init__(self, engine, *, correlation_id: UUID) -> None:
        self._engine = engine
        self._correlation_id = correlation_id
        self._recorded = False

    @property
    def correlation_id(self) -> UUID:
        return self._correlation_id

    @property
    def recorded(self) -> bool:
        """Whether this attempt has already written its one refusal event."""
        return self._recorded

    def record(
        self,
        reason: LoginRefusalReason,
        *,
        transaction_id: UUID | None = None,
    ) -> None:
        """Write this attempt's refusal event, once.

        `transaction_id` is included only when the caller holds a **validated**
        identifier — a value that parsed as a UUID. It is a bounded, non-secret
        128-bit reference to a row, not a credential and not attacker text. When
        there is none, the event names the stable `oauth_callback`/`unbound`
        category instead.
        """
        if self._recorded:
            return
        if transaction_id is None:
            entity_type, entity_id = UNBOUND_ENTITY_TYPE, UNBOUND_ENTITY_ID
        else:
            entity_type, entity_id = TRANSACTION_ENTITY_TYPE, str(transaction_id)
        self._write(
            AuditEvent(
                action=LOGIN_REFUSED_ACTION,
                entity_type=entity_type,
                entity_id=entity_id,
                source=AuditSource.WEB,
                actor_capability=ActorCapability.SYSTEM,
                correlation_id=self._correlation_id,
                payload={"reason": reason.value},
            )
        )
        self._recorded = True

    def record_failure(self, failure: AuthenticationFailure) -> None:
        """Write the event a service already described, once.

        The service builds the `FailureAudit` because it is the only layer that
        knows *which* row failed; the recorder commits it because it is the only
        layer that knows the service's transaction is over. A failure carrying no
        described audit still marks the attempt recorded — a service that
        deliberately describes no event is not a hole for a second one to fill.
        """
        if self._recorded:
            return
        self._recorded = True
        described = failure.audit
        if described is None:
            return
        self._write(
            AuditEvent(
                action=described.action,
                entity_type=described.entity_type,
                entity_id=described.entity_id,
                source=AuditSource.WEB,
                actor_capability=described.capability,
                correlation_id=failure.correlation_id,
                actor_platform_account_id=described.account_id,
                payload=described.payload,
            )
        )

    def _write(self, event: AuditEvent) -> None:
        from adapters.web.repositories import WebAuditRepository

        with self._engine.begin() as connection:
            WebAuditRepository(connection).record(event)


__all__ = [
    "LOGIN_REFUSED_ACTION",
    "LoginRefusalReason",
    "OAuthRefusalRecorder",
    "ROUTE_RECORDED_REASONS",
    "TRANSACTION_ENTITY_TYPE",
    "UNBOUND_ENTITY_ID",
    "UNBOUND_ENTITY_TYPE",
]
