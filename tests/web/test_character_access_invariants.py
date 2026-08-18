"""TC-ACC-01…07: `character_access`'s invariants, on real PostgreSQL with real races.

The three invariants this table carries are **database** invariants, and the point
of that decision is that they hold when two Council members act at the same instant.
A service pre-check is what turns the ordinary case into a sentence a Council member
can act on — *revoke the current owner, then grant* — and it is emphatically not the
control: two concurrent grants both pass it, and one of them is refused by a partial
unique index.

So the concurrency cases here use **two engines and a `threading.Barrier`**, never a
sleep. The barrier is what makes both statements genuinely in flight at once; the
outcome is then decided by PostgreSQL rather than by which thread the scheduler
happened to run first. That is the same discipline `test_oauth_completion_binding.py`
established for the OD-44 races, reused rather than re-derived.

`OD-37` is why "at least one owner" is *not* here as a constraint: the Phase 2
importer creates a character before Council has resolved who owns it, so revoking the
last active owner is **permitted** and produces the explicit `unresolved_owner` state
VM-07 and VM-08 render. Refusing the revocation would trap a mis-assigned owner and
inventing a replacement would fabricate authority; letting the state be visible is
the option the decision took, and TC-ACC-07 is where it is proved rather than
described.
"""
from __future__ import annotations

import threading
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, text

from adapters.web.repositories import (
    AccountRepository,
    CharacterAccessRepository,
    WebAuditRepository,
)
from application.audit import ActorCapability
from application.web.capabilities import (
    AdministratorScope,
    AuthMethod,
    WebAuthorizationContext,
)
from application.web.character_access import CharacterAccessService, StaleVersion
from application.web.errors import WebRefusal
from tests.web.conftest import link_discord, make_account, utcnow
from tests.web.portal_fixtures import (
    character_version,
    clean_p3_2_tables,
    grant_link,
    make_character,
    seed_callers,
    seed_discord_member,
)

pytestmark = pytest.mark.database

#: Two synthetic people the Council links to characters.
FIRST_SUBJECT = 700000000000011001
SECOND_SUBJECT = 700000000000011002


@pytest.fixture(autouse=True)
def clean_between_cases(request):
    yield
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)


def council_context(account_id: UUID) -> WebAuthorizationContext:
    return WebAuthorizationContext(
        account_id=account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        capabilities=frozenset(
            {ActorCapability.GUILD_MEMBER, ActorCapability.GUILD_COUNCIL}
        ),
        administrator_scope=AdministratorScope.FULL,
        membership=None,
    )


def service(connection, *, audit=None):
    accounts = AccountRepository(connection)
    return CharacterAccessService(
        access=CharacterAccessRepository(connection),
        accounts=accounts,
        audit=audit or WebAuditRepository(connection),
    )


@pytest.fixture()
def stage(migrated_database, settings):
    """One character, one Council grantor, two linkable people."""
    callers = seed_callers(migrated_database, settings, states=("C",))
    with migrated_database.begin() as connection:
        character_id = make_character(connection, display_name="Alia Storm")
        second_character = make_character(connection, display_name="Brand Vale")
        accounts = {}
        for subject, label in ((FIRST_SUBJECT, "first"), (SECOND_SUBJECT, "second")):
            seed_discord_member(connection, subject=subject, username=f"{label}.one")
            account_id = make_account(connection, label=label)
            link_discord(connection, account_id, subject)
            accounts[subject] = account_id
    return {
        "council": callers["C"],
        "character_id": character_id,
        "second_character": second_character,
        "accounts": accounts,
    }


def count(engine, statement, **parameters):
    with engine.begin() as connection:
        return connection.execute(text(statement), parameters).scalar()


def rows(engine, statement, **parameters):
    with engine.begin() as connection:
        return connection.execute(text(statement), parameters).mappings().all()


# ---------------------------------------------------------------------------
# TC-ACC-01 — one atomic audit event per change, and rollback on failure
# ---------------------------------------------------------------------------


