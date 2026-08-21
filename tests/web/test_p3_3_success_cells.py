"""The twenty-six permitted cells of the §6.2 matrix, asserted one route at a time.

`test_p3_3_matrix.py` skips the `✓` cells deliberately: a permitted `GET` is
`200` and a permitted mutation is `303`, so "permitted" is not one status and
asserting it generically would assert nothing. These are the other half — what
each permitted cell actually does, including the durable effect where there is
one.

**None of them fetches the page that carries the control first.** The rule holds
in both directions: a refusal must not depend on a control not being rendered,
and a success must not depend on one being rendered.
"""
from __future__ import annotations

import pytest
from sqlalchemy import text

from tests.web.p3_3_fixtures import (
    clean_p3_3_tables,
    complete_preview,
    preview_nonce,
    seed_import,
    seed_job,
    seed_snapshot,
    select_folder,
    snapshot_bytes,
)
from tests.web.portal_fixtures import clean_p3_2_tables, csrf_token_for, seed_callers

pytestmark = pytest.mark.database

FORM = "application/x-www-form-urlencoded"


@pytest.fixture()
def callers(migrated_database, settings):
    yield seed_callers(migrated_database, settings)
    with migrated_database.begin() as connection:
        clean_p3_3_tables(connection)
        clean_p3_2_tables(connection)


@pytest.fixture()
def world(migrated_database, callers):
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
            preview_token="live-token",
        )
        queued_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        # A **second** snapshot carries the applied import, deliberately. R-40
        # lists snapshots that have *not* been applied, so putting the receipt on
        # the snapshot under test would empty the very listing the R-40 cases
        # assert — and would do it for the right reason, which is exactly the
        # kind of correct behaviour a badly arranged fixture hides.
        applied_snapshot_id, applied_checksum = seed_snapshot(
            connection, payload=snapshot_bytes(exported_at="2026-08-03T09:15:00Z")
        )
        import_id = seed_import(
            connection,
            snapshot_id=applied_snapshot_id,
            account_id=callers["C"].account_id,
            checksum=applied_checksum,
        )
    return {
        "snapshot_id": snapshot_id,
        "checksum": checksum,
        "preview_job_id": preview_id,
        "queued_job_id": queued_id,
        "applied_snapshot_id": applied_snapshot_id,
        "import_id": import_id,
    }


def _post(client, settings, caller, path, body):
    return client.post(
        path,
        cookies=caller.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, caller)}&{body}",
    )


# -- R-40 ------------------------------------------------------------------


@pytest.mark.parametrize("state", ["C", "A", "CA"])
async def test_the_snapshot_list_is_readable_by_council_and_administrator(
    client, settings, callers, world, state
):
    """R-40. Both, because the administrator needs it to choose a folder.

    The controls differ and the page says so, but `can_select_folder` and
    `can_preview` are rendering hints — the server refuses R-41 and R-42
    regardless, which the matrix suite proves without ever loading this page.
    """
    response = await client.get(
        "/v1/council/snapshots", cookies=callers[state].cookies(settings)
    )
    assert response.status_code == 200
    assert str(world["snapshot_id"]) in response.text
    # The full checksum is shown; the artifact is not reachable from anywhere.
    assert world["checksum"] in response.text
    assert "/artifact" not in response.text
    assert "/download" not in response.text
    # And the applied one is **not** listed: R-40 is the working set, and a
    # snapshot whose import committed is history reached through R-47.
    assert str(world["applied_snapshot_id"]) not in response.text


async def test_the_snapshot_list_shows_controls_only_to_the_capability_that_has_them(
    client, settings, callers, world
):
    """The honesty half of `can_select_folder` / `can_preview`.

    Asserted because a page that offered a Council member a folder selector would
    be a page that invites a request the server will refuse — which is a usability
    defect rather than a security one, and is still worth not having.
    """
    council = await client.get(
        "/v1/council/snapshots", cookies=callers["C"].cookies(settings)
    )
    administrator = await client.get(
        "/v1/council/snapshots", cookies=callers["A"].cookies(settings)
    )
    assert 'data-control="preview"' in council.text
    assert 'data-control="folder-selection"' not in council.text
    assert 'data-control="folder-selection"' in administrator.text
    assert 'data-control="preview"' not in administrator.text


# -- R-41 ------------------------------------------------------------------


