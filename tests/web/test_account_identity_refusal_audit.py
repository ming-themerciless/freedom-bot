"""R-37: the last-identity refusal is **durable**, and nothing else about it moves.

The gap this file closes: `AccountIdentityService.unlink()` recorded
`identity.link_refused` and then raised, and R-37 ran that work inside one
`engine.begin()`. The raise rolled the transaction back — correctly for the
identity, which must not be retired, and catastrophically for the audit, which
went with it. The route answered `409`, the identity stayed active, and the
record of somebody trying to remove their own way back in did not exist. Every
assertion the suite made about that path was true of the broken behaviour,
because none of them read `audit_events` after the transaction closed.

So the cases below are split by the thing they can actually prove:

* the **durability** cases go through the adapter's `run_identity_unlink`
  against the real engine and then open a *separate* connection to read
  `audit_events`. Reading inside the transaction that wrote it would have passed
  before the fix too.
* the **non-fabrication** cases assert an absence — that a `404`, a stale-state
  refusal, a CSRF rejection or an emergency-session denial writes no
  account-identity event at all. An absence needs a test that fails when the
  absence stops holding, which is why they are here rather than being read off
  the service's control flow.
* the **failure-injection** cases are the two that separate "recorded" from
  "claimed": a mutation that dies must not leave a refusal record, and an audit
  that dies must not leave a `409`.

Everything is synthetic and lives in disposable PostgreSQL. `pytestmark` makes
that a hard requirement rather than a silent skip into a green run.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, BrokenBarrierError
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy import text

from adapters.web.repositories import (
    AccountRepository,
    WebAuditRepository,
    WebAuthnRepository,
)
from adapters.web.portal_routes import run_identity_unlink
from application.audit import ActorCapability
from application.web.account_identities import (
    AccountIdentityService,
    UnlinkRefused,
    UnlinkRefusedPendingAudit,
)
from application.web.capabilities import (
    AdministratorScope,
    AuthMethod,
    WebAuthorizationContext,
)
from application.web.errors import ObjectNotReachable
from tests.web.conftest import link_discord, make_account, utcnow
from tests.web.portal_fixtures import (
    csrf_token_for,
    seed_callers,
    seed_discord_member,
)
from tests.web_fixtures import PUBLIC_ORIGIN

pytestmark = pytest.mark.database

FORM = "application/x-www-form-urlencoded"

#: Synthetic Discord snowflakes. High enough not to collide with the shared
#: caller fixtures, which seed from their own base.
BASE = 700000000000044000


def member_context(account_id: UUID) -> WebAuthorizationContext:
    return WebAuthorizationContext(
        account_id=account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        capabilities=frozenset({ActorCapability.GUILD_MEMBER}),
        administrator_scope=AdministratorScope.FULL,
        membership=None,
    )


def service_for(connection) -> AccountIdentityService:
    """The real service over real repositories. A fake audit proves nothing here."""
    return AccountIdentityService(
        accounts=AccountRepository(connection),
        credentials=WebAuthnRepository(connection),
        audit=WebAuditRepository(connection),
    )


def unlink_change(account_id: UUID, identity_id: UUID, correlation_id: UUID):
    """The unit of work R-37 hands to the adapter's `run_identity_unlink`."""

    def change(connection):
        return service_for(connection).unlink(
            context=member_context(account_id),
            identity_id=identity_id,
            correlation_id=correlation_id,
            now=utcnow(),
        )

    return change


def audit_rows(engine, *, entity_id: UUID | None = None, action: str | None = None):
    """Read `audit_events` on a **fresh** connection, after the work committed.

    The separate connection is the point. The defect wrote the refusal inside the
    transaction that rolled back, so any assertion made through that same
    connection would have observed a row that never survived.
    """
    clauses = ["entity_type = 'external_identity'"]
    parameters: dict[str, object] = {}
    if entity_id is not None:
        clauses.append("entity_id = :entity_id")
        parameters["entity_id"] = str(entity_id)
    if action is not None:
        clauses.append("action = :action")
        parameters["action"] = action
    statement = (
        "SELECT action, entity_type, entity_id, source, actor_capability, "
        "actor_platform_account_id, correlation_id, payload "
        f"FROM audit_events WHERE {' AND '.join(clauses)} ORDER BY occurred_at"
    )
    with engine.begin() as connection:
        return connection.execute(text(statement), parameters).mappings().all()


