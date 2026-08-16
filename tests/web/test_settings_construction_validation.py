"""TC-STRUCT-07 and TC-LIM-06: the settings types are valid by construction (RAID I-10).

`RateLimitSettings`, `BoundsSettings`, `WebAuthnSettings`, `DatabasePoolSettings`
and `WorkerSettings` were public frozen dataclasses with no construction-time
validation. `WebSettings.from_environment()` validated the *strings* it parsed
before it built them, which protects the ordinary environment-loading path and
makes no invariant of the types: direct construction, `dataclasses.replace()`
and a subclass attribute read could each produce an object outside the accepted
register, and the limiter, the body-bound middleware, the client-address policy,
WebAuthn verification, SQLAlchemy engine composition or future worker code would
then trust it.

This is not an environment-string exploit and nothing here claims one. It is the
same authority-boundary shape the session work found five times: **validation
performed by one producer is not an invariant of a public value object.**

The register is the parameterisation source. Every bound in this module comes
from `SETTINGS_NUMERIC_BOUNDS` in `application/web/config.py` rather than being
written out again, because a test that restated the numbers would be one more
copy able to drift from the definition — which is the failure the definition
exists to prevent.

**Levels.** The construction cases go through public constructors and
`dataclasses.replace()`; the aggregation case goes through
`WebSettings.from_environment()`; the consumer cases go through the limiter, the
ASGI application, the break-glass service, engine construction and the startup
checks. No case asserts an annotation, a signature or source text.
"""
from __future__ import annotations

from datetime import timedelta
from dataclasses import fields, replace
from pathlib import Path

import httpx
import pytest

from adapters.web import composition as composition_module
from adapters.web.app import create_app
from adapters.web.composition import build_engine
from adapters.web.repositories import RateLimitRepository
from application.web.capabilities import MembershipProjection
from application.web.config import (
    ACCEPTED_USER_VERIFICATION,
    SETTINGS_NUMERIC_BOUNDS,
    BoundsSettings,
    ConfigurationError,
    DatabasePoolSettings,
    RateLimitSettings,
    SessionSettings,
    SettingsAuthorityError,
    WebAuthnSettings,
    WebSettings,
    WorkerSettings,
    canonical_settings,
)
from application.web.breakglass import BreakGlassService
from application.web.rate_limit import LimitedAction, RateLimiter
from application.web.startup import build_health_view
from tests.web.composition_harness import substituted_composition
from tests.web.conftest import utcnow
from tests.web.test_session_exact_integer_policy import LyingInt
from tests.web_fixtures import TEST_GUILD_ID, web_environment, web_settings

pytestmark = pytest.mark.database


# ---------------------------------------------------------------------------
# Baselines, built from the register rather than from literals
# ---------------------------------------------------------------------------

#: The fields that are not registered numbers, with an accepted value for each.
#: Everything numeric comes from the register, so these are the only literals in
#: the module and each is a shape rather than a policy number.
NON_NUMERIC_FIELDS: dict[type, dict] = {
    SessionSettings: {
        "cookie_name": "__Host-fb_session",
        "cookie_secure": True,
        "login_transaction_cookie_name": "__Host-fb_login_txn",
    },
    WebAuthnSettings: {
        "rp_id": "portal.test",
        "rp_name": "Freedom Blades",
        "allowed_origins": ("https://portal.test",),
        "user_verification": ACCEPTED_USER_VERIFICATION,
    },
    RateLimitSettings: {},
    DatabasePoolSettings: {},
    BoundsSettings: {},
    WorkerSettings: {"enabled": False, "artifact_root": None},
}

SETTINGS_TYPES = sorted(SETTINGS_NUMERIC_BOUNDS, key=lambda cls: cls.__name__)

#: The five types RAID I-10 names. `SessionSettings` is in the register tables
#: too — it has been valid by construction since the idle-policy remediation —
#: and it rides along in the parameterised cases as a regression.
I10_TYPES = [cls for cls in SETTINGS_TYPES if cls is not SessionSettings]


def accepted_values(cls: type, **overrides) -> dict:
    """Every field of `cls` at an accepted value, from the register."""
    values = {
        name: bound.default for name, bound in SETTINGS_NUMERIC_BOUNDS[cls].items()
    }
    values.update(NON_NUMERIC_FIELDS[cls])
    values.update(overrides)
    if cls is BoundsSettings:
        # The one accepted cross-field rule (N-21) has its own cases below; here
        # it is satisfied so that a boundary case about one field is not also a
        # case about the relationship.
        values["audit_page_size_default"] = min(
            values["audit_page_size_default"], values["audit_page_size_max"]
        )
    return values


def valid(cls: type, **overrides):
    return cls(**accepted_values(cls, **overrides))


def companions(cls: type, field_name: str, value: int) -> dict:
    """The other fields a `replace()` must carry so one accepted rule is tested at a time.

    Only N-21's relationship needs one: lowering `audit_page_size_max` to its
    floor also lowers what the default may be, and a case about the *ceiling* of
    one field should not double as a case about the relationship, which has its
    own.
    """
    if cls is BoundsSettings and field_name == "audit_page_size_max":
        default = SETTINGS_NUMERIC_BOUNDS[cls]["audit_page_size_default"].default
        return {"audit_page_size_default": min(default, value)}
    return {}


def field_cases(types=None):
    """(type, field, bound) for every registered number on every type."""
    return [
        pytest.param(cls, name, bound, id=f"{cls.__name__}.{name}")
        for cls in (types or SETTINGS_TYPES)
        for name, bound in SETTINGS_NUMERIC_BOUNDS[cls].items()
    ]


def lying_subclass(instance, field_name: str, later_value):
    """A genuine subclass whose field lies **only after** construction.

    Inherited `__post_init__` runs and observes the valid stored value — so the
    object is one the construction gate accepted — and every read after the first
    answers `later_value`. `__post_init__` is not overridden: a subclass that
    skipped validation would demonstrate a weaker defect than the one recorded,
    and the returned read log is what lets a caller assert how many times a
    consumer read the field.
    """
    base = type(instance)
    reads: list[str] = []

    class Lying(base):  # type: ignore[misc, valid-type]
        __slots__ = ()

        def __getattribute__(self, name: str):
            if name == field_name:
                reads.append(name)
                if len(reads) > 1:
                    return later_value
            return super().__getattribute__(name)

    lying = Lying(
        **{field.name: getattr(instance, field.name) for field in fields(base)}
    )
    assert type(lying).__post_init__ is base.__post_init__, (
        "the subclass must inherit construction validation, not bypass it"
    )
    assert len(reads) == 1, (
        f"inherited construction must have read {field_name} exactly once, and "
        f"validated what it read. Reads: {reads}"
    )
    return lying, reads