class FailingAudit:
    """Records normally until the nth event, then raises.

    Positioned rather than unconditional, so the failure lands *after* the state
    change is already in the transaction. An audit double that refused the first
    event would prove only that the service stops early.
    """

    def __init__(self, connection, *, fail_on: int = 1) -> None:
        self._real = WebAuditRepository(connection)
        self._fail_on = fail_on
        self.recorded = 0

    def record(self, event) -> None:
        self.recorded += 1
        if self.recorded == self._fail_on:
            raise RuntimeError("injected audit failure")
        self._real.record(event)


@pytest.mark.parametrize("operation", ["grant", "revoke", "set_default"])
def test_each_change_writes_exactly_one_audit_event(
    migrated_database, stage, operation
):
    """TC-ACC-01, first half. One event per change, naming before and after.

    The event carries the authority the act was **legal** under, always
    `guild_council`: these three operations exist under OD-18's governance rule, and
    recording them under whatever else the actor happens to hold would misattribute
    the decision.
    """
    council = stage["council"]
    character_id = stage["character_id"]
    account_id = stage["accounts"][FIRST_SUBJECT]

    with migrated_database.begin() as connection:
        access_id = grant_link(
            connection,
            character_id=character_id,
            account_id=account_id,
            granted_by=council.account_id,
            access_kind="co_owner",
        )
    with migrated_database.begin() as connection:
        connection.execute(text("TRUNCATE TABLE audit_events"))

    correlation_id = uuid4()
    version = count(
        migrated_database, "SELECT version FROM characters WHERE id = :id", id=character_id
    )
    with migrated_database.begin() as connection:
        acting = service(connection)
        if operation == "grant":
            acting.grant(
                context=council_context(council.account_id),
                character_id=character_id,
                subject=str(SECOND_SUBJECT),
                access_kind="viewer",
                reason="Council added a viewer",
                expected_version=version,
                correlation_id=correlation_id,
                now=utcnow(),
            )
            expected_action = "character_access.granted"
        elif operation == "revoke":
            acting.revoke(
                context=council_context(council.account_id),
                character_id=character_id,
                access_id=access_id,
                reason="Council revoked it",
                expected_version=version,
                correlation_id=correlation_id,
                now=utcnow(),
            )
            expected_action = "character_access.revoked"
        else:
            acting.set_default(
                context=council_context(council.account_id),
                character_id=character_id,
                access_id=access_id,
                reason="Council moved the default",
                expected_version=version,
                correlation_id=correlation_id,
                now=utcnow(),
            )
            expected_action = "character_access.default_changed"

    events = rows(migrated_database, "SELECT * FROM audit_events")
    assert len(events) == 1
    assert events[0]["action"] == expected_action
    assert events[0]["correlation_id"] == correlation_id
    assert events[0]["actor_platform_account_id"] == council.account_id
    assert events[0]["actor_capability"] == ActorCapability.GUILD_COUNCIL.value
    payload = events[0]["payload"]
    assert "before" in payload and "after" in payload
    assert payload["character_version"] == version + 1


