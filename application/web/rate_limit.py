"""Cross-process authentication rate limiting (N-18, N-30, N-32, N-33).

§7 of the delivery plan settled that a bounded in-process limiter is
insufficient: `freedom-web` and `freedom-worker` are separate processes, and two
of them each counting to ten is a budget of twenty. The counter therefore lives
in PostgreSQL, which is already a required, shared, transactional dependency —
adding Redis for one integer would not be the smallest justified dependency set.

**The known cost, stated rather than discovered later.** A fixed window admits a
2x burst at the boundary: ten starts at 09:59:59 and ten more at 10:00:00 are
twenty in one second, and both are within policy. That is recorded as residual
risk RR-03. A sliding window would cost a second row per event and a range scan
per check; for a control whose job is to make credential-stuffing tedious rather
than impossible, the fixed window is the right trade and the burst is bounded at
2x rather than unbounded.

**Addresses are never stored.** A bucket name carries an HMAC of the address
under a configured key. An unkeyed SHA-256 over an IPv4 address is reversible by
exhaustive search in seconds, so the key is what makes the digest a digest.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from adapters.web.repositories import RateLimitRepository, window_start
from application.web.config import RateLimitSettings, SecretKey, canonical_settings
from application.web.crypto import keyed_digest


class LimitedAction(Enum):
    """The five limited actions, each with its own budget.

    `WEBAUTHN_CHALLENGE` and `WEBAUTHN_ASSERTION` were **one** action until
    2026-08-24 (finding S-7/S3). Sharing a bucket made the two halves of one
    ceremony compete for the same five per-address units: a completed sign-in
    spent two of them and a cancelled prompt spent one, so three ordinary
    fumbles during a Discord outage exhausted the path that exists for outages.

    They are separate because they bound different things. Issuing a challenge
    inserts one short-lived row and reveals nothing — its budget is an
    availability and storage bound. Verifying an assertion is the guess: it is
    the operation N-32 exists to make tedious, and its budget is a security
    bound. One number cannot be set correctly for both.
    """

    OAUTH_START = "oauth_start"
    OAUTH_CALLBACK = "oauth_callback"
    WEBAUTHN_CHALLENGE = "webauthn_challenge"
    WEBAUTHN_ASSERTION = "webauthn_assertion"
    RECOVERY_LOGIN = "recovery_login"


@dataclass(frozen=True, slots=True)
class LimitDecision:
    allowed: bool
    count: int
    limit: int
    retry_after_seconds: int


class RateLimiter:
    """Fixed windows in `auth_rate_limits`, shared by every process.

    Each check is one statement. Two processes cannot both read nine and both
    write ten, because the increment and the read are the same
    `INSERT … ON CONFLICT DO UPDATE … RETURNING`.
    """

    __slots__ = ("_repository", "_settings", "_digest_key")

    def __init__(
        self,
        repository: RateLimitRepository,
        settings: RateLimitSettings,
        digest_key: SecretKey,
    ) -> None:
        """The budgets are read **once, here**, and checked before they are held.

        `canonical_settings` reads each of the ten numbers exactly once and
        rebuilds an ordinary `RateLimitSettings` from those locals, whose
        constructor holds them to the accepted register (2026-08-15, I-10).
        Without it, this object kept whatever was handed to it and re-read a
        budget on every check — so a subclass whose `oauth_starts_per_ip`
        answered `10` when it was looked at and something else when it was used,
        or an `int` subclass answering `False` to `count <= limit`, would have
        made the throttle decorative one request at a time rather than visibly at
        startup.
        """
        self._repository = repository
        self._settings = canonical_settings(settings, RateLimitSettings)
        self._digest_key = digest_key

    def check_ip(
        self, action: LimitedAction, *, client_ip: str, now: datetime
    ) -> LimitDecision:
        limit, window_minutes = self._budget_for(action)
        return self._check(
            bucket=f"{action.value}:ip:{self._digest(client_ip)}",
            limit=limit,
            window_minutes=window_minutes,
            now=now,
        )

    def check_account(
        self, action: LimitedAction, *, account_id, now: datetime
    ) -> LimitDecision:
        """N-32's second budget: per platform account, over a longer window.

        Deliberately lower than the per-address budget. The credential set is two
        keys held by one person; a hundred assertions against that account is an
        attack whatever address they arrive from.
        """
        return self._check(
            bucket=f"{action.value}:account:{account_id}",
            limit=self._settings.webauthn_assertions_per_account,
            window_minutes=self._settings.webauthn_account_window_minutes,
            now=now,
        )

    def check_credential(
        self, action: LimitedAction, *, credential_id: bytes, now: datetime
    ) -> LimitDecision:
        """The **same** budget, for a credential id that resolves to no account.

        It exists so that spending N-32's second budget cannot become an
        account-existence oracle (2026-08-16, P3.G1 security review). If only
        known credentials had an account bucket, the eleventh attempt against an
        enrolled credential would answer `rate_limited` while the eleventh
        attempt against an invented one still answered `invalid` — and that
        difference is exactly the fact break-glass refuses to disclose. With this
        bucket both answer `rate_limited` at the same attempt, in the same
        window, with the same retry hint.

        The bucket carries a keyed digest for the same reason an address does:
        a credential id is a public-key handle held by one authenticator, and
        the rate-limit table is not the place to accumulate a list of them. Rows
        are bounded by the per-address budget that runs first and by N-31's
        sweep, so an attacker cannot grow the table faster than five rows per
        address per ten minutes.
        """
        return self._check(
            bucket=f"{action.value}:credential:{self._digest(credential_id.hex())}",
            limit=self._settings.webauthn_assertions_per_account,
            window_minutes=self._settings.webauthn_account_window_minutes,
            now=now,
        )

    def _budget_for(self, action: LimitedAction) -> tuple[int, int]:
        settings = self._settings
        window = settings.window_minutes
        if action is LimitedAction.OAUTH_START:
            return settings.oauth_starts_per_ip, window
        if action is LimitedAction.OAUTH_CALLBACK:
            return settings.oauth_callbacks_per_ip, window
        if action is LimitedAction.WEBAUTHN_CHALLENGE:
            return settings.webauthn_challenges_per_ip, window
        if action is LimitedAction.WEBAUTHN_ASSERTION:
            return settings.webauthn_assertions_per_ip, window
        return settings.recovery_attempts_per_ip, window

    def _check(
        self, *, bucket: str, limit: int, window_minutes: int, now: datetime
    ) -> LimitDecision:
        start = window_start(now, minutes=window_minutes)
        count = self._repository.increment(bucket=bucket, window_start=start)
        window_end = start + timedelta(minutes=window_minutes)
        return LimitDecision(
            allowed=count <= limit,
            count=count,
            limit=limit,
            retry_after_seconds=max(1, int((window_end - now).total_seconds())),
        )

    def _digest(self, value: str) -> str:
        raw = keyed_digest(self._digest_key, value)
        # Sixteen bytes of a keyed digest, so the bucket name stays inside its
        # 120-character column while remaining far beyond guessing.
        return base64.urlsafe_b64encode(raw[:16]).decode("ascii").rstrip("=")

    def sweep(self, *, now: datetime) -> int:
        """N-31: bound the table's growth without introducing a scheduler."""
        return self._repository.purge(
            before=now - timedelta(minutes=self._settings.cleanup_after_minutes)
        )


__all__ = ["LimitDecision", "LimitedAction", "RateLimiter"]
