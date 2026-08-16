"""C-01, C-02, C-03, C-06 and C-07: the host-local commands, and their refusals.

These four exist **because** they are not routes. ADR 0010 D8's boundary is that
issuing a grant and enrolling a credential require existing host authority, so a
stolen break-glass session cannot do either and neither can anyone on the
internet. `tests/web/test_security_controls.py` asserts the routes are absent;
this file asserts the commands work and refuse correctly.
"""
from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from sqlalchemy import select, text
from webauthn.helpers import bytes_to_base64url

from adapters.database.tables import audit_events, recovery_grants, sessions
from application.web.crypto import token_hash
from tests.web.conftest import enroll_credential, make_account, utcnow
from tests.web.webauthn_double import SoftwareAuthenticator
from tests.web_fixtures import PUBLIC_ORIGIN

pytestmark = pytest.mark.database

RP_ID = "portal.test"


@pytest.fixture()
def operator_environment(monkeypatch, database_url):
    """Point the commands at the disposable database, through the usual validator."""
    monkeypatch.setenv("WEB_DATABASE_URL", database_url)
    monkeypatch.setenv("WEB_ENVIRONMENT", "test")


# ---------------------------------------------------------------------------
# C-01 / C-02
# ---------------------------------------------------------------------------


def test_issuing_a_grant_prints_the_token_once_and_stores_only_its_hash(
    migrated_database, operator_environment, capsys
):
    """TC-BG-06. The token is in the terminal and in no row, log line or payload."""
    from tools import emergency_recovery

    with migrated_database.begin() as connection:
        account_id = make_account(connection, protected=True)

    exit_code = emergency_recovery.main(
        ["issue", "--operator", "Peter Duscha", "--reason", "Discord outage drill"]
    )
    printed = capsys.readouterr().out
    assert exit_code == 0

    token = next(
        line.strip()
        for line in printed.splitlines()
        if line.startswith("    ") and line.strip() and "Correlation" not in line
    )

    with migrated_database.connect() as connection:
        grant = connection.execute(select(recovery_grants)).mappings().one()
        event = connection.execute(
            select(audit_events).where(
                audit_events.c.action == "auth.emergency.recovery.issued"
            )
        ).mappings().one()

    assert bytes(grant["token_hash"]) == token_hash(token)
    assert grant["platform_account_id"] == account_id
    assert grant["created_by_operator"] == "Peter Duscha"
    assert grant["purpose"] == "emergency_login"
    # The token appears nowhere but the operator's terminal.
    assert token not in str(dict(grant))
    assert token not in str(dict(event))
    assert event["entity_id"] == str(grant["id"])
    assert event["actor_platform_account_id"] == account_id


def test_revoking_invalidates_every_outstanding_grant(
    migrated_database, operator_environment, capsys
):
    """C-02, and the incident response ADR 0010 names for a suspected compromise."""
    from tools import emergency_recovery

    with migrated_database.begin() as connection:
        make_account(connection, protected=True)

    emergency_recovery.main(["issue", "--operator", "Peter", "--reason", "drill"])
    capsys.readouterr()

    assert (
        emergency_recovery.main(
            ["revoke", "--operator", "Peter", "--reason", "terminal was shared"]
        )
        == 0
    )

    with migrated_database.connect() as connection:
        grant = connection.execute(select(recovery_grants)).mappings().one()
    assert grant["invalidated_reason"] == "operator_revoked"
    assert grant["consumed_at"] is None


def test_issuing_refuses_when_no_protected_account_exists_yet(
    migrated_database, operator_environment, capsys
):
    """The bootstrap-ordering hazard, named where an operator meets it (RAID A-05).

    Migration 0006 inserts the protected *mapping*; the protected *account* is
    created by the first enrollment. Refusing here with an instruction is better
    than issuing a grant for an account that cannot be authenticated.
    """
    from tools import emergency_recovery

    assert emergency_recovery.main(["issue", "--operator", "P", "--reason", "r"]) == 1
    assert "webauthn_enrollment" in capsys.readouterr().out


def test_an_unnamed_operator_is_refused(migrated_database, operator_environment, capsys):
    """Every emergency action names a human. There is no default."""
    from tools import emergency_recovery

    assert emergency_recovery.main(["issue", "--operator", "  ", "--reason", "r"]) == 2
    assert "--operator is required" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# C-03
