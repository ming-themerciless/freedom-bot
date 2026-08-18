"""TC-STRUCT-01 to TC-STRUCT-06 and TC-VM-01/02: absences, checked mechanically.

Several controls in this package **are** the absence of something — a route, a
column, a capability, an import. An absence that is only described is an absence
nobody is maintaining, so each one here is parsed out of the accepted contract
document and asserted against the running application.
"""
from __future__ import annotations

import ast
import re
from dataclasses import fields, is_dataclass
from pathlib import Path

import pytest

from adapters.web.app import DEFERRED_ROUTES, ROUTE_INVENTORY, create_app
from application.web import view_models
from application.web.config import ConfigurationError, WebSettings
from tests.web_fixtures import web_environment

ROOT = Path(__file__).resolve().parents[2]
ROUTE_CONTRACT = ROOT / "docs" / "contracts" / "phase-3-route-authorization-contract.md"
VIEW_MODEL_CONTRACT = ROOT / "docs" / "contracts" / "phase-3-view-model-contract.md"

#: `| R-01 | `root` | GET | `/` | …`
_ROUTE_ROW = re.compile(
    r"^\|\s*(?P<id>R-\d+)\s*\|\s*`(?P<name>[^`]+)`\s*\|\s*(?P<method>[A-Z]+)\s*\|"
    r"\s*`(?P<path>[^`]+)`\s*\|",
    re.MULTILINE,
)


def parsed_contract_routes() -> dict[str, tuple[str, str]]:
    """Every route the accepted contract defines, by identifier.

    Parsed rather than transcribed: a transcription is a second copy, and the
    whole point of TC-STRUCT-01 is that there is only one.
    """
    body = ROUTE_CONTRACT.read_text()
    return {
        match.group("id"): (match.group("method"), match.group("path"))
        for match in _ROUTE_ROW.finditer(body)
    }


# ---------------------------------------------------------------------------
# TC-STRUCT-01
# ---------------------------------------------------------------------------


def test_the_registered_route_set_equals_the_contract_exactly(app):
    """TC-STRUCT-01. No extra route, no missing route, no drifted method or path.

    This is the structural control behind *"no Phase 3 route or form mutates
    character game state"*: the set is closed, so a mutation endpoint cannot be
    added without failing here.
    """
    contract = parsed_contract_routes()
    assert contract, "the route contract could not be parsed"

    registered = {
        (method, route.path)
        for route in app.routes
        for method in getattr(route, "methods", set()) or set()
        if method not in ("HEAD", "OPTIONS")
    }

    expected = set(ROUTE_INVENTORY.values())
    assert registered == expected

    # And every identifier this package claims matches the contract's own row.
    for identifier, pair in ROUTE_INVENTORY.items():
        assert identifier in contract, f"{identifier} is not in the contract"
        assert contract[identifier] == pair, identifier


def test_every_route_the_contract_defines_is_either_implemented_or_owned_by_a_later_package(
    app,
):
    """The other direction: nothing in the contract is silently missing.

    "Not yet" and "never" are different, and a reader should not have to infer
    which one a gap is. Every contract route is either in this build or named in
    `DEFERRED_ROUTES` with the package that owns it.
    """
    contract = parsed_contract_routes()
    unaccounted = set(contract) - set(ROUTE_INVENTORY) - set(DEFERRED_ROUTES)
    assert unaccounted == set(), f"routes with no owner: {sorted(unaccounted)}"


@pytest.mark.parametrize(
    "path",
    [
        "/v1/council/snapshots",
        "/v1/council/jobs/00000000-0000-4000-8000-000000000000",
        "/v1/audit",
        "/v1/audit/results",
    ],
)
async def test_a_route_owned_by_a_later_package_is_absent_from_this_build(client, path):
    """P3.G2 is a stop gate, and this is what makes it structural.

    **Updated by P3.2** (2026-08-16). This case previously named the member,
    Council and administration paths, and asserted `404` for each because P3.1
    had not built them. They exist now, so the same assertion made about the same
    paths would be asserting that P3.2 was not delivered.

    What the case is *for* is unchanged: the closed route set has a next package
    behind a gate, and the gate is enforced by the routes not being here. The
    paths are therefore moved on to P3.3's — snapshot import, durable jobs and
    audit search — which is where "not yet" now lives. The P3.2 paths are covered
    by the case below, which asserts they are present and refusing rather than
    absent, because those are different facts.
    """
    assert (await client.get(path)).status_code == 404


