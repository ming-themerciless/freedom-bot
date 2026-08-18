"""TC-BG-05b/c/e's direct-HTTP portions and TC-CAP-09, against the real P3.2 routes.

Delivery plan §11 and the OD-45 allocation make these blocking P3.G2 evidence: the
service and database portions were accepted at P3.G1, and the HTTP portions were
explicitly **not** waived — they had to run against the real R-33, R-34 and R-38
handlers, which did not exist until this package built them.

The question all of it answers is one question, from three directions: **no sequence
of break-glass actions followed by an ordinary login yields Council or import
authority.** Emergency administration exists so that an administrator locked out of
Discord can repair the mapping that locked them out (OD-43). It does not exist to
mint game-governance authority, and the attack it must refuse is not "what can this
emergency session do now?" — it is "what can this emergency session arrange for a
later, ordinary session?". That is why the withdrawn TC-BG-05 was wrong and why
05c below logs in *again* before asserting anything.

Every request is issued directly with a valid synchronizer token, never by
rendering R-32 first (route contract §2.2, TC-OBJ-06). A `403` obtained by never
having been offered the control would prove nothing.
"""
from __future__ import annotations

import pytest
from sqlalchemy import text

from adapters.web.portal_routes import GUARDS, P3_2_ROUTE_INVENTORY
from application.audit import ActorCapability
from tests.web.conftest import add_mapping, link_discord, make_account, seed_membership
from tests.web.portal_fixtures import (
    CONTINUITY_ROLE_ID,
    clean_p3_2_tables,
    csrf_token_for,
    grant_link,
    make_character,
    seed_callers,
)
from tests.web_fixtures import PUBLIC_ORIGIN

pytestmark = pytest.mark.database

FORM = "application/x-www-form-urlencoded"

#: The four capabilities N-67 keeps out of a continuity-scoped caller's reach. Only
#: `platform_administrator` is allowed, because repairing the administrator mapping
#: is the whole purpose of the surface.
FORBIDDEN_CAPABILITIES = ["guild_council", "dm", "character_owner", "guild_member"]

#: A role nobody maps yet, used as the target of an attempted mapping.
ATTEMPTED_ROLE_ID = 900000000000000041
#: The role a break-glass session legitimately maps to `platform_administrator`.
REPAIRED_ROLE_ID = 900000000000000042
#: The member who holds it, and who logs in ordinarily afterwards.
REPAIRED_MEMBER_SUBJECT = 700000000000008001


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


@pytest.fixture()
def character(migrated_database, callers):
    with migrated_database.begin() as connection:
        character_id = make_character(connection, display_name="Alia Storm")
        grant_link(
            connection,
            character_id=character_id,
            account_id=callers["M"].account_id,
            granted_by=callers["C"].account_id,
            default_character=True,
        )
    return character_id


async def issue(client, settings, caller, method, path):
    cookies = caller.cookies(settings)
    if method == "GET":
        return await client.get(path, cookies=cookies)
    body = "reason=probe&version=0&role_id=1&capability=guild_council"
    if caller.session_id is not None:
        body = f"csrf_token={csrf_token_for(settings, caller)}&{body}"
    return await client.post(
        path,
        cookies=cookies,
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=body,
    )


def concrete(path, character_id):
    return (
        path.replace("{character_id}", str(character_id))
        .replace("{access_id}", "00000000-0000-4000-8000-000000000001")
        .replace("{mapping_id}", "00000000-0000-4000-8000-000000000002")
        .replace("{proposal_id}", "00000000-0000-4000-8000-000000000003")
        .replace("{identity_id}", "00000000-0000-4000-8000-000000000004")
    )


def rows(engine, statement, **parameters):
    with engine.begin() as connection:
        return connection.execute(text(statement), parameters).mappings().all()


def count(engine, statement, **parameters):
    with engine.begin() as connection:
        return connection.execute(text(statement), parameters).scalar()


