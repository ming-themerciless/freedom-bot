"""TC-AUTH-13: OD-44's durable one-way completion binding.

SM-01 requires that no web session exist unless it is the unique product of
exactly one live, browser-bound OAuth transaction that was correctly consumed.
Before OD-44 the platform obtained that outcome from the *order of the statements
in R-04*: `OAuthLoginService.complete()` received no transaction id at all and
could not establish from durable state that the completion it was performing
corresponded to any transaction. Route ordering made the forbidden state
unlikely; nothing made it impossible.

These tests exist to make the difference visible. They are deliberately weighted
towards the paths a route cannot reach:

- **the direct internal call** — `complete()` invoked with an unknown,
  unconsumed, already-claimed or mismatched id, with a perfectly valid provider
  identity in hand, refuses. That is the case an API comment cannot cover and the
  case a future second completion path would take;
- **the database with the application bypassed** — raw `INSERT`s prove the check
  constraint and the unique index refuse the forbidden rows whatever the
  application believes;
- **two real connections** — the claim's serialization is proved by racing it,
  not by reading the statement;
- **injected failure at each step** — every write inside the completion
  transaction is made to fail in turn, and each one must roll the *whole*
  completion back rather than leave a session behind a half-written login.

No test here sleeps. The concurrency evidence uses a `threading.Barrier`
rendezvous and PostgreSQL's own row lock, so it proves an ordering rather than
observing one that happened to occur.
"""
from __future__ import annotations

import threading
from datetime import timedelta
from hashlib import sha256
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, select, text

from adapters.database.tables import (
    audit_events,
    external_identities,
    oauth_token_grants,
    oauth_transactions,
    platform_accounts,
    sessions,
)
from adapters.web.repositories import OAuthTransactionRepository
from application.web.capabilities import AuthMethod
from application.web.crypto import token_hash
from application.web.errors import AuthenticationFailure
from application.web.providers import ProviderResultMismatch, VerifiedCompletion
from tests.web.conftest import (
    make_account,
    seed_oauth_transaction,
    utcnow,
)

pytestmark = pytest.mark.database


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _provider_result(provider) -> VerifiedCompletion:
    """A real verified completion, as the route would hold it.

    Obtained from the double's own methods rather than constructed, so a test
    that calls `complete()` directly is refused for the reason under test and not
    because it built an identity the service would have rejected anyway.
    """
    tokens = await provider.exchange(code="the-code", code_verifier="the-verifier")
    identity = await provider.verify(tokens)
    return VerifiedCompletion(identity=identity, tokens=tokens)


def _complete(composition, connection, *, transaction_id, completion):
    return composition.services(connection).oauth.complete(
        transaction_id=transaction_id,
        completion=completion,
        return_path="/v1/characters",
        now=utcnow(),
        correlation_id=uuid4(),
        client_ip_hash=None,
        user_agent_digest=None,
    )


def _insert_session(
    connection,
    *,
    account_id: UUID,
    auth_method: str,
    oauth_transaction_id: UUID | None,
    rotated_from: UUID | None = None,
) -> UUID:
    """Insert a session row directly, with the application entirely out of the way.

    Used only by the constraint tests. A test that reached the database through
    the service would prove what the service does; these prove what the database
    refuses when the service is not there to be trusted.
    """
    session_id = uuid4()
    now = utcnow()
    connection.execute(
        text(
            """
            INSERT INTO sessions (
                id, token_hash, platform_account_id, auth_method,
                created_at, last_seen_at, idle_expires_at, absolute_expires_at,
                privilege_fingerprint, rotated_from_session_id, oauth_transaction_id
            ) VALUES (
                :id, :token_hash, :account, :auth_method,
                :now, :now, :idle, :absolute,
                :fingerprint, :rotated_from, :transaction
            )
            """
        ),
        {
            "id": session_id,
            "token_hash": sha256(session_id.bytes).digest(),
            "account": account_id,
            "auth_method": auth_method,
            "now": now,
            "idle": now + timedelta(minutes=60),
            "absolute": now + timedelta(hours=12),
            "fingerprint": sha256(b"fingerprint").digest(),
            "rotated_from": rotated_from,
            "transaction": oauth_transaction_id,
        },
    )
    return session_id


def _counts(connection) -> dict[str, int]:
    """The three absences every refusal in this module has to prove."""
    return {
        "sessions": connection.execute(
            select(text("count(*)")).select_from(sessions)
        ).scalar_one(),
        "token_grants": connection.execute(
            select(text("count(*)")).select_from(oauth_token_grants)
        ).scalar_one(),
        "successes": connection.execute(
            select(text("count(*)")).where(
                audit_events.c.action == "auth.login.succeeded"
            ).select_from(audit_events)
        ).scalar_one(),
    }


def _every_effect_count(connection) -> dict[str, int]:
    """Everything a completion writes, counted — the full absence, not a sample.

    A refused completion must leave *none* of it. `_counts` covers the three that
    every refusal in this module asserts; this adds the account, the external
    identity and the membership projection, which the provider-binding cases
    (TC-AUTH-15) have to prove absent as well.
    """
    counts = _counts(connection)
    counts["accounts"] = connection.execute(
        select(text("count(*)")).select_from(platform_accounts)
    ).scalar_one()
    counts["identities"] = connection.execute(
        select(text("count(*)")).select_from(external_identities)
    ).scalar_one()
    counts["memberships"] = connection.execute(
        text("SELECT count(*) FROM discord_guild_memberships")
    ).scalar_one()
    return counts


NOTHING_HAPPENED = {
    "sessions": 0,
    "token_grants": 0,
    "successes": 0,
    "accounts": 0,
    "identities": 0,
    "memberships": 0,
}