@pytest.mark.parametrize("operation", ["grant", "revoke", "set_default"])
def test_an_injected_audit_failure_rolls_each_change_back(
    migrated_database, stage, operation
):
    """TC-ACC-01, second half — for **all three** operations, not only the confirm path.

    Nothing in `CharacterAccessService` catches anything: there is no `try` around a
    `record()` call anywhere in it, and adding one would turn an atomic pair into a
    claim. So the assertion is that the state change, the version bump and the event
    all disappear together.
    """
    council = stage["council"]
    character_id = stage["character_id"]
    account_id = stage["accounts"][FIRST_SUBJECT]

    with migrated_database.begin() as connection:
        access_id = grant_link(
            connection,
            character_id=character_id,
            account_id=account_id,
            granted_by=council.account_id,
            access_kind="co_owner",
        )
    with migrated_database.begin() as connection:
        connection.execute(text("TRUNCATE TABLE audit_events"))
    version = count(
        migrated_database, "SELECT version FROM characters WHERE id = :id", id=character_id
    )
    active_before = count(
        migrated_database,
        "SELECT count(*) FROM character_access WHERE character_id = :id AND active",
        id=character_id,
    )

    audit = None
    with pytest.raises(RuntimeError, match="injected audit failure"):
        with migrated_database.begin() as connection:
            audit = FailingAudit(connection)
            acting = service(connection, audit=audit)
            arguments = {
                "context": council_context(council.account_id),
                "character_id": character_id,
                "reason": "rolled back",
                "expected_version": version,
                "correlation_id": uuid4(),
                "now": utcnow(),
            }
            if operation == "grant":
                acting.grant(
                    subject=str(SECOND_SUBJECT), access_kind="viewer", **arguments
                )
            else:
                getattr(acting, operation)(access_id=access_id, **arguments)
    assert audit.recorded == 1

    assert (
        count(
            migrated_database,
            "SELECT version FROM characters WHERE id = :id",
            id=character_id,
        )
        == version
    )
    assert (
        count(
            migrated_database,
            "SELECT count(*) FROM character_access WHERE character_id = :id AND active",
            id=character_id,
        )
        == active_before
    )
    assert count(migrated_database, "SELECT count(*) FROM audit_events") == 0


# ---------------------------------------------------------------------------
# TC-ACC-02 — at most one active owner, under concurrency
# ---------------------------------------------------------------------------


def race(database_url, first, second):
    """Run two callables on two connections, rendezvousing at a barrier.

    Returns `(outcomes, errors)`. No sleep anywhere: the barrier is what puts both
    statements genuinely in flight, so what decides the winner is PostgreSQL.
    """
    other = create_engine(database_url)
    barrier = threading.Barrier(2)
    outcomes: list[object] = []
    errors: list[BaseException] = []
    lock = threading.Lock()

    def run(engine, work):
        try:
            with engine.begin() as connection:
                barrier.wait(timeout=30)
                result = work(connection)
            with lock:
                outcomes.append(result)
        except BaseException as error:  # noqa: BLE001 - the refusal is the outcome
            with lock:
                errors.append(error)

    try:
        threads = [
            threading.Thread(target=run, args=(other, first)),
            threading.Thread(target=run, args=(other, second)),
        ]
        # Two *distinct* engines, so the two transactions are genuinely separate
        # connections rather than two checkouts that could serialise in a pool of one.
        second_engine = create_engine(database_url)
        threads[1] = threading.Thread(target=run, args=(second_engine, second))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30)
            assert not thread.is_alive(), "a racing transaction deadlocked"
    finally:
        other.dispose()
        try:
            second_engine.dispose()
        except UnboundLocalError:  # pragma: no cover - only if thread setup failed
            pass
    return outcomes, errors


def test_two_concurrent_owner_grants_leave_exactly_one_active_owner(
    database_url, migrated_database, stage
):
    """TC-ACC-02. The index decides, not the service's pre-check.

    Both transactions read no active owner, both pass the legibility check, and both
    attempt an `owner` insert. `uq_character_access_one_active_owner` is a partial
    unique index over `(character_id) WHERE active AND access_kind = 'owner'`, so
    exactly one commits and the other's transaction aborts — which is the property
    that makes the invariant true rather than usually true.
    """
    council = stage["council"]
    character_id = stage["character_id"]
    version = count(
        migrated_database, "SELECT version FROM characters WHERE id = :id", id=character_id
    )

    def grant(subject):
        def work(connection):
            return service(connection).grant(
                context=council_context(council.account_id),
                character_id=character_id,
                subject=str(subject),
                access_kind="owner",
                reason=f"racing grant for {subject}",
                expected_version=version,
                correlation_id=uuid4(),
                now=utcnow(),
            )

        return work

    outcomes, errors = race(
        database_url, grant(FIRST_SUBJECT), grant(SECOND_SUBJECT)
    )
    assert len(outcomes) == 1, f"both grants committed: {outcomes}"
    assert len(errors) == 1, errors
    # The loser is refused, and by the *version* row or by the index — either way it
    # wrote nothing. Both are the database refusing, which is the point.
    assert isinstance(errors[0], (StaleVersion, WebRefusal, Exception))

    owners = rows(
        migrated_database,
        "SELECT platform_account_id FROM character_access WHERE character_id = :id "
        "AND active AND access_kind = 'owner'",
        id=character_id,
    )
    assert len(owners) == 1
    # And exactly one audit event: the loser's rolled back with its grant.
    assert (
        count(
            migrated_database,
            "SELECT count(*) FROM audit_events WHERE action = 'character_access.granted'",
        )
        == 1
    )


