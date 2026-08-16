"""The portal suite's **one** way to build a composition it controls.

Production construction is `WebComposition(settings=…)` and nothing else: it
derives the engine from `settings.database` and the identity provider from
`settings.discord`, and holds both write-once. That is the point of the P3.G1
provider/engine authority remediation, and it leaves the suite needing two things
production must never offer — a fake provider that answers from a script, and the
session-scoped disposable-PostgreSQL engine `tests/conftest.py` guards.

Both arrive here, through `substituted_composition()`, and nowhere else.

**Why this is not a supported production authority seam.** Reaching it requires
writing a `WebComposition` subclass that overrides two protected methods. There
is no parameter, no keyword, no environment flag and no registry that selects it:
`WebComposition.__init__` and `create_app()` expose nothing an ordinary caller
could pass a provider or an engine through, so a production process cannot arrive
here by mistake, by copy-paste, or by a caller renaming an argument. The subclass
below is in `tests/`, is imported by test modules only, and is never referenced
from `adapters/`, `application/`, `domain/` or `tools/` — `TC-STRUCT-09` asserts
that last part rather than leaving it to review.

**The engine is still guarded.** `require_disposable_engine()` re-runs the two
layers `tests/conftest.py` documents — the static identity check on the URL the
engine dials, and the live "which database did this connection land in, and is it
a Unix-domain socket?" question — against the engine actually handed over. The
reasoning is not re-implemented: these are the same two functions the session
fixture calls. What is added is that they are asked about *this* engine, because
a composition that could be given any engine at all is the defect being fixed.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from sqlalchemy import Engine

from adapters.database.config import EXPECTED_DATABASES
from adapters.database.safety import (
    ConnectionPolicy,
    assert_disposable_target,
    verify_connected_unix_socket_target,
)
from adapters.web.composition import EngineHandle, WebComposition
from application.web.config import WebSettings
from application.web.providers import IdentityProvider

if TYPE_CHECKING:  # pragma: no cover - typing only
    import httpx

#: The same name `tests/conftest.py` resolves `TEST_DATABASE_URL` against.
EXPECTED_TEST_DATABASE = EXPECTED_DATABASES["test"]


def require_disposable_engine(engine: Engine) -> Engine:
    """The suite's safety contract, asked about **this** engine.

    Layer 1 resolves what the engine would dial — including the ambient libpq
    environment — into a normalised identity and refuses anything that is not the
    local disposable database, or that resolves to the same database as
    `DATABASE_URL`. Layer 2 asks the server where a real connection landed and
    requires a Unix-domain socket, which is the only one of the two that can see
    a remapped host or a forwarded port.

    Neither is re-implemented here; both are the functions `tests/conftest.py`
    already uses, so there is one copy of the reasoning and one place for it to
    be wrong. Raises `UnsafeDatabaseTargetError`, which the suite treats as a
    failure rather than a skip.
    """
    # Rendered with the password hidden: the identity this guard resolves is the
    # backend, host, port and database name, and none of those is the password.
    # Passing it would put key material into whatever a refusal or a test failure
    # renders, for no gain.
    assert_disposable_target(
        engine.url.render_as_string(hide_password=True),
        expected_database=EXPECTED_TEST_DATABASE,
        runtime_url=os.environ.get("DATABASE_URL"),
        variable="the engine lent to substituted_composition()",
        policy=ConnectionPolicy.UNIX_SOCKET_ONLY,
    )
    with engine.connect() as connection:
        verify_connected_unix_socket_target(
            connection, expected_database=EXPECTED_TEST_DATABASE
        )
    return engine


class SubstitutedComposition(WebComposition):
    """A production composition whose two infrastructure hooks are overridden.

    Everything else is production's: the settings graph is canonicalised by
    `WebComposition.__init__`, the services, repositories, envelope and lifecycle
    are the production ones, and the provider — whichever one it is — still goes
    through the composition's own "no second Discord authority" requirement. So a
    test exercises the real composition root, not a re-implementation of it.

    Named rather than private because a case that needs one more deviation — a
    subclass answering `settings` with a second graph, to show what `create_app`
    still requires — should extend this one and keep the engine guard, rather
    than write a second composition subclass beside it.
    """

    __slots__ = ("_lent_engine", "_substitute_provider")

    def __init__(
        self,
        *,
        settings: WebSettings,
        engine: Engine,
        provider: IdentityProvider | None,
        provider_client: "httpx.AsyncClient | None",
    ) -> None:
        self._lent_engine = require_disposable_engine(engine)
        self._substitute_provider = provider
        super().__init__(settings=settings, provider_client=provider_client)

    def _build_engine(self) -> EngineHandle:
        """The lent engine, explicitly **unowned**.

        The suite's `migrated_database` fixture is session-scoped and shared by
        hundreds of tests. An application that disposed it would empty a pool the
        next test is still holding connections from, so ownership is stated here
        rather than inferred from "an engine was supplied", which is what the
        removed `engine=` parameter did.
        """
        return EngineHandle(self._lent_engine, owned=False)

    def _build_provider(
        self, client: "httpx.AsyncClient | None"
    ) -> IdentityProvider:
        """The suite's fake, or the real adapter over a supplied transport.

        With no `provider`, this falls through to production's implementation —
        which is how the cases about the *real* `DiscordIdentityProvider` and its
        canonical configuration are written, over `httpx.MockTransport` rather
        than a socket.
        """
        if self._substitute_provider is None:
            return super()._build_provider(client)
        if client is not None:
            raise TypeError(
                "provider_client configures the Discord adapter production "
                "builds; it is meaningless beside a substituted provider that "
                "replaces that adapter entirely. Pass one or the other."
            )
        return self._substitute_provider


def substituted_composition(
    *,
    settings: WebSettings,
    engine: Engine,
    provider: IdentityProvider | None = None,
    provider_client: "httpx.AsyncClient | None" = None,
) -> WebComposition:
    """A composition with a lent engine and, optionally, a substituted provider.

    The name says what it is at every call site: this is not how the portal is
    built in production, and a reader who sees it in `adapters/` or `tools/`
    should treat that as a defect rather than a style question.

    `provider=None` keeps production's Discord adapter, built by the composition
    from its own canonical `settings.discord`; `provider_client` then supplies
    that adapter's transport and nothing else.
    """
    return SubstitutedComposition(
        settings=settings,
        engine=engine,
        provider=provider,
        provider_client=provider_client,
    )


__all__ = [
    "EXPECTED_TEST_DATABASE",
    "SubstitutedComposition",
    "require_disposable_engine",
    "substituted_composition",
]