# ---------------------------------------------------------------------------
# 1. Accepted boundaries survive, unchanged, at both construction routes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("cls", "field_name", "bound"), field_cases())
def test_both_accepted_boundaries_are_carried_exactly(cls, field_name, bound):
    """Requirement: the accepted lower and upper/exact boundaries survive unchanged.

    "Unchanged" is asserted as identity of value *and* type: a validator that
    coerced, clamped or defaulted would pass an equality check on the middle of
    the range and fail here at the edges.

    **An exact entry has one accepted value, and is exercised as one** (corrected
    2026-08-15, N-23 exact-lease remediation). `concurrency` (N-41),
    `trusted_proxy_hops` (N-34) and now `lease_seconds` (N-23) have
    `minimum == maximum`; running the same number twice under the name of two
    boundaries would report two cases where the register states one, and would
    hide the fact that the value either side of it is refused — which is
    `test_a_number_outside_the_register_is_refused`'s job and is asserted there
    for exactly these entries.
    """
    accepted = [bound.minimum]
    if bound.maximum is None:
        # N-22 states a floor and no ceiling. A large value is therefore accepted
        # rather than refused, and inventing a ceiling here would be new policy.
        accepted.append(3600)
    elif bound.maximum != bound.minimum:
        accepted.append(bound.maximum)
    else:
        assert bound.is_exact, "an entry whose bounds are equal is an exact value"

    for value in accepted:
        built = valid(cls, **{field_name: value})
        assert getattr(built, field_name) == value
        assert type(getattr(built, field_name)) is int
        # `dataclasses.replace()` is the second public construction route, and
        # applies the same rule because it runs the same `__post_init__`.
        replaced = replace(
            valid(cls), **{field_name: value}, **companions(cls, field_name, value)
        )
        assert getattr(replaced, field_name) == value


def test_a_stricter_accepted_value_is_preserved_and_not_replaced_by_a_default(tmp_path):
    """Requirement 9: configuration may tighten, and tightening must survive.

    A validator that quietly restored the accepted ceiling after checking it
    would leave every deployment on the ceiling while appearing to work. The
    check runs through the environment, which is where a default could be
    substituted.

    The worker representative is `WORKER_HEARTBEAT_SECONDS`, not
    `WORKER_LEASE_SECONDS` (corrected 2026-08-15, N-23 exact-lease remediation).
    N-23's lease is exactly 60 and therefore has nothing to tighten *to*; its
    heartbeat is the half of that sentence that states a maximum, so it is the
    honest worker case for "a stricter accepted value survives". The refused
    `WORKER_LEASE_SECONDS="30"` this case used to carry is now in
    `test_the_environment_refuses_a_lease_either_side_of_the_accepted_sixty`.
    """
    settings = WebSettings.from_environment(
        web_environment(
            tmp_path,
            WEB_RATE_LIMIT_OAUTH_STARTS="2",
            WEB_MAX_REQUEST_BYTES="4096",
            WEB_DATABASE_POOL_SIZE="1",
            WEB_RECOVERY_GRANT_MINUTES="5",
            WORKER_HEARTBEAT_SECONDS="10",
        )
    )
    assert settings.rate_limits.oauth_starts_per_ip == 2
    assert settings.bounds.max_request_bytes == 4096
    assert settings.database_pool.pool_size == 1
    assert settings.webauthn.recovery_grant_minutes == 5
    assert settings.worker.heartbeat_seconds == 10


# ---------------------------------------------------------------------------
# 2. Out-of-register numbers are refused, at both construction routes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("cls", "field_name", "bound"), field_cases())
def test_a_number_outside_the_register_is_refused(cls, field_name, bound):
    """Requirement: below the floor, and above the ceiling or not the exact value.

    `bound.minimum - 1` is the honest low case for every field: zero for a field
    whose floor is one, −1 for `max_overflow`, whose floor is zero because no
    overflow at all is a legitimate stricter deployment, and — for the three
    **exact** entries — the value one below the accepted one: 0 for `concurrency`
    and `trusted_proxy_hops`, and 59 for N-23's lease. Either side of an exact
    value is refused, because neither side is a tightening.
    """
    refused = [bound.minimum - 1]
    if bound.maximum is not None:
        refused.append(bound.maximum + 1)

    for value in refused:
        with pytest.raises(ValueError, match=field_name):
            valid(cls, **{field_name: value})
        with pytest.raises(ValueError, match=field_name):
            replace(valid(cls), **{field_name: value})


@pytest.mark.parametrize(("cls", "field_name", "bound"), field_cases())
def test_only_an_exact_built_in_int_is_accepted(cls, field_name, bound):
    """Requirement: floats, non-finite floats, `bool` and an `int` subclass refused.

    Each value is chosen so that **range** is not what refuses it: the floats and
    the lying subclass all carry an accepted number, and `True`/`False` are one
    and zero, which the reviewed session implementation accepted as "an int".
    The lying subclass is the finding that reopened this: `isinstance(value, int)`
    is true for it, and `count >= limit` asks *it* for the answer.
    """
    inside = bound.minimum
    for value in (
        float(inside),
        inside + 0.5,
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        False,
        LyingInt(inside),
    ):
        with pytest.raises(ValueError, match=field_name) as failure:
            valid(cls, **{field_name: value})
        assert field_name in str(failure.value)
        with pytest.raises(ValueError, match=field_name):
            replace(valid(cls), **{field_name: value})


# ---------------------------------------------------------------------------
# 3. The accepted non-numeric shapes, and the one accepted cross-field rule
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("overrides", "expected"),
    [
        pytest.param({"rp_id": ""}, "rp_id", id="empty-rp-id"),
        pytest.param({"rp_id": "not a host"}, "rp_id", id="rp-id-not-a-host"),
        pytest.param({"rp_id": "Portal.Test"}, "rp_id", id="rp-id-mixed-case"),
        pytest.param({"rp_id": None}, "rp_id", id="rp-id-none"),
        pytest.param({"rp_name": "  "}, "rp_name", id="blank-rp-name"),
        pytest.param({"allowed_origins": ()}, "allowed_origins", id="no-origins"),
        pytest.param(
            {"allowed_origins": ["https://portal.test"]},
            "allowed_origins",
            id="origins-not-a-tuple",
        ),
        pytest.param(
            {"allowed_origins": ("https://portal.test", "")},
            "allowed_origins",
            id="empty-origin",
        ),
        pytest.param(
            {"allowed_origins": ("https://portal.test extra",)},
            "allowed_origins",
            id="origin-with-space",
        ),
        pytest.param(
            {"user_verification": "preferred"},
            "user_verification",
            id="user-verification-preferred",
        ),
        pytest.param(
            {"user_verification": "discouraged"},
            "user_verification",
            id="user-verification-discouraged",
        ),
    ],
)
def test_webauthn_shapes_are_enforced_at_construction(overrides, expected):
    """N-60's exact user verification, and the shapes the relying party must have.

    A mixed-case relying-party identifier is refused rather than folded: the
    browser derives the identifier it presents from the origin in lowercase, so a
    mixed-case one would refuse every assertion — a fail-closed outcome, but one
    an operator would debug at 3am during the outage this route exists for.

    `user_verification` is the one enum-like field in the set. N-60 accepts
    exactly `required`; `preferred` and `discouraged` are the two values a
    plausible edit would reach for, and either would mean a break-glass
    credential presentable without user verification.
    """
    with pytest.raises(ValueError, match=expected):
        valid(WebAuthnSettings, **overrides)


