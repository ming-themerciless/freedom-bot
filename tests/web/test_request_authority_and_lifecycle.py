"""TC-STRUCT-10 and TC-STRUCT-11: what a request reads, and what a shutdown closes.

Two blocking findings from the fresh independent review of the P3.G1
provider/engine authority remediation, both instances of the shape RAID I-09 and
I-10 track — **validate one thing, then use another** — and both now corrected
structurally rather than by a check.

## Finding 1: `app.state.settings` still governed requests

The provider/engine remediation bound the *composition* to the routes and wrote
that `app.state.settings` was a diagnostic reference whose replacement could not
affect request behaviour. The code said otherwise. `create_app()` assigned the
canonical graph to `app.state.settings`; `_settings(request)` read
`request.app.state.settings` on **every call**; and the request paths used that
helper for the client and user-agent digests, mutation-origin validation, the
session and login cookie names and attributes, CSRF key selection and the health
view. Starlette's `State` is an ordinary mutable namespace, so
`app.state.settings = graph_b` gave an already-validated application a second
complete settings graph to serve from — a different accepted `Origin`, a
different CSRF key authority, a different cookie contract and different keyed
audit and rate-limit identities than the graph the process checked. No private
mutation, no `object.__new__`, no unsupported API: one assignment.

§1 is that finding. Every case builds an application from graph A, replaces
**all four** diagnostic references with objects built from a distinct,
independently valid graph B, and then proves through public application
behaviour that A is still what answers. Graph B is a real configuration the
environment boundary accepts; a case that only worked against an invalid or
hostile second graph would prove less than the defect required.

§2 is the structural half: production request code reads no `app.state` at all,
asserted over the AST rather than reviewed.

## Finding 2: production resources were not wired to the ASGI lifecycle

`WebComposition.aclose()` closed its provider and disposed its engine when it
owned one, and had **no production caller**. `create_app()` installed no
lifespan and no shutdown handler, so a normal ASGI stop left the production HTTP
client and the SQLAlchemy engine and pool open. The evidence offered for the
lifecycle claim was tests calling `composition.aclose()` by hand, which proves
the method and says nothing about the process.

§3 is that finding. Every case drives the **real** lifespan protocol through
`tests/web/lifespan.py`, because `httpx.ASGITransport` never opens a `lifespan`
scope and a case that assumed otherwise would pass with no lifespan installed.

## Finding 3: a spent composition could start a second application

The lifecycle above is one-way — `aclose()` closes the provider's HTTP client
permanently and disposes an owned engine — and the lifespan checked nothing on
the way *in*. So a composition passed to two applications, or one application
whose lifespan was entered again, answered `lifespan.startup.complete` a second
time and served requests until an OAuth route dereferenced the closed provider.
The resource checks were no defence and could not become one: they never look at
the provider, and a disposed SQLAlchemy engine silently builds a replacement pool,
so S-14 and S-15 pass against resources nobody may use.

Worse, §3's repeated-shutdown case **codified** that outcome, entering a second
lifespan over a closed composition and requiring `lifespan.startup.complete` from
it. §3.1 is the correction: `WebComposition` now has an explicit one-way
lifecycle claimed by exactly one application startup, that case no longer enters a
second lifespan, and the second startup is proved to fail, to serve nothing, and
to leave the cleanup counts at exactly one.
"""
from __future__ import annotations

import ast
import asyncio
import base64
import logging
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import select

from adapters.database.tables import oauth_transactions, sessions
from adapters.web import app as app_module
from adapters.web import composition as composition_module
from adapters.web.app import create_app
from adapters.web.composition import (
    CompositionLifecycle,
    CompositionLifecycleError,
    WebComposition,
)
from adapters.web.middleware import ClientAddressPolicy
from application.audit import ActorCapability
from application.web import csrf
from application.web.capabilities import (
    AdministratorScope,
    AuthMethod,
    MembershipProjection,
    WebAuthorizationContext,
)
from application.web.config import (
    ConfigurationError,
    ConfigurationProblem,
    SettingsAuthorityError,
    WebSettings,
)
from application.web.crypto import keyed_digest
from application.web.startup import StartupWarning
from tests.web.composition_harness import substituted_composition
from tests.web.conftest import make_account, seed_oauth_transaction, utcnow
from tests.web.lifespan import application_lifespan, refused_startup
from tests.web_fixtures import (
    PUBLIC_ORIGIN,
    TEST_GUILD_ID,
    FakeDiscordProvider,
    web_settings,
)

pytestmark = pytest.mark.database

#: Graph B's origin. Deliberately *not* in graph A's `WEB_ALLOWED_HOSTS`, so a
#: request that reached the application under B's host rules would be visible as
#: well — but the assertions below are about the origin **header** check, which
#: runs inside the route on the captured graph.
INTRUDER_ORIGIN = "https://intruder.test"

#: Graph B's OAuth transaction lifetime, in minutes. Inside N-04's accepted
#: register — B has to be a configuration a process would accept — and different
#: from graph A's, so the login-transaction cookie's `Max-Age` distinguishes them.
INTRUDER_TRANSACTION_MINUTES = 9


def _key(seed: bytes) -> str:
    """32 bytes of distinct synthetic key material, base64 as the reader expects."""
    return base64.b64encode(seed * 32)[:44].decode("ascii")


def foreign_graph(tmp_path: Path) -> WebSettings:
    """**Graph B**: a second complete configuration the environment accepts.

    Every value below that a case discriminates on is materially different from
    graph A's, and the graph as a whole is one `WebSettings.from_environment`
    builds without a single recorded problem — the same boundary that produced
    graph A. That matters: the finding is that an application can be made to
    observe a *second valid graph*, so a second graph that was invalid, hostile,
    or assembled by private mutation would demonstrate a weaker defect than the
    one recorded.

    The four secret keys are distinct from each other, because `S-04` requires
    it, and distinct from graph A's, because otherwise "the CSRF key is A's"
    would be true for the wrong reason.
    """
    return web_settings(
        tmp_path,
        WEB_PUBLIC_ORIGIN=INTRUDER_ORIGIN,
        WEB_ALLOWED_HOSTS="intruder.test",
        WEB_WEBAUTHN_RP_ID="intruder.test",
        WEB_DISCORD_REDIRECT_URI=f"{INTRUDER_ORIGIN}/auth/discord/callback",
        WEB_DISCORD_CLIENT_ID="9990000003",
        WEB_SESSION_COOKIE_NAME="__Host-fb_session_intruder",
        WEB_OAUTH_TRANSACTION_MINUTES=str(INTRUDER_TRANSACTION_MINUTES),
        WEB_SECRET_KEY_CSRF=_key(b"C"),
        WEB_SECRET_KEY_CURSOR=_key(b"U"),
        WEB_SECRET_KEY_CLIENT_DIGEST=_key(b"D"),
        WEB_TOKEN_ENCRYPTION_KEYS=f"1:{_key(b'K')}",
    )


class RefusingAddressPolicy:
    """An address policy that answers a fixed foreign address for every request.

    Substituted onto `app.state.address_policy` so that "the captured policy is
    what resolved the client" is observable in durable state: if this object were
    consulted, the digest written by R-03 would be over `203.0.113.7` rather than
    over the loopback peer the request actually came from.
    """

    def __init__(self) -> None:
        self.calls = 0

    def resolve(self, request) -> str:
        self.calls += 1
        return "203.0.113.7"


def _marker_templates(tmp_path: Path):
    """A Jinja environment over a directory whose `login.html` says so.

    Substituted onto `app.state.templates`. A response containing `MARKER` would
    mean the rendering environment a route used was resolved per request; the
    real login page means it was the one captured at construction.
    """
    from fastapi.templating import Jinja2Templates

    root = tmp_path / "intruder-templates"
    root.mkdir()
    (root / "login.html").write_text(
        "<html><body>INTRUDER-TEMPLATE-MARKER</body></html>", encoding="utf-8"
    )
    templates = Jinja2Templates(directory=str(root))
    templates.env.autoescape = False
    return templates


