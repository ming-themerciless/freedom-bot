"""TC-AUD-01 to TC-AUD-08: bounded audit search, and everything it will not do.

The audit table is the one table in the platform that grows forever and is never
edited, so its read surface is where two different kinds of mistake would show
up: a query that gets slower every day until it stops working, and a rendering
that forwards something it should not.

The suite is arranged around those two, plus the third property that is an
absence: **there is no audit export, mutation or deletion anywhere** — no route,
no application method, and no grant.
"""
from __future__ import annotations

import ast
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import insert, text
from sqlalchemy.exc import DBAPIError, ProgrammingError

from adapters.database.tables import audit_events
from adapters.web.import_routes import P3_3_ROUTE_INVENTORY
from application.audit import ActorCapability, AuditEvent, AuditSource
from application.web.audit_search import (
    FILTER_VALUE_BOUND,
    MAX_RANGE_DAYS,
    RENDERED_PAYLOAD_KEYS,
    AuditSearchService,
)
from tests.web.p3_3_fixtures import clean_p3_3_tables, utcnow
from tests.web.portal_fixtures import clean_p3_2_tables, seed_callers

pytestmark = pytest.mark.database

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture()
def callers(migrated_database, settings):
    yield seed_callers(migrated_database, settings)
    with migrated_database.begin() as connection:
        clean_p3_3_tables(connection)
        clean_p3_2_tables(connection)


def seed_events(connection, *, account_id, count: int, action: str = "test.event"):
    """`count` append-only events, one second apart, newest last.

    Spaced in time so `(occurred_at DESC, id DESC)` has a real order to page
    through rather than a heap of identical timestamps, and so the cursor's
    trailing primary key is not the only thing distinguishing rows.
    """
    moment = utcnow() - timedelta(seconds=count + 1)
    identifiers = []
    for index in range(count):
        event_id = uuid4()
        identifiers.append(event_id)
        connection.execute(
            insert(audit_events).values(
                id=event_id,
                occurred_at=moment + timedelta(seconds=index),
                actor_platform_account_id=account_id,
                actor_capability="guild_council",
                action=f"{action}.{index:03d}",
                entity_type="reconciliation_job",
                entity_id=str(uuid4()),
                source="web",
                correlation_id=uuid4(),
                payload={"kind": "preview", "folder_id": "actv0000"},
            )
        )
    return identifiers


# ---------------------------------------------------------------------------
# TC-AUD-02 — bounded pagination
# ---------------------------------------------------------------------------


async def test_pagination_is_bounded_and_a_request_for_a_thousand_is_clamped(
    client, settings, migrated_database, callers
):
    """TC-AUD-02. N-21: default 50, maximum 100, cursor-based.

    Clamped rather than refused, deliberately: an oversized page is a caller
    asking for more than the platform will give, which has an obvious safe
    answer. An **unverifiable cursor** is a caller presenting something the
    platform did not mint, which does not — see the case below.
    """
    with migrated_database.begin() as connection:
        seed_events(connection, account_id=callers["C"].account_id, count=120)

    default = await client.get("/v1/audit/results", cookies=callers["C"].cookies(settings))
    huge = await client.get(
        "/v1/audit/results?size=1000", cookies=callers["C"].cookies(settings)
    )
    assert default.status_code == huge.status_code == 200
    assert default.text.count("data-event-id=") == settings.bounds.audit_page_size_default
    assert huge.text.count("data-event-id=") == settings.bounds.audit_page_size_max


