"""TC-AUTH-19l / TC-SESS-08b: the session-policy numbers are typed, not merely ordered.

Codex's independent implementation review and its distinct security-focused pass
of 2026-08-15 report **one** blocking defect from two perspectives (F1 and S1).
Its shape:

- `SessionSettings.__post_init__()` required every registered numeric field to be
  an actual `int`, excluding `bool`, positive and within its ceiling;
- the derived-policy boundary restated the rule as two ordering comparisons —
  `value < 1` and `value > ceiling` — and dropped the type half;
- `float("nan")` makes both comparisons false, so it survived derivation as
  `max_sessions_per_account`; and
- `len(live) >= maximum` is then false for **every** live-session count, so
  `_enforce_session_limit()` revoked nothing and N-66 was inoperative.

The value was reachable through the supported repository constructor with no
`object.__new__`, no mutation of a frozen instance, no forged `SessionPolicy` and
no private helper: `SessionPolicy.derive()` deliberately accepts subclasses of
`SessionSettings`, so a subclass whose inherited construction observes the valid
stored integer can answer differently on the single later read that derivation
makes.

The correction is one authoritative definition rather than a third restatement.
`application/web/config.py` holds `session_policy_problem` /
`session_policy_problems` beside the `SESSION_CEILINGS` register, and **both**
gates call it: `SessionSettings.__post_init__` and `_validate_policy_values` in
`application/web/sessions.py`, which is what `SessionPolicy.__post_init__` and
`SessionPolicy.derive()` both go through. The accepted type is `int` and never
`bool`; refusing anything that is not an `int` covers floats as a class —
integral-looking, fractional, infinite and NaN alike — instead of naming the one
non-finite value a review happened to find.

**What this module deliberately does not do.** It asserts no annotation, no
signature, no source text, and it calls no private helper in place of the
boundary the numbers actually cross. Every case here goes through
`SessionSettings(...)`/`dataclasses.replace`, `SessionPolicy(...)`,
`SessionPolicy.derive()`, `WebSettings.from_environment()` or the service against
real PostgreSQL. The lying-subclass cases are honest to the reported threat: the
subclass **inherits** `__post_init__` rather than bypassing it, so ordinary
construction observes a valid integer and only the later derivation read lies —
bypassing construction would reproduce a different, weaker defect than the one
reviewed.
"""
from __future__ import annotations

import dataclasses
from dataclasses import replace
from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select

from adapters.database.tables import audit_events, sessions
from application.audit import ActorCapability
from application.web.capabilities import (
    AdministratorScope,
    AuthMethod,
    MembershipProjection,
    WebAuthorizationContext,
)
from application.web.config import (
    SESSION_CEILINGS,
    ConfigurationError,
    SessionSettings,
    WebSettings,
)
from application.web.sessions import SessionPolicy
from tests.web.composition_harness import substituted_composition
from tests.web.conftest import make_account, seed_oauth_transaction, utcnow
from tests.web.test_session_touch_lifetime import VALID_SESSION_SETTINGS
from tests.web_fixtures import TEST_GUILD_ID, web_environment, web_settings

pytestmark = pytest.mark.database


#: The register fields `SessionPolicy` carries, and the unit each is stored in.
#: `oauth_transaction_minutes` is deliberately absent: it is in the register and
#: on `SessionSettings`, and no session *lifetime* policy holds it, so its
#: boundary is the settings constructor and not derivation.
POLICY_FIELDS: dict[str, tuple[str, str]] = {
    "idle_minutes": ("ordinary_idle", "minutes"),
    "absolute_hours": ("ordinary_absolute", "hours"),
    "emergency_idle_minutes": ("emergency_idle", "minutes"),
    "emergency_absolute_minutes": ("emergency_absolute", "minutes"),
    "max_sessions_per_account": ("max_sessions_per_account", "count"),
}


def _stored(field_name: str, number: int):
    """What `SessionPolicy` holds for `number` in `field_name`'s unit."""
    _, unit = POLICY_FIELDS[field_name]
    if unit == "count":
        return number
    return timedelta(**{unit: number})


