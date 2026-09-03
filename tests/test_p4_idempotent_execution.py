"""Phase 4 WP-4 — durable idempotent command execution against real PostgreSQL.

A mock does not prove a constraint, a transaction boundary or a concurrent
outcome. Everything here runs against the disposable `freedom_test` database
over the Unix-domain socket, through `SqlAlchemyUnitOfWork` and the existing
`idempotency_keys` table under the Phase-4-owned scope `ledger.post_transaction`.

**What is durable here, exactly.** OD-48 rules that Phase 4 adds no ledger table
and no migration, so the composite unit of work commits the *receipt and the
audit row* to PostgreSQL and publishes the *posting* to the in-memory reference
book only if that commit succeeded. So the idempotency guarantees below — a
retry, a conflicting reuse, two concurrent callers — are proved against a real
unique index on `(scope, key)`, which is the thing WP-4 is about. The ledger's
own durability is owed by the package that gives it a table (5.0 or 5.2), and
nothing in this file claims otherwise.

No migration is added by this package: these tests write rows into an existing
table under a scope nothing else uses.
"""
from __future__ import annotations

import threading
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError, IntegrityError

from adapters.database.unit_of_work import SqlAlchemyUnitOfWork
from adapters.ledger.in_memory import (
    LedgerBook,
    LedgerUnitOfWork,
    unit_of_work_factory,
)
from application.audit import AuditSource
from application.authorization import AuthorizationContext
from application.commands import (
    CommandCaller,
    CommandEnvelope,
    ExpectedVersion,
)
from application.errors import ConcurrencyConflictError
from application.ledger import (
    LEDGER_SCOPE,
    TRANSACTION_POSTED,
    LedgerCommandService,
    LedgerRefused,
)
from domain.identity import DiscordUser
from domain.ledger import (
    AccountKind,
    AccountRef,
    LedgerEntry,
    LedgerTransaction,
    ResourceKind,
)
from domain.money import Money
from tests.fakes import FakeAuthorization, FakeLedgerPrincipals

pytestmark = pytest.mark.database

COUNCIL_USER = 4200000000000000011
OTHER_COUNCIL_USER = 4200000000000000012
#: A guild member holding no Council authority. Deliberately **not** inserted
#: into `discord_users`: every command this user makes is refused before
#: anything is written, so an audit row that needed the foreign key would be a
#: failure of the property under test rather than a fixture omission.
ORDINARY_USER = 4200000000000000013
POSTING_PRINCIPAL = "ledger-worker"
BOOK = UUID("33333333-3333-4333-8333-333333333333")
NOW = datetime(2026, 8, 29, 12, 0, tzinfo=timezone.utc)

#: One attempt's correlation identity — the same rule as the application-level
#: file. The envelope and the transaction it carries must name one id or the
#: command is refused (`correlation_mismatch`, P4-R5), so both helpers default to
#: this and a second attempt passes one fresh id to both.
ATTEMPT = UUID("dddddddd-dddd-4ddd-8ddd-dddddddddddd")

WALLET = AccountRef(BOOK, "wallet", AccountKind.HELD)
INCOME = AccountRef(BOOK, "income", AccountKind.COUNTERPARTY)
EXPENSE = AccountRef(BOOK, "expense", AccountKind.COUNTERPARTY)


# --- wiring -------------------------------------------------------------------


@pytest.fixture()
def ledger(committed_database):
    """Real transactions, one disposable database, one shared reference book."""
    engine = committed_database
    book = LedgerBook()

    def inner() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(engine)

    # Attribution is a foreign key, not a free-text field: an audit row naming a
    # Discord user the platform has never seen is refused by the database.
    with inner() as unit:
        unit.discord_users.add(
            DiscordUser(discord_id=COUNCIL_USER, username="synthetic-council")
        )
        unit.discord_users.add(
            DiscordUser(discord_id=OTHER_COUNCIL_USER, username="synthetic-council-2")
        )
        unit.commit()

    authorization = FakeAuthorization.with_council(COUNCIL_USER)
    authorization.grant(
        AuthorizationContext(
            discord_user_id=OTHER_COUNCIL_USER, guild_member=True, guild_council=True
        )
    )
    principals = FakeLedgerPrincipals.with_poster(POSTING_PRINCIPAL)
    service = LedgerCommandService(
        unit_of_work_factory(book, inner),
        authorization=authorization,
        principals=principals,
    )
    return {
        "engine": engine,
        "book": book,
        "inner": inner,
        "service": service,
        "authorization": authorization,
        "principals": principals,
    }


