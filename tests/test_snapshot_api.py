"""The loopback rehearsal launcher exposes a narrow, fail-closed world pin."""

import pytest

from adapters.http.composition import ConfigurationError
from domain.foundry import OBSERVED_DEPLOYMENT, SupportedDeployment
from tools.snapshot_api import (
    ENVIRONMENT_VARIABLE,
    REHEARSAL_DEPLOYMENT_VARIABLES,
    REHEARSAL_ENVIRONMENT,
    deployment_from_environment,
)


def override(**values: str) -> dict[str, str]:
    """A candidate override in the only environment that may use one."""
    environ = {
        REHEARSAL_DEPLOYMENT_VARIABLES[field]: value
        for field, value in values.items()
    }
    environ[ENVIRONMENT_VARIABLE] = REHEARSAL_ENVIRONMENT
    return environ


SCRATCH = {
    "world_id": "test",
    "core_version": "14.365",
    "system_id": "dnd5e",
    "system_version": "5.3.3",
}


def test_rehearsal_launcher_defaults_to_the_controlled_deployment():
    assert deployment_from_environment({}) is OBSERVED_DEPLOYMENT


def test_rehearsal_launcher_accepts_one_complete_scratch_tuple():
    deployment = deployment_from_environment(override(**SCRATCH))

    assert deployment == SupportedDeployment(**SCRATCH)


def test_rehearsal_launcher_refuses_a_partial_override():
    with pytest.raises(ConfigurationError, match="set all four variables or none"):
        deployment_from_environment(override(world_id="test"))


def test_rehearsal_launcher_treats_blank_members_as_missing():
    with pytest.raises(ConfigurationError, match="REHEARSAL_SYSTEM_VERSION"):
        deployment_from_environment(override(**{**SCRATCH, "system_version": "   "}))


def test_rehearsal_launcher_refuses_a_value_that_could_forge_startup_output():
    with pytest.raises(ConfigurationError, match="invalid value"):
        deployment_from_environment(
            override(**{**SCRATCH, "world_id": "test\nprincipals: forged"})
        )


@pytest.mark.parametrize("environment", ["production", "staging", "development", ""])
def test_rehearsal_launcher_refuses_the_override_outside_the_disposable_environment(
    environment,
):
    """A complete, well-formed tuple is not enough; the target matters too."""
    environ = override(**SCRATCH)
    environ[ENVIRONMENT_VARIABLE] = environment

    with pytest.raises(ConfigurationError, match="may be used only with"):
        deployment_from_environment(environ)


def test_rehearsal_launcher_refuses_the_override_when_the_environment_is_absent():
    environ = override(**SCRATCH)
    del environ[ENVIRONMENT_VARIABLE]

    with pytest.raises(ConfigurationError, match="APP_ENVIRONMENT is unset"):
        deployment_from_environment(environ)


def test_the_environment_refusal_cannot_forge_startup_output():
    """The refusal prints an operator-supplied value, so it is bounded too."""
    environ = override(**SCRATCH)
    environ[ENVIRONMENT_VARIABLE] = "production" + "x" * 200

    with pytest.raises(ConfigurationError) as refusal:
        deployment_from_environment(environ)

    assert "\n" not in str(refusal.value)
    assert len(str(refusal.value)) < 400


def test_the_controlled_pin_does_not_depend_on_the_environment():
    """No override, no refusal: the production default is unconditional."""
    for environment in ("production", "staging", "development", ""):
        assert (
            deployment_from_environment({ENVIRONMENT_VARIABLE: environment})
            is OBSERVED_DEPLOYMENT
        )