# ---------------------------------------------------------------------------


def test_the_first_enrollment_creates_the_protected_account(
    migrated_database, operator_environment, capsys
):
    """C-03. Host-local, and the only path that may create the protected account."""
    from tools import webauthn_enrollment

    authenticator = SoftwareAuthenticator(rp_id=RP_ID, origin=PUBLIC_ORIGIN)
    exit_code = webauthn_enrollment.main(
        [
            "enroll",
            "--operator",
            "Peter Duscha",
            "--nickname",
            "yubikey-1",
            "--credential-id",
            bytes_to_base64url(authenticator.credential_id),
            "--public-key",
            bytes_to_base64url(authenticator.cose_public_key),
        ]
    )
    printed = capsys.readouterr().out
    assert exit_code == 0
    assert "Created the protected administrator account" in printed
    # One credential is below the minimum, and the command says so rather than
    # letting an operator discover it at the production startup refusal.
    assert "below the two-credential minimum" in printed

    with migrated_database.connect() as connection:
        account = connection.execute(
            text("SELECT id FROM platform_accounts WHERE is_protected_admin")
        ).scalar_one()
        credential = connection.execute(
            text("SELECT nickname, created_by_operator FROM webauthn_credentials")
        ).mappings().one()
        event = connection.execute(
            select(audit_events).where(
                audit_events.c.action == "auth.emergency.credential.enrolled"
            )
        ).mappings().one()
    assert credential["nickname"] == "yubikey-1"
    assert credential["created_by_operator"] == "Peter Duscha"
    assert event["actor_platform_account_id"] == account


def test_retiring_below_two_credentials_is_refused(
    migrated_database, operator_environment, capsys
):
    """TC-BG-14. N-13, enforced where the loss would actually happen.

    Retiring below two leaves the administrator one hardware failure away from an
    account recoverable only by database-owner action outside the application.
    """
    from tools import webauthn_enrollment

    authenticator = SoftwareAuthenticator(rp_id=RP_ID, origin=PUBLIC_ORIGIN)
    with migrated_database.begin() as connection:
        account_id = make_account(connection, protected=True)
        first = enroll_credential(
            connection,
            account_id,
            credential_id=authenticator.credential_id,
            public_key=authenticator.cose_public_key,
            nickname="primary",
        )
        enroll_credential(
            connection,
            account_id,
            credential_id=b"second-credential-000000002",
            public_key=authenticator.cose_public_key,
            nickname="backup",
        )

    # Two enrolled: retiring one leaves one, which is below the minimum.
    assert (
        webauthn_enrollment.main(
            [
                "retire",
                "--operator",
                "Peter",
                "--credential",
                str(first),
                "--reason",
                "lost",
            ]
        )
        == 1
    )
    assert "below the minimum" in capsys.readouterr().out

    with migrated_database.connect() as connection:
        enabled = connection.execute(
            text("SELECT count(*) FROM webauthn_credentials WHERE disabled_at IS NULL")
        ).scalar_one()
    assert enabled == 2


def test_listing_never_prints_a_public_key(
    migrated_database, operator_environment, capsys
):
    """A public key is not a secret; it is a fingerprint of a specific authenticator.

    Printing it serves nothing an operator needs, so the listing names record ids
    and the operator's own labels.
    """
    from tools import webauthn_enrollment

    authenticator = SoftwareAuthenticator(rp_id=RP_ID, origin=PUBLIC_ORIGIN)
    with migrated_database.begin() as connection:
        account_id = make_account(connection, protected=True)
        enroll_credential(
            connection,
            account_id,
            credential_id=authenticator.credential_id,
            public_key=authenticator.cose_public_key,
            nickname="primary",
        )

    assert webauthn_enrollment.main(["list", "--operator", "Peter"]) == 0
    printed = capsys.readouterr().out
    assert "primary" in printed
    assert bytes_to_base64url(authenticator.cose_public_key) not in printed
    assert bytes_to_base64url(authenticator.credential_id) not in printed


# ---------------------------------------------------------------------------
# C-06
# ---------------------------------------------------------------------------


