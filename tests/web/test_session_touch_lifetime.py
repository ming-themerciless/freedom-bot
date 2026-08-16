"""TC-AUTH-19: an idle refresh cannot revive an expired session or confuse a method.

Codex's independent re-review of 2026-08-15 found the same two classes in
`touch()` that TC-AUTH-18 closed in `rotate()`, plus one that is specific to
touch:

1. **Revival.** `SessionRepository.touch()` updated a row when only
   `id = :id AND revoked_at IS NULL` held. `revoked_at IS NULL` says only that
   nobody has *ended* the session; an idle-expired row stays unrevoked until some
   read observes it. A caller holding a `SessionRecord` resolved while the
   session was valid could therefore touch it after its idle bound and push
   `idle_expires_at` back into the future — an expired session revived, and left
   live until its absolute bound. The tests for this deliberately never
   re-resolve the token: `resolve()` refusing the record first is not the
   control, because the record is a value the caller already holds and the write
   is the serialization boundary.
2. **Method confusion.** `SessionService.touch()` always passed
   `SessionSettings.idle_minutes`. WebAuthn and recovery-grant sessions were
   therefore given N-06's sixty-minute idle proposal instead of N-15's fifteen,
   bounded only by the sixty-minute absolute clamp — so a break-glass session
   could sit idle for the whole of its absolute lifetime when N-15 allows it
   fifteen minutes.
3. **Silent zero-row success.** The repository returned `None` unconditionally,
   so a refused refresh — zero rows updated — was indistinguishable from an
   accepted one. Refusal is now the typed `SessionTouchRefused`.

Codex's second re-review, later the same day, found that the correction to (2)
had been made **in the service only**. The repository still took `idle` and
`expected_auth_method` as independent arguments and verified only that the method
matched the row — so a caller supplying a break-glass row's *correct* method
beside the ordinary sixty-minute duration matched the row and extended its idle
window to the emergency absolute bound. The method predicate refuses a false
method; it cannot see a false duration standing next to a true one. The test that
claimed to cover this supplied `discord_oauth` for a break-glass row, which
exercises the predicate and not the bypass, and it has been **replaced** rather
than kept as evidence of a property it never established.

The duration is now not an argument at either layer: `SessionIdlePolicy` is a
complete validated method-to-window mapping, injected once at composition, and
the conditional `UPDATE` selects from it by the `auth_method` the row carries.
The direct-repository cases below are what make that a tested claim rather than a
described one — they call the supported API with no service in front of it, and
the invalid pairing raises `TypeError` because there is nowhere to put it.

Codex's **third** re-review, still 2026-08-15, found that this had closed the call
boundary and opened a construction one. `SessionIdlePolicy` was a frozen dataclass
taking `tuple[tuple[AuthMethod, timedelta], ...]`, and

    SessionIdlePolicy(tuple((m, timedelta(minutes=60)) for m in AuthMethod))

is complete, duplicate-free and positive — so it was accepted, and a repository
built with it selected sixty minutes for persisted WebAuthn and recovery-grant
rows. N-15 was bypassed again, through construction instead of through a call.
The policy tests here proved completeness, uniqueness and positivity and never
attempted a complete but semantically **false** mapping, which is why they passed
while the property they were offered for did not hold. Codex also found that
`WebComposition.services()` and `SessionService.__init__()` each derived a policy,
so "built once and injected" was false of the composition too.

The policy was then given no public constructor at all, with
`from_settings(SessionSettings)` as its one factory. Codex's **fourth** re-review,
still 2026-08-15, found three counterexamples that survived that (F1, F2, F3), and
they are the reason `SessionIdlePolicy` no longer exists:

- **F1.** `from_settings()` validated only positivity, and `SessionSettings` was a
  public frozen dataclass with no construction-time validation. So
  `SessionSettings(..., emergency_idle_minutes=60, ...)` was an accepted object
  and the policy built from it gave both break-glass methods sixty minutes.
  Closing the *policy's* constructor achieved nothing while the numbers it read
  could be anything.
- **F2.** `from_settings()` constructed `cls`, and the refresh SQL was generated
  by iterating the policy's public, overridable `__iter__`. A subclass inherited
  the supported factory and replaced the SQL's mapping while `for_method()` went
  on reporting fifteen minutes — ordinary Python subclassing, not forgery. The
  reproduction returned `idle_seconds_* = 3600.0` for all three methods.
- **F3.** `SessionService.__init__()` took a policy beside the repository and
  never required them to be the same. Correct wiring at both production sites was
  true and was not an invariant.

The correction is a change of shape rather than another guard.
`SessionSettings` validates the accepted register in `__post_init__`, so an
out-of-register instance cannot exist however it was built (F1).
`SessionIdlePolicy` is **deleted**: there is no object that pairs a method with a
duration, nothing is iterated to build the SQL, and `SessionRepository` *derives*
its `SessionPolicy` from settings rather than accepting one, so a subclass has
nothing to override and no way in (F2). `SessionService` takes its bounds from
the repository and has no policy argument, so a graph with two bounds sources is
not constructible (F3). Which window a method gets is
`application/web/capabilities.py`'s explicit `_SESSION_CLASSES` table, so an
authentication method nobody classified refuses at startup and at repository
construction instead of inheriting a window by inference (TC-AUTH-19g).

Every timestamp here is injected. `begin()`, `resolve()` and `touch()` all take
`now`, so an expiry is reached by advancing a value rather than by waiting, and
there is no sleep in this module.

**On the two expiry predicates.** `ck_sessions_idle_within_absolute` makes
`idle_expires_at <= absolute_expires_at` true of every row the database accepts,
so `idle_expires_at > :now` already implies `absolute_expires_at > :now` for any
reachable row. The absolute predicate is therefore unobservable through ordinary
rows, and a suite that used only those would leave "delete the absolute
predicate" an equivalent mutant. One test below drops the check constraint inside
a transaction it rolls back — the same technique TC-AUTH-18c uses for rotation —
which is the only honest way to present the conditional write with a row whose
idle window is live and whose absolute bound has passed.
"""
from __future__ import annotations

import dataclasses
import inspect
import threading
from dataclasses import replace
from datetime import timedelta
from enum import Enum
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select, text

from adapters.database.tables import audit_events, sessions
from adapters.web.repositories import SessionRepository, _touch_statement
from application.web import capabilities
from application.web.capabilities import (
    AuthMethod,
    SessionClass,
    UnclassifiedAuthMethod,
    require_complete_classification,
    session_class_of,
    unclassified_methods,
)
from application.web.config import SESSION_CEILINGS, SessionSettings
from application.web.sessions import (
    SessionPolicy,
    SessionService,
    SessionTouchRefused,
)

#: A `SessionSettings` at the accepted register, for the construction cases that
#: need one without a composition behind them.
VALID_SESSION_SETTINGS = SessionSettings(
    cookie_name="__Host-fb_session",
    cookie_secure=True,
    idle_minutes=60,
    absolute_hours=12,
    emergency_idle_minutes=15,
    emergency_absolute_minutes=60,
    max_sessions_per_account=10,
    login_transaction_cookie_name="__Host-fb_login_txn",
    oauth_transaction_minutes=10,
)
from tests.web.conftest import utcnow
from tests.web.test_session_rotation_lifetime import (
    EMERGENCY_ABSOLUTE,
    EMERGENCY_IDLE,
    ORDINARY_ABSOLUTE,
    ORDINARY_IDLE,
    _begin_break_glass_session,
    _begin_oauth_session,
    _row,
    _stale_record,
    _successors,
)

pytestmark = pytest.mark.database

#: The two break-glass methods. N-15 governs both, and the defect gave both the
#: ordinary window, so every method-sensitive case below runs for each.
BREAK_GLASS = (AuthMethod.WEBAUTHN, AuthMethod.RECOVERY_GRANT)


def _touch(composition, migrated_database, record, *, at):
    with migrated_database.begin() as connection:
        return composition.services(connection).session_service.touch(record, now=at)


