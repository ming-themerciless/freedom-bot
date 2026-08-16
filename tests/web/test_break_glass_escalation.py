"""TC-BG-05a…05e and TC-CAP-08…11: emergency authority is not convertible.

This file exists because the withdrawn TC-BG-05 asked the wrong question. It
checked that a break-glass session's own capability set stayed
`{platform_administrator}` and treated a successful mapping change as expected —
which would have passed while the platform was escalatable, because the attack
does not need the emergency session to *hold* Council. It needs the emergency
session to **arrange** for a later ordinary session to hold it.

So the property under test is one about **sequences**:

> No sequence of mapping changes that begins in a break-glass session and passes
> through any number of ordinary logins yields Council, character or import
> authority, until a full-scope administrator ratifies.

`test_the_whole_escalation_sequence_is_refused` is that sentence, executed.
"""
from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import insert, select, text

from adapters.database.tables import (
    role_capability_mapping_events,
    role_capability_mappings,
)
from adapters.web.repositories import RoleMappingRepository
from application.audit import ActorCapability
from application.web.capabilities import (
    AdministratorScope,
    AuthMethod,
    MappingProvenance,
    MembershipProjection,
    RoleCapabilityMapping,
    WebAuthorizationContext,
    resolve_capabilities,
)
from application.web.errors import EmergencyScopeRefused, WebRefusal
from application.web.role_mappings import RoleMappingService, run_mapping_change
from tests.web.conftest import add_mapping, make_account, utcnow
from tests.web_fixtures import (
    BOOTSTRAP_ADMIN_ROLE_ID,
    COUNCIL_ROLE_ID,
    TEST_GUILD_ID,
)

pytestmark = pytest.mark.database

#: The role the attacker in schema §8.1's scenario controls.
ATTACKER_ROLE_ID = 900000000000000077


def _membership(role_ids):
    return MembershipProjection(
        guild_id=TEST_GUILD_ID,
        is_member=True,
        role_ids=frozenset(role_ids),
        observed_at=utcnow(),
    )


def _break_glass_context(account_id):
    return resolve_capabilities(
        account_id=account_id,
        auth_method=AuthMethod.WEBAUTHN,
        membership=None,
        mappings=(),
    )


def _ordinary_context(account_id, role_ids, mappings):
    return resolve_capabilities(
        account_id=account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        membership=_membership(role_ids),
        mappings=mappings,
    )


def _service(connection):
    from adapters.web.repositories import WebAuditRepository

    return RoleMappingService(
        role_mappings=RoleMappingRepository(connection),
        audit=WebAuditRepository(connection),
    )


# ---------------------------------------------------------------------------
# TC-BG-05a
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "capability",
    [
        ActorCapability.GUILD_COUNCIL,
        ActorCapability.DM,
        ActorCapability.CHARACTER_OWNER,
        ActorCapability.GUILD_MEMBER,
    ],
)
def test_a_continuity_scoped_create_is_refused_and_recorded(
    migrated_database, composition, capability
):
    """TC-BG-05a. No row is written, and a refusal row **is**, naming the attempt.

    Recording the attempted capability is the point: *"a break-glass session
    tried to map a role to Council"* is the sentence an incident review needs,
    and it exists nowhere else if the refusal writes only a counter.
    """
    with migrated_database.begin() as connection:
        account_id = make_account(connection, protected=True)
    context = _break_glass_context(account_id)
    correlation_id = uuid4()

    with pytest.raises(EmergencyScopeRefused):
        run_mapping_change(
            migrated_database,
            lambda connection: _service(connection).create(
                context=context,
                guild_id=TEST_GUILD_ID,
                role_id=ATTACKER_ROLE_ID,
                capability=capability,
                reason="emergency repair",
                correlation_id=correlation_id,
            ),
        )

    with migrated_database.connect() as connection:
        written = connection.execute(
            select(text("count(*)"))
            .select_from(role_capability_mappings)
            .where(role_capability_mappings.c.role_id == ATTACKER_ROLE_ID)
        ).scalar_one()
        events = connection.execute(
            select(role_capability_mapping_events).where(
                role_capability_mapping_events.c.correlation_id == correlation_id
            )
        ).mappings().all()

    assert written == 0, "a refused create must write no mapping"
    assert len(events) == 1
    event = events[0]
    assert event["outcome"] == "refused"
    assert event["refusal_code"] == "emergency_scope_refused"
    assert event["capability"] == capability.value
    assert event["scope"] == "emergency_continuity"
    assert event["auth_method"] == "webauthn"