class _FailingAt:
    """A delegate with exactly one method replaced by a raise.

    Narrower than a mock on purpose: every other call goes to the real
    repository, so the transaction under test does the real work right up to the
    step being faulted. A double that faked the whole collaborator would prove
    the rollback of a transaction that had nothing in it.
    """

    def __init__(self, delegate, method: str, error: Exception) -> None:
        self._delegate = delegate
        self._method = method
        self._error = error

    def __getattr__(self, name: str):
        if name == self.__dict__["_method"]:

            def raise_it(*args, **kwargs):
                raise self.__dict__["_error"]

            return raise_it
        return getattr(self.__dict__["_delegate"], name)


async def _start(client):
    response = await client.get("/v1/auth/discord/start")
    assert response.status_code == 303
    return response


def _transaction_cookie(response) -> str:
    for cookie in response.headers.get_list("set-cookie"):
        if cookie.startswith("__Host-fb_login_txn="):
            return cookie.split("=", 1)[1].split(";", 1)[0]
    raise AssertionError("the start route set no login-transaction cookie")


# ---------------------------------------------------------------------------
# TC-AUTH-13a — the bound success
# ---------------------------------------------------------------------------


async def test_one_consumed_transaction_produces_one_bound_session_and_one_success_audit(
    client, provider, migrated_database
):
    """TC-AUTH-13a. The whole point, at the HTTP boundary.

    The session names the transaction, the transaction records the claim, and
    both happened in the transaction that also wrote the success audit.
    """
    start = await _start(client)
    transaction_id = UUID(_transaction_cookie(start))
    state = provider.authorization_calls[-1][0]

    response = await client.get(
        "/auth/discord/callback",
        params={"state": state, "code": "the-code"},
        cookies={"__Host-fb_login_txn": str(transaction_id)},
    )
    assert response.status_code == 303

    with migrated_database.connect() as connection:
        session_rows = connection.execute(select(sessions)).mappings().all()
        transaction = connection.execute(
            select(oauth_transactions).where(oauth_transactions.c.id == transaction_id)
        ).mappings().one()
        successes = connection.execute(
            select(text("count(*)")).where(
                audit_events.c.action == "auth.login.succeeded"
            ).select_from(audit_events)
        ).scalar_one()

    assert len(session_rows) == 1
    assert session_rows[0]["auth_method"] == "discord_oauth"
    assert session_rows[0]["oauth_transaction_id"] == transaction_id
    assert transaction["consumed_at"] is not None
    assert transaction["completion_claimed_at"] is not None
    assert successes == 1


# ---------------------------------------------------------------------------
# TC-AUTH-13b — the direct internal call, which is the finding
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "state",
    ["unknown", "unconsumed", "already_claimed"],
)
async def test_a_direct_completion_without_a_claimable_transaction_is_refused(
    migrated_database, composition, provider, state
):
    """TC-AUTH-13b. The case route ordering cannot cover, and an API comment is not.

    Each parameter is a caller holding a genuinely verified Discord identity and
    real provider tokens — everything the happy path has except a transaction
    that can still be claimed. All three must leave no session, no token grant
    and no success audit.
    """
    completion = await _provider_result(provider)

    with migrated_database.begin() as connection:
        if state == "unknown":
            transaction_id = uuid4()
        elif state == "unconsumed":
            transaction_id = seed_oauth_transaction(connection, consumed=False)
        else:
            transaction_id = seed_oauth_transaction(connection, claimed=True)

    with pytest.raises(AuthenticationFailure) as refusal:
        with migrated_database.begin() as connection:
            _complete(
                composition,
                connection,
                transaction_id=transaction_id,
                completion=completion,
            )

    assert refusal.value.code == "transaction_unknown"
    assert refusal.value.audit is not None
    assert refusal.value.audit.payload == {"reason": "completion_not_claimable"}

    with migrated_database.connect() as connection:
        assert _counts(connection) == {
            "sessions": 0,
            "token_grants": 0,
            "successes": 0,
        }
        # The account is not created either: the claim is the *first* statement,
        # so a refused completion does not leave a half-resolved identity behind.
        assert (
            connection.execute(
                select(text("count(*)")).select_from(platform_accounts)
            ).scalar_one()
            == 0
        )


async def test_a_completion_naming_a_different_transaction_than_the_one_consumed_is_refused(
    client, migrated_database, composition, provider
):
    """TC-AUTH-13b. A *mismatched* id, not merely an absent one.

    The caller consumes one transaction — so a verifier really was recovered and
    a provider exchange really could have happened — and then completes naming a
    second, unconsumed transaction. The claim refuses it, because the claim is
    about *this* row rather than about the existence of some consumed row.
    """
    completion = await _provider_result(provider)
    state = "a-state-for-the-consumed-one"

    with migrated_database.begin() as connection:
        services = composition.services(connection)
        consumed_id = uuid4()
        services.transactions.create(
            state_hash=token_hash(state),
            verifier=composition.envelope.seal(b"v", aad=b"aad"),
            return_path="/v1/characters",
            provider_key="discord",
            expires_at=utcnow() + timedelta(minutes=10),
            client_ip_hash=None,
            transaction_id=consumed_id,
        )
        other_id = seed_oauth_transaction(connection, consumed=False)

    with migrated_database.begin() as connection:
        assert composition.services(connection).transactions.consume(
            transaction_id=consumed_id, state_hash=token_hash(state), now=utcnow()
        ) is not None

    with pytest.raises(AuthenticationFailure):
        with migrated_database.begin() as connection:
            _complete(
                composition,
                connection,
                transaction_id=other_id,
                completion=completion,
            )

    with migrated_database.connect() as connection:
        assert _counts(connection)["sessions"] == 0
        claims = connection.execute(
            select(oauth_transactions.c.id).where(
                oauth_transactions.c.completion_claimed_at.isnot(None)
            )
        ).scalars().all()
    assert claims == [], "no row may be claimed by a refused completion"


# ---------------------------------------------------------------------------
# TC-AUTH-13c — replay and duplicate delivery
# ---------------------------------------------------------------------------