def identity_state(engine, identity_id: UUID) -> str | None:
    with engine.begin() as connection:
        return connection.execute(
            text("SELECT state FROM external_identities WHERE id = :id"),
            {"id": identity_id},
        ).scalar()


def identity_exists(engine, identity_id: UUID) -> bool:
    with engine.begin() as connection:
        return connection.execute(
            text("SELECT count(*) FROM external_identities WHERE id = :id"),
            {"id": identity_id},
        ).scalar() == 1


def seed_member_with_identities(engine, count: int, *, label: str):
    """One ordinary account with `count` active identities. No recovery route."""
    with engine.begin() as connection:
        account_id = make_account(connection, label=label)
        identity_ids = []
        for offset in range(count):
            subject = BASE + abs(hash(label)) % 1000 * 10 + offset
            seed_discord_member(connection, subject=subject, username=f"{label}.{offset}")
            identity_ids.append(link_discord(connection, account_id, subject))
    return account_id, identity_ids


# ---------------------------------------------------------------------------
# 1 & 2 — the refusal is durable, and it says exactly what it said before
# ---------------------------------------------------------------------------


def test_the_last_identity_refusal_survives_the_rollback_that_causes_it(
    migrated_database,
):
    """The regression. Refused, unretired, and **recorded** — all three at once.

    Before the correction the first two held and the third did not, which is why
    this reads the table on a separate connection after `run_identity_unlink`
    returns rather than inside the work.
    """
    account_id, (identity_id,) = seed_member_with_identities(
        migrated_database, 1, label="last-identity"
    )
    correlation_id = uuid4()

    with pytest.raises(UnlinkRefused) as refused:
        run_identity_unlink(
            migrated_database,
            unlink_change(account_id, identity_id, correlation_id),
        )

    # The safe refusal R-37 renders as `409`, unchanged.
    assert refused.value.status == 409
    assert refused.value.correlation_id == correlation_id
    # …and it is the plain refusal, not the carrier: the runner consumed the
    # carrier and re-raised what the route was always given.
    assert type(refused.value) is UnlinkRefused

    # Nothing was retired.
    assert identity_state(migrated_database, identity_id) == "active"

    # Exactly one refusal event, and it committed.
    refusals = audit_rows(
        migrated_database, entity_id=identity_id, action="identity.link_refused"
    )
    assert len(refusals) == 1, "the refusal audit must outlive the rolled-back mutation"

    # And no applied event was fabricated for a mutation that did not happen.
    assert audit_rows(
        migrated_database, entity_id=identity_id, action="identity.unlinked"
    ) == []


def test_the_durable_refusal_carries_exactly_the_accepted_attribution(
    migrated_database,
):
    """Same facts the service always constructed, and no more than those.

    A durable record that lost its actor, its correlation id or its provider key
    would satisfy "a row exists" while answering none of the questions the row is
    kept for.
    """
    account_id, (identity_id,) = seed_member_with_identities(
        migrated_database, 1, label="attribution"
    )
    correlation_id = uuid4()

    with pytest.raises(UnlinkRefused):
        run_identity_unlink(
            migrated_database,
            unlink_change(account_id, identity_id, correlation_id),
        )

    (event,) = audit_rows(
        migrated_database, entity_id=identity_id, action="identity.link_refused"
    )
    assert event["action"] == "identity.link_refused"
    assert event["entity_type"] == "external_identity"
    assert event["entity_id"] == str(identity_id)
    assert event["source"] == "web"
    assert event["actor_capability"] == ActorCapability.GUILD_MEMBER.value
    assert event["actor_platform_account_id"] == account_id
    assert event["correlation_id"] == correlation_id

    # The payload is bounded: the provider key and the named refusal code, and
    # nothing that could carry a token, a cookie or an exception string.
    assert event["payload"] == {
        "provider_key": "discord",
        "refusal": "last_usable_identity",
    }


