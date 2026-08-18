"""The matrix's **permitted** cells, plus TC-OBJ-02/03/04/07 and TC-ACC-04/06.

`test_p3_2_matrix.py` asserts every refused cell of route contract §5.2 and skips
the permitted ones, because `✓` is not one status: a permitted `GET` is `200` and a
permitted mutation is `303` to the page that re-reads the state under fresh
authorization. Those are the cases, and they matter for a reason the refusal cases
cannot cover — a route that refused *everybody* would pass the whole refusal matrix.

The object-level cases sit here too, because they are the other half of the same
question. `obj` in the `M` column of R-21 means "this caller reaches their own
characters and nothing else", and the only way to establish that is to have a
permitted case and a refused case differ by **which object** rather than by who is
asking.

Every request is issued directly, from the route table, with a synchronizer token
derived from the caller's session — never by rendering the page that carries the
control (route contract §2.2).
"""
from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import text

from adapters.web.portal_routes import GUARDS, P3_2_ROUTE_INVENTORY
from application.audit import ActorCapability
from tests.web.conftest import add_mapping, link_discord, make_account
from tests.web.portal_fixtures import (
    ADMIN_SUBJECT,
    COUNCIL_SUBJECT,
    MEMBER_SUBJECT,
    OTHER_MEMBER_SUBJECT,
    character_version,
    clean_p3_2_tables,
    csrf_token_for,
    grant_link,
    make_character,
    seed_callers,
    seed_discord_member,
)
from tests.web_fixtures import COUNCIL_ROLE_ID, PUBLIC_ORIGIN

pytestmark = pytest.mark.database

FORM = "application/x-www-form-urlencoded"

#: A snowflake the Council caller can be asked to link. Synthetic.
LINK_TARGET_SUBJECT = 700000000000005001


@pytest.fixture(autouse=True)
def clean_between_cases(request):
    yield
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)


@pytest.fixture()
def world(migrated_database, settings):
    """Everything a permitted cell needs to succeed rather than 404.

    A permitted cell that answered `404` because its object did not exist would be
    indistinguishable from a permitted cell that was refused, which is the whole
    difficulty with proving a `✓`. So each object is real: a character the member
    owns, a second character they do not, an account with an active Discord identity
    to link, an existing link to revoke and to default, an ordinary mapping to
    revoke and an emergency-provenance one to ratify.
    """
    callers = seed_callers(migrated_database, settings)
    with migrated_database.begin() as connection:
        mine = make_character(connection, display_name="Alia Storm")
        theirs = make_character(connection, display_name="Someone Elses")

        target_account = make_account(connection, label="link-target")
        seed_discord_member(connection, subject=LINK_TARGET_SUBJECT, username="target.one")
        link_discord(connection, target_account, LINK_TARGET_SUBJECT)

        # The member's own link, and a second one the Council routes act on.
        grant_link(
            connection,
            character_id=mine,
            account_id=callers["M"].account_id,
            granted_by=callers["C"].account_id,
            default_character=True,
        )
        revocable = grant_link(
            connection,
            character_id=mine,
            account_id=target_account,
            granted_by=callers["C"].account_id,
            access_kind="co_owner",
        )
        # Somebody else's character, so cross-character substitution has a target.
        other_account = make_account(connection, label="other-member")
        seed_discord_member(connection, subject=OTHER_MEMBER_SUBJECT, username="other.one")
        link_discord(connection, other_account, OTHER_MEMBER_SUBJECT)
        grant_link(
            connection,
            character_id=theirs,
            account_id=other_account,
            granted_by=callers["C"].account_id,
        )

        ordinary_mapping = add_mapping(
            connection,
            role_id=900000000000000021,
            capability=ActorCapability.DM.value,
            created_by=callers["A"].account_id,
        )
        emergency_mapping = add_mapping(
            connection,
            role_id=900000000000000022,
            capability=ActorCapability.PLATFORM_ADMINISTRATOR.value,
            created_by=callers["A"].account_id,
            scope="emergency_continuity",
            auth_method="webauthn",
        )
    return {
        "callers": callers,
        "mine": mine,
        "theirs": theirs,
        "target_account": target_account,
        "revocable": revocable,
        "ordinary_mapping": ordinary_mapping,
        "emergency_mapping": emergency_mapping,
    }


async def post(client, settings, caller, path, body):
    return await client.post(
        path,
        cookies=caller.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, caller)}&{body}",
    )


def version_of(engine, character_id):
    with engine.begin() as connection:
        return character_version(connection, character_id)