async def test_a_replayed_callback_creates_no_second_session_or_success_audit(
    client, provider, migrated_database
):
    """TC-AUTH-13c. The browser delivers the same callback twice.

    The second delivery is refused at `consume()`, as it always was. The value of
    asserting it again here is the *count*: one session and one success audit
    after two deliveries, with the transaction claimed exactly once.
    """
    start = await _start(client)
    transaction_id = UUID(_transaction_cookie(start))
    state = provider.authorization_calls[-1][0]

    first = await client.get(
        "/auth/discord/callback",
        params={"state": state, "code": "the-code"},
        cookies={"__Host-fb_login_txn": str(transaction_id)},
    )
    assert first.status_code == 303
    second = await client.get(
        "/auth/discord/callback",
        params={"state": state, "code": "the-code"},
        cookies={"__Host-fb_login_txn": str(transaction_id)},
    )

    assert second.status_code == 303
    assert "failure=transaction_unknown" in second.headers["location"]
    with migrated_database.connect() as connection:
        counts = _counts(connection)
        claimed_at = connection.execute(
            select(oauth_transactions.c.completion_claimed_at).where(
                oauth_transactions.c.id == transaction_id
            )
        ).scalar_one()
    assert counts["sessions"] == 1
    assert counts["successes"] == 1
    assert claimed_at is not None


async def test_a_second_completion_after_a_successful_login_is_refused(
    client, provider, migrated_database, composition
):
    """TC-AUTH-13c. The claim is a *second* serialization point, after the provider.

    `consume()` already refuses the replayed callback, so this drives the second
    completion the way a future refactor or an internal caller would — directly,
    past the consumption that would have stopped it.
    """
    start = await _start(client)
    transaction_id = UUID(_transaction_cookie(start))
    state = provider.authorization_calls[-1][0]
    response = await client.get(
        "/auth/discord/callback",
        params={"state": state, "code": "the-code"},
        cookies={"__Host-fb_login_txn": str(transaction_id)},
    )
    assert response.status_code == 303

    completion = await _provider_result(provider)
    with pytest.raises(AuthenticationFailure):
        with migrated_database.begin() as connection:
            _complete(
                composition,
                connection,
                transaction_id=transaction_id,
                completion=completion,
            )

    with migrated_database.connect() as connection:
        counts = _counts(connection)
    assert counts["sessions"] == 1
    assert counts["successes"] == 1


# ---------------------------------------------------------------------------
# TC-AUTH-13d — concurrency, against real PostgreSQL
# ---------------------------------------------------------------------------


def test_two_concurrent_claims_produce_one_winner_and_one_refusal(
    database_url, migrated_database, composition
):
    """TC-AUTH-13d. Two connections, a barrier rendezvous, and no sleep anywhere.

    Under `READ COMMITTED` the losing `UPDATE` blocks on the winner's row lock,
    re-evaluates `completion_claimed_at IS NULL` when the lock is released, and
    matches zero rows. The barrier is what makes both statements genuinely
    in flight at once; the outcome is decided by PostgreSQL rather than by which
    thread the scheduler happened to run first.
    """
    with migrated_database.begin() as connection:
        transaction_id = seed_oauth_transaction(connection)

    other = create_engine(database_url)
    barrier = threading.Barrier(2)
    outcomes: list[bool] = []
    lock = threading.Lock()

    def claim(engine):
        with engine.begin() as connection:
            barrier.wait(timeout=30)
            taken = OAuthTransactionRepository(connection).claim_completion(
                transaction_id=transaction_id, provider_key="discord", now=utcnow()
            )
        with lock:
            outcomes.append(taken)

    try:
        threads = [
            threading.Thread(target=claim, args=(migrated_database,)),
            threading.Thread(target=claim, args=(other,)),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30)
            assert not thread.is_alive(), "a claim did not finish; it is deadlocked"
    finally:
        other.dispose()

    assert sorted(outcomes) == [False, True], "exactly one completion may be claimed"

    with migrated_database.connect() as connection:
        claimed = connection.execute(
            select(oauth_transactions.c.completion_claimed_at).where(
                oauth_transactions.c.id == transaction_id
            )
        ).scalar_one()
    assert claimed is not None


async def test_two_concurrent_completions_produce_one_session_and_one_refusal(
    database_url, migrated_database, composition, provider
):
    """TC-AUTH-13d. The whole completion raced, not only its first statement.

    The loser never reaches account resolution, membership or token storage: the
    claim is the first statement in the transaction, so a refused completion is
    refused before it writes anything. That ordering is why this test can assert
    a single account as well as a single session.

    The identity is obtained before the threads start. The database work is
    synchronous and runs in plain threads, exactly as `run_in_threadpool` runs it
    in production; the event loop is not involved in the race.
    """
    completion = await _provider_result(provider)

    with migrated_database.begin() as connection:
        transaction_id = seed_oauth_transaction(connection)

    other = create_engine(database_url)
    barrier = threading.Barrier(2)
    results: list[str] = []
    lock = threading.Lock()

    def complete(engine):
        try:
            with engine.begin() as connection:
                barrier.wait(timeout=30)
                _complete(
                    composition,
                    connection,
                    transaction_id=transaction_id,
                    completion=completion,
                )
            outcome = "completed"
        except AuthenticationFailure:
            outcome = "refused"
        with lock:
            results.append(outcome)

    try:
        threads = [
            threading.Thread(target=complete, args=(migrated_database,)),
            threading.Thread(target=complete, args=(other,)),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30)
            assert not thread.is_alive(), "a completion did not finish"
    finally:
        other.dispose()

    assert sorted(results) == ["completed", "refused"]

    with migrated_database.connect() as connection:
        counts = _counts(connection)
        accounts = connection.execute(
            select(text("count(*)")).select_from(platform_accounts)
        ).scalar_one()
    assert counts["sessions"] == 1
    assert counts["successes"] == 1
    assert accounts == 1


# ---------------------------------------------------------------------------
# TC-AUTH-13e — the database, with the application bypassed entirely
# ---------------------------------------------------------------------------


