"""Typed web configuration, validated once at startup, or the process refuses.

Three rules shape this module, all from the accepted configuration contract
(`docs/contracts/phase-3-configuration-and-dependency-contract.md` §2):

1. **A frozen dataclass tree, built once.** `WebSettings.from_environment` is the
   only constructor. Nothing reads `os.environ` after startup.
2. **Every problem is reported, not the first.** An operator fixing four
   variables should learn about all four in one attempt, so validation collects
   `ConfigurationProblem` records and raises once.
3. **No value is ever echoed.** A problem names the *variable*; it never carries
   what the variable held. That rule is what makes it safe to log a
   `ConfigurationError` in full, and `test_web_configuration.py` asserts it by
   putting a recognisable secret in every variable and searching the rendered
   error for it.

The fifteen startup refusals S-01…S-15 are implemented here, each tagged with its
identifier so `TC-STRUCT-06` can assert that a deliberately wrong configuration
refuses with the documented one.

**Ceilings, not defaults.** Where a variable carries a policy bound (`N-nn`),
configuration may make the platform *stricter* than the accepted policy and never
looser. `WEB_SESSION_IDLE_MINUTES=30` is accepted; `=90` is refused (S-10). That
is the mechanical half of "a configuration file cannot quietly raise an accepted
security limit".

**Why accepted production values appear as constants here.** `.agents/AGENTS.md`
forbids fallback secrets and production identifiers in source. These are neither:
they are never used as a default and never fill in for a missing variable. They
exist only so the process can *refuse* — S-02 has to know the production origin
in order to catch a staging process claiming it, and S-07 has to know the
production guild in order to catch a development process pointed at it. A check
that cannot name what it is checking against is not a check.
"""
from __future__ import annotations

import base64
import ipaddress
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from urllib.parse import urlsplit

from adapters.database.config import EXPECTED_DATABASES, DatabaseSettings
from adapters.database.safety import (
    ConnectionIdentity,
    ConnectionPolicy,
    UnsafeDatabaseTargetError,
)

# --------------------------------------------------------------------------
# Accepted policy values (delivery plan §7; numeric register N-01…N-67).
# Used for refusal comparisons only — never as a default for a missing value.
# --------------------------------------------------------------------------

#: N-01.
PRODUCTION_ORIGIN = "https://freedom-blades.rpgworld.org"
#: N-02.
PRODUCTION_REDIRECT_URI = "https://freedom-blades.rpgworld.org/auth/discord/callback"
#: OD-18; delivery plan §3.
PRODUCTION_GUILD_ID = 1052698198180892733
#: N-03, in the exact order the provider is asked for them.
REQUIRED_OAUTH_SCOPES: tuple[str, ...] = ("identify", "guilds.members.read")
#: The only provider key Phase 3 accepts (ADR 0010 D7).
ACCEPTED_PROVIDER_KEYS = frozenset({"discord"})

#: The placeholder tokens `.env.example` ships. A process started with one of
#: these still holds the example file's value, not a configured one (S-07).
PLACEHOLDER_TOKENS = ("__", "changeme", "replace-me", "your-", "example")

#: The placeholders the reader substitutes for a value it has already refused,
#: so that a settings constructor cannot raise mid-collection and cost the
#: operator the rest of the problem list. Neither is ever a value the process
#: runs under: a run that recorded a problem raises `ConfigurationError` and
#: returns no settings at all. `.invalid` is the reserved TLD (RFC 2606), so
#: neither can resolve or collide with a real deployment name.
_UNSET_HOSTNAME = "unset.invalid"
_UNSET_ORIGIN = "https://unset.invalid"

_ENVIRONMENTS = ("development", "test", "staging", "production")
_LOOPBACK_BIND_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})
_SECRET_MINIMUM_BYTES = 32
_HOST_LABEL = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
_KEY_ENTRY = re.compile(r"^(?P<version>\d{1,5}):(?P<material>[A-Za-z0-9+/=_-]+)$")


# --------------------------------------------------------------------------
# The accepted register, as one runtime definition per number
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PolicyBound:
    """What one registered number may be, and which accepted policy says so.

    One of these is the **whole** rule for its field. The environment reader, the
    settings dataclass that carries the field, and any consumer that reads it
    again all ask this object; none of them restates its numbers. A restatement
    is precisely the drift that made N-66 inoperative twice — the reader and the
    dataclass agreeing on the bounds while disagreeing on the type, and then two
    gates agreeing on the type while one of them accepted an `int` subclass — so
    there is deliberately no second copy of any of these numbers anywhere.

    `maximum` is `None` only where the register states a **floor** with no
    accepted ceiling (N-22's polling interval). Everywhere else the accepted
    value *is* the maximum, because a bound that may only be tightened (S-10) has
    nothing looser to fall back to. That is also why `default` is derived rather
    than stored: a separately written default is a second number that can be
    edited apart from the bound it is supposed to equal.
    """

    minimum: int
    maximum: int | None
    policy: str

    @property
    def default(self) -> int:
        """The accepted value, which is what an unset variable means."""
        return self.minimum if self.maximum is None else self.maximum

    @property
    def is_exact(self) -> bool:
        return self.maximum == self.minimum

    def requirement(self) -> str:
        """The rule in words, **without any value** — safe at the environment boundary."""
        if self.is_exact:
            return f"must be exactly {self.minimum} ({self.policy})."
        if self.maximum is None:
            return (
                f"is below its accepted floor of {self.minimum} ({self.policy}). "
                "Configuration may tighten an accepted policy and never loosen it."
            )
        return (
            f"must be a whole number between {self.minimum} and {self.maximum} "
            f"inclusive ({self.policy}). Configuration may tighten an accepted "
            "policy and never loosen it."
        )

    def refusal_for(self, number: int) -> str | None:
        """`S-10` when the number would **loosen** an accepted policy, else untagged.

        S-10 is "configuration may tighten an accepted policy and never loosen
        it", so it is the identifier for a value above a ceiling, either side of
        an exact value, and below a floor — the three ways a number can buy more
        than the register grants. A value below an ordinary minimum buys nothing;
        it is malformed, and reporting it as S-10 would make that refusal
        identifier mean two different things.
        """
        if self.is_exact or self.maximum is None:
            return "S-10"
        return "S-10" if number > self.maximum else None


def policy_number_problem(
    field_name: str, value: object, bound: PolicyBound
) -> str | None:
    """What is wrong with one registered number, or `None`. **The one definition.**

    **Why the type rule is `type(value) is int` and not `isinstance`.**
    `isinstance(value, int)` is true for `bool` and for every other subclass of
    `int`, and a subclass may override `__lt__`, `__gt__`, `__le__` and `__ge__`.
    Python gives the right-hand operand's reflected comparison priority, so
    `len(live) >= maximum` consults the *subclass* when `maximum` is one — and a
    subclass that answers `False` to every comparison makes a limit inoperative
    while remaining, to `isinstance` and to an `int` annotation, an integer. That
    is the N-66 bypass in its third form, after the non-finite float and the
    two-ordering-comparisons restatement, and it is why the accepted type is the
    exact built-in `int` rather than "something int-like". Nothing is coerced:
    an operator-supplied string is parsed at the environment boundary, and a
    value that reaches a settings constructor is already meant to be a number.

    Returns the first problem for the field, so a value of the wrong type is
    reported as the wrong type rather than also compared against a bound it
    cannot meaningfully be compared with — a comparison the value itself may be
    answering.
    """
    if type(value) is not int:
        return (
            f"{field_name} must be an exact built-in int — never a bool, never a "
            "float whether integral-looking, fractional, infinite or NaN, and "
            "never an int subclass, whose comparison methods can answer anything "
            f"— not {value!r} of type {type(value).__name__}"
        )
    if value < bound.minimum:
        if bound.is_exact:
            return (
                f"{field_name}={value} must be exactly {bound.minimum} "
                f"({bound.policy})"
            )
        if bound.minimum == 1:
            return f"{field_name} must be positive, not {value}"
        return (
            f"{field_name}={value} is below its accepted floor of "
            f"{bound.minimum} ({bound.policy}); configuration may tighten an "
            "accepted policy and never loosen it"
        )
    if bound.maximum is not None and value > bound.maximum:
        if bound.is_exact:
            return (
                f"{field_name}={value} must be exactly {bound.maximum} "
                f"({bound.policy})"
            )
        return (
            f"{field_name}={value} exceeds its accepted ceiling of "
            f"{bound.maximum} ({bound.policy}); configuration may tighten an "
            "accepted policy and never loosen it"
        )
    return None


def settings_numeric_problems(
    values: "Mapping[str, object]", bounds: "Mapping[str, PolicyBound]"
) -> list[str]:
    """Every way `values` misses `bounds`, collected rather than short-circuited.

    A key that is not in `bounds` raises `KeyError` rather than passing as a
    silently unchecked number: a field added to a settings type without a
    register entry must fail loudly, because the alternative is a policy value
    nothing bounds.
    """
    return [
        problem
        for field_name, value in values.items()
        if (problem := policy_number_problem(field_name, value, bounds[field_name]))
        is not None
    ]


def _refuse(subject: str, problems: Sequence[str]) -> None:
    """Raise `ValueError` naming every problem, or return having found none.

    The message names each field **and its value**, which is correct at *this*
    boundary and not at the environment one: these values are literals in code, a
    test or an operator tool, not the contents of a variable that might hold a
    secret. `ConfigurationError` remains the boundary that names variables and
    never values, and `_Reader` keeps its in-range fallbacks so that a settings
    constructor cannot cut the reader's collection short.
    """
    if problems:
        raise ValueError(
            f"these {subject} do not satisfy the accepted policy register: "
            + "; ".join(problems)
        )


def _registered_numbers(
    instance: object, bounds: "Mapping[str, PolicyBound]"
) -> dict[str, object]:
    """Read every registered field **exactly once**, into locals.

    Once, because these types are subclassable and a subclass's property or
    `__getattribute__` may answer differently on a second read. Whatever is
    validated here is therefore whatever the constructor stored, and a caller
    that re-reads the object later is protected by `canonical_settings` instead.
    """
    return {field_name: getattr(instance, field_name) for field_name in bounds}


#: The answer for a type that holds no other settings object. Named rather than
#: written as `{}` at the call site so the descent below reads as "these are the
#: nested fields", not "there might not be a table".
_NO_NESTED_SETTINGS: "Mapping[str, object]" = MappingProxyType({})


class SettingsAuthorityError(TypeError):
    """Two configurations were offered where a process may hold exactly one.

    Raised at the composition/application boundary, never at the environment one,
    so it may name a type or a field path — but it still carries **no configured
    value**, because the graphs it refuses are the ones that hold every secret in
    the process.

    A `TypeError` because that is what it is: an argument of the wrong kind, or
    two arguments where the signature admits one. Callers that already catch
    `TypeError` around composition keep catching this.
    """