def envelope(
    *,
    key: str = "interaction-1",
    version: int = 0,
    user: int = COUNCIL_USER,
    correlation_id: UUID = ATTEMPT,
) -> CommandEnvelope:
    return CommandEnvelope(
        caller=CommandCaller(AuditSource.DISCORD, discord_user_id=user),
        idempotency_key=key,
        correlation_id=correlation_id,
        expected_version=ExpectedVersion("ledger_book", BOOK, version),
    )


def service_envelope(
    *,
    key: str = "interaction-1",
    version: int = 0,
    principal: str = POSTING_PRINCIPAL,
    correlation_id: UUID = ATTEMPT,
) -> CommandEnvelope:
    return CommandEnvelope(
        caller=CommandCaller(AuditSource.FOUNDRY, principal_id=principal),
        idempotency_key=key,
        correlation_id=correlation_id,
        expected_version=ExpectedVersion("ledger_book", BOOK, version),
    )


def reward(
    amount: int = 500,
    *,
    reason: str = "Mission reward",
    occurred_at: datetime = NOW,
    correlation_id: UUID = ATTEMPT,
) -> LedgerTransaction:
    return LedgerTransaction(
        entries=(
            LedgerEntry(WALLET, Money(amount)),
            LedgerEntry(INCOME, Money(-amount)),
        ),
        reason=reason,
        occurred_at=occurred_at,
        correlation_id=correlation_id,
    )


def count(engine, table: str, where: str = "TRUE") -> int:
    with engine.begin() as connection:
        return connection.execute(
            text(f"SELECT count(*) FROM {table} WHERE {where}")
        ).scalar_one()


def receipts(engine) -> int:
    return count(engine, "idempotency_keys", f"scope = '{LEDGER_SCOPE}'")


def posted_events(engine) -> int:
    return count(engine, "audit_events", f"action = '{TRANSACTION_POSTED}'")


# --- one command, one durable receipt -----------------------------------------


def test_a_committed_command_writes_one_receipt_and_one_audit_row(ledger):
    engine = ledger["engine"]

    receipt = ledger["service"].post(envelope(), reward())

    assert receipts(engine) == 1
    assert posted_events(engine) == 1
    assert len(ledger["book"].transactions_for(BOOK)) == 1
    assert receipt.duplicate is False


def test_the_receipt_is_stored_in_the_existing_idempotency_table(ledger):
    """No new table and no migration: an existing column under a new scope."""
    engine = ledger["engine"]

    receipt = ledger["service"].post(envelope(key="stored"), reward())

    with engine.begin() as connection:
        row = connection.execute(
            text(
                "SELECT scope, key, status, response, admission_id "
                "FROM idempotency_keys WHERE scope = :scope"
            ),
            {"scope": LEDGER_SCOPE},
        ).mappings().one()

    assert row["scope"] == LEDGER_SCOPE
    assert row["key"] == "stored"
    assert row["status"] == "completed"
    assert row["response"] == receipt.as_payload()
    # The admission fence belongs to the Foundry submission scope and to no
    # other; this scope is deliberately unfenced, and the table's check
    # constraint permits that for every scope but that one.
    assert row["admission_id"] is None


def test_the_stored_receipt_survives_a_json_round_trip_unchanged(ledger):
    """The property a retry depends on, read back out of PostgreSQL itself."""
    request = envelope(key="round-trip")
    original = ledger["service"].post(request, reward())

    replayed = ledger["service"].post(request, reward())

    assert replayed.duplicate is True
    assert replayed.facts == original.facts
    assert replayed.version == original.version
    assert replayed.correlation_id == original.correlation_id


# --- retry --------------------------------------------------------------------


def test_a_repeated_key_with_identical_content_executes_the_effect_once(ledger):
    engine = ledger["engine"]
    request = envelope(key="retry")

    first = ledger["service"].post(request, reward())
    second = ledger["service"].post(request, reward())
    third = ledger["service"].post(request, reward())

    assert (second.duplicate, third.duplicate) == (True, True)
    assert second.facts == third.facts == first.facts
    assert receipts(engine) == 1
    assert posted_events(engine) == 1
    assert len(ledger["book"].transactions_for(BOOK)) == 1
    assert ledger["book"].balance(WALLET, ResourceKind.MONEY) == Money(500)