async def test_no_count_star_is_issued_over_the_audit_table(
    client, settings, migrated_database, callers
):
    """`total_is_unbounded` is permanently true, and it is not a placeholder.

    A `COUNT(*)` over an append-only log **is** the unbounded scan N-21 forbids.
    Asserted at the statement rather than at the view: every statement the
    request issues is captured, and none of them counts audit rows.
    """
    from sqlalchemy import event

    with migrated_database.begin() as connection:
        seed_events(connection, account_id=callers["C"].account_id, count=10)

    statements: list[str] = []

    def record(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(migrated_database, "before_cursor_execute", record)
    try:
        response = await client.get(
            "/v1/audit/results", cookies=callers["C"].cookies(settings)
        )
    finally:
        event.remove(migrated_database, "before_cursor_execute", record)

    assert response.status_code == 200
    counting = [
        statement
        for statement in statements
        if "count(" in statement.lower() and "audit_events" in statement.lower()
    ]
    assert counting == [], counting
    assert 'data-total-unbounded="true"' in response.text


async def test_the_cursor_pages_forward_without_repeating_or_dropping_a_row(
    client, settings, migrated_database, callers
):
    """The cursor is a **position**, not an offset.

    An offset is wrong in a table that receives inserts while a reader is paging:
    a row added before the cursor shifts every later page by one and the reader
    either sees a row twice or never sees it. Proved by paging the whole set and
    asserting the union is exactly the seeded set, with no duplicate.
    """
    with migrated_database.begin() as connection:
        seeded = seed_events(connection, account_id=callers["C"].account_id, count=25)

    seen: list[str] = []
    url = "/v1/audit/results?size=10"
    for _ in range(5):
        response = await client.get(url, cookies=callers["C"].cookies(settings))
        assert response.status_code == 200
        import re

        seen.extend(re.findall(r'data-event-id="([^"]+)"', response.text))
        match = re.search(r'href="(/v1/audit/results\?cursor=[^"]+)"', response.text)
        if match is None:
            break
        url = match.group(1)

    assert len(seen) == len(set(seen)), "a row was paged twice"
    assert set(seen) == {str(identifier) for identifier in seeded}


async def test_a_tampered_or_unsigned_cursor_is_refused_never_reset(
    client, settings, migrated_database, callers
):
    """TC-AUD-03, N-64. A silently reset cursor hides tampering behind a page
    that looks like it worked.

    Three shapes: no signature at all, a signature that does not verify, and a
    cursor minted for **another listing**. The third is what the scope string is
    for — a cursor from the snapshot listing decodes to a valid position and
    would page a different table.
    """
    from application.web.pagination import encode
    from application.web.snapshot_admin import SNAPSHOT_CURSOR_SCOPE

    with migrated_database.begin() as connection:
        seed_events(connection, account_id=callers["C"].account_id, count=3)

    foreign = encode(
        settings.cursor_key,
        scope=SNAPSHOT_CURSOR_SCOPE,
        parts=(utcnow().isoformat(), str(uuid4())),
    )
    for cursor in ("not-a-cursor", "YWJj.bm90LWEtc2lnbmF0dXJl", foreign):
        response = await client.get(
            f"/v1/audit/results?cursor={cursor}",
            cookies=callers["C"].cookies(settings),
        )
        assert response.status_code == 422, cursor
        assert "data-event-id=" not in response.text, cursor


# ---------------------------------------------------------------------------
# N-63 — filter bounds
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "query",
    [
        # A value over the 120-character bound.
        f"action={'a' * (FILTER_VALUE_BOUND + 1)}",
        # More than five simultaneous filters.
        (
            "action=a&entity_type=b&entity_id=c&capability=guild_council"
            "&source=web&correlation_id=00000000-0000-4000-8000-000000000000"
        ),
        # A range over 366 days.
        "from=2020-01-01T00:00:00Z&to=2026-01-01T00:00:00Z",
        # A range that runs backwards.
        "from=2026-01-02T00:00:00Z&to=2026-01-01T00:00:00Z",
        # A capability outside the closed vocabulary.
        "capability=emperor",
        # A source outside the closed vocabulary.
        "source=telepathy",
        # A malformed correlation id.
        "correlation_id=not-a-uuid",
        # A malformed instant.
        "from=yesterday",
    ],
)
async def test_the_accepted_filter_bounds_are_enforced(
    client, settings, migrated_database, callers, query
):
    """N-63, and each case is refused rather than quietly dropped.

    A filter the platform silently ignored would answer a different question from
    the one asked, and an operator reading an audit result has to be able to
    trust that the rows shown are the rows that match.
    """
    with migrated_database.begin() as connection:
        seed_events(connection, account_id=callers["C"].account_id, count=3)
    response = await client.get(
        f"/v1/audit/results?{query}", cookies=callers["C"].cookies(settings)
    )
    assert response.status_code == 422, query
    assert "data-event-id=" not in response.text