def test_the_one_mapping_a_continuity_scoped_caller_may_create_succeeds(
    migrated_database, composition
):
    """The allowlist's positive half (N-67, schema §8.2 row 1).

    The failure this exists for: the Discord role carrying administrator
    authority has been deleted and recreated with a new snowflake, so the
    protected bootstrap mapping points at a role nobody can hold. Without this,
    restoring administrator access needs database-owner action.
    """
    with migrated_database.begin() as connection:
        account_id = make_account(connection, protected=True)
    context = _break_glass_context(account_id)

    outcome = run_mapping_change(
        migrated_database,
        lambda connection: _service(connection).create(
            context=context,
            guild_id=TEST_GUILD_ID,
            role_id=ATTACKER_ROLE_ID,
            capability=ActorCapability.PLATFORM_ADMINISTRATOR,
            reason="the administrator role was recreated with a new snowflake",
            correlation_id=uuid4(),
        ),
    )

    with migrated_database.connect() as connection:
        row = connection.execute(
            select(role_capability_mappings).where(
                role_capability_mappings.c.id == outcome.mapping_id
            )
        ).mappings().one()
    assert row["created_under_scope"] == "emergency_continuity"
    # Provenance travels with the row. This is what makes the restriction
    # survive an ordinary login instead of being laundered by one.
    assert row["provenance"] == "emergency_continuity"
    assert row["ratified_at"] is None


# ---------------------------------------------------------------------------
# TC-BG-05d
# ---------------------------------------------------------------------------


def test_the_constraint_refuses_the_same_thing_with_the_application_bypassed(
    migrated_database,
):
    """TC-BG-05d. Control 2, and the only one that does not depend on the session.

    Issued directly against the database, as the schema owner, with no
    application in the path at all. It depends on **what is being written**,
    which is why it holds when the service is wrong, bypassed, or replaced by a
    future one that forgets.
    """
    from sqlalchemy.exc import IntegrityError

    with migrated_database.begin() as connection:
        account_id = make_account(connection)

    with pytest.raises(IntegrityError) as failure:
        with migrated_database.begin() as connection:
            connection.execute(
                insert(role_capability_mappings).values(
                    id=uuid4(),
                    guild_id=TEST_GUILD_ID,
                    role_id=ATTACKER_ROLE_ID,
                    capability="guild_council",
                    protected=False,
                    active=True,
                    created_by_account_id=account_id,
                    created_under_auth_method="webauthn",
                    created_under_scope="emergency_continuity",
                    provenance="emergency_continuity",
                    reason="bypassing the application entirely",
                    audit_correlation_id=uuid4(),
                )
            )
    assert "continuity_create_allowlist" in str(failure.value)


# ---------------------------------------------------------------------------
# TC-CAP-08
# ---------------------------------------------------------------------------


