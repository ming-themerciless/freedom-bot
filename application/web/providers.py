"""The identity-provider boundary of ADR 0010 D6.

A provider adapter is responsible for exactly one thing: turning a completed
authentication into a verified `(provider_key, subject)` plus, where the provider
supplies it, a membership and role projection.

**`VerifiedIdentity` carries no capability**, and that is the point. Capability is
resolved by the platform from role-capability mappings (ADR 0004, ADR 0010 D6). A
provider that claimed a capability would be believed by nothing here, because
there is no field for it to claim one in.

Session integrity, authorization, CSRF, origin and host validation, request and
concurrency bounds, rate limiting, audit and safe failure are
**provider-independent core controls**. Replacing Discord replaces what is behind
this protocol and nothing else (delivery plan §9.10).

Phase 3 delivers the boundary, not a second provider (ADR 0010 D7). Adding one
requires its own accepted provider, privacy, account-linking and migration
package; this interface makes that bounded, it does not pre-approve it.

## Every result carries the provider that produced it

`ProviderTokens` and `VerifiedIdentity` each name their `provider_key`, and
`VerifiedCompletion` refuses to exist unless the two agree. The reason is a
concrete finding rather than tidiness: the completion claim binds a login to the
provider recorded on the transaction it is completing, and it can only do that if
the value it binds to is a **property of the verified result** rather than
something the route remembered about which adapter it called. A caller holding one
provider's tokens and another provider's identity holds two halves that never came
from one authentication, and there is deliberately no type that can carry them
both.

The `provider_key` is stamped by the adapter that made the network call, from its
own constant. It is not read from a provider response, because a value the
provider supplies is a value the provider could change — that would be exactly the
unverifiable claim this boundary must not invent.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


class ProviderResultMismatch(Exception):
    """Two provider results that cannot have come from one authentication.

    Raised at construction rather than checked at use, so there is no moment at
    which a mismatched pair exists as a value something could be trusted with. It
    is a defect signal — a route calls one adapter twice and cannot produce one —
    and it therefore reaches the safe-error boundary rather than being handled as
    an expected refusal.
    """


class ProviderUnavailable(Exception):
    """The provider could not be reached, or answered in a way we cannot use.

    Distinct from "the provider said no", and the distinction is load-bearing:
    an outage must never be written into the membership projection as an absence
    (TC-OUT-04). "Refresh failed" and "membership absent" are different facts,
    and a rate-limit storm that recorded the first as the second would revoke a
    guild.
    """


class ProviderRefused(Exception):
    """The provider rejected the exchange — a bad code, a revoked grant.

    Carries no provider text: the browser sees a code and a correlation id, and
    the provider's message goes nowhere (N-25).
    """


@dataclass(frozen=True, slots=True)
class ProviderTokens:
    """Tokens, and the provider they were issued by.

    `provider_key` is stamped by the adapter that performed the exchange, from
    its own constant. It exists so that a token result is self-describing: the
    completion claim binds to the provider recorded on the transaction, and a
    token result that could not say where it came from would leave that binding
    resting on the caller's memory of which adapter it used.
    """

    provider_key: str
    access_token: str
    refresh_token: str | None
    expires_at: datetime
    scopes: str


@dataclass(frozen=True, slots=True)
class ProviderMembership:
    """What the provider says about this person's membership, right now.

    `role_ids` are **stable snowflakes**. Role *names* are presentation and never
    reach a capability decision (OD-18); there is deliberately no field for them.
    """

    guild_id: int
    is_member: bool
    role_ids: frozenset[int]
    observed_at: datetime


@dataclass(frozen=True, slots=True)
class VerifiedIdentity:
    """One completed authentication. No capability, by construction."""

    provider_key: str
    #: The provider's immutable subject. For Discord, the snowflake as a
    #: canonical decimal string.
    subject: str
    #: Display data only, bounded at the view-model boundary. It is stored so an
    #: operator has something to read and is **never** compared: no name, username
    #: or email establishes identity equivalence (ADR 0010 D3).
    username: str
    global_name: str | None
    membership: ProviderMembership | None


@dataclass(frozen=True, slots=True)
class VerifiedCompletion:
    """One provider's tokens and the identity they resolved to, indivisibly.

    This is the **only** input `OAuthLoginService.complete()` accepts for the
    provider half of a login, and constructing one is the point at which the two
    halves are required to agree. A caller that holds Discord tokens and another
    provider's verified identity cannot build this object, so it cannot reach a
    completion with them — which is the difference between a rule and a comment.

    `provider_key` is therefore a *derived* value, not a fourth thing a caller
    supplies: it is the one key both halves already carry.
    """

    identity: VerifiedIdentity
    tokens: ProviderTokens

    def __post_init__(self) -> None:
        if self.identity.provider_key != self.tokens.provider_key:
            # Neither key is quoted: they are configuration-derived adapter
            # constants rather than secrets, but the message is read in logs and
            # a refusal does not need to name them to be actionable.
            raise ProviderResultMismatch(
                "a verified identity and a token result from different providers "
                "cannot form one completion"
            )

    @property
    def provider_key(self) -> str:
        """The provider both halves name. The completion claim binds to this."""
        return self.identity.provider_key


class IdentityProvider(Protocol):
    """What P3.1 implements once and a later approved provider implements again.

    An implementation owes two things beyond answering: it stamps its own
    `provider_key` on every `ProviderTokens` it returns, and it refuses a
    `verify()` call carrying another provider's tokens. The first makes the token
    result self-describing; the second means no adapter can be used as a
    laundering step that turns one provider's tokens into another's identity.
    """

    provider_key: str

    def authorization_url(self, *, state: str, code_challenge: str) -> str:
        """The URL to redirect a browser to. Built server-side, from configuration."""

    async def exchange(self, *, code: str, code_verifier: str) -> ProviderTokens:
        """Trade the authorization code for tokens, presenting the PKCE verifier.

        The returned `ProviderTokens.provider_key` **must** be this adapter's own
        `provider_key`, taken from its constant and never from the response body.
        """

    async def verify(self, tokens: ProviderTokens) -> VerifiedIdentity:
        """Resolve the subject and the current membership projection.

        Must refuse tokens whose `provider_key` is not this adapter's, and must
        return an identity carrying this adapter's `provider_key`.
        """

    async def probe(self) -> bool:
        """Is the provider reachable and answering? One bounded, read-only call.

        Added 2026-08-24 for finding S-4/S5. `/healthz` reported
        `identity_provider: true` as a **literal** — the check that exists to
        tell an operator whether Discord is up said "up" throughout the outage
        the same session had deliberately created, which is worse than reporting
        nothing at all.

        The contract an implementation owes:

        * **bounded** — its own short timeout, tighter than the request timeout,
          so a hanging provider cannot hang the health endpoint;
        * **side-effect free** — no token, no credential, no state change, and
          no scope beyond what an anonymous caller has;
        * **total** — it answers `True` or `False` and raises nothing, because a
          probe that raised would turn a degraded dependency into a `500` from
          the endpoint an operator reaches for during a degradation; and
        * **silent** — the answer is a boolean. No status code, no body, no URL
          and no exception text reaches the caller, because VM-16 carries check
          names and booleans and has never carried anything else.
        """


__all__ = [
    "IdentityProvider",
    "ProviderMembership",
    "ProviderRefused",
    "ProviderResultMismatch",
    "ProviderTokens",
    "ProviderUnavailable",
    "VerifiedCompletion",
    "VerifiedIdentity",
]
