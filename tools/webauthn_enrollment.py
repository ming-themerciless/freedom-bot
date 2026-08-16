"""C-03: enroll or retire a break-glass WebAuthn credential, host-locally.

    python -m tools.webauthn_enrollment list    --operator "…"
    python -m tools.webauthn_enrollment enroll  --operator "…" --nickname "yubikey-1" \
        --credential-id <base64url> --public-key <base64url>
    python -m tools.webauthn_enrollment retire  --operator "…" --credential <uuid>

**Enrollment is host-local only.** There is no web enrollment route (route
contract §8, TC-BG-10), so a stolen break-glass session cannot enroll an
attacker's authenticator — which is the property that keeps a single compromised
emergency session from becoming permanent access.

## Why the ceremony is split

Registration ceremony (`navigator.credentials.create`) happens in a browser, and
a browser is exactly what this command deliberately does not require. The
operator performs the ceremony on the host — with the reference page in
`docs/operations/` — and passes the resulting credential id and COSE public key
here. What is stored is a public key and a counter: **no attestation object, no
private key, no PIN and no biometric material**, none of which ever leaves the
authenticator.

## The two-credential rule

N-13 requires the protected account to keep at least **two** enabled credentials,
and `retire` refuses to take it below that. It cannot be a database constraint
for the same reason OD-37's "at least one owner" cannot be: PostgreSQL cannot
require a row in another table without a deferred trigger, and the account must
exist before the first credential is enrolled. So it is an application invariant
here, a health check in VM-16, and a startup refusal in production (S-15) — three
places, because losing every key is unrecoverable through the application by
design.
"""
from __future__ import annotations

import argparse
from collections.abc import Sequence
from uuid import UUID, uuid4

from webauthn.helpers import base64url_to_bytes

from adapters.web.repositories import (
    AccountRepository,
    WebAuditRepository,
    WebAuthnRepository,
    utcnow,
)
from application.audit import ActorCapability, AuditEvent, AuditSource
from application.web.breakglass import MINIMUM_ENROLLED_CREDENTIALS
from tools.web_operator import (
    EXIT_OK,
    EXIT_REFUSED,
    EXIT_UNSAFE_TARGET,
    TargetRefused,
    require_operator,
    resolve_engine,
)


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    listing = sub.add_parser("list")
    listing.add_argument("--operator", required=True)

    enroll = sub.add_parser("enroll")
    enroll.add_argument("--operator", required=True)
    enroll.add_argument("--nickname", required=True)
    enroll.add_argument("--credential-id", required=True, help="base64url")
    enroll.add_argument("--public-key", required=True, help="base64url COSE key")
    enroll.add_argument("--sign-count", type=int, default=0)
    enroll.add_argument("--transports", default=None)

    retire = sub.add_parser("retire")
    retire.add_argument("--operator", required=True)
    retire.add_argument("--credential", required=True, help="credential record UUID")
    retire.add_argument("--reason", required=True)

    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_arguments(argv)
    try:
        operator = require_operator(arguments.operator)
        engine = resolve_engine()
    except TargetRefused as refusal:
        print(f"Refused: {refusal}")
        return EXIT_UNSAFE_TARGET

    with engine.begin() as connection:
        accounts = AccountRepository(connection)
        credentials = WebAuthnRepository(connection)
        audit = WebAuditRepository(connection)
        account = accounts.protected_administrator()

        if arguments.command == "enroll":
            if account is None:
                # First enrollment creates the protected account. This is the one
                # command that may do so, and it is host-local: the protected
                # account must exist before the portal is exposed (schema §8's
                # bootstrap-ordering hazard, RAID A-05).
                account = _create_protected_account(connection, operator)
                print(f"Created the protected administrator account {account.id}.")
            return _enroll(
                arguments, account, credentials, audit, operator=operator
            )

        if account is None:
            print("Refused: no protected administrator account exists yet.")
            return EXIT_REFUSED

        enabled = credentials.enabled_credentials(account.id)
        if arguments.command == "list":
            print(f"Protected administrator account: {account.id}")
            print(f"Enabled credentials: {len(enabled)} (minimum {MINIMUM_ENROLLED_CREDENTIALS})")
            for record in enabled:
                # The record id and the operator's own label. **Never** the
                # public key: it is not a secret, but it is a fingerprint of a
                # specific authenticator and printing it serves nothing.
                print(f"  {record.id}  {record.nickname or '(no nickname)'}")
            return EXIT_OK

        return _retire(arguments, credentials, audit, account, enabled, operator=operator)