@pytest.mark.parametrize(
    "path",
    [
        "/v1/characters",
        "/v1/characters/00000000-0000-4000-8000-000000000000",
        "/v1/council/characters",
        "/v1/council/identity-migration",
        "/v1/council/field-profile",
        "/v1/admin/role-capabilities",
        "/v1/account/identities",
    ],
)
async def test_a_p3_2_navigation_route_exists_and_refuses_an_unauthenticated_caller(
    client, path
):
    """Present, and refusing — which is the pair `404` cannot express.

    A `404` says the route does not exist; `303` to the login page says it
    exists and this caller has no session (route contract §2.3). Asserting the
    second is what distinguishes "P3.2 is built and guarded" from "P3.2 is built
    and open", and a route accidentally left unguarded would answer `200` here.
    """
    response = await client.get(path)
    assert response.status_code == 303
    assert response.headers["location"] == "/v1/login"


# ---------------------------------------------------------------------------
# TC-STRUCT-04
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("POST", "/v1/characters/00000000-0000-4000-8000-000000000000"),
        ("PUT", "/v1/characters/00000000-0000-4000-8000-000000000000"),
        ("PATCH", "/v1/characters/00000000-0000-4000-8000-000000000000"),
        ("POST", "/v1/characters/00000000-0000-4000-8000-000000000000/level"),
        ("POST", "/v1/characters/00000000-0000-4000-8000-000000000000/correct"),
        ("POST", "/v1/admin/characters/correct"),
    ],
)
async def test_no_character_game_state_correction_endpoint_exists(client, method, path):
    """TC-STRUCT-04. Forged submissions to the plausible paths mutate nothing."""
    response = await client.request(method, path, json={"level": 20})
    assert response.status_code in (404, 405)


# ---------------------------------------------------------------------------
# TC-STRUCT-05
# ---------------------------------------------------------------------------


