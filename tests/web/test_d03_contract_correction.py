"""The accepted D-03 correction, items D-03-2 to D-03-6, asserted against the tree.

**Added 2026-08-19** under change-log `C-P3.4-A`. Item D-03-1 — the `/static/`
surface — has its own module, `test_static_asset_surface.py`, because it is a new
URL surface rather than a correction to an existing one.

Each case here corresponds to a numbered accepted decision, and each asserts the
*implemented* behaviour against the *corrected contract text*, parsed where it can
be parsed. That direction matters: four of these six items were record defects, so
a test that only re-stated the implementation would prove exactly the thing that
was never in doubt.
"""
from __future__ import annotations

import re
from dataclasses import fields
from pathlib import Path
from uuid import uuid4

import pytest

from application.web import view_models
from application.web.view_models import (
    DeniedView,
    DenialCategory,
    IMPLEMENTED_VIEW_MODELS,
    VIEW_MODEL_VERSION,
)
from tests.web.portal_fixtures import (
    MEMBER_SUBJECT,
    OTHER_MEMBER_SUBJECT,
    clean_p3_2_tables,
    csrf_token_for,
    grant_link,
    make_character,
    seed_callers,
    seed_discord_member,
)
from tests.web.conftest import link_discord, make_account
from tests.web_fixtures import PUBLIC_ORIGIN

pytestmark = pytest.mark.database

ROOT = Path(__file__).resolve().parents[2]
VIEW_MODEL_CONTRACT = ROOT / "docs" / "contracts" / "phase-3-view-model-contract.md"
ROUTE_CONTRACT = ROOT / "docs" / "contracts" / "phase-3-route-authorization-contract.md"
P3_2_SUBMISSION = ROOT / "docs" / "review" / "phase-3-p3-2-submission.md"

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
def world(migrated_database, settings):
    """One member with one character, and one character they cannot reach.

    The smallest world in which "denied" and "absent" are both real outcomes,
    which is what the byte-identity cases below need.
    """
    callers = seed_callers(migrated_database, settings, states=("U", "M", "C"))
    with migrated_database.begin() as connection:
        mine = make_character(connection, display_name="Alia Storm")
        theirs = make_character(connection, display_name="Someone Elses")
        grant_link(
            connection,
            character_id=mine,
            account_id=callers["M"].account_id,
            granted_by=callers["C"].account_id,
            default_character=True,
        )
        other_account = make_account(connection, label="other-member")
        seed_discord_member(connection, subject=OTHER_MEMBER_SUBJECT, username="other.one")
        link_discord(connection, other_account, OTHER_MEMBER_SUBJECT)
        grant_link(
            connection,
            character_id=theirs,
            account_id=other_account,
            granted_by=callers["C"].account_id,
        )
    return {"callers": callers, "mine": mine, "theirs": theirs}


def _contract_block(identifier: str) -> str:
    """The fenced `text` block under a `### VM-nn` heading in the contract."""
    body = VIEW_MODEL_CONTRACT.read_text()
    match = re.search(
        rf"^### {re.escape(identifier)} `[^`]+`.*?```text\n(?P<block>.*?)\n```",
        body,
        re.MULTILINE | re.DOTALL,
    )
    assert match, f"{identifier} has no type sketch in the view-model contract"
    return match.group("block")


def _documented_fields(identifier: str, type_name: str) -> list[str]:
    """Field names the contract's sketch lists for one constructor."""
    block = _contract_block(identifier)
    match = re.search(
        rf"{re.escape(type_name)}\(\n(?P<body>.*?)\n\)", block, re.DOTALL
    )
    assert match, f"{type_name} is not sketched under {identifier}"
    names = []
    for line in match.group("body").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        names.append(line.split(":", 1)[0].strip())
    return names


# ---------------------------------------------------------------------------
# D-03-2 — `ConfirmScope`
# ---------------------------------------------------------------------------


def test_confirm_scope_matches_the_corrected_contract_exactly():
    """D-03-2. Eight fields, the accepted eight, in the accepted order.

    `ConfirmScope` was referenced by VM-15 and defined nowhere, so this asserts
    the *new contract text* against the implementation rather than the other way
    round. Order is asserted as well as membership because the contract's sketch
    is what a P3.4 author reads top to bottom, and a sketch listing the same eight
    names in a different order is a sketch that has stopped tracking the code.
    """
    implemented = [field.name for field in fields(view_models.ConfirmScope)]
    assert implemented == [
        "preview_token",
        "checksum_full",
        "folder",
        "profile_version",
        "expires_at",
        "would_create",
        "would_update",
        "blocked",
    ]
    assert _documented_fields("VM-15", "ConfirmScope") == implemented