def test_a_retry_returns_the_original_result_after_the_book_has_moved_on(ledger):
    """The stored receipt, not a recomputation of the system as it is now."""
    request = envelope(key="a", version=0)
    original = ledger["service"].post(request, reward())
    ledger["service"].post(envelope(key="b", version=1), reward(200))

    replayed = ledger["service"].post(request, reward())

    assert replayed.version == original.version == 1
    assert replayed.facts["transaction_id"] == original.facts["transaction_id"]


# --- conflicting reuse --------------------------------------------------------


def test_reuse_of_a_key_with_different_content_fails_closed(ledger):
    engine = ledger["engine"]
    request = envelope(key="reused")
    ledger["service"].post(request, reward(500))

    with pytest.raises(LedgerRefused) as refusal:
        ledger["service"].post(request, reward(9999))

    assert refusal.value.code == "idempotency_key_conflict"
    assert receipts(engine) == 1
    assert posted_events(engine) == 1
    assert ledger["book"].balance(WALLET, ResourceKind.MONEY) == Money(500)


def test_a_conflicting_reuse_is_never_answered_with_the_original_receipt(ledger):
    """Returning it would describe an operation this request is not."""
    request = envelope(key="reused")
    ledger["service"].post(request, reward(500))

    with pytest.raises(LedgerRefused):
        ledger["service"].post(request, reward(9999))


def test_the_scope_isolates_phase_4_keys_from_every_other_users(ledger):
    """`(scope, key)` is unique; the same key in another scope is another key."""
    engine = ledger["engine"]
    ledger["service"].post(envelope(key="shared-key"), reward())

    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO idempotency_keys (id, scope, key, request_hash, status) "
                "VALUES (:id, 'some.other.scope', 'shared-key', :digest, 'completed')"
            ),
            {"id": uuid4(), "digest": bytes(32)},
        )

    assert receipts(engine) == 1
    assert count(engine, "idempotency_keys") == 2


# --- optimistic concurrency ---------------------------------------------------


def test_a_stale_expected_version_commits_nothing_to_the_database(ledger):
    engine = ledger["engine"]
    ledger["service"].post(envelope(key="a", version=0), reward())

    with pytest.raises(ConcurrencyConflictError):
        ledger["service"].post(envelope(key="b", version=0), reward(999))

    assert receipts(engine) == 1
    assert posted_events(engine) == 1
    assert len(ledger["book"].transactions_for(BOOK)) == 1


# --- two concurrent callers ---------------------------------------------------