def _lying_settings(field_name: str, later_value: object):
    """A genuine `SessionSettings` subclass that lies **only after** construction.

    The reported threat shape, reproduced exactly: inherited `__post_init__` runs
    and observes the valid stored integer — so the object is one the settings gate
    accepted — and the *single* read `SessionPolicy.derive()` makes afterwards
    answers `later_value` instead.

    `__post_init__` is **not** overridden. A subclass that skipped validation
    would demonstrate a different and weaker defect than the one reviewed, and the
    returned read log is what lets a caller assert that construction saw the good
    value and derivation read exactly once.
    """
    reads: list[str] = []

    class LyingSettings(SessionSettings):
        __slots__ = ()

        def __getattribute__(self, name: str):
            if name == field_name:
                reads.append(name)
                if len(reads) > 1:
                    return later_value
            return super().__getattribute__(name)

    settings = LyingSettings(**dataclasses.asdict(VALID_SESSION_SETTINGS))
    assert type(settings).__post_init__ is SessionSettings.__post_init__, (
        "the subclass must inherit construction validation, not bypass it"
    )
    assert len(reads) == 1, (
        "inherited construction must have read — and validated — the stored "
        f"integer for {field_name} exactly once"
    )
    return settings, reads


def _context(account_id):
    return WebAuthorizationContext(
        account_id=account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        capabilities=frozenset({ActorCapability.GUILD_MEMBER}),
        administrator_scope=AdministratorScope.FULL,
        membership=MembershipProjection(
            guild_id=TEST_GUILD_ID,
            is_member=True,
            role_ids=frozenset(),
            observed_at=utcnow(),
        ),
    )


def _begin(composition, migrated_database, account_id, *, at):
    with migrated_database.begin() as connection:
        return composition.services(connection).session_service.begin(
            context=_context(account_id),
            now=at,
            correlation_id=uuid4(),
            oauth_transaction_id=seed_oauth_transaction(connection),
        )


def _live_session_ids(connection, account_id) -> set:
    return set(
        connection.execute(
            select(sessions.c.id).where(
                sessions.c.platform_account_id == account_id,
                sessions.c.revoked_at.is_(None),
            )
        ).scalars()
    )


# ---------------------------------------------------------------------------
# Requirement 1 — a directly constructed policy refuses every non-`int` maximum
# ---------------------------------------------------------------------------

#: The finding's own value first, then the rest of the class it belongs to. A fix
#: that patched NaN alone would pass the first case and fail the others, which is
#: the point of listing them.
NON_INTEGER_MAXIMUMS = [
    pytest.param(float("nan"), id="nan"),
    pytest.param(float("inf"), id="inf"),
    pytest.param(float("-inf"), id="-inf"),
    pytest.param(10.0, id="integral-float"),
    pytest.param(2.5, id="fractional-float"),
    pytest.param(True, id="True"),
    pytest.param(False, id="False"),
]


@pytest.mark.parametrize("value", NON_INTEGER_MAXIMUMS)
def test_a_directly_constructed_policy_refuses_a_maximum_that_is_not_an_int(value):
    """Requirement 1. `dataclasses.replace()` and direct construction, both refused.

    `float("nan")` is the reviewed counterexample; `inf` and `-inf` satisfy one
    ordering comparison each and would have been caught by the old code, while
    `10.0` and `2.5` satisfy **both** and would not. `True` and `False` are the
    reason the rule is "an `int` and not a `bool`": `bool` subclasses `int`, so
    `True` would otherwise be a maximum of one and `False` a maximum of zero.
    """
    valid = SessionPolicy.derive(VALID_SESSION_SETTINGS)

    with pytest.raises(ValueError, match="max_sessions_per_account"):
        replace(valid, max_sessions_per_account=value)

    with pytest.raises(ValueError, match="max_sessions_per_account"):
        SessionPolicy(
            ordinary_idle=timedelta(minutes=60),
            ordinary_absolute=timedelta(hours=12),
            emergency_idle=timedelta(minutes=15),
            emergency_absolute=timedelta(minutes=60),
            max_sessions_per_account=value,
        )

    # The valid policy is unharmed, so the refusals above are the value and not a
    # constructor that stopped working.
    assert valid.max_sessions_per_account == 10
    assert type(valid.max_sessions_per_account) is int


def test_the_accepted_maximum_is_an_int_so_the_session_limit_comparison_is_real():
    """Requirement 1. The property `len(live) >= maximum` depends on.

    Stated as its own case because it is the whole mechanism of the defect: the
    enforcement loop compares an `int` count against this value, and a comparison
    against a non-finite float is false for every count without raising anything.
    """
    maximum = SessionPolicy.derive(VALID_SESSION_SETTINGS).max_sessions_per_account
    assert type(maximum) is int, "a bool or float here disables N-66 silently"
    assert 10 >= maximum and 11 >= maximum, (
        "the comparison the limit is enforced by must be true for a count at or "
        "above the maximum"
    )