# ---------------------------------------------------------------------------
# TC-CAP-09 — `AC` mirrors `BG` cell for cell
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("route", sorted(P3_2_ROUTE_INVENTORY))
async def test_ac_answers_exactly_what_bg_answers_on_every_route(
    client, settings, callers, character, route
):
    """TC-CAP-09. The eighth caller state has no matrix column, so this is its column.

    Route contract §3.3 says every `BG` cell applies unchanged to `AC`. Leaving that
    to the rule alone would let a route drift apart from it and still pass a reading,
    so the whole inventory is re-run for a continuity-scoped **ordinary-provider**
    session and each response is compared to the break-glass one.

    `AC` is the state that has to be built rather than described: `auth_method` is
    `discord_oauth`, the membership projection is real, and the only thing making it
    continuity-scoped is that every mapping conferring `platform_administrator` on it
    was created under an emergency scope. A double would prove nothing about it.
    """
    method, path = P3_2_ROUTE_INVENTORY[route]
    target = concrete(path, character)

    break_glass = await issue(client, settings, callers["BG"], method, target)
    continuity = await issue(client, settings, callers["AC"], method, target)

    assert continuity.status_code == break_glass.status_code, (
        f"{route}: BG got {break_glass.status_code}, AC got {continuity.status_code}"
    )
    # For a refusal, the code as well as the status: two different `403`s would
    # satisfy an equality on the status alone while meaning different things.
    if break_glass.headers.get("content-type", "").startswith("application/json"):
        assert continuity.json() == break_glass.json(), route


async def test_the_continuity_surface_is_exactly_n_65_s(client, settings, callers, character):
    """N-65's surface, read off the running application rather than the guard table.

    R-32, R-33, R-34 and R-35 and nothing else. **R-38 is deliberately outside it**:
    ratification is the door between emergency and ordinary authority, and a session
    on the emergency side does not hold the handle.
    """
    # Classified by **refusal code**, not by status. `emergency_surface_refused` is
    # N-65 — "this route is outside the surface" — while `emergency_scope_refused` is
    # N-67, one level down: the route *was* reached and the capability it was asked
    # for is not on the allowlist. Both are `403`, and treating them alike would put
    # R-33 outside the surface it defines, because the probe body deliberately asks
    # for a capability N-67 forbids.
    reachable = set()
    for route, (method, path) in P3_2_ROUTE_INVENTORY.items():
        response = await issue(
            client, settings, callers["BG"], method, concrete(path, character)
        )
        surface_refused = response.headers.get("content-type", "").startswith(
            "application/json"
        ) and response.json().get("error") == "emergency_surface_refused"
        rendered_refusal = (
            response.status_code == 403
            and not response.headers.get("content-type", "").startswith(
                "application/json"
            )
        )
        if not surface_refused and not rendered_refusal and response.status_code != 401:
            reachable.add(route)
    assert reachable == {"R-32", "R-33", "R-34", "R-35"}
    assert "R-38" not in reachable
    # And the guard table says the same thing, so the transcription is checked.
    assert {route for route, guard in GUARDS.items() if guard.continuity_allowed} == (
        reachable
    )


# ---------------------------------------------------------------------------
# TC-BG-05b — the direct-HTTP portion, against the real handlers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("capability", FORBIDDEN_CAPABILITIES)
@pytest.mark.parametrize("state", ["BG", "AC"])
async def test_a_continuity_caller_cannot_create_a_mapping_outside_n_67(
    client, settings, migrated_database, callers, capability, state
):
    """TC-BG-05b, HTTP portion. `403`, no row, and a refusal event that names the attempt.

    Issued straight to R-33 **without ever rendering R-32**. The route enforces none
    of N-67 itself: the service refuses before any row is read or written and records
    the attempt, and the check constraint refuses the insert regardless of what the
    service decided. Three controls, and the route is not one of them — which is
    exactly why the request can be made without the page and still be refused.
    """
    caller = callers[state]
    response = await client.post(
        "/v1/admin/role-capabilities",
        cookies=caller.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=(
            f"csrf_token={csrf_token_for(settings, caller)}"
            f"&role_id={ATTEMPTED_ROLE_ID}&capability={capability}"
            "&reason=attempted+during+an+incident"
        ),
    )
    assert response.status_code == 403, capability
    assert response.json() == {"error": "emergency_scope_refused"}
    assert (
        count(
            migrated_database,
            "SELECT count(*) FROM role_capability_mappings WHERE role_id = :role",
            role=ATTEMPTED_ROLE_ID,
        )
        == 0
    )
    # The refusal is recorded in the append-only mapping-event log, naming the
    # capability that was attempted. A refused attempt nobody can find afterwards is
    # a refused attempt an incident review cannot see.
    events = rows(
        migrated_database,
        "SELECT operation, outcome, capability, refusal_code FROM "
        "role_capability_mapping_events WHERE capability = :capability "
        "AND role_id = :role",
        capability=capability,
        role=ATTEMPTED_ROLE_ID,
    )
    assert events, capability
    assert {row["outcome"] for row in events} == {"refused"}
    assert {row["refusal_code"] for row in events} == {"emergency_scope_refused"}