def test_the_database_refuses_a_discord_oauth_session_with_no_transaction(
    migrated_database,
):
    """TC-AUTH-13e. SM-01's forbidden state, refused without any application code."""
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError, match="ck_sessions_oauth_transaction_binding"):
        with migrated_database.begin() as connection:
            account_id = make_account(connection)
            _insert_session(
                connection,
                account_id=account_id,
                auth_method="discord_oauth",
                oauth_transaction_id=None,
            )


@pytest.mark.parametrize("auth_method", ["webauthn", "recovery_grant"])
def test_the_database_refuses_a_break_glass_session_that_names_a_transaction(
    migrated_database, auth_method
):
    """TC-AUTH-13e. The constraint is an equivalence, not an implication.

    A break-glass session carrying an OAuth transaction id would be a session
    claiming a provenance it does not have — and would consume a transaction's
    one binding slot, so a later genuine completion for that row would be refused
    by the unique index. Both directions are refused.
    """
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError, match="ck_sessions_oauth_transaction_binding"):
        with migrated_database.begin() as connection:
            account_id = make_account(connection)
            transaction_id = seed_oauth_transaction(connection)
            _insert_session(
                connection,
                account_id=account_id,
                auth_method=auth_method,
                oauth_transaction_id=transaction_id,
            )


def test_the_database_refuses_a_second_completion_session_for_one_transaction(
    migrated_database,
):
    """TC-AUTH-13e. The unique index, independent of the claim and of the route."""
    from sqlalchemy.exc import IntegrityError

    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        transaction_id = seed_oauth_transaction(connection, claimed=True)
        _insert_session(
            connection,
            account_id=account_id,
            auth_method="discord_oauth",
            oauth_transaction_id=transaction_id,
        )

    with pytest.raises(IntegrityError, match="uq_sessions_oauth_transaction_id"):
        with migrated_database.begin() as connection:
            _insert_session(
                connection,
                account_id=account_id,
                auth_method="discord_oauth",
                oauth_transaction_id=transaction_id,
            )


def test_the_database_refuses_a_session_naming_a_transaction_that_does_not_exist(
    migrated_database,
):
    """TC-AUTH-13e. The foreign key: a binding must name a row, not a plausible UUID."""
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(
        IntegrityError, match="fk_sessions_oauth_transaction_id_oauth_transactions"
    ):
        with migrated_database.begin() as connection:
            account_id = make_account(connection)
            _insert_session(
                connection,
                account_id=account_id,
                auth_method="discord_oauth",
                oauth_transaction_id=uuid4(),
            )


def test_the_database_refuses_a_completion_claim_on_a_transaction_never_consumed(
    migrated_database,
):
    """TC-AUTH-13e. The claim statement requires it; so does the table."""
    from sqlalchemy.exc import IntegrityError

    with migrated_database.begin() as connection:
        transaction_id = seed_oauth_transaction(connection, consumed=False)

    with pytest.raises(
        IntegrityError, match="ck_oauth_transactions_completion_requires_consumption"
    ):
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    "UPDATE oauth_transactions SET completion_claimed_at = now() "
                    "WHERE id = :id"
                ),
                {"id": transaction_id},
            )


def test_the_expiry_reaper_skips_a_transaction_a_session_still_names(
    migrated_database, composition
):
    """TC-AUTH-13e. N-04's purge keeps working, and `RESTRICT` stays the backstop.

    A session outlives its transaction by design, so the reaper meets referenced
    rows in ordinary operation rather than only in a contrived case. It skips
    them; it does not fail, because a cleanup that fails on a normal Tuesday is a
    cleanup that stops running. The unreferenced expired row beside it is still
    deleted, which is what proves the predicate is a skip and not a no-op.
    """
    from sqlalchemy.exc import IntegrityError

    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        bound_id = seed_oauth_transaction(connection, claimed=True)
        unbound_id = seed_oauth_transaction(connection)
        _insert_session(
            connection,
            account_id=account_id,
            auth_method="discord_oauth",
            oauth_transaction_id=bound_id,
        )

    with migrated_database.begin() as connection:
        deleted = composition.services(connection).transactions.purge_expired(
            before=utcnow() + timedelta(days=365)
        )
    assert deleted == 1

    with migrated_database.connect() as connection:
        remaining = connection.execute(
            select(oauth_transactions.c.id)
        ).scalars().all()
    assert remaining == [bound_id]

    # And a deletion written without that predicate is refused by the database,
    # so the skip above is a courtesy rather than the guarantee.
    with pytest.raises(IntegrityError, match="fk_sessions_oauth_transaction_id"):
        with migrated_database.begin() as connection:
            connection.execute(
                text("DELETE FROM oauth_transactions WHERE id = :id"), {"id": bound_id}
            )


# ---------------------------------------------------------------------------
# TC-AUTH-13f — provider failure, process death and the restart seam
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fault",
    ["unavailable_at_exchange", "unavailable_at_verify", "refuse_exchange", "refuse_verify"],
)
async def test_a_provider_failure_after_consumption_leaves_a_consumed_unclaimed_transaction(
    client, provider, migrated_database, fault
):
    """TC-AUTH-13f. SM-01's provider-outage row, now with the claim as evidence.

    The transaction is spent — it cannot be replayed — and it is **not** claimed,
    so no session exists and none can be produced from it through the route. The
    user signs in again, which is the ruled behaviour.
    """
    start = await _start(client)
    transaction_id = UUID(_transaction_cookie(start))
    state = provider.authorization_calls[-1][0]
    setattr(provider, fault, True)

    response = await client.get(
        "/auth/discord/callback",
        params={"state": state, "code": "the-code"},
        cookies={"__Host-fb_login_txn": str(transaction_id)},
    )

    assert response.status_code == 303
    assert "failure=provider_error" in response.headers["location"]
    with migrated_database.connect() as connection:
        row = connection.execute(
            select(oauth_transactions).where(oauth_transactions.c.id == transaction_id)
        ).mappings().one()
        counts = _counts(connection)
    assert row["consumed_at"] is not None
    assert row["completion_claimed_at"] is None
    assert row["pkce_verifier_ciphertext"] is None, "the verifier is gone either way"
    assert counts == {"sessions": 0, "token_grants": 0, "successes": 0}