def race(ledger, requests, transactions) -> list[object]:
    """Run each command from its own connection at the same instant.

    Each thread builds its own engine, unit-of-work factory and service, so the
    attempts are real PostgreSQL transactions on real separate connections. They
    share one `LedgerBook`, because two racing callers must contend for one
    authority rather than each winning a book of its own.
    """
    url = str(ledger["engine"].url)
    book = ledger["book"]
    results: list[object] = []
    lock = threading.Lock()
    barrier = threading.Barrier(len(requests))

    def run(index: int) -> None:
        engine = create_engine(url)
        service = LedgerCommandService(
            unit_of_work_factory(book, lambda: SqlAlchemyUnitOfWork(engine)),
            authorization=FakeAuthorization.with_council(COUNCIL_USER),
            principals=FakeLedgerPrincipals.with_poster(POSTING_PRINCIPAL),
        )
        try:
            barrier.wait(timeout=10)
            outcome = service.post(requests[index], transactions[index])
        except Exception as error:  # noqa: BLE001 - the outcome is the assertion
            outcome = error
        finally:
            engine.dispose()
        with lock:
            results.append(outcome)

    threads = [threading.Thread(target=run, args=(i,)) for i in range(len(requests))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
    assert len(results) == len(requests), "a racing thread never finished"
    return results


def test_two_concurrent_callers_of_one_key_produce_one_durable_winner(ledger):
    """The mandatory scenario, against the real unique index.

    Sequentially this is the early idempotency read; concurrently it is a lost
    race on `uq_idempotency_keys_scope_key`, resolved by re-reading the winner's
    row rather than by assuming what it says.
    """
    engine = ledger["engine"]
    request = envelope(key="same-key")
    requests = [request, request]
    transactions = [reward(500), reward(500)]

    results = race(ledger, requests, transactions)

    assert not [r for r in results if isinstance(r, BaseException)], results
    winners = [r for r in results if not r.duplicate]
    losers = [r for r in results if r.duplicate]
    assert len(winners) == 1, results
    assert len(losers) == 1
    assert losers[0].facts == winners[0].facts
    assert losers[0].version == winners[0].version

    assert receipts(engine) == 1
    assert posted_events(engine) == 1
    assert len(ledger["book"].transactions_for(BOOK)) == 1
    assert ledger["book"].balance(WALLET, ResourceKind.MONEY) == Money(500)


def test_a_concurrent_loser_never_escapes_as_a_driver_exception(ledger):
    """A raw `IntegrityError` would carry the statement and its parameters."""
    request = envelope(key="same-key")
    results = race(ledger, [request] * 3, [reward(500) for _ in range(3)])

    for result in results:
        if isinstance(result, BaseException):
            assert not isinstance(result, (IntegrityError, DBAPIError)), result
            assert isinstance(result, LedgerRefused), result
    assert receipts(ledger["engine"]) == 1


def test_two_concurrent_callers_of_two_keys_produce_one_version_winner(ledger):
    """Both decided against version 0; only one may commit against it.

    The loser is refused as stale rather than silently posting a second
    transaction against a version that no longer exists.
    """
    engine = ledger["engine"]
    requests = [envelope(key="k-0", version=0), envelope(key="k-1", version=0)]
    transactions = [reward(500), reward(700)]

    results = race(ledger, requests, transactions)

    receipts_returned = [r for r in results if not isinstance(r, BaseException)]
    refusals = [r for r in results if isinstance(r, BaseException)]
    assert len(receipts_returned) == 1, results
    assert len(refusals) == 1
    assert isinstance(refusals[0], ConcurrencyConflictError), refusals[0]

    assert receipts(engine) == 1
    assert posted_events(engine) == 1
    assert len(ledger["book"].transactions_for(BOOK)) == 1


# --- P4-R1: a failed durable commit against a real transaction ----------------


def paused_commit_factory(book, inner_factory, *, arrived, release):
    """A unit of work whose durable commit stops, then fails, inside the book.

    The same instrument as the application-level regression, against a real
    PostgreSQL transaction: the receipt and the audit row are genuinely in
    flight when the failure is injected, so what is asserted afterwards is what
    the database kept.
    """

    class _Paused(LedgerUnitOfWork):
        def commit(self) -> None:
            def paused() -> None:
                arrived.set()
                assert release.wait(timeout=30), "the test never released the commit"
                raise InjectedFailure("injected durable commit failure")

            self._inner.commit = paused
            super().commit()

    def factory():
        return _Paused(book, inner_factory())

    return factory


def announcing_commit_factory(book, inner_factory, *, at_commit):
    class _Announcing(LedgerUnitOfWork):
        def commit(self) -> None:
            at_commit.set()
            super().commit()

    def factory():
        return _Announcing(book, inner_factory())

    return factory


def test_a_failed_durable_commit_keeps_the_concurrent_winners_database_rows(ledger):
    """The mandatory P4-R1 regression, with real receipts and real audit rows.

    Caller A stops inside its durable commit — the point at which the previous
    shape had already made its posting visible — and then fails. Caller B posts
    validly on the shared book with a distinct key while A is there. What
    survives must be exactly B: its transaction, its receipt row, its one audit
    row, and a version and balance that describe B-only history.
    """
    engine = ledger["engine"]
    url = str(engine.url)
    book = ledger["book"]
    arrived = threading.Event()
    release = threading.Event()
    at_commit = threading.Event()
    outcomes: dict[str, object] = {}

    def build(factory_maker, **events):
        own = create_engine(url)
        service = LedgerCommandService(
            factory_maker(book, lambda: SqlAlchemyUnitOfWork(own), **events),
            authorization=FakeAuthorization.with_council(COUNCIL_USER),
            principals=FakeLedgerPrincipals.with_poster(POSTING_PRINCIPAL),
        )
        return own, service

    def run(name, service, own, request, transaction):
        def body() -> None:
            try:
                outcomes[name] = service.post(request, transaction)
            except BaseException as error:  # noqa: BLE001 - asserted below
                outcomes[name] = error
            finally:
                own.dispose()

        thread = threading.Thread(target=body, name=name)
        thread.start()
        return thread

    engine_a, doomed = build(
        paused_commit_factory, arrived=arrived, release=release
    )
    engine_b, winner = build(announcing_commit_factory, at_commit=at_commit)

    thread_a = run(
        "a", doomed, engine_a, envelope(key="doomed", version=0), reward(500)
    )
    assert arrived.wait(timeout=30)
    assert book.transactions_for(BOOK) == ()

    thread_b = run(
        "b", winner, engine_b, envelope(key="winner", version=0), reward(700)
    )
    assert at_commit.wait(timeout=30)
    release.set()
    thread_a.join(timeout=60)
    thread_b.join(timeout=60)
    assert not thread_a.is_alive() and not thread_b.is_alive()

    assert isinstance(outcomes["a"], InjectedFailure), outcomes["a"]
    assert not isinstance(outcomes["b"], BaseException), outcomes["b"]
    assert receipts(engine) == 1
    assert posted_events(engine) == 1
    with engine.begin() as connection:
        key = connection.execute(
            text("SELECT key FROM idempotency_keys WHERE scope = :scope"),
            {"scope": LEDGER_SCOPE},
        ).scalar_one()
    assert key == "winner"
    assert len(book.transactions_for(BOOK)) == 1
    assert book.version_of(BOOK) == 1
    assert book.balance(WALLET, ResourceKind.MONEY) == Money(700)

    following = ledger["service"].post(envelope(key="next", version=1), reward(200))
    assert following.version == 2
    assert receipts(engine) == 2


class InjectedFailure(RuntimeError):
    """A deliberate mid-transaction failure, raised inside a real commit."""


# --- P4-R2: service-principal authority, durably --------------------------- #


def test_an_authorized_principal_is_recorded_as_the_resolved_principal(ledger):
    """The audit row names the principal the port returned, safely."""
    engine = ledger["engine"]

    ledger["service"].post(service_envelope(), reward())

    with engine.begin() as connection:
        row = connection.execute(
            text(
                "SELECT actor_capability, actor_discord_user_id, source, payload "
                "FROM audit_events WHERE action = :action"
            ),
            {"action": TRANSACTION_POSTED},
        ).mappings().one()

    assert row["actor_capability"] == "service_principal"
    assert row["actor_discord_user_id"] is None
    assert row["source"] == "foundry"
    assert row["payload"]["service_principal_id"] == POSTING_PRINCIPAL


@pytest.mark.parametrize(
    "prepare, principal",
    [
        (lambda ledger: None, "never-configured"),
        (
            lambda ledger: ledger["principals"].revoke(POSTING_PRINCIPAL),
            POSTING_PRINCIPAL,
        ),
        (
            lambda ledger: ledger["principals"].deactivate(POSTING_PRINCIPAL),
            POSTING_PRINCIPAL,
        ),
    ],
    ids=["unknown", "revoked", "deactivated"],
)
def test_an_unresolved_principal_writes_nothing_to_the_database(
    ledger, prepare, principal
):
    engine = ledger["engine"]
    prepare(ledger)

    with pytest.raises(LedgerRefused) as refusal:
        ledger["service"].post(service_envelope(principal=principal), reward())

    assert refusal.value.code == "not_authorized"
    assert receipts(engine) == 0
    assert posted_events(engine) == 0
    assert count(engine, "audit_events") == 0
    assert ledger["book"].transactions_for(BOOK) == ()


def test_a_principal_authorized_now_may_be_refused_on_the_next_command(ledger):
    """Authority is re-resolved per execution, against durable evidence."""
    engine = ledger["engine"]
    ledger["service"].post(service_envelope(key="a", version=0), reward())
    ledger["principals"].revoke(POSTING_PRINCIPAL)

    with pytest.raises(LedgerRefused):
        ledger["service"].post(service_envelope(key="b", version=1), reward())

    assert receipts(engine) == 1
    assert posted_events(engine) == 1
    assert ledger["principals"].asked == [POSTING_PRINCIPAL, POSTING_PRINCIPAL]


# --- P4-R3: command identity, against the stored digest -------------------- #


def test_a_different_occurrence_time_conflicts_against_the_stored_digest(ledger):
    engine = ledger["engine"]
    request = envelope(key="shared")
    ledger["service"].post(request, reward(500, occurred_at=NOW))

    with pytest.raises(LedgerRefused) as refusal:
        ledger["service"].post(
            request, reward(500, occurred_at=NOW + timedelta(seconds=1))
        )

    assert refusal.value.code == "idempotency_key_conflict"
    assert receipts(engine) == 1
    assert posted_events(engine) == 1
    assert len(ledger["book"].transactions_for(BOOK)) == 1


def test_another_caller_cannot_replay_a_stored_receipt(ledger):
    """A second Council member, and a service principal, are other commands."""
    engine = ledger["engine"]
    ledger["service"].post(envelope(key="shared"), reward(500))

    for other in (
        envelope(key="shared", user=OTHER_COUNCIL_USER),
        service_envelope(key="shared"),
    ):
        with pytest.raises(LedgerRefused) as refusal:
            ledger["service"].post(other, reward(500))
        assert refusal.value.code == "idempotency_key_conflict"

    assert receipts(engine) == 1
    assert posted_events(engine) == 1


def test_the_stored_digest_is_the_declared_width_and_is_never_rewritten(ledger):
    """A retry compares against the row as stored, and leaves it as stored."""
    engine = ledger["engine"]
    request = envelope(key="stable")
    ledger["service"].post(request, reward())

    with engine.begin() as connection:
        before = connection.execute(
            text("SELECT request_hash FROM idempotency_keys WHERE key = 'stable'")
        ).scalar_one()

    ledger["service"].post(request, reward())

    with engine.begin() as connection:
        after = connection.execute(
            text("SELECT request_hash FROM idempotency_keys WHERE key = 'stable'")
        ).scalar_one()

    assert len(bytes(before)) == 32
    assert bytes(after) == bytes(before)


def test_a_corrupted_stored_receipt_fails_closed_without_re_executing(ledger):
    """The key is spent, so the effect may have happened.

    Re-executing could duplicate it and inventing a receipt would state facts
    nothing recorded, so both are refused — proved against the stored row rather
    than a fake, because it is the stored row that gets corrupted in practice.
    """
    engine = ledger["engine"]
    request = envelope(key="corrupt")
    ledger["service"].post(request, reward())

    with engine.begin() as connection:
        connection.execute(
            text(
                "UPDATE idempotency_keys SET response = :response "
                "WHERE scope = :scope AND key = 'corrupt'"
            ),
            {"response": '{"command": "ledger.post_transaction"}', "scope": LEDGER_SCOPE},
        )

    with pytest.raises(LedgerRefused) as refusal:
        ledger["service"].post(request, reward())

    assert refusal.value.code == "original_result_unavailable"
    assert posted_events(engine) == 1
    assert len(ledger["book"].transactions_for(BOOK)) == 1


# --- safety of what reaches a caller and history ------------------------------


def test_a_refusal_carries_no_sql_no_parameters_and_no_driver_name(ledger):
    request = envelope(key="reused")
    ledger["service"].post(request, reward(500))

    with pytest.raises(LedgerRefused) as refusal:
        ledger["service"].post(request, reward(9999))

    message = str(refusal.value)
    for forbidden in ("INSERT", "SELECT", "psycopg", "idempotency_keys", "9999"):
        assert forbidden not in message, forbidden


def test_the_audit_payload_records_the_reason_and_no_amounts(ledger):
    """History carries what happened, not what anybody holds."""
    engine = ledger["engine"]
    ledger["service"].post(envelope(), reward(500, reason="Mission reward"))

    with engine.begin() as connection:
        payload = connection.execute(
            text(
                "SELECT payload FROM audit_events WHERE action = :action"
            ),
            {"action": TRANSACTION_POSTED},
        ).scalar_one()

    assert payload["reason"] == "Mission reward"
    assert payload["resource"] == "money"
    assert payload["version"] == 1
    assert "500" not in str(payload.values())


def test_the_audit_row_names_the_acting_user_and_capability(ledger):
    engine = ledger["engine"]
    request = envelope()

    ledger["service"].post(request, reward())

    with engine.begin() as connection:
        row = connection.execute(
            text(
                "SELECT actor_discord_user_id, actor_capability, source, "
                "correlation_id FROM audit_events WHERE action = :action"
            ),
            {"action": TRANSACTION_POSTED},
        ).mappings().one()

    assert row["actor_discord_user_id"] == COUNCIL_USER
    assert row["actor_capability"] == "guild_council"
    assert row["source"] == "discord"
    assert row["correlation_id"] == request.correlation_id


# --- what the database itself refuses -----------------------------------------


def test_the_database_refuses_a_second_receipt_for_one_key(ledger):
    """The constraint the whole idempotency path rests on, exercised directly.

    Asserted against PostgreSQL rather than inferred from the service's
    behaviour: if this index were dropped, every test above would still pass on
    the service's own early read, and two concurrent callers would both commit.
    """
    engine = ledger["engine"]
    ledger["service"].post(envelope(key="only-once"), reward())

    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO idempotency_keys (id, scope, key, request_hash, "
                    "status) VALUES (:id, :scope, 'only-once', :digest, 'completed')"
                ),
                {"id": uuid4(), "scope": LEDGER_SCOPE, "digest": bytes(32)},
            )

    assert receipts(engine) == 1