@pytest.mark.parametrize("state", ["BG", "AC"])
async def test_a_continuity_caller_cannot_revoke_a_council_mapping(
    client, settings, migrated_database, callers, state
):
    """TC-BG-05b's R-34 half: revoking Council's mapping is a Council-shaped act.

    The mapping the Council caller depends on already exists (the fixture creates
    it). A continuity-scoped administrator may revoke a `platform_administrator`
    mapping — that is the repair the surface exists for — and nothing else.
    """
    mapping_id = count(
        migrated_database,
        "SELECT id FROM role_capability_mappings WHERE capability = 'guild_council' "
        "AND active",
    )
    caller = callers[state]
    response = await client.post(
        f"/v1/admin/role-capabilities/{mapping_id}/revoke",
        cookies=caller.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=(
            f"csrf_token={csrf_token_for(settings, caller)}&version=0"
            "&reason=attempted+during+an+incident"
        ),
    )
    assert response.status_code == 403
    assert (
        count(
            migrated_database,
            "SELECT active FROM role_capability_mappings WHERE id = :id",
            id=mapping_id,
        )
        is True
    )


@pytest.mark.parametrize("state", ["BG", "AC"])
async def test_a_continuity_caller_cannot_ratify(
    client, settings, migrated_database, callers, state
):
    """TC-BG-05e's HTTP portion, refusal side. `403` from the guard, before the body.

    Ratification is the one exit from emergency-derived authority and it is one-way.
    `FULL_ADMINISTRATOR` demands `discord_oauth` **and** scope `full`, so both
    continuity states are refused before the handler runs. A `403` here during an
    incident is the boundary, not a defect to work around: ratification waits until
    an administrator can authenticate normally — which the success case in
    `test_p3_2_success_cells.py` proves works.
    """
    with migrated_database.begin() as connection:
        mapping_id = add_mapping(
            connection,
            role_id=900000000000000043,
            capability=ActorCapability.PLATFORM_ADMINISTRATOR.value,
            created_by=callers["A"].account_id,
            scope="emergency_continuity",
            auth_method="webauthn",
        )
    caller = callers[state]
    response = await client.post(
        f"/v1/admin/role-capabilities/{mapping_id}/ratify",
        cookies=caller.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=(
            f"csrf_token={csrf_token_for(settings, caller)}&version=0"
            "&reason=ratifying+my+own+mapping"
        ),
    )
    assert response.status_code == 403
    assert (
        count(
            migrated_database,
            "SELECT ratified_at FROM role_capability_mappings WHERE id = :id",
            id=mapping_id,
        )
        is None
    )


# ---------------------------------------------------------------------------
# TC-BG-05c — the sequence, end to end, through HTTP
# ---------------------------------------------------------------------------