def _install_graph_b(app, *, graph, composition, tmp_path) -> RefusingAddressPolicy:
    """Replace **every** diagnostic reference `create_app()` set, with B's.

    All four together, deliberately. Replacing only `app.state.settings` would
    leave a reader able to say the others were never claimed to be inert; the
    factory documents all four as diagnostic, so all four are attacked and all
    four assertions are about behaviour afterwards.
    """
    policy = RefusingAddressPolicy()
    app.state.settings = graph
    app.state.composition = composition
    app.state.templates = _marker_templates(tmp_path)
    app.state.address_policy = policy
    return policy


async def _client(app):
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url=PUBLIC_ORIGIN,
        follow_redirects=False,
    )


def _context(account_id):
    return WebAuthorizationContext(
        account_id=account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        capabilities=frozenset({ActorCapability.GUILD_MEMBER}),
        administrator_scope=AdministratorScope.FULL,
        membership=MembershipProjection(
            guild_id=TEST_GUILD_ID,
            is_member=True,
            role_ids=frozenset(),
            observed_at=utcnow(),
        ),
    )


def _begin_session(migrated_database, composition):
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        return composition.services(connection).session_service.begin(
            context=_context(account_id),
            now=utcnow(),
            correlation_id=uuid4(),
            oauth_transaction_id=seed_oauth_transaction(connection),
        )


@pytest.fixture()
def intruder_graph(tmp_path):
    return foreign_graph(tmp_path)


@pytest.fixture()
def under_replacement(settings, provider, migrated_database, intruder_graph, tmp_path):
    """An application built from A whose four diagnostic references are B's.

    Returned as `(app, original_provider, intruder_provider, policy)`. The
    intruder composition is a real one, built through the suite's substitution
    path from graph B, so `app.state.composition` afterwards is not a stub that
    would fail for the wrong reason — it is an object that could genuinely serve
    requests if anything dereferenced it.
    """
    composition = substituted_composition(
        settings=settings, engine=migrated_database, provider=provider
    )
    app = create_app(composition=composition, run_startup_checks=False)
    intruder = FakeDiscordProvider(subject="700000000000000002")
    policy = _install_graph_b(
        app,
        graph=intruder_graph,
        composition=substituted_composition(
            settings=intruder_graph, engine=migrated_database, provider=intruder
        ),
        tmp_path=tmp_path,
    )
    return app, provider, intruder, policy


# ---------------------------------------------------------------------------
# 1. Finding 1: behaviour comes from graph A after graph B is installed
# ---------------------------------------------------------------------------


async def test_the_accepted_origin_is_still_graph_as_after_the_replacement(
    under_replacement, settings, intruder_graph
):
    """Required property 1. The mutation-origin check, at a mutation route.

    `R-07` validates `Origin` before it does anything else, so this is the
    origin check on its own with no session, rate-limit budget or form body in
    the way. Both directions are asserted: A's origin is still accepted, and the
    origin only graph B would accept is refused. Refusing everything would pass
    the second half for the wrong reason.
    """
    app, *_ = under_replacement
    assert intruder_graph.public_origin != settings.public_origin

    async with await _client(app) as client:
        ours = await client.post(
            "/v1/auth/emergency/webauthn/options",
            headers={"origin": settings.public_origin},
        )
        theirs = await client.post(
            "/v1/auth/emergency/webauthn/options",
            headers={"origin": intruder_graph.public_origin},
        )

    assert ours.status_code == 200, "graph A's origin is still ours"
    assert theirs.status_code == 403
    assert theirs.json()["error"] == "origin_invalid"


async def test_csrf_verification_still_uses_graph_as_key(
    under_replacement, settings, intruder_graph, migrated_database
):
    """Required property 2. The synchronizer token, at `R-05`.

    A CSRF key that could be replaced after startup is a CSRF check an attacker
    can satisfy: they mint a token under the key they installed. Graph B's key is
    presented first — while the session is still live, so the refusal cannot be
    confused with an expired session — and graph A's key second.
    """
    app, *_ = under_replacement
    # The session below is minted through a composition built from graph A,
    # because a session is durable state and the CSRF token is derived from its
    # id — the discriminator here is the *key*, not where the row came from.
    # `==`, not `is`: `WebComposition` canonicalises what it is given, so the
    # intruder composition holds a rebuild of graph B rather than the object.
    assert app.state.composition.settings == intruder_graph
    assert app.state.composition.settings != settings

    real = substituted_composition(
        settings=settings,
        engine=migrated_database,
        provider=FakeDiscordProvider(role_ids=frozenset()),
    )
    issued = _begin_session(migrated_database, real)
    assert settings.csrf_key.material != intruder_graph.csrf_key.material

    async with await _client(app) as client:
        client.cookies.set(settings.session.cookie_name, issued.token)
        forged = await client.post(
            "/v1/auth/logout",
            data={"csrf_token": csrf.issue(intruder_graph.csrf_key, issued.session_id)},
            headers={"origin": settings.public_origin},
        )
        genuine = await client.post(
            "/v1/auth/logout",
            data={"csrf_token": csrf.issue(settings.csrf_key, issued.session_id)},
            headers={"origin": settings.public_origin},
        )

    assert forged.status_code == 403
    assert forged.json()["error"] == "csrf_invalid"
    assert genuine.status_code == 303, "and A's token still works"


async def test_the_session_cookie_looked_up_and_cleared_is_still_graph_as(
    under_replacement, settings, intruder_graph, migrated_database
):
    """Required property 3, the session cookie's **name**, in both directions.

    `R-01` branches on the presence of the session cookie, so the name the
    application answers to is observable without a session at all; `R-05` clears
    it by name, so the name it emits is observable too. A cookie name that
    changed after startup would silently log every authenticated caller out and
    leave the real cookie uncleared on logout.
    """
    app, *_ = under_replacement
    assert intruder_graph.session.cookie_name != settings.session.cookie_name

    async with await _client(app) as client:
        recognised = await client.get(
            "/", cookies={settings.session.cookie_name: "opaque"}
        )
        ignored = await client.get(
            "/", cookies={intruder_graph.session.cookie_name: "opaque"}
        )

    assert recognised.headers["location"] == "/v1/characters"
    assert ignored.headers["location"] == "/v1/login"

    real = substituted_composition(
        settings=settings,
        engine=migrated_database,
        provider=FakeDiscordProvider(role_ids=frozenset()),
    )
    issued = _begin_session(migrated_database, real)
    async with await _client(app) as client:
        client.cookies.set(settings.session.cookie_name, issued.token)
        response = await client.post(
            "/v1/auth/logout",
            data={"csrf_token": csrf.issue(settings.csrf_key, issued.session_id)},
            headers={"origin": settings.public_origin},
        )

    assert response.status_code == 303
    cleared = response.headers.get_list("set-cookie")
    assert any(
        header.startswith(f"{settings.session.cookie_name}=") for header in cleared
    ), cleared
    assert not any(
        header.startswith(f"{intruder_graph.session.cookie_name}=")
        for header in cleared
    ), cleared


async def test_the_login_cookie_emitted_still_carries_graph_as_attributes(
    under_replacement, settings, intruder_graph
):
    """Required property 3, the login-transaction cookie's **attributes**.

    Its name is derived from `WEB_COOKIE_SECURE` and is therefore the same in
    both graphs, so the discriminator here is `Max-Age`, which is
    `oauth_transaction_minutes * 60`. A cookie outliving its transaction is a
    replayable login attempt, which is why N-04's number is a register value and
    not an implementation detail.
    """
    app, *_ = under_replacement
    assert (
        intruder_graph.session.oauth_transaction_minutes
        != settings.session.oauth_transaction_minutes
    )

    async with await _client(app) as client:
        response = await client.get("/v1/auth/discord/start")

    assert response.status_code == 303
    cookie = next(
        header
        for header in response.headers.get_list("set-cookie")
        if header.startswith(f"{settings.session.login_transaction_cookie_name}=")
    )
    accepted = settings.session.oauth_transaction_minutes * 60
    assert f"Max-Age={accepted}" in cookie, cookie
    assert (
        f"Max-Age={intruder_graph.session.oauth_transaction_minutes * 60}"
        not in cookie
    ), cookie
    assert "Secure" in cookie and "HttpOnly" in cookie, cookie


