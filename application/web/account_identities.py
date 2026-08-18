"""R-35 to R-37: the caller's own external identities, and the unlink boundary.

Small, and deliberately so. Phase 3 has exactly one ordinary provider, so this
package's job is not to link accounts across providers — it is to make the
*boundary* real, so that the later approved provider package extends something
that already refuses correctly rather than inventing the rules then.

## What is listed, and what is not

Provider key, subject, when it was linked, when it last authenticated, and
whether it is the identity this session authenticated with. **No token, ever** —
`oauth_token_grants` is not read here and there is no field for its contents.
`subject_display` shows the caller their *own* Discord snowflake in full, because
it is their own identifier, and no view another member can see carries it.

Retired identities stay listed. Historical audit attribution resolves through
`external_identities` after a provider is retired (schema §6.3), so a retired row
is history a person should be able to see; it carries no control, because there
is nothing to do to it.

## The unlink refusal, and the asymmetry inside it

R-37 refuses to leave an account with **no usable identity and no reviewed
recovery route**. The recovery route is not the same for everybody, and that is
the whole of TC-ID-07:

* For the **protected Server Administrator account**, enrolled WebAuthn
  credentials are the reviewed recovery route (N-13, ADR 0010 D8). It may
  therefore unlink its last provider identity — while at least two credentials
  are enabled, which is the same floor C-03 refuses to go below.
* For an **ordinary member**, they are not. There is no member-facing WebAuthn
  enrollment route at all (enrollment is host-local, C-03), so credentials on the
  protected account are not a recovery route somebody else can use, and
  inheriting them would be reading one account's controls as another's.

A break-glass session cannot unlink at all (`BG` and `AC` are `✗ 403` on R-36 and
R-37). Converting a temporary authentication event into a permanent one is the
same laundering N-67 refuses one level down, and the route surface refuses it
here.

## Linking an additional identity

R-36 requires strong reauthentication (N-16) or the separately audited
Council/Server-Administrator recovery decision. Phase 3 exercises neither,
because there is no second ordinary provider to link *to*: the route answers
VM-13's `no_additional_provider` state. A provider display name or an email never
links accounts — `external_identities` has no column for either, so there is
nothing to link by.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from application.audit import ActorCapability, AuditEvent, AuditSource
from application.web.capabilities import WebAuthorizationContext
from application.web.errors import (
    ObjectNotReachable,
    RefusalCode,
    WebRefusal,
)
from application.web.view_models import (
    LINKED_IDENTITY_BOUND,
    AccountIdentitiesView,
    Instant,
    LinkedIdentity,
    bounded_tuple,
)

#: N-13's floor, restated where the unlink decision is taken. C-03 refuses to
#: retire a credential that would leave the protected account with fewer than
#: two; this refuses to remove the *provider* identity that would make those
#: credentials the only way in, unless there are still two of them.
PROTECTED_CREDENTIAL_FLOOR = 2

PROVIDER_DISPLAY_NAMES = {"discord": "Discord"}


class UnlinkRefused(WebRefusal):
    """Removing this identity would leave the account with no way back in.

    `409` with the current state: nothing is wrong with the request, and nothing
    the caller can retype would make it acceptable. What has to change is the
    account's set of identities, which is what the page they are returned to
    shows them.
    """

    def __init__(self, correlation_id: UUID | None = None) -> None:
        super().__init__(
            RefusalCode.STALE_VERSION, status=409, correlation_id=correlation_id
        )


class AccountIdentityService:
    """The caller's own identities. Every method is scoped to `context.account_id`."""

    __slots__ = ("_accounts", "_credentials", "_audit")

    def __init__(self, *, accounts, credentials, audit) -> None:
        self._accounts = accounts
        self._credentials = credentials
        self._audit = audit

    # -- R-35 -------------------------------------------------------------
    def overview(
        self,
        context: WebAuthorizationContext,
        *,
        current_subject: str | None = None,
        state: str = "ready",
    ) -> AccountIdentitiesView:
        """List **this** account's identities. The scope is the parameter, not a filter.

        `context.account_id` is resolved from the session on this request, so
        there is no identifier a caller could substitute to read somebody else's
        list — the method takes no account argument at all.
        """
        rows = self._accounts.identities_for(context.account_id)
        visible, _ = bounded_tuple(rows, LINKED_IDENTITY_BOUND)
        identities = tuple(
            LinkedIdentity(
                identity_id=row["id"],
                provider_key=row["provider_key"],
                provider_display_name=PROVIDER_DISPLAY_NAMES.get(
                    row["provider_key"], row["provider_key"]
                ),
                # The caller's own subject, in full. It is their identifier, and
                # it appears in no view anybody else can see.
                subject_display=row["subject"],
                linked_at=Instant.of(row["linked_at"]),
                last_authenticated_at=(
                    Instant.of(row["last_authenticated_at"])
                    if row["last_authenticated_at"]
                    else None
                ),
                state=row["state"],
                is_current_session_identity=(
                    current_subject is not None and row["subject"] == current_subject
                ),
            )
            for row in visible
        )
        return AccountIdentitiesView(
            state=state,
            account_id=context.account_id,
            identities=identities,
            # Phase 3 has one ordinary provider, so this is the only value the
            # field can take. It is a literal rather than a computed choice
            # because computing it would imply a second provider exists to be
            # chosen — and adding one is a separately approved package (ADR
            # 0010 D7), not a branch somebody flips here.
            additional_provider="no_additional_provider",
            unlink_blocked_reason=self._blocked_reason(context),
        )

    # -- R-37 -------------------------------------------------------------
    def unlink(
        self,
        *,
        context: WebAuthorizationContext,
        identity_id: UUID,
        correlation_id: UUID,
        now: datetime,
    ) -> UUID:
        """Retire one of the caller's own identities, or refuse.

        Both the ownership check and the last-usable-identity rule are here, and
        the ownership check comes first: an identity belonging to another account
        answers `404`, byte-identical to one that does not exist, so the route
        cannot be used to discover whose identity a given UUID is.
        """
        row = self._accounts.identity(identity_id)
        if row is None or row["platform_account_id"] != context.account_id:
            raise ObjectNotReachable(correlation_id)

        # The last-usable-identity rule is an account-wide invariant. Lock the
        # stable parent row, then re-read the target: two concurrent requests can
        # name different identity rows, so a conditional update on the target
        # alone cannot serialize the count-and-retire decision.
        if not self._accounts.lock_identity_changes(context.account_id):
            raise ObjectNotReachable(correlation_id)
        row = self._accounts.identity(identity_id)
        if row is None or row["platform_account_id"] != context.account_id:
            raise ObjectNotReachable(correlation_id)
        if row["state"] != "active":
            # Already retired. Refusing rather than answering "done" keeps the
            # audit honest: nothing happened, and a second retirement record
            # would say something did.
            raise UnlinkRefused(correlation_id)

        if self._accounts.active_identity_count(context.account_id) <= 1:
            if not self._has_reviewed_recovery_route(context.account_id):
                self._audit.record(
                    self._event(
                        "identity.link_refused",
                        identity_id,
                        context,
                        correlation_id,
                        {
                            "provider_key": row["provider_key"],
                            "refusal": "last_usable_identity",
                        },
                    )
                )
                raise UnlinkRefused(correlation_id)

        if not self._accounts.retire_identity(
            identity_id, reason="unlinked by the account holder", at=now
        ):
            raise UnlinkRefused(correlation_id)

        self._audit.record(
            self._event(
                "identity.unlinked",
                identity_id,
                context,
                correlation_id,
                {
                    "provider_key": row["provider_key"],
                    "before": {"state": "active"},
                    "after": {"state": "retired"},
                },
            )
        )
        return identity_id

    # -- helpers ----------------------------------------------------------
    def _has_reviewed_recovery_route(self, account_id: UUID) -> bool:
        """Only the protected account has one, and only while N-13 is satisfied.

        An ordinary member has no WebAuthn credential and no route to enroll one,
        so there is nothing here that could be true for them. Writing the check
        as "does this account hold credentials?" would have been the same thing
        today and the wrong rule the moment member enrollment exists.
        """
        account = self._accounts.get(account_id)
        if account is None or not account.is_protected_admin:
            return False
        return (
            len(self._credentials.enabled_credentials(account_id))
            >= PROTECTED_CREDENTIAL_FLOOR
        )

    def _blocked_reason(self, context: WebAuthorizationContext):
        if context.is_continuity_scoped:
            return "emergency_session"
        if self._accounts.active_identity_count(
            context.account_id
        ) <= 1 and not self._has_reviewed_recovery_route(context.account_id):
            return "last_usable_identity"
        return None

    @staticmethod
    def _event(
        action: str,
        identity_id: UUID,
        context: WebAuthorizationContext,
        correlation_id: UUID,
        payload: dict,
    ) -> AuditEvent:
        return AuditEvent(
            action=action,
            entity_type="external_identity",
            entity_id=str(identity_id),
            source=AuditSource.WEB,
            actor_capability=ActorCapability.GUILD_MEMBER,
            correlation_id=correlation_id,
            actor_platform_account_id=context.account_id,
            payload=payload,
        )


__all__ = [
    "AccountIdentityService",
    "PROTECTED_CREDENTIAL_FLOOR",
    "PROVIDER_DISPLAY_NAMES",
    "UnlinkRefused",
]