async def test_no_break_glass_sequence_yields_council_authority_for_a_later_login(
    client, settings, migrated_database, callers, character
):
    """TC-BG-05c's P3.G2 half, and the reason the withdrawn TC-BG-05 was wrong.

    The sequence, in order:

    1. a break-glass session creates the one mapping it *is* allowed — role X to
       `platform_administrator` — through the real R-33;
    2. a member holding role X logs in **ordinarily**, so the session is
       `discord_oauth` and the membership projection is real;
    3. their administrator authority descends only from an emergency-provenance
       mapping, so they resolve to `emergency_continuity` scope — caller state `AC`;
    4. and from there, every Council route, R-38 and an R-33 attempt for
       `guild_council` are refused, and no import exists.

    Step 2 is the step the withdrawn test omitted. It asked what the emergency
    session could do and answered "not much", which was true and irrelevant: the
    attack arranges authority for a *later* session, and the platform was escalatable
    while that test passed.
    """
    # 1. The allowed repair, through the route, with no page rendered first.
    break_glass = callers["BG"]
    created = await client.post(
        "/v1/admin/role-capabilities",
        cookies=break_glass.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=(
            f"csrf_token={csrf_token_for(settings, break_glass)}"
            f"&role_id={REPAIRED_ROLE_ID}&capability=platform_administrator"
            "&reason=repairing+the+administrator+mapping+during+an+outage"
        ),
    )
    assert created.status_code == 303
    repaired = rows(
        migrated_database,
        "SELECT provenance, created_under_scope, created_under_auth_method FROM "
        "role_capability_mappings WHERE role_id = :role",
        role=REPAIRED_ROLE_ID,
    )
    assert len(repaired) == 1
    # The provenance is the whole mechanism: it is what makes the *next* session
    # continuity-scoped rather than fully authorized.
    assert repaired[0]["provenance"] == "emergency_continuity"
    assert repaired[0]["created_under_auth_method"] == "webauthn"

    # 2 and 3. An ordinary login by a member holding that role.
    from tests.web.portal_fixtures import _build
    from application.web.capabilities import AuthMethod

    with migrated_database.begin() as connection:
        pass
    later = _build(
        migrated_database,
        settings,
        "AC",
        REPAIRED_MEMBER_SUBJECT,
        frozenset({REPAIRED_ROLE_ID}),
        AuthMethod.DISCORD_OAUTH,
    )

    # The session is an ordinary one, not a break-glass one. Asserted from the row,
    # so the case cannot be satisfied by having built the wrong state.
    assert (
        count(
            migrated_database,
            "SELECT auth_method FROM sessions WHERE id = :id",
            id=later.session_id,
        )
        == "discord_oauth"
    )

    # 4. And it is confined to N-65's surface exactly as a break-glass session is.
    for route in ("R-22", "R-23", "R-24", "R-25", "R-28", "R-29", "R-30", "R-38"):
        method, path = P3_2_ROUTE_INVENTORY[route]
        response = await issue(client, settings, later, method, concrete(path, character))
        assert response.status_code in {401, 403}, f"{route}: {response.status_code}"

    attempted = await client.post(
        "/v1/admin/role-capabilities",
        cookies=later.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=(
            f"csrf_token={csrf_token_for(settings, later)}"
            f"&role_id={ATTEMPTED_ROLE_ID}&capability=guild_council"
            "&reason=escalating+after+the+repair"
        ),
    )
    assert attempted.status_code == 403
    assert attempted.json() == {"error": "emergency_scope_refused"}
    assert (
        count(
            migrated_database,
            "SELECT count(*) FROM role_capability_mappings WHERE "
            "capability = 'guild_council' AND role_id = :role",
            role=ATTEMPTED_ROLE_ID,
        )
        == 0
    )
    # No import authority was acquired either. P3.2 builds no import route, so the
    # assertion is that the applied-input uniqueness key shows nothing — the same
    # statement TC-BG-05c makes, in the package that owns the table.
    assert count(migrated_database, "SELECT count(*) FROM snapshot_imports") == 0

    # And the ordinary member's own reach is unchanged: they never gained Council.
    assert (
        count(
            migrated_database,
            "SELECT count(*) FROM character_access WHERE platform_account_id = :account",
            account=later.account_id,
        )
        == 0
    )


async def test_a_continuity_caller_sees_only_the_allowlisted_capability_offered(
    client, settings, callers
):
    """The rendering agrees with the refusal, and the refusal does not depend on it.

    R-32 offers a continuity-scoped administrator exactly `platform_administrator`,
    and says so with a scope notice. That is a courtesy: R-33 refuses everything else
    whether or not this page was ever fetched, which the cases above establish by
    never fetching it.
    """
    response = await client.get(
        "/v1/admin/role-capabilities", cookies=callers["BG"].cookies(settings)
    )
    assert response.status_code == 200
    assert "emergency_continuity_allowlist" in response.text
    for capability in FORBIDDEN_CAPABILITIES:
        assert f'value="{capability}"' not in response.text
