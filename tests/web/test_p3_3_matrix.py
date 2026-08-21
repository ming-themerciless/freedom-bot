"""TC-OBJ-01, TC-OBJ-05/06, TC-CAP-01/02/07/09 and TC-AUD-01 for R-40 to R-49.

Every case builds its request from the route table and sends it **without ever
rendering the page that contains the control**. That is route contract §2.2's
explicit proof that UI hiding is not authorization, and it is why this suite
never issues a `GET` first: a suite that navigated to the snapshot screen and
then clicked would be testing the template.

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

from adapters.web.import_routes import GUARDS, P3_3_ROUTE_INVENTORY
from application.web.jobs import JobState
from tests.web.p3_3_fixtures import (
    clean_p3_3_tables,
    complete_preview,
    seed_job,
    seed_snapshot,
    select_folder,
)
from tests.web.portal_fixtures import clean_p3_2_tables, csrf_token_for, seed_callers

pytestmark = pytest.mark.database

ROOT = Path(__file__).resolve().parents[2]
ROUTE_CONTRACT = ROOT / "docs" / "contracts" / "phase-3-route-authorization-contract.md"

_MATRIX_ROW = re.compile(
    r"^\|\s*(?P<id>R-\d+)\s*\|\s*`(?P<name>[^`]+)`\s*\|(?P<cells>.+)\|\s*$",
    re.MULTILINE,
)

STATES = ("U", "N", "M", "C", "A", "CA", "BG")


def parsed_matrix() -> dict[str, dict[str, str]]:
    """The §6.2 matrix, by route and caller state.

    Parsed rather than transcribed for the same reason TC-STRUCT-01 parses the
    route table: a transcription is a second copy, and the whole point is that
    there is only one.
    """
    body = ROUTE_CONTRACT.read_text()
    section = body.split("### 6.2 P3.3 matrix", 1)[1].split("### 6.3", 1)[0]
    rows: dict[str, dict[str, str]] = {}
    for match in _MATRIX_ROW.finditer(section):
        cells = [cell.strip() for cell in match.group("cells").split("|")]
        if len(cells) < len(STATES):
            continue
        rows[match.group("id")] = dict(zip(STATES, cells[: len(STATES)]))
    return rows


def expected_status(cell: str, *, navigation: bool) -> int | None:
    """One matrix cell as an HTTP status, or `None` when the cell permits."""
    if cell.startswith("✓") or cell.startswith("obj"):
        return None
    match = re.search(r"(\d{3})", cell)
    return int(match.group(1)) if match else None


@pytest.fixture()
def callers(migrated_database, settings):
    yield seed_callers(migrated_database, settings)
    with migrated_database.begin() as connection:
        clean_p3_3_tables(connection)
        clean_p3_2_tables(connection)


@pytest.fixture()
def seeded(migrated_database, callers):
    """A snapshot with a selected folder, a completed preview and a live job.

    Enough for every `{snapshot_id}`, `{job_id}` and `{import_id}` placeholder in
    the inventory to name something that genuinely exists, so a refusal is
    measuring authorization rather than absence.
    """
    with migrated_database.begin() as connection:
        snapshot_id, checksum = seed_snapshot(connection)
        select_folder(
            connection, snapshot_id=snapshot_id, account_id=callers["A"].account_id
        )
        preview_id, _ = complete_preview(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        live_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            state=JobState.QUEUED,
        )
    return {
        "snapshot_id": snapshot_id,
        "checksum": checksum,
        "preview_job_id": preview_id,
        "job_id": live_id,
    }


# ---------------------------------------------------------------------------
# The parse, and the guards it checks
# ---------------------------------------------------------------------------


def test_the_parsed_matrix_covers_every_p3_3_route():
    """Without this, a parse that silently matched nothing would pass everything."""
    matrix = parsed_matrix()
    assert set(matrix) == set(P3_3_ROUTE_INVENTORY), sorted(
        set(P3_3_ROUTE_INVENTORY) ^ set(matrix)
    )
    for route, cells in matrix.items():
        assert set(cells) == set(STATES), route


def test_the_guard_table_agrees_with_the_accepted_matrix():
    """The cheap half of the matrix evidence, and it needs no database.

    If a guard's requirement were widened, every permitted cell below would still
    pass and this would fail. The refusal cases prove the other direction against
    the running application.
    """
    matrix = parsed_matrix()
    assert set(GUARDS) == set(matrix)
    for route, cells in matrix.items():
        guard = GUARDS[route]
        unauthenticated = expected_status(cells["U"], navigation=guard.navigation)
        assert unauthenticated == (303 if guard.navigation else 401), route
        # N-65's surface, read off the `BG` column: a route a break-glass session
        # may reach is exactly a route whose guard permits continuity scope. The
        # accepted matrix permits `BG` on R-48 and R-49 and on nothing else in
        # this package, so this also asserts that no import, preview, apply or
        # folder-selection route admits an emergency session.
        permitted_for_bg = (
            expected_status(cells["BG"], navigation=guard.navigation) is None
        )
        assert guard.continuity_allowed == permitted_for_bg, route


def test_the_contract_body_bounds_are_the_guards_body_bounds():
    """The `Body` column, parsed and compared to what the preamble enforces.

    A bound that lived only in the guard table would be a bound nobody checked
    against the contract, and a route whose form grew past it would fail in
    production rather than here.
    """
    body = ROUTE_CONTRACT.read_text()
    section = body.split("### 6.2 P3.3 matrix", 1)[1].split("### 6.3", 1)[0]
    for match in _MATRIX_ROW.finditer(section):
        cells = [cell.strip() for cell in match.group("cells").split("|")]
        if len(cells) < len(STATES) + 3:
            continue
        route = match.group("id")
        declared = cells[len(STATES) + 2]
        guard = GUARDS[route]
        if declared == "–":
            assert guard.body_bytes is None, route
            continue
        kib = int(re.search(r"(\d+)", declared).group(1))
        assert guard.body_bytes == kib * 1024, route


# ---------------------------------------------------------------------------
# TC-OBJ-01 / TC-OBJ-06 — every route, every caller state
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("route", sorted(P3_3_ROUTE_INVENTORY))
@pytest.mark.parametrize("state", STATES)
async def test_every_route_answers_the_documented_status_for_every_caller_state(
    client, settings, callers, seeded, route, state
):
    """`[MATRIX]` TC-OBJ-01, issued the way TC-OBJ-06 requires.

    The request is constructed from the route table and sent directly. No page is
    fetched first, no control is rendered, and no redirect is followed — so a
    refusal cannot be an artefact of the template not having offered the control.
    """
    method, path = P3_3_ROUTE_INVENTORY[route]
    guard = GUARDS[route]
    expected = expected_status(
        parsed_matrix()[route][state], navigation=guard.navigation
    )
    if expected is None:
        pytest.skip("permitted cells are asserted by the per-route success cases")

    response = await _issue(client, settings, callers[state], method, path, seeded)
    assert response.status_code == expected, (
        f"{route} for caller {state}: expected {expected}, "
        f"got {response.status_code}"
    )
    if expected == 403 and response.headers.get("content-type", "").startswith(
        "application/json"
    ):
        # A refused mutation cell must be measuring **capability**, not a missing
        # synchronizer token. The token is supplied by `_issue`, and this asserts
        # the refusal is not the CSRF one — the failure mode the P3.2 remediation
        # found, where every refused cell passed while measuring nothing about
        # authorization at all.
        assert response.json().get("error") != "csrf_invalid", (
            f"{route} for caller {state}: the cell measured CSRF, not capability"
        )


@pytest.mark.parametrize("route", sorted(P3_3_ROUTE_INVENTORY))
async def test_a_continuity_scoped_administrator_matches_the_break_glass_column(
    client, settings, callers, seeded, route
):
    """TC-CAP-09: the eighth caller state, cell for cell.

    Route contract §3.3 states the rule once — *every matrix cell's `BG` value
    applies unchanged to `AC`* — rather than duplicating a column that could
    drift. That is not left to the rule: `AC` is an **ordinary-provider** session
    (`auth_method` is `discord_oauth`, the membership projection is real) whose
    administrator authority descends only from emergency-provenance mappings, and
    this re-runs the whole inventory as that caller.

    The distinction matters most exactly here. An `AC` caller *is* a guild
    member, so any check that confined emergency scope by testing membership
    would let it through R-41 — and R-41 is the folder selection N-65 names as
    refused.
    """
    method, path = P3_3_ROUTE_INVENTORY[route]
    guard = GUARDS[route]
    break_glass = expected_status(
        parsed_matrix()[route]["BG"], navigation=guard.navigation
    )
    response = await _issue(client, settings, callers["AC"], method, path, seeded)
    if break_glass is None:
        assert response.status_code in (200, 303), route
    else:
        assert response.status_code == break_glass, route


async def test_a_member_learns_nothing_from_a_job_id(
    client, settings, callers, seeded
):
    """TC-OBJ-05: `403` before the job row is read.

    A member is refused on **capability**, in the preamble, before any handler
    touches the repository — so a job UUID is worth nothing to them and the
    property holds without relying on timing (route contract §6.3, F-2).

    Proved by the pair: a real job id and an id that names nothing produce the
    same status *and the same body*. If the row were read first, the two would
    have to differ somewhere, because one of them exists.
    """
    absent = "00000000-0000-4000-8000-0000000000ff"
    cookies = callers["M"].cookies(settings)
    real = await client.get(f"/v1/council/jobs/{seeded['job_id']}", cookies=cookies)
    unreal = await client.get(f"/v1/council/jobs/{absent}", cookies=cookies)

    assert real.status_code == unreal.status_code == 403
    assert real.content == unreal.content


async def test_a_council_member_who_did_not_request_the_job_may_view_it(
    client, settings, migrated_database, callers, seeded
):
    """Council reach is role-derived (OD-37), and import work is Council-wide.

    Asserted rather than assumed, because the opposite — scoping a job to its
    requester — would look like a tightening and would be a contract violation:
    it would make a Council member unable to see the work their own guild is
    doing, and it is not what the accepted matrix says.
    """
    from tests.web.portal_fixtures import COUNCIL_ROLE_ID, TEST_GUILD_ID  # noqa: F401

    # The job was requested by `C`; `CA` is a different account that also holds
    # Council.
    response = await client.get(
        f"/v1/council/jobs/{seeded['job_id']}", cookies=callers["CA"].cookies(settings)
    )
    assert response.status_code == 200


async def test_an_administrator_alone_cannot_preview_or_apply(
    client, settings, callers, seeded
):
    """Plan §12 Phase 3 acceptance, at the route.

    *Platform Administrator alone cannot apply an import.* The same account may
    select the folder — and does, in the fixture — so this is not "the
    administrator cannot reach the snapshot": it is that holding the operational
    role does not confer the game-policy one.
    """
    cookies = callers["A"].cookies(settings)
    token = csrf_token_for(settings, callers["A"])
    headers = {
        "Origin": settings.public_origin,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    preview = await client.post(
        f"/v1/council/snapshots/{seeded['snapshot_id']}/preview-jobs",
        cookies=cookies,
        headers=headers,
        content=f"csrf_token={token}&nonce=probe",
    )
    apply = await client.post(
        f"/v1/council/jobs/{seeded['preview_job_id']}/apply",
        cookies=cookies,
        headers=headers,
        # The canonical R-46 nonce, so the `403` below is unambiguously about
        # capability rather than about a field the request got wrong anyway.
        content=(
            f"csrf_token={token}&nonce={seeded['preview_job_id']}&preview_token=x"
        ),
    )
    assert preview.status_code == 403
    assert apply.status_code == 403


async def test_council_alone_cannot_select_a_folder(
    client, settings, callers, seeded
):
    """The other half of the separation, and the reason it is two capabilities.

    Selecting a folder is an operational act and applying an import is a
    game-policy one. A Council member who could do both would be a Council member
    who could choose the scope of their own confirmation.
    """
    response = await client.post(
        f"/v1/admin/snapshots/{seeded['snapshot_id']}/folder",
        cookies=callers["C"].cookies(settings),
        headers={
            "Origin": settings.public_origin,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        content=f"csrf_token={csrf_token_for(settings, callers['C'])}&folder_id=x",
    )
    assert response.status_code == 403


async def test_a_combined_caller_acts_under_council_authority_for_apply(
    client, settings, migrated_database, callers, seeded
):
    """`CA` may apply, and the job records `guild_council`.

    Route contract §6.2: *`CA` may, and acts under capability `guild_council`,
    which is what `AuthorizationContext.capability` already returns when both are
    held.* Asserted on the durable row rather than on the response, because the
    capability an action was taken under is what the audit trail has to say.
    """
    from sqlalchemy import text

    with migrated_database.begin() as connection:
        connection.execute(
            text(
                "UPDATE reconciliation_job_results SET summary = "
                "jsonb_set(summary, '{preview_token}', '\"live-token\"') "
                "WHERE job_id = :job"
            ),
            {"job": seeded["preview_job_id"]},
        )
    response = await client.post(
        f"/v1/council/jobs/{seeded['preview_job_id']}/apply",
        cookies=callers["CA"].cookies(settings),
        headers={
            "Origin": settings.public_origin,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        content=(
            f"csrf_token={csrf_token_for(settings, callers['CA'])}"
            f"&nonce={seeded['preview_job_id']}&preview_token=live-token"
        ),
    )
    assert response.status_code == 303
    with migrated_database.begin() as connection:
        capability = connection.execute(
            text(
                "SELECT requested_capability FROM reconciliation_jobs "
                "WHERE kind = 'apply'"
            )
        ).scalar_one()
    assert capability == "guild_council"


async def _issue(client, settings, caller, method: str, path: str, seeded):
    concrete = (
        path.replace("{snapshot_id}", str(seeded["snapshot_id"]))
        .replace("{job_id}", str(seeded["job_id"]))
        .replace("{import_id}", "00000000-0000-4000-8000-000000000009")
    )
    cookies = caller.cookies(settings)
    if method == "GET":
        return await client.get(concrete, cookies=cookies)
    # A mutation carries a correct `Origin`, the right content type **and a valid
    # synchronizer token**, so the only thing a refused cell can be measuring is
    # authorization.
    body = "folder_id=probe&nonce=matrix-probe&preview_token=probe"
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
