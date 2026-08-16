"""Authenticated encryption and keyed digests for the portal.

Three primitives, each with exactly one reason to exist:

1. **`Envelope`** — AES-256-GCM with versioned keys and *additional authenticated
   data*, for the two values the platform stores encrypted rather than hashed:
   the PKCE `code_verifier` (schema §9.2.1) and the provider's OAuth tokens
   (§9.5). Both must be *presented* to Discord later, so neither can be a hash.
2. **`keyed_digest`** — HMAC-SHA256 for values that are only ever *compared* or
   *bucketed*: client addresses, user-agent strings, rate-limit buckets. A plain
   SHA-256 over an IPv4 address is reversible by exhaustive search in seconds, so
   the key is what makes the digest a digest.
3. **`token_hash`** — plain SHA-256 over a value that already carries 256 bits of
   entropy: a session token, a recovery grant, an OAuth `state`. **This is
   correct rather than a shortcut.** There is no low-entropy guess for a slow
   hash to slow down, so Argon2 here would be cargo cult; what matters is that
   the stored form is one-way and the comparison is constant-time.

## Why AAD, and what it buys

GCM's additional authenticated data is authenticated but not encrypted, so it
binds a ciphertext to the row it was written for. A `pkce_verifier_ciphertext`
copied from one `oauth_transactions` row into another **fails to authenticate and
raises**, rather than decrypting into a verifier that would complete somebody
else's exchange. That is a different guarantee from "the attacker cannot read
it", and it is the one that matters when the attacker can already write rows.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from application.web.config import EncryptionKeyring, SecretKey

#: AES-GCM's standard nonce length. Twelve bytes is what the mode is specified
#: for; a different length is permitted by the API and is a footgun with it.
NONCE_BYTES = 12

#: Every opaque token the platform mints: session cookies, login-transaction
#: cookies, OAuth `state`, recovery grants. 256 bits, so a hash of it needs no
#: work factor.
TOKEN_BYTES = 32


class DecryptionError(Exception):
    """A ciphertext did not authenticate under the key and AAD it was offered.

    Deliberately does not distinguish "wrong key" from "wrong AAD" from
    "tampered": the caller's correct response is identical in all three cases,
    and the distinction is exactly what an oracle would leak.
    """


@dataclass(frozen=True, slots=True)
class Sealed:
    """One encrypted value, and the two facts needed to open it again."""

    ciphertext: bytes
    nonce: bytes
    key_version: int


class Envelope:
    """Versioned AES-256-GCM. Encrypts under the active key, decrypts under any.

    That asymmetry is the whole rotation story: add a key, switch the active
    version, re-encrypt in the background, remove the old key. At no point is
    there a stored value that cannot be read.
    """

    __slots__ = ("_keyring",)

    def __init__(self, keyring: EncryptionKeyring) -> None:
        self._keyring = keyring

    def seal(self, plaintext: bytes, *, aad: bytes) -> Sealed:
        key = self._keyring.active
        nonce = os.urandom(NONCE_BYTES)
        ciphertext = AESGCM(key.material).encrypt(nonce, plaintext, aad)
        return Sealed(ciphertext=ciphertext, nonce=nonce, key_version=key.version)

    def open(self, sealed: Sealed, *, aad: bytes) -> bytes:
        try:
            key = self._keyring.key_for(sealed.key_version)
        except KeyError as error:
            raise DecryptionError(
                "the key version this value was written under is not configured"
            ) from error
        try:
            return AESGCM(key.material).decrypt(sealed.nonce, sealed.ciphertext, aad)
        except InvalidTag as error:
            raise DecryptionError(
                "the ciphertext did not authenticate under the key and binding it "
                "was offered"
            ) from error


def transaction_aad(transaction_id, key_version: int, provider_key: str) -> bytes:
    """Binds a PKCE verifier to *this* transaction row (schema §9.2.1).

    Without it, a ciphertext moved between rows would decrypt into a verifier
    that completes a flow it was never issued for.
    """
    return f"oauth_transaction|{transaction_id}|{key_version}|{provider_key}".encode()


def token_grant_aad(grant_id, external_identity_id, key_version: int) -> bytes:
    """Binds stored provider tokens to the identity they belong to (schema §9.5)."""
    return f"oauth_token_grant|{grant_id}|{external_identity_id}|{key_version}".encode()


def mint_token() -> str:
    """A new opaque bearer token: 256 bits, URL-safe, never stored in this form."""
    return secrets.token_urlsafe(TOKEN_BYTES)


def token_hash(token: str) -> bytes:
    """The stored form of a high-entropy token. Plain SHA-256, deliberately."""
    return hashlib.sha256(token.encode("utf-8")).digest()


def keyed_digest(key: SecretKey, value: str) -> bytes:
    """A comparable, non-reversible stand-in for a low-entropy value.

    Used for client addresses (`sessions.client_ip_hash`), user-agent strings and
    rate-limit bucket names. The address space is small enough to enumerate, so
    an unkeyed hash would be the address with extra steps.
    """
    return hmac.new(key.material, value.encode("utf-8"), hashlib.sha256).digest()


def constant_time_equals(left: bytes, right: bytes) -> bool:
    """Comparison whose timing does not depend on where the values differ."""
    return hmac.compare_digest(left, right)


def pkce_pair() -> tuple[str, str]:
    """A PKCE `code_verifier` and its S256 `code_challenge` (RFC 7636).

    The verifier is returned in the clear because the caller has to encrypt it
    and hand it to the provider later; it is never returned from storage in this
    form more than once, because consumption erases it in the same statement that
    reads it.
    """
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = _b64url(digest)
    return verifier, challenge


def _b64url(raw: bytes) -> str:
    import base64

    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


__all__ = [
    "DecryptionError",
    "Envelope",
    "NONCE_BYTES",
    "Sealed",
    "TOKEN_BYTES",
    "constant_time_equals",
    "keyed_digest",
    "mint_token",
    "pkce_pair",
    "token_grant_aad",
    "token_hash",
    "transaction_aad",
]