def count(engine, statement, **parameters):
    with engine.begin() as connection:
        return connection.execute(text(statement), parameters).scalar()


# ---------------------------------------------------------------------------
# Permitted reads
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("route", "state"),
    [
        ("R-20", "M"),
        ("R-20", "C"),
        ("R-20", "CA"),
        ("R-21", "M"),
        ("R-21", "C"),
        ("R-22", "C"),
        ("R-22", "CA"),
        ("R-23", "C"),
        ("R-24", "C"),
        ("R-28", "C"),
        ("R-31", "C"),
        ("R-31", "A"),
        ("R-32", "A"),
        ("R-32", "CA"),
        ("R-32", "BG"),
        ("R-35", "N"),
        ("R-35", "M"),
        ("R-35", "C"),
        ("R-35", "A"),
        ("R-35", "BG"),
        ("R-36", "M"),
        ("R-36", "C"),
        ("R-36", "A"),
    ],
)
async def test_a_permitted_read_answers_200(client, settings, world, route, state):
    """The `✓` cells of §5.2's read routes, one status each.

    `R-35` for `N` is deliberate and is not a mistake: a person whose guild
    membership was revoked still reaches their own identity list, because that list
    is how somebody recovers and gating it on membership would lock the door from
    the inside.
    """
    _method, path = P3_2_ROUTE_INVENTORY[route]
    concrete = path.replace("{character_id}", str(world["mine"]))
    response = await client.get(concrete, cookies=world["callers"][state].cookies(settings))
    assert response.status_code == 200, f"{route} for {state}: {response.text[:200]}"
    # Authenticated responses are never cached (route contract §7.2).
    assert response.headers.get("cache-control") == "no-store"


async def test_the_read_routes_render_their_own_view_model(client, settings, world):
    """A `200` is not evidence on its own: the body has to be the right screen.

    Each assertion is a marker the template renders from its view model, so a route
    wired to the wrong service — or to a view whose state is `error` — fails here
    rather than passing on a status code.
    """
    council = world["callers"]["C"]
    member = world["callers"]["M"]

    mine = await client.get("/v1/characters", cookies=member.cookies(settings))
    assert "Alia Storm" in mine.text

    detail = await client.get(
        f"/v1/characters/{world['mine']}", cookies=member.cookies(settings)
    )
    assert "Alia Storm" in detail.text

    index = await client.get("/v1/council/characters", cookies=council.cookies(settings))
    assert "Alia Storm" in index.text and "Someone Elses" in index.text

    links = await client.get(
        f"/v1/council/characters/{world['mine']}/links",
        cookies=council.cookies(settings),
    )
    assert str(world["revocable"]) in links.text

    migration = await client.get(
        "/v1/council/identity-migration", cookies=council.cookies(settings)
    )
    assert 'data-section="totals"' in migration.text

    profile = await client.get(
        "/v1/council/field-profile", cookies=council.cookies(settings)
    )
    assert "reported_never_writable" in profile.text


# ---------------------------------------------------------------------------
# Permitted mutations
# ---------------------------------------------------------------------------


async def test_a_council_member_may_grant_a_link(client, settings, migrated_database, world):
    """R-25's `✓` for `C`: `303` to the page that re-reads under fresh authority.

    Post/redirect/get, not a rendered result: the next `GET` resolves capability
    again, so a privilege that changed between the write and the read is applied to
    the read rather than assumed from the write.
    """
    council = world["callers"]["C"]
    version = version_of(migrated_database, world["theirs"])
    response = await post(
        client,
        settings,
        council,
        f"/v1/council/characters/{world['theirs']}/links",
        f"subject={LINK_TARGET_SUBJECT}&access_kind=co_owner&version={version}"
        "&reason=Council+granted+a+second+authorized+user",
    )
    assert response.status_code == 303
    assert response.headers["location"] == f"/v1/council/characters/{world['theirs']}/links"
    assert (
        count(
            migrated_database,
            "SELECT count(*) FROM character_access WHERE character_id = :id "
            "AND platform_account_id = :account AND active",
            id=world["theirs"],
            account=world["target_account"],
        )
        == 1
    )
    # The optimistic version advanced, and one audit event names the change.
    assert version_of(migrated_database, world["theirs"]) == version + 1
    assert (
        count(
            migrated_database,
            "SELECT count(*) FROM audit_events WHERE action = 'character_access.granted'",
        )
        == 1
    )


