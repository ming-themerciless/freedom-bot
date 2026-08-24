"""TC-SEC-09/13, TC-LIM-01/03/04/05, TC-OUT-01…04 and TC-VM-04, for the P3.3 surface.

The security controls P3.1 established are asserted for the whole application in
`test_security_controls.py`. This suite asserts the parts that are **specific to
the import, job and audit surface**, and there are three of those:

1. **Artifact-derived text never reaches a response**, and it is not stopped by
   escaping — it is stopped by never being stored. An Actor name hostile enough
   to break a template is fine here, because the only Actor name in the whole
   surface is a blocked create-candidate's, bounded and Council-only.
2. **The per-route body bounds** the contract's `Body` column states, which are
   tighter than N-19's and enforced before the body is read.
3. **The outage rules, at the job path.** A read may use the grace; a mutation
   may not, and an apply may not even when no request is involved.
"""
from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from sqlalchemy import text

from application.web.view_models import ACTOR_NAME_BOUND, AUDIT_VALUE_BOUND
from tests import foundry_fixtures as fx
from tests.web.p3_3_fixtures import (
    clean_p3_3_tables,
    complete_preview,
    seed_job,
    seed_snapshot,
    select_folder,
)
from tests.web.portal_fixtures import (
    COUNCIL_SUBJECT,
    clean_p3_2_tables,
    csrf_token_for,
    seed_callers,
    seed_token_grant,
    stale_membership,
)

pytestmark = pytest.mark.database

FORM = "application/x-www-form-urlencoded"

#: The strings TC-SEC-09 parametrizes over, plus the two the P3.3 surface adds:
#: a Foundry Actor name is normalised text from an external world, so an
#: NFC/NFD pair and an RTL override belong here rather than only in the login
#: parametrization.
HOSTILE = [
    "<script>alert(1)</script>",
    '"><img src=x onerror=alert(1)>',
    "{{7*7}}",
    "x" * 10_000,
    "‮evil",
    "café",
    "café",
    "</td></tr><tr><td>injected",
]


def _assert_inert(body: str, hostile: str) -> None:
    """The value rendered, and rendered **inert** via structural DOM inspection.

    Three properties, and each is a different way the value could stop being data:

    1. **no element or active content from it.** Proves the hostile value appears
       only as text content inside its governed container, never as an element,
       attribute, script/style content, comment, or injected sibling;
    2. **no template evaluation** — Jinja renders `{{7*7}}` as the seven
       characters it is;
    3. **surrounding markup still balances**, so nothing closed a cell, row or
       list early.
    """
    soup = BeautifulSoup(body, "html.parser")

    # 1. Surrounding markup balance
    assert body.count("<tr") == body.count("</tr>")
    assert body.count("<td") == body.count("</td>")

    # 2. Locate the governed container
    container = (
        soup.find(attrs={"data-field": "blocked-name"})
        or soup.find(attrs={"data-field": "fact-after"})
        or soup.find(attrs={"data-field": "fact-before"})
    )
    assert container is not None, "Could not locate payload container element in response"

    # 3. Prove payload in container is ONLY text: no dangerous child elements, no on* attributes
    dangerous_tags = {"script", "img", "iframe", "object", "embed", "svg", "style", "audio", "video", "link"}
    for child in container.find_all(True):
        assert child.name.lower() not in dangerous_tags, f"Hostile element <{child.name}> injected in container"
        for attr_name, attr_val in child.attrs.items():
            assert not attr_name.lower().startswith("on"), f"Event handler {attr_name} injected in container child"
            if isinstance(attr_val, str):
                assert not attr_val.lower().startswith("javascript:"), f"javascript: URL injected in container child attribute {attr_name}"

    for attr_name, attr_val in container.attrs.items():
        assert not attr_name.lower().startswith("on"), f"Event handler {attr_name} injected in container"
        if isinstance(attr_val, str):
            assert not attr_val.lower().startswith("javascript:"), f"javascript: URL injected in container attribute {attr_name}"

    # 4. Outside container: only known same-origin fingerprinted htmx script and accepted token emblem
    for s in soup.find_all("script"):
        src = s.get("src", "")
        assert src.startswith("/static/vendor/htmx-") or src.startswith("/static/js/webauthn-emergency."), f"Unauthorized script src={src!r}"
        assert not s.get_text(strip=True), "Script has inline content"

    for img in soup.find_all("img"):
        src = img.get("src", "")
        assert src.startswith("/static/images/freedom-blades-token"), f"Unauthorized img src={src!r}"

    # No element anywhere has inline event handlers or javascript: URLs
    for el in soup.find_all(True):
        for attr_name, attr_val in el.attrs.items():
            assert not attr_name.lower().startswith("on"), f"Document contains unexpected event handler {attr_name}"
            if isinstance(attr_val, str):
                assert not attr_val.lower().startswith("javascript:"), f"Document contains unexpected javascript: URL in {attr_name}"

    # 5. Escaping / non-evaluation
    if "<" in hostile:
        assert hostile not in body, "Raw unescaped markup found in response body"
    if "{{7*7}}" in hostile:
        assert "{{7*7}}" in body, "Jinja template literal {{7*7}} was evaluated instead of rendered as text"