def test_administrator_scope_resolution_is_parametrized_exactly_as_documented():
    """TC-CAP-08. Four cases, and the third is the one that keeps ratification reachable.

    "Every conferring mapping is emergency-derived", not "any": an administrator
    who *also* holds the authority through an ordinary mapping is full-scope, and
    the protected bootstrap row is ordinary by construction. Without that, an
    emergency mapping could make even the protected administrator continuity-
    scoped, and nobody could ever ratify anything.
    """
    account_id = uuid4()
    ordinary = RoleCapabilityMapping(
        id=uuid4(),
        guild_id=TEST_GUILD_ID,
        role_id=BOOTSTRAP_ADMIN_ROLE_ID,
        capability=ActorCapability.PLATFORM_ADMINISTRATOR,
        provenance=MappingProvenance.ORDINARY,
        protected=True,
    )
    emergency = RoleCapabilityMapping(
        id=uuid4(),
        guild_id=TEST_GUILD_ID,
        role_id=ATTACKER_ROLE_ID,
        capability=ActorCapability.PLATFORM_ADMINISTRATOR,
        provenance=MappingProvenance.EMERGENCY_CONTINUITY,
    )

    from_protected = _ordinary_context(
        account_id, {BOOTSTRAP_ADMIN_ROLE_ID}, [ordinary, emergency]
    )
    assert from_protected.administrator_scope is AdministratorScope.FULL

    from_emergency = _ordinary_context(
        account_id, {ATTACKER_ROLE_ID}, [ordinary, emergency]
    )
    assert from_emergency.administrator_scope is AdministratorScope.EMERGENCY_CONTINUITY
    assert from_emergency.is_continuity_scoped

    from_both = _ordinary_context(
        account_id, {BOOTSTRAP_ADMIN_ROLE_ID, ATTACKER_ROLE_ID}, [ordinary, emergency]
    )
    assert from_both.administrator_scope is AdministratorScope.FULL

    break_glass = _break_glass_context(account_id)
    assert break_glass.administrator_scope is AdministratorScope.EMERGENCY_CONTINUITY
    assert break_glass.capabilities == frozenset(
        {ActorCapability.PLATFORM_ADMINISTRATOR}
    )


def test_a_break_glass_session_resolves_to_administrator_even_holding_council_roles(
    migrated_database,
):
    """TC-BG-04's capability half. The Discord projection is not consulted at all.

    Break-glass never touches the membership projection (route contract §7.3), so
    whatever roles the same human holds on Discord are irrelevant to what the
    emergency session may do.
    """
    council = RoleCapabilityMapping(
        id=uuid4(),
        guild_id=TEST_GUILD_ID,
        role_id=COUNCIL_ROLE_ID,
        capability=ActorCapability.GUILD_COUNCIL,
        provenance=MappingProvenance.ORDINARY,
    )
    context = resolve_capabilities(
        account_id=uuid4(),
        auth_method=AuthMethod.WEBAUTHN,
        membership=_membership({COUNCIL_ROLE_ID}),
        mappings=[council],
    )
    assert context.capabilities == frozenset({ActorCapability.PLATFORM_ADMINISTRATOR})
    assert not context.guild_council
    assert context.membership is None


# ---------------------------------------------------------------------------
# TC-BG-05c — the sequence
# ---------------------------------------------------------------------------