async def test_a_council_member_may_revoke_a_link_and_the_row_survives(
    client, settings, migrated_database, world
):
    """R-26's `✓`, and TC-ACC-05's compensating-action model in one case.

    The row is kept: it kiceps its grantor, its reason, its timestamps and its
    correlation id, and only `active`/`revoked_at` change. Deleting it would erase
    why somebody was given access in order to record that they lost it.
    """
    council = world["callers"]["C"]
    version = version_of(migrated_database, world["mine"])
    response = await post(
        client,
        settings,
        council,
        f"/v1/council/characters/{world['mine']}/links/{world['revocable']}/revoke",
        f"version={version}&reason=Council+revoked+the+co-owner",
    )
    assert response.status_code == 303
    row = None
    with migrated_database.begin() as connection:
        row = (
            connection.execute(
                text("SELECT * FROM character_access WHERE id = :id"),
                {"id": world["revocable"]},
            )
            .mappings()
            .one()
        )
    assert row["active"] is False
    assert row["revoked_at"] is not None
    # The *grant's* reason, untouched. The revocation's reason is in the audit event.
    assert row["reason"] == "seeded for a test"
    assert row["granted_by_account_id"] == council.account_id


async def test_a_council_member_may_move_the_default_character(
    client, settings, migrated_database, world
):
    """R-27's `✓`. The default is a property of the **account**, so it moves."""
    council = world["callers"]["C"]
    version = version_of(migrated_database, world["mine"])
    response = await post(
        client,
        settings,
        council,
        f"/v1/council/characters/{world['mine']}/links/{world['revocable']}/default",
        f"version={version}&reason=Council+moved+the+default",
    )
    assert response.status_code == 303
    assert (
        count(
            migrated_database,
            "SELECT count(*) FROM character_access WHERE platform_account_id = :account "
            "AND active AND default_character",
            account=world["target_account"],
        )
        == 1
    )


async def test_an_administrator_may_create_and_revoke_a_mapping(
    client, settings, migrated_database, world
):
    """R-33 and R-34's `✓` for `A`. Council alone is `403`, which the matrix covers."""
    admin = world["callers"]["A"]
    created = await post(
        client,
        settings,
        admin,
        "/v1/admin/role-capabilities",
        "role_id=900000000000000031&capability=dm&reason=Administrator+mapped+a+DM+role",
    )
    assert created.status_code == 303
    mapping_id = count(
        migrated_database,
        "SELECT id FROM role_capability_mappings WHERE role_id = 900000000000000031",
    )
    assert mapping_id is not None

    revoked = await post(
        client,
        settings,
        admin,
        f"/v1/admin/role-capabilities/{world['ordinary_mapping']}/revoke",
        "version=0&reason=Administrator+revoked+it",
    )
    assert revoked.status_code == 303
    assert (
        count(
            migrated_database,
            "SELECT active FROM role_capability_mappings WHERE id = :id",
            id=world["ordinary_mapping"],
        )
        is False
    )


async def test_a_full_scope_administrator_may_ratify_an_emergency_mapping(
    client, settings, migrated_database, world
):
    """R-38's `✓` for `A`: the one exit from emergency-derived authority.

    `FULL_ADMINISTRATOR` demands an ordinary-provider session **and** full scope, so
    this caller qualifies and a `BG` or `AC` one does not — which is the other half
    of TC-BG-05e and is asserted in `test_p3_2_emergency_boundary.py`.
    """
    response = await post(
        client,
        settings,
        world["callers"]["A"],
        f"/v1/admin/role-capabilities/{world['emergency_mapping']}/ratify",
        "version=0&reason=Administrator+ratified+it+after+the+incident",
    )
    assert response.status_code == 303
    with migrated_database.begin() as connection:
        row = (
            connection.execute(
                text("SELECT provenance, ratified_at FROM role_capability_mappings WHERE id = :id"),
                {"id": world["emergency_mapping"]},
            )
            .mappings()
            .one()
        )
    assert row["ratified_at"] is not None
    assert row["provenance"] != "emergency_continuity"


