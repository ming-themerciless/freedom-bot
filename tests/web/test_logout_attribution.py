"""TC-BG-20: `auth.logout` records the authority the actor actually held.

Raised as S-6 by the 2026-08-24 supervised session and confirmed as S2 by the
independent security review, and found the same way S-5 was — by reading the
rows a real break-glass ceremony wrote. The operator signed out of a continuity
session during a verified Discord outage, and the audit recorded:

    auth.logout   actor_capability = guild_member   auth_method = recovery_grant

The two halves of that row contradict each other. A break-glass administrator
holds `{platform_administrator}` and **no** proven guild membership at all
(N-12) — that is the entire point of ADR 0010 D8 — so the primary capability
column stated an authority the actor demonstrably did not hold, on the one event
an incident review reads to establish when emergency access ended.

The `auth_method` payload made the row *correctable by a reader who knew to
look*. That is not the same as correct, and it defeats the migration-0006
constraint swap, whose whole purpose was to make non-Discord attribution
expressible rather than approximate.

Every session class the platform can create is exercised here, not only the two
that were wrong: a regression that fixed break-glass by breaking ordinary logins
would be the same defect pointed the other way.
"""
from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import select

from adapters.database.tables import audit_events
from application.audit import ActorCapability
from application.web.capabilities import (
    AdministratorScope,
    AuthMethod,
    MembershipProjection,
    WebAuthorizationContext,
    audit_capability_of,
)
from tests.web.conftest import (
    link_discord,
    make_account,
    seed_oauth_transaction,
    utcnow,
)
from tests.web_fixtures import TEST_GUILD_ID

pytestmark = pytest.mark.database


def _ordinary_context(account_id, *capabilities):
    """An ordinary Discord session holding exactly these capabilities."""
    return WebAuthorizationContext(
        account_id=account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        capabilities=frozenset(capabilities),
        administrator_scope=AdministratorScope.FULL,
        membership=MembershipProjection(
            guild_id=TEST_GUILD_ID,
            is_member=True,
            role_ids=frozenset(),
            observed_at=utcnow(),
        ),
    )


def _break_glass_context(account_id, auth_method):
    """N-12's continuity session: one capability, no membership, no mappings."""
    return WebAuthorizationContext(
        account_id=account_id,
        auth_method=auth_method,
        capabilities=frozenset({ActorCapability.PLATFORM_ADMINISTRATOR}),
        administrator_scope=AdministratorScope.EMERGENCY_CONTINUITY,
        membership=None,
    )


def _logout_row(engine):
    with engine.connect() as connection:
        return connection.execute(
            select(
                audit_events.c.actor_capability,
                audit_events.c.actor_platform_account_id,
                audit_events.c.actor_discord_user_id,
                audit_events.c.payload,
            ).where(audit_events.c.action == "auth.logout")
        ).mappings().one()


def _sign_in_and_out(migrated_database, composition, *, context, linked: bool):
    """Create a session the way the platform does, then log it out."""
    with migrated_database.begin() as connection:
        services = composition.services(connection)
        issued = services.session_service.begin(
            context=context,
            now=utcnow(),
            correlation_id=uuid4(),
            oauth_transaction_id=(
                seed_oauth_transaction(connection) if linked else None
            ),
        )

    with migrated_database.begin() as connection:
        services = composition.services(connection)
        record = services.session_service.resolve(issued.token, now=utcnow())
        services.session_service.logout(
            record=record,
            account_id=context.account_id,
            now=utcnow(),
            correlation_id=uuid4(),
        )
    return _logout_row(migrated_database)