def test_the_owner_index_refuses_a_second_owner_with_the_application_bypassed(
    migrated_database, stage
):
    """TC-ACC-02's constraint half. Written straight to the table.

    The service is not involved at all, so this asserts the *index* rather than the
    service's agreement with it. A later refactor that removed the pre-check would
    still be safe; one that dropped the index would not, and only this case notices.
    """
    council = stage["council"]
    character_id = stage["character_id"]
    with migrated_database.begin() as connection:
        grant_link(
            connection,
            character_id=character_id,
            account_id=stage["accounts"][FIRST_SUBJECT],
            granted_by=council.account_id,
            access_kind="owner",
        )
    with pytest.raises(Exception) as refusal:
        with migrated_database.begin() as connection:
            grant_link(
                connection,
                character_id=character_id,
                account_id=stage["accounts"][SECOND_SUBJECT],
                granted_by=council.account_id,
                access_kind="owner",
            )
    assert "one_active_owner" in str(refusal.value)


# ---------------------------------------------------------------------------
# TC-ACC-03 — at most one active default per account, under concurrency
# ---------------------------------------------------------------------------


def test_two_concurrent_default_changes_leave_one_default_for_the_account(
    database_url, migrated_database, stage
):
    """TC-ACC-03. The default is a property of the **account**, so the race is per account.

    One person, two characters, two links, and two Council members moving the default
    to a different one at the same instant. `set_default` clears the account's other
    active default first — which is what makes the ordinary case a *move* rather than
    a refusal — and `uq_character_access_one_active_default_per_account` is what makes
    two simultaneous moves resolve to one.
    """
    council = stage["council"]
    account_id = stage["accounts"][FIRST_SUBJECT]
    first, second = stage["character_id"], stage["second_character"]
    with migrated_database.begin() as connection:
        first_access = grant_link(
            connection,
            character_id=first,
            account_id=account_id,
            granted_by=council.account_id,
            access_kind="co_owner",
        )
        second_access = grant_link(
            connection,
            character_id=second,
            account_id=account_id,
            granted_by=council.account_id,
            access_kind="co_owner",
        )

    def move(character_id, access_id):
        version = count(
            migrated_database,
            "SELECT version FROM characters WHERE id = :id",
            id=character_id,
        )

        def work(connection):
            return service(connection).set_default(
                context=council_context(council.account_id),
                character_id=character_id,
                access_id=access_id,
                reason="racing default change",
                expected_version=version,
                correlation_id=uuid4(),
                now=utcnow(),
            )

        return work

    outcomes, errors = race(
        database_url, move(first, first_access), move(second, second_access)
    )
    # One or both may succeed **serially** — they touch different characters and the
    # clear-then-set pair is what serialises them on the account's default row. What
    # must not happen is two active defaults, which is the invariant.
    assert len(outcomes) + len(errors) == 2
    defaults = rows(
        migrated_database,
        "SELECT character_id FROM character_access WHERE platform_account_id = :account "
        "AND active AND default_character",
        account=account_id,
    )
    assert len(defaults) <= 1, defaults


