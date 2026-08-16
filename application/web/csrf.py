"""The synchronizer token of N-17, derived rather than stored.

`base64url(HMAC-SHA256(csrf_signing_key, session_id))`, recomputed for each
render and compared in constant time. Three properties follow from that one line,
and each is a requirement somewhere else in the contract:

- **Session-bound.** A token minted for one session verifies under no other.
- **Rotates with the session.** Session rotation creates a new row with a new id
  (SM-02), so the derived token changes without anything having to remember to
  change it. N-17's "rotates with the session" is therefore structural.
- **Nothing is stored.** A database read never yields a usable token, and there
  is no second column to keep in sync with the first.

**This is a synchronizer token, not a double-submit cookie.** The token is
rendered into the form or into `hx-headers` server-side; it is never read from a
cookie by script. A double-submit scheme would be satisfied by any attacker who
can set a cookie on the site, which is a weaker property than the one the
delivery plan accepted.

The token is verified **before the application service runs** (route contract
§2.1 step 6), and `TC-SEC-02` proves that by asserting the service was never
called on a refusal.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
from uuid import UUID

from application.web.config import SecretKey


def issue(signing_key: SecretKey, session_id: UUID) -> str:
    """The token to render for this session. Deterministic, so nothing is stored."""
    digest = hmac.new(
        signing_key.material, str(session_id).encode("ascii"), hashlib.sha256
    ).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def verify(signing_key: SecretKey, session_id: UUID, presented: str | None) -> bool:
    """Constant-time comparison against the token this session's id derives.

    A missing token is a failure rather than a skip: a mutation that arrives
    without one is either a cross-site request or a bug, and both should be
    refused. `hmac.compare_digest` is used rather than `==` so the comparison's
    timing does not reveal how much of the token was right.
    """
    if not presented:
        return False
    expected = issue(signing_key, session_id)
    return hmac.compare_digest(expected, presented)


__all__ = ["issue", "verify"]
