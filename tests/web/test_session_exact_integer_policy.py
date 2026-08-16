"""TC-AUTH-19m: a registered session number must be an *exact* built-in `int`.

The fourth form of one defect. `SessionSettings.__post_init__` and the
derived-policy gate now share a single definition of what these numbers may be —
that was the 2026-08-15 session-policy numeric-validation remediation — and that
definition said:

    if not isinstance(value, int) or isinstance(value, bool):

which refuses `bool` and every float, and accepts **every other subclass of
`int`**. An `int` subclass may override `__lt__`, `__gt__`, `__le__` and `__ge__`,
and Python gives the right-hand operand's reflected comparison priority, so
`len(live) >= maximum` asks the *subclass* when `maximum` is one. A subclass
answering `False` to every comparison therefore reproduced the NaN outcome
exactly: `_enforce_session_limit` saw false for every live-session count, revoked
nothing, and N-66 was inoperative.

The route needed no `object.__new__`, no mutation of a frozen instance, no
private helper, no forged policy and no skipped `__post_init__`:

    settings = dataclasses.replace(
        VALID_SESSION_SETTINGS, max_sessions_per_account=LyingInt(10)
    )
    policy = SessionPolicy.derive(settings)
    assert not (100 >= policy.max_sessions_per_account)

The accepted rule is therefore `type(value) is int`, stated as an exact type for
the same reason the float rule was stated as a type: it covers the class rather
than the one member of it a review happened to construct. It is deliberately
**not** expressed as `isinstance`, as an annotation, as a coercion, as a list of
excluded subclasses, or as a check of one comparison result — the last of which
would be asking the value under test to grade itself.

**What this module deliberately does not do.** It asserts no annotation, no
signature and no source text. Every case goes through `SessionSettings(...)`,
`dataclasses.replace()`, `SessionPolicy(...)`, `SessionPolicy.derive()`,
`SessionRepository(...)` or the real service against disposable PostgreSQL. The
lying-subclass cases inherit `__post_init__` rather than bypassing it, so
ordinary construction observes a valid stored integer and only the single later
derivation read lies.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select

from adapters.database.tables import audit_events, sessions
from adapters.web.repositories import SessionRepository
from application.web.config import (
    SESSION_BOUNDS,
    SESSION_CEILINGS,
    SessionSettings,
    session_policy_problem,
)
from application.web.sessions import SessionPolicy
from tests.web.conftest import make_account, utcnow
from tests.web.test_session_policy_numeric_validation import (
    POLICY_FIELDS,
    _begin,
    _lying_settings,
    _live_session_ids,
)
from tests.web.test_session_touch_lifetime import VALID_SESSION_SETTINGS

pytestmark = pytest.mark.database


class LyingInt(int):
    """The reported counterexample, verbatim.

    A genuine `int` — `isinstance(LyingInt(10), int)` is true and it is not a
    `bool` — whose rich comparisons answer `False` whatever it is compared with.
    Because Python consults the right-hand operand's reflected comparison first
    when the right-hand type is a subclass of the left's, `count >= maximum` is
    answered by *this* class for every count.
    """

    __slots__ = ()

    def __lt__(self, other):  # noqa: D105 - the whole point is that it lies
        return False

    def __gt__(self, other):
        return False

    def __le__(self, other):
        return False

    def __ge__(self, other):
        return False


class LyingSeconds(float):
    """A `float` whose comparisons lie, for the duration half of the register."""

    __slots__ = ()

    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return False


class LyingTimedelta(timedelta):
    """A genuine `timedelta` that reports a comparison-overriding `total_seconds`."""

    __slots__ = ()

    def total_seconds(self) -> float:
        return LyingSeconds(super().total_seconds())


# ---------------------------------------------------------------------------
# Requirement 1 — settings construction and `replace()`, on every register field
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("field_name", sorted(SESSION_CEILINGS))
def test_settings_construction_refuses_a_comparison_overriding_int_subclass(field_name):
    """Requirement 1. Every registered field, at both public construction routes.

    The value used is the field's own **accepted** number wrapped in the lying
    subclass, so nothing here is refused for being out of range: `LyingInt(10)`
    for `max_sessions_per_account` is ten. What is refused is its type, which is
    the whole finding — a number that is in range and still not a number the
    comparison behind N-66 can be run against.
    """
    accepted, _policy = SESSION_CEILINGS[field_name]
    lying = LyingInt(accepted)

    # It really is an int by the old rule, and really does lie by the new one.
    assert isinstance(lying, int) and not isinstance(lying, bool)
    assert type(lying) is not int
    assert not (accepted >= lying) and not (10**6 >= lying)

    with pytest.raises(ValueError, match=field_name):
        replace(VALID_SESSION_SETTINGS, **{field_name: lying})

    values = {
        field.name: getattr(VALID_SESSION_SETTINGS, field.name)
        for field in VALID_SESSION_SETTINGS.__dataclass_fields__.values()
    }
    values[field_name] = lying
    with pytest.raises(ValueError, match=field_name):
        SessionSettings(**values)


def test_the_shared_definition_itself_refuses_the_subclass_for_every_field():
    """Requirement 1, at the one definition both gates call.

    Parameterised from the register rather than restated, and asserted as a
    *problem* rather than as an absence of one, so a validator that silently
    returned `None` for an unknown field would fail here.
    """
    for field_name, bound in SESSION_BOUNDS.items():
        problem = session_policy_problem(field_name, LyingInt(bound.maximum))
        assert problem is not None and field_name in problem
        # And the accepted plain integer is still accepted, so the rule refuses a
        # type rather than a value.
        assert session_policy_problem(field_name, bound.maximum) is None


# ---------------------------------------------------------------------------
# Requirement 2 — the derived policy, at both of its construction routes
# ---------------------------------------------------------------------------


def test_a_directly_constructed_policy_refuses_a_lying_maximum():
    """Requirement 2. `SessionPolicy(...)` and `dataclasses.replace()` alike."""
    valid = SessionPolicy.derive(VALID_SESSION_SETTINGS)

    with pytest.raises(ValueError, match="max_sessions_per_account"):
        replace(valid, max_sessions_per_account=LyingInt(10))

    with pytest.raises(ValueError, match="max_sessions_per_account"):
        SessionPolicy(
            ordinary_idle=timedelta(minutes=60),
            ordinary_absolute=timedelta(hours=12),
            emergency_idle=timedelta(minutes=15),
            emergency_absolute=timedelta(minutes=60),
            max_sessions_per_account=LyingInt(10),
        )

    assert type(valid.max_sessions_per_account) is int


@pytest.mark.parametrize(
    "attribute",
    ["ordinary_idle", "ordinary_absolute", "emergency_idle", "emergency_absolute"],
)
def test_a_policy_duration_cannot_be_a_lying_int_at_all(attribute):
    """Requirement 2, for the four fields the policy carries as durations.

    A comparison-overriding `int` cannot *become* one of these: they are
    `timedelta`s, and a value that is not one is refused before any comparison is
    attempted. The case is here rather than assumed, because "that field is a
    different type" is the kind of reasoning that was wrong about `bool`.
    """
    valid = SessionPolicy.derive(VALID_SESSION_SETTINGS)
    with pytest.raises(ValueError, match=attribute):
        replace(valid, **{attribute: LyingInt(60)})


def test_a_lying_duration_is_reduced_to_an_exact_int_before_the_register_sees_it():
    """Requirement 2, the other way a lie could reach a session bound.

    A genuine `timedelta` subclass whose `total_seconds()` answers a
    comparison-overriding float is the duration-shaped version of the finding.
    It is refused when it is out of register — which is only possible if the
    number the register was shown was a truthful, exact `int` — and accepted when
    it is in register, with the ordinary comparison holding afterwards.
    """
    valid = SessionPolicy.derive(VALID_SESSION_SETTINGS)

    with pytest.raises(ValueError, match="idle_minutes=90"):
        replace(valid, ordinary_idle=LyingTimedelta(minutes=90))

    accepted = replace(valid, ordinary_idle=LyingTimedelta(minutes=30))
    assert accepted.ordinary_idle == timedelta(minutes=30)


def test_derivation_refuses_a_settings_subclass_that_answers_a_lying_int_later():
    """Requirement 3. The reported sequence, through the supported derivation.

    The subclass is genuine: it inherits `__post_init__`, so the settings gate
    observed a valid stored `10` and accepted the object; the single read
    `derive()` makes afterwards answers `LyingInt(10)`. Both halves of the claim
    are asserted — the field is read **exactly once** during derivation, and that
    one read is fully validated.
    """
    settings, reads = _lying_settings("max_sessions_per_account", LyingInt(10))
    reads_at_construction = len(reads)

    with pytest.raises(ValueError, match="max_sessions_per_account"):
        SessionPolicy.derive(settings)

    assert len(reads) - reads_at_construction == 1, (
        f"derivation must read the field exactly once. Reads: {reads}"
    )
    lied = settings.max_sessions_per_account
    assert type(lied) is LyingInt, "the subclass must actually be lying by now"


@pytest.mark.parametrize("field_name", sorted(POLICY_FIELDS))
def test_derivation_refuses_the_lying_int_on_every_field_the_policy_carries(field_name):
    """Requirement 3, across the register rather than at one field.

    A correction special-cased to `max_sessions_per_account` — the field the
    finding named — passes the case above and fails here.
    """
    accepted, _policy = SESSION_CEILINGS[field_name]
    settings, reads = _lying_settings(field_name, LyingInt(accepted))
    reads_at_construction = len(reads)

    with pytest.raises(ValueError, match=field_name):
        SessionPolicy.derive(settings)

    assert len(reads) - reads_at_construction == 1, (
        f"derivation must read {field_name} exactly once. Reads: {reads}"
    )


# ---------------------------------------------------------------------------
# Requirement 4 — the repository, and N-66 against real PostgreSQL
# ---------------------------------------------------------------------------


def test_the_repository_cannot_be_built_from_settings_that_lie(migrated_database):
    """Requirement 4. The supported route into the running graph is closed.

    `SessionRepository` is the one owner of session bounds in a composition, and
    `SessionPolicy.derive()` is the only way it obtains them. The reproduction
    therefore halts here, before any statement is compiled and before any session
    exists — which is what "the real session service cannot exceed N-66" has to
    mean.
    """
    settings, _reads = _lying_settings("max_sessions_per_account", LyingInt(10))
    with migrated_database.connect() as connection:
        with pytest.raises(ValueError, match="max_sessions_per_account"):
            SessionRepository(connection, settings=settings)


def test_the_old_predicate_would_have_admitted_the_value_and_disabled_the_limit():
    """Requirement 4's falsification control, run rather than asserted in prose.

    This is what makes the cases above discriminating rather than decorative: the
    reviewed predicate is reconstructed here and shown to **accept** the value,
    and the comparison `_enforce_session_limit` performs is shown to be false for
    a population far above the maximum. Nothing in the module under test is
    patched; the old rule is expressed as the two-line expression it was.
    """
    lying = LyingInt(10)

    admitted_by_the_old_rule = isinstance(lying, int) and not isinstance(lying, bool)
    assert admitted_by_the_old_rule, "the old predicate must really have let it in"

    # The consequence, at the exact comparison in `_enforce_session_limit`.
    assert not (10 >= lying)
    assert not (100 >= lying)
    assert not (10_000 >= lying)

    # And the new rule refuses it, at the one definition both gates call.
    assert session_policy_problem("max_sessions_per_account", lying) is not None


def test_the_live_session_bound_still_holds_against_real_postgresql(
    migrated_database, composition
):
    """Requirement 4. The control the bypass disabled, proved durable.

    Eleven logins under the accepted maximum of ten leave exactly ten live
    sessions, the oldest revoked with reason `session_limit`, and one audit
    event — read back from a fresh connection after the creating transactions
    committed. With a lying maximum this sequence produced eleven live sessions,
    no revocation and no audit record.
    """
    maximum = composition.settings.session.max_sessions_per_account
    assert type(maximum) is int and maximum == 10

    with migrated_database.begin() as connection:
        account_id = make_account(connection)

    start = utcnow()
    issued = [
        _begin(
            composition, migrated_database, account_id, at=start + timedelta(seconds=i)
        )
        for i in range(11)
    ]

    with migrated_database.connect() as connection:
        live = _live_session_ids(connection, account_id)
        revoked = connection.execute(
            select(sessions.c.id, sessions.c.revocation_reason).where(
                sessions.c.platform_account_id == account_id,
                sessions.c.revoked_at.is_not(None),
            )
        ).mappings().all()
        events = connection.execute(
            select(audit_events).where(
                audit_events.c.action == "auth.session.revoked"
            )
        ).mappings().all()

    assert live == {session.session_id for session in issued[1:]}
    assert len(live) == maximum
    assert [row["id"] for row in revoked] == [issued[0].session_id]
    assert revoked[0]["revocation_reason"] == "session_limit"
    assert len(events) == 1 and events[0]["payload"]["limit"] == maximum