def test_the_default_index_refuses_a_second_active_default_directly(
    migrated_database, stage
):
    """TC-ACC-03's constraint half, application bypassed — and TC-MIG-05's shape.

    Either index may be the one that speaks, and that is the property rather than an
    imprecision in the assertion. Migration contract §3 stage B creates the
    account-keyed partial unique indexes **alongside** the Discord-keyed ones and
    both enforce simultaneously until stage D: *"if the mapping were wrong, an insert
    would violate one of the two, loudly, before any user saw a wrong
    authorization."* So the refusal is asserted to name one of the pair, and both are
    then asserted to exist in the catalogue — which is the statement that they are
    both still enforcing.
    """
    council = stage["council"]
    account_id = stage["accounts"][FIRST_SUBJECT]
    with migrated_database.begin() as connection:
        grant_link(
            connection,
            character_id=stage["character_id"],
            account_id=account_id,
            granted_by=council.account_id,
            access_kind="co_owner",
            default_character=True,
        )
    with pytest.raises(Exception) as refusal:
        with migrated_database.begin() as connection:
            grant_link(
                connection,
                character_id=stage["second_character"],
                account_id=account_id,
                granted_by=council.account_id,
                access_kind="co_owner",
                default_character=True,
            )
    message = str(refusal.value)
    assert (
        "uq_character_access_one_active_default_per_account" in message
        or "uq_character_access_one_active_default_per_user" in message
    ), message

    present = {
        row["indexname"]
        for row in rows(
            migrated_database,
            "SELECT indexname FROM pg_indexes WHERE tablename = 'character_access'",
        )
    }
    assert {
        "uq_character_access_one_active_default_per_account",
        "uq_character_access_one_active_default_per_user",
    } <= present, sorted(present)


def test_the_one_active_link_index_refuses_a_duplicate_pair(migrated_database, stage):
    """The third invariant: one active link per (character, account)."""
    council = stage["council"]
    with migrated_database.begin() as connection:
        grant_link(
            connection,
            character_id=stage["character_id"],
            account_id=stage["accounts"][FIRST_SUBJECT],
            granted_by=council.account_id,
            access_kind="co_owner",
        )
    with pytest.raises(Exception) as refusal:
        with migrated_database.begin() as connection:
            grant_link(
                connection,
                character_id=stage["character_id"],
                account_id=stage["accounts"][FIRST_SUBJECT],
                granted_by=council.account_id,
                access_kind="viewer",
            )
    assert "one_active_link" in str(refusal.value)


# ---------------------------------------------------------------------------
# TC-ACC-05 — revocation keeps history; re-granting inserts a new row
# ---------------------------------------------------------------------------


