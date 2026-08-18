"""N-64's opaque, HMAC-signed cursor, and N-21's page bounds.

Three rules, and each one is a requirement rather than a preference:

1. **Never an offset.** N-21 forbids an unbounded offset scan, and an offset is
   also wrong in a table that receives inserts while a reader is paging — a row
   added before the cursor shifts every later page by one and the reader either
   sees a row twice or never sees it. The cursor is a *position*: the sort key of
   the last row of the page just rendered, and the next page is everything
   strictly after it under the same total order.

2. **Signed, and refused rather than reset.** A cursor is a value the browser
   holds and hands back, so it is caller input. It is HMAC-signed with the
   dedicated cursor key (S-08 requires it to differ from the CSRF and digest
   keys), verified in constant time, and an unverifiable one is a **refusal**.
   Silently resetting to page one would hide tampering behind a working page, and
   the numeric register says so in as many words.

3. **The sort key is total.** Every ordering here ends in the row's primary key,
   so no two rows compare equal and `(key, id) > (key, id)` is a strict, complete
   order. A cursor over a non-total order silently drops rows that tie at a page
   boundary.

The signature covers the payload *and* the scope string. Scope is what stops a
cursor minted for one listing being replayed into another — a cursor from the
Council character index presented to the identity-migration proposal list would
otherwise verify, decode to a valid position, and page a different table.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
from dataclasses import dataclass
from typing import Sequence

from application.web.config import SecretKey
from application.web.errors import RefusalCode, WebRefusal
from application.web.view_models import (
    PAGE_SIZE_DEFAULT,
    PAGE_SIZE_MAXIMUM,
    Cursor,
)

#: The separator inside a payload. `\x1f` (unit separator) is used rather than a
#: printable character because it cannot occur in the values encoded here —
#: UUIDs, display names normalised to a sort key, and integers — so a value
#: containing the delimiter cannot forge a field boundary.
_FIELD = "\x1f"


class InvalidCursor(WebRefusal):
    """A cursor that does not verify, or that was minted for another listing.

    A `422` rather than a `400`: the caller can correct it by starting the
    listing again, and the route contract's validation-failure row is where a
    correctable input belongs. It is never silently ignored (N-64).
    """

    def __init__(self, correlation_id=None) -> None:
        super().__init__(
            RefusalCode.STALE_VERSION, status=422, correlation_id=correlation_id
        )


def _sign(key: SecretKey, scope: str, payload: str) -> str:
    material = f"{scope}{_FIELD}{payload}".encode("utf-8")
    digest = hmac.new(key.material, material, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def encode(key: SecretKey, *, scope: str, parts: Sequence[str]) -> str:
    """Mint a cursor for the position `parts` describes, inside `scope`."""
    payload = _FIELD.join(parts)
    encoded = base64.urlsafe_b64encode(payload.encode("utf-8")).decode("ascii").rstrip("=")
    return f"{encoded}.{_sign(key, scope, payload)}"


def decode(key: SecretKey, token: str | None, *, scope: str, arity: int) -> tuple[str, ...] | None:
    """The position `token` names, `None` when there is no token, or a refusal.

    `arity` is checked because a verified payload with the wrong number of
    fields is still a payload this listing cannot use, and unpacking it would
    raise somewhere less informative. Nothing about the failure distinguishes a
    forged signature from a malformed payload: both are the same answer to the
    caller.
    """
    if not token:
        return None
    encoded, separator, signature = token.partition(".")
    if not separator:
        raise InvalidCursor()
    try:
        payload = base64.urlsafe_b64decode(_pad(encoded)).decode("utf-8")
    except Exception:  # noqa: BLE001 - every malformed encoding is one outcome
        raise InvalidCursor() from None
    if not hmac.compare_digest(_sign(key, scope, payload), signature):
        raise InvalidCursor()
    parts = tuple(payload.split(_FIELD))
    if len(parts) != arity:
        raise InvalidCursor()
    return parts


def _pad(encoded: str) -> bytes:
    return (encoded + "=" * (-len(encoded) % 4)).encode("ascii")


def page_size(requested: str | None) -> int:
    """N-21: default 50, maximum 100. A request for 1000 is **clamped**.

    Clamped rather than refused, deliberately, and the asymmetry with the cursor
    above is the point: an oversized page is a caller asking for more than the
    platform will give, which has an obvious safe answer, while an unverifiable
    cursor is a caller presenting something the platform did not mint, which does
    not.
    """
    if requested is None:
        return PAGE_SIZE_DEFAULT
    try:
        value = int(requested)
    except (TypeError, ValueError):
        return PAGE_SIZE_DEFAULT
    if value < 1:
        return PAGE_SIZE_DEFAULT
    return min(value, PAGE_SIZE_MAXIMUM)


@dataclass(frozen=True, slots=True)
class Page:
    """One page of rows plus the cursor that continues it.

    Built by over-reading a single row: a repository asks for `size + 1` and
    hands the surplus here, so `has_more` is an observation rather than a second
    `COUNT(*)` over the same predicate.
    """

    rows: tuple
    cursor: Cursor

    @classmethod
    def of(
        cls,
        rows: Sequence,
        *,
        size: int,
        key: SecretKey,
        scope: str,
        position,
    ) -> "Page":
        materialised = tuple(rows)
        has_more = len(materialised) > size
        visible = materialised[:size]
        token = ""
        if has_more and visible:
            token = encode(key, scope=scope, parts=position(visible[-1]))
        return cls(rows=visible, cursor=Cursor(token=token, has_more=has_more))


__all__ = [
    "InvalidCursor",
    "Page",
    "decode",
    "encode",
    "page_size",
]
