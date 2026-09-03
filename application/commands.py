"""What every state-changing request carries, and what it gets back.

A Discord slash command, a web route and the Foundry adapter all reach the same
use case, and each of them knows four things the use case cannot discover for
itself:

1. **who is asking** — `CommandCaller`, an *identity* and the surface it arrived
   on;
2. **which attempt this is** — the idempotency key, so a retry is recognisable
   as one rather than executed twice;
3. **what the caller believed** — `ExpectedVersion`, the aggregate version the
   caller read before deciding; and
4. **what to correlate it with** — a correlation id that ties the audit row, the
   log line and the receipt together.

`CommandEnvelope` carries exactly those and nothing else. It is the smallest
thing the Phase 4 ledger and idempotent-execution services actually consume;
every field below has a caller in `application/ledger.py`.

**The envelope carries authority as an identity, never as a privilege.** There
is deliberately no `guild_council: bool` here. `application/authorization.py`
exists because a resolved `AuthorizationContext` is a *reading* and a reading has
a time: permission is re-resolved through `AuthorizationPort` at the moment the
work is done. An envelope that carried a resolved capability would let a caller
present a privilege it held a minute ago — or one it never held, since the
envelope is built from the request.

**Nothing here is framework-shaped.** No Discord interaction, no HTTP request, no
A1 range, no ORM row, no SQL. An adapter builds an envelope out of its own
request and translates a refusal back into its own vocabulary; that translation
is the adapter's job and happens nowhere else (`.agents/AGENTS.md`: "Return typed
domain/application errors. Translate them to safe user messages only at an outer
boundary").

## Queries — the convention, deliberately without a protocol

Command/query separation is the rule (`.agents/AGENTS.md`): commands change state
and return a receipt; queries read and return view data with no hidden mutation;
`get`, `find`, `render` and `calculate` never persist. The **convention** for a
platform read query is therefore:

- a query takes the caller identity and its own bound inputs, never an envelope —
  it spends no idempotency key, has no expected version and writes no receipt;
- it returns typed view data owned by the package that migrated the fields, and
  a field no package has migrated yet is absent rather than guessed at; and
- it is authorized at the moment it runs, through the same port a command uses.

**No query protocol is defined here, and that is a decision rather than an
omission.** Under the final OD-52 amendment (2026-08-29) Phase 4 creates no
wallet query and no temporary Sheet adapter: package 5.2 introduces the typed
wallet query together with its production adapter and the character page that
consumes it. `.agents/AGENTS.md` forbids an abstraction without a real consumer,
and an interface written here to satisfy the word "query" would have exactly one
caller — its own test.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID

from application.audit import AuditSource
from application.idempotency import IdempotencyKeyError, validate_key

#: The scalar types a receipt fact may hold.
#:
#: Narrow on purpose. A receipt is stored verbatim in `idempotency_keys.response`
#: as JSON and read back by a retry, so anything that cannot survive that round
#: trip unchanged is refused here — where the call site is visible — rather than
#: at the driver, or silently, by arriving back as a different type than it left
#: as. `float` is absent for the reason `domain/quantities.py` gives: a money or
#: resource amount is a whole count of its smallest unit, and a receipt is the
#: last place a binary float should be able to enter the platform.
RECEIPT_SCALARS = (str, int, bool, type(None))


class InvalidEnvelopeError(ValueError):
    """The request cannot be made into an envelope. Nothing was attempted.

    A `ValueError` because it is a malformed input, and it is raised at
    construction so an invalid envelope cannot reach a use case at all. `code` is
    a stable name an adapter branches on; it is never the driver's, the
    framework's or the exception's own text.
    """

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class CommandCaller:
    """Who is asking, and through what.

    Exactly one attribution: a Discord user *or* a service principal. Both would
    be a request claiming to be two callers, and neither would be an
    unattributable mutation — `application/audit.py` refuses to record one for
    any human capability, and this refuses to build one.

    **Both identities are a lookup, never a grant.** This object is built out of
    the request, so `discord_user_id` and `principal_id` are exactly as
    trustworthy as the adapter that supplied them and no more. A use case turns
    either into authority only by asking a port at execution — `AuthorizationPort`
    for a person, `LedgerPrincipalPort` for a service principal — and validating
    the *shape* of an id here proves nothing about whether it exists or what it
    may do. Review finding P4-R2 was a service that read the mere presence of
    `principal_id` as an answer.
    """

    source: AuditSource
    discord_user_id: int | None = None
    principal_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.source, AuditSource):
            raise InvalidEnvelopeError(
                "invalid_caller",
                "A command caller must name the surface it arrived on as an "
                f"AuditSource, not {type(self.source).__name__}.",
            )
        identified = [
            name
            for name, value in (
                ("discord_user_id", self.discord_user_id),
                ("principal_id", self.principal_id),
            )
            if value is not None
        ]
        if len(identified) != 1:
            raise InvalidEnvelopeError(
                "invalid_caller",
                "A command caller is exactly one identity: a Discord user or a "
                f"service principal. This one names {identified or 'neither'}.",
            )
        if self.discord_user_id is not None:
            # Type before magnitude. `discord_user_id <= 0` alone is a
            # comparison rather than a check: `bool` is an `int` subclass, so a
            # flag would arrive as Discord user 1, and a value not orderable
            # against `0` would leave this constructor as a raw `TypeError` an
            # adapter cannot branch on. Nothing is coerced — a string of digits
            # is a refusal, not an integer, because the identity an audit row
            # attributes a mutation to must not depend on the adapter's typing.
            if isinstance(self.discord_user_id, bool) or not isinstance(
                self.discord_user_id, int
            ):
                raise InvalidEnvelopeError(
                    "invalid_caller",
                    "A Discord user is identified by a snowflake integer, not "
                    f"by {type(self.discord_user_id).__name__}.",
                )
            if self.discord_user_id <= 0:
                raise InvalidEnvelopeError(
                    "invalid_caller", "Discord IDs must be positive snowflakes."
                )
        if self.principal_id is not None:
            # Type before blankness, for the reason `ExpectedVersion` gives
            # about its own aggregate type: `.strip()` on a value never
            # established as text leaves this constructor as a raw
            # `AttributeError` an adapter cannot branch on, and `bytes` — which
            # has a `.strip()` of its own — would be admitted as an identity the
            # `str` lookup in `LedgerPrincipalPort.current_principal()` can
            # never match. Refused, never decoded and never coerced with
            # `str(...)`. Shape only: whether this identifier is configured, and
            # what it may do, stays the port's answer at execution.
            if not isinstance(self.principal_id, str):
                raise InvalidEnvelopeError(
                    "invalid_caller",
                    "A service principal is identified in text, not by "
                    f"{type(self.principal_id).__name__}.",
                )
            if not self.principal_id.strip():
                raise InvalidEnvelopeError(
                    "invalid_caller", "A service principal id may not be blank."
                )

    @property
    def is_human(self) -> bool:
        """A person is acting, so a capability must be resolved for them."""
        return self.discord_user_id is not None


@dataclass(frozen=True, slots=True)
class ExpectedVersion:
    """The version of the aggregate the caller read before deciding.

    It names *what* it is the version of, rather than being a bare integer.
    A precondition that does not say which aggregate it constrains is one an
    executor can check against the wrong thing and still pass — and the failure
    mode is a stale write that reported success.
    """

    aggregate_type: str
    aggregate_id: UUID
    version: int

    def __post_init__(self) -> None:
        # Established as text before it is stripped. `describes()` compares
        # against the `str` its caller passes, so a non-string name is a
        # precondition that can never be satisfied — and one with a `.strip()`
        # of its own, such as `bytes`, would be accepted here and then silently
        # fail to match forever. Refused, never coerced with `str(...)`.
        if not isinstance(self.aggregate_type, str):
            raise InvalidEnvelopeError(
                "invalid_expected_version",
                "An aggregate type is named in text, not by "
                f"{type(self.aggregate_type).__name__}.",
            )
        if not self.aggregate_type.strip():
            raise InvalidEnvelopeError(
                "invalid_expected_version",
                "An expected version must name the aggregate type it constrains.",
            )
        if not isinstance(self.aggregate_id, UUID):
            raise InvalidEnvelopeError(
                "invalid_expected_version",
                "An aggregate is identified by a stable UUID, not by "
                f"{type(self.aggregate_id).__name__}. Display names are mutable "
                "and are not identities.",
            )
        # `bool` before `int`: `isinstance(True, int)` is `True`, and a flag
        # arriving where a version belongs would be read as version 1.
        if isinstance(self.version, bool) or not isinstance(self.version, int):
            raise InvalidEnvelopeError(
                "invalid_expected_version",
                "An aggregate version is a whole number, not "
                f"{type(self.version).__name__}.",
            )
        if self.version < 0:
            raise InvalidEnvelopeError(
                "invalid_expected_version", "An aggregate version cannot be negative."
            )

    def describes(self, aggregate_type: str, aggregate_id: UUID) -> bool:
        return self.aggregate_type == aggregate_type and self.aggregate_id == aggregate_id


@dataclass(frozen=True, slots=True)
class CommandEnvelope:
    """The four things an adapter knows that a use case cannot discover."""

    caller: CommandCaller
    idempotency_key: str
    correlation_id: UUID
    #: Optional because not every command has an aggregate to be stale against —
    #: the *first* transaction in a book is posted against version 0, which is a
    #: value rather than an absence, but a command creating an aggregate has
    #: nothing to have read. A service that requires one says so itself.
    expected_version: ExpectedVersion | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.caller, CommandCaller):
            raise InvalidEnvelopeError(
                "invalid_caller",
                f"A command envelope carries a CommandCaller, not "
                f"{type(self.caller).__name__}.",
            )
        try:
            validate_key(self.idempotency_key)
        except IdempotencyKeyError as error:
            # Re-raised rather than propagated so an adapter has one exception
            # type to translate for an unusable envelope, while keeping the code
            # `application/idempotency.py` already publishes for this failure.
            raise InvalidEnvelopeError(error.code, str(error)) from None
        if not isinstance(self.correlation_id, UUID):
            raise InvalidEnvelopeError(
                "invalid_correlation_id",
                "A correlation id is a UUID, so an audit row, a log line and a "
                "receipt can be tied together without parsing free text.",
            )
        if self.expected_version is not None and not isinstance(
            self.expected_version, ExpectedVersion
        ):
            raise InvalidEnvelopeError(
                "invalid_expected_version",
                "An expected version is an ExpectedVersion naming its aggregate, "
                f"not a bare {type(self.expected_version).__name__}.",
            )

    def require_expected_version(
        self, aggregate_type: str, aggregate_id: UUID
    ) -> ExpectedVersion:
        """The precondition for this aggregate, or refuse the command.

        Refusing is the point. A command whose expected version is missing — or
        is a version of something else — is a caller that did not read what it is
        about to change, and executing it anyway is the lost update the
        precondition exists to prevent.
        """
        if self.expected_version is None:
            raise InvalidEnvelopeError(
                "missing_expected_version",
                f"This command changes {aggregate_type} {aggregate_id} and "
                "requires the version the caller read before deciding.",
            )
        if not self.expected_version.describes(aggregate_type, aggregate_id):
            raise InvalidEnvelopeError(
                "invalid_expected_version",
                "The expected version names "
                f"{self.expected_version.aggregate_type} "
                f"{self.expected_version.aggregate_id}, but this command changes "
                f"{aggregate_type} {aggregate_id}.",
            )
        return self.expected_version


@dataclass(frozen=True, slots=True)
class CommandReceipt:
    """What a command returns, and what a retry of it returns unchanged.

    **The receipt is stored, not recomputed.** `as_payload()` is written into
    `idempotency_keys.response` in the transaction that commits the effect, and a
    retry answers from `from_payload()`. Recomputing one would describe the
    system as it is *now* while every identifier in it claimed to describe the
    moment the command committed — and the caller could not tell the two apart.

    `duplicate` is therefore deliberately **not** part of the payload: it says
    something about *this call*, not about the operation, and storing it would
    make the first caller's receipt claim to be a replay of itself.
    """

    command: str
    correlation_id: UUID
    #: The aggregate version *after* the command, so the caller's next command
    #: has a precondition without a second read.
    version: int
    facts: Mapping[str, Any] = field(default_factory=dict)
    duplicate: bool = False

    def __post_init__(self) -> None:
        # Type before blankness, and `ValueError` rather than a new exception
        # type, because this constructor is also the *replay* boundary.
        # `from_payload()` catches `(KeyError, TypeError, ValueError)` and turns
        # a bad stored row into `StoredReceiptUnreadable`; `.strip()` on a value
        # never established as text raised `AttributeError`, which is in neither
        # tuple, so a spent key whose stored command is malformed escaped that
        # contract entirely — against a key whose effect may already have
        # committed, and which must therefore never be re-executed or invented.
        # `bytes`, having a `.strip()` of its own, was accepted instead: a
        # command name no `str` comparison could ever match.
        #
        # Correcting it here rather than by widening the catch list leaves
        # direct construction typed as well, and nothing is coerced with
        # `str(...)`, decoded or normalized. The message names the offending
        # type and never the offending value, so a malformed stored row cannot
        # be echoed into a log line or a caller's reply.
        if not isinstance(self.command, str):
            raise ValueError(
                "A command receipt names its command in text, not by "
                f"{type(self.command).__name__}."
            )
        if not self.command.strip():
            raise ValueError("A command receipt names the command that produced it.")
        if not isinstance(self.correlation_id, UUID):
            raise ValueError("A command receipt carries the command's correlation id.")
        if isinstance(self.version, bool) or not isinstance(self.version, int):
            raise ValueError("A resulting aggregate version is a whole number.")
        frozen = {}
        for key, value in dict(self.facts).items():
            if not isinstance(key, str):
                raise ValueError(
                    f"A receipt fact is keyed by text; this one is keyed by "
                    f"{type(key).__name__}."
                )
            if not isinstance(value, RECEIPT_SCALARS):
                raise ValueError(
                    f"Receipt fact {key!r} holds {type(value).__name__}, which "
                    "cannot round-trip through the stored receipt unchanged. "
                    "Render it as text or a whole number at the call site, where "
                    "the conversion is visible."
                )
            frozen[key] = value
        # Frozen, so a caller holding the dictionary it passed cannot alter what
        # the receipt says after the fact — the same rule `AuditEvent` applies.
        object.__setattr__(self, "facts", MappingProxyType(frozen))

    def as_payload(self) -> dict[str, Any]:
        """Exactly what is stored, and exactly what a replay is rebuilt from."""
        return {
            "command": self.command,
            "correlation_id": str(self.correlation_id),
            "version": self.version,
            "facts": dict(self.facts),
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any], *, duplicate: bool) -> CommandReceipt:
        """Rebuild a stored receipt, or refuse to invent one.

        Every field is required. A receipt missing one is not a receipt with a
        default — it is a row this code did not write, and answering a caller
        from it would be reporting an operation nobody can point to.
        """
        try:
            return cls(
                command=payload["command"],
                correlation_id=UUID(str(payload["correlation_id"])),
                version=payload["version"],
                facts=payload.get("facts") or {},
                duplicate=duplicate,
            )
        except (KeyError, TypeError, ValueError) as error:
            raise StoredReceiptUnreadable(str(error)) from None


class StoredReceiptUnreadable(RuntimeError):
    """A spent idempotency key's stored receipt could not be read back.

    Never resolved into a fresh execution and never into a plausible-looking
    receipt. The key is spent, so the effect may well have happened; running it
    again could duplicate it, and answering with a reconstruction would state
    facts nothing recorded.
    """