# ---------------------------------------------------------------------------
# Requirement 2 — the lying subclass, on `max_sessions_per_account`
# ---------------------------------------------------------------------------


def test_derivation_refuses_a_settings_subclass_that_answers_nan_after_construction():
    """Requirement 2. Codex F1/S1's reproduction, run as a regression.

    The subclass is genuine: it inherits `__post_init__`, so the settings gate saw
    a valid `10` and accepted the object. The single read `derive()` makes then
    answers NaN — and the correction refuses it there, because that gate now
    applies the same type rule rather than two ordering comparisons.

    Both halves of the reviewed claim are asserted: the field is read **exactly
    once** during derivation (so there is no second read for a property to answer
    differently), and that one read is fully validated.
    """
    settings, reads = _lying_settings("max_sessions_per_account", float("nan"))
    reads_at_construction = len(reads)

    with pytest.raises(ValueError, match="max_sessions_per_account"):
        SessionPolicy.derive(settings)

    assert len(reads) - reads_at_construction == 1, (
        "derivation must read the field exactly once: a second read is a second "
        f"answer. Reads: {reads}"
    )
    # And the lie really was live — otherwise the refusal above would prove
    # nothing about the value that reaches the policy.
    lied = settings.max_sessions_per_account
    assert lied != lied, "the subclass must actually be answering NaN by now"


# ---------------------------------------------------------------------------
# Requirement 3 — the same shape on other registered fields
# ---------------------------------------------------------------------------

#: Each is a value the **previous** validator accepted: every one satisfies both
#: `>= 1` and `<= ceiling`, and each is on a different registered field, so a
#: correction special-cased to N-66 or to NaN fails here.
WRONG_TYPES_ON_OTHER_FIELDS = [
    pytest.param("idle_minutes", 60.0, id="idle_minutes-integral-float"),
    pytest.param("emergency_idle_minutes", 15.0, id="emergency_idle-integral-float"),
    pytest.param("absolute_hours", True, id="absolute_hours-bool"),
    pytest.param(
        "emergency_absolute_minutes", float("nan"), id="emergency_absolute-nan"
    ),
]


@pytest.mark.parametrize(("field_name", "later_value"), WRONG_TYPES_ON_OTHER_FIELDS)
def test_derivation_refuses_the_lying_shape_on_every_registered_field(
    field_name, later_value
):
    """Requirement 3. The validator is shared, not a patch aimed at one field.

    `60.0`, `15.0` and `True` all pass the two ordering comparisons the reviewed
    implementation applied — `True` is `1`, which is inside every ceiling — so
    each of these was accepted before the correction and silently became a
    duration. They are refused now for the same reason NaN is: one definition of
    what these numbers may be, called by both gates.
    """
    settings, reads = _lying_settings(field_name, later_value)
    reads_at_construction = len(reads)

    with pytest.raises(ValueError, match=field_name):
        SessionPolicy.derive(settings)

    assert len(reads) - reads_at_construction == 1, (
        f"derivation must read {field_name} exactly once. Reads: {reads}"
    )


# ---------------------------------------------------------------------------
# Requirement 4 — every register field, at both boundaries
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("field_name", sorted(SESSION_CEILINGS))
def test_every_registered_field_accepts_one_and_its_ceiling_at_settings_construction(
    field_name,
):
    """Requirement 4, construction boundary. Parameterised from the register itself.

    The ceilings are read from `SESSION_CEILINGS` rather than restated here: a
    test that repeated the numbers would be a fourth copy of the register and
    could drift from it exactly as the validator did.

    Every bound is a **ceiling with a floor of 1** (S-10) — a deployment may
    tighten an accepted policy and never loosen it — so `1` and the ceiling are
    both accepted, and `0` and ceiling-plus-one are both refused.
    """
    ceiling, policy = SESSION_CEILINGS[field_name]
    assert policy.startswith("N-"), "every ceiling must cite its policy id"

    for accepted in (1, ceiling):
        settings = replace(VALID_SESSION_SETTINGS, **{field_name: accepted})
        assert getattr(settings, field_name) == accepted

    for refused in (0, ceiling + 1):
        with pytest.raises(ValueError, match=field_name):
            replace(VALID_SESSION_SETTINGS, **{field_name: refused})


