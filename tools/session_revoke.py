"""C-07: revoke every session for an account after a suspected compromise.

    python -m tools.session_revoke --account <uuid> --operator "…" --reason "…"
    python -m tools.session_revoke --protected-admin --operator "…" --reason "…"

Revocation is server-side and immediate: sessions are database rows, and
resolution filters on `revoked_at` on **every** request, so there is no cache of
"this session was valid" for a revoked one to slip through. The stored provider
tokens go with them (N-11) — leaving them would keep a credential alive for a
session that no longer exists.

`--protected-admin` exists because the account whose sessions most urgently need
revoking during an incident is the one whose UUID nobody has to hand.
"""
from __future__ import annotations

import argparse
from collections.abc import Sequence
from uuid import UUID, uuid4

from adapters.web.repositories import (
    AccountRepository,
    SessionRepository,
    TokenGrantRepository,
    WebAuditRepository,
    utcnow,
)
from application.web.sessions import SessionService
from application.web.config import SessionSettings
from tools.web_operator import (
    EXIT_OK,
    EXIT_REFUSED,
    EXIT_UNSAFE_TARGET,
    EXIT_USAGE,
    TargetRefused,
    require_operator,
    resolve_engine,
)

#: This command revokes; it never creates or refreshes a session, so the lifetime
#: bounds are irrelevant to it. Stated rather than left to a reader to wonder
#: about. `SessionRepository` requires settings at construction (2026-08-15)
#: because the idle window is a property of what it was built with and never of a
#: call, so every construction site supplies them — including one that will never
#: perform a refresh.
#:
#: These are the accepted register values, not placeholders that happen to look
#: like them: since the idle-policy-construction remediation `SessionSettings`
#: validates itself, so this literal cannot name a window outside N-06, N-07,
#: N-15, N-66 or N-04 even by accident. An operator tool was one of the two
#: documented ways a bypassing instance could previously have been built.
_UNUSED_BOUNDS = SessionSettings(
    cookie_name="__Host-fb_session",
    cookie_secure=True,
    idle_minutes=60,
    absolute_hours=12,
    emergency_idle_minutes=15,
    emergency_absolute_minutes=60,
    max_sessions_per_account=10,
    login_transaction_cookie_name="__Host-fb_login_txn",
    oauth_transaction_minutes=10,
)


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--account", help="Platform account UUID.")
    target.add_argument("--protected-admin", action="store_true")
    parser.add_argument("--operator", required=True)
    parser.add_argument("--reason", required=True)
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
        if arguments.protected_admin:
            account = accounts.protected_administrator()
            if account is None:
                print("Refused: no protected administrator account exists.")
                return EXIT_REFUSED
            account_id = account.id
        else:
            try:
                account_id = UUID(arguments.account)
            except ValueError:
                print("Refused: --account must be a UUID.")
                return EXIT_USAGE
            if accounts.get(account_id) is None:
                print("Refused: no such platform account.")
                return EXIT_REFUSED

        # The service takes its bounds from the repository, so this tool has one
        # bounds source too — the same shape as the composition root, and for the
        # same reason (2026-08-15, finding F3).
        service = SessionService(
            sessions=SessionRepository(connection, settings=_UNUSED_BOUNDS),
            token_grants=TokenGrantRepository(connection),
            audit=WebAuditRepository(connection),
        )
        correlation_id = uuid4()
        revoked = service.revoke_every_session(
            account_id=account_id,
            now=utcnow(),
            correlation_id=correlation_id,
            operator=f"{operator}: {arguments.reason}",
        )

    print(f"Revoked {revoked} session(s) for account {account_id}.")
    print("Stored provider tokens for that account were deleted with them (N-11).")
    print(f"Correlation id: {correlation_id}")
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover - entry point
    raise SystemExit(main())