@pytest.mark.parametrize(
    ("overrides", "expected"),
    [
        pytest.param({"enabled": 1}, "enabled", id="enabled-int"),
        pytest.param({"enabled": "true"}, "enabled", id="enabled-string"),
        pytest.param({"enabled": None}, "enabled", id="enabled-none"),
        pytest.param(
            {"artifact_root": Path("relative/path")}, "artifact_root", id="relative-root"
        ),
        pytest.param({"artifact_root": "/tmp"}, "artifact_root", id="root-as-string"),
    ],
)
def test_worker_shapes_are_enforced_at_construction(overrides, expected):
    """S-11's decision is a `bool`, and S-12's root is an absolute `Path` or nothing.

    A truthy value is not a decision: `WORKER_ENABLED` decides whether *this*
    process claims jobs, and S-11 exists because the deployment mistake it
    prevents — the web process executing a nine-second GIL-holding parse — is
    invisible until it happens.
    """
    with pytest.raises(ValueError, match=expected):
        valid(WorkerSettings, **overrides)


def test_the_worker_artifact_root_may_be_absent_or_absolute():
    """The accepted shapes, so the refusals above are about shape and not presence."""
    assert valid(WorkerSettings, artifact_root=None).artifact_root is None
    root = valid(WorkerSettings, artifact_root=Path("/srv/artifacts"))
    assert root.artifact_root == Path("/srv/artifacts")


def test_the_audit_default_page_size_cannot_exceed_its_maximum():
    """N-21's one accepted cross-field rule, enforced by the object owning both.

    The relationship is checked from the **same single read** of each field the
    numeric check used, so a subclass cannot satisfy the numeric rule with one
    answer and the relationship with another.
    """
    with pytest.raises(ValueError, match="audit_page_size_default"):
        BoundsSettings(
            **{
                **accepted_values(BoundsSettings),
                "audit_page_size_default": 50,
                "audit_page_size_max": 10,
            }
        )

    # Equal is accepted: the rule is "cannot exceed", not "must be smaller".
    equal = BoundsSettings(
        **{
            **accepted_values(BoundsSettings),
            "audit_page_size_default": 25,
            "audit_page_size_max": 25,
        }
    )
    assert equal.audit_page_size_default == equal.audit_page_size_max == 25

    with pytest.raises(ValueError, match="audit_page_size_default"):
        replace(valid(BoundsSettings), audit_page_size_max=10)


def test_no_relationship_is_invented_between_the_worker_or_membership_bounds():
    """The relationships that are **not** in an accepted contract are not enforced.

    N-09 and N-10 state two independent bounds and no accepted document orders
    them, so "grace must exceed the cache" is not enforced; nor is any
    relationship between N-23's lease and N-45's per-attempt cap. Writing either
    in a constructor would be new policy, and the accepted route for new policy
    is a controlled decision.

    **The worker lease/heartbeat pair is no longer an example of this**
    (corrected 2026-08-15, N-23 exact-lease remediation). It was, while this
    module read N-23 as a lease of 1…60, and the pair it accepted —
    `lease_seconds=1, heartbeat_seconds=20` — was presented as evidence that an
    ordering rule was missing. It was evidence that the *lease* bound was wrong:
    N-23 states one lease value, 60 seconds, and every accepted heartbeat is
    already far inside it. That case now lives in
    `test_the_previously_documented_counterexample_no_longer_constructs`, where
    it is refused. Nothing was added to enforce an ordering, and nothing needs
    to be.

    The two combinations below remain unusual and remain inside the register.
    """
    # Accepted, and deliberately not compared: N-45's 300-second per-attempt cap
    # exceeding N-23's 60-second lease is not a rule any accepted document
    # states, so an object holding both is built rather than refused.
    unordered_worker = valid(
        WorkerSettings, attempt_timeout_seconds=300, heartbeat_seconds=20
    )
    assert unordered_worker.attempt_timeout_seconds > unordered_worker.lease_seconds

    odd_bounds = valid(BoundsSettings, membership_cache_seconds=300)
    odd_bounds = replace(odd_bounds, membership_grace_seconds=1)
    assert odd_bounds.membership_grace_seconds < odd_bounds.membership_cache_seconds


# ---------------------------------------------------------------------------
# 3.1 N-23 — the worker lease is one value, not a range
#
# Added 2026-08-15 by the N-23 exact-lease remediation, after independent review
# found the runtime entry reading the accepted row as a ceiling.
#
# `N-23 | Job lease | 60 seconds, heartbeat at most every 20 seconds` states a
# lease *value* and a heartbeat *maximum*. Reading both halves as ceilings made
# `lease_seconds=1` an accepted configuration, which contradicts SM-05's
# `lease_expires_at = now() + 60s`, the schema's claim and renewal statements,
# and the operational contract's `N-23 + N-44` recovery bound — and would lose a
# live claim to ordinary heartbeat scheduling.
#
# Every case below takes its numbers from `WORKER_BOUNDS` except
# `test_the_accepted_n_23_lease_value_is_sixty_seconds`, which is deliberately
# the one place the accepted value is written outside the register: it is the
# binding between the runtime table and the accepted row, and a binding stated in
# terms of the thing it binds would assert nothing.
# ---------------------------------------------------------------------------

WORKER_REGISTER = SETTINGS_NUMERIC_BOUNDS[WorkerSettings]
LEASE = WORKER_REGISTER["lease_seconds"]
HEARTBEAT = WORKER_REGISTER["heartbeat_seconds"]


def test_the_accepted_n_23_lease_value_is_sixty_seconds():
    """The binding between the runtime register and the accepted N-23 row.

    Behaviour, not a table read: 60 is constructed and accepted, and 59 and 61 —
    the values either side of it — are refused. Under the reviewed `1…60` entry
    the first two of these three assertions passed and the 59 case did not, which
    is what makes this the discriminating case for the whole section.

    This is the **only** place the accepted number is written outside
    `WORKER_BOUNDS`, and it is written here on purpose. Everything else in this
    module parameterises from the register, which is right for cases about how a
    bound behaves and useless for the one case about whether the bound is the
    accepted one.
    """
    assert valid(WorkerSettings, lease_seconds=60).lease_seconds == 60
    for refused in (59, 61):
        with pytest.raises(ValueError, match="lease_seconds"):
            valid(WorkerSettings, lease_seconds=refused)