def test_the_web_module_graph_never_reaches_the_bot_config():
    """TC-STRUCT-05 / S-13. The separation is structural, not a convention.

    The bot's `config.py` calls `sys.exit()` on a missing variable, which is fine
    for a bot and wrong for a web process under a supervisor. Resolved by reading
    the *import graph* rather than by grepping: an alias, a re-export or a
    conditional import is still an import.
    """
    offenders: list[str] = []
    for directory in ("application/web", "adapters/web"):
        for path in sorted((ROOT / directory).glob("**/*.py")):
            if "__pycache__" in path.parts:
                continue
            tree = ast.parse(path.read_text(), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                else:
                    continue
                for name in names:
                    if name == "config" or name.startswith("config."):
                        offenders.append(f"{path.relative_to(ROOT)}: {name}")
    assert offenders == []


def test_importing_the_web_package_does_not_pull_in_the_bot_config():
    """The same rule, resolved by running rather than by reading."""
    import importlib
    import sys

    for name in [key for key in sys.modules if key == "config"]:
        del sys.modules[name]
    for module in (
        "application.web.config",
        "application.web.oauth",
        "application.web.breakglass",
        "adapters.web.app",
        "adapters.web.composition",
    ):
        importlib.import_module(module)
    assert "config" not in sys.modules


# ---------------------------------------------------------------------------
# TC-STRUCT-06 — the fifteen startup refusals
# ---------------------------------------------------------------------------


def _refusal_for(tmp_path, **overrides) -> ConfigurationError:
    with pytest.raises(ConfigurationError) as failure:
        WebSettings.from_environment(web_environment(tmp_path, **overrides))
    return failure.value


@pytest.mark.parametrize(
    ("refusal", "overrides"),
    [
        ("S-01", {"WEB_DATABASE_URL": "postgresql+psycopg:///freedom_production"}),
        (
            "S-02",
            {
                "WEB_PUBLIC_ORIGIN": "https://freedom-blades.rpgworld.org",
                "WEB_ALLOWED_HOSTS": "freedom-blades.rpgworld.org",
                "WEB_WEBAUTHN_RP_ID": "freedom-blades.rpgworld.org",
                "WEB_DISCORD_REDIRECT_URI": "https://freedom-blades.rpgworld.org/auth/discord/callback",
                "WEB_WEBAUTHN_ALLOWED_ORIGINS": "https://freedom-blades.rpgworld.org",
            },
        ),
        ("S-03", {"WEB_COOKIE_SECURE": "false"}),
        ("S-04", {"WEB_ALLOWED_HOSTS": "*"}),
        (
            "S-05",
            {"WEB_DISCORD_REDIRECT_URI": "https://elsewhere.test/auth/discord/callback"},
        ),
        ("S-06", {"WEB_DISCORD_SCOPES": "identify,guilds.members.read,email"}),
        ("S-07", {"WEB_DISCORD_GUILD_ID": "1052698198180892733"}),
        ("S-09", {"WEB_WEBAUTHN_RP_ID": "test"}),
        ("S-10", {"WEB_SESSION_IDLE_MINUTES": "90"}),
        ("S-10", {"WEB_SESSION_ABSOLUTE_HOURS": "24"}),
        ("S-10", {"WEB_EMERGENCY_SESSION_IDLE_MINUTES": "30"}),
        ("S-10", {"WEB_MEMBERSHIP_CACHE_SECONDS": "600"}),
        ("S-10", {"WEB_MAX_REQUEST_BYTES": str(4 * 1024 * 1024)}),
        ("S-10", {"WEB_RECOVERY_GRANT_MINUTES": "60"}),
        ("S-10", {"WEB_TRUSTED_PROXY_HOPS": "2"}),
        ("S-11", {"WORKER_ENABLED": "true"}),
        ("S-12", {"WORKER_ARTIFACT_ROOT": "relative/path"}),
    ],
)
def test_each_startup_refusal_refuses_with_its_documented_identifier(
    tmp_path, refusal, overrides
):
    """TC-STRUCT-06. A refusal that has never been observed refusing is an assumption."""
    error = _refusal_for(tmp_path, **overrides)
    assert refusal in error.refusals(), error.render()


def test_every_out_of_range_session_bound_is_reported_in_one_pass(tmp_path):
    """S-10, and rule 2 of this module: report every problem, not the first.

    Added 2026-08-15 with the idle-policy-construction remediation.
    `SessionSettings` now validates the accepted register in its own constructor
    (finding F1), and that constructor runs *inside* `_read_session` — so a
    reader accessor that returned the operator's rejected number would make the
    dataclass raise mid-collection and the operator would see one problem where
    there are five. The accessors record the problem and then fall back to an
    in-range value precisely so this stays true, and this is the test that would
    fail if that were undone.

    Four session bounds are pushed over their ceilings at once, plus a cookie
    name that is refused for a different reason, and all five must be named.
    """
    error = _refusal_for(
        tmp_path,
        WEB_SESSION_IDLE_MINUTES="90",
        WEB_SESSION_ABSOLUTE_HOURS="24",
        WEB_EMERGENCY_SESSION_IDLE_MINUTES="30",
        WEB_MAX_SESSIONS_PER_ACCOUNT="50",
        WEB_SESSION_COOKIE_NAME="fb_session",
    )
    rendered = error.render()
    for variable in (
        "WEB_SESSION_IDLE_MINUTES",
        "WEB_SESSION_ABSOLUTE_HOURS",
        "WEB_EMERGENCY_SESSION_IDLE_MINUTES",
        "WEB_MAX_SESSIONS_PER_ACCOUNT",
        "WEB_SESSION_COOKIE_NAME",
    ):
        assert variable in rendered, (
            f"{variable} must appear: an operator fixing five variables should "
            f"learn about all five in one attempt.\n{rendered}"
        )
    assert "S-10" in error.refusals()
    assert "S-03" in error.refusals()


def test_a_secret_shorter_than_the_minimum_or_shared_with_another_is_refused(tmp_path):
    """S-08, both halves. Key separation is what stops one token being valid elsewhere."""
    short = _refusal_for(tmp_path, WEB_SECRET_KEY_CSRF="tiny")
    assert "S-08" in short.refusals()

    shared_material = web_environment(tmp_path)["WEB_SECRET_KEY_CURSOR"]
    shared = _refusal_for(tmp_path, WEB_SECRET_KEY_CSRF=shared_material)
    assert "S-08" in shared.refusals()


def test_a_configuration_error_names_variables_and_never_values(tmp_path):
    """The rule that makes it safe to log a `ConfigurationError` in full.

    Every variable is given a recognisable value, and the rendered error is
    searched for it. A message that echoed the offending value would put a
    client secret into the first log line an operator pastes into a chat.
    """
    marker = "SUPERSECRETVALUE"
    environment = {
        key: marker for key in web_environment(tmp_path)
    }
    with pytest.raises(ConfigurationError) as failure:
        WebSettings.from_environment(environment)
    rendered = failure.value.render()
    assert marker not in rendered
    assert "WEB_ENVIRONMENT" in rendered


def test_a_valid_configuration_is_accepted(tmp_path):
    """The control case. Without it, every refusal test above could pass vacuously."""
    settings = WebSettings.from_environment(web_environment(tmp_path))
    assert settings.public_host == "portal.test"
    assert settings.discord.scopes == ("identify", "guilds.members.read")


def test_a_secret_never_renders_itself(tmp_path):
    """`SecretKey.__repr__` is overridden, not merely discouraged.

    A dataclass's generated `repr` would put key material into any traceback that
    formats the settings tree — and a traceback is exactly where nobody is
    watching.
    """
    settings = WebSettings.from_environment(web_environment(tmp_path))
    for key in (settings.csrf_key, settings.cursor_key, settings.client_digest_key):
        assert "redacted" in repr(key)
        assert key.material.decode("latin-1") not in repr(key)
    assert "redacted" in repr(settings.encryption.active)


# ---------------------------------------------------------------------------
# TC-VM-01, TC-VM-02, TC-STRUCT-02
# ---------------------------------------------------------------------------


def test_every_view_model_is_frozen_slotted_and_holds_no_mutable_collection():
    """TC-VM-01. A template cannot mutate what it was given, structurally."""
    for identifier, model in view_models.IMPLEMENTED_VIEW_MODELS.items():
        assert is_dataclass(model), identifier
        assert model.__dataclass_params__.frozen, f"{identifier} is not frozen"
        assert "__slots__" in model.__dict__, f"{identifier} is not slotted"
        for field in fields(model):
            annotation = str(field.type)
            assert "list[" not in annotation, f"{identifier}.{field.name}"
            assert "dict[" not in annotation, f"{identifier}.{field.name}"
            assert "set[" not in annotation, f"{identifier}.{field.name}"


def test_the_implemented_view_models_are_a_subset_of_the_documented_set():
    """TC-STRUCT-02, scoped to what P3.1 owns.

    The full equality the contract asks for is only reachable once P3.2 and P3.3
    have implemented theirs; until then the check is that every implemented model
    is documented and every documented one is either implemented or named as
    deferred with its owning package. Recorded as a partial in the P3.1
    submission rather than reported as the whole test.
    """
    documented = set(
        re.findall(r"^### (VM-\d+) `", VIEW_MODEL_CONTRACT.read_text(), re.MULTILINE)
    )
    assert documented, "the view-model contract could not be parsed"

    implemented = set(view_models.IMPLEMENTED_VIEW_MODELS)
    deferred = set(view_models.DEFERRED_VIEW_MODELS)

    assert implemented <= documented, sorted(implemented - documented)
    assert documented - implemented - deferred == set()
    assert implemented & deferred == set()
    assert view_models.VIEW_MODEL_VERSION == "vm-1"


def test_bounded_text_truncates_and_says_so():
    """TC-VM-02. The untruncated value is never sent."""
    long_name = "n" * 500
    bounded = view_models.SafeText.bounded(long_name, view_models.ACTOR_NAME_BOUND)
    assert bounded.truncated is True
    assert len(bounded.value) == view_models.ACTOR_NAME_BOUND

    short = view_models.SafeText.bounded("Alia", view_models.ACTOR_NAME_BOUND)
    assert short.truncated is False
    assert short.value == "Alia"


def test_a_deferred_field_cannot_carry_a_value():
    """TC-VM-03's structural half: the type makes it unrepresentable.

    `MigrationDeferred` has no value field, so a template cannot print one by
    accident and a service cannot supply one by mistake.
    """
    names = {field.name for field in fields(view_models.MigrationDeferred)}
    assert names == {"field_key", "owning_package"}