def test_the_whole_escalation_sequence_is_refused(migrated_database, composition):
    """TC-BG-05c. The attack of schema §8.1, executed end to end and stopped.

        break-glass session
          -> create the one mapping it *is* allowed (administrator for role X)
          -> ordinary Discord login as a member holding role X
          -> assert the resolved set is {platform_administrator}, scope
             emergency_continuity
          -> attempt to map role X to guild_council as that ordinary session
          -> refused

    Every hop is exercised. Asserting each hop in isolation would have passed on
    the platform this test was written to prove is not escalatable.
    """
    with migrated_database.begin() as connection:
        emergency_account = make_account(connection, protected=True)
        ordinary_account = make_account(connection)

    # Hop 1: the emergency session creates the one mapping the allowlist permits.
    outcome = run_mapping_change(
        migrated_database,
        lambda connection: _service(connection).create(
            context=_break_glass_context(emergency_account),
            guild_id=TEST_GUILD_ID,
            role_id=ATTACKER_ROLE_ID,
            capability=ActorCapability.PLATFORM_ADMINISTRATOR,
            reason="restoring administrator continuity",
            correlation_id=uuid4(),
        ),
    )

    # Hop 2: an ordinary Discord login as a member holding that role.
    with migrated_database.connect() as connection:
        mappings = RoleMappingRepository(connection).active_mappings(TEST_GUILD_ID)
    laundered = _ordinary_context(ordinary_account, {ATTACKER_ROLE_ID}, mappings)

    assert laundered.auth_method is AuthMethod.DISCORD_OAUTH
    assert laundered.capabilities == frozenset(
        {ActorCapability.PLATFORM_ADMINISTRATOR, ActorCapability.GUILD_MEMBER}
    )
    # The laundering did not work: the authority descends from an emergency
    # mapping, so it is still continuity-scoped.
    assert laundered.administrator_scope is AdministratorScope.EMERGENCY_CONTINUITY
    assert laundered.is_continuity_scoped
    assert not laundered.guild_council

    # Hop 3: that ordinary administrator session tries to map Council.
    with pytest.raises(EmergencyScopeRefused):
        run_mapping_change(
            migrated_database,
            lambda connection: _service(connection).create(
                context=laundered,
                guild_id=TEST_GUILD_ID,
                role_id=ATTACKER_ROLE_ID,
                capability=ActorCapability.GUILD_COUNCIL,
                reason="the second hop",
                correlation_id=uuid4(),
            ),
        )

    # And R-38's door is shut from this side too.
    with pytest.raises(EmergencyScopeRefused):
        run_mapping_change(
            migrated_database,
            lambda connection: _service(connection).ratify(
                context=laundered,
                mapping_id=outcome.mapping_id,
                expected_version=0,
                reason="ratifying my own mapping",
                correlation_id=uuid4(),
                now=utcnow(),
            ),
        )

    with migrated_database.connect() as connection:
        council_mappings = connection.execute(
            select(text("count(*)"))
            .select_from(role_capability_mappings)
            .where(role_capability_mappings.c.capability == "guild_council")
        ).scalar_one()
        still_emergency = connection.execute(
            select(role_capability_mappings.c.provenance).where(
                role_capability_mappings.c.id == outcome.mapping_id
            )
        ).scalar_one()
    assert council_mappings == 0
    assert still_emergency == "emergency_continuity"


# ---------------------------------------------------------------------------
# TC-BG-05e — ratification is the only exit, and it is one-way
# ---------------------------------------------------------------------------


def test_ratification_by_a_full_scope_administrator_restores_full_scope(
    migrated_database, composition
):
    """TC-BG-05e, first half. R-38 flips provenance once, and scope follows."""
    with migrated_database.begin() as connection:
        emergency_account = make_account(connection, protected=True)
        admin_account = make_account(connection)

    outcome = run_mapping_change(
        migrated_database,
        lambda connection: _service(connection).create(
            context=_break_glass_context(emergency_account),
            guild_id=TEST_GUILD_ID,
            role_id=ATTACKER_ROLE_ID,
            capability=ActorCapability.PLATFORM_ADMINISTRATOR,
            reason="restoring administrator continuity",
            correlation_id=uuid4(),
        ),
    )

    # The full-scope administrator: authority from the protected bootstrap
    # mapping, which migration 0006 inserted `ordinary` by construction.
    with migrated_database.connect() as connection:
        mappings = RoleMappingRepository(connection).active_mappings(TEST_GUILD_ID)
    full = _ordinary_context(admin_account, {BOOTSTRAP_ADMIN_ROLE_ID}, mappings)
    assert full.administrator_scope is AdministratorScope.FULL

    run_mapping_change(
        migrated_database,
        lambda connection: _service(connection).ratify(
            context=full,
            mapping_id=outcome.mapping_id,
            expected_version=0,
            reason="adopting the emergency repair",
            correlation_id=uuid4(),
            now=utcnow(),
        ),
    )

    with migrated_database.connect() as connection:
        row = connection.execute(
            select(role_capability_mappings).where(
                role_capability_mappings.c.id == outcome.mapping_id
            )
        ).mappings().one()
        mappings = RoleMappingRepository(connection).active_mappings(TEST_GUILD_ID)
    assert row["provenance"] == "ordinary"
    assert row["ratified_by_account_id"] == admin_account

    # TC-CAP-10: the account whose authority came only from that mapping is now
    # full-scope, so its next capability resolution differs — which is a
    # different privilege fingerprint, which is what forces N-08's rotation.
    after = _ordinary_context(uuid4(), {ATTACKER_ROLE_ID}, mappings)
    assert after.administrator_scope is AdministratorScope.FULL
    before = _ordinary_context(
        after.account_id,
        {ATTACKER_ROLE_ID},
        [
            RoleCapabilityMapping(
                id=row["id"],
                guild_id=row["guild_id"],
                role_id=row["role_id"],
                capability=ActorCapability.PLATFORM_ADMINISTRATOR,
                provenance=MappingProvenance.EMERGENCY_CONTINUITY,
            )
        ],
    )
    assert before.privilege_fingerprint != after.privilege_fingerprint


