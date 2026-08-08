"""Resolving a presented bearer credential into a scoped service principal.

The whole of this module's job is to answer one question — *which principal, if
any, is this?* — without ever answering a related one an attacker would prefer:
*how close was I?*

**The secret is never stored.** Configuration holds a SHA-256 of it. Compromise
of the configuration file does not yield a usable credential, and rotating one
is editing a hex string rather than handling the secret itself again.

**A plain SHA-256 is the right construction here, and a slow KDF is not.** A
password KDF exists because humans choose low-entropy secrets and an offline
attacker can enumerate them. This secret is required to be at least
`MIN_SECRET_LENGTH` characters of operator-generated randomness, which no
enumeration reaches; and this comparison happens on every submission, where a
deliberately slow hash would be a denial-of-service lever pointed at the server.
The requirement is enforced at *presentation* as well as at configuration time,
so a short secret cannot authenticate even if one is somehow configured.

**Comparison is constant-time.** `hmac.compare_digest` on the digests, so the
time taken reveals nothing about how many leading characters matched.

**The principal id travels in the credential.** `Bearer <id>.<secret>` — so a
presented credential names the record to compare against instead of being
compared against every configured record in turn. That is what keeps the work
per request constant, and it is why an *unknown* id still performs a comparison
against a fixed dummy digest before failing: skipping the work would make an
unknown id measurably faster than a wrong secret.

**No refusal says why.** Unknown id, wrong secret, malformed header and
too-short secret all raise the same error with the same message. The caller is a
machine holding one configured credential; it has nothing to do with a more
specific diagnosis, and an attacker would.
"""
from __future__ import annotations

import hashlib
import hmac
import re
from collections.abc import Mapping
from dataclasses import dataclass

from application.service_principals import ServicePrincipal, ServicePrincipalScope

#: The environment variable holding the configured principals.
PRINCIPALS_VARIABLE = "FREEDOM_SNAPSHOT_PRINCIPALS"

#: One entry per principal, `;`-separated:
#:
#:     <id>|<scope>[,<scope>…]|<sha256 of the secret, hex>
#:
#: The scope list is explicit rather than implied by the variable's name. A
#: credential's authority should be readable from the line that grants it.
_ENTRY_SEPARATOR = ";"
_FIELD_SEPARATOR = "|"
_SCOPE_SEPARATOR = ","

#: Below this, a secret is short enough that offline enumeration of an
#: SHA-256 becomes a real concern. 32 characters of `secrets.token_urlsafe(32)`
#: output is ~192 bits; this bound is the floor, not the recommendation.
MIN_SECRET_LENGTH = 32

_SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")

#: Compared against when no principal matches, so an unknown id costs the same
#: as a wrong secret. Its preimage is not known to anyone, including this code.
_DUMMY_DIGEST = hashlib.sha256(b"freedom-blades/no-such-principal").hexdigest()


class CredentialError(ValueError):
    """The configured credential set is unusable. Raised at startup, not per request."""


class AuthenticationFailed(Exception):
    """The presented credential is not a currently configured principal.

    One error for every cause, by design. See the module docstring.
    """

    def __init__(self) -> None:
        super().__init__(
            "The presented credential is not recognised. Check the configured "
            "endpoint credential, or ask an operator whether it was rotated."
        )


@dataclass(frozen=True, slots=True)
class _Entry:
    principal: ServicePrincipal
    secret_digest: str