async def test_the_action_filter_is_a_prefix_and_not_a_substring(
    client, settings, migrated_database, callers
):
    """`reconciliation.` is an index range; `%council%` is a scan of every row.

    The distinction is a performance control on a table that grows forever, and
    it is also a disclosure control: a substring search over actions is one
    keystroke away from wanting a substring search over payloads.
    """
    with migrated_database.begin() as connection:
        connection.execute(
            insert(audit_events).values(
                id=uuid4(),
                occurred_at=utcnow(),
                actor_platform_account_id=callers["C"].account_id,
                actor_capability="guild_council",
                action="reconciliation.job_queued",
                entity_type="reconciliation_job",
                entity_id=str(uuid4()),
                source="web",
                correlation_id=uuid4(),
                payload={},
            )
        )
    cookies = callers["C"].cookies(settings)
    prefix = await client.get("/v1/audit/results?action=reconciliation.", cookies=cookies)
    middle = await client.get("/v1/audit/results?action=job_queued", cookies=cookies)
    assert prefix.text.count("data-event-id=") == 1
    assert middle.text.count("data-event-id=") == 0


async def test_a_filter_value_containing_sql_wildcards_matches_literally(
    client, settings, migrated_database, callers
):
    """`autoescape=True` on the prefix match, asserted rather than assumed.

    Without it, `%` and `_` in a caller-supplied prefix would be wildcards, and
    a filter of `%` would return the whole table — the unbounded scan N-21
    forbids, reachable from a text box.
    """
    with migrated_database.begin() as connection:
        seed_events(connection, account_id=callers["C"].account_id, count=5)
    response = await client.get(
        "/v1/audit/results?action=%25", cookies=callers["C"].cookies(settings)
    )
    assert response.status_code == 200
    assert response.text.count("data-event-id=") == 0


# ---------------------------------------------------------------------------
# TC-AUD-04, TC-AUD-08 — the absences
# ---------------------------------------------------------------------------


def test_no_application_repository_offers_an_audit_update_or_delete():
    """TC-AUD-04's structural half, over the **AST** rather than by grepping.

    Every module under `application/` and `adapters/` is parsed, and any
    statement that would `update()` or `delete()` `audit_events` is a finding.
    A text search would report the word in a docstring and miss
    `getattr(sqlalchemy, "delete")`; this reports neither.
    """
    findings: list[str] = []
    for directory in ("application", "adapters"):
        for path in sorted((ROOT / directory).glob("**/*.py")):
            if "__pycache__" in path.parts:
                continue
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = getattr(node.func, "id", None) or getattr(
                    node.func, "attr", None
                )
                if name not in ("update", "delete"):
                    continue
                for argument in node.args:
                    if (
                        isinstance(argument, ast.Name)
                        and argument.id == "audit_events"
                    ):
                        findings.append(f"{path}:{node.lineno}")
    assert findings == [], findings


def test_the_audit_search_repository_declares_no_write_method():
    """Not "no write is called": **no write method exists**.

    Asserted by introspection, because a method that existed and was never called
    would be a method a later caller could find.
    """
    from adapters.web.repositories import AuditSearchRepository

    public = {
        name
        for name in dir(AuditSearchRepository)
        if not name.startswith("_")
    }
    assert public == {"search", "labels_for_discord_actors"}


def test_there_is_no_audit_export_mutation_or_deletion_route():
    """TC-AUD-08, over the closed inventory.

    The only audit routes are R-48 and R-49, both `GET`. Asserted against the
    inventory rather than against the application, so it holds even for a route
    somebody registered without adding it to the inventory — that one fails
    `TC-STRUCT-01` instead.
    """
    audit_routes = {
        identifier: pair
        for identifier, pair in P3_3_ROUTE_INVENTORY.items()
        if pair[1].startswith("/v1/audit")
    }
    assert audit_routes == {
        "R-48": ("GET", "/v1/audit"),
        "R-49": ("GET", "/v1/audit/results"),
    }
    assert all(method == "GET" for method, _ in audit_routes.values())