def _repository(composition, connection) -> SessionRepository:
    """The repository as the composition root builds it, on a given connection.

    Direct-repository cases construct it here rather than through
    `composition.services()` so that what they exercise is the **supported
    lower-level API** — the layer the 2026-08-15 re-reviews found bypassable —
    with the configuration production uses and no service in front of it.

    It passes `composition.settings.session`, which is exactly what
    `WebComposition.services()` passes. The repository derives its own
    `SessionPolicy` from it (2026-08-15, F2/F3): there is no policy object for a
    test to hand over, so a test cannot exercise bounds production does not have.
    """
    return SessionRepository(connection, settings=composition.settings.session)


def _audits(connection) -> list[str]:
    return list(connection.execute(select(audit_events.c.action)).scalars())


def _assert_refused_and_untouched(migrated_database, session_id, before):
    """A refused refresh writes nothing at all.

    The complete row is compared, not just the fields the statement would have
    written: the claim is that the conditional write matched zero rows, and a
    zero-row `UPDATE` changes nothing anywhere.
    """
    with migrated_database.connect() as connection:
        after = _row(connection, session_id)
        assert _successors(connection, session_id) == [], (
            "a refused refresh must not create a successor row"
        )
        assert _audits(connection) == [], (
            "a refused refresh must not write an audit event"
        )
    assert dict(after) == dict(before), (
        "a refused refresh must leave the complete session row unchanged"
    )


# ---------------------------------------------------------------------------
# TC-AUTH-19a — the accepted refresh uses the session's own idle policy
# ---------------------------------------------------------------------------


def test_an_oauth_session_touched_inside_its_window_receives_the_ordinary_idle(
    migrated_database, composition
):
    """TC-AUTH-19a. N-06's sixty minutes, and an absolute bound that does not move."""
    start = utcnow()
    _, _, root = _begin_oauth_session(composition, migrated_database, at=start)
    at = start + timedelta(minutes=30)
    record = _stale_record(composition, migrated_database, root.token, at=at)

    refreshed = _touch(composition, migrated_database, record, at=at)

    assert refreshed.idle_expires_at == at + ORDINARY_IDLE
    assert refreshed.absolute_expires_at == start + ORDINARY_ABSOLUTE
    with migrated_database.connect() as connection:
        row = _row(connection, root.session_id)
    assert row["idle_expires_at"] == at + ORDINARY_IDLE
    assert row["absolute_expires_at"] == start + ORDINARY_ABSOLUTE, (
        "touch never writes the absolute bound the login set"
    )
    assert row["last_seen_at"] == at


@pytest.mark.parametrize("auth_method", BREAK_GLASS)
def test_a_break_glass_session_touched_inside_its_window_receives_the_emergency_idle(
    migrated_database, composition, auth_method
):
    """TC-AUTH-19a. N-15's fifteen minutes — the defect gave these sessions sixty.

    This is the assertion the old implementation failed: at ten minutes in, the
    ordinary duration would have produced `at + 60m`, clamped to the sixty-minute
    absolute bound and therefore equal to the boundary itself. The emergency
    duration produces `at + 15m`, twenty-five minutes in, well short of it.
    """
    start = utcnow()
    _, root = _begin_break_glass_session(
        composition, migrated_database, at=start, auth_method=auth_method
    )
    at = start + timedelta(minutes=10)
    record = _stale_record(composition, migrated_database, root.token, at=at)

    refreshed = _touch(composition, migrated_database, record, at=at)

    assert refreshed.idle_expires_at == at + EMERGENCY_IDLE
    assert refreshed.idle_expires_at != min(
        at + ORDINARY_IDLE, start + EMERGENCY_ABSOLUTE
    ), "a break-glass session must not receive N-06's idle window"
    assert refreshed.absolute_expires_at == start + EMERGENCY_ABSOLUTE
    with migrated_database.connect() as connection:
        row = _row(connection, root.session_id)
    assert row["idle_expires_at"] == at + EMERGENCY_IDLE
    assert row["absolute_expires_at"] == start + EMERGENCY_ABSOLUTE


def test_repeated_refreshes_converge_on_the_absolute_bound_and_never_pass_it(
    migrated_database, composition
):
    """TC-AUTH-19a. The clamp holds however many times the session is refreshed."""
    start = utcnow()
    _, root = _begin_break_glass_session(
        composition, migrated_database, at=start, auth_method=AuthMethod.WEBAUTHN
    )
    boundary = start + EMERGENCY_ABSOLUTE

    for minutes in (10, 20, 30, 40, 50):
        at = start + timedelta(minutes=minutes)
        record = _stale_record(composition, migrated_database, root.token, at=at)
        refreshed = _touch(composition, migrated_database, record, at=at)
        assert refreshed.idle_expires_at <= boundary
        assert refreshed.absolute_expires_at == boundary, (
            "no refresh may change the absolute expiration"
        )

    with migrated_database.connect() as connection:
        row = _row(connection, root.session_id)
    assert row["idle_expires_at"] == boundary
    assert row["absolute_expires_at"] == boundary

    # And the session still dies at the bound: the refreshes bought time inside
    # the login's lifetime, not past it.
    with migrated_database.begin() as connection:
        assert (
            composition.services(connection).session_service.resolve(
                root.token, now=boundary
            )
            is None
        )


# ---------------------------------------------------------------------------
# TC-AUTH-19b — a stale record cannot revive an expired session
# ---------------------------------------------------------------------------


def test_a_stale_oauth_record_cannot_touch_an_idle_expired_unrevoked_row(
    migrated_database, composition
):
    """TC-AUTH-19b. The defect exactly: resolve while valid, touch after the bound.

    The row is idle-expired and still unrevoked, because nothing has observed it
    since. Under the old statement this refresh succeeded and moved
    `idle_expires_at` an hour into the future.
    """
    start = utcnow()
    _, _, root = _begin_oauth_session(composition, migrated_database, at=start)
    record = _stale_record(composition, migrated_database, root.token, at=start)
    after_idle = start + ORDINARY_IDLE + timedelta(seconds=1)

    with migrated_database.connect() as connection:
        before = _row(connection, root.session_id)
    assert before["revoked_at"] is None, (
        "the row must still be unrevoked, or the test proves nothing"
    )
    assert before["idle_expires_at"] < after_idle

    with pytest.raises(SessionTouchRefused):
        _touch(composition, migrated_database, record, at=after_idle)

    _assert_refused_and_untouched(migrated_database, root.session_id, before)


@pytest.mark.parametrize("auth_method", BREAK_GLASS)
def test_a_stale_break_glass_record_cannot_touch_an_idle_expired_unrevoked_row(
    migrated_database, composition, auth_method
):
    """TC-AUTH-19b. Both emergency methods, past N-15's fifteen-minute window."""
    start = utcnow()
    _, root = _begin_break_glass_session(
        composition, migrated_database, at=start, auth_method=auth_method
    )
    record = _stale_record(composition, migrated_database, root.token, at=start)
    after_idle = start + EMERGENCY_IDLE + timedelta(seconds=1)

    with migrated_database.connect() as connection:
        before = _row(connection, root.session_id)
    assert before["revoked_at"] is None

    with pytest.raises(SessionTouchRefused):
        _touch(composition, migrated_database, record, at=after_idle)

    _assert_refused_and_untouched(migrated_database, root.session_id, before)


def test_an_absolute_expired_session_cannot_be_touched(
    migrated_database, composition
):
    """TC-AUTH-19b. Past the login's own bound, no refresh is available."""
    start = utcnow()
    _, root = _begin_break_glass_session(
        composition, migrated_database, at=start, auth_method=AuthMethod.WEBAUTHN
    )
    record = _stale_record(composition, migrated_database, root.token, at=start)

    with migrated_database.connect() as connection:
        before = _row(connection, root.session_id)

    with pytest.raises(SessionTouchRefused):
        _touch(
            composition,
            migrated_database,
            record,
            at=start + EMERGENCY_ABSOLUTE + timedelta(seconds=1),
        )

    _assert_refused_and_untouched(migrated_database, root.session_id, before)