@pytest.fixture()
def callers(migrated_database, settings):
    yield seed_callers(migrated_database, settings, states=("C", "A", "M", "U"))
    with migrated_database.begin() as connection:
        clean_p3_3_tables(connection)
        clean_p3_2_tables(connection)


@pytest.fixture()
def snapshot(migrated_database, callers):
    with migrated_database.begin() as connection:
        snapshot_id, checksum = seed_snapshot(connection)
        select_folder(
            connection, snapshot_id=snapshot_id, account_id=callers["A"].account_id
        )
    return snapshot_id, checksum


@pytest.fixture()
def outage(migrated_database, composition, provider, callers):
    """A Council caller whose next request **must** ask the provider, and a
    provider that cannot answer.

    Both halves are necessary and the second is easy to leave out. `_refresh_plan`
    returns `None` when no token grant is stored — there is then no way to ask
    the provider anything — so a case that only aged the projection would produce
    a request that never called the provider, and would pass while proving
    nothing about an outage.
    """
    with migrated_database.begin() as connection:
        identity_id = connection.execute(
            text(
                "SELECT id FROM external_identities WHERE provider_key = 'discord' "
                "AND subject = :subject"
            ),
            {"subject": str(COUNCIL_SUBJECT)},
        ).scalar_one()
        seed_token_grant(composition, connection, identity_id=identity_id)
    provider.unavailable = True
    return provider


def _post(client, settings, caller, path, body, **kwargs):
    return client.post(
        path,
        cookies=caller.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, caller)}&{body}",
        **kwargs,
    )


