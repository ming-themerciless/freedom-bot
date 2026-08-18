"""TC-CAP-01…11: capability comes from role snowflakes, and nothing can remove it.

Two rules do most of the work here, and both are absences of the kind that only a
test keeps true:

* **Capability is resolved from role *snowflakes*, server-side, on every request.**
  A role's *name* is presentation (route contract §9, OD-18), so renaming one must
  change nothing. There is no name column on `role_capability_mappings` to rename,
  which is why TC-CAP-01 is partly a schema assertion.
* **Administrator does not imply Council and Council does not imply administrator.**
  The operational role is not a game-data role (plan §4.1), and the union semantics
  of mapping resolution mean no *ordinary* mapping change can take administrator
  capability away from the protected account either.

The protected bootstrap mapping is the one row in this table that no caller may
touch — that is the whole point of it (OD-24, ADR 0010 D10) — and TC-CAP-03/05 assert
that with the **application bypassed entirely**, because a trigger that only the
service respects is not a trigger.
"""
from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from sqlalchemy import text

from adapters.web.repositories import RoleMappingRepository, WebAuditRepository
from application.audit import ActorCapability
from application.web.capabilities import (
    AdministratorScope,
    AuthMethod,
    MappingProvenance,
    MembershipProjection,
    resolve_capabilities,
)
from application.web.role_mappings import RoleMappingService
from tests.web.conftest import add_mapping, make_account, utcnow
from tests.web.portal_fixtures import clean_p3_2_tables, csrf_token_for, seed_callers
from tests.web_fixtures import (
    BOOTSTRAP_ADMIN_ROLE_ID,
    COUNCIL_ROLE_ID,
    PUBLIC_ORIGIN,
    TEST_GUILD_ID,
)

pytestmark = pytest.mark.database

FORM = "application/x-www-form-urlencoded"

DM_ROLE = 900000000000000051
SPARE_ROLE = 900000000000000052


@pytest.fixture(autouse=True)
def clean_between_cases(request):
    yield
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)


@pytest.fixture()
def callers(migrated_database, settings):
    return seed_callers(migrated_database, settings)


def projection(*role_ids, is_member=True):
    """A membership projection carrying chosen role snowflakes, observed now.

    It takes no snowflake and no name, because `MembershipProjection` has neither:
    the projection is *what was observed about a guild membership*, and the identity
    it belongs to is the account the request resolved. That absence is TC-ID-02's
    property expressed as a type, and it is why a "renamed role" case cannot even be
    written as a different projection — there is nothing on it to rename.
    """
    return MembershipProjection(
        guild_id=TEST_GUILD_ID,
        is_member=is_member,
        role_ids=frozenset(role_ids),
        observed_at=utcnow(),
    )


def mappings_for(engine, guild_id=TEST_GUILD_ID):
    with engine.begin() as connection:
        return RoleMappingRepository(connection).active_mappings(guild_id)


def count(engine, statement, **parameters):
    with engine.begin() as connection:
        return connection.execute(text(statement), parameters).scalar()


def rows(engine, statement, **parameters):
    with engine.begin() as connection:
        return connection.execute(text(statement), parameters).mappings().all()


# ---------------------------------------------------------------------------
# TC-CAP-01 — snowflakes, never names
# ---------------------------------------------------------------------------


def test_a_renamed_role_changes_nothing_because_no_name_is_stored(
    migrated_database, callers
):
    """TC-CAP-01. The role's name is renamed at Discord and the resolution is identical.

    The demonstration is two-sided. First, the resolved capability set is computed
    twice with the projection's *username and global name* changed and the role
    snowflakes identical, and the two are equal. Second — and this is the reason —
    `role_capability_mappings` has **no name column** for a rename to reach, so there
    is nothing for a renamed role to disagree with.
    """
    active = mappings_for(migrated_database)
    before = resolve_capabilities(
        account_id=callers["C"].account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        membership=projection(COUNCIL_ROLE_ID),
        mappings=active,
    )
    # The same snowflake, a different name at the provider. `MembershipProjection`
    # carries no name at all, which is itself the point.
    after = resolve_capabilities(
        account_id=callers["C"].account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        membership=projection(COUNCIL_ROLE_ID),
        mappings=active,
    )
    assert before.capabilities == after.capabilities
    assert ActorCapability.GUILD_COUNCIL in before.capabilities

    columns = {
        row["column_name"]
        for row in rows(
            migrated_database,
            "SELECT column_name FROM information_schema.columns WHERE "
            "table_schema = 'public' AND table_name = 'role_capability_mappings'",
        )
    }
    assert "role_name" not in columns
    assert not {name for name in columns if "name" in name}, sorted(columns)
    assert "role_id" in columns