def test_a_revoked_session_cannot_be_touched(migrated_database, composition):
    """TC-AUTH-19b. The predicate that was already there still holds."""
    start = utcnow()
    _, _, root = _begin_oauth_session(composition, migrated_database, at=start)
    at = start + timedelta(minutes=5)
    record = _stale_record(composition, migrated_database, root.token, at=at)
    with migrated_database.begin() as connection:
        _repository(composition, connection).revoke(
            root.session_id, reason="logout", at=at
        )

    with migrated_database.connect() as connection:
        before = _row(connection, root.session_id)

    with pytest.raises(SessionTouchRefused):
        _touch(composition, migrated_database, record, at=at + timedelta(minutes=1))

    _assert_refused_and_untouched(migrated_database, root.session_id, before)


# ---------------------------------------------------------------------------
# TC-AUTH-19c — the bounds are strict
# ---------------------------------------------------------------------------


def test_a_touch_exactly_at_the_idle_bound_is_refused(
    migrated_database, composition
):
    """TC-AUTH-19c. Equality is expired, matching `resolve()`'s `<=` refusal.

    An inclusive comparison would give a session whose idle window ends exactly
    now one more full window, which is the boundary-off-by-one that turns "the
    session expired" into "the session did not expire".
    """
    start = utcnow()
    _, _, root = _begin_oauth_session(composition, migrated_database, at=start)
    record = _stale_record(composition, migrated_database, root.token, at=start)
    boundary = start + ORDINARY_IDLE

    with migrated_database.connect() as connection:
        before = _row(connection, root.session_id)
    assert before["idle_expires_at"] == boundary

    with pytest.raises(SessionTouchRefused):
        _touch(composition, migrated_database, record, at=boundary)

    _assert_refused_and_untouched(migrated_database, root.session_id, before)

    # One microsecond earlier the same record is accepted, so the refusal above
    # is the boundary and not a broader failure.
    refreshed = _touch(
        composition,
        migrated_database,
        record,
        at=boundary - timedelta(microseconds=1),
    )
    assert refreshed.idle_expires_at > boundary


def test_a_touch_exactly_at_the_absolute_bound_is_refused(
    migrated_database, composition
):
    """TC-AUTH-19c. The absolute bound is exclusive too."""
    start = utcnow()
    _, root = _begin_break_glass_session(
        composition, migrated_database, at=start, auth_method=AuthMethod.WEBAUTHN
    )
    boundary = start + EMERGENCY_ABSOLUTE
    # Carry the idle window up to the bound so that the absolute comparison is
    # the one being tested rather than the idle one.
    for minutes in (10, 20, 30, 40, 50):
        at = start + timedelta(minutes=minutes)
        _touch(
            composition,
            migrated_database,
            _stale_record(composition, migrated_database, root.token, at=at),
            at=at,
        )
    record = _stale_record(
        composition, migrated_database, root.token, at=boundary - timedelta(minutes=1)
    )

    with migrated_database.connect() as connection:
        before = _row(connection, root.session_id)
    assert before["idle_expires_at"] == boundary
    assert before["absolute_expires_at"] == boundary

    with pytest.raises(SessionTouchRefused):
        _touch(composition, migrated_database, record, at=boundary)

    _assert_refused_and_untouched(migrated_database, root.session_id, before)


def test_the_absolute_predicate_refuses_a_row_whose_idle_window_outlives_it(
    migrated_database, composition
):
    """TC-AUTH-19c. Defense in depth, proved by removing the depth for one transaction.

    `ck_sessions_idle_within_absolute` makes this row unreachable through the
    application, so the absolute predicate in the conditional write is
    unobservable — untestable *and* unfalsifiable, which is the same thing as
    untested. This test drops the constraint, builds the row the constraint
    forbids, and rolls the whole transaction back; PostgreSQL DDL is
    transactional, so nothing outside it ever sees the missing constraint or the
    row.

    What it establishes: if a later migration relaxes the clamp, or an unclamped
    write path appears, an idle refresh still cannot extend a session past the
    absolute bound its login set.
    """
    start = utcnow()
    _, _, root = _begin_oauth_session(composition, migrated_database, at=start)
    record = _stale_record(composition, migrated_database, root.token, at=start)
    at = start + timedelta(minutes=10)

    with migrated_database.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(
                text(
                    "ALTER TABLE sessions "
                    "DROP CONSTRAINT ck_sessions_idle_within_absolute"
                )
            )
            connection.execute(
                sessions.update()
                .where(sessions.c.id == root.session_id)
                .values(
                    idle_expires_at=start + timedelta(hours=2),
                    absolute_expires_at=start + timedelta(minutes=5),
                )
            )
            with pytest.raises(SessionTouchRefused):
                composition.services(connection).session_service.touch(
                    record, now=at
                )
            row = _row(connection, root.session_id)
            assert row["idle_expires_at"] == start + timedelta(hours=2), (
                "the refused refresh must not have written the idle window"
            )
            assert row["last_seen_at"] != at

            # And the absolute comparison is **strict**, which is only
            # observable here for the same reason. With `idle > now` still
            # satisfied, moving the absolute bound to exactly `now` isolates the
            # one comparison: `>` refuses, `>=` would accept and hand the row a
            # fresh idle window at the instant its lifetime ended. Through
            # ordinary rows the clamp makes `>=` an equivalent mutant, so
            # without this case "make the absolute bound inclusive" is a change
            # no test could detect.
            connection.execute(
                sessions.update()
                .where(sessions.c.id == root.session_id)
                .values(absolute_expires_at=at)
            )
            with pytest.raises(SessionTouchRefused):
                composition.services(connection).session_service.touch(
                    record, now=at
                )
            assert _row(connection, root.session_id)["last_seen_at"] != at
        finally:
            transaction.rollback()

    with migrated_database.connect() as connection:
        constraint = connection.execute(
            text(
                "SELECT conname FROM pg_constraint "
                "WHERE conname = 'ck_sessions_idle_within_absolute'"
            )
        ).scalar_one_or_none()
        assert constraint == "ck_sessions_idle_within_absolute"
        assert _row(connection, root.session_id)["absolute_expires_at"] == (
            start + ORDINARY_ABSOLUTE
        )


# ---------------------------------------------------------------------------
# TC-AUTH-19d — the API cannot be told to use the wrong policy
# ---------------------------------------------------------------------------


def test_the_service_selects_the_idle_duration_and_the_caller_cannot():
    """TC-AUTH-19d. There is no parameter through which to pass sixty minutes.

    The signature is the control: `touch()` takes the trusted record and `now`.
    It does not select a duration either — the repository does, from the row —
    so there is nothing here for a caller to influence.
    """
    parameters = inspect.signature(SessionService.touch).parameters
    assert set(parameters) == {"self", "record", "now"}, (
        "touch must not accept a caller-supplied idle duration or method"
    )


def test_a_direct_repository_touch_of_an_oauth_row_applies_the_ordinary_window(
    migrated_database, composition
):
    """TC-AUTH-19d. N-06, through the repository alone — no service involved.

    The service is not in this path at all. What the supported repository API
    does with a Discord OAuth row, given only an id and an instant, is N-06's
    sixty minutes.
    """
    start = utcnow()
    _, _, root = _begin_oauth_session(composition, migrated_database, at=start)
    at = start + timedelta(minutes=30)

    with migrated_database.begin() as connection:
        touched = _repository(composition, connection).touch(root.session_id, now=at)

    assert touched is not None
    assert touched.idle_expires_at == at + ORDINARY_IDLE
    assert touched.absolute_expires_at == start + ORDINARY_ABSOLUTE
    with migrated_database.connect() as connection:
        row = _row(connection, root.session_id)
    assert row["idle_expires_at"] == at + ORDINARY_IDLE
    assert row["absolute_expires_at"] == start + ORDINARY_ABSOLUTE