async def test_the_process_death_seam_leaves_no_session_and_no_replayable_transaction(
    client, provider, migrated_database, composition
):
    """TC-AUTH-13f. Process death between the consumption and the completion.

    Automated as far as it can be without killing an uncontrolled process: the
    consumption is committed and the completion simply never happens, which is
    the durable state a killed worker leaves behind. What a restart must find is
    a spent, unclaimed transaction and no session — and a second callback for it
    refused at the consumption, not at the claim.
    """
    start = await _start(client)
    transaction_id = UUID(_transaction_cookie(start))
    state = provider.authorization_calls[-1][0]

    with migrated_database.begin() as connection:
        recovered = composition.services(connection).transactions.consume(
            transaction_id=transaction_id, state_hash=token_hash(state), now=utcnow()
        )
    assert recovered is not None  # the worker got this far, then died

    with migrated_database.connect() as connection:
        row = connection.execute(
            select(oauth_transactions).where(oauth_transactions.c.id == transaction_id)
        ).mappings().one()
        assert _counts(connection) == {"sessions": 0, "token_grants": 0, "successes": 0}
    assert row["consumed_at"] is not None
    assert row["completion_claimed_at"] is None

    # The restart: the browser retries the callback it never saw answered.
    response = await client.get(
        "/auth/discord/callback",
        params={"state": state, "code": "the-code"},
        cookies={"__Host-fb_login_txn": str(transaction_id)},
    )
    assert response.status_code == 303
    assert "failure=transaction_unknown" in response.headers["location"]
    with migrated_database.connect() as connection:
        assert _counts(connection) == {"sessions": 0, "token_grants": 0, "successes": 0}


# ---------------------------------------------------------------------------
# TC-AUTH-13g — every write inside the completion transaction, faulted in turn
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("collaborator", "method"),
    [
        ("_transactions", "claim_completion"),
        ("_accounts", "create_with_identity"),
        ("_membership", "record"),
        ("_tokens", "replace"),
        ("_sessions", "begin"),
        ("_audit", "record"),
    ],
)
async def test_a_failure_at_any_step_rolls_the_whole_completion_back(
    migrated_database, composition, provider, collaborator, method
):
    """TC-AUTH-13g. Six faults, one outcome: nothing at all, and no false success.

    The claim shares the transaction with the account, the membership projection,
    the token grant, the session and the success audit. If any of them cannot be
    written, none of them is — and in particular the claim is released, so the
    transaction is left consumed-and-unclaimed rather than spent on a login that
    did not happen.
    """
    completion = await _provider_result(provider)
    with migrated_database.begin() as connection:
        transaction_id = seed_oauth_transaction(connection)

    boom = RuntimeError("injected failure")
    with pytest.raises(RuntimeError, match="injected failure"):
        with migrated_database.begin() as connection:
            service = composition.services(connection).oauth
            setattr(
                service,
                collaborator,
                _FailingAt(getattr(service, collaborator), method, boom),
            )
            service.complete(
                transaction_id=transaction_id,
                completion=completion,
                return_path="/v1/characters",
                now=utcnow(),
                correlation_id=uuid4(),
                client_ip_hash=None,
                user_agent_digest=None,
            )

    with migrated_database.connect() as connection:
        assert _counts(connection) == {"sessions": 0, "token_grants": 0, "successes": 0}
        claimed = connection.execute(
            select(oauth_transactions.c.completion_claimed_at).where(
                oauth_transactions.c.id == transaction_id
            )
        ).scalar_one()
        accounts = connection.execute(
            select(text("count(*)")).select_from(platform_accounts)
        ).scalar_one()
    assert claimed is None, "a rolled-back completion must release its claim"
    assert accounts == 0


async def test_a_commit_failure_after_a_complete_call_leaves_no_session_and_no_claim(
    migrated_database, composition, provider
):
    """TC-AUTH-13g. The commit itself, rather than a statement inside it.

    `complete()` returning is not a login. The caller's transaction is what makes
    it one, and a caller that fails between the last statement and the commit
    must leave the same nothing behind as a caller that failed at the first.
    """
    completion = await _provider_result(provider)
    with migrated_database.begin() as connection:
        transaction_id = seed_oauth_transaction(connection)

    with pytest.raises(RuntimeError, match="the worker died before COMMIT"):
        with migrated_database.begin() as connection:
            completed = _complete(
                composition,
                connection,
                transaction_id=transaction_id,
                completion=completion,
            )
            assert completed.session.session_id is not None
            raise RuntimeError("the worker died before COMMIT")

    with migrated_database.connect() as connection:
        assert _counts(connection) == {"sessions": 0, "token_grants": 0, "successes": 0}
        claimed = connection.execute(
            select(oauth_transactions.c.completion_claimed_at).where(
                oauth_transactions.c.id == transaction_id
            )
        ).scalar_one()
    assert claimed is None


# ---------------------------------------------------------------------------
# TC-AUTH-13h — what the binding must not disturb
# ---------------------------------------------------------------------------