def test_the_lease_is_registered_as_an_exact_value_and_behaves_as_one():
    """Every neighbour of the accepted lease is refused, from the register alone.

    `PolicyBound.default` is the accepted value, so `default ± 1` are the two
    nearest refusals without restating a number. The refusal message must say
    *exactly*, and must cite N-23: an operator reading "between 1 and 60" would
    conclude a shorter lease was a permitted tightening, which is the reading
    this remediation exists to remove.
    """
    accepted = LEASE.default
    built = valid(WorkerSettings, lease_seconds=accepted)
    assert built.lease_seconds == accepted
    assert type(built.lease_seconds) is int

    for refused in (accepted - 1, accepted + 1):
        with pytest.raises(ValueError, match="lease_seconds") as failure:
            valid(WorkerSettings, lease_seconds=refused)
        message = str(failure.value)
        assert "exactly" in message, message
        assert LEASE.policy in message, message


@pytest.mark.parametrize(
    "refused",
    [
        pytest.param(0, id="zero"),
        pytest.param(-1, id="minus-one"),
        pytest.param(-60, id="negative-lease"),
        pytest.param(1, id="the-old-floor"),
        pytest.param(20, id="the-heartbeat-maximum"),
        pytest.param(86_400, id="a-day"),
    ],
)
def test_a_lease_that_is_not_the_accepted_value_is_refused(refused):
    """Below, above and nowhere near — one rule, not a floor and a ceiling.

    `1` is the reviewed entry's floor and `20` is the heartbeat maximum that the
    withdrawn counterexample paired it with; both were accepted leases before
    this correction and neither is one now.
    """
    with pytest.raises(ValueError, match="lease_seconds"):
        valid(WorkerSettings, lease_seconds=refused)


def test_only_an_exact_built_in_int_is_an_acceptable_lease():
    """A value carrying the accepted number is still refused unless it *is* an `int`.

    Each candidate below equals or looks like the accepted lease, so range is not
    what refuses it. `LyingInt` is the comparison-overriding subclass: a lease of
    `LyingInt(60)` would answer `False` to every ordering comparison a renewal or
    an expiry check made against it.
    """
    accepted = LEASE.default
    for value in (
        float(accepted),
        accepted + 0.5,
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        False,
        LyingInt(accepted),
    ):
        with pytest.raises(ValueError, match="lease_seconds") as failure:
            valid(WorkerSettings, lease_seconds=value)
        assert "int" in str(failure.value)


@pytest.mark.parametrize(
    "refused",
    [
        pytest.param(LEASE.default - 1, id="one-second-short"),
        pytest.param(LEASE.default + 1, id="one-second-long"),
        pytest.param(LyingInt(LEASE.default), id="comparison-overriding-subclass"),
    ],
)
def test_replacing_the_lease_on_a_valid_worker_refuses_at_construction(refused):
    """`dataclasses.replace()` is the second public construction route.

    It runs the same `__post_init__`, so a valid object cannot be edited into an
    invalid one — which is where the original I-10 finding entered.
    """
    valid_worker = valid(WorkerSettings)
    assert valid_worker.lease_seconds == LEASE.default

    with pytest.raises(ValueError, match="lease_seconds"):
        replace(valid_worker, lease_seconds=refused)


def test_the_previously_documented_counterexample_no_longer_constructs():
    """`lease_seconds=1, heartbeat_seconds=20` halts at `WorkerSettings`.

    This pair was recorded — in this module, in the submission and in the RAID
    register — as an in-register configuration proving that an ordering rule
    between the lease and the heartbeat was missing. It proved instead that the
    lease bound was wrong. It is refused now, and refused for the *lease*: the
    heartbeat it carries is the accepted maximum, so nothing here depends on an
    ordering rule and none was added.
    """
    with pytest.raises(ValueError, match="lease_seconds") as failure:
        valid(WorkerSettings, lease_seconds=1, heartbeat_seconds=HEARTBEAT.maximum)
    message = str(failure.value)
    assert "heartbeat_seconds" not in message, (
        "the heartbeat carried here is accepted; only the lease is refused, and "
        "reporting the pair would imply an ordering rule that no contract states"
        f"\n{message}"
    )


def test_the_accepted_heartbeat_boundaries_are_unchanged():
    """N-23's *other* half is still a ceiling with a floor of one.

    The lease became exact; the heartbeat did not, because "at most every 20
    seconds" is a maximum in the same sentence that gives the lease as a value.
    Both accepted boundaries survive and both neighbours are refused.
    """
    for accepted in (HEARTBEAT.minimum, HEARTBEAT.maximum):
        built = valid(WorkerSettings, heartbeat_seconds=accepted)
        assert built.heartbeat_seconds == accepted
        assert built.lease_seconds == LEASE.default

    for refused in (HEARTBEAT.minimum - 1, HEARTBEAT.maximum + 1):
        with pytest.raises(ValueError, match="heartbeat_seconds"):
            valid(WorkerSettings, heartbeat_seconds=refused)


def test_a_worker_whose_lease_lies_on_a_later_read_is_refused_by_canonicalisation():
    """The consumer-side half, on the field this remediation corrected.

    A subclass that stores the accepted lease and answers something else on every
    later read passes its inherited construction gate. `canonical_settings` reads
    each field once and rebuilds the base type, so the lie is refused there
    rather than reaching a renewal that would compute `now() + lease`.
    """
    lying, reads = lying_subclass(valid(WorkerSettings), "lease_seconds", 1)
    reads_at_construction = len(reads)

    with pytest.raises(ValueError, match="lease_seconds"):
        canonical_settings(lying, WorkerSettings)

    assert len(reads) - reads_at_construction == 1, (
        f"canonicalisation must read the lease exactly once. Reads: {reads}"
    )

    rebuilt = canonical_settings(valid(WorkerSettings), WorkerSettings)
    assert type(rebuilt) is WorkerSettings
    assert rebuilt.lease_seconds == LEASE.default


def test_the_environment_accepts_an_unset_lease_as_the_registered_value(tmp_path):
    """An unset variable means the accepted value, taken from the register.

    `web_environment` sets no `WORKER_LEASE_SECONDS`, so this is the ordinary
    deployment case: the reader returns `PolicyBound.default`, which for an exact
    entry is the one accepted value rather than a ceiling to sit on.
    """
    settings = web_settings(tmp_path)
    assert settings.worker.lease_seconds == LEASE.default
    assert type(settings.worker.lease_seconds) is int