def test_confirm_scope_is_optional_on_the_job_view_and_typed_when_present():
    """D-03-2. `confirm` is `None` for anything that is not a confirmable preview.

    Stated in the corrected contract as the presence rule, and asserted here so a
    P3.4 template author's `{% if view.confirm %}` is checking a real invariant.
    """
    annotations = {field.name: str(field.type) for field in fields(view_models.JobStatusView)}
    assert "ConfirmScope" in annotations["confirm"]
    assert "None" in annotations["confirm"]


def test_the_corrected_contract_says_the_checksum_and_versions_are_re_read():
    """D-03-2. The rule that keeps a rendered value from becoming an input.

    R-46 submits `preview_token` and `nonce`; everything else in `ConfirmScope` is
    re-read server-side (route contract §2.4). That sentence is the reason this
    definition is safe to publish to a frontend at all, so its presence in the
    contract is asserted rather than assumed.
    """
    block = VIEW_MODEL_CONTRACT.read_text()
    section = block[block.index("**`ConfirmScope`, defined 2026-08-19**"):]
    section = section[: section.index("### VM-16")]
    assert "re-read server-side" in section
    assert "`preview_token` and `nonce`" in section


# ---------------------------------------------------------------------------
# D-03-3 — `CharacterFilters`
# ---------------------------------------------------------------------------


def test_character_filters_matches_the_corrected_contract_exactly():
    """D-03-3. Two fields, both defaulted, both echoes of validated input."""
    implemented = [field.name for field in fields(view_models.CharacterFilters)]
    assert implemented == ["query", "include_inactive"]
    assert _documented_fields("VM-07", "CharacterFilters") == implemented

    annotations = {field.name: str(field.type) for field in fields(view_models.CharacterFilters)}
    assert "SafeText" in annotations["query"] and "None" in annotations["query"]
    assert annotations["include_inactive"] == "bool"

    empty = view_models.CharacterFilters()
    assert empty.query is None
    assert empty.include_inactive is False


def test_the_corrected_contract_records_that_a_name_search_is_not_an_identity_fact():
    """D-03-3. The one sentence that stops a filter becoming an authorization input."""
    body = VIEW_MODEL_CONTRACT.read_text()
    section = body[body.index("**`CharacterFilters`, defined 2026-08-19**"):]
    section = section[: section.index("## 6.")]
    assert "search fact" in section
    assert "never an identity or authorization" in section


# ---------------------------------------------------------------------------
# D-03-4 — VM-13's CSRF token
# ---------------------------------------------------------------------------


def test_vm_13_carries_a_csrf_token_and_the_contract_now_lists_it():
    """D-03-4. Implemented and, from this correction, recorded."""
    implemented = [field.name for field in fields(view_models.AccountIdentitiesView)]
    assert "csrf_token" in implemented
    assert "csrf_token" in _documented_fields("VM-13", "AccountIdentitiesView")


def test_the_retracted_provenance_claim_is_gone_and_the_p3_2_record_is_untouched():
    """D-03-4. The defect was a claim, so the assertion is about the claim.

    Two halves, and the second is the one that matters. First: the docstring no
    longer says the field was *"Recorded in the P3.2 submission"*. Second: the
    accepted P3.2 submission still contains no occurrence of `csrf_token` — which
    is to say the correction was made by retracting a false statement, **not** by
    editing an accepted historical record until the statement became true.
    """
    source = (ROOT / "application" / "web" / "view_models.py").read_text()
    assert "Recorded in the P3.2 submission" not in source

    if P3_2_SUBMISSION.exists():
        assert "csrf_token" not in P3_2_SUBMISSION.read_text(), (
            "the accepted P3.2 submission must not be edited to manufacture "
            "provenance for a field that was never recorded in it"
        )


def test_the_csrf_design_is_a_synchronizer_token_not_a_double_submit_cookie():
    """D-03-4. N-17's design, restated as an assertion over the corrected block.

    Recording an additive CSRF field is only safe if the record also says which
    scheme it is. A frontend author reading "csrf_token" with no further text
    could reasonably reach for `document.cookie`.
    """
    section = _section_after("**`csrf_token`, recorded 2026-08-19**", "## 5.")
    assert "synchronizer" in section
    assert "never** read from a cookie by script" in section
    assert "double-submit CSRF are both rejected designs" in section


def _section_after(marker: str, terminator: str) -> str:
    body = VIEW_MODEL_CONTRACT.read_text()
    section = body[body.index(marker):]
    return section[: section.index(terminator)]