@pytest.mark.parametrize(
    "statement",
    [
        "UPDATE audit_events SET action = 'tampered'",
        # The statement a well-meaning backfill would issue: an update that
        # touches **only** the column migration 0006 added.
        "UPDATE audit_events SET actor_platform_account_id = NULL",
        "DELETE FROM audit_events",
    ],
)
def test_the_schema_owner_cannot_rewrite_audit_history(migrated_database, statement):
    """TC-AUD-04's trigger half: refused **for the owner too**.

    The runtime role is denied by grant, which
    `tests/test_runtime_grants_live.py` proves; this is the independent second
    control, and it is the one that holds when somebody connects as the migration
    role to fix something by hand.
    """
    with migrated_database.begin() as connection:
        connection.execute(
            insert(audit_events).values(
                id=uuid4(),
                occurred_at=utcnow(),
                actor_capability="system",
                action="probe.event",
                entity_type="probe",
                entity_id="1",
                source="system",
                correlation_id=uuid4(),
                payload={},
            )
        )
    with pytest.raises((DBAPIError, ProgrammingError)):
        with migrated_database.begin() as connection:
            connection.execute(text(statement))
    with migrated_database.begin() as connection:
        surviving = connection.execute(
            text("SELECT action FROM audit_events WHERE entity_type = 'probe'")
        ).scalar_one()
    assert surviving == "probe.event"


@pytest.mark.parametrize(
    ("table", "privilege", "expected"),
    [
        # Schema §11.2's bands for the three tables migration 0011 adds, asserted
        # as **effective** privileges rather than as template text.
        ("reconciliation_jobs", "SELECT", True),
        ("reconciliation_jobs", "INSERT", True),
        ("reconciliation_jobs", "UPDATE", True),
        # No DELETE: N-24's retention sweep is an operator action run as the
        # schema owner, not something the web process or the worker may do to its
        # own queue. A runtime role that could delete a job could delete the
        # record of a refused apply.
        ("reconciliation_jobs", "DELETE", False),
        ("reconciliation_jobs", "TRUNCATE", False),
        ("snapshot_folder_selections", "SELECT", True),
        ("snapshot_folder_selections", "INSERT", True),
        ("snapshot_folder_selections", "UPDATE", True),
        ("snapshot_folder_selections", "DELETE", False),
        ("snapshot_folder_selections", "TRUNCATE", False),
        # The result table **does** hold DELETE: the worker replaces a superseded
        # result, and `ON DELETE CASCADE` from the job carries it with a purge.
        ("reconciliation_job_results", "SELECT", True),
        ("reconciliation_job_results", "INSERT", True),
        ("reconciliation_job_results", "UPDATE", True),
        ("reconciliation_job_results", "DELETE", True),
        ("reconciliation_job_results", "TRUNCATE", False),
    ],
)
def test_the_runtime_role_holds_exactly_the_accepted_p3_3_grants(
    migrated_database, table, privilege, expected
):
    """Schema §11.2 for migration 0011's tables, as PostgreSQL concludes it.

    `has_table_privilege` rather than a parse of the template: the evidence has
    to be the cluster's answer, including anything PUBLIC drift would have added,
    which is the whole finding O-1 the template's normalisation exists for.
    """
    from tests.test_runtime_grants_live import RUNTIME_ROLE, grant_statements

    with migrated_database.begin() as owner:
        exists = owner.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :role"),
            {"role": RUNTIME_ROLE},
        ).scalar()
        if not exists:
            pytest.skip(f"{RUNTIME_ROLE} does not exist")
        for statement in grant_statements():
            owner.execute(text(statement))
        held = owner.execute(
            text("SELECT has_table_privilege(:role, :table, :privilege)"),
            {"role": RUNTIME_ROLE, "table": table, "privilege": privilege},
        ).scalar_one()
    assert held is expected, f"{RUNTIME_ROLE} {privilege} on {table}"


# ---------------------------------------------------------------------------
# TC-AUD-06, TC-AUD-07 — what a rendered row may contain
# ---------------------------------------------------------------------------