def test_break_glass_sessions_are_created_exactly_as_before(
    migrated_database, composition
):
    """TC-AUTH-13h. SM-03's two paths carry no transaction and need none.

    Asserted through `SessionService.begin()` rather than through the routes
    because the routes are covered elsewhere; what is new here is only that a
    session with `oauth_transaction_id IS NULL` is still insertable for these two
    methods, which the check constraint has to permit.
    """
    from application.audit import ActorCapability
    from application.web.capabilities import (
        AdministratorScope,
        WebAuthorizationContext,
    )

    for auth_method in (AuthMethod.WEBAUTHN, AuthMethod.RECOVERY_GRANT):
        with migrated_database.begin() as connection:
            # Not `protected=True`: only one protected administrator may exist
            # (`uq_platform_accounts_one_protected_admin`), and this test is about
            # the binding constraint rather than about that one.
            account_id = make_account(connection)
            issued = composition.services(connection).session_service.begin(
                context=WebAuthorizationContext(
                    account_id=account_id,
                    auth_method=auth_method,
                    capabilities=frozenset(
                        {ActorCapability.PLATFORM_ADMINISTRATOR}
                    ),
                    administrator_scope=AdministratorScope.EMERGENCY_CONTINUITY,
                    membership=None,
                ),
                now=utcnow(),
                correlation_id=uuid4(),
            )
        with migrated_database.connect() as connection:
            row = connection.execute(
                select(sessions).where(sessions.c.id == issued.session_id)
            ).mappings().one()
        assert row["oauth_transaction_id"] is None
        assert row["auth_method"] == auth_method.value


def test_rotation_carries_the_binding_forward_without_a_second_claim(
    migrated_database, composition
):
    """TC-AUTH-13h. N-08 still rotates a Discord OAuth session.

    A rotated session is the same login, so it names the same transaction and
    takes no second claim. The unique index is scoped to non-rotated rows exactly
    so this chain can exist; without that predicate the check constraint would
    demand a transaction id the unique constraint would then refuse, and N-08
    would silently stop working for the platform's main authentication method.
    """
    from application.audit import ActorCapability
    from application.web.capabilities import (
        AdministratorScope,
        MembershipProjection,
        WebAuthorizationContext,
    )
    from tests.web_fixtures import TEST_GUILD_ID

    def context(account_id, *capabilities):
        return WebAuthorizationContext(
            account_id=account_id,
            auth_method=AuthMethod.DISCORD_OAUTH,
            capabilities=frozenset(capabilities),
            administrator_scope=AdministratorScope.FULL,
            membership=MembershipProjection(
                guild_id=TEST_GUILD_ID,
                is_member=True,
                role_ids=frozenset(),
                observed_at=utcnow(),
            ),
        )

    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        transaction_id = seed_oauth_transaction(connection, claimed=True)
        original = composition.services(connection).session_service.begin(
            context=context(account_id, ActorCapability.GUILD_MEMBER),
            now=utcnow(),
            correlation_id=uuid4(),
            oauth_transaction_id=transaction_id,
        )

    with migrated_database.begin() as connection:
        services = composition.services(connection)
        record = services.session_service.resolve(original.token, now=utcnow())
        assert record.oauth_transaction_id == transaction_id
        rotated = services.session_service.rotate_if_privileges_changed(
            record=record,
            context=context(
                account_id,
                ActorCapability.GUILD_MEMBER,
                ActorCapability.GUILD_COUNCIL,
            ),
            now=utcnow(),
            correlation_id=uuid4(),
        )
    assert rotated is not None

    with migrated_database.connect() as connection:
        row = connection.execute(
            select(sessions).where(sessions.c.id == rotated.session_id)
        ).mappings().one()
        claims = connection.execute(
            select(text("count(*)")).where(
                oauth_transactions.c.completion_claimed_at.isnot(None)
            ).select_from(oauth_transactions)
        ).scalar_one()
    assert row["oauth_transaction_id"] == transaction_id
    assert row["rotated_from_session_id"] == original.session_id
    assert claims == 1, "rotation takes no second claim"


# ---------------------------------------------------------------------------
# TC-AUTH-15 — the completion is bound to the transaction's recorded provider
# ---------------------------------------------------------------------------
#
# The OD-44 re-review's first blocking finding. The claim used to check the
# transaction id, `consumed_at` and `completion_claimed_at`, and `complete()` then
# took the provider from whatever `VerifiedIdentity` it had been handed. Those are
# two independent facts, and nothing required them to agree: an internal caller
# holding another provider's verified identity and tokens could spend a consumed
# Discord transaction, and the "mismatched transaction" test above did not cover
# it because it supplied a second *unconsumed* transaction rather than a second
# *provider*.
#
# The fix has two halves, and these tests exercise both:
#
# - the claim carries `provider_key = :provider_key`, so the refusal is a durable
#   database fact rather than a comparison somebody remembered to write;
# - the expected key is derived from `VerifiedCompletion`, one indivisible result
#   whose identity and tokens were required to name the same provider when it was
#   built — so it cannot be supplied by a caller who has only route ordering to
#   support it.


@pytest.fixture()
def other_provider():
    """A second, differently-keyed provider double.

    Not a second *Discord*: the point is a provider whose `provider_key` is not
    the one the transaction records. `FakeDiscordProvider` already takes its key
    as a field, so this needs no new class — and using the same double keeps the
    verified result it produces exactly as real as the one under test.
    """
    from tests.web_fixtures import FakeDiscordProvider

    return FakeDiscordProvider(
        provider_key="another-provider", subject="700000000000000099"
    )


async def test_a_consumed_transaction_cannot_be_completed_by_another_provider(
    migrated_database, composition, other_provider
):
    """TC-AUTH-15a. The finding itself, at the service boundary.

    The transaction is a real, consumed, unclaimed Discord transaction — exactly
    the state a callback reaches after `consume()` — and the completion offered
    for it is another provider's genuinely verified identity and tokens. It is
    refused, and every effect a completion would have is absent: no account, no
    external identity, no membership projection, no token grant, no session and no
    success audit.
    """
    completion = await _provider_result(other_provider)
    assert completion.provider_key == "another-provider"

    with migrated_database.begin() as connection:
        transaction_id = seed_oauth_transaction(connection, provider_key="discord")

    with pytest.raises(AuthenticationFailure) as refusal:
        with migrated_database.begin() as connection:
            _complete(
                composition,
                connection,
                transaction_id=transaction_id,
                completion=completion,
            )

    # The same typed refusal as an unknown id, deliberately: a caller that learned
    # *which* predicate failed would learn whether the id exists and which
    # provider it belongs to.
    assert refusal.value.code == "transaction_unknown"
    assert refusal.value.audit.payload == {"reason": "completion_not_claimable"}

    with migrated_database.connect() as connection:
        assert _every_effect_count(connection) == NOTHING_HAPPENED
        row = connection.execute(
            select(oauth_transactions).where(oauth_transactions.c.id == transaction_id)
        ).mappings().one()
    # Consumed and *unclaimed*: the refusal rolled its own claim back, so the row
    # is in the same terminal state as process death — spent, unreplayable, and
    # unable to produce a session.
    assert row["consumed_at"] is not None
    assert row["completion_claimed_at"] is None


