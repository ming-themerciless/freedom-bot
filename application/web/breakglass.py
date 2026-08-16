"""Break-glass administration: WebAuthn and the host-issued grant (SM-03).

This is the path that must work **when Discord does not**. No step in it contacts
a provider, reads the membership projection or resolves a Discord role, and
`TC-BG-02` proves that by running the whole flow against a faulted double that
refuses every provider call.

## What a break-glass session is, and is not

`{platform_administrator}`, and nothing else, whatever Discord roles the same
human holds (N-12, ADR 0010 D9). Never Council, never character ownership, never
import-apply authority by implication. It is short — fifteen minutes idle, sixty
absolute, no extension (N-15) — and confined further by N-65's route surface and
N-67's mapping allowlist.

## Why there is no password anywhere

ADR 0010 D8. A permanent local password is a standing credential with no expiry,
guessable, phishable and reusable — the "permanent backdoor or overpowered
emergency account" risk the delivery plan names. Two pre-enrolled passkeys plus a
host-issued ten-minute grant cover the same outages without a credential that
exists when nobody is using it.

## Why the grant is hashed with plain SHA-256

Because it is 256 bits of entropy printed once by C-01, not a password. There is
no low-entropy guess for a slow hash to slow down; what matters is that the
stored form is one-way and that consumption is a single conditional statement.
Argon2 here would be cargo cult.

## Enrollment and issuance are host-local, and that is the boundary

There is **no HTTP route** that issues a grant or enrolls a credential (route
contract §8, TC-BG-10). Both require existing host authority, so a stolen
break-glass session cannot enroll an attacker's authenticator and an attacker on
the internet cannot ask for a grant. The alternative — a remote API protected by
an API key — converts "an attacker needs host access" into "an attacker needs one
secret", and that secret would live in a file on the same host anyway.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import webauthn
from webauthn.helpers import base64url_to_bytes
from webauthn.helpers.exceptions import InvalidAuthenticationResponse
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    UserVerificationRequirement,
)

from application.audit import ActorCapability, AuditEvent, AuditSource
from application.web.capabilities import (
    AuthMethod,
    resolve_capabilities,
)
from application.web.config import (
    RateLimitSettings,
    WebAuthnSettings,
    WebSettings,
    canonical_settings,
)
from application.web.crypto import token_hash
from application.web.errors import AuthenticationFailure, FailureAudit
from application.web.sessions import IssuedSession, SessionService

#: The minimum number of enabled credentials the protected account must keep
#: (N-13). It is an application invariant rather than a constraint for the same
#: reason OD-37's "at least one owner" is: PostgreSQL cannot require a row in
#: another table without a deferred trigger, and the account has to exist before
#: the first credential is enrolled.
MINIMUM_ENROLLED_CREDENTIALS = 2


@dataclass(frozen=True, slots=True)
class ChallengeOptions:
    """What R-07 hands the browser. Identical whether or not anything is enrolled."""

    payload: dict
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class EmergencyLogin:
    session: IssuedSession
    account_id: UUID
    credential_record_id: UUID | None
    grant_record_id: UUID | None


class BreakGlassService:
    """WebAuthn assertions and recovery-grant redemption. No Discord anywhere."""

    __slots__ = (
        "_accounts",
        "_credentials",
        "_grants",
        "_sessions",
        "_audit",
        "_settings",
        "_webauthn",
        "_rate_limits",
    )

    def __init__(
        self,
        *,
        accounts,
        webauthn_repository,
        recovery_grants,
        session_service: SessionService,
        audit,
        settings: WebSettings,
    ) -> None:
        self._accounts = accounts
        self._credentials = webauthn_repository
        self._grants = recovery_grants
        self._sessions = session_service
        self._audit = audit
        self._settings = settings
        # The relying party and the per-grant attempt cap are read **once**, here,
        # and validated as they are read (2026-08-15, I-10). Both were previously
        # re-read from the settings tree on every assertion and every redemption,
        # so a subclass that answered one relying-party identifier when it was
        # checked and another when it was used would have moved the credential
        # scope out from under a verification that had already passed.
        self._webauthn = canonical_settings(settings.webauthn, WebAuthnSettings)
        self._rate_limits = canonical_settings(settings.rate_limits, RateLimitSettings)

    # -- WebAuthn ---------------------------------------------------------
    def begin_assertion(
        self, *, now: datetime, client_ip_hash: bytes | None
    ) -> ChallengeOptions:
        """Mint a challenge. **Reveals no account existence.**

        `allow_credentials` is deliberately left empty rather than populated from
        the enrolled set: sending credential ids would tell an unauthenticated
        caller both that an account exists and which authenticators it holds. The
        cost is that the browser must use a discoverable credential, which N-60
        permits, and the benefit is that this response is byte-identical for
        every caller.
        """
        options = webauthn.generate_authentication_options(
            rp_id=self._webauthn.rp_id,
            timeout=60_000,
            allow_credentials=[],
            user_verification=UserVerificationRequirement.REQUIRED,
        )
        expires_at = now + timedelta(
            minutes=self._settings.session.oauth_transaction_minutes
        )
        self._credentials.issue_challenge(
            challenge=options.challenge,
            expires_at=expires_at,
            client_ip_hash=client_ip_hash,
        )
        import json

        return ChallengeOptions(
            payload=json.loads(webauthn.options_to_json(options)),
            expires_at=expires_at,
        )

    def complete_assertion(
        self,
        *,
        credential_payload: dict,
        now: datetime,
        correlation_id: UUID,
        client_ip_hash: bytes | None,
        user_agent_digest: bytes | None,
    ) -> EmergencyLogin:
        """Verify signature, RP ID, origin, user verification and `sign_count`.

        Every failure below is the same `invalid` to the browser and a distinct
        sentence in the audit record. The response must not let a caller tell an
        unknown credential from a bad signature from a replayed challenge.
        """
        raw_id = credential_payload.get("rawId") or credential_payload.get("id")
        if not raw_id:
            raise self._refuse("invalid", correlation_id, reason="no_credential_id")
        try:
            credential_id = base64url_to_bytes(raw_id)
        except Exception as error:  # noqa: BLE001 - malformed input is one outcome
            raise self._refuse(
                "invalid", correlation_id, reason="malformed_credential_id"
            ) from error

        record = self._credentials.find_by_credential_id(credential_id)
        if record is None:
            raise self._refuse("invalid", correlation_id, reason="unknown_credential")

        challenge = self._challenge_from(credential_payload, correlation_id)
        if not self._credentials.consume_challenge(challenge=challenge, now=now):
            # Expired, already used, or never issued. One conditional statement,
            # so a replay and a race end in the same place.
            raise self._refuse("expired", correlation_id, reason="challenge_not_live")

        try:
            verification = webauthn.verify_authentication_response(
                credential=credential_payload,
                expected_challenge=challenge,
                expected_rp_id=self._webauthn.rp_id,
                expected_origin=list(self._webauthn.allowed_origins),
                credential_public_key=record.public_key,
                credential_current_sign_count=record.sign_count,
                require_user_verification=True,
            )
        except InvalidAuthenticationResponse as error:
            raise self._refuse(
                "invalid",
                correlation_id,
                reason="assertion_rejected",
                credential_record_id=record.id,
            ) from error

        # `verify_authentication_response` already refuses a non-increasing
        # counter when the authenticator supplies one. The explicit check is kept
        # because a decrease is the *cloned authenticator* signal, and it should
        # be a named refusal in the audit rather than a generic rejection.
        if verification.new_sign_count and verification.new_sign_count <= record.sign_count:
            raise self._refuse(
                "invalid",
                correlation_id,
                reason="sign_count_did_not_advance",
                credential_record_id=record.id,
            )

        self._credentials.advance_sign_count(
            record.id, sign_count=verification.new_sign_count, at=now
        )
        issued = self._create_emergency_session(
            account_id=record.platform_account_id,
            auth_method=AuthMethod.WEBAUTHN,
            now=now,
            correlation_id=correlation_id,
            client_ip_hash=client_ip_hash,
            user_agent_digest=user_agent_digest,
            payload={"credential_record_id": str(record.id)},
            action="auth.emergency.webauthn.succeeded",
        )
        return EmergencyLogin(
            session=issued,
            account_id=record.platform_account_id,
            credential_record_id=record.id,
            grant_record_id=None,
        )

    def _challenge_from(self, payload: dict, correlation_id: UUID) -> bytes:
        response = payload.get("response") or {}
        client_data = response.get("clientDataJSON")
        if not client_data:
            raise self._refuse("invalid", correlation_id, reason="no_client_data")
        import json

        try:
            decoded = json.loads(base64url_to_bytes(client_data))
            return base64url_to_bytes(decoded["challenge"])
        except Exception as error:  # noqa: BLE001 - malformed input is one outcome
            raise self._refuse(
                "invalid", correlation_id, reason="malformed_client_data"
            ) from error

    # -- Recovery grant ---------------------------------------------------
    def redeem_recovery_grant(
        self,
        *,
        token: str,
        now: datetime,
        correlation_id: UUID,
        client_ip_hash: bytes | None,
        user_agent_digest: bytes | None,
    ) -> EmergencyLogin:
        """Consume a host-issued grant. Replay, expiry and races all yield nothing.

        The session id has to exist before the grant can name it as its consumer,
        and the grant has to be consumed before the session may be handed out.
        Both are true here because they are in one transaction: the session is
        created first, and if consumption then matches zero rows the caller's
        rollback removes the session with it.
        """
        hashed = token_hash(token)
        self._grants.note_attempt(token_hash=hashed)
        if (
            self._grants.attempts_for(token_hash=hashed)
            > self._rate_limits.recovery_attempts_per_grant
        ):
            raise self._refuse(
                "rate_limited", correlation_id, reason="grant_attempt_cap"
            )

        account = self._accounts.protected_administrator()
        if account is None:
            raise self._refuse(
                "not_available", correlation_id, reason="no_protected_account"
            )

        context = resolve_capabilities(
            account_id=account.id,
            auth_method=AuthMethod.RECOVERY_GRANT,
            membership=None,
            mappings=(),
        )
        issued = self._sessions.begin(
            context=context,
            now=now,
            correlation_id=correlation_id,
            client_ip_hash=client_ip_hash,
            user_agent_digest=user_agent_digest,
        )
        grant = self._grants.consume(
            token_hash=hashed, session_id=issued.session_id, now=now
        )
        if grant is None:
            raise self._refuse("invalid", correlation_id, reason="grant_not_live")
        if grant.platform_account_id != account.id:
            raise self._refuse(
                "invalid", correlation_id, reason="grant_names_another_account"
            )

        self._audit.record(
            AuditEvent(
                action="auth.emergency.recovery.consumed",
                entity_type="recovery_grant",
                # The **record id**, never the token. The token is not stored and
                # appears in no row, log line or audit payload.
                entity_id=str(grant.id),
                source=AuditSource.WEB,
                actor_capability=ActorCapability.PLATFORM_ADMINISTRATOR,
                correlation_id=correlation_id,
                actor_platform_account_id=account.id,
                payload={
                    "auth_method": AuthMethod.RECOVERY_GRANT.value,
                    "session_id": str(issued.session_id),
                },
            )
        )
        return EmergencyLogin(
            session=issued,
            account_id=account.id,
            credential_record_id=None,
            grant_record_id=grant.id,
        )

    # -- shared -----------------------------------------------------------
    def _create_emergency_session(
        self,
        *,
        account_id: UUID,
        auth_method: AuthMethod,
        now: datetime,
        correlation_id: UUID,
        client_ip_hash: bytes | None,
        user_agent_digest: bytes | None,
        payload: dict,
        action: str,
    ) -> IssuedSession:
        context = resolve_capabilities(
            account_id=account_id,
            auth_method=auth_method,
            membership=None,
            mappings=(),
        )
        issued = self._sessions.begin(
            context=context,
            now=now,
            correlation_id=correlation_id,
            client_ip_hash=client_ip_hash,
            user_agent_digest=user_agent_digest,
        )
        # Same transaction as the session insert, and this is the strictest place
        # in the platform for that rule: an unrecordable emergency login does not
        # occur. It is also the write the migration-0006 constraint swap exists
        # for — `platform_administrator` with an account and **no** Discord user
        # was illegal before it.
        self._audit.record(
            AuditEvent(
                action=action,
                entity_type="session",
                entity_id=str(issued.session_id),
                source=AuditSource.WEB,
                actor_capability=ActorCapability.PLATFORM_ADMINISTRATOR,
                correlation_id=correlation_id,
                actor_platform_account_id=account_id,
                payload={"auth_method": auth_method.value, **payload},
            )
        )
        return issued

    def _refuse(
        self,
        code: str,
        correlation_id: UUID,
        *,
        reason: str,
        credential_record_id: UUID | None = None,
    ) -> AuthenticationFailure:
        """Build the refusal **and** record it. Returned so callers can `raise` it.

        The audit payload carries the specific reason; the exception carries the
        coarse code the browser sees. Neither carries a secret: no assertion
        bytes, no public key, no token.
        """
        payload: dict[str, object] = {"reason": reason}
        if credential_record_id is not None:
            payload["credential_record_id"] = str(credential_record_id)
        # Described, not written. A refused emergency login rolls its transaction
        # back — that is what "no session was created" means — so the record has
        # to be committed afterwards, by the route, in a fresh transaction. SM-03
        # requires every attempt and outcome to be audited, and a record that
        # vanishes with the refusal would satisfy that only on paper.
        return AuthenticationFailure(
            code=code,
            correlation_id=correlation_id,
            audit=FailureAudit(
                action="auth.emergency.refused",
                entity_type="emergency_login",
                entity_id=str(credential_record_id or "unknown"),
                capability=ActorCapability.SYSTEM,
                payload=payload,
            ),
        )


__all__ = [
    "BreakGlassService",
    "ChallengeOptions",
    "EmergencyLogin",
    "MINIMUM_ENROLLED_CREDENTIALS",
]
