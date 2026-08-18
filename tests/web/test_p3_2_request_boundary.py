"""F3: the mutation preamble's order, asserted by what a refused request did not do.

Route contract §2.1 numbers the chain, and the numbers are a claim about *order*:

    session (4) → origin (5) → CSRF (6) → capability resolution (7) →
    capability decision (7) → object (8) → application service (9)

The reviewed implementation ran 5 and 6 **after** 7. `enter()` refreshed the
membership projection — a network call to Discord and a database write — resolved
capability and took the authorization decision, and only then did
`enter_mutation()` parse the body and verify the synchronizer token on top of the
value `enter()` had returned. A cross-site request from a logged-in Council
member's browser was therefore cheap to make and drove real provider I/O and a real
projection write before anything looked at the token.

Asserting an order is awkward: a passing request performs every step, so the order
is invisible in the success case. What makes it observable is a request that is
refused **in the middle**, and then asking what the steps after the refusal left
behind. Every case below arranges a request for which step 7 genuinely would have
called Discord — a projection past N-09 and a live, correctly bound token grant —
and then asserts, for an invalid token:

- the provider was not called at all (`provider.verify_calls` is empty);
- the projection was not rewritten (its `observed_at` is unchanged);
- no application service ran (each is replaced by a tripwire);
- no state changed and no success audit event was written.

`test_a_valid_token_does_reach_the_provider` is the falsification control: without
it, every assertion above would also pass against a request that never planned a
refresh in the first place, and the suite would be measuring nothing.
"""
from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import text

from application.web.character_access import CharacterAccessService
from application.web.identity_evidence import IdentityMigrationService
from application.web.role_mappings import RoleMappingService
from tests.web.conftest import make_account, utcnow
from tests.web.portal_fixtures import (
    COUNCIL_SUBJECT,
    MEMBER_SUBJECT,
    character_version,
    clean_p3_2_tables,
    csrf_token_for,
    grant_link,
    make_character,
    seed_callers,
    seed_token_grant,
    stale_membership,
)
from tests.web_fixtures import COUNCIL_ROLE_ID, PUBLIC_ORIGIN

pytestmark = pytest.mark.database

FORM = "application/x-www-form-urlencoded"


@pytest.fixture(autouse=True)
def clean_between_cases(request):
    yield
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)


@pytest.fixture()
def tripwires(monkeypatch):
    """Replace every P3.2 application service the mutations use with a tripwire.

    A service that is *called* fails the test where it is called, rather than the
    test having to infer from an absent row that nothing ran. The distinction
    matters: a service that ran and then rolled back leaves no row either, and
    "the service never ran" is the property step 6 is supposed to deliver.
    """
    calls: list[str] = []

    def forbid(name):
        def called(*_arguments, **_keywords):
            calls.append(name)
            raise AssertionError(f"{name} ran for a request refused before step 9")

        return called

    for service, method in (
        (CharacterAccessService, "grant"),
        (CharacterAccessService, "revoke"),
        (CharacterAccessService, "set_default"),
        (IdentityMigrationService, "confirm"),
        (IdentityMigrationService, "reject"),
        (RoleMappingService, "create"),
        (RoleMappingService, "revoke"),
        (RoleMappingService, "ratify"),
    ):
        monkeypatch.setattr(
            service, method, forbid(f"{service.__name__}.{method}"), raising=True
        )
    return calls