async def test_both_client_digests_still_use_graph_as_digest_key(
    under_replacement, settings, intruder_graph, migrated_database
):
    """Required property 4, read back out of durable state.

    `client_digest_key` is what every audited client identity and every
    rate-limit bucket is keyed by, so a key replaced after startup makes the
    digests written before and after uncorrelatable — the same as not recording
    them. The whole login runs, because the client-IP digest lands on the
    transaction row and the user-agent digest lands on the session row, and the
    finding covers both.

    The substituted `app.state.address_policy` is attacked here too: it would
    answer `203.0.113.7` for every request, so the digest below is over the peer
    the request actually came from only if the **captured** policy resolved it.
    """
    app, original, _intruder, policy = under_replacement
    agent = "synthetic-user-agent/1.0"
    assert settings.client_digest_key.material != intruder_graph.client_digest_key.material

    async with await _client(app) as client:
        start = await client.get(
            "/v1/auth/discord/start", headers={"user-agent": agent}
        )
        transaction = next(
            header.split("=", 1)[1].split(";", 1)[0]
            for header in start.headers.get_list("set-cookie")
            if header.startswith(f"{settings.session.login_transaction_cookie_name}=")
        )
        state = original.authorization_calls[-1][0]
        completed = await client.get(
            "/auth/discord/callback",
            params={"state": state, "code": "the-code"},
            cookies={settings.session.login_transaction_cookie_name: transaction},
            headers={"user-agent": agent},
        )

    assert completed.status_code == 303, completed.headers.get("location")
    with migrated_database.connect() as connection:
        recorded_ip = connection.execute(
            select(oauth_transactions.c.client_ip_hash)
        ).scalars().all()
        recorded_agent = connection.execute(
            select(sessions.c.user_agent_digest)
        ).scalars().all()

    assert recorded_ip == [keyed_digest(settings.client_digest_key, "127.0.0.1")]
    assert recorded_ip != [
        keyed_digest(intruder_graph.client_digest_key, "127.0.0.1")
    ]
    assert recorded_ip != [keyed_digest(settings.client_digest_key, "203.0.113.7")]
    assert recorded_agent == [keyed_digest(settings.client_digest_key, agent)]
    assert recorded_agent != [keyed_digest(intruder_graph.client_digest_key, agent)]
    assert policy.calls == 0, "the substituted address policy was never consulted"


async def test_health_evaluation_still_receives_graph_a(
    under_replacement, settings, intruder_graph, monkeypatch
):
    """Required property 5, asserted by identity at the boundary `R-10` calls.

    The health view names check outcomes and no configured value, so what it
    *renders* cannot distinguish the two graphs. What can is which object it was
    handed, so that is what is asserted — `is`, not `==`, because two graphs that
    agree today are still two graphs.
    """
    app, *_ = under_replacement
    seen: list[object] = []
    real = app_module.build_health_view

    def spy(graph, engine, *, provider_ok):
        seen.append(graph)
        return real(graph, engine, provider_ok=provider_ok)

    monkeypatch.setattr(app_module, "build_health_view", spy)

    async with await _client(app) as client:
        response = await client.get("/healthz")

    assert response.status_code in (200, 503)
    assert len(seen) == 1
    assert seen[0] is settings or seen[0] == settings
    assert seen[0] is not intruder_graph
    assert seen[0].public_origin == settings.public_origin


async def test_the_provider_and_engine_remain_bound_to_the_original_composition(
    under_replacement, settings, migrated_database
):
    """Required property 6. The earlier provider/engine regression, still intact.

    `app.state.composition` now holds a **real** composition built from graph B
    with its own provider. If any route dereferenced it, the intruder would have
    answered R-03 and R-04. Both routes are driven and the startup provider is
    shown to be the object that answered, and the transaction the request wrote
    is read back off the engine the original composition serves from.
    """
    app, original, intruder, _policy = under_replacement

    async with await _client(app) as client:
        start = await client.get("/v1/auth/discord/start")
        assert start.status_code == 303
        transaction = next(
            header.split("=", 1)[1].split(";", 1)[0]
            for header in start.headers.get_list("set-cookie")
            if header.startswith(f"{settings.session.login_transaction_cookie_name}=")
        )
        state = original.authorization_calls[-1][0]
        await client.get(
            "/auth/discord/callback",
            params={"state": state, "code": "the-code"},
            cookies={settings.session.login_transaction_cookie_name: transaction},
        )

    assert original.authorization_calls, "R-03 used the provider built at startup"
    assert original.exchange_calls, "and R-04 exchanged through the same object"
    assert intruder.authorization_calls == []
    assert intruder.exchange_calls == []

    with migrated_database.connect() as connection:
        stored = connection.execute(select(oauth_transactions.c.id)).scalars().all()
    assert len(stored) == 1, "the request's transaction opened on the original engine"


async def test_the_rendering_environment_is_the_captured_one(
    under_replacement, settings
):
    """The fourth diagnostic reference, proved inert the same way as the others.

    `app.state.templates` is the Jinja environment whose `autoescape` is set once
    at construction (TC-SEC-08), so a per-request lookup would have made the
    escaping policy replaceable on every HTML response. The substituted
    environment renders a marker instead of the login page; the real page means
    the captured environment answered.
    """
    app, *_ = under_replacement

    async with await _client(app) as client:
        page = await client.get("/v1/login")
        error_page_env = app.state.templates

    assert page.status_code == 200
    assert "INTRUDER-TEMPLATE-MARKER" not in page.text
    assert "Discord" in page.text, "the real login view rendered"
    assert error_page_env.env.autoescape is False, (
        "the substitution really was installed, so the assertion above has teeth"
    )


# ---------------------------------------------------------------------------
# 2. The structural half: production request code reads no `app.state`
# ---------------------------------------------------------------------------
#
# The behaviour cases above are the proof. This is the guard that keeps them
# from silently becoming vacuous: a helper reintroduced next quarter that reads
# `request.app.state.settings` would restore the defect everywhere at once, and
# no single behavioural case is obliged to notice.

#: Where production code lives. `tests/` is deliberately absent: the suite reads
#: `app.state` constantly, and that is the point of keeping the references.
PRODUCTION_PACKAGES = ("adapters", "application", "domain", "helpers", "tools")

#: The one function allowed to touch `app.state`, and only to **write** it. Those
#: four assignments are what makes the references available for diagnostics and
#: test inspection at all.
DIAGNOSTIC_WRITER = "create_app"


