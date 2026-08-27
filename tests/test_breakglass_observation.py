"""The C-11/C-12 harness must refuse before it acts, and S-15 must actually fire.

Two properties matter here, and they pull in opposite directions:

1. **It must reach S-15's production branch**, or criterion 4b cannot be
   discharged before exposure at all — which was the substance of Codex finding
   B-1 and decision D-o.
2. **It must be unable to touch anything real** while doing so.

Every guard below is falsified rather than asserted: the refusal is made to fire,
because a guard that has never fired is a guard nobody has tested.

**These tests are not the SP-27 evidence.** SP-27 is a supervised exercise
against a disposable database actually named `freedom_production`, with outbound
egress blocked and a recorded teardown. What is proved here is that the harness
behaves, so the sitting is spent observing rather than debugging.
"""
from __future__ import annotations

import pytest
from sqlalchemy import text
from uuid import uuid4

from application.web.config import (
    PRODUCTION_GUILD_ID,
    PRODUCTION_ORIGIN,
    PRODUCTION_REDIRECT_URI,
    WebEnvironment,
)
from tools.breakglass_observation import (
    MARKER_TABLE,
    SYNTHETIC_OPERATOR,
    ObservationRefused,
    _assert_no_foreign_credentials,
    _ephemeral_key,
    assert_disposable,
    assert_prepared_by_this_harness,
    build_settings,
    clear,
    count_credentials,
    observe,
    seed,
)


# ---------------------------------------------------------------------------
# Settings: identifiers only, and no key material in the file
# ---------------------------------------------------------------------------


def test_production_settings_are_built_from_the_accepted_identifiers():
    settings = build_settings("production", "postgresql+psycopg:///freedom_production")
    assert settings.environment is WebEnvironment.PRODUCTION
    assert settings.public_origin == PRODUCTION_ORIGIN
    assert settings.discord.redirect_uri == PRODUCTION_REDIRECT_URI
    assert settings.discord.guild_id == PRODUCTION_GUILD_ID


def test_the_synthetic_client_secret_is_not_one_of_the_refused_placeholders():
    """S-07 refuses `.env.example`'s placeholder tokens.

    The assertion is that the settings **built**: had the harness used a
    placeholder, S-07 would have refused it, and this call would have raised.
    """
    settings = build_settings("production", "postgresql+psycopg:///freedom_production")
    assert settings.environment is WebEnvironment.PRODUCTION


def test_keys_are_generated_per_invocation_rather_than_written_into_the_file():
    first, second = _ephemeral_key(), _ephemeral_key()
    assert first != second
    assert len(first) == 44  # 32 random bytes, base64


def test_staging_is_refused_before_any_connection_is_attempted():
    """Finding N-10, made executable.

    The criterion asks for a staging marker on a disposable database. Each
    environment is bound to one database name, so that would mean the deployed
    staging database and the protected account's real credentials.
    """
    with pytest.raises(ObservationRefused) as refusal:
        build_settings("staging", "postgresql+psycopg:///freedom_staging")
    message = str(refusal.value)
    assert "freedom_staging" in message
    assert "REAL credentials" in message
    assert "N-10" in message


def test_an_unknown_environment_is_refused():
    with pytest.raises(ObservationRefused, match="is not one of"):
        build_settings("prod", "postgresql+psycopg:///whatever")


# ---------------------------------------------------------------------------
# Guards, each made to fire
# ---------------------------------------------------------------------------


def test_a_production_target_is_refused_without_the_operators_acknowledgement(db_connection):
    with pytest.raises(ObservationRefused, match="acknowledge-disposable"):
        assert_disposable(db_connection, "production", acknowledged=False)


def test_a_production_target_carrying_real_rows_is_refused(db_connection):
    """The strong guard: a real production database is never empty of history."""
    db_connection.execute(
        text("INSERT INTO discord_users (id, username) VALUES (:id, :username)"),
        {"id": 900000000000000123, "username": "synthetic"},
    )
    with pytest.raises(ObservationRefused) as refusal:
        assert_disposable(db_connection, "production", acknowledged=True)
    assert "discord_users=1" in str(refusal.value)