def test_an_idempotency_receipt_is_never_updated_by_this_package(ledger):
    """There is no `update` on the repository, and none is used here.

    A receipt that could be rewritten would let a later request quietly redefine
    what an earlier one returned.
    """
    from application.repositories import IdempotencyRepository

    offered = {
        name for name in dir(IdempotencyRepository) if not name.startswith("_")
    }

    assert offered == {"add", "find"}


# --- P4-R4: a correction authorizes before it looks anything up, durably ---- #
#
# The application-level file proves the refusals are indistinguishable and that
# no unit of work is opened. What only PostgreSQL can prove is the other half:
# that none of these paths leaves a durable receipt or audit row behind, against
# the real `idempotency_keys` and `audit_events` tables.


class _OtherScopedPrincipal:
    """Resolves, is current, and holds some other scope."""

    principal_id = "read-only-worker"

    def holds(self, scope) -> bool:
        return False


class _WrongScopeDirectory:
    def __init__(self) -> None:
        self.asked: list[str] = []

    def current_principal(self, principal_id: str):
        self.asked.append(principal_id)
        return _OtherScopedPrincipal()


def _ordinary_member(ledger):
    return ledger["service"], lambda key: envelope(
        key=key, version=1, user=ORDINARY_USER
    )


def _revoked_member(ledger):
    ledger["authorization"].revoke(OTHER_COUNCIL_USER)
    return ledger["service"], lambda key: envelope(
        key=key, version=1, user=OTHER_COUNCIL_USER
    )


