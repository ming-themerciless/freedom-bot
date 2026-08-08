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
    """
    return hashlib.sha256("\n".join(parts).encode("utf-8")).digest()