async def test_the_kill_switch_closes_the_portal_and_leaves_health_answering(
    client, tmp_path, monkeypatch, settings
):
    """C-06 / N-56. Layer 1, and the property that makes it usable in an incident.

    Health stays up deliberately: it is on the loopback bind, is not published by
    Caddy, and is what an operator watches while recovering.
    """
    from tools import portal_kill_switch

    monkeypatch.setenv("WEB_KILL_SWITCH_FILE", str(settings.kill_switch_file))

    assert (await client.get("/v1/login")).status_code == 200

    assert (
        portal_kill_switch.main(
            ["on", "--operator", "Peter", "--reason", "portal incident"]
        )
        == 0
    )
    assert settings.kill_switch_file.exists()

    # N-56 bounds the switch's latency at one second per process, because the
    # file is `stat`-ed at most once per second rather than on every request.
    # The wait is the contract, not a flake: asserting immediately would be
    # asserting a policy the platform does not have.
    import asyncio

    await asyncio.sleep(1.05)

    closed = await client.get("/v1/login")
    assert closed.status_code == 503
    assert "Discord bot is unaffected" in closed.text
    assert closed.headers["retry-after"] == "300"

    health = await client.get("/healthz")
    assert health.status_code in (200, 503)
    assert health.json()["checks"]["kill_switch"] is False

    assert portal_kill_switch.main(["off", "--operator", "Peter", "--reason", "done"]) == 0
    assert not settings.kill_switch_file.exists()

    await asyncio.sleep(1.05)
    assert (await client.get("/v1/login")).status_code == 200


def test_the_kill_switch_refuses_a_relative_path(monkeypatch, capsys):
    """A relative path resolves against the working directory, not the operator's intent."""
    from tools import portal_kill_switch

    monkeypatch.setenv("WEB_KILL_SWITCH_FILE", "relative/kill")
    assert portal_kill_switch.main(["status"]) == 4
    assert "absolute path" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# C-07
# ---------------------------------------------------------------------------


def test_revoking_every_session_refuses_each_on_its_next_request(
    migrated_database, composition, operator_environment, capsys
):
    """TC-SESS-07 through the CLI an operator actually runs."""
    from application.audit import ActorCapability
    from application.web.capabilities import (
        AdministratorScope,
        AuthMethod,
        WebAuthorizationContext,
    )
    from tools import session_revoke

    with migrated_database.begin() as connection:
        account_id = make_account(connection, protected=True)
        context = WebAuthorizationContext(
            account_id=account_id,
            auth_method=AuthMethod.WEBAUTHN,
            capabilities=frozenset({ActorCapability.PLATFORM_ADMINISTRATOR}),
            administrator_scope=AdministratorScope.EMERGENCY_CONTINUITY,
            membership=None,
        )
        issued = [
            composition.services(connection).session_service.begin(
                context=context, now=utcnow(), correlation_id=uuid4()
            )
            for _ in range(2)
        ]

    assert (
        session_revoke.main(
            [
                "--protected-admin",
                "--operator",
                "Peter",
                "--reason",
                "suspected compromise",
            ]
        )
        == 0
    )
    assert "Revoked 2 session(s)" in capsys.readouterr().out

    for session in issued:
        with migrated_database.begin() as connection:
            assert (
                composition.services(connection).session_service.resolve(
                    session.token, now=utcnow()
                )
                is None
            )

    with migrated_database.connect() as connection:
        reasons = connection.execute(select(sessions.c.revocation_reason)).scalars().all()
        event = connection.execute(
            select(audit_events).where(
                audit_events.c.action == "auth.session.revoked_all"
            )
        ).mappings().one()
    assert set(reasons) == {"operator"}
    assert event["payload"]["revoked"] == 2
    assert "suspected compromise" in event["payload"]["operator"]


def test_session_revoke_refuses_an_unknown_account(
    migrated_database, operator_environment, capsys
):
    """A command that silently did nothing would look identical to one that worked."""
    from tools import session_revoke

    assert (
        session_revoke.main(
            ["--account", str(uuid4()), "--operator", "Peter", "--reason", "r"]
        )
        == 1
    )
    assert "no such platform account" in capsys.readouterr().out