class _AppStateAccesses(ast.NodeVisitor):
    """Every `<...>.app.state.<name>` access, with the function it appears in.

    Narrow in the dimensions that matter. It does not look at `request.state`,
    which is a genuine per-request namespace and a different thing; it does not
    look at attribute *writes* inside the factory, which are the diagnostic
    references themselves; and it does not look at `tests/`. What it reports is a
    production code path making a mutable application-level namespace answer a
    question — which is exactly the finding.
    """

    def __init__(self) -> None:
        self.functions: list[str] = []
        self.found: list[tuple[str, int, str, bool]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        self.functions.append(node.name)
        self.generic_visit(node)
        self.functions.pop()

    visit_AsyncFunctionDef = visit_FunctionDef  # noqa: N815 - the ast API's name

    def visit_Attribute(self, node: ast.Attribute) -> None:  # noqa: N802
        inner = node.value
        if isinstance(inner, ast.Attribute) and inner.attr == "state":
            root = ast.unparse(inner.value)
            if root == "app" or root.endswith(".app"):
                self.found.append(
                    (
                        self.functions[-1] if self.functions else "<module>",
                        node.lineno,
                        ast.unparse(node),
                        isinstance(node.ctx, ast.Store),
                    )
                )
        self.generic_visit(node)


def app_state_offenders(source: str, *, where: str) -> list[str]:
    """The accesses that are not a diagnostic write inside `create_app`."""
    visitor = _AppStateAccesses()
    visitor.visit(ast.parse(source))
    return [
        f"{where}:{line} {expression}"
        for function, line, expression, is_write in visitor.found
        if not (is_write and function == DIAGNOSTIC_WRITER)
    ]


def test_no_production_module_reads_app_state():
    """TC-STRUCT-10. The authority is what a handler captured, not what it looks up.

    Asserted over the AST rather than by a text search, so `app.state.settings`
    written across two lines, aliased through `request.app`, or mentioned in a
    docstring are each handled correctly rather than each producing a false
    result.
    """
    root = Path(__file__).resolve().parents[2]
    offenders: list[str] = []
    for package in PRODUCTION_PACKAGES:
        for path in sorted((root / package).rglob("*.py")):
            offenders.extend(
                app_state_offenders(
                    path.read_text(encoding="utf-8"),
                    where=str(path.relative_to(root)),
                )
            )
    assert offenders == [], offenders


def test_the_app_state_guard_reports_a_reintroduced_per_request_read():
    """The guard has teeth, and knows which side of the line each access is on.

    Without this, `test_no_production_module_reads_app_state` would pass just as
    happily against a detector that found nothing at all — which is the failure
    mode a structural regression is least likely to notice about itself.
    """
    reintroduced = (
        "def create_app(composition):\n"
        "    app = FastAPI()\n"
        "    app.state.settings = composition.settings\n"
        "    app.state.composition = composition\n"
        "    return app\n"
        "\n"
        "def _settings(request):\n"
        "    return request.app.state.settings\n"
    )
    offenders = app_state_offenders(reintroduced, where="synthetic.py")
    assert offenders == ["synthetic.py:8 request.app.state.settings"], offenders

    # The two diagnostic writes on their own are not a finding: keeping the
    # references is what the factory documents, and banning them would be a
    # guard nobody could satisfy without deleting the operator's view.
    writes_only = (
        "def create_app(composition):\n"
        "    app = FastAPI()\n"
        "    app.state.settings = composition.settings\n"
        "    return app\n"
    )
    assert app_state_offenders(writes_only, where="synthetic.py") == []

    # A *read* inside the factory is still a finding: the factory has the object
    # in a local, and reading it back out of state is how the round trip starts.
    read_in_factory = (
        "def create_app(composition):\n"
        "    app = FastAPI()\n"
        "    app.state.settings = composition.settings\n"
        "    _register(app, app.state.settings)\n"
        "    return app\n"
    )
    assert app_state_offenders(read_in_factory, where="synthetic.py") == [
        "synthetic.py:4 app.state.settings"
    ]


def test_the_factory_still_publishes_the_diagnostic_references():
    """The other half of "narrow": the operator's view is not what was removed.

    The correction is which object a *handler* holds. An application that stopped
    exposing its settings and composition entirely would satisfy the guard above
    and would have thrown away something useful to do it.
    """
    source = (Path(app_module.__file__)).read_text(encoding="utf-8")
    visitor = _AppStateAccesses()
    visitor.visit(ast.parse(source))
    written = {
        expression
        for function, _line, expression, is_write in visitor.found
        if is_write and function == DIAGNOSTIC_WRITER
    }
    assert written == {
        "app.state.settings",
        "app.state.composition",
        "app.state.templates",
        "app.state.address_policy",
    }, written


# ---------------------------------------------------------------------------
# 3. Finding 2: the ASGI lifecycle closes what the process actually used
# ---------------------------------------------------------------------------
#
# Every case below enters the application's lifespan through
# `tests/web/lifespan.py`, which drives the real protocol. That is the whole
# point of the finding: `WebComposition.aclose()` was correct and had no
# production caller, and the evidence offered for production cleanup was tests
# calling it by hand. A case that called it by hand here would repeat the
# mistake, so none of them does — §3's `aclose()` calls are all made *by the
# application*.


class TransportShutdownFailed(RuntimeError):
    """What a provider whose transport cannot be closed cleanly raises.

    A named type rather than a bare `RuntimeError`, so the failure-path case can
    assert that *this* is what surfaced rather than something the lifespan
    machinery produced on its own.
    """


class RecordingProvider:
    """A provider double that counts its closures and can refuse to close.

    It carries no Discord configuration, exactly as `FakeDiscordProvider` does
    not, so it is not a second authority — the only thing it is here to answer is
    "how many times were you closed, and by whom".
    """

    def __init__(self, *, fail: bool = False) -> None:
        self.closes = 0
        self.fail = fail

    async def aclose(self) -> None:
        self.closes += 1
        if self.fail:
            raise TransportShutdownFailed(
                "the provider transport did not shut down cleanly"
            )


class RecordingEngine:
    """Stands in for a SQLAlchemy engine where only disposal is observed."""

    def __init__(self) -> None:
        self.disposals = 0

    def dispose(self) -> None:
        self.disposals += 1


def _production_composition(settings, monkeypatch, *, provider):
    """A composition built the way production builds one, with both edges stubbed.

    `create_engine` and `build_provider` are the two module-level seams the
    composition root calls; replacing them is how a case observes an **owned**
    engine without opening a pool against PostgreSQL and without the harness,
    whose whole purpose is to lend an unowned one. Everything else — the
    canonicalisation, the ownership statement, `aclose()` — is production's.
    """
    engine = RecordingEngine()
    monkeypatch.setattr(
        composition_module, "create_engine", lambda *args, **kwargs: engine
    )
    monkeypatch.setattr(
        composition_module, "build_provider", lambda graph, **kwargs: provider
    )
    return WebComposition(settings=settings), engine


async def test_a_normal_shutdown_closes_the_provider_that_served_requests(
    settings, migrated_database
):
    """Required lifecycle property 1, through the lifespan and through a request.

    This is the integration case §3 is required to have: the application's
    lifespan is entered, R-03 is driven inside it and shown to have used the
    startup provider, and the same object is then shown to have been closed
    exactly once on the way out. Before this remediation the count was zero,
    because nothing called `aclose()` at all.
    """
    provider = FakeDiscordProvider(role_ids=frozenset())
    closes: list[int] = []

    async def counting_close() -> None:
        closes.append(1)

    provider.aclose = counting_close
    composition = substituted_composition(
        settings=settings, engine=migrated_database, provider=provider
    )
    app = create_app(composition=composition, run_startup_checks=False)

    async with application_lifespan(app) as messages:
        assert messages[-1]["type"] == "lifespan.startup.complete"
        assert closes == [], "nothing is closed while the application is serving"
        async with await _client(app) as client:
            started = await client.get("/v1/auth/discord/start")
        assert started.status_code == 303
        assert provider.authorization_calls, "the startup provider served R-03"

    assert messages[-1]["type"] == "lifespan.shutdown.complete"
    assert closes == [1], "and the same provider was closed exactly once"


async def test_a_normal_shutdown_disposes_a_production_owned_engine_once(
    settings, monkeypatch
):
    """Required lifecycle property 2, on the production construction path.

    Built through `WebComposition(settings=…)` with no harness in sight, so the
    engine is one this composition created and therefore owns. `run_startup_checks`
    is off because `RecordingEngine` is not a database; what is under test is
    disposal, not S-14.
    """
    provider = RecordingProvider()
    composition, engine = _production_composition(
        settings, monkeypatch, provider=provider
    )
    app = create_app(composition=composition, run_startup_checks=False)

    assert engine.disposals == 0
    async with application_lifespan(app):
        assert engine.disposals == 0, "not while the application is running"
    assert engine.disposals == 1
    assert provider.closes == 1


async def test_a_normal_shutdown_never_disposes_a_lent_engine(
    settings, provider, migrated_database
):
    """Required lifecycle property 3. The suite's shared fixture engine survives.

    `dispose()` is replaced on the instance rather than asserted around, because
    disposing a SQLAlchemy engine does not make it unusable — it silently
    replaces the pool, which is exactly the kind of damage a later test would
    report as something else entirely.
    """
    disposals: list[int] = []
    migrated_database.dispose = lambda *args, **kwargs: disposals.append(1)
    try:
        composition = substituted_composition(
            settings=settings, engine=migrated_database, provider=provider
        )
        app = create_app(composition=composition, run_startup_checks=False)
        assert composition._owns_engine is False  # noqa: SLF001 - beside the behaviour

        async with application_lifespan(app) as messages:
            pass

        assert messages[-1]["type"] == "lifespan.shutdown.complete"
        assert disposals == [], (
            "an engine the application did not build is not its to dispose"
        )
    finally:
        del migrated_database.dispose


async def test_replacing_the_state_composition_cannot_redirect_cleanup(
    settings, monkeypatch, tmp_path
):
    """Required lifecycle property 4. Shutdown resolves nothing from `app.state`.

    Two failure modes in one assertion set: an intruder composition installed
    before shutdown must not be cleaned up *instead* of the original, and the
    original must not be left open. A lifespan that looked the composition up
    would do both at once — and would report a clean stop while the real HTTP
    client and the real pool stayed open, which is the worst available outcome.
    """
    original_provider = RecordingProvider()
    composition, engine = _production_composition(
        settings, monkeypatch, provider=original_provider
    )
    app = create_app(composition=composition, run_startup_checks=False)

    intruder_provider = RecordingProvider()
    intruder, intruder_engine = _production_composition(
        settings, monkeypatch, provider=intruder_provider
    )

    async with application_lifespan(app):
        app.state.composition = intruder
        app.state.settings = foreign_graph(tmp_path)

    assert original_provider.closes == 1, "the original provider was closed"
    assert engine.disposals == 1, "and the original engine disposed"
    assert intruder_provider.closes == 0, "the intruder's were not touched"
    assert intruder_engine.disposals == 0


async def test_a_failing_provider_close_still_disposes_the_owned_engine(
    settings, monkeypatch
):
    """Required lifecycle property 5. `try/finally`, and a failure that surfaces.

    Three separate claims, because two of them are easy to satisfy by accident:

    1. the owned engine is disposed even though closing the provider raised —
       without the `finally`, one failure would become two, the second being a
       leaked SQLAlchemy pool;
    2. the failure is **not hidden**. Starlette answers a raising shutdown with
       `lifespan.shutdown.failed` and re-raises, so the exception reaches the
       caller — an ASGI stop that could not release its resources is not a clean
       stop, and reporting one would leave an operator with nothing to act on;
       and
    3. neither the exception nor the protocol message renders a configured
       secret. The `failed` message carries a formatted traceback, which is the
       one place in this path where source text is transmitted, so it is checked
       rather than assumed.
    """
    provider = RecordingProvider(fail=True)
    composition, engine = _production_composition(
        settings, monkeypatch, provider=provider
    )
    app = create_app(composition=composition, run_startup_checks=False)

    seen: list[dict] = []
    with pytest.raises(TransportShutdownFailed) as failure:
        async with application_lifespan(app) as messages:
            seen = messages

    assert provider.closes == 1
    assert engine.disposals == 1, "the finally ran despite the provider failing"
    assert seen[-1]["type"] == "lifespan.shutdown.failed"

    rendered = (str(failure.value), seen[-1]["message"])
    secrets = (
        settings.database.url,
        settings.discord.client_secret.material.decode("utf-8"),
        settings.csrf_key.material.decode("latin-1"),
        settings.client_digest_key.material.decode("latin-1"),
    )
    for text in rendered:
        for secret in secrets:
            assert secret not in text


async def test_the_stated_idempotency_rule_holds_under_a_repeated_shutdown(
    settings, monkeypatch
):
    """Required lifecycle property 6. Cleanup runs at most once, and says so.

    A completed application lifespan and a direct `aclose()` afterwards, against
    one composition, touch the resources exactly once in total. The rule is the
    composition's own guard, not HTTPX or SQLAlchemy tolerating a repeat:
    `Engine.dispose()` does not raise on a second call, it silently replaces the
    pool, so a tolerated double disposal is a defect that reports success.

    **A second lifespan is deliberately not one of the paths tried here**
    (2026-08-16, P3.G1 test-clock-authority re-review). This case used to enter
    one and require it to answer `lifespan.shutdown.complete`, which read as
    repeated-shutdown idempotency and was in fact a new *startup* after shutdown:
    the application reported that it had started, and would have served requests
    against a provider this composition had already closed. That is §3.1 below,
    and it now asserts the opposite outcome.
    """
    provider = RecordingProvider()
    composition, engine = _production_composition(
        settings, monkeypatch, provider=provider
    )
    app = create_app(composition=composition, run_startup_checks=False)

    async with application_lifespan(app) as messages:
        pass
    assert messages[-1]["type"] == "lifespan.shutdown.complete"
    assert (provider.closes, engine.disposals) == (1, 1)

    await composition.aclose()

    assert provider.closes == 1, "the provider was closed once in total"
    assert engine.disposals == 1, "and the engine disposed once in total"
    assert composition.lifecycle is CompositionLifecycle.CLOSED


async def test_an_overlapping_shutdown_cannot_close_anything_twice(
    settings, monkeypatch
):
    """The idempotency guard is set before the first `await`, so it holds for a race.

    A flag set *after* the cleanup would leave a window: two shutdown paths
    suspended inside `provider.aclose()` would both proceed. There is no
    suspension point between the test and the set, so the second caller returns
    immediately — asserted by running both concurrently rather than by reading
    the code.
    """
    provider = RecordingProvider()
    composition, engine = _production_composition(
        settings, monkeypatch, provider=provider
    )

    await asyncio.gather(composition.aclose(), composition.aclose())

    assert provider.closes == 1
    assert engine.disposals == 1


async def test_a_composition_cannot_be_relieved_of_its_cleanup_guard(
    settings, provider, migrated_database
):
    """The one mutable lifecycle attribute selects nothing and cannot be wound back.

    `_lifecycle` is not write-once, because it has to move. What it must not
    become is a lever, and there are two halves to that. It governs whether
    cleanup *runs* and whether a startup may be claimed, never which objects
    cleanup touches — those are still the write-once provider and engine. And it
    moves **forward only**: a spent composition cannot be reset to `NEW` and so
    cannot be re-claimed with its provider closed and its engine disposed, which
    is the state a caller reaching for this attribute would be trying to leave.
    """
    composition = substituted_composition(
        settings=settings, engine=migrated_database, provider=provider
    )
    app = create_app(composition=composition, run_startup_checks=False)

    async with application_lifespan(app):
        assert composition.lifecycle is CompositionLifecycle.STARTED
    assert composition.lifecycle is CompositionLifecycle.CLOSED

    with pytest.raises(SettingsAuthorityError, match="written once"):
        composition._provider = FakeDiscordProvider()  # noqa: SLF001
    with pytest.raises(SettingsAuthorityError, match="written once"):
        composition._engine = RecordingEngine()  # noqa: SLF001
    for state in (
        CompositionLifecycle.NEW,
        CompositionLifecycle.STARTED,
        CompositionLifecycle.CLOSING,
        CompositionLifecycle.CLOSED,
    ):
        with pytest.raises(CompositionLifecycleError, match="forward only"):
            composition._lifecycle = state  # noqa: SLF001
    assert composition.provider is provider
    assert composition.engine is migrated_database
    assert composition.lifecycle is CompositionLifecycle.CLOSED


# ---------------------------------------------------------------------------
# 3.1. A composition is claimed for one startup, and a lifetime is spent once
# ---------------------------------------------------------------------------
#
# The independent re-review of the P3.G1 test-clock-authority remediation
# (2026-08-16). `aclose()` permanently closes the provider and disposes an owned
# engine, and the lifespan performed no live-or-closed check on the way *in*. A
# composition passed to two applications — or one application whose lifespan was
# entered a second time — answered `lifespan.startup.complete` and began serving
# with a closed Discord HTTP client behind R-03 and R-04. The first failure was an
# OAuth request, not a startup.
#
# The resource checks were no defence and could not become one. They never look at
# the provider, and `Engine.dispose()` does not invalidate an engine — it silently
# replaces the pool, so S-14 and S-15 open fresh connections through the
# replacement and report a healthy database that nobody may use. The refusal is
# therefore a state transition on the way in, before any check runs.
#
# The suite previously *codified* the unsafe outcome: the repeated-shutdown case
# above entered a second lifespan over a closed composition and required it to
# answer `lifespan.startup.complete`. It no longer does, and the cases below
# assert the opposite.


async def test_a_second_application_cannot_start_on_a_closed_composition(
    settings, monkeypatch
):
    """The replacement for the removed two-application case, with the outcome fixed.

    One composition, two applications, entered in turn. The first runs a complete
    lifespan and releases the provider and the owned engine. The second must
    **fail** its ASGI startup: it never answers `lifespan.startup.complete`, so a
    server receiving the refusal stops rather than binding a socket, and there is
    no window in which a request could reach the closed provider.

    The cleanup counts are asserted after the refusal as well as before it. A
    refused startup on a composition somebody else already closed must release
    nothing — there is nothing left to release — and a second disposal would be
    invisible in `Engine.dispose()`'s own behaviour, which is why it is counted
    here rather than trusted.
    """
    provider = RecordingProvider()
    composition, engine = _production_composition(
        settings, monkeypatch, provider=provider
    )
    first = create_app(composition=composition, run_startup_checks=False)
    second = create_app(composition=composition, run_startup_checks=False)

    async with application_lifespan(first) as messages:
        pass
    assert messages[-1]["type"] == "lifespan.shutdown.complete"
    assert (provider.closes, engine.disposals) == (1, 1)
    assert composition.lifecycle is CompositionLifecycle.CLOSED

    refused = await refused_startup(second)

    assert isinstance(refused.failure, CompositionLifecycleError)
    assert refused.message_types == ("lifespan.startup.failed",)
    assert "lifespan.startup.complete" not in refused.message_types
    assert provider.closes == 1, "the closed provider was not closed again"
    assert engine.disposals == 1, "and the disposed engine not disposed again"


async def test_the_same_application_cannot_start_twice(settings, monkeypatch):
    """The other half of the finding: one application, two startups.

    A composition is spent by the lifespan that ran it, not by the object that
    installed it, so re-entering *the same* application's lifespan after a
    complete shutdown has to refuse for the same reason two applications do. It is
    its own case because a claim implemented on the `FastAPI` object rather than on
    the composition would pass the case above and fail this one.
    """
    provider = RecordingProvider()
    composition, engine = _production_composition(
        settings, monkeypatch, provider=provider
    )
    app = create_app(composition=composition, run_startup_checks=False)

    async with application_lifespan(app):
        pass

    refused = await refused_startup(app)

    assert isinstance(refused.failure, CompositionLifecycleError)
    assert "lifespan.startup.complete" not in refused.message_types
    assert (provider.closes, engine.disposals) == (1, 1)


async def test_a_second_startup_is_refused_while_the_first_is_still_serving(
    settings, migrated_database
):
    """The live case, and the one where a wrong correction would do real damage.

    The second application's startup is attempted *inside* the first's lifespan,
    while the first is serving requests. Two claims, and the second matters as much
    as the first: the refusal is reported, **and** nothing is cleaned up
    underneath the running application. A claim that refused by closing — or a
    lifespan that ran its cleanup on the way out of a failed claim — would take the
    provider and the engine away from an application in service, turning a caller's
    mistake into an outage.

    R-03 is driven after the refusal to show that in application behaviour rather
    than in a counter: the live provider still answers, on the same composition.
    """
    provider = FakeDiscordProvider(role_ids=frozenset())
    closes: list[int] = []

    async def counting_close() -> None:
        closes.append(1)

    provider.aclose = counting_close
    composition = substituted_composition(
        settings=settings, engine=migrated_database, provider=provider
    )
    first = create_app(composition=composition, run_startup_checks=False)
    second = create_app(composition=composition, run_startup_checks=False)

    async with application_lifespan(first) as messages:
        assert messages[-1]["type"] == "lifespan.startup.complete"

        refused = await refused_startup(second)

        assert isinstance(refused.failure, CompositionLifecycleError)
        assert "lifespan.startup.complete" not in refused.message_types
        assert closes == [], "the running application's provider was left alone"
        assert composition.lifecycle is CompositionLifecycle.STARTED

        async with await _client(first) as client:
            started = await client.get("/v1/auth/discord/start")
        assert started.status_code == 303, "the first application is still serving"
        assert provider.authorization_calls, "through the provider it started with"

    assert messages[-1]["type"] == "lifespan.shutdown.complete"
    assert closes == [1], "and the claimant closed it exactly once, on its own exit"


async def test_a_refused_claim_runs_no_resource_check(settings, monkeypatch):
    """The claim is before S-12/S-14/S-15, which is the only place it can be.

    The checks cannot detect this condition, so they must not be the thing that
    runs first. They never look at the provider at all, and `Engine.dispose()`
    replaces the pool rather than invalidating the engine — so a check run against
    a spent composition would open a fresh connection, pass, and report a portal
    fit to serve. Asserted by counting the calls: zero after a refused claim, and
    exactly one for the startup that was allowed.
    """
    seen: list = []
    _pass_resource_checks(monkeypatch, seen=seen)
    provider = RecordingProvider()
    composition, _engine = _production_composition(
        settings, monkeypatch, provider=provider
    )
    first = create_app(composition=composition)
    second = create_app(composition=composition)

    async with application_lifespan(first):
        pass
    assert len(seen) == 1, "the allowed startup ran the checks once"

    refused = await refused_startup(second)

    assert isinstance(refused.failure, CompositionLifecycleError)
    assert len(seen) == 1, "and the refused one ran none: the claim came first"


async def test_a_refused_claim_names_no_configured_value(settings, monkeypatch):
    """A lifecycle refusal is a refusal, so it carries no secret either.

    It reaches the same three channels every startup refusal does — the surfaced
    exception, its chained context, and the `lifespan.startup.failed` message with
    the formatted traceback the specification has the application put in it — so
    it is read and checked exactly as `ConfigurationError` is.
    """
    provider = RecordingProvider()
    composition, _engine = _production_composition(
        settings, monkeypatch, provider=provider
    )
    first = create_app(composition=composition, run_startup_checks=False)
    second = create_app(composition=composition, run_startup_checks=False)

    async with application_lifespan(first):
        pass
    refused = await refused_startup(second)

    chained: list[str] = []
    seen_ids: set[int] = set()
    current: BaseException | None = refused.failure
    while current is not None and id(current) not in seen_ids:
        seen_ids.add(id(current))
        chained.append(f"{type(current).__name__}: {current}")
        current = current.__context__ or current.__cause__

    rendered = (*chained, str(refused.messages[-1].get("message", "")))
    for text in rendered:
        for secret in _secret_material(settings):
            assert secret not in text


async def test_a_composition_discarded_without_starting_still_closes(
    settings, monkeypatch
):
    """`NEW -> CLOSING -> CLOSED`. A composition may be released before it serves.

    The state machine must not require a claim before cleanup: `create_app()` can
    raise, a caller can change its mind, and the constructor's own partial-failure
    path builds nothing that would ever be claimed. Closing an unclaimed
    composition is the honest release of resources it really is holding, and it
    still spends the lifetime — a startup afterwards is refused like any other.
    """
    provider = RecordingProvider()
    composition, engine = _production_composition(
        settings, monkeypatch, provider=provider
    )
    assert composition.lifecycle is CompositionLifecycle.NEW

    await composition.aclose()

    assert (provider.closes, engine.disposals) == (1, 1)
    assert composition.lifecycle is CompositionLifecycle.CLOSED

    app = create_app(composition=composition, run_startup_checks=False)
    refused = await refused_startup(app)

    assert isinstance(refused.failure, CompositionLifecycleError)
    assert (provider.closes, engine.disposals) == (1, 1)


# ---------------------------------------------------------------------------
# 4. The remaining finding: a refused startup releases what it is already holding
# ---------------------------------------------------------------------------
#
# `create_app()` used to construct or accept the composition, call
# `run_resource_checks()`, and only afterwards build the `FastAPI` object the
# lifespan above is installed on. On the production construction path both
# process-lifetime resources — the provider's HTTP client and the owned
# SQLAlchemy engine and its pool — already existed when that call ran. A refusal
# propagated out of the factory, so no application was returned, so no lifespan
# could execute, so `aclose()` had no caller on the one path where the process
# was being told not to run. §3 proved cleanup on a normal shutdown; the failed
# startup was the half still missing, and it is the half an operator meets first.
#
# The checks now run inside the lifespan, before `lifespan.startup.complete`,
# under the same `aclose()` guarantee that owns the exact accepted composition.


#: A refusal that names a variable and no value, exactly as S-14 does. Built here
#: rather than provoked from a real broken database, because what is under test
#: is where the check runs and what happens when it refuses, not the check.
S14_PROBLEM = ConfigurationProblem(
    message=(
        "could not be queried for its Alembic revision. A process that cannot "
        "establish which schema it is serving must not serve one."
    ),
    variables=("WEB_DATABASE_URL",),
    refusal="S-14",
)


def _refuse_resource_checks(monkeypatch, *, seen: list | None = None):
    """Make S-14 refuse, and optionally record what the checks were handed.

    `adapters.web.app` is patched rather than `application.web.startup`, because
    the question is which object *the lifespan* calls with which arguments.
    """

    def refuse(graph, engine):
        if seen is not None:
            seen.append((graph, engine))
        raise ConfigurationError([S14_PROBLEM])

    monkeypatch.setattr(app_module, "run_resource_checks", refuse)


def _pass_resource_checks(monkeypatch, *, seen: list, warnings: tuple = ()):
    def pass_checks(graph, engine):
        seen.append((graph, engine))
        return warnings

    monkeypatch.setattr(app_module, "run_resource_checks", pass_checks)


def _secret_material(settings) -> tuple[str, ...]:
    """Every configured value that must never appear in a refusal or a log."""
    return (
        settings.database.url,
        settings.discord.client_secret.material.decode("utf-8"),
        settings.csrf_key.material.decode("latin-1"),
        settings.client_digest_key.material.decode("latin-1"),
    )


async def test_a_refused_resource_check_fails_asgi_startup_with_the_original_error(
    settings, monkeypatch
):
    """Required property 1. The refusal is an ASGI startup failure, unchanged.

    Two claims. The application answers `lifespan.startup.failed` and never
    `lifespan.startup.complete`, which is what makes a refusal visible to the
    server rather than to whoever happened to call the factory; and what surfaces
    is the **original** typed `ConfigurationError`, carrying the same `S-14` it
    was raised with. A path that wrapped it, replaced it, or reported a generic
    startup fault would leave an operator without the refusal they must act on.
    """
    _refuse_resource_checks(monkeypatch)
    composition, _engine = _production_composition(
        settings, monkeypatch, provider=RecordingProvider()
    )
    app = create_app(composition=composition)

    refused = await refused_startup(app)

    assert isinstance(refused.failure, ConfigurationError)
    assert refused.failure.refusals() == ("S-14",)
    assert refused.message_types == ("lifespan.startup.failed",)
    assert "lifespan.startup.complete" not in refused.message_types


async def test_a_refused_startup_closes_the_provider_exactly_once(
    settings, monkeypatch
):
    """Required property 2. The provider the accepted composition holds is closed.

    Before the correction this count was zero: the provider had been constructed
    by `WebComposition.__init__` and its `httpx.AsyncClient` was open, and the
    factory raised past every line that could have closed it.

    "Exactly once" matters as much as "at least once" — `aclose()`'s guard is
    what a repeated or overlapping shutdown relies on, and a refused startup that
    closed twice would be evidence the guard had been bypassed on this path.
    """
    _refuse_resource_checks(monkeypatch)
    provider = RecordingProvider()
    composition, _engine = _production_composition(
        settings, monkeypatch, provider=provider
    )
    app = create_app(composition=composition)

    assert provider.closes == 0, "the factory returned without closing anything"
    refused = await refused_startup(app)

    assert isinstance(refused.failure, ConfigurationError)
    assert provider.closes == 1


async def test_a_refused_startup_disposes_a_production_owned_engine_exactly_once(
    settings, monkeypatch
):
    """Required property 3, on the production construction path.

    Built through `WebComposition(settings=…)`, so the engine is one this
    composition created and therefore owns — the case the finding is about. A
    leaked SQLAlchemy pool on a host co-located with three Foundry instances, the
    live bot and PostgreSQL is not a cosmetic loss (N-53).
    """
    _refuse_resource_checks(monkeypatch)
    composition, engine = _production_composition(
        settings, monkeypatch, provider=RecordingProvider()
    )
    app = create_app(composition=composition)

    assert engine.disposals == 0
    refused = await refused_startup(app)

    assert isinstance(refused.failure, ConfigurationError)
    assert engine.disposals == 1


async def test_a_refused_startup_never_disposes_a_lent_engine(
    settings, provider, migrated_database, monkeypatch
):
    """Required property 4. Ownership does not change because startup refused.

    The suite's session-scoped `migrated_database` is lent to hundreds of
    compositions in turn. An application that disposed it on the way out of a
    refused startup would empty a pool the next test is still holding connections
    from — and `Engine.dispose()` does not raise, it silently replaces the pool,
    so the damage would surface somewhere else entirely.
    """
    _refuse_resource_checks(monkeypatch)
    disposals: list[int] = []
    migrated_database.dispose = lambda *args, **kwargs: disposals.append(1)
    try:
        composition = substituted_composition(
            settings=settings, engine=migrated_database, provider=provider
        )
        app = create_app(composition=composition)
        assert composition._owns_engine is False  # noqa: SLF001 - beside the behaviour

        refused = await refused_startup(app)

        assert isinstance(refused.failure, ConfigurationError)
        assert disposals == [], (
            "an engine the application did not build is not its to dispose, "
            "whatever the reason it is stopping"
        )
    finally:
        del migrated_database.dispose


async def test_no_request_is_served_after_a_refused_startup(settings, monkeypatch):
    """Required property 5. There is no window between the check and serving.

    The checks complete before `lifespan.startup.complete` is sent, so a server
    that receives the refusal stops instead of binding a socket. At this layer
    that is asserted where requests actually belong: `application_lifespan`'s body
    runs between startup and shutdown, and on a refusal the context manager raises
    without ever entering it.
    """
    _refuse_resource_checks(monkeypatch)
    composition, _engine = _production_composition(
        settings, monkeypatch, provider=RecordingProvider()
    )
    app = create_app(composition=composition)

    served: list[int] = []
    with pytest.raises(ConfigurationError):
        async with application_lifespan(app):
            served.append(1)

    assert served == [], "the application never reached the point of serving"


async def test_replacing_the_state_references_cannot_redirect_checks_or_cleanup(
    settings, monkeypatch, migrated_database, tmp_path
):
    """Required property 6. Neither half resolves anything through `app.state`.

    All four diagnostic references are replaced with graph B's before the lifespan
    is entered — the same attack §1 makes on the request path, aimed at startup.
    Three claims follow: the checks were handed the graph and the engine the
    factory accepted, by identity; the original provider and engine were released;
    and the intruder's were not touched. A lifespan that looked either up would
    fail all three at once, and would report a refusal while the real client and
    the real pool stayed open.
    """
    seen: list = []
    _refuse_resource_checks(monkeypatch, seen=seen)
    original_provider = RecordingProvider()
    composition, engine = _production_composition(
        settings, monkeypatch, provider=original_provider
    )
    app = create_app(composition=composition)

    intruder_provider = RecordingProvider()
    intruder, intruder_engine = _production_composition(
        settings, monkeypatch, provider=intruder_provider
    )
    _install_graph_b(
        app,
        graph=foreign_graph(tmp_path),
        composition=intruder,
        tmp_path=tmp_path,
    )

    refused = await refused_startup(app)

    assert isinstance(refused.failure, ConfigurationError)
    assert len(seen) == 1
    checked_graph, checked_engine = seen[0]
    assert checked_graph is composition.settings, "the accepted graph, not B's"
    assert checked_engine is engine, "and the engine every request would transact on"
    assert original_provider.closes == 1
    assert engine.disposals == 1
    assert intruder_provider.closes == 0, "the intruder's were not touched"
    assert intruder_engine.disposals == 0


async def test_a_refused_startup_transmits_no_secret_anywhere(
    settings, monkeypatch, caplog
):
    """Required property 7, over all three channels a refusal can reach.

    `ConfigurationError` names variables and never values by construction, but
    "by construction" is what the two findings before this one were also said to
    be. So the surfaced exception, its whole chained context, the ASGI
    `lifespan.startup.failed` message — which carries a formatted traceback, the
    one place on this path where source text crosses a protocol boundary — and
    everything logged while the refusal unwound are each read and checked.
    """
    caplog.set_level(logging.DEBUG)
    _refuse_resource_checks(monkeypatch)
    composition, _engine = _production_composition(
        settings, monkeypatch, provider=RecordingProvider()
    )
    app = create_app(composition=composition)

    refused = await refused_startup(app)

    chained: list[str] = []
    seen_ids: set[int] = set()
    current: BaseException | None = refused.failure
    while current is not None and id(current) not in seen_ids:
        seen_ids.add(id(current))
        chained.append(f"{type(current).__name__}: {current}")
        current = current.__context__ or current.__cause__

    rendered = (
        *chained,
        str(refused.messages[-1].get("message", "")),
        caplog.text,
    )
    for text in rendered:
        for secret in _secret_material(settings):
            assert secret not in text


async def test_a_failing_provider_close_does_not_replace_the_startup_refusal(
    settings, monkeypatch
):
    """The documented rule when both halves fail, asserted rather than described.

    Python's default would surface the wrong exception: one raised while another
    is being handled replaces it. A provider whose transport failed to shut down
    would then hide the `ConfigurationError` that refused the boot, leaving an
    operator with a transport fault and no idea the configuration was wrong.

    So the refusal stays at the head and the cleanup failure is attached beneath
    it. Both are reachable from one traceback and neither is dropped — and the
    owned engine is still disposed, because `aclose()`'s own `finally` does not
    care why it was called.
    """
    _refuse_resource_checks(monkeypatch)
    provider = RecordingProvider(fail=True)
    composition, engine = _production_composition(
        settings, monkeypatch, provider=provider
    )
    app = create_app(composition=composition)

    refused = await refused_startup(app)

    assert isinstance(refused.failure, ConfigurationError), (
        "the refusal is what an operator must act on, so it stays at the head"
    )
    assert refused.failure.refusals() == ("S-14",)
    assert provider.closes == 1
    assert engine.disposals == 1, "the finally ran despite the provider failing"

    attached: list[BaseException] = []
    seen_ids: set[int] = set()
    current: BaseException | None = refused.failure.__context__
    while current is not None and id(current) not in seen_ids:
        seen_ids.add(id(current))
        attached.append(current)
        current = current.__context__
    assert any(isinstance(error, TransportShutdownFailed) for error in attached), (
        "and the cleanup failure is not silently dropped"
    )


async def test_a_completed_startup_still_records_its_warnings_from_the_accepted_graph(
    settings, monkeypatch
):
    """The success path is unchanged, and still runs against the accepted objects.

    `startup_warnings` is S-15's development-host output and the reason
    `run_resource_checks` returns anything at all. Moving the call must not turn
    it into a value nobody stores, and the arguments it is called with must be the
    graph and the engine the application serves from — asserted by identity, since
    two objects that agree today are still two objects.
    """
    seen: list = []
    warnings = (StartupWarning(refusal="S-15", message="synthetic"),)
    _pass_resource_checks(monkeypatch, seen=seen, warnings=warnings)
    provider = RecordingProvider()
    composition, engine = _production_composition(
        settings, monkeypatch, provider=provider
    )
    app = create_app(composition=composition)

    assert seen == [], "nothing ran at factory time"
    assert composition.startup_warnings == ()

    async with application_lifespan(app) as messages:
        assert messages[-1]["type"] == "lifespan.startup.complete"
        assert composition.startup_warnings == warnings

    assert messages[-1]["type"] == "lifespan.shutdown.complete"
    assert len(seen) == 1
    assert seen[0][0] is composition.settings
    assert seen[0][1] is engine
    assert provider.closes == 1


async def test_the_factory_no_longer_decides_whether_the_portal_may_start(
    settings, monkeypatch
):
    """The structural half: `create_app()` returning is not a passed check.

    This is the regression that fails if the call is moved back in front of the
    `FastAPI` construction, whatever else stays correct. It is stated as its own
    case because every behavioural case above would still pass against a factory
    that ran the checks *twice* — once where they leak and once where they do not.
    """
    calls: list[int] = []

    def refuse(graph, engine):
        calls.append(1)
        raise ConfigurationError([S14_PROBLEM])

    monkeypatch.setattr(app_module, "run_resource_checks", refuse)
    composition, engine = _production_composition(
        settings, monkeypatch, provider=RecordingProvider()
    )

    app = create_app(composition=composition)

    assert calls == [], "the factory ran no resource check"
    assert engine.disposals == 0, "and disposed nothing, because nothing refused yet"

    refused = await refused_startup(app)

    assert isinstance(refused.failure, ConfigurationError)
    assert calls == [1], "the checks ran exactly once, inside the lifespan"


# ---------------------------------------------------------------------------
# 5. Partial construction: a constructor that fails after building an engine
# ---------------------------------------------------------------------------
#
# The lifespan can only release what a *complete* composition holds. If
# `WebComposition.__init__` builds an owned engine and a later step raises, no
# composition exists for a caller or a lifespan to hold, and the engine has no
# reference anywhere. `Engine.dispose()` is synchronous, so the constructor can
# and now does release it before re-raising.


class ProviderConstructionFailed(RuntimeError):
    """What a provider that cannot be built raises, named so a case can assert it."""


async def test_a_constructor_that_fails_after_building_an_engine_disposes_it(
    settings, monkeypatch
):
    """The owned engine is released on a partial construction, not leaked.

    `build_provider` is the last step `__init__` takes and the one that constructs
    a real `httpx.AsyncClient` in production, so it is where a late refusal is
    reachable. Before the correction the engine built two statements earlier stayed
    open with nothing referring to it.
    """
    engine = RecordingEngine()
    monkeypatch.setattr(
        composition_module, "create_engine", lambda *args, **kwargs: engine
    )

    def refuse(graph, **kwargs):
        raise ProviderConstructionFailed("the provider could not be built")

    monkeypatch.setattr(composition_module, "build_provider", refuse)

    with pytest.raises(ProviderConstructionFailed):
        WebComposition(settings=settings)

    assert engine.disposals == 1, "the engine this constructor built was released"


async def test_a_constructor_that_fails_never_disposes_a_lent_engine(
    settings, provider, migrated_database
):
    """Ownership governs the constructor's cleanup exactly as it governs `aclose()`.

    `SubstitutedComposition` refuses a substituted provider beside a transport for
    the real one, which is a genuine reachable failure *after* the lent engine has
    been recorded. Disposing it would reach into the suite's shared fixture.
    """
    disposals: list[int] = []
    migrated_database.dispose = lambda *args, **kwargs: disposals.append(1)
    try:
        async with httpx.AsyncClient() as transport:
            with pytest.raises(TypeError, match="one or the other"):
                substituted_composition(
                    settings=settings,
                    engine=migrated_database,
                    provider=provider,
                    provider_client=transport,
                )
        assert disposals == []
    finally:
        del migrated_database.dispose