async def test_a_transaction_recorded_for_another_provider_is_not_completable_by_discord(
    migrated_database, composition, provider
):
    """TC-AUTH-15a, the other direction.

    Neither provider is privileged by the rule: the claim compares the row to the
    result, so a transaction started for some other provider cannot be spent by a
    verified Discord login either. Asserting only the first direction would leave
    a rule that happens to hold for the provider the suite uses most.
    """
    completion = await _provider_result(provider)
    assert completion.provider_key == "discord"

    with migrated_database.begin() as connection:
        transaction_id = seed_oauth_transaction(
            connection, provider_key="another-provider"
        )

    with pytest.raises(AuthenticationFailure):
        with migrated_database.begin() as connection:
            _complete(
                composition,
                connection,
                transaction_id=transaction_id,
                completion=completion,
            )

    with migrated_database.connect() as connection:
        assert _every_effect_count(connection) == NOTHING_HAPPENED
        claimed = connection.execute(
            select(oauth_transactions.c.completion_claimed_at).where(
                oauth_transactions.c.id == transaction_id
            )
        ).scalar_one()
    assert claimed is None


async def test_consuming_one_transaction_does_not_authorize_another_providers_result(
    migrated_database, composition, provider, other_provider
):
    """TC-AUTH-15b. Consumption of A authorizes nothing about B, or about B's provider.

    The caller does the work that makes a completion plausible: it consumes a real
    Discord transaction, so a verifier really was recovered and a provider exchange
    really could have followed. It then tries the two substitutions the finding
    describes — the other provider's result against the transaction it consumed,
    and its own result against a second transaction belonging to that other
    provider. Both are refused, and neither transaction is claimed.
    """
    discord_completion = await _provider_result(provider)
    foreign_completion = await _provider_result(other_provider)
    state = "a-state-for-the-consumed-discord-transaction"

    with migrated_database.begin() as connection:
        services = composition.services(connection)
        consumed_id = uuid4()
        services.transactions.create(
            state_hash=token_hash(state),
            verifier=composition.envelope.seal(b"v", aad=b"aad"),
            return_path="/v1/characters",
            provider_key="discord",
            expires_at=utcnow() + timedelta(minutes=10),
            client_ip_hash=None,
            transaction_id=consumed_id,
        )
        foreign_id = seed_oauth_transaction(
            connection, provider_key="another-provider"
        )

    with migrated_database.begin() as connection:
        assert composition.services(connection).transactions.consume(
            transaction_id=consumed_id, state_hash=token_hash(state), now=utcnow()
        ) is not None

    # (1) the consumed Discord transaction, completed with the other provider.
    with pytest.raises(AuthenticationFailure):
        with migrated_database.begin() as connection:
            _complete(
                composition,
                connection,
                transaction_id=consumed_id,
                completion=foreign_completion,
            )

    # (2) the other provider's transaction, completed with the Discord result the
    #     consumption above would have produced.
    with pytest.raises(AuthenticationFailure):
        with migrated_database.begin() as connection:
            _complete(
                composition,
                connection,
                transaction_id=foreign_id,
                completion=discord_completion,
            )

    with migrated_database.connect() as connection:
        assert _every_effect_count(connection) == NOTHING_HAPPENED
        claims = connection.execute(
            select(oauth_transactions.c.id).where(
                oauth_transactions.c.completion_claimed_at.isnot(None)
            )
        ).scalars().all()
    assert claims == [], "no row may be claimed by a refused completion"


async def test_the_matching_provider_still_completes_and_claims_exactly_once(
    migrated_database, composition, provider
):
    """TC-AUTH-15c. The predicate refuses a mismatch and nothing else.

    A control for the four tests above: with the provider that the row records,
    the identical call succeeds, claims the transaction once, and binds the
    session to it. A predicate that refused everything would satisfy the refusal
    tests perfectly.
    """
    completion = await _provider_result(provider)
    with migrated_database.begin() as connection:
        transaction_id = seed_oauth_transaction(connection, provider_key="discord")

    with migrated_database.begin() as connection:
        completed = _complete(
            composition,
            connection,
            transaction_id=transaction_id,
            completion=completion,
        )

    with migrated_database.connect() as connection:
        counts = _counts(connection)
        row = connection.execute(
            select(oauth_transactions).where(oauth_transactions.c.id == transaction_id)
        ).mappings().one()
        session_row = connection.execute(
            select(sessions).where(sessions.c.id == completed.session.session_id)
        ).mappings().one()
    assert counts == {"sessions": 1, "token_grants": 1, "successes": 1}
    assert row["completion_claimed_at"] is not None
    assert session_row["oauth_transaction_id"] == transaction_id