async def test_r37_answers_409_and_leaves_the_refusal_recorded(
    client, settings, migrated_database
):
    """The same property through the route, which is where the defect lived.

    The runner tests above prove the two-transaction rule; this proves R-37
    actually uses it. Composition, guards, `enter_mutation`, the service and the
    repositories are all the real ones — a mocked audit call cannot show that a
    row survived a rollback, because the rollback is the thing being tested.

    Caller `M` is seeded with exactly one active identity and is not the
    protected account, so it has no reviewed recovery route: its own identity is
    the last usable one.
    """
    member = seed_callers(migrated_database, settings, states=("M",))["M"]
    with migrated_database.begin() as connection:
        identity_id = connection.execute(
            text(
                "SELECT id FROM external_identities "
                "WHERE platform_account_id = :account AND state = 'active'"
            ),
            {"account": member.account_id},
        ).scalar()

    response = await client.post(
        f"/v1/account/identities/{identity_id}/unlink",
        cookies=member.cookies(settings),
        headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
        content=f"csrf_token={csrf_token_for(settings, member)}",
    )

    # The accepted safe refusal rendering, unchanged by the correction.
    assert response.status_code == 409
    assert 'data-conflict="stale_version"' in response.text

    assert identity_state(migrated_database, identity_id) == "active"

    (event,) = audit_rows(
        migrated_database, entity_id=identity_id, action="identity.link_refused"
    )
    assert event["actor_platform_account_id"] == member.account_id
    assert event["payload"] == {
        "provider_key": "discord",
        "refusal": "last_usable_identity",
    }
    assert audit_rows(
        migrated_database, entity_id=identity_id, action="identity.unlinked"
    ) == []


# ---------------------------------------------------------------------------
# 3 — success is still one atomic transaction
# ---------------------------------------------------------------------------


def test_a_successful_unlink_retires_and_records_in_one_transaction(
    migrated_database,
):
    """The second transaction is for refusals only; success never touches it."""
    account_id, (first_id, second_id) = seed_member_with_identities(
        migrated_database, 2, label="success"
    )
    correlation_id = uuid4()

    result = run_identity_unlink(
        migrated_database, unlink_change(account_id, first_id, correlation_id)
    )
    assert result == first_id

    # Retired, never deleted: historical attribution resolves through the row.
    assert identity_state(migrated_database, first_id) == "retired"
    assert identity_exists(migrated_database, first_id)
    assert identity_state(migrated_database, second_id) == "active"

    (event,) = audit_rows(
        migrated_database, entity_id=first_id, action="identity.unlinked"
    )
    assert event["correlation_id"] == correlation_id
    assert event["payload"]["before"] == {"state": "active"}
    assert event["payload"]["after"] == {"state": "retired"}

    # A success is not a refusal, and must not have produced one.
    assert audit_rows(
        migrated_database, entity_id=first_id, action="identity.link_refused"
    ) == []


# ---------------------------------------------------------------------------
# 4 & 5 — the refusals that are *not* the audited one
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case", ["absent", "other_account"])
def test_absent_and_other_account_identities_fabricate_no_audit(
    migrated_database, case
):
    """`404`, and a table that did not change. The non-enumeration rule is intact.

    Both cases refuse *before* the account lock, so neither is the last-identity
    fact — and writing one for them would tell an enumerating caller that the
    UUID they guessed is real.
    """
    account_id, (own_id,) = seed_member_with_identities(
        migrated_database, 1, label=f"caller-{case}"
    )
    if case == "absent":
        target = uuid4()
    else:
        _other_account, (target,) = seed_member_with_identities(
            migrated_database, 1, label="stranger"
        )

    with pytest.raises(ObjectNotReachable) as refused:
        run_identity_unlink(
            migrated_database, unlink_change(account_id, target, uuid4())
        )
    assert refused.value.status == 404

    assert audit_rows(migrated_database) == []
    assert identity_state(migrated_database, own_id) == "active"
    if case == "other_account":
        assert identity_state(migrated_database, target) == "active"