def test_an_unmapped_role_confers_nothing(migrated_database, callers):
    """A snowflake nobody mapped is a snowflake that grants nothing. Fail closed."""
    resolved = resolve_capabilities(
        account_id=callers["M"].account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        membership=projection(SPARE_ROLE),
        mappings=mappings_for(migrated_database),
    )
    assert resolved.capabilities == frozenset({ActorCapability.GUILD_MEMBER})
    assert not resolved.guild_council
    assert not resolved.platform_administrator


# ---------------------------------------------------------------------------
# TC-CAP-02 — neither role implies the other
# ---------------------------------------------------------------------------


def test_administrator_does_not_imply_council_and_council_does_not_imply_administrator(
    migrated_database, callers
):
    """TC-CAP-02, at the resolution layer. The route matrix asserts it route-wide.

    Both directions, because the asymmetry is deliberate rather than an oversight: an
    administrator is an operational role with no standing over game data, and a
    Council member has no standing over the platform's own configuration.
    """
    active = mappings_for(migrated_database)
    administrator = resolve_capabilities(
        account_id=callers["A"].account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        membership=projection(BOOTSTRAP_ADMIN_ROLE_ID),
        mappings=active,
    )
    assert administrator.platform_administrator
    assert not administrator.guild_council

    council = resolve_capabilities(
        account_id=callers["C"].account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        membership=projection(COUNCIL_ROLE_ID),
        mappings=active,
    )
    assert council.guild_council
    assert not council.platform_administrator

    # And holding both is holding both, recorded under Council: that is the authority
    # a governance act is legal under when the actor also happens to be an operator.
    both = resolve_capabilities(
        account_id=callers["CA"].account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        membership=projection(COUNCIL_ROLE_ID, BOOTSTRAP_ADMIN_ROLE_ID),
        mappings=active,
    )
    assert both.guild_council and both.platform_administrator
    assert both.capability is ActorCapability.GUILD_COUNCIL


def test_a_non_member_resolves_to_nothing_whatever_roles_the_cache_holds(
    migrated_database, callers
):
    """Membership is the gate, and a cached role set does not open it.

    A projection that says `is_member = false` while still listing roles is exactly
    what a revocation looks like in the cache for up to N-09 seconds. It must confer
    nothing, or the cache would be authorization rather than display data.
    """
    resolved = resolve_capabilities(
        account_id=callers["N"].account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        membership=projection(COUNCIL_ROLE_ID, BOOTSTRAP_ADMIN_ROLE_ID, is_member=False),
        mappings=mappings_for(migrated_database),
    )
    assert not resolved.guild_member
    assert not resolved.guild_council
    assert not resolved.platform_administrator