def _create_protected_account(connection, operator: str):
    from uuid import uuid4 as _uuid4

    from sqlalchemy import insert

    from adapters.database.tables import platform_accounts

    account_id = _uuid4()
    connection.execute(
        insert(platform_accounts).values(
            id=account_id,
            status="active",
            is_protected_admin=True,
            display_label=f"Server Administrator (enrolled by {operator})"[:80],
        )
    )
    from adapters.web.repositories import AccountRecord

    return AccountRecord(
        id=account_id,
        status="active",
        is_protected_admin=True,
        display_label=None,
    )


def _enroll(arguments, account, credentials, audit, *, operator: str) -> int:
    try:
        credential_id = base64url_to_bytes(arguments.credential_id)
        public_key = base64url_to_bytes(arguments.public_key)
    except Exception:  # noqa: BLE001 - malformed input is one outcome
        print("Refused: --credential-id and --public-key must be base64url.")
        return EXIT_REFUSED
    if not credential_id or not public_key:
        print("Refused: an empty credential id or public key is not a credential.")
        return EXIT_REFUSED

    record_id = credentials.enroll(
        account_id=account.id,
        credential_id=credential_id,
        public_key=public_key,
        sign_count=max(0, arguments.sign_count),
        operator=operator,
        nickname=arguments.nickname,
        transports=arguments.transports,
        aaguid=None,
    )
    correlation_id = uuid4()
    audit.record(
        AuditEvent(
            action="auth.emergency.credential.enrolled",
            entity_type="webauthn_credential",
            entity_id=str(record_id),
            source=AuditSource.SYSTEM,
            actor_capability=ActorCapability.PLATFORM_ADMINISTRATOR,
            correlation_id=correlation_id,
            actor_platform_account_id=account.id,
            payload={"operator": operator, "nickname": arguments.nickname},
        )
    )
    total = len(credentials.enabled_credentials(account.id))
    print(f"Enrolled credential {record_id} ({arguments.nickname}).")
    print(f"Correlation id: {correlation_id}")
    print(f"Enabled credentials: {total} (minimum {MINIMUM_ENROLLED_CREDENTIALS})")
    if total < MINIMUM_ENROLLED_CREDENTIALS:
        print(
            "WARNING: the protected account is below the two-credential minimum "
            "(N-13). Enroll another before exposing the portal; production startup "
            "refuses otherwise (S-15)."
        )
    return EXIT_OK


def _retire(arguments, credentials, audit, account, enabled, *, operator: str) -> int:
    try:
        target = UUID(arguments.credential)
    except ValueError:
        print("Refused: --credential must be a credential record UUID.")
        return EXIT_REFUSED

    if not any(record.id == target for record in enabled):
        print("Refused: no enabled credential with that record id.")
        return EXIT_REFUSED

    if len(enabled) - 1 < MINIMUM_ENROLLED_CREDENTIALS:
        # N-13, enforced where the loss would happen. Retiring below two leaves
        # the administrator one hardware failure away from an account that can
        # only be recovered by database-owner action outside the application.
        print(
            f"Refused: retiring this credential would leave {len(enabled) - 1}, "
            f"below the minimum of {MINIMUM_ENROLLED_CREDENTIALS} (N-13). Enroll a "
            "replacement first."
        )
        return EXIT_REFUSED

    credentials.disable(target, at=utcnow())
    correlation_id = uuid4()
    audit.record(
        AuditEvent(
            action="auth.emergency.credential.retired",
            entity_type="webauthn_credential",
            entity_id=str(target),
            source=AuditSource.SYSTEM,
            actor_capability=ActorCapability.PLATFORM_ADMINISTRATOR,
            correlation_id=correlation_id,
            actor_platform_account_id=account.id,
            payload={"operator": operator, "reason": arguments.reason},
        )
    )
    print(f"Retired credential {target}. Correlation id: {correlation_id}")
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover - entry point
    raise SystemExit(main())
