"""The OAuth login flow, in the three pieces a request actually has (SM-01).

Deliberately **not** one method. The flow has a synchronous database half and an
asynchronous provider half, and interleaving them would either hold a database
transaction open across a network call to Discord or block the event loop on
PostgreSQL. Both are forbidden by `.agents/AGENTS.md`, so the seam is explicit:

    start()              -- database, synchronous: rate limit, mint, store
    provider.exchange()  -- network, asynchronous: the route awaits it
    provider.verify()    -- network, asynchronous
    complete()           -- database, synchronous: account, session, audit

`consume()` sits before the provider calls and is the single statement that makes
"exactly once" a database property for the *authorization request* (schema
§9.2.1). It cannot also cover the *completion*, because the completion happens on
the far side of the provider round trip — so OD-44 gives the flow a second
durable step, claimed inside `complete()`'s transaction:

    UPDATE oauth_transactions SET completion_claimed_at = now()
     WHERE id = :id AND consumed_at IS NOT NULL AND completion_claimed_at IS NULL
       AND provider_key = :provider_key

Zero rows is a refusal. The fourth predicate is the OD-44 re-review's first
finding: without it the claim proved only that *a* consumed transaction was being
completed, while the provider identity came from whatever `VerifiedIdentity` the
caller happened to hold — so a consumed Discord transaction could be spent by
another provider's verified result. The expected key now travels with the verified
result itself, as `VerifiedCompletion.provider_key`, and is compared against the
row inside the claiming statement.

The session that transaction produces carries its id in
`sessions.oauth_transaction_id`, which is required for `discord_oauth` by a check
constraint and unique among the sessions a completion creates. SM-01's forbidden
state — a session with no consumed transaction behind it — is therefore refused
by the database rather than made unlikely by the order of the statements in the
route.

## The return target

Only a **path**, and only one from the server-side allowlist below. No absolute
URL, no scheme, no host, and no protocol-relative `//host` value ever reaches a
`Location` header — the check constraint on the column refuses to store one, the
allowlist refuses to accept one, and the value is re-validated at use because a
row written by an earlier version of this code is still a row.

## Why the start is a `GET`

The accepted CSP contains `form-action 'self'`, which browsers enforce across the
redirect chain a form submission produces. A `POST` start answering `303` to
`https://discord.com/…` would be blocked by the policy the project already
accepted. A `GET` navigation is not a form submission, so `form-action` never
applies and N-26 stands unweakened.

The usual objection is login CSRF, and it does not apply: the callback accepts a
`state` only when it matches the `__Host-fb_login_txn` cookie **in the browser
that started the flow**. An attacker who initiates a flow gets the transaction
cookie in their own browser and cannot install it in the victim's. Forcing a
victim's browser to hit the start therefore begins a flow the victim completes as
themselves — a wasted rate-limit slot, not a session confusion (RR-02).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from application.audit import ActorCapability, AuditEvent, AuditSource
from application.web.capabilities import (
    AuthMethod,
    MembershipProjection,
    resolve_capabilities,
)
from application.web.config import WebSettings
from application.web.crypto import (
    DecryptionError,
    Envelope,
    mint_token,
    pkce_pair,
    token_hash,
    transaction_aad,
)
from application.web.errors import AuthenticationFailure, FailureAudit
from application.web.providers import VerifiedCompletion
from application.web.sessions import IssuedSession, SessionService

#: The server-side return-target allowlist. A path that does not match one of
#: these is replaced by the default; it is never rejected with an error, because
#: an attacker learning *which* paths are valid is a small disclosure and a user
#: losing their place is a real annoyance.
RETURN_PATH_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^/v1/characters$"),
    re.compile(
        r"^/v1/characters/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}"
        r"-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    ),
    re.compile(r"^/v1/council(/[A-Za-z0-9._~\-/]*)?$"),
    re.compile(r"^/v1/admin(/[A-Za-z0-9._~\-/]*)?$"),
    re.compile(r"^/v1/account(/[A-Za-z0-9._~\-/]*)?$"),
    re.compile(r"^/v1/audit(/[A-Za-z0-9._~\-/]*)?$"),
)

DEFAULT_RETURN_PATH = "/v1/characters"


def safe_return_path(candidate: str | None) -> str:
    """The allowlist, applied identically when storing and when redirecting.

    A protocol-relative `//evil.example` is a *path* as far as a naive check is
    concerned and a *host* as far as a browser is concerned. That gap is why the
    rule is an allowlist of shapes rather than a list of forbidden prefixes, and
    why the column carries its own `NOT LIKE '//%'` check as well.
    """
    if not candidate or not candidate.startswith("/") or candidate.startswith("//"):
        return DEFAULT_RETURN_PATH
    if "\\" in candidate or "\n" in candidate or "\r" in candidate:
        return DEFAULT_RETURN_PATH
    for pattern in RETURN_PATH_PATTERNS:
        if pattern.match(candidate):
            return candidate
    return DEFAULT_RETURN_PATH


@dataclass(frozen=True, slots=True)
class StartedLogin:
    transaction_id: UUID
    authorization_url: str
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class RecoveredTransaction:
    code_verifier: str
    return_path: str
    provider_key: str


@dataclass(frozen=True, slots=True)
class CompletedLogin:
    session: IssuedSession
    account_id: UUID
    return_path: str


class OAuthLoginService:
    """Owns `oauth_transactions` and the session a successful callback creates."""

    __slots__ = (
        "_transactions",
        "_accounts",
        "_tokens",
        "_mappings",
        "_membership",
        "_sessions",
        "_audit",
        "_envelope",
        "_settings",
    )

    def __init__(
        self,
        *,
        transactions,
        accounts,
        token_grants,
        role_mappings,
        membership,
        session_service: SessionService,
        audit,
        envelope: Envelope,
        settings: WebSettings,
    ) -> None:
        self._transactions = transactions
        self._accounts = accounts
        self._tokens = token_grants
        self._mappings = role_mappings
        self._membership = membership
        self._sessions = session_service
        self._audit = audit
        self._envelope = envelope
        self._settings = settings

    # -- 1. start ---------------------------------------------------------
    def start(
        self,
        *,
        provider,
        return_path: str | None,
        now: datetime,
        client_ip_hash: bytes | None,
    ) -> tuple[StartedLogin, str]:
        """Mint the transaction and return the redirect plus the cookie value.

        The `state` is stored **hashed**: it is only ever compared, so a
        plaintext copy would be a stealable value with no use for it. The PKCE
        verifier is stored **encrypted**, because it has to be presented to the
        provider at the exchange and a hash cannot be.
        """
        state = mint_token()
        verifier, challenge = pkce_pair()
        expires_at = now + timedelta(
            minutes=self._settings.session.oauth_transaction_minutes
        )
        transaction_id = uuid4()
        sealed = self._envelope.seal(
            verifier.encode("ascii"),
            aad=transaction_aad(
                transaction_id,
                self._settings.encryption.active_version,
                provider.provider_key,
            ),
        )
        # The id is generated here rather than by the repository because it is
        # part of the AAD: the ciphertext is bound to the row before the row
        # exists, so a ciphertext moved to another row cannot authenticate.
        stored_id = self._transactions.create(
            state_hash=token_hash(state),
            verifier=sealed,
            return_path=safe_return_path(return_path),
            provider_key=provider.provider_key,
            expires_at=expires_at,
            client_ip_hash=client_ip_hash,
            transaction_id=transaction_id,
        )
        return (
            StartedLogin(
                transaction_id=stored_id,
                authorization_url=provider.authorization_url(
                    state=state, code_challenge=challenge
                ),
                expires_at=expires_at,
            ),
            state,
        )

    # -- 2. consume -------------------------------------------------------
    def consume(
        self,
        *,
        transaction_id: UUID,
        state: str,
        now: datetime,
        correlation_id: UUID,
    ) -> RecoveredTransaction:
        """The one place a verifier is ever recovered, and it is also its erasure.

        A mismatched state, an expired transaction, a replay and a concurrent
        second callback all arrive here as *zero rows*, so they are one branch
        rather than four — which is what makes it hard to get one of them wrong.
        """
        consumed = self._transactions.consume(
            transaction_id=transaction_id, state_hash=token_hash(state), now=now
        )
        if consumed is None:
            raise AuthenticationFailure(
                code="transaction_unknown",
                correlation_id=correlation_id,
                audit=FailureAudit(
                    action="auth.login.refused",
                    entity_type="oauth_transaction",
                    entity_id=str(transaction_id),
                    capability=ActorCapability.SYSTEM,
                    payload={"reason": "transaction_not_live_or_state_mismatch"},
                ),
            )
        try:
            verifier = self._envelope.open(
                consumed.verifier,
                aad=transaction_aad(
                    transaction_id,
                    consumed.verifier.key_version,
                    consumed.provider_key,
                ),
            )
        except DecryptionError as error:
            # A ciphertext that does not authenticate under this row's binding is
            # a moved ciphertext or a tampered one. It raises rather than
            # returning a value that would complete somebody else's exchange.
            raise AuthenticationFailure(
                code="state_mismatch",
                correlation_id=correlation_id,
                audit=FailureAudit(
                    action="auth.login.refused",
                    entity_type="oauth_transaction",
                    entity_id=str(transaction_id),
                    capability=ActorCapability.SYSTEM,
                    payload={"reason": "verifier_binding_failed"},
                ),
            ) from error
        return RecoveredTransaction(
            code_verifier=verifier.decode("ascii"),
            return_path=safe_return_path(consumed.return_path),
            provider_key=consumed.provider_key,
        )

    # -- 3. complete ------------------------------------------------------
    def complete(
        self,
        *,
        transaction_id: UUID,
        completion: VerifiedCompletion,
        return_path: str,
        now: datetime,
        correlation_id: UUID,
        client_ip_hash: bytes | None,
        user_agent_digest: bytes | None,
    ) -> CompletedLogin:
        """Claim the completion, resolve the account, create the session — one transaction.

        **The claim is first, and it is the enforcement** (OD-44). `consume()`
        proved a live browser-bound transaction existed before Discord was
        contacted; the claim proves, from durable state and after Discord
        answered, that this is the only completion that transaction will ever
        have. A caller reaching here with an unknown, unconsumed, already-claimed
        or simply mismatched id matches zero rows and is refused — which is why
        route ordering is no longer what stands between an internal call and a
        session.

        **The claim also binds the provider.** The expected provider key is read
        from `completion`, which is one indivisible verified result: its identity
        and its tokens were required to name the same provider when it was
        constructed, and each of them got that name stamped by the adapter that
        made the network call. So the key passed to the claim is a property of
        *what was verified*, not of which route ran — and a caller holding another
        provider's verified identity and tokens cannot spend a transaction that
        was started for this one. It matches zero rows and is refused exactly like
        an unknown id: same typed failure, same audit, same rollback, and no
        account, identity, membership projection, token grant, session or success
        audit.

        Everything after the claim shares its transaction: the account and
        identity, the membership projection, the encrypted token grant, the
        session carrying `oauth_transaction_id`, the claim itself and the success
        audit commit together or not at all. There is no provider I/O anywhere
        inside it — the exchange and the verification are already over.

        **A non-member receives no session.** ADR 0004 requires the callback to
        reject before a session is created, and this is where that happens: the
        refusal is raised before any account, identity, membership or token row
        is written, the transaction is already consumed so it cannot be replayed,
        and the caller renders VM-02 with `403`. The claim this method took rolls
        back with the refusal, leaving the row consumed-and-unclaimed — the same
        terminal state as process death, and equally unreplayable.

        An earlier revision of this docstring said the membership projection was
        recorded for a non-member anyway. It is not, and it could not be: the
        refusal raises before `record()` and rolls the transaction back in any
        case. TC-AUTH-08 asserts the absence.
        """
        identity = completion.identity
        tokens = completion.tokens
        if not self._transactions.claim_completion(
            transaction_id=transaction_id,
            # Derived from the verified result, never from the route's knowledge
            # of which adapter it called.
            provider_key=completion.provider_key,
            now=now,
        ):
            # Zero rows is a refusal, not a warning. Unknown, unconsumed,
            # already-claimed and another provider's are one branch here because
            # they are one fact: this completion has no live claim behind it, and
            # therefore gets no session, no token grant and no success audit. The
            # branches are also deliberately indistinguishable to the caller — a
            # refusal that said *which* predicate failed would tell a prober
            # whether a transaction id exists and which provider it belongs to.
            raise AuthenticationFailure(
                code="transaction_unknown",
                correlation_id=correlation_id,
                audit=FailureAudit(
                    action="auth.login.refused",
                    entity_type="oauth_transaction",
                    entity_id=str(transaction_id),
                    capability=ActorCapability.SYSTEM,
                    payload={"reason": "completion_not_claimable"},
                ),
            )

        membership = identity.membership
        if membership is None or not membership.is_member:
            # The refusal is **described**, not written: this transaction is
            # about to roll back, and an audit row written inside it would be
            # discarded exactly when the refusal happened. The route commits it
            # afterwards through `record_authentication_failure`.
            raise AuthenticationFailure(
                code="not_a_member",
                correlation_id=correlation_id,
                audit=FailureAudit(
                    action="auth.login.refused",
                    entity_type="external_identity",
                    entity_id=f"{identity.provider_key}:{identity.subject}",
                    capability=ActorCapability.SYSTEM,
                    payload={"reason": "not_a_guild_member"},
                ),
            )

        account = self._accounts.find_by_identity(
            identity.provider_key, identity.subject
        )
        if account is None:
            account = self._accounts.create_with_identity(
                provider_key=identity.provider_key,
                subject=identity.subject,
                correlation_id=correlation_id,
                display_label=identity.username[:80] or None,
            )
        identity_id = self._accounts.identity_id(
            identity.provider_key, identity.subject
        )
        self._accounts.note_authentication(identity_id, at=now)

        projection = self._membership.record(
            discord_user_id=int(identity.subject),
            username=identity.username or "unknown",
            global_name=identity.global_name,
            guild_id=membership.guild_id,
            is_member=True,
            role_ids=membership.role_ids,
            observed_at=membership.observed_at,
        )
        self._store_tokens(identity_id=identity_id, tokens=tokens)

        context = resolve_capabilities(
            account_id=account.id,
            auth_method=AuthMethod.DISCORD_OAUTH,
            membership=projection,
            mappings=self._mappings.active_mappings(membership.guild_id),
        )
        issued = self._sessions.begin(
            context=context,
            now=now,
            correlation_id=correlation_id,
            client_ip_hash=client_ip_hash,
            user_agent_digest=user_agent_digest,
            # The exact id that was claimed a few statements ago, in this same
            # transaction. Passing anything else would be refused by the unique
            # index; passing nothing would be refused by the check constraint.
            oauth_transaction_id=transaction_id,
        )
        # Same transaction as the session insert. A login that cannot be recorded
        # does not happen (SM-01's audit-failure rule).
        self._audit.record(
            AuditEvent(
                action="auth.login.succeeded",
                entity_type="session",
                entity_id=str(issued.session_id),
                source=AuditSource.WEB,
                actor_capability=ActorCapability.GUILD_MEMBER,
                correlation_id=correlation_id,
                actor_platform_account_id=account.id,
                payload={
                    "provider_key": identity.provider_key,
                    "auth_method": AuthMethod.DISCORD_OAUTH.value,
                    # Capabilities, not tokens: the code, the tokens, the state
                    # and the verifier appear in no audit payload, ever.
                    "capabilities": sorted(c.value for c in context.capabilities),
                },
            )
        )
        return CompletedLogin(
            session=issued, account_id=account.id, return_path=return_path
        )

    def _store_tokens(self, *, identity_id: UUID, tokens) -> None:
        """Encrypted, AAD-bound to the identity, and deleted on logout (N-11).

        Stored at all only because membership and role verification needs
        `guilds.members.read` on the member's own token for as long as the
        session lives — and no longer.
        """
        grant_id = uuid4()
        version = self._settings.encryption.active_version
        from application.web.crypto import token_grant_aad

        aad = token_grant_aad(grant_id, identity_id, version)
        access = self._envelope.seal(tokens.access_token.encode("utf-8"), aad=aad)
        refresh = (
            self._envelope.seal(tokens.refresh_token.encode("utf-8"), aad=aad)
            if tokens.refresh_token
            else None
        )
        self._tokens.replace(
            external_identity_id=identity_id,
            access=access,
            refresh=refresh,
            scopes=tokens.scopes,
            access_expires_at=tokens.expires_at,
            grant_id=grant_id,
        )

    def record_refusal(
        self, *, code: str, correlation_id: UUID, subject: str | None = None
    ) -> None:
        """One audit event per refused login, carrying no secret.

        Never the code, the tokens, the state or the verifier — only the reason
        category and the correlation id the user can quote.
        """
        self._audit.record(
            AuditEvent(
                action="auth.login.refused",
                entity_type="oauth_transaction",
                entity_id=subject or "unknown",
                source=AuditSource.WEB,
                actor_capability=ActorCapability.SYSTEM,
                correlation_id=correlation_id,
                payload={"reason": code},
            )
        )


__all__ = [
    "CompletedLogin",
    "DEFAULT_RETURN_PATH",
    "OAuthLoginService",
    "RETURN_PATH_PATTERNS",
    "RecoveredTransaction",
    "StartedLogin",
    "safe_return_path",
]