def _unknown_principal(ledger):
    return ledger["service"], lambda key: service_envelope(
        key=key, version=1, principal="never-configured"
    )


def _revoked_principal(ledger):
    ledger["principals"].revoke(POSTING_PRINCIPAL)
    return ledger["service"], lambda key: service_envelope(key=key, version=1)


def _deactivated_principal(ledger):
    ledger["principals"].deactivate(POSTING_PRINCIPAL)
    return ledger["service"], lambda key: service_envelope(key=key, version=1)


def _wrong_scope_principal(ledger):
    service = LedgerCommandService(
        unit_of_work_factory(ledger["book"], ledger["inner"]),
        authorization=ledger["authorization"],
        principals=_WrongScopeDirectory(),
    )
    return service, lambda key: service_envelope(
        key=key, version=1, principal="read-only-worker"
    )


UNAUTHORIZED_CALLERS = [
    _ordinary_member,
    _revoked_member,
    _unknown_principal,
    _revoked_principal,
    _deactivated_principal,
    _wrong_scope_principal,
]

UNAUTHORIZED_CALLER_IDS = [
    "ordinary-member",
    "revoked-member",
    "unknown-principal",
    "revoked-principal",
    "deactivated-principal",
    "wrong-scope-principal",
]


@pytest.mark.parametrize("caller", UNAUTHORIZED_CALLERS, ids=UNAUTHORIZED_CALLER_IDS)
def test_an_unauthorized_correction_writes_nothing_durable_either_way(ledger, caller):
    """Existing target and unknown target, one refusal, no durable trace."""
    engine = ledger["engine"]
    posted = reward(500)
    ledger["service"].post(envelope(key="a", version=0), posted)
    service, request_for = caller(ledger)

    answers = set()
    for key, target in (("b", posted.id), ("c", uuid4())):
        with pytest.raises(LedgerRefused) as refusal:
            service.compensate(
                request_for(key),
                transaction_id=target,
                reason="Undo",
                occurred_at=NOW,
            )
        answers.add((refusal.value.code, str(refusal.value)))

    assert len(answers) == 1
    assert answers.pop()[0] == "not_authorized"
    # The first posting's receipt and audit row, and nothing else.
    assert receipts(engine) == 1
    assert posted_events(engine) == 1
    assert count(engine, "audit_events") == 1
    assert ledger["book"].transactions_for(BOOK) == (posted,)