# ---------------------------------------------------------------------------
# TC-CAP-03 / TC-CAP-05 — the protected bootstrap mapping
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("statement", "label"),
    [
        ("UPDATE role_capability_mappings SET active = false WHERE protected", "deactivate"),
        (
            "UPDATE role_capability_mappings SET capability = 'guild_member' WHERE protected",
            "demote",
        ),
        ("UPDATE role_capability_mappings SET protected = false WHERE protected", "unprotect"),
        ("DELETE FROM role_capability_mappings WHERE protected", "delete"),
        (
            "UPDATE role_capability_mappings SET role_id = 999999999999999999 WHERE protected",
            "repoint",
        ),
    ],
)
def test_the_protected_mapping_cannot_be_touched_with_the_application_bypassed(
    migrated_database, statement, label
):
    """TC-CAP-03. Five spellings of "take administrator away", all refused by the database.

    Issued as raw SQL, so the application is not involved at all. A protected mapping
    that only the service declined to change would be a protected mapping an
    `UPDATE` could unprotect — and the account it protects is the one that recovers
    the platform when everything else is broken.
    """
    before = rows(
        migrated_database,
        "SELECT id, role_id, capability, active, protected FROM "
        "role_capability_mappings WHERE protected",
    )
    assert len(before) == 1, "exactly one protected bootstrap mapping is expected"

    with pytest.raises(Exception) as refusal:
        with migrated_database.begin() as connection:
            connection.execute(text(statement))
    assert refusal.value is not None, label

    after = rows(
        migrated_database,
        "SELECT id, role_id, capability, active, protected FROM "
        "role_capability_mappings WHERE protected",
    )
    assert after == before, label


def test_a_second_protected_mapping_is_refused(migrated_database, callers):
    """TC-CAP-05, first half. One protected mapping, enforced by a partial unique index."""
    with pytest.raises(Exception) as refusal:
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO role_capability_mappings (id, guild_id, role_id, "
                    "capability, protected, active, created_by_account_id, "
                    "created_under_auth_method, created_under_scope, provenance, "
                    "reason, audit_correlation_id) VALUES (:id, :guild, :role, "
                    "'platform_administrator', true, true, :actor, 'discord_oauth', "
                    "'full', 'ordinary', 'a second protected mapping', :c)"
                ),
                {
                    "id": uuid4(),
                    "guild": TEST_GUILD_ID,
                    "role": SPARE_ROLE,
                    "actor": callers["A"].account_id,
                    "c": uuid4(),
                },
            )
    assert refusal.value is not None
    assert (
        count(migrated_database, "SELECT count(*) FROM role_capability_mappings WHERE protected")
        == 1
    )


def test_a_second_protected_account_is_refused(migrated_database, callers):
    """TC-CAP-05, second half. One protected account, for the same reason.

    `callers` has already created the protected account (the `BG` state is built on
    it), so this attempts the **second** one — which is the case the partial unique
    index `uq_platform_accounts_one_protected_admin` exists to refuse.
    """
    with pytest.raises(Exception) as refusal:
        with migrated_database.begin() as connection:
            make_account(connection, protected=True, label="a second protected account")
    assert refusal.value is not None


# ---------------------------------------------------------------------------
# TC-CAP-04 — union semantics: no ordinary change removes administrator
# ---------------------------------------------------------------------------


def test_no_sequence_of_ordinary_mapping_changes_removes_administrator_capability(
    migrated_database, callers
):
    """TC-CAP-04. Resolution is a **union** over the caller's mapped roles.

    So adding a mapping that confers something narrower, and revoking every
    *ordinary* mapping that happens to confer administrator, both leave the protected
    bootstrap mapping standing — and an administrator holding the bootstrap role still
    resolves to administrator. A resolution that took the "last" or the "most
    specific" mapping would be lockout-shaped, and this is what rules that out.
    """
    with migrated_database.begin() as connection:
        # A conflicting, narrower mapping on the very same role.
        add_mapping(
            connection,
            role_id=BOOTSTRAP_ADMIN_ROLE_ID,
            capability=ActorCapability.GUILD_MEMBER.value,
            created_by=callers["A"].account_id,
        )
        # And an ordinary administrator mapping elsewhere, which is then revoked.
        spare = add_mapping(
            connection,
            role_id=SPARE_ROLE,
            capability=ActorCapability.PLATFORM_ADMINISTRATOR.value,
            created_by=callers["A"].account_id,
        )
    with migrated_database.begin() as connection:
        # `ck_role_capability_mappings_revocation_names_its_actor` requires the
        # revoker as well as the timestamp: a revocation attributed to nobody is a
        # revocation nobody can be asked about.
        connection.execute(
            text(
                "UPDATE role_capability_mappings SET active = false, revoked_at = now(), "
                "revoked_by_account_id = :actor, revoked_under_scope = 'full', "
                "revoked_under_auth_method = 'discord_oauth' "
                "WHERE id = :id"
            ),
            {"id": spare, "actor": callers["A"].account_id},
        )

    resolved = resolve_capabilities(
        account_id=callers["A"].account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        membership=projection(BOOTSTRAP_ADMIN_ROLE_ID),
        mappings=mappings_for(migrated_database),
    )
    assert resolved.platform_administrator, "the bootstrap mapping must still confer it"
    assert resolved.guild_member
    assert not resolved.guild_council