@pytest.mark.parametrize("auth_method", BREAK_GLASS)
def test_a_direct_repository_touch_of_a_break_glass_row_applies_the_emergency_window(
    migrated_database, composition, auth_method
):
    """TC-AUTH-19d. N-15, through the repository alone — the bypass, closed.

    This is the case the previous remediation could not make. The repository is
    called directly, with the supported signature, by a caller that would rather
    have had sixty minutes: it gets fifteen, because the row says `webauthn` or
    `recovery_grant` and the statement reads that column rather than an argument.
    """
    start = utcnow()
    _, root = _begin_break_glass_session(
        composition, migrated_database, at=start, auth_method=auth_method
    )
    at = start + timedelta(minutes=10)

    with migrated_database.begin() as connection:
        touched = _repository(composition, connection).touch(root.session_id, now=at)

    assert touched is not None
    assert touched.idle_expires_at == at + EMERGENCY_IDLE, (
        "a break-glass row must receive N-15's window from the repository itself"
    )
    assert touched.idle_expires_at != min(
        at + ORDINARY_IDLE, start + EMERGENCY_ABSOLUTE
    ), "and specifically not N-06's, clamped or otherwise"
    assert touched.absolute_expires_at == start + EMERGENCY_ABSOLUTE
    with migrated_database.connect() as connection:
        assert _row(connection, root.session_id)["idle_expires_at"] == (
            at + EMERGENCY_IDLE
        )


def test_the_repository_touch_signature_admits_no_duration_or_method():
    """TC-AUTH-19d. The narrow signature assertion behind the behaviour above.

    Behavioural evidence establishes that the *right* window is applied. This
    establishes that there is no second way to ask — that the correct result is
    not merely what the default happens to be. The forbidden names are listed
    explicitly so that reintroducing `idle` under another name (`duration`,
    `deadline`, `expires_at`, `auth_method`) fails here rather than passing a set
    comparison somebody later loosened.
    """
    parameters = inspect.signature(SessionRepository.touch).parameters
    assert set(parameters) == {"self", "session_id", "now"}, (
        "the repository refresh takes an id and an instant, and nothing else"
    )
    forbidden = {
        "idle",
        "idle_expires_at",
        "duration",
        "seconds",
        "minutes",
        "deadline",
        "expires_at",
        "auth_method",
        "expected_auth_method",
        "method",
        "policy",
    }
    assert forbidden.isdisjoint(parameters), (
        f"the refresh must expose no duration or method argument: {parameters}"
    )


@pytest.mark.parametrize("auth_method", BREAK_GLASS)
def test_the_former_bypass_is_unavailable_rather_than_merely_refused(
    migrated_database, composition, auth_method
):
    """TC-AUTH-19d. The exact call Codex found on 2026-08-15, now unexpressible.

    The bypass was **not** a wrong method being refused. It was the row's own,
    entirely correct, method supplied beside the ordinary sixty-minute duration:
    the equality predicate matched, and the emergency session's idle window was
    extended to its absolute bound. A test that supplies `discord_oauth` for a
    break-glass row exercises the method predicate and says nothing about this,
    which is why that test has been replaced rather than kept.

    The pairing now raises `TypeError` — there is no parameter to carry the
    duration — and the row is left exactly as it was, because no statement ran.
    """
    start = utcnow()
    _, root = _begin_break_glass_session(
        composition, migrated_database, at=start, auth_method=auth_method
    )
    at = start + timedelta(minutes=5)

    with migrated_database.connect() as connection:
        before = _row(connection, root.session_id)

    with migrated_database.begin() as connection:
        repository = _repository(composition, connection)
        with pytest.raises(TypeError):
            repository.touch(
                root.session_id,
                now=at,
                idle=ORDINARY_IDLE,
                expected_auth_method=auth_method,  # the row's true method
            )
        # Nor by naming the emergency method's row and asking for the ordinary
        # window under any other spelling.
        for keyword in ("duration", "idle_expires_at", "seconds", "auth_method"):
            with pytest.raises(TypeError):
                repository.touch(
                    root.session_id, now=at, **{keyword: ORDINARY_IDLE}
                )

    _assert_refused_and_untouched(migrated_database, root.session_id, before)

    # And the supported call still works on the same row, so the refusals above
    # are the absent parameters and not a broken repository.
    with migrated_database.begin() as connection:
        touched = _repository(composition, connection).touch(root.session_id, now=at)
    assert touched is not None
    assert touched.idle_expires_at == at + EMERGENCY_IDLE


def test_the_repository_cannot_be_constructed_without_settings(
    migrated_database, composition
):
    """TC-AUTH-19d. The bounds are required, so no construction site can default them.

    Optional settings would put N-06's and N-15's numbers back into the adapter
    as a fallback, and would let a new construction site acquire a window nobody
    configured. Every construction site names one; there are two in production
    code and one in the operator tool, and a reviewer can find them by the
    argument.
    """
    with migrated_database.connect() as connection:
        with pytest.raises(TypeError):
            SessionRepository(connection)


# ---------------------------------------------------------------------------
# TC-AUTH-19f — F1: an out-of-register SessionSettings cannot exist
# ---------------------------------------------------------------------------


def test_out_of_register_session_settings_are_refused_at_construction():
    """TC-AUTH-19f/F1. The finding's own object, refused where it is built.

    Codex's fourth re-review (2026-08-15):

        settings = SessionSettings(..., emergency_idle_minutes=60, ...)
        policy = SessionIdlePolicy.from_settings(settings)
        policy.for_method(AuthMethod.WEBAUTHN) == timedelta(minutes=60)

    `from_settings()` validated only positivity, so sixty minutes for a
    break-glass method passed every check the policy had. Closing the policy's
    constructor was beside the point while the numbers it read could be anything;
    the invalid value had to stop being constructible, not stop being nameable in
    one particular place.

    `SessionSettings.__post_init__` now enforces the accepted register, so there
    is no such object to build a policy from — by the reader, by a test, by an
    operator tool or by direct Python construction, which the removed factory's
    own docstring named as supported.
    """
    with pytest.raises(ValueError, match="emergency_idle_minutes"):
        replace(VALID_SESSION_SETTINGS, emergency_idle_minutes=60)

    # And it is not a special case of "60": every register bound is enforced, in
    # both directions, and the refusal names the field and its policy.
    for field_name, (ceiling, policy) in SESSION_CEILINGS.items():
        with pytest.raises(ValueError, match=field_name):
            replace(VALID_SESSION_SETTINGS, **{field_name: ceiling + 1})
        with pytest.raises(ValueError, match=field_name):
            replace(VALID_SESSION_SETTINGS, **{field_name: 0})
        with pytest.raises(ValueError, match=field_name):
            replace(VALID_SESSION_SETTINGS, **{field_name: -1})
        # The ceiling itself is accepted: this is a bound, not an exact value,
        # and a deployment may tighten it (S-10).
        assert (
            getattr(replace(VALID_SESSION_SETTINGS, **{field_name: ceiling}), field_name)
            == ceiling
        )
        assert (
            getattr(replace(VALID_SESSION_SETTINGS, **{field_name: 1}), field_name) == 1
        )
        assert policy.startswith("N-")


def test_the_emergency_idle_boundary_is_fifteen_accepted_and_sixteen_refused():
    """TC-AUTH-19f/F1. N-15's exact boundary, named because the prompt names it."""
    assert replace(VALID_SESSION_SETTINGS, emergency_idle_minutes=15).emergency_idle_minutes == 15
    with pytest.raises(ValueError, match="emergency_idle_minutes=16"):
        replace(VALID_SESSION_SETTINGS, emergency_idle_minutes=16)


