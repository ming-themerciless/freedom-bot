"""Phase 4 WP-3 — the concrete command-execution path, with fakes.

`LedgerCommandService` is the Phase 4 consumer of every protocol WP-2 and WP-3
introduce: the command envelope, the typed receipt, the ledger repository, the
narrowed unit of work, the authorization port and the existing typed persistence
errors. These tests exercise it against the in-memory reference ledger and the
in-memory unit of work.

**What a fake can and cannot prove.** It can prove that the service asks the
right questions in the right order, and that an injected failure at any write
point leaves nothing behind — because the fake unit of work models the one
property that matters, that uncommitted work disappears. It cannot prove a
PostgreSQL constraint or a lost race; those are
`tests/test_p4_idempotent_execution.py`, against the real database.
"""
from __future__ import annotations

import threading
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest

from adapters.ledger.in_memory import (
    LedgerBook,
    LedgerUnitOfWork,
    unit_of_work_factory,
)
from application.audit import ActorCapability, AuditSource
from application.authorization import AuthorizationContext
from application.commands import (
    CommandCaller,
    CommandEnvelope,
    ExpectedVersion,
    InvalidEnvelopeError,
)
from application.errors import ConcurrencyConflictError, UniquenessConflict
from application.idempotency import canonical_request_hash
from application.ledger import (
    LEDGER_SCOPE,
    POST_TRANSACTION,
    REFUSAL_CODES,
    TRANSACTION_POSTED,
    LedgerCommandService,
    LedgerPrincipal,
    LedgerRefused,
    LedgerRepository,
    LedgerScope,
)
from domain.ledger import (
    AccountKind,
    AccountRef,
    LedgerEntry,
    LedgerTransaction,
    ResourceKind,
)
from domain.money import Money
from domain.resources import Moradinium
from tests.fakes import (
    FakeAuthorization,
    FakeLedgerPrincipals,
    FakeStore,
    InjectedFailure,
    unit_of_work_factory as fake_unit_of_work_factory,
)

COUNCIL_USER = 4200000000000000001
ORDINARY_USER = 4200000000000000002
OTHER_COUNCIL_USER = 4200000000000000003
POSTING_PRINCIPAL = "ledger-worker"
OTHER_PRINCIPAL = "other-worker"
BOOK = UUID("11111111-1111-4111-8111-111111111111")
NOW = datetime(2026, 8, 29, 12, 0, tzinfo=timezone.utc)

#: One attempt's correlation identity. The envelope and the transaction it
#: carries must name the same one or the command is refused
#: (`correlation_mismatch`, review finding P4-R5), so the helpers below default
#: to this value and a test that needs a *second* attempt passes one fresh id to
#: both. Fixed rather than generated, so a helper's default cannot silently
#: become a mismatch.
ATTEMPT = UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc")

WALLET = AccountRef(BOOK, "wallet", AccountKind.HELD)
ESCROW = AccountRef(BOOK, "escrow", AccountKind.HELD)
INCOME = AccountRef(BOOK, "income", AccountKind.COUNTERPARTY)
EXPENSE = AccountRef(BOOK, "expense", AccountKind.COUNTERPARTY)


# --- wiring -------------------------------------------------------------------


class Harness:
    """One book, one store, one service, and the factories behind them."""

    def __init__(self) -> None:
        self.book = LedgerBook()
        self.store = FakeStore()
        self.inner = fake_unit_of_work_factory(self.store)
        self.authorization = FakeAuthorization.with_council(COUNCIL_USER)
        self.authorization.grant(
            AuthorizationContext(discord_user_id=ORDINARY_USER, guild_member=True)
        )
        self.authorization.grant(
            AuthorizationContext(
                discord_user_id=OTHER_COUNCIL_USER,
                guild_member=True,
                guild_council=True,
            )
        )
        self.principals = FakeLedgerPrincipals.with_poster(POSTING_PRINCIPAL)
        self.factory = unit_of_work_factory(self.book, self.inner)
        self.service = LedgerCommandService(
            self.factory,
            authorization=self.authorization,
            principals=self.principals,
        )

    def service_over(self, factory) -> LedgerCommandService:
        """The same service, over a factory that injects a failure."""
        return LedgerCommandService(
            factory,
            authorization=self.authorization,
            principals=self.principals,
        )

    # -- assertions the whole file shares --------------------------------- #

    def transactions(self) -> tuple[LedgerTransaction, ...]:
        return self.book.transactions_for(BOOK)

    def receipts(self) -> list:
        return [
            record
            for (scope, _), record in self.store.idempotency.items()
            if scope == LEDGER_SCOPE
        ]

    def audit_actions(self) -> list[str]:
        return [event.action for event in self.store.audit_events]

    def assert_nothing_happened(self) -> None:
        assert self.transactions() == ()
        assert self.receipts() == []
        assert self.store.audit_events == []


@pytest.fixture()
def harness() -> Harness:
    return Harness()