@pytest.fixture()
def refreshing_council(migrated_database, settings, composition, provider):
    """A Council caller whose next request *must* ask Discord, and a target.

    Three arrangements, each load-bearing:

    1. the membership projection is backdated past N-09, so `open_request()` plans
       a refresh rather than answering from cache;
    2. a live token grant exists and opens under the composition's own envelope, so
       the refresh has something to ask with — without one, `_refresh_plan` returns
       `None` and no call would happen for a reason that has nothing to do with
       CSRF;
    3. the provider double answers as this caller, holding the Council role, so the
       control case still authorizes and the ordering — rather than an incidental
       refusal — is what the refusal cases measure.
    """
    callers = seed_callers(migrated_database, settings, states=("C", "M"))
    provider.subject = str(COUNCIL_SUBJECT)
    provider.role_ids = frozenset({COUNCIL_ROLE_ID})

    with migrated_database.begin() as connection:
        character_id = make_character(connection, display_name="Alia Storm")
        member_account = make_account(connection, label="link-target")
        identity_id = connection.execute(
            text(
                "SELECT id FROM external_identities WHERE provider_key = 'discord' "
                "AND subject = :subject"
            ),
            {"subject": str(COUNCIL_SUBJECT)},
        ).scalar_one()
        seed_token_grant(composition, connection, identity_id=identity_id)
        stale_membership(connection, subject=COUNCIL_SUBJECT)
        stale_membership(connection, subject=MEMBER_SUBJECT)
        observed_at = connection.execute(
            text(
                "SELECT observed_at FROM discord_guild_memberships "
                "WHERE discord_user_id = :subject"
            ),
            {"subject": COUNCIL_SUBJECT},
        ).scalar_one()

    return {
        "callers": callers,
        "character_id": character_id,
        "member_account": member_account,
        "observed_at": observed_at,
    }


def projection_observed_at(engine, subject):
    with engine.begin() as connection:
        return connection.execute(
            text(
                "SELECT observed_at FROM discord_guild_memberships "
                "WHERE discord_user_id = :subject"
            ),
            {"subject": subject},
        ).scalar_one()


def count(engine, statement, **parameters):
    with engine.begin() as connection:
        return connection.execute(text(statement), parameters).scalar()


async def grant_request(client, settings, caller, character_id, account_subject, *, body):
    return await client.post(
        f"/v1/council/characters/{character_id}/links",
        cookies=caller.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=body,
    )


# ---------------------------------------------------------------------------
# The control: a valid token does reach the provider
# ---------------------------------------------------------------------------


async def test_a_valid_token_does_reach_the_provider(
    client, settings, migrated_database, provider, refreshing_council
):
    """Falsification control. Without this the suite would prove nothing.

    Every case below asserts that an invalid token produced **no** provider call.
    That assertion is worthless unless a valid token on the same request produces
    one — otherwise the arrangement might simply never have planned a refresh, and
    "zero calls" would be a statement about the fixture rather than about the
    ordering.
    """
    caller = refreshing_council["callers"]["C"]
    token = csrf_token_for(settings, caller)
    response = await grant_request(
        client,
        settings,
        caller,
        refreshing_council["character_id"],
        None,
        body=(
            f"csrf_token={token}&subject={COUNCIL_SUBJECT}&access_kind=viewer"
            "&version=0&reason=the+control+case"
        ),
    )
    # The grant itself is refused `404` because this snowflake's account holds the
    # session rather than being a link target with an *active* identity for the
    # purpose — what matters here is that the request got **past** step 6 and the
    # provider was consulted at step 7.
    assert response.status_code in {303, 404}
    assert len(provider.verify_calls) == 1
    assert projection_observed_at(migrated_database, COUNCIL_SUBJECT) != (
        refreshing_council["observed_at"]
    )


# ---------------------------------------------------------------------------
# The finding: CSRF is refused before step 7
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("label", "body"),
    [
        ("absent", "subject=1&access_kind=viewer&version=0&reason=forged"),
        (
            "empty",
            "csrf_token=&subject=1&access_kind=viewer&version=0&reason=forged",
        ),
        (
            "another session's",
            "csrf_token=not-this-sessions-token&subject=1&access_kind=viewer"
            "&version=0&reason=forged",
        ),
    ],
)
async def test_an_invalid_token_is_refused_before_any_provider_call(
    client,
    settings,
    migrated_database,
    provider,
    refreshing_council,
    tripwires,
    label,
    body,
):
    """F3. The authorized caller: Council, on a Council route, refused at step 6.

    This is the case the reviewed order got wrong in the way that mattered. The
    caller *would* have been authorized, so every step after 6 would have run: the
    projection refresh, its database write, the capability resolution and the
    authorization decision. Now none of them does.
    """
    caller = refreshing_council["callers"]["C"]
    response = await grant_request(
        client, settings, caller, refreshing_council["character_id"], None, body=body
    )

    assert response.status_code == 403, label
    assert response.json() == {"error": "csrf_invalid"}
    # Step 7 never happened: no network call, and the projection is untouched.
    assert provider.verify_calls == [], label
    assert projection_observed_at(migrated_database, COUNCIL_SUBJECT) == (
        refreshing_council["observed_at"]
    )
    # Step 9 never happened either, and the tripwire says so rather than an
    # absent row implying it.
    assert tripwires == []
    assert count(migrated_database, "SELECT count(*) FROM character_access") == 0
    assert count(migrated_database, "SELECT count(*) FROM audit_events") == 0
    with migrated_database.begin() as connection:
        assert character_version(connection, refreshing_council["character_id"]) == 0