async def test_a_provider_mismatched_completion_writes_exactly_one_refusal_audit(
    migrated_database, composition, other_provider
):
    """TC-AUTH-15d. TC-AUTH-11's exactly-one rule, at the existing boundary.

    The refusal is *described* by the service and *written* by the recorder, in
    its own transaction after the completion's has rolled back — the arrangement
    that already exists for every other terminal refusal. This asserts that the
    provider-mismatch branch joins it rather than inventing a second audit path:
    one `auth.login.refused` event, carrying the reason category and the
    correlation id the caller was given, and no second event when the same
    recorder is offered the failure again.
    """
    from application.web.refusals import OAuthRefusalRecorder

    completion = await _provider_result(other_provider)
    with migrated_database.begin() as connection:
        transaction_id = seed_oauth_transaction(connection, provider_key="discord")

    correlation_id = uuid4()
    recorder = OAuthRefusalRecorder(migrated_database, correlation_id=correlation_id)
    try:
        with migrated_database.begin() as connection:
            composition.services(connection).oauth.complete(
                transaction_id=transaction_id,
                completion=completion,
                return_path="/v1/characters",
                now=utcnow(),
                correlation_id=correlation_id,
                client_ip_hash=None,
                user_agent_digest=None,
            )
        raise AssertionError("a provider-mismatched completion must be refused")
    except AuthenticationFailure as failure:
        recorder.record_failure(failure)
        # A second offer of the same failure must not write a second row.
        recorder.record_failure(failure)

    with migrated_database.connect() as connection:
        events = connection.execute(
            select(audit_events).where(
                audit_events.c.correlation_id == correlation_id
            )
        ).mappings().all()
        assert _every_effect_count(connection) == NOTHING_HAPPENED

    assert len(events) == 1
    assert events[0]["action"] == "auth.login.refused"
    assert events[0]["entity_id"] == str(transaction_id)
    assert events[0]["payload"]["reason"] == "completion_not_claimable"
    # No token, code, state, verifier or provider text ever reaches the payload.
    assert set(events[0]["payload"]) == {"reason"}


def test_the_claim_statement_refuses_a_foreign_provider_key_directly(
    migrated_database
):
    """TC-AUTH-15e. The repository statement, with the service out of the way.

    `claim_completion` is the enforcement point, so it is exercised as one: the
    same consumed row, claimed with the wrong key and then with the right one. A
    mutation that drops the `provider_key` predicate makes the first assertion
    fail here as well as through the service — the evidence does not depend on a
    single layer.
    """
    with migrated_database.begin() as connection:
        transaction_id = seed_oauth_transaction(connection, provider_key="discord")

    with migrated_database.begin() as connection:
        assert not OAuthTransactionRepository(connection).claim_completion(
            transaction_id=transaction_id,
            provider_key="another-provider",
            now=utcnow(),
        )

    with migrated_database.connect() as connection:
        assert connection.execute(
            select(oauth_transactions.c.completion_claimed_at).where(
                oauth_transactions.c.id == transaction_id
            )
        ).scalar_one() is None

    with migrated_database.begin() as connection:
        assert OAuthTransactionRepository(connection).claim_completion(
            transaction_id=transaction_id, provider_key="discord", now=utcnow()
        )


# ---------------------------------------------------------------------------
# TC-AUTH-15f — the typed input that makes the derivation trustworthy
# ---------------------------------------------------------------------------


async def test_a_completion_cannot_be_built_from_two_providers_results(
    provider, other_provider
):
    """TC-AUTH-15f. The halves are required to agree at construction.

    `complete()` derives the expected provider key from `VerifiedCompletion`, and
    that derivation is only worth anything if the object cannot hold one
    provider's tokens beside another's identity. It cannot: the pair is refused
    where it is built, so there is no moment at which a mismatched result exists
    as a value something could be trusted with.
    """
    discord_tokens = await provider.exchange(code="c", code_verifier="v")
    foreign_tokens = await other_provider.exchange(code="c", code_verifier="v")
    discord_identity = await provider.verify(discord_tokens)
    foreign_identity = await other_provider.verify(foreign_tokens)

    with pytest.raises(ProviderResultMismatch):
        VerifiedCompletion(identity=discord_identity, tokens=foreign_tokens)
    with pytest.raises(ProviderResultMismatch):
        VerifiedCompletion(identity=foreign_identity, tokens=discord_tokens)

    # And the agreeing pairs are ordinary values.
    assert VerifiedCompletion(
        identity=discord_identity, tokens=discord_tokens
    ).provider_key == "discord"
    assert VerifiedCompletion(
        identity=foreign_identity, tokens=foreign_tokens
    ).provider_key == "another-provider"


async def test_an_adapter_refuses_to_verify_another_providers_tokens(
    provider, other_provider
):
    """TC-AUTH-15f. The second, independent place the same rule holds.

    Verifying another provider's tokens would return *this* provider's identity
    resolved from a bearer token this adapter never obtained — the laundering step
    that would turn a foreign token result into a matching-key completion. The
    adapter refuses it before its first request, so the claim's predicate is not
    the only thing standing between those two facts.
    """
    from application.web.providers import ProviderRefused

    foreign_tokens = await other_provider.exchange(code="c", code_verifier="v")
    with pytest.raises(ProviderRefused):
        await provider.verify(foreign_tokens)


async def test_the_discord_adapter_stamps_and_checks_its_own_provider_key(tmp_path):
    """TC-AUTH-15f. The real adapter, not the double.

    The double's behaviour is only evidence if it matches the adapter it stands
    in for, so the two rules — a stamped key on the token result, and a refusal to
    verify a foreign one — are asserted against `DiscordIdentityProvider` itself,
    over a mocked transport.
    """
    import httpx

    from adapters.web.discord_provider import DiscordIdentityProvider
    from application.web.providers import ProviderRefused, ProviderTokens
    from tests.web_fixtures import web_settings

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "access_token": "provider-access-token",
                "expires_in": 604800,
                "scope": "identify guilds.members.read",
            },
        )

    adapter = DiscordIdentityProvider(
        web_settings(tmp_path).discord,
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    tokens = await adapter.exchange(code="the-code", code_verifier="the-verifier")
    assert tokens.provider_key == "discord"

    foreign = ProviderTokens(
        provider_key="another-provider",
        access_token=tokens.access_token,
        refresh_token=None,
        expires_at=tokens.expires_at,
        scopes=tokens.scopes,
    )
    with pytest.raises(ProviderRefused):
        await adapter.verify(foreign)