def envelope(
    *,
    key: str = "interaction-1",
    version: int = 0,
    user=COUNCIL_USER,
    correlation_id: UUID = ATTEMPT,
):
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
    source: AuditSource = AuditSource.FOUNDRY,
    correlation_id: UUID = ATTEMPT,
):
    return CommandEnvelope(
        caller=CommandCaller(source, principal_id=principal),
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


def purchase(
    amount: int = 500, *, correlation_id: UUID = ATTEMPT
) -> LedgerTransaction:
    return LedgerTransaction(
        entries=(
            LedgerEntry(WALLET, Money(-amount)),
            LedgerEntry(EXPENSE, Money(amount)),
        ),
        reason="Purchase",
        occurred_at=NOW,
        correlation_id=correlation_id,
    )


# --- the happy path -----------------------------------------------------------


def test_a_posting_commits_the_ledger_the_receipt_and_the_audit_together(harness):
    receipt = harness.service.post(envelope(), reward())

    assert receipt.command == POST_TRANSACTION
    assert receipt.duplicate is False
    assert receipt.version == 1
    assert len(harness.transactions()) == 1
    assert len(harness.receipts()) == 1
    assert harness.audit_actions() == [TRANSACTION_POSTED]
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(500)


def test_the_receipt_names_the_transaction_it_posted(harness):
    posted = reward()

    receipt = harness.service.post(envelope(), posted)

    assert receipt.facts["transaction_id"] == str(posted.id)
    assert receipt.facts["book_id"] == str(BOOK)
    assert receipt.facts["resource"] == "money"
    assert receipt.facts["entry_count"] == 2
    assert receipt.facts["compensates"] is None


def test_the_audit_event_records_the_authority_the_command_was_taken_under(harness):
    request = envelope()

    harness.service.post(request, reward())

    event = harness.store.audit_events[0]
    assert event.actor_capability is ActorCapability.GUILD_COUNCIL
    assert event.actor_discord_user_id == COUNCIL_USER
    assert event.source is AuditSource.DISCORD
    assert event.correlation_id == request.correlation_id
    assert event.payload["reason"] == "Mission reward"
    assert event.payload["version"] == 1


def test_the_version_advances_by_one_per_accepted_transaction(harness):
    harness.service.post(envelope(key="a", version=0), reward())
    second = harness.service.post(envelope(key="b", version=1), reward(200))

    assert second.version == 2
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(700)


def test_a_book_that_has_never_been_posted_to_is_at_version_zero(harness):
    """Zero is a value, not an absence: the first posting expects it."""
    assert harness.service.post(envelope(version=0), reward()).version == 1


def test_every_resource_can_be_posted(harness):
    moradinium = LedgerTransaction(
        entries=(
            LedgerEntry(WALLET, Moradinium(3)),
            LedgerEntry(INCOME, Moradinium(-3)),
        ),
        reason="Mining yield",
        occurred_at=NOW,
        correlation_id=ATTEMPT,
    )

    harness.service.post(envelope(), moradinium)

    assert harness.book.balance(WALLET, ResourceKind.MORADINIUM) == Moradinium(3)
    # …and the money balance of the same account is untouched, because a fold
    # over one resource never sees another's entries.
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(0)


# --- optimistic concurrency ---------------------------------------------------


def test_a_stale_expected_version_applies_nothing(harness):
    """The mandatory scenario, in the form that matters: *nothing* is applied.

    Not "the posting is refused but the receipt is written", and not "the audit
    row records an attempt". A caller that decided against a version of the book
    that no longer exists leaves the system exactly as it found it.
    """
    harness.service.post(envelope(key="a", version=0), reward())

    with pytest.raises(ConcurrencyConflictError):
        harness.service.post(envelope(key="b", version=0), reward(999))

    assert len(harness.transactions()) == 1
    assert len(harness.receipts()) == 1
    assert harness.audit_actions() == [TRANSACTION_POSTED]
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(500)


def test_a_version_ahead_of_the_book_is_also_stale(harness):
    """A caller cannot assert a future it has not observed."""
    with pytest.raises(ConcurrencyConflictError):
        harness.service.post(envelope(version=7), reward())

    harness.assert_nothing_happened()


def test_a_concurrency_conflict_names_no_statement_or_driver(harness):
    with pytest.raises(ConcurrencyConflictError) as conflict:
        harness.service.post(envelope(version=7), reward())

    message = str(conflict.value)
    assert "INSERT" not in message.upper()
    assert "psycopg" not in message
    assert str(BOOK) in message


def test_a_command_without_an_expected_version_is_refused(harness):
    request = CommandEnvelope(
        caller=CommandCaller(AuditSource.DISCORD, discord_user_id=COUNCIL_USER),
        idempotency_key="k",
        correlation_id=ATTEMPT,
    )

    with pytest.raises(InvalidEnvelopeError) as refusal:
        harness.service.post(request, reward())

    assert refusal.value.code == "missing_expected_version"
    harness.assert_nothing_happened()


def test_a_command_carrying_another_aggregates_version_is_refused(harness):
    request = CommandEnvelope(
        caller=CommandCaller(AuditSource.DISCORD, discord_user_id=COUNCIL_USER),
        idempotency_key="k",
        correlation_id=ATTEMPT,
        expected_version=ExpectedVersion("ledger_book", uuid4(), 0),
    )

    with pytest.raises(InvalidEnvelopeError) as refusal:
        harness.service.post(request, reward())

    assert refusal.value.code == "invalid_expected_version"
    harness.assert_nothing_happened()


# --- idempotency, against the fake --------------------------------------------


def test_a_retry_of_the_same_command_returns_the_original_receipt(harness):
    request = envelope()
    posted = reward()

    first = harness.service.post(request, posted)
    second = harness.service.post(request, posted)

    assert second.duplicate is True
    assert second.facts == first.facts
    assert second.version == first.version
    assert second.correlation_id == first.correlation_id
    assert len(harness.transactions()) == 1
    assert harness.audit_actions() == [TRANSACTION_POSTED]


def test_a_retry_answers_from_the_stored_receipt_not_a_recomputation(harness):
    """A recomputed receipt would describe the system as it is *now*.

    Every identifier in it claims to describe the moment the command committed,
    and the caller cannot tell the two instants apart. Here the book has moved on
    between the original and the retry, and the retry still answers with the
    original's version and transaction id.
    """
    request = envelope(key="a", version=0)
    original = harness.service.post(request, reward())
    harness.service.post(envelope(key="b", version=1), reward(200))

    replayed = harness.service.post(request, reward())

    assert replayed.version == original.version == 1
    assert replayed.facts["transaction_id"] == original.facts["transaction_id"]


def test_a_retry_with_a_freshly_built_transaction_is_still_a_retry(harness):
    """A Discord retry rebuilds its command object; the id is new each time.

    The canonical digest deliberately excludes the transaction id, so a rebuilt
    but identical command is recognised as the retry it is rather than refused
    as a conflict.
    """
    request = envelope()

    first = harness.service.post(request, reward())
    second = harness.service.post(request, reward())

    assert second.duplicate is True
    assert second.facts["transaction_id"] == first.facts["transaction_id"]
    assert len(harness.transactions()) == 1


def test_reusing_a_key_for_different_content_fails_closed(harness):
    request = envelope()
    harness.service.post(request, reward(500))

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(request, reward(9999))

    assert refusal.value.code == "idempotency_key_conflict"
    assert len(harness.transactions()) == 1
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(500)


# --- P4-R3: the complete command identity -------------------------------------
#
# The digest used to cover the book, the resource, the expected version, the
# reason, the compensation target and the entries. It did not cover the
# authoritative occurrence time or who was asking, so a key reused for history
# that would have been recorded differently — or reused by a different
# principal — hashed identically to the original and was answered as a retry.


def test_a_different_occurrence_time_under_one_key_conflicts(harness):
    """`occurred_at` is recorded in append-only history: it defines the command."""
    request = envelope()
    harness.service.post(request, reward(500, occurred_at=NOW))

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(
            request, reward(500, occurred_at=NOW + timedelta(days=1))
        )

    assert refusal.value.code == "idempotency_key_conflict"
    assert len(harness.transactions()) == 1


def test_one_microsecond_of_difference_is_a_different_command(harness):
    """The identity is the instant, not a rendering of it rounded to seconds."""
    request = envelope()
    harness.service.post(request, reward(500, occurred_at=NOW))

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(
            request, reward(500, occurred_at=NOW + timedelta(microseconds=1))
        )

    assert refusal.value.code == "idempotency_key_conflict"


def test_the_same_instant_in_another_timezone_is_the_same_command(harness):
    """One instant has one canonical form; 12:00Z and 13:00+01:00 are one moment."""
    request = envelope()
    first = harness.service.post(request, reward(500, occurred_at=NOW))

    replay = harness.service.post(
        request,
        reward(500, occurred_at=NOW.astimezone(timezone(timedelta(hours=1)))),
    )

    assert replay.duplicate is True
    assert replay.facts == first.facts
    assert len(harness.transactions()) == 1


def test_another_human_reusing_one_key_conflicts(harness):
    """Two Council members are two callers, whatever they ask for."""
    harness.service.post(envelope(key="shared", user=COUNCIL_USER), reward(500))

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(
            envelope(key="shared", user=OTHER_COUNCIL_USER), reward(500)
        )

    assert refusal.value.code == "idempotency_key_conflict"
    assert len(harness.transactions()) == 1


def test_another_service_principal_reusing_one_key_conflicts(harness):
    harness.principals.grant(OTHER_PRINCIPAL, LedgerScope.POST_TRANSACTION)
    harness.service.post(service_envelope(key="shared"), reward(500))

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(
            service_envelope(key="shared", principal=OTHER_PRINCIPAL), reward(500)
        )

    assert refusal.value.code == "idempotency_key_conflict"
    assert len(harness.transactions()) == 1


def test_a_principal_cannot_replay_a_persons_command_or_the_reverse(harness):
    harness.service.post(envelope(key="shared"), reward(500))

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(service_envelope(key="shared"), reward(500))

    assert refusal.value.code == "idempotency_key_conflict"


def test_the_same_principal_on_another_surface_conflicts(harness):
    """The surface is written into the audit row, so it is part of the record."""
    harness.service.post(
        service_envelope(key="shared", source=AuditSource.FOUNDRY), reward(500)
    )

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(
            service_envelope(key="shared", source=AuditSource.IMPORT), reward(500)
        )

    assert refusal.value.code == "idempotency_key_conflict"


def test_a_different_expected_version_under_one_key_conflicts(harness):
    harness.service.post(envelope(key="shared", version=0), reward(500))

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(envelope(key="shared", version=1), reward(500))

    assert refusal.value.code == "idempotency_key_conflict"


@pytest.mark.parametrize(
    "second",
    [
        lambda: reward(500, reason="A different reason"),
        lambda: reward(501),
        lambda: purchase(500),
        lambda: LedgerTransaction(
            entries=(
                LedgerEntry(ESCROW, Money(500)),
                LedgerEntry(INCOME, Money(-500)),
            ),
            reason="Mission reward",
            occurred_at=NOW,
            correlation_id=ATTEMPT,
        ),
        lambda: LedgerTransaction(
            entries=(
                LedgerEntry(INCOME, Money(-500)),
                LedgerEntry(WALLET, Money(500)),
            ),
            reason="Mission reward",
            occurred_at=NOW,
            correlation_id=ATTEMPT,
        ),
        lambda: LedgerTransaction(
            entries=(
                LedgerEntry(WALLET, Money(500)),
                LedgerEntry(INCOME, Money(-200)),
                LedgerEntry(EXPENSE, Money(-300)),
            ),
            reason="Mission reward",
            occurred_at=NOW,
            correlation_id=ATTEMPT,
        ),
        lambda: LedgerTransaction(
            entries=(
                LedgerEntry(AccountRef(BOOK, "wallet", AccountKind.COUNTERPARTY), Money(500)),
                LedgerEntry(INCOME, Money(-500)),
            ),
            reason="Mission reward",
            occurred_at=NOW,
            correlation_id=ATTEMPT,
        ),
    ],
    ids=[
        "reason",
        "amount",
        "direction",
        "account",
        "entry-order",
        "entry-count",
        "account-kind",
    ],
)
def test_the_canonical_digest_covers_what_makes_the_command_what_it_is(
    harness, second
):
    request = envelope()
    harness.service.post(request, reward(500))

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(request, second())

    assert refusal.value.code == "idempotency_key_conflict"
    assert len(harness.transactions()) == 1


def test_a_compensation_target_is_part_of_the_command_identity(harness):
    original = harness.service.post(envelope(key="a", version=0), reward(500))
    posted = harness.transactions()[0]
    request = envelope(key="shared", version=1)
    harness.service.compensate(
        request,
        transaction_id=posted.id,
        reason="Corrected",
        occurred_at=NOW,
    )
    assert original.version == 1

    # The same key, the same reason and the same instant — but reversing nothing.
    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(
            request,
            LedgerTransaction(
                entries=(
                    LedgerEntry(WALLET, Money(-500)),
                    LedgerEntry(INCOME, Money(500)),
                ),
                reason="Corrected",
                occurred_at=NOW,
                correlation_id=ATTEMPT,
            ),
        )

    assert refusal.value.code == "idempotency_key_conflict"


def test_a_correlation_id_is_attempt_metadata_and_not_command_identity(harness):
    """Stated explicitly, and the rule agrees with what a retry gets back.

    A retry rebuilds its envelope *and* its transaction, and the second attempt
    may carry a fresh correlation id in both — which is what the P4-R5 fence
    requires and what it deliberately still permits. It is the same command, and
    it is answered from the stored receipt, which carries the **original**
    attempt's correlation id because that is the attempt whose work was
    recorded.
    """
    first = harness.service.post(envelope(key="k"), reward(500))
    retry = uuid4()
    second_request = envelope(key="k", correlation_id=retry)
    assert second_request.correlation_id != first.correlation_id

    replay = harness.service.post(
        second_request, reward(500, correlation_id=retry)
    )

    assert replay.duplicate is True
    assert replay.correlation_id == first.correlation_id
    assert len(harness.transactions()) == 1
    assert harness.store.audit_events[0].correlation_id == first.correlation_id


def test_a_rebuilt_true_retry_executes_once_and_returns_the_accepted_identifiers(
    harness,
):
    """Everything a Discord retry regenerates: transaction id and correlations."""
    first = harness.service.post(envelope(key="k"), reward(500))
    posted = harness.transactions()[0]

    replay = harness.service.post(envelope(key="k"), reward(500))

    assert replay.duplicate is True
    assert replay.facts["transaction_id"] == first.facts["transaction_id"] == str(posted.id)
    assert len(harness.transactions()) == 1
    assert harness.audit_actions() == [TRANSACTION_POSTED]


def test_the_canonical_encoding_cannot_be_collided_by_resplitting_a_field():
    """Length-delimited, so no two field lists share a digest.

    A delimiter-joined encoding makes `["ab", "c"]` and `["a", "bc"]` equal as
    soon as a field can contain the delimiter — and a ledger reason may contain
    anything printable.
    """
    left = canonical_request_hash("s", [("f", "ab"), ("g", "c")])
    right = canonical_request_hash("s", [("f", "a"), ("g", "bc")])

    assert left != right


def test_the_canonical_encoding_distinguishes_a_number_text_and_nothing():
    digests = {
        canonical_request_hash("s", [("f", 1)]),
        canonical_request_hash("s", [("f", "1")]),
        canonical_request_hash("s", [("f", None)]),
        canonical_request_hash("s", [("f", "")]),
    }

    assert len(digests) == 4


def test_the_canonical_encoding_is_bound_to_its_schema_version():
    assert canonical_request_hash("v1", [("f", "x")]) != canonical_request_hash(
        "v2", [("f", "x")]
    )


def test_the_canonical_encoding_refuses_a_boolean():
    """`isinstance(True, int)` is `True`, and `True` is not the amount 1."""
    with pytest.raises(TypeError):
        canonical_request_hash("s", [("f", True)])


def test_a_different_key_posts_a_second_transaction(harness):
    harness.service.post(envelope(key="a", version=0), reward())
    harness.service.post(envelope(key="b", version=1), reward())

    assert len(harness.transactions()) == 2


def test_a_spent_key_whose_receipt_is_unreadable_is_never_re_executed(harness):
    """The key is spent, so the effect may have happened.

    Re-executing could duplicate it; inventing a receipt would state facts
    nothing recorded. Both are refused.
    """
    request = envelope()
    harness.service.post(request, reward())
    record = harness.receipts()[0]
    harness.store.idempotency[(LEDGER_SCOPE, request.idempotency_key)] = (
        _with_response(record, {"command": "ledger.post_transaction"})
    )

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(request, reward())

    assert refusal.value.code == "original_result_unavailable"
    assert len(harness.transactions()) == 1


def test_a_spent_key_with_no_stored_receipt_is_never_re_executed(harness):
    request = envelope()
    harness.service.post(request, reward())
    record = harness.receipts()[0]
    harness.store.idempotency[(LEDGER_SCOPE, request.idempotency_key)] = (
        _with_response(record, None)
    )

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(request, reward())

    assert refusal.value.code == "original_result_unavailable"
    assert len(harness.transactions()) == 1


def _with_response(record, response):
    import dataclasses

    return dataclasses.replace(record, response=response)


# P4-PG5. `CommandReceipt.__post_init__` stripped `command` before establishing
# that it was text, so a stored row whose command is not a string left
# `from_payload()` as a raw `AttributeError` — escaping the
# `StoredReceiptUnreadable` conversion `_replay_record` depends on, against a key
# whose effect may already have committed. The stored-command shapes below are
# the ones a corrupted or foreign-written `idempotency_keys.response` can hold.
@pytest.mark.parametrize(
    "command", [123, True, 1.0, None, b"ledger.post_transaction", ["x"], ("x",)]
)
def test_a_spent_key_with_a_malformed_stored_command_is_never_re_executed(
    harness, command
):
    """The replay refusal, end to end through the application service.

    Nothing is posted a second time, no second audit effect is created, and the
    unreadable receipt is left exactly as it was found rather than replaced by a
    reconstruction.
    """
    request = envelope()
    harness.service.post(request, reward())
    record = harness.receipts()[0]
    identity = (LEDGER_SCOPE, request.idempotency_key)
    corrupted = {
        "command": command,
        "correlation_id": str(ATTEMPT),
        "version": 1,
        "facts": {},
    }
    harness.store.idempotency[identity] = _with_response(record, corrupted)

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(request, reward())

    assert refusal.value.code == "original_result_unavailable"
    assert len(harness.transactions()) == 1
    assert harness.audit_actions() == [TRANSACTION_POSTED]
    assert len(harness.receipts()) == 1
    assert harness.store.idempotency[identity].response == corrupted


# --- insufficient resources ---------------------------------------------------


def test_a_held_account_may_not_go_below_zero(harness):
    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(envelope(), purchase(500))

    assert refusal.value.code == "insufficient_resources"
    harness.assert_nothing_happened()


def test_spending_exactly_what_is_held_is_permitted(harness):
    harness.service.post(envelope(key="a", version=0), reward(500))

    harness.service.post(envelope(key="b", version=1), purchase(500))

    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(0)


def test_spending_one_more_than_is_held_is_refused(harness):
    harness.service.post(envelope(key="a", version=0), reward(500))

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(envelope(key="b", version=1), purchase(501))

    assert refusal.value.code == "insufficient_resources"
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(500)
    assert len(harness.transactions()) == 1


def test_a_counterparty_account_is_unbounded(harness):
    """Bounding it would mean the platform claimed to know the world's balance."""
    harness.service.post(envelope(), reward(500))

    assert harness.book.balance(INCOME, ResourceKind.MONEY) == Money(-500)


def test_the_balance_check_nets_a_transaction_that_touches_one_account_twice(
    harness,
):
    harness.service.post(envelope(key="a", version=0), reward(500))

    both_ways = LedgerTransaction(
        entries=(
            LedgerEntry(WALLET, Money(-600)),
            LedgerEntry(WALLET, Money(200)),
            LedgerEntry(EXPENSE, Money(400)),
        ),
        reason="Part exchange",
        occurred_at=NOW,
        correlation_id=ATTEMPT,
    )
    harness.service.post(envelope(key="b", version=1), both_ways)

    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(100)


def test_the_refusal_names_no_other_players_holdings(harness):
    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(envelope(), purchase(500))

    assert "wallet" in str(refusal.value)
    assert "500" not in str(refusal.value)


# --- authorization ------------------------------------------------------------


def test_an_ordinary_guild_member_is_refused(harness):
    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(envelope(user=ORDINARY_USER), reward())

    assert refusal.value.code == "not_authorized"
    harness.assert_nothing_happened()


def test_a_user_who_is_no_longer_a_guild_member_is_refused(harness):
    harness.authorization.revoke(COUNCIL_USER)

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(envelope(), reward())

    assert refusal.value.code == "not_authorized"
    harness.assert_nothing_happened()


def test_authority_is_resolved_now_rather_than_taken_from_the_request(harness):
    """The port is asked on every command, not once per session."""
    harness.service.post(envelope(key="a", version=0), reward())
    harness.service.post(envelope(key="b", version=1), reward())

    assert harness.authorization.asked == [COUNCIL_USER, COUNCIL_USER]


# --- P4-R2: service-principal authority is resolved, never asserted -----------
#
# Before the remediation, any `CommandCaller` carrying a non-blank `principal_id`
# was an authorized service principal: the envelope named an identity and the
# service read the name as a grant. Every test below calls the service directly,
# which is the level the defect lived at — an outer adapter's check, real or
# claimed, cannot be what makes these pass.


def test_a_currently_authorized_and_correctly_scoped_principal_succeeds(harness):
    receipt = harness.service.post(service_envelope(), reward())

    assert receipt.version == 1
    assert len(harness.transactions()) == 1
    assert harness.principals.asked == [POSTING_PRINCIPAL]


def test_a_successful_principal_command_is_attributed_to_the_resolved_principal(
    harness,
):
    """Safely: the capability, no person, and the id the *port* returned."""
    harness.service.post(service_envelope(), reward())

    event = harness.store.audit_events[0]
    assert event.actor_capability is ActorCapability.SERVICE_PRINCIPAL
    assert event.actor_discord_user_id is None
    assert event.source is AuditSource.FOUNDRY
    assert event.payload["service_principal_id"] == POSTING_PRINCIPAL
    # No person was resolved, so the human port was never asked.
    assert harness.authorization.asked == []


def test_a_human_command_records_no_service_principal(harness):
    harness.service.post(envelope(), reward())

    event = harness.store.audit_events[0]
    assert event.payload["service_principal_id"] is None
    assert harness.principals.asked == []


def test_an_unknown_principal_is_refused(harness):
    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(service_envelope(principal="never-configured"), reward())

    assert refusal.value.code == "not_authorized"
    harness.assert_nothing_happened()


def test_a_revoked_principal_is_refused(harness):
    """A credential withdrawn between two commands must refuse the second."""
    harness.service.post(service_envelope(key="a", version=0), reward())
    harness.principals.revoke(POSTING_PRINCIPAL)

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(service_envelope(key="b", version=1), reward())

    assert refusal.value.code == "not_authorized"
    assert len(harness.transactions()) == 1


def test_a_deactivated_principal_is_refused(harness):
    harness.principals.deactivate(POSTING_PRINCIPAL)

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(service_envelope(), reward())

    assert refusal.value.code == "not_authorized"
    harness.assert_nothing_happened()


class _OtherScopedPrincipal:
    """A principal that exists and does not hold the ledger posting scope.

    Written as a stand-in rather than a `LedgerPrincipal`, because `LedgerScope`
    has exactly one member today and a principal holding only *another* scope
    therefore cannot be constructed. The check exists for the moment a second
    scope does, and this is what exercises it now.
    """

    principal_id = "read-only-worker"

    def holds(self, scope) -> bool:
        return False


class _WrongScopeDirectory:
    def __init__(self) -> None:
        self.asked: list[str] = []

    def current_principal(self, principal_id: str):
        self.asked.append(principal_id)
        return _OtherScopedPrincipal()


def test_a_principal_without_the_posting_scope_is_refused(harness):
    service = LedgerCommandService(
        harness.factory,
        authorization=harness.authorization,
        principals=_WrongScopeDirectory(),
    )

    with pytest.raises(LedgerRefused) as refusal:
        service.post(service_envelope(principal="read-only-worker"), reward())

    assert refusal.value.code == "not_authorized"
    harness.assert_nothing_happened()


@pytest.mark.parametrize(
    "claimed",
    ["ledger-worker-2", "guild-council", "system", "admin"],
    ids=["near-miss", "authority-shaped", "system-shaped", "admin-shaped"],
)
def test_a_caller_constructed_principal_name_cannot_bypass_the_port(harness, claimed):
    """A name is a lookup. Choosing a convincing one resolves to nothing."""
    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(service_envelope(principal=claimed), reward())

    assert refusal.value.code == "not_authorized"
    assert harness.principals.asked == [claimed]
    harness.assert_nothing_happened()


def test_a_principal_refusal_says_which_of_its_causes_applies_to_none_of_them(
    harness,
):
    """Unknown, revoked, deactivated and out-of-scope read identically."""
    messages = set()
    for principal in ("never-configured", POSTING_PRINCIPAL):
        if principal == POSTING_PRINCIPAL:
            harness.principals.revoke(principal)
        with pytest.raises(LedgerRefused) as refusal:
            harness.service.post(service_envelope(principal=principal), reward())
        messages.add(str(refusal.value))

    assert len(messages) == 1
    message = messages.pop()
    assert "never-configured" not in message
    assert POSTING_PRINCIPAL not in message


def test_principal_authority_is_re_resolved_on_every_execution(harness):
    harness.service.post(service_envelope(key="a", version=0), reward())
    harness.service.post(service_envelope(key="b", version=1), reward())

    assert harness.principals.asked == [POSTING_PRINCIPAL, POSTING_PRINCIPAL]


def test_a_refused_principal_leaves_history_receipts_and_audit_untouched(harness):
    harness.service.post(service_envelope(key="a", version=0), reward(500))
    before = harness.transactions()
    harness.principals.revoke(POSTING_PRINCIPAL)

    with pytest.raises(LedgerRefused):
        harness.service.post(service_envelope(key="b", version=1), reward(700))

    assert harness.transactions() == before
    assert len(harness.receipts()) == 1
    assert harness.audit_actions() == [TRANSACTION_POSTED]
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(500)


def test_a_ledger_principal_holding_no_scope_cannot_be_constructed():
    """A principal that resolves and then fails every check is not 'revoked'."""
    with pytest.raises(ValueError):
        LedgerPrincipal(principal_id="worker", scopes=frozenset())


def test_a_ledger_principal_refuses_a_scope_that_is_merely_text():
    with pytest.raises(ValueError):
        LedgerPrincipal(
            principal_id="worker", scopes=frozenset({"ledger:transaction:post"})
        )


def test_a_ledger_principal_refuses_an_identifier_history_cannot_render():
    """The same rule the accepted service-principal model applies."""
    for identifier in ("", "Worker", "worker id", "x" * 65, "worker\n"):
        with pytest.raises(ValueError):
            LedgerPrincipal(
                principal_id=identifier,
                scopes=frozenset({LedgerScope.POST_TRANSACTION}),
            )


def test_every_refusal_code_the_service_raises_is_declared():
    """A code nobody declared would be free text wearing a code's clothes."""
    with pytest.raises(ValueError):
        LedgerRefused("something_went_wrong", "…")

    assert "not_authorized" in REFUSAL_CODES


# --- atomicity under injected failure -----------------------------------------


def test_an_injected_idempotency_failure_leaves_no_posted_transaction(harness):
    """The handover's requirement, in its exact form.

    "An idempotency-record failure cannot leave an unrecorded durable effect."
    The receipt is the record; if writing it fails, the posting must not survive.
    """
    harness.inner.fail_on = "idempotency"

    with pytest.raises(InjectedFailure):
        harness.service.post(envelope(), reward())

    harness.assert_nothing_happened()


def test_an_injected_audit_failure_leaves_no_posted_transaction(harness):
    harness.inner.fail_on = "audit"

    with pytest.raises(InjectedFailure):
        harness.service.post(envelope(), reward())

    harness.assert_nothing_happened()


def test_an_injected_failure_after_an_accepted_transaction_leaves_that_one_alone(
    harness,
):
    """Atomicity is per transaction, not per process."""
    harness.service.post(envelope(key="a", version=0), reward(500))
    harness.inner.fail_on = "idempotency"

    with pytest.raises(InjectedFailure):
        harness.service.post(envelope(key="b", version=1), reward(200))

    assert len(harness.transactions()) == 1
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(500)


def test_an_effect_failure_cannot_publish_success(harness):
    """The other direction: the posting fails, so no receipt claims it worked."""
    service = harness.service_over(
        failing_ledger_factory(harness.book, harness.inner)
    )

    with pytest.raises(InjectedFailure):
        service.post(envelope(), reward())

    harness.assert_nothing_happened()


def test_a_ledger_that_refuses_a_duplicate_identity_is_reported_as_a_conflict(
    harness,
):
    """`append` raises the same typed conflict the database adapter would.

    The service resolves it as a lost race rather than letting a repository's
    exception escape untyped.
    """
    posted = reward()
    harness.service.post(envelope(key="a", version=0), posted)

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(envelope(key="b", version=1), posted)

    assert refusal.value.code == "concurrent_posting"
    assert len(harness.transactions()) == 1


class _RefusingLedgerUnitOfWork(LedgerUnitOfWork):
    """A unit of work whose ledger refuses to accept anything.

    A subclass rather than an instance whose `__enter__` is reassigned: `with`
    looks a special method up on the **type**, so an instance attribute would be
    ignored and the test would pass for the wrong reason — the failure would
    never be injected at all.

    Written here rather than in `tests/fakes.py` because it exists to prove one
    property of one Phase 4 service; a shared fixture would invite it to drift
    into a second way of injecting failures.
    """

    #: What `append` raises. Overridden by the subclass below to inject the
    #: typed conflict instead of an arbitrary fault.
    failure = staticmethod(
        lambda: InjectedFailure("injected ledger append failure")
    )

    def __enter__(self):
        entered = super().__enter__()
        failure = type(self).failure

        def refuse(_transaction, *, expected_version):
            raise failure()

        entered.ledger.append = refuse
        return entered


class _ConflictingLedgerUnitOfWork(_RefusingLedgerUnitOfWork):
    """…and one whose ledger loses a race on an identity nothing here owns."""

    failure = staticmethod(lambda: UniquenessConflict("something_else.identity"))


def failing_ledger_factory(book, inner_factory, unit_class=_RefusingLedgerUnitOfWork):
    def factory():
        return unit_class(book, inner_factory())

    return factory


# --- the commit-time version fence --------------------------------------------


def test_a_book_that_moves_on_before_the_commit_refuses_the_posting(harness):
    """The early version read is a reading; the fence is the guarantee.

    Two callers who both read version 0 would both pass the comparison made when
    their transactions opened. Here the second caller's unit of work is opened
    first — so its early read sees version 0 — and the first caller commits
    before it does. The precondition is re-checked where the write becomes
    visible, and the overtaken caller applies nothing.
    """
    overtaken = harness.factory()
    overtaken.__enter__()
    assert overtaken.ledger.version_of(BOOK) == 0

    harness.service.post(envelope(key="winner", version=0), reward(500))

    overtaken.ledger.append(reward(700), expected_version=0)
    with pytest.raises(ConcurrencyConflictError):
        overtaken.commit()
    overtaken.__exit__(None, None, None)

    assert len(harness.transactions()) == 1
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(500)


def test_a_failed_durable_commit_leaves_no_posting(harness):
    """"An idempotency-record failure cannot leave an unrecorded durable effect."

    The injected-failure tests above fail *before* the commit. This one fails
    *during* it — the one ordering in which a posting could survive a receipt
    that never became durable. It leaves nothing because nothing was ever
    appended, not because a compensating deletion put it back (P4-R1).
    """
    service = harness.service_over(
        failing_commit_factory(harness.book, harness.inner)
    )

    with pytest.raises(InjectedFailure):
        service.post(envelope(), reward())

    harness.assert_nothing_happened()


def test_a_failed_durable_commit_leaves_the_book_free_for_the_next_command(harness):
    """The version is untouched too, not only the transaction list."""
    service = harness.service_over(
        failing_commit_factory(harness.book, harness.inner)
    )
    with pytest.raises(InjectedFailure):
        service.post(envelope(key="doomed"), reward())

    receipt = harness.service.post(envelope(key="next", version=0), reward(200))

    assert receipt.version == 1
    assert len(harness.transactions()) == 1
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(200)


class _FailingCommitUnitOfWork(LedgerUnitOfWork):
    """A unit of work whose *durable* half refuses at the moment of commit."""

    def commit(self) -> None:
        self._inner.commit = _raise_injected
        super().commit()


def _raise_injected() -> None:
    raise InjectedFailure("injected durable commit failure")


def failing_commit_factory(book, inner_factory):
    def factory():
        return _FailingCommitUnitOfWork(book, inner_factory())

    return factory


# --- P4-R1: two callers, one book, one failed durable commit ------------------
#
# The shape this replaces published the posting, released the book's lock,
# committed the durable half, and on failure deleted the last N transactions.
# Two things were wrong with it and each has a test here: the posting was
# externally visible before anything had committed, and the rollback was
# **positional**, so it could delete a concurrent caller's committed transaction
# and keep the failed caller's own.
#
# Synchronization is by events, never by sleeping. `arrived` and `at_commit` are
# set by the units of work themselves at named points, so the interleaving is
# decided by the test rather than by how long anything happens to take.


def paused_commit_factory(book, inner_factory, *, arrived, release, fail: bool):
    """A unit of work that stops *inside* its durable commit until released.

    That is the instant the old shape had already made its posting visible, and
    the instant the new one is holding the book across its durable commit. It is
    the only point at which the difference between them is observable.
    """

    class _Paused(LedgerUnitOfWork):
        def commit(self) -> None:
            durable = self._inner.commit

            def paused() -> None:
                arrived.set()
                assert release.wait(timeout=30), "the test never released the commit"
                if fail:
                    raise InjectedFailure("injected durable commit failure")
                durable()

            self._inner.commit = paused
            super().commit()

    def factory():
        return _Paused(book, inner_factory())

    return factory


def announcing_commit_factory(book, inner_factory, *, at_commit):
    """A unit of work that says when it is about to reach for the book."""

    class _Announcing(LedgerUnitOfWork):
        def commit(self) -> None:
            at_commit.set()
            super().commit()

    def factory():
        return _Announcing(book, inner_factory())

    return factory


def _post_in_thread(service, request, transaction, outcomes, name):
    def run() -> None:
        try:
            outcomes[name] = service.post(request, transaction)
        except BaseException as error:  # noqa: BLE001 - the outcome is asserted
            outcomes[name] = error

    thread = threading.Thread(target=run, name=name)
    thread.start()
    return thread


def test_an_in_flight_posting_is_not_visible_before_its_durable_commit(harness):
    """Property 1, on its own and in the direction that succeeds.

    A reader looking while a commit is in flight sees committed history, and
    committed history does not yet include the posting being decided. This is
    the assertion the previous shape failed: it published first, so the
    transaction was there — and deletable by somebody else's rollback.
    """
    arrived = threading.Event()
    release = threading.Event()
    service = harness.service_over(
        paused_commit_factory(
            harness.book, harness.inner, arrived=arrived, release=release, fail=False
        )
    )
    outcomes: dict[str, object] = {}
    poster = _post_in_thread(service, envelope(key="a"), reward(500), outcomes, "a")

    assert arrived.wait(timeout=30)
    assert harness.transactions() == ()
    assert harness.book.version_of(BOOK) == 0
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(0)

    release.set()
    poster.join(timeout=30)

    assert not isinstance(outcomes["a"], BaseException), outcomes["a"]
    assert len(harness.transactions()) == 1
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(500)


def test_a_failed_durable_commit_cannot_remove_a_concurrent_callers_posting(harness):
    """The handover's mandatory regression, ordering by ordering.

    1. caller A reaches the point after its ledger work would previously have
       become visible — inside its durable commit;
    2. caller B, on the shared book with a distinct key, completes a valid
       posting;
    3. A's durable commit fails;
    4. A's transaction, receipt and success audit are absent;
    5. B's transaction, receipt and success audit remain;
    6. book version and affected balances equal B-only history; and
    7. a following command succeeds against the correct surviving version.
    """
    arrived = threading.Event()
    release = threading.Event()
    at_commit = threading.Event()
    doomed = harness.service_over(
        paused_commit_factory(
            harness.book, harness.inner, arrived=arrived, release=release, fail=True
        )
    )
    winner = harness.service_over(
        announcing_commit_factory(harness.book, harness.inner, at_commit=at_commit)
    )
    outcomes: dict[str, object] = {}

    thread_a = _post_in_thread(
        doomed, envelope(key="a", version=0), reward(500), outcomes, "a"
    )
    assert arrived.wait(timeout=30)
    # A is in its durable commit. Nothing of A's has become visible, which is
    # what makes the rest of this a test of *B's* survival rather than of a
    # deletion that happens to pick the right rows.
    assert harness.transactions() == ()

    thread_b = _post_in_thread(
        winner, envelope(key="b", version=0), reward(700), outcomes, "b"
    )
    assert at_commit.wait(timeout=30)
    release.set()
    thread_a.join(timeout=30)
    thread_b.join(timeout=30)
    assert not thread_a.is_alive() and not thread_b.is_alive()

    # 4 — A left nothing at all.
    assert isinstance(outcomes["a"], InjectedFailure), outcomes["a"]
    # 5 — B is intact: its transaction, its receipt, its one success audit row.
    assert not isinstance(outcomes["b"], BaseException), outcomes["b"]
    surviving = harness.transactions()
    assert len(surviving) == 1
    assert surviving[0].reason == "Mission reward"
    assert list(harness.store.idempotency) == [(LEDGER_SCOPE, "b")]
    assert harness.audit_actions() == [TRANSACTION_POSTED]
    # 6 — version and balance describe B-only history.
    assert outcomes["b"].version == 1
    assert harness.book.version_of(BOOK) == 1
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(700)
    # 7 — and the next command succeeds against that surviving version.
    following = harness.service.post(envelope(key="c", version=1), reward(200))
    assert following.version == 2
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(900)


def test_the_inverse_ordering_leaves_the_earlier_posting_alone(harness):
    """B first, then A fails. A's failure must not reach back to B."""
    winner = harness.service.post(envelope(key="b", version=0), reward(700))
    doomed = harness.service_over(
        failing_commit_factory(harness.book, harness.inner)
    )

    with pytest.raises(InjectedFailure):
        doomed.post(envelope(key="a", version=1), reward(500))

    assert len(harness.transactions()) == 1
    assert list(harness.store.idempotency) == [(LEDGER_SCOPE, "b")]
    assert harness.audit_actions() == [TRANSACTION_POSTED]
    assert winner.version == 1
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(700)
    assert harness.service.post(envelope(key="c", version=1), reward(200)).version == 2


def test_a_failed_commit_leaves_its_idempotency_key_free_for_the_same_key(harness):
    """The same-key ordering, which fails differently from the distinct-key one.

    A's receipt never became durable, so its key was never spent. A caller
    retrying with that key posts once — and must not be told the key is taken,
    nor be handed a receipt for a posting that does not exist.
    """
    doomed = harness.service_over(
        failing_commit_factory(harness.book, harness.inner)
    )
    with pytest.raises(InjectedFailure):
        doomed.post(envelope(key="shared", version=0), reward(500))

    receipt = harness.service.post(envelope(key="shared", version=0), reward(500))

    assert receipt.duplicate is False
    assert receipt.version == 1
    assert len(harness.transactions()) == 1
    assert list(harness.store.idempotency) == [(LEDGER_SCOPE, "shared")]
    assert harness.audit_actions() == [TRANSACTION_POSTED]


def test_the_book_offers_no_way_to_remove_an_accepted_transaction(harness):
    """Structural, not conventional: there is nothing to call.

    `retract` is gone, and no replacement takes its place. A rollback that
    cannot be expressed cannot delete another unit of work's transaction.
    """
    for forbidden in ("retract", "publish", "remove", "delete", "update"):
        assert not hasattr(harness.book, forbidden), forbidden


# --- compensation -------------------------------------------------------------


def test_a_correction_is_a_new_transaction_that_reverses_the_original(harness):
    original = harness.service.post(envelope(key="a", version=0), reward(500))
    original_id = UUID(original.facts["transaction_id"])

    correction = harness.service.compensate(
        envelope(key="b", version=1),
        transaction_id=original_id,
        reason="Reward applied twice",
        occurred_at=NOW + timedelta(days=1),
    )

    assert correction.facts["compensates"] == str(original_id)
    assert len(harness.transactions()) == 2
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(0)


def test_the_corrected_transaction_remains_exactly_as_accepted(harness):
    posted = reward(500)
    harness.service.post(envelope(key="a", version=0), posted)

    harness.service.compensate(
        envelope(key="b", version=1),
        transaction_id=posted.id,
        reason="Undo",
        occurred_at=NOW,
    )

    stored = [t for t in harness.transactions() if t.id == posted.id]
    assert stored == [posted]
    assert stored[0].compensates is None


def test_correcting_a_transaction_that_is_not_in_the_ledger_posts_nothing(harness):
    with pytest.raises(LedgerRefused) as refusal:
        harness.service.compensate(
            envelope(), transaction_id=uuid4(), reason="Undo", occurred_at=NOW
        )

    assert refusal.value.code == "concurrent_posting"
    harness.assert_nothing_happened()


def test_a_correction_that_would_overdraw_a_held_account_is_refused(harness):
    """A correction is a posting and obeys every rule a posting obeys."""
    original_id = UUID(
        harness.service.post(envelope(key="a", version=0), reward(100)).facts[
            "transaction_id"
        ]
    )
    harness.service.post(envelope(key="b", version=1), purchase(100))

    # The reward has already been spent, so reversing it would take the wallet
    # to minus one hundred copper — a debt nobody agreed to.
    with pytest.raises(LedgerRefused) as refusal:
        harness.service.compensate(
            envelope(key="c", version=2),
            transaction_id=original_id,
            reason="That reward was wrong",
            occurred_at=NOW,
        )

    assert refusal.value.code == "insufficient_resources"
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(0)
    assert len(harness.transactions()) == 2


def test_a_correction_is_itself_idempotent(harness):
    original = harness.service.post(envelope(key="a", version=0), reward(500))
    original_id = UUID(original.facts["transaction_id"])
    request = envelope(key="b", version=1)

    first = harness.service.compensate(
        request, transaction_id=original_id, reason="Undo", occurred_at=NOW
    )
    second = harness.service.compensate(
        request, transaction_id=original_id, reason="Undo", occurred_at=NOW
    )

    assert second.duplicate is True
    assert second.facts == first.facts
    assert len(harness.transactions()) == 2


# --- P4-R4: a correction authorizes before it looks anything up ---------------
#
# The defect was not an effect. No caller could post anything, and none of these
# paths ever wrote a posting, a receipt or an audit row. What leaked was a
# *distinction*: `compensate()` read `ledger.get()` first, so an unknown id came
# back with the missing-transaction refusal while an existing one went on to be
# authorized by `post()` and came back with `not_authorized`. Two refusals, one
# oracle. Every test below asserts the two answers are the same answer, and —
# stronger — that the ledger was never consulted at all, by counting the units of
# work the service opened.


def _compensation_refusal(service, request, transaction_id):
    """The refusal one compensation attempt produces, as a value to compare."""
    with pytest.raises(LedgerRefused) as refusal:
        service.compensate(
            request,
            transaction_id=transaction_id,
            reason="Undo",
            occurred_at=NOW,
        )
    return refusal.value


def _ordinary_member(harness):
    return harness.service, lambda key: envelope(key=key, version=1, user=ORDINARY_USER)


def _revoked_member(harness):
    """A Council member whose role was withdrawn between two commands."""
    harness.authorization.revoke(OTHER_COUNCIL_USER)
    return harness.service, lambda key: envelope(
        key=key, version=1, user=OTHER_COUNCIL_USER
    )


def _unknown_principal(harness):
    return harness.service, lambda key: service_envelope(
        key=key, version=1, principal="never-configured"
    )


def _revoked_principal(harness):
    harness.principals.revoke(POSTING_PRINCIPAL)
    return harness.service, lambda key: service_envelope(key=key, version=1)


def _deactivated_principal(harness):
    harness.principals.deactivate(POSTING_PRINCIPAL)
    return harness.service, lambda key: service_envelope(key=key, version=1)


def _wrong_scope_principal(harness):
    """Resolves, is current, and holds some other scope."""
    service = LedgerCommandService(
        harness.factory,
        authorization=harness.authorization,
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
def test_no_unauthorized_caller_can_tell_an_existing_transaction_from_an_unknown_one(
    harness, caller
):
    """The whole of P4-R4, once per caller shape that holds no authority.

    Both attempts must produce the *same* refusal — same code, same prose — and
    the prose must not name the transaction either. A caller that can distinguish
    the two has read the ledger through an authorization boundary it never
    crossed.
    """
    posted = reward(500)
    harness.service.post(envelope(key="a", version=0), posted)
    history = harness.transactions()
    opened = len(harness.inner.units)
    service, request_for = caller(harness)

    existing = _compensation_refusal(service, request_for("b"), posted.id)
    unknown = _compensation_refusal(service, request_for("c"), uuid4())

    assert (existing.code, str(existing)) == (unknown.code, str(unknown))
    assert existing.code == "not_authorized"
    assert str(posted.id) not in str(existing)
    # The refusals are identical because the question was never asked: no unit of
    # work was opened on either path, so `ledger.get` was never reached.
    assert len(harness.inner.units) == opened
    # And nothing was written, on either path, by any of these callers.
    assert harness.transactions() == history
    assert len(harness.receipts()) == 1
    assert harness.audit_actions() == [TRANSACTION_POSTED]


@pytest.mark.parametrize("caller", UNAUTHORIZED_CALLERS, ids=UNAUTHORIZED_CALLER_IDS)
def test_an_unauthorized_correction_of_an_existing_transaction_writes_nothing(
    harness, caller
):
    """Stated separately from the oracle, because it is a separate property.

    A refusal that leaked no distinction but still wrote an audit row would pass
    the test above and still be a defect.
    """
    posted = reward(500)
    harness.service.post(envelope(key="a", version=0), posted)
    service, request_for = caller(harness)

    _compensation_refusal(service, request_for("b"), posted.id)

    assert harness.transactions() == (posted,)
    assert [record.key for record in harness.receipts()] == ["a"]
    assert harness.audit_actions() == [TRANSACTION_POSTED]
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(500)


def test_a_human_correction_resolves_the_authorization_port_exactly_once(harness):
    """One operation, one reading of authority.

    Resolving before the lookup and then delegating to `post()` would resolve
    twice, and a resolution is a reading with a time: the second could answer
    differently, leaving the lookup authorized under one identity and the
    posting recorded under another.
    """
    posted = reward(500)
    harness.service.post(envelope(key="a", version=0), posted)
    harness.authorization.asked.clear()

    harness.service.compensate(
        envelope(key="b", version=1),
        transaction_id=posted.id,
        reason="Undo",
        occurred_at=NOW,
    )

    assert harness.authorization.asked == [COUNCIL_USER]
    # …and the port the caller does not need is not consulted at all.
    assert harness.principals.asked == []


def test_a_principal_correction_resolves_the_principal_port_exactly_once(harness):
    posted = reward(500)
    harness.service.post(service_envelope(key="a", version=0), posted)
    harness.principals.asked.clear()
    harness.authorization.asked.clear()

    harness.service.compensate(
        service_envelope(key="b", version=1),
        transaction_id=posted.id,
        reason="Undo",
        occurred_at=NOW,
    )

    assert harness.principals.asked == [POSTING_PRINCIPAL]
    assert harness.authorization.asked == []


def test_a_refused_correction_resolves_authority_once_and_stops(harness):
    """The refusing path resolves once too — it does not retry the question."""
    posted = reward(500)
    harness.service.post(envelope(key="a", version=0), posted)
    harness.authorization.asked.clear()

    _compensation_refusal(
        harness.service, envelope(key="b", version=1, user=ORDINARY_USER), posted.id
    )

    assert harness.authorization.asked == [ORDINARY_USER]


def test_an_authorized_correction_still_appends_and_records_the_resolved_actor(
    harness,
):
    posted = reward(500)
    harness.service.post(envelope(key="a", version=0), posted)

    receipt = harness.service.compensate(
        envelope(key="b", version=1),
        transaction_id=posted.id,
        reason="Reward applied twice",
        occurred_at=NOW + timedelta(days=1),
    )

    correction = harness.transactions()[1]
    assert correction.compensates == posted.id
    assert receipt.facts["compensates"] == str(posted.id)
    assert harness.book.balance(WALLET, ResourceKind.MONEY) == Money(0)

    event = harness.store.audit_events[-1]
    assert event.actor_capability is ActorCapability.GUILD_COUNCIL
    assert event.actor_discord_user_id == COUNCIL_USER
    assert event.payload["service_principal_id"] is None


def test_a_principal_correction_is_attributed_to_the_resolved_principal(harness):
    """The resolved attribution, carried through — not the request's own text."""
    posted = reward(500)
    harness.service.post(service_envelope(key="a", version=0), posted)

    harness.service.compensate(
        service_envelope(key="b", version=1),
        transaction_id=posted.id,
        reason="Undo",
        occurred_at=NOW,
    )

    event = harness.store.audit_events[-1]
    assert event.actor_capability is ActorCapability.SERVICE_PRINCIPAL
    assert event.actor_discord_user_id is None
    assert event.payload["service_principal_id"] == POSTING_PRINCIPAL
    assert len(harness.transactions()) == 2


def test_a_rebuilt_true_retry_of_a_correction_creates_no_second_effect(harness):
    """A retry regenerates the compensating transaction and its attempt id.

    Neither is command-defining, so the second attempt is answered from the
    stored receipt: one correction, one receipt, one audit row.
    """
    posted = reward(500)
    harness.service.post(envelope(key="a", version=0), posted)
    first = harness.service.compensate(
        envelope(key="b", version=1),
        transaction_id=posted.id,
        reason="Undo",
        occurred_at=NOW,
    )

    second = harness.service.compensate(
        envelope(key="b", version=1, correlation_id=uuid4()),
        transaction_id=posted.id,
        reason="Undo",
        occurred_at=NOW,
    )

    assert second.duplicate is True
    assert second.facts == first.facts
    assert second.correlation_id == first.correlation_id
    assert len(harness.transactions()) == 2
    assert len(harness.receipts()) == 2
    assert harness.audit_actions() == [TRANSACTION_POSTED, TRANSACTION_POSTED]


def test_the_service_offers_no_public_way_to_supply_an_attribution(harness):
    """P4-R4 asked for a private path, not a second public entry point.

    An `_Attribution` is the answer of a port. A public method that accepted one
    would let an adapter present a conclusion where the design requires it to
    present an identity — defect P4-R2 in a new place.
    """
    import inspect

    public = [
        name
        for name, member in inspect.getmembers(
            LedgerCommandService, inspect.isfunction
        )
        if not name.startswith("_")
    ]

    assert sorted(public) == ["compensate", "post"]
    for name in public:
        parameters = inspect.signature(
            getattr(LedgerCommandService, name)
        ).parameters
        assert "attribution" not in parameters, name


# --- P4-R5: one correlation identity per attempt ------------------------------


def test_a_mismatched_correlation_is_refused_before_a_unit_of_work_opens(harness):
    """The fence, and where it sits.

    `harness.inner.units` counts the units of work the service asked its factory
    for. Nothing may be opened: a mismatch is decided from the two objects in
    hand, before the expected version is read, before the digest is computed and
    before any repository is reached.
    """
    opened = len(harness.inner.units)

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(envelope(key="k"), reward(500, correlation_id=uuid4()))

    assert refusal.value.code == "correlation_mismatch"
    assert len(harness.inner.units) == opened
    harness.assert_nothing_happened()


def test_the_correlation_refusal_is_declared_and_names_neither_identity(harness):
    """Typed, declared and fixed prose — the rule every refusal here follows."""
    assert "correlation_mismatch" in REFUSAL_CODES

    request = envelope(key="k")
    mismatched = reward(500, correlation_id=uuid4())

    with pytest.raises(LedgerRefused) as refusal:
        harness.service.post(request, mismatched)

    message = str(refusal.value)
    assert str(request.correlation_id) not in message
    assert str(mismatched.correlation_id) not in message


def test_a_mismatch_is_refused_whichever_side_carries_the_stray_identity(harness):
    """Refused, not silently resolved in favour of one of the two.

    Preferring the envelope's would discard the id the domain object was built
    with; preferring the transaction's would make the caller's correlation a
    suggestion. Both directions are the same refusal.
    """
    codes = set()
    for request, transaction in (
        (envelope(key="a"), reward(500, correlation_id=uuid4())),
        (envelope(key="b", correlation_id=uuid4()), reward(500)),
    ):
        with pytest.raises(LedgerRefused) as refusal:
            harness.service.post(request, transaction)
        codes.add(refusal.value.code)

    assert codes == {"correlation_mismatch"}
    harness.assert_nothing_happened()


def test_an_accepted_command_records_one_correlation_id_in_all_three_places(harness):
    """Ledger history, the stored receipt and the audit row, from one attempt."""
    attempt = uuid4()
    request = envelope(key="k", correlation_id=attempt)

    receipt = harness.service.post(request, reward(500, correlation_id=attempt))

    assert receipt.correlation_id == attempt
    assert harness.transactions()[0].correlation_id == attempt
    assert harness.store.audit_events[0].correlation_id == attempt
    assert harness.receipts()[0].response["correlation_id"] == str(attempt)


def test_an_accepted_correction_records_one_correlation_id_in_all_three_places(
    harness,
):
    """A compensation builds its transaction from the envelope, so it agrees."""
    posted = reward(500)
    harness.service.post(envelope(key="a", version=0), posted)
    attempt = uuid4()

    receipt = harness.service.compensate(
        envelope(key="b", version=1, correlation_id=attempt),
        transaction_id=posted.id,
        reason="Undo",
        occurred_at=NOW,
    )

    correction = harness.transactions()[1]
    assert attempt != posted.correlation_id
    assert receipt.correlation_id == attempt
    assert correction.correlation_id == attempt
    assert harness.store.audit_events[-1].correlation_id == attempt


def test_a_retry_carrying_new_attempt_metadata_in_both_halves_is_still_a_retry(
    harness,
):
    """Correlation stays attempt metadata: the fence constrains one attempt only.

    The retry regenerates its correlation id on *both* halves — legal, because
    they agree with each other — and is answered from the stored receipt. Ledger
    history and the audit row keep the accepted attempt's id.
    """
    original = uuid4()
    first = harness.service.post(
        envelope(key="k", correlation_id=original),
        reward(500, correlation_id=original),
    )

    retry = uuid4()
    replay = harness.service.post(
        envelope(key="k", correlation_id=retry), reward(500, correlation_id=retry)
    )

    assert replay.duplicate is True
    assert replay.correlation_id == original == first.correlation_id
    assert len(harness.transactions()) == 1
    assert harness.transactions()[0].correlation_id == original
    assert harness.audit_actions() == [TRANSACTION_POSTED]
    assert harness.store.audit_events[0].correlation_id == original


def test_correlation_is_not_in_the_command_defining_digest(harness):
    """Read off the digest itself rather than inferred from retry behaviour.

    A fence added by quietly making correlation command-defining would refuse a
    genuine retry as a conflict. This asserts the digest is unchanged by the id
    while the two halves agree.
    """
    service = harness.service
    left = service._digest(
        envelope(key="k", correlation_id=ATTEMPT),
        reward(500, correlation_id=ATTEMPT),
        expected_version=0,
        attribution=service._attribute(
            CommandCaller(AuditSource.DISCORD, discord_user_id=COUNCIL_USER)
        ),
    )
    other = uuid4()
    right = service._digest(
        envelope(key="k", correlation_id=other),
        reward(500, correlation_id=other),
        expected_version=0,
        attribution=service._attribute(
            CommandCaller(AuditSource.DISCORD, discord_user_id=COUNCIL_USER)
        ),
    )

    assert left == right


# --- the boundary itself ------------------------------------------------------


def test_the_ledger_repository_offers_no_update_or_delete():
    """Append-only as a property of the interface, not a convention."""
    offered = {name for name in dir(LedgerRepository) if not name.startswith("_")}

    assert offered == {"version_of", "balance_of", "append", "get"}


def test_every_ledger_repository_method_has_a_phase_4_consumer():
    """`.agents/AGENTS.md`: no abstraction without a real consumer.

    Read from the service's own source rather than asserted in prose, so a
    method that loses its caller fails this instead of quietly becoming a
    speculative interface.
    """
    import inspect

    import application.ledger as module

    source = inspect.getsource(module)
    for name in ("version_of", "balance_of", "append", "get"):
        assert f".ledger.{name}(" in source, name


def test_the_service_exposes_no_framework_object(harness):
    """No Discord object, web request, A1 range, ORM record or SQL shape."""
    import inspect

    import application.ledger as module

    source = inspect.getsource(module)
    for forbidden in (
        "import discord",
        "sqlalchemy",
        "fastapi",
        "psycopg",
        "gspread",
        "SELECT ",
        "INSERT ",
    ):
        assert forbidden not in source, forbidden


def test_a_uniqueness_conflict_the_service_cannot_resolve_is_not_a_receipt(harness):
    """An unresolvable conflict is refused, never resolved into a duplicate."""
    service = harness.service_over(
        failing_ledger_factory(
            harness.book, harness.inner, _ConflictingLedgerUnitOfWork
        )
    )

    with pytest.raises(LedgerRefused) as refusal:
        service.post(envelope(), reward())

    assert refusal.value.code == "concurrent_posting"
    harness.assert_nothing_happened()


def test_post_refuses_anything_that_is_not_a_ledger_transaction(harness):
    """The balance invariant is enforced in the domain; entries are not assembled
    here."""
    with pytest.raises(TypeError):
        harness.service.post(
            envelope(), [LedgerEntry(WALLET, Money(1)), LedgerEntry(INCOME, Money(-1))]
        )