@pytest.mark.parametrize(
    "auth_method",
    [AuthMethod.WEBAUTHN, AuthMethod.RECOVERY_GRANT],
    ids=["webauthn", "recovery_grant"],
)
def test_a_break_glass_logout_is_attributed_to_the_administrator_it_was(
    migrated_database, composition, auth_method
):
    """Both break-glass methods, separately. This is the finding itself.

    Parametrized rather than written once for `webauthn`, because the session the
    operator actually signed out of on 2026-08-24 was a `recovery_grant` one —
    a fix verified only against the method that happens to be listed first would
    have left the observed case untested.
    """
    with migrated_database.begin() as connection:
        account_id = make_account(
            connection, protected=True, label="Server Administrator"
        )

    row = _sign_in_and_out(
        migrated_database,
        composition,
        context=_break_glass_context(account_id, auth_method),
        linked=False,
    )

    assert row["actor_capability"] == ActorCapability.PLATFORM_ADMINISTRATOR.value
    assert row["payload"]["auth_method"] == auth_method.value
    # The account is named and no Discord user is, which is exactly the shape
    # migration 0006's constraint swap exists to permit.
    assert row["actor_platform_account_id"] == account_id
    assert row["actor_discord_user_id"] is None


@pytest.mark.parametrize(
    "capabilities",
    [
        (ActorCapability.GUILD_MEMBER,),
        (ActorCapability.GUILD_MEMBER, ActorCapability.GUILD_COUNCIL),
        (ActorCapability.GUILD_MEMBER, ActorCapability.PLATFORM_ADMINISTRATOR),
    ],
    ids=["member", "council", "administrator"],
)
def test_an_ordinary_logout_is_still_attributed_to_the_member_who_signed_in(
    migrated_database, composition, capabilities
):
    """The unchanged half, held in place by tests rather than by memory.

    `guild_member` is the right word for an ordinary Discord session whatever
    else that person holds, and it is the same word `auth.login.succeeded`
    records for the very same session — the pair of events an investigator reads
    end to end. A Council member's or an administrator's *sign-out* is not an
    exercise of Council or administrator authority; it is the ordinary
    provider-authenticated person leaving.
    """
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        link_discord(connection, account_id, 700000000000000321)

    row = _sign_in_and_out(
        migrated_database,
        composition,
        context=_ordinary_context(account_id, *capabilities),
        linked=True,
    )

    assert row["actor_capability"] == ActorCapability.GUILD_MEMBER.value
    assert row["payload"]["auth_method"] == AuthMethod.DISCORD_OAUTH.value


def test_the_attribution_comes_from_the_persisted_row_and_not_the_caller():
    """Every method is decided in the table, and an unknown one is refused.

    `audit_capability_of` is the whole mechanism, so it is asserted directly as
    well as through the route: the persisted string `"webauthn"` is not a key of
    the table, and a lookup that fell back on a default would hand it whichever
    capability the fallback named — which is the false attribution this function
    exists to end.
    """
    assert audit_capability_of(AuthMethod.DISCORD_OAUTH) is ActorCapability.GUILD_MEMBER
    assert (
        audit_capability_of(AuthMethod.WEBAUTHN)
        is ActorCapability.PLATFORM_ADMINISTRATOR
    )
    assert (
        audit_capability_of(AuthMethod.RECOVERY_GRANT)
        is ActorCapability.PLATFORM_ADMINISTRATOR
    )
    with pytest.raises(TypeError):
        audit_capability_of("webauthn")


def test_a_future_authentication_method_must_state_its_authority():
    """The startup guard, exercised on a synthetic enum a test *can* extend.

    `AuthMethod` is closed, so proving "a method nobody decided an authority for
    is refused" cannot be done by adding a member. It is done the way
    `unclassified_methods` is tested: the same function, over an enum built here.
    """
    import enum

    from application.web.capabilities import (
        UnattributedAuthMethod,
        require_complete_attribution,
        unattributed_methods,
    )

    class _Future(enum.Enum):
        DECIDED = "decided"
        FORGOTTEN = "forgotten"

    table = {_Future.DECIDED: ActorCapability.SYSTEM}
    assert unattributed_methods(_Future, table) == ("forgotten",)
    with pytest.raises(UnattributedAuthMethod, match="forgotten"):
        require_complete_attribution(_Future, table)