def test_an_authorized_correction_commits_one_posting_receipt_and_audit_row(ledger):
    engine = ledger["engine"]
    posted = reward(500)
    ledger["service"].post(envelope(key="a", version=0), posted)

    receipt = ledger["service"].compensate(
        envelope(key="b", version=1),
        transaction_id=posted.id,
        reason="Reward applied twice",
        occurred_at=NOW + timedelta(days=1),
    )

    assert receipt.facts["compensates"] == str(posted.id)
    assert receipts(engine) == 2
    assert posted_events(engine) == 2
    assert len(ledger["book"].transactions_for(BOOK)) == 2
    assert ledger["book"].balance(WALLET, ResourceKind.MONEY) == Money(0)


def test_a_correction_by_a_principal_records_the_resolved_principal_durably(ledger):
    engine = ledger["engine"]
    posted = reward(500)
    ledger["service"].post(service_envelope(key="a", version=0), posted)

    receipt = ledger["service"].compensate(
        service_envelope(key="b", version=1),
        transaction_id=posted.id,
        reason="Undo",
        occurred_at=NOW,
    )

    # Selected by the correction's own entity id rather than by ordering: two
    # rows written in one test can share a timestamp, and a test that depends on
    # which arrived first is asserting the clock's resolution.
    with engine.begin() as connection:
        row = connection.execute(
            text(
                "SELECT actor_capability, actor_discord_user_id, payload "
                "FROM audit_events WHERE entity_id = :entity_id"
            ),
            {"entity_id": receipt.facts["transaction_id"]},
        ).mappings().one()

    assert posted_events(engine) == 2
    assert row["actor_capability"] == "service_principal"
    assert row["actor_discord_user_id"] is None
    assert row["payload"]["service_principal_id"] == POSTING_PRINCIPAL