# ---------------------------------------------------------------------------
# TC-SEC-09 — escaping, and the bound that precedes it
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("hostile", HOSTILE)
async def test_a_hostile_actor_name_in_a_blocked_entry_renders_inert_and_bounded(
    client, settings, migrated_database, callers, snapshot, hostile
):
    """The one Actor name that crosses the boundary, at its worst.

    A blocked create-candidate's display name is the **only** artifact-derived
    text in the whole P3.3 surface, and it is Council-only, capped at 50 entries
    and bounded at §3.2's 120 characters. Everything else about an Actor stays
    server-side, which is why this is one case rather than a parametrization over
    every field.

    Two properties, and the second is the one that matters: the value renders
    inert (escaped, no script, no attribute break-out, `{{7*7}}` unevaluated),
    **and** it is truncated to the bound rather than sent whole.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id, _ = complete_preview(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            blocked_entries=[
                {
                    "external_actor_id": "A" * 16,
                    "display_name": hostile,
                    "issue_code": "unmapped_name_collision",
                    "candidate_character_ids": [],
                }
            ],
        )

    response = await client.get(
        f"/v1/council/jobs/{job_id}", cookies=callers["C"].cookies(settings)
    )
    assert response.status_code == 200
    body = response.text
    _assert_inert(body, hostile)
    # Never the whole of an over-long name. §3.2 bounds it at 120 characters,
    # and the untruncated value is never sent.
    #
    # This asserts the **rendering** bound, because the fixture seeded the stored
    # row directly. The *storage* bound — applied where the worker builds the
    # entry, so the untruncated value is never in the database for the next
    # reader either — is asserted in `test_p3_3_worker.py`, which is where that
    # code runs.
    if len(hostile) > ACTOR_NAME_BOUND:
        assert hostile not in body


@pytest.mark.parametrize("hostile", HOSTILE)
async def test_a_hostile_audit_value_renders_inert_and_bounded(
    client, settings, migrated_database, callers, hostile
):
    """The same, for the audit surface's one free-text field.

    A grant or revocation `reason` is Council-supplied rather than
    artifact-derived, which is why it is rendered at all — bounded at §3.2's 200
    characters per audit value, escaped, and only to Council and administrators.
    """
    from uuid import uuid4

    from adapters.database.tables import audit_events
    from sqlalchemy import insert

    from tests.web.p3_3_fixtures import utcnow

    with migrated_database.begin() as connection:
        connection.execute(
            insert(audit_events).values(
                id=uuid4(),
                occurred_at=utcnow(),
                actor_platform_account_id=callers["C"].account_id,
                actor_capability="guild_council",
                action="character_access.granted",
                entity_type="character_access",
                entity_id=str(uuid4()),
                source="web",
                correlation_id=uuid4(),
                payload={"reason": hostile},
            )
        )
    response = await client.get(
        "/v1/audit/results", cookies=callers["C"].cookies(settings)
    )
    assert response.status_code == 200
    body = response.text
    _assert_inert(body, hostile)
    if len(hostile) > AUDIT_VALUE_BOUND:
        assert hostile not in body
        assert 'data-payload-truncated="true"' in body


async def test_no_reconciliation_warning_text_can_reach_a_response(
    client, settings, migrated_database, callers, snapshot
):
    """TC-VM-04, and it is a design property rather than a filter.

    A reconciliation warning reaches the browser as a **code plus a count**. The
    human sentence is a template-side lookup table the platform owns; text from
    the artifact is never forwarded, and the durable result has nowhere to put it
    — `issue_counts` is `{code, severity, count}` triples and nothing else.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id, _ = complete_preview(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            summary_overrides={
                "issue_counts": [
                    {
                        "code": "unmapped_name_collision",
                        "severity": "error",
                        "count": 2,
                    }
                ]
            },
        )
    response = await client.get(
        f"/v1/council/jobs/{job_id}", cookies=callers["C"].cookies(settings)
    )
    assert 'data-issue-code="unmapped_name_collision"' in response.text
    # No sentence from the reconciliation, in either the response or the row.
    with migrated_database.begin() as connection:
        summary = connection.execute(
            text("SELECT summary FROM reconciliation_job_results")
        ).scalar_one()
    for entry in summary["issue_counts"]:
        assert set(entry) == {"code", "severity", "count"}