class ServicePrincipalRegistry:
    """Every credential this deployment currently accepts.

    Immutable once built. Rotation and revocation are a configuration change
    followed by a reload, which is what makes "revoked" a fact about the running
    process rather than a row somebody might forget to check.
    """

    __slots__ = ("_entries",)

    def __init__(self, entries: Mapping[str, _Entry]) -> None:
        self._entries = dict(entries)

    def __len__(self) -> int:
        return len(self._entries)

    @property
    def principal_ids(self) -> tuple[str, ...]:
        """The configured ids, for an operator-facing startup summary."""
        return tuple(sorted(self._entries))

    @classmethod
    def from_mapping(cls, environ: Mapping[str, str]) -> ServicePrincipalRegistry:
        """Build the registry from configuration, or refuse to start.

        An empty or absent variable produces an **empty registry**, not an
        error. A deployment that has not enabled snapshot submission is a valid
        deployment; every request to it then fails authentication, which is the
        correct behaviour and is also what makes "revoke everything" a one-line
        change.
        """
        raw = (environ.get(PRINCIPALS_VARIABLE) or "").strip()
        if not raw:
            return cls({})

        entries: dict[str, _Entry] = {}
        for index, chunk in enumerate(raw.split(_ENTRY_SEPARATOR), start=1):
            text = chunk.strip()
            if not text:
                continue
            entry = _parse_entry(text, index)
            if entry.principal.principal_id in entries:
                raise CredentialError(
                    f"{PRINCIPALS_VARIABLE} configures "
                    f"{entry.principal.principal_id!r} more than once. Two "
                    "records for one id make it ambiguous which secret and "
                    "which scopes are in force."
                )
            entries[entry.principal.principal_id] = entry
        return cls(entries)

    def authenticate(self, presented: str) -> ServicePrincipal:
        """Resolve a presented `<id>.<secret>` credential, or refuse it."""
        identifier, _, secret = presented.partition(".")
        entry = self._entries.get(identifier)
        expected = entry.secret_digest if entry is not None else _DUMMY_DIGEST
        digest = hashlib.sha256(secret.encode("utf-8")).hexdigest()
        # Both branches do the same work in the same order. `compare_digest` is
        # called even when there is nothing to compare against.
        matched = hmac.compare_digest(digest, expected)
        if entry is None or not matched or len(secret) < MIN_SECRET_LENGTH:
            raise AuthenticationFailed()
        return entry.principal


def parse_bearer(header: str | None) -> str:
    """Extract the credential from an `Authorization` header, or refuse.

    Refuses with the same undifferentiated error as a wrong secret: whether a
    header was malformed or merely wrong is not information a caller needs.
    """
    if not header:
        raise AuthenticationFailed()
    scheme, _, value = header.partition(" ")
    if scheme.lower() != "bearer" or not value.strip():
        raise AuthenticationFailed()
    return value.strip()


def secret_digest(secret: str) -> str:
    """The value an operator puts in configuration for `secret`.

    Exposed so the documented rotation procedure can be a single command that
    does not require the operator to reimplement the construction.
    """
    if len(secret) < MIN_SECRET_LENGTH:
        raise CredentialError(
            f"A submission secret must be at least {MIN_SECRET_LENGTH} "
            "characters of generated randomness. Generate one with "
            "`python -c 'import secrets; print(secrets.token_urlsafe(32))'`."
        )
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def _parse_entry(text: str, index: int) -> _Entry:
    parts = text.split(_FIELD_SEPARATOR)
    if len(parts) != 3:
        raise CredentialError(
            f"{PRINCIPALS_VARIABLE} entry {index} is not "
            "'<id>|<scope>[,<scope>]|<sha256 hex>'."
        )
    identifier, scope_text, digest = (part.strip() for part in parts)

    if not _SHA256_HEX.fullmatch(digest):
        raise CredentialError(
            f"{PRINCIPALS_VARIABLE} entry {index} does not end in a SHA-256 hex "
            "digest. Configuration holds the digest of the secret, never the "
            "secret."
        )

    scopes: set[ServicePrincipalScope] = set()
    for name in scope_text.split(_SCOPE_SEPARATOR):
        candidate = name.strip()
        try:
            scopes.add(ServicePrincipalScope(candidate))
        except ValueError:
            known = ", ".join(sorted(scope.value for scope in ServicePrincipalScope))
            raise CredentialError(
                f"{PRINCIPALS_VARIABLE} entry {index} names scope "
                f"{candidate!r}, which does not exist. Known scopes: {known}."
            ) from None

    try:
        principal = ServicePrincipal(
            principal_id=identifier, scopes=frozenset(scopes)
        )
    except ValueError as error:
        raise CredentialError(
            f"{PRINCIPALS_VARIABLE} entry {index} is invalid: {error}"
        ) from None
    return _Entry(principal=principal, secret_digest=digest)