def test_an_already_retired_identity_is_a_stale_refusal_not_a_last_identity_one(
    migrated_database,
):
    """A stale-state refusal, and deliberately not the named audit fact.

    It raises the plain `UnlinkRefused`, so the runner's carrier branch does not
    fire and nothing is written. Turning every `UnlinkRefused` into
    `identity.link_refused` would record "they tried to remove their last way in"
    about a request that named a row already retired.
    """
    with migrated_database.begin() as connection:
        account_id = make_account(connection, label="already-retired")
        seed_discord_member(connection, subject=BASE + 501, username="retired.one")
        seed_discord_member(connection, subject=BASE + 502, username="retired.two")
        active_id = link_discord(connection, account_id, BASE + 501)
        retired_id = link_discord(
            connection, account_id, BASE + 502, state="retired"
        )

    with pytest.raises(UnlinkRefused) as refused:
        run_identity_unlink(
            migrated_database, unlink_change(account_id, retired_id, uuid4())
        )
    assert refused.value.status == 409
    assert type(refused.value) is UnlinkRefused

    assert audit_rows(migrated_database) == []
    assert identity_state(migrated_database, retired_id) == "retired"
    assert identity_state(migrated_database, active_id) == "active"


# ---------------------------------------------------------------------------
# 6 — refusals that never reach the service
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "case", ["no_csrf", "bad_csrf", "bad_origin", "emergency_session"]
)
async def test_guard_refusals_write_no_account_identity_audit(
    client, settings, migrated_database, case
):
    """CSRF, Origin and the emergency guard refuse *above* the mutation.

    They are not identity decisions and must not produce identity evidence. This
    goes through the route rather than the service because that is the only place
    the guards exist.
    """
    callers = seed_callers(migrated_database, settings, states=("M", "BG"))
    member = callers["M"]
    with migrated_database.begin() as connection:
        identity_id = connection.execute(
            text(
                "SELECT id FROM external_identities "
                "WHERE platform_account_id = :account AND state = 'active'"
            ),
            {"account": member.account_id},
        ).scalar()

    if case == "emergency_session":
        caller = callers["BG"]
        headers = {"content-type": FORM, "origin": PUBLIC_ORIGIN}
        body = f"csrf_token={csrf_token_for(settings, caller)}"
    else:
        caller = member
        origin = (
            "https://attacker.example" if case == "bad_origin" else PUBLIC_ORIGIN
        )
        headers = {"content-type": FORM, "origin": origin}
        body = {
            "no_csrf": "",
            "bad_csrf": "csrf_token=not-the-issued-token",
            "bad_origin": f"csrf_token={csrf_token_for(settings, member)}",
        }[case]

    response = await client.post(
        f"/v1/account/identities/{identity_id}/unlink",
        cookies=caller.cookies(settings),
        headers=headers,
        content=body,
    )

    assert response.status_code == 403
    assert identity_state(migrated_database, identity_id) == "active"
    assert audit_rows(migrated_database, entity_id=identity_id) == []


# ---------------------------------------------------------------------------
# 7 & 8 — the two failures that separate "recorded" from "claimed"
# ---------------------------------------------------------------------------


def test_a_failed_mutation_transaction_records_no_refusal_and_no_success(
    migrated_database, monkeypatch
):
    """The retirement dies mid-transaction. Nothing may be left behind at all."""
    account_id, (first_id, second_id) = seed_member_with_identities(
        migrated_database, 2, label="mutation-fails"
    )

    def exploding_retire(self, identity_id, *, reason, at):
        raise RuntimeError("injected storage failure")

    monkeypatch.setattr(AccountRepository, "retire_identity", exploding_retire)

    with pytest.raises(RuntimeError):
        run_identity_unlink(
            migrated_database, unlink_change(account_id, first_id, uuid4())
        )

    # Not a refusal, not a success, and not retired.
    assert identity_state(migrated_database, first_id) == "active"
    assert identity_state(migrated_database, second_id) == "active"
    assert audit_rows(migrated_database) == []