def test_the_environment_accepts_the_accepted_lease_written_out(tmp_path):
    """`.env.example` ships `WORKER_LEASE_SECONDS=60`, and it must still start.

    An operator who states the accepted value explicitly must not be refused for
    agreeing with the register.
    """
    settings = web_settings(tmp_path, WORKER_LEASE_SECONDS=str(LEASE.default))
    assert settings.worker.lease_seconds == LEASE.default


@pytest.mark.parametrize(
    "supplied",
    [
        pytest.param(str(LEASE.default - 1), id="fifty-nine"),
        pytest.param(str(LEASE.default + 1), id="sixty-one"),
    ],
)
def test_the_environment_refuses_a_lease_either_side_of_the_accepted_sixty(
    tmp_path, supplied
):
    """S-10's exact-value semantics at the environment boundary.

    Either side of an exact value buys something the register does not grant, so
    both are `S-10` rather than one being a mere malformation. The variable is
    named because an operator has to know what to change; the supplied value is
    absent because a `ConfigurationError` is safe to log in full only if it never
    carries what a variable held.
    """
    with pytest.raises(ConfigurationError) as failure:
        WebSettings.from_environment(
            web_environment(tmp_path, WORKER_LEASE_SECONDS=supplied)
        )
    error = failure.value
    rendered = error.render()

    assert "WORKER_LEASE_SECONDS" in rendered, rendered
    assert supplied not in rendered, (
        f"the supplied lease must never be echoed.\n{rendered}"
    )
    assert "S-10" in error.refusals(), rendered
    assert "exactly" in rendered and LEASE.policy in rendered, rendered


def test_an_invalid_lease_still_aggregates_with_other_types(tmp_path):
    """One `ConfigurationError`, not the first problem — with the corrected lease.

    The reader records the lease problem and falls back to the accepted value so
    that `WorkerSettings.__post_init__` cannot raise mid-collection and cost the
    operator the rest of the list. A `ValueError` escaping here instead of a
    `ConfigurationError` would fail this block.
    """
    sentinels = {
        "WEB_RATE_LIMIT_OAUTH_STARTS": "980401",
        "WEB_DATABASE_POOL_SIZE": "980402",
    }
    with pytest.raises(ConfigurationError) as failure:
        WebSettings.from_environment(
            web_environment(
                tmp_path,
                WORKER_LEASE_SECONDS=str(LEASE.default - 1),
                **sentinels,
            )
        )
    error = failure.value
    rendered = error.render()

    for variable, value in sentinels.items():
        assert variable in rendered, rendered
        assert value not in rendered, rendered
    assert "WORKER_LEASE_SECONDS" in rendered, rendered
    assert len(error.problems) >= 3, (
        f"each invalid variable must contribute its own problem.\n{rendered}"
    )


# ---------------------------------------------------------------------------
# 4. A later subclass read, at every seam that reads a settings value again
# ---------------------------------------------------------------------------


def test_the_engine_is_never_built_from_a_pool_that_lies(tmp_path, monkeypatch):
    """`build_engine` reads each pool number once and validates that read.

    The seam is `create_engine` in the composition module, replaced with a spy so
    the arguments can be inspected without opening a connection. Two properties
    are proved: the validated numbers are passed **exactly**, and an invalid pool
    never reaches SQLAlchemy at all — the spy is not called a second time.
    """
    calls: list[tuple] = []

    def spy(url, **kwargs):
        calls.append((url, kwargs))
        return object()

    monkeypatch.setattr(composition_module, "create_engine", spy)
    settings = web_settings(
        tmp_path,
        WEB_DATABASE_POOL_SIZE="3",
        WEB_DATABASE_MAX_OVERFLOW="2",
        WEB_DATABASE_TIMEOUT_SECONDS="4",
        WEB_DATABASE_STATEMENT_TIMEOUT_MS="7500",
    )

    build_engine(settings)
    assert len(calls) == 1
    _url, kwargs = calls[0]
    assert kwargs["pool_size"] == 3
    assert kwargs["max_overflow"] == 2
    assert kwargs["pool_timeout"] == 4
    assert kwargs["connect_args"]["options"] == "-c statement_timeout=7500"

    lying_pool, reads = lying_subclass(settings.database_pool, "pool_size", 500)
    reads_at_construction = len(reads)
    with pytest.raises(ValueError, match="pool_size"):
        build_engine(replace(settings, database_pool=lying_pool))

    assert len(calls) == 1, "an invalid pool must never reach SQLAlchemy"
    assert len(reads) - reads_at_construction == 1, (
        f"engine composition must read pool_size exactly once. Reads: {reads}"
    )


def test_the_limiter_is_never_built_from_budgets_that_lie(migrated_database, settings):
    """`RateLimiter` reads its nine budgets once, at construction, and checks them.

    Before the correction it kept whatever it was handed and re-read a budget on
    every check, so a subclass could answer an accepted number when it was looked
    at and something else when it was used — one request at a time, invisibly.
    """
    lying, reads = lying_subclass(settings.rate_limits, "oauth_starts_per_ip", 10_000)
    reads_at_construction = len(reads)

    with migrated_database.begin() as connection:
        with pytest.raises(ValueError, match="oauth_starts_per_ip"):
            RateLimiter(
                RateLimitRepository(connection), lying, settings.client_digest_key
            )

    assert len(reads) - reads_at_construction == 1, (
        f"the limiter must read each budget exactly once. Reads: {reads}"
    )


def test_the_application_is_never_built_from_bounds_that_lie(
    settings, composition, migrated_database
):
    """`create_app` reads the request bounds once, before either becomes a control.

    Rewritten 2026-08-16 for the canonical-graph correction: the read now happens
    at the composition root rather than in the factory, and `create_app` no longer
    accepts a settings graph *beside* a composition, so the lying bounds are
    supplied as the factory's one authority. What is asserted is unchanged — the
    bound is read exactly once, and the refusal happens before anything holds it.
    """
    lying, reads = lying_subclass(settings.bounds, "max_request_bytes", 64 * 1024 * 1024)
    reads_at_construction = len(reads)

    with pytest.raises(ValueError, match="max_request_bytes"):
        create_app(replace(settings, bounds=lying), run_startup_checks=False)

    assert len(reads) - reads_at_construction == 1, (
        f"application composition must read the bound exactly once. Reads: {reads}"
    )