async def test_an_invalid_token_from_an_unauthorized_session_is_refused_identically(
    client, settings, migrated_database, provider, refreshing_council, tripwires
):
    """The same, for a caller the matrix would have refused anyway.

    A plain member on a Council route is `403` either way, so the *status* proves
    nothing here — what the case establishes is that the refusal happened at step 6
    rather than step 7, so an unauthorized cross-site request cannot be used to
    drive provider traffic or a projection write either. Both callers are refused by
    the same branch, before the platform does any work on their behalf.
    """
    caller = refreshing_council["callers"]["M"]
    before = projection_observed_at(migrated_database, MEMBER_SUBJECT)
    response = await grant_request(
        client,
        settings,
        caller,
        refreshing_council["character_id"],
        None,
        body="subject=1&access_kind=viewer&version=0&reason=forged",
    )
    assert response.status_code == 403
    assert response.json() == {"error": "csrf_invalid"}
    assert provider.verify_calls == []
    assert projection_observed_at(migrated_database, MEMBER_SUBJECT) == before
    assert tripwires == []
    assert count(migrated_database, "SELECT count(*) FROM character_access") == 0
    assert count(migrated_database, "SELECT count(*) FROM audit_events") == 0


async def test_a_valid_token_for_another_session_is_not_this_session_s_token(
    client, settings, migrated_database, provider, refreshing_council, tripwires
):
    """The token is bound to the session, so a real token from elsewhere is forged.

    A synchronizer token that verified against any session would be a token an
    attacker could obtain from their own login and replay against a victim's cookie.
    `csrf.issue` binds it to the session id, and this presents the member's genuine
    token on the Council caller's cookie.
    """
    council, member = (
        refreshing_council["callers"]["C"],
        refreshing_council["callers"]["M"],
    )
    response = await grant_request(
        client,
        settings,
        council,
        refreshing_council["character_id"],
        None,
        body=(
            f"csrf_token={csrf_token_for(settings, member)}&subject=1"
            "&access_kind=viewer&version=0&reason=forged"
        ),
    )
    assert response.status_code == 403
    assert response.json() == {"error": "csrf_invalid"}
    assert provider.verify_calls == []
    assert tripwires == []


# ---------------------------------------------------------------------------
# Steps 5 and 6 keep their relative order, and both precede step 7
# ---------------------------------------------------------------------------


async def test_a_cross_origin_mutation_is_refused_before_the_body_is_read(
    client, settings, migrated_database, provider, refreshing_council, tripwires
):
    """Step 5 precedes step 6, and both precede step 7.

    The request carries a **valid** token and a wrong `Origin`. It is refused
    `origin_invalid` rather than reaching the token check, which is the contract's
    order — the origin check is cheaper than a parse and cheaper than a network
    call — and the provider is still never asked.
    """
    caller = refreshing_council["callers"]["C"]
    response = await client.post(
        f"/v1/council/characters/{refreshing_council['character_id']}/links",
        cookies=caller.cookies(settings),
        headers={"Origin": "https://evil.example", "Content-Type": FORM},
        content=(
            f"csrf_token={csrf_token_for(settings, caller)}&subject=1"
            "&access_kind=viewer&version=0&reason=cross+origin"
        ),
    )
    assert response.status_code == 403
    assert response.json() == {"error": "origin_invalid"}
    assert provider.verify_calls == []
    assert tripwires == []


async def test_an_unauthenticated_mutation_answers_401_and_asks_nothing_else(
    client, settings, migrated_database, provider, refreshing_council, tripwires
):
    """Step 4 precedes step 5, so a session-less mutation does not leak its origin.

    `401` rather than `403 origin_invalid`: an unauthenticated caller learns that
    they are unauthenticated, and nothing about whether their origin would also have
    been wrong. A redirect would be worse still — the browser would follow it and
    the caller would have no way to tell the change was never applied.
    """
    response = await client.post(
        f"/v1/council/characters/{refreshing_council['character_id']}/links",
        headers={"Origin": "https://evil.example", "Content-Type": FORM},
        content="csrf_token=anything&subject=1&access_kind=viewer&version=0&reason=x",
    )
    assert response.status_code == 401
    assert response.json() == {"error": "not_authenticated"}
    assert provider.verify_calls == []
    assert tripwires == []