def test_a_failed_refusal_audit_transaction_never_answers_409(
    migrated_database, monkeypatch
):
    """The audit is the deliverable of this path, so its failure is a failure.

    Answering `409` here would say "your refusal was recorded" about a record
    that does not exist — the exact false success the correction is for. The
    error propagates instead, and the app's handler renders VM-20's correlation
    id and nothing else.
    """
    account_id, (identity_id,) = seed_member_with_identities(
        migrated_database, 1, label="audit-fails"
    )

    def exploding_record(self, event):
        raise RuntimeError("injected audit failure")

    monkeypatch.setattr(WebAuditRepository, "record", exploding_record)

    with pytest.raises(RuntimeError):
        run_identity_unlink(
            migrated_database, unlink_change(account_id, identity_id, uuid4())
        )

    monkeypatch.undo()

    # The identity is untouched, and no `409`-shaped refusal was claimed.
    assert identity_state(migrated_database, identity_id) == "active"
    assert audit_rows(migrated_database) == []


async def test_a_failed_refusal_audit_renders_a_safe_error_not_a_conflict(
    app, settings, migrated_database, monkeypatch
):
    """The same property at the route: `500` with a correlation id, never `409`.

    It builds its own client because `raise_app_exceptions=False` is needed to
    observe the response the application actually produced. Starlette's
    `ServerErrorMiddleware` sends the `500` and then re-raises so the server can
    log it, and the shared fixture's transport would surface that re-raise
    instead of the response — hiding the very thing under test.
    """
    callers = seed_callers(migrated_database, settings, states=("M",))
    member = callers["M"]
    with migrated_database.begin() as connection:
        identity_id = connection.execute(
            text(
                "SELECT id FROM external_identities "
                "WHERE platform_account_id = :account AND state = 'active'"
            ),
            {"account": member.account_id},
        ).scalar()

    real_record = WebAuditRepository.record

    def selective_record(self, event):
        if event.action == "identity.link_refused":
            raise RuntimeError("injected audit failure")
        return real_record(self, event)

    monkeypatch.setattr(WebAuditRepository, "record", selective_record)

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(
        transport=transport, base_url=PUBLIC_ORIGIN, follow_redirects=False
    ) as client:
        response = await client.post(
            f"/v1/account/identities/{identity_id}/unlink",
            cookies=member.cookies(settings),
            headers={"content-type": FORM, "origin": PUBLIC_ORIGIN},
            content=f"csrf_token={csrf_token_for(settings, member)}",
        )
    monkeypatch.undo()

    assert response.status_code == 500
    assert response.status_code != 409
    # N-25: no exception text, no SQL, no path.
    assert "injected audit failure" not in response.text
    assert "RuntimeError" not in response.text
    assert identity_state(migrated_database, identity_id) == "active"


# ---------------------------------------------------------------------------
# 9 — repeats are attempts, and each attempt is its own record
# ---------------------------------------------------------------------------


def test_each_refused_attempt_records_its_own_correlated_event(migrated_database):
    """The contract's unit is the *attempt*, so three attempts are three rows.

    R-37 carries no idempotency key — the route mints a fresh correlation id per
    request — so this asserts the boundary that actually exists rather than
    inventing a deduplication rule the contract does not state.
    """
    account_id, (identity_id,) = seed_member_with_identities(
        migrated_database, 1, label="repeated"
    )
    correlation_ids = [uuid4() for _ in range(3)]

    for correlation_id in correlation_ids:
        with pytest.raises(UnlinkRefused):
            run_identity_unlink(
                migrated_database,
                unlink_change(account_id, identity_id, correlation_id),
            )

    events = audit_rows(
        migrated_database, entity_id=identity_id, action="identity.link_refused"
    )
    assert len(events) == 3
    # Compared as a set: `occurred_at` defaults to `now()`, which is the
    # *transaction's* start time, so three fast attempts can tie and the order
    # is not the property under test — the one-record-per-attempt attribution is.
    assert {event["correlation_id"] for event in events} == set(correlation_ids)
    assert identity_state(migrated_database, identity_id) == "active"


