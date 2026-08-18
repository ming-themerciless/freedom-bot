"""C-04 has a narrow configuration graph, with canonical database safety."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

import tools.identity_migration as command

from application.web.config import PRODUCTION_GUILD_ID
from tools.identity_migration import IdentityMigrationSettings


def environment(**overrides: str) -> dict[str, str]:
    values = {
        "WEB_ENVIRONMENT": "development",
        "WEB_DATABASE_URL": "postgresql+psycopg:///freedom_dev",
        "WEB_DISCORD_GUILD_ID": "700000000000003001",
    }
    values.update(overrides)
    return values


def test_c04_settings_need_only_the_values_the_command_consumes():
    settings = IdentityMigrationSettings.from_environment(environment())

    assert settings.database.environment == "development"
    assert settings.database.identity.database == "freedom_dev"
    assert settings.guild_id == 700000000000003001


def test_c04_settings_reuse_database_name_safety():
    with pytest.raises(ValueError, match="freedom_dev"):
        IdentityMigrationSettings.from_environment(
            environment(WEB_DATABASE_URL="postgresql+psycopg:///freedom_test")
        )


@pytest.mark.parametrize("guild_id", ["", "not-a-snowflake", "0", "-1"])
def test_c04_settings_refuse_an_invalid_guild_id(guild_id: str):
    with pytest.raises(ValueError, match="WEB_DISCORD_GUILD_ID"):
        IdentityMigrationSettings.from_environment(
            environment(WEB_DISCORD_GUILD_ID=guild_id)
        )


def test_c04_refuses_the_production_guild_outside_production():
    """S-07's second half: no non-production run may touch the production guild.

    C-04 scopes its membership scan and every proposal row it writes by this
    snowflake, so a development run carrying the production guild attributes
    evidence to the real community.
    """
    with pytest.raises(ValueError, match="WEB_DISCORD_GUILD_ID"):
        IdentityMigrationSettings.from_environment(
            environment(WEB_DISCORD_GUILD_ID=str(PRODUCTION_GUILD_ID))
        )


def test_c04_refuses_a_foreign_guild_in_production():
    """S-07's first half, and the likelier operator error of the two.

    The one-time migration is a production run. A staging snowflake copied into
    the temporary environment would write a whole evidence run scoped to a guild
    whose members the production database has never projected.
    """
    with pytest.raises(ValueError, match="WEB_DISCORD_GUILD_ID"):
        IdentityMigrationSettings.from_environment(
            environment(
                WEB_ENVIRONMENT="production",
                WEB_DATABASE_URL="postgresql+psycopg:///freedom_production",
                WEB_DISCORD_GUILD_ID="700000000000003001",
            )
        )


def test_c04_accepts_the_production_guild_in_production():
    """The accepted pairing still starts: the guard refuses mismatches only."""
    settings = IdentityMigrationSettings.from_environment(
        environment(
            WEB_ENVIRONMENT="production",
            WEB_DATABASE_URL="postgresql+psycopg:///freedom_production",
            WEB_DISCORD_GUILD_ID=str(PRODUCTION_GUILD_ID),
        )
    )

    assert settings.guild_id == PRODUCTION_GUILD_ID
    assert settings.database.identity.database == "freedom_production"


# ---------------------------------------------------------------------------
# The command path: every configuration refusal lands before Google or an engine
# ---------------------------------------------------------------------------
#: The accepted invocation. These cases never get far enough to read the tab.
C04_ARGV = ["--dry-run", "--player-tab", "Players"]


def drive_main(monkeypatch, values, *, capsys=None):
    """Run `main` against a synthetic environment, with both boundaries armed.

    `create_engine` and the Sheet reader raise if they are reached at all, so a
    case cannot pass merely by exiting 2 for some later reason: the refusal has
    to happen before the command connects to anything. Only this module's `os`
    is substituted, so the real process environment is untouched.
    """

    def engine_boom(*args, **kwargs):
        raise AssertionError("an engine was created before configuration passed")

    def sheet_boom(*args, **kwargs):
        raise AssertionError("Google was reached before configuration passed")

    monkeypatch.setattr(command, "os", SimpleNamespace(environ=dict(values)))
    monkeypatch.setattr("sqlalchemy.create_engine", engine_boom)
    monkeypatch.setattr(command, "build_values_reader", sheet_boom)
    return command.main(list(C04_ARGV))


def test_an_invalid_environment_database_pairing_refuses_before_anything_connects(
    monkeypatch, capsys
):
    """S-01 through the narrow boundary: the pairing is refused, not the URL."""
    exit_code = drive_main(
        monkeypatch, environment(WEB_DATABASE_URL="postgresql+psycopg:///freedom_production")
    )

    assert exit_code == command.EXIT_MISCONFIGURED
    stderr = capsys.readouterr().err
    assert "Configuration refused" in stderr
    # The refusal names the databases it compared and never the connection URL.
    assert "postgresql+psycopg" not in stderr


def test_a_malformed_guild_id_refuses_before_google_is_reached(monkeypatch, capsys):
    exit_code = drive_main(monkeypatch, environment(WEB_DISCORD_GUILD_ID="not-a-snowflake"))

    assert exit_code == command.EXIT_MISCONFIGURED
    assert "WEB_DISCORD_GUILD_ID" in capsys.readouterr().err


def test_an_inherited_pghost_is_still_subject_to_canonical_validation(
    monkeypatch, capsys
):
    """The documented socket URL, redirected by the ambient libpq environment.

    `WEB_DATABASE_URL` names the right database and says nothing about a host,
    so only the inherited variable decides where the credentials go. C-04 passes
    the whole mapping as the libpq environment, so the canonical resolver sees
    it and `SOCKET_OR_LOOPBACK` refuses the remote target.
    """
    exit_code = drive_main(monkeypatch, environment(PGHOST="db.example.org"))

    assert exit_code == command.EXIT_MISCONFIGURED
    stderr = capsys.readouterr().err
    assert "Configuration refused" in stderr
    assert "db.example.org" in stderr


def test_a_hostaddr_inherited_beside_a_socket_url_is_refused_too(monkeypatch, capsys):
    """`PGHOSTADDR` outranks `host`, which is the subtler half of the same rule."""
    exit_code = drive_main(monkeypatch, environment(PGHOSTADDR="203.0.113.7"))

    assert exit_code == command.EXIT_MISCONFIGURED
    assert "Configuration refused" in capsys.readouterr().err