def _declared_nested_settings(expected: type) -> "Mapping[str, object]":
    """Which fields of `expected` hold another settings object — or refuse.

    **Fail closed for a type the graph does not declare** (2026-08-16, P3.G1
    canonical-graph re-review, finding 3). This lookup was
    `CANONICAL_SETTINGS_GRAPH.get(expected, {})`, so an undeclared settings type
    was silently treated as a leaf: canonicalising it would have rebuilt its
    outer shell and left whatever subclass it nested inside untouched, and
    `require_canonical` would have declared that shell canonical. A missing entry
    is not the statement "this type nests nothing"; it is the absence of a
    statement, and the two must not answer the same.

    The declared graph stays the runtime authority — nothing here infers
    structure from annotations. `tests/web/test_canonical_settings_graph.py`
    derives the expected topology independently and proves the declaration is
    complete.
    """
    nested = CANONICAL_SETTINGS_GRAPH.get(expected)
    if nested is None:
        raise SettingsAuthorityError(
            f"{expected.__name__} is not declared in CANONICAL_SETTINGS_GRAPH, so "
            "nothing states which of its fields hold other settings objects. A "
            "type whose nested fields are unstated cannot be canonicalised: its "
            "outer shell would be rebuilt while an overridable object stayed "
            "inside it. Add the type — and every settings field it holds — to "
            "the graph."
        )
    return nested


def canonical_settings(value: object, expected: type) -> object:
    """One read of every field, validated, returned as an instance of `expected`.

    The consumer-side half of the exact-type rule. A settings object arriving at
    a consumer may be a subclass whose attributes answer differently each time
    they are read, so a consumer that reads `settings.pool_size` twice — or that
    reads it once at construction and once per request — has no guarantee that
    the value it validated is the value it uses. This reads each declared field
    of `expected` exactly once and rebuilds the **base** type from those locals,
    whose `__post_init__` then validates them. What comes back is an ordinary
    frozen instance with no overridden reads left in it, so every later read of
    it answers the value that was checked.

    It is not a guard bolted onto an authority that remains independently
    constructible: the five settings types are valid by construction, and this
    exists for the narrower fact that *reading* a subclass is not the same as
    reading what its constructor saw.

    **It descends** (2026-08-16, canonical settings graph). A settings object may
    hold another settings object — `WebSettings` holds twelve, a provider holds
    its client secret, a keyring holds its keys — and rebuilding only the outer
    type would leave a subclass nested inside an exact-base shell, still free to
    answer differently on a later read. `CANONICAL_SETTINGS_GRAPH` states which
    fields those are, so the descent is a declared shape rather than a guess made
    from annotations. A field holding a *tuple* of settings objects is written as
    a one-element tuple of the element type; that is the only container the graph
    contains.
    """
    if not isinstance(value, expected):
        raise TypeError(
            f"{expected.__name__} was expected here, because that is the type "
            f"whose constructor holds the accepted register, not {value!r}"
        )
    # One read per declared field, into locals, before anything is rebuilt from
    # them: whatever is validated below is whatever these reads saw.
    values = {field.name: getattr(value, field.name) for field in fields(expected)}
    for name, nested in _declared_nested_settings(expected).items():
        if isinstance(nested, tuple):
            (element,) = nested
            values[name] = tuple(
                canonical_settings(item, element) for item in values[name]
            )
        else:
            values[name] = canonical_settings(values[name], nested)
    return expected(**values)


class ConfigurationError(Exception):
    """Startup refused. Carries every problem found, and no value.

    Raised — never `sys.exit()`. The web process runs under a supervisor, which
    needs a non-zero exit produced by the entry point rather than by a library
    call halfway down an import (topology §5).
    """

    __slots__ = ("problems",)

    def __init__(self, problems: Sequence["ConfigurationProblem"]) -> None:
        self.problems = tuple(problems)
        super().__init__(self.render())

    def render(self) -> str:
        lines = [
            f"The web portal refuses to start: {len(self.problems)} configuration "
            "problem(s). Variable names are given; values never are."
        ]
        for problem in self.problems:
            lines.append(f"  - {problem.describe()}")
        return "\n".join(lines)

    def refusals(self) -> tuple[str, ...]:
        """The distinct `S-nn` identifiers this refusal covers, in order."""
        seen: list[str] = []
        for problem in self.problems:
            if problem.refusal and problem.refusal not in seen:
                seen.append(problem.refusal)
        return tuple(seen)


@dataclass(frozen=True, slots=True)
class ConfigurationProblem:
    """One reason the process will not start.

    `variables` names the environment variables an operator must change.
    `message` explains the rule. **Neither ever contains a configured value**;
    the class has no field that could hold one.
    """

    message: str
    variables: tuple[str, ...] = ()
    refusal: str | None = None

    def describe(self) -> str:
        named = ", ".join(self.variables) if self.variables else "(no variable)"
        tag = f"[{self.refusal}] " if self.refusal else ""
        return f"{tag}{named}: {self.message}"


class WebEnvironment(Enum):
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"

    @property
    def is_production(self) -> bool:
        return self is WebEnvironment.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self is WebEnvironment.DEVELOPMENT