# ---------------------------------------------------------------------------
# 10 — concurrency: the audit must describe what actually committed
# ---------------------------------------------------------------------------


def test_concurrent_unlinks_leave_one_identity_and_one_honest_audit_trail(
    migrated_database,
):
    """TC-ID-07 with the audit read afterwards, which is the part that was blind.

    Two requests aimed at an account's two different active identities. One
    retires, one is refused, the account keeps a way in — and the table must show
    exactly one applied event for the row that really moved and one refusal for
    the row that did not, with no applied event for a rolled-back retirement.
    """
    account_id, (first_id, second_id) = seed_member_with_identities(
        migrated_database, 2, label="concurrent"
    )
    rendezvous = Barrier(2)

    class CoordinatedAccounts(AccountRepository):
        def active_identity_count(self, candidate: UUID) -> int:
            count = super().active_identity_count(candidate)
            try:
                rendezvous.wait(timeout=0.5)
            except BrokenBarrierError:
                pass
            return count

    def attempt(identity_id: UUID):
        def change(connection):
            service = AccountIdentityService(
                accounts=CoordinatedAccounts(connection),
                credentials=WebAuthnRepository(connection),
                audit=WebAuditRepository(connection),
            )
            return service.unlink(
                context=member_context(account_id),
                identity_id=identity_id,
                correlation_id=uuid4(),
                now=utcnow(),
            )

        try:
            run_identity_unlink(migrated_database, change)
            return "unlinked"
        except UnlinkRefused:
            return "refused"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = sorted(executor.map(attempt, (first_id, second_id)))

    assert outcomes == ["refused", "unlinked"]

    with migrated_database.begin() as connection:
        active = connection.execute(
            text(
                "SELECT count(*) FROM external_identities "
                "WHERE platform_account_id = :account AND state = 'active'"
            ),
            {"account": account_id},
        ).scalar()
    assert active == 1

    applied = audit_rows(migrated_database, action="identity.unlinked")
    refusals = audit_rows(migrated_database, action="identity.link_refused")
    assert len(applied) == 1
    assert len(refusals) == 1

    # The applied event names the row that really retired, and the refusal names
    # the one still standing. A rolled-back retirement must not have been logged.
    assert identity_state(migrated_database, UUID(applied[0]["entity_id"])) == "retired"
    assert identity_state(migrated_database, UUID(refusals[0]["entity_id"])) == "active"


# ---------------------------------------------------------------------------
# The carrier itself, at the boundary the route depends on
# ---------------------------------------------------------------------------


def test_the_carrier_is_still_the_refusal_direct_callers_already_catch(
    migrated_database,
):
    """A service-level consumer that bypasses the runner still sees `UnlinkRefused`.

    The carrier subclasses the refusal deliberately, so introducing the two-phase
    runner did not impose a new exception contract on every existing caller. The
    runner is what makes the record durable; the exception type is what the route
    renders, and it did not change.
    """
    account_id, (identity_id,) = seed_member_with_identities(
        migrated_database, 1, label="carrier"
    )

    with pytest.raises(UnlinkRefused) as refused:
        with migrated_database.begin() as connection:
            service_for(connection).unlink(
                context=member_context(account_id),
                identity_id=identity_id,
                correlation_id=uuid4(),
                now=utcnow(),
            )

    assert isinstance(refused.value, UnlinkRefusedPendingAudit)
    assert refused.value.status == 409
    assert refused.value.event.action == "identity.link_refused"
    assert refused.value.refusal.correlation_id == refused.value.correlation_id