def test_a_correction_resolves_its_authority_port_exactly_once(ledger):
    """One operation, one reading — proved on the path that also persists."""
    posted = reward(500)
    ledger["service"].post(service_envelope(key="a", version=0), posted)
    ledger["principals"].asked.clear()
    ledger["authorization"].asked.clear()

    ledger["service"].compensate(
        service_envelope(key="b", version=1),
        transaction_id=posted.id,
        reason="Undo",
        occurred_at=NOW,
    )

    assert ledger["principals"].asked == [POSTING_PRINCIPAL]
    assert ledger["authorization"].asked == []


def test_a_true_retry_of_a_correction_creates_no_second_durable_effect(ledger):
    engine = ledger["engine"]
    posted = reward(500)
    ledger["service"].post(envelope(key="a", version=0), posted)
    first = ledger["service"].compensate(
        envelope(key="b", version=1),
        transaction_id=posted.id,
        reason="Undo",
        occurred_at=NOW,
    )

    second = ledger["service"].compensate(
        envelope(key="b", version=1, correlation_id=uuid4()),
        transaction_id=posted.id,
        reason="Undo",
        occurred_at=NOW,
    )

    assert second.duplicate is True
    assert second.facts == first.facts
    assert receipts(engine) == 2
    assert posted_events(engine) == 2
    assert len(ledger["book"].transactions_for(BOOK)) == 2


# --- P4-R5: one correlation identity per attempt, durably ------------------ #


def test_a_mismatched_correlation_leaves_the_database_empty(ledger):
    engine = ledger["engine"]

    with pytest.raises(LedgerRefused) as refusal:
        ledger["service"].post(
            envelope(key="k"), reward(500, correlation_id=uuid4())
        )

    assert refusal.value.code == "correlation_mismatch"
    assert receipts(engine) == 0
    assert count(engine, "audit_events") == 0
    assert ledger["book"].transactions_for(BOOK) == ()


def test_one_accepted_command_stores_one_correlation_id_in_every_record(ledger):
    """The stored receipt, the audit row and ledger history, read back out."""
    engine = ledger["engine"]
    attempt = uuid4()

    receipt = ledger["service"].post(
        envelope(key="k", correlation_id=attempt),
        reward(500, correlation_id=attempt),
    )

    with engine.begin() as connection:
        audit = connection.execute(
            text(
                "SELECT correlation_id FROM audit_events WHERE action = :action"
            ),
            {"action": TRANSACTION_POSTED},
        ).scalar_one()
        stored = connection.execute(
            text("SELECT response FROM idempotency_keys WHERE scope = :scope"),
            {"scope": LEDGER_SCOPE},
        ).scalar_one()

    assert receipt.correlation_id == attempt
    assert audit == attempt
    assert stored["correlation_id"] == str(attempt)
    assert ledger["book"].transactions_for(BOOK)[0].correlation_id == attempt


def test_a_retry_with_fresh_attempt_metadata_returns_the_stored_correlation(ledger):
    """A genuine retry may regenerate both halves and is still one effect."""
    engine = ledger["engine"]
    original = uuid4()
    first = ledger["service"].post(
        envelope(key="k", correlation_id=original),
        reward(500, correlation_id=original),
    )

    retry = uuid4()
    replay = ledger["service"].post(
        envelope(key="k", correlation_id=retry), reward(500, correlation_id=retry)
    )

    assert replay.duplicate is True
    assert replay.correlation_id == first.correlation_id == original
    assert receipts(engine) == 1
    assert posted_events(engine) == 1
    assert len(ledger["book"].transactions_for(BOOK)) == 1
