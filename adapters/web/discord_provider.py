"""The Discord identity provider, behind the ADR 0010 D6 boundary.

Two outbound calls and no more: the token exchange, and one guild-member read.
Both are bounded by an explicit timeout and an explicit connection limit, and
both are `async` so nothing here blocks the event loop.

**Scopes are `identify` and `guilds.members.read`, exactly.** The narrower of the
two does the identifying; the wider one returns membership *and role snowflakes
for one guild*, which is what makes role verification a server-side fact rather
than something the browser tells us. No scope beyond those is requested, and a
configuration that asks for one is a startup refusal rather than a warning
(S-06).

**Failure is classified, not flattened.** `ProviderUnavailable` (timeout, 5xx,
429, connection error) and `ProviderRefused` (4xx on the exchange) mean different
things to the caller: the first must never be written into the membership
projection as an absence, because that would revoke a guild during an outage.

**A payload this adapter cannot read is a classified refusal, not a `500`.** A
provider that answers `200` with HTML, with a JSON array, with `expires_in:
"soon"` or with no `id` is *expected* behaviour at a network boundary — a proxy
error page, a version change, a partial outage — and the platform's answer to all
of them is `ProviderRefused`. Letting a `JSONDecodeError` or a `ValueError`
escape would answer the browser with an unhandled error carrying internal detail,
which is exactly what N-25 forbids. This is deliberately narrow: the reads below
are guarded individually and there is no blanket `except Exception` anywhere in
this module, so a genuine defect in *our* code still surfaces as one.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import httpx

from application.web.config import DiscordProviderSettings
from application.web.providers import (
    ProviderMembership,
    ProviderRefused,
    ProviderTokens,
    ProviderUnavailable,
    VerifiedIdentity,
)

#: Bounded, because this process is co-located with three Foundry instances, the
#: live bot and PostgreSQL (RAID R-24). An unbounded pool is an availability
#: defect waiting for a slow provider.
_LIMITS = httpx.Limits(max_connections=10, max_keepalive_connections=5)


class DiscordIdentityProvider:
    """`provider_key = "discord"`. Holds one `AsyncClient` for the process."""

    provider_key = "discord"

    __slots__ = ("_settings", "_client")

    def __init__(
        self, settings: DiscordProviderSettings, *, client: httpx.AsyncClient | None = None
    ) -> None:
        self._settings = settings
        self._client = client or httpx.AsyncClient(
            timeout=httpx.Timeout(settings.api_timeout_seconds),
            limits=_LIMITS,
            follow_redirects=False,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    def authorization_url(self, *, state: str, code_challenge: str) -> str:
        """Built entirely from configuration and the two minted values.

        Nothing the browser supplied reaches this URL. The `redirect_uri` is the
        configured one, which startup already checked shares the public origin
        (S-05), so a callback cannot be delivered somewhere else.
        """
        query = urlencode(
            {
                "client_id": self._settings.client_id,
                "response_type": "code",
                "redirect_uri": self._settings.redirect_uri,
                "scope": self._settings.scope_parameter,
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
                "prompt": "none",
            }
        )
        return f"{self._settings.authorization_url}?{query}"

    async def exchange(self, *, code: str, code_verifier: str) -> ProviderTokens:
        payload = {
            "client_id": self._settings.client_id,
            "client_secret": self._settings.client_secret.material.decode("utf-8"),
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._settings.redirect_uri,
            "code_verifier": code_verifier,
        }
        try:
            response = await self._client.post(
                self._settings.token_url,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        except httpx.HTTPError as error:
            raise ProviderUnavailable("token exchange transport failure") from error

        if response.status_code >= 500 or response.status_code == 429:
            raise ProviderUnavailable(f"token exchange status {response.status_code}")
        if response.status_code >= 400:
            # The provider's error body is deliberately not carried: it would end
            # up in a log line the user can quote, and it says nothing the
            # correlation id does not (N-25).
            raise ProviderRefused("token exchange refused")

        body = _json_object(response, "token exchange")
        access_token = _text(body.get("access_token"))
        if not access_token:
            raise ProviderRefused("token exchange returned no usable access token")
        return ProviderTokens(
            # This adapter's constant, never a field of the response. A key read
            # from the provider would be a key the provider could change, and the
            # completion claim binds to it.
            provider_key=self.provider_key,
            access_token=access_token,
            refresh_token=_text(body.get("refresh_token")) or None,
            expires_at=datetime.now(timezone.utc)
            + timedelta(seconds=max(_seconds(body.get("expires_in")), 60)),
            scopes=_text(body.get("scope")) or self._settings.scope_parameter,
        )

    async def verify(self, tokens: ProviderTokens) -> VerifiedIdentity:
        """`identify` gives the subject; `guilds.members.read` gives one guild.

        The member read is scoped to the configured guild id and to nothing else.
        A 404 from it is a **fact** — this person is not in that guild — and is
        the one non-2xx answer that is not an outage.

        **Another provider's tokens are refused before the first request.** Sending
        them would present a bearer token to Discord that Discord did not issue,
        and — far worse — would return a Discord identity resolved from a token
        this adapter did not obtain. That is the laundering step the provider
        binding exists to prevent, so it is refused here as well as at the
        completion claim: two independent places, neither relying on the other.
        """
        if tokens.provider_key != self.provider_key:
            raise ProviderRefused("token result was issued by another provider")
        headers = {"Authorization": f"Bearer {tokens.access_token}"}
        user = await self._get("/users/@me", headers)
        subject = _text(user.get("id"))
        # A subject that is not a canonical decimal snowflake is a payload this
        # adapter cannot use as an identity, and an identity is the one thing it
        # must never guess at (ADR 0010 D3).
        if not subject.isdigit():
            raise ProviderRefused("identity response carried no usable subject")

        guild_id = self._settings.guild_id
        membership = await self._member(guild_id, headers)
        return VerifiedIdentity(
            provider_key=self.provider_key,
            subject=subject,
            username=_text(user.get("username")),
            global_name=_text(user.get("global_name")) or None,
            membership=membership,
        )

    async def _member(self, guild_id: int, headers: dict[str, str]) -> ProviderMembership:
        url = f"{self._settings.api_base_url}/users/@me/guilds/{guild_id}/member"
        try:
            response = await self._client.get(url, headers=headers)
        except httpx.HTTPError as error:
            raise ProviderUnavailable("membership read transport failure") from error

        observed_at = datetime.now(timezone.utc)
        if response.status_code == 404:
            # A definite answer, not an outage: the person authorized the
            # application and is not in the guild. ADR 0004 requires the callback
            # to reject before a session is created, and this is the fact it
            # rejects on.
            return ProviderMembership(
                guild_id=guild_id,
                is_member=False,
                role_ids=frozenset(),
                observed_at=observed_at,
            )
        if response.status_code >= 500 or response.status_code == 429:
            raise ProviderUnavailable(f"membership read status {response.status_code}")
        if response.status_code >= 400:
            raise ProviderRefused("membership read refused")

        body = _json_object(response, "membership read")
        return ProviderMembership(
            guild_id=guild_id,
            is_member=True,
            role_ids=_role_ids(body.get("roles")),
            observed_at=observed_at,
        )

    async def _get(self, path: str, headers: dict[str, str]) -> dict[str, Any]:
        try:
            response = await self._client.get(
                f"{self._settings.api_base_url}{path}", headers=headers
            )
        except httpx.HTTPError as error:
            raise ProviderUnavailable(f"{path} transport failure") from error
        if response.status_code >= 500 or response.status_code == 429:
            raise ProviderUnavailable(f"{path} status {response.status_code}")
        if response.status_code >= 400:
            raise ProviderRefused(f"{path} refused")
        return _json_object(response, path)


# ---------------------------------------------------------------------------
# Payload readers
# ---------------------------------------------------------------------------
#
# Four small functions rather than one permissive parser, because each states a
# different expectation and the message it raises is the only place the
# distinction survives — none of the provider's bytes travel any further.


def _json_object(response: httpx.Response, what: str) -> dict[str, Any]:
    """The body as a JSON object, or a refusal. Never the body itself."""
    try:
        body = response.json()
    except ValueError:
        # `json.JSONDecodeError` is a `ValueError`. The decoder's message quotes
        # the document, so the cause is dropped rather than chained into a log
        # line that would carry the provider's bytes with it.
        raise ProviderRefused(f"{what} returned a body that is not JSON") from None
    if not isinstance(body, dict):
        raise ProviderRefused(f"{what} returned JSON that is not an object")
    return body


def _text(value: Any) -> str:
    """A string field, or empty. A non-scalar is not coerced into `"[1, 2]"`."""
    if isinstance(value, str):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        # Discord sends snowflakes as strings; a numeric one is still a snowflake.
        return str(value)
    return ""


def _seconds(value: Any) -> int:
    """A lifetime in seconds, or zero. `"soon"` and `null` are both zero."""
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return 0
    return 0


def _role_ids(value: Any) -> frozenset[int]:
    """Stable role snowflakes only.

    A non-list, or an entry that is not a decimal snowflake, contributes nothing:
    a role id that cannot be read must not become a role id that was not granted,
    and it must not become an exception either — an unreadable roles array is a
    membership with fewer roles, which fails closed.
    """
    if not isinstance(value, list):
        return frozenset()
    return frozenset(
        int(role)
        for role in value
        if isinstance(role, (str, int))
        and not isinstance(role, bool)
        and str(role).isdigit()
    )


__all__ = ["DiscordIdentityProvider"]