def test_an_unrecognized_payload_key_renders_as_a_redacted_key(settings):
    """TC-AUD-07. A key with **no value at all** — not truncated, not a type.

    The direction of the rule is what makes it a control. A projection that
    rendered every key and redacted a denylist would be safe only for the keys
    somebody remembered; this one renders a key **only** if the projection
    recognizes it. So a future writer that puts a new key in a payload widens the
    audit table and does not widen the response.
    """
    service = AuditSearchService(
        audit=None, accounts=None, bounds=settings.bounds, cursor_key=settings.cursor_key
    )
    facts, _ = service._facts(
        {
            "folder_id": "actv0000",
            "a_key_nobody_declared": "s3cr3t-value",
            "another_new_one": {"nested": "also secret"},
        }
    )
    by_key = {fact.key: fact for fact in facts}
    assert by_key["folder_id"].after.value == "actv0000"
    for name in ("a_key_nobody_declared", "another_new_one"):
        assert by_key[name].redacted is True
        assert by_key[name].before is None
        assert by_key[name].after is None
    rendered = " ".join(
        part.value
        for fact in facts
        for part in (fact.before, fact.after)
        if part is not None
    )
    assert "s3cr3t-value" not in rendered
    assert "also secret" not in rendered


def test_a_before_after_pair_folds_into_one_fact(settings):
    """`folder_id_before` and `folder_id_after` are one row, not two.

    A reader comparing an operational change should not have to pair them up by
    eye, and the suffix convention is the platform's own — R-41 writes exactly
    that pair.
    """
    service = AuditSearchService(
        audit=None, accounts=None, bounds=settings.bounds, cursor_key=settings.cursor_key
    )
    facts, _ = service._facts(
        {"folder_id_before": "actv0000", "folder_id_after": "arch0000"}
    )
    assert len(facts) == 1
    assert facts[0].key == "folder_id"
    assert facts[0].before.value == "actv0000"
    assert facts[0].after.value == "arch0000"


def test_every_rendered_key_is_a_count_code_or_identifier():
    """The allowlist, checked for what it is rather than for what it says.

    Every entry must be a key one of this repository's own services writes, and
    the guard against the list growing carelessly is that a reviewer can see the
    whole of it. Asserted as a bound rather than an enumeration: a list that grew
    past this would be a list nobody is reading.
    """
    assert len(RENDERED_PAYLOAD_KEYS) <= 80
    assert all(key.islower() and " " not in key for key in RENDERED_PAYLOAD_KEYS)
    # None of the words a secret, a path, an exception or artifact content would
    # arrive under.
    for forbidden in ("token", "secret", "password", "path", "traceback", "sql",
                      "exception", "bytes", "artifact", "raw"):
        assert not any(forbidden in key for key in RENDERED_PAYLOAD_KEYS), forbidden


async def test_a_rendered_audit_row_retains_the_facts_it_must_and_no_others(
    client, settings, migrated_database, callers
):
    """TC-AUD-06, on a real response.

    Retained: actor, action, source, time, correlation id and before/after facts.
    Excluded: raw snapshot bytes, secrets and exception detail. The payload here
    carries all three of the excluded kinds under undeclared keys, which is
    exactly how they would arrive if a future writer were careless.
    """
    with migrated_database.begin() as connection:
        connection.execute(
            insert(audit_events).values(
                id=uuid4(),
                occurred_at=utcnow(),
                actor_platform_account_id=callers["C"].account_id,
                actor_capability="guild_council",
                action="snapshot.folder_selected",
                entity_type="foundry_snapshot",
                entity_id=str(uuid4()),
                source="web",
                correlation_id=uuid4(),
                payload={
                    "folder_id_before": "actv0000",
                    "folder_id_after": "arch0000",
                    "checksum": "b" * 64,
                    "raw_artifact": '{"actors":[{"name":"Real Person"}]}',
                    "oauth_token": "Bearer sup3r-s3cret",
                    "stack_trace": 'File "/opt/discord-bots/x.py", line 1',
                },
            )
        )
    response = await client.get(
        "/v1/audit/results", cookies=callers["C"].cookies(settings)
    )
    assert response.status_code == 200
    # Retained.
    assert "snapshot.folder_selected" in response.text
    assert "actv0000" in response.text and "arch0000" in response.text
    assert "b" * 64 in response.text
    assert "guild_council" in response.text
    # Excluded — every one of them, and their giveaway substrings.
    for leaked in (
        "Real Person",
        "sup3r-s3cret",
        "/opt/discord-bots",
        "Bearer",
        '{"actors"',
    ):
        assert leaked not in response.text, leaked


