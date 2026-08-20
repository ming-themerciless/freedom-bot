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

from starlette.routing import Mount

from adapters.web.app import (
    DEFERRED_ROUTES,
    MOUNT_INVENTORY,
    ROUTE_INVENTORY,
    create_app,
)
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

#: `| M-01 | `static` | `/static` | …` — route contract §1.2's mount table.
#:
#: A **second** grammar rather than a widened first one, because a mount is not a
#: `(method, path)` pair: it claims a prefix, for every method its sub-application
#: answers. Parsing it as a route would have required inventing a method column
#: the contract does not have.
_MOUNT_ROW = re.compile(
    r"^\|\s*(?P<id>M-\d+)\s*\|\s*`(?P<name>[^`]+)`\s*\|\s*`(?P<prefix>[^`]+)`\s*\|",
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


def parsed_contract_mounts() -> dict[str, str]:
    """Every mount §1.2 defines, by identifier. Parsed, for the same reason."""
    body = ROUTE_CONTRACT.read_text()
    return {
        match.group("id"): match.group("prefix")
        for match in _MOUNT_ROW.finditer(body)
    }


# ---------------------------------------------------------------------------
# TC-STRUCT-01
# ---------------------------------------------------------------------------


def test_the_registered_route_set_equals_the_contract_exactly(app):
    """TC-STRUCT-01. No extra route, no missing route, no drifted method or path.

    This is the structural control behind *"no Phase 3 route or form mutates
    character game state"*: the set is closed, so a mutation endpoint cannot be
    added without failing here.

    **This half sees only ordinary method routes.** `getattr(route, "methods", …)`
    is empty for a Starlette `Mount`, so mounts are asserted separately, by
    `test_the_registered_mount_set_equals_the_contract_exactly` below. The two
    together are TC-STRUCT-01.
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


def test_the_registered_mount_set_equals_the_contract_exactly(app):
    """TC-STRUCT-01, mount half. **Added 2026-08-19 (accepted D-03 correction).**

    The case above compares `(method, path)` pairs built from
    `getattr(route, "methods", …)`. A Starlette `Mount` has **no** `methods`
    attribute, so it contributed nothing to that set: `app.mount("/anything",
    SomeApp())` added an entire URL subtree — every method, every path beneath it
    — and the one machine check protecting the closed inventory did not notice.
    That was D-03-1's second half, and this is the assertion that closes it.

    Both directions, like the route halves: every registered mount is declared,
    and every declared mount is registered, and the identifiers agree with the
    contract's own §1.2 table. Falsification evidence — this test failing against
    a deliberately reintroduced undeclared mount, and the tree restored by digest
    afterwards — is recorded in the D-03 correction submission.
    """
    contract = parsed_contract_mounts()
    assert contract, "the mount table in route contract §1.2 could not be parsed"

    registered = {route.path for route in app.routes if isinstance(route, Mount)}
    assert registered == set(MOUNT_INVENTORY.values()), (
        "the registered mount set is not the declared one; an undeclared Mount "
        "claims a whole URL subtree and is a contract violation, not a detail"
    )

    for identifier, prefix in MOUNT_INVENTORY.items():
        assert identifier in contract, f"{identifier} is not in the contract"
        assert contract[identifier] == prefix, identifier

    unaccounted = set(contract) - set(MOUNT_INVENTORY)
    assert unaccounted == set(), f"mounts with no owner: {sorted(unaccounted)}"


def test_the_only_mount_is_the_static_surface(app):
    """One mount, and it is M-01. Stated as its own fact, not inferred.

    The case above proves *agreement* between the contract and the build. This
    one states the number, so that a future change adding a second mount — and
    declaring it in both places, which would keep the case above green — is still
    a visible, deliberate edit to a test rather than a silent widening of the
    application's URL surface.
    """
    mounts = [route for route in app.routes if isinstance(route, Mount)]
    assert len(mounts) == 1
    assert mounts[0].path == "/static"
    assert mounts[0].name == "static"


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
    ("method", "path"),
    [
        # Every plausible shape of the routes the accepted inventory does **not**
        # contain: an artifact download, an audit export, an audit mutation, a
        # correction, a bulk confirmation and a synchronous preview or apply.
        ("GET", "/v1/council/snapshots/00000000-0000-4000-8000-000000000000/artifact"),
        ("GET", "/v1/council/snapshots/00000000-0000-4000-8000-000000000000/download"),
        ("GET", "/v1/audit/export"),
        ("GET", "/v1/audit.csv"),
        ("POST", "/v1/audit/00000000-0000-4000-8000-000000000000/correct"),
        ("DELETE", "/v1/audit/00000000-0000-4000-8000-000000000000"),
        ("POST", "/v1/council/snapshots/00000000-0000-4000-8000-000000000000/preview"),
        ("POST", "/v1/council/snapshots/00000000-0000-4000-8000-000000000000/apply"),
    ],
)
async def test_a_route_outside_the_accepted_inventory_does_not_exist(
    client, method, path
):
    """The closed set, from the other direction. **Updated by P3.3** (2026-08-18).

    This case used to name the four P3.3 navigation paths and assert `404`,
    because the package was behind stop gate P3.G2 and the gate was enforced by
    the routes not being there. They exist now, so the same assertion about the
    same paths would be asserting that P3.3 was not delivered — and there is no
    later package in the accepted inventory to move it on to, because R-49 is the
    last route the contract defines.

    What the case is *for* is unchanged and is now stated directly: the set is
    closed, and the routes the contract deliberately **excludes** answer `404`.
    Each path below is one the route contract names as absent — no artifact
    download, no audit export, no audit mutation or deletion, no correction, and
    no synchronous preview or apply — so a future handler that reintroduced one
    fails here as well as at `TC-STRUCT-01`.

    `404` and not `405`: a path that does not exist is not a method that is not
    allowed, and answering the second would confirm the path.
    """
    response = await client.request(method, path)
    assert response.status_code == 404


@pytest.mark.parametrize(
    ("method", "path"),
    [
        # A mutation on a path the inventory registers as a **read**. There is no
        # audit write use case anywhere in the application, and no handler here.
        ("POST", "/v1/audit"),
        ("PUT", "/v1/audit"),
        ("DELETE", "/v1/audit"),
        ("POST", "/v1/audit/results"),
        ("POST", "/v1/council/snapshots"),
        ("POST", "/v1/council/imports/00000000-0000-4000-8000-000000000000"),
        # `apply` where a job id belongs: the path pattern matches, the method
        # does not exist on it. There is no bulk confirmation route.
        ("POST", "/v1/council/jobs/apply"),
    ],
)
async def test_a_mutation_on_a_read_only_path_is_not_allowed(client, method, path):
    """`405`, and the distinction from `404` is the point.

    These paths **do** exist — as reads. `405` is the honest answer and confirms
    what the inventory says: the route is registered for `GET` and for no other
    method, so there is no audit export, no audit mutation, no audit deletion and
    no bulk confirmation however the request is shaped.

    Asserted rather than assumed, because "no handler is registered" and "a
    handler exists and refuses" are different facts, and only the first of them
    is what the closed inventory claims here.
    """
    response = await client.request(method, path)
    assert response.status_code == 405


@pytest.mark.parametrize(
    "path",
    [
        "/v1/council/snapshots",
        "/v1/council/jobs/00000000-0000-4000-8000-000000000000",
        "/v1/council/imports/00000000-0000-4000-8000-000000000000",
        "/v1/audit",
    ],
)
async def test_a_p3_3_navigation_route_exists_and_refuses_an_unauthenticated_caller(
    client, path
):
    """Present, and refusing — the pair `404` cannot express.

    The counterpart of the P3.2 case below, for the import, job and audit
    surface. A route accidentally left unguarded would answer `200` here.
    """
    response = await client.get(path)
    assert response.status_code == 303
    assert response.headers["location"] == "/v1/login"


@pytest.mark.parametrize(
    "path",
    [
        "/v1/council/jobs/00000000-0000-4000-8000-000000000000/status",
        "/v1/audit/results",
    ],
)
async def test_a_p3_3_fragment_refuses_an_unauthenticated_caller_with_401(
    client, path
):
    """A fragment answers `401`, not `303` (route contract §2.3).

    A redirect swapped into a fragment target would render the login page inside
    the job screen, which looks like a broken page rather than a signed-out one.
    """
    assert (await client.get(path)).status_code == 401


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


def test_the_denial_view_cannot_carry_anything_that_would_break_byte_identity():
    """TC-VM-06. **Added 2026-08-19 (accepted D-03 correction, item D-03-6).**

    The same technique as the case above, applied to the denial body. Route
    contract §2.3 requires the `404` for an unreachable object and the `404` for
    an absent one to be byte-identical, and `denied.html` used to be handed a
    `NonMemberView` with three deliberately inert fields — an empty guild name, an
    empty `Instant` and the nil UUID. That was correct only while the template
    declined to print them, and P3.4 rewrites the template.

    `DeniedView` has exactly two fields, so there is nothing to print. The
    assertion is equality, not a subset: a field **added** here is what would
    reintroduce the hazard, and the failure message says so because the next
    person to hit it will be adding one for a good-looking reason.
    """
    names = {field.name for field in fields(view_models.DeniedView)}
    assert names == {"state", "reason"}, (
        "DeniedView must carry `state` and a closed-vocabulary `reason` and "
        "nothing else. A correlation id, guild name, timestamp, object "
        "identifier or free-text reason on this view model breaks the "
        "byte-identical 404 of route contract §2.3 (TC-OBJ-07) and is a "
        "security change, not a presentation improvement."
    )


def test_the_denied_reason_vocabulary_stays_closed():
    """The other half of the same control: `reason` is not a free-text field.

    A closed `DeniedView` carrying an open reason would leak exactly what the two
    fields were narrowed to prevent, so the vocabulary is asserted here rather
    than left to the type annotation.
    """
    categories = {member.value for member in view_models.DenialCategory}
    assert categories == {
        "not_authenticated",
        "not_a_member",
        "insufficient_capability",
        "not_available",
        "emergency_session_restricted",
        "service_degraded",
    }