def test_ratification_is_one_way_and_happens_once(migrated_database, composition):
    """TC-BG-05e, second half. The trigger refuses both reversals.

    A mapping cannot be pushed back across the boundary to disguise where it came
    from, and it cannot be re-ratified so the record of who adopted it is
    rewritten.
    """
    # `restrict_violation` is what the triggers raise, and psycopg surfaces it as
    # `IntegrityError`. `DatabaseError` is its common ancestor with the other
    # shapes a trigger refusal can take, so the assertion is about *being
    # refused by the database* rather than about which subclass a driver chose.
    from sqlalchemy.exc import DatabaseError

    with migrated_database.begin() as connection:
        emergency_account = make_account(connection, protected=True)
        admin_account = make_account(connection)
        mapping_id = add_mapping(
            connection,
            role_id=ATTACKER_ROLE_ID,
            capability="platform_administrator",
            created_by=emergency_account,
            scope="emergency_continuity",
            auth_method="webauthn",
        )

    with migrated_database.begin() as connection:
        assert RoleMappingRepository(connection).ratify(
            mapping_id=mapping_id,
            ratified_by=admin_account,
            expected_version=0,
            at=utcnow(),
        )

    # Reverse direction: refused by the trigger.
    with pytest.raises(DatabaseError) as reversal:
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    "UPDATE role_capability_mappings "
                    "SET provenance = 'emergency_continuity' WHERE id = :id"
                ),
                {"id": mapping_id},
            )
    assert "ordinary back to emergency_continuity" in str(reversal.value)

    # Second ratification: refused by the trigger.
    with pytest.raises(DatabaseError) as second:
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    "UPDATE role_capability_mappings SET ratified_at = now() "
                    "WHERE id = :id"
                ),
                {"id": mapping_id},
            )
    assert "ratified once" in str(second.value)


# ---------------------------------------------------------------------------
# TC-CAP-03, TC-CAP-04, TC-CAP-05, TC-CAP-11
# ---------------------------------------------------------------------------


def test_the_protected_bootstrap_mapping_cannot_be_changed_by_anyone(
    migrated_database, composition
):
    """TC-CAP-03. The trigger refuses the schema owner too, not only the runtime role."""
    from sqlalchemy.exc import DatabaseError

    with migrated_database.connect() as connection:
        protected_id = connection.execute(
            select(role_capability_mappings.c.id).where(
                role_capability_mappings.c.protected
            )
        ).scalar_one()

    for statement in (
        "UPDATE role_capability_mappings SET active = false WHERE id = :id",
        "UPDATE role_capability_mappings SET capability = 'guild_member' WHERE id = :id",
        "UPDATE role_capability_mappings SET protected = false WHERE id = :id",
        "DELETE FROM role_capability_mappings WHERE id = :id",
    ):
        with pytest.raises(DatabaseError):
            with migrated_database.begin() as connection:
                connection.execute(text(statement), {"id": protected_id})

    with migrated_database.connect() as connection:
        row = connection.execute(
            select(role_capability_mappings).where(
                role_capability_mappings.c.id == protected_id
            )
        ).mappings().one()
    assert row["active"] and row["protected"]
    assert row["capability"] == "platform_administrator"