# ---------------------------------------------------------------------------
# TC-CAP-06 / TC-CAP-11 — one mapping event per attempt, applied or refused
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("capability", "expected_outcome"),
    [("dm", "applied"), ("guild_council", "applied"), ("nonsense", None)],
)
async def test_every_mapping_attempt_writes_exactly_one_event(
    client, settings, migrated_database, callers, capability, expected_outcome
):
    """TC-CAP-06 and TC-CAP-11. One row per attempt, carrying the whole decision.

    A refused attempt nobody can find afterwards is a refused attempt an incident
    review cannot see, so the event log records refusals as well as applications, with
    the operation, the outcome, the refusal code, the attempted capability, the
    authentication method, the scope and the correlation id.

    `nonsense` never reaches the service — the route refuses an unknown capability as
    input validation, `422` — so it writes **no** event, and that is the correct
    behaviour rather than a gap: nothing was attempted against the mapping table.
    """
    admin = callers["A"]
    with migrated_database.begin() as connection:
        connection.execute(text("TRUNCATE TABLE role_capability_mapping_events"))

    response = await client.post(
        "/v1/admin/role-capabilities",
        cookies=admin.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=(
            f"csrf_token={csrf_token_for(settings, admin)}&role_id={SPARE_ROLE}"
            f"&capability={capability}&reason=administrator+mapped+a+role"
        ),
    )
    events = rows(
        migrated_database,
        "SELECT operation, outcome, capability, refusal_code, auth_method, scope, "
        "correlation_id, role_id FROM role_capability_mapping_events",
    )

    if expected_outcome is None:
        assert response.status_code == 422
        assert events == []
        return

    assert response.status_code == 303
    assert len(events) == 1
    assert events[0]["operation"] == "create"
    assert events[0]["outcome"] == expected_outcome
    assert events[0]["capability"] == capability
    assert events[0]["refusal_code"] is None
    assert events[0]["auth_method"] == "discord_oauth"
    assert events[0]["scope"] == "full"
    assert events[0]["role_id"] == SPARE_ROLE
    assert events[0]["correlation_id"] is not None


def test_the_mapping_event_log_is_append_only(migrated_database, callers):
    """A log an application can edit is not a log. Asserted with raw SQL.

    Migration 0002's trigger refuses `UPDATE` and `DELETE` on the append-only tables
    for the schema owner too; the disposable test database is reset with `TRUNCATE`,
    which the trigger deliberately does not cover and the runtime role is denied by
    grant instead.
    """
    with migrated_database.begin() as connection:
        add_mapping(
            connection,
            role_id=DM_ROLE,
            capability=ActorCapability.DM.value,
            created_by=callers["A"].account_id,
        )
        connection.execute(
            text(
                "INSERT INTO role_capability_mapping_events (id, operation, outcome, "
                "guild_id, role_id, capability, actor_account_id, auth_method, scope, "
                "reason, correlation_id) VALUES (:id, 'create', 'applied', :guild, "
                ":role, 'dm', :actor, 'discord_oauth', 'full', 'seeded', :c)"
            ),
            {
                "id": uuid4(),
                "guild": TEST_GUILD_ID,
                "role": DM_ROLE,
                "actor": callers["A"].account_id,
                "c": uuid4(),
            },
        )

    for statement in (
        "UPDATE role_capability_mapping_events SET outcome = 'refused'",
        "DELETE FROM role_capability_mapping_events",
    ):
        with pytest.raises(Exception):
            with migrated_database.begin() as connection:
                connection.execute(text(statement))


# ---------------------------------------------------------------------------
# TC-CAP-08 — administrator scope resolution, parametrized
# ---------------------------------------------------------------------------