async def test_a_system_action_renders_without_an_actor_rather_than_with_a_blank_one(
    client, settings, migrated_database, callers
):
    """`AuditRow.actor` is `None` for system and service-principal actions.

    A row that named nobody by rendering an empty label would read as a defect. A
    row that says there was no person is a fact — the reaper's terminal event is
    exactly that, and it is the one event in this package no human causes.
    """
    with migrated_database.begin() as connection:
        connection.execute(
            insert(audit_events).values(
                id=uuid4(),
                occurred_at=utcnow(),
                actor_capability="system",
                action="reconciliation.job_failed",
                entity_type="reconciliation_job",
                entity_id=str(uuid4()),
                source="system",
                correlation_id=uuid4(),
                payload={"failure_code": "attempts_exhausted", "attempts": 3},
            )
        )
    response = await client.get(
        "/v1/audit/results", cookies=callers["C"].cookies(settings)
    )
    assert response.status_code == 200
    assert "attempts_exhausted" in response.text
    assert 'data-has-actor="false"' in response.text


async def test_a_historical_row_resolves_its_actor_through_a_retired_identity(
    client, settings, migrated_database, callers
):
    """TC-AUD-05. Rows written before migration 0006 keep only a Discord column
    and are never rewritten (ADR 0010 D5).

    The resolution goes through `external_identities` — **including after that
    identity is retired**, which is the reason an identity is retired rather than
    deleted.
    """
    from tests.web.portal_fixtures import COUNCIL_SUBJECT

    with migrated_database.begin() as connection:
        connection.execute(
            insert(audit_events).values(
                id=uuid4(),
                occurred_at=utcnow(),
                actor_discord_user_id=COUNCIL_SUBJECT,
                actor_capability="guild_council",
                action="legacy.action",
                entity_type="character",
                entity_id=str(uuid4()),
                source="discord",
                correlation_id=uuid4(),
                payload={},
            )
        )
        # `ck_external_identities_retirement_is_dated`: a retired identity says
        # **when**. The constraint is the reason a retirement cannot be a state
        # flag somebody set and forgot, and it applies to a test's arrangement
        # exactly as it applies to the service's.
        connection.execute(
            text(
                "UPDATE external_identities SET state = 'retired', "
                "retired_at = now() WHERE subject = :subject"
            ),
            {"subject": str(COUNCIL_SUBJECT)},
        )
    response = await client.get(
        "/v1/audit/results?action=legacy.", cookies=callers["A"].cookies(settings)
    )
    assert response.status_code == 200
    assert "legacy.action" in response.text
    # The actor cell is not the em-dash placeholder: the row resolved a person.
    assert "caller-C" in response.text


def test_every_payload_key_this_repository_writes_is_classified():
    """The allowlist is complete against the code, not against a memory.

    Parsed out of the source: every `payload={...}` literal handed to an
    `AuditEvent` is collected, and each key must be **either** in
    `RENDERED_PAYLOAD_KEYS` or in the deliberate exclusion set below.

    The direction matters. Rendering already fails closed — an unrecognized key
    shows as redacted — so a missing entry is not a disclosure. It is a *silent
    loss*: a Council member reading the audit view would see `(not rendered)`
    where the platform meant to show them a count, and nobody would find out
    until somebody needed that number during an incident. This is what catches
    it at the point the payload is written.
    """
    written: dict[str, str] = {}
    for directory in ("application", "adapters"):
        for path in sorted((ROOT / directory).glob("**/*.py")):
            if "__pycache__" in path.parts:
                continue
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
                if name != "AuditEvent":
                    continue
                for keyword in node.keywords:
                    if keyword.arg != "payload" or not isinstance(
                        keyword.value, ast.Dict
                    ):
                        continue
                    for key in keyword.value.keys:
                        if isinstance(key, ast.Constant) and isinstance(key.value, str):
                            written.setdefault(key.value, f"{path.name}:{key.lineno}")

    #: Keys the projection deliberately does **not** render, each for a stated
    #: reason rather than because nobody got to them.
    excluded = {
        # A `_before`/`_after` pair folds to its stem, which is on the list.
        "folder_id_before",
        "folder_id_after",
    }
    assert written, "the AST scan found no audit payloads, so it proves nothing"
    unclassified = {
        key: where
        for key, where in written.items()
        if key not in RENDERED_PAYLOAD_KEYS and key not in excluded
    }
    assert unclassified == {}, unclassified
