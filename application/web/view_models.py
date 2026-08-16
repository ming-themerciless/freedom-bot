"""Version `vm-1` view models: the whole contract between backend and template.

Every type here is a frozen, slotted dataclass holding tuples and enums. That is
not a style preference — it is four rules from the accepted view-model contract,
stated where they are enforced:

1. **Typed and frozen.** A template cannot mutate what it was given, and a
   service cannot hand a template a `dict` whose keys nobody agreed to.
2. **Bounded.** Every sequence has a stated maximum and a `truncated` flag. An
   unbounded render is an availability defect on a host shared with three Foundry
   instances and the live bot (RAID R-24).
3. **Pre-authorized.** A view model contains only what its caller is already
   entitled to see. Templates perform no authorization and receive no data they
   must remember to hide.
4. **Presentation-safe.** No token, no authenticator secret, no recovery token,
   no exception text, no SQL, no path, no raw artifact byte reaches any field of
   any view model, ever.

**This module implements the P3.1-owned subset**: VM-01 to VM-04 (login,
non-member, degraded, emergency), VM-16 (health) and the cross-cutting VM-19,
VM-20 and VM-21. VM-05 to VM-15, VM-17 and VM-18 belong to P3.2 and P3.3 and are
deliberately absent rather than stubbed — a stub would be a contract the
frontend could start depending on before its authorization was written.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID

from application.audit import ActorCapability

#: The version identifier the whole set carries. A change that removes a field,
#: renames one or narrows an enum is **breaking** and returns through P3.G2/G3.
#: Adding an optional field is additive and does not.
VIEW_MODEL_VERSION = "vm-1"

PageState = Literal["ready", "empty", "loading", "stale", "denied", "invalid", "error"]

#: §3.2's bounds on text that originated outside the platform. A value longer
#: than its bound is truncated **and says so**; the untruncated value is never
#: sent.
DISCORD_NAME_BOUND = 80
ACTOR_NAME_BOUND = 120
CHARACTER_LONG_NAME_BOUND = 240
REASON_BOUND = 500


@dataclass(frozen=True, slots=True)
class SafeText:
    """External text, bounded at construction and escaped at render.

    Bounding here rather than in the template is what makes the bound a property
    of the response instead of a property of one Jinja filter somebody remembered
    to apply.
    """

    value: str
    truncated: bool = False

    @classmethod
    def bounded(cls, raw: str | None, limit: int) -> "SafeText":
        text = raw or ""
        if len(text) <= limit:
            return cls(value=text, truncated=False)
        return cls(value=text[:limit], truncated=True)


@dataclass(frozen=True, slots=True)
class Instant:
    """Always UTC, always ISO-8601 in the machine field.

    Templates never compute a timezone: a template that formatted a time would be
    a second place for "what time is it here" to be answered differently.
    """

    iso_utc: str
    display: str

    @classmethod
    def of(cls, moment: datetime) -> "Instant":
        utc = moment.astimezone(tz=None) if moment.tzinfo is None else moment
        return cls(
            iso_utc=utc.isoformat(),
            display=utc.strftime("%Y-%m-%d %H:%M UTC"),
        )


@dataclass(frozen=True, slots=True)
class Correlation:
    """The one identifier a user may quote to an operator (N-25)."""

    id: UUID


@dataclass(frozen=True, slots=True)
class Actor:
    """Who did something. **Never** a Discord snowflake in a member-facing view."""

    account_id: UUID
    label: SafeText
    capability: ActorCapability


@dataclass(frozen=True, slots=True)
class Cursor:
    """Opaque and HMAC-signed (N-64). Never an offset."""

    token: str
    has_more: bool


class DenialCategory(Enum):
    """A closed vocabulary. Free-text denial reasons leak."""

    NOT_AUTHENTICATED = "not_authenticated"
    NOT_A_MEMBER = "not_a_member"
    INSUFFICIENT_CAPABILITY = "insufficient_capability"
    NOT_AVAILABLE = "not_available"
    EMERGENCY_SESSION_RESTRICTED = "emergency_session_restricted"
    SERVICE_DEGRADED = "service_degraded"


@dataclass(frozen=True, slots=True)
class DeniedReason:
    category: DenialCategory


@dataclass(frozen=True, slots=True)
class MigrationDeferred:
    """Rendered wherever a legacy field would otherwise appear.

    `owning_package` is read from the controlled migration manifest, never typed
    by hand, and this type deliberately has **no value field**: a deferred field
    cannot carry a value, so the type makes that unrepresentable rather than
    relying on a template not to print one.
    """

    field_key: str
    owning_package: str


# ---------------------------------------------------------------------------
# VM-01 `LoginPageView` — R-02
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ProviderOption:
    key: str
    display_name: str
    #: A **path**, so a template cannot be tricked into rendering an off-site
    #: login button.
    start_path: str
    enabled: bool


@dataclass(frozen=True, slots=True)
class DegradedProvider:
    provider_key: str
    since: Instant
    message_code: str


LoginFailureCode = Literal[
    "transaction_expired",
    "transaction_unknown",
    "state_mismatch",
    "provider_error",
    "rate_limited",
    "not_available",
]


@dataclass(frozen=True, slots=True)
class LoginFailure:
    """A code and a correlation id — **never** the provider's error string (N-25)."""

    code: LoginFailureCode
    correlation: Correlation


@dataclass(frozen=True, slots=True)
class LoginPageView:
    state: PageState
    providers: tuple[ProviderOption, ...]
    #: A **configuration** fact, not an account fact. The page must not reveal
    #: whether a credential is enrolled for anyone.
    emergency_access_available: bool
    degraded: DegradedProvider | None = None
    failure: LoginFailure | None = None