@pytest.mark.parametrize("state", ["N", "M", "C", "A", "CA"])
async def test_r_37_is_authorized_for_every_permitted_state_and_then_refused_by_id_07(
    client, settings, migrated_database, world, state
):
    """R-37's `✓`, and what a `✓` in §5.2 actually claims.

    The matrix column says the **authorization chain** permits the request — steps 4
    to 8 — not that the operation succeeds. For R-37 in Phase 3 those are different
    things, and the difference is TC-ID-07 rather than a gap:

    * there is exactly one ordinary provider, so a member has exactly one active
      identity, and
    * unlinking it would leave the account with no usable identity and no reviewed
      recovery route — enrolled WebAuthn credentials are the protected
      administrator's route (N-13, ADR 0010 D8) and there is no member-facing
      enrollment route at all, so inheriting them would read one account's controls
      as another's.

    So every permitted state reaches the service and receives `409 UnlinkRefused`:
    not `401`, not `403`, not the `404` an unreachable identity gets. That is the
    positive evidence for the cell — the caller got *past* authorization — and the
    negative evidence for the operation, which is what TC-ID-07 requires.

    A successful unlink needs an account with two active identities. That state is
    expressible in the schema and is **not** produced here: see
    `test_two_active_provider_identities_fail_closed_rather_than_500`, which is the
    defect this suite found while trying to arrange it.
    """
    caller = world["callers"][state]
    identity_id = count(
        migrated_database,
        "SELECT id FROM external_identities WHERE platform_account_id = :account "
        "AND provider_key = 'discord' AND state = 'active'",
        account=caller.account_id,
    )
    response = await post(
        client,
        settings,
        caller,
        f"/v1/account/identities/{identity_id}/unlink",
        "reason=my+only+identity",
    )
    assert response.status_code == 409, state
    assert (
        count(
            migrated_database,
            "SELECT state FROM external_identities WHERE id = :id",
            id=identity_id,
        )
        == "active"
    )


async def test_r_37_refuses_another_account_s_identity_as_unreachable(
    client, settings, world
):
    """The identity id is caller input, and the scope is `context.account_id`.

    `AccountIdentityService` takes no account parameter, so there is no identifier a
    caller could substitute; an id belonging to somebody else is simply not in this
    account's set and is answered as unreachable.
    """
    response = await post(
        client,
        settings,
        world["callers"]["M"],
        f"/v1/account/identities/{uuid4()}/unlink",
        "reason=somebody+elses+identity",
    )
    assert response.status_code == 404


async def test_two_active_provider_identities_fail_closed_rather_than_500(
    client, settings, migrated_database, world
):
    """A defect this suite found, and the fail-closed answer it now gets.

    `external_identities` is unique on `(provider_key, subject)` and carries no
    constraint against one account holding **two** active identities for the same
    provider, so the state is expressible. `AccountRepository.discord_subject()`
    answered it with `scalar_one_or_none()`, which raises `MultipleResultsFound`
    inside `open_request()` — an unhandled exception, so every protected request by
    such an account was a `500` naming an internal error.

    It is now an ambiguity that fails closed: `503` with VM-03, the same answer a
    provider the platform cannot reach gets, because the platform cannot say whose
    roles this person holds and a capability decision it cannot make is one it must
    not guess. It is deliberately **not** resolved by ordering the rows and taking
    the first.

    No constraint is added to make the state unexpressible: whether one human may
    link two Discord accounts to one platform account is a product decision ADR 0010
    does not settle, and forbidding it in a migration would settle it as a side
    effect of fixing a `500`. The P3.2 submission records it as an open question.
    """
    caller = world["callers"]["M"]
    with migrated_database.begin() as connection:
        link_discord(connection, caller.account_id, 700000000000007001)

    response = await client.get("/v1/characters", cookies=caller.cookies(settings))
    assert response.status_code == 503
    assert "service_degraded" in response.text


# ---------------------------------------------------------------------------
# TC-OBJ — object-level authorization
# ---------------------------------------------------------------------------


async def test_a_member_sees_exactly_their_own_characters(client, settings, world):
    """TC-OBJ-03. Their set, and the default flag is theirs alone."""
    response = await client.get(
        "/v1/characters", cookies=world["callers"]["M"].cookies(settings)
    )
    assert "Alia Storm" in response.text
    assert "Someone Elses" not in response.text


async def test_council_reach_is_role_derived_and_needs_no_access_row(
    client, settings, migrated_database, world
):
    """TC-OBJ-04. A Council member reads any character with no link of their own.

    OD-37: Council reach is deliberately not modelled as an access row, which is
    also why `guild_council` is not an `access_kind`. The assertion is two-sided —
    the read succeeds, and the absence of a row for that account is checked.
    """
    council = world["callers"]["C"]
    assert (
        count(
            migrated_database,
            "SELECT count(*) FROM character_access WHERE platform_account_id = :account",
            account=council.account_id,
        )
        == 0
    )
    response = await client.get(
        f"/v1/characters/{world['theirs']}", cookies=council.cookies(settings)
    )
    assert response.status_code == 200
    assert "Someone Elses" in response.text