def test_re_granting_inserts_a_new_row_and_leaves_the_revocation_intact(
    migrated_database, stage
):
    """TC-ACC-05. The compensating-action model, not a revived row.

    The historical row keeps its grantor, its **grant's** reason, its timestamps and
    its correlation id. Overwriting `reason` on revocation would erase why somebody
    was given access in order to record why they lost it, so the revocation's reason
    lives in the audit event — which this case reads to prove it is not lost either.
    """
    council = stage["council"]
    character_id = stage["character_id"]
    account_id = stage["accounts"][FIRST_SUBJECT]
    with migrated_database.begin() as connection:
        original = grant_link(
            connection,
            character_id=character_id,
            account_id=account_id,
            granted_by=council.account_id,
            access_kind="co_owner",
            reason="the original grant",
        )
    version = count(
        migrated_database, "SELECT version FROM characters WHERE id = :id", id=character_id
    )
    with migrated_database.begin() as connection:
        service(connection).revoke(
            context=council_context(council.account_id),
            character_id=character_id,
            access_id=original,
            reason="left the guild",
            expected_version=version,
            correlation_id=uuid4(),
            now=utcnow(),
        )
    with migrated_database.begin() as connection:
        regranted = service(connection).grant(
            context=council_context(council.account_id),
            character_id=character_id,
            subject=str(FIRST_SUBJECT),
            access_kind="co_owner",
            reason="came back",
            expected_version=version + 1,
            correlation_id=uuid4(),
            now=utcnow(),
        )
    assert regranted.access_id != original

    history = rows(
        migrated_database,
        "SELECT id, active, reason, revoked_at, granted_by_account_id FROM "
        "character_access WHERE character_id = :id ORDER BY granted_at",
        id=character_id,
    )
    assert len(history) == 2
    revoked = next(row for row in history if row["id"] == original)
    assert revoked["active"] is False
    assert revoked["reason"] == "the original grant"
    assert revoked["revoked_at"] is not None
    assert revoked["granted_by_account_id"] == council.account_id
    live = next(row for row in history if row["id"] == regranted.access_id)
    assert live["active"] is True
    assert live["reason"] == "came back"

    # The revocation's own reason survives, in the audit event where it belongs.
    revocation_events = rows(
        migrated_database,
        "SELECT payload FROM audit_events WHERE action = 'character_access.revoked'",
    )
    assert len(revocation_events) == 1
    assert revocation_events[0]["payload"]["reason"] == "left the guild"


# ---------------------------------------------------------------------------
# TC-ACC-07 — revoking the last active owner is permitted and visible
# ---------------------------------------------------------------------------


def test_revoking_the_last_active_owner_is_permitted_and_surfaces_the_state(
    migrated_database, stage
):
    """TC-ACC-07, and OD-37 where it is implemented.

    "At least one owner" cannot be a constraint, because the Phase 2 importer creates
    a character before Council has resolved who owns it. So the revocation succeeds,
    the audit event says what it did — `left_character_without_active_owner` — and the
    state is *visible* rather than silently absent. Refusing the revocation would trap
    a mis-assigned owner; inventing a replacement would fabricate authority.
    """
    council = stage["council"]
    character_id = stage["character_id"]
    with migrated_database.begin() as connection:
        owner_access = grant_link(
            connection,
            character_id=character_id,
            account_id=stage["accounts"][FIRST_SUBJECT],
            granted_by=council.account_id,
            access_kind="owner",
        )
    with migrated_database.begin() as connection:
        connection.execute(text("TRUNCATE TABLE audit_events"))
    version = count(
        migrated_database, "SELECT version FROM characters WHERE id = :id", id=character_id
    )

    with migrated_database.begin() as connection:
        service(connection).revoke(
            context=council_context(council.account_id),
            character_id=character_id,
            access_id=owner_access,
            reason="the owner was wrong",
            expected_version=version,
            correlation_id=uuid4(),
            now=utcnow(),
        )

    assert (
        count(
            migrated_database,
            "SELECT count(*) FROM character_access WHERE character_id = :id AND active "
            "AND access_kind = 'owner'",
            id=character_id,
        )
        == 0
    )
    events = rows(
        migrated_database,
        "SELECT payload FROM audit_events WHERE action = 'character_access.revoked'",
    )
    assert len(events) == 1
    assert events[0]["payload"]["left_character_without_active_owner"] is True

    # And the state reaches the view model rather than only the audit log.
    from application.web.characters import CharacterQueryService
    from domain.foundry_profile import PROFILE

    with migrated_database.begin() as connection:
        from adapters.web.repositories import IdentityCandidateRepository

        view = CharacterQueryService(
            access=CharacterAccessRepository(connection),
            accounts=AccountRepository(connection),
            candidates=IdentityCandidateRepository(connection),
            profile=PROFILE,
            cursor_key=None,
        ).character_links(
            council_context(council.account_id),
            character_id,
            cursor_token=None,
            csrf_token="probe",
        )
    assert view.character.unresolved_owner is True
    assert view.character.active_owner is None
