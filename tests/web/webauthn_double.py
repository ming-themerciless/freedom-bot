"""A software authenticator, so the break-glass path can be tested end to end.

Mocking `verify_authentication_response` would test that the mock was called.
This signs a real ES256 assertion over real authenticator data, so the platform's
verification — RP ID hash, origin, user-verification flag, signature, counter —
is exercised as written, and a mistake in any of them fails a test.

It is a **test double of a security key**, not of the library: `py_webauthn` does
the verifying, exactly as it will in production.
"""
from __future__ import annotations

import hashlib
import json
import struct
from dataclasses import dataclass

import cbor2
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from webauthn.helpers import bytes_to_base64url

#: WebAuthn authenticator-data flags. `UP` is user presence and `UV` is user
#: verification; N-60 requires the second, so an authenticator that set only the
#: first must be refused — which `sign` can be asked to do.
FLAG_USER_PRESENT = 0x01
FLAG_USER_VERIFIED = 0x04


@dataclass
class SoftwareAuthenticator:
    """One credential: a P-256 key pair, a credential id and a counter."""

    rp_id: str
    origin: str
    credential_id: bytes = b"synthetic-credential-id-0001"
    sign_count: int = 0
    _key: ec.EllipticCurvePrivateKey | None = None

    def __post_init__(self) -> None:
        if self._key is None:
            self._key = ec.generate_private_key(ec.SECP256R1())

    @property
    def cose_public_key(self) -> bytes:
        """The COSE_Key an authenticator would have returned at registration.

        `kty=2` (EC2), `alg=-7` (ES256), `crv=1` (P-256), with the raw affine
        coordinates. This is what `webauthn_credentials.public_key` holds — a
        public key, which is not a secret, but is a fingerprint of a specific
        authenticator and is therefore still restricted.
        """
        numbers = self._key.public_key().public_numbers()
        return cbor2.dumps(
            {
                1: 2,
                3: -7,
                -1: 1,
                -2: numbers.x.to_bytes(32, "big"),
                -3: numbers.y.to_bytes(32, "big"),
            }
        )

    def sign(
        self,
        challenge: bytes,
        *,
        user_verified: bool = True,
        sign_count: int | None = None,
        origin: str | None = None,
    ) -> dict:
        """Produce the credential payload a browser would `fetch` to R-08.

        `user_verified=False` and a non-advancing `sign_count` are supported so
        the tests can present the two authenticators the platform must refuse: a
        key used without user verification, and a cloned one.
        """
        self.sign_count = self.sign_count + 1 if sign_count is None else sign_count

        client_data = json.dumps(
            {
                "type": "webauthn.get",
                "challenge": bytes_to_base64url(challenge),
                "origin": origin or self.origin,
                "crossOrigin": False,
            },
            separators=(",", ":"),
        ).encode("utf-8")

        flags = FLAG_USER_PRESENT | (FLAG_USER_VERIFIED if user_verified else 0)
        authenticator_data = (
            hashlib.sha256(self.rp_id.encode("utf-8")).digest()
            + struct.pack("!B", flags)
            + struct.pack("!I", self.sign_count)
        )
        signature = self._key.sign(
            authenticator_data + hashlib.sha256(client_data).digest(),
            ec.ECDSA(hashes.SHA256()),
        )
        return {
            "id": bytes_to_base64url(self.credential_id),
            "rawId": bytes_to_base64url(self.credential_id),
            "type": "public-key",
            "response": {
                "clientDataJSON": bytes_to_base64url(client_data),
                "authenticatorData": bytes_to_base64url(authenticator_data),
                "signature": bytes_to_base64url(signature),
                "userHandle": None,
            },
            "clientExtensionResults": {},
        }


__all__ = ["FLAG_USER_PRESENT", "FLAG_USER_VERIFIED", "SoftwareAuthenticator"]