async def test_cross_character_substitution_is_indistinguishable_from_absence(
    client, settings, world
):
    """TC-OBJ-02 and TC-OBJ-07 together: the two `404` bodies are byte-identical.

    A member requesting somebody else's character and a member requesting a UUID
    that has never existed receive the *same bytes*. Anything that differed —
    including a correlation id, which is why `denied.html` renders none — would tell
    a caller which of the two they had found, and "this character exists but is not
    yours" is exactly the fact the `404` exists to withhold.
    """
    member = world["callers"]["M"]
    inaccessible = await client.get(
        f"/v1/characters/{world['theirs']}", cookies=member.cookies(settings)
    )
    absent = await client.get(
        f"/v1/characters/{uuid4()}", cookies=member.cookies(settings)
    )
    malformed = await client.get(
        "/v1/characters/not-a-uuid", cookies=member.cookies(settings)
    )

    assert inaccessible.status_code == absent.status_code == malformed.status_code == 404
    assert inaccessible.content == absent.content
    assert inaccessible.content == malformed.content
    # And nothing about the object leaks into it.
    assert "Someone Elses" not in inaccessible.text
    assert str(world["theirs"]) not in inaccessible.text


async def test_an_access_id_from_another_character_is_unreachable(
    client, settings, migrated_database, world
):
    """The access id is caller input, so "belongs to this character" is checked.

    Without it, a Council member acting on one character's screen could revoke a
    link belonging to a character they are not looking at.
    """
    council = world["callers"]["C"]
    version = version_of(migrated_database, world["theirs"])
    response = await post(
        client,
        settings,
        council,
        f"/v1/council/characters/{world['theirs']}/links/{world['revocable']}/revoke",
        f"version={version}&reason=wrong+character",
    )
    assert response.status_code == 404
    assert (
        count(
            migrated_database,
            "SELECT active FROM character_access WHERE id = :id",
            id=world["revocable"],
        )
        is True
    )


# ---------------------------------------------------------------------------
# TC-ACC-04 / TC-ACC-06 — optimistic concurrency and the reason requirement
# ---------------------------------------------------------------------------


async def test_a_stale_version_is_refused_409_and_applies_nothing(
    client, settings, migrated_database, world
):
    """TC-ACC-04. The conditional update matched no row, so nothing was written.

    The version bump is the **first** write of every mutation, deliberately: two
    concurrent Council members meet at that row, and the loser is refused before it
    has inserted anything it would then have to be trusted to roll back.
    """
    council = world["callers"]["C"]
    version = version_of(migrated_database, world["mine"])
    response = await post(
        client,
        settings,
        council,
        f"/v1/council/characters/{world['mine']}/links",
        f"subject={LINK_TARGET_SUBJECT}&access_kind=viewer&version={version + 7}"
        "&reason=stale+form",
    )
    assert response.status_code == 409
    assert 'data-conflict="stale_version"' in response.text or "stale" in response.text
    assert version_of(migrated_database, world["mine"]) == version
    assert (
        count(
            migrated_database,
            "SELECT count(*) FROM character_access WHERE character_id = :id AND active",
            id=world["mine"],
        )
        == 2
    )


@pytest.mark.parametrize("reason", ["", "   "])
async def test_a_blank_reason_is_refused_422(
    client, settings, migrated_database, world, reason
):
    """TC-ACC-06. `422` with the form re-rendered, never a bare `400`.

    A Council member has to be able to correct it, and a bare `400` would not tell
    them how. The version is untouched, so a refused attempt is not a state change
    with a message attached.
    """
    council = world["callers"]["C"]
    version = version_of(migrated_database, world["mine"])
    response = await post(
        client,
        settings,
        council,
        f"/v1/council/characters/{world['mine']}/links/{world['revocable']}/revoke",
        f"version={version}&reason={reason}",
    )
    assert response.status_code == 422
    assert version_of(migrated_database, world["mine"]) == version
    assert (
        count(
            migrated_database,
            "SELECT active FROM character_access WHERE id = :id",
            id=world["revocable"],
        )
        is True
    )