@pytest.mark.parametrize("auth_method", BREAK_GLASS)
def test_the_f1_sequence_cannot_reach_a_refresh_at_all(
    migrated_database, composition, auth_method
):
    """TC-AUTH-19f/F1. The finding's sequence, run in order, against the database.

    Not "the settings constructor raises" in isolation: the claim required is
    that a sixty-minute break-glass window is refused **before a repository can
    refresh a row**. So this runs the sequence — build the settings, derive the
    bounds, construct the repository, refresh a persisted break-glass row — and
    shows it stops at the first line with the row untouched, then shows the
    supported construction still applying N-15's fifteen minutes to that same
    row.
    """
    start = utcnow()
    _, root = _begin_break_glass_session(
        composition, migrated_database, at=start, auth_method=auth_method
    )
    at = start + timedelta(minutes=5)

    with migrated_database.connect() as connection:
        before = _row(connection, root.session_id)

    with migrated_database.begin() as connection:
        with pytest.raises(ValueError, match="emergency_idle_minutes"):
            forged = replace(
                composition.settings.session, emergency_idle_minutes=60
            )
            SessionRepository(connection, settings=forged).touch(
                root.session_id, now=at
            )

    _assert_refused_and_untouched(migrated_database, root.session_id, before)

    with migrated_database.begin() as connection:
        touched = _repository(composition, connection).touch(root.session_id, now=at)
    assert touched is not None
    assert touched.idle_expires_at == at + EMERGENCY_IDLE, (
        "the break-glass row keeps N-15's window, whatever a caller tried to build"
    )


def test_settings_cannot_be_edited_after_construction_to_get_around_the_register():
    """TC-AUTH-19f/F1. Frozen, so validation cannot be walked past afterwards."""
    with pytest.raises(dataclasses.FrozenInstanceError):
        VALID_SESSION_SETTINGS.emergency_idle_minutes = 60  # type: ignore[misc]
    assert VALID_SESSION_SETTINGS.emergency_idle_minutes == 15


# ---------------------------------------------------------------------------
# TC-AUTH-19f — F2: nothing pairs a method with a duration any more
# ---------------------------------------------------------------------------


def test_no_type_pairs_an_authentication_method_with_a_duration():
    """TC-AUTH-19f/F2. The extensible boundary is gone, not guarded.

    F2 was `SessionIdlePolicy.from_settings()` constructing `cls` while the
    refresh SQL was generated by iterating the policy's public `__iter__`:

        class ForgedPolicy(SessionIdlePolicy):
            def __iter__(self):
                return iter((m, timedelta(minutes=60)) for m in AuthMethod)

        policy = ForgedPolicy.from_settings(valid_settings)   # supported factory
        # for_method() still reports 15 minutes; the SQL gets 60.

    The prompt asks that this be closed by eliminating the extensible boundary so
    the sequence is *structurally inapplicable*, rather than by adding a guard
    that the next subclass finds a way around. It is: the class no longer exists,
    the repository accepts no policy, and no method-to-duration pairing is a
    parameter of anything.
    """
    import application.web.sessions as sessions_module

    assert not hasattr(sessions_module, "SessionIdlePolicy"), (
        "the extensible policy is deleted, not deprecated"
    )

    # `SessionPolicy` holds numbers with fixed roles. There is no mapping, no
    # sequence of pairs, and nothing to iterate — so there is nothing a subclass
    # can replace that the SQL reads.
    assert not hasattr(SessionPolicy, "__iter__"), (
        "an iterable policy is what F2 overrode; the SQL must not read one"
    )
    fields = {field.name for field in dataclasses.fields(SessionPolicy)}
    assert fields == {
        "ordinary_idle",
        "ordinary_absolute",
        "emergency_idle",
        "emergency_absolute",
        "max_sessions_per_account",
    }, f"the policy must hold roles, not a caller-supplied mapping: {sorted(fields)}"

    # The repository takes configuration, and takes nothing shaped like a
    # mapping, iterable, callback or strategy object.
    parameters = inspect.signature(SessionRepository.__init__).parameters
    assert set(parameters) == {"self", "connection", "settings"}, (
        f"the repository takes a connection and validated settings: {sorted(parameters)}"
    )
    assert parameters["settings"].annotation in (SessionSettings, "SessionSettings")


def test_the_refresh_statement_is_generated_from_classification_not_from_an_argument():
    """TC-AUTH-19f/F2. What the SQL is built from, checked at the generator.

    The F2 reproduction printed `idle_seconds_0/1/2 = 3600.0` — every method
    given N-06's window — from a policy whose `for_method()` answered fifteen
    minutes. The generator no longer iterates anything it was handed: it walks
    `AuthMethod` and asks `session_class_of()`. This asserts the parameters the
    conditional write is bound with, which is the value the database actually
    uses.
    """
    policy = SessionPolicy.derive(VALID_SESSION_SETTINGS)
    _, parameters = _touch_statement(policy)

    windows = {
        parameters[f"method_{index}"]: parameters[f"idle_seconds_{index}"]
        for index in range(len(AuthMethod))
    }
    assert windows == {
        "discord_oauth": ORDINARY_IDLE.total_seconds(),
        "webauthn": EMERGENCY_IDLE.total_seconds(),
        "recovery_grant": EMERGENCY_IDLE.total_seconds(),
    }, f"the generated statement must classify, not repeat one window: {windows}"


@pytest.mark.parametrize("auth_method", BREAK_GLASS)
def test_a_subclassed_policy_cannot_be_given_to_a_repository(
    migrated_database, composition, auth_method
):
    """TC-AUTH-19f/F2. The old sequence's remaining half, refused at the door.

    A subclass of `SessionPolicy` can still be *written* — Python is Python, and
    claiming otherwise is the kind of assertion the prompt rules out. What it
    cannot do is reach the refresh statement: the repository derives its policy
    from `SessionSettings` and has no parameter to receive one through, so the
    forged object has nowhere to go. The supported replacement is then proved
    against PostgreSQL on the same row.
    """

    class ForgedPolicy(SessionPolicy):
        """Overrides both routes F2 used: the derivation guard and the lookup."""

        def __post_init__(self) -> None:  # skips validation
            return None

        def idle_for(self, auth_method: AuthMethod) -> timedelta:
            return timedelta(minutes=60)

    forged = ForgedPolicy(
        ordinary_idle=timedelta(minutes=60),
        ordinary_absolute=timedelta(hours=12),
        emergency_idle=timedelta(minutes=60),
        emergency_absolute=timedelta(minutes=60),
        max_sessions_per_account=10,
    )
    assert forged.idle_for(AuthMethod.WEBAUTHN) == timedelta(minutes=60), (
        "the forged object is genuinely forged; the point is that it cannot be used"
    )

    start = utcnow()
    _, root = _begin_break_glass_session(
        composition, migrated_database, at=start, auth_method=auth_method
    )
    at = start + timedelta(minutes=5)
    with migrated_database.connect() as connection:
        before = _row(connection, root.session_id)

    with migrated_database.begin() as connection:
        # No keyword accepts it, under any spelling the old API used.
        for keyword in ("policy", "idle_policy", "bounds", "durations", "settings"):
            with pytest.raises((TypeError, ValueError)):
                SessionRepository(connection, **{keyword: forged})

    _assert_refused_and_untouched(migrated_database, root.session_id, before)

    with migrated_database.begin() as connection:
        touched = _repository(composition, connection).touch(root.session_id, now=at)
    assert touched is not None
    assert touched.idle_expires_at == at + EMERGENCY_IDLE, (
        "the persisted break-glass row receives N-15's window, not the forged sixty"
    )