def test_the_break_glass_service_is_never_built_from_a_relying_party_that_lies(
    settings, composition, migrated_database, provider
):
    """The relying party is read once, at composition, and checked as it is read.

    It was previously re-read from the settings tree on every assertion and every
    verification, so an identifier could be one value when the challenge was
    minted and another when the response was verified — which is the credential
    scope moving out from under a verification that had already passed.

    **Rewritten 2026-08-16 for the canonical-graph correction.** The read moved
    one layer up: the service no longer rebuilds `settings.webauthn` itself, it
    requires the canonical graph and holds the exact-base object that graph
    already carries. So the lying subclass is now offered where a graph is built
    — the composition root — and the service is built from the composition that
    survives, which is the only way it can now be built at all. The two
    properties asserted are unchanged: the identifier is read exactly once, and
    what the service holds is the base type.
    """
    def compose(webauthn):
        return substituted_composition(
            settings=replace(settings, webauthn=webauthn),
            engine=migrated_database,
            provider=provider,
        )

    malformed, malformed_reads = lying_subclass(settings.webauthn, "rp_id", "not a host")
    plausible, plausible_reads = lying_subclass(
        settings.webauthn, "rp_id", "elsewhere.test"
    )

    with pytest.raises(ValueError, match="rp_id"):
        compose(malformed)
    # A lie that is still *shaped* like a relying party is not refused, and
    # nothing here pretends otherwise: whether an identifier is the **right**
    # one is S-09's question, answered against the public origin, which this
    # type does not carry. What the seam guarantees is the property the
    # finding was about — the identifier is read once, so the challenge and
    # the verification cannot see two different ones.
    plausible_composition = compose(plausible)
    with migrated_database.connect() as connection:
        service = plausible_composition.services(connection).break_glass
        held = service._webauthn  # noqa: SLF001 - the value under test

    assert len(malformed_reads) == 2, (
        f"composition must read the relying party exactly once. {malformed_reads}"
    )
    assert len(plausible_reads) == 2, plausible_reads
    assert type(held) is WebAuthnSettings, (
        "the service must hold the base type, so no later read can answer again"
    )
    assert held.rp_id == "elsewhere.test"
    assert held is plausible_composition.settings.webauthn, (
        "and it must be the canonical graph's object, not a second copy of it"
    )
    # A service built from anything else refuses, so the property above is not a
    # convention the composition root happens to follow.
    with migrated_database.connect() as connection:
        services = plausible_composition.services(connection)
        with pytest.raises(SettingsAuthorityError, match="BreakGlassService"):
            BreakGlassService(
                accounts=services.accounts,
                webauthn_repository=services.credentials,
                recovery_grants=services.grants,
                session_service=services.session_service,
                audit=services.audit,
                settings=replace(settings, webauthn=plausible),
            )


def test_the_startup_checks_are_never_run_against_a_worker_root_that_lies(
    settings, composition, migrated_database
):
    """The artifact root proved ready must be the root the store is opened on."""
    lying, reads = lying_subclass(
        settings.worker, "artifact_root", Path("relative/elsewhere")
    )
    reads_at_construction = len(reads)

    with pytest.raises(ValueError, match="artifact_root"):
        build_health_view(
            replace(settings, worker=lying),
            engine=composition.engine,
            provider_ok=True,
        )

    assert len(reads) - reads_at_construction == 1, (
        f"the health view must read the root exactly once. Reads: {reads}"
    )


@pytest.mark.parametrize("cls", I10_TYPES, ids=lambda cls: cls.__name__)
def test_canonicalisation_refuses_a_duck_type_and_returns_the_base_type(cls):
    """The seam itself: it takes the type whose constructor holds the register.

    A duck type would be a way to supply values that never met the register, and
    what comes back must be an ordinary instance of the base type — not the
    subclass — so that every later read of it answers the value that was checked.
    """
    instance = valid(cls)

    class Duck:
        pass

    with pytest.raises(TypeError, match=cls.__name__):
        canonical_settings(Duck(), cls)

    lying, _reads = lying_subclass(
        instance, next(iter(SETTINGS_NUMERIC_BOUNDS[cls])), 10**9
    )
    with pytest.raises(ValueError):
        canonical_settings(lying, cls)

    rebuilt = canonical_settings(instance, cls)
    assert type(rebuilt) is cls
    assert rebuilt == instance


# ---------------------------------------------------------------------------
# 5. The environment boundary still aggregates, and still echoes nothing
# ---------------------------------------------------------------------------


def test_invalid_variables_across_several_types_raise_one_redacted_error(tmp_path):
    """Requirement 7: one `ConfigurationError`, every variable, no value, no `ValueError`.

    Seven variables spanning four of the five types are made invalid at once. All
    three rules meet here and none may be sacrificed for the others:

    1. **one error, not the first problem** — an operator fixing seven variables
       should learn about all seven in one attempt, which is why the reader
       records a problem and then falls back to the accepted value rather than
       letting a dataclass constructor raise mid-collection;
    2. **no value is ever echoed** — each sentinel is recognisable and none of
       them may appear in the rendered error; and
    3. **the error is the typed one** — a `ValueError` escaping from a settings
       constructor would be an unhandled crash at startup rather than the typed
       refusal an operator can read, and would leave this `pytest.raises` block
       failing with that `ValueError` instead.
    """
    sentinels = {
        "WEB_RATE_LIMIT_OAUTH_STARTS": "970201",
        "WEB_RATE_LIMIT_CLEANUP_MINUTES": "970202",
        "WEB_MAX_REQUEST_BYTES": "97020300",
        "WEB_TRUSTED_PROXY_HOPS": "970204",
        "WEB_RECOVERY_GRANT_MINUTES": "970205",
        "WEB_DATABASE_POOL_SIZE": "970206",
        "WORKER_LEASE_SECONDS": "970207",
    }

    with pytest.raises(ConfigurationError) as failure:
        WebSettings.from_environment(web_environment(tmp_path, **sentinels))
    error = failure.value
    rendered = error.render()

    for variable, value in sentinels.items():
        assert variable in rendered, f"{variable} must be named.\n{rendered}"
        assert value not in rendered, (
            f"the value supplied for {variable} must never be echoed.\n{rendered}"
        )
    assert "S-10" in error.refusals(), rendered
    assert len(error.problems) >= len(sentinels), (
        "each invalid variable must contribute its own problem, not be summarised"
    )


def test_a_malformed_relying_party_and_origin_still_aggregate(tmp_path):
    """The shape refusals are subject to the same rule as the numeric ones.

    `WebAuthnSettings` now refuses these at construction, so the reader must
    substitute an accepted placeholder after recording the problem. If it did
    not, the first bad shape would abort the collection and the operator would
    never learn about the second.
    """
    with pytest.raises(ConfigurationError) as failure:
        WebSettings.from_environment(
            web_environment(
                tmp_path,
                WEB_WEBAUTHN_RP_ID="not a host",
                WEB_WEBAUTHN_USER_VERIFICATION="preferred",
                WEB_RATE_LIMIT_OAUTH_STARTS="970301",
            )
        )
    rendered = failure.value.render()
    for variable in (
        "WEB_WEBAUTHN_RP_ID",
        "WEB_WEBAUTHN_USER_VERIFICATION",
        "WEB_RATE_LIMIT_OAUTH_STARTS",
    ):
        assert variable in rendered, rendered
    assert "970301" not in rendered
    assert "not a host" not in rendered