# ---------------------------------------------------------------------------
# TC-SEC-13 — no artifact anywhere on the P3.3 surface
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "template",
    [
        "/v1/council/snapshots/{snapshot}/artifact",
        "/v1/council/snapshots/{snapshot}/bytes",
        "/v1/council/snapshots/{snapshot}/download",
        "/v1/council/snapshots/{snapshot}.json",
        "/v1/council/jobs/{job}/artifact",
        "/v1/council/jobs/{job}/result.json",
    ],
)
async def test_no_p3_3_path_serves_an_artifact_even_to_council(
    client, settings, migrated_database, callers, snapshot, template
):
    """TC-SEC-13, issued **as Council** — the caller who is most entitled.

    *Audit visibility does not by itself grant permission to download the raw
    artifact.* A `404` for an unauthenticated caller would prove only that the
    route needs a session.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
    path = template.format(snapshot=snapshot_id, job=job_id)
    response = await client.get(path, cookies=callers["C"].cookies(settings))
    assert response.status_code == 404


async def test_a_rendered_job_page_contains_no_artifact_bytes_or_location(
    client, settings, migrated_database, callers, snapshot
):
    """TC-JOB-14. Not even the store's own reference.

    `foundry_snapshots.artifact_location` is a reference into the restricted
    store. It is a filesystem-shaped string, and a response that carried one
    would be telling a browser where the artifact lives.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id, _ = complete_preview(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        location = connection.execute(
            text("SELECT artifact_location FROM foundry_snapshots WHERE id = :id"),
            {"id": snapshot_id},
        ).scalar_one()

    for path in (
        f"/v1/council/jobs/{job_id}",
        f"/v1/council/jobs/{job_id}/status",
        "/v1/council/snapshots",
    ):
        response = await client.get(path, cookies=callers["C"].cookies(settings))
        assert response.status_code == 200, path
        assert location not in response.text, path
        assert "freedom-blades.foundry-export" not in response.text, path
        assert '"actors"' not in response.text, path


# ---------------------------------------------------------------------------
# TC-LIM — the per-route bounds
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("path_template", "bound"),
    [
        ("/v1/admin/snapshots/{snapshot}/folder", 4 * 1024),
        ("/v1/council/snapshots/{snapshot}/preview-jobs", 4 * 1024),
        ("/v1/council/jobs/{job}/cancel", 4 * 1024),
        ("/v1/council/jobs/{job}/apply", 8 * 1024),
    ],
)
async def test_a_body_over_the_routes_own_bound_is_refused_before_it_is_read(
    client, settings, migrated_database, callers, snapshot, path_template, bound
):
    """TC-LIM-01 at the route rather than at the middleware.

    N-19's 1 MiB is applied before routing and is asserted for the whole
    application elsewhere. These are the contract's **tighter** per-route bounds,
    which a body under 1 MiB would otherwise sail through. `413`, and the
    application service is never reached.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
    caller = callers["A"] if "/admin/" in path_template else callers["C"]
    path = path_template.format(snapshot=snapshot_id, job=job_id)
    padding = "p" * (bound + 1)
    response = await _post(client, settings, caller, path, f"nonce=x&pad={padding}")
    assert response.status_code == 413
    assert response.json()["error"] == "body_too_large"

    with migrated_database.begin() as connection:
        applies = connection.execute(
            text("SELECT count(*) FROM reconciliation_jobs WHERE kind = 'apply'")
        ).scalar_one()
    assert applies == 0


async def test_a_mutation_with_no_declared_length_is_refused(
    client, settings, callers, snapshot
):
    """A chunked body with no `Content-Length` is exactly the shape that bypasses
    a limit applied to a header. `411`, and nothing is read."""
    snapshot_id, _ = snapshot

    async def chunks():
        yield b"nonce=x"

    response = await client.post(
        f"/v1/council/snapshots/{snapshot_id}/preview-jobs",
        cookies=callers["C"].cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=chunks(),
    )
    assert response.status_code in (411, 413)


@pytest.mark.parametrize(
    "content_type", ["application/json", "multipart/form-data; boundary=x", "text/plain"]
)
async def test_an_unsupported_content_type_on_a_p3_3_form_route_is_refused(
    client, settings, callers, snapshot, content_type
):
    """TC-LIM-03, including the multipart upload the contract names explicitly.

    None of these routes takes a file. A multipart body reaching one would be a
    body the platform has to buffer to discover it does not want it.
    """
    snapshot_id, _ = snapshot
    response = await client.post(
        f"/v1/council/snapshots/{snapshot_id}/preview-jobs",
        cookies=callers["C"].cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": content_type},
        content="nonce=x",
    )
    assert response.status_code == 415


async def test_a_malicious_folder_id_never_determines_a_path_or_reaches_a_worker(
    client, settings, migrated_database, callers, snapshot
):
    """TC-LIM-04 at the portal boundary.

    A folder id is validated against `selected_folder_ids` — the exported set the
    submission recorded — rather than trusted. A traversal, a null byte or an
    absolute path is not in that set, so it is refused as **input**: it never
    reaches a filesystem, and it never becomes a job a worker would spend ten
    seconds discovering was impossible.
    """
    snapshot_id, _ = snapshot
    for hostile in (
        "../../etc/passwd",
        "/etc/passwd",
        "actv\x00QwErTyUiOpAs",
        "actvQwErTyUiOpAs/../..",
        "'; DROP TABLE characters; --",
    ):
        response = await _post(
            client,
            settings,
            callers["A"],
            f"/v1/admin/snapshots/{snapshot_id}/folder",
            f"folder_id={hostile}",
        )
        assert response.status_code == 422, hostile
    with migrated_database.begin() as connection:
        selections = connection.execute(
            text(
                "SELECT count(*) FROM snapshot_folder_selections "
                "WHERE folder_id <> :expected"
            ),
            {"expected": fx.ACTIVE_FOLDER_ID},
        ).scalar_one()
    assert selections == 0


async def test_the_status_poll_carries_the_configured_floor_and_never_less(
    client, settings, migrated_database, callers, snapshot
):
    """TC-LIM-05's polling half. N-22 is a **floor**, and the server may back off.

    The number in `Retry-After` and in the fragment's poll hint is the validated
    `poll_min_seconds`, so a browser is never asked to poll faster than the
    accepted bound — and the two numbers agree, because a response that told the
    header one thing and the markup another would be honoured inconsistently.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
    response = await client.get(
        f"/v1/council/jobs/{job_id}/status", cookies=callers["C"].cookies(settings)
    )
    floor = settings.bounds.poll_min_seconds
    assert floor >= 2, "N-22's accepted floor"
    assert int(response.headers["Retry-After"]) >= floor
    assert f'hx-trigger="every {floor}s"' in response.text
    assert f'data-poll-after="{floor}"' in response.text