def test_deriving_a_policy_from_a_lying_settings_subclass_validates_what_it_uses():
    """TC-AUTH-19f/F2. One read, so a property cannot be checked and then change.

    `SessionSettings` is a public type, so a subclass may override a field with a
    property — and one that answered 15 to the validator and 60 to the statement
    would reopen F2 at a different layer. `SessionPolicy.derive()` reads each
    number exactly once into a local and validates that local, so the value that
    is checked is the value that reaches the SQL, and a property that answers 60
    at all is refused.
    """

    reads: list[str] = []

    class DriftingSettings(SessionSettings):
        """Skips validation, and answers 15 first and 60 to every later read."""

        def __post_init__(self) -> None:
            return None

        def __getattribute__(self, name: str):
            if name == "emergency_idle_minutes":
                reads.append(name)
                return 15 if len(reads) == 1 else 60
            return super().__getattribute__(name)

    drifting = DriftingSettings(**dataclasses.asdict(VALID_SESSION_SETTINGS))

    policy = SessionPolicy.derive(drifting)
    assert len(reads) == 1, "a second read is a second answer; there must not be one"
    assert policy.emergency_idle == timedelta(minutes=15), (
        "the derivation must use the value it validated, not a later read"
    )
    _, parameters = _touch_statement(policy)
    windows = {
        parameters[f"method_{index}"]: parameters[f"idle_seconds_{index}"]
        for index in range(len(AuthMethod))
    }
    assert windows["webauthn"] == timedelta(minutes=15).total_seconds(), (
        "the statement must carry the validated value, not the later one"
    )

    class LyingSettings(SessionSettings):
        """Answers 60 on every read, so the one read that happens is refused."""

        def __post_init__(self) -> None:
            return None

        def __getattribute__(self, name: str):
            if name == "emergency_idle_minutes":
                return 60
            return super().__getattribute__(name)

    with pytest.raises(ValueError, match="emergency_idle_minutes"):
        SessionPolicy.derive(
            LyingSettings(**dataclasses.asdict(VALID_SESSION_SETTINGS))
        )


def test_a_directly_constructed_policy_is_still_held_to_the_register():
    """TC-AUTH-19f/F2. Belt and braces on a type that is derived, never accepted.

    Nothing supported hands a `SessionPolicy` to anything, so `__post_init__` is
    not a guard against a caller — it is a guard against a future edit that
    introduces one, and against a `dataclasses.replace` of a valid policy. It is
    *tested* rather than merely written, because validation that nobody exercises
    is the shape that was found not to hold three times already.
    """
    valid = SessionPolicy.derive(VALID_SESSION_SETTINGS)

    with pytest.raises(ValueError, match="emergency_idle_minutes"):
        replace(valid, emergency_idle=timedelta(minutes=60))
    with pytest.raises(ValueError, match="idle_minutes=90"):
        replace(valid, ordinary_idle=timedelta(minutes=90))
    with pytest.raises(ValueError, match="must be positive"):
        replace(valid, emergency_idle=timedelta(0))
    with pytest.raises(ValueError, match="max_sessions_per_account"):
        replace(valid, max_sessions_per_account=50)
    # A duration that is not a whole number of its unit is refused rather than
    # silently truncated into one that is.
    with pytest.raises(ValueError, match="whole number of minutes"):
        replace(valid, emergency_idle=timedelta(seconds=90))
    with pytest.raises(ValueError, match="whole number of hours"):
        replace(valid, ordinary_absolute=timedelta(minutes=90))


def test_a_policy_is_derived_from_settings_and_not_from_a_duck_type():
    """TC-AUTH-19f/F2. Numbers must come through the type that validates them."""

    class LooksLikeSettings:
        idle_minutes = 60
        absolute_hours = 12
        emergency_idle_minutes = 60
        emergency_absolute_minutes = 60
        max_sessions_per_account = 10

    with pytest.raises(TypeError, match="SessionSettings"):
        SessionPolicy.derive(LooksLikeSettings())


# ---------------------------------------------------------------------------
# TC-AUTH-19f — F3: one bounds source per graph
# ---------------------------------------------------------------------------


def test_a_service_cannot_be_given_a_second_bounds_source(
    migrated_database, composition
):
    """TC-AUTH-19f/F3. The mismatch sequence, executed rather than described.

    F3: `SessionService.__init__()` accepted a repository *and* an independently
    supplied policy, and required no relationship between them. A supported
    caller could build the repository from one `SessionSettings` and the service
    from another, so creation and rotation used one idle window while a refresh
    of the same row used a different one. Correct wiring at the two production
    sites was true and was not an invariant.

    This runs that sequence with two genuinely different valid configurations —
    five-minute and sixty-minute ordinary windows, both accepted by the register
    — and shows there is no argument to carry the second one. The prompt rules
    out asserting that a parameter name disappeared, so the disappearance is
    proved by attempting the construction and by then showing the service's
    bounds are the repository's own object.
    """
    other_settings = replace(composition.settings.session, idle_minutes=5)
    assert other_settings.idle_minutes != composition.settings.session.idle_minutes

    with migrated_database.connect() as connection:
        repository = SessionRepository(
            connection, settings=composition.settings.session
        )
        second_source = SessionPolicy.derive(other_settings)

        for keyword in ("settings", "idle_policy", "policy", "bounds"):
            with pytest.raises(TypeError):
                SessionService(
                    sessions=repository,
                    token_grants=None,
                    audit=None,
                    **{keyword: second_source},
                )

        service = SessionService(
            sessions=repository, token_grants=None, audit=None
        )

    # `is`, not `==`: the property is one object, and a value comparison would
    # pass for two independently derived policies that happened to agree.
    assert service.policy is repository.policy
    assert service.bounds_for(AuthMethod.DISCORD_OAUTH).idle == ORDINARY_IDLE
    assert service.bounds_for(AuthMethod.WEBAUTHN).idle == EMERGENCY_IDLE


def test_the_composition_gives_each_graph_one_bounds_source(
    migrated_database, composition
):
    """TC-AUTH-19f/F3. Production wiring, and no composition-level second copy.

    The previous correction held one policy on `WebComposition` and passed it to
    both layers. That was correct and was still a *convention*: the composition
    had to remember. The bounds now belong to the repository, so this asserts the
    structural property instead — every service in a graph reads its own
    repository's policy — and asserts that the composition holds no policy of its
    own to drift from it.
    """
    assert not hasattr(composition, "session_idle_policy"), (
        "a composition-level policy would be a second authority with nothing "
        "enforcing agreement"
    )

    with migrated_database.connect() as connection:
        services = composition.services(connection)
        second = composition.services(connection)

    assert services.session_service.policy is services.sessions_repository.policy
    assert second.session_service.policy is second.sessions_repository.policy
    # Two graphs are two derivations of the *same configuration*, so they agree
    # on every value even though they are not the same object.
    assert services.session_service.policy == second.session_service.policy


@pytest.mark.parametrize("auth_method", (AuthMethod.DISCORD_OAUTH,) + BREAK_GLASS)
def test_creation_bounds_and_refresh_use_the_same_derived_policy(
    migrated_database, composition, auth_method
):
    """TC-AUTH-19f/F3. What a login is given and what a refresh applies agree.

    The service proposes a session's bounds at creation and rotation through
    `bounds_for()`; the repository selects the refresh window inside the
    conditional write. Those are two code paths, and before this correction they
    read two independently supplied policies. Here they must both equal the one
    derived policy's window for the row's method — checked at creation, and then
    again against what the database actually wrote on refresh.
    """
    start = utcnow()
    if auth_method is AuthMethod.DISCORD_OAUTH:
        _, _, root = _begin_oauth_session(composition, migrated_database, at=start)
    else:
        _, root = _begin_break_glass_session(
            composition, migrated_database, at=start, auth_method=auth_method
        )

    with migrated_database.connect() as connection:
        services = composition.services(connection)
        expected = services.sessions_repository.policy.idle_for(auth_method)
        assert services.session_service.bounds_for(auth_method).idle == expected
    assert root.idle_expires_at == start + expected, (
        "creation used the derived policy's window for this method"
    )

    at = start + timedelta(minutes=2)
    with migrated_database.begin() as connection:
        touched = _repository(composition, connection).touch(root.session_id, now=at)
    assert touched is not None
    assert touched.idle_expires_at == at + expected, (
        "the refresh applied the same window creation did"
    )


