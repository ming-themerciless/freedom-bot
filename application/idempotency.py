"""A completed operation's receipt, keyed by what the caller asked for.

Two different questions have to stay separate, and conflating them is the
classic idempotency defect:

- **"have I seen this key?"** — answered by `(scope, key)`, which the database
  makes unique;
- **"was it the same request?"** — answered by `request_hash`, a SHA-256 of the
  bound inputs of the operation the key was spent on.

Same key and same hash is a **retry**: the caller gets the original receipt
back, byte for byte, and nothing happens a second time. Same key and a
different hash is a **conflict**: the caller reused a key for something else and
is refused, because returning the original receipt would describe an operation
this request is not.

The receipt itself is stored, so a retry never recomputes anything. A recomputed
receipt describes the system as it is now, while every identifier in it claims
to describe the moment the operation committed — the two instants diverge, and
the caller cannot tell.
"""
from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping
from uuid import UUID, uuid4

#: Matches the `idempotency_keys.key` column, so an over-long key is refused
#: where it can be explained rather than truncated by the database.
KEY_MAX_LENGTH = 255

#: The SHA-256 digest width the `request_hash` check constraint enforces.
REQUEST_HASH_BYTES = 32


class IdempotencyKeyError(ValueError):
    """The caller's key cannot be used. Nothing was written."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class IdempotencyStatus(Enum):
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class IdempotencyRecord:
    """One key, what it was spent on, and the receipt it earned."""

    scope: str
    key: str
    request_hash: bytes
    status: IdempotencyStatus
    response: Mapping[str, Any] | None = None
    #: The admission generation this receipt was earned under, for the scopes
    #: that are fenced. `None` for every other scope.
    #:
    #: Writing this row is what makes a snapshot submission durable — on the
    #: new-bytes path and on the duplicate-bytes path where no snapshot row is
    #: created — so the foreign key it carries is the single point every
    #: acceptance passes through, and the lock that check takes is what
    #: serializes an acceptance against a settlement closure. See
    #: `application/admissions.py`.
    admission_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.scope.strip():
            raise ValueError("An idempotency record requires a scope.")
        validate_key(self.key)
        if len(self.request_hash) != REQUEST_HASH_BYTES:
            raise ValueError(
                f"An idempotency request hash is {REQUEST_HASH_BYTES} bytes; "
                f"this one is {len(self.request_hash)}."
            )

    def matches(self, request_hash: bytes) -> bool:
        return self.request_hash == request_hash


def validate_key(key: str) -> str:
    """Refuse a key that cannot be stored, matched or rendered safely.

    The rules are the ones `application.snapshots.SnapshotImportRecord` applies
    to its own request key, for the same reasons: an over-long key would be a
    driver error rather than an explanation, and a control character would
    corrupt every later rendering of an append-only row.

    This bounds the *column*, not the exposure. Keeping caller text out of
    permanent history is `request_key_digest`'s job, not this function's.
    """
    # Type before every value rule, for the reason `application/commands.py`
    # gives about its own text fields: `.strip()` on a value never established
    # as text leaves this validator as a raw `AttributeError`, and `bytes` —
    # which has a `.strip()` and a `len()` of its own — passed the blank and
    # length rules and failed only inside the control-character scan below, as
    # an unrelated `TypeError`. Neither is an `IdempotencyKeyError`, so both
    # escaped `CommandEnvelope`'s documented
    # `InvalidEnvelopeError(code="invalid_request_key")` contract and the
    # Foundry submission boundary's `SubmissionRefused`.
    #
    # This value is what makes a retry recognisable as a retry. A key that is
    # not `str` can never match the `str` a previous attempt stored, so
    # admitting one would spend a fresh key on every retry — the duplicate
    # execution the mechanism exists to prevent. Refused, therefore, and never
    # coerced with `str(...)`, decoded, normalized or truncated: the offending
    # type is named, the offending value never is.
    if not isinstance(key, str):
        raise IdempotencyKeyError(
            "invalid_request_key",
            f"A request key is text, not {type(key).__name__}.",
        )
    if not key.strip():
        raise IdempotencyKeyError(
            "invalid_request_key", "A request key is required and may not be blank."
        )
    if len(key) > KEY_MAX_LENGTH:
        raise IdempotencyKeyError(
            "invalid_request_key",
            f"A request key may be at most {KEY_MAX_LENGTH} characters; this "
            f"one is {len(key)}.",
        )
    if any(character < " " or character == "\x7f" for character in key):
        raise IdempotencyKeyError(
            "invalid_request_key",
            "A request key must be printable text. It is recorded verbatim in "
            "append-only history, so a control character in it would corrupt "
            "every later rendering of that record.",
        )
    return key


def request_hash(*parts: str) -> bytes:
    """The 32-byte digest of the bound inputs a key was spent on.

    Newline-joined rather than concatenated, so two different splits of the same
    text cannot produce the same digest.

    **Ambiguous for anything but fixed-shape input**, which is why
    `canonical_request_hash` exists beside it. Joining on a separator only keeps
    two field lists apart while no field can contain the separator; a reason
    holding a newline, or a field list whose length varies, collides. This form
    is retained for the one caller whose inputs are a fixed pair of a scope and a
    hex checksum (`application/foundry/submission.py`), where neither can.
    """
    return hashlib.sha256("\n".join(parts).encode("utf-8")).digest()


#: What a canonical field may hold: text, a whole number, or nothing at all.
#:
#: `None` is a *value* rather than a missing field. "This command compensates
#: nothing" and "this command compensates the transaction named by the empty
#: string" are different statements, and a canonicalization that rendered both
#: as `""` would let one be replayed as the other.
CanonicalValue = str | int | None

#: One byte per value, so a type cannot be changed without changing the digest.
#: An integer rendered as text and the same text supplied as text are different
#: fields; without a tag they would not be.
_ABSENT = b"\x00"
_TEXT = b"\x01"
_INTEGER = b"\x02"

#: Every length is written in this many big-endian bytes. Fixed width, so the
#: length prefix itself needs no delimiter.
_LENGTH_BYTES = 8


def canonical_request_hash(
    schema: str, fields: Sequence[tuple[str, CanonicalValue]]
) -> bytes:
    """The 32-byte digest of a *named, typed, length-delimited* field list.

    Three properties, and each of them is a defect this replaces:

    **Length-delimited, so no sequence of fields can collide with another.**
    Every name and every value is written as its byte length followed by its
    bytes, with no separator anywhere. `[("a", "bc")]` and `[("ab", "c")]` are
    therefore different digests, where a delimiter-joined encoding makes them
    equal as soon as a field can contain the delimiter.

    **Typed, so a value cannot change meaning without changing the digest.**
    The integer `1`, the text `"1"` and an absent field are three digests.

    **Versioned, through `schema`.** The digest is stored durably in
    `idempotency_keys.request_hash` and compared against months later. A stored
    key is only interpretable against the field list that produced it, so the
    schema name is the first thing hashed: changing what the fields *mean*
    changes the schema, and every stored key under the old schema keeps meaning
    what it meant. It does not migrate them — it stops them being silently
    reinterpreted.

    The field count is bound in too, so a truncated or extended list cannot
    match a shorter or longer one.
    """
    digest = hashlib.sha256()
    digest.update(_framed(schema.encode("utf-8")))
    digest.update(len(fields).to_bytes(_LENGTH_BYTES, "big"))
    for name, value in fields:
        digest.update(_framed(name.encode("utf-8")))
        digest.update(_tagged(value))
    return digest.digest()


def _tagged(value: CanonicalValue) -> bytes:
    if value is None:
        return _ABSENT
    if isinstance(value, bool):
        # `bool` is an `int` subclass, and `True` would otherwise hash as the
        # integer 1 — the same silent widening `domain/quantities.py` refuses.
        raise TypeError(
            "A canonical field holds text, a whole number or nothing. A boolean "
            "is not an amount and is not a name; render it at the call site, "
            "where what it means is visible."
        )
    if isinstance(value, int):
        return _INTEGER + _framed(str(value).encode("ascii"))
    if isinstance(value, str):
        return _TEXT + _framed(value.encode("utf-8"))
    raise TypeError(
        f"A canonical field cannot hold {type(value).__name__}. Render it as "
        "text or a whole number at the call site, where the conversion is "
        "explicit and testable."
    )


def _framed(raw: bytes) -> bytes:
    return len(raw).to_bytes(_LENGTH_BYTES, "big") + raw
