"""F6/C2: the two-credential shortfall reaches an operator, or it reaches nobody.

Finding F6, from the 2026-08-25 supervised session. `run_resource_checks` produced
exactly the right words —

    [S-15] the protected administrator account has 1 enabled WebAuthn
           credential(s); N-13 requires at least 2.

— and then handed them to `composition.startup_warnings`, which no route, service,
repository or control read. It was never logged. It never reached VM-16. Outside
production, where S-15 is a warning rather than a refusal because the credentials
are hardware, a portal below break-glass's redundancy floor started normally and
answered `/healthz` with `status: ok` and every check green, byte-identically to a
healthy two-credential portal, permanently.

A-05 A-4 requires production-class startup to refuse below two **and** `/healthz` to
report the shortfall. The second half did not exist, so this module is the
regression that says it does: the boolean, at each of the three counts that matter,
the fact that it is queried fresh rather than remembered from boot, and the two
disclosure limits — a count is never published, and the log line carries no
credential.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pytest
from sqlalchemy import text

from adapters.web.app import create_app
from application.web.startup import (
    MINIMUM_ENROLLED_CREDENTIALS,
    build_health_view,
    run_resource_checks,
)
from tests.web.conftest import enroll_credential, make_account
from tests.web.lifespan import application_lifespan

pytestmark = pytest.mark.database


def _seed(migrated_database, credentials: int) -> None:
    """A protected account with `credentials` enabled credentials, or no account."""
    if credentials == 0:
        return
    with migrated_database.begin() as connection:
        account_id = make_account(
            connection, protected=True, label="Server Administrator"
        )
        for index in range(credentials):
            enroll_credential(
                connection,
                account_id,
                credential_id=f"synthetic-credential-{index}".encode(),
                public_key=f"synthetic-public-key-{index}".encode(),
                nickname=f"synthetic-{index}",
            )


def _check(body: dict, name: str) -> bool:
    return body["checks"][name]


# ---------------------------------------------------------------------------
# The check
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("credentials", [0, 1])
async def test_healthz_reports_the_shortfall_below_two_credentials(
    client, migrated_database, credentials
):
    """A-05 A-4's second half. Both states below the floor answer `false`.

    They are below it for different reasons, and the boolean deliberately does not
    distinguish them (2026-08-25, C4). `0` is not "not yet bootstrapped, therefore
    fine": the protected account does not exist, break-glass has no account to
    authenticate, and a Discord outage locks the administrator out. `1` **still
    authenticates** — that key signs in, and during an outage it may be the path an
    operator uses — but it is one loss away from the same lockout, so N-13's
    redundancy floor is unmet and the portal is not ready to be exposed.

    What the operator is told about the difference lives in the operations guide,
    where someone reading it mid-incident will find it; what `/healthz` carries is
    readiness, which is one bit.
    """
    _seed(migrated_database, credentials)

    response = await client.get("/healthz")
    body = response.json()

    assert _check(body, "break_glass_credentials") is False
    assert body["status"] == "degraded"
    assert response.status_code == 503


async def test_healthz_reports_ready_once_two_credentials_are_enrolled(
    client, migrated_database
):
    """A-05 A-5. The same endpoint, the other answer — and no other check moves."""
    _seed(migrated_database, MINIMUM_ENROLLED_CREDENTIALS)

    response = await client.get("/healthz")
    body = response.json()

    assert _check(body, "break_glass_credentials") is True
    assert body["status"] == "ok"
    assert response.status_code == 200


async def test_the_one_and_two_credential_bodies_are_no_longer_identical(
    client, migrated_database
):
    """F6 as it was observed, kept as a falsification.

    The finding was not "a check is missing" in the abstract: it was that the two
    databases produced the *same bytes*. If this ever passes for the wrong reason,
    the assertion above it has stopped meaning anything.
    """
    _seed(migrated_database, 1)
    shortfall = (await client.get("/healthz")).text

    with migrated_database.begin() as connection:
        connection.execute(text("DELETE FROM webauthn_credentials"))
        connection.execute(text("DELETE FROM platform_accounts"))
    _seed(migrated_database, 2)
    ready = (await client.get("/healthz")).text

    assert shortfall != ready, (
        "a one-credential portal and a ready one still answer /healthz identically"
    )


async def test_the_check_is_asked_again_rather_than_remembered_from_startup(
    client, migrated_database, composition
):
    """A credential retired an hour after startup is the same shortfall.

    The startup warning is a fact about boot. Answering the endpoint from it would
    report a portal ready because it *was* ready once, which is the failure mode
    `worker_heartbeat` and `identity_provider` were each corrected for.
    """
    _seed(migrated_database, MINIMUM_ENROLLED_CREDENTIALS)
    assert _check((await client.get("/healthz")).json(), "break_glass_credentials")

    with migrated_database.begin() as connection:
        connection.execute(
            text(
                "UPDATE webauthn_credentials SET disabled_at = now() "
                "WHERE nickname = 'synthetic-1'"
            )
        )

    body = (await client.get("/healthz")).json()
    assert _check(body, "break_glass_credentials") is False
    assert body["status"] == "degraded"


# ---------------------------------------------------------------------------
# What it must not carry
# ---------------------------------------------------------------------------


async def test_the_health_body_publishes_no_credential_count_or_material(
    client, migrated_database
):
    """VM-16 carries check names and booleans. The shortfall does not change that.

    `false` says the portal is not ready to be exposed. How many credentials the
    protected administrator holds, which authenticator they are, and what they are
    called are not facts this endpoint needs to hand to anything that can reach the
    loopback port.
    """
    _seed(migrated_database, 1)

    response = await client.get("/healthz")
    raw = response.text
    body = response.json()

    assert set(body) == {"status", "checks", "version", "environment"}
    assert all(isinstance(value, bool) for value in body["checks"].values())
    for leak in ("synthetic", "credential_id", "public_key", "nickname", "N-13", "S-15", "1 enabled"):
        assert leak not in raw, f"the response disclosed {leak!r}"


def test_the_operations_guide_separates_not_redundant_from_cannot_authenticate():
    """C4, 2026-08-25. The boolean is one bit; the guide owes the operator three states.

    The guide said fewer than two credentials meant "the emergency route cannot be
    used". True of zero and of no protected account, **false of exactly one** — a
    single enabled credential still signs in, and during a Discord outage it may be
    the path actually taken. Telling an operator mid-incident that the authenticator
    in their hand is unusable is worse than telling them nothing, so the corrected
    language is asserted rather than trusted to survive the next edit.
    """
    guide = (
        Path(__file__).resolve().parents[2] / "docs" / "operations" / "web-portal.md"
    ).read_text()
    section = guide[guide.index("**Read `false` as \"not ready\", not as \"no way in\"**"):]
    section = section[: section.index("Two limits, stated rather than implied")]

    assert "break-glass still works" in section, (
        "the one-credential row must say the remaining authenticator still signs in"
    )
    assert "cannot succeed at all" in section, (
        "the zero-credential row must say break-glass cannot authenticate"
    )
    assert "redundancy floor" in guide
    assert "the emergency route cannot be used" not in guide, (
        "the C4 claim must not return: it is false for exactly one credential"
    )


# ---------------------------------------------------------------------------
# The second channel: the startup log
# ---------------------------------------------------------------------------


async def test_the_startup_warning_is_logged_rather_than_only_assigned(
    composition, migrated_database, caplog
):
    """The other half of F6: the process started in silence.

    `startup_warnings` is still diagnostic output no control reads — that is
    deliberate, and `WebComposition` says so. What changed is that the lifespan no
    longer *only* assigns it.
    """
    _seed(migrated_database, 1)

    # The real lifespan, with the real checks: `create_app`'s default. The `app`
    # fixture passes `run_startup_checks=False`, so a test that used it would be
    # asserting about a startup that never ran the check it is named for.
    app = create_app(composition=composition)
    with caplog.at_level(logging.WARNING, logger="freedom.web"):
        async with application_lifespan(app) as messages:
            assert messages[-1]["type"] == "lifespan.startup.complete"

    logged = [record.getMessage() for record in caplog.records]
    assert any("S-15" in message for message in logged), (
        f"the S-15 shortfall was not logged at startup; saw {logged}"
    )
    # The message is the operator's, and it names no credential.
    for leak in ("synthetic", "credential_id", "public_key"):
        assert not any(leak in message for message in logged)


def test_the_warning_the_log_carries_is_the_one_the_check_answers(
    composition, migrated_database
):
    """One condition, two channels, and neither invented for the other."""
    _seed(migrated_database, 1)

    warnings = run_resource_checks(composition.settings, composition.engine)
    view = build_health_view(composition.settings, composition.engine, provider_ok=True)
    check = next(check for check in view.checks if check.name == "break_glass_credentials")

    assert [warning.refusal for warning in warnings] == ["S-15"]
    assert check.ok is False
    assert view.status == "degraded"