def test_a_second_protected_mapping_and_a_second_protected_account_are_refused(
    migrated_database,
):
    """TC-CAP-05. Two anchors for lockout recovery would have no defined winner."""
    from sqlalchemy.exc import DatabaseError, IntegrityError

    with migrated_database.begin() as connection:
        account_id = make_account(connection, protected=True)

    with pytest.raises(DatabaseError):
        with migrated_database.begin() as connection:
            connection.execute(
                insert(role_capability_mappings).values(
                    id=uuid4(),
                    guild_id=TEST_GUILD_ID,
                    role_id=ATTACKER_ROLE_ID,
                    capability="platform_administrator",
                    protected=True,
                    active=True,
                    created_by_account_id=account_id,
                    created_under_auth_method="discord_oauth",
                    created_under_scope="full",
                    provenance="ordinary",
                    reason="a second protected mapping",
                    audit_correlation_id=uuid4(),
                )
            )

    with pytest.raises(IntegrityError):
        with migrated_database.begin() as connection:
            make_account(connection, protected=True)


def test_adding_mappings_can_never_subtract_administrator_capability(
    migrated_database,
):
    """TC-CAP-04. Resolution is a **union**, so there is no application path to lockout.

    The other half of that guarantee is the trigger refusing any change to the
    protected row; between them, nothing the administration surface can do
    removes the last route to administrator authority.
    """
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        add_mapping(
            connection,
            role_id=COUNCIL_ROLE_ID,
            capability="guild_council",
            created_by=account_id,
        )
        add_mapping(
            connection,
            role_id=BOOTSTRAP_ADMIN_ROLE_ID,
            capability="guild_member",
            created_by=account_id,
        )

    with migrated_database.connect() as connection:
        mappings = RoleMappingRepository(connection).active_mappings(TEST_GUILD_ID)

    context = _ordinary_context(
        account_id, {BOOTSTRAP_ADMIN_ROLE_ID, COUNCIL_ROLE_ID}, mappings
    )
    assert ActorCapability.PLATFORM_ADMINISTRATOR in context.capabilities
    assert ActorCapability.GUILD_COUNCIL in context.capabilities


def test_every_mapping_attempt_writes_exactly_one_event(migrated_database, composition):
    """TC-CAP-11. Applied and refused alike, with operation, outcome and scope."""
    with migrated_database.begin() as connection:
        admin_account = make_account(connection)
    with migrated_database.connect() as connection:
        mappings = RoleMappingRepository(connection).active_mappings(TEST_GUILD_ID)
    full = _ordinary_context(admin_account, {BOOTSTRAP_ADMIN_ROLE_ID}, mappings)

    applied_correlation = uuid4()
    run_mapping_change(
        migrated_database,
        lambda connection: _service(connection).create(
            context=full,
            guild_id=TEST_GUILD_ID,
            role_id=COUNCIL_ROLE_ID,
            capability=ActorCapability.GUILD_COUNCIL,
            reason="an ordinary administrator doing ordinary work",
            correlation_id=applied_correlation,
        ),
    )

    with migrated_database.connect() as connection:
        events = connection.execute(
            select(role_capability_mapping_events).where(
                role_capability_mapping_events.c.correlation_id == applied_correlation
            )
        ).mappings().all()
    assert len(events) == 1
    assert events[0]["outcome"] == "applied"
    assert events[0]["operation"] == "create"
    assert events[0]["refusal_code"] is None
    assert events[0]["scope"] == "full"
    assert events[0]["capability"] == "guild_council"