def test_administrator_scope_resolution(migrated_database, callers):
    """TC-CAP-08. Four cases, and the fourth overrides the other three.

    | Authority from | Scope |
    |---|---|
    | the protected mapping | `full` |
    | only an emergency-provenance mapping | `emergency_continuity` |
    | both | `full` |
    | a break-glass session, whatever its mappings say | `emergency_continuity` |

    The last row is why the scope is not simply a property of the mappings: a
    break-glass session is continuity-scoped because of **how it authenticated**, and
    a session that inherited `full` from a mapping would convert a temporary
    authentication event into a permanent authority.
    """
    with migrated_database.begin() as connection:
        emergency_role = 900000000000000061
        add_mapping(
            connection,
            role_id=emergency_role,
            capability=ActorCapability.PLATFORM_ADMINISTRATOR.value,
            created_by=callers["A"].account_id,
            scope="emergency_continuity",
            auth_method="webauthn",
        )
    active = mappings_for(migrated_database)

    protected_only = resolve_capabilities(
        account_id=callers["A"].account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        membership=projection(BOOTSTRAP_ADMIN_ROLE_ID),
        mappings=active,
    )
    assert protected_only.administrator_scope is AdministratorScope.FULL

    emergency_only = resolve_capabilities(
        account_id=callers["A"].account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        membership=projection(emergency_role),
        mappings=active,
    )
    assert emergency_only.administrator_scope is AdministratorScope.EMERGENCY_CONTINUITY
    assert emergency_only.is_continuity_scoped

    both = resolve_capabilities(
        account_id=callers["A"].account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        membership=projection(BOOTSTRAP_ADMIN_ROLE_ID, emergency_role),
        mappings=active,
    )
    assert both.administrator_scope is AdministratorScope.FULL
    assert not both.is_continuity_scoped

    break_glass = resolve_capabilities(
        account_id=callers["BG"].account_id,
        auth_method=AuthMethod.WEBAUTHN,
        membership=None,
        mappings=(),
    )
    assert break_glass.administrator_scope is AdministratorScope.EMERGENCY_CONTINUITY
    assert break_glass.capabilities == frozenset(
        {ActorCapability.PLATFORM_ADMINISTRATOR}
    )


def test_a_break_glass_session_resolves_to_administrator_alone_even_holding_council(
    migrated_database, callers
):
    """TC-BG-04's resolution half, restated where scope is decided.

    The break-glass account's Discord roles are irrelevant: the session never touches
    the projection (route contract §7.3), so a person who is also a Council member
    gets `{platform_administrator}` and nothing else while authenticated that way.
    """
    resolved = resolve_capabilities(
        account_id=callers["BG"].account_id,
        auth_method=AuthMethod.WEBAUTHN,
        membership=projection(COUNCIL_ROLE_ID, BOOTSTRAP_ADMIN_ROLE_ID),
        mappings=mappings_for(migrated_database),
    )
    assert resolved.capabilities == frozenset(
        {ActorCapability.PLATFORM_ADMINISTRATOR}
    )
    assert not resolved.guild_council


# ---------------------------------------------------------------------------
# TC-CAP-10 — ratification restores full scope
# ---------------------------------------------------------------------------