@pytest.mark.parametrize("state", ["A", "CA"])
async def test_an_administrator_selects_a_folder(
    client, settings, migrated_database, callers, world, state
):
    """R-41, and the durable selection it writes."""
    from tests import foundry_fixtures as fx

    response = await _post(
        client,
        settings,
        callers[state],
        f"/v1/admin/snapshots/{world['snapshot_id']}/folder",
        f"folder_id={fx.ACTIVE_FOLDER_ID}",
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/v1/council/snapshots"
    with migrated_database.begin() as connection:
        folder = connection.execute(
            text(
                "SELECT folder_id FROM snapshot_folder_selections "
                "WHERE snapshot_id = :snapshot"
            ),
            {"snapshot": world["snapshot_id"]},
        ).scalar_one()
    assert folder == fx.ACTIVE_FOLDER_ID


# -- R-42 ------------------------------------------------------------------


@pytest.mark.parametrize("state", ["C", "CA"])
async def test_council_enqueues_a_preview_and_is_redirected_to_the_job(
    client, settings, migrated_database, callers, world, state
):
    """R-42. `303` to R-43 — never the result, which does not exist yet.

    And **no work happened in the request** (TC-JOB-01): the job is `queued`,
    with no lease, no attempt and no result.
    """
    response = await _post(
        client,
        settings,
        callers[state],
        f"/v1/council/snapshots/{world['snapshot_id']}/preview-jobs",
        f"nonce={preview_nonce(f'success-{state}')}",
    )
    assert response.status_code == 303
    location = response.headers["location"]
    assert location.startswith("/v1/council/jobs/")
    job_id = location.rsplit("/", 1)[-1]
    with migrated_database.begin() as connection:
        row = (
            connection.execute(
                text("SELECT * FROM reconciliation_jobs WHERE id = :id"),
                {"id": job_id},
            )
            .mappings()
            .one()
        )
    assert row["state"] == "queued"
    assert row["kind"] == "preview"
    assert row["attempts"] == 0
    assert row["lease_owner"] is None
    assert row["result_id"] is None


# -- R-43 and R-44 ---------------------------------------------------------


@pytest.mark.parametrize("state", ["C", "CA"])
async def test_the_job_page_renders_the_bounded_status(
    client, settings, callers, world, state
):
    """R-43. VM-15, and nothing artifact-derived in it."""
    response = await client.get(
        f"/v1/council/jobs/{world['preview_job_id']}",
        cookies=callers[state].cookies(settings),
    )
    assert response.status_code == 200
    assert 'data-job-state="completed"' in response.text
    assert 'data-control="confirm"' in response.text


@pytest.mark.parametrize("state", ["C", "CA"])
async def test_the_status_fragment_answers_with_a_retry_hint(
    client, settings, callers, world, state
):
    """R-44, and N-22's floor in `Retry-After`.

    The number is the validated `poll_min_seconds` bound rather than a literal,
    so what the response asks a browser to honour is what the settings graph
    accepted (TC-LIM-06's P3.3 consumer obligation).
    """
    response = await client.get(
        f"/v1/council/jobs/{world['queued_job_id']}/status",
        cookies=callers[state].cookies(settings),
    )
    assert response.status_code == 200
    assert int(response.headers["Retry-After"]) == settings.bounds.poll_min_seconds
    assert f'data-poll-after="{settings.bounds.poll_min_seconds}"' in response.text


async def test_polling_writes_no_audit_event(
    client, settings, migrated_database, callers, world
):
    """Route contract §6.1: *a poll is a read*.

    Auditing one would flood the append-only table with the fact that somebody
    looked at their own guild's operational state, at up to one event every two
    seconds per watcher, forever.
    """
    with migrated_database.begin() as connection:
        before = connection.execute(
            text("SELECT count(*) FROM audit_events")
        ).scalar_one()
    for _ in range(5):
        await client.get(
            f"/v1/council/jobs/{world['queued_job_id']}/status",
            cookies=callers["C"].cookies(settings),
        )
        await client.get(
            f"/v1/council/jobs/{world['queued_job_id']}",
            cookies=callers["C"].cookies(settings),
        )
    with migrated_database.begin() as connection:
        after = connection.execute(
            text("SELECT count(*) FROM audit_events")
        ).scalar_one()
    assert after == before


# -- R-45 ------------------------------------------------------------------


@pytest.mark.parametrize("state", ["C", "CA"])
async def test_council_cancels_a_queued_job(
    client, settings, migrated_database, callers, world, state
):
    """R-45. A `queued` job cancels immediately."""
    response = await _post(
        client,
        settings,
        callers[state],
        f"/v1/council/jobs/{world['queued_job_id']}/cancel",
        "",
    )
    assert response.status_code == 303
    with migrated_database.begin() as connection:
        row = (
            connection.execute(
                text("SELECT state, finished_at FROM reconciliation_jobs WHERE id = :id"),
                {"id": world["queued_job_id"]},
            )
            .mappings()
            .one()
        )
    assert row["state"] == "cancelled"
    assert row["finished_at"] is not None


# -- R-46 ------------------------------------------------------------------


@pytest.mark.parametrize("state", ["C", "CA"])
async def test_council_confirms_a_preview_by_enqueuing_an_apply(
    client, settings, migrated_database, callers, world, state
):
    """R-46. It **enqueues**; it never applies inline.

    The apply job inherits the preview's scope fingerprint — the scope a Council
    member actually confirmed — and names the preview as its parent, so the
    confirmation is traceable to the thing that was confirmed.
    """
    response = await _post(
        client,
        settings,
        callers[state],
        f"/v1/council/jobs/{world['preview_job_id']}/apply",
        # R-46's nonce is the preview job's own id — the value the confirmation
        # form renders — not a per-case label. Both parametrized callers submit
        # the identical identity and each still enqueues its own apply, because
        # the request key also includes the account.
        f"nonce={world['preview_job_id']}&preview_token=live-token",
    )
    assert response.status_code == 303
    with migrated_database.begin() as connection:
        rows = (
            connection.execute(
                text(
                    "SELECT id, kind, state, parent_job_id, scope_fingerprint, "
                    "requested_capability FROM reconciliation_jobs "
                    "WHERE kind = 'apply'"
                )
            )
            .mappings()
            .all()
        )
        preview_fingerprint = connection.execute(
            text("SELECT scope_fingerprint FROM reconciliation_jobs WHERE id = :id"),
            {"id": world["preview_job_id"]},
        ).scalar_one()
    assert len(rows) == 1
    apply_row = rows[0]
    assert apply_row["state"] == "queued"
    assert apply_row["parent_job_id"] == world["preview_job_id"]
    assert bytes(apply_row["scope_fingerprint"]) == bytes(preview_fingerprint)
    assert apply_row["requested_capability"] == "guild_council"


# -- R-47 ------------------------------------------------------------------


@pytest.mark.parametrize("state", ["C", "A", "CA"])
async def test_the_import_receipt_is_readable_by_council_and_administrator(
    client, settings, callers, world, state
):
    """R-47. Plan §6.4: import and reconciliation history is visible to both.

    And no artifact download exists anywhere in the inventory, which is why the
    receipt names a checksum rather than offering a link.
    """
    response = await client.get(
        f"/v1/council/imports/{world['import_id']}",
        cookies=callers[state].cookies(settings),
    )
    assert response.status_code == 200
    assert 'data-status="applied"' in response.text
    assert "/artifact" not in response.text


# -- R-48 and R-49 ---------------------------------------------------------


@pytest.mark.parametrize("state", ["C", "A", "CA", "BG"])
async def test_audit_search_is_readable_by_council_administrator_and_break_glass(
    client, settings, callers, world, state
):
    """R-48. `BG` is permitted, and that is N-65's surface rather than an exception.

    Reading history is how an administrator restoring continuity finds out what
    happened, and reading changes nothing — which is why the audit routes are the
    only P3.3 routes a continuity-scoped session reaches.
    """
    response = await client.get("/v1/audit", cookies=callers[state].cookies(settings))
    assert response.status_code == 200
    assert 'data-notice="append_only_no_correction_here"' in response.text


@pytest.mark.parametrize("state", ["C", "A", "CA", "BG"])
async def test_the_audit_results_fragment_is_readable_by_the_same_states(
    client, settings, callers, world, state
):
    """R-49, authorized exactly like R-48 and never relying on having been
    reached from it."""
    response = await client.get(
        "/v1/audit/results", cookies=callers[state].cookies(settings)
    )
    assert response.status_code == 200