def test_a_valid_environment_is_still_accepted_and_carries_the_register(tmp_path):
    """Control. Without it every refusal above could be passing vacuously."""
    settings = web_settings(tmp_path)
    for cls, attribute in (
        (RateLimitSettings, "rate_limits"),
        (BoundsSettings, "bounds"),
        (WebAuthnSettings, "webauthn"),
        (DatabasePoolSettings, "database_pool"),
        (WorkerSettings, "worker"),
    ):
        held = getattr(settings, attribute)
        assert type(held) is cls
        for name, bound in SETTINGS_NUMERIC_BOUNDS[cls].items():
            value = getattr(held, name)
            assert type(value) is int
            assert bound.minimum <= value
            assert bound.maximum is None or value <= bound.maximum


# ---------------------------------------------------------------------------
# 6. Consumer evidence — TC-LIM-06
# ---------------------------------------------------------------------------


def _limiter(connection, settings, rate_limits=None):
    return RateLimiter(
        RateLimitRepository(connection),
        rate_limits if rate_limits is not None else settings.rate_limits,
        settings.client_digest_key,
    )


def test_the_limiter_spends_exactly_the_configured_ip_budget(
    migrated_database, settings
):
    """TC-LIM-06, `RateLimitSettings` → IP decisions. N-18, N-32 and N-33.

    Each of the three per-address budgets is spent to its exact accepted value
    and one further attempt is refused, so the numbers the limiter enforces are
    the configured ones rather than a shared default.
    """
    now = utcnow()
    budgets = {
        LimitedAction.OAUTH_START: settings.rate_limits.oauth_starts_per_ip,
        LimitedAction.OAUTH_CALLBACK: settings.rate_limits.oauth_callbacks_per_ip,
        LimitedAction.WEBAUTHN_ASSERTION: settings.rate_limits.webauthn_assertions_per_ip,
        LimitedAction.RECOVERY_LOGIN: settings.rate_limits.recovery_attempts_per_ip,
    }
    with migrated_database.begin() as connection:
        limiter = _limiter(connection, settings)
        for action, budget in budgets.items():
            address = f"203.0.113.{list(budgets).index(action) + 20}"
            decisions = [
                limiter.check_ip(action, client_ip=address, now=now)
                for _ in range(budget + 1)
            ]
            assert all(decision.allowed for decision in decisions[:budget]), action
            assert decisions[-1].allowed is False, action
            assert decisions[-1].limit == budget
            # The retry hint is bounded by the configured window, not by a
            # hard-coded ten minutes.
            assert 0 < decisions[-1].retry_after_seconds <= (
                settings.rate_limits.window_minutes * 60
            )


def test_the_limiter_spends_exactly_the_configured_account_budget(
    migrated_database, settings
):
    """TC-LIM-06, `RateLimitSettings` → N-32's second, per-account budget.

    The *route* consumer evidence for this budget is TC-BG-16 (2026-08-16, P3.G1
    security review): this case proves the configured number is the one spent,
    and that one proves a WebAuthn request reaches it.
    """
    now = utcnow()
    budget = settings.rate_limits.webauthn_assertions_per_account
    with migrated_database.begin() as connection:
        limiter = _limiter(connection, settings)
        decisions = [
            limiter.check_account(
                LimitedAction.WEBAUTHN_ASSERTION, account_id="account-1", now=now
            )
            for _ in range(budget + 1)
        ]
    assert all(decision.allowed for decision in decisions[:budget])
    assert decisions[-1].allowed is False
    assert decisions[-1].limit == budget


def test_an_unresolved_credential_spends_the_same_configured_budget(
    migrated_database, settings
):
    """TC-LIM-06, `RateLimitSettings` → N-32's budget for an unknown credential.

    The same configured number and the same configured window, so the attempt at
    which a caller is refused cannot tell them whether the credential they
    presented is enrolled.
    """
    now = utcnow()
    budget = settings.rate_limits.webauthn_assertions_per_account
    with migrated_database.begin() as connection:
        limiter = _limiter(connection, settings)
        decisions = [
            limiter.check_credential(
                LimitedAction.WEBAUTHN_ASSERTION,
                credential_id=b"never-enrolled-000001",
                now=now,
            )
            for _ in range(budget + 1)
        ]
    assert all(decision.allowed for decision in decisions[:budget])
    assert decisions[-1].allowed is False
    assert decisions[-1].limit == budget
    assert decisions[-1].retry_after_seconds <= (
        settings.rate_limits.webauthn_account_window_minutes * 60
    )


def test_a_stricter_configured_budget_is_the_one_the_limiter_enforces(
    migrated_database, settings
):
    """TC-LIM-06. Two means two — not ten, and not "some budget applied".

    S-10 permits tightening, so a limiter built from a stricter accepted setting
    must spend that number exactly. This is what distinguishes "the configured
    integer is enforced" from "the ceiling happened to hold".
    """
    strict = replace(settings.rate_limits, oauth_starts_per_ip=2)
    now = utcnow()
    with migrated_database.begin() as connection:
        limiter = _limiter(connection, settings, rate_limits=strict)
        decisions = [
            limiter.check_ip(
                LimitedAction.OAUTH_START, client_ip="203.0.113.77", now=now
            )
            for _ in range(3)
        ]
    assert [decision.allowed for decision in decisions] == [True, True, False]
    assert decisions[-1].limit == 2 != settings.rate_limits.oauth_starts_per_ip


def test_the_recovery_grant_attempt_cap_the_service_reads_is_the_validated_one(
    settings, composition, migrated_database
):
    """TC-LIM-06, `RateLimitSettings` → N-33's per-grant cap at its real consumer."""
    with migrated_database.connect() as connection:
        service = composition.services(connection).break_glass
        held = service._rate_limits  # noqa: SLF001 - the value under test
    assert type(held) is RateLimitSettings
    assert held.recovery_attempts_per_grant == (
        settings.rate_limits.recovery_attempts_per_grant
    )


async def test_the_body_bound_middleware_applies_the_configured_limit(
    settings, composition
):
    """TC-LIM-06, `BoundsSettings` → N-19 at the middleware that enforces it.

    A stricter accepted bound is configured and a body just over it is refused
    `413` **before routing**, while a body just under it is not — proving the
    number the middleware holds is the configured one and not the 1 MiB ceiling.
    """
    strict = replace(settings, bounds=replace(settings.bounds, max_request_bytes=4096))
    # One authority (2026-08-16): the stricter graph is what the composition is
    # built from, rather than a second graph handed to the factory beside a
    # composition built from something else.
    app = create_app(
        composition=substituted_composition(
            settings=strict,
            engine=composition.engine,
            # The fixture's double, which carries no Discord configuration. A
            # real provider cannot be passed between compositions at all: the
            # production constructor has no provider parameter, and this
            # substitution path is `tests/web/composition_harness.py`
            # (2026-08-16, P3.G1 provider/engine authority remediation).
            provider=composition.provider,
        ),
        run_startup_checks=False,
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="https://portal.test", follow_redirects=False
    ) as client:
        too_large = await client.post("/v1/anything", content=b"x" * 4097)
        acceptable = await client.post("/v1/anything", content=b"x" * 4000)

    assert too_large.status_code == 413
    assert acceptable.status_code != 413


