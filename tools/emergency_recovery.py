"""C-01 and C-02: issue and revoke a break-glass recovery grant (N-14, N-61).

    python -m tools.emergency_recovery issue  --operator "Peter Duscha" --reason "…"
    python -m tools.emergency_recovery revoke --operator "Peter Duscha" --reason "…"

**There is no HTTP route that does this**, and that absence is the control (ADR
0010 D8, route contract §8). Issuing a grant requires existing host authority, so
the last-resort path cannot be reached from the internet even by someone holding
a stolen break-glass session.

## What is printed, and what is stored

The token is printed **once**, to the operator's terminal, and stored **only** as
a SHA-256 hash. It appears in no row, no log line and no audit payload; the audit
record names the grant's **record id** instead. If the terminal output is lost,
the grant is lost — issue another, which invalidates the first in the same
transaction (N-61).

A plain SHA-256 is correct here rather than a shortcut: the token is 256 bits of
entropy, so there is no low-entropy guess for a slow hash to slow down.

## The window this opens, stated plainly

A recovery grant is a bearer token for ten minutes. If the operator's terminal or
clipboard is compromised in that window, the grant is usable. The compensating
controls are the ten-minute expiry, single use, the one-live-grant rule, and an
audit record the operator can compare against their own action. That residual is
recorded in ADR 0010 rather than argued away.
"""
from __future__ import annotations

import argparse
from collections.abc import Sequence
from datetime import timedelta
from uuid import uuid4

from adapters.web.repositories import (
    AccountRepository,
    RecoveryGrantRepository,
    WebAuditRepository,
    utcnow,
)
from application.audit import ActorCapability, AuditEvent, AuditSource
from application.web.crypto import mint_token, token_hash
from tools.web_operator import (
    EXIT_CANNOT_CONNECT,
    EXIT_OK,
    EXIT_REFUSED,
    EXIT_UNSAFE_TARGET,
    TargetRefused,
    require_operator,
    resolve_engine,
)

#: N-14's ceiling. The command cannot be asked for a longer one.
GRANT_MINUTES = 10


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("issue", "revoke"):
        command = sub.add_parser(name)
        command.add_argument(
            "--operator", required=True, help="The named human running this."
        )
        command.add_argument("--reason", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_arguments(argv)
    try:
        operator = require_operator(arguments.operator)
        engine = resolve_engine()
    except TargetRefused as refusal:
        print(f"Refused: {refusal}")
        return EXIT_UNSAFE_TARGET

    try:
        with engine.begin() as connection:
            accounts = AccountRepository(connection)
            account = accounts.protected_administrator()
            if account is None:
                # The bootstrap-ordering hazard, named where an operator meets
                # it: migration 0006 inserts the protected *mapping*, but the
                # protected *account* is created by the first administrator
                # authentication or by C-03 enrollment.
                print(
                    "Refused: no protected administrator account exists yet. Create "
                    "it by enrolling a break-glass credential "
                    "(`python -m tools.webauthn_enrollment enroll`) before issuing a "
                    "recovery grant."
                )
                return EXIT_REFUSED

            grants = RecoveryGrantRepository(connection)
            audit = WebAuditRepository(connection)
            correlation_id = uuid4()
            now = utcnow()

            if arguments.command == "revoke":
                count = grants.invalidate_all(
                    account_id=account.id, reason="operator_revoked"
                )
                audit.record(
                    AuditEvent(
                        action="auth.emergency.recovery.revoked",
                        entity_type="platform_account",
                        entity_id=str(account.id),
                        source=AuditSource.SYSTEM,
                        actor_capability=ActorCapability.PLATFORM_ADMINISTRATOR,
                        correlation_id=correlation_id,
                        actor_platform_account_id=account.id,
                        payload={
                            "operator": operator,
                            "reason": arguments.reason,
                            "invalidated": count,
                        },
                    )
                )
                print(f"Invalidated {count} outstanding recovery grant(s).")
                print(f"Correlation id: {correlation_id}")
                return EXIT_OK

            token = mint_token()
            expires_at = now + timedelta(minutes=GRANT_MINUTES)
            grant_id = grants.issue(
                account_id=account.id,
                token_hash=token_hash(token),
                expires_at=expires_at,
                operator=operator,
                correlation_id=correlation_id,
            )
            audit.record(
                AuditEvent(
                    action="auth.emergency.recovery.issued",
                    entity_type="recovery_grant",
                    # The record id. **Never the token** — it is not stored, and
                    # it appears in no audit payload.
                    entity_id=str(grant_id),
                    source=AuditSource.SYSTEM,
                    actor_capability=ActorCapability.PLATFORM_ADMINISTRATOR,
                    correlation_id=correlation_id,
                    actor_platform_account_id=account.id,
                    payload={
                        "operator": operator,
                        "reason": arguments.reason,
                        "expires_at": expires_at.isoformat(),
                        "purpose": "emergency_login",
                    },
                )
            )
    except TargetRefused as refusal:
        print(f"Refused: {refusal}")
        return EXIT_CANNOT_CONNECT

    print("Recovery grant issued. The token is shown once and stored only as a hash.")
    print()
    print(f"    {token}")
    print()
    print(f"Grant record id: {grant_id}")
    print(f"Correlation id:  {correlation_id}")
    print(f"Expires:         {expires_at.isoformat()} ({GRANT_MINUTES} minutes)")
    print(
        "Single use, purpose-bound to emergency login. Issuing another invalidates "
        "this one."
    )
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover - entry point
    raise SystemExit(main())