class _Reader:
    """Collects problems instead of raising on the first one.

    Every accessor returns a usable fallback when a value is missing or
    malformed, so validation continues and the operator sees the whole list. The
    fallback is only ever used to keep *validation* going; a run that recorded a
    problem never returns settings.
    """

    __slots__ = ("_values", "problems")

    def __init__(self, values: Mapping[str, str]) -> None:
        self._values = values
        self.problems: list[ConfigurationProblem] = []

    # -- problem recording ------------------------------------------------
    def fail(
        self, message: str, *variables: str, refusal: str | None = None
    ) -> None:
        self.problems.append(
            ConfigurationProblem(
                message=message, variables=tuple(variables), refusal=refusal
            )
        )

    @property
    def failed(self) -> bool:
        return bool(self.problems)

    # -- primitive accessors ----------------------------------------------
    def raw(self, name: str) -> str | None:
        value = self._values.get(name)
        if value is None:
            return None
        value = value.strip()
        return value or None

    def required(self, name: str, *, refusal: str | None = None) -> str:
        value = self.raw(name)
        if value is None:
            self.fail("is required and was not set.", name, refusal=refusal)
            return ""
        return value

    def optional(self, name: str, default: str) -> str:
        value = self.raw(name)
        return default if value is None else value

    def boolean(self, name: str, *, default: bool | None = None) -> bool:
        value = self.raw(name)
        if value is None:
            if default is None:
                self.fail("is required and was not set.", name)
                return False
            return default
        lowered = value.lower()
        if lowered in ("true", "1", "yes", "on"):
            return True
        if lowered in ("false", "0", "no", "off"):
            return False
        self.fail("must be a boolean: true or false.", name)
        return False

    def integer(
        self,
        name: str,
        *,
        default: int | None = None,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> int:
        """A whole number that carries **no** `N-nn` policy bound.

        Two variables are in this category — the bind port and the active
        encryption key version — and their limits are properties of the things
        themselves rather than of the accepted register. Every variable that
        *does* carry a policy bound goes through `registered_integer`, so there
        is no route by which a register number can be written here as a literal.
        """
        value = self.raw(name)
        if value is None:
            if default is None:
                self.fail("is required and was not set.", name)
                return minimum or 0
            number = default
        else:
            try:
                number = int(value)
            except ValueError:
                self.fail("must be a whole number.", name)
                return default if default is not None else (minimum or 0)
        # Each branch records the problem and then returns an **in-range**
        # value. The fallback exists so validation can continue to the next
        # variable (a run that recorded a problem never returns settings), and
        # since 2026-08-15 the settings dataclasses enforce their own bounds.
        # Returning the operator's out-of-range number would make one of those
        # constructors raise here and abort the collection, so the operator
        # would see one problem instead of all of them.
        if minimum is not None and number < minimum:
            self.fail(f"must be at least {minimum}.", name)
            number = minimum
        if maximum is not None and number > maximum:
            self.fail(f"must be at most {maximum}.", name)
            number = maximum
        return number

    def registered_integer(
        self, name: str, field_name: str, bounds: "Mapping[str, PolicyBound]"
    ) -> int:
        """One variable that carries a policy bound, read from **the register**.

        The bound is not restated here and neither is the default: an unset
        variable means the accepted value, and the accepted value is the bound
        (S-10 — a ceiling that may only be tightened has nothing looser to fall
        back to). The accept/refuse decision is `policy_number_problem`, the same
        function the settings dataclass calls, so the reader cannot come to hold
        a different answer than the type it is building.

        Only the **wording** is produced here rather than taken from that
        function, and deliberately: a `ConfigurationError` names the variable and
        never what it held, so the operator-facing sentence is built from the
        bound alone. `PolicyBound.requirement()` cannot contain a supplied value
        because it is never given one.

        A refused value is followed by the accepted one, for the same reason
        every other accessor does that: a run that recorded a problem never
        returns settings, and a constructor raising mid-collection would cost
        the operator the rest of the list.
        """
        bound = bounds[field_name]
        value = self.raw(name)
        if value is None:
            return bound.default
        try:
            number = int(value)
        except ValueError:
            self.fail("must be a whole number.", name)
            return bound.default
        if policy_number_problem(field_name, number, bound) is None:
            return number
        self.fail(bound.requirement(), name, refusal=bound.refusal_for(number))
        return bound.default

    def number(
        self, name: str, *, default: float, minimum: float, ceiling: float
    ) -> float:
        value = self.raw(name)
        if value is None:
            return default
        try:
            parsed = float(value)
        except ValueError:
            self.fail("must be a number.", name)
            return default
        if parsed < minimum:
            self.fail(f"must be at least {minimum}.", name)
        if parsed > ceiling:
            self.fail(
                f"exceeds its accepted ceiling of {ceiling}.",
                name,
                refusal="S-10",
            )
        return parsed

    def csv(self, name: str, *, required: bool = True) -> tuple[str, ...]:
        value = self.raw(name)
        if value is None:
            if required:
                self.fail("is required and was not set.", name)
            return ()
        return tuple(part.strip() for part in value.split(",") if part.strip())

    def snowflake(self, name: str) -> int:
        value = self.raw(name)
        if value is None:
            self.fail("is required and was not set.", name)
            return 0
        if not value.isdigit():
            self.fail("must be a Discord snowflake: decimal digits only.", name)
            return 0
        number = int(value)
        if number <= 0:
            self.fail("must be a positive Discord snowflake.", name)
        return number


# --------------------------------------------------------------------------
# Value objects
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SecretKey:
    """Key material that must never be rendered.

    `__repr__` and `__str__` are overridden rather than merely discouraged: a
    dataclass's generated `repr` would put the bytes into any traceback that
    formats the settings tree, and a traceback is exactly where nobody is
    watching.
    """

    name: str
    material: bytes

    def __repr__(self) -> str:  # pragma: no cover - trivial, asserted by test
        return f"SecretKey({self.name}, {len(self.material)} bytes, redacted)"

    __str__ = __repr__


@dataclass(frozen=True, slots=True)
class EncryptionKey:
    version: int
    material: bytes

    def __repr__(self) -> str:  # pragma: no cover - trivial, asserted by test
        return f"EncryptionKey(v{self.version}, redacted)"

    __str__ = __repr__


@dataclass(frozen=True, slots=True)
class EncryptionKeyring:
    """Versioned AES-256-GCM key material (schema §9.5).

    Newest first. The active version encrypts; every version decrypts, which is
    what makes a rotation a four-step operation with no window in which a stored
    token cannot be read.
    """

    keys: tuple[EncryptionKey, ...]
    active_version: int

    def key_for(self, version: int) -> EncryptionKey:
        for key in self.keys:
            if key.version == version:
                return key
        raise KeyError(
            f"No encryption key with version {version} is configured. A ciphertext "
            "written under a retired key cannot be read; restore the key or "
            "re-encrypt before removing it."
        )

    @property
    def active(self) -> EncryptionKey:
        return self.key_for(self.active_version)


@dataclass(frozen=True, slots=True)
class DiscordProviderSettings:
    provider_key: str
    client_id: str
    client_secret: SecretKey
    redirect_uri: str
    scopes: tuple[str, ...]
    guild_id: int
    api_timeout_seconds: float
    authorization_url: str = "https://discord.com/oauth2/authorize"
    token_url: str = "https://discord.com/api/v10/oauth2/token"
    api_base_url: str = "https://discord.com/api/v10"

    @property
    def scope_parameter(self) -> str:
        return " ".join(self.scopes)


#: The accepted ceilings for every session bound, in **one** place. The
#: environment reader and `SessionSettings.__post_init__` both read these, so a
#: change to the register is one edit rather than two that can drift apart.
#: Configuration may tighten an accepted policy and never loosen it (S-10), so
#: each is a ceiling with a floor of 1 rather than an exact value.
SESSION_CEILINGS: "Mapping[str, tuple[int, str]]" = MappingProxyType(
    {
        "idle_minutes": (60, "N-06"),
        "absolute_hours": (12, "N-07"),
        "emergency_idle_minutes": (15, "N-15"),
        "emergency_absolute_minutes": (60, "N-15"),
        "max_sessions_per_account": (10, "N-66"),
        "oauth_transaction_minutes": (10, "N-04"),
    }
)

#: The same register, as the `PolicyBound` objects every other settings type
#: uses. It is **derived** from `SESSION_CEILINGS` rather than written out again:
#: every session bound is a ceiling with a floor of 1 (S-10), so the two
#: statements are one statement, and a second literal copy of these numbers is
#: exactly the drift this whole line of remediation has been about.
SESSION_BOUNDS: "Mapping[str, PolicyBound]" = MappingProxyType(
    {
        field_name: PolicyBound(minimum=1, maximum=ceiling, policy=policy)
        for field_name, (ceiling, policy) in SESSION_CEILINGS.items()
    }
)


def session_policy_problem(field_name: str, value: object) -> str | None:
    """What is wrong with one registered session-policy number, or `None`.

    **The single definition of "accepted" for these fields** (added 2026-08-15,
    session-policy numeric-validation remediation). It existed twice before: here
    in `SessionSettings.__post_init__` as *whole number, positive, within
    ceiling*, and again in `application/web/sessions.py` as *positive, within
    ceiling* — the type half missing. Two ordering comparisons are not a
    whole-number check, because `float("nan")` makes both of them false: a
    non-finite `max_sessions_per_account` reached the derived policy, and
    `len(live) >= maximum` was then false for every live-session count, so N-66
    revoked nothing. One definition, read by both gates, is what stops the two
    from acquiring different type semantics a third time.

    **And the definition is now `policy_number_problem`, shared with every other
    settings type** (2026-08-15, settings-construction remediation). The type
    rule it applies changed from `isinstance(value, int) and not
    isinstance(value, bool)` to `type(value) is int`, because the first admits
    every *other* subclass of `int` — including one that overrides its rich
    comparisons and answers `False` to all of them, which reached
    `SessionPolicy.derive()` through `dataclasses.replace()` and made
    `len(live) >= maximum` false for every live-session count exactly as the
    non-finite float had. The rule is stated as an exact type for the same reason
    the float rule was: it covers the class rather than the one member of it a
    review happened to construct.
    """
    return policy_number_problem(field_name, value, SESSION_BOUNDS[field_name])


def session_policy_problems(values: "Mapping[str, object]") -> list[str]:
    """Every way `values` misses the register, collected rather than short-circuited.

    `values` is keyed by register field name, so a caller validates the subset it
    holds: `SessionSettings` passes all six, `SessionPolicy` passes the five that
    govern a session's lifetime. A key that is not in `SESSION_CEILINGS` is a
    `KeyError` rather than a silently unchecked number.

    Problems are collected for the same reason the environment reader collects
    them: whoever is building the object should learn about all of them at once.
    """
    return settings_numeric_problems(values, SESSION_BOUNDS)


def validate_session_policy_values(
    values: "Mapping[str, object]", *, subject: str
) -> None:
    """Raise `ValueError` naming every problem, or return having found none.

    The message names each field **and its value**, which is correct at *this*
    boundary and not at the environment one: these values are literals in code, a
    test or an operator tool, not the contents of a variable that might hold a
    secret. `ConfigurationError` remains the boundary that names variables and
    never values, and `_Reader` keeps its in-range fallbacks so that this
    constructor cannot cut the reader's collection short.
    """
    _refuse(subject, session_policy_problems(values))


@dataclass(frozen=True, slots=True)
class SessionSettings:
    """The values that govern every session's lifetime — valid by construction.

    **Validated in `__post_init__` since 2026-08-15** (idle-policy-construction
    remediation, finding F1). It was previously a plain frozen dataclass whose
    numbers were checked only by the environment reader, so

        SessionSettings(..., emergency_idle_minutes=60, ...)

    was an accepted object, and every consumer downstream — the idle policy, the
    repository, the refresh statement — faithfully applied N-06's sixty minutes
    to break-glass sessions. The bypass did not need raw SQL or `object.__new__`;
    it needed the public constructor of a public type, which tests and operator
    tools are documented as using. Reader-side validation cannot make an invalid
    instance of this type impossible, because the reader is not the only way to
    build one.

    So the ceilings are enforced *here*, where the object comes into existence.
    An instance of this class is in-register whatever built it.

    **The layers below it do not stop asking, and they ask the same question**
    (corrected 2026-08-15, session-policy numeric-validation remediation). The
    sentence that used to end the paragraph above — "and the layers below it can
    stop asking" — was the mistake: `SessionPolicy.derive()` accepts subclasses of
    this type, so what it reads is not necessarily what this constructor saw, and
    its own validator had restated the rule without the type check. Both gates now
    call `session_policy_problems`, so there is one definition of what these
    numbers may be and no second copy to drift from it.

    The cookie-shape rules (N-05/S-03) are enforced here for the same reason: a
    `Secure` cookie without the `__Host-` prefix is host-only in our intention
    and not in the browser, and that is a property of the pair of fields rather
    than of where they came from.
    """

    cookie_name: str
    cookie_secure: bool
    idle_minutes: int
    absolute_hours: int
    emergency_idle_minutes: int
    emergency_absolute_minutes: int
    max_sessions_per_account: int
    login_transaction_cookie_name: str
    oauth_transaction_minutes: int

    def __post_init__(self) -> None:
        # The numeric half is `session_policy_problems`, which is the **same**
        # definition `SessionPolicy` is held to (2026-08-15). This gate and that
        # one previously restated the rule, and the restatement dropped the type
        # check, so a value this constructor would have refused was accepted one
        # layer down. The cookie half stays here: it is a property of a pair of
        # fields on this type, and no policy object carries it.
        problems = session_policy_problems(_registered_numbers(self, SESSION_BOUNDS))
        # Read once, and compared against the two names from the same read. A
        # second `self.cookie_secure` per name would be a second chance for a
        # subclass to answer differently between the two halves of one rule.
        secure = self.cookie_secure
        for field_name in ("cookie_name", "login_transaction_cookie_name"):
            name = getattr(self, field_name)
            if not isinstance(name, str) or not name.strip():
                problems.append(f"{field_name} must be a non-empty name")
                continue
            if secure and not name.startswith("__Host-"):
                problems.append(
                    f"{field_name}={name!r} must carry the __Host- prefix when "
                    "cookies are secure (N-05)"
                )
            if not secure and name.startswith("__Host-"):
                problems.append(
                    f"{field_name}={name!r} uses the __Host- prefix, which "
                    "browsers refuse without Secure"
                )
        _refuse("session settings", problems)


#: N-60's recovery-grant lifetime (N-14). The relying-party, origin and
#: user-verification rules are *relational* — they compare the identifier against
#: the public origin and the allowed-host list, neither of which this type holds
#: — so they stay at the environment boundary as S-09/S-10 and only the shape of
#: each value is a property of the type itself.
WEBAUTHN_BOUNDS: "Mapping[str, PolicyBound]" = MappingProxyType(
    {"recovery_grant_minutes": PolicyBound(minimum=1, maximum=10, policy="N-14")}
)

#: N-60's one accepted setting. A break-glass credential presentable without user
#: verification is a key somebody found, so this is an exact value rather than a
#: default.
ACCEPTED_USER_VERIFICATION = "required"


@dataclass(frozen=True, slots=True)
class WebAuthnSettings:
    """The relying party a break-glass credential is scoped to — valid by construction.

    **Validated in `__post_init__` since 2026-08-15** (I-10). Before that, an
    empty relying-party identifier, an empty origin tuple, a user-verification
    setting other than N-60's `required`, or a recovery-grant lifetime of a
    thousand minutes were all accepted objects, and the assertion verification
    built from one would have used them. Only `WebSettings.from_environment()`
    refused them, and the reader is not the only way to build one of these.

    What is checked here is what this type can *know*. `rp_id` must be a
    lowercase hostname, because that is the form every comparison against it
    assumes — the environment boundary lowercases the configured value, and a
    mixed-case identifier would be compared byte-for-byte against the lowercase
    one a browser sends and would refuse every assertion. That it must equal the
    **public origin's** host (S-09) is a relationship with a value this object
    does not carry, and it stays where both halves are in scope.
    """

    rp_id: str
    rp_name: str
    allowed_origins: tuple[str, ...]
    user_verification: str
    recovery_grant_minutes: int

    def __post_init__(self) -> None:
        problems = settings_numeric_problems(
            _registered_numbers(self, WEBAUTHN_BOUNDS), WEBAUTHN_BOUNDS
        )
        rp_id = self.rp_id
        if not isinstance(rp_id, str) or not _is_hostname(rp_id):
            problems.append(f"rp_id must be a hostname, not {rp_id!r}")
        elif rp_id != rp_id.lower():
            problems.append(
                f"rp_id={rp_id!r} must be lowercase: a relying-party identifier "
                "is compared byte-for-byte against the one the browser derives "
                "from the origin, which is lowercase"
            )
        rp_name = self.rp_name
        if not isinstance(rp_name, str) or not rp_name.strip():
            problems.append("rp_name must be a non-empty display string")
        origins = self.allowed_origins
        if not isinstance(origins, tuple) or not origins:
            problems.append(
                f"allowed_origins must be a non-empty tuple of exact origins, "
                f"not {origins!r}"
            )
        else:
            for origin in origins:
                if not _is_origin_shaped(origin):
                    problems.append(
                        f"allowed_origins contains {origin!r}, which is not an "
                        "exact origin"
                    )
        verification = self.user_verification
        if verification != ACCEPTED_USER_VERIFICATION:
            problems.append(
                f"user_verification must be {ACCEPTED_USER_VERIFICATION!r} "
                f"(N-60), not {verification!r}"
            )
        _refuse("WebAuthn settings", problems)


#: N-18, N-32, N-33 and their shared N-30 window, each a ceiling with a floor of
#: 1 — except the cleanup horizon, whose floor is N-31's ten minutes because a
#: window swept before it closes is a window that never counted anything.
RATE_LIMIT_BOUNDS: "Mapping[str, PolicyBound]" = MappingProxyType(
    {
        "window_minutes": PolicyBound(minimum=1, maximum=10, policy="N-18/N-30"),
        "oauth_starts_per_ip": PolicyBound(minimum=1, maximum=10, policy="N-18"),
        "oauth_callbacks_per_ip": PolicyBound(minimum=1, maximum=20, policy="N-18"),
        "webauthn_assertions_per_ip": PolicyBound(minimum=1, maximum=5, policy="N-32"),
        "webauthn_assertions_per_account": PolicyBound(
            minimum=1, maximum=10, policy="N-32"
        ),
        "webauthn_account_window_minutes": PolicyBound(
            minimum=1, maximum=60, policy="N-32"
        ),
        "recovery_attempts_per_ip": PolicyBound(minimum=1, maximum=3, policy="N-33"),
        "recovery_attempts_per_grant": PolicyBound(minimum=1, maximum=5, policy="N-33"),
        "cleanup_after_minutes": PolicyBound(minimum=10, maximum=60, policy="N-31"),
    }
)


@dataclass(frozen=True, slots=True)
class RateLimitSettings:
    """N-18, N-32, N-33 and their shared N-30 window — valid by construction.

    **Validated in `__post_init__` since 2026-08-15** (I-10). These nine numbers
    are the authentication and recovery throttles. Until this constructor
    enforced the register, `RateLimitSettings(window_minutes=1,
    oauth_starts_per_ip=10_000, ...)` was an accepted object and the limiter
    built from it would have counted honestly to a budget nobody accepted; a
    `bool` in any of them would have been a budget of one or zero; and an `int`
    subclass overriding its comparisons would have made `count <= limit` answer
    whatever it liked, which is the N-66 defect wearing a different field name.
    """

    window_minutes: int
    oauth_starts_per_ip: int
    oauth_callbacks_per_ip: int
    webauthn_assertions_per_ip: int
    webauthn_assertions_per_account: int
    webauthn_account_window_minutes: int
    recovery_attempts_per_ip: int
    recovery_attempts_per_grant: int
    cleanup_after_minutes: int

    def __post_init__(self) -> None:
        _refuse(
            "rate-limit settings",
            settings_numeric_problems(
                _registered_numbers(self, RATE_LIMIT_BOUNDS), RATE_LIMIT_BOUNDS
            ),
        )


#: N-53. `max_overflow` floors at 0 — no overflow at all is a legitimate,
#: stricter deployment — and every other pool number floors at 1 because a pool
#: of none, a wait of none or a statement timeout of none are not tighter
#: policies but broken ones. The statement-timeout floor is 100 ms for the same
#: reason: below it the timeout cancels ordinary queries rather than pathological
#: ones.
DATABASE_POOL_BOUNDS: "Mapping[str, PolicyBound]" = MappingProxyType(
    {
        "pool_size": PolicyBound(minimum=1, maximum=5, policy="N-53"),
        "max_overflow": PolicyBound(minimum=0, maximum=5, policy="N-53"),
        "pool_timeout_seconds": PolicyBound(minimum=1, maximum=5, policy="N-53"),
        "statement_timeout_ms": PolicyBound(minimum=100, maximum=10_000, policy="N-53"),
    }
)


@dataclass(frozen=True, slots=True)
class DatabasePoolSettings:
    """N-53's pool topology — valid by construction.

    **Validated in `__post_init__` since 2026-08-15** (I-10). These four numbers
    become SQLAlchemy engine arguments and a PostgreSQL `statement_timeout` on a
    host shared with three Foundry instances, the live bot and the database
    itself. An unbounded pool or a statement timeout of an hour is an
    availability failure for everything on the host, and neither is something the
    type should have permitted merely because the ordinary construction path
    happened to check its strings.
    """

    pool_size: int
    max_overflow: int
    pool_timeout_seconds: int
    statement_timeout_ms: int

    def __post_init__(self) -> None:
        _refuse(
            "database pool settings",
            settings_numeric_problems(
                _registered_numbers(self, DATABASE_POOL_BOUNDS), DATABASE_POOL_BOUNDS
            ),
        )


#: N-09, N-10, N-19, N-21, N-22 and N-34. `trusted_proxy_hops` is the one
#: **exact** value in the set: N-34 accepts exactly one hop, trusted only from a
#: loopback peer, so neither zero nor two is a tightening. `poll_min_seconds` is
#: the one **floor**: N-22 says "no faster than every 2 seconds" and states no
#: ceiling, and inventing one here would be new policy rather than enforcement of
#: the accepted one.
REQUEST_BOUNDS: "Mapping[str, PolicyBound]" = MappingProxyType(
    {
        "max_request_bytes": PolicyBound(
            minimum=1024, maximum=1024 * 1024, policy="N-19"
        ),
        "trusted_proxy_hops": PolicyBound(minimum=1, maximum=1, policy="N-34"),
        "membership_cache_seconds": PolicyBound(minimum=1, maximum=300, policy="N-09"),
        "membership_grace_seconds": PolicyBound(minimum=1, maximum=900, policy="N-10"),
        "audit_page_size_default": PolicyBound(minimum=1, maximum=50, policy="N-21"),
        "audit_page_size_max": PolicyBound(minimum=1, maximum=100, policy="N-21"),
        "poll_min_seconds": PolicyBound(minimum=2, maximum=None, policy="N-22"),
    }
)


@dataclass(frozen=True, slots=True)
class BoundsSettings:
    """The request, proxy, membership, pagination and polling bounds — valid by construction.

    **Validated in `__post_init__` since 2026-08-15** (I-10). Two of these reach
    a security control directly: `max_request_bytes` is the body bound applied
    before a body is read, and `trusted_proxy_hops` is the N-34 client-address
    determination that every rate-limit bucket and every audited client digest is
    keyed by.

    The one cross-field rule N-21 states — a default page size cannot exceed its
    maximum — is enforced **here**, from the same single read of each field the
    numeric check used, because this is the object that owns both of them. No
    other relationship is enforced: N-09 and N-10 state two independent bounds
    and the delivery plan states no ordering between them, and inventing one
    would refuse configurations the contract accepts.
    """

    max_request_bytes: int
    trusted_proxy_hops: int
    membership_cache_seconds: int
    membership_grace_seconds: int
    audit_page_size_default: int
    audit_page_size_max: int
    poll_min_seconds: int

    def __post_init__(self) -> None:
        numbers = _registered_numbers(self, REQUEST_BOUNDS)
        problems = settings_numeric_problems(numbers, REQUEST_BOUNDS)
        default = numbers["audit_page_size_default"]
        maximum = numbers["audit_page_size_max"]
        # Only when both are numbers the register accepted: comparing a value
        # that failed the type rule is asking that value what it thinks.
        if not problems and default > maximum:
            problems.append(
                f"audit_page_size_default={default} cannot exceed "
                f"audit_page_size_max={maximum} (N-21)"
            )
        _refuse("request bounds", problems)


#: N-23, N-41, N-42, N-43 and N-45. Two of the six are **exact** values and the
#: other four are ceilings with a floor of 1.
#:
#: **N-23 is one sentence stating two different kinds of number** (corrected
#: 2026-08-15, N-23 exact-lease remediation). "Job lease | 60 seconds, heartbeat
#: at most every 20 seconds" gives the lease as a *value* and the heartbeat
#: interval as a *maximum*, and the distinction is deliberate: the accepted state
#: machine renews with `now() + 60 seconds`, the accepted schema's claim and
#: renewal statements write the same 60, and the operational contract's recovery
#: bound (`N-23 + N-44`, at most ≈225 s across three claims) is calculated from a
#: 60-second lease. A lease this table permitted to be anything from 1 to 60 was
#: therefore not a tightening of N-23 but a contradiction of the documents that
#: read it, and a one-second lease would lose a live claim to ordinary heartbeat
#: scheduling. So `lease_seconds` is exactly 60, exactly as `concurrency` is
#: exactly 1 (N-41) and `trusted_proxy_hops` is exactly 1 (N-34): neither side of
#: an exact value is a tightening, which is why `PolicyBound.refusal_for` tags
#: both directions `S-10`.
#:
#: **No relationship between lease, heartbeat and attempt timeout is enforced
#: here, and none is needed for the lease and the heartbeat.** With the lease
#: fixed at 60 and the heartbeat accepted only up to 20, every accepted pair
#: already heartbeats well inside its own lease; there is nothing left for an
#: ordering rule to catch. No relationship involving N-45's per-attempt cap is
#: enforced either, because no accepted document states one — and a rule that
#: "sounds sensible" is still new policy, whose accepted route is a controlled
#: decision rather than a constructor.
WORKER_BOUNDS: "Mapping[str, PolicyBound]" = MappingProxyType(
    {
        "concurrency": PolicyBound(minimum=1, maximum=1, policy="N-41"),
        "lease_seconds": PolicyBound(minimum=60, maximum=60, policy="N-23"),
        "heartbeat_seconds": PolicyBound(minimum=1, maximum=20, policy="N-23"),
        "max_attempts": PolicyBound(minimum=1, maximum=3, policy="N-43"),
        "attempt_timeout_seconds": PolicyBound(minimum=1, maximum=300, policy="N-45"),
        "queue_max_depth": PolicyBound(minimum=1, maximum=5, policy="N-42"),
    }
)


@dataclass(frozen=True, slots=True)
class WorkerSettings:
    """Bounds the worker will run under — valid by construction. P3.1 reads only
    `enabled` (S-11) and `artifact_root` (S-12).

    **Validated in `__post_init__` since 2026-08-15** (I-10). The remaining
    fields have no consumer in P3.1 and this package implements none: their
    consumers are P3.3's, and manufacturing worker behaviour here to produce
    consumer evidence would be starting a package that has not been authorised.
    What this constructor does is make them impossible to hold an out-of-register
    value *before* that behaviour exists, which is the point of the I-10 timing
    row: they become mandatory before P3.3 activates them, and the type is ready
    when it does.
    """

    enabled: bool
    concurrency: int
    lease_seconds: int
    heartbeat_seconds: int
    max_attempts: int
    attempt_timeout_seconds: int
    queue_max_depth: int
    artifact_root: Path | None

    def __post_init__(self) -> None:
        problems = settings_numeric_problems(
            _registered_numbers(self, WORKER_BOUNDS), WORKER_BOUNDS
        )
        enabled = self.enabled
        if type(enabled) is not bool:
            problems.append(
                f"enabled must be an exact bool — S-11 refuses a web process "
                f"that claims jobs, and a truthy value is not a decision — not "
                f"{enabled!r} of type {type(enabled).__name__}"
            )
        root = self.artifact_root
        if root is not None:
            if not isinstance(root, Path):
                problems.append(
                    f"artifact_root must be a Path or None, not {root!r}"
                )
            elif not root.is_absolute():
                problems.append(
                    f"artifact_root={str(root)!r} must be absolute: a relative "
                    "path resolves against the process working directory, which "
                    "is not a property the operator set (S-12)"
                )
        _refuse("worker settings", problems)


#: Every settings type whose numbers are in the accepted register, with the table
#: that holds them. Published so a test can parameterise from the register itself
#: rather than restating it — a test that repeated these numbers would be one
#: more copy able to drift from the definition, which is the failure this whole
#: structure exists to prevent.
SETTINGS_NUMERIC_BOUNDS: "Mapping[type, Mapping[str, PolicyBound]]" = MappingProxyType(
    {
        SessionSettings: SESSION_BOUNDS,
        WebAuthnSettings: WEBAUTHN_BOUNDS,
        RateLimitSettings: RATE_LIMIT_BOUNDS,
        DatabasePoolSettings: DATABASE_POOL_BOUNDS,
        BoundsSettings: REQUEST_BOUNDS,
        WorkerSettings: WORKER_BOUNDS,
    }
)


@dataclass(frozen=True, slots=True)
class WebSettings:
    """The whole configuration of one web process."""

    environment: WebEnvironment
    bind_host: str
    bind_port: int
    public_origin: str
    allowed_hosts: tuple[str, ...]
    kill_switch_file: Path
    csrf_key: SecretKey
    cursor_key: SecretKey
    client_digest_key: SecretKey
    database: DatabaseSettings
    database_pool: DatabasePoolSettings
    provider_registry: tuple[str, ...]
    discord: DiscordProviderSettings
    bootstrap_admin_role_id: int
    session: SessionSettings
    webauthn: WebAuthnSettings
    encryption: EncryptionKeyring
    rate_limits: RateLimitSettings
    bounds: BoundsSettings
    worker: WorkerSettings

    @property
    def public_host(self) -> str:
        return urlsplit(self.public_origin).hostname or ""

    @classmethod
    def from_environment(cls, values: Mapping[str, str]) -> "WebSettings":
        """Build settings, or raise `ConfigurationError` naming every problem."""
        reader = _Reader(values)
        environment = _read_environment(reader)
        public_origin = _read_public_origin(reader, environment)
        allowed_hosts = _read_allowed_hosts(reader, public_origin)
        bind_host, bind_port = _read_bind(reader, environment)
        kill_switch_file = _read_kill_switch(reader)
        csrf_key, cursor_key, client_digest_key = _read_secret_keys(reader)
        database, pool = _read_database(reader, environment, values)
        registry = _read_provider_registry(reader)
        discord = _read_discord(reader, environment, public_origin)
        bootstrap_admin_role_id = reader.snowflake("WEB_BOOTSTRAP_ADMIN_ROLE_ID")
        session = _read_session(reader, environment)
        webauthn = _read_webauthn(reader, public_origin, allowed_hosts)
        encryption = _read_encryption(reader)
        _require_distinct_keys(reader, csrf_key, cursor_key, client_digest_key, encryption)
        rate_limits = _read_rate_limits(reader)
        bounds = _read_bounds(reader)
        worker = _read_worker(reader)

        if worker.enabled:
            reader.fail(
                "must be false in the web process. A web process that claimed jobs "
                "would execute the GIL-holding preview work N-40 exists to keep out "
                "of it, stalling polling, health and every other request.",
                "WORKER_ENABLED",
                refusal="S-11",
            )

        if reader.failed or database is None:
            # `database is None` cannot occur without a recorded problem; the
            # second half of the condition is what lets the type checker see
            # that, rather than a cast that would also hide a real bug.
            raise ConfigurationError(
                reader.problems
                or [
                    ConfigurationProblem(
                        message="could not be validated.",
                        variables=("WEB_DATABASE_URL",),
                        refusal="S-01",
                    )
                ]
            )

        return cls(
            environment=environment,
            bind_host=bind_host,
            bind_port=bind_port,
            public_origin=public_origin,
            allowed_hosts=allowed_hosts,
            kill_switch_file=kill_switch_file,
            csrf_key=csrf_key,
            cursor_key=cursor_key,
            client_digest_key=client_digest_key,
            database=database,
            database_pool=pool,
            provider_registry=registry,
            discord=discord,
            bootstrap_admin_role_id=bootstrap_admin_role_id,
            session=session,
            webauthn=webauthn,
            encryption=encryption,
            rate_limits=rate_limits,
            bounds=bounds,
            worker=worker,
        )


# --------------------------------------------------------------------------
# The canonical settings graph (2026-08-16, P3.G1 canonical-graph remediation)
# --------------------------------------------------------------------------

#: Every settings type in the graph, mapped to the fields of it that hold
#: **another** settings object. A type that holds none maps to an empty mapping,
#: which is what makes this table the complete statement of the shape rather than
#: a list of the interesting cases; a field holding a *tuple* of settings objects
#: is written as a one-element tuple of the element type.
#:
#: It exists because the previous correction stopped one level too early. Each
#: settings type validated its own numbers at construction and selected consumers
#: rebuilt the *one* nested object they used, but the composition root still held
#: and redistributed the caller's outer `WebSettings`. A genuine subclass of that
#: type — or of any type below it — passes every construction gate by answering
#: accepted values while it is being validated and a different value on the read
#: that is actually used. Rebuilding the whole graph, once, from one read of
#: every field is what removes the overridden reads instead of guarding against
#: each of them.
#:
#: The register tables above say what a number may *be*. This says what the graph
#: *is*. Neither restates the other, and no policy number appears here.
CANONICAL_SETTINGS_GRAPH: "Mapping[type, Mapping[str, object]]" = MappingProxyType(
    {
        WebSettings: MappingProxyType(
            {
                "csrf_key": SecretKey,
                "cursor_key": SecretKey,
                "client_digest_key": SecretKey,
                "database": DatabaseSettings,
                "database_pool": DatabasePoolSettings,
                "discord": DiscordProviderSettings,
                "session": SessionSettings,
                "webauthn": WebAuthnSettings,
                "encryption": EncryptionKeyring,
                "rate_limits": RateLimitSettings,
                "bounds": BoundsSettings,
                "worker": WorkerSettings,
            }
        ),
        DatabaseSettings: MappingProxyType({"identity": ConnectionIdentity}),
        DiscordProviderSettings: MappingProxyType({"client_secret": SecretKey}),
        EncryptionKeyring: MappingProxyType({"keys": (EncryptionKey,)}),
        BoundsSettings: _NO_NESTED_SETTINGS,
        ConnectionIdentity: _NO_NESTED_SETTINGS,
        DatabasePoolSettings: _NO_NESTED_SETTINGS,
        EncryptionKey: _NO_NESTED_SETTINGS,
        RateLimitSettings: _NO_NESTED_SETTINGS,
        SecretKey: _NO_NESTED_SETTINGS,
        SessionSettings: _NO_NESTED_SETTINGS,
        WebAuthnSettings: _NO_NESTED_SETTINGS,
        WorkerSettings: _NO_NESTED_SETTINGS,
    }
)


def canonical_web_settings(settings: object) -> WebSettings:
    """The one canonical settings graph for a web process.

    Every field of `WebSettings` and of every settings object below it is read
    **once**, and the exact base types are rebuilt from those locals through the
    constructors that hold the accepted register. What comes back has no
    overridden read anywhere in it, so the value each `__post_init__` validated is
    the value every later consumer sees — including a consumer that reads it once
    per request for the life of the process.

    Called once, at the composition root. It is deliberately not called again by
    the consumers below it: a second canonicalization would be a second graph,
    which is the shape of the defect rather than a defence against it. Consumers
    that retain a graph call `require_canonical_web_settings` instead, which
    checks and returns *this* object rather than making another.

    No secret is converted, decoded, rendered or compared. `SecretKey` and
    `EncryptionKey` are rebuilt from the same `bytes` object they already held,
    and both keep the `__repr__` that redacts it.
    """
    return canonical_settings(settings, WebSettings)


def require_canonical(value: object, expected: type, *, subject: str) -> object:
    """`value` is exactly `expected` and canonical all the way down, or refuse.

    The receiving half of the boundary, for a consumer that **retains** a settings
    object and reads it again later. `canonical_web_settings` guarantees the
    property for what it returns; this states it as a requirement on what a
    consumer accepts, so the guarantee does not depend on every construction site
    remembering where the graph came from.

    `type(...) is` rather than `isinstance`, for the same reason the registered
    integers are an exact built-in `int`: a subclass is precisely what may answer
    one value while it is checked and another while it is used, and every
    subclass of every type in this graph is such a subclass in potential. The
    exact-type check on the container is also what makes the field reads below
    trustworthy — an exact frozen dataclass cannot intercept them.

    The refusal names the subject, the field path and the type that was found. It
    names **no configured value**, because the graph it refuses holds every secret
    the process has.
    """
    _require_canonical(value, expected, subject=subject, path=expected.__name__)
    return value


def _require_canonical(value: object, expected: type, *, subject: str, path: str) -> None:
    if type(value) is not expected:
        raise SettingsAuthorityError(
            f"{subject} requires the canonical settings graph: {path} must be "
            f"exactly {expected.__name__}, which is the type whose constructor "
            f"holds the accepted register and whose reads cannot be overridden, "
            f"not {type(value).__name__}. Build it with canonical_settings() at "
            "the composition root and pass that one object."
        )
    for name, nested in _declared_nested_settings(expected).items():
        held = getattr(value, name)
        if isinstance(nested, tuple):
            (element,) = nested
            if type(held) is not tuple:
                raise SettingsAuthorityError(
                    f"{subject} requires the canonical settings graph: "
                    f"{path}.{name} must be an exact tuple, not "
                    f"{type(held).__name__}."
                )
            for index, item in enumerate(held):
                _require_canonical(
                    item, element, subject=subject, path=f"{path}.{name}[{index}]"
                )
        else:
            _require_canonical(held, nested, subject=subject, path=f"{path}.{name}")


def require_canonical_web_settings(settings: object, *, subject: str) -> WebSettings:
    """`require_canonical` for the whole graph, typed as what it returns."""
    _require_canonical(settings, WebSettings, subject=subject, path="WebSettings")
    # The check above proved `type(settings) is WebSettings`, which is stronger
    # than this parameter's annotation. The narrowing is stated here rather than
    # re-derived by a second `isinstance` nothing would act on.
    return settings  # type: ignore[return-value]


# --------------------------------------------------------------------------
# Readers, one per section of the contract
# --------------------------------------------------------------------------


def _read_environment(reader: _Reader) -> WebEnvironment:
    value = reader.raw("WEB_ENVIRONMENT")
    if value is None:
        reader.fail(
            "is required. The web process must state which environment it is, "
            "because every other environment check compares against it.",
            "WEB_ENVIRONMENT",
        )
        return WebEnvironment.DEVELOPMENT
    if value not in _ENVIRONMENTS:
        reader.fail(
            f"must be one of {', '.join(_ENVIRONMENTS)}.", "WEB_ENVIRONMENT"
        )
        return WebEnvironment.DEVELOPMENT
    return WebEnvironment(value)


def _read_public_origin(reader: _Reader, environment: WebEnvironment) -> str:
    value = reader.required("WEB_PUBLIC_ORIGIN")
    if not value:
        return "http://127.0.0.1:8000"
    parts = urlsplit(value)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        reader.fail(
            "must be an absolute origin such as https://host, with no path.",
            "WEB_PUBLIC_ORIGIN",
        )
        return value
    if parts.path not in ("", "/") or parts.query or parts.fragment:
        reader.fail(
            "must be a bare origin: scheme, host and optional port, with no "
            "path, query or fragment.",
            "WEB_PUBLIC_ORIGIN",
        )
    normalised = f"{parts.scheme}://{parts.netloc}"

    if environment.is_production and normalised != PRODUCTION_ORIGIN:
        reader.fail(
            "must be exactly the accepted production origin (N-01) in production.",
            "WEB_PUBLIC_ORIGIN",
            refusal="S-02",
        )
    if not environment.is_production and normalised == PRODUCTION_ORIGIN:
        reader.fail(
            "is the accepted production origin (N-01) but this process is not "
            "production. A staging process claiming the production origin would "
            "receive production cookies and OAuth callbacks.",
            "WEB_PUBLIC_ORIGIN",
            "WEB_ENVIRONMENT",
            refusal="S-02",
        )
    if not environment.is_development and parts.scheme != "https":
        reader.fail(
            "must use https outside development.",
            "WEB_PUBLIC_ORIGIN",
            refusal="S-03",
        )
    return normalised


def _read_allowed_hosts(reader: _Reader, public_origin: str) -> tuple[str, ...]:
    hosts = reader.csv("WEB_ALLOWED_HOSTS")
    if not hosts:
        reader.fail(
            "must list at least one exact hostname. An empty allowlist would "
            "either accept every Host header or none.",
            "WEB_ALLOWED_HOSTS",
            refusal="S-04",
        )
        return ()
    cleaned: list[str] = []
    for host in hosts:
        lowered = host.lower()
        if "*" in lowered:
            reader.fail(
                "must contain exact hostnames only. A wildcard makes host "
                "validation decorative.",
                "WEB_ALLOWED_HOSTS",
                refusal="S-04",
            )
            continue
        if not _is_hostname(lowered):
            reader.fail(
                "contains an entry that is not a hostname.",
                "WEB_ALLOWED_HOSTS",
                refusal="S-04",
            )
            continue
        cleaned.append(lowered)
    public_host = (urlsplit(public_origin).hostname or "").lower()
    if public_host and public_host not in cleaned:
        reader.fail(
            "omits the public origin's own host, so the portal would refuse its "
            "own hostname.",
            "WEB_ALLOWED_HOSTS",
            "WEB_PUBLIC_ORIGIN",
            refusal="S-04",
        )
    return tuple(cleaned)


def _is_hostname(value: str) -> bool:
    if not value or len(value) > 253:
        return False
    try:
        ipaddress.ip_address(value)
    except ValueError:
        pass
    else:
        return True
    return all(_HOST_LABEL.match(label) for label in value.split("."))


def _read_bind(reader: _Reader, environment: WebEnvironment) -> tuple[str, int]:
    host = reader.optional("WEB_BIND_HOST", "127.0.0.1").lower()
    if not environment.is_development and host not in _LOOPBACK_BIND_HOSTS:
        reader.fail(
            "must bind to loopback (N-50). The public perimeter is Caddy; the "
            "application port is private.",
            "WEB_BIND_HOST",
            refusal="S-10",
        )
    port = reader.integer("WEB_BIND_PORT", default=8000, minimum=1, maximum=65535)
    return host, port


def _read_kill_switch(reader: _Reader) -> Path:
    value = reader.required("WEB_KILL_SWITCH_FILE")
    path = Path(value) if value else Path("/nonexistent/kill-switch")
    if value and not path.is_absolute():
        reader.fail(
            "must be an absolute path. A relative path resolves against the "
            "process working directory, which is not a property the operator set.",
            "WEB_KILL_SWITCH_FILE",
        )
    return path


def _read_secret_keys(reader: _Reader) -> tuple[SecretKey, SecretKey, SecretKey]:
    """The three standalone secret keys. The fourth is the active encryption key.

    `WEB_SECRET_KEY_CLIENT_DIGEST` is an addition P3.1 makes to the named set in
    the configuration contract, and it is required by the accepted **schema**:
    `sessions.client_ip_hash` is specified as a *salted* hash and
    `auth_rate_limits.bucket` hashes the address rather than storing it. An
    unkeyed SHA-256 over an IPv4 address is reversible by exhaustive search in
    seconds, so an unsalted digest would be the address with extra steps. It is
    recorded as an addition in the P3.1 submission rather than folded in
    silently, and S-08's "four secret keys" is exactly this set plus the active
    encryption key.
    """
    return (
        _read_secret(reader, "WEB_SECRET_KEY_CSRF"),
        _read_secret(reader, "WEB_SECRET_KEY_CURSOR"),
        _read_secret(reader, "WEB_SECRET_KEY_CLIENT_DIGEST"),
    )


def _read_secret(reader: _Reader, name: str) -> SecretKey:
    value = reader.raw(name)
    if value is None:
        reader.fail("is required and was not set.", name, refusal="S-08")
        return SecretKey(name, b"")
    material = _decode_key_material(value)
    if len(material) < _SECRET_MINIMUM_BYTES:
        reader.fail(
            f"must carry at least {_SECRET_MINIMUM_BYTES} bytes of entropy.",
            name,
            refusal="S-08",
        )
    return SecretKey(name, material)


def _decode_key_material(value: str) -> bytes:
    """Base64 if it decodes cleanly, otherwise the UTF-8 bytes as given.

    Accepting both spellings is deliberate: an operator generating a key with
    `openssl rand -base64 32` and one using a long passphrase both end up with a
    usable key, and neither has to know which the code wanted.
    """
    candidate = value.strip()
    padded = candidate + "=" * (-len(candidate) % 4)
    try:
        decoded = base64.b64decode(padded, validate=True)
    except (ValueError, base64.binascii.Error):  # type: ignore[attr-defined]
        return candidate.encode("utf-8")
    return decoded if decoded else candidate.encode("utf-8")


def _read_database(
    reader: _Reader, environment: WebEnvironment, values: Mapping[str, str]
) -> tuple[DatabaseSettings | None, DatabasePoolSettings]:
    """Validated by the **existing** `adapters/database/config.py`.

    Reusing it matters. The `PGHOSTADDR` and SSH-forward analysis in that module
    is real security work, and a second implementation here would be a second
    place for it to be wrong. The runtime creates and drops nothing, which is the
    documented condition for `SOCKET_OR_LOOPBACK`.
    """
    settings: DatabaseSettings | None = None
    if reader.raw("WEB_DATABASE_URL") is None:
        reader.fail("is required and was not set.", "WEB_DATABASE_URL", refusal="S-01")
    else:
        try:
            settings = DatabaseSettings.from_mapping(
                values,
                environment=environment.value,
                variable="WEB_DATABASE_URL",
                policy=ConnectionPolicy.SOCKET_OR_LOOPBACK,
            )
        except (ValueError, UnsafeDatabaseTargetError) as error:
            expected = EXPECTED_DATABASES.get(environment.value, "?")
            reader.fail(
                f"must name the {environment.value} database ({expected}) on a "
                "local target. The existing database-safety validator refused it: "
                f"{_scrub(str(error))}",
                "WEB_DATABASE_URL",
                "WEB_ENVIRONMENT",
                refusal="S-01",
            )
    pool = DatabasePoolSettings(
        pool_size=reader.registered_integer(
            "WEB_DATABASE_POOL_SIZE", "pool_size", DATABASE_POOL_BOUNDS
        ),
        max_overflow=reader.registered_integer(
            "WEB_DATABASE_MAX_OVERFLOW", "max_overflow", DATABASE_POOL_BOUNDS
        ),
        pool_timeout_seconds=reader.registered_integer(
            "WEB_DATABASE_TIMEOUT_SECONDS", "pool_timeout_seconds", DATABASE_POOL_BOUNDS
        ),
        statement_timeout_ms=reader.registered_integer(
            "WEB_DATABASE_STATEMENT_TIMEOUT_MS",
            "statement_timeout_ms",
            DATABASE_POOL_BOUNDS,
        ),
    )
    return settings, pool


def _scrub(message: str) -> str:
    """Keep a validator's explanation, drop anything that looks like a URL.

    The database validator already redacts credentials, but it does name hosts
    and database names. Those are not secrets and they are the whole point of the
    message; a URL-shaped token is removed anyway, because this text is logged.
    """
    return re.sub(r"\b\w+://\S+", "<redacted-url>", message)


def _read_provider_registry(reader: _Reader) -> tuple[str, ...]:
    keys = reader.csv("WEB_PROVIDER_REGISTRY")
    if not keys:
        return ()
    unknown = [key for key in keys if key not in ACCEPTED_PROVIDER_KEYS]
    if unknown:
        reader.fail(
            "names a provider key Phase 3 does not accept. Adding an ordinary "
            "member provider requires its own accepted provider, privacy, "
            "account-linking and migration package (ADR 0010 D7). A typo here "
            "would otherwise create a shadow subject namespace.",
            "WEB_PROVIDER_REGISTRY",
        )
    if "discord" not in keys:
        reader.fail(
            "must enable the 'discord' provider: it is the only ordinary-member "
            "provider Phase 3 has.",
            "WEB_PROVIDER_REGISTRY",
        )
    return keys


def _read_discord(
    reader: _Reader, environment: WebEnvironment, public_origin: str
) -> DiscordProviderSettings:
    client_id = reader.required("WEB_DISCORD_CLIENT_ID")
    client_secret = _read_secret_free(reader, "WEB_DISCORD_CLIENT_SECRET")
    redirect_uri = reader.required("WEB_DISCORD_REDIRECT_URI")
    scopes = reader.csv("WEB_DISCORD_SCOPES")
    guild_id = reader.snowflake("WEB_DISCORD_GUILD_ID")
    timeout = reader.number(
        "WEB_DISCORD_API_TIMEOUT_SECONDS", default=5.0, minimum=0.5, ceiling=30.0
    )

    if scopes and tuple(scopes) != REQUIRED_OAUTH_SCOPES:
        reader.fail(
            "must be exactly 'identify,guilds.members.read' (N-03). Scope creep "
            "is a privacy change, not a configuration convenience.",
            "WEB_DISCORD_SCOPES",
            refusal="S-06",
        )

    if redirect_uri:
        redirect_parts = urlsplit(redirect_uri)
        origin_parts = urlsplit(public_origin)
        same_origin = (
            redirect_parts.scheme == origin_parts.scheme
            and redirect_parts.netloc == origin_parts.netloc
        )
        if not same_origin:
            reader.fail(
                "does not share the public origin. A callback delivered to "
                "another origin is a token-leak path.",
                "WEB_DISCORD_REDIRECT_URI",
                "WEB_PUBLIC_ORIGIN",
                refusal="S-05",
            )
        if environment.is_production and redirect_uri != PRODUCTION_REDIRECT_URI:
            reader.fail(
                "must be exactly the accepted production redirect URI (N-02) in "
                "production; it is registered at the provider.",
                "WEB_DISCORD_REDIRECT_URI",
                refusal="S-05",
            )

    if environment.is_production:
        if guild_id and guild_id != PRODUCTION_GUILD_ID:
            reader.fail(
                "is not the production guild. A production process pointed at a "
                "staging guild would authorize the wrong community.",
                "WEB_DISCORD_GUILD_ID",
                refusal="S-07",
            )
        if client_id and _looks_like_placeholder(client_id):
            reader.fail(
                "still holds an .env.example placeholder rather than the "
                "production application's client id.",
                "WEB_DISCORD_CLIENT_ID",
                refusal="S-07",
            )
    elif guild_id == PRODUCTION_GUILD_ID:
        reader.fail(
            "is the production guild, but this process is not production. No "
            "implementation package may use the production Discord application "
            "or guild for automated tests (delivery plan §10).",
            "WEB_DISCORD_GUILD_ID",
            "WEB_ENVIRONMENT",
            refusal="S-07",
        )

    return DiscordProviderSettings(
        provider_key="discord",
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scopes=REQUIRED_OAUTH_SCOPES if not scopes else tuple(scopes),
        guild_id=guild_id,
        api_timeout_seconds=timeout,
    )


def _read_secret_free(reader: _Reader, name: str) -> SecretKey:
    """A provider secret: required and never rendered, but not length-bounded.

    Its length is the provider's choice, so S-08's 32-byte rule does not apply;
    what does apply is that it never reaches a log or an error message.
    """
    value = reader.raw(name)
    if value is None:
        reader.fail("is required and was not set.", name)
        return SecretKey(name, b"")
    return SecretKey(name, value.encode("utf-8"))


def _looks_like_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(token in lowered for token in PLACEHOLDER_TOKENS)


def _read_session(reader: _Reader, environment: WebEnvironment) -> SessionSettings:
    secure = reader.boolean(
        "WEB_COOKIE_SECURE", default=None if not environment.is_development else False
    )
    if not environment.is_development and not secure:
        reader.fail(
            "must be true outside development. A session cookie without Secure "
            "is a session cookie an attacker can strip TLS to read.",
            "WEB_COOKIE_SECURE",
            refusal="S-03",
        )
    default_name = "__Host-fb_session" if secure else "fb_session_dev"
    cookie_name = reader.optional("WEB_SESSION_COOKIE_NAME", default_name)
    # As with `_Reader.integer`, a recorded problem is followed by a *usable*
    # fallback: `SessionSettings` enforces the same rule in its constructor
    # (2026-08-15), so keeping the operator's rejected name here would raise
    # there and hide the rest of the configuration problems.
    if secure and not cookie_name.startswith("__Host-"):
        reader.fail(
            "must carry the __Host- prefix when cookies are secure (N-05). The "
            "prefix is what makes the cookie host-only in the browser rather "
            "than only in our intent.",
            "WEB_SESSION_COOKIE_NAME",
            refusal="S-03",
        )
        cookie_name = default_name
    if not secure and cookie_name.startswith("__Host-"):
        reader.fail(
            "uses the __Host- prefix, which browsers refuse without Secure. The "
            "development name must be distinct.",
            "WEB_SESSION_COOKIE_NAME",
        )
        cookie_name = default_name
    transaction_cookie = (
        "__Host-fb_login_txn" if secure else "fb_login_txn_dev"
    )
    def bounded(variable: str, field_name: str) -> int:
        """One accepted bound, read from the register rather than restated.

        The ceiling *is* the accepted default: a policy value that may only be
        tightened has nothing looser to fall back to when the variable is unset.
        Taking both from the register is what keeps this reader and
        `SessionSettings.__post_init__` from drifting apart — the failure mode
        the second gate exists to catch would otherwise be introduced by editing
        one of the two copies. Since 2026-08-15 the accept/refuse decision is the
        same function the constructor calls, so the two cannot disagree about the
        *type* either, which is how they last drifted.
        """
        return reader.registered_integer(variable, field_name, SESSION_BOUNDS)

    return SessionSettings(
        cookie_name=cookie_name,
        cookie_secure=secure,
        idle_minutes=bounded("WEB_SESSION_IDLE_MINUTES", "idle_minutes"),
        absolute_hours=bounded("WEB_SESSION_ABSOLUTE_HOURS", "absolute_hours"),
        emergency_idle_minutes=bounded(
            "WEB_EMERGENCY_SESSION_IDLE_MINUTES", "emergency_idle_minutes"
        ),
        emergency_absolute_minutes=bounded(
            "WEB_EMERGENCY_SESSION_ABSOLUTE_MINUTES", "emergency_absolute_minutes"
        ),
        max_sessions_per_account=bounded(
            "WEB_MAX_SESSIONS_PER_ACCOUNT", "max_sessions_per_account"
        ),
        login_transaction_cookie_name=transaction_cookie,
        oauth_transaction_minutes=bounded(
            "WEB_OAUTH_TRANSACTION_MINUTES", "oauth_transaction_minutes"
        ),
    )


def _read_webauthn(
    reader: _Reader, public_origin: str, allowed_hosts: tuple[str, ...]
) -> WebAuthnSettings:
    rp_id = reader.required("WEB_WEBAUTHN_RP_ID").lower()
    rp_name = reader.optional("WEB_WEBAUTHN_RP_NAME", "Freedom Blades")
    configured_origins = reader.csv("WEB_WEBAUTHN_ALLOWED_ORIGINS", required=False)
    origins = configured_origins or (public_origin,)
    verification = reader.optional("WEB_WEBAUTHN_USER_VERIFICATION", "required")
    if verification != "required":
        reader.fail(
            "must be 'required' (N-60). A break-glass credential that can be "
            "presented without user verification is a key somebody found.",
            "WEB_WEBAUTHN_USER_VERIFICATION",
            refusal="S-10",
        )
    public_host = (urlsplit(public_origin).hostname or "").lower()
    if rp_id and public_host:
        if rp_id != public_host:
            # Stricter than the contract's "must not be a registrable-domain
            # suffix shared with the Foundry hosts", and deliberately so: the
            # Foundry instances live under the same registrable domain
            # (topology §2), so *any* RP ID broader than the portal's own host is
            # an RP ID they could also be reached under. Tightening a policy is
            # permitted; loosening it is not.
            reader.fail(
                "must equal the public origin's own host. A broader relying-party "
                "identifier would also cover the sibling Foundry hostnames under "
                "the same registrable domain, and a page served there could then "
                "use the platform's credentials.",
                "WEB_WEBAUTHN_RP_ID",
                "WEB_PUBLIC_ORIGIN",
                refusal="S-09",
            )
        for host in allowed_hosts:
            if host != public_host and _is_suffix_domain(rp_id, host):
                reader.fail(
                    "is a suffix of another allowed host, so a credential scoped "
                    "to it would be usable there as well.",
                    "WEB_WEBAUTHN_RP_ID",
                    "WEB_ALLOWED_HOSTS",
                    refusal="S-09",
                )
                break
    for origin in origins:
        if origin != public_origin:
            reader.fail(
                "must be a subset of the public origin (N-60).",
                "WEB_WEBAUTHN_ALLOWED_ORIGINS",
                "WEB_PUBLIC_ORIGIN",
                refusal="S-09",
            )
            break
    # The same in-range-fallback discipline `_Reader.integer` uses, and needed
    # here for the same reason: `WebAuthnSettings` enforces the shape of these
    # values in its own constructor (2026-08-15, I-10), so handing it a refused
    # one would raise mid-collection and cost the operator the rest of the list.
    # A run that recorded a problem never returns settings, so no fallback is
    # ever a value the process runs under.
    if not _is_hostname(rp_id):
        if rp_id:
            reader.fail(
                "must be a hostname: a relying-party identifier is a domain, and "
                "the browser derives the one it presents from the origin.",
                "WEB_WEBAUTHN_RP_ID",
                refusal="S-09",
            )
        rp_id = _UNSET_HOSTNAME
    if not all(_is_origin_shaped(origin) for origin in origins):
        if configured_origins:
            reader.fail(
                "must list exact origins: one token each, with no spaces.",
                "WEB_WEBAUTHN_ALLOWED_ORIGINS",
                refusal="S-09",
            )
        # Otherwise the malformation is `WEB_PUBLIC_ORIGIN`'s, which
        # `_read_public_origin` has already reported against its own name.
        origins = (_UNSET_ORIGIN,)
    if verification != ACCEPTED_USER_VERIFICATION:
        verification = ACCEPTED_USER_VERIFICATION
    return WebAuthnSettings(
        rp_id=rp_id,
        rp_name=rp_name,
        allowed_origins=tuple(origins),
        user_verification=verification,
        recovery_grant_minutes=reader.registered_integer(
            "WEB_RECOVERY_GRANT_MINUTES", "recovery_grant_minutes", WEBAUTHN_BOUNDS
        ),
    )


def _is_suffix_domain(candidate: str, host: str) -> bool:
    """True when `candidate` is `host` or a label-aligned suffix of it."""
    return host == candidate or host.endswith("." + candidate)


def _is_origin_shaped(value: object) -> bool:
    """One token, no whitespace, not empty — the shape an *exact* origin has.

    Deliberately no more than that. Whether an allowed origin is the **right**
    origin is S-09's question and is answered against `WEB_PUBLIC_ORIGIN`, a
    value `WebAuthnSettings` does not carry; a syntactic URL check here would be
    a second, weaker version of that rule rather than a property of this type.
    """
    return isinstance(value, str) and bool(value) and value.split() == [value]


def _read_encryption(reader: _Reader) -> EncryptionKeyring:
    raw = reader.csv("WEB_TOKEN_ENCRYPTION_KEYS")
    keys: list[EncryptionKey] = []
    seen: set[int] = set()
    for entry in raw:
        match = _KEY_ENTRY.match(entry)
        if match is None:
            reader.fail(
                "must be a comma-separated list of 'version:base64key' entries, "
                "newest first.",
                "WEB_TOKEN_ENCRYPTION_KEYS",
                refusal="S-08",
            )
            continue
        version = int(match.group("version"))
        material = _decode_key_material(match.group("material"))
        if len(material) != 32:
            reader.fail(
                "carries a key that is not 32 bytes. AES-256-GCM takes a 256-bit "
                "key; a shorter one is a weaker cipher wearing its name.",
                "WEB_TOKEN_ENCRYPTION_KEYS",
                refusal="S-08",
            )
            continue
        if version in seen:
            reader.fail(
                "lists the same key version twice, so which key encrypts is "
                "undecidable.",
                "WEB_TOKEN_ENCRYPTION_KEYS",
                refusal="S-08",
            )
            continue
        seen.add(version)
        keys.append(EncryptionKey(version=version, material=material))
    if not keys:
        reader.fail(
            "must configure at least one 32-byte versioned key.",
            "WEB_TOKEN_ENCRYPTION_KEYS",
            refusal="S-08",
        )
        return EncryptionKeyring(keys=(), active_version=0)
    active = reader.integer(
        "WEB_TOKEN_ENCRYPTION_ACTIVE_VERSION", default=keys[0].version, minimum=0
    )
    if active not in seen:
        reader.fail(
            "names a key version that is not configured, so no new row could be "
            "encrypted.",
            "WEB_TOKEN_ENCRYPTION_ACTIVE_VERSION",
            "WEB_TOKEN_ENCRYPTION_KEYS",
            refusal="S-08",
        )
        active = keys[0].version
    return EncryptionKeyring(keys=tuple(keys), active_version=active)


def _require_distinct_keys(
    reader: _Reader,
    csrf: SecretKey,
    cursor: SecretKey,
    client_digest: SecretKey,
    encryption: EncryptionKeyring,
) -> None:
    """S-08's separation half: the four keys must differ from one another.

    Key separation is what stops a CSRF token from being a valid pagination
    cursor, and what stops either from being usable as encryption key material.
    """
    material = [
        ("WEB_SECRET_KEY_CSRF", csrf.material),
        ("WEB_SECRET_KEY_CURSOR", cursor.material),
        ("WEB_SECRET_KEY_CLIENT_DIGEST", client_digest.material),
    ]
    if encryption.keys:
        try:
            material.append(
                ("WEB_TOKEN_ENCRYPTION_KEYS", encryption.active.material)
            )
        except KeyError:
            pass
    for index, (name, value) in enumerate(material):
        if not value:
            continue
        for other_name, other_value in material[index + 1 :]:
            if value == other_value:
                reader.fail(
                    "shares key material with another secret. Key separation is "
                    "what stops one token being valid in another position.",
                    name,
                    other_name,
                    refusal="S-08",
                )


def _read_rate_limits(reader: _Reader) -> RateLimitSettings:
    """Every budget from `RATE_LIMIT_BOUNDS`; not one of them written twice."""

    def bounded(variable: str, field_name: str) -> int:
        return reader.registered_integer(variable, field_name, RATE_LIMIT_BOUNDS)

    return RateLimitSettings(
        window_minutes=bounded("WEB_RATE_LIMIT_WINDOW_MINUTES", "window_minutes"),
        oauth_starts_per_ip=bounded(
            "WEB_RATE_LIMIT_OAUTH_STARTS", "oauth_starts_per_ip"
        ),
        oauth_callbacks_per_ip=bounded(
            "WEB_RATE_LIMIT_OAUTH_CALLBACKS", "oauth_callbacks_per_ip"
        ),
        webauthn_assertions_per_ip=bounded(
            "WEB_RATE_LIMIT_WEBAUTHN_PER_IP", "webauthn_assertions_per_ip"
        ),
        webauthn_assertions_per_account=bounded(
            "WEB_RATE_LIMIT_WEBAUTHN_PER_ACCOUNT", "webauthn_assertions_per_account"
        ),
        webauthn_account_window_minutes=bounded(
            "WEB_RATE_LIMIT_WEBAUTHN_ACCOUNT_WINDOW_MINUTES",
            "webauthn_account_window_minutes",
        ),
        recovery_attempts_per_ip=bounded(
            "WEB_RATE_LIMIT_RECOVERY_PER_IP", "recovery_attempts_per_ip"
        ),
        recovery_attempts_per_grant=bounded(
            "WEB_RATE_LIMIT_RECOVERY_PER_GRANT", "recovery_attempts_per_grant"
        ),
        cleanup_after_minutes=bounded(
            "WEB_RATE_LIMIT_CLEANUP_MINUTES", "cleanup_after_minutes"
        ),
    )


def _read_bounds(reader: _Reader) -> BoundsSettings:
    def bounded(variable: str, field_name: str) -> int:
        return reader.registered_integer(variable, field_name, REQUEST_BOUNDS)

    audit_max = bounded("WEB_AUDIT_PAGE_SIZE_MAX", "audit_page_size_max")
    audit_default = bounded("WEB_AUDIT_PAGE_SIZE_DEFAULT", "audit_page_size_default")
    if audit_default > audit_max:
        reader.fail(
            "cannot exceed the maximum page size.",
            "WEB_AUDIT_PAGE_SIZE_DEFAULT",
            "WEB_AUDIT_PAGE_SIZE_MAX",
            refusal="S-10",
        )
        # The same in-range fallback every other refusal here uses: `BoundsSettings`
        # enforces this relationship in its own constructor (2026-08-15, I-10), so
        # passing the refused pair on would raise before the remaining variables
        # were read. Tightening the default to the configured maximum is the
        # narrower of the two ways to satisfy the relationship.
        audit_default = audit_max
    return BoundsSettings(
        max_request_bytes=bounded("WEB_MAX_REQUEST_BYTES", "max_request_bytes"),
        trusted_proxy_hops=bounded("WEB_TRUSTED_PROXY_HOPS", "trusted_proxy_hops"),
        membership_cache_seconds=bounded(
            "WEB_MEMBERSHIP_CACHE_SECONDS", "membership_cache_seconds"
        ),
        membership_grace_seconds=bounded(
            "WEB_MEMBERSHIP_GRACE_SECONDS", "membership_grace_seconds"
        ),
        audit_page_size_default=audit_default,
        audit_page_size_max=audit_max,
        poll_min_seconds=bounded("WEB_POLL_MIN_SECONDS", "poll_min_seconds"),
    )


def _read_worker(reader: _Reader) -> WorkerSettings:
    enabled = reader.boolean("WORKER_ENABLED", default=False)
    root_value = reader.raw("WORKER_ARTIFACT_ROOT")
    root = Path(root_value) if root_value else None
    if root is not None and not root.is_absolute():
        reader.fail(
            "must be an absolute path.", "WORKER_ARTIFACT_ROOT", refusal="S-12"
        )
        root = None
    def bounded(variable: str, field_name: str) -> int:
        return reader.registered_integer(variable, field_name, WORKER_BOUNDS)

    return WorkerSettings(
        enabled=enabled,
        concurrency=bounded("WORKER_CONCURRENCY", "concurrency"),
        lease_seconds=bounded("WORKER_LEASE_SECONDS", "lease_seconds"),
        heartbeat_seconds=bounded("WORKER_HEARTBEAT_SECONDS", "heartbeat_seconds"),
        max_attempts=bounded("WORKER_MAX_ATTEMPTS", "max_attempts"),
        attempt_timeout_seconds=bounded(
            "WORKER_ATTEMPT_TIMEOUT_SECONDS", "attempt_timeout_seconds"
        ),
        queue_max_depth=bounded("WORKER_QUEUE_MAX_DEPTH", "queue_max_depth"),
        artifact_root=root,
    )


__all__ = [
    "ACCEPTED_PROVIDER_KEYS",
    "ACCEPTED_USER_VERIFICATION",
    "CANONICAL_SETTINGS_GRAPH",
    "BoundsSettings",
    "ConfigurationError",
    "ConfigurationProblem",
    "DATABASE_POOL_BOUNDS",
    "DatabasePoolSettings",
    "DiscordProviderSettings",
    "EncryptionKey",
    "EncryptionKeyring",
    "PRODUCTION_GUILD_ID",
    "PRODUCTION_ORIGIN",
    "PRODUCTION_REDIRECT_URI",
    "PolicyBound",
    "RATE_LIMIT_BOUNDS",
    "REQUEST_BOUNDS",
    "REQUIRED_OAUTH_SCOPES",
    "RateLimitSettings",
    "SESSION_BOUNDS",
    "SESSION_CEILINGS",
    "SETTINGS_NUMERIC_BOUNDS",
    "SecretKey",
    "SessionSettings",
    "SettingsAuthorityError",
    "WEBAUTHN_BOUNDS",
    "WORKER_BOUNDS",
    "WebAuthnSettings",
    "WebEnvironment",
    "WebSettings",
    "WorkerSettings",
    "canonical_settings",
    "canonical_web_settings",
    "policy_number_problem",
    "require_canonical",
    "require_canonical_web_settings",
    "session_policy_problem",
    "session_policy_problems",
    "settings_numeric_problems",
    "validate_session_policy_values",
]
