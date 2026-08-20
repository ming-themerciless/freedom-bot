"""The composition root: one place where the portal's objects are wired together.

Everything the application layer needs is constructed here and injected, so no
service reaches for a global, reads an environment variable, or opens its own
transaction. That is what makes the services testable against fakes and what
makes the transaction rule — a state change and its audit event share one
transaction — expressible at all.

**One engine, bounded** (N-53). `pool_size=5`, `max_overflow=5`, a five-second
pool timeout and a ten-second `statement_timeout`, because this process is
co-located with three Foundry instances, the live bot and PostgreSQL. A web
request that needs more than ten seconds of SQL is a defect, and letting it hold
a connection while it proves that is an availability problem for everything else
on the host.

**What a production caller may supply is one settings graph, and nothing else**
(2026-08-16, P3.G1 provider/engine authority remediation). `WebComposition`
derives the engine *and* the identity provider from that graph, holds both in
private write-once slots, and exposes them through read-only properties. There is
no `engine=` parameter, no `provider=` parameter and no `provider_double=`
parameter, so "the provider every OAuth request uses and the engine every request
uses come from the canonical graph" is a property of the construction path rather
than of a startup comparison that a later assignment could invalidate.

**A composition serves exactly one application lifespan, once** (2026-08-16,
P3.G1 test-clock-authority re-review). `CompositionLifecycle` below is that rule:
`new -> started -> closing -> closed`, one way, with `claim_for_startup()` as the
only transition out of `new`. It exists because `aclose()` permanently closes the
provider and disposes an owned engine, and nothing previously stopped a second
ASGI startup over the same object from reporting success and serving requests
against a closed HTTP client — a `dispose()`d SQLAlchemy engine silently builds a
replacement pool, so even a passing S-14 would not have noticed.

Substitution for tests goes through `_build_engine` and `_build_provider`, two
protected hooks whose only overrides live in `tests/web/composition_harness.py`.
Overriding a protected method is not something a production caller does by
passing an argument: it requires writing a subclass, which is why the seam is
structurally — and visually — distinct from the supported construction path.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import Engine, create_engine

from adapters.web.repositories import (
    AccountRepository,
    AuditSearchRepository,
    CharacterAccessRepository,
    IdentityCandidateRepository,
    IdentityProposalRepository,
    MembershipProjectionRepository,
    OAuthTransactionRepository,
    RateLimitRepository,
    ReconciliationJobRepository,
    RecoveryGrantRepository,
    RoleMappingRepository,
    SessionRepository,
    SnapshotReadRepository,
    TokenGrantRepository,
    WebAuditRepository,
    WebAuthnRepository,
)
from application.web.account_identities import AccountIdentityService
from application.web.audit_search import AuditSearchService
from application.web.breakglass import BreakGlassService
from application.web.character_access import CharacterAccessService
from application.web.characters import CharacterQueryService
from application.web.identity_evidence import IdentityMigrationService
from application.web.jobs import ReconciliationJobService
from application.web.snapshot_admin import ImportReceiptService, SnapshotAdminService
from application.web.config import (
    DatabasePoolSettings,
    DiscordProviderSettings,
    SettingsAuthorityError,
    WebSettings,
    canonical_settings,
    canonical_web_settings,
)
from application.web.crypto import Envelope
from application.web.oauth import OAuthLoginService
from application.web.providers import IdentityProvider
from application.web.rate_limit import RateLimiter
from application.web.role_mappings import RoleMappingService
from application.web.sessions import SessionService
from domain.foundry_profile import PROFILE as FIELD_PROFILE

if TYPE_CHECKING:  # pragma: no cover - typing only
    import httpx

TEMPLATE_ROOT = Path(__file__).resolve().parent / "templates"

#: The **one** directory the application serves static assets from (M-01, route
#: contract §1.2). Repository-owned and inside this package, deliberately: the
#: static root is not configurable, so there is no environment variable an
#: operator can point at `/etc` or at an artifact directory, and "outside the
#: approved root" is a question with one answer rather than one per deployment.
#:
#: It exists in the tree because `StaticFiles(check_dir=True)` refuses to
#: construct against a missing directory, and refusing loudly at construction is
#: the behaviour worth keeping — the alternative, `check_dir=False`, turns a
#: mis-deployed application into one that answers `404` to every asset and starts
#: normally. Git does not track an empty directory, so the directory holds one
#: empty `.gitkeep` and nothing else. That file is the smallest non-visual
#: placeholder that makes the root real; it is not an asset, and P3.4 owns
#: everything that will actually live here.
STATIC_ROOT = Path(__file__).resolve().parent / "static"


def build_engine(settings: WebSettings) -> Engine:
    """N-53's pool, from four numbers read once and validated before they are used.

    `canonical_settings` is what makes "validated" mean the values *these* four
    arguments carry (2026-08-15, I-10). `settings.database_pool` may be a
    subclass whose attributes answer differently on a second read, so reading it
    into an ordinary `DatabasePoolSettings` first — one read per field, checked
    by that constructor — is what stops an out-of-register pool size or
    statement timeout reaching SQLAlchemy at all.
    """
    pool = canonical_settings(settings.database_pool, DatabasePoolSettings)
    return create_engine(
        settings.database.url,
        pool_size=pool.pool_size,
        max_overflow=pool.max_overflow,
        pool_timeout=pool.pool_timeout_seconds,
        pool_pre_ping=True,
        connect_args={
            # Bounded at the server, not only in the client's intention: a query
            # that outlives this is cancelled by PostgreSQL whatever the
            # application is doing.
            "options": f"-c statement_timeout={pool.statement_timeout_ms}"
        },
    )


def build_provider(
    settings: DiscordProviderSettings, *, client: "httpx.AsyncClient | None" = None
) -> IdentityProvider:
    """The one production construction of the Discord adapter.

    It takes the **provider settings**, never a `WebSettings` graph and never a
    ready-made provider: the only object a caller can influence here is the HTTP
    transport, and `DiscordIdentityProvider` takes the timeout and the
    no-redirect rule from the settings above rather than from that transport
    (2026-08-16, P3.G1 canonical-graph re-review, finding 1).

    A module-level function for the same reason `build_engine` is one: it is the
    seam a test monkeypatches to prove that a refusal happened *before* a
    provider was built, and a method on the composition would make that
    assertion a statement about a half-constructed object.
    """
    from adapters.web.discord_provider import DiscordIdentityProvider

    return DiscordIdentityProvider(settings, client=client)


class CompositionLifecycle(Enum):
    """Where a composition is between "built" and "its resources are gone".

    The member values are the **order** and carry no other meaning: the state
    machine is one-way, so `__setattr__` compares them to refuse any move that is
    not forward. Writing that as four integers keeps the rule to one comparison
    rather than a table of permitted pairs that a fifth state would have to be
    remembered in.

    * `NEW` — constructed. Nothing has claimed it and nothing is closed. The only
      state `claim_for_startup()` accepts.
    * `STARTED` — one ASGI lifespan has claimed it and is responsible for closing
      it. Requests may be served against the provider and the engine.
    * `CLOSING` — `aclose()` has begun and has not finished. Reachable from `NEW`
      as well as from `STARTED`, because a composition can be discarded before it
      ever serves.
    * `CLOSED` — cleanup has run. The provider's HTTP client is closed and an
      owned engine is disposed, permanently.

    `CLOSING` and `CLOSED` answer every guard identically — both refuse a claim
    and both make `aclose()` a no-op — and are still distinct, because a stalled
    or failed shutdown is a different thing for an operator to read than a
    finished one, and collapsing them would make `aclose()` report a completion it
    had not reached.
    """

    NEW = 0
    STARTED = 1
    CLOSING = 2
    CLOSED = 3


class CompositionLifecycleError(RuntimeError):
    """A composition was asked to do something its lifecycle no longer permits.

    A `RuntimeError` rather than a `SettingsAuthorityError`, because nothing is
    wrong with the configuration: the graph, the provider and the engine are the
    ones this process validated. What is wrong is *when* — a second application
    tried to start on a composition that is already serving one, or on one whose
    resources have been released. Like every refusal raised at this boundary it
    names no configured value.
    """


@dataclass(frozen=True, slots=True)
class EngineHandle:
    """The engine that serves requests, and who is responsible for disposing it.

    Ownership is explicit because `aclose()` must dispose exactly what this
    composition created and never what it merely borrowed. A production
    composition always owns its engine — it built it from its own canonical
    graph, immediately below — so `owned=False` exists for the test harness,
    which lends the suite's session-scoped disposable-PostgreSQL engine to many
    compositions in turn. An application disposing that engine would be
    disposing a fixture other tests are still using.
    """

    engine: Engine
    owned: bool


@dataclass(frozen=True, slots=True)
class RequestServices:
    """Every service, bound to one connection and therefore to one transaction."""

    accounts: AccountRepository
    sessions_repository: SessionRepository
    transactions: OAuthTransactionRepository
    tokens: TokenGrantRepository
    credentials: WebAuthnRepository
    grants: RecoveryGrantRepository
    mappings: RoleMappingRepository
    membership: MembershipProjectionRepository
    audit: WebAuditRepository
    rate_limiter: RateLimiter
    session_service: SessionService
    oauth: OAuthLoginService
    break_glass: BreakGlassService
    role_mappings: RoleMappingService
    # -- P3.2 -----------------------------------------------------------
    character_access_repository: CharacterAccessRepository
    identity_candidates: IdentityCandidateRepository
    proposals: IdentityProposalRepository
    characters: CharacterQueryService
    #: The **one** writer of `character_access` anywhere: R-25, R-26, R-27 and
    #: R-29. The identity-migration confirmation creates its link through this
    #: exact object rather than through a second implementation, which is what
    #: stops the migration path having its own version of the one-active-owner
    #: invariant, the optimistic version and the audit event (migration contract
    #: §7.2 as amended by change-log entry C-P3.2-A).
    character_access: CharacterAccessService
    identity_migration: IdentityMigrationService
    account_identities: AccountIdentityService
    # -- P3.3 -----------------------------------------------------------
    snapshots_repository: SnapshotReadRepository
    jobs_repository: ReconciliationJobRepository
    audit_search_repository: AuditSearchRepository
    #: R-42, R-45, R-46 and the read half of R-43/R-44. It never executes a
    #: preview or an apply: the request enqueues durable work and the worker
    #: process claims it (N-40).
    jobs: ReconciliationJobService
    #: R-40 and R-41. `select_folder` writes the selection **and** invalidates
    #: every outstanding job for the snapshot in one transaction, through the
    #: same `jobs` object above rather than a second implementation of the
    #: staleness rule.
    snapshot_admin: SnapshotAdminService
    import_receipts: ImportReceiptService
    audit_search: AuditSearchService


class WebComposition:
    """Holds the process-lifetime objects and builds the per-request ones.

    **It is the one configuration authority in a web process** (2026-08-16).
    `self.settings` is the canonical exact-base graph, built once in `__init__`
    from one read of every supplied field; `create_app` takes its settings from
    here rather than accepting a second graph beside it, and every service,
    repository, provider and middleware object below reads from this one.

    **The provider and the engine are derived from that graph, not supplied**
    (2026-08-16, P3.G1 provider/engine authority remediation). The constructor
    takes `settings` and an optional HTTP *transport*, and nothing else. Both
    dependencies were previously parameters:

    * `provider_double: IdentityProvider` rejected only a concrete
      `DiscordIdentityProvider`. `IdentityProvider` is a structural protocol, so
      a wrapper, a delegating adapter or an ordinary fake could hold graph B's
      client id, secret, redirect URI, scopes, guild and endpoints, pass that
      exclusion, and then build R-03's authorization URL and R-04's token
      exchange for an application that had validated graph A. Naming a parameter
      "double" does not make what arrives through it test-only.
    * `engine: Engine` accepted any SQLAlchemy engine, unrelated to
      `settings.database`. That `settings.database.url` had a single reader
      proved only that the configured database selection could be *ignored*;
      running the S-14/S-15 resource checks against the injected engine proved
      that engine was usable and at the expected revision, not that it was the
      database the canonical graph selected.

    Both parameters are gone. What remains is a pair of protected hooks,
    `_build_engine` and `_build_provider`, called once each from `__init__`;
    their only overrides live in `tests/web/composition_harness.py`, and reaching
    them requires writing a `WebComposition` subclass rather than passing an
    argument.

    **The three process-lifetime objects are write-once.** `settings`, `engine`
    and `provider` are read-only properties over private slots that `__setattr__`
    refuses to rebind, because `create_app` validating a provider at startup said
    nothing about the object a request would dereference a minute later: R-03,
    R-04 and `aclose()` all read `provider`, and it was publicly assignable.

    Two attributes are mutable and neither is a *configuration* authority:
    `startup_warnings`, which is diagnostic output no route, service, repository
    or control reads; and `_lifecycle`, which selects no object and may only ever
    move forward through `CompositionLifecycle`.

    **This object owns the lifetime of what it built** (2026-08-16, P3.G1
    lifecycle remediation). `aclose()` is not a convenience for tests: since this
    remediation `create_app()` installs an ASGI lifespan that holds the exact
    composition it accepted and awaits this method once during shutdown, so a
    normally stopped web process closes the provider that served OAuth and
    disposes the engine it built. See `aclose()` for the ownership and
    idempotency rules.

    That ownership covers **three** exits, not one (2026-08-16, P3.G1 lifecycle
    re-review). A normal shutdown and a refused startup both run `aclose()`,
    because the resource checks moved inside the lifespan that owns this object;
    and a constructor that fails after building an engine disposes it before
    raising, because at that point no complete composition exists for anything
    else to hold. The rule is that no path which builds an engine leaves without
    releasing it.

    **And it is a lifetime, so it is spent once** (2026-08-16, P3.G1
    test-clock-authority re-review). Because `aclose()` is permanent, "who owns
    this" has to be answered before a startup does anything, not only when a
    shutdown arrives. `claim_for_startup()` is that answer: it moves `NEW ->
    STARTED` and refuses every other state, so a composition passed to two
    applications — or an application whose lifespan is entered twice — fails the
    second ASGI startup instead of completing it with a closed Discord HTTP client
    and a disposed engine. Nothing about the refusal releases anything: the
    claimant that already holds this object is the one that will close it, and a
    second application must not close resources it never started. See
    `claim_for_startup()` for why the resource checks cannot stand in for this.
    """

    #: Rebinding any of these after construction is refused. Named here rather
    #: than left to the read-only properties alone, so the private slot behind
    #: each property is write-once too and there is one rule rather than three.
    _WRITE_ONCE = frozenset(
        {"_settings", "_engine", "_owns_engine", "_envelope", "_provider"}
    )

    __slots__ = (
        "_settings",
        "_engine",
        "_owns_engine",
        "_envelope",
        "_provider",
        "_lifecycle",
        "startup_warnings",
    )

    def __init__(
        self,
        *,
        settings: WebSettings,
        provider_client: "httpx.AsyncClient | None" = None,
    ) -> None:
        #: **The one canonical settings graph for this process** (2026-08-16,
        #: P3.G1 canonical-graph remediation). Built here, before anything else
        #: in this constructor runs, from one read of every supplied field.
        #:
        #: What arrives is caller-controlled and may be a subclass of
        #: `WebSettings` — or hold one at any depth — whose reads answer an
        #: accepted value while a constructor validates it and a different value
        #: afterwards. Retaining it, as this line previously did, is what let the
        #: repository validate one session bound while `OAuthLoginService` used
        #: another, and what let a caller give middleware one graph and the
        #: services another. Nothing below this line, and no consumer this object
        #: hands settings to, ever sees the argument again.
        self._settings = canonical_web_settings(settings)
        handle = self._build_engine()
        if type(handle) is not EngineHandle:
            raise SettingsAuthorityError(
                "_build_engine must return an EngineHandle, which is where the "
                "serving engine and the statement of who disposes it are stated "
                f"together, not {type(handle).__name__}."
            )
        self._engine = handle.engine
        self._owns_engine = handle.owned
        # **From here on this constructor owns an engine, so it must not leak one**
        # (2026-08-16, P3.G1 lifecycle re-review, partial-construction audit).
        # Both steps below can raise on inputs the environment boundary accepts:
        # `Envelope` validates the token-encryption key register, and building the
        # provider constructs a real `httpx.AsyncClient` and then has to satisfy the
        # no-second-Discord-authority requirement. Either refusal used to leave a
        # fully built SQLAlchemy engine — and, in production, its pool — with no
        # reference anywhere and no `aclose()` ever reachable, because no complete
        # composition existed for a caller or a lifespan to hold. The engine is the
        # one resource this path can release honestly: `Engine.dispose()` is
        # synchronous, so it is safe to call from `__init__`.
        #
        # A provider that was *constructed and then rejected* is deliberately not
        # closed here. Its `aclose()` is a coroutine and there is no running loop a
        # synchronous constructor may safely await on — inventing one would be a
        # worse defect than the leak it addressed. That path is reachable only from
        # a `WebComposition` subclass whose `_build_provider` returns a
        # `DiscordIdentityProvider` configured from a second graph, which exists
        # nowhere in `adapters/`, `application/`, `domain/` or `tools/`; production
        # has no parameter that can produce it.
        #
        # A `dispose()` that itself failed would surface in place of the
        # construction failure, with that failure chained as its `__context__`.
        # Both are then visible in one traceback, which is the honest outcome here:
        # no object escapes this constructor either way, so there is no ASGI startup
        # contract to keep a particular exception at the head of.
        try:
            self._envelope = Envelope(self._settings.encryption)
            # There is deliberately **no session policy held here** (2026-08-15,
            # idle-policy-construction remediation). A composition-level policy was
            # this root's answer to "the repository and the service must agree", and
            # it worked only because both construction sites remembered to pass the
            # same object. `SessionRepository` now derives the bounds itself and
            # `SessionService` reads them from it, so agreement is structural and a
            # copy held here would be a second authority with nothing to enforce it.
            # The configuration those bounds come from is `settings.session`, which
            # is the canonical graph's exact-base `SessionSettings` — validated as it
            # was read, a few lines above, and unable to answer anything else
            # afterwards. An out-of-register value still refuses at startup, one
            # layer earlier than before.
            self._provider = self._require_no_second_discord_authority(
                self._build_provider(provider_client)
            )
        except BaseException:
            if handle.owned:
                handle.engine.dispose()
            raise
        #: The one-way lifecycle (2026-08-16, P3.G1 test-clock-authority
        #: re-review). It answers two questions with one piece of state: whether
        #: an application may still claim this composition, and whether `aclose()`
        #: has already begun. Not write-once — it has to move — but `__setattr__`
        #: below admits only forward moves, so "started" cannot be walked back to
        #: "new" and a closed composition cannot be reopened.
        self._lifecycle = CompositionLifecycle.NEW
        #: Conditions that are refusals in production and warnings elsewhere
        #: (S-15). Held so an operator can see them and a test can assert
        #: that a development host reports rather than swallows them. The one
        #: attribute here that is not write-once, because it is diagnostic
        #: output rather than an authority: no route, service, repository or
        #: control reads it.
        self.startup_warnings: tuple = ()

    # -- the two protected construction hooks --------------------------------

    def _build_engine(self) -> EngineHandle:
        """The serving engine, derived from **this** composition's canonical graph.

        Production's only implementation, and the reason `create_engine` has one
        caller in this process. `build_engine` reads the canonical pool numbers
        once and hands SQLAlchemy the url `self.settings.database` selected, so
        "the engine every request uses is the database the validated graph
        names" is established by construction — there is no second engine for it
        to be compared against, and no rendered database URL is compared with
        anything (a comparison would admit two authorities that happen to agree,
        would be unreliable across dialect spellings, and would be a comparison
        of a string that may carry credentials).

        Overridden only by `tests/web/composition_harness.py`, which lends the
        suite's guarded disposable-PostgreSQL engine and marks it unowned.
        """
        return EngineHandle(build_engine(self._settings), owned=True)

    def _build_provider(
        self, client: "httpx.AsyncClient | None"
    ) -> IdentityProvider:
        """The identity provider, derived from **this** composition's canonical graph.

        `client` is a transport and never a configuration: `DiscordIdentityProvider`
        takes the timeout and the no-redirect rule from `settings.discord`
        whatever transport it is handed, and the client id, secret, redirect URI,
        scopes, guild id and endpoints are read from that object alone.

        Overridden only by `tests/web/composition_harness.py`, which returns the
        portal suite's fake provider.
        """
        return build_provider(self._settings.discord, client=client)

    def _require_no_second_discord_authority(
        self, provider: IdentityProvider
    ) -> IdentityProvider:
        """What `_build_provider` returned is not another graph's Discord adapter.

        Defense in depth, and the supported state it detects is exactly one: a
        `WebComposition` **subclass** whose `_build_provider` override returns a
        real `DiscordIdentityProvider` configured from a settings graph other
        than this composition's. Production has no such subclass and no
        parameter that could produce that object; the harness in `tests/` could,
        and this is what stops it doing so by accident.

        It is deliberately *not* the security boundary and is not described as
        one. It cannot classify a wrapper or a delegating adapter — a structural
        protocol makes that undecidable — which is precisely why the boundary is
        the absence of a parameter rather than a check on what came through it.

        The question asked is identity, not equality: whether the provider's
        configuration object **is** this graph's `discord`. A field comparison
        would accept two independently built graphs that happen to agree today
        and would be a comparison of the client secret besides.
        """
        from adapters.web.discord_provider import DiscordIdentityProvider

        if isinstance(provider, DiscordIdentityProvider) and not (
            provider.is_configured_from(self._settings.discord)
        ):
            raise SettingsAuthorityError(
                "a Discord identity provider held by this composition must be "
                "the one built from its own canonical settings.discord. The "
                "provider holds the client id, client secret, redirect URI, "
                "scopes and guild id that the authorization URL and the token "
                "exchange are built from, so one configured from a second graph "
                "is an OAuth flow this process never validated — S-05 would have "
                "checked one redirect URI while callers were sent to another."
            )
        return provider

    # -- the process-lifetime objects, read-only -----------------------------

    def __setattr__(self, name: str, value: object) -> None:
        """The two rules that keep this object's state from becoming a lever.

        **Write-once** for the slots behind the properties below. The public names
        are properties with no setter, so `composition.provider = other` already
        refuses. This closes the obvious next reach — assigning the private slot —
        and, more usefully, states the rule in one place rather than relying on
        three property definitions to each keep saying it.

        **Forward-only** for `_lifecycle`, which cannot be write-once because it
        exists in order to move. See `_require_forward_transition`.
        """
        if name in WebComposition._WRITE_ONCE and hasattr(self, name):
            raise SettingsAuthorityError(
                f"{name} is written once, when this composition is constructed, "
                "and never again: the settings graph, the engine and the "
                "identity provider a request uses must be the ones the "
                "application validated at startup. Build another composition "
                "instead of replacing a dependency inside a live one."
            )
        if name == "_lifecycle":
            self._require_forward_transition(value)
        super().__setattr__(name, value)

    def _require_forward_transition(self, value: object) -> None:
        """`_lifecycle` moves forward or not at all.

        The write-once rule cannot be used here, because this attribute exists in
        order to move. What replaces it is monotonicity: `NEW -> STARTED ->
        CLOSING -> CLOSED`, never sideways and never back. Without it the state
        would be a lever rather than a record — resetting a `CLOSED` composition
        to `NEW` would let a second application claim one whose Discord HTTP
        client is closed and whose engine is disposed, which is the defect this
        machine exists to refuse.
        """
        current = getattr(self, "_lifecycle", None)
        if not isinstance(value, CompositionLifecycle):
            raise CompositionLifecycleError(
                "a composition's lifecycle is one of CompositionLifecycle's "
                f"states, not {type(value).__name__}."
            )
        if current is None:
            if value is not CompositionLifecycle.NEW:
                raise CompositionLifecycleError(
                    "a composition begins at CompositionLifecycle.NEW, before it "
                    f"has been claimed or closed, not at {value.name}."
                )
            return
        if value.value <= current.value:
            raise CompositionLifecycleError(
                f"a composition's lifecycle moves forward only: {current.name} "
                f"cannot become {value.name}. A composition that has been claimed "
                "by an application lifespan, or whose provider and engine have "
                "been released, stays that way — build another one rather than "
                "reopening a spent lifetime."
            )

    def claim_for_startup(self) -> None:
        """Claim this composition for **one** application startup, or refuse.

        Called by the ASGI lifespan `create_app()` installs, before the resource
        checks and before anything is served (2026-08-16, P3.G1
        test-clock-authority re-review).

        `aclose()` is permanent: it closes the provider's HTTP client and, for a
        production composition, disposes the engine it built. Before this method
        existed nothing checked that state on the way *in*, so one composition
        passed to two applications — or one application whose lifespan was entered
        a second time — answered `lifespan.startup.complete` and began serving
        with a closed Discord client behind R-03 and R-04. The first failure was
        an OAuth request, not a startup.

        The resource checks are not a substitute for this and never were. They
        would not detect the closed provider at all, and they would not detect the
        disposed engine either: `Engine.dispose()` does not invalidate the engine,
        it replaces the pool, so S-14 and S-15 open fresh connections through the
        replacement and report a healthy database. A check that passes on a
        resource nobody may use is worse than no check, which is why the refusal
        is a state transition here rather than an assertion there.

        **Nothing is closed by a refusal.** In `STARTED` the claimant that already
        holds this object is the one responsible for closing it, and cleaning up
        underneath it would take the provider and the engine away from an
        application that is serving requests — turning a caller's mistake into an
        outage. In `CLOSING` or `CLOSED` there is nothing left to release.
        """
        if self._lifecycle is not CompositionLifecycle.NEW:
            raise CompositionLifecycleError(
                "this composition has already been claimed by an application "
                f"lifespan (it is {self._lifecycle.name.lower()}), and a "
                "composition serves exactly one. Its provider is closed and its "
                "owned engine disposed when that lifespan ends, so a second "
                "startup would report success and then serve requests against a "
                "closed Discord client. Build a composition per application."
            )
        self._lifecycle = CompositionLifecycle.STARTED

    @property
    def settings(self) -> WebSettings:
        """The canonical exact-base graph, for the life of this composition."""
        return self._settings

    @property
    def engine(self) -> Engine:
        """The one engine: startup checks, every request transaction, cleanup."""
        return self._engine

    @property
    def provider(self) -> IdentityProvider:
        """The one identity provider: R-03, R-04 and `aclose()` all read this."""
        return self._provider

    @property
    def lifecycle(self) -> CompositionLifecycle:
        """How far through its one lifetime this composition is.

        Read-only, like the three authorities above: the transitions are
        `claim_for_startup()` and `aclose()`, and there is no fourth caller that
        should be setting a state directly.
        """
        return self._lifecycle

    @property
    def envelope(self) -> Envelope:
        return self._envelope

    def services(self, connection) -> RequestServices:
        settings = self.settings
        accounts = AccountRepository(connection)
        #: The **one** owner of session bounds in this graph. It derives them
        #: from `settings.session` — N-06's, N-07's, N-15's and N-66's numbers
        #: stay in configuration, the adapter holds no duration of its own, and
        #: which window a method gets is the explicit classification table in
        #: `application/web/capabilities.py`. The session service below takes its
        #: bounds from this object rather than being given a second set.
        session_repository = SessionRepository(connection, settings=settings.session)
        transactions = OAuthTransactionRepository(connection)
        tokens = TokenGrantRepository(connection)
        credentials = WebAuthnRepository(connection)
        grants = RecoveryGrantRepository(connection)
        mappings = RoleMappingRepository(connection)
        membership = MembershipProjectionRepository(connection)
        audit = WebAuditRepository(connection)
        character_access_repository = CharacterAccessRepository(connection)
        identity_candidates = IdentityCandidateRepository(connection)
        proposals = IdentityProposalRepository(connection)
        #: Built once here and shared by the three callers that write links, so
        #: the Council screen and the identity-migration confirmation cannot
        #: drift apart: they are not two services that agree, they are one.
        character_access = CharacterAccessService(
            access=character_access_repository, accounts=accounts, audit=audit
        )
        rate_limiter = RateLimiter(
            RateLimitRepository(connection),
            settings.rate_limits,
            settings.client_digest_key,
        )
        # -- P3.3 -------------------------------------------------------
        snapshots_repository = SnapshotReadRepository(
            connection, profile_version=FIELD_PROFILE.version
        )
        jobs_repository = ReconciliationJobRepository(
            connection,
            # N-23's exact lease and N-43's attempt cap, from the validated
            # worker graph. The web process never claims a job (S-11), but it
            # does read and cancel them, and the statements it issues carry the
            # same numbers the worker's do — one source, not two.
            lease_seconds=settings.worker.lease_seconds,
            max_attempts=settings.worker.max_attempts,
        )
        audit_search_repository = AuditSearchRepository(connection)
        job_service = ReconciliationJobService(
            jobs=jobs_repository,
            snapshots=snapshots_repository,
            accounts=accounts,
            audit=audit,
            bounds=settings.bounds,
            # N-42's queue admission bound, read from the same validated graph.
            worker=settings.worker,
        )
        session_service = SessionService(
            sessions=session_repository, token_grants=tokens, audit=audit
        )
        return RequestServices(
            accounts=accounts,
            sessions_repository=session_repository,
            transactions=transactions,
            tokens=tokens,
            credentials=credentials,
            grants=grants,
            mappings=mappings,
            membership=membership,
            audit=audit,
            rate_limiter=rate_limiter,
            session_service=session_service,
            oauth=OAuthLoginService(
                transactions=transactions,
                accounts=accounts,
                token_grants=tokens,
                role_mappings=mappings,
                membership=membership,
                session_service=session_service,
                audit=audit,
                envelope=self.envelope,
                settings=settings,
            ),
            break_glass=BreakGlassService(
                accounts=accounts,
                webauthn_repository=credentials,
                recovery_grants=grants,
                session_service=session_service,
                audit=audit,
                settings=settings,
            ),
            role_mappings=RoleMappingService(role_mappings=mappings, audit=audit),
            character_access_repository=character_access_repository,
            identity_candidates=identity_candidates,
            proposals=proposals,
            characters=CharacterQueryService(
                access=character_access_repository,
                accounts=accounts,
                candidates=identity_candidates,
                # The versioned field profile is **code under change control**
                # (route contract §5.1), so it is imported rather than
                # configured: there is no write route, and a profile an operator
                # could point at something else would be a profile nobody
                # reviewed.
                profile=FIELD_PROFILE,
                cursor_key=settings.cursor_key,
            ),
            character_access=character_access,
            # R-28, R-29 and R-30. `access_service` is the **same object** the
            # line above hands to R-25, not a second construction of the same
            # class: the Council screen's grant and the identity-migration
            # confirmation are not two services that agree, they are one, so
            # they cannot drift apart. R-29's link is written through it in the
            # request's own transaction, which is what makes the confirmation
            # and its authorization atomic.
            identity_migration=IdentityMigrationService(
                proposals=proposals,
                access_service=character_access,
                access=character_access_repository,
                accounts=accounts,
                audit=audit,
                cursor_key=settings.cursor_key,
            ),
            account_identities=AccountIdentityService(
                accounts=accounts, credentials=credentials, audit=audit
            ),
            # -- P3.3 ----------------------------------------------------
            snapshots_repository=snapshots_repository,
            jobs_repository=jobs_repository,
            audit_search_repository=audit_search_repository,
            jobs=job_service,
            snapshot_admin=SnapshotAdminService(
                snapshots=snapshots_repository,
                jobs=jobs_repository,
                audit=audit,
                # The **same** job service R-42 and R-46 use, not a second
                # construction of the class: R-41's invalidation and a
                # confirmation's staleness check are one implementation of the
                # rule rather than two that agree today.
                job_service=job_service,
                cursor_key=settings.cursor_key,
            ),
            import_receipts=ImportReceiptService(
                snapshots=snapshots_repository, accounts=accounts, jobs=jobs_repository
            ),
            audit_search=AuditSearchService(
                audit=audit_search_repository,
                accounts=accounts,
                bounds=settings.bounds,
                cursor_key=settings.cursor_key,
            ),
        )

    async def aclose(self) -> None:
        """Close exactly the provider requests used, and dispose only what we own.

        `self._provider` is the same object R-03 and R-04 dereference — it cannot
        be anything else, because it is written once — so the HTTP client closed
        here is the one whose connections the process actually opened. An engine
        this composition did not build is left alone: disposing a lent one would
        reach into the lender's pool.

        **Called on a refused startup as well as on a normal shutdown**
        (2026-08-16, P3.G1 lifecycle re-review). The lifespan `create_app()`
        installs runs S-12/S-14/S-15 inside itself, so this method is what releases
        the provider and the owned engine when a resource check refuses the boot —
        the path that previously returned no application at all and therefore ran
        no cleanup. Nothing below distinguishes the two callers, and nothing should:
        what is closed and what is only borrowed does not depend on why the process
        is stopping.

        **The idempotency rule is stated here, not borrowed** (2026-08-16, P3.G1
        lifecycle remediation, finding 2). This method performs its cleanup **at
        most once per composition**. The move to `CLOSING` happens before the
        first `await`, which is what makes it hold for an *overlapping* second
        call as well as a later one: there is no suspension point between the test
        and the transition, so two tasks cannot both pass it. A second call is a
        no-op that returns without touching the provider or the engine.

        That idempotency is for a repeated or overlapping **cleanup**, and is not
        a licence to start again (2026-08-16, P3.G1 test-clock-authority
        re-review). A second `aclose()` returning quietly is correct because the
        work is already done; a second *startup* returning quietly would be an
        application serving requests against what this method closed, which is why
        `claim_for_startup()` refuses it rather than relying on the guard below to
        look accommodating.

        The alternative — letting a second call through and relying on
        `httpx.AsyncClient.aclose()` and `Engine.dispose()` to tolerate it — was
        rejected. Both happen to tolerate it today; neither documents it as a
        contract, and `Engine.dispose()` in particular does not raise but
        silently *replaces the pool*, so a stray second disposal would return
        cleanly while discarding connections another holder was still using. A
        rule this object enforces is checkable; a tolerance two libraries happen
        to have is not.

        **An owned engine is disposed even if closing the provider raises.** The
        `finally` is the whole point: a provider whose transport fails to shut
        down cleanly would otherwise leak the SQLAlchemy pool as well, turning
        one failure into two. The provider's exception is **re-raised** rather
        than logged or swallowed — an ASGI shutdown that could not release its
        resources cleanly is not a clean shutdown, and hiding it would leave an
        operator with a process that reported a normal stop. Nothing is added to
        that exception here: no settings value, no database URL and no provider
        configuration is rendered into it or logged beside it.

        Because the state moves before the attempt rather than after it, a failed
        cleanup is **not** retried by a second call. The owned engine has already
        been disposed by the `finally`, so the only thing a retry could repeat is
        the provider close that just failed, and repeating it would surface the
        same failure a second time from a different caller.

        The nested `finally` is what makes the composition reach `CLOSED` even
        when disposal itself raises. Leaving it at `CLOSING` would change nothing
        a guard reads — both states refuse a claim and both make this method a
        no-op — and would report an in-flight shutdown for a process that has
        stopped, which is a worse thing for an operator to be shown than a
        completed one that also raised.
        """
        if self._lifecycle in (
            CompositionLifecycle.CLOSING,
            CompositionLifecycle.CLOSED,
        ):
            return
        self._lifecycle = CompositionLifecycle.CLOSING
        try:
            closer = getattr(self._provider, "aclose", None)
            if closer is not None:
                await closer()
        finally:
            try:
                if self._owns_engine:
                    self._engine.dispose()
            finally:
                self._lifecycle = CompositionLifecycle.CLOSED


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


__all__ = [
    "CompositionLifecycle",
    "CompositionLifecycleError",
    "EngineHandle",
    "RequestServices",
    "STATIC_ROOT",
    "TEMPLATE_ROOT",
    "WebComposition",
    "build_engine",
    "build_provider",
    "utcnow",
]