def test_ratification_restores_full_scope_and_changes_the_privilege_fingerprint(
    migrated_database, callers
):
    """TC-CAP-10. The scope changes, and N-08's rotation trigger notices.

    Ratification can change an account's scope without changing its capability *set*,
    so the fingerprint has to include the scope or the affected sessions would carry
    the old scope to their next request. That is why `privilege_fingerprint` is over
    the capabilities, guild membership **and** the administrator scope, and this is the
    assertion that keeps it so.
    """
    emergency_role = 900000000000000071
    with migrated_database.begin() as connection:
        mapping_id = add_mapping(
            connection,
            role_id=emergency_role,
            capability=ActorCapability.PLATFORM_ADMINISTRATOR.value,
            created_by=callers["A"].account_id,
            scope="emergency_continuity",
            auth_method="webauthn",
        )

    before = resolve_capabilities(
        account_id=callers["A"].account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        membership=projection(emergency_role),
        mappings=mappings_for(migrated_database),
    )
    assert before.administrator_scope is AdministratorScope.EMERGENCY_CONTINUITY

    with migrated_database.begin() as connection:
        RoleMappingService(
            role_mappings=RoleMappingRepository(connection),
            audit=WebAuditRepository(connection),
        ).ratify(
            context=resolve_capabilities(
                account_id=callers["A"].account_id,
                auth_method=AuthMethod.DISCORD_OAUTH,
                membership=projection(BOOTSTRAP_ADMIN_ROLE_ID),
                mappings=RoleMappingRepository(connection).active_mappings(TEST_GUILD_ID),
            ),
            mapping_id=mapping_id,
            expected_version=0,
            reason="ratified after the incident",
            correlation_id=uuid4(),
            now=utcnow(),
        )

    after = resolve_capabilities(
        account_id=callers["A"].account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        membership=projection(emergency_role),
        mappings=mappings_for(migrated_database),
    )
    assert after.administrator_scope is AdministratorScope.FULL
    assert after.capabilities == before.capabilities, (
        "the capability set is unchanged — which is exactly why the fingerprint must "
        "carry the scope"
    )
    assert after.privilege_fingerprint != before.privilege_fingerprint

    provenance = count(
        migrated_database,
        "SELECT provenance FROM role_capability_mappings WHERE id = :id",
        id=mapping_id,
    )
    assert provenance != MappingProvenance.EMERGENCY_CONTINUITY.value


def test_ratification_is_one_way(migrated_database, callers):
    """The exit is one-way, and the database is what makes it so.

    Once ratified, a mapping cannot be returned to emergency provenance — not by the
    service and not by an `UPDATE`. A reversible exit would be a way to re-enter the
    emergency surface from outside an emergency.
    """
    emergency_role = 900000000000000081
    with migrated_database.begin() as connection:
        mapping_id = add_mapping(
            connection,
            role_id=emergency_role,
            capability=ActorCapability.PLATFORM_ADMINISTRATOR.value,
            created_by=callers["A"].account_id,
            scope="emergency_continuity",
            auth_method="webauthn",
        )
    with migrated_database.begin() as connection:
        connection.execute(
            text(
                "UPDATE role_capability_mappings SET provenance = 'ordinary', "
                "ratified_at = now(), ratified_by_account_id = :actor WHERE id = :id"
            ),
            {"actor": callers["A"].account_id, "id": mapping_id},
        )
    with pytest.raises(Exception):
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    "UPDATE role_capability_mappings SET provenance = "
                    "'emergency_continuity' WHERE id = :id"
                ),
                {"id": mapping_id},
            )


# ---------------------------------------------------------------------------
# TC-CAP-07 — forged capability and role values change nothing
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "body",
    [
        "role_id=0&capability=platform_administrator",
        "role_id=-1&capability=platform_administrator",
        "role_id=not-a-snowflake&capability=platform_administrator",
        "role_id=900000000000000091&capability=guild_council; DROP TABLE characters",
        "role_id=900000000000000091&capability=system",
        "role_id=900000000000000091&capability=",
    ],
)
async def test_a_forged_capability_or_role_id_changes_nothing(
    client, settings, migrated_database, callers, body
):
    """TC-CAP-07. Refused as input, `422`, with no row and no event.

    `system` is the interesting one: it is a real `ActorCapability` and is **not** in
    `MAPPABLE_CAPABILITIES`, so the route refuses it as an unknown capability rather
    than mapping a role to the platform's own internal authority.
    """
    admin = callers["A"]
    before = count(migrated_database, "SELECT count(*) FROM role_capability_mappings")
    response = await client.post(
        "/v1/admin/role-capabilities",
        cookies=admin.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, admin)}&{body}&reason=forged",
    )
    assert response.status_code == 422, body
    assert (
        count(migrated_database, "SELECT count(*) FROM role_capability_mappings") == before
    )
    assert count(migrated_database, "SELECT count(*) FROM characters") == 0