# ---------------------------------------------------------------------------
# VM-02 `NonMemberView` — R-04's rejection, and caller state `N`
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class NonMemberView:
    """The person authenticated successfully and is not in the guild.

    That distinction from "not logged in" is the entire content of this view: it
    is what a user needs in order to recover. It names no roles, no characters
    and no other members.
    """

    state: PageState
    reason: DeniedReason
    #: Configuration, not fetched. Asking the provider here would make the
    #: rejection path depend on the provider being reachable.
    guild_display_name: str
    checked_at: Instant
    correlation: Correlation


# ---------------------------------------------------------------------------
# VM-03 `ServiceDegradedView` — any protected route once N-10's grace is spent
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ServiceDegradedView:
    """The visible face of *fail closed*, rendered with `503`.

    It carries no cached role data and no character data, because the point at
    which this view appears is exactly the point at which cached authorization
    stopped being trustworthy.
    """

    state: PageState
    reason: DeniedReason
    subsystem: Literal["identity_provider", "database"]
    grace_expired: bool
    correlation: Correlation


# ---------------------------------------------------------------------------
# VM-04 `EmergencyLoginView` — R-06
# ---------------------------------------------------------------------------

EmergencyFailureCode = Literal[
    "invalid", "expired", "consumed", "rate_limited", "not_available"
]


@dataclass(frozen=True, slots=True)
class EmergencyFailure:
    """Deliberately coarse.

    `invalid`, `expired` and `consumed` are distinguishable to the operator
    through the audit record and **not** through the response: the browser learns
    only that it failed.
    """

    code: EmergencyFailureCode
    correlation: Correlation


@dataclass(frozen=True, slots=True)
class EmergencyLoginView:
    """Discloses no account identifier, no credential nickname and no grant state.

    The page is byte-identical whether or not a credential is enrolled, which is
    why both flags below are static configuration rather than lookups.
    """

    state: PageState
    webauthn_supported_hint: bool
    recovery_form_available: bool
    failure: EmergencyFailure | None = None


# ---------------------------------------------------------------------------
# VM-16 `HealthView` — R-10 (JSON, not HTML)
# ---------------------------------------------------------------------------

HealthCheckName = Literal[
    "database",
    "migrations",
    "artifact_store",
    "worker_heartbeat",
    "expired_leases",
    "identity_provider",
    "kill_switch",
]


@dataclass(frozen=True, slots=True)
class HealthCheck:
    name: HealthCheckName
    ok: bool


@dataclass(frozen=True, slots=True)
class HealthView:
    """No connection string, no host, no credential, no identity, no counts.

    `environment` is included deliberately: the single most useful thing a
    monitor can tell you is that production is running production configuration
    (RAID R-25).
    """

    status: Literal["ok", "degraded"]
    checks: tuple[HealthCheck, ...]
    version: str
    environment: Literal["development", "test", "staging", "production"]

    def as_payload(self) -> dict[str, object]:
        return {
            "status": self.status,
            "checks": {check.name: check.ok for check in self.checks},
            "version": self.version,
            "environment": self.environment,
        }


# ---------------------------------------------------------------------------
# VM-19 / VM-20 / VM-21 — the cross-cutting states
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ConflictView:
    """Any `409`. Always carries the **current** state, so the next action is informed."""

    state: PageState
    conflict: Literal[
        "stale_version",
        "stale_preview",
        "already_applied",
        "already_cancelled",
        "duplicate_request",
    ]
    current: object
    correlation: Correlation


@dataclass(frozen=True, slots=True)
class SafeErrorView:
    """Any `500`: one code, one UUID, nothing else (N-25).

    There is deliberately no `detail` field. Adding one is a security change, not
    a usability improvement — the operator correlates through the log, and the
    user quotes the UUID.
    """

    state: PageState
    correlation: Correlation
    message_code: Literal["unexpected_error"] = "unexpected_error"


FieldErrorCode = Literal[
    "required", "too_long", "not_a_choice", "not_found", "not_permitted", "malformed"
]


@dataclass(frozen=True, slots=True)
class FieldError:
    field: str
    code: FieldErrorCode
    limit: int | None = None


@dataclass(frozen=True, slots=True)
class ValidationView:
    """Any `422`, with the form re-rendered so the user can correct it.

    `not_found` and `not_permitted` are both returned as `not_found` on
    object-scoped fields, matching the route contract's `404` rule so validation
    cannot become the enumeration oracle the status code refuses to be.
    """

    state: PageState
    form: object
    errors: tuple[FieldError, ...]


#: The view models this package implements, by contract identifier. Asserted
#: against the parsed contract document by the structural tests, so a name that
#: drifts fails a test rather than a review.
IMPLEMENTED_VIEW_MODELS: dict[str, type] = {
    "VM-01": LoginPageView,
    "VM-02": NonMemberView,
    "VM-03": ServiceDegradedView,
    "VM-04": EmergencyLoginView,
    "VM-16": HealthView,
    "VM-19": ConflictView,
    "VM-20": SafeErrorView,
    "VM-21": ValidationView,
}

#: Documented in `vm-1` and owned by a later package. Named rather than merely
#: absent, so "not implemented yet" is a recorded fact with an owner instead of
#: something a reader has to infer from a gap.
DEFERRED_VIEW_MODELS: dict[str, str] = {
    "VM-05": "P3.2",
    "VM-06": "P3.2",
    "VM-07": "P3.2",
    "VM-08": "P3.2",
    "VM-09": "P3.2",
    "VM-10": "P3.2",
    "VM-11": "P3.2",
    "VM-12": "P3.2",
    "VM-13": "P3.2",
    "VM-14": "P3.3",
    "VM-15": "P3.3",
    "VM-17": "P3.3",
    "VM-18": "P3.3",
}