async def test_r_37_still_refuses_a_missing_or_invalid_csrf_token(
    client, settings, world
):
    """D-03-4. The field is recorded; the check it feeds is unchanged.

    A record correction that quietly relaxed the verification would be a far worse
    outcome than the missing record, so this is asserted rather than reasoned
    about. Three shapes: absent, wrong, and another caller's genuine token.
    """
    member = world["callers"]["M"]
    council = world["callers"]["C"]
    identity_path = f"/v1/account/identities/{uuid4()}/unlink"
    headers = {"origin": PUBLIC_ORIGIN, "content-type": FORM}

    absent = await client.post(
        identity_path, content="", headers=headers, cookies=member.cookies(settings)
    )
    assert absent.status_code == 403

    forged = await client.post(
        identity_path,
        content="csrf_token=not-a-real-token",
        headers=headers,
        cookies=member.cookies(settings),
    )
    assert forged.status_code == 403

    borrowed = await client.post(
        identity_path,
        content=f"csrf_token={csrf_token_for(settings, council)}",
        headers=headers,
        cookies=member.cookies(settings),
    )
    assert borrowed.status_code == 403


# ---------------------------------------------------------------------------
# D-03-5 — R-36
# ---------------------------------------------------------------------------


async def test_r_36_answers_200_with_a_denied_vm_13_and_never_redirects(
    client, settings, world
):
    """D-03-5. The accepted behaviour, and the absence of the behaviour the table claimed.

    The `303` the contract's table used to state is asserted **absent**, not merely
    unobserved: a redirect here would mean a second ordinary provider had appeared,
    and Phase 3 has exactly one.
    """
    member = world["callers"]["M"]
    response = await client.get(
        "/v1/account/identities/link/start", cookies=member.cookies(settings)
    )
    assert response.status_code == 200
    assert response.status_code != 303
    assert "location" not in response.headers
    assert "no_additional_provider" in response.text or "denied" in response.text


def test_the_route_contract_table_and_prose_now_agree_about_r_36():
    """D-03-5. The correction was to a record, so the record is what is asserted.

    Parsed from the contract rather than transcribed, for the same reason
    TC-STRUCT-01 parses: a transcription would be a second copy of the thing that
    drifted.
    """
    body = ROUTE_CONTRACT.read_text()
    row = re.search(r"^\|\s*R-36\s*\|.*$", body, re.MULTILINE)
    assert row, "R-36 has no row in the route contract"
    cell = row.group(0)
    assert "200" in cell and "VM-13" in cell
    assert "303` to provider" not in cell
    assert "`303` to provider" not in cell


def test_phase_3_still_has_exactly_one_ordinary_provider():
    """D-03-5. The correction adds no provider and no linking flow.

    `additional_provider` keeps its single-member literal, so a second provider
    remains unrepresentable rather than merely unimplemented.
    """
    annotations = {
        field.name: str(field.type)
        for field in fields(view_models.AccountIdentitiesView)
    }
    assert "no_additional_provider" in annotations["additional_provider"]


# ---------------------------------------------------------------------------
# D-03-6 — `DeniedView`
# ---------------------------------------------------------------------------


def test_the_denied_view_is_registered_as_vm_22_and_the_version_is_unchanged():
    """D-03-6. Additive under §1 rule 5: a model is added, `vm-1` stands."""
    assert IMPLEMENTED_VIEW_MODELS["VM-22"] is DeniedView
    assert VIEW_MODEL_VERSION == "vm-1"
    documented = set(
        re.findall(r"^### (VM-\d+) `", VIEW_MODEL_CONTRACT.read_text(), re.MULTILINE)
    )
    assert "VM-22" in documented
    assert set(IMPLEMENTED_VIEW_MODELS) == documented


def test_no_generic_denial_is_constructed_from_the_non_member_view():
    """D-03-6. Read over the source, because the defect was a *carrier*, not a body.

    Every `_denied` helper on the portal and import surfaces must build a
    `DeniedView`. Asserted structurally as well as through responses below,
    because a handler that reverted to VM-02 with inert placeholders would produce
    byte-identical output today and break the moment P3.4's template printed one
    of the three fields — which is exactly the failure this item exists to make
    impossible.
    """
    for module in ("adapters/web/portal_routes.py", "adapters/web/import_routes.py"):
        source = (ROOT / module).read_text()
        denied = source[source.index("def _denied("):]
        denied = denied[: denied.index("\n    def ", 1)]
        assert "DeniedView(" in denied, module
        assert "NonMemberView(" not in denied, module
        for leak in ("correlation=", "guild_display_name=", "checked_at="):
            assert leak not in denied, f"{module}: {leak}"