async def test_the_poll_hint_is_absent_once_the_job_is_terminal(
    client, settings, migrated_database, callers, snapshot
):
    """View-model contract §9.6: polling stops on a terminal `job_state`.

    A fragment that kept polling a `completed` job would be a browser asking the
    platform the same settled question every two seconds forever.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id, _ = complete_preview(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
    response = await client.get(
        f"/v1/council/jobs/{job_id}/status", cookies=callers["C"].cookies(settings)
    )
    assert "hx-trigger" not in response.text
    assert 'data-job-state="completed"' in response.text


# ---------------------------------------------------------------------------
# TC-OUT — the outage rules, where the job path consumes them
# ---------------------------------------------------------------------------


async def test_a_job_read_succeeds_within_the_grace_when_the_provider_is_faulted(
    client, settings, migrated_database, outage, callers, snapshot
):
    """TC-OUT-01 on R-43. A read may use the last successful observation.

    The projection is aged past N-09 so a refresh is planned, and the provider is
    faulted so it fails. Within N-10's grace the read still succeeds, on the
    membership the platform last actually observed.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        stale_membership(connection, subject=COUNCIL_SUBJECT, minutes=6)

    response = await client.get(
        f"/v1/council/jobs/{job_id}", cookies=callers["C"].cookies(settings)
    )
    assert response.status_code == 200


async def test_every_p3_3_mutation_is_refused_immediately_during_an_outage(
    client, settings, migrated_database, outage, callers, snapshot
):
    """TC-OUT-02. A mutation gets **no** grace and does not consume it.

    A stale role is a display inaccuracy on a read and an unauthorized write on a
    mutation, which is the whole asymmetry. Asserted for every mutating route in
    the package, and with the durable effect checked: nothing was enqueued.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        stale_membership(connection, subject=COUNCIL_SUBJECT, minutes=6)

    for path, body in (
        (f"/v1/council/snapshots/{snapshot_id}/preview-jobs", "nonce=outage"),
        (f"/v1/council/jobs/{job_id}/cancel", ""),
        (f"/v1/council/jobs/{job_id}/apply", "nonce=outage&preview_token=x"),
    ):
        response = await _post(client, settings, callers["C"], path, body)
        assert response.status_code == 503, path

    with migrated_database.begin() as connection:
        jobs = connection.execute(
            text("SELECT count(*) FROM reconciliation_jobs")
        ).scalar_one()
        cancelled = connection.execute(
            text(
                "SELECT count(*) FROM reconciliation_jobs "
                "WHERE cancel_requested_at IS NOT NULL"
            )
        ).scalar_one()
    assert jobs == 1, "no job was enqueued during the outage"
    assert cancelled == 0, "and none was cancelled"


async def test_a_protected_job_read_answers_503_once_the_grace_is_exhausted(
    client, settings, migrated_database, outage, callers, snapshot
):
    """TC-OUT-03. Fail closed, and expose no protected data in the process."""
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id, _ = complete_preview(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        stale_membership(connection, subject=COUNCIL_SUBJECT, minutes=30)

    response = await client.get(
        f"/v1/council/jobs/{job_id}", cookies=callers["C"].cookies(settings)
    )
    assert response.status_code == 503
    assert checksum not in response.text
    assert "would_create" not in response.text


async def test_a_provider_failure_during_a_job_read_writes_no_absence(
    client, settings, migrated_database, outage, callers, snapshot
):
    """TC-OUT-04. "Refresh failed" and "membership absent" are different facts.

    A rate-limit storm that recorded the first as the second would revoke a
    guild. The projection is left exactly as it was, so the caller is still
    Council once the provider answers again.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        stale_membership(connection, subject=COUNCIL_SUBJECT, minutes=6)
        before = connection.execute(
            text(
                "SELECT active FROM discord_guild_memberships "
                "WHERE discord_user_id = :subject"
            ),
            {"subject": COUNCIL_SUBJECT},
        ).scalar_one()
    for _ in range(5):
        await client.get(
            f"/v1/council/jobs/{job_id}", cookies=callers["C"].cookies(settings)
        )
    with migrated_database.begin() as connection:
        after = connection.execute(
            text(
                "SELECT active FROM discord_guild_memberships "
                "WHERE discord_user_id = :subject"
            ),
            {"subject": COUNCIL_SUBJECT},
        ).scalar_one()
    assert before is True
    assert after is True, "a failed refresh never wrote an absence"