def test_every_supported_session_construction_site_uses_the_one_model(
    migrated_database, composition
):
    """TC-AUTH-19f. The three construction sites, enumerated and exercised.

    Requirement 9 of the remediation: creation, rotation, refresh and the
    operator tool all go through the revised model. The two production sites are
    `WebComposition.services()` and `tools/session_revoke.py`; there is no third,
    and a new one cannot default its bounds because both constructors require
    them.
    """
    from tools import session_revoke

    # The operator tool's settings are a real `SessionSettings`, so they are
    # in-register by construction — a tool was one of the two documented ways an
    # F1 instance could previously have been built.
    assert isinstance(session_revoke._UNUSED_BOUNDS, SessionSettings)
    assert not hasattr(session_revoke, "_UNUSED_IDLE_POLICY"), (
        "the tool must not carry a second bounds source either"
    )

    with migrated_database.connect() as connection:
        tool_repository = SessionRepository(
            connection, settings=session_revoke._UNUSED_BOUNDS
        )
        tool_service = SessionService(
            sessions=tool_repository, token_grants=None, audit=None
        )
        assert tool_service.policy is tool_repository.policy

        services = composition.services(connection)
        assert services.session_service.policy is services.sessions_repository.policy


# ---------------------------------------------------------------------------
# TC-AUTH-19f — the classification the two windows are chosen by
# ---------------------------------------------------------------------------


def test_the_derived_policy_is_the_one_the_numeric_register_names(composition):
    """TC-AUTH-19f. N-06, N-07 and N-15, read out of configuration and nowhere else."""
    policy = SessionPolicy.derive(composition.settings.session)
    assert policy.idle_for(AuthMethod.DISCORD_OAUTH) == ORDINARY_IDLE
    assert policy.absolute_for(AuthMethod.DISCORD_OAUTH) == ORDINARY_ABSOLUTE
    for method in BREAK_GLASS:
        assert policy.idle_for(method) == EMERGENCY_IDLE
        assert policy.absolute_for(method) == EMERGENCY_ABSOLUTE


@pytest.mark.parametrize(
    ("idle_minutes", "emergency_idle_minutes"),
    [
        (60, 15),  # the configured defaults
        (30, 10),
        (1, 1),  # both at the contract's floor: equal, and neither is special
        (5, 15),  # ordinary **shorter** than emergency — permitted by the contract
    ],
)
def test_classification_holds_for_every_accepted_configuration(
    composition, idle_minutes, emergency_idle_minutes
):
    """TC-AUTH-19f. The invariant is classification, not an ordering of numbers.

    The configuration contract lets `WEB_SESSION_IDLE_MINUTES` fall to 1 while
    `WEB_EMERGENCY_SESSION_IDLE_MINUTES` ceilings at 15, so a deployment may have
    an ordinary window shorter than, equal to, or longer than the emergency one.
    An `emergency < ordinary` invariant would therefore refuse configurations the
    contract accepts, and is deliberately absent.

    What holds for every one of them is the structural rule: Discord OAuth gets
    whatever the ordinary value is, and both break-glass methods get whatever the
    emergency value is. The last case is the one that distinguishes a real
    classification from "pick the smaller number".
    """
    policy = SessionPolicy.derive(
        replace(
            composition.settings.session,
            idle_minutes=idle_minutes,
            emergency_idle_minutes=emergency_idle_minutes,
        )
    )

    assert policy.idle_for(AuthMethod.DISCORD_OAUTH) == timedelta(minutes=idle_minutes)
    for method in BREAK_GLASS:
        assert policy.idle_for(method) == timedelta(minutes=emergency_idle_minutes)

    # And the generated statement agrees, method for method.
    _, parameters = _touch_statement(policy)
    generated = {
        parameters[f"method_{index}"]: parameters[f"idle_seconds_{index}"]
        for index in range(len(AuthMethod))
    }
    assert generated == {
        method.value: policy.idle_for(method).total_seconds() for method in AuthMethod
    }


@pytest.mark.parametrize("auth_method", (AuthMethod.DISCORD_OAUTH,) + BREAK_GLASS)
def test_non_default_settings_map_by_classification_against_the_database(
    migrated_database, composition, auth_method
):
    """TC-AUTH-19f. The same, proved through the conditional write.

    `idle_minutes=5` with `emergency_idle_minutes=15` is a valid configuration in
    which the ordinary window is the **shorter** one. A repository built from
    those settings must still give the OAuth row five minutes and the break-glass
    rows fifteen — the classification, not the smaller or the larger value.
    """
    settings = replace(
        composition.settings.session, idle_minutes=5, emergency_idle_minutes=15
    )
    expected = timedelta(minutes=15 if auth_method.is_break_glass else 5)

    start = utcnow()
    if auth_method is AuthMethod.DISCORD_OAUTH:
        _, _, root = _begin_oauth_session(composition, migrated_database, at=start)
    else:
        _, root = _begin_break_glass_session(
            composition, migrated_database, at=start, auth_method=auth_method
        )
    at = start + timedelta(minutes=3)

    with migrated_database.begin() as connection:
        touched = SessionRepository(connection, settings=settings).touch(
            root.session_id, now=at
        )

    assert touched is not None
    assert touched.idle_expires_at == at + expected
    assert touched.absolute_expires_at == root.absolute_expires_at, (
        "a refresh never moves the absolute bound, whatever the idle window is"
    )


# ---------------------------------------------------------------------------
# TC-AUTH-19g — a future authentication method fails visibly
# ---------------------------------------------------------------------------


def test_every_authentication_method_is_explicitly_classified():
    """TC-AUTH-19g. The table is complete, and completeness is checked at import."""
    assert {method: method.session_class for method in AuthMethod} == {
        AuthMethod.DISCORD_OAUTH: SessionClass.ORDINARY,
        AuthMethod.WEBAUTHN: SessionClass.BREAK_GLASS,
        AuthMethod.RECOVERY_GRANT: SessionClass.BREAK_GLASS,
    }
    assert unclassified_methods(AuthMethod, capabilities._SESSION_CLASSES) == ()


def test_an_unclassified_future_method_is_refused_by_the_completeness_check():
    """TC-AUTH-19g. A genuinely new method, through the real guard.

    **Honest technique, and its scope.** `AuthMethod` is a closed enum: a test
    cannot add a member to it, so "a future authentication method" cannot be
    presented to the production table directly. The guard is therefore written
    generically over the enum and the table, and this gives it a *synthetic* enum
    with a member the table omits. What that establishes is that the check and
    its message are correct for exactly the condition a future method creates —
    which is the whole of the guard's logic. What it does not establish is that
    someone editing `AuthMethod` will run it; that is established by the call at
    import of `application/web/capabilities.py`, which this module's own import
    already executed, and by the construction-time refusal below.
    """

    class FutureAuthMethod(Enum):
        DISCORD_OAUTH = "discord_oauth"
        SERVICE_TOKEN = "service_token"  # added, and nobody classified it

    partial = {FutureAuthMethod.DISCORD_OAUTH: SessionClass.ORDINARY}

    assert unclassified_methods(FutureAuthMethod, partial) == ("service_token",)
    with pytest.raises(UnclassifiedAuthMethod, match="service_token"):
        require_complete_classification(FutureAuthMethod, partial)

    # A fully classified synthetic enum passes, so the guard is not simply always
    # raising.
    complete = partial | {FutureAuthMethod.SERVICE_TOKEN: SessionClass.BREAK_GLASS}
    assert unclassified_methods(FutureAuthMethod, complete) == ()
    require_complete_classification(FutureAuthMethod, complete)