@pytest.mark.parametrize("field_name", sorted(POLICY_FIELDS))
def test_every_lifetime_field_holds_the_same_bounds_at_the_derivation_boundary(
    field_name,
):
    """Requirement 4, derivation boundary. The second gate agrees with the first.

    The accepted half goes through a real `SessionSettings`, and the stored value
    is checked in the policy's own unit — proving the number that was validated is
    the number the policy carries.

    The refused half cannot go through a real `SessionSettings`, because one
    holding `0` or ceiling-plus-one is no longer constructible. It uses the lying
    subclass instead, which is the honest way to present the derivation gate with
    an out-of-register value: exactly the route the finding used.
    """
    ceiling, _ = SESSION_CEILINGS[field_name]
    attribute, _unit = POLICY_FIELDS[field_name]

    for accepted in (1, ceiling):
        policy = SessionPolicy.derive(
            replace(VALID_SESSION_SETTINGS, **{field_name: accepted})
        )
        assert getattr(policy, attribute) == _stored(field_name, accepted), (
            "the derived policy must carry the value it validated"
        )

    for refused in (0, ceiling + 1):
        settings, _ = _lying_settings(field_name, refused)
        with pytest.raises(ValueError, match=field_name):
            SessionPolicy.derive(settings)


# ---------------------------------------------------------------------------
# Requirement 5 — the environment boundary still aggregates, and still says nothing
# ---------------------------------------------------------------------------


def test_several_invalid_session_variables_raise_one_error_naming_all_and_echoing_none(
    tmp_path,
):
    """Requirement 5. One refusal, every variable named, no configured value in it.

    Two rules meet here and neither may be sacrificed for the other:

    1. **every problem is reported, not the first** — an operator fixing six
       variables should learn about all six in one attempt, which is why
       `_Reader`'s accessors record a problem and then return an *in-range*
       fallback rather than letting `SessionSettings.__post_init__` raise
       mid-collection; and
    2. **no value is ever echoed** — a `ConfigurationError` names the variable and
       never what it held, which is what makes it safe to log in full.

    Each variable is given a recognisable sentinel and the rendered error is
    searched for it. The sentinels are deliberately of both kinds: out-of-ceiling
    integers, and one that is not a number at all.
    """
    sentinels = {
        "WEB_SESSION_IDLE_MINUTES": "970001",
        "WEB_SESSION_ABSOLUTE_HOURS": "970002",
        "WEB_EMERGENCY_SESSION_IDLE_MINUTES": "970003",
        "WEB_EMERGENCY_SESSION_ABSOLUTE_MINUTES": "970004",
        "WEB_OAUTH_TRANSACTION_MINUTES": "970005",
        "WEB_MAX_SESSIONS_PER_ACCOUNT": "not-a-number-970006",
    }

    with pytest.raises(ConfigurationError) as failure:
        WebSettings.from_environment(web_environment(tmp_path, **sentinels))
    error = failure.value
    rendered = error.render()

    for variable in sentinels:
        assert variable in rendered, (
            f"{variable} must be named: an operator fixing six variables should "
            f"learn about all six in one attempt.\n{rendered}"
        )
    for variable, value in sentinels.items():
        assert value not in rendered, (
            f"the value supplied for {variable} must never be echoed.\n{rendered}"
        )
        # And not by its recognisable tail either, for the value that is not a
        # bare number.
        assert "970006" not in rendered
    assert "S-10" in error.refusals(), error.render()


def test_the_same_environment_is_accepted_when_the_session_variables_are_in_register(
    tmp_path,
):
    """Requirement 5, control. Without it the refusal above could pass vacuously."""
    settings = WebSettings.from_environment(
        web_environment(
            tmp_path,
            WEB_SESSION_IDLE_MINUTES="30",
            WEB_MAX_SESSIONS_PER_ACCOUNT="3",
        )
    )
    assert settings.session.idle_minutes == 30
    assert settings.session.max_sessions_per_account == 3


# ---------------------------------------------------------------------------
# Requirement 6 — N-66 against real PostgreSQL, at the accepted maximum of ten
# ---------------------------------------------------------------------------


