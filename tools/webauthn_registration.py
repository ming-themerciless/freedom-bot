"""C-03 companion: turn a browser registration ceremony into an enrolled credential.

    python -m tools.webauthn_registration --operator "…" --nickname "iphone" \
        --response <the block the registration page produced>

## Why this exists

`tools.webauthn_enrollment` takes a credential id and a **COSE** public key, and a
browser will not hand either of those over directly: what it returns is a CBOR
attestation object, and the key has to be verified and extracted from it. Before
2026-08-23 the enrollment tool's own docstring pointed operators at "the reference
page in `docs/operations/`", and no such page existed — so there was no supported
way to produce its two arguments at all (P3.5 finding F-7).

This closes that gap without widening any boundary. Enrollment stays host-local:
there is still no HTTP route that enrols a credential (route contract §8,
TC-BG-10), so a stolen break-glass session still cannot register an attacker's
authenticator. The page runs in the operator's browser and transmits nothing; the
operator carries the result to this command, which requires host authority.

## What it verifies before enrolling

The full registration response, through `webauthn.verify_registration_response`:
signature, attestation format, the client data's type and origin, the relying
party hash, and that user verification actually happened. A response that fails
any of those is refused here rather than becoming a credential that cannot log in.

**The challenge is the page's own**, carried alongside the response, and that is a
deliberate limitation stated rather than hidden. A server-issued challenge would
prove freshness, but issuing one needs a route, and the route is what must not
exist. What the check therefore proves is that the response is internally
consistent and genuinely from an authenticator — not that it was made in the last
minute. The compensating controls are that the operator performs the ceremony
themselves and must hold host authority to spend its result, and that replaying an
old response only re-registers the same public key.

## The relying party is checked, not assumed

The commonest way to waste an enrolment is to run the ceremony at the wrong
address: a credential is bound to the relying-party identifier of the page that
created it, so one made at a test address silently cannot authenticate against
production (F-8). This command therefore **requires** the running configuration's
`WEB_WEBAUTHN_RP_ID` to equal the one the page recorded, and refuses otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
from base64 import urlsafe_b64decode
from collections.abc import Sequence

import webauthn
from webauthn.helpers import bytes_to_base64url
from webauthn.helpers.exceptions import InvalidRegistrationResponse

from application.web.config import ConfigurationError, ProcessRole, WebSettings
from tools.web_operator import EXIT_OK, EXIT_REFUSED, EXIT_USAGE


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--operator", required=True, help="The named human running this.")
    parser.add_argument("--nickname", required=True, help="How this authenticator is labelled.")
    parser.add_argument(
        "--response",
        required=True,
        help="The block produced by the registration page.",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Print the credential id and public key instead of enrolling them.",
    )
    return parser.parse_args(argv)


def _decode_block(block: str) -> dict:
    padded = block.strip() + "=" * (-len(block.strip()) % 4)
    return json.loads(urlsafe_b64decode(padded.encode("ascii")).decode("utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_arguments(argv)

    try:
        payload = _decode_block(arguments.response)
    except Exception:  # noqa: BLE001 - malformed input is one outcome
        print("Refused: --response is not the block the registration page produced.")
        return EXIT_USAGE

    for field in ("rpId", "origin", "challenge", "credential"):
        if field not in payload:
            print(f"Refused: the response block is missing '{field}'.")
            return EXIT_USAGE

    try:
        settings = WebSettings.from_environment(os.environ, process=ProcessRole.WEB)
    except ConfigurationError as error:
        print(f"Refused: this host's configuration is not usable.\n{error}")
        return EXIT_REFUSED

    expected_rp_id = settings.webauthn.rp_id
    if payload["rpId"] != expected_rp_id:
        print(
            "Refused: the ceremony was performed at the wrong address.\n"
            f"  the page registered for : {payload['rpId']}\n"
            f"  this portal answers for : {expected_rp_id}\n"
            "A passkey is bound to the address that created it, so this one could "
            "never authenticate here. Reopen the registration page at the correct "
            "address and try again."
        )
        return EXIT_REFUSED

    try:
        verified = webauthn.verify_registration_response(
            credential=payload["credential"],
            expected_challenge=urlsafe_b64decode(
                payload["challenge"] + "=" * (-len(payload["challenge"]) % 4)
            ),
            expected_rp_id=expected_rp_id,
            expected_origin=list(settings.webauthn.allowed_origins),
            require_user_verification=True,
        )
    except InvalidRegistrationResponse as error:
        print(f"Refused: the registration response did not verify.\n  {error}")
        return EXIT_REFUSED

    credential_id = bytes_to_base64url(verified.credential_id)
    public_key = bytes_to_base64url(verified.credential_public_key)
    transports = payload["credential"].get("response", {}).get("transports") or []

    if arguments.print_only:
        print(f"credential-id : {credential_id}")
        print(f"public-key    : {public_key}")
        print(f"transports    : {','.join(transports) or '(none reported)'}")
        return EXIT_OK

    # Reuse the enrollment path rather than reimplementing it: the protected
    # account's creation, the two-credential rule and the audit record all live
    # there, and a second writer of credentials would be a second answer to what
    # "enrolled" means.
    from tools.webauthn_enrollment import main as enroll

    arguments_for_enrollment = [
        "enroll",
        "--operator", arguments.operator,
        "--nickname", arguments.nickname,
        "--credential-id", credential_id,
        "--public-key", public_key,
    ]
    if transports:
        arguments_for_enrollment += ["--transports", ",".join(transports)]
    return enroll(arguments_for_enrollment)


if __name__ == "__main__":  # pragma: no cover - operator entry point
    raise SystemExit(main())