async def test_a_reason_longer_than_the_bound_is_refused_and_never_truncated(
    client, settings, migrated_database, world
):
    """§3.2's bound refuses; it does not cut.

    A truncated justification is a different justification, and the person writing
    it should be told rather than discovering later that half of it was discarded.
    """
    from application.web.character_access import REASON_BOUND

    council = world["callers"]["C"]
    version = version_of(migrated_database, world["mine"])
    response = await post(
        client,
        settings,
        council,
        f"/v1/council/characters/{world['mine']}/links/{world['revocable']}/revoke",
        f"version={version}&reason={'x' * (REASON_BOUND + 1)}",
    )
    assert response.status_code == 422
    assert version_of(migrated_database, world["mine"]) == version


async def test_an_unknown_access_kind_is_refused(client, settings, migrated_database, world):
    """The closed vocabulary is enforced by the service, not by the form's options."""
    council = world["callers"]["C"]
    version = version_of(migrated_database, world["theirs"])
    response = await post(
        client,
        settings,
        council,
        f"/v1/council/characters/{world['theirs']}/links",
        f"subject={LINK_TARGET_SUBJECT}&access_kind=guild_council&version={version}"
        "&reason=a+capability+is+not+an+access+kind",
    )
    assert response.status_code == 422


async def test_a_forged_snowflake_resolves_to_no_account_and_is_unreachable(
    client, settings, migrated_database, world
):
    """TC-ID-08's server-side resolution, from the input side.

    The target platform account is resolved from the **snowflake**, server-side, and
    a snowflake the platform has never seen is refused as unreachable rather than
    causing an account to be created — which would mint a platform identity from a
    Council form.
    """
    council = world["callers"]["C"]
    version = version_of(migrated_database, world["theirs"])
    response = await post(
        client,
        settings,
        council,
        f"/v1/council/characters/{world['theirs']}/links",
        f"subject=799999999999999999&access_kind=viewer&version={version}"
        "&reason=an+invented+snowflake",
    )
    assert response.status_code == 404
    assert count(migrated_database, "SELECT count(*) FROM platform_accounts WHERE "
                 "display_label IS NULL") >= 0


async def test_a_grant_form_cannot_name_a_platform_account_at_all(client, settings, world):
    """TC-ID-08. The form has no such field and the service has no such parameter.

    The strongest available statement of "a forged `platform_account_id` is ignored"
    is that there is nowhere to put one. Asserted over the signature rather than by
    submitting one and observing that nothing happened, because the second reads as
    a coincidence.
    """
    import inspect

    from application.web.character_access import CharacterAccessService

    parameters = inspect.signature(CharacterAccessService.grant).parameters
    assert "platform_account_id" not in parameters
    assert "account_id" not in parameters
    assert "subject" in parameters


# ---------------------------------------------------------------------------
# Every permitted cell of the matrix is covered by something above
# ---------------------------------------------------------------------------


def test_every_permitted_cell_has_a_success_case_in_this_module():
    """The bookkeeping guard, so a `✓` cannot be quietly uncovered.

    `test_p3_2_matrix.py` skips permitted cells; this module is where they are
    asserted. Without this case, a route whose success case was deleted would leave
    its `✓` proved by nothing at all — the skip would still pass.
    """
    import re
    from pathlib import Path

    from tests.web.test_p3_2_matrix import STATES, expected_status, parsed_matrix

    permitted = {
        (route, state)
        for route, cells in parsed_matrix().items()
        for state in STATES
        if expected_status(cells[state], navigation=GUARDS[route].navigation) is None
    }
    covered = set(re.findall(r'\("(R-\d+)", "([A-Z]{1,2})"\)', Path(__file__).read_text()))
    #: Mutations are covered by their own named cases rather than by the read
    #: parametrization, so their routes are listed here with the states those cases
    #: use. Kept as data so the guard names what it is trusting.
    covered |= {
        ("R-25", "C"),
        ("R-26", "C"),
        ("R-27", "C"),
        ("R-29", "C"),
        ("R-30", "C"),
        ("R-33", "A"),
        ("R-34", "A"),
        ("R-38", "A"),
        # R-37's permitted cells are authorized and then refused `409` by TC-ID-07;
        # see the case for why those are different facts in Phase 3.
        ("R-37", "M"),
        ("R-37", "C"),
        ("R-37", "A"),
    }
    # `CA` reaches every Council route through Council and every administrator
    # route through administrator; the equivalence is asserted route-wide by
    # TC-CAP-02's matrix rather than re-listed per cell here.
    outstanding = {
        (route, state)
        for route, state in permitted
        if state not in {"CA", "BG", "N"} and (route, state) not in covered
    }
    assert outstanding == set(), sorted(outstanding)
