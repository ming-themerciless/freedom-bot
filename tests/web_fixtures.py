"""Shared doubles and a synthetic configuration for the portal's tests.

Nothing here touches a real Discord application, a real guild or a real
credential (delivery plan §10: no implementation package may use the production
Discord application or guild for automated tests). The guild snowflake is
synthetic and outside the range Discord has issued, which `WebSettings` refuses
to confuse with production anyway (S-07).
"""
from __future__ import annotations

import base64
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID, uuid4

from application.web.config import WebSettings
from application.web.providers import (
    ProviderMembership,
    ProviderRefused,
    ProviderTokens,
    ProviderUnavailable,
    VerifiedIdentity,
)

TEST_GUILD_ID = 900000000000000001
BOOTSTRAP_ADMIN_ROLE_ID = 900000000000000002
COUNCIL_ROLE_ID = 900000000000000003
DM_ROLE_ID = 900000000000000004
PUBLIC_ORIGIN = "https://portal.test"


def _key(seed: bytes) -> str:
    return base64.b64encode(seed * 32)[:44].decode("ascii")


def web_environment(tmp_path: Path, **overrides: str) -> dict[str, str]:
    """A complete, valid, synthetic environment. Override one key to break one rule."""
    values = {
        "WEB_ENVIRONMENT": "test",
        "WEB_PUBLIC_ORIGIN": PUBLIC_ORIGIN,
        "WEB_ALLOWED_HOSTS": "portal.test",
        "WEB_KILL_SWITCH_FILE": str(tmp_path / "kill-switch"),
        "WEB_SECRET_KEY_CSRF": _key(b"c"),
        "WEB_SECRET_KEY_CURSOR": _key(b"u"),
        "WEB_SECRET_KEY_CLIENT_DIGEST": _key(b"d"),
        "WEB_DATABASE_URL": "postgresql+psycopg:///freedom_test",
        "WEB_PROVIDER_REGISTRY": "discord",
        "WEB_DISCORD_CLIENT_ID": "1234567890",
        "WEB_DISCORD_CLIENT_SECRET": "synthetic-provider-secret",
        "WEB_DISCORD_REDIRECT_URI": f"{PUBLIC_ORIGIN}/auth/discord/callback",
        "WEB_DISCORD_SCOPES": "identify,guilds.members.read",
        "WEB_DISCORD_GUILD_ID": str(TEST_GUILD_ID),
        "WEB_BOOTSTRAP_ADMIN_ROLE_ID": str(BOOTSTRAP_ADMIN_ROLE_ID),
        "WEB_WEBAUTHN_RP_ID": "portal.test",
        "WEB_TOKEN_ENCRYPTION_KEYS": f"1:{_key(b'k')}",
        "WEB_TOKEN_ENCRYPTION_ACTIVE_VERSION": "1",
        "WEB_COOKIE_SECURE": "true",
    }
    values.update(overrides)
    return values


def web_settings(tmp_path: Path, **overrides: str) -> WebSettings:
    return WebSettings.from_environment(web_environment(tmp_path, **overrides))


# ---------------------------------------------------------------------------
# Provider doubles
# ---------------------------------------------------------------------------


@dataclass
class FakeDiscordProvider:
    """A provider that answers from a script instead of from the network.

    It is a *double*, not a mock of `httpx`: the tests that use it are about what
    the platform does with a verified identity, and driving them through a fake
    HTTP layer would be testing `httpx`.
    """

    provider_key: str = "discord"
    subject: str = "700000000000000001"
    username: str = "synthetic-member"
    global_name: str | None = None
    is_member: bool = True
    role_ids: frozenset[int] = field(default_factory=frozenset)
    guild_id: int = TEST_GUILD_ID
    #: Set to make **every** call raise, which is what "Discord is entirely
    #: unavailable" means for TC-BG-02 and the TC-OUT group.
    unavailable: bool = False
    refuse_exchange: bool = False
    #: The four narrower faults. `exchange` and `verify` are separate network
    #: calls with separate failure modes, and the callback's refusal boundary has
    #: to classify each of them — a double that can only fail "somewhere" cannot
    #: tell a test which of the two was exercised.
    unavailable_at_exchange: bool = False
    unavailable_at_verify: bool = False
    refuse_verify: bool = False
    authorization_calls: list[tuple[str, str]] = field(default_factory=list)
    exchange_calls: list[tuple[str, str]] = field(default_factory=list)

    def authorization_url(self, *, state: str, code_challenge: str) -> str:
        self.authorization_calls.append((state, code_challenge))
        return (
            "https://discord.example/oauth2/authorize"
            f"?state={state}&code_challenge={code_challenge}"
            "&scope=identify%20guilds.members.read"
        )

    async def exchange(self, *, code: str, code_verifier: str) -> ProviderTokens:
        if self.unavailable or self.unavailable_at_exchange:
            raise ProviderUnavailable("faulted double")
        if self.refuse_exchange:
            raise ProviderRefused("faulted double")
        self.exchange_calls.append((code, code_verifier))
        return ProviderTokens(
            # Stamped from this double's own key, exactly as the real adapter
            # stamps its constant. A double that left it out would let the suite
            # pass with a token result that cannot say where it came from.
            provider_key=self.provider_key,
            access_token=f"synthetic-access-token-{self.provider_key}",
            refresh_token=f"synthetic-refresh-token-{self.provider_key}",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            scopes="identify guilds.members.read",
        )

    async def verify(self, tokens: ProviderTokens) -> VerifiedIdentity:
        if self.unavailable or self.unavailable_at_verify:
            raise ProviderUnavailable("faulted double")
        if self.refuse_verify:
            raise ProviderRefused("faulted double")
        if tokens.provider_key != self.provider_key:
            # The real adapter refuses this before its first request; a double
            # that accepted it would make the cross-provider tests prove less
            # than they claim.
            raise ProviderRefused("token result was issued by another provider")
        return VerifiedIdentity(
            provider_key=self.provider_key,
            subject=self.subject,
            username=self.username,
            global_name=self.global_name,
            membership=ProviderMembership(
                guild_id=self.guild_id,
                is_member=self.is_member,
                role_ids=frozenset(self.role_ids),
                observed_at=datetime.now(timezone.utc),
            ),
        )


class RecordingAudit:
    """Collects `AuditEvent`s instead of writing them, for service-level tests."""

    def __init__(self) -> None:
        self.events: list = []

    def record(self, event) -> None:
        self.events.append(event)

    def actions(self) -> list[str]:
        return [event.action for event in self.events]


__all__ = [
    "BOOTSTRAP_ADMIN_ROLE_ID",
    "COUNCIL_ROLE_ID",
    "DM_ROLE_ID",
    "FakeDiscordProvider",
    "PUBLIC_ORIGIN",
    "RecordingAudit",
    "TEST_GUILD_ID",
    "web_environment",
    "web_settings",
]