async def test_a_denied_response_body_contains_only_the_category(
    client, settings, world
):
    """D-03-6 / TC-OBJ-07. Nothing identifying reaches the safe denial page."""
    member = world["callers"]["M"]
    response = await client.get(
        f"/v1/characters/{world['theirs']}", cookies=member.cookies(settings)
    )
    assert response.status_code == 404
    body = response.text
    assert "not_available" in body
    for leak in (
        str(world["theirs"]),
        "Someone Elses",
        "00000000-0000-0000-0000-000000000000",
        "Freedom Blades membership",
    ):
        assert leak not in body, leak
    # No UUID of any shape, which covers a correlation id nobody predicted.
    assert not re.search(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        body,
    )
    # No timestamp either: an `Instant` printed on a denial page would vary.
    assert not re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", body)


async def test_denied_and_absent_404_bodies_remain_byte_identical(
    client, settings, world
):
    """D-03-6 / TC-OBJ-07, re-asserted under the new carrier.

    The existing case in `test_p3_2_success_cells.py` proved this before the
    correction. It is asserted again here because the correction changed the
    object the template is handed, and "the byte-identity survived a change to the
    denial carrier" is a different claim from "the byte-identity held once".
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
    assert inaccessible.content == absent.content == malformed.content


async def test_the_import_surface_denies_a_member_with_the_same_bytes(
    client, settings, world
):
    """D-03-6. The other route module's `_denied`, and the same guarantee.

    A member reaching a job or import id learns nothing: `403` before the row is
    read, and a body carrying a category and nothing else. Two different ids
    produce identical bytes, so the identifier is worth nothing to hold.
    """
    member = world["callers"]["M"]
    first = await client.get(
        f"/v1/council/jobs/{uuid4()}", cookies=member.cookies(settings)
    )
    second = await client.get(
        f"/v1/council/jobs/{uuid4()}", cookies=member.cookies(settings)
    )
    assert first.status_code == second.status_code == 403
    assert first.content == second.content
    assert "insufficient_capability" in first.text
    assert not re.search(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        first.text,
    )


async def test_the_non_member_page_keeps_vm_02_and_its_recovery_context(
    client, settings, migrated_database
):
    """D-03-6. The permitted exception, asserted so the correction cannot over-reach.

    `non_member.html` is *meant* to be distinguishable from "not signed in" and
    from a generic denial: the person authenticated and is not in the guild, and
    the guild name, the check time and the correlation id are what they need in
    order to recover. Narrowing this page to `DeniedView` would have been a
    regression dressed as consistency.
    """
    callers = seed_callers(migrated_database, settings, states=("N",))
    response = await client.get(
        "/v1/characters", cookies=callers["N"].cookies(settings)
    )
    assert response.status_code == 403
    body = response.text
    assert "not_a_member" in body
    assert "Freedom Blades" in body
    assert re.search(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        body,
    ), "the non-member page keeps its correlation id; it is a recovery aid here"


async def test_an_unauthorized_call_is_denied_before_the_object_is_looked_up(
    client, settings, world
):
    """D-03-6, invariant 3. Authorization precedes lookup where the contract requires it.

    A real character id and an id that has never existed produce the same status
    and the same bytes for a caller with no Council capability, which is only
    possible if the refusal happened before the row was read.
    """
    member = world["callers"]["M"]
    real = await client.get(
        f"/v1/council/characters/{world['theirs']}/links",
        cookies=member.cookies(settings),
    )
    invented = await client.get(
        f"/v1/council/characters/{uuid4()}/links", cookies=member.cookies(settings)
    )
    assert real.status_code == invented.status_code == 403
    assert real.content == invented.content


@pytest.mark.parametrize(
    "category", sorted(entry.value for entry in DenialCategory)
)
def test_every_denial_category_is_representable_and_carries_nothing_else(category):
    """D-03-6. The closed vocabulary, one case per member.

    Constructed rather than fetched: several of these categories arise only from
    states a route test cannot reach cheaply, and what is being asserted is that
    the *type* admits each of them and nothing more.
    """
    view = DeniedView(
        state="denied", reason=view_models.DeniedReason(DenialCategory(category))
    )
    assert view.reason.category.value == category
    assert {field.name for field in fields(view)} == {"state", "reason"}

    # Frozen **and** slotted, so neither a template filter nor a helper can
    # attach a correlation id to a denial on its way to the renderer.
    with pytest.raises((AttributeError, TypeError)):
        view.correlation = uuid4()
    with pytest.raises((AttributeError, TypeError)):
        view.state = "ready"