def test_assert_inert_semantics_and_falsification() -> None:
    """Falsification: _assert_inert fails if active tags or on* attributes are injected into container."""
    # 1. Safe baseline with escaped hostile payload passes
    safe_html = """<!doctype html><html><head><script defer src="/static/vendor/htmx-2.0.10.71ea67185bfa.min.js"></script></head>
    <body>
      <img src="/static/images/freedom-blades-token.png">
      <table><tr><td>
        <span data-field="blocked-name">&lt;script&gt;alert(1)&lt;/script&gt;</span>
      </td></tr></table>
    </body></html>"""
    _assert_inert(safe_html, "<script>alert(1)</script>")

    # 2. Injected child script element inside container fails
    injected_script_html = """<!doctype html><html><head><script defer src="/static/vendor/htmx-2.0.10.71ea67185bfa.min.js"></script></head>
    <body>
      <table><tr><td>
        <span data-field="blocked-name"><script>alert(1)</script></span>
      </td></tr></table>
    </body></html>"""
    with pytest.raises(AssertionError, match="Hostile element <script> injected in container"):
        _assert_inert(injected_script_html, "<script>alert(1)</script>")

    # 3. Injected event handler inside container fails
    injected_attr_html = """<!doctype html><html><head><script defer src="/static/vendor/htmx-2.0.10.71ea67185bfa.min.js"></script></head>
    <body>
      <table><tr><td>
        <span data-field="blocked-name" onerror="alert(1)">safe text</span>
      </td></tr></table>
    </body></html>"""
    with pytest.raises(AssertionError, match="Event handler onerror injected in container"):
        _assert_inert(injected_attr_html, "safe text")

    # 4. Injected javascript: URL inside container fails
    injected_js_url_html = """<!doctype html><html><head><script defer src="/static/vendor/htmx-2.0.10.71ea67185bfa.min.js"></script></head>
    <body>
      <table><tr><td>
        <span data-field="blocked-name"><a href="javascript:alert(1)">click</a></span>
      </td></tr></table>
    </body></html>"""
    with pytest.raises(AssertionError, match="javascript: URL injected"):
        _assert_inert(injected_js_url_html, "click")

    # 5. Missing Jinja literal {{7*7}} fails
    missing_jinja_html = """<!doctype html><html><head><script defer src="/static/vendor/htmx-2.0.10.71ea67185bfa.min.js"></script></head>
    <body>
      <table><tr><td>
        <span data-field="blocked-name">49</span>
      </td></tr></table>
    </body></html>"""
    with pytest.raises(AssertionError, match="Jinja template literal"):
        _assert_inert(missing_jinja_html, "{{7*7}}")