def test_a_disposable_production_target_passes_the_guard_when_empty(db_connection):
    # The other side of the falsification: the guard must not refuse everything.
    assert_disposable(db_connection, "production", acknowledged=True)


def test_a_non_production_target_needs_no_acknowledgement(db_connection):
    assert_disposable(db_connection, "test", acknowledged=False)


def test_a_credential_this_harness_did_not_create_stops_it_before_any_write(db_connection):
    account_id = uuid4()
    db_connection.execute(
        text(
            "INSERT INTO platform_accounts (id, status, is_protected_admin, display_label) "
            "VALUES (:id, 'active', true, 'someone else')"
        ),
        {"id": account_id},
    )
    db_connection.execute(
        text(
            "INSERT INTO webauthn_credentials "
            "(id, platform_account_id, credential_id, public_key, created_by_operator) "
            "VALUES (:id, :account, :cid, :key, 'a real operator')"
        ),
        {"id": uuid4(), "account": account_id, "cid": b"\x01\x02", "key": b"\x03\x04"},
    )
    with pytest.raises(ObservationRefused, match="did not create"):
        _assert_no_foreign_credentials(db_connection)


def test_a_database_this_harness_did_not_prepare_is_refused(db_connection):
    with pytest.raises(ObservationRefused, match=MARKER_TABLE):
        assert_prepared_by_this_harness(db_connection)


# ---------------------------------------------------------------------------
# The observation itself
# ---------------------------------------------------------------------------


def test_below_the_threshold_a_production_marked_check_refuses_and_names_s15(
    committed_database,
):
    """Criterion 4b's mechanism, proved without a listener.

    `run_resource_checks` is a plain function, so the production branch is
    reached with no uvicorn, no bind and no route — the fact D-o turns on.
    """
    with committed_database.connect() as connection:
        counts = seed(connection, credentials=1)
        assert counts.enabled == 1

    settings = build_settings("production", "postgresql+psycopg:///freedom_production")
    outcome, lines = observe(settings, committed_database)

    assert outcome == "refused"
    rendered = "\n".join(lines)
    assert "S-15" in rendered
    assert "at least 2" in rendered


def test_at_the_threshold_the_same_production_marked_check_passes(committed_database):
    """The falsification: the refusal is about the threshold, not about production.

    Without this, a harness that refused every production-marked check for any
    reason would look identical to one that observed S-15.
    """
    with committed_database.connect() as connection:
        counts = seed(connection, credentials=2)
        assert counts.enabled == 2

    settings = build_settings("production", "postgresql+psycopg:///freedom_production")
    outcome, _ = observe(settings, committed_database)

    assert outcome == "passed"


def test_below_the_threshold_a_non_production_check_warns_instead_of_refusing(
    committed_database,
):
    """S-15 outside production is a warning. Criterion 4a's half of the pair."""
    with committed_database.connect() as connection:
        seed(connection, credentials=1)

    settings = build_settings("test", "postgresql+psycopg:///freedom_test")
    outcome, lines = observe(settings, committed_database)

    assert outcome == "passed"
    assert any("S-15" in line for line in lines)


def test_clearing_removes_exactly_what_the_harness_created(committed_database):
    with committed_database.connect() as connection:
        seed(connection, credentials=2)
        assert count_credentials(connection).enabled == 2
        clear(connection)
        assert count_credentials(connection).enabled == 0
        assert count_credentials(connection).total == 0
        assert connection.execute(
            text("SELECT to_regclass(:name)"), {"name": f"public.{MARKER_TABLE}"}
        ).scalar() is None
        remaining = connection.execute(
            text(
                "SELECT count(*) FROM webauthn_credentials "
                "WHERE created_by_operator = :operator"
            ),
            {"operator": SYNTHETIC_OPERATOR},
        ).scalar_one()
        assert remaining == 0
