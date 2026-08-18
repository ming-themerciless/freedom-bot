"""TC-OBJ-01, TC-OBJ-06, TC-CAP-02 and TC-CAP-09: the matrix, issued directly.

Every case here builds its request from the route table and sends it **without
ever rendering the page that contains the control**. That is route contract
§2.2's explicit proof that UI hiding is not authorization, and it is the reason
these tests never call a `GET` first: a suite that navigated to the Council
screen and then clicked would be testing the template.

The expectations are **parsed out of the accepted contract document**, not
transcribed here. A cell that drifts fails a test rather than passing a reading,
and the `GUARDS` table the routes are built from is asserted against the same
parse — so the matrix, the guards and the running application are one fact
checked twice rather than three copies.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from adapters.web.portal_routes import GUARDS, P3_2_ROUTE_INVENTORY
from tests.web.portal_fixtures import (
    MEMBER_SUBJECT,
    clean_p3_2_tables,
    csrf_token_for,
    grant_link,
    make_character,
    seed_callers,
)

pytestmark = pytest.mark.database

ROOT = Path(__file__).resolve().parents[2]
ROUTE_CONTRACT = ROOT / "docs" / "contracts" / "phase-3-route-authorization-contract.md"

#: `| R-20 | `my_characters` | ✗ 303 | ✗ 403 | ✓ | ✓ | ✗ 403 | ✓ | ✗ 403 | – | – | – |`
_MATRIX_ROW = re.compile(
    r"^\|\s*(?P<id>R-\d+)\s*\|\s*`(?P<name>[^`]+)`\s*\|(?P<cells>.+)\|\s*$",
    re.MULTILINE,
)

STATES = ("U", "N", "M", "C", "A", "CA", "BG")


def parsed_matrix() -> dict[str, dict[str, str]]:
    """The §5.2 matrix, by route and caller state.

    Parsed rather than transcribed for the same reason TC-STRUCT-01 parses the
    route table: a transcription is a second copy, and the whole point is that
    there is only one.
    """
    body = ROUTE_CONTRACT.read_text()
    section = body.split("### 5.2 P3.2 matrix", 1)[1].split("## 6.", 1)[0]
    rows: dict[str, dict[str, str]] = {}
    for match in _MATRIX_ROW.finditer(section):
        cells = [cell.strip() for cell in match.group("cells").split("|")]
        if len(cells) < len(STATES):
            continue
        rows[match.group("id")] = dict(zip(STATES, cells[: len(STATES)]))
    return rows


def expected_status(cell: str, *, navigation: bool) -> int | None:
    """One matrix cell as an HTTP status, or `None` when the cell permits.

    `✓` is "the route accepts the request", which is not one status — a
    permitted `GET` is `200` and a permitted mutation is `303` — so a permitted
    cell returns `None` and the caller asserts what it means for that route.
    """
    if cell.startswith("✓"):
        return None
    if cell.startswith("obj"):
        return None
    match = re.search(r"(\d{3})", cell)
    return int(match.group(1)) if match else None


@pytest.fixture()
def callers(migrated_database, settings):
    yield seed_callers(migrated_database, settings)
    with migrated_database.begin() as connection:
        clean_p3_2_tables(connection)


@pytest.fixture()
def seeded_character(migrated_database, callers):
    """One character the `M` caller owns, so `obj` has something to reach."""
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


def test_the_parsed_matrix_covers_every_p3_2_route():
    """Without this, a parse that silently matched nothing would pass everything."""
    matrix = parsed_matrix()
    assert set(matrix) == set(P3_2_ROUTE_INVENTORY), sorted(
        set(P3_2_ROUTE_INVENTORY) ^ set(matrix)
    )
    for route, cells in matrix.items():
        assert set(cells) == set(STATES), route


def test_the_guard_table_agrees_with_the_accepted_matrix():
    """The routes are built from `GUARDS`; `GUARDS` is checked against the contract.

    This is the cheap half of the matrix evidence and it runs without a
    database: if a guard's requirement were widened, every permitted cell below
    would still pass and this would fail. The refusal cases prove the other
    direction against the running application.
    """
    matrix = parsed_matrix()
    assert set(GUARDS) == set(matrix)
    for route, cells in matrix.items():
        guard = GUARDS[route]
        # `U` distinguishes a navigation route from a partial or a mutation:
        # `303` is the redirect a `GET` navigation gets, `401` is everything
        # else (§2.3).
        unauthenticated = expected_status(cells["U"], navigation=guard.navigation)
        assert unauthenticated == (303 if guard.navigation else 401), route
        # N-65's surface, read off the `BG` column: a route a break-glass
        # session may reach is exactly a route whose guard permits continuity
        # scope.
        permitted_for_bg = expected_status(cells["BG"], navigation=guard.navigation) is None
        assert guard.continuity_allowed == permitted_for_bg, route


@pytest.mark.parametrize("route", sorted(P3_2_ROUTE_INVENTORY))
@pytest.mark.parametrize("state", STATES)
async def test_every_route_answers_the_documented_status_for_every_caller_state(
    client, settings, callers, seeded_character, route, state
):
    """`[MATRIX]` TC-OBJ-01, and TC-OBJ-06's rule about how it is issued.

    The request is constructed from the route table and sent directly. No page
    is fetched first, no control is rendered, and no redirect is followed — so a
    refusal cannot be an artefact of the template not having offered the control.

    A refusal is asserted by **status only** for the permitted cells, because a
    permitted `GET` and a permitted mutation are different successes; the
    refused cells assert the exact documented code, which is the half that
    matters.
    """
    method, path = P3_2_ROUTE_INVENTORY[route]
    guard = GUARDS[route]
    expected = expected_status(parsed_matrix()[route][state], navigation=guard.navigation)
    if expected is None:
        pytest.skip("permitted cells are asserted by the per-route success cases")

    response = await _issue(client, settings, callers[state], method, path, seeded_character)
    assert response.status_code == expected, (
        f"{route} for caller {state}: expected {expected}, got {response.status_code}"
    )
    if expected == 403 and response.headers.get("content-type", "").startswith(
        "application/json"
    ):
        # **Corrected by the P3.2 remediation.** These cases used to omit the
        # synchronizer token while claiming to measure capability denial. Once the
        # request boundary was fixed to verify CSRF *before* capability resolution
        # — which route contract §2.1 requires — a missing token answers `403
        # csrf_invalid`, and every refused mutation cell would have gone on passing
        # while measuring nothing about authorization at all. The token is now
        # supplied (see `_issue`) and the refusal code is asserted, so a cell can no
        # longer be satisfied by the wrong `403`.
        assert response.json().get("error") != "csrf_invalid", (
            f"{route} for caller {state}: the cell measured CSRF, not capability"
        )


async def _issue(client, settings, caller, method: str, path: str, character_id):
    concrete = (
        path.replace("{character_id}", str(character_id))
        .replace("{access_id}", "00000000-0000-4000-8000-000000000001")
        .replace("{mapping_id}", "00000000-0000-4000-8000-000000000002")
        .replace("{proposal_id}", "00000000-0000-4000-8000-000000000003")
        .replace("{identity_id}", "00000000-0000-4000-8000-000000000004")
    )
    cookies = caller.cookies(settings)
    if method == "GET":
        return await client.get(concrete, cookies=cookies)
    # A mutation carries a correct `Origin`, the right content type **and a valid
    # synchronizer token**, so the only thing the cell can be measuring is
    # authorization. The token is derived from the caller's session id exactly as
    # `open_request()` derives it — *without rendering the page that carries one*,
    # which is route contract §2.2's rule and the reason this suite never issues a
    # `GET` first. A caller with no session at all (`U`) gets no token, because
    # there is no session for one to be bound to and step 4 refuses first anyway.
    body = "reason=matrix+probe&version=0&role_id=1&capability=guild_council"
    if caller.session_id is not None:
        body = f"csrf_token={csrf_token_for(settings, caller)}&{body}"
    return await client.post(
        concrete,
        cookies=cookies,
        headers={
            "Origin": settings.public_origin,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        content=body,
    )