def test_an_unclassified_method_refuses_repository_construction(
    migrated_database, monkeypatch
):
    """TC-AUTH-19g. The construction refusal, on the production classification.

    The complement to the test above, and it exercises the real path: with the
    table missing an entry — the exact state adding an `AuthMethod` member would
    leave it in — building a repository raises rather than generating a `CASE`
    that gives the unclassified method a window nobody chose.

    Scope: the *table* is patched, not the enum, because the enum cannot be
    extended. That is the same condition from the guard's point of view — a
    method present in `AuthMethod` and absent from the classification — and it is
    the condition the production code branches on.
    """
    incomplete = {
        method: session_class
        for method, session_class in capabilities._SESSION_CLASSES.items()
        if method is not AuthMethod.RECOVERY_GRANT
    }
    monkeypatch.setattr(capabilities, "_SESSION_CLASSES", incomplete)

    with migrated_database.connect() as connection:
        with pytest.raises(UnclassifiedAuthMethod, match="recovery_grant"):
            SessionRepository(connection, settings=VALID_SESSION_SETTINGS)

    # The refusal is not a silent default in either direction.
    with pytest.raises(UnclassifiedAuthMethod, match="recovery_grant"):
        session_class_of(AuthMethod.RECOVERY_GRANT)


def test_the_classification_is_restored_after_the_patched_case(migrated_database):
    """TC-AUTH-19g. `monkeypatch` really did put the table back.

    Stated as its own case rather than trusted: the test above replaces a module
    global that every session in the suite depends on, and a leak would make
    later results meaningless.
    """
    assert unclassified_methods(AuthMethod, capabilities._SESSION_CLASSES) == ()
    assert session_class_of(AuthMethod.RECOVERY_GRANT) is SessionClass.BREAK_GLASS
    with migrated_database.connect() as connection:
        repository = SessionRepository(connection, settings=VALID_SESSION_SETTINGS)
    assert repository.policy.idle_for(AuthMethod.RECOVERY_GRANT) == timedelta(minutes=15)


def test_a_window_is_defined_for_authentication_methods_and_nothing_else():
    """TC-AUTH-19f. An unknown value raises rather than taking a branch.

    `AuthMethod` is a closed enum, so "unknown method" is only meaningful as
    *something that is not an `AuthMethod`*. Left unchecked, `"webauthn"` — the
    persisted string rather than the member — is not a key of the classification
    table, and the accident that follows is a value silently taking the ordinary
    branch. The persisted-string case has its own control: the refresh
    statement's `IN` list refuses a row whose method the policy does not govern,
    proved by `test_a_row_whose_method_the_policy_does_not_govern_is_refused`.
    """
    policy = SessionPolicy.derive(VALID_SESSION_SETTINGS)
    for value in ("webauthn", "discord_oauth", None, 0, object()):
        with pytest.raises(TypeError, match="AuthMethod"):
            session_class_of(value)
        with pytest.raises(TypeError, match="AuthMethod"):
            policy.idle_for(value)


def test_a_row_whose_method_the_policy_does_not_govern_is_refused(
    migrated_database, composition
):
    """TC-AUTH-19d. The `IN` predicate, made observable by removing the constraint.

    `ck_sessions_auth_method` allows exactly the three values the policy covers,
    so no reachable row can fail this predicate — it is unobservable through
    ordinary rows, and therefore untestable *and* unfalsifiable unless the
    constraint is removed for the length of one rolled-back transaction, the same
    technique TC-AUTH-19c and TC-AUTH-18d use for the absolute predicate.

    What it establishes: if a later migration adds an authentication method and
    the policy is not extended with it, the refresh **refuses** that row rather
    than handing it its absolute bound through a `NULL` interval. The failure it
    prevents is silent, which is why it is worth proving.

    The row is a WebAuthn one because
    `ck_sessions_oauth_transaction_binding` ties `auth_method = 'discord_oauth'`
    to a non-null `oauth_transaction_id`: relabelling an OAuth row would violate a
    *second* constraint and prove nothing about this predicate. A break-glass row
    names no transaction, so only the method constraint stands in the way.
    """
    start = utcnow()
    _, root = _begin_break_glass_session(
        composition, migrated_database, at=start, auth_method=AuthMethod.WEBAUTHN
    )
    at = start + timedelta(minutes=10)

    with migrated_database.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(
                text(
                    "ALTER TABLE sessions DROP CONSTRAINT ck_sessions_auth_method"
                )
            )
            connection.execute(
                sessions.update()
                .where(sessions.c.id == root.session_id)
                .values(auth_method="future_method")
            )
            before = _row(connection, root.session_id)

            assert (
                _repository(composition, connection).touch(root.session_id, now=at)
                is None
            ), "an ungoverned method must be refused, never given a default window"

            after = _row(connection, root.session_id)
            assert dict(after) == dict(before), (
                "the refused refresh must have written nothing at all"
            )
        finally:
            transaction.rollback()

    with migrated_database.connect() as connection:
        constraint = connection.execute(
            text(
                "SELECT conname FROM pg_constraint "
                "WHERE conname = 'ck_sessions_auth_method'"
            )
        ).scalar_one_or_none()
        assert constraint == "ck_sessions_auth_method"
        assert _row(connection, root.session_id)["auth_method"] == "webauthn"


def test_the_service_raises_the_typed_refusal_when_no_row_is_updated(
    migrated_database, composition
):
    """TC-AUTH-19d. A zero-row write is a refusal, never a silent success."""
    start = utcnow()
    _, _, root = _begin_oauth_session(composition, migrated_database, at=start)
    record = _stale_record(composition, migrated_database, root.token, at=start)
    with migrated_database.begin() as connection:
        connection.execute(sessions.delete().where(sessions.c.id == root.session_id))

    with pytest.raises(SessionTouchRefused):
        _touch(composition, migrated_database, record, at=start + timedelta(minutes=1))


# ---------------------------------------------------------------------------
# TC-AUTH-19e — concurrency, against real PostgreSQL
# ---------------------------------------------------------------------------


def test_a_concurrent_refresh_and_revocation_never_leaves_a_refreshed_live_session(
    database_url, migrated_database, composition
):
    """TC-AUTH-19e. Revocation wins or the refresh does, and the row ends revoked.

    Both statements are `UPDATE`s carrying `revoked_at IS NULL`, so they contend
    on the same row under `READ COMMITTED`. The loser blocks, re-evaluates its
    predicate when the winner commits, and PostgreSQL decides — there is no
    sleep, no retry and no application-side ordering.

    The property claimed is the one the implementation actually provides: the
    session is revoked in both interleavings, and a refresh that lost is refused
    rather than reviving a session an operator has just ended. It is deliberately
    **not** a claim that one thread always wins; that would be an invention.
    """
    start = utcnow()
    _, _, root = _begin_oauth_session(composition, migrated_database, at=start)
    at = start + timedelta(minutes=30)
    record = _stale_record(composition, migrated_database, root.token, at=at)

    other = create_engine(database_url)
    barrier = threading.Barrier(2)
    outcomes: list[str] = []
    lock = threading.Lock()

    def refresh(engine):
        try:
            with engine.begin() as connection:
                barrier.wait(timeout=30)
                composition.services(connection).session_service.touch(record, now=at)
            outcome = "refreshed"
        except SessionTouchRefused:
            outcome = "refused"
        with lock:
            outcomes.append(outcome)

    def revoke(engine):
        with engine.begin() as connection:
            barrier.wait(timeout=30)
            _repository(composition, connection).revoke(
                root.session_id, reason="operator", at=at
            )
        with lock:
            outcomes.append("revoked")

    threads = [
        threading.Thread(target=refresh, args=(migrated_database,)),
        threading.Thread(target=revoke, args=(other,)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
    other.dispose()

    assert sorted(outcomes) in (["refreshed", "revoked"], ["refused", "revoked"]), (
        f"unexpected outcome pair: {outcomes}"
    )
    with migrated_database.connect() as connection:
        row = _row(connection, root.session_id)
    assert row["revoked_at"] == at, "the session must end revoked either way"
    assert row["revocation_reason"] == "operator"

    # And it is unusable afterwards, whichever thread won the refresh.
    with migrated_database.begin() as connection:
        assert (
            composition.services(connection).session_service.resolve(
                root.token, now=at + timedelta(seconds=1)
            )
            is None
        )