def test_the_eleventh_live_session_under_a_maximum_of_ten_durably_revokes_the_oldest(
    migrated_database, composition
):
    """Requirement 6. The control the defect disabled, proved end to end.

    With a non-finite maximum, `len(live) >= maximum` was false for every count,
    so this sequence produced eleven live sessions, no revocation and no audit
    event. Every assertion below is made from a **fresh connection** after the
    creating transaction committed, so what is proved is durable state rather than
    a value the service returned.
    """
    maximum = composition.settings.session.max_sessions_per_account
    assert maximum == 10, "this case is about the accepted maximum specifically"

    with migrated_database.begin() as connection:
        account_id = make_account(connection)

    start = utcnow()
    issued = [
        _begin(
            composition,
            migrated_database,
            account_id,
            at=start + timedelta(seconds=index),
        )
        for index in range(10)
    ]

    with migrated_database.connect() as connection:
        assert _live_session_ids(connection, account_id) == {
            session.session_id for session in issued
        }, "ten sessions are inside the bound and none may be revoked yet"
        assert (
            connection.execute(
                select(audit_events.c.action).where(
                    audit_events.c.action == "auth.session.revoked"
                )
            ).all()
            == []
        )

    eleventh = _begin(
        composition, migrated_database, account_id, at=start + timedelta(seconds=11)
    )

    with migrated_database.connect() as connection:
        oldest = connection.execute(
            select(sessions).where(sessions.c.id == issued[0].session_id)
        ).mappings().one()
        live = _live_session_ids(connection, account_id)
        events = connection.execute(
            select(audit_events).where(
                audit_events.c.action == "auth.session.revoked"
            )
        ).mappings().all()

    assert oldest["revoked_at"] is not None, "the oldest live session must be revoked"
    assert oldest["revocation_reason"] == "session_limit"
    assert live == {session.session_id for session in issued[1:]} | {
        eleventh.session_id
    }, "exactly the oldest is revoked, and the eleventh is created"
    assert len(live) == maximum, "the live population must stay at the bound"

    assert len(events) == 1, "the revocation must be audited exactly once"
    assert events[0]["entity_id"] == str(issued[0].session_id)
    assert events[0]["entity_type"] == "session"
    assert events[0]["payload"]["reason"] == "session_limit"
    assert events[0]["payload"]["limit"] == maximum


# ---------------------------------------------------------------------------
# Requirement 7 — a stricter accepted maximum is the one enforced
# ---------------------------------------------------------------------------


def test_a_stricter_configured_maximum_is_enforced_exactly_and_not_a_default(
    migrated_database, tmp_path, provider
):
    """Requirement 7. Three means three — not ten, and not "some bound applied".

    S-10 lets a deployment tighten an accepted policy, so `3` is a valid
    configuration of N-66. This builds a second composition from it and shows the
    live population held at exactly three across two further logins, which
    distinguishes "the configured integer is enforced" from "the default happened
    to hold".
    """
    settings = web_settings(tmp_path, WEB_MAX_SESSIONS_PER_ACCOUNT="3")
    assert settings.session.max_sessions_per_account == 3
    strict = substituted_composition(
        settings=settings, engine=migrated_database, provider=provider
    )
    with migrated_database.connect() as connection:
        assert strict.services(connection).session_service.policy.max_sessions_per_account == 3

    with migrated_database.begin() as connection:
        account_id = make_account(connection)

    start = utcnow()
    issued = [
        _begin(strict, migrated_database, account_id, at=start + timedelta(seconds=i))
        for i in range(3)
    ]

    with migrated_database.connect() as connection:
        assert len(_live_session_ids(connection, account_id)) == 3

    fourth = _begin(
        strict, migrated_database, account_id, at=start + timedelta(seconds=4)
    )
    fifth = _begin(
        strict, migrated_database, account_id, at=start + timedelta(seconds=5)
    )

    with migrated_database.connect() as connection:
        live = _live_session_ids(connection, account_id)
        revoked = connection.execute(
            select(sessions.c.id, sessions.c.revocation_reason).where(
                sessions.c.platform_account_id == account_id,
                sessions.c.revoked_at.is_not(None),
            )
        ).mappings().all()
        limit_events = connection.execute(
            select(audit_events).where(
                audit_events.c.action == "auth.session.revoked"
            )
        ).mappings().all()

    assert live == {issued[2].session_id, fourth.session_id, fifth.session_id}, (
        "the two oldest are revoked in order, and exactly three remain live"
    )
    assert len(live) == 3 and len(live) != 10, (
        "the configured integer is enforced, not the accepted ceiling"
    )
    assert {row["id"] for row in revoked} == {
        issued[0].session_id,
        issued[1].session_id,
    }
    assert {row["revocation_reason"] for row in revoked} == {"session_limit"}
    assert len(limit_events) == 2
    assert {event["payload"]["limit"] for event in limit_events} == {3}