def test_the_client_address_policy_holds_the_exact_accepted_hop_count(
    settings, composition
):
    """TC-LIM-06, `BoundsSettings` → N-34 at the object that interprets the header."""
    app = create_app(composition=composition, run_startup_checks=False)
    assert app.state.address_policy.trusted_hops == settings.bounds.trusted_proxy_hops
    assert app.state.address_policy.trusted_hops == 1


def test_the_membership_bounds_are_validated_but_have_no_p3_1_route_consumer(settings):
    """TC-LIM-06, `BoundsSettings` → N-09/N-10, reported honestly.

    `MembershipProjection.is_fresh` and `within_grace` take the two bounds as
    arguments and apply them exactly, which this proves. **No P3.1 route calls
    either**: the projection freshness decision belongs to the protected-route
    surface, which is P3.2's package. Claiming a consumer that does not exist
    would be the kind of evidence this remediation was written to stop, so what
    is claimed here is what is true — the numbers are in register at
    construction, and the helper that will read them honours them.
    """
    now = utcnow()
    cache = settings.bounds.membership_cache_seconds
    grace = settings.bounds.membership_grace_seconds
    projection = MembershipProjection(
        guild_id=TEST_GUILD_ID,
        is_member=True,
        role_ids=frozenset(),
        observed_at=now,
    )
    assert projection.is_fresh(now=now, cache_seconds=cache)
    assert projection.within_grace(now=now, grace_seconds=grace)

    stale = MembershipProjection(
        guild_id=TEST_GUILD_ID,
        is_member=True,
        role_ids=frozenset(),
        observed_at=now - timedelta(seconds=cache + 1),
    )
    assert not stale.is_fresh(now=now, cache_seconds=cache)
    assert stale.within_grace(now=now, grace_seconds=grace)

    expired = MembershipProjection(
        guild_id=TEST_GUILD_ID,
        is_member=True,
        role_ids=frozenset(),
        observed_at=now - timedelta(seconds=grace + 1),
    )
    assert not expired.within_grace(now=now, grace_seconds=grace)


def test_the_audit_page_and_polling_bounds_have_no_p3_1_consumer_at_all(settings):
    """TC-LIM-06, `BoundsSettings` → N-21/N-22, reported as absent.

    Audit pagination and the polling floor are read by no P3.1 code: the audit
    surface and the reconciliation poll are P3.2 and P3.3 routes. Their bounds
    are enforced at construction now — which is the I-10 requirement — and their
    consumer evidence is an obligation of the package that adds the consumer, not
    something this package may manufacture by writing one.
    """
    assert settings.bounds.audit_page_size_default <= settings.bounds.audit_page_size_max
    assert settings.bounds.poll_min_seconds >= 2


async def test_the_challenge_carries_the_configured_relying_party(
    settings, composition, migrated_database
):
    """TC-LIM-06, `WebAuthnSettings` → the relying party the browser is asked for.

    N-60 requires user verification, and the options the service mints must name
    the configured relying party. Both are asserted on the payload the route
    would return, which is the value that actually reaches the authenticator.
    """
    with migrated_database.begin() as connection:
        options = composition.services(connection).break_glass.begin_assertion(
            now=utcnow(), client_ip_hash=None
        )
    assert options.payload["rpId"] == settings.webauthn.rp_id
    assert options.payload["userVerification"] == ACCEPTED_USER_VERIFICATION
    assert settings.webauthn.user_verification == ACCEPTED_USER_VERIFICATION


def test_the_verification_origins_are_the_configured_ones(
    settings, composition, migrated_database
):
    """TC-LIM-06, `WebAuthnSettings` → the exact origins verification will accept.

    The service holds the validated tuple, and it is the same set the environment
    produced. An assertion presented from any other origin is refused by
    `verify_authentication_response`, whose failure boundary the break-glass
    login suite exercises; what is proved here is that the origins it is given
    are the accepted ones.
    """
    with migrated_database.connect() as connection:
        service = composition.services(connection).break_glass
        held = service._webauthn  # noqa: SLF001 - the value under test
    assert type(held) is WebAuthnSettings
    assert held.allowed_origins == settings.webauthn.allowed_origins
    assert held.rp_id == settings.webauthn.rp_id


def test_the_recovery_grant_lifetime_is_bounded_but_read_by_no_runtime_consumer(
    settings,
):
    """TC-LIM-06, `WebAuthnSettings` → N-14, reported honestly.

    `WEB_RECOVERY_GRANT_MINUTES` is validated here and at the environment
    boundary, and **no runtime code reads it**: `tools/emergency_recovery.py`
    issues grants from its own `GRANT_MINUTES = 10`, which is N-14's accepted
    value written in the operator command rather than taken from configuration.
    That divergence is pre-existing, is not a policy conflict — both are ten —
    and correcting it would change an operator contract this remediation was not
    scoped to touch. It is recorded here and in the submission so the next
    package that touches the recovery path resolves it deliberately.
    """
    from tools.emergency_recovery import GRANT_MINUTES

    assert settings.webauthn.recovery_grant_minutes == 10
    assert GRANT_MINUTES == 10


def test_the_worker_bounds_are_valid_now_and_their_consumers_are_a_p3_3_obligation(
    settings,
):
    """TC-LIM-06, `WorkerSettings` → what P3.1 owns, and what it does not.

    P3.1 reads exactly two of these fields: `enabled`, which S-11 refuses when a
    web process claims jobs, and `artifact_root`, which the S-12 startup check
    proves ready. The lease, heartbeat, attempt, timeout and queue bounds have no
    consumer in this package, and **P3.3 owns their consumer evidence** — the
    claim statement, the heartbeat, the reaper and the attempt cap. Implementing
    any of that here to produce evidence would be starting a package that has not
    been authorised.
    """
    assert settings.worker.enabled is False
    for name, bound in SETTINGS_NUMERIC_BOUNDS[WorkerSettings].items():
        value = getattr(settings.worker, name)
        assert type(value) is int
        assert bound.minimum <= value <= (bound.maximum or value)


def test_a_web_process_that_claims_jobs_still_refuses_to_start(tmp_path):
    """TC-LIM-06, `WorkerSettings` → S-11, the one worker control P3.1 enforces."""
    with pytest.raises(ConfigurationError) as failure:
        WebSettings.from_environment(web_environment(tmp_path, WORKER_ENABLED="true"))
    assert "S-11" in failure.value.refusals()