async def test_a_wrong_content_type_is_refused_415_before_the_token_check(
    client, settings, provider, refreshing_council, tripwires
):
    """The body bound is a boundary too: an unparsed body is not a verified one."""
    caller = refreshing_council["callers"]["C"]
    response = await client.post(
        f"/v1/council/characters/{refreshing_council['character_id']}/links",
        cookies=caller.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": "application/json"},
        content='{"csrf_token": "x"}',
    )
    assert response.status_code == 415
    assert provider.verify_calls == []
    assert tripwires == []


# ---------------------------------------------------------------------------
# Every P3.2 mutation goes through the one preamble
# ---------------------------------------------------------------------------

#: Every mutation in the P3.2 inventory, with a body that is well-formed apart
#: from the missing token. Parametrized from the route table so a mutation added
#: later without the preamble fails here rather than being covered by nothing.
MUTATIONS = [
    ("R-25", "/v1/council/characters/{character}/links"),
    ("R-26", "/v1/council/characters/{character}/links/{uuid}/revoke"),
    ("R-27", "/v1/council/characters/{character}/links/{uuid}/default"),
    ("R-29", "/v1/council/identity-migration/{uuid}/confirm"),
    ("R-30", "/v1/council/identity-migration/{uuid}/reject"),
    ("R-33", "/v1/admin/role-capabilities"),
    ("R-34", "/v1/admin/role-capabilities/{uuid}/revoke"),
    ("R-38", "/v1/admin/role-capabilities/{uuid}/ratify"),
    ("R-37", "/v1/account/identities/{uuid}/unlink"),
]


@pytest.mark.parametrize(("route", "path"), MUTATIONS)
async def test_every_mutation_refuses_a_missing_token_before_doing_anything(
    client,
    settings,
    migrated_database,
    provider,
    refreshing_council,
    tripwires,
    route,
    path,
):
    """`csrf_invalid` on all nine, with no provider call and no service call.

    Including the routes this caller would be refused on for a *different* reason —
    R-33, R-34 and R-38 are administrator routes and this caller is Council. The
    point is that the CSRF refusal comes first: an authorization refusal here would
    mean step 7 ran, which is what the finding was about.
    """
    caller = refreshing_council["callers"]["C"]
    concrete = path.format(
        character=refreshing_council["character_id"],
        uuid="00000000-0000-4000-8000-000000000009",
    )
    response = await client.post(
        concrete,
        cookies=caller.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content="version=0&reason=forged&role_id=1&capability=guild_council",
    )
    assert response.status_code == 403, route
    assert response.json() == {"error": "csrf_invalid"}, route
    assert provider.verify_calls == [], route
    assert tripwires == [], route
    assert count(migrated_database, "SELECT count(*) FROM audit_events") == 0, route


# ---------------------------------------------------------------------------
# The ordering is also a property of the source, and is asserted there
# ---------------------------------------------------------------------------


def test_the_preamble_performs_the_contract_s_steps_in_the_contract_s_order():
    """A structural guard over `_preamble`, so the order cannot drift back.

    The behavioural cases above are the real evidence. This one is cheap insurance
    against the specific regression: it reads the function's source and asserts that
    the CSRF verification appears **before** the provider observation and before
    `authorize`. A future edit that moved the block back would fail here without
    needing a database.
    """
    import inspect

    from adapters.web import portal_routes

    source = inspect.getsource(portal_routes.register)
    preamble = source.split("async def _preamble", 1)[1].split("async def enter", 1)[0]
    positions = {
        name: preamble.index(name)
        for name in (
            "_open",
            "_require_origin",
            "csrf.verify",
            "_observe_membership",
            "authorize(context, guard)",
        )
    }
    assert (
        positions["_open"]
        < positions["_require_origin"]
        < positions["csrf.verify"]
        < positions["_observe_membership"]
        < positions["authorize(context, guard)"]
    ), positions
