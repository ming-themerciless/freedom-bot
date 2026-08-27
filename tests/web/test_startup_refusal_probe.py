"""The probe must refuse when the portal would, and must never print a value.

The second property is the one that would matter if it were wrong: the probe is
run with the deployed environment file sourced into it, so it holds every secret
the portal holds. A probe that echoed its input would put them in an evidence
document.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from application.web.config import ProcessRole
from tests.web_fixtures import web_environment
from tools.startup_refusal_probe import EXIT_ACCEPTED, EXIT_REFUSED, probe

#: A value distinctive enough that finding it in the output proves a leak.
SECRET_MARKER = "synthetic-provider-secret"


def test_a_valid_environment_is_accepted(tmp_path: Path) -> None:
    code, message = probe(web_environment(tmp_path), ProcessRole.WEB)

    assert code == EXIT_ACCEPTED
    assert "NO REFUSAL" in message


@pytest.mark.parametrize(
    "override, refusal",
    [
        pytest.param({"WEB_PUBLIC_ORIGIN": "https://freedom-blades.rpgworld.org"}, "S-02", id="S-02"),
        pytest.param({"WEB_ALLOWED_HOSTS": "*"}, "S-04", id="S-04"),
        pytest.param({"WEB_DISCORD_SCOPES": "identify"}, "S-06", id="S-06"),
        pytest.param({"WEB_SESSION_IDLE_MINUTES": "90"}, "S-10", id="S-10"),
        pytest.param({"WORKER_ENABLED": "true"}, "S-11", id="S-11-web"),
    ],
)
def test_each_deliberately_wrong_value_is_refused(
    tmp_path: Path, override: dict[str, str], refusal: str
) -> None:
    code, message = probe(web_environment(tmp_path, **override), ProcessRole.WEB)

    assert code == EXIT_REFUSED
    assert f"[{refusal}]" in message


def test_s11_refuses_the_worker_direction_too(tmp_path: Path) -> None:
    """Both directions, because N-40's deployment mistake has two shapes."""
    code, message = probe(
        web_environment(tmp_path, WORKER_ENABLED="false"), ProcessRole.WORKER
    )

    assert code == EXIT_REFUSED
    assert "[S-11]" in message


def test_the_refusal_names_variables_and_never_their_values(tmp_path: Path) -> None:
    """The property that keeps the output safe to paste into evidence.

    Falsified rather than assumed: the environment handed in carries a
    distinctive secret, and the assertion is that it does not come back out.
    """
    environment = web_environment(
        tmp_path,
        WEB_ALLOWED_HOSTS="*",
        WEB_DISCORD_CLIENT_SECRET=SECRET_MARKER,
    )

    code, message = probe(environment, ProcessRole.WEB)

    assert code == EXIT_REFUSED
    assert SECRET_MARKER not in message
    # The variable is named; only the value is withheld.
    assert "WEB_ALLOWED_HOSTS" in message
    for value in environment.values():
        if len(value) > 12:  # skip short values like "true" that occur in prose
            assert value not in message, value
